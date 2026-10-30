# 02 · The coding signing model

This is the doc that makes durable coding possible. It explains **which key signs your coding, how
the signature is computed, and how to tell whether you can produce one offline at all** — because
for the newest modules you cannot, and knowing that up front saves you from chasing a dead end.

## The hinge: the bootloader selects the key

Every coded module verifies its coding against a public key **baked into its firmware**. The
matching private key is distributed, per **bootloader (BTLD) id**, inside PSdZData's
`security/sec_ncdkeys.xml`. So the identity that decides everything is the **BTLD id you read from
the car's SVK** — not the model, not the CAFD. Read it first (`tools/identify_btld.py`), then look
it up.

```
car ──22 F1 01──▶ SVK ──BTLD id──▶ sec_ncdkeys.xml entry ──▶ scheme + key ──▶ can I sign offline?
```

For the NBT EVO the BTLD is **`00001FFD`**, and its entry is a filled RSA key — so yes, offline
signing works, and `recover_key.py` recovers it from your own PSdZData.

## Three classes of coding key

`sec_ncdkeys.xml` has one `<NCodSigKey>` per bootloader, carrying a `keyData` body plus attributes
`digestAlg`, `signatureScheme`, and `testKey`. Three cases, and only the first two are useful on a
customer car:

| Class | What `sec_ncdkeys.xml` shows | Can an owner sign offline? |
|---|---|---|
| **Legacy RSA** (`BMWSigVerify`) | filled key body, RSA, digest MD5 or SHA-256, `testKey=false` | **Yes.** Recover the key; sign locally. *(NBT EVO is here.)* |
| **Offline ECDSA** | filled ECDSA key body, `testKey=false` (rare — a handful of modules) | Yes, with an ECDSA signer. |
| **Secure coding** | **empty** key body, ECDSA, `testKey=false` | **No.** The private key is not shipped; only BMW's online backend (HSM) can sign. Backup/read only. |
| *(trap)* **Test keys** | filled ECDSA but `testKey=true` | No — bench/dev keys, not valid on a customer ECU. |

**The discriminator is simply whether the key body is non-empty** (`BMWSigVerify.isValidKey()` in
PSdZ is "the body is not empty"). An empty body *is* "secure coding". As a module line moves to a
newer bootloader, its coding tends to migrate from legacy-RSA (offline) to secure (backend-only).

This matters even though the NBT EVO is firmly in the offline camp: if you point this toolkit at a
*different*, newer module and signing "mysteriously can't produce a key", check the class before
assuming a bug. `recover_key.py` reports the class it found.

## The legacy `BMWSigVerify` primitive (what the NBT EVO uses)

This is the scheme the NBT EVO (and the related clusters) verify. It is a **raw RSA, exponent
e = 3, no padding** signature over a digest of the coding pages. The only per-module variation is
the **digest** and **which datagroups** are covered.

```
content = concat( page(dg) for dg in CONTENT_DGS )     # raw datagroup pages, ascending, no separators
digest  = H(content)                                   # H = MD5 or SHA-256 per the key's digestAlg
m       = int.from_bytes(digest, "little")             # digest as a little-endian integer
s       = pow(m, d, N)                                  # raw RSA-1024, e=3, NO PKCS#1 padding
sig     = wordswap( s.to_bytes(128, "little") )         # byte-reverse each 32-bit word, word order kept
SIG_DG  = be_u32(len(N)//4 words) || sig                # e.g. 00 00 00 20 || 128-byte sig  (132 bytes)
```

The ECU verifies by the inverse (this is exactly what its CheckCodingSignature routine computes):

```
D = pow( int.from_bytes(wordswap(sig), "little"), 3, N )
accept  iff  D.to_bytes(len(digest), "little") == digest   and   D.bit_length() <= 8*len(digest)
```

- **`wordswap`** reverses the bytes within each 4-byte word, keeping word order. (A quirk of BMW's
  big-number storage; the signer and verifier both apply it.)
- **No PKCS#1 / DigestInfo / OID / 0xFF padding.** The bare little-endian hash sits in the low
  bytes, high bytes zero. The ECU gates the digest by the significant-word count
  (`4 words ⇒ MD5`, `5 ⇒ SHA-1`, `8 ⇒ SHA-256`).
- The scheme is **deterministic** (raw RSA e=3): exactly one valid signature exists per content, so
  reproducing it *is* producing the signature the ECU accepts. That's why the self-test
  (`validate/selftest.py`) can prove correctness byte-for-byte against your car's own NCD.

### The two instances this toolkit knows

| Module | BTLD | CAFD | digest | content datagroups | sig datagroup |
|---|---|---|---|---|---|
| **NBT EVO head unit** | `00001FFD` | `00001EF6` | **MD5** | `0x3000`–`0x300F` | **`0x3010`** |
| R1250 cluster (sibling, for contrast) | `00004F8F` | `00004130` | **SHA-256** | `0x3000`–`0x3009`, `0x37EF`, `0x37F0` | **`0x37F1`** |

Same primitive, different digest and datagroup set — which is why `sign_ncd.py` is parameterized by
a **scheme** (digest + content datagroups + signature datagroup), defaulting to the NBT EVO layout.

## Recovering the key (yours, from your data)

The private key is recovered from **your** PSdZData, locally, and never leaves your machine. The
method (`recover_key.py`, and PSdZ does the equivalent internally):

1. Load the **E-SYS private key** from `security/sec_security.lic` (an XML-wrapped PKCS#12). Its
   keystore password is **not a secret you type** — PSdZ derives it, and so does the tool, as
   `HEX_UPPER(SHA1(passphrase[pid]))` from the BMW logo PNGs in your own PSdZ `resource.jar`
   (`nbtevo/psdz_passphrase.py`; point `--resource-jar` at `PSdZ/bin/psdz/resource.jar`).
2. **RSA-unwrap** (PKCS#1 v1.5) the NCD session key — the one named by `sec_ncdkeys.xml`'s
   `encKeyRef` — in `security/sec_keyreference.xml` → an AES-128 key.
3. **AES-128-CBC** (IV = 0) decrypt the `sec_ncdkeys.xml` entry for **your BTLD**, PKCS#5-unpad →
   a PKCS#8 RSA private key (`modulus N`, `private exponent d`, `digestAlg`).

The recovered **modulus is public** (it's baked into the HU firmware); the tool prints it so you can
confirm it matches. The **private exponent is secret** — it is written to a gitignored key file and
nothing else.

> This is an interoperability recovery of **your own** key from **your own** licensed data, for
> **your own** car. The toolkit ships no key and embeds no BMW secret — not the logo resources, not
> the passphrase, not the derived keystore password; all come from your own install. See
> [LEGAL.md](../../LEGAL.md).

## Firmware enforcement — what's proven, what isn't

- **Proven (NBT EVO):** the HU re-verifies the `0x3010` RSA signature over `0x3000`–`0x300F` at
  **every boot**, with the MD5/RSA-1024/e=3 primitive above, using the `00001FFD` public key. An
  unsigned/stale edit reverts. The signer here reproduces the car's own on-NVM signature
  byte-for-byte (that's the self-test).
- **Proven (coding flow, generally):** PSdZ aborts the write (`WRONG_CODING_SIG`) unless the ECU's
  `CheckCodingSignature` routine answers `checkSignCorrect`. So a correct signature is required to
  finalize, regardless of boot behavior.
- **Not assumed:** some sibling modules (e.g. the cluster) do only a *plausibility* check at boot
  and enforce the crypto only through the write flow. Don't generalize one module's boot behavior
  to another — the write-flow enforcement is the dependable invariant.

Next: [03-write-flow.md](03-write-flow.md) turns a signed NCD into a durable write on the car.
