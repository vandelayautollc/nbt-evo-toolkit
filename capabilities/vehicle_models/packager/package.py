#!/usr/bin/env python3
"""
Build a custom-car package (.nbtcar) from a chassis folder.

    python -m capabilities.vehicle_models.packager.package \
        --id WARTHOG --name "M12 Warthog" --folder warthog/out/F30 [--preview shot.png]
    python -m capabilities.vehicle_models.packager.package --selftest

A chassis folder is a built series folder (``vehicle/`` + ``camera_crane/``) made on a stock
series' template (``--template``, default F30). The package is a zip, distributed apart from the
app and installed on the head unit under ``vae/vehicles/<ID>`` beneath ``/opt/hmi/data/ro``:

  car.json      metadata {format, id, name, version, author, description, root, template, files, bytes}
  preview.png   optional, shown in a model list
  bundles.pb    the five index bundles (HmiResource.TResourceDefinition), ungated, for every file
                under <root>/ — appended to each root-7 index (bmw/<line>/widgetasset/resources.pbr)
  registry.pb   one unconditional registry entry (HmiVariantRegistry) pointing vehicle_assetid /
                camera_crane_assetid at the model — written as bmw/<line>/widget/variantregistry.pbvar,
                which loads last, so any series shows the model
  files/...     the model folder as the head unit gets it (vehicle/, camera_crane/, vehicle_<ID>/)

Reads YOUR OWN extracted HMI tree (configure it per hmi.py). No HMI resources ship here.
(The My-Vehicle 2D-picture override, --hero in the research tree, needs a headless renderer and is
not yet ported — see ../README.md.)
"""
import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from capabilities.vehicle_models.packager import bundles as B  # noqa: E402
from capabilities.vehicle_models.packager import hmi  # noqa: E402

FORMAT = 1
ROOT = "vae/vehicles"                       # under /opt/hmi/data/ro; the app's own namespace on the head unit
ID_RE = re.compile(r"[A-Z0-9_]{1,24}")
ZIP_TIME = (2026, 1, 1, 0, 0, 0)            # fixed, so a package builds byte-identically


def build(car_id, name, folder, template, version, author, description, preview, out):
    taken = {s.upper() for s in hmi.stock_series()}
    if not ID_RE.fullmatch(car_id) or car_id in taken:
        raise SystemExit(f"--id {car_id}: needs [A-Z0-9_]{{1,24}} and must not be a stock series")
    for part in ("vehicle/scene.pbx", "vehicle/widget.pbw", "camera_crane/scene.pbx", "camera_crane/widget.pbw"):
        if not os.path.isfile(os.path.join(folder, part)):
            raise SystemExit(f"{folder} has no {part}")
    miss = B.missing_refs(folder)
    if miss:
        raise SystemExit(f"scene names files the folder lacks: {miss[:5]}")

    idx = hmi.stock(hmi.index_path(hmi.LINES[0]))     # any root-7 index holds the template's bundles
    root = f"{ROOT}/{car_id}"
    bundles = B.chassis_bundles(idx, template, car_id, folder, root=ROOT, gated=False)
    coll = B.proto("HmiResource.TResourceDefinition")()
    coll.resourcebundle.extend(bundles)
    bundles_pb = coll.SerializeToString(deterministic=True)
    registry_pb = B.registry_override(hmi.stock(hmi.BRAND_REGISTRY), template, car_id, conditional=False) \
        .SerializeToString(deterministic=True)

    files = {}
    for part in ("vehicle", "camera_crane"):
        for d, _, fs in os.walk(os.path.join(folder, part)):
            for f in fs:
                p = os.path.join(d, f)
                files[os.path.relpath(p, folder).replace(os.sep, "/")] = open(p, "rb").read()
    files[f"vehicle_{car_id}/widget.pbw"] = B.prototype(os.path.join(hmi.ro(), hmi.VEHICLES, template), template, car_id)

    # Every file the bundles list must ship: the head unit resolves them under <root>/.
    listed = set()
    for b in bundles:
        for r in [b.contextresource, *b.resources]:
            for f in r.file:
                if not f.startswith(root + "/"):
                    raise AssertionError(f"bundle file outside {root}: {f}")
                listed.add(f[len(root) + 1:])
    missing = sorted(listed - set(files))
    if missing:
        raise AssertionError(f"bundles list files the package lacks: {missing[:5]}")

    meta = {"format": FORMAT, "id": car_id, "name": name, "version": version, "author": author,
            "description": description, "root": root, "template": template,
            "files": len(files), "bytes": sum(len(v) for v in files.values())}
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        def put(arc, data):
            zi = zipfile.ZipInfo(arc, ZIP_TIME); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
            z.writestr(zi, data)
        put("car.json", json.dumps(meta, indent=1) + "\n")
        if preview:
            put("preview.png", open(preview, "rb").read())
        put("bundles.pb", bundles_pb)
        put("registry.pb", registry_pb)
        for rel in sorted(files):
            put(f"files/{rel}", files[rel])
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"{car_id}: {len(files)} files, {meta['bytes'] // 1024} KiB -> {out} "
          f"({os.path.getsize(out) // 1024} KiB, sha256 {sha[:16]})")
    return out


def selftest():
    """The bundle generator must rebuild every stock five-bundle series byte for byte (same root, gated), and every
    stock file it reads must match the signed manifest (hmi.stock() checks)."""
    bad = 0
    for line in hmi.LINES:
        idx = hmi.stock(hmi.index_path(line))
        ok, other = 0, []
        for s in hmi.stock_series():
            try:
                want = B.series_bundles(idx, s)
            except ValueError:
                other.append(s)                 # not the five-bundle layout (older series); not a template
                continue
            got = B.chassis_bundles(idx, s, s, os.path.join(hmi.ro(), hmi.VEHICLES, s))
            same = all(a.SerializeToString(deterministic=True) == b.SerializeToString(deterministic=True)
                       for a, b in zip(want, got))
            bad += not same
            ok += same
            if not same:
                print(f"{line} {s}: MISMATCH")
        print(f"{line}: {ok} series rebuilt byte-identically; other layouts: {' '.join(other)}")
    hmi.stock(hmi.BRAND_REGISTRY)
    print("selftest", "FAILED" if bad else "ok")
    return not bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--id", help="the model's id on the head unit: [A-Z0-9_]{1,24} (folder vae/vehicles/<ID>)")
    ap.add_argument("--name", help="what a model list shows")
    ap.add_argument("--folder", help="the built chassis folder (vehicle/ + camera_crane/)")
    ap.add_argument("--template", default="F30", help="stock series the folder was built on (default F30)")
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--author", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--preview", help="a PNG shown for the model")
    ap.add_argument("--out", help="default ./<id lowercase>.nbtcar")
    ap.add_argument("--selftest", action="store_true", help="prove the generator rebuilds stock series byte-identically")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if not (a.id and a.name and a.folder):
        ap.error("--id, --name and --folder are required")
    build(a.id, a.name, a.folder, a.template, a.version, a.author, a.description, a.preview,
          a.out or os.path.join(os.getcwd(), f"{a.id.lower()}.nbtcar"))


if __name__ == "__main__":
    main()
