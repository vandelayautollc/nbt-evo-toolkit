#!/usr/bin/env python3
"""
Patch model + authoring: name a patch, edit a file length-preservingly, and wrap it into the
minimal no-signature **file-copy container** you actually flash.

A patch is a `.swdl` flash container whose **file name is the authority on compatibility**:

    <id>-<class><SGBM id>-<version>-<apply|revert>.swdl
    e.g.  devmode-swfl0000271A-007.051.002-apply.swdl

- `id`        : letters/digits/underscore (no '-'), your name for the patch.
- `class`     : the SVK process class of the flash area (swfl, btld, ibad, …).
- `SGBM id`   : 8 hex, the area's id (e.g. 0000271A).
- `version`   : a 1–3 part prefix of the area version it applies to — `007.051.002` that version
                only, `007.051` any 007.051.x, `007` any 007.x.x.
- direction   : `apply` writes the patch; `revert` writes the stock file back.

The head unit only flashes a patch whose target area it actually has (checked against its SVK — see
../validate/check_patch.py and ../03-flashing-safely.md).

## Why two steps (edit, then wrap)

The head unit REJECTS a signed container whose body was modified (the flash signature binds the whole
body), so you do NOT edit a stock `.bin` in place and flash it. Instead you flash a freshly built
**no-signature file-copy container**: with no signature record present the HU's SwdlMaster accepts it
and routes the payload to its on-device file-copy job, which writes your file to a `TargetPath`. See
../01-how-flashing-works.md and ../02-authoring-patches.md.

So authoring is two steps:

    # 1) get the stock file out of your own container, edit only the bytes you intend (length-preserving)
    python patch.py edit --from-container swfl_0000271a.bin --payload NBTCarHU \
                         --offset 0x35A300 --bytes owner_blobB.bin -o NBTCarHU.patched

    # 2) wrap the edited file into the flashable no-sig file-copy container, named by convention
    python patch.py build-filecopy --file NBTCarHU.patched \
                         --target-path /fs/sda0/opt/car/bin/ \
                         --id ownerca --class swfl --sgbm 0000271A --version 007.051.002 -o .

    python patch.py parse    ownerca-swfl0000271A-007.051.002-apply.swdl
    python patch.py discover ./flash-patches
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from nbtevo.uds import PROCESS_CLASS  # noqa: E402  (code -> name; we use the name set)
from capabilities.flash_and_patching.tools import container as C  # noqa: E402

FLASHABLE = {n.lower() for n in PROCESS_CLASS.values()}  # swfl, btld, ibad, swfk, …
EXT = ".swdl"
_NAME = re.compile(r"([A-Za-z0-9_]+)-([A-Za-z]{4})([0-9A-Fa-f]{8})-(\d{3}(?:\.\d{3}){0,2})-(apply|revert)\.swdl")

# TargetPath prefixes the on-device file-copy job accepts, and the write model each implies.
# On this platform the CheckPathPrefix gate runs with EMPTY prefix args, so it is skipped and any
# absolute path (no "../") is accepted (fsc/72) — but confirm the gate state on your own unit, and
# prefer a known-good path. See 02-authoring-patches.md "The path gate".
LIVE_PREFIX = "/fs/sda0/opt/"                       # live-direct: overwrites the live file in place
STAGING_PREFIX = "/fs/sda0/repository/istep/opt/"   # staged: writes the repo copy, needs a linkIStep


@dataclass(frozen=True)
class FlashTarget:
    process_class: str   # e.g. "swfl"
    id: int
    version: List[int]   # 1..3 parts

    @property
    def id_hex(self) -> str:
        return "%08X" % self.id

    @property
    def version_pattern(self) -> str:
        return ".".join("%03d" % v for v in self.version)

    @property
    def area(self) -> str:
        return f"{self.process_class.upper()} {self.id_hex}"

    def matches(self, cls: str, id_: int, main: int, sub: int, patch: int) -> bool:
        """Whether an SVK entry (class name, id, version triple) is this area at an applicable version."""
        return (cls.lower() == self.process_class and id_ == self.id
                and self.version == [main, sub, patch][:len(self.version)])


def parse_name(name: str):
    m = _NAME.fullmatch(name)
    if not m:
        return None
    pid, cls, sgbm, version, kind = m.groups()
    if cls.lower() not in FLASHABLE:
        return None
    parts = [int(x) for x in version.split(".")]
    if any(p > 0xFF for p in parts):
        return None
    return {"id": pid, "target": FlashTarget(cls.lower(), int(sgbm, 16), parts), "direction": kind}


def file_name(pid: str, target: FlashTarget, direction: str) -> str:
    return f"{pid}-{target.process_class.lower()}{target.id_hex}-{target.version_pattern}-{direction}{EXT}"


def discover(folder: str):
    """Pair apply/revert files by (id, target). Later files of the same name would override earlier ones."""
    found = {}
    for p in sorted(Path(folder).glob("*" + EXT)):
        meta = parse_name(p.name)
        if meta:
            found.setdefault((meta["id"], meta["target"]), {})[meta["direction"]] = p.name
    return found


def edit_file(src_bytes: bytes, offset: int, new_bytes: bytes) -> bytes:
    """Overwrite exactly len(new_bytes) at offset — length-preserving. The edit must lie within the
    file. Returns the edited bytes (the original length is unchanged)."""
    if offset < 0 or offset + len(new_bytes) > len(src_bytes):
        raise ValueError(f"edit window [0x{offset:X}, 0x{offset + len(new_bytes):X}) is outside the "
                         f"{len(src_bytes)}-byte file")
    return src_bytes[:offset] + bytes(new_bytes) + src_bytes[offset + len(new_bytes):]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("parse", help="parse a patch file name")
    p.add_argument("name")

    e = sub.add_parser("edit", help="length-preserving byte-window edit of a file (the sub-step before build-filecopy)")
    src = e.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="the file to edit (a standalone file you already have)")
    src.add_argument("--from-container", help="extract the file from this container first (your own firmware)")
    e.add_argument("--payload", help="with --from-container: payload name inside it (e.g. NBTCarHU)")
    e.add_argument("--offset", required=True, help="byte offset within the file (e.g. 0x35A300)")
    e.add_argument("--bytes", required=True, help="file of replacement bytes (length-preserving)")
    e.add_argument("-o", "--out", required=True, help="output patched file")

    b = sub.add_parser("build-filecopy", help="wrap a file into the flashable no-signature file-copy container")
    b.add_argument("--file", required=True, help="the (edited) file to deliver — its bytes become the payload")
    b.add_argument("--target-path", required=True,
                   help="destination DIRECTORY on the HU (e.g. /fs/sda0/opt/car/bin/). "
                        "/fs/sda0/opt/... = live-direct; /fs/sda0/repository/istep/opt/... = staged")
    b.add_argument("--name", default=None, help="on-target filename (default: source basename)")
    b.add_argument("--index", default="0x0002", help="WOODOO group index (arbitrary; no SWE-table verify)")
    b.add_argument("--id", required=True, help="patch id for the file name")
    b.add_argument("--class", dest="cls", required=True, help="flash-area process class (swfl/btld/ibad/…)")
    b.add_argument("--sgbm", required=True, help="flash-area SGBM id, 8 hex (e.g. 0000271A)")
    b.add_argument("--version", required=True, help="area version prefix (e.g. 007.051.002)")
    b.add_argument("--revert", action="store_true", help="name the output a -revert (stock file back) instead of -apply")
    b.add_argument("-o", "--out-dir", default=".")

    d = sub.add_parser("discover", help="list patches in a folder")
    d.add_argument("folder")

    a = ap.parse_args(argv)

    if a.cmd == "parse":
        meta = parse_name(a.name)
        if not meta:
            print("does not follow the patch naming convention", file=sys.stderr)
            return 1
        t = meta["target"]
        print(f"id={meta['id']} area={t.area} version={t.version_pattern} direction={meta['direction']}")
        return 0

    if a.cmd == "edit":
        if a.from_container:
            if not a.payload:
                ap.error("--from-container requires --payload")
            tmp = Path(a.out).with_suffix(Path(a.out).suffix + ".stock")
            n = C.extract_payload(a.from_container, a.payload, str(tmp))
            src = tmp.read_bytes()
            print(f"extracted {a.payload} ({n} bytes) from {a.from_container} -> {tmp}  "
                  f"(keep it to build the matching -revert)")
        else:
            src = Path(a.file).read_bytes()
        new_bytes = Path(a.bytes).read_bytes()
        off = int(a.offset, 0)
        out = edit_file(src, off, new_bytes)
        Path(a.out).write_bytes(out)
        old = src[off:off + len(new_bytes)]
        print(f"edited @0x{off:X} ({len(new_bytes)} bytes, file length {len(out)} unchanged) -> {a.out}")
        print(f"  {old.hex()[:32]}… -> {bytes(new_bytes).hex()[:32]}…")
        print("Length-preserving: only those bytes changed. Validate the built container with check_patch.py.")
        return 0

    if a.cmd == "build-filecopy":
        if a.cls.lower() not in FLASHABLE:
            ap.error(f"--class {a.cls} not a flashable process class {sorted(FLASHABLE)}")
        target = FlashTarget(a.cls.lower(), int(a.sgbm, 16), [int(x) for x in a.version.split(".")])
        blob, info = C.build_filecopy_container(a.file, a.target_path, name=a.name, index=int(a.index, 0))
        name = file_name(a.id, target, "revert" if a.revert else "apply")
        out = Path(a.out_dir) / name
        out.write_bytes(blob)
        model = ("live-direct (overwrites the live file; effective next boot)"
                 if info["target_dir"].startswith(LIVE_PREFIX)
                 else "staged (writes the repo copy; needs a linkIStep to go live)"
                 if info["target_dir"].startswith(STAGING_PREFIX) else "custom path — verify the write model")
        print(f"built no-signature file-copy container -> {out}  ({info['out_size']} bytes)")
        print(f"  delivers {a.file} -> {info['target_full']}")
        print(f"  write model: {model}")
        print("Now validate it before it goes near the car:  python -m "
              "capabilities.flash_and_patching.validate.check_patch --patched "
              f"{out} --expect-file {a.file}")
        return 0

    if a.cmd == "discover":
        got = discover(a.folder)
        if not got:
            print("no patches found")
            return 0
        for (pid, t), dirs in got.items():
            undo = "apply+revert" if {"apply", "revert"} <= set(dirs) else "apply only"
            print(f"{pid}: {t.area} v{t.version_pattern} [{undo}]")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
