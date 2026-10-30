#!/usr/bin/env python3
"""
Flash-plan generator — print the exact UDS/SWDL frame sequence to flash a patched container.

This deliberately does NOT open a socket or touch a car. Flashing is the brick-riskiest operation
here, and (per the project's "instructions over scripts" stance for on-car writes) the right
deliverable is the precise, ordered sequence an operator — or their own transport — executes, plus
the runbook in ../03-flashing-safely.md. The frame builders are a faithful port of the proven
flasher's UDS payloads; the HSFZ framing/tester address are the transport's job, and the
**SecurityAccess key is signed with YOUR own recovered L3 key** via the shared construction in
`nbtevo.l3` (docs/keys.md) — this file ships no key and opens no socket.

    python flash_plan.py --container ownerca-swfl0000271A-007.051.002-apply.swdl

Nothing in this file writes to a vehicle.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ALFI = 0x44            # 4-byte address + 4-byte size
LBN = 0                # logicalBlockNumber for a file-copy container. 0 is proven on-car (the
                       # OPT_DEBUG flash used it); the alternative blobB flasher used 0x1DC [MODELED].
MAX_BLOCKSIZE_PROGMODE = 65521


def _hex(b: bytes) -> str:
    return b.hex().upper()


def plan(container_size: int, lbn: int = LBN, max_block: int = MAX_BLOCKSIZE_PROGMODE) -> list:
    """The ordered sequence. Each item is (frame_hex_or_note, human label). Addr=0, size=container_size."""
    size = container_size
    # requestDownload 34 00 44 <addr:4> <size:4>
    rd = bytes([0x34, 0x00, ALFI]) + (0).to_bytes(4, "big") + size.to_bytes(4, "big")
    n_blocks = max(1, -(-size // (max_block - 2)))  # per-block payload = maxBlockLength minus the 2-byte SID+seq
    return [
        ("— enter programming mode —", ""),
        ("1003", "ExtendedSession"),
        ("222504", "read FlashTiming"),
        ("31010F0C03", "ActivateFlash (energy on) — abort if negative"),
        ("22100A", "read EnergyMode — MUST be non-zero (a gate, not just a read)"),
        ("8502", "DTC off"),
        ("280101", "CommControl: quiet"),
        ("3101100301", "SetExtMode 01 — abort if negative"),
        ("1003", "ExtendedSession again"),
        ("222504", "FlashTiming again"),
        ("1002", "ProgrammingSession — HU self-reboots (NRC 22 = abort); reopen socket, poll 22 F186 until byte[3]==02 (<=50 s)"),
        ("— authenticate (the shared L3 handshake — see docs/keys.md / nbtevo.l3) —", ""),
        ("2711", "SecurityAccess requestSeed (flash level 11) -> 67 11 <seed:8>"),
        ("2712 <KEY:132>", "sendKey: NOT sign-of-seed. sign MD5([UserID][Controller][seed]) e=3 LE; KEY = 00000020 || word-swapped 128B sig. YOUR L3 key (not shipped)"),
        ("— write (nothing touches the live image before transferExit) —", ""),
        ("2EF15A " + _hex(bytes(13)), "write fingerprint (13 zero bytes; its NRC is ignored)"),
        (f"3101FF000244{lbn:08X}06", f"eraseMemory (indicated form; LBN=0x{lbn:X} — file-copy: 0 verified, blobB flasher used 0x1DC; erase+check must match)"),
        (_hex(rd), f"requestDownload addr=0 (always) size={size} (0x{size:X})"),
        ("74 <lenFmt> <maxBlk…>", "reply: read maxNumberOfBlockLength (block payload = that minus 2)"),
        (f"36 <BSC> <block> x {n_blocks}", f"transferData, ~{n_blocks} blocks; BSC starts at 1, wraps FF->00; each -> 76 <BSC>"),
        ("37", "transferExit -> 77  (file-copy runs here; live path: effective next boot; staging path: on linkIStep)"),
        (f"31010202 12 44 {lbn:08X} 0000".replace(" ", ""), "checkMemory (trailing 0000 is a length const, NOT a CRC; failure is non-fatal)"),
        ("3101FF01", "checkProgrammingDependencies"),
        ("— teardown (run all of it, in order, even on abort) —", ""),
        ("3101100F", "ActivateApplicationMode FIRST; then poll 22 F186 until byte[3]==01 (<=40 s)"),
        ("1003 ; 31010F0C00 ; 22100A (loop)", "ExtendedSession -> EnergyOff -> read EnergyMode until ==0 (<=50 s)"),
        ("3101100300", "SetExtMode off"),
        ("280001", "CommControl: normal"),
        ("8501", "DTC on"),
        ("1101", "ECUReset — ONLY if EnergyMode and ExtendedMode both read clean; else do not reset"),
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--container", required=True, help="the patched .swdl to flash")
    ap.add_argument("--lbn", type=lambda x: int(x, 0), default=LBN)
    ap.add_argument("--max-block", type=int, default=MAX_BLOCKSIZE_PROGMODE)
    a = ap.parse_args(argv)

    size = Path(a.container).stat().st_size
    print(f"flash plan for {Path(a.container).name}  ({size} bytes, 0x{size:X})")
    print("target: the HU's own Ethernet node (direct route, fastest) or the FEM gateway, tester src 0xF4 -> 0x63")
    print("THIS PRINTS FRAMES ONLY — it sends nothing. See ../03-flashing-safely.md before flashing.\n")
    for frame, label in plan(size, a.lbn, a.max_block):
        if label == "":
            print(f"\n{frame}")
        else:
            print(f"  {frame:<40} {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
