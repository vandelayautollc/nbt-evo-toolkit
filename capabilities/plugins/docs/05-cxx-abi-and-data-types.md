# 05 — The C++ ABI & SDK Data Types

A verified reference for the *compiled* C++ interface between an RA (Remote Application) plugin and the NBT-Evo HMI process: the `pluginAppInfo` descriptor, `bmw::PluginApp` and its 34-slot vtable, and the header-only value types (`BasicString`, `Parcel`, `Variant`, `Map`, `DataTable`, `Delegate`, `Runnable`, `TextID`, `RHMIInterfaceVersion`) — each with memory layout, mangled symbol names, and the ABI gotchas that decide whether `dlopen` succeeds.

> **Scope & authorization.** Everything here was reverse-engineered from an **offline flash carve** and owner-authorized work on the author's **own titled vehicle**; write your plugin against your **own** head unit. The types below are the *mechanics* of the plugin ABI — nothing here is car-specific (no addresses, VIN, or diagnostic internals belong in this SDK).
>
> **This is the hardest doc in the SDK.** If you only want to place a menu entry and handle button presses, treat these headers as an opaque dependency and copy the example plugin. Read this doc when you need to know *why* a layout is what it is, add a value type the example doesn't use, or debug a crash inside `dlopen`.

---

## 1. What these headers *are*

The SDK ships two hand-written headers — `bmw_abi.h` (minimal, "just enough to load") and `bmw_list.h` (the fuller, authoritative one). **They contain almost no method bodies.** They are *declarations only*: data layouts, mangled-name-compatible signatures, and a handful of inline templates. The real code lives in two shared objects already on the head unit, which your `.so` links against and which the loader resolves at `dlopen(RTLD_NOW)` time.

The two libraries divide the work — and knowing which library *defines* (vs merely imports) a symbol is load-bearing for the `nm` recipes throughout this doc:

| Library | Strong-symbol (`T`) owner of | Also provides | Size (carve) |
|---|---|---|---|
| `libCoreFramework.A.so` | The container/value primitives: the **full `Parcel` ctor/reader/writer set**, `DataTableBase`, `TextID`/`PreinstTextID`, `bmw::fromString`, and the `Map`/`Variant` machinery | `typeinfo for bmw::Parcel` (@0x17110) | 95 KB, ARM EABI5, stripped |
| `libAppFramework.A.so` | `PluginApp` (ctor, vtable, `updateModel`/`addHandler`/`setProperty`/`post`), `Message` | Weak (`W`/COMDAT) instantiations of `BasicString`, `Parcel::~Parcel`, `Parcel` copy-ctor, `Runnable` dtors/vtable, and `Variant` — plus the **only** copy of `BasicString<char>::BasicString(char const*)` | 51 KB, ARM EABI5, stripped |

The loader itself lives in the `HmiMain3D` binary (a large ARM ELF); it was not disassembled for this doc, so any claim about the loader's *internal* logic is marked `[RECONSTRUCTED]` below.

Because the headers only *declare* these symbols, your compiler emits **undefined references** that the framework satisfies at load. Confirmed against the working reference plugin `libDiagnostics12.so`:

```
$ arm-none-eabi-nm -DC libDiagnostics12.so | grep ' U ' | grep bmw::
   U bmw::DataTableBase::at(unsigned int, unsigned int) const
   U bmw::DataTableBase::DataTableBase(bmw::Map<unsigned int, bmw::Variant>*, unsigned int)
   U bmw::Parcel::Parcel(bool)
   U bmw::Parcel::readInt32(int&) const
   U bmw::PluginApp::PluginApp(bmw::IDispatcher&, bmw::BasicString<char>, unsigned int, ... )
   U bmw::PluginApp::setProperty(unsigned int, unsigned int, bmw::Parcel const&)
   U bmw::PluginApp::updateModel(unsigned int, bmw::DataTableBase const&)
   U typeinfo for bmw::PluginApp
   ...
```

Every one of those `U` lines is a promise that must be kept by the framework at runtime. If a mangled name in your header is wrong by one character, `dlopen` fails with an unresolved-symbol error and your plugin never loads. **That is why the exact mangling is load-bearing and why this doc pins each one.**

### Verification legend

Because the headers are reconstructed, this doc labels every structural claim:

- **[VERIFIED]** — confirmed by inspecting the framework binaries (an `nm` symbol, a decoded vtable relocation, or a disassembled instruction). Reproducible with the commands shown.
- **[RECONSTRUCTED]** — an internal detail the author deduced (field names, some sizes, byte offsets the stripped binaries don't expose, the `abiVersion` split) that the carved libraries alone cannot fully pin down. Treat these as "correct enough to compile and run," not gospel.

All symbol addresses below are file offsets inside **whichever of the two libraries actually defines the symbol** — this doc names the library each time, because roughly a third of the value-type symbols are in `libCoreFramework.A.so`, not `libAppFramework.A.so`. The recipes used throughout were:

```
nm -DC   .../ID5/lib/libAppFramework.A.so     # demangled dynamic symbols (PluginApp, Message)
nm -DC   .../ID5/lib/libCoreFramework.A.so    # demangled dynamic symbols (Parcel, DataTableBase, TextID, Map)
nm -D    .../ID5/lib/lib*.A.so                # raw mangled names your header must match
readelf -r .../ID5/lib/libAppFramework.A.so   # vtable relocations
```

---

## 2. `PluginAppInfo` — the descriptor the loader `dlsym()`s   **[VERIFIED]**

This is the single exported, **C-linkage** symbol the HMI looks up after `dlopen`. Its name must be exactly `pluginAppInfo`. It is a flat 24-byte POD (`bmw_abi.h:49-57`):

```c
struct PluginAppInfo {
    unsigned int   abiVersion;    // +0   loader compatibility gate
    const char*    name;          // +4
    const char*    vendor;        // +8
    unsigned int   ifaceVersion;  // +12  forwarded as RHMIInterfaceVersion
    bmw::IPluginApp* (*create)(bmw::IDispatcher&, const char*,
                               const bmw::Bundle&, const bmw::Bundle&);  // +16
    void            (*destroy)(bmw::IPluginApp*);                        // +20
};
```

| Off | Field | Type | Notes |
|----:|-------|------|-------|
| +0  | `abiVersion`   | `uint32` | Loader gate. **[RECONSTRUCTED]** header comment (`bmw_abi.h:50`): read as `low16=major, high16=minor` by the generic loader path. |
| +4  | `name`         | `const char*` | Plugin name (also the manifest `<name>`). |
| +8  | `vendor`       | `const char*` | Free text. |
| +12 | `ifaceVersion` | `uint32` | Forwarded to the ctor as `RHMIInterfaceVersion`. |
| +16 | `create`       | fn ptr | Framework calls this to instantiate; returns the `IPluginApp*` primary base (offset 0 of your `PluginApp` subclass). |
| +20 | `destroy`      | fn ptr | Framework calls this to tear down. |

### Proof from an OEM plugin

The layout is not guessed — it decodes cleanly from the OEM `libSecurityMenu.so`, which exports the same symbol. Raw bytes of the descriptor at `0x3d05c`:

```
$ arm-none-eabi-objdump -s libSecurityMenu.so | grep 3d05
 3d05c 01000000 db510300 e9510300 01000000   ....Q...Q.......   <- abiVersion=1, name, vendor, ifaceVersion=1
 3d06c 00000000 00000000                       ....               <- create, destroy (see relocs)

$ arm-none-eabi-readelf -r libSecurityMenu.so | awk '$1 ~ /^0003d0[6-7]/'
0003d060  R_ARM_RELATIVE                          <- +4  name  -> .rodata string
0003d064  R_ARM_RELATIVE                          <- +8  vendor
0003d06c  R_ARM_ABS32  SecurityMenu::create(...)  <- +16 create = 0x1801c
0003d070  R_ARM_ABS32  SecurityMenu::destroy(...) <- +20 destroy = 0x16890
```

Demangled, those two function pointers are:

```
SecurityMenu::create(bmw::IDispatcher&, char const*, bmw::Bundle const&, bmw::Bundle const&)
SecurityMenu::destroy(bmw::IPluginApp*)
```

— **exactly** the `create`/`destroy` signatures declared in `bmw_abi.h`. `abiVersion` and `ifaceVersion` are both `1`. This is the strongest confirmation in the SDK that the reconstruction matches OEM reality.

### The canonical definition

```cpp
extern "C" PluginAppInfo pluginAppInfo = {
    1,                 // abiVersion   (major=1, minor=0)
    "Diagnostics",     // name
    "owner-research",  // vendor
    1,                 // ifaceVersion (-> RHMIInterfaceVersion{1})
    diag_create,
    diag_destroy,
};
```

> **Gotcha — `create()` builds the object, not the loader.** Both the OEM and the reference plugin define their *own* `create()` and call the `PluginApp` ctor with explicit `major`/`minor`. So the descriptor's `abiVersion`/`ifaceVersion` are consumed by the loader's compatibility check, *not* fed into the ctor by the loader. Keep `ifaceVersion` and the `RHMIInterfaceVersion` you pass to the ctor equal (both `1`) to be safe. Confirmed in `diagnostics.cpp:27-35` and `diagnostics12.cpp:365-372`.

---

## 3. `bmw::PluginApp` — the base class you subclass

Your plugin app *is* a `bmw::PluginApp` subclass. The base is a large polymorphic object whose real ctor installs the real vtable; you override a couple of virtuals and *call* a handful of non-virtual helpers.

### 3.1 Size and internal layout   **[VERIFIED size lower bound; field names RECONSTRUCTED]**

The complete-object ctor is `_ZN3bmw9PluginAppC1E...` at **`0x6f80`** (in `libAppFramework.A.so`). Disassembling it reveals the highest member store is at **`+348`**, so the object is **≥ 352 bytes** (`bmw_list.h:140-147` declares `char _reserved[352-4]`):

```
$ arm-none-eabi-objdump -d libAppFramework.A.so --start-address=0x6f80 --stop-address=0x7760 \
    | grep -oE 'str.*\[r[0-9]+, #[0-9]+\]' | grep -oE '#[0-9]+' | sort -n | tail
   ... #340  #344  #348
```

Two specific offsets the ctor touches, both matching the header comments:

```
6fd8:  str r2, [r5, #4]     <- secondary vptr: the bmw::PluginAppHandler base sub-object @ +4
7074:  str r3, [r5, #88]    <- m_pConnector @ +88 (0x58)
```

| Region | Off | Meaning |
|---|---:|---|
| primary vptr | +0 | `PluginApp`'s own vtable pointer (the one g++ rewrites in your subclass). |
| `PluginAppHandler` base vptr | +4 | Secondary base sub-object (`post`/`dispatch` machinery). Its vtable is emitted right after the primary one — see §3.3. |
| `m_pConnector` | +88 | The connector to the HMI (Etch, per the manifest `<pluginAppConnector>`). **[RECONSTRUCTED name]** |
| … | …+348 | Remaining framework state; opaque to plugins. |

> **Two headers disagree on the size — trust `bmw_list.h`.** The minimal `bmw_abi.h:30` comment calls `PluginApp` "real ~212B" and reserves `char _opaque[512]`; the authoritative `bmw_list.h` reserves 352 bytes to match the verified `+348` highest store. The `~212B` figure in `bmw_abi.h` is a stale early estimate — do **not** size a member layout against it. `bmw_abi.h` gets away with it only because it *over*-reserves (512 bytes) and never defines its own members.
>
> **Gotcha — never define your own members before calling the base ctor, and never `memset` the object.** The base occupies the first ~352 bytes and the real ctor initializes them (including two vptrs). Your subclass members are appended after `+352`.

### 3.2 The constructor   **[VERIFIED]**

```
0x6f80  bmw::PluginApp::PluginApp(bmw::IDispatcher&, bmw::BasicString<char>,
                                  unsigned int, unsigned int,
                                  bmw::RHMIInterfaceVersion,
                                  bmw::Bundle const&, bmw::Bundle const&)   [C1 complete]
0x7760  ... same signature ...                                             [C2 base]
```

Raw: `_ZN3bmw9PluginAppC1ERNS_11IDispatcherENS_11BasicStringIcEEjjNS_20RHMIInterfaceVersionERKNS_6BundleES8_` (both in `libAppFramework.A.so`).

Note **`BasicString<char>` is passed by value** (not by reference) and the two `Bundle`s by const-reference. Your subclass ctor forwards all seven arguments verbatim:

```cpp
Diagnostics(bmw::IDispatcher& d, bmw::BasicString<char> name, unsigned maj, unsigned mn,
            bmw::RHMIInterfaceVersion rhmi, const bmw::Bundle& cfg, const bmw::Bundle& res)
    : bmw::PluginApp(d, name, maj, mn, rhmi, cfg, res) { ... }
```

The ctor installs the real primary vtable at `+0` and the `PluginAppHandler` vtable at `+4`. When g++ compiles your subclass it *rewrites only the primary vtable* (slots you override point at your code; the rest keep the framework's addresses, imported as undefined symbols). This is why a subclass that overrides just `onInit`/`onFinalize` still emits ~30 undefined `bmw::PluginApp::*` references — they populate the inherited vtable slots.

### 3.3 The 34-slot primary vtable   **[VERIFIED — decoded from relocations]**

The vtable symbol `vtable for bmw::PluginApp` is at `0xd100` (in `libAppFramework.A.so`). Word `+0` is offset-to-top, `+4` is the RTTI pointer (`_ZTIN3bmw9PluginAppE`), and slots begin at `0xd108`. Every slot below was read directly out of `.data.rel.ro` via `readelf -r` and cross-referenced to a demangled symbol — this is not inferred from the header, it *is* the binary's dispatch table:

| # | vtable @ | fn @ | Signature | Plugin does |
|--:|:--------:|:----:|-----------|-------------|
| 0 | 0xd108 | 0x6a90 | `~PluginApp()` *(complete, D1)* | dtor |
| 1 | 0xd10c | 0x6808 | `~PluginApp()` *(deleting, D0)* | dtor |
| 2 | 0xd110 | 0x6750 | `bool start()` | inherit |
| 3 | 0xd114 | 0x668c | `bool stop()` | inherit |
| 4 | 0xd118 | 0x4fe4 | `bool activate()` | inherit |
| 5 | 0xd11c | 0x505c | `bool deactivate()` | inherit |
| 6 | 0xd120 | 0x5094 | `bool init()` | inherit *(calls `onInit`)* |
| 7 | 0xd124 | 0x50c4 | `bool finalize()` | inherit *(calls `onFinalize`)* |
| 8 | 0xd128 | 0x604c | `void post(const Message&)` | inherit |
| 9 | 0xd12c | 0x6038 | `void post(const Message&, uint)` | inherit |
| 10 | 0xd130 | 0x6024 | `void post(Runnable*)` | **call** |
| 11 | 0xd134 | 0x6010 | `void post(Runnable*, uint ms)` | **call** |
| 12 | 0xd138 | 0x5114 | `bool getName() const` | inherit |
| 13 | 0xd13c | 0x6138 | `bool getResourceFile(ResourceType::ResourceTypes) const` | inherit |
| 14 | 0xd140 | 0x5124 | `bool getVersion(uint&,uint&,uint&) const` | inherit |
| 15 | 0xd144 | 0x5148 | `bool getRhmiVersion(RHMIInterfaceVersion&) const` | inherit |
| 16 | 0xd148 | 0x5a88 | `bool invokeCommand(uint, const Parcel&)` | inherit |
| 17 | 0xd14c | 0x5a18 | `bool updateModel(uint, const Parcel&, uchar)` *(virtual)* | inherit |
| 18 | 0xd150 | 0x5de8 | `bool handleEvent(uint, uint, const Parcel&)` | inherit |
| 19 | 0xd154 | 0x59a8 | `bool invokeDataUpdate(uint, const Parcel&)` | inherit |
| 20 | 0xd158 | 0x5504 | `bool requestDataValue(uint)` | inherit |
| 21 | 0xd15c | 0x5108 | `bool onError(uint, const BasicString<char>&)` | *(override to log)* |
| 22 | 0xd160 | 0x50ec | `bool onInit()` | **override** |
| 23 | 0xd164 | 0x50fc | `bool onFinalize()` | **override** |
| 24 | 0xd168 | 0x5524 | `bool getCapabilities(const std::string&)` | inherit |
| 25 | 0xd16c | 0x5778 | `bool onCheckAppAvailable()` | *(override to gate)* |
| 26 | 0xd170 | 0x6228 | `bool handleMessage(const Message&)` | inherit |
| 27 | 0xd174 | 0x5d40 | `bool invokeCommandWithMap(uint, const Map<uint,Variant>&)` | inherit |
| 28 | 0xd178 | 0x5cd0 | `bool updateModelWithMap(uint, const Map<uint,Variant>&)` | inherit |
| 29 | 0xd17c | 0x5f9c | `bool handleEventWithMap(uint,uint,const Map<uint,Variant>&)` | inherit |
| 30 | 0xd180 | 0x57c0 | `bool invokeCDSUpdate(BasicString<char>&, BasicString<ushort>&)` | inherit |
| 31 | 0xd184 | 0x560c | `bool invokeVoiceStateChanged(ushort)` | inherit |
| 32 | 0xd188 | 0x5788 | `bool invokeAppManagerUpdate(const BasicString<char>&)` | inherit |
| 33 | 0xd18c | 0x575c | `bool invokeSdsEvent(uint, const Map<uint,Variant>&)` | inherit |

Immediately after slot 33, the framework emits the secondary vtable for the `bmw::PluginAppHandler` base sub-object (the `nextExecTime`/`dispatch`/`handleMessage` machinery of the object at `+4`); its address-point symbol `vtable for bmw::PluginAppHandler` resolves at **`0xd1d0`** (`nm -DC libAppFramework.A.so`).

> **The return types are `[RECONSTRUCTED]`.** Mangled names encode parameter lists and `const`-ness but **not** return types, so `bool start()` vs `void start()` cannot be confirmed from the binary; the `bool`/`void` column matches the reconstructed header. What *is* verified is the slot **order, count, address, and parameter signature** of all 34 entries.
>
> **The two rules that make this table safe to build against:**
> 1. **Order and count are frozen.** Declare the virtuals in `bmw_list.h`'s exact order, all 34, or g++ builds a differently-shaped subclass vtable and the framework calls the wrong slot. Do **not** add or reorder virtuals.
> 2. **Signatures matter for the ABI.** `const`-ness is part of the mangled slot for `getName`/`getVersion`/`getRhmiVersion`/`getResourceFile`; the two `post(...)` entries are the only `void`-returning virtuals in the reconstructed header.
>
> Whether the framework actually *invokes* `onError` (slot 21) or `onCheckAppAvailable` (slot 25) for RA plugins is an open question — those hooks are present but were not observed firing in the carve.

### 3.4 Non-virtual helpers you *call*   **[VERIFIED]**

These are **not** in the vtable — they are ordinary member functions (strong `T` in `libAppFramework.A.so`) that you invoke on `this`. They are the entire "output" surface of a plugin (push data to models, wire up callbacks, set component properties, schedule work):

| Symbol @ (App) | Signature | Purpose |
|:--------------:|-----------|---------|
| 0x539c | `updateModel(uint model, const DataTableBase&)` | push a list/table into a `raListModel`. |
| 0x529c | `updateModel(uint model, const BasicString<char>&)` | push a string into a `raDataModel`. |
| 0x52dc | `updateModel(uint model, const TextID&)` | push a localized text id. |
| 0x5970 | `addHandler(uint action, const Delegate<bool,const Parcel&>&)` | bind a `raAction` to a member fn. |
| 0x5db0 | `addHandler(uint state, uint action, const Delegate<bool,const Parcel&>&)` | state-scoped variant. |
| 0x54a4 | `setProperty(uint component, uint prop, const Parcel&)` | set a component property at runtime (e.g. `SELECTABLE=2` to grey a button). |

Raw manglings (spot-checked in `libAppFramework.A.so`):

```
_ZN3bmw9PluginApp11updateModelEjRKNS_13DataTableBaseE              0x539c
_ZN3bmw9PluginApp11updateModelEjRKNS_11BasicStringIcEE             0x529c
_ZN3bmw9PluginApp11updateModelEjRKNS_6TextIDE                      0x52dc
_ZN3bmw9PluginApp10addHandlerEjRKNS_8DelegateIbRKNS_6ParcelEvvvEE  0x5970
_ZN3bmw9PluginApp10addHandlerEjjRKNS_8DelegateIbRKNS_6ParcelEvvvEE 0x5db0
_ZN3bmw9PluginApp11setPropertyEjjRKNS_6ParcelE                     0x54a4
```

There are **many more** `updateModel` overloads defined in `libAppFramework.A.so` — `bool`(0x515c), `char`(0x519c), `uchar`(0x517c), `int`(0x521c), `uint`(0x51fc), `short`, `ushort`, `float`(0x523c), `const char*`(0x525c), `wchar_t const*`, `Image`, `Date`, `Time`, `DateTime`, `ImageID`, and `DataTableBase` with extra range args — plus `triggerEvent`, `amRegisterApp`, `sdsRegisterIntent`, `cdsGetPropertyAsync`, `persistSetResource`, and the whole `*WithMap` family. The headers only declare the subset the reference plugin needs; add the overload you want by copying its mangled name from `nm -DC libAppFramework.A.so`. (See **06 — Runtime API Reference** for the full enumeration.)

---

## 4. Value types (header-only + linked)

> **Where these live.** Except where noted, the value-type ctors/dtors/accessors below are strong (`T`) symbols in **`libCoreFramework.A.so`**, *not* `libAppFramework.A.so`. Grep the correct library or you'll get nothing back.

### 4.1 `BasicString<char>` — the COW string   **[VERIFIED symbols, layout RECONSTRUCTED]**

The framework's string is copy-on-write. `bmw_list.h:30-39` models it as a **single 4-byte pointer** to a COW buffer whose length/refcount header sits at negative offsets `[-12..-1]`:

```cpp
template <class T> class BasicString {
    T* m_data;                                   // +0 (COW buffer ptr; header at [-12..-1])
public:
    BasicString(const T* s);                     // _ZN3bmw11BasicStringIcEC1EPKc
    BasicString(const BasicString& o);           // _ZN3bmw11BasicStringIcEC1ERKS1_
    ~BasicString();                              // _ZN3bmw11BasicStringIcED1Ev
    BasicString& operator=(const BasicString&);  // _ZN3bmw11BasicStringIcEaSERKS1_
};
```

All are COMDAT-weak (`W`), but they are **not all in both libraries** — an important nuance for `dlopen` resolution:

```
$ nm -DC libAppFramework.A.so | grep 'BasicString<char>::'
  0000845c W bmw::BasicString<char>::BasicString(char const*)          <- ONLY here
  00008310 W bmw::BasicString<char>::BasicString(bmw::BasicString<char> const&)
  000081a4 W bmw::BasicString<char>::~BasicString()
  0000838c W bmw::BasicString<char>::operator=(bmw::BasicString<char> const&)

$ nm -DC libCoreFramework.A.so | grep 'BasicString<char>::'
  00009f24 W ...BasicString(bmw::BasicString<char> const&)    # copy-ctor: in both
  00009d50 W ...~BasicString()                                # dtor: in both
  00009fa0 W ...operator=(...)                                # assign: in both
  # BasicString(char const*)  --  ABSENT
```

> **Gotcha — the from-C-string ctor `_ZN3bmw11BasicStringIcEC1EPKc` lives in `libAppFramework.A.so` only** (@0x845c). The copy-ctor, dtor, and `operator=` are duplicated (weak) in both libs, but the from-`char*` ctor is not — so the "resolves regardless of which library loads first" reassurance holds for the copy/dtor/assign trio but **not** for the `char const*` ctor. In practice both libs are loaded by the time your plugin does, so this is fine; it matters only if you ever try to satisfy the plugin against `libCoreFramework.A.so` alone.

Because it has a user copy-ctor and dtor it is **non-trivial**, so g++ passes it by *invisible reference* even where the signature says by-value (the `PluginApp` ctor's second parameter). Construct one from a C string wherever the API wants a string:

```cpp
updateModel(SVT_DETAIL_MODEL, bmw::BasicString<char>(buf));   // diagnostics12.cpp:188
```

> **Header discrepancy to know about.** `bmw_abi.h:15-24` declares `BasicString` as `char _opaque[32]` — deliberately **over**-sized, because that minimal header only ever passes it by reference/value and never touches a field. The authoritative `bmw_list.h` says the real object is **4 bytes**. Use `bmw_list.h` for anything that stores a string as a member.

### 4.2 `RHMIInterfaceVersion` — trivial POD by value   **[VERIFIED]**

```cpp
struct RHMIInterfaceVersion { unsigned int value; };   // 4 bytes, trivially copyable
```

Must stay a trivial aggregate (no user ctor) so it is passed in a single register, matching the ctor disassembly (`bmw_abi.h:26-28`). You build it inline: `bmw::RHMIInterfaceVersion v; v.value = 1;`.

### 4.3 `TextID` — 8-byte localized-text handle   **[VERIFIED symbols; tag RECONSTRUCTED]**

```cpp
class TextID { unsigned int m_a, m_b; public: TextID(unsigned int id); };
```

`nm -DC libCoreFramework.A.so` confirms three ctors (each in C1/C2 form — see §4.10):

```
_ZN3bmw6TextIDC1Ej    0xd180   TextID::TextID(unsigned int)
_ZN3bmw6TextIDC1Ejj   0xd150   TextID::TextID(unsigned int, unsigned int)
_ZN3bmw6TextIDC1Ev    0xd1b8   TextID::TextID()
```

(A related `bmw::PreinstTextID` sits right beside it at 0xd1e8, for pre-installed text DBs.) Two `uint` words ⇒ 8 bytes, trivially copyable. Its `VariantTag` is **40 (0x28)** **[RECONSTRUCTED]** (§4.5 — unlike the `BasicString` tag it was not independently disassembled, because the reference plugin never instantiates `ObjectContainer<TextID>`). Use it with `updateModel(model, TextID(id))` to feed a text id from the plugin's text DB instead of a literal string.

### 4.4 `Parcel` — the serialization buffer   **[symbol names/addresses VERIFIED; byte layout RECONSTRUCTED]**

`Parcel` is how scalar payloads cross the ABI in both directions: **outbound** you build one to carry a property value into `setProperty`; **inbound** the framework hands your `raAction` handler a `const Parcel&` carrying the selected row index.

Its symbols are defined (strong `T`) in **`libCoreFramework.A.so`**. Its **byte layout** — 20 bytes, 4-aligned, `{buf*@0, size@4, cap@8, vptr@12, pos@16}` — is **reconstructed from `bmw_list.h:47-64`**, not read from the binary: the stripped libs expose no `Parcel` member or offset symbols, only `typeinfo for bmw::Parcel` (@0x17110, in Core), which confirms the class *is* polymorphic but does **not** pin the vptr offset.

```cpp
class Parcel {
    unsigned int _raw[5];                    // 20 bytes; real ctor/dtor manage it  [layout RECONSTRUCTED]
public:
    Parcel();                                // _ZN3bmw6ParcelC1Ev
    explicit Parcel(bool);                   // _ZN3bmw6ParcelC1Eb
    ~Parcel();                               // _ZN3bmw6ParcelD1Ev
    bool readInt32 (int&)          const;    // _ZNK3bmw6Parcel9readInt32ERi
    bool readUInt32(unsigned int&) const;    // _ZNK3bmw6Parcel10readUInt32ERj
    bool readBool  (bool&)         const;    // _ZNK3bmw6Parcel8readBoolERb
private:
    Parcel(const Parcel&);                   // hidden: would shallow-copy buf@0
    Parcel& operator=(const Parcel&);
};
```

Verified addresses (only the ones the SDK declares are shown; the binary also has `readUInt8/16`, `readFloat32`, `readString`, the `writeXxx` set, and value ctors `Parcel(int)`, `Parcel(uint)`, `Parcel(float)`, `Parcel(const BasicString<char>&)`, etc.):

```
# libCoreFramework.A.so
0xbd84 Parcel::Parcel()            0xceb8 Parcel::Parcel(bool)  [C1]   0xcf1c Parcel::Parcel(bool) [C2]
0xbe54 Parcel::readBool(bool&) const
0xc048 Parcel::readUInt32(unsigned int&) const
0xc0a8 Parcel::readInt32(int&) const
0x17110 typeinfo for bmw::Parcel
# libAppFramework.A.so (weak copies used by PluginApp's own code)
0x8204 Parcel::~Parcel()   [W]     0x9fd0 Parcel::Parcel(bmw::Parcel const&)  [W, hidden in header]
```

> **Gotcha — the vptr is at `+12`, not `+0` (RECONSTRUCTED).** The header treats `Parcel` as polymorphic with its vtable pointer *not* the first word (the buffer pointer is). **Do not** declare virtuals on the header's `Parcel` — that would put a vptr at `+0` and corrupt the layout. Store 20 opaque bytes and let the linked ctor/dtor manage them. (The exact `+12` offset is the author's reconstruction; the binary confirms only that the class is polymorphic.)
>
> **Gotcha — copy is deleted on purpose.** A default copy would shallow-copy `buf@0` and double-free. The binary *does* export a copy-ctor (`0x9fd0`, weak, in App) but the SDK hides it so you can't accidentally copy a `Parcel` by value. Pass by `const&`.

Typical use, both directions:

```cpp
// outbound: grey/un-grey a button via SELECTABLE (property 2)
void set_button(unsigned comp, bool en){ bmw::Parcel p(en); setProperty(comp, 2u, p); }

// inbound: read the selected row index out of an raAction callback
bool onSvtRow(const bmw::Parcel& p){
    int i = -1;
    if (!p.readInt32(i)) { unsigned u=0; if (p.readUInt32(u)) i=(int)u; }
    ...
}
```

### 4.5 `Variant` / `IObjectContainer` / `ObjectContainer<T>` / `VariantTag`   **[VERIFIED]**

A `Variant` is a **4-byte handle** (one pointer, `m_impl @ +0`) to a polymorphic pimpl that carries one typed value. This is how a `DataTable` cell holds a string, a text id, or any other value with a runtime tag (`bmw_list.h:66-91`):

```cpp
class Variant {
public:
    class IObjectContainer {                     // vtable: [0]~D1 [1]~D0 [2]type [3]clone
        virtual ~IObjectContainer();
        virtual unsigned int type()   const = 0;
        virtual IObjectContainer* clone() const = 0;
    };
    template <class T>
    class ObjectContainer : public IObjectContainer {
        T m_val;                                 // +4 (payload; as<T>() returns this+4)
        virtual unsigned int type() const { return (unsigned int)VariantTag<T>::value; }
        virtual IObjectContainer* clone() const { return new ObjectContainer<T>(m_val); }
    };
    IObjectContainer* m_impl;                    // +0
};
```

The **tag values** are `type()` return constants, and they are real: compiling `ObjectContainer<BasicString<char>>::type()` produces literally `mov r0, #34`:

```
$ arm-none-eabi-objdump -d libDiagnostics12.so
  000040f8 <..ObjectContainer<BasicString<char>>::type() const>:
    40f8:  e3a00022  mov  r0, #34  @ 0x22      <- returns 34
    ...
```

| `T` | `VariantTag<T>::value` | Confirmed by |
|-----|:---:|---|
| `BasicString<char>` | **34 (0x22)** | `mov r0, #34` in the compiled plugin **[VERIFIED]** |
| `TextID` | **40 (0x28)** | `bmw_list.h:69` **[RECONSTRUCTED]** |

The framework provides `Variant::is<T>()`, `Variant::as<T&>()`, `~Variant`, `operator=` and the `Map<uint,Variant>`/`Map<BasicString,Variant>` machinery as COMDAT-weak symbols; the container's own vtable/typeinfo are emitted into *your* `.so` when you instantiate `ObjectContainer<T>` (they appear as `V`/`W` symbols in `libDiagnostics12.so`). To put a string in a cell:

```cpp
bmw::Variant& c = table.at(row, 0);
c.m_impl = new bmw::Variant::ObjectContainer<bmw::BasicString<char>>(bmw::BasicString<char>(s));
```

> **Gotcha — you assign `m_impl` directly.** The SDK doesn't reconstruct `Variant`'s value-setting ctors, so the reference plugin writes the container pointer straight into the cell. `DataTable::clear()` (called by `updateModel`'s deep copy and by `~DataTable`) owns and frees these containers via their virtual `~IObjectContainer`.

### 4.6 `Map<K,V>` — the hash container   **[VERIFIED constants; field names RECONSTRUCTED]**

`Map<uint,Variant>` is the column type inside a `DataTable`. It is **24 bytes**, and the ctor must set specific non-zero defaults or the first insert divides by zero (`bmw_list.h:93-106`):

```cpp
template <class K, class V> class Map {
    void*        m_buckets;      // +0   = 0
    unsigned int m_bucketCount;  // +4   = 17   <-- hash modulus, MUST be nonzero
    unsigned int m_size;         // +8   = 0
    unsigned int m_f12;          // +12  = 0
    void*        m_memBlock;     // +16  = 0    (node pool)
    unsigned int m_f20;          // +20  = 10   (nodes per pool chunk)
public:
    Map() : m_buckets(0), m_bucketCount(17), m_size(0),
            m_f12(0), m_memBlock(0), m_f20(10) {}
};
```

Those two magic constants are not guessed — they appear as immediate moves in the inlined `Map` ctor of the compiled plugin (the `DataTable<1>` path builds one `Map` per column):

```
$ arm-none-eabi-objdump -d libDiagnostics12.so | grep -E 'mov.*#17|mov.*#10'
  324c:  e3a03011  mov  r3, #17     <- m_bucketCount
  325c:  e3a0300a  mov  r3, #10     <- m_f20
```

`operator[]`, `newAssoc`, `copyFrom`, `~Map` etc. are COMDAT-weak (`W`) and appear in **both** framework libs (the strong container implementation is in `libCoreFramework.A.so`), so you never implement them — you just make sure the ctor's field defaults are right. The field *names* `m_f12`/`m_f20` and the rest of the 24-byte layout beyond the two confirmed immediates are the author's reconstruction.

> **Gotcha — `bucketCount = 17`.** Leave it at the reconstructed `17`. A zero here means a modulo-by-zero on the first `operator[]`, which crashes the HMI UI thread.

### 4.7 `DataTableBase` / `DataTable<NCOLS>`   **[VERIFIED]**

`DataTableBase` is the 8-byte handle a list model wants; `DataTable<NCOLS>` is a template that owns the per-column `Map`s and frees them via RAII (`bmw_list.h:108-125`). Its symbols are strong (`T`) in **`libCoreFramework.A.so`**:

```cpp
class DataTableBase {
    Map<unsigned int, Variant>* m_columns;   // +0
    unsigned int                m_nColumns;  // +4
public:
    DataTableBase(Map<unsigned int, Variant>* cols, unsigned int nCols);  // 0xaa24 [C1]
    Variant& at(unsigned int row, unsigned int col) const;                // 0xab38
    void     clear();                                                     // 0xaa90
};

template <int NCOLS> class DataTable : public DataTableBase {
    Map<unsigned int, Variant> m_cols[NCOLS];
public:
    DataTable() : DataTableBase(m_cols, NCOLS) {}
    ~DataTable() { clear(); }
};
```

Confirmed symbols (`nm -DC libCoreFramework.A.so`):

```
_ZN3bmw13DataTableBaseC1EPNS_3MapIjNS_7VariantEEEj   0xaa24  DataTableBase(Map<uint,Variant>*, uint) [C1]
_ZN3bmw13DataTableBaseC2EPNS_3MapIjNS_7VariantEEEj   0xaa10  ... [C2]
_ZNK3bmw13DataTableBase2atEjj                        0xab38  at(uint,uint) const  -> Variant&
_ZN3bmw13DataTableBase5clearEv                       0xaa90  clear()
# bonus: rows() const @0xaa38, columns() const @0xaa80
```

`at(row,col)` returns a `Variant&` you populate (§4.5). One column ⇒ `DataTable<1>`. Fill it, then hand it to `updateModel`:

```cpp
bmw::DataTable<1>* t = new bmw::DataTable<1>();
add_row(*t, 0, "Read DTCs");            // c.m_impl = new ObjectContainer<BasicString<char>>(...)
updateModel(LIST_MODEL, *t);            // updateModel DEEP-COPIES the table
```

> **Gotcha — `updateModel` deep-copies, so ownership is simple but leaks are easy.** `updateModel(uint,const DataTableBase&)` (`0x539c`, in App) copies the table's contents into the model, so the framework does *not* take ownership of your `DataTable`. In the reference plugin `fill()` heap-allocates the `DataTable` and does not delete it — a small deliberate leak per refresh. If you allocate on the stack instead, its `~DataTable`/`clear()` will free the `Variant` containers when it goes out of scope, which is fine *after* `updateModel` has copied them. Pick one model and be consistent.

### 4.8 `Delegate<R, A1..A4>` — member-fn callback   **[VERIFIED]**

A `Delegate` is an **8-byte POD** — `{ void* obj; R(*exec)(void*, A1); }` — plus a per-`(class,method)` static thunk that recovers the typed `this` and forwards. This is how an `raAction` id gets bound to one of your member functions (`bmw_list.h:127-135`):

```cpp
template <class R, class A1 = void, class A2 = void, class A3 = void, class A4 = void>
class Delegate {
public:
    void* m_obj;                    // +0
    R (*m_exec)(void*, A1);         // +4
    template <class C, R (C::*M)(A1)>
    static R execImpl(void* self, A1 a) { return (static_cast<C*>(self)->*M)(a); }
};
```

`Delegate` has **no standalone symbols** in the framework — it is header-only, inlined into each caller and into the `Map` key/value types that store it. The framework side of `addHandler` proves the 5-parameter shape (`R` + `A1..A4`, all `void` past `A1`):

```
_ZN3bmw9PluginApp10addHandlerEjRKNS_8DelegateIbRKNS_6ParcelEvvvEE
                                      ^Delegate< b, RK Parcel, v, v, v >
```

Your `execImpl` instantiations show up as weak symbols in your `.so` — one per bound method:

```
$ arm-none-eabi-nm -C libDiagnostics12.so | grep execImpl
  bool bmw::Delegate<bool, bmw::Parcel const&,...>::execImpl<Diagnostics, &Diagnostics::onBuild>(void*, bmw::Parcel const&)
  bool bmw::Delegate<bool, bmw::Parcel const&,...>::execImpl<Diagnostics, &Diagnostics::onRead >(void*, bmw::Parcel const&)
  ... one per raAction
```

Wire-up pattern (from `diagnostics12.cpp:327-329`) — set `m_obj`, point `m_exec` at the template-instantiated thunk, register against the action id:

```cpp
bmw::Delegate<bool, const bmw::Parcel&> dB;
dB.m_obj  = this;
dB.m_exec = &bmw::Delegate<bool,const bmw::Parcel&>
              ::execImpl<Diagnostics, &Diagnostics::onBuild>;
addHandler(BUILD_ACTION, dB);   // BUILD_ACTION = raAction id 21 in the DescFile
```

### 4.9 `Runnable` — the UI-thread work item, and the COMDAT-weak dtor trick   **[VERIFIED]**

`Runnable` is the **root interface** for a unit of work you `post()` onto the HMI dispatcher (UI) thread. It is **4 bytes (vptr only)** with a 3-entry vtable `[~D1, ~D0, run()]` (`bmw_list.h:19-27`):

```cpp
class Runnable {
public:
    virtual ~Runnable() {}        // emits LOCAL weak D2/D1/D0 in your .so — see below
    virtual void run() = 0;       // vtable slot 2
};
```

`nm` on `libAppFramework.A.so` confirms the type is real (vtable + typeinfo present) but that it exports **only `D1` and `D0`** dtors — **not `D2`** (the base-object dtor):

```
$ nm -D libAppFramework.A.so | grep _ZN3bmw8RunnableD
  00008038 W _ZN3bmw8RunnableD1Ev      (present)
  00008fec W _ZN3bmw8RunnableD0Ev      (present)
  # _ZN3bmw8RunnableD2Ev               -- ABSENT (in both libs)
$ nm -DC libAppFramework.A.so | grep 'vtable for bmw::Runnable'
  0000d088 V vtable for bmw::Runnable
```

> **Why the inline empty `~Runnable(){}` in the header is mandatory.** When you subclass `Runnable`, your derived dtor must call the base **base-object** dtor `_ZN3bmw8RunnableD2Ev`. The OEM libs don't export it. Declaring `virtual ~Runnable() {}` in the header makes g++ emit its **own local, COMDAT-weak** copies of the Runnable dtors, vtable and typeinfo into your `.so`, so `dlopen(RTLD_NOW)` has everything it needs. Verified in the compiled plugin:
> ```
> $ arm-none-eabi-nm libDiagnostics12.so | grep -E 'Runnable|vtable for bmw::Runnable'
>   0000408c W _ZN3bmw8RunnableD1Ev
>   00004148 W _ZN3bmw8RunnableD0Ev
>   0000579c V vtable for bmw::Runnable        # local copy, merges with the lib's
> ```
> (At `-O`, g++ folds `D2` into `D1`, so you see `D1`/`D0` weak; the exact set of emitted dtor variants depends on optimization level. The point holds either way: your object file *provides* a definition instead of importing the missing base dtor, and because they're COMDAT-weak they merge harmlessly with the framework's copies at load.)

**Lifetime contract — the framework never frees a `Runnable` for you:**

```cpp
class ChildPoller : public bmw::Runnable {
    Diagnostics* app_; pid_t pid_; unsigned ms_;
public:
    virtual void run() {
        int st = 0;
        if (::waitpid(pid_, &st, WNOHANG) == 0) {   // still running:
            app_->on_poll_running();
            app_->post(this, ms_);                  //   RE-POST self, return WITHOUT deleting
            return;
        }
        app_->on_scan_done();
        delete this;                                // done: delete self at the END of run()
    }
};
```

A **one-shot** `Runnable` must `delete this;` at the end of `run()`. A **self-rescheduling** one re-`post(this, ms)`s and returns without deleting. `run()` always fires on the UI thread, which is what makes it safe to touch models/properties from inside it (`diagnostics12.cpp:352-358`).

### 4.10 Complete-object vs base-object ctors (C1/C2)   **[VERIFIED]**

Every non-trivial value type is emitted in two ctor forms at adjacent addresses — `C1` (complete-object) and `C2` (base-object) — and both are exported. This doc cites the `C1` address; if you match a raw mangled name from a disassembly you may land on the `C2` sibling instead. Confirmed pairs:

| Type ctor | C1 @ | C2 @ | Library |
|---|:---:|:---:|---|
| `Parcel::Parcel(bool)` | 0xceb8 | 0xcf1c | Core |
| `DataTableBase::DataTableBase(Map*, uint)` | 0xaa24 | 0xaa10 | Core |
| `TextID::TextID(uint)` | 0xd180 | 0xd19c | Core |

Functionally the two are equivalent for a leaf class like these (no virtual bases), so either address satisfies the reference.

---

## 5. Threading & ownership summary (why the ABI is shaped this way)

- **Everything runs on one thread** — the HMI UI/dispatcher thread. `onInit`, every `raAction` handler, and every `Runnable::run()` are called there.
- **Long work goes in a child process** (`posix_spawn`), never a `pthread`, and is polled by a self-rescheduling `Runnable` posted with `post(this, ms)`. All model/property mutation happens on the UI thread inside `run()`.
- **`updateModel(...,DataTableBase&)` deep-copies**, so a table you build is yours to free; the framework keeps its own copy.
- **`Parcel` is move-only-ish** (copy hidden); pass by `const&`.
- **`Variant` cells own their `ObjectContainer`**, freed by `DataTable::clear()`.

See **07 — Threading and Safety Model** for the full lifecycle, and **04 — Menus, Screens and Layout** for how the `raAction`/`raListModel`/component ids in the tables above map to the DescFile XML.

---

## Appendix A — Symbol quick-reference

> **Regenerate any row with `nm -DC <library> | grep <name>`** — but grep the **right** library. The two tables below are split by where each symbol is *defined*; a symbol listed under Core is `U`/absent in App and vice versa (except the weak container instantiations, which appear in both).

### A.1 Defined in `libAppFramework.A.so`

| Symbol @ | Demangled |
|:--------:|-----------|
| 0x6f80 | `PluginApp::PluginApp(IDispatcher&, BasicString<char>, uint, uint, RHMIInterfaceVersion, Bundle const&, Bundle const&)` [C1] |
| 0x6a90 / 0x6808 | `~PluginApp()` D1 / D0 (vtable slots 0/1) |
| 0x539c | `PluginApp::updateModel(uint, DataTableBase const&)` |
| 0x529c | `PluginApp::updateModel(uint, BasicString<char> const&)` |
| 0x52dc | `PluginApp::updateModel(uint, TextID const&)` |
| 0x5970 / 0x5db0 | `PluginApp::addHandler(uint, Delegate…)` / `(uint,uint,Delegate…)` |
| 0x54a4 | `PluginApp::setProperty(uint, uint, Parcel const&)` |
| 0x6024 / 0x6010 | `PluginApp::post(Runnable*)` / `post(Runnable*, uint)` |
| 0x50ec / 0x50fc | `PluginApp::onInit()` / `onFinalize()` (vtable slots 22/23) |
| 0xd100 | `vtable for bmw::PluginApp` (slots at +8 … +0x8c) |
| 0xd1d0 | `vtable for bmw::PluginAppHandler` (secondary base sub-object @ +4) |
| 0x845c / 0x81a4 | `BasicString<char>::BasicString(char const*)` / `~BasicString()` (weak; the `char const*` ctor is here **only**) |
| 0x8204 / 0x9fd0 | `Parcel::~Parcel()` / `Parcel::Parcel(Parcel const&)` (weak) |
| 0x8038 / 0x8fec / 0xd088 | `Runnable` D1 / D0 / `vtable for bmw::Runnable` |

### A.2 Defined in `libCoreFramework.A.so`

| Symbol @ | Demangled |
|:--------:|-----------|
| 0xbd84 / 0xceb8 | `Parcel::Parcel()` / `Parcel::Parcel(bool)` [C1] |
| 0xbe54 / 0xc048 / 0xc0a8 | `Parcel::readBool / readUInt32 / readInt32` (all `const`) |
| 0x17110 | `typeinfo for bmw::Parcel` (polymorphic; does not pin the vptr offset) |
| 0xaa24 / 0xab38 / 0xaa90 | `DataTableBase::DataTableBase [C1] / at / clear` |
| 0xaa38 / 0xaa80 | `DataTableBase::rows() / columns()` |
| 0xd180 / 0xd150 / 0xd1b8 | `TextID::TextID(uint) [C1] / (uint,uint) / ()` |
| 0xd1e8 | `PreinstTextID::PreinstTextID(uint)` |
| (weak, both libs) | `Map<uint,Variant>::operator[] / newAssoc / copyFrom / ~Map`, `BasicString<char>` copy-ctor/dtor/`operator=`, `Variant::is<>/as<>/~Variant`, `bmw::fromString` |

Add `-D` (without `C`) to any recipe to get the raw mangled form your header must match **exactly** — one wrong character and `dlopen` refuses the plugin.

---

## Sources & authorization

All facts in this document were derived from an **owner-authorized offline flash carve** of the author's **own titled vehicle's** NBT-Evo head unit, plus end-to-end validation of the working reference plugin: it was **verified end-to-end on the author's OPT_DEBUG-enabled unit** — discovered, `dlopen`'d (constructor + `create()` markers fire), the menu entry rendered, and `updateModel`/`addHandler`/`setProperty` all working. That result is scoped to the author's own OPT_DEBUG-enabled unit; a *stock* unit enforces no signature on load and accepts an unsigned, uncoded `.so` (the loader links no crypto; confirmed on-car). Nothing here is specific to any one vehicle — the descriptor, `PluginApp`, its vtable, and the value types are the generic *mechanics* of the RA-plugin ABI, written for a developer working on their **own** head unit.

Primary sources opened for this doc:

- **Framework binaries** (`nm -DC` / `nm -D` / `readelf -r` / `objdump -d`): `libAppFramework.A.so` (51 KB, ARM EABI5, stripped) and `libCoreFramework.A.so` (95 KB, ARM EABI5, stripped) from the HMI (`ID5`) `lib/` directory in the carve.
- **OEM reference plugin** `libSecurityMenu.so` (the `pluginAppInfo` descriptor proof, §2).
- **Reconstructed SDK headers** `bmw_abi.h` (minimal) and `bmw_list.h` (authoritative) — these are **hand-reconstructed** from the symbol tables above; method *signatures* and *mangled names* are **[VERIFIED]** against the binaries, but internal **field names** (`m_pConnector`, `m_f12`, `m_f20`, `m_buckets`, …) and some **byte offsets/sizes** (notably the `Parcel` 20-byte layout and `+12` vptr) are the author's reconstruction and are marked **[RECONSTRUCTED]** where they appear. BMW's real source may label them differently.
- **Compiled reference plugin** `libDiagnostics12.so` and its sources `diagnostics.cpp` / `diagnostics12.cpp` (the `VariantTag=34`, `Map` `17`/`10` immediates, `Runnable` weak-dtor emission, and `Delegate` `execImpl` thunks).

Where a claim could not be independently confirmed from the binaries — the loader's `abiVersion` major/minor split (the loader lives in `HmiMain3D`, not disassembled here), `VariantTag<TextID>=40`, vtable-slot return types, and whether `onError`/`onCheckAppAvailable` actually fire for RA plugins — it is labeled **[RECONSTRUCTED]** or called out as an open question in-place.
