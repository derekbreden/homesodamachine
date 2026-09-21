"""One Beduan socket panel using the enclosure's actual four horizontal bores."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
sys.path[:0] = [str(ROOT / 'hardware/scripts'),
               str(ROOT / 'hardware/printed-parts/enclosure/enclosure')]

import cadquery as cq
import enclosure as enc
from _cadq_export import export_assembly
from _material_base import M_PETGF_BLACK, one_body
from flute_payload import cut


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def function_digest(function):
    tree = ast.parse(inspect.getsource(function))
    return hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()


def build():
    seat, tray = enc._seat, enc._valve_tray
    width = 2 * (seat.seat_half_x + tray.MARGIN)
    height = tray.height(((0.0, 0.0),))
    station_z = height / 2
    face_y = seat.seat_top_z
    body = enc._ybox(-width / 2, width / 2,
                     face_y - tray.THICK, face_y, 0.0, height)
    at = cq.Location(cq.Vector(0, 0, station_z))
    turn = cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90)
    body = body.cut(tray.build_body_clearance().val().moved(turn).moved(at))
    for socket in enc._valve_socket_cutters(0.0, 1, 0.0, station_z):
        body = body.cut(socket)
    body = body.cut(tray.build_port_channel(height + 2).val().moved(turn).moved(at))
    valve = seat.valve.build_beduan_solenoid().val().moved(turn).moved(at)
    return body.clean(), valve, {'width_mm': width, 'height_mm': height,
        'thickness_mm': tray.THICK, 'bearing_face_y_mm': face_y,
        'socket_floor_y_mm': seat.socket_floor_z,
        'socket_diameter_mm': 2 * seat.socket_radius,
        'socket_depth_mm': seat.socket_depth(),
        'post_pitch_x_mm': 2 * seat.corner_inset_x,
        'post_pitch_z_mm': 2 * seat.corner_inset_y,
        'station_z_mm': station_z}


def main():
    body, valve, dimensions = build()
    errors = []
    if not body.isValid() or len(body.Solids()) != 1:
        errors.append('Socket panel must be one valid solid.')
    readings = []
    for distance in (20.0, 10.0, 5.2, 2.0, 0.0):
        overlap = body.intersect(valve.translate((0.0, distance, 0.0))).Volume()
        readings.append({'valve_outward_offset_mm': distance,
                         'interference_mm3': overlap})
        if overlap > 1e-5:
            errors.append(f'Valve interference at {distance:g} mm: {overlap:g} mm3')
    if errors:
        raise ValueError(errors)
    name = 'valve-socket-fit'
    step, stl = HERE / (name + '.step'), HERE / (name + '.stl')
    cq.exporters.export(body, str(stl), tolerance=0.04, angularTolerance=0.08)
    export_assembly(one_body(cq.Workplane(obj=body), name, M_PETGF_BLACK), str(step))
    cut(step, stl)
    import trimesh
    mesh = trimesh.load_mesh(stl)
    if not mesh.is_watertight or len(mesh.split()) != 1:
        raise ValueError('Printed mesh must be one closed body.')
    functions = (enc._valve_socket_cutters, enc._teardrop_y,
                 enc._valve_tray.build_body_clearance, enc._valve_tray.build_port_channel)
    report = {'status': 'native_socket_panel_checks_pass', 'physical_fit_tested': False,
        'scope': 'Beduan post/socket and bearing-face fit only. No carrier, tee, tube or complete enclosure release.',
        'dimensions': dimensions, 'native_valve_insertion_samples': readings,
        'print_orientation': 'Enclosure +Z up; four socket axes horizontal on Y; port channel vertical and open at both ends.',
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            Path(__file__), Path(enc._seat.__file__), Path(enc._seat.valve.__file__),
            Path(enc._valve_tray.__file__), Path(enc.fits.__file__))},
        'production_function_ast_sha256': {f.__module__ + '.' + f.__name__: function_digest(f) for f in functions},
        'artifacts': {str(p.relative_to(ROOT)): sha(p) for p in (step, stl, step.with_suffix('.step.mesh'))},
        'mesh_watertight': True, 'mesh_bodies': 1, 'triangles': len(mesh.faces),
        'nominal_radial_clearance_mm': enc._seat.socket_clearance,
        'retention_qualified': False,
        'physical_readings_required': ['Full insertion of all four posts without reaming.',
            'Broad body bearing face seated with no rocking.',
            'Fit on the other received valves.',
            'Whether the valve remains seated when the panel faces down.'],
        'errors': errors}
    (HERE / 'geometry-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'dimensions': dimensions,
                      'triangles': report['triangles']}, indent=2))


if __name__ == '__main__':
    main()
