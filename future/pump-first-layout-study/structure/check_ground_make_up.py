"""Native free-end wire reservations for preassembled rear-hatch ground lugs.

All four wires are crimped and the fan is torqued on the removed article. Their
opposite ends remain free while it lands; the wire cut lengths are retained by
moving those free tail endpoints. This makes no fixed-end stretch claim.
"""
from pathlib import Path
import sys,json,hashlib,math
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY/'pump'))
import generate as G
sys.path.insert(0,str(STUDY/'wiring'))
from ground_interfaces import CIRCUIT_LABELS,CIRCUIT_RING_INDICES
from evidence_binding import manifest_content_sha256
from structure import proof_sources
OUT=ROOT/'.cache/pump-first-layout/structure/roof-hatch/ground-make-up'
POWER_ROUTE_KEYS=['AC6-G','PE-carbonator','PE-feed','PE-under-counter']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def port(index,datum,clock):
    physical=CIRCUIT_RING_INDICES[CIRCUIT_LABELS[index]]
    angle=math.radians(clock-physical*60.)
    axis=cq.Vector(math.cos(angle),math.sin(angle),0)
    origin=cq.Vector(*datum)+axis*9+cq.Vector(0,0,-2.1-.8*physical)
    return origin,axis


def wire_at(index,lift,length,datum,clock):
    origin,heading=port(index,datum,clock)
    origin+=cq.Vector(0,0,lift)
    lead=.5
    p=origin+heading*lead
    edges=[cq.Edge.makeLine(origin,p)]
    r=3.4
    down=cq.Vector(0,0,-1)
    if index==0:
        edge,p,_,_=G.exact_arc(p,heading,cq.Vector(0,-1,0),r)
        edges.append(edge);heading=cq.Vector(0,-1,0)
    elif index==2:
        for target in [cq.Vector(0,1,0)]:
            edge,p,_,_=G.exact_arc(p,heading,target,r)
            edges.append(edge);heading=target
    elif index==3:
        # The physical second ring escapes fore/east of the controller's
        # aft corner. Turn east before descending through that open lane.
        edge,p,_,_=G.exact_arc(p,heading,cq.Vector(1,0,0),r)
        edges.append(edge);heading=cq.Vector(1,0,0)
        east_lead=4.807
        q=p+heading*east_lead;edges.append(cq.Edge.makeLine(p,q));p=q
    edge,p,_,_=G.exact_arc(p,heading,down,r)
    edges.append(edge)
    plane=326.
    stop=cq.Vector(p.x,p.y,plane+r)
    if stop.z>=p.z:
        raise ValueError(('Insufficient down leg',index,lift,p.z,stop.z))
    edges.append(cq.Edge.makeLine(p,stop))
    p=stop
    heading=down
    tail_heading=cq.Vector(-1,0,0)if index==0 else cq.Vector(0,-1,0)
    edge,p,_,_=G.exact_arc(p,heading,tail_heading,r)
    edges.append(edge)
    heading=tail_heading
    if index==0:
        edge,p,_,_=G.exact_arc(p,heading,cq.Vector(0,-1,0),r)
        edges.append(edge)
        heading=cq.Vector(0,-1,0)
    elif index==1:
        tail,p,_,_=G.exact_s(p,heading,cq.Vector(-3,0,0),r)
        edges.extend(tail)
    used=sum(e.Length() for e in edges)
    if used>=length:
        raise ValueError(('Temporary make-up needs more than cut length',index,lift,used,length))
    end=p+heading*(length-used)
    edges.append(cq.Edge.makeLine(p,end))
    return cq.Wire.assembleEdges(edges),origin,heading,end


def main(hatch_path=None,report_path=None,lifts=None):
    import check_hatch_hose as HH
    sources=proof_sources.snapshot(__file__,G.__file__,HH.__file__,
                                  STUDY/'wiring/ground_interfaces.py',
                                  STUDY/'wiring/native_harness.py')
    OUT.mkdir(parents=True,exist_ok=True)
    hatch_file=Path(hatch_path)if hatch_path else HERE/'roof-hatch.json'
    hatch=json.loads(hatch_file.read_text())
    structure=json.loads((HERE/'candidate.json').read_text())
    power=json.loads((STUDY/'wiring/power-candidate.json').read_text())
    mount=next(m for m in structure['mounts'] if m['owner']=='ground-stack')
    datum=mount['mouth'];clock=mount.get('clock_degrees',0.)
    if hatch.get('ground_pose_override'):
        datum=hatch['ground_pose_override']['datum_mm'];clock=hatch['ground_pose_override']['clock_degrees']
    keys=POWER_ROUTE_KEYS
    missing=[k for k in keys if k not in power.get('power_routes',{})]
    if missing:
        raise ValueError('Final ground-tail proof requires actual installed cut lengths: '+', '.join(missing))
    targets=[power['power_routes'][k]['length_mm']for k in keys]
    inputs,manifests,packets=HH.current_native_inputs(hatch,hatch_file)
    absent={'enclosure-front-top','funnel','funnel-frame','funnel-cover',
            'asse-drip-pan','moisture-plate','display','display-cover','display-gasket',
            'elbow-cradle','funnel-drain-union','funnel-drain-stub','tube-fluid-4',
            'hatch-seam-silicone'}
    absent|={n for n in inputs if n.startswith(('wire-','control-','loom-','harness-',
                                             'hatch-screw-silicone-cap-','hatch-screw-'))}
    deferred={'tube-water-2','tube-water-3','tube-water-5','tube-water-6',
              'tube-water-supply-link','tube-co2-0','tube-co2-1','tube-carb-1',
              'tube-fluid-1','tube-fluid-2','tube-fluid-14','tube-fluid-18','tube-fluid-28'}
    import check_asse_factory as AF
    absent.update(AF.front_members(inputs,packets))
    for packet in packets:
        for key in ['front_shell_fuse_part_names','front_carried_part_names','frame_fuse_part_names']:
            absent.update(packet.get(key,[]))
        deferred.update(packet.get('factory_deferred_part_names',[]))
    deferred.difference_update(n for n in inputs if n in {'asse1022-assembly','asse-removable-carrier'}
                               or n.startswith(('asse-carrier-','asse-retention-tie-')))
    shapes={n:cq.Shape.importBrep(str(ROOT/r['brep'])) for n,r in inputs.items()
            if n not in absent|deferred}
    carried=set(hatch['carried_names'])|{'rear-roof-hatch'}
    boxes={n:G.bounds(s)for n,s in shapes.items()}
    # Installed fan and normal dock witnesses use every published rigid route,
    # including connections that are left free during the separate landing.
    static_shapes={n:cq.Shape.importBrep(str(ROOT/r['brep']))for n,r in inputs.items()
                   if n not in {'ground-stack','ground-roof-boss','hatch-seam-silicone'}
                   and not n.startswith(('wire-','control-','loom-','harness-','hatch-screw-silicone-cap-'))}
    static_boxes={n:G.bounds(s)for n,s in static_shapes.items()}
    fan=cq.Shape.importBrep(str(ROOT/inputs['ground-stack']['brep']))
    dock_shapes={'ground-stack':fan}
    sys.path.insert(0,str(STUDY/'wiring'))
    from native_harness import sweep
    for i,key in enumerate(keys):
        p,a=port(i,datum,clock)
        label=['compressor','carbonator','feed','under-counter'][i]
        terminal=power['ports']['PE-'+label]
        if (p-cq.Vector(*terminal['point'])).Length>1e-6:
            raise ValueError('Ground factory datum differs from installed port: '+key)
        paths=terminal.get('lead_paths')
        if paths:
            dock_shapes['installed-departure-'+key]=sweep(paths[0],3.2,3.4)[0]
        else:
            dock_shapes['installed-departure-'+key]=cq.Solid.makeCylinder(1.6,8.4,p,a)
    static_checks=[];static_blockers=[]
    for name,s in dock_shapes.items():
        b=G.bounds(s);bad=[];near=[]
        for n,t in static_shapes.items():
            v=static_boxes[n]
            if not all(b[j]<=v[j+3]+1 and v[j]<=b[j+3]+1 for j in range(3)):continue
            gap=s.distance(t)
            if gap>=1-1e-6:continue
            common=G.overlap(s,t)if gap<1e-6 else 0.
            row={'other':n,'gap_mm':gap,'common_mm3':common};near.append(row)
            if common>.01:bad.append(row)
        static_checks.append({'piece':name,'pass':not bad,'blockers':bad,'close_pairs':near})
        static_blockers.extend({'piece':name,**row}for row in bad)
        print('installed ground',name,bad,flush=True)
    checks=[];blockers=[]
    for lift in (lifts if lifts is not None else [22.5,18.,14.,10.,6.,3.,1.,0.]):
        wires={};wire_boxes={}
        if lift<=14:
            import check_hatch_hose as HH
            pump=json.loads((STUDY/'pump/candidate.json').read_text())
            hose_wire,_,_=HH.solve(lift,pump['routes']['water-6']['developed_length_mm'])
            pos,axis=G.point(G.P.discharge(),G.loc(shift=G.PUMP_ORIGIN))
            hose=cq.Solid.sweep(cq.Wire.makeCircle(7.55,cq.Vector(*pos),cq.Vector(*axis)),
                                 [],hose_wire,makeSolid=True,isFrenet=True)
            wires['temporary-water-6']=hose;wire_boxes['temporary-water-6']=G.bounds(hose)
        for i,key in enumerate(keys):
            wire,origin,heading,end=wire_at(i,lift,targets[i],datum,clock)
            _,axis=port(i,datum,clock)
            shape=cq.Solid.sweep(cq.Wire.makeCircle(1.6,origin,axis),[],wire,
                                 makeSolid=True,isFrenet=True)
            path=OUT/(key+'-hatch-z-'+str(lift)+'.brep')
            shape.exportBrep(str(path))
            b=G.bounds(shape);bad=[];near=[]
            for n,source in {**shapes,**wires}.items():
                s=source.translate((0,0,lift)) if n in carried else source
                v=(wire_boxes[n]if n in wire_boxes else boxes[n]).copy()
                if n in carried:
                    v[2]+=lift;v[5]+=lift
                if not all(b[j]<=v[j+3]+1 and v[j]<=b[j+3]+1 for j in range(3)):
                    continue
                gap=shape.distance(s)
                if gap>=1-1e-6:
                    continue
                common=G.overlap(shape,s) if gap<1e-6 else 0.
                row={'other':n,'gap_mm':gap,'common_mm3':common}
                near.append(row)
                if common>.01:
                    bad.append(row);blockers.append({'wire':key,'hatch_lift_z_mm':lift,**row})
            checks.append({'wire':key,'hatch_lift_z_mm':lift,'length_mm':wire.Length(),
                           'target_length_mm':targets[i],'length_error_mm':wire.Length()-targets[i],
                           'physical_ring_index':CIRCUIT_RING_INDICES[CIRCUIT_LABELS[i]],
                           'temporary_handling_plane_z_mm':326.,
                           'normal_barrel_lead_mm':.5,'minimum_radius_mm':3.4,
                           'free_other_end_mm':end.toTuple(),'brep':str(path.relative_to(ROOT)),
                           'sha256':sha(path),'pass':not bad,'close_pairs':near})
            wires['temporary-'+key]=shape
            wire_boxes['temporary-'+key]=b
            print('ground free tail',key,lift,bad,flush=True)
    report={'pass':not blockers and not static_blockers,'checks':checks,'blockers':blockers,
            'installed_fan_and_normal_docks':static_checks,'installed_blockers':static_blockers,
            'datum_mm':datum,'clock_degrees':clock,'native_inputs':inputs,
            'circuit_ring_indices':CIRCUIT_RING_INDICES,
            'manifest_sha256':manifests,
            'manifest_content_sha256':manifests.content_sha256,
            'source_inputs':sources,
            'power_manifest_sha256':manifests[str((STUDY/'wiring/power-candidate.json').relative_to(ROOT))],
            'hatch_manifest_sha256':manifests[str(hatch_file.relative_to(ROOT))],
            'scope':'Four full cut-length free-ended 3.2mm wires at eight hatch heights. The ring ends are precrimped; opposite endpoints move freely during landing and are terminated after seating. Separate installed departure witnesses use the exact published power-port lead paths, including their normal stems and compound R3.4 bends; temporary handling bends start0.5mm past the actual barrel ends.',
            'factory_sequence':['Crimp the four ring-terminal wires at their final cut lengths. Leave their opposite WAGO/lower-boundary ends unterminated.',
                 'Torque the complete ring/washer/M3 stack on the removed hatch with full tool access before PSU installation.',
                 'Present the hatch14mm raised with its four free wire tails in the shown temporary front channel; seat it while the tails absorb motion through their free endpoint positions.',
                 'After seating, move each compliant tail into its separately audited installed route and terminate its opposite end through the open front-top/funnel factory aperture. Complete existing lower-system terminations before closing their retained factory enclosure.',
                 'Torque and seal the hatch only after inspecting the ground make-up and all installed connections.'],
            'limits':['Native temporary curves are geometric reservations, not continuous flexible compliance or a factory dexterity proof.',
                      'The ground screw is fastened on the removed hatch. Seated PSU clearance does not provide a vertical underside160mm key path.',
                      'Lower metalwork bond interfaces are existing unlocated boundaries; this study does not invent connectors or holes below the cap.',
                      'The temporary tails are handling shapes; final electrical occupancy is bound by the power route audit.']}
    drift=[n for n,r in inputs.items()if sha(ROOT/r['brep'])!=r['sha256']]
    report['source_drift']=drift+proof_sources.changed(sources)
    report['manifest_drift']=[n for n,h in manifests.content_sha256.items()if manifest_content_sha256(ROOT/n)!=h]
    report['pass']=report['pass'] and not report['source_drift'] and not report['manifest_drift']
    (Path(report_path)if report_path else HERE/'ground-make-up-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'blockers':len(blockers)}),flush=True)


if __name__=='__main__':
    main()
