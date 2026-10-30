#!/usr/bin/env python3
"""
Validate a no-signature file-copy container before you ever flash it — offline.

This is the artifact `patch.py build-filecopy` produces and the thing you actually flash. It must be
a clean WOODOO container that carries NO signature record (so the head unit routes it to the
file-copy job) and delivers exactly the file you intend to a sane TargetPath. This checks:

  1. the patch **file name** parses and names a flashable area (the compatibility authority);
  2. the container **parses to EOF** (the WOODOO structure is intact — a corrupt container is the
     fastest way to brick a flash);
  3. **no signature record** is present (no `F0002000.nsw`, no `*.sign`) — a signature would make the
     HU verify the whole body and REJECT it; its absence is what makes the file-copy route work;
  4. it is **minimal**: the stream-start envelope + exactly one `Tag=FIL` descriptor + its data (a
     stray extra group is a warning, not an automatic pass);
  5. the descriptor's **TargetPath is sane** (absolute, ends in `/`, contains no `../`) and — advisory
     — begins with a known-good prefix (live `/fs/sda0/opt/` or staging `/fs/sda0/repository/istep/opt/`);
  6. optionally, the **embedded file is what you meant**: `--expect-file F` asserts the payload equals
     F byte-for-byte; or `--stock-file S --offset O --len N` asserts the payload is the same length as
     the stock file and differs from it ONLY inside the intended window (the length-preserving edit);
  7. optionally `--owner-blobB B`: the 128-byte window at `--offset` equals your own modulus B and is
     not the value in the stock file.

A container that fails any non-advisory check must not be flashed.

    python -m capabilities.flash_and_patching.validate.check_patch \
        --patched ownerca-swfl0000271A-007.051.002-apply.swdl \
        --stock-file NBTCarHU.stock --offset 0x35A300 --len 128 --owner-blobB owner_blobB.bin
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from capabilities.flash_and_patching.tools import container as C  # noqa: E402
from capabilities.flash_and_patching.tools import patch as P  # noqa: E402

_SIG_NAMES = {"F0002000.nsw"}


def _walk(path: str):
    """Return (records, descriptor_names, fil_group). fil_group = (descriptor, [data_records]) for the
    Tag=FIL payload, or None. Raises C.ContainerError on a malformed stream (incl. not ending at EOF)."""
    filesize = Path(path).stat().st_size
    records, names, fil = [], [], None
    with open(path, "rb") as fh:
        for desc, data in C._group_iter(fh, filesize):
            if desc is not None and desc.metadata:
                nm = desc.metadata.get("Name", "")
                if nm:
                    names.append(nm)
                if desc.metadata.get("Tag", "") == "FIL" and data:
                    fil = (desc, data)
            for r in ([desc] if desc is not None else []) + list(data):
                records.append(r)
    last_end = max((r.end for r in records), default=0)
    if last_end != filesize:
        raise C.ContainerError(f"stream did not end at EOF: leftover {filesize - last_end} byte(s)")
    return records, names, fil


def _read_payload(path: str, data_records) -> bytes:
    out = bytearray()
    with open(path, "rb") as fh:
        for r in data_records:
            fh.seek(r.body_offset)
            out += fh.read(r.length)
    return bytes(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--patched", required=True, help="the no-sig file-copy container to validate")
    ap.add_argument("--expect-file", help="assert the embedded payload equals this file byte-for-byte")
    ap.add_argument("--stock-file", help="assert the payload differs from this stock file only in the window")
    ap.add_argument("--offset", type=lambda x: int(x, 0), help="window offset within the payload/file")
    ap.add_argument("--len", type=int, help="window length (bytes)")
    ap.add_argument("--owner-blobB", help="assert the window equals this modulus and is not the stock value")
    a = ap.parse_args(argv)

    patched = Path(a.patched)
    ok = True
    warn = False

    def check(label, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        ok &= bool(cond)

    def note(label, cond):
        nonlocal warn
        print(f"  [{'ok' if cond else 'WARN'}] {label}")
        warn |= not cond

    # 1. name parses + flashable area
    meta = P.parse_name(patched.name)
    check(f"patch file name parses + flashable area ({patched.name})", meta is not None)

    # 2/3/4. structure, no signature, minimal shape
    try:
        records, names, fil = _walk(str(patched))
        check("container parses cleanly to EOF", True)
    except C.ContainerError as ex:
        check(f"container parses cleanly to EOF ({ex})", False)
        records, names, fil = [], [], None

    has_sig = any(n in _SIG_NAMES or n.endswith(".sign") for n in names)
    check("no signature record present (F0002000.nsw / *.sign absent)", not has_sig)
    check("exactly one Tag=FIL payload present", fil is not None)
    # minimal = stream-start envelope + 1 descriptor + its data record(s). Descriptor count == 1.
    n_desc = sum(1 for r in records if r.is_descriptor)
    note(f"minimal shape (1 descriptor; found {n_desc})", n_desc == 1)

    payload = b""
    if fil is not None:
        desc, data = fil
        tpath = desc.metadata.get("TargetPath", "")
        name = desc.metadata.get("Name", "")
        check(f"descriptor has TargetPath + Name ({tpath}{name})", bool(tpath) and bool(name))
        check("TargetPath is absolute", tpath.startswith("/"))
        check("TargetPath has no '../' traversal", "../" not in tpath)
        check("TargetPath ends with '/' (so Name appends cleanly)", tpath.endswith("/"))
        known = tpath.startswith(P.LIVE_PREFIX) or tpath.startswith(P.STAGING_PREFIX)
        note(f"TargetPath begins with a known-good prefix ({P.LIVE_PREFIX} or {P.STAGING_PREFIX})", known)
        model = ("live-direct" if tpath.startswith(P.LIVE_PREFIX)
                 else "staged (needs linkIStep)" if tpath.startswith(P.STAGING_PREFIX) else "custom")
        print(f"       -> write model: {model}")
        payload = _read_payload(str(patched), data)
        print(f"       -> payload {len(payload)} bytes, sha256 {hashlib.sha256(payload).hexdigest()[:16]}…")

    # 6. embedded payload == expected file
    if a.expect_file and fil is not None:
        want = Path(a.expect_file).read_bytes()
        check(f"embedded payload equals {a.expect_file} ({len(want)} bytes)", payload == want)

    # 6b/7. length-preserving edit vs stock + owner blobB
    if a.stock_file and fil is not None:
        stock = Path(a.stock_file).read_bytes()
        check(f"payload same length as stock file ({len(stock)} bytes)", len(payload) == len(stock))
        if len(payload) == len(stock):
            diffs = [i for i in range(len(stock)) if stock[i] != payload[i]]
            if a.offset is not None and a.len is not None:
                lo, hi = a.offset, a.offset + a.len
                stray = [d for d in diffs if not (lo <= d < hi)]
                check(f"no changes outside the {a.len}-byte window @0x{a.offset:X}", not stray)
                check(f"at least one byte changed in the window ({len(diffs)} differ total)", len(diffs) > 0)
            else:
                check(f"at least one byte changed ({len(diffs)} differ)", len(diffs) > 0)

    if a.owner_blobB and fil is not None and a.offset is not None:
        mod = Path(a.owner_blobB).read_bytes()
        window = payload[a.offset:a.offset + len(mod)]
        check(f"window @0x{a.offset:X} equals your owner modulus ({len(mod)} bytes)", window == mod)
        if a.stock_file:
            stock = Path(a.stock_file).read_bytes()
            stock_window = stock[a.offset:a.offset + len(mod)]
            check("window is NOT the stock value (anchor actually swapped)", window != stock_window)

    tail = "" if not warn else "  (with warnings — read them)"
    print("\n" + (f"ALL PASS — safe to flash per the runbook (03-flashing-safely.md).{tail}"
                  if ok else "FAILED — do NOT flash this container."))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
