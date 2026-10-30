#!/usr/bin/env python3
r"""
FSC tool — generate an owner key, mint FSCs under it, verify and parse them.

The NBT EVO verifies every "long" FSC against ONE modulus — **blobB** — compiled into `NBTCarHU`
at file offset 0x35A300 (128 bytes, little-endian, exponent e=3, PKCS#1 v1.5 / MD5). There is no
per-feature key and no certificate lookup. So an FSC is accepted iff its RSA signature verifies
under whatever modulus is installed as blobB.

You do NOT hold BMW's FSC private key, and this tool ships none. The owner-authorized path is to
install **your own** modulus as blobB (a length-preserving 128-byte patch — see ../02-blobB-and-minting.md
and the flash capability) and then mint FSCs with **your own** private key. This tool signs with the
key *you* supply/generate; it cannot and does not forge BMW's.

    python fsc.py keygen -o owner_key.json --blobb owner_blobB.bin   # your e=3 trust anchor
    python fsc.py mint   --key owner_key.json --appno 0x0143 -o carplay.fsc   # CarPlay, VIN-generic
    python fsc.py verify --fsc carplay.fsc --key owner_key.json      # prove the unit would accept it
    python fsc.py parse  --fsc carplay.fsc                           # decode the body fields
    python fsc.py whosigned --fsc a.fsc --fsc b.fsc \                # WHOSE anchor is on this unit?
        --anchor bmw=genuine_blobB.bin --anchor mine=owner_key.json --recover

Before overwriting blobB on a unit you didn't set up, run `whosigned` on FSCs you read off it
(see ../03-apply-and-read.md): you may not be the first to have swapped it.

⚠️ Enabling a feature BMW has not licensed to you may breach your agreement with BMW even on your own
car — that is between you and BMW. Use only on a vehicle you own. See ../../../LEGAL.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import struct
import sys
from math import gcd
from pathlib import Path

MD5_DIGESTINFO = bytes.fromhex("3020300c06082a864886f70d020505000410")
BLOBB_OFFSET = 0x35A300   # blobB location in NBTCarHU (for the flash patch; see 02-blobB-and-minting.md)


# ---- the 60-byte signed body (byte-exact to the EVO FSC layout) ----

def build_body(appno, upgrade_idx=1, supplier_id=b"       1", requester_type=b"       1",
               counter=0x0001, fscs_id=b"C329361", vin=None, date=b"201608242124") -> bytes:
    b = bytearray(b"\x01\x01")
    b += struct.pack(">H", appno)
    b += struct.pack(">H", upgrade_idx)
    assert len(supplier_id) == 8
    b += supplier_id
    b += b"\x01"                       # count code
    assert len(requester_type) == 8
    b += requester_type
    b += struct.pack(">H", counter)    # <=9999 count field
    b += b"\x01"                       # FscsId-type
    assert len(fscs_id) == 7
    b += fscs_id
    b += b"\x01"                       # VIN-type (1 => 9-byte VIN follows)
    if vin is None:
        b += b"\x00" * 9               # VIN-generic (unit skips the per-VIN compare)
    else:
        v = vin.encode() if isinstance(vin, str) else vin
        assert len(v) == 9, "VIN field is 9 bytes"
        b += v
    b += b"\x04\x02"                   # date tag/len
    assert len(date) == 12
    b += date                          # GeneralizedTime (YYYYMMDDhhmm)
    b += b"Z\x00\x00"
    assert len(b) == 60, f"body len {len(b)}"
    return bytes(b)


def pkcs1_v15_md5(digest: bytes, modlen=128) -> bytes:
    assert len(digest) == 16
    t = MD5_DIGESTINFO + digest
    pslen = modlen - 3 - len(t)
    assert pslen >= 8
    return b"\x00\x01" + b"\xff" * pslen + b"\x00" + t


def mint_fsc(n: int, d: int, appno: int, **body_kw) -> bytes:
    """A 188-byte FSC signed by private (n, d). e is implied by the verifier (3)."""
    body = build_body(appno, **body_kw)
    em = pkcs1_v15_md5(hashlib.md5(body).digest(), 128)
    sig = pow(int.from_bytes(em, "big"), d, n)
    return body + sig.to_bytes(128, "big")


def verify_fsc(fsc: bytes, n: int, e: int = 3):
    """Reproduce the on-device verifier (NBTCarHU FUN_00305c50): m = sig^e mod N, strip PKCS#1, cmp MD5."""
    body, sigb = fsc[:-128], fsc[-128:]
    sig = int.from_bytes(sigb, "big")
    if sig >= n:
        return False, "sig>=N"
    m = pow(sig, e, n).to_bytes(128, "big")
    if m[:2] != b"\x00\x01":
        return False, "bad 00 01"
    i = 2
    while i < 128 and m[i] == 0xFF:
        i += 1
    if m[i] != 0x00:
        return False, "FF run not 00-terminated"
    i += 1
    if m[i:i + 18] != MD5_DIGESTINFO:
        return False, "bad DigestInfo"
    if i + 34 != 128:
        return False, f"slack: envelope not exactly 128 (i={i})"
    if m[i + 18:i + 34] != hashlib.md5(body).digest():
        return False, "hash mismatch"
    return True, "OK"


def parse_body(fsc: bytes) -> dict:
    b = fsc[:-128]
    vin = b[34:43]
    return {
        "version": b[0:2].hex(),
        "appno": f"0x{struct.unpack('>H', b[2:4])[0]:04X}",
        "upgrade_index": struct.unpack(">H", b[4:6])[0],
        "supplier_id": b[6:14].decode("latin1"),
        "requester_type": b[15:23].decode("latin1"),
        "counter": struct.unpack(">H", b[23:25])[0],
        "fscs_id": b[26:33].decode("latin1"),
        "vin": "(VIN-generic)" if vin == b"\x00" * 9 else vin.decode("latin1"),
        "creation_date": b[45:57].decode("latin1"),
        "signature_len": len(fsc) - len(b),
    }


# ---- owner trust anchor (your own e=3 keypair; its modulus replaces blobB) ----

def _is_probable_prime(num, k=24):
    if num < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if num % sp == 0:
            return num == sp
    r, dd = 0, num - 1
    while dd % 2 == 0:
        dd //= 2; r += 1
    for _ in range(k):
        a = 2 + secrets.randbelow(num - 3)
        x = pow(a, dd, num)
        if x in (1, num - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, num)
            if x == num - 1:
                break
        else:
            return False
    return True


def _rand_prime_e3(bits):
    """A prime p with (p-1) coprime to 3, so e=3 is invertible."""
    while True:
        cand = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        while not _is_probable_prime(cand):
            cand += 2
        if (cand - 1) % 3 != 0:
            return cand


def keygen(bits=1024):
    """Generate the owner trust anchor: RSA, e=3 (what the FSC verifier uses)."""
    p = _rand_prime_e3(bits // 2)
    q = _rand_prime_e3(bits // 2)
    while q == p:
        q = _rand_prime_e3(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    assert gcd(3, phi) == 1
    return {"n_hex": f"{n:x}", "e": 3, "d_hex": f"{pow(3, -1, phi):x}", "bits": n.bit_length()}


def blobB_le(n: int) -> bytes:
    """The 128-byte blobB replacement: modulus, little-endian, length-preserving."""
    return n.to_bytes(128, "little")


def fingerprint(n: int) -> str:
    """Stable short id for a trust anchor = SHA-256 of its blobB bytes (as they sit in NBTCarHU)."""
    return hashlib.sha256(blobB_le(n)).hexdigest()[:16]


# ---- identifying WHOSE anchor is installed (who signed the FSCs on a unit) ----
#
# You are not the only person who might have swapped blobB. Before you overwrite it, find out what
# is already installed, so you don't strand a genuine BMW anchor or someone else's owner-CA swap.
#
# Two ways to answer "who signed this unit's FSCs":
#   (a) Verify the installed FSC(s) against candidate anchors you know (genuine BMW blobB carved
#       from a stock NBTCarHU; your own key). Whichever verifies is the installed anchor.
#   (b) If none match — it's a *third party's* anchor — recover its modulus straight from the FSCs.
#       e=3 makes this possible: for each token, sig^3 - paddedMessage is an exact multiple of N, so
#       gcd across two+ tokens from the same unit yields N (times a tiny cofactor we strip). Then
#       fingerprint it; it's a stranger's key, and your swap would replace it.

def _padded_int(body: bytes) -> int:
    return int.from_bytes(pkcs1_v15_md5(hashlib.md5(body).digest()), "big")


def recover_modulus(fscs):
    """Recover the signing modulus from >=2 FSCs signed by the SAME anchor (e=3 gcd attack)."""
    if len(fscs) < 2:
        raise ValueError("need >=2 FSCs signed by the same anchor to recover a modulus")
    g = 0
    for f in fscs:
        body, sigb = f[:-128], f[-128:]
        g = gcd(g, abs(int.from_bytes(sigb, "big") ** 3 - _padded_int(body)))
    # g == N * gcd(cofactors); strip the small cofactor without cutting into a ~1024-bit modulus.
    p = 2
    while p < 100000:
        while g % p == 0 and (g // p).bit_length() >= 1000:
            g //= p
        p += 1
    return g


# ---- CLI ----

def _load_modulus(args) -> int:
    if args.key:
        return int(json.loads(Path(args.key).read_text())["n_hex"], 16)
    if args.blobb:
        return int.from_bytes(Path(args.blobb).read_bytes(), "little")
    raise SystemExit("need --key or --blobb for the modulus")


def _load_anchor(spec: str):
    """Parse a '[label=]path' anchor spec into (label, modulus). path = key JSON or 128-byte blobB."""
    label, _, path = spec.partition("=")
    if not path:
        label, path = "", label
    raw = Path(path).read_bytes()
    try:
        n = int(json.loads(raw.decode())["n_hex"], 16)      # owner key JSON
    except (ValueError, UnicodeDecodeError, KeyError):
        if len(raw) != 128:
            raise SystemExit(f"{path}: not a key JSON and not a 128-byte blobB")
        n = int.from_bytes(raw, "little")                   # raw blobB (NBTCarHU bytes)
    return (label or path), n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("keygen", help="generate your own e=3 trust anchor + blobB replacement")
    g.add_argument("-o", "--out", required=True, help="owner key JSON (keep the private part secret)")
    g.add_argument("--blobb", help="also write the 128-byte LE blobB replacement here")
    g.add_argument("--bits", type=int, default=1024)

    m = sub.add_parser("mint", help="mint an FSC signed by your own key")
    m.add_argument("--key", required=True)
    m.add_argument("--appno", required=True, help="application number, e.g. 0x0143 (CarPlay) — see ../catalog.md")
    m.add_argument("--vin", help="9-char VIN field for a unit-locked FSC (omit for VIN-generic)")
    m.add_argument("--upgrade-index", type=int, default=1)
    m.add_argument("-o", "--out", required=True)

    v = sub.add_parser("verify", help="check an FSC would be accepted under a modulus")
    v.add_argument("--fsc", required=True)
    v.add_argument("--key", help="owner key JSON (its modulus)")
    v.add_argument("--blobb", help="or a 128-byte LE blobB file")

    p = sub.add_parser("parse", help="decode an FSC's body fields")
    p.add_argument("--fsc", required=True)

    fp = sub.add_parser("fingerprint", help="print the stable short id of an anchor (key or blobB)")
    fp.add_argument("--key")
    fp.add_argument("--blobb")

    w = sub.add_parser("whosigned", help="identify WHOSE anchor signed FSC(s) read off a unit")
    w.add_argument("--fsc", required=True, action="append",
                   help="an FSC token read from the unit (repeatable; give 2+ for --recover)")
    w.add_argument("--anchor", action="append", default=[],
                   help="candidate anchor '[label=]path' (key JSON or 128-byte blobB); repeatable")
    w.add_argument("--recover", action="store_true",
                   help="if no candidate matches, recover the unknown modulus from 2+ FSCs (e=3)")

    a = ap.parse_args(argv)

    if a.cmd == "keygen":
        key = keygen(a.bits)
        Path(a.out).write_text(json.dumps(key, indent=2))
        try:
            Path(a.out).chmod(0o600)
        except OSError:
            pass
        if a.blobb:
            Path(a.blobb).write_bytes(blobB_le(int(key["n_hex"], 16)))
        print(f"owner trust anchor: e={key['e']}, {key['bits']}-bit, modulus {key['n_hex'][:16]}…")
        print(f"  key  -> {a.out} (PRIVATE — this is the root of trust for all your FSCs)")
        if a.blobb:
            print(f"  blobB-> {a.blobb} (128-byte LE; patch NBTCarHU @0x{BLOBB_OFFSET:06X} with this)")
        return 0

    if a.cmd == "mint":
        key = json.loads(Path(a.key).read_text())
        n, d = int(key["n_hex"], 16), int(key["d_hex"], 16)
        vin = a.vin.encode() if a.vin else None
        fsc = mint_fsc(n, d, int(a.appno, 0), upgrade_idx=a.upgrade_index, vin=vin)
        ok, msg = verify_fsc(fsc, n)
        if not ok:
            print(f"ERROR: minted FSC failed self-verify ({msg})", file=sys.stderr)
            return 1
        Path(a.out).write_bytes(fsc)
        print(f"minted AppNo {int(a.appno, 0):#06x} ({len(fsc)} B) -> {a.out}; self-verify OK")
        return 0

    if a.cmd == "verify":
        n = _load_modulus(a)
        ok, msg = verify_fsc(Path(a.fsc).read_bytes(), n)
        print(json.dumps({"accepted": ok, "detail": msg}, indent=2))
        return 0 if ok else 1

    if a.cmd == "parse":
        print(json.dumps(parse_body(Path(a.fsc).read_bytes()), indent=2))
        return 0

    if a.cmd == "fingerprint":
        n = _load_modulus(a)
        print(f"{fingerprint(n)}  (e=3, {n.bit_length()}-bit)")
        return 0

    if a.cmd == "whosigned":
        tokens = [Path(f).read_bytes() for f in a.fsc]
        anchors = [_load_anchor(s) for s in a.anchor]
        print(f"{len(tokens)} FSC(s):")
        for f, tok in zip(a.fsc, tokens):
            b = parse_body(tok)
            print(f"  {f}: AppNo {b['appno']}, VIN {b['vin']}")
        matched = None
        if anchors:
            print("\nagainst candidate anchors:")
            for label, n in anchors:
                res = [verify_fsc(t, n)[0] for t in tokens]
                tag = "ALL" if all(res) else ("some" if any(res) else "none")
                print(f"  [{tag:4}] {label}  (fp {fingerprint(n)})")
                if all(res) and matched is None:
                    matched = (label, n)
        if matched:
            label, n = matched
            print(f"\n==> signed by: {label}  (fp {fingerprint(n)}). This is the installed anchor.")
            return 0
        if not a.recover:
            print("\n==> no candidate anchor verifies all tokens."
                  + ("" if anchors else " (give --anchor, or --recover)")
                  + ("\n    Add the genuine BMW blobB and your own key as --anchor, or pass --recover." if anchors else ""))
            return 1
        try:
            n = recover_modulus(tokens)
        except ValueError as e:
            print(f"\n==> cannot recover: {e}", file=sys.stderr)
            return 2
        if all(verify_fsc(t, n)[0] for t in tokens):
            print(f"\n==> signed by an UNKNOWN anchor (not any candidate): fp {fingerprint(n)}, "
                  f"{n.bit_length()}-bit.\n    Someone else swapped blobB. Your overwrite would replace it.")
            return 0
        print("\n==> recovery inconclusive — tokens may not share one anchor, or need more samples.",
              file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
