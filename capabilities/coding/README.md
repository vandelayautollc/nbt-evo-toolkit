# Coding

Change the head unit's **coding** — the per-vehicle configuration that toggles features, regional
behavior, and UI options — in a way that **survives a reboot**. This is the fully worked reference
capability; the other folders follow its shape.

> ⚠️ Writing coding can disable features or, if you corrupt the dataset, leave the HU in a degraded
> state. **Read and back up first** (`tools/read_coding.py`), validate your change offline
> (`validate/selftest.py`) *before* sending it, and confirm ownership
> ([LEGAL.md](../../LEGAL.md)). Reads are safe; writes are gated.
>
> ⚠️ **Not every option works on every unit.** A parameter in the definitions map, correctly signed
> and read back, can still do nothing on your car, or freeze the HMI or stop a screen from loading.
> Whether it works depends on the hardware fitted, the software/CAFD build, the other bits, and the
> FSCs. Verify a change from the consumer in firmware where you can. Otherwise test it by applying
> and reverting. Batching changes is fine, but stage the revert first and record exactly what every
> write changed. Revert as soon as the UI doesn't come up, and be ready to bisect if the user hits
> a problem later. See **[05-apply-observe-revert.md](05-apply-observe-revert.md)**.

## The one thing to understand first

The NBT EVO re-verifies a cryptographic **signature** over its coding **at every boot**. A raw byte
edit you write without re-signing passes momentarily and then **reverts on the next boot**. Durable
coding therefore means: edit the bytes **and** recompute the signature with the right key, then
write both through the authenticated UDS coding flow. Miss the signature and nothing sticks.

That key is selected by the head unit's **bootloader (BTLD) id**. Identifying the BTLD and looking
up its key/scheme is the hinge of this whole capability — [02-signing-model.md](02-signing-model.md).

## Read this section in order

1. **[01-concepts.md](01-concepts.md)** — how coding is stored: datagroups, the CAFD, the NCD
   container, the CPS stamp. The vocabulary everything else uses.
2. **[02-signing-model.md](02-signing-model.md)** — the per-BTLD signing model: the legacy
   RSA `BMWSigVerify` scheme (what the NBT EVO uses), the SHA-256 variant, and "secure coding"
   (ECDSA, backend-only) — and how to tell which one you're facing. **The key doc.**
3. **[03-write-flow.md](03-write-flow.md)** — the exact UDS choreography to write coding durably,
   with the safety gates.
4. **[04-definitions.md](04-definitions.md)** — how to turn a raw coding coordinate into a
   human-meaningful parameter. The full map of all **1481** parameters ships in
   **[`definitions/`](definitions/)** (`cafd_00001ef6_definitions.md` / `.json`).
5. **[05-apply-observe-revert.md](05-apply-observe-revert.md)** — whether a change will work on
   *this* unit. Verify it from firmware, stage the revert, apply (batched is fine) with every delta
   logged, and check that the HMI comes up. Revert if it doesn't, and debug or bisect when the user
   reports a problem. **Read before your first real write.**

## Tools

All read the shared `nbtevo` package (`pip install -e .` from the repo root).

| Script | Does | Touches car | Gated |
|---|---|---|---|
| `tools/identify_btld.py` | Read SVK → print BTLD, CAFD, VIN; look up the coding scheme | reads | no |
| `tools/read_coding.py` | Dump the live coding datagroups to an NCD backup | reads | no |
| `tools/recover_key.py` | Recover **your** signing key from **your** PSdZData | no (local) | **yes** |
| `tools/sign_ncd.py` | Apply edits to an NCD and (re)compute the signature | no (local) | no |
| `tools/write_coding.py` | Write a signed NCD to the car (full choreography) | **writes** | **yes** |
| `validate/selftest.py` | Prove the signer reproduces your car's own signature byte-for-byte | no (local) | no |

## The happy path

```bash
pip install -e .
export NBTEVO_OWN_VIN=YOURVIN
export NBTEVO_PSDZDATA=/path/to/your/psdzdata

# 1. Orient.
python -m capabilities.coding.tools.identify_btld --host 169.254.104.13

# 2. Back up the live coding (do this every time).
python -m capabilities.coding.tools.read_coding --host 169.254.104.13 -o backup.ncd

# 3. Recover your own signing key (one time), then PROVE the signer works on your own data.
python -m capabilities.coding.tools.recover_key --btld 00001FFD -o ~/.nbtevo/key.json
python -m capabilities.coding.validate.selftest --ncd backup.ncd --key ~/.nbtevo/key.json

# 4. Edit + re-sign offline, verifying the signature locally before anything goes to the car.
python -m capabilities.coding.tools.sign_ncd backup.ncd modified.ncd \
    --key ~/.nbtevo/key.json --set 0x3001,0x62,2,0x78,3

# 5. Stage the revert (rehearse writing the untouched backup), then write the change
#    (gated: confirms the connected VIN == the VIN you own).
python -m capabilities.coding.tools.write_coding --host 169.254.104.13 \
    --ncd backup.ncd --key ~/.nbtevo/key.json
python -m capabilities.coding.tools.write_coding --host 169.254.104.13 \
    --ncd modified.ncd --key ~/.nbtevo/key.json

# 6. Confirm it on THIS unit: read back and diff, then check the HMI comes up and the feature works.
#    If the UI freezes, doesn't load, or reboot-loops, revert first: re-run step 5's write with
#    --ncd backup.ncd. See 05-apply-observe-revert.md.
python -m capabilities.coding.tools.read_coding --host 169.254.104.13 -o after.ncd
```

## A worked cross-capability example

Coding is often only half of a feature — it may also need an FSC entitlement. For a complete,
ordered recipe (the firmware-checked `CARPLAY_SWT` bit *plus* the `0x0143` FSC), see
[examples/carplay.md](../../examples/carplay.md).
