#!/usr/bin/env python3
"""
Validate an RSVI mesh before you build it into a model bundle and install it.

Checks the structural invariants the head unit's reader enforces (indices in range, stride matches
the element layout, triangle count consistent) and does a round-trip (read → write → read) to
confirm the mesh survives our codec content-identically. Offline; no car.

Usage:
    python -m capabilities.vehicle_models.validate.check_rsvi model.rsvi [more.rsvi ...]
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from capabilities.vehicle_models.tools import rsvi  # noqa: E402


def check_one(path: str) -> bool:
    m = rsvi.read_rsvi(path)
    ok = True

    def fail(msg: str):
        nonlocal ok
        print(f"  [FAIL] {msg}")
        ok = False

    # Structural invariants the HU reader requires.
    if m["numTriangles"] * 3 != len(m["indices"]):
        fail(f"triangle count {m['numTriangles']} != indices/3 {len(m['indices']) / 3:.1f}")
    if m["numVertices"] > 0x10000:
        fail(f"{m['numVertices']} vertices exceeds u16 index space (65536)")
    if m["indices"] and max(m["indices"]) >= m["numVertices"]:
        fail(f"index {max(m['indices'])} >= numVertices {m['numVertices']}")
    if any(e["usage"] not in rsvi.USAGE_SIZE for e in m["elements"]):
        fail("unknown vertex-element usage")
    if rsvi.attr(m, 0) is None:
        fail("no position element (usage 0) — the HU needs a_Position")

    # Round-trip: write what we read, read it back, compare content.
    if ok:
        with tempfile.NamedTemporaryFile(suffix=".rsvi", delete=False) as tf:
            tmp = tf.name
        try:
            rsvi.write_rsvi(tmp, m["elements"], m["vertices"], m["indices"])
            m2 = rsvi.read_rsvi(tmp)
            if m2["vertices"] != m["vertices"] or m2["indices"] != m["indices"]:
                fail("round-trip changed the mesh content")
        finally:
            Path(tmp).unlink(missing_ok=True)

    els = ", ".join((e["name"] or rsvi.USAGE_NAME[e["usage"]]) for e in m["elements"])
    print(f"  {Path(path).name}: {m['numVertices']} verts, {m['numTriangles']} tris, "
          f"stride {m['stride']} [{els}] {'OK' if ok else 'FAILED'}")
    return ok


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    all_ok = True
    for p in sys.argv[1:]:
        print(p)
        all_ok &= check_one(p)
    print("\n" + ("ALL PASS" if all_ok else "FAILED — do not install a mesh that fails validation."))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
