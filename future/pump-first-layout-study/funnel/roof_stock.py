"""Native 12 mm ceiling stock with the enlarged funnel mating voids open.

The nominal production ceiling extends Z343..355. Its added inner stock ends
at Z353 to overlap the retained outer 3 mm roof. Component crown pockets are
opened by the study integration after the final locations have been selected.
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
ROOT=next(p for p in Path(__file__).resolve().parents
          if (p/'hardware/scripts/_cadq_export.py').exists())
HERE=Path(__file__).parent
from study_configuration import configuration,save_record
extra,preview,candidate=configuration()
OUT=ROOT/'.cache/pump-first-layout/funnel'/f'aft-{extra:g}'/'shells'
OUT.mkdir(parents=True,exist_ok=True)
native=cq.Workplane('XY').box(197,246.5,10,centered=(True,True,False)).translate((0,342.05,343)).val()
interfaces=json.loads((HERE/f'mating-aft-{extra:g}.json').read_text())['interfaces']
for n in ('frame-shell-clearance','brim-pocket','collar-throat','back-rail-channels'):
    native=native.cut(cq.Shape.importBrep(str(ROOT/interfaces[n]['brep'])),tol=.0001)
native=native.clean()
assert native.isValid() and len(native.Solids())==1
path=OUT/'funnel-mated-ceiling-stock.brep';native.exportBrep(str(path))
b=native.BoundingBox()
info={'aft_extension_mm':extra,'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'bounds_world_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],
      'nominal_finished_ceiling_mm':12,'nominal_finished_ceiling_z_mm':[343,355],
      'added_stock_z_mm':[343,353],'role':'structure',
      'detail':f'Native production12mm roof stock, added to retained3mm outer roof with current +{extra:g}mm funnel/frame opening already cut; final component crown pockets must be opened after fusing.',
      'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
      'valid':native.isValid(),'solids':len(native.Solids())}
save_record('roof-stock',extra,preview,info)
print(json.dumps(info,indent=2))
