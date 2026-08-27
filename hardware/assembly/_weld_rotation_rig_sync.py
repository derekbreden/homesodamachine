"""Doc-sync driver for hardware/assembly/weld-rotation-rig.md.

The rig's whole specification is one circle: the corner the plate and the bore
leave when the plate seats to its recess. So every figure in that document —
the lap length, the table speed at each travel speed, the fillet each leaves,
the heat a lap costs — is derived here from the tube's bore and the plate's
seat, and from nothing typed twice.

`v = ωR` is the only conversion the rig performs, and R is the bore radius.

Run: tools/cad-venv/bin/python hardware/assembly/_weld_rotation_rig_sync.py
"""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_hw / "cut-parts" / "carbonation" / "endcaps-circular"))
sys.path.insert(0, str(_here))

from _pressure_vessel_sync import carbonator_rod_len, plate_recess  # noqa: E402
from docgen import substitute_md  # noqa: E402
from endcap_circular_dxf import disc_diameter, disc_thickness, tube_id  # noqa: E402

MM_PER_IN = 25.4

TUBE_OD_IN = 5.000
TUBE_LEN = 152.4          # mm — the cut length the vessel is built from
ROD_DIA = 0.125 * MM_PER_IN

# 316L. Density is the handbook value; specific heat is what turns a lap's
# energy into the bulk temperature rise the thin wall actually sees.
DENSITY = 7.98e-3         # g/mm³
SPECIFIC_HEAT = 0.50      # J/g·K

# The machine, at the recipe in pressure-vessel.md step 3.
LASER_W = 700.0
POWER_FRACTION = 0.60
WIRE_DIA = 0.030 * MM_PER_IN     # ER316L .030
WIRE_FEED = 12.0                 # mm/s — step 3's recipe

# The travel speeds the doc tabulates, and the one it is written around.
SPEEDS = [5, 6, 8, 10, 12, 15, 20]
V_NOM = 8.0

# The head's own axis. The beam bisects the corner at 45° from vertical, and the
# slide is built parallel to it so travel changes standoff and nothing else.
# The retract only has to leave; the clearance below is what it leaves by.
PLUNGE_ANGLE = 45.0       # ° from vertical
RETRACT = 30.0            # mm of slide travel at the exit
NOZZLE_STANDOFF = 10.0    # mm — nozzle tip above the plate face at weld height
OVERLAP_DEG = 20.0        # ° of lap past 360°

# A synchronous rotisserie motor is line-locked, so on 60 Hz it sits at the top
# of its plate rating — which is what the cheap proof would actually run at.
TYD_RPM = 2.4

bead_diameter = tube_id * MM_PER_IN
bead_radius = bead_diameter / 2
bead_circumference = math.pi * bead_diameter
wire_area = math.pi * WIRE_DIA ** 2 / 4


def rpm(v: float) -> float:
    """Table speed for a travel speed at the bead — v = ωR, R the bore radius."""
    return v * 60.0 / bead_circumference


def fillet_leg(v: float, feed: float = WIRE_FEED) -> float:
    """Leg of the triangular fillet a travel speed leaves at a given wire feed.

    Deposit per mm of travel is the wire's own section times how much wire
    arrives per mm; a triangle of that area has legs of √(2A). This is the
    number a hand cannot hold and a turned part hands you.
    """
    return math.sqrt(2 * (feed / v) * wire_area)


def _cylinder_mass(diameter: float, length: float) -> float:
    return math.pi * diameter ** 2 / 4 * length * DENSITY


def masses() -> tuple[float, float]:
    """Grams turned at step 3 (tube + one plate) and step 5 (tube + two + rod)."""
    tube_od = TUBE_OD_IN * MM_PER_IN
    tube = (math.pi / 4) * (tube_od ** 2 - bead_diameter ** 2) * TUBE_LEN * DENSITY
    plate = _cylinder_mass(disc_diameter * MM_PER_IN, disc_thickness * MM_PER_IN)
    rod = _cylinder_mass(ROD_DIA, carbonator_rod_len)
    return tube + plate, tube + 2 * plate + rod


def main():
    m_s3, m_s5 = masses()
    beam_w = LASER_W * POWER_FRACTION
    lap_energy = beam_w * (bead_circumference / V_NOM)

    retract_z = RETRACT * math.cos(math.radians(PLUNGE_ANGLE))
    deg_s = 360.0 * V_NOM / bead_circumference

    variables = {
        "RECESS": f"{plate_recess:.2f} mm",
        "PLUNGE_ANGLE": f"{PLUNGE_ANGLE:.0f}\u00b0",
        # A vertical slide under a leaning head moves the landing point radially
        # by tan(lean) per mm; a slide along the beam moves it not at all.
        "VERT_COUPLE": f"{math.tan(math.radians(PLUNGE_ANGLE)):.2f} mm",
        "RETRACT": f"{RETRACT:.0f} mm",
        "RETRACT_Z": f"{retract_z:.1f} mm",
        "NOZZLE_STANDOFF": f"{NOZZLE_STANDOFF:.0f} mm",
        "EXIT_CLEAR": f"{retract_z + NOZZLE_STANDOFF - plate_recess:.1f} mm",
        "ANGLE_1DEG": f"{NOZZLE_STANDOFF * math.tan(math.radians(1)):.2f} mm",
        "OVERLAP_DEG": f"{OVERLAP_DEG:.0f}\u00b0",
        "DEG_S": f"{deg_s:.1f}\u00b0/s",
        "OVERLAP_S": f"{OVERLAP_DEG / deg_s:.1f} s",
        "OVERLAP_MM": f"{bead_circumference * OVERLAP_DEG / 360:.1f} mm",
        "TRIP_1S": f"{deg_s:.1f}\u00b0",
        "TRIP_1S_MM": f"{bead_circumference * deg_s / 360:.1f} mm",
        "LAP_380": f"{bead_circumference * (360 + OVERLAP_DEG) / 360 / V_NOM:.1f} s",
        "BEAD_D": f"{bead_diameter:.2f} mm",
        "BEAD_C": f"{bead_circumference:.2f} mm",
        "MASS_S3": f"{m_s3 / 1000:.2f} kg",
        "MASS_S5": f"{m_s5 / 1000:.2f} kg",
        "V_NOM": f"{V_NOM:.0f} mm/s",
        "WIRE_NOM": f"{WIRE_FEED:.0f} mm/s",
        "WIRE_AREA": f"{wire_area:.3f} mm²",
        "RPM_NOM": f"{rpm(V_NOM):.3f} RPM",
        "RPM_WINDOW": f"{rpm(SPEEDS[0]):.2f} – {rpm(SPEEDS[-2]):.2f} RPM",
        "V_TYD": f"{TYD_RPM / 60 * bead_circumference:.1f} mm/s",
        "HEAT_MM": f"{beam_w / V_NOM:.1f} J/mm",
        "HEAT_LAP": f"{lap_energy / 1000:.1f} kJ",
        "HEAT_DT": f"{lap_energy / (m_s3 * SPECIFIC_HEAT):.0f} K",
    }
    for v in SPEEDS:
        variables[f"RPM_{v}"] = f"{rpm(v):.3f} RPM"
        variables[f"REV_{v}"] = f"{bead_circumference / v:.1f} s"
        variables[f"LEG_{v}"] = f"{fillet_leg(v):.2f} mm"

    substitute_md(_here / "weld-rotation-rig.md", variables)
    print(
        f"bead {bead_circumference:.2f} mm  "
        f"nominal {rpm(V_NOM):.3f} RPM / {bead_circumference / V_NOM:.1f} s  "
        f"leg {fillet_leg(V_NOM):.2f} mm  "
        f"mass {m_s3 / 1000:.2f}/{m_s5 / 1000:.2f} kg"
    )


if __name__ == "__main__":
    main()
