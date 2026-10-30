#!/usr/bin/env python3
"""
Write a signed coding NCD to the head unit — the full durable-coding choreography.

SAFETY: defaults to a DRY RUN. It connects, enters the coding session, reads the SecurityAccess
seed, verifies the NCD signature locally, and PRINTS the exact writes it would perform — but sends
no write and no key — unless you pass --commit. Even with --commit it refuses unless the connected
car's VIN equals NBTEVO_OWN_VIN (so you cannot write to the wrong car), and unless the NCD's
signature verifies locally first.

The actual write additionally needs your module's L3 SecurityAccess key response, which is
module-specific and NOT shipped (see compute_security_key below and ../03-write-flow.md). Wire it
with your own key before a real commit.

Usage (rehearse):  python -m capabilities.coding.tools.write_coding --host H --ncd m.ncd --key k.json
Usage (for real):  …same… --commit            # gated + requires a working SecurityAccess hook
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from nbtevo import consent, srec  # noqa: E402
from nbtevo.hsfz import HsfzClient, TGT_HU  # noqa: E402
from nbtevo.uds import Uds  # noqa: E402
from capabilities.coding.tools import sign_ncd  # noqa: E402

SESSION_EXTENDED = 0x03
SESSION_CODING = 0x41
SA_LEVEL = 0x01
RID_CHECK_CODING_SIG = 0x0F01
DID_CPS = 0x37FE


def compute_security_key(seed: bytes, l3_key_path: str, btld: int = 0x00001FFD) -> bytes:
    """
    Compute the SecurityAccess key response from the seed, using YOUR own recovered L3 key.

    Recover the key from your own PSdZData (ships none):
        python -m nbtevo.keys --btld <id> --kind l3 -o l3_key.json      (see docs/keys.md)
    The seed→key construction (MD5 of [UserID][Controller][seed], raw RSA e=3 little-endian, the
    00000020 + per-word-swap wire format) is the shared L3 handshake — `nbtevo.l3` implements it,
    and the same key/construction unlocks flashing. VALIDATE against your own car: a positive 67 is
    the proof. Until you pass --l3-key, the tool runs dry and never reaches this.
    """
    import json
    from nbtevo import l3
    key = json.loads(Path(l3_key_path).read_text())
    return l3.sign_seed(seed, key, btld=btld)


def planned_writes(mem: srec.Mem, scheme: sign_ncd.Scheme):
    """Ordered (datagroup, bytes) writes: user datagroups first, signature datagroup LAST."""
    present = sorted({a >> 8 for a in mem})
    order = [dg for dg in present if dg != scheme.sig_dg] + ([scheme.sig_dg] if scheme.sig_dg in present else [])
    for dg in order:
        page = srec.pages(mem, [dg])[dg]
        yield dg, page


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True)
    ap.add_argument("--target", type=lambda x: int(x, 0), default=TGT_HU)
    ap.add_argument("--ncd", required=True, help="signed NCD to write")
    ap.add_argument("--key", required=True, help="key JSON (for local signature verification)")
    ap.add_argument("--scheme", default=sign_ncd.DEFAULT_SCHEME, choices=sorted(sign_ncd.SCHEMES))
    ap.add_argument("--l3-key", help="your L3 SecurityAccess key (required for --commit)")
    ap.add_argument("--commit", action="store_true", help="actually write (gated); omit to rehearse")
    a = ap.parse_args()

    scheme = sign_ncd.SCHEMES[a.scheme]
    key = sign_ncd.load_key(a.key)
    mem, _ = srec.parse(Path(a.ncd).read_text())

    # Refuse to proceed with an invalid signature — a bad sig can't produce a durable write anyway.
    if not sign_ncd.verify(mem, key, scheme):
        print("ERROR: NCD signature does not verify locally. Re-sign with sign_ncd.py first.", file=sys.stderr)
        return 1
    print("local signature check: OK")

    if a.commit:
        consent.require_owner("write coding to the connected vehicle")

    with HsfzClient(a.host) as c:
        hu = Uds(c, a.target)
        vin = hu.read_vin()
        print(f"connected VIN: {vin}")
        if a.commit:
            consent.assert_vin_match(vin)  # hard stop if not the car you own

        hu.session(SESSION_EXTENDED)
        hu.session(SESSION_CODING)
        seed = hu.security_access_seed(SA_LEVEL)
        print(f"coding session entered; SecurityAccess seed = {seed.hex()}")

        writes = list(planned_writes(mem, scheme))
        if not a.commit:
            print("\n-- DRY RUN -- would perform (no bytes sent):")
            for dg, page in writes:
                print(f"   2E {dg >> 8:02X} {dg & 0xFF:02X}  ({len(page)} bytes)")
            print(f"   31 01 {RID_CHECK_CODING_SIG >> 8:02X} {RID_CHECK_CODING_SIG & 0xFF:02X}  CheckCodingSignature")
            print(f"   2E {DID_CPS >> 8:02X} {DID_CPS & 0xFF:02X}  CPS, read-back, then 11 01 reset")
            print("\nRehearsal only. Re-run with --commit (and a wired --l3-key) to write.")
            return 0

        if not a.l3_key:
            print("ERROR: --commit needs --l3-key (your L3 SecurityAccess key)", file=sys.stderr)
            return 2
        hu.security_access_key(SA_LEVEL, compute_security_key(seed, a.l3_key))
        print("SecurityAccess granted (67 02)")

        for dg, page in writes:
            hu.write_did(dg, page)
            print(f"   wrote 0x{dg:04X} ({len(page)} bytes)")
        resp = hu.routine_control(0x01, RID_CHECK_CODING_SIG)
        if b"\x00" in resp:  # module-specific token; confirm checkSignCorrect for your ECU
            pass
        print(f"CheckCodingSignature -> {resp.hex()}")
        hu.write_did(DID_CPS, b"\x00")  # CPS payload is module-specific; see 03-write-flow.md
        print(f"CPS read-back: {hu.read_did(DID_CPS).hex()}")
        hu.ecu_reset(0x01)
        print("reset issued; HU will reboot and re-verify the new coding")

    print("\nDone. Read the coding back (read_coding.py) and diff to confirm the change stuck, then confirm the HMI")
    print("comes back up and the feature behaves. If the UI freezes, doesn't load, or reboot-loops, revert first:")
    print("re-run this tool with --ncd <your backup>. See ../05-apply-observe-revert.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
