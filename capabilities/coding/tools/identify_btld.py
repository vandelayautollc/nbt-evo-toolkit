#!/usr/bin/env python3
"""
Identify the head unit: read its SVK and print the bootloader (BTLD), live CAFD, VIN, and the
coding signing class that applies. This is the first thing to run — everything keys off the BTLD.

Read-only; default session, no SecurityAccess, no consent gate needed.

Usage:
    python -m capabilities.coding.tools.identify_btld --host 169.254.104.13
    python -m capabilities.coding.tools.identify_btld --discover --bind 169.254.199.50
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from nbtevo.hsfz import HsfzClient, TGT_HU, discover  # noqa: E402
from nbtevo.uds import Uds  # noqa: E402

# Known coding classes by BTLD (extend as you characterize more modules; see ../02-signing-model.md).
BTLD_INFO = {
    "00001FFD": ("HU_NBT2 (NBT EVO head unit)", "legacy RSA / BMWSigVerify / MD5", "offline-signable"),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", help="gateway or HU IP (HSFZ :6801)")
    ap.add_argument("--target", type=lambda x: int(x, 0), default=TGT_HU, help="diag address (default 0x63)")
    ap.add_argument("--discover", action="store_true", help="broadcast-discover endpoints first")
    ap.add_argument("--bind", default="169.254.199.50", help="your IP on the ENET segment (for --discover)")
    a = ap.parse_args()

    host = a.host
    if a.discover or not host:
        print(f"discovering on {a.bind} …")
        for ep in discover(bind_ip=a.bind):
            tag = "  <- gateway" if ep.is_gateway else ""
            print(f"  {ep.ip:16} DIAGADR={ep.diag_addr}  VIN={ep.vin}{tag}")
            if ep.is_gateway and not host:
                host = ep.ip
        if not host:
            print("no gateway found; pass --host", file=sys.stderr)
            return 2

    with HsfzClient(host) as c:
        hu = Uds(c, a.target)
        vin = hu.read_vin()
        svk = hu.read_svk()
        btld = svk.bootloader
        cafd = hu.read_live_cafd()

    print(f"\nhost        {host}  (target 0x{a.target:02X})")
    print(f"VIN         {vin}")
    print(f"BTLD        {btld}")
    print(f"live CAFD   {cafd}")
    if btld:
        variant, scheme, signable = BTLD_INFO.get(btld.id_hex, ("(uncharacterized)", "?", "?"))
        print(f"\nvariant     {variant}")
        print(f"coding key  {scheme}")
        print(f"offline     {signable}")
        if btld.id_hex not in BTLD_INFO:
            print("\nThis BTLD isn't in the known table. Check its class in sec_ncdkeys.xml")
            print("(see ../02-signing-model.md) before assuming offline signing is possible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
