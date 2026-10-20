from pathlib import Path
from collections import defaultdict
import sys,json,re,hashlib
import numpy as np
import trimesh
from shapely.geometry import LineString,Point,box
from shapely.ops import unary_union
root=Path.cwd();sys.path.insert(0,str(root/'tools/funnel-mold-print'))
from review_extrusion import material_section
sys.path.insert(0,str(root/'hardware/scripts'))
from enclosure_support_audit import _arc_points
work=root/'tmp/funnel-runoff/corner-slice'
mesh=trimesh.load(root/'hardware/printed-parts/zone-c/funnel-mold/cavity.stl',force='mesh',process=True)
x=y=z=0.0;width=.45;height=.24;feature='';begun=False
roads=defaultdict(list);envelope=[]
raw=(work/'native/plate_1.gcode').read_text().split('; MACHINE_END_GCODE_START')[0]
model_features={'Outer wall','Inner wall','Overhang wall','Top surface','Bottom surface','Internal solid infill','Sparse infill','Bridge','Gap infill'}
for line in raw.splitlines():
 if line.startswith('; CHANGE_LAYER'):begun=True
 elif line.startswith('; Z_HEIGHT:'):z=float(line.split(':')[1])
 elif line.startswith('; LAYER_HEIGHT:'):height=float(line.split(':')[1])
 elif line.startswith('; LINE_WIDTH:'):width=float(line.split(':')[1])
 elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
 fields=line.partition(';')[0].split()
 if not fields or fields[0] not in ('G0','G1','G2','G3'):continue
 v={t[0]:float(t[1:]) for t in fields[1:] if re.fullmatch(r'[XYZEIJRP][-+]?\d*\.?\d+',t)}
 nx,ny=v.get('X',x),v.get('Y',y)
 if begun and v.get('E',0)>0 and (nx,ny)!=(x,y):
  points=[(x,y),*( [(nx,ny)] if fields[0] in ('G0','G1') else _arc_points((x,y),(nx,ny),v,fields[0]=='G2'))]
  for (px,py),(qx,qy) in zip(points[:-1],points[1:]):
   if feature in model_features and 54.8<z<56.7:
    a=(py-160,-(px-149.5));b=(qy-160,-(qx-149.5))
    if max(a[0],b[0])>-108 and min(a[0],b[0])<-98 and max(a[1],b[1])>-73 and min(a[1],b[1])<-63:
     roads[z].append((a,b,width,height,feature))
   if feature not in ('Custom','Flush','Prime tower'):
    envelope.extend([(min(px,qx)-width/2,min(py,qy)-width/2),(max(px,qx)+width/2,max(py,qy)+width/2)])
 x,y=nx,ny
window=box(-104.4,-69.1,-101.7,-65.8)
readings=[];all_polys={};sections={}
for z,data in sorted(roads.items()):
 hs=sorted(set(round(a[3],7) for a in data))
 h=.24
 layer=unary_union([LineString([a,b]).buffer(w/2,quad_segs=8) for a,b,w,h,f in data])
 section=material_section(mesh,z-h/2)
 target=section.intersection(window)
 all_polys[z]=layer;sections[z]=section
 coverage=target.intersection(layer).area/target.area if target.area else 1
 missing=target.difference(layer)
 polys=[missing] if missing.geom_type=='Polygon' else list(getattr(missing,'geoms',[]))
 boundary_points=[Point(v) for p in polys if p.geom_type=='Polygon' for v in p.exterior.coords]
 deviation=max((point.distance(layer) for point in boundary_points),default=0.0)
 local=layer.intersection(window)
 above_previous=None
 if len(readings):
  prev=all_polys[readings[-1]['z_mm']]
  above_previous=local.intersection(prev).area/local.area if local.area else None
 hit=[p for p in data if LineString(p[:2]).buffer(p[2]/2).intersects(window)]
 readings.append({'z_mm':z,'model_height_mm':h,'emitted_extrusion_height_values_mm':hs,'section_midplane_z_mm':z-h/2,'native_target_area_mm2':target.area,'covered_target_fraction':coverage,'emitted_segment_count':len(hit),'maximum_uncovered_vertex_distance_mm':deviation,'features':sorted(set(p[4] for p in hit)),'line_widths_mm':sorted(set(p[2] for p in hit)),'local_bead_overlap_previous_layer_fraction':above_previous})
e=np.array(envelope);print(json.dumps({'layers':readings,'deposited_xy_envelope_mm':[float(e[:,0].min()),float(e[:,1].min()),float(e[:,0].max()),float(e[:,1].max())]},indent=2))
(work/'path-readings.json').write_text(json.dumps({'layers':readings,'deposited_xy_envelope_mm':[float(e[:,0].min()),float(e[:,1].min()),float(e[:,0].max()),float(e[:,1].max())]},indent=2)+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
chosen=[r['z_mm'] for r in readings if 55.3<r['z_mm']<56.3]
fig,axes=plt.subplots(1,len(chosen),figsize=(4*len(chosen),4),squeeze=False)
for ax,z in zip(axes[0],chosen):
 sec=sections[z].intersection(box(-106,-71,-100,-64))
 for poly in ([sec] if sec.geom_type=='Polygon' else getattr(sec,'geoms',[])):
  if poly.geom_type=='Polygon':
   ax.fill(*poly.exterior.xy,color='#dee4eb',zorder=0)
   for ring in poly.interiors:ax.fill(*ring.xy,color='white',zorder=1)
 for a,b,w,h,f in roads[z]:
  p=LineString([a,b]).buffer(w/2,quad_segs=8)
  ax.fill(*p.exterior.xy,color='#1677b3' if f in ('Outer wall','Overhang wall') else '#d87926',alpha=.6,zorder=2)
 ax.plot([-103.074],[-67.485],'ko',markersize=4)
 ax.set_xlim(-105,-101);ax.set_ylim(-70,-65);ax.set_aspect('equal');ax.set_title(f'Layer Z {z:.2f} mm');ax.set_xlabel('Native X (mm)')
axes[0,0].set_ylabel('Native Y (mm)')
fig.tight_layout();fig.savefig(work/'corner-paths.png',dpi=180);plt.close(fig)
