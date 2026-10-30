"""A stock vehicle folder read as an authoring **template**: every mesh file ("slot"), the scene nodes that
draw it, each node's vertex layout, and the frame (node -> CAD) its vertices live in.

You author a custom car by *mutating a copy of a stock series' ``vehicle/`` folder* (e.g. F30) so scene.pbx
keeps every node, material, resource path and the widget's bindings, then adding your own content beside them.
This reader gives the builder (``author.py``) the node paths, matrices, materials and layouts it needs.

The stock folder comes from **your own** extracted HMI tree (see ``packager/hmi.py``); this ships no BMW data.
"""
import math
import os
import re
import struct

import numpy as np

from ..packager.hmi import proto


def rsvi_header(path):
    """Element list + counts of an RSVI file without decompressing it (the node's vertex layout)."""
    b = open(path, "rb").read(4096)
    assert b[:4] == b"RSVI", path
    (ne,) = struct.unpack_from("<I", b, 4); i = 8
    els = []
    for _ in range(ne):
        off, usage, idx = struct.unpack_from("<III", b, i); i += 12
        name = None
        if usage == 3:
            j = b.index(b"\0", i); name = b[i:j].decode(); i = j + 1
        els.append({"offset": off, "usage": usage, "index": idx, "name": name})
    nv, nt, csz = struct.unpack_from("<III", b, i)
    return {"elements": els, "numVertices": nv, "numTriangles": nt}


def local_matrix(node):
    """4x4 of a TNode: T * Rz * Ry * Rx * S (Maya XYZ order, degrees)."""
    s = [node.scale.x, node.scale.y, node.scale.z] if node.HasField("scale") else [1, 1, 1]
    r = [node.rotation.x, node.rotation.y, node.rotation.z] if node.HasField("rotation") else [0, 0, 0]
    t = [node.translation.x, node.translation.y, node.translation.z] if node.HasField("translation") else [0, 0, 0]
    x, y, z = (math.radians(a) for a in r)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    R = np.array([[cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
                  [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
                  [-sy, cy * sx, cy * cx]])
    M = np.eye(4); M[:3, :3] = R * np.array(s); M[:3, 3] = t
    return M


def walk(node, parent=np.eye(4)):
    """Yield (node, cad_matrix) pre-order, including render-layer base nodes + children. The CAD node's own
    transform is excluded, so matrices map a node's local frame to the shared CAD frame."""
    is_cad = node.name == "|VEHICLE|CAD"
    M = np.eye(4) if is_cad else parent @ local_matrix(node)
    yield node, M
    for c in node.child:
        yield from walk(c, M)
    for rl in node.renderLayer:
        base = rl.baseNode
        Mb = M @ local_matrix(base)
        yield base, Mb
        for c in rl.child:
            yield from walk(c, Mb)


class Template:
    def __init__(self, vehicle_dir):
        self.dir = vehicle_dir
        self.scene = proto("HmiScenegraph.TScene").FromString(
            open(os.path.join(vehicle_dir, "scene.pbx"), "rb").read())
        self.nodes = {}                  # path -> (TNode, node->CAD matrix)
        self.slots = {}                  # rsvi file name -> dict(file, nodes, material, code, matrix, node, elements…)
        for node, M in walk(self.scene.root):
            self.nodes[node.name] = (node, M)
            for mesh in node.mesh:
                f = os.path.basename(mesh.meshResource)[:-4] + ".rsvi"
                mm = re.search(r"_(M[A-Z0-9]{3})_", mesh.materialReference)
                code = mm.group(1) if mm else ""
                s = self.slots.get(f)
                if s is None:
                    hdr = rsvi_header(os.path.join(vehicle_dir, "meshes", f))
                    s = self.slots[f] = {"file": f, "nodes": [], "material": mesh.materialReference,
                                         "code": code, "matrix": M, "node": node.name, **hdr}
                s["nodes"].append(node.name)
        self.materials = {m.name: m for m in self.scene.materialLibrary.material}

    def refresh(self):
        """Recompute node matrices and slot frames from the (possibly edited) scene, so a mesh written after a
        pivot moved lands in the new frame."""
        for node, M in walk(self.scene.root):
            self.nodes[node.name] = (node, M)
        for s in self.slots.values():
            s["matrix"] = self.nodes[s["node"]][1]

    def slot(self, key):
        """Slot by file name or by a unique substring of it."""
        if key in self.slots:
            return self.slots[key]
        hits = [f for f in self.slots if key in f]
        if len(hits) != 1:
            raise KeyError(f"{key}: {hits}")
        return self.slots[hits[0]]

    def biggest_slot(self):
        """The slot with the most triangles — a good, carve-agnostic 'like' template (usually the body)."""
        return max(self.slots.values(), key=lambda s: s["numTriangles"])
