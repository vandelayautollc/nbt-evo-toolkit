# NBT EVO Toolkit

Reverse-engineering notes and tooling for the **BMW NBT EVO** head unit — enough for a competent
agent (human or AI) to reproduce, on **their own car**, the full set of owner-authorized
modifications: changing coding, reading/creating/applying feature codes, flashing and patching,
building QNX software, writing HMI plugins, and installing custom 3D vehicle models.

> ### ⚠️ One rule, before anything else
> **Only use this on a vehicle you own, or one whose owner has explicitly authorized you to
> modify.** This is interoperability tooling for an owner working on their own car over a local
> (OBD/Ethernet) connection. It is not for cars you don't own. Read **[LEGAL.md](LEGAL.md)** — it
> is a hard precondition, not boilerplate.

## What's in the box (and what isn't)

This repo ships **method, tooling, validators, our reverse-engineered facts** (format specs + the
coding definitions). It ships **no** manufacturer data:

| Ships here ✅ | You supply ❌ (from your own licensed copy, for your own car) |
|---|---|
| How each mechanism works (docs) | PSdZData (BMW's config/firmware/coding distribution) |
| Scripts that operate on *your* data | Your **CAFD** coding layout — it lives *inside* PSdZData above (your **NCD** isn't supplied at all: the tools read it off your own car) |
| Our **coding definitions** (what each var does) + **file-format specs** | Your recovered signing key (the scripts recover it locally from your PSdZData) |
| Validators that check *your* results · File **names + hashes** to locate inputs | The firmware/flash binaries themselves |

Open-source codecs the format specs rely on (LZO, NRV2D, Snappy, protobuf, QNX-IFS) are
**referenced, not vendored** — your agent installs them for its own OS (see [`formats/`](formats/)).

See **[docs/psdzdata-manifest.md](docs/psdzdata-manifest.md)** for exactly which files you need and
how to confirm you have the right ones.

## The hardware this targets

**NBT EVO** (a.k.a. "NBT2", `HU_NBT2`) — the 2016–2020-era BMW head unit. QNX-based HMI on an
OMAP + Jacinto + V850 stack, reached for diagnostics over OBD-II or ENET (Ethernet) using
HSFZ/UDS. If your car has the earlier NBT (not EVO), the entry-level `HU_ENTRY`, or the later MGU
(iDrive 7/8), the *methods* here will rhyme but the specifics (addresses, keys, container formats)
will differ — see [docs/00-platform-overview.md](docs/00-platform-overview.md) to tell which you
have.

## Capabilities

Each folder under `capabilities/` is self-contained: a concept doc, the scripts, and a validator.

| Capability | What it lets an owner do | Status |
|---|---|---|
| **[coding](capabilities/coding/)** | Read and change coding (feature toggles, regional settings), understand and reproduce the coding **signature** so changes survive a reboot | ✅ fully worked |
| **[fsc](capabilities/fsc/)** | Read/understand feature codes (FSC); on your own unit, mint + apply them under your own trust anchor (blobB) | ◑ mint/verify/read + catalog (tested); car-write steps documented |
| **[flash_and_patching](capabilities/flash_and_patching/)** | Enable developer/debug builds (OPT_DEBUG), author `.swdl` patches (incl. the fsc blobB swap), and flash them | ◑ container/patch tooling + validator + flash-plan (tested); live flash is a runbook |
| **[qnx_dev](capabilities/qnx_dev/)** | Build your own QNX/ARM binaries and run them on the HU (and on an emulator first) | ✅ toolchain + ABI gate + buildable sample + docs |
| **[plugins](capabilities/plugins/)** | Write HMI plugins that add UI and behavior to iDrive | ✅ full SDK (18 docs + headers + example plugin) |
| **[vehicle_models](capabilities/vehicle_models/)** | Generate a custom 3D vehicle model and install it as your car's iDrive hero image | ◑ authoring + packager (selftest-proven); SSH installer next |

**Worked examples** (`examples/`) combine capabilities into one real outcome:
- **[examples/carplay.md](examples/carplay.md)** — activate Apple CarPlay: the CarPlay **FSC**
  (`0x0143`) *plus* the coding bit the firmware checks (`CARPLAY_SWT`), in order, with how to
  confirm each half took. A good model for "feature X needs entitlement **and** coding".

`docs/` holds the cross-cutting foundation every capability builds on:
- **[00-platform-overview.md](docs/00-platform-overview.md)** — quick orientation: is this an NBT EVO, and how do you reach it
- **[01-transport-connect.md](docs/01-transport-connect.md)** — ENET/HSFZ discovery and the UDS session everything rides on
- **[architecture.md](docs/architecture.md)** — the deep map: processors, QNX + ABI, the HMI engine stack, and what each firmware binary does
- **[resource-pipeline.md](docs/resource-pipeline.md)** — how the HMI decides *what it shows* (the enabler for "how do I change X image/text/sound")
- **[investigation-playbook.md](docs/investigation-playbook.md)** — the **method** for answering a question this repo hasn't pre-solved
- **[toolchain.md](docs/toolchain.md)** — the analysis tools for self-service discovery
- **[capability-map.md](docs/capability-map.md)** — a one-screen index for agents
- **[psdzdata-manifest.md](docs/psdzdata-manifest.md)** — the files you supply, by name + hash
- **[keys.md](docs/keys.md)** — every key: what it does, where it comes from, which action needs it
- **[versioning.md](docs/versioning.md)** — the reference build, what transfers to other SWFL/CAFD versions, and what you re-verify (offsets, coordinates, keys, node names)
- **[staging-files-over-ssh.md](docs/staging-files-over-ssh.md)** — the shared file-install path: root shell, remount rw, place/rename-over, restart, verify (plugins + custom cars use it)
- **[hmi-debugging.md](docs/hmi-debugging.md)** — logs and HMI health: where the HU logs, how to tell a hung HMI from a crash loop from a rejected value, and what to snapshot before a revert

### The capabilities are examples, not the boundary

Each `capabilities/` folder is a **worked example of a general method**, not the limit of what this
head unit allows. If you're asked for something not covered below — "change this other image",
"what does this coding value do", "enable this behavior" — read **[architecture.md](docs/architecture.md)**
and **[investigation-playbook.md](docs/investigation-playbook.md)** and go find it in the system.
The repo is built to teach you where to look, so a more capable agent isn't fenced in by our recipes.

## Quick start

```bash
# 1. Read the rule.
less LEGAL.md

# 2. Install the shared library (editable) so the capability tools can import it.
pip install -e .

# 3. Tell the toolkit which car is yours. Nothing that writes to a car, or recovers a
#    key, will run until this is set and matches the connected vehicle's VIN.
export NBTEVO_OWN_VIN=YOURVINHERE          # the VIN on YOUR title/registration

# 4. Point the toolkit at your own extracted PSdZData (and, for key recovery, your own PSdZ
#    resource.jar — the keystore password is derived from it, never typed; see docs/keys.md).
export NBTEVO_PSDZDATA=/path/to/your/psdzdata
export NBTEVO_PSDZ_RESOURCE_JAR=/path/to/your/PSdZ/bin/psdz/resource.jar

# 5. Start with a read. Reads are always safe and need no consent gate.
python -m capabilities.coding.tools.identify_btld --host 169.254.x.x
```

## For AI agents

Start at **[AGENTS.md](AGENTS.md)**. It tells you how to navigate the repo, the preconditions you
must confirm with the operator, and the order to do things in.

## Status

Extracted from a large private research tree. **All six capabilities now have landed tooling or an
SDK**, not just outlines: **coding** (sign/verify proven against the car's own NCD), **plugins** (a
full 18-doc HMI SDK + example plugin), and **qnx_dev** (toolchain + a sample that builds to the
exact target ABI) are complete; **vehicle_models**, **fsc**, and **flash_and_patching** have their
offline tooling + validators done, with the car-*write* step (install / apply / flash) as a precise
runbook keyed to the owner's own key and car. See each folder's README for its state.

## License & use

The code and documentation in this repository are open source under the **[MIT License](LICENSE)**.

**No-harm disclaimer.** This is interoperability tooling for an owner working on their own vehicle.
It is not intended for, and must not be used to, harm anyone; touch a vehicle or system you don't
own or aren't authorized to modify; defeat safety, theft/immobilizer, or emissions controls; or do
anything unlawful. See **[LEGAL.md](LEGAL.md)**. This is the project's statement of intended use and
of your own legal responsibility; the license itself is plain MIT.

It ships no manufacturer firmware, data, or keys, and the license grants no rights in any; you
supply your own and must not redistribute them. Provided with no warranty — modifying vehicle
electronics is entirely at your own risk.
