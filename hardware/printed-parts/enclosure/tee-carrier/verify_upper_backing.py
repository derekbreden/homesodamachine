"""Verify retained upper station stock in the generated native carrier and print mesh."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import subprocess

import cadquery as cq
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union
import trimesh

import tee_carrier as carrier

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
SPEC = carrier.DEFAULT_SPEC


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moment(mesh, x):
    segments = trimesh.intersections.mesh_plane(mesh, plane_origin=[x, 0, 0],
                                                plane_normal=[1, 0, 0])
    lines = [LineString(np.round(line[:, 1:3], 7)) for line in segments]
    loops = [Polygon(poly.exterior) for poly in polygonize(unary_union(lines))]
    total = np.zeros(3)
    for index, poly in enumerate(loops):
        point = poly.representative_point()
        depth = sum(other.contains(point) and other.area > poly.area
                    for other_index, other in enumerate(loops) if other_index != index)
        points = np.array(poly.exterior.coords)
        y, z = points[:-1].T
        yn, zn = points[1:].T
        cross = y * zn - yn * z
        area = cross.sum() / 2
        first = ((y + yn) * cross).sum() / 6
        second = ((y * y + y * yn + yn * yn) * cross).sum() / 12
        total += (1 if area > 0 else -1) * (-1 if depth % 2 else 1) * np.array([area, first, second])
    area, first, second = total
    return {'area_mm2': float(area), 'centroid_y_mm': float(first / area),
            'Izz_mm4': float(second - first * first / area)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-dir', type=Path,
                        help='Optional saved pre-correction native halves for an exact change-volume comparison')
    args = parser.parse_args()
    errors, rows, inputs = [], [], {}
    for side, name in ((-1, 'left'), (1, 'right')):
        native = HERE / f'enclosure-tee-carrier-{name}.step'
        stl = native.with_suffix('.stl')
        body = cq.importers.importStep(str(native)).val()
        inputs[name] = {'step_sha256': sha(native), 'stl_sha256': sha(stl)}
        station_rows = []
        for x in SPEC.tee_xs:
            if (x > 0) != (side > 0):
                continue
            stock = carrier._box(x - SPEC.trough_r + 0.01, x + SPEC.trough_r - 0.01,
                                 SPEC.stub_relief_y + 0.01, SPEC.web_aft_y - 0.01,
                                 SPEC.trough_top_z + 0.01, SPEC.web_z[1] - 0.01).val()
            missing = stock.cut(body).Volume()
            # Reintroduce the defect to prove this stock reading rejects it.
            continued_trough = cq.Solid.makeCylinder(
                SPEC.trough_r, SPEC.web_z[1] - SPEC.trough_top_z + 1.0,
                cq.Vector(x, SPEC.trough_axis_y, SPEC.trough_top_z), cq.Vector(0, 0, 1))
            defect = body.cut(continued_trough)
            defect_missing = stock.cut(defect).Volume()
            station_rows.append({'x_mm': x, 'required_stock_mm3': stock.Volume(),
                                 'missing_stock_mm3': missing,
                                 'continued_trough_missing_stock_mm3': defect_missing})
            if missing > 1e-5 or defect_missing < 1.0:
                errors.append(f'{name} station X{x:g}: retained-stock regression check failed')
        comparison = None
        baseline = args.baseline_dir / native.name if args.baseline_dir else None
        if baseline is not None:
            if not baseline.is_file():
                raise FileNotFoundError(baseline)
            before = cq.importers.importStep(str(baseline)).val()
            added = body.cut(before)
            removed = before.cut(body).Volume()
            web = next(shape for label, shape in carrier.insertion_envelopes(SPEC, side)
                       if label == 'web')
            outside_web_envelope = added.cut(web).Volume()
            arm_overlap = sum(added.intersect(arm).Volume() for arm in carrier.arm_probes(SPEC))
            allowed = cq.Compound.makeCompound([
                carrier._box(x - SPEC.trough_r, x + SPEC.trough_r,
                             SPEC.web_fore_y, SPEC.bearing_y,
                             SPEC.trough_top_z, SPEC.web_z[1]).val()
                for x in SPEC.tee_xs if (x > 0) == (side > 0)])
            outside_upper_troughs = added.cut(allowed).Volume()
            comparison = {'baseline_step_sha256': sha(baseline), 'added_mm3': added.Volume(),
                          'removed_mm3': removed, 'added_outside_web_envelope_mm3': outside_web_envelope,
                          'added_arm_overlap_mm3': arm_overlap,
                          'added_outside_upper_trough_regions_mm3': outside_upper_troughs}
            if (added.Volume() <= 0 or max(removed, outside_web_envelope, arm_overlap,
                                           outside_upper_troughs) > 1e-5):
                errors.append(f'{name}: correction changes geometry outside the retained upper station stock')
        rows.append({'side': name, 'stations': station_rows, 'native_comparison': comparison})
    audit = json.loads((HERE / 'readiness-audit.json').read_text())
    baseline_commit = audit['baseline_commit']
    relative = (HERE / 'enclosure-tee-carrier-right.stl').relative_to(ROOT)
    baseline_bytes = subprocess.check_output(['git', 'show', f'{baseline_commit}:{relative}'], cwd=ROOT)
    baseline_mesh = trimesh.load(io.BytesIO(baseline_bytes), file_type='stl')
    mesh = trimesh.load_mesh(HERE / 'enclosure-tee-carrier-right.stl')
    sections = []
    for x, name in ((20.07, 'inner tee centre'), (79.82, 'outer tee centre')):
        before, current = moment(baseline_mesh, x), moment(mesh, x)
        sections.append({'section': name, 'x_mm': x, 'before_spring_move': before,
                         'corrected_print': current, 'Izz_ratio': current['Izz_mm4'] / before['Izz_mm4']})
    result = {
        'status': 'pass' if not errors else 'fail', 'errors': errors,
        'source_sha256': sha(HERE / 'tee_carrier.py'), 'inputs': inputs,
        'current_trough_top_z_mm': SPEC.trough_top_z,
        'current_retained_upper_backing_mm': SPEC.web_aft_y - SPEC.stub_relief_y,
        'current_retained_upper_height_mm': SPEC.web_z[1] - SPEC.trough_top_z,
        'native_stock_readings': rows,
        'pre_spring_move_baseline_commit': baseline_commit,
        'pre_spring_move_mesh_sha256': hashlib.sha256(baseline_bytes).hexdigest(),
        'printed_sections': sections,
        'section_scope': 'Mesh sections normal to X, centroidal Izz at equal material modulus. '
                         'No whole-carrier compliance, joint preload, infill or layer adhesion result.',
        'clearance_scope': 'Added material is entirely within the already-declared rectangular web '
                           'entry envelope and outside current arm probes. Carrier selftest separately '
                           'checks tube relief and retained backing. The actual production tee remains unqualified.',
        'production_ready': False,
    }
    (HERE / 'upper-backing-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'errors': errors,
                      'sections': [(row['section'], row['Izz_ratio']) for row in sections]}, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
