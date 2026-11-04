"""The ASSE 1022's outlet adapter — 3/8" female-flare swivel onto 1/4"
push-to-connect, so the water path leaves the backflow preventer at 1/4" OD and
carries no 3/8" tubing on toward the pump
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2). It is what
lets the ASSE feed the 1/4" split (V-K + V-A) directly.

Two John Guest fittings made up as one stack — no single-piece 3/8"-flare ×
1/4"-push adapter exists in a potable grade, in any material or brand
([`ledger/bom.md`](/hardware/ledger/bom.md) §3):

  * **PI4512F6S** — 3/8" FFL swivel × 3/8" PTC, gray acetal, lead-free. Its
    chrome swivel nut draws the ASSE 1022's flare nose against the seat (flat-
    faced flare seal, no PTFE tape); its 3/8" collet faces downstream.
  * **PP061208W** — 3/8" stem × 1/4" PTC reducer, pushed into that collet. The
    stem is the whole 3/8" run: it starts and ends inside the fitting, and the
    LLDPE leaves at 1/4".

External envelope only — the swivel nut is a wrench hex that spins on the body
and never touches water, and both collets are plain cylinders at the cartridge
OD.

Frame: +X = flow axis, the swivel-nut face at X = 0 — it lands flat on the ASSE
1022's outlet face, so the two mate at that plane. The 1/4" PTC collet mouth is
at +X. Centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/flare38-14ptc/flare38_14ptc.py

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

# --- PI4512F6S, 3/8" FFL swivel x 3/8" PTC -------------------------------

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('flare38_14ptc')
globals().update({name: _reference_values[name] for name in ('NUT_ACROSS_CORNERS', 'NUT_LENGTH', 'NUT_BORE_D', 'NECK_D', 'NECK_LENGTH', 'COLLET38_D', 'COLLET38_LENGTH', 'COLLAR_LENGTH', 'COLLET14_D', 'COLLET14_LENGTH', 'TUBE_D', 'LENGTH')})

                            # flare nose occupies the nut rather than its metal

# --- PP061208W, 3/8" stem x 1/4" PTC reducer -----------------------------
# The stem itself is buried in the collet above; what stands proud is its collar
# and the 1/4" collet body.



def flare_face():
    "The swivel nut's seating face: (position, outward axis). Lands flat on the\n    ASSE 1022's flare outlet, so this face and that one are the same plane."
    return _reference_data('flare38_14ptc', 'flare_face', (), {})


def tube_port():
    'The 1/4" PTC mouth the LLDPE pushes into: (position, outward axis).'
    return _reference_data('flare38_14ptc', 'tube_port', (), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'flare38-14ptc.step'
PAYLOAD_PATH = _FROZEN_DIR / 'flare38-14ptc.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('flare38-14ptc frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
