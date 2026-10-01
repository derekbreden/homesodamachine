"""Verify accepted physical interfaces in the complete upper shell solids."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
import numpy as np
import trimesh
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir());ENC=HERE.parent
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ENC),str(ROOT/'hardware/manifold-layout')]
import enclosure as e,_box_spec
import _display_wing_interface as dw
import _nameplate_wing_interface as nw
import enclosure_assembly as assembly
rows=[]
def check(name,value,**data):
 rows.append({'check':name,'pass':bool(value),**data});print(name,value,data,flush=True)
 if not value:raise ValueError(name)
def empty(name,a,b):
 volume=abs(a.intersect(b).Volume());check(name,volume<1e-5,overlap_mm3=volume)
def equal(name,a,b):
 delta=abs(a.cut(b).Volume())+abs(b.cut(a).Volume());check(name,delta<1e-5,delta_mm3=delta)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 box,_=_box_spec.read(e.Box,e.Bound,(e.Pack,e.PortField,e.Nameplate),path=HERE/'enclosure-box.json')
 shapes={name:cq.importers.importStep(str(ENC/f'enclosure-{name}.step')).val() for name in ('front-top','back-top')}
 front,back=shapes.values()
 display_dir=ENC.parent/'display-cover/face-up-trial'
 name_dir=ENC.parent/'nameplate/horizontal-wing-trial'
 cover=cq.importers.importStep(str(display_dir/'display-cover-flat-wings.step')).val()
 main_cover=cq.importers.importStep(str(ENC.parent/'display-cover/display-cover.step')).val()
 equal('display cover equals accepted physical cover',main_cover,cover)
 np_saved=cq.importers.importStep(str(name_dir/'nameplate-horizontal-wings-001.step')).val()
 np_main=cq.importers.importStep(str(ENC.parent/'nameplate/nameplate-001.step')).val()
 equal('nameplate equals accepted physical part including artwork',np_main,np_saved)
 coupon=cq.importers.importStep(str(name_dir/'nameplate-horizontal-wings-receiver.step')).val()
 equal('nameplate receiver cutter equals accepted receiver',nw.receiver(),coupon)
 p=e.display_plane(box.outer);loc=cq.Location(p)
 seated=cover.moved(loc);empty('display cover seated in full front-top',seated,front)
 for axis,limits in ((0,(-.3,.3)),(1,(-.15,.15)),(2,(0,.6))):
  for v in limits:
   vec=[0,0,0];vec[axis]=v
   empty(f'display cover axis {axis} at {v}',cover.translate(vec).moved(loc),front)
 # The accepted cover must still be caught at either lateral limit.
 for x in (-.3,0,.3):
  clash=cover.translate((x,0,.65)).moved(loc).intersect(front).Volume()
  check(f'display capture at X {x}',clash>1,overlap_mm3=clash)
 floor=box.outer[3]-nw.THICK
 station=box.pack.nameplate
 np_loc=(station.x,floor,station.z)
 empty('nameplate seated in full back-top',np_saved.translate(np_loc),back)
 for axis,limits in ((0,(-.15,.15)),(1,(0,.45)),(2,(-.4,.15))):
  for v in limits:
   vec=list(np_loc);vec[axis]+=v
   empty(f'nameplate axis {axis} at {v}',np_saved.translate(vec),back)
 room=e._ybox(-108,108,4,472,box.pump_bay[2]+.02,356)
 for i,void in enumerate(dw.support_exits(250,inset=.05,roof_drop=.02)):
  empty(f'wing {i} support exit through display storey',void.moved(loc).intersect(room),front)
 module=assembly.build_display(box)
 empty('complete deeper display module clears front-top',module,front)
 funnel,_=assembly.build_funnel(box)
 empty('complete deeper display module clears funnel',module,funnel)
 jack=assembly._pump_jack_service_bound(module,cq.Workplane(obj=front),box)
 check('pump-jack service path',jack.ok,reading=jack._asdict())
 # A local interface edit may not silently change the accepted tee mechanism or seams.
 previous=ROOT/'.cache/enclosure-accepted-integration/before'
 oldfront=cq.importers.importStep(str(previous/'enclosure-front-top.step')).val()
 oldback=cq.importers.importStep(str(previous/'enclosure-back-top.step')).val()
 lower=e._ybox(-108,108,4,472,159,box.pump_bay[2]-.001)
 equal('front-top below display storey unchanged',front.intersect(lower),oldfront.intersect(lower))
 region=e._ybox(station.x-59,station.x+59,box.outer[3]-16,box.outer[3]+1,station.z-25,station.z+25)
 equal('back-top outside nameplate receiver unchanged',back.cut(region),oldback.cut(region))
 # These local interfaces do not move placement stations. Check the affected
 # hardware directly with its production placement functions.
 previous_box,_=_box_spec.read(e.Box,e.Bound,(e.Pack,e.PortField,e.Nameplate),
                              path=ROOT/'hardware/manifold-layout/enclosure-box.json')
 check('production enclosure datums retained',previous_box.outer==box.outer and previous_box.inner==box.inner
       and previous_box.y_joint==box.y_joint and previous_box.splits==box.splits,
       outer=box.outer,splits=box.splits)
 foam,_=assembly.build_foam(0)
 psu,_=assembly.build_psu(foam,assembly.east_wall_seat())
 r=nw.production_backing(nw.receiver(),nw.dimensions.station(0,0),nw.THICK).translate(np_loc)
 empty('nameplate receiver clears PSU',r,psu)
 empty('full back-top clears PSU',back,psu)
 gap=assembly._clearing.gap(r,psu,5)
 check('nameplate receiver retains required PSU clearance',gap>=assembly.NAMEPLATE_PSU_CLEAR-1e-6,
       measured_mm=gap,required_mm=assembly.NAMEPLATE_PSU_CLEAR,
       local_backing_mm=nw.EAST_BACKING)
 for name,s in shapes.items():
  path=ENC/f'enclosure-{name}.stl';m=trimesh.load_mesh(path)
  check(name+' solid and mesh',s.isValid() and len(s.Solids())==1 and m.is_watertight and m.is_winding_consistent,
        facets=len(m.faces),bounds=m.bounds.tolist())
 # The roof show curves that vary with print Z, measured on the STEP.
 round_faces=[]
 for face in front.Faces():
  b=face.BoundingBox()
  if face.geomType() not in ('PLANE','CYLINDER') and b.zmax>352 and b.zmin>340:
   round_faces.append({'type':face.geomType(),'bounds':[b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]})
 (HERE/'geometry-check.json').write_text(json.dumps({'pass':True,'checks':rows,
    'front_roof_blend_faces':round_faces,
    'accepted_clearances_preserved':True,'pcb_opening_depth_mm':e.display_facet_thickness+e.display_pcb_cut_through,
    'module_rear_clearance_mm':1.,'minimum_ridge_stock_mm':e.ridge_wall_t,
    'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ENC/'enclosure.py',ENC/'_display_wing_interface.py',ENC/'_nameplate_wing_interface.py',HERE/'enclosure-box.json',
            *[ENC/f'enclosure-{n}{ext}' for n in shapes for ext in ('.step','.stl')]]}},indent=2)+'\n')

if __name__=='__main__':main()
