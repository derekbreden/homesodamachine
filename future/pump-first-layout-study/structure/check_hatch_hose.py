"""Constant cut-length hose poses for the separate rear hatch's +Z landing.

The fixed west roof pocket retains its installed high plane. Only the final
return S curve gains a vertical component as the hatch rises; the low diagonal
curve changes plane to retain the measured cut length and actual barb normals.
"""
from pathlib import Path
import sys, json, hashlib, math
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY/'pump'))
import generate as G
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources

OUT=ROOT/'.cache/pump-first-layout/structure/roof-hatch/hose-landing'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def wire_at(lift,degrees):
    pos, heading = G.point(G.P.discharge(),G.loc(shift=G.PUMP_ORIGIN))
    start=cq.Vector(*pos)
    heading=cq.Vector(*heading)
    r=15.9
    phi=math.radians(degrees)
    a=start+heading*.5
    edges=[cq.Edge.makeLine(start,a)]
    for end_heading in (cq.Vector(-math.cos(phi),0,-math.sin(phi)),
                        cq.Vector(-1,0,0),cq.Vector(0,0,1)):
        edge,a,_,_=G.exact_arc(a,heading,end_heading,r)
        edges.append(edge)
        heading=end_heading
    riser=a
    shift=cq.Vector(0,426.2-riser.y,0)
    theta=math.acos(1-shift.Length/(2*r))
    axial=2*r*math.sin(theta)
    sstart=cq.Vector(riser.x,riser.y,342-r-axial)
    if sstart.z<=riser.z:
        raise ValueError('Insufficient fixed riser height')
    edges.append(cq.Edge.makeLine(riser,sstart))
    tail,a,_,_=G.exact_s(sstart,heading,shift,r)
    edges.extend(tail)
    edge,a,_,_=G.exact_arc(a,heading,cq.Vector(1,0,0),r)
    edges.append(edge)
    heading=cq.Vector(1,0,0)
    end=cq.Vector(-15,453.5,342+lift)
    shift=cq.Vector(0,end.y-a.y,end.z-a.z)
    if shift.Length>=2*r:
        raise ValueError('Hatch lift exceeds the available R15.9 return offset')
    theta=math.acos(1-shift.Length/(2*r))
    axial=2*r*math.sin(theta)
    bend_start=cq.Vector(end.x-axial,a.y,a.z)
    if bend_start.x<=a.x:
        raise ValueError('Insufficient final return length')
    edges.append(cq.Edge.makeLine(a,bend_start))
    tail,a,_,_=G.exact_s(bend_start,heading,shift,r)
    edges.extend(tail)
    if (a-end).Length>1e-6:
        raise ValueError('Endpoint mismatch')
    return cq.Wire.assembleEdges(edges),riser


def solve(lift,target):
    low,high=.01,G.DISCH_DOWN_DEGREES
    lw,_=wire_at(lift,low)
    hw,_=wire_at(lift,high)
    if not lw.Length()<=target<=hw.Length()+1e-6:
        raise ValueError(('Cut length outside plane family',lift,lw.Length(),target,hw.Length()))
    for _ in range(45):
        mid=(low+high)/2
        wire,riser=wire_at(lift,mid)
        if wire.Length()<target:
            low=mid
        else:
            high=mid
    angle=(low+high)/2
    wire,riser=wire_at(lift,angle)
    return wire,riser,angle


def current_native_inputs(hatch,hatch_path=None):
    """Bind every selected scene module, with freshly recut parents last."""
    inputs=hatch['native_inputs'].copy()
    import audit
    manifests=audit.ManifestHashes();packets=[]
    for relative in ['funnel/candidate.json','pump/candidate.json','pump/fluid24-candidate.json',
                     'routing/candidate.json','structure/candidate.json','mounts/candidate.json',
                     'mounts/fluid-candidate.json','routing/co2-candidate.json','mounts/body-candidate.json',
                     'mounts/water5-hosts.json','routing/tube-hosts.json',
                     'wiring/control-reserves.json','wiring/control-fanouts-check.json',
                     'wiring/controls-candidate.json','wiring/power-candidate.json',
                     'structure/roof-hatch.json','structure/scene-stock.json']:
        path=Path(hatch_path)if relative=='structure/roof-hatch.json' and hatch_path else STUDY/relative
        if path.exists():
            packet=json.loads(path.read_text())
            if relative=='structure/scene-stock.json' and not proof_sources.scene_stock_current(packet):continue
            manifests[str(path.relative_to(ROOT))]=sha(path);packets.append(packet)
            manifests.content_sha256[str(path.relative_to(ROOT))]=content_sha256(packet)
            for n,rec in packet.get('parts',{}).items():
                inputs[n]={'brep':rec['brep'],'sha256':sha(ROOT/rec['brep'])}
    return inputs,manifests,packets


def main():
    sources=proof_sources.snapshot(__file__,G.__file__,HERE/'check_asse_factory.py')
    OUT.mkdir(parents=True,exist_ok=True)
    hatch=json.loads((HERE/'roof-hatch.json').read_text())
    pump=json.loads((STUDY/'pump/candidate.json').read_text())
    inputs,manifests,packets=current_native_inputs(hatch)
    carried=set(hatch['carried_names'])|{'rear-roof-hatch'}
    absent={'enclosure-front-top','funnel','funnel-frame','funnel-cover',
            'asse-drip-pan','moisture-plate','display','display-cover','display-gasket',
            'elbow-cradle','funnel-drain-union','funnel-drain-stub','tube-fluid-4',
            'hose-engagement-pump-discharge','hose-clamp-pump-discharge',
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
    # The ASSE is assembled before this separate hatch phase. Its earlier
    # column-slide deferral must not remove installed hardware here.
    deferred.difference_update(n for n in inputs if n in {'asse1022-assembly','asse-removable-carrier'}
                               or n.startswith(('asse-carrier-','asse-retention-tie-')))
    shapes={n:cq.Shape.importBrep(str(ROOT/rec['brep'])) for n,rec in inputs.items()
            if n not in absent|deferred}
    target=pump['routes']['water-6']['developed_length_mm']
    pos,axis=G.point(G.P.discharge(),G.loc(shift=G.PUMP_ORIGIN))
    poses=[]
    blockers=[]
    for lift in range(14,-1,-1):
        wire,riser,angle=solve(lift,target)
        hose=cq.Solid.sweep(cq.Wire.makeCircle(7.55,cq.Vector(*pos),cq.Vector(*axis)),
                            [],wire,makeSolid=True,isFrenet=True)
        path=OUT/('water6-hatch-z-'+str(lift)+'.brep')
        hose.exportBrep(str(path))
        b=G.bounds(hose)
        rows=[]
        for n,source in shapes.items():
            s=source.translate((0,0,lift)) if n in carried else source
            v=G.bounds(s)
            if not all(b[j]<=v[j+3]+1 and v[j]<=b[j+3]+1 for j in range(3)):
                continue
            gap=hose.distance(s)
            if gap>=1-1e-6:
                continue
            common=G.overlap(hose,s) if gap<1e-6 else 0.
            row={'other':n,'hatch_lift_z_mm':lift,'gap_mm':gap,'common_mm3':common}
            rows.append(row)
            if common>.01:
                blockers.append(row)
        poses.append({'hatch_lift_z_mm':lift,'plane_degrees':angle,'length_mm':wire.Length(),
                      'length_error_mm':wire.Length()-target,'minimum_radius_mm':15.9,
                      'fixed_west_high_plane_z_mm':342.,'west_riser_mm':riser.toTuple(),
                      'brep':str(path.relative_to(ROOT)),'sha256':sha(path),
                      'close_pairs':rows,'pass':not any(r['common_mm3']>.01 for r in rows)})
        print('hatch hose',lift,'angle',round(angle,5),'close',rows,flush=True)
    report={'pass':not blockers,'target_length_mm':target,'poses':poses,'blockers':blockers,
            'native_inputs':inputs,'manifest_sha256':manifests,
            'manifest_content_sha256':manifests.content_sha256,
            'source_inputs':sources,
            'hatch_manifest_sha256':manifests[str((HERE/'roof-hatch.json').relative_to(ROOT))],
            'deferred_connections':sorted(deferred),'absent_names':sorted(absent),
            'source_drift':[n for n,r in inputs.items() if sha(ROOT/r['brep'])!=r['sha256']]+proof_sources.changed(sources),
            'scope':'Fifteen exact nominal R15.9 constant-length braided hose poses for a separate hatch +Z landing from14mm raised to seated. The fixed west high plane remains Z342.',
            'limits':['Sampled available geometry is not a continuous elastic deformation, PVC memory, clamp load or factory dexterity proof.',
                      'The pump end remains clamped; engage the free discharge-chain end with its hatch raised14mm, then follow this family while landing.',
                      'The water5 core end and roof-to-floor electrical harnesses remain free until the hatch is seated; their final installed occupancy belongs to the whole assembly audit.']}
    report['pass']=report['pass'] and not report['source_drift']
    report['manifest_drift']=[n for n,h in manifests.content_sha256.items()if manifest_content_sha256(ROOT/n)!=h]
    report['pass']=report['pass'] and not report['manifest_drift']
    (HERE/'hatch-hose-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'blockers':len(blockers)}),flush=True)


if __name__=='__main__':
    main()
