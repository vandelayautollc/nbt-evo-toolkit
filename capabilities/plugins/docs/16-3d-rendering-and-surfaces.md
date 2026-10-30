# 16 — 3D Rendering & Surfaces

Whether an RA plugin can put its **own 3D / arbitrary GPU-drawn content** on screen — and at
what privilege. Short version: the HMI will **not render 3D *for* you** (there is no
scene/mesh/model3d you declare and fill at runtime), but the process a plugin is `dlopen`'d into
**is** a full OpenGL ES 2.0 / EGL / QNX-Screen / GENIVI-ilm client, so a plugin *can* render its
own 3D **in-process** and get it on screen two ways — composite a live GPU surface through the
HMI's one **surface component**, or render offscreen and push the frames as **stream-image
bitmaps** (`docs/15` §2.2). The image route is fully in-API and works uncertified today; the
surface route's *permission* is open to an uncertified plugin, but its *plumbing* is not part of
the sanctioned RA API and is unproven end-to-end.

> **Scope & authorization.** Everything here was reverse-engineered from an **offline flash
> carve** and **owner-authorized** work on the author's **own titled NBT-Evo head unit**, running
> 100 % vanilla OEM firmware with only `OPT_DEBUG` enabled (system-service access; it does not
> change what the HMI accepts). No hardware was touched for this document — it is a static read of
> a flash carve. No VIN, private network address, or car-specific diagnostic payload is part of
> this SDK. Build and test only on hardware you own.

> **Evidence legend.**
> **[CONFIRMED]** — read the disassembled logic, or direct byte/file evidence (a symbol, an RTTI
> class name, an ELF `NEEDED` entry, an on-disk OEM file, a string at an offset). Re-verified
> against the carve for this document where noted.
> **[STRONG]** — a structural fact (import-set intersection, a factory registry, a constructor
> denylist, "no gate string exists on this path") that forces the conclusion without a full
> instruction trace.
> **[PLAUSIBLE]** — an indirect reading the carve does not fully settle.
> **[UNKNOWN]** — the disassembly did not reach it; stated as an open question, not a guess.
>
> This section is **part RE, part engineering**. Every forward-looking engineering judgement is
> labelled **[ENGINEERING-INFERENCE]** and is grounded in what is mapped into the process plus the
> QNX-Screen / GENIVI-ilm architecture — never in wishful reading. **"The mechanism exists in the
> binary" and "an *uncertified* plugin can actually reach it" are graded separately throughout.**
>
> `HmiMain3D` **virtual addresses** are used for disassembly walks (matching `docs/14`; e.g. the
> permission getter entry `0x2512878`); **file offsets** are used for string/data citations. For
> this single-`LOAD` EXEC image **vaddr = fileoff + 0x100000**.

Related docs: **`03`** (DescFile grammar), **`05`** (C++ ABI & data types), **`06`** (runtime
API), **`07`** (threading & the worker→dispatcher hand-off), **`14`** (signing, coding & the
184-bit permission bitset), **`15`** (graphics, gauges & images — the stream-image escape hatch).

---

## 0. TL;DR — is there any facility to render our own 3D?

**There is no declarative 3D, but there are two in-process render-your-own-3D routes. One (stream
image) works uncertified today; the other (surface composite) has an open permission gate but
unproven plumbing.** In three parts:

1. **No "give the HMI a mesh" path — [CONFIRMED].** The RemoteApp model family is
   `Bool / Chart / Data / DataRequest / Gauge / Image / Int / List / Preview / Roll` — **all 2D
   UI, none a scene/mesh/model3d model** — and the DescFile `TAG_*` set has **no**
   scene/mesh/model3d/dyngfx tag. `DynGFX3D` is a native scene traversal with no plugin entry
   point. So nothing you *declare and fill at runtime* becomes geometry. The native 3D engine
   (Candera/INES: OpenCTM meshes + GLSL-ES shaders + a compiled `scene.pbx`) is real and
   data-driven, but it is fed by native code, not by an RA model.

2. **The GPU is already in your address space — [CONFIRMED].** A plugin `.so` is `dlopen`'d
   **into** `HmiMain3D`, which `NEEDED`s `libGLESv2.so.1`, `libEGL.so.1`, `libscreen.so.1` (QNX
   Screen), `libilmClient.gpp.so.1` (GENIVI IVI Layer Manager), `libtilerusr.so.1`,
   `libOpenCTM.so`, `libDevIL.so`, and imports the **entire GLES2 draw API + EGL context/surface
   creation + the full FBO/`glReadPixels` readback path**. A plugin can stand up its **own** EGL
   context + offscreen FBO/pbuffer in-process; multiple EGL contexts already coexist in this one
   process natively, so this is an existing pattern, not a novel demand on the driver.

3. **Two routes to screen, split by certificate:**
   - **Route B — offscreen → stream image (uncertified, works today): [STRONG].** Render 3D into
     a plugin-owned FBO on a private GL worker thread, `glReadPixels` to RGBA, hand the buffer to
     the dispatcher thread, push it through a `raImageModel` stream image
     (`CRemoteAppImageModel::loadImageStreamResource`, `docs/15` §2.2). Rides the `ImageDynamic`
     bit, which **defaults set** — **no `RHMI_PERM_LAYER` needed**. Cost: per-frame
     readback+re-upload, the `docs/15` stream size cap, modest resolution/framerate.
   - **Route A — composite your own live surface via `<surfaceComponent>`: permission open
     [CONFIRMED at the gate], reachability [STRONG], full use [PLAUSIBLE].** The HMI's one facility
     for *externally-rendered* GPU content is the **surface component**, whose init requires
     `RHMI_PERM_LAYER` = **bitset index 19**, which is **default-set** — an uncertified plugin
     passes the gate. But the component only **composites a surface that already exists on a valid
     layer**; to show its *own* 3D a plugin must create+drive its own ilm/Screen/EGL surface with
     **native calls outside the RA API**, and no OEM or plugin DescFile declares `<surfaceComponent>`
     at all. Best quality (live, hardware-composited, zero readback) but unproven plumbing.

**The uncertified-vs-certified split, up front:** *Certificate buys you almost nothing here.* The
only 3D-relevant permission bit, `RHMI_PERM_LAYER` (idx 19), is **already granted by default**
(`docs/14` §4.4); a `DevelopmentCertificate` only unlocks the 9-index privileged denylist
`{13–18,20,21,22}`, and **19 is not in it**. So the real gate on rich 3D is **not a permission
bit** — it is (a) the missing declarative path, (b) for Route A, native surface/layer plumbing
outside the API, and (c) for a bundled-asset path, an offline toolchain problem. An uncertified
plugin has the *same* 3D reach as a certified one; the recommended path for both is Route B.

**Bottom line:** yes, you can render your own 3D — **in-process, into a bitmap, pushed as a stream
image (Route B), uncertified**. Everything richer (a live composited surface) is permission-open
but architecturally out of the sanctioned API.

---

## 1. No declarative 3D — the HMI will not render geometry *for* you

The single most important negative result: **there is no RemoteApp model, and no DescFile tag,
that lets a plugin hand the HMI a mesh, a scene, or a 3D object to draw.** You cannot stream
geometry the way you can stream a bitmap (`docs/15` §2.2).

### 1.1 The RemoteApp model family is 2D-only — [CONFIRMED]

The `ra*` model vocabulary in `HmiMain3D` is exactly:

```
raBoolModel  raChartModel  raDataModel  raDataRequestModel  raGaugeModel
raImageModel  raIntModel  raListModel  raPreviewModel  raRollModel
```

(re-verified for this doc: `strings | grep -oE '^ra[A-Za-z]+Model$'`). Every one is a 2D UI
primitive — booleans, numeric values, data tables/requests, a 2D chart, images, lists, a preview
pane, a spin-roll. **None is a scene / mesh / model3d / surface model.** The corresponding RTTI
classes are `CRemoteApp{Bool,Data,Gauge,Image,Int,List,Preview,Roll}Model` (+`CRemoteAppAction`);
there is no `CRemoteApp*SceneModel` / `*MeshModel` / `*Model3D`. The `Preview` model
(`CRemoteAppPreviewModel`) generates **2D UI-object** widgets by type name for content/state
previews — not geometry. **[CONFIRMED — RTTI + tag-string scan]**

*(Correction to a premise carried in from earlier notes: the family is ten `ra*` tags, not eight —
`raChartModel` and `raDataRequestModel` are also present. Neither is 3D, so the answer is
unchanged; the premise is just completed here.)*

### 1.2 No 3D DescFile tag; `DynGFX3D` is native-only — [CONFIRMED]

The DescFile tag set (`CHmiGenStringConstants::TAG_*`) contains **no** `TAG_SCENE`, `TAG_MESH`,
`TAG_MODEL3D`, `TAG_DYNGFX`, or `TAG_3D` (re-verified: `strings | grep -iE 'TAG_(SCENE|MESH|MODEL3D|DYNGFX|3D)'`
returns nothing). The graphics tags a plugin *can* declare are the 2D ones catalogued in `docs/15`
§3 (`TAG_IMAGE`, `TAG_RAIMAGEMODEL`, `TAG_GAUGE`, `TAG_WIDGET`) plus `TAG_SURFACECOMPONENTE`
(§2 below).

`DynGFX` / `DynGFX3D` — the engine's dynamic-graphics traversal (`CDynGfx3DTraversal`,
`CDocumentTraversal::DYNGFX3D`, `startDynGfx3D`, logs `DynGFX3D has no HotSpots`, `dyngfx3D must
not be 0`) — runs **over the compiled native scene tree**, has **no** DescFile tag, and exposes
**no** plugin-facing binding. It is not plugin-declarable. **[CONFIRMED]** (Consistent with
`docs/15` §3.)

### 1.3 The native 3D engine exists and is data-driven — but the data is native-fed

For completeness (and to head off the "surely I can just drop in a `.ctm`" question): `HmiMain3D`
is a **Candera/INES** GLES2/EGL scene-graph engine. A native 3D object is assembled from four data
layers, all on-disk under `data/ro/common`:

| Layer | Format | Binary anchor |
|---|---|---|
| Geometry | **OpenCTM** `meshes/*.ctm` | `CHmiResourceMesh::loadFromBinaryStream`, `ctmNewContext`/`ctmLoadCustom`, `Hmi_Ines_MeshRender` |
| Materials | **GLSL-ES** `*.vert`/`*.frag` | `.HmiScenegraph.TMaterial` |
| Scene | compiled **HmiScenegraph** protobuf `scene.pbx` | `.HmiScenegraph.TMesh/.TNode/.TCamera`, `Scenegraph.pb.cc` |
| Widget wrapper | **HmiWidget** protobuf `.pbw` | `.HmiWidget.TLayoutSceneGraphProject` |

An `ego_model/<chassis>.zip` is a self-contained 3D bundle (meshes/*.ctm one-per-material,
shaders, `scene.pbx`, `widget.pbw`); the generic on-screen node is the native widget
`CGfxWidget3DModel`, and the native base 3D widget types with real factories are
`eWidgetType_{Asset, Model, Scene, SceneBase, Layer, Transform}` (re-verified). **[CONFIRMED for
the format/classes]** This engine is **generic and data-driven** — which is what makes the
*bundled-asset* idea in §5 conceivable — but every shipped scene is fed by native code, and
**nothing an RA plugin declares at runtime reaches it.**

> A note on why "just add a `WidgetDBFile`/`AssetDBFile` of your own meshes" is not a §3 route:
> the app framework *does* recognise per-plugin-app `WidgetDBFile` and `AssetDBFile` manifest
> params (re-verified present in `HmiMain3D` and `libAppFramework.A.so`), and the load path is
> **not** permission-gated — but **no manifest on this device uses them** (the only two App-plugins
> in the carve, `SecurityMenu` and `ActiveSeating`, are both `PluginsCoded`, both certificated, and
> both ship only `ImageDBFile`/`TextDBFile`). It is a present-but-never-exercised static bundle
> path whose real wall was authoring valid compiled Candera `.pbw`/`scene.pbx` (an offline toolchain
> problem, not a permission bit; solved offline — see the RSVI tooling in [`../../vehicle_models/`](../../vehicle_models/)). It is a *build-time asset* route, not *rendering your own 3D*, so
> it lives in §5's open questions rather than as a live route. **[params + ungated load: params
> CONFIRMED, ungated STRONG; end-to-end use: PLAUSIBLE]**

---

## 2. The surface component — the live-3D route

`HmiMain3D` has **exactly one** facility for putting *externally-rendered* GPU content on screen:
the **surface component** (`CAbstractSurfaceComponent`, DescFile tag `surfaceComponent`). It does
**not render anything itself** — it takes a surface **another renderer already produced** (a QNX
Screen / GENIVI-ilm surface, identified by a numeric *surface id* carried in a model) and
**composites that foreign render target into an HMI layer** of the single `HmiMain3D` scene.

### 2.1 What it is on the DescFile side — [CONFIRMED it is registered; STRONG that a plugin may declare it]

`surfaceComponent` is a first-class entry in the **one** HmiGenEngine component-factory table —
the same registry that dispatches every other component tag.
`CHmiGenStringConstants::TAG_SURFACECOMPONENTE` (`0x393856c`) dereferences to the literal
`"surfaceComponent"` (`0x3010b6e`), and its factory row sits inline in the dispatch table
(`{id 0xa4, flags 0x000a0022, factory-thunk, tag→0x393856c}`) between the ordinary component rows.
Its bound model attribute is **`surfaceIdModel`** (`0x3938600` → `"surfaceIdModel"` `0x3010c6e`);
there is also a `layerIdModel` constant. The surface id is a **live, settable** value carried in
that model and updated through `valueChangedIdModels`, not a compile-time constant. **[CONFIRMED —
`nm -D` symbol → string deref + factory-row structure]**

**No OEM DescFile and no plugin DescFile in the carve declares it.** A `grep` for
`surfaceComponent`/`surfaceIdModel` across all of `data/ro` (including `hmiplugins/` and
`PluginsCoded/`) is empty (re-verified). So the tag exists and is wired into the shared parser
registry, but the plugin-parse → surfaceComponent-factory path is **never exercised** by a shipped
file.

That it is *plugin-declarable* is **[STRONG]**, not CONFIRMED: it lives in the same shared parser
registry that already handles the `<components>`/`<image>`/idModel elements OEM plugins do use; its
`init` reads the **owning app's** permission set (a per-app gate is only meaningful if apps/plugins
can instantiate the component); and unlike entry-button / notification-center / speech there is
**no** integrate-time "surface not allowed for remote app" rejection string. What is *not* nailed:
the RA-integrate dispatch into this specific factory was not byte-traced, and `surfaceIdModel` was
not confirmed to be one of the plugin-settable `ra*` model types (it reads like a plain idModel,
sibling to `imageIdModel`/`textIdModel`, which *are* plugin-declarable — **[PLAUSIBLE]**).

### 2.2 The mechanism — embedding a foreign surface — [CONFIRMED that it takes/validates/maps a surface id; layer-add is import/string inference]

`HmiMain3D` links the GENIVI IVI Layer Manager client (`libilmClient.gpp.so.1`) and QNX Screen
(`libscreen.so.1`) and imports `ilm_getPropertiesOfSurface`, `ilm_getSurfaceIDs`,
`ilm_getSurfaceIDsOnLayer`, `ilm_layerAddSurface`, `ilm_layerSetRenderOrder` (re-verified, all `U`
in dynsym). `CAbstractSurfaceComponent::valueChangedIdModels` takes the native surface id from the
model, runs it through a mapper, **maps it to a `wal3d::SurfaceId`**, then **validates window and
layer ids** before setting — read straight from its trace strings:

```
"mapped native surfaceId %x to wal3d::SurfaceId id %x"   (0x2e37c7f)
"window ID %x not valid, not setting"                    (0x2e37cec)
"Overriding layer ID with %x"                            (0x2e37d48)
"Got invalid layer ID for surfaceId %x, cannot set"      (0x2e37d9c)
```

The `CWal3dNBTevo` layer-manager wrapper owns the Screen-window / ilm-layer plumbing
(`createWindow`, layer add). Net: **the component adds an already-existing ilm surface to an HMI
layer** — it embeds a render target produced elsewhere; it never draws. **[CONFIRMED that it takes
a pre-existing surface id, validates window/layer ids, and maps native→`wal3d::SurfaceId` — from
strings + the getter/mapper; the specific `ilm_layerAddSurface` call site was *not* traced (no
direct ARM `BL` caller was found — the layer-add is reached via Thumb/indirect code, likely through
`CWal3dNBTevo`), so the "adds to a layer" verb rests on the import set + validation strings, not a
read dataflow into `ilm_layerAddSurface`.]**

`init` also requires a non-null **`IHmiCommAdapter`** — the per-app context bridge through which a
component reaches its owning application (its `CRhmiApplicationInfo` and its permission set). A null
adapter aborts with `"[CAbstractSurfaceComponent::init] No IHmiCommAdapter supplied, cannot init
component"` (`0x2e37b66`); the permission object is fetched from that same adapter (accessor
`0x2500d2c`, an offset-getter returning `adapter+0x28`) immediately before the permission test.

The canonical **native** producer of the composited surface is the **video pipeline**: the one
named surface-id model key in the binary is `VideoSurfaceId` (`0x2c37c90`, re-verified present),
and `libdce.so.1` (TI Distributed Codec Engine, OMAP hardware video decode) is `NEEDED`. So the
native use is compositing a decoded video/camera surface (rear-view camera, video playback, or a
companion render target) into the scene. **[STRONG that the native source is the video pipeline;
PLAUSIBLE on the precise consumer set.]**

### 2.3 The permission crux — `RHMI_PERM_LAYER` = bit 19, default-granted — [CONFIRMED at the gate; end-to-end reachability STRONG]

`CAbstractSurfaceComponent::init` (function at vaddr `0x11b2958`, source
`abstractcomponents/CAbstractSurfaceComponent.cpp`) gates itself on one capability. The
disassembly of the check is unambiguous:

```
0x11b29b4  mov r0, r6            ; r6 = IHmiCommAdapter (just null-checked)
0x11b29b8  bl  0x2500d2c         ; -> app permission object (adapter+0x28)
0x11b29bc  mov r1, #19           ; permission index 19 (0x13)  <-- RHMI_PERM_LAYER
0x11b29c0  bl  0x2512878         ; CRhmiApplicationPermissions::get(idx)
0x11b29c4  cmp r0, #0
0x11b29c8  bne 0x11b2a28         ; nonzero => granted, continue init
0x11b29cc  ...                   ; else: "No permission RHMI_PERM_LAYER, aborting" (0x2e37bbb)
```

`0x2512878` is the **184-bit-bitset getter** documented in `docs/14` §4.1 — a bounds-checked
function (`cmp r1,#183`; on the in-range path `byte = obj+4+(idx>>3)`, `bit = idx&7`, return
`(byte>>bit)&1`; out-of-range logs and returns 0), the same getter entry `docs/14` names at
`0x2512878`. The index passed is the literal **19**. **[CONFIRMED — disasm; the abort string
literally reads `RHMI_PERM_LAYER`, so `RHMI_PERM_LAYER == index 19` is pinned for *this* gate,
independent of `docs/14`'s GOT-reloc derivation.]**

The decisive half is the **default constructor** (vaddr `0x2512958`; re-verified `docs/14` §4.2):
it writes `0xFF` to all 23 bitset bytes (**every bit set**), then calls the set/clear helper
(`0x2512be0`) with value 0 for exactly the indices **13, 14, 15, 16, 17, 18, 20, 21, 22** — the
privileged denylist — **skipping 19**. So in the permissive no-certificate default, **bit 19 stays
set**; `get(19)` returns nonzero and the `bne` is taken.

Therefore `RHMI_PERM_LAYER == index 19 == LayerAccess`, and it is **granted by default**. This
pins `docs/14` §4.4's "layer access granted by default" (previously listed but with the behavioural
half only STRONG) to **CONFIRMED for this specific gate**: the surface component's own `init` is
what binds `RHMI_PERM_LAYER` to bit 19, and bit 19 is the one gap in the `{13–18,20–22}` denylist.
A `DevelopmentCertificate` is required only to *unlock the denied bits*; it is irrelevant here
because 19 was never denied.

> **Reachability nuance (honesty point).** The two *mechanical* halves — "init tests bit 19" and
> "the permissive-default object has bit 19 set" — are each **[CONFIRMED]** by disasm. The
> *composed* end-to-end verdict — "an uncertified plugin's surface-component `init` passes" — also
> needs the premise that an uncertified in-process plugin's app object **is** that permissive-default
> object. `docs/14` §4.3 grades that premise **[STRONG]** (no in-process code narrows the bitset,
> and the cert-narrowing path can't run for a `CLocalPluginAppConnector` — but the exact
> object-attach was not single-stepped). A composed claim inherits its weakest link, so the
> **end-to-end permission verdict is [STRONG]**, resting on two CONFIRMED sub-facts and one STRONG
> premise. Either way: **the permission bit is not what blocks Route A.**

### 2.4 So can a plugin render its own 3D *through* it? — [feasibility: ENGINEERING-INFERENCE, PLAUSIBLE]

The permission door is open, but the surface component is a **compositor, not a canvas**.
`valueChangedIdModels` rejects any surface/window/layer id that is not already a valid ilm/wal3d
surface on a valid layer — a plugin cannot invent an id. To show its **own** GPU/3D content on this
path, a plugin would have to, from inside the `HmiMain3D` process it is `dlopen`'d into:

1. create its **own** QNX Screen window and ilm surface (native `libscreen.so.1` /
   `libilmClient.gpp.so.1`, both mapped), render into it with `libEGL.so.1` / `libGLESv2.so.1`
   (mapped), and obtain a **valid layer id** the compositor recognises;
2. publish that native surface id into a `surfaceIdModel` bound to a `<surfaceComponent>` in its
   DescFile.

Step 1 is entirely **outside** the sanctioned RA runtime API (`docs/06` gives you
fill-model / flip-property / handle-action — nothing that creates surfaces). It is *technically*
reachable (the process shares one address space with all the graphics libraries mapped), but it
means writing raw native Screen/ilm/EGL code that **contends for the HMI's single compositor**,
coordinates render order and layer ownership with the host, and can destabilise the whole HMI.
Whether a plugin-created surface even gets a layer the `CWal3dNBTevo`/ilm manager treats as valid
— the crux of the feasibility gap — was **not** verified; `valueChangedIdModels` enforcing valid
window/layer ids is exactly the wall. **[ENGINEERING-INFERENCE, PLAUSIBLE — not observed working.]**

For custom pixels (including a self-rendered 3D frame), the **supported** route stays Route B (§3.2
/ `docs/15` §2.2). Route A is the *live-surface* alternative: same permission verdict
(uncertified-OK), much heavier, and only partially in reach.

---

## 3. Rendering your own 3D in-process

Both routes start the same way — **a plugin renders its own 3D with its own GL context, in the
`HmiMain3D` process.** They differ only in how the result reaches the screen.

### 3.1 The GPU is already in the plugin's address space — [CONFIRMED reach; STRONG in-process GL]

A plugin `.so` is `dlopen`'d **into** `HmiMain3D` (`docs/14` §1: `DynamicLibrary::load` = `dlopen`),
and that process is a full OpenGL ES 2.0 / EGL client. Its `NEEDED` list carries `libGLESv2.so.1`,
`libEGL.so.1`, `libscreen.so.1`, `libilmClient.gpp.so.1`, `libtilerusr.so.1`, `libOpenCTM.so`,
`libDevIL.so` (re-verified), and its dynsym imports the **entire** GLES2 draw API plus EGL
display/context/window-surface creation and the **complete FBO/readback path** —
`glGenFramebuffers`, `glBindFramebuffer`, `glFramebufferTexture2D`, `glCheckFramebufferStatus`,
`glGenRenderbuffers`, `glRenderbufferStorage`, **`glReadPixels`**. **[CONFIRMED — `readelf -d`,
`nm -D`]**

Those libraries are mapped once for the process. A plugin that links its own `libEGL.so.1` /
`libGLESv2.so.1` binds its imports to the **already-loaded** instances (ordinary ELF/RTLD reuse of
a `NEEDED` object), so it can call the full API — including entry points `HmiMain3D` itself never
uses. `libEGL.so.1` exports `eglCreatePbufferSurface`, `eglMakeCurrent`, `eglBindAPI`,
`eglQueryString`, `eglGetDisplay`, `eglInitialize`, `eglChooseConfig`, `eglCreateContext`;
`libGLESv2.so.1` exports the FBO calls. `HmiMain3D` itself imports **no** `eglCreatePbufferSurface`
(it uses *window* surfaces) — confirming a plugin needs its own EGL link for the **offscreen**
pbuffer/FBO path. **[CONFIRMED — `nm -D` on the libs]**

**Multiple EGL context-creation sites already exist in this one process** — the main WAL3D renderer
(`[WAL3D] NBTEvo wal3d initialized.`, `eglCreateContext failed. err=%x`), a separate
Spirit-of-Ecstasy roundel context (`[CCarSpiritOfEcstasyActivity::init] unable to create FBM
context`), and a navigation history context (`createHistoryContext`). **[CONFIRMED that multiple
context-creation sites exist; STRONG (inference) that they coexist at runtime — a static string
carve shows the sites, not simultaneous liveness.]** Either way, a plugin adding one more context
is an **existing pattern, not a novel demand on the driver.**

> **In-process GL reach — [STRONG].** A plugin *can* create its own `EGLContext` + pbuffer + FBO
> and drive GLES independently. The binding, the API surface and the multi-context precedent are
> all confirmed; what remains inference is only the runtime plumbing below (the end-to-end frame
> loop was not executed on-target).

### 3.2 The safe render-loop pattern — reconciled with docs/07

`docs/07` says **all model/UI work runs on the single dispatcher thread; never block it.** GL is
orthogonal to that rule: an `EGLContext` is **per-thread-current**, and the HMI's own renderer runs
on its own GL / "surface sync" thread (`[WAL3D] surface sync thread`, `eglCreateSyncKHR`). So a
plugin's GL work **must not** run on the dispatcher thread (wrong thread for a context, and it would
stall the HMI). The safe shape is the `docs/07` worker→UI hand-off, one level up:

- a **private GL worker thread** owns the plugin's `EGLContext` (+ a small pbuffer to satisfy
  `eglMakeCurrent`) and does all `gl*` calls and `glReadPixels`;
- it hands the finished RGBA buffer to the dispatcher thread via `post(Runnable*, ms)` — the same
  `ChildPoller` hand-off from `docs/07` §2, a **thread** here rather than a `posix_spawn`'d
  process, which is acceptable **only because the worker never touches the model**;
- the model push happens **on the dispatcher thread**, inside that `Runnable::run()`.

**[ENGINEERING-INFERENCE, STRONG]** — grounded in the per-thread-current EGL rule, the confirmed
separate HMI GL thread, and `docs/07`'s hand-off contract.

### 3.3 Route A vs Route B

**Route A — composite (best quality, unproven plumbing).** Render into the plugin's own ilm/wal3d
surface, hand its surface id to a `<surfaceComponent>`, and the HMI composites it **live** into a
layer — the only true real-time 3D-into-the-HMI-scene path, hardware-accelerated, **zero readback**.
Its permission bit is **open** (§2.3). Its obstacles are the §2.4 ones: **declarability**
(`<surfaceComponent>` recognised but never exercised by any shipped file — [STRONG/PLAUSIBLE]) and
**surface/layer ownership** (the plugin must create a real ilm surface the compositor assigns a
valid layer to — [PLAUSIBLE, unverified]). Treat Route A as *promising but unproven* for a plugin.

**Route B — offscreen → stream image (uncertified, works today).** Render 3D into a plugin-owned
**pbuffer/FBO** on the GL worker thread, `glReadPixels` to RGBA, `post` the buffer to the
dispatcher thread, and push it through a **`raImageModel` stream image**
(`CRemoteAppImageModel::loadImageStreamResource`, `docs/15` §2.2). This needs **no
`RHMI_PERM_LAYER`** — it rides the **`ImageDynamic` bit (idx 0), default-set** (`docs/14` §4.4),
so the `Images from streams are not allowed by certificate!` path cannot fire for an uncertified
plugin. **[STRONG — mechanism CONFIRMED (FBO+`glReadPixels` imported; the stream sink and its cert
gate confirmed in `docs/15`); end-to-end frame loop not run on-target. The exact permission index
of the stream gate is `docs/14`/`docs/15`'s STRONG mapping (`ImageDynamic` = idx 0); the stream
handler reads a cached flag rather than an inline `get(0)`, so idx-0 was not re-confirmed at the
xref — but idx 0, like every image bit, lies outside the denylist and is default-set, so the
"uncertified CAN" verdict holds regardless.]**

Cost, honestly: `glReadPixels` is a **synchronous pipeline stall** on the tiled PowerVR-class GPU,
and the bitmap re-enters as a **texture upload** — a readback + re-upload every frame. Output is
bounded by the `docs/15` stream **byte-size cap** (`Image data (%u Bytes) too large!` — numeric
value **[UNKNOWN]**, `docs/15` §6 #4), which caps resolution, and by dispatcher `post` latency,
which caps framerate. **[ENGINEERING-INFERENCE, PLAUSIBLE]** Good for a live custom dial / graph /
small 3D badge; not for a full-screen high-fps scene.

---

## 4. Capability table

| 3D route | How | Privilege / permission | Uncertified plugin CAN? | Quality | Grade |
|---|---|---|---|---|---|
| **Declarative 3D (push geometry at runtime)** | *(no RA 3D model; no `TAG_SCENE/MESH/MODEL3D`)* | n/a — no path | **❌ No** | — | CONFIRMED (none) |
| **`DynGFX3D`** | *(no DescFile tag; native scene traversal)* | n/a — not plugin-declarable | **❌ No** | — | CONFIRMED |
| **Reuse an OEM 3D widget by name** | `<widget widgetName="…">` at a native 3D template | none (no cert string on `<widget>`) | ⚠️ **Ungated but ~unusable** — the 3D templates need an `AssetId`/camera-layer a plugin can't cleanly provision | native | CONFIRMED (ungated) / PLAUSIBLE-thin (useful 3D) |
| **Bundle your own assets** | ship `<AssetDBFile>` (meshes/shaders/`scene.pbx`) + `<WidgetDBFile>` (`.pbw` of generic 3D types) + `<widget widgetName>` | params ungated | ⚠️ **Architecturally open, unproven** — blocked by authoring compiled Candera `.pbw`/`scene.pbx` (toolchain), not a permission | native (in-scene) | params CONFIRMED / ungated STRONG / end-to-end PLAUSIBLE |
| **Route A — composite your own live surface** | render own ilm/EGL surface → `<surfaceComponent surfaceIdModel>` | `RHMI_PERM_LAYER` = **bit 19, default-set** | ⚠️ **Permission yes; plumbing unproven** — needs native Screen/ilm/EGL surface + valid layer, outside the RA API | **Best** — live HW composite, no readback | gate CONFIRMED / reachability STRONG / full use PLAUSIBLE |
| **Route B — offscreen → stream image** | own EGL pbuffer/FBO → `glReadPixels` → `raImageModel` stream (`loadImageStreamResource`) | `ImageDynamic` = **bit 0, default-set** (no `RHMI_PERM_LAYER`) | **✅ Yes** — works today, fully in-API | Size-/fps-limited; per-frame readback+upload | STRONG (mechanism CONFIRMED; end-to-end not run) |

The only permission bit any of these routes touches, `RHMI_PERM_LAYER` (idx 19), is **granted by
default** — so **no route here is certificate-gated**. Route B additionally rides only the image
bits, which are also default-set (`docs/15` §2.3). Certificate buys nothing for 3D.

---

## 5. Recommendation

**(a) For an uncertified plugin (`data/ro/Plugins/`): take Route B.** It is the only route whose
every link is confirmed default-open and fully in the RA API. Render your 3D offscreen on a private
GL worker thread, read it back, and push frames as `raImageModel` stream images — the `docs/15`
§2.2 escape hatch, driven by the `docs/07` worker→dispatcher hand-off. Design around the size cap
(pick a modest resolution) and the readback cost (target a live gauge / graph / small rotating
badge, not a full-screen high-fps scene). This is the concrete answer to "can we render our own
3D?": **yes — offscreen, as a bitmap, uncertified.**

**(b) For a certified plugin: the same Route B, plus Route A as an *upgrade path you must
validate*.** A certificate does **not** unlock any additional 3D capability — `RHMI_PERM_LAYER` is
already default-granted, so Route A's *permission* gate is open to an uncertified plugin too. What a
certified/OEM-aligned effort buys is the standing to do the **unsupported native plumbing** Route A
needs (creating an ilm/Screen/EGL surface the compositor assigns a valid layer to, and declaring a
`<surfaceComponent>` bound to it) with OEM knowledge of the surface/layer namespace. If — and only
if — surface/layer ownership and `<surfaceComponent>` declarability are settled on-target (§6),
Route A becomes the true real-time option (live, hardware-composited, zero readback). Until then,
do not treat it as available.

**Do not** count on: a declarative mesh/scene model (none exists), the native sport dials or
`DynGFX3D` (native-only, `docs/15` §5), or dropping loose `.ctm`/`.pbw` files into an `AssetDBFile`
(present-but-unexercised, and toolchain-blocked).

---

## 6. Open questions / how to settle them

| # | Open question | Grade | How to settle it |
|---|---|---|---|
| 1 | Does the RA-integrate / plugin-DescFile parse path actually **dispatch to the surfaceComponent factory** for a plugin-owned `<components>` block? | [STRONG that it can be declared; not byte-traced] | Trace `CHmiIntegrator`'s per-tag component dispatch into the row at fileoff `0x2d5b0`; or drop a test `<surfaceComponent>` into an `OPT_DEBUG` plugin DescFile and watch for the init log. |
| 2 | Is **`surfaceIdModel`** a plugin-settable `ra*` model type, or a native-only idModel? | [PLAUSIBLE] | Trace its model-registration/factory; compare to `imageIdModel`/`textIdModel` (which *are* plugin-declarable). |
| 3 | Can an in-process plugin obtain a **valid ilm/wal3d layer id** that `CAbstractSurfaceComponent` accepts (it rejects invalid window/layer ids), and how is render order arbitrated against the host compositor? **This — not the permission — is Route A's true feasibility crux.** | [UNKNOWN / engineering estimate] | On-target: create a Screen window + ilm surface from a plugin, feed its id, and observe `valueChangedIdModels` accept vs `window ID … not valid`. |
| 4 | The **stream-image byte-size cap** value (`Image data (%u Bytes) too large!` @`0x2e1e83c`), which sets Route B's max resolution. | [UNKNOWN] (`docs/15` §6 #4) | Resolve the compare immediate near the size-cap string load, or push increasing bitmaps on-target. |
| 5 | Exact permission index the **stream-image gate** reads (mapped to `ImageDynamic`/idx 0 in `docs/14`/`docs/15`, but the handler reads a cached flag, not an inline `get(0)`). Not load-bearing — idx 0 is default-set regardless. | [STRONG] | Trace where the model's dynamic/stream flag is populated from the bitset. |
| 6 | Does a delayed dispatcher `post()` tick fast enough for a **smooth Route B frame loop**? | [UNKNOWN] (`docs/07` marks delayed-post scheduling uncharacterized) | On-target: measure the achieved refresh of a growth-gated stream-image push. |
| 7 | Is `EGL_KHR_surfaceless_context` supported (would let the GL worker skip the throwaway pbuffer), and can a plugin context **share a sharegroup** with the HMI renderer? Ergonomics, not feasibility. | [UNKNOWN] | On-target `eglQueryString(EGL_EXTENSIONS)`; not determinable from a static carve. |
| 8 | The precise native **consumer set** of `VideoSurfaceId` / the surface-compositing path (rear-view camera vs media vs RSE vs companion process). | [PLAUSIBLE] (video source is STRONG) | Locate the code-side `surfaceComponent` instantiation(s); no OEM DescFile declares one. |
| 9 | Can a plugin-supplied **`AssetDBFile`/`WidgetDBFile`** be authored and loaded end-to-end (Candera `.pbw`/`scene.pbx` serialization; any asset-bundle validation)? Note a *separate* signature-associated ego-model **network-upload** path exists (`BMW.INFOTAINMENT.EgoModelUpload`), distinct from the plugin AssetDB path. | [PLAUSIBLE; authoring SOLVED offline 2026-10-05] | Authoring is no longer the wall. `scene.pbx`/`widget.pbw` round-trip byte-for-byte through `protoc` with the recovered descriptors, and `.rsvi` meshes are readable and writable. See the RSVI tooling in [`../../vehicle_models/`](../../vehicle_models/). Still open: author a minimal bundle, test on-target. |

---

## 7. Sources & method

- **Owner-authorized, offline-carve reverse engineering** of the author's own titled NBT-Evo head
  unit (100 % vanilla OEM firmware, `OPT_DEBUG` for system access only). No hardware was touched;
  this is a static read of a flash carve.
- **Binaries / files** (under
  `opt/hmi/ID5/`):
  `bin/HmiMain3D` (ARM32, `.symtab` stripped; dynsym + RTTI class-name strings; `NEEDED`
  `libGLESv2.so.1`, `libEGL.so.1`, `libscreen.so.1`, `libilmClient.gpp.so.1`, `libtilerusr.so.1`,
  `libOpenCTM.so`, `libdce.so.1`, `libDevIL.so`); `lib/libEGL.so.1` / `lib/libGLESv2.so.1`
  (exported pbuffer/FBO API); `lib/libAppFramework.A.so` (`WidgetDBFile`/`AssetDBFile` params);
  `data/ro/PluginsCoded/{SecurityMenu,ActiveSeating}/*` (the only two App-plugins — both
  certificated, neither declares a surface/widget/asset DB); `data/ro/common/**` (the Candera/INES
  3D asset bundles).
- **Cross-referenced RE:** prior reverse-engineering of the native sport dials (`docs/15` §5) and
  the application map / service graph of the HMI apps.
- **Method.** Structural facts (RTTI class names, `TAG_*` and `ra*Model` symbols, `NEEDED` lists,
  ilm/EGL/GLES import sets, on-disk zips, string offsets, manifest contents) were verified directly
  with `strings -a -t x`, `nm -D`, `readelf -d`, `grep` and `unzip`, and **re-verified against the
  carve while writing this document** — including independent confirmation of: the sole
  `RHMI_PERM_LAYER` token; the `surfaceComponent`/`surfaceIdModel`/`layerIdModel`/`VideoSurfaceId`
  strings; the ten `ra*Model` tags (none 3D); the native 3D `eWidgetType_{Asset,Model,Scene,
  SceneBase,Layer,Transform}` base set (no `Frame3D`/`Group` enum); the five ilm imports and the
  graphics `NEEDED` set; and that no manifest/DescFile in `data/ro` declares
  `surfaceComponent`/`WidgetDBFile`/`AssetDBFile`. Control-flow claims (`CAbstractSurfaceComponent::init`
  bit-19 gate, the permission getter `0x2512878` and constructor `0x2512958` denylist) come from the
  lead's targeted ARM/capstone passes (host `objdump` cannot disassemble this ARM EABI5 binary) and
  match `docs/14` §4 byte-for-byte at the cited addresses.
- **All three research angles** (surface component, in-process GL feasibility, native-3D/assets)
  were **adversarially verified**; where a verifier refuted or downgraded a claim, **the corrected
  grade is used here** — notably: the surface-component end-to-end permission verdict is **STRONG**
  (two CONFIRMED sub-facts + one STRONG "receives permissive default" premise from `docs/14` §4.3),
  not CONFIRMED; the `ilm_layerAddSurface` compositing verb rests on imports+validation strings, not
  a traced call; "multiple EGL contexts" is CONFIRMED as context-creation *sites* and STRONG as
  runtime coexistence; the asset/widget-DB load being **ungated** is STRONG (a no-gate-string
  structural inference), while the params + per-app DB slots are CONFIRMED; and the native 3D base
  widget-type list was corrected (`Frame3D` is a `.pbw` prototype name, not a native enum).
- **Confidence is graded on every material claim** per the legend at the top. Engineering
  feasibility is labelled **[ENGINEERING-INFERENCE]** and kept distinct from what was read from the
  binary. An explicit **[UNKNOWN]** with a way to settle it (§6) is preferred over invented
  certainty.
