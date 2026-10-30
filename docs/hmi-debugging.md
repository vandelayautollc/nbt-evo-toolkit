# Logs & HMI debugging — hung, crashed, or rejected?

You've just changed something (usually coding), and the HMI isn't behaving: a black screen, a
frozen menu, or a feature that never shows up. This page covers how to tell **which kind** of
failure it is and where the HU writes down what went wrong. It's the observation half of
[coding/05](../capabilities/coding/05-apply-observe-revert.md): that doc says *when* to revert,
this one helps you work out *why*.

Most of this needs the dev shell, i.e. SSH on the `dwc0` IP of an OPT_DEBUG unit
([staging-files-over-ssh.md](staging-files-over-ssh.md)). Without it you still have UDS (DTCs,
coding read-back) and the operator's eyes.

> **Evidence legend.** **on-car**: observed on the reference unit. **static**: read from the
> firmware carve (boot scripts, format strings), not seen live. **inferred**: a reasoned
> conclusion that hasn't been tested. Paths and process names are from the reference build
> ([versioning.md](versioning.md)); re-check them on yours.

## Snapshot first, because some of it won't survive the revert

The system log is a RAM ring buffer, and the revert ends in a reset, so **capture before you
revert** if the shell answers. A capture takes seconds. Use one SSH session, since `inetd`
rate-limits logins:

```sh
ssh -o HostKeyAlgorithms=+ssh-rsa root@<dev-ip> '
echo "== HmiMain3D";  pidin -p HmiMain3D
echo "== dumps";      ls -l /fs/sda1/dump /fs/sda1/dump/jacinto /var/dump
echo "== sloginfo";   sloginfo' > hu-snapshot-$(date +%Y%m%d-%H%M%S).txt
```

Take one of these as part of your **baseline**, before the first write. Most of what follows is a
comparison against it: a different pid, a new core file, new log lines.

The HU has no `head`, `base64` or `strings` (on-car), so pull logs back whole and search them on
your workstation. Don't rely on the HU's text tools.

## Triage: which failure is it?

| What you see | Likely state | Next |
|---|---|---|
| UDS (`22 F1 90`) doesn't answer | Still booting, or a fault deeper than the HMI | Wait out your baseline boot time, then try an ignition cycle ([coding/05 Step 3](../capabilities/coding/05-apply-observe-revert.md#step-3--apply-observe-and-revert-on-the-criteria-you-set-in-advance)) |
| UDS answers, SSH doesn't yet | Dev services still starting | Wait; screenshots also only work after a full boot ([toolchain.md](toolchain.md#screenshotting-the-hmi)) |
| `HmiMain3D` missing from `pidin` | Crashed and not (yet) recovered | Wait ~30 s, snapshot, look for a new core file, then revert |
| `HmiMain3D` **pid changes** between snapshots, screen blanks every ~30 s | **Crash loop** | Snapshot, then revert. With coding, every restart re-reads the same coding, so it'll keep crashing until you revert *(inferred)* |
| pid stable, two screenshots identical across a controller input | **Hung** UI | `pidin -p HmiMain3D` for thread states, snapshot, then revert |
| pid stable, UI responsive, but the feature is missing, a menu is empty, or a screen won't open | **Rejected or inert**: the consumer ignored the value, a gate is missing, or hardware is absent | Search `sloginfo` for the consumer's complaint (below), then go to the firmware trace in [coding/05 Step 0](../capabilities/coding/05-apply-observe-revert.md#step-0--prefer-evidence-from-the-firmware) |

**How a crash recovers (on-car).**
- After a crash, `HmiMain3D` comes back with a **new pid** in about **25–30 s**. The same pid means
  it hasn't crashed since your last look.
- The respawn doesn't come from `starter`: its config has `OnTerminate=IGNORE_ALL` for
  `HmiMain3D` (static). The recovery is the system watchdog's; most likely that's `CSI_NBT`, the
  recovery manager that `starter` restarts up to 99 times (static).
- Don't `slay HmiMain3D` over and over to "test" this. Repeated slays have been observed to
  destabilise the HMI.

## Where the logs are

| Sink | What lands there | How to read it | Evidence |
|---|---|---|---|
| **System log** (`slogger`) | The HMI logs through `libhmilog.so` (`/opt/hmi/lib`); car apps log through Harman's `HBSyslog`/`slog*` calls | `sloginfo` (pull it whole and search locally) | on-car (`sloginfo` used); static (lib paths) |
| ↳ size and lifetime | RAM ring: `slogger -m -u 110 -s 1024k` on the HU node's boot script, so about 1 MB and overwritten as it fills | Capture soon after the event, and before any reset | static (boot script); lost on reboot is *inferred* |
| **Core dumps** (`dumper`) | One core file per crashed process: `/fs/sda1/dump/<proc>.core` on the OMAP, and `/fs/sda1/dump/jacinto/` for Jacinto processes (written across qnet) | `ls -l` against your baseline; a new or newer file means that process crashed | on-car (a real `HmiMain3D.core` was pulled from there); static (Jacinto dumper line) |
| ↳ what's in a core | The `HmiMain3D` core seen had ~1,000 segments, mostly with no file contents | Use it for *that* and *when* it crashed and its segment map, not for a full post-mortem | on-car |
| **Assert backtraces** | Harman processes run with `HB_ASSERTION_BACKTRACE_DIR=/var/dump` (`MAX=50`) and abort on assert or fatal error | `ls -l /var/dump`; pull new files | static (process environment); persistence across reboot not established |

### Lines worth searching for

- **Camera / video coding**: `EarlyVideoApp` / `EarlyICam2App` write `<EarlyVideo>`-prefixed lines
  that **print the coding values they read** and complain about bad ones (static: format strings,
  not captured live):
  - `CPEarlyVideoCoding::isVideoWatchdogEnabled: VIDEO_WATCHDOG_REARVIEW = 0x%02x`, and similar
    lines for each value read;
  - `castCameraSystem: camera system is out of range - check the version of binary earlysyset`,
    which means a coded value is outside what this build handles;
  - `onCameraRequest: Camera (InstID = 0x%02x) is disabled by coding, %s request is ignored`.
- **Start-up variant**: `StarterPlugin: Final Variant Vector: 0x%04X`. This is the runtime variant
  word computed at boot, which decides which optional processes start (static).
- **Noise you can ignore**: `HmiMain3D` logs `OTF init failed!` whenever BMW's OTF trace agent
  isn't running. On a stock unit it normally isn't, and the message is harmless (on-car).
- **Your own feature**: search for the token name, the consumer binary's name (see the
  [playbook §5 index](investigation-playbook.md#where-codingresource-values-are-consumed-the-5-index)),
  or a plugin name. Diff the log against your baseline snapshot to see what's new.

## HMI process facts

- **Binary**: `/opt/hmi/bin/zipped/HmiMain3D`, launched by `starter` (partition `interaction`,
  priority 10). The full argv and env are visible in `pidin -p HmiMain3D arg` / `env` if you need
  to compare against stock (on-car argv).
- **Threads**: `pidin -p HmiMain3D` lists them. A healthy HMI has a per-frame render thread
  constantly RUNNING (about 50–60 Hz); the others sit blocked (on-car). If nothing is ever RUNNING
  across several looks, and the screen is frozen, the HMI is hung.
- **Open files**: `pidin -p HmiMain3D fds` (on-car). This is useful when a screen fails to load,
  to see whether it opened the resource you expect.
- **Memory map**: `pidin -p HmiMain3D mem`.

## DTCs over UDS

Reading DTCs is a standard UDS read (`19 02 FF`, reportDTCByStatusMask), needs no SecurityAccess,
and works without the dev shell. The toolkit's `nbtevo` client can send it as is:

```python
from nbtevo.hsfz import HsfzClient, TGT_HU
from nbtevo.uds import Uds

with HsfzClient("<diag-ip>") as c:
    r = Uds(c, TGT_HU).raw(bytes.fromhex("1902FF"))     # 59 02 <availMask> then [DTC(3) status(1)]*
    assert r[:2] == b"\x59\x02", f"negative response: {r.hex()}"
    for i in range(3, len(r) - 3, 4):
        print(r[i:i + 3].hex().upper(), f"status=0x{r[i + 3]:02X}")
```

Diff the result against your baseline. Two notes:
- The HU raises an integrity DTC when a **manifest-listed file** is changed in place (LMPC,
  [architecture.md](architecture.md)). That signals a *file* change, not a coding one.
- The specific DTC numbers that mean "HMI fault" aren't mapped in this toolkit. Treat any new DTC
  that appears with your change as a lead, not a diagnosis.

## Deeper tools (when the logs don't say)

- **Kernel event trace.** The kernel is the instrumented `procnto-smp-instr`, so `tracelogger -f
  /fs/ram5/t.kev -s2` records kernel events (file opens, messages) while you reproduce the
  problem. `traceprinter` is **not** on the HU: copy the `.kev` off and decode it offline with the
  QNX SDP System Analysis tools (on-car: `tracelogger` present, `traceprinter` absent). This is the
  closest thing to `strace`; there is no `strace` or `ltrace` on QNX.
- **Live debugger.** `qconn` listens on 8000 on OPT_DEBUG units, so host-side `ntoarm-gdb` (QNX SDP
  6.5.0) can attach to a running process (on-car: `qconn` running; a gdb session on `HmiMain3D`
  isn't recorded). The toolchain is in [qnx_dev](../capabilities/qnx_dev/). There is no compiler
  on the HU.
- **BMW's OTF trace agent** (`/opt/hmi/otf/BMWOTFagent`, gated by the `TRACE` coding parameter
  through the runtime variant word) **isn't a usable log source yet**. It has been started by hand,
  but it's a silent server speaking an undecoded protocol. `HmiMain3D` only connects to it if it's
  already running when the HMI starts. Don't change coding just to try it.

## Honest status

- **On-car**:
  - the pid-change crash signature and its ~25–30 s recovery;
  - the thread and fd views (`pidin -p HmiMain3D`, `… fds`);
  - `sloginfo` and `tracelogger` present, `traceprinter` absent;
  - a core file pulled from `/fs/sda1/dump`;
  - the missing HU text tools;
  - the `OTF init failed!` line.
- **Static**:
  - the slogger buffer size;
  - the dumper and backtrace directories;
  - the `<EarlyVideo>` and `StarterPlugin` message formats;
  - the `starter` restart policy.

  These come from the carve and are worth confirming on your unit.
- **Inferred**:
  - the system log doesn't survive a reboot (memory-backed ring), so snapshot first anyway;
  - a crash-causing coding value causes a crash loop;
  - the HMI watchdog is `CSI_NBT`.
- **Untested as written**: the snapshot one-liner and the DTC snippet. Each command in them has
  been used on its own (or is a standard UDS read), but not in this combined form.
