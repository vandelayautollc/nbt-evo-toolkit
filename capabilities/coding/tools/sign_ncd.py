#!/usr/bin/env python3
"""
Sign (or re-sign) an NBT EVO coding NCD after edits — the BMWSigVerify primitive.

The head unit re-verifies the coding signature at every boot, so any datagroup edit must be
followed by recomputing the signature datagroup, or the change reverts. This script does both:
apply ``--set`` edits to an NCD, recompute the signature with your recovered key, self-verify, and
write the result. Signing is local and needs no car.

See ../02-signing-model.md for the scheme. Verifying needs only the public modulus; producing a new
signature needs the private exponent (recover it with recover_key.py — your key, your data).

Usage:
    python -m capabilities.coding.tools.sign_ncd IN.ncd OUT.ncd --key key.json \
        --set 0x3001,0x62,2,0x78,3        # dg, offset, value, mask, shift

    python -m capabilities.coding.tools.sign_ncd IN.ncd --verify --key key.json   # just check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Allow running as a module from the repo root, or as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from nbtevo import srec  # noqa: E402


@dataclass(frozen=True)
class Scheme:
    """A coding signature scheme: which datagroups, which digest, where the signature lives."""
    name: str
    content_dgs: Tuple[int, ...]
    sig_dg: int
    digest: str  # "md5" or "sha256"

    @property
    def digest_len(self) -> int:
        return {"md5": 16, "sha256": 32}[self.digest]


# The NBT EVO head unit (CAFD 00001EF6) layout, and a sibling for contrast. Default is the EVO.
SCHEMES: Dict[str, Scheme] = {
    "nbtevo": Scheme("nbtevo", tuple(range(0x3000, 0x3010)), 0x3010, "md5"),
    # R1250 cluster CAFD 00004130 — same primitive, SHA-256, different datagroups.
    "kombi3": Scheme("kombi3", tuple(list(range(0x3000, 0x300A)) + [0x37EF, 0x37F0]), 0x37F1, "sha256"),
}
DEFAULT_SCHEME = "nbtevo"


@dataclass
class Key:
    modulus: int
    public_exponent: int
    private_exponent: Optional[int] = None
    digest: Optional[str] = None
    btld: Optional[str] = None

    @property
    def nbytes(self) -> int:
        return (self.modulus.bit_length() + 7) // 8


def load_key(path: str) -> Key:
    d = json.loads(Path(path).read_text())
    return Key(
        modulus=int(d["modulus_hex"], 16),
        public_exponent=int(d.get("public_exponent", 3)),
        private_exponent=int(d["private_exponent_hex"], 16) if d.get("private_exponent_hex") else None,
        digest=d.get("digest"),
        btld=d.get("btld"),
    )


def wordswap(b: bytes) -> bytes:
    """Byte-reverse each 32-bit word, keeping word order (BMW big-number storage quirk)."""
    return b"".join(b[i:i + 4][::-1] for i in range(0, len(b), 4))


def content_digest(mem: srec.Mem, scheme: Scheme) -> bytes:
    pages = srec.pages(mem, scheme.content_dgs)
    content = b"".join(pages[dg] for dg in scheme.content_dgs if dg in pages)
    return hashlib.new(scheme.digest, content).digest()


def sign_digest(digest: bytes, key: Key) -> bytes:
    if key.private_exponent is None:
        raise ValueError("this key has no private exponent; recover it with recover_key.py")
    m = int.from_bytes(digest, "little")
    s = pow(m, key.private_exponent, key.modulus)
    return wordswap(s.to_bytes(key.nbytes, "little"))


def signature_page(sig: bytes, key: Key) -> bytes:
    """Signature datagroup payload: big-endian word count || signature."""
    return (key.nbytes // 4).to_bytes(4, "big") + sig


def resign(mem: srec.Mem, key: Key, scheme: Scheme) -> bytes:
    sig = sign_digest(content_digest(mem, scheme), key)
    page = signature_page(sig, key)
    for i, b in enumerate(page):
        mem[(scheme.sig_dg << 8) | i] = b
    return sig


def verify(mem: srec.Mem, key: Key, scheme: Scheme) -> bool:
    """Reproduce the ECU's CheckCodingSignature math. Needs only the public modulus."""
    digest = content_digest(mem, scheme)
    sig_page = srec.pages(mem, [scheme.sig_dg]).get(scheme.sig_dg, b"")
    if len(sig_page) < 4 + key.nbytes:
        return False
    sig = sig_page[4:4 + key.nbytes]
    D = pow(int.from_bytes(wordswap(sig), "little"), key.public_exponent, key.modulus)
    return D.to_bytes(scheme.digest_len, "little") == digest and D.bit_length() <= 8 * scheme.digest_len


def parse_set(s: str) -> Tuple[int, int, int, int, int]:
    p = s.split(",")
    dg, off, val = int(p[0], 0), int(p[1], 0), int(p[2], 0)
    mask = int(p[3], 0) if len(p) > 3 else 0xFF
    shift = int(p[4], 0) if len(p) > 4 else 0
    return dg, off, val, mask, shift


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ncd_in")
    ap.add_argument("ncd_out", nargs="?", help="output NCD (omit with --verify)")
    ap.add_argument("--key", required=True, help="key JSON from recover_key.py")
    ap.add_argument("--scheme", default=DEFAULT_SCHEME, choices=sorted(SCHEMES))
    ap.add_argument("--set", action="append", default=[], metavar="DG,OFF,VAL[,MASK,SHIFT]",
                    help="edit a coding byte, e.g. 0x3001,0x62,2,0x78,3")
    ap.add_argument("--verify", action="store_true", help="only verify the input NCD's signature")
    a = ap.parse_args(argv)

    scheme = SCHEMES[a.scheme]
    key = load_key(a.key)
    mem, recs = srec.parse(Path(a.ncd_in).read_text())

    if a.verify:
        ok = verify(mem, key, scheme)
        print(json.dumps({"scheme": scheme.name, "signature_valid": ok}, indent=2))
        return 0 if ok else 1

    if not a.ncd_out:
        ap.error("ncd_out is required unless --verify")
    for s in a.set:
        srec.set_byte(mem, *parse_set(s))
    sig = resign(mem, key, scheme)
    if not verify(mem, key, scheme):
        print("ERROR: self-verify failed after signing", file=sys.stderr)
        return 1
    Path(a.ncd_out).write_text(srec.emit(mem, recs))
    print(json.dumps({
        "scheme": scheme.name, "btld": key.btld, "digest": scheme.digest,
        "edits": len(a.set), "signature": sig.hex(), "out": a.ncd_out,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
