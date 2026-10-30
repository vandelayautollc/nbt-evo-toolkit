# Architecture reference — the NBT EVO head unit

This is the **map**. It describes how the head unit is built so you can reason about a question this
repo hasn't pre-answered. If you're an agent asked to do something not covered by a capability
folder, read this and [investigation-playbook.md](investigation-playbook.md), then go look in the
right place in the firmware — don't guess, and don't assume our capability recipes are the limit of
what's possible.

Confidence: facts here are from the unit's own binaries and on-car behavior unless tagged
**(hypothesis)**. The firmware itself is not shipped — you work from the owner's own extracted copy
(see [psdzdata-manifest.md](psdzdata-manifest.md)).

## Processors — three brains, one module

| Processor | What runs on it | Why you care |
|---|---|---|
| **TI OMAP5432** (dual ARM Cortex-A15, ARMv7-A, PowerVR SGX544 GPU) | **QNX** + the whole **HMI** ("iDrive"), plus the OMAP "car" apps | Where UI, coding consumers, plugins, and 3D models live. Your target for almost everything visible. |
| **TI Jacinto** (DRA7xx) | media/graphics/audio processing, the **diagnostics dispatcher**, `AudioProcess` (inside an LZO-packed QNX IFS) | Audio routing, video sources, and the path inbound UDS takes to reach the HMI. |
| **Renesas V850 / RH850** ("IOC") | always-on **gateway** to the car's CAN buses; keeper of the **durable** coding/nvram tier | Durability: a change is only permanent once the V850 commits it (signed-diag flush / controlled shutdown). A volatile shell poke never sticks. |

The OMAP is the "car/master" node (`hu-omap`); it talks to a Jacinto/display node over **qnet**.

## Operating system and ABI — the porting gate

- **QNX Neutrino RTOS 6.5.0 SP1** — kernel `procnto-smp-instr`; loader `/usr/lib/ldqnx.so.2`;
  `libc.so.3`, `libm.so.2`, `libsocket.so.3`, `libstdc++.so.6` (GCC 4.4 C++ ABI).
- **Toolchain: GCC 4.4.2 / QNX SDP 6.5.0.** This pins the SDP version for anything that links QNX.
- **Binary ABI (the hard gate for any drop-in binary):** ELF32, little-endian, **ARMv7-A**, EABI5,
  **soft-float base AAPCS** (FP args in core registers, even though VFP/NEON instructions are used).
  QNX triplet **`ntoarmv7le`** (`qcc -Vgcc_ntoarmv7le`). Hard-float, AArch64, or Linux/glibc
  binaries will **not** load. `HmiMain3D` is non-PIE (fixed load `0x00100000`); shared libs are PIC.
- See `capabilities/qnx_dev/` for building to this target.

## HMI engine stack

From most to least certain:

- **GLES2 + EGL** on the **PowerVR SGX544**; QNX **Screen** compositor; GENIVI **ilm** layer manager
  (layers/surfaces — how a window gets on screen). **(confirmed)**
- **MoCCA** — BMW's C++ application framework the HMI apps are built on. **(confirmed)**
- **GENIVI CommonAPI over SOME/IP** + BMW **DSI / servicebroker** for inter-service calls;
  internal codename "Colibry". **(confirmed as present)**
- HMI scene graph **"Ines"** (C++, `Ines::CInes*`) + widget layer **"Populus"** + **Lua 5.1.4** for
  logic. The *names* are in the binaries; the *vendor* of Populus is unconfirmed **(hypothesis)**.
  What matters for you is the **resource formats** they consume — see
  [resource-pipeline.md](resource-pipeline.md).

Practical consequence: the HMI is **data-driven**. Most of what you'd want to change (images, text,
3D cars, layouts, which feature shows) is selected by **resources and coding**, not hard-coded in
`HmiMain3D`. Start at the resource pipeline, not the disassembler.

## Filesystem layout (on `hu-omap`)

| Path | Holds |
|---|---|
| `/fs/sda0` | the eMMC root; most other paths are hard-links back into here |
| `/opt/hmi/ID5/data/ro` | the HMI's read-only resource tree (`assetDB/`, `bmw/`, `common/`, `db/`) |
| `/opt/car/bin` | the OMAP "car" apps (`EarlyVideoApp`, `EarlyICam2App`, nav, …) |
| `repository/istep/opt/hmi/…` | the layered repository the live tree is composed from |
| `/dev/shmem/sysetpage` | shared-memory mirror of coding the HMI reads at runtime (layout unverified) |
| `/etc/pf.conf`, `/etc/pf_OBD_dwc0.conf` | the packet-filter ruleset (see Networking) |

**Integrity: files are hard-links to manifest-listed repository files, hashed by LMPC** (a link
manager that raises a DTC on mismatch). So **never overwrite a stock file in place** — add a new
file, rename a new file over the live link, or add a new variant/series folder. This rule governs
every "install" in this repo. (`capabilities/*/` all respect it.)

## The binaries, and what each is responsible for

This table is the "where do I look?" index. Binaries live under the extracted firmware
(`00002720` = HMI, `0000271A` = OMAP core/media, `00001FFD` = bootloader bundle incl. the Jacinto
IFS).

| Binary / lib | Responsibility | Look here when… |
|---|---|---|
| `HmiMain3D` | the HMI itself (scene graph, widgets, rendering). ~60 MB — never full-analyze; use targeted decompile | a screen/asset/behavior is drawn and you need the exact resolver |
| `libhmicoding.so` | coding → HMI: the `va_<TOKEN>_<value>` table, `isVariantSet(id)`/`getVariantVal(id)`, variant flag ids | a feature/asset is gated by coding; mapping variantFlag↔coding |
| `libhmidb.so` | resource bundle registry (`readResourceBundle`, `setDynamicStreamResourceData`) — last registration wins | you need to override an asset without editing stock |
| `libhmizip.so` | `nrv2d` (de)compression for `text.db` | reading/writing HMI UI strings |
| `sysetshellevo` | on-device coding shell + the syset descriptor table (BMW engineering tokens, enum value names) | recovering a coding parameter's real name/values |
| `EarlyVideoApp` / `EarlyICam2App` | video source/route coding consumers (`CPVideoRouting::getRoute` 26-row table), startup emblem | camera/video/reverse-image behavior |
| `apnnav*` | navigation (not stripped: `nbt_coding_if_get<TOKEN>`) | nav-gated behavior; a readable example of a coding consumer |
| `AudioProcess` (Jacinto IFS) | audio processing; `EQ_VARIANT` → `/data/mm/eqdata/<series>_<sys>_VARIANT<n>.bin` | sound/EQ behavior |
| `LayerManagerControl` | ilm layer/screen control (also how you screenshot a display) | compositing, screenshots, drawing your own layer |
| `pf` ruleset | the HU firewall | a port/service is unexpectedly unreachable (`EHOSTUNREACH` = a pf block) |

## Networking

- The HU has **two Ethernet interfaces** on the tethered segment:
  - the **diagnostic** endpoint (the IP from UDS `22 17 2A`) — HSFZ/UDS, serves `0x63`. Port 22 closed.
  - the **QNX dev** interface (`dwc0`) — a *different* IP, runs **SSH** (`QNX_Secure_Shell`) and
    `qconn` (8000). This is the dev/plugin/3D-model install path; it is **not** discoverable from
    UDS and does not route diagnostics.
- **pf firewall**: default-drop on `dwc0`; BMW passes a fixed short list (ssh/telnet/qconn/6801/6811
  /NetBIOS/DHCP/…). A locally-dropped packet surfaces as `EHOSTUNREACH`, not a timeout — that error
  is the signature of a pf block, useful when debugging why something can't connect.
- Nodes talk over **qnet**.

## Where the subsystems you'll want live

- **Coding** (feature toggles, regional, UI options): `capabilities/coding/` — consumed by
  `libhmicoding` + the apps above; durable via the signed UDS path.
- **FSC** (paid-feature entitlement) + BlobB: `capabilities/fsc/` — one statically-linked userspace
  service validates per-VIN tokens against a trust store.
- **Flashing / patches** (OPT_DEBUG, software areas): `capabilities/flash_and_patching/`.
- **Your own code**: `capabilities/qnx_dev/`. **UI plugins**: `capabilities/plugins/`. **3D cars**:
  `capabilities/vehicle_models/`.

For *how to approach a question none of these cover*, go to
[investigation-playbook.md](investigation-playbook.md).
