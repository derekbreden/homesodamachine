"""Sample installed and selected native wet-ramp normals; no draining claim."""
from pathlib import Path
import json,math,sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts/_cadq_export.py').exists())
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/zone-c/funnel')]
import funnel as f
from OCP.BRepGProp import BRepGProp_Face
from OCP.gp import gp_Pnt,gp_Vec
rows=[]
for extra in (0,60):
 d=f.collar_d+extra-12
 ramp=f._loft_rc(153,d,0,0,6-f.chute_h,3,f.neck_dx,-extra/2,
                 6-f.chute_h-f._ramp_rise,f.mouth_corner_r)
 samples=[]
 for face in ramp.Faces():
  if face.geomType()=='PLANE': continue
  g=BRepGProp_Face(face.wrapped)
  u0,u1,v0,v1=face._uvBounds()
  for i in range(1,40):
   for j in range(1,20):
    u=u0+(u1-u0)*i/40;v=v0+(v1-v0)*j/20
    p=gp_Pnt();n=gp_Vec();g.Normal(u,v,p,n)
    grade=math.degrees(math.atan2(math.hypot(n.X(),n.Y()),abs(n.Z())))
    samples.append((grade,p.X(),p.Y(),p.Z()))
 low=min(samples)
 assert low[0]>0
 row=dict(aft_extension_mm=extra,samples=len(samples),minimum_sampled_ramp_grade_deg=low[0],
   minimum_sample_local_xyz_mm=list(low[1:]),
   method='Native surface normal samples on the loft side faces at 39×19 interior UV stations per face. Horizontal end caps excluded.',
   scope='This is a sampled geometric slope, not a measured complete-draining result or minimum continuous surface proof.')
 rows.append(row);print(extra,row['minimum_sampled_ramp_grade_deg'],flush=True)
(Path(__file__).parent/'ramp-grade.json').write_text(json.dumps({'rows':rows},indent=2)+'\n')
