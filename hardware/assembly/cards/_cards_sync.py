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
   `_bom_sync.py` asserts `not ml.JOINS`. A card that says "no connection is
   cut in the front wall" is only true while `pack.front_ports` is empty, so
   the assertion is what puts the sentence back when it stops being true — the
   value alone cannot, because there is no number in it to drift.
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
from collections import Counter, namedtuple
from pathlib import Path

# The gate renders no CAD and supersedes no build: it reads one assembly and
# rewrites text. Same opt-out `_build.py` takes.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

CARDS_DIR = Path(__file__).resolve().parent
_hw = next(p for p in CARDS_DIR.parents if p.name == "hardware")
for _p in ("manifold-layout", "printed-parts/cadlib", "printed-parts/cold-core",
           "printed-parts/enclosure/y-wall-of-back-top", "printed-parts/enclosure/enclosure",
           "printed-parts/enclosure/pump-tray", "reference/compressor",
           "reference/jg-bulkhead-union", "reference/iec-c14-inlet",
           "printed-parts/zone-c/funnel", "reference/worm-clamp",
           "reference/jg-pp0408w", "reference/funnel-drain-stub"):
    sys.path.insert(0, str(_hw / _p.replace("/", os.sep)))

sys.path.insert(0, str(CARDS_DIR))
from _cardgen import sync  # noqa: E402
from _cards_ip import internal_plumbing  # noqa: E402  — IP + WR + FU
from _cards_cc import cold_core, refrigerant_loop  # noqa: E402
from _cards_fs import bench  # noqa: E402  — PV + CA + FC + AB + FS + GT

Machine = namedtuple("Machine", "a pack box")

# ── entities ───────────────────────────────────────────────────────────────
# A value is written into the card's source, so it is spelled the way the card
# spells it — `×` as an entity, like every other × on the page.
X = "&#215;"        # ×
DIA = "&#8960;"     # ⌀
NDASH = "&ndash;"   # –


def _machine() -> Machine:
    """The appliance as the last build wrote it down. Every fact below is read off that one
    reading, and nothing here stands a machine to get it.

    `box` and `pack` are the same record: the Box carries every station the Pack put on a
    wall, which is all these cards read either of them for."""
    import _facts
    f = _facts.read()
    return Machine(f, f.box, f.box)


# ═══ 00 — The cover ════════════════════════════════════════════════════════

#: The page the deck opens on, which is not one of the operations it tables.
COVER = "00-cover"


def deck(_m: Machine):
    """The cover's contents table and its count of the whole: the deck's own shape.

    THE ONE CARD THAT STATES THE DECK RATHER THAN THE APPLIANCE. Every other figure
    here is read off the built machine because the machine is what gets built; these
    are read off the card files because the deck is what gets printed. `tools/` is a
    station deck with a build of its own one directory down, and the glob that counts
    these does not descend into it.

    The registry is that same census, so a deck a bench starts writing needs a row on
    the cover and nothing here: its code arrives as a name this card is registered for
    and does not carry, and the last card of a deck deleted takes the name off both
    sides at once.

    `CARDS_SA` LANDS TWICE, and both are the same claim about the same thing. The
    cover reads `102 cards · one per bench operation, N per finished unit`, and cards
    are what it counts across the whole sentence: the deck holds an operation card
    for each step of the bench and a unit card for each sub-assembly one finished
    machine carries, and the SA deck is the second kind. A count of the sub-assemblies
    themselves would be a smaller figure — the cold core and the cap lid each take two
    cards, one per state — so this is the deck's shape and not the machine's."""
    stems = sorted(p.stem for p in CARDS_DIR.glob("*.html") if p.stem != COVER)
    counts = Counter(stem.partition("-")[0] for stem in stems)

    # A CARD IS NAMED FOR ITS DECK AND ITS PLACE IN IT — `pv-03-rod-register` — so one
    # census answers the table's figure twice: how many cards a deck holds, and how far
    # it runs. A gap or a repeat parts the two readings, and a bench reading `PV 14` off
    # the table goes to the tray for a PV-14 that was never printed.
    for code, held in sorted(counts.items()):
        numbers = sorted(s.partition("-")[2].partition("-")[0] for s in stems
                         if s.partition("-")[0] == code)
        assert numbers == [f"{i:02d}" for i in range(1, held + 1)], (
            f"the {code.upper()} deck is numbered {numbers} — the cover tables one figure "
            f"for how many cards it holds and how far it runs; renumber it")

    facts = {
        # The deck's length, less the page that states it.
        "CARDS_TOTAL": f"{len(stems)}",
        # One per row of the table, in the code the row's chip carries. `CARDS_SA` lands
        # twice on the page — the row, and the footer's clause about the unit cards —
        # because they are one count, and a name is one value across the whole deck.
        **{f"CARDS_{code.upper()}": f"{held}" for code, held in counts.items()},
    }
    return facts, {COVER: set(facts)}


# ═══ EN — Enclosure mechanical ═════════════════════════════════════════════

def enclosure(m: Machine):
    """`enclosure-mechanical.md`'s eight steps: the box, its walls' stations, and
    what stands inside it."""
    import compressor as _comp
    import enclosure as _enc
    import enclosure_assembly as _ea
    import _scorecard as _card
    import iec_c14_inlet as _c14
    import jg_bulkhead_union as _jg
    from _y_wall_dimensions import (ac_inlet_recess_depth_max,
                                        ac_inlet_recess_depth_min)
    from _cold_core_interface import (cap_conduits,
                                      outer_shell_x_length, outer_shell_y_length)

    box, pack = m.box, m.pack
    pieces = sorted(m.a.pieces)

    # ── what the cards' sentences stand on ────────────────────────────────
    # EN-01 stages four quadrants, the pump cartridge that rides out of their bay, the cap
    # screwed under it and the ceiling panel; EN-07 cross-pins the quadrants alone and
    # brings back-top down with its ceiling already in. THE FOUR ARE HELD FOUR
    # DIFFERENT WAYS — a quadrant is cross-pinned, the pump cartridge slides and is pinned by
    # nothing, the cap is screwed to the pump cartridge on the bench, the ceiling panel rides
    # a dado down each of back-top's flanks and is blocked by two transverse keepers — so a piece
    # added or renamed has no number in these sentences to drift, and this is the only
    # thing that can put them back.
    assert pieces == ["back-bottom", "back-top", "ceiling-panel", "front-bottom",
                      "front-top", "pump-cap", "pump-cartridge"], (
        f"the box prints as {pieces} and EN-01 stages four quadrants, one pump cartridge, its "
        f"cap and the ceiling panel, EN-07 cross-pins the quadrants alone — restate them, "
        f"or the deck ships a card for a part that is not made")
    # The panel is a piece of the box and not a quadrant: it is neither cross-pinned nor
    # a wall, so EN-07's cross-pin count must not take it.
    quadrants = [p for p in pieces
                 if not p.startswith("pump-") and p != "ceiling-panel"]
    # EN-01 tables ONE Z seam for both columns and EN-07 draws it as one level line
    # round the box, the four pieces meeting at a four-way corner on each side wall.
    # Two planes again and both cards are drawing a box that is not this one.
    assert abs(box.splits[0] - box.splits[1]) < 1e-9, (
        f"the Z seams stand at {box.splits} — EN-01 tables one seam for both columns "
        f"and EN-07 draws them on one rule; say what they are instead")
    # EN-02: "no connection is cut in the front wall" — the pump bay is the one
    # opening cut there and the pump cartridge's face closes it — which is why CO2 comes
    # in at the back. EN-04: the condenser's air still has no route through a side
    # face (enclosure-mechanical.md Open items 2) — the card says so, and stops
    # saying so the moment a grille is cut.
    assert not pack.front_ports, (
        f"{len(pack.front_ports)} station(s) are cut in the front wall — EN-02 says no "
        f"connection is, and EN-02's whole CO2 paragraph is about that. The pump cartridge is "
        f"a piece of that wall, not a station in it")
    # EN-06: "every one of those bosses is on `enclosure-back-top`", which is what
    # makes the power column bench work on that piece rather than work inside a
    # standing box. A boss forward of the Y seam or below the back Z seam is in a
    # different piece and the step is a different step.
    stray = [b for b in box.east_bosses if b[0] < box.y_joint or b[1] < box.splits[1]]
    assert not stray, (
        f"{len(stray)} +X wall boss(es) fall outside `enclosure-back-top` ({stray}) — EN-06 "
        f"offers the whole power column up to that one piece on the bench")
    # EN-03: "it is the only body in the box that is bolted down", and every post under
    # it goes through one of its own feet. Both sentences are this one reading — the
    # slab's whole boss census against the compressor's own mounting pattern — and
    # neither has a number in it that could drift instead.
    assert len(pack.floor_bosses) == len(_comp.mount_pattern()), (
        f"the floor slab stands {len(pack.floor_bosses)} boss(es) and the compressor's "
        f"plate has {len(_comp.mount_pattern())} holes — EN-03 fastens one body on four "
        f"posts and says nothing else in the box is bolted down")
    # EN-05: the core is reached through its LID, and the face it mates against the stratum
    # carries the copper/PRV slot and no round bore at all. Both reed cables are conduits in
    # the cap for that reason — a station on the front face is a fitting behind the condenser.
    assert {"reed-cable-a", "reed-cable-b"} <= set(cap_conduits), (
        f"the cap carries {sorted(cap_conduits)} and neither reed cable is among them — "
        f"EN-05 brings both up their own channels and out the lid, because the front face "
        f"is mated shut against the stratum")

    # The two bores in that wall, taken from the functions that STRIKE them rather
    # than recomputed beside them. `pack.back_ports` is the list `enclosure._port_cuts`
    # bores, and these are the calls that fill it — with the same carries — so a card
    # cannot state a hole the wall does not have. The union's figure is quoted once for
    # a row of four, which holds only while the four are on one diameter.
    union_bores = m.a.wall_ports["union"]
    port_hole_ds = {round(p[3], 6) for p in union_bores}
    assert len(port_hole_ds) == 1, (
        f"the +Y wall's four unions are bored at {sorted(port_hole_ds)} and EN-02/IP-02 "
        f"quote one figure for all of them")
    port_hole_d = union_bores[0][3]
    co2_hole_d = m.a.wall_ports["co2"][3]

    ox0, ox1, oy0, oy1, oz0, oz1 = box.outer
    nut_d, _ = _jg.panel_footprint()
    c14_w, _ = _c14.panel_footprint()
    # A hand has to get a socket onto each nut with its neighbours already made
    # up; this is the clear wall that leaves, priced the way
    # `_enclosure_mechanical_sync._port_chain` prices it.
    chain_3 = 3 * nut_d + 2 * 7.0

    # The four JG unions, read as an ARRANGEMENT rather than as four stations: two
    # columns, two storeys, and which column the blue ring stands on.
    #
    # `union_bores` is the same four holes the diameter is quoted off, so the
    # arrangement and the bore agree by construction.
    corners = {(round(p[1], 3), round(p[2], 3)) for p in union_bores}
    port_cols = sorted({x for x, _z in corners})
    port_storeys = sorted({z for _x, z in corners})
    assert len(port_cols) == 2 and len(port_storeys) == 2, (
        f"the +Y wall's four unions stand on {len(port_cols)} column(s) and "
        f"{len(port_storeys)} storey(s) — EN-02 seats them as a rectangle, so say what "
        f"they are instead: {sorted(corners)}")
    assert corners == {(x, z) for x in port_cols for z in port_storeys}, (
        f"two unions share a corner of the +Y wall's rectangle and one corner is empty "
        f"— EN-02 has the bench seat one body per corner: {sorted(corners)}")
    carb_end = "east" if round(_ea.PANEL_X["bulkhead-carb"], 3) == port_cols[-1] else "west"

    # The funnel opening's own rectangle against the seam it may cross.
    hx0, hx1, hy0, hy1 = m.a.hopper_hole
    funnel_pieces = ("both top pieces" if hy1 > box.y_joint
                     else "`enclosure-front-top`")
    assert abs((hx0 + hx1) / 2.0 - (ox0 + ox1) / 2.0) < 1e-6, (
        "the funnel opening is off centre across the box and EN-09 sends the bench "
        "straight down it — say where it is instead")

    # The refrigeration stratum's own width across the pair as it stands, and the cold
    # core's beside it. A body ON THE FLOOR is held one `side_band_inset` in from the ±X
    # walls where it meets one of the seam's bosses in depth AND in height, so each mouth,
    # plug and socket collar seats at full section. Both figures are carried because the
    # stated appliance width has to take whichever of them is wider, and neither the
    # card nor this comment gets to name which — the two spans do.
    def _span(*names):
        boxes = [m.a.bb(n) for n in names]
        return max(b.xmax for b in boxes) - min(b.xmin for b in boxes)

    facts = {
        # The box.
        "BOX_SIZE": f"{ox1 - ox0:.0f} {X} {oy1 - oy0:.0f} {X} {oz1 - oz0:.0f} mm",
        "BOX_PIECES": f"{len(pieces)}",
        # EN-07 pins the quadrants and nothing else: the pump cartridge is held by its
        # rails and comes out in the user's hands, so it is not one of the pieces
        # a screw crosses.
        "BOX_QUADRANTS": f"{len(quadrants)}",
        "WALL_T": f"{m.a.constants['wall']:.4g} mm",
        "Y_SEAM": f"{box.y_joint:.4g}",
        # ONE FIGURE FOR BOTH COLUMNS, which the assertion above is what holds: the
        # seam is a level line round the box, so a second name for the back column's
        # half of it would be a fact that can only ever agree with this one.
        "Z_SEAM_FRONT": f"{box.splits[0]:.4g}",
        "STRATUM_X": f"{_span('compressor', 'condenser+fan'):.0f} mm",
        "CORE_X": f"{_span('foam-assembly'):.0f} mm",
        "SIDE_BAND": f"{m.a.constants['side_band_inset']:.4g} mm",
        # Inserts set while the box is still open bench (EN-01). The +X wall's
        # count is one fact under one name: EN-01 presses those inserts, EN-06
        # drives their screws and PC-01/PC-03 send the bench to them, and four
        # cards stating one wall's boss chain cannot be allowed to disagree.
        "WALL_BOSSES": f"{len(box.east_bosses)}",
        "C14_INSERTS": f"{len(box.c14)}",
        # The +Y wall (EN-02). Arrangement, not stations.
        "BACK_BODIES": f"{len(box.back_ports)}",
        "PORT_COL_PITCH": f"{port_cols[1] - port_cols[0]:.4g} mm",
        "CARB_END": carb_end,
        "PORT_HOLE_D": f"{DIA}{port_hole_d:.4g}",
        "CO2_HOLE_D": f"{DIA}{co2_hole_d:.4g}",
        "PORT_NUT_D": f"{nut_d:.4g} mm",
        "PORT_CHAIN_3": f"{chain_3:.4g} mm",
        "C14_FLANGE_W": f"{c14_w:.4g} mm",
        "AC_RECESS": f"{ac_inlet_recess_depth_min:.4g}{NDASH}"
                     f"{ac_inlet_recess_depth_max:.4g} mm",
        # The refrigeration stratum (EN-03, EN-04). The compressor's figures are the
        # donor's own — a plate and a bolt pattern a bench measures with calipers —
        # and its crown is read off the placed body, which stands on the slab.
        "FLOOR_BOSSES": f"{len(pack.floor_bosses)}",
        "COMP_MOUNT_D": f"{_comp.MOUNT_D:.4g}",
        "COMP_MOUNT_PITCH": f"{_comp.MOUNT_PITCH_X:.4g} {X} {_comp.MOUNT_PITCH_Y:.4g} mm",
        "COMP_PLATE": f"{_comp.BASE_X:.4g} {X} {_comp.BASE_Y:.4g} mm",
        "COMP_CROWN": f"{m.a.bb('compressor').zmax:.4g} mm",
        "SIDE_OPENINGS": f"{len(box.east_ports)}",
        # The cold core (EN-05).
        "CORE_FOOTPRINT": f"{outer_shell_x_length:.4g} {X} {outer_shell_y_length:.4g} mm",
        "CAP_CONDUITS": f"{len(cap_conduits)}",
        # The funnel opening (EN-09).
        "FUNNEL_PIECES": funnel_pieces,
        # What the closed chassis reads as (EN-07).
        "BODY_COUNT": f"{len(_card.mounts())}",
    }

    cards = {
        "en-01-stage-the-printed-pieces": {
            "BOX_SIZE", "BOX_PIECES", "WALL_T", "Y_SEAM", "Z_SEAM_FRONT",
            "WALL_BOSSES", "C14_INSERTS"},
        # UMBILICAL_DROP is the internal-plumbing subsystem's name for the gap between
        # the two storeys, and one namespace spans the deck: EN-02 states the same
        # rectangle IP-05 rides, so it reads the storey pitch off the same fact rather
        # than deriving a second one that could drift from it.
        "en-02-y-wall-bodies": {
            "BACK_BODIES", "PORT_COL_PITCH", "UMBILICAL_DROP", "CARB_END",
            "PORT_HOLE_D", "CO2_HOLE_D",
            "PORT_NUT_D", "PORT_CHAIN_3", "C14_FLANGE_W", "AC_RECESS"},
        "en-03-bolt-the-compressor-down": {
            "FLOOR_BOSSES", "COMP_MOUNT_D", "COMP_MOUNT_PITCH", "COMP_PLATE",
            "COMP_CROWN"},
        "en-04-stand-the-stratum": {
            "STRATUM_X", "CORE_X", "SIDE_BAND", "SIDE_OPENINGS"},
        "en-05-seat-cold-core": {
            "CORE_FOOTPRINT", "CAP_CONDUITS", "CORE_FRONT_PORTS"},
        "en-07-close-the-box": {
            "BOX_QUADRANTS", "Y_SEAM", "Z_SEAM_FRONT",
            "BODY_COUNT"},
        "en-09-display-and-funnel": {"FUNNEL_PIECES"},
    }
    return facts, cards


# ═══ ES — Power column ════════════════════════════════════════════════

def power_column(m: Machine):
    """`power-column.md`: the five bodies of the power column, and the +X wall
    bosses each one's own hole pattern stands there."""
    import ground_ring_stack as _gnd
    import meanwell_irm90 as _psu
    import pcba_tray as _pcba
    import teyleten_relay as _relay

    # One boss per hole in each body's own pattern, carried through that body's own
    # placement (`enclosure_assembly.wall_mounts`). Counting the patterns here and the wall
    # there is the check: if they disagree, a body is mounted by something other
    # than its own holes and PC-01's table is describing a different machine.
    column = {"PSU_BOSSES": len(_psu.holes),
              "MAIN_BOARD_BOSSES": len(_pcba.board.holes),
              "RELAY1_BOSSES": len(_relay.holes),
              "RELAY2_BOSSES": len(_relay.holes),
              "GND_BOSSES": len(_gnd.holes)}
    assert sum(column.values()) == len(m.box.east_bosses), (
        f"the five bodies' own patterns hold {sum(column.values())} holes and the +X wall "
        f"stands {len(m.box.east_bosses)} bosses — PC-01's table is the wall's census, so "
        f"one of them has gained a station the other has not")

    # The screw schedule falls out of the same patterns: one M3 in through each
    # body from the room. The ground stack's is the long one — it comes down
    # through a fan of ring terminals before it reaches its insert.
    long_screws = len(_gnd.holes)
    facts = {
        "COLUMN_SCREWS_M3X8": f"{len(m.box.east_bosses) - long_screws}",
        "COLUMN_SCREWS_M3X10": f"{long_screws}",
        # The main board's own cut outline (`pcba.tsx`'s Edge_Cuts path, in the pcb
        # frame the tray shares) — not the gerber's stroked/plotted edge, which
        # reads wider by the render aperture.
        "MAIN_BOARD_SIZE": f"{_pcba.board.length:.4g} {X} {_pcba.board.width:.4g} mm",
        # No insert is pressed on this bench — every one is already in a wall boss.
        # Typed, because there is no insert census to read: none of the five bodies
        # declares inserts of its own, so nought is not a count of anything. What
        # holds it is the assertion above — every hole in every body's pattern lands
        # on a +X wall boss, so there is no boss anywhere else for this bench to set.
        # A carrier part with an insert of its own would break that equality first.
        "COLUMN_INSERTS_HERE": "0",
        **{k: str(v) for k, v in column.items()},
    }
    # EN-06 is an enclosure card and its figures are the column's — it drives the
    # screws this bench stages for. A card is registered by whichever subsystem
    # derives what it says, and `collect` merges one namespace across the deck.
    column_names = {"WALL_BOSSES", *column}
    cards = {
        "pc-01-prepare-the-wall": {
            *column_names, "COLUMN_SCREWS_M3X8", "COLUMN_SCREWS_M3X10",
            "COLUMN_INSERTS_HERE"},
        "pc-03-stage-psu-relays-board": {
            "WALL_BOSSES", "MAIN_BOARD_BOSSES", "COLUMN_INSERTS_HERE", "MAIN_BOARD_SIZE"},
        "en-06-power-column": {
            *column_names, "COLUMN_SCREWS_M3X8", "COLUMN_SCREWS_M3X10"},
    }
    return facts, cards


# One function per subsystem, in deck order. `_build.py` runs all of them.
# ═══ SA — Sub-assembly states ══════════════════════════════════════════════

def sub_assemblies(m: Machine):
    """The unit cards: what one finished sub-assembly carries, and by what joint.

    EVERY FIGURE HERE IS THE ONE THE PICTURE IS CUT WITH. `hardware/assembly/scenes`
    decides which bodies a unit shows off `_scorecard.MOUNTS` and the three anchor
    tables; these counts come off the same reading, so a card cannot say three ribs
    beside a picture that draws four."""
    import sys as _sys
    _sys.path.insert(0, str(_hw / "assembly" / "scenes"))
    import _scenes
    import _scorecard as _sc
    import _cold_core_interface as _cci
    import funnel_drain_stub as _stub
    import funnel as _funnel

    import enclosure as _enc
    import pump_tray as _tray

    holder = _scenes.holders()
    joint = {name: j for name, _by, j in _sc.mounts()}

    def under(part, *joints):
        return sorted(n for n, by in holder.items()
                      if by == part and joint.get(n) in joints)

    back_top_ribs = sorted(n for n, by in holder.items()
                           if by == "enclosure-back-top" and n.startswith("tube-"))
    cap_ribs = sorted(n for n, by in holder.items()
                      if by == "foam-assembly" and n.startswith("tube-"))
    # A rib the cap prints and a rib a zip tie closes are two counts. `fluid-14` reaches a valve
    # on the front top, so its channel leaves SA-04 empty and SA-07 is where the tie goes on.
    cap_lid = _scenes.SCENE_BY_ID["cap-lid"]
    front_top = _scenes.SCENE_BY_ID["front-top"]
    ribs_tied = [n for n in cap_ribs if n not in cap_lid.later]
    ribs_empty = [n for n in cap_ribs if n in cap_lid.later]
    cap_chains = under("foam-assembly", "cradle")
    cap_cradled = [n for n in cap_chains if n.startswith("valve-") or n == "vk-solenoid"]
    cap_chain_bodies = [n for n in cap_chains if n.endswith("-chain")]

    # The +Y wall's crossings: the bodies on that piece that no screw fastens
    # because each is drawn up by its own nut on its own thread. The split-and-
    # regulator pair bears on the same piece and is NOT this — those hang off the
    # line they splice — so the joint is what selects, not the piece.
    captured = under("enclosure-back-top", "wall-capture")

    # SA-01 and SA-02 each end on a body that is NOT in their picture: the tray in
    # one, the funnel in the other. The piece carries it in the finished machine and the
    # scene holds it back, which is the pair of readings those two sentences stand on.
    for scene_id, absent in (("back-top", "asse-drip-pan"), ("front-top", "funnel"),
                             ("funnel-drain", "funnel-drain-union"),
                             ("cap-lid", "tube-fluid-14")):
        scene = _scenes.SCENE_BY_ID[scene_id]
        assert holder.get(absent) in scene.roots and absent in scene.later, (
            f"the {scene_id} scene draws {absent}, and its card says the piece leaves the "
            f"bench without it — hold it back in `_scenes.SCENES`, or restate the card")

    # The wells this piece leaves the bench with — lever nuts pressed butt-first into printed
    # pockets, and nothing else: the collet plate stands in a SLOT rather than a well, which is
    # what keeps the steel out of a count about lever nuts.
    front_top_wells = [n for n in under("enclosure-front-top", "well")
                       if n not in front_top.later]

    # No tray stands on the piece the bay is cut in. SA-02's note sends both pumps out of the
    # front of the machine on the pump cartridge, and there is no number in that sentence.
    assert not under("enclosure-front-top", "tray"), (
        f"{', '.join(under('enclosure-front-top', 'tray'))} hang(s) in a tray on "
        f"`enclosure-front-top` — SA-02 says the pumps ride out of the front bay on "
        f"`enclosure-pump-cartridge` and this piece keeps the valves; restate the card")

    # SA-09'S UNIT IS TWO PRINTED PIECES CLOSED ON THE PUMPS BETWEEN THEM, and the pumps are
    # the only bodies standing on it. A body the tables hand this piece by some other joint is
    # a column the card has not got.
    cart_pumps = under("enclosure-pump-cartridge", "case")
    carried = sorted(n for n, by in holder.items()
                     if by == "enclosure-pump-cartridge" and n not in _sc.RIDES)
    assert carried == cart_pumps, (
        f"`enclosure-pump-cartridge` carries {carried} and closes on {cart_pumps} in the case "
        f"it makes round them — SA-09 names one joint for the whole unit; restate the card")

    # WHY A CAP CAN CARRY A PUMP AT ALL. The part's own stamped bracket stands proud of the head
    # all round in the very plane the two pieces part on, so it laps the cap's top face and the
    # two screws take the load through it. A bracket inside the head's own square laps nothing.
    assert _tray.bracket_half > _tray.head_half, (
        f"the Kamoer's bracket is {2 * _tray.bracket_half:g} across a head of "
        f"{2 * _tray.head_half:g} — SA-09 hangs both pumps off a lip standing proud all round, "
        f"and that lip is the whole load path the cap's two screws close")

    # THE FOUR BARB TUBES THE UNIT LEAVES THE BENCH HOLDING IN THE AIR, off the pumps whose
    # barbs grip them. ONE STUB PER HOLE IN THE STEEL: the plate is bored one hole per barb tee
    # and the tubes thread it as the pump cartridge goes home, so a stub with no hole in front of it
    # is one the first pull tears out. `_pump_replacement_sync` asks the service bench's half of
    # this same reading.
    cart_stubs = sorted(n for n, by in holder.items()
                        if by in set(cart_pumps) and n.startswith("tube-"))
    assert len(cart_stubs) == len(m.box.collet_plate["holes"]), (
        f"the pump cartridge carries {len(cart_stubs)} barb tube(s) and the collet plate is bored "
        f"{len(m.box.collet_plate['holes'])} hole(s) — SA-09 stands one stub in every hole")
    # WHAT EACH OF THEM STANDS PROUD OF ITS BARB, which is the berth the steel and its two airs
    # are spent in. One plate presses one plane, so the four are one figure or the card has no
    # sentence: a stub the plate is not in the berth of releases nothing.
    stands = {round(m.a.bb(n).ymax - m.a.bb(n).ymin, 6) for n in cart_stubs}
    assert len(stands) == 1, (
        f"the four barb tubes stand {sorted(stands)} proud of their barbs — SA-09 quotes one "
        f"figure for all four, and one collet plate stands in one berth")

    # SA-06's three figures are the drain joint's own stack, and each of them is read off the
    # part that owns it: the stub states its own length and how much of it the spout takes, the
    # union states the grip, and the funnel states the wall the band closes.
    _stub.joint_holds()

    # WHAT A UNIT LEAVES THE BENCH HOLDING IN THE AIR, and for the two units it is two readings.
    # A box half's is its `also` rows — runs made up early, which nothing derives. The core's is
    # read off its crossings: every conduit's tube is drawn whole, so what says whether its far
    # end is taken is whether the body that end lands on is in the picture too.
    by_id = {r.id: r for r in m.a.runs}

    def loose(scene_id):
        drawn = set(_scenes.named(_scenes.SCENE_BY_ID[scene_id], m.a.runs))
        out = []
        for _line, half in _scenes.crossings(m.a.runs).items():
            if half not in drawn:
                continue
            run = by_id[half[len("tube-"):]]
            far = next(e for e in (run.frm, run.to) if not e.startswith("foam-assembly."))
            if far.split(".")[0] not in drawn:
                out.append(half)
        return sorted(out)

    core_loose = loose("cold-core")

    # SA-08 IS SA-07 LESS SA-04, drawn from the core's own model rather than the machine's one
    # solid — so the lines it counts are the core's internal ones, standing where the cap is not.
    # `CAP_FLUID_LINES` of them rise into the cap; the PRV vent leaves at a wall slot instead,
    # which is the whole of the difference between the two counts. The cap's other two conduits
    # carry a reed cable apiece and no line at all.
    # The core's own lines are named the way the machine holds them — under `INNER_ROOT_HELD`,
    # the same path a body inside a sub-assembly carries everywhere else.
    open_core = sorted(n for n in _scenes.named(_scenes.SCENE_BY_ID["cold-core-open"], m.a.runs)
                       if n.startswith(f"{_scenes.INNER_ROOT_HELD}line-"))
    # EVERY LINE INSIDE THE SHELL IS DRAWN WHOLE, so the shortest of them is the one a bench
    # would mistake for a stub — the reservoir fills, which are the gap between two bores plus
    # the run their conduit hands to the manifold.
    assert len(open_core) == len(_cci.cap_fluid_conduits) + 1, (
        f"the open core stands {len(open_core)} internal lines against "
        f"{len(_cci.cap_fluid_conduits)} fluid conduits — SA-08 says every conduit's line and "
        f"the PRV vent, and nothing else leaves this shell")

    # EVERY FLUID CONDUIT LEAVES THE CORE CARRYING A TUBE. SA-07 stands one in each and says how
    # many end in the air; both come off the mouths the runs actually land on, so a conduit that
    # stops being plumbed — or a line that stops leaving by the top — fails here rather than
    # leaving a sentence quietly wrong beside a picture that has already changed.
    core_mouths = {f"foam-assembly.{c}" for c in _cci.cap_fluid_conduits}
    conduit_runs = sorted(r.id for r in m.a.runs if r.frm in core_mouths or r.to in core_mouths)
    assert len(conduit_runs) == len(_cci.cap_fluid_conduits), (
        f"{len(conduit_runs)} run(s) land on the core's {len(_cci.cap_fluid_conduits)} fluid "
        f"conduits ({', '.join(conduit_runs)}) — SA-07 stands one tube in every one of them")
    assert set(core_loose) <= {f"tube-{r}" for r in conduit_runs}, (
        f"the cold-core scene hangs {', '.join(sorted(set(core_loose)))}, and not every one of "
        f"them is a cap conduit's own far end — SA-07 counts loose ends by conduit")

    facts = {
        "SA01_BOSSED": f"{len(under('enclosure-back-top', 'bosses'))}",
        "SA01_CAPTURED": f"{len(captured)}",
        "SA01_RIB_RUNS": f"{len(back_top_ribs)}",
        # The front top's two columns, each a different joint on one piece: the valves and
        # the display's cover plate come down on bosses — the valve seats fused into its own
        # decks, the plate's two in the facet's inset floor — and the lever nuts stand in
        # wells printed in its walls.
        "SA02_SEATED": f"{len(under('enclosure-front-top', 'bosses'))}",
        "SA02_WELLS": f"{len(front_top_wells)}",
        "SA04_CRADLES": f"{len(cap_cradled)}",
        "SA04_CHAINS": f"{len(cap_chain_bodies)}",
        "SA04_RIB_RUNS": f"{len(ribs_tied)}",
        "SA04_RIB_EMPTY": f"{len(ribs_empty)}",
        "SA08_LINES": f"{len(open_core)}",
        "SA05_HANGING": f"{len(_scenes.SCENE_BY_ID['back-half'].also)}",
        "SA07_HANGING": f"{len(core_loose)}",
        "SA07_CLOSED": f"{len(conduit_runs) - len(core_loose)}",
        "SA06_STUB_LEN": f"{_stub.LENGTH:g}",
        "SA06_SPOUT_LAND": f"{_stub.FUNNEL_ENGAGEMENT:g}",
        "SA06_UNION_INSERT": f"{_stub.UNION_INSERTION:g}",
        "SA06_SPOUT_WALL": f"{_funnel.spout_wall:g}",
        "PUMP_MOUNT_SCREWS": f"{len(_cci.deck_mount_xy('seaflo-pump'))}",
        # A cap pours with six, clamped to the shell's face, and they come out
        # again after cure — the stack's other six belong to the other cap.
        "CAP_POUR_SCREWS": f"{len(_cci.attachment_xy_positions)}",
        # SA-09's figures are the case the two pieces make round a Kamoer: the octagon that
        # locates it, the bracket the cap carries it by, and the two screws that close on that
        # bracket. Each read off the module that cuts it.
        "SA09_PUMPS": f"{len(cart_pumps)}",
        "PUMP_SOCKET": f"{2 * _tray.boss_half:.4g} mm",
        "PUMP_BRACKET": f"{2 * _tray.bracket_half:.4g} mm",
        "PUMP_HEAD_W": f"{2 * _tray.head_half:.4g} mm",
        "SA09_CAP_SCREWS": f"{len(_enc.cap_screw_ys(m.box.inner, m.box.collet_plate))}",
        "SA09_CAP_SCREW": f"M3 {X} {_enc.screw_len:.4g}",
        # And what it leaves the bench holding out in the air, and how far that stands.
        "SA09_STUBS": f"{len(cart_stubs)}",
        "SA09_STUB_STAND": f"{stands.pop():.4g} mm",
    }

    cards = {
        "sa-01-back-top": {"SA01_BOSSED", "SA01_CAPTURED", "SA01_RIB_RUNS", "WALL_BOSSES",
                           "FLUID_18_LEN"},
        "sa-02-front-top": {"SA02_SEATED", "SA02_WELLS"},
        "sa-03-cap-lid-fill": {"CAP_POUR_SCREWS", "CAP_CONDUITS"},
        "sa-04-cap-lid": {"PUMP_MOUNT_SCREWS", "SA04_CRADLES", "SA04_CHAINS", "SA04_RIB_RUNS",
                          "SA04_RIB_EMPTY"},
        "sa-05-back-half": {"SA05_HANGING"},
        "sa-06-funnel-drain": {"SA06_STUB_LEN", "SA06_SPOUT_LAND", "SA06_UNION_INSERT",
                               "SA06_SPOUT_WALL"},
        "sa-07-cold-core": {"CAP_CONDUITS", "SA07_HANGING", "SA07_CLOSED"},
        "sa-08-cold-core-open": {"CAP_CONDUITS", "SA08_LINES"},
        "sa-09-pump-cartridge": {"SA09_PUMPS", "PUMP_SOCKET", "PUMP_BRACKET", "PUMP_HEAD_W",
                                 "SA09_CAP_SCREWS", "SA09_CAP_SCREW", "SA09_STUBS",
                                 "SA09_STUB_STAND"},
    }
    return facts, cards


SUBSYSTEMS = (deck, enclosure, power_column, cold_core, refrigerant_loop,
              internal_plumbing, bench, sub_assemblies)


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
