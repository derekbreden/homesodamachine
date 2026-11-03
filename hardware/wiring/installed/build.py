"""Materialize installed wiring and update the populated native/viewer assembly.

    tools/cad-venv/bin/python hardware/wiring/installed/build.py
    tools/cad-venv/bin/python hardware/wiring/installed/build.py --kernel

The kernel command requires the populated enclosure's explicit fine model.
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
# Run as a script, the wiring is routed on the mesh kernel (`hardware/scripts/meshcad`).
if __name__=='__main__' and '--kernel' not in sys.argv:
    import meshcad
    meshcad.activate()
from hardware.wiring.installed.connections import connections, interfaces, UNUSED, BOUNDARIES
from hardware.wiring.installed.model import STOCK, shape
from hardware.wiring.installed.routes import routed
from hardware.wiring.installed.terminals import Attachments

OUT=ROOT/'hardware/wiring/enclosure-wiring'


def routed_inputs(scene, ea):
    """Resolve the installed route records and their attachment/connection context."""
    at=Attachments(scene,ea)
    at.resolve()
    graph=connections()
    routes=routed(graph,at)
    return at,graph,routes


def compose(scene, ea):
    import cadquery as cq
    at,graph,routes=routed_inputs(scene,ea)
    assembly=cq.Assembly(name='installed-wiring')
    for route in routes:
        stock=STOCK[route.connection.stock]
        s=shape(route,stock['od_mm'])
        assembly.add(s,name='wire-'+route.connection.id,color=cq.Color(*stock['color']))
    from hardware.wiring.installed.terminations import add_terminations
    terminations=add_terminations(assembly,at,graph,routes)
    from hardware.wiring.installed.bundles import add_jackets
    bundles=add_jackets(assembly,at)
    return assembly,_manifest(at,graph,routes,terminations,bundles)


def _manifest(at,graph,routes,terminations,bundles):
    used={id for c in graph for id in (c.start,c.end)}
    return {
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
            'Routes are the selected installed geometry. The manual review checks larger-body clearance; wire-to-wire and wire-to-tube contacts are excluded. Physical harness handling remains separate.',
            'Lengths follow the routed insulated conductor centreline; hidden crimp insertion, cut reserve, sleeve fit and final service slack are separate.',
            'Wire bend radii are reported geometric radii, not manufacturer-qualified minima.',
            'No rigid Faston boot box is imposed on the flexible valve tabs or the pump motor tabs. G/J use an aft exit at the tab engagement region.',
            'Nominal and unlocated terminals remain visible in the graph and manifest; no exact donor termination is invented.',
            'The electrical graph does not qualify grounding, mains isolation, current capacity or energization.',
        ],
    }


def numeric_inputs(scene,ea):
    """Resolve the same installed geometry and facts before any conductor/body build."""
    at,graph,routes=routed_inputs(scene,ea)
    from hardware.wiring.installed.terminations import inputs as termination_inputs
    from hardware.wiring.installed.bundles import inputs as jacket_inputs
    from hardware.wiring.installed.wire_geometry import numbers
    terminations,termination_facts=termination_inputs(at,graph,routes)
    jackets,bundle_facts=jacket_inputs(at)
    return (numbers([r.record()for r in routes],STOCK,components=[*terminations,*jackets]),
            _manifest(at,graph,routes,termination_facts,bundle_facts))


def numeric_source_paths(numbers=None):
    """Loaded repository readers and explicit placement data for the numeric handoff."""
    from hardware.wiring.installed._model_input import QUERY_SOURCES
    paths={Path(module.__file__).resolve() for module in tuple(sys.modules.values())
           if getattr(module,'__file__',None) and str(module.__file__).endswith('.py')}
    paths.update(QUERY_SOURCES)
    paths.update(ROOT/path for path in (
        'hardware/manifold-layout/above-core.json',
        'hardware/manifold-layout/enclosure-box.json',
        'hardware/reference/g-ganen-pump/reference-parameters.json',
        'hardware/reference/g-ganen-pump/under-head-clearance.json',
        'hardware/reference/g-ganen-pump/underside-observation/rigid-underside.json',
    ))
    if numbers is not None:
        paths.update(ROOT/row['step'] for row in numbers.get('components',())
                     if row['kind']=='import')
    return sorted(str(path.relative_to(ROOT)) for path in paths
                  if path.is_relative_to(ROOT) and path.is_file())


def attach(assembly, ea, *, kernel=False):
    """Include wiring in the normal enclosure composition without re-standing it."""
    if kernel:
        import cadquery as cq
        if not getattr(cq,'MESH',False):
            raise ValueError('Kernel wiring attachment requires the mesh assembly path')
        return _defer_kernel(assembly,ea)
    scene={n:(s,c) for n,s,c in ea.ml.placed_leaves(assembly)}
    wires,manifest=compose(scene,ea)
    assembly.add(wires,name='installed-wiring')
    assembly.wiring_body_names=frozenset(child.name for child in wires.children)
    assembly.wiring_model=manifest


def _defer_kernel(assembly,ea,*,output=OUT):
    """Resolve attachments from the physical fine export once its checks finish."""
    assembly.wiring_body_names=frozenset()
    assembly.wiring_kernel_pending={'module':ea,'output':output}


def _attach_kernel(assembly,numbers,manifest,*,output=OUT,sources=()):
    """Attach lazy fine bodies while retaining the producer's paired display files."""
    import cadquery as cq
    import _rust_part
    from meshcad import scene
    if not getattr(cq,'MESH',False):
        raise ValueError('Kernel wiring attachment requires the mesh assembly path')
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    numbers={**numbers,'file_stem':output.name}
    _rust_part.cut('machine','installed-wires',numbers,output.parent,numbers_name=output.name)
    # The file's f64 arrays stay exact and its native backend is built only if queried.
    bodies=scene.load(Path(str(output)+'.step.npz'),snap=False)
    wires=cq.Assembly(name='installed-wiring')
    for name,(shape,rgb) in bodies.items():
        wires.add(shape,name=name,color=cq.Color(*rgb,1.,False) if rgb is not None else None)
    assembly.add(wires,name='installed-wiring')
    assembly.wiring_body_names=frozenset(bodies)
    assembly.wiring_model=manifest
    assembly.wiring_kernel={
        'output':output,
        'sources':[*[ROOT/p for p in sources],
                   *[ROOT/p for p in sorted(_rust_part._READ_TARGETS) if (ROOT/p).is_file()]],
    }


def export_enclosure(assembly, target, *, physical_export=None):
    """One physical export followed by the separately replaceable wiring block."""
    if isinstance(assembly, dict):
        import _machine_export
        return _machine_export.export(assembly, Path(target).parent)
    import cadquery as cq
    from _cadq_export import export_assembly
    from hardware.wiring.installed.step_merge import install
    physical=cq.Assembly(name=assembly.name)
    wires=None
    for child in assembly.children:
        if child.name=='installed-wiring':wires=child
        else:physical.add(child,name=child.name)
    if physical_export is None:
        export_assembly(physical,str(target))
    else:
        physical_export(physical,target)
    pending=getattr(assembly,'wiring_kernel_pending',None)
    if pending is not None:
        from hardware.wiring.installed._model_input import read, measurements
        from check_asse_drain import NAMES as drain_members
        model=Path(str(target)+'.npz')
        assembly.physical_fine_reading=measurements(model,component_names=drain_members)
        numbers,manifest=numeric_inputs(read(model,reading=assembly.physical_fine_reading),pending['module'])
        numbers['physical_fine_model_sha256']=assembly.physical_fine_reading['sha256']
        _attach_kernel(assembly,numbers,manifest,output=pending['output'],
                       sources=numeric_source_paths(numbers))
        del assembly.wiring_kernel_pending
        wires=next(child for child in assembly.children if child.name=='installed-wiring')
    if wires is not None:
        kernel=getattr(assembly,'wiring_kernel',None)
        if kernel is not None:
            output=kernel['output']
            receipt=install(Path(target),Path(str(output)+'.step'),
                            wire_model=Path(str(output)+'.step.npz'))
            manifest=assembly.wiring_model
            manifest['physical_fine_model_sha256']=digest(Path(str(target)+'.npz'))
            manifest['wiring_fine_model_sha256']=receipt['wiring_fine_model']['sha256']
            manifest['wiring_numbers_sha256']=digest(output.with_suffix('.numbers.json'))
            write_manifest(manifest,Path(target),output=output,
                           additional_sources=[Path(__file__).with_name('wire_geometry.py'),
                                               *[ROOT/p for p in numeric_source_paths()],
                                               *kernel['sources']])
            receipt['connection_count']=manifest['connection_count']
            review=output.parent/'installed/integration-review.json'
            review.parent.mkdir(parents=True,exist_ok=True)
            review.write_text(json.dumps(receipt,indent=2)+'\n')
            return
        # Preserve native swept-face orientation through STEP readback.
        export_assembly(wires,str(OUT.with_suffix('.step')),precision_mode=1)
        write_manifest(assembly.wiring_model,Path(target))
        install(Path(target),OUT.with_suffix('.step'))



def export_from_fine(model, target, ea, *, reading=None, output=OUT):
    """Resolve numeric wiring against the finished physical model and append in Rust.

    The fine reader supplies frame/port scalar data. No meshcad assembly is loaded
    and wire STEP/payload bytes are merged without rebuilding physical geometry.
    """
    import _machine_export
    import _rust_part
    from hardware.wiring.installed._model_input import read

    model, target, output = Path(model), Path(target), Path(output)
    numbers, manifest = numeric_inputs(read(model, reading=reading), ea)
    numbers = {**numbers, 'file_stem': output.name,
               'physical_fine_model_sha256': digest(model)}
    output.parent.mkdir(parents=True, exist_ok=True)
    _rust_part.cut('machine', 'installed-wires', numbers, output.parent,
                   numbers_name=output.name)
    receipt = _machine_export.append_wiring(
        target, Path(str(output)+'.step'),
        wire_model=Path(str(output)+'.step.npz'))
    manifest['physical_fine_model_sha256'] = digest(model)
    manifest['wiring_fine_model_sha256'] = receipt['wiring_fine_model']['sha256']
    manifest['wiring_numbers_sha256'] = digest(output.with_suffix('.numbers.json'))
    sources = [ROOT/p for p in numeric_source_paths(numbers)]
    sources.extend(ROOT/p for p in sorted(_rust_part._READ_TARGETS) if (ROOT/p).is_file())
    write_manifest(manifest, target, output=output, additional_sources=sources,
                   physical_sha256=receipt['physical_step_sha256'])
    receipt['connection_count'] = manifest['connection_count']
    review = output.parent/'installed/integration-review.json'
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(json.dumps(receipt, indent=2)+'\n')
    return {'manifest': manifest, 'receipt': receipt}

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def write_manifest(manifest,scene_step,*,output=OUT,additional_sources=(),physical_sha256=None):
    from _realized import code_digest
    # The physical scene digest excludes this wiring subassembly, avoiding a
    # circular hash when the same wiring is materialized a second time.
    if physical_sha256 is None:
        from hardware.wiring.installed.step_merge import base_document
        raw=base_document(scene_step.read_text())
        physical_sha256=hashlib.sha256(raw.encode()).hexdigest()
    manifest['physical_scene_sha256']=physical_sha256
    paths=[Path(__file__),Path(__file__).with_name('connections.py'),
           Path(__file__).with_name('model.py'),Path(__file__).with_name('terminals.py'),
           Path(__file__).with_name('_model_input.py'),
           ROOT/'hardware/scripts/_assembly_model.py',
           ROOT/'hardware/scripts/_realized.py',
           ROOT/'hardware/manifold-layout/enclosure_assembly.rs',
           Path(__file__).with_name('routes.py'),Path(__file__).with_name('retainers.py'),
           Path(__file__).with_name('manifold_bank_routes.py'),
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
           ROOT/'hardware/printed-parts/cold-core/_foam_cap.py',
           ROOT/'hardware/cold-core-layout/_carbonator.py',
           ROOT/'hardware/cold-core-layout/_carbonator_bond.py',
           ROOT/'hardware/assembly/harnesses/j2.json',ROOT/'hardware/assembly/harnesses/j13.json']
    paths.extend(Path(p) for p in additional_sources)
    paths=list(dict.fromkeys(paths))
    manifest['source_sha256']={str(p.relative_to(ROOT)):digest(p) for p in paths}
    manifest['source_code_digest_algorithm']='_realized.code_digest'
    manifest['source_code_digest']={str(p.relative_to(ROOT)):code_digest(p)
                                    for p in paths if p.suffix=='.py'}
    output.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with output.with_suffix('.csv').open('w',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['wire_id','harness','net','from_terminal','to_terminal','awg',
                         'modeled_length_mm','route_status','start_status','end_status','service'])
        for row in manifest['routes']:
            writer.writerow([row['id'],row['harness'],row['net'],row['start'],row['end'],
                             STOCK[row['stock']]['awg'],row['length_mm'],row['route_status'],
                             manifest['terminals'][row['start']]['status'],
                             manifest['terminals'][row['end']]['status'],row['service']])


def read_enclosure(target):
    """Read installed-body measurements from the materialized fine model."""
    model = Path(str(target) + '.npz')
    if model.is_file():
        from hardware.wiring.installed._model_input import read
        return read(model)
    from _cadq_export import import_assembly
    return import_assembly(str(target))


def _kernel_main(target,output,verify_retained=False):
    """Resolve attachment inputs in a native child, then build after that child exits."""
    import subprocess
    import tempfile
    import _rust_part
    import _run_slots
    _rust_part.start()
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='hsm-wiring-inputs-') as temporary:
        handoff=Path(temporary)/'inputs.json'
        command=[sys.executable,str(ROOT/'tools/run.py'),'--cad','--',sys.executable,
                 str(Path(__file__).resolve()),'--numbers-output',str(handoff),
                 '--target',str(target)]
        subprocess.run(command,check=True,**_run_slots.subprocess_kwargs())
        data=json.loads(handoff.read_text())
    # The native process and its shape storage have exited before this kernel run.
    _rust_part.cut('machine','installed-wires',data['numbers'],output,
                   numbers_name='enclosure-wiring')
    from hardware.wiring.installed.step_merge import install
    sources=[Path(__file__).with_name('wire_geometry.py'),
             *[ROOT/p for p in data['sources']],
             *[ROOT/p for p in sorted(_rust_part._READ_TARGETS) if (ROOT/p).is_file()]]
    receipt=install(target,output/'enclosure-wiring.step',verify_retained=verify_retained,
                    wire_model=output/'enclosure-wiring.step.npz')
    data['manifest']['wiring_fine_model_sha256']=receipt['wiring_fine_model']['sha256']
    data['manifest']['wiring_numbers_sha256']=digest(output/'enclosure-wiring.numbers.json')
    write_manifest(data['manifest'],target,output=output/'enclosure-wiring',
                   additional_sources=sources)
    receipt['connection_count']=data['manifest']['connection_count']
    review=output/'installed/integration-review.json'
    review.parent.mkdir(parents=True,exist_ok=True)
    review.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'conductors':data['manifest']['connection_count'],
                      'harnesses':len(data['manifest']['harnesses']),
                      'terminal_status':data['manifest']['terminal_status_counts'],
                      'frame_max_residual_mm':max(r['maximum_extent_residual_mm']
                          for r in data['manifest']['reference_frames'].values())}),flush=True)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--kernel',action='store_true',help='Build from the explicit fine enclosure model')
    mode.add_argument('--numbers-output',type=Path,help=argparse.SUPPRESS)
    parser.add_argument('--target',type=Path,default=ROOT/'hardware/manifold-layout/enclosure-assembly.step')
    parser.add_argument('--output',type=Path,default=OUT.parent)
    parser.add_argument('--verify-retained',action='store_true')
    args=parser.parse_args()
    if args.kernel:
        return _kernel_main(args.target,args.output,args.verify_retained)
    if args.numbers_output is not None:
        import enclosure_assembly as ea
        from hardware.wiring.installed._model_input import read
        model=Path(str(args.target)+'.npz')
        numbers,manifest=numeric_inputs(read(model),ea)
        numbers['file_stem']='enclosure-wiring'
        fine_digest=digest(model)
        numbers['physical_fine_model_sha256']=fine_digest
        manifest['physical_fine_model_sha256']=fine_digest
        args.numbers_output.write_text(json.dumps({'numbers':numbers,'manifest':manifest,
                                                  'sources':numeric_source_paths(numbers)})+'\n')
        return
    import enclosure_assembly as ea
    from _cadq_export import export_assembly
    from hardware.wiring.installed.step_merge import install
    target=args.target
    print('Read populated enclosure',flush=True)
    scene=read_enclosure(target)
    print('Resolve electrical attachments and route every conductor',flush=True)
    wires,manifest=compose(scene,ea)
    output=args.output/'enclosure-wiring'
    args.output.mkdir(parents=True,exist_ok=True)
    write_manifest(manifest,target,output=output)
    export_assembly(wires,str(output.with_suffix('.step')),precision_mode=1)
    print('Install wiring while retaining all physical assembly records and meshes',flush=True)
    receipt=install(target,output.with_suffix('.step'),verify_retained=args.verify_retained)
    receipt['connection_count']=manifest['connection_count']
    review=args.output/'installed/integration-review.json'
    review.parent.mkdir(parents=True,exist_ok=True)
    review.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'conductors':manifest['connection_count'],
                      'harnesses':len(manifest['harnesses']),
                      'terminal_status':manifest['terminal_status_counts'],
                      'frame_max_residual_mm':max(r['maximum_extent_residual_mm'] for r in manifest['reference_frames'].values())}),flush=True)


if __name__=='__main__': main()
