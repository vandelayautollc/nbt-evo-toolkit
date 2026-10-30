# The HMI resource pipeline — how the head unit decides what to show

This is the doc that lets you answer "**how do I change X?**" for most *visible* things — an image,
the car model, a string, a sound — because almost all of it is **data-driven and coding-gated**,
not hard-coded. Understand this pipeline and the investigation method in
[investigation-playbook.md](investigation-playbook.md) becomes concrete.

## The core idea: GID → bundle → variant gate → coding

The HMI refers to a resource by a **GID** (a graphic/resource id, e.g.
`START_MAIN_SELECTION_MYVEHICLE`, or a numeric id). A GID does **not** map to one file — it maps to
**several candidate bundles, each gated by a `variantFlag`**, and the HMI picks the bundle whose
flag is active for *this* car.

```
GID ──▶ assetDB/resources.ptr        (plaintext map; resources.pbr is the binary twin)
          ├─ bundle A  variantFlag 1360|1365|1377   ← chosen if the car's variant matches
          ├─ bundle B  variantFlag 1361
          └─ …
                    │
     variantFlag ids ARE libhmicoding "va" ids ──▶ coding value
          e.g. 1360 = F30 (BAUREIHE value 64)
                    │
     BAUREIHE = SYSTEM_EINSTELLUNGEN.BAUREIHE = coding datagroup 0x3004, byte 4
```

So "which car picture / which layout / which regional asset" is ultimately a **coding** decision
(`capabilities/coding/`). Change the coding and a different already-present bundle is selected;
change the *bundle* (add your own) and you introduce a new choice. Both are valid levers — pick the
one that fits the task.

## Asset kinds and where they live

Under `/opt/hmi/ID5/data/ro` (and the `common/`, `bmw/` trees):

| Kind | Where / format | How it's chosen |
|---|---|---|
| **Loose PNG** (tiles, heroes, backdrops) | `assetDB/Domains/…/*.png` | GID → variant-gated bundle |
| **3D vehicle model** (the rotatable car) | `…/3d_car/…/*.pbw` (widget graph) rendering `vehicles/<SERIES>/*.rsvi` meshes via a `.pbx` scene; textures PNG; shaders `.shd` | series via `bmw/widget/variantregistry.pbvar` (series→assetid) |
| **UI text** | `bmw/db/text.db` — NRV2D-compressed UTF-16 (`libhmizip`) | by string id; one DB |
| **Audio / EQ** | `/data/mm/eqdata/<series>_<AUDIO_SYSTEM>_VARIANT<n>.bin` | `EQ_VARIANT` coding → `AudioProcess` |

Formats that look opaque are decodable (see [toolchain.md](toolchain.md)): `.pbw`/`.pbx`/`.pbvar`
are **protobuf** (round-trip byte-identical with `protoc --decode/--encode`); `.rsvi` is a documented
mesh container (header + Snappy-compressed interleaved verts/indices); `text.db` is NRV2D.

## The two ways to change a visible asset

1. **Rename-over a loose file.** The PNGs are hard-links to LMPC-manifested repository files
   ([architecture.md](architecture.md) §Integrity). **Never write a stock file in place** — it
   changes the hash and raises a DTC. Instead put your new file alongside and **rename it over** the
   live link (breaking the hard-link), or:
2. **Register your own bundle (last-wins).** `libhmidb readResourceBundle` registers bundles by
   numeric id and **the last registration wins** (`setDynamicStreamResourceData` frees the prior).
   `assetDB` is scanned before `widgetasset`, so an **ungated** bundle carrying a GID beats BMW's
   gated ones for every series — a clean override with no stock edit and no coding change. This is
   how a custom hero image or a whole custom car is installed (`capabilities/vehicle_models/`).

Either way the HMI **caches resources at startup**, so your change shows only after an `appreset`
or a reboot.

## Worked example: "how do I change the car picture?"

This is the exact path that was reverse-engineered — it's the template for any visible asset:

1. **Identify the artifact on the running HMI** — screenshot the screen (via `LayerManagerControl`,
   see [toolchain.md](toolchain.md)) so you know precisely what you're changing.
2. **Find its GID** — the *My Vehicle* tile is `START_MAIN_PADS_MYV_SIMPLEBC_GRAPHIC` (id6 style) /
   `START_MAIN_SELECTION_MYVEHICLE` (ID5 list hero); the drive-mode popup car is a **live 3D render**
   (`3d_car/preview_car_fes/3dcar_fes.pbw`), not a PNG — so the two need different approaches.
3. **Find where it's referenced** — grep `assetDB/resources.ptr` for the GID → the per-model
   bundles and their `variantFlag`s.
4. **Find the gate** — the F30 bundle's flag `1360` = `libhmicoding` va id for BAUREIHE value 64 =
   F30; BAUREIHE is coding `0x3004`/byte 4. So the *selection* is coding-driven.
5. **Choose the lever** — to swap the PNG: rename a new file over the F30 hero link. To change the
   3D car: add a new series folder + `variantregistry.pbvar` entry (last-wins), no stock edit.
6. **Respect integrity** — add/rename, never overwrite stock (LMPC).
7. **Apply + reset + verify** — install over SSH, `appreset`, confirm with another screenshot.

That chain — *screenshot → GID → reference table → coding/variant gate → safe edit point → reset →
verify* — is the general method. The next one ("what does coding value Y do?") trades the resource
tables for a firmware trace; see the playbook.

## What this does and doesn't cover

- **Covers** anything the HMI selects from data: images, 3D models, text, regional/variant assets,
  feature visibility, audio variants.
- **Doesn't cover** behavior with no data knob — that lives in `HmiMain3D`/app logic and needs a
  firmware trace (playbook) or, to change it, a plugin (`capabilities/plugins/`) or a patch
  (`capabilities/flash_and_patching/`).
