"""Machine display cover and receiver with broad leaves and square retaining hooks.

Cover coordinates: X across the screen, Y up the screen, Z out of the face.
The receiver's display plane stands 30 degrees above the print bed.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if p.name == 'hardware').parent
sys.path[:0] = [str(HERE.parent), str(ROOT/'hardware/scripts'),
               str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
import display_cover as cover
from _cadq_export import export_assembly, note_write
from _materials import M_PETGF_BLACK, one_body
from flute_payload import cut

COVER_NAME = 'display-cover-retention-v2'
RECEIVER_NAME = 'display-receiver-retention-v2'
INSET = .9
WALL = cover.retention.WALL
LIP = 2*cover.retention.LIP
EXTRA_REACH = .5
ROOT_DEPTH = cover.retention.ROOT
SHOULDER_DEPTH = ROOT_DEPTH+cover.retention.LIP_START+EXTRA_REACH
LIP_LAND = cover.retention.LIP_LAND
NOSE_DEPTH = (cover.retention.DEPTH-cover.retention.ROOT
              -cover.retention.LIP_START-LIP_LAND)*LIP/cover.retention.LIP
TIP_DEPTH = SHOULDER_DEPTH+LIP_LAND+NOSE_DEPTH
SKIRT_OUTER = cover.retention.OUTER_X-INSET
ROOT_EDGE_STOCK = .5
ROOT_FILLET = .8
CORNER_X = cover.cover_x/2-cover.cover_corner_r
CORNER_Y = cover.cover_slope/2-cover.cover_corner_r
SPAN_LIMIT = 2*(CORNER_Y+math.sqrt(cover.cover_corner_r**2
                                -(SKIRT_OUTER+ROOT_EDGE_STOCK-CORNER_X)**2))
SPAN = math.floor(SPAN_LIMIT*2)/2
END_SLIP = .5
RUN = SPAN+2*END_SLIP
CATCH = cover.retention.CATCH
CATCH_EDGE = cover.retention.OUTER_X-1.2+cover.retention.LIP-1.0
NECK_X = cover.retention.NECK_X
OVERLAP = SKIRT_OUTER+LIP-CATCH_EDGE
INSERTION_SLIP = .1
FLEX_CLEARANCE = .6
FLEX_EDGE = SKIRT_OUTER-WALL-OVERLAP-INSERTION_SLIP-FLEX_CLEARANCE
BEARING_CLEARANCE = SHOULDER_DEPTH-CATCH
LEDGE_THICKNESS = 2.0
WIDTH = 142.0
HEIGHT = 98.0
FRAME_THICKNESS = 6.0
RECEIVER_DEPTH = max(15.0, TIP_DEPTH+1)
RECEIVER_HALF_RUN = RUN/2+4
PCB_WIDTH = 106.0+2*cover.dims.fits.slip
PCB_HEIGHT = 69.0+2*cover.dims.fits.slip
PCB_OFFSET = (.5, -1.0)
CHEEK_THICKNESS = 4.0
ANGLE = 30.0
BASE_Z = min(-HEIGHT/2*math.sin(math.radians(ANGLE))-FRAME_THICKNESS-1,
             -RECEIVER_HALF_RUN*math.sin(math.radians(ANGLE))
             -RECEIVER_DEPTH*math.cos(math.radians(ANGLE))-1)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def side_box(side, x0, x1, y0, y1, z0, z1):
    lo, hi = sorted((side*x0, side*x1))
    return box(lo, hi, y0, y1, z0, z1)


def skirt(side):
    x = SKIRT_OUTER
    profile = [(x-WALL, -ROOT_DEPTH), (x, -ROOT_DEPTH),
               (x, -SHOULDER_DEPTH), (x+LIP, -SHOULDER_DEPTH),
               (x+LIP, -SHOULDER_DEPTH-LIP_LAND), (x, -TIP_DEPTH),
               (x-WALL, -TIP_DEPTH)]
    wire = cq.Wire.makePolygon([cq.Vector(side*px, -SPAN/2, z)
                               for px, z in [*profile, profile[0]]])
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, SPAN, 0))


def build_cover():
    bezel = cover.rounded_prism(cover.cover_x, cover.cover_slope,
                               cover.cover_corner_r, -ROOT_DEPTH, 0)
    window = cover.rounded_prism(cover.window_x, cover.window_slope,
                                cover.window_corner_r, -TIP_DEPTH-1, 1)
    body = bezel.fuse(skirt(-1), skirt(1)).cut(window).clean()
    roots = [e for e in body.Edges() if e.geomType() == 'LINE'
             and abs(e.Length()-SPAN) < 1e-6
             and abs(abs(e.Center().x)-(SKIRT_OUTER-WALL)) < 1e-6
             and abs(e.Center().z+ROOT_DEPTH) < 1e-6]
    assert len(roots) == 2
    return body.fillet(ROOT_FILLET, roots).clean()


def display_cuts():
    d = cover.dims
    inset = cover.rounded_prism(d.display_inset_x, d.display_inset_slope,
                                d.display_inset_corner_r, -d.display_inset_depth, 1)
    glass = cover.rounded_prism(d.display_bezel_x+2*d.fits.slip,
                                d.display_bezel_slope+2*d.fits.slip,
                                d.display_corner_r+d.fits.slip, -d.display_bezel_depth, 1)
    pcb = box(PCB_OFFSET[0]-PCB_WIDTH/2, PCB_OFFSET[0]+PCB_WIDTH/2,
              PCB_OFFSET[1]-PCB_HEIGHT/2, PCB_OFFSET[1]+PCB_HEIGHT/2,
              -RECEIVER_DEPTH-1, 1)
    return inset.fuse(glass, pcb)


def receiver_surround():
    body = box(-WIDTH/2, WIDTH/2, -HEIGHT/2, HEIGHT/2, -FRAME_THICKNESS, 0)
    for side in (-1, 1):
        body = body.fuse(side_box(side, 51, WIDTH/2, -RECEIVER_HALF_RUN,
                                 RECEIVER_HALF_RUN, -RECEIVER_DEPTH, 0))
    body = body.cut(display_cuts())
    for side in (-1, 1):
        slot = side_box(side, FLEX_EDGE, NECK_X, -RUN/2, RUN/2, -CATCH, 1)
        under = side_box(side, FLEX_EDGE, WIDTH/2+1, -HEIGHT/2-1, HEIGHT/2+1,
                         -RECEIVER_DEPTH-1, -CATCH)
        body = body.cut(slot.fuse(under))
        ledge = side_box(side, CATCH_EDGE, NECK_X+1, -RUN/2, RUN/2,
                         -CATCH, -CATCH+LEDGE_THICKNESS)
        body = body.fuse(ledge)
    return body.clean()


def print_pose(shape):
    return shape.rotate((0, 0, 0), (1, 0, 0), ANGLE).translate((0, 0, -BASE_Z))


def build_receiver():
    body = receiver_surround().rotate((0, 0, 0), (1, 0, 0), ANGLE)
    a = math.radians(ANGLE)
    underside = -FRAME_THICKNESS+.5
    ends = [(y*math.cos(a)-underside*math.sin(a),
             y*math.sin(a)+underside*math.cos(a)) for y in (-HEIGHT/2, HEIGHT/2)]
    front = -HEIGHT/2*math.cos(a)-1
    back = ends[1][0]+1
    profile = [(front, BASE_Z), (back, BASE_Z), (back, ends[1][1]),
               ends[1], ends[0]]
    for side in (-1, 1):
        x0 = -WIDTH/2 if side < 0 else WIDTH/2-CHEEK_THICKNESS
        wire = cq.Wire.makePolygon([cq.Vector(x0, y, z) for y, z in [*profile, profile[0]]])
        body = body.fuse(cq.Solid.extrudeLinear(wire, [], cq.Vector(CHEEK_THICKNESS, 0, 0)))
    body = body.fuse(box(-WIDTH/2, WIDTH/2, front, front+4, BASE_Z, BASE_Z+4))
    return body.clean().translate((0, 0, -BASE_Z))


def main():
    for name, build in [(COVER_NAME, build_cover), (RECEIVER_NAME, build_receiver)]:
        body = build()
        assert body.isValid() and len(body.Solids()) == 1
        out = HERE/(name+'.step')
        export_assembly(one_body(cq.Workplane(obj=body), name, M_PETGF_BLACK), str(out))
        body.copy(mesh=False).exportStl(str(out.with_suffix('.stl')),
                                      tolerance=.005, angularTolerance=.05, relative=False)
        note_write(out.with_suffix('.stl'))
        cut(out, out.with_suffix('.stl'))
        print(name, 'span', SPAN, 'hook', LIP, 'overlap', OVERLAP)
    values = {'LIP': LIP, 'SPAN': SPAN, 'INSET': INSET, 'WALL': WALL,
              'ROOT_EDGE_STOCK': ROOT_EDGE_STOCK, 'ROOT_FILLET': ROOT_FILLET,
              'OVERLAP': OVERLAP, 'MIN_OVERLAP': OVERLAP-cover.cover_slip,
              'BEARING_CLEARANCE': BEARING_CLEARANCE, 'NOSE_DEPTH': NOSE_DEPTH,
              'TIP_DEPTH': TIP_DEPTH, 'END_SLIP': END_SLIP, 'ANGLE': ANGLE}
    cover.substitute_md(HERE/'README.md', {key:f'{value:g} mm' for key,value in values.items()
                                          if key != 'ANGLE'} | {'ANGLE':f'{ANGLE:g}°'})


if __name__ == '__main__':
    main()
