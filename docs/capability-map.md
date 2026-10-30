# Capability map (for agents)

A one-screen index: task → where to go. Read [AGENTS.md](../AGENTS.md) first for the preconditions.

## Orientation (always do these first)

| You want to… | Go to | Needs a car? | Writes? |
|---|---|---|---|
| Confirm it's an NBT EVO; quick stack intro | [docs/00-platform-overview.md](00-platform-overview.md) | no | no |
| Get on the wire; read VIN/SVK/BTLD/CAFD | [docs/01-transport-connect.md](01-transport-connect.md) | yes | no |
| Understand the system deeply (the map) | [docs/architecture.md](architecture.md) | no | no |
| Know which PSdZData files to supply | [docs/psdzdata-manifest.md](psdzdata-manifest.md) | no | no |
| Know which key an action needs (+ recover it) | [docs/keys.md](keys.md) | no | no |
| Know if a bundled offset/coordinate fits your build | [docs/versioning.md](versioning.md) | no | no |

## No recipe for your task? (the common case)

The capabilities below are **worked examples of a method**, not the whole of what's possible. For
anything not listed — a different image/text/sound, an undocumented coding value, a behavior with no
knob — don't stop:

| You want to… | Go to |
|---|---|
| Change what the HMI *shows* (image, 3D car, text, audio variant) | [docs/resource-pipeline.md](resource-pipeline.md) |
| Answer "how do I change / find X?" in general | [docs/investigation-playbook.md](investigation-playbook.md) |
| Know which tool to use for a step | [docs/toolchain.md](toolchain.md) |

## Capabilities

| You want to… | Go to | Writes to car? | Key precondition |
|---|---|---|---|
| Read current coding | `capabilities/coding/` (`tools/read_coding.py`) | no | transport only |
| Change coding so it survives reboot | `capabilities/coding/` (concepts → signing → write-flow) | **yes** | your recovered signing key; a backup |
| Understand what a coding parameter means | `capabilities/coding/04-definitions.md` | no | your own CAFD |
| Test whether a coding change works on *this* unit (apply/observe/revert, bisect) | `capabilities/coding/05-apply-observe-revert.md` | **yes** | a staged, signed backup; a baseline boot |
| Screenshot the HMI (see what a change did) | `docs/toolchain.md` → Screenshotting the HMI | no (SSH read) | HU dev access (OPT_DEBUG); a fully booted HU |
| Read logs / core dumps / DTCs; tell hung from crashed from rejected | `docs/hmi-debugging.md` | no (reads) | HU dev access for logs; UDS for DTCs |
| Read / create / apply a feature code (FSC) | `capabilities/fsc/` | **yes** (apply) | your own FSC data |
| Enable developer/debug build (OPT_DEBUG) | `capabilities/flash_and_patching/` | **yes** (flash) | BTLD/key match; a backup |
| Understand or author a flash patch (`.swdl`) | `capabilities/flash_and_patching/` | **yes** (apply) | correct target SWFL |
| Build a QNX binary and run it on the HU | `capabilities/qnx_dev/` | no (SSH, not diag) | QNX SDK; HU dev access |
| Add UI/behavior via an HMI plugin | `capabilities/plugins/` | no (file install) | HU dev access |
| Install a custom 3D vehicle model | `capabilities/vehicle_models/` | no (file install) | HU dev access |
| Stage/install any file on the HU over SSH | `docs/staging-files-over-ssh.md` | no (file install) | HU dev access (OPT_DEBUG) |

## The rule of thumb for "will this stick?"

A raw byte edit that isn't **re-signed** (coding) or **flashed through the authenticated path**
reverts on the next boot. Durability on the NBT EVO always comes from a valid signature or an
authenticated write — never from poking volatile state. Each capability's doc says what "durable"
requires for that mechanism.

## …and "will this work on *this* car?"

Durable is not the same as working. A correctly signed, durable coding change can still be inert,
or it can hang the UI, on a unit whose hardware or build doesn't match what the option expects.
Confirm it from the consuming firmware, or apply it, watch, and revert
([coding/05](../capabilities/coding/05-apply-observe-revert.md)).

## Status legend

- ✅ fully worked — concept + tools + validators present and exercised.
- 🔜 outline — the mechanism is documented and pointed to; tools are being ported in.

Current: **coding ✅**; **plugins ✅** (full HMI plugin SDK + example); **qnx_dev ✅** (toolchain +
ABI gate + buildable sample); **vehicle_models ◑** (authoring tools + `.nbtcar` packager,
selftest-proven; full authoring layer `tools/{mesh,scene_template,widget_expr,author}.py` + the all-features `examples/blueprint/`; shared SSH install procedure in `staging-files-over-ssh.md`); **fsc ◑** (mint/verify/read + feature catalog, tested;
blobB-patch + apply documented); **flash_and_patching ◑** (container/patch tooling + validator +
flash-plan, tested; live flash is a runbook). All capabilities now have landed tooling or SDKs.
