"""The supply reference exposes its manufacturer-derived mounting and terminal datums.

X spans the case width, Y its length, and Z rises from the mounting plane.
The footprint center is the origin, with the AC terminal row toward positive Y.
The Rust source cuts the exterior from the parameters beside this module.
"""

import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent
STEP_PATH = _HERE / "meanwell-irm90.step"
PAYLOAD_PATH = _HERE / "meanwell-irm90.step.mesh"
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"
_REPLICA = json.loads((_HERE / "replica-parameters.json").read_text())

# --- Measured / datasheet geometry ----------------------------------------

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('meanwell_irm90')
globals().update({name: _reference_values[name] for name in ('width', 'length', 'height', 'ledge_h', 'ledge_len', 'hole_dia', 'hole_dx', 'hole_dy', 'mass_g', 'holes', 'block_inset', 'block_h', 'block_w', 'block_len')})


def _terminal(side):
    return _REPLICA["terminal_interfaces"]["ac" if side > 0 else "dc"]


def _block(sy):
    row = _terminal(sy)
    return tuple(row["screw_center"]), tuple(row["screw_axis"])


def ac_in():
    "AC screw-head plane and screwdriver axis in the module's frame."
    return _block(1.)


def dc_out():
    "DC screw-head plane and screwdriver axis in the module's frame."
    return _block(-1.)


def wire_entry(side):
    "Wire-mouth row center and outward axis in the supply's frame."
    row = _terminal(side)
    return tuple(row["wire_center"]), tuple(row["wire_axis"])


def main():
    print("Mean Well IRM-90-12ST power module")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
