"""
UDS (ISO 14229) services and the BMW SVK codec, on top of :mod:`nbtevo.hsfz`.

Only the services this toolkit needs are here: session control, SecurityAccess, RDBI/WDBI,
RoutineControl, ECUReset — plus SVK (``22 F1 01``) decoding, because the SVK is how you learn a
module's **bootloader (BTLD)** and **coding (CAFD)** ids, which almost everything keys off.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .hsfz import HsfzClient, TGT_HU

# --- service ids ---
SID_DIAGNOSTIC_SESSION = 0x10
SID_ECU_RESET = 0x11
SID_SECURITY_ACCESS = 0x27
SID_READ_DATA_BY_ID = 0x22
SID_WRITE_DATA_BY_ID = 0x2E
SID_ROUTINE_CONTROL = 0x31

# --- common DIDs ---
DID_SVK = 0xF101          # SVK_Aktuell (software version compact)
DID_VIN = 0xF190          # VIN (latin-1)
DID_HU_IP = 0x172A        # module's own Ethernet IP (ver|ip4|mask4|gw4)

# --- NBT EVO coding datagroups (read via RDBI with the datagroup as the DID) ---
DG_CAF_ID = 0x300F        # CAF_ID datagroup; its value is an 8-byte SGBM id → the live CAFD
DG_CODING_FIRST = 0x3000
DG_CODING_LAST = 0x300D   # user coding datagroups (NBT EVO 00001EF6); 0x3010 holds the signature

# --- SVK process classes (first byte of each 8-byte entry) ---
PROCESS_CLASS = {
    1: "HWEL", 2: "HWAP", 3: "HWFR", 4: "GWTB", 5: "CAFD", 6: "BTLD", 7: "FLSL",
    8: "SWFL", 9: "SWFF", 10: "SWPF", 11: "ONPS", 12: "IBAD", 13: "SWFK", 15: "FAFP",
    16: "FCFA", 26: "TLRT", 27: "TPRG", 28: "BLUP", 29: "FLUP", 160: "ENTD", 161: "NAVD",
    162: "FCFN", 192: "SWUP", 193: "SWIP",
}


class NegativeResponse(RuntimeError):
    NRC = {
        0x10: "generalReject", 0x11: "serviceNotSupported", 0x22: "conditionsNotCorrect",
        0x31: "requestOutOfRange", 0x33: "securityAccessDenied", 0x35: "invalidKey",
        0x36: "exceedNumberOfAttempts", 0x7E: "subFunctionNotSupportedInActiveSession",
        0x7F: "serviceNotSupportedInActiveSession",
    }

    def __init__(self, sid: int, nrc: int):
        self.sid, self.nrc = sid, nrc
        name = self.NRC.get(nrc, "unknown")
        super().__init__(f"UDS 0x{sid:02X} negative response: 0x{nrc:02X} ({name})")


def _check(req_sid: int, resp: bytes) -> bytes:
    if len(resp) >= 3 and resp[0] == 0x7F and resp[1] == req_sid:
        raise NegativeResponse(req_sid, resp[2])
    if not resp or resp[0] != req_sid + 0x40:
        raise RuntimeError(f"unexpected UDS response to 0x{req_sid:02X}: {resp.hex()}")
    return resp


@dataclass
class SgbmId:
    process_class: str
    class_code: int
    id: int
    main: int
    sub: int
    patch: int

    @property
    def id_hex(self) -> str:
        return "%08X" % self.id

    @property
    def version(self) -> str:
        return "%03d.%03d.%03d" % (self.main, self.sub, self.patch)

    def __str__(self) -> str:
        return f"{self.process_class}-{self.id_hex}-{self.version}"


@dataclass
class Svk:
    svk_version: int
    prog_dep_checked: int
    entries: List[SgbmId]

    def of_class(self, name: str) -> List[SgbmId]:
        return [e for e in self.entries if e.process_class == name]

    @property
    def bootloader(self) -> Optional[SgbmId]:
        btld = self.of_class("BTLD")
        return min(btld, key=lambda e: (e.id, e.main, e.sub, e.patch)) if btld else None

    @property
    def codings(self) -> List[SgbmId]:
        return self.of_class("CAFD")


def decode_sgbm(b: bytes, at: int = 0) -> SgbmId:
    code = b[at]
    return SgbmId(
        process_class=PROCESS_CLASS.get(code, "UNKNOWN"),
        class_code=code,
        id=int.from_bytes(b[at + 1:at + 5], "big"),
        main=b[at + 5], sub=b[at + 6], patch=b[at + 7],
    )


def decode_svk(value: bytes) -> Svk:
    """
    Decode a raw SVK value (the bytes *after* ``62 F1 01``).

    Layout: ``[svkVersion u8][progDepChecked u8][count u16 BE][fingerprint 4|13][N×8 entry]``.
    The fingerprint length varies, so entries are taken from the last ``8N`` bytes (PSdZ's own
    tail-rule fallback).
    """
    if len(value) < 4:
        raise ValueError(f"SVK too short: {len(value)} bytes")
    count = int.from_bytes(value[2:4], "big")
    need = count * 8
    if 4 + need > len(value):
        raise ValueError(f"SVK announces {count} entries but has only {len(value)} bytes")
    first = len(value) - need
    entries = [decode_sgbm(value, first + i * 8) for i in range(count)]
    return Svk(svk_version=value[0], prog_dep_checked=value[1], entries=entries)


class Uds:
    """Thin UDS facade bound to one target address over an HSFZ session."""

    def __init__(self, client: HsfzClient, tgt: int = TGT_HU):
        self.c = client
        self.tgt = tgt

    def raw(self, uds: bytes) -> bytes:
        return self.c.request(self.tgt, uds)

    def session(self, sub: int) -> bytes:
        return _check(SID_DIAGNOSTIC_SESSION, self.raw(bytes([SID_DIAGNOSTIC_SESSION, sub])))

    def ecu_reset(self, sub: int = 0x01) -> bytes:
        return _check(SID_ECU_RESET, self.raw(bytes([SID_ECU_RESET, sub])))

    def security_access_seed(self, level: int) -> bytes:
        r = _check(SID_SECURITY_ACCESS, self.raw(bytes([SID_SECURITY_ACCESS, level])))
        return r[2:]  # strip SID echo + level

    def security_access_key(self, level: int, key: bytes) -> bytes:
        return _check(SID_SECURITY_ACCESS, self.raw(bytes([SID_SECURITY_ACCESS, level]) + key))

    def read_did(self, did: int) -> bytes:
        req = bytes([SID_READ_DATA_BY_ID, did >> 8, did & 0xFF])
        r = _check(SID_READ_DATA_BY_ID, self.raw(req))
        return r[3:]  # strip 62 + 2-byte DID echo

    def write_did(self, did: int, data: bytes) -> bytes:
        req = bytes([SID_WRITE_DATA_BY_ID, did >> 8, did & 0xFF]) + data
        return _check(SID_WRITE_DATA_BY_ID, self.raw(req))

    def routine_control(self, sub: int, rid: int, data: bytes = b"") -> bytes:
        req = bytes([SID_ROUTINE_CONTROL, sub, rid >> 8, rid & 0xFF]) + data
        return _check(SID_ROUTINE_CONTROL, self.raw(req))

    # --- convenience ---

    def read_vin(self) -> str:
        return self.read_did(DID_VIN).decode("latin1").strip("\x00 ")

    def read_svk(self) -> Svk:
        return decode_svk(self.read_did(DID_SVK))

    def read_live_cafd(self) -> Optional[SgbmId]:
        """
        The live coding dataset id. Prefer the CAF_ID datagroup (``22 30 0F``, an 8-byte SGBM id);
        fall back to the SVK's CAFD entry. Returns None if neither is present.
        """
        try:
            v = self.read_did(DG_CAF_ID)
            if len(v) >= 8:
                e = decode_sgbm(v, 0)
                if e.process_class == "CAFD":
                    return e
        except (NegativeResponse, RuntimeError):
            pass
        codings = self.read_svk().codings
        return codings[0] if codings else None
