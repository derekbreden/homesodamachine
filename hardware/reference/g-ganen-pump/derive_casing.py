"""Inspect casing sections in the measured pump frame, without changing raw scans.

This produces modeling observations, not a production-qualified pump. Each radial
bin retains its contributing passes, spread and coverage. Missing angular bands
remain explicit. Barbs, feet, fixture putty and leads have separate interfaces.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np

from scan_tools import load_cloud, transform_points

HERE = Path(__file__).resolve().parent
STATIONS = [-77.3, -76, -70, -60, -50, -45.8, -45.2, -44.1, -43.4,
            -40, -36, -33, -29, -25, -20, -15, -10, -5, -1,
            1, 5, 10, 20, 30, 40, 50, 60, 70, 76, 78, 80, 81.8]


def casing_selection(points, normals):
    """Inspected casing regions, excluding outboard barbs, sliders and fixtures.

    The sloping lower rail surface separates the rigid motor cradle from the
    rubber upstands. This is a selection boundary, not a manufactured surface.
    The motor-can envelope separately fills its real ventilation openings.
    """
    x, y, z = points.T
    maximum_y = np.where((x > -43.5) & (x < -26), 22., 31.)
    lower_z = np.where(x < 0, 4., -3.)
    maximum_z = np.where(x < 0, 61., 59.8)
    selected = ((abs(y) < maximum_y) & (z > lower_z) & (z < maximum_z)
                & (abs(normals[:, 0]) < .995))
    motor = x >= 0
    selected &= (~motor | ((abs(y) < 28.0)
                           & ((abs(y) < 18) | (z > .8*abs(y)-5.75))
                           & ((z < 24) | (np.hypot(y, z-34.1) < 26.2))))
    selected &= np.sum(normals[:, 1:3]*(points[:, 1:3]-[0., 32.]), axis=1) > 0
    return selected


def longest_gap(present):
    if not np.any(present):
        return len(present)
    missing = ~np.r_[present, present]
    longest = current = 0
    for item in missing:
        current = current+1 if item else 0
        longest = max(longest, current)
    return min(longest, len(present))


def section(points, normals, x, bins):
    # The axial outward faces belong to separate end-plane observations. Rigid
    # radial sections omit their near-axial normals and the outboard barb body.
    selected = (abs(points[:, 0]-x) < .24) & casing_selection(points, normals)
    q = points[selected][:, 1:3]
    center = np.array([0., 32.])
    relative = q-center
    outward = np.sum(normals[selected][:, 1:3]*relative, axis=1) > 0
    q, relative = q[outward], relative[outward]
    angle = np.arctan2(relative[:, 1], relative[:, 0])
    radius = np.linalg.norm(relative, axis=1)
    sector = np.minimum(bins-1, np.floor((angle+np.pi)/(2*np.pi)*bins).astype(int))
    rows = []
    for index in range(bins):
        mask = sector == index
        if mask.sum() < 3:
            rows.append(None)
            continue
        values = radius[mask]
        rows.append({'points': int(mask.sum()), 'radius_median_mm': float(np.median(values)),
                     'radius_p05_mm': float(np.percentile(values, 5)),
                     'radius_p95_mm': float(np.percentile(values, 95)),
                     'median_yz_mm': np.median(q[mask], axis=0).tolist()})
    return rows


def run(measurements, bins):
    report = json.loads(measurements.read_text())
    sources, observations = [], []
    for item in report['passes']:
        source = item['source']
        p, n, checked = load_cloud(source['path'], source['sha256'])
        p, n = p[::3], n[::3]
        t = np.array(item['native_to_reference'])
        p, n = transform_points(p, t), n @ t[:3, :3].T
        observations.append([section(p, n, x, bins) for x in STATIONS])
        sources.append({'id': item['id'], **checked, 'native_to_reference': t.tolist(),
                        'sample_stride': 3})
    sections = []
    for station_index, x in enumerate(STATIONS):
        rows = []
        for index in range(bins):
            per_pass = {sources[k]['id']: values[station_index][index]
                        for k, values in enumerate(observations)
                        if values[station_index][index] is not None}
            if not per_pass:
                rows.append({'angle_radians': float(-np.pi+(index+.5)*2*np.pi/bins),
                             'status': 'unobserved', 'passes': {}})
                continue
            radii = [v['radius_median_mm'] for v in per_pass.values()]
            rows.append({'angle_radians': float(-np.pi+(index+.5)*2*np.pi/bins),
                         'status': 'observed', 'passes': per_pass,
                         'equal_pass_median_radius_mm': float(np.median(radii)),
                         'pass_median_span_mm': float(np.ptp(radii))})
        present = np.array([row['status'] == 'observed' for row in rows])
        sections.append({'x_mm': x, 'radial_origin_yz_mm': [0., 32.],
                         'observed_bins': int(present.sum()), 'angular_bins': bins,
                         'longest_unobserved_angle_degrees': longest_gap(present)*360/bins,
                         'bins': rows})
    return {'status': 'observed_casing_sections_not_production_qualification',
            'coordinate_scale_factor': 1.0, 'sources': sources, 'sections': sections,
            'section_half_width_mm': .24,
            'input_sha256': {measurements.name: hashlib.sha256(measurements.read_bytes()).hexdigest()},
            'tool_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                            for name in ('derive_casing.py', 'scan_tools.py')},
            'limits': ['This section ledger does not fill unobserved angular bands.',
                       'Region limits separate casing from ports/fixtures; they are not measured overall bounds.',
                       'Axial shoulders, fasteners, feet, lead exit and barbs require their own measured solids.',
                       'Section-derived occupied volumes describe external clearance, not actual material or mass.']}


def render(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    selected = [0, 3, 8, 12, 16, 21, 24, 30]
    fig, axes = plt.subplots(2, 4, figsize=(14, 8), constrained_layout=True)
    colors = ['#1b6e91', '#bd6324', '#569947']
    for ax, index in zip(axes.ravel(), selected):
        item = report['sections'][index]
        for source, color in zip(report['sources'], colors):
            xy = [row['passes'][source['id']]['median_yz_mm'] for row in item['bins']
                  if source['id'] in row['passes']]
            if xy:
                xy = np.array(xy)
                ax.scatter(xy[:, 0], xy[:, 1], s=9, color=color, label=source['id'])
        ax.set_title(f"X {item['x_mm']:g} mm · {item['observed_bins']}/{item['angular_bins']} bins")
        ax.set_aspect('equal'); ax.grid(alpha=.2)
        ax.set_xlabel('Y (mm)'); ax.set_ylabel('Z (mm)')
    axes[0, 0].legend(fontsize=7)
    fig.suptitle('Observed casing sections · unit-scale rigid alignment\n'
                 'Open angular bands remain explicit; separate feet, ports and fixtures are excluded', fontsize=11)
    fig.savefig(HERE/'casing-sections.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path, default=HERE/'registered-measurements.json')
    parser.add_argument('--bins', type=int, default=120)
    parser.add_argument('--out', type=Path, default=HERE/'casing-sections.json')
    args = parser.parse_args()
    report = run(args.measurements, args.bins)
    render(report)
    report['diagnostic_sha256'] = {'casing-sections.png': hashlib.sha256((HERE/'casing-sections.png').read_bytes()).hexdigest()}
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps([{key: item[key] for key in ('x_mm', 'observed_bins', 'longest_unobserved_angle_degrees')}
                      for item in report['sections']], indent=2))
