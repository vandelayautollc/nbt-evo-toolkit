"""Geometry containers, procedural primitives, and the RSVI vertex-layout writer — the authoring core
for building your *own* 3D car.

A part returns a ``Mesh`` in the CAD frame (centimetres; **x = rear, y = right, z = up**). ``fill_layout``
interleaves it into a given RSVI element layout; ``write_slot`` moves a mesh into a scene node's local frame
and writes the ``.rsvi`` with that node's exact vertex layout. The primitives (``box``, ``cylinder``) let you
compose an original model from code with no external asset.

Ported from the reverse-engineering kit; depends only on numpy + this package's ``rsvi`` writer.
"""
import numpy as np

from .rsvi import write_rsvi_arrays

WHITE = (1.0, 1.0, 1.0, 1.0)


class Mesh:
    """Indexed triangles. P (n,3); N (n,3) or None; UV0/UV1 (n,2) or None; COL (n,4) or None (a_Color);
    I (m,3), counter-clockwise front faces."""

    def __init__(self, P, I, N=None, UV0=None, UV1=None, COL=None, name=""):
        self.P = np.asarray(P, float).reshape(-1, 3)
        self.I = np.asarray(I, np.int64).reshape(-1, 3)
        self.N = None if N is None else np.asarray(N, float).reshape(-1, 3)
        self.UV0 = None if UV0 is None else np.asarray(UV0, float).reshape(-1, 2)
        self.UV1 = None if UV1 is None else np.asarray(UV1, float).reshape(-1, 2)
        self.COL = None if COL is None else np.asarray(COL, float).reshape(-1, 4)
        self.name = name

    def __len__(self):
        return len(self.I)

    @staticmethod
    def concat(meshes, name=""):
        meshes = [m for m in meshes if m is not None and len(m)]
        if not meshes:
            return None
        base = np.cumsum([0] + [len(m.P) for m in meshes[:-1]])

        def cat(attr, width, fill):
            if all(getattr(m, attr) is None for m in meshes):
                return None
            return np.concatenate([getattr(m, attr) if getattr(m, attr) is not None
                                   else np.tile(fill, (len(m.P), 1)) for m in meshes]).reshape(-1, width)
        return Mesh(np.concatenate([m.P for m in meshes]), np.concatenate([m.I + b for m, b in zip(meshes, base)]),
                    N=cat("N", 3, [0, 0, 1]), UV0=cat("UV0", 2, [0, 0]), UV1=cat("UV1", 2, [0, 0]),
                    COL=cat("COL", 4, WHITE), name=name)

    def transformed(self, M):
        """Apply a 4x4 (points) and its inverse-transpose (normals); flips winding for mirroring matrices."""
        P = self.P @ M[:3, :3].T + M[:3, 3]
        N = None
        if self.N is not None:
            N = self.N @ np.linalg.inv(M[:3, :3])
            N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
        I = self.I[:, ::-1] if np.linalg.det(M[:3, :3]) < 0 else self.I
        return Mesh(P, I, N, self.UV0, self.UV1, self.COL, self.name)

    def translated(self, t):
        M = np.eye(4); M[:3, 3] = t
        return self.transformed(M)


def smooth_normals(P, I):
    """Area-weighted vertex normals over shared vertex indices."""
    fn = np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]])
    N = np.zeros_like(P)
    for k in range(3):
        np.add.at(N, I[:, k], fn)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)


def tangents(P, N, UV, I):
    """Per-vertex tangent and binormal (unit, Gram-Schmidt against N), as BMW stores them (w = 0)."""
    p0, p1, p2 = P[I[:, 0]], P[I[:, 1]], P[I[:, 2]]
    t0, t1, t2 = UV[I[:, 0]], UV[I[:, 1]], UV[I[:, 2]]
    e1, e2 = p1 - p0, p2 - p0
    d1, d2 = t1 - t0, t2 - t0
    r = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(r) < 1e-12, 1e-12, r)
    sdir = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / r[:, None]
    tdir = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / r[:, None]
    T = np.zeros_like(P); B = np.zeros_like(P)
    for k in range(3):
        np.add.at(T, I[:, k], sdir); np.add.at(B, I[:, k], tdir)
    T = T - N * np.sum(N * T, 1, keepdims=True)
    bad = np.linalg.norm(T, axis=1) < 1e-9
    if bad.any():
        a = np.where(np.abs(N[bad, 0:1]) < 0.9, [[1, 0, 0]], [[0, 1, 0]])
        T[bad] = np.cross(N[bad], a)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    hand = np.sign(np.sum(np.cross(N, T) * B, 1, keepdims=True)); hand[hand == 0] = 1
    B = np.cross(N, T) * hand
    return T, B


def tiny(at=(0.0, 0.0, 0.0)):
    """A 1 mm placeholder triangle at [at] — fills a scene slot you want *invisible* (so its node, material and
    every widget binding stay valid) while nothing shows. Use it to blank the stock car's meshes."""
    a = np.asarray(at, float)
    P = a + np.array([[0, 0, 0], [0.1, 0, 0], [0, 0, 0.1]])
    return Mesh(P, [[0, 1, 2]], N=[[0, -1, 0]] * 3, UV0=[[0, 0]] * 3, UV1=[[0, 0]] * 3, COL=[WHITE] * 3,
                name="placeholder")


# ---- procedural primitives (original geometry, no external asset) ----

def box(size, center=(0, 0, 0), col=None):
    """An axis-aligned box. size = (sx, sy, sz) cm; center in the CAD frame. 24 verts (flat-shaded faces)."""
    sx, sy, sz = (s / 2.0 for s in size)
    cx, cy, cz = center
    faces = [  # (normal, four corners CCW seen from outside)
        ([0, 0, 1], [(-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]),      # +z top
        ([0, 0, -1], [(-sx, sy, -sz), (sx, sy, -sz), (sx, -sy, -sz), (-sx, -sy, -sz)]),  # -z bottom
        ([1, 0, 0], [(sx, -sy, -sz), (sx, sy, -sz), (sx, sy, sz), (sx, -sy, sz)]),       # +x rear
        ([-1, 0, 0], [(-sx, sy, -sz), (-sx, -sy, -sz), (-sx, -sy, sz), (-sx, sy, sz)]),  # -x front
        ([0, 1, 0], [(sx, sy, -sz), (-sx, sy, -sz), (-sx, sy, sz), (sx, sy, sz)]),       # +y right
        ([0, -1, 0], [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, -sy, sz), (-sx, -sy, sz)]),  # -y left
    ]
    P, N, I = [], [], []
    for nrm, corners in faces:
        b = len(P)
        for c in corners:
            P.append((c[0] + cx, c[1] + cy, c[2] + cz)); N.append(nrm)
        I += [[b, b + 1, b + 2], [b, b + 2, b + 3]]
    return Mesh(P, I, N=N, COL=None if col is None else [col] * len(P), name="box")


def cylinder(radius, length, axis="y", center=(0, 0, 0), segments=24, col=None):
    """A capped cylinder of [length] along [axis] ('x'|'y'|'z'), [radius] cm. Good for wheels (axis 'y')."""
    ax = {"x": 0, "y": 1, "z": 2}[axis]
    u, v = [i for i in range(3) if i != ax]
    P, N, I = [], [], []
    th = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    rim = np.stack([np.cos(th), np.sin(th)], 1) * radius
    for sign in (-1, 1):                                   # the two end rings
        b = len(P)
        for (a, c) in rim:
            p = [0, 0, 0]; p[ax] = sign * length / 2; p[u] = a; p[v] = c
            P.append(p); n = [0, 0, 0]; n[u], n[v] = a, c; N.append(n)
    for i in range(segments):                              # side quads
        j = (i + 1) % segments
        a0, a1, b0, b1 = i, j, segments + i, segments + j
        I += [[a0, a1, b1], [a0, b1, b0]]
    for sign, base in ((-1, 0), (1, segments)):            # caps (fan from a center vertex)
        c = len(P); p = [0, 0, 0]; p[ax] = sign * length / 2; P.append(p)
        nn = [0, 0, 0]; nn[ax] = sign; N.append(nn)
        for i in range(segments):
            j = (i + 1) % segments
            tri = [c, base + i, base + j] if sign > 0 else [c, base + j, base + i]
            I += [tri]
    P = np.array(P, float) + np.array(center, float)
    return Mesh(P, I, N=N, COL=None if col is None else [col] * len(P), name="cylinder")


# ---- RSVI layout fill ----

def fill_layout(mesh, elements):
    """Interleave mesh data into an RSVI element list. Missing data: normal = smooth, uv = 0, a_Color = white,
    tangent/binormal from uv0. ``elements`` is a scene node's own vertex layout (copied from the template)."""
    n = len(mesh.P)
    cols = []
    T = B = None
    N = mesh.N if mesh.N is not None else smooth_normals(mesh.P, mesh.I)
    for e in elements:
        u, name = e["usage"], e["name"]
        if u == 0:
            cols.append(mesh.P)
        elif u == 1:
            cols.append(N)
        elif u == 2:
            uv = mesh.UV0 if e["index"] == 0 else mesh.UV1
            cols.append(uv if uv is not None else np.zeros((n, 2)))
        elif name == "a_Color":
            cols.append(mesh.COL if mesh.COL is not None else np.tile(WHITE, (n, 1)))
        elif name in ("a_Tangent", "a_Binormal"):
            if T is None:
                uv = mesh.UV0 if mesh.UV0 is not None else np.zeros((n, 2))
                T, B = tangents(mesh.P, N, uv, mesh.I)
            v = T if name == "a_Tangent" else B
            cols.append(np.hstack([v, np.zeros((n, 1))]))
        else:
            raise ValueError(f"unknown custom element {name}")
    return np.hstack(cols).astype(np.float32)


def write_slot(path, mesh, matrix, elements):
    """Write [mesh] (CAD frame) to the RSVI [path], moved into the local frame given by [matrix] (node->CAD)
    and interleaved into [elements] (that node's layout)."""
    local = mesh.transformed(np.linalg.inv(matrix))
    if len(local.P) > 0x10000:
        raise ValueError(f"{path}: {len(local.P)} vertices > 65536; split it")
    verts = fill_layout(local, elements)
    if not np.all(np.isfinite(verts)):
        raise ValueError(f"{path}: non-finite vertex data")
    write_rsvi_arrays(path, elements, verts, local.I.astype(np.uint16))
    return len(local.P), len(local.I)
