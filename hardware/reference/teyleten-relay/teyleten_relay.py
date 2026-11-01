"""Reference solid for the Teyleten 3.3 V opto-isolated 1-channel relay module
(Amazon B07XGZSYJV), used twice on back-top's dry west wall — relay #1 switches
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

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
STEP_PATH = _HERE / "teyleten-relay.step"
PAYLOAD_PATH = _HERE / "teyleten-relay.step.mesh"
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"

# --- Calipered geometry ---------------------------------------------------
length = 70.0          # X
width = 17.0           # Y
pcb_t = 1.5            # PCB thickness
envelope_z = 19.0      # pin tips to relay-can top
pin_drop = 2.0         # pins below the PCB underside
hole_dia = 3.2         # M3 clearance (diameter not calipered; assumed)
hole_dx = 66.0 / 2.0   # +/-33 along length
hole_dy = 13.0 / 2.0   # +/-6.5 across width

# For the shared module-tray engine.
name = "relay"
holes = [(sx * hole_dx, sy * hole_dy) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]

# The two terminal groups, inboard of the corner holes at either end of the board: the
# COM/NO/NC screw block on +X, the VCC/GND/IN header on −X. Both are entered from ABOVE, and
# `land_z` is the one height a wire comes down to — the taller screw block's own top, which the
# shorter header is served at as well.
screw_blk_inset, screw_blk_h = 10.0, 10.0
header_inset, header_h = 9.0, 8.5
land_z = pcb_t + screw_blk_h


def contacts():
    """The COM/NO/NC screw block: `(position, outward axis)` in the relay's own frame."""
    return ((length / 2.0 - screw_blk_inset, 0.0, land_z), (0.0, 0.0, 1.0))


def logic():
    """The VCC/GND/IN header, at the same landing plane."""
    return ((-(length / 2.0 - header_inset), 0.0, land_z), (0.0, 0.0, 1.0))


def main():
    print("Teyleten 3.3 V opto-isolated relay module")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
