# 03 — The DescFile (`.xml`) Reference

> Complete, source-grounded grammar reference for the NBT-Evo HMI RA-plugin
> DescFile (`.xml`): every element, attribute, and enumeration, cross-checked
> against the OEM `SecurityMenu` / `ActiveSeating` DescFiles, the `HmiMain3D`
> parser tokens, and a working example plugin.

> **Scope & authorization.** This document describes the *generic* grammar of the
> NBT-Evo HMI "RA plugin" DescFile, reverse-engineered from an offline flash carve
> and owner-authorized work on the author's own titled vehicle. It is written for a
> developer building a plugin for **their own** head unit. Nothing here is
> car-specific: no VIN, network address, or private diagnostic detail is part of
> the SDK.

The **DescFile** is the second of the three artifacts that make up an RA plugin
(see `01-architecture-and-loading.md`). It is a plain XML file named by the
`<DescFile>` parameter of the plugin's `.manifest` (see `02-manifest-format.md`,
e.g. `<DescFile>{pluginDir}/Diagnostics.xml</DescFile>`). At HMI start the loader
in **HmiMain3D** parses it and builds the plugin's entire *declarative* UI: its
menu entry, its screens, the components on those screens, the data models the
components bind to, and the action ids that route user input back into your `.so`.
Your compiled code (this doc covers the XML; the C++ side is
`05-cxx-abi-and-data-types.md`) never creates widgets directly — it only *fills models*,
*flips properties*, and *handles actions*, all keyed by the numeric ids you assign
here.

> **This file is not the `<Bundle>` format.** The `.xml` files under
> `data/ro/hmiplugins/` (`A4APlugin.xml`, `RemotingPlugin.xml`) use a completely
> different `<Bundle exportedSymbolName=… ><Plugin implementedInterface=… >`
> schema — those are the RHMI/remoting **Bundle** descriptors (`RemotingPlugin.xml`
> loads `libhmiremoting.so`), a *separate loading mechanism* from **both** the
> RA-plugin framework this doc teaches **and** the in-process device-abstraction
> layer (`libhmiplugin.so` / `THmiPluginProxy`). They are **not** RA plugins and
> are out of scope here (see `01-architecture-and-loading.md`).

---

## 0. Status legend

Every non-trivial claim below is tagged:

| Tag | Meaning |
|-----|---------|
| **CARVE** | Confirmed directly in an OEM DescFile shipped on the unit (`SecurityMenu` / `ActiveSeating`). |
| **PARSER** | The element/attribute name is a literal token inside the `HmiMain3D` binary's DescFile parser. |
| **EXAMPLE** | Present in the working example plugin (`Diagnostics.xml`) but not (yet) seen in an OEM file. |
| **RECON** | Inferred/reconstructed (e.g. semantics of a numeric id that ships without its symbolic name). Treat as a good hypothesis, not gospel. |

Two carve facts frame everything:

1. **The DescFile ships in *numeric* form.** OEM plugins are authored in a
   symbolic "Editor" file (`SecurityMenu_Editor.xml`) that `#include`s constant
   headers (`PropertyTypes.h`, `CPeerLayoutSet.h`, …) and uses names like
   `VISIBLE`, `SELECTABLE`, `ACT_SEC_Haupttafel`; a build step resolves those to
   the integers you see in the runtime `SecurityMenu.xml`. The symbolic property
   names **do** appear inside `HmiMain3D`, but *only* as human-readable labels
   embedded in log/diagnostic format strings (e.g.
   `[AbstractSeparator::setProperty] %u.%u -> Property SELECTABLE ignored for separator`,
   `Setting POSITION_X of component %u.%u …`, `property HMISTATE_TABLETYPE not allowed`) —
   **not** as a runtime symbol→id lookup table. The DescFile parser keys on the
   numeric ids alone, so you author the numeric form directly. (**PARSER**; the one
   exception is `BACKGROUND`, which is absent from the binary's strings entirely.)
2. **All DescFile element names are literal parser tokens.** Every element listed
   in this doc was verified to exist verbatim inside `HmiMain3D`, so the grammar
   here is the grammar the loader actually accepts, not a guess.

---

## 1. The id namespace model (read this first)

Within a single `<pluginApp>` there is **one flat unsigned-integer id space**.
Component ids, action ids, model ids, state ids and event ids are all drawn from
it and **must be unique across the whole `<pluginApp>`**. (In OEM files the ids are
simply a monotonically increasing counter assigned by the editor; in the example
they are grouped by hand — entry `1`, actions `10–27`, models `50–52`, components
`2–13` — purely for readability. **CARVE/EXAMPLE**)

There are **four kinds of id**, and the whole reason the DescFile exists is to let
your C++ reference UI by number:

| Id kind | Declared by | Referenced from a component via | Bound in C++ (`06`) by |
|---------|-------------|----------------------------------|------------------------|
| **hmiAction** | `<hmiAction id=… target=…>` | `action="<id>"` | *nothing* — handled entirely in-HMI (navigates to `target` state). |
| **raAction** | `<raAction id=…>` | `action="<id>"` or `changeAction="<id>"` | `addHandler(actionId, delegate)` / `addHandler(stateId, actionId, delegate)`. |
| **model** | any `<ra*Model>` / `<*IdModel>` | `model="<id>"`, `imageModel=`, `previewModel=`, `valueModel=`, … | `updateModel(modelId, data)`. |
| **component** | any component element's `id=` | (targeted, not referenced) | `setProperty(componentId, propId, parcel)`. |

So a button `<button id="4" action="22" text="Read DTCs"/>` says: *component 4,
when pressed, fires action 22.* Because 22 is declared as a `<raAction>`, the press
is delivered to whatever your code registered with `addHandler(22, …)`. Had 22
been an `<hmiAction id="22" target="300">`, the press would instead just navigate
to state 300 and your code would never see it. **CARVE** (`Diagnostics.xml:22–29`,
`Diagnostics.xml:71`) + **RECON** for the exact dispatch, corroborated by the
handler wiring in `diagnostics12.cpp:329–347` (not proven by disassembly).

---

## 2. Element nesting tree

```
pluginApps                         (root, one per file)
└── pluginApp            [1..*]    one menu app; attrs: applicationType, applicationWeight, text, textModel, insert*…
    ├── comment          [0..1]    free-form; usually empty <comment/>
    ├── entryButton      [1]       the item that appears in the host menu
    │   └── properties → property*
    ├── actions          [1]
    │   ├── hmiAction*             in-HMI navigation  (id, target)
    │   └── raAction*              callback into your .so (id, actionType?)
    ├── models           [1]
    │   ├── raListModel* raDataModel* raBoolModel* raIntModel*
    │   ├── raImageModel* raGaugeModel* raPreviewModel*
    │   ├── textIdModel* (→ synonyms)  imageIdModel*
    │   └── formatDataModel* (→ models → raDataModel*)
    ├── events           [0..1]
    │   ├── focusEvent*            (id, target | targetModel)
    │   ├── statusbarEvent*        (id, textModel)
    │   └── popupEvent*            (id, priority, target, type)
    └── hmiStates        [1]
        ├── hmiState*        │ each state = one screen
        ├── toolbarHmiState* │ (id, text, textModel, parentId)
        └── popupHmiState*   │
            ├── widgetName       [0..1]   named layout table
            ├── properties → property*    state-level props (e.g. HMISTATE_TABLETYPE)
            ├── layoutGroups → layoutGroup*   (name, width)
            ├── optionComponents → <component>*   OPTION hard-button menu
            ├── components → <component>*         on-screen widgets
            └── toolbarComponents → <component>*  (toolbarHmiState only)

<component> ∈ { button, list, label, separator, image,
                checkbox, radiobutton, gauge, widget }
   every component: id + (model/action/changeAction/…) + optional
       ├── properties → property* (→ property may hold condition→assignments→assignment*)
       ├── bindings → binding*        (widget only)
       └── tooltipText                (label/gauge/…)
```

**PARSER** — all of the above element names are literal strings in `HmiMain3D`.
**CARVE** — every element except the ones flagged **EXAMPLE** below appears in
`SecurityMenu.xml` and/or `ActiveSeating.xml`.

---

## 3. Root & application elements

### 3.1 `<pluginApps>` — document root **CARVE**

Container only; no attributes. One per file. Holds one or more `<pluginApp>`.
(One file *may* declare several apps: `SecurityMenu.xml` declares 10 sibling
`<pluginApp>`s, one per menu page — `SecurityMenu.xml:3,63,99,271,…`.)

### 3.2 `<pluginApp>` — one menu app **CARVE**

| Attribute | Type | Req? | Meaning | Evidence |
|-----------|------|------|---------|----------|
| `applicationType` | enum string | **yes** | Which host menu the entry docks into / how it is placed. See §7.1. | `Diagnostics.xml:14`, `ActiveSeating.xml:3`, `SecurityMenu.xml:3` |
| `applicationWeight` | int | no | Sort order within the target menu (lower = earlier; ties broken by host — RECON). | `Diagnostics.xml:14`, `ActiveSeating.xml:3` |
| `text` | string | no | Developer/label text for the entry. A `textModel` (if present) overrides it with a localized text-DB string. | all |
| `textModel` | model id | no | `textIdModel` supplying the localized menu label. | `SecurityMenu.xml:3` |
| `entryButtonFocusID` | int | no | *(Custom only)* focus id of the existing OEM widget to attach near. | `ActiveSeating.xml:3` |
| `insertStateID` | int | no | *(Custom only)* native OEM state to inject the entry into. | `ActiveSeating.xml:3` |
| `insertAfterFocusID` | int | no | *(Custom only)* insert immediately after this focus id (`0` = first — RECON). | `ActiveSeating.xml:3` |

> **RECON.** The `insert*`/`entryButtonFocusID` trio is only used together with
> `applicationType="Custom"`; it is the manual placement mechanism for apps that
> don't dock into a named menu. Apps with a named `applicationType`
> (`VehicleInformation`, `Settings__SpecialVehicle`, `ServiceMenu`) omit them and let
> `CMappings::ENTRY_MAPPINGS` resolve placement. See §7.1.

### 3.3 `<comment>` **CARVE**

Free-form. In every OEM and example file it is the empty element `<comment/>`.

### 3.4 `<entryButton>` **CARVE**

The single item that shows up in the host menu; pressing it fires its `action`.

| Attribute | Type | Meaning | Evidence |
|-----------|------|---------|----------|
| `id` | component id | the entry button's own component id | `Diagnostics.xml:16` |
| `action` | action id | fired on press — typically an `hmiAction` to your root state, or a `raAction` | `Diagnostics.xml:16`, `SecurityMenu.xml:5` |
| `text` | string | fallback label | all |
| `model` | model id | `textIdModel` for the localized label | `SecurityMenu.xml:65` |
| `previewModel` | model id | `raPreviewModel` shown in the menu preview pane when the entry is focused | `SecurityMenu.xml:65` |

Child: `<properties>` (§6). In both the example and ActiveSeating the entry button
carries `<property id="23" value="2"/>` (**EXAMPLE/CARVE**; `Diagnostics.xml:18`,
`ActiveSeating.xml:9`). Id 23 is an entry-only property whose symbolic name is not
recoverable — see Open Questions. SecurityMenu entry buttons instead carry
`<property id="3" value="false"/>` (`VISIBLE=false`, `SecurityMenu.xml:7`).

---

## 4. `<actions>` — the two action kinds

`<actions>` is a flat list mixing the two kinds. Ids share the app-wide namespace.

### 4.1 `<hmiAction>` — in-HMI navigation **CARVE/PARSER**

```xml
<hmiAction id="11" target="200"/>   <!-- pressing a component with action="11" navigates to hmiState 200 -->
```

| Attribute | Type | Meaning |
|-----------|------|---------|
| `id` | action id | referenced by a component's `action=` |
| `target` | hmiState id | the screen to navigate to |

An `hmiAction` is resolved **entirely inside HmiMain3D** — the framework pushes
`target` onto the state stack. Your `.so` is never called. Use it for pure menu
navigation. **CARVE** `Diagnostics.xml:22–24`, `SecurityMenu.xml` (`hmiAction id="3" target="690"`).

### 4.2 `<raAction>` — callback into your plugin **CARVE/PARSER**

```xml
<raAction id="21"/>                          <!-- discrete: fires once per activation -->
<raAction actionType="Continuous" id="38"/>  <!-- continuous: fires repeatedly while the input is held -->
```

| Attribute | Type | Meaning |
|-----------|------|---------|
| `id` | action id | the value your code passes to `addHandler(id, …)` |
| `actionType` | enum string | `""`/absent = discrete (default); `Continuous` = repeated delivery while the input is held/pressed |

**CARVE**: default (discrete) form `Diagnostics.xml:25–31`; `Continuous` at
`SecurityMenu.xml:110–111`. When the user activates a component whose `action` (or
`changeAction`) names an `raAction`, HmiMain3D delivers it to the delegate you
registered — carrying a `Parcel` payload (row index for a list, new value for a
gauge, etc.). See `06-runtime-api-reference.md` and the handler wiring in
`diagnostics12.cpp:329–347`.

> **What `Continuous` actually is (correction to a common misreading).** In the
> carve the only two `Continuous` raActions are ids `38` and `39`
> (`SecurityMenu.xml:110–111`), and both are the `action=` of ordinary
> **push-to-talk buttons** — "Sprachdurchsage" and "Kommandodurchsage"
> (`SecurityMenu.xml:233–234`). `Continuous` therefore means *repeated delivery
> while a component is held/pressed* (hold-to-repeat / push-to-talk), and it is a
> property of **buttons**, not gauges. **Every gauge `changeAction` in the carve is
> a plain discrete `raAction` with no `actionType`** (decls at
> `SecurityMenu.xml:112–113,117,120,125`; the gauge at `:235` uses `action="40"
> changeAction="41"`, both discrete). Reserve `Continuous` for controls that must
> fire while held.

### 4.3 The `changeAction` attribute **CARVE**

`changeAction` is a *component attribute* (not an `<actions>` element) that names a
second `raAction`, distinct from `action`. It is used on value-editing components
(the carve uses it on `gauge`): `action` fires on the final commit, while
`changeAction` fires on each incremental value change as the user adjusts the
control. Both reference an `raAction` id and are delivered to your `addHandler`
delegate exactly like `action`. **CARVE** `SecurityMenu.xml:235`
(`<gauge action="40" changeAction="41" …>`, both ids declared as discrete
raActions).

---

## 5. `<models>` — data models

A **model** is a named slot the UI reads its content from. There are two families:

* **`ra*` models — dynamic**, filled by your plugin at runtime via
  `updateModel(id, …)`. The `ra` prefix = *Remote Application*.
* **`*IdModel` — static**, a fixed reference into the plugin's text/image resource
  DBs (`TextDBFile`/`ImageDBFile` from the manifest). Not updated by code.

A component binds to a model by id (`model=`, `imageModel=`, `previewModel=`,
`valueModel=`, `tooltipModel=`, `textModel=`). `updateModel(modelId, data)` targets
the model *by id*, and every component bound to it re-renders. (The runtime
copy/threading semantics of `updateModel()` are covered in
`07-threading-and-safety-model.md`, not here.)

### 5.1 Dynamic (`ra*`) models

| Element | Attributes | Fed by C++ with | Evidence |
|---------|-----------|-----------------|----------|
| `raListModel` | `id`, `modelType?` (`Richtext`) | a `DataTable` (rows × columns) | `Diagnostics.xml:34–35`, `SecurityMenu.xml:140` |
| `raDataModel` | `id`, `modelType` (see §7.2) | a scalar / string matching `modelType` | `Diagnostics.xml:36`, `ActiveSeating.xml:43–59` |
| `raBoolModel` | `id` | a bool (e.g. checkbox state) | `SecurityMenu.xml` (`raBoolModel id="55"`) |
| `raIntModel` | `id`, `modelType` (`NativeStateID`), `value` | preset int; used to point at a native OEM state | `ActiveSeating.xml:30`, `SecurityMenu.xml` |
| `raImageModel` | `id` | a dynamic image handle | `SecurityMenu.xml` (`raImageModel id="7"`) |
| `raGaugeModel` | `id`, `min`, `max`, `increment`, `value?` | current gauge value | `SecurityMenu.xml:140` |
| `raPreviewModel` | `id`, `modelType` (`StatePreview` \| `ContentPreview`), `previewState` | (static) live thumbnail of another `hmiState` | `SecurityMenu.xml:85–86` |

### 5.2 Static resource models

| Element | Attributes | Meaning | Evidence |
|---------|-----------|---------|----------|
| `textIdModel` | `id`, `textId`, `modelType?` | localized string from the text DB; child `<synonyms/>` (voice synonyms, usually empty) | `ActiveSeating.xml:31–33`, `SecurityMenu.xml` |
| `imageIdModel` | `id`, `imageId`, `modelType?` | bitmap from the image DB | `ActiveSeating.xml:70`, `SecurityMenu.xml` |
| `formatDataModel` | `id`, `formatString`, `formatStringModel`, `modelType?` | printf-style composition: a `formatStringModel` (a `textIdModel`) with `{…}` filled from nested `<models><raDataModel …/></models>` | `ActiveSeating.xml:64–68` |

> **RECON.** `raPreviewModel modelType="StatePreview" previewState="N"` renders a
> live miniature of state `N`; confirmed indirectly by the HmiMain3D log strings
> `[CAbstractComponent] Preview for component %u.%u: statePreview for component %u
> (provided by previewModel %u)` and
> `[CListEntryPoint] Preview for entryPoint of app '%s': statePreview …`.
> `ContentPreview` is the second preview variant (see §7.2). **CARVE**
> `SecurityMenu.xml:85–86` (`raPreviewModel id="1002" modelType="StatePreview"`
> and `id="1019" modelType="ContentPreview"`, both `previewState="32"`).

---

## 6. `<properties>` / `<property>` — per-element property bag

Any component, the entry button, and any `hmiState` may carry a `<properties>`
block of `<property>` rows. A property sets a typed attribute of the element by
**numeric id**; the value is parsed per the property's implicit type.

```xml
<button id="4" action="22" text="Read DTCs">
  <properties>
    <property id="2" value="false"/>   <!-- SELECTABLE = false: greyed/unfocusable -->
  </properties>
</button>
```

| Attr | Meaning |
|------|---------|
| `id` | the property-type id (see §7.3) |
| `value` | the value (`true`/`false`, an int, or a resource id per the property type) |

At runtime you can flip a property that your C++ holds a handle to (by component
id) with `setProperty(componentId, propId, Parcel(value))` — e.g. enabling a button
once data is ready. **CARVE** (`Diagnostics.xml:62,67`, `ActiveSeating.xml`
widespread) + **RECON** for the runtime path (see `06-runtime-api-reference.md`).

### 6.1 Conditional property values — `<condition>` / `<assignments>` / `<assignment>` **CARVE**

A property's value can be *chosen at render time* from a condition instead of being
a constant. The only condition type seen in the carve is `LAYOUTBAG` (the active
layout variant / screen configuration):

```xml
<property id="20" value="626">                 <!-- POSITION_X default -->
  <condition conditionType="LAYOUTBAG">
    <assignments>
      <assignment conditionValue="0" value="626"/>
      <assignment conditionValue="1" value="476"/>
      <assignment conditionValue="2" value="626"/>
    </assignments>
  </condition>
</property>
```

| Element | Attributes | Meaning |
|---------|-----------|---------|
| `condition` | `conditionType` (`LAYOUTBAG`) | selects the switch variable |
| `assignments` | — | container of cases |
| `assignment` | `conditionValue`, `value` | if the condition equals `conditionValue`, use `value` |

**CARVE** `SecurityMenu.xml:1688`. **PARSER** corroboration: HmiMain3D drives
several distinct property kinds from a `LAYOUTBAG` condition, e.g. list column
widths (`[CAbstractList::setProperty] %u.%u LAYOUTBAG condval 0x%x, set column
widths from '%s'`) **and** component visibility
(`Setting property visible %u.%u LAYOUTBAG condval 0x%x, set visibility from '%d'`)
— i.e. `LAYOUTBAG` can select `VISIBLE` (property 3) and position/size values, not
only column widths. This is resolved by HmiMain3D; no C++ involvement.

---

## 7. Enumerations

### 7.1 `applicationType` values

Resolved by `CMappings::ENTRY_MAPPINGS` inside HmiMain3D. **Four** concrete values
appear in this carve — treat them as *the values that appear in this carve*, **not**
the complete set the framework accepts; the full enumeration is **not recoverable**
(it lives in a build-time header not on the unit). For the fuller treatment (native
anchors, the "no fitting rule found" behavior, portability), see
`04-menus-screens-and-layout.md` §1.1.

| Value | Placement | Evidence |
|-------|-----------|----------|
| `VehicleInformation` | Docks the entry into the Vehicle-Information menu. | `Diagnostics.xml:14` (**EXAMPLE**; verified end-to-end on the author's OPT_DEBUG-enabled unit) |
| `Settings__SpecialVehicle` | Docks into Settings → Special-Vehicle submenu. | `SecurityMenu.xml:3` (**CARVE**, 10×) |
| `ServiceMenu` | Docks into the vehicle **Service** menu; the framework synthesizes the entry (no `entryButton`). | 4 OEM `HmiGen_*RemoteService.xml` files (**CARVE**) |
| `Custom` | No named menu; you place the entry manually via `entryButtonFocusID` / `insertStateID` / `insertAfterFocusID`. | `ActiveSeating.xml:3` (**CARVE**) |

> **RECON.** The `__`-delimited form (`Settings__SpecialVehicle`) reads as
> `Menu__Submenu`; expect other `Area__Sub` values to exist for other menus.

### 7.2 `modelType` values

Seen on `raDataModel` / `raListModel` / `raIntModel` / `raPreviewModel`.

| `modelType` | Used on | Payload | Status |
|-------------|---------|---------|--------|
| *(empty / absent)* | list/data | generic | CARVE |
| `Richtext` | `raListModel`, `raDataModel` | multi-line rich text; on a `list`, one block of text (see `label` below) | CARVE + PARSER + ON-CAR |
| `Integer` | `raDataModel` | signed int | CARVE |
| `UnsignedInteger` | `raDataModel` | unsigned int | CARVE + PARSER |
| `Boolean` | `raDataModel` | bool | CARVE + PARSER |
| `FloatingPoint` | `raDataModel` | float | CARVE + PARSER |
| `Enumeration` | `raDataModel` | enum index | CARVE |
| `StringIdentity` | `raDataModel` | opaque string key | CARVE |
| `NativeStateID` | `raIntModel` | id of a native OEM state | CARVE + PARSER |
| `StatePreview` | `raPreviewModel` | live preview of `previewState` (another `hmiState`) | CARVE + PARSER |
| `ContentPreview` | `raPreviewModel` | preview of the *content* of `previewState`; the preview variant used by nearly every interactive OEM component | CARVE + PARSER |

(Evidence: `ActiveSeating.xml:43–59,30`; `SecurityMenu.xml:85–86`; PARSER tokens —
including `ContentPreview` — confirmed present as strings in HmiMain3D.
`Enumeration` and `StringIdentity` are correctly *not* PARSER-tagged: they are
absent from the binary's strings.)

### 7.3 `property` ids **CARVE (authoritative)**

This table was derived by **aligning the two SecurityMenu files
position-for-position**: `SecurityMenu.xml` (numeric runtime form) and
`SecurityMenu_Editor.xml` (symbolic source form) each contain exactly **675**
`<property>` elements, and zipping them yields a clean, 1:1, unambiguous
numeric→name mapping. Only these nine distinct ids appear across all 675
properties, so the table is complete for the carve. The Editor's `<header>` cites
`PropertyTypes.h` as the source of these constants (`SecurityMenu_Editor.xml:6`).

| id | Symbolic name | Type | Applies to | Notes |
|----|---------------|------|-----------|-------|
| 2 | `SELECTABLE` | bool | component | focusable/interactive; `false` = greyed. Runtime-toggle target. |
| 3 | `VISIBLE` | bool | component / entry | shown/hidden. Can be driven by a `LAYOUTBAG` condition (§6.1). |
| 9 | `WIDTH` | int px | component | |
| 10 | `HEIGHT` | int px | component | |
| 17 | `ALIGNMENT` | enum int | component | text/content alignment. |
| 20 | `POSITION_X` | int px | component | absolute X (with `POSITION_Y`, for free layout). |
| 21 | `POSITION_Y` | int px | component | absolute Y. |
| 24 | `HMISTATE_TABLETYPE` | enum int | **hmiState** | state layout table type (values `3`, `13` seen). Parser-special-cased — see §7.4. |
| 39 | `BACKGROUND` | int | component | background style/handle. (Only id whose symbolic name is absent from the binary's strings.) |

**Open:** `23` — an **entry-button** property (value `2`) used by the example and by
ActiveSeating (`ActiveSeating.xml:9`); its symbolic name is *not* in the
SecurityMenu mapping (SecurityMenu entry buttons use `VISIBLE` instead), so it is
unresolved. See Open Questions.

> **CARVE**: `SecurityMenu.xml` numeric ids ↔ `SecurityMenu_Editor.xml` symbolic
> ids, 675:675. The example file's inline comments corroborate 2/9/10/20/21
> (`Diagnostics.xml:62,92–95`).

### 7.4 `HMISTATE_TABLETYPE` (property 24) values

Observed on state `<properties>`: `13` (full-screen RSE tables in ActiveSeating,
`ActiveSeating.xml:172`) and `3` (list-style state, `ActiveSeating.xml:193`). The
full enum is **RECON**; treat `13`=full-screen table, `3`=list as working
hypotheses.

> **Parser special-casing (PARSER).** `HMISTATE_TABLETYPE` is not handled like an
> ordinary component property: HmiMain3D transforms and validates it at load time.
> Its logs include
> `[CHmiIntegrator::filterXmlStructure] hmistates: converted HMISTATE_TABLETYPE to attribute (value=%d)`
> (the loader hoists the property into a state attribute) and
> `property HMISTATE_TABLETYPE not allowed` (rejected where it does not belong).
> Declare it only on an `hmiState`'s `<properties>`.

### 7.5 `conditionType` values

Only `LAYOUTBAG` observed (§6.1). **CARVE/PARSER.**

### 7.6 `actionType` values

`""`/absent (discrete) and `Continuous` (§4.2). **CARVE.**

---

## 8. `<hmiStates>` — screens

`<hmiStates>` holds the plugin's screens. Three state elements exist:

| Element | Adds | Evidence |
|---------|------|----------|
| `hmiState` | plain screen | `Diagnostics.xml:39`, `ActiveSeating.xml:192` |
| `toolbarHmiState` | a `<toolbarComponents>` block (bottom toolbar buttons) | `ActiveSeating.xml:205`, `SecurityMenu.xml:1404` |
| `popupHmiState` | rendered as a popup that takes focus, opened only by a `<popupEvent>` (§12) | `SecurityMenu.xml:2736` |

Common state attributes:

| Attribute | Type | Meaning | Evidence |
|-----------|------|---------|----------|
| `id` | state id | navigation target (`hmiAction target`, `focusEvent target`, …) | all |
| `text` | string | dev label | all |
| `textModel` | model id | localized title | `ActiveSeating.xml:192`, `SecurityMenu.xml` |
| `parentId` | state id | parent screen, for a hierarchical page/back stack | `SecurityMenu.xml` (`parentId="95"`) |

State children:

* `<widgetName>` — names a predefined OEM layout table this state is built on
  (e.g. `LT_State_RSE_FullScreen_ActiveSeating`). **CARVE** `ActiveSeating.xml:170`.
* `<properties>` — state-level properties (esp. `HMISTATE_TABLETYPE`, §7.4).
* `<layoutGroups>` — see §10.
* `<optionComponents>` — see §11.
* `<components>` — the on-screen widgets (§9).
* `<toolbarComponents>` — toolbar buttons (`toolbarHmiState` only), same component
  grammar. **CARVE** `ActiveSeating.xml:285–292`.

An empty `<hmiStates/>` is legal for a pluginApp that only injects a menu entry and
navigates elsewhere (`SecurityMenu.xml:61`).

---

## 9. Components

All components live in `<components>`, `<toolbarComponents>`, or
`<optionComponents>`. Every component has an `id` (app-wide unique) and may carry a
`<properties>` block and, for text components, a `<tooltipText>` element.

### 9.1 Component attribute matrix **CARVE**

| Element | id | action | changeAction | model | imageModel | textModel | previewModel | tooltipModel | other | Evidence |
|---------|----|--------|--------------|-------|-----------|-----------|--------------|--------------|-------|----------|
| `button` | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | `text` | `Diagnostics.xml:41`, `ActiveSeating.xml:286` |
| `list` | ✓ | ✓ | | ✓ | | | | | | `Diagnostics.xml:71`, `ActiveSeating.xml:197` |
| `label` | ✓ | | | ✓ | | | | | `text`; child `<tooltipText>` | `Diagnostics.xml:90`, `ActiveSeating.xml:245` |
| `separator` | ✓ | | | | | | | | | `Diagnostics.xml:70`, `SecurityMenu.xml` |
| `image` | ✓ | | | ✓ | ✓ | | | | | `ActiveSeating.xml:211`, `SecurityMenu.xml` |
| `checkbox` | ✓ | ✓ | | ✓ | | ✓ | ✓ | | `text` | `SecurityMenu.xml:94` |
| `radiobutton` | ✓ | ✓ | | ✓ | | ✓ | ✓ | | `text` | `SecurityMenu.xml:1159` |
| `gauge` | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | | `text`; child `<tooltipText>` | `SecurityMenu.xml:235` |
| `widget` | ✓ | | | | | | | | `widgetName`; child `<bindings>` | `ActiveSeating.xml:219` |

Notes:

* **`imageModel` scope.** In the carve `imageModel` appears only on `button`
  (`ActiveSeating.xml:286`) and `image`. No `checkbox`, `radiobutton`, or `gauge`
  carries one — the checkbox at `SecurityMenu.xml:94` uses `model` + `previewModel`
  only. Do not assume `imageModel` on the toggle/gauge components.
* **`text` vs `model`.** `text=` is a raw fallback label; when a `model`/`textModel`
  is present it wins (localized). `ActiveSeating.xml:202` shows `text=""` with
  `model="44"`.
* **`list`.** `model` is the `raListModel` supplying rows; `action` is the
  `raAction` fired when a row is activated (the `Parcel` carries the row index).
  `Diagnostics.xml:71`. Lists honor `LAYOUTBAG` column-width conditions (§6.1).
* **`label`.** A display-only text sink. In the example the SVT detail pane is a
  `Richtext` `label` bound to `raDataModel` 52 because labels aren't focusable
  (`Diagnostics.xml:90`). Absolute-position with `WIDTH/HEIGHT/POSITION_X/POSITION_Y`
  properties.

  **A label is one line high.** The HMI picks each component's widget from
  `data/ro/app/hmigenengine/hmigen_generationrules.pbg`, and a `label` is always
  `LT_Label_A4A`, whatever its model. On the car, a label in the stock column (no
  position or size) bound to a `Richtext` model showed only the first line of a
  `\n`-joined string (VAE Powertools 1.3.0). Whether `HEIGHT` gives the example's
  absolutely placed label more lines is untested.

  **For multi-line text, use a Richtext list.** A `list` bound to a model with
  `modelType="Richtext"` is drawn as `LT_ScrollLabel_A4A`: one block of text that
  wraps and breaks at `\n`, with nothing in it focusable when `SELECTABLE` (2) is
  `false`. Fill it with a table of **one row and one cell**, the whole text. OEM
  ActiveSeating fills its tutorial text this way with a `TextID`
  (`ActiveSeating.xml:197`, model 274). A `BasicString` cell works too (on the car,
  VAE Powertools 1.3.1); leading spaces are kept. The rich-text parser reads `<`…`>`
  as markup, so keep them out of the text. While the car is moving, the HMI cuts
  a Richtext list to 3 or 9 lines (its speedlock). A Richtext model with several
  rows drew nothing in an earlier test.

  ```xml
  <raListModel id="51" modelType="Richtext"/>
  ...
  <list id="7" model="51">
    <properties><property id="2" value="false"/></properties>  <!-- display only -->
  </list>
  ```
* **`gauge`.** `action` fires on commit; `changeAction` fires on each incremental
  value change (§4.3). Both are discrete `raAction`s in the carve. Bound to a
  `raGaugeModel` (`min`/`max`/`increment`/`value`). `SecurityMenu.xml:235,140`.
* **`checkbox` / `radiobutton`.** `action` fires on toggle; `model` (a
  `raBoolModel`) holds the state. `SecurityMenu.xml:94,1159`.

### 9.2 `<widget>` and `<bindings>` **CARVE**

A `widget` embeds a predefined OEM layout table (`widgetName=`, e.g.
`LT_Table_RSE_ActiveSeating`) and wires that table's named parameters to your
models through `<bindings>`:

```xml
<widget id="187" widgetName="LT_Table_RSE_ActiveSeating">
  <bindings>
    <binding key="GaugeLeftEnabled" valueModel="188"/>
    <binding key="GaugeLeftValue"   valueModel="190"/>
    <binding key="Description_Text" valueModel="198"/>
  </bindings>
  <properties> … </properties>
</widget>
```

| `binding` attr | Meaning |
|----------------|---------|
| `key` | the table's parameter name (widget-specific; discover per `widgetName`) |
| `valueModel` | the model id feeding that parameter |

**CARVE** `ActiveSeating.xml:219–236`. Widgets are how OEM plugins render
rich/animated screens; a hobbyist plugin can stick to `button`/`list`/`label`/
`gauge` and never touch them, but the grammar supports them. Note the `key` names
(`GaugeLeftValue`, …) are specific to each named layout table and are **not** a
fixed vocabulary — discover them per `widgetName` or avoid `<widget>` entirely.

---

## 10. `<layoutGroups>` / `<layoutGroup>` **CARVE**

Scopes the width of the primary content column of a state.

```xml
<layoutGroups>
  <layoutGroup name="List" width="700"/>
</layoutGroups>
```

| Attribute | Meaning |
|-----------|---------|
| `name` | the layout region name (`"List"` in every observed case) |
| `width` | region width in px |

Set a large `width` for a full-width list, or a smaller value (OEM uses `700`) to
reserve the remainder for an absolutely-positioned detail pane — the master/detail
pattern. **CARVE** `SecurityMenu.xml:876` (`700`); **EXAMPLE** `Diagnostics.xml:50`
(full-width) and `:80` (700 px + positioned detail label). (The overall content-area
width used in the example, ~1280 px, is an example-derived assumption, not a carve
constant.)

---

## 11. `<optionComponents>` — the hardware OPTION-button menu **CARVE/PARSER**

A state may declare an `<optionComponents>` block: the context menu shown when the
user presses the physical **OPTION** button on that screen. It contains the same
component elements (typically `button`s), each carrying a `raAction` back to your
plugin.

```xml
<optionComponents>
  <button id="12" action="26" text="Re-read DTCs"/>
  <button id="13" action="27" text="Clear DTCs"/>
</optionComponents>
```

**PARSER**: parsed by HmiMain3D's `createOptionComponents`, mapped through
`CMappings::OPTIONCOMPONENT_MAPPINGS` (both are symbols/strings in the binary), and
the parser guards on `optionComponentID > 0u`. **CARVE**: the OEM uses it too,
including the empty form `<optionComponents/>` (`SecurityMenu.xml:1405`). The example
populates it (`Diagnostics.xml:55–58`). Because OPTION items get no hover/focus
context, treat their actions as whole-screen commands.

---

## 12. `<events>` — declarative event hooks **CARVE**

| Element | Attributes | Meaning | Evidence |
|---------|-----------|---------|----------|
| `focusEvent` | `id`, `target` \| `targetModel` | when a component/state gains focus, navigate to `target` state (or use `targetModel`, a `NativeStateID` `raIntModel`) | `ActiveSeating.xml:162–166`, `SecurityMenu.xml:59` |
| `statusbarEvent` | `id`, `textModel` | drive the status-bar text from a model | `SecurityMenu.xml:58` |
| `popupEvent` | `id`, `priority`, `target`, `type` | trigger a `popupHmiState` (`target`) at a given `priority` | `SecurityMenu.xml:2733` |

**Popups, from the disassembly of `HmiMain3D` (DISASM, not yet run on a car).**
- **Loader.** `CPopupEvent::setProperties` (0x1109b2c) reads `target`, `priority` and an undocumented `type`.
- **`priority` is required.** It must be 1–18 (it selects the popup's activity type). A missing or 0 priority asserts
  "Invalid popup priority", and the popup is not opened.
- **`type`.** `type="4"` sets the popup service's "reappear" flag (0x20): the popup comes back after it is closed.
  Other values give no flags.
- **Opening and closing.** The plugin fires the event with `PluginApp::triggerEvent(id)` (`libAppFramework.A.so`
  0x5444) to open the popup. `triggerEvent(id, Parcel(false))` (0x5464) closes it: `CPopupEvent::perform` (0x1109380)
  reads the event's key-0 bool, and false closes.
- **Gates.** Opening is refused without the certificate's popup permission or past its popup count ("RHMI popup not
  allowed"), and while the speed lock "LeaveApp" is on.
- **Focus and timeout.** A plugin popup always takes focus, and the HMI gives it no timeout
  (`CAbstractPopupHmiState::openPopup` 0x11acda4 hard-codes both). To close one by itself, the plugin posts a Runnable
  that fires the close.
- **Titleless.** State property 24 (`tableType`) = 22 converts a popup state to the titleless
  `dynamicTitlelessPopupHmiState`; 20 converts it to `dynamicPopupHmiState`. These dynamic popups show only `label`
  and `button` components.

**Popups on the car (VAE Powertools 1.3.1–1.4.1, 2026-10-09). ON-CAR.**
- **Opening and closing work** as above. A titleless popup with a single `label` and **no button** opens, takes focus
  and closes again, which no OEM plugin popup does. It draws as a slim bar with the text on one line and the HMI's
  orange back arrow on its left. The arrow belongs to the popup frame (`LT_State_PopupSmall`, whose only exposed
  property is `IsBluRayOrDVDPanel`), so it can't be hidden. In a dynamic popup a `label` is a `dynamicPopupLabel`
  (`LT_Label_6Row_1TextDyn`), which wraps over up to six lines.
- **A popup opened too early is lost.** One opened while the HMI shows the start-up Driver profiles list never
  appears, either then or later.
- **Know when it shows.** The HMI tells the plugin when the popup state becomes visible (state event 11, key 23 true;
  see `06-runtime-api-reference.md` §A.2). So a plugin can treat "not visible within a few seconds" as dropped,
  cancel, and ask again.

`focusEvent` with `targetModel` (rather than `target`) lets focus jump to a
*native* OEM state by id (paired with `raIntModel modelType="NativeStateID"`).
**CARVE** `SecurityMenu.xml:59` (`focusEvent id="24" targetModel="21"`), model 21
being a `raIntModel … NativeStateID`.

---

## 13. Minimal well-formed DescFile (generic skeleton)

A complete, schema-valid two-screen plugin — one menu entry, a root menu, and one
tool screen with a button, a separator, a list, and an OPTION command:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<pluginApps>
  <pluginApp applicationType="VehicleInformation" applicationWeight="200" text="MyTool">
    <comment/>

    <!-- menu entry -> hmiAction 10 -> root state 100 -->
    <entryButton action="10" id="1"/>

    <actions>
      <hmiAction id="10" target="100"/>   <!-- entry           -> root menu   -->
      <hmiAction id="11" target="200"/>   <!-- "Open tool" item -> tool screen -->
      <raAction  id="20"/>                <!-- "Run" pressed         (addHandler 20) -->
      <raAction  id="21"/>                <!-- result row selected   (addHandler 21) -->
      <raAction  id="22"/>                <!-- OPTION: Refresh        (addHandler 22) -->
    </actions>

    <models>
      <raListModel id="50"/>              <!-- filled via updateModel(50, DataTable) -->
    </models>

    <hmiStates>
      <hmiState id="100" text="MyTool">
        <components>
          <button id="2" action="11" text="Open tool"/>
        </components>
      </hmiState>

      <hmiState id="200" text="Tool">
        <layoutGroups>
          <layoutGroup name="List" width="1280"/>
        </layoutGroups>
        <optionComponents>
          <button id="9" action="22" text="Refresh"/>
        </optionComponents>
        <components>
          <button id="3" action="20" text="Run">
            <properties>
              <property id="2" value="true"/>   <!-- SELECTABLE -->
            </properties>
          </button>
          <separator id="4"/>
          <list id="5" model="50" action="21"/>
        </components>
      </hmiState>
    </hmiStates>
  </pluginApp>
</pluginApps>
```

C++ side (see `06-runtime-api-reference.md`): register `addHandler(20/21/22, …)`, fill
the list with `updateModel(50, dataTable)`, grey/enable the Run button with
`setProperty(3, /*SELECTABLE*/2, Parcel(bool))`.

---

## 14. Confirmed-from-OEM vs. inferred-from-example

* **Confirmed only from OEM** (not in the example; use the OEM file as your
  template): `toolbarHmiState` + `toolbarComponents`, `popupHmiState` +
  `popupEvent`, `checkbox`, `radiobutton`, `gauge` + `changeAction` +
  `raGaugeModel`, `widget` + `bindings`, `image`, `textIdModel`/`imageIdModel`/
  `formatDataModel`/`raBoolModel`/`raImageModel`/`raIntModel`/`raPreviewModel`
  (`StatePreview` + `ContentPreview`), `focusEvent`/`statusbarEvent`,
  `condition`/`assignments`/`assignment`, `parentId`, `widgetName`, `Continuous`
  actions (on push-to-talk buttons), and the `Custom` placement attributes
  (`entryButtonFocusID`/`insertStateID`/`insertAfterFocusID`).
* **Exercised in the example and verified end-to-end on the author's OPT_DEBUG-enabled unit**: `pluginApps`/`pluginApp`/
  `entryButton`/`actions`(`hmiAction`+`raAction`)/`models`(`raListModel`+
  `raDataModel`)/`hmiStates`/`hmiState`/`components`(`button`+`list`+`label`+
  `separator`)/`layoutGroups`/`optionComponents`/`properties` and property ids
  2/9/10/20/21.
* **Reconstructed** (semantics of ids that ship numeric): the `property` id→name
  table (from the SecurityMenu numeric↔symbolic alignment — authoritative for the
  nine ids seen), `HMISTATE_TABLETYPE` value meanings, the full
  `applicationType`/`modelType`/`conditionType` enumerations, and the exact dispatch
  of `hmiAction` vs `raAction`.

Cross-references: `01-architecture-and-loading.md` (how the three artifacts fit),
`02-manifest-format.md` (`<DescFile>` linkage, text/image DBs),
`04-menus-screens-and-layout.md` (the `applicationType` menu tree and the property-id
catalog), `05-cxx-abi-and-data-types.md` (`PluginApp`, `Parcel`/`DataTable`, and the
reconstructed C++ types), `06-runtime-api-reference.md`
(`addHandler`/`updateModel`/`setProperty` and the runtime model-update recipes), and
`07-threading-and-safety-model.md` (the model-copy/threading semantics).

---

## Sources

These facts come from an **owner-authorized, offline flash carve** of the author's
own titled vehicle plus **end-to-end validation of a working example plugin on the
author's OPT_DEBUG-enabled unit**. Nothing here is car-specific (no VIN, network
address, or private diagnostic detail).
Grammar and enumerations are grounded in real OEM DescFiles
(`SecurityMenu.{xml,_Editor.xml,_Tree.xml}`, `ActiveSeating.xml`) and in literal
parser tokens/log strings inside the `HmiMain3D` binary; the working example is the
reference plugin's `Diagnostics.{xml,manifest}` + `diagnostics12.cpp`.

Reliability tags used throughout: **CARVE** (in an OEM file on the unit), **PARSER**
(a literal token/string in `HmiMain3D`), **EXAMPLE** (in the example plugin only),
**RECON** (reconstructed/inferred — a good hypothesis, not gospel). The C++
linkage details referenced here live in `05-cxx-abi-and-data-types.md` and rest on
**hand-reconstructed** SDK headers (`bmw_abi.h`, `bmw_list.h`) built from exported
library symbols, not vendor headers — treat all reconstructed-ABI details as such.
The DescFile *grammar* itself is not reconstructed: it is verified against real OEM
XML and the binary's parser tokens. (A **stock**, non-`OPT_DEBUG` unit enforces
**no signature** on plugin load — the loader links no cryptography and has no signature
branch, confirmed on-car by the owner's unsigned plugin; `OPT_DEBUG` only grants the
filesystem write to place the files. See `01-architecture-and-loading.md §3.1` / `14-signing-and-coding.md`.)
