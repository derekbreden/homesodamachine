"""
Touch-Flo faucet assembly — work-in-progress build-up of the user's
faucet vision on top of the reference valve body.

WHAT THIS IS
============
A growing assembly model that combines the harvested Touch-Flo valve
body (read from `../valve-body-reference/touch-flo-valve-body-reference.step`)
with the parts we are designing around it. The script writes a single
multi-solid STEP file so each iteration can be eyeballed in a viewer.

This is NOT the printed shell. The shell will be a separate file that
wraps around the assembly described here. This file is the body +
tubes + (eventually) other inserts that the shell must accommodate.

PARTS CURRENTLY MODELED
=======================
1. Valve body (loaded from the reference STEP — never modified here).
2. Water dispense tube — Ø 9.5 mm × straight section, inserted into
   the body's water port and extending 40 mm above the plateau.
   O-rings on the actual tube exist but are not modeled (geometry
   only; envelope is the bare 9.5 mm OD).

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path

import cadquery as cq


# ═══════════════════════════════════════════════════════
# REFERENCE BODY GEOMETRY (mirrored from valve-body-reference)
# ═══════════════════════════════════════════════════════
#
# These three constants are duplicated from
# `../valve-body-reference/generate_step_cadquery.py`.
# If they change there, update them here too.
#
PORT_CENTER_X = 8.875        # mm — water port center (X axis)
PORT_CENTER_Y = 0.0          # mm — water port center (Y axis)
PLATEAU_Z     = 39.0         # mm — top face of the rectangular body


# ═══════════════════════════════════════════════════════
# WATER DISPENSE TUBE
# ═══════════════════════════════════════════════════════
#
# A straight Ø 9.5 mm tube that drops into the 9.75 mm water port.
# The 0.25 mm radial gap is taken up by O-rings on the real tube
# (not modeled). The tube extends a comfortable amount into the
# port for retention, and 40 mm above the plateau for visualization.
# Eventually this tube will be bent; for now it is a straight stub.
#
WATER_TUBE_OD            = 9.5    # mm — outer diameter of the tube body
WATER_TUBE_ABOVE_PLATEAU = 40.0   # mm — length above the plateau
WATER_TUBE_INTO_PORT     = 15.0   # mm — length inserted into the port

WATER_TUBE_Z_BOTTOM = PLATEAU_Z - WATER_TUBE_INTO_PORT     # 24.0 mm
WATER_TUBE_Z_TOP    = PLATEAU_Z + WATER_TUBE_ABOVE_PLATEAU # 79.0 mm
WATER_TUBE_LENGTH   = WATER_TUBE_Z_TOP - WATER_TUBE_Z_BOTTOM


# ═══════════════════════════════════════════════════════
# REFERENCE BODY LOADING
# ═══════════════════════════════════════════════════════

REF_BODY_STEP = (
    Path(__file__).resolve().parent.parent
    / "valve-body-reference"
    / "touch-flo-valve-body-reference.step"
)


def load_valve_body() -> cq.Workplane:
    """Load the harvested valve body from the reference STEP file.

    Read-only — this file never modifies the body geometry.
    """
    return cq.importers.importStep(str(REF_BODY_STEP))


# ═══════════════════════════════════════════════════════
# TUBE BUILDERS
# ═══════════════════════════════════════════════════════

def build_water_dispense_tube() -> cq.Workplane:
    """A straight Ø 9.5 mm cylinder sitting in the water port.

    Centered on the port location in X-Y; spans from inside the port
    (Z = WATER_TUBE_Z_BOTTOM) to WATER_TUBE_Z_TOP above the plateau.
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=WATER_TUBE_Z_BOTTOM)
        .center(PORT_CENTER_X, PORT_CENTER_Y)
        .circle(WATER_TUBE_OD / 2.0)
        .extrude(WATER_TUBE_LENGTH)
    )


# ═══════════════════════════════════════════════════════
# ASSEMBLY
# ═══════════════════════════════════════════════════════

def build_assembly() -> cq.Assembly:
    """Combine the reference body and our new parts into one assembly."""
    body = load_valve_body()
    water_tube = build_water_dispense_tube()

    assy = cq.Assembly(name="touch-flo-faucet-assembly")
    assy.add(body, name="valve_body", color=cq.Color("black"))
    assy.add(water_tube, name="water_dispense_tube",
             color=cq.Color(0.85, 0.85, 0.88))   # near-stainless silver
    return assy


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    assy = build_assembly()

    here = Path(__file__).resolve().parent
    out  = here / "touch-flo-faucet-assembly.step"
    # cq.Assembly.save() emits a deprecation warning in this CadQuery
    # version but still produces correct multi-solid STEP. The
    # cq.exporters.export(assy, ...) replacement currently rejects
    # Assembly objects on this install — revisit when the venv is bumped.
    assy.save(str(out))

    print("Touch-Flo faucet assembly")
    print(f"  Reference body:        {REF_BODY_STEP.name}")
    print(f"  Water dispense tube:   Ø{WATER_TUBE_OD} mm "
          f"× {WATER_TUBE_LENGTH:.1f} mm long")
    print(f"                         Z = {WATER_TUBE_Z_BOTTOM:.1f} → {WATER_TUBE_Z_TOP:.1f}")
    print(f"                         {WATER_TUBE_INTO_PORT} mm into port + "
          f"{WATER_TUBE_ABOVE_PLATEAU} mm above plateau")
    print(f"  Center on port:        X = {PORT_CENTER_X} mm, Y = {PORT_CENTER_Y} mm")
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
