"""Doc-sync driver for hardware/printed-parts/enclosure/back-panel/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(_hw / "manifold-layout"))

from docgen import substitute_md  # noqa: E402


# AC inlet recess: an IEC 60320 C14 receptacle nests into the panel face,
# the mating C13 cord housing ending flush with the panel surface. The
# depth range lets the C13 housing nest without bottoming on the bezel.
# Typed, because the recess has no CAD — there is nothing yet to read it off.
ac_inlet_recess_depth_min = 3.0
ac_inlet_recess_depth_max = 5.0

# The rear face's identification colours, by the fluid each names — the one
# statement of what a colour MEANS on this machine.
#
# Blue is spent: `bom.md` §3 buys the carbonated-water umbilical riser in BLUE
# LLDPE and §8 buys the union that receives it wearing a blue accent ring, so
# blue names carbonated water and nothing else on this wall. That leaves the
# customer's teed-in tap-water station as the WHITE-marked one and the CO2
# inlet as the RED one, which is the scheme §"Umbilical port — tube
# identification" states and the quick-start sheet aims arrows by.
#
# Both the iso line-art that paints these rings onto the wall
# (`../drawings/line-art/_appliance_model.py`) and the quick-start sheet that
# points at them (`/hardware/quickstart/appliance_quickstart.py`) read them
# from here, so the face a customer looks at and the sheet in their hand
# cannot disagree about which colour is which line.
port_colors = {
    "carb": (31, 111, 235),     # carbonated water — the umbilical riser
    "water": (255, 255, 255),   # tap water — the customer's teed-in supply
    "co2": (214, 58, 58),       # CO2 — the customer's regulator tether
}


def port_color_hex(fluid):
    """One identification colour as `#rrggbb`, for an SVG presentation
    attribute."""
    return "#%02x%02x%02x" % port_colors[fluid]


def port_color_svg(fluid):
    """One identification colour in the `rgb(r, g, b)` spelling the iso
    renderer writes into a marking's `fill` — which is the string a consumer
    of that SVG finds the marking by."""
    return "rgb(%d, %d, %d)" % port_colors[fluid]


def carb_union_end():
    """Which end of the umbilical row the blue-ringed carbonated-water union
    stands at — READ off `front_half.PANEL_X`, the pitch the three unions are
    placed on, so the user rule ("blue tube into the blue-ringed bulkhead, at
    this end") cannot outlive the row it describes. +X is east."""
    import front_half as _fh
    x = _fh.PANEL_X["bulkhead-carb"]
    return "east" if x == max(_fh.PANEL_X.values()) else "west"


def panel_hole_diameters():
    """The two bores this panel carries: `(bulkhead, co2)`.

    Taken from the functions that STRIKE them, not from a second copy of their
    arithmetic. `front_half.back_wall_ports` and `front_half.co2_wall_port` are the
    calls `front_half.pack` fills `back_ports` with, and `enclosure._port_cuts` bores
    that list — so these are the holes that get cut, and a change to HOW either is
    struck (a chamfer allowance, a different slip for gas than for water) arrives here
    instead of leaving the README quoting the old rule.

    Both strike against a placed fitting, so both want the pack. That is why this is a
    function and not a module constant, and why `front_half` is imported inside it: the
    reading costs a build, and the drivers that import this module for the AC recess or
    the port colours must not pay for one — or for loading the layout to get them.

    All four PP1208E bulkheads on this panel — 1 water inlet + 3 umbilical-port unions —
    share one hole, which is the figure the README quotes.
    """
    import front_half as _fh
    a = _fh.build_pack()
    bores = _fh.back_wall_ports(a.bulkhead_carry, *a.panel_carries.values())
    diameters = {round(p[3], 6) for p in bores}
    if len(diameters) != 1:
        raise ValueError(
            f"the four panel unions are bored at {sorted(diameters)}. The README gives them "
            f"one hole, so either they go back on one diameter or it reads them out apiece.")
    return bores[0][3], _fh.co2_wall_port(a.co2_inlet_carry)[3]


def main():
    bulkhead_panel_hole_diameter, co2_panel_hole_diameter = panel_hole_diameters()
    variables = {
        "AC_RECESS_DEPTH": f"{ac_inlet_recess_depth_min:.4g}–{ac_inlet_recess_depth_max:.4g} mm",
        "PANEL_HOLE_D": f"{bulkhead_panel_hole_diameter:.1f} mm",
        "PANEL_HOLE_D_SHORT": f"{bulkhead_panel_hole_diameter:.4g}",
        "CO2_HOLE_D": f"{co2_panel_hole_diameter:.4g}",
        "CARB_COLOR": port_color_hex("carb"),
        "WATER_COLOR": port_color_hex("water"),
        "CO2_COLOR": port_color_hex("co2"),
        "CARB_END": carb_union_end(),
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "AC_RECESS_DEPTH": 2,
            "PANEL_HOLE_D": 2,
            "PANEL_HOLE_D_SHORT": 1,
            "CO2_HOLE_D": 1,
            "CARB_COLOR": 1,
            "WATER_COLOR": 1,
            "CO2_COLOR": 1,
            "CARB_END": 2,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
