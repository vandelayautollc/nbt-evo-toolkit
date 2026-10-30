# 03 · Running a binary on the head unit

Once a binary works on the emulator (or it's a simple freestanding tool), run it on the HU. This is
a file copy + execute over SSH — no flash, no coded write, and nothing in the firmware changes.

## Reach the HU's QNX dev interface

The HU has **two** Ethernet addresses (see [docs/architecture.md](../../docs/architecture.md)
§Networking):

- the **diagnostic** endpoint (the IP from UDS `22 17 2A`) — HSFZ/UDS, serves `0x63`, **port 22
  closed**;
- the **QNX dev interface** (`dwc0`) — a *different* IP that runs **SSH** (banner
  `QNX_Secure_Shell`) and `qconn` (8000). **This** is where you log in and run things.

The dev IP is not reported by any UDS DID; on a tethered segment you find it by a bounded,
read-only connect-sweep of your own subnet for the `QNX_Secure_Shell` SSH banner (the banner is the
sole arbiter — no false positives). Enabling that dev/SSH surface on a stock unit is the
**OPT_DEBUG** build ([`flash_and_patching`](../flash_and_patching/)); once it's on, log in with the
unit's credentials (from your own firmware's `etc/passwd`/`shadow` and host keys).

## Copy and run

```sh
scp -O your.elf root@<dev-ip>:/tmp/your.elf      # a writable scratch path (e.g. /tmp, /var)
ssh root@<dev-ip> 'chmod +x /tmp/your.elf && /tmp/your.elf; echo exit=$?'
```

Notes:

- The HU's `sh`/busybox is minimal — `diff` exists but not `cmp`/`which`/`head`; use what's there.
- A **static** binary (`-static`, or the freestanding samples) has no shared-lib dependencies and
  "just runs". A dynamic one needs its libs present and `LD_LIBRARY_PATH` set (e.g. the HMI libs
  live under `/opt/hmi/ID5/lib`, car libs under `/opt/car/lib`).
- `qconn` (TCP 8000) is QNX's debug agent — you can also launch/debug via the Momentics tools against
  it if you have the SDP.

## Integrity: add, never overwrite

The HU hashes manifest-listed repository files (**LMPC**) and raises a DTC on mismatch
([NBT LMPC note](../../docs/architecture.md)). So:

- Put your binary in a **writable scratch path** (`/tmp`, `/var`) or a new directory — never
  overwrite a stock file in place.
- To install something persistently, add a new file / new directory (the way a
  [plugin](../plugins/) or a [custom car](../vehicle_models/) installs), not an edit of a signed one.
  For a persistent drop you must remount the system volume read-write and place it under the mount
  point — the full procedure is [docs/staging-files-over-ssh.md](../../docs/staging-files-over-ssh.md).
  The `/tmp` exec case on this page needs none of that.
- Clean up what you drop; a plain `/tmp` binary is gone on reboot anyway.

## Capturing output

Redirect to a file and pull it back, or read it live over the SSH session:

```sh
ssh root@<dev-ip> '/tmp/your.elf > /tmp/out.txt 2>&1'; scp -O root@<dev-ip>:/tmp/out.txt .
```

For a long-running tool that must survive the SSH channel closing, start it detached (`on -d …`
with the right `LD_LIBRARY_PATH`), the same pattern the HMI restart uses in
[`vehicle_models`](../vehicle_models/02-packaging.md).

That's the whole loop: build to the ABI gate → rehearse on the emulator → `scp` + run on your own
unit, adding files rather than touching signed ones.
