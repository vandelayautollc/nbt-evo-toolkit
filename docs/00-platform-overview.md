# 00 · Platform overview — is this an NBT EVO, and what is it?

Before using any capability, confirm you are looking at an **NBT EVO** and understand the stack it
runs. Everything downstream (addresses, container formats, keys) depends on it.

> This is the quick orientation. For the **deep map** — processors, OS/ABI, the HMI engine stack,
> the filesystem, and what each firmware binary is responsible for — see
> **[architecture.md](architecture.md)**, and **[investigation-playbook.md](investigation-playbook.md)**
> for how to answer questions the capability folders don't cover.

## Identifying the head unit

The reliable way is to read it from the car, not to guess from the model year. Connect (see
[01-transport-connect.md](01-transport-connect.md)) and read the head unit's **SVK** (`22 F1 01`)
at diagnostic address **0x63**. The SVK lists the module's software as SGBM ids; the one that
matters most is the **bootloader (BTLD)**.

| BTLD id | Base variant | Head unit |
|---|---|---|
| `00001FFD` | `HU_NBT2` | **NBT EVO** (this toolkit's target) |
| (earlier) | `HU_NBT` | NBT (not EVO) — methods rhyme, specifics differ |
| (entry) | `HU_ENTRY*` | Entry / EntryNav — different SoC |
| (later) | `HU_MGU` | MGU (iDrive 7/8) — out of scope |

`capabilities/coding/tools/identify_btld.py` does this for you and prints the BTLD and live CAFD.
If the BTLD is not `00001FFD`, stop and recalibrate: the rest of this repo is written for the EVO.

## The hardware stack

The NBT EVO head unit is a multi-processor module:

- **OMAP** (TI OMAP, ARM Cortex-A) — runs the **QNX** OS and the HMI ("iDrive") on top of BMW's
  **MoCCA** application framework. This is where coding is consumed, the UI lives, and where
  plugins and custom 3D vehicle models run.
- **Jacinto** (TI DRA7xx) — media/graphics/audio processing and the diagnostics dispatcher.
- **V850 / RH850** (the "IOC", a Renesas automotive MCU) — the always-on gateway between the HU
  and the car's CAN buses, and the keeper of the **durable** coding/nvram tier.

Key consequence, remembered the hard way: a byte you poke into the HU's live RAM or a shell's
volatile store is **not durable**. The durable tier lives on the V850 and is only committed on a
controlled shutdown or a signed-diagnostic write. Durable coding therefore goes through the
**signed UDS coding path**, not a shell. See `capabilities/coding/`.

## How diagnostics reach it

F-series cars use **HSFZ over Ethernet (ENET)** — not DoIP. A tester (your laptop/Pi/phone)
reaches the car through the OBD-II port with an ENET cable, or over the local Ethernet segment.
The **FEM** body gateway (diag `0x10`) routes requests to every module by the UDS target byte; the
NBT EVO answers at **0x63**. The HU is itself an Ethernet ECU behind the FEM's Ethernet switch, and
also exposes its own Ethernet endpoint (useful — and faster — for HU-only flash/coding work). Full
detail in [01-transport-connect.md](01-transport-connect.md).

There is also a **QNX dev interface** on the HU (a second IP, with an SSH service) that is separate
from the diagnostic endpoint. It is relevant to QNX development and plugins, not to coding/FSC. See
`capabilities/qnx_dev/`.

## The ids that drive everything

Two live-read identifiers decide almost every downstream choice. Read them first, never assume:

- **BTLD id** (`SVK` → `BTLD`): selects which **coding signing key/scheme** applies, and which
  bootloader a flash container must match. This is the hinge of the whole platform — see
  `capabilities/coding/02-signing-model.md`.
- **CAFD id + version** (`22 30 0F`, else `SVK` → `CAFD`): selects which **coding layout** to
  decode and which definitions map applies. On this class of car the live CAFD is `00001EF6`.

## What you'll need from your own licensed data

This toolkit ships no BMW data. For coding you need your own **PSdZData** (BMW's config/firmware
distribution) so the scripts can locate your CAFD and recover your own signing key. Which files,
and how to confirm you have the right ones, is in [psdzdata-manifest.md](psdzdata-manifest.md).
