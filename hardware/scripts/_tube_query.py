"""Explicit tube entries and sample batches for the existing fine-model reader."""
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class TubeModel:
    model: Path
    groups: dict[str, tuple[int, ...]]
    leaf_names: tuple[str, ...]


def read(model, run_ids):
    """Read the name table; no mesh, solid or geometry backend is constructed."""
    import _assembly_model

    names = [re.sub(r"/\d+$", "", name) for name, _rgb in _assembly_model.identity(model)]
    wanted = {'tube-' + name for name in run_ids}
    groups = {}
    for index, name in enumerate(names):
        if name in wanted or name.rsplit('/', 1)[-1] in wanted:
            groups.setdefault(name, []).append(index)
    return TubeModel(Path(model), {name: tuple(indices) for name, indices in groups.items()},
                     tuple(dict.fromkeys(names)))


def measure(model, batches, *, timings=None):
    """Resolve all sample batches in one part-engine request, with actual fine entries."""
    import _rust_part

    groups = [{'name': name, 'indices': list(model.groups[name]), 'batches': rows}
              for name, rows in batches.items()]
    result = _rust_part.check('machine', 'tube-route-samples',
                              {'model': str(model.model), 'groups': groups})
    if timings is not None:
        timings.update({group['name']: group['seconds'] for group in result['groups']})
    return {group['name']: {row['name']: row['samples'] for row in group['batches']}
            for group in result['groups']}


def verify_runs(runs, model, tolerance_mm, method):
    """Read the original centre and wall probes against their named fine tube entries."""
    import numpy as np

    groups, batches, probe_indices = {}, {}, {}
    for run in runs:
        if not run['bodies'] or any(name not in model.groups for name in run['bodies']):
            raise ValueError(f"{run['id']}: displayed tube body is missing; regenerate the assembly STEP.")
        groups[run['id']] = tuple(index for name in run['bodies'] for index in model.groups[name])
        centre = {'name': 'centre', 'points': run['points']}
        probes, spans = [], {}
        bore = run.get('bore_radius_mm')
        if bore:
            points = np.asarray(run['points'], float)
            for i, (point, s) in enumerate(zip(points, run['s'])):
                if i in (0, len(points) - 1):
                    continue
                ahead, behind = points[i + 1], points[i - 1]
                ds0, ds1 = s - run['s'][i - 1], run['s'][i + 1] - s
                axis = (point - behind) * (ds1 / ds0) + (ahead - point) * (ds0 / ds1)
                unit = axis / np.linalg.norm(axis)
                side = np.cross(axis, (0., 0., 1.) if abs(unit[2]) < .9 else (1., 0., 0.))
                side /= np.linalg.norm(side)
                other = np.cross(axis, side)
                other /= np.linalg.norm(other)
                mid_wall = (run['radius_mm'] + bore) / 2.
                spans[i] = len(probes)
                probes.extend((point + d * mid_wall).tolist() for d in (side, -side, other, -other))
        else:
            centre['inside_tolerance_mm'] = tolerance_mm
        batches[run['id']] = [centre, {'name': 'wall', 'points': probes,
                                     'inside_tolerance_mm': tolerance_mm}]
        probe_indices[run['id']] = spans
    answers = measure(TubeModel(model.model, groups, model.leaf_names), batches)
    failures = []
    for run in runs:
        rows = answers[run['id']]
        worst = 0.
        bore = run.get('bore_radius_mm')
        failure = None
        for i, (point, s, sample) in enumerate(zip(run['points'], run['s'], rows['centre'])):
            if bore:
                offset = probe_indices[run['id']].get(i)
                missed = [] if offset is None else [k for k, value in enumerate(rows['wall'][offset:offset + 4])
                                                     if not value['inside']]
                if missed:
                    failure = (f"{run['id']}: centreline leaves the displayed tube at s={s:.2f} "
                               f"of {run['s'][-1]:.2f} mm, {tuple(round(c, 2) for c in point)} "
                               f"(wall probes {missed} outside); regenerate the assembly STEP.")
                    break
                expected = bore
            else:
                if not sample['inside']:
                    failure = (f"{run['id']}: centreline leaves the displayed tube at s={s:.2f} "
                               f"of {run['s'][-1]:.2f} mm; regenerate the assembly STEP.")
                    break
                expected = min(run['radius_mm'], s, run['s'][-1] - s)
            worst = max(worst, abs(expected - sample['distance_mm']))
        if failure is None and worst > tolerance_mm:
            failure = (f"{run['id']}: centreline differs from displayed tube by {worst:.3f} mm; "
                       "regenerate the assembly STEP.")
        if failure is not None:
            failures.append(failure)
        else:
            run['displayed_alignment'] = {'method': method, 'samples': len(run['points']),
                                          'max_surface_miss_mm': worst, 'tolerance_mm': tolerance_mm}
    if failures:
        raise ValueError('; '.join(failures))
