# 18 — Writing Coding & Settings (the SystemSettings2 store)

Can an in-process HMI plugin **persist** a coding/settings change on its own unit — write the
SystemSettings2 (syset2) store, trigger the `changeId` rebuild of `/sysetpage`, and have the
change survive a reboot? This is the **write** counterpart to [doc-17 (the read
path)](17-coding-data-path.md). Short version: **reaching the store from a plugin is feasible**
(it is a normal named DSI service and the HMI process is already a DSI client), and a successful
store *does* bump the `changeId` and rebuild `/sysetpage` and persist. But **whether the server
accepts an unauthorized coding write is the open question** — the only signature check we can read
is **client-side** (in the diag/UDS app), and the authoritative `SysetSrv` store handler is not a
readable binary in this carve. And even a persisted write **does not live-apply to the running
HMI** (read-once; §4). So the honest answer is *reachable and effective, authorization-at-the-server
UNKNOWN* — with a one-command on-car test that settles it.

> **Scope & authorization.** Everything here was reverse-engineered from an **offline flash
> carve** and **owner-authorized** work on the author's **own titled NBT-Evo head unit**, running
> 100 % vanilla OEM firmware with only `OPT_DEBUG` enabled (system-service access; it does not
> change what the HMI or the settings server accept). No hardware was touched for this document —
> it is a static read of a flash carve. This is **defensive / architectural** understanding of the
> owner's own device, for the SDK: it reports the write-authorization model faithfully, **including
> where enforcement is and is *not* present**. No VIN, private network address, or car-specific
> diagnostic payload is part of this SDK. Build and test only on hardware you own.

> **Evidence legend.**
> **[CONFIRMED]** — read the disassembled logic, or direct byte/file evidence (a symbol, an RTTI
> class name, an ELF `NEEDED`/reloc entry, an on-disk OEM file, a string at an offset). Re-verified
> against the carve for this document.
> **[STRONG]** — a structural fact (import-set intersection, a service-role registration, a symbol
> table, "no such exporter/gate exists on this path") that forces the conclusion without a full
> instruction trace.
> **[PLAUSIBLE]** — an indirect reading the carve does not fully settle.
> **[UNKNOWN]** — the carve cannot settle it; stated as an open question with the decisive test,
> not a guess. **The security crux (§3) has one such residue and it is called out explicitly.**
>
> `binary:0x…` are virtual addresses / string offsets in that binary; `.c:NNN` are lines in the
> Ghidra decompiles of your own carved binaries. Symbol facts are `nm -D` / `readelf`.

---

## 0. TL;DR — can a plugin change `/sysetpage` and bump the `changeId`?

Three parts to the answer; keep them separate, because they carry very different confidence.

> **Reachability — YES, a plugin can *invoke* the store.** The store is a normal, servicebroker-
> resolvable DSI service, **`SysetSrv.DSYSSysetClientStore`**. `HmiMain3D` is already a full
> DSI/servicebroker client, and HMI plugins are native `.so`s `dlopen`'d into it, so plugin code
> can drive that service over the process's existing connection. The client cache lib
> (`libsys_data_systemsettings_containers`) is on-FS and its in-process dependencies are already
> satisfied inside `HmiMain3D` by `libhmicoding.so`. The one irreducible **bring-your-own** is the
> DSI store *proxy* itself (per-binary generated code, in **no** shared library) plus the
> `DSYSSysetTypes::KeyValue` serialization. **[CONFIRMED the service is reachable & the process is a
> DSI client; STRONG that a native plugin can drive it.]**
>
> **Authorization — THE CRUX — NOT settled from the carve.** The only coding-signature check we can
> read is **client-side**, in the diag/UDS app (`NbtEvoOmapDiagHUHighApp`) and in `NBTCarHU` — it
> verifies the tester's blob *before* the identical store call. The write-client lib itself has
> **zero** authorization logic. BMW's own crypto-free engineering shell `sysetshellevo` can *form*
> an unsigned coding store over the same interface. **But** the authoritative `SysetSrv` **server**
> — which alone decides accept/reject — runs inside the `stage2`/MoCCA container (and on the Jacinto
> side) and is **not a readable binary in this carve**, so whether it re-checks a signature, caller
> identity, or a protected coding-key namespace is **UNKNOWN**. The lean toward "the server does not
> gate coding" is only **PLAUSIBLE/WEAK** (it rests on the single `sysetshellevo` tool, and *both*
> real coding-write clients carry signature machinery — equally consistent with coding being
> signature-*expected*). **Do not read this as "a plugin can freely self-code."** §3 gives the
> one-command on-car test that resolves it.
>
> **Apply — even a persisted write does NOT reach the running HMI.** Per [doc-17](17-coding-data-path.md),
> the HMI reads `/sysetpage` **once at init** into a private snapshot with no re-read and no change
> subscription. A store persists and rebuilds `/sysetpage` live, but the running HMI keeps the stale
> value until **re-init = HMI restart / ECU reset** (`ECUReset 11 01`). The change *persists* and
> *applies after re-init*. **[CONFIRMED HMI read-once; STRONG apply⇒reset.]**

**Net:** a plugin can *issue* a store and, if accepted, it *will* bump the `changeId`, rebuild
`/sysetpage`, and persist across reboot — but it will not show in the running HMI without a reset,
and **whether the server accepts an unauthorized coding key is the unresolved, security-relevant
question.**

---

## 1. The write path — recap end-to-end

A coding/settings write is a **two-part mechanism** (a client-side shared-memory cache session,
then a DSI commit), followed by a server-side persist + a projection rebuild:

```
 ESYS / tester ──UDS──► NbtEvoOmapDiagHUHighApp        ◄── signature/CRC verified HERE (CLIENT-side)
                          checkSignatureCoding / CHBSignatureIf::checkSignatureAndCRC
                          "[dia] signature check was succesfull"   (only then ↓)
                            │
                            │  build a pending "cache session"  (client-side, shmem)
                            │  CSysetClientDataAccessor(page,lock)
                            │    startCacheSession → insertCacheItem(keyId, CHBBuffer) → endCacheSession
                            ▼
                          CnbtSysetClientStore → CDSYSSysetClientStoreProxy
                            │  requestStoreChange(cookie)      ──DSI──►  SysetSrv.DSYSSysetClientStore
                            ▼
 ┌───────────────────────────────────────────────┐   authoritative store — NOT a readable ELF here
 │ SysetSrv / SysetSrvEvo                          │   (hosted in /opt/sys/bin/stage2, MoCCA/libmldr;
 │  (the settings "sync master")                   │    -nosysetsyncmaster ⇒ master/slave; Jacinto side)
 │   • persists via Persistency  (survives reboot) │
 │   • bumps a changeId                            │──► responseStore: new changeId
 └───────────────────────┬─────────────────────────┘
                         │ DSYSSysetProxy changeId
                         ▼
                   sysetpageproxy.processEvent
                     "DSYSSysetProxy changeId: %d, keys: %d" → CSysetPageProxyJobUpdate::execute
                     → rebuild /sysetpage (+ /sysetpage-lock)          ◄── LIVE
                         │
                         ▼
                   HmiMain3D reads /sysetpage ONCE at init  (read-once — doc-17)
```

Two things to hold onto for the rest of the doc:

1. The **signature is verified in the diag app, then** the key-values are stored. The store libs
   carry no verification of their own. **[CONFIRMED — see §3.]**
2. The store *call* is identical whoever makes it — the diag app, `NBTCarHU`, the `sysetshellevo`
   engineering shell, or (hypothetically) a plugin all drive the **same** `CSysetClientDataAccessor`
   cache session + `requestStoreChange` against the **same** `SysetSrv.DSYSSysetClientStore` role.
   **[CONFIRMED — §2.]**

---

## 2. Reachability — can a plugin invoke the store? (Q1)

**Yes, technically.** The store is a named DSI service, the HMI process is already a DSI client,
and plugins are native in-process code. The only hard requirement a plugin must satisfy itself is
the **generated DSI store proxy** (and the `KeyValue` serialization it carries).

### 2.1 The pieces, and where each one is

| Piece the store needs | Status in the `HmiMain3D` process | Grade |
|---|---|---|
| DSI stack (servicebroker / base / colibry) | **Already loaded** — `readelf -d HmiMain3D` `NEEDED` `libsys_dsi_servicebroker.gpp.so.4`, `libsys_dsi_base.gpp.so.4`, `libsys_dsi_colibry.gpp.so.8` | [CONFIRMED] |
| The service `SysetSrv.DSYSSysetClientStore` | **Reachable by name** — a normal servicebroker-resolvable role (registered by writers on this node; `NBTCarHU.c:18608`, proxy idx `0x1f`, right after the read proxy `SysetPageProxy.DSYSSysetClientGet` `0x1e` at `:18606`) | [CONFIRMED] |
| Native plugin execution in-process | **Yes** — `libhmiplugin.so` (a `HmiMain3D` `NEEDED`) uses `dlopen` + `PluginFramework::XmlScanner::getOsArchSpecificLibraryPath`; plugin code has full ELF capability | [CONFIRMED] |
| Client cache lib `…_containers.gpp.so` | **On-FS & `dlopen`-able** (the diag app already links it dynamically); `.gpp.so` matches `HmiMain3D`'s libstdc++ ABI. Exports `CSysetClientDataAccessor::{startCacheSession@0xd6c8, insertCacheItem@0xd6b4, endCacheSession@0xd684}` | [CONFIRMED] |
| `sysetDefaults_*` + `SysetPageGetSh_*` (the cache lib's undefined imports) | **Already satisfied in-process** — `libhmicoding.so` (a `HmiMain3D` `NEEDED`, hence in the global symbol scope) **exports** the exact names: `sysetDefaults_getBuffer@0x71810`, `getSizeById@0x719e4`, `getDataVersionById@0x71878`, `isValidId@0x7187c`, `SysetPageGetSh_attach@0x69728`, `getMappedCbBuffer@0x68fb4`, `update@0x69644` | [CONFIRMED] |
| `DSYSSysetTypes::KeyValue` (ctor/assign/dtor) | **NOT provided** by any HMI-carve `.so` — a genuine bring-your-own for the cache route | [CONFIRMED] |
| **DSI `CDSYSSysetClientStoreProxy`** | **In NO shared library anywhere** (searched every `.so` under `opt/` and the ID5 HMI carve) — per-binary *generated* code, compiled into each writer. **The plugin must lift/generate it** (or hand-roll the DSI request event) | [CONFIRMED] |
| A DSI receive/dispatch context for the response | Reuse the HMI CoreFramework dispatcher, **or** spawn its own (as `sysetshellevo` does: `dsircvMasterChannel`/`dsircvSubChannel`) | [STRONG] |
| `/sysetpage` opened **RWRITE** (cache route stages KeyValues in the page) | The HMI opens the page **read-only**; whether the shm object's owner/mode lets the HMI uid `shm_open(O_RDWR)` is **not determinable offline** | [PLAUSIBLE / UNKNOWN] |

> **Correction to an earlier structural read.** An intermediate finding claimed the cache lib's
> `sysetDefaults_*` / `SysetPageGetSh_*` imports had "no provider" in the HMI process and would have
> to be brought in. That was scoped to `sda3/opt` and missed the HMI carve: `libhmicoding.so`
> **statically defines and exports** all of them (verified above), and it is a `NEEDED` of
> `HmiMain3D`, so a `dlopen`'d `…_containers.gpp.so` binds against it at load. This **strengthens**
> reachability (fewer bring-your-owns), it does not weaken it.

### 2.2 The concrete call sequence a plugin would replicate

Recovered from the shipped engineering shell `sysetshellevo` and the diag app:

```
resolve  "SysetSrv.DSYSSysetClientStore"                 // servicebroker lookup (in-proc SB)
acc = CSysetClientDataAccessor("/sysetpage","/sysetpage-lock")
s   = acc.startCacheSession()
acc.insertCacheItem(s, keyId, CHBBuffer(value))           // e.g. a CB_FENT_MIRACAST coding key
... repeat per key ...
acc.endCacheSession(s)                                    // stages the pending KeyValues (+ a "mark")
proxy.requestStoreChange(cookie)                          // CDSYSSysetClientStoreRequestEvent
   → response UPD_ID_responseStore  ⇒ new changeId
```

Confirmed against `sysetshellevo` (`CSysetShellCommandStore …: requestStoreChange( cookie = 0x%x )`,
`Set CAF-key value …: setc[ey] {<key_name>|<key_id>}=<key_value>`) and against the diag app
(`NbtEvoOmapDiagHUHighApp.c` `FUN_0013e744@49250`: env-path ctor `SYSET_PAGE`/`SYSET_PAGELOCK`
default `/sysetpage`,`/sysetpage-lock`; `startCacheSession@49291`; `endCacheSession@49044/49072/49099`;
`insertCacheItem@114209`). **[CONFIRMED.]**

### 2.3 Two routes, and the irreducible dependency

- **Route A — reuse shipped libs.** `dlopen` `…_containers.gpp.so`, let its `sysetDefaults_*` /
  `SysetPageGetSh_*` bind against `libhmicoding` (already in-process), build the cache session, then
  send `requestStoreChange` via a **brought-in DSI store proxy**. Also needs `DSYSSysetTypes::KeyValue`
  brought in (no HMI provider). Caveat: the cache stages into `/sysetpage` **RWRITE** (open perm for
  the HMI uid is the one unresolved reachability item).
- **Route B — hand-roll.** Bring only the generated `CDSYSSysetClientStoreProxy` + `KeyValue`
  serialization and issue the DSI store directly on the in-process servicebroker — sidesteps the
  cache lib and possibly the `/sysetpage` RWRITE requirement (if the request event carries the
  KeyValue payload rather than a shmem cookie — **UNKNOWN** which).

Either way the **DSI store proxy is the irreducible bring-your-own** (it exists in no shared lib),
and the DSI stack + the service name + the cache lib's deps are all already present.

> **Getting the code *in* is a separate gate (see [doc-14](14-signing-and-coding.md)).** §2 there
> establishes that a dropped-in plugin's *load* does **not** require a signature. `libhmiplugin.so`
> shows no signature/permission/certificate gate strings, so a plugin-load crypto gate is **not
> established** from this carve (**UNKNOWN**). That gate is about admitting native code into
> `HmiMain3D`; it does not change whether that code, once running, can *call* the store.

---

## 3. Authorization — the crux (Q2)

**This is the security-relevant question, and the carve cannot settle it. Verdict: UNKNOWN at the
server, with a PLAUSIBLE/WEAK lean toward "no server-side signature gate." A one-command on-car test
resolves it.**

### 3.1 What *is* confirmed: the readable signature check is client-side

| Claim | Evidence | Grade |
|---|---|---|
| The write-client cache lib has **no** authorization logic | `nm -DC …_containers.gpp.so` exports only the data model (`NSyset::CSysetCbFunction`, `CSysetAdjustSymbol`, `CSysetDataCache`, `CSysetClientDataAccessor`) + `DSYSSysetTypes::KeyValue`; `strings \| grep -iE 'signature\|crc\|auth\|verify'` → **empty**. It is a dumb cache client. | [CONFIRMED] |
| The coding-signature check runs **in the diag/UDS app**, on the tester blob, *before* the store | `NbtEvoOmapDiagHUHighApp`: `checkSignatureCoding` @0x1b5cbd, `CHBSignatureIf::checkSignatureAndCRC signature from Tester encrypted:` @0x1b5cf4, `[dia] signature check was succesfull` @0x1b5e12, `[dia] ERROR: signature check failed` @0x1b5e39, `Coding Data signature is %s HALLO` @0x1b5c7a, and a policy path `Accepted wrong signature or CRC` @0x1ae2f1. The `[dia]` prefix + "from Tester" place it in the diagnostic app. | [CONFIRMED] |
| The **same** signature machinery also lives in `NBTCarHU` (the other real coding-write client) | `strings NBTCarHU` → `checkSignatureCoding` (count 1), plus `CnbtSysetClientStore` + `SysetSrv.DSYSSysetClientStore`. So signature-checking **co-locates with the coding-write path in both** clients that do real coding writes. | [CONFIRMED] |
| BMW's own engineering shell can *form* an **unsigned** coding store over the same interface | `sysetshellevo` (`/opt/sys/bin`): `setc[ey] … = "Set CAF-key value"` (CAF = coding), `store = requestStoreChange(cookie)`, targeting `SysetSrv.DSYSSysetClientStore`. It has **no crypto engine** — `nm -DC` shows only `CHBCRC`/`ZIN_CRC` (no rsa/sha/aes/`CHBSignature`/`checkSignature`). Its only store preconditions: state `FullyOperable` and a non-empty **mark** (`AUTHORITY_MARKED`/`AUTHORITY_UNMARKED`/`SIGNATURE`). | [CONFIRMED] |

So: **the signature gate that exists in readable code is a client-side gate, and nothing readable
re-verifies it.** That much is solid.

### 3.2 What is NOT confirmed: whether the *server* gates a coding store

The authoritative decision-maker is the `SysetSrv`/`SysetSrvEvo` **server**, and it is **not a
readable binary in this carve**:

- It is the settings **sync master**, hosted in the `stage2`/MoCCA container: `starter.cfg` launches
  `/opt/sys/bin/stage2 -l /opt/sys/lib/libmldr.so … -nosysetsyncmaster --stage2-initstate=FullyOperable`
  (`-nosysetsyncmaster` ⇒ these OMAP instances are *slaves*; `FullyOperable` is the normal running
  state, matching `sysetshellevo`'s store precondition). **[CONFIRMED — `starter.cfg`.]**
- Across `/opt/*/bin` the **only** `DSYSSyset*Stub` is `sysetpageproxy:CDSYSSysetClientGetStub` — the
  **read** side. **No** readable ELF provides the **store** stub or the `SysetSrv` role; the server
  interface set (`SysetService.SysetSrv`, `SysetSrv.DSYSSysetClientStore/DSYSSysetAdmin/DSYSOnOff`)
  appears only inside the **Jacinto** firmware blobs. **[CONFIRMED — role/stub search + Jacinto strings.]**

Therefore whether the server (a) re-verifies a `SIGNATURE` mark, (b) requires `AUTHORITY_MARKED` for
coding keys, or (c) enforces a caller-identity / **coding-vs-adjustment namespace ACL** is
**UNKNOWN** from static analysis.

### 3.3 Why the "server doesn't gate coding" lean is only PLAUSIBLE/WEAK

An earlier synthesis graded this **STRONG**, citing "three non-diag writers store unsigned." That
does **not** survive verification, and the corrected picture is much weaker:

- Of the three, **two do not write the coding store at all.** `srv-hddmgr2` and `hddsafemodectl`
  reference `SysetSrv.DSYSSysetClientStore` **0 times each**; they set a single HDD **SafeMode**
  system key through a scoped wrapper (`CSMIfDsiSysetKeyCtl`, `SetKeyValueHddSafeMode`,
  `SYSETKEYCTL_SAFEMODEKEY`). They only show a *non-coding* key is writable — **the classic
  coding-vs-settings conflation**, not evidence about coding. **[CONFIRMED — role count 0; scoped
  SafeMode strings.]**
- Only **`sysetshellevo`** writes the coding (`Cb`) namespace unsigned — and that proves a client can
  **issue** an unsigned coding store, **not** that the server **accepts/persists** it. `sysetshellevo`
  can *also* register a `SIGNATURE` mark, so it "functions" whether or not the server gates coding.
- Meanwhile **both** real coding-write clients (the diag app **and** `NBTCarHU`) carry the coding-
  signature machinery — a pattern **at least as consistent** with the coding namespace being
  signature-*expected* as with the server ignoring signatures.

**Fair grade:** server-side coding authorization **UNKNOWN**; the "no signature gate" reading
**PLAUSIBLE/WEAK**, resting on one engineering tool. A server-side coding-namespace ACL is a **live
alternative**, not a mere residual. **Do not overclaim.**

> **Two citation corrections carried in for accuracy.**
> (1) `sysetshellevo` *does* contain the strings `AES_128`/`DES_CBC` — but as **coding value-labels**
> (`M_SECURITY_MODE_*` neighbours, i.e. security-mode CAF option names), **not** a crypto engine; the
> "no crypto engine" conclusion stands via `nm` (only `CHBCRC`).
> (2) The `changeId` log strings `UPD_ID_responseStore`/`UPD_ID_storedChangeId` live in
> `sysetshellevo`/`NBTCarHU` (`CnbtSysetClientStore`), **not** the diag app (0 hits). The diag app's
> `responseStoredChange Cookie=%x, ChangeId=%x` / `onEndStoreTraceTimeStamp` belong to its
> `[dia-trace]` `CInternalTraceSystemSettings` TRACE-config subsystem, not the vehicle-coding store.
> The `changeId` mechanism itself is real (`ChangeId_NoResponse` DSI attr on the store response) — §4.

### 3.4 The decisive on-target test (owner's own unit, existing root shell)

The owner already has an `OPT_DEBUG` root shell, so the crux is settled with the shipped tool — no
plugin needed to answer the *authorization* question:

1. In normal `FullyOperable` state, run `sysetshellevo`; `getcb <coding-key you're entitled to>` to
   read the current value.
2. `setc <coding-key>=<new value>`; register a mark that is **`AUTHORITY_UNMARKED`/CRC only** (no
   signature); `store`.
3. Read back `getlaststoredchangeid`; watch `sysetpageproxy` log the `DSYSSysetProxy changeId` bump
   and `/sysetpage` rebuild; **reboot** and confirm the value survived.
   - **Accepted + `changeId` bumps + persists ⇒ the server does NOT gate coding by signature** — a
     plugin (or the root shell) can persist coding.
   - **Rejected (permission/signature/authority error), or an `AUTHORITY_UNMARKED` coding value
     silently not projected ⇒ the server DOES gate** — a plugin cannot self-code. Capture the error
     to characterize the gate (state / role / namespace / signature).
4. Plugin equivalent (only needed to prove the *plugin* path specifically): from `HmiMain3D`, resolve
   `SysetSrv.DSYSSysetClientStore`, run the §2.2 sequence, `requestStoreChange`, observe accept/reject.

The test is safe (a coding value the owner is entitled to) and directly resolves the one residual
that matters.

---

## 4. Effect — if accepted, what actually happens (Q3)

Assume the server accepts a store. The reader-side effect chain is **confirmed**; the caveat is that
it does **not** reach the running HMI.

| Link | Evidence | Grade |
|---|---|---|
| store → **`changeId` bump** returned to the writer | `CnbtSysetClientStore::processEvent UPD_ID_responseStore change id %d` / `UPD_ID_storedChangeId stored change id %d` (in `sysetshellevo`/`NBTCarHU`); the store response carries `ChangeId_NoResponse` | [CONFIRMED client protocol / STRONG server increments] |
| `changeId` → **`/sysetpage` rebuilt live** | `sysetpageproxy`: `CSysetPageProxy::processEvent DSYSSysetProxy changeId: %d, keys: %d` → `CSysetPageProxyJobUpdate::execute … Failed write page '%s'`; self-desc `update SysetPage with key values received from SysetSrvEvo` | [CONFIRMED] |
| **persists across reboot** | `Persistency.DSYSPersistency` role; durable "storedChangeId" semantics; `/sysetpage` is a **volatile** RAM projection rebuilt from the persisted KV store at boot (doc-17 §2). Concrete flash region **UNKNOWN**. | [STRONG] (backend UNKNOWN) |
| running **HMI does NOT live-apply** | HMI maps `/sysetpage` **once** at `CHmiVariantServer::init` (`libhmicoding.so:0x48164`) into a private snapshot, no re-read/subscription (doc-17 §1). Applies only after **re-init = HMI restart / ECU reset** (`ECUReset 11 01`). | [CONFIRMED read-once / STRONG apply⇒reset] |

**Who re-reads live?** The central `libhmicoding` consumer does **not** (read-once, CONFIRMED). The
`/sysetpage` page *mechanism* supports versioning (`SysetPageGetSh_getChangeAttr`/`update`,
`getDataVersion`), so a **bespoke** ID5 app that re-attaches/polls the page *could* observe a store
live — but no such consumer was found and not every ID5 binary was audited (**UNKNOWN**; doc-17 §6).
**Do not assume a live store reaches any HMI feature without a restart.**

---

## 5. Write paths compared

Three ways a change can reach the store on this unit. The **key asymmetry**: the coding **signature
is a client-side gate inside the diag app** (and `NBTCarHU`), guarding only the sanctioned path (c).
Paths (a) and (b) issue the *identical* store on the *same* DSI role and never touch it — **but
whether the server accepts them is the open Q2 (§3), identical for both.**

| Path | How the store is issued | Signature check? | Persist / apply | Feasibility on this unit |
|---|---|---|---|---|
| **(a) HMI plugin** brings the client | native `.so` in `HmiMain3D`; cache via `…_containers.gpp.so` (deps satisfied by `libhmicoding`) + **brought-in** DSI store proxy + `KeyValue`, over the in-proc servicebroker | **Bypassed** — the verifier lives in the diag app, not the store path | if accepted: persists; HMI needs restart to apply | **STRONG-feasible / PLAUSIBLE effort** — store proxy is the irreducible bring-your-own; `/sysetpage` RWRITE for the HMI uid unverified |
| **(b) `sysetshellevo` over the `OPT_DEBUG` root shell** *(author already has this)* | `setc <key>=<val>` then `store` → `requestStoreChange` → same role | **None** — no crypto engine, CRC-mark only | if accepted: persists; only precondition is `FullyOperable` (normal state) | **CONFIRMED present.** The pragmatic path; independent of any plugin |
| **(c) sanctioned ESYS / UDS** | ESYS —UDS→ diag app → same store client | **Yes, CLIENT-side** (`checkSignatureCoding` → then store) | persists; ESYS forces apply with `ECUReset 11 01` | the reference / authorized path |

Notes, owner-authorized framing:
- (a) and (b) are the *same* server question; (b) is already available to the owner via the root
  shell, so it is the natural way to **answer §3's crux** before ever building a plugin.
- None of (a)/(b) forges anything: they issue a store the owner is entitled to on the owner's own
  unit. Whether the server *honours* an unsigned coding store is exactly what §3.4 measures.
- "Bypassed" in (a)/(b) means the **client-side** check is bypassed. It says nothing about a
  server-side check, which is **UNKNOWN** (§3.2).

---

## 6. Open questions / decisive on-target tests

| # | Open question | Grade | How to settle it |
|---|---|---|---|
| 1 | **THE CRUX.** Does the `SysetSrv`/`SysetSrvEvo` **server** gate a coding store (re-verify a `SIGNATURE` mark, require `AUTHORITY_MARKED` for coding keys, or apply a caller-identity / coding-namespace ACL)? The server is the `-nosysetsyncmaster` master in the `stage2`/MoCCA container and lives (readably) only in Jacinto blobs. | [UNKNOWN] | §3.4 test: `sysetshellevo` `setc` a coding key with an `AUTHORITY_UNMARKED`/CRC mark → `store`; observe accept+`changeId`+reboot-survival (server does not gate) vs reject/not-projected (server gates). |
| 2 | `AUTHORITY_UNMARKED` vs `AUTHORITY_MARKED` semantics for a **coding** key: accepted+projected, accepted-but-not-projected, or rejected? | [UNKNOWN] | Same test; compare an `UNMARKED` coding store vs an `UNMARKED` adjustment store. |
| 3 | Is the CODING (`Cb`) namespace treated differently from freely-writable ADJUSTMENT/custom keys **at the server**? (Many services write settings freely — must **not** be generalized to coding.) | [UNKNOWN] | `setc` (coding) vs `seta` (adjust) vs `setk` (custom) through the same store path; compare accept/persist. |
| 4 | Does `requestStoreChange` carry the `KeyValue` payload **in the DSI message** (`CDSYSSysetClientStoreRequestEvent`) or only a **cookie** referencing the `/sysetpage` shmem cache? Determines whether Route A actually needs `/sysetpage` **RWRITE**. | [UNKNOWN] | Trace the request-event serialization on-target, or with a working ARM disassembler. |
| 5 | Can the HMI uid `shm_open("/sysetpage", O_RDWR)` (cache-route stager)? | [PLAUSIBLE] | On-target as the HMI uid: `shm_open("/sysetpage", O_RDWR)` and `…/sysetpage-lock`; success ⇒ Route A cache stage is in reach. |
| 6 | Is native-**plugin load** into `HmiMain3D` itself signature/permission-gated (doc-14)? `libhmiplugin.so` shows no such strings. Affects getting code *in*, not whether it can call the store. | [UNKNOWN] | Disassemble `libhmiplugin` load path; or drop a benign unsigned plugin and observe load (doc-14 §2). |
| 7 | Does any bespoke ID5 consumer re-read `/sysetpage` live (see a store without a restart)? Central `libhmicoding` is read-once (CONFIRMED); others unaudited. | [UNKNOWN] | Scan each ID5 app binary for `SysetPageGetSh_attach` + a periodic coding-key read; or watch the UI during the §3.4 store. |

**One-line resolver:** the §3.4 `sysetshellevo` store on the owner's own unit answers #1–#3 at once,
and — because (a) and (b) hit the same server — simultaneously tells you whether the **plugin** path
would be accepted.

---

## 7. Sources & method

- **Owner-authorized, offline-carve reverse engineering** of the author's own titled NBT-Evo head
  unit (vanilla OEM firmware, `OPT_DEBUG` for system-service access only). No hardware was touched;
  this is a static read of a flash carve. Because the code is stock, what these OEM binaries do here
  is what a stock unit does.
- **Binaries & files (re-verified for this document).**
  Write client lib `…/opt/sys/lib/libsys_data_systemsettings_containers.{cpp-ne,gpp}.so`
  (`CSysetClientDataAccessor` exports; imports `sysetDefaults_*`/`SysetPageGetSh_*`/`DSYSSysetTypes::KeyValue`);
  `…/opt/sys/bin/{sysetshellevo, sysetpageproxy}` (the crypto-free shell writer; the `/sysetpage`
  rebuilder); `…/opt/sys/bin/{srv-hddmgr2, hddsafemodectl}` (scoped SafeMode-key writers — *not* the
  coding store); `…/opt/core/bin/NbtEvoOmapDiagHUHighApp` and `…/opt/car/bin/NBTCarHU` (the two real
  coding-write clients, both with the client-side signature check); `…/opt/sys/etc/starter.cfg`
  (`stage2 -nosysetsyncmaster --stage2-initstate=FullyOperable`); HMI (read-only ref)
  `opt/hmi/ID5/bin/HmiMain3D`, `opt/hmi/ID5/lib/{libhmicoding.so, libhmiplugin.so}`; the Jacinto
  blobs in your carve's `0000271a` partition (only place the `SysetSrv` server role is named).
  Decompiles: Ghidra output of `NbtEvoOmapDiagHUHighApp` and `NBTCarHU` from your own carve.
- **Method.** Structural facts (`nm -D` symbol sets & the exact `sysetDefaults_*`/`SysetPageGetSh_*`
  provider match in `libhmicoding`, `readelf -d` `NEEDED`, `readelf -r` relocs, `strings` at offsets,
  role-string counts, `starter.cfg`) were verified directly against the carve while writing this
  document. The client store sequence is read from `NbtEvoOmapDiagHUHighApp.c` and corroborated by
  `sysetshellevo` strings. The authoritative server handler was **not** readable (MoCCA/`stage2`
  container / Jacinto), which is why §3 is graded **UNKNOWN** and the decisive on-target test is
  given rather than a guessed verdict.
- **Confidence is graded on every material claim** per the legend at the top. The security-relevant
  crux — **does the server gate a coding write** — is deliberately held at **UNKNOWN** (PLAUSIBLE/WEAK
  lean only), because the readable evidence is entirely client-side. This document **refines the
  write half** of [doc-17 (the read path)](17-coding-data-path.md) and cross-links
  [doc-14 (signing / coding / certificate permissions)](14-signing-and-coding.md) §2 (load needs no
  signature), §4 (capability map), §5 (what "Coded" gates).
