"""Bind the low420's closed, lever and entry fields to the current controller."""
from pathlib import Path
import hashlib,json
import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    roof=json.loads((HERE/'roof-candidate.json').read_text())
    wr=json.loads((HERE/'wr-candidate.json').read_text())
    structure=json.loads((HERE.parent/'structure/candidate.json').read_text())
    pcbr=structure['parts']['pcba']
    pcb=cq.Shape.importBrep(str(ROOT/pcbr['brep']))
    parts={'closed_body':roof['expected_devices']['wago-reeds-b'],
      'opened_levers':roof['working_envelopes']['wago-reeds-b']['levers'],
      'entry_wires':roof['working_envelopes']['wago-reeds-b']['entry_wire'],
      'platform':wr['parts']['west-junction-platform']}
    checks=[]
    for name,r in parts.items():
        shape=cq.Shape.importBrep(str(ROOT/r['brep']))
        gap=shape.distance(pcb)
        common=abs(shape.intersect(pcb,tol=.0001).Volume(tol=1e-9))
        checks.append({'part':name,'native_gap_mm':gap,'common_mm3':common,
          'pass':gap>=.9999 and common<.001})
    report={'checks':checks,'pass':all(r['pass'] for r in checks),
      'input_geometry_sha256':{name:hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()
        for name,r in {'pcba':pcbr,**parts}.items()},
      'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
      'scope':'Exact native low420/controller clearance. Closed body, both lever fields and all entry turns preserve at least1mm air.'}
    (HERE/'junction-controller-clearance.json').write_text(json.dumps(report,indent=2)+'\n')
    roof['controller_clearances_mm']={
      {'closed_body':'reeds_b_closed_body','opened_levers':'reeds_b_opened_levers',
       'entry_wires':'reeds_b_entry_wires','platform':'junction_platform'}[r['part']]:r['native_gap_mm']
      for r in checks}
    roof['controller_clearance_review']=report
    (HERE/'roof-candidate.json').write_text(json.dumps(roof,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    assert report['pass'],checks

if __name__=='__main__':main()
