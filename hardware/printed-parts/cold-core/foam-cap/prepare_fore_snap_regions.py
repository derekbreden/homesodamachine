"""Write the fore snap receiver's local infill-only print specification.

Run manually after exporting the current lid. This reads source dimensions and
the current STL without importing a CAD kernel, slicing or contacting a printer.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import sys


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
PREPARATION = ROOT / 'hardware/printed-parts/enclosure/trial-preparation'
sys.path[:0] = [str(HERE.parent), str(ROOT / 'hardware/manifold-layout'), str(PREPARATION)]
import _reservoir_a_snap as snap
import above_core as layout
import _mesh


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE / 'fore-snap-print-regions.json')
    args = parser.parse_args()
    spec = snap.specification()
    cx, cy, cz = spec['centre_world_mm']
    half_x, half_y = spec['wing_outer_x_mm'], spec['station_length_mm']/2
    lid_face = layout.specification()['cap_face_z_mm']
    world = [cx-half_x, cx+half_x, cy-half_y, cy+half_y,
             min(cz+spec['base_floor_z_mm'], lid_face-spec['wall_mm']),
             cz+spec['base_top_z_mm']]
    corners = [layout.world_to_cap(point) for point in
               itertools.product(*[world[i:i+2] for i in (0, 2, 4)])]
    native = [value for axis in range(3)
              for value in (min(point[axis] for point in corners),
                            max(point[axis] for point in corners))]
    stl = HERE / 'foam-cap-lid-top.stl'
    step = stl.with_suffix('.step')
    vertices = _mesh.read_stl(stl).reshape(-1, 3)
    low, high = vertices.min(axis=0), vertices.max(axis=0)
    clipped = [value for axis in range(3) for value in
               (max(native[2*axis], float(low[axis])),
                min(native[2*axis+1], float(high[axis])))]
    if any(clipped[i+1] <= clipped[i] for i in (0, 2, 4)):
        raise ValueError('The fore receiver/root modifier is outside the current lid bounds')
    row = dict(name='Reservoir A fore snap receiver, axial shoulders and lid root',
               machine_bounds_mm=native, applied_source_bounds_mm=clipped,
               world_bounds_mm=world, sparse_infill_density='100%',
               sparse_infill_pattern='zig-zag')
    sources = [Path(__file__), Path(snap.__file__), Path(layout.__file__),
               ROOT / 'hardware/manifold-layout/above-core.json',
               HERE.parent / '_reservoir_a_anchors.py', HERE / 'foam_cap.py']
    record = dict(
        scope='One infill-only modifier through the existing fore snap receiver, its '
              'full axial shoulders and one wall into the lid root. No load capacity '
              'or lifetime qualification.',
        use='Manual print preparation for foam-cap-lid-top only. The box intersects '
            'existing material and adds no geometry. All other lid walls, infill, '
            'pose, features and support settings retain their current recipe.',
        producer=relative(Path(__file__)),
        coordinate_frames={'foam-cap-lid-top': 'Source STEP/STL coordinates before '
                           'the installed cap half-turn; world_bounds_mm uses appliance coordinates.'},
        source_sha256={relative(path): sha(path) for path in sources},
        native_artifact_sha256={'foam-cap-lid-top': {'.step': sha(step), '.stl': sha(stl)}},
        part_process_overrides={}, pieces={'foam-cap-lid-top': [row]})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(path=str(args.out), source_bounds_mm=clipped,
                         world_bounds_mm=world, native_artifact_sha256=record['native_artifact_sha256']),
                     indent=2))


if __name__ == '__main__':
    main()
