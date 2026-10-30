"""A small expression language for widget.pbw (HmiWidget TDataBinding trees), written as Python.

    from capabilities.vehicle_models.tools import widget_expr as E   # E.P, E.R, E.C, E.sin, E.vec3 …
    theta = R("LOCO_theta_MDL.output")               # a named expression (internalModelValue)
    x = C(12.5) * cos(theta) + P("FESStaging") * 3   # a parameter (externalModelValue), constants, operators
    ctx.define("ROD_x", x); ctx.bind(node, translate=vec3(x, 0, 0))

Every node knows its data type (Float, Vec3 or Bool), so each operation lists one TEDataType per operand, as
BMW's exporter writes them (Mul(Float, Vec3) is scalar times vector; comparisons give Bool; IfThenElse takes
Bool, Float, Float). Constants fold. `msg()` returns the protobuf (parsed from protobuf text, so the curve
extension `[HmiWidget.curve]` works), `evaluate()` computes a value in Python for given parameters, curves and
named expressions, the same way the viewer does, so the build can check what it wrote.

Operators that BMW's own cars use: Add Mul Equal Less Greater GreaterEqual IfThenElse Clamp MuxVec3 Mix
RemapValue Pow. Sub Div Neg Sin Cos are in TEOperatorType too; whether HmiMain3D implements Sin/Cos (and with
radians) is checked separately; `TRIG` says whether this build may use them.
"""
import math

import numpy as np

TRIG = True                   # set False to forbid Sin/Cos (they raise), e.g. if the HU turns out not to have them

_OPS = {"Neg": 1, "Abs": 3, "Add": 6, "Sub": 7, "Mul": 8, "Div": 9, "Min": 10, "Max": 11, "Equal": 12,
        "NotEqual": 13, "Less": 14, "Greater": 15, "LessEqual": 16, "GreaterEqual": 17, "IfThenElse": 18,
        "Clamp": 19, "MuxVec3": 21, "Mix": 28, "Pow": 32, "Sin": 37, "Cos": 38}
_BOOL_OPS = {"Equal", "NotEqual", "Less", "Greater", "LessEqual", "GreaterEqual"}


def _fmt(v):
    r = repr(float(v))
    return r[:-2] if r.endswith(".0") else r


class X:
    """An expression node. kind: 'param' | 'ref' | 'const' | 'curve' | 'anim' | 'op'. An 'anim' node reads a
    composite animation's return value (name = compositeIdentifier, value = the returnValue key), see anim()."""

    def __init__(self, kind, dtype, name=None, value=None, op=None, args=()):
        self.kind, self.dtype, self.name, self.value, self.op, self.args = kind, dtype, name, value, op, tuple(args)

    # ---- operators ----
    def __add__(self, o): return _arith("Add", self, o)
    def __radd__(self, o): return _arith("Add", o, self)
    def __sub__(self, o): return _arith("Sub", self, o)
    def __rsub__(self, o): return _arith("Sub", o, self)
    def __mul__(self, o): return _arith("Mul", self, o)
    def __rmul__(self, o): return _arith("Mul", o, self)
    def __truediv__(self, o): return _arith("Div", self, o)
    def __neg__(self): return _arith("Mul", self, -1.0)
    def __gt__(self, o): return op("Greater", self, o)
    def __lt__(self, o): return op("Less", self, o)
    def __ge__(self, o): return op("GreaterEqual", self, o)
    def __le__(self, o): return op("LessEqual", self, o)

    # ---- output ----
    def text(self, indent=0):
        """Protobuf text of this node as a TDataBinding body."""
        s = " " * indent
        if self.kind == "param":
            return f'{s}key {{ valueString: "{self.name}" }}\n{s}provider {{ source: TEProviderSource_ExtModelValue }}\n'
        if self.kind == "ref":
            return f'{s}key {{ valueString: "{self.name}" }}\n{s}provider {{ source: TEProviderSource_IntModelValue }}\n'
        if self.kind == "curve":
            return f'{s}provider {{ [HmiWidget.curve] {{ curveReference {{ valueString: "{self.name}" }} }} }}\n'
        if self.kind == "anim":
            return (f'{s}key {{ valueString: "{self.value}" }}\n'
                    f'{s}provider {{ [HmiWidget.animation] {{ valueString: "{self.name}" }} }}\n')
        if self.kind == "const":
            if self.dtype == "Bool":
                return f'{s}provider {{ variant {{ Bool: {"true" if self.value else "false"} }} }}\n'
            if self.dtype == "Vec3":
                x, y, z = (_fmt(v) for v in self.value)
                return f'{s}provider {{ variant {{ Numeric {{ Vec3f {{ x: {x} y: {y} z: {z} }} }} }} }}\n'
            return f'{s}provider {{ variant {{ Numeric {{ Float: {_fmt(self.value)} }} }} }}\n'
        out = f"{s}provider {{\n{s} operation {{\n{s}  operator: TEOperatorType_{self.op}\n"
        for a in self.args:
            out += f"{s}  dataType: TEDataType_{a.dtype}\n"
        for a in self.args:
            out += f"{s}  operand {{\n{a.text(indent + 3)}{s}  }}\n"
        return out + f"{s} }}\n{s}}}\n"

    def msg(self):
        """The TDataBinding protobuf message."""
        from google.protobuf import text_format
        from ..packager.hmi import proto, pool
        m = proto("TDataBinding")()
        text_format.Parse(self.text(), m, descriptor_pool=pool())
        return m

    def evaluate(self, params=None, refs=None, curves=None):
        """Value in Python. params: {name: value}; refs: {name: X or value}; curves: {name: callable(domain)}.
        An animation value is read from params["anim:<compositeIdentifier>.<key>"] (0 when absent)."""
        params, refs, curves = params or {}, refs or {}, curves or {}
        k = self.kind
        if k == "const":
            return np.array(self.value, float) if self.dtype == "Vec3" else self.value
        if k == "param":
            return params[self.name]
        if k == "anim":
            return params.get(f"anim:{self.name}.{self.value}", 0.0)
        if k == "ref":
            r = refs[self.name]
            return r.evaluate(params, refs, curves) if isinstance(r, X) else r
        if k == "curve":
            return curves[self.name]()
        v = [a.evaluate(params, refs, curves) for a in self.args]
        f = {"Add": lambda: sum(v[1:], v[0]), "Sub": lambda: v[0] - v[1], "Mul": lambda: _prod(v),
             "Div": lambda: v[0] / v[1] if np.all(v[1]) else 0.0, "Neg": lambda: -v[0], "Abs": lambda: abs(v[0]),
             "Min": lambda: np.minimum(v[0], v[1]), "Max": lambda: np.maximum(v[0], v[1]),
             "Equal": lambda: v[0] == v[1], "NotEqual": lambda: v[0] != v[1], "Less": lambda: v[0] < v[1],
             "Greater": lambda: v[0] > v[1], "LessEqual": lambda: v[0] <= v[1],
             "GreaterEqual": lambda: v[0] >= v[1], "IfThenElse": lambda: v[1] if v[0] else v[2],
             "Clamp": lambda: np.clip(v[0], v[1], v[2]), "MuxVec3": lambda: np.array(v, float),
             "Mix": lambda: v[0] + (v[1] - v[0]) * v[2], "Pow": lambda: np.power(v[0], v[1]),
             "Sin": lambda: np.sin(v[0]), "Cos": lambda: np.cos(v[0])}[self.op]
        return f()

    def __repr__(self):
        if self.kind == "const":
            return _fmt(self.value) if self.dtype != "Vec3" else f"vec3({', '.join(_fmt(a) for a in self.value)})"
        if self.kind in ("param", "ref"):
            return ("$" if self.kind == "param" else "@") + self.name
        if self.kind == "curve":
            return f"curve({self.name})"
        if self.kind == "anim":
            return f"anim({self.name}.{self.value})"
        sym ={"Add": "+", "Sub": "-", "Mul": "*", "Div": "/"}.get(self.op)
        if sym:
            return "(" + f" {sym} ".join(map(repr, self.args)) + ")"
        return f"{self.op.lower()}({', '.join(map(repr, self.args))})"


def _prod(v):
    r = v[0]
    for x in v[1:]:
        r = r * x
    return r


def C(v):
    """A constant: number, bool or 3-vector."""
    if isinstance(v, X):
        return v
    if isinstance(v, bool):
        return X("const", "Bool", value=v)
    if np.ndim(v) == 1:
        return X("const", "Vec3", value=tuple(float(a) for a in v))
    return X("const", "Float", value=float(v))


def P(name, dtype="Float"):
    """A parameter the HMI sets (externalModelValue)."""
    return X("param", dtype, name=name)


def R(name, dtype="Float"):
    """A named expression (internalModelValue), e.g. 'WHEELSLEFT_rotation_PMA.output3Dx'."""
    return X("ref", dtype, name=name)


def curve(name):
    """The value of a widget curve at its own sample position."""
    return X("curve", "Float", name=name)


def anim(name, key="phase"):
    """A composite animation's current value (TDataProvider extension [HmiWidget.animation], the binding's key =
    the returnValue key), e.g. the 0->1 sawtooth of a looping clock from ctx.add_clock()."""
    return X("anim", "Float", name=name, value=key)


def op(name, *args):
    args = [C(a) for a in args]
    if name not in _OPS:
        raise ValueError(name)
    if name in ("Sin", "Cos") and not TRIG:
        raise ValueError(f"{name}: trigonometric operators are disabled (sd.expr.TRIG)")
    if name in _BOOL_OPS:
        dtype = "Bool"
    elif name == "MuxVec3":
        dtype = "Vec3"
    elif name == "IfThenElse":
        dtype = args[1].dtype
    else:
        dtype = "Vec3" if any(a.dtype == "Vec3" for a in args) else "Float"
    return X("op", dtype, op=name, args=args)


def _arith(name, a, b):
    a, b = C(a), C(b)
    if a.kind == "const" and b.kind == "const" and "Vec3" not in (a.dtype, b.dtype):
        return C({"Add": lambda: a.value + b.value, "Sub": lambda: a.value - b.value,
                  "Mul": lambda: a.value * b.value, "Div": lambda: a.value / b.value}[name]())
    if name == "Add":
        if b.kind == "const" and b.dtype == "Float" and b.value == 0:
            return a
        if a.kind == "const" and a.dtype == "Float" and a.value == 0:
            return b
    if name == "Sub" and b.kind == "const" and b.dtype == "Float" and b.value == 0:
        return a
    if name == "Mul":
        for k, o in ((a, b), (b, a)):
            if k.kind == "const" and k.dtype == "Float":
                if k.value == 1:
                    return o
                if k.value == 0 and o.dtype == "Float":
                    return C(0.0)
    return op(name, a, b)


def sin(x): return op("Sin", x)
def cos(x): return op("Cos", x)
def vec3(x, y, z): return op("MuxVec3", x, y, z)
def clamp(x, lo, hi): return op("Clamp", x, lo, hi)
def mix(a, b, t): return op("Mix", a, b, t)
def if_(c, a, b): return op("IfThenElse", c, a, b)
def pow_(a, b): return op("Pow", a, b)
def min_(a, b): return op("Min", a, b)
def max_(a, b): return op("Max", a, b)


def fourier(theta, c0, a, b):
    """c0 + sum_k a[k-1] cos(k theta) + b[k-1] sin(k theta), theta in radians; tiny terms dropped."""
    out = C(c0)
    for k, (ak, bk) in enumerate(zip(a, b), start=1):
        t = theta if k == 1 else theta * k
        if abs(ak) > 1e-6:
            out = out + C(ak) * cos(t)
        if abs(bk) > 1e-6:
            out = out + C(bk) * sin(t)
    return out


def hermite_keys(points):
    """Curve points [(domain, value, slope_in, slope_out)] -> TCurveDefinition text, BMW's encoding: each tangent
    vector is (slope x gap, gap) with gap = the distance to the neighbouring key on that side."""
    out = "curveValueType: TENumericType_float\n"
    for i, (d, v, si, so) in enumerate(points):
        gi = d - points[i - 1][0] if i else 0.0
        go = points[i + 1][0] - d if i + 1 < len(points) else 0.0
        out += (f"point {{ point {{ value {{ Float: {_fmt(v)} }} domain: {_fmt(d)} }}\n"
                f"  incommingInterpolation {{ interpolation: TCurvePointInterpolationType_Hermite "
                f"tangentVector {{ value {{ Float: {_fmt(si * gi)} }} domain: {_fmt(gi)} }} }}\n"
                f"  outgoingInterpolation {{ interpolation: TCurvePointInterpolationType_Hermite "
                f"tangentVector {{ value {{ Float: {_fmt(so * go)} }} domain: {_fmt(go)} }} }} }}\n")
    return out


DEG = 180.0 / math.pi
