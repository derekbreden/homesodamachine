"""Create source-bound viewer payloads without contacting motion or printers."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import cadquery as cq
import trimesh
from OCP.Quantity import Quantity_TypeOfColor

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/printed-parts/fixtures/gun-positioner'
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import flute_payload as fp
import _mesh_payload as mp

spec = importlib.util.spec_from_file_location('gp', OUT / 'gun_positioner.py')
gp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gp)
parts = json.loads((OUT / 'parts.json').read_text())
checks = []
for part in parts:
    stl = OUT / part['stl']
    step = OUT / part['step']
    mesh = trimesh.load_mesh(stl)
    mesh.merge_vertices()
    if not mesh.is_watertight or not mesh.is_winding_consistent:
        raise ValueError(f"Open or inconsistent fabrication STL: {stl.name}")
    pos, nrm, idx, fac = fp.creased(mesh)
    color = list(cq.Color(*gp.COLORS[part['material']]).wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB))
    data = dict(name=part['name'], color=color, pos=pos.ravel().tolist(),
                nrm=nrm.ravel().tolist(), idx=idx.ravel().tolist(), fac=fac.tolist())
    mp.write([data], str(step) + '.mesh', src=mp.source_digest(step),
             cut=dict(dev=0.0, bound=round(fp.deflection(mesh), 4)))
    checks.append(dict(part=part['name'], triangles=len(mesh.faces), watertight=True,
                       winding_consistent=True, payload_preserves_STL_triangles=True))

assembly, instances = gp.assembly()
step = OUT / 'gun-positioner-assembly.step'
mp.write(mp.from_assembly(assembly), str(step) + '.mesh', src=mp.source_digest(step))
(OUT / 'mesh-export-check.json').write_text(json.dumps(dict(
    status='Successful export checks; no physical or post-publication lint acceptance.',
    source_sha256=hashlib.sha256((OUT / 'gun_positioner.py').read_bytes()).hexdigest(),
    fabrication_parts=checks, assembly_instances=len(instances)), indent=2) + '\n')

hashes = {str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for directory in ('step', 'stl', 'templates') for p in sorted((OUT / directory).iterdir())}
for name in ('gun-positioner-assembly.step', 'gun-positioner-assembly.step.mesh'):
    hashes[name] = hashlib.sha256((OUT / name).read_bytes()).hexdigest()
(OUT / 'asset-hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
receipt = json.loads((OUT / 'export-receipt.json').read_text())
for path in (Path(__file__), ROOT / 'hardware/scripts/flute_payload.py', ROOT / 'hardware/scripts/_mesh_payload.py'):
    receipt['sources_sha256'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
receipt.update(payload_status='Successful source-bound viewer payload export',
               fabrication_payloads=len(parts), assembly_payload_sha256=hashes['gun-positioner-assembly.step.mesh'],
               mesh_check_receipt='mesh-export-check.json')
(OUT / 'export-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(dict(payloads=len(parts)+1, mesh_checks='passed'), indent=2))
