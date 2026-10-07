"""Check an analytic print recipe against held native bytes without exporting."""
from io import BytesIO
from pathlib import Path
import hashlib
import itertools
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopTools import TopTools_ListOfShape


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def material_common(left, right, tolerance):
    """Return an independently built, per-solid native material witness."""
    operation = BRepAlgoAPI_Common()
    arguments = TopTools_ListOfShape()
    arguments.Append(left.copy(mesh=False).wrapped)
    tools = TopTools_ListOfShape()
    tools.Append(right.copy(mesh=False).wrapped)
    operation.SetArguments(arguments)
    operation.SetTools(tools)
    operation.SetFuzzyValue(tolerance)
    operation.SetRunParallel(True)
    operation.Build()
    if not operation.IsDone():
        raise ValueError('Native material common did not complete')
    result = operation.Shape()
    if result.IsNull():
        return 0., {'completed': True, 'empty': True, 'solid_count': 0}
    shape = cq.Shape.cast(result)
    solids = shape.Solids()
    if any(not solid.isValid() for solid in solids):
        raise ValueError('Invalid material common solid')
    volume = sum(abs(solid.Volume(tol=1e-9)) for solid in solids)
    return volume, {'completed': True, 'empty': not solids,
                    'solid_count': len(solids), 'volume_mm3': volume}


def full_material_coverage(source, target):
    """Every source solid must have its full volume in the target material."""
    source_solids, target_solids = source.Solids(), target.Solids()
    attempts = []
    for tolerance in [0., .0001, .00001]:
        attempt = {'tolerance_mm': tolerance, 'target_solid_pairs': [], 'source_solids': []}
        try:
            # Summing pairwise commons is a union witness only when target
            # solids do not themselves contain overlapping material.
            for first, second in itertools.combinations(range(len(target_solids)), 2):
                common, witness = material_common(target_solids[first], target_solids[second], tolerance)
                attempt['target_solid_pairs'].append({'indices': [first, second], **witness})
                if common >= .001:
                    raise ValueError('Target solids overlap; pairwise material sum is ambiguous')
            for index, solid in enumerate(source_solids):
                expected = abs(solid.Volume(tol=1e-9))
                witnesses = []
                present = 0.
                for target_index, other in enumerate(target_solids):
                    common, witness = material_common(solid, other, tolerance)
                    present += common
                    witnesses.append({'target_solid': target_index, **witness})
                passed = abs(present-expected) < .001
                attempt['source_solids'].append({
                    'source_solid': index, 'source_volume_mm3': expected,
                    'independent_common_volume_mm3': present,
                    'material_error_mm3': abs(present-expected),
                    'commons': witnesses, 'pass': passed})
            attempt['pass'] = bool(source_solids) and all(row['pass'] for row in attempt['source_solids'])
        except (ValueError, RuntimeError) as error:
            attempt.update({'error': str(error), 'pass': False})
        attempts.append(attempt)
        if attempt['pass']:
            return {'pass': True, 'attempts': attempts}
    return {'pass': False, 'attempts': attempts}


class ReceivedNative:
    def __init__(self, root, manifest):
        self.root = Path(root)
        self.manifest = manifest
        self.records = {}
        for key in ['parts', 'clearance_cutters', 'pilot_cutters', 'joined_root_coupons']:
            self.records.update(manifest.get(key, {}))
        self.shapes = {}
        self.checks = []
        self.inputs = {}

    def shape(self, name, analytic):
        if name in self.shapes:
            return self.shapes[name]
        record = self.records[name]
        path = self.root / record['brep']
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        declared = record.get('sha256')
        if isinstance(declared, dict):
            declared = declared.get(record['brep'])
        if declared and digest != declared:
            raise ValueError('Changed held native input: ' + name)
        received = cq.Shape.importBrep(BytesIO(raw))
        analytic_coverage = full_material_coverage(analytic, received)
        received_coverage = full_material_coverage(received, analytic)
        differences = {}
        for label, left, right in [('analytic_missing', analytic, received),
                                   ('received_excess', received, analytic)]:
            try:
                remainder = left.copy(mesh=False).cut(right.copy(mesh=False), tol=.0001)
                differences[label] = {'volume_mm3': sum(abs(s.Volume(tol=1e-9)) for s in remainder.Solids()),
                                      'empty': not remainder.Solids()}
            except (ValueError, RuntimeError) as error:
                differences[label] = {'operation_error': str(error)}
        missing = differences['analytic_missing'].get('volume_mm3', 0.)
        excess = differences['received_excess'].get('volume_mm3', 0.)
        volume = abs(received.Volume(tol=1e-9) - analytic.Volume(tol=1e-9))
        area = abs(received.Area() - analytic.Area())
        box_error = max(abs(a-b) for a, b in zip(bounds(received), bounds(analytic)))
        passed = (analytic.isValid() and received.isValid()
                  and len(received.Solids()) == len(analytic.Solids())
                  and analytic_coverage['pass'] and received_coverage['pass']
                  and max(missing, excess, volume, area) < .001
                  and box_error < 1e-6)
        self.checks.append({
            'check': 'held native recipe parity: ' + name,
            'brep': record['brep'], 'sha256': digest,
            'analytic_missing_mm3': missing, 'received_excess_mm3': excess,
            'volume_error_mm3': volume, 'area_error_mm2': area,
            'bounds_error_mm': box_error, 'native_bytes_rewritten': False,
            'analytic_material_in_received': analytic_coverage,
            'received_material_in_analytic': received_coverage,
            'difference_boolean_diagnostics': differences,
            'pass': passed})
        if not passed:
            raise ValueError('Held native geometry differs from analytic recipe: ' + name)
        self.inputs['received:' + name] = {'brep': record['brep'], 'sha256': digest}
        self.shapes[name] = received
        return received

    def record(self, name, analytic):
        self.shape(name, analytic)
        return dict(self.records[name])
