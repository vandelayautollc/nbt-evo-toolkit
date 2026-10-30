# 02 · blobB and minting (your own trust anchor)

The owner-authorized way to make FSCs your unit accepts: install **your own** modulus as blobB,
then sign FSCs with **your own** key. No BMW key is forged or needed.

> ⚠️ This enables licensed features. Do it only on a vehicle you own; the licensing question is
> between you and BMW. See [LEGAL.md](../../LEGAL.md) and the [LICENSE](../../LICENSE).

## The idea

`blobB` is the single RSA modulus the long-FSC verifier trusts ([01-concepts.md](01-concepts.md)) —
128 bytes, little-endian, e=3, at `NBTCarHU` file offset **`0x35A300`**. Swap those 128 bytes for
your own modulus and the unit now trusts **you**: FSCs you sign with the matching private key verify
and activate. You become the "CA" for your own unit's features.

```
your e=3 keypair ──public modulus──▶ patched into NBTCarHU @0x35A300 (blobB)  ──▶ unit trusts you
                 └─private key──────▶ signs FSCs (tools/fsc.py mint) ──────────▶ unit accepts them
```

## Step 1 — generate your trust anchor

```bash
python capabilities/fsc/tools/fsc.py keygen -o owner_key.json --blobb owner_blobB.bin
```

- `owner_key.json` — your RSA e=3 key. **The private part is the root of trust for every FSC you
  issue; keep it secret** (the tool writes it `0600`, and `.gitignore` keeps `*key*.json` out of git).
- `owner_blobB.bin` — the 128-byte little-endian modulus, ready to patch in.

## Step 2 — install your modulus as blobB (a flash patch)

> **First, find out what's already installed.** You may not be the first to swap this unit's
> anchor — a used HU can carry a genuine BMW anchor, your own, or a *stranger's* owner-CA modulus,
> and overwriting it blindly strands whatever's there. Before this step, inventory the installed
> anchor per [03-apply-and-read.md § "Who signed this unit's FSCs?"](03-apply-and-read.md#who-signed-this-units-fscs-do-this-before-you-overwrite-blobb)
> (`fsc.py whosigned` / `fingerprint`). Then overwrite deliberately.

The patch is **length-preserving**: replace the 128 bytes at `NBTCarHU` offset `0x35A300` with
`owner_blobB.bin`. Because the size is unchanged, no ELF offsets move; and because the FSC key and
the **coding** key are *disjoint singletons* (coding verifies against a different key — DEV-2048 at
a separate offset, `~0x35cb00`), **a surgical blobB-only patch does not break coding**. (Wholesale
engine/persistence replacement *would* break coding — don't do that; the surgical 128-byte swap is
the clean path.)

> **`0x35A300` is build-specific.** It's a file offset into *this* `NBTCarHU` (SWFL `0000271A`
> @ `007.051.002`). On a different SWFL version the offset moves — **find it on your own binary**
> (scan `NBTCarHU` for the stock 128-byte modulus; it sits near the DEV-2048 coding key) and confirm
> by re-verifying a stock FSC under the bytes you find. See [docs/versioning.md](../../docs/versioning.md).

Applying the patch means flashing the patched `NBTCarHU` to the unit — that is the
**`flash_and_patching`** capability. You do **not** edit the signed SWFL container in place (the head
unit rejects a modified signed container); you edit the `NBTCarHU` *file* and deliver it in a
no-signature file-copy container. The edit itself is just:

```
NBTCarHU[0x35A300 : 0x35A300 + 128] = owner_blobB.bin
```

With the flash capability's tooling that is two steps — edit the file, then wrap it:

```bash
patch.py edit --from-container swfl_0000271a.bin --payload NBTCarHU \
    --offset 0x35A300 --bytes owner_blobB.bin -o NBTCarHU.patched
patch.py build-filecopy --file NBTCarHU.patched --target-path /fs/sda0/opt/car/bin/ --name NBTCarHU \
    --id ownerca --class swfl --sgbm 0000271A --version 007.051.002 -o .
```

See [../flash_and_patching/02-authoring-patches.md](../flash_and_patching/02-authoring-patches.md).

Keep a copy of the stock 128 bytes so you can put BMW's trust anchor back. Verify after flashing by
applying an owner-signed FSC and seeing the feature activate (see [03-apply-and-read.md](03-apply-and-read.md));
there is no raw blobB read-back over the diagnostic bus, so activation is the confirmation.

## Step 3 — mint FSCs under your key

```bash
# CarPlay, VIN-generic (application numbers are in catalog.md)
python capabilities/fsc/tools/fsc.py mint --key owner_key.json --appno 0x0143 -o carplay.fsc

# or unit-locked to your own VIN
python capabilities/fsc/tools/fsc.py mint --key owner_key.json --appno 0x0143 --vin YOURVIN12 -o carplay.fsc

python capabilities/fsc/tools/fsc.py verify --fsc carplay.fsc --key owner_key.json   # OK
```

`mint` builds the 60-byte body, MD5s it, and signs with your private key into the exact zero-slack
PKCS#1 v1.5 envelope the device expects, then self-verifies. `verify` reproduces the on-device
check against any modulus (`--key` yours, or `--blobb` a 128-byte file) so you can confirm what a
unit with that blobB would accept *before* you go near the car.

## Prove it offline first

```bash
python -m capabilities.fsc.validate.check_fsc
```

Generates a fresh anchor, mints several FSCs, and shows each is **accepted under your key** and
**rejected under a different key** — i.e. acceptance really does depend on the installed modulus.
This is the whole mechanism, demonstrated without a vehicle.

Next: [03-apply-and-read.md](03-apply-and-read.md) — getting the FSC onto the unit and reading what's
installed.
