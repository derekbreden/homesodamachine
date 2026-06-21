"""Bag-circuit tray: 4 axis-aligned Beduan valves + 2 Tee fittings.

The [fluid-topology](../../../topology/fluid-topology.md) bag circuit as a
tray. The four valves sit ports-along-X with no aiming tilt, paired in two
columns: V-F over V-I on the −X side, V-E over V-H on the +X side. Each row's
two valves connect **in-line through a Tee** whose run lies along X; the Tee's
branch rises (+Z) to the bag.

    V-F ──┬── V-E      Y-E run; branch up → Bag A
          ┊
    V-I ──┴── V-H      Y-H run; branch up → Bag B

This module also holds the shared parallel-tray base — `place_valve`,
`place_tee`, `build_tray`, and the common geometry — imported by the
all-Tee gate-tray variants in `../nozzle-gate-tray/` and `../bib-gate-tray/`.

Origin = cell center, Z = 0 the valve mounting plane, ports at Z = 11.3.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw.parent / "tools",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
from docgen import substitute_md
import single_tray as cell

port_z = cell.port_center_z
socket_radius = cell.socket_radius
saddle_radius = cell.saddle_radius
corner_pos = cell.corner_pos
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
socket_floor_z = cell.socket_floor_z
_tee_path = _hw / "reference" / "tee-connector" / "tee-connector.step"
_elbow_path = _hw / "reference" / "elbow-connector" / "elbow-connector.step"

# --- Shared geometry ------------------------------------------------------
port_half = 29.5  # valve port half-length
row_half = cell.valve.body_width_x / 2  # column-pair half-spacing = the valve's X half-width
tee_run_half = 20.07  # Tee run half-length (port to center)
valve_x = tee_run_half + port_half  # valve-center X; the inner port tip lands on the Tee run port
elbow_reach = 19.56  # elbow leg: collet face to the bend corner (axis intersection)

# This tray's valves + Tees.
valves = {
    "VF": (-valve_x, +row_half),
    "VI": (-valve_x, -row_half),
    "VE": (+valve_x, +row_half),
    "VH": (+valve_x, -row_half),
}
# Tee centers; run along X joins the row's two valves, branch +Z to the bag.
tees = {"YE": (0.0, +row_half), "YH": (0.0, -row_half)}


def place_valve(cx, cy, rot):
    """Valve rotated ``rot`` deg about Z; flow arrow (local +Y) points toward
    the spades = the outlet."""
    return (
        cell.valve.build_beduan_solenoid()
        .val()
        .rotate((0, 0, 0), (0, 0, 1), rot)
        .translate((cx, cy, 0.0))
    )


def place_tee(cx, cy):
    """Tee, run along X (joins valves / butts the next Tee), branch up (+Z)."""
    fit = cq.importers.importStep(str(_tee_path)).val()
    return (
        fit.rotate((0, 0, 0), (0, 1, 0), 90.0)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
        .translate((cx, cy, port_z))
    )


def place_elbow(cx, cy, ux, uy):
    """Elbow on a valve's outer (unoccupied) port: one leg collinear with the
    port axis — its collet butting the port tip — and the bend turning the line
    +Z up out of the tray. ``(cx, cy)`` is the valve center; ``(ux, uy)`` the
    outward unit vector of that port (pointing away from the valve)."""
    fit = cq.importers.importStep(str(_elbow_path)).val()
    # The elbow's native +Y leg maps onto the −outward direction (collet faces
    # the valve); a Z-only rotation leaves its +Z leg pointing up.
    phi = math.degrees(math.atan2(ux, -uy))
    corner = (
        cx + (port_half + elbow_reach) * ux,
        cy + (port_half + elbow_reach) * uy,
        port_z,
    )
    return fit.rotate((0, 0, 0), (0, 0, 1), phi).translate(corner)


def build_assembly():
    # Outlets point +X: V-F/V-I out to the center Tees, V-E/V-H out to the pumps.
    parts = {nm: place_valve(*p, -90.0) for nm, p in valves.items()}
    parts.update({nm: place_tee(*p) for nm, p in tees.items()})
    # An elbow turns each valve's outer (unoccupied) port +Z up out of the tray.
    parts.update({
        f"E{nm}": place_elbow(cx, cy, -1.0 if cx < 0 else 1.0, 0.0)
        for nm, (cx, cy) in valves.items()
    })
    return parts


# --- Tray frame + stacking walls ------------------------------------------
margin = 3.0
wall_thickness = 3.0
wall_clear = 1.0
wall_top_z = 60.0
stack_pitch = wall_top_z - bot_z
valve_y_extent = row_half + cell.valve.body_radius  # outer body edge of the butted pair
plate_half_y = valve_y_extent + wall_clear + wall_thickness

valve_pad = corner_pos + socket_radius + margin  # plate reach beyond a valve center in X
plate_half_x = valve_x + valve_pad

# Connector groove: a Tee's run/collet outer radius plus clearance, the
# trough the fitting sets into at port height (port_z).
tee_radius = 6.86            # Tee run/collet outer radius (body 13.72 wide)
groove_clearance = 0.25
tee_groove_radius = tee_radius + groove_clearance


def _box(x0, x1, y_half, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, 2 * y_half, z1 - z0, centered=(True, True, False))
        .translate(((x0 + x1) / 2.0, 0.0, z0))
    )


def build_tray(valve_centers, connectors, plate_x, plate_y_half):
    """Solid frame plate spanning ``plate_x`` (lo, hi), with a four-socket
    cradle and port saddle per valve, a groove per connector, and two ±Y
    stacking walls."""
    tray = _box(plate_x[0], plate_x[1], plate_y_half, bot_z, top_z)

    for vx, vy in valve_centers:
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                tray = tray.cut(
                    cq.Workplane("XY")
                    .workplane(offset=socket_floor_z)
                    .center(vx + sx * corner_pos, vy + sy * corner_pos)
                    .circle(socket_radius)
                    .extrude(top_z - socket_floor_z + 1.0)
                )
        port = cq.Solid.makeCylinder(
            saddle_radius,
            2.0 * port_half,
            cq.Vector(vx - port_half, vy, port_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=port))

    for cx, cy, length, radius in connectors:
        groove = cq.Solid.makeCylinder(
            radius,
            length,
            cq.Vector(cx - length / 2.0, cy, port_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=groove))

    for sy in (+1.0, -1.0):
        wall = _box(plate_x[0], plate_x[1], wall_thickness / 2.0, bot_z, wall_top_z)
        tray = tray.union(wall.translate((0.0, sy * (plate_y_half - wall_thickness / 2.0), 0.0)))
    return tray


def tee_grooves(tee_centers):
    """Connector grooves (cx, cy, length, radius) for Tee centers; each Tee run
    lies along X, so its groove is a cylinder of one run length."""
    return [(cx, cy, 2.0 * tee_run_half, tee_groove_radius) for cx, cy in tee_centers]


def build_bag_circuit_tray():
    return build_tray(
        list(valves.values()),
        tee_grooves(tees.values()),
        (-plate_half_x, plate_half_x),
        plate_half_y,
    )


def main():
    export_step(build_bag_circuit_tray(), str(_here.parent / "bag-circuit-tray.step"))
    print("-> bag-circuit-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "VALVE_X": f"{valve_x:.4g}",
            "PORT_Z": f"{port_z:.4g}",
            "TRAY_BOT_Z": f"{bot_z:.4g}",
            "TRAY_TOP_Z": f"{top_z:.4g}",
            "BAG_PLATE_W": f"{2 * plate_half_x:.0f}",
            "BAG_PLATE_D": f"{2 * plate_half_y:.0f}",
            "STACK_PITCH": f"{stack_pitch:.4g}",
            "WALL_TOP_Z": f"{wall_top_z:.4g}",
        },
        expected_counts={
            "VALVE_X": 1, "PORT_Z": 1, "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 1,
            "BAG_PLATE_W": 1, "BAG_PLATE_D": 1, "STACK_PITCH": 2, "WALL_TOP_Z": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
