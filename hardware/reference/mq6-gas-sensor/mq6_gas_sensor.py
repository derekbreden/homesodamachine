"""ACEIRMC MQ-6 combustible-gas (LPG / isobutane) sensor module — the
appliance's `mq6-sensor`, standing on edge low in the refrigeration bay where
leaked isobutane pools on the cabinet floor. `enclosure._west_cradle` prints the
card slot that holds it and `enclosure_assembly.build_mq6` places it.

External envelope only — the carrier PCB, the cylindrical MQ-6 sensor can on
top, and the 4-pin header (VCC / GND / DO / AO) below one edge. The comparator
IC, trim pot and LEDs are flush SMD and not modeled. THE BOARD CARRIES NO
MOUNTING HOLE, which is why what holds it is a slot its edges slide into rather
than a pair of screws.

Frame: PCB in the XY plane, sensor can up (+Z), header pins down (-Z); the
header-pin tips sit at Z = 0 (the bbox floor). Origin centered on the PCB.

The can is centred on the board, so it leaves only half a millimetre at each
short edge and `PCB_Y / 2 - CAN_D / 2` at each long one. THE LONG EDGES ARE THE
ONLY ONES WITH MATERIAL TO GRIP, and the cradle reads that off these constants.

Run:
    tools/cad-venv/bin/python hardware/reference/mq6-gas-sensor/mq6_gas_sensor.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

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


def build():
    """PCB slab with the sensor can on top and a 4-pin header below one short
    edge; the pin tips sit at Z = 0."""
    pcb_z0 = PIN_LEN
    pcb = (
        cq.Workplane("XY")
        .box(PCB_X, PCB_Y, PCB_T, centered=(True, True, False))
        .translate((0, 0, pcb_z0))
    )
    can = (
        cq.Workplane("XY")
        .workplane(offset=pcb_z0 + PCB_T)
        .circle(CAN_D / 2.0)
        .extrude(CAN_H)
    )
    part = pcb.union(can)
    # 4-pin header along the -X edge, pins hanging to Z = 0.
    row_x = -PCB_X / 2.0 + PIN_ROW_INSET
    y0 = -(PIN_COUNT - 1) * PIN_PITCH / 2.0
    for i in range(PIN_COUNT):
        pin = (
            cq.Workplane("XY")
            .box(PIN_SQ, PIN_SQ, PIN_LEN, centered=(True, True, False))
            .translate((row_x, y0 + i * PIN_PITCH, 0))
        )
        part = part.union(pin)
    return part


def main():
    part = build()
    bb = part.val().BoundingBox()
    print("ACEIRMC MQ-6 combustible-gas sensor module")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  PCB {PCB_X}×{PCB_Y}×{PCB_T}; can Ø{CAN_D}×{CAN_H}; {PIN_COUNT}-pin header × {PIN_LEN}")
    out = _here.parent / "mq6-gas-sensor.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
