"""What the HMI needs to see a new series folder: index bundles, a registry override, a prototype widget.

A series folder `vehicles/<S>/` is five index bundles in root 7's resources.pbr (both camera_crane files, the
vehicle scene with its bitmaps/meshes/shaders, the vehicle widget with the same plus scene.pbx, and the
`vehicle_<S>` prototype), all gated by the series' variant flag. Per-file rules, exact for all 215 F30 files:
  meshes/X.rsvi   preparationphase 1, aliases meshes/X.rsvi + meshes/X.ctm (scene.pbx names the .ctm)
  bitmaps/X.png   preparationphase 1, alias bitmaps/X.png
  shaders/X.shd   alias shaders/X.shd
  scene.pbx       aliases scene.pbx + scene.ptx (the widgets ask for scene.ptx)
"""
import copy, os, re

from .hmi import VEHICLES, proto

KINDS = ("scene", "bitmaps", "meshes", "shaders")


def kind(rel):
    """rel is relative to vehicle/ or camera_crane/."""
    if rel == "scene.pbx":
        return "scene"
    top = rel.split("/", 1)[0]
    return top if top in KINDS and "/" in rel else None


def make_resource(template, file, rel):
    r = copy.deepcopy(template)
    del r.file[:]; r.file.append(file)
    del r.alias[:]
    k = kind(rel)
    if k == "meshes":
        r.alias.extend([rel, rel[:-len(".rsvi")] + ".ctm"]); r.preparationphase = 1
    elif k == "bitmaps":
        r.alias.append(rel); r.preparationphase = 1
    elif k == "shaders":
        r.alias.append(rel); r.ClearField("preparationphase")
    else:
        r.alias.extend(["scene.pbx", "scene.ptx"]); r.ClearField("preparationphase")
    return r


def folder_files(folder, part):
    """Files under <folder>/<part>/ that belong in the index, relative to that part."""
    root = os.path.join(folder, part)
    out = []
    for d, _, fs in os.walk(root):
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
            if kind(rel) and (rel == "scene.pbx" or rel.endswith((".rsvi", ".png", ".shd"))):
                out.append(rel)
    return out


def series_bundles(index_bytes, series):
    idx = proto("HmiResource.TResourceDefinition").FromString(index_bytes)
    pre = f"{VEHICLES}/{series}/"
    found = [b for b in idx.resourcebundle if b.contextresource.file[0].startswith(pre)]
    if len(found) != 5:
        raise ValueError(f"expected 5 index bundles for {series}, found {len(found)}")
    return found


def chassis_bundles(index_bytes, series, name, folder, root=VEHICLES, gated=True):
    """The five bundles for a chassis folder installed at `<root>/<name>/` (paths relative to /opt/hmi/data/ro),
    modelled on the series' own (order, file rules, and its variant flags when [gated]), with the file lists taken
    from the folder. Ungated bundles register on every car; the app's packages use that with root vae/vehicles."""
    old, new = f"{VEHICLES}/{series}/", f"{root}/{name}/"
    aliases = {f"vehicles/{series}/vehicle_{series}": f"vehicles/{name}/vehicle_{name}",
               f"vehicles/{series}/vehicle": f"vehicles/{name}/vehicle",
               f"vehicles/{series}/camera_crane": f"vehicles/{name}/camera_crane"}
    out = []
    for tb in series_bundles(index_bytes, series):
        b = copy.deepcopy(tb)
        ctx = b.contextresource
        rest = ctx.file[0][len(old):]
        if rest.startswith(f"vehicle_{series}/"):
            rest = f"vehicle_{name}/" + rest[len(f"vehicle_{series}/"):]
        ctx.file[0] = new + rest
        for i, a in enumerate(ctx.alias):
            if a not in aliases:
                raise ValueError(f"unexpected context alias {a}")
            ctx.alias[i] = aliases[a]
        if tb.resources:
            part = tb.resources[0].file[0][len(old):].split("/", 1)[0]          # vehicle or camera_crane
            order = {r.file[0][len(old) + len(part) + 1:]: (i, r) for i, r in enumerate(tb.resources)}
            kinds = []
            for r in tb.resources:
                k = kind(r.file[0][len(old) + len(part) + 1:])
                if k not in kinds:
                    kinds.append(k)
            have = [f for f in folder_files(folder, part) if kind(f) in kinds]
            have.sort(key=lambda f: (kinds.index(kind(f)), order.get(f, (len(order), None))[0], f))
            del b.resources[:]
            for rel in have:
                t = order[rel][1] if rel in order else next(r for r in tb.resources if kind(r.file[0][len(old) + len(part) + 1:]) == kind(rel))
                b.resources.append(make_resource(t, f"{new}{part}/{rel}", rel))
        if not gated:
            b.ClearField("variantFlag"); b.ClearField("orNotVariantFlag")
        out.append(b)
    return out


def patched_index(index_bytes, bundles):
    """Stock index + appended bundles. A repeated field merges by concatenation, so the stock bytes stay a
    byte-exact prefix and nothing BMW wrote is re-encoded."""
    extra = proto("HmiResource.TResourceDefinition")()
    extra.resourcebundle.extend(bundles)
    out = index_bytes + extra.SerializeToString(deterministic=True)
    n = len(proto("HmiResource.TResourceDefinition").FromString(out).resourcebundle)
    if n != len(proto("HmiResource.TResourceDefinition").FromString(index_bytes).resourcebundle) + len(bundles):
        raise AssertionError("patched index does not parse to stock + added bundles")
    return out


def registry_override(registry_bytes, series, name, conditional=True):
    """A registry collection that re-points every entry selecting vehicles/<series>/vehicle_<series> to the
    chassis: same variant flags, only vehicle_assetid and camera_crane_assetid. The rest of the series entry
    (PDC sectors, camera/radar positions, tailgate angles) describes the real car and stays BMW's.
    Not [conditional]: one entry with no flag, which applies to every car (the file loads last of all)."""
    coll = proto("HmiVariantRegistry.TVariantRegistryCollection").FromString(registry_bytes)
    want = f"vehicles/{series}/vehicle_{series}"
    out = proto("HmiVariantRegistry.TVariantRegistryCollection")()
    for e in coll.entry:
        params = {p.key.valueString: p for p in e.parameter}
        if "vehicle_assetid" not in params or params["vehicle_assetid"].variant.AssetId != want:
            continue
        if not conditional and out.entry:
            continue
        ne = out.entry.add()
        if conditional and e.HasField("variantFlag"):
            ne.variantFlag.CopyFrom(e.variantFlag)
        for key, value in (("vehicle_assetid", f"vehicles/{name}/vehicle_{name}"),
                           ("camera_crane_assetid", f"vehicles/{name}/camera_crane")):
            p = ne.parameter.add(); p.CopyFrom(params[key]); p.variant.AssetId = value
    if not out.entry:
        raise ValueError(f"no registry entry selects {want}")
    return out


def prototype(series_dir, series, name):
    """vehicle_<name>/widget.pbw: BMW's 67-byte prototype for the series, pointed at vehicles/<name>/vehicle."""
    w = proto("HmiWidget.TWidgetCollection").FromString(
        open(os.path.join(series_dir, f"vehicle_{series}", "widget.pbw"), "rb").read())
    assets = [x for x in w.widget if x.HasField("prototypeAsset")]
    if len(assets) != 1 or assets[0].prototypeAsset.AssetId != f"vehicles/{series}/vehicle":
        raise ValueError("unexpected prototype widget")
    assets[0].prototypeAsset.AssetId = f"vehicles/{name}/vehicle"
    return w.SerializeToString(deterministic=True)


REF = re.compile(rb"meshes/[A-Za-z0-9_]+\.ctm|bitmaps/[A-Za-z0-9_\-]+\.png|shaders/[A-Za-z0-9_]+\.(?:vert|frag)")


def missing_refs(folder):
    """Files scene.pbx names that the chassis folder lacks (the index can only list what exists).
    scene.pbx says meshes/X.ctm for meshes/X.rsvi and shaders/X.vert for shaders/X.vert.shd."""
    out = []
    for part in ("vehicle", "camera_crane"):
        have = set(folder_files(folder, part))
        for m in sorted({x.decode() for x in REF.findall(open(os.path.join(folder, part, "scene.pbx"), "rb").read())}):
            f = m[:-4] + ".rsvi" if m.endswith(".ctm") else m + ".shd" if m.startswith("shaders/") else m
            if f not in have:
                out.append(f"{part}/{f}")
    return out
