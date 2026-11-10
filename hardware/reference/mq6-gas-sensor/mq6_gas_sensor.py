"""ACEIRMC MQ-6 combustible-gas (LPG / isobutane) sensor module — the
appliance's `mq6-sensor`, lying on edge along the floor of the refrigeration
bay's −X strip where leaked isobutane pools on the cabinet floor.
`enclosure._west_cradle` prints the two posts that hold it and
`enclosure_assembly.build_mq6` places it.

The carrier PCB and header datums locate its printed edge cradle. The Rust
producer models the sensor's stepped base and tapered cap. Comparator,
adjustment-pot and LED placement remain unmodeled pending received-board
evidence. The retained board has no mounting-hole geometry; the cradle grips
its short edges.

Frame: PCB in the XY plane, sensor can up (+Z), header pins down (-Z); the
header-pin tips sit at Z = 0 (the bbox floor). Origin centered on the PCB.

The can is centred on the board, so it leaves `PCB_Y / 2 - CAN_D / 2`
at each LONG edge and `PCB_X / 2 - CAN_D / 2` at each SHORT one.
THE SHORT EDGES, AT THE TWO ENDS OF THE LONG RUN, ARE THE ONLY ONES WITH
MATERIAL TO GRIP, and the cradle reads that off these constants.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
STEP_PATH = _HERE / "mq6-gas-sensor.step"
PAYLOAD_PATH = _HERE / "mq6-gas-sensor.step.mesh"
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('mq6_gas_sensor')
globals().update({name: _reference_values[name] for name in ('PCB_X', 'PCB_Y', 'PCB_T', 'CAN_D', 'CAN_H', 'PIN_LEN', 'PIN_SQ', 'PIN_PITCH', 'PIN_COUNT', 'PIN_ROW_INSET')})



def card_plane():
    "The board's own centre, on its mid-plane, as a `(position, outward axis)` station.\n\n    This is the point whatever holds the card is stationed on. THE BOX'S CENTRE IS NOT IT:\n    the pins reach 6 mm off one face and the can 14 off the other, so a slot struck on the\n    box would sit 4 mm behind the card it grips."
    return _reference_data('mq6_gas_sensor', 'card_plane', (), {})


def header_span():
    "The pin field's own extent, as `(along the row, off the board's centre)`.\n\n    Whatever holds this board has to open a way through to the header — the pins face\n    the board's back, so a cheek that crosses them is a cheek the loom cannot pass.\n    Read off the header rather than typed where the cradle is cut."
    return _reference_data('mq6_gas_sensor', 'header_span', (), {})


def main():
    print("ACEIRMC MQ-6 combustible-gas sensor module")
    print(f"  PCB {PCB_X}×{PCB_Y}×{PCB_T}; can Ø{CAN_D}×{CAN_H}; {PIN_COUNT}-pin header × {PIN_LEN}")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
