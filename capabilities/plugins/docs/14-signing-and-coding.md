# 14 — Signing, Coding & Certificate Permissions

What actually gates an RA plugin — and what does not. Three unrelated subsystems get
conflated under "is my plugin allowed to run": **signing** (`.p7b`/`.p12` PKCS#7 integrity /
trust), **coding** (BMW vehicle *Codierung* / FA-FDL feature enablement, a.k.a.
`PluginsCoded`), and **certificate permissions** (a runtime *capability* bitset). This document
separates them, answers whether loading needs any of them, and says — with graded confidence,
from the OEM binaries — where each one really acts.

> **Scope & authorization.** Everything here was reverse-engineered from an **offline flash
> carve** and **owner-authorized** work on the author's **own titled vehicle**, whose head unit
> runs **100 % vanilla OEM firmware with only `OPT_DEBUG` enabled** (a persistent `starter.cfg`
> enable that turns on the platform's ssh/telnet/qconn system services). Because the code is
> stock, whatever the OEM loader does in this carve is exactly what a stock unit's loader does.
> No VIN, private network address, or car-specific diagnostic payload is part of this SDK. Build
> and test only on hardware you own.

> **Evidence legend.** Every material claim below carries one of four grades:
> **[CONFIRMED]** — read the disassembled logic, or direct byte evidence (a symbol table, an ELF
> `NEEDED` list, an on-disk OEM file). Independently re-verified for this document where noted.
> **[STRONG]** — a structural fact (ELF dependencies, symbol-set intersections, "no crypto to
> call") that forces the conclusion without a full instruction trace.
> **[PLAUSIBLE]** — an indirect reading the carve does not fully settle.
> **[UNKNOWN]** — the disassembly did not reach it; stated as an open question, not a guess.
>
> Addresses written as `HmiMain3D:0x…` are that binary's virtual addresses. Disassembly-level
> claims were produced by the lead's targeted ARM/capstone passes (host `objdump` lacks ARM);
> the *structural* scaffolding around them — every `NEEDED` list, symbol set, string, and
> on-disk file cited — was re-verified directly against the carve while writing this doc.

---

## 0. TL;DR

An **unsigned, un-coded** RA plugin dropped into `data/ro/Plugins/` **loads and runs on a stock
unit**, and it does so for a *structural* reason, not because of `OPT_DEBUG`:

> **The in-process plugin loader performs no cryptographic verification of the manifest or the
> `.so` at any point.** The core HMI process (`HmiMain3D`) contains no crypto library and calls
> no OpenSSL function. Loading is a plain `dlopen()` + `dlsym("pluginAppInfo")` + a null-check on
> the returned descriptor, guarded only by manifest-validity and an *optional* permission-policy
> hook. **[CONFIRMED]**

The PKCS#7 / X.509 machinery is real, but it lives in a **different** module
(`libhmiremoting.so`) and authenticates **remote** apps (the A4A / RemoteApp path), not local
`.so` plugins. "Coding" is a **third**, separate thing (vehicle feature enablement via
`libhmicoding.so`), and it never gates a dropped-in plugin's load either. `OPT_DEBUG` is
orthogonal to all of it — it grants the *filesystem write access* to place the files, nothing
more.

The one caveat, kept honest throughout: this is **CONFIRMED for the uncoded `Plugins/`
directory** (where you drop plugins). The coded `PluginsCoded/` directory installs an extra
"coding list", and its **inputs are now resolved**: at registration (`HmiMain3D:0x108a1c4–
0x108a2ac`) the HMI calls `libhmicoding`'s `isVariantSet` (vtable `+0xc`) for features
**`0x0C0E`** and **`0x9C55`** and builds a coding-enabled name list — `ActiveSeating` /
`SecurityMenu` — attached to the `/PluginsCoded` scan root (`coded=true`, `0x24f15a0`). So the
`PluginsCoded/` gate is a **coding-value** gate (its inputs = those two features, keyed by
plugin name); the exact instruction that applies the list to filter a discovered manifest wasn't
single-stepped (strong-by-construction). Either way it is a boolean coding check, **never** a
signature verify — the whole load path links no cryptography (below).

---

## 1. Three concepts you must not conflate

| Concept | Lives in | What it is | Gates a `Plugins/` `.so` load? |
|---|---|---|---|
| **LOAD** | `HmiMain3D` (rhmiappmanager `ManagedPluginApp`) + `libhmiplugin.so` (`ManifestScanner`) + `libCoreFramework.A.so` (`DynamicLibrary::load` = `dlopen`) | manifest scan → `dlopen` → `pluginAppInfo` entry-point resolve | **This is the gate.** It checks neither a signature nor a coding value. **[CONFIRMED]** |
| **SIGNING** (`.p7b` PKCS#7, `.p12` PKCS#12) | `libhmiremoting.so` (`CAuthVerification`, OpenSSL `EVP_VerifyFinal`/`PKCS7`/`X509_CRL_verify`), with `libhmia4a.so` doing key/cert *reading* | remote-app (A4A) session certificate authentication + CRL revocation | **No.** `HmiMain3D`, `libhmiplugin.so` and `libhmicoding.so` link no crypto (byte-grep: 0 `PKCS7`/`X509`/`libcrypto`); the `ManagedPluginApp::init` abort list has no signature branch. The `PluginsCoded/` `.p7b`/`.p12` are A4A PKI (`CN=a4a_app_Connected…`), not load inputs. **[CONFIRMED]** (+ on-car: owner's unsigned plugin loaded) |
| **CODING** (Codierung / FA-FDL, `PluginsCoded`) | `libhmicoding.so` (`CHmiVariantServer::isVariantSet`, `CVACoding`, reads the `syset2` store over DSI) | boolean/value lookup of vehicle feature coding | **No** for the uncoded `/Plugins` load. For `/PluginsCoded`, coding (`isVariantSet` `0x0C0E`/`0x9C55`, keyed by plugin name) feeds the coded root's enable-list; strict load-filtering is strong-by-construction. Built-in static plugins are separately gated by `isVariantSet(0x5383)` (`registerPluginCoded 0x21f6f0`). **[CONFIRMED / STRONG]** |
| **CERT PERMISSIONS** | `CRhmiApplicationPermissions` (a 184-bit bitset, in both `HmiMain3D` and `libhmiremoting.so`) | a loaded app's **runtime capabilities** | **No.** It is a *capability* gate applied after load, and only narrowed by a verified remote certificate. **[CONFIRMED]** |

The cross-checks that keep these four apart are structural and were re-verified for this doc:

- `HmiMain3D` `NEEDED` = 56 libs, **none** `libcrypto`/`libssl`; it links `libhmicoding.so`,
  `libhmiplugin.so`, `libhmizip.so`, `libBMWOTFapi.so.3`. Its dynsym has **0** real OpenSSL
  symbols (the one grep hit, a `boost::basic_regex …EPKcS7_j` mangling, is a false positive).
  **[CONFIRMED — `readelf -d`, `nm -D`]**
- `libhmiplugin.so` (the loader lib) links **neither** `libcrypto` **nor** `libhmicoding` — it is
  structurally both signing- and coding-agnostic. **[CONFIRMED]**
- `libhmicoding.so` links **no** crypto — coding is plain feature-flag lookup, not cryptography.
  **[CONFIRMED]**
- `.p7b` is referenced at runtime by **only** `libhmiremoting.so`; `.p12` is referenced by **no**
  runtime ELF at all (`HmiMain3D`, `libhmicoding`, `libhmiplugin`, `libhmiremoting`, `libhmia4a`
  all = 0). **[CONFIRMED — `grep -acF`]**

---

## 2. Does loading require a signature? — **No.** (Q1)

### 2.1 The complete load path

Loading a loose-file RA plugin runs through three code owners, none of which does crypto:

1. **Discovery** — `HmiMain3D:0x108a2e0` registers a directory table `{ "/Plugins",
   "/PluginsCoded" }` (packed adjacent strings; both literals present in the stock binary —
   `/Plugins` ×2, `/PluginsCoded` ×1) into **one** `map<path, coded-bool>`:
   - `/Plugins` → scan method `0x24f14ec`, **coded = false**;
   - `/PluginsCoded` → scan method `0x24f15a0`, **coded = true**, which *additionally* copies a
     coding/permission list into the object. Both call the **same** map-insert and the **same**
     downstream loader. The coded directory gets **no** extra `.p7b`/signature lookup here.
     **[CONFIRMED — disasm]**
2. **Manifest validate + `ManagedPluginApp::init`** (`HmiMain3D:0x24f5090–0x24f5fbc`) — this is
   `rhmiappmanager`'s `ManagedPluginApp`, which builds a `CLocalPluginAppConnector` (*Local* =
   in-process). This code is statically linked **only** in `HmiMain3D` (`ManagedPluginApp`,
   `CLocalPluginAppConnector`, `rhmiappmanager` appear in `HmiMain3D` and in no lib).
   **[CONFIRMED — strings + disasm]**
3. **The actual `dlopen`/`dlsym`** — `ManagedPluginApp::init` calls `bmw::DynamicLibrary::load`
   (`libCoreFramework.A.so:0x132d8`), a **bare** `dlopen(name, 0x202)` wrapper with no
   verification, then `getSymbol("pluginAppInfo")` = a bare `dlsym`. (`HmiMain3D`'s own dynsym
   imports neither `dlopen` nor `dlsym` — it delegates the load to `libCoreFramework`.)
   **[CONFIRMED — disasm + `nm -D`]**

### 2.2 The exhaustive list of things that can abort a load

Read end-to-end from the two loader functions. **Every** abort condition, in order:

| # | Gate | Failure string | Grade | Nature |
|---|---|---|---|---|
| 1 | manifest XML loads | `Loading manifest XML failed` | [CONFIRMED] | XML |
| 2 | has a `<plugin>` tag | `Manifest does not contain a <plugin> tag` | [CONFIRMED] | XML |
| 3 | XML well-formed | `Manifest XML data is corrupt` | [CONFIRMED] | XML |
| 4 | name non-empty | `Plugin has no name` | [CONFIRMED] | field presence |
| 5 | **optional** policy hook | `Plugin is not allowed` | [CONFIRMED] | **permission/policy virtual call — not crypto** |
| 6 | DescFile (`.xml`) non-empty | `Plugin does not refer to a UI description file` | [CONFIRMED] | field presence |
| 7 | code-DLL name non-empty | `Plugin has no code behind dynamic link library` | [CONFIRMED] | field presence |
| 8 | `dlopen()` succeeds | `Unable to load dynamic link library: <dlerror>` | [CONFIRMED] | loader |
| 9 | `dlsym("pluginAppInfo")` ≠ NULL | `…does not contain a pluginAppInfo entry point` | [CONFIRMED] | loader |
| 10 | descriptor `+0x10` & `+0x14` ≠ NULL | `The plugin's pluginAppInfo entry point is invalid` | [CONFIRMED] | struct |
| — | **signature / hash / certificate check** | *(no such string exists)* | **[CONFIRMED ABSENT]** | none in the path |

The full loader error-string cluster in `HmiMain3D` `.rodata` (all present exactly once) contains
**no** signature / certificate / hash / integrity / "not coded" load-failure message. The only
"invalid" is *"The plugin's pluginAppInfo entry point is invalid."* **[CONFIRMED — `strings`]**

### 2.3 The "Plugin is not allowed" hook is a boolean, not a signature

Gate #5 (`HmiMain3D:0x24f5658`) is a C++ virtual call: `policy = [this+0x80]; if (policy != NULL
&& policy->vtable[+8](plugin) == 0)` → *"Plugin is not allowed."* **If `policy == NULL` the check
is skipped and the plugin is allowed by default.** It is a permission/policy predicate, **not** a
cryptographic verification. **[CONFIRMED — disasm]**

For the **uncoded** `/Plugins` scan (`coded = false`, no coding list installed), this policy is
consistent with being NULL — matching the observed load of the author's unsigned/uncoded plugin.
The exact store to `[this+0x80]` was not located, so "the uncoded policy is always NULL" is
**[STRONG]**, not CONFIRMED. For the **coded** `/PluginsCoded` scan, whether the installed coding
list is ever wired into this hook is **[UNKNOWN]** — see §5 and §8.

> **Answer to Q1.** What gates an in-process plugin from loading is **only** manifest-validity +
> a valid `pluginAppInfo` entry point, plus an *optional* boolean permission/policy hook. There
> is **no** signature check, **no** integrity/hash check, and — for the uncoded `Plugins/`
> directory — **no** FDL/FA coding-value check, anywhere before or after `dlopen`. **[CONFIRMED
> for `Plugins/`; the coded-dir policy inputs are UNKNOWN.]**

---

## 3. What the `.p7b` / `.p12` files actually do (Q2)

### 3.1 Where runtime crypto really lives

The crypto-linked modules are the **A4A / RemoteApp** plugins under `data/ro/hmiplugins/`, not
the loader:

- **`libhmiremoting.so`** — `NEEDED libcrypto.so.2`; the **full PKCS#7 + CRL verification set**:
  `EVP_VerifyFinal`, `PEM_read_bio_PKCS7`, `PKCS7_free`, `X509_CRL_verify`, `X509_verify_cert`.
  It defines `CAuthVerification`, `CAuthPermManager`, `CAuthToken`, and
  `CRHMIAuthPermHandler::getRHMIApplicationPermissions`. **[CONFIRMED — `readelf`/`nm`]**
- **`libhmia4a.so`** — also `NEEDED libcrypto.so.2`, but its OpenSSL imports are **key/cert
  *reading* only**: `PEM_read_bio_X509`, `PEM_read_bio_RSAPrivateKey`, `BIO_new_mem_buf`,
  `SSL_CTX_use_RSAPrivateKey`. **No** `EVP_VerifyFinal`, **no** `PKCS7`, **no** `X509_CRL_verify`.
  **[CONFIRMED — `nm -D`]**

> ⚠️ Correction to an earlier lead: `libhmiremoting.so` is **not** the *only* module that links
> crypto — `libhmia4a.so` does too. What **is** exclusive to `libhmiremoting.so` is the PKCS#7
> **signature + CRL verification** set. Neither module is the in-process loader, so the
> substantive conclusion (local load does no crypto) is unaffected. **[CONFIRMED]**

### 3.2 What `libhmiremoting` verifies, and when

`libhmiremoting.so`'s certificate logic is the **RemotingServiceSession "SAS"** (session
authentication) flow: `sas_certificate` (*"certificate is invalid or expired"*), `sas_crl` /
`sas_UPDATE_CRL` checked against the system CRL `data/ro/revoke_crl.p7b`, and `rhmi_create: not
permitted for this certificate`. It authenticates the certificate a **remote** app presents when
it connects over the A4A/RemoteApp channel, and derives that remote app's permission set. It is a
**remote-app-path** check, invoked from `CRHMIApplication::initialize()` (the remoting server
session) — **never** by the in-process loader for a local `.so`. **[CONFIRMED]**

### 3.3 So what are the `.p7b`/`.p12` inside `PluginsCoded/`?

`data/ro/PluginsCoded/{SecurityMenu,ActiveSeating}/` each ship the ordinary RA-plugin triplet
(`lib<Name>.so` + `<Name>.manifest` + `<Name>.xml` DescFile) **plus** `<Name>.p7b` (PKCS#7) and
`<Name>.p12` (PKCS#12 key+cert bundle). Two facts pin down what these are **not**:

1. The coded plugins' manifests are **ordinary `<plugin>` manifests** — `<name>`, `<type>App`,
   `<file>`, `pluginAppConnector` (Etch), `DescFile`, Text/Image DB. They declare **no** coding
   feature id and **no** reference to their own `.p7b`/`.p12`. So the manifest loader has nothing
   signing/coding-related to enforce from them. **[CONFIRMED — read the on-disk manifests]**
2. No in-process load-path binary references `.p7b`/`.p12` (`HmiMain3D`, `libhmicoding`,
   `libhmiplugin` all = 0); at runtime `.p7b` is touched **only** by `libhmiremoting`'s cert/CRL
   code, and `.p12` by **no** runtime ELF. **[CONFIRMED — `grep -acF`]**

> **Answer to Q2.** The `.p7b`/`.p12` are **not** consumed by the in-process plugin loader. At
> runtime, `.p7b` (PKCS#7) is verified **only** by `libhmiremoting.so` on the **remote-app** SAS
> path (certificate + CRL for a connecting RemoteApp). `.p12` is read by **no** runtime ELF — it
> is a build / SWDL / provisioning key+cert artifact. The copies inside `PluginsCoded/` are
> provisioning/trust material for those OEM apps' remote-facing surface, **[PLAUSIBLE]**, and are
> **not** a gate on loading a `Plugins/` plugin. **[CONFIRMED absence in the load path.]**

---

## 4. Certificate permissions & the capability map (Q3)

### 4.1 The permission object: a 184-bit capability bitset

Every loaded RA/RemoteApp carries one `CRhmiApplicationPermissions` — a flat **184-bit bitset** at
object offset `+4`, addressed by a numeric permission index with a bounds check at 183:

```
bool get(idx):  if (idx > 183) assert;  return (byte[this+4 + idx/8] >> (idx&7)) & 1
void set(idx,v): byte |= / &=~ (1 << (idx&7))
```

Byte-identical getter/setter logic exists in both `libhmiremoting.so` (`0x515018` / `0x515004`)
and `HmiMain3D` (getter entry `0x2512878`, setter entry `0x2512be0`). **[CONFIRMED — disasm]**

### 4.2 The default (no-certificate) state is **permissive**

The constructor does: `memset(bitset, 0, 23)` → overwrite **all 23 bytes with `0xFF`** (all 184
bits **set**) → then explicitly **clear a 9-index privileged denylist**: `{13,14,15,16,17,18,20,
21,22}`. (`libhmiremoting:0x5150f8`, `HmiMain3D:0x2512958`.) **[CONFIRMED — disasm]**

So a freshly constructed permission object **grants everything except those 9 privileged
capabilities**. An app keeps this state unless something actively narrows it.

### 4.3 Only a verified certificate — over the remoting path — can change it

The one routine that maps a certificate/token into the bitset is
`CRHMIAuthPermHandler::getRHMIApplicationPermissions()` (`libhmiremoting:0x26eeb0`). It
**early-returns**, leaving the permissive default untouched, unless **both** an `IAuthPermManager`
and an app-id are present; only then does it write each bit from the auth token. Its single caller
is `CRHMIApplication::initialize()` — the remoting server session. **[CONFIRMED — disasm]**

An in-process plugin (a `CLocalPluginAppConnector`, `isLocal = true`) never has an auth manager,
so `getRHMIApplicationPermissions` cannot run against it. Corroborating this from the other side:
in `HmiMain3D` the permission **setter is called from 18 sites, all inside the two constructors** —
there is **no** `set()` call from model/app logic, so `HmiMain3D` has no in-process mechanism to
narrow a bitset after construction. The only non-default source is cross-process marshaling from
the remoting process, which a local plugin never triggers. **[CONFIRMED that no in-process code
narrows it; STRONG that the local plugin therefore keeps the permissive default — the exact
object-attach in `CLocalPluginAppConnector` init was not single-stepped.]**

### 4.4 Capability map — what an unsigned plugin can and cannot do

Index → permission resolved from the cert-populate loop via its `R_ARM_GLOB_DAT` relocations.
"Uncertified?" is the default bit from §4.2.

| idx | Permission | Capability | Uncertified plugin? |
|----|----|----|----|
| 0 | ImageDynamic | dynamic images | ✅ granted |
| 1 | ImageStatic | static images | ✅ granted |
| 2 | Image | image models | ✅ granted |
| 3 | Navigation | navigation data | ✅ granted |
| 4 | TTS | text-to-speech | ✅ granted |
| 5 | Phone | phone actions | ✅ granted |
| 6 | Contact | contacts | ✅ granted |
| 7 | Popup | popups | ✅ granted |
| 9 | SpeechGlobal | global speech | ✅ granted |
| 10 | SpeechLocal | local speech | ✅ granted |
| 11 | HmiControl | HMI control | ✅ granted |
| 12 | EventTriggerMenuChange | event-triggered menu change | ✅ granted |
| 19 | LayerAccess | layer access | ✅ granted |
| 13 | UnlimitedFocusEvents | unlimited focus stealing | ❌ needs cert |
| 14 | SASAllowedDevCertWithSpeedLock | interaction / video **in motion** (dev-cert) | ❌ needs cert |
| 15 | PIA | PIA | ❌ needs cert |
| 16 | Map | map-layer overlay | ❌ needs cert |
| 17 | Voice | voice | ❌ needs cert |
| 18 | AppStubButtonEverywhere | entry button everywhere | ❌ needs cert |
| 20 | NotificationCenter | notification-center intrusion | ❌ needs cert |
| 21 | PadFocusEvents | pad focus events | ❌ needs cert |
| 22 | PadFocusEventsPermanent | permanent pad focus events | ❌ needs cert |

**Grading the two halves of this table separately (an important honesty point):**

- The **index → permission → default-bit map** is **[CONFIRMED]** (GOT-reloc resolution + the
  constructor denylist read directly).
- The **behavioural** claim "an uncertified plugin can *actually exercise* capability X" is
  **[CONFIRMED] for the image model only** — `CRemoteAppImageModel` reads bits 0/1/2 at
  registration, caches them, and its per-call gate checks the cached bit before the *"Images …
  are not allowed by certificate!"* path; since `ImageDynamic` (idx 0) defaults **set**, an
  uncertified plugin's images are allowed end-to-end. For the other ~12 "granted" capabilities
  (navigation, TTS, phone, contacts, popup, speech, HmiControl, EventTriggerMenuChange,
  LayerAccess) the per-model enforcement wiring was not individually traced, so those are
  **[STRONG]** (bit defaults set + models read the bitset), not per-capability confirmed.

The image bits being set by default is precisely why the `CRemoteAppImageModel` *"not allowed by
certificate"* warnings **cannot fire for an uncertified plugin** — they only trigger when a
certificate's token *clears* an image bit.

### 4.5 `DevelopmentCertificatePermission` is a permission *level*, not a load gate

The manifest/DescFile declares a permission **level** — `DefaultPermission` vs
`DevelopmentCertificatePermission` (both literals present in `HmiMain3D` and `libhmiremoting`) —
and the certificate is checked against a **development vs production X.509 root**
(`libhmiremoting` carries the *"…against PRODUCTION/DEVELOPMENT root"* verification strings). A
development certificate is what *unlocks* the privileged denylist bits (notably idx 14, dev-cert-
with-speedlock). It gates **capabilities**, not loading. **[STRONG]**

> **Answer to Q3.** The certificate/permission system gates a plugin's **runtime capabilities**,
> not its loading. Capabilities live in `CRhmiApplicationPermissions` (a 184-bit bitset). A plugin
> with **no** certificate gets the **permissive default**: every *normal* capability granted
> (images, lists, navigation, TTS, phone, contacts, popups, speech, HMI control, layer access) and
> only **9 privileged** capabilities denied (interaction/video in motion, notification-center
> intrusion, unlimited/permanent focus stealing, PIA, map overlay, voice). Unlocking the 9
> requires a real BMW-issued certificate delivered over the remoting/A4A path — which an
> in-process plugin has no way to present. **[CONFIRMED for the object default + the map; STRONG
> that the local plugin keeps that default and can use the normal capabilities beyond images.]**

---

## 5. What `PluginsCoded` / "Coded" gates (Q4)

### 5.1 "Coded" means *coding-dependent*, not *signed*

Vehicle coding on the NBT-Evo HMI is served by **`libhmicoding.so`** through `CHmiVariantServer`
(and lower-level `CVACoding`), obtained via `hmiplugin::getVariantServer()`. Its query surface —
`isVariantSet(featureId) → bool`, `isVariantSetInternal(VACodingFeature)`, `getVariantVal`,
`getCodingName` — reads coded feature bytes from the **`syset2`** store over DSI
(`CDsiBinaryStream::getCodingFromSyset2`). `libhmicoding.so` links **no** crypto: coding is a
feature-flag lookup, not cryptography. **[CONFIRMED — `nm -D`, `readelf`]**

Signing and coding make **no cross-calls**: `libhmiremoting.so` lists `libhmicoding.so` as a
transitive `NEEDED` dependency but imports **zero** coding symbols from it (symbol-set
intersection = 0). The two subsystems are independent at the call level. **[CONFIRMED]**

> ⚠️ Wording correction: it is inaccurate to say "`libhmiremoting` imports no coding" at the
> `NEEDED` level (it lists `libhmicoding.so`). The precise, and stronger, statement is that it
> makes **no coding call** — 0 imported coding symbols; the `NEEDED` entry is vestigial.

### 5.2 Coding does **not** gate a dropped-in plugin's load

- The loader lib `libhmiplugin.so` links neither `libhmicoding` nor `libcrypto` and has no
  coding/crypto strings — structurally coding-agnostic. **[STRONG]**
- `HmiMain3D`'s plugin-directory setup registers **both** `/Plugins` and `/PluginsCoded`
  **unconditionally** (`0x108a2e0`/`0x108a324–0x108a408`). The variant server is consulted there
  **only as a filesystem-root path provider** — its return value is *string-concatenated* with
  `"/Plugins"` / `"/PluginsCoded"` — so it cannot be a boolean coding gate, and no branch drops
  `/Plugins`. **[CONFIRMED — disasm]**

### 5.3 The one real coding gate is on the *built-in/static* path, not the filesystem path

`CHmiPluginManager::registerPluginCoded` (`HmiMain3D:0x21f6f0–0x21f9c8`, from
`CHmiPluginManager.h`) **does** check coding: it calls `getVariantServerFast()->isVariantSet(0x5383)`
and, when the feature is **set**, *additionally* registers the coding-dependent built-in classes
`IHmiPadManager` + `IDevPadConfiguration` (via `StaticClassProxy` / `CHmiPluginProxy`); the base
`IHmiAppManager` registers **unconditionally**. These are **statically-linked** plugin classes
compiled into `HmiMain3D`, **not** filesystem `manifest → dlopen → entry-point` loads.
**[CONFIRMED — disasm]**

> Two refinements over the first reading of this function: (a) `isVariantSet` **selects which
> built-in coding-dependent plugins additionally register** — it does not "refuse" a filesystem
> plugin; and (b) the *"…is not coded"* trace is emitted from a **secondary instance-cache
> check**, not directly from the `isVariantSet == false` edge. The load-bearing point is
> unchanged: coding is checked here, on the static/built-in registration path, **never** on the
> filesystem manifest+dlopen path. The mapping vtable-slot `+12 == isVariantSet` is
> signature/string-matched, so that exact identity is **[STRONG]**, not byte-proven; that a
> *coding query* happens here is **[CONFIRMED]** (`getVariantServerFast` is a `libhmicoding`
> export). **[CONFIRMED core / STRONG slot-identity]**

### 5.4 The `PluginsCoded` directory, then, is provenance — not a load gate

`PluginsCoded/{SecurityMenu,ActiveSeating}` are OEM-provisioned, coding-dependent plugins that
load through the **same** crypto-free, coding-free manifest loader as any RA plugin, and
*additionally* carry `.p7b`/`.p12` for the remoting/permission trust layer when they act as a
RemoteApp. "Coded" labels **provenance** (OEM coding-dependent, provisioned + signed); it is
**not** a load-time coding check applied to the plain `/Plugins` directory. **[STRONG]**

> **Answer to Q4.** "Coded" = coding-*dependent* (gated on BMW vehicle Codierung / FA-FDL), in a
> different library (`libhmicoding.so`) from signing (`libhmiremoting.so`), and separate from it.
> Coding does **not** gate loading of a dropped-in RA plugin. The single genuine coding check
> (`registerPluginCoded`) governs whether OEM **built-in static** components activate — not an
> arbitrary `Plugins/` `.so`. **[CONFIRMED for the uncoded path; the coded-dir *optional* policy
> hook (§2.3) is the one place a coding-value gate on filesystem plugins is UNKNOWN.]**

### 5.5 A note on a third enablement axis: FSC/SWT

Distinct again from both coding and signing is the head unit's own feature **licensing**:
FSC/SWT (Freischaltcode / signed software token — `DSYSNBTSwtFscTool`, `DSYSNBTSignatures`,
`DSYSNBTDiffieHellman` in the CarHU/FSC service). `CHmiVariantServer` *merges* SWT-derived flags
with vehicle coding (`setSwtCarplayEnabled`, `setSwtA4AEnabled`). So three enablement notions
coexist — **vehicle coding**, **FSC/SWT licensing**, **plugin signing** — and none of them gates
the in-process plugin load. **[STRONG]** (The FSC verification flow itself was not decompiled;
this rests on the string inventory + the `CHmiVariantServer` SWT setters.)

---

## 6. `OPT_DEBUG` & debug mode: what they change, and don't (Q5)

Three separate "debug/developer" mechanisms exist on this unit; **none gates the in-process
loader.**

### 6.1 `OPT_DEBUG` = system services only, not read by the HMI

`OPT_DEBUG` is a QNX `starter.cfg` **package** flag (`RequestState STOP→RUN`) that launches the
platform daemons `devc-pty` / `inetd` / `qconn` / `qnxcommd`, delivered by a **no-signature SWDL
file copy** of `/opt/sys/etc/starter.cfg` and consumed by the **platform starter**, granting root
ssh/telnet/qconn + filesystem write. `HmiMain3D` never sees it: the binary contains **no**
`OPT_DEBUG`/`starter.cfg` literal, and while `getenv` is imported, `OPT_DEBUG` isn't even an
environment variable. Its **only** relevance to plugins is that fs-write lets the owner *place*
the `.so`/manifest/xml under the read-only `data/ro/`. **[CONFIRMED for the mechanism; STRONG that
the HMI does not observe it.]**

### 6.2 `Hmi_Dev_OE_Base_isDebugModeActive` = an OTF diagnostic, not a gate

This name is **not** a stored config flag. At `HmiMain3D:0x7da8f4` it is registered as the name
argument to an `OTF_CppScopeEntry` constructor — one of ~30 consecutive `Hmi_Dev_OE_Base_*` OTF
**instrumentation scope entries**: a read-only developer/diagnostic query reachable only over the
`BMWOTFagent` channel. That agent is itself dormant on a bone-stock unit — it is gated by a
**separate** lever (the coding `TRACE` bit → runtime-variant vector → a different `starter.cfg`
process), **not** by `OPT_DEBUG`. Nothing in the loader or permission code references
`isDebugModeActive`. **[CONFIRMED — disasm of the OTF registration]**

> Correction to the first reading: `isDebugModeActive` **is** present in `HmiMain3D` (as a *local*
> symbol / string), so the earlier "absent from dynsym → not used" argument is the wrong basis.
> The correct basis is the **read load path itself**: the validate function and
> `ManagedPluginApp::init` contain **no** debug predicate and no branch on any debug flag — the
> only conditional is the optional policy at `[plugin+0x80]`. **[STRONG, on the read path.]**

### 6.3 The real on-screen "developer mode" is `ENTWICKLER_MENUE` — a coding bit, disabled here

The engineering menu is gated by `ENTWICKLER_MENUE`, a **coded FA parameter** (`dg3006` byte 28
bit 6, syset page `PRODUKTLINIE`), read via `libhmicoding` `CVACoding::getCodingVal`. On this car
it is coded **`00` = Disabled** — i.e. **the same as stock**. Per `HmiMain3D` strings it relaxes
some **out-of-process RemoteApp / app-stub** capabilities (`[CAppStubManager] ENTWICKLER_MENU
mode, granted usage of custom focus id … not in Spec`). It is a *coding* flag in a *different*
subsystem — **not** `OPT_DEBUG`, **not** the OTF `isDebugModeActive` — and it does **not** touch
the in-process plugin loader. **[CONFIRMED that it is coded 00 here + distinct; STRONG that its
effect is on the out-of-process app-stub path.]**

> **Answer to Q5.** `OPT_DEBUG` and the HMI's debug facilities are **orthogonal** to the
> in-process plugin loader. The load path branches on no debug predicate and calls no crypto;
> `OPT_DEBUG` only supplies the filesystem write access to place the files. A stock,
> non-`OPT_DEBUG` unit's loader would take the **identical** decision for the same manifest +
> `.so`. **[STRONG — from the read load path + the mechanism separation.]**

---

## 7. Stock unit vs the author's unit

The author's unit differs from a stock unit in exactly **one** load-relevant way, and it is not a
loader relaxation:

| Axis | Author's unit | Stock unit | Same loader decision? |
|---|---|---|---|
| Plugin-loader binary (`HmiMain3D`/`libhmiplugin`/`libCoreFramework`) | vanilla OEM | vanilla OEM | **Yes** — same bytes, no crypto, unconditional dir registration |
| `OPT_DEBUG` | **enabled** (ssh/telnet/qconn + fs-write) | disabled | **Yes** for the loader — `OPT_DEBUG` is not read by the HMI; it only grants the write access to *place* the files |
| `ENTWICKLER_MENUE` | coded **00 = Disabled** | coded 00 = Disabled | **Yes** — same as stock |
| OTF / `isDebugModeActive` | dormant (separate TRACE lever, not set) | dormant | **Yes** — not in the load path anyway |

> **Would a stock, non-`OPT_DEBUG` unit's loader behave identically?** **Yes — [STRONG].** The
> loader is neutral to debug state, coding-agnostic on the uncoded `Plugins/` path, and
> structurally incapable of a signature check (no crypto in-process). The plugin loaded on the
> author's unit because the loader accepts a valid manifest + a `dlopen`-able `.so` exporting
> `pluginAppInfo` — nothing OPT_DEBUG-specific. **The real barrier for a third party is *write
> access* to the read-only `data/ro/`, not a loader gate.** `OPT_DEBUG` (or any other route to
> `data/ro` write access) is what a stock unit lacks; the loader's decision, given the files
> present, is the same.
>
> Two honest caveats: (1) this is proven for the **uncoded `Plugins/`** directory; the
> **`PluginsCoded/`** optional policy hook (§2.3) is UNKNOWN. (2) System-integrity mechanisms
> **outside** the HMI process — e.g. an SWDL/flash-time signature check, or read-only-mount
> enforcement of `data/ro` — are out of scope of this binary set and were not evaluated here.

---

## 8. Open questions / how to settle them

| # | Open question | Grade | How to settle it |
|---|---|---|---|
| 1 | Is the `ManagedPluginApp` policy object at `[this+0x80]` ever non-NULL, and specifically for `/PluginsCoded`? What does its `vtable[+8]` consult — the coding list at `this+0x34`, or a permission table? | [UNKNOWN] (uncoded → NULL is [STRONG]) | Find the `ManagedPluginApp` constructor / the `str [this,#0x80]` store and dump the vtable at slot `+8`. Even if active, it is a boolean `isAllowed`, never a PKCS#7 verify. |
| 2 | Are `PluginsCoded/{SecurityMenu,ActiveSeating}/*.p7b/*.p12` verified at **SWDL / flash / provisioning** time by a component *outside* this HMI carve (the SWDL/update handler or the NBTCarHU/FSC service)? | [UNKNOWN] | RE the SWDL/update handler + `NBTCarHU`. Nothing in the HMI runtime reads them. |
| 3 | Do the coded filesystem plugins gate their **menu-entry visibility** on coding at runtime (an `onCheckAppAvailable` / `CRemoteApplication` availability query into `CHmiVariantServer`) after load? | [UNKNOWN] | Disassemble the `CRemoteApplication` availability path. This would be a *visibility* gate, not a *load* gate — it does not contradict §2. |
| 4 | Per-model enforcement of the non-image capabilities (navigation, TTS, phone, contacts, popup, speech, HmiControl, EventTriggerMenuChange, LayerAccess) for a local plugin. | [STRONG], not per-capability confirmed | Map each of the getter's 21 call-sites to its `(model, permission-index)` pair. |
| 5 | The `.manifest` enumeration / `ManifestScanner` step between directory registration and `ManagedPluginApp` parse was inferred, not single-stepped. | [PLAUSIBLE] | Trace `PluginFramework::ManifestScanner::visit` in `libhmiplugin.so`. Does not affect the crypto verdict (that lib has no crypto). |
| 6 | Could a `PluginsCoded` app that *also* exposes a RemoteApp/A4A interface be gated by the certificate on its **remote-facing** entry points, even though its in-process load is not? | [PLAUSIBLE] | The in-process load and the A4A cert gate are architecturally separate; a hybrid app's remote surface would still hit the SAS cert path. Untested. |

---

## 9. Sources & method

- **Owner-authorized, offline-carve reverse engineering** of the author's own titled NBT-Evo head
  unit (100 % vanilla OEM firmware, `OPT_DEBUG` enabled for system access only). No hardware was
  touched for this analysis; it is a static read of a flash carve.
- **Binaries** (paths under `opt/hmi/ID5/`):
  `bin/HmiMain3D`; `lib/{libhmicoding.so, libhmiplugin.so, libhmizip.so, libCoreFramework.A.so,
  libAppFramework.A.so}`; `data/ro/hmiplugins/{libhmiremoting.so, libhmia4a.so}`;
  `data/ro/PluginsCoded/{SecurityMenu,ActiveSeating}/*`; `data/ro/revoke_crl.p7b`.
- **Method.** Structural facts (`NEEDED` lists, symbol sets, strings, on-disk files) were verified
  directly with `readelf -d`, `nm -D`, `strings`, `grep -acF`, and file listings — and were
  re-verified against the carve while writing this document. Control-flow claims (the loader
  functions, the permission constructor/getter/setter, `getRHMIApplicationPermissions`,
  `registerPluginCoded`, the directory registration, the OTF scope registration) come from the
  lead's targeted ARM/capstone disassembly (host `objdump` cannot disassemble this ARM EABI5
  binary; string references use GOTOFF addressing against GOT base `0x39e7930`, which naive
  absolute-xref searches miss). All four research angles were adversarially verified; where a
  verifier downgraded a claim, the **corrected** grade is used here.
- **Confidence is graded on every material claim** per the legend at the top. An explicit
  **[UNKNOWN]** with a way to settle it (§8) is deliberately preferred over invented certainty.
