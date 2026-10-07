"""Lid-rooted lower seats and dressed closed ties for the check and split tee.

The check bears on its keyed hex flats; the tee bears on its measured fixed
run collar. Both lower seats have continuous stock into the existing cap lid.
The exact tie tunnels keep three-millimetre fore/aft webs and bottom stock.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, math, sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts/check-tee'
sys.path[:0]=[str(STUDY),str(STUDY/'pump'),str(HERE)]
import audit
import generate as G
import fluid_hosts as F
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources
from structure.received_native import ReceivedNative


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(x0,y0,z0,x1,y1,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))


def ring_profile(points,width,centre_y,inner_offset,outer_offset):
    outside=cq.Workplane('XZ').polyline(points).close().wire().offset2D(outer_offset).extrude(width).val()
    inside=cq.Workplane('XZ').polyline(points).close().wire().offset2D(inner_offset).extrude(width).val()
    return outside.cut(inside).translate((0,centre_y+width/2,0)).clean()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true',
                        help='Verify held complete native articles against the recipe without exporting.')
    args=parser.parse_args()
    received=ReceivedNative(ROOT,json.loads((HERE/'check-tee-candidate.json').read_bytes()))if args.check else None
    sources=proof_sources.snapshot(__file__,G.__file__,F.__file__,
                                  sys.modules[ReceivedNative.__module__].__file__)
    models,records,changed,mates,inputs=audit.collect()
    manifest_contents=dict(inputs.content_sha256)
    manifest_files={k:STUDY/folder/file for k,folder,file in [
        ('funnel','funnel','candidate.json'),('pump','pump','candidate.json'),
        ('pump-fluid24','pump','fluid24-candidate.json'),('routing','routing','candidate.json'),
        ('structure','structure','candidate.json'),('mounts','mounts','candidate.json'),
        ('wiring','wiring','candidate.json'),('fluid-mounts','mounts','fluid-candidate.json'),
        ('body-mounts','mounts','body-candidate.json'),('water5-mounts','mounts','water5-hosts.json'),
        ('tube-hosts','routing','tube-hosts.json'),('roof-hatch','structure','roof-hatch.json'),
        ('scene-stock','structure','scene-stock.json')]}
    for relative in ['routing/co2-candidate.json','wiring/control-reserves.json',
                     'wiring/control-fanouts-check.json','wiring/controls-candidate.json',
                     'wiring/power-candidate.json']:
        path=STUDY/relative
        if path.exists():
            manifest=json.loads(path.read_text());inputs[str(path.relative_to(ROOT))]=sha(path)
            manifest_contents[str(path.relative_to(ROOT))]=content_sha256(manifest)
            manifest_files[relative]=path
            for name,r in manifest.get('parts',{}).items():
                records[name]=r;models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
    models={n:s for n,s in models.items()if not n.startswith(('check-lid-','tee-lid-','check-retention-','tee-retention-'))}
    routing=json.loads((STUDY/'routing/candidate.json').read_text())
    check=models['gasher-co2'];tee=models['water-split']
    cb=G.bounds(check);cx=(cb[0]+cb[3])/2;cy=(cb[1]+cb[4])/2
    cz=routing['ports']['gasher-co2']['inlet']['pos'][2]
    tx,tail_y,tz=routing['ports']['water-split']['supply']['pos']
    ty=routing['ports']['water-split']['to-flavor']['pos'][1]
    sys.path.insert(0,str(ROOT/'hardware/reference/water-split'))
    import water_split as T
    sources.update(proof_sources.snapshot(T.__file__,T.tee.__file__))
    station,radius,span=T.clearance_seat(9.5,2.5)
    # Use the measured aft fixed collar. Its full pressed collet envelope
    # remains outside this seat and the lower manifold cable ribbon is clear.
    collar_y=ty+station[0][1]
    shapes={};cutters={};owners={};properties={}
    r=8.5+.15/math.sin(math.pi/3);drop=r*math.sin(math.pi/3)
    lower=[(cx-r,cz),(cx-r/2,cz-drop),(cx+r/2,cz-drop),
           (cx+r,cz),(cx+r,cz+20),(cx-r,cz+20)]
    pocket=(cq.Workplane('XZ').polyline(lower).close().extrude(11.826).val()
            .translate((0,cy+11.826/2,0)))
    seat=box(cx-7.4,cy-11.826/2,250.8,cx+6.3,cy+11.826/2,cz-3.).cut(pocket)
    hex_points=[(cx+8.5*math.cos(k*math.pi/3),cz+8.5*math.sin(k*math.pi/3))for k in range(6)]
    band=ring_profile(hex_points,4.826,cy,0.,1.)
    tunnel=ring_profile(hex_points,5.826,cy,-.2,1.2)
    head=box(cx-6,cy-5,cz+8.15,cx+6,cy+5,cz+14.15)
    tie=band.fuse(head).clean();seat=seat.cut(tunnel).clean()
    shapes['check-lid-seat']=seat;shapes['check-retention-tie']=tie
    cutters['check-lid-tie-tunnel']=(tunnel,'cold-core-lid')
    owners['check-lid-seat']=owners['check-retention-tie']='gasher-co2'
    properties['check']={'axis_mm':[cx,cy,cz],'seat_width_mm':11.826,
                         'tie_width_mm':4.826,'tie_thickness_mm':1.,
                         'tunnel_width_mm':5.826,'axial_web_mm':3.,
                         'minimum_bottom_stock_mm':cz-drop-1.2-250.8,
                         'hex_normal_slip_mm':.15}
    # A lower bearing pad needs no outboard radial wall. This keeps the exact
    # 16.5mm purchased collar and1mm tie within the original215mm enclosure.
    width=9.5;clear_r=radius+.15
    if abs(tz-265.)>1e-6:
        raise ValueError('The direct tee seat requires the selected axisZ265.0.')
    tee_floor=252.5
    seat=box(87.5,collar_y-width/2,tee_floor,tx+7.4,collar_y+width/2,tz-3.25)
    bore=cq.Solid.makeCylinder(clear_r,width,cq.Vector(tx,collar_y-width/2,tz),cq.Vector(0,1,0))
    seat=seat.cut(bore)
    # Keep the bought collar's9.5mm bearing pad. The complete belt occupies
    # the separately measured, narrower fixed run-root patch, so its exterior
    # has1.25mm running air inside the original3mm side-wall skin.
    root_lo,root_hi=T.tee.RUN_ROOT_BAND
    root_radius=T.tee.ARM_R
    root_y=ty+(root_lo+root_hi)/2
    root_pad=box(87.5,root_y-width/2,tee_floor,tx+7.4,root_y+width/2,tz-3.25)
    root_pad=root_pad.cut(cq.Solid.makeCylinder(clear_r,width,
        cq.Vector(tx,root_y-width/2,tz),cq.Vector(0,1,0)))
    root_bearing=box(87.5,ty+root_lo,tee_floor,tx+7.4,ty+root_hi,tz-3.25)
    root_bearing=root_bearing.cut(cq.Solid.makeCylinder(root_radius+.15,root_hi-root_lo,
        cq.Vector(tx,ty+root_lo,tz),cq.Vector(0,1,0)))
    seat=seat.fuse(root_pad).fuse(root_bearing)
    band=cq.Solid.makeCylinder(root_radius+1.,2.5,cq.Vector(tx,root_y-1.25,tz),cq.Vector(0,1,0)).cut(
        cq.Solid.makeCylinder(root_radius,2.5,cq.Vector(tx,root_y-1.25,tz),cq.Vector(0,1,0)))
    tunnel=cq.Solid.makeCylinder(root_radius+1.2,3.5,cq.Vector(tx,root_y-1.75,tz),cq.Vector(0,1,0)).cut(
        cq.Solid.makeCylinder(root_radius-.2,3.5,cq.Vector(tx,root_y-1.75,tz),cq.Vector(0,1,0)))
    a,b=cq.Vector(tx,root_y,tz),cq.Vector(tx,root_y+1,tz)
    head=box(tx-4,root_y+.4,tz+9.4,tx+4,root_y+8.4,tz+14.4).rotate(a,b,-30.)
    neck=box(tx-.5,root_y-1.25,tz+7.5,tx+.5,root_y+1.25,tz+9.65).rotate(a,b,-30.)
    tie=band.fuse(head).fuse(neck)
    seat=seat.cut(tunnel)
    gas_channel=cq.Solid.makeCylinder(4.175,90,cq.Vector(83.,380,257.575),cq.Vector(0,1,0))
    co2_path=STUDY/'routing/co2-candidate.json'
    if co2_path.exists():
        co2=json.loads(co2_path.read_text())
        exact=co2.get('clearance_cutters',{}).get('tube-co2-0')
        if exact:
            # Cut the actual stock-radius local S after the seat and lid are
            # fused. The ordinary cylinder alone does not cover its fore run.
            exact_channel=cq.Shape.importBrep(str(ROOT/exact['brep']))
            seat=seat.cut(exact_channel)
            cutters['tee-lid-exact-gas-clearance']=(exact_channel,'cold-core-lid')
    seat=seat.cut(gas_channel).clean()
    # The inherited lower shell corner sweeps over the added outboard toe.
    # The root tie tunnel retains3.2mm bottom stock. A raised outer toe provides positive factory running air
    # above that corner and retains a complete3mm bought-body bearing floor.
    outer_rib_relief=box(97.5,root_y-width/2-.01,250.4,104.5,
                         collar_y+width/2+.01,253.7)
    toe_relief=box(95.25,root_y-width/2-.01,250.4,104.5,
                   collar_y+width/2+.01,253.6)
    for name,tool in [('tee-lid-outer-rib-relief',outer_rib_relief),
                      ('tee-lid-factory-toe-relief',toe_relief)]:
        seat=seat.cut(tool)
        cutters[name]=(tool,'cold-core-lid')
    shapes['tee-lid-seat']=seat;shapes['tee-retention-tie']=tie
    cutters['tee-lid-tie-tunnel']=(tunnel,'cold-core-lid')
    cutters['tee-lid-gas-portal']=(gas_channel,'cold-core-lid')
    owners['tee-lid-seat']=owners['tee-retention-tie']='water-split'
    properties['tee']={'axis_mm':[tx,ty,tz],'fixed_aft_collar_y_mm':collar_y,
        'measured_fixed_patch_y_mm':[ty+12.,ty+15.1],
        'measured_fixed_root_patch_y_mm':[ty+root_lo,ty+root_hi],
        'fixed_root_radius_mm':root_radius,'tie_station_y_mm':root_y,
        'tie_band_y_mm':[root_y-1.25,root_y+1.25],
        'seat_width_mm':width,'tie_width_mm':2.5,'tie_thickness_mm':1.,
        'tunnel_width_mm':3.5,'axial_web_mm':3.,'minimum_bottom_stock_mm':tz-root_radius-1.2-253.6,
        'bore_slip_mm':.15,'root_overlap_into_lid_x_mm':3.,
        'ribbon_vertical_air_mm':1.25,'low_gas_air_mm':1.325,
        'gas_portal_axis_mm':[83.,0,257.575],'gas_portal_diameter_mm':8.35,
        'floor_base_z_mm':tee_floor,'outboard_floor_z_mm':253.7,
        'factory_toe_x_min_mm':95.25,'factory_toe_floor_z_mm':253.6,
        'factory_toe_running_air_mm':.2,
        'factory_toe_bearing_floor_mm':tz-clear_r-253.6,
        'outboard_bearing_web_minimum_stock_mm':tz-math.sqrt(clear_r**2-(97.5-tx)**2)-253.7,
        'tie_head_clock_about_y_deg':-30.,'tie_head_nominal_size_mm':[8.,8.,5.],
        'tie_head_radial_offset_mm':9.4,'tie_head_axial_min_y_mm':root_y+.4,
        'tie_outboard_extent_x_mm':tx+root_radius+1.,
        'tie_running_air_to_chase_mm':104.5-(tx+root_radius+1.)}
    # Fixed lid bodies pass a moving back-top. This local service chase gives
    # their exact occupied exterior the full rear-column approach while
    # preserving the exterior3mm side wall and every below-cap interface.
    tee_body=seat.fuse(tie).fuse(tee)
    b=G.bounds(tee_body)
    slide=box(b[0]-1,b[1]-267.3,253.4,104.5,b[4]+1,b[5]+1)
    cutters['tee-lid-factory-slide-clearance']=(slide,'enclosure-back-top')
    if received:
        if set(shapes)!=set(received.manifest['parts'])or set(cutters)!=set(received.manifest['clearance_cutters']):
            raise ValueError('Held check/TEE part or cutter names differ from the authoritative recipe')
        shapes={name:received.shape(name,shape)for name,shape in shapes.items()}
        cutters={name:(received.shape(name,shape),owner)for name,(shape,owner)in cutters.items()}
        slide=cutters['tee-lid-factory-slide-clearance'][0]
    models['enclosure-back-top']=models['enclosure-back-top'].cut(slide)
    check_rows=[];native_inputs={}
    for n,r in records.items():
        if r and n in models:native_inputs[n]={'brep':r['brep'],'sha256':sha(ROOT/r['brep'])}
    for name,s in shapes.items():
        bad=[];near=[];b=G.bounds(s)
        for other,t in models.items():
            if other=='cold-core/foam-cap-lid-top' and name.endswith('seat'):continue
            if not audit.broad(b,G.bounds(t),1):continue
            gap=s.distance(t)
            if gap>=1-1e-6:continue
            common=G.overlap(s,t)if gap<1e-6 else 0.
            row={'other':other,'gap_mm':gap,'common_mm3':common};near.append(row)
            if common>.01:bad.append(row)
        for other,t in shapes.items():
            if other<=name:continue
            common=G.overlap(s,t)
            if common>.01:bad.append({'other':other,'common_mm3':common})
        row={'part':name,'pass':not bad and s.isValid() and len(s.Solids())==1,
             'valid':s.isValid(),'solids':len(s.Solids()),'blockers':bad,'close_pairs':near}
        check_rows.append(row);print(name,row,flush=True)
    joined=models['cold-core/foam-cap-lid-top']
    for n in ['check-lid-seat','tee-lid-seat']:joined=joined.fuse(shapes[n])
    for tool,owner in cutters.values():
        if owner=='cold-core-lid':joined=joined.cut(tool)
    check_rows.append({'check':'seats and native lid join into one solid',
                       'pass':joined.isValid() and len(joined.Solids())==1,
                       'valid':joined.isValid(),'solids':len(joined.Solids())})
    for label,p in properties.items():
        check_rows.append({'check':label+' minimum3mm tunnel floor and axial webs',
                           'pass':p['minimum_bottom_stock_mm']>=3-1e-6 and p['axial_web_mm']>=3,
                           'bottom_stock_mm':p['minimum_bottom_stock_mm'],'axial_web_mm':p['axial_web_mm']})
    check_rows.append({'check':'tee outboard bearing ribs retain3mm stock and floor air',
                       'pass':properties['tee']['outboard_bearing_web_minimum_stock_mm']>=3.,
                       'minimum_stock_mm':properties['tee']['outboard_bearing_web_minimum_stock_mm'],
                       'floor_air_mm':properties['tee']['outboard_floor_z_mm']-253.4})
    check_rows.append({'check':'tee factory toe retains3mm bought-body bearing and positive floor air',
                       'pass':properties['tee']['factory_toe_bearing_floor_mm']>=3.-1e-6,
                       'bearing_floor_mm':properties['tee']['factory_toe_bearing_floor_mm'],
                       'running_air_mm':properties['tee']['factory_toe_running_air_mm']})
    import baseline
    accepted_lid=baseline.read(names=['cold-core/foam-cap-lid-top'])['cold-core/foam-cap-lid-top']
    for name,tool in [('tee-lid-outer-rib-relief',outer_rib_relief),
                      ('tee-lid-factory-toe-relief',toe_relief)]:
        removed=G.overlap(accepted_lid,tool)
        check_rows.append({'check':name+' preserves complete accepted cap-lid interface',
                           'accepted_stock_removed_mm3':removed,'pass':removed<.0001})
    check_rows.append({'check':'complete tee belt stays on measured fixed root patch with positive wall air',
                       'pass':root_y-1.25>=ty+root_lo and root_y+1.25<=ty+root_hi
                               and properties['tee']['tie_running_air_to_chase_mm']>=1.,
                       'measured_patch_y_mm':properties['tee']['measured_fixed_root_patch_y_mm'],
                       'belt_y_mm':properties['tee']['tie_band_y_mm'],
                       'running_air_mm':properties['tee']['tie_running_air_to_chase_mm']})
    OUT.mkdir(parents=True,exist_ok=True)
    def record(name,s,detail):
        if received:return received.record(name,s)
        path=OUT/(name+'.brep');s.exportBrep(str(path))
        return {'brep':str(path.relative_to(ROOT)),'sha256':sha(path),'role':'structure',
                'bounds_mm':G.bounds(s),'detail':detail,'valid':s.isValid(),'solids':len(s.Solids())}
    parts={n:record(n,s,'Lid-rooted lower keyed/fixed-collar seat with3mm fore/aft tunnel webs and bottom stock.'if n.endswith('seat')else
        'Closed nominal nylon tie and conservative locking head:4.826×1mm wide check band or2.5×1mm tee band; dressed before roof closure.')for n,s in shapes.items()}
    cutter_records={n:{**record(n,s,'Exact tie passage or full rear-column/factory-entry clearance.'),'print_owner':owner,
                       'minimum_exterior_wall_stock_mm':3. if owner=='enclosure-back-top' else None}
                    for n,(s,owner) in cutters.items()}
    root_coupons={}
    for label,a,b in [('fore',collar_y-width/2,collar_y-1.75),('aft',collar_y+1.75,collar_y+width/2)]:
        for kind,x0,x1,z0,z1 in [('lid-bond',87.5,90.5,252.5,253.4),
                                ('factory-toe-bearing',95.25,96.25,253.6,256.6),
                                ('outboard-bearing',97.5,tx+7.4,253.7,256.7)]:
            name='tee-'+kind+'-coupon-'+label
            coupon=box(x0,a,z0,x1,b,z1)
            own_missing=abs(coupon.cut(shapes['tee-lid-seat']).Volume())
            joined_missing=abs(coupon.cut(joined).Volume())
            check_rows.append({'check':name+' complete native load stock',
                               'own_missing_mm3':own_missing,'joined_missing_mm3':joined_missing,
                               'pass':own_missing<.0001 and joined_missing<.0001})
            root_coupons[name]={**record(name,coupon,'Exact positive lid bond or3mm outboard bearing-stock witness required after final parent fusion and recuts.'),
                               'print_owner':'cold-core-lid','host_part':'tee-lid-seat',
                               'require_missing_volume_mm3_below':.0001}
    for name in ['tee-lid-factory-slide-clearance']:
        cutter_records[name].update(factory_upper_bay_channel=True,
                                   preserved_frame_receiver_z_min_mm=303.9)
    if received:
        check_rows.extend(received.checks)
        native_inputs.update(received.inputs)
    result={'parts':parts,'lid_fuse_part_names':['check-lid-seat','tee-lid-seat'],
        'joined_root_coupons':root_coupons,
        'clearance_cutters':cutter_records,'checks':check_rows,'pass':all(r['pass']for r in check_rows),
        'native_inputs':native_inputs,'manifest_sha256':inputs,
        'manifest_content_sha256':manifest_contents,'source_inputs':sources,'properties':properties,
        'intended_contacts':[['check-lid-seat','cold-core/foam-cap-lid-top'],['tee-lid-seat','cold-core/foam-cap-lid-top']],
        'factory_sequence':['Seat and retain the check and purchased TEE on the open core before the back-column approach. The TEE toe has0.2mm native running air above the inherited lower corner, and its outer ribs clear the bay floor by0.3mm. Its bonded inboard spine and full-depth upper-bay chase preserve every below-cap interface.',
                            'Thread and close the ties before the column enters. The complete2.5mm TEE belt bears on the measured fixed root atY409.85..412.35, with its complete locking head clocked30degrees inboard. The belt retains1.25mm running air to the outboard chase; opposite tube ends stay free and accessible on the open cart. The complete column motion has separate evidence in structure/factory-slide-check.json.',
                            'Keep crossing supply/gas/flavor links and lower lead exits free until the column and purchased TEE are seated. Final installed flexible occupancy is audited independently.'],
        'qualification_limits':['Tie/head envelopes are nominal conservative reservations; actual purchased head dimensions, tie tension, creep, vibration and factory dressing require physical qualification.',
                                'Lower seats establish geometric load paths. They do not establish allowable insert load, component retention force or appliance lifetime.',
                                'The0.2mm temporary running air above the inherited lower shell corner requires physical tolerance and factory-motion qualification.',
                                'The measured fixed run-root band supports the complete nominal belt. Actual tie/head stock, neck shape, installation dressing and retention force require physical qualification; the head model is a conservative reservation, not a measurement of purchased locking detail.']}
    drift=[n for n,r in native_inputs.items()if sha(ROOT/r['brep'])!=r['sha256']]
    result['source_drift']=drift+proof_sources.changed(sources)
    result['geometry_pass']=result['pass']
    result['manifest_drift']=[k for k,h in manifest_contents.items()if manifest_content_sha256(ROOT/k)!=h]
    result['pass']=result['pass'] and not result['source_drift'] and not result['manifest_drift']
    if received and content_sha256(result)!=content_sha256(received.manifest):
        raise ValueError('Received check/TEE refresh changed complete held manifest content')
    (HERE/'check-tee-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass':result['pass'],'failed':[r for r in check_rows if not r['pass']]}),flush=True)


if __name__=='__main__':main()
