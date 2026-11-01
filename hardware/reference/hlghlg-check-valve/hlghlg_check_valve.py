"""HLGHLG 1/4" OD push-to-connect check valve, POM (Amazon B0FSSZS6HH) — the water-side check
between the G Ganen's discharge and the cold core's water inlet. It holds the carbonator's
pressure off the idle pump ([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2).

One moulded body: a push-to-connect socket at each end, a narrow neck behind the inlet socket
and the barrel carrying the moulded flow arrow behind that. The neck is the one section on it a
holder can key on, because a shoulder stands at each end of it.

External envelope only — the poppet, spring and seals are not modeled.

  PROVISIONAL: the listing dimensions it 51 mm end to end and 14 mm across, and gives no
pressure rating, cracking pressure or seal material. The sections between are scaled off the
listing's dimensioned photograph. Reconcile against a valve in hand.

Frame: the valve stands on Z with water running DOWN it, the inlet collet's mouth at Z = 0 and
the outlet's at −Z, centred on X and Y.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "hlghlg-check-valve.step"
PAYLOAD_PATH = _here.parent / "hlghlg-check-valve.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

TUBE_D = 6.35               # the 1/4" OD LLDPE both ends accept
LENGTH = 51.0               # the listing's end-to-end dimension
BODY_D = 14.0               # and its diameter, across the sockets

# Inlet first, as `(label, diameter, length)`.
SECTIONS = (
    ("inlet collet", 12.0, 1.6),
    ("inlet socket", BODY_D, 14.4),
    ("neck", 9.3, 6.2),
    ("barrel", 12.6, 11.6),
    ("barrel step", 13.0, 1.8),
    ("outlet socket", BODY_D, 13.4),
    ("outlet collet", 12.6, 2.0),
)


def sections():
    """Every section as `(label, radius, s0, s1)`, `s` running from the inlet down the valve."""
    out, s = [], 0.0
    for label, dia, length in SECTIONS:
        out.append((label, dia / 2.0, s, s + length))
        s += length
    return tuple(out)


def inlet():
    """The push-fit the discharge elbow's tube pushes into: (position, outward axis)."""
    return (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)


def outlet():
    """The push-fit the LLDPE to the core pushes into: (position, outward axis)."""
    return (0.0, 0.0, -LENGTH), (0.0, 0.0, -1.0)


def tube_port():
    """Downstream tube station used by the installed plumbing graph."""
    return outlet()


def main():
    print("hlghlg-check-valve")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
