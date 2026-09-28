"""Read emitted support roads below both hooks or receiver ledges, labelled or not."""

import json
import math
import sys
from pathlib import Path

import numpy as np

import types
import retention_reach_trial as reach
trial = types.SimpleNamespace(**vars(reach.base))

job = Path(sys.argv[1]).resolve()
preparation = json.loads((job/'preparation.json').read_text())
verification = json.loads((job/'verification.json').read_text())
part, = preparation['parts']
trial.COVER_NAME=part['name']
trial.SHOULDER_DEPTH=reach.shoulder(reach.VARIANTS[part['name']])
segments = json.loads((job/'support-segments.json').read_text())
center = np.array(part['source_center_mm'])
translation = np.array(part['plate_translation_mm'])
a = np.array([s['a'] for s in segments])
b = np.array([s['b'] for s in segments])
points = np.concatenate([a, (a+b)/2, b])
radii = np.tile(np.array([s['width']/2 for s in segments]), 3)
is_cover = part['name'] == trial.COVER_NAME
if is_cover:
    assert part['rotation_x_degrees'] == 180
    points = (points-translation)*np.array([1, -1, -1])+center
    along = points[:, 1]
    gap = points[:, 2]+trial.SHOULDER_DEPTH
    inner = trial.SKIRT_OUTER
    removal = 'Two fully exposed outside lanes; peel supports outward beside the bezel.'
else:
    assert part['name'] == trial.RECEIVER_NAME and part['rotation_x_degrees'] == 0
    points += center-translation
    angle = math.radians(trial.ANGLE)
    plane = -trial.CATCH
    along = (points[:, 1]+plane*math.sin(angle))/math.cos(angle)
    height = points[:, 1]*math.tan(angle)+plane/math.cos(angle)-trial.BASE_Z
    gap = height-points[:, 2]
    inner = trial.CATCH_EDGE
    removal = 'Open underside and back, inside the cheeks, before inserting the cover or display.'

contacts = []
for side in (-1, 1):
    x = side*points[:, 0]
    mask = ((x+radii >= inner) & (x-radii <= trial.SKIRT_OUTER+trial.LIP)
            & (abs(along) <= trial.SPAN/2) & (gap >= 0) & (gap <= .6))
    assert mask.sum() > 10, side
    extent = [float(along[mask].min()), float(along[mask].max())]
    assert extent[1]-extent[0] > trial.SPAN-5, (side, extent)
    assert abs(float(gap[mask].min())-.24)<.001, gap[mask].min()
    contacts.append({'side': side, 'road_samples_below_bearing': int(mask.sum()),
                     'local_along_leaf_span_mm': extent,
                     'vertical_distance_to_nominal_bearing_plane_mm':
                     [float(gap[mask].min()), float(gap[mask].max())]})
audit = json.loads((job/('support-audit-'+part['name']+'.json')).read_text())
report = {'pass': True, 'native_archive_sha256': verification['native_archive_sha256'],
          'gcode_sha256': verification['gcode_sha256'], 'part': part['name'],
          'support_road_segments_examined': len(segments), 'include_unlabelled_support': True,
          'contacts_below_both_bearings': contacts, 'summary': audit['summary'],
          'removal_lane': removal, 'physical_support_removal_tested': False,
          'visible_round_policy': 'Bezel rounds are in XY; the small inner leaf-root fillets are hidden structural faces.',
          'reading_scope': 'Support roads span both square bearings. This does not measure printed finish, removal effort, insertion force or retention.'}
(job/'support-removal-review.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
