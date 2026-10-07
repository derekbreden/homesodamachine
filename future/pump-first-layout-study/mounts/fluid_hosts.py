"""Roof-rooted retention for the actual ASSE barrel and measured meter collars.

The brass vent remains downward. Wide ties carry the ASSE into keyed upper
hex seats; narrow ties retain the meter's two fixed collars. Separate collets,
the vent fall and the measured meter lead root stay exposed.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,math,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts/fluid'
sys.path.insert(0,str(STUDY))
import baseline
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources
from structure import received_native

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def bounds(s):
    b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def broad(a,b,pad=0):
    return all(a[i]<=b[i+3]+pad and b[i]<=a[i+3]+pad for i in range(3))

def common(a,b):
    if not broad(bounds(a),bounds(b)):return 0.
    return abs(a.intersect(b,tol=.0001).Volume(tol=1e-9))

def asse_seat(x,y,z,width,root=343.):
    # The barrel's fixed vent keys its clock. Offset the upper hex flats by
    # 0.25mm and retain3mm radial stock, with the mouth open below the axis.
    r=16.5+.25/math.sin(math.pi/3)
    drop=r*math.sin(math.pi/3)
    reach=r+3.
    crown=z+drop+3.
    x0=x-width/2;x1=x+width/2
    seat=box(x0,x1,y-reach,y+reach,z,crown)
    pocket=(cq.Workplane('YZ').polyline([
        (y-r,z),(y-r/2,z+drop),(y+r/2,z+drop),
        (y+r,z),(y+r,z-10),(y-r,z-10)]).close().extrude(width)
        .val().translate((x0,0,0)))
    seat=seat.cut(pocket)
    # Rear-rooted end columns leave the shortened funnel's sloping underside
    # free. The shared tie tunnel has3mm end webs and a3mm roof cover.
    back_y=y+r-.01
    seat=seat.fuse(box(x0,x1,back_y,y+reach,z,root+.01))
    tunnel=box(x-5.826/2,x+5.826/2,back_y-.1,y+reach+.1,crown+3,root-3)
    return seat.cut(tunnel).clean(),tunnel

def meter_seat(x,y,z,width=6.9,root=351.):
    # The scanned collar is7.2mm long, drafted8.95..9.15R. A9.4R slip bore
    # leaves3mm radial walls and1.7mm axial webs beside a3.5mm tie passage.
    r=9.4;reach=r+3.;y0=y-width/2;y1=y+width/2
    crown=z+r+3.
    rib=box(x-reach,x+reach,y0,y1,z,crown)
    for a,b in [(y0,y-1.75),(y+1.75,y1)]:
        rib=rib.fuse(box(x-reach,x+reach,a,b,crown,root+.01))
    bore=cq.Solid.makeCylinder(r,width,cq.Vector(x,y0,z),cq.Vector(0,1,0))
    bore=bore.fuse(box(x-r,x+r,y0,y1,z-r-reach,z))
    rib=rib.cut(bore).clean()
    # Trim the unused rectangular crown corners. The diagonal is outside the
    # R12.4 radial stock, and permits the retained high water tube to pass the
    # east tie crown with an actual dressed tie instead of an empty reserve.
    for sign in [-1,1]:
        corner=(cq.Workplane('XZ').polyline([
            (x+sign*reach,z+reach),
            (x+sign*(reach-2.9),z+reach),
            (x+sign*reach,z+reach-2.9)]).close().extrude(width)
            .val().translate((0,y1,0)))
        rib=rib.cut(corner)
    # The clearance operation is reapplied after every parent fusion. Preserve
    # the actual bearing webs, including their positive roof-root volume.
    pocket=box(x-reach-2,x+reach+2,y0-.15,y1+.15,343,root).cut(rib)
    return rib,pocket

def loop_band(plane,points,width,shift):
    outside=cq.Workplane(plane).polyline(points).close().wire().offset2D(.5).extrude(width).val()
    inside=cq.Workplane(plane).polyline(points).close().wire().offset2D(-.5).extrude(width).val()
    return outside.cut(inside).translate(shift).clean()

def asse_tie(x,y,z):
    r=16.5+.25/math.sin(math.pi/3);drop=r*math.sin(math.pi/3)
    reach=r+3.6;top=z+drop+6.6;bottom=z-drop-.5
    loop=loop_band('YZ',[(y-reach,z-.5),(y-reach,top),(y+reach,top),
                        (y+reach,z-.5),(y+8.7,bottom),(y-8.7,bottom)],4.826,(x-2.413,0,0))
    head=box(x-6,x+6,y+20.5,y+30.5,z+13.6,z+19.6)
    return loop.fuse(head).clean()

def asse_removable(xs,y,z):
    """Fore-inserted keyed carrier on two independent roof clamp stations."""
    top= z+21.639419162443238-2.
    beam_bottom=top-3.
    carrier=None
    for x in xs:
        seat,_=asse_seat(x,y,z,11.826)
        seat=seat.intersect(box(x-8,x+8,y-25,y+25,z,z+18.45)).clean()
        riser=box(x-5.913,x+5.913,y-.8,y+2.2,z+15.3,top)
        seat=seat.fuse(riser)
        carrier=seat if carrier is None else carrier.fuse(seat)
    carrier=carrier.fuse(box(-52,22,y-.8,y+2.2,beam_bottom,top)).clean()
    stubs={};clamps={};screws={};pilots={};stations=[]
    for i,x in enumerate([-48.,18.],1):
        mouth_y=y+3.35;back=mouth_y+8.7;axis_z=z+28.55
        stub=box(x-4,x+4,mouth_y,back,axis_z-4,343.01)
        pilot=cq.Solid.makeCylinder(2,5.7,cq.Vector(x,mouth_y,axis_z),cq.Vector(0,1,0))
        stubs[f'asse-roof-seat-{i}']=stub.cut(pilot).clean()
        # The lower shelf supports the carrier's3mm transverse beam. A
        # separate upper arm lands on the roof block; its7.3mm screw stack
        # leaves4.7mm of actual short-insert engagement.
        fore=y-3.95
        plate=box(x-4,x+4,fore,fore+3,beam_bottom-3,axis_z+4)
        plate=plate.fuse(box(x-4,x+4,fore+3,mouth_y,axis_z-3,axis_z+4))
        plate=plate.fuse(box(x-4,x+4,fore+3,y+2.2,beam_bottom-3,beam_bottom))
        hole=cq.Solid.makeCylinder(1.65,mouth_y-fore+.04,cq.Vector(x,fore-.02,axis_z),cq.Vector(0,1,0))
        clamps[f'asse-carrier-clamp-{i}']=plate.cut(hole).clean()
        screw=cq.Solid.makeCylinder(1.5,12,cq.Vector(x,fore,axis_z),cq.Vector(0,1,0))
        head=cq.Solid.makeCylinder(2.75,3,cq.Vector(x,fore-3,axis_z),cq.Vector(0,1,0))
        rr=2.5/math.sqrt(3)
        points=[cq.Vector(x+rr*math.cos(k*math.pi/3),fore-3,axis_z+rr*math.sin(k*math.pi/3))for k in range(6)]
        socket=cq.Solid.extrudeLinear(cq.Wire.makePolygon(points+[points[0]]),[],cq.Vector(0,1.8,0))
        screws[f'asse-carrier-screw-{i}']=screw.fuse(head).cut(socket)
        pilots[f'asse-carrier-pilot-{i}']=pilot
        stations.append({'index':i,'owner':'asse-removable-carrier','mouth':[x,mouth_y,axis_z],
                         'axis':[0,1,0],'pilot_depth':5.7,'insert_length':4.,'screw_length':12.,
                         'head_bearing_y_mm':fore,'stack_mm':mouth_y-fore,
                         'actual_engagement':12-(mouth_y-fore),'tip_reserve':5.7-(12-(mouth_y-fore)),
                         'root_cover':3.,'carrier_beam_stock_mm':3.,'clamp_bearing_stock_mm':3.})
    return carrier,stubs,clamps,screws,pilots,stations

def asse_factory_cutters(carrier,lift,travel):
    """Conservative native-face prisms over the complete fore carrier travel."""
    tools={}
    raised=carrier.translate((0,0,lift))
    for i,face in enumerate(raised.Faces()):
        b=bounds(face)
        if b[5]+1<=343.:continue
        top=b[5]+1.
        if top>352.:raise ValueError('ASSE carrier motion would breach3mm exterior stock')
        tools[f'asse-carrier-roof-channel-{i}']=box(b[0]-1,b[3]+1,b[1]-travel-1,b[4]+1,343.,top)
    return tools

def meter_tie(x,y,z):
    upper=13.1;lower=9.9;chamfer=3.1
    points=[(x+upper,z-.5),(x+upper,z+upper-chamfer),
            (x+upper-chamfer,z+upper),(x-upper+chamfer,z+upper),
            (x-upper,z+upper-chamfer),(x-upper,z-.5)]
    points += [(x+lower*math.cos(t),z-.5+lower*math.sin(t))
               for t in [math.pi+i*math.pi/24 for i in range(25)]]
    # XZ extrusion points toward-Y; keep the band centred on its collar.
    loop=loop_band('XZ',points,2.5,(0,y+1.25,0))
    head=box(x+11,x+19,y-4,y+4,z-5.1,z-.1)
    return loop.fuse(head).clean()

def main():
    sources=proof_sources.snapshot(__file__,baseline.__file__,received_native.__file__)
    p=argparse.ArgumentParser();p.add_argument('--probe-asse-y',type=float)
    p.add_argument('--probe-asse-dx',type=float,default=0)
    p.add_argument('--frame',type=float)
    p.add_argument('--check',action='store_true',help='Verify the analytic recipe against held native files and refresh evidence without exporting.')
    a=p.parse_args()
    if a.check and (a.probe_asse_y is not None or a.probe_asse_dx or a.frame is not None):
        raise ValueError('Received check requires the selected fixed recipe')
    received=received_native.ReceivedNative(ROOT,json.loads((HERE/'fluid-candidate.json').read_text()))if a.check else None
    routing=json.loads((STUDY/'routing/candidate.json').read_text())
    load=lambda r:cq.Shape.importBrep(str(ROOT/r['brep']))
    axis=routing['ports']['asse1022-assembly']['tube-in']['pos']
    vent=routing['ports']['asse1022-assembly']['vent-tip']['pos']
    y=axis[1] if a.probe_asse_y is None else a.probe_asse_y
    z=axis[2]
    xs=[vent[0]+a.probe_asse_dx-(19+6.265)/2,vent[0]+a.probe_asse_dx+(19+6.265)/2]
    shapes={};cutters={};owners={};checks=[]
    carrier,stubs,clamps,screws,asse_pilots,asse_stations=asse_removable(xs,y,z)
    # The measured WAGO-G2 groove enters normally along-Y. Its full34mm
    # factory wire approach grazes the west carrier station's upper east
    # corner. A1mm-air cylinder retains the completeR3.6 pilot stock and
    # three-mm blind cap; the separate clamp receives the same passage.
    power=json.loads((STUDY/'wiring/power-candidate.json').read_text())
    g2=power['power_routes']['PE-feed']['from']
    if g2['label']!='wago-g:2':raise ValueError('Expected measured WAGO-G2 feed entry')
    entry=cq.Vector(*g2['point']);normal=cq.Vector(*g2['axis'])
    g2_tool=cq.Solid.makeCylinder(2.6,40,entry+normal*40,-normal)
    pilot_guard=cq.Solid.makeCylinder(3.6,8.7,cq.Vector(-48,y+3.35,z+28.55),cq.Vector(0,1,0))
    checks.append({'check':'G2 entry retains complete1.6mm pilot surround and3mm blind end',
                   'guard_removed_mm3':common(g2_tool,pilot_guard),
                   'pass':common(g2_tool,pilot_guard)<.0001})
    stubs['asse-roof-seat-1']=stubs['asse-roof-seat-1'].cut(g2_tool)
    clamps['asse-carrier-clamp-1']=clamps['asse-carrier-clamp-1'].cut(g2_tool)
    cutters['asse-g2-wire-entry-channel']=g2_tool
    shapes['asse-removable-carrier']=carrier
    shapes.update(stubs);shapes.update(clamps);shapes.update(screws)
    for n in shapes:owners[n]='asse1022-assembly'
    lift=14.289419162443238+1.
    cutters.update(asse_factory_cutters(carrier,lift,y-170.))
    # The west tube connects while the held valve is15mm east, before the
    # final lowering/west shift. Its free end turns down then fore atR14.
    # These two conservative flank channels cover that handling family,
    # preserve4mm outer stock and stay below the captured frame rails for
    # everyY at or forward of the selected295.6915mm frame rear.
    cutters['asse-factory-supply-wall-fore']=box(-103.5,-98.49,199.999,300.,276.275,303.79)
    cutters['asse-factory-supply-wall-aft-turn']=box(-103.5,-98.49,300.,314.475,276.275,321.225)
    for i,x in enumerate(xs,1):
        shapes[f'asse-retention-tie-{i}']=asse_tie(x,y,z)
        owners[f'asse-retention-tie-{i}']='asse1022-assembly'
    meter=routing['ports']['digiten-flow'];mi=meter['inlet']['pos'];mo=meter['outlet']['pos']
    for i,cy in enumerate([mi[1]+7.3,mo[1]-7.3],1):
        shapes[f'meter-roof-seat-{i}'],cutters[f'meter-roof-pocket-{i}']=meter_seat(mi[0],cy,mi[2])
        owners[f'meter-roof-seat-{i}']='digiten-flow'
        shapes[f'meter-retention-tie-{i}']=meter_tie(mi[0],cy,mi[2])
        owners[f'meter-retention-tie-{i}']='digiten-flow'
        cutters[f'meter-tie-head-pocket-{i}']=box(mi[0]+10,mi[0]+20,cy-5,cy+5,mi[2]-6.1,mi[2]+.9)
    if received:
        shapes={n:received.shape(n,s)for n,s in shapes.items()}
        cutters={n:received.shape(n,s)for n,s in cutters.items()}
        asse_pilots={n:received.shape(n,s)for n,s in asse_pilots.items()}
    records={};models={};replaced=set();manifest_inputs={};manifest_content_inputs={};native_inputs={}
    for folder,file in [('funnel','candidate.json'),('pump','candidate.json'),('pump','fluid24-candidate.json'),
                        ('routing','candidate.json'),('structure','candidate.json'),('mounts','candidate.json'),
                        ('mounts','body-candidate.json'),('routing','co2-candidate.json'),('wiring','candidate.json'),
                        ('wiring','control-reserves.json'),('wiring','control-fanouts-check.json')]:
        path=STUDY/folder/file
        if not path.exists():continue
        manifest_inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        m=json.loads(path.read_text());manifest_content_inputs[str(path.relative_to(ROOT))]=content_sha256(m)
        replaced.update(m.get('replacement_names',[]));records.update(m.get('parts',{}))
    for name,r in records.items():
        if name.startswith(('asse-roof-seat','asse-removable-carrier','asse-carrier-','meter-roof-seat','asse-retention-tie','meter-retention-tie')):continue
        if r.get('role') in ['walls','context']:continue
        native_inputs[name]={'brep':r['brep'],'sha256':hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()}
        models[name]=load(r)
    if a.frame is not None:
        fm=json.loads((STUDY/f'funnel/candidate-aft-{a.frame:g}.json').read_text())
        for name,r in fm['parts'].items():models[name]=load(r)
    if a.probe_asse_y is not None:
        models['asse1022-assembly']=models['asse1022-assembly'].translate((a.probe_asse_dx,y-axis[1],0))
    for name,shape in shapes.items():
        hits=[]
        for other,body in models.items():
            if a.probe_asse_y is not None and other.startswith(('tube-water-1','tube-water-2','tube-water-3')):continue
            vol=common(shape,body)
            if vol>.001:hits.append({'part':other,'common_mm3':vol})
        checks.append({'part':name,'valid_single_solid':shape.isValid() and len(shape.Solids())==1,
                       'owner_gap_mm':shape.distance(models[owners[name]]),'interferences':hits,
                       'pass':shape.isValid() and len(shape.Solids())==1 and not hits})
    for first,second in itertools.combinations(shapes,2):
        volume=common(shapes[first],shapes[second])
        checks.append({'parts':[first,second],'common_mm3':volume,'pass':volume<.001})
    OUT.mkdir(parents=True,exist_ok=True)
    def record(name,s,detail):
        if received:return received.record(name,s)
        f=OUT/(name+'.brep');s.exportBrep(str(f))
        return {'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
                'bounds':bounds(s),'role':'structure','detail':detail}
    parts={}
    for n,s in shapes.items():
        if 'tie' in n:
            detail='Nominal closed nylon tie band:4.826×1mm ASSE or2.5×1mm meter section; conservative12×10×6mm ASSE-rear or8×8×5mm meter-side locking-head/tail working volume. Purchased head shape is unmeasured. ASSE ties close after carrier fastening; meter ties close before roof sliding.'
        elif n=='asse-removable-carrier':
            detail='Separate keyed upper brass carrier with two11.826mm-wide seats and a3mm transverse beam. Enter fore at15.289419mm lift, lower over the separately held valve, then support its beam on two bolted3mm shelves. Wide ties retain the barrel.'
        elif n.startswith('asse-roof-seat'):
            detail='High roof block with8mm transverse section, short4mm insert,5.7mm pilot and3mm blind end. Retains the removable carrier clamp; the ASSE and carrier are absent during main enclosure sliding.'
        elif n.startswith('asse-carrier-clamp'):
            detail='Separate3mm bearing shelf and fore plate; upper arm lands on the high roof block. M3×12 screw clamps a7.3mm stack with4.7mm short-insert engagement and1mm blind tip reserve.'
        elif n.startswith('asse-carrier-screw'):
            detail='M3×12 socket screw with2.5AF socket,7.3mm stack and4.7mm actual insert engagement.'
        else:
            detail='Roof-rooted measured fixed-collar half-round seat;3mm radial walls,1.7mm axial webs,3.5mm tie passage,0.15mm axial ends;6in narrow tie retains the meter.'
        parts[n]=record(n,s,detail)
    # These small solid witnesses identify positive stock at the actual roof
    # bearing, independently of a contact graph or a bounding-box overlap.
    # The final joined-print checker reapplies every clearance and pilot tool
    # before requiring these same volumes to remain completely occupied.
    root_coupons={}
    for i,cy in enumerate([mi[1]+7.3,mo[1]-7.3],1):
        host=f'meter-roof-seat-{i}'
        for label,cy0,cy1 in [('fore',cy-3.45,cy-1.75),('aft',cy+1.75,cy+3.45)]:
            name=f'meter-root-coupon-{i}-{label}'
            coupon=box(mi[0]+9.4,mi[0]+12.4,cy0,cy1,350.,351.)
            missing=abs(coupon.cut(shapes[host]).Volume())
            checks.append({'check':name+' positive roof bearing stock',
                           'missing_mm3':missing,'pass':missing<.0001})
            root_coupons[name]=dict(record(name,coupon,'Actual3×1.7×1mm positive roof-bearing stock witness, required after all parent recuts.'),
                                        print_owner='enclosure-back-top',host_part=host,
                                        require_missing_volume_mm3_below=.0001)
    guard=pilot_guard.cut(asse_pilots['asse-carrier-pilot-1'])
    missing=abs(guard.cut(shapes['asse-roof-seat-1']).Volume())
    checks.append({'check':'G2-relieved ASSE station complete pilot annulus and blind cap',
                   'missing_mm3':missing,'pass':missing<.0001})
    root_coupons['asse-g2-pilot-stock']=dict(
        record('asse-g2-pilot-stock',guard,'CompleteØ4 pilot with1.6mm surrounding stock through5.7mm depth and3mm closed blind end.'),
        print_owner='enclosure-back-top',host_part='asse-roof-seat-1',
        require_missing_volume_mm3_below=.0001)
    cutter_records={}
    for n,s in cutters.items():
        factory_wall=n.startswith('asse-factory-supply-wall')
        detail=('Factory west supply-tail channel:1mm pipe air,4mm exterior stock, below the frame receiver forY≤295.6915.' if factory_wall else 'Native carrier-entry roof channel or local meter/tie pocket; at least3mm exterior cover.')
        cutter_records[n]=dict(record(n,s,detail),print_owner='enclosure-back-top')
        if n=='asse-g2-wire-entry-channel':
            cutter_records[n].update(detail='Measured WAGO-G2 normal34mm wire-entry passage,1mm radial air; retains the completeØ4 pilot plus1.6mm surround and3mm blind cover.',
                                     normal_entry_mm=34.,wire_diameter_mm=3.2,
                                     radial_air_mm=1.,minimum_pilot_surround_mm=1.6,
                                     blind_end_cover_mm=3.)
        if n.startswith('asse-carrier-roof-channel'):
            cutter_records[n].update(factory_upper_bay_channel=True,
                                     minimum_exterior_stock_mm=355.-bounds(s)[5],
                                     preserved_frame_receiver_z_min_mm=303.9)
        if factory_wall:
            cutter_records[n].update(factory_upper_bay_channel=True,
                                     minimum_exterior_stock_mm=4.,
                                     preserved_frame_receiver_z_min_mm=303.9,
                                     frame_rear_y_mm=295.69150792328)
    pilot_records={n:dict(record(n,s,'Exact short-insert pilot recut after roof fusion.'),print_owner='enclosure-back-top')for n,s in asse_pilots.items()}
    if received:
        checks.extend(received.checks)
        native_inputs.update(received.inputs)
    result={'parts':parts,'clearance_cutters':cutter_records,'pilot_cutters':pilot_records,
            'joined_root_coupons':root_coupons,
            'shell_fuse_part_names':[n for n in parts if 'seat' in n],
            'factory_carried_part_names':['digiten-flow']+[n for n in parts if n.startswith('meter-retention-tie')],
            'factory_deferred_part_names':['asse1022-assembly','asse-removable-carrier']+[n for n in parts if n.startswith(('asse-carrier-','asse-retention-tie-'))],
            'standalone_print_parts':{'asse-removable-carrier':{'source_part':'asse-removable-carrier','rotation_x_deg':180,'fuse_part_names':[]},**{n:{'source_part':n,'rotation_x_deg':90,'fuse_part_names':[]}for n in clamps}},
            'mounts':asse_stations,
            'carrier_factory':{'body_entry_axis_y_mm':[170,270],'body_entry_offset_x_mm':15.,'entry_roll_degrees':-90,'entry_axis_z_mm':324.,'unroll_axis_y_mm':270.,'unroll_axis_z_mm':324.,'aft_advance_axis_z_mm':319.15,'lower_stage_axis_y_mm':304.5,'lower_stage_axis_z_mm':317.05,'supply_makeup_body_offset_x_mm':15.,'supply_normal_approach_mm':10.,'final_axis_y_mm':y,'final_axis_z_mm':z,'carrier_entry_axis_y_mm':[170,y],'carrier_entry_lift_z_mm':lift,'carrier_roof_channel':{'method':'Conservative swept native-face bounding prisms over the full carrier entry stroke,1mm air.','maximum_cut_z_mm':max(bounds(s)[5]for n,s in cutters.items()if n.startswith('asse-carrier-')),'minimum_exterior_stock_mm':355-max(bounds(s)[5]for n,s in cutters.items()if n.startswith('asse-carrier-'))},'fixture':'Hold the bare valve15mm east during its rolled fore entry and staged advance/lowering. Connect the west tube atY310.3/Z317.05, then lower and shift west with its opposite end free. The independent fore support prongs hold its frozen seated datum while the carrier and clamps are fitted. Purchased VK is installed afterward; its fused lid cradle remains present.','report':'future/pump-first-layout-study/structure/asse-factory-check.json'},
            'native_inputs':native_inputs,'manifest_sha256':manifest_inputs,
            'manifest_content_sha256':manifest_content_inputs,
            'source_inputs':sources,
            'intended_contacts':[], 'checks':checks,'pass':all(c['pass'] for c in checks),
            'asse_axis':[axis[0],y,z],'meter_fixed_collar_bands':[[mi[1]+3.7,mi[1]+10.9],[mo[1]-10.9,mo[1]-3.7]],
            'qualification_limits':['Nominal mounts require native joined-stock and slicing checks. Nylon retention, creep, vibration and factory tie dressing require physical qualification.','The two short-insert clamp stations and3mm shelves need physical load/creep qualification; native pilot stock and a joined print do not establish strength.','Rigid factory motion, workholding and the free-ended west tube handling family have separate evidence in asse-factory-check.json; actual collet make-up, tube memory and fixture stiffness remain physical qualifications.']}
    result['source_drift']=[n for n,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]+proof_sources.changed(sources)
    result['manifest_drift']=[n for n,h in manifest_content_inputs.items()if manifest_content_sha256(ROOT/n)!=h]
    result['geometry_pass']=result['pass']
    result['pass']=result['pass']and not result['source_drift']and not result['manifest_drift']
    if received:
        before=content_sha256(received.manifest);after=content_sha256(result)
        unchanged=before==after
        result['checks'].append({'check':'received refresh preserves complete semantic manifest content',
                                'before_content_sha256':before,'after_content_sha256':after,'pass':unchanged})
        if not unchanged:raise ValueError('Received fluid-host refresh changes substantive manifest fields')
    file=HERE/('fluid-probe.json' if a.probe_asse_y is not None or a.frame is not None else 'fluid-candidate.json')
    file.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass':result['pass'],'checks':checks},indent=2),flush=True)

if __name__=='__main__':main()
