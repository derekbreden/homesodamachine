"""Read support roads below both retaining ledges, including unlabelled tips."""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

import display_receiver_trial as trial
from prepare_print import JOB as DEFAULT_JOB

JOB = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else DEFAULT_JOB
preparation = json.loads((JOB/'preparation.json').read_text())
verification = json.loads((JOB/'verification.json').read_text())
part, = preparation['parts']
assert part['rotation_x_degrees'] == 0
segments = json.loads((JOB/'support-segments.json').read_text())
offset = np.array(part['source_center_mm'])-np.array(part['plate_translation_mm'])
a = np.array([s['a'] for s in segments])+offset
b = np.array([s['b'] for s in segments])+offset
widths = np.array([s['width'] for s in segments])
points = np.concatenate([a, (a+b)/2, b])
radii = np.tile(widths/2, 3)
angle = math.radians(trial.ANGLE)
plane = -trial.retention.CATCH
local_y = (points[:, 1]+plane*math.sin(angle))/math.cos(angle)
height = points[:, 1]*math.tan(angle)+plane/math.cos(angle)-trial.BASE_Z
gap = height-points[:, 2]
contacts = []
for side in (-1, 1):
    x = side*points[:, 0]
    mask = ((x+radii >= trial.CATCH_EDGE) &
            (x-radii <= trial.SKIRT_OUTER+trial.retention.LIP) &
            (abs(local_y) <= trial.retention.LENGTH/2) & (gap >= 0) & (gap <= .6))
    assert mask.sum() > 10, side
    extent = [float(local_y[mask].min()), float(local_y[mask].max())]
    assert extent[1]-extent[0] > 20, (side, extent)
    contacts.append({'side': side, 'road_samples_below_hook_overlap': int(mask.sum()),
                     'local_along_skirt_span_mm': extent,
                     'vertical_distance_to_nominal_catch_plane_mm':
                     [float(gap[mask].min()), float(gap[mask].max())]})
audit = json.loads((JOB/'support-audit-display-receiver-trial-v1.json').read_text())
foot_front = -trial.HEIGHT/2*math.cos(angle)-1
report = {'pass': True, 'native_archive_sha256': verification['native_archive_sha256'],
          'gcode_sha256': verification['gcode_sha256'],
          'support_road_segments_examined': len(segments),
          'include_unlabelled_support': True,
          'labelled_interfaces': audit['summary']['explicit_interface_islands'],
          'contacts_below_nominal_hook_overlap': contacts,
          'summary': audit['summary'],
          'removal_lane': {'inner_cheek_planes_x_mm': [-trial.WIDTH/2+trial.CHEEK_THICKNESS,
                                                       trial.WIDTH/2-trial.CHEEK_THICKNESS],
                           'front_foot_inboard_y_mm': foot_front+4,
                           'rear_foot': 'absent',
                           'access': 'Open underside and back, before inserting cover, glass or gasket.'},
          'physical_support_removal_tested': False,
          'reading_scope': 'Support bead samples lie below both nominal hook engagement strips. Physical catch finish and retention remain the bench trial.'}
(JOB/'support-removal-review.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
