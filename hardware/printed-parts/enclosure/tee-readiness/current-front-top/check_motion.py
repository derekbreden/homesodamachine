#!/usr/bin/env python3
"""Existing carrier entry/motion audit against the fresh front-top and bounded neighbors.

Uses current native carrier halves and cartridge/cap. Valve/coil neighbors and
moving tees/tubes use the production placement functions. Other shell quadrants,
cold core, water pump and fittings outside this local set are not qualified.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
os.environ.setdefault('HSM_NO_BUILD_LOCK','1')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def match(a,b,path='root'):
    if isinstance(a,dict):
        if set(a)!=set(b):raise ValueError('Fixture keys differ at '+path)
        for key in a:match(a[key],b[key],path+'.'+key)
    elif isinstance(a,(list,tuple)):
        if len(a)!=len(b):raise ValueError('Fixture length differs at '+path)
        for i,(x,y) in enumerate(zip(a,b)):match(x,y,f'{path}[{i}]')
    elif isinstance(a,(int,float)) and not isinstance(a,bool):
        if abs(a-b)>1e-5:raise ValueError(f'Fixture datum differs at {path}: {a} / {b}')
    elif a!=b:raise ValueError(f'Fixture value differs at {path}: {a} / {b}')


def main():
    fixture=json.loads((HERE/'fixture.json').read_text())
    before_inputs={**fixture['input_sha256'],fixture['step']:fixture['step_sha256']}
    for path in (HERE/'fixture.json',
                 ROOT/'hardware/printed-parts/enclosure/enclosure/pump-cartridge-generation.json',
                 ROOT/'hardware/printed-parts/enclosure/tee-carrier/spring-measurements.json',
                 ROOT/'hardware/reference/jg-pp0208e-tee/scan-registration.json'):
        before_inputs[str(path.relative_to(ROOT))]=sha(path)
    for name,digest in {**fixture['source_sha256'],**before_inputs}.items():
        assert sha(ROOT/name)==digest,name
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard',
                                   '--','hardware','tools'],cwd=ROOT,text=True).splitlines()
    before_sources={name:sha(ROOT/name) for name in names
                    if name.endswith('.py') and (ROOT/name).is_file()}
    sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/scripts'),
                 str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
    import verify_tee_integration as region
    import _box_spec
    import cadquery as cq
    ea,enc,carrier=region.ea,region.enc,region.carrier
    box,_bounds=_box_spec.read(enc.Box,enc.Bound,(enc.Pack,enc.PortField,enc.Nameplate),
                              path=ROOT/'hardware/manifold-layout/enclosure-box.json')
    started=time.perf_counter()
    lift,carry,stood=region.small_placed_region()
    solids={name:solid for name,solid,_color in stood}
    trays=ea.pump_tray_stations(solids)
    plate=ea.collet_plate_spec(carry,trays)
    spec=ea.tee_carrier_spec(carry,stood,plate)
    interface=ea.tee_carrier_interface(spec,plate,stood)
    match(trays,box.pack.pump_trays,'pump_trays')
    match(plate,box.pack.collet_plate,'collet_plate')
    match(interface,box.pack.tee_carrier,'tee_carrier')
    mismatches=carrier.placement_mismatches(spec)
    if mismatches:raise ValueError('Native carrier specification differs: '+str(mismatches))
    a=cq.Assembly(name='bounded-front-top-neighbors')
    for name,solid,_color in stood:a.add(solid,name=name)
    a.tee_carrier=interface
    a.tee_carrier_spec=spec
    # The successful dedicated cartridge manifest qualifies these exact native
    # pieces independently of the unfinished complete enclosure assembly.
    cartridge=json.loads((ROOT/'hardware/printed-parts/enclosure/enclosure/pump-cartridge-generation.json').read_text())
    for name in ('pump-cartridge','pump-cap'):
        path=ROOT/f'hardware/printed-parts/enclosure/enclosure/enclosure-{name}.step'
        expected=cartridge['artifact_sha256'][str(path.relative_to(ROOT))]
        assert sha(path)==expected,path
        before_inputs[str(path.relative_to(ROOT))]=expected
        a.add(cq.importers.importStep(str(path)).val(),name='enclosure-'+name)
    halves={}
    for side,label in ((-1,'left'),(1,'right')):
        path=ROOT/f'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-{label}.step'
        before_inputs[str(path.relative_to(ROOT))]=sha(path)
        halves[side]=cq.importers.importStep(str(path)).val()
    wall=cq.importers.importStep(str(ROOT/fixture['step'])).val()
    saved_builder=carrier.build_half
    try:
        # The enclosing-envelope and motion checks now read the actual native
        # carrier files. No geometry or threshold in the existing audit is changed.
        carrier.build_half=lambda _spec,side:cq.Workplane(obj=halves[side])
        bound=ea._carrier_front_top_motion_bound(a,wall,box)
    finally:
        carrier.build_half=saved_builder
    sources={}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if not name or Path(name).suffix!='.py':continue
        path=Path(name).resolve()
        if not path.is_relative_to(ROOT) or '/site-packages/' in str(path):continue
        name=str(path.relative_to(ROOT));digest=sha(path)
        if before_sources.get(name)!=digest:raise ValueError('Loaded source changed: '+name)
        sources[name]=digest
    for name,digest in before_inputs.items():
        if sha(ROOT/name)!=digest:raise ValueError('Native input changed: '+name)
    result={'status':'pass' if bound.ok else 'fail','bound':bound._asdict(),
            'scope':__doc__,'fixture_sha256':sha(HERE/'fixture.json'),
            'source_sha256':dict(sorted(sources.items())),
            'input_sha256':before_inputs,'native_carrier_halves':True,
            'present_neighbors':[name for name,_shape,_color in stood]
                                +['enclosure-pump-cartridge','enclosure-pump-cap'],
            'blocking_neighbors_used_by_existing_audit':[name for name,_shape,_color in stood
                                                        if name.startswith(('coil-','valve-'))]
                                                       +['current-front-top','enclosure-pump-cartridge','enclosure-pump-cap'],
            'excluded_context':['Other enclosure quadrants and installed hardware outside the named local set.',
                                'Selected G Ganen integration; this is the completed SeaFlo-sized Box baseline.',
                                'Integral latch and positive spring capture studies are not integrated into these production carrier halves.'],
            'unqualified_tee_datums':region.tee.UNQUALIFIED_DATUMS,
            'assembly_current':False,'production_enclosure_released':False,
            'elapsed_seconds':time.perf_counter()-started}
    (HERE/'motion-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'bound':result['bound'],
                      'elapsed_seconds':result['elapsed_seconds']},indent=2),flush=True)
    return int(not bound.ok)


if __name__=='__main__':raise SystemExit(main())
