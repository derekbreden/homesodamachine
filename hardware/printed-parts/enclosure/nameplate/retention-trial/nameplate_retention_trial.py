"""Broad-leaf, 3.6 mm-hook nameplate and matching receiver fit coupon."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path.insert(0,str(HERE.parent))
import nameplate as plate
from _cadq_export import export_assembly, export_step, _write_mesh_payload, _per_solid_color
from _materials import M_PETGF_BLACK, one_body

# A private interface instance keeps the coupon's dimensions separate from the enclosure.
spec = importlib.util.spec_from_file_location('nameplate_trial_interface',plate.interface.__file__)
interface = importlib.util.module_from_spec(spec)
spec.loader.exec_module(interface)
interface.TAB_WIDTH = 32.0
interface.LIP = 3.6
interface.LIP_START = 9.25
interface.TAB_LENGTH = 13.65
interface.BEARING_SLIP = 1.23
FLEX_MARGIN = .6
DEFLECTION = interface.LIP-interface.SIDE_SLIP+.1
FLEX_EDGE = interface.TAB_X-interface.TAB_THICK/2-DEFLECTION*interface.TAB_LENGTH/interface.LIP_START-FLEX_MARGIN


def inward():
    return FLEX_EDGE


interface.inward = inward
NAME = 'nameplate-broad-leaf-001'
RECEIVER = 'nameplate-broad-leaf-receiver'


def blank():
    body = (cq.Workplane('XY').rect(plate.WIDTH,plate.HEIGHT).extrude(plate.THICK)
            .edges('|Z').fillet(plate.CORNER_R).faces('<Z').chamfer(plate.BEVEL).val()
            .rotate((0,0,0),(1,0,0),-90))
    body = body.fuse(*interface.tabs()).clean()
    roots = [e for e in body.Edges() if abs(e.Center().y)<1e-6
             and abs(abs(e.Center().x)-(interface.TAB_X-interface.TAB_THICK/2))<1e-5
             and abs(e.Length()-interface.TAB_WIDTH)<1e-5]
    assert len(roots)==2
    return body.fillet(interface.TAB_ROOT_R,roots).clean()


def receiver():
    shell = interface.box(-plate.WIDTH/2-4,plate.WIDTH/2+4,plate.THICK-3,plate.THICK,
                          -plate.HEIGHT/2-4,plate.HEIGHT/2+4)
    return interface.apply(shell,interface.station(0,0),plate.THICK).clean()


def main():
    body = blank(); fixture = receiver(); ink = plate.build_ink(1)
    black = body.cut(ink).clean()
    assert all(s.isValid() and len(s.Solids())==1 for s in (body,black,fixture))
    assert abs(black.Volume()+ink.Volume()-body.Volume())<1e-5
    assert body.intersect(fixture).Volume()<1e-6
    assert body.translate((0,-.1,0)).intersect(fixture).Volume()>1
    assert body.translate((0,interface.BEARING_SLIP+.1,0)).intersect(fixture).Volume()>.1
    for side,tab in zip((-1,1),interface.tabs()):
        slope = side*DEFLECTION/interface.LIP_START
        bent = tab.transformGeometry(cq.Matrix([[1,slope,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]))
        for half in range(math.ceil(interface.TAB_LENGTH*2)+2):
            assert bent.translate((0,half*.5,0)).intersect(fixture).Volume()<1e-6
    shoulder = interface.LIP_START-interface.BEARING_SLIP
    assert abs(shoulder-(plate.interface.LIP_START-plate.interface.BEARING_SLIP))<1e-6
    face = interface.box(-100,100,0,plate.THICK+1,-100,100)
    a,b = body.intersect(face),plate.blank_plate().intersect(face)
    face_delta = a.cut(b).Volume()+b.cut(a).Volume()
    assert abs(face_delta)<1e-6
    assembly = cq.Assembly()
    assembly.add(black,name=NAME,color=plate._filament(plate.BLACK))
    assembly.add(ink,name=NAME+'-ink',color=plate._filament(plate.WHITE))
    for name,part,exterior in ((NAME,assembly,body),(RECEIVER,one_body(fixture,RECEIVER,M_PETGF_BLACK),fixture)):
        path=HERE/(name+'.step')
        export_assembly(part,str(path));export_step(exterior,str(path.with_suffix('.stl')))
        _write_mesh_payload(path,_per_solid_color(part))
    report={'pass':True,'leaf_span_mm':interface.TAB_WIDTH,'hook_projection_mm':interface.LIP,
            'leaf_thickness_mm':interface.TAB_THICK,'extra_arm_reach_mm':.75,
            'root_fillet_mm':interface.TAB_ROOT_R,'end_stock_mm':(plate.HEIGHT-interface.TAB_WIDTH)/2,
            'nominal_bearing_clearance_mm':interface.BEARING_SLIP,'catch_depth_from_plate_back_mm':shoulder,
            'tip_depth_from_plate_back_mm':interface.TAB_LENGTH,
            'nominal_engagement_mm':interface.LIP-interface.SIDE_SLIP,
            'minimum_engagement_at_lateral_float_mm':interface.LIP-interface.SIDE_SLIP-interface.SLIP,
            'nominal_bearing_area_each_mm2':interface.TAB_WIDTH*(interface.LIP-interface.SIDE_SLIP),
            'flex_lane_inner_x_mm':FLEX_EDGE,'insertion_sweep_clear':True,
            'face_geometry_difference_mm3':face_delta,'artwork':'Identical unit 0001 black/white artwork.',
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (Path(__file__),Path(plate.__file__),Path(plate.interface.__file__),HERE/(NAME+'.step'),HERE/(NAME+'.stl'),HERE/(RECEIVER+'.step'),HERE/(RECEIVER+'.stl'))},
            'physical_fit':'Pending: clean snap, no bow, shake retention and support removal.'}
    (HERE/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('pass','leaf_span_mm','hook_projection_mm','nominal_bearing_clearance_mm','minimum_engagement_at_lateral_float_mm')},indent=2))


if __name__=='__main__':
    main()
