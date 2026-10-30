# 17 — The Coding Data Path

How a vehicle-coding value (CarPlay, WiFi-Mirroring/"WMI", Miracast, …) actually reaches a
running HMI app — and, critically, *when*. The short version: the running HMI **never reads the
`.ncd`**. It reads a **shared-memory projection of the applied netto coding** (`/sysetpage`,
a.k.a. "syset2"), and it reads it **once, at its own process init**, into a private snapshot.
This document traces the whole chain — write → store → shared page → HMI cache → `isVariantSet`
— and pins down the three timings that get blurred: **coding-write time**, **boot**, and **each
read**. It **refines** [doc-14 §5 (what "Coded" gates)](14-signing-and-coding.md); it does not
contradict it.

> **Scope & authorization.** Everything here was reverse-engineered from an **offline flash
> carve** and **owner-authorized** work on the author's **own titled vehicle**, whose head unit
> runs vanilla OEM firmware with only `OPT_DEBUG` enabled (persistent `starter.cfg` system
> services). Because the code is stock, whatever these OEM binaries do in this carve is what a
> stock unit does. No VIN, private network address, or car-specific diagnostic payload is part of
> this SDK. Build and test only on hardware you own.

> **Evidence legend.** Every material claim below carries one of four grades:
> **[CONFIRMED]** — the disassembled logic was read (ARM EABI5, via `arm-none-eabi-objdump`;
> host `objdump` cannot decode this arch), or direct byte evidence (a symbol table, an ELF
> section size, an on-disk file, a decompile line). Re-verified for this document.
> **[STRONG]** — a structural fact (symbol-set, section sizes, a `starter.cfg` order, "no such
> file exists") that forces the conclusion without a full instruction trace.
> **[PLAUSIBLE]** — an indirect reading the carve does not fully settle.
> **[UNKNOWN]** — the carve cannot settle it; stated as an open question, not a guess. The
> live-vs-reboot half of Q3 has one such residue, and it is called out explicitly.
>
> Addresses written `libhmicoding.so:0x…` are that binary's virtual addresses. `.c:NNN`
> citations are lines in Ghidra decompiles of your own carved binaries.

---

## 0. TL;DR

Three questions, three direct answers:

> **Q1 — Do the running HMI apps read gated features directly out of the `.ncd`? No.** The
> `.ncd` is a Motorola S-Record — the ESYS/UDS *transport* format — and **no `.ncd` or `CAFD`
> file exists anywhere on the running filesystem**. The HMI reads the **applied netto coding**
> out of a shared-memory page (`/sysetpage` / "syset2") and answers
> `CHmiVariantServer::isVariantSet(id)` / `CVACoding::getCodingVal`. The feature *descriptor*
> (which bit lives at which byte) is **compiled into `libhmicoding.so`**, not parsed from a
> file. **[CONFIRMED]**
>
> **Q2 — Is the coding parsed for global consumption at boot? Two-level answer, and the levels
> matter.** The **raw byte page** is built globally at boot: `sysetpageproxy` (boot process
> #109) publishes `/sysetpage`, a read-only shared-memory projection of the persisted settings
> store, for every process to map. But that page is **rebuilt from the already-persisted netto
> coding — it is *not* a parse of an `.ncd`/CAFD descriptor** (there is no such file to parse).
> And each *consumer's* parse-into-usable-form happens later, at that consumer's own init, not at
> boot. **[CONFIRMED]**
>
> **Q3 — On recode: live update, or reboot? The *store* updates live; the *HMI* does not.** A
> UDS recode writes new bytes into the settings store and `sysetpageproxy` rebuilds `/sysetpage`
> **live** on a `changeId` event — no reboot needed for the store. But the running HMI holds a
> **read-once private snapshot** taken at its init, with **no re-read path and no change
> subscription**, so it keeps the *stale* value. Applying a recode to the HMI therefore requires
> **re-initialization = HMI restart / ECU reset**. In the field ESYS ends a coding job with UDS
> `ECUReset 11 01`, which does exactly that. **[CONFIRMED that the HMI is read-once; STRONG that
> apply ⇒ reset; UNKNOWN only whether some *other* bespoke app polls live — see §6].**

### Data-flow at a glance

```
  ESYS / tester (off-car tool)
        │  UDS coding write  (Motorola S-Record  ==  the .ncd, transport only)
        ▼
 ┌──────────────────────────┐      .ncd is consumed HERE and never written to the running FS
 │ NbtEvoOmapDiagHUHighApp   │      checkSignatureCoding + CHBSignatureIf::checkSignatureAndCRC
 │  (diag / UDS server)      │      → CSysetClientDataAccessor cache-session (KeyValue)
 └───────────┬──────────────┘
             │ SysetSrv.DSYSSysetClientStore        ◄── WRITE-TIME (recode)
             ▼
 ┌──────────────────────────┐      authoritative store, flash-backed + checksummed
 │ SysetSrv / SysetSrvEvo    │──────► Persistency  (Persistency.DSYSPersistency)
 │  ("SystemSettings2")      │         AdjustBlock / E2P.*   ── survives power-off
 └───────────┬──────────────┘
             │ changeId (write) / rebuild (boot)     ◄── BOOT: rebuild only, NOT an .ncd parse
             ▼
 ┌──────────────────────────┐      POSIX shared memory, RONLY-mapped by consumers
 │ sysetpageproxy → /sysetpage │    "update SysetPage with key values received from SysetSrvEvo"
 │  ("syset2", RAM page)     │      rebuilt live on changeId (JobUpdate)
 └───────────┬──────────────┘
   direct shm attach (Sh)   │  SysetPageGetSh_attach / getBuffer
             ▼
 ┌──────────────────────────┐      CHmiVariantServer::init → CVACoding::open  (ONCE)
 │ libhmicoding.so           │        walk 3835-feature table → getCodingFromSyset2
 │  CHmiCodingService         │        → memcpy into PRIVATE buffer (SNAPSHOT)
 │  CVACoding (THmiMap cache) │        → CL6CodingVerification::execute (L6 checksum, once)
 └───────────┬──────────────┘        ◄── AT-INIT: read-once, cached, verified once
             │ isVariantSet(id) / getCodingVal   ── pure cache lookup, NO syset call
             ▼
 ┌──────────────────────────┐
 │ HMI app / RA-plugin       │   sees the coding value as of the last HMI (re)start
 └──────────────────────────┘
```

---

## 1. The read path — how a running HMI answers `isVariantSet`

**The HMI reads coding from `/sysetpage`, not from the `.ncd`, and the descriptor is baked into
the binary.** `libhmicoding.so` exports the whole coding surface: `CHmiVariantServer`,
`CHmiCodingService`, `CVACoding`, `CL6CodingVerification`, `CDsiBinaryStream`. The on-target read
path is `CDsiBinaryStream::getCodingFromSyset2(...)` (mangled
`_ZN16CDsiBinaryStream19getCodingFromSyset2EjPvjt`), which fetches from the shared page. There is
**no `.ncd`/`CAFD` path string anywhere in the library** — only the unused
`CFileBinaryStream::readCodingBlock` sibling carries `"CODING FILE …"` log strings, and it has
**zero call-sites**. **[CONFIRMED: `nm -D` + `strings`; caller count from disasm below.]**

Two distinct things reach the HMI from two distinct places:

| What | Where it lives at runtime | Grade |
|---|---|---|
| The **descriptor** (feature → byte/bit/mask; the CAFD's job) | **Compiled into `libhmicoding.so`** as the `CODING_FEATURE` table + `nbtSysetDefaults_getCbf<CONTAINER>_CB_F<FEATURE>` default accessors | [CONFIRMED] |
| The **applied netto coding** (the actual coded bytes for *this* car) | The `/sysetpage` shared page (syset2), fetched by `getCodingFromSyset2` → `SysetPageGetSh_getBuffer` | [CONFIRMED] |
| The **`.ncd` file** | **Nowhere on the running system** — it is the ESYS/UDS transport S-Record only | [CONFIRMED] |

So the descriptor is *never* parsed from a file on-target; the netto bytes come from syset2; the
`.ncd` is a flashing artifact. `CVACoding::getCodingCafId` exists so the HMI knows *which* CAFD
identity its compiled table corresponds to, but the layout itself is static code.

### 1.1 The read is done exactly once, at HMI process init — CONFIRMED at instruction level

This is the load-bearing fact for Q3, so it was disassembled, not inferred:

```
CHmiVariantServer::init      (libhmicoding.so:0x48164)
   └─ bl 0x5a2d8  CVACoding::open              ← the ONLY caller of open()
        │  loop r-idx 0 … 0xEFB  (movw r3,#3835)   ← walk all 3835 VACodingFeature entries
        └─ bl 0x65560  CHmiCodingService::openBinaryStream   ← the ONLY caller of openBinaryStream()
             └─ new CDsiBinaryStream(cafId)
                  getCodingFromSyset2:
                     bl 0x690c4  SysetPageGetSh_getBuffer     ← fetch from the shared page
                     bl 0x717c0  nbtSysetDefaults_getBuffer    ← fallback: compiled-in defaults
                     bl 0x465f8  memcpy@plt                    ← COPY into caller's PRIVATE buffer
        └─ bl 0x64454  CL6CodingVerification::execute          ← L6 checksum verify, once
```

- `openBinaryStream` (0x65560) has **exactly one** `bl` caller — at 0x5a618, inside
  `CVACoding::open`. `CVACoding::open` (0x5a2d8) has **exactly one** `bl` caller — at 0x481d0,
  inside `CHmiVariantServer::init`. Coding is thus opened, copied, and verified **once per HMI
  process life**. **[CONFIRMED — `bl`-target counts over the full ARM disassembly.]**
- `getCodingFromSyset2` **`memcpy`s** the `SysetPageGetSh_getBuffer` result into the caller's
  destination (0x687cc). It is a **snapshot**, not a live pointer into `/sysetpage`. If the
  shared page is unavailable it falls back to the compiled-in `nbtSysetDefaults_getBuffer`.
  **[CONFIRMED.]**
- The loop bound `movw r3, #3835 (0xEFB)` appears in `CVACoding::open` — the full feature-table
  walk. **[CONFIRMED.]**

### 1.2 Runtime queries are pure cache lookups — no syset call

Once the snapshot is built, `isVariantSet` / `getCodingVal` never touch syset again:

- `CHmiVariantServer::isVariantSet(uint)` (0x47bc0) contains **zero `bl` instructions** — it is a
  leaf that reads the cached per-feature block pointer inline. **[CONFIRMED.]**
- `CVACoding::getCodingVal(VACodingFeature, uint8&)` (0x52360) calls only
  `THmiMap<VACodingFeature,CODING_FEATURE*>::lookup` (0x5afdc) and
  `CL6CodingVerification::retrieveCodingValue` (0x52088, pure bit math: base+offset, mask). **No
  Syset accessor is called at query time.** **[CONFIRMED.]**

The failure string `"[CHmiCodingService] Unable to access syset page!"` and the verification
strings `"HMI Coding Verification:%cFAILED"` / `"Coding Block:%c%s"` all live in
`libhmicoding.so`, confirming that the *init-time* access is the one that can fail — not the
per-query path. **[CONFIRMED — `strings`.]**

**Net for Q1:** an HMI app or plugin asking "is CarPlay coded on?" gets an answer from a
**snapshot of the netto coding taken when the HMI last started**, resolved against a
**compiled-in descriptor**. It does not read the `.ncd`, and it does not re-read syset per call.

---

## 2. The global store — syset2 / SystemSettings2, and when it is populated

### 2.1 The store is a POSIX shared-memory page, `/sysetpage`

Every process reads coding from a shared-memory page named `/sysetpage` (lock `/sysetpage-lock`),
created and maintained by `opt/sys/bin/sysetpageproxy`. The proxy's own self-description string
is decisive:

> `sysetpageproxy - update SysetPage with key values received from SysetSrvEvo`

So the page is a **projection of the authoritative `SysetSrvEvo` server's key-values** — not a
parse of any coding file. It carries `shm_open`/`shm_unlink`,
`SYSETPAGE_OPEN_SHARED_MEMORY_RONLY` / `SYSETPAGE_MAP_SHARED_MEMORY_RONLY`, `ONE_PAGE`,
`CSysetPageProxy::requestBoot`, and the rebuild machinery `doInitPageBuildContext … lookupItemCount`
/ `CSysetPageProxyJobUpdate::execute`. Because it is RAM, it **cannot survive a reboot and must be
rebuilt each boot**. **[CONFIRMED — `strings` of `sysetpageproxy`.]**

**Two access styles read the same page — worth separating for plugin authors:**

- The **HMI** attaches to the shared memory **directly**: `SysetPageGetSh_attach`,
  `SysetShAccObj_attach`, `SysetShAccObj_timedLockROnly`, `SysetPageGetSh_getBuffer`. The DSI role
  string `SysetPageProxy.DSYSSysetClientGet` is **not present in `libhmicoding.so`** — the HMI
  does not do a DSI round-trip to read coding. **[CONFIRMED — `nm -D`; role string absent.]**
- The **diag app and the car service** (`NbtEvoOmapDiagHUHighApp`, `NBTCarHU`) hold the DSI role
  `SysetPageProxy.DSYSSysetClientGet` (e.g. `NBTCarHU.c:18606`). Same page, DSI-mediated access.
  **[CONFIRMED — decompile + strings.]**

The coding-block-to-value mapping is applied at **read time** by
`libsys_data_prj_nbt_systemsettings2_cbmapping.cpp-ne.so`, which exports **exactly two** functions
— `SysetPageGet_getMappedCbBuffer` and `SysetPageGet_getMappedCbValue` — and imports
`SysetPageGet_getBuffer` / `getValue` / `getDataVersion`. Its `.text` is `0x4324` but its `.data`
is **4 bytes** and `.bss` `0x1c`: it is **accessor logic, not a stored table**. It maps a
coding-block byte position to a value out of the page on demand. **[STRONG — export set + section
sizes; not disassembled to rule out an internal cache.]**

### 2.2 Persistence is a dedicated service — not the page, not the `.ncd`

Authoritative coding is owned by `SysetSrv`/`SysetSrvEvo` and persisted by `opt/sys/bin/Persistency`
(DSI role `Persistency.DSYSPersistency`), which stores checksummed records:
`"ClientStoreData %s/%s, SID 0x%08x, operationID 0x%08x"`,
`"PersSrvDBG: ClientStoreData: Checksum invalid for operationID 0x%08x"`. Coding/adjust values
live as an **"AdjustBlock"** and in `E2P.*` (EEPROM) namespaces, with an explicit
`"Compiled version: %hu, stored version: %u"` distinction (compiled defaults vs persisted coding —
seen in `sysetadjread`). The persistent data sits **behind the Persistency DSI service**, not as a
plain coding file on the mounted filesystem. **[CONFIRMED — `strings`.]**

### 2.3 Population timing — the three phases, kept crisp

This is the crux of Q2. The three phases are genuinely different and must not be blurred:

| Phase | What happens | Grade |
|---|---|---|
| **Coding-WRITE time** (ESYS codes the ECU) | The diag app `NbtEvoOmapDiagHUHighApp` receives coding over UDS, verifies it (`checkSignatureCoding`, `CHBSignatureIf::checkSignatureAndCRC`, `"Coding Data signature is %s HALLO"`), then **stores the block into `SysetSrv` via `SysetSrv.DSYSSysetClientStore`** using a `CSysetClientDataAccessor` cache-session (`startCacheSession` → `insertCacheItem` → `endCacheSession`/`update`, `DSYSSysetTypes::KeyValue`). `SysetSrv` persists it via `Persistency`. **This is when syset2 is populated.** | [CONFIRMED — diag decompile `NbtEvoOmapDiagHUHighApp.c:209/3109/9222`, strings] |
| **BOOT** | `Persistency` (boot process **#108**) starts, loading the persisted netto coding; then `sysetpageproxy` (boot process **#109**) rebuilds `/sysetpage` from `SysetSrvEvo`'s key-values. **This is a rebuild of a derived RAM cache — not a parse of an `.ncd`/CAFD.** Nothing in the boot chain reads a coding file, and none exists to read. | [CONFIRMED — `starter.cfg` Number 108 < 109; RAM page ⇒ necessarily rebuilt] |
| **Each READ** | `cbmapping`'s `getMappedCbValue` maps coding-block bytes → values on demand; the HMI's own reads are served from its at-init snapshot (§1). | [STRONG mapping / CONFIRMED HMI snapshot] |

**Answer to Q2:** the NCD is **not** parsed at boot for global consumption. The globally-consumed
store is the `/sysetpage` shared memory; it is **populated at coding-write time and persisted**,
and at boot it is only **rebuilt from the persisted netto coding**. The `.ncd` never exists as a
file on the running system, so there is nothing at boot to parse it from.

> **Where the authoritative `SysetSrv`/`SysetSrvEvo` server actually runs** is not a standalone
> named binary in this carve slice — it is hosted inside a MoCCA/`stage2` container (the loader
> `-nosysetsyncmaster` arg hints at a syset sync master/slave arrangement). This does not affect
> the boot-vs-write verdict. **[STRONG / residual — see §6.]**

---

## 3. On change (recode) — live-update vs reboot/reset

Because §1 proved the HMI holds a read-once snapshot, the on-change behavior splits cleanly by
layer. **The store is live; the HMI is not.**

| Layer | Behavior on a UDS recode | Grade |
|---|---|---|
| SystemSettings2 store (`SysetSrv`) | Written **live** via the diag `CSysetClientDataAccessor` cache-session; persisted via `Persistency` | [CONFIRMED] |
| `/sysetpage` shared page | Rebuilt **live** by the proxy on a `changeId` event: `CSysetPageProxy::processEvent DSYSSysetProxy changeId: %d, keys: %d` → `JobUpdate` → attach+write page. No reboot needed for the page to update. | [CONFIRMED] |
| Running HMI view | **Not updated.** No reload/refresh/`onCodingChanged` method exists on `CHmiVariantServer`; no DSI coding-change subscription exists in `libhmicoding.so`. The `getDataVersion` calls that do exist are internal per-read validity gates *inside* `SysetPageGet_getMappedCb*` (choose shared-page vs compiled defaults), not change-driven re-reads. `registerVariantClient` is HMI *apps* subscribing to the coding *server* — not the server re-reading syset. | [CONFIRMED] |
| Apply to the HMI | Requires **re-init = HMI restart / ECU reset**. Reset plumbing is present: `PowerStateController.DSYSReset` + `CDSYSResetClient` (`NBTCarHU.c:18618`), and the diag app's `CDSYSResetRequestEvent`. | [STRONG] |

**The nuance that makes this non-obvious:** the *infrastructure* is live-update capable — the
store change-notifies (`changeId`), the page rebuilds, and the HMI-side read library even exposes
`SysetPageGetSh_getChangeAttr` / `SysetPageGetSh_update`. But the HMI **never calls the refresh
path for coding**; it built its snapshot once at init and answers from it forever. So a recode
propagates to the store and the shared page **immediately**, yet the HMI keeps returning the old
value until it re-runs `CHmiVariantServer::init`.

**Verdict for Q3:** syset2 updates **live** at write time; the HMI **applies coding only on
(re)init**. In practice a recode of an HMI-consumed feature needs an **ECU reset / power cycle** to
take effect — which matches BMW convention: ESYS terminates a coding job with UDS `ECUReset 11 01`,
routed through `PowerStateController.DSYSReset`, and the HMI then re-runs `init` against the fresh
page. The "tester sends `11 01`" step is convention (not observable in an offline carve), so the
*apply-requires-reset* claim is **STRONG, not CONFIRMED** — the decisive on-car test is in §6.

---

## 4. Worked examples — CarPlay and WMI / WiFi-Mirroring / Miracast

Both flow through the **same** `CVACoding::open` → `isVariantSet`/`getCodingVal` path as every
other feature — they are **not special-cased**. **[CONFIRMED — same table, same loop.]**

| Feature | Coding parameter(s) in the HMI container | syset default accessor (container · CBF) |
|---|---|---|
| **CarPlay** | `va_CARPLAY_SWT`, `va_CARPLAY_FULLSCREEN`, `va_APPLE_ENHANCEMENTS`, `va_API_APPLE_AUTH_CHIP_ON_OFF` | `nbtSysetDefaults_getCbfSYSTEM_EINSTELLUNGEN_CB_FCARPLAY_SWT` |
| Apple-auth HW | `PRODLOGISTIC_HWCODING_APPLEDRM` (E2P/adjust) | hardware Apple-DRM/auth-chip presence |
| **WMI / WiFi-Mirroring / Miracast** | `va_ENT_MIRACAST`, `va_ENT_MIRACAST_DISPLAY_SETTINGS`, `va_ENT_MIRACAST_MULTIPLE_STREAMS`; also `CB_FMIRRORING`, `CB_FWLAN_WIFI_DIRECT` | `nbtSysetDefaults_getCbfHMI_CB_FENT_MIRACAST` |
| (sibling) A4A / Apps | `va_A4A_SWT`, `va_A4A_*` | `nbtSysetDefaults_getCbfHMI_CB_FA4A_SWT` |

**[CONFIRMED — all names present in `libhmicoding.so`'s coding-name table + `nbtSysetDefaults`
accessors.]**

### 4.1 CarPlay is NOT a plain coding feature — it carries a second, SWT/FSC axis

This is the one correction plugin authors must internalize (it refines doc-14 §5.5):

- **Coding gate** (`CARPLAY_SWT`, `ENT_MIRACAST`, …): read **once at init**, cached (§1). Recoding
  it requires a **reset** to apply (§3).
- **Runtime software-enabling token (SWT)** — **CarPlay and A4A only**: `libhmicoding.so` exports
  runtime setters `CHmiVariantServer::setSwtCarplayEnabled(bool)` (0x518c0) and
  `setSwtA4AEnabled(bool)` (0x518ac), both **weak** symbols. Neither has any *internal* caller
  (0 `bl` sites) — they are driven by **external HMI apps**, not from `init` and not from the
  coding read. And the token has its **own persistence channel**, distinct from the coding/adjust
  store: `Persistency.DSYSPersistencyFsc`, `CDSYSPersistencyFscStub.cpp`, `--persfscommit`. So
  CarPlay/A4A availability is `coding-bit AND SWT-token`, and the token can flip **at runtime
  without recoding**. **[CONFIRMED that the setter + separate FSC channel exist; STRONG on the
  exact token-verification internals — not disassembled.]**
- **Miracast / WMI / Mirroring / WiFi-Direct**, by contrast, have **no `setSwt*` setter** — they
  are **purely coding-gated**. **[CONFIRMED — no such symbol for these features.]**

Practical consequence: reading only `isVariantSet(CARPLAY_SWT)` can *mis*report CarPlay's real
availability, because the SWT token is a second gate. For Miracast/WMI, the coding bit is the whole
story.

---

## 5. What this means for a plugin

A plugin that wants to gate its behavior on a coded feature should:

- **Query through the HMI coding surface** — `CHmiVariantServer::isVariantSet(id)` /
  `getVariantVal` / `CVACoding::getCodingVal` — which resolves against the `/sysetpage` snapshot.
  See [doc-06 runtime API](06-runtime-api-reference.md) for how a plugin reaches the variant
  server. **Do not** read the `.ncd` (it is not on-target) and **do not** attach `/sysetpage`
  yourself unless you deliberately want the *live* page rather than the HMI's snapshot.
- **Treat coded values as a boot-time snapshot.** The value your plugin sees is whatever coding was
  present when the **HMI last started**. This is stable for the life of the HMI process — good for
  a one-shot capability check at plugin init, and consistent with the rest of the HMI (which is
  reading the same snapshot).
- **Do not expect a recode to take effect while the HMI is running.** After the car is recoded, an
  **ECU reset / power cycle** is required before `isVariantSet` returns the new value. If your
  plugin caches a coding decision, it does not need its own invalidation logic — a reset restarts
  everything anyway — but it must not *assume* a live recode reached it.
- **For CarPlay / A4A specifically, distinguish the two axes.** The coding bit (`CARPLAY_SWT`,
  snapshot) and the runtime SWT token (`setSwtCarplayEnabled`, live, separate FSC persistence) can
  disagree. If your plugin cares about *actual current* CarPlay availability, the coding bit alone
  is not authoritative. Miracast/WMI have only the coding bit.

> **This refines [doc-14](14-signing-and-coding.md).** Doc-14 §5 establishes that "Coded" is a
> *feature-enablement* axis separate from signing, and that coding does **not** gate a dropped-in
> plugin's *load*. This document adds the mechanism *underneath* that: **how** a coded value
> physically reaches the HMI (syset2 shared page, not the `.ncd`), **when** (write-time populate →
> boot rebuild → read-once at HMI init), and the **apply-after-recode** implication (reset
> required). Doc-14 §5.5's "third enablement axis: FSC/SWT" is the same `setSwtCarplayEnabled` /
> `Persistency.DSYSPersistencyFsc` token described in §4.1 here.

---

## 6. Open questions / decisive on-target tests

| # | Open question | Grade | How to settle it |
|---|---|---|---|
| 1 | Does a recode **without** an ECU reset ever reach the HMI? The central `libhmicoding` path is definitively read-once, but a *bespoke* HMI app could attach `/sysetpage` directly and poll one parameter live. Not every ID5 app binary was audited. | [UNKNOWN] | Scan each HMI app binary for `SysetPageGetSh_attach` + a periodic read of a coding key; or the on-car test below. |
| 2 | Whether ESYS/the tester actually issues UDS `ECUReset 11 01` at the end of a coding job on *this* unit (BMW convention; the reset plumbing is present but the recode→reset sequence is not observable offline). | [STRONG] | On-car test below, step 4. |
| 3 | The SWT/FSC token mechanics for CarPlay/A4A: what calls `setSwtCarplayEnabled`, how the token is verified, how `Persistency.DSYSPersistencyFsc` feeds it. Only the setter symbol, the `CB_FCARPLAY_SWT` coding bit, and the separate FSC channel are visible. | [STRONG] | Disassemble the setter's callers in the HMI apps and the FSC persistency request/response path. |
| 4 | Exact numeric `VACodingFeature` enum ids for `CARPLAY_SWT` / `ENT_MIRACAST` (only the `va_` names and their shared `open()` loop membership were extracted). | [UNKNOWN] | Extract the enum from the `CODING_FEATURE` table indexing in `CVACoding::open`. |
| 5 | The concrete flash region/partition `Persistency` writes the syset/adjust + FSC blocks to (behind the DSI service; only `E2P.*` / `AdjustBlock` namespaces + a backup filename are visible). | [UNKNOWN] | RE the `Persistency` backend / storage descriptor; not needed for the boot-vs-write verdict. |

**Decisive on-car test (upgrades the STRONG items to CONFIRMED):**

1. With the HMI running, UDS-write `CARPLAY_SWT` (or `ENT_MIRACAST`) to a new value **without**
   issuing `11 01`.
2. Confirm the **store/page updated live**: watch `sysetpageproxy` log a `changeId` bump /
   `/sysetpage` rebuild, and read the value back over `SysetPageProxy.DSYSSysetClientGet`.
3. Confirm the **HMI has NOT applied it**: the CarPlay/WMI UI state is unchanged and `isVariantSet`
   still returns the old value.
4. Issue UDS `11 01` (or power-cycle) → the HMI re-runs `init` → confirm the feature now toggles.

That sequence isolates "syset updated live" (steps 1–2) from "HMI applies only on reset" (steps
3–4), which is exactly the boundary Q3 turns on.

---

## 7. Sources & method

- **Owner-authorized, offline-carve reverse engineering** of the author's own titled NBT-Evo head
  unit (vanilla OEM firmware, `OPT_DEBUG` for system access only). No hardware was touched for this
  analysis; it is a static read of a flash carve.
- **Binaries.**
  `opt/hmi/ID5/lib/libhmicoding.so`
  (the HMI coding surface);
  `…/opt/sys/bin/{sysetpageproxy, Persistency, sysetadjread}` and
  `…/opt/sys/lib/libsys_data_prj_nbt_systemsettings2_cbmapping.cpp-ne.so` (the syset2 store);
  `…/opt/core/bin/NbtEvoOmapDiagHUHighApp` (UDS coding-write path) and `…/opt/car/bin/NBTCarHU`
  (car service, reset + DSI roles); `…/opt/sys/etc/starter.cfg` (boot order);
  `/CAFD_00001EF6_006_064_014.ncd` (the transport S-Record, repo root — **not** on the running FS).
  Decompiles: Ghidra output of `NbtEvoOmapDiagHUHighApp` and `NBTCarHU` from your own carve.
- **Method.** Structural facts (`nm -D` symbol sets, `readelf -S` section sizes, `strings`, `file`,
  `find`, `starter.cfg` `<Number>` order, on-disk file presence) were verified directly against the
  carve while writing this document. The load-bearing control-flow claims — read-once path
  (`init`→`open`→`openBinaryStream` single-caller chain), the `memcpy` snapshot in
  `getCodingFromSyset2`, the 3835-entry (`0xEFB`) loop, and the *zero* syset calls in `isVariantSet`
  / `getCodingVal` — come from an `arm-none-eabi-objdump` disassembly of `libhmicoding.so` (host
  `objdump` cannot decode this ARM EABI5 binary), with `bl`-target counts taken over the full
  listing. The diag write path is read from the `NbtEvoOmapDiagHUHighApp.c` decompile
  (`CSysetClientDataAccessor` cache-session at `.c:209/3109/9222`).
- **Confidence is graded on every material claim** per the legend at the top. Two claims are
  deliberately held below CONFIRMED and marked: *apply-requires-reset* is **STRONG** (the tester's
  `11 01` is BMW convention, not offline-observable), and *no other app polls syset live for coding*
  is **UNKNOWN** (not every ID5 app binary was audited). Both are settled by the on-car test in §6.
