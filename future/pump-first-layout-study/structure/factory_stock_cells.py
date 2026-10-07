"""Complete native stock cells for the rear shell's factory Y translation."""
from pathlib import Path
import hashlib
import itertools

import cadquery as cq
import audit
from structure import received_native
from structure import assemble_prints_verified as material

ROOT = Path(__file__).resolve().parents[3]
LIMIT_MM3 = .001


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def volume(shape):
    return sum(abs(solid.Volume(tol=1e-9)) for solid in shape.Solids())


def coverage_error(proof):
    accepted = next(row for row in proof['attempts'] if row['pass'])
    return sum(row['material_error_mm3'] for row in accepted['source_solids'])


def exact_coverage(source, target):
    proof = received_native.full_material_coverage(source, target)
    if not proof['pass'] or not proof['attempts'][0]['pass']:
        raise ValueError('Complete exact native material coverage failed')
    return proof


def decompose(source, output_dir, source_record):
    """Return received cells whose complete union equals the received shell.

    Each spatial scope is independently certified by full material Common.
    Exact cells selection certifies the original in the complete OR union;
    each cell is also independently certified inside the original. Separate
    integrations of trimmed pieces are retained as diagnostics.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_reader = received_native.ReceivedNative(
        ROOT, {'parts': {'shell-contact-band': source_record}})
    source = source_reader.shape('shell-contact-band', source)
    if not source.isValid() or any(not s.isValid() for s in source.Solids()):
        raise ValueError('Invalid complete shell contact band')
    cells = {}
    records = {}
    scopes = {}
    for xi, (x0, x1) in enumerate(zip([-120., -97.5, 97.5], [-97.5, 97.5, 120.])):
        for yi, (y0, y1) in enumerate(zip([-100., 463.], [463., 700.])):
            name = f'x{xi}-y{yi}'
            bounds = [x0, y0, 253.3, x1, y1, 314.3]
            scope = cq.Solid.makeBox(x1-x0, y1-y0, 61., cq.Vector(x0, y0, 253.3))
            cell = source.copy(mesh=False).intersect(scope, tol=0.)
            solids = cell.Solids()
            if not solids or not cell.isValid() or any(not s.isValid() for s in solids):
                raise ValueError('Invalid native stock cell: ' + name)
            path = output_dir / (name + '.brep')
            cell.exportBrep(str(path))
            record = {'brep': str(path.relative_to(ROOT)), 'sha256': sha(path)}
            records[name] = record
            scopes[name] = (scope, bounds)
            cells[name] = cell

    reader = received_native.ReceivedNative(ROOT, {'parts': records})
    cells = {name: reader.shape(name, cell) for name, cell in cells.items()}
    scope_rows = []
    for name, cell in cells.items():
        scope, bounds = scopes[name]
        proof = exact_coverage(cell, scope)
        raw_bounds = audit.bbox(cell)
        bbox_inside = all(raw_bounds[i] >= bounds[i]-1e-6 and
                          raw_bounds[i+3] <= bounds[i+3]+1e-6 for i in range(3))
        scope_rows.append({'cell': name, **records[name], 'scope_bounds_mm': bounds,
                           'raw_native_bounds_mm': raw_bounds,
                           'raw_bbox_inside_scope_diagnostic': bbox_inside,
                           'valid': cell.isValid(), 'solid_count': len(cell.Solids()),
                           'face_count': len(cell.Faces()), 'volume_mm3': volume(cell),
                           'complete_native_material_in_scope': proof, 'pass': True})

    compound = cq.Compound.makeCompound(list(cells.values()))
    in_source = exact_coverage(compound, source)
    source_error = coverage_error(in_source)
    if source_error >= LIMIT_MM3:
        raise ValueError('Complete stock-cell containment error exceeds the material limit')
    solids = [(name, i, s) for name, cell in cells.items()
              for i, s in enumerate(cell.Solids())]
    pairs = []
    for (first, fi, a), (second, si, b) in itertools.combinations(solids, 2):
        amount, witness = received_native.material_common(a, b, 0.)
        row = {'first_cell': first, 'first_solid': fi, 'second_cell': second,
               'second_solid': si, **witness, 'common_mm3': amount,
               'pass': amount < 1e-8}
        if not row['pass']:
            raise ValueError('Native stock-cell material interiors overlap')
        pairs.append(row)

    complete = []
    for index, solid in enumerate(source.Solids()):
        complete.append(material.grouped_source_coverage_certificate(
            solid, [s for _, _, s in solids], source_error,
            'factory shell/original solid ' + str(index)))
    raw_sum = volume(compound)
    sum_diagnostic = received_native.full_material_coverage(source, compound)
    receipt = {
        'pass': True, 'method': 'complete_native_spatial_stock_cells',
        'source_record': dict(source_record), 'source_bounds_mm': audit.bbox(source),
        'source_valid': source.isValid(), 'source_solid_count': len(source.Solids()),
        'source_face_count': len(source.Faces()), 'source_volume_mm3': volume(source),
        'source_received_parity': source_reader.checks,
        'cell_received_parity': reader.checks, 'cells': scope_rows,
        'disjoint_native_material_interiors': pairs,
        'complete_cell_material_in_original': in_source,
        'cell_material_outside_original_bound_mm3': source_error,
        'complete_original_in_cell_union': complete,
        'complete_original_coverage_bound_mm3': sum(
            row['outside_union_upper_bound_mm3'] for row in complete),
        'separately_integrated_volume_sum_mm3_diagnostic': raw_sum,
        'separately_integrated_volume_error_mm3_diagnostic': abs(raw_sum-volume(source)),
        'separately_integrated_coverage_diagnostic': sum_diagnostic,
        'material_limit_mm3': LIMIT_MM3,
        'proof': 'Every received cell is valid, completely inside its closed spatial '
                 'scope and the original shell. Their material interiors are disjoint. '
                 'The exact native OR union covers every complete original solid with '
                 'bidirectional material Commons. A continuous nonpenetration certificate '
                 'for every complete cell therefore certifies the complete shell.',
    }
    if receipt['complete_original_coverage_bound_mm3'] >= LIMIT_MM3:
        raise ValueError('Complete stock-union coverage bound exceeds the material limit')
    return cells, records, receipt


def monotone_cap_contact(cell, cell_record, cell_scope, cap, cap_record, stroke):
    """Certify the one rear-cell/cap-lid contact over nonnegative Y offsets."""
    if cell_scope != [-97.5, 463., 253.3, 97.5, 700., 314.3] or stroke < 0.:
        raise ValueError('Unexpected nominal cap-contact motion or cell scope')
    scope = cq.Solid.makeBox(195., 237., 61., cq.Vector(-97.5, 463., 253.3))
    cell_in_scope = exact_coverage(cell, scope)
    scope_error = coverage_error(cell_in_scope)
    prism_bounds = [-90.5, -100., -100., 90.5, 465.3, audit.bbox(cap)[5]]
    prism = cq.Solid.makeBox(181., 565.3, prism_bounds[5]+100.,
                             cq.Vector(-90.5, -100., -100.))
    cap_in_prism = exact_coverage(cap, prism)
    cap_error = coverage_error(cap_in_prism)
    if scope_error != 0. or cap_error != 0.:
        raise ValueError('Pointwise cap-contact proof requires exact zero coverage errors')
    exclusion = []
    for index, solid in enumerate(cell.Solids()):
        amount, witness = received_native.material_common(solid, prism, 0.)
        row = {'cell_solid': index, **witness, 'common_mm3': amount,
               'pass': amount == 0.}
        if not row['pass']:
            raise ValueError('Nominal rear cell enters the closed cap-lid prism')
        exclusion.append(row)
    return {
        'pass': True, 'cell': 'x1-y1', 'fixed': 'cold-core/foam-cap-lid-top',
        'cell_record': dict(cell_record), 'fixed_record': dict(cap_record),
        'offset_y_interval_mm': [0., stroke], 'cell_scope_bounds_mm': cell_scope,
        'complete_cell_material_in_scope': cell_in_scope,
        'complete_cell_scope_coverage_error_mm3': scope_error,
        'closed_prism_bounds_mm': prism_bounds,
        'complete_fixed_material_in_prism': cap_in_prism,
        'complete_fixed_prism_coverage_error_mm3': cap_error,
        'complete_cell_prism_exclusion': exclusion,
        'method': 'native_monotone_prism_nonpenetration',
        'proof': 'The complete cell lies at Y>=463, above the prism fore bound -100, '
                 'and has no material intersection with the prism. A nonnegative pure '
                 'Y translation preserves X and Z. Points outside by X or Z stay outside; '
                 'every other point is beyond the rear plane Y=465.3 and stays beyond it. '
                 'The complete fixed cap lid lies in the prism, so this named pair '
                 'cannot penetrate over the complete stroke, including seated contact. '
                 'Every other neighbor receives the unchanged midpoint separation test.',
    }
