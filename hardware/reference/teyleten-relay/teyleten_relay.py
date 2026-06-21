"""Reference solid for the Teyleten 3.3 V opto-isolated 1-channel relay module
(Amazon B07XGZSYJV), used 2x on the power/controller trays — relay #1 switches
the compressor's 120 VAC hot leg, relay #2 gates 12 V to the diaphragm pump.

A generic reseller board with no controlled drawing; geometry is calipered:
a long narrow PCB with the SRD relay can + a 3-pole COM/NO/NC screw block on one
short end and a VCC/GND/IN 3-pin header on the other, header/relay pins poking
~2 mm below the board.

Coordinate frame
----------------
- X = length (70 mm), Y = width (17 mm), Z = height up from the PCB underside.
- Origin at the board-footprint center; Z = 0 the PCB bottom = the standoff
  (mounting) plane. Pins protrude to Z = -2; the relay can tops out near Z = 17.
- Screw block on the +X end, logic header on the -X end.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

# --- Calipered geometry ---------------------------------------------------
length = 70.0          # X
width = 17.0           # Y
pcb_t = 1.5            # PCB thickness
envelope_z = 19.0      # pin tips to relay-can top
pin_drop = 2.0         # pins below the PCB underside
hole_dia = 3.2         # M3 clearance (diameter not calipered; assumed)
hole_dx = 66.0 / 2.0   # +/-33 along length
hole_dy = 13.0 / 2.0   # +/-6.5 across width


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))

    # SRD relay can, dominant component, near center.
    relay = (
        cq.Workplane("XY")
        .box(19.0, 15.6, envelope_z - pin_drop - pcb_t, centered=(True, True, False))
        .translate((-2.0, 0.0, pcb_t))
    )
    # 3-pole COM/NO/NC screw block on the +X end.
    screw_blk = (
        cq.Workplane("XY")
        .box(11.0, 15.0, 10.0, centered=(True, True, False))
        .translate((length / 2.0 - 6.0, 0.0, pcb_t))
    )
    # VCC/GND/IN 3-pin header on the -X end.
    header = (
        cq.Workplane("XY")
        .box(8.0, 3.0, 8.5, centered=(True, True, False))
        .translate((-(length / 2.0 - 5.0), 0.0, pcb_t))
    )
    # Representative pin protrusion below the board (clearance the tray must give).
    pins = (
        cq.Workplane("XY")
        .box(length - 12.0, width - 4.0, pin_drop, centered=(True, True, False))
        .translate((0.0, 0.0, -pin_drop))
    )

    part = pcb.union(relay).union(screw_blk).union(header).union(pins)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            part = part.cut(
                cq.Workplane("XY")
                .workplane(offset=-pin_drop)
                .center(sx * hole_dx, sy * hole_dy)
                .circle(hole_dia / 2.0)
                .extrude(pin_drop + pcb_t)
            )
    return part


def main():
    export_step(build(), str(_here.parent / "teyleten-relay.step"))
    print("-> teyleten-relay.step")


if __name__ == "__main__":
    main()
