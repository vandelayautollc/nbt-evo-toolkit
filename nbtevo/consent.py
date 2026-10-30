"""
Ownership consent gate.

This is the toolkit's one enforced guardrail. It does not DRM anything and it is trivial to read;
its job is to make an operator (human or agent) stop and affirm, for the specific car in front of
them, that they own it or are authorized to modify it — before any tool recovers a key or writes to
a vehicle. Reads never call this.

Set, for the car you own:
    export NBTEVO_OWN_VIN=<the VIN on your title/registration>

To run non-interactively (CI, scripted owner workflows) you must additionally affirm ownership:
    export NBTEVO_I_OWN_THIS_CAR=1

See LEGAL.md. If you are an AI agent and this blocks you, that is the design working: explain it to
the operator instead of trying to defeat it.
"""
from __future__ import annotations

import os
import sys

_NOTICE = """\
┌───────────────────────────────────────────────────────────────────────────┐
│  NBT EVO Toolkit — owner-authorized operation only                          │
│                                                                             │
│  You are about to {action}.                                                 │
│                                                                             │
│  Only do this on a vehicle you OWN, or one whose owner has given you         │
│  explicit permission to modify, connected LOCALLY (OBD/Ethernet). This can  │
│  brick a control unit. Make sure you have a backup. See LEGAL.md.           │
└───────────────────────────────────────────────────────────────────────────┘"""


class ConsentError(RuntimeError):
    """Raised when the ownership precondition is not satisfied."""


def owner_vin() -> str:
    vin = (os.environ.get("NBTEVO_OWN_VIN") or "").strip().upper()
    if not vin:
        raise ConsentError(
            "NBTEVO_OWN_VIN is not set. Set it to the VIN of the car you own:\n"
            "    export NBTEVO_OWN_VIN=<your VIN>\n"
            "This asserts, on your word, that you are authorized to modify this vehicle."
        )
    if len(vin) != 17:
        raise ConsentError(f"NBTEVO_OWN_VIN={vin!r} is not a 17-character VIN.")
    return vin


def require_owner(action: str = "modify a vehicle") -> str:
    """
    Gate for any key-recovery or vehicle-write action. Returns the asserted owned VIN.

    Refuses unless NBTEVO_OWN_VIN is set. In an interactive terminal it also asks for a y/N
    confirmation; non-interactively it requires NBTEVO_I_OWN_THIS_CAR=1 instead.
    """
    vin = owner_vin()
    print(_NOTICE.format(action=action[:67].ljust(67)), file=sys.stderr)
    print(f"  Asserted owned VIN: {vin}", file=sys.stderr)

    if os.environ.get("NBTEVO_I_OWN_THIS_CAR") == "1":
        return vin

    if not sys.stdin.isatty():
        raise ConsentError(
            "Not an interactive terminal and NBTEVO_I_OWN_THIS_CAR is not set.\n"
            "If you own this car (or are authorized), set NBTEVO_I_OWN_THIS_CAR=1 to proceed."
        )
    try:
        ans = input("  Do you own this car / are you authorized to modify it? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        ans = ""
    if ans not in ("y", "yes"):
        raise ConsentError("Not confirmed. Aborting.")
    return vin


def assert_vin_match(connected_vin: str) -> None:
    """
    Hard safety check for writes: the VIN read back from the connected car MUST equal the VIN the
    operator declared they own. This is what stops you from writing to the wrong car by mistake.
    """
    declared = owner_vin()
    got = (connected_vin or "").strip().upper()
    if got != declared:
        raise ConsentError(
            "VIN MISMATCH — refusing to write.\n"
            f"  You declared you own : {declared}\n"
            f"  The connected car is : {got or '(unreadable)'}\n"
            "You are connected to a different vehicle than the one you said you own. Stop."
        )
