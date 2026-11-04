"""The four shapes a holder is cut in, and the dock they all stand on.

Frame: world +Z is up, +Y is the operator-facing front, +X is the operator's right.
Every holder is a stock cq-gridfinity body on the 42 mm grid with its bottom at Z = 0,
prints on its own feet without support, and stands anywhere a baseplate reaches.

Each shape is chosen for what it does *not* need to know:

- **tub** — an open bin, plain or divided. Needs an upper bound on what goes in it and
  nothing else. Loose stock, packs decanted, anything that stands on a floor.
- **cradle** — a 90-degree V-trough. A round thing self-centres in a V at any radius and
  is free to turn, so the trough reads neither the diameter nor the width of the spool
  it carries. Wire, solder, tape, ribbon, braid.
- **comb** — slots that taper from a wide mouth to a narrow root. A tool descends until
  its own thickness wedges it, so the slot reads no thickness. Pliers, cutters, crimpers,
  strippers, anything flat that stands.
- **index** — bores at a nominal diameter. This one *does* cut to a size, and the only
  figures it accepts are exact ones: a 9/64 in drill is 9/64 in, a T18 barrel is 6.5 mm.

`_bound.Env` is what keeps the difference honest. A tub, a cradle and a comb read only
upper bounds, so a parcel's figure sizes them fairly and no fit rests on it; an index
reads `Env.size` for every bore, so a parcel offered to one is refused at build time.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware") / "scripts"))
import _rust_part
_rust_part.start()

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _kit  # noqa: E402
from _bound import Env, Heap  # noqa: E402,F401


#: A holder's own plastic, everywhere it is not a stock library profile.

import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('_holder')
globals().update({name: _reference_values[name] for name in ('wall', 'slip', 'trough_angle', 'slot_mouth', 'slot_root', 'slot_taper', 'slot_floor')})


#: Air between a stored thing and any surface that is not holding it.

#: The V a cradle's trough is cut at, measured from horizontal. At 45 degrees the
#: trough prints as drawn and a round thing rests on two lines whatever its radius.

#: A comb's slot: a parallel throat down to a taper, and a narrow root. Nothing between
#: them is read from a content. A thick tool stands the length of the throat and stops
#: where the taper meets its own thickness; a thin one runs to the root and is pinched
#: there. Taper alone would hold the thick tool 9 mm down and let it wave about.

#: A comb's slot floor stands this far above the holder's own floor, so a tool's point
#: lands on plastic and not on the bin's base profile.


# ============================================================
# THE DOCK
# ============================================================

def dock(x_u, y_u):
    """The bench plate holders stand on. Any Gridfinity baseplate docks any holder."""
    return _kit.dock_body(x_u, y_u)


# ============================================================
# TUB — AN OPEN BIN
# ============================================================

def tub(x_u, y_u, height_u, length_div=0, width_div=0, labels=True, scoops=False):
    """An open bin, `length_div` walls across X and `width_div` across Y.

    The library's own body. Its label ledge stands on the +Y wall and takes 12 mm tape,
    and a divided bin carries a shallower ledge along each divider.
    """
    return _kit.bin_body(
        x_u,
        y_u,
        height_u,
        length_div=length_div,
        width_div=width_div,
        labels=labels,
        scoops=scoops,
    )


def tub_holds(x_u, y_u, height_u, length_div=0, width_div=0):
    'What one compartment of that tub offers: clear X, clear Y, clear Z.\n\n    The Z is to the interior ceiling — the shelf the lip stands on — and not to the top\n    reference, so a thing that fits this is not crushed by whatever is stacked above.\n    '
    return _reference_data('_holder', 'tub_holds', (x_u, y_u, height_u, length_div, width_div), {})


def assert_tub_takes(name, env, x_u, y_u, height_u, length_div=0, width_div=0):
    'The room one compartment of that tub leaves around `env`, lying in the pose the\n    catalog gives it.\n\n    Reads `env` only for an upper bound, so a parcel sizes a tub honestly: whatever came\n    out of that box goes into this compartment.\n    '
    return _reference_data('_holder', 'assert_tub_takes', (name, env, x_u, y_u, height_u, length_div, width_div), {})


def tub_height_for(x_u, y_u, takes, length_div=0, width_div=0, headroom=4.0, margin=slip, limit=30):
    "The shortest tub that takes all of `takes`, in height units.\n\n    A tub's footprint and its divisions are a choice — how the bench wants the stock\n    laid out. Its height is not: it is whatever the deepest thing in it needs, and\n    writing that figure down by hand only invites it to go stale when a pack count\n    changes. So the catalog states the footprint and this states the height.\n    "
    return _reference_data('_holder', 'tub_height_for', (x_u, y_u, takes, length_div, width_div, headroom, margin, limit), {})


def assert_heap_fits(name, env, x_u, y_u, height_u, length_div=0, width_div=0):
    'How deep a heap of loose pieces stands in one compartment.'
    return _reference_data('_holder', 'assert_heap_fits', (name, env, x_u, y_u, height_u, length_div, width_div), {})


# ============================================================
# CRADLE — A V-TROUGH FOR ANYTHING ROUND
# ============================================================

def cradle_profile(x_u, y_u, height_u, end_wall=wall, vertex_flat=2.0):
    'The authored V cutter profile and its clear run.'
    return _reference_data('_holder', 'cradle_profile', (x_u, y_u, height_u, end_wall, vertex_flat), {})


def cradle(x_u, y_u, height_u, end_wall=wall, vertex_flat=2.0):
    """A solid blank with a 90-degree V cut along X, and an end wall at each end of it.

    A cylinder laid in a V rests on two lines and centres itself between them, and it
    does that at every radius: nothing here is cut to a spool's diameter or to its width.
    The trough runs as deep as the blank allows and its walls rise at `trough_angle`, so
    a small reel sits low between them and a large one rides high on the mouth edges.
    Both turn freely, which is what a wire spool is for.

    The reel is free to wander along X between the end walls; `spacer` fills the slack
    beside a narrow one.
    """
    blank = _kit.blank_body(x_u, y_u, height_u)
    profile, length = cradle_profile(x_u, y_u, height_u, end_wall, vertex_flat)
    cutter = (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(length / 2.0, both=True)
    )
    return blank.cut(cutter)


def cradle_trough(x_u, y_u, height_u, end_wall=wall, vertex_flat=2.0):
    "The trough's mouth width, its depth and its clear run along X."
    return _reference_data('_holder', 'cradle_trough', (x_u, y_u, height_u, end_wall, vertex_flat), {})


def cradle_seat(mouth, depth, diameter, vertex_flat=2.0):
    'Where a reel of `diameter` comes to rest in that trough, above the plateau.\n\n    Under the mouth it beds between the two 45-degree walls and its centre stands\n    `radius * sqrt(2)` above the vertex. Over the mouth it rests on the two mouth edges\n    instead and its centre stands over the plateau. Either way it is carried on two lines\n    and turns; the only thing that changes with diameter is how high it rides.\n    '
    return _reference_data('_holder', 'cradle_seat', (mouth, depth, diameter, vertex_flat), {})


def assert_cradle_takes(name, env, x_u, y_u, height_u, end_wall=wall):
    "The trough is longer than the reel is wide, and the reel clears what is beside it.\n\n    Every reading here is an upper bound — how wide the reel might be, how large across\n    it might be — so a parcel's figure is a fair input. Nothing in `cradle` asks how\n    *small* the reel is, which is the reading a parcel cannot give and exactly the one\n    four ramps spaced at a parcel's width were asking for.\n    "
    return _reference_data('_holder', 'assert_cradle_takes', (name, env, x_u, y_u, height_u, end_wall), {})


def spacer_profile(width, x_u, y_u, height_u, end_wall=wall, vertex_flat=2.0):
    'The authored sliding V profile, in its flat-face-down print pose.'
    return _reference_data('_holder', 'spacer_profile', (width, x_u, y_u, height_u, end_wall, vertex_flat), {})


def spacer(width, x_u, y_u, height_u, end_wall=wall, vertex_flat=2.0):
    """A block that drops into a cradle's trough beside a narrow reel and takes up its run.

    The cradle's own V in section, 0.4 mm under it so it slides, and `width` thick along
    the trough. Print as many as the slack wants.

    IT COMES OFF THE BED UPSIDE DOWN. Its wide face is flat and its point is a ridge, so
    it prints flat-face-down with the ridge in the air and needs no support; in the
    trough it goes the other way up, ridge into the V.
    """
    profile = spacer_profile(width, x_u, y_u, height_u, end_wall, vertex_flat)
    return (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(width / 2.0, both=True)
    )


# ============================================================
# COMB — A SLOT PER TOOL, THROAT THEN TAPER
# ============================================================

def slot_mouth_for(env, clearance=2.0, least=8.0):
    'How wide a slot has to be to take `env`, from an upper bound and nothing else.\n\n    A tool is no thicker than the least side of the box it came out of, whatever pose it\n    was packed in. That reading is the one a parcel gives honestly, and it is the only\n    reading a comb ever takes.\n    '
    return _reference_data('_holder', 'slot_mouth_for', (env, clearance, least), {})


def comb_layout(x_u, y_u, height_u, mouths, root=slot_root, floor=slot_floor, taper=slot_taper):
    'Slot profiles and clear run, shared by the native builder and kernel.'
    return _reference_data('_holder', 'comb_layout', (x_u, y_u, height_u, mouths, root, floor, taper), {})


def comb(x_u, y_u, height_u, mouths, root=slot_root, floor=slot_floor, taper=slot_taper):
    """A solid blank with one slot per tool, cut along Y and packed across X.

    A slot runs its own `mouth` across from the plateau down a parallel throat, then
    closes to `root` over the last `taper` of its depth. A tool goes in head down and
    descends until its own thickness meets the taper: a crimper head stops at the bottom
    of the throat with the whole throat around it, a tweezer runs on to the root and is
    pinched there.

    Each slot is cut to the tool it takes rather than to the widest of the family, so a
    15 mm pliers wrench is not rattling in a 46 mm mouth beside a 41 mm tubing cutter.
    The taper leans about 45 degrees and the throat is vertical: the whole slot prints
    as drawn.
    """
    blank = _kit.blank_body(x_u, y_u, height_u)
    profiles, length = comb_layout(x_u, y_u, height_u, mouths, root, floor, taper)
    cutter = None
    for profile in profiles:
        one = (
            cq.Workplane("XZ")
            .polyline(profile)
            .close()
            .extrude(length / 2.0, both=True)
        )
        cutter = one if cutter is None else cutter.union(one)
    return blank.cut(cutter)


def comb_slot(y_u, height_u, mouth, root=slot_root, floor=slot_floor):
    """One slot's mouth, its root, its depth and its run along Y."""
    return _reference_data('_holder', 'comb_slot', (y_u, height_u, mouth, root, floor), {})


def comb_grip(depth, thickness, mouth, root=slot_root, taper=slot_taper):
    "How far a tool `thickness` thick descends into a slot of that depth.\n\n    The throat first, then as far into the taper as its own thickness allows. This is\n    the figure that says whether a tool stands or waves about, and it is read from an\n    upper bound on the tool: a thicker reading gives a shallower answer, so a parcel's\n    figure understates the grip and never overstates it.\n    "
    return _reference_data('_holder', 'comb_grip', (depth, thickness, mouth, root, taper), {})


def assert_comb_takes(name, env, y_u, height_u, mouth, root=slot_root, floor=slot_floor, taper=slot_taper):
    "A tool goes into its slot and stands in it.\n\n    Upper bounds only. The tool is no thicker than the least side of its parcel, so the\n    mouth takes it and the taper stops it; no wider across than the middle side, so the\n    slot's run takes it; no longer than the greatest, so its lean is no worse than this.\n    "
    return _reference_data('_holder', 'assert_comb_takes', (name, env, y_u, height_u, mouth, root, floor, taper), {})


# ============================================================
# INDEX — BORES AT A NOMINAL SIZE
# ============================================================

def index_layout(x_u, y_u, height_u, rows, depth=None, floor=4.0):
    'Nominal bore positions and floor, shared by native and kernel builders.'
    return _reference_data('_holder', 'index_layout', (x_u, y_u, height_u, rows, depth, floor), {})


def index(x_u, y_u, height_u, rows, depth=None, floor=4.0):
    """A solid blank bored for things whose diameter is a standard.

    `rows` reads front to back; each row is a list of `(env, count)` and each row is
    pitched on its own bores, so a row of twelve 3.6 mm drills packs tight in front of a
    row of five countersinks stepping 1/4 to 3/4 inch. Within a row, neighbours stand a
    wall apart whatever their two diameters, and a row is only as deep as its widest bore.

    Every `env` is read with `Env.size`, so an index built on a parcel's figure does not
    build: a bore is cut *to* a thing, and a parcel says only what box it came in.
    """
    blank = _kit.blank_body(x_u, y_u, height_u)
    floor_z, top_z, placed = index_layout(x_u, y_u, height_u, rows, depth, floor)
    cutter = None
    for env, x, y, diameter in placed:
        one = _kit.round_pocket(diameter, x, y, floor_z, top_z)
        cutter = one if cutter is None else cutter.union(one)
    return blank.cut(cutter), placed


def index_depth(height_u, floor=4.0, depth=None):
    'How deep a bore runs from the plateau.'
    return _reference_data('_holder', 'index_depth', (height_u, floor, depth), {})


def assert_index_holds(name, env, height_u, floor=4.0, depth=None):
    'How far a thing standing in its bore is held, and how far it stands proud.'
    return _reference_data('_holder', 'assert_index_holds', (name, env, height_u, floor, depth), {})


# ============================================================
# CHECKS EVERY HOLDER RUNS
# ============================================================

def assert_printable(name, shape):
    """One solid, inside the printer, standing on its own feet."""
    _kit.assert_one_solid(name, shape)
    _kit.assert_h2c_fit(name, shape)


def assert_docks(name, plate, shape):
    """The holder seats on a baseplate, touching it and entering it nowhere."""
    _kit.assert_seated(f"{name} on the dock", plate, shape, _kit.dock_seat_z)
