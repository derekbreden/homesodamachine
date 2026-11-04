"""Line-art reference solid of the neoFit ABU44 acetal bulkhead connector — the 1/4" tube
through-wall union the rear face's CO2 inlet is clamped in.

Reduced to coaxial cylinders: a collet body and release ring at each end with
the M17 barrel spanning the panel and separate nut. Figures come from neoFit's
*Bulkhead Union* dimensional sheet (`ABU44` row). Its B1/B2 dimensions are tube
stop depths. The external division about the flange is a nominal, unmeasured
reference; only the overall length and named panel/nut dimensions are drawn
from the sheet. Confirm received fitting dimensions before accepting this fit.

    Pressure          290 psi at 33 °F and 68 °F, 232 psi at 150 °F
    Max torque        1.1 ft lb on the nut
    Barrel            M17 × 1.5 — a PARALLEL metric thread, so the nut runs the whole length
                      of it and the panel is clamped between nut and flange
    Bag               10

The barrel sets the rear panel's clearance bore. The selected production grid
retains a 6 mm clamped stack between flange and nut, with the colored label
recess included in that stack.

Coordinate convention — jg_bulkhead_union's, so the two families seat the same way:
  Y = tube-flow axis. +Y = outward, toward the customer's tube.
  Origin = the flange's panel-seating face. The flange and everything beyond it sit at y ≥ 0;
      the barrel and the far end sit at y < 0.
  +Z = up. X completes the right-handed frame.

Run:
    tools/cad-venv/bin/python hardware/reference/neofit-bulkhead/neofit_bulkhead.py
    tools/cad-venv/bin/python hardware/reference/neofit-bulkhead/neofit_bulkhead.py selftest

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

STEP = _here.parent / "neofit-bulkhead.step"


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('neofit_bulkhead')
globals().update({name: _reference_values[name] for name in ('_IN', 'TUBE_OD', 'THREAD_D', 'THREAD_PITCH', 'OVERALL', 'FLANGE_AF', 'NUT_AF', 'TUBE_STOP_DEPTH', 'NOMINAL_OUTBOARD_REACH', 'PANEL_THREAD', 'NUT_LEN', 'MASS_G', 'PRESSURE_PSI_68F', 'MAX_TORQUE_FTLB', 'FLANGE_D', 'NUT_D', 'near_ring_face_y', 'far_ring_face_y', 'far_body_face_y', 'PROUD_LENGTH')})



def _corners(across_flats: float):
    "A hex's across-corners envelope, which is what crowds a neighbour on a panel."
    return _reference_data('neofit_bulkhead', '_corners', (across_flats,), {})


# --- the ABU44 row of neoFit's Bulkhead Union sheet -------------------------

# A — 7.899, the BARE BARREL the sheet dimensions between the flange's face and the nut's. It is
# the clear span available to the panel before the separately dimensioned nut.
# The production wall and flush label share the selected 6 mm clamped stack.

# The two hexes as the circles that crowd a neighbour on the wall.

# Seating planes along Y. The flange bears at y = 0 and stands proud outboard; the bare barrel
# and the inboard body run to y < 0.
#
# The separate nut is supplied by the panel assembly. A is the clear flange-to-nut
# span and E is the nut width: the threaded barrel continues through both. The
# inboard body begins beyond that complete span, so it does not occupy nut stock.
# Its radial envelope remains conservative and unmeasured.


def panel_hole_d(clearance: float):
    'The through-hole diameter, given the slip a panel wants around the barrel.'
    return _reference_data('neofit_bulkhead', 'panel_hole_d', (clearance,), {})


def panel_footprint():
    '`(width, height)` the fitting takes on the panel FACE — the nut, which is the wider of\n    its two hexes. Round to a neighbour, so one figure twice.'
    return _reference_data('neofit_bulkhead', 'panel_footprint', (), {})


def flange_footprint():
    'What the OUTBOARD flange covers, and so what a bulkhead ring has to reach past to show.'
    return _reference_data('neofit_bulkhead', 'flange_footprint', (), {})


def port(side: float):
    'One of the two 1/4" tube ports: `(position, outward axis)`, `side` picking the near\n    (+Y, outboard) or far (−Y, inboard) end.'
    return _reference_data('neofit_bulkhead', 'port', (side,), {})


def selftest() -> int:
    """The fitting against the sheet it is read from."""
    fails = []
    if abs((near_ring_face_y - far_ring_face_y) - OVERALL) > 1e-9:
        fails.append(
            f"the two end faces stand {near_ring_face_y - far_ring_face_y:.3f} apart and the "
            f"sheet's L is {OVERALL:.3f}")
    if FLANGE_D >= NUT_D:
        fails.append(
            f"the flange Ø{FLANGE_D:.3f} is not narrower than the nut Ø{NUT_D:.3f}, and "
            f"`panel_footprint` reports the nut as the wider")
    if TUBE_OD >= THREAD_D:
        fails.append(f"a Ø{TUBE_OD:g} bore does not fit inside a Ø{THREAD_D:g} barrel")
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  neofit-bulkhead ABU44  M{THREAD_D:g}×{THREAD_PITCH:g}, "
              f"flange Ø{FLANGE_D:.2f} / nut Ø{NUT_D:.2f}, "
              f"{PANEL_THREAD:.2f} mm panel span plus {NUT_LEN:.2f} mm nut width, "
              f"{PRESSURE_PSI_68F:g} psi at 68 °F")
    return 1 if fails else 0


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'neofit-bulkhead.step'
PAYLOAD_PATH = _FROZEN_DIR / 'neofit-bulkhead.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('neofit-bulkhead frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
