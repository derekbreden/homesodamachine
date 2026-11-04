"""GAGIRA 316L SS reducing coupling, 3/8" NPT F × 1/4" NPT F — the upstream
adapter that closes the gap between the appliance's 1/4" water run and the ASSE
1022's 3/8" male inlet ([`ledger/bom.md`](/hardware/ledger/bom.md) §3).

External envelope only — a hex barrel bored from each end at the major Ø of the
male thread that end takes, so a fitting threaded in occupies its socket rather
than the coupling's metal; the threads themselves are not cut. Hex 7/8" across
flats, the common size for a 3/8" body; length off the same fitting class.

The small (1/4" NPT F) end takes the John Guest PP010822E's male shank; the
large (3/8" NPT F) end threads onto the ASSE 1022's male inlet, so the coupling
sits between them on the flow axis.

Frame: +X = flow axis, the 1/4" (upstream) end at X = 0; centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/gagira-reducing-coupling/gagira_reducing_coupling.py

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
_reference_values = _reference_data('gagira_reducing_coupling')
globals().update({name: _reference_values[name] for name in ('HEX_ACROSS_CORNERS', 'LENGTH', 'SMALL_SOCKET_D', 'SMALL_SOCKET_DEPTH', 'LARGE_SOCKET_D', 'LARGE_SOCKET_DEPTH')})



def small_end():
    'The 1/4" NPT female end: (position, outward axis) — the PP010822E\'s shank\n    threads in this far (SMALL_SOCKET_DEPTH).'
    return _reference_data('gagira_reducing_coupling', 'small_end', (), {})


def large_end():
    'The 3/8" NPT female end: (position, outward axis) — this is what goes onto\n    the ASSE 1022\'s male inlet, LARGE_SOCKET_DEPTH deep.'
    return _reference_data('gagira_reducing_coupling', 'large_end', (), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'gagira-reducing-coupling.step'
PAYLOAD_PATH = _FROZEN_DIR / 'gagira-reducing-coupling.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('gagira-reducing-coupling frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
