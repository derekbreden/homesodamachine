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
    check('frame retains complete brim-bearing stock',
          frame.Volume()>old_frame.Volume(),baseline_frame_mm3=old_frame.Volume(),
          current_frame_mm3=frame.Volume(),added_fraction=(frame.Volume()-old_frame.Volume())/old_frame.Volume())
    retained_lower_top = rail + ff.receiver_height
    lower=e._ybox(-120,120,0,480,floor-1,retained_lower_top)
    delta=abs(frame.intersect(lower).cut(old_frame).Volume())+abs(old_frame.intersect(lower).cut(frame).Volume())
    check('frame socket, rails and lower corbels equal retained baseline',delta<1e-5,
          delta_mm3=delta,below_z_mm=retained_lower_top)
    correction_baseline=ROOT/'.cache/front-roof-flat-wall/baseline'
    old_front=cq.importers.importStep(str(correction_baseline/'enclosure-front-top.step')).val()
    flat_wall=e._report_ridge_roof(cq.Workplane(obj=shells['front-top']),box)
    check('one continuous flat display wall with declared cable openings',
          flat_wall['flat_face_count']==1,**flat_wall)
    wall_y=r['front']-e.slide_slip
    foot=box.pump_bay[2]
    wall_region=e._ybox(-120,120,box.pack.collet_plate['aft_y']-.001,
                       wall_y+e._cable_clip.DEPTH+.001,foot-.001,box.outer[5]+1)
    roof_region=e._ybox(-120,120,wall_y,box.y_joint+e.lip_len+1,
                       334-e.slide_slip-.001,box.outer[5]+1)
    loom=e._ridge_loom_station(box.outer,box.pack.collet_plate,box.pump_bay)
    old_clip_z=loom[2]-e._cable_clip.seat_top()
    old_clip_end=box.inner[1]-e.pump_lead_clip_edge_land
    old_clip_face=box.pack.collet_plate['aft_y']+e.ridge_wall_t
    clip_region=e._ybox(old_clip_end-e._cable_clip.RUN-1,old_clip_end+1,
                        old_clip_face-1,wall_y+e._cable_clip.DEPTH+1,
                        old_clip_z-1,flat_wall['clip_origin_mm'][2]+e._cable_clip.HEIGHT+1)
    allowed=wall_region.fuse(roof_region).fuse(clip_region)
    delta=abs(shells['front-top'].cut(old_front).cut(allowed).Volume())+abs(old_front.cut(shells['front-top']).cut(allowed).Volume())
    check('front-top retained outside display wall, clip and roof clearance',delta<1e-5,
          delta_outside_declared_change_regions_mm3=delta)
    added_front=abs(shells['front-top'].cut(old_front).Volume())
    removed_front=abs(old_front.cut(shells['front-top']).Volume())
    prior_frame=cq.importers.importStep(str(correction_baseline/'funnel-frame.step')).val().translate((0,ff.center_y,floor))
    added_frame=abs(frame.cut(prior_frame).Volume())
    removed_frame=abs(prior_frame.cut(frame).Volume())
    check('display wall stock and occupied enclosure air quantified',True,
          added_front_top_stock_mm3=added_front,removed_front_top_stock_mm3=removed_front,
          front_top_air_occupied_ml=(added_front-removed_front)/1000,
          added_frame_stock_mm3=added_frame,removed_frame_stock_mm3=removed_frame,
          net_enclosure_air_occupied_ml=(added_front-removed_front+added_frame-removed_frame)/1000,
          scope='Combined rigid front-top and frame solid volume change; this is enclosure air, not liquid funnel capacity.')
    addition,channel=e._cable_clip.local_geometry(embed=0,
                         wall_thickness=wall_y-box.pack.collet_plate['aft_y'])
    location=cq.Location(cq.Plane(origin=flat_wall['clip_origin_mm'],xDir=(0,1,0),normal=(1,0,0)))
    clip=addition.cut(channel).moved(location)
    channel=channel.moved(location)
    clip_missing=abs(clip.cut(shells['front-top']).Volume())
    channel_blocked=abs(channel.intersect(shells['front-top']).Volume())
    check('relocated clip is complete and its channel is open',clip_missing<1e-5 and channel_blocked<1e-5,
          missing_clip_stock_mm3=clip_missing,blocked_channel_mm3=channel_blocked)
    empty('frame clears relocated cable clip',frame,clip)
    empty('frame clears relocated cable channel',frame,channel)
    check('frame leaves clearance to clip and channel',frame.distance(clip)>0 and frame.distance(channel)>0,
          clip_distance_mm=frame.distance(clip),channel_distance_mm=frame.distance(channel))
    for sign in (-1,1):
        xa,xb=sorted((sign*(box.outer[1]-e.front_top_flank_t),sign*box.outer[1]))
        witness=e._rounded_outer(box.outer).intersect(e._ybox(
            xa,xb,r['front']+10,box.y_joint-e.slide_slip,346+e.slide_slip,box.outer[5]))
        missing=abs(witness.cut(shells['front-top']).Volume())
        check(f'complete {e.front_top_flank_t:g} mm roof flank {sign:+g}',missing<1e-5,
              nominal_section_mm=e.front_top_flank_t,missing_stock_mm3=missing,
              witness_y_mm=[r['front']+10,box.y_joint-e.slide_slip],witness_z_mm=[346+e.slide_slip,box.outer[5]])
    solid,cavity,meta=ff.funnel.build_solids()
    capacity=cavity.intersect(ff.funnel._box(600,600,meta['end_z'],meta['top_z'],0,0)).Volume()/1000
    check('silicone capacity retained',abs(capacity-ff.funnel.capacity_ml)<.25,
          native_capacity_ml=capacity,nominal_capacity_ml=ff.funnel.capacity_ml,capacity_loss_ml=0,
          basis='Silicone source and cavity geometry retained; only rigid wall and frame boundaries changed.')
    added=frame.cut(old_frame)
    assembly_path=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    assembly=import_assembly(str(assembly_path))
    names=[]
    for label,stock in [('frame',added),('front-top',shells['front-top'].cut(old_front))]:
        a=stock.BoundingBox()
        for name,(s,_color) in assembly.items():
            if name.startswith('enclosure') or name=='funnel-frame':continue
            b=s.BoundingBox()
            if any(getattr(a,k+'max')<getattr(b,k+'min') or getattr(b,k+'max')<getattr(a,k+'min') for k in 'xyz'):continue
            names.append(label+'/'+name);empty('added '+label+' stock clears '+name,stock,s)
    paths=[Path(__file__),box_path,frame_path,frame_path.with_suffix('.stl'),assembly_path,
           ENC/'enclosure.py',FUNNEL/'funnel_frame.py',FUNNEL/'funnel.py',Path(e._cable_clip.__file__),
           *[ENC/f'enclosure-{n}.{ext}' for n in shells for ext in ('step','stl')]]
    result=dict(schema=1,checks=rows,roof_datums_mm=r,
                nearby_installed_members_checked=names,
                source_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},
                retained_baseline_sha256={p.name:sha(p) for p in baseline.glob('*.step')},
                flat_wall_baseline_sha256={p.name:sha(p) for p in correction_baseline.glob('*.step')},
                scope='Native roof, flat wall and retained mating geometry. Added rigid stock checked against installed bodies from the named assembly export; full motion, load capacity, physical fit, print finish and support removal remain separate qualifications.')
    result['pass']=all(row['pass'] for row in rows)
    (HERE/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['pass']:raise ValueError([r['check'] for r in rows if not r['pass']])

if __name__=='__main__':main()
