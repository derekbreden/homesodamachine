"""One-piece ASA Aero bench float with an RC62 at its axial midplane.

Frame: open guide bore on Z, flat print bottom at Z=0. The enclosed annular
pocket is filled with the magnet during a native layer pause.
"""

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / "hardware/scripts/_rust_part.py").is_file())
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "hardware/scripts"))
if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

sys.path.insert(0, str(HERE.parents[1]))
from _float_interface import (
    diameter, bore_diameter, guide_diameter, magnet_od, magnet_id,
    magnet_thickness, magnet_tolerance, magnet_mass, pocket_od, pocket_id,
    pocket_depth, water_density, design_foam_density, minimum_reserve_lift_g,
    height_increment, layer_height, xy_contour_compensation, xy_hole_compensation,
    annular_area, pocket_volume, minimum_height, height, magnet_midplane,
    magnet_seat, pocket_roof, pause_before_z, rod_axis_from_inner_wall,
    minimum_wall_clearance, maximum_wall_clearance, magnet_above_waterline,
)


def measurements():
    displacement_cc = annular_area * height / 1000
    foam_cc = displacement_cc - pocket_volume / 1000
    table = []
    for density in (0.46, 0.53, 0.55, 0.60, 0.65, 0.70):
        mass = foam_cc * density + magnet_mass
        reserve = displacement_cc * water_density - mass
        table.append({"foam_density_g_cc": density, "assembled_mass_g": mass,
                      "reserve_lift_g": reserve,
                      "guided_upright_freeboard_mm": reserve / (water_density * annular_area / 1000)})
    return {
        "article": "One-piece ASA Aero guided bench float; RC62 inserted during printing",
        "cad_revision": "v2-upper-clearance",
        "accepted_print_reference": "mark2-print/v1/float-preflight.json; immutable v1 source commit and snapshot",
        "dimensions_mm": {"diameter": diameter, "height": height, "guide_bore": bore_diameter,
                          "bench_guide": guide_diameter,
                          "guide_radial_clearance": (bore_diameter - guide_diameter) / 2,
                          "magnet_midplane": magnet_midplane, "magnet_seat": magnet_seat,
                          "pocket_roof": pocket_roof, "pocket_od": pocket_od,
                          "pocket_id": pocket_id, "pocket_depth": pocket_depth,
                          "bore_side_collar": (pocket_id - bore_diameter) / 2,
                          "outer_band_beside_magnet": (diameter - pocket_od) / 2,
                          "foam_below_magnet": magnet_seat,
                          "foam_above_pocket": height - pocket_roof},
        "sizing": {"outcome": "Positive guided lift with a 5 g allowance for density and absorbed-water variation in a bench trial",
                   "water_density_g_cc": water_density,
                   "design_foam_density_g_cc": design_foam_density,
                   "minimum_reserve_lift_g": minimum_reserve_lift_g,
                   "minimum_calculated_height_mm": minimum_height,
                   "upward_height_rounding_mm": height_increment,
                   "equation": "H = (reserve + magnet_mass - foam_density * pocket_volume) / ((water_density - foam_density) * annular_area)",
                   "scope": "Foam density is an engineering assumption, not a measured tolerance or a water-absorption allowance proven adequate for service."},
        "volumes_cc": {"external_displacement_excluding_open_bore": displacement_cc,
                       "asa_aero": foam_cc, "magnet_pocket": pocket_volume / 1000},
        "magnet": {"model": "K&J RC62", "od_mm": magnet_od, "id_mm": magnet_id,
                   "thickness_mm": magnet_thickness, "dimensional_tolerance_mm": magnet_tolerance,
                   "mass_g": magnet_mass, "grade": "N42", "continuous_operating_limit_c": 80,
                   "source": "https://www.kjmagnetics.com/rc62-neodymium-ring-magnet"},
        "installation": {"rod_axis_from_inner_wall_mm": rod_axis_from_inner_wall,
                         "body_wall_clearance_range_mm": [minimum_wall_clearance, maximum_wall_clearance],
                         "design_magnet_above_waterline_mm": magnet_above_waterline(),
                         "scope": "Upright geometric clearances; liquid switching heights require finished-float and installed-reed calibration"},
        "buoyancy": table,
        "neutral_foam_density_g_cc": (displacement_cc * water_density - magnet_mass) / foam_cc,
        "print_intent": {"layer_height_mm": layer_height, "wall_loops": 300,
                         "pause_before_layer_z_mm": pause_before_z,
                         "xy_contour_compensation_mm": xy_contour_compensation,
                         "xy_hole_compensation_mm": xy_hole_compensation,
                         "minimum_compensated_radial_magnet_clearance_mm": min(
                             (pocket_od - magnet_od - magnet_tolerance) / 2 + xy_hole_compensation,
                             (magnet_id - magnet_tolerance - pocket_id) / 2 - xy_contour_compensation),
                         "minimum_nominal_pocket_depth_clearance_mm": pocket_depth - magnet_thickness - magnet_tolerance,
                         "scope": "Native slicing must verify the printed seat, last open-pocket layer, pause and first covering deposition. CAD midpoint is exact; the physical center depends on layer quantization and actual magnet thickness."},
        "qualification": {"density_measured": False, "buoyancy_measured": False,
                          "paused_magnet_retention_verified": False,
                          "magnet_heat_exposure_verified": False,
                          "pressure_rating": "Unqualified bench prototype",
                          "wetted_service": "Not qualified; no water uptake, pressure endurance or material-contact acceptance is recorded",
                          "upright_scope": "Guided on the bench rod; no free-floating upright stability claim"}
    }


def numbers():
    """What all_aero_float.rs cuts in the guide-bore frame."""
    from _materials import linear
    return {"diameter": diameter, "height": height, "bore_diameter": bore_diameter,
            "pocket_od": pocket_od, "pocket_id": pocket_id,
            "magnet_seat": magnet_seat, "pocket_roof": pocket_roof,
            "magnet_od": magnet_od, "magnet_id": magnet_id,
            "magnet_thickness": magnet_thickness,
            "insertion_lift": 9.0,
            "color_aero": list(linear("#EEE4C4")),
            "color_magnet": list(linear("#737D88"))}


def write(output=HERE):
    import _rust_part
    from flute_payload import cut as write_print_payload
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    _rust_part.cut('cold-core', 'all-aero-float', numbers(), output)
    write_print_payload(output / 'float-aero.step', output / 'float-aero.stl')
    info = measurements()
    (output / 'design.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps({"height_mm": height, "minimum_height_mm": minimum_height,
                      "midplane_mm": magnet_midplane, "buoyancy": info["buoyancy"]}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE)
    args = parser.parse_args()
    write(args.output)
