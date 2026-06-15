"""Magnet float — printed buoyant puck that rides the level-sensing rod
in a flavor reservoir, carrying an embedded neodymium ring magnet the
external wall reeds track. The ring drops into an open-top pocket during
a print pause and is sealed under a bridged PETG roof, so the only wetted
material is food-grade PETG and the only wetted metal stays the SS rod.

Frame: +Z is the float axis (vertical, and the print-up direction); the
part is axisymmetric about Z at world (X, Y) = (0, 0). The rod runs along
Z through the center bore; the ring magnet sits concentric at the bottom
of the internal cavity, with the buoyancy void above it.

The float replaces the harvested DEVMO donut of `level-sensing.md`. A
neodymium ring (Br ~1.3 T) throws ~4x the field of that ferrite donut, so
the reeds trip with the magnet held off the wall — but neodymium is dense,
and PETG sinks in syrup, so the buoyancy void is sized in `main()` to lift
the magnet's mass with reserve. See `magnet-float.md`."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_step
from docgen import substitute_md


# Donor magnet: AplysiaTech N52 sintered-NdFeB ring (Amazon B0GD15CWCL,
# 1" OD x 1/2" ID x 1/8"), axially magnetized through the thickness.
magnet_outer_diameter = 25.4
magnet_inner_diameter = 12.7
magnet_thickness = 3.18
magnet_density = 7.5e-3  # g/mm^3, sintered NdFeB

# Float-guide rod: matches reservoir.py ROD_DIAMETER (Tandefio B0CY4DWJFQ,
# 1/8" 316 SS). The bore is the rod plus a free-slide clearance — the float
# must travel ~170 mm of level change without binding on the rod.
rod_diameter = 3.175
rod_slip_clearance = 0.6
bore_diameter = rod_diameter + rod_slip_clearance

# Shell. Side and floor carry the watertight wall; the roof is the bridged
# ceiling printed over the buoyancy void after the magnet is dropped in, so
# it gets an extra layer or two and ironing (see magnet-float.md).
side_wall = 2.0
floor_thickness = 2.0
roof_thickness = 2.5
bore_wall = 1.6

# The ring is located radially by its OD against the pocket side; its ID
# runs loose around the central bore tube.
magnet_pocket_clearance = 0.3

bore_radius = bore_diameter / 2
cavity_inner_radius = bore_radius + bore_wall
cavity_outer_radius = magnet_outer_diameter / 2 + magnet_pocket_clearance
float_outer_radius = cavity_outer_radius + side_wall
float_outer_diameter = 2 * float_outer_radius

# Buoyancy inputs. syrup_density is the low-end design estimate for the
# Pepsi-made sucralose 1:20 concentrate (no sugar, so near water); designing
# at the low end leaves reserve if it runs denser. reserve_buoyancy is the
# displaced-weight margin over assembled weight.
syrup_density = 1.10e-3  # g/mm^3
petg_density = 1.27e-3   # g/mm^3
reserve_buoyancy = 1.15

magnet_mass = (
    magnet_density
    * math.pi
    / 4
    * (magnet_outer_diameter**2 - magnet_inner_diameter**2)
    * magnet_thickness
)

# Solve the cavity height that meets reserve_buoyancy. Displacement is the
# outer envelope minus the through-bore; assembled weight is the PETG shell
# (envelope minus cavity minus bore) plus the magnet. Both are affine in the
# cavity height, so the reserve condition resolves to one division.
_displacing_area = math.pi * (float_outer_radius**2 - bore_radius**2)
_cavity_area = math.pi * (cavity_outer_radius**2 - cavity_inner_radius**2)
_solid_end_caps = floor_thickness + roof_thickness
_denominator = syrup_density * _displacing_area - reserve_buoyancy * petg_density * (
    _displacing_area - _cavity_area
)
_numerator = (
    reserve_buoyancy * petg_density * _displacing_area * _solid_end_caps
    + reserve_buoyancy * magnet_mass
    - syrup_density * _displacing_area * _solid_end_caps
)
cavity_height = _numerator / _denominator

void_height = cavity_height - magnet_thickness
float_height = _solid_end_caps + cavity_height

# The pause plane: print floor + the magnet-deep pocket walls, stop here,
# drop the ring over the bore tube onto the floor, resume. Above it the
# walls continue to form the void, then the roof bridges the cavity closed.
magnet_insert_pause_z = floor_thickness + magnet_thickness

assert void_height > magnet_thickness, "buoyancy void collapsed — lighter magnet or denser syrup needed"


def build_magnet_float():
    body = cq.Workplane("XY").circle(float_outer_radius).extrude(float_height)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=floor_thickness)
        .circle(cavity_outer_radius)
        .circle(cavity_inner_radius)
        .extrude(cavity_height)
    )
    bore = cq.Workplane("XY").circle(bore_radius).extrude(float_height)
    return body.cut(cavity).cut(bore)


def _buoyancy_report():
    # _displacing_area already excludes the through-bore, so displacement is
    # that cross-section over the full height; the shell is what remains once
    # the cavity is carved from it.
    displacement = _displacing_area * float_height
    petg_volume = displacement - _cavity_area * cavity_height
    assembled_mass = petg_density * petg_volume + magnet_mass
    displaced_mass = syrup_density * displacement
    return {
        "float_od": float_outer_diameter,
        "float_height": float_height,
        "void_height": void_height,
        "pause_z": magnet_insert_pause_z,
        "magnet_mass": magnet_mass,
        "petg_mass": petg_density * petg_volume,
        "assembled_mass": assembled_mass,
        "displaced_mass": displaced_mass,
        "reserve": displaced_mass / assembled_mass,
    }


def main():
    here = Path(__file__).resolve().parent
    export_step(build_magnet_float(), str(here / "magnet-float.step"))
    print("-> magnet-float.step")

    r = _buoyancy_report()
    print(
        f"   OD {r['float_od']:.1f} x H {r['float_height']:.1f} mm | "
        f"pause Z {r['pause_z']:.2f} mm | "
        f"mass {r['assembled_mass']:.1f} g (magnet {r['magnet_mass']:.1f} g) | "
        f"displaces {r['displaced_mass']:.1f} g | reserve {r['reserve']:.2f}x"
    )

    variables = {
        "MAGNET_OD": f"{magnet_outer_diameter:.4g} mm",
        "MAGNET_ID": f"{magnet_inner_diameter:.4g} mm",
        "MAGNET_T": f"{magnet_thickness:.4g} mm",
        "MAGNET_MASS": f"{magnet_mass:.1f} g",
        "BORE_D": f"{bore_diameter:.4g} mm",
        "FLOAT_OD": f"{float_outer_diameter:.4g} mm",
        "FLOAT_H": f"{float_height:.4g} mm",
        "VOID_H": f"{void_height:.4g} mm",
        "PAUSE_Z": f"{magnet_insert_pause_z:.4g} mm",
        "SYRUP_RHO": f"{syrup_density * 1000:.2f} g/cm³",
        "RESERVE": f"{r['reserve']:.2f}×",
    }
    substitute_md(
        here / "magnet-float.md",
        variables=variables,
        expected_counts={
            "MAGNET_OD": 1,
            "MAGNET_ID": 1,
            "MAGNET_T": 1,
            "MAGNET_MASS": 2,
            "BORE_D": 1,
            "FLOAT_OD": 2,
            "FLOAT_H": 1,
            "VOID_H": 1,
            "PAUSE_Z": 1,
            "SYRUP_RHO": 1,
            "RESERVE": 1,
        },
    )
    print("-> magnet-float.md")


if __name__ == "__main__":
    main()
