"""Write local solid-infill regions for the cold-core casing and equipment lid.

Run manually after exporting the current pieces. This reads native construction
datums and the current print meshes; it starts no generator, slice or printer.
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
import _reservoir_a_c2 as snap
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
    low, high = spec['base_bounds_mm']
    world = [value for axis in range(3) for value in (low[axis], high[axis])]
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
    row = dict(name='Reservoir A fore direct C2 pair and lid root',
               machine_bounds_mm=native, applied_source_bounds_mm=clipped,
               world_bounds_mm=world, sparse_infill_density='100%',
               sparse_infill_pattern='zig-zag')
    import _cold_core_interface as core
    import _above_core_mounts as mounts
    import _foam_cap as cap
    paths = {'foam-cap-lid-top': stl,
             'foam-cap-bottom': HERE / 'foam-cap-bottom.stl',
             'foam-shell': HERE.parent / 'foam-shell' / 'foam-shell.stl'}
    pieces = {'foam-cap-lid-top': [row], 'foam-cap-bottom': [], 'foam-shell': []}
    mesh_bounds = {}
    for name, path in paths.items():
        points = _mesh.read_stl(path).reshape(-1, 3)
        mesh_bounds[name] = (points.min(axis=0), points.max(axis=0))

    def box(name, label, x, y, half, z0, z1):
        bounds = [x-half, x+half, y-half, y+half, z0, z1]
        lo, hi = mesh_bounds[name]
        clipped = [value for axis in range(3) for value in
                   (max(bounds[2*axis], float(lo[axis])),
                    min(bounds[2*axis+1], float(hi[axis])))]
        pieces[name].append(dict(name=label, machine_bounds_mm=bounds,
            applied_source_bounds_mm=clipped, sparse_infill_density='100%',
            sparse_infill_pattern='zig-zag'))

    root = 3.0
    for index, (x, y) in enumerate(core.attachment_xy_positions, 1):
        box('foam-shell', f'M5 host {index}, both inserts, tail and wall root',
            x, y, core.screw_guard_diameter/2.+root, 0., core.foam_shell_rim_z)
        lo, hi = mesh_bounds['foam-cap-bottom']
        box('foam-cap-bottom', f'M5 head pad {index} and floor/wall root',
            x, y, core.head_cbore_radius+core.wall_thickness+root,
            float(lo[2]), float(hi[2]))
    for index, (x, y) in enumerate(core.lid_attachment_xy_positions, 1):
        box('foam-cap-lid-top', f'M5 head bearing {index} and plate root',
            x, y, core.head_cbore_radius+root, 0., cap.lid_total_height)
    for name in core.deck_mounts:
        top = cap.lid_total_height+core.deck_mount_standoff(name)
        for index, (x, y) in enumerate(core.deck_mount_xy(name), 1):
            box('foam-cap-lid-top', f'{name} insert post {index} and plate root',
                x, y, core.deck_mount_boss_radius+root, 0., top)
    sources = [Path(__file__), Path(snap.__file__), Path(layout.__file__),
               ROOT / 'hardware/manifold-layout/above-core.json',
            HERE.parent / '_reservoir_a_anchors.py', HERE / 'foam_cap.py',
            Path(core.__file__), Path(mounts.__file__), Path(cap.__file__)]
    record = dict(
        scope='Finite infill-only modifiers through the fore C2 shared base, '
              'all M5 casing hosts/head bearings and PCB insert posts, '
              'each with its supporting plate/wall root. No load capacity '
              'or lifetime qualification.',
        use='Manual print preparation for the equipment lid, shell and bottom cap. Each box intersects '
            'existing material and adds no geometry. All other lid walls, infill, '
            'pose, features and support settings retain their current recipe.',
        producer=relative(Path(__file__)),
        coordinate_frames={name: 'Source STEP/STL coordinates before installed '
                           'placement; world_bounds_mm, where present, uses appliance coordinates.'
                           for name in pieces},
        source_sha256={relative(path): sha(path) for path in sources},
        native_artifact_sha256={name: {'.step': sha(path.with_suffix('.step')), '.stl': sha(path)}
                               for name, path in paths.items()},
        part_process_overrides={}, pieces=pieces)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(path=str(args.out), source_bounds_mm=clipped,
                         world_bounds_mm=world, native_artifact_sha256=record['native_artifact_sha256']),
                     indent=2))


if __name__ == '__main__':
    main()
