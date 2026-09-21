"""Current split/regulator placement, complete anchors and local west-wall stock."""
from pathlib import Path
import hashlib,json,sys,time,zipfile
import cadquery as cq
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file());HERE=ROOT/'.cache/scanner-review/split-regulator-wall';HERE.mkdir(parents=True,exist_ok=True)
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(ROOT/'hardware/scripts')]
import enclosure_assembly as A
E=A._enc
PACK=Path('/tmp/scanner-review/integration-correction/route-pack'); rec=json.loads((PACK/'frames.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bb(s):
 b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def vol(s):return abs(s.Volume())
start=time.monotonic();sources={str(p.relative_to(ROOT)):sha(p) for p in [Path(A.__file__),Path(E.__file__),Path(A._split.__file__),Path(A._flowreg.__file__),Path(E._interface.__file__),Path(A._split.tee.__file__),Path(A._lines.__file__)]}
funnel_path=PACK.parent/'route-neighbors/funnel.brep'
funnel=cq.Shape.importBrep(str(funnel_path))
sources[str(funnel_path)]=sha(funnel_path)
sources[str(PACK/'frames.json')]=sha(PACK/'frames.json')
p,axis,_d=rec['asse1022-assembly']['ports']['tube-out']
split,sc=A.build_split(lambda _station:(p,axis));reg,rc=A.build_flowreg(sc)
placed={'water-split':(split,None),'flow-regulator':(reg,None)}
pockets=A.flank_reliefs(placed);raw=A.body_anchors({'water-split':sc,'flow-regulator':rc});stations=A.stand_anchors(raw)
roots,lane=E.back_top_frames();ylo=min(bb(s)[1] for s in [split,reg])-15;yhi=max(bb(s)[4] for s in [split,reg])+15;zlo=min(bb(s)[2] for s in [split,reg])-15;ztop=E.back_top_ceiling_face()
base=E._ybox(-E.appliance_width/2,roots[0],ylo,yhi,zlo,ztop)
base=base.fuse(E._ybox(-E.appliance_width/2,-60,ylo,yhi,ztop,ztop+E.ceiling_skin))
def anchors(stock):return E._tube_anchors(stock,roots,lane,stations,ylo,yhi,zlo,ztop+E.ceiling_skin,up=-1)
ordinary=anchors(base);fixture=anchors(E._flank_body_pockets(base,pockets));protruding=ordinary.cut(base)
report={'status':'in_progress','source_sha256':sources,'frames_sha256':sha(PACK/'frames.json'),'scope':'Fresh current placement and complete native local wall/ceiling/anchor fixture; no full producer or native slice.','placement':{'split_bounds_mm':bb(split),'regulator_bounds_mm':bb(reg),'FLOWREG_TURN':A.FLOWREG_TURN,'FLAVOR_STEP':A.FLAVOR_STEP},'pockets':pockets,'anchors':[],'fixture_valid':fixture.isValid(),'fixture_solids':len(fixture.Solids()),'complete_protruding_anchor_stock_missing_mm3':vol(protruding.cut(fixture)),'body_checks':{},'checks':[]}
for name,(s,_c) in placed.items():report['body_checks'][name]={'wall_and_anchor_overlap_mm3':vol(s.intersect(fixture)),'wall_and_anchor_air_mm':s.distance(fixture)}
for (name,_section,_root,_piece),st in zip([r for r in A.BODY_ANCHOR_SITES if r[0] in placed],stations):
 mid,u,n,r,*_=st;reach=r+E.wall
 # _tube_anchors backs a shallow channel only as far as the nominal wall plane.
 bface=mid[0]-roots[0];blane=mid[0]-lane[0]
 relief=bface<blane-1e-9 and bface-reach<E.tie_t
 broot=blane if relief else bface
 cavdepth=min(E.tube_anchor_cavity_depth+E.fits.supported_surface,broot-reach)
 cavity_mid_b=reach+cavdepth/2
 # A 2.5 x1 mm tail crosses the complete vertical mouth, including both exits.
 tie=E._ybox(mid[0]-cavity_mid_b-E.tie_t/2,mid[0]-cavity_mid_b+E.tie_t/2,
             mid[1]-E.tie_w/2,mid[1]+E.tie_w/2,mid[2]-reach-2,mid[2]+reach+2)
 skin=E._ybox(-E.appliance_width/2+.01,lane[0]-.01,mid[1]-E.tie_w/2,mid[1]+E.tie_w/2,mid[2]-reach,mid[2]+reach)
 tie_overlap=vol(tie.intersect(fixture));body_overlap=vol(tie.intersect(placed[name][0]))
 row={'name':name,'station':st,'complete_length_mm':E.tube_anchor_len,'web_thickness_mm':E.wall,'end_web_length_mm':E.tie_cav_wall,'tie_width_mm':E.tie_w,'tie_thickness_mm':E.tie_t,'tie_cavity_width_mm':E.tie_cav_w,'tie_cavity_depth_mm':cavdepth,'side_air_mm_each':(E.tie_cav_w-E.tie_w)/2,'depth_air_mm_total':cavdepth-E.tie_t,'threading_corridor_bounds_mm':bb(tie),'threading_corridor_print_overlap_mm3':tie_overlap,'threading_corridor_hardware_overlap_mm3':body_overlap,'nominal_wall_probe_missing_mm3':vol(skin.cut(fixture)),'nominal_outer_backing_mm':E.wall,'worst_groove_remaining_skin_mm':E.wall-E.flute_depth,'minimum_tie_loop_mm':E.tube_anchor_tie_loop(r),'end_forms':A.BODY_ANCHOR_END_FORMS[name],'actual_column_bounds_mm':E.tube_anchor_end_columns(st,roots,lane,-1,ztop) if A.BODY_ANCHOR_END_FORMS[name]==('column','column') else [None,None]}
 # A closed 1 mm-thick witness band with concentric rounded corners,
 # through the retained passage and around the actual fitting. Its 2.5 mm
 # axial width is the specified tie; the witness has 0.5 mm rib-corner air and 0.25 mm bore air.
 w=reach+.5;front=-r-.25;back=reach+.5
 origin=tuple(mid[k]-u[k]*E.tie_w/2 for k in range(3))
 outside=E._anchor_rib(origin,u,n,E.tie_w,w+E.tie_t,front-E.tie_t,back+E.tie_t)
 outside=cq.Workplane(obj=outside).edges('|Y').fillet(1.5).val()
 inside_origin=tuple(origin[k]-u[k] for k in range(3))
 inside=E._anchor_rib(inside_origin,u,n,E.tie_w+2,w,front,back)
 inside=cq.Workplane(obj=inside).edges('|Y').fillet(.5).val()
 loop=outside.cut(inside)
 loop_checks={other:{'overlap_mm3':vol(loop.intersect(body)),'air_mm':loop.distance(body)} for other,body in [('printed_fixture',fixture),('funnel',funnel),*[(k,v[0]) for k,v in placed.items()]]}
 row['closed_tie_witness']={'width_mm':E.tie_w,'thickness_mm':E.tie_t,'band_length_mm':vol(loop)/(E.tie_w*E.tie_t),'inner_corner_radius_mm':.5,'outer_corner_radius_mm':1.5,'valid':loop.isValid(),'body_count':len(loop.Solids()),'bounds_mm':bb(loop),'native_checks':loop_checks,'scope':'A continuous rounded closed band proves an available loop; tightening force and minimum physical bend radius remain unmeasured.'}
 loop.exportBrep(str(HERE/(name+'-tie-witness.brep')))
 report['checks'].append({'name':name+' closed tie loop','pass':loop.isValid() and len(loop.Solids())==1 and all(v['overlap_mm3']<1e-6 for v in loop_checks.values())})
 report['anchors'].append(row)
 report['checks'] += [{'name':name+' full native backing','pass':row['nominal_wall_probe_missing_mm3']<1e-6},{'name':name+' full-width tie threading','pass':tie_overlap<1e-6 and body_overlap<1e-6 and cavdepth>=E.tie_t}]
for pocket in pockets:
 name,x0,x1,*_=pocket
 report.setdefault('pocket_stock',[]).append({'name':name,'depth_mm':x1-x0,'native_outer_stock_mm':x0+E.appliance_width/2,'worst_groove_stock_mm':x0+E.appliance_width/2-E.flute_depth})
report['checks'] += [{'name':'all complete anchors preserved','pass':report['complete_protruding_anchor_stock_missing_mm3']<1e-6},{'name':'one valid attached fixture','pass':fixture.isValid() and len(fixture.Solids())==1},{'name':'placed body clearances','pass':all(v['wall_and_anchor_overlap_mm3']<1e-6 for v in report['body_checks'].values())}]
report['support_access']={'orientation':'Back-top ceiling-down, machine -Z up.','pocket_return':'45 degree lower return; native pocket cut precedes complete anchor fuses.','anchor_seats':'Half-round seats open toward +X into the empty enclosure; detach interfaces and withdraw through that open face before fittings and zip ties are installed.','tie_channel':'The quantified 2.5 x1 mm threading probe traverses each central channel through its upper and lower mouths. This is a tie threading reading, not proof that a whole support tree exits intact.','actual_support_topology':'Requires the production slice of the regenerated complete back-top; no support-road count or cleanup effort is claimed here.'}
report['input_drift']=[p for p,h in sources.items() if sha(Path(p) if Path(p).is_absolute() else ROOT/p)!=h];report['elapsed_seconds']=time.monotonic()-start;report['status']='local_wall_anchor_pass' if all(c['pass'] for c in report['checks']) and not report['input_drift'] else 'local_wall_anchor_fail'
fixture.exportBrep(str(HERE/'wall-fixture.brep'))
for name,(shape,_carry) in placed.items():shape.exportBrep(str(HERE/(name+'.brep')))
report['reference_limit']='Flow-regulator reference is the existing provisional catalogue-photo envelope; this reading verifies its current placed model, not new caliper or scan evidence.'
report['reproducer_sha256']=sha(Path(__file__))
archive=OUT/'split-regulator-wall-inputs.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for path in sorted(HERE.glob('*.brep')):z.write(path,'native/'+path.name)
 z.write(funnel_path,'native/funnel.brep')
 z.write(PACK/'frames.json','inputs/frames.json')
 z.write(Path(__file__),'reproducer/verify_split_regulator_wall.py')
 for name,digest in sources.items():
  path=Path(name) if Path(name).is_absolute() else ROOT/name
  if path.suffix=='.py' and sha(path)==digest:z.write(path,'sources/'+str(path.relative_to(ROOT)))
 z.writestr('native-sha256.json',json.dumps({p.name:sha(p) for p in sorted(HERE.glob('*.brep'))}|{'funnel.brep':sha(funnel_path)},indent=2)+'\n')
 z.writestr('reading.json',json.dumps(report,indent=2)+'\n')
report['retained_inputs']={'path':str(archive.relative_to(ROOT)),'sha256':sha(archive)}
(OUT/'split-regulator-wall-check.json').write_text(json.dumps(report,indent=2)+'\n')
(HERE/'wall-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':report['checks'],'elapsed_seconds':report['elapsed_seconds'],'input_drift':report['input_drift'],'retained_inputs':report['retained_inputs']},indent=2),flush=True)
