# 03 · Flashing safely (the runbook)

The car-touching step. Do it only on a vehicle you own, parked, ignition/terminal state stable, with
healthy battery voltage. Have your **stock container** (for the `-revert`) and your recovery backstop
ready *before* you start. This is a runbook, not a one-command tool — the brick-riskiest operation
deserves deliberate steps.

## Before you connect

1. **Confirm the target matches your car** — read the SVK (`22 F1 01`):
   - **Bootloader must be `00001FFD`.** The L3 key is bound to this BTLD; another bootloader refuses
     SecurityAccess outright, and the whole key story assumes it ([docs/versioning.md](../../docs/versioning.md)).
   - **The patch's flash area (process class + SGBM id) must exist in the SVK at a version the patch
     declares.** The filename convention encodes this and `check_patch.py` / `patch.py discover`
     enforce it. A live-direct patch (OPT_DEBUG) built for the wrong software version flips a flag the
     wrong image doesn't understand and **fails the next boot** — this is a real brick path, so match
     the version before you flash.
2. **Validate the patch** — `check_patch.py` must pass (parses to EOF, same size, no stray changes).
   A container that fails this will not be flashed.
3. **Have the revert** — build the `-revert` patch (stock bytes) now, so a known-good restore is one
   flash away. (For an A/B-staged patch the inactive slot is also a fallback — [02](02-authoring-patches.md).)
4. **Know your backstop** — the ultimate recovery is out-of-band (serial / eMMC re-image). If you
   cannot recover the module out-of-band, do not flash.
5. **Get your SecurityAccess key** — the flash unlock (`27 11`/`27 12`) uses your module's **L3 key**
   — the *same* key the coding write uses. Recover it: `python -m nbtevo.keys --btld <id> --kind l3
   -o l3_key.json`. The seed→key is **not** "sign the seed": it's the shared L3 construction
   (MD5 of `[UserID][Controller][seed]`, raw e=3 LE, `00000020` + per-word-swapped 128-byte sig),
   implemented in [`nbtevo.l3`](../../nbtevo/l3.py) — see [docs/keys.md](../../docs/keys.md). The
   toolkit ships no key and no turnkey flasher; you sign the seed with your own recovered key.

## Connect

Prefer the **direct-to-HU route**: read the HU's own IP from `22 17 2A`, then open an HSFZ session
straight to that node, target `0x63` ([docs/01-transport-connect.md](../../docs/01-transport-connect.md)).
It is far faster than the gateway and answers in the bootloader across the programming reboot. Use
the FEM gateway route only as a fallback.

## Execute the plan

`flash_plan.py --container <patch>.swdl` prints the exact ordered frames. Send them in order:

1. **Enter programming mode** — `10 03` → `22 2504` → `31 01 0F0C 03` (energy on; abort if negative)
   → `22 100A` (**EnergyMode must read non-zero** — it's a gate) → `85 02` / `28 01 01` →
   `31 01 1003 01` → `10 03` / `22 2504` → `10 02`. The HU **self-reboots into its bootloader**;
   **reopen the socket** and poll `22 F186` until byte[3]==`0x02` (≤50 s, ~1 s cadence) before
   continuing. (`10 02` returning NRC `0x22` = prep insufficient → abort.) Entering prog mode is
   itself reversible.
2. **Authenticate** — `27 11` → `67 11 <seed:8>`; build the key with your L3 key via the shared
   construction ([`nbtevo.l3`](../../nbtevo/l3.py) / [docs/keys.md](../../docs/keys.md)) and send
   `27 12 <132-byte KEY>`. A `67 12` means you're in. NRC `0x13` = wire-format wrong (the `00000020`
   prefix / word-swap), `0x35` = bad signature, `0x36` = locked (wait the `0x37` delay).
3. **Write** — `2E F15A <13×00>` fingerprint (its NRC is ignored) → `31 01 FF00 02 44 <LBN:4> 06`
   eraseMemory → `34 00 44 <addr=00000000> <size=whole container>` requestDownload (read
   `maxNumberOfBlockLength` from the `74` reply) → `36 <BSC> <block>` ×N transferData (**BSC starts at
   1**, wraps `FF`→`00`; each `76 <BSC>` echoes it) → `37` → `77` transferExit. Use **`LBN 0`** for a
   file-copy container (proven on-car via the OPT_DEBUG flash; the alternative blobB flasher's `0x1DC`
   is `[MODELED]` — [02](02-authoring-patches.md)); erase and checkMemory must match. **The file is
   written at `37`** — if anything fails before it, abort; nothing was written.
4. **Verify** — `31 01 0202 12 44 <LBN:4> 0000` checkMemory (the trailing `0000` is a length const,
   **not** a CRC — don't compute one; a checkMemory failure is **non-fatal**, log it and continue) and
   `31 01 FF01` checkProgrammingDependencies.
5. **Teardown (do all of it, in order — even if you aborted):**
   1. `31 01 100F` **ActivateApplicationMode first** (settles the EnergyMode window).
   2. Reopen the socket; poll `22 F186` until byte[3]==`0x01` (back in the app, ≤40 s).
   3. Loop: `10 03` → `31 01 0F0C 00` EnergyOff → read `22 100A` **until EnergyMode==0** (≤50 s, ~3 s).
   4. `31 01 1003 00` ExtModeOff → `28 00 01` CommNormal → `85 01` DTC on → read `22 100E`.
   5. `11 01` ECUReset **only if EnergyMode and ExtendedMode both read clean** — otherwise do **not**
      reset (an unconditional reset can strand the HU in programming/energy-on state); re-run the loop
      or power-cycle instead.

Pacing: programming mode negotiates a large block (~64 KB; the per-block payload is
`maxNumberOfBlockLength − 2`). Keep a background TesterPresent (`3E 80` functional to `0xDF`, ~every
1 s) alive during the write. Honour `7F … 78` responsePending by **extending** the receive window
(P2\* ≈ 6.5 s, with an absolute ~120 s ceiling) — erase and checkMemory can emit `0x78` for a long
time. Per-block: NRC `0x73` (wrongBlockSequenceCounter) means the ECU already advanced — treat it as
success; `0x21`/`0x7F` → brief wait and resend (≈6 tries); any other NRC → fatal abort.

## Confirm it worked

There is no raw read-back of the written file over the bus ([fsc §65]). Confirm **functionally**:

- **OPT_DEBUG**: the developer surface/behavior the patch enables is now present.
- **blobB swap**: apply an owner-signed FSC and watch the feature activate — it can only verify if
  the installed modulus is now yours (see [../fsc/03-apply-and-read.md](../fsc/03-apply-and-read.md)).
  Coding should still work (disjoint key); a quick coding read/verify confirms it.

## If it goes wrong

- **Abort before `37 transferExit`** → nothing was written; run the teardown, power-cycle, retry.
- **Bad write, by TargetPath:**
  - **live path (`/fs/sda0/opt/…`)** — the file is overwritten in place at `37` but takes effect only
    on the **next boot**, so before you reboot you still have a working system; flash the `-revert`
    (stock file) to put it back. If you already rebooted into a bad file, re-flash the `-revert` from
    the bootloader. (A live write is `O_TRUNC`: an interrupted transfer can leave the file truncated —
    the `-revert` is your fix, which is why you keep the stock file.)
  - **staging path (`/fs/sda0/repository/istep/opt/…`)** — only the repository copy was written; the
    **live file is untouched** until a `linkIStep` promotes it, so you simply don't promote a bad one
    / re-flash the correct `apply` first.
  The module stays in or returns to the bootloader for another attempt as long as it still answers.
- **No diagnostic answer at all** → the out-of-band backstop (serial / eMMC). This is why you confirm
  recovery *before* flashing.

## Status

This sequence is **proven on-car**: the OPT_DEBUG file-copy flash was run over the UDS route (in both
a Pi tool and the Android app), authenticated with the L3 handshake, committed, and brought up the
dev/SSH surface after reboot — exercising the whole state machine, `LBN 0`, the fingerprint, and the
teardown end-to-end. The offline authoring + validation + plan are shipped and tested here; the live
write is this runbook plus your own L3 key. A tested one-command flasher is intentionally not shipped
(same stance as the coding write path and the custom-car installer) — the brick-riskiest step stays a
deliberate, readable sequence.
