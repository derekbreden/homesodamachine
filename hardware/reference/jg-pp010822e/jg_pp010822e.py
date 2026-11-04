"""John Guest PP010822E male connector, 1/4" OD push-to-connect × 1/4" NPT M,
black polypropylene — the appliance's NPT-to-PTC transition. Six per build
([`ledger/bom.md`](/hardware/ledger/bom.md) §3): three on the water path, two on
the CO2 path, one on the carbonated-water outlet.

External envelope only — a PTC collet body, a wrench hex, and a plain-cylinder
NPT shank at its nominal major, no helix. Same modeling class as the neoFit bulkhead
inlet next door, one tube size down.

On the ASSE 1022 chain this is the last piece before the metal: the 1/4" LLDPE
from the rear-wall bulkhead pushes into the collet, and the shank threads into
the GAGIRA coupling's small end.

Frame: +X = flow axis, the PTC collet at X = 0 (upstream, where the tube pushes
in), the NPT shank at +X. Centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-pp010822e/jg_pp010822e.py

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('jg_pp010822e')
globals().update({name: _reference_values[name] for name in ('COLLET_D', 'COLLET_LENGTH', 'HEX_ACROSS_CORNERS', 'HEX_LENGTH', 'SHANK_D', 'SHANK_LENGTH', 'TUBE_D', 'LENGTH')})



def tube_port():
    'The PTC mouth the 1/4" LLDPE pushes into: (position, outward axis).'
    return _reference_data('jg_pp010822e', 'tube_port', (), {})


def shank_end():
    'The far end of the NPT male shank: (position, outward axis) — it threads\n    SHANK_LENGTH into whatever female it meets.'
    return _reference_data('jg_pp010822e', 'shank_end', (), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'jg-pp010822e.step'
PAYLOAD_PATH = _FROZEN_DIR / 'jg-pp010822e.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('jg-pp010822e frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
