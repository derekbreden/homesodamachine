"""Measure useful fill levels in the actual enclosed native cavity."""
from pathlib import Path
import hashlib,json,math
import cadquery as cq
ROOT=next(p for p in Path(__file__).resolve().parents
          if (p/'hardware/scripts/_cadq_export.py').exists())
HERE=Path(__file__).parent
manifest=json.loads((HERE/'candidate.json').read_text())
path=ROOT/manifest['capacity_artifact']['brep']
cavity=cq.Shape.importBrep(str(path))
top=355
w,d=manifest['mouth_dimensions_mm']
area=w*d-(4-math.pi)*14**2
capacity=cavity.Volume(tol=1e-9)
rows=[]
OUT=ROOT/'.cache/pump-first-layout/funnel'/f"aft-{manifest['aft_extension_mm']:g}"
for wanted in (440,500,600):
    headroom=(capacity-1000*wanted)/area
    level=top-headroom
    # These fills stand within the straight mouth section. The native Boolean
    # below supplies an independent volume reading for the computed liquid level.
    assert level>336.864053708995
    clip=cq.Solid.makeBox(1000,1000,level-300,cq.Vector(-500,-500,300))
    liquid=cavity.intersect(clip,tol=.0001).clean()
    measured=liquid.Volume(tol=1e-9)/1000
    assert abs(measured-wanted)<.001,(wanted,measured)
    row={'fill_ml':wanted,'liquid_surface_world_z_mm':level,'headroom_mm':headroom,
         'native_measured_ml':measured,'cover_skirt_underside_z_mm':349,
         'nominal_surface_below_cover_skirt':level<349}
    if wanted in (500,600):
        brep=OUT/f'funnel-liquid-{wanted}ml.brep';liquid.exportBrep(str(brep))
        mesh=OUT/f'funnel-liquid-{wanted}ml.json';v,t=liquid.tessellate(.12,.08)
        mesh.write_text(json.dumps({'vertices':[[p.x,p.y,p.z] for p in v],
                                   'triangles':[list(p) for p in t]},separators=(',',':'))+'\n')
        row['inspection_artifact']={'brep':str(brep.relative_to(ROOT)),'mesh':str(mesh.relative_to(ROOT)),
                                    'detail':f'Actual{wanted}mL liquid volume in the selected native cavity; surfaceZ{level:.3f},headroom{headroom:.3f}mm. Cover-skirt clearance is recorded independently.'}
    rows.append(row)
result={'aft_extension_mm':manifest['aft_extension_mm'],'preferred_inspection_fill_ml':500,
        'straight_mouth_area_mm2':area,'rows':rows,
        'native_cavity_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Gravity level in the nominal upright cavity. Fill levels do not establish draining rate, splash containment or molded-part tolerances.'}
(HERE/'capacity-levels.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
