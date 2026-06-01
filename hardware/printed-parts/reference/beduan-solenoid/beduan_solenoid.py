"""Reference solid for the Beduan 12V DC normally-closed solenoid valve
(2-way, 1/4" quick-connect, Amazon B07NWCQJK9) — used 12x on the
fluid-topology manifold (see `hardware/bom.md`). Dimensions from
`hardware/off-the-shelf-parts/beduan-solenoid/`.

Components
----------
1. White valve body  — central boss (dia 32.25, Z 6->30.6) + 4 corner
                       bosses (dia 6.8, Z 0->30.6) + square top box
                       (32.25 x 32.25, Z 25.6->30.6)
2. Solenoid coil     — box 32.25 (X) x 24 (Y) x 26 (Z), Z 30.6->56.6
3. Port / flow axis  — cylinder dia 15, length 59 along Y at Z 11.3; the
                       two ends are the quick-connect collets
4. Spade terminals   — two blades 6.3 (X) x 15 (Y) x 0.8 (Z) off the +Y
                       coil face, 10 apart in X at Z 50
5. Flow arrow        — embossed on the central boss's −Z face, pointing +Y
                       toward the spades (one-way flow)

Coordinate convention
---------------------
- X = width  : across the body, perpendicular to flow
- Y = depth  : along the tube-flow axis, port-to-port
- Z = height : up from the mounting surface, through the coil

Origin is the center of the white-body footprint in X-Y; the mounting
surface (bottom of the white body) sits at Z = 0.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
from _cadq_export import export_step

# --- White valve body (fluid section) -------------------------------------
# Five cylinders inscribed in a 32.25 mm square footprint: a central boss
# (dia = the footprint width) raised 6 mm off the mounting surface, plus
# four full-height corner bosses (the 2x2 mounting pattern) tucked tangent
# to the footprint corners.
body_x = 32.25  # square footprint width; also the central-boss diameter
body_y = 32.25
body_z = 30.6
body_center_boss_z_start = 6.0
body_corner_boss_diameter = 6.8
body_top_box_height = 5.0  # square box capping the top, fills the corners

# --- Solenoid coil (electrical section), centered on top of the body ------
coil_x = 32.25
coil_y = 24.0
coil_z = 26.0

# --- Port / tube-flow axis (two QC collets + bore), along Y ---------------
port_diameter = 15.0
port_length = 59.0
port_radius = port_diameter / 2.0
port_center_z = body_z / 2.0 - 4.0

# --- Spade terminals (two flat blades off the coil's +Y face) -------------
# Oriented as protruding blades: 6.3 wide (X), 0.8 thick (Z), 15 long (Y),
# extending +Y straight out of the coil's +Y face (an XZ-plane face). Side
# by side in X, up near the top of the coil where the connector block sits.
spade_width = 6.3       # along X
spade_thickness = 0.8   # along Z
spade_length = 15.0     # along +Y (protrusion)
spade_x_spacing = 10.0  # center-to-center along X
spade_z_center = 50.0   # height on the +Y face
coil_face_y = coil_y / 2.0  # +Y face of the coil, at Y = 12

# --- Flow-direction arrow (embossed on the central boss) ------------------
arrow_emboss = 0.5  # raised height of the arrow off the boss surface


def build_beduan_solenoid():
    # White body: a central boss raised off the mounting surface, plus four
    # full-height corner bosses tucked tangent to the square footprint's
    # corners (centers inset by their radius so they sit inside it).
    body = (
        cq.Workplane("XY")
        .workplane(offset=body_center_boss_z_start)
        .circle(body_x / 2.0)
        .extrude(body_z - body_center_boss_z_start)
    )
    corner_r = body_corner_boss_diameter / 2.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            boss = (
                cq.Workplane("XY")
                .center(sx * (body_x / 2.0 - corner_r), sy * (body_y / 2.0 - corner_r))
                .circle(corner_r)
                .extrude(body_z)
            )
            body = body.union(boss)
    # Square top box: fills the footprint corners for the top 5 mm, just
    # under the coil (Z 25.6 -> 30.6).
    top_box = (
        cq.Workplane("XY")
        .workplane(offset=body_z - body_top_box_height)
        .box(body_x, body_y, body_top_box_height, centered=(True, True, False))
    )
    body = body.union(top_box)
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
    port_cut = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .circle(body_x / 2.0)
        .extrude(body_center_boss_z_start)
    )
    port = cq.Workplane(obj=port)
    port = port.cut(port_cut)
    valve = body.union(coil).union(port)

    for x_center in (-spade_x_spacing / 2.0, spade_x_spacing / 2.0):
        spade = (
            cq.Workplane("XY")
            .box(spade_width, spade_length, spade_thickness, centered=True)
            .translate((x_center, coil_face_y + spade_length / 2.0, spade_z_center))
        )
        valve = valve.union(spade)

    # Flow-direction arrow on the central boss's −Z face, pointing +Y toward
    # the spades — the valve's one-way flow direction.
    arrow_pts = [
        (-1.0, -5.0), (1.0, -5.0), (1.0, 1.0), (2.5, 1.0),
        (0.0, 5.0), (-2.5, 1.0), (-1.0, 1.0),
    ]
    arrow = (
        cq.Workplane("XY")
        .workplane(offset=body_center_boss_z_start - arrow_emboss)
        .polyline(arrow_pts)
        .close()
        .extrude(arrow_emboss + 0.2)
    )
    valve = valve.union(arrow)
    return valve


def main():
    valve = build_beduan_solenoid()
    export_step(valve, str(_here.parent / "beduan-solenoid.step"))
    print("-> beduan-solenoid.step")


if __name__ == "__main__":
    main()
