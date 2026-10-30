# 05 · Will it work on *this* unit? — verify, apply, observe, revert, bisect

A coding parameter appearing in the [definitions map](04-definitions.md), a correct signature, and a
clean read-back mean the bytes you wrote are on the car. They do **not** mean the option does what
you wanted on *this* car. Whether a coding change takes effect depends on what the unit actually
has: the hardware fitted, the software build, the CAFD version, the other coding bits, and the FSC
entitlements. On a unit where those don't line up, the same signed change can do nothing, or it can
leave a menu that won't open, a screen that never loads, or an HMI that freezes or reboot-loops.

So treat every coding change as an **experiment on this unit** until you have watched it work here.
This doc is the method: verify from firmware where you can, set up the revert before the first
write, and record exactly what each write changed. Batching changes is fine. Decide in advance what
"broken" looks like, revert first and investigate after, and be ready to bisect when the user hits
a problem, whether that is right after the write or days later.

Apply/revert testing is a legitimate way to find out, not a last resort. Coding is fully reversible
as long as you hold your signed backup and the diagnostic path answers. What makes it safe is the
discipline below, not luck.

## Why a valid option might not work here

| Cause | What you see | How to catch it before you write |
|---|---|---|
| **Hardware not fitted** (camera, Wi-Fi/combox, MFi auth chip, a tuner, HUD, rear-seat screens, a different display) | Nothing happens, or the HMI waits on a device/service that never answers: a hang, a blank screen, a menu that won't open | Trace the consumer (below): what device, file, or service does the enabled branch open or wait on? Check the car's fitted options. |
| **Different software build** (HMI SWFL or CAFD version) | The coordinate maps to a different bit, so the wrong thing changes; the consumer is missing or behaves differently | Compare your SVK with [versioning.md](../../docs/versioning.md); check the CAFD sha256; regenerate the definitions from your own CAFD ([04](04-definitions.md)). |
| **No consumer in this build** | Nothing happens | [Playbook §5 index](../../docs/investigation-playbook.md#where-codingresource-values-are-consumed-the-5-index): if no binary reads the token, the change is inert. Don't write it. |
| **Part of an interdependent set** | Half-wired: the menu entry appears but its screen fails to load, or the feature starts and then stalls | Read the loader for the feature's full gate list. CarPlay needs three coding gates **plus** an FSC ([examples/carplay.md](../../examples/carplay.md)). |
| **Entitlement missing** | Wired correctly, but the licence check fails and the feature stays dark | [fsc](../fsc/): read the installed FSCs. |
| **Value the consumer doesn't handle** | A default branch, or an index past the end of a table (the video route table has 26 rows; `255` = no route) | Read which enum values the consumer actually switches on. Write only those. |
| **FA-gated / recomputed later** | Works now, then reverts after a later VO/FA recode | The FA-gate caveat in [examples/carplay.md](../../examples/carplay.md#the-fa-gate-caveat-important). |

## Step 0 · Prefer evidence from the firmware

The best way to know whether an option will work is to read the code that consumes it. The method
is the [investigation playbook](../../docs/investigation-playbook.md#worked-example-what-does-coding-value-y-do)
("what does coding value Y do?"), and you are looking for four things:

1. **Is there a reader at all** in *this* build? If there isn't, the change is inert. Say so and
   skip it.
2. **What does the value switch?** For example a route code, a visibility flag, a file suffix, or a
   process or service that gets started.
3. **What does that branch depend on?** A device node, a DSI service, a resource file, another
   coding bit, or an FSC. If it blocks waiting on something this car doesn't have, you have found
   the hang before touching the car.
4. **Which values are handled?** Only write values the consumer has a case for.

Record how you know each fact: **firmware-traced**, **map-only** (from the definitions, not traced),
or **unknown**. That label goes in your report.

Static evidence narrows the experiment but it doesn't replace observing the car. When the firmware
can't settle the question (a stripped binary, or a consumer in a process the carve doesn't contain),
move on to apply/revert testing. That is a sound way to get the answer.

## Step 1 · Set up before the first write

- **Back up** with `read_coding.py` and treat that file as read-only. Name it by date and keep a copy
  off the machine. This file is your revert; it is already correctly signed because it came from
  the car.
- **Stage the revert.** Dry-run `write_coding.py --ncd backup.ncd` now, so the revert is a command
  you have already run once and checked, not one you write while the screen is frozen. Note the
  exact command.
- **Record a baseline** of the unchanged unit:
  - how long a normal reboot takes: `11 01` until the HU is back on its IP, then until UDS answers,
    then until the home screen appears;
  - what the screens you're about to affect look like;
  - which DTCs are already present;
  - an HMI health snapshot: the `HmiMain3D` pid, the core-dump listing, and `sloginfo`
    ([hmi-debugging.md](../../docs/hmi-debugging.md#snapshot-first-because-some-of-it-wont-survive-the-revert)).

  Without a baseline you can't tell a slow boot from a hung one. If you want the revert path proven
  before you need it, one option is to commit the **unchanged** backup once: a zero-delta write
  that runs the whole flow (L3 unlock, signature check, reset) and gives you the reboot timing.
- **Decide how you'll see the screen.** The agent usually can't. You have two options. With
  OPT_DEBUG and SSH, take screenshots of the central display
  ([recipe](../../docs/toolchain.md#screenshotting-the-hmi)), take a baseline shot of each screen
  you're about to affect, and check that `HmiMain3D` is running. Otherwise ask the operator to
  watch and report. Agree beforehand exactly what you need from them, for example "tell me when the
  home screen appears, and whether the iDrive controller responds". The two caveats in the recipe
  apply to every check below:
  - a capture works only once the system has fully booted, so an early failure isn't a hang;
  - one normal-looking frame doesn't prove the HMI is responsive. Compare two shots with a
    controller input in between.
- **The car:** parked, battery healthy or on a charger, nothing else flashing or coding.

## Step 2 · Batch freely, but stay debuggable

You don't have to write one option at a time. Putting everything the user asked for into one
signed write costs one sign, write, reset cycle, and that's usually what the user wants. The cost
of batching only shows up if something goes wrong, because then you have to work out which option
did it (Step 4). So batch in a way that keeps that search cheap:

- **Record the exact delta of every write:** each coordinate with its old and new value, and which
  feature it belongs to. Without this you can't debug later.
- **Group by feature.** Keep interdependent bits together, so a later bisect can split along feature
  lines rather than through the middle of a group.
- **Use judgment on risky options.** An option that is only described by the map (not traced in
  firmware), or one that needs hardware you're not sure is fitted, is the likeliest culprit. You can
  put it in its own write or a later batch so a failure points straight at it. This is a judgment
  call, not a rule.
- Build each NCD from the **last known-good** NCD, never from a broken state. Re-sign it and verify
  it locally ([03](03-write-flow.md)).
- **Keep the artifacts:** the backup, every NCD you wrote, and a log with one row per write:

  | # | Delta (coord: old → new, feature) | NCD file | Write result / NRC | Read-back diff | Observed | Verdict |
  |---|---|---|---|---|---|---|

  Keep them after the session ends. Problems often surface only when the user actually uses the
  feature (opening a menu, plugging in a phone, reversing), and the log is what lets you debug then.

## Step 3 · Apply, observe, and revert on the criteria you set in advance

The HMI reads coding **once, at init** ([plugins/17](../plugins/docs/17-coding-data-path.md)), so
every change has to be observed **after the reset** that ends the write flow. Check these in order:

1. The HU is back on its diagnostic IP and UDS answers (`22 F1 90`) within the baseline time.
2. `read_coding.py` and a diff show **only** the intended delta.
3. The HMI reaches the home screen within the baseline time, confirmed by a screenshot or by the
   operator. Screenshots fail until the boot completes; keep retrying until the margin runs out.
4. The affected feature works: its menus open, its screens load, and it does what you expected.
5. Nothing else regressed: neighbouring features, audio, camera and PDC display, and DTCs compared
   with the baseline.

**Revert immediately**, by writing the last known-good NCD, if any of these happen:

- the HMI doesn't reach the home screen within the baseline plus a generous margin (twice the
  baseline is a reasonable rule of thumb), or it stays black, frozen, or unresponsive to the
  controller;
- the HMI restarts repeatedly (a reboot loop);
- a screen or menu freezes or never loads;
- a safety-relevant display or function regressed (reverse camera, PDC, warning chimes);
- new DTCs appear that relate to the change.

Once you're past the margin, don't keep waiting to see whether it settles, and don't stack another
change on top to fix it. If the shell answers, **take a snapshot first**: it takes seconds, and the
system log is a RAM buffer that the revert's reset will likely wipe. Then **revert, and
investigate offline** with the snapshot and Step 0. [hmi-debugging.md](../../docs/hmi-debugging.md)
helps you tell a hung HMI from a crash loop from a rejected value.

**Reverting while the UI is frozen.** The coding write is served by the diagnostic app
(`NbtEvoOmapDiagHUHighApp`), which is a separate process from the HMI (`HmiMain3D`). See
[plugins/17](../plugins/docs/17-coding-data-path.md). A frozen or crashed UI therefore doesn't by
itself take down UDS. Read the VIN to confirm UDS answers, then write the backup. If UDS doesn't
answer, wait out a full boot and try again, then try an ignition cycle. If the HU still never
answers diagnostics, stop and tell the operator. Recovery at that point is outside this capability
(see the backstop in [flash_and_patching/03](../flash_and_patching/03-flashing-safely.md)).

**A revert is also a write.** Verify it the same way: the read-back diff against the backup must be
empty, and the HMI must return to its baseline behaviour.

## Step 4 · Debug when the user hits a problem

A problem can show up straight after the write (Step 3), or later, when the user reports something
like "the camera view is black" or "the media menu freezes". Start the same way in both cases:

1. **Pin down the symptom.** Which screen, which action, every time or only sometimes? Get a
   screenshot if you can, and a snapshot taken just after the user reproduces the problem:
   `sloginfo`, the `HmiMain3D` pid, and new core files
   ([hmi-debugging.md](../../docs/hmi-debugging.md)). "It's broken" isn't something you can
   bisect. A log line naming the consumer that complained often is.
2. **Find the candidates in the log.** List every write since the last known-good state. If the
   symptom clearly belongs to one feature (the camera view breaks, and you changed video-routing
   bits), revert that feature's group first. That's often the whole fix.
3. **Confirm it's the coding.** If it isn't obvious, revert to the full backup. If the symptom
   persists, the coding isn't the cause. That's worth knowing, and you can tell the user so instead
   of guessing.
4. **Bisect** the delta, as below.

Bisect by halving:

1. Revert to known-good.
2. Split the delta into two halves, **A** and **B**. Keep interdependent groups whole. Splitting a
   group the firmware says must be set together produces exactly the half-wired failure you're
   hunting.
3. Apply **A** alone on top of known-good, then observe (Step 3). If it's bad, the culprit is in A;
   revert and recurse into A. If it's good, recurse into B (either keep A as the new known-good, or
   revert it to keep the two halves independent).
4. Stop when the culprit is a single parameter or a single group. Each round is a full sign, write,
   reset, observe cycle, so *n* parameters take about log₂ *n* rounds. Log every round.
5. **Watch for interactions.** If A alone and B alone are both fine but A + B is bad, the fault comes
   from a combination. Bisect pairs across A and B.

Bisecting by removal finds what **breaks** things. It doesn't help when the problem is "the feature
never appears". In that case a gate is missing, not extra. Go back to Step 0 for the consumer's full
gate list (coding bits, FSC, hardware), or add the missing member of the group.

## Step 5 · Report what actually happened

- Which changes were **firmware-verified**, which were **found by experiment**, and which are
  **unknown**.
- The final state on the car (read back, not assumed), and where the backup and the step log are.
- **What the user should watch for:** the features you changed and where they'd notice a problem,
  and how to get back to stock (the backup). Then a later report can be traced back to the right
  write.
- Anything that **didn't work on this unit**, with the reason if you know it (hardware not fitted,
  no consumer in this build, a missing gate). These are worth contributing back as notes against the
  build and hardware where you saw them.
- Every failed write, with its actual NRC ([AGENTS.md §5](../../AGENTS.md)).

## Honest status

- **Revert = an ordinary signed write** of the car's own NCD, through the same flow as any change.
  It is exactly as trustworthy as the write flow ([03 · Honest status](03-write-flow.md#honest-status)).
- **"UDS still answers when the HMI hangs"** is structural: the diag app and the HMI are separate
  processes in the carve. It is not tested against every failure mode. Confirm UDS answers before
  you rely on it.
- **No timings are given on purpose.** Boot times vary by unit and build, which is why Step 1 has you
  measure your own baseline.
