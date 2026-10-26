"""Doc-sync driver for hardware/assembly/pressure-vessel.md.

Run: tools/cad-venv/bin/python hardware/assembly/_pressure_vessel_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)

sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")
                       / "cut-parts" / "carbonation" / "float-rod"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cold-core"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")
        / "cut-parts" / "carbonation" / "endcaps-circular"),
)

import math

from _cold_core_interface import (
    above_carbonator_elbows_height,
    below_carbonator_elbows_height,
    carbonator_height,
    carbonator_outer_radius,
)
from endcap_circular_dxf import disc_thickness, hole_diameter, register_depth, register_radius
import float_rod_dimensions as rod_spec
from docgen import substitute_md

MM_PER_IN = 25.4
PSI_PER_BAR = 14.5038
PSI_PER_ATM = 14.6959

# Nominal gas feed: the 0.3 MPa (3 bar) preset of the in-appliance PISCO RVFUP1/4-1/4-0.3
# secondary regulator (hardware/reference/compact-inline-candidates). Refill can compress
# the trapped headspace above it: the downstream
# check isolates the headspace from the regulator, so this is not a maximum vessel
# pressure. The procedure's nominal figures and the downstream bench documents read it.
secondary_regulator_bar = 3.0
secondary_regulator_pressure_psi = round(secondary_regulator_bar * PSI_PER_BAR, 1)

# Thin-wall hoop stress in the tube at that feed: the 5" OD over the tube's 0.065" wall.
tube_wall = 0.065 * MM_PER_IN     # mm — OnlineMetals #12498
hoop_stress_psi = secondary_regulator_pressure_psi * carbonator_outer_radius / tube_wall

# What the feed carbonates to at the carbonator-wall setpoint and the top of its band
# (acceptance-and-burn-in.md). A volume is the CO2, at 0 °C and 1 atm, that one volume of
# water holds. CO2 solubility is Weiss (1974) for fresh water, taken on the CO2 fugacity;
# N2, O2 and Ar are Weiss (1970) fresh-water Bunsen coefficients.
carbonation_basis_c = (2.0, 4.0)
# Tap water arrives saturated with air at about this temperature. Air leaves the sealed
# headspace only dissolved in the water dispensed, so it builds until the outgoing water
# carries what the incoming water brings.
tap_water_c = 15.0
_AIR = (  # mole fraction in dry air, then the Bunsen coefficient's three terms
    (0.78084, -59.6274, 85.7661, 24.3696),   # N2
    (0.20946, -58.3877, 85.8079, 23.8439),   # O2
    (0.00934, -55.6578, 82.0262, 22.5929),   # Ar
)


def _vapor_atm(t_c):
    return 0.61121 * math.exp((18.678 - t_c / 234.5) * (t_c / (257.14 + t_c))) / 101.325


def _bunsen(a1, a2, a3, t_c):
    t = t_c + 273.15
    return math.exp(a1 + a2 * (100 / t) + a3 * math.log(t / 100))


def headspace_air_atm(t_c):
    """The air partial pressure a sealed headspace over water at t_c settles at."""
    dry = 1.0 - _vapor_atm(tap_water_c)
    return sum(x * dry * _bunsen(a1, a2, a3, tap_water_c) / _bunsen(a1, a2, a3, t_c)
               for x, a1, a2, a3 in _AIR)


def carbonation_volumes(t_c, air):
    """Equilibrium volumes of CO2 at the nominal feed, over a pure-CO2 headspace or one
    carrying the settled air."""
    t = t_c + 273.15
    p_total = secondary_regulator_pressure_psi / PSI_PER_ATM + 1.0
    p_co2 = p_total - _vapor_atm(t_c) - (headspace_air_atm(t_c) if air else 0.0)
    k0 = math.exp(-58.0931 + 90.5069 * (100 / t) + 22.2940 * math.log(t / 100))  # mol/(kg·atm)
    b = -1636.75 + 12.0408 * t - 3.27957e-2 * t ** 2 + 3.16528e-5 * t ** 3     # cm³/mol
    fugacity = p_co2 * math.exp(b * p_total / (82.0578 * t))
    return k0 * fugacity * 22.26      # L of CO2 at 0 °C and 1 atm per kg of water

# The finished rod and its toleranced assembly interface are defined by the
# part source used by FR-CARB-01. Register depth is to the drill tip, not a
# flat-ended rod's seating plane.
carbonator_rod_len = rod_spec.finished_length * MM_PER_IN
carbonator_rod_tolerance = rod_spec.length_tolerance * MM_PER_IN


def main():
    # The two elbow envelopes are equal by design; ELBOW_ENV is a single
    # substitution. If they diverge, split into ABOVE / BELOW variables.
    assert above_carbonator_elbows_height == below_carbonator_elbows_height, (
        f"above ({above_carbonator_elbows_height}) != below ({below_carbonator_elbows_height}); "
        "split ELBOW_ENV into ABOVE / BELOW variables."
    )
    lo, hi = carbonation_basis_c

    variables = {
        # Tube cut length / carbonator-as-assembled height.
        "TANK_H": f"{carbonator_height:.4g} mm",
        # Vertical envelope for the 1/4" NPT 90° elbow stack above and
        # below the carbonator (foam-shell budget).
        "ELBOW_ENV": f"{above_carbonator_elbows_height:.4g} mm",
        "ROD_LEN": f"{rod_spec.finished_length:.3f} ±{rod_spec.length_tolerance:.3f} in ({carbonator_rod_len:.2f} ±{carbonator_rod_tolerance:.2f} mm)",
        "REGISTER_RADIUS_IN": f"{register_radius:.4f}",
        "REGISTER_RADIUS_MM": f"{register_radius * MM_PER_IN:.3f} mm",
        # Nominal gas-feed setpoint / design reference, not an upper pressure bound.
        "WORKING_PSI": f"{secondary_regulator_pressure_psi:.4g} PSI",
        "REG_FIXED": f"fixed {secondary_regulator_bar:g}-bar "
                     f"({secondary_regulator_pressure_psi:.4g} PSI)",
        "HOOP_PSI": f"{round(hoop_stress_psi, -1):,.0f} PSI",
        # The feed's equilibrium carbonation, over pure CO2 and over the settled air.
        "CARB_PURE": f"{carbonation_volumes(lo, False):.1f} volumes at {lo:g} °C and "
                     f"{carbonation_volumes(hi, False):.1f} at {hi:g} °C",
        "CARB_AIR": f"{carbonation_volumes(lo, True):.1f} volumes at {lo:g} °C and "
                    f"{carbonation_volumes(hi, True):.1f} at {hi:g} °C",
        "HEADSPACE_AIR": f"{headspace_air_atm(lo) * PSI_PER_ATM:.0f} PSI",
        # The endplate's laser-cut tap-drill opening; not the purchased elbow's flow bore.
        "PORT_BORE": f'⌀{hole_diameter * MM_PER_IN:.4g} mm ({hole_diameter:.3f}")',
    }

    substitute_md(
        _here / "pressure-vessel.md",
        variables=variables,
    )
    print("-> pressure-vessel.md")


if __name__ == "__main__":
    main()
