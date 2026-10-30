# FSC — feature codes & the blobB trust anchor

Read and understand the head unit's **FSC** (Freischaltcode / SWT) feature entitlements, and — on
your own unit — install your own trust anchor so you can mint and apply FSCs the unit accepts.

> ⚠️ **Read this first.** FSC is BMW's *licensing* mechanism. Enabling a feature BMW has not licensed
> to you may breach your agreement with BMW **even on your own car** — that is between you and BMW,
> and this project takes no position on it beyond: do it only on a vehicle you own, bound to your own
> VIN, and never to someone else's car. The toolkit ships **no BMW key** and cannot forge one. See
> [LEGAL.md](../../LEGAL.md) (the project's no-harm disclaimer).

## What's actually possible here (and why)

Every "long" FSC is checked against **one** RSA modulus — **blobB** — compiled into `NBTCarHU`.
There is no per-feature key and no BMW certificate lookup for it. You do **not** hold BMW's FSC
private key. So:

- You **cannot** forge a BMW-signed FSC offline. (Stock blobB stays BMW's; you have no `d` for it.)
- You **can**, on a unit you own, **replace blobB with your own modulus** (a 128-byte, length-
  preserving patch) and then **mint FSCs with your own key** — the unit accepts them because the
  installed trust anchor is now yours. Coding is unaffected (it's keyed by a *different*, disjoint
  key). This is a trust-anchor swap on your own hardware, not a forgery of BMW's.

That's the honest shape: read/inspect anytime; to *enable* a feature, you install your own trust and
issue your own entitlement, on your own car.

## Read this section in order

1. **[01-concepts.md](01-concepts.md)** — what FSC/SWT is: the engine, the `Swt` service, the FSC
   token format, SWID/application-number, VIN-binding, and the exact verify chain.
2. **[02-blobB-and-minting.md](02-blobB-and-minting.md)** — the trust-anchor model: install your own
   blobB and mint FSCs under it (the tools), and why coding survives.
3. **[03-apply-and-read.md](03-apply-and-read.md)** — read the installed FSCs (and detect a swapped
   trust), and apply an FSC over the diagnostic bus.
4. **[catalog.md](catalog.md)** — application-number → feature name (CarPlay, nav, speech, …).

## Tools

| Script | Does | Touches car | Status |
|---|---|---|---|
| `tools/fsc.py keygen` | generate your own e=3 trust anchor + the 128-byte blobB replacement | no (local) | ✅ |
| `tools/fsc.py mint` | mint an FSC signed by your own key | no (local) | ✅ |
| `tools/fsc.py verify` | check an FSC would be accepted under a given modulus | no (local) | ✅ |
| `tools/fsc.py parse` | decode an FSC's body fields | no (local) | ✅ |
| `tools/fsc.py fingerprint` | stable short id of an anchor (key or blobB) — label known anchors | no (local) | ✅ |
| `tools/fsc.py whosigned` | **identify whose anchor signed FSCs read off a unit** (before you overwrite blobB); recovers an unknown modulus via e=3 | no (local) | ✅ |
| `validate/check_fsc.py` | prove the mint/verify + modulus-recovery model end to end | no (local) | ✅ |
| blobB patch | install your modulus into `NBTCarHU` | **flash** | 🔜 via `flash_and_patching` |
| storeFSC apply | write an FSC to the unit over the `Swt` service | **writes** | 🔜 documented runbook |

## The happy path

```bash
pip install -e .
python -m capabilities.fsc.validate.check_fsc          # prove the model, no car

# your own trust anchor (keep the key private — it is YOUR root of trust)
python capabilities/fsc/tools/fsc.py keygen -o owner_key.json --blobb owner_blobB.bin

# mint an entitlement under your key (see catalog.md for application numbers)
python capabilities/fsc/tools/fsc.py mint --key owner_key.json --appno 0x0143 -o carplay.fsc
python capabilities/fsc/tools/fsc.py verify --fsc carplay.fsc --key owner_key.json
```

Then install `owner_blobB.bin` into `NBTCarHU` (02 + the flash capability) and apply `carplay.fsc`
(03). The mint/verify/read tooling is here and tested; the two car-touching steps are documented
runbooks pending their capability ports.

> An FSC is only *half* of most features. For CarPlay, the `0x0143` FSC must be paired with a
> specific set of coding bits — see the worked example [examples/carplay.md](../../examples/carplay.md).
