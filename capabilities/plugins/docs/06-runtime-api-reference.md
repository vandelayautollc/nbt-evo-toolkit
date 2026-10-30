# 06 — Runtime API Reference (Available Function Calls)

*A carve-grounded catalog of the NBT-Evo HMI RA-plugin runtime surface: the 34-slot `bmw::PluginApp` vtable of callbacks the framework invokes on you (in practice you override only `onInit`/`onFinalize`), and the non-virtual helpers you call back — `updateModel`, `addHandler`, `setProperty`, `post` — all wired to DescFile `raAction`/model ids and confined to the single UI thread.*

> **Scope & authorization.** This document describes the C++ runtime surface of the NBT-Evo HMI **RA plugin** framework (`bmw::PluginApp`), reverse-engineered from an offline flash carve and owner-authorized work on the author's **own** titled vehicle. It presents the plugin *mechanics* generically, for a developer building a menu app for **their own** head unit. It is a companion to the manifest/DescFile docs — the numeric identifiers used here (`raAction` ids, model ids, component ids) are declared in your `<Name>.xml` DescFile; see the DescFile reference for how they are defined, and the Data Structures reference for the `Parcel`/`Variant`/`DataTable` payload types threaded through these calls.

This is the "what can I call, and what gets called on me" reference. There are exactly two directions of traffic across the plugin boundary:

- **(A) Callbacks the framework invokes on you** — virtual methods of `bmw::PluginApp` you may override. The framework owns the calling; you supply behavior.
- **(B) Methods you call on `bmw::PluginApp`** — non-virtual (framework-provided) helpers you invoke to push data into the UI, bind handlers, change properties, and schedule work.

Everything below runs on **one thread**: the HMI UI / dispatcher thread. There is no framework-provided worker thread. Keep every callback and every helper call short and non-blocking; offload real work to a child process and poll it with a rescheduling `Runnable` (summarized in [§4](#4-threading-model--the-one-rule); the full treatment is in `07-threading-and-safety-model.md`).

---

## 0. Cheat sheet

| Call | Direction | Purpose | Thread | Declared where |
|---|---|---|---|---|
| `onInit()` | framework → you | one-time setup: seed models, register handlers | UI | override (slot 22) |
| `onFinalize()` | framework → you | one-time teardown | UI | override (slot 23) |
| `onCheckAppAvailable()` | framework → you | gate whether the menu entry is offered | UI | override (slot 25), optional; OEM-used |
| `onError(code, msg)` | framework → you | framework-reported error notification | UI | override (slot 21), optional; OEM-used |
| `handleEvent(state, event, Parcel)` | framework → you | low-level UI event (below `raAction`) | UI | override (slot 18), rare |
| `updateModel(model, DataTableBase&)` | you → framework | push a list/table into a `raListModel` | **UI only** | `bmw_list.h:150` |
| `updateModel(model, BasicString<char>&)` | you → framework | push a string into a `raDataModel` | **UI only** | `bmw_list.h:151` |
| `updateModel(model, TextID&)` | you → framework | push a localized text-id into a model | **UI only** | `bmw_list.h:152` |
| `addHandler(action, Delegate)` | you → framework | bind a `raAction` to a member fn (global) | UI (do it in `onInit`) | `bmw_list.h:153` |
| `addHandler(state, action, Delegate)` | you → framework | bind a `raAction` scoped to one `hmiState` | UI (do it in `onInit`) | `bmw_list.h:154` |
| `setProperty(comp, prop, Parcel&)` | you → framework | change a component property at runtime (grey/un-grey, geometry) | **UI only** | `bmw_list.h:156` |
| `post(Runnable*)` | you → framework | run a `Runnable` on the next UI dispatch cycle | any → UI | `bmw_list.h:168` |
| `post(Runnable*, ms)` | you → framework | run a `Runnable` after `ms` on the UI thread | any → UI | `bmw_list.h:169` |

All symbols above are exported by `libAppFramework.A.so` and resolved when the HMI `dlopen()`s your `.so`. The reconstructed declarations live in [`capabilities/plugins/reference/sdk/bmw_list.h`](../reference/sdk/bmw_list.h); the fullest real usage is [`capabilities/plugins/reference/example-plugin/hello_plugin_stage1.cpp`](../reference/example-plugin/diagnostics.cpp).

> **VERIFIED vs RECONSTRUCTED.** The *symbols and signatures* in this doc are carve-confirmed: read directly out of `libAppFramework.A.so` with `nm -DC`, matching the imports of both the example plugin and the OEM `libSecurityMenu.so`. The **vtable slot numbers** (e.g. `onInit=22`, `onFinalize=23`) are reconstructed in `bmw_list.h` **and independently spot-confirmed** from the real subclass vtable in `libDiagnostics12.so` (vtable @ `0x56cc`; slot relocations give slot 2 = `PluginApp::start()`, slot 10 = `post(Runnable*)`, slot 21 = `onError`, slot 22 = `onInit`, slot 23 = `onFinalize`, slot 25 = `onCheckAppAvailable`). The **class layout** in `bmw_list.h` (field offsets, and the internals of `Parcel`/`Variant`/`Map`/`DataTable`) is **hand-reconstructed** from disassembly and is the part most likely to shift on a different firmware build. Where a claim rests on reconstruction rather than an exported symbol, it is called out inline.

---

## A. Callbacks the framework invokes on you

Your plugin class derives from `bmw::PluginApp`. The base class has a **34-slot primary vtable** ([`bmw_list.h–191`](../reference/sdk/bmw_list.h)). The compiler emits a vtable for *your* subclass in which every slot you do not override points back at the framework's base implementation — which is why a plugin's `.so` lists `start`, `stop`, `activate`, `handleEvent`, `invokeCommand`, etc. as **undefined imports** even when you never wrote them: those slots are filled by the linker from `libAppFramework.A.so` at `dlopen` time. Confirmed: `nm -DC libDiagnostics12.so` shows `U bmw::PluginApp::start()`, `U bmw::PluginApp::handleEvent(...)`, `U bmw::PluginApp::invokeCommand(...)`, `U ...getName() const`, etc., although the source overrides only `onInit`/`onFinalize`.

**The practical reality first.** A real OEM plugin overrides almost nothing. The top-level class of the OEM `libSecurityMenu.so` overrides exactly **four** `bmw::PluginApp` virtuals — **`onInit()` (slot 22), `onFinalize()` (slot 23), `onError()` (slot 21), and `onCheckAppAvailable()` (slot 25)** — and additionally defines its own non-virtual helpers (`cdsReceive(...)`, several `loadImage(...)` overloads) plus the static `create`/`destroy` factory pair required by the loader. (`nm -DC libSecurityMenu.so`: `SecurityMenu::onInit` @0x14d14, `onFinalize` @0x14c08, `onError` @0x14c9c, `onCheckAppAvailable` @0x149a8 are the only defined vtable-override text symbols.) The example plugin is leaner still — it overrides only `onInit`/`onFinalize` ([`diagnostics.cpp:84–85`](../reference/example-plugin/diagnostics.cpp), and their definitions at `:323` and `:350`). **You almost certainly only need `onInit`/`onFinalize`** — reach for `onCheckAppAvailable` and `onError` only when you need conditional visibility or framework-error logging. Everything else in this section is documented so you know the seam exists.

### The full vtable (slot order is part of the ABI)

| Slot | Signature | Group | Return meaning | Overridden in the wild? |
|---|---|---|---|---|
| 0/1 | `~PluginApp()` | dtor | — | via subclass dtor |
| 2 | `bool start()` | lifecycle | proceed? | no (base) |
| 3 | `bool stop()` | lifecycle | proceed? | no (base) |
| 4 | `bool activate()` | lifecycle | proceed? | no (base) |
| 5 | `bool deactivate()` | lifecycle | proceed? | no (base) |
| 6 | `bool init()` | lifecycle | success? | no (base) |
| 7 | `bool finalize()` | lifecycle | success? | no (base) |
| 8 | `void post(const Message&)` | scheduling | — | **call, don't override** |
| 9 | `void post(const Message&, unsigned)` | scheduling | — | **call, don't override** |
| 10 | `void post(Runnable*)` | scheduling | — | **call, don't override** |
| 11 | `void post(Runnable*, unsigned)` | scheduling | — | **call, don't override** |
| 12 | `bool getName() const` | info getter | name valid? | no (base returns ctor name) |
| 13 | `bool getResourceFile(ResourceTypes) const` | info getter | present? | no (base) |
| 14 | `bool getVersion(uint&, uint&, uint&) const` | info getter | valid? | no (base returns ctor version) |
| 15 | `bool getRhmiVersion(RHMIInterfaceVersion&) const` | info getter | valid? | no (base returns ctor rhmi) |
| 16 | `bool invokeCommand(uint, const Parcel&)` | event/command | handled? | no (base) |
| 17 | `bool updateModel(uint, const Parcel&, uchar)` | event/command | handled? | no — **inbound; not the outbound `updateModel` you call** |
| 18 | `bool handleEvent(uint state, uint event, const Parcel&)` | event/command | handled? | rare |
| 19 | `bool invokeDataUpdate(uint, const Parcel&)` | event/command | handled? | no (base) |
| 20 | `bool requestDataValue(uint)` | event/command | handled? | no (base) |
| 21 | `bool onError(uint, const BasicString<char>&)` | misc | handled? | **OEM (SecurityMenu)** |
| 22 | `bool onInit()` | lifecycle | success (see note) | **YES** |
| 23 | `bool onFinalize()` | lifecycle | success? | **YES** |
| 24 | `bool getCapabilities(const std::string&)` | info getter | supported? | no (base) |
| 25 | `bool onCheckAppAvailable()` | lifecycle/gate | **true ⇒ entry shown** | **OEM (SecurityMenu)** |
| 26 | `bool handleMessage(const Message&)` | event/command | handled? | no (base) |
| 27 | `bool invokeCommandWithMap(uint, const Map<uint,Variant>&)` | event/command | handled? | no (base) |
| 28 | `bool updateModelWithMap(uint, const Map<uint,Variant>&)` | event/command | handled? | no (base) |
| 29 | `bool handleEventWithMap(uint, uint, const Map<uint,Variant>&)` | event/command | handled? | no (base) |
| 30 | `bool invokeCDSUpdate(BasicString<char>&, BasicString<ushort>&)` | misc (CDS) | handled? | no (base) |
| 31 | `bool invokeVoiceStateChanged(ushort)` | misc (SDS) | handled? | no (base) |
| 32 | `bool invokeAppManagerUpdate(const BasicString<char>&)` | misc | handled? | no (base) |
| 33 | `bool invokeSdsEvent(uint, const Map<uint,Variant>&)` | misc (SDS) | handled? | no (base) |

Slot order is [`bmw_list.h–191`](../reference/sdk/bmw_list.h), spot-confirmed against the `libDiagnostics12.so` vtable relocations as noted above. The `WithMap` variants (27–29) and `Map<uint,Variant>` are the framework's richer key→`Variant` payload path; the non-`Map` variants pass a `Parcel`. Both `Delegate` payload shapes have matching `addHandler` binders — see [§B.2](#b2-addhandler--bind-a-raaction-to-a-member-function).

### A.1 Lifecycle

```cpp
virtual bool onInit();      // slot 22 — override this
virtual bool onFinalize();  // slot 23 — override this
```

- **`onInit()`** fires once, on the UI thread, after your object is constructed and its DescFile is parsed, before the entry is interactive. This is where you (1) seed initial model contents with `updateModel`, and (2) bind every `raAction` with `addHandler`. Return `true` on success. In the example it seeds both list models with hint text and registers all seven action handlers, then returns `true` ([`diagnostics.cpp:323–349`](../reference/example-plugin/diagnostics.cpp)).
- **`onFinalize()`** fires once at teardown; free anything you own and return `true` ([`diagnostics.cpp:350`](../reference/example-plugin/diagnostics.cpp)).
- **`start`/`stop`/`activate`/`deactivate`/`init`/`finalize` (slots 2–7)** are the framework's finer-grained lifecycle transitions. The base implementations are sufficient; neither the example nor the OEM `SecurityMenu` overrides them. Treat `onInit`/`onFinalize` as your real hooks.

> **Return-value note (inference).** The examples always `return true` from `onInit`, and a `bool` return plainly signals success/failure — but the exact consequence of returning `false` from `onInit` (does the load abort cleanly? is the entry hidden?) is **not tested in the carve**. Treat `onInit`→`true` as the contract; do not rely on a specific failure path for `false`. Only `onInit`'s success convention and `onCheckAppAvailable`'s gating are directly observed; the other slots' "proceed?/handled?" return meanings are reasonable inference from their `bool` return types, not proven per slot.

> **Naming trap.** `onInit`/`onFinalize` (slots 22/23) are the plugin-author hooks. `init`/`finalize` (slots 6/7) are internal framework transitions. Override the `on*` pair.

### A.2 Events & commands

```cpp
virtual bool handleEvent(unsigned state, unsigned event, const Parcel&);           // slot 18
virtual bool invokeCommand(unsigned cmd, const Parcel&);                           // slot 16
virtual bool invokeDataUpdate(unsigned model, const Parcel&);                      // slot 19
virtual bool requestDataValue(unsigned model);                                     // slot 20
virtual bool updateModel(unsigned, const Parcel&, unsigned char);                  // slot 17 (VIRTUAL — inbound)
virtual bool invokeCommandWithMap(unsigned, const Map<unsigned,Variant>&);         // slot 27
virtual bool updateModelWithMap(unsigned, const Map<unsigned,Variant>&);           // slot 28
virtual bool handleEventWithMap(unsigned, unsigned, const Map<unsigned,Variant>&); // slot 29
virtual bool handleMessage(const Message&);                                        // slot 26
```

These are the framework's raw input channels. **You normally do not touch any of them** — the whole point of the DescFile `raAction` + `addHandler` mechanism (below) is that the framework routes UI presses to *your named member functions* without you overriding `handleEvent`. Override `handleEvent`/`invokeCommand` only if you need events the DescFile action model doesn't expose. Return `true` when you have consumed the event, `false` to let the framework fall through. Neither the example nor the OEM `SecurityMenu` overrides any of them.

> Slot 17 `updateModel(unsigned, const Parcel&, unsigned char)` is a **virtual, inbound** callback and is a different method from the non-virtual outbound `updateModel(model, DataTableBase&)` you call in [§B.1](#b1-updatemodel--push-data-into-a-model). Same name, opposite direction; C++ overload/vtable rules keep them distinct (mangled `_ZN3bmw9PluginApp11updateModelEjRKNS_6ParcelEh` @0x5a18 vs `..._ZN3bmw9PluginApp11updateModelEjRKNS_13DataTableBaseE` @0x539c).

> When the framework selects the `*WithMap` (`Map<uint,Variant>`) inbound path versus the flat `Parcel` path for the same interaction is **not established** by any inspected source; both binder families exist, but the example only exercises the `Parcel` path.

**State events (ON-CAR, VAE Powertools 1.4.x).** The HMI calls `handleEventWithMap(state, event, map)` whenever one of your DescFile's states changes, `hmiState` and `popupHmiState` alike:

| `event` | Meaning | Map key | Value |
|---|---|---|---|
| `11` | visibility | `23` | `bool` visible |
| `1` | focus | `4` | `bool` focused |

Opening a popup gives `11 {23: true}` and then `1 {4: true}` within 0.1 s. Closing it gives `1 {4: false}` and then `11 {23: false}`. Entering a menu page gives the same kind of events for its state; a page that becomes visible as the focused button's preview gets `11` without `1`. At load the HMI also sends `state 0` events `3` and `12`, with neither key.

Subscribe per state with the state-scoped binder, as OEM ActiveSeating does for its screens (`libActiveSeating.so` 0xd7f8, 0xd81c):

```cpp
void addHandlerWithMap(unsigned state, unsigned event,
                       const Delegate<bool, const Map<unsigned, Variant>&>& d);  // _ZN3bmw9PluginApp17addHandlerWithMapEjjRKNS_8DelegateIbRKNS_3MapIjNS_7VariantEEEvvvEE

bool MyApp::onPopupVisible(const bmw::Map<unsigned, bmw::Variant>& m) {
    const bmw::Variant* v = m.find(23);                       // bmw_list.h: the OEM's inline lookup
    bool visible = v && v->m_impl && reinterpret_cast<const unsigned char*>(v->m_impl)[4];
    ...
}
```

To log every event, override `handleEventWithMap` and call `bmw::PluginApp::handleEventWithMap` after; the base dispatches to the bound handlers. Don't use `%` in plugin code: g++ 4.4.2 compiles it to a call to `__umodsi3`, which the head unit's libc doesn't export, so the plugin would fail to load (`Map::find` uses a long division instead).

### A.3 Info getters

```cpp
virtual bool getName() const;                                   // slot 12
virtual bool getVersion(unsigned&, unsigned&, unsigned&) const; // slot 14
virtual bool getRhmiVersion(RHMIInterfaceVersion&) const;       // slot 15
virtual bool getResourceFile(ResourceType::ResourceTypes) const;// slot 13
virtual bool getCapabilities(const std::string&);               // slot 24
virtual bool onCheckAppAvailable();                             // slot 25
```

- **`getName` / `getVersion` / `getRhmiVersion`** are answered by the base class from the values you pass to the `PluginApp` **constructor** (name, `major`, `minor`, `RHMIInterfaceVersion`). Do **not** override these — supply them once at construction ([`diagnostics.cpp:365–367`](../reference/example-plugin/diagnostics.cpp) passes `name`, `1u`, `0u`, `rhmi=1`). Confirmed: OEM `SecurityMenu` defines no `getName`/`getVersion`/`getRhmiVersion` override, so it inherits the ctor-backed base implementation.
- **`getCapabilities(const std::string&)`** — capability negotiation; the base default is fine. (Its `std::string` parameter is the one place the ABI touches libstdc++ — mangling `...RKSs`; note the `#include <string>` in [`bmw_list.h`](../reference/sdk/bmw_list.h).)
- **`onCheckAppAvailable()`** (slot 25) — return `true` to have the menu entry offered, `false` to hide it. This is a hook OEM plugins actually use (`SecurityMenu::onCheckAppAvailable` is a defined symbol). Override it if your app should only appear under some condition; otherwise the base default offers it. Note: whether a `false` behaves differently at boot versus at runtime is not tested in the carve.

### A.4 Misc / subsystem events

```cpp
virtual bool onError(unsigned code, const BasicString<char>& msg);              // slot 21
virtual bool invokeCDSUpdate(BasicString<char>&, BasicString<unsigned short>&); // slot 30 (Car Data Service)
virtual bool invokeVoiceStateChanged(unsigned short);                          // slot 31 (speech)
virtual bool invokeAppManagerUpdate(const BasicString<char>&);                 // slot 32
virtual bool invokeSdsEvent(unsigned, const Map<unsigned,Variant>&);           // slot 33 (Speech Dialog System)
```

Subsystem notification hooks.

- **`onError` (slot 21)** is an **OEM-exercised hook**: the OEM `SecurityMenu` overrides it (`SecurityMenu::onError(unsigned int, bmw::BasicString<char> const&)` @0x14c9c is a defined `T` symbol) — the example plugin does not. Override it to react to (or log) framework-reported errors, keyed by `code` with a human-readable `msg`.
- **CDS/SDS/AppManager hooks (slots 30–33)** are for plugins that integrate with the car-data bus or the speech dialog system; the base defaults ignore them, and **neither the example nor `SecurityMenu` overrides any of them**.

> A related outbound helper exists: `bmw::PluginApp::cdsSetPropertyAsync(BasicString<char>&, BasicString<ushort>&, const uchar*, uint)` (exported from `libAppFramework.A.so` @0x554c) is a real CDS async-property call you can invoke. Its exact usage is not established by any inspected source and it is out of scope for a first plugin; it is noted here only so you know a CDS async-property path is available.

---

## B. Methods you call on `bmw::PluginApp`

These are the outbound calls. Each is a real exported symbol of `libAppFramework.A.so`. **Call all of them on the UI thread only** — in practice that means from `onInit`, from an `addHandler` callback, or from inside a `Runnable::run()` you posted (all three already run on the UI thread).

### B.1 `updateModel` — push data into a model

Push data into a DescFile model (`<raListModel>` / `<raDataModel>`) by numeric id. The framework re-renders the bound component. **`updateModel` deep-copies its argument** (reconstructed from the example's free-after-handoff idiom, not independently proven from a symbol), so you may — and the example does — build a heap `DataTable`, hand it over, and let it be freed.

```cpp
void updateModel(unsigned model, const DataTableBase& table);      // list/table model
void updateModel(unsigned model, const BasicString<char>& text);   // single string (e.g. a label's text)
void updateModel(unsigned model, const TextID& textId);            // localized text id
```

| Overload | Mangled symbol (`libAppFramework.A.so`) | Use for |
|---|---|---|
| `updateModel(uint, const DataTableBase&)` | `_ZN3bmw9PluginApp11updateModelEjRKNS_13DataTableBaseE` @0x539c | rows of a `raListModel` |
| `updateModel(uint, const BasicString<char>&)` | `_ZN3bmw9PluginApp11updateModelEjRKNS_11BasicStringIcEE` @0x529c | a text `raDataModel` |
| `updateModel(uint, const TextID&)` | `_ZN3bmw9PluginApp11updateModelEjRKNS_6TextIDE` @0x52dc | a localized string id |

The framework exports a **large** overload family over the same id space — `bool`, `char`, `uchar`, `short`, `ushort`, `int`, `unsigned`, `float`, `char const*`, `wchar_t const*`, `BasicString<char>`, `BasicString<unsigned short>` (UTF-16), `Image`, `ImageID`, `Date`, `Time`, `DateTime`, `TextID` — plus two windowed variants `updateModel(uint, DataTableBase const&, uint,uint,uint)` (@0x53bc) and `+3` more uints (@0x53f4) for partial/paged list updates (all present in `nm -DC libAppFramework.A.so`). Pick whichever matches the model's declared type in your DescFile.

**List example** — build a 1-column table of strings and push it to list model `50`:

```cpp
// A row is a Variant holding a BasicString<char>, stored at table cell (row, col).
static void add_row(bmw::DataTable<1>& t, unsigned r, const char* s) {
    bmw::Variant& c = t.at(r, 0);
    c.m_impl = new bmw::Variant::ObjectContainer<bmw::BasicString<char> >(
                   bmw::BasicString<char>(s));
}

void MyApp::fill_list(unsigned model, const char* lines[], unsigned n) {
    bmw::DataTable<1>* t = new bmw::DataTable<1>();   // deep-copied by updateModel
    for (unsigned i = 0; i < n; ++i) add_row(*t, i, lines[i]);
    updateModel(model, *t);                            // -> the <raListModel> re-renders
}
```

(Real usage: `add_row` [`diagnostics.cpp:113–116`](../reference/example-plugin/diagnostics.cpp); `fill` `:118–137`; `updateModel(model, *t)` `:135`.)

**String example** — drive a `Richtext` `raDataModel` (the right-hand detail pane in the example):

```cpp
char buf[4096];
/* ...compose buf... */
updateModel(DETAIL_MODEL, bmw::BasicString<char>(buf));   // cf. diagnostics12.cpp:188
```

A `label` shows one line of that, whatever the model (`03-descfile-xml-reference.md`, `label`).

**Multi-line text block** — fill a display-only `<list>` bound to `<raListModel modelType="Richtext">` with one row of one cell, the whole text (OEM ActiveSeating does this with a `TextID`; a `BasicString` works on the car too, in VAE Powertools 1.3.1):

```cpp
bmw::DataTable<1> table;                                   // deep-copied by updateModel
table.at(0, 0).m_impl = new bmw::Variant::ObjectContainer<bmw::BasicString<char> >(
                            bmw::BasicString<char>("First line\n   indented line\nLast line"));
updateModel(TEXT_MODEL, table);                            // wraps, and breaks at '\n'
```

> **Never push an empty list.** The example always seeds at least one hint row ([`diagnostics.cpp:134`](../reference/example-plugin/diagnostics.cpp), `:163`); an earlier RE stage recorded the reason in a comment — *"NEVER empty -> no re-entry crash"* — an empty model risks a re-entry crash. Seed models in `onInit` before the entry is interactive.

### B.2 `addHandler` — bind a `raAction` to a member function

Route a DescFile `<raAction id="N"/>` to one of your methods. Two overloads:

```cpp
void addHandler(unsigned action, const Delegate<bool, const Parcel&>& d);                 // global
void addHandler(unsigned state,  unsigned action, const Delegate<bool, const Parcel&>& d);// scoped to one hmiState
```

| Overload | Mangled symbol | Meaning |
|---|---|---|
| `addHandler(uint, Delegate)` | `_ZN3bmw9PluginApp10addHandlerEjRKNS_8DelegateIbRKNS_6ParcelEvvvEE` @0x5970 | action fires from any state |
| `addHandler(uint, uint, Delegate)` | `_ZN3bmw9PluginApp10addHandlerEjjRKNS_8DelegateIbRKNS_6ParcelEvvvEE` @0x5db0 | action fires only in `state` |

Both take a `Delegate<bool, const Parcel&>` — an 8-byte POD `{void* m_obj; bool(*m_exec)(void*, const Parcel&);}` ([`bmw_list.h–135`](../reference/sdk/bmw_list.h)). The `m_exec` thunk is generated per (class, method) by the template `Delegate::execImpl<C, &C::method>`, so the bound function's signature must be `bool C::method(const bmw::Parcel&)`.

**Binding pattern** (do this in `onInit`):

```cpp
bool MyApp::onBuild(const bmw::Parcel&);   // your handler, must return bool

bool MyApp::onInit() {
    bmw::Delegate<bool, const bmw::Parcel&> d;
    d.m_obj  = this;
    d.m_exec = &bmw::Delegate<bool, const bmw::Parcel&>
                   ::execImpl<MyApp, &MyApp::onBuild>;
    addHandler(BUILD_ACTION, d);           // BUILD_ACTION == <raAction id> in the DescFile
    /* ...bind the rest... */
    return true;
}
```

(Real usage: [`diagnostics.cpp:327–329`](../reference/example-plugin/diagnostics.cpp) for one handler; `:327–347` binds all seven; the `Delegate` template is [`bmw_list.h–135`](../reference/sdk/bmw_list.h).)

**Which form to use.** The OEM `libSecurityMenu.so` imports **both** forms — the 2-arg global (`_ZN3bmw9PluginApp10addHandlerEjRKNS_8DelegateIbRKNS_6ParcelEvvvEE`) and the 3-arg state-scoped (`_ZN3bmw9PluginApp10addHandlerEjjRKNS_8DelegateIbRKNS_6ParcelEvvvEE`). Use the **3-arg** form when the same action id appears in more than one `hmiState` and must mean different things per screen; use the **2-arg** form when action ids are globally unique (as in the example — its ids 21–27 are all distinct, so it uses the 2-arg form throughout).

There is also a `Map`-payload binder family — `addHandlerWithMap(uint[, uint], Delegate<bool, const Map<uint,Variant>&>)` (exported @0x5c98 for the 2-arg, @0x5f64 for the 3-arg) — pairing with the `*WithMap` inbound virtuals when you want key→`Variant` argument maps instead of a flat `Parcel`.

### B.3 `setProperty` — change a component property at runtime

Change a property of a component (declared by `id` in the DescFile) after load. The classic use is enabling/greying a button.

```cpp
void setProperty(unsigned component, unsigned prop, const Parcel& value);
```

Mangled: `_ZN3bmw9PluginApp11setPropertyEjjRKNS_6ParcelE` @0x54a4 ([`bmw_list.h`](../reference/sdk/bmw_list.h)).

`prop` is a property id; the value is carried in a `Parcel`. The verified idiom is the **`SELECTABLE` property (id `2`)** driven by a boolean `Parcel` to grey/un-grey a button:

```cpp
void MyApp::set_button(unsigned comp, bool enabled) {
    bmw::Parcel p(enabled);                 // explicit Parcel(bool) ctor writes the value
    setProperty(comp, /*SELECTABLE*/ 2u, p);
}
```

(Real usage: `set_button` [`diagnostics.cpp:194–197`](../reference/example-plugin/diagnostics.cpp); `PROP_SELECTABLE = 2` at `:41`; the DescFile can set the same property statically, e.g. `<property id="2" value="false"/>` to start a button greyed — see `Diagnostics.xml`.) Other property ids appear in DescFiles for geometry (`20`=POS_X, `21`=POS_Y, `9`=WIDTH, `10`=HEIGHT in `Diagnostics.xml`); those can likewise be driven at runtime through `setProperty`, though the example only exercises `SELECTABLE`. A `setPropertyWithMap` variant exists (@0x54c4) for `Map`-valued properties.

### B.4 `post` — schedule work on the UI thread

Hand a `bmw::Runnable*` to the dispatcher; its `run()` fires later **on the UI thread**.

```cpp
void post(Runnable* r);                 // next dispatch cycle
void post(Runnable* r, unsigned ms);    // after ms milliseconds
```

| Overload | Mangled symbol | Meaning |
|---|---|---|
| `post(Runnable*)` | `_ZN3bmw9PluginApp4postEPNS_8RunnableE` @0x6024 | run ASAP on the UI thread |
| `post(Runnable*, unsigned)` | `_ZN3bmw9PluginApp4postEPNS_8RunnableEj` @0x6010 | run after `ms` on the UI thread |

`post` is safe to call from any thread (it enqueues onto the dispatcher); the `Runnable` body then executes on the UI thread, so it is the sanctioned bridge from background work back to `updateModel`/`setProperty`. (In the reconstructed vtable `post` occupies slots 8–11; it is provided by the framework and *called*, never overridden. `PluginApp::post` forwards to `PluginAppHandler::post`, both exported; whether the effective dispatch is virtual or a direct forward is an ABI nuance that is not load-bearing for plugin authors.)

**Ownership rule (important — the framework never frees your `Runnable`):**

- A **one-shot** must `delete this` at the end of `run()`.
- A **self-rescheduling** poller re-posts itself (`post(this, ms)`) and returns *without* deleting; it deletes only on the terminal tick.

```cpp
// Self-rescheduling UI-thread poller: watches a child process without blocking.
class ChildPoller : public bmw::Runnable {
public:
    ChildPoller(MyApp* app, pid_t pid, unsigned ms) : app_(app), pid_(pid), ms_(ms) {}
    virtual ~ChildPoller() {}
    virtual void run() {
        int st = 0;
        if (::waitpid(pid_, &st, WNOHANG) == 0) {  // still running
            app_->on_poll_running();               // safe: we're on the UI thread
            app_->post(this, ms_);                 // re-arm; do NOT delete
            return;
        }
        app_->on_scan_done();
        delete this;                               // terminal tick: free ourselves
    }
private:
    MyApp* app_; pid_t pid_; unsigned ms_;
};

// kick it off after spawning the child:
post(new ChildPoller(this, pid, 400u), 400u);      // cf. diagnostics12.cpp:219
```

(Real usage: `ChildPoller` class [`diagnostics.cpp:67–74`](../reference/example-plugin/diagnostics.cpp); `run()` `:352–358`; the re-arm `app_->post(this, ms_)` `:355`; the initial `post(new ChildPoller(...), 400u)` `:219`. The `Runnable` base — root interface, `run()` at vtable slot 2, dtor emitted locally weak — is [`bmw_list.h–27`](../reference/sdk/bmw_list.h).)

---

## 2. The `Parcel` payload (what your handlers read, what `setProperty` writes)

`Parcel` is the flat serialization buffer threaded through **every** action handler (as `const Parcel&`) and **every** `setProperty` value. You only need a few members; the full accessor/producer catalog belongs to the Data Structures reference.

```cpp
class Parcel {                       // reconstructed layout: 20 bytes, 4-aligned
public:
    Parcel();                        // _ZN3bmw6ParcelC1Ev        — empty buffer
    explicit Parcel(bool);           // _ZN3bmw6ParcelC1Eb        — writes one bool (used by setProperty)
    ~Parcel();                       // _ZN3bmw6ParcelD1Ev        — frees the buffer
    bool readInt32 (int&)          const;  // _ZNK3bmw6Parcel9readInt32ERi
    bool readUInt32(unsigned int&) const;  // _ZNK3bmw6Parcel10readUInt32ERj
    bool readBool  (bool&)         const;  // _ZNK3bmw6Parcel8readBoolERb
private:
    Parcel(const Parcel&);           // deleted on purpose — would shallow-copy the buffer
    Parcel& operator=(const Parcel&);
};
```

| Member | Direction | Typical use |
|---|---|---|
| `Parcel()` | construct | an empty parcel |
| `explicit Parcel(bool)` | construct + write | build a boolean value for `setProperty` (e.g. `SELECTABLE`) |
| `readInt32(int&)` | read | pull a signed arg out of a handler's `Parcel` |
| `readUInt32(unsigned&)` | read | pull an unsigned arg — e.g. the selected **row index** in a list handler |
| `readBool(bool&)` | read | pull a boolean arg |

All three read accessors return `bool` (success) and write through the reference argument. Declarations: [`bmw_list.h–60`](../reference/sdk/bmw_list.h); row-index read in the example row handler: [`diagnostics.cpp:290–296`](../reference/example-plugin/diagnostics.cpp). The `Parcel` layout (`{buf*@0, size@4, cap@8, vptr@12, pos@16}`) is **hand-reconstructed**; the ctor/dtor and accessor *symbols* are carve-verified. Copy/assign are intentionally hidden because a shallow copy would double-free the buffer — pass `Parcel` only by `const&`. For the complete producer side (`write*` methods, `Variant`, `DataTable`) see the Data Structures reference.

---

## 3. The wiring pattern (how ids connect the DescFile to your C++)

Everything the framework calls back into you is addressed by a **numeric id declared in your DescFile**. There are two id namespaces and each has one binding call:

```
                DescFile (<Name>.xml)                     C++ (your PluginApp subclass)
  ACTIONS   <raAction id="21"/>   ── addHandler(21, delegate<&MyApp::onBuild>) ──▶ bool onBuild(const Parcel&)
            (a <button action="21">
             or <list ... action="23">
             fires it)

  MODELS    <raListModel id="50"/>  ──────────── updateModel(50, DataTable) ──────▶  list re-renders
            <raDataModel id="52"/>  ──────────── updateModel(52, BasicString) ─────▶  label/richtext re-renders
            (a <list model="50"> or
             <label model="52">
             displays it)
```

**Action flow (inbound):** the user activates a component whose `action="N"` → the framework looks up the `Delegate` you bound for action `N` with `addHandler` → your `bool onX(const Parcel&)` runs on the UI thread. The `Parcel` carries any argument (e.g. the selected row index — read it with `Parcel::readUInt32`; see the row handler [`diagnostics.cpp:290–296`](../reference/example-plugin/diagnostics.cpp)). Return `true` to mark it handled.

**Model flow (outbound):** you call `updateModel(N, …)` → the framework replaces model `N`'s contents (deep copy) → every component with `model="N"` re-renders.

Concrete correspondence in the example (DescFile ids ↔ handlers):

| DescFile declaration (`Diagnostics.xml`) | Bound in `onInit` | Handler (`diagnostics12.cpp`) |
|---|---|---|
| `<raAction id="21"/>` ("Build module list" button) | `addHandler(21, …)` `:329` | `onBuild` `:223` |
| `<raAction id="22"/>` ("Read" button) | `addHandler(22, …)` `:332` | `onRead` `:234` |
| `<raAction id="23"/>` (list row select) | `addHandler(23, …)` `:335` | `onRow` `:289` |
| `<raAction id="24"/>` (second-tool button) | `addHandler(24, …)` `:338` | `onReadSvt` `:243` |
| `<raAction id="25"/>` (master-list row select) | `addHandler(25, …)` `:341` | `onSvtRow` `:290` |
| `<raAction id="26"/>` (OPTION menu item) | `addHandler(26, …)` `:344` | `onReReadDtc` `:257` |
| `<raAction id="27"/>` (OPTION menu item) | `addHandler(27, …)` `:347` | `onClearDtc` `:273` |
| `<raListModel id="50"/>` | — | `updateModel(50, table)` via `fill()` `:135` |
| `<raListModel id="51"/>` (master list) | — | `updateModel(51, table)` `:164` |
| `<raDataModel id="52" modelType="Richtext"/>` | — | `updateModel(52, BasicString)` `:188` |

> Pick your own id numbers; they only need to agree between the DescFile and the `addHandler`/`updateModel` calls. Keep action ids globally unique to use the 2-arg `addHandler`; reuse them across states only with the 3-arg state-scoped form.

---

## 4. Threading model — the one rule

**There is a single UI/dispatcher thread and every call in this document belongs to it.** The framework invokes all of your callbacks (§A) on it, and every helper you call (§B) mutates UI state that only that thread may touch. Blocking it freezes the head unit. (This single-thread property rests on the example's design and comments plus behavior observed on the author's OPT_DEBUG-enabled unit, not on an exported symbol; a different HMI build could in principle differ, but the pattern below is the safe assumption. The dispatcher structure is examined in `07-threading-and-safety-model.md`.)

The proven pattern for real work (verified end-to-end on the author's OPT_DEBUG-enabled unit):

1. In an `addHandler` callback, **spawn a child process** (`posix_spawn`) with its stdio redirected to `/dev/null` — never block, never `fork`+`exec`+`wait` inline. ([`diagnostics.cpp:199–221`](../reference/example-plugin/diagnostics.cpp).)
2. **`post` a self-rescheduling `Runnable`** that `waitpid(…, WNOHANG)`s the child every ~400 ms *on the UI thread* (`:219`, `:352–358`).
3. On each tick and on completion, do all `updateModel`/`setProperty` from inside `run()` — which is already on the UI thread — so model/property mutation is always single-threaded.

This keeps the HMI responsive while long operations run out-of-process, and it is why `post` + `Runnable` (not a raw thread) is the sanctioned concurrency primitive. See `07-threading-and-safety-model.md` for the full safety treatment.

---

## 5. Minimal complete surface (what you'll actually write)

For a real menu app you need, in total:

```cpp
class MyApp : public bmw::PluginApp {
public:
    MyApp(bmw::IDispatcher& d, bmw::BasicString<char> name, unsigned maj, unsigned mn,
          bmw::RHMIInterfaceVersion rhmi, const bmw::Bundle& cfg, const bmw::Bundle& res)
        : bmw::PluginApp(d, name, maj, mn, rhmi, cfg, res) {}   // pass name/version/rhmi here

    virtual bool onInit();       // seed models + addHandler(...) each raAction
    virtual bool onFinalize() { return true; }

    bool onSomething(const bmw::Parcel&);  // one per raAction, returns bool
};
```

Override `onInit` and `onFinalize`; bind each `raAction` with `addHandler`; push data with `updateModel`; grey/un-grey with `setProperty`; offload work with `post(new Runnable, ms)`. That is the whole runtime API you touch. See the **Manifest & Loader** doc for how the `.so` is discovered and `pluginAppInfo`/`create` is resolved, the **DescFile** doc for the XML that declares the ids used above, and the **Data Structures** doc for the `Parcel`/`Variant`/`DataTable` payload types.

---

## Sources

- **Provenance.** Every fact here comes from an **owner-authorized offline flash carve** of the author's own titled vehicle plus **end-to-end validation of the example plugin on the author's OPT_DEBUG-enabled unit**. This on-car result is scoped to the author's own OPT_DEBUG-enabled unit; a stock unit loads the same unsigned/uncoded plugin (the loader enforces no signature; confirmed on-car). The plugin mechanics are presented generically; no car-specific network addresses, VIN, or private diagnostic-tool details are part of this SDK.
- **Carve-verified (exported symbols).** All helper and callback **mangled names, signatures, and offsets** were read with `nm -DC` from `opt/hmi/ID5/lib/libAppFramework.A.so` and the OEM `libSecurityMenu.so`. The 34-slot vtable **ordering** is spot-confirmed from the real subclass vtable in `libDiagnostics12.so` (vtable @0x56cc). The DescFile↔C++ id mappings are cross-checked between `Diagnostics.xml` and `diagnostics12.cpp`.
- **Reconstructed (marked inline).** The `bmw::PluginApp`/`Parcel`/`Variant`/`Map`/`DataTable` **class layouts** in [`bmw_list.h`](../reference/sdk/bmw_list.h) are hand-reconstructed from disassembly and are the details most likely to shift on a different NBT-Evo firmware build. The **single-thread guarantee**, the **`updateModel` deep-copy**, and the **"framework never frees your `Runnable`"** rule are reconstructed from the example's design and behavior observed on the author's OPT_DEBUG-enabled unit. Per-slot return-value semantics beyond `onInit`/`onCheckAppAvailable` are inferred from `bool` return types, not proven.
