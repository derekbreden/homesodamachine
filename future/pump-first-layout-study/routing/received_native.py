"""Read-only native correspondence for selected producer outputs."""
import hashlib
from io import BytesIO
from pathlib import Path
import sys

import cadquery as cq
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wiring'))
import audit
from structure.assemble_prints_verified import contained_by_common
from fluid_members import circular_parity


def receive(root, record, name, inputs):
    raw = (root / record['brep']).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    declared = record.get('sha256')
    if isinstance(declared, str) and declared != digest:
        raise ValueError('Declared native output changed: ' + name)
    shape = cq.Shape.importBrep(BytesIO(raw))
    if not shape.isValid() or shape.wrapped.IsNull():
        raise ValueError('Invalid received producer output: ' + name)
    inputs[name] = {'brep': record['brep'], 'sha256': digest}
    return shape


def material_equivalence(received, expected, name):
    a, b = received.Volume(tol=1e-9), expected.Volume(tol=1e-9)
    if not received.isValid() or not expected.isValid():
        raise ValueError('Invalid expected/received native material: ' + name)
    forward = contained_by_common(received, expected, name + '/received_in_recipe')
    reverse = contained_by_common(expected, received, name + '/recipe_in_received')
    return {'check': 'received producer output matches complete analytic native material',
            'part': name, 'received_volume_mm3': a, 'recipe_volume_mm3': b,
            'received_solids': len(received.Solids()), 'recipe_solids': len(expected.Solids()),
            'material_volume_error_mm3': abs(a - b),
            'received_in_recipe': forward, 'recipe_in_received': reverse,
            'pass': abs(a - b) < .001 and forward['pass'] and reverse['pass']}


def circular_equivalence(received, expected, edges, diameter, name):
    a, received_section = circular_parity(received, diameter, edges)
    b, recipe_section = circular_parity(expected, diameter, edges)
    # Each received circular face reconstructs one closed physical solid.
    # A one-to-one native material witness establishes equality of the two
    # unions without asking OCC to classify a solid against a compound.
    first, second = a.Solids(), b.Solids()
    target_bounds = [audit.bbox(solid) for solid in second]
    remaining = set(range(len(second)))
    witnesses = []
    for index, solid in enumerate(first):
        bounds = audit.bbox(solid)
        attempts = []
        for target_index in sorted(remaining):
            other = second[target_index]
            box_error = max(abs(x-y)for x,y in zip(bounds,target_bounds[target_index]))
            # A full-material one-to-one match must have identical exact
            # native extrema. Nonmatching boxes cannot be such a witness.
            if box_error >= 1e-5:
                continue
            try:
                forward = contained_by_common(solid,other,name+f'/member-{index}/received_in_recipe-{target_index}')
                reverse = contained_by_common(other,solid,name+f'/member-{index}/recipe-{target_index}_in_received')
                error = abs(solid.Volume(tol=1e-9)-other.Volume(tol=1e-9))
                passed = forward['pass'] and reverse['pass'] and error < .001
                witness = {'received_member':index,'recipe_member':target_index,
                           'native_bounds_error_mm':box_error,'material_volume_error_mm3':error,
                           'received_in_recipe':forward,'recipe_in_received':reverse,'pass':passed}
                attempts.append(witness)
                if passed:
                    remaining.remove(target_index)
                    witnesses.append(witness)
                    break
            except Exception as failure:
                attempts.append({'recipe_member':target_index,'error':str(failure),'pass':False})
        else:
            witnesses.append({'received_member':index,'attempts':attempts,'pass':False})
    material = {'check':'one-to-one independent solid-to-solid native material equivalence',
                'received_members':len(first),'recipe_members':len(second),'members':witnesses,
                'unmatched_recipe_members':sorted(remaining),
                'pass':len(first)==len(second) and not remaining and all(row['pass']for row in witnesses)}
    return {'check': 'received circular output matches exact selected centreline and full material',
            'part': name, 'received_section': received_section,
            'recipe_section': recipe_section, 'member_material_equivalence': material,
            'pass': received_section['pass'] and recipe_section['pass'] and material['pass']}


def centreline_equivalence(received, expected_edges, name):
    edges = received.Edges()
    checks = []
    for index, (a, b) in enumerate(zip(edges, expected_edges)):
        positions = [(a.positionAt(t) - b.positionAt(t)).Length for t in (0., .25, .5, .75, 1.)]
        tangent = [a.tangentAt(t).getAngle(b.tangentAt(t)) for t in (0., .5, 1.)]
        radius = abs(a.radius() - b.radius()) if a.geomType() == b.geomType() == 'CIRCLE' else 0.
        checks.append({'edge': index, 'received_kind': a.geomType(), 'recipe_kind': b.geomType(),
                       'length_error_mm': abs(a.Length() - b.Length()),
                       'native_parameter_point_errors_mm': positions,
                       'native_tangent_errors_rad': tangent, 'radius_error_mm': radius,
                       'pass': a.geomType() == b.geomType() and abs(a.Length() - b.Length()) < 1e-5
                               and max(positions) < 1e-5 and max(tangent) < 1e-5 and radius < 1e-5})
    return {'check': 'received centreline matches every selected analytic native edge',
            'part': name, 'received_edges': len(edges), 'recipe_edges': len(expected_edges),
            'edges': checks, 'pass': len(edges) == len(expected_edges) and all(row['pass'] for row in checks)}
