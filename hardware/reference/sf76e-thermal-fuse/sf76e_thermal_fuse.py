"""BOJACK SF76E SEFUSE thermal cutoff — the appliance's `thermal-fuse`, the
hardware-only backstop in series with the compressor's AC hot leg.

An axial one-shot cutoff: a metal case with a lead out of each end, open for good
once its own case reaches 77 °C. Nothing reads it, nothing switches it and nothing
resets it, and what it opens on is the temperature of that case. It lies along the
compressor's power box — the outside of the donor's moulded cover over the terminal
block and the PTC start relay — on the station `compressor.power_face` states, laid
there by `enclosure_assembly.build_thermal_fuse`.

Geometry is the SEFUSE **SF/E series** outline (NEC/SCHOTT), the series the SF76E
belongs to: case Ø4.2 × 11, leads Ø1, one 20 mm and one 35 mm, 66 mm end to end.
The case is drawn as a plain cylinder; the real one tapers into each lead, so this
is the loose envelope rather than the silhouette.

**Only the leads' first 3 mm are modeled.** The datasheet forbids a bend closer
than 3 mm to the body, so that stub is the length of lead whose pose the part
fixes; past it the lead is wire and goes where the loom goes. `ground-ring-stack`
draws its tongues and omits the cable the same way.

Coordinate frame
----------------
- X = the fuse's own axis, lead to lead, origin at the case's mid-length.
- Z = 0 is the SEATING PLANE — the generatrix the case lies on, so whatever
  straps it down reads its own surface as this plane. The axis runs one case
  radius above it and the leads run on the axis, so a lead stands 1.6 mm clear
  of the seat and nothing but the case touches it.
- Y is centred on the axis.

Ratings, from the SF/E standard-rating table: functioning temperature T_F 77 °C,
holding temperature T_H 62 °C, maximum temperature limit T_M 150 °C, 10 A at
250 V AC.

Run:
    tools/cad-venv/bin/python hardware/reference/sf76e-thermal-fuse/sf76e_thermal_fuse.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step  # noqa: E402

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


def envelope_hold():
    """Read the three statements back off the solid: the axis lies along X, the case
    sits ON the seating plane rather than through it or above it, and the leads add
    exactly the two stubs the bend rule reserves."""
    bb = build().BoundingBox()
    for ax, got, want in (("x", bb.xmax - bb.xmin, LENGTH),
                          ("y", bb.ymax - bb.ymin, BODY_D),
                          ("z", bb.zmax - bb.zmin, BODY_D)):
        if abs(got - want) > 1e-6:
            raise ValueError(
                f"the fuse measures {got:g} across {ax} against the {want:g} its case and "
                f"lead stubs come to — the envelope this module draws is no longer the one "
                f"it declares.")
    if abs(bb.zmin) > 1e-6:
        raise ValueError(
            f"the case's contact line stands at z = {bb.zmin:g} — Z = 0 is the seating "
            f"plane, and a cutoff off the face it senses is a cutoff reading cabinet air.")


def main():
    envelope_hold()
    part = build()
    bb = part.BoundingBox()
    print("BOJACK SF76E SEFUSE thermal cutoff — SEFUSE SF/E series outline")
    print(f"  X[{bb.xmin:.2f}, {bb.xmax:.2f}]  Y[{bb.ymin:.2f}, {bb.ymax:.2f}]"
          f"  Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  case  Ø{BODY_D:g} x {BODY_L:g}, lying on the seating plane, "
          f"axis at z {AXIS_Z:g}")
    print(f"  leads Ø{LEAD_D:g}, {LEAD_STUB:g} of straight modeled each end "
          f"({LEAD_STANDOFF:g} clear of the seat); {LEAD_SHORT:g} + {LEAD_LONG:g} "
          f"in the part, {OVERALL_L:g} end to end")
    print(f"  opens at {TF_C:g} °C, holds below {TH_C:g} °C, "
          f"{RATED_A:g} A / {RATED_V:g} V AC")
    out = _here.parent / "sf76e-thermal-fuse.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
