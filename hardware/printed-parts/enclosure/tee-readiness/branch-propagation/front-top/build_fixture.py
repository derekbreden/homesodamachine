#!/usr/bin/env python3
"""Build a measured-branch front-top fixture without touching production shell outputs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
BOX = ROOT/'hardware/manifold-layout/enclosure-box.json'
STEP = HERE/'front-top.step'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--box-sha256', required=True)
    args = parser.parse_args()
    if sha(BOX) != args.box_sha256:
        raise ValueError('Box differs from the completed producer output requested')
    names = subprocess.check_output(
        ['git','ls-files','--cached','--others','--exclude-standard','--','hardware','tools'],
        cwd=ROOT,text=True).splitlines()
    before = {name:sha(ROOT/name) for name in names
              if name.endswith('.py') and (ROOT/name).is_file()}
    sys.path.insert(0,str(ROOT/'hardware/scripts'))
    sys.path.insert(0,str(ROOT/'hardware/printed-parts/enclosure/enclosure'))
    import _box_spec
    import enclosure as enc
    import cadquery as cq
    import trimesh
    box,bounds = _box_spec.read(enc.Box,enc.Bound,(enc.Pack,enc.PortField,enc.Nameplate),path=BOX)
    enc.BOUNDS[:] = bounds
    started = time.perf_counter()
    print('Building current front-top fixture from Box '+args.box_sha256,flush=True)
    piece = enc.build_piece(box,'front','top')
    shape = piece.val()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise ValueError(f'Front-top validity={shape.isValid()}, solids={len(shape.Solids())}')
    os.environ['HSM_SKIP_MESH_PAYLOAD'] = '1'
    enc.export_assembly(enc.one_body(piece,'current-front-top-fixture',enc.PIECE_COLORS['front-top']),str(STEP))
    stl_path = STEP.with_suffix('.stl')
    # The fixture carries a smooth surface, without the production show flutes.
    # Use the ordinary absolute-tolerance body mesh and its quantized Manifold
    # reconciliation: OCC can supply zero-area facets along a touching edge.
    raw_mesh = enc._piece_mesh(shape)
    written_mesh = enc._flute_skin.as_written(raw_mesh)
    surface = trimesh.boolean.union([written_mesh], engine='manifold', check_volume=False)
    mesh_volume_change = abs(surface.volume-written_mesh.volume)
    mesh_bound_change = float(abs(surface.bounds-written_mesh.bounds).max())
    if mesh_volume_change > 1e-6 or mesh_bound_change > 1e-6:
        raise ValueError('Fixture mesh reconciliation changes volume or exterior bounds')
    surface.export(str(stl_path))
    mesh = trimesh.load_mesh(stl_path)
    if not (mesh.is_watertight and mesh.is_winding_consistent
            and mesh.body_count == 1 and mesh.volume > 0
            and enc._flute_skin.non_manifold_edges(mesh) == 0):
        raise ValueError('Front-top STL is not one closed oriented volume')
    native = cq.importers.importStep(str(STEP)).val()
    if not native.isValid() or len(native.Solids()) != 1:
        raise ValueError('Reread native front-top is not one valid solid')
    source_volume,native_volume = shape.Volume(),native.Volume()
    volume_error = abs(native_volume-source_volume)
    source_box,native_box = shape.BoundingBox(),native.BoundingBox()
    bbox_error = max(abs(getattr(source_box,key)-getattr(native_box,key))
                     for key in ('xmin','ymin','zmin','xmax','ymax','zmax'))
    print(f'Native round trip: source volume {source_volume:.12f}, imported {native_volume:.12f}; '
          f'absolute delta {volume_error:.12f}, relative {volume_error/source_volume:.3g}; '
          f'max bound delta {bbox_error:.9g} mm',flush=True)
    # OCC mass properties use adaptive integration; their absolute numerical error
    # scales with a complete enclosure piece. Retain both readings, plus an
    # independent dimensional round-trip check, instead of a fixed micro-volume.
    if volume_error/source_volume > 1e-6 or bbox_error > 1e-5:
        raise ValueError('Native STEP round-trip readings exceed the retained tolerances')
    sources = {}
    for module in tuple(sys.modules.values()):
        name = getattr(module,'__file__',None)
        if not name or Path(name).suffix != '.py':continue
        path = Path(name).resolve()
        if not path.is_relative_to(ROOT) or '/site-packages/' in str(path):continue
        relative = str(path.relative_to(ROOT))
        digest = sha(path)
        if before.get(relative) != digest:raise ValueError('Loaded source changed: '+relative)
        sources[relative] = digest
    if sha(BOX) != args.box_sha256:raise ValueError('Box changed during fixture construction')
    b = native.BoundingBox()
    record = {'status':'measured_branch_front_top_fixture_valid',
              'created_at_utc':datetime.now(timezone.utc).isoformat(),
              'scope':'Current measured-branch tee and SeaFlo-sized Box baseline. G Ganen integration, terminal-ring qualification, final carrier design and print support review remain separate.',
              'assembly_current':False,'production_enclosure_released':False,
              'print_build_up':'+Z','support_toolpath_reviewed':False,
              'command':sys.argv,'source_sha256':dict(sorted(sources.items())),
              'input_sha256':{str(BOX.relative_to(ROOT)):args.box_sha256},
              'step':str(STEP.relative_to(ROOT)),'step_sha256':sha(STEP),
              'stl':str(stl_path.relative_to(ROOT)),'stl_sha256':sha(stl_path),
              'stl_valid':True,'stl_facets':len(mesh.faces),'stl_volume_mm3':float(mesh.volume),
              'stl_surface':'Smooth native fixture; no production show flutes or print release.',
              'mesh_reconciliation':{'method':'ordinary enclosure absolute-tolerance tessellation, float32 quantization and single-body Manifold union',
                  'source_facets':len(raw_mesh.faces),'retained_facets':len(mesh.faces),
                  'volume_delta_mm3':float(mesh_volume_change),'max_bound_delta_mm':mesh_bound_change,
                  'non_manifold_edges':enc._flute_skin.non_manifold_edges(mesh)},
              'valid':native.isValid(),'solids':len(native.Solids()),
              'volume_mm3':native.Volume(),
              'source_volume_mm3':source_volume,'absolute_volume_delta_mm3':volume_error,
              'relative_volume_delta':volume_error/source_volume,'max_bound_delta_mm':bbox_error,
              'round_trip_tolerances':{'relative_volume':1e-6,'bound_delta_mm':1e-5},
              'bbox_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],
              'elapsed_seconds':time.perf_counter()-started}
    (HERE/'fixture.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('status','step_sha256','solids','volume_mm3','elapsed_seconds')},indent=2),flush=True)


if __name__=='__main__':main()
