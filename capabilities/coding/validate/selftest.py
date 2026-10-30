#!/usr/bin/env python3
"""
Prove the signer and your recovered key are correct — against your own car's own coding.

Two checks, both local, no car needed (just a backup NCD read from your car with read_coding.py):

  1. VERIFY  — the signature already in the NCD validates against the public modulus using the ECU's
     own CheckCodingSignature math. Confirms you decoded the scheme right.
  2. REPRODUCE — if the key has a private exponent, re-sign the NCD's content and check the result
     equals the signature bytes already in the NCD, BYTE FOR BYTE. Because the scheme is
     deterministic (raw RSA, e=3), only the correct key reproduces the car's own signature — so this
     is proof the recovered key is right. If it fails, do NOT use the key.

Usage:
    python -m capabilities.coding.validate.selftest --ncd backup.ncd --key ~/.nbtevo/key.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from nbtevo import srec  # noqa: E402
from capabilities.coding.tools import sign_ncd  # noqa: E402


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ncd", required=True, help="a backup NCD read from your own car")
    ap.add_argument("--key", required=True)
    ap.add_argument("--scheme", default=sign_ncd.DEFAULT_SCHEME, choices=sorted(sign_ncd.SCHEMES))
    a = ap.parse_args(argv)

    scheme = sign_ncd.SCHEMES[a.scheme]
    key = sign_ncd.load_key(a.key)
    mem, _ = srec.parse(Path(a.ncd).read_text())

    results = []

    # 1. VERIFY the car's own signature.
    ok_verify = sign_ncd.verify(mem, key, scheme)
    results.append(("VERIFY   car's own signature validates", ok_verify))

    # 2. REPRODUCE it with the private key.
    if key.private_exponent is None:
        results.append(("REPRODUCE (skipped: key has no private exponent)", None))
    else:
        existing = srec.pages(mem, [scheme.sig_dg]).get(scheme.sig_dg, b"")[4:4 + key.nbytes]
        recomputed = sign_ncd.sign_digest(sign_ncd.content_digest(mem, scheme), key)
        results.append(("REPRODUCE recomputed signature == car's", existing == recomputed and len(existing) > 0))

    print(f"scheme: {scheme.name}  digest: {scheme.digest}  btld: {key.btld}\n")
    all_pass = True
    for label, ok in results:
        mark = "— " if ok is None else ("PASS" if ok else "FAIL")
        print(f"  [{mark}] {label}")
        if ok is False:
            all_pass = False

    if all_pass:
        print("\nALL PASS — the scheme and your key are correct; signing will produce durable coding.")
        return 0
    print("\nFAIL — do not write coding with this key. Re-check recover_key.py inputs and the BTLD/scheme.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
