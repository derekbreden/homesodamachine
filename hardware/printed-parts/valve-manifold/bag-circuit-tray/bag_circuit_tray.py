"""Bag-circuit tray: 4 axis-aligned Beduan valves + 2 parallel Y-dividers.

The [fluid-topology](../../../topology/fluid-topology.md) bag circuit as a
tray. The four valves sit ports-along-X with no aiming tilt, butted in two
columns: V-F over V-I on the −X side, V-E over V-H on the +X side. The two
Y-dividers sit side by side (not in series) in the center, long axis along X,
so the gap between the two valve columns spans a single divider length.

    V-F ┐        ┌ V-E
        ├  Y-E  ─┤
        ┊        ┊
        ├  Y-H  ─┤
    V-I ┘        └ V-H

Each divider's stem meets the −X-column valve's inner port; its two +X outlets
feed the +X-column valve and the bag (Bag A for Y-E, Bag B for Y-H). The bag
and pump-side runs leave the tray.

Origin = cell center, Z = 0 the valve mounting plane, ports at Z = 11.3.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw,
    _hw / "printed-parts" / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import single_tray as cell

PORT_Z = cell.port_center_z
socket_radius = cell.socket_radius
saddle_radius = cell.saddle_radius
corner_pos = cell.corner_pos
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
_div_path = _hw / "printed-parts" / "reference" / "y-divider" / "y-divider.step"

# --- Layout (axis-aligned, ports along X) ---------------------------------
DIV_HALF = 19.25          # divider stem/outlet reach from its center (X)
PORT_HALF = 29.5          # valve port half-length
row_half = 16.125         # half the butted-pair pitch = valve body half-width
Vx = DIV_HALF + PORT_HALF  # 48.75: valve column X so the inner port tip meets
                           #          the divider face

# valve centers
VALVES = {
    "VF": (-Vx, +row_half),
    "VI": (-Vx, -row_half),
    "VE": (+Vx, +row_half),
    "VH": (+Vx, -row_half),
}
# divider centers (long axis +X, stem -> -X, outlets -> +X)
DIVIDERS = {"YE": (0.0, +row_half), "YH": (0.0, -row_half)}


def place_valve(cx, cy):
    return (
        cell.valve.build_beduan_solenoid()
        .val()
        .rotate((0, 0, 0), (0, 0, 1), 90.0)
        .translate((cx, cy, 0.0))
    )


def place_divider(cx, cy):
    fit = cq.importers.importStep(str(_div_path)).val()
    return fit.rotate((0, 0, 0), (0, 1, 0), -90.0).translate((cx, cy, PORT_Z))


def build_assembly():
    parts = {nm: place_valve(*p) for nm, p in VALVES.items()}
    parts.update({nm: place_divider(*p) for nm, p in DIVIDERS.items()})
    return parts


# --- Tray frame + stacking walls ------------------------------------------
margin = 3.0
wall_thickness = 3.0
wall_clear = 1.0
wall_top_z = 60.0
stack_pitch = wall_top_z - bot_z   # 63 mm

_socket_max_x = Vx + corner_pos
plate_half_x = _socket_max_x + socket_radius + margin
valve_y_extent = row_half + 16.125          # outer body edge = 32.25
plate_half_y = valve_y_extent + wall_clear + wall_thickness
cut_half_x = 24.0   # clears both dividers (reach |X| = 19.25), short of sockets
cut_half_y = 32.0   # clears the divider Y-spread (body reach |Y| = 31.6)


def _box(x0, x1, y_half, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, 2 * y_half, z1 - z0, centered=(True, True, False))
        .translate(((x0 + x1) / 2.0, 0.0, z0))
    )


def build_tray(valve_centers, plate_x, plate_y_half, gap_x, gap_y_half):
    """Generic parallel-divider tray: a frame plate with a central open gap, a
    four-socket + shared-row-saddle cradle per valve, and two ±Y stacking
    walls. ``plate_x`` / ``gap_x`` are (lo, hi) so the plate can be asymmetric.
    """
    cx_mid = (plate_x[0] + plate_x[1]) / 2.0
    tray = _box(plate_x[0], plate_x[1], plate_y_half, bot_z, top_z)
    tray = tray.cut(_box(gap_x[0], gap_x[1], gap_y_half, bot_z - 1.0, top_z + 1.0))

    for vx, vy in valve_centers:
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                tray = tray.cut(
                    cq.Workplane("XY")
                    .center(vx + sx * corner_pos, vy + sy * corner_pos)
                    .circle(socket_radius)
                    .extrude(top_z + 1.0)
                )

    saddle_len = (plate_x[1] - plate_x[0]) + 4.0
    for cy in dict.fromkeys(vy for _, vy in valve_centers):
        saddle = cq.Solid.makeCylinder(
            saddle_radius,
            saddle_len,
            cq.Vector(cx_mid - saddle_len / 2.0, cy, PORT_Z),
            cq.Vector(1.0, 0.0, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=saddle))

    for sy in (+1.0, -1.0):
        wall = _box(plate_x[0], plate_x[1], wall_thickness / 2.0, bot_z, wall_top_z)
        tray = tray.union(wall.translate((0.0, sy * (plate_y_half - wall_thickness / 2.0), 0.0)))
    return tray


def build_bag_circuit_tray():
    return build_tray(
        list(VALVES.values()),
        (-plate_half_x, plate_half_x),
        plate_half_y,
        (-cut_half_x, cut_half_x),
        cut_half_y,
    )


def main():
    export_step(build_bag_circuit_tray(), str(_here.parent / "bag-circuit-tray.step"))
    print("-> bag-circuit-tray.step")


if __name__ == "__main__":
    main()
