"""Finite proxy/vessel screen for the correlated local working subset.

Distance is an analytic capped-cylinder signed distance evaluated on a refined
surface mesh. The receipt subtracts the maximum triangle edge and tessellation
allowance, giving a conservative sampled-surface lower bound. It is a proxy
screen, not physical-gun or swept-path acceptance.
"""
import importlib.util
import json
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'hardware/printed-parts/fixtures/gun-positioner'
s=importlib.util.spec_from_file_location('gp',OUT/'gun_positioner.py');gp=importlib.util.module_from_spec(s);s.loader.exec_module(gp)
gp.init_parts()
# Fixed gun solid excludes the intended contacting consumable wire.
g=gp.box(135,34,34).translate((14.5,0,30.35))
for diameter,length,x in((24,18,82),(11,46,100),(17,31,146)):
 g=g.union(gp.cylinder(diameter,length).rotate((0,0,0),(0,1,0),90).translate((x,0,47.35)))
g=g.union(gp.box(35,28,95).translate((-36,0,-64.65)))
v,f=g.val().tessellate(.10,.12);v=np.array([p.toTuple() for p in v]);f=np.array(f)
v,f=trimesh.remesh.subdivide_to_size(v,f,max_edge=1.0,max_iter=10)
edge=max(np.linalg.norm(v[f[:,i]]-v[f[:,(i+1)%3]],axis=1).max() for i in range(3))
# Include face centers as an additional screen; the edge bound remains valid.
v=np.vstack((v,v[f].mean(axis=1)));relative=v-gp.TOOL
radius=63.5;bottom=132.35;top=284.75;mid=(top+bottom)/2;half=(top-bottom)/2
minimum=1e9;worst=None;poses=0
for yaw in(-5,0,5):
 for pitch in(-10,-5,0,5,10):
  for roll in(-5,0,5):
   R=gp.rotation('z',105+yaw)@gp.rotation('y',60+pitch)@gp.rotation('x',roll)
   neutral=relative@R.T+gp.DOT
   for dx in(-.25,.25):
    for dy in(-.25,.25):
     for dz in(-.25,.25):
      points=neutral+np.array([dx,dy,dz]);q=np.column_stack((np.linalg.norm(points[:,:2],axis=1)-radius,np.abs(points[:,2]-mid)-half))
      distances=np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(np.maximum(q[:,0],q[:,1]),0)
      value=float(distances.min());poses+=1
      if value<minimum:minimum=value;worst={'yaw_deg':yaw,'pitch_deg':pitch,'roll_deg':roll,'endpoint_offset_mm':[dx,dy,dz],'surface_point_mm':points[np.argmin(distances)].tolist()}
record={'status':'Finite correlated-pose proxy screen, not continuous sweep or physical-gun acceptance.','checked_angle_grid_deg':{'yaw':[-5,0,5],'pitch':[-10,-5,0,5,10],'roll':[-5,0,5]},'endpoint_offset_corner_mm':[-.25,.25],'poses_checked':poses,'gun_surface_sample_points':len(v),'mesh_maximum_edge_mm':float(edge),'tessellation_allowance_mm':.10,'minimum_sampled_proxy_vessel_distance_mm':minimum,'conservative_sampled_surface_lower_bound_mm':minimum-edge-.10,'worst_sample':worst,'vessel_envelope':{'axis':'world Z','radius_mm':radius,'bottom_z_mm':bottom,'top_z_mm':top},'excluded_collision_pairs':['Consumable wire X177..200 versus seam: intended contact; endpoint must be observed.','Gun versus its own TPU pads and jaws: intended clamped contact.'],'checked_collision_pairs':['Gun body/nozzle/handle proxy versus conservative complete127 mm vessel cylinder.'],'limitations':['The gun is an unscanned dimensional proxy, not vendor CAD. Actual gun shell, protruding wire, clamps, released tray, all mechanism bodies, lenses, camera stages and cables require a physical static sweep.','Angles between grid samples are not cleared by this finite test. Full independent XYZ and angular travel contains collision poses; tube is absent for unrestricted dry commissioning.','The actual seam is at inner wall radius61.85 mm; the complete63.5 mm outer vessel cylinder is deliberately conservative for solid gun clearance.']}
(OUT/'working-subset-clearance.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
