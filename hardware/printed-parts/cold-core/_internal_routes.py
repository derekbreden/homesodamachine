"""The lines INSIDE the cold core, drawn.

Seven conduits stand on the top cap and two cables leave by the front field; this
module is the other half of each of those — the run from the fitting a line lands on
to the mouth it leaves by, as a swept ⌀[6.35](LLDPE_TUBE_OD) solid on the tube's own
centreline. The shell is a set of voids and a line is a void's occupant, so nothing
about a route shows up in a bounding box and nothing about it collides with anything:
the only way to know a line fits is to draw it and measure it, which is what
`report_routes` does at every foam-assembly build.

WHERE EACH LINE GOES, and what it does at the end of it:

  water-in         down the forward strip, along the +Y band and in at the carbonator's
                   TOP plate — above the water line, where the pump pushes filtered tap
                   water in against the CO2 back-pressure and it falls into the headspace.
  carb-water-out   the carbonator's BOTTOM plate, under the liquid: the vessel's own
                   drain. Out through a slot in the support ring, up beside the coil, and
                   onto the port lane only once the tank's top plate is under it.
  co2-in           the one line that runs DOWN. The port lane the shell's whole height,
                   one corner in the open at the bottom, and straight in along the leaning
                   bore through the ring — then inside the vessel to the sparge stone
                   hanging in the water column, so the gas enters BELOW the liquid and
                   dissolves on the way up.
  reservoir-a      each reservoir's floor bulkhead, at the bottom of the wet V and the
  reservoir-b      lowest drainable point in it. Out of the pocket at the bulkhead band,
                   about into its own ±Y band, and up the forward strip.
  reservoir-a-fill onto the bore in that reservoir's own cap, opening into the HEADSPACE
  reservoir-b-fill above the liquid. Face to face with the conduit over it, so these two
                   have no run in the shell at all — they are the gap between two bores.

Every vessel here is filled high and drawn low. Nothing that enters can leave without
crossing the vessel, which is what the air-purge and clean-flush service modes run on.

THE BANDS ARE STACKED IN Z, not in Y. The port lane is one bore wide, so two lines that
want it at the same height cannot pass: what separates them is the storey each takes.
Reservoir A's draw has the lane's own floor at the bulkhead band, under everything;
the CO2 falls to the plate band above it and turns in; the carbonated water does not
join the lane until it is over the tank. `report_routes` is what proves those three
never meet.

WHAT A CORNER TURNS AT IS NOT CHOSEN HERE — it is what the corridor leaves, and
`fit_route` is how the corridor states it: each line is drawn at the stock arc and
stepped down until it stops meeting anything. The reading that comes back is the
measurement, and the whole reason to draw these at all. The corners that pay most are
the ones where a line comes out of a bore and has to be turned before it reaches the
next wall — a reservoir draw crossing its pocket into a ±Y band whose outboard half the
attachment bosses have, and the carbonated water stepping over the CO2 under the bottom
plate. Both are potted where they turn, and both are printed every build.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

from _cold_core_interface import (
    bulkhead_elbow_exit_z,
    cap_conduit_shell_xy,
    co2_inlet_y,
    foam_shell_outer_height,
    hole_shift_from_edge,
    lldpe_bend_radius,
    lldpe_tube_od,
    port_lane_mid_y,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    tank_coil_envelope_radius,
    tank_support_ring_height,
    tank_top_plate_z,
    vessel_port_offset,
    wall_and_floor_thickness,
    west_lane_mid_y,
)
from _port_cuts import (
    co2_inlet_lane_xyz,
    co2_inlet_xyz,
    flavor_line_hole_x,
    front_face_port_z,
    water_outlet_ring_crossing_x,
)

sys.path.insert(0, str(Path(__file__).resolve().parent / "reservoir"))
import reservoir as _reservoir  # noqa: E402


line_radius = lldpe_tube_od / 2.0
# Foam a potted line wants around it before anything else stands there. It is not a
# printed wall — nothing here is printed — it is how close a laid tube may run to the
# next solid and still have the pour reach between them.
line_hug = 2.0

# THE ARC EVERY CORNER IN HERE IS DRAWN TO — the machine's own `_routing.BEND_RATIO` × the
# tube, which is what every run outside the core is drawn to as well, so a line does not
# change what it can do at the shell wall. `lldpe_bend_radius` is the cold core's own
# statement about the corner a POTTED line holds once the foam is round it; a corner that
# comes in under it is named in `report_routes` and paid for in the band that made it.
routing_bend_ratio = 2.0
route_bend_radius = routing_bend_ratio * lldpe_tube_od

# --- The storeys ------------------------------------------------------------
#
# Four heights carry everything, and which one a line is on is most of where it is.
pocket_storey_z = bulkhead_elbow_exit_z                       # both reservoirs' floor bulkheads
plate_storey_z = front_face_port_z                            # both bottom-plate elbows
top_band_z = tank_top_plate_z + hole_shift_from_edge          # both top-plate elbows
shell_top_z = foam_shell_outer_height                         # where a riser meets its conduit

# A fifth, and the only one that exists because two lines want the same place. Both
# bottom-plate lines leave their elbows on `plate_storey_z`, and both have to get out of
# the under-tank space on the −Y side: the CO2's leaning bore sweeps that whole quadrant,
# so the carbonated water crosses OVER it, one tube and one hug clear. The step is taken
# under the plate, which is `tank_envelope_z_range[0]` overhead and leaves room for it.
crossing_storey_z = plate_storey_z + lldpe_tube_od + line_hug

# The strip every riser to the forward band climbs, read off the conduits that stand over
# it rather than restated: all three are on it, so any one of them names it.
forward_band_x = cap_conduit_shell_xy("water-in")[0]

# The reservoir cap's outer face — what a fill conduit's tube bottoms on. The reservoir
# body's own top with its cap on, which is the part's reading and not a figure here.
reservoir_cap_top_z = _reservoir.outer_z_range[1] + _reservoir.cap_total_height

# The tank + its wrapped coil, as one cylinder: what the carbonated water's riser stands
# off, and the reason it stands where it does.
tank_envelope_z_range = (wall_and_floor_thickness + tank_support_ring_height, tank_top_plate_z)


def coil_standoff_y(x):
    """The −Y a riser at `x` stands on to clear the tank+coil envelope by one `line_hug`.

    A riser between the pockets has the whole −Y foam zone to stand in, from the coil out
    to the shell wall, and only the port lane's own strip is spoken for. This is the
    inboard edge of that zone at one X."""
    reach = tank_coil_envelope_radius ** 2 - x ** 2
    inboard = math.sqrt(reach) if reach > 0.0 else 0.0
    return -(inboard + line_radius + line_hug)


# --- The routes -------------------------------------------------------------
#
# Each is a centreline through the shell's own frame, fitting first, conduit last. A run
# stops at `shell_top_z`, the shell's open top: above that the cap's conduit carries it,
# and the cap is a different part.


def _routes():
    a_bulkhead = (+reservoir_bulkhead_port_x, 0.0, pocket_storey_z)
    b_bulkhead = (-reservoir_bulkhead_port_x, 0.0, pocket_storey_z)
    a_wall_y = reservoir_bulkhead_port_y                    # A crosses the −Y pocket wall
    b_wall_y = -reservoir_bulkhead_port_y                   # B crosses the +Y one
    carb_x = water_outlet_ring_crossing_x
    carb_riser_y = coil_standoff_y(carb_x)
    co2_x, co2_lane_y = cap_conduit_shell_xy("co2-in")
    carb_lane_y = cap_conduit_shell_xy("carb-water-out")[1]
    water_in_y = cap_conduit_shell_xy("water-in")[1]
    a_riser_y = cap_conduit_shell_xy("reservoir-a")[1]
    b_riser_y = cap_conduit_shell_xy("reservoir-b")[1]

    return {
        # The carbonator's top plate, above the liquid. Out of the elbow laterally, out to
        # the +Y band in the fourteen millimetres between that plate and the cap's floor,
        # forward along it, and into the strip.
        "water-in": [
            (0.0, +vessel_port_offset, top_band_z),
            (0.0, west_lane_mid_y, top_band_z),
            (forward_band_x, west_lane_mid_y, top_band_z),
            (forward_band_x, water_in_y, top_band_z),
            (forward_band_x, water_in_y, shell_top_z),
        ],
        # Reservoir B's trough. Its elbow points straight at its wall bore, so the run out
        # of the pocket is one line across the open space under the raised floor.
        "reservoir-b": [
            b_bulkhead,
            (-reservoir_bulkhead_port_x, west_lane_mid_y, pocket_storey_z),
            (forward_band_x, west_lane_mid_y, pocket_storey_z),
            (forward_band_x, b_riser_y, pocket_storey_z),
            (forward_band_x, b_riser_y, shell_top_z),
        ],
        # Reservoir A's trough. Its wall bore steps inboard of the bulkhead axis to leave
        # the outboard slot for the reed cable, so its elbow is clocked off the wall's own
        # normal and the run straightens onto the bore before it reaches it.
        "reservoir-a": [
            a_bulkhead,
            (flavor_line_hole_x, a_wall_y / 2.0, pocket_storey_z),
            (flavor_line_hole_x, port_lane_mid_y, pocket_storey_z),
            (forward_band_x, port_lane_mid_y, pocket_storey_z),
            (forward_band_x, a_riser_y, pocket_storey_z),
            (forward_band_x, a_riser_y, shell_top_z),
        ],
        # The only line that runs down. It falls the whole shell in the port lane and turns
        # ONCE, out in the open at the bottom, straight onto the leaning bore that carries it
        # through the ring to the collet under the bottom plate's lane-side port.
        "co2-in": [
            (co2_x, co2_lane_y, shell_top_z),
            co2_inlet_lane_xyz,
            co2_inlet_xyz,
        ],
        # The carbonator's bottom plate, under the liquid. Its elbow is clocked −X, out to
        # its own column on the +Y side of the plate's axis where the CO2 never reaches;
        # then it steps UP a storey, because the only way out of the under-tank space on
        # this side crosses the CO2's own run and one of them has to go over. It leaves
        # through the ring's slot at that height and climbs beside the coil — clear of the
        # lane, which the CO2 owns down there — until the top plate is under it.
        "carb-water-out": [
            (0.0, +vessel_port_offset, plate_storey_z),
            (carb_x, +vessel_port_offset, plate_storey_z),
            (carb_x, +vessel_port_offset, crossing_storey_z),
            (carb_x, carb_riser_y, crossing_storey_z),
            (carb_x, carb_riser_y, top_band_z),
            (carb_x, carb_lane_y, top_band_z),
            (carb_x, carb_lane_y, shell_top_z),
        ],
        # The two fills are the gap between two bores: the cap conduit above and the bore in
        # the reservoir's own cap below, with the pour clearance over the reservoir between
        # them and nothing else to cross.
        "reservoir-a-fill": [
            cap_conduit_shell_xy("reservoir-a-fill") + (reservoir_cap_top_z,),
            cap_conduit_shell_xy("reservoir-a-fill") + (shell_top_z,),
        ],
        "reservoir-b-fill": [
            cap_conduit_shell_xy("reservoir-b-fill") + (reservoir_cap_top_z,),
            cap_conduit_shell_xy("reservoir-b-fill") + (shell_top_z,),
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


# What a corner is allowed to come down to before the line is not a line any more. Below
# this a 1/4" LLDPE tube kinks whatever it is potted in.
bend_floor = 0.5 * lldpe_tube_od
# The ladder a route's arc is tried down, stock first. The first rung that fits is what the
# corridor gives; anything under `route_bend_radius` is a corner the shell charged for.
bend_ladder = (1.0, 0.8, 0.65, 0.5, 0.4, 0.3, 0.25)

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
        if all(tube.intersect(o).Volume() <= touch_volume for o in obstacles.values()):
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
    corner comes to. A line the corridor forces under the stock arc is on the page, with the
    number, rather than found at the bench."""
    print("  internal routes: %d lines, ⌀%.2f, stock arc %.4g mm (%g × OD)"
          % (len(fitted), lldpe_tube_od, route_bend_radius, routing_bend_ratio))
    bad = []
    for name in sorted(fitted):
        bend, tube = fitted[name]
        _v, radius = corner_radii(routes[name], bend)
        corners = [r for r in radius[1:-1] if r > 0.0]
        tightest = min(corners) if corners else float("inf")
        hits = []
        for other, solid in obstacles.items():
            volume = tube.intersect(solid).Volume()
            if volume > touch_volume:
                hits.append("%s by %.2f mm³" % (other, volume))
        print("    %-17s %6.1f mm, %d corners, arc %5.2f mm, tightest %s — %s"
              % (name, route_wire(routes[name], bend).Length(), len(corners), bend,
                 ("%5.2f mm" % tightest) if corners else " none  ",
                 "clear" if not hits else "** " + "; ".join(hits)))
        if hits:
            bad.append("%s meets %s" % (name, "; ".join(hits)))
    names = sorted(fitted)
    crossed = False
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            volume = fitted[a][1].intersect(fitted[b][1]).Volume()
            if volume > touch_volume:
                crossed = True
                bad.append("%s and %s share %.2f mm³ — two tubes in one corridor"
                           % (a, b, volume))
    print("    no line meets another" if not crossed else "    ** LINES CROSS **")
    assert not bad, "internal routes do not fit:\n      " + "\n      ".join(bad)
