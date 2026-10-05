"""Check fabrication solids and same-face drill circles without mesh lint."""
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/printed-parts/fixtures/gun-positioner'
src=OUT/'gun_positioner.py'
spec=importlib.util.spec_from_file_location('gun_positioner_source_check',src)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.init_parts()
invalid=[];overlaps=[];clearances=[]
for name,d in m.PARTS.items():
    if d['kind'] in ('metal','print') and not d['model'].val().isValid():invalid.append(name)
    faces={'registered_XY':d.get('holes',[])}
    for face,h in d.get('drilling_faces',{}).items():
        if isinstance(h,dict):h=h.get('holes_mm',[])
        if isinstance(h,list):faces[face]=h
    for face,holes in faces.items():
        circles=[h for h in holes if isinstance(h,(list,tuple)) and len(h)==3]
        for a,b in itertools.combinations(circles,2):
            distance=math.hypot(a[0]-b[0],a[1]-b[1]);ligament=distance-(a[2]+b[2])/2
            row=dict(part=name,face=face,a=a,b=b,center_distance_mm=distance,bore_ligament_mm=ligament)
            if ligament< -1e-7:overlaps.append(row)
            elif ligament<3:clearances.append(row)
assembly,instances=m.assembly();fixtures=m.fixture_assemblies()
record=dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
            fabrication_parts=sum(d['kind'] in ('metal','print') for d in m.PARTS.values()),
            registered_parts=len(m.PARTS),assembly_instances=len(instances),
            fixture_instances={n:len(v[1]) for n,v in fixtures.items()},
            invalid_solids=invalid,same_face_drill_circle_overlaps=overlaps,
            bore_ligaments_below3mm=clearances,
            head_clearance_checks=[
                dict(joint='SBR block and carriage attachment',centers=[[77,84],[90,90]],distance_mm=math.hypot(13,6),two10mm_washer_clearance_mm=math.hypot(13,6)-10),
                dict(joint='gauge cap and rear M4',centers=[[28,48.2],[20.5,36.5]],distance_mm=math.hypot(7.5,11.7),OD12_plus_OD10_clearance_mm=math.hypot(7.5,11.7)-11),
                dict(joint='hub end keeper and M5 mounts',keeper_OD_mm=20,mount_pattern_mm=[26,20],M5_washer_OD_mm=10,radial_clearance_mm=math.hypot(13,10)-15),
                dict(joint='belt guard M3 and upper M6 washers',centers=[[5,13],[12,22]],distance_mm=math.hypot(7,9),OD7_plus_OD12_clearance_mm=math.hypot(7,9)-9.5,guard_spacer_to_thrust_radial_clearance_mm=math.hypot(5,13)-12),
                dict(joint='thrust support leg foot heads',distance_mm=math.hypot(4.7,12),two10mm_washer_clearance_mm=math.hypot(4.7,12)-10),
                dict(joint='service clamp and fork head',distance_mm=math.hypot(10,14.475),two10mm_washer_clearance_mm=math.hypot(10,14.475)-10)],
            status='pass' if not invalid and not overlaps else 'fail',
            scope='Analytic solid validity and registered same-face drill/head geometry only. This is not mesh lint, physical fit, strength, clearance of the complete moving assembly, print acceptance or accuracy acceptance.')
(OUT/'fabrication-source-check.json').write_text(json.dumps(record,indent=2)+'\n')
(OUT/'geometry-check.json').write_text(json.dumps(m.checks(),indent=2)+'\n')
print(json.dumps({k:record[k] for k in ('source_sha256','fabrication_parts','assembly_instances','fixture_instances','invalid_solids','same_face_drill_circle_overlaps','status')},indent=2))
if invalid or overlaps:raise SystemExit(1)
