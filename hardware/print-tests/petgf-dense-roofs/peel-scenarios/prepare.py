"""prepare.py builds and slices the D-process anchoring and enclosure-surface comparison."""
import importlib.util
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
source = ROOT/'hardware/print-tests/enclosure-support-scenarios/prepare.py'
spec = importlib.util.spec_from_file_location('scenario_plate',source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.HERE = HERE
module.RUN = ROOT/'.cache/runs/d-peel-scenarios-2026-11-09'
module.TITLE = '2026-11-09-D-peel-scenarios-left04-z018-mark1'


def geometry():
    """Generate only the selected specimen geometry through the existing Rust sandbox."""
    config = json.loads((HERE/'samples.json').read_text())
    out = module.RUN/'geometry'
    inputs = out/'inputs'
    inputs.mkdir(parents=True,exist_ok=True)
    for family in config['families']:
        if family['kind']!='crop':
            continue
        path = ROOT/family['source']
        mesh = module.trimesh.load_mesh(path,process=True)
        module.np.savez(inputs/(family['id']+'.npz'),
            names=module.np.frombuffer(json.dumps([family['id']]).encode(),dtype=module.np.uint8),
            colors=module.np.frombuffer(b'[null]',dtype=module.np.uint8),
            records=module.np.frombuffer(json.dumps([[{'kind':'MESH','src':family['source'],'op':'read-stl'}]]).encode(),dtype=module.np.uint8),
            V0=module.np.asarray(mesh.vertices,dtype=module.np.float64),T0=module.np.asarray(mesh.faces,dtype=module.np.uint32),
            F0=module.np.zeros(len(mesh.faces),dtype=module.np.uint32))
        family['source_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (inputs/'spec.json').write_text(json.dumps(config,indent=2)+'\n')
    link = ROOT/'tools/hsm/sandbox/examples/d-peel-scenarios.rs'
    if not link.exists():
        link.symlink_to(HERE/'samples.rs')
    try:
        module.heavy(['cargo','run','--release','--locked','-j2','--manifest-path','tools/hsm/Cargo.toml',
                      '-p','hsm-sandbox','--example','d-peel-scenarios','--',out])
    finally:
        if link.is_symlink() and link.resolve()==HERE/'samples.rs':
            link.unlink()
    record = json.loads((out/'geometry.json').read_text())
    parts = HERE/'parts'
    parts.mkdir(exist_ok=True)
    for part in record['specimens']:
        name = part['id']+'.stl'
        shutil.copyfile(out/name,parts/name)
    shutil.copyfile(out/'geometry.json',parts/'geometry.json')


module.geometry = geometry

if __name__=='__main__':
    module.main()
