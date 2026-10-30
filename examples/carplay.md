# Worked example — activating Apple CarPlay

> **Your own car only.** CarPlay on the NBT EVO is a factory option (SALAPA **6CP**, "Smartphone
> Integration"). Enabling a feature you don't hold a BMW licence for may breach your agreement with
> BMW — that's between you and BMW. This walks the *mechanism* end-to-end on a unit **you own**; it
> is not for cars you don't, and it does not defeat any safety, theft, or emissions control.

CarPlay is the cleanest example of a feature that needs **two** independent things in place at once,
which is why it's the first worked example:

1. **Entitlement** — an **FSC** (feature code) for the CarPlay application number. This is the
   licence the firmware checks.
2. **Coding** — the signed coding bit the head unit checks before it offers CarPlay
   (`CARPLAY_SWT`). The firmware's CarPlay check reads that one bit and requires the FSC as well.
   A known-working car also sets one more bit whose role is unproven (§2).

Set only one half and nothing happens: entitlement without coding = licensed but not wired;
coding without entitlement = wired but the licence check fails. This example lists **both** halves
exactly, in order, and how to confirm each took.

It spans two capabilities — [`fsc`](../capabilities/fsc/) for the entitlement and
[`coding`](../capabilities/coding/) for the bits. Read those for the full mechanism; this page is
the recipe that combines them.

---

## 0 · Before you touch anything

- **Hardware reality check.** NBT EVO CarPlay runs **wired over USB** and needs the Apple **MFi
  authentication** path on the media USB port. Coding cannot conjure hardware: if your car has no
  media USB port / no MFi auth chip, the coding bits won't produce CarPlay. Cars built with the USB
  media interface (most 2016+) have it. This recipe is **wired only**: no wireless CarPlay path was
  found on the NBT EVO.
- **Back up your coding.** `python -m capabilities.coding.tools.read_coding --host <HU> -o backup.ncd`.
  This is your one-command revert.
- **Know your CAFD version.** The coordinates below are from CAFD `00001EF6` (layouts `006.048.013`
  and `006.064.014`). The tools read the version off the car; confirm your unit matches before
  trusting fixed coordinates — see [coding/04-definitions.md](../capabilities/coding/04-definitions.md).

---

## 1 · Entitlement — the CarPlay FSC (AppNo `0x0143`)

CarPlay's application number is **`0x0143`** (323) — see [fsc/catalog.md](../capabilities/fsc/catalog.md).

First **read what's already installed** (safe, no key): if your unit already carries a valid
BMW-signed CarPlay FSC, you're done with this half — skip to coding.

```
# read installed FSC state; look for AppNo 0x0143 active (see fsc/03-apply-and-read.md)
python capabilities/fsc/tools/fsc.py parse --fsc <dumped>.fsc      # decode a token you read back
```

If it's **not** present, you mint and apply your own under your own trust anchor (blobB). This is
the owner-CA path: you install **your** blobB so the unit accepts **your** signatures, then mint a
CarPlay FSC against it.

> **Before overwriting blobB, check whose anchor is already there** — a used unit may carry a
> genuine BMW anchor or *someone else's* owner-CA swap, which your overwrite would strand. Read a
> couple of installed FSCs and run `fsc.py whosigned` (see
> [fsc/03-apply-and-read.md](../capabilities/fsc/03-apply-and-read.md#who-signed-this-units-fscs-do-this-before-you-overwrite-blobb)).

```
# one-time: recover/generate your owner key + blobB, install blobB into NBTCarHU
#   (see fsc/02-blobB-and-minting.md and the flash capability for the length-preserving blobB swap)

# mint a CarPlay FSC, bound to YOUR VIN (recommended; CarPlay FSCs are normally VIN-specific)
python capabilities/fsc/tools/fsc.py mint --key owner_key.json --appno 0x0143 --vin <YOURVIN> -o carplay.fsc

# prove the unit would accept it, offline, before you ever touch the car
python capabilities/fsc/tools/fsc.py verify --fsc carplay.fsc --key owner_key.json      # must say OK
```

Then **apply** it over the diagnostic link (`requestStoreFSC`, behind the write-session SecurityAccess
— the **L3 key**; see [fsc/03-apply-and-read.md](../capabilities/fsc/03-apply-and-read.md)).

> Entitlement route in one line: *stock BMW FSC present → use it; absent → install your blobB and
> mint+apply your own `0x0143`.*

---

## 2 · Coding — the bits that wire CarPlay in

Edit these datagroups in a copy of `backup.ncd`, re-sign `dg3010`, and write the signed NCD (the
whole flow — sign + the `27 01/02` write session — is [coding/03-write-flow.md](../capabilities/coding/03-write-flow.md)).

### Required: the CarPlay coding check

| Coordinate | Set to | Token | Evidence |
|---|---|---|---|
| `dg3004 / byte 0 / 0x04` | `1` | `CARPLAY_SWT` | The head unit's CarPlay check (`isAppCoded` in `NBTCarHU`) reads this one bit. It offers CarPlay only when the bit is 1 **and** the `0x0143` FSC is accepted. It's 0 in the reference unit's stock coding and 1 in its working CarPlay coding. *Firmware-traced and seen on the car.* |

This is the only coding bit the firmware's CarPlay check reads.

### Also set in a known-working CarPlay coding

| Coordinate | Set to | Token | Status |
|---|---|---|---|
| `dg3001 / byte 29` | `0x15` (21) | `AUX1_IN_HU` | **Unproven.** The reference unit's working CarPlay coding changes it from `0xFF` to `0x15`, but no code that reads this byte was found in this build. Set it to match the working car, or settle it with the test below. |
| `dg3000 / byte 39 / 0x80` | `1` (optional) | `CARPLAY_FULLSCREEN` | Shows CarPlay full screen instead of in a window. Cosmetic. |

**The test that settles `AUX1_IN_HU`.** With the FSC active, write only `CARPLAY_SWT = 1` and leave
`AUX1_IN_HU` at `0xFF`. Reset the HU and plug in an iPhone:
- if CarPlay comes up, `AUX1_IN_HU` isn't needed;
- if it doesn't, add `AUX1_IN_HU = 0x15` and compare.

Report the result either way, so this page can drop the "unproven".

### Already set from the factory: nothing to write

The reference unit already had these values in its stock coding, set by its factory options rather
than by CarPlay. Its working CarPlay coding leaves them unchanged:

| Coordinate | Stock value | Token |
|---|---|---|
| `dg3003 / byte 22 / 0x40` | `1` | `API_APPLE_AUTH_CHIP_ON_OFF` |
| `dg3003 / byte 2 / 0x1C` | `5` (NBT) | `API_TYPE` |
| `dg3004 / byte 2 / 0x20` | `1` | `PIA_A4A` |
| `dg3004 / byte 1 / 0x01` | `1` | `PIA_PORTIERUNGSMASTER` |

If yours read differently, your car lacks the options that set them. Whether CarPlay then needs them
is untested, so compare against your own backup before changing them.

### Not CarPlay settings

Earlier versions of this page listed these as CarPlay bits. The evidence says they aren't:

| Coordinate | Token | Why it doesn't belong here |
|---|---|---|
| `dg3003 / byte 20 / 0x40` | `WLAN_DIAGNOSE` | A Wi-Fi diagnostic mode. No CarPlay, connectivity, media or HMI code reads it, and it's already 1 in stock coding. |
| `dg3000 / byte 22 / 0x80` | `APPLE_ENHANCEMENTS` | Off in the known-working CarPlay coding, so it isn't required. |
| `dg3003 / byte 2 / 0x01` | `A4A_WIRELESS_IOS` | A4A is BMW's own smartphone-apps link, not CarPlay. No wireless CarPlay path was found on NBT EVO. |
| `dg3004 / byte 32 / 0x03` | `CP_NMEA_VARIANT` | A GPS datum setting (WGS-84 or GCJ-02 for mainland China), not an enable. Leave it at stock. |

The old claim that one firmware function, `FUN_00334d3c`, reads "three CarPlay enable points" was
wrong. That function only builds the generic reader for the whole dg3003 page.

### The FA-gate caveat (important)

`CARPLAY_SWT` is FA-gated: it follows option 6CP (Smartphone Integration) and is suppressed by 6AE
(TeleServices). If the car recomputes its coding from the FA (vehicle order) and the FA has no 6CP,
the recompute clears the bit again. So there are two durable routes:

- **Direct write (what this toolkit does):** write the bits straight into the datagroups and sign.
  Durable across reboots. But a later *VO/FA recode* would undo them — so don't FA-recode the HU
  after, or:
- **Add 6CP to your FA first**, then code from FA. Then the bits are "legitimate" to the FA logic and
  survive a recode. (FA editing is outside this toolkit; the direct-write route is self-contained.)

---

## 3 · Order of operations

1. **Back up** coding (`read_coding`) and record your stock blobB.
2. **Entitlement:** read FSC state. If no valid CarPlay FSC → install owner blobB, `mint` + `verify`
   `0x0143`, then `apply` it.
3. **Coding:** edit the datagroups in §2 on a copy of the backup, **re-sign `dg3010`**
   (`sign_ncd.py`), confirm it verifies locally, then signed-write (`write_coding.py`, which refuses
   unless the connected VIN is yours and the signature checks). Writing all of §2 in one go is
   fine. If the HMI freezes or doesn't come up, or CarPlay doesn't appear, revert and build back up
   one bit at a time ([coding/05](../capabilities/coding/05-apply-observe-revert.md)):
   1. `CARPLAY_SWT` alone;
   2. then `AUX1_IN_HU`;
   3. then `CARPLAY_FULLSCREEN`.
4. **Reset** the HU (the write flow ends in `11 01`); it reboots and re-verifies.

Entitlement before or alongside coding is fine; just have **both** in place before you judge whether
it worked.

---

## 4 · Confirm it worked

- **Coding:** `read_coding` again and diff. `CARPLAY_SWT`, and anything else you set, should read
  its new value, and `dg3010` should match.
- **Entitlement:** read FSC state (`22 FDEC` / `GetFSC`); `0x0143` shows active. If you installed
  your own blobB, re-verifying against a *genuine* blobB will flag it self-signed — expected
  ([fsc/03-apply-and-read.md](../capabilities/fsc/03-apply-and-read.md)).
- **End to end:** plug an iPhone into the media USB port — the car offers CarPlay.

If coding reads back correct and the FSC is active but CarPlay still doesn't appear, suspect
**hardware** (no MFi path / wrong USB port) or a **cable** (a data-capable Lightning/USB-C cable,
not charge-only) before re-checking bits.

---

## 5 · Revert

- **Coding:** write `backup.ncd` back (it's already correctly signed — it's what the car gave you).
  If the HMI is frozen or won't load after the coding write, revert anyway. The write goes over UDS
  to the diag app, not through the HMI.
- **Entitlement:** `DisableFSC 0x0143`, and/or restore genuine blobB — once BMW's blobB is back, a
  self-signed CarPlay FSC goes inert on its own.

---

## Honest status

- **Proven offline:** the coding signer reproduces the car's own signature byte-for-byte
  (`coding/validate/selftest.py`); FSC `mint`/`verify` are tested (`fsc/validate/check_fsc.py`).
- **Runbooks (your key, your car):** the coding **write** (`27 01/02` SecurityAccess) and the FSC
  **apply** (`requestStoreFSC`) are documented car-write steps behind your own **L3 key**
  (`python -m nbtevo.keys --kind l3`, see [docs/keys.md](../docs/keys.md)) — no turnkey one-command
  tool is shipped, by design.
- **The CarPlay requirements, graded:**
  - the `0x0143` FSC and `CARPLAY_SWT` are traced in firmware and match a known-working car;
  - `AUX1_IN_HU` matches a known-working car, but no firmware reader was found (test in §2);
  - the factory-set bits were checked only against one car's stock coding.

  **Validate on your own unit:** read back, and trust behavior over assumption.
