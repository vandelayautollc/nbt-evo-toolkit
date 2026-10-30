# Tutorial: Your First Plugin

> **Scope & authorization.** This tutorial documents the NBT-Evo HMI "RA plugin" extension mechanism, reverse-engineered from an offline flash carve and validated end-to-end on the author's own titled vehicle (an OPT_DEBUG-enabled head unit). It is written for a developer working on **their own** head unit. The example payloads here are deliberately generic; nothing in this document requires or discloses any specific vehicle's network, VIN, or diagnostic tooling.

This is the hands-on path through the SDK. You will build three plugins of increasing capability, each one flashing out a single idea:

| Stage | You build | New concept |
|-------|-----------|-------------|
| **0 — Hello, loader** | A `.so` that does nothing but get discovered, `dlopen`'d and constructed | Discovery, the `pluginAppInfo` entry point, deploy & validate loop |
| **1 — A screen with a button + a list** | A menu app with one screen, one button, one populated list | `bmw::PluginApp` subclass, `onInit()`, `addHandler()`, `updateModel()` with a `DataTable` |
| **2 — Do real work safely** | The same app, now running a background job without ever freezing the HMI | `posix_spawn` child + a self-rescheduling `bmw::Runnable` poller + `setProperty()` greying |

> **Stage names vs. the reference source files.** This tutorial's stage numbers are pedagogical and do **not** match the `Stage-N` labels in the in-repo reference `.cpp` files (those count from 1). If you cross-reference the shipped source: tutorial **Stage 0** ≈ `hello_plugin_stage1.cpp` (the minimal loader proof), and the later tutorial stages build up to the full `diagnostics.cpp` reference plugin — both in [`../reference/example-plugin/`](../reference/example-plugin/). The reference plugin was reached through a longer internal progression; only the start (`hello_plugin_stage1.cpp`) and end (`diagnostics.cpp`) ship.

Each stage lists its **goal**, the **files that change**, the **code**, and the **build → deploy → observe** steps. At the end there is a "where to go next" map into the reference docs and a troubleshooting table.

> **Not covered here.** The `.xml` "Bundle" plugins under `hmiplugins/` (e.g. `A4APlugin.xml`, `RemotingPlugin.xml` → `libhmiremoting.so`, whose root element is `<Bundle exportedSymbolName="…">`) are RHMI/remoting infrastructure — a completely different mechanism, and also distinct from the in-process device-abstraction layer (`libhmiplugin.so` and its `THmiPluginProxy`/`CPxy*` classes; "Populus" is the author's informal nickname for that layer, not a firmware name). RA plugins are the loose-file menu apps under `Plugins*/`. See the [architecture-and-loading doc](01-architecture-and-loading.md) for the distinction.

---

## 0. Prerequisites

You need three things before Stage 0.

**A cross-toolchain matching the OEM ABI.** The plugins are QNX 6.5 / ARM (EABI5) shared objects. The OEM framework was built with **gcc 4.4.2**; use the matching QNX cross-compiler (`ntoarm-g++`) so the C++ ABI (name mangling, class layout, vtable emission) lines up. The reference `Makefile` assumes you have run `source .../qnx650/env.sh` first (per its header comment on line 2 — it is guidance to the developer, not something `make` invokes for you).

```makefile
# Makefile — cross-build one plugin .so for NBT-Evo (QNX/ARM). gcc 4.4.2 == OEM toolchain.
# source .../qnx650/env.sh first (sets up ntoarm-g++ on PATH).
CXX      := ntoarm-g++
LIBDIR   := /path/to/carve/opt/hmi/ID5/lib
LIBS     := $(LIBDIR)/libAppFramework.A.so $(LIBDIR)/libCoreFramework.A.so
CXXFLAGS := -shared -fPIC -O2 -fno-strict-aliasing -Wall -fno-exceptions
LDFLAGS  := -Wl,--allow-shlib-undefined -Wl,-soname,libMyPlugin.so

libMyPlugin.so: myplugin.cpp bmw_list.h
	$(CXX) $(CXXFLAGS) myplugin.cpp $(LIBS) $(LDFLAGS) -o $@
```

Two flags matter. `-fno-exceptions` keeps the object lean and avoids pulling EH machinery the HMI process does not expect from a plugin. `-Wl,--allow-shlib-undefined` lets you link against `libAppFramework.A.so` / `libCoreFramework.A.so` for their symbols while leaving the plugin's own undefined `bmw::*` references to be resolved at `dlopen` time inside `HmiMain3D`.

**The framework libraries to link against.** You link the two framework `.so`s from a carve of *your* head unit's HMI partition: `libAppFramework.A.so` (the `bmw::PluginApp` class, `updateModel`, `addHandler`, `setProperty`, `post`) and `libCoreFramework.A.so` (`BasicString`, `DataTableBase`, `Parcel`, `Variant`). A built plugin's `NEEDED` list confirms the runtime dependency set: `libAppFramework.A.so`, `libCoreFramework.A.so`, `libstdc++.so.6`, `libm.so.2`, `libc.so.3` — all already present on the HU.

**The two reconstructed SDK headers.** `bmw_abi.h` is the minimal one (enough to construct a `bmw::PluginApp` and export the descriptor — all you need for Stage 0). `bmw_list.h` is the fuller one (adds `Runnable`, `Parcel`, `Variant`/`ObjectContainer`, `DataTable<N>`, `Delegate`, and the full 34-slot `PluginApp` — needed from Stage 1 on).

> **⚠ These headers are hand-reconstructed**, not an OEM SDK. Class *bodies* live in the framework `.so`s and are resolved at `dlopen`; the headers only re-declare the data layouts and the method signatures/vtable order the ABI needs. Every offset comment in them (e.g. `updateModel(…DataTableBase…) 0x539c`, `addHandler(uint,Delegate) 0x5970`, `addHandler(uint,uint,Delegate) 0x5db0`, `setProperty 0x54a4`, `PluginApp::PluginApp 0x6f80`, `post(Runnable*,uint) 0x6010`) was checked against the real exported symbols and matches — but treat the headers as *reconstructed ABI* and re-verify against your own carve if your firmware differs. See the [C++ ABI reference](05-cxx-abi-and-data-types.md).

---

## Stage 0 — "Hello, loader"

**Goal:** prove that an **unsigned, un-coded** plugin dropped into the HMI's plugin directory is discovered, memory-mapped, and handed to the framework — with zero risk to the running HMI. You write no UI logic yet; you only want to see the loader accept your artifacts. (Verified end-to-end on the author's OPT_DEBUG-enabled unit; a **stock** unit enforces no signature on load (loader links no crypto; confirmed on-car) — OPT_DEBUG only grants the filesystem write.)

### The three artifacts

Every RA plugin is a directory of three loose files named after the plugin:

1. `<Name>.manifest` — loader config (XML).
2. `<Name>.xml` — the *DescFile*: declares the menu entry and (later) screens.
3. `lib<Name>.so` — the compiled plugin, exporting one C symbol: `pluginAppInfo`.

#### `MyPlugin.manifest`

```xml
<?xml version="1.0" encoding="utf-8"?>
<plugin>
	<name>MyPlugin</name>
	<type>App</type>
	<file>{pluginDir}/MyPlugin</file>            <!-- loader appends "lib"+".so" -> libMyPlugin.so -->
	<config>
		<autoStart>yes</autoStart>
		<dependencies>
			<pluginAppConnector>
				<type>Etch</type>
				<id>100</id>                       <!-- pick an id no other plugin uses -->
				<asyncCallbacks>yes</asyncCallbacks>
			</pluginAppConnector>
		</dependencies>
		<parameters>
			<DescFile>{pluginDir}/MyPlugin.xml</DescFile>
		</parameters>
	</config>
</plugin>
```

`{pluginDir}` is expanded by the loader to your plugin's own directory. `<autoStart>yes</autoStart>` makes the framework construct the app at HMI start. The `pluginAppConnector` `id` is a per-plugin connector number — give yours a value no shipping plugin uses (the OEM `SecurityMenu` uses `200`, `ActiveSeating` uses `17`, and the reference PowerTools plugin uses `100`). The manifest structure mirrors the OEM `SecurityMenu.manifest`, minus the optional `TextDBFile`/`ImageDBFile`/`ImagePath` parameters you do not need yet. Full field reference: [02-manifest-format.md](02-manifest-format.md).

#### `MyPlugin.xml` (the DescFile)

The minimal DescFile adds a single menu entry:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<pluginApps>
  <pluginApp applicationType="VehicleInformation" applicationWeight="200" text="MyPlugin">
    <comment/>
    <entryButton action="10" id="1">
      <properties>
        <property id="23" value="2"/>            <!-- carried by every OEM/reference entry button -->
      </properties>
    </entryButton>
    <actions>
      <hmiAction id="10" target="100"/>          <!-- entry button -> screen 100 (defined in Stage 1) -->
    </actions>
    <hmiStates/>
  </pluginApp>
</pluginApps>
```

> **⚠ In Stage 0 the entry is a non-functional placeholder.** Its `hmiAction` targets `hmiState 100`, which does not exist until Stage 1. The entry will appear in the menu and the markers below will confirm the load, but **pressing it navigates to an undefined state and may misbehave** — that is expected at this stage. Every OEM and reference DescFile defines a real `hmiState` for every `hmiAction` target; you will add screen `100` in Stage 1. (If you prefer a clean Stage 0, you can drop the `<entryButton>`/`<hmiAction>` entirely and rely solely on the filesystem markers to prove the load.)

`applicationType` selects which OEM menu your entry appears under (`VehicleInformation` = the vehicle/My-Vehicle menu; the OEM `SecurityMenu` uses `Settings__SpecialVehicle`). `applicationWeight` orders it among siblings. The `entryButton` carries `<property id="23" value="2"/>` in the reference PowerTools DescFile and in the OEM plugins; its exact semantics are documented in the [property-id catalog](04-menus-screens-and-layout.md) — copy it as shown. Full `applicationType` enumeration and the menu-layout rules: [04-menus-screens-and-layout.md](04-menus-screens-and-layout.md), with the DescFile grammar in [03-descfile-xml-reference.md](03-descfile-xml-reference.md).

#### `myplugin.cpp` (Stage 0 source)

This is the whole plugin. It writes filesystem "markers" you can read over ssh, then hands the framework a *default* `bmw::PluginApp` whose real ctor installs the real vtable — so any virtual call the framework makes dispatches safely into `libAppFramework` with default (empty) behavior.

```cpp
// myplugin.cpp — Stage-0 loader-validation plugin.
// Proves an unsigned, un-coded plugin is discovered, dlopen'd and constructed.
#include "bmw_abi.h"
#include <cstdio>
#include <unistd.h>
#include <ctime>

static void marker(const char* path, const char* what) {
    FILE* f = fopen(path, "w");
    if (f) { fprintf(f, "%s pid=%d time=%ld\n", what, (int)getpid(), (long)time(0)); fclose(f); }
}

// Fires the instant HmiMain3D dlopen()s this .so — definitive load proof,
// independent of any bmw:: ABI correctness.
__attribute__((constructor))
static void on_load() { marker("/tmp/myplugin_loaded", "libMyPlugin.so dlopened"); }

// The framework calls this to instantiate the app. Returning a real bmw::PluginApp
// (its ctor installs the real vtable) means later virtual calls dispatch correctly.
static bmw::IPluginApp* my_create(bmw::IDispatcher& disp, const char* name,
                                  const bmw::Bundle& cfg, const bmw::Bundle& res) {
    marker("/tmp/myplugin_created", "MyPlugin::create called");
    bmw::RHMIInterfaceVersion rhmi; rhmi.value = 1;          // == pluginAppInfo.ifaceVersion
    bmw::PluginApp* p =
        new bmw::PluginApp(disp, bmw::BasicString<char>(name),
                           1u /*major*/, 0u /*minor*/, rhmi, cfg, res);
    return reinterpret_cast<bmw::IPluginApp*>(p);            // IPluginApp = primary base @ offset 0
}

static void my_destroy(bmw::IPluginApp* app) {
    marker("/tmp/myplugin_destroyed", "MyPlugin::destroy called");
    (void)app;   // stage-0: intentionally leak; proper delete comes in Stage 1
}

// The exported, un-mangled symbol the loader dlsym()s. Name MUST be "pluginAppInfo".
extern "C" PluginAppInfo pluginAppInfo = {
    1,             // abiVersion   (ctor reads low16=major=1, high16=minor=0)
    "MyPlugin",    // name
    "yourname",    // vendor
    1,             // ifaceVersion (ctor reads this as RHMIInterfaceVersion)
    my_create,
    my_destroy,
};
```

Three things make this work and are worth understanding now:

- **`pluginAppInfo` is the entire contract with the loader.** `HmiMain3D` `dlsym`s exactly that name. If it is missing you get `Error: Plugin does not contain a pluginAppInfo entry point`; if its fields are unusable, `Error: The plugin's pluginAppInfo entry point is invalid` (both strings are present verbatim in the `HmiMain3D` binary). The 24-byte layout `{abiVersion, name, vendor, ifaceVersion, create, destroy}` is fixed by the OEM `SecurityMenu`/`ActiveSeating` descriptors.
- **The `__attribute__((constructor))` marker fires on `dlopen`, before `create()`.** It is your ground-truth "the file was found and mapped" signal, independent of whether your descriptor or ABI is correct. Keep one in every plugin during bring-up.
- **`create()` returns the *primary base* pointer.** `bmw::IPluginApp` is `PluginApp`'s primary base at offset 0, so the `reinterpret_cast` is a no-op that just satisfies the type. (From Stage 1 you return your own subclass instead.)

### Build → deploy → validate

**Build.** Point the `Makefile` at `myplugin.cpp` (Stage 0 only needs `bmw_abi.h`, but linking the same way is fine) and run `make`. Confirm the descriptor and dependencies before you go near the car:

```sh
# pluginAppInfo must be an exported DATA symbol (type 'D'); NEEDED must list the two framework libs.
nm -D libMyPlugin.so | grep pluginAppInfo          # -> "........ D pluginAppInfo"
readelf -d libMyPlugin.so | grep -E 'NEEDED|SONAME'
```

**Deploy.** RA plugins live in `…/data/ro/Plugins/<Name>/`, a sibling of the OEM `PluginsCoded/`. The `Plugins/` directory (no "Coded") holds plugins that require **no** coding — which is why an unsigned, un-coded plugin loads on the author's OPT_DEBUG-enabled unit. (The `HmiMain3D` binary references both `/Plugins/` and `/PluginsCoded` as loader-scanned paths — a carve fact; whether a **stock** unit without OPT_DEBUG still loads an unsigned, un-coded plugin from `Plugins/` is an open question.) Create it if it does not exist and copy the three files in:

```sh
mount -uw /fs/sda0
mkdir -p /fs/sda0/opt/hmi/ID5/data/ro/Plugins/MyPlugin
# copy libMyPlugin.so, MyPlugin.manifest, MyPlugin.xml into that directory
sync
```

**Trigger a re-scan.** The plugin directory is read at HMI start, so restart the HMI process (stop `HmiMain3D` and let it respawn, ~10–30 s) or reboot the unit.

**Validate.** `/tmp` is RAM and readable over ssh while the HMI runs:

```sh
ls -l /tmp/myplugin_loaded     # written by the .so constructor on dlopen  -> DISCOVERY + LOAD proven
ls -l /tmp/myplugin_created    # written when the framework calls create() -> descriptor/ABI accepted
sloginfo | grep -i myplugin    # any framework log line about your plugin
```

Both files present = the loader found, `dlopen`'d, accepted your descriptor, and constructed your app. A "MyPlugin" entry should also appear in the vehicle-info menu (from the DescFile).

**Rollback is total:** `rm -rf …/Plugins/MyPlugin ; sync ; restart HMI`. Nothing in the HMI binary changed — the plugin is loose files.

---

## Stage 1 — "A screen with a button + a list"

**Goal:** turn the placeholder entry into a real screen — one button and one list you fill with your own rows. You will now subclass `bmw::PluginApp`, override `onInit()` (vtable slot 22), register a button handler with `addHandler()`, and push data into a list model with `updateModel()`.

### Files that change

**`MyPlugin.xml`** — declare a screen (`hmiState`), the components on it, the actions they fire, and the list model. Screen `100` now exists, so the Stage 0 entry becomes fully functional:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<pluginApps>
  <pluginApp applicationType="VehicleInformation" applicationWeight="200" text="MyPlugin">
    <comment/>
    <entryButton action="10" id="1">
      <properties>
        <property id="23" value="2"/>
      </properties>
    </entryButton>
    <actions>
      <hmiAction id="10" target="100"/>   <!-- entry button -> screen 100 -->
      <raAction  id="21"/>                <!-- "Do it" button pressed -> our C++ callback -->
      <raAction  id="23"/>                <!-- a list row was selected -> our C++ callback -->
    </actions>
    <models>
      <raListModel id="50"/>              <!-- the list we fill from C++ -->
    </models>
    <hmiStates>
      <hmiState id="100" text="MyPlugin">
        <components>
          <button id="3" action="21" text="Do it"/>
          <separator id="4"/>
          <list id="5" model="50" action="23"/>
        </components>
      </hmiState>
    </hmiStates>
  </pluginApp>
</pluginApps>
```

Two kinds of action appear here, and the difference is the whole navigation model:

| Action element | Fires | Handled by |
|----------------|-------|------------|
| `hmiAction` | Navigation to another `hmiState` (`target=`) | The HMI itself — no C++ callback |
| `raAction` | A "remote application" callback | **Your** plugin, via `addHandler(id, delegate)` |

A `button` carries an `action`; a `list` carries both a `model` (what it displays) and an `action` (fired on row select). Component ids, action ids, and model ids share one namespace within a `pluginApp` and must all be distinct. Full component/property/action vocabulary: [03-descfile-xml-reference.md](03-descfile-xml-reference.md) (component and action declarations) and [04-menus-screens-and-layout.md](04-menus-screens-and-layout.md) (the property-id catalog).

**`myplugin.cpp`** — switch to `bmw_list.h`, subclass, and implement `onInit()`:

```cpp
// myplugin.cpp — Stage-1: one screen, one button, one populated list.
#include "bmw_list.h"
#include <cstdio>

class MyPlugin : public bmw::PluginApp {
public:
    MyPlugin(bmw::IDispatcher& d, bmw::BasicString<char> name,
             unsigned maj, unsigned min, bmw::RHMIInterfaceVersion rhmi,
             const bmw::Bundle& cfg, const bmw::Bundle& res)
        : bmw::PluginApp(d, name, maj, min, rhmi, cfg, res) {}

    virtual bool onInit();                    // slot 22 — populate models + register handlers
    bool onButton(const bmw::Parcel& p);      // raAction 21
    bool onRow   (const bmw::Parcel& p);      // raAction 23
};

// Helper: append one string cell as row r, column 0, of a 1-column table.
static void add_row(bmw::DataTable<1>& t, unsigned r, const char* s) {
    bmw::Variant& cell = t.at(r, 0);          // inserts row r; cell.m_impl starts null
    cell.m_impl = new bmw::Variant::ObjectContainer<bmw::BasicString<char> >(
                      bmw::BasicString<char>(s));   // Variant tag 34 = string
}

bool MyPlugin::onInit()
{
    // 1. Build a 1-column list with >= 1 row and push it to raListModel 50.
    static const char* const kRows[] = { "Ready", "Row two", "Row three" };
    const unsigned N = sizeof(kRows) / sizeof(kRows[0]);

    bmw::DataTable<1> table;                   // one column, on the STACK
    for (unsigned r = 0; r < N; ++r) add_row(table, r, kRows[r]);
    updateModel(50u, table);                   // deep-copied by the framework
    // table's dtor -> clear() frees our column Variants; the framework kept its own copy.

    // 2. Wire the button and the row-select action to our methods.
    bmw::Delegate<bool, const bmw::Parcel&> dBtn;
    dBtn.m_obj  = this;
    dBtn.m_exec = &bmw::Delegate<bool, const bmw::Parcel&>
                    ::execImpl<MyPlugin, &MyPlugin::onButton>;
    addHandler(21u, dBtn);

    bmw::Delegate<bool, const bmw::Parcel&> dRow;
    dRow.m_obj  = this;
    dRow.m_exec = &bmw::Delegate<bool, const bmw::Parcel&>
                    ::execImpl<MyPlugin, &MyPlugin::onRow>;
    addHandler(23u, dRow);

    return true;
}

bool MyPlugin::onButton(const bmw::Parcel& /*p*/) {
    // Rebuild and re-push the list, or kick off work (Stage 2).
    return true;   // true = handled
}

bool MyPlugin::onRow(const bmw::Parcel& p) {
    int idx = -1;
    p.readInt32(idx);      // selected row index (verify field order on your build)
    (void)idx;
    return true;
}

// --- loader descriptor: same 24-byte ABI, now creating our subclass ---
struct PluginAppInfo {
    unsigned int abiVersion; const char* name; const char* vendor; unsigned int ifaceVersion;
    bmw::PluginApp* (*create)(bmw::IDispatcher&, const char*, const bmw::Bundle&, const bmw::Bundle&);
    void (*destroy)(bmw::PluginApp*);
};
static bmw::PluginApp* my_create(bmw::IDispatcher& d, const char* nm,
                                 const bmw::Bundle& c, const bmw::Bundle& r) {
    bmw::RHMIInterfaceVersion rhmi; rhmi.value = 1;
    return new MyPlugin(d, bmw::BasicString<char>(nm), 1u, 0u, rhmi, c, r);
}
static void my_destroy(bmw::PluginApp* app) { delete app; }   // real dtor now
extern "C" PluginAppInfo pluginAppInfo = {
    1, "MyPlugin", "yourname", 1, my_create, my_destroy
};
```

What each new piece is doing:

- **`onInit()` is vtable slot 22.** The framework calls it after construction; it is where you populate models and register handlers. Overriding it is the whole point of subclassing. The base class provides the other 33 slots (`start`/`stop`/`activate`/…/`handleEvent`/…); you only override what you need. Slot map: [05-cxx-abi-and-data-types.md](05-cxx-abi-and-data-types.md).
- **`DataTable<1>` + `Variant::ObjectContainer<BasicString<char>>` (tag 34) is the list idiom.** `table.at(r,0)` inserts the cell and returns a `Variant&` whose `m_impl` is null; you assign a heap `ObjectContainer` holding a string. `updateModel(50u, table)` **deep-copies** the table into the framework's model, so it is safe to let your local, stack-allocated `table` destruct immediately afterward (its `clear()` frees your copies). Prefer a stack `DataTable` so it is freed automatically.
- **Never push an empty list.** Always add at least one row before `updateModel`. An empty list model has been observed to cause a re-entry crash; keep a "Ready"/placeholder row when you have nothing else.
- **`Delegate` is an 8-byte `{object, static thunk}` pair.** `execImpl<Class, &Class::method>` is a compile-time-generated static function that casts `void*` back to your object and calls the member. `addHandler` binds a `raAction` id to it. Two overloads exist: the **`(action, delegate)`** form (2 arguments, `@0x5970`) registers a handler by action id, and the **`(state, action, delegate)`** form (3 arguments, `@0x5db0`) also takes a state id — read as scoping the handler to one screen, with the shorter form registering it more broadly (the shorter form is what this tutorial uses; the state-scoping semantics are inferred from the extra parameter, not traced in the disassembly).

**Build/deploy/observe:** rebuild, redeploy the three files, restart the HMI. Open **MyPlugin** from the vehicle menu → you land on screen 100 with a "Do it" button, a separator, and a three-row list. Selecting a row fires `onRow`; pressing the button fires `onButton`. Add a `dlog()`-style file trace inside each (see Stage 2's `dlog`) if you want to confirm the callbacks over ssh.

---

## Stage 2 — "Do real work safely"

**Goal:** make the button *do something* — run a real background job and stream its output into the list — **without ever blocking or destabilizing the HMI**. This is the single most important pattern in the SDK, because everything in a plugin runs on the HMI's UI/dispatcher thread.

> The working reference plugin used this exact structure to drive an external process and stream its results into the list. **Here the payload is deliberately neutral** — we run a harmless shell command that writes a file, then display the file. Swap in whatever your own plugin actually does; the *safety structure* is what you copy verbatim.

### The three rules

1. **Do the slow work in a separate process.** `posix_spawn` returns immediately; the child's I/O and any bug it has can never touch `HmiMain3D`'s address space. Redirect the child's stdio to `/dev/null`.
2. **Never block the UI thread.** Do not `waitpid()` (blocking) on the UI thread. Instead, post a self-rescheduling `bmw::Runnable` that polls the child with `waitpid(…, WNOHANG)` every few hundred ms.
3. **Touch models and properties only on the UI thread.** `updateModel()` and `setProperty()` are called from `onInit`, from your `raAction` handlers, and from the poller's `run()` — all of which the framework runs on the UI thread. Never call them from any thread you spawned yourself.

### Files that change

**`MyPlugin.xml`** — give the button a `SELECTABLE` property so you can grey it while the job runs. Property id `2` is `SELECTABLE` (enabled/greyed):

```xml
<hmiState id="100" text="MyPlugin">
  <components>
    <button id="3" action="21" text="Run job">
      <properties>
        <property id="2" value="true"/>     <!-- SELECTABLE: starts enabled -->
      </properties>
    </button>
    <separator id="4"/>
    <list id="5" model="50" action="23"/>
  </components>
</hmiState>
```

**`myplugin.cpp`** — add the spawn + poller + greying. This is the diagnostics-stage structure with a neutral command:

```cpp
// myplugin.cpp — Stage-2: run a background job, stream output, keep the UI live.
#include "bmw_list.h"
#include <cstdio>
#include <cstring>
#include <spawn.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>

extern char **environ;

enum {
    RUN_BTN         = 3,    // component id (setProperty target)
    PROP_SELECTABLE = 2,    // property id: enabled/greyed
    LIST_MODEL      = 50,
    RUN_ACTION      = 21,   // raAction ids
    ROW_ACTION      = 23
};
static const char* OUT = "/tmp/myplugin_out.txt";   // job output (RAM, always writable)

// Crash-proof file trace: reopen+flush+close per line, so a crash never loses it.
static void dlog(const char* s){ FILE* f=fopen("/tmp/myplugin_trace.log","a"); if(f){fputs(s,f);fputc('\n',f);fclose(f);} }

static long file_size(const char* p){ FILE* f=fopen(p,"rb"); if(!f) return -1; fseek(f,0,SEEK_END); long s=ftell(f); fclose(f); return s; }

class MyPlugin;   // fwd

// A self-rescheduling poller. Runs on the UI thread; reposts itself until the child exits.
class ChildPoller : public bmw::Runnable {
public:
    ChildPoller(MyPlugin* app, pid_t pid, unsigned ms) : app_(app), pid_(pid), ms_(ms) {}
    virtual ~ChildPoller() {}
    virtual void run();                          // vtable slot 2
private:
    MyPlugin* app_; pid_t pid_; unsigned ms_;
};

class MyPlugin : public bmw::PluginApp {
public:
    MyPlugin(bmw::IDispatcher& d, bmw::BasicString<char> name, unsigned maj, unsigned mn,
             bmw::RHMIInterfaceVersion rhmi, const bmw::Bundle& cfg, const bmw::Bundle& res)
        : bmw::PluginApp(d,name,maj,mn,rhmi,cfg,res), busy_(false), pid_(0), last_(-1) {}

    virtual bool onInit();
    bool onRun(const bmw::Parcel&);              // raAction 21
    bool onRow(const bmw::Parcel&);              // raAction 23

    void refresh();                              // rebuild the list from OUT (UI thread only)
    void set_button(unsigned comp, bool en);     // grey / un-grey via SELECTABLE
    void on_poll_running();                      // per-tick, while child alive
    void on_job_done();                          // child exited

    bool  busy_;
    pid_t pid_;
    long  last_;
};

static void add_row(bmw::DataTable<1>& t, unsigned r, const char* s){
    bmw::Variant& c = t.at(r,0);
    c.m_impl = new bmw::Variant::ObjectContainer<bmw::BasicString<char> >(bmw::BasicString<char>(s));
}

void MyPlugin::refresh(){
    bmw::DataTable<1> t;                                 // STACK object -> freed on return
    unsigned n = 0;
    FILE* f = fopen(OUT, "r");
    if (f){
        char buf[256];
        while (n < 400 && fgets(buf, sizeof buf, f)){
            int L=(int)strlen(buf);
            while (L>0 && (buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
            if (L) add_row(t, n++, buf);
        }
        fclose(f);
    }
    if (n == 0) add_row(t, n++, busy_ ? "Working..." : "Press \"Run job\"");
    updateModel((unsigned)LIST_MODEL, t);                // deep-copied; t's dtor frees our cells
}

void MyPlugin::set_button(unsigned comp, bool en){
    bmw::Parcel p(en);                                   // Parcel(bool) carries the value
    setProperty(comp, (unsigned)PROP_SELECTABLE, p);
}

bool MyPlugin::onRun(const bmw::Parcel&){
    if (busy_) return true;
    remove(OUT);
    // NEUTRAL payload: harmless command that writes OUT. Replace with your own work.
    char* argv[] = { (char*)"/bin/sh", (char*)"-c",
                     (char*)"ls -la /fs/sda0 > /tmp/myplugin_out.txt", 0 };
    posix_spawn_file_actions_t fa;
    posix_spawn_file_actions_init(&fa);
    posix_spawn_file_actions_addopen(&fa, 0, "/dev/null", O_RDONLY, 0);
    posix_spawn_file_actions_addopen(&fa, 1, "/dev/null", O_WRONLY, 0);
    posix_spawn_file_actions_addopen(&fa, 2, "/dev/null", O_WRONLY, 0);
    pid_t pid = 0;
    int rc = posix_spawn(&pid, "/bin/sh", &fa, 0, argv, environ);
    posix_spawn_file_actions_destroy(&fa);
    if (rc != 0){ dlog("[app] posix_spawn failed"); return true; }

    busy_ = true; pid_ = pid; last_ = -1;
    set_button((unsigned)RUN_BTN, false);                // grey the button while working
    refresh();                                           // show "Working..."
    post(new ChildPoller(this, pid, 400u), 400u);        // start polling in 400 ms
    return true;
}

bool MyPlugin::onRow(const bmw::Parcel& p){ int i=-1; p.readInt32(i); (void)i; return true; }

void MyPlugin::on_poll_running(){
    long sz = file_size(OUT);
    if (sz != last_){ last_ = sz; refresh(); }           // stream output as the file grows
}
void MyPlugin::on_job_done(){
    busy_ = false;
    refresh();
    set_button((unsigned)RUN_BTN, true);                 // un-grey when finished
}

bool MyPlugin::onInit(){
    refresh();                                           // initial hint (no job on boot)
    bmw::Delegate<bool, const bmw::Parcel&> dRun; dRun.m_obj=this;
    dRun.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<MyPlugin,&MyPlugin::onRun>;
    addHandler((unsigned)RUN_ACTION, dRun);
    bmw::Delegate<bool, const bmw::Parcel&> dRow; dRow.m_obj=this;
    dRow.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<MyPlugin,&MyPlugin::onRow>;
    addHandler((unsigned)ROW_ACTION, dRow);
    return true;
}

// The poller: polls without blocking; reposts itself; deletes itself when the child exits.
void ChildPoller::run(){
    int st = 0;
    pid_t r = ::waitpid(pid_, &st, WNOHANG);
    if (r == 0){ app_->on_poll_running(); app_->post(this, ms_); return; }  // alive -> repost
    app_->on_job_done();
    delete this;                                          // done -> free (LAST statement)
}

struct PluginAppInfo {
    unsigned int abiVersion; const char* name; const char* vendor; unsigned int ifaceVersion;
    bmw::PluginApp* (*create)(bmw::IDispatcher&, const char*, const bmw::Bundle&, const bmw::Bundle&);
    void (*destroy)(bmw::PluginApp*);
};
static bmw::PluginApp* my_create(bmw::IDispatcher& d, const char* nm, const bmw::Bundle& c, const bmw::Bundle& r){
    bmw::RHMIInterfaceVersion v; v.value = 1;
    return new MyPlugin(d, bmw::BasicString<char>(nm), 1u, 0u, v, c, r);
}
static void my_destroy(bmw::PluginApp* a){ delete a; }
extern "C" PluginAppInfo pluginAppInfo = {
    1, "MyPlugin", "yourname", 1, my_create, my_destroy
};
```

> **Note on `refresh()` vs. the reference source.** The reference `diagnostics8.cpp` heap-allocates its per-refresh table (`new bmw::DataTable<1>()`) and never deletes it — a small leak on every poll tick, harmless in practice but a real defect. Because `updateModel()` deep-copies, a **stack** `DataTable<1>` (as shown above) is both correct and simpler: it frees your row `Variant`s automatically when `refresh()` returns. Use the stack form.

The `Runnable` lifecycle is subtle and matters:

- **`post(runnable, ms)` schedules `run()` on the UI thread after `ms` milliseconds.** Inside `run()` you decide the object's fate: a *rescheduling* runnable calls `post(this, ms)` again and returns **without** deleting; a *one-shot* calls `delete this` as its **last** statement. The framework never frees a `Runnable` for you. Here, while the child is alive we repost; once `waitpid` reaps it we finalize and `delete this`.
- **`Runnable`'s destructor is intentionally defined inline in `bmw_list.h`.** The OEM libs export only the `D1`/`D0` variants of `~Runnable`, not the base-object `D2` that a derived class's destructor calls. Defining `~Runnable(){}` in the header emits local weak `D2`/`D1`/`D0` so `dlopen(RTLD_NOW)` resolves them, and the vtable/typeinfo become COMDAT-weak and merge with the libs' copies. If you re-declare `Runnable` yourself and omit that inline body, the plugin fails to load with an undefined-symbol error for `_ZN3bmw8RunnableD2Ev`.
- **`setProperty(comp, 2, Parcel(bool))` greys/un-greys a component.** `Parcel(bool)` is a real framework ctor that writes the value into the parcel; property `2` is `SELECTABLE`. Full property-id table: [04-menus-screens-and-layout.md](04-menus-screens-and-layout.md).

**Build/deploy/observe:** rebuild, redeploy, restart HMI, open MyPlugin, press **Run job**. The button greys, the list shows "Working…", then fills with the command's output, and the button un-greys — and the HMI stays fully responsive throughout. Watch `/tmp/myplugin_trace.log` over ssh to follow the lifecycle.

---

## Where to go next

You now have the full skeleton. Each dimension has a dedicated reference doc:

| If you want to… | See |
|-----------------|-----|
| Understand RA plugins vs. the `hmiplugins/` remoting Bundles vs. the `libhmiplugin.so` device-abstraction layer, and the whole load pipeline | [01-architecture-and-loading.md](01-architecture-and-loading.md) |
| Every field of the `.manifest` (connectors, TextDB/ImageDB, parameters) | [02-manifest-format.md](02-manifest-format.md) |
| The full DescFile schema — `pluginApp`, `hmiState`, `layoutGroup`, `optionComponents`, master/detail | [03-descfile-xml-reference.md](03-descfile-xml-reference.md), with layout in [04-menus-screens-and-layout.md](04-menus-screens-and-layout.md) |
| Every component (`button`/`list`/`label`/`checkbox`/`radiobutton`/`gauge`/`image`/`separator`) and every `property id` (including `entryButton` property `23`) | [03-descfile-xml-reference.md](03-descfile-xml-reference.md) (components) and [04-menus-screens-and-layout.md](04-menus-screens-and-layout.md) (property-id catalog) |
| `hmiAction` vs `raAction`, events, `Continuous` actions, option menus | [03-descfile-xml-reference.md](03-descfile-xml-reference.md) (action declarations) and [06-runtime-api-reference.md](06-runtime-api-reference.md) (`addHandler` wiring) |
| Model types (`raListModel`/`raDataModel`/`textIdModel`/`imageIdModel`/`raBoolModel`/…), `DataTable<N>`, multi-column tables, `Variant` tags | [05-cxx-abi-and-data-types.md](05-cxx-abi-and-data-types.md) (`DataTable`/`Variant` types) and [06-runtime-api-reference.md](06-runtime-api-reference.md) (runtime model updates) |
| The 34-slot vtable, ctor ABI, `Delegate` thunks, `Parcel`, offsets | [05-cxx-abi-and-data-types.md](05-cxx-abi-and-data-types.md) |
| The threading model, `Runnable` lifecycle, cross-thread rules in depth | [07-threading-and-safety-model.md](07-threading-and-safety-model.md) |
| Toolchain setup, packaging, and the deploy/rollback loop | [08-building-and-deploying.md](08-building-and-deploying.md) |

**Open questions this tutorial does not resolve** (deferred to the reference docs, and not fully pinned from the carve):

- **Multi-column lists.** This tutorial only builds a 1-column `DataTable<1>`. `DataTable<N>` for `N>1` and how columns map to list slots are covered in [05-cxx-abi-and-data-types.md](05-cxx-abi-and-data-types.md) (the `DataTable` type) and [06-runtime-api-reference.md](06-runtime-api-reference.md) (pushing models at runtime); a 1-column list is the safe starting point.
- **`entryButton` property `23`.** Carried verbatim by the reference and OEM entry buttons (`value="2"`); copy it as shown. Its precise meaning is documented in the [property-id catalog](04-menus-screens-and-layout.md).
- **`pluginAppConnector` semantics.** Beyond "pick an id no other plugin uses," what the `Etch` connector brokers, whether the id must be globally unique across installed plugins, and the role of `asyncCallbacks` are open; see [02-manifest-format.md](02-manifest-format.md).
- **`Parcel` field order** for a selected row index (`readInt32`) is flagged build-dependent in the reference source; verify it live on your firmware.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| No `/tmp/*_loaded` marker; `sloginfo` shows `Plugin does not contain a pluginAppInfo entry point` | Symbol not exported, mis-named, or C++-mangled | Export `extern "C" PluginAppInfo pluginAppInfo = …`; verify with `nm -D lib*.so \| grep pluginAppInfo` → type `D` |
| `_loaded` marker present but `dlopen` fails with an undefined-symbol error (no `_created`) | A `bmw::*` symbol did not resolve — wrong/missing framework lib, or the `Runnable` `D2` gotcha | Confirm `NEEDED` lists `libAppFramework.A.so` + `libCoreFramework.A.so`; keep the inline `~Runnable(){}` from `bmw_list.h`; build with the matching gcc 4.4.2 toolchain |
| `sloginfo` shows `The plugin's pluginAppInfo entry point is invalid` | Descriptor fields wrong — bad `create`/`destroy` pointers or `abiVersion`/`ifaceVersion` the ctor rejects | Match the 24-byte layout exactly; use `abiVersion=1`, `ifaceVersion=1`, and set `rhmi.value` equal to `ifaceVersion` |
| No menu entry appears, but markers are written | DescFile not parsed or `applicationType` unknown | Check `<DescFile>` path in the manifest; use a known `applicationType` (e.g. `VehicleInformation`); watch for `application popup for state '%d' has invalid application type %d` |
| Menu entry appears but pressing it misbehaves / dead-ends | `hmiAction` `target` points at an `hmiState` that is not defined (the Stage-0 situation) | Define an `hmiState` for every `hmiAction` target before wiring the entry button |
| `create()` never called (no `_created` marker) | `<autoStart>` off, or `create` field null | Set `<autoStart>yes</autoStart>`; ensure the descriptor's `create` points at your function |
| List is blank or the HMI crashes on navigation into the screen | Empty list model pushed, or `updateModel` called before a row was added | Always `add_row(...)` at least one row before `updateModel`; keep a placeholder row |
| Crash on row select or button press | Handler not registered for that `raAction` id, or `Delegate.m_obj`/`m_exec` not set | Register every `raAction` in `onInit` with a fully-populated `Delegate`; ids in the DescFile must match the `addHandler` ids |
| HMI freezes while your job runs | Blocking call on the UI thread (`waitpid` without `WNOHANG`, blocking socket/read) | Move slow work to a `posix_spawn` child; poll with a self-reposting `Runnable` using `WNOHANG` |
| Random corruption / crashes under load | `updateModel`/`setProperty` called from a thread you spawned | Only ever touch models/properties from `onInit`, `raAction` handlers, or a posted `Runnable::run()` (all UI-thread) |
| Handler component ids "work" for one screen but collide | Component/action/model ids not unique within the `pluginApp` | Keep every id distinct; use an `enum` of named ids as in Stage 2 |

---

## Sources

These facts come from an **owner-authorized offline flash carve** of the author's own titled vehicle's NBT-Evo HMI partition, plus **end-to-end validation on the author's OPT_DEBUG-enabled unit** of the discovery → `dlopen` → `create` → screen → background-job flow using a reference plugin. Every non-obvious claim is grounded in a primary source that was opened directly:

- **Carve-confirmed schema** — the manifest and DescFile vocabulary was cross-checked against the OEM `SecurityMenu` and `ActiveSeating` plugins and against the reference PowerTools `Diagnostics.manifest` / `Diagnostics.xml`; the two loader error strings and the `/Plugins/` vs `/PluginsCoded` paths are present verbatim in the `HmiMain3D` binary.
- **Verified end-to-end on the author's OPT_DEBUG-enabled unit** — discovery and construction of an unsigned, un-coded plugin from `data/ro/Plugins/`; the `updateModel`/`addHandler`/`setProperty`/ctor/`post` symbol offsets; the `SELECTABLE=2` greying; and the end-to-end `ChildPoller` background-job flow (demonstrated with the reference plugin, reproduced here with a neutral payload). This is a result on the author's own OPT_DEBUG-enabled unit, **not** a claim about a stock unit; a stock unit enforces no signature on load (the loader links no crypto; confirmed on-car) — see `14-signing-and-coding.md`.
- **Reconstructed ABI (marked as such)** — `bmw_abi.h` and `bmw_list.h` are **hand-reconstructed** from RE of `libAppFramework.A.so`, `libCoreFramework.A.so`, and `HmiMain3D`; they are **not** an OEM SDK. Class bodies resolve at `dlopen`. Every offset and signature cited (e.g. `onInit` slot 22, `Runnable::run` slot 2, the 34-slot primary vtable, `addHandler` `@0x5970`/`@0x5db0`, `updateModel` `@0x539c`) was matched against the real exported symbols and agrees — but treat it as reconstructed ABI and re-verify against your own carve if your firmware differs.
- **RE-derived behavioral notes** — "`updateModel` deep-copies the `DataTable`," "an empty list model can trigger a re-entry crash," and the state-scoping reading of the 3-argument `addHandler` are conclusions drawn from source comments and observed behavior, not independently instrumented; they are flagged where they appear.
