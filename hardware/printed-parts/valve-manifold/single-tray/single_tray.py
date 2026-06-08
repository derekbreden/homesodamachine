"""Single-Beduan cradle tray for the valve manifold.

A cradle for one Beduan solenoid valve (modeled in
`../../../reference/beduan-solenoid/`). The valve's four corner bosses drop
into four sockets and its port cylinder nestles into a lengthwise saddle,
locating the valve in X-Y while its round body boss rests on the tray top.

Coordinate convention matches the valve: origin at the valve footprint
center, Z = 0 the valve mounting plane (corner-boss bottoms). The tray
fills the posts-only Z band below the round boss (Z 0 -> 6) plus a floor,
with its top surface at Z = 6 where the round boss begins. The valve
seats with its four posts in the sockets, its port in the saddle, and its
round boss resting on the tray top.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware / "scripts"))
sys.path.insert(0, str(_hardware / "reference" / "beduan-solenoid"))
sys.path.insert(0, str(_hardware.parent / "tools"))
from _cadq_export import export_step
from docgen import substitute_md
import beduan_solenoid as valve

# --- Valve features the tray engages ---
# Corner-boss centers are inset from the footprint corners by their radius.
corner_pos = valve.corner_inset
corner_boss_radius = valve.corner_boss_radius
port_radius = valve.port_radius
port_center_z = valve.port_center_z
boss_start_z = valve.boss_z_range[0]  # posts-only band tops out here

# --- Tray parameters -----------------------------------------
socket_clearance = -0.05  # radial offset for the corner bosses
saddle_clearance = 0.2   # radial play for the port
wall = 3.0               # material outboard of the body footprint in X
floor = 3.0              # under the sockets and the saddle
saddle_half_y = 20.0     # saddle / tray reach in Y; leaves the collet ends free

tray_top_z = boss_start_z
tray_bottom_z = -floor
tray_half_x = valve.body_radius + wall
tray_half_y = saddle_half_y

socket_radius = corner_boss_radius + socket_clearance
saddle_radius = port_radius + saddle_clearance
socket_floor_z = -1.0    # socket floor, below the post tips at Z = 0


def build_single_tray():
    block = (
        cq.Workplane("XY")
        .box(
            2 * tray_half_x,
            2 * tray_half_y,
            tray_top_z - tray_bottom_z,
            centered=(True, True, False),
        )
        .translate((0.0, 0.0, tray_bottom_z))
    )

    # Port saddle: a concave trough along Y, open through the top face, that
    # the port nestles into.
    saddle_len = 2 * tray_half_y + 2.0
    saddle = cq.Solid.makeCylinder(
        saddle_radius,
        saddle_len,
        cq.Vector(0.0, -saddle_len / 2.0, port_center_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    tray = block.cut(cq.Workplane(obj=saddle))

    # Four corner-boss sockets: blind holes from the tray top down past Z = 0;
    # the posts hang free, the round boss seats on the tray top.
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            socket = (
                cq.Workplane("XY")
                .workplane(offset=socket_floor_z)
                .center(sx * corner_pos, sy * corner_pos)
                .circle(socket_radius)
                .extrude(tray_top_z - socket_floor_z + 1.0)
            )
            tray = tray.cut(socket)
    return tray


def main():
    tray = build_single_tray()
    export_step(tray, str(_here.parent / "single-tray.step"))
    print("-> single-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "POST_DIA": f"{2 * corner_boss_radius:.4g}",
            "SOCKET_DIA": f"{2 * socket_radius:.4g}",
            "SOCKET_FLOOR_Z": f"{socket_floor_z:.4g}",
            "PORT_DIA": f"{2 * port_radius:.4g}",
            "SADDLE_DIA": f"{2 * saddle_radius:.4g}",
            "SADDLE_CLEAR": f"{saddle_clearance:.4g} mm",
            "TRAY_TOP_Z": f"{tray_top_z:.4g}",
            "TRAY_BOT_Z": f"{tray_bottom_z:.4g}",
            "BLOCK_X": f"{2 * tray_half_x:.4g}",
            "BLOCK_Y": f"{2 * tray_half_y:.4g}",
            "BLOCK_Z": f"{tray_top_z - tray_bottom_z:.4g}",
            "FLOOR_UNDER_SOCKET": f"{socket_floor_z - tray_bottom_z:.4g} mm",
            "SADDLE_REACH": f"{saddle_half_y:.4g}",
            "PORT_HALF": f"{valve.port_length / 2:.4g}",
            "WALL": f"{wall:.4g} mm",
            "FLOOR": f"{floor:.4g} mm",
        },
        expected_counts={
            "POST_DIA": 1, "SOCKET_DIA": 1, "SOCKET_FLOOR_Z": 2,
            "PORT_DIA": 2, "SADDLE_DIA": 1, "SADDLE_CLEAR": 2,
            "TRAY_TOP_Z": 4, "TRAY_BOT_Z": 1,
            "BLOCK_X": 1, "BLOCK_Y": 1, "BLOCK_Z": 1,
            "FLOOR_UNDER_SOCKET": 1, "SADDLE_REACH": 2, "PORT_HALF": 1,
            "WALL": 1, "FLOOR": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
