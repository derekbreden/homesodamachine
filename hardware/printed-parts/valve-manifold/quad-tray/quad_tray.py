"""Source-selection cell: a tray for 4 Beduan valves + 2 Y-dividers.

Realizes the front-end of the fluid topology (`../../../topology/
fluid-topology.md`): V-A and V-B merge at Y-A, Y-A bridges to Y-B, and Y-B
splits to V-C and V-D.

    V-A ┐                       ┌ V-C
        ├ Y-A ===(bridge)=== Y-B ┤
    V-B ┘                       └ V-D

The Y-divider (`../../reference/y-divider/`, a McMaster 51055K417 stand-in for
the BOM's John Guest PP2308E) is a trident: one stem and two parallel outlets
14.7 mm apart (Y = ±7.35), all three ports on one axis. The valves run ports
along X; each reaches its divider with an ~11.8 mm tube.

Layout (origin = cell center, Z = valve mounting plane, ports at Z = 11.3):
- Four valves at (±X_V, ±Y_V), ports along X. Left pair's inner ports face
  +X to Y-A; right pair's face -X to Y-B.
- Y-A flat at (-X_Y, 0, 11.3): stem → +X to the bridge, two outlets → -X at
  Y = ±7.35 to V-A / V-B. Y-B mirrored. Y-A↔Y-B bridge gap 5 mm.

The tray is a frame plate: four valve cradles (single-cell sockets + a shared
port saddle per Y row) around a central open gap that clears both dividers
(which dip to Z 3.2, below the Z=6 top) and the tubes, with two side walls
rising to Z=60 so the next cell stacks at a 63 mm pitch.
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
import single_tray as cell  # verified cell params + the valve + the divider path

# --- Imported geometry ----------------------------------------------------
PORT_Z = cell.port_center_z          # 11.3
socket_radius = cell.socket_radius   # 3.6
saddle_radius = cell.saddle_radius   # 7.7
corner_pos = cell.corner_pos         # 12.725
top_z = cell.tray_top_z              # 6.0
bot_z = cell.tray_bottom_z           # -3.0
_div_path = _hw / "printed-parts" / "reference" / "y-divider" / "y-divider.step"

# --- Arrangement (first pass; verified clash-free in the module test) ------
Y_V = 18.0                           # valve pitch/2 in Y
CENTRAL_GAP = 5.0                    # Y-A stem to Y-B stem
X_Y = (38.5 + CENTRAL_GAP) / 2.0     # divider center offset = 21.75
TUBE_X = 5.0                         # X component of the valve->divider tube
X_V = X_Y + 19.25 + TUBE_X + 29.5    # valve center offset = 75.5

VALVES = [(-X_V, +Y_V), (-X_V, -Y_V), (+X_V, +Y_V), (+X_V, -Y_V)]

# --- Tray frame + stacking walls ------------------------------------------
margin = 3.0                       # floor material beyond the outer sockets
valve_body_half = 16.125
wall_thickness = 3.0
wall_clear = 3.0                   # gap between valve body/coil and a wall
wall_top_z = 60.0                  # > 56.6 coil top, so the next tray stacks
stack_pitch = wall_top_z - bot_z   # 63 mm Z rise between stacked trays

plate_half_x = X_V + corner_pos + socket_radius + margin   # ~94.8
# In Y the plate reaches past the valve body + clearance to carry the walls.
plate_half_y = Y_V + valve_body_half + wall_clear + wall_thickness  # 40.125
cut_half_x = 44.0   # clears both dividers (reach X = ±41) with margin
cut_half_y = 20.0   # clears divider Y = ±15.45 with margin


def place_valve(cx, cy):
    return cell.valve.build_beduan_solenoid().val().rotate(
        (0, 0, 0), (0, 0, 1), -90
    ).translate((cx, cy, 0.0))


def place_divider(cx, sign):
    fit = cq.importers.importStep(str(_div_path)).val()
    return fit.rotate((0, 0, 0), (0, 1, 0), 90 * sign).translate((cx, 0.0, PORT_Z))


def build_assembly():
    """The 4 valves + 2 dividers, for fit verification / preview."""
    return {
        "VA": place_valve(-X_V, +Y_V), "VB": place_valve(-X_V, -Y_V),
        "VC": place_valve(+X_V, +Y_V), "VD": place_valve(+X_V, -Y_V),
        "YA": place_divider(-X_Y, +1), "YB": place_divider(+X_Y, -1),
    }


def build_quad_tray():
    tray = (
        cq.Workplane("XY")
        .box(2 * plate_half_x, 2 * plate_half_y, top_z - bot_z, centered=(True, True, False))
        .translate((0.0, 0.0, bot_z))
    )
    # Central open gap for the two dividers + the bridge/branch tubes.
    gap = (
        cq.Workplane("XY")
        .box(2 * cut_half_x, 2 * cut_half_y, (top_z - bot_z) + 2.0, centered=(True, True, False))
        .translate((0.0, 0.0, bot_z - 1.0))
    )
    tray = tray.cut(gap)
    # One port saddle per Y row (V-A/V-C share Y=+18; V-B/V-D share Y=-18).
    saddle_len = 2 * plate_half_x + 4.0
    for cy in (+Y_V, -Y_V):
        saddle = cq.Solid.makeCylinder(
            saddle_radius, saddle_len,
            cq.Vector(-saddle_len / 2.0, cy, PORT_Z), cq.Vector(1.0, 0.0, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=saddle))
    # Four corner-boss sockets per valve, blind to Z = 0.
    for cx, cy in VALVES:
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                socket = (
                    cq.Workplane("XY")
                    .center(cx + sx * corner_pos, cy + sy * corner_pos)
                    .circle(socket_radius)
                    .extrude(top_z + 1.0)
                )
                tray = tray.cut(socket)
    # Two side walls (±Y), full X length, rising clear of the valve coils so
    # the next tray stacks on their tops. The X-ends stay open for the ports.
    for sy in (+1.0, -1.0):
        wall = (
            cq.Workplane("XY")
            .box(2 * plate_half_x, wall_thickness, wall_top_z - bot_z, centered=(True, True, False))
            .translate((0.0, sy * (plate_half_y - wall_thickness / 2.0), bot_z))
        )
        tray = tray.union(wall)
    return tray


def main():
    export_step(build_quad_tray(), str(_here.parent / "quad-tray.step"))
    print("-> quad-tray.step")


if __name__ == "__main__":
    main()
