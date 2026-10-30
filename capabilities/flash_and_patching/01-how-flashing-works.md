# 01 · How flashing works

Two things to understand: the **container** a flash payload travels in, and the **state machine**
that writes it. Both are reverse-engineered from the head unit's own flasher; the toolkit's
`container.py` parses the former and `flash_plan.py` emits the latter.

## The container (WOODOO / IOC-BOLO `.bin` / `.swdl`)

Each firmware file (`<class>_<sgbm>.bin.<version>`, class ∈ {btld, swfl, ibad, …}) is a
Harman **WOODOO** scripted-flash container: a uniform, byte-packed stream of 9-byte-header records
from offset 0, no separate file header.

```
offset size field
  +0    1   marker    0x01 stream-start · 0x02 descriptor (ASCII Key=Val; metadata) · 0x03/0x04 data
  +1    2   index     u16 LE — a descriptor and its data records share one index
  +3    4   length    u32 LE — body byte count that follows
  +7    1   segment   on 0x02: count of following data records · on data: 1-based ordinal
  +8    1   flags     constant 0x00
  < body: length bytes, immediately after the header, no padding >
```

A **descriptor** (`0x02`) carries `Name=…;Tag=…;TargetPath=…;` metadata; the **data records** after
it (same index) concatenate to that file's payload. `Tag=FIL` records reconstruct the on-disk file
tree (so the whole QNX userspace — including `NBTCarHU` — is addressable inside the container). Large
files split into 20,000,000-byte segments sharing one index. A stock container ends with the BMW SWE
**flash signature** block (`F0002000.nsw`, RSA-1024/MD5 over the image — the *flash* signature,
separate from coding and FSC).

**The patch you flash omits that signature.** The flash finalizer checks a "signature present" flag:
when a signature is present it is verified over the whole body, so a stock container you modified is
rejected. A freshly built container with **no signature record** short-circuits to ACCEPT and is
routed to the on-device file-copy job, which writes the payload to its `TargetPath`. That is why the
toolkit builds a minimal no-signature file-copy container rather than editing a signed `.bin` — see
[02-authoring-patches.md](02-authoring-patches.md).

`container.py list <file>` walks it to exact EOF; `locate_payload(file, "NBTCarHU")` returns where a
named payload lives inside the container; `extract_payload(file, "NBTCarHU", out)` writes that file
out so you can edit it and re-wrap it (see [02-authoring-patches.md](02-authoring-patches.md)).

## The flash state machine

The write is UDS/SWDL over the diagnostic link (HSFZ; [docs/01-transport-connect.md](../../docs/01-transport-connect.md)),
tester `0xF4` → head unit `0x63`. The proven order (what `flash_plan.py` prints):

```
— enter programming mode —
10 03                     ExtendedSession
22 2504                   read FlashTiming
31 01 0F0C 03             ActivateFlash (energy on)   — abort if negative
22 100A                   read EnergyMode             — MUST be non-zero (a gate, not just a read)
85 02 · 28 01 01          DTC off · CommControl quiet
31 01 1003 01             SetExtMode                  — abort if negative
10 03 · 22 2504           ExtendedSession again · FlashTiming again
10 02                     ProgrammingSession  → HU SELF-REBOOTS into the bootloader
                          (NRC 0x22 here = prep insufficient → abort)
                          reopen the socket, poll 22 F186 until byte[3]==0x02 (<=50 s, 1 s cadence)
— authenticate —
27 11 → 67 11 <seed:8>    SecurityAccess requestSeed (FLASH level 11 — not the coding level 01)
27 12 <KEY:132>           sendKey — the shared L3 seed→key construction, YOUR L3 key.
                          NOT "sign of the seed": sign MD5([UserID][Controller][seed]), raw e=3 LE,
                          KEY = 00 00 00 20 ‖ word-swapped 128-byte sig. See docs/keys.md (nbtevo.l3).
— write (nothing is committed until transferExit) —
2E F15A <13×00>           write fingerprint (13 zero bytes; its NRC is ignored)
31 01 FF00 02 44 <LBN:4> 06   eraseMemory (indicated form: method 02, no addr/size)
34 00 44 <addr:4=0> <size:4>  requestDownload (addr ALWAYS 0; size = whole container)
                              → 74 reply carries maxNumberOfBlockLength
36 <BSC> <block> × N      transferData (BSC starts at 1, wraps FF→00; block = maxBlock−2) → 76 <BSC>
37                        transferExit → 77
31 01 0202 12 44 <LBN:4> 0000  checkMemory (trailing 0000 is a length const, NOT a CRC; non-fatal)
31 01 FF01                checkProgrammingDependencies
— teardown (always run, even on abort; see 03) —
31 01 100F                ActivateApplicationMode  ← FIRST
   poll 22 F186 until byte[3]==0x01 (back in the app, <=40 s)
   loop: 10 03 → 31 01 0F0C 00 EnergyOff → read 22 100A until EnergyMode==0 (<=50 s)
31 01 1003 00 ExtModeOff · 28 00 01 CommNormal · 85 01 DTC on
11 01                     ECUReset — ONLY if EnergyMode and ExtendedMode both read clean
```

The `<LBN>` (logical block number) is **not** derived from the address — it's a block token. For a
file-copy container, **`0` is proven on-car** (it's what the OPT_DEBUG file-copy flash used); an
alternative UDS blobB flasher instead used `0x000001DC` (the `NBTCarHU` container record index), which
is `[MODELED]` and not the route that was exercised (see [02-authoring-patches.md](02-authoring-patches.md)).
**eraseMemory and checkMemory must carry the same LBN** (the ECU enforces it). The seed→key
construction and its exact wire format are in
[docs/keys.md](../../docs/keys.md) — getting them wrong returns NRC `0x13` (format) or `0x35` (bad
signature), not a silent failure.

Why this matters for safety:

- **Nothing touches the live image before `37 transferExit`.** Erase prepares the block; data streams
  in via `transferData`; the file-copy job writes the file at/after `transferExit`. An abort before
  `37` leaves everything intact, so a failed/aborted transfer is recoverable — the tooling and runbook
  treat pre-`37` aborts as safe. (*When* it goes live then depends on the `TargetPath`, not the patch:
  a **live** path (`/fs/sda0/opt/…`) is overwritten in place at `37` and takes effect on the **next
  boot**; a **staging** path (`/fs/sda0/repository/istep/opt/…`) is written to the repository copy and
  goes live only on a later `linkIStep` — [02](02-authoring-patches.md). A live write is `O_TRUNC`, so
  an interrupted live transfer can corrupt the file — keep the `-revert`.)
- **`10 02` reboots the HU into its bootloader.** Non-destructive and reversible on its own (it comes
  back), but it is the point of no quick return once you proceed to erase.
- **Teardown is not optional and not the doc's old short form.** It must `31 01 100F` *first*, settle
  the energy/mode registers, and issue `11 01` **only if they read clean** — an unconditional reset
  can strand the HU in programming/energy-on state. The full teardown is in [03](03-flashing-safely.md).
- **The authenticated path is the only one.** The HU verifies the SWE flash signature and gates the
  write behind SecurityAccess; you don't bypass it — you authenticate with your own L3 key.

## Routing (and why it's ~100× faster direct)

Flash through the FEM gateway works but its store-and-forward hop is the bottleneck. Connecting
straight to the **HU's own Ethernet node** (the IP from `22 17 2A`), target `0x63`, is far faster and
the HU answers there even across the programming-mode reboot. Use the gateway route only as a
fallback. The block size also matters: programming mode negotiates a large `maxNumberOfBlockLength`
(~64 KB, `MAX_BLOCKSIZE_PROGMODE = 65521`); the per-block payload is that minus the 2-byte SID+BSC.
If the HU instead advertises a small block (≤ ~4092, the app-mode regime), the transfer is far
slower — the large programming-mode block over the direct route is the bulk of the ~100× win.

Next: [02-authoring-patches.md](02-authoring-patches.md).
