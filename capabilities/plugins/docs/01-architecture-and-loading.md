# 01 — Architecture, Plugin Discovery, Loading & Lifecycle

How the NBT-Evo HMI process (`HmiMain3D`) discovers, `dlopen()`s, validates, constructs and
runs a loose-file **RA plugin** — from the on-disk directory layout, through the
`pluginAppInfo` descriptor, to `onInit()` / `onFinalize()`.

> **Scope & authorization.** This document describes the *mechanics* of the NBT-Evo HMI's
> RA-plugin extension point so that developers can write menu apps for **their own** head
> units. Everything here was reverse-engineered from an offline flash carve and owner-authorized
> work on the author's own titled vehicle. No car-specific network addresses, VINs, or private
> diagnostic payloads are part of the SDK — those belong to a private app built on top of this
> mechanism. Every path below is generic to the platform.

> **Evidence legend.** Claims are tagged so you know how far to trust them:
> **[CARVE]** = confirmed by a byte in the flash image (a binary string/symbol, or an OEM
> manifest/DescFile on disk).
> **[PROOF]** = verified end-to-end on the author's OPT_DEBUG-enabled unit — the reference
> plugin's on-car load test, where the marker files fire. This is a claim about the author's own
> unit only, not about a stock (no-OPT_DEBUG) unit.
> **[RECON]** = reconstructed ABI, hand-declared in the SDK headers — correct enough to build
> and load, but not lifted verbatim from BMW source.
> **[INFER]** = a reasonable reading of the evidence whose exact runtime detail the carve does
> not settle.

---

## 1. What `HmiMain3D` is

The entire on-screen experience of an NBT-Evo head unit — every menu, list, popup and
animation — is produced by a **single process**, `HmiMain3D`: a large dynamically-linked
ARM ELF (`APPLICATION_MAP.md` §0, item 6: *"The HMI is one process, `HmiMain3D` — a 59.8 MB
dynamically-linked ARM ELF …"*). That process runs on the head unit's TI OMAP5432 application
processor under QNX Neutrino 6.5.0 SP1 (`APPLICATION_MAP.md` §0, item 1: *"two QNX Neutrino
6.5.0 SP1 computers"*; item 2: *"`hu-omap` — TI OMAP5432 ES2.0 … runs the experience: HMI …"*).

`HmiMain3D` is *not* statically self-contained — it pulls in 56 shared libraries at run time
(`DT_NEEDED` count = 56 **[CARVE]**), and among them are the two that matter to us:
`libAppFramework.A.so` and `libCoreFramework.A.so` (`APPLICATION_MAP.md` §4.1). Those two
libraries are the **RHMI (Remote HMI) application framework** — namespace `bmw::`, classes
`PluginApp` / `RHMIInterfaceVersion` / `Bundle` (`APPLICATION_MAP.md` §7).

An **RA plugin ("Remote Application" plugin)** is a menu app written against that framework,
compiled to a shared object, and dropped into a directory that `HmiMain3D` scans at startup.
The framework discovers it, `dlopen()`s it, reads a descriptor symbol, constructs your app
object, and asks the declarative HMI engine to draw the menu entry your plugin declares. Your
`.so` never draws pixels itself — it feeds data models and receives callbacks; the HMI renders.

### 1.1 Three different things are called a "plugin" — do not conflate them

`HmiMain3D` hosts three unrelated extension mechanisms. This SDK documents **only the first**.

| # | Mechanism | Loaded from | Artifact shape | What it is | This SDK? |
|---|---|---|---|---|---|
| 1 | **RA plugin** (RHMI menu app) | `data/ro/Plugins/`, `data/ro/PluginsCoded/` | `<Name>.manifest` + `<Name>.xml` (DescFile) + `lib<Name>.so` exporting `pluginAppInfo` | A menu app: declares a menu entry + screens + data models; framework `dlopen`s it and calls `create()` | **YES** |
| 2 | **Device / proxy layer** (`THmiPluginProxy`) | compiled *into* `HmiMain3D` via `libhmiplugin.so` | C++ template instantiations `hmiplugin::THmiPluginProxy<CImpl,IInterface>` | In-process abstraction over "everything outside the process" (`IDev*`/`CDev*`, 160 bindings) — the device-abstraction layer | No |
| 3 | **Bundle plugin** | `data/ro/hmiplugins/` | `<Bundle>`-schema XML + `lib<name>.so` exporting a `*Bundle` symbol | RHMI *infrastructure* services (e.g. `RemotingPlugin` → `libhmiremoting.so`, `A4APlugin` → `libhmia4a.so`) | No |

Mechanism #2 is the in-process device layer (`APPLICATION_MAP.md` §4.3). It uses a completely
different loader path (a template registry — no `.manifest`, no `pluginAppInfo`), and it is
what an earlier note loosely called a "device-abstraction layer." **"Populus" is not a firmware
name** — a `grep -ri populus` over the whole carve returns nothing (`APPLICATION_MAP.md` §7); it
is only the author's informal nickname for this in-process device-abstraction layer, whose real
firmware artifacts are `libhmiplugin.so` and the `THmiPluginProxy<Impl,Iface>` / `CPxy*` classes.
If you are here to add a menu item, you want mechanism #1 and can ignore #2 and #3 entirely.

Mechanism #3 uses a distinct XML schema — a `<Bundle exportedSymbolName=… implementedInterface=…>`
root with `<Plugin>` children — nothing like an RA DescFile:

```xml
<!-- data/ro/hmiplugins/RemotingPlugin.xml — a BUNDLE plugin, NOT an RA plugin -->
<Bundle exportedSymbolName="RemotingBundle" implementedInterface="RemotingBundle" path="hmiremoting">
  <Plugin exportedSymbolName="CDataExchangeService" implementedInterface="IDataExchangeService" version="1.0.0.0" autostartDelay="0">
    <Dependency requiredInterface="IA4AAudioService" />
  </Plugin>
</Bundle>
```

`RemotingPlugin` / `libhmiremoting.so` is in fact the RHMI *remoting host* that your RA plugin
runs on top of. That matters for lifecycle timing — see §6.

---

## 2. Anatomy of an RA plugin: files in one directory

An RA plugin is **not** an archive or a package — it is a plain directory of loose files that
you copy onto the head unit. For a **code-backed** plugin (the developer case), the minimal set
is exactly three artifacts:

| File | Role | Format | Read by |
|---|---|---|---|
| `<Name>.manifest` | Loader config — the entry point the scanner reads | XML, root `<plugin>` | the plugin scanner, **first** |
| `<Name>.xml` (the *DescFile*) | UI description — menu entry, screens, components, actions, data models | XML, root `<pluginApps>` | the HMI integrator, **after** load |
| `lib<Name>.so` | The compiled ARM/QNX code, exporting C symbol `pluginAppInfo` | QNX ELF shared object | `dlopen`/`dlsym`, **after** manifest parse |

The word "three files" applies to the code-backed case only. The loader also supports two
code-less backings selected by the manifest's `<file>` token (§4.2): a **DescFile-only** plugin
ships *no* `.so` at all, and a **statically-linked** plugin's code is compiled into `HmiMain3D`
itself. A developer writing their own menu app almost always wants the code-backed form.

OEM plugins ship additional optional files in the same directory — a text database, an image
database, a bitmap folder, and a signature/certificate pair — all named by the manifest
(§5.3). None of those are required for a working plugin: the reference plugin ships only the
three above and loads successfully **[PROOF]** (`capabilities/plugins/docs/08-building-and-deploying.md`
line 3–6).

The directory itself becomes the substitution token **`{pluginDir}`**, which the manifest uses
to refer to its own siblings (§4). `{pluginDir}` is a literal string constant inside `HmiMain3D`
at file offset `0x300f900` **[CARVE]**, in the same loader rodata cluster as the `DescFile`
constant at `0x300f8bd` and the code-less tokens `{xmlOnly}` (`0x300f8f6`) and `{staticLibrary}`
(`0x300f90c`). The substitution itself is driven by the `ManagedPluginApp::PLUGIN_DIR_WILDCARD`
sentinel, spliced with `ManagedPluginApp::PATH_DELIMITER` **[CARVE]** (symbols
`_ZN16ManagedPluginApp19PLUGIN_DIR_WILDCARDE`, `_ZN16ManagedPluginApp14PATH_DELIMITERE`) — the
loader replaces the wildcard with the plugin's own directory and joins path segments with the
delimiter, which is why a manifest never hard-codes an absolute path and the directory can be
renamed or moved freely.

---

## 3. The plugin search directories

At startup the framework scans well-known directories under the HMI's read-only data root,
`/opt/hmi/data/ro/` (a literal constant in the binary at offset `0x2af8ec2` **[CARVE]**; on
disk this path is a symlink into `…/opt/hmi/ID5/data/ro/`, `APPLICATION_MAP.md` §2.5). Three
directory constants are compiled into `HmiMain3D` **[CARVE]**:

| Directory (binary constant) | Offset in `HmiMain3D` | Purpose |
|---|---|---|
| `/Plugins/` | `0x2af4ae9` | **Uncoded** drop-in plugins — the developer directory |
| `/PluginsCoded` | `0x2deaab1` (genuinely adjacent to a bare `/Plugins` at `0x2deaaa8`, 9 bytes away) | **Coded** OEM plugins, gated by vehicle coding |
| `hmiplugins` | `0x2aef03e` | Bundle plugins (mechanism #3, §1.1) — *not* RA menu apps |

(The `.manifest` constant lives at `0x2af4e90`, in the same loader rodata cluster as the
`/Plugins/` constant.)

`data/ro/Plugins/` **does not exist in the OEM image** — it ships empty / absent
(`DEPLOY.md` line 4: *"create the `Plugins/` dir — it does not exist yet; sibling of
`PluginsCoded/`"*). It is nonetheless a live scan root: the directory constant is baked into
the loader, so a plugin placed there is discovered. This is the directory the reference plugin
uses.

`data/ro/PluginsCoded/` holds the OEM RA plugins that shipped on this car — `SecurityMenu` and
`ActiveSeating`. Their directories also contain a `.p7b` (PKCS#7 detached signature) and a
`.p12` (PKCS#12 certificate bundle), which `data/ro/Plugins/` plugins do not have.

### 3.1 "Coded" vs "uncoded", "signed" vs "unsigned"

These two axes are independent, and both are visible in the carve:

- **Coded** = the plugin's availability is gated by the vehicle's coding data. The loader has a
  dedicated failure path for it: `Failed to register coding-dependend plugin %s with code %d`
  (binary offset `0x2aedaae`) as distinct from the general `Failed to register plugin %s with
  code %d` (`0x2aec516`) **[CARVE]**. The `PluginsCoded/` directory name is exactly this
  concept. Which coding parameter enables a given coded plugin is not resolved by the carve
  (see Open Questions). An **uncoded** plugin (in `Plugins/`) carries no such gate.
- **Signed** = the plugin directory carries a `.p7b`/`.p12` certificate. On this platform the
  certificate appears to govern *privileged capabilities* rather than mere loadability — e.g.
  the string `RHMI popup not allowed (Certificate does not allow popups or max. count
  exceeded)` (offset `0x2e16300`) ties a certificate to a capability grant **[CARVE][INFER]**.
  An **unsigned** plugin simply omits those files.

**The load-decisive fact for developers:** an **unsigned + uncoded** plugin placed in
`data/ro/Plugins/<Name>/` is discovered, `dlopen`ed and constructed — verified end-to-end, and
confirmed on-car (the owner's own unsigned plugin ran from `Plugins/` on a stock unit). This is
the whole point of the reference plugin's *stage-1* build **[PROOF]**. The load gate enforces
**no signature**: `HmiMain3D`, `libhmiplugin.so` and `libhmicoding.so` link no cryptography
(byte-grep: 0 `PKCS7`/`X509`/`libcrypto`), and the complete `ManagedPluginApp::init` abort list
(`HmiMain3D:0x24f5330–0x24f6060`) is just manifest-field presence + one *optional* boolean
policy predicate (`this->[0x80]->vtable[+8]`, `0x24f5658`) + `dlopen`/`dlsym("pluginAppInfo")`
null-checks — no signature/cert/hash branch exists, and the policy hook is the **same, coding-
independent** object for both scan roots. OPT_DEBUG only grants the filesystem write to place
the files; it does not change the gate.
`diagnostics.cpp` writes two marker
files — one from a `.so` constructor (fires the instant `dlopen()` runs) and one from
`create()` (fires when the framework accepts the descriptor and instantiates the app):

```c
// capabilities/plugins/reference/example-plugin/hello_plugin_stage1.cpp:21-22 — proves DISCOVERY + dlopen
__attribute__((constructor))
static void diag_on_load() { marker("/tmp/diag_plugin_loaded", "libDiagnostics.so dlopened"); }
```

Deploy = copy the three files into `data/ro/Plugins/Diagnostics/` and restart the HMI; PASS =
the marker files appear (`DEPLOY.md` line 16–20). Because the plugin is loose files and nothing
in the HMI binary is touched, it is fully reversible: `rm -rf` the directory and restart
(`DEPLOY.md` line 22–24).

---

## 4. The manifest: the entry point that names everything else

The **manifest is the entry point**; it names the other artifacts. The loader reads it first
(it is what the directory scan looks for — the `.manifest` constant is co-located with the
directory constants in the binary, §3). Here is the complete reference manifest — this is the
*whole* schema you need for an uncoded, code-backed plugin:

```xml
<!-- capabilities/plugins/reference/example-plugin/Diagnostics.manifest -->
<?xml version="1.0" encoding="utf-8"?>
<plugin>
    <name>Diagnostics</name>                          <!-- required: the plugin's name -->
    <type>App</type>                                  <!-- App = an RA menu app -->
    <file>{pluginDir}/Diagnostics</file>              <!-- base name -> lib<base>.so -->
    <config>
        <autoStart>yes</autoStart>                    <!-- start at HMI bring-up -->
        <dependencies>
            <pluginAppConnector>
                <type>Etch</type>                     <!-- the RPC/serialization connector -->
                <id>100</id>                          <!-- connector instance id -->
                <asyncCallbacks>yes</asyncCallbacks>
            </pluginAppConnector>
        </dependencies>
        <parameters>
            <DescFile>{pluginDir}/Diagnostics.xml</DescFile>   <!-- locates the DescFile -->
        </parameters>
    </config>
</plugin>
```

Field-by-field, each backed by a loader string in `HmiMain3D` **[CARVE]**:

| Manifest node | Meaning | Loader gate if missing/invalid |
|---|---|---|
| `<plugin>` root | Marks the file as a plugin manifest | `Error: Manifest does not contain a <plugin> tag` (`0x300f969`) |
| `<name>` | Plugin identity (dedup key) | `Error: Plugin has no name` (`0x300f99a`) |
| `<type>App</type>` | RA menu-app type (see §4.1) | (rejected as not an app) |
| `<file>` | The plugin's code backing — one of three tokens (§4.2) | `Error: Plugin has no code behind dynamic link library` (`0x300fa23`) |
| `<parameters><DescFile>` | Path to the UI DescFile | `Error: Plugin does not refer to a UI description file` (`0x300f9ec`) |
| `<dependencies><pluginAppConnector>` | RPC connector the app talks over | `Error: Plugin has no valid PluginAppConnector` (`0x300fa7f`) |
| `<config><autoStart>` | Start at bring-up vs on demand | (literal constant `autoStart` present) |

Two details worth internalizing beyond the field table:

1. **`{pluginDir}` is substituted with the plugin's own directory** before any path is opened
   (via `PLUGIN_DIR_WILDCARD` + `PATH_DELIMITER`, §2), so the manifest is position-independent —
   you can rename/move the directory freely.
2. **The DescFile is located *only* via `<parameters><DescFile>`.** There is no naming
   convention that ties `Foo.xml` to `Foo.manifest` automatically; the manifest points at it
   explicitly. (By convention everyone names it `<Name>.xml`, but the loader follows the path.)

The **connector** (`<pluginAppConnector>`) deserves a note: the OEM plugins declare
`<type>Etch</type>` (Apache Etch, the RPC/serialization layer RHMI uses) with a numeric `<id>`
— `100` here, `200` for `SecurityMenu`, `17` for `ActiveSeating`
(`SecurityMenu.manifest`, `ActiveSeating.manifest`) **[CARVE]**. Inside the framework this
becomes a `CLocalPluginAppConnector` (real class symbol `_ZTV24CLocalPluginAppConnector`) that
bridges your in-process `PluginApp` to the HMI. `asyncCallbacks=yes` means your `raAction`
callbacks are delivered asynchronously **[INFER]**. (A field-by-field manifest deep-dive lives
in the sibling doc `02-manifest-format.md`; this section is the loader's-eye view.)

### 4.1 `<type>` and the name-collision (dedup) rule

Every RA menu app in the carve declares `<type>App</type>` — `Diagnostics`, `SecurityMenu` and
`ActiveSeating` all use it, and it is the only `<type>` value observed. `App` selects the
RA-menu-app kind; a code-less variant is chosen by the `<file>` *token* (§4.2), not by a
different `<type>`.

`<name>` is the plugin's identity and its **dedup key**. During the scan the loader distinguishes
a first sighting from a repeat: it logs `Found plugin: ` (`0x300f633`) for a new plugin and
`Found plugin already present: ` (`0x300f614`) when a plugin of that name has already been
registered **[CARVE]**. A duplicate-named plugin therefore does not silently co-exist; the
second is treated as already-present rather than loaded again. Separately, attempting to bring
up a plugin that is already live is refused with `Error: Plugin already running` (`0x300f925`)
**[CARVE]**. Practical rule: **pick a unique `<name>` that does not collide with an OEM plugin**
(`SecurityMenu`, `ActiveSeating`, …) or with another plugin you have installed, or the loader
will keep the first and drop yours.

### 4.2 The three `<file>` backings

The `<file>` element does not always name a `.so`. `HmiMain3D` recognizes three tokens, each a
`ManagedPluginApp` sentinel **[CARVE]** (symbols alongside the rodata cluster at §2):

| `<file>` value | Sentinel | Loader behavior | Use case |
|---|---|---|---|
| `{pluginDir}/<base>` | `PLUGIN_DIR_WILDCARD` (`_ZN16ManagedPluginApp19PLUGIN_DIR_WILDCARDE`) | Substitute `{pluginDir}`, then `dlopen` `<dir>/lib<base>.so` | **Developer / normal code-backed plugin** |
| `{xmlOnly}` | `XML_ONLY_PLUGIN` (`_ZN16ManagedPluginApp15XML_ONLY_PLUGINE`) | No `.so`; the plugin is a declarative DescFile only — no C++ code is loaded | A pure UI declaration with no behaviour of its own |
| `{staticLibrary}` | `STATIC_LIBRARY_WILDCARD` (`_ZN16ManagedPluginApp23STATIC_LIBRARY_WILDCARDE`) | No `.so`; the implementation is statically linked into `HmiMain3D` | OEM built-in implementations |

So the `Error: Plugin has no code behind dynamic link library` gate fires only on the
`{pluginDir}/<base>` path when the named `.so` is missing or unresolvable — a `{xmlOnly}`
plugin legitimately carries no code, and a `{staticLibrary}` plugin's code is already inside the
host binary. As a developer you use `{pluginDir}/<base>`; the base name has **no `lib` prefix
and no `.so` suffix** — the manifest says `Diagnostics`, and the loader resolves that to
`libDiagnostics.so`, matching your build's soname
(`capabilities/plugins/reference/example-plugin/Makefile` line 7: `-Wl,-soname,libDiagnostics.so`).

### 4.3 The `.so`: the `pluginAppInfo` descriptor

The one thing the loader requires from a code-backed plugin is a single exported, un-mangled C
symbol named **`pluginAppInfo`** (a literal constant at `0x300fb1e`; the loader `dlsym()`s it,
and rejects the plugin with `Error: Plugin does not contain a pluginAppInfo entry point`
(`0x300fb2c`) if absent, or `Error: The plugin's pluginAppInfo entry point is invalid`
(`0x300fb68`) if malformed) **[CARVE]**. It is a 24-byte descriptor struct **[RECON]** (layout
reconstructed from `SecurityMenu` / `ActiveSeating`, `bmw_abi.h` line 49–57):

```c
// bmw_abi.h:49-57  — the descriptor the loader dlsym()s (24 bytes)
struct PluginAppInfo {
    unsigned int   abiVersion;    // +0   ctor reads low16=major, high16=minor
    const char*    name;          // +4
    const char*    vendor;        // +8
    unsigned int   ifaceVersion;  // +12  read as RHMIInterfaceVersion
    bmw::IPluginApp* (*create)(bmw::IDispatcher&, const char*,
                               const bmw::Bundle&, const bmw::Bundle&);  // +16
    void            (*destroy)(bmw::IPluginApp*);                        // +20
};

extern "C" PluginAppInfo pluginAppInfo = {   // diagnostics.cpp:43-50
    1, "Diagnostics", "owner-research", 1, diag_create, diag_destroy,
};
```

`create()` is the factory the framework calls to instantiate your app; it must return a
`bmw::PluginApp` subclass (returned as its primary base `IPluginApp*`, which lives at offset 0).
`destroy()` is called to tear it down. The framework wraps the instance it gets back as an
internal `ManagedPluginApp` (a real `HmiMain3D` class, `_ZTV16ManagedPluginApp`) **[CARVE]**.

The C++ side of all of this — `bmw::PluginApp`'s constructor, its 34-slot primary vtable, and
the non-virtual helpers `updateModel()` / `addHandler()` / `setProperty()` / `post()` — is
covered in the sibling C++ ABI & data-types doc (`05-cxx-abi-and-data-types.md`), with the
runtime API for those calls in `06-runtime-api-reference.md`; the DescFile schema (menu entry,
`hmiState`s, components, `hmiAction` / `raAction`, `raListModel` / `raDataModel`, properties) in
`03-descfile-xml-reference.md`. Here we only need to know that these symbols are real, exported,
and resolved at `dlopen` time — confirmed by `nm -DC libAppFramework.A.so` **[CARVE]**, which
shows `bmw::PluginApp::addHandler`, `::setProperty`, the whole `::updateModel` overload set, and
`::onFinalize` all present as defined text symbols (`T`). The vtable slot order used below
(`onInit` = slot 22, `onFinalize` = slot 23) is itself carve-confirmable from
`libAppFramework.A.so`'s vtable relocations, and matches the reconstructed header
(`bmw_list.h:180`).

---

## 5. The load lifecycle, end to end

### 5.1 Ordered sequence

From cold start to your menu appearing and back:

1. **Scan.** The framework enumerates the plugin directories (`/Plugins/`, `/PluginsCoded`).
   For each subdirectory it looks for a `*.manifest`. On finding one it logs `Found plugin: `,
   or `Found plugin already present: ` if a plugin of that `<name>` was already registered
   (§4.1) **[CARVE]**.
2. **Parse manifest.** Reads `<plugin>`, extracts `<name>`, `<file>`, `<parameters><DescFile>`,
   `<dependencies><pluginAppConnector>`, `<config><autoStart>`. Rejects here with the
   `Error: Plugin has no name` / `…no code behind…` / `…does not refer to a UI description
   file` / `…no valid PluginAppConnector` gates if any required field is missing.
3. **`dlopen(lib<file>.so)`** (for the `{pluginDir}/<base>` backing). The shared object is
   mapped; **all C++ static constructors and any `__attribute__((constructor))` run now** (this
   is the stage-1 load proof, §3.1). Eager symbol resolution means unresolved framework symbols
   would fail here — which is why the SDK headers emit local weak fallbacks for a few undefined
   base dtors (`bmw_list.h` line 19–27). A `{xmlOnly}` / `{staticLibrary}` plugin skips this
   step.
4. **`dlsym("pluginAppInfo")`.** Missing → `Error: Plugin does not contain a pluginAppInfo
   entry point`. Present but malformed (null `create`, bad `abiVersion`) →
   `Error: The plugin's pluginAppInfo entry point is invalid`.
5. **Policy/coding gate.** For a coded plugin, coding is checked (`Failed to register
   coding-dependend plugin %s with code %d`); a disallowed plugin is rejected with
   `Error: Plugin is not allowed` (`0x300f9b5`). Uncoded plugins pass trivially.
6. **`create(dispatcher, name, cfg, res)`.** The framework calls your factory. Your `create()`
   constructs the `bmw::PluginApp` subclass; the base constructor installs the real vtable and
   wires the `PluginAppConnector`. Returns `IPluginApp*`.
7. **`onInit()` (vtable slot 22).** The framework calls your override. This is where you build
   your initial data models (`updateModel(...)`) and register action handlers
   (`addHandler(...)`) — see `bmw_list.h` line 180 (`virtual bool onInit();  // 22  <-- override`)
   and the worked example `diagnostics2.cpp` line 21–53.
8. **Integrate DescFile.** The HMI integrator reads the DescFile (`<pluginApps>`) and builds the
   declared menu entry + screens. Your menu entry now appears in the live HMI. (Integration
   errors surface as `Error: PluginApp %s reported an integration error…` /
   `PluginApplication had an hmiState with id 0.`)
9. **Run.** The user navigates: an `hmiAction` moves between your declared `hmiState`s (handled
   entirely by the HMI); an `raAction` fires a callback into your registered handler with a
   `Parcel` of arguments. You respond by pushing new model data / setting properties.
10. **Teardown.** `onFinalize()` (slot 23) then `destroy()` release the app. For an uncoded
    drop-in, an HMI restart re-runs the whole sequence from step 1.

> **On ordering:** steps 1–4 are strongly evidenced by the manifest field dependencies and the
> loader's own error strings; the *relative* order of the policy gate (step 5) versus `create`
> is **[INFER]** — string layout in the binary is rodata order, not execution order, and this
> was not traced through disassembly.

### 5.2 Sequence diagram

```
 disk: data/ro/Plugins/Diagnostics/          HmiMain3D (UI/dispatcher thread)        your lib<Name>.so
 ┌───────────────────────────────┐          ┌──────────────────────────────┐        ┌───────────────┐
 │ Diagnostics.manifest          │          │  plugin scanner               │        │               │
 │ Diagnostics.xml (DescFile)    │          │                               │        │               │
 │ libDiagnostics.so             │          │                               │        │               │
 └───────────────────────────────┘          └──────────────────────────────┘        └───────────────┘
                                                  │
        scan dir, find *.manifest  ──────────────▶│   "Found plugin: Diagnostics"  (or "already present")
        read <plugin>{name,file,DescFile,conn} ◀──┤   (reject: no name / no .so / no DescFile / no connector)
                                                  │
                    dlopen(libDiagnostics.so) ────┼───────────────────────────────────▶│  .so ctors run
                                                  │                                     │  → /tmp/diag_plugin_loaded  [PROOF]
                    dlsym("pluginAppInfo")   ─────┼───────────────────────────────────▶│  returns &pluginAppInfo
                                                  │   (reject: missing / invalid entry point)
                    coding / "is allowed?" gate   │   (coded only; uncoded passes)
                                                  │
                    create(disp,name,cfg,res) ────┼───────────────────────────────────▶│  new Diagnostics(...)
                                                  │                                     │  base ctor installs vtable
                                                  │◀────────────────────────────────────┤  return IPluginApp*
                                                  │                                     │  → /tmp/diag_plugin_created [PROOF]
                    onInit()  [vtable slot 22] ───┼───────────────────────────────────▶│  updateModel()/addHandler()
                                                  │◀────────────────────────────────────┤  return true
        Diagnostics.xml  ─── integrate DescFile ─▶│   build menu entry + hmiStates  → ENTRY APPEARS
                                                  │
  user: navigate ─ hmiAction ──────────────────▶ │   (HMI switches hmiState; no callback to you)
  user: press ─── raAction ────────────────────▶ │─────────────────────────────────── ▶│  your handler(Parcel&)
                                                  │
                    onFinalize() [slot 23] ───────┼───────────────────────────────────▶│
                    destroy(app) ─────────────────┼───────────────────────────────────▶│  delete app
 └──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 OEM plugins carry more, but the shape is identical

Compare the reference manifest with `SecurityMenu`'s — the OEM one adds a text DB, an image
DB, and a bitmap path parameter, all located via `{pluginDir}`:

```xml
<!-- data/ro/PluginsCoded/SecurityMenu/SecurityMenu.manifest — extra parameters (all optional) -->
<parameters>
    <DescFile>{pluginDir}/SecurityMenu.xml</DescFile>
    <TextDBFile>{pluginDir}/SecurityMenu_ALL_Texts.zip</TextDBFile>
    <ImageDBFile>{pluginDir}/SecurityMenu_ALL_Images.zip</ImageDBFile>
    <parameter><name>ImagePath</name><value>{pluginDir}/Bitmaps/</value></parameter>
</parameters>
```

Everything above `DescFile` is optional for a minimal plugin — the reference plugin ships none
of it and still loads and renders **[PROOF]**. The `SecurityMenu` directory *also* contains
`SecurityMenu.p12` + `SecurityMenu.p7b` (its certificate/signature) and a `SecurityMenu_Tree.xml`
(a separate `<hmiStateTree>` naming a state hierarchy) — again, none of which the loader
requires for an uncoded plugin.

---

## 6. Where RA plugins sit in HMI bring-up (timing)

`autoStart` plugins are not started the instant `HmiMain3D` launches — they start once the RHMI
remoting layer is up. The binary carries the log line
`[CHmiGenMain::onHmiGenEventState] Remoting ready received. Starting up appmanager autostart
apps` (`0x2dea9cb`) **[CARVE]**. In other words: the Bundle plugin `RemotingPlugin`
(`libhmiremoting.so`, mechanism #3) initializes the RHMI remoting host; when it signals
"Remoting ready," the app manager brings up the `autoStart` RA plugins. This is why the
connector dependency (`<pluginAppConnector><type>Etch</type>`) exists — your plugin is a
*remote application* from the framework's point of view, even though it runs in-process.

Practical consequence: if your plugin's `onInit()` needs a service that itself comes up late,
do not block the UI thread waiting for it in `onInit()` — schedule work instead (§7).

---

## 7. Runtime model (one paragraph; full treatment in sibling docs)

Everything the framework calls on your plugin — `create()`, `onInit()`, every `raAction`
handler, `onFinalize()` — runs on the **HMI UI/dispatcher thread**. You must never block it.
The reference plugin's pattern for long work is to fork an **isolated child process** with
`posix_spawn()` and poll it from the UI thread with a **self-rescheduling `bmw::Runnable`**:
`run()` calls `waitpid(pid, &st, WNOHANG)`, and if the child is still running it re-posts itself
with `post(this, ms)` and returns, so control returns to the dispatcher between polls
(`capabilities/plugins/reference/example-plugin/diagnostics.cpp` line 16–17, 66–67, 201–209, 354–355).
All model/property updates happen on the UI thread; `updateModel()` deep-copies the `DataTable`
so the framework keeps its own copy (`bmw_list.h` line 108–125; `diagnostics2.cpp` line 36–38).
The threading / `Runnable` / child-process details are documented fully in
`07-threading-and-safety-model.md`; the C++ ABI in the sibling doc `05-cxx-abi-and-data-types.md`.

---

## 8. Minimal checklist to get *something* loaded

1. Write a `<Name>.manifest` (§4) — get a **unique** `<name>` (§4.1), `<file>`
   (`{pluginDir}/<base>`, §4.2), `<DescFile>`, and a `<pluginAppConnector>` right.
2. Write a `<Name>.xml` DescFile that declares one menu entry and one `hmiState` (schema in
   `03-descfile-xml-reference.md`).
3. Compile a `lib<Name>.so` that exports `pluginAppInfo` with a working `create()`/`destroy()`
   and (optionally) a `.so` constructor marker so you can prove load (`diagnostics.cpp` is 50
   lines and does exactly this). Build/deploy details: `08-building-and-deploying.md`.
4. `mkdir -p data/ro/Plugins/<Name>/`, copy the three files in, `sync`, restart the HMI.
5. Verify: your marker file appears (load proven) and your menu entry shows up.

---

## Caveats

- **The SDK headers are hand-reconstructed [RECON].** `bmw_abi.h` and `bmw_list.h` were built
  from symbol tables and disassembly of `libAppFramework.A.so` / `libCoreFramework.A.so` /
  `libSecurityMenu.so` / `HmiMain3D`, not from BMW source. Struct sizes are deliberately
  over-padded and layouts are "correct enough to construct and dispatch," per the header
  comments (`bmw_abi.h` line 30–43). The *directory layout, manifest schema, `<file>` tokens,
  DescFile schema, and the `pluginAppInfo` requirement* are all **[CARVE]** — those are bytes on
  disk, not reconstruction.
- **The 24-byte `PluginAppInfo` layout is [RECON]** from `SecurityMenu`/`ActiveSeating`
  (`bmw_abi.h` line 49). It builds and loads, but field offsets past `abiVersion` should be
  treated as validated-by-working rather than proven-by-spec.
- **Loader validation *gate list* is [CARVE]; gate *order* is [INFER].** Every error string in
  §4/§5 is a real constant in `HmiMain3D` at the cited offset, but the sequence in which the
  loader checks them (and whether the coding/allow gate runs before or after `create()`) was
  inferred from the manifest's field dependencies, not traced through control flow. Rodata
  string order is not execution order.
- **Signature semantics are [INFER].** `.p7b`/`.p12` files sit beside OEM coded plugins, and a
  certificate is referenced in a *capability* string (RHMI popups). The reference plugin loads
  with **no** signature from `data/ro/Plugins/`, so a signature is clearly not required for the
  uncoded path — but exactly what the certificate gates for coded/privileged plugins is not
  fully mapped here.
- **This is one firmware build.** All paths, offsets and schemas are from HMI build
  `NBTEvo_ID5_2403` (`APPLICATION_MAP.md` §0). Other NBT-Evo builds/generations (the binary
  even carries alternate roots `start_ID4_HMI.cfg` / `start_ID5_HMI.cfg`) may differ.

## Open questions

- **Which coding parameter enables a `PluginsCoded` plugin?** *(mostly resolved)* At
  registration (`HmiMain3D:0x108a1c4–0x108a2ac`) the HMI queries `libhmicoding`'s `isVariantSet`
  (vtable `+0xc`) for features **`0x0C0E`** and **`0x9C55`** and builds a coding-enabled **name
  list** — `ActiveSeating` / `SecurityMenu` — which it attaches to the `/PluginsCoded` scan root
  (registered `coded=true`, `0x24f15a0`). So the gate **inputs** are those two coding features
  keyed by plugin name. The exact instruction that applies the list to filter a discovered
  `PluginsCoded/` manifest wasn't single-stepped (strong-by-construction), and the compiler-fused
  feature→name pairing isn't pinned 1:1 — but it is a **coding** gate, not a signature one.
- **Signing on `data/ro/Plugins/`: resolved — not enforced.** The load path links no
  cryptography and has no signature branch (§3.1), and the owner's unsigned plugin loaded from
  `Plugins/` on a stock unit. The two scan roots (`/Plugins` `coded=false`, `/PluginsCoded`
  `coded=true`) are registered **unconditionally** (`0x108a344–0x108a408`, straight-line, no
  branch) — there is no in-path switch that "disables a scan root"; doing so would need binary
  modification, not configuration. (Note: in the stock carve only `PluginsCoded/` and
  `hmiplugins/` ship; `Plugins/` is a live, code-registered root the stock image leaves empty —
  which is exactly where an owner drops an uncoded plugin.)
- **`<pluginAppConnector><id>` namespace.** OEM plugins use distinct ids (17/200). The value
  `100` is **not** a loader priority — it is the reference plugin's `<pluginAppConnector><id>`,
  read from the manifest (there is no plugin "priority" field in `HmiMain3D`; the only "priority"
  strings are thread/ProcUnit scheduling). Whether two plugins may share an id, and what the id
  selects on the connector, is still runtime-unverified.
- **Does `autoStart=no` change discovery, or only start timing?** Not tested — all working
  examples use `autoStart=yes`.
- **Exact `dlopen` flags and symbol-resolution mode.** The SDK's weak-dtor workaround
  (`bmw_list.h` line 19–27) plus the Makefile's `-Wl,--allow-shlib-undefined` imply eager
  (`RTLD_NOW`-style) resolution, but the precise flags the loader passes were not extracted.

---

## Sources

The facts above come from an owner-authorized, offline flash carve of the author's own titled
vehicle plus end-to-end validation of a purpose-built reference plugin on the author's
OPT_DEBUG-enabled unit. Primary sources are cited
inline as `path:line`, `path (§section)`, or by binary offset. **[CARVE]** facts are bytes on
disk (loader strings/symbols in `HmiMain3D`, OEM `.manifest`/DescFile files, exported framework
symbols via `nm -DC`); **[PROOF]** facts are verified end-to-end on the author's
OPT_DEBUG-enabled unit (the reference plugin's on-car load test), scoped to that unit and not a
stock one; **[RECON]** facts (the SDK headers `bmw_abi.h` / `bmw_list.h`, and the 24-byte
`PluginAppInfo` layout) are hand-reconstructed ABI — correct enough to build, load and dispatch,
but not lifted from BMW source and marked as such wherever relied upon. Nothing car-specific
(network addresses, VIN, diagnostic payloads) is part of this SDK; the plugin *mechanics* here
are generic to the platform.
