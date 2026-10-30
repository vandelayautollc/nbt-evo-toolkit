# 02 · The build → emulate loop

Rehearse off-car. A QNX/ARM **user-mode** emulator runs your binary — ARM instructions plus a QNX
personality (kernel calls + resource-manager messages backed by the host filesystem) — on x86-64
Linux, so you iterate in seconds without touching the car. The car is only for the final
confirmation.

> User-mode means you emulate the **process**, not the OMAP5432 SoC — no CPU-peripheral or GPU
> model. That is plenty for logic, kernel calls, file and socket I/O, and framework bring-up; it is
> not for anything that renders pixels on the real GPU.

## The kernel-call boundary (what the emulator must model)

A QNX process reaches the kernel through `svc #0`, with the **call number in `r12`** (success
returns at `svc+4`, error at `svc+8`). The two calls the samples use:

| op | `r12` | meaning |
|---|---|---|
| `0x0b` | `__KER_MSG_SENDV` | send a message; a `MsgSendv` to connection id 1 carrying an `_IO_WRITE` message is stdout |
| `0x2f` | `__KER_THREAD_DESTROY` | with tid = -1, exit the whole process with a status |

An emulator that decodes a `MsgSendv(_IO_WRITE)` at the resource-manager layer prints guest stdout
with **no C library involved** — which is why `sample/` runs on it without the SDP. Real programs
go further: `open()`/`read()`/`write()` are resource-manager messages (`_IO_*` wire layouts) to
path-manager connections; sockets reach a `socket` resource manager. A useful emulator therefore
models: the **syspage/cpupage/TLS** bootstrap, ELF load + relocations + the `auxv` stack, the
`svc` dispatch table, and the `_IO_*` resmgr protocol, with libc loaded from your own firmware.

## Standing one up (from your own firmware)

The emulator is built around a dynamic-recompiler/interpreter ARM core (e.g. the Qiling/Unicorn
engine) plus a QNX personality. It loads **`libc.so.3` carved from your own firmware** (this repo
ships no firmware) so the guest's real OEM libc runs. A sensible bring-up ladder:

1. a freestanding binary that writes + exits (the `sample/` — proves the `svc`/resmgr path);
2. an SDP-compiled freestanding binary (proves the compiler path);
3. a libc-linked binary that `printf`s (proves ELF load + relocations + libc's call surface);
4. file I/O against a host-backed VFS, then sockets;
5. framework-linked code (the HMI/MoCCA libraries) for plugin bring-up.

Run the samples once you have an emulator and a carved libc:

```sh
cd sample
make run EMU="python /path/to/your/qnxemu/run_trace.py" LIBC=/path/to/your/libc.so.3
```

## Why rehearse here

- **Speed:** rebuild-and-run is seconds; a car round-trip is minutes and risks the unit.
- **Observability:** you see every kernel call and message — the fastest way to find why a binary
  faults or an `open()` returns the wrong errno.
- **Safety:** a crash in the emulator costs nothing. Only move to the HU
  ([03-on-car.md](03-on-car.md)) once the logic is right.

This repo ships the method and the sample, not the emulator engine or any firmware — you build the
emulator around your own carved binaries. (If you don't need framework bring-up, a freestanding tool
needs no emulator at all: build it and run it straight on the HU.)
