"""Reference solid for the Mean Well IRM-90-12ST — 12 V / 6.7 A encapsulated
AC-DC power module (the screw-terminal "ST" variant), used once on back-top's
ceiling.

Geometry from the official Mean Well IRM-90-SPEC mechanical drawing: a potted
brick whose two short ends step down to 6.7 mm ledges carrying the screw-terminal
blocks (AC in on one end, DC out on the other).

Coordinate frame
----------------
- X = width (52 mm), Y = length (109 mm), Z = height up from the base.
- Origin at the footprint center; Z = 0 the mounting (base) plane.
- AC 2-pole screw block at +Y end, DC 4-pole screw block at -Y end.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
STEP_PATH = _HERE / "meanwell-irm90.step"
PAYLOAD_PATH = _HERE / "meanwell-irm90.step.mesh"
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"

# --- Measured / datasheet geometry ----------------------------------------

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('meanwell_irm90')
globals().update({name: _reference_values[name] for name in ('width', 'length', 'height', 'ledge_h', 'ledge_len', 'hole_dia', 'hole_dx', 'hole_dy', 'mass_g', 'holes', 'block_inset', 'block_h', 'block_w', 'block_len')})


# The mount pattern in the module's own frame, on the base plane the bores are entered
# from — the four M3 clearance holes, which run the potting's whole height, so an M3 goes
# in from the top face and lands in whatever stands under the base.

# Screw heads face +Z. Wire entries face out along the module's long axis,
# +Y for AC and -Y for DC. Block dimensions are representative, not measured.


def _block(sy):
    return _reference_data('meanwell_irm90', '_block', (sy,), {})


def ac_in():
    "AC screw-head plane and screwdriver axis in the module's frame."
    return _reference_data('meanwell_irm90', 'ac_in', (), {})


def dc_out():
    "DC screw-head plane and screwdriver axis in the module's frame."
    return _reference_data('meanwell_irm90', 'dc_out', (), {})


def wire_entry(side):
    'Representative wire-mouth centre and outward axis, AC +1 / DC -1.\n\n    Separate from the screw-head axis. The side-entry mouths and screw heads\n    require room in different directions.\n    '
    return _reference_data('meanwell_irm90', 'wire_entry', (side,), {})


def main():
    print("Mean Well IRM-90-12ST power module")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
