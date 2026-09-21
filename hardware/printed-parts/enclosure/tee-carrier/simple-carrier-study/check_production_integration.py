"""Compare the integrated source bodies with the frozen-input native study."""
import ast
import contextlib
import io
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
from build_concept import build,sha

HERE=Path(__file__).resolve().parent
REPO=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
sys.path.insert(0,str(HERE.parent))
import tee_carrier as carrier
import enclosure


def region_hash(path,names):
    source=path.read_text()
    rows={}
    for node in ast.parse(source).body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names:
            rows[node.name]=hashlib.sha256(ast.get_source_segment(source,node).encode()).hexdigest()
    if set(rows)!=set(names):raise ValueError('Missing owned source region')
    return rows


def main():
    _M,I,_plain,_blank,L,R,Rrigid,*_=build()
    actual=carrier.assembly_parts()
    rows=[]
    for key,study in (('left',L),('right',R),('right_structural',Rrigid)):
        live=actual[key]
        rows.append({'part':key,'live_valid':live.isValid(),'live_solids':len(live.Solids()),
            'live_volume_mm3':live.Volume(),'study_volume_mm3':study.Volume(),
            'added_mm3':live.cut(study).Volume(),'missing_mm3':study.cut(live).Volume()})
    buffer=io.StringIO()
    with contextlib.redirect_stdout(buffer):
        selftest_exit=carrier.selftest()
    cups=[]
    live_cups=enclosure._tee_carrier_fixed_cups(carrier.interface())
    for station,live in zip(I['spring_stations'],live_cups):
        x,z=station['x'],station['z'];floor=station['seat_floor_y'];r=I['spring_bore_d']/2
        p=cq.Vector(x,floor+1.9,z)
        study=cq.Solid.makeCylinder(r+2,6.1,p,cq.Vector(0,1,0)).cut(
            cq.Solid.makeCylinder(r,6.3,p-cq.Vector(0,.1,0),cq.Vector(0,1,0)))
        live=live.val() if isinstance(live,cq.Workplane) else live
        cups.append({'x_mm':x,'live_valid':live.isValid(),'live_solids':len(live.Solids()),
            'added_mm3':live.cut(study).Volume(),'missing_mm3':study.cut(live).Volume()})
    sources=[HERE.parent/'tee_carrier.py',HERE.parent/'_simple_carrier.py',HERE.parent/'_carrier_motion.py']
    ep=REPO/'hardware/printed-parts/enclosure/enclosure/enclosure.py'
    ap=REPO/'hardware/manifold-layout/enclosure_assembly.py'
    report={'scope':'Production source versus the isolated study, before combined generation. Only listed bodies and owned function regions are compared. Final whole-enclosure generation and its actual support slice remain separate.',
        'script_sha256':sha(__file__),'study_generator_sha256':sha(HERE/'build_concept.py'),
        'source_sha256':{str(p.relative_to(REPO)):sha(p) for p in sources},
        'shared_file_snapshots':{str(p.relative_to(REPO)):sha(p) for p in (ep,ap)},
        'owned_region_sha256':{
            str(ep.relative_to(REPO)):region_hash(ep,['_tee_carrier_fixed_cups','_tee_carrier_service_slots']),
            str(ap.relative_to(REPO)):region_hash(ap,['tee_carrier_spec','tee_carrier_interface','_carrier_front_top_motion_bound'])},
        'selftest':{'exit_code':selftest_exit,'output':buffer.getvalue()},
        'carrier_bodies':rows,'fixed_cup_extensions':cups,'interface':carrier.interface(),
        'all_native_bodies_equal':selftest_exit==0 and all(r['live_valid'] and r['live_solids']==1 and r['added_mm3']<1e-5 and r['missing_mm3']<1e-5 for r in rows+cups)}
    (HERE/'production-integration-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'equal':report['all_native_bodies_equal'],'carrier':rows,'fixed_cups':cups},indent=2))
    if not report['all_native_bodies_equal']:raise SystemExit(1)


if __name__=='__main__':main()
