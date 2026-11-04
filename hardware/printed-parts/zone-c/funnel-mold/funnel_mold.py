"""Two PETG mold bodies with flat print bases and steep corbels.

Frame: funnel brim centred in XY, cavity base at Z=0, +Z is closure lift.
The cavity prints upright; the core prints inverted on its flat dry back.
Six walls and 15% gyroid fill the solid stock. Bolt pockets have open side access.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents
            if any((p/'hardware/scripts'/name).is_file() for name in ('_rust_part.py','_cadq_export.py')))
sys.path[:0] = [str(ROOT/'hardware/printed-parts/zone-c/funnel'),
                str(ROOT/'hardware/scripts')]
if __name__ == '__main__':
    import _rust_part
    _rust_part.start()
import funnel

finish_allowance = 0.30
# Dry-backing margin for the forming ramp's rounded offset joins.
forming_join_allowance = 0.01
shell_thickness = 5.0
corbel_run_per_rise = 0.5
base_thickness = 5.0
bolt_pocket_width = 12.0
flange_thickness = 5.0
flange_margin = 16.0
flange_radius = 47.0  # expanded apron tooling within the nominal chamber envelope
bolt_diameter = 5.0
bolt_edge_margin = 6.0
bolt_station = 50.0
locator_diameter = 8.0
locator_height = 3.0
locator_leadin = 1.0
locator_clearance = 0.60
locator_slot_travel = 1.5
locator_x = 25.0
locator_front_land = 11.0
rod_diameter = funnel.spout_id
rod_length = 25.0
rod_clearance = 0.40
rod_guide_length = 8.0
rod_seat_wall = shell_thickness
# The rod's lower end stands in a blind socket in the cavity floor, so the bore opens through
# the plug's bottom face. Both depths are measured below that face.
rod_socket_diameter = rod_diameter+rod_clearance
rod_socket_depth = 1.5
rod_end_depth = rod_socket_depth
vent_diameter = 4.0
pour_diameter = 11.0
floor_reserve = 0.7
pry_width = 16.0
pry_depth = 5.0
pry_height = 1.0
tolerance = 0.0001
chamber_diameter = 299.72


def _design(parts, m, minimum_backing, minimum_core_backing, containment):
    n = numbers()
    top, neck, end = m['top_z'], m['neck_z'], m['end_z']
    x, y = m['ncx'], m['ncy']
    floor, back = n['floor_z'], n['back_z']
    flange_width, flange_depth = n['flange_size']
    bolt_xy, locator_xy = n['bolt_xy'], n['locator_xy']
    base_width, base_depth = n['base_size']
    base_radius = n['base_radius']
    corbel_bottom, corbel_top = n['corbel_z']
    guide_radius = (rod_diameter+rod_clearance)/2
    guide_top = neck+rod_guide_length
    dry_radius = guide_radius+(back-guide_top)*corbel_run_per_rise
    rod_bottom = end-rod_end_depth
    rod_top = rod_bottom+rod_length
    rod_engagement = rod_top-neck
    pour, vents = n['pour_xy'], n['vent_xy']
    info = {
        'dimensions_mm': {n: [s.BoundingBox().xlen, s.BoundingBox().ylen,
                              s.BoundingBox().zlen] for n, s in parts.items()},
        'volume_ml': {n: s.Volume()/1000 for n, s in parts.items()},
        'shell_thickness_mm': shell_thickness, 'flange_thickness_mm': flange_thickness,
        'minimum_cavity_backing_mm': minimum_backing,
        'backing_join_allowance_mm': forming_join_allowance,
        'minimum_core_backing_mm': minimum_core_backing,
        'liquid_containment': containment,
        'parting_z_mm': top-floor, 'finish_allowance_mm': finish_allowance,
        'casting_scope': 'whole finished funnel with flat-bottomed integral roof apron, rectangular block, flat bearing face and straight 6 mm outlet',
        'flange_plan_mm': [flange_width, flange_depth],
        'flange_corner_radius_mm': flange_radius,
        'flange_margin_mm': flange_margin,
        'plug_blank_mm': [funnel.plug_width,
                          2*funnel.elbow_cradle.plug_half_length(funnel.plug_width/2)],
        'rod_support': {'engagement_mm': rod_guide_length-finish_allowance,
            'guide_diameter_mm': 2*guide_radius, 'dry_shank_diameter_mm': rod_diameter,
            'guide_diametral_clearance_mm': rod_clearance,
            'guide_length_mm': rod_guide_length-finish_allowance,
            'guide_top_mm': guide_top-floor,
            'guide_open': True,
            'rod_projection_above_guide_mm': rod_top-guide_top,
            'straight_dry_wall_mm': rod_seat_wall,
            'registration': 'open upper guide and lower blind floor seat',
            'retention': 'gravity; rod rests on lower floor and lifts out from the dry back',
            'air_path': 'open annular passage to dry back',
            'flash': 'trim guide overflow at bowl throat and lower-seat collar flush with block bottom'},
        'rod_socket': {'diameter_mm': rod_socket_diameter, 'depth_mm': rod_socket_depth,
            'rod_end_depth_mm': rod_end_depth, 'floor_backing_mm': shell_thickness,
            'reference': 'blind pilot seat below block bottom; bare floor establishes axial datum'},
        'rod': {'material': '304 stainless steel', 'diameter_mm': rod_diameter,
                'length_mm': rod_length, 'profile': 'straight stock cylinder',
                'supplier': 'uxcell 25-piece pack',
                'url': 'https://www.amazon.com/dp/B07Z18CKCY',
                'finishing': 'clean and apply release'},
        'funnel_to_mould_z_translation_mm': -floor,
        'finished_funnel_step_sha256': hashlib.sha256(
            (ROOT/'hardware/printed-parts/zone-c/funnel/funnel.step').read_bytes()).hexdigest(),
        'locators': {'diameter_mm': locator_diameter, 'height_mm': locator_height,
                     'radial_clearance_mm': locator_clearance, 'slot_travel_each_way_mm': locator_slot_travel,
                     'centres_xy_mm': locator_xy},
        'clamping': {'hole_diameter_mm': bolt_diameter, 'centres_xy_mm': bolt_xy,
                     'fastener': 'M4 x 20 with 9 mm OD washers and nuts; or small clamps on flange'},
        'ports': {'fill_diameter_mm': pour_diameter, 'vent_diameter_mm': vent_diameter,
                  'fill_xy_mm': pour, 'vent_xy_mm': vents},
        'print_bases': {'cavity_plan_mm': [base_width, base_depth],
            'cavity_corner_radius_mm': base_radius, 'base_thickness_mm': base_thickness,
            'corbel_run_per_rise': corbel_run_per_rise,
            'corbel_angle_from_bed_deg': math.degrees(math.atan(1/corbel_run_per_rise)),
            'corbel_print_z_mm': [base_thickness, corbel_top-floor],
            'bolt_access_pocket_width_mm': bolt_pocket_width,
            'bolt_access_open_downward': True,
            'bolt_access_inner_wall_height_mm': (bolt_edge_margin+4.6)/corbel_run_per_rise,
            'core': 'flat dry back with one circular tapered access hole'},
        'dry_opening_mm': 2*dry_radius,
        'dry_opening_depth_mm': 2*dry_radius,
        'dry_opening_shape': 'circular conical access to straight rod guide',
        'postprint_breathers': breathers(base_width, back-floor),
        'ramp_print_z_mm': {'cavity': [neck-floor, m['ramp_top_z']-floor],
                            'core': [back-m['ramp_top_z'], back-neck]},
        'nominal_chamber_diameter_mm': chamber_diameter,
        'load_screen': load_screen(m, end),
        'status': 'Complete two-body tooling with flat print bases and straight stock steel rod; native geometry verified'}
    return info


def breathers(base_width, core_back):
    return {'diameter_mm': 1.5,
        'cavity': {'entry_xyz_mm': [[-base_width/2, -30, 2.5], [base_width/2, 30, 2.5]],
            'drill_axes': [[1, 0, 0], [-1, 0, 0]], 'depth_mm': 3.2,
            'face': 'vertical sides of the flat base, clear of the catch tray'},
        'core': {'entry_xyz_mm': [[-40, -30, core_back], [40, 30, core_back]],
            'drill_axes': [[0, 0, -1], [0, 0, -1]], 'depth_mm': 1.8,
            'face': 'flat outer dry back'},
        'method': 'Drill through the printed skins into sparse infill after printing with a depth stop; keep dry faces and holes uncoated. CAD blind holes would receive sealed slicer walls.'}


def load_screen(m, bottom):
    span = m['w']
    pressure = 0.001  # N/mm² = 1 kPa, including head and a modest process allowance.
    head = m['top_z']+flange_thickness-bottom
    return {'model': 'silicone hydrostatic head and conservative uniform process-load screen',
            'span_mm': span, 'pressure_kpa': pressure*1000,
            'silicone_density_assumption_kg_m3': 1130,
            'maximum_silicone_head_mm': head, 'head_pressure_kpa': 1130*9.81*(head/1000)/1000,
            'pressure_force_n': pressure*span**2,
            'condition': 'complete mold inside chamber; fill, vents, rod guide and drilled dry-side infill breathers open to chamber air',
            'process': 'six walls, six top/bottom layers and 15% gyroid; slow evacuation and venting while silicone is fluid',
            'scope': 'Applied liquid load only. No stiffness, lifetime or pressure rating is inferred from infill percentage.'}


def numbers():
    """Current mold dimensions and stations, beside the authored funnel dimensions."""
    n = funnel.numbers()
    keys = ('finish_allowance', 'forming_join_allowance', 'shell_thickness',
            'corbel_run_per_rise', 'base_thickness', 'bolt_pocket_width',
            'flange_thickness', 'flange_margin', 'flange_radius', 'bolt_diameter',
            'bolt_edge_margin', 'bolt_station', 'locator_diameter', 'locator_height',
            'locator_leadin', 'locator_clearance', 'locator_slot_travel', 'locator_x',
            'locator_front_land', 'rod_diameter', 'rod_length', 'rod_clearance',
            'rod_guide_length', 'rod_seat_wall', 'rod_socket_diameter', 'rod_socket_depth',
            'rod_end_depth', 'vent_diameter', 'pour_diameter', 'floor_reserve',
            'pry_width', 'pry_depth', 'pry_height', 'tolerance', 'chamber_diameter')
    n.update({key: globals()[key] for key in keys})
    top, end = n['top_z'], n['end_z']
    floor = end-rod_socket_depth-shell_thickness-floor_reserve
    back = top+flange_thickness
    width = funnel.apron_width+2*flange_margin
    depth = funnel.apron_depth+2*abs(funnel.apron_y)+2*flange_margin
    bx, by = width/2-bolt_edge_margin, depth/2-bolt_edge_margin
    z0, z1 = floor+base_thickness, top-flange_thickness
    run = (z1-z0)*corbel_run_per_rise
    port_x = funnel.apron_width/2-14.5
    front_y = funnel.apron_y-funnel.apron_depth/2+10.0
    rear_y = funnel.apron_y+funnel.apron_depth/2-12.0
    locator_front = funnel.apron_y-funnel.apron_depth/2-locator_front_land
    n.update({
        'floor_z': floor, 'back_z': back, 'flange_size': [width, depth],
        'base_size': [width-2*run, depth-2*run], 'base_radius': flange_radius-run,
        'corbel_z': [z0, z1], 'bolt_limits': [bx, by],
        'bolt_xy': [(side*bx, station*bolt_station) for side in (-1, 1) for station in (-1, 1)]
                   + [(station*bolt_station, side*by) for side in (-1, 1) for station in (-1, 1)],
        'locator_xy': [(locator_x, locator_front), (-locator_x, locator_front)],
        'pour_xy': [-port_x, front_y],
        'vent_xy': [(port_x, front_y), (port_x, rear_y), (-port_x, rear_y),
                    (-funnel.apron_width/2+7.0, 0), (funnel.apron_width/2-7.0, 0)],
    })
    from _materials import linear
    for name, color in {'cavity': '#3D9998', 'core': '#D8A751',
                        'funnel': '#555C68', 'rod': '#AAB9C8'}.items():
        n[name+'_color'] = list(linear(color))
    return n


class _PartFacts:
    def __init__(self, facts):
        self.facts = facts

    def BoundingBox(self):
        from types import SimpleNamespace
        low, high = self.facts['bounds']
        return SimpleNamespace(xlen=high[0]-low[0], ylen=high[1]-low[1], zlen=high[2]-low[2])

    def Volume(self):
        return self.facts['volume_mm3']


def main(output):
    import _rust_part
    n = numbers()
    output.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('funnel', 'funnel-mold', n, output)
    facts = {row['name']: {'bounds': [row['min'], row['max']], 'volume_mm3': row['volume']}
             for row in said['bodies'][:4]}
    facts['checks'] = said['bodies'][0]['checks']
    parts = {name: _PartFacts(facts[name]) for name in ('cavity', 'core', 'funnel', 'rod')}
    m = {'w': funnel.collar_w, 'd': funnel.collar_d,
         'top_z': n['top_z'], 'ramp_top_z': n['ramp_z'][0],
         'neck_z': n['ramp_z'][1], 'end_z': n['end_z'],
         'ncx': funnel.neck_dx, 'ncy': funnel.neck_dy,
         'out_w': funnel.apron_width, 'out_d': funnel.apron_depth+2*abs(funnel.apron_y)}
    check = facts['checks']
    info = _design(parts, m, check['minimum_cavity_backing_mm'],
                   check['minimum_core_backing_mm'], check['liquid_containment'])
    info['cavity_backing_scope'] = check['cavity_backing_scope']
    import numpy as np
    radii = []
    dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
    for name in ('cavity', 'core'):
        facets = np.frombuffer((output/f'{name}.stl').read_bytes(), dtype=dtype, offset=84)
        xy = facets['vertices'][:, :, :2].astype(np.float64)
        radii.append(float(np.linalg.norm(xy, axis=2).max()))
    info['enclosing_diameter_mm'] = 2*max(radii)
    info['chamber_radial_clearance_mm'] = chamber_diameter/2-max(radii)
    assert info['chamber_radial_clearance_mm'] > 0
    info['volume_measurement_scope'] = 'Numerical integration of the fine f64 models; printed facets have their own bound records.'
    info['shell_sha256'] = {f'{name}.{suffix}': hashlib.sha256((output/f'{name}.{suffix}').read_bytes()).hexdigest()
                           for name in ('cavity', 'core') for suffix in ('step', 'stl', 'step.mesh', 'step.npz')}
    info['status'] = 'Complete two-body tooling with flat print bases and straight stock steel rod; authored fine geometry verified'
    (output/'design.json').write_text(json.dumps(info, indent=2)+'\n')
    print('-> mold bodies, tooling views, fine models, print meshes and design.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'hardware/printed-parts/zone-c/funnel-mold')
    args = parser.parse_args()
    main(args.output)
