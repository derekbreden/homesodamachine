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

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _kit  # noqa: E402
from _bound import Env, Heap  # noqa: E402,F401


#: A holder's own plastic, everywhere it is not a stock library profile.
wall = 3.0

#: Air between a stored thing and any surface that is not holding it.
slip = 1.5

#: The V a cradle's trough is cut at, measured from horizontal. At 45 degrees the
#: trough prints as drawn and a round thing rests on two lines whatever its radius.
trough_angle = 45.0

#: A comb's slot: a parallel throat down to a taper, and a narrow root. Nothing between
#: them is read from a content. A thick tool stands the length of the throat and stops
#: where the taper meets its own thickness; a thin one runs to the root and is pinched
#: there. Taper alone would hold the thick tool 9 mm down and let it wave about.
slot_mouth = 34.0
slot_root = 5.0
slot_taper = 14.0

#: A comb's slot floor stands this far above the holder's own floor, so a tool's point
#: lands on plastic and not on the bin's base profile.
slot_floor = 6.0


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
    """What one compartment of that tub offers: clear X, clear Y, clear Z.

    The Z is to the interior ceiling — the shelf the lip stands on — and not to the top
    reference, so a thing that fits this is not crushed by whatever is stacked above.
    """
    return (
        _kit.cell_span(x_u, length_div),
        _kit.cell_span(y_u, width_div),
        _kit.interior_ceiling_z(height_u) - _kit.bin_floor_z,
    )


def assert_tub_takes(name, env, x_u, y_u, height_u, length_div=0, width_div=0, margin=slip):
    """One compartment of that tub takes `env` lying in the pose the catalog gives it.

    Reads `env` only for an upper bound, so a parcel sizes a tub honestly: whatever came
    out of that box goes into this compartment.
    """
    clear_x, clear_y, clear_z = tub_holds(x_u, y_u, height_u, length_div, width_div)
    for axis, want, have in (
        ("x", env.most("x"), clear_x),
        ("y", env.most("y"), clear_y),
        ("z", env.most("z"), clear_z),
    ):
        room = have - want
        if room < margin:
            raise ValueError(
                f"{name}: {env.name} wants {want:.1f} mm in {axis} of a {have:.1f} mm "
                f"compartment, leaving {room:.1f} mm against a {margin:.1f} mm margin"
            )
    print(
        f"   {name}: {env.name} in {clear_x:.1f} x {clear_y:.1f} x {clear_z:.1f} mm, "
        f"{min(clear_x - env.most('x'), clear_y - env.most('y'), clear_z - env.most('z')):.1f} mm spare"
    )


def tub_height_for(x_u, y_u, takes, length_div=0, width_div=0, headroom=4.0,
                   margin=slip, limit=30):
    """The shortest tub that takes all of `takes`, in height units.

    A tub's footprint and its divisions are a choice — how the bench wants the stock
    laid out. Its height is not: it is whatever the deepest thing in it needs, and
    writing that figure down by hand only invites it to go stale when a pack count
    changes. So the catalog states the footprint and this states the height.
    """
    clear_x, clear_y, _ = tub_holds(x_u, y_u, 2, length_div, width_div)
    for env in takes:
        if isinstance(env, Heap):
            continue
        for axis, clear in (("x", clear_x), ("y", clear_y)):
            if env.most(axis) + margin > clear:
                raise ValueError(
                    f"{env.name} is {env.most(axis):.1f} mm in {axis} and a {x_u}x{y_u} "
                    f"split {length_div} x {width_div} offers {clear:.1f} mm. No depth "
                    f"fixes a footprint: split it less, or stand it on a wider one."
                )

    for height_u in range(2, limit + 1):
        clear_x, clear_y, clear_z = tub_holds(x_u, y_u, height_u, length_div, width_div)
        floor = (clear_x - 2.0 * margin) * (clear_y - 2.0 * margin)
        if floor <= 0.0:
            continue
        deepest = 0.0
        for env in takes:
            if isinstance(env, Heap):
                deepest = max(deepest, env.volume / floor + headroom)
            else:
                deepest = max(deepest, env.most("z") + margin)
        if deepest <= clear_z:
            return height_u
    raise ValueError(
        f"nothing under {limit} units takes {len(takes)} things on a {x_u}x{y_u} "
        f"footprint split {length_div} x {width_div}"
    )


def assert_heap_fits(name, env, x_u, y_u, height_u, length_div=0, width_div=0, headroom=4.0):
    """A heap of loose pieces lies in one compartment without reaching its ceiling."""
    clear_x, clear_y, clear_z = tub_holds(x_u, y_u, height_u, length_div, width_div)
    floor = (clear_x - 2.0 * slip) * (clear_y - 2.0 * slip)
    stands = env.volume / floor
    if stands + headroom > clear_z:
        raise ValueError(
            f"{name}: {env.name} stands {stands:.1f} mm in a {clear_z:.1f} mm "
            f"compartment, inside the {headroom:.1f} mm that is meant to stay empty"
        )
    print(f"   {name}: {env.name} stands {stands:.1f} mm of {clear_z:.1f} mm")
    return stands


# ============================================================
# CRADLE — A V-TROUGH FOR ANYTHING ROUND
# ============================================================

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
    top_z = _kit.top_reference_z(height_u)
    half_mouth, depth, length = cradle_trough(x_u, y_u, height_u, end_wall, vertex_flat)
    half_mouth /= 2.0

    profile = [
        (-half_mouth, top_z + 0.2),
        (-vertex_flat / 2.0, top_z - depth),
        (vertex_flat / 2.0, top_z - depth),
        (half_mouth, top_z + 0.2),
    ]
    cutter = (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(length / 2.0, both=True)
    )
    return blank.cut(cutter)


def cradle_trough(x_u, y_u, height_u, end_wall=wall, vertex_flat=2.0):
    """The trough's mouth width, its depth and its clear run along X."""
    top_z = _kit.top_reference_z(height_u)
    #: The V rises at 45 degrees, so its mouth is as wide as it is deep. It stops at
    #: whichever comes first: the holder's own floor, or the plateau the lip stands on.
    half_mouth = min(
        vertex_flat / 2.0 + (top_z - _kit.bin_floor_z),
        _kit.plateau_half(y_u) - wall,
    )
    depth = half_mouth - vertex_flat / 2.0
    length = 2.0 * (_kit.plateau_half(x_u) - end_wall)
    return 2.0 * half_mouth, depth, length


def cradle_seat(mouth, depth, diameter, vertex_flat=2.0):
    """Where a reel of `diameter` comes to rest in that trough, above the plateau.

    Under the mouth it beds between the two 45-degree walls and its centre stands
    `radius * sqrt(2)` above the vertex. Over the mouth it rests on the two mouth edges
    instead and its centre stands over the plateau. Either way it is carried on two lines
    and turns; the only thing that changes with diameter is how high it rides.
    """
    radius = diameter / 2.0
    half_mouth = mouth / 2.0
    if radius / 2.0 ** 0.5 <= half_mouth:
        return radius * 2.0 ** 0.5 - depth
    return (radius ** 2 - half_mouth ** 2) ** 0.5


def assert_cradle_takes(name, env, x_u, y_u, height_u, end_wall=wall):
    """The trough is longer than the reel is wide, and the reel clears what is beside it.

    Every reading here is an upper bound — how wide the reel might be, how large across
    it might be — so a parcel's figure is a fair input. Nothing in `cradle` asks how
    *small* the reel is, which is the reading a parcel cannot give and exactly the one
    four ramps spaced at a parcel's width were asking for.
    """
    mouth, depth, length = cradle_trough(x_u, y_u, height_u, end_wall)
    width = env.thinnest  # no wider than the least side of its parcel
    across = env.longest  # and no larger across than the greatest
    if width + slip > length:
        raise ValueError(
            f"{name}: {env.name} is up to {width:.1f} mm wide in a {length:.1f} mm trough"
        )
    rides = cradle_seat(mouth, depth, across)
    overhang = across / 2.0 - rides - _kit.outer_size(y_u) / 2.0
    print(
        f"   {name}: {env.name} up to {width:.1f} mm wide and {across:.1f} mm across, "
        f"in a {mouth:.1f} mm mouth {depth:.1f} mm deep over {length:.1f} mm; "
        f"riding {rides:+.1f} mm on the plateau and standing "
        f"{across + rides:.0f} mm over the bench"
    )
    if overhang > 0.0:
        print(
            f"   {name}: and reaching {overhang:.1f} mm past the module in Y at its "
            f"widest, so nothing tall stands beside it"
        )
    return rides


def spacer(width, x_u, y_u, height_u, end_wall=wall, vertex_flat=2.0):
    """A block that drops into a cradle's trough beside a narrow reel and takes up its run.

    The cradle's own V in section, 0.4 mm under it so it slides, and `width` thick along
    the trough. Print as many as the slack wants.

    IT COMES OFF THE BED UPSIDE DOWN. Its wide face is flat and its point is a ridge, so
    it prints flat-face-down with the ridge in the air and needs no support; in the
    trough it goes the other way up, ridge into the V.
    """
    mouth, depth, _ = cradle_trough(x_u, y_u, height_u, end_wall, vertex_flat)
    half_mouth = mouth / 2.0 - 0.4
    profile = [
        (-half_mouth, 0.0),
        (-vertex_flat / 2.0, depth),
        (vertex_flat / 2.0, depth),
        (half_mouth, 0.0),
    ]
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
    """How wide a slot has to be to take `env`, from an upper bound and nothing else.

    A tool is no thicker than the least side of the box it came out of, whatever pose it
    was packed in. That reading is the one a parcel gives honestly, and it is the only
    reading a comb ever takes.
    """
    return max(least, env.thinnest + clearance)


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
    top_z = _kit.top_reference_z(height_u)
    floor_z = _kit.bin_floor_z + floor
    throat_z = floor_z + taper
    if throat_z >= top_z:
        raise ValueError(
            f"a {taper:.1f} mm taper leaves no throat in a {top_z - floor_z:.1f} mm slot"
        )

    length = 2.0 * (_kit.plateau_half(y_u) - wall)
    run = 2.0 * (_kit.plateau_half(x_u) - wall)
    span = sum(mouths) + wall * (len(mouths) - 1)
    if span > run:
        raise ValueError(
            f"{len(mouths)} slots run {span:.1f} mm over a {run:.1f} mm plateau"
        )

    cutter = None
    centers = []
    x = -span / 2.0
    for mouth in mouths:
        x += mouth / 2.0
        centers.append(x)
        profile = [
            (x - mouth / 2.0, top_z + 0.2),
            (x - mouth / 2.0, throat_z),
            (x - root / 2.0, floor_z),
            (x + root / 2.0, floor_z),
            (x + mouth / 2.0, throat_z),
            (x + mouth / 2.0, top_z + 0.2),
        ]
        one = (
            cq.Workplane("XZ")
            .polyline(profile)
            .close()
            .extrude(length / 2.0, both=True)
        )
        cutter = one if cutter is None else cutter.union(one)
        x += mouth / 2.0 + wall
    return blank.cut(cutter), centers


def comb_slot(y_u, height_u, mouth, root=slot_root, floor=slot_floor):
    """One slot's mouth, its root, its depth and its run along Y."""
    depth = _kit.top_reference_z(height_u) - (_kit.bin_floor_z + floor)
    return mouth, root, depth, 2.0 * (_kit.plateau_half(y_u) - wall)


def comb_grip(depth, thickness, mouth, root=slot_root, taper=slot_taper):
    """How far a tool `thickness` thick descends into a slot of that depth.

    The throat first, then as far into the taper as its own thickness allows. This is
    the figure that says whether a tool stands or waves about, and it is read from an
    upper bound on the tool: a thicker reading gives a shallower answer, so a parcel's
    figure understates the grip and never overstates it.
    """
    throat = depth - taper
    if thickness >= mouth:
        return throat
    if thickness <= root:
        return depth
    return throat + taper * (mouth - thickness) / (mouth - root)


def assert_comb_takes(name, env, y_u, height_u, mouth, neighbour,
                      root=slot_root, floor=slot_floor, taper=slot_taper):
    """A tool goes into its slot, stands in it, and stays out of the next one.

    Upper bounds only. The tool is no thicker than the least side of its parcel, so the
    mouth takes it and the taper stops it; no wider across than the middle side, so the
    slot's run takes it; no longer than the greatest, so its lean is no worse than this.

    A slot cut to an upper bound is loose around a tool that turns out thinner, and a
    loose tool leans. What matters is not that it stands plumb — no tool in a rack does —
    but that it does not come to rest on the tool beside it. `neighbour` is how far away
    that is.
    """
    mouth_w, root_w, depth, length = comb_slot(y_u, height_u, mouth, root, floor)
    thick = env.thinnest
    if thick + 1.0 > mouth_w:
        raise ValueError(
            f"{name}: {env.name} is up to {thick:.1f} mm thick at a {mouth_w:.1f} mm mouth"
        )
    across = sorted((env.x, env.y, env.z))[1]
    if across > length:
        raise ValueError(
            f"{name}: {env.name} is up to {across:.1f} mm across a {length:.1f} mm slot"
        )
    grip = comb_grip(depth, thick, mouth_w, root_w, taper)
    stands = env.longest - grip
    lean = env.longest * (mouth_w - thick) / grip
    if lean > neighbour:
        raise ValueError(
            f"{name}: {env.name} leans up to {lean:.0f} mm at the top with "
            f"{neighbour:.0f} mm to the slot beside it"
        )
    print(
        f"   {name}: {env.name} up to {thick:.1f} mm thick in a {mouth_w:.1f} mm mouth, "
        f"held over {grip:.1f} mm, standing {stands:.0f} mm proud, leaning at most "
        f"{lean:.0f} of {neighbour:.0f} mm"
    )
    return stands


# ============================================================
# INDEX — BORES AT A NOMINAL SIZE
# ============================================================

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
    top_z = _kit.top_reference_z(height_u)
    floor_z = _kit.bin_floor_z + floor
    if depth is not None:
        floor_z = max(floor_z, top_z - depth)

    reach_x = _kit.plateau_half(x_u) - wall
    reach_y = _kit.plateau_half(y_u) - wall

    laid = []
    for row in rows:
        bores = [(env, env.size("x") + slip) for env, count in row for _ in range(count)]
        run = sum(d for _, d in bores) + wall * (len(bores) - 1)
        if run > 2.0 * reach_x:
            raise ValueError(
                f"a row of {len(bores)} bores runs {run:.1f} mm over a "
                f"{2.0 * reach_x:.1f} mm plateau"
            )
        x = -run / 2.0
        placed_row = []
        for env, diameter in bores:
            x += diameter / 2.0
            placed_row.append((env, x, diameter))
            x += diameter / 2.0 + wall
        laid.append((placed_row, max(d for _, d in bores)))

    height = sum(depth_y for _, depth_y in laid) + wall * (len(laid) - 1)
    if height > 2.0 * reach_y:
        raise ValueError(
            f"{len(laid)} rows stand {height:.1f} mm over a {2.0 * reach_y:.1f} mm plateau"
        )

    cutter = None
    placed = []
    y = height / 2.0
    for placed_row, row_depth in laid:
        y -= row_depth / 2.0
        for env, x, diameter in placed_row:
            one = _kit.round_pocket(diameter, x, y, floor_z, top_z)
            cutter = one if cutter is None else cutter.union(one)
            placed.append((env, x, y, diameter))
        y -= row_depth / 2.0 + wall

    _kit.assert_inside_plateau(
        f"index {x_u}x{y_u}x{height_u}",
        max(abs(x) + d / 2.0 for _, x, _, d in placed),
        max(abs(y) + d / 2.0 for _, _, y, d in placed),
        x_u,
        y_u,
    )
    return blank.cut(cutter), placed


def index_depth(height_u, floor=4.0, depth=None):
    """How deep a bore runs from the plateau."""
    top_z = _kit.top_reference_z(height_u)
    floor_z = _kit.bin_floor_z + floor
    if depth is not None:
        floor_z = max(floor_z, top_z - depth)
    return top_z - floor_z


def assert_index_holds(name, env, height_u, floor=4.0, depth=None, min_grip=12.0):
    """A thing standing in its bore is held over enough of its length to stand up."""
    grip = index_depth(height_u, floor, depth)
    stands = env.size("z") - grip
    if grip < min_grip:
        raise ValueError(
            f"{name}: {env.name} is held over {grip:.1f} mm, against {min_grip:.1f} mm"
        )
    print(
        f"   {name}: {env.name} at {env.size('x'):.2f} mm, held over {grip:.1f} mm, "
        f"standing {stands:.0f} mm proud"
    )
    return stands


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
