# Staging files on the head unit over SSH

The canonical "how do I get a file onto the HU and make it stick" reference. Plugins, custom-car
models, and your own QNX binaries all install the same way: reach a root shell, make the system
volume writable, place **new** files (or rename-over, never edit-in-place), restart the HMI, verify,
and restore the mount state. This doc is the shared mechanism; each capability's own doc says *which*
files go *where*.

> **Your own car only.** This is a local root shell on an embedded computer you own. Nothing here
> touches a network or vehicle you don't. See [../LEGAL.md](../LEGAL.md).

## Prerequisite: a root shell on the dev interface

The HU has **two** Ethernet addresses (see [architecture.md](architecture.md) §Networking):

- the **diagnostic** endpoint (IP from UDS `22 17 2A`) — HSFZ/UDS only, **port 22 closed**;
- the **QNX dev interface** (`dwc0`, a *different* IP) — runs **SSH** (banner `QNX_Secure_Shell`)
  and `qconn` (TCP 8000). **This** is where you log in.

That dev/SSH surface is part of the **developer build**: on a stock unit you enable it with
**OPT_DEBUG** ([`../capabilities/flash_and_patching/`](../capabilities/flash_and_patching/)). Find
the dev IP by a bounded, read-only connect-sweep of your own tethered subnet for the
`QNX_Secure_Shell` banner (the banner is the sole arbiter). Log in as root with your own unit's
credentials (from your firmware's `etc/passwd`/`shadow` and host keys). A modern client needs the
legacy host-key algorithm re-enabled:

```sh
ssh -o HostKeyAlgorithms=+ssh-rsa root@<dev-ip>
```

> **Login-rate cap.** `inetd` throttles SSH: too many logins in a short window (observed ≈ >40/min)
> gets the service cut for ~10 minutes. **Batch your work into few sessions** — open one shell and
> run a script, or pipe a compound command — rather than one `ssh` per command.

## The filesystem map

| Path | What it is |
|---|---|
| `/fs/sda0` | the system data **volume** (device `/dev/hd0t177`); **mounted read-only** in normal use |
| `/fs/sda0/opt/hmi/ID5/data/ro` | the **live** HMI data tree — what the HMI actually reads (`ID5`/`ID6…` by HMI line) |
| `/fs/sda0/repository/istep/opt/hmi/ID5/data/ro` | the **repository** — the signed source `LinkManagerHU` builds the live tree from |
| `/opt/hmi/data/ro` | a **symlink** onto the live tree; `/opt` resolves onto `/fs/sda0` |
| `…/data/ro/Plugins/` | where an uncoded [plugin](../capabilities/plugins/) folder goes (absent on a stock image — you create it) |
| `…/data/ro/vae/vehicles/<id>/` | a [custom car](../capabilities/vehicle_models/)'s own folder (new namespace, nothing stock) |
| `/tmp`, `/var` | writable scratch; **`/tmp` is RAM, wiped on every HMI restart/reboot** |

Persistence: files under `/fs/sda0` survive reboots; `/tmp` does not. The HU's `sh`/busybox is
minimal — `diff` exists, but **no hash tool**, and no `cmp`/`which`/`head`. Use what's there.

## Step 1 — make the volume writable

```sh
mount -uw /fs/sda0      # remount read-WRITE  (-u = update in place)
#   … do your writes …
mount -ur /fs/sda0      # restore read-only when done
```

> **Write under the remounted mount point, not through `/opt`.** `/opt` is a *different* filesystem;
> a bare `mkdir -p /opt/hmi/...` can land on the wrong mount. Do every `mkdir`/copy/`mv`/`rm` under
> the real path, e.g. `/fs/sda0/opt/hmi/ID5/data/ro/...`. Confirm the backing path for your unit
> first: `ls -l /opt/hmi/data/ro` shows where the symlink points.

## Step 2 — move the files in

Stage into `/tmp` first, then `mv` into place under the remounted volume. Two transports:

**A — a whole folder, via a tar pipe (proven).** The HU has `bsdtar`:
```sh
# push: stream a local tar into a scratch dir on the HU
ssh -o HostKeyAlgorithms=+ssh-rsa root@<dev-ip> 'rm -rf /tmp/stage && mkdir /tmp/stage'
ssh -o HostKeyAlgorithms=+ssh-rsa root@<dev-ip> 'cd /tmp/stage && bsdtar -xf -' < payload.tar
```
**B — a single file, via scp:**
```sh
scp -O your.file root@<dev-ip>:/tmp/
```
Then, in one shell, place them:
```sh
mount -uw /fs/sda0
mkdir -p /fs/sda0/opt/hmi/ID5/data/ro/<dest>
cp /tmp/stage/* /fs/sda0/opt/hmi/ID5/data/ro/<dest>/
chmod 755 /fs/sda0/opt/hmi/ID5/data/ro/<dest>/lib<Name>.so   # a loadable .so needs exec bits
```

To pull a file back (e.g. captured output), the HU `bsdtar` can base32/64-encode to stdout, or just
`cat` it over the session:
```sh
ssh -o HostKeyAlgorithms=+ssh-rsa root@<dev-ip> 'cat /tmp/out.txt' > out.txt
```

## Step 3 — the integrity rule (LMPC): add or rename-over, never edit in place

`LinkManagerHU` periodically hashes every **manifest-listed** repository file and raises a DTC after
repeated mismatches (see the [LMPC note in architecture.md](architecture.md)). So:

- **New files** (a `Plugins/<Name>/` folder, a `vae/vehicles/<id>/` tree, a binary in `/tmp`) are in
  no manifest and are **never checked** — this is the safe default.
- A **stock file that must change** is replaced by a **rename-over**, never an in-place edit: build
  the new file as a *new* file (new inode) and `mv` it over the path, keeping the original beside it
  (e.g. `resources.pbr.orig`) still hard-linked to the untouched signed inode. Editing the path in
  place mutates the shared signed inode and trips LMPC.

```sh
mv  "$idx.new"  "$idx.orig"   # WRONG shape — don't clobber; keep the original
# right shape:
cp  "$idx"      "$idx.orig"    # keep the signed inode aside (hard link preserved)
mv  "$idx.new"  "$idx"         # new inode over the path; signed copy untouched
```

## Step 4 — apply (restart the HMI)

Most installs are read at HMI start, so restart the application layer. Run it **detached** (`on -d`)
so your SSH shell returns while the layer bounces:

```sh
LD_LIBRARY_PATH=/opt/car/lib on -d /opt/car/bin/OnOffDSICommander appreset
```

`appreset` restarts the HMI without a cold boot (a full `reboot`/power-cycle also works and is the
fallback). It **wipes `/tmp`**, so to detect that the restart actually happened, drop a marker in
`/tmp` *before* firing and poll for its disappearance — don't detect by PID (QNX's deterministic
start order makes PID checks unreliable).

## Step 5 — verify, then restore read-only

- **Restore the mount:** `mount -ur /fs/sda0`.
- **Integrity intact:** if you did a rename-over, confirm the signed copy is still byte-identical
  (`diff "$idx.orig" "$repo_copy"`), and that the live path now points at your new inode (`ls -l`
  link counts: your new file has a link count of 1; the preserved original still shares the signed
  inode's count).
- **Feature present:** the plugin's menu entry renders / the custom car shows / your binary runs.
  There's no hash tool on the HU, so verify by **behavior and `ls -l`**, not checksums.

## Undo

Reverse it, equally LMPC-safely, under the same remount:

- **Added files/folders** → delete them.
- **Rename-over** → `mv "$idx.orig" "$idx"` (puts the original signed inode back).
- A loaded plugin `.so` the running HMI may still have open: **don't delete it** — rename its folder
  out of `Plugins/` and delete it only after the next HMI restart has released it.
- Restore the mount state (`mount -ur /fs/sda0`) and restart the HMI if the change needs it.

---

### Where each capability's specifics live

This doc is the shared mechanism. For *what* to place and *where*:

- **Plugins** — [capabilities/plugins/docs/08-building-and-deploying.md](../capabilities/plugins/docs/08-building-and-deploying.md) (the three files, `Plugins/<Name>/`, the discovery ladder).
- **Custom cars** — [capabilities/vehicle_models/02-packaging.md](../capabilities/vehicle_models/02-packaging.md) (the `.nbtcar`, the registry override, the index rename-over).
- **Your own QNX binary** — [capabilities/qnx_dev/03-on-car.md](../capabilities/qnx_dev/03-on-car.md) (the ephemeral `/tmp` exec case — no remount needed).
