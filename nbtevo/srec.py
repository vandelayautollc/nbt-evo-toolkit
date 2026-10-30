"""
Motorola S-record codec for BMW NCD coding containers.

A BMW NCD (the on-the-wire coding dataset) is an S-record file. Each coding *datagroup* maps to an
S-record address as  ``addr = (datagroup << 8) | page_offset``  — so datagroup 0x3001, byte 0x62 is
at S-record address 0x300162. This module parses an NCD into a flat ``addr -> byte`` map (plus the
record templates, so it can be re-emitted byte-structure-preserving), and extracts per-datagroup
"pages".

Parsing/emitting is structure-preserving: ``emit()`` re-emits exactly the records ``parse()`` read,
with only the data bytes you changed updated and checksums recomputed. Nothing else moves.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

Mem = Dict[int, int]
Record = tuple


def parse(text: str) -> Tuple[Mem, List[Record]]:
    """Return (mem: addr->byte, records: templates for re-emission)."""
    mem: Mem = {}
    recs: List[Record] = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 4 or line[0] != "S":
            if line:
                recs.append(("raw", line))
            continue
        t = line[1]
        if t in "123":
            alen = {"1": 2, "2": 3, "3": 4}[t]  # address length in bytes
            cnt = int(line[2:4], 16)
            addr = int(line[4:4 + alen * 2], 16)
            dlen = cnt - alen - 1
            data = bytes.fromhex(line[4 + alen * 2:4 + alen * 2 + dlen * 2])
            for i, b in enumerate(data):
                mem[addr + i] = b
            recs.append(("data", t, alen, addr, dlen))
        else:
            recs.append(("raw", line))
    return mem, recs


def emit(mem: Mem, recs: List[Record]) -> str:
    """Re-emit the records, substituting current ``mem`` bytes and recomputing checksums."""
    out: List[str] = []
    for r in recs:
        if r[0] == "raw":
            out.append(r[1])
            continue
        _, t, alen, addr, dlen = r
        data = bytes(mem[addr + i] for i in range(dlen))
        body = addr.to_bytes(alen, "big") + data
        cnt = alen + dlen + 1
        chk = (~(cnt + sum(body)) & 0xFF)
        out.append(f"S{t}{cnt:02X}{body.hex().upper()}{chk:02X}")
    return "\n".join(out) + "\n"


def pages(mem: Mem, datagroups: Iterable[int]) -> Dict[int, bytes]:
    """Extract the contiguous page bytes of each datagroup present in ``mem``."""
    result: Dict[int, bytes] = {}
    for dg in datagroups:
        offs = [a & 0xFF for a in mem if (a >> 8) == dg]
        if not offs:
            continue
        ln = max(offs) + 1
        result[dg] = bytes(mem.get((dg << 8) | i, 0) for i in range(ln))
    return result


def get(mem: Mem, datagroup: int, offset: int) -> int:
    return mem.get((datagroup << 8) | offset, 0)


def set_byte(mem: Mem, datagroup: int, offset: int, value: int,
             mask: int = 0xFF, shift: int = 0) -> None:
    """Set bits of one coding byte. ``value`` is placed as ``(value << shift) & mask``."""
    a = (datagroup << 8) | offset
    mem[a] = (mem.get(a, 0) & ~mask) | ((value << shift) & mask)
