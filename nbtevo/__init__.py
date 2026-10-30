"""
nbtevo — shared primitives for the NBT EVO Toolkit.

Owner-authorized vehicle diagnostics/coding for the operator's OWN car only. See LEGAL.md.

Modules:
  consent  — the ownership gate (call before any key-recovery or vehicle write)
  srec     — Motorola S-record codec for NCD coding containers
  hsfz     — ENET/HSFZ discovery + transport (F-series; not DoIP)
  uds      — UDS services + SVK/SGBM decoding (bootloader/CAFD identification)
  keys     — shared key recovery (NCD coding key + L3 SecurityAccess key); see docs/keys.md
"""
__all__ = ["consent", "srec", "hsfz", "uds", "keys", "l3"]
__version__ = "0.1.0"
