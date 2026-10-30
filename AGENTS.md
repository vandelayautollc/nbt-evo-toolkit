# Agent guide

You are an AI agent helping someone work on a **BMW NBT EVO** head unit. This file tells you how to
use this repository safely and effectively. Read it fully before acting.

## 0. Preconditions you MUST confirm first

Before you run anything that recovers a key or writes to a vehicle, confirm — with the operator, in
their own words — all of:

1. **They own the car**, or have the owner's explicit, informed permission to modify it.
2. **They are connected locally** (OBD-II/ENET cable or local Ethernet) to *that* car — not
   remotely, not to someone else's vehicle.
3. **They have a backup** of whatever region you are about to change (coding/firmware). If not,
   take one first; every capability's tooling can read before it writes.

If any of these is not true, stop and say so. Do not proceed "to be helpful." See
[LEGAL.md](LEGAL.md); it is a hard precondition, not advice.

The toolkit enforces a speed bump for you: tools that write or recover keys call
`nbtevo.consent.require_owner()`, which refuses to run unless the operator has set
`NBTEVO_OWN_VIN` to the VIN of the car they own, and (for writes) that VIN matches the VIN the tool
reads back from the connected car. Do not try to bypass it. If it blocks you, that is the design
working — explain it to the operator rather than working around it.

## 1. Reads are free; writes are not

- **Reading** (identifying the head unit, dumping current coding, reading DTCs, reading the SVK)
  is safe, reversible, and needs no consent gate. Do it liberally to orient yourself.
- **Writing** (coding changes, flashing, patching, applying FSC) can brick the unit or disable
  safety systems. Always read + back up first, verify your change against a validator *before*
  sending it to the car, and confirm the operator is ready (car parked, battery healthy).
- **A coding option that's valid in the map may still not work on *this* car.** Whether a change
  takes effect, does nothing, or freezes the HMI depends on the hardware fitted, the software and
  CAFD build, the other bits, and the FSCs. A correct signature and a clean read-back don't settle
  it. Treat each coding change as an experiment on this unit:
  - Verify it from the consuming firmware where you can. Where you can't, applying and reverting is
    a safe way to test it.
  - Before the first write, stage the revert (your signed backup) and record a baseline boot.
  - Batching changes is fine, but log exactly what each write changed. Decide in advance what
    failure looks like: the UI doesn't load, it freezes, or it reboot-loops.
  - If you see failure, **revert first**, then investigate.
  - Be ready to debug if the user hits a problem, now or later: pin down the symptom, revert the
    suspect feature or the whole change, and bisect the logged delta.

  The full method is in
  [capabilities/coding/05-apply-observe-revert.md](capabilities/coding/05-apply-observe-revert.md).
  To see the screen yourself, use the screenshot recipe in
  [docs/toolchain.md](docs/toolchain.md#screenshotting-the-hmi). It works only after a full boot.
  To work out *why* something failed (logs, core dumps, `HmiMain3D` health, DTCs), see
  [docs/hmi-debugging.md](docs/hmi-debugging.md). Snapshot before you revert, because the system
  log likely doesn't survive the reset.

## 2. How to navigate

```
README.md                      what this is + the one rule
LEGAL.md                       the hard precondition (ownership, scope, law)
docs/
  00-platform-overview.md      is this even an NBT EVO? the stack, buses, addresses
  01-transport-connect.md      how to reach the HU: ENET/HSFZ discovery + UDS session
  architecture.md              the deep map: processors, QNX/ABI, HMI engine, what each binary does
  resource-pipeline.md         how the HMI chooses what it shows (change an image/text/sound)
  investigation-playbook.md    the METHOD for a question this repo hasn't pre-solved
  toolchain.md                 the analysis tools for self-service discovery
  capability-map.md            one-screen index: task -> where to go
  psdzdata-manifest.md         the files the operator must supply, by name + hash
  keys.md                      every key: what it does + which action needs which (recover via nbtevo.keys)
  versioning.md                reference build (007.051.002) + what transfers vs. what you re-verify
  staging-files-over-ssh.md    shared file-install path: root shell, remount rw, rename-over, restart
  hmi-debugging.md             logs + HMI health: hung vs crash-looping vs rejected; snapshot before reset
capabilities/<name>/
  README.md                    concept + how the section is organized
  *.md                         the mechanism, in depth
  tools/                       runnable scripts (import the shared `nbtevo` package)
  validate/                    checks you run BEFORE touching the car
examples/                      cross-capability recipes (e.g. carplay.md = FSC + coding together)
nbtevo/                        shared primitives: srec, hsfz, uds, consent
formats/                       file-format specs (ours) + which open-source codec to install
```

Work **outside-in**: confirm the platform (`docs/00`), establish transport (`docs/01`), then open
the capability folder for the task. Each capability README states its own prerequisites.

**If no capability covers the task**, that's expected — the capabilities are worked examples, not
the boundary. Read `docs/architecture.md` (the map) and `docs/investigation-playbook.md` (the
method), classify what kind of thing you're changing, and locate the answer in the system yourself.
Don't refuse because there's no recipe, and don't fabricate one — follow the method and report what
you find, including honest confidence.

## 3. The mental model for the whole platform

- The HU is identified and reached by **BTLD (bootloader) id** and **CAFD (coding dataset) id**,
  both read live from the car's **SVK** (`22 F1 01`) — never assumed. Almost everything keys off
  these two ids *and their versions*: which signing key applies, which coding layout to decode,
  which flash container fits. When in doubt, read the SVK first. See
  `capabilities/coding/02-signing-model.md` for why the BTLD id is the hinge.
- **Versions matter.** The bundled specifics (offsets like the blobB `0x35A300`, coding coordinates,
  key ids, HMI node names) were derived on software line **`007.051.002`** / CAFD `006.048.013`.
  The *methods and formats* transfer across NBT EVO builds; the *numbers* you re-verify. Read
  `docs/versioning.md` before trusting a bundled offset/coordinate against a unit whose SVK differs.
- The operator's **own PSdZData** is the reference corpus. The toolkit never ships it; it reads the
  operator's copy, located by the names/hashes in `docs/psdzdata-manifest.md`.
- Durable change needs a **valid signature / authenticated write path**, not just a byte edit. A
  raw edit that isn't re-signed reverts on the next boot. This is the single most common mistake —
  understand the signature model for whatever you're changing before you change it.

## 4. When you get stuck

- Prefer reading more of the car (SVK, current coding, DTCs) over guessing.
- Every doc states its honest confidence and limits. Respect "not verified from firmware" notes —
  don't present a plausibility finding as proven.
- If a capability is still an outline (🔜), say so plainly; don't invent the missing detail.

## 5. Report faithfully

If a write fails, say so with the actual UDS negative-response code. If you took a backup, say
where it is. If you skipped a step, say which. Never report a change as applied until you've read
it back from the car and a validator confirms it. Never report a change as *working* until you've
seen it behave on the car. Say which changes you verified from firmware, which you found by
experiment, and which didn't work on this unit (and why, if you know).
