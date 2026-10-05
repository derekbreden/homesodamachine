"""Check the exported flush roof, retained mating datums and added-stock clearances."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
ENC=ROOT/'hardware/printed-parts/enclosure/enclosure'
FUNNEL=HERE.parent
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ENC),str(FUNNEL)]
import enclosure as e,funnel_frame as ff,_box_spec
from _cadq_export import import_assembly
from materialize_pump_cartridge import _declared_box

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    box,_bounds,box_path=_declared_box(_box_spec,e)
    rows=[]
    def check(name,ok,**values):
        rows.append({'check':name,'pass':bool(ok),**values})
        print(name,bool(ok),values,flush=True)
    def empty(name,a,b):
        v=abs(a.intersect(b).Volume());check(name,v<1e-5,overlap_mm3=v)
    floor,plug,rail=ff.datums(e.funnel_seat_z(box.outer))
    seat=e.funnel_seat_z(box.outer)
    r=ff.roof_datums(box.inner,box.pack.funnel,seat,box.y_joint)
    frame_path=FUNNEL/'funnel-frame.step'
    frame=cq.importers.importStep(str(frame_path)).val().translate((0,ff.center_y,floor))
    shells={n:cq.importers.importStep(str(ENC/f'enclosure-{n}.step')).val() for n in ('front-top','back-top')}
    for name,s in [('funnel-frame',frame),*shells.items()]:
        check(name+' one valid solid',s.isValid() and len(s.Solids())==1,volume_mm3=s.Volume())
    check('frame roof flush with shell exterior',abs(frame.BoundingBox().zmax-box.outer[5])<1e-6,
          frame_top_z_mm=frame.BoundingBox().zmax,roof_z_mm=box.outer[5])
    check('existing outlet socket and rail datums retained',abs(floor-299.9)<1e-6 and abs(plug-302.9)<1e-6 and abs(rail-306.9)<1e-6,
          underside_z_mm=floor,socket_floor_z_mm=plug,rail_z_mm=rail,silicone_seat_z_mm=seat)
    brim=ff.funnel._rounded_box(ff.funnel.collar_w+2*ff.funnel.brim_overhang,
          ff.funnel.collar_d+2*ff.funnel.brim_overhang,ff.funnel.brim_corner_r,
          seat-ff.web,seat,0,ff.center_y)
    collar=ff.funnel._rounded_box(ff.funnel.collar_w+0.6,ff.funnel.collar_d+0.6,
          ff.funnel.collar_corner_r+0.3,seat-ff.web-1,seat+1,0,ff.center_y)
    bearing=brim.cut(collar)
    loss=abs(bearing.cut(frame).Volume())
    check('complete slipped brim footprint has 3 mm of frame bearing',loss<1e-5,missing_volume_mm3=loss,bearing_volume_mm3=bearing.Volume())
    check('display-side roof landing retains 3 mm',abs((ff.center_y-ff.funnel.collar_d/2-ff.funnel.brim_overhang-e.funnel_collar_air)-r['front']-3)<1e-6,
          roof_front_y_mm=r['front'],landing_mm=3)
    front_clear=(r['front']-e._swept_top.profile(box.outer)['roof'][0])
    check('frame roof stays behind display roof arris',front_clear>=0,air_mm=front_clear)
    for n,s in shells.items():empty('frame seated in '+n,frame,s)
    baseline=ROOT/'.cache/flush-funnel-roof/baseline'
    old_frame=cq.importers.importStep(str(baseline/'funnel-frame.step')).val().translate((0,ff.center_y,floor))
    check('front roof stops before existing back-top',abs(r['back']-(box.y_joint-e.slide_slip))<1e-6,
          roof_back_y_mm=r['back'],y_seam_mm=box.y_joint,running_air_mm=e.slide_slip)
    rear=e._ybox(-120,120,box.y_joint,400,seat+0.001,seat+20)
    upper_rear=abs(frame.intersect(rear).Volume())
    check('rear frame stays beneath existing back-top ceiling',upper_rear<1e-5,
          rear_frame_above_seat_mm3=upper_rear)
    old_back_path=baseline/'enclosure-back-top.step'
    back_paths=[ENC/f'enclosure-back-top.{ext}' for ext in ('step','stl','step.mesh')]
    check('existing back-top export triplet retained exactly',
          all(sha(p)==sha(baseline/p.name) for p in back_paths),
          sha256={p.name:sha(p) for p in back_paths})
    check('frame stock addition is confined to roof and complete brim bearing',
          frame.Volume()>old_frame.Volume(),baseline_frame_mm3=old_frame.Volume(),
          current_frame_mm3=frame.Volume(),added_fraction=(frame.Volume()-old_frame.Volume())/old_frame.Volume())
    lower=e._ybox(-120,120,0,480,floor-1,r['taper_floor']-0.001)
    delta=abs(frame.intersect(lower).cut(old_frame).Volume())+abs(old_frame.intersect(lower).cut(frame).Volume())
    check('lower frame equals retained baseline',delta<1e-5,delta_mm3=delta,below_z_mm=r['taper_floor']-0.001)
    for n,s in shells.items():
        old=cq.importers.importStep(str(baseline/f'enclosure-{n}.step')).val()
        below=e._ybox(-120,120,0,480,150,r['taper_floor']-e.slide_slip-0.001)
        delta=abs(s.intersect(below).cut(old).Volume())+abs(old.intersect(below).cut(s).Volume())
        check(n+' below roof equals retained baseline',delta<1e-5,delta_mm3=delta,below_z_mm=r['taper_floor']-e.slide_slip-0.001)
    added=frame.cut(old_frame)
    assembly_path=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    assembly=import_assembly(str(assembly_path))
    names=[]
    a=added.BoundingBox()
    for name,(s,_color) in assembly.items():
        if name.startswith('enclosure') or name=='funnel-frame':continue
        b=s.BoundingBox()
        if any(getattr(a,k+'max')<getattr(b,k+'min') or getattr(b,k+'max')<getattr(a,k+'min') for k in 'xyz'):continue
        names.append(name);empty('added frame stock clears '+name,added,s)
    paths=[Path(__file__),box_path,frame_path,frame_path.with_suffix('.stl'),assembly_path,
           ENC/'enclosure.py',FUNNEL/'funnel_frame.py',*[ENC/f'enclosure-{n}.{ext}' for n in shells for ext in ('step','stl')]]
    result=dict(schema=1,checks=rows,roof_datums_mm=r,
                nearby_installed_members_checked=names,
                source_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},
                retained_baseline_sha256={p.name:sha(p) for p in baseline.glob('*.step')},
                scope='Native roof and retained mating geometry. Added frame stock checked against installed bodies from the named assembly export; full motion, load capacity, physical fit, print finish and support removal remain separate qualifications.')
    result['pass']=all(row['pass'] for row in rows)
    (HERE/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['pass']:raise ValueError([r['check'] for r in rows if not r['pass']])

if __name__=='__main__':main()
