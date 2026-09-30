"""Support-free face-up nameplate with coplanar wings and a matching receiver coupon."""
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
import wing_interface as interface

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path.insert(0,str(HERE.parent))
import nameplate as plate

NAME = 'nameplate-horizontal-wings-001'
RECEIVER = 'nameplate-horizontal-wings-receiver'
ARTWORK_RISE = .48


def print_pose(shape):
    return shape.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),180)


def main():
    blank,fixture = interface.blank(),interface.receiver()
    original = plate.build_ink(1).translate((0,interface.THICK-plate.THICK,0))
    black = blank.cut(original).clean()
    white = cq.Compound.makeCompound([s.fuse(s.translate((0,ARTWORK_RISE,0))).clean()
                                      for s in original.Solids()])
    exterior = black.fuse(*white.Solids()).clean()
    for solid in (black,exterior,fixture):
        assert solid.isValid() and len(solid.Solids())==1
    assert black.intersect(white).Volume()<1e-6
    assert exterior.intersect(fixture).Volume()<1e-6
    assert exterior.translate((0,-.1,0)).intersect(fixture).Volume()>1
    assert exterior.translate((0,interface.THICKNESS_AIR+.1,0)).intersect(fixture).Volume()>1
    assert abs(print_pose(exterior).BoundingBox().zmin)<1e-6
    assert len(white.Solids())==len(original.Solids())==29
    assert all(abs(s.BoundingBox().ymax-(interface.THICK+ARTWORK_RISE))<1e-6 for s in white.Solids())
    assert abs(interface.THICK-interface.FIELD_THICK)<1e-6
    assert interface.THICK-interface.WING_THICK-interface.THICKNESS_AIR>=1.2-1e-6
    # All artwork remains within the flat face with its original planar contours.
    ib=white.BoundingBox()
    assert max(abs(ib.xmin),abs(ib.xmax))<plate.WIDTH/2
    assert max(abs(ib.zmin),abs(ib.zmax))<plate.HEIGHT/2
    # Both wing bearing planes share the first-layer plane with the complete plate back.
    posed = print_pose(exterior)
    bed_area = sum(f.Area() for f in posed.Faces() if abs(f.Center().z)<1e-6
                   and f.geomType()=='PLANE' and abs(f.normalAt().z)>.999)
    assert bed_area>plate.WIDTH*plate.HEIGHT
    assembly=cq.Assembly()
    assembly.add(black,name=NAME,color=plate._filament(plate.BLACK))
    assembly.add(white,name=NAME+'-ink',color=plate._filament(plate.WHITE))
    coupon=plate.one_body(fixture,RECEIVER,plate.M_PETGF_BLACK)
    for name,part,body in ((NAME,assembly,exterior),(RECEIVER,coupon,fixture)):
        path=HERE/(name+'.step')
        plate.export_assembly(part,str(path))
        plate.export_step(body,str(path.with_suffix('.stl')))
        plate._write_mesh_payload(path,plate._per_solid_color(part))
    paths=[Path(__file__),Path(interface.__file__),Path(interface.fits.__file__),Path(plate.__file__),
           Path(plate.interface.__file__),HERE/(NAME+'.step'),HERE/(NAME+'.stl'),
           HERE/(RECEIVER+'.step'),HERE/(RECEIVER+'.stl')]
    report={'pass':True,'wing_projection_mm':interface.PROJECTION,
            'wing_thickness_mm':interface.WING_THICK,'wing_span_mm':interface.WING_SPAN,
            'wing_end_radius_mm':interface.END_RADIUS,
            'slot_thickness_mm':interface.WING_THICK+interface.THICKNESS_AIR,
            'slot_thickness_air_mm':interface.THICKNESS_AIR,
            'slot_tip_air_mm':interface.TIP_AIR,
            'minimum_engagement_at_lateral_float_mm':interface.PROJECTION-2*interface.FACE_SLIP,
            'minimum_flat_bearing_at_lateral_float_mm':interface.PROJECTION-2*interface.FACE_SLIP-interface.ENTRY_BEVEL_WIDTH,
            'field_thickness_mm':interface.FIELD_THICK,'plate_thickness_mm':interface.THICK,
            'raised_perimeter':False,
            'face_perimeter_air_mm':interface.FACE_SLIP,
            'slot_end_air_mm':interface.END_AIR,
            'seated_pure_axis_travel_mm':{'X':2*interface.FACE_SLIP,
                                         'Y':interface.THICKNESS_AIR,
                                         'Z':2*interface.FACE_SLIP+interface.SUPPORTED_END_AIR},
            'clearance_policy':'Shared static fits.slip at locating gaps; nonlocating wing tips have 0.25 mm X clearance and the Y slot has 0.30 mm clearance above the seated wing as a local thickness-fit trial. fits.supported_surface once at print-down mouth and slot ends. Zero at the back seating datum. No sliding or low-force additions.',
            'entry_bevel_mm':{'width':interface.ENTRY_BEVEL_WIDTH,'depth':interface.ENTRY_BEVEL_DEPTH},
            'supported_end_extra_clearance_mm':interface.SUPPORTED_END_AIR,
            'receiver_lip_thickness_mm':interface.THICK-interface.WING_THICK-interface.THICKNESS_AIR,
            'body_receiver_overlap_mm3':exterior.intersect(fixture).Volume(),
            'bed_contact_mm2':bed_area,'first_layer_includes_plate_and_both_wings':True,
            'artwork_rise_mm':ARTWORK_RISE,'raised_white_solids':len(white.Solids()),
            'print_planes_z_mm':{'back_and_wings':0,'wing_top':interface.WING_THICK,
                                 'inlay_bottom':interface.THICK-plate.INK_DEPTH,
                                 'black_face':interface.THICK,'white_top':interface.THICK+ARTWORK_RISE},
            'support_policy':'Nameplate requires no supports. Receiver prints in enclosure wall orientation.',
            'physical_qualification':'Pending insertion flex, relaxed flatness, shake retention and QR scan. CAD capture is not a force or strain qualification.',
            'receiver_integration':'Coupon uses the reusable wall cutter in wing_interface.py; full enclosure receiver awaits this mechanism fit trial.',
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (HERE/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
