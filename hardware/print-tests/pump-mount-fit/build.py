"""Isolated pump seat and both rail stops on the production-thickness lid base."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'hardware/scripts'),
               str(ROOT/'hardware/printed-parts/cadlib'),
               str(ROOT/'hardware/printed-parts/cold-core'),
               str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import above_core
import _above_core_mounts as mounts
from _cadq_export import export_step
from print_mesh import write_print_stl

PLATE_THICKNESS = 7.4
OUTER_MARGIN = 3.0


def main():
    parts = HERE/'parts'
    parts.mkdir(parents=True, exist_ok=True)
    datum = mounts.pump_cradle_datums()
    selected = datum['selected']
    cx = datum['centre_world_mm'][0]
    fy = datum['frame']['translation_mm'][1]
    face = above_core.specification()['cap_face_z_mm']
    first, last = selected['motor_band_native_x_mm']
    stop_first = min(p[0] for p in selected['rail_stop_native_x_mm'])
    stop_last = max(p[1] for p in selected['rail_stop_native_x_mm'])
    xa, xb = cx-datum['stock_half_width_mm']-OUTER_MARGIN, cx+datum['stock_half_width_mm']+OUTER_MARGIN
    ya, yb = fy+min(first,stop_first)-OUTER_MARGIN, fy+max(last,stop_last)+OUTER_MARGIN
    plate = cq.Solid.makeBox(xb-xa, yb-ya, PLATE_THICKNESS,
                            cq.Vector(xa,ya,face-PLATE_THICKNESS))
    base = plate.fuse(mounts.pump_cradle()).clean()
    assert base.isValid() and len(base.Solids()) == 1
    translation = (-(xa+xb)/2., -(ya+yb)/2., PLATE_THICKNESS-face)
    base = base.translate(translation)
    seated_cap = mounts.pump_snap_cap().translate(translation)
    cap_overlap = base.intersect(seated_cap).Volume()
    assert cap_overlap < 1.e-7, ('Clip receiving room is occupied',cap_overlap)
    step, stl = parts/'pump-mount-base.step', parts/'pump-mount-base.stl'
    export_step(base, str(step))
    mesh = write_print_stl(base, stl)
    clip = ROOT/'hardware/printed-parts/cold-core/foam-cap/pump-snap-cap.stl'
    published = json.loads((ROOT/'hardware/cad-artifacts.json').read_text())['solids']
    clip_digest = hashlib.sha256(clip.read_bytes()).hexdigest()
    assert clip_digest == published[str(clip.relative_to(ROOT))]
    inputs = ['hardware/printed-parts/cold-core/_above_core_mounts.py',
              'hardware/manifold-layout/above-core.json',
              'hardware/reference/g-ganen-pump/reference-parameters.json']
    old_path = ROOT/'.cache/pump-print/thin-before-pump-mount-base.step'
    comparison = None
    if old_path.exists():
        old = cq.importers.importStep(str(old_path)).val()
        comparison = dict(before_faces=len(old.Faces()),after_faces=len(base.Faces()),
                          before_edges=len(old.Edges()),after_edges=len(base.Edges()),
                          removed_stock_mm3=old.cut(base).Volume(),
                          added_stock_mm3=base.cut(old).Volume())
    report = dict(
        scope='Physical fit trial: current production cradle, continuous hook pockets and broad joined rail-stop stock, on an isolated 7.4 mm lid plate.',
        base=dict(step=str(step.relative_to(ROOT)),stl=str(stl.relative_to(ROOT)),
                  step_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),
                  stl_sha256=hashlib.sha256(stl.read_bytes()).hexdigest(),
                  native_valid=True,solid_count=1,mesh_watertight=bool(mesh.is_watertight),
                  bounds_mm=mesh.bounds.tolist(),plate_thickness_mm=PLATE_THICKNESS,
                  world_to_print_translation_mm=translation),
        clip=dict(stl=str(clip.relative_to(ROOT)),stl_sha256=clip_digest,
                  source='Exact published printable clip, axial end down.',
                  axial_length_mm=selected['snap_band_native_x_mm'][1]-selected['snap_band_native_x_mm'][0],
                  nominal_arch_mm=selected['cap_arch_wall_mm']),
        saddle_band_native_x_mm=selected['motor_band_native_x_mm'],
        solid_end_stock_mm=datum['end_stock_mm'],
        stops_native_x_mm=selected['rail_stop_native_x_mm'],
        fore_stop_height_above_lid_mm=datum['frame']['translation_mm'][2]+selected['rail_stop_native_z_mm']-face,
        rear_stop_height_above_lid_mm=datum['centre_world_mm'][2]-face,
        stop_stock_width_mm=datum['stock_half_width_mm']+selected['rail_stop_contact_native_y_mm'][1],
        continuous_backing_width_mm=datum['stock_half_width_mm']+next(rail['outer_y_mm'] for rail in datum['rail_rooms'] if rail['side'] < 0),
        topology_comparison=comparison,
        seated_cap_overlap_mm3=cap_overlap,
        input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
        physical_fit='Awaiting the pump trial.')
    (HERE/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__ == '__main__':
    main()
