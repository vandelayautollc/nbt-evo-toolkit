# Versions — what this was derived on, and what carries to yours

Everything in this toolkit was reverse-engineered on **one** head-unit software set. Some of what's
written here is true for the whole NBT EVO generation (protocols, file formats, the ABI, the signing
*model*); some of it is a number — an **offset**, a **coordinate**, a **key id**, a **node name** —
that is only true for a specific build and must be re-checked on yours. This page says which is which,
what SWFL versions to expect to work, and how to tell where your unit sits.

> The one rule: **read your own SVK first** (`22 F1 01`, see [01-transport-connect.md](01-transport-connect.md))
> and compare it to the reference set below. Methods transfer; numbers you verify.

## The reference build (what the bundled specifics describe)

Read from an **NBT EVO** (`HU_NBT2`), software line **`007.051.002`**:

| Thing | Reference value | Where it's used |
|---|---|---|
| Bootloader (BTLD) | `00001FFD` @ `007.051.002` | selects the coding + L3 keys ([keys.md](keys.md)) |
| Coding dataset (CAFD) | `00001EF6` @ `006.048.013` (and `006.064.014`, same layout) | coding coordinates ([coding](../capabilities/coding/)) |
| OMAP core / media SWFL | `0000271A` @ `007.051.002` | holds `NBTCarHU` (FSC engine + blobB); OPT_DEBUG target |
| HMI SWFLs | `00002719` / `00002720` @ `007.051.002` | scene/widget + the `vehicles/` templates ([vehicle_models](../capabilities/vehicle_models/)) |
| OS / toolchain | QNX Neutrino 6.5.0 SP1, GCC 4.4.2 | the ABI gate for QNX binaries + plugins |

The full SVK table (every SGBM id + version + size) and the decrypted-CAFD `sha256` are in
[psdzdata-manifest.md](psdzdata-manifest.md). Match your pool files to it to know you have the right
inputs.

## What transfers vs. what you re-verify

**Version-stable — expected to hold across the whole NBT EVO generation** (these are protocol / format /
architecture facts, not build constants):

- the transport and UDS flows — HSFZ over ENET, the SVK/SGBM structure, the coding write and flash
  SecurityAccess choreographies ([01](01-transport-connect.md), [coding/03](../capabilities/coding/03-write-flow.md), [flash/03](../capabilities/flash_and_patching/03-flashing-safely.md));
- the WOODOO/IOC-BOLO `.swdl` **container format** ([flash/01](../capabilities/flash_and_patching/01-how-flashing-works.md));
- the coding **signing model** — RSA e=3, datagroup pages + a signature datagroup, keyed by BTLD ([coding/02](../capabilities/coding/02-signing-model.md));
- the FSC **token format + blobB verify** — 188-byte token, MD5 + RSA e=3 under one modulus ([fsc/01](../capabilities/fsc/01-concepts.md));
- the **QNX 6.5.0 / EABI5 soft-float** ABI and the RA-plugin loader model ([qnx_dev/01](../capabilities/qnx_dev/01-toolchain-and-abi.md), [plugins](../capabilities/plugins/));
- the HMI **resource pipeline** — resources index → bundles → variant flag → coding ([resource-pipeline.md](resource-pipeline.md)).

**Version-sensitive — re-verify on your own build.** These are the numbers/names that move:

| What | Reference | On a different build | How to re-derive |
|---|---|---|---|
| **blobB offset** in `NBTCarHU` | `0x35A300` | **will differ** — it's a file offset into a specific SWFL build | scan `NBTCarHU` for the stock 128-byte modulus (it sits near the coding **DEV-2048** key `~0x35cb00`); confirm by re-verifying a stock FSC under the bytes you find ([fsc/03](../capabilities/fsc/03-apply-and-read.md)) |
| **coding key offset** (DEV-2048) | `~0x35cb00` | will differ | same approach; it's disjoint from blobB (why the blobB swap doesn't break coding) |
| **coding coordinates** (dg/byte/bit) | CAFD `006.048.013` / `006.064.014` | identical on those two; **other CAFD versions may remap** | regenerate the map from *your* CAFD (`definitions/build_definitions.py`); the sha256 in the manifest tells you if yours matches ours ([coding/04](../capabilities/coding/04-definitions.md)) |
| **which key** | BTLD `00001FFD` | a different BTLD ⇒ a different key (and possibly a different key *class*) | recover keyed by **your** BTLD (`nbtevo.keys --btld <id>`, [keys.md](keys.md)); the signing model handles legacy-RSA vs secure-ECDSA BTLDs ([coding/02](../capabilities/coding/02-signing-model.md)) |
| **flash target + version string** | SWFL `0000271A` @ `007.051.002` | your SWFL id/version | read it from your SVK; the patch tooling takes `--sgbm`/`--version` from what you read ([flash README](../capabilities/flash_and_patching/README.md)) |
| **HMI node / material names, scene/widget layout, `vehicles/` templates** | this build's carve | per HMI SWFL build | the packager `--selftest` rebuilds your stock bundles byte-for-byte — if it passes, your tree matches the tools; author against *your* template ([vehicle_models](../capabilities/vehicle_models/)) |
| **plugin ABI** (vtable slots, offsets, mangled names) | one ID5 build | per build | re-verify against your own carve with `nm -DC` ([plugins §ABI](../capabilities/plugins/docs/06-runtime-api-reference.md)) |

## So: which SWFL versions "work"?

- **Same line (`007.051.002`)** — every bundled specific applies directly. Confirm with the SVK table
  and the CAFD sha256.
- **Other NBT EVO builds (other `007.0xx` / neighbouring lines, other region/market images)** — the
  **methods and formats are expected to work**; the **offsets, coordinates, key ids and node names
  will not be assumed correct**. Re-derive each from the "how" column above before you write anything.
  Nothing here hard-codes a version into a write path: the coding signer reads the BTLD and CAFD
  version off the car, the flasher takes the SGBM/version you pass, and the key tools are keyed by your
  BTLD — so a matching-method/different-numbers build is a *re-verify*, not a rewrite.
- **Not NBT EVO** (plain NBT, `HU_ENTRY`, or MGU / iDrive 7–8) — a different platform; the methods
  *rhyme* but the specifics (addresses, container, keys, schema) differ. See
  [00-platform-overview.md](00-platform-overview.md) to tell which you have.

## Check where your unit sits (2 minutes, read-only)

1. **Read the SVK** — `22 F1 01` decoded ([01-transport-connect.md](01-transport-connect.md)) gives your
   BTLD / CAFD / SWFL ids **and versions**.
2. **Compare** to the reference table above and the full table in [psdzdata-manifest.md](psdzdata-manifest.md).
3. **If they match** — bundled specifics apply; proceed per each capability.
4. **If they differ** — the methods still apply; re-derive the version-sensitive numbers via the "how"
   column and the [investigation-playbook.md](investigation-playbook.md). Every capability doc also
   states its own "honest status" and which facts are build-specific.
