"""
Shared key recovery — recover YOUR own keys for YOUR bootloader from YOUR own PSdZData, locally.

One engine for every key the write paths need, keyed by the bootloader (BTLD) id read from the car:

  kind "ncd"  — the coding signing key (Codier-Sign), from security/sec_ncdkeys.xml.
                Used to (re)sign an NCD so a coding change survives reboot (capabilities/coding).
  kind "l3"   — the Level-3 SecurityAccess key (BMWSigVerify), from security/sec_auth_l3.xml.
                Used to unlock a WRITE session: coding write (27 01/02) and flash (27 11/12).

Both are E-SYS-wrapped in their sec_*.xml and recovered through the same chain:
  1. load the E-SYS private key from security/sec_security.lic (a PKCS#12). Its password is NOT a
     secret you type — PSdZ derives it, and so do we: HEX_UPPER(SHA1(passphrase[pid])), where pid is
     read from your own .lic and the passphrase is decoded from the BMW logo PNGs in your own PSdZ
     runtime (see nbtevo/psdz_passphrase.py). Point --resource-jar at your PSdZ/bin/psdz/resource.jar;
  2. RSA-unwrap the session key referenced in security/sec_keyreference.xml → an AES-128 key;
  3. AES-128-CBC (IV=0) decrypt the entry for your BTLD → a PKCS#8 RSA private key.

The recovered modulus is public (baked into the HU firmware / its verify facility); the private
exponent is secret and is written only to the local, gitignored key file. This ships NO key and
embeds NO BMW secret (not the logos, not the passphrase, not the derived password — all come from
your own install at run time). See docs/keys.md for what each key does.

    python -m nbtevo.keys --btld 00001FFD --kind ncd -o ncd_key.json --resource-jar .../resource.jar
    python -m nbtevo.keys --btld 00001FFD --kind l3  -o l3_key.json  --resource-jar .../resource.jar

Requires:  pip install -e '.[crypto]'   ·   gated by nbtevo.consent (owner action).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Tuple

from . import consent

DIGEST_MAP = {"MD5": "md5", "SHA-256": "sha256", "SHA256": "sha256", "SHA-1": "sha1"}

# Per-kind: the source file, a hint to find the session-key reference, and what the key is for.
KINDS = {
    "ncd": {
        "file": "sec_ncdkeys.xml",
        "ref_hint": "NCDS",
        "elem": "NCodSigKey",
        "use": "coding signature — (re)sign an NCD (capabilities/coding/tools/sign_ncd.py)",
    },
    "l3": {
        "file": "sec_auth_l3.xml",
        "ref_hint": "AS_L3",          # sec_keyreference.xml SessionKey reference token (fallback)
        "elem": "AuthenticationKey",  # the per-BTLD key element in sec_auth_l3.xml
        "use": "SecurityAccess (write unlock) — coding write 27 01/02 and flash 27 11/12",
    },
}


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _blob(s: str) -> bytes:
    s = re.sub(r"\s+", "", s or "")
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return bytes.fromhex(s)
    return base64.b64decode(s)


def _unwrap_session_key(keyref_xml: Path, esys_priv, ref_name: Optional[str]) -> bytes:
    """
    RSA-unwrap the AES session key from sec_keyreference.xml.

    Each key file names its session key exactly, in its root `encKeyRef` attribute
    (e.g. sec_auth_l3.xml → "refKey_AS_L3_…", sec_ncdkeys.xml → "refKey_NCDS_…"); the
    reference's wrapped blob is the `<SessionKey><Reference>…</Reference><keyData>` whose
    Reference matches. Selecting by that exact name matters: every SessionKey is wrapped to the
    same E-SYS key, so they ALL decrypt to a 16-byte AES key — "first one that decrypts" would
    silently pick the wrong one and the downstream AES-CBC would yield garbage.
    """
    from cryptography.hazmat.primitives.asymmetric import padding
    root = ET.parse(keyref_xml).getroot()
    entries = []  # (reference_name, wrapped_text)
    for sk in root.iter():
        if _localname(sk.tag) != "SessionKey":
            continue
        ref = next((( (c.text or "").strip()) for c in sk.iter()
                    if _localname(c.tag).lower() == "reference"), None)
        kd = next((c.text for c in sk.iter()
                   if _localname(c.tag).lower() == "keydata" and (c.text or "").strip()), None)
        if kd is not None:
            entries.append((ref, kd))

    def _unwrap(text: str) -> bytes:
        key = esys_priv.decrypt(_blob(text), padding.PKCS1v15())
        return key if len(key) in (16, 24, 32) else key[-16:]

    if ref_name:
        exact = [t for r, t in entries if r == ref_name]
        substr = [t for r, t in entries if r and ref_name in r]
        for text in exact or substr:
            return _unwrap(text)
    # No (matching) named reference: fall back to the first blob that unwraps to a sane AES key.
    for _ref, text in entries:
        try:
            return _unwrap(text)
        except Exception:  # noqa: BLE001
            continue
    raise KeyError(f"could not unwrap any session key from {keyref_xml} (ref {ref_name!r})")


def _find_entry(sec_xml: Path, btld: str, elem_hint: Optional[str]) -> Tuple[bytes, dict]:
    root = ET.parse(sec_xml).getroot()
    btld_norm = btld.lower().lstrip("0") or "0"
    for el in root.iter():
        if elem_hint and _localname(el.tag) != elem_hint:
            continue
        blob = ET.tostring(el, encoding="unicode").lower()
        if f"btld-{btld.lower()}" in blob or re.search(rf"\b0*{btld_norm}\b", blob):
            kd = next((c for c in el.iter() if _localname(c.tag).lower() in ("keydata", "key", "privatekey")), None)
            if kd is not None and (kd.text or "").strip():
                return _blob(kd.text), kd.attrib
    raise KeyError(f"no key entry for BTLD {btld} in {sec_xml}")


def recover(psdzdata: Path, btld: str, kind: str, keystore_password: bytes) -> dict:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {sorted(KINDS)}")
    from cryptography.hazmat.primitives.serialization import pkcs12, load_der_private_key
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    spec = KINDS[kind]
    sec = psdzdata / "security"
    lic, keyref, src = sec / "sec_security.lic", sec / "sec_keyreference.xml", sec / spec["file"]
    for p in (lic, keyref, src):
        if not p.exists():
            raise FileNotFoundError(f"expected {p} — is NBTEVO_PSDZDATA pointing at your psdzdata/ root?")

    from . import psdz_passphrase

    esys_priv, _, _ = pkcs12.load_key_and_certificates(psdz_passphrase.keystore_der(lic), keystore_password)
    if esys_priv is None:
        raise ValueError("no private key in sec_security.lic (derived keystore password rejected)")
    # Each key file names its session key exactly (root encKeyRef); fall back to the hint if absent.
    ref_name = ET.parse(src).getroot().get("encKeyRef") or spec.get("ref_hint")
    aes_key = _unwrap_session_key(keyref, esys_priv, ref_name)

    body, attrib = _find_entry(src, btld, spec["elem"])
    dec = Cipher(algorithms.AES(aes_key), modes.CBC(b"\x00" * 16)).decryptor()
    pt = dec.update(body) + dec.finalize()
    pt = pt[: -pt[-1]] if pt and pt[-1] <= 16 else pt  # PKCS#5 unpad
    priv = load_der_private_key(pt, password=None)
    nums = priv.private_numbers()
    pub = nums.public_numbers
    digest_attr = next((v for k, v in attrib.items() if _localname(k).lower() == "digestalg"), None)
    return {
        "btld": btld.upper(),
        "kind": kind,
        "use": spec["use"],
        "scheme": next((v for k, v in attrib.items() if _localname(k).lower() == "signaturescheme"), "BMWSigVerify"),
        "digest": DIGEST_MAP.get((digest_attr or "").upper().replace(" ", "-"), "md5"),
        "test_key": str(attrib.get("testKey", "")).lower() == "true",
        "public_exponent": pub.e,
        "modulus_hex": "%x" % pub.n,
        "private_exponent_hex": "%x" % nums.d,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--btld", required=True, help="bootloader id, e.g. 00001FFD (read it with coding/identify_btld)")
    ap.add_argument("--kind", required=True, choices=sorted(KINDS), help="ncd = coding signing · l3 = SecurityAccess")
    ap.add_argument("--psdzdata", default=os.environ.get("NBTEVO_PSDZDATA"))
    ap.add_argument("--resource-jar", default=os.environ.get("NBTEVO_PSDZ_RESOURCE_JAR"),
                    help="your PSdZ runtime resource.jar (…/PSdZ/bin/psdz/resource.jar) — holds the "
                         "logo PNGs the keystore password is derived from; NOT in psdzdata/")
    ap.add_argument("--bmw-logo", help="alternative to --resource-jar: path to your own bmw_logo.png")
    ap.add_argument("--bmw-mini-logo", help="…and your own bmw_mini_logo.png")
    ap.add_argument("-o", "--out", required=True, help="where to write the recovered key JSON (gitignored)")
    a = ap.parse_args(argv)

    try:
        consent.require_owner(f"recover your {a.kind.upper()} key from your own PSdZData")
    except consent.ConsentError as e:
        print(e, file=sys.stderr)
        return 2
    if not a.psdzdata:
        print("set NBTEVO_PSDZDATA (or pass --psdzdata) to your extracted psdzdata/ root", file=sys.stderr)
        return 2
    if not ((a.bmw_logo and a.bmw_mini_logo) or a.resource_jar):
        print("point to your own BMW logo resources so the keystore password can be derived:\n"
              "  --resource-jar <your PSdZ/bin/psdz/resource.jar>   (or set NBTEVO_PSDZ_RESOURCE_JAR)\n"
              "  or both --bmw-logo and --bmw-mini-logo\n"
              "There is no passphrase to type — PSdZ derives the keystore password from these.",
              file=sys.stderr)
        return 2
    try:
        from . import psdz_passphrase
        lic = Path(a.psdzdata) / "security" / "sec_security.lic"
        keystore_password = psdz_passphrase.derive_keystore_password(
            lic,
            resource_jar=Path(a.resource_jar) if a.resource_jar else None,
            logo_png=Path(a.bmw_logo) if a.bmw_logo else None,
            mini_logo_png=Path(a.bmw_mini_logo) if a.bmw_mini_logo else None,
        )
        key = recover(Path(a.psdzdata), a.btld, a.kind, keystore_password)
    except ImportError:
        print("this tool needs the crypto extra:  pip install -e '.[crypto]'", file=sys.stderr)
        return 2
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"recovery failed: {e}", file=sys.stderr)
        return 1

    out = Path(a.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(key, indent=2))
    try:
        out.chmod(0o600)
    except OSError:
        pass
    if key["test_key"]:
        print("WARNING: testKey entry — a bench key, NOT valid on a customer ECU.", file=sys.stderr)
    print(f"recovered {key['kind'].upper()} key for BTLD {key['btld']}  ({key['scheme']}/{key['digest']}, e={key['public_exponent']})")
    print(f"  use: {key['use']}")
    print(f"  modulus (public): {key['modulus_hex'][:24]}…")
    print(f"  -> {out} (private exponent kept local; gitignored)")
    if a.kind == "ncd":
        print("  verify it: python -m capabilities.coding.validate.selftest --ncd backup.ncd --key", out)
    else:
        print("  the proof an L3 key is right is a 67 SecurityAccess response on the car (see docs/keys.md).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
