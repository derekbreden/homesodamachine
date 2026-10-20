"""Bonded SB443-IN columns for the pump cartridge's magnetic seat.

Each pump's load line carries one column of four attracting pairs, centred
between that pump's two fluid ports. In each mating part the column is one
plain pocket, open only at the mating face and roofed by one 45-degree ridge,
cut into solid wall: front-top's receiver wall and the cartridge's aft wall
between each pump's two tube passages. Every printed face of the pocket keeps
its printed-fit allowance (`fits.py`): running clearance at the sides and ends,
which a block slides past as it is pushed home, and static clearance at the
floor it seats on. Each block is bedded in DP420 and pushed home to the floor,
so its pole stands proud of the face by its own thickness less the pocket
depth, and the seated pairs' poles meet and seat the cartridge. No magnetic
force or printed strength is inferred from this geometry.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path.insert(0, str(HW / 'printed-parts' / 'cadlib'))
import fits  # noqa: E402


# K&J SB443-IN drawing rev 0. General three-decimal tolerance is +/-0.004 in;
# the front band and groove height carry +/-0.010 in.
BAR = 6.35
THICKNESS = 4.7625
GENERAL_TOLERANCE = 0.004 * 25.4
GROOVE_FRONT = 0.063 * 25.4
GROOVE_HEIGHT = 0.063 * 25.4
GROOVE_TOLERANCE = 0.010 * 25.4
GROOVED_WIDTH = 0.188 * 25.4
MAX_SERVICE_C = 80.0

ROWS_PER_COLUMN = 4
COLUMNS_PER_HALF = 2
MAGNETS_PER_HALF = ROWS_PER_COLUMN * COLUMNS_PER_HALF

# A block slides past the pocket's sides and ends as it is pushed home, and seats
# head-on on its floor.
SIDE_AIR = fits.running
FLOOR_AIR = fits.slip
SLOT_HALF = BAR / 2.0 + SIDE_AIR
# Bedding stays behind the front band's shallowest drawing position, so every
# pole face and the frame gap in front of it stay dry.
BEDDING_FRONT = GROOVE_FRONT - GROOVE_TOLERANCE


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0,
                            cq.Vector(x0, y0, z0))


def _span(a, b):
    return min(a, b), max(a, b)


def _ridge(x, half, y0, y1, z):
    """A 45-degree roof along Y: its eaves `half` either side of `x` at `z`, its ridge over `x`."""
    wire = cq.Wire.makePolygon([cq.Vector(x - half, y0, z), cq.Vector(x + half, y0, z),
                                cq.Vector(x, y0, z + half)], close=True)
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), cq.Vector(0.0, y1 - y0, 0.0))


def _fused(shapes):
    shapes = tuple(shapes)
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


def column_limits(z):
    """The pocket's Z extent below its ridge: four drawing-maximum blocks with running
    air at both ends, centred on the row."""
    half = ROWS_PER_COLUMN * (BAR + GENERAL_TOLERANCE) / 2.0 + SIDE_AIR
    return z - half, z + half


@dataclass(frozen=True)
class Interface:
    holes: tuple
    moving_face_y: float
    fixed_face_y: float

    @property
    def frame_gap(self):
        return self.fixed_face_y - self.moving_face_y

    @property
    def pole_y(self):
        """Where nominal poles meet: the middle of the frame gap."""
        return (self.fixed_face_y + self.moving_face_y) / 2.0

    @property
    def proud(self):
        """A nominal block's pole stands this far out of its face, bottomed in its pocket."""
        return self.frame_gap / 2.0

    @property
    def depth(self):
        """Pocket depth from the mating face: a nominal block stands `proud` out of it once
        bottomed, with the floor's static allowance behind it."""
        return THICKNESS - self.proud + FLOOR_AIR

    def proud_range(self):
        """A bottomed block's pole stand-out over the drawing's thickness tolerance."""
        seat = self.depth - FLOOR_AIR
        return (THICKNESS - GENERAL_TOLERANCE - seat, THICKNESS + GENERAL_TOLERANCE - seat)

    def into(self, side):
        if side not in ("moving", "fixed"):
            raise ValueError("side is 'moving' or 'fixed'")
        return -1.0 if side == "moving" else 1.0

    def face(self, side):
        self.into(side)
        return self.moving_face_y if side == "moving" else self.fixed_face_y

    def floor(self, side):
        return self.face(side) + self.into(side) * self.depth

    def yspan(self, side, d0, d1):
        """Depth is measured from the nominal pole plane into the owning part."""
        into = self.into(side)
        return _span(self.pole_y + into * d0, self.pole_y + into * d1)


def interface(holes, moving_face_y, fixed_face_y):
    result = Interface(tuple(tuple(map(float, h)) for h in holes),
                       float(moving_face_y), float(fixed_face_y))
    column_stations(result.holes)
    if result.frame_gap <= 0.0:
        raise ValueError("The poles meet across a positive frame gap")
    return result


def pocket(i, side, x, z):
    """One plain pocket per column, open only at the owning part's face, roofed by a
    45-degree ridge standing on both side walls."""
    bottom, top = column_limits(z)
    y0, y1 = _span(i.face(side) - i.into(side) * 0.1, i.floor(side))
    return (_box(x - SLOT_HALF, x + SLOT_HALF, y0, y1, bottom, top)
            .fuse(_ridge(x, SLOT_HALF, y0, y1, top)).clean())


def magnet(i, side, x, z):
    """Nominal purchased block with its two side grooves, bottomed: pole face on the pole plane."""
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
    """Production integration API, per side: cut `cutter` from the mating part.
    `magnets` are named reference solids, not printed geometry; `potting` is the
    nominal cured bedding, deliberately separate from PET-GF."""
    i = interface(holes, moving_face_y, fixed_face_y)
    out = {"interface": i, "dimensions": dimensions(i)}
    for side in ("moving", "fixed"):
        cutters, magnets, fills = [], {}, []
        for col, (x, z) in enumerate(column_stations(i.holes), start=1):
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
        out[side] = {"cutter": _fused(cutters), "magnets": magnets, "potting": _fused(fills)}
    return out


def dimensions(i):
    bottom, top = column_limits(0.0)
    low, high = i.proud_range()
    return {"magnet": "K&J SB443-IN", "magnets_per_half": len(stations(i.holes)),
            "columns_per_half": len(column_stations(i.holes)),
            "rows_per_column": ROWS_PER_COLUMN,
            "column_axes_xz_mm": column_stations(i.holes),
            "nominal_bar_mm": [BAR, THICKNESS, BAR],
            "frame_faces_y_mm": [i.moving_face_y, i.fixed_face_y],
            "frame_gap_nominal_mm": i.frame_gap,
            "pole_plane_y_mm": i.pole_y,
            "pole_proud_nominal_mm": i.proud,
            "pole_proud_drawing_range_mm": [low, high],
            "frame_gap_drawing_range_mm": [2 * low, 2 * high],
            "pocket_width_mm": 2 * SLOT_HALF,
            "pocket_depth_mm": i.depth,
            "pocket_height_mm": top - bottom,
            "pocket_ridge_rise_mm": SLOT_HALF,
            "side_and_end_air_mm": SIDE_AIR,
            "floor_air_mm": FLOOR_AIR,
            "bedding_front_depth_mm": BEDDING_FRONT,
            "assembly": "Each block bedded in DP420 and pushed home to its pocket floor, both "
                        "parts together, one cure before the cartridge is seated",
            "magnet_pull_force_established": False,
            "customer_adjustment": False}
