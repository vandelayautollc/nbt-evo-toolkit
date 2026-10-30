# Investigation playbook — answering a question this repo hasn't

The capability folders are **worked examples, not the boundary** of what's possible on this head
unit. This doc is the method they're examples of: given a novel "how do I change / find / enable
X?", how to locate the answer in the system yourself. It's deliberately capability-neutral — a more
capable agent should use it to go where we haven't, not treat our recipes as the ceiling.

Read [architecture.md](architecture.md) (the map) and [resource-pipeline.md](resource-pipeline.md)
(how visible things are chosen) first. [toolchain.md](toolchain.md) has the tools each step uses.

## First: classify the question

The right starting point depends on *what kind of thing* X is. Decide this before touching anything:

| X is… | It's probably governed by… | Start at |
|---|---|---|
| a picture / 3D model / text / regional asset / feature visibility | **resources + coding** | [resource-pipeline.md](resource-pipeline.md) |
| a configurable toggle / regional / UI option | **coding** | `capabilities/coding/` |
| a paid/licensed feature (nav, apps, video-in-motion) | **FSC entitlement** | `capabilities/fsc/` |
| fixed program behavior with no data knob | **app/HMI logic** → change via plugin or patch | playbook §firmware-trace, then `capabilities/plugins/` or `flash_and_patching/` |
| a whole new program you want to run | **your own binary** | `capabilities/qnx_dev/` |

Most "change what I see" questions are the first two rows and never require a disassembler.

## The general loop

Whatever the class, the shape is the same:

1. **Observe the artifact precisely.** Don't work from a description — capture ground truth. For
   screens, screenshot via `LayerManagerControl` (dump screen 0 = CID;
   [recipe](toolchain.md#screenshotting-the-hmi)). For behavior, read the
   relevant DTCs/logs ([hmi-debugging.md](hmi-debugging.md)). You want the exact id/name/string,
   not "the car picture".
2. **Name it.** Turn the observation into an identifier the system uses: a resource **GID**, a
   coding **token**, an **FSC/SWID** feature id, a file path, or a symbol. The naming sources are in
   [architecture.md](architecture.md) (the syset token table in `sysetshellevo`, the resource ids
   in `resources.ptr`, the feature catalog for FSC).
3. **Find where it's referenced.** Static search first — it's cheap and safe:
   - resources: grep `assetDB/resources.ptr` for the GID.
   - coding: find the `va_<TOKEN>` entry in `libhmicoding`, and which binary reads it.
   - strings: `strings`/grep the extracted firmware for the id/path/message.
4. **Find the gate.** What decides the current value? A **coding** datagroup/bit (resource-pipeline
   shows the variantFlag↔coding link), an **FSC** token, or a build-time constant. If it's coding or
   FSC, you may be done — change the gate (`capabilities/coding/` or `fsc/`).
5. **If there's no data knob, trace the consumer in firmware.** Identify which binary reads it
   (table below), then do a **targeted** decompile — never full-analyze `HmiMain3D` (~60 MB); point
   the tool at the one function/xref (see toolchain). You're looking for: what the value switches,
   or where the behavior is decided.
6. **Choose the safe change point.** Prefer, in order: coding → FSC → resource override (add/rename,
   never overwrite — LMPC) → plugin (adds behavior without touching stock) → patch (modifies a
   signed software area; highest risk). The earlier the lever, the safer and more reversible.
7. **Apply, reset, verify.** Install over the right path (UDS for coding/FSC/flash; SSH for
   file/plugin/model installs), trigger the needed reset (`appreset`, HMI reset, or ECU reset), and
   **re-observe** to confirm — then read back / screenshot. Never report success without step 7.
   Before you apply, decide what failure looks like (the HMI doesn't come back, freezes, or
   reboot-loops) and have the revert ready to run. If you see failure, revert first and investigate
   after. A change that's correct for this build can still be wrong for this unit's hardware. For
   coding, the full apply/observe/revert/bisect loop is
   [coding/05](../capabilities/coding/05-apply-observe-revert.md).

## Where coding/resource values are consumed (the §5 index)

When you must trace a value to its effect, this is which binary to open:

- **HMI-wide feature/variant**: `libhmicoding.so` holds the `va_<TOKEN>_<value>` table and
  `isVariantSet(id)`/`getVariantVal(id)`; `HmiMain3D` asks for those ids (plus ~1,067 derived ids
  computed in `CHmiVariantServer::init`). The HMI's own UI strings are in `bmw/db/text.db`
  (NRV2D UTF-16).
- **Video / camera / reverse image**: `EarlyVideoApp` / `EarlyICam2App` (`/opt/car/bin`) log their
  coding reads; video source bytes index `CPVideoRouting::getRoute`'s 26-row route table (255 = no
  route).
- **Navigation**: `apnnav*` is **not stripped** (`nbt_coding_if_get<TOKEN>`) — the easiest readable
  example of a coding consumer.
- **Audio / EQ**: `AudioProcess` lives in the Jacinto IFS inside the bootloader bundle
  (`00001FFD`, LZO-packed QNX IFS); `EQ_VARIANT` selects an eqdata bin.
- **Not every token has a consumer** in a given build — if a value has no reader anywhere, changing
  it does nothing. Conclude that honestly rather than inventing an effect.

## Worked example: "what does coding value Y do?"

1. Read the token's engineering name/values from the syset table (`sysetshellevo`).
2. Find `va_<TOKEN>_<value>` in `libhmicoding`; note the variant id.
3. Grep the firmware for that id / the token across the binaries in the index above.
4. In the consumer that hits, targeted-decompile the reader to see what the value switches (a route
   code, a visibility flag, a file suffix, …).
5. If nothing reads it, it's inert in this build — say so.

That's the same loop as the image example, with step 3–5 in firmware instead of resource tables.
The method doesn't change; only *where you look* does, and the classification table tells you that.

## Habits that keep you right

- **Static before dynamic, read before write.** Every answer above is reachable by reading
  (resource tables, strings, targeted decompile, coding reads) before you change anything.
- **Confidence honesty.** Mark firmware plausibility as plausibility; don't present an inferred
  mapping as proven (the variantFlag→series map, for one, is inferred but holds everywhere checked).
- **Integrity + reversibility first.** Favor the earliest, most reversible lever. Add, don't
  overwrite. Keep a backup. The system tells you when you've broken a rule (DTC on LMPC mismatch,
  `EHOSTUNREACH` on a pf block, coding revert on an unsigned edit) — learn those signatures.
