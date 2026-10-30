# Plugins — the NBT EVO HMI Plugin SDK

**Write your own menu apps for the BMW NBT-Evo / "ID5" head-unit HMI.**

> Part of the [NBT EVO Toolkit](../../README.md). This is a **file install** (loose files in the
> HMI's `Plugins/` directory), not a flash or a coded write — the gentlest, most reversible way to
> extend the car. It needs the QNX/ARM toolchain from [`qnx_dev`](../qnx_dev/) to build the `.so`.
> Owner-authorized, your own car only — see [LEGAL.md](../../LEGAL.md) and [LICENSE](../../LICENSE).

This is an open, community-authored SDK for the NBT-Evo HMI's **RA plugin** ("Remote
Application" plugin) extension point — the mechanism the head unit's HMI process
(`HmiMain3D`) uses to discover a directory of loose files, `dlopen()` a shared object out of
it, and run it as a menu app. If you have ever wanted to add your own screen, list, or tool
to the infotainment menu, this is the seam that lets you do it, and these docs are the map.

> **Scope & authorization (read once).** Everything here was reverse-engineered from an
> **offline flash carve** and **owner-authorized** work on the author's **own titled
> vehicle**, and is written for a developer working on a head unit **they own**. The SDK
> documents the plugin *mechanics* generically — no VIN, private network address, or
> car-specific diagnostic payload is part of it. Plugins are loose files: nothing in the HMI
> binary is modified, and a plugin is removed by deleting its directory and restarting the
> HMI. Build and test only on hardware you own.

---

## What an RA plugin is

A plugin is **three loose files in one directory** that the HMI discovers and runs as a menu
app:

| File | What it is |
|------|------------|
| `<Name>.manifest` | Loader config (XML): the plugin's name, type, `.so` base name, `autoStart`, its connector dependency, and where its DescFile lives. |
| `<Name>.xml` (the **DescFile**) | The declarative UI: the menu entry, the screens (`hmiState`s), the components (`button` / `list` / `label` / `separator` / …), the navigation and callback actions, and the data models the UI binds to. |
| `lib<Name>.so` | Your compiled ARM/QNX code, exporting one C symbol — `pluginAppInfo` — through which the framework constructs and runs your `bmw::PluginApp` subclass. |

Drop those three files into the HMI's uncoded `Plugins/` directory, restart the HMI, and your
menu entry appears — and this ran on a stock unit: the owner's own unsigned plugin loaded from
`Plugins/`. Signing is **not** enforced on plugin load (the loader links no cryptography and has
no signature branch); `OPT_DEBUG` only grants the filesystem write to place the files. The
`PluginsCoded/` root additionally carries a coding-value check (`isVariantSet 0x0C0E/0x9C55`),
not a signature. See [`docs/08-building-and-deploying.md`](docs/08-building-and-deploying.md) and
[`docs/14-signing-and-coding.md`](docs/14-signing-and-coding.md).
Your `.so` never draws pixels: it fills **data models**, flips **properties**, and receives
**action callbacks** — the HMI renders everything.

> This SDK covers **only** the RA plugin (menu-app) mechanism. The head unit hosts two other,
> unrelated extension points — an in-process device-abstraction layer and a set of
> infrastructure "bundle" plugins under `hmiplugins/`. Neither is an RA menu app, and neither
> is covered here. See [`docs/01-architecture-and-loading.md`](docs/01-architecture-and-loading.md)
> for the full three-way distinction.

---

## How it works in 6 bullets

1. **Discovery.** At HMI start, `HmiMain3D` scans well-known plugin directories
   (`data/ro/Plugins/`, `data/ro/PluginsCoded/`), finds each `<Name>.manifest`, and reads it
   first — the manifest names every other artifact.
2. **Load.** For a code-backed plugin the loader `dlopen()`s `lib<Name>.so` and `dlsym()`s a
   single exported C symbol, `pluginAppInfo` — a 24-byte descriptor `{abiVersion, name, vendor,
   ifaceVersion, create, destroy}`.
3. **Construct.** The framework calls your `create()`, which returns a `bmw::PluginApp`
   subclass. The base constructor installs the real vtable and wires the connector to the HMI.
4. **Init.** The framework calls your `onInit()` (vtable slot 22). There you seed your data
   models with `updateModel(...)` and bind each `raAction` to one of your methods with
   `addHandler(...)`.
5. **Integrate & run.** The HMI parses your DescFile, builds the declared menu entry and
   screens, and shows them. `hmiAction`s navigate between your screens entirely inside the HMI;
   `raAction`s call back into your code with a `Parcel` of arguments.
6. **One thread, never blocked.** Everything the framework calls on you runs on the single HMI
   UI/dispatcher thread. Long work goes in a `posix_spawn` child process, polled from the UI
   thread by a self-rescheduling `bmw::Runnable` you `post(this, ms)`; all model/property
   updates happen on the UI thread.

---

## Quick start

New here? Read **[`docs/00-getting-started.md`](docs/00-getting-started.md)** first — it
sequences the whole doc set and defines the vocabulary. Then go straight to the hands-on
build in **[`docs/09-tutorial-first-plugin.md`](docs/09-tutorial-first-plugin.md)**, which
walks you from a "does it even load?" marker plugin (Stage 0) up to a screen with a button and
a list (Stage 1) and finally a safe background job (Stage 2). The tutorial's Stage 0 is a
50-line `.so` whose entire job is to prove discovery + `dlopen` + `create()` with zero UI risk;
get that green before you write any UI code.

---

## What's in the box

The `docs/` folder is nine dimension references plus this orientation, in reading order:

| Doc | Covers |
|-----|--------|
| [`docs/00-getting-started.md`](docs/00-getting-started.md) | Orientation + glossary: how to read the SDK, prerequisites, and the core terms in one page. Start here. |
| [`docs/01-architecture-and-loading.md`](docs/01-architecture-and-loading.md) | The big picture: what `HmiMain3D` is, the three-file anatomy, the plugin search directories, the `pluginAppInfo` descriptor, and the full discovery → `dlopen` → `create` → `onInit` load lifecycle. |
| [`docs/02-manifest-format.md`](docs/02-manifest-format.md) | Complete `.manifest` reference: every element, the `{pluginDir}` / `{xmlOnly}` / `{staticLibrary}` file tokens, the connector block, the recognized resource-DB keys, and exactly what the loader requires vs. ignores. |
| [`docs/03-descfile-xml-reference.md`](docs/03-descfile-xml-reference.md) | The DescFile (`.xml`) grammar: every element, attribute, and enumeration — the id namespace, `hmiAction`/`raAction`, models, components, properties, layout groups, option components, and events. |
| [`docs/04-menus-screens-and-layout.md`](docs/04-menus-screens-and-layout.md) | The UX view of the DescFile: how `applicationType` places your entry, how screens and the navigation graph connect, the layout system (list templates, absolute positioning), and the master-detail recipe. |
| [`docs/05-cxx-abi-and-data-types.md`](docs/05-cxx-abi-and-data-types.md) | The compiled C++ ABI: the `pluginAppInfo` descriptor, `bmw::PluginApp` and its 34-slot vtable, and the value types (`BasicString`, `Parcel`, `Variant`, `Map`, `DataTable`, `Delegate`, `Runnable`, `TextID`) with layouts and mangled names. The hardest doc; skip it until you need it. |
| [`docs/06-runtime-api-reference.md`](docs/06-runtime-api-reference.md) | The available function calls: the callbacks the framework invokes on you (you override only `onInit`/`onFinalize`) and the helpers you call back — `updateModel`, `addHandler`, `setProperty`, `post` — wired to DescFile ids. |
| [`docs/07-threading-and-safety-model.md`](docs/07-threading-and-safety-model.md) | How not to crash the HMI: the single-thread rule, the child-process + self-rescheduling-poller pattern, memory/ownership rules, the teardown hazard, and a copyable best-practices checklist. |
| [`docs/08-building-and-deploying.md`](docs/08-building-and-deploying.md) | Toolchain and deployment: the QNX SDP 6.5.0 / `ntoarm-g++` (gcc 4.4.2) cross-build, the Makefile flag-by-flag, object self-checks, the deploy layout, the marker-based validation ladder, and one-line rollback. |
| [`docs/09-tutorial-first-plugin.md`](docs/09-tutorial-first-plugin.md) | The hands-on tutorial: three plugins of increasing capability (loader proof → screen + button + list → safe background job), each with full code and a troubleshooting table. |

**Suggested paths:**
- *Just want a menu entry to appear?* 00 → 09 (Stages 0–1), dipping into 02 and 04 as needed.
- *Building something real?* Add 06 (the API you call) and 07 (how not to freeze the HMI).
- *Debugging a load failure or a crash inside `dlopen`?* 05 (the ABI) and 08 (the object
  self-checks and validation ladder).

---

## `reference/` — headers and a working example

The `reference/` folder ships the artifacts the docs are grounded in, ready to copy into your
own plugin project:

### `reference/sdk/` — the two reconstructed SDK headers

- **`bmw_abi.h`** — the minimal header: just enough to construct a `bmw::PluginApp` and export
  a `pluginAppInfo`. Everything a Stage-0 loader-proof plugin needs.
- **`bmw_list.h`** — the fuller, authoritative header: adds `Runnable`, `Parcel`,
  `Variant`/`ObjectContainer`, `DataTable<N>`, `Delegate`, and the full 34-slot `PluginApp`.
  Use this from Stage 1 on.

> **These headers are hand-reconstructed, not an OEM SDK.** They contain almost no method
> bodies — the real code lives in `libAppFramework.A.so` / `libCoreFramework.A.so` on the head
> unit and is resolved at `dlopen(RTLD_NOW)`. The headers re-declare only the data layouts,
> mangled-name-compatible signatures, and vtable order the ABI needs. Every offset and
> signature was checked against real exported symbols, but treat struct sizes and internal
> field names as *correct-enough-to-build-and-run*, and re-verify against your **own** carve if
> your firmware differs. Details and the verification recipes are in `docs/05`.

### `reference/example-plugin/` — a minimal, buildable example

- **`Diagnostics.manifest`** — a complete, minimal manifest (the whole schema you need for an
  uncoded, code-backed plugin).
- **`Diagnostics.xml`** — the matching DescFile: a menu entry, screens, a button, a list, a
  master-detail pane, and an OPTION menu.
- **`Makefile`** — the QNX/ARM cross-build (point `CARVE` at your own carved framework libs;
  `source` your QNX SDP `env.sh` first).
- **`hello_plugin_stage1.cpp`** — the ~50-line loader-proof plugin: it writes filesystem
  markers on `dlopen` and on `create()`, then hands the framework a default `bmw::PluginApp`.
  This is the first thing to build and deploy.

The framework libraries (`libAppFramework.A.so`, `libCoreFramework.A.so`) are **not**
redistributable and are **not** included — each developer carves their own copy from their own
unit's flash and links against it. See `docs/08` for how.

---

## Verified vs. reconstructed

The docs tag claims so you know how far to trust them, and you should keep the distinction:

- **Carve-confirmed** facts are bytes on disk — loader strings and symbols in `HmiMain3D`, the
  OEM `.manifest` / DescFile files, and exported framework symbols read with `nm -DC`. The
  directory layout, the manifest and DescFile *grammar*, the `pluginAppInfo` requirement, and
  the framework symbol names/signatures/offsets are all in this class.
- **Reconstructed-ABI** facts are the hand-built headers (`bmw_abi.h`, `bmw_list.h`) — struct
  sizes, some byte offsets, and internal field names deduced from stripped binaries. They build
  and run, but they are not lifted from BMW source.

Everything here is from **one firmware build** (an ID5 NBT-Evo). Other builds and generations
(the binary even carries `start_ID4_HMI.cfg` / `start_ID5_HMI.cfg` roots) may differ — the
method is meant to be re-run against your own carve, not trusted blind.

---

## Contributing & scope

This SDK aims to be a shared, hobbyist-friendly reference so other developers can write their
own NBT-Evo menu apps. Contributions that make it **more precise** are the most valuable:

- **Confirm or correct a reconstructed detail** against a different carve — a struct size, a
  vtable slot, an offset, a property id, an `applicationType` value. Say which firmware build
  you checked.
- **Fill a documented gap.** Several docs point at content that is not yet written (a dedicated
  data-models reference, resource-bundle authoring, a firmware-compatibility matrix, a
  consolidated error-string catalog). Those are open for contribution.
- **Keep it generic.** Do not add a specific vehicle's VIN, network addresses, or private
  diagnostic-tool internals — those belong in *your own* plugin, not in the SDK. Present the
  plugin mechanics generically, and mark every non-obvious claim with a primary source and a
  verified-vs-reconstructed tag, the way the existing docs do.

**Out of scope**, by design: the in-process device-abstraction layer and the `hmiplugins/`
bundle plugins (not menu apps); how to obtain shell/root access to a head unit (a precondition,
not part of this SDK); anything requiring access to a network or a vehicle you do not own.
