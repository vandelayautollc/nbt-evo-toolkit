# 04 — Menus, Screens & Layout

*The UX/layout companion to the DescFile reference (see `03-descfile-xml-reference.md`). Where `03` catalogs every DescFile element, this doc explains how those declarations turn into a menu the driver can actually reach and navigate.*

> **Authorization.** Everything here was reverse-engineered from an offline flash carve and owner-authorized work on the author's own titled vehicle. It is written for a developer working on their **own** head unit. Menus are presented generically; no car-specific network address, VIN, or diagnostic-scanner detail is part of the SDK.

> **Verified vs. reconstructed.** Facts drawn from OEM DescFiles on disk, from the loader strings inside `HmiMain3D`, and from the working reference plugin are **carve-confirmed**. The numeric property-id → *name* mapping (e.g. `2 = SELECTABLE`) is partly **reconstructed** from the reference plugin's own comments plus observed behavior, and is flagged as such in §6. Read those flags before you rely on an id whose meaning is marked reconstructed.

---

## 0. The one-paragraph model

A plugin's `<Name>.xml` DescFile is a tree of **screens** (`hmiState`) built from **components** (`button`, `list`, `label`, `separator`, …). Exactly one thing decides **where in the car's menu the plugin appears**: the `applicationType` attribute on `<pluginApp>`. One button — the `entryButton` — is the door from that location into your plugin. Its `action=` may point at an `hmiAction` (jump straight to a screen — the portable, reference-plugin path) **or** at a `raAction` (fire a callback into your `.so`, which is the OEM `Settings__SpecialVehicle` norm; see §1.5). From a screen, every `button`'s `action=` points at an `hmiAction` whose `target=` is the id of the next `hmiState`; that is the entire navigation graph. Within a screen, a `layoutGroup` picks a stock template (full-width list vs. a 700 px master column), and any component can override placement with absolute `<property>` coordinates. That is the whole surface. The rest of this doc is detail.

### 0.1 Two XML dialects — read this before comparing with OEM files

The DescFile schema accepts **two interchangeable spellings** for `id` and `value`. The reference plugin and this doc use the **attribute form**; many OEM DescFiles use the **nested-element form**. They mean the same thing to the loader:

```xml
<!-- Attribute form (used throughout this doc and the reference plugin) -->
<hmiAction id="3" target="4"/>
<property id="2" value="true"/>

<!-- Nested-element form (used by the OEM HmiGen_* files) -->
<!-- HmiGen_NavigationRemoteService.xml:5-7, 287-292 -->
<hmiAction target="4"><id>3</id></hmiAction>
<property value="true"><id>2</id></property>
```

The OEM files additionally wrap everything in a `<pluginApps>` root and declare `encoding="ISO-8859-1"` (`HmiGen_NavigationRemoteService.xml:1-2`). When you open an OEM DescFile to confirm a schema detail, expect the nested form; write your own plugin in whichever you prefer — the attribute form is terser and is what the examples below use.

---

## 1. The menu-integration model

### 1.1 `applicationType` decides *where* the entry appears

`applicationType` is **not** free text. When the HMI integrates your plugin it looks for a *generation rule* keyed by that string; if none matches, integration fails outright. The loader says so in as many words:

```
[HmiDescription::integrate] Description insert state id invalid.
                            Probably no fitting rule found for applicationType %s.
```
*(string in `.../ID5/bin/HmiMain3D`)*

So the set of usable `applicationType` values is fixed by the HMI build, not by you. The named values are resolved to an integer (the binary exports `getApplicationTypeInt`) and matched against `HmiGenerationRules` / `TEntryPointEffect` rules baked into the HMI resource bundles — which is why grepping the binary for a value like `VehicleInformation` returns nothing: the names live in compiled rule data, not as loose strings. What the **carve actually contains** is **four** `applicationType` values — three in shipping OEM DescFiles (`ServiceMenu`, `Settings__SpecialVehicle`, `Custom`) plus `VehicleInformation`, the reference plugin's choice. These are the values that appear in this carve, **not** the complete set the framework accepts:

| `applicationType` | Menu location (native anchor) | Entry created by | Evidence |
|---|---|---|---|
| `ServiceMenu` | The vehicle **Service/menu** list (`ST_MyV_Selection_ServiceMenu`, driven by `CCarServiceMenuActivity`) | **Framework** — no `entryButton` element | 4 OEM `HmiGen_*RemoteService.xml` files use it; `HmiGen_NavigationRemoteService.xml:3` |
| `Settings__SpecialVehicle` | The **Special Vehicle** settings submenu (`CCarSpecialVehicleActivity` / `CPxyCANDevicesSpecialVehicle…SpecialVehicleMenuControl`) | Your `entryButton` (fires a `raAction`, §1.5) | `SecurityMenu.xml:3`; **10** pluginApps carve-wide, all in `SecurityMenu.xml` |
| `Custom` | **Anywhere** — you name a native state to hook into (§1.4) | Your `entryButton` | `ActiveSeating.xml:3` |
| `VehicleInformation` | My-Vehicle information menu *(author's choice for the reference plugin; treat as build-dependent)* | Your `entryButton` | `Diagnostics.xml:14`; placement observed, see §8 |

**Practical guidance.** If your target HMI build has a rule for a named type you want (e.g. a settings submenu), use it and supply an `entryButton`. If you cannot confirm a named rule exists, use **`Custom`** and anchor explicitly (§1.4) — it is the portable path and the one that does not depend on a rule you cannot see. Always confirm on your own unit: a wrong `applicationType` produces the "no fitting rule found" log and your menu entry simply never appears.

### 1.2 Two shapes of entry: framework-generated vs. `entryButton`

There are two distinct integration shapes in the carve, and they look different in XML:

**(a) `ServiceMenu` — no `entryButton`.** The `<pluginApp>` has `applicationType="ServiceMenu"` and a `textModel` for its label, then jumps straight to `<actions>`/`<hmiStates>`. The framework synthesizes the list entry for you.

```xml
<!-- HmiGen_NavigationRemoteService.xml:3 (shown here in attribute form) -->
<pluginApp applicationType="ServiceMenu" textModel="510">
  <actions> ... </actions>
  <hmiStates> ... </hmiStates>
</pluginApp>
```

**(b) Everything else — you declare an `entryButton`.** The `entryButton` carries an `action=` (the door), an `id=`, an optional visible `text=`/`model=`, an optional `previewModel=` (§1.6), and optional `<properties>`. Its `action=` may reference **either**:

- an **`hmiAction`** — navigate directly to a screen. This is the reference plugin's path and the simplest one to reason about:

  ```xml
  <!-- Diagnostics.xml:14 (reference plugin) -->
  <pluginApp applicationType="VehicleInformation" applicationWeight="200" text="PowerTools">
    <entryButton action="10" id="1">
      <properties>
        <property id="23" value="2"/>     <!-- entryButton-specific flag; see §6 -->
      </properties>
    </entryButton>
    <actions>
      <hmiAction id="10" target="100"/>   <!-- the door: entry -> first screen -->
      ...
  ```

- **or** a **`raAction`** — fire a callback into your `.so` (§1.5). This is what **all ten** OEM `Settings__SpecialVehicle` entry buttons do.

The loader itself only requires that an entry button have **a container or an action**; one with neither is rejected as useless (`[CAbstractEntryButton] … No container and no action -> menu entry will be useless`). The entry's label comes from the `entryButton`'s `text`/`model` if present, otherwise from the `pluginApp` `text`/`textModel`; the loader will even swap them (`[CHmiDescription::init] Replacing text model of description by text model of entry button`).

> **Multiple entries in one DescFile.** A plugin can declare **multiple** `<pluginApp>` blocks in one DescFile, each its own menu entry. `SecurityMenu.xml` ships **ten**, all `Settings__SpecialVehicle`: *Security Menu* (:3), *Scheibenheizung* (:63), *Kommunikation* (:99), *Sondersignalanlage* (:271), *Tonfolgeanlage* (:1245), *Zentralverriegelung* (:1623), *Einstellungen* (:1876), *Feuerlöschanlage* (:2698), *Atemluftanlage* (:2852), and *InfoText* (:3220). Every `entryButton` id must be unique across the file or the loader errors (`[CHmiDescription::init] EntryButton with duplicate id %d`).

### 1.3 `applicationWeight` orders sibling entries

When several entries share one target location, `applicationWeight` is their sort key. The reference plugin (`Diagnostics.xml:14`) and the one **carve** plugin that sets it (`ActiveSeating.xml:3`) both use `applicationWeight="200"`; the OEM `Settings__SpecialVehicle` apps in `SecurityMenu.xml` omit it entirely (zero occurrences carve-wide). The `Custom` path additionally exposes a per-list `listOrder`, which the loader reads from the anchor menu entry's focus id and falls back to a default when it can't (`[CAppStubManager] Couldn't get listOrder from entry menu with focus ID %u. Will use default %u`). The **direction** of the weight sort (ascending vs. descending) is not settled by the carve — see §8. Rule of thumb: pick a value and confirm placement on your unit relative to the neighbors you care about.

### 1.4 `Custom`: the portable "anchor anywhere" mechanism

`Custom` is the general escape hatch — internally the *"Entry Button Everywhere"* feature. Instead of relying on a named rule, you tell the loader exactly which native menu state to insert into and where in that state's list to sit. The loader documents the required attributes itself:

```
[CHmiDescription::load] Misusage of Entry Button Everywhere configuration.
   Use applicationType 'Custom', set at least insertStateID and optional
   either insertAfterFocusID or replaceFocusID.
[CAppStubManager] AppStubButton Everywhere will be used! Variables:
   insertStateID %d, insertAfterFocusID %d, replaceFocusID %d, listOrder %d!
```

The one shipping example wires all of this on the `<pluginApp>` element:

```xml
<!-- ActiveSeating.xml:3 -->
<pluginApp applicationType="Custom" applicationWeight="200"
           entryButtonFocusID="7217" insertAfterFocusID="0" insertStateID="1789"
           text="Active Seating">
  <entryButton action="112" id="113" model="2">
    <properties><property id="23" value="2"/></properties>
  </entryButton>
```

| Attribute | Meaning |
|---|---|
| `insertStateID` | The **native HMI state** to insert the entry into (the anchor screen). Required. |
| `insertAfterFocusID` | Put the new entry **after** this existing focus id in that state's list. `0` = beginning. |
| `replaceFocusID` | Alternative to `insertAfterFocusID`: **replace** an existing entry instead of inserting. |
| `entryButtonFocusID` | The focus id your entry button claims in the anchor list. Must be in-spec unless developer mode is on: `[CAppStubManager] Entry menu custom focus id %u … not in Spec. Use managed focus ID` / `ENTWICKLER_MENU mode, granted usage of custom focus id`. |

Because these ids are **native-state** ids specific to a given HMI build, a `Custom` anchor is only portable insofar as the target build exposes the same anchor state — document the `insertStateID` you chose so other developers can adjust it for their unit. (Native state ids come from the HMI's own state tree, which this SDK does not enumerate; discover them on your build.)

### 1.5 When the entry button fires a `raAction` (the OEM norm)

All ten `SecurityMenu.xml` entry buttons point their `action=` at a `raAction`, not an `hmiAction`. For example the first entry:

```xml
<!-- SecurityMenu.xml:5,11 -->
<entryButton action="2" id="1" text="SecurityMenu">
  <properties><property id="3" value="false"/></properties>
</entryButton>
<actions>
  <raAction actionType="" id="2"/>     <!-- entry button fires THIS, into the .so -->
  <hmiAction id="3" target="690"/>     <!-- a separate action, not what the button points at -->
</actions>
```

The mechanics are identical to any other `raAction` (see `05-cxx-abi-and-data-types.md`): when the entry button is activated, the framework invokes the delegate you registered with `addHandler(actionId, delegate)`, and your native code decides what happens — check availability, kick off a background read, and drive the screen. This is why the OEM Special-Vehicle apps pair the entry with `raPreviewModel`/`focusEvent` machinery (§1.6, §2.3) instead of a declarative target.

**Recommendation for third-party plugins:** prefer the **`hmiAction`** entry (§1.2a). The reconstructed SDK ABI (`bmw_list.h`) exposes model/property/handler/post helpers but **no** general "navigate to hmiState" call, so a `raAction` entry that must then move the user to a screen relies on framework behavior this SDK does not fully pin down. `hmiAction` navigation is handled entirely by the HMI and needs no native code — it is the reliable, portable door. Use the `raAction` entry only when you specifically need to run code *before* anything is shown (the OEM availability-gate pattern).

### 1.6 Menu-entry previews — `previewModel`

An entry or menu button may carry `previewModel="<id>"`, referencing a `raPreviewModel` model that renders a preview of the target when the entry is highlighted. The OEM Special-Vehicle entries use it pervasively:

```xml
<!-- SecurityMenu.xml:65 (entry) and its model (same pluginApp) -->
<entryButton action="25" id="34" model="28" previewModel="1002" text="Scheibenheizung"> ... </entryButton>
...
<raPreviewModel id="1002" modelType="StatePreview"   previewState="32"/>
<raPreviewModel id="1019" modelType="ContentPreview" previewState="32"/>
```

`modelType` is `StatePreview` or `ContentPreview`, and `previewState` names the state being previewed. This is a menu-*appearance* concern; the model plumbing (`raPreviewModel` alongside `raListModel`/`raDataModel`) is covered in `06-runtime-api-reference.md`. If you do not set `previewModel`, the entry simply shows no preview.

---

## 2. Screens and the navigation graph

### 2.1 `hmiState` = one screen; `hmiAction target=` = the edges

Every `<hmiState>` is a screen, identified by a plugin-local integer `id`. Navigation is a plain directed graph: a component's `action=` names an `hmiAction`, and that action's `target=` is the id of the screen to switch to. The reference plugin's graph is a clean three-level tree:

```
entryButton(action=10) ──hmiAction 10 target=100──▶ state 100  "PowerTools"
   state 100 button(action=11) ──hmiAction 11 target=200──▶ state 200  "Read DTCs"
   state 100 button(action=12) ──hmiAction 12 target=300──▶ state 300  "SVT"
```

```xml
<!-- Diagnostics.xml:22, 39-43 -->
<hmiAction id="10" target="100"/>
<hmiAction id="11" target="200"/>
<hmiAction id="12" target="300"/>
...
<hmiState id="100" text="PowerTools">
  <components>
    <button id="2" action="11" text="Read DTCs"/>   <!-- -> state 200 -->
    <button id="7" action="12" text="SVT"/>          <!-- -> state 300 -->
  </components>
</hmiState>
```

Two kinds of action live side by side in `<actions>` and must not be confused (full treatment in `03-descfile-xml-reference.md` / `05-cxx-abi-and-data-types.md`):

- **`hmiAction`** — pure screen navigation, handled entirely by the HMI. `target=` is another `hmiState`. Your `.so` never sees it.
- **`raAction`** — a callback **into your plugin**. When the component fires, the framework invokes the handler you registered with `addHandler(actionId, delegate)`. In the reference plugin, `raAction 21` ("Build module list") lands in `Diagnostics::onBuild` (`diagnostics12.cpp:329`). Use `hmiAction` to *go somewhere*, `raAction` to *do something*.

A component carries only one `action=`. To both navigate and react, navigate with `hmiAction`, then react in that destination screen's `onInit`-registered handlers.

### 2.2 `parentId` and the back edge

Forward edges are `hmiAction target=`. The **back** relationship is expressed with `parentId` on the child `hmiState`, which also matches a separate `*_Tree.xml` when a plugin ships one. The OEM SecurityMenu declares its hierarchy both ways — inline `parentId` (`SecurityMenu.xml:229` `<hmiState id="96" parentId="95" …>`) and as a standalone tree:

```xml
<!-- SecurityMenu_Tree.xml -->
<hmiStateTree>
  <state id="DLG_SEC_Kommunikation"   parent=""/>
    <state id="DLG_SEC_Sprechanlage"  parent="DLG_SEC_Kommunikation"/>
    <state id="DLG_SEC_Durchsagen"    parent="DLG_SEC_Kommunikation"/>
  <state id="DLG_SEC_Sondersignalanlage" parent=""/>
    <state id="DLG_SEC_Anhaltesignalgeber" parent="DLG_SEC_Sondersignalanlage"/>
</hmiStateTree>
```

Top-level screens use `parent=""`. Setting `parentId` lets the HMI render the correct title/back-chain automatically. The reference plugin's states 200/300 hang off the menu (100) via their `hmiAction`s and do not set `parentId`; for deeper trees, set it so the built-in back button behaves.

### 2.3 `focusEvent` — reacting to a screen becoming focused

`<focusEvent>` (in `<events>`) fires when a state gains focus or a model's value changes, letting you refresh data lazily instead of on load. `SecurityMenu.xml:89` `<focusEvent id="31" target="32"/>` runs when state 32 is focused; `ActiveSeating.xml:166` `<focusEvent id="23" targetModel="12"/>` fires on a model change. This is the hook to populate a screen the moment the user opens it. The framework is explicit that **popups are not part of this graph**: `[AbstractPopupHmiState] Popups must be opened via popup event. Not via hmiAction, nor via focusEvent`.

---

## 3. The layout system

Within a screen, components are placed one of two ways: **flow** into a stock template via a `layoutGroup`/`slotName`, or **absolute** via coordinate properties. You can mix them in one state (SecurityMenu does: flowed `List` buttons plus absolutely-placed images).

### 3.1 `layoutGroup "List"` — the stock list template and its width

A `<layoutGroups>` block with a single `<layoutGroup name="List" width="…"/>` selects the standard vertical-list layout for the screen and, crucially, **sets the width of that list region**. Two idioms appear:

- **Full-width list — `width="1280"`.** The list spans the whole content area; the scrollbar sits at the far right. Used for a plain single-column screen.

  ```xml
  <!-- Diagnostics.xml:48-51 (DTC screen) -->
  <hmiState id="200" text="Read DTCs">
    <layoutGroups><layoutGroup name="List" width="1280"/></layoutGroups>
    ...
  ```

- **Master column — `width="700"`.** The list is confined to a 700 px left column, leaving the remaining ~580 px (of the ~1280-wide content area) free for a detail pane you place absolutely (§3.3, §4). This is the OEM Special-Vehicle idiom.

  ```xml
  <!-- Diagnostics.xml:78-81 (SVT master-detail) ; mirrors SecurityMenu.xml:875-877 -->
  <hmiState id="300" text="SVT">
    <layoutGroups><layoutGroup name="List" width="700"/></layoutGroups>
    ...
  ```

Components join the list by carrying `slotName="List"` (the OEM SecurityMenu buttons do: `SecurityMenu.xml:1088` `<button … slotName="List" …>`, 26 such rows). In the reference plugin the components sit in the default slot and are pulled into the list template implicitly; `slotName="List"` is the explicit, OEM-faithful form. The framework confirms the mechanism internally with `generateLayoutGroups` / `deferredInitLayoutGroups` and the `CRhmiLayoutGroup` / `CHmiUILayoutGroup` classes, and warns when a slot is missing (`- Error: List slot not found in mainMenu widget!`).

### 3.2 Per-list width — `<property id="6">`

Independently of the group width, an individual `<list>` can set its own width with **property 6**. OEM navigation lists use plain pixel widths, and one shipping ServiceMenu list uses a two-column spec:

```xml
<!-- HmiGen_NavigationRemoteService.xml:472-474 (pixel width) -->
<list action="134" id="132" model="133">
  <properties><property id="6" value="400"/></properties>
</list>

<!-- HmiGen_TVRemoteService.xml:202 (two-column "fixed,fill" spec) -->
<property id="6" value="317,*"/>
```

Observed values: `400`, `460` (both in `HmiGen_NavigationRemoteService.xml`), and `317,*` — a two-column `fixed,fill` spec that appears exactly once carve-wide, in the normal shipping `HmiGen_TVRemoteService.xml` (not an editor file). Use property 6 to size a list that must share a row with something else; use `layoutGroup width` to size the list *region* for the whole screen. The comma column-spec form is parsed **generically** by the base `CAbstractList` (property 6 = `LIST_COLUMNWIDTH`, with a no-condition parse path), not special-cased to the OEM ServiceMenu — so a third-party RA-plugin list parses it the same way; only the on-screen render on a plugin list is still unverified on-car (see §8).

### 3.3 Absolute positioning — `POSITION_X/Y`, `WIDTH`, `HEIGHT`

Any component can be pinned with four coordinate properties, in the screen's pixel space:

| id | name | unit |
|---|---|---|
| `20` | `POSITION_X` | px from left |
| `21` | `POSITION_Y` | px from top |
| `9`  | `WIDTH` | px |
| `10` | `HEIGHT` | px |

The reference plugin places its detail label to the right of a 700 px master column:

```xml
<!-- Diagnostics.xml:90-97 -->
<label id="11" model="52">          <!-- Richtext, display-only -->
  <properties>
    <property id="20" value="720"/>  <!-- X: just right of the 700px list -->
    <property id="21" value="96"/>   <!-- Y -->
    <property id="9"  value="520"/>  <!-- W: 720+520 = 1240, inside the ~1280 area -->
    <property id="10" value="360"/>  <!-- H -->
  </properties>
</label>
```

The OEM Sondersignalanlage screen places ~20 images this way over a 700 px list (`SecurityMenu.xml:878-1087`), e.g. `POS_X=765 POS_Y=80 W=480 H=351`. Coordinates are relative to the screen's content area; the ID5 main display's plugin content area is ~1280 px wide (consistent with `1280` full-width lists and the 720+520 right pane). Fullscreen RSE widget states use a larger 1440×810 space with negative offsets (`ActiveSeating.xml:238-241` `W=1440 H=810 X=-90 Y=-36`) — mind which surface your state renders on.

### 3.4 State layout template — `<property id="24">`

A **state-level** `<property id="24">` (inside the `hmiState`'s own `<properties>`, not a component's) selects the screen's layout template. Values seen: `3` on list/master screens (`SecurityMenu.xml:872`, `ActiveSeating.xml:194`) and `13` on fullscreen widget screens (`ActiveSeating.xml:172,208,297`). Treat property 24 as "which stock screen frame this state uses"; leave it unset for the default list frame (the reference plugin does, and relies on `layoutGroup` alone).

---

## 4. Recipe: the master-detail screen

The most useful compound pattern — a selectable list on the left driving a read-only detail pane on the right — is worth a step-by-step. It is exactly the reference plugin's SVT screen (`Diagnostics.xml:78-98`), and it mirrors the OEM Special-Vehicle 700 px idiom.

1. **Scope the list to a master column.** `<layoutGroup name="List" width="700"/>` on the state.
2. **Declare a selectable list** bound to a list model, with an `raAction` so your `.so` learns which row was picked:
   ```xml
   <list id="10" model="51" action="25"/>   <!-- left: selectable; fires raAction 25 -->
   ```
3. **Declare a display-only detail** to the right, bound to a data model, pinned absolutely in the free space. The reference uses a **`label`** (with a `Richtext` model), *not* another list: a label is not focusable, so it never steals a scroll target (rationale in `diagnostics12.cpp:167-169`). **Caveat:** a label is `LT_Label_A4A`, one line high; in the stock column it shows only the first line of its text, and whether `HEIGHT` gives it more is untested. The proven multi-line text block is a display-only **Richtext list** filled with one cell (`03-descfile-xml-reference.md`, `label`).
   ```xml
   <label id="11" model="52">
     <properties>
       <property id="20" value="720"/><property id="21" value="96"/>
       <property id="9" value="520"/><property id="10" value="360"/>
     </properties>
   </label>
   ```
4. **Wire selection in C++.** Register a handler for the list's `raAction`; on each row-select, read the row index from the `Parcel`, remember it, and rebuild the detail model with `updateModel`. The reference does this in `Diagnostics::onSvtRow` → `fill_svt_right()` (`diagnostics12.cpp:290-296, 170-190`), pushing one `\n`-joined string into model 52 via `updateModel(SVT_DETAIL_MODEL, BasicString<char>(buf))`.
5. **Optionally grey the driving button** while a background read runs, via `setProperty(component, SELECTABLE=2, Parcel(false))` (`diagnostics12.cpp:194-197`) — see §6 and `05-cxx-abi-and-data-types.md` for `setProperty`.

Model plumbing (`raListModel` vs `raDataModel modelType="Richtext"`, and how `updateModel` deep-copies the table) belongs to `06-runtime-api-reference.md`; here the point is purely the *layout* recipe: **700 px list + absolutely-placed Richtext label = master-detail** (with the one-line caveat in step 3).

---

## 5. The OPTION-button menu (`optionComponents`)

Hardware/rotary "OPTION" gives a screen a context menu without spending room on-screen. Declare it as `<optionComponents>` inside the `hmiState`; its buttons carry `raAction`s straight back to your plugin:

```xml
<!-- Diagnostics.xml:55-58 -->
<optionComponents>
  <button id="12" action="26" text="Re-read DTCs"/>   <!-- raAction 26 -->
  <button id="13" action="27" text="Clear DTCs"/>     <!-- raAction 27 -->
</optionComponents>
```

`HmiMain3D` parses this via `createOptionComponents` (string confirmed in the binary); for an RA plugin the option buttons behave like any other `raAction` source — register handlers in `onInit` exactly as for on-screen buttons (`diagnostics12.cpp:342-347`, `onReReadDtc`/`onClearDtc`). Use it for whole-screen verbs (re-run, clear, export) that would clutter the main list. OEM screens also use an empty `<optionComponents/>` to declare "this screen has an OPTION menu, populated elsewhere" (`SecurityMenu.xml:1405`).

Related but distinct: **`toolbarHmiState`** + `<toolbarComponents>` give a screen a persistent on-screen toolbar of image buttons (`ActiveSeating.xml:285-292`), and are the right tool for media-style transport controls rather than a hidden option list.

---

## 6. Property-id catalog (layout & component state)

Every `<property>` is `id` + `value`. Ids are shared across all component types; a given id is only meaningful on components that honor it (a `separator` ignores `SELECTABLE`: `[AbstractSeparator::setProperty] Property SELECTABLE ignored for separator`). Below is every id seen in the carve's DescFiles, with the value type and effect. **V** = carve-verified meaning; **R** = reconstructed/inferred (confirm on your unit before relying on it).

| id | name | applies to | value | effect | conf. |
|---|---|---|---|---|---|
| `2` | `SELECTABLE` | button, checkbox, list, label, widget (not separator) | `true`/`false` | Enabled + focusable when true; greyed/inert when false. Set at runtime with `setProperty(comp, 2, Parcel(bool))`. A label with `2=true` becomes focusable. | **V** |
| `3` | `VISIBLE` *(avail.)* | image (mostly), entryButton | `true`/`false` | On images, shows/hides the element (`false` = hidden layer, toggled at runtime). On `entryButton`, OEM sets `false` — an availability gate rather than draw-visibility. | R |
| `6` | list width / columns | `list` only | px int or `"fixed,*"` | Width of that individual list, or a column spec (`317,*` = fixed+fill, `HmiGen_TVRemoteService.xml:202`). Independent of `layoutGroup width`. | **V** |
| `9` | `WIDTH` | any (with absolute pos) | px int | Component width. | **V** |
| `10` | `HEIGHT` | any (with absolute pos) | px int | Component height. | **V** |
| `17` | `ALIGNMENT` | image (`0`), label (`1`) | small int | Content/text **alignment** enum (confirmed via BMW's own `SecurityMenu_Editor.xml` symbolic names + the `PropertyType::ALIGNMENT` setter string in `HmiMain3D`). `0` = default (all images); `1` = used on the two centered header labels. The enum member→value constants aren't pinned. | **V** (name) |
| `20` | `POSITION_X` | any (with absolute pos) | px int (may be negative) | X from content-area left. | **V** |
| `21` | `POSITION_Y` | any (with absolute pos) | px int (may be negative) | Y from content-area top. | **V** |
| `22` | `BOOKMARKABLE` | `hmiState` (state-level) | `false` | Bookmark/favorite-ability of the element. On a state/container it's a **no-op** — `HmiMain3D` logs `[CAbstractContainer::setProperty] … BOOKMARKABLE ignored for states!` — which is why the OEM HmiGen state-level use (`Navigation:261`, `Phone:70`, `TV:207`, `Gracenote:24`) is always `false`. | **V** (name) |
| `23` | entryButton flag | `entryButton` only | `2` | On `entryButton` only (`Diagnostics.xml:18`, `ActiveSeating.xml:9`). In the **component** property namespace id 23 = `SPEAKABLE` (a *deprecated* speech-command flag — `HmiMain3D`: `SPEAKABLE property not supported` / `property SPEAKABLE=1 … no longer supported`); it is **not** a button kind/priority. Whether an entryButton honors id 23, and what value `2` means there, is unconfirmed — no entryButton consumer of it found. | R |
| `24` | state layout template | `hmiState` (state-level) | `3`, `13` | Selects the screen frame: `3` = list/master screens, `13` = fullscreen widget screens. | R |
| `39` | `BACKGROUND` | `image` | `0` | Image **background fill** (confirmed via `SecurityMenu_Editor.xml` symbolic names, 103×, in the field-39 slot). `0` = none/transparent (the only value in the carve). Build-time only — `HmiMain3D` has no runtime `setProperty` case for id 39 (falls to the silent default). | **V** (name) |

Notes:
- **Component `<property>` vs. state `<property>`.** Ids `22` and `24` sit in the `hmiState`'s own `<properties>` and affect the screen; all others sit in a component's `<properties>` and affect that component.
- **Set at build time or at runtime.** Any of these can be written in the DescFile; `SELECTABLE` is writable live from the `.so` via `setProperty` (`bmw_list.h:156`). The coordinate ids `9/10/20/21` **are** dispatched to real position/size handlers by `HmiMain3D`'s `setProperty` switch (each runs the per-layout component setter, not the silent default) — the handler is wired; only the live on-screen effect is still to be seen on-car (see §8).
- **These mirror OEM patterns.** The reference plugin deliberately copies `HmiGen_NavigationRemoteService` (list widths, `SELECTABLE` on labels) and the SecurityMenu Special-Vehicle screens (700 px `List` + absolute images) — cite those two files when you need a second example of any id.

---

## 7. End-to-end: the reference plugin as a map

Putting §1–§6 together on `Diagnostics.xml` (the working reference), the entire menu/layout is:

```
pluginApp  applicationType=VehicleInformation  weight=200  text="PowerTools"
│
├─ entryButton(action=10, prop23=2) ──hmiAction 10──▶ state 100 "PowerTools"  [door, §1.2a]
│
├─ state 100  (menu)                                                    [§2.1]
│    ├─ button "Read DTCs"  action=11 ──hmiAction 11──▶ state 200
│    └─ button "SVT"        action=12 ──hmiAction 12──▶ state 300
│
├─ state 200 "Read DTCs"   layoutGroup List width=1280  (full-width)    [§3.1]
│    ├─ optionComponents: "Re-read DTCs"(ra26) "Clear DTCs"(ra27)        [§5]
│    ├─ button "Build module list"(ra21, SELECTABLE=true)               [§6]
│    ├─ button "Read DTCs"(ra22, SELECTABLE=false → greyed)             [§6]
│    ├─ separator
│    └─ list model=50 action=ra23
│
└─ state 300 "SVT"         layoutGroup List width=700  (master column)  [§3.1, §4]
     ├─ button "Read SVT"(ra24, SELECTABLE=true)
     ├─ separator
     ├─ list  model=51 action=ra25         (left: selectable master)
     └─ label model=52  @ X=720 Y=96 W=520 H=360  (right: Richtext detail) [§3.3]
```

Every arrow out of a menu button is an `hmiAction target=` (navigation, HMI-handled); every `ra##` is an `raAction` callback into your `.so`, registered in `onInit`. Every box is an `hmiState`. Every placement is a `layoutGroup` choice plus, where needed, the property-6/9/10/20/21 catalog above. That is the complete menu-and-layout surface of an RA plugin. Note the contrast with the OEM `Settings__SpecialVehicle` apps, whose **entry** buttons fire a `raAction` instead (§1.5) — the reference plugin uses the simpler `hmiAction` entry throughout.

---

## 8. Open questions & build-dependent caveats

These are the points this SDK cannot settle from a single-car carve. Confirm on your own unit before depending on them.

| Topic | Status |
|---|---|
| **Property-id names/effects** | `SELECTABLE`(2), `WIDTH`(9), `HEIGHT`(10), `POSITION_X`(20), `POSITION_Y`(21), and per-list width(6) are carve-verified. The names/effects of ids `3, 17, 22, 23, 24, 39` are **reconstructed** from observed values and context (flagged **R** in §6). |
| **`applicationType` portability** | Names resolve through compiled HMI generation-rule data, not loose strings. Only `ServiceMenu`, `Settings__SpecialVehicle`, and `Custom` appear in shipping DescFiles here. `VehicleInformation` is the reference author's choice; its My-Vehicle placement was observed for **one** build and is not proven portable. Prefer `Custom` (§1.4) when you cannot confirm a named rule exists. |
| **`applicationWeight` sort direction** | Ascending vs. descending is undetermined — both plugins that set it use `200`. |
| **`Custom` anchor ids** | `insertStateID`/`insertAfterFocusID`/`replaceFocusID`/`entryButtonFocusID` are **native** HMI state/focus ids specific to a build; this SDK does not enumerate the native state tree. A `Custom` anchor is only as portable as the anchor state it names. |
| **Coordinate space** | The ~1280 px main-display content area and the 1440×810 RSE surface are **inferred** from coordinate values, not a documented display spec. |
| **Live coordinate updates** | `setProperty` **dispatches** `9/10/20/21` to real position/size handlers in `HmiMain3D` (the id switch runs the per-layout component setter for each; unhandled ids hit a silent no-op instead) — statically wired, confirmed in the carve. Only `SELECTABLE`(2) has been *observed* live; the coordinate ids' runtime effect is still to be confirmed on-car. |
| **Two-column list spec (`317,*`)** | Parsed **generically** by the base `CAbstractList::setProperty` (property 6 = `LIST_COLUMNWIDTH`), not special-cased to the OEM ServiceMenu — it has a no-condition (`condition: 0xFFFFFFFF`) parse path and is gated only by list type (`Richtext` lists ignore it). So a plain `<property id="6" value="317,*"/>` on a non-Richtext RA-plugin list is parsed the same way; only the on-screen render on a plugin list is still unverified on-car. |
| **`raAction` entry navigation** | The OEM entry-button→`raAction` path (§1.5) hands control to native code; the reconstructed ABI exposes no general "navigate to hmiState" helper, so a third-party plugin cannot rely on it to move screens. Use an `hmiAction` entry. |

---

## Sources

All facts above come from an **owner-authorized offline flash carve** of the author's own head unit plus **end-to-end validation of the working reference plugin on the author's OPT_DEBUG-enabled unit** (it is discovered, `dlopen`'d, its menu entry appears, its `hmiState`s render, and `updateModel`/`addHandler`/`setProperty` all work). A stock unit enforces **no signature** on plugin load (the load path links no cryptography and has no signature branch — see `01 §3.1` / `14`), confirmed on-car by the owner's unsigned plugin loading from `Plugins/`; the `/PluginsCoded` root additionally carries a coding-value enable-list (`isVariantSet 0x0C0E/0x9C55`). Primary sources are cited inline as `path:line` or `path (symbol/string)`:

- **Reference plugin (verified end-to-end on the author's OPT_DEBUG-enabled unit):** `capabilities/plugins/reference/ (example-plugin/{Diagnostics.xml,diagnostics.cpp}, sdk/bmw_list.h)`.
- **OEM DescFiles (carve-confirmed):** `.../ID5/data/ro/PluginsCoded/SecurityMenu/{SecurityMenu.xml,SecurityMenu_Tree.xml}`, `.../PluginsCoded/ActiveSeating/ActiveSeating.xml`, `.../ID5/data/ro/HmiGen_{Navigation,TV,Phone}RemoteService.xml`.
- **Loader strings:** `.../ID5/bin/HmiMain3D` (quoted verbatim).

Facts labeled **R** in §6 and everything under §8 are **reconstructed** or **build-dependent**: the SDK ABI headers (`bmw_abi.h`, `bmw_list.h`) are hand-reconstructed from symbol tables and behavior, and property-id *names* are inferred from observed values. Treat them as starting points to confirm on your own unit, not guarantees.

---

*Next: `05-cxx-abi-and-data-types.md` (how `raAction`s reach your code and how `setProperty`/`updateModel` push state back) and `06-runtime-api-reference.md` (`raListModel`/`raDataModel`/`raPreviewModel`, `Richtext`, and the `DataTable` deep-copy contract).*
