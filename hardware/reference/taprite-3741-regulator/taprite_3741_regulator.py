"""Taprite 3741 CGA-320 CO2 regulator — the primary regulator that ships with the appliance,
set at the factory to 75 psi.

It stands on the customer's own CO2 cylinder and is the only thing on this machine the customer
threads onto anything. Its CGA-320 nut pulls down on the cylinder valve. Its outlet is the gray
acetal PI010822S the factory threads into the body's 1/4" NPT port in place of Taprite's flare
fitting, and the red 1/4" tether to the CO2 bulkhead on the +Y wall of back-top is pushed into
that at the factory too (`ledger/bom.md` §4). Regulator and tether ship as one piece.

THE CUSTOMER SETS NOTHING ON IT. The pressure adjustment is a slotted screw out the front of the
black bonnet, under a jam nut: acceptance step 1 turns it to `FACTORY_SET_PSI` on the regulator's
own upper gauge, locks the nut and paint-marks the pair, and it ships at that setting. There is
no knob and no outlet shutoff; the cylinder valve opens and closes the gas.

Two dials, which do not read the same thing: the +X dial reads the cylinder, 0–2000 psi, with a
green band where a cylinder with liquid CO2 in it reads and a red band at the empty end; the +Z
dial reads what goes out to the appliance, 0–160 psi. Both are drawn with their scales and their
needles at rest on zero, which is the state the part ships in.

Where the figures come from
---------------------------
Taprite's own sales drawing (3741_SALES rev C, drawn 1:2: 7" wide, 6" tall, 4.3" deep) and its
parts breakdown (3741 REGULATOR ASSEMBLY rev C, 10-2010), read at 150 px to the real inch. What is
standardised is taken at its standard — the CGA-320 nut's 1-1/8" hex and 0.825"-14 thread, the
PI010822S's nominal 1/4" push-fit envelope. `README.md` says which figure is which.

Coordinate frame
----------------
The frame the regulator hangs in once it is on the cylinder:

- **+Y** out of the body's face toward the customer — the bonnet and its adjusting screw.
- **+Z** up — the outlet-pressure dial. **−Z** down — the outlet and its gray push-fit.
- **−X** the inlet axis, out toward the cylinder — the CGA-320 nut.
- **+X** the cylinder-contents dial.

Origin where the bonnet's axis crosses the inlet and outlet axes. Standing in front of it, the
customer sees the cylinder on their right, the contents dial on their left, the outlet dial above,
the outlet below and the safety blow-off on the upper right of the body.

Run:
    tools/cad-venv/bin/python hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

STEP = _here.parent / "taprite-3741-regulator.step"

# --- the setting it ships at ---------------------------------------------------
FACTORY_SET_PSI = 75.0           # acceptance step 1; the in-machine WR1105 holds 3 bar below it
RELIEF_PSI = 130.0               # the safety blow-off, 130 ± 4 psi on Taprite's drawing

# --- the standards ----------------------------------------------------------
# CGA-320 is the connection every USA CO2 beverage cylinder presents: a 0.825"-14 NGO-RH male
# thread on the valve, and a female nut on the regulator that pulls a nipple down onto the
# valve's own face with a nylon washer between them. The nut takes a 1-1/8" wrench.
CGA320_NUT_FLATS = 25.4 * 1.125
CGA320_THREAD_D = 25.4 * 0.825
CGA320_NUT_LENGTH = 25.4
CGA320_NIPPLE_D = 15.9          # the nose that seats on the cylinder valve, inside the nut

# The outlet push-fit: John Guest PI010822S, gray acetal, at the repository's nominal 1/4"
# male-connector envelope (`reference/jg-pp010822e`). Its NPT shank is inside the body's port.
PTC_COLLET_D = 14.0
PTC_COLLET_LENGTH = 13.5
PTC_HEX_ACROSS_CORNERS = 16.5
PTC_HEX_LENGTH = 5.0
NPT_D = 13.7                     # 1/4" NPT major, for the turn of thread left showing
TUBE_D = 6.35                    # the red 1/4" tether it takes

# --- the gauges ----------------------------------------------------------------
# Both are 2" dials in a knurled 2-1/4" bezel, face toward the customer.
DIAL_D = 51.0                    # the printed disc, its rim under the bezel
WINDOW_D = 48.5                  # what the bezel leaves of it
CASE_D = 58.5
CASE_DEPTH = 28.0
GAUGE_FACE_Y = 14.0              # where the dial's own front plane stands
BEZEL_PROUD = 3.0                # how far the bezel stands over the dial
OUTLET_REACH = 67.0              # body centre to the outlet dial's centre, up
TANK_REACH = 65.0                # body centre to the contents dial's centre, out +X
GAUGE_STEM_D = 13.7              # each gauge's 1/4" NPT stem where it leaves the body
GAUGE_BLOCK_W = 14.0             # the wrench block under each case
GAUGE_BLOCK_LENGTH = 9.0

# --- the body ---------------------------------------------------------------
BODY_D = 44.0                    # the brass body behind the bonnet
BODY_BACK_Y = -11.0
BODY_FRONT_Y = 13.5
PORT_BOSS_D = 18.0               # each port's boss, standing to `PORT_FACE_R`
PORT_FACE_R = 23.0

# The black zinc bonnet: the diaphragm flange, a hex neck, and the round nose the adjusting
# screw runs out of.
FLANGE_D = 50.0
FLANGE_FRONT_Y = 25.4
FLANGE_EDGE_R = 2.0
NECK_FLATS = 31.0
NECK_FRONT_Y = 39.0
NOSE_D = 29.0
NOSE_FRONT_Y = 62.3
NOSE_CHAMFER = 2.0
# The adjustment: a 3/8" slotted screw under a jam nut, locked at the factory.
JAM_NUT_FLATS = 25.4 * 0.5
JAM_NUT_FRONT_Y = 70.0
SCREW_D = 25.4 * 0.375
SCREW_TIP_Y = 92.3
SLOT_W = 1.6
SLOT_DEPTH = 3.0

INLET_AXIS = (-1.0, 0.0, 0.0)    # out toward the cylinder, on the customer's right
TANK_AXIS = (1.0, 0.0, 0.0)      # the contents dial, on the customer's left
INLET_NIPPLE_D = 14.0
INLET_NUT_NEAR = 60.0            # the nut's inboard face, run up onto the valve
INLET_NUT_FACE = INLET_NUT_NEAR + CGA320_NUT_LENGTH
INLET_NIPPLE_END = INLET_NUT_FACE - 9.0   # the nose, inside the nut, on the valve's face

OUTLET_THREAD_Z = -PORT_FACE_R - 1.0      # the turn of NPT left showing below the port face
OUTLET_HEX_Z = OUTLET_THREAD_Z - PTC_HEX_LENGTH
OUTLET_MOUTH_Z = OUTLET_HEX_Z - PTC_COLLET_LENGTH

# The safety blow-off, on the body's upper right: Taprite's own fitting, its vent holes in its
# end face. It is not a pull-ring valve and nothing in the guides asks the customer to touch it.
BLOWOFF_BEARING_DEG = 135.0      # in the XZ plane, CCW from +X: up and out toward the inlet
BLOWOFF_ROOT_R = 18.0
BLOWOFF_BODY_D = 11.0
BLOWOFF_BODY_R = 30.0
BLOWOFF_CAP_D = 13.0
BLOWOFF_CAP_R = 37.0
BLOWOFF_VENT_D = 1.6

# --- what each dial says ----------------------------------------------------
# A dial's scale runs 270° clockwise from its zero at the lower left. Each dial carries psi on its
# outer ring in black and bar on its inner ring in red.
DIAL_ZERO_DEG = 225.0
DIAL_SWEEP_DEG = 270.0
TANK_FULL_PSI = 2000.0
OUTLET_FULL_PSI = 160.0
# The contents dial's bands, in psi: red at the empty end, green where a cylinder still holding
# liquid CO2 reads (its vapour pressure, about 850 psi at room temperature). Placed off
# Taprite's drawing and the product photograph; the received part fixes them.


def _ring_spec(full, major, minor, labels):
    """One printed scale: its full-scale value, its tick steps and the values it letters."""
    return {"full": full, "major": major, "minor": minor, "labels": labels}


OUTLET_DIAL = {
    "outer": _ring_spec(OUTLET_FULL_PSI, 20.0, 5.0, (20, 40, 60, 80, 100, 120, 140, 160)),
    "inner": _ring_spec(OUTLET_FULL_PSI / 14.5038, 2.0, 1.0, (2, 4, 6, 8, 10)),
    "units": ("psi", "bar"),
    "stamp": "TAPRITE",
    "bands": (),
}

# Where each ring sits on the face of a 2" dial.
OUTER_NUMERAL_R = 20.6
OUTER_TICK_OUT_R = 23.6
OUTER_TICK_MAJOR_R = 20.0 + 2.2
OUTER_TICK_MINOR_R = 22.4
INNER_ARC_R = 14.6
INNER_TICK_MAJOR_R = 12.2
INNER_TICK_MINOR_R = 13.3
INNER_NUMERAL_R = 10.3
UNIT_UPPER_R = 6.9
UNIT_LOWER_R = 10.2
STAMP_R = 5.2
NUMERAL_SIZE = 3.0
STAMP_SIZE = 2.4
UNIT_SIZE = 2.8
MAJOR_TICK_W = 0.8
MINOR_TICK_W = 0.45
PRINT_T = 0.6
BAND_T = 0.25                    # the bands go down first and the scale is printed over them
NEEDLE_R = 19.0
NEEDLE_TAIL_R = 4.6
NEEDLE_W = 1.3
HUB_DIAL_D = 4.6
BAND_NEAR_R = 16.0
BAND_FAR_R = 23.6

# A dial faces +Y and is read from +Y, so its own right hand is world −X. This is the plane every
# mark on it is drawn on: the mark's `(u, v)` are its right and its up as the customer sees them.


# --- the stations the rest of the world reaches ------------------------------

def inlet() -> tuple:
    """The CGA-320 nut's outer face, and the axis it runs onto the cylinder valve along:
    `(position, outward axis)`. The nipple inside it seats on the valve's own face with the
    supplied nylon washer between."""
    return (-INLET_NUT_FACE, 0.0, 0.0), INLET_AXIS


def outlet() -> tuple:
    """The PI010822S's push-fit mouth, where the red tether goes in: `(position, outward
    axis)`."""
    return (0.0, 0.0, OUTLET_MOUTH_Z), (0.0, 0.0, -1.0)


def adjustment() -> tuple:
    """The slotted adjusting screw's tip and the axis it turns about — set and locked at the
    factory, and what a picture points at to say "leave this alone"."""
    return (0.0, SCREW_TIP_Y, 0.0), (0.0, 1.0, 0.0)


def relief() -> tuple:
    """The safety blow-off's vented end face."""
    x, z = _bearing(BLOWOFF_CAP_R)
    return (x, 0.0, z), _bearing(1.0, as_axis=True)


def tank_dial() -> tuple:
    """The cylinder-contents dial's centre and the direction it is read from."""
    return (TANK_REACH, GAUGE_FACE_Y, 0.0), (0.0, 1.0, 0.0)


def outlet_dial() -> tuple:
    """The outlet-pressure dial's centre and the direction it is read from."""
    return (0.0, GAUGE_FACE_Y, OUTLET_REACH), (0.0, 1.0, 0.0)


def stations() -> dict:
    """Everything a picture or a neighbour points at, under the name it is pointed at by."""
    return {"inlet": inlet(), "outlet": outlet(), "adjustment": adjustment(),
            "relief": relief(), "tank-dial": tank_dial(), "outlet-dial": outlet_dial()}


# --- the solid ---------------------------------------------------------------


# --- a dial ------------------------------------------------------------------

def _bearing(r: float, as_axis: bool = False):
    """A point on the blow-off's axis at radius `r`, in the XZ plane."""
    a = math.radians(BLOWOFF_BEARING_DEG)
    x, z = r * math.cos(a), r * math.sin(a)
    return (x, 0.0, z) if as_axis else (x, z)


def _scale_deg(value: float, full: float) -> float:
    """Where a reading stands on the face, in degrees CCW from the customer's own right."""
    return DIAL_ZERO_DEG - DIAL_SWEEP_DEG * value / full


def _at(r: float, deg: float) -> tuple:
    """A point on the face at `(radius, angle)`, in the dial plane's own `(u, v)`."""
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))


def _steps(step: float, full: float):
    """Every reading a tick stands at, zero and full scale included."""
    n = int(math.floor(full / step + 1e-9))
    return [i * step for i in range(n + 1)]


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'taprite-3741-regulator.step'
PAYLOAD_PATH = _FROZEN_DIR / 'taprite-3741-regulator.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('taprite-3741-regulator frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
