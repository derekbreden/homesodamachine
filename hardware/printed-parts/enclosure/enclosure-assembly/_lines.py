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
    foam-cap top — with the ASSE 1022 chain lying along it: its 1/4" inlet west off the water
    bulkhead (water-1), its 1/4" outlet east onto the line to the split (water-2). The chain's
    mass sits high, so a LANE runs the strip's whole length beneath it at the suction's own
    height, and V-K lies along that lane: fed east off the split in the pocket (water-3), it
    looks straight west down the lane at the north-facing suction (water-4). The band UNDER
    the ASSE body stays open the same way: the drip the vent lets go of falls through it.
  * the east pocket — the open column between the cold core's east face and the +X wall, aft
    of the pump's narrow head end. The water chain hangs down it in one plane: the split at the
    top taking the ASSE feed, then the flow regulator, then the fall to V-A (fluid-1, fluid-2).
    It is the only lane across the deck that the pump does not fill.
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
  * the +X wall pocket and the channel inboard of it — the cold core's own standoff off that
    wall, where the two nozzle-outlet elbows stand, and the wide horizontal channel over the
    nozzle gate's spade tabs and the electronics shelf's board, under the hopper funnel's
    basin, which runs unbroken the full depth of the box. It is wide rather than tall, so
    fluid-18/28 share one deck ([292.4](NOZ_DECK_Z)) side by side in x rather than stacking,
    and reach the rear flavor bulkheads without either climbing over the other. They take the
    two lanes inboard of the flavor tap's fall, which owns the band's outermost. The pocket is
    also the Y seam's corner-post lane, so both step west out of it before turning aft at all.

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

    # water-2 — the 1/4" line off the ASSE's east outlet: straight east along the strip
    # to the east pocket, then down the pocket's open column and south into the split's
    # north-facing run. The descent stands off the split far enough to turn into it.
    runs.append(route(
        "water-2", "asse1022-assembly.tube-out",
        sp.x("supply"),                      # east down the strip to the pocket's line
        sp.y("supply", 13.0),                # north of the split, clear of its collet
        sp.z("supply"),                      # down the pocket to the split's port plane
        "water-split.supply",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, WBEND),
        note="tap water: ASSE 1022 outlet → split run"))

    # water-3 — the short straight hop off the split's west-facing branch into V-K's
    # inlet: the two collets are collinear along X in the one plane.
    runs.append(route(
        "water-3", "water-split.to-vk",
        "vk-fill-valve.inlet",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(2.0, 2.0),
        note="tap water: split branch → V-K inlet"))

    # water-4 — V-K's outlet looks straight down the lane under the ASSE overhang: west
    # to the suction's own line, then the short turn south into the north-facing barb.
    # The 1/4" LLDPE steps up to the pump's 3/8" barb there (adapter in the BOM) — the
    # barbs are molded into the head, so that step is the only 3/8" on this side.
    runs.append(route(
        "water-4", "vk-fill-valve.outlet",
        pump.x("suction"),                   # west down the lane to the suction's line
        "seaflo-pump.suction",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, 2.0),
        note="tap water: V-K outlet → SeaFlo suction (under the ASSE overhang)"))

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

    # water-5 — the 1/4" LLDPE off the chain's collet, down the corridor and west to the
    # cold core's water inlet on its front face.
    runs.append(route(
        "water-5", "discharge-chain.tube-port",
        disch.z("tube-port", -12.0),         # on down the corridor, under the turn
        foam.x("water-in"),                  # west to the port's own line
        foam.z("water-in"),                  # up to the port's height
        "foam-assembly.water-in",
        kind="water", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, WBEND),
        note="carb water: discharge chain → cold-core water inlet"))

    # fluid-1 / fluid-2 — the flavor tap. The split's south run carries the ASSE feed on
    # down the east pocket into the flow regulator, and the regulator's outlet runs the
    # length of the pocket south, drops past the nozzle-gate tray's east end and turns
    # in over V-A's up-facing collet. The pocket is open the whole way (probe: x 272–292
    # clear from the split's plane down to the manifold).
    reg = f["flow-regulator"]
    src = f["source-select-assembly"]
    runs.append(route(
        "fluid-1", "water-split.to-flavor",
        reg.y("inlet", 11.0),                # south down the pocket, short of the regulator
        reg.x("inlet"),                      # west one lane, off the wall's boss-chain band
        "flow-regulator.inlet",
        kind="fluid", bend=WBEND, skew=DISCHARGE_SKEW, stub=(WBEND, WBEND),
        note="flavor tap: split run → flow regulator"))
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
    # An apex is hand-placed in the LANE (x, y — which side of the spout the arc passes), but its
    # height is not a world Z: it is a rise over the crown of the one elbow the leg arcs over. Named
    # that way it rides that elbow's tray, so a stack that closes carries both arcs down with it and
    # the turn off each collet keeps its angle. A frozen Z would hold the apex where the tray no
    # longer is, and the exit lead runs out of tangent for the sharper turn.
    for cid, elb, div, port, apex, lead, bend in (
        ("fluid-13", "elbow-bag-y-d", "y-d", "Y-D-2", None,                                   (8.0, 6.5), 8.0),  # one bend into the yawed outlet
        ("fluid-17", "elbow-y-g",     "y-d", "Y-D-3", (202.0, 111.0, "elbow-y-d",     3.77),  LEAD, DBEND),      # over elbow-y-d
        ("fluid-23", "elbow-bag-y-g", "y-g", "Y-G-2", (207.0, 118.0, "elbow-bag-y-d", 8.05),  (4.0, 8.0), DBEND),  # short exit lead + high apex, held EAST: the funnel spout drops into the west half of the lane and its foot sits level with elbow-bag-y-d's crown, so there is no gap between them to take — this clears the elbow and passes the spout on its east side
        ("fluid-27", "elbow-y-d",     "y-g", "Y-G-3", None,                                   (8.0, 6.0), DBEND),  # y-g sits west of this elbow, so it leaves on its collet and turns
    ):
        mids = [] if apex is None else [(apex[0], apex[1], f[apex[2]].bb.zmax + apex[3])]
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
                        kind="fluid", bend=6.0, skew=DISCHARGE_SKEW, lead=(6.0, 0.0),
                        note="discharge stem P-B-O → y-d Y-D-1, led off pump-b to the collets' meet"))
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
        (34.0, 71.0, 257.0), (72.0, 59.0, 273.0), (110.0, 57.0, 279.0), (150.0, 62.0, 283.0), (196.0, 65.0, 286.0), (213.0, 84.0, 285.0),
        "pump-b.P-B-I",
        kind="fluid", bend=6.0, skew=DISCHARGE_SKEW, lead=(8.0, 3.0),
        note="suction stem tee-y-c Y-C-3 → pump-b P-B-I: forward off the tee, then east OVER the "
             "y-d/y-g dividers. It rides the slot the lowered divider crowns open under the funnel "
             "basin, held SOUTH (y~63) of the discharge runs (fluid-13/23, y74+) and the funnel's "
             "drain dip (x186-197), climbing north only east of the dip to drop into the inlet"))
    runs.append(R.bent(
        "fluid-21", "tee-y-f.Y-F-3",
        (26.0, 120.0, 236.0), (29.0, 95.0, 264.0), (64.0, 89.0, 277.0),
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
    fall_y = R.channel(src.bb.ymax, foam.bb.ymin)
    baglines = (("fluid-15", "Y-E", "reservoir-A", "east"),
                ("fluid-25", "Y-H", "reservoir-B", "west"))

    # The tray's STEP bakes each roll in, so re-derive both branches from the live solids and
    # refuse a pose that no longer falls into the corridor above its reservoir, or that breaks
    # the pair's parallel. The exact clearance to the source stack each branch threads — whose
    # aft window is not a plane this can test against — is held by the scorecard (lines-clear,
    # clearance-floor); here we gate only the aim.
    aim = {}
    for cid, tee, port, _side in baglines:
        tip, n, res = bag.at(f"{tee}-2"), bag.normal(f"{tee}-2"), foam.at(port)
        if n[1] <= 0.0 or -n[2] < abs(n[1]):
            raise ValueError(
                f"{cid}: {tee}'s branch leaves along {tuple(round(v, 3) for v in n)} — to feed the "
                f"fall it must aim AFT (+Y, into the corridor) and fall (within 45° of vertical). "
                f"Roll it into the fall: bag_circuit_tray `bag_fall_aim`.")
        entry_z = tip[2] + n[2] * (fall_y - tip[1]) / n[1]     # where the branch axis meets the lane
        if entry_z <= res[2]:
            raise ValueError(
                f"{cid}: {tee}'s branch reaches the corridor lane (y {fall_y:.1f}) at z {entry_z:.1f}, "
                f"at or below {port} (z {res[2]:.1f}) — too low to drop into the port. Roll it "
                f"steeper: bag_circuit_tray `bag_fall_aim`.")
        aim[tee] = (tip, n, res, entry_z)
    # Parallel, or the two branches cross in the shared X plane. Both carry the one `bag_fall_aim`,
    # so this holds by construction; it fires only if the Tees are given different rolls.
    nE, nH = aim["Y-E"][1], aim["Y-H"][1]
    if sum(nE[i] * nH[i] for i in range(3)) < math.cos(math.radians(1.0)):
        raise ValueError(
            f"fluid-15/25: the two bag branches are not parallel (Y-E {tuple(round(v, 3) for v in nE)}, "
            f"Y-H {tuple(round(v, 3) for v in nH)}) — they would cross in their shared X plane. Give "
            f"both Tees the one bag_circuit_tray `bag_fall_aim`.")

    # The corridor has to hold the lines it was opened for, measured on the two faces that bound it.
    corridor = foam.bb.ymin - src.bb.ymax
    if corridor < contents.BAG_FALL_CORRIDOR:
        raise ValueError(
            f"fluid-15/25: the fall corridor is {corridor:.2f} mm — the manifold stack's aft face "
            f"({src.bb.ymax:.2f}) to the cold core's front face ({foam.bb.ymin:.2f}) — inside the "
            f"{contents.BAG_FALL_CORRIDOR:.2f} a 1/4\" line takes with a lane clearance either "
            f"side. Move the core aft (_contents FRONT_DEPTH) or the stack forward.")

    for cid, tee, port, side in baglines:
        tip, n, res, entry_z = aim[tee]
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
    # of the +X wall pocket onto the deck, steps WEST into its lane, runs AFT down the lane over
    # the nozzle gate's spade tabs and the electronics shelf, steps WEST into its bulkhead's lane,
    # and closes straight IN. One axis a move, every corner square.
    #   The deck is [292.4](NOZ_DECK_Z) — the bulkheads' own collet height, shared by both runs.
    # 18 rides the outer lane [262.18](NOZ_LANE_OUTER_X), 28 the inner [250.18](NOZ_LANE_INNER_X);
    # 28 crosses 18's lane forward of 18's elbow, so 28 leaves the lane first and 18 second, each
    # into the bulkhead on its own side. Both turn aft west of the ±X boss-chain band, which
    # carries the seam's Z-pin stations and Y corner column.
    #   LANE_CLEAR is the gap the deck holds over what passes beneath it, measured below against
    # every placed part it crosses — the gate's spade tabs always, and the electronics shelf's
    # board whenever the shelf is on the deck.
    cold = f["foam-assembly"]
    LANE_CLEAR = 5.65                      # the gap a lane holds off whatever bounds it
    od = f["elbow-noz-a"].diam("free")     # the line's own bore, off the collet it leaves
    deck_z = f["bulkhead-flavor-a"].at("tube-in")[2]  # the height the runs close at
    # The band stands on the core's east face. Its outermost lane is the flavor tap's — fluid-2
    # falls down the pocket on V-A's own X, which lands there — so both nozzle runs take the
    # lanes inboard of it.
    flavor_x = cold.bb.xmax - LANE_CLEAR - od / 2.0
    outer_x = flavor_x - (od + LANE_CLEAR)
    crossings = [("the nozzle gate's spade tabs", contents.noz_spade_crown())]
    if "pcba" in f:
        crossings.append(("the electronics shelf's board", f["pcba"].bb.zmax))
    for what, crown in crossings:
        if deck_z - od / 2.0 - crown < LANE_CLEAR:
            raise ValueError(
                f"fluid-18/28: the deck ({deck_z:.2f}, the bulkheads' collet height) clears {what} "
                f"({crown:.2f}) by {deck_z - od / 2.0 - crown:.2f} mm, inside the "
                f"{LANE_CLEAR:.2f} mm the lane holds — lower {what}, or raise the bulkheads.")
    # 18's west step off the pocket is [27.03](NOZ_POCKET_STEP) mm, and the square corner at each
    # end of it seats a tangent in that leg.
    NBEND = 7.0
    # The water chain — the flow regulator, the split and V-K — stands down the east pocket at
    # the deck height these lanes would otherwise run at. The lanes dip UNDER the whole column:
    # aft at the deck over the spade tabs, down ahead of the regulator (the southernmost of the
    # three), along below all of them (they start well above the clear aft floor), then up past
    # V-K's back face into the bulkhead lane.
    chain = [f["flow-regulator"], f["water-split"], f["vk-fill-valve"]]
    vk_f = f["vk-fill-valve"]
    dip_z = min(c.bb.zmin for c in chain) - 7.0     # under the whole column, over the clear floor
    dip_y_in = min(c.bb.ymin for c in chain) - 6.0  # drop ahead of the southernmost of them
    dip_y_out = vk_f.bb.ymax + 11.5                 # rise behind V-K, clear of water-4's lane
    for cid, elb, bulk, lane_x in (
        ("fluid-18", "elbow-noz-a", "bulkhead-flavor-a", outer_x),                  # outer lane
        ("fluid-28", "elbow-noz-b", "bulkhead-flavor-b", outer_x - (od + LANE_CLEAR)),  # inner lane
    ):
        b = f[bulk]
        runs.append(route(
            cid, f"{elb}.free",
            {"z": deck_z},                      # up out of the pocket, onto the deck over the spade tabs
            {"x": lane_x},                      # west into its own lane, clear of the boss chain
            {"y": dip_y_in},                    # aft to just ahead of the split
            {"z": dip_z},                       # drop under the split + V-K
            {"y": dip_y_out},                   # aft under them, past V-K's back face
            {"z": deck_z},                      # rise back to the deck at the bulkhead
            b.x("tube-in"),                     # west into the bulkhead's own lane
            f"{bulk}.tube-in",
            kind="fluid", bend=NBEND, skew=DISCHARGE_SKEW,
            note=f"nozzle outlet: {elb} → {bulk}, up over the shelf, dipping under the split + V-K"))

    return runs


def build() -> dict:
    """The runs as placed solids: {name: (solid, color)} — copper for the refrigerant loop,
    white LLDPE for the fluid (flavor) and tap-water runs."""
    return {r.id: (R.tube(r), COPPER if r.kind == "refrigerant" else LLDPE) for r in build_runs()}


def lane_stations() -> dict:
    """The nozzle-outlet lanes' stations, taken from the built runs themselves — so the numbers
    the prose above quotes are literally the numbers the tubes were swept along, not a second
    hand-kept copy of them. `enclosure_assembly` feeds these to the [value](NAME) markers."""
    pts = {r.id: r.pts for r in build_runs() if r.id in ("fluid-18", "fluid-28")}
    return {
        "NOZ_DECK_Z":      f"{pts['fluid-18'][2][2]:.4g}",   # the shared deck, the bulkheads' collet height
        "NOZ_LANE_OUTER_X": f"{pts['fluid-18'][2][0]:.5g}",  # 18's lane, off the cold core's east face
        "NOZ_LANE_INNER_X": f"{pts['fluid-28'][2][0]:.5g}",  # 28's lane, one lane inboard of it
        # 18's west step off the pocket — the leg that sets the corner radius both runs turn at.
        "NOZ_POCKET_STEP": f"{math.dist(pts['fluid-18'][1], pts['fluid-18'][2]):.4g}",
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
