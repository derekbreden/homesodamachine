"""Manual native reading of the pump snap and its production exports.

Run explicitly after exporting the pieces and the full appliance. This reader is
not called by a build, hook or scorecard. It writes evidence, never production CAD
or printer commands. The two cubic wing poses are geometric states, not FEA.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import math
import os
import re
import struct
import sys


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
ENC = HERE.parent
VOLUME_TOL = 1e-4
AREA_TOL = 1e-4
LINEAR_TOL = 1e-5
MESH_BOUND_TOL = .002
RETIRED = {f'pump-retainer-{side}-{kind}'
           for side in ('left', 'centre', 'right') for kind in ('screw', 'insert')}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def label(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def base(name):
    return re.sub(r'/\d+$', '', name)


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def difference(reference, candidate):
    return dict(removed_mm3=volume(reference.cut(candidate)),
                added_mm3=volume(candidate.cut(reference)),
                maximum_bound_delta_mm=max(abs(a-b) for a, b in zip(
                    bounds(reference), bounds(candidate))))


def same_shape(reading):
    return (reading['removed_mm3'] <= VOLUME_TOL
            and reading['added_mm3'] <= VOLUME_TOL
            and reading['maximum_bound_delta_mm'] <= LINEAR_TOL)


def payload(path, body=None):
    """Read the member census and, when requested, only one body's positions."""
    import numpy as np

    positions = []
    with Path(path).open('rb') as source:
        size = struct.unpack('<I', source.read(4))[0]
        header = json.loads(source.read(size))
        if header.get('v') != 3:
            raise ValueError(f'{path}: current source-bearing payload required')
        start = 4 + size
        for mesh in header['meshes']:
            if body is not None and base(mesh['name']) == body:
                offset, count = mesh['pos']
                source.seek(start + offset)
                positions.append(np.frombuffer(source.read(count*4), dtype='<f4').reshape(-1, 3))
    return header, positions


def array_bounds(arrays):
    import numpy as np

    if not arrays:
        raise ValueError('No geometry was read for the named body')
    low = np.stack([row.min(axis=0) for row in arrays]).min(axis=0)
    high = np.stack([row.max(axis=0) for row in arrays]).max(axis=0)
    return [float(value) for axis in range(3) for value in (low[axis], high[axis])]


def glb(path, body):
    """Read actual float32 vertices, rather than trusting accessor min/max metadata."""
    import numpy as np

    with Path(path).open('rb') as source:
        magic, version, length = struct.unpack('<III', source.read(12))
        if magic != 0x46546C67 or version != 2 or length != Path(path).stat().st_size:
            raise ValueError(f'{path}: malformed GLB header')
        size, kind = struct.unpack('<II', source.read(8))
        if kind != 0x4E4F534A:
            raise ValueError(f'{path}: GLB JSON chunk is absent')
        scene = json.loads(source.read(size))
        size, kind = struct.unpack('<II', source.read(8))
        if kind != 0x004E4942:
            raise ValueError(f'{path}: embedded GLB buffer is absent')
        binary = source.read(size)
    nodes = [node for node in scene['nodes'] if 'mesh' in node]
    positions, transforms = [], []
    for node in nodes:
        if base(node['name']) != body:
            continue
        transforms.append({key: node[key] for key in ('matrix', 'translation', 'rotation', 'scale')
                           if key in node})
        for primitive in scene['meshes'][node['mesh']]['primitives']:
            accessor = scene['accessors'][primitive['attributes']['POSITION']]
            if (accessor['componentType'] != 5126 or accessor['type'] != 'VEC3'
                    or 'sparse' in accessor):
                raise ValueError('The scene positions are not ordinary float32 VEC3 values')
            view = scene['bufferViews'][accessor['bufferView']]
            offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
            positions.append(np.ndarray((accessor['count'], 3), dtype='<f4', buffer=binary,
                                        offset=offset, strides=(view.get('byteStride', 12), 4)))
    return scene, nodes, positions, transforms


def run(args, report):
    import numpy as np

    for directory in (ROOT / 'hardware/scripts', ENC):
        sys.path.insert(0, str(directory))
    os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')
    import cadquery as cq
    import enclosure as e
    import _fixed_pump_mount as mount
    import _box_spec
    from _cadq_export import import_assembly, import_step
    from materialize_pump_cartridge import _declared_box

    def bind(path, kind):
        path = Path(path).resolve()
        row = dict(path=label(path), sha256=sha(path))
        report[kind].append(row)
        return row

    def check(name, passed, **reading):
        row = dict(check=name, pass_=bool(passed), **reading)
        row['pass'] = row.pop('pass_')
        report['checks'].append(row)
        print(f'{name}: {"pass" if passed else "FAIL"}', flush=True)
        return passed

    baseline = json.loads(args.baseline.read_text())
    bind(args.baseline, 'sources')
    for path in (Path(__file__), ENC / '_fixed_pump_mount.py', ENC / 'enclosure.py',
                 ROOT / 'hardware/manifold-layout/enclosure_assembly.py',
                 ROOT / 'hardware/manifold-layout/_scorecard.py',
                 ROOT / 'hardware/assembly/scenes/_scenes.py',
                 ROOT / 'hardware/assembly/scenes/render_scenes.py',
                 ROOT / 'hardware/scripts/flute_payload.py',
                 ROOT / 'hardware/scripts/_cadq_export.py',
                 ROOT / 'hardware/scripts/_box_spec.py'):
        bind(path, 'sources')
    box, _bound, box_path = _declared_box(_box_spec, e)
    bind(box_path, 'sources')
    d, s = mount.datums(e, box), mount.snap_datums(e, box)
    report['datums'] = dict(carrier=d, snap=s, relaxed_tip_spread_mm=mount.RELAXED_SPREAD,
                            seated_tip_spread_mm=mount.SEATED_SPREAD)

    retainer_path = ENC / 'enclosure-pump-retainer.step'
    front_path = ENC / 'enclosure-front-top.step'
    for step in (retainer_path, front_path):
        native_id = bind(step, 'artifacts')
        bind(step.with_suffix('.stl'), 'artifacts')
        mesh = step.with_suffix('.step.mesh')
        bind(mesh, 'artifacts')
        header, _positions = payload(mesh)
        check(f'{step.stem} viewer lineage', header.get('src') == native_id['sha256'],
              native_sha256=native_id['sha256'], viewer_source_sha256=header.get('src'))

    relaxed = import_step(retainer_path).val()
    front = import_step(front_path).val()
    expected_relaxed = mount.retainer(e, box).val()
    seated = mount.retainer(e, box, seated=True).val()
    for name, shape in (('printed relaxed retainer', relaxed), ('seated retainer', seated),
                        ('front-top', front)):
        check(name + ' native body', shape.isValid() and len(shape.Solids()) == 1,
              valid=shape.isValid(), solids=len(shape.Solids()),
              bounds_mm=bounds(shape), volume_mm3=volume(shape))
    reading = difference(expected_relaxed, relaxed)
    check('printed STEP matches relaxed source', same_shape(reading), **reading)
    for name, shape, spread in (('relaxed', relaxed, mount.RELAXED_SPREAD),
                                ('seated', seated, mount.SEATED_SPREAD)):
        b = bounds(shape)
        expected = s['hook_outer_x'] + spread
        error = max(abs(b[0]+expected), abs(b[1]-expected),
                    abs(b[2]-d['y0']), abs(b[3]-d['y1']), abs(b[4]-s['floor_z']))
        check(name + ' tip pose and common end planes', error <= LINEAR_TOL,
              maximum_error_mm=error, expected_tip_abs_x_mm=expected,
              full_y_mm=[d['y0'], d['y1']])

    profile_rows = []
    for row in baseline['preserved_pump_profile_functions']:
        tree = ast.parse((ROOT / row['path']).read_text())
        node = next(node for node in tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == row['function'])
        digest = hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
        profile_rows.append(dict(**row, current_ast_sha256=digest,
                                 unchanged=digest == row['ast_sha256']))
    cutters = mount.lower_voids(e, box)
    cut_rows = [dict(well=index, relaxed_material_in_void_mm3=volume(relaxed.intersect(cutter)),
                    seated_material_in_void_mm3=volume(seated.intersect(cutter)))
                for index, cutter in enumerate(cutters, 1)]
    check('fitted pump profile source and empty lower wells',
          all(row['unchanged'] for row in profile_rows)
          and all(max(row['relaxed_material_in_void_mm3'],
                      row['seated_material_in_void_mm3']) <= VOLUME_TOL for row in cut_rows),
          preserved_profile_functions=profile_rows, native_void_readings=cut_rows,
          scope='Profile construction is unchanged from the frozen source commit; '
                'the current printed and seated solids keep those inverse spaces empty.')

    for side in (-1., 1.):
        xa, xb = sorted((side*(s['wing_inner_x']-.001),
                         side*(s['hook_outer_x']+mount.RELAXED_SPREAD+1.)))
        wing = relaxed.intersect(e._ybox(xa, xb, d['y0']-1., d['y1']+1.,
                                        s['floor_z']-.01, s['root_z']-.001))
        foot = wing.intersect(e._ybox(xa, xb, d['y0']-1., d['y1']+1.,
                                      s['floor_z']-.01, s['hook_step_z']-.001))
        wb, fb = bounds(wing), bounds(foot)
        error = max(abs(b[index]-d[key]) for b in (wb, fb)
                    for index, key in ((2, 'y0'), (3, 'y1')))
        check(f'{side:+g} wing and hook share full Y span', error <= LINEAR_TOL,
              wing_bounds_mm=wb, foot_bounds_mm=fb, maximum_y_error_mm=error)

    overlap = volume(front.intersect(seated))
    check('seated retainer and receiver have no material overlap', overlap <= VOLUME_TOL,
          shared_volume_mm3=overlap)
    floor_faces = []
    floor_gaps = []
    y_air = []
    for side in (-1., 1.):
        xa, xb = sorted((side*s['receiver_inner_x'], side*s['receiver_back_x']))
        faces = [face for face in front.Faces()
                 if face.geomType() == 'PLANE'
                 and max(abs(bounds(face)[i]-s['receiver_floor_z']) for i in (4, 5)) <= LINEAR_TOL
                 and bounds(face)[0] >= xa-LINEAR_TOL
                 and bounds(face)[1] <= xb+LINEAR_TOL
                 and bounds(face)[2] >= s['receiver_y0']-LINEAR_TOL
                 and bounds(face)[3] <= s['receiver_y1']+LINEAR_TOL]
        area = sum(face.Area() for face in faces)
        expected_area = ((s['receiver_back_x']-s['receiver_inner_x'])
                         * (s['receiver_y1']-s['receiver_y0']-(s['port_y1']-s['port_y0'])))
        floor_faces.append(dict(side=side, faces=len(faces), area_mm2=area,
                                expected_area_mm2=expected_area,
                                native_face_bounds_mm=[bounds(face) for face in faces]))
        floor_gaps.append(bounds(seated)[4]-faces[0].Center().z if faces else None)
        if faces:
            y_air.extend((bounds(seated)[2]-min(bounds(face)[2] for face in faces),
                          max(bounds(face)[3] for face in faces)-bounds(seated)[3]))
    check('receiver bearing floors and nominal clearances',
          all(row['faces'] and abs(row['area_mm2']-row['expected_area_mm2']) <= AREA_TOL
              for row in floor_faces)
          and all(value is not None and abs(value-.15) <= LINEAR_TOL for value in floor_gaps)
          and len(y_air) == 4 and all(abs(value-.25) <= LINEAR_TOL for value in y_air),
          floor_planes=floor_faces, floor_clearance_mm=floor_gaps, y_end_clearance_mm=y_air,
          scope='Nominal CAD clearances; printing variation and loaded displacement are unmeasured.')

    cy = (s['port_y0']+s['port_y1'])/2.
    constant = s['receiver_back_x']+s['receiver_roof_z']
    roof_rows = []
    for side in (-1., 1.):
        points = [(side*x, cy, constant-x) for x in
                  (s['receiver_inner_x'], s['receiver_back_x'], s['port_outer_x'])]
        candidates = []
        for face in front.Faces():
            if face.geomType() != 'PLANE':
                continue
            normal = face.normalAt()
            if (abs(normal.y) > LINEAR_TOL or abs(abs(normal.x)-abs(normal.z)) > LINEAR_TOL
                    or abs(normal.x) < .5):
                continue
            errors = [face.distance(cq.Vertex.makeVertex(*point)) for point in points]
            if max(errors) <= LINEAR_TOL:
                candidates.append(dict(normal=normal.toTuple(), bounds_mm=bounds(face),
                                       maximum_point_distance_mm=max(errors)))
        roof_rows.append(dict(side=side, profile_points_mm=points, continuous_faces=candidates))
    check('continuous 45 degree pocket and screwdriver roof',
          all(len(row['continuous_faces']) == 1 for row in roof_rows), roof_faces=roof_rows)

    # Subtract only the two moving wings. Tool contact on a wing is intentional;
    # interference with the fixed carrier or fixed receiver is not.
    carrier = seated
    for side in (-1., 1.):
        carrier = carrier.cut(mount._wing(e, box, side, mount.SEATED_SPREAD))
    radius = 3.31/2.
    cylinder = cq.Solid.makeCylinder(radius, 66., cq.Vector(0., 0., -58.), cq.Vector(0., 0., 1.))
    poses = [(0., float(offset)) for offset in np.linspace(-15., 0., 16)]
    poses += [(float(angle), 0.) for angle in np.linspace(0., 34., 18)]
    tool_rows = []
    for side in (-1., 1.):
        pivot = np.array([side*s['port_outer_x'], cy, s['receiver_z0']])
        readings = []
        for angle, offset in poses:
            theta = math.radians(angle)
            normal = np.array([side*math.cos(theta), 0., math.sin(theta)])
            axis = np.array([-side*math.sin(theta), 0., math.cos(theta)])
            origin = pivot-radius*normal+offset*axis
            tool = cylinder.rotate((0., 0., 0.), (0., 1., 0.), -side*angle).translate(tuple(origin))
            readings.append(dict(angle_deg=angle, insertion_offset_mm=offset,
                                 fixed_receiver_overlap_mm3=volume(tool.intersect(front)),
                                 fixed_carrier_overlap_mm3=volume(tool.intersect(carrier))))
        tool_rows.append(dict(side=side, pivot_mm=pivot.tolist(), sampled_poses=readings,
                              maximum_fixed_receiver_overlap_mm3=max(
                                  row['fixed_receiver_overlap_mm3'] for row in readings),
                              maximum_fixed_carrier_overlap_mm3=max(
                                  row['fixed_carrier_overlap_mm3'] for row in readings)))
    minimum_roof_z = constant-s['port_outer_x']
    tool_maximum_z = s['receiver_z0']+8.
    check('centered 3.31 mm tool approach and lever samples',
          all(max(row['maximum_fixed_receiver_overlap_mm3'],
                  row['maximum_fixed_carrier_overlap_mm3']) <= VOLUME_TOL for row in tool_rows)
          and minimum_roof_z-tool_maximum_z >= 1.65-LINEAR_TOL,
          envelope_diameter_mm=2*radius, usable_y_air_each_mm=(s['port_y1']-s['port_y0']-2*radius)/2.,
          angle_range_deg=[0., 34.], insertion_offset_range_mm=[-15., 0.],
          corbel_vertical_separation_bound_mm=minimum_roof_z-tool_maximum_z, sides=tool_rows,
          scope='Discrete native samples of a conservative cylindrical tool envelope with '
                'front-top loose and its underside open. No continuous swept-volume proof, '
                'tip pressure, release force or simultaneous retraction of both wing ends.')

    assembly_path = args.assembly.resolve()
    assembly_id = bind(assembly_path, 'artifacts')
    mesh_path = assembly_path.with_suffix('.step.mesh')
    bind(mesh_path, 'artifacts')
    mesh_header, installed_positions = payload(mesh_path, 'enclosure-pump-retainer')
    bind(args.glb, 'artifacts')
    _scene, nodes, scene_positions, retainer_transforms = glb(args.glb, 'enclosure-pump-retainer')
    print('Reading current named native appliance bodies', flush=True)
    native = {name: shape for name, (shape, _colour) in import_assembly(assembly_path).items()}
    expected_names = set(baseline['full_appliance_members'])-RETIRED
    payload_names = {base(row['name']) for row in mesh_header['meshes']}
    scene_names = {base(node['name']) for node in nodes}
    expected_scene = set(baseline['pump_mount_members'])-RETIRED
    check('native appliance and viewer preserve members except six pump fasteners',
          set(native) == expected_names and payload_names == expected_names
          and mesh_header.get('src') == assembly_id['sha256'],
          native_count=len(native), expected_count=len(expected_names), viewer_count=len(payload_names),
          missing_native=sorted(expected_names-set(native)), extra_native=sorted(set(native)-expected_names),
          missing_viewer=sorted(expected_names-payload_names), extra_viewer=sorted(payload_names-expected_names),
          retired_hardware_found=sorted(RETIRED & (set(native) | payload_names)),
          viewer_source_sha256=mesh_header.get('src'),
          other_hardware_preserved=sorted(set(baseline['other_hardware_members']) & set(native) & payload_names))
    check('installation GLB preserves members except six pump fasteners', scene_names == expected_scene,
          expected_count=len(expected_scene), current_count=len(scene_names),
          missing=sorted(expected_scene-scene_names), extra=sorted(scene_names-expected_scene),
          retired_hardware_found=sorted(RETIRED & scene_names))
    for name, reference in (('enclosure-front-top', front), ('enclosure-pump-retainer', seated)):
        candidate = native[name]
        reading = difference(reference, candidate)
        check(name + ' is exact installed native geometry', same_shape(reading)
              and candidate.isValid() and len(candidate.Solids()) == 1,
              valid=candidate.isValid(), solids=len(candidate.Solids()), **reading)
    expected_bounds = bounds(seated)
    mesh_bounds, glb_bounds = array_bounds(installed_positions), array_bounds(scene_positions)
    mesh_error = max(abs(a-b) for a, b in zip(expected_bounds, mesh_bounds))
    glb_error = max(abs(a-b) for a, b in zip(expected_bounds, glb_bounds))
    front_transforms = [{key: node[key] for key in ('matrix', 'translation', 'rotation', 'scale')
                         if key in node} for node in nodes if base(node['name']) == 'enclosure-front-top']
    check('viewer and GLB carry the seated wing pose', mesh_error <= MESH_BOUND_TOL
          and glb_error <= MESH_BOUND_TOL and bool(front_transforms)
          and all(row == front_transforms[0] for row in retainer_transforms),
          native_seated_bounds_mm=expected_bounds, viewer_bounds_mm=mesh_bounds,
          glb_local_bounds_mm=glb_bounds, maximum_viewer_bound_error_mm=mesh_error,
          maximum_glb_bound_error_mm=glb_error, common_view_transforms=retainer_transforms)

    changed = [row['path'] for kind in ('sources', 'artifacts') for row in report[kind]
               if sha(ROOT / row['path']) != row['sha256']]
    check('all inputs remain unchanged during the reading', not changed, changed_paths=changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=HERE / 'baseline-hardware.json')
    parser.add_argument('--assembly', type=Path,
                        default=ROOT / 'hardware/manifold-layout/enclosure-assembly.step')
    parser.add_argument('--glb', type=Path, default=ROOT / 'hardware/assembly/scenes/glb/pump-mount.glb')
    parser.add_argument('--out', type=Path, default=HERE / 'native-review.json')
    args = parser.parse_args()
    report = dict(scope='Manual current-export geometry and installation identity reading. '
                  'The cubic relaxed/seated wing forms are geometric poses, not FEA. '
                  'No printed fit, load capacity, creep, lifetime, release force or '
                  'full-Y retraction qualification is established.',
                  tolerances=dict(volume_mm3=VOLUME_TOL, native_area_mm2=AREA_TOL,
                                  native_linear_mm=LINEAR_TOL,
                                  viewer_bounds_mm=MESH_BOUND_TOL),
                  sources=[], artifacts=[], checks=[])
    try:
        run(args, report)
        report['status'] = 'pass' if all(row['pass'] for row in report['checks']) else 'fail'
    except Exception as error:
        report.update(status='error', error=f'{type(error).__name__}: {error}')
        print(report['error'], file=sys.stderr, flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(args.out.suffix+'.tmp')
    temporary.write_text(json.dumps(report, indent=2)+'\n')
    temporary.replace(args.out)
    print(f'{label(args.out)}: {report["status"]}', flush=True)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
