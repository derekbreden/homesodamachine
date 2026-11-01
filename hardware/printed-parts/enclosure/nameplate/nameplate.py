"""104.53 × 38 mm horizontal nameplate, printed face up in two-colour PET-GF.

All white artwork rises 0.48 mm above the flat black face. Two horizontal
wings share the flat back and enter side pockets in enclosure-back-top. The origin
is the back of the plate; +Y points out of the enclosure, +Z up, and text reads
along -X when viewed from outside.

Run with a unit number (1..9999), or `selftest` to check the plate and receiver.
"""

import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "enclosure"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(_hw.parent / "tools"))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq
import qrcode
from fontTools.pens.basePen import BasePen
from fontTools.svgLib.path import parse_path
from qrcode.util import MODE_ALPHA_NUM, QRData
from shapely.geometry import box as polygon_box
from shapely.ops import unary_union

from _cadq_export import export_assembly, export_step, _write_mesh_payload, _per_solid_color
from _materials import M_PETGF_BLACK, one_body, step_safe
from docgen import substitute_md
import _nameplate_interface as interface
import _nameplate_wing_interface as wing_interface
import _nameplate_dimensions as _plan

WIDTH = interface.WIDTH
HEIGHT = interface.HEIGHT
THICK = wing_interface.THICK
ARTWORK_RISE = .48
CORNER_R = interface.CORNER_R
BEVEL = interface.BEVEL
SLIP = interface.SLIP
WALL = interface.WALL
INK_DEPTH = 0.72
LOGO_H = 25.0
QR_MODULE = 1.1
QR_ACTIVE = 21 * QR_MODULE
QR_QUIET = 4 * QR_MODULE
QR_LEFT = 76.39581168241278
QR_TOP = (HEIGHT-QR_ACTIVE)/2
LOGO_LEFT = 5.034188317587201
BLACK = (28, 30, 33)
WHITE = (222, 222, 219)
_BRAND_MARK = _hw.parent / "brand" / "mark.svg"
_SVG_C = 512.0


def seat():
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


def _upright(shape):
    return (shape.rotate((0, 0, 0), (1, 0, 0), 90.0)
                 .rotate((0, 0, 0), (0, 0, 1), 180.0))


def _place(shape, x_start, z_mid):
    bb = shape.BoundingBox()
    return shape.translate((x_start-bb.xmax, THICK-INK_DEPTH-bb.ymin,
                            z_mid-(bb.zmin+bb.zmax)/2))


class _OutlinePen(BasePen):
    """SVG curves into exact planar lines/Béziers on the wall's XZ plane."""
    def __init__(self, tx, ty):
        super().__init__(None)
        self.tx, self.ty = tx, ty
        self.wires = []

    def point(self, p):
        return cq.Vector(WIDTH/2-p[0]-self.tx, THICK-INK_DEPTH,
                         HEIGHT/2-p[1]-self.ty)

    def _moveTo(self, p):
        self.start = self.last = p
        self.edges = []

    def _lineTo(self, p):
        if p != self.last:
            self.edges.append(cq.Edge.makeLine(self.point(self.last), self.point(p)))
        self.last = p

    def _curveToOne(self, p1, p2, p3):
        self.edges.append(cq.Edge.makeBezier([self.point(p) for p in (self.last,p1,p2,p3)]))
        self.last = p3

    def _qCurveToOne(self, p1, p2):
        self.edges.append(cq.Edge.makeBezier([self.point(p) for p in (self.last,p1,p2)]))
        self.last = p2

    def _closePath(self):
        self._lineTo(self.start)
        self.wires.append(cq.Wire.assembleEdges(self.edges))

    def _endPath(self):
        raise ValueError("Nameplate lettering must have closed contours")


@lru_cache(maxsize=1)
def build_name():
    from cadquery.occ_impl.shapes import sortWiresByBuildOrder
    root = ET.parse(_here.with_name("wordmark.svg")).getroot()
    parts = []
    for group in root:
        if group.get("aria-label") not in ("HOME", "SODA", "MACHINE"):
            continue
        tx, ty = map(float, re.fullmatch(r"translate\(([-\d.]+) ([-\d.]+)\)",
                                       group.get("transform")).groups())
        pen = _OutlinePen(tx, ty)
        for child in group:
            parse_path(child.get("d"), pen)
        for outer, *inner in sortWiresByBuildOrder(pen.wires):
            parts.append(cq.Solid.extrudeLinear(outer, inner, cq.Vector(0,INK_DEPTH,0)))
    return cq.Compound.makeCompound(parts)


def qr_matrix(unit):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    qr.add_data(QRData(_plan.unit_url(unit), mode=MODE_ALPHA_NUM))
    qr.make(fit=False)
    return qr.get_matrix()


def _qr_polygons(unit):
    # Join diagonal-only white contacts by 0.02 mm, below the print resolution,
    # so the two-colour interface has closed manifold faces rather than two
    # cavity wires intersecting at a single point. The 1.1 mm pitch is exact.
    matrix = qr_matrix(unit)
    regions = []
    for row, cells in enumerate(matrix):
        col = 0
        while col < 21:
            if not cells[col]:
                col += 1
                continue
            end = col+1
            while end < 21 and cells[end]:
                end += 1
            regions.append(polygon_box(col*QR_MODULE, row*QR_MODULE,
                                       end*QR_MODULE, (row+1)*QR_MODULE))
            col = end
    for row in range(20):
        for col in range(20):
            a,b,c,d = matrix[row][col],matrix[row][col+1],matrix[row+1][col],matrix[row+1][col+1]
            if a == d and b == c and a != b:
                x,y = (col+1)*QR_MODULE, (row+1)*QR_MODULE
                regions.append(polygon_box(x-.01,y-.01,x+.01,y+.01))
    joined = unary_union(regions)
    return [joined] if joined.geom_type == "Polygon" else joined.geoms


def build_qr(unit):
    def wire(ring):
        return cq.Wire.makePolygon([cq.Vector(WIDTH/2-QR_LEFT-x,THICK-INK_DEPTH,
                                             HEIGHT/2-QR_TOP-y)
                                    for x,y in ring.coords], close=True)
    parts = [cq.Solid.extrudeLinear(wire(p.exterior), [wire(r) for r in p.interiors],
                                    cq.Vector(0,INK_DEPTH,0)) for p in _qr_polygons(unit)]
    return cq.Compound.makeCompound(parts)


@lru_cache(maxsize=4)
def build_inlay(unit):
    logo = _place(_upright(build_logo()), WIDTH/2-LOGO_LEFT, 0)
    return cq.Compound.makeCompound([logo, build_name(), build_qr(unit)])


@lru_cache(maxsize=4)
def build_ink(unit):
    return cq.Compound.makeCompound([
        s.fuse(s.translate((0,ARTWORK_RISE,0))).clean()
        for s in build_inlay(unit).Solids()])


@lru_cache(maxsize=1)
def blank_plate():
    return wing_interface.blank()


@lru_cache(maxsize=4)
def build_plate(unit):
    return blank_plate().cut(build_inlay(unit)).clean()


def _filament(rgb):
    return step_safe(cq.Color(*(c/255 for c in rgb)))


def build_part(unit):
    a = cq.Assembly()
    a.add(build_plate(unit), name=f"nameplate-{unit:03d}", color=_filament(BLACK))
    a.add(build_ink(unit), name=f"nameplate-{unit:03d}-ink", color=_filament(WHITE))
    return a


def split(shape):
    solids = shape.Solids()
    body = [s for s in solids if s.BoundingBox().ymin < 1e-6]
    if len(body) != 1:
        raise ValueError(f"Expected one nameplate body, found {len(body)}")
    return body[0], cq.Compound.makeCompound([s for s in solids if s is not body[0]])


def print_pose(shape):
    """The full plate back and both horizontal wings lie on the bed."""
    return shape.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),180)


def build_receiver():
    return wing_interface.receiver()


def step_path(unit):
    return _here.parent / f"nameplate-{unit:03d}.step"


def selftest():
    import _rust_part
    print(json.dumps(_rust_part.check("enclosure-components", "nameplate", numbers(1)), indent=2))
    return 0


def main(unit):
    _plan.serial_of(unit)
    import _rust_part
    _rust_part.cut("enclosure-components", "nameplate", numbers(unit), _here.parent,
                   numbers_name=None if unit == 1 else f"nameplate-{unit:03d}")
    variables = {"PLATE_W":f"{WIDTH:g} mm", "PLATE_H":f"{HEIGHT:g} mm",
                 "NAMEPLATE_T":f"{THICK:g} mm", "INK_DEPTH":f"{INK_DEPTH:g} mm",
                 "TAB_PITCH":f"{2*interface.TAB_X:g} mm",
                 "TAB_TO_END":f"{WIDTH/2-interface.TAB_X:.1f} mm",
                 "SHOULDER_W":f"{interface.SHOULDER_W:g} mm",
                 "SHOULDER_STOCK":f"{interface.SHOULDER_STOCK:g} mm",
                 "BAR_FRAME":f"{interface.BAR_FRAME:g} mm",
                 "POCKET_FLOOR":f"{WALL-THICK:g} mm"}
    substitute_md(_here.with_name("README.md"), variables=variables)
    print(f"Nameplate {unit:04d}: {WIDTH:g} × {HEIGHT:g} × {THICK:g} mm; face-up PET-GF")
    print(f"QR: {_plan.unit_url(unit)}, version 1/M, 21×21 modules at {QR_MODULE:g} mm")

def _icon_xy(p, scale):
    """One icon point in the plate's flat XY frame, centred on the mark's own centre."""
    return ((p[0] - _SVG_C) * scale, -(p[1] - _SVG_C) * scale)


class _FaucetPen:
    """Read the master path's lines and semicircles into one explicitly closed CAD wire."""

    def moveTo(self, point):
        self.point = point
        self.path = cq.Workplane("XY").moveTo(*_icon_xy(point, 1.0))

    def lineTo(self, point):
        self.path = self.path.lineTo(*_icon_xy(point, 1.0))
        self.point = point

    def arcTo(self, rx, ry, rotation, large, sweep, point):
        dx, dy = point[0] - self.point[0], point[1] - self.point[1]
        if not (math.isclose(rx, ry) and math.isclose(rotation, 0.0)
                and math.isclose(math.hypot(dx, dy), 2.0 * rx)):
            raise ValueError("The faucet master must use unrotated circular semicircles")
        direction = 1.0 if sweep else -1.0
        midpoint = ((self.point[0] + point[0] + direction * dy) / 2.0,
                    (self.point[1] + point[1] - direction * dx) / 2.0)
        self.path = self.path.threePointArc(_icon_xy(midpoint, 1.0),
                                           _icon_xy(point, 1.0))
        self.point = point

    def closePath(self):
        # parse_path supplies the explicit final line back to the start before this call.
        self.wire = self.path.wire().val()

    def endPath(self):
        raise ValueError("The faucet master must be a closed silhouette")


def build_logo(height: float = LOGO_H):
    """The master faucet and drop at their visible height, filled `INK_DEPTH` thick."""
    root = ET.parse(_BRAND_MARK).getroot()
    faucet = root.find(".//*[@id='faucet']")
    drop = root.find(".//*[@id='drop']")
    if faucet is None or drop is None:
        raise ValueError("The brand master must contain the faucet path and drop circle")
    pen = _FaucetPen()
    parse_path(faucet.attrib["d"], pen)
    center = _icon_xy((float(drop.attrib["cx"]), float(drop.attrib["cy"])), 1.0)
    circle = cq.Workplane("XY").center(*center).circle(float(drop.attrib["r"])).val()
    wires = (pen.wire, circle)
    scale = height / cq.Compound.makeCompound(wires).BoundingBox().ylen
    return cq.Compound.makeCompound([
        cq.Workplane("XY").add(wire.scale(scale)).toPending().extrude(INK_DEPTH).val()
        for wire in wires
    ])


def logo_width(height: float = LOGO_H) -> float:
    return build_logo(height).BoundingBox().xlen


class _NumbersPen(BasePen):
    """The SVG's own line and Bézier control points, in the plate's X/Z frame."""

    def __init__(self, point=lambda p: list(p)):
        super().__init__(None)
        self.point = point
        self.loops = []

    def _moveTo(self, p):
        self.start = self.last = p
        self.segments = []

    def _lineTo(self, p):
        if p != self.last:
            self.segments.append({'line': [self.point(q) for q in (self.last, p)]})
        self.last = p

    def _curveToOne(self, p1, p2, p3):
        self.segments.append({'cubic': [self.point(q) for q in (self.last, p1, p2, p3)]})
        self.last = p3

    def _qCurveToOne(self, p1, p2):
        self.segments.append({'quad': [self.point(q) for q in (self.last, p1, p2)]})
        self.last = p2

    def arcTo(self, rx, ry, rotation, large, sweep, p):
        dx, dy = p[0] - self.last[0], p[1] - self.last[1]
        if not (math.isclose(rx, ry) and math.isclose(rotation, 0.)
                and math.isclose(math.hypot(dx, dy), 2. * rx)):
            raise ValueError("The faucet master must use unrotated circular semicircles")
        direction = 1. if sweep else -1.
        middle = ((self.last[0] + p[0] + direction * dy) / 2.,
                  (self.last[1] + p[1] - direction * dx) / 2.)
        self.segments.append({'arc': [self.point(q) for q in (self.last, middle, p)]})
        self.last = p

    def _closePath(self):
        self._lineTo(self.start)
        self.loops.append(self.segments)

    def _endPath(self):
        raise ValueError("Nameplate artwork must have closed contours")


def _wordmark_numbers():
    root = ET.parse(_here.with_name("wordmark.svg")).getroot()
    groups = []
    for group in root:
        if group.get("aria-label") not in ("HOME", "SODA", "MACHINE"):
            continue
        tx, ty = map(float, re.fullmatch(r"translate\(([-\d.]+) ([-\d.]+)\)",
                                       group.get("transform")).groups())
        pen = _NumbersPen(lambda p: [WIDTH/2-p[0]-tx, HEIGHT/2-p[1]-ty])
        for child in group:
            parse_path(child.get("d"), pen)
        groups.append(pen.loops)
    return groups


def _logo_numbers():
    root = ET.parse(_BRAND_MARK).getroot()
    faucet = root.find(".//*[@id='faucet']")
    drop = root.find(".//*[@id='drop']")
    if faucet is None or drop is None:
        raise ValueError("The brand master must contain the faucet path and drop circle")
    pen = _NumbersPen()
    parse_path(faucet.get('d'), pen)
    cx, cy, radius = (float(drop.get(k)) for k in ('cx', 'cy', 'r'))
    # The retained master has horizontal semicircles. Their middle points carry
    # their extrema, so these are the same exact bounds as build_logo's wires.
    points = [p for loop in pen.loops for seg in loop for pts in seg.values() for p in pts]
    points += [[cx-radius, cy-radius], [cx+radius, cy+radius]]
    left, right = min(p[0] for p in points), max(p[0] for p in points)
    bottom, top = min(p[1] for p in points), max(p[1] for p in points)
    scale = LOGO_H / (top-bottom)
    def point(p):
        return [WIDTH/2-LOGO_LEFT-(p[0]-left)*scale,
                ((bottom+top)/2-p[1])*scale]
    pen = _NumbersPen(point)
    parse_path(faucet.get('d'), pen)
    return {'faucet': pen.loops[0], 'drop_center': point((cx, cy)),
            'drop_radius': radius*scale, 'width': (right-left)*scale}


def numbers(unit=1):
    """The accepted artwork, flat wings and receiver coupon in millimetres."""
    from _materials import linear
    _plan.serial_of(unit)
    wing = wing_interface
    pw, ph = WIDTH+2*wing.FACE_SLIP, HEIGHT+2*wing.FACE_SLIP
    margin = max(2., wing.FLOOR_STOCK)
    rear = -wing.FLOOR_STOCK-wing.BACK_AIR
    zedge = ph/2+margin
    z0 = -wing.WING_SPAN/2-wing.END_AIR-wing.SUPPORTED_END_AIR
    z1 = wing.WING_SPAN/2+wing.END_AIR
    roof = wing.WING_THICK+wing.THICKNESS_AIR
    qr = []
    for polygon in _qr_polygons(unit):
        qr.append([[[WIDTH/2-QR_LEFT-x, HEIGHT/2-QR_TOP-y] for x, y in ring.coords]
                   for ring in (polygon.exterior, *polygon.interiors)])
    return {
        'name': f'nameplate-{unit:03d}', 'unit': unit, 'payload': _plan.unit_url(unit),
        'width': WIDTH, 'height': HEIGHT, 'thick': THICK, 'corner': CORNER_R,
        'wing_projection': wing.PROJECTION, 'wing_span': wing.WING_SPAN,
        'wing_thick': wing.WING_THICK, 'wing_corner': wing.END_RADIUS,
        'ink_depth': INK_DEPTH, 'artwork_rise': ARTWORK_RISE,
        'black': list(linear(_filament(BLACK))), 'white': list(linear(_filament(WHITE))),
        'receiver_color': list(linear(M_PETGF_BLACK)),
        'wordmark': _wordmark_numbers(), 'logo': _logo_numbers(), 'qr': qr,
        'qr_quiet': [WIDTH/2-QR_LEFT-QR_ACTIVE-QR_QUIET,
                     WIDTH/2-QR_LEFT+QR_QUIET, THICK-INK_DEPTH, THICK+ARTWORK_RISE,
                     -QR_ACTIVE/2-QR_QUIET, QR_ACTIVE/2+QR_QUIET],
        'qr_fits': QR_LEFT+QR_ACTIVE+QR_QUIET <= WIDTH and QR_TOP >= QR_QUIET,
        'receiver': {
            'shell': [-WIDTH/2-wing.PROJECTION-3., WIDTH/2+wing.PROJECTION+3.,
                      THICK-3., THICK, -HEIGHT/2-4., HEIGHT/2+4.],
            'pad_width': pw+2*(wing.PROJECTION+2.),
            'pad_height': ph+2.+margin, 'pad_corner': CORNER_R+2.,
            'pad_y': [rear, THICK], 'pad_z': (margin-2.)/2.,
            'ramp_yz': [[rear, zedge], [rear, zedge-wing.FLOOR_STOCK],
                        [-wing.BACK_AIR, zedge]], 'ramp_x': [-pw, pw],
            'mouth_width': WIDTH+2*wing.FACE_X_AIR, 'mouth_height': ph,
            'mouth_corner': CORNER_R+wing.FACE_SLIP,
            'mouth_y': [-wing.BACK_AIR, THICK+1.],
            'mouth_shift_z': -wing.SUPPORTED_END_AIR,
            'slots': [[min(side*(WIDTH/2-.1), side*(WIDTH/2+wing.PROJECTION+wing.TIP_AIR)),
                       max(side*(WIDTH/2-.1), side*(WIDTH/2+wing.PROJECTION+wing.TIP_AIR)),
                       -wing.BACK_AIR, roof, z0, z1] for side in (-1, 1)],
            'bevels_xy': [[[side*(WIDTH/2+wing.FACE_SLIP), roof],
                          [side*(WIDTH/2+wing.FACE_SLIP+wing.ENTRY_BEVEL_WIDTH), roof],
                          [side*(WIDTH/2+wing.FACE_SLIP), roof+wing.ENTRY_BEVEL_DEPTH]]
                         for side in (-1, 1)],
            'slot_z': [z0, z1],
            'diamond_xz': [[-9., 0.], [0., -10.], [9., 0.], [0., 10.]],
            'diamond_y': [rear-.5, .5],
            'thickness_air': wing.THICKNESS_AIR,
        },
    }



if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main(int(sys.argv[1]) if len(sys.argv)>1 else 1)
