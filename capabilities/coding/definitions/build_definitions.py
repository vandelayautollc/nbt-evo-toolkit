#!/usr/bin/env python3
"""
Build the shipped coding-definitions files from a human-map JSON.

The definitions describe *what each coding coordinate means* for CAFD 00001EF6 — our own
descriptions, not BMW data. This script produces the two files that ship in this folder:

  cafd_00001ef6_definitions.json   machine-readable, one record per coordinate
  cafd_00001ef6_definitions.md     human-readable, grouped by datagroup

It strips the two car-specific fields a working map carries (``active`` = this car's current value,
and the "on this car" phrasing of ``fa_gate``) so what ships is purely the definition. Re-run it
against a map regenerated from your own CAFD (see ../04-definitions.md) to refresh or extend these.

Usage:
    python build_definitions.py SOURCE_human_map.json [--out-dir .]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

# Text fields may carry this car's activation state ("Inactive on this car.", "Active via FA …").
# Drop any clause mentioning "on this car" so the shipped descriptions are car-agnostic.
_CAR_CLAUSE = re.compile(r"[^.;,]*\bthis car\b[^.;,]*", re.IGNORECASE)


def scrub_text(t: str | None) -> str:
    if not t:
        return ""
    t = _CAR_CLAUSE.sub("", t)
    t = re.sub(r"\s*([.;,])(\s*[.;,])+", r"\1", t)   # collapse orphaned delimiters
    t = re.sub(r"\(\s*\)", "", t)                      # empty parens left behind
    t = re.sub(r"\s{2,}", " ", t).strip(" ;,.")
    return (t + ".") if t and not t.endswith((".", "!", "?")) else t

CAFD = "00001EF6"
VERSION = "006.048.013"

# Fields that are pure definition (generic to the CAFD), in ship order.
KEEP = ["coord", "dg", "byte", "end", "mask", "field", "default", "fa_gate", "gate_crits",
        "token", "name", "description", "values", "flags", "number", "presets", "confidence",
        "source", "notes"]


def scrub(rec: dict) -> dict:
    out = {k: rec[k] for k in KEEP if k in rec}
    # Normalize the car-specific gate phrasing to a generic statement.
    g = str(out.get("fa_gate", "")).strip().lower()
    if "this car" in g:
        out["fa_gate"] = "FA-gated (depends on vehicle options)"
    # Strip car-specific activation state from free text.
    for f in ("description", "notes"):
        if f in out:
            cleaned = scrub_text(out[f])
            if cleaned:
                out[f] = cleaned
            else:
                out.pop(f, None)
    return out


def build_md(recs: list) -> str:
    by_dg: dict[str, list] = defaultdict(list)
    for r in recs:
        by_dg[r["dg"]].append(r)
    lines = [
        f"# NBT EVO coding definitions — CAFD {CAFD} (v{VERSION})",
        "",
        f"Human-readable description of every coding parameter in CAFD `{CAFD}`: what each "
        "coordinate `(datagroup, byte, mask)` is, its settable values, the factory default, and an "
        "honest confidence rating. These are our own descriptions reconstructed from firmware "
        "tokens, enum tables, and traces (see [../04-definitions.md](../04-definitions.md)); they "
        "are not BMW data. Car-specific state has been removed.",
        "",
        f"**{len(recs)} parameters.** Confidence: `high` = corroborated; `med` = reasoned from one "
        "good source; `low` = genuinely reserved/undocumented (not a guess).",
        "",
        f"**{sum(1 for r in recs if r.get('source') == 'firmware-trace')} are `source: firmware-trace`:** "
        "name, description and value labels written from the firmware itself (the code that reads the "
        "value, the unit's own value table, the files it loads). Where a firmware trace exists it is "
        "preferred over every other source.",
        "",
    ]
    for dg in sorted(by_dg):
        rs = by_dg[dg]
        lines.append(f"## Datagroup 0x{dg} ({len(rs)} parameters)")
        lines.append("")
        for r in sorted(rs, key=lambda x: (x["byte"], x["mask"])):
            name = r.get("name") or f"({r.get('token','?')})"
            lines.append(f"### `{r['coord']}` — {name}  ·  _{r.get('confidence','?')}_")
            if r.get("description"):
                lines.append("")
                lines.append(r["description"])
            vals = r.get("values") or {}
            if vals:
                lines.append("")
                lines.append("| value | meaning |")
                lines.append("|---|---|")
                for k, v in vals.items():
                    lines.append(f"| `{k}` | {v} |")
            if r.get("flags"):
                lines.append("")
                lines.append("Bits (set = on): " + "; ".join(f"bit {b} {lab}" for b, lab in r["flags"].items()))
            if r.get("number"):
                n = r["number"]
                lines.append("")
                lines.append(f"Number: raw {n['min']}–{n['max']} × {n['factor']} + {n['offset']} {n.get('unit', '')}".rstrip()
                             + (f"; typical {', '.join(map(str, r['presets']))}" if r.get("presets") else ""))
            if r.get("notes") and r.get("source") == "firmware-trace":
                lines.append("")
                lines.append(f"_{r['notes']}_")
            meta = []
            if r.get("default") not in (None, ""):
                meta.append(f"default `{r['default']}`")
            if r.get("fa_gate"):
                meta.append(f"gate: {r['fa_gate']}")
            if r.get("token"):
                meta.append(f"token `{r['token']}`")
            if r.get("source"):
                meta.append(f"source: {r['source']}")
            if meta:
                lines.append("")
                lines.append("· ".join(meta))
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="human-map JSON (list of per-coordinate records)")
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()

    src = json.loads(Path(a.source).read_text())
    recs = [scrub(r) for r in (src if isinstance(src, list) else list(src.values()))]
    recs.sort(key=lambda r: (r["dg"], r["byte"], r["mask"]))

    out = Path(a.out_dir)
    (out / f"cafd_{CAFD.lower()}_definitions.json").write_text(json.dumps(recs, indent=1, ensure_ascii=False))
    (out / f"cafd_{CAFD.lower()}_definitions.md").write_text(build_md(recs))
    print(f"wrote {len(recs)} definitions to {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
