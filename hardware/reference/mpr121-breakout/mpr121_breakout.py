"""HiLetgo MPR121-Breakout-V12 capacitive touch controller — the appliance's `mpr121`,
the one I²C device that is not on the controller PCBA.

Twelve charge-transfer electrode inputs behind one I²C address (0x5A), on the board's J8
loom. It sits at the manifold beside the cap-sense sleeve, which is what puts it off the
board at all: the sleeve's two foil rings are the electrodes, and the wire between a ring
and this part is inside the measurement. `wiring/ac-wiring-schedule.md` SIG-8 runs the I²C
the distance so the electrodes do not.

External envelope only — the carrier PCB and the two 0.1" male headers the kit ships with:
a 12-pin row for `ELE0`…`ELE11` and a 6-pin row for the bus (`IRQ` / `SCL` / `SDA` /
`3V3` / `GND` / `ADD`). The MPR121QR2 itself is a 3 x 3 x 0.65 QFN and the pull-ups and
the VREG cap are 0603s; all of it is flush SMD and none of it is modeled.

Coordinate frame
----------------
- PCB in the XY plane, components up (+Z), header pins down (-Z); the pin tips sit at
  Z = 0, so the box's floor is the pins and the board rides `PIN_LEN` above it.
- X is the board's 1.2" long axis, which is the axis both header rows run along.
- **-Y is the electrode edge and +Y is the bus edge.** The rows face opposite ways, so
  which way the board is turned decides which of its two conductor bundles is short.

Figures are the SparkFun MPR121 Breakout (SEN-09695) outline this board is a copy of:
1.2" x 0.8" on 0.1" headers.

Run:
    tools/cad-venv/bin/python hardware/reference/mpr121-breakout/mpr121_breakout.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step  # noqa: E402

PCB_X, PCB_Y, PCB_T = 30.48, 20.32, 1.6      # 1.2" x 0.8" FR-4
PIN_LEN = 6.0                                 # header pins below the board
PIN_SQ = 0.64                                 # 0.025" square post
PIN_PITCH = 2.54
ELE_PINS = 12                                 # ELE0…ELE11, on the -Y edge
BUS_PINS = 6                                  # IRQ SCL SDA 3V3 GND ADD, on the +Y edge
ROW_INSET = 2.54                              # header centreline in from its own long edge

I2C_ADDR = 0x5A                               # ADD tied low by the board's own jumper

# --- what those give ------------------------------------------------------
PCB_Z0 = PIN_LEN                              # the board's underside, over the pin tips
ELE_Y = -PCB_Y / 2.0 + ROW_INSET
BUS_Y = PCB_Y / 2.0 - ROW_INSET
ELE_SPAN = (ELE_PINS - 1) * PIN_PITCH         # 27.94 — the 12-pin row nearly fills the edge
BUS_SPAN = (BUS_PINS - 1) * PIN_PITCH


def _row_x(n, i):
    return -(n - 1) * PIN_PITCH / 2.0 + i * PIN_PITCH


def electrode(i: int) -> tuple:
    """One of `ELE0`…`ELE11` as `(the pin's tip, the direction the wire leaves)` in this
    frame. The row is centred on the board's X and stands on the -Y edge."""
    return ((_row_x(ELE_PINS, i), ELE_Y, 0.0), (0.0, 0.0, -1.0))


def electrodes() -> tuple:
    return tuple(electrode(i) for i in range(ELE_PINS))


def bus_pin(i: int) -> tuple:
    """One of the six bus pins, same shape, on the +Y edge — where the J8 loom lands."""
    return ((_row_x(BUS_PINS, i), BUS_Y, 0.0), (0.0, 0.0, -1.0))


def bus() -> tuple:
    """The bus row's own centre, as `(position, the direction the loom leaves)`."""
    return ((0.0, BUS_Y, 0.0), (0.0, 0.0, -1.0))


def electrode_row() -> tuple:
    """The electrode row's own centre, the point an electrode lead is measured from."""
    return ((0.0, ELE_Y, 0.0), (0.0, 0.0, -1.0))


def card_plane() -> tuple:
    """The board's own centre, on its mid-plane. THE BOX'S CENTRE IS NOT IT: the pins reach
    `PIN_LEN` off one face and nothing reaches off the other, so a holder struck on the box
    sits 3 mm behind the card it grips."""
    return ((0.0, 0.0, PCB_Z0 + PCB_T / 2.0), (0.0, 0.0, 1.0))


def build():
    """The PCB slab with both header rows hanging under it, pin tips at Z = 0."""
    part = (cq.Workplane("XY")
            .box(PCB_X, PCB_Y, PCB_T, centered=(True, True, False))
            .translate((0.0, 0.0, PCB_Z0)))
    for n, y in ((ELE_PINS, ELE_Y), (BUS_PINS, BUS_Y)):
        for i in range(n):
            part = part.union(
                cq.Workplane("XY")
                .box(PIN_SQ, PIN_SQ, PIN_LEN, centered=(True, True, False))
                .translate((_row_x(n, i), y, 0.0)))
    return part.val()


def envelope_hold():
    """Read the frame's statements back off the solid: the pin tips on Z = 0, the board on
    its own 1.2 x 0.8, and both rows inside the edges they stand on."""
    bb = build().BoundingBox()
    for what, got, want in (("the pin tips", bb.zmin, 0.0),
                            ("the board's crown", bb.zmax, PCB_Z0 + PCB_T),
                            ("the board across X", bb.xmax - bb.xmin, PCB_X),
                            ("the board across Y", bb.ymax - bb.ymin, PCB_Y)):
        if abs(got - want) > 1e-6:
            raise ValueError(
                f"{what} reads {got:g} against the {want:g} this module declares — the "
                f"envelope has come off the outline it is built from.")
    if ELE_SPAN + PIN_SQ > PCB_X:
        raise ValueError(
            f"the {ELE_PINS}-pin row spans {ELE_SPAN + PIN_SQ:g} on a board {PCB_X:g} "
            f"across — the electrodes have run off the edge they are soldered to.")


def main():
    envelope_hold()
    part = build()
    bb = part.BoundingBox()
    print("HiLetgo MPR121-Breakout-V12 — the off-board cap-sense controller")
    print(f"  X[{bb.xmin:.2f}, {bb.xmax:.2f}]  Y[{bb.ymin:.2f}, {bb.ymax:.2f}]"
          f"  Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  PCB {PCB_X:g} x {PCB_Y:g} x {PCB_T:g} at z {PCB_Z0:g}")
    print(f"  {ELE_PINS}-pin electrode row on -Y at y {ELE_Y:g}, spanning {ELE_SPAN:g}")
    print(f"  {BUS_PINS}-pin bus row on +Y at y {BUS_Y:g}, spanning {BUS_SPAN:g}")
    print(f"  I2C 0x{I2C_ADDR:02X}")
    out = _here.parent / "mpr121-breakout.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
