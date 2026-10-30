#!/usr/bin/env python3
"""
Prove the FSC model end to end — offline, no car, no BMW key.

Generates a fresh owner trust anchor (e=3), mints FSCs under it for a few application numbers
(including a VIN-locked one), and checks that:
  1. each minted FSC is ACCEPTED under the owner modulus (the on-device verifier would accept it);
  2. each is REJECTED under a *different* modulus (so acceptance really depends on the installed key);
  3. the body round-trips through the parser.

This demonstrates the whole mechanism without touching a vehicle: mint-under-your-own-key works, and
an FSC is accepted iff its signature verifies against the modulus installed as blobB.

    python -m capabilities.fsc.validate.check_fsc
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from capabilities.fsc.tools import fsc as F  # noqa: E402

# A few application numbers from ../catalog.md (feature names are documentation, not keys).
APPNOS = [0x0143, 0x006F, 0x00E5, 0x0120]


def main() -> int:
    owner = F.keygen(1024)
    other = F.keygen(1024)
    n_owner, d_owner = int(owner["n_hex"], 16), int(owner["d_hex"], 16)
    n_other = int(other["n_hex"], 16)

    all_ok = True

    def check(label, cond):
        nonlocal all_ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        all_ok &= cond

    print(f"owner trust anchor: e={owner['e']}, {owner['bits']}-bit\n")
    for appno in APPNOS:
        fsc = F.mint_fsc(n_owner, d_owner, appno)
        ok_self, _ = F.verify_fsc(fsc, n_owner)
        ok_other, _ = F.verify_fsc(fsc, n_other)
        body = F.parse_body(fsc)
        check(f"AppNo {appno:#06x}: accepted under owner key", ok_self)
        check(f"AppNo {appno:#06x}: rejected under a different key", not ok_other)
        check(f"AppNo {appno:#06x}: parses back to the same AppNo", body["appno"] == f"0x{appno:04X}")

    # VIN-locked variant (9-char VIN field).
    vin_fsc = F.mint_fsc(n_owner, d_owner, 0x0143, vin=b"OWNVIN001")
    ok_vin, _ = F.verify_fsc(vin_fsc, n_owner)
    check("VIN-locked FSC accepted under owner key", ok_vin)
    check("VIN-locked FSC carries the VIN", F.parse_body(vin_fsc)["vin"] == "OWNVIN001")

    # "Who signed it" — recover the signing modulus straight from FSCs (e=3), as `whosigned --recover`
    # does against an unknown third-party anchor. Prove it lands on the real modulus, not the other.
    two = [F.mint_fsc(n_owner, d_owner, ap) for ap in (0x0143, 0x006F)]
    recovered = F.recover_modulus(two)
    check("modulus recovered from 2 FSCs equals the true anchor", recovered == n_owner)
    check("recovered anchor fingerprint matches the owner key",
          F.fingerprint(recovered) == F.fingerprint(n_owner))
    check("a different anchor has a different fingerprint", F.fingerprint(n_owner) != F.fingerprint(n_other))

    print("\n" + ("ALL PASS — the FSC mint/verify model is correct." if all_ok
                  else "FAILED — model mismatch; do not rely on these tools."))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
