"""Source-selection cell: a tray for 4 Beduan valves + 2 Y-dividers.

The [fluid-topology](../../../topology/fluid-topology.md) front end as a tray:
V-A and V-B merge at Y-A, Y-A bridges to Y-B, Y-B splits to V-C and V-D.

    V-A ┐                       ┌ V-C
        ├ Y-A ==(bridge)== Y-B ┤
    V-B ┘                       └ V-D

The Y-divider (`../../../reference/y-divider/`, a McMaster 51055K417 stand-in for
the BOM's John Guest PP2308E) is a trident: one stem and two parallel outlets
[14.7](OUTLET_GAP) mm apart (Y = ±[7.35](OUTLET_Y)), all three ports on one axis.

Layout (origin = cell center, Z = valve mounting plane, ports at Z = [11.3](PORT_Z)):
- The two dividers sit close, stems [2](BRIDGE_GAP) mm apart at the center bridge: Y-A flat
  at (-[20.25](DIV_X), 0, [11.3](PORT_Z)) with stem → +X, two outlets → -X at Y = ±[7.35](OUTLET_Y); Y-B
  mirrored.
- Each valve is rotated about Z so its port axis points straight at the
  divider outlet it feeds — a straight [15](TUBE) mm tube spans the gap. The valves
  sit at (±[81.75](SRC_VALVE_X), ±[21.32](SRC_VALVE_Y)), tilted ~17° off X, the
  minimum Y separation that keeps the four bodies clear.

The tray is a frame plate: four valve cradles (single-cell sockets at each
valve's rotated corners + a saddle along each aim line) around a central open
gap that clears both dividers and the tubes, with two side walls rising to
Z = [60](WALL_TOP_Z) so the next cell stacks at a [63](STACK_PITCH) mm pitch.
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
    _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray",
    _hw.parent / "tools",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
import single_tray as cell
import bag_circuit_tray as bc

port_z = cell.port_center_z
socket_radius = cell.socket_radius
saddle_radius = cell.saddle_radius
corner_pos = cell.corner_pos
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
socket_floor_z = cell.socket_floor_z
_div_path = _hw / "reference" / "y-divider" / "y-divider.step"

# --- Divider spacing + aimed valve geometry -------------------------------
div_half = 19.25          # divider stem/outlet reach from its center
outlet_y = 7.35           # divider outlet offset from its axis
port_half = 29.5          # valve port half-length
bridge_gap = 2.0          # stem-to-stem gap between Y-A and Y-B
tube = 15.0               # straight valve-port-tip to divider-outlet run

divider_x = (2 * div_half + bridge_gap) / 2.0  # divider center offset
_aim_len = port_half + tube                     # valve center to divider outlet
_outlet_x = divider_x + div_half                 # |x| of a divider outlet


def _upper_valve_at(vy):
    """The +Y valve solid, aimed at its outlet and dropped at its (−X, vy)."""
    vx = _outlet_x + math.sqrt(_aim_len ** 2 - (vy - outlet_y) ** 2)
    ang = math.degrees(math.atan2(outlet_y - vy, vx - _outlet_x)) - 90.0
    return _valve_solid.rotate((0, 0, 0), (0, 0, 1), ang).translate((-vx, vy, 0.0))


# valve_y is solved from the valve solid: the two facing valves mirror across
# Y = 0, so the tightest clear offset is where the aimed body just reaches the
# centerline. The square top-box corners, swung out by the aim, reach furthest
# in — so this tracks the valve's X width on its own.
_valve_solid = cell.valve.build_beduan_solenoid().val()
_lo, _hi = outlet_y + 1.0, 30.0
for _ in range(40):
    _mid = (_lo + _hi) / 2.0
    if _upper_valve_at(_mid).BoundingBox().ymin < 0.0:
        _lo = _mid
    else:
        _hi = _mid
valve_y = _hi
valve_x = _outlet_x + math.sqrt(_aim_len ** 2 - (valve_y - outlet_y) ** 2)
valve_y_extent = _upper_valve_at(valve_y).BoundingBox().ymax  # plate reach in |Y|

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


def _valve_axes(vx, vy, dx, dy):
    """Aim unit (valve → its divider outlet) and the outward wall normal — the
    in-plane perpendicular pointing away from Y = 0."""
    ax, ay = dx - vx, dy - vy
    n = math.hypot(ax, ay)
    a = (ax / n, ay / n)
    perp = (a[1], -a[0])
    if (perp[1] < 0) != (vy < 0):
        perp = (-perp[0], -perp[1])
    return a, perp


def _line_xy(px, py, a):
    """Slope, intercept of the line through (px, py) along direction a."""
    m = a[1] / a[0]
    return m, py - m * px


def _wall_corner(vx, vy, a, nout, off, t):
    """A point ``off`` outboard of valve center along ``nout`` and ``t`` along
    the aim axis ``a``."""
    return (vx + off * nout[0] + t * a[0], vy + off * nout[1] + t * a[1])


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
    names = ("VA", "VB", "VC", "VD")
    parts = {nm: place_valve(*p, flip=flip[nm]) for nm, p in zip(names, valves)}
    parts["YA"] = place_divider(-divider_x, +1)
    parts["YB"] = place_divider(+divider_x, -1)
    # An elbow turns each valve's outer (back, away-from-divider) port +Z up.
    for nm, (vx, vy, dx, dy) in zip(names, valves):
        ox, oy = vx - dx, vy - dy
        n = math.hypot(ox, oy)
        parts[f"E{nm}"] = bc.place_elbow(vx, vy, ox / n, oy / n)
    return parts



# --- Tray frame + stacking walls ------------------------------------------
margin = 3.0
wall_thickness = 3.0
wall_clear = 1.0
wall_top_z = 60.0
stack_pitch = wall_top_z - bot_z

_socket_x = [
    abs(vx + _rot2(sx * corner_pos, sy * corner_pos, _aim_phi(vx, vy, dx, dy))[0])
    for vx, vy, dx, dy in valves
    for sx in (-1.0, 1.0)
    for sy in (-1.0, 1.0)
]
plate_half_x = max(_socket_x) + socket_radius + margin
plate_half_y = valve_y_extent + wall_clear + wall_thickness
# Grooves cradling the divider tridents into the floor.
div_body_half = 8.1             # divider body half-thickness (16.2 mm envelope)
div_groove_radius = div_body_half + 0.3   # + clearance
div_span = _outlet_x   # divider reach in |X|

# The tray pinches in the middle: full-width floor + full-height walls hug the
# two valve ends (|X| > x_split), and a narrow central bridge hugs the dividers
# between them. The bridge floor is only as wide in Y as the dividers reach, and
# its walls rise only high enough to clear them.
x_split = min(_socket_x) - (socket_radius + margin)    # inner edge of a valve band
div_y_extent = outlet_y + div_groove_radius            # divider reach in |Y| incl. groove
hug_half_y = div_y_extent + wall_clear + wall_thickness  # central bridge half-width
div_crown_z = port_z + div_body_half                   # divider crown height
hug_wall_top_z = div_crown_z + 2.0                     # short central walls just clear the dividers
valve_back_x = plate_half_x                            # valve-end floor back edge (covers the rear sockets)

# Walls hug the valve bodies and the port cylinders. The tall valve-end walls run
# parallel to each valve's outer top-box edge; the short central walls bump
# outward where a valve's inner port pokes past the divider-hug line.
body_width_x = cell.valve.body_width_x                 # valve top-box width (local X)
body_width = cell.valve.body_width                     # valve top-box depth (local Y)
tall_inner = body_width_x / 2 + wall_clear             # tall-wall inner face, off valve center
port_face_offset = cell.valve.port_radius + wall_clear  # short-wall bump, off the port axis


def build_source_select_tray():
    def extrude_xy(pts, z0, z1):
        return (
            cq.Workplane("XY").polyline(pts).close()
            .extrude(z1 - z0).translate((0.0, 0.0, z0))
        )

    # Central bridge: the short walls hug the dividers but bump outward where a
    # valve's inner port pokes past the hug line; the bridge floor follows.
    side_profiles = {}
    for sy in (-1.0, 1.0):
        hug_in = sy * (hug_half_y - wall_thickness)
        vL, vR = sorted((v for v in valves if (v[1] < 0) == (sy < 0)), key=lambda v: v[0])
        aL, noutL = _valve_axes(*vL)
        aR, noutR = _valve_axes(*vR)
        mL, cL = _line_xy(vL[0] + port_face_offset * noutL[0], vL[1] + port_face_offset * noutL[1], aL)
        mR, cR = _line_xy(vR[0] + port_face_offset * noutR[0], vR[1] + port_face_offset * noutR[1], aR)
        inner = [
            (-x_split, mL * -x_split + cL),    # left port tangent at the bridge end
            ((hug_in - cL) / mL, hug_in),       # left tangent meets the divider-hug line
            ((hug_in - cR) / mR, hug_in),       # straight hug across the dividers
            (x_split, mR * x_split + cR),        # right port tangent at the bridge end
        ]
        outer = [(x, y + sy * wall_thickness) for x, y in inner]
        side_profiles[sy] = (inner, outer)

    tray = extrude_xy(side_profiles[-1.0][1] + side_profiles[1.0][1][::-1], bot_z, top_z)
    for sx in (-1.0, 1.0):
        # Valve-end floor follows the walls: the two tall walls' slanted outer
        # faces on ±Y, the connecting-wall inner faces on the inboard side, and
        # full width only across the back where the rear sockets sit.
        vp = next(v for v in valves if v[0] * sx > 0 and v[1] > 0)   # +Y valve this end
        vm = next(v for v in valves if v[0] * sx > 0 and v[1] < 0)   # −Y valve this end

        def faces(v):
            a, nout = _valve_axes(*v)
            fo = _wall_corner(v[0], v[1], a, nout, tall_inner + wall_thickness, body_width / 2)   # front-outer
            bo = _wall_corner(v[0], v[1], a, nout, tall_inner + wall_thickness, -body_width / 2)  # back-outer
            fi = _wall_corner(v[0], v[1], a, nout, tall_inner, body_width / 2)
            return fo, bo, fi[0] - sx * wall_thickness               # +connecting-wall inner-face x

        fop, bop, cwx = faces(vp)
        fom, bom, _ = faces(vm)
        bx = sx * valve_back_x
        tray = tray.union(extrude_xy([
            (cwx, fom[1]), (fom[0], fom[1]), (bom[0], bom[1]), (bx, bom[1]),
            (bx, bop[1]), (bop[0], bop[1]), (fop[0], fop[1]), (cwx, fop[1]),
        ], bot_z, top_z))

    for vx, vy, dx, dy in valves:
        phi = _aim_phi(vx, vy, dx, dy)
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                ox, oy = _rot2(sx * corner_pos, sy * corner_pos, phi)
                socket = (
                    cq.Workplane("XY")
                    .workplane(offset=socket_floor_z)
                    .center(vx + ox, vy + oy)
                    .circle(socket_radius)
                    .extrude(top_z - socket_floor_z + 1.0)
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

    # Tall valve-end walls: a full-height slab parallel to each valve's outer
    # top-box edge, set one clearance outboard of it.
    for vx, vy, dx, dy in valves:
        a, nout = _valve_axes(vx, vy, dx, dy)
        t_back, t_front = -body_width / 2, body_width / 2   # spans the valve top-box edge
        tray = tray.union(extrude_xy(
            [_wall_corner(vx, vy, a, nout, tall_inner, t_back),
             _wall_corner(vx, vy, a, nout, tall_inner, t_front),
             _wall_corner(vx, vy, a, nout, tall_inner + wall_thickness, t_front),
             _wall_corner(vx, vy, a, nout, tall_inner + wall_thickness, t_back)],
            bot_z, wall_top_z,
        ))

    # Short central walls: the hug/bump strip per side, just clearing the dividers.
    for sy in (-1.0, 1.0):
        inner, outer = side_profiles[sy]
        tray = tray.union(extrude_xy(inner + outer[::-1], bot_z, hug_wall_top_z))

    # Short connecting walls: a 3 mm-thick wall per junction, running in Y from
    # the short-wall end to the tall wall's front edge (overlapping both so it
    # fuses into the perimeter).
    for vx, vy, dx, dy in valves:
        a, nout = _valve_axes(vx, vy, dx, dy)
        m, c = _line_xy(vx + port_face_offset * nout[0], vy + port_face_offset * nout[1], a)
        sx, sy = math.copysign(1.0, vx), math.copysign(1.0, vy)
        fi = _wall_corner(vx, vy, a, nout, tall_inner, body_width / 2)               # tall front-inner
        fo = _wall_corner(vx, vy, a, nout, tall_inner + wall_thickness, body_width / 2)  # tall front-outer
        ty = m * (sx * x_split) + c                                  # short-wall inner end y
        x0, x1 = sorted((fi[0], fi[0] - sx * wall_thickness))        # 3 mm in X, reaching the tall wall
        y0, y1 = sorted((ty, fo[1]))                                 # from the short-wall end up to the tall wall
        tray = tray.union(
            cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, hug_wall_top_z - bot_z, centered=(False, False, False))
            .translate((x0, y0, bot_z))
        )
    return tray


def main():
    export_step(build_source_select_tray(), str(_here.parent / "source-select-tray.step"))
    print("-> source-select-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "OUTLET_GAP": f"{2 * outlet_y:.4g}",
            "PORT_Z": f"{port_z:.4g}",
            "BRIDGE_GAP": f"{bridge_gap:.4g}",
            "DIV_X": f"{divider_x:.4g}",
            "OUTLET_Y": f"{outlet_y:.4g}",
            "TUBE": f"{tube:.4g}",
            "SRC_VALVE_X": f"{valve_x:.4g}",
            "SRC_VALVE_Y": f"{valve_y:.4g}",
            "TRAY_BOT_Z": f"{bot_z:.4g}",
            "TRAY_TOP_Z": f"{top_z:.4g}",
            "SRC_PLATE_W": f"{2 * plate_half_x:.0f}",
            "SRC_PLATE_D": f"{2 * plate_half_y:.0f}",
            "STACK_PITCH": f"{stack_pitch:.4g}",
            "WALL_TOP_Z": f"{wall_top_z:.4g}",
            "COIL_TOP": f"{cell.valve.coil_z_range[1]:.4g}",
        },
        expected_counts={
            "OUTLET_GAP": 1, "PORT_Z": 2, "BRIDGE_GAP": 1, "DIV_X": 1,
            "OUTLET_Y": 2, "TUBE": 1, "SRC_VALVE_X": 1, "SRC_VALVE_Y": 1,
            "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 1, "SRC_PLATE_W": 1, "SRC_PLATE_D": 1,
            "STACK_PITCH": 2, "WALL_TOP_Z": 1, "COIL_TOP": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        _here,
        variables={
            "SRC_VALVE_X": f"{valve_x:.4g}",
            "SRC_VALVE_Y": f"{valve_y:.4g}",
            "OUTLET_GAP": f"{2 * outlet_y:.4g}",
            "OUTLET_Y": f"{outlet_y:.4g}",
            "PORT_Z": f"{port_z:.4g}",
            "BRIDGE_GAP": f"{bridge_gap:.4g}",
            "DIV_X": f"{divider_x:.4g}",
            "TUBE": f"{tube:.4g}",
            "WALL_TOP_Z": f"{wall_top_z:.4g}",
            "STACK_PITCH": f"{stack_pitch:.4g}",
        },
        expected_counts={
            "SRC_VALVE_X": 1, "SRC_VALVE_Y": 1,
            "OUTLET_GAP": 1, "OUTLET_Y": 2, "PORT_Z": 2,
            "BRIDGE_GAP": 1, "DIV_X": 1, "TUBE": 1,
            "WALL_TOP_Z": 1, "STACK_PITCH": 1,
        },
    )
    print(f"-> {_here.name} (self)")


if __name__ == "__main__":
    main()
