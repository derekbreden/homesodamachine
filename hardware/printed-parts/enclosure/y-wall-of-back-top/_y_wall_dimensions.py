"""Doc-sync driver for hardware/printed-parts/enclosure/y-wall-of-back-top/README.md.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(_hw / "manifold-layout"))
sys.path.insert(0, str(_hw / "scripts"))

from docgen import substitute_md  # noqa: E402
from _material_base import stock_srgb  # noqa: E402

sys.path.insert(0, str(_hw / "printed-parts/enclosure/enclosure"))
from _enclosure_data import read as _read

_palette = _read("rear", black_srgb=stock_srgb("M_PETGF_BLACK"))


def __getattr__(name):
    if name == "M_PETGF_BLACK":
        from _material_base import M_PETGF_BLACK
        globals()[name] = M_PETGF_BLACK
        return M_PETGF_BLACK
    raise AttributeError(name)


def __dir__():
    return sorted(set(globals()) | {"M_PETGF_BLACK"})


# AC inlet recess: the bore the mating C13 cord housing enters, wall and inlet
# tunnel in one (`enclosure._c14_tunnel`), with the IEC 60320 C14 receptacle's
# flange seated at its floor and its shroud standing back up it. The depth range
# is how far the housing comes down that bore. Typed off the cordset, which this
# tree carries no body for — there is nothing to read it off.


def c14_rim_inset():
    """How far the inlet's rim face, on the pocket floor, sits inside the wall's outer plane: the
    bore the C13 nose crosses before it reaches the inlet."""
    import enclosure_assembly as _ea
    return _read('rim-inset', rear_plane_y=_ea._enc.rear_plane_y,
                 wall=_ea._enc.wall, seat_y=_ea.c14_seat_y())


# The wall's identification colours, by the fluid each names — the one
# statement of what a colour MEANS on this machine.
#
# Blue is spent: `bom.md` §3 buys the carbonated-water umbilical riser in BLUE
# LLDPE and §8 buys the union that receives it wearing a blue accent ring, so
# blue names carbonated water and nothing else on this wall. That leaves the
# customer's teed-in tap-water station as the WHITE-marked one and the CO2
# inlet as the RED one, which is the scheme §"Umbilical port — tube
# identification" states and the quick start names its ports by.
#
# The iso line-art that paints these rings onto the wall
# (`../drawings/line-art/_appliance_model.py`) reads them from here, and the
# quick start (`/hardware/quickstart/`) reads the same four into its generated
# stylesheet from this file — so the face a customer looks at and the sheet in
# their hand cannot disagree about which colour is which line.
# FOUR TUBE COLOURS AND FOUR CHIP COLOURS, and they are the same four: a chip
# is the colour of the tube that goes into it. Black is not the absence of a
# marking on this wall — it is the FLAVOUR colour, the stock `_routing.SPOOLS`
# cuts both flavour lines off, and both flavour ports wear it. What black does
# not do is tell A from B: a customer pushes black into either one and the
# manifold sorts them.
port_colors = {name: tuple(_palette['port_colors'][name]) for name in _palette['port_order']}

# THE SPOOL EACH CHIP AND ITS TUBE COLLAR ARE CUT OFF, and it is not the tube's own colour.
# `port_colors` is the IDENTIFICATION scheme — neoFlo LLDPE, what the customer's tube is — and a
# chip printed to match one is Polymaker Fiberon PET-GF15, a different product that happens to
# answer to the same name. White, blue and red are the median of the wound filament in
# Polymaker's product photographs (FL02003, FL02006, FL02007). Black uses the shared
# PET-GF stock appearance. `ledger/purchases.md` §13 buys all four.
chip_filaments = {name: (_palette['chip_filaments'][name][0],
                         tuple(_palette['chip_filaments'][name][1]))
                  for name in _palette['filament_order']}
chip_word_colors = {name: tuple(_palette['chip_word_colors'][name])
                    for name in _palette['filament_order']}

def chip_color(fluid):
    """The colour one chip actually comes out — the filament it prints in, not the
    identification colour it stands for.

    `port_colors` is the SCHEME: what blue means on this wall, and the neoFlo
    LLDPE the customer's tube is cut off. A chip printed to match one is Fiberon
    PET-GF15, a different product answering to the same name.
    `enclosure_assembly.build_bulkhead_rings` and the tube collars draw the chip
    from here and the drawings paint the scheme from `port_colors`."""
    return chip_filaments[fluid][1]


def word_color(fluid):
    """The colour a chip's WORD is lettered in — the one of the black and white spools that reads
    against the filament that chip actually prints in. `bulkhead_ring` cuts the recess and this is
    what fills it and stands out of it."""
    return chip_word_colors[fluid]


def port_color_hex(fluid):
    """One identification colour as `#rrggbb`, for an SVG presentation
    attribute."""
    return _palette['hex'][fluid]


def port_color_svg(fluid):
    """One identification colour in the `rgb(r, g, b)` spelling the iso
    renderer writes into a marking's `fill` — which is the string a consumer
    of that SVG finds the marking by."""
    return _palette['svg'][fluid]


def carb_union_end(panel_x):
    """Which end of the umbilical row the blue-ringed carbonated-water union
    stands at — READ off the `enclosure_assembly.PANEL_X` mapping `main` hands in, so the user
    rule ("blue tube into the blue-ringed bulkhead, at
    this end") cannot outlive the row it describes. +X is east."""
    return _read('carb-union-end', panel_x=panel_x)


def dropped_union_end(panel_on_gate_lane, panel_x):
    """Which end of the umbilical row stands off the row's own storey — READ off
    `enclosure_assembly.PANEL_ON_GATE_LANE` mapping `main` hands in against `PANEL_X`, so the user rule ("the
    ones lower down are at this end") cannot outlive the arrangement it
    describes. +X is east."""
    return _read('dropped-union-end', lanes=list(panel_on_gate_lane), panel_x=panel_x)


def panel_hole_diameters(ports):
    """The two bores this wall carries: `(bulkhead, co2)`.

    Taken from the functions that STRIKE them, not from a second copy of their
    arithmetic. `enclosure_assembly.y_wall_ports` and `enclosure_assembly.co2_wall_port` are the
    calls `enclosure_assembly.pack` fills `back_ports` with, and `enclosure._port_cuts` bores
    that list — so these are the holes that get cut, and a change to HOW either is
    struck (a chamfer allowance, a different slip for gas than for water) arrives here
    instead of leaving the README quoting the old rule.

    Both strike against a placed fitting, so both wanted the pack. `_facts` carries what
    those two calls returned when the machine was last stood, so the reading is the same
    reading and no build is taken for it. `main` imports that doc-only reading and hands the
    ports in; drivers importing this module for the AC recess or colours load neither the facts
    nor the assembled machine.

    All four PP1208E bulkheads on this wall — 1 water inlet + 3 umbilical-port unions —
    use the largest union opening for the quarter-inch figure; metric flavor openings are listed separately.
    """
    return tuple(_read('panel-hole-diameters', ports=ports))


def main():
    import above_core
    rows = above_core.specification()['rear_wall']['grid']['rows_z_mm']
    substitute_md(_here / 'README.md', variables=_read('grid-variables', rows=rows))
    print("-> README.md")


if __name__ == "__main__":
    main()
