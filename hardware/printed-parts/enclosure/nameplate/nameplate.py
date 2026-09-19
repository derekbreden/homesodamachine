"""104.53 × 38 mm horizontal nameplate, printed artwork-down in two-colour PET-GF.

The body and flush white artwork share a flat show face. Two integral tabs
project from the back into rigid shoulders in enclosure-back-top. The origin
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

import cadquery as cq
import qrcode
from cadquery.occ_impl.shapes import sortWiresByBuildOrder
from fontTools.pens.basePen import BasePen
from fontTools.svgLib.path import parse_path
from qrcode.util import MODE_ALPHA_NUM, QRData
from shapely.geometry import box as polygon_box
from shapely.ops import unary_union

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "enclosure"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(_hw.parent / "tools"))
from _cadq_export import export_assembly, export_step, _write_mesh_payload, _per_solid_color
from _materials import step_safe
from docgen import substitute_md
import _nameplate_interface as interface
import _nameplate_dimensions as _plan

WIDTH = interface.WIDTH
HEIGHT = interface.HEIGHT
THICK = interface.THICK
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
    assert qr.modules_count == 21
    return qr.get_matrix()


def build_qr(unit):
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
    polygons = [joined] if joined.geom_type == "Polygon" else joined.geoms
    def wire(ring):
        return cq.Wire.makePolygon([cq.Vector(WIDTH/2-QR_LEFT-x,THICK-INK_DEPTH,
                                             HEIGHT/2-QR_TOP-y)
                                    for x,y in ring.coords], close=True)
    parts = [cq.Solid.extrudeLinear(wire(p.exterior), [wire(r) for r in p.interiors],
                                    cq.Vector(0,INK_DEPTH,0)) for p in polygons]
    return cq.Compound.makeCompound(parts)


@lru_cache(maxsize=4)
def build_ink(unit):
    logo = _place(_upright(build_logo()), WIDTH/2-LOGO_LEFT, 0)
    return cq.Compound.makeCompound([logo, build_name(), build_qr(unit)])


@lru_cache(maxsize=1)
def blank_plate():
    body = (cq.Workplane("XY").rect(WIDTH, HEIGHT).extrude(THICK)
            .edges("|Z").fillet(CORNER_R).faces("<Z").chamfer(BEVEL).val()
            .rotate((0,0,0), (1,0,0), -90))
    body = body.fuse(*interface.tabs()).clean()
    # Round the two inner roots where flexure is highest. The outer roots
    # retain their full section against the straight receiving slot.
    roots = [e for e in body.Edges()
             if abs(e.Center().y) < 1e-6
             and abs(abs(e.Center().x)-(interface.TAB_X-interface.TAB_THICK/2)) < 1e-5
             and abs(e.Length()-interface.TAB_WIDTH) < 1e-5]
    if len(roots) != 2:
        raise ValueError(f"Expected two tab roots, found {len(roots)}")
    return body.fillet(interface.TAB_ROOT_R, roots).clean()


@lru_cache(maxsize=4)
def build_plate(unit):
    return blank_plate().cut(build_ink(unit)).clean()


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
    """Put the show face at bed Z=0 with the two tabs pointing upward."""
    return shape.rotate((0,0,0), (1,0,0), 90).rotate((0,0,0), (1,0,0), 180).translate((0,0,THICK))


def build_receiver():
    """A pocket-and-shoulders fit coupon using the production enclosure cutter."""
    shell = interface.box(-WIDTH/2-4, WIDTH/2+4, THICK-3, THICK,
                          -HEIGHT/2-4, HEIGHT/2+4)
    return interface.apply(shell, interface.station(0,0), THICK).clean()


def step_path(unit):
    return _here.parent / f"nameplate-{unit:03d}.step"


def selftest():
    body, ink = build_plate(1), build_ink(1)
    receiver = build_receiver()
    assert body.isValid() and len(body.Solids()) == 1
    assert receiver.isValid() and len(receiver.Solids()) == 1
    assert all(s.isValid() for s in ink.Solids())
    assert body.intersect(ink).Volume() < 1e-6
    assert body.intersect(receiver).Volume() < 1e-6
    assert abs(body.Volume()+ink.Volume()-blank_plate().Volume()) < 1e-5
    # The face seats at the pocket floor; it cannot travel farther inward.
    assert body.translate((0,-.1,0)).intersect(receiver).Volume() > 1
    # Outward travel stops at the lips, after their known bearing clearance.
    assert body.translate((0,interface.BEARING_SLIP+.1,0)).intersect(receiver).Volume() > .1
    # Deflected-tab clearance through the complete insertion stroke. This
    # geometric sweep does not estimate force or qualify PET-GF strain.
    for side,tab in zip((-1,1),interface.tabs()):
        slope = side*(interface.LIP-interface.SIDE_SLIP+.01)/interface.LIP_START
        bent = tab.transformGeometry(cq.Matrix([[1,slope,0,0],[0,1,0,0],
                                                [0,0,1,0],[0,0,0,1]]))
        for half_mm in range(20):
            assert bent.translate((0,half_mm*.5,0)).intersect(receiver).Volume() < 1e-6
    for unit in (1, 27, 9999):
        assert len(qr_matrix(unit)) == 21
        assert all(len(row) == 21 for row in qr_matrix(unit))
    # Full quiet-zone margins, with no mark or letter reaching into that field.
    quiet = interface.box(WIDTH/2-QR_LEFT-QR_ACTIVE-QR_QUIET,
                          WIDTH/2-QR_LEFT+QR_QUIET, THICK-INK_DEPTH,THICK,
                          -QR_ACTIVE/2-QR_QUIET, QR_ACTIVE/2+QR_QUIET)
    assert build_name().intersect(quiet).Volume() < 1e-6
    assert QR_LEFT+QR_ACTIVE+QR_QUIET <= WIDTH
    assert QR_TOP >= QR_QUIET
    posed = print_pose(cq.Compound.makeCompound([body, ink]))
    assert abs(posed.BoundingBox().zmin) < 1e-6
    bed = [f for f in posed.Faces() if abs(f.Center().z)<1e-6
           and abs(abs(f.normalAt().z)-1)<1e-6]
    area = WIDTH*HEIGHT-(4-math.pi)*CORNER_R**2
    assert abs(sum(f.Area() for f in bed)-area) < 1e-4
    print(json.dumps({"valid_body":True, "valid_receiver":True,
                      "body_receiver_overlap_mm3":body.intersect(receiver).Volume(),
                      "bed_contact_mm2":round(area,3),
                      "lip_engagement_mm":interface.LIP-interface.SIDE_SLIP,
                      "bearing_clearance_mm":interface.BEARING_SLIP,
                      "insertion_sweep":"20 poses per tab; no interference",
                      "qr":"version 1 / M / 21x21 / 1.1 mm modules",
                      "payload":_plan.unit_url(1)}, indent=2))
    return 0


def main(unit):
    _plan.serial_of(unit)
    part = build_part(unit)
    assert build_plate(unit).isValid() and all(s.isValid() for s in build_ink(unit).Solids())
    export_assembly(part, str(step_path(unit)))
    # A single-material STL records the physical exterior. The STEP/3MF retain
    # the two colour volumes; the viewer payload keeps those colours too.
    export_step(blank_plate(), str(step_path(unit).with_suffix(".stl")))
    if not os.environ.get("HSM_SKIP_MESH_PAYLOAD"):
        _write_mesh_payload(step_path(unit), _per_solid_color(part))
    if unit == 1:
        receiver = build_receiver()
        receiver_path = _here.with_name("nameplate-receiver.step")
        export_step(receiver, str(receiver_path))
        export_step(receiver, str(receiver_path.with_suffix(".stl")))
        if not os.environ.get("HSM_SKIP_MESH_PAYLOAD"):
            _write_mesh_payload(receiver_path, receiver)
    variables = {"PLATE_W":f"{WIDTH:g} mm", "PLATE_H":f"{HEIGHT:g} mm",
                 "NAMEPLATE_T":f"{THICK:g} mm", "INK_DEPTH":f"{INK_DEPTH:g} mm"}
    substitute_md(_here.with_name("README.md"), variables=variables)
    print(f"Nameplate {unit:04d}: {WIDTH:g} × {HEIGHT:g} × {THICK:g} mm; face-down PET-GF")
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



if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main(int(sys.argv[1]) if len(sys.argv)>1 else 1)
