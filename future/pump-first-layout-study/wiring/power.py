"""Exact nominal bay routes for AC, 12V and protective-earth conductors.

IRM-90 is Class II and has no earth terminal. Protective earth bonds the
appliance metalwork. The study does not invent the unlocated purchased motor,
compressor or lower metalwork terminals: their explicit reserved boundaries
are separate from the measured bay fittings.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import cadquery as cq
import numpy as np

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/wiring/power'
sys.path[:0]=[str(HERE),str(STUDY)]
import audit
from native_harness import sweep,bounds,broad
from power_harness import PowerGuide as Guide
from ground_interfaces import CIRCUIT_RING_INDICES
from evidence_binding import content_sha256
from structure.received_native import ReceivedNative

def endpoint_equal(a,b,tolerance=1e-6):
    """Compare endpoint geometry at the route's micrometre numeric tolerance."""
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tolerance
    if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        return len(a)==len(b) and all(endpoint_equal(x,y,tolerance)for x,y in zip(a,b))
    if isinstance(a,dict) and isinstance(b,dict):
        return a.keys()==b.keys() and all(endpoint_equal(a[k],b[k],tolerance)for k in a)
    return a==b

COMPRESSOR_EXIT=(96.5,447.)
LOWER_EARTH_EXITS={'carbonator':(95.,440.),'under-counter':(99.,436.)}

def write_lower_exits(received=None):
    """Publish the complete three occupied bay-boundary lead exteriors."""
    rows={'compressor-jacket-reserve':(*COMPRESSOR_EXIT,9.,'Conservative Ø9 SJOOW jacket exterior; factory compressor termination remains unlocated.')}
    for label,xy in LOWER_EARTH_EXITS.items():
        rows['lower-'+label+'-earth-reserve']=(*xy,3.2,label+' protective-earth bay exit; lower metalwork termination remains unlocated.')
    result={'parts':{},'clearance_cutters':{},'scope':'Full lead exteriors from Z253.4 to293 outside the foam cap. Installed occupancy is tested with the complete power module; no lower termination or cold-core hole is invented.'}
    for name,(x,y,d,detail) in rows.items():
        shape=cq.Solid.makeCylinder(d/2,39.6,cq.Vector(x,y,253.4),cq.Vector(0,0,1))
        f=OUT/(name+'.brep')
        if received:
            result['parts'][name]=received.record(name,shape)
        else:
            shape.exportBrep(str(f))
            result['parts'][name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
                'bounds':bounds(shape),'role':'wiring','color_role':'earth' if d==3.2 else 'return','detail':detail}
        cutter=cq.Solid.makeCylinder(d/2+1,39.6,cq.Vector(x,y,253.4),cq.Vector(0,0,1))
        f=OUT/(name+'-clearance.brep')
        if received:
            result['clearance_cutters'][name]=received.record(name+'-clearance',cutter)
        else:
            cutter.exportBrep(str(f))
            result['clearance_cutters'][name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
    if received:
        if content_sha256(result)!=content_sha256(received.manifest):
            raise ValueError('Received lower-lead refresh changed complete held manifest content')
    else:
        (HERE/'lower-lead-exits.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def port(owner,point,axis,label,basis='Nominal terminal reservation'):
    return {'owner':owner,'point':list(point),'axis':list(axis),'label':label,'basis':basis}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',default=None)
    parser.add_argument('--resume-failed',action='store_true')
    parser.add_argument('--reroute',default='',help='Comma-separated selected routes to replace while resuming the other native paths')
    parser.add_argument('--exits-only',action='store_true')
    parser.add_argument('--search-states',type=int,default=600000)
    parser.add_argument('--terminal-docks',choices=['normal','prepared'],default='normal')
    parser.add_argument('--check',action='store_true',
                        help='Check all19 held prepared-dock paths; no native export or route search.')
    args=parser.parse_args()
    if args.check:
        if args.only or args.reroute or args.exits_only:
            parser.error('--check checks the complete held19 routes and lower exteriors')
        args.resume_failed=True;args.terminal_docks='prepared'
    if args.only and args.resume_failed:parser.error('--only and --resume-failed are mutually exclusive')
    if args.reroute and not args.resume_failed:parser.error('--reroute requires --resume-failed')
    forced_reroutes={name.strip()for name in args.reroute.split(',')if name.strip()}
    OUT.mkdir(parents=True,exist_ok=True)
    source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [Path(__file__),HERE/'native_harness.py',HERE/'power_harness.py',HERE/'recover_power.py',HERE/'adopt_power_recipes.py',HERE/'circular_clearance.py',
                             HERE/'ground_interfaces.py',STUDY/'routing/fluid_members.py',STUDY/'audit.py',STUDY/'evidence_binding.py',
                             STUDY/'structure/received_native.py']}
    lower_received=None
    held_lower_raw=None
    if args.check:
        held_lower_raw=(HERE/'lower-lead-exits.json').read_bytes()
        held_lower=json.loads(held_lower_raw)
        # Part and cutter names share the public key in this manifest. Give
        # the checker an internal cutter label while keeping the held record.
        recipe={**held_lower,'clearance_cutters':{
            name+'-clearance':record for name,record in held_lower['clearance_cutters'].items()}}
        lower_received=ReceivedNative(ROOT,recipe)
        lower_received.manifest=held_lower
    exits=write_lower_exits(lower_received)
    if args.exits_only:
        print(json.dumps({'published_lower_exteriors':len(exits['parts'])}),flush=True);return
    manifest_inputs={};manifest_contents={}
    if held_lower_raw is not None:
        lower_name=str((HERE/'lower-lead-exits.json').relative_to(ROOT))
        manifest_inputs[lower_name]=hashlib.sha256(held_lower_raw).hexdigest()
        manifest_contents[lower_name]=content_sha256(held_lower)
    def read_manifest(path):
        raw=path.read_bytes()
        manifest_inputs[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
        parsed=json.loads(raw);manifest_contents[str(path.relative_to(ROOT))]=content_sha256(parsed)
        return parsed
    meta=read_manifest(STUDY/'mounts/junction-port-approaches.json')['junctions']
    ports={};jobs=[]
    def wago(name,i):
        row=next(p for p in meta[name] if p['port_index']==i)
        key=name+':'+str(i)
        ports[key]=port(name,row['mouth'],row['outward_axis'],key,'Nominal source groove pitch and exact retained purchased envelope')
        return key
    def add(key,p):ports[key]=p;return key
    def job(name,a,b,color,topology):jobs.append((name,a,b,color,topology))
    structure=read_manifest(STUDY/'structure/candidate.json')
    psu=cq.Shape.importBrep(str(ROOT/structure['parts']['psu']['brep']))
    terminal_faces=[f for f in psu.Faces() if f.geomType()=='PLANE' and f.normalAt().z>.99
                    and abs(f.Center().z-(psu.BoundingBox().zmin+13.7))<.01]
    ac_center=next(f.Center() for f in terminal_faces if abs(f.Area()-128)<.01)
    dc_center=next(f.Center() for f in terminal_faces if abs(f.Area()-200)<.01)
    # Soldered tabs have a downward wire approach at their fore ends. Molded
    # inlet L/N markings still govern assembly; the two power blade identities
    # are nominal in this reference, while the offset centre blade is PE.
    inlet={
      'H':add('C14-H',port('c14-inlet',(-64,436.21,338.86058083755),(0,0,-1),'C14 nominal line solder tab')),
      'N':add('C14-N',port('c14-inlet',(-77.8,436.21,338.66058083755),(0,0,-1),'C14 nominal neutral solder tab')),
      'G':add('C14-PE',port('c14-inlet',(-70.75,436.21,333.61058083755),(0,0,-1),'C14 centre earth solder tab'))}
    # The representative reference blocks expose exact top faces. Their clamp
    # make-up is unmeasured; the 7.5/5mm pole pitch is a terminal fit reserve.
    ac={
      'H':add('PSU-L',port('psu',(ac_center.x,ac_center.y-3.75,ac_center.z),(0,0,1),'IRM AC line')),
      'N':add('PSU-N',port('psu',(ac_center.x,ac_center.y+3.75,ac_center.z),(0,0,1),'IRM AC neutral'))}
    dc={
      'V12':add('PSU-V12',port('psu',(dc_center.x,dc_center.y+7.5,dc_center.z),(0,0,1),'IRM DC +V')),
      'GND':add('PSU-GND',port('psu',(dc_center.x,dc_center.y-2.5,dc_center.z),(0,0,1),'IRM DC −V'))}
    floor=read_manifest(STUDY/'mounts/floor-candidate.json')['endpoints']
    c1=floor['relay-1']['contacts']['point'];c2=floor['relay-2']['contacts']['point']
    r1com=add('R1-COM',port('relay-1',c1,(0,0,1),'Relay1 contact COM'))
    r1no=add('R1-NO',port('relay-1',(c1[0],c1[1]+5,c1[2]),(0,0,1),'Relay1 contact NO'))
    r2com=add('R2-COM',port('relay-2',c2,(0,0,1),'Relay2 contact COM'))
    r2no=add('R2-NO',port('relay-2',(c2[0],c2[1]+5,c2[2]),(0,0,1),'Relay2 contact NO'))
    pump=read_manifest(STUDY/'pump/candidate.json')
    pump_origin=pump['poses']['g-ganen-pump']['origin_mm']
    motor={}
    for label,dy in [('+',-4),('−',6)]:
        point=[pump_origin[0]+85,pump_origin[1]+dy,pump_origin[2]+21]
        motor[label]=add('MOTOR-'+label,port('g-ganen-pump',point,(0,0,1),'Motor pigtail '+label,
          'Nominal upward approach at the upper boundary of the observed motor lead region; terminal polarity and rigid strain relief are unlocated'))
    controller=cq.Shape.importBrep(str(ROOT/structure['parts']['pcba']['brep']))
    j10_z=337.5000002+controller.BoundingBox().zmin-329.9
    pcb_dx=controller.BoundingBox().xmin+20.
    j10={
      'V12':add('J10-V12',port('pcba',(-2.4+pcb_dx,412.76606415,j10_z),(0,0,-1),'J10 east V12 clamp')),
      'GND':add('J10-GND',port('pcba',(-7.4+pcb_dx,412.76606415,j10_z),(0,0,-1),'J10 west GND clamp'))}
    ring={}
    ground_mount=next(m for m in structure['mounts'] if m['owner']=='ground-stack')
    ground_datum=ground_mount['mouth']
    for label,i in CIRCUIT_RING_INDICES.items():
        a=math.radians(60*i-ground_mount.get('clock_degrees',0));axis=(math.cos(a),-math.sin(a),0)
        point=(ground_datum[0]+9*axis[0],ground_datum[1]+9*axis[1],ground_datum[2]-2.1-i*.8)
        ring[label]=add('PE-'+label,port('ground-stack',point,axis,'Earth fan '+label,
          'Representative insulated ring barrel exterior; ring3 is spare and no ring carries a PSU bond'))
        ports[ring[label]]['ring_index']=i
    breakout={}
    for label,offset in [('H',(-1.95,-1.125833)),('N',(1.95,-1.125833)),('G',(0,2.251666))]:
        xy=(COMPRESSOR_EXIT[0]+offset[0],COMPRESSOR_EXIT[1]+offset[1])
        breakout[label]=add('COMP-'+label,port('compressor-jacket-reserve',(*xy,293),(0,0,1),'Compressor '+label+' breakout',
          'Conservative 9mm SJOOW jacket bay exit; factory-external compressor connector is unlocated in retained source'))
    lower={}
    for label,xy in LOWER_EARTH_EXITS.items():
        lower[label]=add('LOWER-'+label,port('lower-'+label+'-earth-reserve',(*xy,293),(0,0,1),'Lower '+label+' bond boundary',
          'Metalwork termination below the scoped bay is unlocated; no cold-core hole is invented'))
    for net in ['H','N','G']:
        junction={'H':'wago-h','N':'wago-n','G':'wago-g'}[net]
        job('AC1-'+net,inlet[net],wago(junction,1),{'H':'line','N':'neutral','G':'earth'}[net],'C14 to AC distribution')
    for net in ['H','N']:
        job('AC2-'+net,wago('wago-h' if net=='H' else 'wago-n',2),ac[net],'line' if net=='H' else 'neutral','AC distribution to ClassII PSU')
    job('AC3-H',wago('wago-h',3),r1com,'line','Unswitched line to relay1 COM')
    job('AC4-H',r1no,breakout['H'],'switched-line','Relay1 NO to compressor SJOOW hot')
    job('AC5-N',wago('wago-n',3),breakout['N'],'neutral','AC neutral to compressor SJOOW')
    job('PE-feed',wago('wago-g',2),ring['feed'],'earth','AC earth distribution to bonded ring fan')
    job('AC6-G',ring['compressor'],breakout['G'],'earth','Ring fan to compressor SJOOW earth')
    for net in ['V12','GND']:
        name='wago-v12' if net=='V12' else 'wago-gnd'
        job('DC1-'+net,dc[net],wago(name,1),'positive' if net=='V12' else 'return','PSU DC output to distribution')
    job('DC2-V12',wago('wago-v12',2),r2com,'positive','12V distribution to relay2 COM')
    job('DC3-V12',r2no,motor['+'],'switched-positive','Relay2 NO to motor pigtail reserve')
    job('DC3-GND',wago('wago-gnd',2),motor['−'],'return','DC return to motor pigtail reserve')
    for net in ['V12','GND']:
        job('DC4-'+net,wago('wago-v12' if net=='V12' else 'wago-gnd',3),j10[net],
          'positive' if net=='V12' else 'return','12V distribution to J10')
    for label in ['carbonator','under-counter']:
        job('PE-'+label,ring[label],lower[label],'earth','Ring fan to lower metalwork boundary reserve')
    # Eight occupied fore leads leave the main row in paired west/east lanes.
    # Complete lead paths preserve each later entry, rather than reserving only
    # an isolated local quarter bend at the connector.
    layout={('wago-h',1):('direct',-1),('wago-h',2):('low',-1),('wago-h',3):('low',1),
            ('wago-n',1):('upper-low',-1),('wago-n',2):('upper-low',1),('wago-n',3):('upper-high',1),
            ('wago-g',1):('deep',1),('wago-g',2):('direct',1)}
    for (owner,i),(kind,sign) in (layout.items() if args.terminal_docks=='prepared' else []):
        key=owner+':'+str(i)
        if key not in ports:continue
        p=ports[key]['point'];x,y,z=p;exit_x=-101.9 if sign<0 else -25.9
        if kind=='direct' and sign<0:
            lead=[p,[x,329.15,z],[x-4.8,329.15,335.15],[x-8.4,332.75,335.15],[x-8.4,340.55,335.15]]
        elif kind=='direct':lead=[p,[x,329.15,z],[x+sign*6.7,329.15,333.25],[exit_x,329.15,333.25]]
        elif kind=='low':
            if sign<0:exit_x=-97.7
            lead=[p,[x,329.15,z],[x,329.15,333.15],[x,336.05,333.15],[exit_x,336.05,333.15]]
        elif kind=='deep':lead=[p,[x,329.15,z],[x,329.15,324.8],[x,354.55,324.8]]
        else:
            height=344.75 if kind=='upper-low' else 348.35;rise=height-z
            lead=[p,[x,328.15,z],[x+sign*rise,328.15,height],[x+sign*(rise+4),332.15,height],[exit_x,332.15,height]]
        ports[key]['lead_paths']=[lead]
    # The relay feed leaves the bank normally into the fore aperture. The
    # complete member guard selects its turn without prescribing a transverse
    # exit that would consume the adjacent occupied AC conductor lanes.
    if args.terminal_docks=='prepared':
        terminal=ports['wago-h:3'];p=np.asarray(terminal['point']);axis=np.asarray(terminal['axis'])
        terminal['lead_paths']=[[p.tolist(),(p+axis*reach).tolist()]for reach in [8.4,12.6,16.8]]
    for key in j10.values():
        x,y,z=ports[key]['point']
        if args.terminal_docks=='prepared' and key!='J10-V12':
            ports[key]['lead_paths']=[[ports[key]['point'],[x,y,326.4],[x,y+12.6,326.4]]]
        else:
            ports[key]['lead_paths']=[[ports[key]['point'],[x,y,z-reach]]for reach in [5.4,6.8,8.4]]
    # The three return conductors leave the recessed bank normally, then rise
    # above its roof platform. Reserve each complete disjoint R3.4 departure
    # before routing the first return; a longer straight fore dock meets stock.
    for index in [1,2,3]:
        key='wago-gnd:'+str(index)
        if key in ports:
            x,y,z=ports[key]['point']
            ports[key]['lead_paths']=[[ports[key]['point'],[x,y-5.4,z],[x,y-5.4,347.9]]]
            if index==1:
                ports[key]['lead_paths']+=[[ports[key]['point'],[x,y-reach,z]]for reach in [5.4,6.8,8.4]]
    # These exact full-diameter departures turn before the nearby controller
    # and CO2 crossover. The lowest ring leaves into the clear aft-west lane.
    for label,normal,dx,dy,end_z in [('feed',5.4,0.,None,326.),('under-counter',4.6,10.,-1.6,326.)]:
        terminal=ports[ring[label]]
        p=np.asarray(terminal['point']);q=p+np.asarray(terminal['axis'])*normal
        end_y=437. if dy is None else float(q[1])+dy
        terminal['lead_paths']=[[p.tolist(),q.tolist(),[float(q[0])+dx,end_y,end_z]]]
    # Preserve the centre earth blade's lower normal escape before dressing
    # either offset power blade. Future-lead reservations protect every exit.
    jobs.sort(key=lambda j:0 if j[0]=='AC1-G' else 1)
    if args.only:jobs=[j for j in jobs if j[0]==args.only]
    used={k for j in jobs for k in j[1:3]}
    guide=Guide([ports[k] for k in sorted(used)])
    guide.used_port_labels=set()
    guide.max_states=args.search_states
    result={'parts':{},'power_routes':{},'replacement_names':[], 'intended_contacts':[], 'clearance_cutters':{},'ports':ports,
      'ground_ring_indices':CIRCUIT_RING_INDICES,
      'basis':{'wire_diameter_mm':3.2,'geometric_radius_mm':3.4,'main_gauge_awg':16,'compressor_awg':18,
               'supply_class':'ClassII; no FG terminal or protective-earth PSU lead'},
      'qualification_limits':['3.2mm main-wire exterior and R3.4 bends are geometric reserves; the purchased wire grade and formed bend are not physically qualified.',
        'PSU pole pitches, C14 L/N blade identities, relay clamps and ring barrels are nominal reference interfaces; verify actual markings and terminations during factory make-up.',
        'Motor lead exit is an observed region, not a fixed terminal or strain-relief datum.',
        'Donor compressor external connector and lower metalwork earth terminations are unlocated in canonical CAD. The explicit bay exits reserve their routes without inventing those interfaces.',
        'Native occupied geometry does not qualify mains insulation, earth continuity, strain relief, cooling, vibration or lifetime.']}
    result['native_inputs']=guide.native_inputs
    result['inputs_sha256']=manifest_inputs
    result['manifest_content_sha256']=manifest_contents
    result['source_inputs']=source_inputs
    # Explicit lead exteriors reach the floor of this study's bay. The lower
    # factory terminations remain unlocated. The jacket stays outside the foam
    # cap and gets an exact wall chase instead of an invented cold-core bore.
    for name,rec in exits['parts'].items():
        shape=cq.Shape.importBrep(str(ROOT/rec['brep']))
        result['parts'][name]=rec;guide.records[name]=rec;guide.models[name]=shape;guide.obstacles[name]=shape
        result['clearance_cutters'][name]=exits['clearance_cutters'][name]
    exit_checks=[]
    exit_obstacle_names=sorted(guide.obstacles)
    for name in exits['parts']:
        shape=guide.models[name];near=[];hits=[]
        for other,obstacle in guide.obstacles.items():
            if name==other or not broad(bounds(shape),bounds(obstacle),1):continue
            gap=shape.distance(obstacle)
            if gap>=1-1e-6:continue
            common=abs(shape.intersect(obstacle,tol=.0001).Volume(tol=1e-9)) if gap<1e-6 else 0.
            row={'other':other,'gap_mm':gap,'common_mm3':common};near.append(row)
            if common>.001:hits.append(row)
        exit_checks.append({'part':name,'pass':not hits,'blockers':hits,'close_pairs':near})
    result['lower_exit_checks']=exit_checks
    if not all(c['pass'] for c in exit_checks):
        if args.check:
            raise ValueError('Held complete lower-bay lead exterior clearance failed')
        result['failures']=[{'route':'lower-lead-exits','reason':'Complete lead exterior overlaps installed hardware','checks':exit_checks}]
        result['pass']=False
        (HERE/'power-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
        raise ValueError('Complete lower-bay lead exterior clearance failed')
    guide.refresh()
    if args.resume_failed:
        previous=json.loads((HERE/'power-candidate.json').read_text())
        if args.check:
            if len(previous.get('power_routes',{}))!=19 or not endpoint_equal(previous['ports'],ports):
                raise ValueError('Complete held19 route inventory or authoritative terminal docks changed')
            held_exits=previous['lower_exit_checks']
            fresh_exits={check['part']:check for check in exit_checks}
            if len(fresh_exits)!=len(exit_checks) or {check['part']for check in held_exits}!=set(fresh_exits):
                raise ValueError('Held lower exterior diagnostic inventory changed')
            for held in held_exits:
                fresh=fresh_exits[held['part']]
                if {k:v for k,v in held.items()if k!='close_pairs'}!={k:v for k,v in fresh.items()if k!='close_pairs'}:
                    raise ValueError('Held lower exterior diagnostic values changed: '+held['part'])
                for pair in held['close_pairs']:
                    matches=[row for row in fresh['close_pairs']if row['other']==pair['other']]
                    if len(matches)!=1 or matches[0]!=pair:
                        raise ValueError('Held lower exterior neighbor values changed: '+held['part']+'/'+pair['other'])
            # Preserve the complete measured snapshot in the substantive
            # manifest. The current complete scan, including every new
            # neighbor, belongs to the source/native-bound evidence below.
            current_lower_exterior_receipt={
                'method':'Complete current received lower-bay lead exterior scan against every declared obstacle; existing held rows and values matched exactly.',
                'native_binding_keys':exit_obstacle_names,
                'checks':exit_checks,'held_diagnostic_values_matched':True,
                'new_neighbor_rows':[{'part':fresh['part'],**pair}
                    for fresh in exit_checks for pair in fresh['close_pairs']
                    if pair['other']not in {row['other']for held in held_exits
                        if held['part']==fresh['part']for row in held['close_pairs']}],
                'pass':all(check['pass']for check in exit_checks),
            }
            result['lower_exit_checks']=held_exits
            # Harmless reimport arithmetic may differ below a micrometre.
            # Keep the complete selected numeric records after proving every
            # recomputed endpoint and approach field equivalent above.
            ports=previous['ports'];result['ports']=ports
        for name,record in previous.get('power_routes',{}).items():
            if name in forced_reroutes:
                print('wire selected for replacement',name,flush=True);continue
            if any(not endpoint_equal(previous['ports'][key].get(field),ports[key].get(field))
                   for key in [record['from_key'],record['to_key']]
                   for field in ['owner','point','axis','lead_paths']):
                print('wire resume needs changed-endpoint reroute',name,flush=True)
                if args.check:raise ValueError('Held route terminal changed: '+name)
                continue
            key='wire-'+name;part=previous['parts'][key];path=ROOT/part['brep']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=part['sha256']:raise ValueError('Changed native wire cannot resume '+name)
            shape=cq.Shape.importBrep(str(path))
            from circular_clearance import paired_members,CircularSelfIntersection
            try:
                authored,_=sweep(record['points_mm'],record['diameter_mm'],record['radius_mm'])
                physical,_,section=paired_members(authored,record['diameter_mm'],gap=0.,fuse_clearance=False)
            except CircularSelfIntersection as error:
                if args.check:raise ValueError('Held route has a complete-section self intersection: '+name)from error
                print('wire resume needs section reroute',name,error.indices,error.volume,flush=True);continue
            from power_harness import terminal_approach_members
            owners,_=terminal_approach_members(physical,ports[record['from_key']],ports[record['to_key']],record['diameter_mm'])
            previous_inputs=previous.get('native_inputs',{})
            changed_obstacles={n:s for n,s in guide.obstacles.items()
                if previous_inputs.get(n)!=guide.native_inputs.get(n)
                or n in previous.get('source_drift',[])}
            hits=[];members=physical.Solids()
            for n,s in changed_obstacles.items():
                if not broad(bounds(physical),bounds(s)):continue
                tested=cq.Compound.makeCompound([member for i,member in enumerate(members)if i not in owners.get(n,set())])
                if audit.common(tested,s)>.001:hits.append(n)
            if hits:
                print('wire resume needs reroute',name,hits,flush=True);continue
            guide.wires[key]=physical
            _,center=sweep(record['points_mm'],record['diameter_mm'],with_centerline=True)
            if not hasattr(guide,'wire_centers'):guide.wire_centers={}
            guide.wire_centers[key]=np.asarray(center['centerline_samples_mm'])
            record['from']=ports[record['from_key']]
            record['to']=ports[record['to_key']]
            result['parts'][key]=part;result['power_routes'][name]=record
            guide.used_port_labels.update(ports[record[end]]['label']for end in ['from_key','to_key'])
            result['clearance_cutters'][key]=previous['clearance_cutters'][key]
            print('wire resume admitted',name,'changed bodies checked',len(changed_obstacles),flush=True)
        result['intended_contacts']=[p for p in previous.get('intended_contacts',[]) if p[0] in result['parts']]
        guide.refresh()
        jobs=[j for j in jobs if j[0] not in result['power_routes']]
        if args.check and jobs:
            raise ValueError('Held19 refresh requires a route change: '+','.join(job[0]for job in jobs))
        if not jobs and len(result['power_routes'])==19 and previous.get('physical_member_gate',{}).get('pass'):
            result['physical_member_gate']=previous['physical_member_gate']
    total=len(result['power_routes'])+len(jobs)
    result['expected_route_count']=total
    failures=[]
    for name,a,b,color,topology in jobs:
        try:
            shape,record=guide.route(ports[a],ports[b],'wire-'+name)
        except ValueError as e:
            failures.append({'route':name,'reason':str(e)});print('WIRE FAILURE',name,str(e),flush=True);continue
        f=OUT/('wire-'+name+'.brep');shape.exportBrep(str(f))
        result['parts']['wire-'+name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
          'bounds':bounds(shape),'role':'wiring','color_role':color,'detail':topology+'; nominal Ø3.2 conductor exterior, exact R3.4 arcs.'}
        record['topology']=topology;record['from_key']=a;record['to_key']=b
        result['power_routes'][name]=record
        for end in [a,b]:
            if ports[end]['owner'] in guide.models:result['intended_contacts'].append(['wire-'+name,ports[end]['owner']])
        # Fuse independently enlarged analytic sections. A whole-path sweep
        # can classify a close return incorrectly and lose a clearance member.
        from circular_clearance import paired_members
        authored,_=sweep(record['points_mm'],record['diameter_mm'],record['radius_mm'])
        _,cutter,clearance_proof=paired_members(authored,record['diameter_mm'],gap=1.,fuse_clearance=True)
        _,enlarged,_=paired_members(authored,record['diameter_mm'],gap=1.,fuse_clearance=False)
        containment=[]
        for index,member in enumerate(enlarged.Solids()):
            missing=abs(member.cut(cutter,tol=.0001).Volume(tol=1e-9))
            if missing>.001:raise ValueError('Complete power clearance loses member '+name)
            containment.append({'member':index,'enlarged_missing_mm3':missing,'pass':True})
        record['clearance_union_proof']={**clearance_proof,'enlarged_member_containment':containment}
        f=OUT/('wire-'+name+'-clearance.brep');cutter.exportBrep(str(f))
        result['clearance_cutters']['wire-'+name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
        guide.refresh()
        result['failures']=failures;result['pass']=not failures and len(result['power_routes'])==total
        (HERE/'power-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    if lower_received:
        result['checks']=lower_received.checks
        result['native_inputs'].update(lower_received.inputs)
    if args.check:
        result.setdefault('checks',[]).append(current_lower_exterior_receipt)
    result['source_drift']=[n for n,r in guide.native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    result['source_drift']+=[n for n,h in source_inputs.items()if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
    result['manifest_drift']=[n for n,h in manifest_contents.items()if content_sha256(json.loads((ROOT/n).read_bytes()))!=h]
    result['failures']=failures;result['pass']=not failures and len(result['power_routes'])==total and not result['source_drift'] and not result['manifest_drift']
    if args.check and content_sha256(result)!=content_sha256(previous):
        raise ValueError('Received19 power refresh changed complete held manifest content')
    (HERE/'power-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'routes':len(result['power_routes']),'pass':result['pass'],'failures':failures},indent=2),flush=True)

if __name__=='__main__':main()
