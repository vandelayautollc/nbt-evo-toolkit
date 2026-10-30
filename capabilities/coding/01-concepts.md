# 01 · Coding concepts

The vocabulary the rest of this section uses. All of it is readable from your own car and your own
CAFD; none of it is secret.

## Datagroups and coordinates

The head unit's coding lives in a set of **datagroups**, each a short page of bytes. On the NBT EVO
(CAFD `00001EF6`) the user coding datagroups are **`0x3000`–`0x300D`**, with `0x300F` holding the
**CAF_ID** (the live coding dataset's SGBM id) and **`0x3010`** holding the **signature** (see
[02-signing-model.md](02-signing-model.md)).

A single coding parameter is addressed by a **coordinate**: `(datagroup, byte offset, bit mask)`.
For example `0x3001 / 0x62 / 0x78` is "datagroup 0x3001, byte 0x62, bits 3–6". A parameter may be
one bit, a few bits, a whole byte, or several bytes. Reading the parameter = masking those bits out
of the byte; writing it = merging new bits in (what `nbtevo.srec.set_byte` does).

```
datagroup 0x3001, byte 0x62 = 0b x010 1xxx
                                   └┬─┘        value field under mask 0x78, shift 3  →  value 2
```

## CAFD — the layout

The **CAFD** (Coding Application Function Data) is BMW's definition of *what each coordinate means*
for a given head unit: which datagroups exist, which bits form which parameter, and (stripped of
human names) the engineering tokens and enumerations. It is distributed inside PSdZData as an
encrypted container (`cafd_<id>.caf.<ver>`) and identified by an SGBM id + version — here
`00001EF6` v`006.048.013`.

- You **read the current values** from the car (the datagroup bytes).
- You **interpret** them with the CAFD layout (which bits are which parameter).
- [04-definitions.md](04-definitions.md) covers decrypting your CAFD and building a human map.

Two live CAFD versions are known to share the NBT EVO layout: `006.048.013` and `006.064.014`. The
tools decode by reading the version from the car, not by assuming one.

## NCD — the container on the wire

When coding is written, the bytes travel as an **NCD** (the coding dataset), formatted as a
**Motorola S-record** file. The mapping is simple and total:

```
S-record address = (datagroup << 8) | byte_offset
    0x3001, 0x62  →  0x300162
    0x3010, 0x00  →  0x301000   (signature datagroup)
```

`nbtevo.srec` parses an NCD into a flat `addr → byte` map, lets you edit it, and re-emits it with
checksums recomputed and nothing else moved. A **backup** (`read_coding.py`) is just the live
datagroups captured as an NCD, which you can diff, edit, and write back.

## CPS — the coding production stamp

After a successful coded write, the flow writes a **CPS** (`Codierpruefstempel`, DID `0x37FE`) — a
production stamp recording that a valid coding operation completed. The write flow writes it last,
reads it back, and only then resets the ECU. If the signature check fails, the CPS is *not* written
and the operation aborts. See [03-write-flow.md](03-write-flow.md).

## Why a byte edit alone reverts

The head unit verifies the signature datagroup against the coding bytes **at boot**. Edit a
datagroup without recomputing `0x3010`, and the next boot sees a coding whose signature no longer
matches — and restores the previous/default coding. This is the single most common mistake. The
fix is not a trick; it's to hold the signing key and re-sign, which is exactly what this capability
is about.

## The durable tier

Even a *correctly signed* write is only made durable when the HU commits it to the **V850** (the
always-on MCU that keeps nvram). The authenticated UDS coding flow triggers that commit as part of
its finalize + reset; a volatile shell `store` does **not**. So: durable coding = signed NCD
written through the UDS flow in [03-write-flow.md](03-write-flow.md), not a shell poke.
