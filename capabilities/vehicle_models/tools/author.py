"""Author a custom car by mutating a copy of a stock series' ``vehicle/`` folder.

``Car(template_dir, out_dir)`` copies a stock ``vehicle/`` (from your own HMI tree) and gives you an API to
*add to it*: your own meshes, materials and bitmaps, plus the widget bindings/curves/clocks that animate them.
Every stock node, material, parameter and binding is kept, so the HMI still finds everything it sets — your
content hangs beside it. Write the result with ``Car.save()``, then package the series folder with
``packager/package.py``.

Frames: meshes are built in the CAD frame (cm; x = rear, y = right, z = up). Rotations are degrees, Maya XYZ.

This is the reverse-engineered authoring layer. The schema (``packager/hmi_descriptors.bin``) and its loader
ship with the toolkit; the stock template is yours (see ``packager/hmi.py``). Nothing BMW-derived is shipped.
"""
import hashlib
import os
import shutil

import numpy as np

from ..packager import hmi
from . import widget_expr as E
from .mesh import fill_layout, write_slot
from .rsvi import write_rsvi_arrays
from .scene_template import Template


def mesh_file_name(name):
    """BMW's mesh file pattern <16 hex upper><NAME>Shape. The HMI resolves meshes through the asset index, not
    the name, so the hex prefix is just sha1(name)[:16] — unique and stable."""
    return hashlib.sha1(name.encode()).hexdigest()[:16].upper() + name + "Shape"


class Car:
    def __init__(self, template_dir, out_series, root=None):
        """template_dir: a stock series folder (holds vehicle/ + camera_crane/). out_series: where the copy +
        your edits land. root: an optional own root node path to hang your nodes under (else use existing nodes)."""
        if os.path.abspath(template_dir) == os.path.abspath(out_series):
            raise ValueError("out_series must differ from template_dir")
        if os.path.exists(out_series):
            shutil.rmtree(out_series)
        shutil.copytree(template_dir, out_series)
        self.out = out_series
        self.vehicle = os.path.join(out_series, "vehicle")
        self.tmpl = Template(self.vehicle)
        self.scene = self.tmpl.scene
        TW = hmi.proto("HmiWidget.TWidgetCollection")
        self.widget = TW.FromString(open(os.path.join(self.vehicle, "widget.pbw"), "rb").read())
        self.W = self.widget.widget[0]
        self.paths = {}
        for path in self.tmpl.nodes:
            self.paths.setdefault(path.rsplit("|", 1)[-1], path)
        self.defined = {im.key.valueString for im in self.W.internalModelValue}
        self.curves = {c.curveIdentifier.valueString for c in self.W.curve}
        self.added = {}
        if root:
            self.add_node(*root.rsplit("|", 1))

    # ---- lookup ----
    def path(self, p):
        if "|" in p:
            return p
        if p not in self.paths:
            raise KeyError(f"no node named {p}")
        return self.paths[p]

    def node(self, path):
        self.tmpl.refresh()
        return self.tmpl.nodes[self.path(path)][0]

    def matrix(self, path):
        self.tmpl.refresh()
        return self.tmpl.nodes[self.path(path)][1]

    def _children(self, path):
        """The repeated 'child' list [path]'s new children go into (a node's own, or a render layer's base)."""
        path = self.path(path)
        hit = []

        def walk(n, layer_base=False):
            if n.name == path and not layer_base:
                hit.append(n.child)
            for c in n.child:
                walk(c)
            for rl in n.renderLayer:
                if rl.baseNode.name == path:
                    hit.append(rl.child)
                walk(rl.baseNode, True)
                for c in rl.child:
                    walk(c)
        walk(self.scene.root)
        if len(hit) != 1:
            raise KeyError(f"{path}: {len(hit)} child-list matches")
        return hit[0]

    # ---- scene: nodes, meshes, materials, bitmaps ----
    def _new_node(self, path, T=(0, 0, 0), R=(0, 0, 0), S=(1, 1, 1)):
        n = hmi.proto("HmiScenegraph.TNode")()
        n.name, n.renderOrder, n.childSortOrderRank = path, 0, 0
        n.scale.x, n.scale.y, n.scale.z = (float(v) for v in S)
        n.rotation.x, n.rotation.y, n.rotation.z = (float(v) for v in R)
        n.translation.x, n.translation.y, n.translation.z = (float(v) for v in T)
        return n

    def add_node(self, parent, name, T=(0, 0, 0), R=(0, 0, 0), S=(1, 1, 1)):
        """A transform node (a pivot) under [parent]; returns its full path. Bind its rotation/translation later
        to animate everything beneath it (wheels, doors, a beacon)."""
        parent = self.path(parent)
        path = f"{parent}|{name}"
        if name in self.paths and self.paths[name] != path:
            raise ValueError(f"node name {name} already used at {self.paths[name]}")
        if path in self.tmpl.nodes:
            raise ValueError(f"{path} exists")
        self._children(parent).append(self._new_node(path, T, R, S))
        self.paths[name] = path
        self.tmpl.refresh()
        self.added[path] = ("node",)
        return path

    def _mesh_template(self, like):
        """(TMesh, element layout) of a stock slot/node, to copy material + uniforms + vertex layout from."""
        try:
            slot = self.tmpl.slot(like)
            node = self.tmpl.nodes[slot["node"]][0]
            return node.mesh[0], slot["elements"]
        except KeyError:
            node = self.node(like)
            f = os.path.basename(node.mesh[0].meshResource)[:-4] + ".rsvi"
            return node.mesh[0], self.tmpl.slots[f]["elements"]

    def add_mesh(self, parent, name, mesh, like, material=None, uniforms=None):
        """A mesh node [name] under [parent] drawing your geometry [mesh]. [like]: a stock slot/node whose TMesh
        (material, uniforms, vertex layout) to copy; [material]: a material name to use instead; [uniforms]:
        {name: value} overriding copied uniforms. Writes the .rsvi under meshes/. Returns the node path."""
        if mesh is None or len(mesh) == 0:
            raise ValueError(f"{name}: empty mesh")
        tm, elements = self._mesh_template(like)
        path = self.add_node(parent, name)
        node = self.node(path)
        m = node.mesh.add()
        m.CopyFrom(tm)
        base = name + "Shape"
        m.baseNode.CopyFrom(self._new_node(f"{path}|{base}"))
        fname = mesh_file_name(name)
        m.meshResource = f"meshes/{fname}.ctm"            # on-device name; the .rsvi is the source form
        if material:
            if material not in {x.name for x in self.scene.materialLibrary.material}:
                raise KeyError(material)
            m.materialReference = material
        for k, v in (uniforms or {}).items():
            u = [x for x in m.uniform if x.name == k]
            if not u:
                raise KeyError(f"{name}: uniform {k} not on {like}")
            val = u[0].value
            if val.HasField("Float"):
                val.Float = float(v)
            elif val.HasField("Vec3f"):
                val.Vec3f.x, val.Vec3f.y, val.Vec3f.z = (float(a) for a in v)
            elif val.HasField("Vec4f"):
                val.Vec4f.x, val.Vec4f.y, val.Vec4f.z, val.Vec4f.w = (float(a) for a in v)
        local_m = np.linalg.inv(self.matrix(path))
        write_slot(os.path.join(self.vehicle, "meshes", fname + ".rsvi"),
                   mesh, self.matrix(path), elements)
        self.paths[base] = f"{path}|{base}"
        self.added[path] = ("mesh", len(mesh.P), len(mesh.I), m.materialReference)
        return path

    def add_material(self, name, like, **render):
        """A copy of stock material [like], renamed [name]; render: renderMode fields to set (e.g.
        depthWrite=False, culling='TEFace_None', or blending={...}). Recolour by overriding a uniform on the
        meshes that use it (add_mesh(..., uniforms={...}))."""
        lib = self.scene.materialLibrary
        src = [m for m in lib.material if m.name == like]
        if len(src) != 1:
            raise KeyError(like)
        m = lib.material.add()
        m.CopyFrom(src[0])
        m.name = name
        for k, v in render.items():
            if k == "blending":
                for bk, bv in v.items():
                    setattr(m.renderMode.blending, bk, bv)
            else:
                setattr(m.renderMode, k, v)
        self.added[name] = ("material",)
        return name

    def blank_stock_meshes(self, keep=()):
        """Replace every stock mesh with a 1 mm placeholder (so only YOUR car shows), keeping the nodes,
        materials and all widget bindings valid. [keep]: file-name substrings to leave intact (e.g. a ground
        shadow). Call this before adding your own meshes if you want a clean replacement rather than an overlay."""
        from .mesh import tiny
        self.tmpl.refresh()
        for f, slot in self.tmpl.slots.items():
            if any(k in f for k in keep):
                continue
            write_slot(os.path.join(self.vehicle, "meshes", f), tiny(slot["matrix"][:3, 3]),
                       slot["matrix"], slot["elements"])

    # ---- widget: expressions, curves, bindings, clocks ----
    def define(self, name, x):
        """A named internal expression (reuse it with E.R(name))."""
        if name in self.defined:
            raise ValueError(f"expression {name} exists")
        im = self.W.internalModelValue.add()
        im.key.valueString = name
        im.binding.CopyFrom(E.C(x).msg())
        self.defined.add(name)
        return E.R(name, E.C(x).dtype)

    def add_curve(self, name, sample, points):
        """A Hermite curve sampled at expression [sample]; points = [(domain, value, slope_in, slope_out)].
        Returns E.curve(name)."""
        from google.protobuf import text_format
        if name in self.curves:
            raise ValueError(f"curve {name} exists")
        c = self.W.curve.add()
        c.curveIdentifier.valueString = name
        c.samplePosition.CopyFrom(E.C(sample).msg())
        text_format.Parse(E.hermite_keys(points), c.curveDefinition, descriptor_pool=hmi.pool())
        self.curves.add(name)
        return E.curve(name)

    def bind(self, path, translate=None, rotate=None, scale=None, visible=None, uniforms=None):
        """Drive a node's transform/visibility (or a mesh uniform) from expressions. translate/rotate/scale:
        an E expression (usually E.vec3(...)); visible: a Bool expression; uniforms: {name: expr}."""
        path = self.path(path)
        if uniforms:
            node = self.node(path)
            if node.mesh:
                path = node.mesh[0].baseNode.name
        np_ = self.W.nodeParam.add()
        np_.identifier.valueString = path
        np_.node.provider.variant.AsciiString = path
        for field, x in (("translation", translate), ("rotation", rotate), ("scale", scale)):
            if x is not None:
                getattr(np_.transform, field).CopyFrom(E.C(x).msg())
        if visible is not None:
            np_.nodeProperties.visible.CopyFrom(E.C(visible).msg())
        for k, x in (uniforms or {}).items():
            u = np_.uniform.add()
            u.name.provider.variant.AsciiString = k
            u.value.CopyFrom(E.C(x).msg())
        return np_

    def add_clock(self, name, duration_ms, run_param=None, kick=None):
        """A free-running clock: a composite animation returning "phase", a 0->1 sawtooth over [duration_ms]
        that loops forever. Returns E.anim(name) (the phase, 0 until it runs). Use sin/cos of phase*2π for a
        continuous idle animation (a blinking beacon, drifting steam). A conditional trigger on the Bool
        [run_param] (default <name>Run, default true) starts/stops it; [kick] (default FESStaging>0.5) re-starts
        it as a load-time fallback. Mirrors BMW's own WheelRotation clock pattern."""
        from google.protobuf import text_format
        run = run_param or name + "Run"
        if any(c.compositeIdentifier.valueString == name for c in self.W.compositeAnimation):
            raise ValueError(f"clock {name} exists")
        text = ""
        if run not in {p.key.valueString for p in self.W.externalModelValue}:
            text += f'externalModelValue {{ key {{ valueString: "{run}" }} variant {{ Bool: true }} }}\n'
        text += (
            f'compositeAnimation {{ compositeIdentifier {{ valueString: "{name}" }}\n'
            f'  returnValue {{ key {{ valueString: "phase" }}\n'
            f'    animation {{ identifier {{ valueString: "saw" }}\n'
            f'      widgetAnimation {{ startValue {{ Float: 0 }} endValue {{ Float: 1 }} '
            f'durationValue: {int(duration_ms)} interpolator: TEAnimationInterpolator_Linear '
            f'returnType: TEDataType_Float loopCount: 0 }}\n'
            f'      trigger {{ action: TEAnimationSlot_SlotAnimationStart }} }}\n'
            f'    returnType: TEDataType_Float defaultValue {{ Numeric {{ Float: 0 }} }} }} }}\n')

        def command(action):
            return f'animationTrigger {{ animation {{ valueString: "{name}" }} action: TEAnimationAction_{action} }}'
        text += (f'trigger {{ identifier {{ valueString: "{run}" }} conditionalTrigger {{\n'
                 f'  condition {{ key {{ valueString: "{run}" }} provider {{ source: TEProviderSource_ExtModelValue }} }}\n'
                 f'  command {{ {command("Start")} }} elseCommand {{ {command("Stop")} }} }} }}\n')
        if kick is None:
            kick = E.P("FESStaging") > 0.5
        if kick is not False:
            text += (f'trigger {{ identifier {{ valueString: "{name}Kick" }} conditionalTrigger {{\n'
                     f'  condition {{\n{E.C(kick).text(4)}  }}\n  command {{ {command("Start")} }} }} }}\n')
        text_format.Merge(text, self.W, descriptor_pool=hmi.pool())
        self.added[name] = ("clock",)
        return E.anim(name, "phase")

    # ---- output ----
    def save(self):
        """Write the edited scene.pbx + widget.pbw back into the series folder. Byte-deterministic."""
        open(os.path.join(self.vehicle, "scene.pbx"), "wb").write(
            self.scene.SerializeToString(deterministic=True))
        open(os.path.join(self.vehicle, "widget.pbw"), "wb").write(
            self.widget.SerializeToString(deterministic=True))
        return self.out
