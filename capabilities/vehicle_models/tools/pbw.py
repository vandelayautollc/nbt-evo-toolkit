#!/usr/bin/env python3
"""
.pbw: the NBT-Evo HMI's widget definition (protobuf, hand-decoded). For a 3D model widget (…/vehicles/<series>/vehicle/,
…/camera_crane/) it is a Maya dependency graph exported as data: the parameters the HMI sets, the utility nodes
between them (multDoubleLinear, plusMinusAverage, condition, remapValue, …) as expressions, the animation curves, and
the bindings that drive scene.pbx node transforms, visibility and shader uniforms from them.

The real schema (HmiWidget.TWidgetCollection, embedded in HmiMain3D) is recovered by emulator/tools/hmi_pack.py;
`protoc --decode`/`--encode` with emulator/data/hmi_descriptors.bin round-trips the F30 vehicle and camera widgets
byte-for-byte, so author widgets as protobuf text. This module reads by field number:

TWidgetCollection: 1 widget[] TWidget {
   4  externalModelValue[]  {1 key {2 name}, 2 TVariant}      the parameters the HMI sets, with defaults:
                            TVariant {1 Bool | 2 AsciiString | 5 Numeric {3 Float | 5 Vec3f | 6 Vec4f}}
   5  internalModelValue[]  {1 key, 2 TDataBinding}            named utility-node outputs ("L1DOOR_MDL.output")
   7  nodeParam[]           {1 identifier {2 node path}, 3 transform {1 scale, 2 rotation°, 3 translation},
                             4 uniform[] {1 name, 2 value}, 6 renderLayerProperties {1 renderPassEnabled},
                             7 nodeProperties {1 visible, 2 renderOrderRank, 6 material, …}}
  12  compositeAnimation[]  {1 compositeIdentifier {2 name}, 4 returnValue[] {1 key {2 name}, 2 animation[]
                             {1 identifier, 2 widgetAnimation {1 startValue {3 Float}, 3 endValue, 5 durationValue
                             (ms), 8 interpolator, 9 returnType, 10 loopCount (0/-1 = forever)}, 4 trigger}, 3 returnType,
                             4 defaultValue}}          a clock/tween; 13 trigger[] starts and stops it
  19  curve[]               {1 curveIdentifier, 2 samplePosition (TDataBinding), 3 curveDefinition {1 type,
                             2 point[] {1 point {1 value, 2 domain}, 2 incoming, 3 outgoing interpolation
                             {1 type 0 Step / 1 Linear / 2 Hermite, 2 tangentVector {1 Δvalue, 2 Δdomain}}}}}
}
TDataBinding = {1 key {2 name}, 2 TDataProvider}; TDataProvider = {1 variant (a constant) | 4 source
(TEProviderSource 0 ExtModelValue = a parameter, 1 IntModelValue = a named expression) | 5 operation
{1 operator, 2 dataType[], 3 operand[] (TDataBinding)} | 11 animation {2 compositeIdentifier} (the binding's key
names the returnValue) | 12 curve reference {1 {2 curve name}}}.
TEDataType: 2 Float, 5 Vec3, 11 Bool. TEOperatorType (all of it; the F30 uses the starred ones):
  0 Not 1 Neg 2 Inv 3 Abs 4 And 5 Or 6 Add* 7 Sub 8 Mul* 9 Div 10 Min 11 Max 12 Equal* 13 NotEqual 14 Less*
  15 Greater* 16 LessEqual 17 GreaterEqual* 18 IfThenElse* 19 Clamp* 20 MuxVec2 21 MuxVec3* 22 MuxVec4
  23 ColorFade 24 NormalizeInRange 25 isRessourceValid 26 IsEmpty 27 MuxAlignment 28 Mix* 29 Step 30 SmoothStep
  31 RemapValue* 32 Pow* 33 Switch 34 LogBaseE 35 Convert 36 DebugOutput 37 Sin 38 Cos 39 Tan 40 XOr 41 DemuxVec
In this file's JSON an expression is {"p": parameter} | {"e": named expression} | {"c": constant} |
{"op": operator, "t": dataTypes, "a": operands} | {"curve": name} | {"anim": compositeIdentifier, "key": returnValue};
a curve key is [domain, value, inType, inDvalue, inDdomain, outType, outDvalue, outDdomain]; "anims" lists the
composite animations as {name: {key: {"start", "end", "duration_ms", "loop"}}} (first sub-animation of each return
value); evaluate() reads an animation's value from params["anim:<name>.<key>"] (0 by default), the viewer from the
wall clock (a looping linear tween = a sawtooth from start to end every duration_ms).

Usage:  pbw.py json <widget.pbw> [out.json]    params, expressions, curves and bindings as JSON (exprs as small ASTs)
        pbw.py text <widget.pbw>               the same, as readable formulas
"""
import json, struct, sys

OPS = {6: "+", 7: "-", 8: "*", 9: "/", 12: "==", 13: "!=", 14: "<", 15: ">", 16: "<=", 17: ">=", 18: "if",
       19: "clamp", 21: "vec3", 28: "mix", 31: "remap", 32: "pow"}


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
        if fn == 0:
            raise ValueError("field 0")
        if wt == 0:
            v, i = _varint(b, i); out.append((fn, v))
        elif wt == 2:
            n, i = _varint(b, i)
            if i + n > hi:
                raise ValueError("overrun")
            out.append((fn, (i, i + n))); i += n
        elif wt == 5:
            out.append((fn, struct.unpack_from("<f", b, i)[0])); i += 4
        elif wt == 1:
            out.append((fn, struct.unpack_from("<d", b, i)[0])); i += 8
        else:
            raise ValueError("wire type %d" % wt)
    return out


class Msg:
    """One protobuf message: fields by number, nested messages decoded on demand."""

    def __init__(self, b, lo, hi):
        self.b, self.f = b, _fields(b, lo, hi)

    def all(self, fn):
        return [v for f, v in self.f if f == fn]

    def get(self, fn):
        v = self.all(fn)
        return v[0] if v else None

    def msg(self, fn):
        v = self.get(fn)
        return Msg(self.b, *v) if isinstance(v, tuple) else None

    def msgs(self, fn):
        return [Msg(self.b, *v) for v in self.all(fn) if isinstance(v, tuple)]

    def str(self, fn):
        v = self.get(fn)
        return self.b[v[0]:v[1]].decode("latin1") if isinstance(v, tuple) else None


def value(m):
    """A parameter or constant value: float, [x, y, z(, w)], bool as 0/1, or a string."""
    t = m.msg(5)
    if t is not None:
        if t.get(3) is not None:
            return t.get(3)
        for fn, n in ((5, 3), (6, 4)):
            v = t.msg(fn)
            if v is not None:
                return [v.get(k) or 0.0 for k in range(1, n + 1)]
        return 0.0
    if m.get(1) is not None and not isinstance(m.get(1), tuple):
        return float(m.get(1))
    for fn in (2, 10):
        if isinstance(m.get(fn), tuple):
            return m.str(fn)
    return None


def expr(m):
    """Expression message -> AST: {"p": param} | {"e": expression} | {"c": value} | {"op", "t", "a"} | {"curve"} |
    {"anim", "key"}."""
    an = m.msg(2).msg(11) if m.msg(2) else None
    if an is not None:                           # composite animation value: key = its returnValue
        return {"anim": an.str(2), "key": m.msg(1).str(2) if m.msg(1) else None}
    ref = m.msg(1)
    if ref is not None and ref.str(2) is not None:
        kind = (m.msg(2).get(4) if m.msg(2) else 0) or 0
        return {"e" if kind == 1 else "p": ref.str(2)}
    body = m.msg(2)
    if body is None:
        raise ValueError("empty expression")
    if body.msg(1) is not None:
        return {"c": value(body.msg(1))}
    op = body.msg(5)
    if op is not None:
        return {"op": op.get(1), "t": op.all(2), "a": [expr(a) for a in op.msgs(3)]}
    cu = body.msg(12)
    if cu is not None:
        return {"curve": cu.msg(1).str(2)}
    raise ValueError("unknown expression form")


def read_widget(path):
    """A widget.pbw (path, or its bytes) -> {"params", "exprs", "curves", "bindings", "anims"}."""
    b = bytes(path) if isinstance(path, (bytes, bytearray)) else open(path, "rb").read()
    w = Msg(b, 0, len(b)).msg(1)
    out = {"params": {}, "exprs": {}, "curves": {}, "bindings": [], "anims": {}}
    for p in w.msgs(4):
        name = p.msg(1).str(2)
        if name and not name.startswith("eParam_") and name != "WidgetNameHint":
            out["params"][name] = value(p.msg(2))
    for e in w.msgs(5):
        out["exprs"][e.msg(1).str(2)] = expr(e.msg(2))
    for c in w.msgs(19):
        keys = []
        for k in c.msg(3).msgs(2):
            kv = k.msg(1)
            row = [kv.get(2) or 0.0, value(kv) if kv.msg(5) else 0.0]
            if kv.msg(1) is not None:                 # {1 {3 value}} rather than {5 …}
                row[1] = kv.msg(1).get(3) or 0.0
            for tn in (2, 3):
                t = k.msg(tn)
                d = t.msg(2) if t else None
                row += [t.get(1) if t else 0, (d.msg(1).get(3) or 0.0) if d and d.msg(1) else 0.0,
                        (d.get(2) or 0.0) if d else 0.0]
            keys.append(row)                          # [time, value, inType, inDv, inDt, outType, outDv, outDt]
        out["curves"][c.msg(1).str(2)] = {"input": expr(c.msg(2)), "keys": keys}
    for ca in w.msgs(12):                             # composite animations (clocks, tweens)
        rets = {}
        for rv in ca.msgs(4):
            sub = rv.msg(2)
            wa = sub.msg(2) if sub is not None else None
            if wa is None:
                continue
            num = lambda fn: (wa.msg(fn).get(3) or 0.0) if wa.msg(fn) is not None else 0.0  # noqa: E731
            loop = wa.get(10) or 0
            if loop >= 1 << 63:                       # int32 -1 is a 10-byte varint
                loop -= 1 << 64
            rets[rv.msg(1).str(2)] = {"start": num(1), "end": num(3), "duration_ms": wa.get(5) or 0, "loop": loop}
        out["anims"][ca.msg(1).str(2)] = rets
    for bnd in w.msgs(7):
        d = {"node": bnd.msg(1).str(2)}
        xf = bnd.msg(3)
        if xf:
            for fn, key in ((1, "scale"), (2, "rotate"), (3, "translate")):
                if xf.msg(fn):
                    d[key] = expr(xf.msg(fn))
        for fn, key in ((6, "layer"), (7, "visible")):
            if bnd.msg(fn):
                d[key] = expr(bnd.msg(fn).msg(1))
        uni = {}
        for u in bnd.msgs(4):
            uni[u.msg(1).msg(2).msg(1).str(2)] = expr(u.msg(2))
        if uni:
            d["uniforms"] = uni
        out["bindings"].append(d)
    return out


def _curve_at(c, t):
    """Step/Linear/Hermite by the left key's outgoing type; a Hermite tangent is (value Δ, domain Δ), so its slope is
    Δv/Δt. Clamped outside the keys."""
    k = c["keys"]
    if not k:
        return 0.0
    if t <= k[0][0]:
        return k[0][1]
    for a, b in zip(k, k[1:]):
        if t <= b[0]:
            span = b[0] - a[0]
            if span <= 0:
                return b[1]
            s = (t - a[0]) / span
            if a[5] == 0:
                return a[1]
            if a[5] == 1:
                return a[1] + (b[1] - a[1]) * s
            m0 = (a[6] / a[7] if a[7] else 0.0) * span
            m1 = (b[3] / b[4] if b[4] else 0.0) * span
            s2, s3 = s * s, s * s * s
            return ((2 * s3 - 3 * s2 + 1) * a[1] + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * b[1]
                    + (s3 - s2) * m1)
    return k[-1][1]


def evaluate(w, params=None):
    """An evaluator over widget [w] with [params] overriding the defaults: returns ev(ast) -> float | list."""
    env = dict(w["params"]); env.update(params or {})
    memo = {}

    def lift(f, *xs):
        if any(isinstance(x, list) for x in xs):
            n = max(len(x) for x in xs if isinstance(x, list))
            return [f(*[x[i] if isinstance(x, list) else x for x in xs]) for i in range(n)]
        return f(*xs)

    def ev(a):
        if "p" in a:
            v = env.get(a["p"], 0.0)
            return v if isinstance(v, (list, float, int)) else 0.0
        if "e" in a:
            if a["e"] not in memo:
                memo[a["e"]] = ev(w["exprs"][a["e"]])
            return memo[a["e"]]
        if "c" in a:
            return a["c"]
        if "curve" in a:
            c = w["curves"][a["curve"]]
            return _curve_at(c, ev(c["input"]))
        if "anim" in a:
            v = env.get("anim:%s.%s" % (a["anim"], a.get("key")), 0.0)
            return v if isinstance(v, (float, int)) else 0.0
        x = [ev(v) for v in a["a"]]
        op = a["op"]
        if op in (1, 3, 10, 11, 29, 37, 38):          # Neg Abs Min Max Step(edge, x) Sin Cos (one or two Floats)
            import math
            f = {1: lambda p: -p, 3: abs, 10: min, 11: max, 29: lambda e, p: 0.0 if p < e else 1.0,
                 37: math.sin, 38: math.cos}[op]
            return lift(f, *x)
        if op == 6:
            r = x[0]
            for y in x[1:]: r = lift(lambda p, q: p + q, r, y)
            return r
        if op == 8:
            r = x[0]
            for y in x[1:]: r = lift(lambda p, q: p * q, r, y)
            return r
        if op == 7: return lift(lambda p, q: p - q, x[0], x[1])
        if op == 9: return lift(lambda p, q: p / q if q else 0.0, x[0], x[1])
        if op in (12, 13, 14, 15, 16, 17):
            f = {12: lambda p, q: p == q, 13: lambda p, q: p != q, 14: lambda p, q: p < q,
                 15: lambda p, q: p > q, 16: lambda p, q: p <= q, 17: lambda p, q: p >= q}[op]
            return 1.0 if f(x[0], x[1]) else 0.0
        if op == 18: return x[1] if x[0] else x[2]
        if op == 19: return lift(lambda p, lo, hi: min(max(p, lo), hi), *x)
        if op == 21: return list(x)
        if op == 28: return lift(lambda p, q, t: p + (q - p) * t, *x)
        if op == 31: return lift(lambda v, a0, a1, b0, b1: b0 + (v - a0) / (a1 - a0) * (b1 - b0) if a1 != a0 else b0, *x)
        if op == 32: return lift(lambda p, q: p ** q, x[0], x[1])
        raise ValueError("opcode %d" % op)

    return ev


def hidden_nodes(w, params=None):
    """Node paths whose visibility binding is off for [params] (defaults otherwise)."""
    ev = evaluate(w, params)
    return {d["node"] for d in w["bindings"] if "visible" in d and not ev(d["visible"])}


def fmt(a):
    if "p" in a: return "$" + a["p"]
    if "e" in a: return "@" + a["e"]
    if "curve" in a: return "curve(%s)" % a["curve"]
    if "anim" in a: return "anim(%s.%s)" % (a["anim"], a.get("key"))
    if "c" in a:
        c = a["c"]
        return "(%s)" % ", ".join("%g" % x for x in c) if isinstance(c, list) else "%g" % c if isinstance(c, float) else repr(c)
    op = OPS.get(a["op"], "op%d" % a["op"])
    args = [fmt(x) for x in a["a"]]
    if op in ("+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">=") and len(args) >= 2:
        return "(" + (" %s " % op).join(args) + ")"
    if op == "if":
        return "(%s ? %s : %s)" % tuple(args)
    return "%s(%s)" % (op, ", ".join(args))


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    w = read_widget(argv[2])
    if argv[1] == "json":
        s = json.dumps(w, separators=(",", ":"))
        if len(argv) > 3: open(argv[3], "w").write(s)
        else: print(s)
    elif argv[1] == "text":
        for k, v in w["params"].items(): print("param", k, "=", v)
        for k, v in w["exprs"].items(): print("expr ", k, "=", fmt(v))
        for k, v in w["curves"].items(): print("curve", k, "(", fmt(v["input"]), ")", len(v["keys"]), "keys")
        for k, v in w["anims"].items(): print("anim ", k, v)
        for d in w["bindings"]:
            print("bind ", d["node"])
            for key in ("scale", "rotate", "translate", "layer", "visible"):
                if key in d: print("     ", key, "=", fmt(d[key]))
            for k, v in d.get("uniforms", {}).items(): print("      uniform", k, "=", fmt(v))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
