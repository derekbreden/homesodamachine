"""Flatten only the installed WATER chip's decorative west rim.

The purchased union, clamped annulus, bore, lettering and receiver stay fixed.
"""
from pathlib import Path
import hashlib
import json
import sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
CACHE=ROOT/'.cache/pump-first-layout/routing'
sys.path[:0]=[str(STUDY)]
import baseline
import evidence_binding

WEST_FACE=-107.5

def flatten_water_ring(shape):
    b=shape.BoundingBox()
    keeper=cq.Solid.makeBox(b.xmax-WEST_FACE+1,b.ylen+2,b.zlen+2,
                            cq.Vector(WEST_FACE,b.ymin-1,b.zmin-1))
    result=shape.intersect(keeper,tol=.0001)
    assert result.isValid() and len(result.Solids())==1
    assert result.BoundingBox().xmin>=WEST_FACE-1e-6
    return result

def finish_record():
    return {'finish':'Flat west decorative rim at the established exterior face',
        'west_face_mm':WEST_FACE,'decorative_rim_trim_mm':1.48,
        'bore_diameter_mm':17.44,'west_material_outside_bore_mm':8.28,
        'west_visible_color_beyond_union_flange_mm':5.57,
        'unchanged':['union geometry and pose','17.44 mm chip bore',
                     'complete flange bearing annulus','lettering and recess',
                     'receiver bore, floor, slip and keying geometry'],
        'receiver_scope':'The exact original chip pocket is retained inside the established width; its overhanging decorative outline lies outside the physical wall.'}

def bounds(s):
    b=s.BoundingBox()
    return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def common(a,b):
    return a.intersect(b,tol=.0001).Volume(tol=1e-9)

def publish(write_geometry=True):
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [Path(__file__),HERE/'build_candidate.py',STUDY/'baseline.py',STUDY/'evidence_binding.py']}
    path=HERE/'candidate.json';data=json.loads(path.read_bytes())
    rec=data['parts']['bulkhead-ring-water']
    delta=tuple(rec['transform']['translation'])
    original=baseline.read(['bulkhead-ring-water'])['bulkhead-ring-water'].translate(delta)
    baseline_record=baseline.prepare()['parts']['bulkhead-ring-water']
    baseline_path=baseline.CACHE/baseline_record['file']
    baseline_sha=hashlib.sha256(baseline_path.read_bytes()).hexdigest()
    result=flatten_water_ring(original)
    centre=data['ports']['bulkhead-water']['inboard']['pos'];b=original.BoundingBox()
    cylinder=lambda r:cq.Solid.makeCylinder(r,b.ylen+.2,cq.Vector(centre[0],b.ymin-.1,centre[2]),cq.Vector(0,1,0))
    flange=cylinder(11.43);bore=cylinder(8.7199)
    word_rec=data['parts']['bulkhead-ring-water-word'];word_path=ROOT/word_rec['brep']
    word_sha=hashlib.sha256(word_path.read_bytes()).hexdigest()
    word=cq.Shape.importBrep(str(word_path));wb=word.BoundingBox()
    word_region=cq.Solid.makeBox(wb.xlen+2,b.ylen+.2,wb.zlen+2,cq.Vector(wb.xmin-1,b.ymin-.1,wb.zmin-1))
    removed=original.cut(result,tol=.0001)
    checks=[{'name':'valid single printed chip','pass':result.isValid() and len(result.Solids())==1},
      {'name':'215 mm appliance width','pass':result.BoundingBox().xmin>=WEST_FACE-1e-6,'west_face_mm':result.BoundingBox().xmin},
      {'name':'complete flange bearing material preserved','removed_bearing_volume_mm3':common(removed,flange),'pass':common(removed,flange)<1e-6},
      {'name':'complete chip bore preserved','material_in_bore_mm3':common(result,bore),'pass':common(result,bore)<1e-6},
      {'name':'word and recessed lettering preserved','removed_word_region_mm3':common(removed,word_region),'word_sha256':word_sha,'pass':common(removed,word_region)<1e-6}]
    union_rec=data['parts']['bulkhead-water'];union_path=ROOT/union_rec['brep']
    union_sha=hashlib.sha256(union_path.read_bytes()).hexdigest()
    union=cq.Shape.importBrep(str(union_path));overlap=common(result,union)
    checks.append({'name':'purchased union native clearance','common_mm3':overlap,'pass':overlap<1e-6})
    shell_path=STUDY/'funnel/shells.json';shell_data=json.loads(shell_path.read_bytes())
    pocket_rec=shell_data['interfaces']['original-rear-chip-pocket-0']
    pocket_path=ROOT/pocket_rec['brep'];pocket_sha=hashlib.sha256(pocket_path.read_bytes()).hexdigest()
    pocket=cq.Shape.importBrep(str(pocket_path)).translate((centre[0]+78.07,0,centre[2]-336.21058083755))
    outside=abs(result.cut(pocket,tol=.0001).Volume(tol=1e-9))
    checks.append({'name':'complete chip fits the unchanged keyed receiver',
                   'outside_receiver_volume_mm3':outside,'pass':outside<1e-6})
    wrong=result.rotate((centre[0],b.ymin,centre[2]),(centre[0],b.ymin+1,centre[2]),180)
    wrong_outside=abs(wrong.cut(pocket,tol=.0001).Volume(tol=1e-9))
    checks.append({'name':'upside-down chip placement remains rejected',
                   'outside_receiver_volume_mm3':wrong_outside,'pass':wrong_outside>1})
    assert all(row['pass']for row in checks),checks
    if write_geometry:
        output=CACHE/'bulkhead-ring-water.brep';result.exportBrep(str(output))
        rec.update(brep=str(output.relative_to(ROOT)),bounds=bounds(result),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
            detail='WATER identification chip with its west decorative rim flat at X−107.5; native bore, flange bearing and TAP lettering preserved.',decorative_finish=finish_record())
        data.setdefault('interface_moves',{})['water_identification_chip']=finish_record()
        data.setdefault('standalone_print_parts',{})['water-identification-ring']={
            'source_part':'bulkhead-ring-water','rotation_x_deg':90}
        path.write_text(json.dumps(data,indent=2)+'\n')
    else:
        selected_path=ROOT/rec['brep']
        selected=cq.Shape.importBrep(str(selected_path))
        missing=abs(result.cut(selected,tol=.0001).Volume(tol=1e-9))
        extra=abs(selected.cut(result,tol=.0001).Volume(tol=1e-9))
        current_sha=hashlib.sha256(selected_path.read_bytes()).hexdigest()
        checks.append({'name':'selected producer geometry correspondence',
            'missing_volume_mm3':missing,'extra_volume_mm3':extra,
            'pass':missing<1e-6 and extra<1e-6 and current_sha==rec['sha256']})
        assert all(row['pass']for row in checks),checks
    native_inputs={'bulkhead-water':{'brep':union_rec['brep'],'sha256':union_sha},'bulkhead-ring-water-word':{'brep':word_rec['brep'],'sha256':word_sha},
         'original-ring':{'brep':str(baseline_path.relative_to(ROOT)),'sha256':baseline_sha},
         'original-chip-pocket':{'brep':pocket_rec['brep'],'sha256':pocket_sha},
         'selected-ring':{'brep':rec['brep'],'sha256':rec['sha256']}}
    content_inputs={str(path.relative_to(ROOT)):evidence_binding.content_sha256(data)}
    content_inputs[str(shell_path.relative_to(ROOT))]=evidence_binding.content_sha256(shell_data)
    drift=['native:'+name for name,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    drift+=['source:'+p for p,h in sources.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    drift+=['manifest-content:'+p for p,h in content_inputs.items()if evidence_binding.manifest_content_sha256(ROOT/p)!=h]
    report={'pass':all(row['pass']for row in checks)and not drift,'checks':checks,'original_bounds_mm':bounds(original),
      'selected_bounds_mm':bounds(result),'decorative_material_removed_mm3':removed.Volume(tol=1e-9),
      'finish':finish_record(),'part':rec,
      'native_inputs':native_inputs,'source_inputs':sources,'source_drift':drift,
      'manifest_content_sha256':content_inputs,
      'scope':'Native geometry and lettering preservation. The trim remains 5.57 mm outside the complete flange and preserves 8.28 mm material outside the bore. Existing physical finish acceptance retains its scope; the flat decorative rim is a new printed detail.'}
    (HERE/'water-ring-finish.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'removed_mm3':report['decorative_material_removed_mm3'],'bounds':report['selected_bounds_mm'],'checks':checks},indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Rebind the selected native finish proof without changing any part or scene record.')
    publish(write_geometry=not parser.parse_args().check)
