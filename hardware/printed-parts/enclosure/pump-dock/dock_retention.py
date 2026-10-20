"""Printed-in SB443-IN columns for the pump cartridge's magnetic seat.

Each pump's load line carries one column of four attracting pairs, centred
between that pump's two fluid ports. In each mating part the column is one
vertical slot, open at the mating face, whose side walls carry a printed rail
in each of the blocks' two side grooves. The blocks drop down the rails at one
print pause, bare pole faces toward the mate, and the first layer after the
pause closes over them. Pulled toward its mate, each block bears on its rails
with its pole half the frame gap proud of its face, so the poles of a seated
pair meet in the middle of the gap and the meeting poles seat the cartridge.
The slots are cut into solid walls: front-top's receiver wall and the
cartridge's aft wall between each pump's two tube passages.
No magnetic force or printed strength is inferred from this geometry.
"""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq


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

# The slot keeps this air beside each block; the blocks slide down it by hand.
SIDE_AIR = 0.10
SLOT_HALF = BAR / 2.0 + SIDE_AIR
# Each rail fills its groove less 0.05 mm fore and aft, and stops short of the
# groove floor by RAIL_TIP_AIR.
RAIL = GROOVE_HEIGHT - 0.10
RAIL_TIP_AIR = 0.09
RAIL_TIP_HALF = GROOVED_WIDTH / 2.0 + RAIL_TIP_AIR
# Air behind the thickest block pushed in onto its rails.
FLOOR_AIR = 0.15
# Air over a stack of four drawing-maximum blocks, under the first closing layer.
STACK_AIR = 0.15


def _span(a, b):
    return min(a, b), max(a, b)


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0,
                            cq.Vector(x0, y0, z0))


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
    """The slot's floor and roof in Z: four nominal blocks stand on the floor, and the
    first layer over the slot clears four drawing-maximum blocks by STACK_AIR."""
    bottom = z - ROWS_PER_COLUMN * BAR / 2.0
    return bottom, bottom + ROWS_PER_COLUMN * (BAR + GENERAL_TOLERANCE) + STACK_AIR


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
        """Where the poles of a seated pair meet: the middle of the frame gap."""
        return (self.fixed_face_y + self.moving_face_y) / 2.0

    @property
    def proud(self):
        """Each pole stands this far out of its face, pulled onto its rails."""
        return self.frame_gap / 2.0

    @property
    def rail_depths(self):
        """The rail's two faces, measured into the part from its mating face. A block
        pulled toward its mate bears its back band on the deeper face."""
        deep = GROOVE_FRONT + GROOVE_HEIGHT - self.proud
        return deep - RAIL, deep

    @property
    def pushed_proud(self):
        """The pole's stand-out with the block pushed back onto the rail's shallow face."""
        return GROOVE_FRONT - self.rail_depths[0]

    @property
    def floor_depth(self):
        return THICKNESS + GENERAL_TOLERANCE - self.pushed_proud + FLOOR_AIR

    def into(self, side):
        if side not in ("moving", "fixed"):
            raise ValueError("side is 'moving' or 'fixed'")
        return -1.0 if side == "moving" else 1.0

    def face(self, side):
        self.into(side)
        return self.moving_face_y if side == "moving" else self.fixed_face_y

    def at(self, side, d0, d1):
        """A Y span at depths d0..d1 into the owning part from its mating face."""
        into, face = self.into(side), self.face(side)
        return _span(face + into * d0, face + into * d1)


def interface(holes, moving_face_y, fixed_face_y):
    result = Interface(tuple(tuple(map(float, h)) for h in holes),
                       float(moving_face_y), float(fixed_face_y))
    column_stations(result.holes)
    if result.frame_gap <= 0.0:
        raise ValueError("The poles meet across a positive frame gap")
    if result.pushed_proud < 0.0:
        raise ValueError("A block pushed onto its rails would sink below its face")
    return result


def slot(i, side, x, z):
    """One column's slot: open at the mating face, a rail standing into each side
    groove, a flat floor in Z for the stack and a flat roof the print closes over it."""
    bottom, top = column_limits(z)
    r0, r1 = i.rail_depths
    d = i.floor_depth
    # The slot's section in the part's own depth: wide, narrowed by the rails, wide.
    section = [(-SLOT_HALF, -0.1), (-SLOT_HALF, r0), (-RAIL_TIP_HALF, r0),
               (-RAIL_TIP_HALF, r1), (-SLOT_HALF, r1), (-SLOT_HALF, d),
               (SLOT_HALF, d), (SLOT_HALF, r1), (RAIL_TIP_HALF, r1),
               (RAIL_TIP_HALF, r0), (SLOT_HALF, r0), (SLOT_HALF, -0.1)]
    into, face = i.into(side), i.face(side)
    points = [cq.Vector(x + u, face + into * depth, bottom) for u, depth in section]
    wire = cq.Wire.makePolygon(points + [points[0]])
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire),
                                  cq.Vector(0.0, 0.0, top - bottom))


def magnet(i, side, x, z):
    """Nominal purchased block with its two side grooves, pulled onto its rails: pole
    face on the pole plane."""
    half = BAR / 2.0
    y0, y1 = i.at(side, -i.proud, THICKNESS - i.proud)
    body = _box(x - half, x + half, y0, y1, z - half, z + half)
    gy0, gy1 = i.at(side, GROOVE_FRONT - i.proud, GROOVE_FRONT + GROOVE_HEIGHT - i.proud)
    neck = GROOVED_WIDTH / 2.0
    for sign in (-1, 1):
        gx0, gx1 = _span(x + sign * neck, x + sign * (half + 0.1))
        body = body.cut(_box(gx0, gx1, gy0, gy1, z - half - 0.1, z + half + 0.1))
    return body.clean()


def features(holes, moving_face_y, fixed_face_y):
    """Production integration API, per side: cut `cutter` from the mating part.
    `magnets` are named reference solids, not printed geometry."""
    i = interface(holes, moving_face_y, fixed_face_y)
    out = {"interface": i, "dimensions": dimensions(i)}
    for side in ("moving", "fixed"):
        cutters, magnets = [], {}
        for col, (x, z) in enumerate(column_stations(i.holes), start=1):
            cutters.append(slot(i, side, x, z))
            for row in range(ROWS_PER_COLUMN):
                magnets[f"pump-dock-SB443-{side}-{col}-{row + 1}"] = magnet(
                    i, side, x, row_z(z, row))
        out[side] = {"cutter": _fused(cutters), "magnets": magnets}
    return out


def dimensions(i):
    bottom, top = column_limits(0.0)
    r0, r1 = i.rail_depths
    columns = column_stations(i.holes)
    return {"magnet": "K&J SB443-IN", "magnets_per_half": len(stations(i.holes)),
            "columns_per_half": len(columns),
            "rows_per_column": ROWS_PER_COLUMN,
            "column_axes_xz_mm": columns,
            "nominal_bar_mm": [BAR, THICKNESS, BAR],
            "frame_faces_y_mm": [i.moving_face_y, i.fixed_face_y],
            "frame_gap_mm": i.frame_gap,
            "pole_plane_y_mm": i.pole_y,
            "pole_proud_pulled_mm": i.proud,
            "pole_proud_pushed_mm": i.pushed_proud,
            "slot_width_mm": 2 * SLOT_HALF,
            "rail_mm": {"depths_from_face": [r0, r1], "thickness": RAIL,
                        "tip_gap": 2 * RAIL_TIP_HALF, "tip_air": RAIL_TIP_AIR},
            "slot_depth_mm": i.floor_depth,
            "slot_floor_z_mm": [z + bottom for _x, z in columns],
            "first_layer_over_slot_z_mm": [z + top for _x, z in columns],
            "drawing_maximum_stack_air_mm": STACK_AIR,
            "nominal_stack_air_mm": top - bottom - ROWS_PER_COLUMN * BAR,
            "assembly": "Four blocks per slot dropped down the rails at one print pause per "
                        "part, alternating poles; the next layer closes over them",
            "magnet_pull_force_established": False,
            "customer_adjustment": False}
