# Freestanding QNX/armle-v7 samples

Two tiny programs that prove the build→run loop **without the QNX SDP**, built with the free
bare-metal ARM toolchain (`arm-none-eabi`):

- **`hello.S`** — a freestanding assembler sample.
- **`qwrite.c`** — the same in C (proves the compiler path, not just the assembler).

Both are static `ET_EXEC`, **ELF32 ARM EABI5 little-endian, soft-float**, linked at
`-Ttext=0x100000` (the load address the OEM `EXEC` uses), entry `_start`, **no libc and no startup
objects**. They talk straight to the kernel-call boundary — so they print on a QNX/ARM user-mode
emulator and on the head unit, with no C library involved.

```sh
pacman -S arm-none-eabi-binutils arm-none-eabi-gcc   # or your distro's equivalent
make                                                  # -> hello.elf, qwrite.elf
file hello.elf   # ELF 32-bit LSB executable, ARM, EABI5 … statically linked
```

## The two kernel calls they use

`svc #0`, immediate always 0, call number in `r12`; success returns at `svc+4`, error at `svc+8`.

| op | `r12` | registers | notes |
|---|---|---|---|
| write | `0x0b` `__KER_MSG_SENDV` | r0=coid(1=stdout), r1=&iov, r2=parts(1), r3=0, r4=0 | iov = `{u32 base, u32 len}`; msg = 16-byte `_io_write` header (`type=0x102`, `nbytes`@+4) + payload |
| exit | `0x2f` `__KER_THREAD_DESTROY` | r0=tid(-1 ⇒ whole process), r1=prio(-1), r2=status | |

That one `MsgSendv` of an `_IO_WRITE` message to connection id 1 is how a bare binary writes to
stdout; a user-mode emulator that decodes it at the resource-manager layer prints it with no libc.
This is why the freestanding path needs no SDP.

## Running them

Point `EMU` at your QNX/ARM user-mode emulator and `LIBC` at a `libc.so.3` carved from **your own**
firmware (see [../02-emulator-loop.md](../02-emulator-loop.md)); this repo ships neither:

```sh
make run EMU="python /path/to/your/qnxemu/run_trace.py" LIBC=/path/to/your/libc.so.3
# | hello from a hand-built QNX/ARM binary, running on our emulator
```

## The next step: a libc-linked binary

The freestanding trick is perfect for kernel-call logic, but the real target — a static HSFZ/UDS
client, or anything using sockets — links the QNX C library, which needs the licensed **QNX SDP
6.5.0**. See [../01-toolchain-and-abi.md](../01-toolchain-and-abi.md) for the `qcc -Vgcc_ntoarmv7le
-static` path. Build it `-static` and you get one drop-in file for the HU with no shared-lib deps.
