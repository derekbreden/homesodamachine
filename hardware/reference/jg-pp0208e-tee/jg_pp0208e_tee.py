"""John Guest PP0208E — the 1/4" push-to-connect union tee in black polypropylene.

Three identical ports on one body: a straight RUN of two in line, and a BRANCH off the middle of
it at a right angle. Every port takes 1/4" OD LLDPE by push, and nothing on the fitting threads,
clamps or takes a tool. It is the tee in the install kit, the split on the ASSE 1022's outlet
(`../water-split/`), and six of the manifold's eight junctions.

The figures are John Guest's own, off the Polypropylene Equal Tee data sheet Pp4608_01/23, 1/4"
row — the row `PP0208W` (white), `PP0208W-B` (white, blue collet) and `PP0208E` (black) share.
`*B`, `*C` and `*G` are dimensioned there WITH THE COLLETS IN THE RELEASE POSITION, pressed home
against the collar, which is the state the solid here is cut in; at rest each collet stands
1.65 mm further out, calipered on the fitting in hand at `../tee-connector/README.md`.

The arm's own steps — the barrel between the hub and the collar, and the collet's outside — are
not on the data sheet. They are the tree's one drawing of a John Guest 1/4" push-fit port, shared
with the Quick Start's plumbing scenes (`../../quickstart/plumbing/`), so a collet the customer
pushes a tube into is the same collet wherever this repository draws one.

Coordinate frame
----------------
- The RUN on Z, its two collet faces at ±`REACH`. The BRANCH on +Y, its face at the same
  `REACH`. All three ports are coaxial with the body centre, which is the origin.
- The same frame `../tee-connector/` states, so a turn written for one tee turns the other.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-pp0208e-tee/jg_pp0208e_tee.py

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

STEP = _here.parent / "jg-pp0208e-tee.step"

# --- the data sheet, Pp4608_01/23, 1/4" row ---------------------------------


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('jg_pp0208e_tee')
globals().update({name: _reference_values[name] for name in ('TUBE_OD', 'RUN_SPAN', 'REACH', 'INSERTION', 'COLLAR_D', 'BORE_D', 'BRANCH_ENVELOPE', 'ARM_D', 'COLLAR_NEAR', 'COLLAR_FAR', 'COLLET_D', 'COLLET_BORE', 'COLLET_PROUD', 'MEASURE_TOL', 'ARMS')})


# --- the arm's profile, shared with `../../quickstart/plumbing/` -------------
# Outward from the hub each arm carries the same three sections: a barrel the neighbouring arm's
# root crosses, then the collar standing full `COLLAR_D`, then the release collet standing proud
# of the collar's face so a thumb reaches it around the tube.


# The three arms, each as `(outward axis, the port's own name)`. The run's two are the tee's
# straight-through path and the branch is what turns off it; which leg of a junction lands on
# which is the topology's business (`../../topology/fluid-topology.md`).


def run(sign: float):
    "One of the run's two collinear ports, `sign` picking the +Z or −Z end:\n    `(position, outward axis)`. The station is the COLLET'S own outer face — the plane a tube\n    crosses to enter, and runs `INSERTION` beyond."
    return _reference_data('jg_pp0208e_tee', 'run', (sign,), {})


def branch():
    'The third port, perpendicular to the run, out +Y.'
    return _reference_data('jg_pp0208e_tee', 'branch', (), {})


def stations():
    'All three ports, under the ends they stand on.'
    return _reference_data('jg_pp0208e_tee', 'stations', (), {})


def envelope():
    '`(across the run, along the run, off the branch)` — the box the fitting takes, and what\n    crowds a neighbour. The branch reads to the far side of the run body, not to its own centre,\n    because that is the side a wall stands on.'
    return _reference_data('jg_pp0208e_tee', 'envelope', (), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'jg-pp0208e-tee.step'
PAYLOAD_PATH = _FROZEN_DIR / 'jg-pp0208e-tee.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('jg-pp0208e-tee frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
