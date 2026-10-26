"""Manual native scope extension across the landed M5 enclosure-joint geometry."""
from pathlib import Path
import argparse
import json

import refine_review as refinement
import review as r


def swept(bounds, offset):
    return [value + (min(0.,offset[i//2]) if i%2 == 0 else max(0.,offset[i//2]))
            for i,value in enumerate(bounds)]


def domain_reading(label, moving, fixed, offset):
    moving_bounds = swept(r.shape_bounds(r.compound(moving)), offset)
    rows = []
    for name, shape in fixed.items():
        for index, component in enumerate(shape.Solids()):
            bounds = r.shape_bounds(component)
            gap = r.box_gap(moving_bounds,bounds)
            row = dict(fixed=name, component=index, fixed_bounds_mm=bounds,
                       swept_axis_separation_mm=gap)
            if gap <= r.DISTANCE_MARGIN:
                row['native_path'] = r.translation(label,moving,
                    {f'{name}-{index}':component},offset)
                if row['native_path']['status'] != 'clear_continuous_native_distance_intervals':
                    raise RuntimeError(f'Unresolved native joint-domain path: {label}: {row}')
            rows.append(row)
    return dict(label=label, moving_bodies=list(moving), start_offset_mm=offset,
                swept_moving_bounds_mm=moving_bounds, fixed_components=rows,
                empty_fixed_bodies=[name for name,shape in fixed.items() if not shape.Solids()],
                status='clear_complete_swept_domains')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old-top',type=Path,default=Path(
        '/tmp/pump-mount-before-wing-cleanout-08cc/enclosure-front-top.step'))
    parser.add_argument('--landed-top',type=Path,default=Path(
        '/tmp/pump-m5-main-before-cleanouts/enclosure-front-top.step'))
    parser.add_argument('--joint-review',type=Path,default=r.ENC/'y-seam-100-review.json')
    parser.add_argument('--reading',type=Path,default=r.HERE/'native-review.json')
    parser.add_argument('--delta-directory',type=Path,default=Path('/tmp/hsm-pump-main-joint-deltas'))
    parser.add_argument('--pump-stock-sha',default='08cc201935f6bf345f48946be255b62d1cd8806ac3ebfa5c94fbf1675af7e290',
                        help='identified complete added-pump-stock reading retained by the predecessor')
    args=parser.parse_args()
    prior_sha=r.sha(args.reading)
    reading=json.loads(args.reading.read_text())
    joint_sha=r.sha(args.joint_review)
    joint=json.loads(args.joint_review.read_text())
    old,old_id=refinement.read_native(args.old_top)
    landed,landed_id=refinement.read_native(args.landed_top)
    if landed_id['sha256'] != joint['input_sha256'][str((r.ENC/'enclosure-front-top.step').relative_to(r.ROOT))]:
        raise RuntimeError('Landed front-top differs from the identified joint review')
    added,removed=refinement.delta(old,landed)
    hardware,cache=r.native_hardware(r.ROOT/'hardware/manifold-layout/enclosure-assembly.step',
        reading['native_hardware_cache']['assembly_sha256'])
    bottom,bottom_id=refinement.read_native(r.ENC/'enclosure-front-bottom.step')
    if bottom_id['sha256'] != joint['input_sha256'][str((r.ENC/'enclosure-front-bottom.step').relative_to(r.ROOT))]:
        raise RuntimeError('Front-bottom differs from the identified joint review')
    bottom_added,bottom_removed=refinement.delta(hardware['enclosure-front-bottom'],bottom)
    args.delta_directory.mkdir(parents=True,exist_ok=True)
    cached={}
    for label,shape in (('top-added',added),('top-removed',removed),
                        ('bottom-added',bottom_added),('bottom-removed',bottom_removed)):
        path=args.delta_directory/(label+'.brep')
        shape.exportBrep(str(path))
        cached[label]=dict(path=str(path),sha256=r.sha(path),volume_mm3=r.volume(shape),
                           bounds_mm=refinement.solid_bounds(shape))
    (args.delta_directory/'index.json').write_text(json.dumps(dict(
        old_top=old_id,landed_top=landed_id,current_bottom=bottom_id,
        original_hardware_cache=cache,bodies=cached),indent=2)+'\n')
    box,_=r._box_spec.read(r.enc.Box,r.enc.Bound,(r.enc.Pack,r.enc.PortField,r.enc.Nameplate))
    retainer,retainer_id=refinement.read_native(r.ENC/'enclosure-pump-retainer.step')
    pump_names=[f'pump-{p}-{part}' for p in ('a','b') for part in ('head','boss','motor')]
    stub_ids=[cid for cid,_a,_b,how in r.manifold.SEGMENTS if how in r.manifold.BARB_OF]
    unit={'enclosure-pump-retainer':retainer,**{name:hardware[name] for name in pump_names},
          **{f'tube-fluid-{cid}':hardware[f'tube-fluid-{cid}'] for cid in stub_ids}}
    d=r.mount.datums(r.enc,box)
    casings={f'casing-x{x:g}':r.cq.Solid.makeCylinder(r.enc._tray.fitting_w/2.,4.305,
        r.cq.Vector(x,d['head_y']+27.,z),r.cq.Vector(0.,1.,0.))
        for x,z in box.pack.collet_plate['holes']}
    group_names={'tee-'+name.lower() for name in r.manifold.PUMP_JUNCTIONS}
    group_names.update(f'{part}-v-{v}' for part in ('valve','coil') for v in ('e','f','h','i'))
    group_names.update(f'tube-fluid-{cid}' for cid,_a,_b,how in r.manifold.SEGMENTS if how.startswith('fore-'))
    groups={name:hardware[name] for name in group_names}
    drivers={f'driver-x{f["x"]:g}':r.cq.Solid.makeCylinder(1.75,70.,
        r.cq.Vector(f['x'],f['y'],f['head_seat_z']-70.)) for f in r.mount.fasteners(r.enc,box)}
    fixed={'landed-M5-top-added-stock':added}
    paths=[domain_reading('M5 top vs motor-first pump unit',unit,fixed,(0.,0.,-130.)),
           domain_reading('M5 top vs declared casing loading',casings,fixed,(0.,0.,-130.)),
           domain_reading('M5 top vs prepared fore groups',groups,fixed,
               (0.,reading['tee_group_approaches']['conservative_test_travel_mm'],0.)),
           domain_reading('M5 top vs underside drivers',drivers,fixed,(0.,0.,0.)),
           domain_reading('M5 top vs pump closing allowance',unit,fixed,(0.,0.,.4))]
    travel=reading['changed_mount_chassis_slide']['total_travel_mm']
    paths.append(domain_reading('Changed front-bottom vs installed pump-mount closing slide',
        {**unit,**casings},{'current-front-bottom-added-stock':bottom_added},(0.,-travel,0.)))
    lower={name:hardware[name] for name in ('compressor','condenser+fan','fuse-clamp','mq6-sensor')}
    lower['enclosure-front-bottom']=bottom
    paths.append(domain_reading('Added M5 top rides aft over the current lower assembly',
        {'landed-M5-top-added-stock':added},lower,(0.,-travel,0.)))
    old_stock=next(part for entry in reading['printed_stock_refinements'] for part in entry['parts']
        if part['refined_native']['sha256']==args.pump_stock_sha and 'added_bounds_mm' in part)
    old_stock_swept=swept(old_stock['added_bounds_mm'],(0.,-travel,0.))
    bottom_gap=(r.box_gap(old_stock_swept,r.shape_bounds(bottom_added))
                if bottom_added.Solids() else None)
    prior_joint_bounds=[dict(native=part['refined_native'],
        swept_bounds_mm=swept(part['native_deltas']['top-added']['bounds_mm'],(0.,-travel,0.)))
        for entry in reading['printed_stock_refinements'] for part in entry['parts']
        if part.get('native_deltas',{}).get('top-added',{}).get('bounds_mm') is not None]
    for row in prior_joint_bounds:
        row['new_front_bottom_axis_gap_mm']=(r.box_gap(row['swept_bounds_mm'],r.shape_bounds(bottom_added))
                                             if bottom_added.Solids() else None)
    neighbors=r.contacts({'landed-M5-top-added-stock':added},
        {name:hardware[name] for name in ('display','funnel-frame')})
    if (neighbors or (bottom_gap is not None and bottom_gap<=r.DISTANCE_MARGIN)
            or any(row['new_front_bottom_axis_gap_mm'] is not None
                   and row['new_front_bottom_axis_gap_mm']<=r.DISTANCE_MARGIN for row in prior_joint_bounds)):
        raise RuntimeError(f'Unresolved landed-M5 interaction: {neighbors}, stock gap={bottom_gap}')
    if r.sha(args.joint_review)!=joint_sha:
        raise RuntimeError('Joint review changed during its read')
    result=dict(part='enclosure-front-top',original_native=old_id,refined_native=landed_id,
        bearing_and_screw_guard_top_z_mm=reading['datums']['flange_z']+r.enc._tray.boss_depth+.4,
        landed_joint_review=dict(path=r.path_label(args.joint_review),sha256=joint_sha,
                                 identified_input_sha256=joint['input_sha256']),
        hardware_cache=cache,moving_retainer=retainer_id,current_front_bottom=bottom_id,
        native_deltas=cached,complete_domain_readings=paths,
        prior_added_pump_stock_swept_bounds_mm=old_stock_swept,
        prior_added_pump_stock_to_new_front_bottom_axis_gap_mm=bottom_gap,
        prior_added_pump_stock_native=old_stock['refined_native'],
        prior_joint_added_stock_swept_domains=prior_joint_bounds,
        added_M5_stock_display_and_funnel_contacts=neighbors,
        scope='The original rigid-path input identities are retained. Landed M5 top additions '
            'are separated from every applicable complete swept pump/casing/fore-group/driver '
            'domain and queried against installed display/funnel neighbors. The changed '
            'front-bottom is compared directly with its original cached body and its added '
            'stock is separated from the complete pump-mount closing-slide domains. The '
            'other 32 named hardware bodies require their own final-subset agreement. '
            'This extends pump-mount rigid-path scope; the M5 joint keeps its identified '
            'separate review and physical qualification limits.')
    reading['printed_stock_refinements'].append(dict(role='landed_main_M5_scope_extension',
        verification_source_sha256=r.sha(Path(__file__).resolve()),prior_reading_sha256=prior_sha,
        status='native_refinement_clear',parts=[result]))
    temporary=args.reading.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(reading,indent=2)+'\n')
    temporary.replace(args.reading)
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
