# The `.manifest` File Format

> Complete reference for the NBT-Evo HMI RA-plugin `.manifest` (XML): every element and attribute, the `{pluginDir}`/`{xmlOnly}`/`{staticLibrary}` tokens, the five loader-recognized file-DB keys, and exactly what the `ManagedPluginApp` loader requires versus ignores.

> **Authorization / scope.** Everything here was reconstructed from an offline flash carve and owner-authorized work on the author's own titled vehicle. It is written for a developer working on *their own* head unit. The mechanics below are generic to the NBT-Evo HMI; no car-specific addresses, VINs, or private diagnostic-app details are part of the SDK.

A plugin is a directory of three loose files that the HMI process (`HmiMain3D`) discovers, loads, and runs as a menu app:

| File | Role | Documented in |
|------|------|----------------|
| `<Name>.manifest` | Loader configuration (this document) | **this doc** |
| `<Name>.xml` (the *DescFile*) | Menu entry, screens, components, models, actions | `03-descfile-xml-reference.md` |
| `lib<Name>.so` | Compiled ARM/QNX code exporting `pluginAppInfo` | `05-cxx-abi-and-data-types.md` |

The `.manifest` is the entry point: the loader reads it first, and every other artifact is located *through* it. This document is a complete reference for its XML.

> **Not to be confused with `hmiplugins/*.xml`.** The carve also contains `data/ro/hmiplugins/A4APlugin.xml` and `RemotingPlugin.xml`. Those use a *different* schema — `<Bundle exportedSymbolName="…" implementedInterface="…" path="…"><Plugin … version="…" autostartDelay="…"/></Bundle>`, optionally with `<Dependency requiredInterface="…"/>` children (`A4APlugin.xml:2-4`, `RemotingPlugin.xml:2-5`) — and belong to a *distinct* RHMI/remoting bundle mechanism, **not** the RA plugin loader: their `path` attributes name the bundle libraries (`RemotingPlugin.xml` → `hmiremoting` = `libhmiremoting.so`; `A4APlugin.xml` → `hmia4a`), loaded by that remoting infrastructure. That is separate again from the in-process device-abstraction layer `libhmiplugin.so` (the author's notes nickname it "Populus"; it is not a framework name found in the unit) — and none of the `.manifest` tokens documented below appear in `libhmiplugin.so` either (grep: `pluginDir`, `DescFile`, `autoStart`, `pluginAppConnector`, `asyncCallbacks`, `ManagedPluginApp` all 0 hits); they all live in `HmiMain3D`. Do not model your plugin on the `<Bundle>` format.

---

## 1. Where manifests live, and how they are discovered

The RA-plugin loader is the class `ManagedPluginApp` (in `HmiMain3D`; in-binary source path `../../src/framework/lib/rhmiappmanager/src/ManagedPluginApp.cpp`). At HMI start it scans two sibling directories under `…/opt/hmi/ID5/data/ro/`:

| Directory | Meaning | Coding gate |
|-----------|---------|-------------|
| `Plugins/` | Uncoded plugins | **No** — always loaded if present |
| `PluginsCoded/` | Coding-gated plugins | **Yes** — subject to a vehicle-coding allow check |

Both directory names are literals in `HmiMain3D` (`/Plugins`, `/PluginsCoded`, each present once), and the two OEM plugin names appear next to them in the same string block (`ActiveSeating`, `SecurityMenu`). For each subdirectory the loader looks for a file ending in `.manifest` (literal `.manifest` in `HmiMain3D`; the driver `CDevHMIControl` logs `[DHCtrl] Loading plug-in: %s.`). The scan itself is traced by two log fragments in the binary — `Searching in Plugin directory: ` and `Searching in subDir of Plugin directory: ` — confirming the loader walks the directory and then its immediate subdirectories.

Path assembly uses a fourth `ManagedPluginApp` static beside the three `<file>` wildcards: `PATH_DELIMITER` (symbol `_ZN16ManagedPluginApp14PATH_DELIMITERE`), used to join the resolved directory to the file basenames.

> **On a missing directory** the loader emits a message assembled at runtime from two adjacent format fragments — `Plugins directory '` + *path* + `' not found` (a `printf`-style `%s` join, **not** a single verbatim literal) — and continues. Both fragments are separately present in `HmiMain3D`; quoting them here reflects that they are two pieces, to keep the doc's byte-exact citation standard honest.

**Discovery rule of thumb:** one plugin = one subdirectory = one `.manifest`. The subdirectory is what `{pluginDir}` resolves to (Section 5).

> **Deployment / validation procedure — verified end-to-end on the author's OPT_DEBUG-enabled unit.** The reference stage-1 plugin proves discovery on the author's own unit without signing or coding: its shared object writes `/tmp/diag_plugin_loaded` from an ELF `__attribute__((constructor))` (fires the instant the loader `dlopen()`s the `.so`) and `/tmp/diag_plugin_created` from `create()` (`capabilities/plugins/reference/example-plugin/hello_plugin_stage1.cpp:6-7,21-22,29`). The procedure is: drop the three files into a hand-created `…/data/ro/Plugins/<Name>/` directory (sibling of `PluginsCoded/`), restart the HMI to force a re-scan, then check for the two marker files (`DEPLOY.md:3-5,16-20`). On the author's OPT_DEBUG-enabled unit both markers appear — the plugin is discovered and `dlopen`'d from the uncoded `Plugins/` path, and its menu entry then renders. **Scope:** this is verified on the author's own OPT_DEBUG-enabled unit only; it is *not* a claim about a stock unit. A stock unit enforces **no signature** on load (the loader links no cryptography; confirmed on-car) — see `14-signing-and-coding.md`. A plugin placed under `PluginsCoded/` additionally requires passing the coding allow check (`HmiMain3D`: `Error: Plugin is not allowed`); the two OEM examples ship there because they are coding-gated features.

---

## 2. The example manifest, in full

This is the reference plugin's manifest (`capabilities/plugins/reference/example-plugin/Diagnostics.manifest`). It is the **minimal shape that loads** — every element shown is load-bearing.

```xml
<?xml version="1.0" encoding="utf-8"?>
<plugin>
    <name>Diagnostics</name>
    <type>App</type>
    <file>{pluginDir}/Diagnostics</file>
    <config>
        <autoStart>yes</autoStart>
        <dependencies>
            <pluginAppConnector>
                <type>Etch</type>
                <id>100</id>
                <asyncCallbacks>yes</asyncCallbacks>
            </pluginAppConnector>
        </dependencies>
        <parameters>
            <DescFile>{pluginDir}/Diagnostics.xml</DescFile>
        </parameters>
    </config>
</plugin>
```

Note `<file>` names the shared object **without** the `lib` prefix or `.so` suffix: `{pluginDir}/Diagnostics` resolves to `libDiagnostics.so` in the plugin directory (Section 5).

---

## 3. Element reference

The document is a shallow tree: a `<plugin>` root, a flat identity block (`name`/`type`/`file`), then a `<config>` subtree holding startup, dependencies, and parameters.

### 3.1 `<plugin>` — root element

| | |
|---|---|
| **Required** | Yes. The loader rejects any manifest whose root is not `<plugin>`: `Error: Manifest does not contain a <plugin> tag`. |
| **Attributes** | None observed. |
| **Children** | `<name>`, `<type>`, `<file>`, `<config>` (in that order in all samples; order-independence not proven — keep this order). |

### 3.2 `<name>` — plugin identity

| | |
|---|---|
| **Required** | **Yes.** Missing name is fatal: `Error: Plugin has no name`. |
| **Value** | A short identifier string (`Diagnostics`, `SecurityMenu`, `ActiveSeating`). |
| **Convention** | Matches the directory name and the `<file>`/`<DescFile>` basenames. Not proven to be enforced, but everything the developer references by `{pluginDir}/<Name>…` assumes it. |

### 3.3 `<type>` — application kind

| | |
|---|---|
| **Required** | No (treated as advisory). |
| **Observed value** | `App` — the only value across all three manifests. |
| **Loader behavior** | The loader reads it and **logs** it (`Warning: Plugin type is `) but does **not** switch on it: there is no *standalone* `App` string — no whole string equal to `App` for the loader to compare the `<type>` value against — anywhere in `HmiMain3D` (`strings \| grep -xF App` = 0). ("App" does occur as a *substring* of unrelated messages such as `App '%s' not found!`, but nothing the connector/loader matches `<type>` against.) Use `App`; other values are unverified. |

### 3.4 `<file>` — code object, with wildcards

`<file>` tells the loader where the plugin's code lives. Its value is a path in which a leading token may be substituted.

| Form | Meaning |
|------|---------|
| `{pluginDir}/<Name>` | Dynamic plugin: load `lib<Name>.so` from the plugin directory. **This is the normal case.** |
| `{xmlOnly}` | *(reconstructed)* Description-only plugin — no shared object; the plugin is pure DescFile UI with no C++ behind it. |
| `{staticLibrary}` | *(reconstructed)* Plugin code is statically linked into `HmiMain3D` rather than loaded from a `.so`. |

The three tokens are consecutive literals in `HmiMain3D` (`{xmlOnly}`, `{pluginDir}`, `{staticLibrary}`, adjacent in the string dump) — exposed as the `ManagedPluginApp` statics `XML_ONLY_PLUGIN`, `PLUGIN_DIR_WILDCARD`, and `STATIC_LIBRARY_WILDCARD` (symbols `_ZN16ManagedPluginApp15XML_ONLY_PLUGINE`, `…19PLUGIN_DIR_WILDCARDE`, `…23STATIC_LIBRARY_WILDCARDE`, each present once).

For a dynamic plugin the loader then:
1. Loads the object (`ManagedPluginApp::init(): mDynamicLibrary.load( … )`; failure → `Error: Unable to load dynamic link library: `).
2. `dlsym`s the exported descriptor **`pluginAppInfo`** (literal in `HmiMain3D`; missing → `Error: Plugin does not contain a pluginAppInfo entry point`; malformed → `Error: The plugin's pluginAppInfo entry point is invalid`).
3. Calls its `create()` (failure → `Error: Unable to create instance of: `).

If `<file>` names no usable object and the plugin is not xml-only/static, the loader fails with `Error: Plugin has no code behind dynamic link library`. See `05-cxx-abi-and-data-types.md` for the `pluginAppInfo` descriptor and `create`/`destroy`.

### 3.5 `<config>` — configuration container

A structural wrapper with no attributes. It holds `<autoStart>`, `<dependencies>`, and `<parameters>`. All three samples nest the startup/connector/parameter data here; treat `<config>` as required because the required `DescFile` and connector live inside it.

### 3.6 `<autoStart>` — start on load

| | |
|---|---|
| **Path** | `<config>/<autoStart>` |
| **Required** | No (token `autoStart` is read by the loader; default when absent is unproven). |
| **Observed value** | `yes` in all three manifests. |
| **Meaning** | Start the plugin (call its lifecycle `start()`/`onInit()`) as soon as it is loaded, rather than lazily on first navigation. Use `yes`. |

### 3.7 `<dependencies>` and `<pluginAppConnector>`

`<dependencies>` wraps the plugin's connector declaration. In every sample it contains exactly one `<pluginAppConnector>`. A **valid** connector is mandatory: `Error: Plugin has no valid PluginAppConnector`.

```xml
<dependencies>
    <pluginAppConnector>
        <type>Etch</type>
        <id>100</id>
        <asyncCallbacks>yes</asyncCallbacks>
    </pluginAppConnector>
</dependencies>
```

| Child | Meaning | Observed values | Notes |
|-------|---------|-----------------|-------|
| `<type>` | Nominal RPC/serialization transport | `Etch` (all three) | **Ignored by value.** The string `Etch` does not appear in `HmiMain3D` at all (0 substring hits). Whatever the type says, the loader instantiates a `CLocalPluginAppConnector` (`…/localpluginappconnector/CLocalPluginAppConnector.cpp`) using a MOST-style serializer (`MOSTSerializer.cpp`). "Etch" is the BMW/Apache-Etch framework name kept for documentation; keep it for convention. |
| `<id>` | Numeric connector / application id used when the app registers with the HMI integrator | `100` (example), `200` (SecurityMenu), `17` (ActiveSeating) | Integer. The OEM apps use distinct ids; uniqueness is recommended but not proven required. |
| `<asyncCallbacks>` | Whether the connector delivers callbacks asynchronously | `yes` (all three) | Boolean-style flag (token `asyncCallbacks` is read by the loader). Use `yes`. |

### 3.8 `<parameters>` — files and custom key/values

`<parameters>` is where the plugin's resource files and any custom settings are declared. Two kinds of children appear:

**(a) Loader-recognized file keys.** These five element names are literals in `ManagedPluginApp` (each present once in `HmiMain3D`) and are looked up by name. Their values are paths (subject to `{pluginDir}` substitution):

| Key | Purpose | Required | In OEM samples? |
|-----|---------|----------|-----------------|
| `<DescFile>` | The DescFile XML (menu/UI description) | **Yes** — missing → `Error: Plugin does not refer to a UI description file` | Yes (all) |
| `<TextDBFile>` | Localized text database (`.zip`) | Optional | SecurityMenu, ActiveSeating |
| `<ImageDBFile>` | Image/bitmap database (`.zip`) | Optional | SecurityMenu, ActiveSeating |
| `<WidgetDBFile>` | Widget database | Optional | **None** — recognized by the loader but unused by our samples |
| `<AssetDBFile>` | Asset database | Optional | **None** — recognized by the loader but unused by our samples |

**(b) Generic `<parameter>` name/value pairs.** Anything else is an opaque setting handed to the plugin (via its config `Bundle`), not interpreted by the loader:

```xml
<parameter>
    <name>ImagePath</name>
    <value>{pluginDir}/Bitmaps/</value>
</parameter>
```

`ImagePath` is used by both OEM plugins (`SecurityMenu.manifest:19-22`, `ActiveSeating.manifest:19-22`) yet the string `ImagePath` does **not** appear in `HmiMain3D` (grep: 0 hits) — confirming these are pass-through settings the plugin reads itself, not loader keys. Add your own `<parameter>` blocks the same way.

---

## 4. Side-by-side: example vs the two OEM manifests

| Field | **Diagnostics** (SDK example) | **SecurityMenu** (OEM) | **ActiveSeating** (OEM) |
|-------|------------------------------|------------------------|--------------------------|
| Directory | `Plugins/Diagnostics/` (uncoded) | `PluginsCoded/SecurityMenu/` | `PluginsCoded/ActiveSeating/` |
| `<name>` | `Diagnostics` | `SecurityMenu` | `ActiveSeating` |
| `<type>` | `App` | `App` | `App` |
| `<file>` | `{pluginDir}/Diagnostics` | `{pluginDir}/SecurityMenu` | `{pluginDir}/ActiveSeating` |
| `<autoStart>` | `yes` | `yes` | `yes` |
| connector `<type>` | `Etch` | `Etch` | `Etch` |
| connector `<id>` | `100` | `200` | `17` |
| `<asyncCallbacks>` | `yes` | `yes` | `yes` |
| `<DescFile>` | `{pluginDir}/Diagnostics.xml` | `{pluginDir}/SecurityMenu.xml` | `{pluginDir}/ActiveSeating.xml` |
| `<TextDBFile>` | — | `{pluginDir}/SecurityMenu_ALL_Texts.zip` | `{pluginDir}/ActiveSeating_ALL_Texts.zip` |
| `<ImageDBFile>` | — | `{pluginDir}/SecurityMenu_ALL_Images.zip` | `{pluginDir}/ActiveSeating_ALL_Images.zip` |
| custom `<parameter>` | — | `ImagePath` = `{pluginDir}/Bitmaps/` | `ImagePath` = `{pluginDir}/Bitmaps/` |
| XML encoding | `utf-8` | `utf-8` | `utf-8` |

**What the differences tell you:** the *only* mandatory delta between a trivial plugin and a full OEM one is the resource bundles. A plugin with no localized text and no bundled images (it can draw text/images inline in its DescFile) needs only `<DescFile>`, exactly as the example shows. Text/image DBs and custom parameters are additive. Connector `<id>` differs per app but is otherwise interchangeable in form.

---

## 5. The `{pluginDir}` token and path resolution

`{pluginDir}` (the `PLUGIN_DIR_WILDCARD` static) is replaced at load time by the absolute path of the plugin's own directory — the subdirectory the `.manifest` was found in, joined to the file basenames via the `PATH_DELIMITER` static. So for a plugin discovered at `…/data/ro/Plugins/Diagnostics/`:

| In the manifest | Resolves to |
|-----------------|-------------|
| `{pluginDir}/Diagnostics` | `…/Plugins/Diagnostics/` + `lib`+`Diagnostics`+`.so` → `libDiagnostics.so` |
| `{pluginDir}/Diagnostics.xml` | `…/Plugins/Diagnostics/Diagnostics.xml` |
| `{pluginDir}/Bitmaps/` (ImagePath) | `…/Plugins/Diagnostics/Bitmaps/` |

Substitution is observed in `<file>`, in the file-DB keys (`<DescFile>` etc.), and in a custom `<parameter>` value (`ImagePath`) — i.e. it applies to path-bearing values wherever the token appears, not only to loader keys. **Always** use `{pluginDir}`-relative paths: it makes the plugin directory relocatable and is how every OEM manifest is written. Absolute paths are untested and would break if the plugin is moved between `Plugins/` and `PluginsCoded/`.

---

## 6. What the loader requires vs. ignores

Reconstructed from the `ManagedPluginApp` validation sequence in `HmiMain3D` (error strings quoted verbatim — each present once in the binary — in load order):

| Check | On failure | Class |
|-------|-----------|-------|
| Manifest XML parses | `Error: Loading manifest XML failed (` | **Required** |
| Root is `<plugin>` | `Error: Manifest does not contain a <plugin> tag` | **Required** |
| Has `<name>` | `Error: Plugin has no name` | **Required** |
| Passes coding allow check *(PluginsCoded only)* | `Error: Plugin is not allowed` | **Required** (coded dir) |
| `<type>` present | `Warning: Plugin type is ` (logged) | **Advisory** — value ignored |
| Has a `DescFile` parameter | `Error: Plugin does not refer to a UI description file` | **Required** |
| Dynamic plugin has code object | `Error: Plugin has no code behind dynamic link library` | **Required** (dynamic) |
| Manifest data structurally sane | `Error: Manifest XML data is corrupt` | **Required** |
| Valid `<pluginAppConnector>` | `Error: Plugin has no valid PluginAppConnector` | **Required** |
| `.so` loads | `Error: Unable to load dynamic link library: ` | **Required** (dynamic) |
| Exports `pluginAppInfo` | `Error: Plugin does not contain a pluginAppInfo entry point` | **Required** (dynamic) |
| Descriptor valid | `Error: The plugin's pluginAppInfo entry point is invalid` | **Required** (dynamic) |
| `create()` succeeds | `Error: Unable to create instance of: ` | **Required** (dynamic) |
| Not already loaded | `Error: Plugin already running` | Guard |

**Ignored by value (safe to keep for convention):** the `<type>` value (`App`) and the connector `<type>` value (`Etch`). There is no standalone `App` string for the loader to match `<type>` against (only unrelated substrings like `App '%s' not found!`), and `Etch` has zero occurrences of any kind — so both are logged/carried but never matched. **Ignored entirely:** unknown `<parameter>` names (stored and passed through to the plugin, never interpreted by the loader).

---

## 7. A minimal manifest template

Copy this, rename `MyApp` throughout, and drop it in `Plugins/MyApp/` alongside `libMyApp.so` and `MyApp.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<plugin>
    <name>MyApp</name>
    <type>App</type>
    <file>{pluginDir}/MyApp</file>
    <config>
        <autoStart>yes</autoStart>
        <dependencies>
            <pluginAppConnector>
                <type>Etch</type>
                <id>101</id>
                <asyncCallbacks>yes</asyncCallbacks>
            </pluginAppConnector>
        </dependencies>
        <parameters>
            <DescFile>{pluginDir}/MyApp.xml</DescFile>
            <!-- optional resource bundles:
            <TextDBFile>{pluginDir}/MyApp_ALL_Texts.zip</TextDBFile>
            <ImageDBFile>{pluginDir}/MyApp_ALL_Images.zip</ImageDBFile>
            <parameter><name>ImagePath</name><value>{pluginDir}/Bitmaps/</value></parameter>
            -->
        </parameters>
    </config>
</plugin>
```

Pick a connector `<id>` not already used by an OEM plugin (avoid `17`, `200`, and any other in-use value). See `03-descfile-xml-reference.md` for authoring `MyApp.xml` and `05-cxx-abi-and-data-types.md` for building `libMyApp.so`.

---

## 8. Verified vs. reconstructed — summary

- **Carve-confirmed (byte-exact):** the three `.manifest` files and every element/value in Sections 2–4; the loader token strings and full error-message sequence in `HmiMain3D` (`ManagedPluginApp.cpp`); the discovery directories `Plugins`/`PluginsCoded`; the scan log fragments `Searching in Plugin directory: ` / `Searching in subDir of Plugin directory: `; the `PATH_DELIMITER` static; the `.manifest` extension; the `dlsym` symbol name `pluginAppInfo`; the five recognized file-DB keys (incl. `WidgetDBFile`/`AssetDBFile`, present in the loader but unused by the samples); the absence of any standalone `App` string, of `Etch`, and of `ImagePath` as loader literals; the byte-identical SDK copy of the example manifest (`diff` clean).
- **Verified end-to-end on the author's OPT_DEBUG-enabled unit:** discovery + load of an uncoded plugin from `Plugins/` with no signing/coding. The marker-file proof (`/tmp/diag_plugin_loaded` from the `.so` constructor on `dlopen`, `/tmp/diag_plugin_created` from `create()`) and the deploy/validate steps in the reference plugin (`diagnostics.cpp`, `DEPLOY.md`) fire on the author's own unit: the plugin is discovered, `dlopen`'d, and its menu entry renders. **Scoped to the author's OPT_DEBUG-enabled unit** — this is not a claim about a stock unit; a stock unit enforces **no signature** on load (the loader links no cryptography; confirmed on-car by the owner's unsigned plugin loading from `Plugins/`) — see `14-signing-and-coding.md`. `PluginsCoded/` adds a coding-value check (`isVariantSet 0x0C0E/0x9C55`), not a signature.
- **Reconstructed / inferred (labeled inline):** the exact `<file>` semantics of `{xmlOnly}` and `{staticLibrary}`; the precise scope of `{pluginDir}` substitution; the default of `<autoStart>` when omitted; whether connector `<id>` must be globally unique; the format/consumption of `WidgetDBFile`/`AssetDBFile`; the precise coding-gate semantics behind `Plugin is not allowed`.

---

## Sources

These facts come from an **owner-authorized offline flash carve** of the author's own titled vehicle plus on-car procedure work; no third-party systems are involved and no car-specific network addresses, VIN, or private diagnostic-app internals are part of the SDK. Primary sources opened for this document:

- `capabilities/plugins/reference/example-plugin/Diagnostics.manifest` — reference plugin manifest.
- `opt/hmi/ID5/data/ro/PluginsCoded/SecurityMenu/SecurityMenu.manifest` and `…/ActiveSeating/ActiveSeating.manifest` — the two OEM manifests.
- `opt/hmi/ID5/bin/HmiMain3D` — the ARM ELF containing `ManagedPluginApp`; all token literals, error strings, statics, and negative (0-hit) claims were confirmed with `strings`/`grep` against this binary.
- `opt/hmi/ID5/lib/libhmiplugin.so` — the in-process device-abstraction layer (the author's notes nickname it "Populus"; not a framework name found in the unit); confirmed to contain **none** of the RA-plugin loader tokens.
- `opt/hmi/ID5/data/ro/hmiplugins/A4APlugin.xml`, `RemotingPlugin.xml` — the distinct `<Bundle>`/`<Plugin>` schema (not this loader).
- `capabilities/plugins/reference/example-plugin/hello_plugin_stage1.cpp`, `DEPLOY.md` — the stage-1 marker-file design and deploy/validate procedure.

**Reconstructed-ABI note:** the C++/ABI-level headers referenced from this document (`bmw_abi.h`, `bmw_list.h`, the `PluginAppInfo` descriptor, the `PluginApp` vtable) are **hand-reconstructed** from library symbols, not an OEM header, and are marked as such wherever cited. The `.manifest` XML files themselves are exact bytes carved from the flash and are authoritative.
