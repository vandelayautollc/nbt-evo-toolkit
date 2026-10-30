#!/usr/bin/env python3
r"""
BLUEPRINT — a tiny ORIGINAL car that exercises every custom-car feature, as a reference you copy from.

Nothing here is a third-party model: the geometry is a few boxes and cylinders generated in code, so the
whole thing is yours to publish. It is deliberately ugly and deliberately complete — each section below
demonstrates one capability, heavily commented, so "how do I add X?" has a worked answer in one file.

What it shows, in order:
  1. blank the stock car            Car.blank_stock_meshes()         -> only your car draws
  2. your own material              Car.add_material()
  3. custom geometry                Car.add_mesh() + mesh.box/cylinder()
  4. wheels that spin               Car.bind(rotate=...) from BMW's own wheel signal
  5. roll-in on open                Car.bind(translate=...) from FESStaging, eased by a curve
  6. a continuous idle animation    Car.add_clock() + sin(phase)      (the "Sin/Cos" lever)
  7. a door that opens              Car.bind(rotate=...) from DoorL1Open
  8. lamps that switch with lights  Car.bind(visible=...) from LightOn

Build (needs your own extracted HMI tree configured for the packager — see ../../02-packaging.md and
../../packager/hmi.py; the stock F30 'vehicle/' is the template this mutates):

    python -m capabilities.vehicle_models.examples.blueprint.build_blueprint --out /tmp/BLUEPRINT
    python -m capabilities.vehicle_models.packager.package --id BLUEPRINT --name "Blueprint car" \
        --folder /tmp/BLUEPRINT --template F30 --out blueprint.nbtcar

Then install blueprint.nbtcar the same way as any custom car (../../02-packaging.md, and the shared SSH
staging in docs/staging-files-over-ssh.md). Owner's own car only.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from capabilities.vehicle_models.packager import hmi                     # noqa: E402
from capabilities.vehicle_models.tools import author, mesh               # noqa: E402
from capabilities.vehicle_models.tools import widget_expr as E           # noqa: E402

TWO_PI = 2 * math.pi

# BMW's own HMI signals (externalModelValue params / internalModelValue refs the stock widget exposes).
# Discover them on your tree by reading the stock widget.pbw with tools/pbw.py; these are F30's.
WHEEL_SPIN = "GlobalWheelsRotation_MDL.output"   # ref: global wheel roll angle (radians), BMW's own
STAGING = "FESStaging"                            # param: 0 parked -> 1 the drive-mode popup is open
DOOR = "DoorL1Open"                               # param: front-left door, 0 shut -> 1 open
LIGHTS = "LightOn"                                # param (bool-ish): headlights on


def build(template_dir, out_dir):
    # A Car copies the stock 'vehicle/' and lets you add to it. Every stock node/material/binding is kept,
    # so the HMI still finds everything it sets; your content hangs beside it.
    car = author.Car(template_dir, out_dir)

    # The body slot is a good carve-agnostic 'like' template: its material, uniforms and vertex layout are
    # what add_mesh copies. We also attach our nodes in the same render-layer container it lives in.
    body = car.tmpl.biggest_slot()
    bay = body["node"].rsplit("|", 1)[0]          # the render-layer child container holding the body mesh

    # (1) Hide the stock car — replace every stock mesh with a 1 mm placeholder, keeping its ground shadow
    #     so we still cast one. Nodes, materials and all the widget's bindings stay valid.
    car.blank_stock_meshes(keep=("GRD", "GROUND", "DSC", "SHADOW"))

    # Our own root pivot: bind THIS for the whole-car roll-in (never bind a stock node's transform — BMW may
    # already bind it). Everything else parents under here.
    root = car.add_node(bay, "BP_ROOT")

    # (2) Your own material — a renamed copy of the stock car-paint material.
    car.add_material("BP_PAINT", body["material"])
    glass = next((m for m in car.tmpl.materials if "GL" in m), body["material"])   # a glassy one for lamps

    # (3) Custom geometry — a body + a cabin, boxes in the CAD frame (cm; x=rear, y=right, z=up).
    car.add_mesh(root, "BP_BODY", mesh.box((430, 185, 90), center=(0, 0, 55)), like=body["file"], material="BP_PAINT")
    car.add_mesh(root, "BP_CABIN", mesh.box((210, 165, 70), center=(-20, 0, 120)), like=body["file"], material="BP_PAINT")

    # (4) Wheels that spin. A cylinder along the axle (Y), one pivot node per wheel. Binding the pivot's
    #     rotation about Y to BMW's own wheel-roll ref makes them turn exactly with the HMI's wheel signal.
    spin_deg = E.R(WHEEL_SPIN) * E.C(180.0 / math.pi)        # ref is radians; node rotations are degrees
    for name, (x, y) in {"LF": (150, -95), "RF": (150, 95), "LR": (-150, -95), "RR": (-150, 95)}.items():
        pivot = car.add_node(root, f"BP_WHEEL_{name}", T=(x, y, 34))
        car.add_mesh(pivot, f"BP_TYRE_{name}", mesh.cylinder(34, 26, axis="y"), like=body["file"])
        car.bind(pivot, rotate=E.vec3(0, spin_deg, 0))       # <-- wheel spin

    # (5) Roll-in: as the drive-mode popup opens (FESStaging 0->1) slide the car in from behind. An eased
    #     curve (Hermite) sampled by the staging value drives the slide, instead of a linear ramp.
    stage = E.clamp(E.P(STAGING), 0.0, 1.0)
    ease = car.add_curve("BP_ROLLIN", sample=stage,
                         points=[(0.0, 1.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0)])   # 1->0 with flat tangents (ease)
    car.bind(root, translate=E.vec3(ease * E.C(260.0), 0, 0))                   # 260 cm back when parked

    # (6) A continuous idle animation — the "Sin/Cos" lever. A free-running clock gives a 0->1 phase; sin of
    #     it drives a beacon that spins and bobs forever while the popup is up. This is how the steam-loco
    #     chuff / rotating-light effects are built.
    phase = car.add_clock("BP_IDLE", duration_ms=1600)       # loops every 1.6 s
    ang = phase * E.C(360.0)                                  # 0 -> 360 deg per loop
    bob = E.sin(phase * E.C(TWO_PI)) * E.C(4.0)              # +/- 4 cm vertical bob
    beacon = car.add_node(root, "BP_BEACON", T=(-20, 0, 165))
    car.add_mesh(beacon, "BP_BEACON_MESH", mesh.box((24, 24, 16), center=(0, 0, 8)), like=body["file"], material=glass)
    car.bind(beacon, rotate=E.vec3(0, 0, ang), translate=E.vec3(-20, 0, E.C(165.0) + bob))

    # (7) A door that opens. A thin flap on a vertical hinge (pivot at its front edge), its Z-rotation bound
    #     to the HMI's door signal: shut at 0, ~65 deg open at 1.
    hinge = car.add_node(root, "BP_DOOR", T=(30, -92, 70))
    car.add_mesh(hinge, "BP_DOOR_MESH", mesh.box((90, 6, 55), center=(-45, 0, 0)), like=body["file"], material="BP_PAINT")
    car.bind(hinge, rotate=E.vec3(0, 0, E.P(DOOR) * E.C(-65.0)))   # <-- door opens with DoorL1Open

    # (8) Lamps that switch with the headlights. Two small boxes; their visibility bound to the light signal
    #     (shown only when the headlights are on).
    for name, y in (("L", -70), ("R", 70)):
        lamp = car.add_mesh(root, f"BP_LAMP_{name}", mesh.box((10, 26, 18), center=(218, y, 60)),
                            like=body["file"], material=glass)
        car.bind(lamp, visible=E.P(LIGHTS, "Bool"))               # <-- on with the headlights

    return car.save()


def verify(out_dir):
    """Re-read the authored widget with the toolkit's own evaluator and confirm each feature responds to its
    HMI signal. Offline proof that the bindings are wired correctly (not a substitute for an on-car look)."""
    from capabilities.vehicle_models.tools import pbw
    w = pbw.read_widget(os.path.join(out_dir, "vehicle", "widget.pbw"))
    B = {d["node"].rsplit("|", 1)[-1]: d for d in w["bindings"] if "BP_" in d["node"]}
    ok = True

    def check(label, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        ok = ok and cond

    ev = pbw.evaluate
    check("wheels respond to WheelsRotationValue",
          abs(ev(w, {"WheelsRotationValue": 1000.0})(B["BP_WHEEL_LF"]["rotate"])[1]) > 1e-3
          and abs(ev(w, {"WheelsRotationValue": 0.0})(B["BP_WHEEL_LF"]["rotate"])[1]) < 1e-6)
    check("roll-in: parked back ~260 cm, open ~0",
          abs(ev(w, {"FESStaging": 0.0})(B["BP_ROOT"]["translate"])[0] - 260) < 1.0
          and abs(ev(w, {"FESStaging": 1.0})(B["BP_ROOT"]["translate"])[0]) < 1.0)
    check("door opens with DoorL1Open (0 -> -65 deg)",
          abs(ev(w, {"DoorL1Open": 0.0})(B["BP_DOOR"]["rotate"])[2]) < 1e-6
          and abs(ev(w, {"DoorL1Open": 1.0})(B["BP_DOOR"]["rotate"])[2] + 65) < 1e-3)
    check("lamps gate on LightOn",
          B["BP_LAMP_L"]["node"] in pbw.hidden_nodes(w, {"LightOn": 0})
          and B["BP_LAMP_L"]["node"] not in pbw.hidden_nodes(w, {"LightOn": 1}))
    check("idle clock drives the beacon (phase .25 -> 90 deg)",
          abs(ev(w, {"anim:BP_IDLE.phase": 0.25})(B["BP_BEACON"]["rotate"])[2] - 90) < 1e-3)
    print("  " + ("all features verified" if ok else "SOME CHECKS FAILED"))
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the blueprint custom car (an original, all-features example).")
    ap.add_argument("--out", required=True, help="output series folder (gets a copy of the template + your edits)")
    ap.add_argument("--template-dir", help="stock series folder (holds vehicle/). Default: F30 under your HMI tree.")
    ap.add_argument("--verify", action="store_true", help="after building, check each feature responds to its signal")
    a = ap.parse_args(argv)
    tmpl = a.template_dir or os.path.join(hmi.ro(), "bmw", "widgetasset", "vehicles", "F30")
    if not os.path.isdir(os.path.join(tmpl, "vehicle")):
        raise SystemExit(f"no vehicle/ under {tmpl} — point --template-dir at a stock series folder, or\n"
                         "configure your HMI tree for the packager (see ../../packager/hmi.py).")
    out = build(tmpl, a.out)
    print(f"blueprint built -> {out}")
    rc = 0
    if a.verify:
        rc = 0 if verify(out) else 1
    print("package it:  python -m capabilities.vehicle_models.packager.package "
          f"--id BLUEPRINT --name 'Blueprint car' --folder {out} --template F30 --out blueprint.nbtcar")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
