"""BOJACK SF76E SEFUSE thermal cutoff — the appliance's `thermal-fuse`, the
hardware-only backstop in series with the compressor's AC hot leg.

An axial one-shot cutoff: a metal case with a lead out of each end, open for good
once its own case reaches 77 °C. Nothing reads it, nothing switches it and nothing
resets it, and what it opens on is the temperature of that case. It lies along the
compressor's power box — the flank of the donor's moulded cover over the terminal
block and the PTC start relay — on the station `compressor.power_face` states, laid
there by `enclosure_assembly.build_thermal_fuse`.

Geometry is the SEFUSE **SF/E series** outline (NEC/SCHOTT), the series the SF76E
belongs to: case Ø4.2 × 11, leads Ø1, one 20 mm and one 35 mm, 66 mm end to end.
The case is drawn as a plain cylinder; the real one tapers into each lead, so this
is the loose envelope rather than the silhouette.

**Only the leads' first 3 mm are modeled.** The datasheet forbids a bend closer
than 3 mm to the body, so that stub is the length of lead whose pose the part
fixes; past it the lead is wire and goes where the loom goes.

Coordinate frame
----------------
- X = the fuse's own axis, lead to lead, origin at the case's mid-length.
- Z = 0 is the SEATING PLANE — the generatrix the case lies on, so whatever
  holds it down reads its own surface as this plane. The axis runs one case
  radius above it and the leads run on the axis, so a lead stands 1.6 mm clear
  of the seat and nothing but the case touches it.
- Y is centred on the axis.

Ratings, from the SF/E standard-rating table: functioning temperature T_F 77 °C,
holding temperature T_H 62 °C, maximum temperature limit T_M 150 °C, 10 A at
250 V AC.

Run:
    tools/cad-venv/bin/python hardware/reference/sf76e-thermal-fuse/sf76e_thermal_fuse.py


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'sf76e-thermal-fuse.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'sf76e-thermal-fuse.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'sf76e-thermal-fuse.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

# --- SF/E series outline (datasheet, mm) ----------------------------------
BODY_D = 4.2           # case diameter, ±0.2
BODY_L = 11.0          # case length, ±0.5
LEAD_D = 1.0           # lead wire, ±0.1
LEAD_STUB = 3.0        # the datasheet's minimum straight before a bend is allowed
# Stated, not modeled: the two leads are this long and the part measures this end
# to end. Whoever cuts the harness needs the figures; the solid does not carry them.
LEAD_SHORT = 20.0
LEAD_LONG = 35.0
OVERALL_L = 66.0

# --- SF/E standard rating -------------------------------------------------
TF_C = 77              # rated functioning temperature — where it opens for good
TH_C = 62              # holding temperature — indefinitely safe below this
TM_C = 150             # maximum temperature limit
RATED_A = 10
RATED_V = 250

# --- what those give ------------------------------------------------------
LENGTH = BODY_L + 2.0 * LEAD_STUB      # the modeled body's own X extent
AXIS_Z = BODY_D / 2.0                  # the axis, one radius off the seating plane
# The air under a lead. A Ø1 wire on the axis of a Ø4.2 case cannot reach the
# surface the case lies on, so the case is the whole of the thermal contact.
LEAD_STANDOFF = AXIS_Z - LEAD_D / 2.0


def build():
    """The case lying on Z = 0 with a lead stub off each end, all on one axis."""
    import cadquery as cq
    case = cq.Solid.makeCylinder(
        BODY_D / 2.0, BODY_L,
        cq.Vector(-BODY_L / 2.0, 0.0, AXIS_Z), cq.Vector(1, 0, 0))
    part = cq.Workplane(obj=case)
    for sx in (-1.0, 1.0):
        lead = cq.Solid.makeCylinder(
            LEAD_D / 2.0, LEAD_STUB,
            cq.Vector(sx * BODY_L / 2.0, 0.0, AXIS_Z), cq.Vector(sx, 0, 0))
        part = part.union(cq.Workplane(obj=lead))
    return part.val()


def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__ == "__main__":
    main()


def __getattr__(name):
    if name == 'cq':
        import cadquery as cq
        return cq
    if name in {'export_assembly'}:
        import _cadq_export
        return getattr(_cadq_export, name)
    if name in {'M_TINNED_STEEL', 'one_body'}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
