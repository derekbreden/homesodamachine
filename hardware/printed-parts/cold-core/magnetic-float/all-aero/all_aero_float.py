"""One-piece ASA Aero bench float with an RC62 at its axial midplane.

Frame: open guide bore on Z, flat print bottom at Z=0. The enclosed annular
pocket is filled with the magnet during a native layer pause.
"""

import json
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / "hardware/scripts/_cadq_export.py").is_file())
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _cadq_export import export_assembly
from _materials import one_body
from flute_payload import cut as write_print_payload

diameter = 36.0
bore_diameter = 4.8
guide_diameter = 3.175
magnet_od = 19.05
magnet_id = 9.525
magnet_thickness = 3.175
magnet_tolerance = 0.1
magnet_mass = 5.09
pocket_od = 19.35
pocket_id = 9.225
pocket_depth = 3.4
water_density = 0.9997
design_foam_density = 0.65
minimum_reserve_lift_g = 5.0
height_increment = 1.0
layer_height = 0.2
xy_contour_compensation = 0.05
xy_hole_compensation = -0.05

annular_area = math.pi * ((diameter / 2) ** 2 - (bore_diameter / 2) ** 2)
pocket_volume = math.pi * ((pocket_od / 2) ** 2 - (pocket_id / 2) ** 2) * pocket_depth
# Buoyancy is water displacement less foam and magnet mass. Pocket air is not
# charged as foam. Round upwards to a whole millimetre for this bench article.
minimum_height = ((minimum_reserve_lift_g + magnet_mass
                   - design_foam_density * pocket_volume / 1000)
                  / ((water_density - design_foam_density) * annular_area / 1000))
height = math.ceil(minimum_height / height_increment) * height_increment
magnet_midplane = height / 2
magnet_seat = magnet_midplane - magnet_thickness / 2
pocket_roof = magnet_seat + pocket_depth
pause_before_z = math.ceil(pocket_roof / layer_height - 1e-9) * layer_height


def annulus(outer_radius, inner_radius, bottom, top):
    return (cq.Workplane("XY").workplane(offset=bottom)
            .circle(outer_radius).circle(inner_radius).extrude(top - bottom).val())


def build():
    envelope = annulus(diameter / 2, bore_diameter / 2, 0, height)
    pocket = annulus(pocket_od / 2, pocket_id / 2, magnet_seat, pocket_roof)
    body = envelope.cut(pocket).clean()
    magnet = annulus(magnet_od / 2, magnet_id / 2,
                     magnet_seat, magnet_seat + magnet_thickness)
    assert body.isValid() and len(body.Solids()) == 1
    assert body.intersect(magnet).Volume() < 1e-7
    return body, magnet


def measurements(body):
    displacement_cc = annular_area * height / 1000
    foam_cc = body.Volume() / 1000
    assert abs(foam_cc - (displacement_cc - pocket_volume / 1000)) < 1e-7
    table = []
    for density in (0.46, 0.53, 0.55, 0.60, 0.65, 0.70):
        mass = foam_cc * density + magnet_mass
        reserve = displacement_cc * water_density - mass
        table.append({"foam_density_g_cc": density, "assembled_mass_g": mass,
                      "reserve_lift_g": reserve,
                      "guided_upright_freeboard_mm": reserve / (water_density * annular_area / 1000)})
    return {
        "article": "One-piece ASA Aero guided bench float; RC62 inserted during printing",
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


def write():
    body, magnet = build()
    foam_color, magnet_color = cq.Color("#EEE4C4"), cq.Color("#737D88")
    export_assembly(one_body(cq.Workplane(obj=body), "float-aero", foam_color),
                    str(HERE / "float-aero.step"))
    stl = HERE / "float-aero.stl"
    cq.exporters.export(body, str(stl), tolerance=0.01, angularTolerance=0.06)
    mesh = trimesh.load(stl, force="mesh", process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent
    mesh.export(stl)
    write_print_payload(HERE / "float-aero.step", stl)
    half = (cq.Workplane("XY").box(diameter + 2, diameter, height + 2,
            centered=(True, True, False)).translate((0, -diameter / 2, -1)).val())
    open_body = body.intersect(cq.Workplane("XY").box(diameter + 2, diameter + 2, pocket_roof,
                              centered=(True, True, False)).val())
    for name, cut in (("assembly", None), ("section", half)):
        view = cq.Assembly(name=f"all-aero-float-{name}")
        view.add(body if cut is None else body.intersect(cut), name="float-aero", color=foam_color)
        view.add(magnet if cut is None else magnet.intersect(cut), name="RC62", color=magnet_color)
        export_assembly(view, str(HERE / f"{name}.step"))
    insertion = cq.Assembly(name="all-aero-float-magnet-insertion")
    insertion.add(open_body, name="printed-open-pocket", color=foam_color)
    insertion.add(magnet.translate((0, 0, 9)), name="insert-RC62", color=magnet_color)
    export_assembly(insertion, str(HERE / "insertion.step"))
    info = measurements(body)
    (HERE / "design.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps({"height_mm": height, "minimum_height_mm": minimum_height,
                      "midplane_mm": magnet_midplane, "buoyancy": info["buoyancy"]}, indent=2))


if __name__ == "__main__":
    write()
