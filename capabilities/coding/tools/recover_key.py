#!/usr/bin/env python3
"""
Recover YOUR coding signing (NCD) key — a thin wrapper over the shared recovery engine.

This is the same tool as `python -m nbtevo.keys --kind ncd …`, kept here so the coding happy path
reads naturally. For the SecurityAccess (L3) key that the coding *write* needs, use `--kind l3`
(via `nbtevo.keys`). The full key map is in ../../../docs/keys.md.

    python -m capabilities.coding.tools.recover_key --btld 00001FFD -o ~/.nbtevo/ncd_key.json \
        --resource-jar /path/to/your/PSdZ/bin/psdz/resource.jar

No passphrase is ever typed: the keystore password is derived from your own PSdZ resources
(see docs/keys.md and nbtevo/psdz_passphrase.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from nbtevo import keys  # noqa: E402

if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--kind" not in argv:
        argv = ["--kind", "ncd", *argv]   # coding's default key is the NCD signing key
    raise SystemExit(keys.main(argv))
