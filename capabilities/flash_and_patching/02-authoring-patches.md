# 02 · Authoring patches

A patch is a `.swdl` flash container plus a naming convention that says exactly what it fits. The
container you flash is a **minimal, no-signature file-copy container**: it carries one file and a
`TargetPath`, and because it has **no signature record** the head unit routes it to its on-device
file-copy job, which writes your file onto the live (or staged) filesystem. `patch.py build-filecopy`
builds it; `check_patch.py` proves it before you flash.

## Why a no-signature file-copy container (and not an edited `.bin`)

A stock firmware container (`swfl_0000271a.bin.007_051_002`, etc.) ends with the BMW SWE **flash
signature** (`F0002000.nsw`, RSA-1024/MD5 over the whole image). The head unit's flash finalizer
checks a "signature present" flag: **if a signature is present it is verified over the entire body**,
so a stock container whose bytes you modified — even one byte, even length-preservingly — **fails
that check and is rejected**. You cannot surgically edit a signed `.bin` and flash it.

What you *can* do is deliver a **fresh container with no signature record at all**. With no signature
present, the finalizer short-circuits to ACCEPT and hands the stream to the file-copy job, which
writes the payload to `<TargetPath>/<Name>` — gated only by a path check (see "The path gate" below).
This is the mechanism both worked patches use. It is reverse-engineered from the head unit's own
flasher and the two proven owner tools.

So the file you flash is small (envelope + descriptor + your one file), not the multi-hundred-MB
stock image, and it is built, not edited.

## The two authoring steps

**Step 1 — edit the file (length-preserving).** Get the stock file out of your own container and
change only the bytes you intend. `patch.py edit` does this and keeps the file length identical:

```bash
# pull NBTCarHU out of your own extracted stock container, swap the 128-byte blobB window
python patch.py edit --from-container swfl_0000271a.bin --payload NBTCarHU \
    --offset 0x35A300 --bytes owner_blobB.bin -o NBTCarHU.patched
# (--from-container also writes NBTCarHU.patched.stock — keep it to build the -revert)
```

`edit` writes exactly `len(--bytes)` at `--offset` and nothing else, so the file stays the same
length and only your window changes. (You can also pass `--file` to edit a standalone file you
already have, e.g. a `starter.cfg` you modified another way.)

**Step 2 — wrap it into the flashable container**, named by the convention below:

```bash
python patch.py build-filecopy --file NBTCarHU.patched \
    --target-path /fs/sda0/opt/car/bin/ --name NBTCarHU \
    --id ownerca --class swfl --sgbm 0000271A --version 007.051.002 -o .
# -> ownerca-swfl0000271A-007.051.002-apply.swdl
```

**Always validate before flashing** — this is the gate that catches a corrupt build, an accidental
signature, a stray edit, or a wrong TargetPath:

```bash
python -m capabilities.flash_and_patching.validate.check_patch \
    --patched ownerca-swfl0000271A-007.051.002-apply.swdl \
    --stock-file NBTCarHU.patched.stock --offset 0x35A300 --len 128 --owner-blobB owner_blobB.bin
```

It checks the container **parses to EOF**, carries **no signature record**, is **minimal** (envelope
+ one `Tag=FIL` payload), has a **sane TargetPath**, and — given the stock file and window — that the
payload differs from stock **only inside your window** (and, with `--owner-blobB`, that the window is
now your modulus and not the stock value). Build the matching `-revert` the same way from the *stock*
file (`--revert` on `build-filecopy`), so you can always put the file back.

## The filename convention (the authority on compatibility)

```
<id>-<class><SGBM id>-<version>-<apply|revert>.swdl
ownerca-swfl0000271A-007.051.002-apply.swdl
ownerca-swfl0000271A-007.051.002-revert.swdl
```

- **id** — your name for the patch (letters/digits/underscore, no `-`).
- **class** — the flash area's SVK process class: `swfl`, `btld`, `ibad`, `swfk`, … .
- **SGBM id** — 8 hex, the area's id.
- **version** — a 1–3 part prefix of the area version it applies to: `007.051.002` that version
  only, `007.051` any `007.051.x`, `007` any `007.x.x`.
- **apply / revert** — write the patch, or write the stock file back.

Nothing in the tooling knows a patch by name; patches are **discovered** by this convention
(`patch.py discover`) and offered only when the head unit's SVK has the target area at an applicable
version. The `class`/`SGBM`/`version` you pass describe the area whose file you're replacing (for
NBTCarHU that's the `swfl 0000271A` application area) — match them to your own SVK before flashing.

## The path gate (`CheckPathPrefix`) — where a file-copy patch may land

The file-copy job runs the payload's `TargetPath` through a `CheckPathPrefix` check before writing.
What that check enforces depends on how the job was started:

- The allowed-prefix string is **not hard-coded** — it comes from the file-copy service's process
  arguments. On this platform those arguments are **empty**, so the length-gated prefix compare is
  **skipped entirely** and any absolute `TargetPath` is accepted (verified by static RE of the
  service binary and its launch config). **Confirm this on your own unit** — a differently configured
  unit could set a non-empty prefix.
- Even with a non-empty prefix set, the check is a literal prefix match plus two guards: the path
  must **not contain `../`**, and the character right after the prefix must be `/`. An absolute path
  under the prefix with no `../` passes.

So keep `TargetPath` **absolute, free of `../`, and ending in `/`** (the validator enforces all
three). The known-good destinations:

| TargetPath | Write model | Effect |
|---|---|---|
| `/fs/sda0/opt/car/bin/` · `/fs/sda0/opt/sys/etc/` … (`/fs/sda0/opt/…`) | **live-direct** | overwrites the live file in place (`O_TRUNC`), effective on the **next boot** |
| `/fs/sda0/repository/istep/opt/…` | **staged** | writes the repository copy; a separate `LinkManager` `linkIStep` (not over the diagnostic bus) promotes it live |

> ⚠️ **Live-direct is a torn-write risk.** `O_TRUNC` empties the live file at transfer start; an
> interrupted transfer corrupts the live file. Keep the stock file (to re-flash via `-revert`) and a
> serial/eMMC backstop, and prefer doing it in programming mode. The staged path leaves the live file
> untouched until promotion, but needs that extra `linkIStep` step the diagnostic bus can't do.

## What `<LBN>` the flash carries

The erase/checkMemory frames carry a logical block number. For a file-copy container, **`LBN 0` is
proven on-car** — it's what the OPT_DEBUG file-copy flash used, and that flash authenticated,
committed, and brought up the dev/SSH surface afterward. An alternative UDS blobB flasher instead
used `0x000001DC` (the container's NBTCarHU record index); that value is `[MODELED]` and was **not**
the route actually exercised (see "The proven route for blobB" below), so use `LBN 0` for a file-copy
container. **eraseMemory and checkMemory must carry the same LBN** (the ECU enforces it), and a
checkMemory failure on the file-copy route is non-fatal (see [03](03-flashing-safely.md)).

## Worked patch 1 — blobB trust-anchor swap (for `fsc`)

Replace the 128-byte FSC-verify modulus inside `NBTCarHU` with your own, so your own-signed FSCs are
accepted. Step 1: `edit --from-container <your swfl> --payload NBTCarHU --offset 0x35A300 --bytes
owner_blobB.bin` (the `owner_blobB.bin` is from `fsc`'s `keygen`). Step 2: `build-filecopy
--target-path /fs/sda0/opt/car/bin/ --name NBTCarHU` (live-direct) — or the `…/repository/istep/opt/car/bin/`
staging path for the safer A/B route. It is length-preserving (128→128) and leaves coding working,
because coding is keyed by a *different, disjoint* key. See
[../fsc/02-blobB-and-minting.md](../fsc/02-blobB-and-minting.md).

> **The proven route for blobB is SSH, not this flash.** Once OPT_DEBUG is on (patch 2), the dev
> shell is up and the simplest, proven way to swap blobB is a plain in-place file edit over SSH
> (`mount -uw`, `dd` the 128 bytes, `mount -ur`) — see [docs/staging-files-over-ssh.md](../../docs/staging-files-over-ssh.md)
> and the `fsc` capability. Use *this* UDS file-copy flash for blobB only if you want to swap it
> **without** a dev shell; its `LBN 0x1DC` from the alternative blobB flasher is `[MODELED]` — use
> `LBN 0` as for any file-copy container.

## Worked patch 2 — OPT_DEBUG (developer/debug build) — the proven flash

OPT_DEBUG turns on the head unit's developer/debug build (what unlocks the dev/SSH surface the
`qnx_dev` and `plugins` work builds on). **This is the flash that has actually been run on this car**
(over the UDS route in both a Pi tool and the Android app): after it committed and the HU rebooted,
`sshd`/`telnetd`/`qconn` came up — which is the end-to-end proof of the whole state machine, the L3
handshake, the fingerprint, and `LBN 0`. The file is `starter.cfg` with a startup flag flipped
(STOP → RUN); wrap it with `--target-path /fs/sda0/opt/sys/etc/ --name starter.cfg` (live-direct,
`LBN 0`). The modified `starter.cfg` need not be length-preserving — it's a whole-file copy — but keep
the change minimal and keep the byte-exact stock `starter.cfg` to build the `-revert`.

Both patches are the same shape: one small file, delivered by a no-signature file-copy container to a
known-good `TargetPath`, reversible by flashing the stock file back. Next:
[03-flashing-safely.md](03-flashing-safely.md).
