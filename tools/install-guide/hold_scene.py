#!/usr/bin/env python3
"""Draw the app's phone-at-the-faucet illustration from the faucet's source solids.

The fixed front camera looks down 15 degrees. The phone lies parallel to the
display, turned 34 degrees toward the hand. A continuous housing silhouette,
the cover's front bezel and aperture, the recessed glass, and the three tube
mouths carry separate pen weights. The app supplies the template image's color.

Regenerate with tools/cad-venv/bin/python tools/install-guide/hold_scene.py.
An optional output path writes a study without replacing the app asset.
"""
from pathlib import Path
import math
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
sys.path.insert(0, str(HARDWARE / 'install-guide'))
os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')

import cadquery as cq  # noqa: E402
from cadquery.occ_impl.exporters.svg import getPaths  # noqa: E402
from OCP.BRepLib import BRepLib  # noqa: E402
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt  # noqa: E402
from OCP.HLRAlgo import HLRAlgo_Projector  # noqa: E402
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape  # noqa: E402
from shapely import line_merge, union_all  # noqa: E402
from shapely.geometry import LineString, Polygon  # noqa: E402
import _cad_art as art  # noqa: E402

ASSET = ROOT / 'ios/SodaMachine/SodaMachine/Assets.xcassets/HoldAtFaucet.imageset/HoldAtFaucet.svg'
ELEVATION = 15.0
PHONE = (71.6, 147.6, 7.8)
TWIST = 34.0
GAP = 20.0
CORNER = 3.0
# Fixed image-plane registration keeps the camera, pan and scale stable.
LEFT = -19.012
WIDTH, HEIGHT = 143.48, 126.63
PHONE_FADE = (0.58, 0.78)


def projected(v):
    e = math.radians(ELEVATION)
    return v.x, v.y * math.sin(e) + v.z * math.cos(e)


def polylines(edges):
    if edges.IsNull():
        return []
    BRepLib.BuildCurves3d_s(edges, 1e-7)
    _, paths = getPaths([cq.Shape(edges)], [])
    return [[(float(x), float(y))
             for x, y in re.findall(r'[ML]([-+\d.eE]+),([-+\d.eE]+)', path)]
            for path in paths]


def visible_lines(shapes):
    """Project visible sharp edges and silhouettes, retaining their source bodies."""
    hlr = HLRBRep_Algo()
    for obj in shapes.values():
        hlr.Add(obj.wrapped)
    e = math.radians(ELEVATION)
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(
        gp_Pnt(), gp_Dir(0, -math.cos(e), math.sin(e)), gp_Dir(1, 0, 0))))
    hlr.Update()
    hlr.Hide()
    lines = HLRBRep_HLRToShape(hlr)
    return {name: {'sharp': polylines(lines.VCompound(obj.wrapped)),
                   'outline': polylines(lines.OutLineVCompound(obj.wrapped))}
            for name, obj in shapes.items()}


def wire_lines(wire):
    lines = visible_lines({'wire': wire})['wire']
    return lines['sharp'] + lines['outline']


def front_face(obj, normal):
    """The broad planar face looking along normal, independent of edge ordering."""
    return max((face for face in obj.Faces()
                if face.geomType() == 'PLANE' and face.normalAt().dot(normal) > 0.999),
               key=lambda face: face.Area())


def silhouette(shapes):
    """Union projected solid triangles so touching pieces share one outer contour."""
    triangles = []
    for obj in shapes:
        vertices, faces = obj.tessellate(0.025, 0.04)
        points = [projected(v) for v in vertices]
        for face in faces:
            triangle = Polygon([points[i] for i in face])
            if triangle.area > 1e-9:
                triangles.append(triangle)
    merged = union_all(triangles, grid_size=0.001)
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda poly: poly.area)
    return list(merged.exterior.simplify(0.008, preserve_topology=True).coords)


def clip(line, inside):
    """Keep the portions of a polyline for which inside(point) >= 0."""
    pieces, piece = [], [line[0]] if inside(line[0]) >= 0 else []
    for a, b in zip(line, line[1:]):
        fa, fb = inside(a), inside(b)
        if (fa >= 0) != (fb >= 0):
            k = fa / (fa - fb)
            cut = (a[0] + k * (b[0] - a[0]), a[1] + k * (b[1] - a[1]))
            if fa >= 0:
                pieces.append(piece + [cut])
                piece = []
            else:
                piece = [cut]
        if fb >= 0:
            piece.append(b)
    pieces.append(piece)
    return [p for p in pieces if len(p) > 1]


class Pen:
    def __init__(self, top):
        self.top = top
        self.occluder = None

    def page(self, p):
        return p[0] - LEFT, self.top - p[1]

    def curve(self, points, closed=False):
        """Smooth projected curves while retaining straight runs and hard joins."""
        points = [self.page(p) for p in points]
        if closed and math.dist(points[0], points[-1]) < 0.01:
            points = points[:-1]
        if len(points) < 2:
            return ''
        fmt = lambda p: f'{p[0]:.3f},{p[1]:.3f}'
        n = len(points)

        def tangent(i):
            if not closed and i in (0, n - 1):
                a, b = points[max(0, i - 1)], points[min(i + 1, n - 1)]
                length = math.dist(a, b)
                return ((b[0] - a[0]) / length, (b[1] - a[1]) / length) if length else (0, 0)
            a, b, c = points[(i - 1) % n], points[i], points[(i + 1) % n]
            u, v = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
            lu, lv = math.hypot(*u), math.hypot(*v)
            if min(lu, lv) < 1e-8:
                return 0, 0
            if (u[0] * v[0] + u[1] * v[1]) / (lu * lv) < math.cos(math.radians(32)):
                return 0, 0
            if lu > 1.25 and lv < 1.25:
                return u[0] / lu, u[1] / lu
            if lv > 1.25 and lu < 1.25:
                return v[0] / lv, v[1] / lv
            direction = u[0] / lu + v[0] / lv, u[1] / lu + v[1] / lv
            length = math.hypot(*direction)
            return direction[0] / length, direction[1] / length

        out = ['M' + fmt(points[0])]
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            a, b = points[i], points[j]
            length = math.dist(a, b)
            if length > 1.25:
                out.append('L' + fmt(b))
                continue
            ta, tb = tangent(i), tangent(j)
            c1 = a[0] + ta[0] * length / 3, a[1] + ta[1] * length / 3
            c2 = b[0] - tb[0] * length / 3, b[1] - tb[1] * length / 3
            out.append('C' + fmt(c1) + ' ' + fmt(c2) + ' ' + fmt(b))
        if closed:
            out.append('Z')
        return ' '.join(out)

    def paths(self, lines, simplify=0.009):
        lines = [LineString(line) for line in lines
                 if len(line) > 1 and LineString(line).length > 0.05]
        if not lines:
            return []
        merged = union_all(lines, grid_size=0.0005)
        if self.occluder is not None:
            merged = merged.difference(self.occluder)
        if merged.is_empty:
            return []
        merged = line_merge(merged)
        lines = [merged] if merged.geom_type == 'LineString' else list(merged.geoms)
        result = []
        for line in lines:
            if line.geom_type != 'LineString':
                continue
            points = list(line.simplify(simplify).coords)
            result.append(self.curve(points, math.dist(points[0], points[-1]) < 0.015))
        return result

    def group(self, lines, width, opacity=1, simplify=0.009):
        return (f'<g fill="none" stroke="currentColor" stroke-width="{width}" opacity="{opacity}">'
                + ''.join(f'<path d="{d}"/>' for d in self.paths(lines, simplify)) + '</g>')

    def region(self, region):
        polygons = [region] if region.geom_type == 'Polygon' else list(region.geoms)
        return ' '.join(self.curve(list(ring.coords), True)
                        for polygon in polygons if polygon.geom_type == 'Polygon'
                        for ring in (polygon.exterior, *polygon.interiors))


def drawing():
    fa = art._load_faucet_module()
    _, tip = fa.load_shell_pieces()
    head = {'tip': tip.val(), 'cover': fa.load_display_cover().val(),
            'display': fa.build_display_body().val(), 'screen': fa.build_display_screen().val()}
    front = cq.Workplane('XY').box(200, 100, 400).translate((0, -150, 150)).val()
    for name, obj in (('soda', fa.build_soda_faucet_tube()),
                      ('flavor_right', fa.build_flavor_faucet_run(1)),
                      ('flavor_left', fa.build_flavor_faucet_run(-1))):
        head[name] = obj.val().intersect(front)

    box = head['screen'].BoundingBox()
    centre = cq.Vector((box.xmin + box.xmax) / 2, (box.ymin + box.ymax) / 2, (box.zmin + box.zmax) / 2)
    up = cq.Vector(0, box.ymax - box.ymin, box.zmax - box.zmin).normalized()
    normal = cq.Vector(0, -up.z, up.y)
    tilt = math.degrees(math.atan2(up.z, up.y))
    view_y = cq.Vector(0, math.sin(math.radians(ELEVATION)), math.cos(math.radians(ELEVATION)))
    w, h, t = PHONE

    def placed(v, at):
        tw, tl = math.radians(TWIST), math.radians(tilt)
        x = v[0] * math.cos(tw) - v[1] * math.sin(tw)
        y = v[0] * math.sin(tw) + v[1] * math.cos(tw)
        return cq.Vector(x, y * math.cos(tl) - v[2] * math.sin(tl),
                         y * math.sin(tl) + v[2] * math.cos(tl)) + at

    r = 10.5
    rim = [(sx * (w / 2 - r) + r * math.cos(a), sy * (h / 2 - r) + r * math.sin(a), t)
           for sx, sy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270))
           for a in (math.radians(a0 + i) for i in range(0, 91, 3))]
    at = centre + normal * GAP
    left = min((projected(placed(v, at)) for v in rim), key=lambda p: p[0])
    goal = projected(centre)
    at += cq.Vector(goal[0] + CORNER - left[0], 0, 0) + up * ((goal[1] - left[1]) / up.dot(view_y))
    phone = (cq.Workplane('XY').box(w, h, t, centered=(True, True, False))
             .edges('|Z').fillet(10.5).edges('>Z or <Z').fillet(1.6)).val()
    phone = phone.rotate((0, 0, 0), (0, 0, 1), TWIST).rotate((0, 0, 0), (1, 0, 0), tilt).translate(at)
    phone_lines = visible_lines({'phone': phone})['phone']
    pen = Pen(max(y for line in phone_lines['outline'] for _, y in line) + 0.65)
    head_outline = silhouette([head[n] for n in ('tip', 'cover', 'display')])
    phone_outline = silhouette([phone])
    phone_path = pen.curve(phone_outline, True)
    # Clip the source geometry itself. CoreSVG then receives ordinary visible
    # paths; the foreground phone has no renderer-dependent knockout mask.
    pen.occluder = Polygon(phone_outline).buffer(0.1, join_style='round')
    head_fill = pen.region(Polygon(head_outline).difference(pen.occluder))

    # Broad external faces identify the visible feature loops without relying on
    # OpenCascade's ordering of a body's edges.
    _, up_gooseneck, tip_normal = fa.faucet_shell._tip_frame()
    end_normal = up_gooseneck.multiply(-1)
    bezel = front_face(head['cover'], tip_normal)
    glass = front_face(head['screen'], tip_normal)
    cap = front_face(head['tip'], end_normal)
    cap_centre = projected(cap.outerWire().Center())
    cap_back = [piece for line in wire_lines(cap.outerWire())
                for piece in clip(line, lambda p: p[1] - cap_centre[1])]
    mouths = {name: front_face(head[name], end_normal) for name in ('soda', 'flavor_left', 'flavor_right')}
    faucet_lines = visible_lines(head)
    walls = []
    for name, mouth in mouths.items():
        cx, _ = projected(mouth.Center())
        for line in faucet_lines[name]['sharp'] + faucet_lines[name]['outline']:
            length = sum(math.dist(a, b) for a, b in zip(line, line[1:]))
            if not 0.05 < length < 2:
                continue
            # At the two touching flavor ends only the outboard walls carry ink.
            if name != 'soda' and (sum(x for x, _ in line) / len(line) - cx) * cx <= 0:
                continue
            walls.append(line)

    def phone_point(x, y, z=t):
        return pen.page(projected(placed((x, y, z), at)))

    top, bottom = phone_point(0, h / 2), phone_point(0, -h / 2)
    origin = phone_point(0, 0, t + 0.025)
    axis_x, axis_y = phone_point(1, 0, t + 0.025), phone_point(0, 1, t + 0.025)
    matrix = ','.join(f'{v:.8f}' for v in (axis_x[0] - origin[0], axis_x[1] - origin[1],
                                          axis_y[0] - origin[0], axis_y[1] - origin[1], *origin))
    along = lambda f: (top[0] + (bottom[0] - top[0]) * f, top[1] + (bottom[1] - top[1]) * f)
    hand0, hand1 = (along(f) for f in PHONE_FADE)
    mask_bounds = f'maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="0" y="0" width="{WIDTH}" height="{HEIGHT}" mask-type="luminance"'
    return '\n'.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none">',
        '<title>Hold an iPhone to the faucet display</title>',
        '<desc>A measured front view of the faucet, its tapered display bezel and three separate outlets. The phone is angled toward the display.</desc>',
        '<defs>',
        '<linearGradient id="stem-ink" gradientUnits="userSpaceOnUse" x1="0" y1="1.4" x2="0" y2="8"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white"/></linearGradient>',
        f'<mask id="stem-exit" {mask_bounds}><rect width="160" height="160" fill="url(#stem-ink)"/></mask>',
        f'<linearGradient id="phone-ink" gradientUnits="userSpaceOnUse" x1="{hand0[0]}" y1="{hand0[1]}" x2="{hand1[0]}" y2="{hand1[1]}"><stop stop-color="white"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>',
        f'<mask id="phone-exit" {mask_bounds}><rect width="170" height="180" fill="url(#phone-ink)"/></mask>',
        '</defs>',
        '<g stroke-linecap="round" stroke-linejoin="round">',
        '<g mask="url(#stem-exit)">',
        f'<path d="{head_fill}" fill="currentColor" fill-rule="evenodd" fill-opacity=".025"/>',
        pen.group([head_outline], 0.64, simplify=0),
        pen.group(wire_lines(bezel.outerWire()), 0.46, 0.95),
        pen.group([line for wire in bezel.innerWires() for line in wire_lines(wire)], 0.30, 0.65),
        pen.group(wire_lines(glass.outerWire()), 0.38, 0.9),
        pen.group(cap_back, 0.32, 0.72),
        pen.group(wire_lines(mouths['soda'].outerWire()), 0.40, 0.95),
        pen.group([line for name in ('flavor_left', 'flavor_right')
                   for line in wire_lines(mouths[name].outerWire())], 0.30, 0.95),
        pen.group(walls, 0.24, 0.65),
        '</g>',
        '<g mask="url(#phone-exit)">',
        f'<path d="{phone_path}" fill="currentColor" fill-opacity=".018" stroke="currentColor" stroke-width=".60"/>',
        f'<rect x="-34.05" y="-72.05" width="68.1" height="144.1" rx="8.75" transform="matrix({matrix})" stroke="currentColor" stroke-width=".27" opacity=".65"/>',
        f'<rect x="-9.75" y="59.3" width="19.5" height="5.8" rx="2.85" transform="matrix({matrix})" stroke="currentColor" stroke-width=".38" opacity=".95"/>',
        '</g></g></svg>', ''])


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ASSET
    out.write_text(drawing())
    print(out)
