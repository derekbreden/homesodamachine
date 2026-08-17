"""Doc-sync driver for hardware/printed-parts/enclosure/back-panel/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(_hw / "manifold-layout"))
sys.path.insert(0, str(_hw / "scripts"))

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
# FOUR TUBE COLOURS AND FOUR CHIP COLOURS, and they are the same four: a chip
# is the colour of the tube that goes into it. Black is not the absence of a
# marking on this wall — it is the FLAVOUR colour, the stock `_routing.SPOOLS`
# cuts both flavour lines off, and both flavour ports wear it. What black does
# not do is tell A from B: a customer pushes black into either one and the
# manifold sorts them.
port_colors = {
    "carb": (31, 111, 235),     # carbonated water — the umbilical riser
    "water": (255, 255, 255),   # tap water — the customer's teed-in supply
    "co2": (214, 58, 58),       # CO2 — the customer's regulator tether
    "flavor": (38, 38, 41),     # flavour — both nozzle feeds, one colour
}


# THE SPOOL EACH CHIP IS CUT OFF, and it is not the tube's own colour. `port_colors` is the
# IDENTIFICATION scheme — neoFlo LLDPE, what the customer's tube is — and a chip printed to match
# one is Bambu PETG Basic, a different product that happens to answer to the same name. These are
# the filaments themselves, sampled off the store's own product photograph (`ledger/purchases.md`
# buys White 30106, Navy Blue 30604 and Red 30201; black is the enclosure's own 30105 stock).
chip_filaments = {
    "water": ("PETG Basic White 30106", (255, 255, 255)),
    "carb": ("PETG Basic Navy Blue 30604", (45, 113, 211)),
    "co2": ("PETG Basic Red 30201", (227, 52, 49)),
    "flavor": ("PETG Basic Black 30105", (38, 38, 41)),
}
# Which of black and white a chip's word letters in, one entry per `chip_filaments` spool.
chip_word_colors = {
    "water": (0, 0, 0),
    "carb": (255, 255, 255),
    "co2": (255, 255, 255),
    "flavor": (255, 255, 255),
}


def chip_color(fluid):
    """The colour one chip actually comes out — the filament it prints in, not the
    identification colour it stands for.

    `port_colors` is the SCHEME: what blue means on this wall, and the neoFlo
    LLDPE the customer's tube is cut off. A chip printed to match one is Bambu
    PETG Basic, a different product answering to the same name, and the two are
    a few points apart. `enclosure_assembly.build_port_rings` draws the chip
    from here and the drawings paint the scheme from `port_colors`."""
    return chip_filaments[fluid][1]


def word_color(fluid):
    """The colour a chip's WORD is lettered in — the one of black and white that reads against the
    filament that chip actually prints in. `port_ring` cuts the recess and this is what fills it."""
    return chip_word_colors[fluid]


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
    stands at — READ off `enclosure_assembly.PANEL_X`, the pitch the three unions are
    placed on, so the user rule ("blue tube into the blue-ringed bulkhead, at
    this end") cannot outlive the row it describes. +X is east."""
    import enclosure_assembly as _ea
    x = _ea.PANEL_X["bulkhead-carb"]
    return "east" if x == max(_ea.PANEL_X.values()) else "west"


def dropped_union_end():
    """Which end of the umbilical row stands off the row's own storey — READ off
    `enclosure_assembly.PANEL_ON_GATE_LANE` against `PANEL_X`, so the user rule ("the
    ones lower down are at this end") cannot outlive the arrangement it
    describes. +X is east."""
    import enclosure_assembly as _ea
    lo = [_ea.PANEL_X[n] for n in _ea.PANEL_ON_GATE_LANE]
    return "east" if min(lo) > min(_ea.PANEL_X.values()) else "west"


def panel_hole_diameters():
    """The two bores this panel carries: `(bulkhead, co2)`.

    Taken from the functions that STRIKE them, not from a second copy of their
    arithmetic. `enclosure_assembly.back_wall_ports` and `enclosure_assembly.co2_wall_port` are the
    calls `enclosure_assembly.pack` fills `back_ports` with, and `enclosure._port_cuts` bores
    that list — so these are the holes that get cut, and a change to HOW either is
    struck (a chamfer allowance, a different slip for gas than for water) arrives here
    instead of leaving the README quoting the old rule.

    Both strike against a placed fitting, so both wanted the pack. `_facts` carries what
    those two calls returned when the machine was last stood, so the reading is the same
    reading and no build is taken for it — which is why this stays a function and why
    `_facts` is imported inside it: the drivers that import this module for the AC recess
    or the port colours load nothing to get them.

    All four PP1208E bulkheads on this panel — 1 water inlet + 3 umbilical-port unions —
    share one hole, which is the figure the README quotes.
    """
    import _facts
    ports = _facts.read().wall_ports
    diameters = {round(p[3], 6) for p in ports["union"]}
    if len(diameters) != 1:
        raise ValueError(
            f"the four panel unions are bored at {sorted(diameters)}. The README gives them "
            f"one hole, so either they go back on one diameter or it reads them out apiece.")
    return ports["union"][0][3], ports["co2"][3]


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
        "FLAVOR_COLOR": port_color_hex("flavor"),
        "CARB_END": carb_union_end(),
        "FLAVOR_B_END": dropped_union_end(),
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
