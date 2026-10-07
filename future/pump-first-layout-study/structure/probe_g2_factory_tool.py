"""Concrete fore-aperture hook and wire entry for the final ground junction."""
from pathlib import Path
import sys,json,math,hashlib
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY/'pump'))
import generate as G
from evidence_binding import manifest_content_sha256
from structure import proof_sources
OUT=ROOT/'.cache/pump-first-layout/structure/g2-factory-tool'
def main(hatch_path=None,report_path=None):
    import check_hatch_hose as HH
    import check_asse_factory as AF
    sources=proof_sources.snapshot(__file__,G.__file__,HH.__file__,AF.__file__)
    OUT.mkdir(parents=True,exist_ok=True)
    hatch_path=Path(hatch_path)if hatch_path else HERE/'roof-hatch.json'
    h=json.loads(hatch_path.read_text())
    recs,manifests,packets=HH.current_native_inputs(h,hatch_path)
    absent={'enclosure-front-top','funnel','funnel-frame','funnel-cover','display','display-cover','display-gasket'}
    absent.update(AF.front_members(recs,packets))
    for packet in packets:
        for key in ['front_shell_fuse_part_names','front_carried_part_names','frame_fuse_part_names']:
            absent.update(packet.get(key,[]))
    shapes={n:cq.Shape.importBrep(str(ROOT/r['brep']))for n,r in recs.items()
            if n not in absent and not n.startswith(('wire-','control-','loom-'))}
    inputs={n:{'brep':recs[n]['brep'],'sha256':hashlib.sha256((ROOT/recs[n]['brep']).read_bytes()).hexdigest()}for n in shapes}
    channel=cq.Solid.makeBox(20.8,5.65,9,cq.Vector(-53.15,322.,343.)).fuse(
        cq.Solid.makeBox(4.7,18.6,9,cq.Vector(-45.8,326.7,343.)))
    parent_channel_common=G.overlap(shapes['enclosure-back-top'],channel)
    boxes={n:G.bounds(s)for n,s in shapes.items()}
    p=cq.Vector(-42.75,342.,349.);heading=cq.Vector(0,1,.47).normalized()
    r=1.1
    edge,a,_,_=G.exact_arc(p,heading,cq.Vector(0,0,-1),r)
    end=a+cq.Vector(0,0,-.2)
    thin_start=p-heading*30
    wire=cq.Wire.assembleEdges([cq.Edge.makeLine(thin_start,p),edge,cq.Edge.makeLine(a,end)])
    tip=cq.Solid.sweep(cq.Wire.makeCircle(.65,thin_start,heading),[],wire,makeSolid=True,isFrenet=True)
    handle=cq.Solid.makeCylinder(1.25,60,thin_start-heading*60,heading)
    tool=tip.fuse(handle)
    poses=[];bad=[]
    for angle in [0.,30.,60.,90.,120.,150.,180.]:
        s=tool.rotate(p.toTuple(),(p+heading).toTuple(),angle)
        travels=[0.]if angle<180 else[0.,2.,5.,10.,12.]
        for travel in travels:
            t=s.translate(tuple(-heading*travel));rows=[];b=G.bounds(t)
            for n,u in shapes.items():
                q=boxes[n]
                if not all(b[j]<=q[j+3] and q[j]<=b[j+3]for j in range(3)):continue
                if t.distance(u)>1e-6:continue
                v=G.overlap(t,u)
                if v>.01:rows.append({'other':n,'common_mm3':v})
            path=OUT/('hook-'+str(angle)+'-'+str(travel)+'.brep');t.exportBrep(str(path))
            pose={'roll_degrees':angle,'withdraw_mm':travel,'pass':not rows,'blockers':rows,
                  'brep':str(path.relative_to(ROOT))};poses.append(pose)
            if rows:bad+=rows
            print('hook',angle,travel,rows,flush=True)
    # After the hook clears the fore face, lower and flatten it in the local
    # roof channel. Its reinforced shank then leaves horizontally above VK.
    source=tool.rotate(p.toTuple(),(p+heading).toTuple(),180).translate(tuple(-heading*12))
    pivot=p-heading*12
    flattened=None
    staged=[]
    for drop in [1.,2.,3.,pivot.z-340.]:
        staged.append(('lower-'+str(drop),source.translate((0,0,-drop))))
    low=source.translate((0,0,340-pivot.z));centre=cq.Vector(pivot.x,pivot.y,340)
    alpha=math.degrees(math.atan(.47))
    for pitch in [-5.,-10.,-15.,-20.,-alpha]:
        t=low.rotate(centre.toTuple(),(centre+cq.Vector(1,0,0)).toTuple(),pitch)
        staged.append(('flatten-'+str(pitch),t))
        flattened=t
    for travel in [10.,20.,40.,60.,80.]:
        staged.append(('horizontal-out-'+str(travel),flattened.translate((0,-travel,0))))
    for label,t in staged:
        rows=[];b=G.bounds(t)
        for n,u in shapes.items():
            q=boxes[n]
            if not all(b[j]<=q[j+3] and q[j]<=b[j+3]for j in range(3)):continue
            if t.distance(u)>1e-6:continue
            v=G.overlap(t,u)
            if v>.01:rows.append({'other':n,'common_mm3':v})
        path=OUT/(label+'.brep');t.exportBrep(str(path))
        poses.append({'pose':label,'pass':not rows,'blockers':rows,'brep':str(path.relative_to(ROOT))})
        if rows:bad+=rows
        print(label,rows,flush=True)
    power=json.loads((STUDY/'wiring/power-candidate.json').read_text())
    feed=power['power_routes']['PE-feed']['from']
    if feed['label']!='wago-g:2':raise ValueError('Ground feed must terminate at the measured second G distribution groove')
    mouth=cq.Vector(*feed['point']);normal=cq.Vector(*feed['axis'])
    entry=cq.Solid.makeCylinder(1.6,34,mouth+normal*34,-normal)
    rows=[];b=G.bounds(entry)
    for n,u in shapes.items():
        q=boxes[n]
        if not all(b[j]<=q[j+3] and q[j]<=b[j+3]for j in range(3)):continue
        v=G.overlap(entry,u)
        if v>.01:rows.append({'other':n,'common_mm3':v})
    print('wire insertion',rows,flush=True)
    path=OUT/'g2-fore-channel.brep';channel.exportBrep(str(path))
    working=cq.Solid.makeBox(7.6,9.3,6.85,cq.Vector(-46.55,334.55,344.15))
    engagement=G.overlap(tool,working)
    report={'pass':not bad and not rows and engagement>.01 and parent_channel_common<.001,
            'tool_poses':poses,'wire_entry_blockers':rows,
            'current_parent_already_has_tool_channel':parent_channel_common<.001,
            'undeclared_parent_channel_stock_mm3':parent_channel_common,
            'native_inputs':inputs,'manifest_sha256':manifests,
            'manifest_content_sha256':manifests.content_sha256,
            'source_inputs':sources,
            'actual_wire_entry_point_mm':feed['point'],'wire_entry_normal':feed['axis'],
            'hatch_manifest_sha256':manifests[str(hatch_path.relative_to(ROOT))],
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_drift':[n for n,r in inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]+proof_sources.changed(sources),
            'nominal_fixture_enters_measured_lever_working_volume_mm3':engagement,
            'channel':{'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                       'print_owner':'enclosure-back-top','minimum_roof_stock_mm':3.},
            'tool':{'tip_diameter_mm':1.3,'reinforced_shank_diameter_mm':2.5,'hook_radius_mm':1.1,
                    'thin_reach_mm':30,'shank_length_mm':60,'slope_dz_dy':.47},
            'scope':'Rigid nominal fixture approach/roll/withdrawal and 34mm normal wire insertion before the front-top/frame/funnel closes, with final flexible harnesses not yet dressed in this channel. Lever force and pad contact are physical qualification; the source lever model is a measured working envelope.'}
    report['pass']=report['pass'] and not report['source_drift']
    report['manifest_drift']=[n for n,v in manifests.content_sha256.items()if manifest_content_sha256(ROOT/n)!=v]
    report['pass']=report['pass'] and not report['manifest_drift']
    (Path(report_path)if report_path else HERE/'g2-factory-tool-probe.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
