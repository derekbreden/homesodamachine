"""Measure the rigid switch underside from unit-scale archived pump scans."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
HERE = Path(__file__).resolve().parent
REF = HERE.parent
sys.path.insert(0, str(REF))
from scan_tools import load_cloud, plane, transform_points

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    source = REF/'registered-measurements.json'
    report = json.loads(source.read_text())
    readings = []
    for row in report['passes']:
        p, n, checked = load_cloud(row['source']['path'], row['source']['sha256'])
        t = np.array(row['native_to_reference'])
        p = transform_points(p, t)
        n = n @ t[:3, :3].T
        selected = ((p[:,0] > -64) & (p[:,0] < -46) & (abs(p[:,1]) < 12)
                    & (p[:,2] > 15.7) & (p[:,2] < 17.8) & (abs(n[:,2]) > .97))
        item = {'pass': row['id'], 'source': checked,
                'native_to_reference': t.tolist(), 'selected_points': int(selected.sum())}
        if selected.sum() < 30:
            item['status'] = 'Rigid underside occluded in this view'
        else:
            center, normal, residual = plane(p[selected])
            if normal[2] > 0: normal = -normal
            item.update(point_mm=center.tolist(), normal=normal.tolist(), residual_mm=residual)
        readings.append(item)
    first = readings[0]
    return {'schema': 1, 'part': 'G Ganen pump rigid switch underside',
        'status': 'Observed external open air; loose flexible leads excluded from rigid envelope',
        'frame': 'Native reference: X positive toward motor rear, foot-bearing datum Z0',
        'physical_observation': 'under-head-tube/flat-elbow-observation.json',
        'surface_selection': {'x_interval_mm': [-64, -46], 'abs_y_max_mm': 12,
            'z_interval_mm': [15.7, 17.8], 'abs_normal_z_min': .97,
            'scope': 'Broad near-planar switch underside visible in the feet-up and on-back scans. The lead loops below this surface are flexible and separately visible in the photographs.'},
        'readings': readings,
        'open_air': {'x_interval_mm': [-62.0, -45.55], 'y_interval_mm': [-20., 20.],
            'bottom_z_mm': -2., 'roof_plane': {'point_mm': first['point_mm'],
                'normal': first['normal'], 'inward_allowance_mm': .10},
            'boundary_scope': 'The narrow axial interval retains the lower front switch block and the head shoulder. The transverse interval is below the observed rigid underside and its rising side edges. The lower-scanned underside and a 0.10mm inward air allowance retain conservative rigid stock. This open region is independent of mating fitting geometry.'},
        'affected_components': ['rigid_casing_envelope', 'switch_outer_shell_external_envelope'],
        'excluded_from_correction': ['head outer shell', 'lower cradle', 'all four rubber feet', 'motor', 'barbs', 'crown features'],
        'limits': ['The rigid surface fits do not establish absolute optical-scanner accuracy.',
            'Loose leads can occupy this space and are dressed during assembly; they are not rigid pump material.',
            'The observed open region does not qualify any installed enclosure route or mounting load.'],
        'input_sha256': {'registered-measurements.json': sha(source)},
        'tool_sha256': {'under-head-clearance/measure.py': sha(Path(__file__)), 'scan_tools.py': sha(REF/'scan_tools.py')}}

if __name__ == '__main__':
    target = REF/'under-head-clearance.json'
    target.write_text(json.dumps(run(), indent=2)+'\n')
    print(target)
