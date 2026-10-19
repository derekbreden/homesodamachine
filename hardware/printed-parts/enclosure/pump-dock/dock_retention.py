"""Bonded SB443-IN columns for the permanent pump dock.

Each pump's load line carries one column of four attracting pairs, centred
between that pump's two fluid ports. Each column sits in one plain pocket in
each mating part, open only at the mating face. The fixed pocket is as deep
as the thinnest block the drawing allows: each fixed block bottoms on its
floor and stands flush with the bay wall face or just proud of it. The
moving blocks are set against those poles with the cartridge seated on its
rigid lands, so the bare faces meet across the body air. Cured epoxy fills
each pocket behind the front bands and locks every block by its own side
grooves. No magnetic force or printed strength is inferred from this
geometry.
"""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq


# K&J SB443-IN drawing rev 0. General three-decimal tolerance is +/-0.004 in.
# The nominal purchased-part model uses its published fractional envelope.
BAR = 6.35
THICKNESS = 4.7625
GENERAL_TOLERANCE = 0.004 * 25.4
DRAWING_BAR_MAX = BAR + GENERAL_TOLERANCE
DRAWING_THICKNESS_MIN = (0.188 - 0.004) * 25.4
DRAWING_THICKNESS_MAX = (0.188 + 0.004) * 25.4
GROOVE_FRONT = 0.063 * 25.4
GROOVE_HEIGHT = 0.063 * 25.4
GROOVE_TOLERANCE = 0.010 * 25.4
GROOVED_WIDTH = 0.188 * 25.4
MAX_SERVICE_C = 80.0
# A fixed block bottomed on its floor stands this far proud of the wall at most.
FIXED_PROUD_MAX = DRAWING_THICKNESS_MAX - DRAWING_THICKNESS_MIN

ROWS_PER_COLUMN = 4
COLUMNS_PER_HALF = 2
MAGNETS_PER_HALF = ROWS_PER_COLUMN * COLUMNS_PER_HALF

# A drawing-maximum block keeps this air on each side of its pocket and at the
# stack's two ends; the bedding fills it.
SIDE_AIR = 0.10
SLOT_HALF = DRAWING_BAR_MAX / 2.0 + SIDE_AIR
# The moving pocket keeps this bedding behind the thickest block when it meets
# the proudest fixed pole.
BACK_AIR = 0.25
STRUCTURAL_STOCK = 3.0
# Bedding stays behind the front band's shallowest drawing position, so every
# pole face and the body air in front of it stay dry.
BEDDING_FRONT = GROOVE_FRONT - GROOVE_TOLERANCE


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


def row_z(z, row):
    return z + (row - (ROWS_PER_COLUMN - 1) / 2.0) * BAR


def stations(holes):
    """One station per magnet in one mating half, bottom to top in each column."""
    return tuple((x, row_z(z, row))
                 for x, z in column_stations(holes)
                 for row in range(ROWS_PER_COLUMN))


@dataclass(frozen=True)
class Interface:
    holes: tuple
    moving_face_y: float
    fixed_face_y: float

    @property
    def pole_y(self):
        """The bare pole plane of nominal blocks: a fixed block bottomed in its pocket."""
        return self.fixed_face_y - (THICKNESS - DRAWING_THICKNESS_MIN)

    @property
    def frame_gap(self):
        return self.fixed_face_y - self.moving_face_y

    @property
    def fixed_floor_y(self):
        return self.fixed_face_y + DRAWING_THICKNESS_MIN

    @property
    def moving_floor_y(self):
        """Bedding room behind the thickest moving block on the proudest fixed pole."""
        return self.fixed_face_y - FIXED_PROUD_MAX - DRAWING_THICKNESS_MAX - BACK_AIR

    def into(self, side):
        if side not in ("moving", "fixed"):
            raise ValueError("side is 'moving' or 'fixed'")
        return -1.0 if side == "moving" else 1.0

    def face(self, side):
        self.into(side)
        return self.moving_face_y if side == "moving" else self.fixed_face_y

    def floor(self, side):
        return self.moving_floor_y if self.into(side) < 0 else self.fixed_floor_y

    def yspan(self, side, d0, d1):
        """Depth is measured from the nominal bare pole plane into the owning part."""
        into = self.into(side)
        return _span(self.pole_y + into * d0, self.pole_y + into * d1)


def interface(holes, moving_face_y, fixed_face_y):
    result = Interface(tuple(tuple(map(float, h)) for h in holes),
                       float(moving_face_y), float(fixed_face_y))
    column_stations(result.holes)
    if result.frame_gap <= FIXED_PROUD_MAX:
        raise ValueError("The body air must exceed the proudest fixed pole")
    return result


def column_limits(z):
    """The pocket's Z extent: a drawing-maximum stack and its end air, centred on the row."""
    half = ROWS_PER_COLUMN * DRAWING_BAR_MAX / 2.0 + SIDE_AIR
    return z - half, z + half


def pocket(i, side, x, z):
    """One plain rectangular pocket per column, open only at the owning part's face."""
    bottom, top = column_limits(z)
    mouth = i.face(side) - i.into(side) * 0.1
    y0, y1 = _span(mouth, i.floor(side))
    return _box(x - SLOT_HALF, x + SLOT_HALF, y0, y1, bottom, top)


def column_stock(i, side, x, z):
    """Solid stock with the nominal 3 mm wall behind and around the pocket."""
    bottom, top = column_limits(z)
    half = SLOT_HALF + STRUCTURAL_STOCK
    y0, y1 = _span(i.face(side), i.floor(side) + i.into(side) * STRUCTURAL_STOCK)
    return _box(x - half, x + half, y0, y1,
                bottom - STRUCTURAL_STOCK, top + STRUCTURAL_STOCK)


def magnet(i, side, x, z):
    """Nominal purchased block with its two side grooves, pole face on the pole plane."""
    half = BAR / 2.0
    y0, y1 = i.yspan(side, 0.0, THICKNESS)
    body = _box(x - half, x + half, y0, y1, z - half, z + half)
    gy0, gy1 = i.yspan(side, GROOVE_FRONT, GROOVE_FRONT + GROOVE_HEIGHT)
    neck = GROOVED_WIDTH / 2.0
    for sign in (-1, 1):
        gx0, gx1 = _span(x + sign * neck, x + sign * (half + 0.1))
        body = body.cut(_box(gx0, gx1, gy0, gy1, z - half - 0.1, z + half + 0.1))
    return body.clean()


def features(holes, moving_face_y, fixed_face_y):
    """Production integration API: fuse `stock`, then subtract `cutter`, per side.

    `magnets` are named reference solids, not printed geometry. `potting` is
    the nominal cured bedding, deliberately separate from PET-GF.
    """
    i = interface(holes, moving_face_y, fixed_face_y)
    out = {"interface": i, "dimensions": dimensions(i)}
    for side in ("moving", "fixed"):
        stocks, cutters, magnets, fills = [], [], {}, []
        for col, (x, z) in enumerate(column_stations(i.holes), start=1):
            stocks.append(column_stock(i, side, x, z))
            cavity = pocket(i, side, x, z)
            cutters.append(cavity)
            bars = []
            for row in range(ROWS_PER_COLUMN):
                shape = magnet(i, side, x, row_z(z, row))
                magnets[f"pump-dock-SB443-{side}-{col}-{row + 1}"] = shape
                bars.append(shape)
            fy0, fy1 = _span(i.pole_y + i.into(side) * BEDDING_FRONT, i.floor(side))
            fill = cavity.intersect(_box(x - 20, x + 20, fy0, fy1, z - 40, z + 40))
            fills.append(fill.cut(_fused(bars)).clean())
        out[side] = {"stock": _fused(stocks), "cutter": _fused(cutters),
                     "magnets": magnets, "potting": _fused(fills)}
    return out


def dimensions(i):
    bottom, top = column_limits(0.0)
    return {"magnet": "K&J SB443-IN", "magnets_per_half": len(stations(i.holes)),
            "columns_per_half": len(column_stations(i.holes)),
            "rows_per_column": ROWS_PER_COLUMN,
            "column_axes_xz_mm": column_stations(i.holes),
            "nominal_bar_mm": [BAR, THICKNESS, BAR],
            "frame_faces_y_mm": [i.moving_face_y, i.fixed_face_y],
            "frame_gap_mm": i.frame_gap,
            "nominal_bare_pole_plane_y_mm": i.pole_y,
            "fixed_pole_proud_of_wall_mm": [0.0, FIXED_PROUD_MAX],
            "moving_pole_proud_of_cartridge_mm": [i.frame_gap - FIXED_PROUD_MAX, i.frame_gap],
            "pocket_width_mm": 2 * SLOT_HALF,
            "pocket_height_mm": top - bottom,
            "fixed_pocket_depth_mm": i.fixed_floor_y - i.fixed_face_y,
            "moving_pocket_depth_mm": i.moving_face_y - i.moving_floor_y,
            "drawing_maximum_side_air_mm": SIDE_AIR,
            "moving_bedding_behind_block_mm": [BACK_AIR, BACK_AIR + 2 * FIXED_PROUD_MAX],
            "bedding_front_depth_mm": BEDDING_FRONT,
            "minimum_back_and_side_stock_mm": STRUCTURAL_STOCK,
            "assembly": "Fixed blocks bonded bottomed in their pockets; moving blocks "
                        "bonded against the cured fixed poles with the cartridge seated "
                        "on its four lands",
            "magnet_pull_force_established": False,
            "pogo_seats_changed": False,
            "customer_adjustment": False}
