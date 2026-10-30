# 01 · How the 3D vehicle model works, and how a custom one installs

The rotatable car on the *My Vehicle* / drive-mode screens is a **live 3D render**, not a picture.
This doc is the model's anatomy and the install mechanism — enough to author and fit your own.
Formats are specified in [formats/](../../formats/README.md); the authoring core (`rsvi.py`) ships
in `tools/`.

## The resource chain

The HMI assembles the car from four layers, each selected by the vehicle's series (see
[resource-pipeline.md](../../docs/resource-pipeline.md) for how series → coding works):

```
variantregistry.pbvar   series condition → vehicle_assetid / camera_crane_assetid   (which model)
      │
scene.pbx               node tree: names, transforms (scale/rot°/trans cm), child nodes, mesh refs
      │
widget.pbw              animation graph: wheels turn, car rolls in, light cones, drive-mode tint
      │
*.rsvi + textures + shaders    the meshes (RSVI), PNG textures, PowerVR .shd shaders
```

- **`variantregistry.pbvar`** (protobuf) maps a series condition to the model asset ids. Entry 0 is
  the default. Adding an **unconditional** entry here is how a custom model is selected for any car
  (it loads last; last wins).
- **`scene.pbx`** (protobuf) is an exported node tree: each node has a name, a transform (scale,
  rotation in degrees, translation in cm), children, and optionally a mesh path. Doors, wheels, and
  trunk are child nodes **local to their pivots**; rim meshes are shared across the four wheels.
- **`widget.pbw`** (protobuf) is an exported Maya dependency graph that animates the scene:
  `FESStaging` rolls the car in (body slides, wheels spin the matching distance), `WheelsRotationValue`
  turns the rims, light-cone and ground nodes fade with drive mode, and shader uniforms tint
  Eco/Comfort/Sport (same mesh, different uniforms — not per-mode models).
- **`*.rsvi`** are the meshes. Units are **cm, z up, x toward the rear**. Format + codec:
  [formats/](../../formats/README.md) and `tools/rsvi.py`.

## The RSVI mesh format (the authoring core)

`tools/rsvi.py` reads and writes RSVI with a pure-Python Snappy codec (no external dependency),
exports OBJ, and builds an RSVI from a JSON mesh description:

```bash
python capabilities/vehicle_models/tools/rsvi.py info  car.rsvi          # elements, vert/tri counts
python capabilities/vehicle_models/tools/rsvi.py obj   car.rsvi car.obj  # positions, normals, UV0, faces
python capabilities/vehicle_models/tools/rsvi.py build mesh.json out.rsvi
```

Validate any mesh before you build it into a bundle:

```bash
python -m capabilities.vehicle_models.validate.check_rsvi car.rsvi
```

The validator enforces the HU reader's invariants (positions present, indices in range, ≤ 65536
vertices, stride matches the element layout) and round-trips the mesh to prove it survives the codec
content-identically. A mesh that fails this will not render — fix it before packaging.

## The install model: a custom car is its own series folder, chosen by a registry override

You do **not** edit BMW's models. You add yours as a new model and point an unconditional registry
entry at it, so it wins for every series — no stock file is modified (respecting LMPC integrity,
see [architecture.md](../../docs/architecture.md)).

A **chassis folder** is a built series folder — `vehicle/` + `camera_crane/`, each with its
`scene.pbx` + `widget.pbw` + meshes — made on a stock series as a **template** (e.g. F30, so it
inherits working pivots and animation wiring). It's packaged as a `.nbtcar` (a zip) carrying:

| In the package | What it is |
|---|---|
| `car.json` | metadata: id, name, version, root, template, file list |
| `files/…` | the model folder as the HU gets it (`vehicle/`, `camera_crane/`, `vehicle_<ID>/`) |
| `bundles.pb` | the resource index bundles (`HmiResource.TResourceDefinition`), **ungated**, listing every file under the root |
| `registry.pb` | one **unconditional** registry entry (`variantregistry`) pointing the asset ids at your model |

On the head unit it installs under **`vae/vehicles/<ID>`** beneath `/opt/hmi/data/ro`; the installer
appends `bundles.pb` to every root-7 index (`<brand>/<line>/widgetasset/resources.pbr`) and writes
`registry.pb` as `<brand>/<line>/widget/variantregistry.pbvar`, **which loads last** — so any brand,
line, or series then shows your model. Files are added, never overwritten; reverting is removing the
folder and the appended entries and resetting the HMI.

Optionally, `--hero` also replaces the 2D *My Vehicle* picture (the `widgetasset` index is scanned
after `assetDB`, and the last registration of a GID wins — see
[resource-pipeline.md](../../docs/resource-pipeline.md)).

## Proven

This mechanism has rendered several fully custom chassis on-car as their own vehicles (a drivable
truck; an animated steam locomotive with rod motion and clock-driven steam; a faithfully-modeled
other-make car on BMW's own F30 pivots) — evidence the path is sound end to end.

## What ships now vs. next

- **Now (exercised):** the read/inspect tools — `tools/rsvi.py` (mesh read/write/OBJ/build,
  pure-Python Snappy), `tools/rsvi_scene.py` (scene-tree parse/export), `tools/pbw.py` (animation
  graph decode + evaluate) — the full **authoring** layer that writes a model from code
  (`tools/mesh.py` geometry + primitives, `tools/scene_template.py`, `tools/widget_expr.py` the
  binding DSL, `tools/author.py` the `Car` builder), a runnable all-features **blueprint**
  (`examples/blueprint/`), the mesh validator `validate/check_rsvi.py`, and the **`.nbtcar` packager**
  (`packager/`, with the shipped HMI protobuf schema set `hmi_descriptors.bin`). The packager reads
  your own extracted HMI tree and its `--selftest` rebuilds every stock series' index bundles
  byte-identically — see [02-packaging.md](02-packaging.md).
- **Next:** a scripted installer/uninstaller over SSH (steps documented in 02-packaging.md); the
  `--hero` 2D-picture override (needs a headless renderer); an optional WebGL previewer.
