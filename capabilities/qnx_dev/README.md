# QNX development

Build your own native binaries for the head unit's **QNX** OS and run them on the HU — after
rehearsing on an emulator so you don't learn on the car. This underpins [`plugins`](../plugins/)
(a plugin `.so` is a QNX/ARM build) and lets you run your own diagnostic/utility tools on the unit.

> A dev-access capability: you copy a file over SSH and run it. No flash, no coded write. Owner's
> own car only — see [LEGAL.md](../../LEGAL.md). Respect the unit's file integrity (add files,
> don't overwrite signed ones — LMPC, see [docs/architecture.md](../../docs/architecture.md)).

## The target, in one line (the ABI gate)

**QNX Neutrino 6.5.0 SP1 · ELF32 ARM EABI5 little-endian · armv7-a · soft-float base AAPCS · QNX
triplet `ntoarmv7le` · GCC 4.4.2 / QNX SDP 6.5.0.** A binary that isn't this will not load. The
sample in [`sample/`](sample/) builds to exactly this — verify with `file`/`readelf` (see
[01-toolchain-and-abi.md](01-toolchain-and-abi.md)).

## Read this section in order

1. **[01-toolchain-and-abi.md](01-toolchain-and-abi.md)** — the ABI gate in detail, and the two
   build paths: freestanding (free `arm-none-eabi`, no SDP) and QNX-linked (licensed SDP 6.5.0).
2. **[02-emulator-loop.md](02-emulator-loop.md)** — the build→emulate loop: the kernel-call
   boundary, and standing up a QNX/ARM user-mode emulator against your own carved libc.
3. **[03-on-car.md](03-on-car.md)** — getting a binary onto the HU over SSH and running it.

## What's here

| Path | What | Status |
|---|---|---|
| `sample/hello.S`, `sample/qwrite.c`, `sample/Makefile` | freestanding "hello" (asm + C), builds with `arm-none-eabi`, no SDP | ✅ builds to the exact target ABI |
| `01/02/03.md` | toolchain + ABI, the emulator loop, on-car execution | ✅ |

## The discipline

**Static → emulator → car.** Each step is cheaper and safer than the next:

```sh
cd sample && make          # build freestanding — no SDP, no car, produces armle-v7 EABI5 soft-float
#   (rehearse framework-linked code on an emulator built from YOUR firmware — see 02)
#   (then copy the static binary to the HU over SSH and run it — see 03)
```

You supply your own QNX SDP (for libc-linked builds), your own emulator image/libc (carved from your
own firmware), and your own HU dev access. This repo ships the method, the ABI gate, and a sample —
no manufacturer SDK or firmware.
