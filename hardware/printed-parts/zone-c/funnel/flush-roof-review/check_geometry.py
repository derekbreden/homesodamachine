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

RETAINED_PROOF_SHA256='fe1d56813052753f024f024746c966a9c06979d07c6a9c84b27897680a8f3448'
PREVIOUS_FRAME_SHA256='5da1c15d6526467fa4c53978608c5467d1647f0f8a6f9aa99754c65a4de8ef93'
PREVIOUS_FLAT_FRONT_SHA256='a35f0dc6d127ca234965d67be0385f138e9b00630ad7f117a584ad07a3276aac'

def volume(shape):
    """Adaptive native integration; no tessellated volume estimates."""
    return abs(shape.Volume(tol=1e-9))

def bounds(shape):
    b=shape.BoundingBox()
    return {k:[getattr(b,k+'min'),getattr(b,k+'max')] for k in 'xyz'}

def separate(a,b):
    """A strict box separation proves zero intersection without a Boolean."""
    a,b=a.BoundingBox(),b.BoundingBox()
    return any(getattr(a,k+'max')<getattr(b,k+'min') or
               getattr(b,k+'max')<getattr(a,k+'min') for k in 'xyz')

def retained_proof():
    """Preserve the exact earlier native witnesses when refreshing this record.

    The rear-corner check binds the sole subsequent frame source change. This
    avoids repeating the slow whole imported-frame/shell Boolean, while the
    current front-top is compared directly against its bound prior export.
    """
    record=json.loads((HERE/'geometry-check.json').read_text())
    if 'retained_native_proof' in record:
        record=record['retained_native_proof']['record']
    encoded=(json.dumps(record,indent=2)+'\n').encode()
    if hashlib.sha256(encoded).hexdigest()!=RETAINED_PROOF_SHA256 or not record['pass']:
        raise ValueError('The retained native proof is missing or does not match its exact digest')
    return {'artifact_sha256':RETAINED_PROOF_SHA256,'record':record}

def selected_fit_regions(box):
    """Exact old-minus-selected cutter solids, never permissive bounding boxes."""
    retention=e._retention
    x,z=e.pump_retention_station(box)
    face,into=e.pump_retention_face(box,'front-top')
    radius=retention.OD/2+.2
    depth=retention.THICKNESS+.4
    y0,y1=sorted((face+into*retention.FACE_COVER,
                 face+into*(retention.FACE_COVER+depth)))
    arc_z=z+.2
    roof_z=z+retention.OD/2+retention.ROOF_AIR
    previous=cq.Solid.makeCylinder(radius,y1-y0,cq.Vector(x,y0,arc_z),cq.Vector(0,1,0)).fuse(
        cq.Solid.makeBox(2*radius,y1-y0,roof_z-arc_z,cq.Vector(x-radius,y0,arc_z))).clean()
    selected=e.pump_retention_pocket(box,'front-top')
    regions=[dict(name='C3 front-top RC62 pocket',kind='magnet',
                  previous=previous,selected=selected,
                  allowed=previous.cut(selected),expected=previous.cut(selected),
                  previous_radial_air_mm=.2,previous_axial_air_mm=.4,
                  selected_radial_air_mm=retention.RADIAL_AIR,
                  selected_axial_air_mm=retention.AXIAL_AIR,
                  dimensions_mm=retention.dimensions((x,z),face,into))]
    band=e._piece_bands(box,'front-top')
    for ti,(plane,sign,seats) in enumerate(box.pack.valve_trays):
        zs=[sz for _sx,sz in seats]
        mid_z=(min(zs)+max(zs))/2
        if not (band[0]<=plane<=band[1] and band[2]<=mid_z<=band[3]):continue
        along=sorted((plane+sign*e._seat.socket_floor_z,
                      plane+sign*(e._seat.seat_top_z+1)))
        grip=sorted((plane+sign*e._seat.socket_floor_z,
                     plane+sign*e._seat.seat_top_z))
        for si,(sx,sz) in enumerate(seats):
            for ci,(dx,dz) in enumerate((dx,dz)
                    for dx in (-e._seat.corner_inset_x,e._seat.corner_inset_x)
                    for dz in (-e._seat.corner_inset_y,e._seat.corner_inset_y)):
                px,pz=sx+dx,sz-sign*dz
                previous=e._teardrop_y(7.2/2,px,pz,*along)
                selected=e._teardrop_y(e._seat.socket_radius,px,pz,*along)
                allowed=previous.cut(selected)
                axial=e._ybox(px-10,px+10,*grip,pz-10,pz+10)
                regions.append(dict(name=f'V69 tray {ti} seat {si} post {ci}',kind='valve',
                    previous=previous,selected=selected,allowed=allowed,
                    expected=allowed.intersect(axial),axis_xz_mm=[px,pz],
                    socket_y_mm=along,bearing_y_mm=plane+sign*e._seat.seat_top_z,
                    grip_y_mm=grip,previous_socket_diameter_mm=7.2,
                    selected_socket_diameter_mm=e._seat.socket_diameter,
                    teardrop_roof_angle_degrees=e.teardrop_roof_angle))
    return regions

def main():
    box,_bounds,box_path=_declared_box(_box_spec,e)
    retained=retained_proof()
    prior=retained['record']
    prior_rows={row['check']:row for row in prior['checks']}
    rear_path=HERE/'rear-corner-check.json'
    rear_proof=json.loads(rear_path.read_text())
    generation_path=HERE/'generation.json'
    generation=json.loads(generation_path.read_text())
    rows=[]
    def check(name,ok,**values):
        rows.append({'check':name,'pass':bool(ok),**values})
        print(name,bool(ok),values,flush=True)
    def empty(name,a,b):
        v=0.0 if separate(a,b) else volume(a.intersect(b))
        check(name,v<1e-5,overlap_mm3=v)
    floor,plug,rail=ff.datums(e.funnel_seat_z(box.outer))
    seat=e.funnel_seat_z(box.outer)
    r=ff.roof_datums(box.inner,box.pack.funnel,seat,box.y_joint)
    frame_path=FUNNEL/'funnel-frame.step'
    frame=cq.importers.importStep(str(frame_path)).val().translate((0,ff.center_y,floor))
    shells={n:cq.importers.importStep(str(ENC/f'enclosure-{n}.step')).val() for n in ('front-top','back-top')}
    previous_frame_path=ROOT/'.cache/frame-seam-square/baseline/funnel-frame.step'
    previous_front_path=ROOT/'.cache/front-roof-flat-wall/previous-flat/enclosure-front-top.step'
    check('retained native witnesses and bounded corner proof bind current sources',
          sha(previous_frame_path)==PREVIOUS_FRAME_SHA256 and
          sha(previous_front_path)==PREVIOUS_FLAT_FRONT_SHA256 and rear_proof['pass'] and
          rear_proof['previous_frame_step_sha256']==PREVIOUS_FRAME_SHA256 and
          prior['source_sha256'][str(frame_path.relative_to(ROOT))]==PREVIOUS_FRAME_SHA256 and
          prior['source_sha256'][str((ENC/'enclosure-front-top.step').relative_to(ROOT))]==PREVIOUS_FLAT_FRONT_SHA256 and
          all(sha(ROOT/p)==digest for p,digest in rear_proof['source_sha256'].items()) and
          all(sha(ROOT/p)==digest for p,digest in rear_proof['output_sha256'].items()) and
          sha(ENC/'enclosure.py')==prior['source_sha256'][str((ENC/'enclosure.py').relative_to(ROOT))] and
          sha(box_path)==prior['source_sha256'][str(box_path.relative_to(ROOT))],
          retained_native_proof_sha256=RETAINED_PROOF_SHA256,
          bounded_corner_proof_sha256=sha(rear_path))
    check('fresh producer binds all reviewed leaf outputs and loaded geometry sources',
          all(sha((ENC if name=='front-top' else FUNNEL)/filename)==digest
              for name,outputs in generation['outputs'].items() for filename,digest in outputs.items()) and
          all(sha(ROOT/p)==digest for p,digest in generation['source_sha256'].items()
              if not p.startswith('.cache/')),
          generation_sha256=sha(generation_path))
    previous_frame=cq.importers.importStep(str(previous_frame_path)).val().translate((0,ff.center_y,floor))
    previous_front=cq.importers.importStep(str(previous_front_path)).val()
    for name,s in [('funnel-frame',frame),*shells.items()]:
        check(name+' one valid solid',s.isValid() and len(s.Solids())==1,volume_mm3=volume(s))
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
    loss=prior_rows['complete slipped brim footprint has 3 mm of frame bearing']['missing_volume_mm3']
    check('complete slipped brim footprint has 3 mm of frame bearing',
          loss<1e-5 and rear_proof['pass'],missing_volume_mm3=loss,bearing_volume_mm3=volume(bearing),
          basis='Exact retained native witness plus source-bound upper-corner additions; no stock is removed and the complete added footprint below Z349 was already present.')
    check('display-side roof landing retains 3 mm',abs((ff.center_y-ff.funnel.collar_d/2-ff.funnel.brim_overhang-e.funnel_collar_air)-r['front']-3)<1e-6,
          roof_front_y_mm=r['front'],landing_mm=3)
    front_clear=(r['front']-e._swept_top.profile(box.outer)['roof'][0])
    check('frame roof stays behind display roof arris',front_clear>=0,air_mm=front_clear)
    baseline=ROOT/'.cache/flush-funnel-roof/baseline'
    old_frame=cq.importers.importStep(str(baseline/'funnel-frame.step')).val().translate((0,ff.center_y,floor))
    check('front roof stops before existing back-top',abs(r['back']-(box.y_joint-e.slide_slip))<1e-6,
          roof_back_y_mm=r['back'],y_seam_mm=box.y_joint,running_air_mm=e.slide_slip)
    corner_additions=[]
    for sign in (-1,1):
        x0=-r['width']/2 if sign<0 else r['width']/2-ff.corner_radius
        corner=cq.Solid.makeBox(ff.corner_radius,ff.corner_radius,r['top']-seat,
            cq.Vector(x0,r['back']-ff.corner_radius,seat))
        backing=cq.Solid.makeBox(ff.corner_radius,ff.corner_radius,.05,
            cq.Vector(x0,r['back']-ff.corner_radius,seat-.05))
        missing=volume(corner.cut(frame))
        missing_backing=volume(backing.cut(frame))
        previous_corner=previous_frame.intersect(corner)
        current_corner=frame.intersect(corner)
        gain=current_corner.cut(previous_corner)
        removed=volume(previous_corner.cut(current_corner))
        cx=sign*(r['width']/2-ff.corner_radius)
        circle=cq.Solid.makeCylinder(ff.corner_radius,r['top']-seat,
                  cq.Vector(cx,r['back']-ff.corner_radius,seat))
        expected=corner.cut(circle)
        unexpected=volume(gain.cut(expected))+volume(expected.cut(gain))
        corner_additions.append(gain)
        gaps={n:corner.distance(s) for n,s in shells.items()}
        check(f'square rear roof corner {sign:+g} is backed and clears both shells',
              missing<1e-5 and missing_backing<1e-5 and removed<1e-5 and unexpected<1e-5 and
              all(gap>=e.slide_slip-1e-6 for gap in gaps.values()),
              missing_corner_stock_mm3=missing,missing_backing_mm3=missing_backing,
              removed_corner_stock_mm3=removed,unexpected_corner_delta_mm3=unexpected,
              added_corner_stock_mm3=volume(gain),
              shell_clearance_mm=gaps,corner_z_mm=[seat,r['top']])
    rear=e._ybox(-120,120,box.y_joint,400,seat+0.001,seat+20)
    upper_rear=volume(frame.intersect(rear))
    check('rear frame stays beneath existing back-top ceiling',upper_rear<1e-5,
          rear_frame_above_seat_mm3=upper_rear)
    old_back_path=baseline/'enclosure-back-top.step'
    back_paths=[ENC/f'enclosure-back-top.{ext}' for ext in ('step','stl','step.mesh')]
    check('existing back-top export triplet retained exactly',
          all(sha(p)==sha(baseline/p.name) for p in back_paths),
          sha256={p.name:sha(p) for p in back_paths})
    check('frame retains complete brim-bearing stock',
          volume(frame)>volume(old_frame),baseline_frame_mm3=volume(old_frame),
          current_frame_mm3=volume(frame),added_fraction=(volume(frame)-volume(old_frame))/volume(old_frame))
    retained_lower_top = rail + ff.receiver_height
    delta=prior_rows['frame socket, rails and lower corbels equal retained baseline']['delta_mm3']
    check('frame socket, rails and lower corbels equal retained baseline',
          delta<1e-5 and rear_proof['pass'] and all(g.BoundingBox().zmin>=seat-1e-6 for g in corner_additions),
          delta_mm3=delta,below_z_mm=retained_lower_top,
          basis='Exact bound native baseline witness and the corner proof: the only frame source change adds stock at Z349..355, above the complete retained socket/rail/corbel band.')
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
    structural_allowed=wall_region.fuse(roof_region).fuse(clip_region)
    fits=selected_fit_regions(box)
    check('operator C3 and V69 selections are the current production geometry',
          e._retention.FIT_COUPON=='C3' and e._retention.RADIAL_AIR==0 and
          e._retention.AXIAL_AIR==0 and e._retention.ROOF_AIR==.48 and
          abs(e._seat.socket_diameter-6.9)<1e-9 and len(fits)==33,
          magnet_label=e._retention.FIT_COUPON,valve_socket_diameter_mm=e._seat.socket_diameter,
          front_top_magnet_pocket_count=1,front_top_valve_socket_count=len(fits)-1)
    fit_masks=cq.Compound.makeCompound([fit['allowed'] for fit in fits])
    fit_stock=[]
    fit_regions=[]
    fit_totals={'magnet':0.0,'valve':0.0}
    for fit in fits:
        stock=shells['front-top'].intersect(fit['allowed'])
        missing=volume(fit['expected'].cut(stock))
        excess=volume(stock.cut(fit['expected']))
        blocked=volume(fit['selected'].intersect(shells['front-top']))
        baseline_stock=volume(fit['allowed'].intersect(previous_front))
        added_volume=volume(stock)
        fit_stock.append(stock)
        fit_totals[fit['kind']]+=added_volume
        public={key:value for key,value in fit.items()
                if key not in ('previous','selected','allowed','expected')}
        public.update(allowed_region_bounds_mm=bounds(fit['allowed']),
            region='Exact previous cutter minus selected cutter, including the tangent teardrop roof where applicable.',
            allowed_change_volume_mm3=volume(fit['allowed']),
            selected_fit_added_stock_mm3=added_volume,
            missing_expected_fit_stock_mm3=missing,unexpected_fit_stock_mm3=excess,
            selected_opening_blocked_mm3=blocked,previous_fit_stock_mm3=baseline_stock)
        fit_regions.append(public)
        check(fit['name']+' retains the selected opening and exact fit stock',
              missing<1e-5 and excess<1e-5 and blocked<1e-5 and baseline_stock<1e-5,
              **{key:value for key,value in public.items() if key not in ('name','kind','region')})
    # The immediately preceding flat-wall export gives a direct current-shell
    # comparison. It has the complete prior wall and the 7.20 mm / .2/.4 fits.
    selected_addition=shells['front-top'].cut(previous_front)
    selected_removal=previous_front.cut(shells['front-top'])
    outside_fits=volume(selected_addition.cut(fit_masks))
    removed_fit=volume(selected_removal)
    check('front-top equals the bound flat-wall export outside exact selected fit regions',
          outside_fits<1e-5 and removed_fit<1e-5,
          previous_flat_front_top_step_sha256=sha(previous_front_path),
          added_stock_outside_fit_regions_mm3=outside_fits,removed_stock_mm3=removed_fit,
          fit_stock_volume_mm3=sum(fit_totals.values()),
          comparison_added_stock_mm3=volume(selected_addition))
    for name in shells:
        fit_overlap=sum(0.0 if separate(frame,stock) else volume(frame.intersect(stock))
                        for stock in fit_stock) if name=='front-top' else 0.0
        prior_overlap=prior_rows['frame seated in '+name]['overlap_mm3']
        check('frame seated in '+name,
              prior_overlap<1e-5 and fit_overlap<1e-5 and outside_fits<1e-5 and
              removed_fit<1e-5 and rear_proof['pass'],
              overlap_mm3=prior_overlap+fit_overlap,
              basis='Bound full seated native witness, direct current-shell difference restricted to the 33 exact fit regions, and direct upper-corner shell clearance checks.',
              selected_fit_stock_overlap_mm3=fit_overlap)
    print('Computing one shared front-top structural difference',flush=True)
    added_front_shape=shells['front-top'].cut(old_front)
    removed_front_shape=old_front.cut(shells['front-top'])
    outside_added=volume(added_front_shape.cut(structural_allowed).cut(fit_masks))
    outside_removed=volume(removed_front_shape.cut(structural_allowed))
    delta=outside_added+outside_removed
    check('front-top retained outside display wall, clip, roof and exact selected fit regions',delta<1e-5,
          delta_outside_declared_change_regions_mm3=delta,
          added_stock_outside_declared_regions_mm3=outside_added,
          removed_stock_outside_structural_regions_mm3=outside_removed,
          named_fit_regions=[fit['name'] for fit in fits],
          structural_region_bounds_mm={'display_wall':bounds(wall_region),
            'roof_clearance':bounds(roof_region),'relocated_clip':bounds(clip_region)},
          basis='The fit regions permit only exact old-minus-selected cutter additions; no selected-fit stock removal is excused.')
    added_front=volume(added_front_shape)
    removed_front=volume(removed_front_shape)
    prior_frame=cq.importers.importStep(str(correction_baseline/'funnel-frame.step')).val().translate((0,ff.center_y,floor))
    prior_metric=prior_rows['display wall stock and occupied enclosure air quantified']
    # Exact bounded corners update the retained frame-difference witness. The
    # native mass-property difference independently supplies the total metric.
    added_frame=prior_metric['added_frame_stock_mm3']+sum(volume(g.cut(prior_frame)) for g in corner_additions)
    removed_frame=prior_metric['removed_frame_stock_mm3']-sum(volume(g.intersect(prior_frame)) for g in corner_additions)
    front_net=volume(shells['front-top'])-volume(old_front)
    frame_net=volume(frame)-volume(prior_frame)
    total_fit=sum(fit_totals.values())
    total_air=(front_net+frame_net)/1000
    residual=(added_front-removed_front+added_frame-removed_frame)-(front_net+frame_net)
    check('display wall stock and occupied enclosure air quantified',abs(residual)<.05,
          added_front_top_stock_mm3=added_front,removed_front_top_stock_mm3=removed_front,
          front_top_air_occupied_ml=front_net/1000,
          selected_magnet_fit_stock_mm3=fit_totals['magnet'],
          selected_valve_fit_stock_mm3=fit_totals['valve'],
          selected_fit_air_occupied_ml=total_fit/1000,
          display_wall_and_roof_front_top_air_occupied_ml=(front_net-total_fit)/1000,
          added_frame_stock_mm3=added_frame,removed_frame_stock_mm3=removed_frame,
          frame_air_occupied_ml=frame_net/1000,
          square_rear_corner_added_stock_mm3=sum(volume(g) for g in corner_additions),
          wall_and_frame_air_occupied_ml=total_air-total_fit/1000,
          net_enclosure_air_occupied_ml=total_air,
          native_volume_integration_relative_tolerance=1e-9,
          difference_witness_mass_closure_residual_mm3=residual,
          scope='Combined rigid front-top and frame native solid volume relative to the hash-bound wide flush-roof baseline. Selected-fit stock is quantified separately; this is enclosure air, not liquid funnel capacity.')
    addition,channel=e._cable_clip.local_geometry(embed=0,
                         wall_thickness=wall_y-box.pack.collet_plate['aft_y'])
    location=cq.Location(cq.Plane(origin=flat_wall['clip_origin_mm'],xDir=(0,1,0),normal=(1,0,0)))
    clip=addition.cut(channel).moved(location)
    channel=channel.moved(location)
    clip_missing=volume(clip.cut(shells['front-top']))
    channel_blocked=volume(channel.intersect(shells['front-top']))
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
        missing=volume(witness.cut(shells['front-top']))
        check(f'complete {e.front_top_flank_t:g} mm roof flank {sign:+g}',missing<1e-5,
              nominal_section_mm=e.front_top_flank_t,missing_stock_mm3=missing,
              witness_y_mm=[r['front']+10,box.y_joint-e.slide_slip],witness_z_mm=[346+e.slide_slip,box.outer[5]])
    solid,cavity,meta=ff.funnel.build_solids()
    capacity=volume(cavity.intersect(ff.funnel._box(600,600,meta['end_z'],meta['top_z'],0,0)))/1000
    check('silicone capacity retained',abs(capacity-ff.funnel.capacity_ml)<.25,
          native_capacity_ml=capacity,nominal_capacity_ml=ff.funnel.capacity_ml,capacity_loss_ml=0,
          basis='Silicone source and cavity geometry retained; only rigid wall and frame boundaries changed.')
    assembly_path=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    assembly=import_assembly(str(assembly_path))
    names=[]
    for label,stock in [('frame rear corner '+str(i),g) for i,g in enumerate(corner_additions)]+[
            ('front-top',added_front_shape)]:
        for name,(s,_color) in assembly.items():
            if name.startswith('enclosure') or name=='funnel-frame':continue
            if separate(stock,s):continue
            names.append(label+'/'+name);empty('added '+label+' stock clears '+name,stock,s)
    for name in ('funnel','funnel-cover'):
        prior_row=prior_rows['added frame stock clears '+name]
        check('retained added frame stock clears '+name,prior_row['pass'] and rear_proof['pass'],
              overlap_mm3=prior_row['overlap_mm3'],
              basis='Retained native added-stock witness; silicone source is unchanged and current added corners receive separate current-assembly checks.')
    paths=[Path(__file__),box_path,frame_path,frame_path.with_suffix('.stl'),assembly_path,
           ENC/'enclosure.py',FUNNEL/'funnel_frame.py',FUNNEL/'funnel.py',Path(e._cable_clip.__file__),
           Path(e._retention.__file__),Path(e._seat.__file__),rear_path,generation_path,
           ENC/'magnet-retention/fit-coupons/physical-fit-selection.json',
           *[ENC/f'enclosure-{n}.{ext}' for n in shells for ext in ('step','stl')]]
    result=dict(schema=2,checks=rows,roof_datums_mm=r,selected_fit_change_regions=fit_regions,
                retained_native_proof=retained,
                nearby_installed_members_checked=names,
                source_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},
                retained_baseline_sha256={p.name:sha(p) for p in baseline.glob('*.step')},
                flat_wall_baseline_sha256={p.name:sha(p) for p in correction_baseline.glob('*.step')},
                selected_fit_baseline_sha256={'front_top_step':sha(previous_front_path),
                                             'funnel_frame_step':sha(previous_frame_path)},
                scope='Native roof, flat wall, exact selected C3/V69 fit changes and retained mating geometry. Seated/lower/bearing witnesses are explicitly hash-bound and extended by bounded native corner and current fit-region comparisons. Current added front-top and corner stock is checked against installed bodies from the named assembly; full motion, load capacity, physical fit, print finish and support removal remain separate qualifications.')
    result['pass']=all(row['pass'] for row in rows)
    (HERE/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n')
    if not result['pass']:raise ValueError([r['check'] for r in rows if not r['pass']])

if __name__=='__main__':main()
