"""The lines INSIDE the cold core, drawn.

Nine conduits stand on the top cap — seven fluid lines and both reed cables; this
module is the other half of each of those — the run from the fitting a line lands on
to the mouth it leaves by, as a swept ⌀[6.35](LLDPE_TUBE_OD) solid on the tube's own
centreline. The shell is a set of voids and a line is a void's occupant, so nothing
about a route shows up in a bounding box and nothing about it collides with anything:
the only way to know a line fits is to draw it and measure it, which is what
`report_routes` does at every foam-assembly build.

WHERE EACH LINE GOES, and what it does at the end of it:

  water-in         down the forward strip, along the +Y band and across the carbonator's own
                   top on one diagonal to the carbonator's TOP plate — above the water
                   line, where the pump pushes filtered tap water in against the CO2
                   back-pressure and it falls into the headspace.
  carb-water-out   the carbonator's BOTTOM plate, under the liquid: the carbonator's own
                   drain. Out flat on its own storey and through a slot in the support
                   ring, up beside the coil, and onto the port lane only once the tank's
                   top plate is under it.
  co2-in           the one line that runs DOWN. The port lane's own column the shell's
                   whole height, a leg along its floor, and straight in along the
                   leaning reach that bores the support ring — then inside the carbonator to
                   the sparge stone hanging in the water column, so the gas enters BELOW
                   the liquid and dissolves on the way up.
  reservoir-a      each reservoir's floor bulkhead, at the bottom of the wet V and the
  reservoir-b      lowest drainable point in it. Out of the pocket at the bulkhead band,
                   about into its own ±Y band, and up the forward strip.
  reservoir-a-fill onto the bore in that reservoir's own cap, opening into the HEADSPACE
  reservoir-b-fill above the liquid. Face to face with the conduit over it, so these two
                   have no run in the shell at all — they are the gap between two bores.

The carbonator and both reservoirs are filled high and drawn low. Nothing that enters
one can leave without crossing it, which is what the air-purge and clean-flush service modes run on.

THE BANDS ARE STACKED IN Z, not in Y — AND A RISER IS ON NO BAND. A lane is one bore
wide, so two runs that want it at the same height cannot pass: what separates them is the
storey each takes. On the port lane, reservoir A's draw has the lane's own floor at the
bulkhead band, under everything; the evaporator's inlet copper takes a storey above it;
the carbonated water does not join the lane until it is over the tank. On the west lane,
reservoir B's draw has that same floor, and the PRV vent and the evaporator's outlet
copper take the two storeys over it.
A RISER answers to none of that — it stands in every storey at once, so what keeps it
clear is its X, and one bore of lane holds exactly one riser. EACH LANE CARRIES ONE. The
CO2's fall is the port lane's (`_cold_core_interface.co2_cap_x`), and the evaporator's
outlet copper is the west lane's, which is why the vent crosses the wall UNDER that copper
rather than over it (`copper_plugs.prv_vent_z`). `report_routes` is what proves they never
meet.

WHAT A CORNER TURNS AT IS NOT CHOSEN HERE — it is what the corridor leaves, and
`fit_route` is how the corridor states it: each line is drawn at the stock arc and
stepped down until it stops meeting anything. The reading that comes back is the
measurement, and the whole reason to draw these at all.

TWO THINGS BUY A CORNER, and both are in here. Where a line crosses a wall, the WALL
gives way: its opening is the line's own corridor rather than a circle
(`_port_cuts.cut_line_corridors`), so a draw may come about the moment it is through
instead of holding a bore's length of straight first. Where a line has to reach and rise
at once, it LEANS: one diagonal in place of two square corners on a step's own width,
which is what the carbonated water does under the tank to cross the CO2 and again at the
top to put itself on its conduit's column.

WHAT IS LEFT SHORT is printed by name at every build. `top_band_to_cap` is the band between
the tank's top plate and the cap's floor, and it is narrower than the step `water-in` takes
in to its conduit's station — so that step is not taken in it. `top_band_z` is the TANK's
storey and the tank is what holds a line on it; past the rim the strip under the forward
band stands open to the shell's floor, and `water-in` drops onto `water_in_lane_z` to cross
and spends the height it gains on the lean into the station.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(_here.parent / "reservoir"))
sys.path.insert(0, str(_here.parent / "copper-plugs"))
sys.path.insert(0, str(_here.parent / "prv-shroud"))
sys.path.insert(0, str(_here.parents[2] / "scripts"))

from _cold_core_interface import (  # noqa: E402
    bulkhead_elbow_exit_z,
    cap_conduit_shell_xy,
    co2_inlet_y,
    foam_shell_outer_height,
    hole_shift_from_edge,
    lldpe_bend_radius,
    lldpe_tube_od,
    port_hole_radius,
    outer_shell_y_length,
    port_lane_mid_y,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    tank_coil_envelope_radius,
    tank_support_ring_height,
    tank_top_plate_z,
    carbonator_port_offset,
    wall_and_floor_thickness,
    west_lane_mid_y,
)
from _foam_cap import cap_face_z  # noqa: E402
from _port_cuts import (  # noqa: E402
    co2_inlet_lane_xyz,
    co2_inlet_xyz,
    flavor_line_hole_x,
    front_face_port_z,
    water_outlet_ring_crossing_x,
)
import reservoir as _reservoir  # noqa: E402
import prv_shroud as _shroud  # noqa: E402
from _routing import stock_min, stock_of  # noqa: E402
import _overlap  # noqa: E402


line_radius = lldpe_tube_od / 2.0
# Foam a potted line wants around it before anything else stands there. It is not a
# printed wall — nothing here is printed — it is how close a laid tube may run to the
# next solid and still have the pour reach between them.
line_hug = 2.0

# THE ARC EVERY CORNER IN HERE IS DRAWN TO — the stock's own floor, read off the machine's
# STOCKS table rather than restated, so a line does not change what it can do at the shell
# wall and the bench test behind that figure answers for the core too. `lldpe_bend_radius`
# is the cold core's separate statement about a corner a POTTED line holds once the foam is
# round it; a corner under the stock floor is named in `report_routes` and paid for in the
# band that made it.
route_bend_radius = stock_min("fluid", lldpe_tube_od)
route_stock = stock_of("fluid", lldpe_tube_od)

# --- The storeys ------------------------------------------------------------
#
# Four heights carry everything, and which one a line is on is most of where it is.
pocket_storey_z = bulkhead_elbow_exit_z                       # both reservoirs' floor bulkheads
plate_storey_z = front_face_port_z                            # both bottom-plate elbows
top_band_z = tank_top_plate_z + hole_shift_from_edge          # both top-plate elbows
shell_top_z = foam_shell_outer_height                         # where a riser enters its conduit
conduit_mouth_z = cap_face_z                                  # and where it comes back out

# WHERE A RISER JOINS A LANE, and what it holds under the shell's top when it gets there.
# The last leg of every riser is on its conduit's own axis, because the bore through the cap
# is, and one stock arc of it is what the corner at the bottom of that leg takes. So a line
# still stepping sideways at the top has that arc to finish in and no more — the arc is fenced
# by the SHELL's top and not by the conduit's mouth, because what is over the shell is a ⌀6.5
# bore and a tube inside it is straight or it is not in it.
lane_step_top_z = shell_top_z - route_bend_radius

# The strip every riser to the forward band climbs, read off the conduits that stand over
# it rather than restated: all three are on it, so any one of them names it.
forward_band_x = cap_conduit_shell_xy("water-in")[0]

# The storey `water-in` crosses to the forward band on, under the tank's own. It drops onto
# this on the lane leg, once the diagonal off the top plate is past the tank's rim — the
# evaporator's outlet copper is the west lane's occupant under it, at z 169.6 and below.
water_in_lane_z = 180.0

# How much of its rise `water-in` takes on the step in to its own conduit's station. What is
# left above the step is the straight the bore is entered on. `report_routes` prints the arc
# each line comes back at.
water_in_step_climb = 25.0

# The reservoir cap's outer face — what a fill conduit's tube bottoms on. The reservoir body's
# own top with its cap on, which is the part's reading and not a figure here: `cap_assembly_lift`
# is where `reservoir.py` says its cap-local zero lands, and it stands one TPU GASKET over the
# body's rim rather than on it. The rod is cut to the register that lift leaves.
reservoir_cap_z = _reservoir.cap_assembly_lift
reservoir_cap_top_z = reservoir_cap_z + _reservoir.cap_total_height

# THE PRV'S RELIEF, and the only line that leaves this core by a FLANK. `prv-shroud` caps the
# SV-125 for the pour and vents through its BARREL's underside, so what leaves the shroud is
# already pointing down and takes no corner to start (`prv-shroud/prv_shroud.py` says why the
# cap cannot send one). The bore stands on the west lane's own y by the station it is bored at,
# so the line falls that lane, turns once, and goes straight out the +Y wall.
#
# WHY THIS ONE DOES NOT LEAVE BY THE LID. The core is reached through its lid because nothing
# potted in it can ever be reached again — every other run here ends on a fitting the machine
# makes up, the seven on the cap deck and the two coppers on the refrigeration base's own picks.
# A relief vent has no far fitting: it terminates open, and what it owes is the shortest path to
# air outside the cabinet. THE TUBE IS THE THROTTLE IN A RELIEF PATH: the SV-125's rated
# discharge is about what a bare 1/4" orifice passes at its set pressure, so every diameter of
# tube after the bore is friction taken straight off that number. This line is drawn the short
# way out, and the appliance's own chase carries the discharge down the OUTSIDE of the west wall
# — where length costs nothing, because the chase runs several times the tube's bore in section.
prv_vent_lane_y = west_lane_mid_y
prv_vent_start = (0.0, prv_vent_lane_y,
                  tank_top_plate_z + hole_shift_from_edge - _shroud.outer_diameter / 2.0)
prv_vent_flank_y = outer_shell_y_length / 2.0     # the +Y outer face, where it leaves

# WHAT FIXES THE TWO ENDS IS THE ONE CORNER BETWEEN THEM, so neither is a chosen height.
# A square corner sets back one radius on each of its legs. The OUT leg has the lane-to-wall
# standoff to spend and that is under the stock arc on its own, so it runs past the flank to
# finish it; the FALL leg has to find the whole setback in the drop from the bore, and
# nothing above it can be traded — the bore is one shroud radius under the top plate's band and
# the shell's top is over that. So the fall is the arc plus a margin, and the crossing is
# wherever that lands. Move the arc, the shroud or the plate and the station follows.
prv_vent_fall_margin = 2.0
prv_vent_cross_z = prv_vent_start[2] - (route_bend_radius + prv_vent_fall_margin)
# How far the OUT LEG runs past the flank: what it is short of the stock arc by, and a
# millimetre more so the corner is clear of the skin's own corridor. THE TUBE IS CUT FLUSH WITH
# THE FLANK, and the appliance's chase lands the lip of its mouth on that same plane
# (`enclosure._vent_chase`).
prv_vent_reach = route_bend_radius - (prv_vent_flank_y - prv_vent_lane_y) + 1.0

# WHERE THE WATER INLET CROSSES THE VESSEL'S OWN TOP. Its port is the top plate's −Y hole and
# its conduit stands over the +Y band, so the line has to cross the axis somewhere in the band
# between that plate and the cap's floor — where the tank has already ended and the space is
# open. It crosses on ONE DIAGONAL from the port to the west lane, which is also what clocks
# the elbow: a line leaving on the diagonal's own axis needs no corner to start it, and the
# straight it gives the collet is the whole 105 mm reach instead of a leg out of a corner.
#   The column it lands on is the balance of two bodies. Inboard, the PRV STACK stands on the
# +Y port — elbow, valve and a ⌀23 cup along the axis — and the water inlet's own collet swings
# past the PRV's elbow as the diagonal steepens. Outboard, RESERVOIR B's pocket wall closes in.
# Measured on the placed solids over landing columns 44..49: the collet's gap to the PRV elbow
# runs 0.46 → 2.07 mm and the diagonal's gap to the shell runs 1.83 → 0.84 mm, and they cross
# here, at 1.44 and 1.49 mm. Under 37 the diagonal meets the PRV stack; past 48.5 it meets the
# pocket wall, which gives way to a corridor and would open a hole into the pocket.
water_in_cross_x = -47.0

# The tank + its wrapped coil, as one cylinder: what the carbonated water's riser stands
# off, and the reason it stands where it does.
tank_envelope_z_range = (wall_and_floor_thickness + tank_support_ring_height, tank_top_plate_z)


def coil_standoff_y(x):
    """The −Y a riser at `x` stands on to clear the tank+coil envelope by one `line_hug`.

    A riser between the pockets has the whole −Y foam zone to stand in, from the coil out
    to the shell wall, and only the port lane's own strip is spoken for. This is the
    inboard edge of that zone at one X — and the clearance is RADIAL, because the envelope
    is a cylinder: what a riser stands off is the surface on its own azimuth, not the point
    level with it in Y."""
    clear = tank_coil_envelope_radius + line_radius + line_hug
    reach = clear ** 2 - x ** 2
    return -math.sqrt(reach) if reach > 0.0 else 0.0


def co2_run_y(x):
    """The Y the CO2's reach in stands at, at one X — `None` at an X its lean never reaches.

    It leans across the shell's floor from the port lane to the carbonator's own port, so where
    a line crossing its column meets it is a reading off that lean and not the plate's
    axis. A column OUTSIDE that lean's own span does not cross it at all, and `None` is
    that: the lean runs the +X half (`_cold_core_interface.co2_lane_x`) and stops on the
    carbonator's axis, so nothing standing further out has it to clear."""
    (x0, y0, _z0), (x1, y1, _z1) = co2_inlet_lane_xyz, co2_inlet_xyz
    if not min(x0, x1) - 1e-9 <= x <= max(x0, x1) + 1e-9:
        return None
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


# --- The routes -------------------------------------------------------------
#
# Each is a centreline through the shell's own frame, fitting first, conduit last. A run ends at
# `conduit_mouth_z`, the cap face — one length of tube from the fitting it is made up on, up its
# lane, through the cap's own bore, and out. That is the plane the machine's run to the same
# conduit starts on (`enclosure_assembly`'s `foam-assembly.<conduit>` port), so the two are one
# tube end to end with nothing counted twice and nothing left out between them. With the cap off
# the bench it is the 40 mm every line stands proud of the shell.


def _routes():
    a_bulkhead = (+reservoir_bulkhead_port_x, 0.0, pocket_storey_z)
    b_bulkhead = (-reservoir_bulkhead_port_x, 0.0, pocket_storey_z)
    a_wall_y = reservoir_bulkhead_port_y                    # A crosses the −Y pocket wall
    b_wall_y = -reservoir_bulkhead_port_y                   # B crosses the +Y one
    carb_x = water_outlet_ring_crossing_x
    carb_riser_y = coil_standoff_y(carb_x)
    co2_x, co2_lane_y = cap_conduit_shell_xy("co2-in")
    carb_lane_y = cap_conduit_shell_xy("carb-water-out")[1]
    # The carbonated water's LEAN at the top, and the rise it owes anything under the tank.
    #   Under the tank the only run it could meet is the CO2's reach in, and that reach stops
    # on the carbonator's axis — the CO2 falls the lane's +X half, so its lean never comes out as
    # far as this column. `co2_run_y` says so by returning None, and a crossing nobody makes
    # costs no rise: the outlet runs flat on its own storey from the elbow to the coil's
    # standoff and climbs from there. Where the two columns DO meet, the rise is one tube and
    # one hug of clearance at the crossing, opened out over the reach the lean has left.
    co2_under_tank_y = co2_run_y(carb_x)
    carb_co2_rise = 0.0 if co2_under_tank_y is None else (lldpe_tube_od + line_hug) * (
        (carbonator_port_offset - carb_riser_y) / (carbonator_port_offset - co2_under_tank_y))
    #   At the top it steps out onto the lane, and that lean is at 45° — the step outboard
    # and the last of the rise are one move, so two square corners on a step's own width
    # become two shallow ones on a diagonal half again as long. It ends on
    # `lane_step_top_z`, one stock arc under the shell's top.
    carb_lane_step = abs(carb_lane_y - carb_riser_y)
    #   THAT STEP CARRIES THE RUN BETWEEN TWO COLUMNS, because the climb cannot. The crossing
    # below answers to the support ring's own slot and the cap bore to the deck above, so the
    # two are not one column — but the climb between them is pinned by the annulus it rises in,
    # between the wrapped coil and a reservoir pocket's centreward arc, and a lean of even a
    # few millimetres puts it in the pocket. The step is already leaving that annulus for the
    # lane, so it takes the X with it and costs no corner: the run keeps the four points it
    # always had, and the crossing stays square on `water_outlet_climb_x`.
    carb_cap_x = cap_conduit_shell_xy("carb-water-out")[0]
    water_in_y = cap_conduit_shell_xy("water-in")[1]
    a_riser_y = cap_conduit_shell_xy("reservoir-a")[1]
    b_riser_y = cap_conduit_shell_xy("reservoir-b")[1]

    return {
        # The carbonator's top plate, above the liquid. Out of the elbow on one diagonal that
        # crosses the carbonator's own top to the +Y band — the tank has ended by this height, so
        # the crossing costs nothing but the room between the PRV stack and reservoir B's
        # pocket (`water_in_cross_x`) — then forward along that band and in to the strip.
        #   IT LEAVES THE TANK'S OWN STOREY ON THE LANE LEG. `top_band_z` is struck off the top
        # plate and the tank is what holds a line up on it; past the rim the strip is open to
        # the shell's floor, so the lane leg falls to `water_in_lane_z` as it runs forward.
        #   THE STEP AT THE END CLIMBS WHILE IT STEPS. It travels outboard of both pockets —
        # the reservoirs and their caps fill them to within a pour clearance of the cap's floor
        # — and arrives on its conduit's own station, which stands inboard of that. The step
        # carries `water_in_step_climb` of the rise with it, so it reaches the station on a Y-Z
        # diagonal and the corner into the mouth turns about forty degrees. What stands above
        # it is the straight the bore is entered on.
        "water-in": [
            (0.0, -carbonator_port_offset, top_band_z),
            (water_in_cross_x, west_lane_mid_y, top_band_z),
            (forward_band_x, west_lane_mid_y, water_in_lane_z),
            (forward_band_x, water_in_y, water_in_lane_z + water_in_step_climb),
            (forward_band_x, water_in_y, conduit_mouth_z),
        ],
        # Reservoir B's trough. Its elbow points straight at its wall bore, so the run out
        # of the pocket is one line across the open space under the raised floor.
        "reservoir-b": [
            b_bulkhead,
            (-reservoir_bulkhead_port_x, b_wall_y, pocket_storey_z),        # the pocket-wall bore
            (-reservoir_bulkhead_port_x, west_lane_mid_y, pocket_storey_z),
            (forward_band_x, west_lane_mid_y, pocket_storey_z),
            (forward_band_x, b_riser_y, pocket_storey_z),
            (forward_band_x, b_riser_y, conduit_mouth_z),
        ],
        # Reservoir A's trough. Its wall bore steps inboard of the bulkhead axis to leave
        # the outboard slot for the reed cable, so its elbow is clocked off the wall's own
        # normal and the run straightens onto the bore before it reaches it.
        "reservoir-a": [
            a_bulkhead,
            (flavor_line_hole_x, a_wall_y / 2.0, pocket_storey_z),   # straight by mid-floor
            (flavor_line_hole_x, port_lane_mid_y, pocket_storey_z),  # out through the bore
            (forward_band_x, port_lane_mid_y, pocket_storey_z),
            (forward_band_x, a_riser_y, pocket_storey_z),
            (forward_band_x, a_riser_y, conduit_mouth_z),
        ],
        # The only line that runs down, and the only riser the port lane carries. It falls the
        # whole shell on the CAP CONDUIT's column, runs the lane's floor to the column the
        # support ring leaves it, and only there leans in to the collet under the bottom
        # plate's lane-side port. The fall and the lean stand apart because the ring is at the
        # floor and the conduit is in the cap: the run turns on that floor either way, so the
        # floor leg buys the conduit its own column for the price of a turn already spent.
        "co2-in": [
            (co2_x, co2_lane_y, conduit_mouth_z),
        ] + ([(co2_x, co2_lane_y, co2_inlet_lane_xyz[2])]
             if abs(co2_x - co2_inlet_lane_xyz[0]) > 1e-9 else []) + [
            co2_inlet_lane_xyz,
            co2_inlet_xyz,
        ],
        # The carbonator's bottom plate, under the liquid. Its elbow is clocked −X, out to
        # its own column on the +Y side of the plate's axis; then straight out to the coil's
        # standoff on that same storey, because the CO2's reach in stops on the carbonator's axis
        # and there is nothing under the tank on this column to go over (`carb_co2_rise`). It
        # leaves through the ring's own slot on that leg and climbs beside the coil — clear of
        # the lane, which the copper owns down there — and leans at the top to put itself on
        # the conduit's own column for the last stock arc.
        "carb-water-out": [
            (0.0, +carbonator_port_offset, plate_storey_z),
            (carb_x, +carbonator_port_offset, plate_storey_z),
            (carb_x, carb_riser_y, plate_storey_z + carb_co2_rise),
            (carb_x, carb_riser_y, lane_step_top_z - carb_lane_step),
            (carb_cap_x, carb_lane_y, lane_step_top_z),
            (carb_cap_x, carb_lane_y, conduit_mouth_z),
        ],
        # The PRV's relief: the only line here that starts on a PRINTED part rather than on a
        # fitting, and the only one that leaves by a FLANK instead of by the lid. Out of the
        # shroud's underside pointing down, one corner, and straight out the +Y wall into the
        # socket the appliance's chase holds across the band. Unpressurized until the valve pops.
        "prv-vent": [
            prv_vent_start,
            (prv_vent_start[0], prv_vent_lane_y, prv_vent_cross_z),
            (prv_vent_start[0], prv_vent_flank_y + prv_vent_reach, prv_vent_cross_z),
        ],
        # The two fills are the gap between two bores: the cap conduit above and the bore in
        # the reservoir's own cap below, with the pour clearance over the reservoir between
        # them and nothing else to cross.
        "reservoir-a-fill": [
            cap_conduit_shell_xy("reservoir-a-fill") + (reservoir_cap_top_z,),
            cap_conduit_shell_xy("reservoir-a-fill") + (conduit_mouth_z,),
        ],
        "reservoir-b-fill": [
            cap_conduit_shell_xy("reservoir-b-fill") + (reservoir_cap_top_z,),
            cap_conduit_shell_xy("reservoir-b-fill") + (conduit_mouth_z,),
        ],
    }


routes = _routes()


# --- Drawing one -------------------------------------------------------------


def _drop_collinear(points):
    """Points with every straight-through vertex removed — three in a line have no corner
    to turn, and a zero-radius arc is not a curve."""
    kept = [cq.Vector(*points[0])]
    for p in points[1:]:
        v = cq.Vector(*p)
        if (v - kept[-1]).Length < 1e-9:
            continue
        if len(kept) >= 2:
            a, b = kept[-2], kept[-1]
            if ((b - a).normalized().cross((v - b).normalized())).Length < 1e-9:
                kept[-1] = v
                continue
        kept.append(v)
    return kept


def corner_radii(points, bend_radius):
    """The radius each interior corner actually turns at.

    Every corner wants `bend_radius`, and what stops one is the leg it shares: two corners
    on a short leg cannot both set back what they want, so the pair gives up the same
    fraction until they fit. A corner that comes back under the stock arc is a corner the
    reach bought with, and `report_routes` is where that shows."""
    v = _drop_collinear(points)
    n = len(v)
    half = [0.0] * n
    for i in range(1, n - 1):
        u = (v[i - 1] - v[i]).normalized()
        w = (v[i + 1] - v[i]).normalized()
        half[i] = math.acos(max(-1.0, min(1.0, u.dot(w)))) / 2.0
    radius = [0.0] * n
    for i in range(1, n - 1):
        radius[i] = bend_radius
    for _ in range(64):
        setback = [radius[i] / math.tan(half[i]) if half[i] > 1e-9 else 0.0 for i in range(n)]
        worst = 1.0
        for i in range(n - 1):
            leg = (v[i + 1] - v[i]).Length
            want = setback[i] + setback[i + 1]
            if want > leg:
                worst = min(worst, leg / want)
        if worst >= 1.0 - 1e-12:
            break
        for i in range(1, n - 1):
            radius[i] *= worst * 0.999      # a hair, so two arcs never meet on a point
    return v, radius


def route_legs(points, bend_radius=route_bend_radius):
    """One line's STRAIGHTS, the corners taken out: `(start, end)` in order.

    A fitting made up on a port takes the tube on the port's own axis, so what it needs is
    a straight to receive it, and how much straight there is is what the corners either end
    of it leave."""
    v, radius = corner_radii(points, bend_radius)
    legs = []
    tail = v[0]
    for i in range(1, len(v) - 1):
        u = (v[i - 1] - v[i]).normalized()
        w = (v[i + 1] - v[i]).normalized()
        half = math.acos(max(-1.0, min(1.0, u.dot(w)))) / 2.0
        setback = radius[i] / math.tan(half)
        head = v[i] + u.multiply(setback)
        if (head - tail).Length > 1e-7:
            legs.append((tail, head))
        tail = v[i] + w.multiply(setback)
    if (v[-1] - tail).Length > 1e-7:
        legs.append((tail, v[-1]))
    return legs


def route_wire(points, bend_radius=route_bend_radius):
    """The centreline as one wire: straights with an arc at each corner."""
    v, radius = corner_radii(points, bend_radius)
    edges = []
    tail = v[0]
    for i in range(1, len(v) - 1):
        u = (v[i - 1] - v[i]).normalized()
        w = (v[i + 1] - v[i]).normalized()
        half = math.acos(max(-1.0, min(1.0, u.dot(w)))) / 2.0
        setback = radius[i] / math.tan(half)
        p_in = v[i] + u.multiply(setback)
        p_out = v[i] + w.multiply(setback)
        centre = v[i] + (u.normalized() + w.normalized()).normalized().multiply(
            radius[i] / math.sin(half))
        mid = centre + (v[i] - centre).normalized().multiply(radius[i])
        if (p_in - tail).Length > 1e-7:                  # two arcs may meet with no straight
            edges.append(cq.Edge.makeLine(tail, p_in))
        edges.append(cq.Edge.makeThreePointArc(p_in, mid, p_out))
        tail = p_out
    if (v[-1] - tail).Length > 1e-7:
        edges.append(cq.Edge.makeLine(tail, v[-1]))
    return cq.Wire.assembleEdges(edges)


def build_route(points, bend_radius=route_bend_radius, radius=line_radius):
    """One line as a solid — the tube, not the centreline."""
    wire = route_wire(points, bend_radius)
    profile = cq.Workplane(cq.Plane(origin=wire.startPoint(), normal=wire.tangentAt(0)))
    return profile.circle(radius).sweep(
        cq.Workplane("XY").newObject([wire]), isFrenet=True).val()


def route_corridor(name, radius=port_hole_radius):
    """One line's OPENING — the same run swept at the ⌀[6.5](PORT_HOLE_DIAMETER) shell
    standard instead of at the tube's OD, which is what a wall the line crosses has to
    leave for it. Given a bigger `radius` it is the opening grown, which is how the land
    between this opening and its neighbour in the same wall gets priced.

    A wall here is two millimetres of PETG, and a hole in a sheet that thin is whatever
    shape goes through it. Cut as the corridor rather than as a circle, a line may turn AT
    the wall instead of a bore's length beyond it, and the tube still crosses on the same
    ⌀6.5-around-⌀6.35 tight fit that keeps the body pour out of a pocket — the clearance is
    radial to the tube's own path either way.

    Cut at the STOCK arc, not at the fitted one: the opening is made for the corner the
    stock asks for, and a line that still cannot turn there is one something else charges,
    which `report_routes` names."""
    return build_route(routes[name], route_bend_radius, radius)


# What a corner is allowed to come down to before the drawing stops meaning anything: half
# the tube's own diameter, where the centreline arc is the tube's own wall.
bend_floor = 0.5 * lldpe_tube_od
# The ladder a route's arc is tried down, stock first, each rung a sixth off the last. The
# first rung that fits is what the corridor gives, to about that resolution; anything under
# `route_bend_radius` is a corner the shell charged for.
bend_ladder = tuple(0.85 ** k for k in range(24))

# A tube and a solid that read as touching. Two surfaces built to the same nominal face
# meet at a sliver of this order, and a real interference is orders above it.
touch_volume = 0.1


def fit_route(points, obstacles):
    """The largest arc off `bend_ladder` at which this line meets nothing, and the line
    drawn to it: `(bend_radius, solid)`.

    A corner is not a choice made here — it is what the corridor leaves. Drawing the line
    at the stock arc and stepping down until it fits is how the corridor states its own
    answer, and the answer is what `report_routes` prints. A line that fits nowhere down
    to `bend_floor` comes back at the floor, still meeting something, and fails there."""
    for rung in bend_ladder:
        bend = route_bend_radius * rung
        if bend < bend_floor:
            break
        tube = build_route(points, bend)
        if all(_overlap.volume(tube, o) <= touch_volume for o in obstacles.values()):
            return bend, tube
    return bend_floor, build_route(points, bend_floor)


def build_routes(obstacles=None):
    """Every line in the pack: name → `(bend_radius, solid)`, each drawn at the arc its own
    corridor leaves. With no obstacles given, every line is drawn at the stock arc."""
    if obstacles is None:
        return {n: (route_bend_radius, build_route(p)) for n, p in routes.items()}
    return {n: fit_route(p, obstacles) for n, p in routes.items()}


# --- Measuring them ----------------------------------------------------------


def tank_envelope():
    """The tank and its wrapped coil as one cylinder — an obstacle, not a part."""
    z0, z1 = tank_envelope_z_range
    return cq.Solid.makeCylinder(tank_coil_envelope_radius, z1 - z0,
                                 cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


def report_routes(fitted, obstacles):
    """Print each line's reading and fail on any that does not fit.

    Three claims. (1) NO LINE MEETS A SOLID: not the shell it runs inside, not a reservoir
    filling a pocket, not the tank. A bore it passes through is a void, so a line that reads
    blocked is a line with no hole in front of it. (2) NO TWO LINES MEET: the bands are one
    bore wide and it is the storeys that keep them apart, so the pack has to be read as a
    pack. (3) EVERY LINE NAMES THE ARC IT TURNS AT, and the corner that arc's tightest
    corner comes to — and the pack's own SHORT LIST is the last line printed, so a corner the
    core forces under the stock arc is on the page, with the number, rather than found at the
    bench."""
    print("  internal routes: %d lines in %s, stock arc %.4g mm — %s"
          % (len(fitted), route_stock.name, route_bend_radius, route_stock.source))
    bad = []
    short = []
    for name in sorted(fitted):
        bend, tube = fitted[name]
        _v, radius = corner_radii(routes[name], bend)
        corners = [r for r in radius[1:-1] if r > 0.0]
        tightest = min(corners) if corners else float("inf")
        hits = []
        for other, solid in obstacles.items():
            volume = _overlap.volume(tube, solid)
            if volume > touch_volume:
                hits.append("%s by %.2f mm³" % (other, volume))
        print("    %-17s %6.1f mm, %d corners, arc %5.2f mm, tightest %s — %s"
              % (name, route_wire(routes[name], bend).Length(), len(corners), bend,
                 ("%5.2f mm" % tightest) if corners else " none  ",
                 "clear" if not hits else "** " + "; ".join(hits)))
        if hits:
            bad.append("%s meets %s" % (name, "; ".join(hits)))
        if corners and tightest < route_bend_radius - 1e-9:
            short.append("%s at %.2f mm" % (name, tightest))
    names = sorted(fitted)
    crossed = False
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            volume = _overlap.volume(fitted[a][1], fitted[b][1])
            if volume > touch_volume:
                crossed = True
                bad.append("%s and %s share %.2f mm³ — two tubes in one corridor"
                           % (a, b, volume))
    print("    no line meets another" if not crossed else "    ** LINES CROSS **")
    print("    every corner at the stock arc" if not short else
          "    under the %.4g mm stock arc: %s" % (route_bend_radius, "; ".join(short)))
    assert not bad, "internal routes do not fit:\n      " + "\n      ".join(bad)
