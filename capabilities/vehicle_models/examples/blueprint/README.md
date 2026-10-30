# Blueprint — a custom car that uses every feature

A tiny, deliberately plain car — a few boxes and cylinders generated in code — that wires up **every**
custom-car capability, so "how do I add X?" has a worked, runnable answer in one file:
[`build_blueprint.py`](build_blueprint.py). The geometry is original (no third-party mesh), so the builder
is yours to publish; what it produces is *your* `.nbtcar`, built from *your* stock template.

This is the reference you copy from. The steam-loco / Warthog models are the same method at full scale.

## What it demonstrates

| # | Feature | How, in the builder | HMI signal |
|---|---|---|---|
| 1 | Replace the stock car | `car.blank_stock_meshes(keep=…)` | — |
| 2 | Your own material | `car.add_material("BP_PAINT", like=…)` | — |
| 3 | Custom geometry | `car.add_mesh(…, mesh.box/cylinder(...))` | — |
| 4 | **Wheels that spin** | `car.bind(pivot, rotate=vec3(0, spin, 0))` | `WheelsRotationValue` → `GlobalWheelsRotation_MDL.output` |
| 5 | **Roll-in on open** | `car.bind(root, translate=…)` eased by `car.add_curve(...)` | `FESStaging` |
| 6 | **Continuous idle anim** (Sin/Cos) | `phase = car.add_clock(...)`; `sin(phase·2π)` | free-running clock |
| 7 | **A door that opens** | `car.bind(hinge, rotate=vec3(0,0, door·-65))` | `DoorL1Open` |
| 8 | **Lamps that switch** | `car.bind(lamp, visible=…)` | `LightOn` |

Every binding is a Python expression over the HMI's own signals (`tools/widget_expr.py`): parameters the HMI
sets each frame, named internal refs it computes (the wheel-roll angle), constants, arithmetic, `sin`/`cos`,
`clamp`, `mix`, comparisons, and Hermite `curve`s.

## The authoring layer (what makes this possible)

`package.py` wraps an already-authored chassis folder; these tools **author** that folder — they write the
`scene.pbx` node graph and the `widget.pbw` animation/binding graph that the readers (`rsvi_scene.py`,
`pbw.py`) only read:

| Tool | Role |
|---|---|
| [`tools/mesh.py`](../../tools/mesh.py) | geometry: `Mesh`, `box()`, `cylinder()`, normals/tangents, `tiny()`, `fill_layout`, `write_slot` |
| [`tools/scene_template.py`](../../tools/scene_template.py) | reads a stock `vehicle/` as a template: node paths, matrices, materials, per-node vertex layouts |
| [`tools/widget_expr.py`](../../tools/widget_expr.py) | the expression DSL for bindings/curves (`E.P`, `E.R`, `E.C`, `E.sin`, `E.vec3`, `E.clamp`, …) |
| [`tools/author.py`](../../tools/author.py) | `Car`: copy a template and **add** nodes, meshes, materials, bindings, curves, clocks; `save()` |

The protobuf schema they build against (`packager/hmi_descriptors.bin`, our recovered descriptor set) and its
loader (`packager/hmi.py: proto()`) already ship with the toolkit.

## Build it

You supply the stock template (the `vehicle/` folder the builder mutates) from your **own** extracted HMI
tree — same configuration the packager uses ([`../../02-packaging.md`](../../02-packaging.md),
[`../../packager/hmi.py`](../../packager/hmi.py)). Then:

```bash
# 1. author the series folder (default template: F30 under your HMI tree)
python -m capabilities.vehicle_models.examples.blueprint.build_blueprint --out /tmp/BLUEPRINT --verify
#    --verify re-reads the widget and checks each feature responds to its signal (offline proof)

# 2. wrap it into an installable .nbtcar (ungated, your own namespace)
python -m capabilities.vehicle_models.packager.package \
    --id BLUEPRINT --name "Blueprint car" --folder /tmp/BLUEPRINT --template F30 --out blueprint.nbtcar
```

Install `blueprint.nbtcar` the way any custom car installs — the LMPC-safe file steps in
[`../../02-packaging.md`](../../02-packaging.md) and the shared SSH staging in
[`docs/staging-files-over-ssh.md`](../../../../docs/staging-files-over-ssh.md). **Your own car only.**

## Extending it (features documented, left for you to add)

- **Bitmaps / textures** — `car.add_bitmap(name, image)` then point a material's sampler at it; recolour by
  overriding a mesh uniform (`add_mesh(..., uniforms={...})`).
- **PDC collision coats** — the additive `M_CAR_MCPS_…` material + twin nodes shown during parking; add coat
  meshes bound visible to the PDC state.
- **Camera presets** — the `camera_crane/` widget holds the drive-mode/Car-Check camera moves; the same
  `Car`/`widget_expr` approach edits it.
- **My Vehicle hero image** — a separate still-image route (a GID bundle in the `.nbtcar`), not this 3D path.

## Honest status

The authoring layer and this blueprint are **proven offline**: the builder writes `scene.pbx` + `widget.pbw`
that re-read through the toolkit's own readers, the meshes pass `validate/check_rsvi.py`, the folder packages
into a valid `.nbtcar`, and `--verify` confirms every feature responds to its signal. The **on-car** look of a
newly-authored model is the one thing only your own unit can confirm — treat the first install as a careful,
reversible step (the package uninstalls cleanly; see [`../../02-packaging.md`](../../02-packaging.md)).
