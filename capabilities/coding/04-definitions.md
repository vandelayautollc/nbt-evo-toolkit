# 04 · Definitions — making a coordinate mean something

A coordinate like `0x3001 / 0x62 / 0x78 = 2` is durable and correct, but meaningless until you know
it's "startup emblem → ALPINA". This doc is the human-readable map of what every
coordinate means — and how to regenerate or extend it from your own CAFD.

> **What ships here** (`definitions/`): our own descriptions of all **1481** parameters in CAFD
> `00001EF6` (v006.048.013) — `cafd_00001ef6_definitions.md` (readable, grouped by datagroup) and
> `cafd_00001ef6_definitions.json` (machine-readable). These are *our reconstructed descriptions*
> (physical facts about what each var does), not BMW data, and all car-specific state has been
> stripped. `build_definitions.py` regenerates them from a human-map JSON, and
> `apply_firmware_labels.py` overlays the firmware-traced labels on top (below). If your car's CAFD
> differs, regenerate from your own (pipeline below).

## Where the names come from

BMW strips human names out of the shipped CAFD, so a map is reconstructed from sources where the
meaning still lives, then translated to plain English:

1. **Engineering tokens** — the HU firmware's own syset descriptor table carries the BMW tokens
   (e.g. `ENT_COVERFLOW`, `MOMENTANVERBRAUCHSANZEIGE`). Ground truth for *what* a field is.
2. **Per-value enum names** — the same table names the settable values (e.g. a drive-source field
   whose values are `{1: CD, 2: DVD, 3: Blu-ray}`).
3. **FA/SALAPA gates** — which option code activates a parameter, from BMW's option catalog.
4. **Firmware traces** — for opaque fields, trace the consumer in the HU binaries to see what the
   value actually switches (see the repo's notes on coding value consumers).
5. **Translation + review** — German tokens expanded to faithful English; each parameter named and
   then independently re-checked, so a plausible-but-wrong guess gets caught.

The result is a per-coordinate record: `{coordinate, name, description, values, default, fa_gate,
confidence, source}`. **Confidence is honest** — "low" means a genuinely reserved/undocumented bit,
not a guess dressed up.

## Which source wins: firmware traces first

The `source` field says where a record's text came from. **Firmware-traced text is preferred over
every other source.**

| `source` | What it means | Trust |
|---|---|---|
| `firmware-trace` | Written from the firmware itself: the code that reads the value, the unit's own symbol↔raw value table, the files it loads (e.g. the startup-emblem artwork). These records may also carry `flags` (what each bit means), `number` (raw range × factor + offset, unit) and a note when the trace found **no reader**, i.e. the value has no effect in this build. | Highest. Prefer it over anything else. |
| `firmware`, `firmware-token` | Named from the firmware's own token and enum tables; what the value *does* wasn't traced. | Good for *what* the field is; check the effect before relying on it. |
| `inferred` | Reasoned from neighbours and context. | Treat as a lead. |

**Every record comes from our own reverse engineering**: a firmware trace, or the token and the unit's
own value table. A trace can overturn a reading of the token. For example, `STARTUP_EMBLEM` value 9
is the M-logo glow, because the firmware loads the `eva_animation_0x09_*` artwork for it.

`apply_firmware_labels.py` applies the overlay. It takes the firmware-traced functions from our
research map, matches each one to its coordinate, and replaces that record's name, description and
value labels. It also swaps in the map's re-authored text for every function the map flags
`clean_room`, and warns about any record whose `source` isn't one of the values above. Re-run it
whenever more functions get traced:

```bash
python capabilities/coding/definitions/apply_firmware_labels.py \
    <map>_userfacing.json <map>_fields.json --inputs <map>/inputs/
```

> **A definition describes the parameter, not your car.** The map says what a coordinate means in
> this CAFD. It does not say that setting it will work on *your* unit. The hardware fitted, the HMI
> build, the other coding bits, and the FSCs decide that, and an option that needs something missing
> can be inert or can hang the UI. `confidence` rates the *description*, not whether the option will
> work on your unit. Before relying on an option, trace its consumer or test it with apply/revert
> ([05-apply-observe-revert.md](05-apply-observe-revert.md)).

## The regeneration pipeline

Pointing at your own extracted CAFD (`$NBTEVO_PSDZDATA`), the pipeline is:

```
cafd_<id>.caf.<ver>  ──decrypt──▶  CAFD XML spine  ──skeleton──▶  coordinate list
                                                         │
          firmware syset tokens ──┐                      │
          firmware enum values  ──┼──▶  naming layer  ──merge──▶  human map (md + json)
          FA/SALAPA catalog     ──┘
```

Stages (the repo's `coding/` tooling implements each; port order for this folder):

| Stage | Input | Output |
|---|---|---|
| decrypt | your `.caf` (CMS) + your PSdZData keys | decrypted CAFD XML |
| skeleton | CAFD XML | coordinate list (every `(dg, byte, mask)`) |
| extract-enums | HU `sysetshellevo` firmware | token + enum-value dictionaries |
| build-map | skeleton + dictionaries + catalog | token map (machine) |
| build-human-map | token map + naming layer | `*_HUMAN_MAP.md` + `*_human_map.json` |

A regeneration check: the decrypted CAFD XML for `00001EF6` v`006.048.013` is byte-identical across
NBT EVOs on that version — its `sha256` is in [docs/psdzdata-manifest.md](../../docs/psdzdata-manifest.md).
If your decrypt matches, your source and pipeline agree before you build names on top.

The bundled map covers v`006.048.013` and v`006.064.014` (same layout). On any other CAFD version,
regenerate from your own CAFD rather than trusting these coordinates — see
[docs/versioning.md](../../docs/versioning.md) for what's version-stable vs. what moves.

## Authoring user-facing wording

If you present these parameters in an app or sheet, write the *wording* (labels, value names)
yourself, from the token, the value table and the trace. Keep a short style guide
(sentence case, "Enabled/Disabled", number presets, "checked/checkbox" for US English) and key each
label to the CAFD version it was written against, so a layout change can't silently remap a label.

## Using the map at runtime

Look a coordinate up in `definitions/cafd_00001ef6_definitions.json` (the bundled map, or your
regenerated one) to get its name, legal values, and default; then decoding/encoding is mechanical:

```python
from nbtevo import srec
mem, recs = srec.parse(open("backup.ncd").read())

# read a parameter at (datagroup, offset, mask, shift)
raw = (srec.get(mem, 0x3001, 0x62) & 0x78) >> 3        # → current value

# set it, then RE-SIGN before writing (see 02 / 03) — a bare edit reverts on boot
srec.set_byte(mem, 0x3001, 0x62, value=2, mask=0x78, shift=3)
```

The map tells you the coordinate and the legal values; `nbtevo.srec` does the bit surgery;
`sign_ncd.py` makes it durable.
