"""Kitchen Edition enclosure contents — the core subsystems packed.

Detailed STEP imports where they exist (cold-core foam assembly — shell +
top/bottom foam-cap stacks — the compressor shroud, the source-select
assembly, the bag-circuit assembly, the nozzle-gate assembly, both Kamoer
pump assemblies, both pump-inlet union tees, both pump-discharge dividers
(Y-D/Y-G) and their four turn elbows, the water deck (SeaFlo pump, its
discharge chain, the ASSE 1022 assembly, the split, V-K, the flow
regulator, the drip pan + its rails), the CO2 chain (DERPIPE inlet, GASHER
check, WR1110 regulator), the DIGITEN flow meter on the carb-water riser,
the PCBA, the power assembly, the AC hub, relay
#1, the ground stack, the MQ-6 gas sensor, the panel bulkheads + C14).
One placeholder primitive remains (condenser+fan). Not everything is
packed — deferred, tracked by the fluid topology
(/hardware/topology/fluid-topology.md) and the scorecard's connection
table, never silently dropped: the Shutao moisture plate lying in the drip
pan, and the two electrical parts the shelf has no station for yet — the DC
distribution block and relay #2, whose ports are authored PROVISIONAL
against that.

Components only: no tubes, no wires, no mount features. enclosure_assembly.py
verifies the pack pairwise non-intersecting at every export.

The Waterdrop 15UC-UF inline filter (~Ø63 × 311 mm) mounts outside the
enclosure, inline on the customer's 1/4" LLDPE feed upstream of the
rear-panel water-inlet bulkhead (/hardware/assembly/internal-plumbing.md §2).

Coordinate frame: +X right, +Y back, +Z up. Origin at the lower-front-left
corner. The enclosure is four printed pieces — a Y seam as far back as the
cold core allows, and a Z seam per column: at the front stack's waist over
the condenser in the front pieces, above the foam-cap top in the back
(enclosure.py `z_joint_front` / `z_joint_back`) — whose lips and cross-pin
pods hug the walls; the wall-adjacent insets below keep content clear of
them.

The band above the cold core — foam-cap top to ceiling, the foam's full
footprint — is the appliance's service bay. The electronics shelf (power
assembly, PCBA, DC distribution block) lies flat on the foam-cap top in
its front half, and every external connection (the faucet umbilical, the
C14 mains inlet, the tap-water inlet) penetrates the rear wall above the
cold core, its body reaching ~28–35 mm forward into the band's open rear
half. The risers' tube-and-cord traffic climbs the foam's front face and
crosses the band to those terminations. The cold core seats directly
against the rear wall.

The cold core's tube connections are defined by the foam shell's
penetrations (/hardware/printed-parts/cold-core/foam-shell/README.md
§Penetrations), all on its −Y front wall — in enclosure world coordinates:
  * carbonated-water outlet at (141.5, 182, 37) — one of the vessel's two
    bottom-plate ports. The riser cannot leave this face head-on: refrig-2
    climbs the same x on its way to the evaporator inlet above, and stands
    9.52 mm off the collet. So the line turns WEST inside that gap, climbs
    the front face west of the bag fall, runs east through the DIGITEN flow
    meter lying in the strip at the water inlet's own height, and climbs
    from there to the rear umbilical;
  * reservoir (bag) lines at (44.5, 182, 35.5) and (238.5, 182, 35.5) —
    they climb the foam front face to the bag-circuit loops;
  * the shared slot at x 141.5 spanning z ~72–246 — both copper evaporator
    stubs (to the compressor), the water inlet (from the SeaFlo discharge),
    and the PRV vent;
  * CO2 inlet at (160.5, 182, 37) — beside the carbonated-water outlet on
    the vessel's other bottom-plate port, its bore carrying on through the
    support ring to the elbow under the plate. It is fed from the front of
    the machine, from the chain hanging off the front-panel inlet.

Strata, floor to ceiling:
  * Floor:   compressor shroud (front-left) + condenser/fan (front-right,
             cross-flow along X, the donor block tipped on its back so its
             long dimension runs along Y and the floor stratum tops out
             level with the compressor; the donor's factory filter-drier is
             brazed to its outlet, inside this harvested block), the MQ-6
             on the floor between the compressor and the cold core
             (isobutane sinks).
  * The machine corridor (compressor back face to cold-core front face,
             below the tray stack's floor): open. It carries the
             manifold's cross-machine lines and refrig-3's unauthored run
             to the compressor's suction port; refrig-1 and refrig-2
             already cross its east half.
  * Zone A:  cold core (foam assembly: bottom cap + shell + top cap) at the
             back, flat on the floor — its bottom cap's lid is a plane,
             every cap screw down in its own counterbore — fenced ahead by
             the floor's two core lugs, with its −Y dispense/service ports
             facing forward.
  * Zone C (the front column's upper band): the valve-manifold tray stack,
             pressed aft against the cold core — the source-select
             assembly (Tray 1: V-A, V-B, Y-A, Y-B, V-C, V-D on a printed
             tray) FLOORING the stack, plate down and valves up, spanning
             the front width with its tall walls' backs on the foam's
             front face and its east collets facing up at the tap feed
             and the funnel drain that arrive from above; the bag-circuit
             assembly (Tray 2: V-E/V-F/V-H/V-I + Tees Y-E/Y-H) INVERTED
             on top of it, wall-top to wall-top, its bare east ports
             facing the nozzle-gate pocket and its bag branches out ±Y;
             and the nozzle-gate assembly (Tray 3: V-G/V-J, all ports
             bare) INVERTED the same way in that pocket — east of the
             bag assembly on the stack's second-story plane — its
             inner ports facing west at the bag east bank across the
             seats reserved for the pump-discharge tees (Y-D/Y-G,
             deferred), its outer ports facing east at the wall. The
             lower trays' west outlet elbows are rolled off their port
             axes to face each other — the source's inward, the bag's
             outward — down one leaning line: the JUNCTION COLUMN, with
             the pump-inlet union tees standing on that line and one
             straight stub joining each collet to the tee it butts. The
             stack floats over the floor stratum,
             leaving an open under-stack corridor for the manifold's
             cross-machine lines, and its floor clears the front Z-seam's
             lip band. Ahead of the stack, the PUMP ROW: both Kamoer
             KPHM400 assemblies lying depth-along-X in one pose — motors
             west, outlet elbows standing on the +Z faces, free collets
             facing west at the row's crest. P-A's head is nose-in at
             mid-row, its aft elbow one clearance ahead of the bag tray's
             Y-E bag branch; P-B sits one slot east and forward, ahead of
             the source-select east bank. The funnel's centred drain
             hangs over the row with the stack's whole height below it
             before segment 4 reaches V-B-I. Holders TBD (held).
  * Zone B (the band above the cold core): the WATER DECK on the foam-cap
             top. The SeaFlo lies across the bay, motor axis along X, base
             flat on the cap, nudged east so its head's two ±Y barbs clear
             the ASSE chain — the suction faces NORTH up to the split, the
             discharge SOUTH down to the cold core's water-in. In the strip behind it
             the ASSE 1022 assembly lies along X, its 1/4" PTC inlet WEST off
             the tap-water bulkhead it protects (segment water-1), its 1/4"
             PTC outlet EAST onto the 1/4" line to the split (water-2). Its
             atmospheric vent hangs in its native pose: the drip falls
             straight down its own column to the foam-cap top, where the pan
             + moisture plate sit, and the band beneath the body is left open
             for them. V-K lies along the lane the chain's overhang leaves
             beneath it, and the split hangs in the east pocket: its run
             carries the ASSE outlet down the pocket to the flow regulator
             and V-A, and its branch turns V-K's share west toward the
             suction. The rear half of the band stays open for the panel bodies
             reaching in from the wall (the umbilical triangle, the
             tap-water bulkhead, and the C14 in the west corner) and the
             riser traffic crossing to them.
  * Zone C top: the top wall right of the display is one open rectangle
             cut at the placed funnel's collar (enclosure.py
             `_hopper_hole` reads FUNNEL_CX/CY + the funnel's own dims) —
             the funnel is a static part (hopper_funnel.py, local frame)
             whose brim rests on the box top. The rear-panel port field is
             what sets the box height.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"

# The manifold trays' own modules: the junction column's aim is solved in
# bag_circuit_tray, and the tee poses below stand on the same elbow rolls the
# tray STEPs are built with.
_VM = _hw / "printed-parts" / "valve-manifold"
for _p in (_hw / "scripts", _repo / "tools", _hw / "reference" / "beduan-solenoid",
           _VM / "single-tray", _VM / "bag-circuit-tray", _VM / "source-select-tray",
           _VM / "nozzle-gate-tray",
           _hw / "reference" / "asse1022-assembly", _hw / "reference" / "multiplex-asse1022",
           _hw / "reference" / "gagira-reducing-coupling", _hw / "reference" / "jg-pp010822e",
           _hw / "reference" / "flare38-14ptc",
           _hw / "reference" / "water-split",
           _hw / "reference" / "neofit-flow-control",
           _hw / "reference" / "digiten-flow-sensor",
           _hw / "reference" / "seaflo-discharge-chain",
           _hw / "reference" / "seaflo-22-pump",
           _hw / "printed-parts" / "enclosure" / "drip-pan",
           _hw / "printed-parts" / "electronics",
           _hw / "printed-parts" / "electronics" / "pcba-tray",
           _hw / "printed-parts" / "zone-c" / "hopper-funnel",
           _hw / "printed-parts" / "enclosure" / "enclosure"):    # `enclosure`, imported in placed_funnel
    sys.path.insert(0, str(_p))
import hopper_funnel as _funnel          # noqa: E402  — its neck offset, so the drain rides the part
import _boxes                            # noqa: E402
import bag_circuit_tray as _bag          # noqa: E402
import source_select_tray as _src        # noqa: E402
import nozzle_gate_tray as _noz          # noqa: E402
import asse1022_assembly as _bfp         # noqa: E402  — its three terminals, carried to world
import multiplex_asse1022 as _mx         # noqa: E402  — the body's flow-axis height, the roll pivot
import water_split as _split             # noqa: E402  — its three 1/4" collets, the same way
import neofit_flow_control as _flowreg   # noqa: E402  — its two 1/4" collets and its stem
import digiten_flow_sensor as _digiten   # noqa: E402  — its two 1/4" PTC collets, coaxial on ±X
import seaflo_discharge_chain as _disch  # noqa: E402  — its barb tip and its 1/4" collet
import seaflo_22_pump as _seaflo         # noqa: E402  — its two head barbs
import beduan_solenoid as _vk            # noqa: E402  — V-K's two 1/4" QC collets
import drip_pan as _pan                  # noqa: E402  — its lift, its section, its rail offset
import module_tray as _mt                # noqa: E402  — the floor and standoff under every board
import pcba_tray as _pcba                # noqa: E402  — the board's outline, holes and thickness
sys.path.insert(0, str(_hw / "printed-parts" / "electronics" / "ac-hub"))
sys.path.insert(0, str(_hw / "reference" / "wago-221-413"))
sys.path.insert(0, str(_hw / "reference" / "teyleten-relay"))
sys.path.insert(0, str(_hw / "reference" / "ground-ring-stack"))
import ac_hub as _achub                  # noqa: E402  — the hub's own hold-down pattern
import wago_221_413 as _wago             # noqa: E402  — the lug body a pocket seats
import teyleten_relay as _relay_ref      # noqa: E402  — the relay's ends and its PCB
import ground_ring_stack as _gnd_ref     # noqa: E402  — the lug fan's own stack pitch
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "reference" / "meanwell-irm90"))
import _cold_core_interface as _cc       # noqa: E402  — the cap's deck-mount stations, in its own frame
import meanwell_irm90 as _psu_ref        # noqa: E402  — the PSU's section and its two terminal ledges


# --- Source STEPs ---------------------------------------------------------
FOAM_ASSEMBLY = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
COMP_SHROUD   = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
SOURCE_SELECT = _hw / "printed-parts" / "valve-manifold" / "source-select-tray" / "source-select-assembly.step"
BAG_CIRCUIT   = _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray" / "bag-circuit-assembly.step"
NOZZLE_GATE   = _hw / "printed-parts" / "valve-manifold" / "nozzle-gate-tray" / "nozzle-gate-assembly.step"
# Kamoer KPHM400 peristaltic pump assembly — a PP0308E 90° elbow on each of its two +Y outlets.
PUMP_ASSEMBLY = _hw / "reference" / "kamoer-kphm400" / "pump-assembly.step"
# JG PP0208E union tee — the pump-inlet junctions Y-C / Y-F, tube-hung.
TEE_CONNECTOR = _hw / "reference" / "tee-connector" / "tee-connector.step"
# JG PP0308E 90° elbow — turns the bag east / nozzle-gate west ports −Y toward the dividers.
ELBOW_CONNECTOR = _hw / "reference" / "elbow-connector" / "elbow-connector.step"
# JG PP2308E two-way divider (reference/y-divider — McMaster 51055K417 stand-in) — the actual
# Y connector for the pump-discharge junctions Y-D / Y-G. A trident: one stem and two parallel
# outlets 14.7 mm apart, all three ports on the one axis.
DIVIDER_CONNECTOR = _hw / "reference" / "y-divider" / "y-divider.step"
# The controller board alone, its underside on Z = 0: what the appliance carries, bolted
# to four boss columns of the foam cap. The tray it seats on at the bench is a different
# STEP and does not ship inside the machine.
PCBA_BOARD     = _hw / "printed-parts" / "electronics" / "pcba-tray" / "pcba-board.step"
# The Mean Well IRM-90-12ST, on its own four columns of the same cap.
MEANWELL_STEP  = _hw / "reference" / "meanwell-irm90" / "meanwell-irm90.step"
# Teyleten relay #1 — the compressor's 120 VAC hot switch, on four more columns.
RELAY_STEP     = _hw / "reference" / "teyleten-relay" / "teyleten-relay.step"
# The AC hub with its three Wago 221-413 lever nuts seated.
AC_HUB         = _hw / "printed-parts" / "electronics" / "ac-hub" / "ac-hub-assembly.step"
# The chassis-ground ring-terminal stack — the bolted lug fan that is the ground bus.
# Its own frame puts Z = 0 on the landing surface, the shank running −Z into the insert.
GND_STACK      = _hw / "reference" / "ground-ring-stack" / "ground-ring-stack.step"
DC_DIST        = _hw / "reference" / "dc-dist-block" / "dc-dist-block.step"
MQ6_STEP       = _hw / "reference" / "mq6-gas-sensor" / "mq6-gas-sensor.step"
DERPIPE_STEP   = _hw / "reference" / "derpipe-co2-inlet" / "derpipe-co2-inlet.step"
# The CO2 chain's two bodies, both authored +Y = flow. The GASHER check's female
# socket is at −Y and its male stub at +Y, so it threads straight onto the
# DERPIPE's stub; the WR1110 secondary regulator is female both ends and takes
# a PP010822E at each (reference/gasher-check-valve, reference/wr1110-regulator).
GASHER_STEP    = _hw / "reference" / "gasher-check-valve" / "gasher-check-valve.step"
WR1110_STEP    = _hw / "reference" / "wr1110-regulator" / "wr1110-regulator.step"
# The DIGITEN FL-S402B Hall-effect turbine meter, inline on the carb-water riser.
# Its own frame is +X = flow, the two 1/4" PTC collets coaxial on ±X, the rotor
# spinning about Y and the pigtail boss leaving +Z (reference/digiten-flow-sensor).
DIGITEN_STEP   = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"
# The ASSE 1022 chain as one piece: PP010822E → GAGIRA coupling → Multiplex 19-0897
# → flare38-14ptc (3/8" flare → 1/4" PTC), plus the clear-PVC vent stub. Its own
# frame is +X = flow, the Multiplex inlet at x 0, the vent running −Z; the outlet
# leaves at 1/4" OD (reference/asse1022-assembly).
ASSE1022_STEP  = _hw / "reference" / "asse1022-assembly" / "asse1022-assembly.step"
JG_BULKHEAD    = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"
IEC_C14        = _hw / "reference" / "iec-c14-inlet" / "iec-c14-inlet.step"
# The SeaFlo 22-series diaphragm pump, 190 × 112 × 61 with its feet: the water
# deck's floor plan. Its own frame is +X = motor axis, the head at −X; the two
# 3/8" barbs leave the head's ±Y side faces (reference/seaflo-22-pump).
SEAFLO_STEP    = _hw / "reference" / "seaflo-22-pump" / "seaflo-22-pump.step"
# The water split — a 1/4" PTC union tee (PP0208E) on the ASSE's 1/4" outlet,
# feeding V-K and the flavor tap. Its own frame is the run along ±Y, the branch
# on −X (reference/water-split).
WATER_SPLIT_STEP = _hw / "reference" / "water-split" / "water-split.step"
# The flow regulator — the neoFit ABCVU44 needle valve on the flavor tap, throttling
# the manifold's feed to its low working pressure. Its own frame is +X = flow, the
# needle stem on +Z (reference/neofit-flow-control).
FLOWREG_STEP   = _hw / "reference" / "neofit-flow-control" / "neofit-flow-control.step"
# The pump's discharge chain — MAACFLOW barb + GASHER check + PP450822E, made up as one
# piece. Its own frame is +Z = flow with the barb tip at Z = 0, water running DOWN it
# (reference/seaflo-discharge-chain).
DISCH_CHAIN_STEP = _hw / "reference" / "seaflo-discharge-chain" / "seaflo-discharge-chain.step"
# The drip pan — the printed catch basin under the ASSE 1022's atmospheric vent,
# with the moisture plate lying in it. Its own frame is the basin upright, floor at
# Z = 0 (printed-parts/enclosure/drip-pan).
DRIP_PAN_STEP  = _hw / "printed-parts" / "enclosure" / "drip-pan" / "drip-pan.step"
# The rail pair the basin's floor flanges ride, VHB'd to the foam-cap lid. Placed
# from the basin by the part's own `rail_offset()`, so the two cannot drift apart.
DRIP_RAILS_STEP = _hw / "printed-parts" / "enclosure" / "drip-pan" / "drip-pan-rails.step"
# V-K — the Beduan 12 V NC solenoid, the water-supply fill/shutoff valve
# (reference/beduan-solenoid). Its own frame is +Y = flow, the arrow the outlet.
BEDUAN_STEP    = _hw / "reference" / "beduan-solenoid" / "beduan-solenoid.step"

# --- Primitive dimensions + placement anchors ----------------------------
# Condenser+fan and the SeaFlo pump are packed as primitive boxes (dimensions
# below); the rest are placement anchors — nominal dims that position the
# STEP-loaded parts against their datums.
# Condenser + fan harvested from the donor ice maker, with the donor's own
# factory filter-drier + capillary-tube subassembly brazed to its outlet and
# kept in service (hardware/reference/ice-maker/README.md "Filter-drier" — the
# small donor drier, NOT the shelf-spare Supco SUD8358): one harvested block,
# so the drier is not packed as its own solid. The block lies tipped on its
# back (a −90° turn about X): FACE_A (178, matching the compressor envelope)
# runs along Y as the front block's depth, FACE_B (151) stands as the height —
# topping out level with the compressor, so the whole column above the floor
# stratum stays open. The airflow axis rides the tip unchanged: the fan +
# finstack stack depth, calipered [56 mm](CONDENSER_AIRFLOW) combined, along X.
CONDENSER_FACE_A, CONDENSER_FACE_B, CONDENSER_AIRFLOW = 178.0, 151.0, 56.0
# Front block (Zones C/D) Y depth — the cold core (Zone A) seats behind it, and
# everything the foam-cap top carries rides with it. The condenser block stands
# CONDENSER_FACE_A of this; the rest is the column between the manifold stack
# and the core.
FRONT_DEPTH = 182.0
# The corridor a bag line falls down: one 1/4" line wide with a lane clearance
# either side. Each line leaves the core at its own shell-side bore and falls in
# its own column, down the recess in the manifold stack's aft profile, so the
# lane is measured there rather than across the stack's whole width.
BAG_FALL_CORRIDOR = 5.65 + 6.35 + 5.65
# The manifold stack's aft face stands this far behind SRC_SEL_POS, and holds
# this much air off the cold core's front face. What stands in that air is the
# discharge chain, hanging its 17.0 mm of Y depth down the one column deep
# enough to take it — the stack's own aft face and the core's front face are the
# two walls of that column.
STACK_AFT_REACH = 46.44
STACK_CORE_GAP = 18.01
# The manifold stack's own origin Y, and the deck's datum. The pump row, the
# dividers and the hopper's drain all stand off it, so the column the core
# pushes on travels as one piece.
DECK_Y = FRONT_DEPTH - STACK_CORE_GAP - STACK_AFT_REACH
# The SeaFlo lies motor-axis along X across the service bay, its base flat on the
# foam cap. The head's two barbs leave its ±Y faces: the suction faces north (+Y)
# up to the split feeding it, the discharge faces south (−Y) down to the cold
# core's water-in. It stands at the cap's FRONT EDGE, its front face on the foam's
# y=200: forward is what opens the aft strip and the west column into one contiguous
# void, and the electronics shelf (power assembly, PCBA) has no other plane in this
# bay. The north suction still clears the ASSE chain by a wide margin, and the aft
# strip it leaves is deeper than the drip pan's floor needs to take the moisture
# plate's long edge flat. Its X keeps the discharge barb on the chain's own column,
# so the hose leaves the molded barb straight south and turns down the corridor with
# no offset to take up — the discharge hose's bend radius is a gate, so that matters.
SEAFLO_YAW = 180.0
SEAFLO_POS = (189.5, FRONT_DEPTH + 49.0)   # front face on the cap's front edge, east face on its east edge
# The ASSE 1022 chain lies along +X in the service bay's AFT STRIP, over the
# foam-cap top and behind the pump. Flow runs west to east: the 1/4" PTC inlet at
# the west end takes its pigtail off the rear-panel water bulkhead, and the 1/4"
# PTC at the east end starts the 1/4" LLDPE run to the split. The chain is ROLLED
# about its own flow axis, so the vent stub leaves the body pointing aft and down
# and the body's underside rides clear of the pan below it.
#   The roll turns about the line the two fittings sit on, so the water line holds
# still through it: `ASSE1022_AXIS` is that line, and `asse_pos()` carries the
# part's own origin around it. Move the roll and the tube ports do not move.
#   PROVISIONAL: the chain's envelope comes from the reference model, which divides
# the Multiplex spec sheet rather than measuring the five parts on the shelf.
ASSE1022_AXIS = (102.0, FRONT_DEPTH + 145.5, 314.0)   # the flow axis, in world
ASSE1022_YAW = 0.0
ASSE1022_ROLL = 45.0
# The drip pan is not posed. In X the basin hangs EAST of the vent column, the tip
# landing `DRIP_VENT_INSET` inside its west outer face — the aft strip's west end is the
# controller board's, and what the basin does not take there is the board's connector
# lane. The tip's X is fixed by the chain's own length along its flow axis and does not
# move with the roll, which is the provisional half of that pose; the inset it leaves is
# what absorbs a re-roll's swing in Y. In Y the basin's back face lands on the foam cap's
# rear edge, the face it will draw out through. Its section and its lift are the part's
# own — `drip_pan_seat()` re-derives that lift from the placed chain's underside.
DRIP_PAN_X, DRIP_PAN_Y = _pan.PAN_X, _pan.PAN_Y
DRIP_VENT_INSET = 14.0   # basin west outer face to the vent column
# V-K — the water-supply fill/shutoff solenoid (Beduan 12 V NC): DOWNSTREAM of the
# ASSE 1022, between the split and the SeaFlo suction. Closed, it stops all water
# reaching the carbonator. Its own frame is +Y = flow (arrow toward the outlet),
# turned a half turn so it STANDS ALONG Y in the aft strip's east void, east of every
# rear-panel body: the inlet looks north at the water that comes up to it, the outlet
# south down the open lane at the suction, and its port plane is the suction's own. It
# stands on a short cradle off the foam cap (clearances in the scorecard).
#   Along Y and not along X because the valve is 59 mm between collets: laid across the
# strip it needs that length PLUS the split's body east of it, and the +X wall arrives
# first. Stood down the strip, the length runs into depth the strip has and the column
# the nozzle lanes need stays open beside it.
BEDUAN_YAW = 180.0
BEDUAN_POS = (264.0, FRONT_DEPTH + 142.5, 274.1)   # base centre on a cradle above the cap
# The controller board and the PSU, each bolted to four boss columns of the foam cap.
# Neither is posed here: the cap owns its deck-mount stations and `deck_mount()` carries
# them to world, so the body, its connector map and the column it stands on move together.
# Both lie flat and no tray floor stands between them and the cap: the board's underside on
# its column tops, standing through the lid, and the PSU's flat on the lid itself.
#   THE BOARD lies ACROSS the cap's FRONT in its own frame's orientation, its short side
# into the face, its front columns one `deck_mount_cap_gap` off the front cavity wall. Its
# twelve top-entry wafers plug from the bay's own opening above; the J10 12 V throats look
# WEST down the open lane beside it.
#   THE PSU takes the AFT STRIP, west of the drip basin, laid ACROSS the strip, its rear
# columns the same gap off the cap's rear corner boss. Its AC end faces the C14 inlet's own
# column above it.
#   BETWEEN THEM runs the power strip: the AC hub across the lid's pour hole, relay #1
# behind it, the ground stack east of the relay, each on columns of the same cap.
#   The two nozzle lanes cross the deck the far side of the pump; no body here shares a deck
# with them.
PCBA_YAW = 180.0
PSU_YAW = 90.0
# Relay #1's hole rectangle IS the cap's `relay-1` pitch, so it lies along the strip
# untured: COM/NO screw block EAST beside the ground stack, under the C14's own column
# where the shroud's SJOOW lead arrives; VCC/GND/IN header WEST down the lane the board's
# J5 loom crosses.
RELAY_YAW = 0.0
# The split lies UNDER V-K, in the band between the foam cap and V-K's cradle — the one
# place in the strip's east void with a footprint free once the valve is standing in it.
# Its run carries the ASSE feed across the void — in at the WEST face off water-2, on at
# the EAST to the flow regulator and V-A — and its branch turns V-K's share NORTH, where
# water-3 takes it up to the valve's inlet. The branch has to point north and the run has
# to lie along X, which is one turn about Z and one about its own run axis: the roll is
# what puts the branch on the far side of the run from where the yaw alone would leave it.
SPLIT_YAW = 270.0
SPLIT_ROLL = 180.0
SPLIT_POS = (257.0, FRONT_DEPTH + 145.5, 260.4)   # centre; its port plane, standing on the cap under V-K
# The flow regulator (neoFit ABCVU44) sits inline on the split's flavor run, in the band
# between the hopper funnel's basin and the cap's front edge — the pump fills the deck behind
# it, and this band is the only length of open air on the flavor run's own X. Its needle stem
# stands up where a screwdriver reaches it over the deck. Its own frame is +X = flow; yawed so
# the flow runs south, in at the north face off fluid-1 and on at the south face into the fall.
# It sits on V-A's own X, so the line it feeds drops straight into that up-facing collet.
# The regulator's outlet stands this far north of V-A's up-facing collet — the leg fluid-2
# turns its bend in — on a body reaching FLOWREG_HALF_Y from its centre to either port.
FLOWREG_DROP = 6.72
FLOWREG_HALF_Y = 23.0
FLOWREG_YAW = 270.0
# The discharge chain hangs vertically in the bag-fall corridor, just clear of the cold
# core's front face — the only column deep enough to stand its 83.4 mm. The pump's barbs
# are molded into the head, so a stub of 3/8" braided PVC is the only thing that can leave
# the discharge: it runs south off the barb, turns down over the cap's front edge, and
# clamps onto this chain's barb, which is where the 3/8" ends. Placed unturned — its own
# frame already runs the water down. Its X rides the pump's discharge, not a number of its
# own: the hose turns at R15.9, so any offset between the two costs two tangent lengths of
# strip the bay does not have. The corridor bounds this chain in Y, not in X.
DISCH_CHAIN_POS = (SEAFLO_POS[0] + 36.6, FRONT_DEPTH - 10.0, 265.0)   # the barb tip; the collet hangs LENGTH below it
# The funnel's placement: its collar-rect centre in plan, plus a rotation
# about its own Z. This is the CENTRE OF THE TOP-WALL FRAME — the basin sits
# the same `hopper_funnel.brim_margin` off the display gusset, the corner pod,
# the front ledge and the cold core's band alike, so the brim reads square in
# its opening from above instead of crowding one edge. Plan area — not depth —
# carries its volume: the shallow floor (hopper_funnel.ramp_angle) and the
# centred spout's short runs keep the drain high, hanging over the pump row
# with the segment-4 fall banked in open air below it (the pumps' `clear`
# keep-out holds that drop corridor open). With the spout centred the
# rotation picks nothing; 0 keeps the frame axis-aligned. The static
# funnel (zone-c/hopper-funnel, local frame) seats with its brim underside
# on the box's outer top; enclosure.py cuts the top-wall opening from this
# same centre + the funnel's own collar dims, and asserts both the collar and
# the brim that overhangs it land inside that frame. Its depth stands off the
# deck datum: the drain feeds V-B on the manifold stack, so the spout holds its
# station over that collet as the column travels, and the collar's Y is sized to
# the top wall the move leaves it (hopper_funnel `collar_d`).
FUNNEL_CX, FUNNEL_CY = 193.75, DECK_Y - 43.05
FUNNEL_ROT = 0.0
# The source-select assembly is the stack's anchor and its FLOOR: local
# origin (cell centre, valve mounting plane) in world, rotated 180° about Z,
# which keeps the plate down and the valves up while swapping its ends —
# V-A/V-B east, V-C/V-D west. Its east collets face UP, where both the lines
# that feed them arrive from: the tap-water chain off the rear bulkhead into
# V-A, and the hopper funnel's drain into V-B, a fall the height of the
# stack. Its tall walls' back faces stand
# BAG_FALL_CORRIDOR off the cold core's front face (the `clear foam-assembly`
# rule): that open Y is the lane both bag lines fall down to the reservoir
# ports low on the core, and the only one that reaches reservoir-A, which sits
# behind the condenser. The aft-station elbow columns set how far forward
# the back pieces' Y-seam machinery must stop (enclosure _dims y_elbows). In X
# the full-width foam behind the stack pins both interior walls; the stack itself
# rides a few millimetres inboard of each — its −X outlet-elbow column (and the
# junction tees below) clear the −X wall's seam furniture, its +X elbows clear the
# +X wall — so the enclosure seam machinery runs unbroken there (no wall relief).
SRC_SEL_POS = (143.0, DECK_Y, 167.8)
# The bag-circuit assembly rides INVERTED on top of it — rotated 180° about Y,
# seated wall-tops-to-wall-tops on the source tray's stacking walls (a
# declared contact), both trays' walls meeting at z 227.8 — which lands each
# pump-inlet Tee's two valve ports on ONE side of the machine (V-E/V-H west,
# V-F/V-I east) and turns the west collets DOWN into the junction column and
# the east collets UP toward the pump row that discharges into them. The X
# slide puts its west elbow column on the source tray's: the two trays' elbow
# corners disagree by the junction aim's `junction_dx`, because each west
# elbow is rolled off its port axis to face the other (bag_circuit_tray
# `_junction_aim`). Both bag branches are rolled about their runs to the one
# `bag_fall_aim` (bag_circuit_tray), aimed DOWN the fall they feed, so each leaves
# the tray near vertical rather than sideways, clear of the hug walls, and turns
# along the corridor to its own reservoir. The floor stratum below stays open under the stack —
# the under-stack corridor.
_SRC_CORNER_X = _src.valve_x + (_bag.port_half + _bag.elbow_reach) * (_src._ox / _src._on)
_BAG_CORNER_X = _bag.valve_x + _bag.port_half + _bag.elbow_reach
JUNCTION_SLIDE = _SRC_CORNER_X - _BAG_CORNER_X - _bag.junction_dx
STACK_PITCH_Z = 2 * _bag.wall_top_z       # wall top to wall top, the stack contact
BAG_CIRCUIT_POS = (SRC_SEL_POS[0] - JUNCTION_SLIDE,
                   SRC_SEL_POS[1],
                   SRC_SEL_POS[2] + STACK_PITCH_Z)

# The nozzle-gate assembly (Tray 3 — V-G/V-J, every port bare) rides INVERTED
# in the pocket EAST of the bag assembly: the same 180°-about-Y hang and the
# same second story — its hanging wall tops reach the source tray's wall-top
# plane, though the source's east wall slabs (which follow its aimed valves)
# stop just outboard of them, so the tray floats in the pocket until its
# holder. The shared story lands its ports on the bag tray's own port plane,
# inner ports facing west at the bag east bank across the pocket, outer
# (nozzle-outlet) ports facing east, inset well off the +X wall (GATE_WALL_INSET)
# so their outlet elbows have room to turn aft to the rear umbilical. The X slide
# holds the gate one clearance east of the bag tray's bare V-F/V-I port tips,
# opening the pocket the discharge fittings (bag + gate outlet elbows and the
# Y-connector tees) settle into between the two banks.
TEE_BODY_CLEAR = 2.5
# The gate is anchored on its own X (it does NOT ride the bag/source slide): its
# west inner ports and outlet elbows stay put while the bag and its own outlet
# elbows translate, so the two elbow banks face across the pocket at the
# Y-connector tees hung between them.
_GATE_ANCHOR_BAG_X = 144.0 - JUNCTION_SLIDE
# The gate sits inset from the +X wall: GATE_WALL_INSET is how far its bare east
# ports (V-G-O/V-J-O, the nozzle outlets) stand off the wall, opening the pocket
# their outlet elbows turn aft into on the way to the rear umbilical. The foam
# pins the +X wall at the full interior width regardless, so this only insets the
# gate — it does not shrink the box. Bounded west by the source-select east bank
# and the bag's east discharge elbows (the scorecard's clearance floor).
GATE_WALL_INSET = 11.0
# The gate does NOT take STACK_PITCH_Z: that pitch is wall-top to wall-top, and this
# tray seats on its FLOOR, not its walls (`_flip_x_in_place` below turns it valves-up).
# So its origin rides the source tray's wall top plus its OWN wall height — shorter than
# the stacked trays', since its wall tops face open air (`_noz.wall_top_z`).
NOZZLE_GATE_POS = (_GATE_ANCHOR_BAG_X + 2.0 * _bag.port_half + _bag.tee_branch_reach
                   + _bag.tee_radius + TEE_BODY_CLEAR - GATE_WALL_INSET,
                   SRC_SEL_POS[1],
                   SRC_SEL_POS[2] + _src.wall_top_z + _noz.wall_top_z)

# The pump row: both Kamoer KPHM400 assemblies (P-A west, P-B east) lying
# depth-along-X ahead of the tray stack, in ONE pose — a −90° turn about Y
# lays the depth axis west (motor at −X), then a +90° roll about X turns
# the outlet face up, so each pump's two elbows stand on its +Z face, legs
# turning west over the head, free collets facing −X at the row's crest.
# The POS tuples are the pump's local origin (base-plate bore-opening
# face, case centre) in world; the row rides at the tray stack's height,
# P-A dropped off it by the display clearance below (the row's stack ties
# are z-tight otherwise — the two lift together):
#   * P-A: head nose-in at mid-row, the segment-4 drop corridor under the
#     funnel's centred drain held open over it (the `clear hopper-funnel`
#     rule), the long body crossing the ±X wall corners well above the
#     front Z-seam's boss-pod band (which reaches ~14 mm inboard below the
#     seam), aft elbow one clearance ahead of the inverted bag tray's Y-E
#     bag branch (the `near bag-circuit-assembly` rule). It rides below P-B
#     because its FORWARD outlet elbow stands under the display housing's
#     back plane: the facet is flush to the front wall, so that plane cuts
#     down through the row's crest and the elbow drops to pass beneath it.
#   * P-B: the same pose one slot east — head at the east end, under the
#     funnel's floor — and slid forward, its aft elbow threading ahead of
#     the source-select east bank's walls (the `clear
#     source-select-assembly` rule); its row tie is the nose gap to P-A
#     (the `near pump-a` rule).
PUMP_A_POS = (89.62, SRC_SEL_POS[1] - 39.55, 190.31)
PUMP_B_POS = (222.50, SRC_SEL_POS[1] - 46.00, 192.31)

# The pump-inlet union tees (fluid topology Y-C / Y-F) hang in the junction
# column between the trays' facing west collets. Both elbows are rolled off
# their port axes to aim at each other (bag_circuit_tray `_junction_aim`), so
# the column does not stand vertical — it leans off Z, and each tee is turned
# to stand on the lean: its RUN collinear with the pair of collets it butts, so
# segments 9/10 and 19/20 are straight tube with no bend anywhere and one stub
# at each end. Its BRANCH starts perpendicular-east, then rolls about the run
# axis by JUNCTION_ROLL to swing forward (−Y), into the open band ahead of the
# pump row where its suction leg (segments 11/21) picks it up and carries it over
# pump A — a spin about the run leaves the two run ports untouched, so the
# source/bag legs stay straight. Tube-hung PTC fittings, carried by their lines:
# no tray, no holder. Every number derives from the trays' own layout, so a tray
# move carries the tees with it.
JUNCTION = {                      # tee → the (source, bag) collets its run butts
    "tee-y-c": ("VC", "VE"),
    "tee-y-f": ("VD", "VH"),
}
JUNCTION_ROLL = {                 # extra roll of a tee about its run axis: branch swung forward off the pump row
    "tee-y-c": -90.0,             # fully −Y: branch faces straight into the open band ahead of the pumps
    "tee-y-f": -55.0,             # −Y-dominant, canted east just enough to thread its run past tee-y-c
}
JUNCTION_LIFT = {                 # slide a tee's centre this far up its run toward the bag port, raising its
    "tee-y-c": 7.0,              # branch exit so the suction stem leaves gently (fluid-11 needs no sharp climb)
}


def asse_pos():
    """The chain's translation — the part origin that holds `ASSE1022_AXIS` on the
    flow axis through the roll. The roll turns about the part's own origin, which
    sits `BODY_CENTER_Z` under that axis, so the origin swings around it."""
    t = math.radians(ASSE1022_ROLL)
    z = _mx.BODY_CENTER_Z
    return (ASSE1022_AXIS[0],
            ASSE1022_AXIS[1] + z * math.sin(t),
            ASSE1022_AXIS[2] - z * math.cos(t))


def _face_of(axis):
    """The enclosure port convention (x±/y±/z±) for an outward axis. A rolled port
    points between two of them; it is named for the one it leans on hardest, ties
    going to the later axis, so a vent turned off vertical still reads as facing
    down rather than raising."""
    ax = [round(float(c), 9) + 0.0 for c in axis]
    i = max(range(3), key=lambda k: (abs(ax[k]), k))
    return "xyz"[i] + ("+" if ax[i] > 0 else "-")


def bfp_terminal(name):
    """One of the ASSE 1022 assembly's three terminals in world: `(pos, face)`.

    The reference module owns each station — `tube_in` off the PP010822E's own port,
    `tube_out` off the flare38-14ptc's 1/4" collet, `vent_tip` at the stub's open end —
    and this carries them through the same yaw + roll + translation the solid takes, in
    that order, so a length changed anywhere in that chain moves the world port with it.
    The two tube ports sit ON the roll axis, so the roll leaves them where they are."""
    pos, axis = {"tube-in": _bfp.tube_in, "tube-out": _bfp.tube_out,
                 "vent-tip": _bfp.vent_tip}[name]()
    for turn in (lambda v: _yaw_z(v, ASSE1022_YAW), lambda v: _roll_x(v, ASSE1022_ROLL)):
        pos, axis = turn(pos), turn(axis)
    return tuple(p + o for p, o in zip(pos, asse_pos())), _face_of(axis)


def placed_asse():
    """The ASSE 1022 chain seated in world, the way `_build` seats it."""
    return _rot(_rot(_load(ASSE1022_STEP), (0, 0, 1), ASSE1022_YAW),
                (1, 0, 0), ASSE1022_ROLL).translate(asse_pos())


def asse_underside():
    """The lowest point anywhere on the placed chain — the ceiling over the drip pan.
    Unrolled that is the vent stub's tip; rolled it is a body corner, and the tip
    stands above it."""
    return placed_asse().BoundingBox().zmin


def split_terminal(name):
    """One of the water split's three 1/4" collets in world: `(pos, face)`.

    The reference module owns each station — `supply` and `to_flavor` (the run, the
    ASSE feed carried straight through) and `to_vk` (the branch). The yaw that turns
    the tee turns its three ports with it."""
    pos, axis = {"supply": _split.supply, "to-vk": _split.to_vk,
                 "to-flavor": _split.to_flavor}[name]()
    pos, axis = _roll_x(pos, SPLIT_ROLL), _roll_x(axis, SPLIT_ROLL)
    pos, axis = _yaw_z(pos, SPLIT_YAW), _yaw_z(axis, SPLIT_YAW)
    face = {(-1.0, 0.0, 0.0): "x-", (1.0, 0.0, 0.0): "x+", (0.0, 1.0, 0.0): "y+",
            (0.0, -1.0, 0.0): "y-", (0.0, 0.0, 1.0): "z+", (0.0, 0.0, -1.0): "z-"}[
        tuple(round(float(c), 9) + 0.0 for c in axis)]
    return tuple(p + o for p, o in zip(pos, SPLIT_POS)), face


def flowreg_terminal(name):
    """One of the flow regulator's two 1/4" collets in world: `(pos, face)`. Its own
    frame is +X = flow; the yaw that turns the valve turns its ports with it."""
    pos, axis = {"inlet": _flowreg.inlet, "outlet": _flowreg.outlet}[name]()
    pos, axis = _yaw_z(pos, FLOWREG_YAW), _yaw_z(axis, FLOWREG_YAW)
    face = {(-1.0, 0.0, 0.0): "x-", (1.0, 0.0, 0.0): "x+", (0.0, 1.0, 0.0): "y+",
            (0.0, -1.0, 0.0): "y-", (0.0, 0.0, 1.0): "z+", (0.0, 0.0, -1.0): "z-"}[
        tuple(round(float(c), 9) + 0.0 for c in axis)]
    return tuple(p + o for p, o in zip(pos, flowreg_pos())), face


def digiten_terminal(name):
    """One of the flow meter's two 1/4" PTC collets, or its pigtail boss tip, in world:
    `(pos, face)`. Placed unturned, so each station is its own frame's plus the body
    centre — including the boss height, which is the reference part's and not a number
    kept here."""
    pos, axis = {"inlet": _digiten.inlet, "outlet": _digiten.outlet,
                 "wire-exit": _digiten.wire_exit}[name]()
    face = {(-1.0, 0.0, 0.0): "x-", (1.0, 0.0, 0.0): "x+", (0.0, 0.0, 1.0): "z+"}[
        tuple(round(float(c), 9) + 0.0 for c in axis)]
    return tuple(p + o for p, o in zip(pos, DIGITEN_POS)), face


def disch_terminal(name):
    """One of the discharge chain's two ends in world: `(pos, face)`. Placed unturned,
    so each station just shifts by DISCH_CHAIN_POS."""
    pos, axis = {"barb-tip": _disch.barb_tip, "tube-port": _disch.tube_port}[name]()
    face = {(0.0, 0.0, 1.0): "z+", (0.0, 0.0, -1.0): "z-"}[
        tuple(round(float(c), 9) + 0.0 for c in axis)]
    return tuple(p + o for p, o in zip(pos, DISCH_CHAIN_POS)), face


def flowreg_pos():
    """The flow regulator's centre: V-A's own X and Y, so the line it feeds falls straight into
    that up-facing collet, standing FLOWREG_DROP north of the collet on its own body half-length;
    and the split's Z, which is the LANE UNDER THE PUMP — the gap the pump's bracket leaves
    between its body and the cap runs the bay's whole width, and the flavor run crosses the
    machine along it without ever climbing into the deck the pump fills."""
    collet, _ = src_collet("VA")
    return (collet[0], collet[1] + FLOWREG_DROP + FLOWREG_HALF_Y, SPLIT_POS[2])


_FOAM_TOP_CACHE = None


def foam_cap_top():
    """The foam cap's LID outer face — the water deck's floor, the Z the pump's base sits
    on, and the Z the PSU's does. The foam assembly's own top is higher: the board's
    deck-mount columns stand `deck_mount_proud()` through the lid, and the board rides
    their tops."""
    global _FOAM_TOP_CACHE
    if _FOAM_TOP_CACHE is None:
        _FOAM_TOP_CACHE = (_load(FOAM_ASSEMBLY).BoundingBox().zlen
                           - _cc.deck_mount_proud())
    return _FOAM_TOP_CACHE


def deck_mount(name):
    """A cap deck mount in world: `(centre, stations, top_z)`. The cap is placed spun a
    half turn about its own centre, so a station at `(px, py)` in the cap's frame lands
    at `(cap_cx - px, cap_cy - py)`; `top_z` is where the module's underside seats — the
    column tops of a mount that stands through the lid, the lid's own face of one that
    stops beneath it. The cap owns the stations — this only carries them."""
    fb = _load(FOAM_ASSEMBLY).BoundingBox()
    # The pack seats the assembly by its bbox min at (0, FRONT_DEPTH, 0).
    cx, cy = fb.xlen / 2.0, FRONT_DEPTH + fb.ylen / 2.0
    pts = tuple((cx - px, cy - py) for px, py in _cc.deck_mount_xy(name))
    ctr = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    return ctr, pts, foam_cap_top() + _cc.deck_mount_standoff(name)


_FOAM_FRAME = None


def foam_shell_port(x, z, y=None):
    """A point in the foam SHELL's own frame, carried into world.

    The shell IS the foam assembly's frame — the caps stack around it without
    moving it — and the pack seats that assembly by its bbox min at
    (0, FRONT_DEPTH, 0). `y` defaults to the shell's −Y outer face,
    where every front penetration opens. A port that reads its X and Z off
    the cold core's own constants through this moves when the bore moves,
    instead of being retyped after it."""
    global _FOAM_FRAME
    if _FOAM_FRAME is None:
        fb = _load(FOAM_ASSEMBLY).BoundingBox()
        _FOAM_FRAME = (-fb.xmin, FRONT_DEPTH - fb.ymin, -fb.zmin)
    dx, dy, dz = _FOAM_FRAME
    if y is None:
        y = -_cc.outer_shell_y_length / 2.0
    return (x + dx, y + dy, z + dz)


def drip_pan_seat():
    """The Z the drip pan's floor stands at — the top face of its printed rails.

    The printed rail sets the seat; this measures the air it leaves between the
    basin's rim and the placed chain's underside, and raises outside the band
    `drip_pan.VENT_GAP` .. `+ VENT_GAP_SLACK` — under it the stub is crowded, over
    it the deck below the pan has gone to waste."""
    seat = foam_cap_top() + _pan.RAIL_LIFT
    under = asse_underside()
    gap = under - (seat + _pan.PAN_Z)
    lo, hi = _pan.VENT_GAP, _pan.VENT_GAP + _pan.VENT_GAP_SLACK
    if not (lo - 1e-6 <= gap <= hi + 1e-6):
        raise ValueError(
            f"drip-pan rim to chain: the placed chain's underside at z={under:.4f} over a "
            f"cap top of {foam_cap_top():.4f} leaves {gap:.4f} mm above a {_pan.PAN_Z:g} mm "
            f"basin on a {_pan.RAIL_LIFT:g} mm rail — outside {lo:g}..{hi:g}. Reprint the "
            f"rail at {under - _pan.PAN_Z - foam_cap_top() - lo:.2f} mm or re-pose the chain.")
    return seat


def seaflo_terminal(name):
    """One of the SeaFlo's two head barbs in world: `(pos, face)`. They leave the
    head's ±Y side faces, so the yaw that turns the pump turns them with it."""
    pos, axis = {"suction": _seaflo.suction, "discharge": _seaflo.discharge}[name]()
    pos, axis = _yaw_z(pos, SEAFLO_YAW), _yaw_z(axis, SEAFLO_YAW)
    face = {(-1.0, 0.0, 0.0): "x-", (1.0, 0.0, 0.0): "x+", (0.0, 1.0, 0.0): "y+",
            (0.0, -1.0, 0.0): "y-", (0.0, 0.0, 1.0): "z+", (0.0, 0.0, -1.0): "z-"}[
        tuple(round(float(c), 9) + 0.0 for c in axis)]
    origin = (SEAFLO_POS[0], SEAFLO_POS[1], foam_cap_top())
    return tuple(p + o for p, o in zip(pos, origin)), face


def seaflo_low_crown():
    """The pump's LOW END: `(crown_z, (x0, x1))` in world — the top face of the pressure
    switch and the X window it spans.

    The pump is not one height. The motor can, the head block and the head's top boss all
    stand to `OVERALL_H`; the switch stops well under them, at `SWITCH_Z1`, over its own
    length. That step is the only plane a line can cross the pump on and still have air
    over it — the nozzle lanes take it. Carried through SEAFLO_YAW the way the barbs are,
    so the window follows the pose rather than assuming one."""
    ends = [_yaw_z((x, 0.0, 0.0), SEAFLO_YAW)[0] + SEAFLO_POS[0]
            for x in (_seaflo.X_SWITCH_FACE, _seaflo.X_HEAD_END)]
    return foam_cap_top() + _seaflo.SWITCH_Z1, (min(ends), max(ends))


def vk_terminal(name):
    """One of V-K's two 1/4" QC collets in world: `(pos, face)`. The Beduan's own
    frame is +Y = flow (arrow = outlet); the yaw lays it along X, so the inlet looks
    east at the split's branch and the outlet west at the suction."""
    pos, axis = {"inlet": _vk.inlet, "outlet": _vk.outlet}[name]()
    pos, axis = _yaw_z(pos, BEDUAN_YAW), _yaw_z(axis, BEDUAN_YAW)
    face = {(-1.0, 0.0, 0.0): "x-", (1.0, 0.0, 0.0): "x+", (0.0, 1.0, 0.0): "y+",
            (0.0, -1.0, 0.0): "y-", (0.0, 0.0, 1.0): "z+", (0.0, 0.0, -1.0): "z-"}[
        tuple(round(float(c), 9) + 0.0 for c in axis)]
    return tuple(p + o for p, o in zip(pos, BEDUAN_POS)), face


def psu_terminal(name):
    """One of the PSU's two terminal blocks in world: `(pos, face)`. The Mean Well's own
    frame puts the AC primary on +Y and the DC secondary on −Y, each a screw block standing
    on its stepped end ledge; `PSU_YAW` carries them, and both land face-up, which is how a
    ferrule goes under a captive screw. The yaw is chosen by this: it puts the AC end on the
    C14 inlet's own column, so the energized run is the short one."""
    ctr, _pts, top = deck_mount("psu")
    sy = {"ac-in": 1.0, "dc-out": -1.0}[name]
    x, y, _ = _yaw_z((0.0, sy * (_psu_ref.length / 2.0 - 6.0), 0.0), PSU_YAW)
    return ((ctr[0] + x, ctr[1] + y, top + _psu_ref.ledge_h + 7.0), "z+")


def ac_hub_lug(pole):
    """One of the AC hub's three Wago lever nuts in world: `(pos, face)`. H / N / G run
    west to east along the row. Each lug stands on its butt end in its well, so the wire
    ports face up off its top face and its levers work off the −Y face below them."""
    ctr, _pts, top = deck_mount("ac-hub")
    places = tuple(_achub.LAYOUT.mount_places)
    mx = sum(p[0] for p in places) / len(places)
    my = sum(p[1] for p in places) / len(places)
    lx, ly = _achub.LAYOUT.wago_places[{"H": 0, "N": 1, "G": 2}[pole]]
    return ((ctr[0] + lx - mx, ctr[1] + ly - my,
             top + _achub.floor_t + _wago.depth), "z+")


def relay_terminal(name):
    """One of relay #1's two terminal groups in world: `(pos, face)`. The Teyleten's own
    frame puts the COM/NO/NC screw block on +X and the VCC/GND/IN header on −X; both land
    face-up on the PCB, which is the plane a ferrule goes down onto."""
    ctr, _pts, top = deck_mount("relay-1")
    dx = {"contacts": _relay_ref.length / 2.0 - 10.0,
          "logic": -(_relay_ref.length / 2.0 - 9.0)}[name]
    x, y, _ = _yaw_z((dx, 0.0, 0.0), RELAY_YAW)
    return ((ctr[0] + x, ctr[1] + y, top + _relay_ref.pcb_t + 10.0), "z+")


def ground_stud():
    """The ground bus's landing in world: `(pos, face)` — the top of the lug fan, where
    the next ring terminal goes on and the screw comes down."""
    ctr, _pts, top = deck_mount("ground")
    return ((ctr[0], ctr[1], top + _gnd_ref.ring_count * _gnd_ref.tongue_t), "z+")


def pcba_pose():
    """The board's placement: `(yawed_solid, offset)`. Seating the board is putting the
    centre of its four MH holes on the centre of the cap's `pcba` deck mount — then every
    hole is over its own column by construction, and nothing here chooses a coordinate.
    The exported body is already centred on its outline, so the hole centre is read in
    that frame, not the pcb frame."""
    ctr, _pts, top = deck_mount("pcba")
    body = _rot(_load(PCBA_BOARD), (0, 0, 1), PCBA_YAW)
    holes = _pcba.board.holes
    hx = sum(h[0] for h in holes) / len(holes)
    hy = sum(h[1] for h in holes) / len(holes)
    cx, cy, _ = _yaw_z((hx, hy, 0.0), PCBA_YAW)
    return body, (ctr[0] - cx, ctr[1] - cy, top)


def pcba_port(px, py):
    """A point in the board's OWN pcb frame — `pcbX`/`pcbY` exactly as written in
    [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) — carried to world on the board's TOP FACE, the plane
    every one of the twelve JST wafers and both edge connectors mate off.

    The board seats by its own centre on the cap's deck-mount centre, so the whole mapping is
    that pose's yaw and offset. A port cannot drift from the body carrying it, and moving the
    cap's station moves the column, the board and this map together."""
    x, y, _ = _yaw_z((px - _pcba._centre[0], py - _pcba._centre[1], 0.0), PCBA_YAW)
    _body, (dx, dy, dz) = pcba_pose()
    return (x + dx, y + dy, dz + _pcba._thickness)


def _yaw_z(v, deg):
    """Rotate a point or an axis about Z by `deg` — the first half of the pose."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2])


def _roll_x(v, deg):
    """Rotate a point or an axis about X by `deg` — the second half, the vent's turn."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(v):
    m = math.sqrt(_dot(v, v))
    return (v[0] / m, v[1] / m, v[2] / m)


def src_collet(name):
    """A source-tray boundary collet in world: (position, outward axis). The
    tray sits 180° about Z, so local X and Y negate and local Z carries."""
    p, d = _src.boundary_collets()[name]
    return ((SRC_SEL_POS[0] - p[0], SRC_SEL_POS[1] - p[1], SRC_SEL_POS[2] + p[2]),
            (-d[0], -d[1], d[2]))


def bag_collet(name):
    """A bag-tray boundary collet in world — an outer elbow's, a bare east
    port's, or a Tee's bag branch. The tray rides inverted (180° about Y), so
    local Y carries and local X and Z negate."""
    p, d = (_bag.bag_branches() if name.startswith("Y") else _bag.boundary_collets())[name]
    return ((BAG_CIRCUIT_POS[0] - p[0], BAG_CIRCUIT_POS[1] + p[1], BAG_CIRCUIT_POS[2] - p[2]),
            (-d[0], d[1], -d[2]))


# The nozzle-gate tray is flipped a further 180° about X, in place (about its own
# centre), so the valves that hung down now stand up but the tray keeps its exact
# Z-envelope — clearing the hopper funnel above exactly as the un-flipped tray did —
# while the west inner ports drop from the top of that envelope to the bottom, into
# the discharge tees' reach. The flip axis passes through the tray centre: its Y
# centre is NOZZLE_GATE_POS[1] (the tray is symmetric there) and its Z centre is
# measured off the placed solid.
_GATE_CZ_CACHE = None


def _gate_cz():
    global _GATE_CZ_CACHE
    if _GATE_CZ_CACHE is None:
        bb = _rot(_load(NOZZLE_GATE), (0, 1, 0), 180.0).translate(NOZZLE_GATE_POS).BoundingBox()
        _GATE_CZ_CACHE = (bb.zmin + bb.zmax) / 2.0
    return _GATE_CZ_CACHE


def noz_collet(name):
    """A nozzle-gate-tray bare port collet in world: (position, outward axis) —
    `VG-I`/`VJ-I` the inner (tee-side) ports facing west, `VG-O`/`VJ-O` the outer
    (nozzle-outlet) ports facing east. The tray rides inverted (180° about Y) then
    flipped 180° about X in place: local X negates (the inversion), local Y and Z
    reflect about the tray centre (NOZZLE_GATE_POS[1], `_gate_cz()`)."""
    p, d = _noz.port_collets()[name]
    return ((NOZZLE_GATE_POS[0] - p[0], NOZZLE_GATE_POS[1] - p[1], 2.0 * _gate_cz() - (NOZZLE_GATE_POS[2] - p[2])),
            (-d[0], -d[1], d[2]))


def noz_spade_crown():
    """The nozzle-gate valves' spade tabs' crown in world. The tabs reach east off the coil
    faces, below the coil tops that set the gate's box. Rides the tray's flip exactly as
    `noz_collet` does — local Z carries through to world."""
    v = _noz.bc.cell.valve
    return (2.0 * _gate_cz() - NOZZLE_GATE_POS[2]
            + v.spade_z_center + v.spade_thickness / 2.0)


def junction(tee):
    """A pump-inlet tee's pose: (centre, run axis, branch axis, stub). The run is the line joining
    the two collets it butts. Centred on that line the tube left over splits evenly into a stub at
    each end, less any JUNCTION_LIFT that slides the fitting up the run toward the bag port (which
    lengthens the source stub and shortens the bag one). The branch is east made perpendicular to
    that run."""
    ps, _ns = src_collet(JUNCTION[tee][0])
    pb, _nb = bag_collet(JUNCTION[tee][1])
    span = tuple(pb[i] - ps[i] for i in range(3))
    run = _unit(span)
    east = (1.0, 0.0, 0.0)
    branch = _unit(tuple(east[i] - _dot(east, run) * run[i] for i in range(3)))
    roll = JUNCTION_ROLL.get(tee, 0.0)
    if roll:
        branch = _unit(_spin(branch, run, roll))
    lift = JUNCTION_LIFT.get(tee, 0.0)
    centre = tuple((ps[i] + pb[i]) / 2.0 + lift * run[i] for i in range(3))
    return (centre, run, branch, math.sqrt(_dot(span, span)) / 2.0 - _bag.tee_run_half)


def tee_port(tee, port):
    """A pump-inlet tee's port in world: (position, outward axis). `port` is 1
    (run, facing the source), 2 (run, facing the bag) or 3 (the branch, facing
    its pump) — the fluid topology's own numbering for Y-C / Y-F."""
    centre, run, branch, _stub = junction(tee)
    axis, reach = {1: (tuple(-c for c in run), _bag.tee_run_half),
                   2: (run, _bag.tee_run_half),
                   3: (branch, _bag.tee_branch_reach)}[port]
    return tuple(centre[i] + reach * axis[i] for i in range(3)), axis

# The whole boss chain — head counterbore + pin body + heat-set + cap, less the
# wall the counterbore sinks into — reaches this far inboard of a side wall, and
# so does the corner post carrying it. The ±X walls therefore stand this far off
# the COLD CORE rather than against it: the core spans the interior wall to wall
# and floor to its cap, so a wall on its face leaves the seam machinery nowhere
# to go, and it is the core that sets the box width. enclosure.py reads this as
# the side-wall standoff. Front floor content set against a side wall is inset
# the same, to clear the ribs.
SIDE_RIB_INSET = 14.0
# Floor parts are raised one wall, clearing the front pieces' bottom seam lip
# so the split can pull forward past them. The box floors to a fixed Z=0
# datum, so raising them leaves the floor in place.
SEAM_CLEAR_LIFT = 3.0
# Enclosure wall thickness (mirrors ../enclosure/enclosure.py `wall`) — used to
# seat content against the seam lips' inner faces, one wall in from the walls.
WALL = 3.0
# The back wall stands one wall behind the rearmost content — the cold core —
# instead of hard against it, so the core seats flush against the rear Z-seam
# lip's inner face rather than against the wall itself. enclosure.py reads it
# from here as `rear_seam_clear`, so the wall the panel bodies seat against and
# the wall the box is built to are one number and cannot drift apart.
REAR_STANDOFF = 3.0
# The FRONT wall stands the same one wall off the pack, for the front column's
# Z-seam lip: the compressor and the tipped condenser reach that seam's height
# at the front wall, and a wall on their faces leaves the lip's front segment
# nowhere to run — a lip missing a side is a butt joint over that run, on the
# box's most visible face. Held off, the segment runs the full width behind
# them. enclosure.py reads it from here as the front inset, and panel_bodies()
# seats the DERPIPE on the wall it opens, so the two cannot drift apart.
FRONT_STANDOFF = 3.0
# Vertical gap between a stratum's tallest part and the parts seated above it.
STACK_GAP = 2.5

# --- Electronics shelf + rear-panel ports -----------------------------------
# The shelf lies flat on the foam-cap top in the front half of the band
# above the cold core — the rear-wall port bodies reach ~28–35 mm forward
# into the band's rear half, and the shelf may not stand under them (the
# assembly check intersects the real bodies). The shelf parts also stay
# inset off the ±X walls (the Z-seam lip band hugs the walls at the
# foam-top level, and the corner-boss chains reach ~14 in). Nothing on the
# cap has to clear a CO2 entry: that line leaves the core's front face down
# at the vessel's bottom plate and never reaches this deck.
# Every external connection penetrates the REAR wall (back_wall_ports
# below), in the band above the cold core (the foam tops out at ~263; the
# rear Z-seam lip band tops out at ~279) — their bodies hang in the band's
# open rear half. enclosure.py cuts the holes into the back pieces;
# panel_bodies() seats the receptacle / bulkhead bodies through them. Hole
# inventory and specs: ../back-panel/README.md.
PORT_BULKHEAD_D = 18.0        # JG 1/4" bulkhead panel hole (clears the Ø17.14 barrel)
PORT_C14_W, PORT_C14_H = 28.5, 25.5   # C14 through-body 27.5 wide, z −10.2/+12.2 about
                                      # its axis (measured off the reference STEP) +
                                      # clearance; the flange seats proud on the
                                      # outer face
# The panel-clamping NUT / flange footprints are far wider than the through-holes,
# so the cluster is spaced to the NUTS (not the holes) or the real hardware fouls.
# Measured off the reference STEPs: jg-bulkhead-union, iec-c14-inlet.
PORT_NUT_D = 22.86           # JG bulkhead nut, across the panel face (measured)
PORT_C14_FLANGE_W = 30.5     # C14 flange width across the panel face (measured)
PORT_C14_FLANGE_H = 23.5     # C14 flange height across the panel face (measured)
PORT_NUT_GAP = 7.0           # clear gap between adjacent bulkhead nuts (the margin)
UMBILICAL_Z_FLOOR = 281.0    # lowest bulkhead-nut edge: the rear Z-seam lip band
                             # tops out at z_joint_back + lip_len (~279) on the back wall
# Rear-wall stations, left to right: the C14 on the power assembly's column
# (its cordage drops the rear wall and runs forward over the foam top to
# the AC hub), then the tap-water bulkhead, then the umbilical triangle —
# every body hangs in the band's open rear half, behind the shelf row.
# The triangle stands east of the drip pan's lane: the pan draws aft through this
# wall, and its rails run the strip's full depth, so the lower row's nuts have to
# clear the rail pair's east web.
UMBILICAL_X = 217.0          # triangle column center
WATER_BACK_X = 56.0          # west of the umbilical, on the ASSE chain's inlet end
# On the chain's inlet height, so the pigtail turns one corner between the two collets.
WATER_BACK_Z = bfp_terminal("tube-in")[0][2]
# The C14 stands in the panel's WEST corner, clear of the umbilical's field and of
# the water deck's x-span. Its cordage drops the rear wall and runs forward along
# the west wall to the AC hub, so it crosses neither the ASSE 1022's drip column
# nor the pan's ground on the cap. PORT_C14_FLANGE_W/2 off the corner-post band
# leaves the flange its own bearing on the printed wall, and its flange top rides
# level with the tap-water nut's — the top edge of the field, and what the wall
# takes its ceiling from.
C14_BACK_X = 22.0
C14_BACK_Z = WATER_BACK_Z + PORT_NUT_D / 2.0 - PORT_C14_FLANGE_H / 2.0
# CO2 inlet — the DERPIPE 5/16"-tube PTC × 1/4" NPT M fitting on the front
# panel, front-left, NPT side facing inboard to carry the GASHER check screwed
# straight onto its stub (internal-plumbing.md §1). Its Z stands the chain in
# the open band between the compressor's top and the pump row's underside,
# which is the one place in the front column deep enough to hang a rigid
# fitting off the wall; above the front Z-seam's lip rim, so the hole is cut
# in one piece.
CO2_INLET_X = 46.0
CO2_INLET_Z = 172.0
CO2_HOLE_D = 14.5            # clears the DERPIPE's 1/4" NPT shank (Ø~13.7 major)
# The GASHER's socket mouth meets the DERPIPE's stub shoulder — an envelope
# butt for a made-up thread, so the pair reads as one body off the wall.
# Stated in build()'s own frame rather than read off the wall, because the
# wall is derived FROM build(); `_panel_bodies` asserts the two do meet.
CO2_GASHER_Y = 2.0
# The WR1110 cannot follow the check inline: the band at the inlet's own X
# runs out on the source-select tray's underside before the regulator's 57 mm
# are up. So it lies ACROSS the band instead — the band is the machine's whole
# width and only one fitting deep — and a tube takes the single corner between
# them. Its X puts the outlet's exit stub over the slot between the compressor
# and the condenser, the one column in the front stratum that runs to the
# floor, which is how the line gets under the tray to the cold core. Its Y
# stands it forward of the check's outlet by more than that corner's tangents,
# and its Z is the check's, so nothing climbs between them. Cradle TBD.
WR1110_YAW = -90.0           # flow +X
WR1110_CX = 167.5
WR1110_CY = 66.0
# DERPIPE_BODY_L: the outboard reach that seats the collet face proud of the
# front wall (the model's outboard face is at its Y origin).
DERPIPE_BODY_L = 17.0
# The DIGITEN flow meter, inline on the carb-water riser. Placed UNTURNED: its own
# frame already runs the flow +X and stands the pigtail boss +Z, which is the pose
# this station wants. It lies in the STRIP AHEAD OF THE COLD CORE'S FRONT FACE, at
# the water inlet's own height — the one band of that strip nothing stands in: the
# source-select assembly stops short of it to the south, the bag-circuit tray clears
# it above, and the discharge chain hangs down it well to the east. A 60 mm rigid
# body with a Ø26 waist fits here with 7.0 mm to the foam face and 6.1 mm to the
# tray. Sitting at the riser's own height rather than above it keeps the climb out
# of water-5's band entirely: the riser owns the strip below the meter, the water
# inlet's line owns everything above it, and the two never cross. Its X puts the
# inlet collet clear of the climb and the outlet collet clear of the lane east, so
# the two runs meet it head-on down its own axis and neither turns inside it.
# Cradle TBD.
DIGITEN_POS = (160.0, 164.0, 204.0)          # the body centre; the collets sit ±30 off it in X


# --- Colors ---------------------------------------------------------------
COLORS = {
    "foam-assembly":     cq.Color(0.55, 0.75, 0.95, 0.55),
    "compressor-shroud": cq.Color(0.60, 0.62, 0.66),
    "condenser+fan":     cq.Color(0.78, 0.55, 0.35),
    "mq6-sensor":        cq.Color(0.30, 0.45, 0.85),
    # The Multiplex's brass body carries the chain's color, as its own assembly draws it.
    "asse1022-assembly": cq.Color(0.72, 0.58, 0.28),
    "source-select-assembly": cq.Color(0.60, 0.40, 0.70),
    "bag-circuit-assembly":   cq.Color(0.35, 0.62, 0.55),
    "nozzle-gate-assembly":   cq.Color(0.75, 0.62, 0.30),
    "pump-a":            cq.Color(0.72, 0.28, 0.30),
    "pump-b":            cq.Color(0.72, 0.28, 0.30),
    "tee-y-c":           cq.Color(0.92, 0.92, 0.92),
    "tee-y-f":           cq.Color(0.92, 0.92, 0.92),
    "y-d":               cq.Color(0.30, 0.55, 0.85),
    "y-g":               cq.Color(0.30, 0.55, 0.85),
    "elbow-y-d":         cq.Color(0.85, 0.85, 0.88),
    "elbow-y-g":         cq.Color(0.85, 0.85, 0.88),
    "elbow-bag-y-d":     cq.Color(0.85, 0.85, 0.88),
    "elbow-bag-y-g":     cq.Color(0.85, 0.85, 0.88),
    "elbow-noz-a":       cq.Color(0.85, 0.85, 0.88),
    "elbow-noz-b":       cq.Color(0.85, 0.85, 0.88),
    "seaflo-pump":       cq.Color(0.32, 0.38, 0.46),
    "water-split":       cq.Color(0.88, 0.89, 0.91),
    "flow-regulator":    cq.Color(0.80, 0.82, 0.86),
    "digiten-flow":      cq.Color(0.92, 0.92, 0.94),
    "discharge-chain":   cq.Color(0.72, 0.74, 0.78),
    "vk-fill-valve":      cq.Color(0.85, 0.86, 0.90),
    "drip-pan":          cq.Color(0.62, 0.66, 0.72),
    "drip-pan-rails":    cq.Color(0.45, 0.50, 0.58),
    "psu":               cq.Color(0.72, 0.74, 0.78),
    "relay-1":           cq.Color(0.20, 0.45, 0.75),
    "ac-hub":            cq.Color(0.85, 0.78, 0.62),
    "ground-stack":      cq.Color(0.80, 0.80, 0.83),
    "pcba":              cq.Color(0.15, 0.45, 0.25),
    "dc-dist":           cq.Color(0.20, 0.20, 0.22),
    # Panel bodies wear the customer wayfinding colors — blue = carb water,
    # white = tap water, red = CO2 (back-panel README + unboxing brief).
    "bulkhead-carb":     cq.Color(0.25, 0.45, 0.90),
    "bulkhead-flavor-a": cq.Color(0.20, 0.20, 0.22),
    "bulkhead-flavor-b": cq.Color(0.20, 0.20, 0.22),
    "bulkhead-water":    cq.Color(0.92, 0.92, 0.92),
    "c14-inlet":         cq.Color(0.12, 0.12, 0.14),
    "co2-inlet":         cq.Color(0.85, 0.35, 0.30),
    "gasher-co2":        cq.Color(0.85, 0.35, 0.30),
    "wr1110":            cq.Color(0.72, 0.30, 0.26),
}


def _load(path):
    return cq.importers.importStep(str(path)).val()


def _rot(shape, axis, deg):
    return shape.rotate((0, 0, 0), axis, deg)


def _spin(v, axis, deg):
    """Rodrigues: turn a vector `deg` about a unit axis through the origin."""
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    x = _cross(axis, v)
    return tuple(v[i] * c + x[i] * s + axis[i] * _dot(axis, v) * (1.0 - c) for i in range(3))


def _aim(shape, run, branch):
    """Turn a union tee — native run +Z, native branch +Y — so its run lies
    along `run` and its branch along `branch` (unit, perpendicular). Two turns:
    swing +Z onto the run, then spin about the run until the carried +Y lands
    on the branch."""
    y = (0.0, 1.0, 0.0)
    axis = _cross((0.0, 0.0, 1.0), run)
    if _dot(axis, axis) > 1e-18:
        axis = _unit(axis)
        turn = math.degrees(math.acos(max(-1.0, min(1.0, run[2]))))
        shape, y = shape.rotate((0, 0, 0), axis, turn), _spin(y, axis, turn)
    elif run[2] < 0.0:
        shape = shape.rotate((0, 0, 0), (0, 1, 0), 180.0)
    spin = math.degrees(math.atan2(_dot(_cross(y, branch), run), _dot(y, branch)))
    return shape.rotate((0, 0, 0), run, spin)


def _flip_x_in_place(shape):
    """Rotate a placed solid 180° about the X axis through its own bbox centre —
    a flip that keeps its exact position/envelope, only turning it top-to-bottom."""
    bb = shape.BoundingBox()
    cy, cz = (bb.ymin + bb.ymax) / 2.0, (bb.zmin + bb.zmax) / 2.0
    return shape.rotate((0.0, cy, cz), (1.0, cy, cz), 180.0)


def _place_elbow(shape, port_pos, port_dir, free_dir, stub=2.0):
    """A 90° elbow butting a port (world pos, outward `port_dir`): one collet faces
    back into the port (stub off it), the free leg runs along `free_dir` (⊥ port_dir).
    Native elbow collets are +Y (butt) and +Z (free), so `_aim` places it."""
    butt = tuple(-c for c in port_dir)
    reach = tuple(port_pos[i] + (stub + _bag.elbow_reach) * port_dir[i] for i in range(3))
    return _aim(shape, free_dir, butt).translate(reach)


def _elbow_free_port(collet, free_dir, stub=2.0):
    """The world position of the free (empty) port of an elbow placed by `_place_elbow`
    on `collet` (a (pos, outward-dir) pair) with the given free direction."""
    port_pos, port_dir = collet
    corner = tuple(port_pos[i] + (stub + _bag.elbow_reach) * port_dir[i] for i in range(3))
    return tuple(corner[i] + _bag.elbow_reach * free_dir[i] for i in range(3))


# ── Pump-discharge junctions Y-D / Y-G ───────────────────────────────────────────────────────
# Each pump merges a flavor's two sources — its bag valve and its nozzle-gate valve — through a
# JG PP2308E two-way divider (the `y-divider`), then feeds its pump. The netlist is DIAGONAL
# because the two trays seat a flavor's valves on opposite rows: Y-D (flavor A → pump A) joins
# bag V-F and nozzle V-G; Y-G (flavor B → pump B) joins bag V-I and nozzle V-J.
#
# The four turn-elbows sit at the corners of a rectangle in the Y-Z plane — the bag ports high
# (z≈277), the nozzle ports low (z≈242) — and the diagonal netlist runs two CROSSING tubes across
# it. Each divider is placed by hand over the pump row (DISCHARGE_DIV) and aimed so its two parallel
# outlets face back at the mean of the two elbow CORNERS it receives (`_divider_out_sep`); each elbow
# then aims its free leg straight at the outlet it feeds (`elbow_free_dir`) — mating face to mating
# face — plus a hand-set upward LIFT (DISCHARGE_LIFT) for the two long crossing legs, so they leave
# climbing and clear the near flavor's fitting instead of driving through it. Soft LLDPE takes up the
# residual: straight where it can be, gently bent where a run has to step over a fitting (_lines.py).
# The dividers' stems point −out (≈−Y) at the pump discharge they'll later take (segments 12/22,
# unauthored).
DIV_HALF     = 19.25                          # divider stem/outlet reach from centre (off the STEP)
DIV_OUTLET_Y = 7.35                           # each outlet's offset from the divider axis
ELBOW_STUB   = 2.0                            # tube between a valve port and its turn elbow

DISCHARGE_ELBOW = {                           # turn elbow → (tray, bare valve-port key it turns)
    "elbow-bag-y-d": ("bag", "VF"),
    "elbow-y-d":     ("noz", "VJ-I"),
    "elbow-bag-y-g": ("bag", "VI"),
    "elbow-y-g":     ("noz", "VG-I"),
}
DISCHARGE_NET = {                             # divider → (bag elbow → upper outlet 2, noz elbow → lower outlet 3)
    "y-d": ("elbow-bag-y-d", "elbow-y-g"),
    "y-g": ("elbow-bag-y-g", "elbow-y-d"),
}
# Each turn elbow's free leg first AIMS at the outlet it feeds (in the Y-Z plane ⊥ its ±X valve
# axis — so the mating faces point at each other and the run leaves nearly straight), then tilts UP
# by DISCHARGE_LIFT[name]°. The lift is 0 for a short leg that shoots straight into its outlet, and
# positive for a long crossing leg that must climb OVER the near flavor's fitting before it drops
# into its outlet — the gentle over-the-top the diagonal netlist needs.
DISCHARGE_LIFT = {
    "elbow-bag-y-d":  0.0,                     # short leg → y-d, straight in
    "elbow-y-d":      0.0,                     # short leg → y-g, straight in
    "elbow-bag-y-g": 15.0,                     # long leg → y-g, climbs over elbow-bag-y-d
    "elbow-y-g":     22.0,                     # long leg → y-d, climbs over elbow-y-d
}
# Divider → centre, over the pump row, aimed at its elbows. Both ride LOW in the pump-row band —
# their crowns tucked under the hopper funnel's basin floor with room to spare above, so the
# channel-A suction leg (fluid-11) can cross OVER them on its way from tee-y-c to pump B's inlet
# without driving through their bodies or the funnel. y-g drops furthest (fluid-11 crosses right
# over its crown); y-d rides a touch higher so its own body keeps clear of pump B just below it.
DISCHARGE_DIV = {
    "y-d": (214.0, SRC_SEL_POS[1] - 73.30, 267.5),
    "y-g": (167.97, SRC_SEL_POS[1] - 69.84, 266.0),
}
DISCHARGE_YAW = {                             # extra Z-turn of a divider: stem toward its pump, outlets the same off their elbows
    "y-d": 16.0,
}

# ── Nozzle-outlet elbows ─────────────────────────────────────────────────────────────────────
# A PP0308E on each bare nozzle-gate outer port (V-G-O/V-J-O, facing east), turning its nozzle
# line UP out of the +X wall pocket, where the run climbs aft over the electronics shelf to the
# rear flavor bulkhead (segments 18/28). Each body stands in the pocket between the gate's east
# ports and the +X wall — the cold core's own SIDE_RIB_INSET standoff, which is one fitting depth
# deep at GATE_WALL_INSET. Nothing is cut for them: the gate keeps its X station, so the junction
# pocket west of it is untouched, and the wall's seam machinery clears this band on its own — the
# front Z-lip rim tops out well below these bodies, and the Y-seam corner column stands aft of them.
OUTLET_ELBOW = {                              # elbow → the nozzle-gate outer port it turns
    "elbow-noz-a": "VG-O",                    # nozzle A → bulkhead-flavor-a
    "elbow-noz-b": "VJ-O",                    # nozzle B → bulkhead-flavor-b
}
OUTLET_FREE = (0.0, 0.0, 1.0)                 # free leg UP, leaving the pocket for the run aft


def outlet_free_pose(name):
    """A nozzle-outlet elbow's free (empty) port in world: (position, outward axis) — where its run
    to the rear flavor bulkhead leaves, one bend up off the pocket."""
    return _elbow_free_port(noz_collet(OUTLET_ELBOW[name]), OUTLET_FREE, ELBOW_STUB), OUTLET_FREE


def _discharge_collet(name):
    kind, key = DISCHARGE_ELBOW[name]
    return bag_collet(key) if kind == "bag" else noz_collet(key)


def _perp(v, ax):
    """Component of v perpendicular to unit axis `ax`."""
    d = _dot(v, ax)
    return tuple(v[i] - d * ax[i] for i in range(3))


def _elbow_corner(collet, stub=ELBOW_STUB):
    """The elbow's turn centre: `stub` + one reach out along the valve port, where the free leg
    pivots. Independent of the elbow's roll."""
    pos, d = collet
    return tuple(pos[i] + (stub + _bag.elbow_reach) * d[i] for i in range(3))


def _elbow_outlet(name):
    """The (divider, port) an elbow feeds — the bag elbow → upper outlet 2, the nozzle elbow → lower
    outlet 3."""
    for div, (be, ne) in DISCHARGE_NET.items():
        if name == be:
            return div, 2
        if name == ne:
            return div, 3
    raise KeyError(name)


def elbow_free_dir(name):
    """A discharge elbow's free-leg direction: aim the free leg (in the Y-Z plane ⊥ its ±X valve
    axis) straight at the OUTLET it feeds — so a short leg is one straight tube, mating face to mating
    face — then tilt it up by DISCHARGE_LIFT[name]° (a rotation in that Y-Z plane, toward +Z). Lift 0
    stays aimed at the outlet; a positive lift makes a long crossing leg climb before it drops in."""
    corner = _elbow_corner(_discharge_collet(name))
    div, port = _elbow_outlet(name)
    target = divider_port(div, port)[0]
    d = tuple(target[i] - corner[i] for i in range(3))
    base = _unit((0.0, d[1], d[2]))                    # point the free leg at the outlet (Y-Z only)
    th = math.radians(DISCHARGE_LIFT[name])
    c, s = math.cos(th), math.sin(th)
    return (0.0, base[1] * c + base[2] * s, -base[1] * s + base[2] * c)   # tilt up toward +Z


def elbow_free_pose(name):
    """A discharge elbow's free (empty) port in world: (position, outward axis) — where its tube
    to the divider leaves."""
    free = elbow_free_dir(name)
    return _elbow_free_port(_discharge_collet(name), free, ELBOW_STUB), free


def _divider_out_sep(name):
    """Aim divider `name`: its outlets face `out` — from the centre toward the mean of the two elbow
    CORNERS it receives — and split along `sep`, the vertical ⊥ out (so the upper outlet takes the
    high bag leg, the lower the low nozzle leg). The centres sit far enough apart on X that this aim
    only leans each trident modestly toward the shared cluster without the two bodies meeting; and
    because the outlet face looks straight back at the cluster, each elbow can aim its free leg right
    into its outlet. Aimed at the CORNERS (fixed, independent of the elbow rolls that aim back at
    these outlets — so there is no circular solve). Stem faces −out (−Y) at the pump."""
    centre = DISCHARGE_DIV[name]
    be, ne = DISCHARGE_NET[name]
    cb = _elbow_corner(_discharge_collet(be))
    cn = _elbow_corner(_discharge_collet(ne))
    mean = tuple((cb[i] + cn[i]) / 2.0 for i in range(3))
    out = _unit(tuple(mean[i] - centre[i] for i in range(3)))
    yaw = DISCHARGE_YAW.get(name, 0.0)
    if yaw:
        th = math.radians(yaw)
        c, s = math.cos(th), math.sin(th)
        out = _unit((out[0] * c - out[1] * s, out[0] * s + out[1] * c, out[2]))
    sep = _unit(_perp((0.0, 0.0, 1.0), out))
    return out, sep


def _place_divider(shape, name):
    """Divider `name` at its centre, aimed by `_divider_out_sep`: outlets face `out`, stem −out,
    outlets split ±DIV_OUTLET_Y along `sep`. Native long axis +Z (stem) / −Z (outlets), outlets
    offset ±Y — `_aim` maps native +Z onto −out and native +Y onto sep."""
    out, sep = _divider_out_sep(name)
    return _aim(shape, tuple(-c for c in out), sep).translate(DISCHARGE_DIV[name])


def divider_port(name, port):
    """A discharge divider's port in world: (position, outward axis). `port` is 1 (stem, −out at
    the pump), 2 (upper outlet, +sep — the bag leg) or 3 (lower outlet, −sep — the gate leg)."""
    c = DISCHARGE_DIV[name]
    out, sep = _divider_out_sep(name)
    if port == 1:
        return tuple(c[i] - DIV_HALF * out[i] for i in range(3)), tuple(-x for x in out)
    s = DIV_OUTLET_Y if port == 2 else -DIV_OUTLET_Y
    pos = tuple(c[i] + DIV_HALF * out[i] + s * sep[i] for i in range(3))
    return pos, out


# ── Pump-discharge outlet elbow re-aim ───────────────────────────────────────────────────────
# PUMP_OUTLET_AIM re-rolls a pump's discharge outlet elbow about its vertical port axis to the
# free-leg heading its stem run leaves along. pump-a aims east at y-g; pump-b aims northwest at
# y-d's yawed stem, so segment 12 leaves straight at the divider.
PUMP_ELBOW_REACH = 19.56                          # outlet elbow free-leg: collet face to bend corner
# The outlet collet stands this far off its pump's own placement origin in plan, on both pumps,
# at the one deck Z the two elbows share. Carried off the pump so the collet travels with it.
_PUMP_OUTLET_OFFSET = (8.94, -63.50)
_PUMP_OUTLET_Z = 278.17
_PUMP_OUTLET_BASE = {                             # as-placed outlet collet CENTRE: (pos, free-leg dir)
    name: ((pos[0] + _PUMP_OUTLET_OFFSET[0], pos[1] + _PUMP_OUTLET_OFFSET[1], _PUMP_OUTLET_Z),
           (-1.0, 0.0, 0.0))
    for name, pos in (("pump-a", PUMP_A_POS), ("pump-b", PUMP_B_POS))
}
PUMP_OUTLET_AIM = {                               # re-rolled free-leg heading (horizontal); absent = as placed
    "pump-a": (0.97, -0.22, 0.0),
    "pump-b": (-0.847, 0.532, 0.0),
}


def _pump_outlet_corner(name):
    """The outlet elbow's bend corner: one free-leg reach back from the collet, on the vertical
    axis the elbow rolls about."""
    pos, d = _PUMP_OUTLET_BASE[name]
    return tuple(pos[i] - PUMP_ELBOW_REACH * d[i] for i in range(3))


def pump_outlet_pose(name):
    """A pump's discharge outlet collet in world: (position, outward axis) — where segment 12/22
    leaves. Re-rolled to PUMP_OUTLET_AIM[name] where present, else as placed."""
    base_pos, base_d = _PUMP_OUTLET_BASE[name]
    aim = PUMP_OUTLET_AIM.get(name)
    if aim is None:
        return base_pos, base_d
    t = _unit(aim)
    corner = _pump_outlet_corner(name)
    return tuple(corner[i] + PUMP_ELBOW_REACH * t[i] for i in range(3)), t


def _pump_outlet_roll(name):
    """CCW degrees about +Z from the as-placed free leg to PUMP_OUTLET_AIM[name]."""
    _p, base_d = _PUMP_OUTLET_BASE[name]
    t = _unit(PUMP_OUTLET_AIM[name])
    return math.degrees(math.atan2(t[1], t[0]) - math.atan2(base_d[1], base_d[0]))


def _reaim_pump_outlet(shape, name):
    """Roll `name`'s discharge outlet elbow — the high-Z front sub-solid — about its vertical port
    axis to PUMP_OUTLET_AIM[name]."""
    corner = _pump_outlet_corner(name)
    roll = _pump_outlet_roll(name)
    base_pos, _d = _PUMP_OUTLET_BASE[name]
    solids = shape.Solids()

    def outlet_key(s):
        b = s.BoundingBox()
        if b.zmax < 260.0:                        # a low pump body, not an elbow
            return 1e9
        cx, cy = (b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0
        return (cx - base_pos[0]) ** 2 + (cy - base_pos[1]) ** 2

    outlet = min(solids, key=outlet_key)
    turned = outlet.rotate((corner[0], corner[1], 0.0), (corner[0], corner[1], 1.0), roll)
    return cq.Compound.makeCompound([s for s in solids if s is not outlet] + [turned])


# ── Pump-suction inlet elbow re-aim ──────────────────────────────────────────────────────────
# PUMP_INLET_AIM re-rolls a pump's suction inlet elbow (the aft, west-facing station) about its
# vertical port axis to face the tee its suction leg comes from. pump-b stands east of the bag
# tray, with room to roll northwest at tee-y-c. pump-a's inlet stays west: the bag tray fills the
# space between it and tee-y-f, which hangs behind the tray, so fluid-21 reaches it from the west.
# The inlet collet stands this far off its pump's own placement origin in plan, on both pumps,
# at the deck Z the outlet elbow shares. Carried off the pump so the collet travels with it.
_PUMP_INLET_OFFSET = (8.94, -6.50)
_PUMP_INLET_BASE = {                              # as-placed inlet collet CENTRE: (pos, free-leg dir)
    name: ((pos[0] + _PUMP_INLET_OFFSET[0], pos[1] + _PUMP_INLET_OFFSET[1], _PUMP_OUTLET_Z),
           (-1.0, 0.0, 0.0))
    for name, pos in (("pump-a", PUMP_A_POS), ("pump-b", PUMP_B_POS))
}
PUMP_INLET_AIM = {                                # re-rolled free-leg heading (horizontal); absent = as placed
    "pump-b": (-0.940, 0.342, 0.0),
}


def _pump_inlet_corner(name):
    """The inlet elbow's bend corner: one free-leg reach back from the collet, on the vertical
    axis the elbow rolls about."""
    pos, d = _PUMP_INLET_BASE[name]
    return tuple(pos[i] - PUMP_ELBOW_REACH * d[i] for i in range(3))


def pump_inlet_pose(name):
    """A pump's suction inlet collet in world: (position, outward axis) — where segment 11/21
    closes. Re-rolled to PUMP_INLET_AIM[name] where present, else as placed."""
    base_pos, base_d = _PUMP_INLET_BASE[name]
    aim = PUMP_INLET_AIM.get(name)
    if aim is None:
        return base_pos, base_d
    t = _unit(aim)
    corner = _pump_inlet_corner(name)
    return tuple(corner[i] + PUMP_ELBOW_REACH * t[i] for i in range(3)), t


def _pump_inlet_roll(name):
    """CCW degrees about +Z from the as-placed free leg to PUMP_INLET_AIM[name]."""
    _p, base_d = _PUMP_INLET_BASE[name]
    t = _unit(PUMP_INLET_AIM[name])
    return math.degrees(math.atan2(t[1], t[0]) - math.atan2(base_d[1], base_d[0]))


def _reaim_pump_inlet(shape, name):
    """Roll `name`'s suction inlet elbow — the high-Z aft sub-solid — about its vertical port axis
    to PUMP_INLET_AIM[name]."""
    corner = _pump_inlet_corner(name)
    roll = _pump_inlet_roll(name)
    base_pos, _d = _PUMP_INLET_BASE[name]
    solids = shape.Solids()

    def inlet_key(s):
        b = s.BoundingBox()
        if b.zmax < 260.0:                        # a low pump body, not an elbow
            return 1e9
        cx, cy = (b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0
        return (cx - base_pos[0]) ** 2 + (cy - base_pos[1]) ** 2

    inlet = min(solids, key=inlet_key)
    turned = inlet.rotate((corner[0], corner[1], 0.0), (corner[0], corner[1], 1.0), roll)
    return cq.Compound.makeCompound([s for s in solids if s is not inlet] + [turned])


def _at(shape, xmin, ymin, zmin):
    bb = shape.BoundingBox()
    return shape.translate((xmin - bb.xmin, ymin - bb.ymin, zmin - bb.zmin))


def _box(dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False)).val()


def _cyl(d, length, axis):
    """Cylinder of diameter d along a unit axis, base at the origin."""
    return cq.Solid.makeCylinder(d / 2.0, length, cq.Vector(0, 0, 0), cq.Vector(*axis))


_PLACED: dict | None = None


def build():
    """The pack as placed solids: {name: (solid, color)}.

    Memoized for the life of the process. The port frame, the panel bodies, the enclosure's own
    sizing, `_lines._frames()` and the scorecard each ask for the pack, and every one of them
    would otherwise re-import the same STEPs; a rebuild is always a fresh process."""
    global _PLACED
    if _PLACED is None:
        _PLACED = _build()
    return _PLACED


def _build():
    placed = {}

    foam = _load(FOAM_ASSEMBLY)
    fb = foam.BoundingBox()
    cold_w = fb.xlen                            # ~283 wide (shell + cap stacks, 253.4 tall)
    foam_top = fb.zlen                          # the shelf floor, the cap's own top

    # --- Zone A: cold core at the back, flat on the floor slab. Its bottom
    # cap's lid is the whole bearing surface — a plane, with every cap screw
    # down in a counterbore in its own head pad — so nothing stands between the
    # core and the floor. X is fenced by the seam posts standing on the
    # footprint's own ±X edges, +Y by the back Z-seam lip, −Y by the two core
    # lugs the floor grows ahead of it. The −Y service/dispense ports face
    # forward.
    placed["foam-assembly"] = _at(foam, 0.0, FRONT_DEPTH, 0.0)

    # --- Floor: compressor shroud front-left, condenser/fan front-right,
    # tipped on its back (airflow axis still across X): the donor block's
    # FACE_A dimension runs along Y — the front block is as deep as it — and
    # FACE_B stands as the height, level with the compressor top, leaving the
    # whole front column above the floor stratum open. Both sit one corner-rib
    # chain inboard of the cold core's own side faces, and the side walls stand a
    # further chain outboard of those — so the floor stratum keeps SIDE_RIB_INSET
    # of free width at each wall beyond what the ribs need. Closing that would
    # move refrig-1's lane with them. The donor's factory
    # filter-drier rides the condenser block (brazed to its outlet), not packed
    # separately; the MQ-6 sits on the floor between the compressor and the
    # cold core, low, where leaked isobutane pools.
    # −90° about Z so the shroud's single copper-bearing face (native −X) points +Y,
    # toward the foam/cold-core it mates to — not −Y toward the removable front shell.
    # The AC gland (native +Y) then faces +X, into the inter-part channel. Same 178×133×151
    # footprint either way (a Z-rotation of the box), so the pack is unchanged.
    comp = _rot(_load(COMP_SHROUD), (0, 0, 1), -90.0)
    placed["compressor-shroud"] = _at(comp, SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    cond = _box(CONDENSER_AIRFLOW, CONDENSER_FACE_A, CONDENSER_FACE_B)  # the tipped block
    placed["condenser+fan"] = _at(cond, cold_w - CONDENSER_AIRFLOW - SIDE_RIB_INSET, 0.0, SEAM_CLEAR_LIFT)
    placed["mq6-sensor"] = _at(_load(MQ6_STEP), 100.0, 134.0, SEAM_CLEAR_LIFT)

    # The CO2 chain, in the band the compressor's top and the pump row's
    # underside leave open. Both bodies are authored +Y = flow and both run +Y
    # here, so neither turns. The check screws onto the DERPIPE's stub and the
    # wall carries it; the regulator stands clear of it further east on its own
    # cradle, and one tube crosses between them.
    _gasher = _load(GASHER_STEP)
    placed["gasher-co2"] = _gasher.translate(
        (CO2_INLET_X, CO2_GASHER_Y - _boxes.boxed(_gasher).ymin, CO2_INLET_Z))
    _reg = _rot(_load(WR1110_STEP), (0, 0, 1), WR1110_YAW)
    _reg_bb = _boxes.boxed(_reg)
    placed["wr1110"] = _at(_reg,
                           WR1110_CX - _reg_bb.xlen / 2.0,
                           WR1110_CY - _reg_bb.ylen / 2.0,
                           CO2_INLET_Z - _reg_bb.zlen / 2.0)

    # The carb-water riser's flow meter, lying unturned in the strip ahead of the
    # cold core's front face — flow +X, pigtail boss up where the J4 loom reaches it.
    placed["digiten-flow"] = _load(DIGITEN_STEP).translate(DIGITEN_POS)

    # The ASSE 1022 assembly: the water path's one non-negotiable component with the
    # four fittings that reach it from 1/4" tube on one side and 3/8" hose on the
    # other, as one piece. It packs up in the service bay's aft strip, at the rear
    # bulkhead it protects (ASSE1022_AXIS). Its own frame is the world's axes
    # (+X = flow, vent −Z), so the pose is a yaw about Z, then a roll about X that
    # lays the vent over toward +Y, then the translation `asse_pos()` derives — the
    # same two turns `bfp_terminal` walks the three terminals through, in order.
    placed["asse1022-assembly"] = placed_asse()

    # --- Zone C: the source-select assembly (Tray 1 — V-A/V-B/Y-A/Y-B/V-C/V-D
    # on its printed tray) floors the manifold stack, spanning the front width,
    # pressed aft against the cold core's front face. Rotated 180° about Z
    # (plate down, valves up, V-A/V-B east) then translated: the assembly's own
    # frame (cell centre, valve mounting plane) is the placement datum, so
    # SRC_SEL_POS reads as its world pose. Its wall backs on the foam face are
    # a declared contact, held by the scorecard's `near foam-assembly` rule on
    # the real solids.
    placed["source-select-assembly"] = _rot(_load(SOURCE_SELECT), (0, 0, 1), 180.0).translate(SRC_SEL_POS)

    # Above it, the bag-circuit assembly (Tray 2 — V-E/V-F/V-H/V-I + Tees
    # Y-E/Y-H on the dog-bone tray, both bag branches rolled to the one
    # `bag_fall_aim` — each aimed down its fall) rides
    # INVERTED: rotated 180° about Y, which puts each
    # pump-inlet Tee's pair of valve ports on one side (V-E/V-H west, in the
    # junction column over the source west bank they tee with), turns those
    # west collets DOWN into the column and the east collets UP toward the
    # pump row. Its wall tops seat on the source tray's (a declared contact);
    # the floor stratum stays open below the stack.
    placed["bag-circuit-assembly"] = _rot(_load(BAG_CIRCUIT), (0, 1, 0), 180.0).translate(BAG_CIRCUIT_POS)

    # East of it, the nozzle-gate assembly (Tray 3 — V-G/V-J, bare ports) rides
    # INVERTED, then flipped 180° about X in place (`_flip_x_in_place`): same
    # envelope, but the valves stand up and the west inner ports drop to the
    # discharge tees below (NOZZLE_GATE_POS + noz_collet).
    placed["nozzle-gate-assembly"] = _flip_x_in_place(
        _rot(_load(NOZZLE_GATE), (0, 1, 0), 180.0).translate(NOZZLE_GATE_POS))

    # Ahead of the stack, the pump row: both Kamoer assemblies in one lying
    # pose (depth west about Y, then rolled +90° about X so the elbows ride
    # the +Z face, free collets facing west at the crest), each translated
    # by its POS tuple. Each pump's two elbow stations straddle its width;
    # the funnel's spout descends between P-A's stations onto its head-top
    # clearance, and P-B's forward slide keeps its aft elbow ahead of the
    # source-select east bank.
    pump = _load(PUMP_ASSEMBLY)
    lay = _rot(_rot(pump, (0, 1, 0), -90.0), (1, 0, 0), 90.0)
    placed["pump-a"] = lay.translate(PUMP_A_POS)
    placed["pump-b"] = lay.translate(PUMP_B_POS)
    for name in PUMP_OUTLET_AIM:
        placed[name] = _reaim_pump_outlet(placed[name], name)
    for name in PUMP_INLET_AIM:
        placed[name] = _reaim_pump_inlet(placed[name], name)

    # The pump-inlet union tees, hanging in the junction column: each one
    # stands on the line between the two collets it butts (`junction`), run
    # collinear with the pair and branch swung east at its pump.
    tee = _load(TEE_CONNECTOR)
    for name in JUNCTION:
        centre, run, branch, _stub = junction(name)
        placed[name] = _aim(tee, run, branch).translate(centre)

    # Pump-discharge junctions Y-D/Y-G (topology + solved poses in the DISCHARGE_* block above).
    # A 90° elbow turns each source valve's port off the stack, rolled so its free leg aims at the
    # divider outlet it feeds; each flavor's two elbows meet at a PP2308E two-way divider — the real
    # Y connector — seated in the open air over the pump row, tilted so its two parallel outlets
    # face back at the elbows (stem −Y toward the pump discharge it will later take). Each LLDPE run
    # is then one straight tube from an elbow's free collet into a divider outlet.
    elbow = _load(ELBOW_CONNECTOR)
    for name in DISCHARGE_ELBOW:
        collet = _discharge_collet(name)
        placed[name] = _place_elbow(elbow, collet[0], collet[1], elbow_free_dir(name), ELBOW_STUB)
    divider = _load(DIVIDER_CONNECTOR)
    for name in DISCHARGE_DIV:
        placed[name] = _place_divider(divider, name)

    # The nozzle-outlet elbows — each bare east port turned up into the +X wall pocket the
    # cold core's boss chain opens (OUTLET_ELBOW).
    for name, port in OUTLET_ELBOW.items():
        collet = noz_collet(port)
        placed[name] = _place_elbow(elbow, collet[0], collet[1], OUTLET_FREE, ELBOW_STUB)

    # --- Zone B, the band above the cold core: the WATER DECK, lying on the
    # foam-cap top. The pump lies across the bay (nudged east) with its barbs on
    # the ±Y faces; the ASSE chain runs along the aft strip, its vent weeping into
    # the pan on the cap, and the split + V-K stand in the aft strip's east void.
    #
    # The power assembly, the PCBA and the DC block are carried in the BOM and
    # built as trays; their STEPs are the three paths above, unplaced.
    placed["seaflo-pump"] = _rot(
        _load(SEAFLO_STEP), (0, 0, 1), SEAFLO_YAW
        ).translate((SEAFLO_POS[0], SEAFLO_POS[1], foam_cap_top()))
    # The basin's own origin, which `rail_offset()` speaks from: the walls centred
    # on the vent column, the back face on the foam cap's rear edge. `_at` anchors
    # on a bounding box, and the basin's reaches out to its flange tips, so the
    # flange's width is what separates the two X's below.
    _vent_xy = bfp_terminal("vent-tip")[0]
    _pan_x = _vent_xy[0] - DRIP_VENT_INSET
    _pan_y = FRONT_DEPTH + fb.ylen - DRIP_PAN_Y
    _pan_z = drip_pan_seat()
    placed["drip-pan"] = _at(_load(DRIP_PAN_STEP),
                             _pan_x - _pan.FLANGE_W, _pan_y, _pan_z)
    _rail_dx, _rail_dy, _rail_dz = _pan.rail_offset()
    placed["drip-pan-rails"] = _at(_load(DRIP_RAILS_STEP),
                                   _pan_x + _rail_dx, _pan_y + _rail_dy,
                                   _pan_z + _rail_dz)
    placed["water-split"] = _rot(
        _rot(_load(WATER_SPLIT_STEP), (1, 0, 0), SPLIT_ROLL), (0, 0, 1), SPLIT_YAW
        ).translate(SPLIT_POS)
    placed["flow-regulator"] = _rot(
        _load(FLOWREG_STEP), (0, 0, 1), FLOWREG_YAW
        ).translate(flowreg_pos())
    placed["discharge-chain"] = _load(DISCH_CHAIN_STEP).translate(DISCH_CHAIN_POS)

    # V-K, the fill/shutoff solenoid, on its cradle in the aft strip's east void,
    # placed unturned: inlet −Y off the split's north run, outlet +Y wrapping west
    # to the suction. Same frame its two collets take in `vk_terminal`.
    placed["vk-fill-valve"] = _rot(
        _load(BEDUAN_STEP), (0, 0, 1), BEDUAN_YAW
        ).translate(BEDUAN_POS)

    # The two electronics modules, each seated on four boss columns of the foam cap. Both are
    # placed by their own centre landing on the cap's deck-mount centre, so their mounting holes
    # land on the columns by construction. `pcba_pose` is the same transform `pcba_port` reads.
    _board, _board_at = pcba_pose()
    placed["pcba"] = _board.translate(_board_at)
    _psu_ctr, _psu_pts, _psu_top = deck_mount("psu")
    _psu = _rot(_load(MEANWELL_STEP), (0, 0, 1), PSU_YAW)
    _psu_bb = _psu.BoundingBox()
    placed["psu"] = _psu.translate((
        _psu_ctr[0] - (_psu_bb.xmin + _psu_bb.xmax) / 2.0,
        _psu_ctr[1] - (_psu_bb.ymin + _psu_bb.ymax) / 2.0,
        _psu_top - _psu_bb.zmin))

    # The power block, in the strip between them. Each body's own mount pattern lands on
    # the cap's station, so nothing here picks a coordinate.
    _relay_ctr, _relay_pts, _relay_top = deck_mount("relay-1")
    _relay = _rot(_load(RELAY_STEP), (0, 0, 1), RELAY_YAW)
    _relay_bb = _relay.BoundingBox()
    # Z = 0 in the relay's own frame is its PCB underside — the plane that lands on the
    # column tops. Its pins hang below it.
    placed["relay-1"] = _relay.translate((
        _relay_ctr[0] - (_relay_bb.xmin + _relay_bb.xmax) / 2.0,
        _relay_ctr[1] - (_relay_bb.ymin + _relay_bb.ymax) / 2.0,
        _relay_top))
    _hub_ctr, _hub_pts, _hub_top = deck_mount("ac-hub")
    _hub = _load(AC_HUB)
    _hub_mounts = tuple(_achub.LAYOUT.mount_places)
    _hub_at = (sum(p[0] for p in _hub_mounts) / len(_hub_mounts),
               sum(p[1] for p in _hub_mounts) / len(_hub_mounts))
    placed["ac-hub"] = _hub.translate((
        _hub_ctr[0] - _hub_at[0], _hub_ctr[1] - _hub_at[1],
        _hub_top - _hub.BoundingBox().zmin))
    _gnd_ctr, _gnd_pts, _gnd_top = deck_mount("ground")
    _gnd = _load(GND_STACK)
    _gnd_bb = _gnd.BoundingBox()
    placed["ground-stack"] = _gnd.translate((
        _gnd_ctr[0] - (_gnd_bb.xmin + _gnd_bb.xmax) / 2.0,
        _gnd_ctr[1] - (_gnd_bb.ymin + _gnd_bb.ymax) / 2.0,
        _gnd_top))

    return {n: (s, COLORS[n]) for n, s in placed.items()}


def _port_frame():
    """The shared port-band geometry: (x_lo, x_hi, y_wall) — the pack's inner
    walls the panel bodies seat against."""
    placed = build()
    bbs = [_boxes.boxed(s) for s, _c in placed.values()]
    x_lo = min(b.xmin for b in bbs)                # -X inner wall
    x_hi = max(b.xmax for b in bbs)                # +X inner wall
    # The back wall does NOT sit on the foam's back face — it stands one
    # REAR_STANDOFF behind it, and the panel bodies seat against the wall.
    y_wall = max(b.ymax for b in bbs) + REAR_STANDOFF
    return x_lo, x_hi, y_wall


def front_wall_y():
    """The front wall's INNER face — the pack's frontmost point stood off by
    FRONT_STANDOFF, the same rule enclosure.py sizes the box by. Read by
    panel_bodies() so the DERPIPE seats on the wall the box actually has."""
    placed = build()
    return min(_boxes.boxed(s).ymin for s, _c in placed.values()) - FRONT_STANDOFF


# The order back_wall_ports() returns its holes in, and so the order panel_bodies()
# seats the through-wall bodies in.
BACK_PORT_ORDER = ("bulkhead-flavor-b", "bulkhead-flavor-a", "bulkhead-carb",
                   "bulkhead-water", "c14-inlet")


def back_port_station(name):
    """Where a rear-panel body sits on the wall: (x, z), by the name it is seated
    under. The one reading of a station — the hole, the body and the port share it."""
    holes = {n: h for n, h in zip(BACK_PORT_ORDER, back_wall_ports())}
    return holes[name][1], holes[name][2]


def back_wall_ports():
    """Through-holes the rear panel needs: (kind, x, z, *size) in world
    coords — 'round' (a diameter) or 'rect' (x, z size). enclosure.py cuts
    these through the back pieces' +Y wall. Every external connection lands
    here, in the band above the cold core; the bodies hang in the band's
    open rear half. Inventory: ../back-panel/README.md."""
    d = PORT_BULKHEAD_D
    r = PORT_NUT_D / 2.0
    p = PORT_NUT_D + PORT_NUT_GAP                  # umbilical pitch: nut + margin, so nuts clear
    dz = p * (3.0 ** 0.5) / 2.0                    # triangular-cluster vertical span
    z_mid = UMBILICAL_Z_FLOOR + r + dz / 2.0       # lower nuts ride the lip band
    return [
        # Faucet umbilical: two flavor bulkheads on the lower row, the carb-water
        # (blue-ringed) bulkhead at the top vertex — the densest-three-circle
        # triangle the tube bundle packs into (back-panel README §"Bulkhead array").
        # Neither flavor hole carries an accent ring, so which one is A is free: B
        # takes the west station and A the east, the order their runs arrive in.
        ("round", UMBILICAL_X - p / 2.0, z_mid - dz / 2.0, d),   # flavor B
        ("round", UMBILICAL_X + p / 2.0, z_mid - dz / 2.0, d),   # flavor A
        ("round", UMBILICAL_X,           z_mid + dz / 2.0, d),   # carb-water (top vertex)
        # The utility pair: the tap-water bulkhead mid-panel, and the C14
        # mains inlet over the power assembly its cordage drops to.
        ("round", WATER_BACK_X, WATER_BACK_Z, d),
        ("rect", C14_BACK_X, C14_BACK_Z, PORT_C14_W, PORT_C14_H),
    ]


def port_footprint(hole):
    """(width, height) the clamping hardware of one back_wall_ports() hole
    occupies on the panel FACE — a bulkhead nut, or the C14's flange. Far wider
    than the through-hole, and it is what crowds the neighbours, the walls, and
    the ceiling, so anything sizing a wall to the port field measures this."""
    if hole[0] == "rect":
        return PORT_C14_FLANGE_W, PORT_C14_FLANGE_H
    return PORT_NUT_D, PORT_NUT_D


def front_wall_ports():
    """Through-holes the front panel needs: (kind, x, z, *size), same shapes
    as back_wall_ports. enclosure.py cuts these through the front pieces' −Y
    wall. One port: the CO2 inlet the DERPIPE threads through."""
    return [("round", CO2_INLET_X, CO2_INLET_Z, CO2_HOLE_D)]


_PANEL: dict | None = None


def panel_bodies():
    """The connector bodies seated through the enclosure walls — four JG
    bulkhead unions and the C14 receptacle on the rear panel (the faucet
    umbilical, the tap-water inlet, the mains inlet), the DERPIPE CO2 inlet
    on the front panel. Their outboard ends stand proud of the walls, and
    enclosure.py sizes the box from build()'s bbox — so they place here and
    enclosure_assembly.py adds them to the rendered assembly.

    Memoized like build(): the port frame, `_lines._frames()` and the scorecard
    each ask for these, and every one would otherwise reload the same fitting
    STEPs and re-box the pack the wall inset reads."""
    global _PANEL
    if _PANEL is None:
        _PANEL = _panel_bodies()
    return _PANEL


def _panel_bodies():
    _x_lo, _x_hi, y_wall = _port_frame()
    y_out = y_wall + WALL                          # rear-panel outer face
    bodies = {}

    jg = _load(JG_BULKHEAD)                        # +Y outward, origin on the panel face
    names = list(BACK_PORT_ORDER)
    for hole in back_wall_ports():
        kind, hx, hz = hole[0], hole[1], hole[2]
        if kind == "rect":
            bodies[names.pop(0)] = _load(IEC_C14).translate((hx, y_out, hz))
        else:
            bodies[names.pop(0)] = jg.translate((hx, y_out, hz))

    # DERPIPE CO2 inlet on the front panel: 5/16" PTC collet outboard, wrench
    # hex, NPT stub through the hole reaching inboard toward the GASHER → WR1110
    # chain. The reference model's outboard collet face is at its Y origin, so
    # it seats the same outboard reach the two placeholder cylinders did.
    y_front_out = front_wall_y() - WALL            # front-panel outer face
    bodies["co2-inlet"] = _load(DERPIPE_STEP).translate(
        (CO2_INLET_X, y_front_out - 2.0 - DERPIPE_BODY_L, CO2_INLET_Z))
    # The GASHER check screws onto that stub. Its socket mouth has to land ON
    # the stub's shoulder, not near it, and this is the one place both bodies
    # are in hand — build() places the check before the wall it would have to
    # read exists.
    _stub_tip = _boxes.boxed(bodies["co2-inlet"]).ymax
    assert abs(_stub_tip - CO2_GASHER_Y) < 1e-6, (
        f"the GASHER's socket stands at y={CO2_GASHER_Y:g}, but the DERPIPE's "
        f"stub ends at y={_stub_tip:.6g} — the pair is not made up")

    return {n: (s, COLORS[n]) for n, s in bodies.items()}


FUNNEL_STEP = _repo / "hardware" / "printed-parts" / "zone-c" / "hopper-funnel" / "hopper-funnel.step"


_FUNNEL = None


def placed_funnel():
    """The static funnel (hopper_funnel.py, its own frame: collar-centre origin, z 0 = brim
    underside) seated in the top-wall opening: rotated FUNNEL_ROT about its own Z, then
    translated to FUNNEL_CX/CY with the brim underside on the box's outer top. enclosure.py
    cuts the opening from the same placement, so funnel and hole cannot drift apart.

    The drain hangs off its spout, so segment 4 anchors on this body — `_lines._frames()`
    carries it alongside the panel bodies. Memoized like build(): `enclosure._dims()` boxes
    the whole pack to size the wall, and the funnel and the routed drain both ask for it."""
    global _FUNNEL
    if _FUNNEL is None:
        _FUNNEL = _placed_funnel()
    return _FUNNEL


def _placed_funnel():
    import enclosure                                # imports this module: deferred to call time

    return (_load(FUNNEL_STEP)
            .rotate((0, 0, 0), (0, 0, 1), FUNNEL_ROT)
            .translate((FUNNEL_CX, FUNNEL_CY, enclosure._dims().outer[5])))


def funnel_drain():
    """The hopper's drain in world: the spout exit annulus centre. The neck stands on the
    funnel's own offset off the collar centre, and the spout tip is the placed body's lowest
    point — so the port rides the part, whatever the basin is sized to or seated on."""
    return (FUNNEL_CX + _funnel.neck_dx, FUNNEL_CY,
            _boxes.boxed(placed_funnel()).zmin)
