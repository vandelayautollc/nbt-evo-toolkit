# PSdZData — the files you supply

This toolkit ships **no** BMW data. The scripts read **your own** copy of **PSdZData** — BMW's
official configuration/firmware/coding distribution — for the reference your agent needs (your
CAFD coding layout, your bootloader, your signing key store). This page says which files matter,
how to confirm you have the right ones, and where the tools expect them.

> You obtain PSdZData from your own licensed source. This project neither provides it nor tells you
> how to obtain it. Point the toolkit at your extracted copy:
> ```
> export NBTEVO_PSDZDATA=/path/to/your/psdzdata
> ```

## Layout of a PSdZData tree (the parts this toolkit uses)

```
psdzdata/
├── swe/                     software pool (very large; you need only a few files)
│   ├── cafd/   cafd_<id>.caf.<ver>     coding application function data (encrypted CMS)
│   ├── btld/   btld_<id>.bin.<ver>     bootloader
│   ├── swfl/   swfl_<id>.*             software flash payloads (HMI, media, speech, …)
│   └── flsl/   flsl_<id>.*             flash slot lists
├── security/
│   ├── sec_ncdkeys.xml      per-bootloader NCD (coding) signing keys  ← key recovery reads this
│   ├── sec_keyreference.xml session key references
│   ├── sec_auth_l3.xml      L3 SecurityAccess keys (coding write unlock)
│   └── sec_security.lic     XML-wrapped PKCS#12 holding the E-SYS private key (unwraps the session key)
└── mapping/
    └── blmap.xml            bootloader id → base-variant map (BTLD → HU_NBT2, …)
```

Key recovery also needs **one file from outside `psdzdata/`**: your PSdZ runtime's
`PSdZ/bin/psdz/resource.jar` (it ships in the same ISTA-D / Rheingold + PSdZ bundle). The
`sec_security.lic` keystore password is not a secret you type — the tool derives it from the BMW
logo PNGs inside that jar, exactly as PSdZ does. Point `--resource-jar` (or
`NBTEVO_PSDZ_RESOURCE_JAR`) at your own copy; nothing from it is committed. See
[keys.md](keys.md#recovering-a-key-the-one-tool).

## The NBT EVO head-unit software set

This is the HU's SVK as read from an NBT EVO (`HU_NBT2`, BTLD `00001FFD`). Use it to recognize the
files you need from your own pool. SGBM id + version together name the pool file
(e.g. CAFD `00001EF6` v`006.048.013` → `cafd_00001ef6.caf.006_048_013`). "scharfsign." =
production-signed.

| SGBM id | class | version | size | description |
|---|---|---|---|---|
| `00001EF6` | **CAFD** | 006.048.013 | 231 KB | **Coding data** — the one coding needs |
| `00001FFD` | **BTLD** | 007.051.002 | 108 MB | Bootloader NBT EVO — selects the coding key |
| `000024A7` | NAVD | 255.004.251 | — | Navigation map data |
| `000025DB` | ENTD | 004.016.002 | — | Entertainment data |
| `0000270B` | IBAD | 007.051.002 | 741 MB | Animations + MP3 (RR4) |
| `0000270C` | IBAD | 007.051.002 | 1.1 GB | Animations + MP3 (BMW) |
| `00002712` | IBAD | 007.051.002 | 210 MB | Text + graphics US/JAP/ASIA (RR4) |
| `00002714` | IBAD | 007.051.002 | 532 MB | Text + graphics US/JAP/ASIA (BMW) |
| `00002718` | SWFL | 007.051.002 | 129 MB | HMI (RR4) |
| `00002719` | SWFL | 007.051.002 | 513 MB | HMI |
| `0000271A` | SWFL | 007.051.002 | 942 MB | **NBT Core / Media / Connectivity / Nav** — the OPT_DEBUG flash target |
| `0000271C` | SWFL | 007.051.002 | 4 KB | TTS |
| `0000271E` | SWFL | 007.051.002 | 539 KB | EQ |
| `0000271F` | SWFL | 007.051.002 | 1.3 MB | Gateway table |
| `00002720` | SWFL | 007.051.002 | 758 MB | HMI common |
| `00002721` | SWFL | 007.051.002 | 213 MB | Speech Asia |
| `00002722` | SWFL | 007.051.002 | 108 MB | Speech USA |
| `00002727` | SWFL | 007.051.002 | 1.1 GB | Speech common |
| `00002FC4` | HWEL | 001.004.001 | — | Hardware element (US / ID5) |

> Your versions may differ — read your own car's SVK with `identify_btld.py` and match. The
> **class + id** are the stable identity; the version floats with I-Stufe.

## Confirming you have the right coding file

Coding only needs the **CAFD** (`00001EF6`) and, for writes, the **key store** + **BTLD id**. The
`.caf` pool file is an encrypted CMS container; the toolkit decrypts it to a CAFD XML spine. As a
regeneration check, the decrypted CAFD `00001EF6` version `006.048.013` is, byte-for-byte:

```
cafd_00001ef6_048_013.decrypted.xml
  sha256 = 4c7c2447a874841a904a5c93da3960c9f0f3aa0d0107b507dd4874f0416c4767
  size   = 7,011,305 bytes
```

(This is the *decrypted artifact*, which an owner regenerates from their own `.caf`; it is not a
BMW file and is identical for any NBT EVO on this CAFD version. If your regeneration produces these
bytes, your pipeline and your source agree.)

## Which key for which bootloader

The single most important mapping for coding writes: **the bootloader id selects the signing key.**
`sec_ncdkeys.xml` holds one entry per BTLD. Whether coding is offline-signable at all is decided
there — see `capabilities/coding/02-signing-model.md`. For the NBT EVO:

| BTLD | key in `sec_ncdkeys.xml` | scheme | offline? |
|---|---|---|---|
| `00001FFD` | filled RSA, `BMWSigVerify`, digest MD5 | legacy "coding version 1" | **yes** — the toolkit recovers it from your PSdZData |

`capabilities/coding/tools/recover_key.py` locates and decrypts **your** key for **your** BTLD from
**your** `sec_ncdkeys.xml`. The key never leaves your machine and is never committed (see
`.gitignore`).
