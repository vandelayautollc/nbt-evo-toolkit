# 03 · The write flow (durable coding over UDS)

How a **signed** NCD becomes a durable change on the car. This is the dangerous part: do it with a
backup in hand, the car parked, and battery voltage healthy. The implementation is
`tools/write_coding.py`; it defaults to a **dry run** (prints the frames it would send) and only
writes when you pass `--commit` and the gate passes.

## Preconditions

1. **Ownership gate** — `write_coding.py` calls `nbtevo.consent.require_owner()` and then reads the
   connected car's VIN (`22 F1 90`) and refuses unless it equals `NBTEVO_OWN_VIN`. This is what
   stops a write to the wrong car.
2. **A backup** — take one with `read_coding.py` first. Always.
3. **A valid signature** — the NCD's signature datagroup (`0x3010`) must verify against its coding
   bytes. `write_coding.py` re-checks this locally before sending anything; a bad signature aborts.
4. **The write-unlock key** — the coding write needs SecurityAccess, which uses the module's **L3
   SecurityAccess key** (a *different* key from the NCD signing key, but also tied to the BTLD).
   Recover it with the shared tool: `python -m nbtevo.keys --btld <id> --kind l3 -o l3_key.json`
   (the same key unlocks flashing — see [docs/keys.md](../../docs/keys.md)). Without it configured,
   the tool runs the whole flow *except* the unlock and the write, so you can still rehearse it.

## The choreography

```
10 03                         enter extendedDiagnosticSession
10 41                         enter codingSession (sub-id 0x41)
27 01            → seed        SecurityAccess requestSeed  (coding unlock, level 01)
27 02 <key>      → 67 02       SecurityAccess sendKey      (shared L3 handshake — see below, nbtevo.l3)
                              ── writes, per datagroup, signature LAST ──
2E 30 00 <bytes>              write datagroup 0x3000
2E 30 01 <bytes>              write datagroup 0x3001
   …                          … every user datagroup that changed …
2E 30 0F <bytes>              write CAF_ID datagroup (if present/changed)
2E 30 10 00 00 00 20 <sig>    write the SIGNATURE datagroup (0x3010) LAST
31 01 0F 01       → checkSignCorrect   CheckCodingSignature routine (RID 0x0F01)
2E 37 FE <cps>                write the Coding Production Stamp (CPS, DID 0x37FE)
22 37 FE          → read-back  confirm the CPS took
11 01                         hard ECUReset — the HU reboots and re-verifies the new coding
```

Notes that matter:

- **Signature datagroup is written last.** The ECU's check routine runs against the full set; write
  the data first, then `0x3010`.
- **`31 01 0F 01` is the gate.** If it does not return `checkSignCorrect`, the operation is aborted
  *before* the CPS is written — exactly as PSdZ does (`WRONG_CODING_SIG`). A failure here almost
  always means the signature doesn't match the bytes (re-sign) or you edited a datagroup the
  signature doesn't cover.
- **CPS last, then reset.** The CPS (`0x37FE`) records a valid coding completed; it's written and
  read back, then the HU is hard-reset (`11 01`). On the NBT EVO the HU **reboots instantly** and
  comes back on its own IP in a few seconds; the write is durable across that reboot because it was
  signed and finalized.
- **SecurityAccess is level 01 (`27 01`/`27 02`), not the flash level.** The seed→key response is the
  **shared L3 construction** — sign `MD5([UserID][Controller][seed])` with your L3 key, raw RSA e=3
  little-endian, encoded `00000020` + per-word-swapped 128-byte sig — the *same* handshake flashing
  uses at level 11 ([docs/keys.md](../../docs/keys.md)). `write_coding.py` computes it via
  [`nbtevo.l3`](../../nbtevo/l3.py) from your recovered `l3_key.json`; it is **not** a plain "sign the
  seed".

## Verifying the write

Don't trust "no error" — read it back:

1. After the reset settles, `read_coding.py` again and diff against your intended NCD.
2. The changed parameter should read the new value, and `0x3010` should match.
3. If a feature didn't change behavior, re-check your coordinate/value in
   [04-definitions.md](04-definitions.md) — a correct, signed write of the *wrong* bit is still a
   correct signed write.
4. A clean read-back proves the bytes, not the behavior. **Watch the HMI come back up** and exercise
   the feature. An option can be correct for this CAFD and still not work on this unit's hardware
   or build, or it can hang the UI. The observe/revert criteria and the bisect procedure are in
   [05-apply-observe-revert.md](05-apply-observe-revert.md).

## Reverting

Keep your pre-change backup. To revert, write the backup NCD the same way (it is already correctly
signed, because it's what the car gave you). The app's own editor models this as a two-way slide:
*keep* the new coding or *revert* to the pre-write backup — both are just signed NCD writes.

**Stage the revert before you write the change**: dry-run the backup write once so the revert is a
command you have already checked. If the HMI freezes or doesn't load after a write, the revert still
goes over UDS. The coding write is served by the diag app, not the HMI, so a frozen UI doesn't by
itself block it. Revert first, then investigate. See
[05-apply-observe-revert.md](05-apply-observe-revert.md).

## Honest status

- The **signing** half is proven and self-testable (`validate/selftest.py`): the signer reproduces
  the car's own NCD signature byte-for-byte.
- The **write choreography** above is faithfully transcribed from the proven flow, and
  `write_coding.py` implements it — including the SecurityAccess step, which now computes the key via
  [`nbtevo.l3`](../../nbtevo/l3.py) from the `l3_key.json` you recover (`--l3-key`). It still ships
  **dry-run by default**; `--commit` additionally hard-checks the connected VIN against the one you
  own. Treat the first real `--commit` as a careful, backed-up, parked-car operation, and read back
  to confirm — the on-car `67 02` is the proof your key is right.
