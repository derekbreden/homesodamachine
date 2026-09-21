"""Bounded source routes checked against retained native integration geometry.

The archive deliberately separates the retained frame capture, the lowered inner
manifold solids and the fresh cap lid. Full regenerated shell fit is a separate gate.
"""
from pathlib import Path
import os,sys,json,hashlib,tempfile,zipfile,argparse
os.environ['HSM_NO_BUILD_LOCK']='1'
HERE=Path(__file__).resolve().parent;root=HERE.parents[4]
parser=argparse.ArgumentParser(description='Recheck source-authored routes against the explicitly retained native integration inputs.')
parser.add_argument('--output',type=Path,default=HERE/'corrected-route-check.json')
args=parser.parse_args()
archive=HERE/'corrected-route-inputs.zip'
workspace=tempfile.TemporaryDirectory(prefix='hsm-corrected-routes-');bundle=Path(workspace.name)
with zipfile.ZipFile(archive) as z:z.extractall(bundle)
for name,digest in json.loads((bundle/'manifest.json').read_text()).items():
 if hashlib.sha256((bundle/name).read_bytes()).hexdigest()!=digest:raise ValueError('Retained native input hash mismatch: '+name)
cache=bundle/'route-pack'
sys.path[:0]=[str(root/'hardware/manifold-layout'),str(root/'hardware/scripts')]
import cadquery as cq
import enclosure_assembly as ea
L=ea._lines;R=ea._routing
import _clearing as C, _boxes, _overlap
records=json.loads((cache/'frames.json').read_text());solids={n:cq.Shape.importBrep(str(cache/r['brep'])) for n,r in records.items()}
F={n:R.frame(n,solids[n],r['ports']) for n,r in records.items() if 'ports' in r}
extra=cache.parent/'route-neighbors';er=json.loads((extra/'neighbors.json').read_text())['placed']
solids.update({n:cq.Shape.importBrep(str(extra/v['brep'])) for n,v in er.items()})
inner=bundle/'inner-limb'
for n in json.loads((inner/'probe.json').read_text())['affected']:
 solids[n]=cq.Shape.importBrep(str(inner/(n+'.brep')))
 if n in F:
  F[n]=R.frame(n,solids[n],{k:([p[0],p[1],p[2]-1.5],v,d) for k,(p,v,d) in records[n]['ports'].items()})
for n in ('stub-fluid-2','stub-fluid-4'):solids.pop(n,None)
# Build the source-owned split and regulator with their actual placement functions.
source_out=records['asse1022-assembly']['ports']['tube-out']
split,split_carry=ea.build_split(lambda station:(source_out[0],source_out[1]))
reg,reg_carry=ea.build_flowreg(split_carry)
for n,obj,carry in [('water-split',split,split_carry),('flow-regulator',reg,reg_carry)]:
 solids[n]=obj;ports={}
 for key,(station,d) in L.STATIONS[n].items():
  p,axis=carry(station());ports[key]=(p,axis,d)
 F[n]=R.frame(n,obj,ports)
n='bulkhead-flavor-b';solids[n]=solids[n].translate((0,0,-1.55));F[n]=R.frame(n,solids[n],{k:([p[0],p[1],p[2]-1.55],v,d) for k,(p,v,d) in records[n]['ports'].items()})
# Preserve the fully qualified corrected cap as an independent native obstacle.
solids['current-cap-lid']=cq.Shape.importBrep(str(bundle/'cap-lid.brep'))
L.frames=lambda *_:F
R.BLOCKED.clear();runs=L.build_runs(solids,{})
tubes={r.id:R.tube(r) for r in runs}
selected={'water-2','water-3','fluid-1','fluid-2','fluid-16','fluid-24','fluid-28'}
report={'scope':'Current source authored pack routes against corrected fixed inner bodies, exact source split/regulator, lowered Flavor-B and corrected cap lid. Canonical full regenerated shell clearance remains separate.','sources':{str(Path(m.__file__).relative_to(root)):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (ea,L,ea._enc._interface,L._cc)},'routes':[],'blocked':R.BLOCKED}
for r in runs:
 if r.id not in selected:continue
 t=tubes[r.id];bb=_boxes.loose(t);near=[]
 for n,s in {**solids,**{'tube-'+n:t for n,t in tubes.items() if n!=r.id}}.items():
  if n.startswith('stub-') or n in {r.frm.split('.')[0],r.to.split('.')[0]}:continue
  if n=='foam-assembly':continue # cap reconstruction and canonical aggregate are separate
  if C.box_gap(bb,_boxes.loose(s))>=2:continue
  gap=C.gap(t,s,2.)
  if gap<2:
   near.append({'name':n,'air_mm':gap,'native_air_mm':t.distance(s),'native_overlap_mm3':t.intersect(s).Volume(),'required_air_mm':0.0 if (r.id=='water-3' and n=='current-cap-lid') else 1.0,'seat_scope':'Purpose-built water3 cap bearing; free first bend checked separately' if (r.id=='water-3' and n=='current-cap-lid') else None})
 skew=R.leg_skew(r.pts[0],r.pts[1],F[r.frm.split('.')[0]].normal(r.frm.split('.')[1]))
 row={'id':r.id,'pts':r.pts,'minimum_radius_mm':r.tightest,'exit_skew_degrees':skew,'near':near,'native_valid':t.isValid(),'pass':r.tightest>=14-1e-6 and not R.BLOCKED.get(r.id) and all(x['air_mm']>=x['required_air_mm']-1e-6 and x['native_overlap_mm3']<1e-6 for x in near)}
 report['routes'].append(row);print(json.dumps(row),flush=True)
if 'water-3' in tubes:
 free=tubes['water-3'].intersect(cq.Solid.makeBox(100.,250.,150.,cq.Vector(-130.,190.,220.)))
 report['water3_free_bend_foam_air_mm']=C.gap(free,solids['foam-assembly'],4.)
 report['split_free_lead']=C.cast(F['water-split'].at('to-vk'),F['water-split'].normal('to-vk'),6.35,40.,solids,skip=('water-split','stub-water-3'))
report['flowreg_funnel_air_mm']=reg.distance(solids['funnel'])
report['all_pass']=all(r['pass'] for r in report['routes']) and not report['blocked'] and report['water3_free_bend_foam_air_mm']>=1 and report['split_free_lead'][1]>=17.175 and report['flowreg_funnel_air_mm']>=1
report['input_archive']=str(archive.relative_to(root));report['input_archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest();report['reproducer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
out=args.output;out.write_text(json.dumps(report,indent=2)+'\n')
print('ALL PASS',report['all_pass'],flush=True)
raise SystemExit(0 if report['all_pass'] else 1)
