# File-format reference

The head unit's data files look opaque but every one is decodable. This folder is the **physical
facts**: for each format, (1) the **spec** — our reverse-engineering of the BMW/NBT-specific layout,
which you won't find published anywhere else — and (2) the **open-source codec** that does the
generic heavy lifting, which you install yourself.

**Split, on purpose:** the compression/serialization *algorithms* (LZO, NRV2D, Snappy, protobuf,
QNX-IFS walking) are all open source — we **reference** them so your agent downloads and sets them
up for its own OS, and we don't vendor GPL/QNX-licensed code. The BMW-specific *framing/semantics*
on top are **ours and ship here** as specs. With a spec + a codec you can write an extractor in any
language, on any OS — which is the point.

> Licensing note: UCL (NRV2D) is GPL and `dumpifs` needs a QNX license, so neither is bundled —
> install them yourself, or use the clean-room alternatives noted. Everything in *this* repo is
> under the project's [MIT License](../LICENSE).

---

## PSdZData container (`swfl_<id>.*`, `btld_<id>.*`, `cafd_<id>.caf.*`, …)

The outer wrapper around every pool file. Identify by the first bytes:

| Shape | First bytes / marker | Contents |
|---|---|---|
| Legacy BMW binary container | `90 ?? 2A 00 A1 ??` | length-prefixed binary blocks |
| Newer tar container | ASCII `<kind>_<UUID>_<VER>.json` | tar: JSON header + signature + data |
| XML descriptor | `<?xml … <BINARY-HEADER xmlns="binary-header.xsd"` | clear-text metadata |
| **CAFD** (coding) | `<?xml … <caf … isEncrypted="true"` | PKCS#7/CMS-encrypted coding payload |
| Dir-style | a dir with `.json` + `.sig` + `.bin.gz` under `full/` | gzip + JSON metadata + signature |

- **Codec:** none clean/public — our own parser (ships with `capabilities/flash_and_patching/` and
  `qnx_dev/` as those land). The CMS decrypt of a CAFD uses your own PSdZData keys
  (`capabilities/coding/tools/recover_key.py` territory).
- **SVK** (`22 F1 01`), the in-container/over-UDS software-version table, is already decoded in
  [`nbtevo/uds.py`](../nbtevo/uds.py) (`decode_svk`): `[svkVersion u8][progDepChecked u8][count u16
  BE][fingerprint 4|13][N×8 entry]`, entry = `[classCode u8][id u32 BE][main u8][sub u8][patch u8]`.

## QNX IFS — the OS/app image (and HBCIFS)

The OMAP and Jacinto filesystems are **QNX IFS** images; the NBT's are **HBCIFS = *Harman Becker*
Compressed IFS** (the HU's maker). Structure: a startup header + image header + a directory of
record entries pointing at (optionally compressed) file data.

- **Codec (open source, install yourself):**
  - **`dump_hbcifs`** — a C fork that explicitly handles IFS / ImageFS / **HBCIFS**:
    https://github.com/ReverseEngDotDev/dump_hbcifs (build with a C compiler on any OS).
  - **`dumpifs`** — the official QNX utility (needs a QNX license on newer SDPs).
  - **`qnxmount`** — `pip install qnxmount` (parses/mounts QNX filesystems; Linux-tested).
- **Our layer:** which image lives in which pool file (the Jacinto IFS is inside the `00001FFD`
  bootloader bundle), and the LZO framing around compressed records — documented with
  `capabilities/qnx_dev/`.

## LZO — record compression inside IFS

- **Codec:** `pip install python-lzo` (wraps `liblzo2`), available on all platforms; or `liblzo2`
  via your OS package manager. Standard, open (GPL for liblzo2 — use as an installed dependency,
  not vendored).

## NRV2D — the UI string table (`bmw/db/text.db`)

`text.db` is an **NRV2D-compressed UTF-16 string table** (decompressed on the HU by `libhmizip`'s
`nrv2d_decompress`). NRV2D is one of Markus Oberhumer's NRV algorithms.

- **Codec (open source, install yourself):** **UCL** implements NRV2B/NRV2D/NRV2E —
  https://www.oberhumer.com/opensource/ucl/ (GPL; install/build yourself, don't bundle). A small
  clean-room NRV2D decompressor is a candidate to ship here later so the repo is self-contained.
- **Our layer (spec):** after NRV2D decompression the payload is a UTF-16 string table keyed by
  string id; the `text.db` header frames the compressed block. (Full byte layout lands with the
  text-editing tooling.)

## protobuf — the HMI graphs (`.pbw`, `.pbx`, `.pbvar`)

The 3D-car animation graph (`widget.pbw`), scene node tree (`scene.pbx`), and series registry
(`variantregistry.pbvar`) are **protocol buffers**. They round-trip **byte-identical** through
`protoc`, so you can edit them as text.

- **Codec (open source, install yourself):** `protoc` (the protobuf compiler) — `pip install
  protobuf` for the Python runtime, or the `protobuf`/`protobuf-compiler` OS package.
  `protoc --decode_raw < file` prints field numbers + wire types with **no schema needed**.
- **Our layer (the value):** the *semantic schema* — what the fields mean. For `widget.pbw`:
  field 4 = 158 params + defaults; field 5 = named expressions (MDL/PMA/CND/RMV); field 7 = node
  bindings (path → {1 scale, 2 rotate°, 3 translate, 4 shader uniform, 7 visibility}); field 19 =
  Hermite curves ([t, v, in(type,Δv,Δt), out(…)]). Opcodes are BMW's `HmiBase.TEOperatorType` enum
  (6 Add, 8 Mul, 18 IfThenElse, 19 Clamp, 28 Mix, 31 RemapValue, 32 Pow, …). The `.proto` schemas
  ship with `capabilities/vehicle_models/`.

## RSVI — 3D meshes (`vehicles/<series>/*.rsvi`)

The vehicle meshes. Container is ours; the payload compression is Snappy.

```
"RSVI"                     magic
u32  nElements
nElements × {
  u32 offset               byte offset of this attribute in a vertex
  u32 usage                0=position 1=normal 2=uv(set idx) 3=custom
  char[16] name            NUL-padded (e.g. a_Color, a_Tangent, a_Binormal)
}
u32  nVerts
u32  nTris
u32  compSize              size of the Snappy block
Snappy( interleaved vertex data, then u16 triangle indices )   # no padding
```

- **Codec (open source, install yourself):** Snappy — `pip install python-snappy` or `cramjam`
  (cross-platform). (Validated: our encoder matches a `cramjam` reference to ~1.01× BMW size.)
- Units cm, z up, x to rear; wheels/doors/trunk are local to their pivots; rim meshes are shared.
  Reader/writer tooling (`rsvi.py`) ships with `capabilities/vehicle_models/`.

---

## How to use this folder

1. Identify the format (first bytes / extension / the table above).
2. Install the referenced codec for your OS (the `pip`/package/repo line above).
3. Apply our spec to frame/interpret what the codec gives you.
4. For visible assets, remember the integrity rule: **add/rename, never overwrite stock** (LMPC —
   see [docs/architecture.md](../docs/architecture.md)).
