from pathlib import Path
import sys,json,math,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/cadlib'),str(ROOT/'hardware/printed-parts/cold-core'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import _above_core_mounts as mounts
import above_core,rear_snaps,fits
from print_mesh import write_print_stl
from _cadq_export import export_step
OUT=HERE;d=mounts.pump_cradle_datums();cx,cy,cz=d['centre_world_mm'];frame=d['frame'];fy=frame['translation_mm'][1];tz=frame['translation_mm'][2];face=above_core.specification()['cap_face_z_mm'];first,last=d['band_native_x_mm'];fore,rear=d['selected']['rail_stop_native_x_mm'];wide=d['stock_half_width_mm']+3.;half=24.81
params=json.loads((ROOT/'hardware/reference/g-ganen-pump/reference-parameters.json').read_text());floor=tz+params['rigid_underside']['wire_cover_floor_datum']['coefficients'][2]-fits.running

def box(lo,hi):return cq.Solid.makeBox(*(hi[k]-lo[k] for k in range(3)),cq.Vector(*lo))
# One large block, with a flat floor, straight channel and two flat rail seats.
blank=box((cx-wide,fy+fore[0],face-.1),(cx+wide,fy+rear[1],cz))
body=blank.cut(box((cx-half,fy+fore[0]-.1,floor),(cx+half,fy+rear[1]+.1,cz+1)))
for rail in d['rail_rooms']:
 a,b,c=rail['floor_planes'][0];c-=fits.running*math.sqrt(1+a*a+b*b);outer=rail['outer_y_mm'];near=rail['side']*half;profiles=[]
 for x in (fore[1],rear[0]):
  yz=[(outer,a*x+b*outer+c),(near,a*x+b*near+c),(near,100.),(outer,100.)]
  profiles.append(cq.Wire.makePolygon([cq.Vector(x,y,z) for y,z in yz],close=True))
 body=body.cut(cq.Solid.makeLoft(profiles,ruled=True).moved(above_core.frame_location(frame)))
# One plane clears both head lugs and meets the full-height receiver end stock.
slope=(cz-tz-24.75)/first;profiles=[]
for x in (fore[0]-.1,first):
 z=tz+24.75+slope*x;y=fy+x
 profiles.append(cq.Wire.makePolygon([cq.Vector(cx-wide-.1,y,z),cq.Vector(cx+wide+.1,y,z),cq.Vector(cx+wide+.1,y,cz+1),cq.Vector(cx-wide-.1,y,cz+1)],close=True))
body=body.cut(cq.Solid.makeLoft(profiles,ruled=True))
for cap in d['caps']:
 station=dict(cap['snap_station'],outer=wide)
 for pocket in rear_snaps.pockets(station):body=body.cut(mounts._pump_cap_to_world(pocket,cap))
plate=box((cx-wide-3,fy+fore[0]-3,face-7.4),(cx+wide+3,fy+rear[1]+3,face))
proposal=plate.fuse(body).clean();current=plate.fuse(mounts.pump_cradle()).clean();stock=plate.fuse(blank).clean();cap=mounts.pump_snap_cap()
report={'scope':'Whole mount comparison on the same lid section. Proposal is carved from one broad blank. The upper spring clip and receiving ledges stay at their production datums. The proposed floor has 0.25 mm nominal air to the corrected rigid cable-cover datum.','geometry':{},'rail_bearing_widths_mm':[abs(r['outer_y_mm'])-half for r in d['rail_rooms']],'outer_half_width_mm':wide,'central_channel_width_mm':2*half,'floor_world_z_mm':floor,'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'hardware/manifold-layout/above-core.json',ROOT/'hardware/printed-parts/cold-core/_above_core_mounts.py',ROOT/'hardware/reference/g-ganen-pump/reference-parameters.json']}}
for name,shape in [('current-common-plate',current),('solid-block',proposal),('starting-block',stock),('seated-cap',cap)]:
 path=OUT/(name+'.step');export_step(shape,str(path));m=write_print_stl(shape,OUT/(name+'.stl'));r={'valid':shape.isValid(),'solids':len(shape.Solids()),'faces':len(shape.Faces()),'edges':len(shape.Edges()),'volume_mm3':shape.Volume(),'watertight':bool(m.is_watertight),'triangles':len(m.faces),'step_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'stl_sha256':hashlib.sha256((OUT/(name+'.stl')).read_bytes()).hexdigest()};report['geometry'][name]=r;print(name,json.dumps(r),flush=True)
report['cap_overlap_mm3']=proposal.intersect(cap).Volume();print('cap_overlap',report['cap_overlap_mm3'],flush=True)
(OUT/'solid-block-report.json').write_text(json.dumps(report,indent=2)+'\n')
# Native reading of the complete bare purchased pump, in its production pose.
import above_core_parts as parts
pump=parts.pump_native().moved(above_core.location('g-ganen-pump'));report['pump_overlap_mm3']=sum(s.Volume() for s in pump.intersect(proposal).Solids());print('pump_overlap',report['pump_overlap_mm3'],flush=True)
export_step(pump,str(OUT/'bare-pump.step'))
(OUT/'solid-block-report.json').write_text(json.dumps(report,indent=2)+'\n')
