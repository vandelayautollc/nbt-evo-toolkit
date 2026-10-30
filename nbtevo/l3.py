#!/usr/bin/env python3
"""
L3 SecurityAccess signer — turn a requestSeed response into a sendKey response, with YOUR own
recovered L3 key. The *same* construction unlocks a coding write (``27 01``/``27 02``) and a flash
(``27 11``/``27 12``); see docs/keys.md.

This ships **no key**. You pass the ``l3_key.json`` you recovered from your own PSdZData
(``python -m nbtevo.keys --kind l3``) — it holds the modulus and private exponent. The algorithm
itself is not secret: the seed is folded into a block, MD5'd, signed raw-RSA e=3 (little-endian),
and wire-encoded a particular way. Documenting it lets your own agent run the handshake without any
embedded BMW secret.

    from nbtevo.l3 import sign_seed
    key = json.load(open("l3_key.json"))                 # {modulus_hex, private_exponent_hex, ...}
    sendkey = sign_seed(seed, key, btld=0x00001FFD)        # bytes to put after 27 02 / 27 12

CLI (for rehearsing / checking the math off-car):
    python -m nbtevo.l3 --key l3_key.json --seed 1122334455667788 --btld 00001FFD
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def _wordswap(b: bytes) -> bytes:
    """Reverse the bytes within each 32-bit word (the 27 12 KEY encoding)."""
    if len(b) % 4:
        raise ValueError("length must be a multiple of 4")
    return b"".join(b[i:i + 4][::-1] for i in range(0, len(b), 4))


def sign_seed(seed: bytes, key: dict, btld: int = 0x00001FFD, user_id: int = 0x00000000,
              modlen: int = 128) -> bytes:
    """Build the SecurityAccess sendKey payload (the bytes after ``27 02`` / ``27 12``).

    seed    : the 8-byte seed from the requestSeed positive response (67 01/67 11 <seed>).
    key     : dict with ``modulus_hex`` + ``private_exponent_hex`` (from ``nbtevo.keys --kind l3``);
              ``public_exponent`` defaults to 3.
    btld    : the Controller word folded into the signed block (your BTLD id).
    user_id : the 4-byte testerId sent with requestSeed. 0 is the value the proven flash used
              (the OPT_DEBUG file-copy flash authenticated and committed on-car with testerId 0).

    Returns ``00 00 00 20`` (word count 32, big-endian) followed by the 128-byte signature with each
    32-bit word byte-reversed — 132 bytes total. Raises if the signature fails self-verification.
    """
    if len(seed) != 8:
        raise ValueError(f"seed must be 8 bytes, got {len(seed)}")
    n = int(key["modulus_hex"], 16)
    d = int(key["private_exponent_hex"], 16)
    e = int(key.get("public_exponent", 3))

    block = user_id.to_bytes(4, "big") + btld.to_bytes(4, "big") + seed    # [UserID][Controller][seed]
    m = int.from_bytes(hashlib.md5(block).digest(), "little")              # MD5 read little-endian
    s = pow(m, d, n)
    if pow(s, e, n) != m:                                                  # self-check: s^e mod N == m
        raise ValueError("signature failed self-verification — wrong key?")
    sig = s.to_bytes(modlen, "little")
    return (modlen // 4).to_bytes(4, "big") + _wordswap(sig)               # 00 00 00 20 || swapped sig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", required=True, help="l3_key.json from `nbtevo.keys --kind l3`")
    ap.add_argument("--seed", required=True, help="8-byte seed as hex (16 chars), from 67 01/67 11")
    ap.add_argument("--btld", type=lambda x: int(x, 16), default=0x00001FFD, help="Controller id (hex)")
    ap.add_argument("--user-id", type=lambda x: int(x, 16), default=0x00000000, help="testerId (hex)")
    a = ap.parse_args(argv)

    try:
        key = json.loads(Path(a.key).read_text())
        seed = bytes.fromhex(a.seed)
        payload = sign_seed(seed, key, btld=a.btld, user_id=a.user_id)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"sendKey payload ({len(payload)} bytes): {payload.hex().upper()}")
    print(f"full PDU:  2712{payload.hex().upper()}   (coding: 2702…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
