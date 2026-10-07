"""Emit native matching interfaces and query occupied stock before the cavity is subtracted."""
from pathlib import Path
import hashlib,json,sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts/_cadq_export.py').exists())
HERE=Path(__file__).parent
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/zone-c/funnel'),str(HERE.parent)]
import cadquery as cq
import funnel as f,funnel_frame as ff
import baseline
from study_configuration import configuration,save_record
extra,preview,candidate=configuration()
f.collar_d+=extra;f.neck_dy=-extra/2
cy=ff.center_y+extra/2;ff.center_y=cy;ff.depth=f.collar_d+24.6;ff.corbel_foot_half_depth+=extra/2
import enclosure as e
OUT=ROOT/'.cache/pump-first-layout/funnel'/f'aft-{extra:g}'/'mating';OUT.mkdir(parents=True,exist_ok=True)
inner=(-104.5,104.5,14,468.3,0,352);outer=(-107.5,107.5,5,471.3,-6,355)
raw=ff.body_blank((0,cy),349,inner=inner,y_joint=200)
shapes={
 'frame-blank':raw,
 'frame-shell-clearance':ff.shell_clearance((0,cy),349,inner,200),
 'front-roof-clearance':ff.front_roof_clearance(inner,(0,cy),349,200),
 'front-seam-relief':ff.front_seam_relief(outer,200,(0,cy),349),
 'front-receivers':ff.receivers(inner,outer,200,(0,cy),349,'front'),
 'back-receivers':ff.receivers(inner,outer,200,(0,cy),349,'back'),
 'front-rail-channels':e._z_rail_channels(inner,200,306.9,'front',None,runs=ff.rail_runs(inner,200,'front',(0,cy))),
 'back-rail-channels':e._z_rail_channels(inner,200,306.9,'back',None,runs=ff.rail_runs(inner,200,'back',(0,cy))),
 'brim-pocket':f._rounded_box(f.collar_w+2*(f.brim_overhang+.25),f.collar_d+2*(f.brim_overhang+.25),f.brim_corner_r+.25,349,356,0,cy),
 'collar-throat':f._rounded_box(f.collar_w+.5,f.collar_d+.5,f.collar_corner_r+.25,348,349.01,0,cy),
}
records={}
for n,s in shapes.items():
 path=OUT/f'{n}.brep';s.exportBrep(str(path));b=s.BoundingBox()
 records[n]={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'bounds_world_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]}
reads=[]
installed=baseline.read(names=['asse1022-assembly','coil-v-a','coil-v-b','valve-v-a','valve-v-b'])
for name,solid in installed.items():
 if name=='asse1022-assembly':continue
 overlap=solid.intersect(raw).Volume(tol=1e-9)
 reads.append({'name':name,'reference':'full frame blank before subtracting funnel clearance',
  'overlap_mm3':overlap,'distance_mm':raw.distance(solid)})
for y,z in [(331,280.2),(334,277.2)]:
 shift=(361.51,y+78.07,z-307.21058083755)
 solid=installed['asse1022-assembly'].rotate((0,0,0),(0,0,1),90).translate(shift)
 overlap=solid.intersect(raw).Volume(tol=1e-9)
 gap=raw.distance(solid)
 reads.append({'name':f'asse-at-Y{y:g}-vent-Z{z:g}','transform':{'yaw_deg':90,'translation_mm':list(shift)},
  'reference':'full frame blank before subtracting funnel clearance; zero common proves clearance from its contained final body',
  'overlap_mm3':overlap,'distance_mm':gap})
 print(reads[-1],flush=True)
save_record('mating',extra,preview,{'aft_extension_mm':extra,'interfaces':records,'blank_stock_reads':reads,
 'scope':'Native matching receiver/channel/cutter interfaces, plus full-blank bounds. Positive blank overlap alone cannot establish a final frame collision after carving. A strictly positive gap from the blank proves gap from the final body, except rail heads outside ASSE X.'})
