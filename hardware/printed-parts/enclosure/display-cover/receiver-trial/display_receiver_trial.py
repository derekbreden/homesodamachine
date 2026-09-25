"""Full-width machine-display receiver coupon for the 1.2 mm inset cover.

The display plane is 30 degrees above the bed, as on front-top. The upper slots
retain their outer walls. A short ledge at each hook and a wider inward flex lane
form the trial receivers. Two side cheeks and a front foot carry the surround.
"""

import json
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if p.name == 'hardware').parent
sys.path[:0] = [str(ROOT / 'hardware/scripts'),
               str(ROOT / 'hardware/printed-parts/enclosure/enclosure')]
from _cadq_export import export_assembly, note_write
from _materials import M_PETGF_BLACK, one_body
import _enclosure_interface as dims
import _display_retention as retention
from _swept_top import ANGLE, rounded_prism

NAME = 'display-receiver-trial-v1'
COVER_INSET = 1.2
OVERLAP = 1.0
SKIRT_OUTER = retention.OUTER_X - COVER_INSET
CATCH_EDGE = SKIRT_OUTER + retention.LIP - OVERLAP
FLEX_EDGE = SKIRT_OUTER - retention.WALL - 1.6
LEDGE_THICKNESS = 2.0
WIDTH = 142.0
HEIGHT = 98.0
FRAME_THICKNESS = 6.0
RECEIVER_DEPTH = 15.0
RECEIVER_HALF_RUN = retention.RUN / 2.0 + 4.0
PCB_WIDTH = 106.0 + 2.0 * dims.fits.slip
PCB_HEIGHT = 69.0 + 2.0 * dims.fits.slip
PCB_OFFSET = (0.5, -1.0)
CHEEK_THICKNESS = 4.0
BASE_Z = -HEIGHT / 2.0 * math.sin(math.radians(ANGLE)) - FRAME_THICKNESS - 1.0


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def side_box(side, x0, x1, y0, y1, z0, z1):
    lo, hi = sorted((side*x0, side*x1))
    return box(lo, hi, y0, y1, z0, z1)


def display_cuts():
    inset = rounded_prism(dims.display_inset_x, dims.display_inset_slope,
                          dims.display_inset_corner_r, -dims.display_inset_depth, 1.0)
    glass = rounded_prism(dims.display_bezel_x + 2*dims.fits.slip,
                          dims.display_bezel_slope + 2*dims.fits.slip,
                          dims.display_corner_r + dims.fits.slip,
                          -dims.display_bezel_depth, 1.0)
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
        slot = side_box(side, FLEX_EDGE, retention.NECK_X,
                        -retention.RUN/2, retention.RUN/2, -retention.CATCH, 1)
        underneath = side_box(side, FLEX_EDGE, WIDTH/2+1,
                              -HEIGHT/2-1, HEIGHT/2+1,
                              -RECEIVER_DEPTH-1, -retention.CATCH)
        body = body.cut(slot.fuse(underneath))
        ledge = side_box(side, CATCH_EDGE, retention.NECK_X+1,
                         -retention.RUN/2, retention.RUN/2,
                         -retention.CATCH, -retention.CATCH+LEDGE_THICKNESS)
        body = body.fuse(ledge)
    return body.clean()


def print_pose(shape):
    return shape.rotate((0, 0, 0), (1, 0, 0), ANGLE).translate((0, 0, -BASE_Z))


def build():
    body = receiver_surround().rotate((0, 0, 0), (1, 0, 0), ANGLE)
    a = math.radians(ANGLE)
    underside = -FRAME_THICKNESS + 0.5
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
    body = build()
    if not body.isValid() or len(body.Solids()) != 1:
        raise ValueError('The coupon must be one valid solid')
    out = HERE / (NAME + '.step')
    export_assembly(one_body(cq.Workplane(obj=body), NAME, M_PETGF_BLACK), str(out))
    body.copy(mesh=False).exportStl(str(out.with_suffix('.stl')),
                                  tolerance=.005, angularTolerance=.05, relative=False)
    note_write(out.with_suffix('.stl'))
    from flute_payload import cut
    cut(out, out.with_suffix('.stl'))
    bb = body.BoundingBox()
    print(json.dumps({'part': NAME, 'bounds_mm': [bb.xlen, bb.ylen, bb.zlen],
                      'volume_mm3': body.Volume(), 'nominal_overlap_mm': OVERLAP,
                      'minimum_overlap_at_lateral_float_mm': OVERLAP-dims.display_cover_slip,
                      'upper_outside_skirt_clearance_mm': retention.NECK_X-SKIRT_OUTER,
                      'outside_skirt_clearance_at_ledge_mm': CATCH_EDGE-SKIRT_OUTER,
                      'inward_flex_clearance_mm': SKIRT_OUTER-retention.WALL-FLEX_EDGE,
                      'bearing_clearance_mm': retention.BEARING_SLIP,
                      'display_plane_angle_degrees': ANGLE}, indent=2))


if __name__ == '__main__':
    main()
