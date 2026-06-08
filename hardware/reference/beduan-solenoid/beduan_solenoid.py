"""Reference solid for the Beduan 12V DC normally-closed solenoid valve
(2-way, 1/4" quick-connect, Amazon B07NWCQJK9) — used 12x on the
fluid-topology manifold (see `hardware/bom.md`).

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
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments

# --- White valve body -----------------------------------------------------
body_width = 32.25                  # footprint width; also the central-boss diameter
body_radius = body_width / 2.0  # [16.12 mm](BODY_RADIUS)
corner_boss_radius = 6.8 / 2.0
top_box_height = 5.0

body_top_z = 30.6
boss_z_range = (6.0, body_top_z)              # central boss; corner posts run full-height below it
corner_boss_z_range = (0.0, body_top_z)
top_box_z_range = (body_top_z - top_box_height, body_top_z)
corner_spacing = 24.4  # corner-post center-to-center, both axes
corner_inset = corner_spacing / 2.0  # [12.2 mm](CORNER_INSET)

# --- Solenoid coil (X spans the footprint width) --------------------------
coil_depth = 24.0                   # Y
coil_z_range = (body_top_z, body_top_z + 26.0)  # top [56.6 mm](COIL_TOP_Z)

# --- Port: two quick-connect collets + bore, along Y ----------------------
port_radius = 15.0 / 2.0
port_length = 59.0
port_center_z = body_top_z / 2.0 - 4.0  # [11.3 mm](PORT_CENTER_Z)

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
    # The boss underside is the arrow's flat seat.
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
    substitute_md(
        _here.parent / "README.md",
        variables={
            "BODY_DIA": f"{body_width:.4g}",
            "POST_DIA": f"{2 * corner_boss_radius:.4g}",
            "PORT_DIA": f"{2 * port_radius:.4g}",
            "PORT_LEN": f"{port_length:.4g}",
            "BODY_TOP_Z": f"{body_top_z:.4g}",
            "BOSS_Z0": f"{boss_z_range[0]:.4g}",
            "TOP_BOX_H": f"{top_box_height:.4g}",
            "TOP_BOX_Z0": f"{top_box_z_range[0]:.4g}",
            "COIL_DEPTH": f"{coil_depth:.4g}",
            "COIL_H": f"{coil_z_range[1] - coil_z_range[0]:.4g}",
            "COIL_TOP": f"{coil_z_range[1]:.4g}",
            "SPADE_W": f"{spade_width:.4g}",
            "SPADE_LEN": f"{spade_length:.4g}",
            "SPADE_T": f"{spade_thickness:.4g}",
            "SPADE_SPACING": f"{spade_x_spacing:.4g}",
            "SPADE_Z": f"{spade_z_center:.4g}",
            "COIL_FACE_Y": f"{coil_face_y:.4g}",
            "SPADE_Y_END": f"{coil_face_y + spade_length:.4g}",
        },
        expected_counts={
            "BODY_DIA": 9, "POST_DIA": 2, "PORT_DIA": 1, "PORT_LEN": 2,
            "BODY_TOP_Z": 7, "BOSS_Z0": 3, "TOP_BOX_H": 2, "TOP_BOX_Z0": 2,
            "COIL_DEPTH": 2, "COIL_H": 1, "COIL_TOP": 2,
            "SPADE_W": 1, "SPADE_LEN": 1, "SPADE_T": 1,
            "SPADE_SPACING": 1, "SPADE_Z": 1, "COIL_FACE_Y": 1, "SPADE_Y_END": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables={
            "BODY_RADIUS": f"{body_radius:.4g} mm",
            "CORNER_INSET": f"{corner_inset:.4g} mm",
            "PORT_CENTER_Z": f"{port_center_z:.4g} mm",
            "COIL_TOP_Z": f"{coil_z_range[1]:.4g} mm",
        },
        expected_counts={
            "BODY_RADIUS": 1,
            "CORNER_INSET": 1,
            "PORT_CENTER_Z": 1,
            "COIL_TOP_Z": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
