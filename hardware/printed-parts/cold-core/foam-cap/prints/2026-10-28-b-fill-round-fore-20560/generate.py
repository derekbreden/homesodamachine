"""Crop the production cup and lid with the fore clamp row at Y205.60."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
OUT = ROOT/'.cache/prints/2026-10-28-b-fill-round-fore-20560'
sys.path[:0] = [str(ROOT/'hardware'/p) for p in (
    'scripts', 'manifold-layout', 'printed-parts/cold-core', 'printed-parts/cadlib')]
import above_core
import _above_core_mounts as mounts
import _cold_core_interface as core
import _reservoir_b_fill as fill
from _show_skin import write_bed_file


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(leaves):
    data = fill.passage()
    low, high = data['stock_min_world_mm'], data['stock_max_world_mm']
    crop = cq.Solid.makeBox(*(b-a for a, b in zip(low, high)), cq.Vector(*low))
    height = core.foam_cap_height-core.head_pad_height
    frame = above_core.frame_location(above_core.cap_lid_pose())
    directory = OUT/'round20560'
    directory.mkdir(parents=True, exist_ok=True)
    record = {'scope': 'Local coupons cropped from the production Y205.60 cap leaves.',
              'world_crop_mm': [low, high], 'generator_sha256': sha(Path(__file__)),
              'clamp_stations': data['clamp_stations'],
              'roof_allowance_mm': data['supported_roof_allowance_mm'],
              'normal_seating_allowance_mm': data['lid_bottom_world_z_mm']-data['cup_top_world_z_mm'],
              'production_print_up_retained': True, 'source_step_sha256': {}, 'variants': {}}
    row = {'fore_screw_y_mm': data['clamp_stations'][1]['axis_world_xy_mm'][1], 'pieces': {}}
    worlds = []
    for kind, name in [('cup', 'foam-cap-top'), ('lid', 'foam-cap-lid-top')]:
        source = leaves/(name+'.step')
        local = cq.importers.importStep(str(source)).val()
        world = local.translate((0, 0, -height if kind=='cup' else 0)).moved(frame)
        world = world.intersect(crop).clean()
        assert world.isValid() and len(world.Solids())==1
        worlds.append(world)
        local = mounts.world_shape_in_cap(world)
        if kind=='cup':
            local = local.translate((0, 0, height))
        step, stl = directory/(kind+'.step'), directory/(kind+'.stl')
        cq.exporters.export(local, str(step))
        write_bed_file(local, stl)
        row['pieces'][kind] = {'valid': True, 'solids': 1, 'volume_mm3': world.Volume(),
            'step': str(step.relative_to(ROOT)), 'step_sha256': sha(step),
            'stl': str(stl.relative_to(ROOT)), 'stl_sha256': sha(stl)}
        record['source_step_sha256'][name] = sha(source)
    row['cup_lid_overlap_mm3'] = max(0., worlds[0].intersect(worlds[1]).Volume())
    record['variants']['round20560'] = row
    (HERE/'geometry.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--leaves', type=Path,
        default=ROOT/'hardware/printed-parts/cold-core/foam-cap')
    main(parser.parse_args().leaves.resolve())
