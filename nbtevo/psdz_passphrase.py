"""
Derive the sec_security.lic keystore password from YOUR own PSdZ install — no secret to type.

The E-SYS keystore `security/sec_security.lic` is a PKCS#12. Its password is **not** a secret you
know or set: PSdZ computes it itself, from resources that ship in the BMW software. There is nothing
for an owner to "have." This module reproduces exactly what PSdZ's own
`com.bmw.psdz.security.impl.LicenseValidatorCrypto.readTrustInformation` → `genHashedPIN` does:

    password = HEX_UPPER( SHA1( passphrase[pid] ) )

where
  * `pid` is read from the `<... pid="N">` attribute of your own `sec_security.lic`, and
  * `passphrase[pid]` is one entry of a `<pplist>` that is *steganographically* encoded into two BMW
    logo PNGs (`bmw_logo.png` = AES-CBC ciphertext, `bmw_mini_logo.png` = the AES key), ported from
    `com.bmw.psdz.security.img.ResourceParser.processImg`. Those PNGs live in the PSdZ runtime, in
    `.../PSdZ/bin/psdz/resource.jar` (part of the same ISTA-D / Rheingold + PSdZ bundle your PSdZData
    came from). Point this at your own copy; nothing from BMW is shipped here.

Ship-nothing: this file is **method only**. It embeds no logo image, no passphrase, and no derived
password — all three come out of the owner's own licensed BMW install at run time.

Stego algorithm (per pixel, skipping row 0 and column 0): take the low 2 bits of R, then G, then B;
pack three 2-bit groups into one byte (6 bits), add 32 to make it printable ASCII, stop at '_'. The
resulting ASCII is a hex string; its bytes are the payload. For the full logo that payload is the
AES-128-CBC ciphertext (IV=0, PKCS#7 pad) of the `<pplist>` XML; for the mini logo it is the AES key.
"""
from __future__ import annotations

import base64
import hashlib
import struct
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path
from typing import Dict, Optional, Tuple

LOGO_NAME = "bmw_logo.png"
MINI_LOGO_NAME = "bmw_mini_logo.png"


# --- minimal PNG reader: 8-bit truecolor (RGB), non-interlaced -----------------------------------
# The BMW logo PNGs are color-type 2, bit-depth 8, non-interlaced. Decoding them needs only zlib +
# the five standard scanline filters, so the toolkit avoids a Pillow dependency for one image read.
def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)


def decode_png_rgb8(data: bytes) -> Tuple[int, int, bytes]:
    """Return (width, height, rgb_bytes) for an 8-bit, non-interlaced, truecolor-RGB PNG."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    i = 8
    w = h = 0
    idat = bytearray()
    while i < len(data):
        (ln,) = struct.unpack(">I", data[i : i + 4])
        typ = data[i + 4 : i + 8]
        body = data[i + 8 : i + 8 + ln]
        if typ == b"IHDR":
            w, h, bd, ct, _comp, _filt, interlace = struct.unpack(">IIBBBBB", body)
            if (bd, ct, interlace) != (8, 2, 0):
                raise ValueError(
                    f"expected 8-bit non-interlaced RGB PNG (got bitdepth={bd} colortype={ct} "
                    f"interlace={interlace}); this logo differs from the known BMW resource"
                )
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        i += 12 + ln  # length(4) + type(4) + body + CRC(4)
    raw = zlib.decompress(bytes(idat))
    stride = w * 3
    out = bytearray()
    prev = bytes(stride)
    p = 0
    for _ in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p : p + stride])
        p += stride
        if f == 1:  # Sub
            for x in range(3, stride):
                line[x] = (line[x] + line[x - 3]) & 0xFF
        elif f == 2:  # Up
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 0xFF
        elif f == 3:  # Average
            for x in range(stride):
                a = line[x - 3] if x >= 3 else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 0xFF
        elif f == 4:  # Paeth
            for x in range(stride):
                a = line[x - 3] if x >= 3 else 0
                c = prev[x - 3] if x >= 3 else 0
                line[x] = (line[x] + _paeth(a, prev[x], c)) & 0xFF
        elif f != 0:
            raise ValueError(f"unknown PNG filter {f}")
        out += line
        prev = bytes(line)
    return w, h, bytes(out)


# --- steganographic payload (ResourceParser.processImg) ------------------------------------------
def stego_payload(png_bytes: bytes) -> bytes:
    w, h, px = decode_png_rgb8(png_bytes)
    two_bits = []
    for row in range(h):
        if row == 0:
            continue
        base = row * w * 3
        for col in range(w):
            if col == 0:
                continue
            o = base + col * 3
            two_bits.append(px[o] & 3)
            two_bits.append(px[o + 1] & 3)
            two_bits.append(px[o + 2] & 3)
    chars = []
    i = 0
    while i + 2 < len(two_bits):
        byte = two_bits[i] | (two_bits[i + 1] << 2) | (two_bits[i + 2] << 4)
        ch = chr(byte + 32)
        chars.append(ch)
        i += 3
        if ch == "_":
            break
    if chars and chars[-1] == "_":
        chars.pop()
    return bytes.fromhex("".join(chars))


def recover_passphrases(logo_png: bytes, mini_logo_png: bytes) -> Dict[str, str]:
    """Decode the `<pplist>` → {pid: passphrase} from the two logo PNGs. Needs the crypto extra."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.padding import PKCS7

    ciphertext = stego_payload(logo_png)
    key = stego_payload(mini_logo_png)
    if len(key) not in (16, 24, 32):
        raise ValueError(f"unexpected AES key length {len(key)} from {MINI_LOGO_NAME}")
    dec = Cipher(algorithms.AES(key), modes.CBC(b"\x00" * 16)).decryptor()
    padded = dec.update(ciphertext) + dec.finalize()
    unpad = PKCS7(128).unpadder()
    xml = unpad.update(padded) + unpad.finalize()
    root = ET.fromstring(xml)
    pps = {p.attrib["id"]: (p.text or "") for p in root.iter() if p.tag.endswith("passphrase")}
    if not pps:
        raise ValueError("no <passphrase> entries in the decoded pplist")
    return pps


# --- locating the logos + reading the .lic pid ---------------------------------------------------
def _read_logos(
    resource_jar: Optional[Path], logo_png: Optional[Path], mini_logo_png: Optional[Path]
) -> Tuple[bytes, bytes]:
    if logo_png and mini_logo_png:
        return Path(logo_png).read_bytes(), Path(mini_logo_png).read_bytes()
    if resource_jar:
        with zipfile.ZipFile(resource_jar) as z:
            names = z.namelist()

            def grab(leaf: str) -> bytes:
                hit = next((n for n in names if n.rsplit("/", 1)[-1] == leaf), None)
                if hit is None:
                    raise FileNotFoundError(f"{leaf} not in {resource_jar}")
                return z.read(hit)

            return grab(LOGO_NAME), grab(MINI_LOGO_NAME)
    raise ValueError(
        "need the BMW logo resources: pass --resource-jar <PSdZ/bin/psdz/resource.jar> "
        "(or NBTEVO_PSDZ_RESOURCE_JAR), or both --bmw-logo and --bmw-mini-logo"
    )


def parse_lic(lic_path: Path) -> Tuple[Optional[str], bytes]:
    """
    A PSdZ `sec_security.lic` is an outer XML wrapper: `<... pid="N">BASE64(PKCS#12)</...>`.
    Return (pid, pkcs12_der). If the file is already a raw PKCS#12 (no XML wrapper), return
    (None, raw_bytes) — then no pid is available and the password cannot be derived from it.
    """
    data = Path(lic_path).read_bytes()
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None, data  # already an unwrapped .p12
    pid = root.attrib.get("pid")
    inner = (root.text or "").strip()
    return pid, base64.b64decode(inner)


def lic_pid(lic_path: Path) -> str:
    """The `pid` that selects which passphrase opens this .lic (its outer-XML root attribute)."""
    pid, _ = parse_lic(lic_path)
    if pid is None:
        raise ValueError(f"no pid attribute on {lic_path} (is it the XML-wrapped sec_security.lic?)")
    return pid


def keystore_der(lic_path: Path) -> bytes:
    """The inner PKCS#12 DER of sec_security.lic (base64-decoded from its XML wrapper)."""
    return parse_lic(lic_path)[1]


def derive_keystore_password(
    lic_path: Path,
    *,
    resource_jar: Optional[Path] = None,
    logo_png: Optional[Path] = None,
    mini_logo_png: Optional[Path] = None,
) -> bytes:
    """
    The PKCS#12 password for `sec_security.lic`, derived (never typed) exactly as PSdZ derives it:
    HEX_UPPER(SHA1(passphrase[pid])), pid from the .lic, passphrase from the owner's own logo PNGs.
    Returns ASCII bytes, ready to hand to a PKCS#12 loader.
    """
    pid = lic_pid(lic_path)
    logo, mini = _read_logos(resource_jar, logo_png, mini_logo_png)
    pps = recover_passphrases(logo, mini)
    if pid not in pps:
        raise KeyError(f"sec_security.lic pid={pid} not among decoded passphrases {sorted(pps)}")
    return hashlib.sha1(pps[pid].encode("ascii")).hexdigest().upper().encode("ascii")
