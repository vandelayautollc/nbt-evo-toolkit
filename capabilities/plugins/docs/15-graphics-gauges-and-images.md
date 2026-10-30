# 15 — Graphics, Gauges & Images

What an RA plugin can actually put on screen — dials/gauges, custom images, custom drawing —
and which of it works for an **uncertified** plugin dropped in `data/ro/Plugins/` versus needing
coding/a certificate. Short version: a plugin gets a **numeric value control** (a bar/edit
widget, *not* a round dial) and a **generous raster-image path** (ship PNGs, or push a bitmap you
render yourself), both uncertified. It does **not** get a free-form drawing canvas, and it can
**neither reuse nor feed** the native engine sport-display gauges.

> **Scope & authorization.** Everything here was reverse-engineered from an **offline flash
> carve** and **owner-authorized** work on the author's **own titled NBT-Evo head unit**, running
> 100 % vanilla OEM firmware with only `OPT_DEBUG` enabled (system-service access; it does not
> change what the HMI accepts). No VIN, private network address, or car-specific diagnostic
> payload is part of this SDK. Build and test only on hardware you own.

> **Evidence legend.**
> **[CONFIRMED]** — read the disassembled logic, or direct byte/file evidence (a symbol, an RTTI
> class name, a string at an offset, an on-disk OEM file). Re-verified against the carve for this
> document where noted.
> **[STRONG]** — a structural fact (symbol-set intersection, a template family, "no cert string
> exists on this path") that forces the conclusion without a full instruction trace.
> **[PLAUSIBLE]** — an indirect reading the carve does not fully settle.
> **[UNKNOWN]** — the disassembly did not reach it; stated as an open question, not a guess.
>
> Addresses are `HmiMain3D` **file offsets** unless written as a vaddr; for this binary
> **vaddr = fileoff + 0x100000** (single R-E `LOAD` at vaddr `0x100000`, fileoff `0`). A few
> cross-referenced offsets in the source findings were quoted as vaddrs; they are reduced to file
> offsets here. Control-flow claims come from the lead's targeted ARM/capstone passes (host
> `objdump` cannot disassemble this ARM EABI5 binary; string refs use GOTOFF addressing); the
> string, symbol, RTTI and on-disk-file scaffolding around them was re-verified directly.

Related docs: **`03`** (DescFile grammar), **`04`** (menus/layout + property ids), **`05`** (C++
ABI & data types), **`06`** (runtime API), **`14`** (signing, coding & the permission bitset).

---

## 0. TL;DR — can a plugin do custom graphics / dials & gauges without reusing the sport displays?

**Yes for raster graphics and a numeric gauge; no for a round analog dial or a free-form canvas;
and the sport displays are neither reusable nor necessary.** In three parts:

1. **Dials & gauges — a plugin gauge exists, but it is not a round dial.** A plugin declares a
   `<raGaugeModel>` and binds it to a `<gauge>` component (`TAG_GAUGE` / `TAG_RAGAUGEMODEL`,
   `CRemoteAppGaugeModel` / `CAbstractGauge`). It is self-contained (the plugin owns
   value/min/max/increment), interactive, and needs **no certificate**. But the HMI has **no
   round/needle/arc/circular gauge widget at all** — every gauge-capable layout template is a
   **slider/bar** or an **edit-roll picker**. So a plugin can add an interactive *numeric value
   control*, not a speedometer-style dial. **[CONFIRMED that no round dial is declarable; STRONG
   on the exact widget family]**

2. **Custom images — yes, and this is the real "custom graphics" route.** A plugin ships its own
   PNGs in an `ImageDBFile` zip (addressed by numeric id) **and/or** pushes a **runtime-generated
   bitmap** through a `raImageModel` (`CRemoteAppImageModel::loadImageStreamResource`). Both are
   gated by certificate bits that **default to set**, so an uncertified `Plugins/` plugin passes
   every image gate. **If you want a truly custom-looking dial, you render it into a bitmap
   yourself and push it as a stream image** — that is the escape hatch, not the sport display.
   **[CONFIRMED for the static-PNG path; CONFIRMED the stream path exists; STRONG that an
   uncertified plugin can drive it end-to-end]**

3. **No free-form canvas, and the sport displays are off-limits.** The `<widget>` / CustomDraw
   element is **not** a plugin drawing surface — it binds by name to a widget BMW already compiled
   into the firmware, so a third-party plugin cannot author new draw content through it. And the
   engine power/torque **sport-display gauges are a native activity welded to a fixed car
   signal** — no DescFile identity, no widget to clone, and the HU cannot even feed a value into
   them. You do not reuse the sport displays; you cannot. **[CONFIRMED]**

**Bottom line for the SDK:** custom **raster** graphics (static + runtime-generated) are fully
available uncertified; a numeric **gauge** is available uncertified but renders in the platform's
bar/value style; custom **vector/canvas** drawing and the **sport dials** are native-only.
Anything richer than an image or the stock gauge means *rendering it yourself and shipping it as
pixels*.

---

## 1. Gauges & dials — `raGaugeModel` + `<gauge>`

A `<gauge>` binds a numeric `<raGaugeModel>` (an integer with `min`/`max`/`increment`) to an
on-screen control the user can read and adjust. Every gauge in the carve is a volume/tuner
control ("Lautstärke"). Unlike images, **a gauge needs no certificate** and works in an
uncertified `data/ro/Plugins/` plugin. **[STRONG]**

### 1.1 The important correction up front: there is no round-dial widget

The HMI has **no gauge widget class**. A grep of every layout-template name in `HmiMain3D` for
`Dial`/`Needle`/`Round`/`Arc`/`Circular`/`Gauge` returns **zero** round-gauge templates — the
only hits are the phone dialer (`CHmiLT_Button_Com_DialNumber_Entry`) and `…SearchResult` /
`…Background` false positives. Every gauge-capable template is a **slider/bar** variant
(`CHmiLT_Slider_1TextLeft_1TextRight`, `…_1IconLeft_1IconRight`, `…_2Row_*`,
`CHmiLT_SliderBar_Equalizer{Inner,Outer}`, `CHmiLT_Slider{Left,Right,Up,Down}Button_*`), and
there is no `eWidgetType_Gauge` / `CGfxWidgetGauge` in the widget enum or the vtable set.
**[CONFIRMED — `strings` scan, re-verified for this doc]**

So the honest answer to *"can we do a custom dial, or must we reuse the sport-display stuff?"* is
**neither**: a plugin `<gauge>` gives you an **interactive numeric value control**, and for an
actual round dial you must **render it yourself and ship it as a stream image** (§2.2), not use
`<gauge>` and not reuse the sport gauges (§5).

### 1.2 DescFile: `<raGaugeModel>` and `<gauge>`

Declared in `<models>`, then referenced by a `<gauge>` component. Both the flat-attribute and the
child-element forms are accepted (`CHmiGenStringConstants::TAG_RAGAUGEMODEL` @`0x039384e8`,
`TAG_GAUGE` @`0x03938590`).

```xml
<!-- in <models> -->
<raGaugeModel id="62" min="0" max="16" increment="1" value="1"/>                <!-- SecurityMenu.xml:140 -->
<raGaugeModel id="332" min="0" max="99995" increment="5" modelType="BigNumber" value="0"/> <!-- TVRemoteService:131 -->

<!-- in an <hmiState>'s <components> -->
<gauge id="108" model="62" text="Lautstärke innen" textModel="77"
       action="40" changeAction="41" previewModel="1019">                       <!-- SecurityMenu.xml:235 -->
  <tooltipText>Lautstärke innen</tooltipText>
</gauge>
```

**`<raGaugeModel>` attributes** (all integers):

| attr | meaning | evidence |
|---|---|---|
| `id` | model id the `<gauge model=…>` binds to | `SecurityMenu.xml:140` |
| `min` / `max` | value range (inclusive) | `SecurityMenu.xml:140`; `SecurityMenu_Editor.xml:17994` |
| `increment` | step size for one +/- press | `SecurityMenu.xml:140` |
| `value` | initial value (optional; defaults 0) | `TVRemoteService:125` |
| `modelType` | `""` (default) or a named type — **validated in native code** (§1.3) | `TVRemoteService:131` |

**`<gauge>` component attributes/children:**

| attr / child | role | evidence |
|---|---|---|
| `id` | component id (for `setProperty`) | `SecurityMenu.xml:235` |
| `model` | → the `raGaugeModel` id that holds the value | `SecurityMenu.xml:235` |
| `action` | raAction fired **on commit** (edit toggled off) | `SecurityMenu.xml:235`; `docs/03` §4 |
| `changeAction` | raAction fired **on each increment** while editing | `SecurityMenu.xml:235`; `docs/03` §4 |
| `text` | design-time label (author aid) | `SecurityMenu.xml:235` |
| `textModel` | → a `textIdModel`; the shown label/description | `SecurityMenu.xml:235` |
| `previewModel` | → an `raPreviewModel` for the split-screen preview pane (usually the "none" model) | `SecurityMenu.xml:235` |
| `imageModel` | optional icon (observed on a **toolbar**-hosted gauge only) | `TVRemoteService:161-166` |
| `<tooltipText>` | child element, spoken/hover text | `SecurityMenu.xml:236` |
| `<properties>` | generic component props (see `docs/04`, e.g. SELECTABLE) | grammar; cf. `docs/03` §9 |

`<gauge>.model` is a plain id reference into `<models>`; `changeAction` / `action` are ids of
`<raAction>` entries you bind at runtime (§1.5). **[CONFIRMED]**

### 1.3 What it renders as — a value control, in one of two families

**Corrected from the first-pass finding.** `CAbstractGauge::initGauge` does **not** build one
identical widget for every `modelType`. It constructs an object whose RTTI class name is
**`CAbstractEditLabelImpl`** (`22CAbstractEditLabelImpl` @`0x2e3ab84`, source
`…/abstractcomponents/CAbstractEditLabelImpl.cpp` @`0x2e3b158`) — an **editable numeric-value
control** — and, across its `modelType` branches, allocates objects of **two different sizes**
(three 164-byte and three 676-byte allocations in `initGauge`, `0x11c3800–0x11c42c0`). The
`modelType` therefore selects **which widget family** renders, not merely a number format:

- **Edit-label / slider family** (the volume default, plus `Balance`, `Progress`): a horizontal
  **value bar / slider** with a label and a value — the co-referenced template in the
  `CAbstractGauge.cpp`/`CAbstractSliderImpl.cpp` literal region is
  `CHmiLT_Slider_1TextLeft_1TextRight` (a track with fill/thumb, a left text area and a right text
  area). `CAbstractSliderImpl` (`19CAbstractSliderImpl` @`0x2e39d28`) provides the
  increase/decrease/toggle-edit machinery. **[STRONG — the slider is the visual involved; the
  object `initGauge` constructs is `CAbstractEditLabelImpl`, and the exact edit-label↔slider
  composition was not fully disassembled]**
- **Roll-picker family** (`Date`, `Time`, `BigNumber`): a **spinning edit-roll** driven by a
  roll helper — `CRhmiBigNumberRollHelper` (`24CRhmiBigNumberRollHelper` @`0x2e3ac10`),
  `CRhmiDateRollHelper` (@`0x2e3abc8`), `CRhmiTimeRollHelper` (@`0x2e3abec`), plus
  `CRhmiConfigurableRollHelper`. `CAbstractEditLabelImpl::init` logs *"Created EditRoll with
  type=%d (%s)"* (@`0x2e3b38c`) and the BigNumber helper logs *"Initialised EditRoll_BigNumber
  helper"* (@`0x2e3b105`); the corresponding native states are `CHmiLT_State_EditRoll_BigNumber`,
  `…_Regular`, `…_Standard_Set_Date`, `…_Standard_Set_Time`, etc. So **`modelType="BigNumber"`
  is a distinct roll-picker widget, not "the same slider with a different number format"** — a
  correction to the initial finding. **[CONFIRMED that BigNumber routes to a roll helper;
  PLAUSIBLE on the precise per-token→family branch mapping, which was inferred from alloc sizes +
  the roll-helper class set, not branch-traced]**

**`modelType` accepts more than `BigNumber`.** The `initGauge` `strcmp` cascade validates a set of
named tokens and rejects anything else with *"Invalid gauge model type '%s'!"* (@`0x2e398aa`).
The tokens the disassembly resolved are **`Balance`, `Progress`, `Date`, `Time`, `BigNumber`**
(plus the empty default). Independently here, `Balance` (@`0x2b1c2f1`) and `BigNumber`
(@`0x2e1a060`) verify as clean standalone strings and the `Date`/`Time`/`BigNumber` roll-helper
classes are present; the OEM DescFiles only ever use the default and `BigNumber`, so the *carve
usage* is narrow while the *binary acceptance* is wider. **[STRONG — five-token set from the
`strcmp` trace; `Balance`+`BigNumber`+roll-helpers independently confirmed; some operands land
mid-blob in a merged string table and were not each re-cleaned here]**

> **Takeaway.** A plugin `<gauge>` is a **bar / editable-value / roll control — never a round
> analog dial.** The `modelType` you almost always want is the default (a value bar) or, for a
> large numeric entry, `BigNumber` (a rolling number).

### 1.4 Indicator vs. interactive

Interactive by default. The user toggles edit mode, then `+`/`-` steps the value (debounced
500 ms — `TDebouncedSlider<…,500>` @`0x2b1a490`); **each step** fires `changeAction`
(`onGaugeChangeActionInternal` @`0x2e50b84`) and **committing** fires `action`
(`onGaugeActionInternal` @`0x2e50ba0`), both through `IAbstractGaugeImpl` (@`0x2e50bb8`). Boost
binds of `onToggleEdit` / `onIncreaseValue` / `onDecreaseValue` sit in the same region
(@`0x2e39b88`/`98`/`a8`). To use a gauge as a **read-only indicator**, omit `changeAction` /
`action` and just push values with `updateModel`. **[CONFIRMED — the machinery; STRONG on the
exact edit-mode state machine, which was not disassembled]**

### 1.5 C++: driving and reading a gauge

The value is an **integer** in `[min,max]`. Seed/update it from the UI thread with the scalar
`updateModel` overload; receive user changes by binding the `changeAction` (and/or `action`) with
`addHandler`, reading the new value from the handler's `Parcel`.

```cpp
// --- DescFile ids (from <Name>.xml) ---
enum { MDL_VOL = 62, GAUGE = 108, ACT_COMMIT = 40, ACT_CHANGE = 41 };

bool MyApp::onInit() {
    updateModel(MDL_VOL, (int)current_volume_);          // seed the value   (libAppFramework 0x521c)

    bmw::Delegate<bool, const bmw::Parcel&> d;           // bind the live-change action
    d.m_obj  = this;
    d.m_exec = &bmw::Delegate<bool, const bmw::Parcel&>::execImpl<MyApp, &MyApp::onVolChange>;
    addHandler(ACT_CHANGE, d);                           // per-increment    (addHandler 0x5970)
    // bind ACT_COMMIT the same way if you only need the final value
    return true;
}

// fires on every +/- step; p carries the new gauge value
bool MyApp::onVolChange(const bmw::Parcel& p) {
    int v = 0;
    if (!p.readInt32(v)) { unsigned u = 0; if (p.readUInt32(u)) v = (int)u; }  // Parcel 0xc0a8
    current_volume_ = v;
    apply_volume(v);
    return true;                                         // consumed
}
```

- **Set** with `updateModel(unsigned,int)` @`0x521c` (or `updateModel(unsigned,unsigned)`
  @`0x51fc`); the value is clamped to the model's `min`/`max`. Gauge value→track fraction uses
  `vcvt.f32.u32` at `0x11c4028`/`0x11c4188`. **[CONFIRMED — `nm -DC libAppFramework.A.so`]**
- **Read** the change with the same `Delegate<bool,const Parcel&>` + `addHandler` mechanism used
  for list rows; the value comes out of the `Parcel` via `readInt32`/`readUInt32` (idiom:
  `diagnostics5.cpp:82`). The exact gauge-value `Parcel` encoding was inferred from the shared
  action/Parcel dispatch, not byte-traced end to end — **[STRONG]**. See `docs/05` §Parcel and
  `docs/06` §B.2.
- HMI-side classes: `CRemoteAppGaugeModel` (`20CRemoteAppGaugeModel` @`0x2e14ee8`),
  `CRemoteAppGaugeModelFactory`, `IRemoteAppGaugeModelListener` (`28IRemoteAppGaugeModelListener`
  @`0x2e3a204`) — the per-`raGaugeModel` proxy the framework registers; you touch it only
  indirectly through `updateModel` / `addHandler`. **[CONFIRMED]** See `docs/05` for the class
  layout.

### 1.6 Permission verdict — no certificate or coding required

**[STRONG]**

- The 184-bit capability bitset (`docs/14` §4.4) has **no gauge/slider index**; the 9-index
  privileged denylist `{13–18,20,21,22}` is focus/map/voice/notification, none gauge-related.
- The only models with a certificate gate are the **image** models (§2.3); **no
  "…not allowed by certificate" string exists for gauge or slider** anywhere in the binary.
- Disassembly of `CAbstractGauge::initGauge` (`0x11c3800–0x11c42c0`) shows **no call into any
  `CRhmiApplicationPermissions` / `Auth` accessor** on the gauge path (a few unnamed internal
  helpers were not recursed into, which keeps this **STRONG** rather than CONFIRMED).

So a `<gauge>` behaves like the permissive-default capabilities: fully usable by an uncertified
plugin, subject only to the loader's optional *load*-time policy hook (`docs/14` §2.3), which
gates loading, not gauges specifically. A coded/certified plugin gains **nothing** extra for
gauges.

---

## 2. Images — ship PNGs, or push a bitmap you render yourself

A plugin has exactly **one** mechanism for *its own pixels*: the **image models**
(`CRemoteAppImageModel`, `20CRemoteAppImageModel` @`0x2e14b28`). Two flavors, both uncertified.

### 2.1 Static PNGs by numeric id — the `ImageDBFile` (supported path) — [CONFIRMED]

The manifest declares an **`ImageDBFile`**, a plain `.zip` of PNGs named by **numeric id**:

```xml
<!-- manifest -->
<ImageDBFile>{pluginDir}/MyApp_ALL_Images.zip</ImageDBFile>
```
```
MyApp_ALL_Images.zip
 ├── 55010.png
 ├── 55011.png
 └── 55014.png
```

In the DescFile you declare an **image-id model** and bind it to an `<image>` component (or a
button's `imageModel`):

```xml
<models>
  <imageIdModel id="169" imageId="55011"/>   <!-- fixed: resolves 55011.png -->
  <imageIdModel id="164"/>                    <!-- mutable: id chosen at runtime -->
</models>
...
<image id="165" model="164">
  <properties>                                <!-- layout props, see docs/04 -->
    <property id="20" value="493"/> <property id="21" value="163"/>  <!-- x, y -->
    <property id="9"  value="246"/> <property id="10" value="443"/>  <!-- w, h -->
  </properties>
</image>
```

`imageId="N"` → `N.png` inside the zip — verified on-disk. The decode path is **DevIL/ILU**
(`HmiMain3D` `NEEDED` `libDevIL.so` + `libILU.so`; `ilLoadImage`; libpng error strings present),
and images scale to the component's width/height. The zip is read by
`HmiGen_CRemoteAppImageModel_loadImageIdResource` (@`0x2e1ec02`); a bad zip logs *"ImageDB is not
a Zip file, or broken"* (@`0x2dfa6ad`). **[CONFIRMED]**

> **Note on the on-disk example.** `ActiveSeating` declares **five** static `imageId`s
> (`55010–55014`, `ActiveSeating.xml:70–95`) but its zip ships **ten** PNGs
> (`55002,55004,55006,55008,55009,55010–55014`). The extra five are the large seat-illustration
> images selected **at runtime** through the mutable `imageIdModel id=164` (`setImage(id)` →
> `loadImageIdResource`) — a correction to the first-pass "exactly 55010–55014" note, and a good
> illustration of the runtime-chosen-id path. **[CONFIRMED — `unzip -l`]**

There is also an **`ImagePath`** manifest parameter (`{pluginDir}/Bitmaps/`) holding *named*
PNGs. These are **not** referenced from the DescFile (grep of `ActiveSeating.xml` for the shipped
`rse_active_seating_*` filenames = 0) — they feed the **native** widget you bind by name (§3), not
your `<image>` components. **For a plugin's own graphics, use the `ImageDBFile` + `imageId`.**
**[CONFIRMED / STRONG on `ImagePath`'s native-consumer role]**

### 2.2 Runtime-generated bitmaps by stream — the custom-graphics escape hatch — [CONFIRMED path]

`CRemoteAppImageModel` (declared `<raImageModel>`) has a **second** loader beside the id path:
`HmiGen_CRemoteAppImageModel_loadImageStreamResource` (@`0x2e1ec32`). From C++ you set the model's
image to a **raw bitmap you generated at runtime** — draw a needle, a graph, a custom dial, hand
over the pixels. **This is the real "custom graphics" capability, and the way to get a
custom-looking gauge.** ActiveSeating declares such mutable models (`<imageIdModel id=164/>`,
`<raImageModel id=167/>`); SecurityMenu declares `<raImageModel id=7/8/22>`.

Constraints read from the binary:

- a **per-model dynamic flag** — declare the model dynamic-capable or you hit *"Dynamic images not
  allowed for model %u.%u!"* (@`0x2e1eb84`); its origin (DescFile attribute vs. C++ setup) was
  not fully traced — **[STRONG that DescFile declaration suffices; PLAUSIBLE on the flag origin]**;
- a **byte-size cap** — oversize pushes hit *"Image data (%u Bytes) too large!"* (@`0x2e1e83c`);
  the exact cap value was not resolved — **[UNKNOWN]**;
- the certificate gate *"Images from streams are not allowed by certificate!"* (@`0x2e1ea5d`),
  which an uncertified plugin **passes** (§2.3).

The exact C++ call to push a stream bitmap (`CRemoteAppImageModel` setter signature, buffer/pixel
format) is `docs/06` territory and was not extracted here; the model and its loader are confirmed,
but *an uncertified plugin driving the stream push end-to-end* is inferred from the passed cert
gate, not demonstrated. **[STRONG]**

### 2.3 Why the image gates don't stop an uncertified plugin — [CONFIRMED]

There are exactly **three** *"not allowed by certificate"* image strings, and they map to three
default-**set** permission bits:

| string | offset | permission (docs/14) | default |
|---|---|---|---|
| `[RemoteAppImageModel] Images are not allowed by certificate! (AppId=%u)` | `0x2e1e881` | `Image` (idx 2) | **set** |
| `[CRemoteAppImageModel] Images from ImageIDs are not allowed…` | `0x2e1ea11` | `ImageStatic` (idx 1) | **set** |
| `[CRemoteAppImageModel] Images from streams are not allowed…` | `0x2e1ea5d` | `ImageDynamic` (idx 0) | **set** |

`CRhmiApplicationPermissions` defaults **permissive** — all 184 bits set minus the 9-index
denylist `{13–18,20,21,22}` (`docs/14` §4.2). Image bits `0/1/2` are **outside** the denylist, so
an uncertified `Plugins/` plugin passes every image gate; these warnings can only fire when a
**certificate clears** a bit. The gate is real logic, not a string: `setImage`
(`0x1133a60–0x1133e10`) caches a flags byte at `model+0x14` and `tst`s masks `0x40`/`0x20`/`0x04`
before each string, and those three cert-string pointers sit in that function's literal pool.
**[CONFIRMED that three flag-bit tests guard those exact strings inside `setImage`; STRONG on the
exact permission-index label for each — the `0x40/0x20/0x04` cache masks don't map 1:1 to indices
`0/1/2`, so the label↔bit mapping is inferred from `docs/14`, not single-stepped. All three default
set regardless, so the "uncertified CAN" verdict is unaffected.]**

### 2.4 Formats

**PNG is confirmed** shipped and decoded (all plugin images are `.png`; DevIL `ilLoadImage`;
libpng chunk/size error strings present). DevIL can also decode JPG/BMP/TGA/GIF, so non-PNG raster
in the `ImageDBFile` is **[PLAUSIBLE]** but untested in this carve. Component sizing is via the
layout properties (`docs/04`: `id=9` width / `id=10` height / `id=20` x / `id=21` y), e.g.
ActiveSeating's `1440×810` fullscreen and `246×443` insets. **[CONFIRMED for PNG]**

---

## 3. The CustomDraw `<widget>` — a named native container, not a canvas — [CONFIRMED]

It is tempting to read `<widget>` as "draw whatever I want." **It is not.**

`CGfxWidgetCustomDraw::createWidget()` is a **native container** that instantiates **child widgets
from a fixed compiled palette** — its failure string is *"[CGfxWidgetCustomDraw - createWidget()]:
Could not create child widget type \"%s\"!"* (@`0x2b00b8c`), source `CGfxWidgetCustomDraw.cpp`
(@`0x2b00790`), driven from C++ by `CHmiWidgetCustomDrawCommand`
(`27CHmiWidgetCustomDrawCommand` @`0x2f7e03c`). The palette is the compiled `eWidgetType_*` enum
(`Image`, `Rectangle`, `Text`, `DrawArea`, `Box`, `ScrollArea`, `NinePartImage`, `ExternalImage`,
`ImageAtlasAnimation`, `WidgetCustomDraw`, …). **None of that is authored from a plugin
DescFile.**

What a plugin's `<widget>` actually does is **bind, by name, to a widget BMW already compiled into
the firmware's layout tree** and feed it data:

```xml
<widget id="187" widgetName="LT_Table_RSE_ActiveSeating">   <!-- native, OEM-compiled -->
  <bindings>
    <binding key="GaugeLeftValue"      valueModel="190"/>   <!-- feed data only -->
    <binding key="IllustrationVisible" valueModel="194"/>
  </bindings>
</widget>
```

Decisive evidence it is name-bound to compiled native classes, not plugin content:

- Every `<widget>` in `ActiveSeating.xml` points at an OEM name
  (`LT_Table_RSE_ActiveSeating`, `…_Intro`, `…_End`, `LT_State_RSE_FullScreen_ActiveSeating`) and
  ships **zero draw commands** — only `<binding>` keys and layout `<property>`. Those names resolve
  to **compiled C++ classes** in `HmiMain3D` (`N12uiinterfaces…CHmiLT_Table_RSE_ActiveSeating`,
  `…_Intro`, `…_End`, `CHmiLT_State_RSE_FullScreen_ActiveSeating`). A third-party plugin **cannot
  add a new native widget class**, so `widgetName="something_i_invented"` resolves to nothing.
  **[CONFIRMED]**
- The `<binding>` `key` names (`GaugeLeftValue`, `GaugeRightValue`, `BraceLeftEnabled`, …) are
  **specific to each named native template** (they are that template's parameter names), not a
  generic vocabulary — see `docs/03` §9. **[CONFIRMED]**
- The DescFile tag set (`CHmiGenStringConstants::TAG_*`) contains **no** `TAG_CUSTOMDRAW`,
  `TAG_DYNGFX`, `TAG_DRAWAREA`, or `TAG_CANVAS`. The graphics tags a plugin can declare are only
  `TAG_IMAGE`, `TAG_IMAGEIDDATAMODEL`, `TAG_RAIMAGEMODEL`, `TAG_GAUGE`, `TAG_RAGAUGEMODEL`,
  `TAG_WIDGET`. **[CONFIRMED]**

**The wall on custom drawing is native layout-DB availability, not a permission bit.** There is
**no** cert string for `widget`, `gauge`, `customdraw`, or `dyngfx` — so `<widget>` instantiation
is not permission-gated. `ActiveSeating` happens to be a **coded/certified** plugin
(`PluginsCoded/`, `.p12`/`.p7b`, `applicationType="Custom"`), but its use of `<widget>` needs no
permission an uncertified plugin lacks — it needs the **native template name**, which the OEM
shipped alongside that app, not a certificate. **[CONFIRMED that no cert gate applies to
`<widget>`; STRONG that it therefore works regardless of permissions, bounded only by native
availability]**

**`DynGFX` / `DynGFX3D`** (the dynamic-graphics / hotspot mechanism —
`CDynGfxTraversal`, `CDynGfx3DTraversal`, `CHotSpot*Traversal`, `CDocumentTraversal::DYNGFX`) is a
**native scene-document render-pipeline traversal**, with **no** corresponding DescFile tag and no
plugin-facing binding — **not plugin-declarable**. **[STRONG]**

> Note: `TAG_SURFACECOMPONENT` also exists in the tag set and was not characterized here. It is
> not a draw/canvas tag (likely a native video/graphics surface); whether it is plugin-declarable
> and what it renders is **[UNKNOWN]** (§6).

---

## 4. Capability table

| Graphics feature | How declared (DescFile) | Renders what | Permission bit | Uncertified `Plugins/` plugin CAN? | Grade |
|---|---|---|---|---|---|
| **Numeric gauge / value bar** | `<raGaugeModel>` + `<gauge>` (default `modelType`) | horizontal **value bar / slider** with label+value (editable) | none — no cert string on gauge path | **✅ Yes** (platform style, **not** a round dial) | STRONG |
| **Roll-picker gauge** | `<gauge>` with `modelType="BigNumber"` (also `Date`/`Time`) | spinning **edit-roll** number/date/time picker | none | **✅ Yes** | STRONG (path) / PLAUSIBLE (per-token family) |
| **Round analog dial** | — (no tag; no `eWidgetType_Gauge`) | — | — | **❌ No** — render it yourself + stream image | CONFIRMED |
| **Image by id (static)** | `<imageIdModel imageId=N>` + `<image>`; ship `N.png` in `ImageDBFile` | your PNG, scaled to component w/h | `Image`(2)/`ImageStatic`(1) — default **set** | **✅ Yes** | CONFIRMED |
| **Image by id (runtime-chosen)** | `<imageIdModel id=X>` (no `imageId`); C++ `setImage(id)` | your PNG, selected at runtime | same as above | **✅ Yes** | CONFIRMED (path) / STRONG (exact bit) |
| **Image by stream (dynamic)** | `<raImageModel>`; C++ push raw bitmap → `loadImageStreamResource` | **runtime-generated pixels** (custom dial, graph, needle) | `ImageDynamic`(0) — default **set**; + per-model flag + size cap | **✅ Yes** (size-limited) | CONFIRMED (path exists) / STRONG (end-to-end) |
| **`<widget>` / CustomDraw** | `<widget widgetName=X>` + `<binding>` | a **pre-authored native** widget named `X` | none — no cert string for widgets | ⚠️ **Only if `X` exists in firmware**; cannot author new draw content | CONFIRMED (no gate) / STRONG (name-bound) |
| **DynGFX / DynGFX3D** | *(no DescFile tag)* | native scene-graph dynamic graphics + hotspots | n/a — not plugin-declarable | **❌ No** | STRONG |
| **Engine sport-display gauges** | *(no DescFile tag / identity)* | native power/torque round needles (fixed car signal) | n/a — native activity | **❌ No** (neither instantiate nor feed) | CONFIRMED |

The only *"not allowed by certificate"* strings on any **graphics** path are the three image ones
(§2.3). (The binary does gate other, non-graphics things by certificate — e.g. an `RHMI popup not
allowed` string at `0x2e16300` — so "images are the only cert-gated feature" would be wrong; but
for **graphics**, image is the only cert-gated path.) **[CONFIRMED]**

---

## 5. Sport displays vs. plugin gauges — why you don't (and can't) reuse them

**"Reuse the sport-display stuff" is not a path for a plugin, and you would not want it to be.**

### 5.1 The sport display is native and vehicle-bound — unreachable from a DescFile

The engine power/torque gauges are drawn by **`CCarInstrumentsOfSportActivity`**
(`30CCarInstrumentsOfSportActivity` @`0x2c9686c`, source
`../../src/hmi/app/hmimycar/CCarInstrumentsOfSportActivity.cpp` @`0x2c9692b`), a **compiled HMI
activity** on the native state `ST_MyV_DrivingExcitement_InstrumentsOfSport` (@`0x2c9139b`). Its
device `CDevCarInstrumentsOfSport` subscribes the inbound **"Vehicle" DSI/CommonAPI** attributes
`3194`/`3195`/`3304`; the needle carrier is **id `3195` / `0xC7B`** (`power = byte+0x79`,
`torque = byte+0x78`, each `0–100 %` of full scale, `0xFF` = invalid) on the `CPxyVehicle` proxy.
The activity applies a `×0.01` scale and writes the named float resource keys
`current_value_power` (@`0x2c968b0`) / `current_value_torque` (@`0x2c968c4`) into the sport
screen's own composer scene. **[CONFIRMED — byte-traced from the sport-display data path in
your own carve; the device subscribes three attributes, with `3195` the power/torque carrier —
not "exactly one"]**

Two facts make it **unreachable from a DescFile**:

- **No XML identity.** A grep of *every* OEM DescFile (`data/ro/*.xml`, `PluginsCoded/`,
  `hmiplugins/`) for `InstrumentsOfSport`, `SportActivity`, `CarInstruments`,
  `current_value_power`, `current_value_torque`, `DrivingExcitement` returns **zero hits**. There
  is nothing to name. **[CONFIRMED]**
- **No gauge widget to clone.** No `eWidgetType_Gauge`, no `CGfxWidgetGauge` (§1.1). The needle is
  a bespoke asset of the sport scene, not a reusable widget class. **[CONFIRMED]**

You also cannot push data **into** it: the HU is a **pure SOME/IP client** of the Vehicle service
(it *subscribes* to id `3195`; it cannot *provide* it), and no DescFile binding key targets the
sport resource keys. **The native gauge screens are closed to plugins in both directions.**
**[CONFIRMED / STRONG]**

### 5.2 The plugin gauge is a bar/roll control — it won't look like the sport needle

Because there is no gauge widget class, the `<gauge>` component (`CAbstractGauge`) fetches a
generic UI object from the theme (*"Could not get HmiUIObject for CAbstractGauge with id %u"*
@`0x2e39904`), turns its numeric value into a float scale factor (`gaugeValueToScaleValue` — a
compiled symbol occurring ~14× in `.rodata`, **not** a theme script) feeding generic
`eWidgetType_Scaling`/`_Transform` assets. The presentation the ROM ships **for the RA `<gauge>`
path** is the **value bar + glow** (`common/script/sliderGauge.lua`: `barSize.x = value*2`,
`glowSize`), and every OEM instance is a volume/tuner slider. **[STRONG — mechanism; "no needle
skin reachable by a bare `<gauge>`" is STRONG, absence not exhaustively provable]**

> The theme *does* contain other native gauge renderings (e.g. an OnBoardComputer `obc_gauge`
> shader + `gauge_quad_shape` mesh, and a ClimateComfort air-quality gauge mesh), but they are
> tied to their own native devices and were **not** shown to be selectable by a plugin's
> `<gauge>`. So "the value bar is the only gauge look" is scoped to *the RA `<gauge>` path*, not to
> the whole ROM. **[STRONG]**

The sport dial's polished needle lives in the sport screen's dedicated composer scene, keyed to
`current_value_*` — **it cannot be borrowed** by a plugin gauge.

### 5.3 So: dials/gauges — reuse the sport display, or not?

**Neither required nor possible.** Your two real options:

1. **Numeric `<gauge>`** (`raGaugeModel` + `gauge`) — a genuine plugin-declarable interactive
   gauge; uncertified; but it renders in the **platform's** bar/roll style, **not** a round dial.
2. **Self-render + stream image** (§2.2) — draw the dial exactly how you want into a bitmap and
   push it through a `raImageModel` (`loadImageStreamResource`). **This is the path to a fully
   custom-looking dial**, and it is uncertified. Trade-off: you own the rendering and live within
   the stream size cap and refresh cost.

The higher-privilege middle option — binding a native `<widget widgetName=…>` that already
contains gauge artwork (as `ActiveSeating` does with `GaugeLeftValue`/`GaugeRightValue`) — needs a
**native template that exists in the ROM** and, in the one OEM exemplar, ships as a
coded/certified plugin (§3). Still not the sport display.

---

## 6. Open questions / how to settle them

| # | Open question | Grade | How to settle it |
|---|---|---|---|
| 1 | Exact `modelType`→widget-family branch mapping in `initGauge` (which token → 164-byte roll vs 676-byte edit-label/slider). | [PLAUSIBLE] (inferred from alloc sizes + roll-helper class set) | CFG-trace the three-way branch from each `strcmp` hit to its `new`/ctor site. Confirms whether `Balance`/`Progress` are edit-label/slider and `Date`/`Time`/`BigNumber` are roll pickers. |
| 2 | The full accepted `modelType` token set. Five (`Balance`,`Progress`,`Date`,`Time`,`BigNumber`) were read from the `strcmp` cascade; some operands land mid-blob in a merged string table. | [STRONG] | Resolve each `strcmp` literal-pool operand to a clean interned string; confirm none is a Variant-type assert rather than a `modelType`. |
| 3 | Exact `Parcel` byte-encoding of the value delivered to a gauge `changeAction` handler (`readInt32` vs `readUInt32` vs `readFloat32`). | [STRONG] (inferred from shared action/Parcel path) | On-target: bind `changeAction`, log the raw `Parcel`, confirm the accessor. |
| 4 | The stream/dynamic-image **byte-size cap** value (*"Image data too large"*). | [UNKNOWN] | Resolve the comparison immediate near the size-cap string load; or push increasing bitmaps on-target. |
| 5 | Origin of the per-model **dynamic-image flag** (DescFile attribute vs required C++ setup), and the exact `CRemoteAppImageModel` stream-push C++ signature. | [STRONG] (declaration suffices) / [UNKNOWN] (ABI) | Extract the setter overload in `docs/06`; trace where the `model+0x3d/+0x3e` dynamic bits are set. |
| 6 | Whether **any** native `widgetName` is realistically reachable/useful to a generic third-party plugin (the `LT_*` names are app-specific compiled classes with their own binding keys). | [PLAUSIBLE: practically no] | Enumerate `N12uiinterfaces…CHmiLT_*` classes and their binding keys; identify any generic gauge/table template not tied to a specific OEM app. |
| 7 | `TAG_SURFACECOMPONENT` — is it plugin-declarable, and what does it render? | [UNKNOWN] | Find the parser handler for `TAG_SURFACECOMPONENT` and its component class; likely a native video/graphics surface. |
| 8 | Non-PNG raster (JPG/BMP/TGA/GIF) support in the `ImageDBFile`. | [PLAUSIBLE] | Ship a non-PNG in a test `ImageDBFile` and observe DevIL decode on-target. |
| 9 | Whether any ROM theme container exposes a **rotary-needle** presentation selectable by a bare `<gauge>`. | [STRONG: no] (absence not exhaustively proven) | Enumerate every theme layout package bound to `CAbstractGauge`; confirm all are slider/edit-roll. |

---

## 7. Sources & method

- **Owner-authorized, offline-carve reverse engineering** of the author's own titled NBT-Evo head
  unit (100 % vanilla OEM firmware, `OPT_DEBUG` for system access only). No hardware was touched;
  this is a static read of a flash carve.
- **Binaries / files** (under
  `opt/hmi/ID5/`):
  `bin/HmiMain3D` (ARM32, RTTI class-name strings + 13 422 dynsym; `NEEDED` `libDevIL.so`,
  `libILU.so`); `lib/libAppFramework.A.so` (`updateModel`, `addHandler` exports);
  `data/ro/PluginsCoded/{SecurityMenu,ActiveSeating}/*.xml` + `ActiveSeating_ALL_Images.zip`;
  `data/ro/hmiplugins/HmiGen_TVRemoteService.xml`; `data/ro/common/script/sliderGauge.lua`.
- **Sport displays:** prior reverse-engineering of the sport-display data path and source ECU
  (relied upon for the DSI `3195` data path, not re-derived here).
- **Method.** Structural facts (RTTI class names, `TAG_*` symbols, `NEEDED` lists, on-disk zips,
  string offsets) were verified directly with `strings -a -t x`, `nm -DC`, `readelf -d`,
  `unzip -l` and `grep`, and re-verified against the carve while writing this document — including
  independent confirmation of: the absence of any round-gauge template, the `CAbstractEditLabelImpl`
  / roll-helper class set, the three image cert strings, and the ten-PNG `ImageDBFile`.
  Control-flow claims (`initGauge`'s alloc/branch structure, `setImage`'s flag-bit gates, the
  gauge action dispatch) come from the lead's targeted ARM/capstone passes (host `objdump` cannot
  disassemble this ARM EABI5 binary). All three research angles (gauges, images/custom-draw,
  sport-display comparison) were adversarially verified; **where a verifier refuted or downgraded a
  claim, the corrected grade is used here** — notably: the gauge impl is `CAbstractEditLabelImpl`
  (not `CAbstractSliderImpl`), `modelType` accepts more than `BigNumber`, `BigNumber` is a
  roll-picker (not the slider re-formatted), and the sport-display device subscribes three
  attributes (not one).
- **Confidence is graded on every material claim** per the legend at the top. An explicit
  **[UNKNOWN]** with a way to settle it (§6) is preferred over invented certainty.
