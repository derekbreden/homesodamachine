"""Reference solid for the Beduan 12V DC normally-closed solenoid valve
(2-way, 1/4" quick-connect — Amazon B07NWCQJK9), the off-the-shelf valve
used 12x per unit on the fluid-topology manifold (see `hardware/bom.md`).

This is a purchased part, not a printed one — the model is a coarse
keep-out envelope for rack/manifold layout, not a manufacturing drawing.
It is built from four primitives positioned to match the caliper-verified
photos in `hardware/off-the-shelf-parts/beduan-solenoid/` (see that
folder's `extracted-results/geometry-description.md`).

Four primitives
---------------
1. White valve body  — box 32.25 (X) x 32.25 (Y) x 30.6 (Z)
2. Solenoid coil     — box 32.25 (X) x 24   (Y) x 26   (Z)
3. Port / flow axis  — cylinder dia 15, length 59, axis along Y
4. Spade terminals   — two blades 6.3 (X) x 15 (Y) x 0.8 (Z), off +Y face

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
- Two spade terminals extend +Y straight out of the coil's +Y face (an
  XZ-plane face at Y = 12), reaching Y = 27 — thin coplanar blades, side
  by side 10 mm apart in X, up at Z = 50 near the connector block seen in
  the photos.

Open assumptions to adjust on the next pass (flagged in the caliper doc
as unmeasured): port-axis height in Z, coil footprint vs. body footprint,
spade-terminal placement on the coil's +Y face (modeled here, but the
height and the 31.41 mm protrusion are first-pass), and which face
actually carries the 2x2 mounting-hole grid.
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

# --- Spade terminals (two flat blades off the coil's +Y face) -------------
# Oriented as protruding blades: 6.3 wide (X), 0.8 thick (Z), 15 long (Y),
# extending +Y straight out of the coil's +Y face (an XZ-plane face). Side
# by side in X, up near the top of the coil where the connector block sits.
# Placement is a first-pass estimate (see geometry-description.md).
spade_width = 6.3       # along X
spade_thickness = 0.8   # along Z
spade_length = 15.0     # along +Y (protrusion)
spade_x_spacing = 10.0  # center-to-center along X
spade_z_center = 50.0   # height on the +Y face
coil_face_y = coil_y / 2.0  # +Y face of the coil, at Y = 12


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
    valve = body.union(coil).union(cq.Workplane(obj=port))

    for x_center in (-spade_x_spacing / 2.0, spade_x_spacing / 2.0):
        spade = (
            cq.Workplane("XY")
            .box(spade_width, spade_length, spade_thickness, centered=True)
            .translate((x_center, coil_face_y + spade_length / 2.0, spade_z_center))
        )
        valve = valve.union(spade)
    return valve


def main():
    valve = build_beduan_solenoid()
    export_step(valve, str(_here.parent / "beduan-solenoid.step"))
    print("-> beduan-solenoid.step")


if __name__ == "__main__":
    main()
