#!/usr/bin/env python3
"""
Overlay our firmware-traced labels onto the shipped coding definitions.

The research map we keep alongside this toolkit describes each coding function in its own words. For
some functions that text was written from the firmware itself (``basis: firmware``):
  - the code that reads the value;
  - the unit's own symbol/raw table;
  - the artwork or files it loads.
Firmware-traced text is preferred over every other source, including the token-derived labels the
definitions were first built from.

For each firmware-traced function, matched by coordinate ``(dg, byte, mask)``, this script:
  - replaces the name, description and value labels;
  - adds checklist bits (``flags``) and number specs (``number``, ``presets``);
  - fixes a token that isn't a real token;
  - records why a value has no effect when the trace found no reader;
  - marks the record ``source: firmware-trace``.
The script also replaces two kinds of record with the research map's own text for that coordinate,
whatever its basis:
  - records whose ``source`` isn't one of our own (``OURS``);
  - every function the research map flags ``clean_room`` (``--inputs``), i.e. one it re-authored from
    BMW's token, the unit's own value table and the CAFD gate alone.
That text is marked ``firmware-token`` when it wasn't traced. Every shipped record should come from our
own reverse engineering; the script warns about any that doesn't.

It then rebuilds both shipped files. Re-run it whenever the research map gains more traced functions.

Inputs (from the research map, not shipped here):
  USERFACING.json  {"functions": [{function, name, description, values:[{raw, symbol, label}],
                    confidence, basis, [flags], [number, presets, specials], [hidden], note}]}
  FIELDS.json      {"fields": {function: {dg, byte, mask, ...} | {unmapped: true}}}

  INPUTS/         chunk_*.json, the research map's per-function inputs, carrying ``clean_room``

Usage:
    python apply_firmware_labels.py USERFACING.json FIELDS.json --inputs INPUTS/ [--out-dir .]
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

from build_definitions import CAFD, KEEP, build_md, scrub_text


def car_agnostic(text: str) -> str:
    """The map is written car-agnostic; scrub only if a per-car clause slipped in (scrubbing normalizes punctuation)."""
    return scrub_text(text) if "this car" in text.lower() else text

_TOKEN = re.compile(r"^[A-Za-z0-9_]+$")
# Provenance values from our own reverse engineering (see ../04-definitions.md, "Which source wins").
OURS = {"firmware-trace", "firmware", "firmware-token", "inferred"}
_XREF = re.compile(r"“([^”]+)”")


def coord_key(dg, byte, mask) -> tuple:
    return (str(dg).upper(), int(byte), int(mask, 16) if isinstance(mask, str) else int(mask))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("userfacing")
    ap.add_argument("fields")
    ap.add_argument("--inputs", help="dir of chunk_*.json inputs; functions flagged clean_room are replaced")
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent))
    a = ap.parse_args()

    out = Path(a.out_dir)
    defs_path = out / f"cafd_{CAFD.lower()}_definitions.json"
    recs = json.loads(defs_path.read_text())
    by_coord = {coord_key(r["dg"], r["byte"], int(r["mask"].rstrip("b"), 2)): r for r in recs}
    functions = json.loads(Path(a.userfacing).read_text())["functions"]
    fields = json.loads(Path(a.fields).read_text())["fields"]
    clean_room = set()
    for p in sorted(glob.glob(str(Path(a.inputs) / "chunk_*.json"))) if a.inputs else []:
        clean_room |= {r["token"] for r in json.loads(Path(p).read_text()) if r.get("clean_room")}

    # Descriptions refer to other functions by name ("see “Startup screen”"). Our names differ from the
    # map's wherever a function isn't traced yet, so append the coordinate to make the reference stand alone.
    coord_of, names = {}, {}
    for f in functions:
        c = fields.get(f["function"], {})
        if "dg" in c and coord_key(c["dg"], c["byte"], c["mask"]) in by_coord:
            coord_of[f["function"]] = by_coord[coord_key(c["dg"], c["byte"], c["mask"])]["coord"]
            names.setdefault(f["name"], []).append(coord_of[f["function"]])

    def xref(text: str) -> str:
        def sub(m):
            hits = names.get(m.group(1), [])
            return f"{m.group(0)} (`{hits[0]}`)" if len(hits) == 1 else m.group(0)
        return _XREF.sub(sub, text)

    applied, replaced, unmapped = 0, 0, []
    for f in functions:
        traced = f.get("basis") == "firmware"
        if f["function"] not in coord_of:
            if traced:
                unmapped.append(f["function"])
            continue
        c = fields[f["function"]]
        r = by_coord[coord_key(c["dg"], c["byte"], c["mask"])]
        if not traced and r.get("source") in OURS and f["function"] not in clean_room:
            continue
        token = f["function"].split(".", 1)[1]
        if not _TOKEN.match(r.get("token") or ""):
            r["token"] = token
        r["name"] = f["name"]
        r["description"] = xref(car_agnostic(f["description"]))
        values = {str(v["raw"]): v["label"] for v in f.get("values", [])}
        values.update({str(s["raw"]): s["label"] for s in f.get("specials", [])})
        r["values"] = values
        for k in ("flags", "number", "presets"):
            if f.get(k):
                r[k] = f[k]
            else:
                r.pop(k, None)
        r["confidence"] = f["confidence"]
        r["source"] = "firmware-trace" if traced else "firmware-token"
        # Earlier notes came from the sources this replaces; keep only what the trace established.
        r.pop("notes", None)
        if f.get("hidden"):
            r["notes"] = car_agnostic("Not a user setting: " + f["hidden"])
        applied += traced
        replaced += not traced

    recs = [{k: r[k] for k in KEEP if k in r} for r in recs]
    recs.sort(key=lambda r: (r["dg"], r["byte"], r["mask"]))
    defs_path.write_text(json.dumps(recs, indent=1, ensure_ascii=False))
    (out / f"cafd_{CAFD.lower()}_definitions.md").write_text(build_md(recs))
    print(f"applied {applied} firmware-traced functions and re-authored {replaced} records "
          f"in {defs_path.name} (+ .md)")
    left = [r["coord"] for r in recs if r.get("source") not in OURS]
    if left:
        print(f"WARNING: {len(left)} records have a source that isn't ours: {', '.join(left)}")
    if unmapped:
        print(f"skipped {len(unmapped)} with no single coordinate: {', '.join(unmapped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
