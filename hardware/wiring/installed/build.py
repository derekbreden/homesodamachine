"""Materialize installed wiring and update the populated native/viewer assembly.

    tools/cad-venv/bin/python hardware/wiring/installed/build.py

The manual review is a separate command, not a build/commit gate.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
from hardware.wiring.installed.connections import connections, interfaces, UNUSED, BOUNDARIES
from hardware.wiring.installed.model import STOCK, shape
from hardware.wiring.installed.routes import routed
from hardware.wiring.installed.terminals import Attachments

OUT=ROOT/'hardware/wiring/enclosure-wiring'


def compose(scene, ea):
    import cadquery as cq
    at=Attachments(scene,ea)
    at.resolve()
    graph=connections()
    routes=routed(graph,at)
    assembly=cq.Assembly(name='installed-wiring')
    for route in routes:
        stock=STOCK[route.connection.stock]
        s=shape(route,stock['od_mm'])
        assembly.add(s,name='wire-'+route.connection.id,color=cq.Color(*stock['color']))
    from hardware.wiring.installed.terminations import add_terminations
    terminations=add_terminations(assembly,at,graph,routes)
    from hardware.wiring.installed.bundles import add_jackets
    bundles=add_jackets(assembly,at)
    used={id for c in graph for id in (c.start,c.end)}
    manifest={
        'schema':1,'units':'mm','frame':'Enclosure assembly XYZ; Z up',
        'scope':'Installed enclosure wiring, including embedded core leads. External cord, faucet and umbilical end at the enclosure interfaces.',
        'connection_count':len(graph),'harnesses':dict(sorted(Counter(c.harness for c in graph).items())),
        'route_status_counts':dict(Counter(r.status for r in routes)),
        'stock':STOCK,'unused':UNUSED,'boundaries':BOUNDARIES,
        'interfaces':interfaces(at.terminals,graph),
        'terminal_status_counts':dict(sorted(Counter(at.terminals[id].status for id in used).items())),
        'terminals':{id:asdict(at.terminals[id]) for id in sorted(used)},
        'reference_frames':at.frame_checks,
        'cable_passages':at.passages,
        'pcb_reference':at.pcb_reference,
        'terminations':terminations,
        'bundles':bundles,
        'routes':[r.record() for r in routes],
        'limits':[
            'Routes and conductor packing are proposed installed geometry; physical harness dressing and assembly are not accepted by this model.',
            'Lengths follow the routed insulated conductor centreline; hidden crimp insertion, cut reserve, sleeve fit and final service slack are separate.',
            'Wire bend radii are reported geometric radii, not manufacturer-qualified minima.',
            'No rigid Faston boot box is imposed on the flexible valve tabs or the pump motor tabs. G/J use a proposed aft exit at the tab engagement region.',
            'Nominal and unlocated terminals remain visible in the graph and manifest; no exact donor termination is invented.',
            'The electrical graph does not qualify grounding, mains isolation, current capacity or energization.',
        ],
    }
    return assembly,manifest


def attach(assembly, ea):
    """Include wiring in the normal enclosure composition without re-standing it."""
    scene={n:(s,c) for n,s,c in ea.ml.placed_leaves(assembly)}
    wires,manifest=compose(scene,ea)
    assembly.add(wires,name='installed-wiring')
    assembly.wiring_body_names=frozenset(child.name for child in wires.children)
    assembly.wiring_model=manifest


def export_enclosure(assembly, target):
    """One physical export followed by the separately replaceable wiring block."""
    import cadquery as cq
    from _cadq_export import export_assembly
    from hardware.wiring.installed.step_merge import install
    physical=cq.Assembly(name=assembly.name)
    wires=None
    for child in assembly.children:
        if child.name=='installed-wiring':wires=child
        else:physical.add(child,name=child.name)
    export_assembly(physical,str(target))
    if wires is not None:
        # Preserve native swept-face orientation through STEP readback.
        export_assembly(wires,str(OUT.with_suffix('.step')),precision_mode=1)
        write_manifest(assembly.wiring_model,Path(target))
        install(Path(target),OUT.with_suffix('.step'))


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(manifest,scene_step):
    # The physical scene digest excludes this wiring subassembly, avoiding a
    # circular hash when the same wiring is materialized a second time.
    from hardware.wiring.installed.step_merge import base_document
    raw=base_document(scene_step.read_text())
    manifest['physical_scene_sha256']=hashlib.sha256(raw.encode()).hexdigest()
    paths=[Path(__file__),Path(__file__).with_name('connections.py'),
           Path(__file__).with_name('model.py'),Path(__file__).with_name('terminals.py'),
           Path(__file__).with_name('routes.py'),Path(__file__).with_name('retainers.py'),
           Path(__file__).with_name('route-overrides.json'),
           Path(__file__).with_name('terminations.py'),
           Path(__file__).with_name('step_merge.py'),
           Path(__file__).with_name('bundles.py'),Path(__file__).with_name('bundle-routes.json'),
           Path(__file__).with_name('connector-map.json'),
           ROOT/'hardware/manifold-layout/above_core.py',
           ROOT/'hardware/manifold-layout/above-core.json',
           ROOT/'hardware/manifold-layout/above_core_wiring.py',
           ROOT/'hardware/manifold-layout/enclosure-box.json',
           ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure.py',
           ROOT/'hardware/printed-parts/enclosure/enclosure/_fixed_pump_mount.py',
           ROOT/'hardware/printed-parts/cold-core/_above_core_mounts.py',
           ROOT/'hardware/printed-parts/cold-core/_cold_core_interface.py',
           ROOT/'hardware/assembly/harnesses/j2.json',ROOT/'hardware/assembly/harnesses/j13.json']
    manifest['source_sha256']={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with OUT.with_suffix('.csv').open('w',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['wire_id','harness','net','from_terminal','to_terminal','awg',
                         'modeled_length_mm','route_status','start_status','end_status','service'])
        for row in manifest['routes']:
            writer.writerow([row['id'],row['harness'],row['net'],row['start'],row['end'],
                             STOCK[row['stock']]['awg'],row['length_mm'],row['route_status'],
                             manifest['terminals'][row['start']]['status'],
                             manifest['terminals'][row['end']]['status'],row['service']])


def main():
    import enclosure_assembly as ea
    from _cadq_export import import_assembly,export_assembly
    from hardware.wiring.installed.step_merge import install
    target=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    print('Read populated native enclosure',flush=True)
    scene=import_assembly(str(target))
    print('Resolve electrical attachments and route every conductor',flush=True)
    wires,manifest=compose(scene,ea)
    write_manifest(manifest,target)
    export_assembly(wires,str(OUT.with_suffix('.step')),precision_mode=1)
    print('Install wiring while retaining all physical assembly records and meshes',flush=True)
    receipt=install(target,OUT.with_suffix('.step'),verify_retained='--verify-retained' in sys.argv)
    receipt['connection_count']=manifest['connection_count']
    (ROOT/'hardware/wiring/installed/integration-review.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'conductors':manifest['connection_count'],
                      'harnesses':len(manifest['harnesses']),
                      'terminal_status':manifest['terminal_status_counts'],
                      'frame_max_residual_mm':max(r['maximum_extent_residual_mm'] for r in manifest['reference_frames'].values())}),flush=True)


if __name__=='__main__': main()
