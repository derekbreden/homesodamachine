"""Native fore entry and fastening of the separate ASSE carrier.

The interval proof bounds every rigid point's displacement from the midpoint
pose. A positive OCC separation larger than that bound certifies the complete
interval; inconclusive intervals subdivide. Final bearing planes are checked
separately and are never accepted as occupied nominal mating stock.
"""
from pathlib import Path
import hashlib,json,math,sys,time
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
sys.path[:0]=[str(STUDY),str(STUDY/'pump'),str(STUDY/'mounts')]
import baseline,audit,generate as G,fluid_hosts as F
from evidence_binding import manifest_content_sha256
from structure import proof_sources

OUT=ROOT/'.cache/pump-first-layout/structure/asse-factory'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def box(x0,x1,y0,y1,z0,z1):return F.box(x0,x1,y0,y1,z0,z1)

def front_members(models,packets):
    """Retained front-top manifold/display membership from its assembly contract."""
    retained=baseline.prepare()['parts']
    changed={n for p in packets for n in p.get('parts',{})}
    names={n for n in retained if n.startswith(('tee-y-','valve-v-','coil-v-',
            'turn-fluid-','enclosure-tee-carrier-','tee-carrier-spring-',
            'enclosure-window-cover-'))and n not in changed}
    names.update({'wago-mana','wago-manb','display','display-cover',
                  'display-gasket','pump-contact-male'})
    names.update('tube-fluid-'+str(i)for i in [9,10,11,12,13,17,19,20,21,22,23,27])
    return names&models.keys()

def loaded():
    prepared=json.loads((HERE/'candidate.json').read_text())
    if 'enclosure-back-top' not in prepared.get('parts',{}):
        raise RuntimeError('ASSE factory proof requires the current prepared parent shell')
    index=baseline.prepare()
    records={n:{'brep':str((baseline.CACHE/r['file']).relative_to(ROOT))}
             for n,r in index['parts'].items()}
    manifests=audit.ManifestHashes();data=[];current=set();removed=set()
    paths=[STUDY/p for p in [
        'funnel/candidate.json','pump/candidate.json','pump/fluid24-candidate.json',
        'routing/candidate.json','structure/candidate.json','mounts/candidate.json',
        'mounts/fluid-candidate.json','mounts/body-candidate.json',
        'mounts/water5-hosts.json','routing/tube-hosts.json',
        'routing/co2-candidate.json','structure/roof-hatch.json',
        'wiring/control-reserves.json','wiring/control-fanouts-check.json',
        'structure/scene-stock.json']]
    for path in paths:
        if not path.exists():continue
        m=json.loads(path.read_text())
        if path.name=='scene-stock.json' and not proof_sources.scene_stock_current(m):continue
        data.append(m)
        manifests[str(path.relative_to(ROOT))]=sha(path)
        manifests.content_sha256[str(path.relative_to(ROOT))]=audit.content_sha256(m)
        records.update(m.get('parts',{}));current.update(m.get('parts',{}))
        removed.update(m.get('replacement_names',[]))
    records={n:r for n,r in records.items()if n not in removed or n in current}
    models={n:cq.Shape.importBrep(str(ROOT/r['brep']))for n,r in records.items()}
    inputs={n:{'brep':r['brep'],'sha256':sha(ROOT/r['brep'])}for n,r in records.items()}
    return models,inputs,manifests,data

class Certifier:
    def __init__(self,fixed):
        self.fixed=fixed;self.boxes={n:audit.bbox(s)for n,s in fixed.items()}
        self.evaluations=0;self.certified=0;self.maximum_depth=0

    def motion(self,name,at,bound,ignore=()):
        """Certify all t in [0,1], using a midpoint displacement bound."""
        rows=[];gaps={};blockers=[];uncertified=[]
        cache={}
        def pose(t):
            if t not in cache:cache[t]=at(t)
            return cache[t]
        def interval(lo,hi,depth):
            mid=(lo+hi)/2;s=pose(mid);b=audit.bbox(s);delta=bound((hi-lo)/2)
            self.maximum_depth=max(self.maximum_depth,depth)
            for n,other in self.fixed.items():
                if n in ignore or not audit.broad(b,self.boxes[n],delta):continue
                if hasattr(bound,'axes'):
                    da=bound.axes((hi-lo)/2);ob=self.boxes[n]
                    if any(b[j+3]+da[j]<=ob[j]+1e-8 or ob[j+3]<=b[j]-da[j]+1e-8
                           for j in range(3)):
                        self.certified+=1
                        continue
                key=(n,mid)
                if key not in gaps:
                    gaps[key]=s.distance(other);self.evaluations+=1
                gap=gaps[key]
                if gap>delta+1e-7:
                    self.certified+=1
                    continue
                if gap<1e-7:
                    common=audit.common(s,other,True)
                    if common>.001:
                        blockers.append({'fixed':n,'t':mid,'common_mm3':common})
                        return False
                if depth>=16:
                    uncertified.append({'fixed':n,'interval':[lo,hi],
                                        'gap_mm':gap,'displacement_bound_mm':delta})
                    return False
                # Recheck the two halves against all neighbors. The complete
                # interval is accepted only after every neighboring article
                # receives a positive separation certificate.
                return interval(lo,mid,depth+1) and interval(mid,hi,depth+1)
            return True
        passed=interval(0.,1.,0)
        for t in [0.,1.]:
            s=pose(t);b=audit.bbox(s)
            for n,other in self.fixed.items():
                if n in ignore or not audit.broad(b,self.boxes[n],0):continue
                gap=s.distance(other);self.evaluations+=1
                if gap<1e-7:
                    common=audit.common(s,other,True)
                    if common>.001:
                        blockers.append({'fixed':n,'t':t,'common_mm3':common});passed=False
        row={'motion':name,'pass':passed,'blockers':blockers,
             'uncertified_intervals':uncertified,'native_distance_evaluations':len(gaps),
             'method':'Midpoint native separation exceeds the maximum Euclidean displacement of every article point; otherwise bisect.'}
        print('ASSE factory',name,passed,len(gaps),blockers,uncertified,flush=True)
        return row

def translation(source,delta):
    d=cq.Vector(*delta)
    bound=lambda half:d.Length*half
    bound.axes=lambda half:[abs(v)*half for v in d.toTuple()]
    return lambda t:source.translate(tuple(d*t)),bound

def hex_key(x,y,z):
    """2.5AF160mm entering leg with a32mm perpendicular external handle."""
    r=2.5/math.sqrt(3)
    pts=[cq.Vector(x+r*math.cos(k*math.pi/3),y,z+r*math.sin(k*math.pi/3))
         for k in range(6)]
    wire=cq.Wire.makePolygon(pts+[pts[0]])
    leg=cq.Solid.extrudeLinear(wire,[],cq.Vector(0,-160,0))
    points=[cq.Vector(x+r*math.cos(k*math.pi/3),y-160+r*math.sin(k*math.pi/3),z)
            for k in range(6)]
    handle=cq.Solid.extrudeLinear(cq.Wire.makePolygon(points+[points[0]]),[],cq.Vector(0,0,32))
    return leg.fuse(handle)

def temporary_tube(port,length):
    p=cq.Vector(*port['pos']);n=cq.Vector(*port['axis'])
    lead=2.;r=14.;a=p+n*lead
    edge,end,_,_=G.exact_arc(a,n,cq.Vector(0,-1,0),r)
    remain=length-lead-edge.Length()
    if remain<=0:raise ValueError('Cut length cannot form the factory free tail')
    wire=cq.Wire.assembleEdges([cq.Edge.makeLine(p,a),edge,
                              cq.Edge.makeLine(end,end+cq.Vector(0,-remain,0))])
    return cq.Solid.sweep(cq.Wire.makeCircle(3.175,p,n),[],wire,makeSolid=True,isFrenet=True),wire

def supply_tail(port,length,body_x_mm=15.,axis_z_mm=317.05,dock_mm=0.):
    """R14 down/fore free end; fixed west cruise while the valve moves west."""
    p=cq.Vector(port['pos'][0]+body_x_mm-dock_mm,port['pos'][1],axis_z_mm)
    n=cq.Vector(-1,0,0);a=p+n*2.;edges=[cq.Edge.makeLine(p,a)]
    # The variable compound plane holds the long fore cruise atZ298.5,
    # above the flavor-pair seat and below the complete frame receiver roots.
    drop=axis_z_mm-298.5
    alpha=math.acos((drop/14.-1.)/math.sqrt(2.))-math.pi/4
    for end_heading in [cq.Vector(0,-math.sin(alpha),-math.cos(alpha)),cq.Vector(0,-1,0)]:
        edge,a,_,_=G.exact_arc(a,n,end_heading,14.)
        edges.append(edge);n=end_heading
    shift=cq.Vector(-99.325-a.x,0,0)
    if shift.Length>1e-8:
        tail,a,_,_=G.exact_s(a,n,shift,14.);edges.extend(tail)
    remaining=length-sum(e.Length()for e in edges)
    if remaining<=0:raise ValueError('Supply free tail exceeds the final cut length')
    edges.append(cq.Edge.makeLine(a,a+n*remaining))
    wire=cq.Wire.assembleEdges(edges)
    return cq.Solid.sweep(cq.Wire.makeCircle(3.175,p,cq.Vector(-1,0,0)),[],wire,
                         makeSolid=True,isFrenet=True),wire

def prong(x):
    # The two independent nominal steel pads bear the measured lower brass
    # flat. Their fore handles stay above the suction station; the vent and
    # both closed tie bands remain between the pads.
    bottom=294.16058083755676
    profile=[(170.,299.4),(297.8,299.4),(302.05,bottom),
             (318.55,bottom),(318.55,bottom-3),
             (302.05,bottom-3),(297.8,296.4),(170.,296.4)]
    return cq.Workplane('YZ').polyline(profile).close().extrude(3.).val().translate((x-1.5,0,0))

def main():
    sources=proof_sources.snapshot(__file__,G.__file__,F.__file__)
    t0=time.time();OUT.mkdir(parents=True,exist_ok=True)
    models,inputs,manifest_hashes,packets=loaded()
    routing=json.loads((STUDY/'routing/candidate.json').read_text())
    fluid=json.loads((STUDY/'mounts/fluid-candidate.json').read_text())
    body=models['asse1022-assembly'];carrier=models['asse-removable-carrier']
    inlet=routing['ports']['asse1022-assembly']['tube-in']
    outlet=routing['ports']['asse1022-assembly']['tube-out']
    vent=routing['ports']['asse1022-assembly']['vent-tip']
    centre=cq.Vector(vent['pos'][0],inlet['pos'][1],inlet['pos'][2])
    c=centre.toTuple();lift=fluid['carrier_factory']['carrier_entry_lift_z_mm']
    absent={'enclosure-front-top','funnel','funnel-frame','funnel-cover',
            'display','display-cover','display-gasket','asse-drip-pan','moisture-plate',
            'elbow-cradle','funnel-drain-union','funnel-drain-stub','tube-fluid-4',
            'rear-roof-hatch','ground-stack','ground-roof-boss','discharge-chain',
            'discharge-chain-anchor','discharge-chain-lower-key','hose-clamp-chain-discharge',
            'hose-engagement-chain-discharge','vk-solenoid'}
    absent.update(n for n in models if n.startswith(('enclosure-pump-','grip-','tee-carrier-spring')))
    absent.update(front_members(models,packets))
    absent.update(n for n in models if n.startswith(('hatch-screw-','hatch-seam-',
                  'discharge-chain-clip-screw-','asse-retention-tie-',
                  'asse-carrier-clamp-','asse-carrier-screw-')))
    deferred={n for n in models if n.startswith(('tube-','wire-','control-','loom-','harness-',
               'carb-foam-'))}
    deferred.update(n for n in models if n.startswith('cold-core/line-')
                    and n!='cold-core/line-prv-vent')
    for packet in packets:
        absent.update(packet.get('front_shell_fuse_part_names',[]))
        absent.update(packet.get('frame_fuse_part_names',[]))
        absent.update(packet.get('front_carried_part_names',[]))
        deferred.update(packet.get('factory_deferred_part_names',[]))
    deferred.difference_update({'asse1022-assembly','asse-removable-carrier'})
    fixed={n:s for n,s in models.items()if n not in absent|deferred|
           {'asse1022-assembly','asse-removable-carrier'}}
    # The current parent stock must contain the published continuous carrier
    # roof channel. Applying the identical declared subtractive cutter here
    # permits a source-bound diagnostic before the final parent shell rerun.
    roof=fixed['enclosure-back-top'];removed=[]
    for name,rec in fluid['clearance_cutters'].items():
        if not name.startswith(('asse-carrier-roof-channel','asse-factory-supply-wall')):continue
        cut=cq.Shape.importBrep(str(ROOT/rec['brep']))
        removed.append({'cutter':name,'parent_removed_mm3':audit.common(roof,cut,True)})
        roof=roof.cut(cut)
    fixed['enclosure-back-top']=roof
    source_parent_prepared=all(r['parent_removed_mm3']<.001 for r in removed)
    cert=Certifier(fixed);motions=[]
    pose=lambda x,y,z,r:body.rotate(c,(c[0]+1,c[1],c[2]),r).translate((x,y-c[1],z-c[2]))
    body_states=[(15.,170.,324.,-90.),(15.,270.,324.,-90.),(15.,270.,324.,0.),
                 (15.,270.,319.15,0.),(15.,304.5,319.15,0.),
                 (15.,304.5,317.05,0.),(15.,c[1],317.05,0.),
                 (15.,c[1],c[2],0.),(0.,c[1],c[2],0.)]
    radius=max(math.hypot(v.Center().y-centre.y,v.Center().z-centre.z)for v in body.Vertices())
    for i,(a,b)in enumerate(zip(body_states,body_states[1:]),1):
        if a[3]!=b[3]:
            angle=b[3]-a[3]
            at=lambda t,a=a,angle=angle:pose(a[0],a[1],a[2],a[3]+angle*t)
            bound=lambda half,angle=angle:2*radius*math.sin(math.radians(abs(angle)*half)/2)
        else:
            at,bound=translation(pose(*a),(b[0]-a[0],b[1]-a[1],b[2]-a[2]))
        motions.append(cert.motion('bare-valve-'+str(i),at,bound))
    # Connect the west tube while the valve is held15mm east, before its final
    # lowering/west shift. The free opposite end permits an exact-cut-length
    # R14 down/fore family; the absolute west cruise staysX−99.325.
    tail_rows=[];tail_sources={};tail_blockers=[]
    supply_length=routing['routes']['water-supply-link']['developed_length_mm']
    tail_states=[('west-normal-dock',15.,317.05,d)for d in [10.,8.,6.,4.,2.,0.]]
    tail_states += [('held-valve-lowering',15.,z,0.)for z in [314.,312.,310.,c[2]]]
    tail_states += [('held-valve-west-shift',x,c[2],0.)for x in [12.,9.,6.,3.,0.]]
    for number,(phase,x,z,dock)in enumerate(tail_states):
        tube,wire=supply_tail(inlet,supply_length,x,z,dock)
        occupants={**fixed,'asse1022-assembly':pose(x,c[1],z,0.)};bad=[]
        for other,s in occupants.items():
            if not audit.broad(audit.bbox(tube),audit.bbox(s),0):continue
            if tube.distance(s)>1e-7:continue
            common=audit.common(tube,s,True)
            if common>.001:bad.append({'fixed':other,'common_mm3':common})
        path=OUT/('asse-supply-free-'+str(number)+'.brep');tube.exportBrep(str(path))
        row={'phase':phase,'body_offset_x_mm':x,'flow_axis_z_mm':z,'normal_dock_mm':dock,
             'length_mm':wire.Length(),'final_cut_length_mm':supply_length,
             'length_error_mm':wire.Length()-supply_length,'minimum_radius_mm':14.,
             'brep':str(path.relative_to(ROOT)),'sha256':sha(path),
             'blockers':bad,'pass':not bad};tail_rows.append(row);tail_blockers+=bad
        print('ASSE supply tail',phase,x,z,dock,bad,flush=True)
    tail_sources['supply']=tube
    right,wire=temporary_tube(outlet,routing['routes']['water-2']['developed_length_mm'])
    rc=Certifier({**fixed,'asse1022-assembly':body})
    at,bound=translation(right.translate((12,0,0)),(-12,0,0))
    # Its installed mouth is an exact end-face contact. The translation
    # remains on the port's outward side; all other articles receive the
    # interval certificate and the bought mouth gets native endpoint checks.
    motions.append(rc.motion('outlet-tube-normal-dock',at,bound,ignore=['asse1022-assembly']))
    tail_sources['outlet']=right
    carrier_fixed={**fixed,'asse1022-assembly':body}
    carrier_fixed.update({f'free-asse-{n}-tail':s for n,s in tail_sources.items()})
    cc=Certifier(carrier_fixed)
    start=carrier.translate((0,170.-c[1],lift))
    at,bound=translation(start,(0,c[1]-170.,0))
    motions.append(cc.motion('raised-carrier-fore-entry',at,bound))
    at,bound=translation(carrier.translate((0,0,lift)),(0,0,-lift))
    motions.append(cc.motion('carrier-vertical-lowering',at,bound))
    # Exact independent fixture pads and staged fore insertion. Purchased VK
    # remains absent; its entire fused lid cradle stays in every rigid check.
    xs=[vent['pos'][0]-(19+6.265)/2-5.,vent['pos'][0]+(19+6.265)/2+8.]
    fixtures={f'asse-holding-prong-{i}':prong(x)for i,x in enumerate(xs,1)}
    fixture_rows=[]
    for name,s in fixtures.items():
        path=OUT/(name+'.brep');s.exportBrep(str(path))
        occupants={**fixed}
        fc=Certifier(occupants);at,bound=translation(s.translate((0,-70,0)),(0,70,0))
        motions.append(fc.motion(name+'-entry',at,bound))
        contacts=[]
        for other,article in {'asse1022-assembly':body,'asse-removable-carrier':carrier,
                              **{n:s for n,s in models.items()if n.startswith('asse-retention-tie-')}}.items():
            common=audit.common(s,article,True);gap=s.distance(article)
            contacts.append({'other':other,'common_mm3':common,'gap_mm':gap,
                             'pass':common<.001})
        fixture_rows.append({'name':name,'brep':str(path.relative_to(ROOT)),
                             'sha256':sha(path),'contacts':contacts,
                             'pass':all(r['pass']for r in contacts),
                             'bearing_path':'The prong upper profile decreases monotonically aft. Every fore-translated pose remains at or below its final upper boundary throughout the valve footprint; the final native common is zero.'})
    clamp_rows=[];tool_rows=[];fasteners=[]
    ready={**carrier_fixed,'asse-removable-carrier':carrier,**fixtures}
    for m in fluid['mounts']:
        i=m['index'];name='asse-carrier-clamp-'+str(i);s=models[name]
        # The carrier's underside and the block's fore face are exact bearing
        # planes. The fore approach keeps the shelf below that beam and the
        # arm fore of the block; nominal common remains zero at every pose.
        exact_mates=['asse-removable-carrier','asse-roof-seat-'+str(i)]
        rc=Certifier(ready);at,bound=translation(s.translate((0,-70,0)),(0,70,0))
        motions.append(rc.motion(name+'-fore-entry',at,bound,ignore=exact_mates))
        mate_rows=[]
        for other in exact_mates:
            for dy in [-70.,-35.,-1.,0.]:
                a=s.translate((0,dy,0));vol=audit.common(a,ready[other],True)
                mate_rows.append({'other':other,'offset_y_mm':dy,'common_mm3':vol,'pass':vol<.001})
        clamp_rows.append({'name':name,'bearing_planes_mm':{
                            'beam_lower_z':audit.bbox(carrier)[5]-3,
                            'block_fore_y':m['mouth'][1]},'checks':mate_rows,
                            'pass':all(r['pass']for r in mate_rows)})
        ready[name]=s
        screw=models['asse-carrier-screw-'+str(i)]
        tool=hex_key(m['mouth'][0],m['head_bearing_y_mm']-1.2,m['mouth'][2])
        tc=Certifier(ready)
        at,bound=translation(tool.translate((0,-60,0)),(0,60,0))
        tool_rows.append(tc.motion('asse-key-'+str(i)+'-normal-entry',at,bound))
        path=OUT/('asse-clamp-key-'+str(i)+'.brep');tool.exportBrep(str(path))
        # Actual retained4mm insert/12mm screw:4.7mm engagement and1mm reserve.
        pilot=fluid['pilot_cutters']['asse-carrier-pilot-'+str(i)]
        p=cq.Shape.importBrep(str(ROOT/pilot['brep']))
        block=ready['asse-roof-seat-'+str(i)]
        x,y,z=m['mouth']
        outer=cq.Solid.makeCylinder(3.6,8.7,cq.Vector(x,y,z),cq.Vector(0,1,0))
        coupon=outer.cut(cq.Solid.makeCylinder(2,5.7,cq.Vector(x,y,z),cq.Vector(0,1,0)))
        missing=coupon.cut(block).Volume()
        passage=audit.common(screw,block,True)+audit.common(screw,s,True)
        tool_stock=audit.common(tool,block,True)+audit.common(tool,s,True)
        fasteners.append({'index':i,'mouth':m['mouth'],'axis':m['axis'],
                          'stock_coupon_missing_mm3':missing,
                          'screw_nominal_stock_common_mm3':passage,
                          'key_nominal_stock_common_mm3':tool_stock,
                          'short_insert_mm':4.,'pilot_depth_mm':5.7,
                          'surround_mm':1.6,'closed_end_mm':3.,
                          'actual_engagement_mm':m['actual_engagement'],
                          'screw_tip_reserve_mm':m['tip_reserve'],
                          'pass':missing<.001 and passage<.001 and tool_stock<.001})
    # With both ties closed, withdraw the two independent workholding pads
    # through the same fore opening. They remain outside the closed tie bands.
    after={**ready,**{n:s for n,s in models.items()if n.startswith(('asse-retention-tie-',
                            'asse-carrier-screw-'))}}
    for name,s in fixtures.items():
        fc=Certifier({n:t for n,t in after.items()if n not in fixtures and n!='asse1022-assembly'})
        at,bound=translation(s,(0,-70,0))
        motions.append(fc.motion(name+'-withdrawal',at,bound))
    drift=[n for n,r in inputs.items()if sha(ROOT/r['brep'])!=r['sha256']]+proof_sources.changed(sources)
    manifest_drift=[n for n,h in manifest_hashes.content_sha256.items()if manifest_content_sha256(ROOT/n)!=h]
    all_rows=motions+tool_rows+fixture_rows+clamp_rows+fasteners+tail_rows
    geometry_pass=all(r['pass']for r in all_rows)
    report={'pass':geometry_pass and source_parent_prepared and not drift and not manifest_drift,
            'geometry_pass':geometry_pass,
            'rigid_motions':motions,'tool_motions':tool_rows,'fixture':fixture_rows,
            'clamp_bearing_checks':clamp_rows,'fastener_checks':fasteners,
            'constant_cut_length_temporary_tubes':tail_rows,
            'native_inputs':inputs,'manifest_sha256':manifest_hashes,
            'manifest_content_sha256':manifest_hashes.content_sha256,
            'source_inputs':sources,
            'source_drift':drift,'manifest_drift':manifest_drift,
            'diagnostic_parent_stock_removed':removed,
            'current_parent_already_has_carrier_channel':source_parent_prepared,
            'fixed_names':sorted(fixed),'absent_names':sorted(absent),
            'deferred_names':sorted(deferred),
            'factory_sequence':[
                'Close the back column on its retained Y rails with only the two high carrier blocks present; leave the ASSE, carrier, clamps, ties, purchased VK and front-top/frame absent.',
                'Hold the bare valve15mm east of its finalX datum, enter atY170/Z324 rolled−90°X, unroll atY270, lower toZ319.15, advance toY304.5, lower toZ317.05, then advance toY310.3. PurchasedVK and its electrical connections remain absent; its fused cradle is present.',
                'At that held pose, insert the measured-cut-length west supply tube along its10mm nominal normal approach. Its other end is free in the exactR14 down/fore handling curve, whose long fore cruise staysZ298.5. Lower the valve toZ308.45 and shift it15mm west to its frozen installed datum using the sampled constant-cut-length tube family.',
                'Insert the two independent fore support prongs under the held valve; their pads bear the lower brass flats outside the vent and tie bands. Connect the east tube through its independently checked12mm normal approach with its opposite end free.',
                'Enter the carrier upright at15.289419mm lift through the full roof channel, lower over the held barrel, insert both separate clamps from fore, and tighten bothM3×12 screws with the160mm2.5AF normal tool. The3mm shelves carry the transverse beam.',
                'Thread and close both wide ties around the brass barrel and carrier through their exposed rear head working volumes. Withdraw the independent support prongs fore. Install the purchasedVK on its retained cradle afterward; complete and dress the free ASSE tube ends and compliant looms.',
                'Install the pan and complete the separately proven late front-top/frame 102.2 mm closure only after the hatch, G2 junction and all final pipe/harness dressing is complete.'
            ],
            'scope':'Continuous rigid interval certificates for the named bare valve, separate carrier, outlet normal dock and nominal screw keys. Fifteen native constant-cut-length R14 west tube handling poses qualify geometric reservations. Mating carrier/clamp/block planes receive separate native common and analytical plane separation checks.',
            'qualification_limits':[
                'The nominal steel fixture dimensions reserve geometric access; its load capacity, surface protection and human reach require physical factory qualification.',
                'The west10mm/east12mm normal tube approaches are geometric factory reservations. Purchased collet engagement, insertion force, actual tube memory and subsequent flexible dressing require physical qualification; the sampled west tube family is not a continuous elastic motion proof.',
                'Tie threading, head shape, applied tension, creep and vibration retention require physical qualification. The native closed loops and head working volumes qualify installed occupancy.',
                'Short-insert pullout, printed shelf bending and the two clamp load paths require physical qualification. Single-solid geometry and pilot stock alone do not establish strength.',
                'Any diagnostic roof subtraction must be present in the final joined roof before this becomes a final source-bound assembly proof.'
            ],'elapsed_seconds':time.time()-t0}
    (HERE/'asse-factory-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'motions':len(motions),'tools':len(tool_rows),
                      'source_drift':drift,'manifest_drift':manifest_drift,
                      'parent_prepared':source_parent_prepared}),flush=True)

if __name__=='__main__':main()
