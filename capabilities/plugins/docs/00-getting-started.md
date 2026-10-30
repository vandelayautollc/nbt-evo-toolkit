# 00 — Getting Started

> One page to orient you: what to install, which docs to read in what order, and a glossary of
> the terms the rest of the SDK uses without stopping to define them.

> **Scope & authorization.** This SDK documents the NBT-Evo / ID5 HMI **RA plugin** mechanism,
> reverse-engineered from an offline flash carve and owner-authorized work on the author's own
> titled vehicle. It is written for a developer building a menu app for a head unit **they own**.
> The plugin mechanics are generic — no VIN, private network address, or car-specific diagnostic
> detail is part of the SDK.

If you have not yet, read the top-level [`../README.md`](../README.md) first — it gives the
one-paragraph picture and the "how it works in 6 bullets." This page assumes you are past that
and ready to actually build something.

---

## 1. What you are building

An **RA plugin** is a directory of three loose files — a `.manifest`, a `.xml` DescFile, and a
`lib<Name>.so` — that the HMI process (`HmiMain3D`) discovers, `dlopen()`s, and runs as a menu
app. Your compiled code never draws anything: it fills **data models**, flips component
**properties**, and receives **action callbacks**; the HMI renders the UI declared in your
DescFile. Everything runs on one thread (the HMI UI/dispatcher thread), and the plugin is fully
reversible — nothing in the HMI binary is touched.

This is a different thing from the head unit's other two extension points (an in-process
device-abstraction layer, and the infrastructure "bundle" plugins under `hmiplugins/`). Those
are **not** menu apps and are out of scope; [`01-architecture-and-loading.md`](01-architecture-and-loading.md)
draws the full distinction so you don't model your plugin on the wrong one.

---

## 2. Prerequisites

Before Stage 0 of the tutorial you need four things. The details are in
[`08-building-and-deploying.md`](08-building-and-deploying.md); the short list:

1. **A matching cross-toolchain.** The HMI is QNX 6.5.0 / ARM (EABI5) and the OEM framework was
   built with **gcc 4.4.2**. Use **QNX SDP 6.5.0**, whose ARM C++ driver is `ntoarm-g++`
   (gcc 4.4.2). A modern g++ will mangle names and lay out classes incompatibly and your plugin
   will not load.
2. **The two framework libraries from your own carve** — `libAppFramework.A.so` and
   `libCoreFramework.A.so` (from `…/opt/hmi/ID5/lib/`). You link against them so your `bmw::`
   references have something to bind to; they are not redistributable, so carve your own.
3. **The two reconstructed SDK headers** — `bmw_abi.h` (minimal; enough for Stage 0) and
   `bmw_list.h` (fuller; needed from Stage 1). Both are in [`../reference/sdk/`](../reference/sdk/).
4. **Shell + writable-filesystem access to a head unit you own.** Dropping files on the unit and
   restarting the HMI requires a root shell and a data partition you can remount read-write. How
   you obtain that is a **precondition of this SDK, not part of it** — the docs assume you already
   have it.

---

## 3. The reading order

You do not need all nine references at once. Read in this sequence, pulling in the deep dives
only when a stage forces you to:

1. **Orientation — you are here.** Then skim
   [`01-architecture-and-loading.md`](01-architecture-and-loading.md) for the load pipeline and the
   three-file anatomy. That is enough context to start.
2. **Build the loader-proof plugin.** Go to the tutorial,
   [`09-tutorial-first-plugin.md`](09-tutorial-first-plugin.md) **Stage 0**. Get a green marker
   file before writing any UI. It uses [`08-building-and-deploying.md`](08-building-and-deploying.md)
   for the build/deploy/rollback loop.
3. **Add a screen.** Tutorial **Stage 1** (a button + a list). When you need the exact XML,
   reach for [`02-manifest-format.md`](02-manifest-format.md) (the `.manifest`),
   [`03-descfile-xml-reference.md`](03-descfile-xml-reference.md) (the DescFile grammar), and
   [`04-menus-screens-and-layout.md`](04-menus-screens-and-layout.md) (where the entry appears and how
   screens lay out).
4. **Do real work safely.** Tutorial **Stage 2** (a background job that never freezes the HMI).
   Pair it with [`06-runtime-api-reference.md`](06-runtime-api-reference.md) (the calls you make and
   the callbacks you receive) and [`07-threading-and-safety-model.md`](07-threading-and-safety-model.md)
   (the single-thread rule, the poller pattern, ownership, and the teardown hazard).
5. **Deep ABI, only when you need it.** [`05-cxx-abi-and-data-types.md`](05-cxx-abi-and-data-types.md)
   is the hardest doc — the `PluginApp` vtable and the `Parcel`/`Variant`/`DataTable` layouts.
   Read it to debug a crash inside `dlopen`, to add a value type the example doesn't use, or to
   understand *why* a layout is what it is. For a first plugin you can treat the headers as an
   opaque dependency and copy the example.

> **A note on the reference set.** These docs were written as parallel dimension studies and
> occasionally cross-reference each other by an earlier working title or number. When a link in
> one doc doesn't resolve to a filename in `docs/`, match it by topic — the mapping is: manifest
> → `02`, DescFile grammar → `03`, menus/layout → `04`, C++ ABI & data types → `05`, runtime API
> → `06`, threading → `07`. There is not (yet) a standalone "data models" doc; model content
> lives in `05` (the data types) and `06` (the runtime calls).

---

## 4. Glossary

The terms the rest of the SDK leans on, shortest-useful-definition first. Where a term is a
literal token in the manifest, DescFile, or binary, that is noted.

| Term | What it means |
|------|---------------|
| **RA plugin** | *Remote Application plugin.* A menu app: a directory of three loose files (`.manifest` + DescFile + `lib<Name>.so`) the HMI discovers, `dlopen()`s, and runs. "Remote" because the framework treats it as a remote application even though it runs in-process. The one thing this SDK documents. |
| **manifest** | `<Name>.manifest` — the loader-config XML the scanner reads **first**. Root `<plugin>`; declares `<name>`, `<type>App</type>`, the `<file>` code backing, `<autoStart>`, the `<pluginAppConnector>` dependency, and (via `<parameters><DescFile>`) where the DescFile is. It names every other artifact. |
| **DescFile** | `<Name>.xml` — the declarative UI description the HMI parses after load. Root `<pluginApps>`; declares the menu entry, screens, components, actions, and models. Your code references everything in it by numeric id. |
| **applicationType** | Attribute on `<pluginApp>` that decides **which host menu** your entry docks into (e.g. `VehicleInformation`, `Settings__SpecialVehicle`, `ServiceMenu`, or `Custom` to anchor manually). Resolved by compiled HMI generation rules, so the usable set is fixed by the firmware build — a wrong value means the entry never appears. |
| **hmiState** | One **screen**, identified by a plugin-local integer `id`. A DescFile declares a tree of them under `<hmiStates>`. Navigation between screens is a plain directed graph whose edges are `hmiAction target=` ids. |
| **hmiAction** | A **navigation** action: `<hmiAction id=… target=…>`. When a component with `action="<id>"` fires, the HMI pushes `target` (another `hmiState`) onto the state stack. Handled **entirely inside the HMI** — your code never sees it. Use it to *go somewhere*. |
| **raAction** | A **callback** action: `<raAction id=…>`. When a component with `action="<id>"` fires, the framework invokes the delegate you bound with `addHandler(id, …)`, passing a `Parcel` of arguments. Use it to *do something*. `hmiAction` navigates; `raAction` calls back. |
| **model** | A named data slot the UI reads its content from, declared in `<models>` and bound by a component via `model="<id>"` (and friends). `ra*` models (`raListModel`, `raDataModel`, …) are **dynamic** — you fill them at runtime with `updateModel(id, data)`; `*IdModel` models are **static** references into resource DBs. |
| **layoutGroup** | `<layoutGroup name="List" width="…"/>` on an `hmiState` — selects the stock list template and sets the width of the list region. A full-width value gives a plain list; a narrower one (OEM uses `700`) reserves the remainder for an absolutely-positioned detail pane (the master-detail idiom). |
| **PluginApp** | `bmw::PluginApp` — the framework base class **your plugin subclasses**. It has a 34-slot primary vtable; you override `onInit()`/`onFinalize()` (and rarely a couple of others) and **call** the non-virtual helpers `updateModel()`, `addHandler()`, `setProperty()`, and `post()`. |
| **pluginAppInfo** | The single exported, un-mangled C symbol the loader `dlsym()`s from your `.so` — a 24-byte descriptor `{abiVersion, name, vendor, ifaceVersion, create, destroy}`. `create()` is the factory that returns your `PluginApp` subclass. No `pluginAppInfo`, no load. |
| **Parcel** | `bmw::Parcel` — the flat serialization buffer scalars cross the ABI in. Your `raAction` handlers receive a `const Parcel&` (read a row index with `readUInt32`, etc.); you build one to carry a value into `setProperty`. Copy is deliberately hidden — pass by `const&`, read scalars out immediately, never store it. |
| **DataTable** | `bmw::DataTable<NCOLS>` — the rows-×-columns container a list model wants. You fill cells with `Variant`s (each holding a `BasicString`, a `TextID`, …) and hand it to `updateModel(model, table)`. `updateModel` **deep-copies** it, so the table is yours to free (a stack `DataTable` frees itself via RAII). |
| **Runnable** | `bmw::Runnable` — a unit of work you `post()` onto the UI thread; override `run()`. The sanctioned concurrency primitive: a **self-rescheduling** `Runnable` `post(this, ms)`s itself to poll a `posix_spawn` child from the UI thread without blocking it. The framework never frees a `Runnable` — a one-shot `delete this` at the end of `run()`; a poller deletes only on its terminal tick. |
| **SELECTABLE** | Component property **id `2`** (a boolean). `true` = enabled and focusable; `false` = greyed and inert. The canonical runtime property toggle: `setProperty(comp, 2, Parcel(false))` greys a button while a job runs, `Parcel(true)` re-enables it. Prefer greying to removing a component — removing risks dangling focus targets. |

Two conventions worth internalizing early, both from the glossary above:

- **Numeric ids are the wiring.** Component ids, action ids, model ids, and state ids all live in
  **one flat namespace per `<pluginApp>`** and must be unique. Your C++ references the UI purely
  by these numbers — `addHandler(21, …)` binds `raAction 21`, `updateModel(50, …)` fills model
  50, `setProperty(4, 2, …)` sets `SELECTABLE` on component 4.
- **One thread, never blocked.** `onInit`, every `raAction` handler, and every `Runnable::run()`
  run on the HMI UI thread. Blocking it freezes the head unit. Real work goes in a child process,
  polled from the UI thread — see `07`.

---

## 5. The five-minute checklist

To get *something* loaded, in order:

1. Write `<Name>.manifest` with a **unique** `<name>`, `<file>{pluginDir}/<Name></file>`, a
   `<DescFile>`, and a `<pluginAppConnector>` (`02`).
2. Write `<Name>.xml` declaring one menu entry and (at least) one `hmiState` (`03`, `04`).
3. Compile `lib<Name>.so` exporting `pluginAppInfo` with a working `create()`/`destroy()` and a
   `.so`-constructor marker so you can prove load (`05`, `08`; the ~50-line
   [`../reference/example-plugin/hello_plugin_stage1.cpp`](../reference/example-plugin/hello_plugin_stage1.cpp)
   does exactly this).
4. `mkdir -p …/data/ro/Plugins/<Name>/`, copy the three files in, `sync`, restart the HMI (`08`).
5. Verify: your marker file appears (load proven) and your menu entry shows up. Then graduate to
   `updateModel`/`setProperty`/`post` and follow the tutorial (`09`).

If a rung fails, the tutorial's troubleshooting table (`09`) and the validation ladder (`08`)
tell you which stage broke and why.
