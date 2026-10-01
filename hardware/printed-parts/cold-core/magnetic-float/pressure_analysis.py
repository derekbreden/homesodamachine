"""Pressure loads and thickness sensitivity for the sealed bench float.

MPa = N/mm². The elastic ovalization screen is a homogeneous-ring approximation;
its stiffness and imperfection factors are assumptions, not FDM allowables.
"""

import json
import math
from pathlib import Path

import magnetic_float as m

HERE = Path(__file__).resolve().parent
PSI_TO_MPA = 0.006894757293168


def calculate():
    loads = []
    for psi in (90, 125, 180):
        p = psi * PSI_TO_MPA
        R, a, b, c = m.outer_radius, m.core_outer_radius, m.bore_radius, m.core_inner_radius
        loads.append({
            'external_pressure_psi': psi, 'differential_MPa': p,
            'annular_end_load_N': p * math.pi * (R * R - b * b),
            'outer_wall_maximum_hoop_compression_MPa': 2 * p * R * R / (R * R - a * a),
            'bore_wall_maximum_hoop_tension_MPa': p * (c * c + b * b) / (c * c - b * b),
            'axial_average_compression_MPa': p * (R * R - b * b) / (R * R - a * a + c * c - b * b),
            'foam_contact_pressure_MPa_if_it_takes_full_load': p,
        })
    sensitivity = []
    for thickness in (1.0, 1.8, 2.4, 3.0):
        radius = m.outer_radius - thickness / 2
        for modulus in (1000, 1420):
            ideal = modulus / (4 * (1 - 0.38 ** 2)) * (thickness / radius) ** 3
            sensitivity.append({
                'outer_diameter_mm': m.diameter, 'wall_mm': thickness,
                'assumed_modulus_MPa': modulus, 'assumed_Poisson_ratio': 0.38,
                'ideal_ovalization_pressure_psi': ideal / PSI_TO_MPA,
                'at_50_percent_of_ideal_psi': 0.5 * ideal / PSI_TO_MPA,
            })
    comparisons = []
    for diameter, height, outer, bore_wall, floor, roof, bore in (
        (28, 50, 1, 1, 1, 1, 6),
        (28, 50, 3, 1.8, 3, 3, 4.8),
        (m.diameter, m.height, m.outer_wall, m.bore_wall, m.floor, m.roof, m.bore_diameter),
    ):
        displaced = math.pi * ((diameter / 2) ** 2 - (bore / 2) ** 2) * height / 1000
        interior = math.pi * ((diameter / 2 - outer) ** 2 - (bore / 2 + bore_wall) ** 2) * (height - floor - roof) / 1000
        magnet = math.pi * ((m.magnet_od / 2) ** 2 - (m.magnet_id / 2) ** 2) * m.magnet_height / 1000
        pocket = math.pi * ((m.magnet_pocket_od / 2) ** 2 - (m.magnet_pocket_id / 2) ** 2) * m.magnet_pocket_depth / 1000
        lead_relief = 2 * math.pi * m.insertion_lead ** 2 * (diameter / 2 - outer + bore / 2 + bore_wall) / 1000
        relief = pocket - magnet + lead_relief
        mass = (displaced - interior) * m.petg_density + (interior - magnet - relief) * 0.55 + m.magnet_mass
        comparisons.append({'diameter_mm': diameter, 'height_mm': height, 'outer_wall_mm': outer,
                            'bore_wall_mm': bore_wall, 'floor_mm': floor, 'roof_mm': roof,
                            'bore_mm': bore, 'aero_density_g_cc': 0.55,
                            'assembly_relief_cc': relief,
                            'assembled_mass_g': mass, 'reserve_lift_g': displaced - mass})
    return {
        'geometry': m.measurements(m.build())['dimensions_mm'],
        'load_basis': 'Ambient-pressure sealed interior; full exterior gauge pressure, no load credit for foam.',
        'stress_model': 'Lame thick-cylinder hoop stresses away from ends; axial stress averaged over both PETG tubes.',
        'loads': loads,
        'ovalization_model': 'p = E/(4*(1-nu^2)) * (t/mean_radius)^3, NASA SP-8007 Rev 2 equation 27 at gamma=1.',
        'model_limits': 'Screen only: short, relatively thick, anisotropic printed shell with flat ends and foam. The formula does not validate its buckling pressure, creep life, end caps, layer bonds or sealing. The 50% column is a sensitivity assumption, not a qualified knockdown factor.',
        'sources': {
            'shell_formula': 'https://ntrs.nasa.gov/citations/20205011530',
            'petg_translucent_XY_Youngs_modulus_1420_MPa': 'https://cdn.shopify.com/s/files/1/0574/3116/2995/files/Bambu_PETG_Translucent_Technical_Data_Sheet.pdf?v=1704680051',
            'successful_water_recipe': 'petg-water-recipe.json',
            'sphere_thread_leak_commit': 'b7dc4d576e9dc38794d190f31473f31d71aa4aa1',
        },
        'stiffness_basis': '1420 MPa is the published PETG Translucent mean XY Young\'s modulus (reported spread ±160 MPa) for specimens conditioned at 65 C for 8 h. This is a material screen input, not the printed shell\'s measured modulus. 1000 MPa is an assumed reduced-stiffness scenario, not measured creep data.',
        'thickness_sensitivity': sensitivity, 'buoyancy_geometry_comparison': comparisons,
        'pressure_rating': 'No float pressure test recorded.',
    }


if __name__ == '__main__':
    result = calculate()
    (HERE / 'pressure-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['loads'], indent=2))
