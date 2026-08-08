"""Doc-sync driver for hardware/assembly/cards/ — every figure the cards state
that the machine owns.

    tools/cad-venv/bin/python hardware/assembly/cards/_cards_sync.py
    tools/cad-venv/bin/python hardware/assembly/cards/_cards_sync.py --check

The default rewrites each card's `data-gen` markers from the built appliance.
`--check` writes nothing and exits 2 on the first disagreement — that is the mode
`_build.py` runs, so a stale deck cannot be printed. Underscore-prefixed: the
dev-server watcher never runs it.

Marker syntax and the checks this driver's registry buys are `_cardgen.py`.

ADDING A CARD
-------------

One subsystem is one function taking the built `Machine` and returning
`(facts, cards)`; `SUBSYSTEMS` is the list of them. To put a figure on a card:

1. Derive it in that subsystem's function. READ IT OFF THE MACHINE, never off
   another document — the machine is what gets built. Prefer a structural
   reading to a coordinate: "the east end of the row" survives the row moving,
   "z 342.4" does not, and the row moved twice this month.
2. Assert the structure the sentence around it depends on, the way
   `_bom_sync.py` asserts `not ml.JOINS`. A card that says "nothing is cut in
   the front wall" is only true while `pack.front_ports` is empty, so the
   assertion is what puts the sentence back when it stops being true — the value
   alone cannot, because there is no number in it to drift.
3. Wrap the value on the card: `<span class="dim" data-gen="NAME">value</span>`,
   or `data-gen` straight on a `<td class="v">`. Text only, no child tags.
4. Add the name to that card's set in `cards`, and name this driver in the
   card's `.src` footer.

A card that states nothing the machine owns — a hand technique, a torque by
feel — needs no entry and is left alone. It is a card's numbers that go stale,
not its craft.
"""

import os
import sys
from collections import namedtuple
from pathlib import Path

# The gate renders no CAD and supersedes no build: it reads one assembly and
# rewrites text. Same opt-out `_build.py` takes.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

CARDS_DIR = Path(__file__).resolve().parent
_hw = next(p for p in CARDS_DIR.parents if p.name == "hardware")
for _p in ("manifold-layout", "printed-parts/cadlib", "printed-parts/cold-core",
           "printed-parts/enclosure/back-panel", "cut-parts/compressor-shroud",
           "reference/jg-bulkhead-union", "reference/iec-c14-inlet"):
    sys.path.insert(0, str(_hw / _p.replace("/", os.sep)))

sys.path.insert(0, str(CARDS_DIR))
from _cardgen import sync  # noqa: E402
from _cards_ip import internal_plumbing  # noqa: E402  — IP + WR + FU
from _cards_cc import cold_core, refrigerant_loop  # noqa: E402

Machine = namedtuple("Machine", "a pack box")

# ── entities ───────────────────────────────────────────────────────────────
# A value is written into the card's source, so it is spelled the way the card
# spells it — `×` as an entity, like every other × on the page.
X = "&#215;"        # ×
DIA = "&#8960;"     # ⌀
NDASH = "&ndash;"   # –
PRIME = "&Prime;"   # ″


def _machine() -> Machine:
    """The appliance, built once. Every fact below is read off this."""
    import front_half as _fh  # noqa: E402  — expensive; imported inside the build
    return Machine(*_fh.machine())


# ═══ EN — Enclosure mechanical ═════════════════════════════════════════════

def enclosure(m: Machine):
    """`enclosure-mechanical.md`'s eight steps: the box, its walls' stations, and
    what stands inside it."""
    import enclosure as _enc
    import front_half as _fh
    import _scorecard as _card
    import iec_c14_inlet as _c14
    import jg_bulkhead_union as _jg
    from _back_panel_dimensions import (ac_inlet_recess_depth_max,
                                        ac_inlet_recess_depth_min)
    from _cold_core_interface import (cap_conduits, front_port_order,
                                      outer_shell_x_length, outer_shell_y_length)
    from _compressor_shroud_dimensions import (panel_hole_label,
                                               terminal_block_clearance_mm,
                                               wall_thickness_in)

    box, pack = m.box, m.pack
    pieces = sorted(_enc.build_pieces(box)[0])

    # ── what the cards' sentences stand on ────────────────────────────────
    # EN-01 and EN-02 both say the box is four pieces and no panel. A fifth
    # printed piece — a front or back panel coming back — has no number in it to
    # drift, so this is the only thing that can put those sentences back.
    assert pieces == ["back-bottom", "back-top", "front-bottom", "front-top"], (
        f"the box prints as {pieces} and EN-01/EN-02 stage four pieces and no separate "
        f"panel — restate them, or the deck ships a card for a part that is not made")
    # EN-02: "nothing at all is cut in the front wall", which is why CO2 comes in
    # at the back. EN-04: the condenser's air still has no route through a side
    # face (enclosure-mechanical.md Open items 2) — the card says so, and stops
    # saying so the moment a grille is cut.
    assert not pack.front_ports and not box.front_ports, (
        f"{len(box.front_ports)} station(s) are cut in the front wall — EN-02 says nothing "
        f"is, and EN-02's whole CO2 paragraph is about that")
    # EN-06: "every one of those bosses is on `enclosure-back-top`", which is what
    # makes the power column bench work on that piece rather than work inside a
    # standing box. A boss forward of the Y seam or below the back Z seam is in a
    # different piece and the step is a different step.
    stray = [b for b in box.east_bosses if b[0] < box.y_joint or b[1] < box.splits[1]]
    assert not stray, (
        f"{len(stray)} +X wall boss(es) fall outside `enclosure-back-top` ({stray}) — EN-06 "
        f"offers the whole power column up to that one piece on the bench")
    # EN-05: the core is reached through its lid, and what is left on the face it
    # mates against the stratum is the two reed cables.
    assert front_port_order == ("reed-cable-a", "reed-cable-b"), (
        f"the core's front face carries {front_port_order} — EN-05 says two reed cables "
        f"and the copper/PRV slot, and that face is mated shut against the stratum")

    ox0, ox1, oy0, oy1, oz0, oz1 = box.outer
    nut_d, _ = _jg.panel_footprint()
    c14_w, _ = _c14.panel_footprint()
    # A hand has to get a socket onto each nut with its neighbours already made
    # up; this is the clear wall that leaves, priced the way
    # `_enclosure_mechanical_sync._port_chain` prices it.
    chain_3 = 3 * nut_d + 2 * 7.0

    # The umbilical row, read as an arrangement rather than as three stations: a
    # single pitch, and which END of the row the blue ring is on. Both survive the
    # row moving, which it does.
    xs = sorted(_fh.PANEL_X.values())
    pitches = {round(b - a, 6) for a, b in zip(xs, xs[1:])}
    assert len(pitches) == 1, (
        f"the umbilical row stands on {sorted(pitches)} and EN-02 quotes one pitch")
    carb_end = "east" if _fh.PANEL_X["bulkhead-carb"] == xs[-1] else "west"

    # EN-07 pins each Z seam at both ends of each ±X wall so it cannot hinge open
    # at the end it was not pinned at. That is the shape of the sentence, so the
    # count is read off the stations rather than typed beside it.
    z_stations = _enc._z_stations(box.inner, box.y_joint)
    assert len({s[4] for s in z_stations}) == 2, (
        "the Z seams no longer pin per Y column and EN-07 closes them one column at a time")

    # The hopper opening's own rectangle against the seam it may cross.
    hx0, hx1, hy0, hy1 = _enc._hopper_hole(box.inner, box.outer, box.y_joint, box.funnel)
    hopper_pieces = ("both top pieces" if hy1 > box.y_joint
                     else "`enclosure-front-top`")
    assert abs((hx0 + hx1) / 2.0 - (ox0 + ox1) / 2.0) < 1e-6, (
        "the hopper opening is off centre across the box and EN-09 sends the bench "
        "straight down it — say where it is instead")

    # The widest body ON THE FLOOR is what the ±X walls stand their boss chains
    # off, so this pair is why the box is the width it is.
    def _span(*names):
        boxes = [_fh.box(pack.placed[n][0]) for n in names]
        return max(b.xmax for b in boxes) - min(b.xmin for b in boxes)

    facts = {
        # The box.
        "BOX_SIZE": f"{ox1 - ox0:.0f} {X} {oy1 - oy0:.0f} {X} {oz1 - oz0:.0f} mm",
        "BOX_PIECES": f"{len(pieces)}",
        "WALL_T": f"{_enc.wall:.4g} mm",
        "Y_SEAM": f"{box.y_joint:.4g}",
        "Z_SEAM_FRONT": f"{box.splits[0]:.4g}",
        "Z_SEAM_BACK": f"{box.splits[1]:.4g}",
        "SEAM_SCREWS_Z": f"{sum(1 for s in z_stations if s[4] == 'front')}",
        "STRATUM_X": f"{_span('compressor-shroud', 'condenser+fan'):.0f} mm",
        "CORE_X": f"{_span('foam-assembly'):.0f} mm",
        "SIDE_BAND": f"{_enc.side_rib_inset:.4g} mm",
        # Inserts set while the box is still open bench (EN-01). The +X wall's
        # count is one fact under one name: EN-01 presses those inserts, EN-06
        # drives their screws and ES-01/ES-03 send the bench to them, and four
        # cards stating one wall's boss chain cannot be allowed to disagree.
        "WALL_BOSSES": f"{len(box.east_bosses)}",
        "C14_BOSSES": f"{len(box.c14)}",
        # The rear wall (EN-02). Arrangement, not stations.
        "BACK_BODIES": f"{len(box.back_ports)}",
        "UMBILICAL_PITCH": f"{next(iter(pitches)):.4g} mm",
        "CARB_END": carb_end,
        "PORT_HOLE_D": f"{DIA}18",
        "CO2_HOLE_D": f"{DIA}15.42",
        "PORT_NUT_D": f"{nut_d:.4g} mm",
        "PORT_CHAIN_3": f"{chain_3:.4g} mm",
        "C14_FLANGE_W": f"{c14_w:.4g} mm",
        "AC_RECESS": f"{ac_inlet_recess_depth_min:.4g}{NDASH}"
                     f"{ac_inlet_recess_depth_max:.4g} mm",
        # The refrigeration stratum (EN-03, EN-04).
        "PANEL_HOLE": f"{panel_hole_label[:-1]}{PRIME}",
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:.4g} mm",
        "SHROUD_WALL_IN": f"{wall_thickness_in:.4g}{PRIME}",
        "SIDE_OPENINGS": f"{len(box.east_ports)}",
        # The cold core (EN-05).
        "CORE_FOOTPRINT": f"{outer_shell_x_length:.4g} {X} {outer_shell_y_length:.4g} mm",
        "CAP_CONDUITS": f"{len(cap_conduits)}",
        "CORE_FRONT_PORTS": f"{len(front_port_order)}",
        # The hopper (EN-09).
        "HOPPER_PIECES": hopper_pieces,
        # What the closed chassis reads as (EN-07).
        "BODY_COUNT": f"{len(_card.mounts())}",
    }

    cards = {
        "en-01-stage-the-four-pieces": {
            "BOX_SIZE", "BOX_PIECES", "WALL_T", "Y_SEAM", "Z_SEAM_FRONT", "Z_SEAM_BACK",
            "WALL_BOSSES", "C14_BOSSES"},
        "en-02-rear-wall-bodies": {
            "BACK_BODIES", "UMBILICAL_PITCH", "CARB_END", "PORT_HOLE_D", "CO2_HOLE_D",
            "PORT_NUT_D", "PORT_CHAIN_3", "C14_FLANGE_W", "AC_RECESS"},
        "en-03-compressor-shroud": {
            "PANEL_HOLE", "TB_CLEARANCE", "SHROUD_WALL_IN"},
        "en-04-stand-the-stratum": {
            "STRATUM_X", "CORE_X", "SIDE_BAND", "SIDE_OPENINGS"},
        "en-05-seat-cold-core": {
            "CORE_FOOTPRINT", "CAP_CONDUITS", "CORE_FRONT_PORTS"},
        "en-07-close-the-box": {
            "BOX_PIECES", "Y_SEAM", "Z_SEAM_FRONT", "Z_SEAM_BACK", "SEAM_SCREWS_Z",
            "BODY_COUNT"},
        "en-09-display-and-hopper": {"HOPPER_PIECES"},
    }
    return facts, cards


# ═══ ES — Electronics shelf ════════════════════════════════════════════════

def electronics_shelf(m: Machine):
    """`electronics-shelf.md`: the five bodies of the power column, and the +X wall
    bosses each one's own hole pattern stands there."""
    import ac_hub as _hub
    import ground_ring_stack as _gnd
    import meanwell_irm90 as _psu
    import pcba_tray as _pcba
    import teyleten_relay as _relay

    # One boss per hole in each body's own pattern, carried through that body's own
    # placement (`front_half.wall_mounts`). Counting the patterns here and the wall
    # there is the check: if they disagree, a body is mounted by something other
    # than its own holes and ES-01's table is describing a different machine.
    column = {"PSU_BOSSES": len(_psu.holes),
              "PCBA_BOSSES": len(_pcba.board.holes),
              "RELAY1_BOSSES": len(_relay.holes),
              "AC_HUB_BOSSES": len(_hub.holes),
              "GND_BOSSES": len(_gnd.holes)}
    assert sum(column.values()) == len(m.box.east_bosses), (
        f"the five bodies' own patterns hold {sum(column.values())} holes and the +X wall "
        f"stands {len(m.box.east_bosses)} bosses — ES-01's table is the wall's census, so "
        f"one of them has gained a station the other has not")

    # The screw schedule falls out of the same patterns: one M3 in through each
    # body from the room. The ground stack's is the long one — it comes down
    # through a fan of ring terminals before it reaches its insert.
    long_screws = len(_gnd.holes)
    facts = {
        "SHELF_SCREWS_M3X8": f"{len(m.box.east_bosses) - long_screws}",
        "SHELF_SCREWS_M3X10": f"{long_screws}",
        # No insert is pressed on this bench — every one is already in a wall
        # boss. Nought is a figure a card states, so it is a figure the gate
        # holds: if the shelf ever grows a printed part with an insert of its
        # own, this stops being nought and ES-01's second step is wrong.
        "SHELF_INSERTS_HERE": "0",
        **{k: str(v) for k, v in column.items()},
    }
    # EN-06 is an enclosure card and its figures are the shelf's — it drives the
    # screws this bench stages for. A card is registered by whichever subsystem
    # derives what it says, and `collect` merges one namespace across the deck.
    column_names = {"WALL_BOSSES", *column}
    cards = {
        "es-01-prepare-the-shelf": {
            *column_names, "SHELF_SCREWS_M3X8", "SHELF_SCREWS_M3X10",
            "SHELF_INSERTS_HERE"},
        "es-03-stage-psu-relays-pcba": {
            "WALL_BOSSES", "PCBA_BOSSES", "SHELF_INSERTS_HERE"},
        "en-06-power-column": {
            *column_names, "SHELF_SCREWS_M3X8", "SHELF_SCREWS_M3X10"},
    }
    return facts, cards


# One function per subsystem, in deck order. `_build.py` runs all of them.
SUBSYSTEMS = (enclosure, electronics_shelf, cold_core, refrigerant_loop, internal_plumbing)


def collect(machine: Machine = None):
    """Every subsystem's facts and registry, merged.

    A name derived twice must be derived to the same value: one namespace across
    the deck is what stops an EN card and an ES card stating the same wall's boss
    count and disagreeing. This is `docgen.lint`'s cross-file check, held inside
    the one driver that owns every card."""
    machine = _machine() if machine is None else machine
    facts, cards = {}, {}
    for subsystem in SUBSYSTEMS:
        got_facts, got_cards = subsystem(machine)
        for name, value in got_facts.items():
            if name in facts and facts[name] != value:
                raise ValueError(
                    f"{subsystem.__name__} derives {name} as {value!r} and another "
                    f"subsystem derives it as {facts[name]!r} — one name, one value")
            facts[name] = value
        for stem, names in got_cards.items():
            if stem in cards:
                raise ValueError(f"{stem} is registered by two subsystems")
            cards[stem] = names
    return facts, cards


def main(check: bool = False) -> int:
    facts, cards = collect()
    return sync(CARDS_DIR, facts, cards, check=check)


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv[1:]))
