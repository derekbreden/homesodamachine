"""Interface-preserving east-wall relief for the held Water5 removable key.

The received key's outer cylindrical bearing defines a quarter-millimetre
running envelope. A twelve-millimetre outward normal entry sweeps that
envelope. Its exact split plane protects the whole fixed seat and its blind
fasteners. The cutter belongs only to the east nine-millimetre wall.

``make_pocket(key, seat, properties)`` returns a cutter and native receipt.
The command exports this tool only; every component and parent stays held.
"""
from io import BytesIO
from pathlib import Path
import hashlib
import json
import math
import sys

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopTools import TopTools_ListOfShape

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
OUT = ROOT / '.cache/pump-first-layout/structure/water5-key-pocket'
sys.path[:0] = [str(STUDY), str(HERE)]
from audit import bbox
from evidence_binding import content_sha256
from received_native import full_material_coverage, material_common
from assemble_prints import joined


def _native_common(left, right):
    operation = BRepAlgoAPI_Common()
    arguments = TopTools_ListOfShape()
    arguments.Append(left.copy(mesh=False).wrapped)
    tools = TopTools_ListOfShape()
    tools.Append(right.copy(mesh=False).wrapped)
    operation.SetArguments(arguments)
    operation.SetTools(tools)
    operation.SetFuzzyValue(0.)
    operation.SetRunParallel(True)
    operation.Build()
    if not operation.IsDone():
        raise ValueError('Independent exact pocket Common did not complete')
    raw = operation.Shape()
    if raw.IsNull():
        return cq.Compound.makeCompound([])
    result = cq.Shape.cast(raw)
    if any(not s.isValid() for s in result.Solids()):
        raise ValueError('Invalid independent pocket Common material')
    return result


def _world_box(location, x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0,
                            cq.Vector(x0, y0, z0)).moved(location)


def make_pocket(key, seat, properties, radial_air_mm=.25,
                outward_entry_mm=12., wall_x_mm=(98.5, 107.5)):
    """Return the exact owner-scoped cutter and complete-seat preservation.

    The designed seat/key split is an intentional planar bearing interface.
    It is preserved with zero material removal. The surrounding wall has
    0.25 mm radial and axial running clearance to the curved key bearing.
    Every received key ear is checked as part of the same full-key sweep.
    """
    if not key.isValid() or len(key.Solids()) != 1:
        raise ValueError('One valid held removable key is required')
    if not seat.isValid() or len(seat.Solids()) != 1:
        raise ValueError('One valid held fixed seat is required')
    if radial_air_mm != .25 or outward_entry_mm != 12.:
        raise ValueError('Selected pocket binds0.25mm running air and12mm entry')
    centre = cq.Vector(*properties['centre_mm'])
    normal = cq.Vector(*properties['normal']).normalized()
    axis = cq.Vector(*properties['tube_axis']).normalized()
    if abs(axis.z - 1) > 1e-8 or abs(normal.z) > 1e-8:
        raise ValueError('Selected key uses a vertical tube and horizontal split normal')
    radial = normal.cross(axis).normalized()
    location = cq.Location(cq.Plane(origin=centre, xDir=normal, normal=radial))
    split = properties['split_local_mm']
    length = properties['bearing_length_mm']
    expected_radius = properties['bore_radius_mm'] + properties['radial_stock_mm']
    outer_faces = []
    for index, face in enumerate(key.Faces()):
        if face.geomType() != 'CYLINDER':
            continue
        cylinder = BRepAdaptor_Surface(face.wrapped).Cylinder()
        radius = cylinder.Radius()
        direction = cylinder.Axis().Direction()
        origin = cylinder.Location()
        if (abs(radius - expected_radius) < 1e-6
                and abs(abs(direction.Z()) - 1) < 1e-8
                and math.hypot(origin.X() - centre.x, origin.Y() - centre.y) < 1e-6):
            outer_faces.append({'index': index, 'radius_mm': radius,
                                'bounds_mm': bbox(face), 'area_mm2': face.Area()})
    if not outer_faces:
        raise ValueError('Held key does not have its declared full outer circular bearing')
    radius = outer_faces[0]['radius_mm']
    zmin = min(r['bounds_mm'][2] for r in outer_faces)
    zmax = max(r['bounds_mm'][5] for r in outer_faces)
    if max(abs(zmin - (centre.z - length / 2)),
           abs(zmax - (centre.z + length / 2))) > 1e-5:
        raise ValueError('Held key bearing axial faces differ from the declared9.5mm section')
    height = length + 2 * radial_air_mm
    lower = centre.z - length / 2 - radial_air_mm
    radius_air = radius + radial_air_mm
    # Local Y is world Z. Local Z is the horizontal transverse direction.
    # The disc segment N<=split is swept outward. Its shifted curved cap
    # and a straight chord prism are the exact complete swept segment.
    disc = cq.Solid.makeCylinder(radius_air, height,
                                cq.Vector(centre.x, centre.y, lower), axis)
    free_half = _world_box(location, -200, split, -80, 80, -80, 80)
    segment = _native_common(disc, free_half)
    if not segment.isValid() or len(segment.Solids()) != 1:
        raise ValueError('Expanded key bearing is not one valid clipped segment')
    chord_half = math.sqrt(radius_air * radius_air - split * split)
    shifted = segment.translate((-normal.x * outward_entry_mm,
                                  -normal.y * outward_entry_mm, 0))
    bridge = _world_box(location, split - outward_entry_mm, split,
                        -height / 2, height / 2, -chord_half, chord_half)
    envelope = joined(shifted, bridge, 'Water5 key entry', 'exact chord prism')
    enclosure_wall = cq.Solid.makeBox(wall_x_mm[1] - wall_x_mm[0], 500, 102,
                                      cq.Vector(wall_x_mm[0], 0, 253.4))
    cutter = _native_common(envelope, enclosure_wall)
    if not cutter.isValid() or len(cutter.Solids()) != 1:
        raise ValueError('Water5 key aperture is not one valid owner-scoped solid')
    box = bbox(cutter)
    outer_stock = wall_x_mm[1] - box[3]
    if box[0] < wall_x_mm[0] - 1e-6 or outer_stock < 3.:
        raise ValueError('Key aperture violates the east-wall exterior stock')
    checks = []
    for name, part in [('shifted rounded cap', shifted), ('straight chord sweep', bridge)]:
        witness = full_material_coverage(part, envelope)
        checks.append({'check': 'complete envelope operand: ' + name, **witness})
    seat_local = seat.moved(location.inverse)
    key_local = key.moved(location.inverse)
    cutter_local = cutter.moved(location.inverse)
    sb, kb, cb = bbox(seat_local), bbox(key_local), bbox(cutter_local)
    checks.append({'check': 'native split half-space preserves full seat material',
                   'split_local_mm': split, 'seat_min_normal_mm': sb[0],
                   'key_max_normal_mm': kb[3], 'cutter_max_normal_mm': cb[3],
                   'pass': sb[0] >= split - 1e-6 and cb[3] <= split + 1e-6})
    removed, witness = material_common(seat.Solids()[0], cutter.Solids()[0], 0.)
    checks.append({'check': 'complete fixed seat bearing and fastener stock unchanged',
                   'removed_material_mm3': removed, 'independent_common': witness,
                   'pass': removed < .001})
    preserved = seat.copy(mesh=False).cut(cutter.copy(mesh=False), tol=0.)
    seat_witness = full_material_coverage(seat, preserved)
    checks.append({'check': 'independent complete held-seat material retention',
                   'retained_volume_mm3': preserved.Volume(tol=1e-9), **seat_witness})
    # Full-key poses include both screw ears. Their world X decreases
    # monotonically throughout this pure outward normal entry. The circular
    # bearing's continuous path is already the analytic chord/cap envelope.
    for travel in [0., .25, .5, 1., 2., 3., 4., 5., 8., 12.]:
        moved = key.translate((-normal.x * travel, -normal.y * travel, 0))
        in_wall = _native_common(moved, enclosure_wall)
        if in_wall.Solids():
            witness = full_material_coverage(in_wall, cutter)
        else:
            witness = {'pass': True, 'empty_owner_crossing': True}
        checks.append({'check': 'complete held-key east-wall crossing',
                       'outward_travel_mm': travel,
                       'occupied_wall_volume_mm3': sum(abs(s.Volume(tol=1e-9))
                                                      for s in in_wall.Solids()), **witness})
    # All ear stock lies outside the axial bearing band. Prove it stays
    # inboard of the wall with the same running margin; outward motion only
    # increases this X separation.
    bearing_band = cq.Solid.makeBox(100, 100, length,
                                    cq.Vector(centre.x - 50, centre.y - 50,
                                              centre.z - length / 2))
    ears = key.copy(mesh=False).cut(bearing_band, tol=0.)
    ear_max = max(bbox(s)[3] for s in ears.Solids())
    ear_air = wall_x_mm[0] - ear_max
    checks.append({'check': 'both complete screw ears have outward-entry wall air',
                   'ear_max_x_mm': ear_max, 'minimum_wall_air_mm': ear_air,
                   'required_air_mm': radial_air_mm, 'pass': ear_air >= radial_air_mm})
    checks.append({'check': 'practical circular and axial running gaps',
                   'received_outer_radius_mm': radius,
                   'pocket_outer_radius_mm': radius_air,
                   'radial_air_mm': radius_air - radius,
                   'top_air_mm': lower + height - (centre.z + length / 2),
                   'bottom_air_mm': centre.z - length / 2 - lower,
                   'mating_split_plane_mm': split,
                   'mating_face_removed_mm3': removed,
                   'pass': min(radius_air - radius,
                               lower + height - (centre.z + length / 2),
                               centre.z - length / 2 - lower) >= radial_air_mm - 1e-9})
    checks.append({'check': 'fixed-width exterior flank and below-cap preservation',
                   'minimum_exterior_stock_mm': outer_stock,
                   'cutter_min_z_mm': box[2], 'pass': outer_stock >= 3. and box[2] > 253.4})
    certificate = {'pass': all(row['pass'] for row in checks),
                   'checks': checks, 'cutter_bounds_mm': box,
                   'received_outer_bearing_faces': outer_faces,
                   'fixed_seat_volume_mm3': seat.Volume(tol=1e-9),
                   'split_mating_plane_preserved': True,
                   'radial_and_axial_running_air_mm': radial_air_mm,
                   'outward_entry_mm': outward_entry_mm,
                   'outward_axis': [-normal.x, -normal.y, 0.],
                   'minimum_exterior_stock_mm': outer_stock,
                   'scope': 'Exact circular bearing swept along its outward normal, with '
                            '0.25mm radial/top/bottom clearance. The exact planar split '
                            'bearing interface is preserved. Both screw ears remain inboard '
                            'with practical air. Final printed running fit, tool workholding '
                            'and the complete assembly inventory need separate qualification.'}
    if not certificate['pass']:
        raise ValueError('Water5 key pocket failed: ' + json.dumps(checks))
    return cutter, certificate


def main():
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in [Path(__file__), HERE / 'received_native.py',
                         HERE / 'assemble_prints.py', STUDY / 'audit.py',
                         STUDY / 'evidence_binding.py']}
    path = STUDY / 'mounts/water5-hosts.json'
    raw = path.read_bytes()
    manifest = json.loads(raw)
    native_inputs = {}
    def load(name):
        record = manifest['parts'][name]
        data = (ROOT / record['brep']).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != record['sha256']:
            raise ValueError('Changed held native: ' + name)
        native_inputs[name] = {'brep': record['brep'], 'sha256': digest}
        return cq.Shape.importBrep(BytesIO(data))
    key = load('water5-east-drop-key')
    seat = load('water5-east-drop-seat')
    cutter, report = make_pocket(key, seat, manifest['split_seat_properties'])
    OUT.mkdir(parents=True, exist_ok=True)
    tool = OUT / 'water5-key-pocket.brep'
    cutter.exportBrep(str(tool))
    report.update({'clearance_cutter': {
        'brep': str(tool.relative_to(ROOT)),
        'sha256': hashlib.sha256(tool.read_bytes()).hexdigest(),
        'print_owner': 'enclosure-back-top', 'bounds_mm': bbox(cutter),
        'minimum_exterior_stock_mm': report['minimum_exterior_stock_mm'],
        'full_interface_preserving_key_entry': True,
        'factory_upper_bay_channel': True,
        'scope': report['scope']},
        'native_inputs': native_inputs,
        'manifest_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(raw).hexdigest()},
        'manifest_content_sha256': {str(path.relative_to(ROOT)): content_sha256(manifest)},
        'source_inputs': sources})
    drift = [name for name, record in native_inputs.items()
             if hashlib.sha256((ROOT / record['brep']).read_bytes()).hexdigest() != record['sha256']]
    drift.extend(name for name, expected in sources.items()
                 if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected)
    if content_sha256(json.loads(path.read_bytes())) != content_sha256(manifest):
        drift.append(str(path.relative_to(ROOT)))
    report['source_drift'] = drift
    report['pass'] = report['pass'] and not drift
    (HERE / 'water5-key-pocket.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Water5 key wall relief PASS' if report['pass'] else 'Water5 key relief FAIL', flush=True)
    print(json.dumps({'bounds_mm': bbox(cutter), 'checks': len(report['checks']),
                      'minimum_exterior_stock_mm': report['minimum_exterior_stock_mm'],
                      'drift': drift}), flush=True)
    if not report['pass']:
        raise ValueError('Water5 key input drift')


if __name__ == '__main__':
    main()
