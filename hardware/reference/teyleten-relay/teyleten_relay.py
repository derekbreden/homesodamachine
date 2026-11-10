"""Expose the Teyleten relay replica's mounting datums and installation wire interfaces.

The frozen reference shows an idealized component exterior around a fitted PCB.
Both ends carry screw terminals. X runs toward the relay-contact end; Z rises
from the PCB underside toward the components. Covered surfaces and deep cavities
remain unqualified, as recorded in scan-model-evidence.json.

scan-datums.json owns the dimensions. scan_model.rs prepares the frozen geometry;
frozen-asset.json records the resulting model and display payload.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
STEP_PATH = _HERE / "teyleten-relay.step"
PAYLOAD_PATH = _HERE / "teyleten-relay.step.mesh"
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"

# Dimensional readers share the frozen reference's scan datums.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('teyleten_relay')
globals().update({name: _reference_values[name] for name in ('length', 'width', 'pcb_t', 'envelope_z', 'pin_drop', 'hole_dia', 'hole_dx', 'hole_dy', 'name', 'holes', 'screw_blk_inset', 'screw_blk_h', 'header_inset', 'header_h', 'land_z')})


def contacts():
    "The relay-contact wire entries: `(position, outward axis)` in the native frame."
    return _reference_data('teyleten_relay', 'contacts', (), {})


def logic():
    'The control-terminal wire entries in the native frame.'
    return _reference_data('teyleten_relay', 'logic', (), {})


def main():
    print("Teyleten 3.3 V opto-isolated relay module")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
