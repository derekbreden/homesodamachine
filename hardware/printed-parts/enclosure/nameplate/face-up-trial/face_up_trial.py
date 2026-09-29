"""Broad-leaf nameplate with 0.48 mm raised white lettering, printed face up."""
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path.insert(0,str(HERE.parent/'retention-trial'))
import nameplate_retention_trial as retention

plate = retention.plate
NAME = 'nameplate-face-up-raised-001'
LETTER_RISE = .48


def print_pose(shape):
    """Hook tips on the bed; the readable show face points toward positive Z."""
    return (shape.rotate((0,0,0),(1,0,0),90)
            .rotate((0,0,0),(0,0,1),180)
            .translate((0,0,retention.interface.TAB_LENGTH)))


def main():
    blank = retention.blank()
    original_ink = plate.build_ink(1)
    black = blank.cut(original_ink).clean()
    names = plate.build_name().Solids()
    raised = [s.fuse(s.translate((0,LETTER_RISE,0))).clean() for s in names]
    logo = plate._place(plate._upright(plate.build_logo()),plate.WIDTH/2-plate.LOGO_LEFT,0)
    ink = cq.Compound.makeCompound([logo,*raised,plate.build_qr(1)])
    exterior = blank.fuse(*raised).clean()
    assert exterior.isValid() and len(exterior.Solids()) == 1
    assert black.isValid() and len(black.Solids()) == 1
    assert all(s.isValid() for s in ink.Solids())
    assert black.intersect(ink).Volume() < 1e-6
    assert abs(black.Volume()+ink.Volume()-exterior.Volume()) < 1e-4
    ordinary = retention.interface.box(-100,100,-100,plate.THICK,-100,100)
    unchanged = exterior.intersect(ordinary)
    delta = unchanged.cut(blank).Volume()+blank.cut(unchanged).Volume()
    assert delta < 1e-5,delta
    fixture = cq.importers.importStep(str(retention.HERE/(retention.RECEIVER+'.step'))).val()
    assert exterior.intersect(fixture).Volume() < 1e-6
    assert exterior.translate((0,-.1,0)).intersect(fixture).Volume() > 1
    assert exterior.translate((0,retention.interface.BEARING_SLIP+.1,0)).intersect(fixture).Volume() > .1
    face_z = retention.interface.TAB_LENGTH+plate.THICK
    posed = print_pose(exterior)
    assert abs(posed.BoundingBox().zmin) < 1e-6
    assert abs(posed.BoundingBox().zmax-(face_z+LETTER_RISE)) < 1e-6
    assert all(abs(s.BoundingBox().ymax-(plate.THICK+LETTER_RISE))<1e-6 for s in raised)
    assembly = cq.Assembly()
    assembly.add(black,name=NAME,color=plate._filament(plate.BLACK))
    assembly.add(ink,name=NAME+'-ink',color=plate._filament(plate.WHITE))
    path=HERE/(NAME+'.step')
    plate.export_assembly(assembly,str(path))
    plate.export_step(exterior,str(path.with_suffix('.stl')))
    plate._write_mesh_payload(path,plate._per_solid_color(assembly))
    inputs=[Path(__file__),Path(retention.__file__),Path(plate.__file__),Path(plate.interface.__file__),
            Path(plate.__file__).with_name('wordmark.svg'),ROOT/'brand/mark.svg',
            retention.HERE/(retention.RECEIVER+'.step'),path,path.with_suffix('.stl')]
    report={'pass':True,'letter_rise_mm':LETTER_RISE,'raised_letter_solids':len(raised),
            'flush_artwork':'Faucet logo and unit-0001 QR.','below_show_face_geometry_difference_mm3':delta,
            'receiver_overlap_mm3':exterior.intersect(fixture).Volume(),
            'leaf_span_mm':retention.interface.TAB_WIDTH,'hook_projection_mm':retention.interface.LIP,
            'bearing_clearance_mm':retention.interface.BEARING_SLIP,'receiver_reused':True,
            'print_planes_z_mm':{'hook_tip':0,'hook_nose_end':retention.interface.TAB_LENGTH-retention.interface.LIP_START-retention.interface.LIP_LAND,
                'hook_bearing':retention.interface.TAB_LENGTH-retention.interface.LIP_START,
                'plate_back':retention.interface.TAB_LENGTH,'white_inlay_base':face_z-plate.INK_DEPTH,
                'show_face':face_z,'letter_top':face_z+LETTER_RISE},
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
            'physical_fit':'Pending: support removal, engagement, bow, shake retention and QR scan.'}
    (HERE/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('pass','letter_rise_mm','below_show_face_geometry_difference_mm3','print_planes_z_mm')},indent=2))


if __name__=='__main__':main()
