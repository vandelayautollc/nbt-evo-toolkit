# Flash & patching

Author and apply your own `.swdl` flash patches on your own head unit: enable the developer/debug
build (OPT_DEBUG), install your own FSC trust anchor (the blobB swap `fsc` needs), or make any other
surgical, length-preserving firmware change — through BMW's own authenticated flash state machine.

> ⚠️ **Highest-risk capability.** A corrupt or interrupted flash can leave a module unbootable. Only
> flash a vehicle you own, parked, with healthy battery voltage. Validate every patch offline first
> (`validate/check_patch.py`), understand the **revert** before you apply, and know your recovery
> backstop (serial/eMMC). See [LEGAL.md](../../LEGAL.md) and [03-flashing-safely.md](03-flashing-safely.md).

## The honest shape of this capability

Flashing is where a mistake bricks hardware, so — following the project's "instructions over
scripts" rule for on-car writes — the split is deliberate:

- **Offline, shipped and tested:** the container parser/extractor, the **patch authoring** tools
  (length-preserving file edit + the no-signature file-copy container builder + the filename
  convention), and a **validator** that refuses a bad patch (including one that still carries a
  signature, or edits a byte it shouldn't).
- **The flash itself:** a **flash-plan generator** (emits the exact ordered UDS frame sequence, but
  opens no socket and writes nothing) plus a precise **runbook**. The live write's SecurityAccess is
  signed with **your own L3 key** (recovered from your own PSdZData) using the shared seed→key
  construction in [`nbtevo.l3`](../../nbtevo/l3.py) — see [docs/keys.md](../../docs/keys.md) and
  [03-flashing-safely.md](03-flashing-safely.md). This toolkit ships no key and no turnkey flasher.

The patch you flash is a **minimal, no-signature file-copy container**, not an edited copy of a
stock `.bin`: the head unit rejects a signed container whose body was modified, but accepts a
signature-free container and routes its payload to an on-device file-copy job. See
[01-how-flashing-works.md](01-how-flashing-works.md).

## Read this section in order

1. **[01-how-flashing-works.md](01-how-flashing-works.md)** — the WOODOO/`.swdl` container, why the
   patch you flash omits the signature, and the flash state machine (prog session → auth → erase →
   download → transfer → exit → check → reset).
2. **[02-authoring-patches.md](02-authoring-patches.md)** — the two authoring steps (edit the file,
   wrap it into a no-signature file-copy container), the filename convention, the `CheckPathPrefix`
   path gate, and the two worked patches (OPT_DEBUG and the blobB trust-anchor swap).
3. **[03-flashing-safely.md](03-flashing-safely.md)** — the runbook: SecurityAccess with your own
   key, the fast direct-to-HU route, block-size, verify, and recovery.

## Tools

| Script | Does | Touches car | Status |
|---|---|---|---|
| `tools/container.py` | list/extract a WOODOO `.bin`/`.swdl`; pull out a payload; build a no-sig file-copy container | no | ✅ |
| `tools/patch.py` | `edit` a file length-preservingly, `build-filecopy` the flashable container, parse/discover patches | no | ✅ |
| `validate/check_patch.py` | prove the container is safe (parses to EOF, **no signature record**, minimal, sane TargetPath, only the intended bytes changed) | no | ✅ |
| `tools/flash_plan.py` | print the exact UDS flash sequence for a container (no socket) | no | ✅ |
| the flash itself | execute the plan over the diagnostic link | **flash** | runbook (03), proven on-car via the OPT_DEBUG flash; SA signer is `nbtevo.l3` + your own L3 key |

## The happy path (authoring, offline)

```bash
pip install -e .

# 1) edit the file: pull NBTCarHU out of your own SWFL container, swap the 128-byte blobB window
python capabilities/flash_and_patching/tools/patch.py edit \
    --from-container swfl_0000271a.bin --payload NBTCarHU \
    --offset 0x35A300 --bytes owner_blobB.bin -o NBTCarHU.patched

# 2) wrap it into the flashable no-signature file-copy container, named by convention
python capabilities/flash_and_patching/tools/patch.py build-filecopy \
    --file NBTCarHU.patched --target-path /fs/sda0/opt/car/bin/ --name NBTCarHU \
    --id ownerca --class swfl --sgbm 0000271A --version 007.051.002 -o .

# 3) prove it's safe before it goes anywhere near the car
python -m capabilities.flash_and_patching.validate.check_patch \
    --patched ownerca-swfl0000271A-007.051.002-apply.swdl \
    --stock-file NBTCarHU.patched.stock --offset 0x35A300 --len 128 --owner-blobB owner_blobB.bin

# 4) see exactly what the flash would send
python capabilities/flash_and_patching/tools/flash_plan.py \
    --container ownerca-swfl0000271A-007.051.002-apply.swdl
```

Then follow [03-flashing-safely.md](03-flashing-safely.md) to execute the plan on your own parked car.
