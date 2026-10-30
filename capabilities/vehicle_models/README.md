# Custom 3D vehicle models

Generate a custom 3D vehicle model and install it as your car's iDrive **hero image** — the
rotatable 3D car on the *My Vehicle* / vehicle-status screens — on your own head unit. It's a
**file install** of art assets (over SSH), not a coded write or a flash, and it's fully reversible,
which makes it the lowest-risk capability here.

> Respect the HU's file integrity: a custom car is added as its **own** model + an unconditional
> registry override — no stock file is overwritten (LMPC, see
> [architecture.md](../../docs/architecture.md)). Reverting = remove what you added + reset the HMI.

## Read this section in order

1. **[01-concepts.md](01-concepts.md)** — the model's anatomy (`variantregistry` → `scene.pbx` →
   `widget.pbw` → `.rsvi` meshes), the coordinate system, and the install mechanism (a chassis
   folder packaged as a `.nbtcar`, selected by a last-wins registry entry).
2. **[02-packaging.md](02-packaging.md)** — build a `.nbtcar` from a chassis folder (point the
   packager at your own extracted HMI tree; prove the setup with `--selftest`) and install it.
3. **[examples/blueprint/](examples/blueprint/)** — a tiny **original** car that wires up *every*
   feature (custom geometry, materials, spinning wheels, roll-in, a Sin/Cos idle animation, a door,
   switchable lamps) in one commented, runnable file. The reference you copy from.
4. **[formats/](../../formats/README.md)** — the byte-level specs for RSVI, protobuf (`.pbw/.pbx/
   .pbvar`), and which open-source codecs to install.

## Tools

| Script | Does | Touches car | Status |
|---|---|---|---|
| `tools/rsvi.py` | read/write RSVI meshes, export OBJ, build from JSON (pure-Python Snappy, no deps) | no (offline) | ✅ |
| `tools/rsvi_scene.py` | parse/export the `scene.pbx` node tree (whole-car OBJ / JSON) | no (offline) | ✅ |
| `tools/pbw.py` | decode + **evaluate** the `widget.pbw` animation graph (params, expressions, curves, bindings) | no (offline) | ✅ |
| `tools/mesh.py` | geometry kit: `Mesh`, `box()`/`cylinder()` primitives, normals/tangents, RSVI layout fill | no (offline) | ✅ |
| `tools/scene_template.py` | read a stock `vehicle/` as an authoring template (node paths, matrices, layouts) | no (offline) | ✅ |
| `tools/widget_expr.py` | the expression DSL for bindings/curves (`E.P/R/C`, `sin`, `vec3`, `clamp`, …) | no (offline) | ✅ |
| `tools/author.py` | **author** `scene.pbx`+`widget.pbw`: add nodes/meshes/materials/bindings/curves/clocks | no (offline) | ✅ |
| `validate/check_rsvi.py` | validate a mesh against the HU reader's invariants + round-trip it | no (offline) | ✅ |
| `examples/blueprint/` | an original all-features car (builds + self-verifies each feature) | no (offline) | ✅ |
| `packager/package.py` | build an installable `.nbtcar` from a chassis folder (reads your own HMI tree) | no (offline) | ✅ (selftest-proven) |
| install | copy the package onto the HU and register it | file install (SSH) | runbook ([02](02-packaging.md) + [staging](../../docs/staging-files-over-ssh.md)) |

## The happy path (authoring core, available now)

```bash
pip install -e .      # from the repo root

# Inspect a stock mesh you've pulled from your own extracted HMI tree.
python capabilities/vehicle_models/tools/rsvi.py info  vehicle/meshes/body.rsvi
python capabilities/vehicle_models/tools/rsvi.py obj   vehicle/meshes/body.rsvi body.obj   # edit in a 3D tool

# Build your edited mesh back to RSVI and validate it before it ever goes near the car.
python capabilities/vehicle_models/tools/rsvi.py build body.json body.rsvi
python -m capabilities.vehicle_models.validate.check_rsvi body.rsvi
```

Everything above is offline and needs no car and no deps. Preview a whole model off-car before
installing — a model can be rendered in a viewer from its scene + meshes.

## Status

**Authoring + packaging are here and exercised — including authoring the scene/animation graph from
code, not just editing meshes.** Reading (`rsvi.py`, `rsvi_scene.py`, `pbw.py`), the **authoring**
layer (`mesh.py`, `scene_template.py`, `widget_expr.py`, `author.py`), the mesh validator, and the
`.nbtcar` **packager** (with the shipped HMI protobuf schema set) are all in. The
[blueprint example](examples/blueprint/) builds an original all-features car and `--verify` confirms
every feature responds to its HMI signal; the packager's `--selftest` rebuilds every stock series'
index bundles **byte-identically** from your own extracted HMI tree.

The one thing only your own unit can confirm is the **on-car look** of a freshly-authored model —
treat a first install as a careful, reversible step. Install is a documented runbook
([02-packaging.md](02-packaging.md) + [staging-files-over-ssh.md](../../docs/staging-files-over-ssh.md)),
not a turnkey script, by design. Still optional: the **`--hero`** 2D-picture override (needs a
headless renderer) and a **WebGL previewer**.
