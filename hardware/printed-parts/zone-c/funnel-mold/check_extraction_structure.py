"""Read continuous load-bearing stock from the STEP and screen nominal sections.

Run with tools/cad-venv/bin/python. Forces are analysis inputs, not a lifting
rating. The closed-form sections omit local stress concentrations and print
defects; they do not measure extraction force or establish material allowables.
"""
from pathlib import Path
import hashlib
import json
import math
import cadquery as cq
import funnel_mold as mold

here = Path(__file__).resolve().parent
read = lambda name: cq.importers.importStep(str(here / f'funnel-mold-{name}.step')).val()
cavity, core = read('cavity'), read('core')
top = cavity.BoundingBox().zmax
column_height = top - 3.0
wall_height = top - mold.lip_h - mold.station_top_gap
records = []
for angle in range(0, 360, 90):
    column = mold._quarter(mold._cyl(mold.column_radius, column_height, 0,
                                    mold.jack_x, mold.washer_y), angle)
    root_end = mold.jack_x - mold.nut_slot_width / 2 - 1.0
    arm = mold._quarter(mold._box(root_end-mold.station_arm_root,
        mold.station_arm_width, top, top+mold.plate_thk,
        (root_end+mold.station_arm_root)/2), angle)
    column_missing = column.cut(cavity).Volume()
    arm_missing = arm.cut(core).Volume()
    blade = mold._quarter(mold._box(mold.guide_width-1.2, mold.guide_depth-1.2,
        top-mold.guide_drop+0.8, top, mold.guide_x, mold.guide_y), angle)
    blade_missing = blade.cut(core).Volume()
    assert column_missing < 0.001, (angle, 'column neck or void', column_missing)
    assert arm_missing < 0.001, (angle, 'arm root is interrupted', arm_missing)
    assert blade_missing < 0.001, (angle, 'guide blade is interrupted', blade_missing)
    records.append({'station_degrees': angle,
                    'missing_column_stock_mm3': column_missing,
                    'missing_arm_root_stock_mm3': arm_missing,
                    'missing_inscribed_blade_stock_mm3': blade_missing})

radius = mold.column_radius
column_area = math.pi * radius**2
column_section_modulus = math.pi * radius**3 / 4
arm_span = mold.jack_x-mold.station_arm_root
arm_width, arm_height = mold.station_arm_width, mold.plate_thk
arm_inertia = arm_width * arm_height**3 / 12
wall_span = mold.jack_x-mold.station_root
wall_width = 2 * mold.station_wall
nut_roof = mold.plate_thk-(1.2+mold.nut_slot_height)
nut_area = mold.nut_width**2-math.pi*(mold.jack_hole/2)**2
_, _, funnel = mold.HF.build_solids()
mouth_area = funnel['bore_w'] * funnel['bore_d']
sealed_mouth_force = 0.101325 * mouth_area
modulus = 1000.0

def load_case(force):
    bending = force * abs(mold.washer_y-mold.jack_y) / column_section_modulus
    return {
        'force_per_jack_N': force,
        'four_equal_jacks_total_N': 4*force,
        'column_max_nominal_normal_stress_MPa': force/column_area+bending,
        'arm_root_nominal_bending_MPa': force*arm_span*(arm_height/2)/arm_inertia,
        'arm_tip_deflection_at_assumed_modulus_mm': force*arm_span**3/(3*modulus*arm_inertia),
        'paired_wall_nominal_bending_MPa': 6*force*wall_span/(wall_width*wall_height**2),
        'nut_average_bearing_pressure_MPa': force/nut_area,
        'nut_roof_simple_beam_screen_MPa': 3*force*mold.nut_slot_width/(2*mold.nut_width*nut_roof**2),
    }

def lateral_case(force):
    width, depth = mold.guide_width-1.2, mold.guide_depth-1.2
    reach = mold.guide_drop
    # The inscribed rectangle remains inside the corner chamfers and travel mark.
    inertia_x, inertia_y = width*depth**3/12, depth*width**3/12
    return {'tip_force_N': force, 'free_reach_mm': reach,
        'inscribed_section_mm': [width, depth],
        'radial_load_root_nominal_bending_MPa': force*reach*(width/2)/inertia_y,
        'tangential_load_root_nominal_bending_MPa': force*reach*(depth/2)/inertia_x,
        'radial_tip_deflection_at_assumed_modulus_mm': force*reach**3/(3*modulus*inertia_y),
        'tangential_tip_deflection_at_assumed_modulus_mm': force*reach**3/(3*modulus*inertia_x)}

report = {
    'purpose': 'Continuous stock verification and nominal section screening; no rated lifting load.',
    'source_sha256': hashlib.sha256((here/'funnel_mold.py').read_bytes()).hexdigest(),
    'step_sha256': {n: hashlib.sha256((here/f'funnel-mold-{n}.step').read_bytes()).hexdigest()
                   for n in ('cavity', 'core')},
    'continuous_stock_checks': records,
    'sections_mm': {'column_diameter': 2*radius, 'column_height': column_height,
        'column_area_mm2': column_area, 'screw_eccentricity': abs(mold.washer_y-mold.jack_y),
        'arm_width': arm_width, 'arm_height': arm_height, 'arm_screen_span': arm_span,
        'wall_pair_total_thickness': wall_width, 'wall_height': wall_height,
        'wall_screen_span': wall_span, 'nut_roof': nut_roof,
        'guide_blade': [mold.guide_width, mold.guide_depth],
        'guide_root_shoulder': mold.guide_root_run},
    'assumed_elastic_modulus_MPa': modulus,
    'suction_sensitivity': {'condition': 'Hypothetical perfect vacuum over the entire core mouth at one standard atmosphere outside; excludes adhesion and friction.',
        'mouth_width_mm': funnel['bore_w'], 'mouth_depth_mm': funnel['bore_d'],
        'projected_area_mm2': mouth_area, 'total_force_N': sealed_mouth_force,
        'equal_force_per_jack_N': sealed_mouth_force/4},
    'load_cases': [load_case(f) for f in (250.0, sealed_mouth_force/4, 1000.0)],
    'lateral_guide_cases': [lateral_case(f) for f in (50.0, 100.0)],
    'model_limits': [
        'Column: eccentric compression on a solid circular section, ignoring the additional stiffness of its walls.',
        'Arm and paired walls: rectangular cantilevers fixed at the stated roots. The true mold distributes load in three dimensions.',
        'Nut: mean pressure over its square footprint excluding the printed clearance bore. The roof screen is an 8 mm wide beam spanning the 8.4 mm slot under a central point load.',
        'Guide: full free reach loaded at its tip in either horizontal direction. The 10.8 x 38.8 mm inscribed rectangle excludes corner chamfers and the shallow travel mark; the 6 mm root shoulder and guide-sleeve restraint receive no stiffness credit.',
        'Local stress concentrations, interlayer defects, creep, coating adhesion and silicone extraction force are not quantified.',
        'No factor of safety or certified capacity is inferred from supplier coupon strengths.',
    ],
    'material_reference': {
        'url': 'https://store.bblcdn.com/fd2c725549734dcd9c14004fdca8a4d4.pdf',
        'title': 'Bambu PETG Translucent Technical Data Sheet V1.0',
        'tensile_Z_typical_MPa': 29, 'bending_Z_typical_MPa': 55,
        'specimen_note': 'Supplier specimens were dried/annealed at 65 C for eight hours. Values are comparative coupon data, not allowables for this unannealed tooling.',
    },
}
(here/'extraction-loads.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'continuous_stock_checks': records, 'load_cases': report['load_cases']}, indent=2))
