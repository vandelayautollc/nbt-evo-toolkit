# Freestanding QNX/armle-v7 samples — build with the FREE bare-metal ARM toolchain
# (arm-none-eabi), NO QNX SDP required. They talk straight to the kernel-call boundary
# (svc #0, call number in r12), so they run on a QNX/ARM user-mode emulator and on the HU.
#
#   make            # build hello.elf (asm) and qwrite.elf (C)
#   make run        # build + run under your emulator (set EMU + LIBC — see ../02-emulator-loop.md)
#
# For a real libc-linked binary (sockets, an HSFZ/UDS client) you need the licensed QNX SDP 6.5.0:
#   qcc -Vgcc_ntoarmv7le -static ...     (see ../01-toolchain-and-abi.md)
#
# Toolchain:  pacman -S arm-none-eabi-binutils arm-none-eabi-gcc  (or your distro's equivalent)

AS      = arm-none-eabi-as
LD      = arm-none-eabi-ld
CC      = arm-none-eabi-gcc
ASFLAGS = -march=armv7-a -EL
LDFLAGS = -EL -Ttext=0x100000 -e _start
CFLAGS  = -march=armv7-a -marm -O2 -ffreestanding -nostdlib -nostartfiles \
          -fno-stack-protector -static -Wl,-Ttext=0x100000 -Wl,-e,_start

# Point these at YOUR emulator and a libc.so.3 carved from YOUR own firmware (see ../02).
EMU  ?= @echo "set EMU to your QNX/ARM emulator run command (see ../02-emulator-loop.md); then: make run EMU=... LIBC=..." #
LIBC ?= /path/to/your/extracted/libc.so.3

all: hello.elf qwrite.elf

hello.elf: hello.S
	$(AS) $(ASFLAGS) -o hello.o hello.S
	$(LD) $(LDFLAGS) -o $@ hello.o

qwrite.elf: qwrite.c
	$(CC) $(CFLAGS) -o $@ qwrite.c

run: all
	$(EMU) hello.elf  --libc $(LIBC) --count 2000 --quiet
	$(EMU) qwrite.elf --libc $(LIBC) --count 5000 --quiet

clean:
	rm -f *.o hello.elf qwrite.elf
.PHONY: all run clean
