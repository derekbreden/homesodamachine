"""Source-selection cell: a tray for 4 Beduan valves + 2 Y-dividers.

The [fluid-topology](../../../topology/fluid-topology.md) front end as a tray:
V-A and V-B merge at Y-A, Y-A bridges to Y-B, Y-B splits to V-C and V-D.

    V-A ┐                       ┌ V-C
        ├ Y-A ==(bridge)== Y-B ┤
    V-B ┘                       └ V-D

The Y-divider (`../../../reference/y-divider/`, a McMaster 51055K417 stand-in for
the BOM's John Guest PP2308E) is a trident: one stem and two parallel outlets
14.7 mm apart (Y = ±7.35), all three ports on one axis.

Layout (origin = cell center, Z = valve mounting plane, ports at Z = 11.3):
- The two dividers sit close, stems 2 mm apart at the center bridge: Y-A flat
  at (-20.25, 0, 11.3) with stem → +X, two outlets → -X at Y = ±7.35; Y-B
  mirrored.
- Each valve is rotated about Z so its port axis points straight at the
  divider outlet it feeds — a straight 15 mm tube spans the gap. The valves
  sit at (±82.03, ±20.45), tilted ~17° off X, the minimum Y separation that
  keeps the four bodies clear.

The tray is a frame plate: four valve cradles (single-cell sockets at each
valve's rotated corners + a saddle along each aim line) around a central open
gap that clears both dividers and the tubes, with two side walls rising to
Z = 60 so the next cell stacks at a 63 mm pitch.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw,
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import single_tray as cell

port_z = cell.port_center_z
socket_radius = cell.socket_radius
saddle_radius = cell.saddle_radius
corner_pos = cell.corner_pos
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
_div_path = _hw / "reference" / "y-divider" / "y-divider.step"

# --- Divider spacing + aimed valve geometry -------------------------------
div_half = 19.25          # divider stem/outlet reach from its center
outlet_y = 7.35           # divider outlet offset from its axis
port_half = 29.5          # valve port half-length
bridge_gap = 2.0          # stem-to-stem gap between Y-A and Y-B
tube = 15.0               # straight valve-port-tip to divider-outlet run
valve_y = 20.45           # valve Y offset — minimum that keeps bodies clear

divider_x = (2 * div_half + bridge_gap) / 2.0  # divider center offset
_aim_len = port_half + tube                     # valve center to divider outlet
_outlet_x = divider_x + div_half                 # |x| of a divider outlet
valve_x = _outlet_x + math.sqrt(_aim_len ** 2 - (valve_y - outlet_y) ** 2)

# Per valve: (center_x, center_y, outlet_x, outlet_y) it aims at.
valves = [
    (-valve_x, +valve_y, -_outlet_x, +outlet_y),   # V-A -> Y-A upper
    (-valve_x, -valve_y, -_outlet_x, -outlet_y),   # V-B -> Y-A lower
    (+valve_x, +valve_y, +_outlet_x, +outlet_y),   # V-C -> Y-B upper
    (+valve_x, -valve_y, +_outlet_x, -outlet_y),   # V-D -> Y-B lower
]


def _aim_phi(vx, vy, dx, dy):
    """Z rotation mapping the valve's native +Y port axis onto the center->outlet aim."""
    return math.degrees(math.atan2(dy - vy, dx - vx)) - 90.0


def _rot2(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (x * c - y * s, x * s + y * c)


def place_valve(vx, vy, dx, dy, flip=False):
    # The aimed port (local +Y) is the outlet for V-A/V-B feeding Y-A; for
    # V-C/V-D it is the inlet drawing from Y-B (flow out to Y-KA/Y-KB), flipped 180.
    ang = _aim_phi(vx, vy, dx, dy) + (180.0 if flip else 0.0)
    return (
        cell.valve.build_beduan_solenoid()
        .val()
        .rotate((0, 0, 0), (0, 0, 1), ang)
        .translate((vx, vy, 0.0))
    )


def place_divider(cx, sign):
    fit = cq.importers.importStep(str(_div_path)).val()
    return fit.rotate((0, 0, 0), (0, 1, 0), 90 * sign).translate((cx, 0.0, port_z))


def build_assembly():
    flip = {"VA": False, "VB": False, "VC": True, "VD": True}
    parts = {nm: place_valve(*p, flip=flip[nm]) for nm, p in zip(("VA", "VB", "VC", "VD"), valves)}
    parts["YA"] = place_divider(-divider_x, +1)
    parts["YB"] = place_divider(+divider_x, -1)
    return parts



# --- Tray frame + stacking walls ------------------------------------------
margin = 3.0
wall_thickness = 3.0
wall_clear = 1.0
wall_top_z = 60.0
stack_pitch = wall_top_z - bot_z
valve_y_extent = 40.61             # valve reach in |Y| after aiming

_socket_x = [
    abs(vx + _rot2(sx * corner_pos, sy * corner_pos, _aim_phi(vx, vy, dx, dy))[0])
    for vx, vy, dx, dy in valves
    for sx in (-1.0, 1.0)
    for sy in (-1.0, 1.0)
]
plate_half_x = max(_socket_x) + socket_radius + margin
plate_half_y = valve_y_extent + wall_clear + wall_thickness
# Grooves cradling the divider tridents into the floor.
div_groove_radius = 8.1 + 0.3   # divider body half-thickness (16.2 mm) + clearance
div_span = _outlet_x   # divider reach in |X|


def build_source_select_tray():
    tray = (
        cq.Workplane("XY")
        .box(2 * plate_half_x, 2 * plate_half_y, top_z - bot_z, centered=(True, True, False))
        .translate((0.0, 0.0, bot_z))
    )
    for vx, vy, dx, dy in valves:
        phi = _aim_phi(vx, vy, dx, dy)
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                ox, oy = _rot2(sx * corner_pos, sy * corner_pos, phi)
                socket = (
                    cq.Workplane("XY")
                    .center(vx + ox, vy + oy)
                    .circle(socket_radius)
                    .extrude(top_z + 1.0)
                )
                tray = tray.cut(socket)
        ax, ay = dx - vx, dy - vy
        n = math.hypot(ax, ay)
        ux, uy = ax / n, ay / n
        saddle_len = 140.0
        saddle = cq.Solid.makeCylinder(
            saddle_radius,
            saddle_len,
            cq.Vector(vx - ux * saddle_len / 2.0, vy - uy * saddle_len / 2.0, port_z),
            cq.Vector(ux, uy, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=saddle))

    # Grooves along X at the trident axes (stem at Y = 0, outlets at
    # Y = +/-outlet_y) seat the divider bodies into the floor.
    for gy in (0.0, +outlet_y, -outlet_y):
        groove = cq.Solid.makeCylinder(
            div_groove_radius,
            2.0 * div_span,
            cq.Vector(-div_span, gy, port_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=groove))

    for sy in (+1.0, -1.0):
        wall = (
            cq.Workplane("XY")
            .box(2 * plate_half_x, wall_thickness, wall_top_z - bot_z, centered=(True, True, False))
            .translate((0.0, sy * (plate_half_y - wall_thickness / 2.0), bot_z))
        )
        tray = tray.union(wall)
    return tray


def main():
    export_step(build_source_select_tray(), str(_here.parent / "source-select-tray.step"))
    print("-> source-select-tray.step")


if __name__ == "__main__":
    main()
