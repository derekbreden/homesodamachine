"""Continuous fore power-wire band beneath the H/N/G working halves.

Retain west root stock from Y343.7 aft, all3mm blank-half grips and the unchanged device
poses. The subtracted host is an exact subset of the checked closed-body host.
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'.cache/pump-first-layout/mounts/roof'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(s):
 b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def main():
 manifest=HERE/'roof-candidate.json';m=json.loads(manifest.read_text());record=m['parts']['west-junction-platform'];input_path=ROOT/record['brep'];original=cq.Shape.importBrep(str(input_path))
 lift=m.get('high_junction_lift_mm',0.);floor=332.75+lift
 cutter=cq.Solid.makeBox(69.61,12.3,3.02,cq.Vector(-99.51,331.4,floor-.01));host=original.cut(cutter,tol=.0001).clean()
 shell=cq.Shape.importBrep(str(ROOT/'.cache/pump-first-layout/mounts/enclosure-back-top.brep'));joined=shell.fuse(host,tol=.0001).clean()
 retained=cq.Solid.makeBox(3.5,70.9,3,cq.Vector(-99.5,343.7,floor));grip=cq.Solid.makeBox(80,15,15,cq.Vector(-100,343.7,floor))
 checks=[{'test':'subtracted native host valid and single solid','valid':host.isValid(),'solids':len(host.Solids()),'pass_result':host.isValid() and len(host.Solids())==1},
 {'test':'host remains subset of checked occupied geometry','added_mm3':host.cut(original).Volume(),'pass_result':abs(host.cut(original).Volume())<.001},
 {'test':'complete3.5mm west root strip from Y343.7 aft retained','removed_mm3':original.intersect(retained).cut(host).Volume(),'pass_result':abs(original.intersect(retained).cut(host).Volume())<.001},
 {'test':'blank-half grip stock fromY343.7 retained','removed_mm3':original.intersect(grip).cut(host).Volume(),'pass_result':abs(original.intersect(grip).cut(host).Volume())<.001},
 {'test':'printed platform remains joined to actual wall','valid':joined.isValid(),'solids':len(joined.Solids()),'root_common_mm3':host.intersect(shell).Volume(),'pass_result':joined.isValid() and len(joined.Solids())==1}]
 result={'checks':checks,'pass_result':all(c['pass_result'] for c in checks),'removed_stock_mm3':original.cut(host).Volume(),'continuous_band_mm':[-99.5,331.4,floor,-29.9,343.7,floor+3],'input_sha256':digest(input_path),'scope':'Native continuous wire-fanout clearance open through the west edge. The complete stock is a subset of the previous no-interference host; printed strength and formed wire/termination retention remain unqualified.'}
 assert result['pass_result'],checks
 path=OUT/'west-junction-platform-power-channel.brep';host.exportBrep(str(path));v,t=host.tessellate(.12,.08);mesh=path.with_suffix('.json');mesh.write_text(json.dumps({'vertices':[[p.x,p.y,p.z] for p in v],'triangles':[list(p) for p in t]},separators=(',',':'))+'\n')
 m['parts']['west-junction-platform']={**record,'brep':str(path.relative_to(ROOT)),'mesh':str(mesh.relative_to(ROOT)),'sha256':digest(path),'bounds':bounds(host),'detail':record['detail']+' Continuous H/N/G fore floor opening through the west edge permits full power-wire fanout at Z333.25 while retaining the west root from Y343.7 aft and all blank-half grips.'}
 m['continuous_power_band']=result;m['checks']+=checks;m['source_sha256'][str(Path(__file__).relative_to(ROOT))]=digest(Path(__file__));manifest.write_text(json.dumps(m,indent=2)+'\n');(HERE/'power-channel-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
