# 03 · Reading installed FSCs and applying one

Reading is safe and needs no trust swap — do it to see what your unit is entitled to and to detect
whether a trust-anchor swap is in place. Applying writes to the unit.

## Read what's installed

The unit exposes its FSC state over the diagnostic bus. Two complementary reads:

- **FSC status DID `22 FDEC`** — enumerates the installed FSCs and their state. Combined with a
  re-verify against the **genuine** blobB (taken from a stock `NBTCarHU`), this tells you whether a
  given FSC is BMW-signed or self-signed:
  - a stock unit: every FSC verifies under genuine blobB;
  - an owner-CA unit: your FSCs **fail** under genuine blobB (they verify only under *your* modulus)
    — that failure is the signal that the trust anchor was swapped.
- **`Swt` service verbs** — `GetFSC` / `CheckFSC` / `CheckFscAccepted` / `StatusApplication` return
  per-application state through the service.

There is **no raw blobB read-back** over the bus (no ReadMemoryByAddress, no upload service that
reaches `NBTCarHU`), so you confirm the installed trust *indirectly*: apply an owner-signed FSC and
watch the feature activate (only possible if the installed modulus is yours), and/or read `22 FDEC`
and see your FSCs flagged self-signed against genuine blobB. Together these are unambiguous.

## Who signed this unit's FSCs? (do this BEFORE you overwrite blobB)

You are **not** necessarily the first person to touch this unit's trust anchor — a used head unit
may already carry a genuine BMW anchor, *your* anchor from an earlier swap, or **someone else's**
owner-CA modulus. Overwriting blobB blindly strands whatever's there (its FSCs go inert). So
inventory the installed anchor first. Two ways, by what access you have:

**A — you have filesystem/SSH access to the HU (definitive).** Read the 128 blobB bytes straight
out of `NBTCarHU` at offset `0x35A300` (little-endian) and fingerprint them:

```
dd if=<path-to-NBTCarHU> bs=1 skip=$((0x35A300)) count=128 of=installed_blobB.bin
python capabilities/fsc/tools/fsc.py fingerprint --blobb installed_blobB.bin
```

Compare that fingerprint to the genuine BMW anchor (carve `installed_blobB.bin`'s equivalent from a
**stock** `NBTCarHU` of the same software version) and to your own key
(`fsc.py fingerprint --key owner_key.json`). A match tells you exactly what's installed.

**B — diagnostic access only (no shell).** You can't read blobB over the bus, but you can read the
**FSCs** (`22 FDEC` / `GetFSC`) and ask whose anchor signed them — which is the installed anchor,
since the unit only keeps FSCs that verify under it. Dump two or more tokens and run:

```
# name the anchors you know; --recover handles an anchor you DON'T know (e=3 modulus recovery)
python capabilities/fsc/tools/fsc.py whosigned \
    --fsc tokenA.fsc --fsc tokenB.fsc \
    --anchor bmw=genuine_blobB.bin --anchor mine=owner_key.json --recover
```

- verifies under **genuine BMW** → stock anchor; a normal retrofit, nothing swapped.
- verifies under **your** key → you (or your earlier self) already own this unit's trust.
- verifies under **neither**, and `--recover` prints an unknown fingerprint → **a third party swapped
  blobB**. Their FSCs are theirs; your overwrite would replace their anchor with yours (and you'd
  re-mint your own FSCs afterward). Decide that deliberately.

`--recover` uses the fact that the verifier's exponent is **3**: for each token
`sig³ − paddedMessage` is an exact multiple of the modulus, so the GCD across two tokens from the
same unit yields the modulus with no prior knowledge of it. Proven offline in
[validate/check_fsc.py](validate/check_fsc.py).

## Apply an FSC

An FSC is applied by the engine's **`requestStoreFSC`** verb (internally `doStoreFSC`), reached over
the `Swt` DSI service across the diagnostic link (behind the usual SecurityAccess write session —
the **L3 key**, recovered with `python -m nbtevo.keys --kind l3`, see [docs/keys.md](../../docs/keys.md)).
The stored/entered form is the 188-byte token **base32-encoded** (`getBinaryFSC` decodes
it); `tools/fsc.py` emits the raw binary — base32-encode it for the wire.

The shape of the apply, once you're in a write session to `0x63`:

1. (If you installed your own trust anchor) confirm blobB is yours — otherwise a self-signed FSC is
   rejected. See [02-blobB-and-minting.md](02-blobB-and-minting.md).
2. Send the base32 FSC via `requestStoreFSC` for its application number.
3. The engine runs the same verify as [01-concepts.md](01-concepts.md) (`CheckFSC`) and stores it on
   success; `CheckFscAccepted` / `StatusApplication` then report it active.
4. The consuming app (`Connectivity`, `Online`, `apnnav*`) picks up the new activation state.

> This is the mechanism as reverse-engineered; a tested one-command apply tool is not shipped here
> yet (it's a write path behind SecurityAccess, like the coding write). Treat a first real apply as
> a careful, backed-up operation on your own parked car, and confirm by reading the state back.

## Revert

Re-apply the stock trust anchor (put BMW's blobB back — keep the stock 128 bytes from step 2 of
[02-blobB-and-minting.md](02-blobB-and-minting.md)) and/or `DisableFSC` the application numbers you
added. Because an owner FSC only verifies under your modulus, restoring genuine blobB alone already
makes your self-signed FSCs inert.

## Honest status

- **Read/inspect** (`22 FDEC` + re-verify against a local stock blobB; `GetFSC`/`CheckFSC` over the
  service) — straightforward and safe; model it with `tools/fsc.py verify`.
- **Apply** (`requestStoreFSC` over the `Swt` service) — documented here as the mechanism; the
  runnable write tool lands with the diagnostic-write work (same SecurityAccess story as coding).
