"""Native west-flank opening for the held flush ASSE drip pan.

The held pan supplies the two rounded pull-face end profiles and the basin's
outer end face. Their X projection defines the whole occupied silhouette.
The opening has 0.25 mm running room on its Y sides and above, and 0.5 mm
below. Only the nine-millimetre west wall receives this aperture.

``make_slot(pan)`` returns the cutter and an independent native certificate.
The command writes the cutter/receipt only; it never rebuilds a parent print
or exports a component. The selected pan's dimensions and native bytes remain
the input authority.
"""
from io import BytesIO
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
OUT = ROOT / '.cache/pump-first-layout/structure/pan-slot'
sys.path[:0] = [str(STUDY), str(HERE)]

from audit import bbox
from evidence_binding import content_sha256
from received_native import full_material_coverage, material_common
from assemble_prints import joined


def _plane_x(face, value):
    b = bbox(face)
    return (face.geomType() == 'PLANE' and b[3] - b[0] < 1e-5
            and abs((b[0] + b[3]) / 2 - value) < 1e-5)


def _extrude_face(face, x, depth):
    """Keep all original curved edges in an X-normal section."""
    b = bbox(face)
    offset = x - (b[0] + b[3]) / 2
    wire = face.outerWire().translate((offset, 0, 0))
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(depth, 0, 0))


def _union(parts, label):
    shape = parts[0]
    for index, part in enumerate(parts[1:], 1):
        shape = joined(shape, part, label, str(index))
    witnesses = [full_material_coverage(part, shape) for part in parts]
    if (not shape.isValid() or len(shape.Solids()) != 1
            or not all(row['pass'] for row in witnesses)):
        raise ValueError('Incomplete native ' + label)
    return shape, witnesses


def _end_profile(shape, x):
    faces = [f for f in shape.Faces() if _plane_x(f, x)]
    if len(faces) != 1 or len(faces[0].Wires()) != 1:
        raise ValueError('Projected silhouette needs one closed native end face')
    return faces[0].outerWire()


def _settlement_coverage(wire, depth, travel, cutter):
    """Cover every continuous Z translation using exact boundary-edge prisms.

    A translated region is covered by its initial region and the ruled
    patches swept by its boundary edges. Extruding every such planar patch
    across the wall gives native material witnesses for the full interval.
    Vertical straight edges sweep zero area and need no additional material.
    """
    checks = []
    for index, edge in enumerate(wire.Edges()):
        operation = BRepPrimAPI_MakePrism(edge.wrapped, gp_Vec(0, 0, -travel), False, True)
        patch = cq.Shape.cast(operation.Shape())
        area = patch.Area()
        if area < 1e-7:
            checks.append({'check': 'continuous settlement boundary patch ' + str(index),
                           'native_edge_type': edge.geomType(), 'swept_area_mm2': area,
                           'zero_area_parallel_edge': True, 'pass': True})
            continue
        if not patch.isValid() or len(patch.Faces()) != 1:
            raise ValueError('Invalid continuous settlement boundary patch')
        solid = _extrude_face(patch.Faces()[0], bbox(cutter)[0], depth)
        if not solid.isValid() or len(solid.Solids()) != 1:
            raise ValueError('Invalid continuous settlement material prism')
        witness = full_material_coverage(solid, cutter)
        checks.append({'check': 'continuous settlement boundary patch ' + str(index),
                       'native_edge_type': edge.geomType(), 'swept_area_mm2': area,
                       'swept_volume_mm3': solid.Volume(tol=1e-9), **witness})
    return checks


def make_slot(pan, flank_x_mm=(-107.5, -98.5), side_top_air_mm=.25,
              bottom_air_mm=.5, fixed_lid_top_mm=253.4000102):
    """Return ``(cutter, certificate)`` without changing any received geometry.

    The complete projected profile is proved to contain the full held pan.
    Native coverage of translations in all four requested gap directions
    proves each allowance. Pure X travel and gravity settlement between zero
    and the lower allowance stay in the same extruded opening.
    """
    if not pan.isValid() or len(pan.Solids()) != 1:
        raise ValueError('One valid held pan solid is required')
    if (abs(flank_x_mm[0] + 107.5) > 1e-9
            or abs(flank_x_mm[1] + 98.5) > 1e-9
            or side_top_air_mm != .25 or bottom_air_mm != .5):
        raise ValueError('This helper binds the selected nine-mm flank and allowances')
    bounds = bbox(pan)
    if abs(bounds[0] - flank_x_mm[0]) > 1e-6:
        raise ValueError('The selected pan pull face must be flush with the west wall')
    # The basin's complete east end face fills its projected cavity. The
    # rounded cap faces share a plane at the measured pull-face rear edge.
    basin = [f for f in pan.Faces() if _plane_x(f, bounds[3])]
    if len(basin) != 1:
        raise ValueError('Cannot identify the held basin outer end face')
    caps = []
    for index, face in enumerate(pan.Faces()):
        b = bbox(face)
        if face.geomType() != 'PLANE' or b[3] - b[0] >= 1e-5:
            continue
        if (abs(b[1] - bounds[1]) < 1e-5
                or abs(b[4] - bounds[4]) < 1e-5):
            caps.append((index, face))
    if len(caps) != 2:
        raise ValueError('Cannot identify both complete rounded pull-face end profiles')
    cap_x = [(bbox(face)[0] + bbox(face)[3]) / 2 for _, face in caps]
    if abs(cap_x[0] - cap_x[1]) > 1e-6:
        raise ValueError('Pull-face profiles do not share their measured rear plane')
    x, depth = flank_x_mm[0], flank_x_mm[1] - flank_x_mm[0]
    pieces = [_extrude_face(face, x, depth)
              for face in [basin[0], *[f for _, f in caps]]]
    profile, union_witnesses = _union(pieces, 'pan full projected profile')
    # Unify only this newly generated planar section's shared end faces. Both
    # full material directions guard against a successful-looking refiner
    # dropping a rounded cap. No received pan or parent is refined.
    refined = profile.clean()
    refinement_witnesses = [full_material_coverage(profile, refined),
                            full_material_coverage(refined, profile)]
    if (not refined.isValid() or len(refined.Solids()) != 1
            or not all(row['pass'] for row in refinement_witnesses)):
        raise ValueError('Projected section refinement changed native material')
    profile = refined
    wire = _end_profile(profile, x)
    offsets = wire.offset2D(side_top_air_mm, kind='arc')
    if len(offsets) != 1 or not offsets[0].isValid():
        raise ValueError('Rounded running offset is not one valid closed wire')
    symmetric = cq.Solid.extrudeLinear(offsets[0], [], cq.Vector(depth, 0, 0))
    # A downward 0.25-mm extrusion of the symmetric offset changes only the
    # required lower allowance: .25 below from the offset plus .25 travel.
    down = bottom_air_mm - side_top_air_mm
    cutter, opening_witnesses = _union(
        [symmetric, symmetric.translate((0, 0, -down))], 'pan running aperture')
    c = bbox(cutter)
    if (c[0] < flank_x_mm[0] - 1e-6 or c[3] > flank_x_mm[1] + 1e-6
            or c[2] <= fixed_lid_top_mm):
        raise ValueError('Pan opening crosses the fixed lid or nine-mm flank boundary')
    extended_profile = cq.Solid.extrudeLinear(
        wire.translate((bounds[0] - 1 - x, 0, 0)), [],
        cq.Vector(bounds[3] - bounds[0] + 2, 0, 0))
    pan_witness = full_material_coverage(pan, extended_profile)
    checks = [{'check': 'complete held pan fits its projected rounded silhouette',
               **pan_witness}]
    gap_shifts = [('fore side', (0, -side_top_air_mm, 0)),
                  ('aft side', (0, side_top_air_mm, 0)),
                  ('top', (0, 0, side_top_air_mm)),
                  ('bottom', (0, 0, -bottom_air_mm)),
                  ('nominal', (0, 0, 0))]
    for label, shift in gap_shifts:
        witness = full_material_coverage(profile.translate(shift), cutter)
        checks.append({'check': label + ' full-profile native gap',
                       'translation_mm': list(shift), **witness})
    checks.extend(_settlement_coverage(wire, depth, bottom_air_mm, cutter))
    expected = [bounds[1] - side_top_air_mm, bounds[2] - bottom_air_mm,
                bounds[4] + side_top_air_mm, bounds[5] + side_top_air_mm]
    actual = [c[1], c[2], c[4], c[5]]
    error = max(abs(a - b) for a, b in zip(actual, expected))
    checks.append({'check': 'exact directional opening bounds',
                   'expected_yz_mm': expected, 'actual_yz_mm': actual,
                   'maximum_error_mm': error, 'pass': error < 1e-5})
    lid_scope = cq.Solid.makeBox(9, c[4] - c[1] + 2,
                                fixed_lid_top_mm - 248,
                                cq.Vector(x, c[1] - 1, 248))
    below, below_witness = material_common(cutter.Solids()[0], lid_scope, 0.)
    checks.append({'check': 'fixed lid and every below-cap plane remain outside the aperture',
                   'fixed_lid_top_mm': fixed_lid_top_mm,
                   'aperture_bottom_mm': c[2],
                   'vertical_separation_mm': c[2] - fixed_lid_top_mm,
                   'common_mm3': below, 'native_witness': below_witness,
                   'pass': below < .001 and c[2] > fixed_lid_top_mm})
    certificate = {
        'pass': all(row['pass'] for row in checks),
        'pan_bounds_mm': bounds, 'cutter_bounds_mm': c,
        'pull_face_projection': {
            'native_cap_face_indices': [i for i, _ in caps],
            'native_cap_plane_x_mm': cap_x[0],
            'native_cap_wire_edge_types': [[e.geomType() for e in f.outerWire().Edges()]
                                           for _, f in caps],
            'basin_end_plane_x_mm': bounds[3],
            'profile_union_material_witnesses': union_witnesses,
            'profile_refinement_material_witnesses': refinement_witnesses,
            'opening_union_material_witnesses': opening_witnesses},
        'flank_x_mm': list(flank_x_mm), 'flank_span_mm': depth,
        'directional_allowances_mm': {'fore': side_top_air_mm,
                                     'aft': side_top_air_mm,
                                     'above': side_top_air_mm,
                                     'below': bottom_air_mm},
        'checks': checks,
        'continuous_motion_scope':
            'The complete pan is contained in the X-extruded silhouette. Pure X extraction '
            'and uniform downward settlement from0 to0.5mm use that same open silhouette; '
            'the profile-offset union contains the swept settlement interval. Other bay '
            'neighbors, cable handling, wall bearing, printed fit and liquid sealing require '
            'their separate complete-scene and physical qualifications.'}
    if not certificate['pass']:
        raise ValueError('Pan opening certificate failed: ' + json.dumps(checks))
    return cutter, certificate


def main():
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in [Path(__file__), HERE / 'received_native.py',
                         HERE / 'assemble_prints.py', STUDY / 'audit.py',
                         STUDY / 'evidence_binding.py']}
    path = STUDY / 'routing/candidate.json'
    raw = path.read_bytes()
    manifest = json.loads(raw)
    record = manifest['parts']['asse-drip-pan']
    native_path = ROOT / record['brep']
    native = native_path.read_bytes()
    digest = hashlib.sha256(native).hexdigest()
    if digest != record['sha256']:
        raise ValueError('Held pan bytes differ from their native receipt')
    pan = cq.Shape.importBrep(BytesIO(native))
    cutter, report = make_slot(pan)
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'pan-slot.brep'
    cutter.exportBrep(str(output))
    report.update({
        'clearance_cutter': {
            'brep': str(output.relative_to(ROOT)),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'print_owner': 'enclosure-back-top',
            'bounds_mm': bbox(cutter), 'full_west_flank_aperture': True,
            'fixed_lid_and_lower_interfaces_unchanged': True,
            'scope': 'Full held rounded pull-face silhouette with0.25mm sides/top and0.5mm '
                     'below allowance; exact west9mm flank only. Apply uncropped by the '
                     'ordinary aft-funnel clearance scope.'},
        'native_inputs': {'asse-drip-pan': {'brep': record['brep'], 'sha256': digest}},
        'manifest_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(raw).hexdigest()},
        'manifest_content_sha256': {str(path.relative_to(ROOT)): content_sha256(manifest)},
        'source_inputs': sources})
    drift = []
    if native_path.read_bytes() != native:
        drift.append('held pan bytes changed')
    if content_sha256(json.loads(path.read_bytes())) != content_sha256(manifest):
        drift.append('pan manifest geometry changed')
    for source, expected in report['source_inputs'].items():
        if hashlib.sha256((ROOT / source).read_bytes()).hexdigest() != expected:
            drift.append(source)
    report['source_drift'] = drift
    report['pass'] = report['pass'] and not drift
    (HERE / 'pan-slot.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Pan full-profile opening PASS' if report['pass'] else 'Pan opening FAIL', flush=True)
    print(json.dumps({'bounds_mm': bbox(cutter),
                      'directional_allowances_mm': report['directional_allowances_mm'],
                      'checks': len(report['checks']), 'drift': drift}), flush=True)
    if not report['pass']:
        raise ValueError('Pan slot input drift')


if __name__ == '__main__':
    main()
