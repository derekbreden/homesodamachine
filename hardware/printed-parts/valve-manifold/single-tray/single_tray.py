"""Single-Beduan cradle tray for the valve manifold (first pass).

A drop-in cradle for one Beduan solenoid valve (modeled in
`../../reference/beduan-solenoid/`). The valve's four corner bosses drop
into four sockets and its port cylinder nestles into a lengthwise saddle,
locating the valve in X-Y while its round body boss rests on the tray top.

Socket and saddle geometry are imported from the valve model so they track
it as it evolves.

Coordinate convention matches the valve: origin at the valve footprint
center, Z = 0 the valve mounting plane (corner-boss bottoms). The tray
fills the "posts-only" Z band below the round boss (Z 0 -> 6) plus a floor,
with its top surface at Z = 6 where the round boss begins. So the valve
seats with its four posts in the sockets, its port in the saddle, and its
round boss resting on the tray top.

First-pass choices to iterate on: socket/saddle clearances, floor and wall
thickness, how far the saddle runs in Y (it stops short of the collet ends
so tubes can still reach the ports), and whether the round boss should
bear on the tray top at all. This is one cell — the multi-valve layout
(side-by-side vs. stacked) is the next problem.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware))
sys.path.insert(0, str(_hardware / "printed-parts" / "reference" / "beduan-solenoid"))
from _cadq_export import export_step
import beduan_solenoid as valve

# --- Valve features the tray engages (imported, so they track the model) ---
# Corner-boss centers are inset from the footprint corners by their radius.
corner_pos = valve.body_x / 2.0 - valve.body_corner_boss_diameter / 2.0  # +/-12.725
corner_boss_radius = valve.body_corner_boss_diameter / 2.0
port_radius = valve.port_radius
port_center_z = valve.port_center_z
boss_start_z = valve.body_center_boss_z_start  # 6.0; posts-only band tops out here

# --- Tray parameters (first pass) -----------------------------------------
socket_clearance = 0.2   # radial play for the corner bosses
saddle_clearance = 0.2   # radial play for the port
wall = 3.0               # material outboard of the body footprint in X
floor = 3.0              # under the sockets and the saddle
saddle_half_y = 20.0     # saddle / tray reach in Y; leaves the collet ends free

tray_top_z = boss_start_z          # 6.0
tray_bottom_z = -floor             # -3.0
tray_half_x = valve.body_x / 2.0 + wall
tray_half_y = saddle_half_y

socket_radius = corner_boss_radius + socket_clearance
saddle_radius = port_radius + saddle_clearance


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

    # Port saddle: subtract the port (+clearance) as a lengthwise channel
    # along Y. It cuts the block from the port's underside up through the
    # top face, leaving a concave trough the port nestles into.
    saddle_len = 2 * tray_half_y + 2.0  # overshoot both Y faces for a clean cut
    saddle = cq.Solid.makeCylinder(
        saddle_radius,
        saddle_len,
        cq.Vector(0.0, -saddle_len / 2.0, port_center_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    tray = block.cut(cq.Workplane(obj=saddle))

    # Four corner-boss sockets: blind holes from the tray top down to Z = 0,
    # so each post drops in and bottoms on the floor.
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            socket = (
                cq.Workplane("XY")
                .center(sx * corner_pos, sy * corner_pos)
                .circle(socket_radius)
                .extrude(tray_top_z + 1.0)  # overshoot the top for a clean cut
            )
            tray = tray.cut(socket)
    return tray


def main():
    tray = build_single_tray()
    export_step(tray, str(_here.parent / "single-tray.step"))
    print("-> single-tray.step")


if __name__ == "__main__":
    main()
