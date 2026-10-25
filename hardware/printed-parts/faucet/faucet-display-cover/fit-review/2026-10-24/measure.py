"""Manual comparison of the failed Sculpted cover and working Industrial control."""
from contextlib import ExitStack
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
import importlib.util,json,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').is_file())
FAUCET=ROOT/'hardware/printed-parts/faucet'
sys.path[:0]=[str(FAUCET/'industrial'),str(FAUCET/'faucet-shell'),str(ROOT/'hardware/faucet-layout')]
import faucet_shell as shell
import industrial_display_cover as industrial
import faucet_assembly as assembly
SOURCE=FAUCET/'faucet-display-cover/faucet_display_cover.py'
REVIEW=FAUCET/'industrial/display-seat-review/2026-10-24'


def sculpted(name):
    spec=importlib.util.spec_from_file_location(name,SOURCE)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def measure():
    changed={'display_feet_n':7.1,'display_floor_n':7.1,'display_face_n':shell.display_face_n-4.5,'display_cover_top_n':shell.display_cover_top_n-4.5}
    result={};solids={}
    origin,along,normal=shell._tip_frame()
    frame=cq.Location(cq.Plane(origin=origin,xDir=(1,0,0),normal=normal))
    with ExitStack() as stack:
        for k,v in changed.items():stack.enter_context(patch.object(shell,k,v))
        tip=cq.importers.importStep(str(REVIEW/'candidate-tip.step')).val()
        display=assembly.build_display_body().val();screen=assembly.build_display_screen().val()
        control=industrial.build_seated_display_cover().val()
        controls=industrial.build_display_cover().val()
        solids.update(tip=tip,display=display,screen=screen,industrial=control,industrialPrint=controls)
        raw_clearance=shell.build_display_neck_clearance
        for label,extension in [('printedSculpted',0.),('correctedSculpted',.5),('extraOneMillimeter',1.)]:
            with ExitStack() as child:
                child.enter_context(patch.object(shell,'display_face_n',changed['display_face_n']+extension))
                child.enter_context(patch.object(shell,'display_cover_top_n',changed['display_cover_top_n']+extension))
                child.enter_context(patch.object(shell,'build_display_neck_clearance',lambda e=extension: raw_clearance().translate(normal.multiply(e).toTuple())))
                cover=sculpted(label)
                seated=cover.build_seated_display_cover().val();printable=cover.build_display_cover().val()
                solids[label]=seated;solids[label+'Print']=printable
                result[label]={'wing_reach_extension_mm':extension,'bezel_top_n_mm':cover.plate_n_top,'bezel_inner_n_mm':cover.bezel_n_bottom,'glass_gap_mm':cover.bezel_n_bottom-changed['display_face_n'],'bezel_thickness_mm':cover.bezel_thickness,'lip_top_to_bezel_inner_mm':cover.bezel_n_bottom-shell.display_clip_top_n,'lip_bottom_top_n_mm':[shell.display_clip_bottom_n,shell.display_clip_top_n],'seated_cover_to_tip_intersection_mm3':seated.intersect(tip).Volume(),'display_body_to_cover_intersection_mm3':seated.intersect(display).Volume(),'screen_to_cover_intersection_mm3':seated.intersect(screen).Volume(),'valid_single_solid':printable.isValid() and len(printable.Solids())==1,'volume_mm3':printable.Volume()}
                print(label,json.dumps(result[label]),flush=True)
        dims=industrial.DIMENSIONS
        result['industrial']={'wing_reach_extension_mm':dims.wing_extension_mm,'bezel_top_n_mm':dims.n_top,'bezel_inner_n_mm':dims.bezel_n_bottom,'glass_gap_mm':dims.bezel_n_bottom-changed['display_face_n'],'bezel_thickness_mm':dims.n_top-dims.bezel_n_bottom,'lip_top_to_bezel_inner_mm':dims.bezel_n_bottom-shell.display_clip_top_n,'lip_bottom_top_n_mm':[shell.display_clip_bottom_n,shell.display_clip_top_n],'seated_cover_to_tip_intersection_mm3':control.intersect(tip).Volume(),'display_body_to_cover_intersection_mm3':control.intersect(display).Volume()}
        result['tube_crown_n_mm']=shell.tube_shell_center_y+shell.tube_shell_outer_r
        result['nominal_arch_cutout_clearance_at_crown_mm']={'printedSculpted':shell.display_cover_slip,'industrial':shell.display_cover_slip+.5,'correctedSculpted':shell.display_cover_slip+.5}
        result['retained']={'display_foot_bearing_n_mm':7.1,'display_drop_mm':4.5,'foot_recess_depth_mm':1.0,'radial_lip_engagement_mm':shell.display_neck_outer_r-shell.display_clip_lip_radius,'preload_at_lip_top_mm':1.25}
    frozen=cq.importers.importStep(str(FAUCET/'industrial/prints/2026-10-24-sculpted-cover-uniform024-mark2/sculpted-display-cover-low45.step')).val()
    result['baseline_native_volume_difference_mm3']=frozen.Volume()-solids['printedSculptedPrint'].Volume()
    result['recorded_at_utc']=datetime.now(timezone.utc).isoformat()
    for name,solid in solids.items():
        cq.exporters.export(solid,str(HERE/(name+'.step')))
    cq.exporters.export(solids['correctedSculptedPrint'],str(HERE/'corrected-sculpted-cover.stl'),tolerance=.005,angularTolerance=.1)
    (HERE/'native-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    return solids,frame,result

if __name__=='__main__':measure()
