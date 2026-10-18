"""Post-print SB443-IN columns for the permanent pump dock.

The six mating pairs sit in two three-high columns. Bare pole faces meet in
recesses behind the fixed wall; the moving guard enters those recesses. Thin
printed rails retain the grooved blocks, while mechanically keyed, room-cured
potting fills their axial allowance after the pole faces have been gauged.
No magnetic force or printed strength is inferred from this geometry.
"""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq


# K&J SB443-IN drawing rev 0. General three-decimal tolerance is +/-0.004 in.
# The nominal purchased-part model uses its published fractional envelope.
BAR = 6.35
THICKNESS = 4.7625
GENERAL_TOLERANCE = 0.004 * 25.4
DRAWING_THICKNESS_MAX = (0.188 + 0.004) * 25.4
GROOVE_FRONT = 0.063 * 25.4
GROOVE_HEIGHT = 0.063 * 25.4
GROOVE_TOLERANCE = 0.010 * 25.4
GROOVED_WIDTH = 0.188 * 25.4
GROOVED_WIDTH_TOLERANCE = 0.010 * 25.4
MAX_SERVICE_C = 80.0

ROWS_PER_COLUMN = 3
COLUMNS_PER_HALF = 2
MAGNETS_PER_HALF = ROWS_PER_COLUMN * COLUMNS_PER_HALF

# These are local dry fitting allowances, separate from the wet receiver bore.
SLOT_HALF = 3.325
RAIL_TIP = 2.625
RAIL_FRONT = 2.00
RAIL_THICKNESS = 0.60
BACK_AIR = 0.20
SIDE_KEY = 1.60
KEY_FRONT = RAIL_FRONT + RAIL_THICKNESS
STRUCTURAL_STOCK = 3.0
GUARD_AIR = 0.25
GUARD_POLE_PROUD = 0.65
MOVING_POLE_PROJECTION = 2.0
LOADING_AIR = 0.20


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0,
                            cq.Vector(x0, y0, z0))


def _span(a, b):
    return min(a, b), max(a, b)


def _fused(shapes):
    shapes = tuple(shapes)
    if not shapes:
        raise ValueError("At least one solid is required")
    return shapes[0].fuse(*shapes[1:]).clean()


def column_stations(holes):
    """Two column centres, each midway between one pump's two actual port axes."""
    holes = tuple(sorted((float(x), float(z)) for x, z in holes))
    if len(holes) != 4 or max(z for _, z in holes) - min(z for _, z in holes) > 1e-6:
        raise ValueError("The dock requires four ports on one horizontal row")
    return tuple(((pair[0][0] + pair[1][0]) / 2.0,
                  (pair[0][1] + pair[1][1]) / 2.0)
                 for pair in (holes[:2], holes[2:]))


def stations(holes):
    """One station per magnet in one mating half, bottom to top in each column."""
    return tuple((x, z + (row - (ROWS_PER_COLUMN - 1) / 2.0) * BAR)
                 for x, z in column_stations(holes)
                 for row in range(ROWS_PER_COLUMN))


@dataclass(frozen=True)
class Interface:
    holes: tuple
    moving_face_y: float
    fixed_face_y: float

    @property
    def pole_y(self):
        return self.moving_face_y + MOVING_POLE_PROJECTION

    @property
    def frame_gap(self):
        return self.fixed_face_y - self.moving_face_y

    def into(self, side):
        if side not in ("moving", "fixed"):
            raise ValueError("side is 'moving' or 'fixed'")
        return -1.0 if side == "moving" else 1.0

    def face(self, side):
        self.into(side)
        return self.moving_face_y if side == "moving" else self.fixed_face_y

    def yspan(self, side, d0, d1):
        """Depth is measured from the bare pole face into its owning part."""
        into = self.into(side)
        return _span(self.pole_y + into * d0, self.pole_y + into * d1)


def interface(holes, moving_face_y, fixed_face_y):
    result = Interface(tuple(tuple(map(float, h)) for h in holes),
                       float(moving_face_y), float(fixed_face_y))
    column_stations(result.holes)
    if result.frame_gap <= 0 or result.pole_y <= result.fixed_face_y:
        raise ValueError("The pole plane must be inside the fixed-wall counterbore")
    return result


def column_limits(z):
    bottom = z - ROWS_PER_COLUMN * BAR / 2.0
    stack_max = bottom + ROWS_PER_COLUMN * (BAR + GENERAL_TOLERANCE)
    rail_top = stack_max + LOADING_AIR
    top = rail_top + BAR + GENERAL_TOLERANCE + LOADING_AIR
    return bottom, rail_top, top


def column_cavity(i, side, x, z):
    """Rail-guided stack and front-loading mouth above it, including potting keys.

    A bar enters the full-width upper mouth along Y, then drops along Z onto
    the rails. That route remains accessible after the owning print finishes.
    The cured keyed fill closes both the loading mouth and the stack's Z route.
    """
    bottom, rail_top, top = column_limits(z)
    depth = DRAWING_THICKNESS_MAX + BACK_AIR
    face_depth = i.into(side) * (i.face(side) - i.pole_y)
    # Begin outside both the main face and any proud guard.
    start = min(face_depth - 0.1, -GUARD_POLE_PROUD - 0.1)
    y0, y1 = i.yspan(side, start, depth)
    main = _box(x - SLOT_HALF, x + SLOT_HALF, y0, y1, bottom, top)
    ry0, ry1 = i.yspan(side, RAIL_FRONT, RAIL_FRONT + RAIL_THICKNESS)
    for sign in (-1, 1):
        rx0, rx1 = _span(x + sign * RAIL_TIP, x + sign * SLOT_HALF)
        rail = _box(rx0, rx1, ry0, ry1, bottom - 0.1, rail_top)
        main = main.cut(rail)
    # Wider cavities behind the rail form undercut keys. Their cured resin
    # cannot pull through the narrower front opening even if adhesion is lost.
    ky0, ky1 = i.yspan(side, KEY_FRONT, depth)
    keys = []
    for sign in (-1, 1):
        kx0, kx1 = _span(x + sign * (SLOT_HALF - 0.01),
                         x + sign * (SLOT_HALF + SIDE_KEY))
        keys.append(_box(kx0, kx1, ky0, ky1, bottom, top))
    return main.fuse(*keys).clean()


def column_stock(i, side, x, z):
    """Local stock including 3 mm around the back and sides of every key."""
    bottom, _, top = column_limits(z)
    half = SLOT_HALF + SIDE_KEY + STRUCTURAL_STOCK
    if side == "moving":
        y0 = i.pole_y - (DRAWING_THICKNESS_MAX + BACK_AIR + STRUCTURAL_STOCK)
        y1 = i.pole_y - GUARD_POLE_PROUD
    else:
        y0 = i.fixed_face_y
        y1 = i.pole_y + DRAWING_THICKNESS_MAX + BACK_AIR + STRUCTURAL_STOCK
    return _box(x - half, x + half, y0, y1,
                bottom - STRUCTURAL_STOCK, top + STRUCTURAL_STOCK)


def guard_clearance(i, x, z):
    """Fixed-wall recess for the moving guard; the original body stops still seat."""
    bottom, _, top = column_limits(z)
    half = SLOT_HALF + SIDE_KEY + STRUCTURAL_STOCK + GUARD_AIR
    return _box(x - half, x + half, i.fixed_face_y - 0.1,
                i.pole_y - GUARD_POLE_PROUD + GUARD_AIR,
                bottom - STRUCTURAL_STOCK - GUARD_AIR,
                top + STRUCTURAL_STOCK + GUARD_AIR)


def magnet(i, side, x, z, *, tolerance=False):
    """Nominal purchased block with its two actual grooves, or a fit envelope."""
    if tolerance:
        half = (BAR + GENERAL_TOLERANCE) / 2.0
        thick = DRAWING_THICKNESS_MAX
    else:
        half, thick = BAR / 2.0, THICKNESS
    y0, y1 = i.yspan(side, 0.0, thick)
    body = _box(x - half, x + half, y0, y1, z - half, z + half)
    if tolerance:
        front = GROOVE_FRONT + GROOVE_TOLERANCE
        rear = 2 * (GROOVE_FRONT - GROOVE_TOLERANCE)
        neck = (GROOVED_WIDTH + GROOVED_WIDTH_TOLERANCE) / 2.0
    else:
        front = GROOVE_FRONT
        rear = GROOVE_FRONT + GROOVE_HEIGHT
        neck = GROOVED_WIDTH / 2.0
    gy0, gy1 = i.yspan(side, front, rear)
    for sign in (-1, 1):
        gx0, gx1 = _span(x + sign * neck, x + sign * (half + 0.1))
        body = body.cut(_box(gx0, gx1, gy0, gy1, z - half - 0.1, z + half + 0.1))
    return body.clean()


def features(holes, moving_face_y, fixed_face_y):
    """Production integration API: fuse stock, then subtract cutter per side.

    `magnets` are named reference solids, not printed geometry. `potting` is
    the nominal cured-fill envelope, deliberately separate from PET-GF.
    `setting_gauges` are factory tools and stay outside the appliance assembly.
    """
    i = interface(holes, moving_face_y, fixed_face_y)
    out = {"interface": i, "dimensions": dimensions(i)}
    for side in ("moving", "fixed"):
        stocks, cutters, magnets, fills = [], [], {}, []
        for col, (x, z) in enumerate(column_stations(i.holes), start=1):
            stocks.append(column_stock(i, side, x, z))
            cavity = column_cavity(i, side, x, z)
            cutters.append(cavity)
            bars = []
            for row in range(ROWS_PER_COLUMN):
                mz = z + (row - (ROWS_PER_COLUMN - 1) / 2.0) * BAR
                shape = magnet(i, side, x, mz)
                magnets[f"pump-dock-SB443-{side}-{col}-{row + 1}"] = shape
                bars.append(shape)
            # Potting starts behind the front band, keeping every pole bare.
            fy0, fy1 = i.yspan(side, GROOVE_FRONT - GROOVE_TOLERANCE,
                              DRAWING_THICKNESS_MAX + BACK_AIR)
            bottom, _, top = column_limits(z)
            fill = cavity.intersect(_box(x - 20, x + 20, fy0, fy1, bottom, top))
            fills.append(fill.cut(_fused(bars)).clean())
        if side == "fixed":
            cutters.extend(guard_clearance(i, x, z) for x, z in column_stations(i.holes))
        out[side] = {"stock": _fused(stocks), "cutter": _fused(cutters),
                     "magnets": magnets, "potting": _fused(fills),
                     "setting_gauges": tuple(setting_gauge(i, side, x, z)
                                             for x, z in column_stations(i.holes))}
    return out


def setting_gauge(i, side, x, z):
    """One flat pole-setting tool registering on the owning part's body plane.

    The two side feet clear the guard and counterbore; a 6 mm central rib
    enters the mouth and touches all three pole faces. Gauge step accuracy
    and installed frame gap are factory measurements, not print assumptions.
    """
    bottom, rail_top, top = column_limits(z)
    outer_half = SLOT_HALF + SIDE_KEY + STRUCTURAL_STOCK + GUARD_AIR
    foot_inner, foot_outer = outer_half + 1.0, outer_half + 4.0
    bridge0, bridge1 = top + STRUCTURAL_STOCK + 1.0, top + STRUCTURAL_STOCK + 4.0
    if side == "moving":
        y0, y1 = i.pole_y, i.pole_y + 3.0
        foot_y0, foot_y1 = i.moving_face_y, y1
    else:
        y0, y1 = i.fixed_face_y - 3.0, i.pole_y
        foot_y0, foot_y1 = y0, i.fixed_face_y
    stem_y0, stem_y1 = (y0, y1) if side == "moving" else (foot_y0, foot_y1)
    ribs = [_box(x - 3.0, x + 3.0, y0, y1, bottom, rail_top),
            _box(x - 3.0, x + 3.0, stem_y0, stem_y1, bottom, bridge1),
            _box(x - foot_outer, x + foot_outer, foot_y0, foot_y1, bridge0, bridge1)]
    for sign in (-1, 1):
        a, b = _span(x + sign * foot_inner, x + sign * foot_outer)
        ribs.append(_box(a, b, foot_y0, foot_y1, bottom, bridge1))
    return _fused(ribs)


def dimensions(i):
    common_front = GROOVE_FRONT + GROOVE_TOLERANCE
    common_back = 2 * (GROOVE_FRONT - GROOVE_TOLERANCE)
    return {"magnet": "K&J SB443-IN", "magnets_per_half": len(stations(i.holes)),
            "columns_per_half": len(column_stations(i.holes)),
            "rows_per_column": ROWS_PER_COLUMN,
            "column_axes_xz_mm": column_stations(i.holes),
            "nominal_bar_mm": [BAR, THICKNESS, BAR],
            "frame_faces_y_mm": [i.moving_face_y, i.fixed_face_y],
            "frame_gap_mm": i.frame_gap, "bare_pole_plane_y_mm": i.pole_y,
            "moving_pole_projection_mm": i.pole_y - i.moving_face_y,
            "fixed_pole_recess_mm": i.pole_y - i.fixed_face_y,
            "moving_guard_projection_mm": i.pole_y - GUARD_POLE_PROUD - i.moving_face_y,
            "guard_running_air_mm": GUARD_AIR,
            "common_drawing_groove_interval_mm": [common_front, common_back],
            "rail_depth_interval_mm": [RAIL_FRONT, RAIL_FRONT + RAIL_THICKNESS],
            "key_cavity_front_depth_mm": KEY_FRONT,
            "rail_to_worst_drawing_groove_air_mm": [RAIL_FRONT - common_front,
                                                    common_back - RAIL_FRONT - RAIL_THICKNESS],
            "rail_tip_to_maximum_groove_neck_air_mm": RAIL_TIP - (GROOVED_WIDTH + GROOVED_WIDTH_TOLERANCE) / 2,
            "minimum_back_and_side_stock_mm": STRUCTURAL_STOCK,
            "assembly": "Post-print front loading, then mechanically keyed room-temperature potting against pole-setting gauges",
            "magnet_pull_force_established": False,
            "pogo_seats_changed": False,
            "customer_adjustment": False}
