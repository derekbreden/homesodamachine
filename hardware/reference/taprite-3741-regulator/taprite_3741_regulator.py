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

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('taprite_3741_regulator')
globals().update({name: _reference_values[name] for name in ('FACTORY_SET_PSI', 'RELIEF_PSI', 'CGA320_NUT_FLATS', 'CGA320_THREAD_D', 'CGA320_NUT_LENGTH', 'CGA320_NIPPLE_D', 'PTC_COLLET_D', 'PTC_COLLET_LENGTH', 'PTC_HEX_ACROSS_CORNERS', 'PTC_HEX_LENGTH', 'NPT_D', 'TUBE_D', 'DIAL_D', 'WINDOW_D', 'CASE_D', 'CASE_DEPTH', 'GAUGE_FACE_Y', 'BEZEL_PROUD', 'OUTLET_REACH', 'TANK_REACH', 'GAUGE_STEM_D', 'GAUGE_BLOCK_W', 'GAUGE_BLOCK_LENGTH', 'BODY_D', 'BODY_BACK_Y', 'BODY_FRONT_Y', 'PORT_BOSS_D', 'PORT_FACE_R', 'FLANGE_D', 'FLANGE_FRONT_Y', 'FLANGE_EDGE_R', 'NECK_FLATS', 'NECK_FRONT_Y', 'NOSE_D', 'NOSE_FRONT_Y', 'NOSE_CHAMFER', 'JAM_NUT_FLATS', 'JAM_NUT_FRONT_Y', 'SCREW_D', 'SCREW_TIP_Y', 'SLOT_W', 'SLOT_DEPTH', 'INLET_AXIS', 'TANK_AXIS', 'INLET_NIPPLE_D', 'INLET_NUT_NEAR', 'INLET_NUT_FACE', 'INLET_NIPPLE_END', 'OUTLET_THREAD_Z', 'OUTLET_HEX_Z', 'OUTLET_MOUTH_Z', 'BLOWOFF_BEARING_DEG', 'BLOWOFF_ROOT_R', 'BLOWOFF_BODY_D', 'BLOWOFF_BODY_R', 'BLOWOFF_CAP_D', 'BLOWOFF_CAP_R', 'BLOWOFF_VENT_D', 'DIAL_ZERO_DEG', 'DIAL_SWEEP_DEG', 'TANK_FULL_PSI', 'OUTLET_FULL_PSI', 'OUTLET_DIAL', 'OUTER_NUMERAL_R', 'OUTER_TICK_OUT_R', 'OUTER_TICK_MAJOR_R', 'OUTER_TICK_MINOR_R', 'INNER_ARC_R', 'INNER_TICK_MAJOR_R', 'INNER_TICK_MINOR_R', 'INNER_NUMERAL_R', 'UNIT_UPPER_R', 'UNIT_LOWER_R', 'STAMP_R', 'NUMERAL_SIZE', 'STAMP_SIZE', 'UNIT_SIZE', 'MAJOR_TICK_W', 'MINOR_TICK_W', 'PRINT_T', 'BAND_T', 'NEEDLE_R', 'NEEDLE_TAIL_R', 'NEEDLE_W', 'HUB_DIAL_D', 'BAND_NEAR_R', 'BAND_FAR_R')})


# --- the standards ----------------------------------------------------------
# CGA-320 is the connection every USA CO2 beverage cylinder presents: a 0.825"-14 NGO-RH male
# thread on the valve, and a female nut on the regulator that pulls a nipple down onto the
# valve's own face with a nylon washer between them. The nut takes a 1-1/8" wrench.

# The outlet push-fit: John Guest PI010822S, gray acetal, at the repository's nominal 1/4"
# male-connector envelope (`reference/jg-pp010822e`). Its NPT shank is inside the body's port.

# --- the gauges ----------------------------------------------------------------
# Both are 2" dials in a knurled 2-1/4" bezel, face toward the customer.

# --- the body ---------------------------------------------------------------

# The black zinc bonnet: the diaphragm flange, a hex neck, and the round nose the adjusting
# screw runs out of.
# The adjustment: a 3/8" slotted screw under a jam nut, locked at the factory.



# The safety blow-off, on the body's upper right: Taprite's own fitting, its vent holes in its
# end face. It is not a pull-ring valve and nothing in the guides asks the customer to touch it.

# --- what each dial says ----------------------------------------------------
# A dial's scale runs 270° clockwise from its zero at the lower left. Each dial carries psi on its
# outer ring in black and bar on its inner ring in red.
# The contents dial's bands, in psi: red at the empty end, green where a cylinder still holding
# liquid CO2 reads (its vapour pressure, about 850 psi at room temperature). Placed off
# Taprite's drawing and the product photograph; the received part fixes them.


def _ring_spec(full, major, minor, labels):
    'One printed scale: its full-scale value, its tick steps and the values it letters.'
    return _reference_data('taprite_3741_regulator', '_ring_spec', (full, major, minor, labels), {})



# Where each ring sits on the face of a 2" dial.

# A dial faces +Y and is read from +Y, so its own right hand is world −X. This is the plane every
# mark on it is drawn on: the mark's `(u, v)` are its right and its up as the customer sees them.


# --- the stations the rest of the world reaches ------------------------------

def inlet():
    "The CGA-320 nut's outer face, and the axis it runs onto the cylinder valve along:\n    `(position, outward axis)`. The nipple inside it seats on the valve's own face with the\n    supplied nylon washer between."
    return _reference_data('taprite_3741_regulator', 'inlet', (), {})


def outlet():
    "The PI010822S's push-fit mouth, where the red tether goes in: `(position, outward\n    axis)`."
    return _reference_data('taprite_3741_regulator', 'outlet', (), {})


def adjustment():
    'The slotted adjusting screw\'s tip and the axis it turns about — set and locked at the\n    factory, and what a picture points at to say "leave this alone".'
    return _reference_data('taprite_3741_regulator', 'adjustment', (), {})


def relief():
    "The safety blow-off's vented end face."
    return _reference_data('taprite_3741_regulator', 'relief', (), {})


def tank_dial():
    "The cylinder-contents dial's centre and the direction it is read from."
    return _reference_data('taprite_3741_regulator', 'tank_dial', (), {})


def outlet_dial():
    "The outlet-pressure dial's centre and the direction it is read from."
    return _reference_data('taprite_3741_regulator', 'outlet_dial', (), {})


def stations():
    'Everything a picture or a neighbour points at, under the name it is pointed at by.'
    return _reference_data('taprite_3741_regulator', 'stations', (), {})


# --- the solid ---------------------------------------------------------------


# --- a dial ------------------------------------------------------------------

def _bearing(r: float, as_axis: bool=False):
    "A point on the blow-off's axis at radius `r`, in the XZ plane."
    return _reference_data('taprite_3741_regulator', '_bearing', (r, as_axis), {})


def _scale_deg(value: float, full: float):
    "Where a reading stands on the face, in degrees CCW from the customer's own right."
    return _reference_data('taprite_3741_regulator', '_scale_deg', (value, full), {})


def _at(r: float, deg: float):
    "A point on the face at `(radius, angle)`, in the dial plane's own `(u, v)`."
    return _reference_data('taprite_3741_regulator', '_at', (r, deg), {})


def _steps(step: float, full: float):
    'Every reading a tick stands at, zero and full scale included.'
    return _reference_data('taprite_3741_regulator', '_steps', (step, full), {})


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
