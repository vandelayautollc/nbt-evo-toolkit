# 01 · Toolchain and the ABI gate

The single thing that decides whether a binary runs on the head unit is its ABI. Get it right and a
freestanding tool needs no licensed SDK at all; get it wrong and nothing loads.

## The ABI gate (confirmed from the HU's own binaries)

| Property | Value |
|---|---|
| OS | QNX Neutrino RTOS **6.5.0 SP1** (`procnto-smp-instr`, loader `/usr/lib/ldqnx.so.2`, `libc.so.3`) |
| CPU / ISA | dual ARM Cortex-A15, **ARMv7-A**, little-endian |
| Object | **ELF32, LSB, ARM, EABI5** ("Version5 EABI") |
| Float ABI | **soft-float base AAPCS** — FP args in core registers (VFP/NEON *instructions* are used, but the *call* ABI is soft-float) |
| QNX triplet | **`ntoarmv7le`** (`qcc -Vgcc_ntoarmv7le`) |
| OEM compiler | **GCC 4.4.2** (the QNX SDP 6.5.0 compiler — pins the SDP version; matters for the C++ ABI, see `plugins`) |
| Load address | OEM `EXEC` binaries load at `0x00100000` (non-PIE); shared libs are PIC |

Verify any candidate binary:

```sh
file your.elf       # want: ELF 32-bit LSB executable, ARM, EABI5 … statically linked
readelf -h your.elf # Flags: … Version5 EABI, soft-float ABI   ← the two that bite
```

Hard-float (VFP-ABI), AArch64/ARMv8, or glibc/Linux binaries will **not** load. The `sample/`
builds produce exactly this ABI — that's the reference.

## Path A — freestanding (no SDP, free toolchain)

For a tool that only needs kernel calls (write, exit, and other `svc #0` operations), build with the
**free bare-metal ARM toolchain** and talk straight to the kernel-call boundary — no libc, no
startup objects:

```sh
pacman -S arm-none-eabi-binutils arm-none-eabi-gcc
cd sample && make          # hello.elf (as+ld) and qwrite.elf (gcc), static armle-v7 EABI5 soft-float
```

This is enough for kernel-call demos and simple utilities, and it runs on the emulator
([02-emulator-loop.md](02-emulator-loop.md)) and the HU with nothing else installed. See
[`sample/README.md`](sample/README.md) for the two kernel calls it uses.

## Path B — QNX-linked (licensed SDP 6.5.0)

For anything that links the QNX C library — sockets (a static HSFZ/UDS client), threads, the HMI
frameworks (plugins) — you need the **QNX SDP 6.5.0** (BlackBerry/QNX-licensed; you supply your
own). Then:

```sh
source /path/to/your/qnx650/qnxsdp-env.sh        # sets QNX_HOST / QNX_TARGET + the toolchain on PATH
qcc -Vgcc_ntoarmv7le -static your.c -o your.elf   # one drop-in file, no shared-lib deps on the HU
```

- Prefer **`-static`** for on-car tools: a single file with no shared-lib dependencies.
- `qcc` wraps a FLEXlm license check; the underlying `ntoarmv7-gcc`/`ntoarmv7-ld` need no license, so
  a license-less install can still build by invoking those directly (with the right crt objects and
  `--dynamic-linker /usr/lib/ldqnx.so.2` for a dynamic build).
- A Linux-host SDP may ship only the x86 *target* sysroot; the **ARM target package** (or generating
  ARM link stubs from your firmware's exported symbols) is what a libc-linked ARM build needs.

## C++ (for plugins)

Plugin `.so`s are C++ and must match the OEM **GCC 4.4 C++ ABI** (name mangling, vtable layout). The
[`plugins`](../plugins/) SDK covers the C++ ABI and the exact `ntoarm-g++` build; it depends on this
same toolchain.
