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

COLLET_D = 14.0             # 1/4" PTC collet body OD
COLLET_LENGTH = 13.5        # push-in cartridge + release collar
HEX_ACROSS_CORNERS = 16.5   # 9/16" hex (14.29 across flats)
HEX_LENGTH = 5.0            # wrench flat thickness
SHANK_D = 13.7              # 1/4" NPT major Ø (simplified, no helix)
SHANK_LENGTH = 11.0         # NPT engagement
TUBE_D = 6.35               # the 1/4" OD LLDPE it accepts
LENGTH = COLLET_LENGTH + HEX_LENGTH + SHANK_LENGTH


def tube_port():
    """The PTC mouth the 1/4" LLDPE pushes into: (position, outward axis)."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def shank_end():
    """The far end of the NPT male shank: (position, outward axis) — it threads
    SHANK_LENGTH into whatever female it meets."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


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
