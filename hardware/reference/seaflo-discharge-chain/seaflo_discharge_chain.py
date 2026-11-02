"""The water check chain — the three fittings that take the pump's discharge off
1/4" LLDPE, hold the carbonator's pressure off the pump when it is idle, and hand
the water back onto 1/4" LLDPE for the cold core's water inlet
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), made up on
the bench as one piece and laid in its rib on the cold core's cap.

The tube from the discharge elbow on the G Ganen's barb
([`diaphragm-pump-sleeve`](/hardware/printed-parts/diaphragm-pump-sleeve/README.md))
pushes into the first fitting:

  * **PP010822E** 1/4" PTC × 1/4" NPT M — its collet takes the elbow's tube and its
    thread goes into the check's socket.
  * **GASHER** 1/4" NPT check, female in / male out. The arrow points away from the
    pump.
  * **PP450822E** 1/4" NPT F × 1/4" PTC — its socket takes the check's male stub
    and its collet starts the 1/4" LLDPE to the core.

External envelopes only, each fitting a plain body at its nominal size; every
NPT joint is drawn made up to its engagement, so the length is what the chain
actually stands, not the sum of the parts.

Frame: the chain stands on Z with water running DOWN it, the inlet collet mouth at
Z = 0 and the outlet collet mouth at −Z. Centered on X and Y.

Run:
    tools/cad-venv/bin/python hardware/reference/seaflo-discharge-chain/seaflo_discharge_chain.py


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'seaflo-discharge-chain.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'seaflo-discharge-chain.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'seaflo-discharge-chain.fine.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"


def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
    raise SystemExit(0)


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "reference" / "gasher-check-valve"))
sys.path.insert(0, str(_hw / "reference" / "jg-pp010822e"))
import gasher_check_valve as check   # the middle fitting's own three sections
import jg_pp010822e as male          # the inlet fitting's collet, hex and shank

NPT_ENGAGE = 11.0           # how deep a 1/4" NPT male runs into its female

# John Guest PP450822E 1/4" NPT F x 1/4" PTC.
JG_SOCKET_D, JG_SOCKET_L = 15.0, 8.0
JG_HEX, JG_HEX_L = 16.5, 5.0
JG_COLLET_D, JG_COLLET_L = 14.0, 13.0

TUBE_D = 6.35               # the 1/4" OD LLDPE both collets accept


# The stack inlet first, as `(label, diameter, length)`. `build()` lays these down and a
# holder reads the same list for the section it seats on — the check is metal and the two John
# Guest fittings polypropylene, which is what says where a zip tie may close. A shank buried
# whole in its mate stands no length of its own.
SECTIONS = tuple(row for row in (
    ("PP010822E collet", male.COLLET_D, male.COLLET_LENGTH),
    ("PP010822E hex", male.HEX_ACROSS_CORNERS, male.HEX_LENGTH),
    ("PP010822E NPT", male.SHANK_D, male.SHANK_LENGTH - NPT_ENGAGE),
    ("GASHER socket", check.SOCKET_D, check.SOCKET_LENGTH),
    ("GASHER hex", check.HEX_ACROSS_CORNERS, check.HEX_LENGTH),
    ("GASHER stub", check.THREAD_D, check.STUB_LENGTH - NPT_ENGAGE),
    ("PP450822E socket", JG_SOCKET_D, JG_SOCKET_L),
    ("PP450822E hex", JG_HEX, JG_HEX_L),
    ("PP450822E collet", JG_COLLET_D, JG_COLLET_L),
) if row[2] > 0.0)

LENGTH = sum(length for _label, _dia, length in SECTIONS)


def sections():
    """Every section as `(label, radius, s0, s1)`, `s` running from the inlet down the chain."""
    out, s = [], 0.0
    for label, dia, length in SECTIONS:
        out.append((label, dia / 2.0, s, s + length))
        s += length
    return tuple(out)


def inlet():
    """The PP010822E's 1/4" PTC mouth the discharge elbow's tube pushes into:
    (position, outward axis)."""
    return (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)


def tube_port():
    """The PP450822E's 1/4" PTC mouth the LLDPE to the core pushes into: (position, axis)."""
    return (0.0, 0.0, -LENGTH), (0.0, 0.0, -1.0)


def build():
    """The three fittings stacked along −Z, inlet mouth at Z = 0, made up at each NPT joint
    so the stack stands its real length. The check's three sections come off its own module —
    socket boss, hex barrel, male stub, at the sizes it draws them."""
    import cadquery as cq
    part, z = None, 0.0
    for _label, dia, length in SECTIONS:
        z -= length
        seg = cq.Solid.makeCylinder(
            dia / 2.0, length, cq.Vector(0, 0, z), cq.Vector(0, 0, 1))
        part = seg if part is None else part.fuse(seg)
    return part


def __getattr__(name):
    if name == 'cq':
        import cadquery as cq
        return cq
    if name in {'export_assembly'}:
        import _cadq_export
        return getattr(_cadq_export, name)
    if name in {'one_body', 'M_STAINLESS'}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
