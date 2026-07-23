"""Bag-circuit tray: 4 axis-aligned Beduan valves + 2 Tee fittings.

The [fluid-topology](../../../topology/fluid-topology.md) bag circuit as a
tray. The four valves sit ports-along-X with no aiming tilt, paired in two
columns: V-F over V-I on the −X side, V-E over V-H on the +X side. Each row's
two valves connect **in-line through a Tee** whose run lies along X, leaving the
Tee free to ROLL about that run: the branch aims wherever the roll puts it, and
`branch_rolls` carries one angle per Tee.

    V-I ──┬── V-H      Y-H run; branch rolled to `bag_fall_aim`, near +Z
          ┊
    V-F ──┴── V-E      Y-E run; branch → −Y to Bag A, through the hug wall

Y-E squares outward at +90°, leaving along −Y through a notch in the central hug
wall. Y-H is AIMED instead — see `bag_fall_aim` — so its branch leaves near +Z,
clearing the hug walls entirely rather than passing through one.

This module also holds the shared parallel-tray base — `place_valve`, `place_tee`
(and its roll variant `place_tee_rolled`), `build_tray`, and the common geometry
— imported by the nozzle-gate tray in `../nozzle-gate-tray/`.

Origin = cell center, Z = 0 the valve mounting plane, ports at Z = 11.3.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw.parent / "tools",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
import single_tray as cell

port_z = cell.port_center_z
socket_radius = cell.socket_radius
saddle_radius = cell.saddle_radius
corner_pos = cell.corner_pos
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
socket_floor_z = cell.socket_floor_z
_tee_path = _hw / "reference" / "tee-connector" / "tee-connector.step"
_elbow_path = _hw / "reference" / "elbow-connector" / "elbow-connector.step"

# --- Shared geometry ------------------------------------------------------
port_half = 29.5  # valve port half-length
row_half = cell.valve.body_width_x / 2  # column-pair half-spacing = the valve's X half-width
tee_run_half = 20.07  # Tee run half-length (port to center)
tee_branch_reach = 20.066  # Tee branch: run-center to branch-port tip
valve_x = tee_run_half + port_half  # valve-center X; the inner port tip lands on the Tee run port
elbow_reach = 19.56  # elbow leg: collet face to the bend corner (axis intersection)

# This tray's valves + Tees. The enclosure hangs this tray INVERTED (180°
# about Y — see _contents), which negates local X and Z and keeps local Y; the
# name↔row assignment is chosen so each valve lands on the world station its
# fluid-topology channel pairs with — channel A (V-E/V-F, Tee Y-E) forward
# under the source tray's V-C, channel B (V-H/V-I, Y-H) aft.
valves = {
    "VI": (-valve_x, +row_half),
    "VF": (-valve_x, -row_half),
    "VH": (+valve_x, +row_half),
    "VE": (+valve_x, -row_half),
}
# Tee centers; run along X joins the row's two valves.
tees = {"YH": (0.0, +row_half), "YE": (0.0, -row_half)}

# A Tee's run seats in a plain cylindrical groove, so nothing in the tray fixes
# how far the fitting is rolled about it — the branch may aim anywhere in the
# plane perpendicular to the run, not merely at the four square poses. The roll
# is measured off `place_tee`'s branch-up (+Z) pose, positive about local +X.
#
# The enclosure hangs this tray INVERTED (180° about Y — see _contents), which
# carries local Y and negates local Z: a branch at roll 0 points straight DOWN in
# world, ±90 leaves along ∓Y.
#
# `bag_fall_aim` is Y-H's. Bag B's line falls the whole height of the machine to
# reservoir B low on the cold core, and this is the roll that points the branch
# down that fall — at the fall corridor's lane, at the port's own height — so the
# line leaves the fitting ALREADY FALLING and takes no bend at the top. The STEP
# bakes the pose in, so the angle is declared here and gated in
# enclosure-assembly/_lines, which re-solves the aim against the live corridor and
# port and raises if this roll no longer lands on the lane.
# Y-E squares outward into the hug wall's notch, its own line unrouted.
bag_fall_aim = -9.1619
branch_rolls = {"YH": bag_fall_aim, "YE": +90.0}


def branch_dir(roll):
    """A Tee branch's unit axis in tray coordinates, for a roll about its run.
    Roll 0 is `place_tee`'s branch-up (+Z); positive rolls about local +X."""
    r = math.radians(roll)
    return (0.0, -math.sin(r), math.cos(r))


def place_valve(cx, cy, rot):
    """Valve rotated ``rot`` deg about Z; flow arrow (local +Y) points toward
    the spades = the outlet."""
    return (
        cell.valve.build_beduan_solenoid()
        .val()
        .rotate((0, 0, 0), (0, 0, 1), rot)
        .translate((cx, cy, 0.0))
    )


def place_tee(cx, cy):
    """Tee, run along X (joins valves / butts the next Tee), branch up (+Z)."""
    fit = cq.importers.importStep(str(_tee_path)).val()
    return (
        fit.rotate((0, 0, 0), (0, 1, 0), 90.0)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
        .translate((cx, cy, port_z))
    )


def place_tee_rolled(cx, cy, roll):
    """Tee, run along X (valve on the −X end), rolled ``roll`` degrees about that
    run off `place_tee`'s branch-up pose — the fitting's one free axis, since the
    groove it seats in is a plain cylinder. ±90 turns the branch outward along ∓Y
    through the hug wall's notch; a small roll leaves it near +Z, clear of the
    walls. `branch_dir` gives the axis the branch ends up on."""
    return place_tee(cx, cy).rotate(
        (cx, cy, port_z), (cx + 1.0, cy, port_z), roll
    )


def place_elbow(cx, cy, ux, uy, roll=0.0):
    """Elbow on a valve's outer (unoccupied) port: one leg collinear with the
    port axis — its collet butting the port tip — and the free leg turned by
    ``roll`` about that axis: 0 points it +Z up out of the tray, 180 straight
    down, ±90 sideways. ``(cx, cy)`` is the valve center; ``(ux, uy)`` the
    outward unit vector of that port (pointing away from the valve). The free
    collet lands ``elbow_reach`` from the bend corner along the rolled leg."""
    fit = cq.importers.importStep(str(_elbow_path)).val()
    # The elbow's native +Y leg maps onto the −outward direction (collet faces
    # the valve); a Z-only rotation leaves its +Z leg pointing up.
    phi = math.degrees(math.atan2(ux, -uy))
    corner = (
        cx + (port_half + elbow_reach) * ux,
        cy + (port_half + elbow_reach) * uy,
        port_z,
    )
    e = fit.rotate((0, 0, 0), (0, 0, 1), phi).translate(corner)
    if roll:
        e = e.rotate(corner, (corner[0] + ux, corner[1] + uy, corner[2]), roll)
    return e


def elbow_collet(cx, cy, ux, uy, roll=0.0):
    """Where `place_elbow` leaves the free collet, in tray coordinates:
    (position, outward unit axis). This is the tray's boundary anchor — a line
    leaves along the axis and the enclosure carries both through its placement
    to get the world port. Same arguments as `place_elbow`, so the two cannot
    describe different elbows."""
    r = math.radians(roll)
    d = (uy * math.sin(r), -ux * math.sin(r), math.cos(r))
    corner = (
        cx + (port_half + elbow_reach) * ux,
        cy + (port_half + elbow_reach) * uy,
        port_z,
    )
    return tuple(corner[i] + elbow_reach * d[i] for i in range(3)), d


def build_assembly():
    # Outlets point +X: V-F/V-I out to the center Tees, V-E/V-H out to the pumps.
    parts = {nm: place_valve(*p, -90.0) for nm, p in valves.items()}
    # Each Tee is rolled about its run to aim its bag branch (`branch_rolls`).
    parts.update({nm: place_tee_rolled(*p, branch_rolls[nm]) for nm, p in tees.items()})
    # An elbow turns each junction-column valve's outer (unoccupied) port off
    # the tray, clocked by `rolls`; the east bank's outer ports run bare.
    parts.update({
        f"E{nm}": place_elbow(*valves[nm], *_outer_port(valves[nm][0]), roll=roll)
        for nm, roll in rolls.items()
    })
    return parts


def _outer_port(cx):
    """The outward unit vector of a valve's outer port — this tray's valves run
    ports-along-X, so it is simply which end of the row the valve sits on."""
    return (-1.0 if cx < 0 else 1.0), 0.0


def boundary_collets():
    """Every boundary connector in tray coordinates: {name: (position, outward
    axis)} — the west bank's outer-elbow free collets (V-E/V-H, the junction
    column) and the east bank's bare outer-port tips (V-F/V-I, awaiting the
    pump-discharge tees). The tray's boundary — what the enclosure routes
    lines to."""
    out = {}
    for nm, (cx, cy) in valves.items():
        ux, uy = _outer_port(cx)
        if nm in rolls:
            out[nm] = elbow_collet(cx, cy, ux, uy, roll=rolls[nm])
        else:
            out[nm] = ((cx + port_half * ux, cy + port_half * uy, port_z),
                       (ux, uy, 0.0))
    return out


def bag_branches():
    """Each Tee's bag-branch collet tip in tray coordinates, same shape as
    `boundary_collets` — the tip `tee_branch_reach` from the run centre along the
    axis its roll puts the branch on. Same `branch_rolls` the solid is built from,
    so the anchor and the fitting cannot describe different branches."""
    out = {}
    for nm, (cx, cy) in tees.items():
        d = branch_dir(branch_rolls[nm])
        c = (cx, cy, port_z)
        out[nm] = (tuple(c[i] + tee_branch_reach * d[i] for i in range(3)), d)
    return out


# --- Tray frame + stacking walls ------------------------------------------
margin = 3.0
wall_thickness = 3.0
wall_clear = 1.0
# A wall's own job ends at the top of what it retains — the valve's coil.
valve_coil_top_z = cell.valve.coil_z_range[1]
# A STACKED tray's walls do a second job: they are the seat the tray above lands on
# (scorecard `TOUCHING_OK`), and so they are the only thing holding this tray's coils
# off the facing tray's across that seam. STACK_COIL_CLEAR is that facing-coil gap,
# split between the two trays — the whole reason a stacking wall stands proud of its
# valve at all. A tray whose wall tops face open air instead (the nozzle gate, hung
# valves-up) carries no seat, so it passes `wall_top=valve_coil_top_z` and ends flush.
# Twice the enclosure's clearance floor. The two coils are purchased bodies that must
# never be clamped between their trays, and nothing else rides this gap; every
# millimetre of it costs two in stack height. Seeded, not ratified — like `BEND_RATIO`.
stack_coil_clear = 3.4
wall_top_z = valve_coil_top_z + stack_coil_clear / 2.0
stack_pitch = wall_top_z - bot_z

# Valve reach in X from its center, per height band. These trays seat the valves
# ports-along-X (rotated ±90°), so a feature's local Y depth is what it reaches in
# tray X: the white body — round boss and top box alike — runs out to
# [16.12](VALVE_BODY_HALF_X) mm and tops out at Z [30.6](VALVE_BODY_TOP_Z), and above
# that only the coil stands, the motor body, a thinner protrusion reaching
# [12](VALVE_COIL_HALF_X) mm. The stacking walls step with it and end flush in both
# bands, so no wall stands proud of a valve at its own height and none cuts into the
# wider body below. The ports and the spade terminals reach further still and are no
# concern of the walls; the floor keeps the full plate to carry the corner sockets.
valve_body_half_x = max(cell.valve.body_radius, cell.valve.body_width / 2.0)
valve_coil_half_x = cell.valve.coil_depth / 2.0
valve_body_top_z = cell.valve.body_top_z


# --- The junction column's aim --------------------------------------------
# In the enclosure the two manifold trays stack wall-top to wall-top with
# their west outlet elbows facing each other across the gap, and a union tee
# hangs between them (fluid-topology Y-C / Y-F). Their west port rows lie
# [19.6](JUNCTION_OFFSET) mm apart in Y: this tray's elbow corner sits on its
# valve's own row, the source tray's swings wider, its valves being aimed at
# their divider outlets.
#
# Each elbow rolls off its port axis to take up that offset — the source pair
# INWARD, this tray's pair OUTWARD — until the two collets aim down one line,
# with the tee hung on it and a straight stub at each end. `junction_roll` is
# the roll leaving the least angle between a collet's own axis and that line.
# `junction_skew` is the angle left at each end: the source tray's elbow leaves
# the YZ plane as it rolls and this tray's stays in it, so the two axes reach
# the line out of different planes. `junction_dx` is the X gap between the
# collets that splits the skew evenly, supplied by the bag tray's slide.
src_elbow_row = 36.725     # the source tray's west elbow corner |Y| and the
src_port_tilt = 18.30      # plan tilt of the port it rides — both asserted
                           # against the real layout in source_select_tray
bag_elbow_row = row_half   # this tray's ports run along X: corner on the row
junction_offset = src_elbow_row - bag_elbow_row    # the rows' Y disagreement
junction_rise = 2 * wall_top_z - 2 * port_z        # corner to corner, stacked


def _junction_aim():
    """Solve the elbow roll that best aims the two facing collets at each
    other. A collet rides the end of its elbow leg, so a roll moves it and
    turns it together; the cost is the worse of the two angles between a
    collet's axis and the line joining the pair, minimised over the roll and
    over the X gap the bag tray's slide is free to set. Returns (roll°,
    skew°, dx) — the source rolls +roll and this tray −roll on the same row
    (mirrored on the other), which is what makes one turn in and one out."""
    tilt = math.radians(src_port_tilt)
    sux, suy = math.cos(tilt), math.sin(tilt)

    def worst(t, dx):
        s, c = math.sin(t), math.cos(t)
        ns = (-suy * s, sux * s, c)                     # source collet, rolled in
        nb = (0.0, -s, -c)                              # bag collet, rolled out
        ps = [elbow_reach * v for v in ns]
        pb = [o + elbow_reach * v for o, v in
              zip((dx, junction_offset, junction_rise), nb)]
        j = [pb[i] - ps[i] for i in range(3)]
        m = math.sqrt(sum(v * v for v in j))
        j = [v / m for v in j]

        def angle(n):
            d = max(-1.0, min(1.0, sum(n[i] * j[i] for i in range(3))))
            return math.degrees(math.acos(d))

        return max(angle(ns), angle([-v for v in nb]))

    def minimise(f, lo, hi):
        for _ in range(80):
            m1, m2 = lo + (hi - lo) / 3.0, hi - (hi - lo) / 3.0
            lo, hi = (lo, m2) if f(m1) < f(m2) else (m1, hi)
        return (lo + hi) / 2.0

    def dx_for(t):
        return minimise(lambda d: worst(t, d), -15.0, 15.0)

    t = minimise(lambda tt: worst(tt, dx_for(tt)), 0.0, math.radians(45.0))
    return math.degrees(t), worst(t, dx_for(t)), dx_for(t)


junction_roll, junction_skew, junction_dx = _junction_aim()

# Per-valve elbow rolls — only the junction column's west bank wears elbows,
# authored for this tray's INVERTED pose in the enclosure (hung 180° about Y),
# which turns a local up-turn straight DOWN in world: V-E/V-H keep the local
# up-turn and add the junction aim — rolled OUTWARD (away from the tray
# centreline, mirrored per row) so each collet faces down the line to the
# source tray's, which rolls the same amount inward to meet it. The east
# bank's outer ports (V-F/V-I) run bare, facing east in world at the
# nozzle-gate pocket, awaiting the pump-discharge tees (Y-D / Y-G).
rolls = {"VE": +junction_roll, "VH": -junction_roll}

valve_y_extent = row_half + cell.valve.body_radius  # outer body edge of the butted pair
plate_half_y = valve_y_extent + wall_clear + wall_thickness

valve_pad = corner_pos + socket_radius + margin  # plate reach beyond a valve center in X
plate_half_x = valve_x + valve_pad

# Connector groove: a Tee's run/collet outer radius plus clearance, the
# trough the fitting sets into at port height (port_z).
tee_radius = 6.86            # Tee run/collet outer radius (body 13.72 wide)
groove_clearance = 0.25
tee_groove_radius = tee_radius + groove_clearance


def _box(x0, x1, y_half, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, 2 * y_half, z1 - z0, centered=(True, True, False))
        .translate(((x0 + x1) / 2.0, 0.0, z0))
    )


def _cut_cradles(tray, valve_centers, connectors):
    """Cut a four-socket cradle and a port saddle per valve, plus a groove per
    connector, into ``tray``."""
    for vx, vy in valve_centers:
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                tray = tray.cut(
                    cq.Workplane("XY")
                    .workplane(offset=socket_floor_z)
                    .center(vx + sx * corner_pos, vy + sy * corner_pos)
                    .circle(socket_radius)
                    .extrude(top_z - socket_floor_z + 1.0)
                )
        port = cq.Solid.makeCylinder(
            saddle_radius,
            2.0 * port_half,
            cq.Vector(vx - port_half, vy, port_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=port))

    for cx, cy, length, radius in connectors:
        groove = cq.Solid.makeCylinder(
            radius,
            length,
            cq.Vector(cx - length / 2.0, cy, port_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
        tray = tray.cut(cq.Workplane(obj=groove))
    return tray


def _wall_span(valve_centers, plate_x, half_x):
    """The X span of a ±Y stacking wall in one height band: ``half_x`` beyond the
    outermost valve centers, clamped to the plate — the wall ends at the valves,
    never past them."""
    xs = [cx for cx, _cy in valve_centers]
    return (max(plate_x[0], min(xs) - half_x),
            min(plate_x[1], max(xs) + half_x))


def _stacking_wall(valve_centers, plate_x, y_half, wall_top=None):
    """A ±Y stacking wall as two stacked slabs, stepped where the valve narrows:
    up to the body top it spans the valve bodies, above it retreats to the coils.
    Built centered on Y = 0 for the caller to translate onto its side. `wall_top`
    defaults to the stacked height (`wall_top_z`); a tray that seats nothing passes
    `valve_coil_top_z` and its wall ends level with the coil."""
    return _box(*_wall_span(valve_centers, plate_x, valve_body_half_x),
                y_half, bot_z, valve_body_top_z).union(
        _box(*_wall_span(valve_centers, plate_x, valve_coil_half_x),
             y_half, valve_body_top_z, wall_top_z if wall_top is None else wall_top))


def build_tray(valve_centers, connectors, plate_x, plate_y_half, wall_top=None):
    """Solid frame plate spanning ``plate_x`` (lo, hi), with a four-socket
    cradle and port saddle per valve, a groove per connector, and two ±Y
    stacking walls. The walls step with the valves' own X footprint
    (`_stacking_wall`), sitting flush with the body low down and with the motor
    body above it rather than protruding past either. `wall_top` overrides how
    high the coil-band slab runs — see `_stacking_wall`."""
    tray = _box(plate_x[0], plate_x[1], plate_y_half, bot_z, top_z)
    tray = _cut_cradles(tray, valve_centers, connectors)
    for sy in (+1.0, -1.0):
        wall = _stacking_wall(valve_centers, plate_x, wall_thickness / 2.0, wall_top)
        tray = tray.union(wall.translate((0.0, sy * (plate_y_half - wall_thickness / 2.0), 0.0)))
    return tray


def tee_grooves(tee_centers):
    """Connector grooves (cx, cy, length, radius) for Tee centers; each Tee run
    lies along X, so its groove is a cylinder of one run length."""
    return [(cx, cy, 2.0 * tee_run_half, tee_groove_radius) for cx, cy in tee_centers]


# --- Bag-circuit dog-bone: the tray pinches in the center -----------------
# Full-width floor + full-height walls hug the two valve columns; a narrow
# central bridge hugs the two Tees between them with short walls that just clear
# the Tee runs, joined to the columns by short connecting walls.
bc_x_split = valve_x - valve_pad                       # column/bridge boundary (inner-socket support)
bc_hug_half_y = row_half + tee_groove_radius + wall_clear + wall_thickness  # bridge half-width
bc_hug_wall_top_z = port_z + tee_radius + 2.0          # short central walls just clear the Tee runs
bc_col_inner = bc_x_split - margin                     # columns reach inboard, under the connecting walls
bc_col_outer = valve_x + valve_body_half_x             # column walls end flush with the valve bodies (not the plate edge)
bc_col_outer_coil = valve_x + valve_coil_half_x        # and step back to the motor bodies above them


def build_bag_circuit_tray():
    tray = _box(-bc_x_split, bc_x_split, bc_hug_half_y, bot_z, top_z)                 # central Tee bridge
    tray = tray.union(_box(bc_col_inner, plate_half_x, plate_half_y, bot_z, top_z))   # +X valve column
    tray = tray.union(_box(-plate_half_x, -bc_col_inner, plate_half_y, bot_z, top_z)) # −X valve column
    tray = _cut_cradles(tray, list(valves.values()), tee_grooves(tees.values()))

    for sy in (+1.0, -1.0):
        y_col = sy * (plate_half_y - wall_thickness / 2.0)
        y_hug = sy * (bc_hug_half_y - wall_thickness / 2.0)
        # full-height column walls (carry the stack pitch) + short central wall.
        # The columns end flush with the outer valves, not at the plate edge, so no
        # wall protrudes past the valves into the junction pocket — at the valve
        # bodies below (bc_col_outer) and at the motor bodies above
        # (bc_col_outer_coil), stepping where the valve itself narrows. Their inner
        # ends run under the connecting walls, the tray's own spine.
        for sx in (+1.0, -1.0):
            lo, hi = sorted((sx * bc_col_inner, sx * bc_col_outer))
            tray = tray.union(_box(lo, hi, wall_thickness / 2.0, bot_z, valve_body_top_z).translate((0.0, y_col, 0.0)))
            lo, hi = sorted((sx * bc_col_inner, sx * bc_col_outer_coil))
            tray = tray.union(_box(lo, hi, wall_thickness / 2.0, valve_body_top_z, wall_top_z).translate((0.0, y_col, 0.0)))
        tray = tray.union(_box(-bc_x_split, bc_x_split, wall_thickness / 2.0, bot_z, bc_hug_wall_top_z).translate((0.0, y_hug, 0.0)))
        # connecting walls bridge the pinch from each short-wall end to its column wall
        for sx in (+1.0, -1.0):
            x0, x1 = sorted((sx * bc_col_inner, sx * bc_x_split))
            y0, y1 = sorted((sy * (bc_hug_half_y - wall_thickness), sy * plate_half_y))
            tray = tray.union(
                cq.Workplane("XY")
                .box(x1 - x0, y1 - y0, bc_hug_wall_top_z - bot_z, centered=(False, False, False))
                .translate((x0, y0, bot_z))
            )

    # A Tee rolled to leave SIDEWAYS runs along ±Y at port_z and must cross its
    # hug wall: cut a notch so the branch clears the central floor and passes
    # through. The bottom half arcs around the branch (a Y-cylinder matching the
    # tube); the top half is a straight slot, open through the wall top so the
    # fitting drops in. A Tee rolled to leave upward instead (Y-H, aimed down the
    # enclosure's fall) rises off the ports in open air and stops short of the wall
    # — it needs no notch, and cutting one would only open the wall for nothing.
    z_top = bc_hug_wall_top_z + 1.0
    for nm, (cx, cy) in tees.items():
        sy = 1.0 if cy >= 0 else -1.0
        reach_y = cy + tee_branch_reach * branch_dir(branch_rolls[nm])[1]
        if abs(reach_y) < bc_hug_half_y - wall_thickness:
            continue                       # the branch stops short of the wall
        y0, y1 = sorted((cy, sy * (bc_hug_half_y + 2.0)))
        bore = cq.Solid.makeCylinder(
            tee_groove_radius, y1 - y0,
            cq.Vector(cx, y0, port_z), cq.Vector(0.0, 1.0, 0.0),
        )
        top = (
            cq.Workplane("XY")
            .box(2.0 * tee_groove_radius, y1 - y0, z_top - port_z, centered=(True, False, False))
            .translate((cx, y0, port_z))
        )
        tray = tray.cut(cq.Workplane(obj=bore)).cut(top)
    return tray


def main():
    export_step(build_bag_circuit_tray(), str(_here.parent / "bag-circuit-tray.step"))
    print("-> bag-circuit-tray.step")
    substitute_py_comments(
        _here,
        variables={
            "JUNCTION_OFFSET": f"{junction_offset:.4g}",
            "VALVE_BODY_HALF_X": f"{valve_body_half_x:.4g}",
            "VALVE_COIL_HALF_X": f"{valve_coil_half_x:.4g}",
            "VALVE_BODY_TOP_Z": f"{valve_body_top_z:.4g}",
        },
        expected_counts={
            "JUNCTION_OFFSET": 1,
            "VALVE_BODY_HALF_X": 1,
            "VALVE_COIL_HALF_X": 1,
            "VALVE_BODY_TOP_Z": 1,
        },
    )
    print(f"-> {_here.name} (self)")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "VALVE_X": f"{valve_x:.4g}",
            "PORT_Z": f"{port_z:.4g}",
            "TRAY_BOT_Z": f"{bot_z:.4g}",
            "TRAY_TOP_Z": f"{top_z:.4g}",
            "BAG_PLATE_W": f"{2 * plate_half_x:.0f}",
            "BAG_PLATE_D": f"{2 * plate_half_y:.0f}",
            "STACK_PITCH": f"{stack_pitch:.4g}",
            "WALL_TOP_Z": f"{wall_top_z:.4g}",
        },
        expected_counts={
            "VALVE_X": 1, "PORT_Z": 1, "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 1,
            "BAG_PLATE_W": 1, "BAG_PLATE_D": 1, "STACK_PITCH": 2, "WALL_TOP_Z": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
