# 07 — Threading, Lifecycle Safety & Best Practices

*Reverse-engineered from an offline flash carve and verified end-to-end on the author's own titled vehicle — an **OPT_DEBUG-enabled** unit. A stock unit enforces no signature on load (the loader links no cryptography; confirmed on-car — see `14-signing-and-coding.md`); still, write and test everything on a head unit you own. This document describes the plugin **mechanics** generically.*

This is the "how to not crash the HMI" chapter. An RA plugin runs **inside** the HMI process (`HmiMain3D`). There is no sandbox: a segfault, an infinite loop, or a blocking syscall in your plugin is a segfault / freeze / hang of the whole infotainment UI. The good news is that the reference plugin ([`capabilities/plugins/reference/example-plugin/hello_plugin_stage1.cpp`](../reference/example-plugin/diagnostics.cpp)) reaches a design that is **safe by construction**, and every safety property below is something you can copy verbatim.

If you read only one thing: **your code always runs on the HMI's single UI/dispatcher thread. Never block it. Do blocking work in a separate process, and poll that process from the UI thread.**

> **Verified vs. Reconstructed — read this first.** The framework **symbol addresses and mangled names** cited below are *carve-confirmed* (`nm -DC` on the real OEM `.so`s). The **runtime behaviors** — the single-thread guarantee, the `updateModel` deep-copy, "the framework never frees your `Runnable`", the per-cell `clone()` mechanism — are *reconstructed*: inferred from disassembly, from the hand-written SDK headers ([`bmw_list.h`](../reference/sdk/bmw_list.h) banner), and from the reference plugin's behavior observed on the author's OPT_DEBUG-enabled unit. Where a claim is reconstructed rather than carve-proven, this doc says so inline. The safe design in §2 holds either way, which is the point of building it that way.

---

## 1. The single-thread rule

Every entry point the framework calls into your plugin runs on **one** thread — the HMI dispatcher (UI) thread:

| Entry point | Declared as | Runs on |
|---|---|---|
| `onInit()` | `bmw::PluginApp` vtable slot 22 | UI thread |
| `onFinalize()` | vtable slot 23 | UI thread |
| Your action handlers (`onBuild`, `onRow`, …) | registered via `addHandler()` | UI thread |
| `Runnable::run()` | your `post()`-ed runnable | UI thread |

**Structural evidence (carve-confirmed):** `PluginApp` inherits `PluginAppHandler`, which derives from `bmw::AbstractHandler`, whose constructor takes a `bmw::IDispatcher&`. In `libAppFramework.A.so` that constructor appears only as an **undefined reference** (`U bmw::AbstractHandler::AbstractHandler(bmw::IDispatcher&)`, `nm -DC`); it is *defined and exported* by `libCoreFramework.A.so` (`0000f590 T …`) and resolved from there at load. The link relationship still proves `PluginAppHandler` is-a dispatcher-backed `AbstractHandler(IDispatcher&)`. The dispatch entry point itself **is** a `libAppFramework` export — `bmw::PluginAppHandler::dispatch()` @ `0xa5cc` — and the `post(Runnable*)` family are members of that same handler (`bmw::PluginAppHandler::post(bmw::Runnable*)` @ `0xa804`, `post(bmw::Runnable*, unsigned int)` @ `0xa790`). So a posted `Runnable` is drained by the same dispatch loop that delivers your action callbacks.

The reference plugin's own header comment states the rule in its own words — quoting it exactly ([`diagnostics.cpp:16-18`](../reference/example-plugin/diagnostics.cpp)):

> *"every scan is an isolated child (posix_spawn); the UI thread never blocks; a self-rescheduling Runnable polls waitpid(WNOHANG) ON THE UI THREAD (post, ms) and does all model/property updates there."*

*(This single-thread guarantee is **reconstructed** — structurally consistent with the exported `PluginAppHandler`/`IDispatcher`/`dispatch()` symbols and stated in the plugin's own design notes, but the stripped carve cannot prove the dispatcher never delivers a callback on another thread. The design below is safe regardless, because it never touches the model outside the paths the framework invokes.)*

**Two consequences, both mandatory:**

1. **Never block the UI thread.** No synchronous socket I/O, no `waitpid()` without `WNOHANG`, no `sleep()`, no large file parse, no anything that can take more than a few milliseconds. While you are inside `onInit()` / a handler / `run()`, the HMI is *not painting and not handling input*.
2. **All model and property updates must happen on the UI thread.** `updateModel(...)` (@ `0x539c` for the `DataTableBase` overload, [`bmw_list.h`](../reference/sdk/bmw_list.h)) and `setProperty(...)` (@ `0x54a4`, [`bmw_list.h`](../reference/sdk/bmw_list.h)) are **not** thread-safe entry points. Because the safe design (below) only ever calls them from `onInit`, from handlers, and from `Runnable::run()` — all UI-thread — you never touch the model from anywhere else.

> An earlier reverse-engineering stage reaped the child with a *detached worker thread* and was careful to keep `updateModel()` off that thread (a `pthread_create`/`detach` pair). **That approach is superseded.** The mature design (§2) drops `pthread` entirely (no `<pthread.h>` in [`diagnostics.cpp:20-26`](../reference/example-plugin/diagnostics.cpp)) and does the reaping on the UI thread via a self-rescheduling `Runnable`, so there is no worker thread to get wrong. Do not reintroduce a worker thread.

---

## 2. The long-work pattern (child process + self-rescheduling poller)

Any real plugin eventually needs to do something slow: talk to a bus, read a file that takes seconds to fill, run a scan. The proven pattern has **two** isolation layers:

1. **Process isolation** — the blocking job runs in a separate process launched with `posix_spawn()`. Its address space is its own, so a hang or crash in the worker *cannot* corrupt or take down `HmiMain3D`. The worst case is a stuck child, which you never `wait()` for blockingly.
2. **Non-blocking reaping** — a `bmw::Runnable` that you re-post on a timer polls the child with `waitpid(..., WNOHANG)` and refreshes models as the child's output file grows. Each poll is a few microseconds on the UI thread; between polls the UI is fully live.

### 2.1 The poller

`bmw::Runnable` is the root interface: `sizeof 4` (vptr only), vtable `[~D1, ~D0, run()]` with `run()` at slot 2, and you override `run()` ([`bmw_list.h`](../reference/sdk/bmw_list.h)). Subclass it to hold a back-pointer to your app, the child `pid`, and the poll interval:

```cpp
class MyApp;   // fwd

// Self-rescheduling UI-thread poller for a spawned worker child.
class ChildPoller : public bmw::Runnable {
public:
    ChildPoller(MyApp* app, pid_t pid, unsigned ms) : app_(app), pid_(pid), ms_(ms) {}
    virtual ~ChildPoller() {}
    virtual void run();
private:
    MyApp*   app_;
    pid_t    pid_;
    unsigned ms_;
};
```
*(shape from [`diagnostics.cpp:67-74`](../reference/example-plugin/diagnostics.cpp))*

The whole safety story lives in `run()` — five lines:

```cpp
void ChildPoller::run() {
    int st = 0;
    pid_t r = ::waitpid(pid_, &st, WNOHANG);      // NON-blocking: returns 0 if still running
    if (r == 0) {                                 // child alive ->
        app_->on_poll_running();                  //   refresh models if output grew
        app_->post(this, ms_);                    //   re-post SELF for the next tick
        return;                                   //   ...and DO NOT delete
    }
    app_->on_scan_done();                         // child exited -> finalize once
    delete this;                                  // last tick only: free the runnable
}
```
*(verbatim structure from [`diagnostics.cpp:352-358`](../reference/example-plugin/diagnostics.cpp))*

### 2.2 Spawning and arming the poller

```cpp
void MyApp::spawn_and_poll(int kind, char* const argv[]) {
    if (scanning_) return;                        // single-flight: never two children at once

    // Detach the child's stdio so it can never inherit or block on the HMI's fds.
    posix_spawn_file_actions_t fa;
    posix_spawn_file_actions_init(&fa);
    posix_spawn_file_actions_addopen(&fa, 0, "/dev/null", O_RDONLY, 0);
    posix_spawn_file_actions_addopen(&fa, 1, "/dev/null", O_WRONLY, 0);
    posix_spawn_file_actions_addopen(&fa, 2, "/dev/null", O_WRONLY, 0);

    pid_t pid = 0;
    int rc = posix_spawn(&pid, WORKER_BIN, &fa, 0, argv, environ);
    posix_spawn_file_actions_destroy(&fa);
    if (rc != 0) return;                          // spawn failed -> stay idle, UI untouched

    scanning_ = true; scan_kind_ = kind; pid_ = pid; last_res_size_ = -1;
    set_button(RUN_BTN, false);                   // grey the trigger so it can't re-fire
    refresh_view();                               // show "Working..." immediately

    post(new ChildPoller(this, pid, 400u), 400u); // arm the first tick, +400 ms
}
```
*(genericized from [`diagnostics.cpp:199-221`](../reference/example-plugin/diagnostics.cpp); the reference uses `posix_spawn` with all three std fds redirected to `/dev/null`, sets `scanning_`, greys the button, and `post(new ChildPoller(this, pid, 400u), 400u)`)*

`post(Runnable*, unsigned int ms)` is `PluginApp` vtable slot 11 ([`bmw_list.h`](../reference/sdk/bmw_list.h)); the `ms` argument is a delay, so re-posting with the same `ms` gives you a fixed-interval timer. *(That a delayed `post(this, ms)` ticks only while the dispatcher is idle enough to service it is the natural behavior of a single-threaded dispatcher, but **not measurable** from a stripped carve; treat the exact scheduling/priority as uncharacterized and design so that a late tick is harmless — which the growth-gated refresh in §2.3 ensures.)*

### 2.3 The per-tick and finalize hooks

The poller calls two app methods. `on_poll_running()` does incremental UI refresh **only when the output actually grew** (cheap, and avoids pointless deep-copies):

```cpp
void MyApp::on_poll_running() {
    long sz = file_size(RESULT_FILE);
    if (sz != last_res_size_) {                   // only refresh on real growth
        last_res_size_ = sz;
        refresh_view();                           // re-reads file, calls updateModel(...)
    }
}
```
*(from [`diagnostics.cpp:298-307`](../reference/example-plugin/diagnostics.cpp))*

`on_scan_done()` runs exactly once, clears the single-flight flag, does a final refresh, and re-enables the trigger button:

```cpp
void MyApp::on_scan_done() {
    scanning_ = false;
    refresh_view();                               // final, complete result
    set_button(RUN_BTN, true);                    // un-grey the trigger
}
```
*(from [`diagnostics.cpp:309-321`](../reference/example-plugin/diagnostics.cpp))*

### 2.4 Why each piece is safe

| Property | What guarantees it | Failure it prevents |
|---|---|---|
| Blocking work is in a child | `posix_spawn` gives a separate address space & PID ([`diagnostics.cpp:207`](../reference/example-plugin/diagnostics.cpp)) | A crash/hang in the worker cannot fault `HmiMain3D` |
| UI thread never blocks | `waitpid(..., WNOHANG)` returns immediately ([`diagnostics.cpp:354`](../reference/example-plugin/diagnostics.cpp)) | UI freeze while the job runs |
| Timer re-queues, not spins | `post(this, ms)` re-queues on the dispatcher ([`diagnostics.cpp:355`](../reference/example-plugin/diagnostics.cpp)) | Busy-waiting / starving the dispatcher |
| Model touched only on UI thread | `on_poll_running`/`on_scan_done` are called from `run()` ([`diagnostics.cpp:355-356`](../reference/example-plugin/diagnostics.cpp)) | Cross-thread `updateModel` corruption |
| No double-free / leak of the poller | one-shot terminal `delete this`; alive path re-posts and returns ([`diagnostics.cpp:355-357`](../reference/example-plugin/diagnostics.cpp)) | Use-after-free or leaked `Runnable` |
| One job at a time | `scanning_` guard at the top of `spawn_and_poll` ([`diagnostics.cpp:200`](../reference/example-plugin/diagnostics.cpp)) | Two children racing the same output file |
| Child can't touch HMI fds | all three std fds redirected to `/dev/null` ([`diagnostics.cpp:203-205`](../reference/example-plugin/diagnostics.cpp)) | Child writing into an inherited HMI descriptor |
| Spawn failure is inert | `rc != 0` returns without setting state ([`diagnostics.cpp:209`](../reference/example-plugin/diagnostics.cpp)) | A half-armed poll with no child |

---

## 3. Memory & ownership rules

These are the four ownership facts you must internalize. Three are about objects you pass to the framework; one is about the object the framework runs for you.

### 3.1 `updateModel()` deep-copies the DataTable — so your table is *yours* to free

`updateModel(unsigned int model, const DataTableBase& t)` takes the table **by const reference and makes its own deep copy** — a behavior **reconstructed** empirically across RE stages (see below), not read from OEM source. The framework does **not** retain your pointer. This was the single most consequential thing to pin down during RE, and the reference tree records the whole investigation:

- **Early belief (stack RAII):** an early stage built a `bmw::DataTable<1>` **on the stack**, called `updateModel(50u, table)`, and let the destructor `clear()` the column `Variant`s on scope exit — comment: *"the framework kept its own copy."* This works, and is the leanest option when the whole table is built in one function.
- **Defensive stage (heap, never freed):** a later stage hedged against the *opposite* possibility — that `updateModel` might store a reference/shallow copy — by heap-allocating the table once and **never** freeing it, so a dangling pointer was impossible.
- **Resolved (deep copy confirmed by behavior):** the resolved semantics — *"A fresh table each refresh; deep-copied by updateModel (per ABI RE), so the old one can be dropped."* The mature plugin then heap-allocates a **fresh** `DataTable` on every refresh and simply lets it leak, because refreshes are user-driven and rare:

```cpp
void MyApp::fill(unsigned model, const char* path, const char* hint) {
    bmw::DataTable<1>* t = new bmw::DataTable<1>();   // deep-copied by updateModel
    // ... populate rows ...
    updateModel(model, *t);                           // framework copies; *t now droppable
    // NOTE: *t is intentionally not deleted here -> a tiny, bounded, user-paced leak.
}
```
*(from [`diagnostics.cpp:118-136`](../reference/example-plugin/diagnostics.cpp))*

**Practical guidance for your plugin:** either build the table on the **stack** and let RAII free it after `updateModel` returns (§ `diagnostics2` — the clean choice), or heap-allocate and delete it yourself right after the call. Do **not** keep a heap table alive expecting the framework to read from it later — it won't; it already copied. The reference's deliberate per-refresh leak is acceptable *only* because refreshes are rare and user-triggered; a poller that refreshed every 400 ms for hours should free its table (stack RAII makes this automatic). Note that the stack-RAII posture is the **safe-either-way** choice: it is leak-free whether the framework deep-copies or (contrary to the RE) shallow-copies, because you keep your originals alive until `updateModel` returns.

### 3.2 `Runnable` ownership — the framework never frees it

From the interface contract ([`bmw_list.h`](../reference/sdk/bmw_list.h)): *"Framework never frees it: a one-shot must `delete this` at the END of `run()`; a rescheduling one reposts (`post(this,ms)`) and returns without deleting."* That is exactly what `ChildPoller::run()` does — repost-and-return while the child lives, `delete this` on the terminal tick ([`diagnostics.cpp:355-357`](../reference/example-plugin/diagnostics.cpp)).

| Runnable kind | Who frees it | When |
|---|---|---|
| One-shot | itself | `delete this;` as the last statement of `run()` |
| Self-rescheduling | itself | `delete this;` only on the tick that stops rescheduling |
| Posted but never run (see §6) | *nobody* | leaked — avoid by not posting on a dying app |

A subtle ABI point that makes the self-freeing `Runnable` link at all (**carve-confirmed**): the OEM libs export `Runnable`'s `D1`/`D0` destructors as **weak** — `_ZN3bmw8RunnableD1Ev` and `_ZN3bmw8RunnableD0Ev` show as `W` in **both** `libAppFramework.A.so` and `libCoreFramework.A.so` (`nm -D`) — but **not** the base-object `D2` (no `_ZN3bmw8RunnableD2Ev` is exported anywhere). Defining an inline `virtual ~Runnable() {}` in the header emits a local weak `D2/D1/D0` so `dlopen(RTLD_NOW)` resolves your derived destructor ([`bmw_list.h`](../reference/sdk/bmw_list.h)). If you write your own runnable, keep that inline empty destructor.

### 3.3 `Parcel` copy is hidden on purpose

`Parcel` is a 20-byte serialization buffer `{buf*, size, cap, vptr, pos}` whose copy-ctor and `operator=` are **declared private and left undefined** — because a default copy would shallow-copy `buf@0` and lead to a double free ([`bmw_list.h`](../reference/sdk/bmw_list.h)). Handlers receive `const bmw::Parcel&`; **read from it, never copy or store it**. If you need a value out of it, pull it immediately with `readInt32()` / `readUInt32()` / `readBool()` and keep the scalar:

```cpp
bool MyApp::onSvtRow(const bmw::Parcel& p) {
    int i = -1;
    if (!p.readInt32(i)) { unsigned u = 0; if (p.readUInt32(u)) i = (int)u; }
    if (i >= 0 && i < ngroups_) { selected_ = i; refresh_detail(); }
    return true;
}
```
*(from [`diagnostics.cpp:290-296`](../reference/example-plugin/diagnostics.cpp); note the defensive int-then-uint fallback for field-order robustness)*

To *send* a bool (e.g. to `setProperty`), construct a fresh `Parcel(bool)` locally and pass it by const-ref; let it die with the statement ([`diagnostics.cpp:194-197`](../reference/example-plugin/diagnostics.cpp)).

### 3.4 `Variant` cell ownership inside a DataTable

A table cell is a `Variant` whose `m_impl` points to a heap `ObjectContainer<T>` you `new` ([`diagnostics.cpp:113-116`](../reference/example-plugin/diagnostics.cpp); container template at [`bmw_list.h`](../reference/sdk/bmw_list.h)). You allocate it; the table owns it thereafter. `DataTable<N>::~DataTable()` calls `clear()`, which frees the column `Map`s and their `Variant`s ([`bmw_list.h`](../reference/sdk/bmw_list.h); `DataTableBase::clear()` is a real export, `0xaa90 T` in `libCoreFramework.A.so`). So the ownership chain is:

> **you `new` the container → you hand the `DataTable` to `updateModel` (which deep-copies) → your `DataTable`'s destructor frees your originals.**

The deep copy is understood — *per the reconstructed `Variant`/`ObjectContainer` model* ([`bmw_list.h`](../reference/sdk/bmw_list.h)) — to proceed by cloning each container through the polymorphic `IObjectContainer::clone()` hook (`clone()` returns `new ObjectContainer<T>(m_val)` in the reconstructed inline template). Treat the per-cell `clone()` **mechanism** as reconstructed-header inference: `clone()` is a hand-reconstructed inline in the SDK header, and the real `updateModel` body lives in the stripped lib, so the copy is behaviorally confirmed but its exact internal path is not carve-provable. Practically it does not matter: you never manually free a `Variant` you placed in a table; freeing the table frees them. (This is why the stack-RAII table of §3.1 is leak-free and the heap table of §3.1 leaks unless you delete it.)

---

## 4. Defensive design that made the example safe by construction

These are not incidental — each one closes a specific failure mode, and together they mean the reference plugin *cannot* misbehave in the ways an in-process extension usually does.

1. **No work on boot.** `onInit()` only paints hints and registers handlers — it never spawns a scan ([`diagnostics.cpp:323-349`](../reference/example-plugin/diagnostics.cpp); comment *"DTC hint (no scan on boot)"* at line 325). If your plugin auto-runs heavy work in `onInit`, every HMI boot pays that cost and any bug is a boot-time UI hazard. Do work **only** in response to a button press.

2. **Distinct component / action / model ids.** All ids are a single flat `enum` with no collisions ([`diagnostics.cpp:36-54`](../reference/example-plugin/diagnostics.cpp)), and they match the DescFile 1:1 ([`Diagnostics.xml`](../reference/example-plugin/Diagnostics.xml)). A duplicated id silently routes an event to the wrong handler or model — a class of bug that is invisible until it fires on-car.

3. **Grey out, don't remove.** A control that must be temporarily unavailable is disabled via the `SELECTABLE` property (id `2`) — `setProperty(comp, 2, Parcel(false))` — never deleted from the tree ([`diagnostics.cpp:194-197`](../reference/example-plugin/diagnostics.cpp); `PROP_SELECTABLE=2` in the enum at `diagnostics12.cpp:40`, XML default states at [`Diagnostics.xml:60-69`](../reference/example-plugin/Diagnostics.xml)). The "Read" button ships greyed and only un-greys once its prerequisite exists ([`diagnostics.cpp:315-318`](../reference/example-plugin/diagnostics.cpp)). Removing/re-adding components at runtime risks dangling focus targets; toggling `SELECTABLE` keeps the layout stable. (See [**04 — Menus, screens & layout**](04-menus-screens-and-layout.md) for the property-id catalog and [**03 — DescFile / XML reference**](03-descfile-xml-reference.md) for the XML default states.)

4. **Validate before you trust a result.** Every read checks the output file is non-empty before parsing (`file_nonempty()` / `file_size()` at [`diagnostics.cpp:59-60`](../reference/example-plugin/diagnostics.cpp)), and the list is **never** left empty — an empty result falls back to a hint row (*"Working..."* / *"Press …"*) ([`diagnostics.cpp:134`](../reference/example-plugin/diagnostics.cpp)). An always-non-empty model matters: an earlier RE stage noted *"NEVER empty -> no re-entry crash."*

5. **Single-flight.** `if (scanning_) return;` guards every trigger ([`diagnostics.cpp:200`](../reference/example-plugin/diagnostics.cpp) `spawn_and_poll`, `:225` `onBuild`, `:236` `onRead`, `:245` `onReadSvt`), so a mashed button can't spawn overlapping children or two pollers.

---

## 5. Stability & rollback mindset

An RA plugin is **loose files in a directory** — nothing in the HMI binary changes. That makes the entire mechanism fully reversible and gives you a risk-free way to prove a load before you trust it with UI-affecting code.

- **Nothing patched.** The plugin is `<Name>.manifest` + `<Name>.xml` + `lib<Name>.so` dropped into the HMI's plugin directory; the loader discovers and `dlopen`s them. *(This was verified end-to-end on the author's OPT_DEBUG-enabled unit; a stock unit enforces no signature before it will `dlopen` an uncoded plugin (the loader links no crypto; confirmed on-car), so prove the load on your own unit first.)* Removing the directory and restarting the HMI restores the stock state exactly ([`08-building-and-deploying.md`](08-building-and-deploying.md): *"Plugin dir is loose files — fully reversible; nothing in the HMI binary changed"* at line 24).

- **Prove the load with a marker, not with UI code.** The stage-1 plugin's *entire* job is to prove discovery + `dlopen` + `create()` with **zero** UI risk. A library constructor writes a marker the instant the `.so` is mapped, and `create()` writes a second marker when the framework accepts the descriptor:

```cpp
__attribute__((constructor))
static void on_load() { marker("/tmp/myplugin_loaded", "so dlopened"); }   // fires on dlopen

static bmw::IPluginApp* my_create(/* ... */) {
    marker("/tmp/myplugin_created", "create called");                       // ABI accepted
    // ... construct a real bmw::PluginApp (its ctor installs the real vtable) ...
}
```
*(from [`hello_plugin_stage1.cpp:14-35`](../reference/example-plugin/hello_plugin_stage1.cpp))*

  On a system where `/tmp` is RAM-backed, you check `ls -l /tmp/myplugin_loaded` / `_created` over ssh while the HMI runs — a green load with **no** custom code touching the model yet ([`08-building-and-deploying.md`](08-building-and-deploying.md)). Only after that passes do you graduate to a plugin that calls `updateModel` / `setProperty`. *(The `/tmp`-is-RAM marker technique and the 400 ms poll interval are properties of a particular head-unit environment; verify a RAM-backed scratch path and your own timing on your unit.)*

- **Roll back in one line.** `rm -rf <pluginDir>/<Name> ; sync ; restart HMI` ([`08-building-and-deploying.md`](08-building-and-deploying.md)). Because you never edited the HMI binary, there is nothing else to undo. Keep a stage-1 marker build around as a bisection tool: if a fuller plugin misbehaves, dropping back to the marker-only `.so` tells you instantly whether the problem is load/ABI or your own logic.

> The stage-1 `destroy()` deliberately **leaks** the app object (*"intentionally leak (proper dtor is stage-2)"*, [`hello_plugin_stage1.cpp:38-39`](../reference/example-plugin/hello_plugin_stage1.cpp)) — acceptable for a load-proof throwaway, **not** for a shipping plugin, which should `delete app;` in `destroy()` as the mature reference does ([`diagnostics.cpp:369`](../reference/example-plugin/diagnostics.cpp)).

---

## 6. Teardown hazard (know this before you ship)

The one place the reference design is **not** provably safe is teardown while a scan is in flight. `onFinalize()` in the reference simply `return true;` — it does **not** reap the child or cancel the poller ([`diagnostics.cpp:350`](../reference/example-plugin/diagnostics.cpp)). If the framework destroys the `PluginApp` while a `ChildPoller` is still queued, the next tick dereferences a freed `app_` (`app_->on_poll_running()`), a classic use-after-free.

**`onInit`/`onFinalize` are not the whole lifecycle.** The reconstructed `PluginApp` vtable ([`bmw_list.h`](../reference/sdk/bmw_list.h)) exposes six earlier lifecycle virtuals — `start()` (slot 2), `stop()` (3), `activate()` (4), `deactivate()` (5), `init()` (6), `finalize()` (7) — in addition to `onInit()` (22) and `onFinalize()` (23):

| Slot | Method | Likely role |
|---|---|---|
| 2 | `start()` | app started by the loader |
| 3 | `stop()` | app stopped (candidate cancellation hook) |
| 4 | `activate()` | app/screen brought to foreground |
| 5 | `deactivate()` | app/screen backgrounded (candidate pause hook) |
| 6 | `init()` | framework-level init (precedes `onInit`) |
| 7 | `finalize()` | framework-level finalize |
| 22 | `onInit()` | plugin-facing init (paint hints, register handlers) |
| 23 | `onFinalize()` | plugin-facing finalize |

A dynamically-unloaded or deactivated plugin most likely transits `deactivate()`/`stop()`/`finalize()` **before (or instead of)** `onFinalize()`. If your plugin can be torn down or backgrounded dynamically, hook your cancellation there as well, not only in `onFinalize()`. *(Slot roles above are reconstructed from the header's slot order; their exact semantics are not carve-proven.)*

In practice the reference is mitigated by three things — the app is `autoStart` and effectively process-lifetime ([`Diagnostics.manifest:7`](../reference/example-plugin/Diagnostics.manifest): `<autoStart>yes</autoStart>`); scans are short and user-paced; and finalize during an active scan was not observed on the author's OPT_DEBUG-enabled unit. But if your plugin can be torn down dynamically, **do not** rely on that. The framework exports a cancel primitive — `bmw::PluginAppHandler::stop(bmw::Runnable*)` @ `0xa8c8` (`nm -DC libAppFramework.A.so`, carve-confirmed) — which is the intended lever: in a teardown/deactivate hook, `stop()` the pending poller (or set a "dying" flag the poller checks before touching `app_`) and reap or kill the child. Whether `stop()` is *sufficient* for safe teardown — and whether the dispatcher drains or drops pending `Runnable`s on app destroy — is **untested** in the reference tree; the symbol's existence is confirmed but its behavior is an open question. Treat wiring it up as required work for any dynamically-unloaded plugin.

---

## 7. Best-practices checklist

Copyable rules, each traceable to a source above:

- [ ] **Never block the UI thread** — no sync I/O, `sleep`, or blocking `waitpid` in `onInit`, handlers, or `run()` (§1).
- [ ] **Do blocking work in a `posix_spawn` child**, stdio → `/dev/null`, address space isolated (§2.2).
- [ ] **Poll the child from the UI thread** with a self-rescheduling `Runnable` + `waitpid(WNOHANG)` + `post(this, ms)` (§2.1).
- [ ] **One-shot `Runnable`s `delete this` at the end of `run()`**; rescheduling ones `delete this` only on the terminal tick (§3.2).
- [ ] **Update models/properties only on the UI thread** — i.e. only from `onInit`/handlers/`run()` (§1).
- [ ] **Prefer a stack `DataTable`** (RAII frees it, and it is safe-either-way) or delete your heap table right after `updateModel` — the framework deep-copies (§3.1).
- [ ] **Never keep, copy, or store a `Parcel`** — read scalars out immediately (§3.3).
- [ ] **Never leave a model empty** — always emit ≥1 row/hint (§4.4).
- [ ] **Single-flight every trigger** with a `scanning_`/busy guard (§4.5).
- [ ] **Grey via `SELECTABLE`, never remove components** at runtime (§4.3).
- [ ] **Do no heavy work in `onInit`** — only on explicit user action (§4.1).
- [ ] **Keep all ids distinct** and matched 1:1 with the DescFile (§4.2; see [**03 — DescFile / XML reference**](03-descfile-xml-reference.md)).
- [ ] **Validate output (marker/non-empty) before trusting it** (§4.4, §5).
- [ ] **Prove the load with a stage-1 marker `.so`** before shipping UI code (§5).
- [ ] **Handle teardown** — `stop()` the poller and reap the child in a teardown/deactivate hook (`onFinalize`, and consider `deactivate()`/`stop()`) if your plugin can be unloaded dynamically (§6).
- [ ] **Keep a one-line rollback** ready; never patch the HMI binary (§5).

---

### Cross-references
- [**03 — DescFile / XML reference**](03-descfile-xml-reference.md) — the `raAction`/action and property *declarations* (the XML default states referenced from §4.2/§4.3).
- [**04 — Menus, screens & layout**](04-menus-screens-and-layout.md) — the property-id catalog (`SELECTABLE`, positions, etc.).
- [**05 — C++ ABI & data types**](05-cxx-abi-and-data-types.md) — the `PluginApp` 34-slot vtable, `Runnable`, `Delegate`, and the `DataTable`/`Variant`/`Parcel` types, with the reconstructed-header caveats.
- [**06 — Runtime API reference**](06-runtime-api-reference.md) — the `updateModel`/`setProperty`/`addHandler`/`post` callables and the `Delegate` wiring referenced from `onInit`.
- [**08 — Building & deploying**](08-building-and-deploying.md) — the QNX/ARM cross-build (`ntoarm-g++`) and the deploy/validate/rollback loop summarized in §5.

---

### Sources

These facts were reverse-engineered from an **owner-authorized offline flash carve** of the author's own titled vehicle and verified end-to-end on that same head unit — the author's **OPT_DEBUG-enabled** unit. Primary sources are the reference plugin tree ([`reference/example-plugin/`](../reference/example-plugin/): `diagnostics.cpp`, `hello_plugin_stage1.cpp`, `Diagnostics.xml`, `Diagnostics.manifest`; headers in [`reference/sdk/`](../reference/sdk/)) and the carved OEM framework libraries (`libAppFramework.A.so`, `libCoreFramework.A.so` from your own HMI carve), inspected with `nm -DC`.

**Verified vs. reconstructed:** framework **symbol names and addresses** (e.g. `post` @ `0xa804`/`0xa790`, `dispatch()` @ `0xa5cc`, `stop(Runnable*)` @ `0xa8c8`, `updateModel(…DataTableBase const&)` @ `0x539c`, `setProperty` @ `0x54a4`, the weak `Runnable` `D1`/`D0` with no `D2`) are carve-confirmed. The `bmw_abi.h` / `bmw_list.h` **SDK headers are hand-reconstructed** from disassembly ([`bmw_list.h`](../reference/sdk/bmw_list.h) banner); accordingly the **single-thread guarantee**, the **`updateModel` deep-copy** and its per-cell `clone()` path, the **"framework never frees your `Runnable`"** contract, the **vtable slot roles**, and the **dispatcher scheduling of a delayed `post`** are reconstructed inferences — marked as such inline where they appear. This SDK doc intentionally omits the author's car-specific details (on-HU scanner binary path, gateway address, VIN) and presents only the generic plugin mechanics, with `WORKER_BIN` / `RESULT_FILE` placeholders in place of the author's private app paths.
