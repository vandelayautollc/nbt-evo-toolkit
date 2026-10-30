#!/usr/bin/env python3
"""
Assemble an NBT-Evo HMI 3D car (…/widgetasset/vehicles/<series>/vehicle/) from its scene graph and RSVI meshes.

scene.pbx is a raw protobuf HmiScenegraph.TScene. The real schema is embedded in HmiMain3D and recovered by
emulator/tools/hmi_pack.py (descriptor set emulator/data/hmi_descriptors.bin); `protoc --decode` / `--encode`
with that set round-trips the F30 scene byte-for-byte, so edit scenes as text. This module reads it by field number:
  TScene: 1 root TNode, 3 materialLibrary, 4 renderPass[]
  TNode: 1 name ("|VEHICLE|CAD|…" full path), 2 renderOrder, 3 childSortOrderRank, 4 scale, 5 rotation (degrees),
        6 translation (cm), 10 child[], 11 mesh[] TMesh, 13 renderLayer[] TRenderLayer
  TMesh: 1 baseNode (the "…Shape" node; a shared mesh keeps its source's shape name), 2 meshResource
        "meshes/<16 hex><NAME>Shape.ctm" (-> the .rsvi of the same name), 3 materialReference, 4 uniform[]
        {1 name, 2 TNumericValue {1 Int, 3 Float, 5 Vec3f, 6 Vec4f…}, 3 type}, 5 attributeParameter[]
  TRenderLayer: 1 baseNode, 2 materialReference (the composite quad), 3 uniform[], 4 renderPass, 8 child[]
        (RL0_PT holds layer RL0, whose children RL1_PT/RL2_PT hold the wheel and body layers)
  TMaterialLib: 1 material[] {1 name_SG, 2 renderMode, 3 shaderReference, 4 texture[] {1 name, 2 bitmapReference,
        3 minFilter, 4 magFilter, 6 anisotropicSamples, 7 wrapModeU, 8 wrapModeV, 9 uniformName}},
        2 shader[] {1 name, 2 vertexShader, 3 fragmentShader -> shaders/<name>.{vert,frag}.shd, SGX binaries},
        3 bitmap[] {1 name, 2 resource | render target 4 width 5 height}
  TRenderMode: 1 winding, 2 culling (TEFace 1 Front 2 Back 3 FrontAndBack 4 None), 3 blending {1 opColor, 2 opAlpha
        (TEBlendOperation 1 None 2 Add 3 Subtract 4 ReverseSubtract), 3 srcColor, 4 srcAlpha, 5 dstColor, 6 dstAlpha
        (TEBlendFactor 1 Zero 2 One 3 SrcColor 4 InvSrcColor 5 SrcAlpha 6 SrcAlphaSaturate 7 InvSrcAlpha 8 DstColor
        9 InvDstColor 10 DstAlpha 11 InvDstAlpha)}, 5 depthCompare (TECompareFunction 1 Never 2 Less 3 LessEqual
        4 Equal 5 NotEqual 6 GreaterEqual 7 Greater 8 Always), 6 depthWrite, 10 colorWrite {red green blue alpha}
  Texture filters: 1 Nearest 2 Linear 3-6 mipmapped (6 LinearMipMapLinear). Wrap: 1 Repeat 2 ClampToEdge 3 Mirrored.
Rotation is applied as Rz·Ry·Rx (Maya's default XYZ order). Several nodes can share one mesh file (the 4 rims),
so there are more mesh nodes than .rsvi files. Which nodes show is decided by the widget (pbw.py): e.g. the
wheel cut-outs (MRLC) and brake cuts (MBRC) are hidden unless a tyre/brake highlight or X-ray is on.

Usage:  rsvi_scene.py tree   <vehicle dir>                 node tree with transforms and meshes
        rsvi_scene.py obj    <vehicle dir> <out.obj>       whole car in world space, one OBJ group per mesh node
        rsvi_scene.py render <vehicle dir> <out.png>       4-view flat-shaded preview (needs numpy + Pillow)
        rsvi_scene.py json   <vehicle dir> [out.json]      nodes, materials and bitmaps for a viewer
"""
import math, os, re, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsvi import read_rsvi, attr  # noqa: E402
from pbw import Msg, read_widget, evaluate, hidden_nodes  # noqa: E402

# Parts that are effects, not car body: ground/shadow planes, headlight beams, masks, PDC overlays.
EFFECTS = ("GROUND", "MLFG", "MLIC", "MASK", "PDC", "SHADOW")

# Preview colours by material code (the 4 letters in "…__MWRM_1"); 3-letter keys cover a family.
MATERIAL_COLOURS = {
    "MCP": (165, 170, 180), "MGL": (45, 60, 80), "MWRM": (205, 208, 214), "MWCT": (38, 38, 40),
    "MBRB": (95, 95, 100), "MBP": (30, 30, 33), "MCH": (225, 230, 235), "MLI": (240, 225, 180),
    "MLF": (240, 225, 180), "MIN": (85, 75, 70), "MFI": (22, 22, 24), "MLG": (70, 100, 170),
}


def _varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7F) << s; s += 7
        if c < 0x80:
            return r, i


def _fields(b, lo, hi):
    i, out = lo, []
    while i < hi:
        key, i = _varint(b, i)
        fn, wt = key >> 3, key & 7
        if wt == 0:
            v, i = _varint(b, i); out.append((fn, 0, v))
        elif wt == 2:
            n, i = _varint(b, i); out.append((fn, 2, (i, i + n))); i += n
        elif wt == 5:
            out.append((fn, 5, struct.unpack_from("<f", b, i)[0])); i += 4
        elif wt == 1:
            i += 8
        else:
            raise ValueError("bad wire type")
    return out


def read_scene(path):
    b = open(path, "rb").read()
    nodes = []

    def vec(r):
        d = {fn: v for fn, t, v in _fields(b, *r) if t == 5}
        return (d.get(1, 0.0), d.get(2, 0.0), d.get(3, 0.0))

    def header(node, r):
        for fn, t, v in _fields(b, *r):
            if fn == 1 and t == 2: node["name"] = b[v[0]:v[1]].decode("latin1")
            elif fn == 4 and t == 2: node["S"] = vec(v)
            elif fn == 5 and t == 2: node["R"] = vec(v)
            elif fn == 6 and t == 2: node["T"] = vec(v)

    def walk(r, parent):
        node = {"name": "", "S": (1, 1, 1), "R": (0, 0, 0), "T": (0, 0, 0), "mesh": None, "parent": parent}
        idx = len(nodes); nodes.append(node)
        header(node, r)
        for fn, t, v in _fields(b, *r):
            if t != 2:
                continue
            if fn == 10:
                walk(v, idx)
            elif fn == 11:
                m = re.search(rb"meshes/[0-9A-F]{16}[^\x00\"]*?Shape\.ctm", b[v[0]:v[1]])
                if m: node["mesh"] = os.path.basename(m.group(0).decode())[:-4]
            elif fn == 13:                         # renderLayer: its baseNode is a child, holding the layer's children
                layer = {"name": "", "S": (1, 1, 1), "R": (0, 0, 0), "T": (0, 0, 0), "mesh": None, "parent": idx}
                lidx = len(nodes); nodes.append(layer)
                for f2, t2, v2 in _fields(b, *v):
                    if f2 == 1 and t2 == 2: header(layer, v2)
                    elif f2 == 8 and t2 == 2: walk(v2, lidx)

    for fn, t, v in _fields(b, 0, len(b)):
        if fn == 1 and t == 2:
            walk(v, -1)
    return nodes


def _matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _local(n):
    x, y, z = (math.radians(a) for a in n["R"])
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    r = [[cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
         [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
         [-sy, cy * sx, cy * cx]]
    s = n["S"]; t = n["T"]
    return [[r[i][0] * s[0], r[i][1] * s[1], r[i][2] * s[2], t[i]] for i in range(3)] + [[0, 0, 0, 1]]


def world_parts(vehicle_dir, include_effects=False, params=None):
    """Yields (node name, mesh dict, 4x4 world matrix) for every mesh node the widget shows with [params]."""
    nodes = read_scene(os.path.join(vehicle_dir, "scene.pbx"))
    wp = os.path.join(vehicle_dir, "widget.pbw")
    hidden = hidden_nodes(read_widget(wp), params) if os.path.exists(wp) else set()
    world, off = [], []
    for n in nodes:
        local = _local(n)
        world.append(_matmul(world[n["parent"]], local) if n["parent"] >= 0 else local)
        off.append(n["name"] in hidden or (n["parent"] >= 0 and off[n["parent"]]))
    cache = {}
    for n, w, o in zip(nodes, world, off):
        if not n["mesh"] or o:
            continue
        leaf = n["name"].split("|")[-1]
        if not include_effects and any(e in n["name"] for e in EFFECTS):
            continue
        p = os.path.join(vehicle_dir, "meshes", n["mesh"] + ".rsvi")
        if p not in cache:
            cache[p] = read_rsvi(p)
        yield leaf, cache[p], w


def _xf(w, p):
    return tuple(w[i][0] * p[0] + w[i][1] * p[1] + w[i][2] * p[2] + w[i][3] for i in range(3))


def export_obj(vehicle_dir, out):
    base = 1
    with open(out, "w") as f:
        f.write(f"# {vehicle_dir} assembled from scene.pbx (units: cm, z up, x toward the rear)\n")
        for leaf, m, w in world_parts(vehicle_dir):
            pos = attr(m, 0)
            f.write(f"o {leaf}\n")
            for p in pos:
                f.write("v %.4f %.4f %.4f\n" % _xf(w, p))
            ix = m["indices"]
            for k in range(0, len(ix), 3):
                f.write(f"f {ix[k] + base} {ix[k + 1] + base} {ix[k + 2] + base}\n")
            base += len(pos)


def render(vehicle_dir, out):
    import numpy as np
    from PIL import Image, ImageDraw
    tris, cols = [], []
    for leaf, m, w in world_parts(vehicle_dir):
        P = np.array(attr(m, 0)); W = np.array(w)
        P = P @ W[:3, :3].T + W[:3, 3]
        tag = re.search(r"_(M[A-Z0-9]{3})_\d+$", leaf)
        col = MATERIAL_COLOURS.get(tag.group(1)[:3] if tag else "", (150, 150, 160))
        col = MATERIAL_COLOURS.get(tag.group(1) if tag else "", col)
        I = np.array(m["indices"]).reshape(-1, 3)
        tris.append(P[I]); cols += [col] * len(I)
    T = np.concatenate(tris); cols = np.array(cols)
    flat = T.reshape(-1, 3); T = T - (flat.min(0) + flat.max(0)) / 2
    Wd, Hd = 640, 360
    sheet = Image.new("RGB", (Wd * 2, Hd * 2), (20, 20, 28))
    for vi, (az, el) in enumerate([(35, 15), (0, 3), (90, 5), (145, 25)]):
        a, e = math.radians(az), math.radians(el)
        X, Y, Z = T[..., 0], T[..., 1], T[..., 2]
        sx = X * math.cos(a) - Y * math.sin(a); y1 = X * math.sin(a) + Y * math.cos(a)
        depth = y1 * math.cos(e) + Z * math.sin(e); sy = Z * math.cos(e) - y1 * math.sin(e)
        s = 0.9 * min(Wd / np.ptp(sx), Hd / np.ptp(sy)); px = Wd / 2 + sx * s; py = Hd / 2 - sy * s
        V = np.stack([sx, sy, depth], -1); nrm = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
        shade = 0.35 + 0.65 * np.abs(nrm[:, 2]) / (np.linalg.norm(nrm, axis=1) + 1e-12)
        im = Image.new("RGB", (Wd, Hd), (20, 20, 28)); d = ImageDraw.Draw(im)
        for k in np.argsort(depth.mean(1)):        # painter's algorithm: far to near
            d.polygon([(px[k, j], py[k, j]) for j in range(3)], fill=tuple(int(min(255, c * shade[k])) for c in cols[k]))
        sheet.paste(im, ((vi % 2) * Wd, (vi // 2) * Hd))
    sheet.save(out)


def _vec(m):
    return [m.get(k) or 0.0 for k in (1, 2, 3)] if m else None


def _uniform(u):
    v = u.msg(2)
    if v is None:
        return None
    if v.get(3) is not None:
        return v.get(3)
    for fn, n in ((5, 3), (6, 4)):
        if v.msg(fn):
            return [v.msg(fn).get(k) or 0.0 for k in range(1, n + 1)]
    return 0.0


def scene_json(vehicle_dir):
    """The scene as plain data: nodes (pre-order, parent index, S/R/T, mesh, material, uniform defaults),
    materials (shader, render state, textures) and bitmaps."""
    b = open(os.path.join(vehicle_dir, "scene.pbx"), "rb").read()
    top = Msg(b, 0, len(b))
    nodes = []

    def header(node, h):
        node["name"] = h.str(1) or node.get("name", "")
        for fn, key in ((4, "S"), (5, "R"), (6, "T")):
            if h.msg(fn):
                node[key] = _vec(h.msg(fn))

    def walk(m, parent):
        node = {"name": "", "parent": parent, "S": [1, 1, 1], "R": [0, 0, 0], "T": [0, 0, 0]}
        idx = len(nodes); nodes.append(node)
        header(node, m)
        mi = m.msg(11)
        if mi:
            node["mesh"] = os.path.basename(mi.str(2))[:-4] + ".rsvi"
            # the shape node's own path; a shared mesh keeps its source's shape name
            # ("…|WHEELLR__MWCT_1|WHEELLF__MWCT_1Shape"), and widget uniform bindings address it by that path
            node["shape"] = mi.msg(1).str(1) if mi.msg(1) else None
            node["material"] = mi.str(3)
            node["uniforms"] = {u.str(1): _uniform(u) for u in mi.msgs(4)}
        for c in m.msgs(10):
            walk(c, idx)
        for rl in m.msgs(13):                 # renderLayer: its baseNode becomes a child holding the layer's children
            layer = {"name": "", "parent": idx, "S": [1, 1, 1], "R": [0, 0, 0], "T": [0, 0, 0],
                     "layer": rl.str(2)}
            lidx = len(nodes); nodes.append(layer)
            if rl.msg(1):
                header(layer, rl.msg(1))
            for c in rl.msgs(8):
                walk(c, lidx)

    walk(top.msg(1), -1)
    lib = top.msg(3)
    mats = {}
    for m in lib.msgs(1):
        st = m.msg(2); bl = st.msg(3) if st else None; cm = st.msg(10) if st else None
        mats[m.str(1)] = {
            "shader": m.str(3),
            "cull": st.get(2) if st else 2,
            # [opColor, opAlpha, srcColor, srcAlpha, dstColor, dstAlpha]; opColor 1 = no blending
            "blend": [bl.get(k) or 0 for k in range(1, 7)] if bl else [1, 1, 0, 0, 0, 0],
            "depthTest": st.get(5) if st else 3,
            "depthWrite": st.get(6) if st else 1,
            "colorMask": [cm.get(k) or 0 for k in (1, 2, 3, 4)] if cm else [1, 1, 1, 1],
            "textures": [{"sampler": t.str(9), "bitmap": t.str(2), "filter": [t.get(3), t.get(4)],
                          "anisotropy": t.get(6), "wrap": [t.get(7), t.get(8)]} for t in m.msgs(4)],
        }
    bitmaps = {}
    for t in lib.msgs(3):
        if t.str(2):
            bitmaps[t.str(1)] = os.path.basename(t.str(2))
        else:
            bitmaps[t.str(1)] = {"target": [t.get(4), t.get(5)]}
    return {"nodes": nodes, "materials": mats, "bitmaps": bitmaps}


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    cmd, vdir = argv[1], argv[2]
    if cmd == "tree":
        for n in read_scene(os.path.join(vdir, "scene.pbx")):
            print(n["name"], n["S"], n["R"], n["T"], n["mesh"] or "")
    elif cmd == "obj":
        export_obj(vdir, argv[3])
    elif cmd == "render":
        render(vdir, argv[3])
    elif cmd == "json":
        import json
        s = json.dumps(scene_json(vdir), separators=(",", ":"))
        if len(argv) > 3: open(argv[3], "w").write(s)
        else: print(s)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
