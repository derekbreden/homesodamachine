"""Support-free display bezel and a separate, production-oriented receiver trial.

X runs across the screen, Y up it and Z out of the visible face. The cover's
back and both wings share one bed plane. The glass seat follows that back plane.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path[:0] = [str(HERE.parent), str(HERE.parent/'retention-trial'), str(ROOT/'hardware/scripts')]
import display_cover as cover
import retention_trial as accepted
from _cadq_export import export_assembly, note_write
from _materials import one_body, M_PETGF_BLACK
from flute_payload import cut

NAME = 'display-cover-flat-wings'
RECEIVER = 'display-receiver-flat-wings'
THICK = 3.84
WING_THICK = 1.44
WING_REACH = 3.60
WING_SPAN = 70.0
WING_END_R = .60
fits = cover.dims.fits
FACE_X_AIR = .30
FACE_Y_AIR = fits.slip
# The bedded wing has a smooth top; the receiver's retaining roof is supported.
BEARING_RELIEF = .20
BEARING_AIR = fits.slip+fits.supported_surface+BEARING_RELIEF
# The bezel locates X; these tips do not need to register against slot ends.
TIP_AIR = FACE_X_AIR+.25
END_AIR = fits.slip
LIP_THICK = THICK-WING_THICK-BEARING_AIR
BACK = -THICK
GLASS_SEAT = BACK-2.0
WIDTH, HEIGHT, FRAME_THICK = 142.0, 98.0, 8.0
ANGLE = accepted.ANGLE
CHEEK = 4.0
BASE_Z = -HEIGHT/2*math.sin(math.radians(ANGLE))-FRAME_THICK-1


def box(x0, x1, y0, y1, z0, z1):
    return accepted.box(x0, x1, y0, y1, z0, z1)


def wing(side):
    # The inboard millimetre overlaps the continuous bezel side rail.
    reach = WING_REACH+1.0
    return cover.rounded_prism(reach, WING_SPAN, WING_END_R, BACK, BACK+WING_THICK).translate(
        (side*(cover.cover_x/2+(WING_REACH-1)/2), 0, 0))


def build_cover():
    bezel = cover.rounded_prism(cover.cover_x, cover.cover_slope, cover.cover_corner_r, BACK, 0)
    window = cover.rounded_prism(cover.window_x, cover.window_slope, cover.window_corner_r, BACK-1, 1)
    return bezel.fuse(wing(-1), wing(1)).cut(window).clean()


def receiver_surround():
    d = cover.dims
    body = box(-WIDTH/2, WIDTH/2, -HEIGHT/2, HEIGHT/2, -FRAME_THICK, 0)
    inset = cover.rounded_prism(cover.cover_x+2*FACE_X_AIR, cover.cover_slope+2*FACE_Y_AIR,
                               cover.cover_corner_r+FACE_Y_AIR, BACK, 1)
    glass = cover.rounded_prism(d.display_bezel_x+2*d.fits.slip, d.display_bezel_slope+2*d.fits.slip,
                               d.display_corner_r+d.fits.slip, GLASS_SEAT, 1)
    pcb = box(accepted.PCB_OFFSET[0]-accepted.PCB_WIDTH/2, accepted.PCB_OFFSET[0]+accepted.PCB_WIDTH/2,
              accepted.PCB_OFFSET[1]-accepted.PCB_HEIGHT/2, accepted.PCB_OFFSET[1]+accepted.PCB_HEIGHT/2,
              -FRAME_THICK-1, 1)
    body = body.cut(inset.fuse(glass, pcb))
    for side in (-1, 1):
        slot = accepted.side_box(side, cover.cover_x/2-.1, cover.cover_x/2+WING_REACH+TIP_AIR,
                                 -WING_SPAN/2-END_AIR, WING_SPAN/2+END_AIR,
                                 BACK, BACK+WING_THICK+BEARING_AIR)
        body = body.cut(slot)
    # Open each pocket through the frame in the actual print-down direction.
    # Its retaining lip remains, while no pocket floor traps support beneath it.
    for opening in support_exits():
        body = body.cut(opening)
    return body.clean()


def support_exits(inset=0., roof_drop=0., depth=None):
    """Swept pocket mouths; print-down is local (0, -sin(angle), -cos(angle))."""
    roof = BACK+WING_THICK+BEARING_AIR-roof_drop
    depth = roof+FRAME_THICK+2 if depth is None else depth
    shift_y = -depth*math.tan(math.radians(ANGLE))
    exits = []
    for side in (-1,1):
        xa,xb = sorted((side*(cover.cover_x/2-.1), side*(cover.cover_x/2+WING_REACH+TIP_AIR)))
        xa,xb = xa+inset,xb-inset
        y0,y1 = -WING_SPAN/2-END_AIR+inset,WING_SPAN/2+END_AIR-inset
        wire = cq.Wire.makePolygon([cq.Vector(x,y,roof) for x,y in
                                   ((xa,y0),(xb,y0),(xb,y1),(xa,y1),(xa,y0))])
        exits.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,shift_y,-depth)))
    return exits


def build_receiver():
    body = receiver_surround().rotate((0, 0, 0), (1, 0, 0), ANGLE)
    a = math.radians(ANGLE)
    underside = -FRAME_THICK+.5
    ends = [(y*math.cos(a)-underside*math.sin(a), y*math.sin(a)+underside*math.cos(a))
            for y in (-HEIGHT/2, HEIGHT/2)]
    front = -HEIGHT/2*math.cos(a)-1
    back = ends[1][0]+1
    profile = [(front, BASE_Z), (back, BASE_Z), (back, ends[1][1]), ends[1], ends[0]]
    for x0 in (-WIDTH/2, WIDTH/2-CHEEK):
        wire = cq.Wire.makePolygon([cq.Vector(x0, y, z) for y, z in [*profile, profile[0]]])
        body = body.fuse(cq.Solid.extrudeLinear(wire, [], cq.Vector(CHEEK, 0, 0)))
    body = body.fuse(box(-WIDTH/2, WIDTH/2, front, front+4, BASE_Z, BASE_Z+4))
    return body.clean().translate((0, 0, -BASE_Z))


def main(receiver_only=False):
    bezel, fixture = build_cover(), receiver_surround()
    assert bezel.isValid() and len(bezel.Solids()) == 1
    assert abs(bezel.intersect(fixture).Volume()) < 1e-6
    assert bezel.translate((0, 0, BEARING_AIR+.05)).intersect(fixture).Volume() > 1
    assert bezel.translate((0, 0, -.05)).intersect(fixture).Volume() > 1
    assert LIP_THICK >= 1.8-1e-6
    clearances = []
    for lateral in (-FACE_X_AIR, 0., FACE_X_AIR):
        placed = bezel.translate((lateral, 0, 0))
        assert abs(placed.intersect(fixture).Volume()) < 1e-6
        assert placed.translate((0, 0, BEARING_AIR+.05)).intersect(fixture).Volume() > 1
        clearances.append({'lateral_mm': lateral, 'seated_intersection_mm3': abs(placed.intersect(fixture).Volume())})
    # The optical window and the 1 mm gasket/1 mm glass stack have their own space.
    glass_shadow = cover.rounded_prism(cover.dims.display_bezel_x, cover.dims.display_bezel_slope,
                                      cover.dims.display_corner_r, GLASS_SEAT, BACK-.0001)
    assert abs(bezel.intersect(glass_shadow).Volume()) < 1e-6
    assert abs(bezel.mirror('YZ').cut(bezel).Volume()) < 1e-6
    assert abs(bezel.mirror('XZ').cut(bezel).Volume()) < 1e-6
    # Verify a continuous vertical exit from each pocket through the whole fixture,
    # including its bed-standing cheeks and crossbar. These are removal lanes, not
    # extra mating clearances; the bezel's own back land supplies the seating datum.
    printed_receiver = build_receiver()
    exits = []
    for void in support_exits(inset=.05,roof_drop=.02,depth=100):
        posed = void.rotate((0,0,0),(1,0,0),ANGLE).translate((0,0,-BASE_Z))
        blocked = abs(posed.intersect(printed_receiver).Volume())
        assert blocked < 1e-6,blocked
        exits.append({'print_down_blocked_volume_mm3':blocked})
    travel = []
    for axis,limits in ((0,(-FACE_X_AIR,FACE_X_AIR)),(1,(-FACE_Y_AIR,FACE_Y_AIR)),(2,(0.,BEARING_AIR))):
        for value,extra in ((limits[0],-.01),(limits[1],.01)):
            vector=[0.,0.,0.];vector[axis]=value
            overlap=abs(bezel.translate(vector).intersect(fixture).Volume())
            assert overlap<1e-6,(axis,value,overlap)
            vector[axis]=value+extra
            blocked=abs(bezel.translate(vector).intersect(fixture).Volume())
            assert blocked>1e-6,(axis,value,blocked)
            travel.append({'axis':'XYZ'[axis],'limit_mm':value,'at_limit_overlap_mm3':overlap,
                           'past_limit_overlap_mm3':blocked})
    if receiver_only:
        saved_cover = cq.importers.importStep(str(HERE/(NAME+'.step'))).val()
        assert abs(saved_cover.cut(bezel).Volume())+abs(bezel.cut(saved_cover).Volume()) < 1e-6
    exports = ((RECEIVER, printed_receiver),) if receiver_only else ((NAME, bezel), (RECEIVER, printed_receiver))
    for name, body in exports:
        assert body.isValid() and len(body.Solids()) == 1
        path = HERE/(name+'.step')
        export_assembly(one_body(cq.Workplane(obj=body), name, M_PETGF_BLACK), str(path))
        body.copy(mesh=False).exportStl(str(path.with_suffix('.stl')), tolerance=.005, angularTolerance=.05, relative=False)
        note_write(path.with_suffix('.stl'))
        cut(path, path.with_suffix('.stl'))
    paths = [Path(__file__), Path(cover.__file__), Path(accepted.__file__), Path(fits.__file__)] + [HERE/(n+e) for n in (NAME, RECEIVER) for e in ('.step', '.stl')]
    report = {'pass': True, 'cover_thickness_mm': THICK,
              'wing_thickness_mm': WING_THICK, 'wing_projection_mm': WING_REACH, 'wing_span_mm': WING_SPAN,
              'normal_clearance_mm': BEARING_AIR, 'receiver_lip_mm': LIP_THICK,
              'tip_air_mm': TIP_AIR, 'end_air_mm': END_AIR,
              'face_perimeter_air_mm':{'X':FACE_X_AIR,'Y':FACE_Y_AIR},
              'clearance_basis':{'fit':'static','base_mm':fits.slip,'retaining_roof_supported_surface_mm':fits.supported_surface,
                                 'normal_fit_trial_relief_mm':BEARING_RELIEF,
                                 'body_X_fit_trial_relief_per_side_mm':FACE_X_AIR-fits.slip,
                                 'sliding_extra_mm':0.,'low_force_extra_mm':0.,'bezel_back_datum_mm':0.},
              'pure_axis_travel_mm':{'X':2*FACE_X_AIR,'Y':2*FACE_Y_AIR,'Z':BEARING_AIR},
              'pure_axis_fit_checks':travel,'support_exit_checks':exits,
              'support_exit_policy':'Each wing pocket opens through the underside along print-down; the pocket floor is absent. Trees can rise from the bed and leave downward.',
              'nominal_capture_mm': WING_REACH-FACE_X_AIR,
              'minimum_capture_at_full_lateral_float_mm': WING_REACH-2*FACE_X_AIR,
              'minimum_tip_gap_at_full_lateral_float_mm': TIP_AIR-FACE_X_AIR,
              'lateral_fit_checks': clearances,
              'glass_gasket_intersection_mm3': abs(bezel.intersect(glass_shadow).Volume()),
              'cover_back_plane_mm': BACK, 'glass_seat_plane_mm': GLASS_SEAT,
              'display_recess_increase_mm': THICK-cover.dims.display_cover_thickness,
              'gasket_thickness_mm': 1.0, 'receiver_orientation_degrees': ANGLE,
              'main_enclosure_integration': 'Pending fit acceptance and complete display-module/back-housing clearance check at the 1.84 mm deeper seat.',
              'physical_qualification': 'Pending insertion flex, complete wing capture, relaxed flatness and shake retention. This trial does not inherit physical acceptance from the vertical-leaf cover.',
              'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (HERE/'geometry-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--receiver-only', action='store_true')
    main(parser.parse_args().receiver_only)
