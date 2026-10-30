#!/usr/bin/env python3
"""
RSVI: the NBT-Evo HMI's mesh format (the 3D car models under /opt/hmi/ID5/data/ro/*/widgetasset/vehicles/<series>/).

Reader: HmiMain3D CHmiResourceMesh::loadFromBinaryStream (0x195d87c, resource type '8'; type '6' is OpenCTM, which the
same function also accepts, so .rsvi files are BMW's pre-baked form of OpenCTM sources). All little-endian:

  char[4] "RSVI"
  u32     numElements
  numElements x { u32 byteOffset; u32 usage; u32 setIndex; [usage 3: char name[] NUL-terminated] }
              usage 0 = position  (3 floats, 12 B)  -> a_Position
              usage 1 = normal    (3 floats, 12 B)  -> a_Normal
              usage 2 = texcoord  (2 floats,  8 B)  -> a_TextureCoordinate<setIndex or ''>
              usage 3 = custom    (4 floats, 16 B)  -> the given name (a_Color, a_Tangent, a_Binormal, ...)
  u32     numVertices
  u32     numTriangles
  u32     compressedSize
  byte    payload[compressedSize] = Snappy( vertices[numVertices * stride] ++ u16 indices[numTriangles * 3] )

stride = sum of element sizes (the reader adds them up; byteOffset is each element's place in the vertex). The
reader requires the Snappy length to fit (numVertices*stride + numTriangles*6, rounded up to 4 bytes) and indices
must be < 65536.

Usage:  rsvi.py info  <file.rsvi>...
        rsvi.py obj   <file.rsvi> <out.obj>          (positions, normals, first UV set, faces)
        rsvi.py build <in.json> <out.rsvi>           (see write_rsvi; JSON = {"elements":[...], "vertices":[[...]], "indices":[...]})
"""
import json, struct, sys

USAGE_SIZE = {0: 12, 1: 12, 2: 8, 3: 16}
USAGE_NAME = {0: "position", 1: "normal", 2: "texcoord", 3: "custom"}


# ---- Snappy (raw block format) ----

def _varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7F) << s; s += 7
        if c < 0x80:
            return r, i


def snappy_decompress(b):
    n, i = _varint(b, 0)
    out = bytearray()
    while i < len(b):
        tag = b[i]; i += 1
        t = tag & 3
        if t == 0:                                  # literal
            ln = tag >> 2
            if ln >= 60:
                nb = ln - 59
                ln = int.from_bytes(b[i:i + nb], "little"); i += nb
            ln += 1
            out += b[i:i + ln]; i += ln
            continue
        if t == 1:                                  # copy, 1-byte offset
            ln = ((tag >> 2) & 7) + 4
            off = ((tag >> 5) << 8) | b[i]; i += 1
        elif t == 2:                                # copy, 2-byte offset
            ln = (tag >> 2) + 1
            off = int.from_bytes(b[i:i + 2], "little"); i += 2
        else:                                       # copy, 4-byte offset
            ln = (tag >> 2) + 1
            off = int.from_bytes(b[i:i + 4], "little"); i += 4
        if off == 0 or off > len(out):
            raise ValueError("bad snappy offset")
        for _ in range(ln):                         # byte-wise: copies may overlap
            out.append(out[-off])
    if len(out) != n:
        raise ValueError(f"snappy length {len(out)} != header {n}")
    return bytes(out)


def snappy_compress(data):
    """Valid Snappy stream with a simple greedy matcher (4-byte hash, 2-byte-offset copies)."""
    out = bytearray()
    n = len(data)
    v = n
    while True:                                     # varint length
        if v < 0x80:
            out.append(v); break
        out.append((v & 0x7F) | 0x80); v >>= 7

    def emit_literal(a, b):
        while a < b:
            ln = min(b - a, 65536)
            if ln <= 60:
                out.append((ln - 1) << 2)
            elif ln <= 256:
                out.append(60 << 2); out.append(ln - 1)
            else:
                out.append(61 << 2); out.extend((ln - 1).to_bytes(2, "little"))
            out.extend(data[a:a + ln]); a += ln

    table = {}
    i = lit = 0
    while i + 4 <= n:
        key = data[i:i + 4]
        j = table.get(key)
        table[key] = i
        if j is not None and i - j <= 0xFFFF:
            ln = 4
            while i + ln < n and data[j + ln] == data[i + ln] and ln < 64:
                ln += 1
            emit_literal(lit, i)
            out.append(((ln - 1) << 2) | 2); out.extend((i - j).to_bytes(2, "little"))
            i += ln; lit = i
        else:
            i += 1
    emit_literal(lit, n)
    return bytes(out)


# ---- RSVI ----

def read_rsvi(path):
    b = open(path, "rb").read()
    if b[:4] != b"RSVI":
        raise ValueError("not RSVI")
    i = 4
    (ne,) = struct.unpack_from("<I", b, i); i += 4
    elements = []
    for _ in range(ne):
        off, usage, idx = struct.unpack_from("<III", b, i); i += 12
        name = None
        if usage == 3:
            j = b.index(b"\0", i); name = b[i:j].decode(); i = j + 1
        elif usage not in USAGE_SIZE:
            raise ValueError(f"bad usage {usage}")
        elements.append({"offset": off, "usage": usage, "index": idx, "name": name})
    nv, nt, csz = struct.unpack_from("<III", b, i); i += 12
    raw = snappy_decompress(b[i:i + csz])
    if i + csz != len(b):
        raise ValueError(f"{len(b) - i - csz} trailing bytes")
    stride = sum(USAGE_SIZE[e["usage"]] for e in elements)
    vbytes = nv * stride
    if len(raw) < vbytes + nt * 6:
        raise ValueError("payload shorter than vertices+indices")
    verts = [struct.unpack_from(f"<{stride // 4}f", raw, k * stride) for k in range(nv)]
    idx = list(struct.unpack_from(f"<{nt * 3}H", raw, vbytes))
    return {"elements": elements, "stride": stride, "vertices": verts, "indices": idx,
            "numVertices": nv, "numTriangles": nt, "compressedSize": csz, "rawSize": len(raw)}


def attr(m, usage, index=0, name=None):
    """Return the per-vertex tuples for one element, or None."""
    for e in m["elements"]:
        if e["usage"] == usage and (usage == 3 and e["name"] == name or usage != 3 and e["index"] == index):
            a = e["offset"] // 4; n = USAGE_SIZE[usage] // 4
            return [v[a:a + n] for v in m["vertices"]]
    return None


def write_rsvi(path, elements, vertices, indices):
    """elements: [{"usage":0..3,"index":k,"name":str|None}] in vertex order; offsets are computed."""
    hdr = bytearray(b"RSVI") + struct.pack("<I", len(elements))
    off = 0
    for e in elements:
        hdr += struct.pack("<III", off, e["usage"], e.get("index", 0))
        if e["usage"] == 3:
            hdr += e["name"].encode() + b"\0"
        off += USAGE_SIZE[e["usage"]]
    stride = off
    raw = bytearray()
    for v in vertices:
        if len(v) * 4 != stride:
            raise ValueError("vertex size != stride")
        raw += struct.pack(f"<{len(v)}f", *v)
    if len(indices) % 3 or max(indices, default=0) >= min(len(vertices), 0x10000):
        raise ValueError("bad indices")
    raw += struct.pack(f"<{len(indices)}H", *indices)
    # No padding: BMW's files end right after the indices; the reader rounds its own buffer up to whole words.
    comp = snappy_compress(bytes(raw))
    hdr += struct.pack("<III", len(vertices), len(indices) // 3, len(comp))
    open(path, "wb").write(bytes(hdr) + comp)


def write_rsvi_arrays(path, elements, verts, indices):
    """write_rsvi for numpy data: verts float32 (n, stride/4) already interleaved in [elements] order, indices
    (m, 3) or flat. Element offsets are recomputed (they must match the order). Compresses with cramjam's Snappy
    when installed (much faster), else with snappy_compress; both decode with the HU's reader."""
    import numpy as np
    verts = np.ascontiguousarray(verts, "<f4")
    idx = np.ascontiguousarray(indices, "<u2").ravel()
    stride = sum(USAGE_SIZE[e["usage"]] for e in elements)
    if verts.ndim != 2 or verts.shape[1] * 4 != stride:
        raise ValueError(f"vertex width {verts.shape} != stride {stride}")
    if len(verts) > 0x10000 or len(idx) % 3 or (len(idx) and int(np.asarray(indices).max()) >= len(verts)):
        raise ValueError("bad vertex count or indices")
    hdr = bytearray(b"RSVI") + struct.pack("<I", len(elements))
    off = 0
    for e in elements:
        hdr += struct.pack("<III", off, e["usage"], e.get("index", 0))
        if e["usage"] == 3:
            hdr += e["name"].encode() + b"\0"
        off += USAGE_SIZE[e["usage"]]
    raw = verts.tobytes() + idx.tobytes()
    try:
        import cramjam
        comp = bytes(cramjam.snappy.compress_raw(raw))
    except ImportError:
        comp = snappy_compress(raw)
    hdr += struct.pack("<III", len(verts), len(idx) // 3, len(comp))
    open(path, "wb").write(bytes(hdr) + comp)


def to_obj(m, out):
    pos = attr(m, 0); nrm = attr(m, 1); uv = attr(m, 2, 0)
    with open(out, "w") as f:
        for p in pos: f.write("v %.6f %.6f %.6f\n" % p)
        if uv:
            for t in uv: f.write("vt %.6f %.6f\n" % t)
        if nrm:
            for n in nrm: f.write("vn %.6f %.6f %.6f\n" % n)
        ix = m["indices"]
        for k in range(0, len(ix), 3):
            a, b, c = (x + 1 for x in ix[k:k + 3])
            if uv and nrm: f.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}\n")
            elif nrm: f.write(f"f {a}//{a} {b}//{b} {c}//{c}\n")
            elif uv: f.write(f"f {a}/{a} {b}/{b} {c}/{c}\n")
            else: f.write(f"f {a} {b} {c}\n")


def main(argv):
    cmd = argv[1]
    if cmd == "info":
        for p in argv[2:]:
            m = read_rsvi(p)
            els = ", ".join((e["name"] or USAGE_NAME[e["usage"]] + (str(e["index"]) if e["usage"] == 2 else ""))
                            for e in m["elements"])
            print(f"{p.split('/')[-1]}: {m['numVertices']} verts, {m['numTriangles']} tris, stride {m['stride']} [{els}]")
    elif cmd == "obj":
        to_obj(read_rsvi(argv[2]), argv[3])
    elif cmd == "build":
        j = json.load(open(argv[2]))
        write_rsvi(argv[3], j["elements"], j["vertices"], j["indices"])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
