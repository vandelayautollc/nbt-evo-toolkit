#!/usr/bin/env python3
"""
Back up the head unit's live coding to an NCD file. Read-only; do this before any coding change.

Reads each coding datagroup over UDS (``22 <dg>``) and writes a Motorola S-record NCD — the same
format write_coding.py consumes, so a backup is also a ready-to-write revert image.

Usage:
    python -m capabilities.coding.tools.read_coding --host 169.254.104.13 -o backup.ncd
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from nbtevo import srec  # noqa: E402
from nbtevo.hsfz import HsfzClient, TGT_HU  # noqa: E402
from nbtevo.uds import NegativeResponse, Uds  # noqa: E402

# NBT EVO coding datagroups incl. CAF_ID (0x300F) and the signature (0x3010).
DEFAULT_DGS = list(range(0x3000, 0x3011))


def read_coding(hu: Uds, datagroups) -> tuple[srec.Mem, list]:
    mem: srec.Mem = {}
    recs: list = [("raw", "S00600004844521B")]  # "HDR" S0 header (cosmetic)
    for dg in datagroups:
        try:
            page = hu.read_did(dg)
        except NegativeResponse:
            continue  # datagroup absent on this variant
        base = dg << 8
        for i, b in enumerate(page):
            mem[base + i] = b
        recs.append(("data", "3", 4, base, len(page)))
    recs.append(("raw", "S70500000000FA"))  # S7 terminator
    return mem, recs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True)
    ap.add_argument("--target", type=lambda x: int(x, 0), default=TGT_HU)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    with HsfzClient(a.host) as c:
        hu = Uds(c, a.target)
        vin = hu.read_vin()
        mem, recs = read_coding(hu, DEFAULT_DGS)

    Path(a.out).write_text(srec.emit(mem, recs))
    ndg = sum(1 for r in recs if r[0] == "data")
    print(f"VIN {vin}: backed up {ndg} datagroups ({len(mem)} bytes) -> {a.out}")
    print("Keep this file. Writing it back is a clean revert (it is already correctly signed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
