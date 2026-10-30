# FSC application-number catalog (NBT / NBT EVO)

The **application number** (AppNo) is the feature id carried in an FSC body (bytes 2–3, u16 BE — see
[01-concepts.md](01-concepts.md)). This table maps AppNo → feature, for the NBT / NBT EVO platform.

**Source & provenance:** the names are the verbatim `TITLE_ENGB` from BMW's ISTA repair database
table `XEP_SWIACTIVATIONCODE_SWT`, with its `FUNCTION` column (the platform tag) used to pick the
NBT/NBT-EVO variant of each feature. These are **feature-name facts**, not keys or codes — the
catalog tells you *which* AppNo a feature is; it does not contain any FSC. (ISTA stores the AppNo as
its **decimal** string; the FSC body uses the hex u16.)

| AppNo (hex) | dec | Feature | Platform note |
|---|---|---|---|
| `0x006F` | 111 | Satellite tuner (SDARS / SiriusXM) | SDARS, incl. NBT/NBTevo |
| `0x0078` | 120 | Satellite tuner (Radio2 SDARS) | |
| `0x0071` | 113 | Web browser | Champ2 browser |
| `0x0090` | 144 | Web browser | Entry Online browser |
| `0x007F` | 127 | Bluetooth | |
| `0x0099` | 153 | Bluetooth | |
| `0x007C` | 124 | Integrated telephony | |
| `0x0082` | 130 | Telephone | |
| `0x009C` | 156 | **BMW Apps** | Apps4Auto / A4A |
| `0x009E` | 158 | Voice processing (speech) | NBT — iSpeech |
| `0x009F` | 159 | Voice processing with read-out (TTS) | NBT — TTS |
| `0x00A0` | 160 | Professional navigation (US / ECE) | NBT — Navi Professional ECE/US |
| `0x00A1` | 161 | Professional navigation (Asia) | NBT — Navi Professional Asia |
| `0x00E5` | 229 | **M Laptimer** | NBT — Lap Timer |
| `0x00F5` | 245 | Road map — North America | NBT EVO map |
| `0x0120` | 288 | Road map — Europe | NBT EVO map |
| `0x0143` | 323 | **Apple CarPlay** | NBT / NBT EVO CarPlay |
| `0x016E` | 366 | Speech processing (NLU) | NBTevo Speech NLU (Nuance) |
| `0x016F` | 367 | Speech processing (TTS) | NBTevo Speech TTS |
| `0x0170` | 368 | Component protection (re-init) | ENTRYevo / NBTevo — *not* a voice feature |
| `0x01CF` | 471 | Map of Russia (FSC short) | NBT EVO |
| `0x01D0` | 472 | Map of Russia (FSC light) | NBT EVO |

Entry / EntryEVO / MGU variants of some of these exist under other AppNos (e.g. speech
`0x00C7/0x00C8` EntryNAV, `0x0112/0x0113` EntryEVO, `0x0179/0x017A` MGU) — they are **not** the
NBT EVO ones; match the platform tag to your unit. Confirm the live AppNo set on your own unit by
reading its FSC state ([03-apply-and-read.md](03-apply-and-read.md)) rather than assuming.
