#!/usr/bin/env python3
"""The app's HoldAtFaucet picture: a phone held to the faucet display the way people hold one
at a card reader, drawn as outlines.

The faucet head is the current source model, seen from the front and a little above, the way
the person holding the phone sees it: its display, the nozzle under it, and the arm running
back out of the picture. The phone is a prop, an outline lying parallel to the display a
little off its face, turned the way a right hand holds it, with its top corner over the
display. The arm fades where it leaves the head and the phone fades toward the hand. The
lines are hidden-line views of the solids, as in the kit drawings. The drawing is a template
image: the app colors it.
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
import _cad_art as art  # noqa: E402

ASSET = ROOT / 'ios/SodaMachine/SodaMachine/Assets.xcassets/HoldAtFaucet.imageset/HoldAtFaucet.svg'

ELEVATION = 15.0   # the view above level, degrees: the nozzle still shows under the display
PHONE = (71.6, 147.6, 7.8)   # a common phone's outline and thickness, mm
TWIST = 34.0       # the phone turned in its own plane, top toward the faucet, degrees
GAP = 20.0         # the phone's back off the display screen, mm
CORNER = 3.0       # the phone's nearest edge right of the screen's centre, in the view, mm
ARM = (25.0, 34.0) # the arm fading out, above the screen's centre in the view, mm
HAND = (0.40, 0.78)  # the phone fading out, as fractions of its length from its top
STROKE = 0.65      # line width, mm
MARGIN = 4.0       # space around the drawing, mm


def shape(obj):
    return obj.val() if hasattr(obj, 'val') else obj


def polylines(edges):
    if edges.IsNull():
        return []
    BRepLib.BuildCurves3d_s(edges, 1e-6)
    _, paths = getPaths([cq.Shape(edges)], [])
    lines = [[(float(x), float(y)) for x, y in re.findall(r'[ML]([-+\d.eE]+),([-+\d.eE]+)', path)]
             for path in paths]
    return [line for line in lines if len(line) > 1
            and sum(math.dist(a, b) for a, b in zip(line, line[1:])) > 0.5]


def clip(line, inside):
    """The parts of a polyline where inside(point) >= 0."""
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


def drawing() -> str:
    fa = art._load_faucet_module()
    parts = art._children_by_name(fa.build_assembly())
    # The display module is drawn by its screen alone; its body only hides what is behind it.
    head = {name: shape(parts[name].obj) for name in
            ('shell_tip', 'faucet-display-cover-seated', 'faucet_display', 'faucet_display_screen')}
    # The tubes only where they end, in the nozzle under the display.
    front = cq.Workplane('XY').box(200, 100, 400).translate((0, -150, 150)).val()
    head['nozzle'] = cq.Compound.makeCompound(
        [shape(parts[n].obj).intersect(front)
         for n in ('soda_faucet_tube', 'flavor_tube_pos_x', 'flavor_tube_neg_x')])

    box = head['faucet_display_screen'].BoundingBox()
    centre = cq.Vector((box.xmin + box.xmax) / 2, (box.ymin + box.ymax) / 2, (box.zmin + box.zmax) / 2)
    up = cq.Vector(0, box.ymax - box.ymin, box.zmax - box.zmin).normalized()
    normal = cq.Vector(0, -up.z, up.y)
    tilt = math.degrees(math.atan2(up.z, up.y))
    e = math.radians(ELEVATION)
    view_x, view_y = cq.Vector(1, 0, 0), cq.Vector(0, math.sin(e), math.cos(e))
    seen = lambda v: (v.dot(view_x), v.dot(view_y))

    w, h, t = PHONE
    body = (cq.Workplane('XY').box(w, h, t, centered=(True, True, False))
            .edges('|Z').fillet(10.5).edges('>Z or <Z').fillet(1.6)).val()
    island = (cq.Workplane('XY').workplane(offset=t).center(0, h / 2 - 11.6)
              .rect(19.5, 5.8).extrude(0.3).edges('|Z').fillet(2.85)).val()

    def placed(v, at):
        """A point of the phone, from its own frame to where it is held: turned about Z by
        TWIST, then tipped about X to the display's tilt, as the solids are below."""
        tw, tl = math.radians(TWIST), math.radians(tilt)
        x, y, z = v[0] * math.cos(tw) - v[1] * math.sin(tw), v[0] * math.sin(tw) + v[1] * math.cos(tw), v[2]
        return cq.Vector(x, y * math.cos(tl) - z * math.sin(tl), y * math.sin(tl) + z * math.cos(tl)) + at

    # Its outline's leftmost point in the view sits CORNER right of the screen's centre.
    r = 10.5
    rim = [(sx * (w / 2 - r) + r * math.cos(a), sy * (h / 2 - r) + r * math.sin(a), t)
           for sx, sy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270))
           for a in (math.radians(a0 + i) for i in range(0, 91, 3))]
    at = centre + normal * GAP
    left = min((seen(placed(v, at)) for v in rim), key=lambda p: p[0])
    goal = seen(centre)
    at = at + view_x * (goal[0] + CORNER - left[0]) + up * ((goal[1] - left[1]) / up.dot(view_y))
    phone = {name: s.rotate((0, 0, 0), (0, 0, 1), TWIST).rotate((0, 0, 0), (1, 0, 0), tilt)
             .translate(at.toTuple()) for name, s in (('body', body), ('island', island))}

    hlr = HLRBRep_Algo()
    for s in (*head.values(), *phone.values()):
        hlr.Add(s.wrapped)
    camera = (0, -math.cos(e), math.sin(e))
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(), gp_Dir(*camera), gp_Dir(1, 0, 0))))
    hlr.Update()
    hlr.Hide()
    lines = HLRBRep_HLRToShape(hlr)
    sharp = lambda s: polylines(lines.VCompound(s.wrapped))
    outline = lambda s: polylines(lines.OutLineVCompound(s.wrapped))

    screen = sharp(head['faucet_display_screen']) + outline(head['faucet_display_screen'])
    screen_top = max(y for line in screen for _, y in line)
    # The cover is drawn by its outline alone, without the edge where it meets the arm.
    cover = [line for line in outline(head['faucet-display-cover-seated'])
             if min(y for _, y in line) < screen_top]
    faucet = (sharp(head['shell_tip']) + outline(head['shell_tip']) + cover + screen
              + sharp(head['nozzle']) + outline(head['nozzle']))
    held = sum((sharp(s) + outline(s) for s in phone.values()), [])

    arm_fade, arm_end = (goal[1] + d for d in ARM)
    # Along the phone in the view: 0 at its top edge, 1 at its bottom edge.
    top, bottom = seen(placed((0, h / 2, t), at)), seen(placed((0, -h / 2, t), at))
    axis = (bottom[0] - top[0], bottom[1] - top[1])
    along = lambda p: ((p[0] - top[0]) * axis[0] + (p[1] - top[1]) * axis[1]) / (axis[0] ** 2 + axis[1] ** 2)
    on_phone = lambda f: (top[0] + axis[0] * f, top[1] + axis[1] * f)
    faucet = [piece for line in faucet for piece in clip(line, lambda p: arm_end - p[1])]
    held = [piece for line in held for piece in clip(line, lambda p: HAND[1] - along(p))]

    points = [p for line in faucet + held for p in line]
    left_x = min(x for x, _ in points) - MARGIN
    top_y = max(y for _, y in points) + STROKE
    width = max(x for x, _ in points) + MARGIN - left_x
    height = top_y - min(y for _, y in points) + MARGIN
    page = lambda p: (p[0] - left_x, top_y - p[1])
    d = lambda line: 'M' + ' L'.join('%.2f,%.2f' % page(p) for p in line)
    hand0, hand1 = page(on_phone(HAND[0])), page(on_phone(HAND[1]))
    return '\n'.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" height="{height:.1f}" '
        f'viewBox="0 0 {width:.2f} {height:.2f}">',
        '<defs>',
        f'<linearGradient id="arm" gradientUnits="userSpaceOnUse" x1="0" y1="{top_y - arm_end:.2f}" '
        f'x2="0" y2="{top_y - arm_fade:.2f}">'
        '<stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000"/>'
        '</linearGradient>',
        f'<linearGradient id="hand" gradientUnits="userSpaceOnUse" x1="{hand0[0]:.2f}" '
        f'y1="{hand0[1]:.2f}" x2="{hand1[0]:.2f}" y2="{hand1[1]:.2f}">'
        '<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#000" stop-opacity="0"/>'
        '</linearGradient>',
        '</defs>',
        f'<g fill="none" stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round">',
        '<g stroke="url(#arm)">', *(f'<path d="{d(line)}"/>' for line in faucet), '</g>',
        '<g stroke="url(#hand)">', *(f'<path d="{d(line)}"/>' for line in held), '</g>',
        '</g>', '</svg>', ''])


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ASSET
    out.write_text(drawing())
    print(out)
