"""Reference solid for the Beduan 12V DC normally-closed solenoid valve
(2-way, 1/4" quick-connect, Amazon B07NWCQJK9) — used 12x on the
fluid-topology manifold (see `hardware/bom.md`). Dimensions from
`hardware/off-the-shelf-parts/beduan-solenoid/`.

A white valve body (central boss + four corner posts + a square top box),
a solenoid coil stacked on top, a port running through on the flow axis,
two spade terminals, and a flow-direction arrow on the boss underside.

Coordinate frame
----------------
- X = width  : across the body, perpendicular to flow
- Y = depth  : along the tube-flow axis, port-to-port; +Y is the outlet,
               toward the spades, the direction the flow arrow points
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

# --- White valve body -----------------------------------------------------
body_width = 32.25                  # footprint width; also the central-boss diameter
body_radius = body_width / 2.0
corner_boss_radius = 6.8 / 2.0
top_box_height = 5.0

body_top_z = 30.6
boss_z_range = (6.0, body_top_z)              # central boss; corner posts run full-height below it
corner_boss_z_range = (0.0, body_top_z)
top_box_z_range = (body_top_z - top_box_height, body_top_z)
corner_inset = body_radius - corner_boss_radius

# --- Solenoid coil (X spans the footprint width) --------------------------
coil_depth = 24.0                   # Y
coil_z_range = (body_top_z, body_top_z + 26.0)

# --- Port: two quick-connect collets + bore, along Y ----------------------
port_radius = 15.0 / 2.0
port_length = 59.0
port_center_z = body_top_z / 2.0 - 4.0

# --- Spade terminals, off the +Y coil face --------------------------------
spade_width = 6.3                   # X
spade_thickness = 0.8               # Z
spade_length = 15.0                 # +Y protrusion
spade_x_spacing = 10.0
spade_z_center = 50.0
coil_face_y = coil_depth / 2.0

# --- Flow arrow on the boss's −Z face, pointing +Y (the flow direction) ---
arrow_emboss = 0.5
arrow_sink = 0.2
arrow_stem_half = 1.0
arrow_head_half = 2.5
arrow_profile = [
    (-arrow_stem_half, -5.0), (arrow_stem_half, -5.0),
    (arrow_stem_half, 1.0), (arrow_head_half, 1.0),
    (0.0, 5.0),
    (-arrow_head_half, 1.0), (-arrow_stem_half, 1.0),
]


def build_body():
    body = (
        cq.Workplane("XY")
        .workplane(offset=boss_z_range[0])
        .circle(body_radius)
        .extrude(boss_z_range[1] - boss_z_range[0])
    )
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            post = (
                cq.Workplane("XY")
                .center(sx * corner_inset, sy * corner_inset)
                .circle(corner_boss_radius)
                .extrude(corner_boss_z_range[1] - corner_boss_z_range[0])
            )
            body = body.union(post)
    top_box = (
        cq.Workplane("XY")
        .workplane(offset=top_box_z_range[0])
        .box(body_width, body_width, top_box_height, centered=(True, True, False))
    )
    return body.union(top_box)


def build_coil():
    return (
        cq.Workplane("XY")
        .workplane(offset=coil_z_range[0])
        .box(body_width, coil_depth, coil_z_range[1] - coil_z_range[0], centered=(True, True, False))
    )


def build_port():
    port = cq.Solid.makeCylinder(
        port_radius,
        port_length,
        cq.Vector(0.0, -port_length / 2.0, port_center_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    # Trim the port flush below the boss so the boss underside is a flat seat
    # for the arrow.
    boss_underside = (
        cq.Workplane("XY")
        .circle(body_radius)
        .extrude(boss_z_range[0])
    )
    return cq.Workplane(obj=port).cut(boss_underside)


def build_spades():
    return [
        cq.Workplane("XY")
        .box(spade_width, spade_length, spade_thickness, centered=True)
        .translate((sx * spade_x_spacing / 2.0, coil_face_y + spade_length / 2.0, spade_z_center))
        for sx in (-1.0, 1.0)
    ]


def build_arrow():
    return (
        cq.Workplane("XY")
        .workplane(offset=boss_z_range[0] - arrow_emboss)
        .polyline(arrow_profile)
        .close()
        .extrude(arrow_emboss + arrow_sink)
    )


def build_beduan_solenoid():
    valve = build_body().union(build_coil()).union(build_port())
    for spade in build_spades():
        valve = valve.union(spade)
    return valve.union(build_arrow())


def main():
    export_step(build_beduan_solenoid(), str(_here.parent / "beduan-solenoid.step"))
    print("-> beduan-solenoid.step")


if __name__ == "__main__":
    main()
