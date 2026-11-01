"""ACEIRMC MQ-6 combustible-gas (LPG / isobutane) sensor module — the
appliance's `mq6-sensor`, lying on edge along the floor of the refrigeration
bay's −X strip where leaked isobutane pools on the cabinet floor.
`enclosure._west_cradle` prints the two posts that hold it and
`enclosure_assembly.build_mq6` places it.

External envelope only — the carrier PCB, the cylindrical MQ-6 sensor can on
top, and the 4-pin header (VCC / GND / DO / AO) below one edge. The comparator
IC, trim pot and LEDs are flush SMD and not modeled. THE BOARD CARRIES NO
MOUNTING HOLE, which is why what holds it is a slot its edges slide into rather
than a pair of screws.

Frame: PCB in the XY plane, sensor can up (+Z), header pins down (-Z); the
header-pin tips sit at Z = 0 (the bbox floor). Origin centered on the PCB.

The can is centred on the board, so it leaves `PCB_Y / 2 - CAN_D / 2` — half a
millimetre — at each LONG edge and `PCB_X / 2 - CAN_D / 2` at each SHORT one.
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

PCB_X, PCB_Y, PCB_T = 32.0, 20.0, 1.6
CAN_D, CAN_H = 19.0, 14.0            # MQ-6 sensor can (steel mesh cap)
PIN_LEN = 6.0                        # header pins below the board
PIN_SQ = 0.64                        # 0.025" square post
PIN_PITCH = 2.54
PIN_COUNT = 4
PIN_ROW_INSET = 3.0                  # header centreline in from the -X short edge


def card_plane():
    """The board's own centre, on its mid-plane, as a `(position, outward axis)` station.

    This is the point whatever holds the card is stationed on. THE BOX'S CENTRE IS NOT IT:
    the pins reach 6 mm off one face and the can 14 off the other, so a slot struck on the
    box would sit 4 mm behind the card it grips."""
    return ((0.0, 0.0, PIN_LEN + PCB_T / 2.0), (0.0, 0.0, 1.0))


def header_span():
    """The pin field's own extent, as `(along the row, off the board's centre)`.

    Whatever holds this board has to open a way through to the header — the pins face
    the board's back, so a cheek that crosses them is a cheek the loom cannot pass.
    Read off the header rather than typed where the cradle is cut."""
    return ((PIN_COUNT - 1) * PIN_PITCH / 2.0 + PIN_SQ / 2.0,
            PCB_X / 2.0 - PIN_ROW_INSET)


def main():
    print("ACEIRMC MQ-6 combustible-gas sensor module")
    print(f"  PCB {PCB_X}×{PCB_Y}×{PCB_T}; can Ø{CAN_D}×{CAN_H}; {PIN_COUNT}-pin header × {PIN_LEN}")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
