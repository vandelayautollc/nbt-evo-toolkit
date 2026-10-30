# 01 · FSC / SWT concepts

The vocabulary and the mechanism. All of it is from first-hand RE of the head unit's own binaries;
none of it is secret, and the toolkit ships no BMW key.

## What FSC is

An **FSC** (FreiSchaltCode) / **SWT** (SoftWare-Token Freischaltung) is a per-feature entitlement
the head unit checks before enabling an optional function — navigation, maps, speech/TTS,
CarPlay, BMW Apps, satellite radio, etc. It is a signed binary token, **VIN-bindable**, keyed by a
feature id. This axis is **orthogonal to coding**: coding (CAFD) toggles configuration; FSC
authorizes licensed features. Changing one does not change the other.

## The engine and the service

One statically-linked service, **`opt/car/bin/NBTCarHU`**, is the whole SWT/FSC engine (it carries
its own OpenSSL CMS/PKCS7/RSA/X509 and BMW's SGIff SWT library). It registers the **`Swt`** family
on the DSI service broker and exposes the FSC verbs:

```
requestStoreFSC · CheckFSC · DisableFSC · GetFSC · CheckFscAccepted ·
CheckFscShort · SetFscShort · GetSeed · StatusApplication · ActivationNessesarry
```

Feature consumers (`Connectivity`, `Online`, the `apnnav*` navigation engines) don't decide
entitlement themselves — they ask the `Swt` service and gate their own behavior on the answer
("activation state = %d").

## The FSC token

A long FSC is a **188-byte binary** = a **60-byte body** + a **128-byte RSA signature**. The
user-facing form is the body+sig **base32-encoded** (`getBinaryFSC` decodes base32 on the way in).
The body layout (`tools/fsc.py build_body`, byte-exact to the EVO form):

| offset | field |
|---|---|
| 0–1 | version `01 01` |
| 2–3 | **application number** (AppNo, u16 BE) — the feature id (see [catalog.md](catalog.md)) |
| 4–5 | upgrade index (u16 BE) |
| 6–13 | supplier id (8 ASCII) |
| 15–22 | requester type (8 ASCII) |
| 23–24 | counter |
| 26–32 | FSCS id (7 ASCII) |
| 33 | VIN-type (`01` ⇒ a 9-byte VIN follows) |
| 34–42 | **VIN** (9 bytes; all-zero ⇒ VIN-generic, the unit skips the per-VIN compare) |
| 45–56 | creation date (GeneralizedTime `YYYYMMDDhhmm`) |

Feature identity is a **SWID** (4-byte) + the **16-bit application number**; the AppNo is what the
body carries and what the catalog names.

## The verify chain (what the device actually checks)

Reverse-engineered byte-for-byte from `NBTCarHU` (`doCheckFSC` → `FUN_0030544c` → `FUN_00305dc4`
→ `FUN_00305c50`). It is deliberately simple:

```
signed region = fsc[: len(fsc) - 128]          # the whole body before the 128-byte signature
digest        = MD5(signed region)             # standard MD5, no prefix/suffix
accept iff:  sig^e mod N  unpads as PKCS#1 v1.5 (00 01 | FF… | 00 | MD5-DigestInfo | digest)
             with  e = 3  and  N = blobB
```

- **blobB** is a single 128-byte RSA modulus (little-endian in the file, e=3) at `NBTCarHU` file
  offset **`0x35A300`**. **There is no per-AppNo key and no certificate lookup** for the long-FSC
  path — one modulus verifies every long FSC.
- The envelope is **zero-slack** PKCS#1 v1.5 over an MD5 DigestInfo — exactly 128 bytes, nothing
  free. `tools/fsc.py verify_fsc` reproduces this check.
- It is **deterministic** (raw RSA e=3), so there is one valid signature per body under a given key.

(There is also a certificate-based transport for FSC delivery — FAFP `.fap`, CMS EnvelopedData
AES-256 to a device recipient cert, validated against the **KISS persistence** ROOT→SIGS→FSCS cert
chain. That chain is runtime state, not compiled in. The long-FSC `blobB` path above is the one the
mint/verify tooling models.)

## VIN-binding

An FSC either carries a real 9-byte VIN (unit-locked: only that VIN accepts it) or an all-zero VIN
(VIN-generic). Keep it **your own VIN** for a unit-locked entitlement; a VIN-generic token is still
only useful on a unit whose blobB you control. Minting a token for *someone else's* VIN is out of
scope and pointless — it would also require their unit's blobB to be yours. See [LEGAL.md](../../LEGAL.md).

## Why you can't just forge one, and what you can do

The genuine `blobB` is BMW's public modulus; its private key is in no asset we hold, so you can't
produce a signature stock blobB accepts. The owner-authorized lever is to **replace blobB with your
own modulus** on a unit you own and sign with your own key — covered next in
[02-blobB-and-minting.md](02-blobB-and-minting.md).
