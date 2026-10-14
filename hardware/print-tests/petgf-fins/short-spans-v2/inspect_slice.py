"""Read one saved diagnostic slice. Manual evidence collection, no build integration."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import zipfile

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from review import segments


def footprint(paths):
    return unary_union([LineString([p['a'][:2], p['b'][:2]]).buffer(p['width']/2)
                        for p in paths])


def main():
    archive = Path(sys.argv[1]).resolve()
    stem = archive.name.removesuffix('.gcode.3mf')
    spec = json.loads((HERE / f'{stem}.print.json').read_text())
    with zipfile.ZipFile(archive) as z:
        raw = z.read('Metadata/plate_1.gcode')
        checksum = z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        settings = json.loads(z.read('Metadata/project_settings.config'))
    text = raw.decode()
    paths = segments(text)
    lo, hi = np.full(2, np.inf), np.full(2, -np.inf)
    for p in paths:
        xy = np.asarray([p['a'][:2], p['b'][:2]])
        lo = np.minimum(lo, xy.min(axis=0)-p['width']/2)
        hi = np.maximum(hi, xy.max(axis=0)+p['width']/2)
    rows = []
    for part in spec['parts']:
        own = [p for p in paths if p['object'] == part['identify_id']]
        bed = footprint([p for p in own if math.isclose(p['z'], .2, abs_tol=1e-4)])
        joined = bed.buffer(.005).buffer(-.005)
        bodies = list(joined.geoms) if joined.geom_type == 'MultiPolygon' else [joined]
        row = {'id': part['id'], 'deposited_segments': len(own),
               'model_max_nozzle_z_mm': max(p['z'] for p in own),
               'bed_components': len(bodies),
               'bed_component_separation_mm': min(
                   (a.distance(b) for i,a in enumerate(bodies) for b in bodies[i+1:]), default=None)}
        if 'first_roof_nozzle_z_mm' in part:
            axis = 0 if part['bridge_axis'] == 'X' else 1
            trans = np.asarray(part['plate_translation_mm'])
            lower = [p for p in own if abs(p['z']-part['roof_bottom_z_mm']) < 1e-4]
            below = footprint(lower)
            roof_lo, roof_hi = np.asarray(part['roof_bounds_local_mm']) + trans
            roof = [p for p in own if abs(p['z']-part['first_roof_nozzle_z_mm']) < 1e-4
                    and all(roof_lo[i]-.01 <= (p['a'][i]+p['b'][i])/2 <= roof_hi[i]+.01 for i in (0,1))]
            clear_lo, clear_hi = np.asarray(part['clear_span_bounds_local_mm'])+trans[axis]
            axial = [p for p in roof
                     if abs(p['a'][1-axis]-p['b'][1-axis]) < .005
                     and min(p['a'][axis],p['b'][axis]) < clear_lo+.1
                     and max(p['a'][axis],p['b'][axis]) > clear_hi-.1]
            bridge = [p for p in axial if p['feature'] == 'Bridge']
            row.update(first_roof_z_mm=part['first_roof_nozzle_z_mm'], bridge_axis=part['bridge_axis'],
                       axial_cross_span_moves=len(axial), axial_bridge_rasters=len(bridge),
                       axial_move_lengths_mm=sorted({round(abs(p['a'][axis]-p['b'][axis]),4) for p in axial}),
                       bridge_speed_mm_s=sorted({round(p['speed'],4) for p in bridge}),
                       roof_fan_pwm=sorted({p['fan'] for p in roof}),
                       roof_extrusion_heights_mm=sorted({p['height'] for p in roof}),
                       first_roof_extrusion_line=roof[0]['line'],
                       first_roof_endpoint_distances_to_prior_beads_mm=[
                           Point(roof[0][key][:2]).distance(below) for key in ('a','b')],
                       axial_endpoint_distance_max_mm=max(
                           (Point(p[key][:2]).distance(below) for p in axial for key in ('a','b')), default=None),
                       maximum_unsupported_axial_move_mm=max(
                           (LineString([p['a'][:2],p['b'][:2]]).difference(below).length for p in axial), default=None))
            if part['kind'] == 'fin_landing_bridge':
                row['lower_tooth_height_mm'] = sorted({p['height'] for p in lower})
                tips = []
                tooth_centers = [p[0] for p in part.get('lower_teeth_center_and_width_mm',
                    ((.4, .8), (2, .5), (4, .5), (6, .5), (8, .5), (10, .5), (11.6, .8)))]
                for y in tooth_centers:
                    a = np.array([3+part['clear_span_mm']+.02, y])
                    b = np.array([roof_hi[0]-trans[0]+.22, y])
                    if axis == 1:
                        a, b = np.array([-a[1],a[0]]), np.array([-b[1],b[0]])
                        b[1] = roof_hi[1]-trans[1]+.22
                    a, b = a+trans[:2], b+trans[:2]
                    tips.append(LineString([a,b]).difference(below.buffer(.005)).length)
                row['lower_tooth_probe_missing_lengths_mm'] = tips
        if part['kind'] == 'slope':
            active = [p for p in own if p['z'] >= part['underside_start_z_mm']]
            row.update(angle_from_bed_degrees=part['angle_from_bed_degrees'],
                       orientation=part['orientation'],
                       fan_pwm_by_feature={f:sorted({p['fan'] for p in active if p['feature']==f})
                                           for f in sorted({p['feature'] for p in active})})
        rows.append(row)
    ramps_end = max(r['model_max_nozzle_z_mm'] for r in rows if r['id'][0] in ('S','R'))
    onsets = {str(s): min(r['first_roof_z_mm'] for r in rows if r.get('first_roof_z_mm')
                        and r['id'] in (f'C{s}',f'F{s}')) for s in (2,4,6,8)}
    keys = ('enable_support','brim_type','layer_height','initial_layer_print_height','filament_type',
            'filament_colour','filament_density','nozzle_diameter','filament_nozzle_map',
            'fan_min_speed','fan_max_speed','overhang_fan_speed','full_fan_speed_layer',
            'close_fan_the_first_x_layers','nozzle_temperature','nozzle_temperature_initial_layer',
            'filament_bridge_speed','curr_bed_type')
    record = {'native_archive':archive.name,
              'native_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
              'gcode_sha256':hashlib.sha256(raw).hexdigest(),
              'embedded_md5_matches':hashlib.md5(raw).hexdigest()==checksum,
              'trim_commands':re.findall(r'^\s*G29\.1[^\n]*',text,re.M),
              'printed_layers':len(re.findall(r'^; CHANGE_LAYER',text,re.M)),
              'effective_settings':{k:settings.get(k) for k in keys},
              'model_bead_xy_bounds_mm':[lo.tolist(),hi.tolist()],
              'minimum_model_bead_edge_inset_mm':min(lo[0],lo[1],325-hi[0],320-hi[1]),
              'support_extrusion_segments':sum(p['feature'].startswith('Support') for p in paths),
              'ramps_last_nozzle_z_mm':ramps_end,'bridge_onsets_by_span_mm':onsets,
              'specimens':rows,
              'limits':'Commanded paths and bead envelopes; physical sag, attachment and strength are unmeasured.'}
    (HERE / f'{stem}.native-review.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'archive':archive.name,'checksum_ok':record['embedded_md5_matches'],
                      'edge_inset_mm':record['minimum_model_bead_edge_inset_mm'],
                      'ramps_end_z_mm':ramps_end,'bridge_onsets':onsets,
                      'bridges':[r for r in rows if 'first_roof_z_mm' in r],
                      'slope_fans':{r['id']:r['fan_pwm_by_feature'] for r in rows if 'fan_pwm_by_feature' in r}}))


if __name__ == '__main__':
    main()
