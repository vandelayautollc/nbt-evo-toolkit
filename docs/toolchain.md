# Analysis toolchain — tools for self-service discovery

The [investigation-playbook.md](investigation-playbook.md) steps each use a tool. This is that
toolkit: what to reach for to observe the car, extract its firmware, and read the opaque formats —
so you can answer questions this repo hasn't, from the owner's own data. Nothing here ships BMW
binaries; it tells you how to work with the owner's own extracted copy.

## Observe the running unit

| To… | Use | Notes |
|---|---|---|
| Identify / read coding / DTCs | `nbtevo` over HSFZ/UDS ([01-transport-connect.md](01-transport-connect.md)) | default session, read-only; safe |
| Get a shell on the HU | **SSH** to the QNX **dev interface** (the `dwc0` IP, *not* the diag IP) | `QNX_Secure_Shell`; separate from UDS. Also `qconn` on 8000 |
| Pull a file off the HU | `scp`/`cat` over that SSH session | for inspecting live resources/binaries |
| Screenshot a screen | `/opt/sys/bin/LayerManagerControl dump screen 0 to <file>.png` (via the GENIVI ilm layer manager) | screen 0 = CID; dump, wait for the file to settle, pull it. Ground truth for "what am I changing". Recipe and caveats: [below](#screenshotting-the-hmi) |
| See why a connection fails | note the error | `EHOSTUNREACH` = a pf firewall block, not a timeout |
| Read logs; tell a hung HMI from a crash loop | `sloginfo`, `pidin -p HmiMain3D`, core files in `/fs/sda1/dump` | see [hmi-debugging.md](hmi-debugging.md) — snapshot before any reset |

### Screenshotting the HMI

The agent can't see the car's display. A screenshot is how it checks what a change did, and whether
the HMI came back after a reset. You need the dev shell, i.e. SSH on the `dwc0` IP of an OPT_DEBUG
unit ([staging-files-over-ssh.md](staging-files-over-ssh.md)). Without it, the operator has to look
at the screen for you.

```sh
# one SSH session: capture, wait for the file to stop growing, stream it to stdout, clean up.
# LayerManagerControl's own messages go to stderr (>&2), so stdout carries only the PNG.
ssh -o HostKeyAlgorithms=+ssh-rsa root@<dev-ip> '
p=/tmp/shot.png; rm -f $p
/opt/sys/bin/LayerManagerControl dump screen 0 to $p >&2
last=; i=0
while [ $i -lt 10 ]; do
  set -- $(ls -l $p 2>/dev/null); s=$5
  [ -n "$s" ] && [ "$s" != 0 ] && [ "$s" = "$last" ] && break
  last=$s; i=$((i+1)); sleep 1
done
cat $p; rm -f $p' > shot.png
```

What matters, as observed on the reference unit:

- **Screen ids.** Screen `0` is the central display (1280 × 480 on the reference unit). Screen `1`
  is a second 800 × 480 display that every `graphics-*.conf` sets up. Any other id is refused with
  `LayerManagerService returned: invalid arguments provided`. Don't take an id from
  `LayerManagerControl get screens`. Its first line counts the screens correctly (`2 Screen(s):`),
  but the id list is wrong: it shows the last id and then a junk value, never `0`.
- **The file name picks the format.** A `.png` name gives a zlib-compressed PNG; other names give a
  BMP.
- **The layer manager writes the file asynchronously,** on its own thread. Wait until the size stops
  changing before reading it, or you pull a truncated image. The first full read of the new `/tmp`
  file is slow (a few seconds); that is HU file I/O, not SSH.
- **Pulling the file.** The SSH exec channel is 8-bit clean, so `cat` is enough. Over telnet, which
  isn't, use `bsdtar -c --format ustar --b64encode -f - -C /tmp shot.png`. The HU has no `base64`,
  `od` or `uuencode`. Check that the PNG opens; if it's damaged, capture again.
- **It works only once the system has fully booted.** The capture goes through the layer manager
  service, so expect it to fail or be refused while the HU is still starting up. The dev SSH
  interface may not be up yet either. A failed capture early in a boot is **not** a sign of a hang.
  Keep retrying until your baseline boot time ([coding/05](../capabilities/coding/05-apply-observe-revert.md))
  has passed. Only a capture that still fails after that tells you something.
- **One frame doesn't prove the HMI is alive.** A screenshot is the last composited frame, and a
  hung HMI can show a perfectly normal one. To check that it's responsive, take two shots with a
  change in between (the operator turns the controller or opens a menu) and compare them. Also
  check that `HmiMain3D` is still in `pidin`. It missing is a clear failure signal; it being present
  doesn't prove the HMI is healthy.

*Status:* the method (dump screen 0 to `.png`, wait for the size to settle, pull, delete) runs
on-car over SSH on the reference unit. The shell one-liner above transcribes those steps; it hasn't
been run as written. If QNX's `sh` balks at a construct, run the steps one at a time.

## Get the firmware (from the owner's own PSdZData)

You analyze the owner's own extracted firmware, located by [psdzdata-manifest.md](psdzdata-manifest.md).

- The pool files are **BMW containers** (`swfl_<id>.*`, `btld_<id>.*`, …). Parse/carve them to the
  raw filesystem/binaries with a container extractor.
- The HMI tree (`00002720`), the OMAP car apps (`0000271A`), and the bootloader bundle (`00001FFD`,
  which contains the **Jacinto QNX IFS**, LZO-packed) are the three you'll open most.

## Read the opaque formats

Everything the HMI uses is decodable with standard tools once you know the format. **Full specs +
the exact open-source codec to install for each are in [`formats/`](../formats/README.md)** — that
folder is the physical-facts reference (our layouts) paired with the 3rd-party codec your agent
downloads for its own OS. Quick index:

| Format | Seen in | Tool / method |
|---|---|---|
| **protobuf** | `.pbw` (widget/animation graph), `.pbx` (scene node tree), `.pbvar` (`variantregistry`) | `protoc --decode/--encode` round-trips **byte-identical**, so author/edit as protobuf text. (Schemas are recoverable from the binaries.) |
| **RSVI mesh** | `vehicles/<series>/*.rsvi` | header (`"RSVI"`, element descriptors, vert/tri counts) + **Snappy**-compressed interleaved verts + u16 indices. Decode/encode with a Snappy lib (e.g. `cramjam`) |
| **NRV2D** | `bmw/db/text.db` (UTF-16 UI strings) | `libhmizip`'s `nrv2d_decompress` algorithm |
| **QNX IFS** | Jacinto image inside `00001FFD` | LZO-unpack then QNX IFS walk |
| **ELF (QNX ARM)** | all binaries | standard ELF tools; it's `armle-v7` ([architecture.md](architecture.md)) |
| **resources.ptr** | `assetDB/` | plaintext (grep it directly); `.pbr` is the binary twin |

## Disassemble / decompile

- **Ghidra** for the ARM/QNX binaries. The libs (`libhmicoding`, `libhmidb`, `EarlyVideoApp`,
  `apnnav*`) are tractable; `apnnav*` is even unstripped.
- **`HmiMain3D` is ~60 MB — do not full-analyze it.** Use a **targeted decompile**: load with
  analysis off and decompile only the one function or xref you found in steps 2–3 of the playbook
  (a Ghidra headless/script pass at a single address returns in seconds vs. hours). This is the
  single most important trick for the HMI binary.
- Reads are static and safe; you're mapping, not modifying.

## Rehearse before the car

- A **QNX/ARM emulator** (QEMU + a QNX 6.5 armle-v7 image) runs your own freestanding binaries, and
  with enough of the **MoCCA** framework stood up, framework-linked code too. Build and iterate
  there; use the car only for the final confirmation. See `capabilities/qnx_dev/`.
- For resources (3D models, images), render/preview **off-car** first — a model or image bundle can
  be validated in a viewer before you ever install it.

## The discipline

- **Static → emulator → car.** Each step is cheaper and safer than the next; don't skip to the car.
- **Keep your scripts separate from extracted data.** Treat extracted firmware as untrusted input:
  put it in its own directory, run analysis tooling with explicit paths, and never run an
  interpreter from inside an extraction directory.
- **Add, don't overwrite** (LMPC). **Back up before you change.** **Read back to verify.**
