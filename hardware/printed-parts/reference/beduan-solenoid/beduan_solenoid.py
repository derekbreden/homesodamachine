"""Reference solid for the Beduan 12V DC normally-closed solenoid valve
(2-way, 1/4" quick-connect — Amazon B07NWCQJK9), the off-the-shelf valve
used 12x per unit on the fluid-topology manifold (see `hardware/bom.md`).

This is a purchased part, not a printed one — the model is a coarse
keep-out envelope for rack/manifold layout, not a manufacturing drawing.
It is built from three primitives positioned to match the caliper-verified
photos in `hardware/off-the-shelf-parts/beduan-solenoid/` (see that
folder's `extracted-results/geometry-description.md`).

Three primitives
----------------
1. White valve body  — box 32.25 (X) x 32.25 (Y) x 30.6 (Z)
2. Solenoid coil     — box 32.25 (X) x 24   (Y) x 26   (Z)
3. Port / flow axis  — cylinder dia 15, length 59, axis along Y

Coordinate convention (matches the geometry-description doc)
------------------------------------------------------------
- X = width   : across the body, perpendicular to flow
- Y = depth   : along the tube-flow axis, port-to-port
- Z = height  : up from the mounting surface, through the coil

Origin is the center of the white-body footprint in X-Y; the mounting
surface (bottom of the white body) sits at Z = 0.

Arrangement (first-pass, photo-matched)
---------------------------------------
- The white body sits on the Z = 0 mounting plane and rises to Z = 30.6.
- The solenoid coil is centered on top of the body in both X and Y, from
  Z = 30.6 to Z = 56.6 — a T-profile, symmetric in X. Stacked heights
  30.6 + 26 = 56.6 mm reproduce the caliper-measured 56.04 mm from
  mounting surface to the far edge of the coil.
- The port cylinder runs along Y through the body, centered in X, 4 mm
  below the body's mid-height. At length 59 it overhangs the 32.25-deep
  body by ~13.4 mm each side as the two quick-connect collet stubs;
  collet-to-collet measured 56.00 mm.

Open assumptions to adjust on the next pass (flagged in the caliper doc
as unmeasured): port-axis height in Z, coil footprint vs. body footprint,
spade-connector terminals (not yet modeled), and which face actually
carries the 2x2 mounting-hole grid.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
from _cadq_export import export_step

# --- White valve body (fluid section) -------------------------------------
body_x = 32.25
body_y = 32.25
body_z = 30.6

# --- Solenoid coil (electrical section), centered on top of the body ------
coil_x = 32.25
coil_y = 24.0
coil_z = 26.0

# --- Port / tube-flow axis (two QC collets + bore), along Y ---------------
port_diameter = 15.0
port_length = 59.0
port_radius = port_diameter / 2.0
# Port axis sits 4 mm below the white body's mid-height. The true height is
# unmeasured (see geometry-description.md "Remaining Unknowns"); this is a
# photo-matched estimate.
port_center_z = body_z / 2.0 - 4.0


def build_beduan_solenoid():
    body = cq.Workplane("XY").box(
        body_x, body_y, body_z, centered=(True, True, False)
    )
    coil = (
        cq.Workplane("XY")
        .workplane(offset=body_z)
        .box(coil_x, coil_y, coil_z, centered=(True, True, False))
    )
    # Cylinder with its base circle centered on the -Y end, extruded +Y so
    # it straddles the body symmetrically: Y in [-29.5, +29.5].
    port = cq.Solid.makeCylinder(
        port_radius,
        port_length,
        cq.Vector(0.0, -port_length / 2.0, port_center_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    return body.union(coil).union(cq.Workplane(obj=port))


def main():
    valve = build_beduan_solenoid()
    export_step(valve, str(_here.parent / "beduan-solenoid.step"))
    print("-> beduan-solenoid.step")


if __name__ == "__main__":
    main()
