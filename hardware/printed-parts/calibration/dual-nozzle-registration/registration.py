"""Coplanar black/white alignment ladders for a documented residual XY correction."""
import hashlib,json,sys
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path[:0]=[str(ROOT/'hardware/scripts')]
from _cadq_export import export_assembly,export_step,_write_mesh_payload,_per_solid_color
NAME='dual-nozzle-registration'
BASE=.96;TOP=1.44
OFFSETS={'X':[round(-1.05+.05*i,2) for i in range(15)],
         'Y':[round(.35+.05*i,2) for i in range(15)]}
PITCH=7.0

def block(x0,x1,y0,y1,z0,z1):
 return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def build():
 black=block(-55,55,-19,20,0,BASE);white=[];rows=[]
 for i,(dx,dy) in enumerate(zip(OFFSETS['X'],OFFSETS['Y'])):
  x=(i-7)*PITCH
  black=black.fuse(block(x-.45,x+.45,10.8,14.2,BASE,TOP),
                   block(x-3,x-.4,-5.45,-4.55,BASE,TOP))
  white.extend((block(x+dx-.45,x+dx+.45,6.4,9.8,BASE,TOP),
                block(x+.4,x+3,-5+dy-.45,-5+dy+.45,BASE,TOP)))
  for y in (17,-10):
   label=(cq.Workplane('XY',origin=(x,y,BASE)).text(str(i),2.6,TOP-BASE,font='Helvetica',halign='center',valign='center',combine=False).val())
   black=black.fuse(label)
  rows.append({'index':i,'candidate_white_correction_mm':{'X':dx,'Y':dy},'x_station_mm':x})
 for text,x,y in [('X',-51,2),('Y',-51,-15)]:
  label=cq.Workplane('XY',origin=(x,y,BASE)).text(text,3,TOP-BASE,font='Helvetica',combine=False).val()
  black=black.fuse(label)
 return black.clean(),cq.Compound.makeCompound(white),rows

def main():
 black,white,rows=build();physical=black.fuse(*white.Solids()).clean()
 assert black.isValid() and white.isValid() and physical.isValid() and len(physical.Solids())==1
 assert black.intersect(white).Volume()<1e-6
 assembly=cq.Assembly();assembly.add(black,name=NAME,color=cq.Color(.10,.11,.12));assembly.add(white,name=NAME+'-white',color=cq.Color(.95,.95,.93))
 path=HERE/(NAME+'.step');export_assembly(assembly,str(path));export_step(physical,str(path.with_suffix('.stl')));_write_mesh_payload(path,_per_solid_color(assembly))
 report={'pass':True,'purpose':'Measure the residual relative displacement of the two nozzles using coplanar black/white line pairs.','printer':'Mark2','material':'Black and white PET-GF','nozzle_pair_mm':[.4,.4],'base_mm':BASE,'top_mm':TOP,'pair_top_surfaces_coplanar':True,'candidate_spacing_mm':.05,'candidates':rows,'reading':'Choose the index whose black and white lines align in each row. X row corrects printer X; Y row corrects printer Y. Selected candidate is the correction to apply to white, not the measured error. Adjacent indices tie: report both.','applied_job_correction_mm':[0,0],'normal_nozzle_offset_calibration':'Usual Auto launch option; no touchscreen-managed calibration is required.','qualification':'A measured correction requires a second zero-residual validation print before use on product parts. The coupon only identifies relative error; it does not identify which physical nozzle is wrong.','source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),path,path.with_suffix('.stl'))}}
 (HERE/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
