"""_lines — the runs the box carries, authored port to port.

[`_routing.py`](_routing.py) is the kit; this file is the authorship: one `route(...)` per
connection, its waypoints written against the ports and body faces that shape them.

Today: the sealed refrigerant loop (`scorecard.REFRIGERANT_SEGMENTS`) — the discharge and
liquid legs authored, the suction leg unauthored — the tap-water path's first segment
(`scorecard.WATER_SEGMENTS`), and the manifold's junction column, fully joined: both trays'
west collets into the union tees hanging between them. Seven corridors carry the authored
legs, each measured off the faces that bound it:

  * the machine corridor — compressor back face to cold-core front face — with the
    valve-manifold tray stack in its upper band (z 164.8–296.1). The stack's central span stops
    at y 155.3, so a window stands open off the cold-core face at the evaporator ports; below
    the stack's floor the corridor runs the box's whole width, and refrig-1 and refrig-2 cross
    its east half. The west lane and the floor lane stay open for refrig-3's reach to the
    compressor's suction port.
  * the service bay's aft strip — the SeaFlo's back face to the rear-panel bodies, over the
    foam-cap top — with the ASSE 1022 chain lying along its west half: its 1/4" inlet west off
    the water bulkhead (water-1), its 1/4" outlet east onto the line to the split (water-2). The
    strip's EAST void carries the rest of the water chain in two strata, east of every rear-panel
    body: V-K stands down it with its port plane at the suction's, and the split lies under V-K's
    cradle a stratum below, its branch looking north so water-3 climbs the column between them.
    V-K's outlet then looks south down the LANE the pump's back face and V-K's own leave open
    across the strip, west to the suction's X and into the north-facing barb (water-4). The band
    UNDER the ASSE body stays open the same way: the drip the vent lets go of falls through it.
  * the lane under the pump — the gap the SeaFlo's bracket leaves between its body and the
    foam-cap top, running the bay's whole width and depth and free of everything the deck above
    it is full of. The flavor tap crosses the machine along it: fluid-1 from the split, west out
    from under V-K, south under the pump's head and back onto V-A's own X into the flow regulator
    standing in the band ahead of the cap, and fluid-2 on down into V-A's up-facing collet.
  * the bag-fall corridor — the open Y behind the whole stack, aft face to cold-core front face
    (_contents `BAG_FALL_CORRIDOR`), running the box's full height and width. It is what stands
    the core off the stack, and the only lane that reaches either reservoir port low on that
    face: reservoir-A's sits behind the condenser, which fills the machine corridor's east end
    from the floor to z 154. Both bag lines fall down it as a parallel pair (fluid-15/25) — each
    bag tee rolled to the one `bag_fall_aim`, its branch aimed into the corridor, turning along
    it to its own reservoir's end (bag A east, bag B west) and dropping straight into the port.
  * the band across the middle of the machine — the source-select tray's crown for a floor, the
    pump-discharge dividers' undersides for a ceiling, and on the funnel drain's own y the slot
    between the nozzle-gate tray's front face and pump-b's outlet elbows. The crossing discharge
    runs hang off the dividers that roof it, so it stands clear beneath them. fluid-4 falls into
    it down the spout's axis and runs east along it to V-B-I.
  * the condenser channel — 21 mm, compressor +X face to condenser −X face, one lane wide.
    refrig-1 crosses at the discharge's height and climbs the tipped block's flank to the
    back-top inlet; refrig-2 leaves the front-bottom outlet along the channel floor — the two
    share the lane plane 69 mm apart in z.
  * the junction column — the open air off the trays' west ends, outboard of the west valve
    banks: the source tray's pair pointing up from below, the inverted bag tray's pointing
    down from above, ~60 mm apart, and the pump-inlet union tees (`tee-y-c`, `tee-y-f`)
    hanging between them on the line the collets make. Each elbow is rolled off its port
    axis to aim along that line (bag_circuit_tray `_junction_aim`), which leans ~11.6° off
    Z, so all four legs — fluid-9/19 down from the source, fluid-10/20 up from the bag —
    are straight tube, ~10 mm each, no bends. Each tee's branch is then rolled about the run
    (`JUNCTION_ROLL`) to swing forward off the pump row, and fluid-11/21 carry the suction
    over pump A to the pump inlets.
  * the strip ahead of the cold core's front face, which carries the two lines that face has
    to serve and stacks them by the height of their own ports. The carbonated-water outlet is
    the LOW port and the water inlet is the HIGH one, so the riser owns the strip's bottom and
    water-5 owns its crown, and neither crosses the other. The riser's outlet collet cannot be
    left head-on: refrig-2 climbs the same station to the evaporator inlet above and stands
    9.52 mm off it, so the line turns west inside that gap, then climbs WEST of the bag fall
    and of the shared slot to the DIGITEN meter lying in the strip at the water inlet's height
    — the one band of the strip nothing stands in. From the meter it goes east and then DOWN,
    not over: the pump's crown and the ceiling leave a Ø6.35 centreline needing 328.575 and
    allowed 328.545, so the crossing is the lane under the pump, which the flavor tap already
    uses. It comes up the last stratum in the column EAST of the ASSE, because water-2 runs
    across the carb bulkhead's own southward line 11.04 mm off its collet. water-5 takes the
    crown above all of it: its collet looks down off the bottom of the discharge chain, below
    the port it feeds, so it drops clear, climbs east of the riser's lane, crosses west over
    the riser's turn into the under-pump lane, and falls onto the inlet's own height.
  * the +X wall pocket and the channel inboard of it — the cold core's own standoff off that
    wall, where the two nozzle-outlet elbows stand, and the wide horizontal channel over the
    nozzle gate's spade tabs and the electronics shelf's board, under the hopper funnel's
    basin, which runs unbroken the full depth of the box. It carries fluid-18/28 aft on one deck
    ([292.4](NOZ_DECK_Z)) as far as the pump, and there they CLIMB: the pump fills the deck the
    whole way across, so both cross it on its low end — the pressure switch's crown — and come
    down again in the lane behind it. The pocket is also the Y seam's corner-post lane, so both
    step west out of it before turning aft at all.

Precedent: `pcba.tsx`'s `route(...)` call sites.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(_here.parent))

import _boxes
import _contents as contents
import _routing as R
from _routing import route

# 1/4" ACR copper, drawn as the metal it is.
COPPER = cq.Color(0.72, 0.45, 0.20)
# 1/4" LLDPE, drawn as the soft tube it is.
LLDPE = cq.Color(0.90, 0.90, 0.94)
# How far off a divider/elbow collet's axis a pump-discharge run may enter as one straight length
# of soft LLDPE — the flex a push-to-connect collet takes, past the copper loop's COLLET_SKEW.
# The aimed poses (_contents `_solve_discharge`) leave a few degrees of residual the tube absorbs;
# y-g, boxed in over pump-b, is the tightest at ~9°.
DISCHARGE_SKEW = 22.0

# Connections the pack does not carry as it stands, each with the measurement that blocks it.
# They stay counted against the `routed` axis.
BLOCKED: dict = {}

# neoPure PVCR-0610 3/8" ID polyester-reinforced clear PVC, the only thing that can leave
# the pump's molded barbs. Ø15.1 OD, and it turns at [15.9](HOSE_BEND) mm — the radius is
# the whole reason it can get off the barb at all inside the strip it has.
HOSE_OD = 15.1
HOSE_BEND = 15.9


def _frames():
    """A frame per placed component, per through-wall panel body, and the hopper funnel: its body
    box from the pack, its ports from the scorecard's port table. The panel bodies (the rear
    bulkheads) and the funnel are not interior components, but a run terminates on the bulkheads'
    inward collets and one falls from the funnel's drain, so they carry frames too."""
    import scorecard                                   # deferred: scorecard reads this module back

    placed = {**contents.build(), **contents.panel_bodies(),
              "hopper-funnel": (contents.placed_funnel(), None)}
    by_comp: dict = {}
    for p in scorecard.PORTS:
        if p.pos is not None and p.face and p.component in placed:
            by_comp.setdefault(p.component, {})[p.name] = (p.pos, p.face, p.diam)
    return {n: R.frame(n, placed[n][0], by_comp.get(n, {})) for n in placed}


def _column_aft(solid, x, half_w, z_lo, z_hi) -> float:
    """The aft-most Y a solid reaches inside one fall column — the band `half_w` either side of
    `x`, over the Z the line falls through. A column the solid never enters answers with the
    solid's own front face, which leaves the corridor open."""
    bb = solid.BoundingBox()
    column = cq.Solid.makeBox(
        2.0 * half_w, bb.ylen + 2.0, abs(z_hi - z_lo) + 2.0,
        cq.Vector(x - half_w, bb.ymin - 1.0, min(z_lo, z_hi) - 1.0),
    )
    inside = solid.intersect(column)
    return inside.BoundingBox().ymax if inside.Solids() else bb.ymin


def _deck(x, dy, z) -> tuple:
    """A waypoint over the manifold deck, its depth carried off the stack. `dy` stands the
    waypoint that far forward of `SRC_SEL_POS`, so a run whose two ends both ride the stack
    keeps its shape when the stack moves."""
    return (x, contents.SRC_SEL_POS[1] + dy, z)


_RUNS: list | None = None


def build_runs() -> list:
    """The authored runs. Each waypoint is a port offset, a body face, or a bend-radius reach.

    Memoized for the life of the process. The export, the routed axis, the lines-clear gate and
    the lane stations each ask for the runs; a rebuild is always a fresh process. `_routing`'s
    frame registry is filled by the first call and reads the same afterwards."""
    global _RUNS
    if _RUNS is None:
        _RUNS = _authored_runs()
    return _RUNS


def _authored_runs() -> list:
    import scorecard                                   # deferred: scorecard reads this module back

    f = _frames()
    cond, foam = f["condenser+fan"], f["foam-assembly"]
    bend = R.BEND_RATIO * 6.35                              # 1/4" ACR copper, the loop's line

    # Each lane sits one bend radius off the face its ports turn away from.
    slot = cond.bb.xmin - bend

    runs = []

    # refrig-1 — hot gas off the compressor's back face onto the corridor lane, across to the
    # condenser channel, aft along the tipped block's flank, up into the inlet at the
    # condenser's back-top.
    runs.append(route(
        "refrig-1", "compressor-shroud.refrig-discharge",
        {"x": slot},                                        # across into the condenser channel
        cond.y("refrig-inlet"),                             # aft to the inlet's station
        cond.z("refrig-inlet"),                             # up the channel to its height
        "condenser+fan.refrig-inlet",
        note="hot gas: compressor → condenser"))

    # refrig-2 — liquid line off the tipped condenser's front-bottom outlet (the donor drier +
    # cap tube ride this leg, inside the harvested block): along the channel floor, aft to the
    # corridor's approach lane, across the machine at the floor — 70 mm under refrig-1's channel
    # crossing — then up the cold-core face into the evaporator inlet at its station.
    runs.append(route(
        "refrig-2", "condenser+fan.refrig-outlet",
        foam.y("evap-inlet", -bend),                        # aft: one bend off the cold-core face
        foam.x("evap-inlet"),                               # across the machine at the floor
        foam.z("evap-inlet"),                               # up the cold-core face to the inlet
        "foam-assembly.evap-inlet",
        note="liquid: condenser (drier + cap tube) → evaporator"))

    # water-1 — the tap-water pigtail: the rear bulkhead's inboard collet forward (−Y)
    # to the ASSE inlet's own line, then east into its 1/4" PTC inlet. Straight into
    # the backflow preventer now — V-K has moved downstream of it.
    bfp = f["asse1022-assembly"]
    sp = f["water-split"]
    vk = f["vk-fill-valve"]
    pump = f["seaflo-pump"]
    WBEND = 3.0                              # 1/4" LLDPE, the tight pigtail's radius
    runs.append(route(
        "water-1", "bulkhead-water.tube-in",
        bfp.y("tube-in"),                    # forward (−Y) to the inlet's own line
        "asse1022-assembly.tube-in",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(6.0, 3.0),
        note="tap water: rear bulkhead → ASSE 1022 inlet"))

    # The strip's east void carries the chain in TWO strata: V-K stands down it with its port
    # plane at the suction's, and the split lies under V-K's cradle with its own a stratum below.
    # Every hop between them is a climb or a fall in the open column east of the rear-panel
    # bodies — the one column in the strip with no bulkhead reaching into it.
    runs.append(route(
        "water-2", "asse1022-assembly.tube-out",
        sp.out("supply", 20.0),              # east, clear of the ASSE's own end, into the column
        sp.z("supply"),                      # down the column to the split's own plane, under V-K
        "water-split.supply",                # east into its west-facing run
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, 2.0),
        note="tap water: ASSE 1022 outlet → split run, down the column west of V-K"))

    # water-3 — the split's branch looks north out from under V-K; the line stands off the
    # valve's back face, climbs the stratum between them and turns south into the inlet.
    runs.append(route(
        "water-3", "water-split.to-vk",
        vk.out("inlet", 4.0),                # north, clear of the valve's own back face
        vk.x("inlet"),                       # east onto the valve's own line
        vk.z("inlet"),                       # up the column to the valve's port plane
        "vk-fill-valve.inlet",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, 2.0),
        note="tap water: split branch → V-K inlet, up the strip's east column"))

    # water-4 — V-K looks straight south down the open lane between the pump's back face and
    # its own: the line drops into that lane, runs west to the suction's own X and turns south
    # into the north-facing barb. The 1/4" LLDPE steps up to the pump's 3/8" barb there
    # (adapter in the BOM) — the barbs are molded into the head, so that step is the only 3/8"
    # on this side.
    runs.append(route(
        "water-4", "vk-fill-valve.outlet",
        {"y": (pump.bb.ymax + vk.bb.ymin) / 2.0},   # south into the lane the two faces leave
        pump.x("suction"),                   # west down that lane to the suction's line
        "seaflo-pump.suction",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, 2.0),
        note="tap water: V-K outlet → SeaFlo suction, down the lane behind the pump"))

    # water-6 — the 3/8" stub off the discharge. The pump's barbs are molded into the head,
    # so this hose is the only thing that can leave the port: it runs south off the barb,
    # over the cap's front edge, and turns down into the corridor onto the chain's barb.
    disch = f["discharge-chain"]
    runs.append(route(
        "water-6", "seaflo-pump.discharge",
        disch.y("barb-tip"),                 # south to the corridor's own line
        "discharge-chain.barb-tip",
        kind="water", bend=HOSE_BEND, skew=DISCHARGE_SKEW,
        stub=(HOSE_BEND, HOSE_BEND),
        note="carb water: SeaFlo discharge barb → discharge chain (3/8\" braided PVC)"))

    # water-5 — the 1/4" LLDPE off the chain's collet to the cold core's water inlet on its
    # front face. The collet looks DOWN off the bottom of the chain, 36.8 mm below the port
    # it feeds, so the line drops clear of it before it can turn at all. From there it takes
    # the strip's CROWN: it climbs east of the riser's lane, crosses west above everything
    # the riser owns, and falls onto the inlet's own height. The whole run is above the
    # meter and above the riser's aft turn, so the two lines share the strip without
    # crossing — the water inlet is the high port on this face and this is the high line.
    WATER5_CLIMB_X = 212.0                   # west of the chain's body, east of the riser's lane
    WATER5_CROWN   = 272.0                   # over carb-2's turn into the under-pump lane
    runs.append(route(
        "water-5", "discharge-chain.tube-port",
        disch.z("tube-port", -12.0),         # on down the corridor, under the turn
        {"x": WATER5_CLIMB_X},               # west off the chain's own body
        {"z": WATER5_CROWN},                 # up the strip to its crown
        foam.x("water-in"),                  # west to the port's own line
        foam.z("water-in"),                  # down onto the port's height
        "foam-assembly.water-in",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, WBEND),
        note="carb water: discharge chain → cold-core water inlet, over the riser"))

    # --- CO2: the front-panel inlet to the cold core's bottom-plate port. The
    # GASHER check is made up on the DERPIPE's stub and carries no line, so the
    # path is two runs of 1/4" LLDPE past it, one on each side of the regulator.
    reg110 = f["wr1110"]
    comp = f["compressor-shroud"]
    CBEND = 6.0                              # 1/4" LLDPE, the CO2 line's radius

    # co2-1 — off the check's stub, forward onto the regulator's own line, then
    # east the width of the band into its west-facing inlet. One corner, no
    # climb: the regulator lies in the check's own Z plane.
    runs.append(route(
        "co2-1", "gasher-co2.outlet",
        reg110.y("inlet"),                   # forward onto the regulator's line
        "wr1110.inlet",
        kind="co2", bend=CBEND, stub=(CBEND, CBEND),
        note="CO2: check outlet → WR1110 inlet, across the band"))

    # co2-2 — the regulator's outlet steps east into the slot between the
    # compressor and the condenser, the one column in the front stratum open to
    # the floor, and falls down it to the cold core's port height. From there it
    # runs aft into the machine corridor behind the compressor, west onto the
    # port's own line, and closes north into the core's front face. The corridor
    # crossing is taken in its FRONT half, one leg off the compressor's back
    # face: the two bag lines fall down the corridor's aft half on their own
    # reservoirs' X and turn along the floor there, and the CO2 crossing has to
    # be clear of both before it reaches them.
    runs.append(route(
        "co2-2", "wr1110.outlet",
        foam.z("co2-in"),                    # down the slot to the port's height
        comp.face("y+", 2.0 * CBEND),        # aft into the corridor's front half
        foam.x("co2-in"),                    # west onto the port's own line
        "foam-assembly.co2-in",
        kind="co2", bend=CBEND, stub=(CBEND, CBEND),
        note="CO2: WR1110 outlet → cold-core CO2 inlet, down the inter-block slot"))

    # --- The carbonated-water riser: the cold core's bottom-plate outlet to the rear
    # umbilical, with the DIGITEN turbine meter inline. It is the longest path in the
    # machine and the only one that has to get from the floor at the front to the top of
    # the back wall, and four things bound it, each measured:
    #   * refrig-2 climbs the outlet's own x on its way to the evaporator inlet above and
    #     stands 9.52 mm off the collet, so the line cannot leave this face head-on — it
    #     turns WEST one bend radius off the face, inside that gap.
    #   * the bag fall owns the strip east of the climb: fluid-15 drops it on the
    #     reservoir's own line, so the climb stands WEST of that and of the shared slot.
    #   * over the pump there is no lane at all: the crown is 325.40 and the ceiling
    #     331.72, which leaves a Ø6.35 centreline needing 328.575 and allowed 328.545.
    #     So the crossing goes UNDER, in the lane the pump's bracket leaves over the cap.
    #   * water-2 runs east across the carb bulkhead's own southward line 11.04 mm off its
    #     collet, so the last climb stands in the column EAST of it and comes back west.
    # The riser stops climbing at the meter and hands the strip above it to water-5, whose
    # port is the high one on this face: carb-1 owns the front face below the meter's plane
    # and water-5 crosses at the crown, so the two share the strip without a crossing.
    # The two halves come out at [225.6](CARB_1_LEN) and [309.9](CARB_2_LEN) mm of stock, which
    # is what the shop cuts and what the CARGEN insulation is cut to follow.
    digi, b_carb = f["digiten-flow"], f["bulkhead-carb"]
    RBEND = 4.0                              # 1/4" LLDPE, the riser's radius
    RISER_CLIMB_X = 112.0                    # west of the bag fall, clear of the shared slot
    RISER_LANE_X = 200.0                     # the under-pump lane, west of water-5's climb
    # The exit off the core is one bend radius — the shortest turn the tube can take, which
    # is what keeps it inside the escape refrig-2 leaves. The approach into the bulkhead is
    # all water-2 leaves — its east leg crosses the collet's own southward line — so the
    # last climb stands as far north as that run's column allows and closes on what is left.
    # The reach east off the meter is the distance to the lane, so that leg rides a move of
    # either.
    RISER_OFF_METER = RISER_LANE_X - digi.at("outlet")[0]
    RISER_APPROACH = 5.0
    runs.append(route(
        "carb-1", "foam-assembly.carb-water-out",
        {"x": RISER_CLIMB_X},                # west inside refrig-2's standoff, off the bag fall
        digi.z("inlet"),                     # up the front face to the meter's own plane
        digi.y("inlet"),                     # south onto the meter's own axis
        "digiten-flow.inlet",                # east into its west-facing collet
        kind="water", bend=RBEND, skew=DISCHARGE_SKEW, stub=(RBEND, RBEND),
        note="carb water: cold-core outlet → DIGITEN flow meter, up the front face"))
    runs.append(route(
        "carb-2", "digiten-flow.outlet",
        {"z": sp.at("supply")[2]},           # up into the lane under the pump
        b_carb.out("tube-in", RISER_APPROACH),   # aft along it, past water-2's column
        b_carb.x("tube-in"),                 # east onto the bulkhead's own column
        "bulkhead-carb.tube-in",             # and straight up it into the collet
        kind="water", bend=RBEND, skew=DISCHARGE_SKEW,
        stub=(RISER_OFF_METER, RISER_APPROACH),
        note="carb water: DIGITEN outlet → rear umbilical, under the pump and up east of the ASSE"))

    # fluid-1 / fluid-2 — the flavor tap. Both runs live in the LANE UNDER THE PUMP: the pump's
    # bracket carries its body clear of the cap, and the gap that leaves runs the bay's whole
    # width and depth, free of everything the deck above it is full of. fluid-1 leaves the
    # split's west-facing run into that lane, crosses south under the pump's head and back east
    # onto V-A's own X, and closes north-to-south into the regulator standing in the band ahead
    # of the cap. fluid-2 then runs the regulator's outlet south past the nozzle-gate tray's east
    # end and turns down over V-A's up-facing collet.
    reg = f["flow-regulator"]
    src = f["source-select-assembly"]
    # The +X wall's inner face steps in as it runs forward — the rib band the seam's stations
    # stand on — so the flavor run leaves the split hard against it and comes west off it while
    # it is still aft, in the same lane the pump's back face and V-K's front face leave open.
    vk_pump_lane = (pump.bb.ymax + vk.bb.ymin) / 2.0
    runs.append(route(
        "fluid-1", "water-split.to-flavor",
        sp.out("to-flavor", 8.0),            # east out from under V-K, into the lane
        {"y": vk_pump_lane},                 # south to the lane behind the pump, off the wall's ribs
        reg.x("inlet"),                      # west onto the regulator's own line
        reg.out("inlet", 14.0),              # south under the pump, short of the regulator
        "flow-regulator.inlet",
        kind="fluid", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, 2.0),
        note="flavor tap: split run → flow regulator, along the lane under the pump"))
    runs.append(route(
        "fluid-2", "flow-regulator.outlet",
        src.y("V-A-I"),                      # south down the pocket to V-A's own line
        "source-select-assembly.V-A-I",      # then straight down the pocket into the collet
        kind="fluid", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, WBEND),
        note="flavor tap: flow regulator → V-A inlet"))

    # refrig-3 — the suction leg, unauthored. Its corridor stands open: the source-select
    # tray's central span stops at y 155.3 over the outlet's x, leaving ~27 mm off the
    # cold-core face at the outlet's own height, and the drop from there to the floor lane is
    # clear the whole way down past the stack. The floor lane is refrig-2's, so the two want
    # separating in y before this one is drawn.

    # fluid-4 — the hopper funnel's gravity drain into the shared source bank. It falls straight
    # down the spout's own axis into the band between the pump-discharge dividers' undersides and
    # the source tray's crown, runs east along that band on the drain's own y, drops at the collet's
    # station to under the nozzle-gate tray's floor, and turns aft onto V-B-I's upturned collet.
    # Every leg falls: this line carries head, not pressure. The band is the opening the crossing
    # discharge runs leave — they hang off the dividers that roof it.
    funnel, gate = f["hopper-funnel"], f["nozzle-gate-assembly"]
    src = f["source-select-assembly"]
    dod = funnel.diam("drain")              # the drain's own bore, off the spout it leaves
    FALL_CLEAR = 5.65                       # what the fall holds off each body it passes
    FALL_BEND = 12.0                        # 1/4" LLDPE, clean-sweeping radius (as the copper loop uses)
    drain_y, collet_x = funnel.at("drain")[1], src.at("V-B-I")[0]
    band_ceiling = min(f["y-d"].bb.zmin, f["y-g"].bb.zmin) - FALL_CLEAR - dod / 2.0
    band_floor = src.bb.zmax + FALL_CLEAR + dod / 2.0
    runs.append(R.bent(
        "fluid-4", "hopper-funnel.drain",
        (funnel.at("drain")[0], drain_y, band_ceiling),   # down under the dividers, into the band
        (collet_x, drain_y, band_floor),                  # east along it, over the source tray's crown
        (collet_x, drain_y,                               # down at the collet's station
         gate.bb.zmin - FALL_CLEAR - dod / 2.0),          # under the gate tray's floor before it turns
        "source-select-assembly.V-B-I",
        kind="fluid", bend=FALL_BEND, skew=DISCHARGE_SKEW, lead=(0.0, 6.0),
        note="hopper drain → V-B-I: down the spout's axis into the band under the dividers, east "
             "over the source tray, then aft and down onto the collet — every leg falls"))

    # The junction column's four legs — fluid-9/19 down from the source bank, fluid-10/20 up
    # from the bag bank — are one shape. Each elbow is rolled to aim along the column and the
    # tee stands on the line its two collets make (_contents `junction`), so the leg is the
    # straight between them: no constraint, no stub, no bend, ~1.8° of collet skew at each
    # end.
    for cid, frm, to, ch in (
        ("fluid-9",  "source-select-assembly.V-C-O", "tee-y-c.Y-C-1", "A source"),
        ("fluid-19", "source-select-assembly.V-D-O", "tee-y-f.Y-F-1", "B source"),
        ("fluid-10", "bag-circuit-assembly.V-E-O",   "tee-y-c.Y-C-2", "A bag return"),
        ("fluid-20", "bag-circuit-assembly.V-H-O",   "tee-y-f.Y-F-2", "B bag return"),
    ):
        runs.append(route(cid, frm, to, kind="fluid", stub=0.0,
                          note=f"channel {ch}: collet to tee, straight down the junction column"))

    # The pump-discharge runs — each flavor's bag + nozzle legs meet at its two-way divider. The
    # netlist is DIAGONAL (a flavor's two valves sit on opposite tray rows), so the two long legs
    # cross the row. Each turn-elbow aims its free leg at the outlet it feeds (_contents
    # `elbow_free_dir`), so a run leaves nearly along its collet: fluid-27 is one straight tube into
    # its outlet; fluid-13 bends once into y-d's yawed outlet; the two long crossing legs (17, 23)
    # leave climbing (the elbow's lift) and are carried OVER the near flavor's fitting by one
    # hand-placed apex, then down — a gentle arc, authored point-to-point with `bent`.
    # Both crossings run the open lane between the two trays (x 189.2–208.6), and the hopper
    # funnel's spout drops into its west half. The spout cannot be ducked under: its foot lands
    # level with elbow-bag-y-d's crown, leaving no gap between them to thread, and the tube is
    # climbing over that elbow just where the foot arrives. So fluid-23 holds EAST of the spout.
    # This is what caps hopper_funnel.ramp_angle — every degree lowers the foot, and the day it
    # falls a tube's width below the crown this lane closes. Each takes a
    # `lead=` stub, so it leaves and enters straight along its collet (skew ~0 by construction) and
    # only the apex is hand-placed, then rounds at the DBEND radius. The divider stems to the pumps
    # (segments 12/22) leave below, from each divider's own stem port.
    LEAD = 8.0                              # exit/approach stub: straight lead-out/-in along each collet
    DBEND = 12.0                            # 1/4" LLDPE, clean-sweeping radius (as the copper loop uses)
    # An apex is hand-placed in the LANE by its x — which side of the spout the arc passes. Neither
    # of its other two coordinates is a world number: its depth is an offset off the manifold
    # stack's own Y, and its height a rise over the crown of the one elbow the leg arcs over. Named
    # that way it rides that elbow's tray in both axes, so a stack that closes or slides carries
    # both arcs with it and the turn off each collet keeps its angle. A frozen number would hold the
    # apex where the tray no longer is, and the exit lead runs out of tangent for the sharper turn.
    for cid, elb, div, port, apex, lead, bend in (
        ("fluid-13", "elbow-bag-y-d", "y-d", "Y-D-2", None,                                     (8.0, 6.5), 6.0),  # one bend into the yawed outlet, on the row's tight radius — y-d rides its pump, this elbow its tray
        ("fluid-17", "elbow-y-g",     "y-d", "Y-D-3", (202.0, -24.55, "elbow-y-d",     3.77),  LEAD, DBEND),      # over elbow-y-d
        ("fluid-23", "elbow-bag-y-g", "y-g", "Y-G-2", (207.0, -17.55, "elbow-bag-y-d", 8.05),  (4.0, 8.0), DBEND),  # short exit lead + high apex, held EAST: the funnel spout drops into the west half of the lane and its foot sits level with elbow-bag-y-d's crown, so there is no gap between them to take — this clears the elbow and passes the spout on its east side
        ("fluid-27", "elbow-y-d",     "y-g", "Y-G-3", None,                                     (8.0, 6.0), DBEND),  # y-g sits west of this elbow, so it leaves on its collet and turns
    ):
        mids = ([] if apex is None else
                [(apex[0], contents.SRC_SEL_POS[1] + apex[1], f[apex[2]].bb.zmax + apex[3])])
        runs.append(R.bent(cid, f"{elb}.free", *mids, f"{div}.{port}",
                            kind="fluid", bend=bend, skew=DISCHARGE_SKEW, lead=lead,
                            note=f"discharge {port}: {elb} → {div} {port}, bent over the row"))

    # The pump-discharge stems (segments 12/22) — each divider's stem back to a pump outlet.
    # pump-b's outlet elbow and y-d's yawed stem sit near each other but no longer face down one
    # line (y-d aims at its elbows, which ride the west-inset gate), so fluid-12 leaves pump-b on
    # its collet (an exit lead) and turns to the meet point of the two collet axes before closing
    # into the stem. fluid-22 leaves pump A's east-facing outlet, crosses the open band over the
    # pumps, and turns into y-g's stem; the two sit in separate bays.
    op, od = contents.pump_outlet_pose("pump-b")
    sp, sd = contents.divider_port("y-d", 1)
    runs.append(R.bent("fluid-12", "pump-b.P-B-O", R.meet(op, od, sp, sd, 0.85), "y-d.Y-D-1",
                        kind="fluid", bend=5.0, skew=DISCHARGE_SKEW, lead=(6.0, 0.0),
                        note="discharge stem P-B-O → y-d Y-D-1, led off pump-b to the collets' meet — "
                             "the pair stands 15 mm apart, so the turn between them is the tightest "
                             "on the fluid side"))
    runs.append(R.bent("fluid-22", "pump-a.P-A-O", "y-g.Y-G-1",
                        kind="fluid", bend=8.0, skew=DISCHARGE_SKEW, lead=(8.0, 6.0),
                        note="discharge stem P-A-O → y-g Y-G-1: y-g now sits close off the pump's "
                             "east outlet and near square to it, so the two leads carry the turn "
                             "between them — no room across for a sweeping apex"))

    # The pump-suction stems (segments 11/21) — each pump's inlet back to its channel's junction
    # tee. Each branch is rolled forward, off the pump row (_contents `JUNCTION_ROLL`), so a run
    # leaves its collet heading −Y and picks up its `lead=` stub there. fluid-11 climbs out of
    # tee-y-c behind pump A's west motor barrel, drapes east over the pump bodies — below the row's
    # elbows, ahead of the bag tray — into pump B's far inlet, rolled northwest to meet it
    # (`PUMP_INLET_AIM`). fluid-21 climbs out of the buried tee-y-f up the west end of the column,
    # where the source tray floor drops away, then runs east above it into pump A's near inlet
    # (west face). Both close on the collet CENTRES (`_PUMP_INLET_BASE`).
    SLEAD = 12.0                        # exit/approach stub: straight lead off each suction collet
    runs.append(R.bent(
        "fluid-11", "tee-y-c.Y-C-3",
        _deck(34.0, -64.55, 257.0), _deck(72.0, -76.55, 273.0), _deck(110.0, -78.55, 279.0),
        _deck(150.0, -73.55, 283.0), _deck(196.0, -70.55, 286.0), _deck(213.0, -51.55, 285.0),
        "pump-b.P-B-I",
        kind="fluid", bend=6.0, skew=DISCHARGE_SKEW, lead=(8.0, 3.0),
        note="suction stem tee-y-c Y-C-3 → pump-b P-B-I: forward off the tee, then east OVER the "
             "y-d/y-g dividers. It rides the slot the lowered divider crowns open under the funnel "
             "basin, held SOUTH of the discharge runs (fluid-13/23) and the funnel's "
             "drain dip (x186-197), climbing north only east of the dip to drop into the inlet"))
    runs.append(R.bent(
        "fluid-21", "tee-y-f.Y-F-3",
        _deck(26.0, -15.55, 236.0), _deck(29.0, -40.55, 264.0), _deck(64.0, -46.55, 277.0),
        "pump-a.P-A-I",
        kind="fluid", bend=10.0, skew=DISCHARGE_SKEW, lead=SLEAD,
        note="suction stem tee-y-f Y-F-3 → pump-a P-A-I, up the west end then east above the source tray"))

    # fluid-15 / fluid-25 — the two bag lines, a cooperative PAIR down the one corridor open
    # behind the whole stack: the open Y between the manifold stack's aft face and the core's
    # front face (_contents BAG_FALL_CORRIDOR). Both bag Tees roll to the SAME aft angle
    # (bag_circuit_tray `bag_fall_aim`), so their branches leave the stack PARALLEL and never
    # cross, though both run centres sit on one X. Each branch aims down into the corridor,
    # turns along it to its own reservoir's end — bag A east, bag B west — and drops straight
    # into the port. The forward Tee (Y-E) cannot fall clear in one lean the way a lone aft
    # branch could: a shallow branch off it drives through the source stack under the tray, and
    # a straight drop off it would cut across the aft branch's line. The shared steep angle
    # answers both — threading the source tray's aft window and holding the pair parallel.
    bag = f["bag-circuit-assembly"]
    BBEND = 6.0              # 1/4" LLDPE
    baglines = (("fluid-15", "Y-E", "reservoir-A", "east"),
                ("fluid-25", "Y-H", "reservoir-B", "west"))

    # The tray's STEP bakes each roll in, so re-derive both branches from the live solids and
    # refuse a pose that no longer falls into the corridor above its reservoir, or that breaks
    # the pair's parallel. The exact clearance to the source stack each branch threads — whose
    # aft window is not a plane this can test against — is held by the scorecard (lines-clear,
    # clearance-floor); here we gate only the aim.
    #   Each line falls in its own column, down the recess in the stack's aft profile, so both the
    # lane and the corridor that has to hold it are measured in that column.
    stack = contents.build()["source-select-assembly"][0]
    aim = {}
    for cid, tee, port, _side in baglines:
        tip, n, res = bag.at(f"{tee}-2"), bag.normal(f"{tee}-2"), foam.at(port)
        if n[1] <= 0.0 or -n[2] < abs(n[1]):
            raise ValueError(
                f"{cid}: {tee}'s branch leaves along {tuple(round(v, 3) for v in n)} — to feed the "
                f"fall it must aim AFT (+Y, into the corridor) and fall (within 45° of vertical). "
                f"Roll it into the fall: bag_circuit_tray `bag_fall_aim`.")
        aft = _column_aft(stack, res[0], BBEND, res[2], tip[2])
        corridor = foam.bb.ymin - aft
        if corridor < contents.BAG_FALL_CORRIDOR:
            raise ValueError(
                f"{cid}: the fall corridor in {port}'s own column (x {res[0]:.1f}) is "
                f"{corridor:.2f} mm — the manifold stack's aft face there ({aft:.2f}) to the cold "
                f"core's front face ({foam.bb.ymin:.2f}) — inside the "
                f"{contents.BAG_FALL_CORRIDOR:.2f} a 1/4\" line takes with a lane clearance either "
                f"side. Move the core aft (_contents FRONT_DEPTH), the stack forward "
                f"(_contents STACK_CORE_GAP), or the port's shell bore into the stack's recess "
                f"(_port_cuts flavor_line_shell_hole_x).")
        fall_y = R.channel(aft, foam.bb.ymin)
        entry_z = tip[2] + n[2] * (fall_y - tip[1]) / n[1]     # where the branch axis meets the lane
        if entry_z <= res[2]:
            raise ValueError(
                f"{cid}: {tee}'s branch reaches the corridor lane (y {fall_y:.1f}) at z {entry_z:.1f}, "
                f"at or below {port} (z {res[2]:.1f}) — too low to drop into the port. Roll it "
                f"steeper: bag_circuit_tray `bag_fall_aim`.")
        aim[tee] = (tip, n, res, entry_z, fall_y)
    # Parallel, or the two branches cross in the shared X plane. Both carry the one `bag_fall_aim`,
    # so this holds by construction; it fires only if the Tees are given different rolls.
    nE, nH = aim["Y-E"][1], aim["Y-H"][1]
    if sum(nE[i] * nH[i] for i in range(3)) < math.cos(math.radians(1.0)):
        raise ValueError(
            f"fluid-15/25: the two bag branches are not parallel (Y-E {tuple(round(v, 3) for v in nE)}, "
            f"Y-H {tuple(round(v, 3) for v in nH)}) — they would cross in their shared X plane. Give "
            f"both Tees the one bag_circuit_tray `bag_fall_aim`.")

    for cid, tee, port, side in baglines:
        tip, n, res, entry_z, fall_y = aim[tee]
        runs.append(R.bent(
            cid, f"bag-circuit-assembly.{tee}-2",
            (tip[0], fall_y, entry_z),          # into the corridor, on the branch's own axis
            (res[0], fall_y, entry_z),          # along the corridor to the reservoir's end
            (res[0], fall_y, res[2]),           # straight down the corridor to the port's height
            f"foam-assembly.{port}",
            kind="fluid", bend=BBEND, skew=DISCHARGE_SKEW,
            note=f"bag {port[-1]}: branch aimed down into the fall corridor, {side} along it to "
                 f"the reservoir's end, straight down, and into the port"))

    # The nozzle-outlet runs (segments 18/28). Each leaves its elbow's free collet straight UP out
    # of the +X wall pocket onto the deck, steps into its lane, runs AFT down the lane over the
    # nozzle gate's spade tabs and the electronics shelf, CLIMBS over the pump, comes back down
    # behind the water chain, steps WEST into its bulkhead's lane, and closes straight IN. One
    # axis a move, every corner square.
    #   The deck is [292.4](NOZ_DECK_Z) — the bulkheads' own collet height, shared by both runs
    # and the height each closes at.
    #   LANE_CLEAR is the gap a lane holds off whatever bounds it, measured on the deck leg against
    # every placed part that leg CROSSES — the gate's spade tabs always, and the electronics shelf's
    # board only where the shelf is laid under a lane. The guard is below, once the lanes know their
    # own columns.
    LANE_CLEAR = 5.65                      # the gap a lane holds off whatever bounds it
    od = f["elbow-noz-a"].diam("free")     # the line's own bore, off the collet it leaves
    deck_z = f["bulkhead-flavor-a"].at("tube-in")[2]  # the height the runs close at
    # 28's west step off the pocket is [41.08](NOZ_POCKET_STEP) mm, and the square corner at each
    # end of it seats a tangent in that leg. 18 takes no step at all — its lane IS the column its
    # elbow stands in.
    NBEND = 7.0
    # The lanes cross the pump on its LOW END. `contents.seaflo_low_crown` is the pressure switch's
    # top face and the X window it spans — the motor, the head and the boss all stand well over it,
    # and this is the one plane on the pump with air above it. [310.2](NOZ_CLIMB_Z) is that crown
    # plus a lane. The pump is then free to travel east UNDER these two runs for as long as the
    # window still holds them, which is why what bounds its east reach is the water chain and not
    # these lanes.
    #   In X, 18 keeps the pocket column its own elbow stands in [274.18](NOZ_LANE_OUTER_X), which
    # passes east of the pump, the regulator, the split and V-K alike and never has to climb at
    # all. 28 steps west into the low window [248.13](NOZ_LANE_INNER_X) and climbs, because west of
    # the pocket the deck is the pump's the whole way across.
    #   Both close the same way: they come out of the pocket into the LANE the pump's back face
    # and V-K's front face leave open across the strip, run west along it to their own bulkhead's
    # column, and turn north into it. That lane is one tube deep, so the two runs take it at two
    # heights — 18 at the bulkheads' own deck, 28 still up at its climb, coming down onto the deck
    # only once it stands over its own bulkhead, west of everything 18 occupies.
    reg, vk_f, split = f["flow-regulator"], f["vk-fill-valve"], f["water-split"]
    crown, window = contents.seaflo_low_crown()
    climb_z = crown + od / 2.0 + LANE_CLEAR
    pump = f["seaflo-pump"]
    # Both lanes stand inside the low window, one against each of its edges — that is the widest
    # they can be spaced and still both cross the pump where the pump is short.
    outer_x = window[1] - od / 2.0 - LANE_CLEAR         # 18, against the window's east edge
    inner_x = window[0] + od / 2.0 + LANE_CLEAR         # 28, against its west edge
    if outer_x - inner_x < od + LANE_CLEAR:
        raise ValueError(
            f"fluid-18/28: the pump's low window (x {window[0]:.2f}..{window[1]:.2f}) leaves its "
            f"two lanes {outer_x - inner_x:.2f} mm apart, inside the {od + LANE_CLEAR:.2f} mm a "
            f"lane and its clearance take — the two runs cannot both cross the pump here.")
    # Each lane leaves the deck ahead of the SOUTHERNMOST thing standing in its own column — the
    # pump for both, and for the outer lane the regulator too, whose stem reaches deck height in
    # the band ahead of the cap. A lane that waited for the pump would run through that stem.
    def _climb_y_in(lane_x):
        south = [b.bb.ymin for b in (pump, reg)
                 if b.bb.xmin - od / 2.0 < lane_x < b.bb.xmax + od / 2.0
                 and b.bb.zmin < deck_z + od / 2.0 < b.bb.zmax]
        return min(south, default=pump.bb.ymin) - 6.0
    exit_y = (pump.bb.ymax + vk_f.bb.ymin) / 2.0        # the lane the pump and V-K leave between them
    drop_y = vk_f.bb.ymin + 9.0                        # and where each comes down, off water-4's lane

    def _over_pump(lane_x):
        return lane_x - od / 2.0 < pump.bb.xmax         # the TUBE crosses it, not just its clearance

    # What a lane holds its clearance off is what stands UNDER ITS DECK LEG — the stretch it takes at
    # deck height, from its elbow's column west into its lane and aft to where it climbs, or to the
    # strip if it never meets the pump. The spade tabs lie under both legs by construction. The
    # shelf's board lies under them only if it is laid in the lanes' own columns; a board standing
    # anywhere else in the bay is not something these runs pass over, and its crown does not bind
    # a deck it never shares.
    def _under_deck(bb):
        pad = od / 2.0 + LANE_CLEAR
        for elb, lane_x in (("elbow-noz-a", outer_x), ("elbow-noz-b", inner_x)):
            ex, ey = f[elb].at("free")[:2]
            ay = _climb_y_in(lane_x) if _over_pump(lane_x) else exit_y
            if (bb.xmin < max(ex, lane_x) + pad and bb.xmax > min(ex, lane_x) - pad
                    and bb.ymin < max(ey, ay) + pad and bb.ymax > min(ey, ay) - pad):
                return True
        return False

    crossings = [("the nozzle gate's spade tabs", contents.noz_spade_crown())]
    if "pcba" in f and _under_deck(f["pcba"].bb):
        crossings.append(("the electronics shelf's board", f["pcba"].bb.zmax))
    for what, top in crossings:
        if deck_z - od / 2.0 - top < LANE_CLEAR:
            raise ValueError(
                f"fluid-18/28: the deck ({deck_z:.2f}, the bulkheads' collet height) clears {what} "
                f"({top:.2f}) by {deck_z - od / 2.0 - top:.2f} mm, inside the "
                f"{LANE_CLEAR:.2f} mm the lane holds — lower {what}, or raise the bulkheads.")
    # The two cross the strip one lane apart in Z: 18 at its own climb, 28 one lane over it, so
    # the leg each takes west to its bulkhead's column never meets the other's.
    for cid, elb, bulk, lane_x, cross_z in (
        ("fluid-18", "elbow-noz-a", "bulkhead-flavor-a", outer_x, climb_z),
        ("fluid-28", "elbow-noz-b", "bulkhead-flavor-b", inner_x, climb_z + od + LANE_CLEAR),
    ):
        # A lane is only allowed over the pump where the pump is low. Anywhere else the crown is
        # the motor's or the boss's and the climb would have to leave the box.
        lo, hi = lane_x - od / 2.0 - LANE_CLEAR, lane_x + od / 2.0 + LANE_CLEAR
        over_pump = _over_pump(lane_x)
        if over_pump and not (window[0] <= lo and hi <= window[1]):
            raise ValueError(
                f"{cid}: its lane (x {lo:.2f}..{hi:.2f}, a lane's clearance either side) reaches "
                f"over the pump (east to x {pump.bb.xmax:.2f}) outside the low window x "
                f"{window[0]:.2f}..{window[1]:.2f} the pressure switch opens — over the motor, the "
                f"head or the boss the crown is {pump.bb.zmax:.2f} and no lane clears it under the "
                f"ceiling. Move the lane into the window, or the pump (_contents SEAFLO_POS) out "
                f"from under it.")
        b = f[bulk]
        # The step west off the pocket, unless the lane is the pocket column itself; and the climb,
        # unless the lane passes east of the pump and never meets it.
        step = [] if abs(lane_x - f[elb].at("free")[0]) < 1e-9 else [{"x": lane_x}]
        climb = [{"y": _climb_y_in(lane_x)}, {"z": cross_z}] if over_pump else []
        runs.append(route(
            cid, f"{elb}.free",
            {"z": deck_z},                      # up out of the pocket, onto the deck over the spade tabs
            *step,                              # west into its own lane, clear of the boss chain
            *climb,                             # up ahead of the pump, over its low end
            {"y": exit_y},                      # aft into the lane behind the pump
            b.x("tube-in"),                     # west along that lane to the bulkhead's own column
            *([{"y": drop_y}, {"z": deck_z}] if climb else []),  # aft off water-4's lane, then down
            f"{bulk}.tube-in",
            kind="fluid", bend=NBEND, skew=DISCHARGE_SKEW,
            note=f"nozzle outlet: {elb} → {bulk}, out over the shelf and west behind the pump"))

    return runs


def build() -> dict:
    """The runs as placed solids: {name: (solid, color)} — copper for the refrigerant loop,
    white LLDPE for the fluid (flavor) and tap-water runs."""
    return {r.id: (R.tube(r), COPPER if r.kind == "refrigerant" else LLDPE) for r in build_runs()}


def lane_stations() -> dict:
    """The nozzle-outlet lanes' stations and the carb riser's two cut lengths, taken from the
    built runs themselves — so the numbers the prose above quotes are literally the numbers the
    tubes were swept along, not a second hand-kept copy of them. `enclosure_assembly` feeds
    these to the [value](NAME) markers."""
    pts = {r.id: r.pts for r in build_runs() if r.id in ("fluid-18", "fluid-28")}
    riser = {r.id: r for r in build_runs() if r.id in ("carb-1", "carb-2")}
    return {
        # The riser's two halves, either side of the flow meter: what the shop cuts, and what
        # the CARGEN insulation is cut to follow (internal-plumbing.md §4).
        "CARB_1_LEN": f"{riser['carb-1'].length:.4g}",
        "CARB_2_LEN": f"{riser['carb-2'].length:.4g}",
        # The deck each closes at, and the highest the pair ever runs — over the pump's low crown.
        "NOZ_DECK_Z":      f"{pts['fluid-18'][1][2]:.4g}",
        "NOZ_CLIMB_Z":     f"{max(p[2] for p in pts['fluid-18']):.4g}",
        # The column each holds all the way aft: 18's is its own pocket, 28's the window west of
        # the regulator. Both are the x the run still has once it has finished stepping.
        "NOZ_LANE_OUTER_X": f"{pts['fluid-18'][2][0]:.5g}",
        "NOZ_LANE_INNER_X": f"{pts['fluid-28'][2][0]:.5g}",
        # 28's west step off the pocket — the leg that sets the corner radius it turns at.
        "NOZ_POCKET_STEP": f"{math.dist(pts['fluid-28'][1], pts['fluid-28'][2]):.4g}",
    }


# A run whose id is not itself a connection, because an in-line fitting splits it: a union
# tee's RUN ports face each other down one straight path, so two segments butted into them
# can be one piece of authored geometry answering for both on the routed axis. Empty — every
# authored run is one connection; the union tees are placed components whose collets anchor
# their segments separately.
CARRIES: dict = {}


def routed_ids() -> set:
    """The connection ids with a built path — what the scorecard's `routed` axis counts."""
    return {c for r in build_runs() for c in CARRIES.get(r.id, (r.id,))}


def clearances(solids: dict) -> list:
    """Each run's tightest gap to a part it does not terminate on, or to another run. The two
    components a run joins are skipped. Reported, not gated; `HSM_SKIP_CLEARANCES` drops it.

    The nearest is found by a box-sorted branch-and-bound. A box gap is a lower bound on the exact
    solid gap — a box encloses its solid, so two boxes are at least as close as the solids inside
    them — so candidates are ordered by box gap and, once one's box gap exceeds the tightest exact
    gap found, every farther candidate is skipped: its exact gap cannot be smaller. The reported
    number is still the exact BRepExtrema distance to the true nearest; only the queries that
    provably cannot win are dropped, several hundred of them per build. The cached boxes make the
    ordering nearly free. PRUNE_SLOP guards the bound against floating-point on a near-flush pair."""
    import scorecard

    PRUNE_SLOP = 1e-6                                   # mm; a box gap this much past best still queries
    runs = build_runs()
    tubes = {r.id: R.tube(r) for r in runs}
    boxes = {n: _boxes.boxed(s) for n, s in solids.items()}
    tube_boxes = {rid: _boxes.boxed(t) for rid, t in tubes.items()}

    out = []
    for r in runs:
        t, tb = tubes[r.id], tube_boxes[r.id]
        ends = {r.frm.split(".")[0], r.to.split(".")[0]}
        cand = [(scorecard._bbox_gap(tb, boxes[n]), n, solids[n]) for n in solids if n not in ends]
        cand += [(scorecard._bbox_gap(tb, tube_boxes[o]), o, tubes[o]) for o in tubes if o != r.id]
        cand.sort(key=lambda c: c[0])
        best = None                                    # (exact gap, name) of the nearest so far
        for bgap, n, s in cand:
            if best is not None and bgap > best[0] + PRUNE_SLOP:
                break                                  # lower bound past best: no farther body can win
            g = scorecard._solid_gap(t, s)
            if best is None or (g, n) < best:
                best = (g, n)
        out.append((r, best))
    return out
