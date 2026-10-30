# Contributing

Thanks for wanting to improve this. Two rules keep the project publishable and legitimate; please
hold the line on both.

## 1. Ship no owner/manufacturer data — ever

This repo contains **no** PSdZData, firmware, coding datasets (CAFD/NCD), FSC codes, keys, VINs, or
other vehicle identifiers, and it never will. Contribute **method, tooling, and validators** that
operate on data the *user supplies from their own licensed sources*.

- No keys, no `.ncd`/`.caf`, no firmware/flash binaries, no VINs, no packet captures. The
  `.gitignore` is a safety net, not permission — don't commit these even if a pattern misses them.
- No embedded manufacturer secrets, and no values *derived* from them — no PKCS#12 password, no
  passphrase, no logo/resource blobs. Where a step needs such a value, **derive it at run time from
  the user's own licensed install** (as `nbtevo/psdz_passphrase.py` does for the keystore password),
  never bake it in.
- Reference files by **name + hash + id/version**, not by shipping them (see
  `docs/psdzdata-manifest.md`).

## 2. Keep it owner-authorized

Everything here is for an owner working on their **own** car. Don't add anything whose purpose is
to operate on vehicles the user doesn't own, to forge entitlements for other cars, or to defeat
emissions or theft/immobilizer protections. See [LEGAL.md](LEGAL.md).

## Style and conventions

- Shared primitives go in `nbtevo/`; capability-specific code under `capabilities/<name>/tools/`
  and validators under `.../validate/`. Scripts are runnable as `python -m
  capabilities.<name>.tools.<script>`.
- Each capability folder is self-contained: a concept doc, tools, and a validator the user runs
  **before** touching the car.
- Be honest about confidence. Mark what's proven vs. plausible; a 🔜 outline must not read like a
  finished tool. State negative-response codes and failures faithfully.
- Reads are free; writes are gated. Anything that writes to a vehicle or recovers a key must go
  through `nbtevo.consent`.

## Status convention

- ✅ fully worked — concept + tools + a validator, exercised.
- 🔜 outline — mechanism documented, tooling being ported. Say so clearly.
