"""First-pass multi-valve manifold tray — a naive grid (first waggle).

Tiles the verified single-Beduan cell (`../single-tray/`) into a COLS x ROWS
grid so we can measure how big a naive arrangement actually is. This is NOT a
topology-aware layout — it is the simplest thing that holds 12 valves, built
to expose the packing problem, not solve it.

The one hard geometric fact driving the shape: a Beduan's port is an in-line
through-line that sticks out ~29.5 mm from each end of the body. So valves
pack densely across X (perpendicular to the ports) but need a Y pitch greater
than the 59 mm port length, or the in-line ports of one row run into the next.
Hence COLS wide, ROWS deep, with a generous Y pitch.

Each column's two valves share one continuous port saddle (their ports are
colinear along Y). Each valve gets four corner-boss sockets. The slab stops
short of the outermost port ends in Y so the collets stay exposed for tubing.

Cell geometry (socket/saddle radii, the Z=6 top plane, corner inset) is
imported from `single_tray`, which imports it from the valve model — so the
whole stack tracks the Beduan as it changes.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hardware,
    _hardware / "printed-parts" / "reference" / "beduan-solenoid",
    _hardware / "printed-parts" / "valve-manifold" / "single-tray",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import single_tray as cell  # reuses the verified cell geometry + valve import

# --- Grid (first pass) ----------------------------------------------------
COLS = 6   # along X — the dense direction (perpendicular to the ports)
ROWS = 2   # along Y — one row per flavor bank
X_PITCH = 36.0   # body is 32.25 wide -> ~3.75 mm between bodies
Y_PITCH = 62.0   # > 59 mm port length so colinear ports of the two rows clear

wall = 3.0
slab_top_z = cell.tray_top_z       # 6.0, where the round boss rests
slab_bottom_z = cell.tray_bottom_z  # -3.0
socket_radius = cell.socket_radius
saddle_radius = cell.saddle_radius
corner_pos = cell.corner_pos


def col_x(i):
    return (i - (COLS - 1) / 2.0) * X_PITCH


def row_y(j):
    return (j - (ROWS - 1) / 2.0) * Y_PITCH


def cell_centers():
    return [(col_x(i), row_y(j)) for j in range(ROWS) for i in range(COLS)]


# Slab: wide enough to wrap every socket plus a wall; in Y it stops short of
# the outermost port ends so the collets stay exposed for tubing.
_max_col_x = col_x(COLS - 1)
_max_row_y = row_y(ROWS - 1)
slab_half_x = _max_col_x + corner_pos + socket_radius + wall
slab_half_y = _max_row_y + corner_pos + socket_radius + wall


def build_grid_tray():
    slab = (
        cq.Workplane("XY")
        .box(
            2 * slab_half_x,
            2 * slab_half_y,
            slab_top_z - slab_bottom_z,
            centered=(True, True, False),
        )
        .translate((0.0, 0.0, slab_bottom_z))
    )

    # One continuous port saddle per column — both rows' colinear ports share
    # it. Overshoots both Y faces so the channel opens at the slab ends.
    saddle_len = 2 * slab_half_y + 4.0
    for i in range(COLS):
        saddle = cq.Solid.makeCylinder(
            saddle_radius,
            saddle_len,
            cq.Vector(col_x(i), -saddle_len / 2.0, cell.port_center_z),
            cq.Vector(0.0, 1.0, 0.0),
        )
        slab = slab.cut(cq.Workplane(obj=saddle))

    # Four corner-boss sockets per valve, blind to Z = 0.
    for cx, cy in cell_centers():
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                socket = (
                    cq.Workplane("XY")
                    .center(cx + sx * corner_pos, cy + sy * corner_pos)
                    .circle(socket_radius)
                    .extrude(slab_top_z + 1.0)
                )
                slab = slab.cut(socket)
    return slab


def main():
    tray = build_grid_tray()
    export_step(tray, str(_here.parent / "grid-tray.step"))
    print("-> grid-tray.step")


if __name__ == "__main__":
    main()
