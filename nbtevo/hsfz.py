"""
HSFZ (High-Speed Fahrzeug-Zugang) transport — BMW F-series ENET diagnostics.

F-series cars (incl. the NBT EVO's host) speak **HSFZ**, not DoIP. The flow, proven on-car:

  1. Discovery: UDP broadcast ``00 00 00 00 00 11`` (ctrl 0x0011, "ident") to ``<bcast>:6811``.
     Each gateway/edge replies; the reply's *source IP* is the endpoint, and its payload (after the
     6-byte header) is a latin-1 ident string carrying ``DIAGADR<nn>``, ``BMWMAC<..>``, ``BMWVIN<..>``.
  2. Transport: TCP to ``<ip>:6801``. Frame = ``u32 length`` ``u16 ctrl`` ``u8 src`` ``u8 tgt`` ``uds...``
     where ``length`` counts the bytes after the control word (= 2 + len(uds) for a data frame).
     ctrl 0x0001 = data, 0x0002 = ack (skip it), 0x0011 = ident.
  3. Routing is the target byte alone. Connect once to the gateway and set ``tgt`` per ECU; the
     gateway forwards onto CAN/MOST/Ethernet. No routing-activation handshake (that's DoIP only).

Addresses: tester src = 0xF4, functional = 0xDF, FEM gateway = 0x10, NBT EVO head unit = 0x63.

Two endpoints you will see on the tethered link-local segment:
  - the **FEM gateway** (ident starts ``DIAGADR10``): connect here to reach the *whole car*.
  - the **HU's own edge** (serves 0x63 only): faster for HU-only work (coding/flash); the HU's own
    IP is also readable via ``22 17 2A`` once you're talking to 0x63.

This is a minimal, dependency-free client intended for owner diagnostics on the operator's own car.
"""
from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass
from typing import List, Optional

IDENT_PORT = 6811
DIAG_PORT = 6801

CTRL_DATA = 0x0001
CTRL_ACK = 0x0002
CTRL_IDENT = 0x0011

SRC_TESTER = 0xF4
TGT_FUNCTIONAL = 0xDF
TGT_GATEWAY = 0x10
TGT_HU = 0x63


@dataclass
class Endpoint:
    ip: str
    diag_addr: Optional[int]  # from DIAGADR<nn>, hex
    vin: Optional[str]
    mac: Optional[str]
    raw_ident: str

    @property
    def is_gateway(self) -> bool:
        return self.diag_addr == TGT_GATEWAY


def _parse_ident(payload: bytes, ip: str) -> Endpoint:
    s = payload.decode("latin1", "replace")
    def field(tag: str, n: int) -> Optional[str]:
        i = s.find(tag)
        return s[i + len(tag): i + len(tag) + n] if i >= 0 else None
    diag = field("DIAGADR", 2)
    vin = field("BMWVIN", 17)
    mac = field("BMWMAC", 12)
    return Endpoint(
        ip=ip,
        diag_addr=int(diag, 16) if diag else None,
        vin=vin.strip("\x00 ") if vin else None,
        mac=mac if mac else None,
        raw_ident=s,
    )


def discover(bind_ip: str, broadcast: str = "169.254.255.255",
             timeout: float = 3.0) -> List[Endpoint]:
    """
    Broadcast the HSFZ ident request and collect replies.

    ``bind_ip`` must be your host's address on the ENET segment (e.g. a 169.254.x.x link-local or a
    tethering address) so the probe egresses the right interface.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((bind_ip, 0))
    sock.settimeout(timeout)
    sock.sendto(struct.pack(">IH", 0, CTRL_IDENT), (broadcast, IDENT_PORT))

    found: dict[str, Endpoint] = {}
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            data, (ip, _) = sock.recvfrom(4096)
        except socket.timeout:
            break
        if len(data) < 6:
            continue
        _, ctrl = struct.unpack(">IH", data[:6])
        if ip not in found:
            found[ip] = _parse_ident(data[6:], ip)
    sock.close()
    return list(found.values())


class HsfzClient:
    """A single TCP/6801 HSFZ session. Set the target per request; the gateway routes."""

    def __init__(self, ip: str, src: int = SRC_TESTER, connect_timeout: float = 5.0):
        self.ip = ip
        self.src = src
        self.sock = socket.create_connection((ip, DIAG_PORT), timeout=connect_timeout)
        self.sock.settimeout(5.0)

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self) -> "HsfzClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _send(self, tgt: int, uds: bytes) -> None:
        frame = struct.pack(">IH", 2 + len(uds), CTRL_DATA) + bytes([self.src, tgt]) + uds
        self.sock.sendall(frame)

    def _recv_frame(self) -> tuple[int, bytes]:
        hdr = self._recv_exact(6)
        length, ctrl = struct.unpack(">IH", hdr)
        body = self._recv_exact(length) if length else b""
        return ctrl, body

    def _recv_exact(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("HSFZ peer closed the connection")
            buf += chunk
        return buf

    def request(self, tgt: int, uds: bytes, p2_star: float = 6.0) -> bytes:
        """
        Send a UDS request to ``tgt`` and return the raw UDS response bytes.

        Transparently drops ack frames (ctrl 0x0002) and the request echo, and re-arms on
        ``7F xx 78`` (responsePending), riding the extended P2* timer.
        """
        self._send(tgt, uds)
        deadline = time.time() + p2_star
        while time.time() < deadline:
            try:
                ctrl, body = self._recv_frame()
            except socket.timeout:
                break
            if ctrl != CTRL_DATA or len(body) < 2:
                continue  # ack / status frame
            resp = body[2:]  # strip src, tgt
            if not resp:
                continue
            if resp == uds[:1] * 0:  # defensive; never true, keeps shape clear
                continue
            # Drop the request echo (some gateways reflect it).
            if resp == uds:
                continue
            # responsePending: keep waiting.
            if len(resp) >= 3 and resp[0] == 0x7F and resp[2] == 0x78:
                deadline = time.time() + p2_star
                continue
            return resp
        raise TimeoutError(f"no UDS response from 0x{tgt:02X} for {uds.hex()}")
