"""The enclosure's requirements as a single pass/fail scorecard — the one place the
appliance's printable + assembleable rules are enumerated as executable checks,
computed from the placed geometry (the same solids the pack check already builds).
Printed at the tail of every `enclosure_assembly.py` run, so the agent and a human
read the same verdict from the same shapes — a result no one can narrate around.

Modeled on the board's `hardware/pcb/pcba/scorecard.ts`. Two kinds of check:

  - GATE — a manufacturability requirement that must hold to PRINT + ASSEMBLE the box
           as it stands. A failing gate is a box you cannot build; only pack-closes
           blocks the export today, the rest report until gating turns on.
  - GOAL — the realization work this whole effort exists to drive, reported as a
           `score` (0..100), not a gate — the box still builds while it converts.

The board had ONE goal (take every connection off the autorouter onto deliberate hand
copper). The enclosure has SIX axes, one per thing every component owes:

    mounted — FOCUS. The feature that fastens the component is printed INTO another placed
              part, the way the board's four boss columns stand in the cold core's cap.
              Resting on a part is not being mounted, and neither is capture or adhesive.
    placed  — deferred. Placement criteria are DEFINED in code (expected face-to-datum
              measurements) and currently HELD. "Foam is against the back-bottom",
              with "against" pinned to numbers the scorecard measures.
    located — deferred. Every connector (tube + wire) has a POSITION on the component — a
              point on the body the scorecard confirms is on-surface. A connection has no
              path until both its ends are located, so this precedes routed.
    shaped  — deferred. Real geometry, not a placeholder box/cylinder.
    routed  — deferred. Every connection (fluid + water + CO2 + refrigerant + electrical) a real 3D
              path (bend radius, length, clearance), not endpoints + an external graph.
    held    — deferred. A printed holder that fastens the component to the enclosure (a
              few bosses + screws, or a tray-with-bosses that itself fastens) — not a
              free solid resting in a collision-checked void. Looser than `mounted`: a
              tray whose own holders are not printed into what it sits on counts here
              and not there.

The focus is `bend-radius` and `mounted`, in that order, and the card prints both above the
blocks they live in — one is a gate and one a goal, so no single block carries the pair. Every
other axis is gray behind them. Bend radius is what says the pack is not arranged yet: a corner
short of its stock's minimum is a tube that cannot be built, most of them are bound by where
their two ends STAND, and the ends that bind them are placements — so driving it is moving
bodies, and nearly every body has some moving left to do.
The score is by AUTHORSHIP, not by "it doesn't collide": a bounding box that happens not
to overlap is the enclosure's version of the autorouter's accidentally-clean net —
crediting it would count the box-thinking this effort exists to remove as progress. So
`shaped`/`held` are read from the declared COMPONENTS registry, `placed` from measured
face-to-datum rules and `located` from measured port positions (both authored per component),
and `routed` from the fluid + CO2 + refrigerant + wiring topologies (a connection counts only once a
real path exists). Prose for the why — and the lessons — is in requirements.md.
"""

from __future__ import annotations

import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _boxes  # noqa: E402  — optimal bounding boxes, memoized once per placed solid
import need  # noqa: E402  — what a run connects (span, axis split, detour), before what it rides
import _contents as contents  # noqa: E402  — the manifold ports derive from the pack's own placement

# The cold core's own module. Every front foam port names a STATION the shell is
# cut with, so a bore that moves in the shell moves its port with it. `_contents`
# has already put the cold-core directory on the path.
import _cold_core_interface as _cc  # noqa: E402

# The rear panel's through-wall fittings' own modules, for the same reason: a
# station's reach off the wall is the fitting's figure, not one retyped beside it.
# `_contents` has already put both directories on the path.
import jg_bulkhead_union as _jg  # noqa: E402
import iec_c14_inlet as _c14  # noqa: E402

# Minimum solid-to-solid distance. cadquery 2 binds OpenCascade as OCP; the guarded import
# leaves `_HAVE_EXACT` false when it is absent, and `_solid_gap` raises.
try:
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound
    from OCP.gp import gp_Pnt
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.TopTools import TopTools_ListOfShape
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    _HAVE_EXACT = True
except Exception:  # pragma: no cover - environment guard
    _HAVE_EXACT = False

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_TOPOLOGY = _repo / "hardware" / "topology" / "fluid-topology.md"
_WIRING = _repo / "hardware" / "wiring" / "ac-wiring-schedule.md"

# ── Standards / floors ──────────────────────────────────────────────────────
# Provisional inter-part clearance floor: FDM print tolerance + a hand's assembly
# margin. NOT yet ratified — the first directed step (real footprints + a ratified
# clearance standard) sets this and the TOUCHING_OK set below. Grow context keep-outs
# later (tube bend radius, tool/wrench access, condenser airflow) as their own gates.
CLEARANCE_FLOOR = 1.0
SLIP_TOL = 5.0        # piece∩piece volume under this = a slide-fit seam (matches _report_split)
CLASH_TOL = 1.0       # solid∩solid volume over this = a real overlap (matches enclosure_assembly)
BED_TOL = 1.0         # a printed piece within this of the bed still "fits" (matches _report_split)
REPORT_NEAR = 6.0     # only rank part-pairs closer than this (keeps the clearance detail focused)
DETAIL_MAX = 40
FOCUS_DETAIL_MAX = 140  # the row cap on the focus axes; both carry more open items than DETAIL_MAX
# The two focus axes, in the order the card leads with them. Every surface that renders this
# scorecard — the terminal below, the viewer's modal — reads the order from here.
FOCUS_IDS = ("bend-radius", "mounted")


# ── The component registry — the reviewable heart ───────────────────────────
# Every solid the pack places, with its per-axis state DECLARED (not inferred from the
# shape): `kind` is geometry authorship (shaped), `held` is the holder state (held),
# `sourced` is whether a real selected part / finished print exists. build_scorecard
# asserts these names equal the placed set, so a new part can't be added without
# declaring what it still owes. As holders get built, flip `held`; as placeholders
# become real STEP/engineered parts, flip `kind` — and the score moves. Placement rules
# (the placed axis) live separately in PLACEMENT_RULES, keyed by the same names.
@dataclass
class Component:
    name: str
    kind: str        # "real" (imported STEP / engineered) | "placeholder" (box/cylinder)
    sourced: bool    # a real selected part or finished printed-part design exists
    held: str        # "none" | "wall-capture" | "shell-facet" | "bosses" | "tray" | "cradle"
                     #        | "floor-capture" | "cap" | "rails"
    note: str = ""

    @property
    def is_real(self) -> bool:
        return self.kind == "real"

    @property
    def is_held(self) -> bool:
        return self.held != "none"


def _c(name, kind, sourced, held, note=""):
    return Component(name, kind, sourced, held, note)


COMPONENTS = [
    _c("foam-assembly",     "real",        True,  "floor-capture", "cold core; yawed a quarter turn so its short axis runs across the machine, its bottom cap's lid flat on the floor slab, flush against the seams at the sides and back. Unfastened by design — the floor carries it, the seam posts fence it"),
    # Zone D — the refrigeration stratum, stacked: compressor on the floor, condenser above it
    _c("compressor-shroud", "real",        True,  "none", "the donor compressor UPRIGHT in its sheet-metal shroud (cut-parts/compressor-shroud), standing on the floor slab one SEAM_CLEAR_LIFT up and centred across the band the cold core opens. Upright is the compressor's constraint — gravity-fed oil pickup — so the shroud's open face points down and the turn is a yaw: its single copper-bearing face reads +Y across the machine corridor at the core, and its AC gland +X. Seat, plan register, capture bosses and the compressor's own grommeted foot pads: TBD"),
    _c("condenser+fan",     "placeholder", True,  "none", "harvested donor block with the factory filter-drier brazed to its outlet, standing over the shroud on its 151 with its airflow axis ACROSS the machine and its exhaust face +X, the wall it stands against. Only its 56 runs across, at the +X end, so a 125 mm lane stays open at the −X end of the band. Shelf, ear pads and the two side grilles the crossing needs: TBD"),
    # Front-panel / opening
    _c("display",           "real",        True,  "shell-facet", "Waveshare 4.3B: 45° facet housing spanning the front-top's full width, the glass centred on it (bezel counterbore + PCB through-hole)"),
    _c("hopper-funnel",     "real",        True,  "none", "removable cast silicone basin, INTEGRAL to the shell: the printed top face is cut with the collar's own opening (`enclosure._hopper_hole`, taken off hopper_funnel's dims at the placed centre), the collar drops through it, and the flat brim flange — overhanging the collar all round — bears on the one `brim_margin` of top wall the hole is asserted to keep on every side. Directly behind the display facet, one `hopper_front_ledge` of wall between the facet's back plane and the frame. The opening crosses the Y seam, so both top pieces take their share of the cut (`enclosure._hopper_cut`) and the collar bridges it. No fastener pattern of its own — it lifts straight out"),
    # Zone B — the WATER DECK, in the rear band of the cap the shelf's front third leaves
    _c("seaflo-pump",       "real",        True,  "none", "SEAFLO 22-series 12 V 1.3 GPM diaphragm pump (reference/seaflo-22-pump). Lies motor-axis along Y — the only axis it fits, being longer between its ends than the cap is wide — head and feet forward, the motor can cantilevering aft over the clear cap behind them. Its two 3/8\" barbs are molded into the head casting and leave its ±Y side faces, which this yaw puts on the machine's ±X: discharge east over the cold core's port column, suction west at the fittings lane. Its base foot is a fraction of its footprint, and it is the one body the box's DEPTH gives way to. Isolation mounts to the foam cap TBD"),
    _c("suction-chain",     "real",        True,  "none", "MAACFLOW 3/8\" barb + PP450822E 1/4\" PTC, made up as one piece (reference/seaflo-suction-chain) — the discharge chain's two end fittings with nothing between them, since nothing holds pressure off the pump on the inlet side. LIES DOWN along Y in the slot between the casting's east flank and the stand's aft row, laid by the discharge chain's own turn: barb AFT at the stub, collet FORWARD at V-K, so both of its runs meet a mouth facing along their own axis and neither has to turn over onto it. Standing it in the open pocket is not available — a chain on end there faces its barb at the ceiling, and a hose fed from a barb 70 mm below it has to come over the top to get down onto it. Clears the casting by 8.44 and the aft row by 2.50 MEASURED AGAINST SOLIDS; both of those columns read closed off the bounding boxes and both boxes are wrong about it. Seated by its COLLET, the mouth water-4 ends on. Bracket TBD"),
    _c("discharge-chain",   "real",        True,  "none", "MAACFLOW 3/8\" barb + GASHER 1/4\" check + PP450822E 1/4\" PTC, made up as one piece (reference/seaflo-discharge-chain). The pump's barbs are molded into its head — no thread, and the 90° barbed accessory does not fit it — so a stub of 3/8\" braided PVC is the only thing that can leave the discharge, and the 3/8\" ends at this chain's barb. LIES DOWN along Y in the strip ahead of the pump, level with the discharge that feeds it and clear over the board below: barb aft at the pump, collet forward over the cap's front edge, where the fall to the core's water-in begins. Standing it native is not available — it is taller than the discharge stands over a cap it would drop through. Bracket TBD"),
    _c("asse1022-assembly", "real",        True,  "none", "Multiplex 19-0897 ASSE 1022 backflow preventer + PP010822E, GAGIRA coupling, flare38-14ptc (3/8\" flare → 1/4\" PTC) and the clear-PVC vent stub as one chain (reference/asse1022-assembly). Runs FRONT TO BACK down the fittings lane west of the pump — the lane is narrower than the chain is long — with its 1/4\" PTC inlet AFT under the rear-panel water bulkhead it is fed from and its 1/4\" PTC outlet forward at the split. Vent in its native pose, weeping down its own column onto the pan's ground below it. Its Z is not free: the basin's rim and section set it. Nothing holds it: 140 mm of brass with no mounting ear on it, tube-hung on the line. Holder TBD"),
    _c("water-split",       "real",        True,  "none",      "JG PP0208E 1/4\" union tee (reference/water-split); second fitting of the WALL SEQUENCE — tube-hung on the chain's own axis in all three coordinates, its supply mouth one JUNCTION_LEG_LEAD down the line from the chain's outlet. Run along the wall, supply aft at the chain, flavor tap forward at the regulator inline ahead, branch falling to V-K. Chain, split and regulator are one family on one line. Nothing holds any of the three — a push-fit union tee has no ear to bolt. Holder TBD"),
    _c("flow-regulator",    "real",        True,  "none",      "neoFit ABCVU44 1/4\" needle flow control (reference/neofit-flow-control) — the flavor tap's regulator, throttling the manifold's feed to its low working pressure. Third fitting of the WALL SEQUENCE: inline on the split's flavor collet, quarter-turned so both collets lie on Y, its inlet one JUNCTION_LEG_LEAD of straight from the mouth that feeds it — so fluid-1 is that straight, and the outlet fires forward down the wall's open strip with fluid-2 one lean onto V-A's inlet. Every coordinate reads off the split's collet (`contents.flowreg_lane`), so it follows the sequence. Its needle stem stands up, reached over the shelf from the bay. Nothing holds it, as with the two fittings ahead of it. Holder TBD"),
    _c("drip-pan",          "real",        True,  "rails",  "Printed PETG catch basin (printed-parts/enclosure/drip-pan) — a rimmed tray at tray scale, one plan outline at r6 carried through floor, walls and flange. Stands in the fittings loft under the ASSE chain, hung at the plane the chain's underside leaves (drip_pan_seat); in plan its RIM lands on the −X wall's inner face (`contents.drip_pan_west`) and the vent's own column centres it in Y, the flange arriving at the discharge barb's lead ahead of the wall. NOTHING STANDS UNDER ITS FLOOR — the basin lies over the casting, so section beneath it is height charged twice and it comes out of the vent gap above. What carries it is its own RIM: a `drip_pan.FLANGE_W` flange turned out all four ways at the top of the walls, its top face flush with them, on a 45° haunch, leaving `drip_pan.bearing_w()` of flat underside a side. A rail pair printed into the enclosure's back-top piece (`contents.drip_pan_rails`) stands under that band, rooted on the −X wall and running east on the withdrawal axis; the two inboard arrises take the haunches and hold the tray on its column, and a stop bar across their east ends (`contents.drip_pan_stop`) is how far in it goes — the rim's own r16 plan corners carry its east edge back west in the rails' own bands, so the bar spans the whole width to meet the straight run between those arcs. Home is the rim's west edge flush with the wall's inner face. UNFASTENED BY DESIGN — it draws WEST out through the slot in that same wall (`contents.west_wall_ports`) to be emptied, so it carries no `MOUNTED_BY` row"),
    _c("digiten-flow",      "real",        True,  "none", "DIGITEN FL-S402B G1/4\" Hall-effect turbine meter (reference/digiten-flow-sensor) — the dispense sensor: the pulse train off this rotor is what tells the firmware the faucet is open, so the flavor pumps have something to meter against. Inline on the carb-water riser where it crosses the LOFT, yawed a quarter turn so the flow runs aft with the riser and the pigtail boss stands up at the J4 loom. Its rigid axis hangs over the SeaFlo's crown in the loft's EAST pocket, clear east of pump A's two loft lines — which is also the column that keeps the riser monotonic, the cold core's outlet standing east of the meter and the blue-ringed bulkhead west of it. The loft's west lane cannot hold it: pump A's suction and discharge run that lane's whole length a tube over the pump's crown, and a body this long laid there stands in one or the other at every height. Cradle TBD"),
    # The CO2 chain — the side-wall inlet's two inline bodies, wall-hung in the machine
    # corridor behind the refrigeration stratum.
    _c("gasher-co2",        "real",        True,  "wall-capture", "GASHER 1/4\" NPT soft-seat check (reference/gasher-check-valve) — the CO2 inlet's check, female socket screwed onto the DERPIPE's male stub and male stub facing the regulator, flow west into the corridor. Held by the fitting it is made up on, which the east wall holds: no bracket of its own"),
    _c("wr1110",            "real",        True,  "none", "Interstate Pneumatics WR1110 fixed-90 PSI secondary regulator (reference/wr1110-regulator), female 1/4\" NPT both ends, one tube hop inboard of the check ON the same axis — inline, the pose the machine corridor's straight-line depth takes: the chain lies along the corridor under every line its floor carries. A PP450822E takes the check's stub to tube and a PP010822E in each of its own ends takes it back. Cradle TBD (enclosure-mechanical Open #6, and it hangs in this pocket)"),
    # Zone B — the ELECTRONICS SHELF, on the cap's own deck-mount columns
    _c("pcba",              "real",        True,  "none", "Controller board (pcb/pcba), hung on the +X WALL a storey over the power block rather than standing on the cap — the two boards one above the other on the same flank, so every electrical body is on the far side of the machine from every wet one. The board is 85.05 x 72.85 as fabbed and its four mounting holes are fixed. Three faces seat it, all of them faces the brick below already answered to: EAST on `CORE_EAST_FACE`; FOOT one clearance floor over that brick's crown, so the supply's loss rises through a gap instead of into a board laid on it; AFT one hug forward of `c14_inboard_y()`, the receptacle being the one body that reaches into the bay at the height this board stands. A quarter roll about its own long axis lays that axis fore and aft down the flank, so only the board's thickness reaches inboard. Wall bosses and their pattern: TBD"),
    _c("psu",               "real",        True,  "none", "Mean Well IRM-90-12ST 12 V open-frame supply (reference/meanwell-irm90), hung on the +X WALL rather than standing on the deck. The brick is 109 × 52 × 33.5 and the band between the pump's aft casting and the rear seam lip is 109 of Y at this flank, so the LONG axis lies fore and aft, the 52 stands up, and only the 33.5 reaches inboard — its whole plan footprint is a 33.5 mm strip against the wall instead of a 109 × 52 island under the bay. Its east face is on `CORE_EAST_FACE`, clear of every post, pod and plug the Y seam puts in the ±X rib band; its aft face is on the rear seam lip's own standoff, under the C14; its lower long edge rests on the cap lid. Both terminal blocks look INBOARD, off the face a screwdriver reaches. Nothing wet stands over it. NOTHING FASTENS IT YET — the wall bosses are not built, so it carries no `MOUNTED_BY` row; relay #2 and the DC block are not yet stationed"),
    _c("relay-1",           "real",        True,  "none", "Teyleten 3.3 V opto-isolated relay module #1 (reference/teyleten-relay) — the compressor's 120 VAC hot switch. It LIES DOWN on the cap's lid in the aft-east deck band the two boards left, its long axis fore and aft on the band's own deep axis and its shallowest dimension standing up, and it carries the AC hub on its back. West face one clearance floor off the pump casting's east flank, the lane's own west wall; aft face on the rear seam lip's standoff. Its pins hang below its PCB. Bracket: TBD"),
    _c("ac-hub",            "real",        True,  "none", "The printed AC hub carrying its three Wago 221-413 lever nuts (printed-parts/electronics/ac-hub) — the H / N / G mains distribution. It lies FLAT on the relay's back, one clearance floor over that module's crown and flush with its west face, wells opening UP with each lug's wire half standing proud where a hand and a ferrule reach it. Its aft face is on the rear seam lip's standoff, so the mains block sits beside the inlet it distributes with the fluid cluster's whole width of wall between it and any joint that can weep, and nothing wet anywhere over it. Its floor ends at the wells and it carries NO hold-down of its own: it is a tray, and the joint that will hold it is a printed one grown into whatever body ends up carrying it"),
    _c("ground-stack",      "real",        True,  "none", "The chassis-ground ring-terminal stack (reference/ground-ring-stack) — the single-point ground bus, ON THE +X WALL over the hub, the last of the electrical bodies off the cap. An M3 x 10 SHCS through an external-tooth washer clamps a fan of green ring lugs — one per exposed-metal load, plus the C14 earth off the G Wago — down onto the column's insert; the lugs bolted together are the bus. The one station whose screw clamps a lug stack rather than a module. NOTHING FASTENS IT YET — the wall bosses are not built, so it carries no `MOUNTED_BY` row"),
    # Rear-panel bodies, clamped through the wall in ONE ROW above the water deck
    _c("bulkhead-flavor-a", "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut"),
    _c("bulkhead-flavor-b", "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut"),
    _c("bulkhead-carb",     "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut; the accented (blue-ringed) hole, in the middle of the three so neither flavor can be mistaken for it"),
    _c("bulkhead-water",    "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut, over the ASSE chain's inlet column"),
    _c("c14-inlet",         "real",        True,  "wall-capture", "C14 mains inlet: rear-wall cutout + its own flange, over the PSU its cordage drops to"),
    _c("co2-inlet",         "real",        True,  "wall-capture", "DERPIPE 5/16\" PTC × 1/4\" NPT (reference/derpipe-co2-inlet): east side-wall hole + its own NPT thread, low in the machine corridor behind the refrigeration stratum. Red accent ring at the panel opening; the customer's cylinder stands beside the machine and its short red tether lands here"),
    # Zone C — the valve manifold, in the front column ahead of the core
    _c("source-tray-assembly", "real",     True,  "none", "The manifold's SOURCE pair — V-A on tap water, V-B on the hopper — on one printed two-valve tray (printed-parts/valve-manifold/two-valve-tray), the first of the four identical two-valve cradles to be placed. Lies flat, plate down and valves up, ports along Y, both INLETS aft and both OUTLETS forward; the cell is symmetric under a half turn so the tray permits either clocking and fixes neither. Its east seat stands on the hopper spout's own column — V-B gates a gravity drain, which is the one line in this machine that cannot be routed around anything — and its coils ride at the top of a column standing on the refrigeration stratum's roof, with the basin overhead as their ceiling. Nothing holds it: the plate is 9 mm of floor with 56.6 mm of valve on it, and the stack pitch, the standoff that sets it and whatever seats the five are the tray README's own Open item"),
    _c("tee-y-a",           "real",        True,  "none", "JG PP0208E union tee (reference/tee-connector — McMaster 51175K143 stand-in) — Y-A, the WEST half of the manifold's junction. Its RUN stands UP the west column: V-A's outlet a stack pitch above and V-C's inlet below are two ports on one line, which is what a run is, so the tap-water source falls straight through the fitting to channel A's select. Its BRANCH reaches EAST at Y-B's, and the two meet on fluid-6 — the H's crossbar, which is what puts all four ports on one hydraulic node. `contents.junction_tee_pos` derives all three coordinates from the four collets and the fitting's own reach; the column stands `contents.junction_column_x` outboard of its seat, which is the branch reaching further than half the valve pitch. Tube-hung on its own three legs; no cradle, no holder"),
    _c("selects-tray-assembly", "real",    True,  "none", "The manifold's SELECTS pair — V-C and V-D, the two channel gates — on the second of the four identical two-valve trays, in the source pair's own column one `contents.tray_stack_pitch` under it, coils packed up under that tray's plate. Same part, same flat pose, ports along Y; clocked the OTHER way round — both INLETS forward at the junction that feeds them, both OUTLETS aft at the pump row still to come, with the core's front face standing `SOURCE_TRAY_AFT_BAND` behind those collets. The `TRAY_STACK_GAP` over its coils is the depth a valve's corner posts stand in the sockets of the plate above, so a valve lifts out of its seat with the stack made up. Stands in the top third of the condenser's intake lane. Nothing holds it, and nothing yet stands it off the tray above — the standoff the pitch implies is the tray README's own Open item"),
    _c("tee-y-b",           "real",        True,  "none", "JG PP0208E union tee (reference/tee-connector — McMaster 51175K143 stand-in) — Y-B, the EAST half of the manifold's junction. The same fitting as Y-A in the same pose yawed the other way, one seat pitch east, so the two stand abreast with their branches facing each other. Its run stands up the east column, V-B's outlet over V-D's inlet, carrying the hopper source down to channel B's select; its branch reaches WEST at Y-A's across fluid-6. Every mode opens one of {V-A, V-B} and one of {V-C, V-D}, so the traffic the pair carries is one source to one select, straight down a column or across the bar. Tube-hung on its own three legs; no cradle, no holder"),
    _c("bag-a-tray-assembly", "real",      True,  "none", "The manifold's BAG-A pair — V-E drawing from reservoir A, V-F returning to it — on the third of the four identical two-valve trays, and the column's bottom seat: under this plate is the compressor shroud's roof, and `contents.tray_column_floor` is the band between them, shorter than one `tray_stack_pitch`. Same part, same flat pose, ports along Y. The bag's two ends are V-E's INLET and V-F's OUTLET, and those two face FORWARD at Y-E; V-E-O and V-F-I face AFT at the pump row, so the pair is the first with its two valves seated opposite ways round. Reservoir A rides Y-E's stem, so one line (fluid-15) crosses the machine to the cold core's face and both the fill and the draw are on it — up the lane between this plate's own east edge and the condenser's intake face, so the column is passed on the outside and the band under the plate carries nothing. Stands in the middle third of the condenser's intake lane. Nothing holds it, and nothing yet stands it off the tray above — the standoff the pitch implies is the tray README's own Open item"),
    _c("pump-b",            "real",        True,  "none", "Kamoer KPHM400-SW3B25 peristaltic (reference/kamoer-kphm400) — CHANNEL A's pump, standing UPRIGHT in the front column's west-forward box, motor up, its two head barbs facing aft down the lane at Y-C and Y-D. Upright and here is not a preference: a `fit.py search` over the whole front column at four orientations returns 23 free poses of 20160, and this box is the only one of them that takes the body on end. Its Z is derived rather than picked — the barbs stand on the BAG-A pair's own port plane, so both its tees lie in one plane with the collets they join. Bare pump, no elbow: the barbs already look down the lane its lines run in, so what each takes is a straight 1/4\" adapter. Isolation mounts and holder TBD"),
    _c("tee-y-c",           "real",        True,  "none", "JG PP0208E union tee (reference/tee-connector — McMaster 51175K143 stand-in) — Y-C, channel A's SUCTION junction, where the shared source and the bag draw meet at pump B's inlet. A TEE and not a divider because it reaches BETWEEN trays rather than joining one tray's own pair (../../../topology/fluid-topology.md): a tray only ever lies plate-up, so its two seats stand side by side and their junction can only be a trident, while a junction reaching between two of them has one leg arriving on a different line. Its RUN lies along the PUMP LANE — the strip west of the tray column that both of pump B's lines run down — and its BRANCH stands UP, which is the axis the third leg leaves on: the fall from the selects pair a stack pitch above. `contents.pump_row_tee_pos` derives all three coordinates from the barb its run stands off. Tube-hung on its own three legs; no cradle, no holder"),
    _c("tee-y-d",           "real",        True,  "none", "JG PP0208E union tee (reference/tee-connector — McMaster 51175K143 stand-in) — Y-D, channel A's DISCHARGE junction, splitting pump B's outlet between the bag it fills and the nozzle gate it dispenses through. The same fitting as Y-C in the same pose, one lane-width east of it on its own barb's column, so the two stand abreast in the pump lane on one plane. Run along the lane, branch UP — and this one's branch is the manifold's longest climb, a storey from the front column to the nozzle gate in the loft. Tube-hung on its own three legs; no cradle, no holder"),
    _c("bag-b-tray-assembly", "real",      True,  "cap", "The manifold's BAG-B pair — V-H drawing from reservoir B, V-I returning to it — on the fourth of the four identical two-valve trays, and the first body of the LOFT: the band between the water deck's crown and the ceiling. Same part, same flat pose, ports along Y, and bag A's clocking mirrored — the bag's two ends are V-H's INLET and V-I's OUTLET and those two face FORWARD at Y-H, with V-H-O and V-I-I aft into the junction bay. Its two valves are seated the other way ROUND from bag A's, which is what makes that bay work: V-I-I lands on the column V-J-I takes on the tray facing it, so the two collets Y-G feeds sit on one line and the tee's run passes straight through. It stands at the FRONT of the loft's west lane, clear of the funnel's aft skirt and up over V-K's coil, which is the deck's tallest body under it — forward because Y-H hangs a `divider_reach` ahead of the pair and wants to land over the electronics shelf, at the head of the column reservoir B's line climbs. Its floor is the cap's own lid and its fastening its two mount ears: bolted down the tray's centreline — the one column of it the cap's cavity can answer, its west cell overhanging the core into the −X rib band — to two cap columns that stop under the lid, the PSU's joint. M3 × 16 through ear and lid into a ruthex short in each; the stations stand where the placed ears land (`contents.TRAY_MOUNTS`), and `deck-mounts-land` holds the cap's table to them"),
    _c("vk-tray-assembly", "real",         True,  "cap", "V-K, the tap-water FILL/SHUTOFF solenoid, alone on the MIDDLE of the aft stand's three two-valve rows, one `contents.AFT_TRAY_BAY` behind the bag-B pair. It takes the plate's EAST seat — the one nearest the SeaFlo — so its outlet faces the pump's suction barb across the lane between them and water-4 is the tube that makes the crossing. This plate stands on the plane its own junction opens on — V-J's inlet on `Y-G-3`'s Y (`contents.vk_tray_y`) — so what fixes it is the fitting that feeds it and not the casting in the other lane; the pump packs against its own lane's far end (`contents.seaflo_front_y`) and the two read no body of each other's. Its WEST seat is bare, and that bare cell is the lane fluid-17 comes aft on to reach the gate behind it. Same part, same flat pose, ports along Y as every tray in the manifold. Bolted flat on the cap's lid through its mount ears to cap columns under the lid, M3 × 16 into a ruthex short in each; its stations stand where the placed ears land (`contents.TRAY_MOUNTS`), held by `deck-mounts-land`"),
    _c("nozzle-b-tray-assembly", "real",   True,  "cap", "V-J, the NOZZLE-B GATE, alone on the family's one-seat plate — the twin of the nozzle-A gate's, on the aft stand's middle row beside V-K. A one-seat plate because it is one valve: a two-seat plate with a seat left empty renders a valve that is not in the machine and not in the BOM (`single_valve_tray`). It is clocked the way its two runs leave it — inlet FORWARD at the junction bay Y-G stands in, outlet AFT at the panel field its bulkhead is in — and it packs west onto the SeaFlo's own flank like every row of this stand (`contents.aft_tray_x`), which is the column the two-valve plate's west seat stood on. Bolted flat on the cap's lid through its two mount ears to cap columns under the lid, M3 × 16 into a ruthex short in each; its stations stand where the placed ears land (`contents.TRAY_MOUNTS`), held by `deck-mounts-land`"),
    _c("nozzle-tray-assembly", "real",     True,  "cap", "V-G, the NOZZLE-A GATE, alone on the family's one-seat plate — in the WEST LANE'S FORWARD END, on the lid's own west flank ahead of the pump. It carries no junction of its OWN: V-G-I is fed by Y-D a storey and a half down in the front column, and V-G-O runs alone to its bulkhead — so the plate is placed by those two runs and by nothing else, its X on the column they share (`contents.nozzle_tray_x`), its Y on the forwardmost plane a cap deck column may take (`contents.nozzle_tray_y`). UNTURNED, its two collets on ±Y: the inlet opens FORWARD on the column `fluid-17` climbs onto, so the leg that closes on it is the collet's own axis, and the outlet opens AFT into the band between this plate and the pump's front face, where `fluid-18` turns. Its outlet is one of the only two lines the manifold sends out of the machine, and that is what puts this gate up here instead of in the front column. Bolted flat on the cap's lid through its two mount ears to cap columns under the lid, M3 × 16 into a ruthex short in each; its stations stand where the placed ears land (`contents.TRAY_MOUNTS`), held by `deck-mounts-land`"),
    _c("tee-y-f",           "real",        True,  "none", "JG PP0208E union tee (reference/tee-connector — McMaster 51175K143 stand-in) — Y-F, channel B's SUCTION junction, where the shared source and the bag-B draw meet at pump A's inlet. It stands in the LOFT'S PUMP LANE, the strip between the loft trays' east face and the SeaFlo's west flank that runs the aft stand's whole depth with nothing in it, on the front column's own tee construction (`contents.TEE_ROLL`): RUN along the lane at the stand's port plane, BRANCH UP. The branch takes the shared source's climb out of the front column; the run's aft collet takes the bag-B draw, which comes about in the junction bay and again on this column; the run's fore collet sends the pump's suction forward down the machine, over the electronics shelf and down the front column to a barb a storey and a half below. `contents.aft_row_tee_pos` derives its three coordinates from the lane and the bag pair's aft face. Tube-hung on its own three legs; no cradle, no holder"),
    _c("tee-y-g",       "real",        True,  "none", "JG PP0208E union tee (reference/tee-connector) — the same fitting the manifold's six other junctions are, standing IN THE LANE east of V-K's plate rather than across the bay at the far end of it. Its RUN lies along that lane with one valve on each end — aft at the nozzle-B gate's inlet, forward at the bag pair's fill valve — so the leg `fluid-27` already ran down the lane to reach this junction is now the run itself and its crossing is gone. The BRANCH stands UP into the loft `fluid-22` crosses at. Seated on the plate's east face and its forward face, on `aft_port_z` so neither run leg climbs. Bracket TBD"),
    _c("pump-a",            "real",        True,  "none", "Kamoer KPHM400-SW3B25 peristaltic (reference/kamoer-kphm400) — CHANNEL B's pump, standing UPRIGHT beside channel A's in the front column, same part and same native turn, motor down and both head barbs out the +Y face at the strip behind them. The two are one pose read twice on one lane — same band, same foot, same barb plane, stepped east so the two inner barbs of that row stand a `contents.PUMP_TWIN_PITCH` apart, which is a tube's width and the pack's floor between the two legs that leave them — and what the second one needs is 62.61 mm of width, which is the MOTOR's own square and not the body's box: the part is three stacked solids and only its bottom third is that wide. Its foot stands on the same `contents.FRONT_COLUMN_FLOOR` over the refrigeration stratum's roof that its twin's does, in the front Z seam's own band, and the display's facet roofs the column above it. Bare pump, no elbow, for the reason channel A's is bare. Both of its lines reach the loft, so this is the one pump whose junctions do not stand beside it. Isolation mounts and holder TBD"),
    _c("tee-y-e",           "real",        True,  "none", "JG PP0208E union tee (reference/tee-connector — McMaster 51175K143 stand-in) — Y-E, where reservoir A's fill and draw meet. It joins one tray's own pair, as Y-H does, and it is a TEE and not that trident because of the room it has: it stands in the STRIP between the pump row's aft faces and the bag pair's forward collets, and a fitting 40.13 mm collet to collet cannot lie along a strip that deep. So it stands ACROSS it — both collet axes square to Y, all three collets in one vertical plane, its own diameter the whole of the depth it takes. The RUN lies along X, the axis the strip runs on: reservoir A's line arrives on its EAST collet, straight down the tray-east lane, and the bag DRAW leaves its west one. The FILL takes the BRANCH, which faces down on V-F's own column. A down-facing collet is entered by a rising leg, so it stands a `contents.JUNCTION_LEG_LEAD` over the pair's port plane and both valve legs climb into it (../../../topology/fluid-topology.md). Numbered from the end the BAG rides, as Y-H is. Tube-hung on its own three legs; no tray, no holder"),
]

# ── Pose provenance (the settled set) ───────────────────────────────────────────────────────
# A component's POSE — where it stands and how it is turned — is PROVISIONAL unless it is named
# here. The default is provisional, and it is the state of nearly every body in this pack.
#   `_contents.py` states what each pose FOLLOWS, in one voice. This states which poses the
# following stops at. Named here, a pose is an INPUT to the work and a neighbour's face can be
# priced against. Absent, the pose is PART of the work, and a limit reported against it is a
# limit against a draft (`calibration/Fences.md`, *The frozen first draft*).
#   The value states what is settled, which is narrower than the body. A settled pose still
# moves; moving it costs a reason rather than a line.
#   The ENCLOSURE WALLS are the sixth settled placement and have no row here, having no registry
# entry: they are the envelope, fixed by the brief (`CLAUDE.md`).
#   ROUTES are not poses, and none of them are settled — every run in `_lines.py`, the copper
# between the settled bodies included. `need.py` ranks them; `room.py` reads the bands they cross.
SETTLED = {
    "foam-assembly":
        "The cold core, yawed a quarter turn so its short axis runs across the machine, its "
        "bottom cap's lid flat on the floor slab, flush against the seams at the sides and back. "
        "The yaw is what buys the full width and the floor is what carries it.",
    "compressor-shroud":
        "UPRIGHT on the floor slab, centred across the band the cold core opens. Upright is the "
        "compressor's own constraint — gravity-fed oil pickup — so the turn is a yaw and the "
        "open face points down. The station is settled; the seat, plan register and capture "
        "bosses under it are not built yet.",
    "condenser+fan":
        "Over the shroud on its 151, airflow axis ACROSS the machine, exhaust face +X at the "
        "wall it stands against — the loop's hot end stacked on its own stratum with the band "
        "between them the front Z seam's. The block is still a placeholder; its POSE is not.",
    "display":
        "Centred on the 45° facet spanning the front-top's full width, let into the top-front "
        "corner. The facet is the customer-facing plane of the machine and the glass is centred "
        "on it.",
    "hopper-funnel":
        "The basin resting on the top-wall rim ledge directly behind the display facet, its "
        "spout on V-B's own column: V-B gates a gravity drain, the one line in this machine "
        "that cannot be routed around anything, so the spout's column is the fixed thing and "
        "the basin hangs off it. Settled in WHERE IT STANDS. The closed aft-west corner "
        "(`hopper_funnel.notch_x` / `notch_y`) is not covered by this: the basin is a "
        "customer-facing cast part and a corner taken out of it to clear a fitting clamp is an "
        "open defect, `assembly/enclosure-mechanical.md` Open #8.",
}


def pose(name: str) -> str:
    """`settled` or `provisional` for a component's placement — the default is provisional."""
    return "settled" if name in SETTLED else "provisional"


# The joints closed by a MADE-UP THREAD instead of by a line: two ports screwed into each
# other until the fitting's own shoulder takes up, stated as the port pair rather than the
# body pair because it is the PORTS that mate. A made-up joint is a connection carrying no
# run, which is the one relation `_lines.py` cannot report, so both gates that read a joint
# read it from here: the two bodies meet on purpose (TOUCHING_OK is derived below), and
# neither port owes the other the lead a line would leave on (`port_mates`).
MADE_UP = [
    # The CO2 inlet's check, its female socket run down onto the DERPIPE's male NPT stub.
    (("co2-inlet", "npt-out"), ("gasher-co2", "inlet")),
]

# Unordered part pairs allowed to touch by design — a part resting on another's top, or
# a body reaching into a pan. PROVISIONAL: seeded from the pack's deliberate stacks; the
# clearance gate excludes these, so a sub-floor gap between any OTHER pair is what fails.
# Ratifying this set (and the floor above) is the first directed step.
#   Every pair written out here is the FOAM CAP carrying something: the whole of Zone B
# stands on that one lid, either flat on its face or on the deck-mount columns that stand
# through it. The made-up threads join them — a joint that is tightened metal to metal is
# a contact by construction, so it is read off `MADE_UP` rather than retyped.
#   A declared contact says these two touch. It does not say the module is on the columns that
# are supposed to carry it: a module stood clear of its own rectangle still rests on the lid and
# still lands here, exempt. `deck-mounts-land` is the check that reads that joint.
TOUCHING_OK = {
    frozenset(p) for p in [
        ("foam-assembly", "seaflo-pump"),       # the pump's base flat on the foam-cap top
        ("foam-assembly", "bag-b-tray-assembly"),    # the aft stand's forward plate flat on the cap
        ("foam-assembly", "nozzle-tray-assembly"),   # and the wide plate behind it (`aft_tray_z`)
        ("foam-assembly", "vk-tray-assembly"),       # and the middle row's, on the same lid
        ("foam-assembly", "nozzle-b-tray-assembly"),  # and the nozzle-B gate's, on the same lid
        # The +X WALL COLUMN's two lowest bodies still rest their feet on that lid — hung on the
        # wall in X, stood on the cap in Z. The three above them read the body under them
        # instead, so the cap carries nothing electrical any more.
        ("foam-assembly", "psu"),               # the brick's lower long edge down on the lid's face
        ("foam-assembly", "pcba"),              # the board's lower long edge on the same face
    ]
} | {frozenset((a[0], b[0])) for a, b in MADE_UP}


# ── Connections (the routed axis) — fluid segments + electrical runs ─────────
@dataclass
class Connection:
    id: str
    kind: str              # "fluid" | "wire"
    frm: str
    to: str
    routed: bool = False   # a real 3D path exists — set from _lines.py's authored runs
    blocked: str = ""      # why it cannot be routed as the pack stands (deferred, not removed)


# The sealed refrigerant loop — declared here, not parsed. It binds the three floor/back
# components (compressor, condenser, cold-core evaporator) and lives in NO segment table:
# fluid-topology.md is the beverage manifold, and the wiring schedule is electrical. Its
# topology is verified-by-disassembly in reference/ice-maker/README.md and built in
# assembly/refrigerant-loop.md. Without this the routed axis silently omits the loop the
# whole cold core exists to run. The drier + capillary tube ride the condenser→evaporator leg.
REFRIGERANT_SEGMENTS = [
    ("refrig-1", "compressor-shroud discharge", "condenser+fan inlet"),
    ("refrig-2", "condenser+fan outlet (drier + cap tube)", "foam-assembly evaporator inlet"),
    ("refrig-3", "foam-assembly evaporator outlet", "compressor-shroud suction"),
]

# The tap-water path — declared here for the same reason the refrigerant loop is. It lives in no
# segment table: fluid-topology.md starts at "Tap water source", which is this path's far end, so
# its 28 segments are the beverage manifold downstream of the carbonator. This is the run from the
# rear-panel bulkhead through the backflow preventer, the split, and the V-K fill/shutoff valve to
# the carbonator's water inlet, built in assembly/internal-plumbing.md §2. It is all 1/4" LLDPE and
# steps back up to 3/8" only at the SeaFlo barbs. The ASSE 1022's vent is not here: it terminates
# to atmosphere.
WATER_SEGMENTS = [
    ("water-1", "bulkhead-water tube-in", "asse1022-assembly tube-in (PP010822E → GAGIRA coupling)"),
    ("water-2", "asse1022-assembly tube-out (PI4512F6S + PP061208W, 1/4\" PTC)", "water-split supply (PP0208E 1/4\" tee)"),
    ("water-3", "water-split to-vk (PP0208E 1/4\" tee)", "V-K inlet on the nozzle plate (Beduan 1/4\" QC)"),
    ("water-4", "V-K outlet on the nozzle plate (Beduan 1/4\" QC)", "suction-chain tube-port (PP450822E 1/4\" PTC)"),
    ("water-5", "discharge-chain tube-port (PP450822E 1/4\" PTC)", "foam-assembly water-in"),
    ("water-6", "seaflo-pump discharge (3/8\" barb, molded)", "discharge-chain barb-tip (3/8\" braided-PVC stub, 2 clamps)"),
    ("water-7", "seaflo-pump suction (3/8\" barb, molded)", "suction-chain barb-tip (3/8\" braided-PVC stub, 2 clamps)"),
]


# The CO2 path — declared here for the reason the refrigerant loop and the tap-water path are:
# fluid-topology.md is the beverage manifold downstream of the carbonator, and this path is
# upstream of it. It runs from the front-panel DERPIPE inlet through the GASHER check and the
# WR1110 secondary regulator to the carbonator's bottom-plate CO2 port, and is built in
# assembly/internal-plumbing.md §1. Two segments: the DERPIPE → GASHER joint is a made-up
# 1/4" NPT thread carrying no line, and everything past the regulator's outlet is one run of
# 1/4" LLDPE that ends on the adapter already made up under the vessel's plate.
CO2_SEGMENTS = [
    ("co2-1", "gasher-co2 outlet (PP010822E, 1/4\" NPT M x PTC)", "wr1110 inlet (PP010822E)"),
    ("co2-2", "wr1110 outlet (PP010822E)", "foam-assembly co2-in (through the shell wall onto the vessel's bottom-plate elbow)"),
]


# The carbonated-water riser — declared here for the reason the three paths above are:
# fluid-topology.md's 28 segments are the flavor manifold, and this is the dispense leg
# downstream of the carbonator, `P3 --> Faucet` in fluid-topology-carbonator.mmd. It runs
# from the vessel's bottom-plate outlet on the cold core's front face to the blue-ringed
# rear-panel bulkhead the faucet umbilical plugs into, and is built in
# assembly/internal-plumbing.md §4. All 1/4" LLDPE, insulated either side of the meter's
# own body. The DIGITEN turbine meter splits it in two: the meter is a placed body with a
# collet at each end, so each half anchors on its own port rather than being one run with
# a fitting drawn on it.
CARB_SEGMENTS = [
    ("carb-1", "foam-assembly carb-water-out (PP010822E on the vessel's bottom-plate Port 3)", "digiten-flow inlet (1/4\" PTC collet)"),
    ("carb-2", "digiten-flow outlet (1/4\" PTC collet)", "bulkhead-carb tube-in (JG PP1208E, inboard)"),
]


def load_connections() -> list[Connection]:
    """Every connection the box must route: the fluid tube segments (fluid-topology.md,
    `| N | From | To |`), the electrical runs (ac-wiring-schedule.md, `| AC/DC/SIG/LV-N |
    From | To |`), the sealed refrigerant loop (REFRIGERANT_SEGMENTS), the tap-water
    path (WATER_SEGMENTS), the CO2 path (CO2_SEGMENTS) and the carb-water riser
    (CARB_SEGMENTS). A connection counts as routed only once a real 3D path is
    modeled (_lines.py's authored runs)."""
    conns: list[Connection] = []
    if _TOPOLOGY.is_file():
        row = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
        for line in _TOPOLOGY.read_text().splitlines():
            m = row.match(line)
            if m:
                conns.append(Connection(f"fluid-{m.group(1)}", "fluid", m.group(2).strip(), m.group(3).strip()))
    if _WIRING.is_file():
        row = re.compile(r"^\|\s*((?:AC|DC|SIG|LV)-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
        for line in _WIRING.read_text().splitlines():
            m = row.match(line)
            if m:
                conns.append(Connection(m.group(1), "wire", m.group(2).strip(), m.group(3).strip()))
    for cid, frm, to in REFRIGERANT_SEGMENTS:
        conns.append(Connection(cid, "refrigerant", frm, to))
    for cid, frm, to in WATER_SEGMENTS:
        conns.append(Connection(cid, "water", frm, to))
    for cid, frm, to in CO2_SEGMENTS:
        conns.append(Connection(cid, "co2", frm, to))
    for cid, frm, to in CARB_SEGMENTS:
        conns.append(Connection(cid, "water", frm, to))
    # Routed state comes from the paths _lines.py builds. Deferred import: _lines reads PORTS
    # back out of this module.
    import _lines
    done = _lines.routed_ids()
    short = _lines.blocked_ids()
    for c in conns:
        c.routed = c.id in done
        c.blocked = short.get(c.id, "")
    return conns


# ── Placement rules (the placed axis) — measured expectations, two forms ──
# Each component's INTENDED placement, written as measurements the scorecard checks:
#   (face, max_mm)          — face-to-datum: the component's `face` must sit within
#                             max_mm of the enclosure interior's same face
#                             (enclosure._dims() `inner`). iz0 is the fixed Z=0 floor
#                             (not content-derived), so "z-" is a true "how far off the
#                             floor" check; the other interior faces hug the content, so
#                             "within a millimeter of x-/x+/y+" reads as "this part is
#                             the one against that wall".
#   ("near", other, max_mm) — part-to-part: the exact solid-to-solid gap to `other`
#                             must be at most max_mm. This is how a pack relation is
#                             stated — "receives the funnel" — measured on the real
#                             solids, not their boxes (the clearance-floor gate bounds
#                             the same gap from below).
#   ("clear", other, min_mm) — part-to-part keep-out: the exact solid-to-solid gap to
#                             `other` must be at least min_mm. This is how a held-open
#                             working space is stated — "the under-display channel
#                             stays open" — a deliberate reservation, not an accident
#                             of the pack.
# A component is `placed` when it has rules AND every rule holds; rules defined but
# violated are a visible drift; no rules yet = not started. Every component earns rules
# eventually. Faces: x-/x+ = left/right walls, y-/y+ = front/back walls, z-/z+ = floor/ceiling.
def _declare_placement_rules():
    """The placed axis's measured expectations, built on first use — `placement_rules()`,
    and `scorecard.PLACEMENT_RULES`.

    A `near`/`clear` tolerance may be struck off the pack itself (`contents.pump_twin_gap`
    and its kin read placed boxes), so building this table at import builds the pack. Taken
    when a rule is first read instead.
    """
    return {
        # "Foam is against the back-bottom, full width, standing on its lid" — the
        # canonical example, and the pose the whole thin machine stands on. It seats flush
        # against the SEAMS rather than the walls: the ±X walls stand one boss chain
        # (`_contents.SIDE_RIB_INSET`) off it so the corner posts and boss chains have their
        # full section, and the back wall one wall (`enclosure.rear_seam_clear`) off it so the
        # rear Z-seam lip's inner face is what it seats against. Those standoffs are the
        # placement, so the tolerances carry them. In Z it stands on the floor slab itself: its
        # bottom lid is a plane and nothing is under it. `y+` and `z-` together are the
        # back-bottom corner; the two `x` rules are the full width the yaw bought.
        #   Its `y+` is NOT stated: the core is no longer the rearmost body. The SeaFlo runs
        # front to back over it and overhangs the cap's own rear edge, so the pump is what the
        # back wall stands off and the pump is where that rule now lives. The core keeps its
        # X fences and its floor.
        "foam-assembly":     [("x-", 15.0), ("x+", 15.0), ("z-", 1.0)],
        # "The compressor is on the floor at the front, upright, centred across the machine."
        # The two x rules carry the same bound, which is what makes them a centring statement
        # rather than two stances. `clear foam-assembly` is the machine corridor — the band
        # its copper turns in on the way to the core's front face, which nothing may close.
        "compressor-shroud": [("y-", 4.0), ("z-", 4.0), ("x-", 17.0), ("x+", 17.0),
                              ("clear", "foam-assembly", 40.0)],
        # "The condenser stands over the compressor, off the cold core's face." `near
        # compressor-shroud` is the stack — a block off its own stratum has no root — held at
        # the one band the front Z seam has (`_contents.STACK_GAP`), and the `clear` rule is
        # the air between the loop's hot end and its cold one.
        "condenser+fan":     [("near", "compressor-shroud", contents.STACK_GAP + 1.0),
                              ("y-", 4.0),
                              ("clear", "foam-assembly", 2.0)],
        # "The display is CENTRED on a facet that runs the full width, let into the
        # top-front corner." The two x rules carry the same bound, which is what makes
        # them a centring statement rather than two stances: neither wall may be nearer
        # than the other by more than the tolerance. y− and z+ are the letting-in — the
        # body's own faces one facet wall inside the front and top walls.
        "display":           [("x-", 48.0), ("x+", 48.0), ("y-", 2.0), ("z+", 2.0)],
        # "The funnel rides the top wall, hard behind the display" — brim top one brim thickness
        # + one wall above the interior ceiling, and its collar's front edge one brim margin
        # behind the facet's own back plane, which `_contents.funnel_centre` places it on and
        # `enclosure._hopper_hole` asserts the frame for.
        "hopper-funnel":     [("z+", 6.1)],
        # --- Zone B, the service bay above the cold core -------------------------
        # The pump lies front to back on the cap, its motor can cantilevering aft. `y+` fences
        # the tail's drift toward the wall — a band, not a hug: the wall stands where the rear
        # panel's own field put it, and the tail room behind the can is what that leaves.
        # `near foam-assembly` is the seat — its base is flat on the lid. `clear` is the strip
        # ahead of it the chain lies in — and the chain's own placement states the trade: it
        # packs aft on its stub's lead but yields that lead to the condenser's port-clear when
        # the strip closes, so what this rule holds is the floor, not a band.
        "seaflo-pump":       [("y+", 15.0), ("near", "foam-assembly", 0.5),
                              ("clear", "discharge-chain", 1.0)],
        # The chain lies along Y on the pump's crown, on the stub of 3/8" braided PVC that is the
        # only thing that leaves the discharge — so `near seaflo-pump` is the roof it stands on.
        "discharge-chain":   [("near", "seaflo-pump", 2.0)],
        # The suction chain lies in the SLOT between the casting and the stand's aft row, on the
        # stub that is the only thing that leaves the suction — nothing under it it can bear on,
        # so what this rule holds is the slot's two walls. Both read closed off the boxes.
        "suction-chain":     [("clear", "nozzle-b-tray-assembly", 1.0), ("clear", "seaflo-pump", 1.0)],
        # The ASSE chain runs down the lane with its inlet under the bulkhead it is fed from
        # (`near bulkhead-water` — the feed that anchors the pose), its vent falling into the
        # basin below it, and its body standing off the −X wall's seam furniture. The bound is
        # loose because the port field is a STRATUM above the water deck here, not beside
        # it: even a station standing on the chain's own column is one climb away, and that
        # climb is the height the deck takes.
        "asse1022-assembly": [("near", "bulkhead-water", 26.0),
                              ("fall", "vent-tip", "drip-pan", 60.0),
                              ("clear", "seaflo-pump", 30.0)],
        # The split hangs off the chain that feeds it — on its plane, a step east of its outlet
        # column — so its rules read that chain and the bodies that bound the loft it hangs in.
        # No seat rule: the deck below is the loft trays' ground and holds no station for this
        # fitting (`fit.py slab`, the component note).
        # Second fitting of the wall sequence: its supply mouth one JUNCTION_LEG_LEAD off the
        # chain's outlet on that outlet's own column, the hopper cone's sheet the ceiling over
        # its forward half.
        "water-split":       [("near", "asse1022-assembly", contents.JUNCTION_LEG_LEAD + 4.0),
                              ("clear", "hopper-funnel", 1.0),
                              ("clear", "flow-regulator", 5.0)],
        # V-K stands on its cradle ACROSS THE LANE from the split that feeds it, lifted off the
        # cap by that cradle, clear of the pump it discharges to. `near water-split` is the strip
        # between the two bodies — the one water-3's branch climb stands in, and the whole reason
        # the valve is not laid across the lane instead.
        # The regulator stands on the loft floor over the aft stand's coils, one hop down the
        # lane from the split that feeds it, so its tie is that fitting and its holds are the
        # bodies that bound the loft.
        # Third fitting of the wall sequence: inline ahead of the split's flavor collet, under
        # the same cone-sheet ceiling.
        "flow-regulator":    [("near", "water-split", contents.JUNCTION_LEG_LEAD + 4.0),
                              ("clear", "hopper-funnel", 1.0)],
        # The pan is centred on the vent column rather than posed, so its rules read the seat
        # and the two bodies that bound its column: the casting its floor stands over, and the
        # chain overhead whose underside it hangs from.
        "drip-pan":          [("clear", "seaflo-pump", 3.0),
                              ("clear", "asse1022-assembly", 3.0)],
        # The electrical block stands in two columns on the machine's east flank. On the WALL:
        # the brick, and the board a storey over it reading that brick's own crown as its floor,
        # so the `near` that matters for the board is the body under it and not the cap it left.
        # The 10 mm between them is the air the supply's loss rises through — the bay has no
        # ventilation — and it is the one gap here that is a requirement rather than a result.
        "psu":               [("near", "foam-assembly", 0.5),
                              ("clear", "seaflo-pump", 1.0)],
        "pcba":              [("near", "psu", 10.0),
                              ("clear", "seaflo-pump", 3.0),
                              ("clear", "c14-inlet", 1.0)],
        # On the DECK, in the band the boards left: the relay lying down on the lid and the hub
        # lying on the relay's back. Each reads the body it stands on, so the column holds
        # together if any one of them moves, and both hold off the casting to their west.
        "relay-1":           [("near", "psu", 1.0),
                              ("clear", "seaflo-pump", 1.0),
                              ("clear", "c14-inlet", 1.0)],
        "ac-hub":            [("near", "relay-1", 1.0),
                              ("clear", "seaflo-pump", 1.0),
                              ("clear", "c14-inlet", 1.0)],
        "ground-stack":      [("near", "ac-hub", 1.0),
                              ("clear", "c14-inlet", 1.0),
                              ("clear", "psu", 1.0)],
        # --- Zone C, the valve manifold in the front column -----------------------
        # "The source pair heads the column, in the front column ahead of the core and off the
        # condenser's intake face."
        #   `clear hopper-funnel` is the basin overhead — this column's ceiling, bounded by
        # `_contents.SOURCE_TRAY_HEADROOM`. The gap is exact solid to exact solid: the basin's
        # floor slopes up toward the front, so the surface standing over these coils is not the
        # spout tip that sets the funnel's bounding box.
        #   `clear foam-assembly` says the tray is in the FRONT COLUMN and not over the cap. It
        # is not the aft band: the tray stands well above the core's crown, so the measured gap
        # runs diagonally to the shell's top-front arris and is much longer than the Y the feeds
        # actually turn in. That band is `_contents.SOURCE_TRAY_AFT_BAND`, and what holds it is
        # fluid-2's own turn west and fluid-4's turn forward, both authored inside it.
        #   `clear condenser+fan` is the block's INTAKE: the air crosses the cabinet from the −X
        # side face into its finstack, so this lane is the one the tray must not stand in.
        "source-tray-assembly": [("clear", "hopper-funnel", contents.SOURCE_TRAY_HEADROOM),
                                 ("clear", "foam-assembly", 30.0),
                                 ("clear", "condenser+fan", 10.0)],
        # "The selects pair is PACKED UP UNDER THE SOURCE PAIR, in that tray's own column."
        #   `near source-tray-assembly` is the pack relation — the one thing this tray is packed
        # against — and its bound is `_contents.TRAY_STACK_GAP`, so the gap that keeps a valve
        # liftable is the gap the rule measures. Plate underside to coil crown, exact solid to
        # exact solid.
        #   `clear foam-assembly` says the tray is in the FRONT COLUMN and not over the cap. This
        # tray straddles the core's crown rather than standing over it, so the gap runs straight
        # down Y to the shell's front face and is the aft band itself — `SOURCE_TRAY_AFT_BAND`,
        # the number the pair above derives its own Y from, which this one inherits.
        #   `clear condenser+fan` is again the block's INTAKE, and the gap the rule measures is
        # what this tray leaves between itself and the finstack the air crosses to.
        "selects-tray-assembly": [("near", "source-tray-assembly", contents.TRAY_STACK_GAP + 0.5),
                                  ("clear", "foam-assembly", contents.SOURCE_TRAY_AFT_BAND - 0.5),
                                  ("clear", "condenser+fan", 10.0)],
        # "The bag-A pair is PACKED UP UNDER THE SELECTS PAIR, on the column's bottom seat."
        #   `near selects-tray-assembly` is the pack relation, bounded by `TRAY_STACK_GAP` like the
        # tray above it, so the same liftable-valve gap is the gap the rule measures.
        #   `clear compressor-shroud` is what the column has left under its bottom plate —
        # `contents.tray_column_floor`. No line crosses in it: every corridor `_lines` uses passes
        # the column rather than threading under it, so what the band is for is reaching the seat,
        # and the bound is the pack's own floor. `tray_column_floor` itself raises when the plate is
        # under the roof.
        #   `clear foam-assembly` is the aft band, the same `SOURCE_TRAY_AFT_BAND` the pair above
        # inherits: this tray straddles nothing, so the gap runs straight down Y to the shell's
        # front face.
        #   `clear condenser+fan` is the block's INTAKE. This is the third body in that lane.
        "bag-a-tray-assembly": [("near", "selects-tray-assembly", contents.TRAY_STACK_GAP + 0.5),
                                ("clear", "compressor-shroud", CLEARANCE_FLOOR),
                                ("clear", "foam-assembly", contents.SOURCE_TRAY_AFT_BAND - 0.5),
                                ("clear", "condenser+fan", 10.0)],
        # "The manifold's junction stands on the two columns its four ports make." Each tee is held
        # to BOTH trays, because its run reaches a collet on each and it sits midway between them:
        # the bound is the standoff `contents.junction_tee_pos` leaves, half the stack pitch less
        # the fitting's own run. A tee nearer one tray than that has slid down its column.
        "tee-y-a":           [("near", "source-tray-assembly", contents.tray_stack_pitch() / 2.0),
                              ("near", "selects-tray-assembly", contents.tray_stack_pitch() / 2.0),
                              ("clear", "condenser+fan", 10.0)],
        "tee-y-b":           [("near", "source-tray-assembly", contents.tray_stack_pitch() / 2.0),
                              ("near", "selects-tray-assembly", contents.tray_stack_pitch() / 2.0),
                              ("clear", "condenser+fan", 10.0)],
        # "Y-E stands ACROSS the strip between the pump row's aft faces and the bag pair's forward
        # collets." Both `near` rules are that strip: the fitting's own body is what fills it, so the
        # bound either side is that body's half-width and the pack's floor, and `contents.y_e_pos`
        # raises the day the strip is narrower than the two together.
        "tee-y-e":           [("near", "bag-a-tray-assembly", contents.TEE_HALF_W + 1.5),
                              ("near", "pump-a", contents.TEE_HALF_W + 1.5),
                              ("clear", "condenser+fan", 10.0)],
        # --- Zone C's second stand: channel A's pump, and the loft over the water deck ----
        # "Channel A's pump stands upright in the front column's west-forward box, in the same
        # lane as channel A's own trays."
        #   `near bag-a-tray-assembly` is that relation, and the bound is the lane it leaves
        # between its barb face and that tray's own — the corridor fluid-11 and fluid-12 run
        # down to Y-C and Y-D. What holds the pose in Z is not a rule but a derivation:
        # `contents._build` stands the barbs ON that tray's port plane.
        #   `clear condenser+fan` is the block's intake lane, which every body in the front column
        # stands in.
        "pump-b":            [("near", "bag-a-tray-assembly", 25.0),
                              ("clear", "condenser+fan", 10.0)],
        # "The pump row's two tees stand abreast in the pump lane, on their own barbs' columns."
        #   `near pump-b` is the relation that places each: the tee stands off the barb its run
        # butts, and the bound is the lane's own length — pump aft face to the aft band the tray
        # leg turns in — halved, because the tee sits midway down it. `clear` on the tray column
        # and on each other is the lane's width, which is what holds the two apart; `clear
        # condenser+fan` is the intake lane every body in the front column stands in.
        "tee-y-c":           [("near", "pump-b", 45.0),
                              ("clear", "bag-a-tray-assembly", 1.0),
                              ("clear", "tee-y-d", 1.0),
                              ("clear", "condenser+fan", 10.0)],
        "tee-y-d":           [("near", "pump-b", 45.0),
                              ("clear", "bag-a-tray-assembly", 1.0),
                              ("clear", "tee-y-c", 1.0),
                              ("clear", "condenser+fan", 10.0)],
        # "The bag-B pair and the nozzle gates stand in the LOFT's west lane, a JUNCTION BAY apart."
        #   Each reads `clear` of the other at `contents.AFT_TRAY_BAY`: the two pairs face each
        # other collet for collet across that bay, and what stands in it is a fitting — Y-G's run,
        # the one straight line the two facing columns already share. A pack gap here is what the
        # four legs owed into the slot could not leave through.
        #   `clear vk-fill-valve` is the loft's own FLOOR under this lane. The deck beneath the
        # loft is not level — V-K's coil is its tallest body — so what a plate up here clears is
        # that coil and not a plane, and the gap the rule measures is the whole of it.
        #   `clear hopper-funnel` is the loft's forward face, the basin's aft skirt, measured
        # against the real surface: the box says the pair is a millimetre off it and the solid
        # says far more, and the pair is placed against the second. `clear pump-a` is the east
        # lane it leaves whole for a body that fills it.
        "bag-b-tray-assembly": [("clear", "nozzle-tray-assembly", contents.AFT_TRAY_BAY - 0.5),
                                ("clear", "hopper-funnel", 5.0),
                                ("clear", "pump-a", 5.0)],
        #   The nozzle pair's own last rule is the lane its two outlet runs turn in: it is the
        # only pair with lines that leave the machine, and what they leave through stands on the
        # rear wall behind it. `clear asse1022-assembly` is the chain under it — the one body on
        # the deck that reaches the loft's floor, and it is held out of it.
        "nozzle-tray-assembly": [("clear", "bag-b-tray-assembly", contents.AFT_TRAY_BAY - 0.5),
                                 ("clear", "asse1022-assembly", 1.0),
                                 ("clear", "bulkhead-flavor-a", 20.0)],
        # "Channel B's two tees stand in the loft — Y-G in the bay its run crosses, Y-F in the
        # lane pump A's own two lines run down."
        #   `near bag-b-tray-assembly` places both of them, and for the same reason: every leg
        # either one has to a body up here is a short one off that pair. Y-G's two run legs are a
        # `TEE_RUN_LEAD` of tube each; Y-F's BRANCH is what reaches back at the same pair's draw,
        # so the bound is the fitting's own body plus the pack's floor. Both of the legs that leave
        # the loft (fluid-21 out of Y-F, fluid-22 into Y-G) reach the front column, and neither is
        # a placement relation — a run that long is measured, not packed against.
        "tee-y-g":           [("near", "vk-tray-assembly", contents.TEE_HALF_W + 1.5),
                              ("clear", "nozzle-tray-assembly", contents.TEE_RUN_LEAD - 0.5),
                              ("clear", "tee-y-f", 1.0)],
        "tee-y-f":           [("near", "bag-b-tray-assembly", contents.TEE_HALF_W + 1.5),
                              ("clear", "nozzle-tray-assembly", 1.0),
                              ("clear", "seaflo-pump", 1.0)],
        # Y-H hangs off its pair like the other three, and the two `clear` rules are what it
        # hangs BETWEEN: the funnel's skirt above it and the shelf's crown one clearance floor
        # below — its legs' geometry stands its belly right on that floor over the PSU. The
        # `near` reads solids, and the nearest span to its pair runs diagonal to the collet
        # stack, wider than the axial reach the pose is derived from.
        # "Channel B's pump stands UPRIGHT in the front column beside channel A's, on the strip
        # between that pump's flank and the condenser's intake face."
        #   `near pump-b` is the whole of the seat: the two are one pose read twice, this one seated
        # off its twin in all three axes, and the bound is `contents.pump_twin_gap()` — what the two
        # flanks are left with once their inner barbs stand a `contents.PUMP_TWIN_PITCH` apart.
        #   `clear condenser+fan` is what the lane has left once both motors are in it. It is under
        # the 10 mm every other body in this column holds off that face: the strip is
        # `TRAY_EAST_LANE`-wide short of taking two 62.61 mm motors at that hold, and this is the
        # rest of it. The block is still a placeholder, so the number is what the geometry leaves
        # rather than what a thermal bound would ask for.
        #   `clear display` is the facet overhead, which roofs this column, and `clear
        # compressor-shroud` the refrigeration stratum's roof under its foot — the pump is the body
        # in this column that reaches lowest, and the band it leaves is the front Z seam's.
        "pump-a":            [("near", "pump-b", contents.pump_twin_gap() + 0.5),
                              ("clear", "condenser+fan", 8.0),
                              ("clear", "display", 5.0),
                              ("clear", "compressor-shroud", contents.FRONT_COLUMN_FLOOR - 0.5),
                              ("clear", "bag-a-tray-assembly", 1.0)],
        # "The CO2 check is made up on the side-wall inlet's stub", so its placement IS that
        # joint: it touches the fitting it threads onto and hangs in the corridor, off the
        # shroud's aft face ahead of it. `near` carries the slop the made-up pair is built to,
        # which is what `_panel_bodies` asserts the two land within.
        "gasher-co2":        [("near", "co2-inlet", contents.CO2_MADE_UP_TOL),
                              ("clear", "compressor-shroud", 4.0)],
        # The regulator continues the same axis one tube hop inboard of the check, between the
        # shroud's aft face and the core's front one, the two faces that make the corridor a
        # corridor. `near` is the bound on that hop, held apart from `CO2_HOP` itself: past it
        # co2-1 stops being one straight length of tube between two adapters and becomes a run.
        "wr1110":            [("near", "gasher-co2", 12.0),
                              ("clear", "compressor-shroud", 3.0),
                              ("clear", "foam-assembly", 15.0),
                              ("clear", "condenser+fan", 5.0)],
        # "The flow meter lies inline on the riser, in the loft's east pocket over the water
        # deck's crown" — the pump carries both bounds, which is what makes the pair a band
        # rather than two stances: `clear` is the room the riser's own fittings need under the
        # body, `near` is the pocket itself, and without it the meter is free to drift up the
        # loft's open air into the display facet. Its WEST edge is pump A's two loft lines,
        # which are runs and not parts — no placement rule can state them, `lines-clear` is
        # what holds that edge, and `fit.py search` is what picked this column clear of them.
        "digiten-flow":      [("clear", "seaflo-pump", 1.0),
                              ("near", "seaflo-pump", 20.0)],
        # --- The panel bodies: the rear port row, and the CO2 inlet on the east wall ---
        # Each stands in a hole its own wall cuts and is held by its own nut or thread, so the
        # placement IS the pierce, and the three axes divide cleanly. The wall's own axis is the
        # reach past the cavity plane — the end the customer pushes a tube onto, which has to stand
        # proud of the panel without fouling what the machine backs up against. The second face rule
        # is the stratum the row runs on. And ALONG the wall the row's pitch is a band, not a floor:
        # `near` is the neighbour that fixes the station, `clear` is the room to get a hand on each
        # nut, and a fitting that had only the floor could slide down the wall unopposed.
        #   The pitch itself is `back_wall_ports()`; these are what it has to buy.
        # The water bulkhead's hand-room reads differently from its row-mates': the ASSE chain
        # hangs on this fitting's own feed, `ASSE_INLET_HOP` of tube away, and its nut is made
        # up before the chain is hung — parts go in — so the standing gap owes the hop's tube,
        # not a hand.
        "bulkhead-water":    [("y+", 13.0), ("z+", 21.0),
                              ("near", "c14-inlet", 9.0),
                              ("clear", "c14-inlet", 5.0),
                              ("clear", "asse1022-assembly", 8.0)],
        "bulkhead-flavor-b": [("y+", 13.0), ("z+", 21.0),
                              ("near", "bulkhead-carb", 9.0),
                              ("clear", "bulkhead-carb", 5.0),
                              ("clear", "c14-inlet", 5.0)],
        "bulkhead-carb":     [("y+", 13.0), ("z+", 21.0),
                              ("near", "bulkhead-flavor-a", 9.0),
                              ("clear", "bulkhead-flavor-a", 5.0),
                              ("clear", "bulkhead-flavor-b", 5.0)],
        "bulkhead-flavor-a": [("y+", 13.0), ("z+", 21.0),
                              ("near", "bulkhead-carb", 9.0),
                              ("clear", "bulkhead-carb", 5.0),
                              ("clear", "nozzle-tray-assembly", 20.0)],
        # The C14 is the one rectangular station in the row, and it reaches further out than the
        # JG fittings because a mains cord's hood is what lands on it.
        "c14-inlet":         [("y+", 15.0), ("z+", 20.0),
                              ("near", "bulkhead-water", 9.0),
                              ("clear", "bulkhead-water", 5.0),
                              ("clear", "nozzle-tray-assembly", 15.0)],
        # The CO2 inlet is the only body on the EAST wall, and the axes divide the same way: `x+` is
        # the collet the customer's red tether lands on, `z-` is how low it stands under everything
        # the corridor floor carries, and the shroud ahead of it carries the band its stub reaches
        # inboard across. The check made up on that stub is placed from the check's own side.
        "co2-inlet":         [("x+", 23.0), ("z-", 46.0),
                              ("near", "compressor-shroud", 15.0),
                              ("clear", "compressor-shroud", 8.0),
                              ("clear", "foam-assembly", 25.0)],
    }


# The rows a build computes. Unset — the default — is all of them.
# `HSM_CARD_ONLY=bend-radius,mounted` computes those two and STANDS THE REST DOWN.
#
# A stood-down row reads "not computed" and never "pass": nothing looked at it, and a gate
# nobody looked at is not a gate that held. `gates_pass` stays false while any gate is stood
# down, so a partial card cannot report BUILD-READY.
#
# Measured, on the pack as it stands: clearance-floor 37 s, lines-clear 29 s, placed 17 s,
# routed 17 s, pack-closes 6 s, and every other row under half a second.
CARD_ONLY = frozenset(
    r.strip() for r in os.environ.get("HSM_CARD_ONLY", "").split(",") if r.strip())


def _computes(cid: str) -> bool:
    return not CARD_ONLY or cid in CARD_ONLY


def _stood_down(cid: str, label: str, kind: str = "gate") -> "Check":
    return Check(cid, label, kind, "skip", "not computed", "—")


_PLACEMENT_RULES = None


def placement_rules() -> dict:
    """The placement rules. The same dict object every call — `scorecard_selftest` puts a
    probe rule in it and takes it out again."""
    global _PLACEMENT_RULES
    if _PLACEMENT_RULES is None:
        _PLACEMENT_RULES = _declare_placement_rules()
    return _PLACEMENT_RULES


def placement_audit(solids: dict, inner: tuple) -> list[tuple[str, bool, list]]:
    """For each component that has placement rules, measure every rule and return
    (name, all_hold, [(label, gap, bound_mm, ok)]) — label is the face for a face-to-datum
    rule, "near <other>" / "clear <other>" for the part-to-part forms. Components without
    rules are not returned — they are simply not-yet-placed."""
    if not _computes("placed"):
        return []
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    datum = {"x-": ix0, "x+": ix1, "y-": iy0, "y+": iy1, "z-": iz0, "z+": iz1}
    out = []
    for name, rules in placement_rules().items():
        if name not in solids:
            continue
        bb = _boxes.boxed(solids[name])
        val = {"x-": bb.xmin, "x+": bb.xmax, "y-": bb.ymin, "y+": bb.ymax, "z-": bb.zmin, "z+": bb.zmax}
        checks = []
        for rule in rules:
            if rule[0] == "near":
                _tag, other, mx = rule
                gap = _solid_gap(solids[name], solids[other]) if other in solids else float("inf")
                checks.append((f"near {other}", gap, mx, gap <= mx))
            elif rule[0] == "clear":
                # A keep-out against an absent neighbor is an authoring error, not a
                # vacuously-held rule — it must flag, same as `near`.
                _tag, other, mn = rule
                present = other in solids
                gap = _solid_gap(solids[name], solids[other]) if present else float("inf")
                checks.append((f"clear {other}", gap, mn, present and gap >= mn))
            elif rule[0] == "fall":
                _tag, port, other, mx = rule
                p = next(q for q in ports() if q.component == name and q.name == port)
                who, drop = _fall_first(p.pos, p.diam, mx, solids, skip=(name,))
                checks.append((f"fall {port} onto {who or 'nothing'}", drop, mx, who == other))
            else:
                f, mx = rule
                g = abs(val[f] - datum[f])
                checks.append((f, g, mx, g <= mx))
        out.append((name, all(c[3] for c in checks), checks))
    return out


def _fall_first(pos, dia, reach, solids: dict, skip=()) -> tuple:
    """What a drip leaving `pos` lands on, and how far it falls to get there: a column of `dia`
    dropped `reach` straight down, and the highest body it meets. `(None, reach)` when the column
    reaches its full length untouched — that is the probe's own length, not a clearance.

    A boolean that will not resolve raises: an unmeasured body is not an absent one, and the
    difference decides what gets wet."""
    import cadquery as cq

    col = cq.Solid.makeCylinder(dia / 2.0, reach, cq.Vector(*pos), cq.Vector(0, 0, -1))
    best, who = reach, None
    for n, s in solids.items():
        if n in skip:
            continue
        if _bbox_gap(_boxes.boxed(col), _boxes.boxed(s)) > 0:
            continue
        try:
            inter = col.intersect(s)
            if inter.Volume() <= CLASH_TOL:
                continue
        except Exception as exc:
            raise RuntimeError(
                f"the fall from {tuple(round(c, 2) for c in pos)} against {n} could not be taken "
                f"({exc}) — what the drip lands on is unknown, not clear") from exc
        drop = pos[2] - inter.BoundingBox().zmax
        if drop < best:
            best, who = max(0.0, drop), n
    return who, best


# ── The port LEAD (a gate) — that a located port can actually be used ────────
# `placement_audit` gates how close two BODIES come and `ports_audit` gates that a port sits on
# its own body's surface. Neither asks the question a connector exists to answer: is there room
# for a line to LEAVE it. A port is a hole with a direction, and a hole with another body parked
# in front of it is a hole nothing can be plugged into — a defect that shows up nowhere else,
# because both bodies may be a clean clearance apart while the collet between them is useless.
#
# So: cast the port's own bore along its own axis, at the port's own Ø, for the straight a run
# off it would take, and require the cast to reach. `probe.cast` is the same query; this is it
# taken against the pack the scorecard already has, once per port, so the gate needs no second
# world.
#
# What the cast may hit is the body the port is JOINED to — a divider's outlet stands
# `divider_reach()` off the valve collet it feeds, and a tee's run collet stands
# `TEE_RUN_LEAD` off its, both by construction — so the mate is held out. The mate is read off
# the AUTHORED RUNS rather than from prose: a run names `component.port` at each end, so the
# body at the far end of every run terminating on this port is what the lead is allowed to end
# on. A port with no run yet is held to the full lead against everything, which is the useful
# direction — that is exactly the state the loft's four collets were in.
# The gate's population is the ports that carry a LINE WITH A BEND RADIUS — every tube, and no
# wire: a loom turns against its own insulation and needs no straight, so casting a cable gland's
# bore is measuring the wrong thing. And it is the ports on REAL geometry: a station PICKED on a
# primitive box (`condenser+fan`) is a claim about the box, not a measurement of the part, so a
# lead taken off it measures the box. Those are still measured and still printed — the gate's
# population follows the `shaped` axis, and a placeholder's ports join it when its geometry does.
PORT_LEAD_KINDS = ("fluid", "refrigerant")
PORT_LEAD_BENDS = 2.0   # × the line's bend radius: the stub a run leaves a fitting on, and the
                        # tangent its first corner is seated on — `_routing.route`'s own two
                        # reaches, and the shortest straight any turn off a port can be built in.


def _lead_first(pos, axis, dia, reach, solids: dict, skip=()) -> tuple:
    """What a line leaving `pos` along `axis` runs into, and how far it gets: a column of `dia`
    swept `reach` along the axis, and the NEAREST body it meets. `(None, reach)` when the column
    reaches its full length untouched — that is the probe's own length, not a clearance.

    A boolean that will not resolve raises, for `_fall_first`'s reason: an unmeasured body is
    not an absent one, and the difference decides whether a fitting can be plugged in."""
    import cadquery as cq

    col = cq.Solid.makeCylinder(dia / 2.0, reach, cq.Vector(*pos), cq.Vector(*axis))
    best, who = reach, None
    for n, s in solids.items():
        if n in skip:
            continue
        if _bbox_gap(_boxes.boxed(col), _boxes.boxed(s)) > 0:
            continue
        try:
            inter = col.intersect(s)
            if inter.Volume() <= CLASH_TOL:
                continue
        except Exception as exc:
            raise RuntimeError(
                f"the lead out of {tuple(round(c, 2) for c in pos)} against {n} could not be "
                f"taken ({exc}) — whether the port can be used is unknown, not clear") from exc
        b = inter.BoundingBox()
        # How far along the axis the nearest point of the intersection lies.
        corners = [(b.xmin, b.xmax), (b.ymin, b.ymax), (b.zmin, b.zmax)]
        got = min(sum((c[i] - pos[i]) * axis[i] for i in range(3))
                  for c in ((corners[0][a], corners[1][bb], corners[2][cc])
                            for a in (0, 1) for bb in (0, 1) for cc in (0, 1)))
        if got < best:
            best, who = max(0.0, got), n
    return who, best


def port_mates(runs) -> dict:
    """`(component, port)` → the set of component names the port's own CONNECTIONS join it to.
    Mostly read off the runs' anchors, so a line re-authored elsewhere moves what its port is
    allowed to open onto; plus the `MADE_UP` threads, which are the same relation with no run
    in it — each end opens onto the body it is screwed into, and a joint tightened home has
    no line to report."""
    out: dict = {}
    for r in runs:
        (fc, _, fp), (tc, _, tp) = r.frm.partition("."), r.to.partition(".")
        out.setdefault((fc, fp), set()).add(tc)
        out.setdefault((tc, tp), set()).add(fc)
    for (ac, ap), (bc, bp) in MADE_UP:
        out.setdefault((ac, ap), set()).add(bc)
        out.setdefault((bc, bp), set()).add(ac)
    return out


def port_leads(solids: dict, mates: dict | None = None) -> list[tuple[str, str, str | None, float, float, bool, bool]]:
    """Every tube port's clear lead: `(component, port, what it meets, how far, what it needs,
    ok, gated)`. A port needs `PORT_LEAD_BENDS` bend radii of its own bore along its own axis,
    clear of every body but the one its own runs join it to.

    The reach is the LINE's radius, not the port's: soft LLDPE turns at `_lines.WBEND` and
    1/4" ACR copper at `_routing.BEND_RATIO` × its OD, so a flavor collet asks 8 mm of straight
    where a refrigerant stub asks 25.4."""
    import _lines
    import _routing as R

    real = {c.name for c in COMPONENTS if c.is_real}
    if mates is None:
        mates = port_mates(_lines.build_runs())
    out = []
    for p in ports():
        if p.kind not in PORT_LEAD_KINDS or p.pos is None or not p.face or p.diam is None:
            continue
        if p.component not in solids:
            continue
        bend = _lines.WBEND if p.kind == "fluid" else R.BEND_RATIO * p.diam
        need = PORT_LEAD_BENDS * bend
        skip = {p.component} | mates.get((p.component, p.name), set())
        who, free = _lead_first(p.pos, R.normal_of(p.face), p.diam, need, solids, skip=skip)
        out.append((p.component, p.name, who, free, need, who is None, p.component in real))
    return out


# ── Ports (the located axis) — where every connector sits on the component, and how big ──
# A connection has no path until BOTH its ends have a position AND a bore on a real body. This
# is the located axis: each component's tube/wire connectors, declared with a world position,
# the body face it exits, and a nominal bore Ø, then checked to actually sit on the placed
# solid's surface. Positions are DERIVED where the part documents its penetrations (foam-shell
# README §Penetrations; compressor_shroud.py hole centers carried through _contents'
# rotate+placement) and PICKED off the model where it doesn't; Ø comes from the line/fitting the
# port carries (1/4" ACR copper = 6.35, 3/8" hose barb = 9.525, a cable gland, …). `pos=None`
# marks a connector whose position is still unknown, `diam=None` one still unsized — each a
# visible "needs a value", never a silent gap. A component is `located` when it has ports AND
# every one is positioned, on-surface, AND sized — the specificity the PCBA had per pad, so both
# our routing and the audit can read every coordinate and bore.
@dataclass
class Port:
    name: str            # connector id, unique within its component
    component: str       # the COMPONENTS name it sits on
    kind: str            # "fluid" | "refrigerant" | "electrical"
    pos: tuple | None    # (x, y, z) world coords, or None = not yet located
    face: str            # body face it exits: x-/x+/y-/y+/z-/z+ ("" when pos is None)
    diam: float | None   # nominal bore Ø in mm — the flow/conductor opening at the port: a
                         # tube/fitting nominal (1/4"=6.35, 3/8"=9.525), a copper OD, or a
                         # cable-gland passage. None = not yet sized. This is the mating and
                         # routing dimension — a coordinate says WHERE a line lands, the Ø says
                         # WHAT fits there; the PCBA pad-size analog. A port is fully specified
                         # (and its component `located`) only with both a position AND a Ø.
    mates: str           # the other end, human-readable
    note: str = ""


def _p(name, component, kind, pos, face, diam, mates, note=""):
    return Port(name, component, kind, pos, face, diam, mates, note)


# Front foam ports. `foam_shell_port` takes a STATION NAME — a front-port-field
# station for the six round bores, a copper plug for the four the slot carries — and
# carries it into world through the yaw, so these follow both the shell's own port
# layout and the pose the pack gives it instead of being retyped after either. It
# hands back the FACE with the position — the yaw puts the shell's local −X on world
# −Y, facing the user — which is what each row spreads.
_FOAM_PORT = contents.foam_shell_port


# The CO2 chain's mouths, each off the module that draws the body it is on and carried into
# world by the seat the pack gave that body — the two the pack holds, and the DERPIPE's two,
# which `panel_bodies()` seats through the wall. A body that moves takes its mouths with it.
_CO2_CHAIN = contents.co2_chain_port
_CO2_INLET = contents.co2_inlet_port

# The rear-panel bodies' own reaches, off the wall face `panel_bodies()` seats them on: the
# stated rear plane the box is built to, plus the wall.
_PANEL_OUT = contents.REAR_PLANE_Y + contents.WALL
# JG bulkhead union: tube-face reach outboard / inboard of the panel, off the fitting's
# own two ports — so a run drawn to a station butts the collet face that is there.
_JG_OUT, _JG_IN = _jg.port(+1)[0][1], -_jg.port(-1)[0][1]
# C14 inlet: the spade TIPS' plane inboard of the panel. The flange bears on the INNER
# face, so the wall's own thickness stands in front of the fitting's three figures.
_C14_IN = contents.WALL + _c14.FLANGE_T + _c14.BODY_DEPTH + _c14.TAB_PROUD
def _declare_ports():
    """The declared connector set, built on first use — `ports()`, and `scorecard.PORTS`.

    Every station here reads off the pack: `contents.foam_shell_port`, `pump_port`,
    `back_port_station` and their kin resolve against placed solids, so the first one
    evaluated builds the whole pack. Built at import that cost lands on anything that
    imports this module for any reason — a probe, `need.py`, a one-line query — so it is
    taken when a port is first asked for instead.
    """
    _BACK_A     = contents.back_port_station("bulkhead-flavor-a")
    _BACK_B     = contents.back_port_station("bulkhead-flavor-b")
    _BACK_CARB  = contents.back_port_station("bulkhead-carb")
    _BACK_WATER = contents.back_port_station("bulkhead-water")
    _BACK_C14   = contents.back_port_station("c14-inlet")

    declared = [
        # foam-assembly — 8 tube penetrations (foam-shell README §Penetrations) + 2 reed-cable exits.
        # NINE on the shell's −X face, which the yaw puts at the machine's front: six take their own
        # round bore on the front port field, three share the slot above it, and every one of them
        # reaches that face along the port lane rather than head-on — so a station's Z is where its
        # line crosses the wall, not where its fitting sits. The tenth leaves by the TOP CAP, whose
        # outer face is the service bay's floor. Ø: the beverage/flavor lines run the
        # foam shell's Ø6.5 port-holes (_cold_core_interface.port_hole_radius 3.25) sized for 1/4"
        # tube; the water-in takes the SeaFlo's 3/8" discharge on the warm side; the copper legs are
        # 1/4" ACR = 6.35. Every mate named here is a body the thin pack has not placed yet, so each
        # of these is a located end waiting on its other one; that is what `routed` is counting.
        _p("carb-water-out", "foam-assembly", "fluid",       *_FOAM_PORT("carb-water-out"), 6.35,  "the carb-water riser, to the faucet umbilical", "1/4\" tank NPT elbow line"),
        _p("reservoir-A",    "foam-assembly", "fluid",       *_FOAM_PORT("reservoir-a"), 6.35,  "reservoir A ↔ peristaltic pump A (bag circuit)", "1/4\" LLDPE flavor line, Ø6.5 foam port"),
        _p("reservoir-B",    "foam-assembly", "fluid",       *_FOAM_PORT("reservoir-b"), 6.35,  "reservoir B DRAW → V-H, the bag-B pair's inlet", "1/4\" LLDPE off the bulkhead at the bottom of the wet V, up the +Y band potted, out this conduit"),
        _p("reservoir-b-fill", "foam-assembly", "fluid",     *_FOAM_PORT("reservoir-b-fill"), 6.35,  "V-I outlet → reservoir B FILL, the bore in its own cap", "1/4\" LLDPE down this conduit onto the reservoir cap's fill bore, above the liquid"),
        _p("co2-in",         "foam-assembly", "fluid",       *_FOAM_PORT("co2-in"), 6.35,  "the CO2 chain (front-panel inlet → check → regulator)", "1/4\" LLDPE; the Ø6.5 bore runs on through the support ring to the adapter under the plate"),
        _p("evap-inlet",     "foam-assembly", "refrigerant", *_FOAM_PORT("lower"), 6.35,  "condenser+fan outlet (liquid line via drier + cap tube)", "1/4\" ACR copper"),
        _p("evap-outlet",    "foam-assembly", "refrigerant", *_FOAM_PORT("middle"), 6.35,  "compressor-shroud suction", "1/4\" ACR copper"),
        _p("water-in",       "foam-assembly", "fluid",       *_FOAM_PORT("water-in"), 6.35,  "the tap-water path's pump discharge (carbonator water inlet)", "1/4\" LLDPE up the TOP CAP's conduit at the cap's west end; the tube leaves the PP010822E on the top-plate Port 2 elbow laterally, runs the band under the cap floor, and climbs this bore to the deck. The SeaFlo's 3/8\" discharge steps down at the warm-side check valve, so the bore sees 1/4\""),
        _p("prv-vent",       "foam-assembly", "fluid",       *_FOAM_PORT("top"), 6.35,  "appliance interior (relief-event discharge only)", "1/4\" relief discharge"),
        _p("reed-cable-A",   "foam-assembly", "electrical",  *_FOAM_PORT("reed-cable-a"), 6.5,   "J6 REEDS A — reservoir A level reeds (SIG-10)", "reed cable through the Ø6.5 shell bore, outboard of reservoir-A's (_reed_channels.py)"),
        _p("reed-cable-B",   "foam-assembly", "electrical",  *_FOAM_PORT("reed-cable-b"), 6.5,   "J7 REEDS B — reservoir B level reeds (SIG-11)", "reed cable through the Ø6.5 shell bore, outboard of reservoir-B's (_reed_channels.py)"),
        # Hopper funnel — the removable silicone basin's single drain: the spout-tube exit annulus,
        # feeding the manifold's shared source by tube (segment 4). Defined in the funnel's own frame
        # (hopper_funnel.drain_local = (neck_dx, 0, −drop)) carried through the placement's FUNNEL_ROT
        # + `funnel_centre()` (brim on the box top), so it rides the part. The spout sits on the collar
        # centre and the shallow full-width floor keeps it high — the whole column beneath it is open,
        # which is what segment 4 needs, since it may only ever fall.
        _p("drain", "hopper-funnel", "fluid", contents.funnel_drain(), "z-", 6.35, "V-B-I by tube — segment 4 (hopper gate → shared source; must fall)", "funnel drain; spout exit annulus (`spout_id` 6.35 bore), bottom face of the spout tube"),
        # compressor-shroud — the shroud's own four penetrations, carried through `_contents`'
        # turn and seat (`shroud_port`) rather than retyped after them. Both copper stubs share
        # the +Y face that looks across the machine corridor at the core; suction and discharge
        # are assigned by world x per the physical loop — discharge inboard, under the condenser
        # it feeds, suction outboard at the core's own port lane. Copper is 1/4" ACR; the AC
        # gland Ø and the earth-stud Ø are estimates pending the shroud teardown.
        _p("ac-mains",        "compressor-shroud", "electrical",  contents.shroud_port("ac-mains"),  "x+", 22.2, "Teyleten relay #1 / AC distribution (AC-4 switched-H + AC-5 N, 3-wire gland)", "the shroud's own 7/8\" panel hole (compressor_shroud.ac_hole_diameter_mm), clamping the SS 1/2\" NPT cable gland"),
        _p("earth-bond",      "compressor-shroud", "electrical",  contents.shroud_port("earth-bond"), "x+", 5.0,  "electronics-shelf ground bus (AC-6)", "M5 earth stud/ring (estimate — confirm at shroud teardown)"),
        _p("refrig-suction",  "compressor-shroud", "refrigerant", contents.shroud_port("refrig-suction"),   "y+", 6.35, "foam-assembly evaporator outlet", "1/4\" ACR copper"),
        _p("refrig-discharge","compressor-shroud", "refrigerant", contents.shroud_port("refrig-discharge"), "y+", 6.35, "condenser+fan inlet", "1/4\" ACR copper"),
        # condenser+fan — a harvested donor block packed as a primitive, so these are PICKS on
        # its placed box, not measurements of the part: both refrigerant ports on the narrow +Y
        # face it presents to the machine corridor (drier + cap tube hang off the outlet), the
        # fan pigtail on the +X face its air leaves by. They move when the block does.
        _p("refrig-inlet",  "condenser+fan", "refrigerant", contents.condenser_port("refrig-inlet"),  "z+", 6.35, "compressor-shroud discharge", "1/4\" ACR copper, entering the block's crown where refrig-1's climb turns in over it"),
        _p("refrig-outlet", "condenser+fan", "refrigerant", contents.condenser_port("refrig-outlet"), "x-", 6.35, "filter-drier → cap tube → foam-assembly evaporator inlet", "1/4\" ACR copper, leaving low on the intake face at the tray-east lane refrig-2 falls down"),
        _p("fan-power",     "condenser+fan", "electrical",  contents.condenser_port("fan-power"),     "x+", 4.0,  "J2 MANIFOLD B FAN + COM (DC-8, 12 V)", "DC pigtail 2-wire (estimate); on the exhaust face, fan centred"),
        # Display — the one harness off the back of the Waveshare board, into the facet's cavity.
        _p("harness", "display", "electrical", contents.display_harness(), "y+", 8.0, "5 V power + display data (PCBA / power bus)", "connector not modeled in STEP; PROVISIONAL on the interior back face — refine with a pick"),
        # Rear-panel bodies. Each station is a reach off `_PANEL_OUT`, the face `panel_bodies()`
        # seats them on, so a body's two ends move with the wall the pack sized.
        _p("tube-out", "bulkhead-flavor-a", "fluid", (_BACK_A[0], _PANEL_OUT + _JG_OUT, _BACK_A[1]), "y+", 6.35, "customer flavor A line (rear umbilical)", "JG 1/4\" PTC, outward"),
        _p("tube-in",  "bulkhead-flavor-a", "fluid", (_BACK_A[0], _PANEL_OUT - _JG_IN, _BACK_A[1]), "y-", 6.35, "flavor A internal line (bag/pump circuit A)", "JG 1/4\" PTC, inward"),
        _p("tube-out", "bulkhead-flavor-b", "fluid", (_BACK_B[0], _PANEL_OUT + _JG_OUT, _BACK_B[1]), "y+", 6.35, "customer flavor B line (rear umbilical)", "JG 1/4\" PTC, outward"),
        _p("tube-in",  "bulkhead-flavor-b", "fluid", (_BACK_B[0], _PANEL_OUT - _JG_IN, _BACK_B[1]), "y-", 6.35, "flavor B internal line (bag/pump circuit B)", "JG 1/4\" PTC, inward"),
        _p("tube-out", "bulkhead-carb", "fluid", (_BACK_CARB[0], _PANEL_OUT + _JG_OUT, _BACK_CARB[1]), "y+", 6.35, "carbonated-water line (rear umbilical / faucet)", "JG 1/4\" PTC, outward"),
        _p("tube-in",  "bulkhead-carb", "fluid", (_BACK_CARB[0], _PANEL_OUT - _JG_IN, _BACK_CARB[1]), "y-", 6.35, "the carb-water riser off the cold core's front face — segment carb-2", "JG 1/4\" PTC, inward"),
        _p("tube-out", "bulkhead-water", "fluid", (_BACK_WATER[0], _PANEL_OUT + _JG_OUT, _BACK_WATER[1]), "y+", 6.35, "house tap-water line (rear umbilical)", "JG 1/4\" PTC, outward"),
        _p("tube-in",  "bulkhead-water", "fluid", (_BACK_WATER[0], _PANEL_OUT - _JG_IN, _BACK_WATER[1]), "y-", 6.35, "asse1022-assembly tube-in (the backflow preventer's own chain) — segment water-1", "JG 1/4\" PTC, inward; the chain's inlet stands directly under this station, so the pigtail turns one corner"),
        _p("mains-in", "c14-inlet", "electrical", (_BACK_C14[0], _PANEL_OUT - _C14_IN, _BACK_C14[1] + 0.5), "y-", 8.0, "AC distribution — L/N/E to the electronics shelf", "C14 spade terminals; 3-wire mains harness inboard"),
        # The CO2 chain, wall-hung on one axis into the machine corridor: the DERPIPE's two
        # ends bracket the east wall, the check's bracket its made-up thread, and the
        # regulator's bracket the hop.
        _p("tube-in",  "co2-inlet", "fluid", *_CO2_INLET("collet"),   7.94, "customer CO2 supply — 5/16\" push-to-connect (the cylinder's short red tether)", "5/16\" PTC collet, outboard"),
        _p("npt-out",  "co2-inlet", "fluid", *_CO2_INLET("stub-tip"), 6.35, "gasher-co2 inlet — the check threads onto this stub", "1/4\" NPT shank, inboard"),
        _p("inlet",    "gasher-co2", "fluid", *_CO2_CHAIN("gasher-co2", "inlet"),  6.35, "co2-inlet npt-out (made up, no line between)", "1/4\" NPT female socket"),
        _p("outlet",   "gasher-co2", "fluid", *_CO2_CHAIN("gasher-co2", "outlet"), 6.35, "wr1110 inlet — segment co2-1", "1/4\" NPT male stub, into a PP450822E onto 1/4\" tube"),
        _p("inlet",    "wr1110", "fluid", *_CO2_CHAIN("wr1110", "inlet"),  6.35, "gasher-co2 outlet — segment co2-1", "1/4\" NPT female socket, PP010822E onto 1/4\" tube"),
        _p("outlet",   "wr1110", "fluid", *_CO2_CHAIN("wr1110", "outlet"), 6.35, "foam-assembly co2-in — segment co2-2", "1/4\" NPT female socket, PP010822E onto 1/4\" tube"),
        # The ASSE 1022 chain — the tap-water path's one non-negotiable component, with the
        # fittings that reach it from 1/4" tube on one side and 3/8" hose on the other.
        _p("tube-in",  "asse1022-assembly", "fluid", *contents.bfp_terminal("tube-in"),  6.35, "bulkhead-water tube-in — segment water-1", "JG PP010822E 1/4\" PTC, facing aft (+Y) up at the bulkhead it is fed from"),
        _p("tube-out", "asse1022-assembly", "fluid", *contents.bfp_terminal("tube-out"), 6.35, "water-split supply — segment water-2", "flare38-14ptc 1/4\" PTC, facing forward (−Y) down the lane to the split"),
        _p("vent-tip", "asse1022-assembly", "fluid", *contents.bfp_terminal("vent-tip"), 6.35, "atmosphere, dripping onto the drip pan + moisture plate (deferred) — never plumbed", "Sealproof 1/4\" ID clear-PVC stub, facing −Z over the basin; cut to length at the bench"),
        # V-K, the fill/shutoff solenoid.
        _p("V-K-I", "vk-tray-assembly", "fluid", *contents.vk_terminal("inlet"),  6.35, "water-split to-vk — segment water-3", "Beduan 1/4\" QC collet, facing forward (−Y) at the fall out of the fittings loft"),
        _p("V-K-O", "vk-tray-assembly", "fluid", *contents.vk_terminal("outlet"), 6.35, "seaflo-pump suction — segment water-4", "Beduan 1/4\" QC collet, facing aft (+Y), its leg turning east into the strip west of the pump"),
        # The split — one run carried straight through, one branch turned.
        _p("supply",    "water-split", "fluid", *contents.split_terminal("supply"),    6.35, "asse1022-assembly tube-out — segment water-2", "PP0208E 1/4\" PTC run"),
        _p("to-vk",     "water-split", "fluid", *contents.split_terminal("to-vk"),     6.35, "vk-tray-assembly V-K-I — segment water-3", "PP0208E 1/4\" PTC branch"),
        _p("to-flavor", "water-split", "fluid", *contents.split_terminal("to-flavor"), 6.35, "flow-regulator inlet — fluid segment 1", "PP0208E 1/4\" PTC run"),
        # The flavor tap's regulator.
        _p("inlet",  "flow-regulator", "fluid", *contents.flowreg_terminal("inlet"),  6.35, "water-split to-flavor — fluid segment 1", "neoFit 1/4\" PTC collet"),
        _p("outlet", "flow-regulator", "fluid", *contents.flowreg_terminal("outlet"), 6.35, "the valve manifold's shared source — fluid segment 2", "neoFit 1/4\" PTC collet"),
        # The pump and the chain that leaves its discharge.
        _p("suction",  "seaflo-pump", "fluid", *contents.seaflo_terminal("suction"),   15.1, "suction-chain barb-tip — segment water-7", "3/8\" hose barb molded into the head, facing east (+X) at the stand's aft row; a braided-PVC stub clamps over it and carries the 3/8\" to the suction chain, where it ends"),
        _p("discharge", "seaflo-pump", "fluid", *contents.seaflo_terminal("discharge"), 15.1, "discharge-chain barb-tip — segment water-6", "3/8\" hose barb molded into the head, facing west (−X) at the wall; a braided-PVC stub comes about in the pocket and climbs the pump's west flank onto the chain"),
        _p("barb-tip",  "discharge-chain", "fluid", *contents.disch_terminal("barb-tip"),  15.1, "seaflo-pump discharge — segment water-6", "MAACFLOW 3/8\" hose barb, facing aft (+Y) at the stub off the pump, level with it; worm-gear clamp"),
        _p("tube-port", "discharge-chain", "fluid", *contents.disch_terminal("tube-port"), 6.35, "foam-assembly water-in — segment water-5", "PP450822E 1/4\" PTC collet, facing forward (−Y) off the far end of the laid-down chain, over the cap's front edge — above the port it feeds, so water-5 only ever descends"),
        _p("tube-port", "suction-chain", "fluid", *contents.suct_terminal("tube-port"), 6.35, "vk-tray-assembly V-K-O — segment water-4", "PP450822E 1/4\" PTC collet, facing FORWARD off the near end of the laid-down chain at V-K's outlet — the two mouths face along one axis, so water-4 is an offset into the slot and not a turn"),
        _p("barb-tip",  "suction-chain", "fluid", *contents.suct_terminal("barb-tip"),  15.1, "seaflo-pump suction — segment water-7", "MAACFLOW 3/8\" hose barb, facing AFT off the far end of the laid-down chain — fed from behind, so the stub runs past it under the chain and loops up in the room the rear plane leaves; worm-gear clamp"),
        # The carb riser's flow meter, inline in the loft with the flow running aft.
        _p("inlet",   "digiten-flow", "fluid", *contents.digiten_terminal("inlet"),  6.35, "foam-assembly carb-water-out — segment carb-1", "1/4\" PTC collet, facing forward (−Y) at the riser's climb out of the front column"),
        _p("outlet",  "digiten-flow", "fluid", *contents.digiten_terminal("outlet"), 6.35, "bulkhead-carb tube-in — segment carb-2", "1/4\" PTC collet, facing aft (+Y) at the climb to the rear port row"),
        _p("pigtail", "digiten-flow", "electrical", *contents.digiten_terminal("wire-exit"), 8.0, "J4 SENSORS — DIGITEN flow pulse (SIG-4)", "3-wire pigtail on a JST-XH 3-pin, leaving the rim boss upward"),
        # The AC hub's three lever nuts — the mains distribution.
        _p("H", "ac-hub", "electrical", *contents.ac_hub_lug("H"), 8.0, "C14 hot in (AC-1 H); out to PSU primary (AC-2 H) and relay #1 COM (AC-3)", "16 AWG, ferruled under the lever"),
        _p("N", "ac-hub", "electrical", *contents.ac_hub_lug("N"), 8.0, "C14 neutral in (AC-1 N); out to PSU primary (AC-2 N); third port open for the shroud lead (AC-5)", "16 AWG, ferruled under the lever"),
        _p("G", "ac-hub", "electrical", *contents.ac_hub_lug("G"), 8.0, "C14 earth in (AC-1 G); out to PSU chassis (AC-2 G) and the ground stack", "16 AWG, ferruled under the lever"),
        # Relay #1 and the ground bus.
        _p("contacts", "relay-1", "electrical", *contents.relay_terminal("contacts"), 8.0, "COM from the H lever nut (AC-3); NO to the compressor shroud's switched hot (AC-4)", "16 AWG, crimp forks under captive screws"),
        _p("logic",    "relay-1", "electrical", *contents.relay_terminal("logic"),    6.0, "board J5 RELAYS loom — VCC/GND/IN (LV-1/2/3)", "22 AWG under captive screws"),
        _p("stud", "ground-stack", "electrical", *contents.ground_stud(), 10.0, "chassis ground — C14 earth off the G lever nut, PSU chassis, pressure vessel, compressor body, and the shroud bond (AC-6)", "16 AWG green, ring terminals stacked under one M3 x 10"),
        # The supply's two terminal blocks.
        _p("ac-in",  "psu", "electrical", *contents.psu_terminal("ac-in"),  10.0, "C14 mains inlet via the AC distribution — H+N+G (AC-1/AC-2)", "16 AWG mains, ferruled under captive screws"),
        _p("dc-out", "psu", "electrical", *contents.psu_terminal("dc-out"), 8.0,  "dc-dist 12 V block (DC-1)", "16 AWG, ferruled under captive screws"),
        # The board's twelve top-entry wafers and its two edge connectors, each read in the
        # board's OWN pcb frame and carried to world by the pose its four holes take.
        _p("J1-manifold-a", "pcba", "electrical", contents.pcba_port(11.0, 16.48),   "z+", 10.0, "8 manifold-A solenoids (DC-6)", "9-cond JST XH"),
        _p("J2-manifold-b", "pcba", "electrical", contents.pcba_port(11.0, -5.77),   "z+", 8.0,  "4 manifold-B solenoids + condenser fan (DC-7/DC-8)", "6-cond JST XH"),
        _p("J3-faucet",     "pcba", "electrical", contents.pcba_port(-52.25, -30.3), "z+", 6.0,  "faucet display UART up the umbilical (SIG-6)", "4-cond JST XH"),
        _p("J4-sensors",    "pcba", "electrical", contents.pcba_port(-35.0, -30.3),  "z+", 8.0,  "temp bus + DIGITEN flow + moisture (SIG-1/4/9)", "7-cond JST XH"),
        _p("J5-relays",     "pcba", "electrical", contents.pcba_port(-41.95, 31.0),  "z+", 6.0,  "both Teyleten relay modules (LV-1/2/3)", "4-cond JST XH"),
        _p("J6-reeds-a",    "pcba", "electrical", contents.pcba_port(-27.1, 31.0),   "z+", 7.0,  "foam-assembly reed-cable-A — reservoir A reeds (SIG-10)", "5-cond JST XH"),
        _p("J7-reeds-b",    "pcba", "electrical", contents.pcba_port(-0.5, -30.3),   "z+", 8.0,  "foam-assembly reed-cable-B — reservoir B + carbonator reeds (SIG-2/3/11)", "7-cond JST XH"),
        _p("J8-i2c",        "pcba", "electrical", contents.pcba_port(1.3, 31.0),     "z+", 6.0,  "off-board MPR121 cap-sense (SIG-8)", "4-cond JST XH"),
        _p("J9-display",    "pcba", "electrical", contents.pcba_port(-17.75, -30.3), "z+", 6.0,  "display harness — 4.3B RS485 + 12 V (SIG-7)", "4-cond JST XH"),
        _p("J10-12v",       "pcba", "electrical", contents.pcba_port(12.35, -21.5),  "z+", 5.0,  "dc-dist 12 V block — board power inlet (DC-4)", "2-pole 5.0 mm screw block"),
        _p("J11-gas",       "pcba", "electrical", contents.pcba_port(-62.0, -23.85), "z+", 6.0,  "mq6-sensor header — MQ-6 gas/leak sensor (SIG-12)", "4-cond JST XH"),
        _p("J13-pumps",     "pcba", "electrical", contents.pcba_port(-12.25, 31.0),  "z+", 6.0,  "Kamoer pump A + B motors (DC-5)", "4-cond JST XH"),
        _p("J14-usb",       "pcba", "electrical", contents.pcba_port(-62.0, 16.5),   "z+", 9.0,  "USB-C programming port (bench only, no loom)", "USB-C receptacle"),
        # The source pair's four bare collets. The tray module owns every one of them
        # (`two_valve_tray.port_collets`) and `source_tray_port` only carries them, so a seat
        # pitch or a port length changed on the part moves the world station with it. Both
        # inlets face AFT, at the two feeds that come from the back of the machine; both
        # outlets face FORWARD, each at the head of its own junction column.
        _p("V-A-I", "source-tray-assembly", "fluid", *contents.source_tray_port("V-A-I"), 6.35, "flow-regulator outlet — fluid segment 2", "Beduan 1/4\" QC collet, facing aft (+Y) up the bay at the regulator that feeds it"),
        _p("V-A-O", "source-tray-assembly", "fluid", *contents.source_tray_port("V-A-O"), 6.35, "tee-y-a Y-A-1 — fluid segment 3", "Beduan 1/4\" QC collet, facing forward (−Y) at the head of the west column"),
        _p("V-B-I", "source-tray-assembly", "fluid", *contents.source_tray_port("V-B-I"), 6.35, "hopper-funnel drain — fluid segment 4 (must only ever fall)", "Beduan 1/4\" QC collet, facing aft (+Y) under the spout's own column"),
        _p("V-B-O", "source-tray-assembly", "fluid", *contents.source_tray_port("V-B-O"), 6.35, "tee-y-b Y-B-1 — fluid segment 5", "Beduan 1/4\" QC collet, facing forward (−Y) at the head of the east column"),
        # Y-A's three, numbered from the SOURCE end down: the run's two collets stand a stack
        # pitch apart on the west column with the fitting midway between them, and the branch
        # reaches east at Y-B's across the crossbar.
        _p("Y-A-1", "tee-y-a", "fluid", *contents.y_a_port("Y-A-1"), 6.35, "source-tray-assembly V-A-O — fluid segment 3", "PP0208E 1/4\" PTC run collet, facing UP (+Z) the column at V-A"),
        _p("Y-A-2", "tee-y-a", "fluid", *contents.y_a_port("Y-A-2"), 6.35, "selects-tray-assembly V-C-I — fluid segment 7", "PP0208E 1/4\" PTC run collet, facing DOWN (−Z) the column at V-C"),
        _p("Y-A-3", "tee-y-a", "fluid", *contents.y_a_port("Y-A-3"), 6.35, "tee-y-b Y-B-3 — fluid segment 6", "PP0208E 1/4\" PTC branch, facing EAST (+X) at Y-B's own across the crossbar"),
        # The selects pair's four. Same tray, same module, the clocking turned round: both
        # INLETS face FORWARD at the foot of their own junction column, both OUTLETS AFT at the
        # pump row still to be placed.
        _p("V-C-I", "selects-tray-assembly", "fluid", *contents.selects_tray_port("V-C-I"), 6.35, "tee-y-a Y-A-2 — fluid segment 7", "Beduan 1/4\" QC collet, facing forward (−Y) at the foot of the west column"),
        _p("V-C-O", "selects-tray-assembly", "fluid", *contents.selects_tray_port("V-C-O"), 6.35, "tee-y-c Y-C-1 — fluid segment 9", "Beduan 1/4\" QC collet, facing aft (+Y) at the pump row"),
        _p("V-D-I", "selects-tray-assembly", "fluid", *contents.selects_tray_port("V-D-I"), 6.35, "tee-y-b Y-B-2 — fluid segment 8", "Beduan 1/4\" QC collet, facing forward (−Y) at the foot of the east column"),
        _p("V-D-O", "selects-tray-assembly", "fluid", *contents.selects_tray_port("V-D-O"), 6.35, "tee-y-f Y-F-1 — fluid segment 19", "Beduan 1/4\" QC collet, facing aft (+Y) at the pump row"),
        # Y-B's three, the same fitting read the same way one seat pitch east: run up the east
        # column, branch back west at Y-A's.
        _p("Y-B-1", "tee-y-b", "fluid", *contents.y_b_port("Y-B-1"), 6.35, "source-tray-assembly V-B-O — fluid segment 5", "PP0208E 1/4\" PTC run collet, facing UP (+Z) the column at V-B"),
        _p("Y-B-2", "tee-y-b", "fluid", *contents.y_b_port("Y-B-2"), 6.35, "selects-tray-assembly V-D-I — fluid segment 8", "PP0208E 1/4\" PTC run collet, facing DOWN (−Z) the column at V-D"),
        _p("Y-B-3", "tee-y-b", "fluid", *contents.y_b_port("Y-B-3"), 6.35, "tee-y-a Y-A-3 — fluid segment 6", "PP0208E 1/4\" PTC branch, facing WEST (−X) at Y-A's own across the crossbar"),
        # The bag-A pair's four — the first pair whose two valves face OPPOSITE ways, because the
        # circuit puts the bag on V-E's inlet and V-F's outlet. Those two go FORWARD to Y-E; the
        # other two go AFT to the pump row, which is where the rest of channel A is.
        _p("V-E-I", "bag-a-tray-assembly", "fluid", *contents.bag_a_tray_port("V-E-I"), 6.35, "tee-y-e Y-E-3 — fluid segment 16", "Beduan 1/4\" QC collet, facing forward (−Y) at the junction the bag draws through"),
        _p("V-E-O", "bag-a-tray-assembly", "fluid", *contents.bag_a_tray_port("V-E-O"), 6.35, "tee-y-c Y-C-2 — fluid segment 10", "Beduan 1/4\" QC collet, facing aft (+Y) at the pump row"),
        _p("V-F-I", "bag-a-tray-assembly", "fluid", *contents.bag_a_tray_port("V-F-I"), 6.35, "tee-y-d Y-D-2 — fluid segment 13", "Beduan 1/4\" QC collet, facing aft (+Y) at the pump row"),
        _p("V-F-O", "bag-a-tray-assembly", "fluid", *contents.bag_a_tray_port("V-F-O"), 6.35, "tee-y-e Y-E-1 — fluid segment 14", "Beduan 1/4\" QC collet, facing forward (−Y) at the junction the pump returns through"),
        # Y-E's three, numbered from the end the BAG rides. This one stands ACROSS the strip ahead
        # of its pair, so its collets face along X and DOWN rather than along the pair's own axis:
        # the reservoir line and the draw are the run's two, and the fill is the branch.
        _p("Y-E-1", "tee-y-e", "fluid", *contents.y_e_port("Y-E-1"), 6.35, "bag-a-tray-assembly V-F-O — fluid segment 14", "PP0208E 1/4\" PTC BRANCH, facing DOWN (−Z) on V-F's own column at the leg that climbs into it"),
        _p("Y-E-2", "tee-y-e", "fluid", *contents.y_e_port("Y-E-2"), 6.35, "foam-assembly reservoir-A — fluid segment 15", "PP0208E 1/4\" PTC RUN, the EAST of the two, facing back down the tray-east lane at the bag line that crosses the machine to the core's face"),
        # The pump row's two tees. Y-C's run carries the bag draw forward into the pump and its
        # branch takes the fall from the selects pair; Y-D's run carries the pump's outlet aft to
        # the bag's fill valve and its branch is the climb to the loft. Both stand on the pump
        # lane, so both runs face along Y and both branches face up.
        _p("Y-C-1", "tee-y-c", "fluid", *contents.y_c_port("Y-C-1"), 6.35, "selects-tray-assembly V-C-O \u2014 fluid segment 9", "PP0208E 1/4\" PTC BRANCH, facing up (+Z) at the selects pair's fall"),
        _p("Y-C-2", "tee-y-c", "fluid", *contents.y_c_port("Y-C-2"), 6.35, "bag-a-tray-assembly V-E-O \u2014 fluid segment 10", "PP0208E 1/4\" PTC RUN, the AFT of the two, facing back up the pump lane at the bag draw"),
        _p("Y-C-3", "tee-y-c", "fluid", *contents.y_c_port("Y-C-3"), 6.35, "pump-b P-B-I \u2014 fluid segment 11", "PP0208E 1/4\" PTC RUN, the FORWARD of the two, facing down the lane at pump B's inlet barb"),
        _p("Y-D-1", "tee-y-d", "fluid", *contents.y_d_port("Y-D-1"), 6.35, "pump-b P-B-O \u2014 fluid segment 12", "PP0208E 1/4\" PTC RUN, the FORWARD of the two, facing down the lane at pump B's outlet barb"),
        _p("Y-D-2", "tee-y-d", "fluid", *contents.y_d_port("Y-D-2"), 6.35, "bag-a-tray-assembly V-F-I \u2014 fluid segment 13", "PP0208E 1/4\" PTC RUN, the AFT of the two, facing back up the pump lane at the bag's fill valve"),
        _p("Y-D-3", "tee-y-d", "fluid", *contents.y_d_port("Y-D-3"), 6.35, "nozzle-tray-assembly V-G-I \u2014 fluid segment 17", "PP0208E 1/4\" PTC BRANCH, facing up (+Z) at the storey-high climb to the nozzle gate"),
        _p("Y-E-3", "tee-y-e", "fluid", *contents.y_e_port("Y-E-3"), 6.35, "bag-a-tray-assembly V-E-I — fluid segment 16", "PP0208E 1/4\" PTC RUN, the WEST of the two, facing west along the strip at the leg that falls to V-E"),
        # The bag-B pair's four — bag A's circuit mirrored, so the same clocking and the same map.
        # The bag's two ends face FORWARD at Y-H; V-H-O and V-I-I face AFT at channel B's pump.
        _p("V-H-I", "bag-b-tray-assembly", "fluid", *contents.bag_b_tray_port("V-H-I"), 6.35, "foam-assembly reservoir-B — fluid segment 26", "Beduan 1/4\" QC collet, facing forward (−Y) at the divider the bag draws through"),
        _p("V-H-O", "bag-b-tray-assembly", "fluid", *contents.bag_b_tray_port("V-H-O"), 6.35, "tee-y-f Y-F-2 — fluid segment 20", "Beduan 1/4\" QC collet, facing aft (+Y) into the junction bay at Y-F's branch"),
        _p("V-I-I", "bag-b-tray-assembly", "fluid", *contents.bag_b_tray_port("V-I-I"), 6.35, "tee-y-g Y-G-3 — fluid segment 23", "Beduan 1/4\" QC collet, facing aft (+Y) into the bay, its leg climbing into Y-G's WEST outlet overhead"),
        _p("V-I-O", "bag-b-tray-assembly", "fluid", *contents.bag_b_tray_port("V-I-O"), 6.35, "foam-assembly reservoir-b-fill — fluid segment 24", "Beduan 1/4\" QC collet, facing forward (−Y) at the divider the pump returns through"),
        # The nozzle gates' four. Both INLETS face forward at the two pump rows that feed them —
        # one in the front column, one in this loft — and both OUTLETS aft at the rear panel.
        _p("V-G-I", "nozzle-tray-assembly", "fluid", *contents.nozzle_tray_port("V-G-I"), 6.35, "tee-y-d Y-D-3 — fluid segment 17", "Beduan 1/4\" QC collet, facing forward (−Y) into the junction bay at the storey-and-a-half climb from channel A's pump row"),
        _p("V-G-O", "nozzle-tray-assembly", "fluid", *contents.nozzle_tray_port("V-G-O"), 6.35, "bulkhead-flavor-a tube-in — fluid segment 18", "Beduan 1/4\" QC collet, facing aft (+Y) at the rear panel's flavor-A bulkhead"),
        _p("V-J-I", "nozzle-b-tray-assembly", "fluid", *contents.nozzle_b_tray_port("V-J-I"), 6.35, "tee-y-g Y-G-2 — fluid segment 27", "Beduan 1/4\" QC collet, facing forward (−Y) down the stand's east lane, round V-K's plate and west under the trident into Y-G's EAST outlet"),
        _p("V-J-O", "nozzle-b-tray-assembly", "fluid", *contents.nozzle_b_tray_port("V-J-O"), 6.35, "bulkhead-flavor-b tube-in — fluid segment 28", "Beduan 1/4\" QC collet, facing aft (+Y) at the rear panel's flavor-B bulkhead"),
        # Channel B's pump row. Y-F's run lies along the loft's pump lane with its branch reaching
        # west at the bag pair; Y-G's run is the straight line the bay already holds, with its
        # branch standing up at the pump's high barb.
        _p("Y-F-1", "tee-y-f", "fluid", *contents.y_f_port("Y-F-1"), 6.35, "selects-tray-assembly V-D-O — fluid segment 19", "PP0208E 1/4\" PTC RUN, the AFT of the two, facing back up the loft's pump lane at the climb out of the front column"),
        _p("Y-F-2", "tee-y-f", "fluid", *contents.y_f_port("Y-F-2"), 6.35, "bag-b-tray-assembly V-H-O — fluid segment 20", "PP0208E 1/4\" PTC BRANCH, facing west (−X) across the junction bay at the bag-B draw"),
        _p("Y-F-3", "tee-y-f", "fluid", *contents.y_f_port("Y-F-3"), 6.35, "pump-a P-A-I — fluid segment 21", "PP0208E 1/4\" PTC RUN, the FORWARD of the two, facing down the lane at pump A's low barb"),
        _p("Y-G-1", "tee-y-g", "fluid", *contents.y_g_port("Y-G-1"), 6.35, "pump-a P-A-O — fluid segment 22", "PP2308E 1/4\" PTC STEM, facing up (+Z) at the climb to pump A's high barb"),
        _p("Y-G-2", "tee-y-g", "fluid", *contents.y_g_port("Y-G-2"), 6.35, "nozzle-b-tray-assembly V-J-I — fluid segment 27", "PP2308E 1/4\" PTC outlet, the EAST of the two, facing down (−Z) over the bay, on the lane the nozzle-B feed comes west down"),
        _p("Y-G-3", "tee-y-g", "fluid", *contents.y_g_port("Y-G-3"), 6.35, "bag-b-tray-assembly V-I-I — fluid segment 23", "PP2308E 1/4\" PTC outlet, the WEST of the two, facing down (−Z) over the bay, on the column the bag pair's own draw collet stands on"),
        # The two pumps' barbs. Each is the part's own station (`kamoer_kphm400.arch_xs` on its
        # head's +Y face at the arch plane) carried through the turn and seat the body takes. A
        # peristaltic head has no fixed sense — the rotor's direction is the motor's wiring — so
        # which barb is suction and which discharge is an assignment, made so no leg crosses another.
        _p("P-A-I", "pump-a", "fluid", *contents.pump_port("pump-a", "P-A-I"), 6.35, "tee-y-f Y-F-3 — fluid segment 21", "Kamoer head barb, the LOW one on the lying pump's west face; a straight 1/4\" adapter takes the LLDPE"),
        _p("P-A-O", "pump-a", "fluid", *contents.pump_port("pump-a", "P-A-O"), 6.35, "tee-y-g Y-G-1 — fluid segment 22", "Kamoer head barb, the HIGH one on the lying pump's west face; a straight 1/4\" adapter takes the LLDPE"),
        _p("P-B-I", "pump-b", "fluid", *contents.pump_port("pump-b", "P-B-I"), 6.35, "tee-y-c Y-C-3 — fluid segment 11", "Kamoer head barb, the WEST one on the standing pump's aft face, on the bag-A pair's own port plane"),
        _p("P-B-O", "pump-b", "fluid", *contents.pump_port("pump-b", "P-B-O"), 6.35, "tee-y-d Y-D-1 — fluid segment 12", "Kamoer head barb, the EAST one on the standing pump's aft face, on the bag-A pair's own port plane"),
    ]

    # A foam-shell port's Ø is checked against the hole it actually crosses. The lane is one
    # bore wide, so there is a single number to check against, and a port declared fatter than
    # it is a line that does not go through the wall — whatever its fitting is on the warm side.
    # The `located` axis cannot catch this: it asks whether a coordinate lands on the body's
    # surface, and a Ø too big for the bore lands on the surface exactly as well as one that
    # fits. A component's own ports being self-consistent with its geometry is a property of
    # the declaration, so it is checked where the declaration is.
    foam_bore = contents.foam_shell_bore()
    for port in declared:
        if port.component == "foam-assembly" and port.diam is not None:
            assert port.diam <= foam_bore + 1e-9, (
                f"foam-assembly:{port.name} declares Ø{port.diam:g} through the shell's "
                f"Ø{foam_bore:g} port lane — it cannot cross the wall. Every transition happens "
                f"on the warm side (assembly/cold-core.md), so the Ø here is the line AT the wall")
    return declared


_PORTS = None


def ports() -> list:
    """The declared connector set. The same list object every call — `scorecard_selftest`
    appends a probe port to it and takes it away again."""
    global _PORTS
    if _PORTS is None:
        _PORTS = _declare_ports()
    return _PORTS


def __getattr__(name):
    """`scorecard.PORTS` from another module. A bare `PORTS` inside this one does not come
    through here, so this module's own readers call `ports()`."""
    if name == "PORTS":
        return ports()
    if name == "PLACEMENT_RULES":
        return placement_rules()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Components that carry NO tube or wire connector at all — a passive body, located trivially
# once declared connector-free. Declaring the absence is the honest analogue of declaring a
# position — never a silent gap, and it lets the located axis reach 100% without inventing a
# port. The basin catches the vent's drip and is drawn out to be emptied by hand, and its rails
# are structure; nothing joins either. A name here must own no PORTS entry (asserted in
# ports_audit).
PASSIVE_NO_PORTS: frozenset = frozenset({"drip-pan"})


def _on_bbox_surface(pos, bb, tol) -> bool:
    """True when `pos` lies on the bounding box's surface: inside (+tol) on every axis AND
    flush against at least one face."""
    x, y, z = pos
    axes = ((x, bb.xmin, bb.xmax), (y, bb.ymin, bb.ymax), (z, bb.zmin, bb.zmax))
    inside = all(lo - tol <= v <= hi + tol for v, lo, hi in axes)
    on_face = any(abs(v - lo) <= tol or abs(v - hi) <= tol for v, lo, hi in axes)
    return inside and on_face


def _face_shell(solid):
    """The solid's faces as one compound. Distance to a solid is 0 anywhere inside it; distance
    to its faces is the distance to its surface, which is what a port sits on."""
    comp = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(comp)
    for f in solid.Faces():
        builder.Add(comp, f.wrapped)
    return comp


def _surface_dist(pos, shell) -> float | None:
    """Exact distance from `pos` to the body's surface — None when only the box can answer."""
    if not _HAVE_EXACT or shell is None:
        return None
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(*pos)).Vertex()
    dss = BRepExtrema_DistShapeShape(v, shell)
    dss.Perform()
    return dss.Value() if dss.IsDone() else None


def _on_surface(pos, solid, shell, diam, tol) -> bool:
    """True when `pos` sits on the body's real surface. A port names the mouth of the bore it
    carries, so the allowance is one bore radius — the distance from a bore's centre out to its
    rim — plus tol. An opening is wherever the body has one: the free collet of an elbow, a
    connector on a populated board, a hole in a wall. Degrades to the bounding box when the exact
    kernel is unavailable."""
    d = _surface_dist(pos, shell)
    if d is None:
        return _on_bbox_surface(pos, _boxes.boxed(solid), tol)
    return d <= (diam or 0.0) / 2.0 + tol


# A FLUID port is the mouth of a bore a tube BUTTS: the tube is cut square, pushed to the
# collet face, and stops. So a fluid figure is held to the face itself, not the neighbourhood —
# three ways a declaration can miss it, each its own read:
#   adrift (rim)  — the point stands more than `FLUID_FACE_TOL` past its own bore radius off
#                   the body: nowhere near any face.
#   adrift (seat) — no material within `FLUID_FACE_SEAT` behind the plane it names: the face
#                   it claims to be the mouth of is not there, and a tube drawn to it ends in
#                   air. This is the read that catches a float over a SOLID-faced fitting,
#                   which sits inside the rim allowance for the whole of a small drift.
#   buried        — more than `FLUID_FACE_PAST` of the body stands past the plane: the
#                   declaration is inside the fitting, and a tube drawn to it interpenetrates.
# Electrical points land ON terminals and refrigerant stubs pass THROUGH walls into brazed
# bores; neither is a butted face, so both keep the loose on-surface read.
FLUID_FACE_TOL = 0.35
FLUID_FACE_SEAT = 0.5     # how far behind the face plane material must begin
FLUID_FACE_PAST = 1.0     # mm³ of own-body volume past the plane before it reads buried
_FLUID_WINDOW = 1.5       # the checks look this many bore Ø around the axis — one fitting,
                          # not the fused neighbour beside it


def _face_slabs(pos, face, diam, solid) -> tuple:
    """`(seated, past)` for a fluid face: the body's own volume in a window just BEHIND the
    plane the port names, and just PAST it. An open collet face reads (its rim annulus, ~0);
    a float reads (~0, ~0); a declaration inside the fitting reads (…, the slab between it
    and the face that is there). Windowed to `_FLUID_WINDOW` bore Ø so a sibling feature of
    the same fused body is not read as burial. A boolean that will not resolve raises — an
    unmeasured face is not an open one."""
    import cadquery as cq
    import _routing as R

    axis = R.normal_of(face)
    r = _FLUID_WINDOW * diam
    def _window(start_off, length):
        start = tuple(p + start_off * a for p, a in zip(pos, axis))
        return cq.Solid.makeCylinder(r, length, cq.Vector(*start), cq.Vector(*axis))
    out = []
    for win in (_window(-FLUID_FACE_SEAT - FLUID_FACE_TOL,
                        FLUID_FACE_SEAT + FLUID_FACE_TOL),   # behind the plane, up to it
                _window(FLUID_FACE_TOL, 3.0 * diam)):        # past it, clear of its own rim
        if _bbox_gap(_boxes.boxed(win), _boxes.boxed(solid)) > 0:
            out.append(0.0)
            continue
        try:
            out.append(win.intersect(solid).Volume())
        except Exception as exc:
            raise RuntimeError(
                f"the material about a fluid face at {tuple(round(c, 2) for c in pos)} could "
                f"not be measured ({exc}) — an unmeasured face is not an open one") from exc
    return tuple(out)


def _fluid_face_status(pos, face, diam, solid, shell) -> str | None:
    """The fluid-face verdict for one port: None when the face is where it says, else the
    status string carrying the measurement."""
    d = _surface_dist(pos, shell)
    rim = diam / 2.0
    if d is not None and d > rim + FLUID_FACE_TOL:
        return f"adrift — {d - rim:.2f} mm past a bore radius off the body"
    seated, past = _face_slabs(pos, face, diam, solid)
    if past > FLUID_FACE_PAST:
        return f"buried — {past:.0f} mm³ of the body past the face it names"
    if seated <= FLUID_FACE_PAST:
        return f"adrift — no material within {FLUID_FACE_SEAT:g} mm behind the face it names"
    return None


def ports_audit(solids: dict, tol: float = 2.0) -> list[tuple[str, bool, list]]:
    """Group PORTS by component; return (component, all_located, [(port, status)]) where status
    is 'ok' (positioned + on the placed body's surface + sized), 'off-surface' (a position not on
    the solid — a drifted/typo'd port), 'no-pos' (not yet located), or 'no-diam' (located but its
    bore Ø is still unknown). A FLUID port is held to its own collet face instead of the loose
    on-surface read — `adrift — …` when the face it names is not there (off the rim, or air
    behind the plane), `buried — …` when the body stands past it — each status carrying its
    measurement, because a tube drawn to a drifted face stops in air or inside the fitting and
    nothing else on the card would say so. A component is located only when every port is 'ok' —
    a full coordinate AND bore, the PCBA per-pad specificity. Components with no ports declared
    are not returned — like placement rules, they are simply not-yet-authored."""
    by_comp: dict[str, list[Port]] = {}
    for p in ports():
        by_comp.setdefault(p.component, []).append(p)
    contradiction = PASSIVE_NO_PORTS & by_comp.keys()
    assert not contradiction, f"declared connector-free but has ports: {sorted(contradiction)}"
    out = []
    for comp, comp_ports in by_comp.items():
        solid = solids.get(comp)
        shell = _face_shell(solid) if (solid is not None and _HAVE_EXACT) else None
        rows = []
        for p in comp_ports:
            fluid = (p.kind == "fluid" and p.pos is not None and p.diam is not None
                     and bool(p.face) and solid is not None and shell is not None)
            if p.pos is None:
                rows.append((p, "no-pos"))
            elif fluid:
                verdict = _fluid_face_status(p.pos, p.face, p.diam, solid, shell)
                rows.append((p, verdict if verdict is not None else "ok"))
            elif solid is None or not _on_surface(p.pos, solid, shell, p.diam, tol):
                rows.append((p, "off-surface"))
            elif p.diam is None:
                rows.append((p, "no-diam"))
            else:
                rows.append((p, "ok"))
        out.append((comp, all(s == "ok" for _pt, s in rows), rows))
    return out


# ── Geometry audits (the inputs the gates read) ─────────────────────────────
def _bbox_gap(a, b) -> float:
    """Min distance between two axis-aligned bounding boxes (0 if they overlap). A
    lower bound on the true solid gap, so it safely prefilters the exact query."""
    dx = max(0.0, a.xmin - b.xmax, b.xmin - a.xmax)
    dy = max(0.0, a.ymin - b.ymax, b.ymin - a.ymax)
    dz = max(0.0, a.zmin - b.zmax, b.zmin - a.zmax)
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def _solid_gap(a, b) -> float:
    """Exact min distance between two solids (0 if touching/overlapping). A gap that cannot
    be taken exactly raises; the scorecard prints what this returns as a measurement."""
    if not _HAVE_EXACT:
        raise RuntimeError(
            "exact solid distance is unavailable — OCP.BRepExtrema did not import, so no "
            "clearance here is a measurement")
    dss = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    if not dss.IsDone():
        raise RuntimeError(
            "exact solid distance did not resolve between two solids — the gap is unknown, "
            "not large")
    return dss.Value()


# The overlap every clash check reads, and it takes OCCT's boolean TWICE, because one ask is
# not a measurement.
#
# An exact Common hands back an EMPTY result — IsDone, no error, no solid — for two bodies
# whose surfaces are exactly TANGENT along the crossing. Two tubes of one Ø meeting on one
# stratum are that case, and the pack builds it deliberately: a port row fixes both runs to a
# single z, so their axes meet inside a plane, the two surfaces touch at the poles of the
# crossing and the section curve is singular at those two points. On sweeps this long, this
# far from the origin, the section step cannot resolve that node inside Precision::Confusion
# and returns nothing at all — a whole Steinmetz solid of interpenetration reported as zero,
# so the one arrangement most likely to be wrong is the one a single ask cannot see.
#
# So an empty exact result is asked again with a fuzz, and only then. The retry is bounded on
# both sides. Under 1e-5 the tangency is still unresolved (1e-6 returns the same nothing); far
# over it a fuzz SWALLOWS a real overlap shallower than itself, and CLASH_TOL is reached by a
# thin wide one (1 mm³ is 1e-5 mm over 100,000 mm²) as readily as by a deep narrow one. What
# it cannot do is invent an overlap: a fuzz raises the tolerance for merging coincident
# geometry, it does not grow the solids, so two bodies that merely touch — a tray on its lid,
# a foot on the floor slab — still measure zero however large it is, and the gate stays quiet
# on every seated part.
CLASH_FUZZ = 1e-5


def _common(a, b) -> tuple:
    """The solid two bodies share and its volume, as (shape, mm³). Empty is (shape, 0.0)."""
    if not _HAVE_EXACT:
        raise RuntimeError(
            "the exact boolean is unavailable — OCP.BRepAlgoAPI did not import, so no overlap "
            "here is a measurement")
    shape, vol = _common_at(a, b, 0.0)
    return (shape, vol) if vol > 0.0 else _common_at(a, b, CLASH_FUZZ)


def _common_at(a, b, fuzz: float) -> tuple:
    """One Common at one fuzz, as (cq shape, volume). Raises rather than reporting an
    unresolved boolean as a clean pair."""
    import cadquery as cq

    args, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
    args.Append(a.wrapped)
    tools.Append(b.wrapped)
    op = BRepAlgoAPI_Common()
    op.SetArguments(args)
    op.SetTools(tools)
    if fuzz:
        op.SetFuzzyValue(fuzz)
    op.Build()
    if not op.IsDone():
        raise RuntimeError(
            f"an intersection did not resolve between two solids (fuzz {fuzz:g}) — the overlap "
            f"is unknown, not absent")
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(op.Shape(), props)
    return cq.Shape.cast(op.Shape()), props.Mass()


def _common_volume(a, b) -> float:
    """Just the mm³ of `_common` — what the gates threshold against CLASH_TOL."""
    return _common(a, b)[1]


# ── Shape (the shaped axis) — the boxes a component really occupies ─────────────────────────
# A component is a set of bodies, and its boxes are their boxes: one per solid it is built from,
# following the part's own construction. The single box drawn around all of them is a different
# object — the compressor shroud's holds twenty times the shroud's material, a flavor pump's holds
# three times its own, and an elbow's is mostly the air in the corner of the L. `box_fill` is how
# much of the boxes is material: at 1.0 they are the part, and the lower it runs the less a box
# stands in for the shape and the more only the solid will answer (`_solid_gap`, `_on_surface`).
def component_boxes(shape) -> list:
    """One axis-aligned box per solid the component is built from."""
    return _boxes.boxed_solids(shape)


def _box_vol(bb) -> float:
    return bb.xlen * bb.ylen * bb.zlen


def box_fill(shape) -> float:
    """Material volume over the volume of the component's boxes."""
    total = sum(_box_vol(b) for b in component_boxes(shape))
    return shape.Volume() / total if total > 0 else 0.0


def is_primitive(shape) -> bool:
    """True when the geometry is a bare box or cylinder — makeBox leaves one solid with six
    planar faces, makeCylinder one solid with three (two planar caps and a round side). Authored
    geometry carries holes, bosses and fillets on top of that: the flattest real body in the pack,
    a probe plate with two lead holes, already has eight faces."""
    if len(shape.Solids()) != 1:
        return False
    faces = shape.Faces()
    planar = sum(1 for f in faces if f.geomType() == "PLANE")
    return (len(faces) == 6 and planar == 6) or (len(faces) == 3 and planar == 2)


def shape_audit(solids: dict) -> dict:
    """Per component: its boxes, how much of them is material, and whether the geometry is still
    a bare primitive — what the shaped axis measures the registry's declaration against."""
    return {n: (component_boxes(s), box_fill(s), is_primitive(s)) for n, s in solids.items()}


def pack_clashes(solids: dict, pieces: dict) -> list[tuple[str, str, float]]:
    """Every content pair, plus every content-vs-piece pair, whose overlap volume passes
    CLASH_TOL — the pack-closes gate (the box's original collision check, now the
    scorecard's first gate)."""
    if not _computes("pack-closes"):
        return []
    names = list(solids)
    bbs = {n: _boxes.boxed(solids[n]) for n in names}
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if _bbox_gap(bbs[a], bbs[b]) > 0:
                continue
            v = _common_volume(solids[a], solids[b])
            if v > CLASH_TOL:
                out.append((a, b, v))
    for hn, hs in pieces.items():
        hbb = _boxes.boxed(hs)
        for n in names:
            if _bbox_gap(hbb, bbs[n]) > 0:
                continue
            v = _common_volume(hs, solids[n])
            if v > CLASH_TOL:
                out.append((hn, n, v))
    return out


def clash_solids(solids: dict, pieces: dict, limit: int = DETAIL_MAX) -> list:
    """The intersection SOLID of each clashing pair pack_clashes reports (same pairs, same order,
    up to `limit`) — the overlap volume itself, returned as (a, b, shape). The dev editor renders
    these so a clash is a body you can see and frame under x-ray at the exact overlap, not just the
    two whole parts named. Kept out of pack_clashes so the gate stays a fast volume-only pass; the
    limit bounds the extra boolean work (a wild move can clash with many parts at once)."""
    names = list(solids)
    bbs = {n: _boxes.boxed(solids[n]) for n in names}
    out = []

    def add(a, b, sa, sb):
        try:
            inter, vol = _common(sa, sb)
            if vol > CLASH_TOL:
                out.append((a, b, inter))
        except Exception:
            pass  # a boolean that OCCT can't resolve just doesn't get a body — the gate still fails

    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if len(out) >= limit:
                return out
            if _bbox_gap(bbs[a], bbs[b]) > 0:
                continue
            add(a, b, solids[a], solids[b])
    for hn, hs in pieces.items():
        hbb = _boxes.boxed(hs)
        for n in names:
            if len(out) >= limit:
                return out
            if _bbox_gap(hbb, bbs[n]) > 0:
                continue
            add(hn, n, hs, solids[n])
    return out


# ── How deep one tube stands inside another ─────────────────────────────────────────────────
# A run is a centreline and a radius, so two runs are two chains of capsules: they overlap
# where their centrelines pass closer than the two radii together, and the amount under is how
# far one tube stands inside the other. `line_clashes` gates on VOLUME, which is the measure
# that carries every pair — a tube against a printed piece has no centreline to compare — and
# this is what a tube-against-tube row is read in. A third of a millimetre and a bore driven
# dead through its neighbour are 1 mm³ and 175 mm³; they are 0.32 mm and 6.35 mm.
#
# CHORD is the sag allowed when an arc is walked as segments, so a depth is that much coarse.
# It answers for a tube the sweep can make: a corner turning tighter than the tube's own radius
# sweeps a surface that closes on itself, where the distance-to-centreline reading and the solid
# part company. `bend-radius` is the gate that fails those corners.
CHORD = 0.05


def _run_polyline(run) -> list:
    """The run's centreline as points — straights whole, each arc walked at a step whose chord
    sag stays under CHORD."""
    pts = run.pts
    corner = {i: (run.radii[i], turn) for i, turn, _a, _b in run.bends}
    out = [tuple(pts[0])]
    for i in range(1, len(pts) - 1):
        if i not in corner:
            continue
        r, turn = corner[i]
        rad = math.radians(turn)
        tan = r * math.tan(rad / 2.0)
        din, dout = _unit_to(pts[i - 1], pts[i]), _unit_to(pts[i], pts[i + 1])
        p1 = [pts[i][k] - din[k] * tan for k in range(3)]
        p2 = [pts[i][k] + dout[k] * tan for k in range(3)]
        bis = _normalize([dout[k] - din[k] for k in range(3)])
        ctr = [pts[i][k] + bis[k] * (r / math.cos(rad / 2.0)) for k in range(3)]
        u = [(p1[k] - ctr[k]) / r for k in range(3)]
        v = [(p2[k] - ctr[k]) / r for k in range(3)]
        steps = max(1, math.ceil(rad / (2.0 * math.acos(max(-1.0, 1.0 - CHORD / r)))))
        out.append(tuple(p1))
        sweep = math.sin(rad)
        if sweep > 1e-12:
            for s in range(1, steps):
                f = s / steps
                a1, a2 = math.sin((1 - f) * rad) / sweep, math.sin(f * rad) / sweep
                out.append(tuple(ctr[k] + r * (a1 * u[k] + a2 * v[k]) for k in range(3)))
        out.append(tuple(p2))
    out.append(tuple(pts[-1]))
    return out


def _unit_to(a, b) -> list:
    return _normalize([b[k] - a[k] for k in range(3)])


def _normalize(v) -> list:
    ln = math.sqrt(sum(c * c for c in v)) or 1.0
    return [c / ln for c in v]


def _segment_gap(p1, q1, p2, q2) -> float:
    """Closest distance between two 3D segments (Ericson, Real-Time Collision Detection
    §5.1.9). Segments that lie parallel fall out of clamping s to [0, 1]."""
    d1 = [q1[i] - p1[i] for i in range(3)]
    d2 = [q2[i] - p2[i] for i in range(3)]
    r = [p1[i] - p2[i] for i in range(3)]
    a = sum(c * c for c in d1)
    e = sum(c * c for c in d2)
    f = sum(d2[i] * r[i] for i in range(3))
    c = sum(d1[i] * r[i] for i in range(3))
    if a <= 1e-12 or e <= 1e-12:
        s = 0.0 if a <= 1e-12 else max(0.0, min(1.0, -c / a))
        t = max(0.0, min(1.0, f / e)) if e > 1e-12 else 0.0
    else:
        b = sum(d1[i] * d2[i] for i in range(3))
        denom = a * e - b * b
        s = max(0.0, min(1.0, (b * f - c * e) / denom)) if denom > 1e-12 else 0.0
        t = (b * s + f) / e
        if t < 0.0:
            t, s = 0.0, max(0.0, min(1.0, -c / a))
        elif t > 1.0:
            t, s = 1.0, max(0.0, min(1.0, (b - c) / a))
    c1 = [p1[i] + d1[i] * s for i in range(3)]
    c2 = [p2[i] + d2[i] * t for i in range(3)]
    return math.sqrt(sum((c1[i] - c2[i]) ** 2 for i in range(3)))


def tube_depth(run_a, run_b) -> float:
    """How far the deeper of two runs stands inside the other, mm. 0.0 where they are clear."""
    reach = run_a.diam / 2.0 + run_b.diam / 2.0
    pa, pb = _run_polyline(run_a), _run_polyline(run_b)
    worst = 0.0
    for s1, s2 in zip(pa, pa[1:]):
        for u1, u2 in zip(pb, pb[1:]):
            worst = max(worst, reach - _segment_gap(s1, s2, u1, u2))
    return max(0.0, worst)


def line_clashes(lines: dict, solids: dict, ends: dict) -> list[tuple[str, str, float]]:
    """Every routed tube that INTERPENETRATES another tube, or a placed solid it does not
    terminate on, by overlap volume over CLASH_TOL — the routed analogue of pack_clashes. A tube
    driving through a part, or through another tube, is as unbuildable as two overlapping solids;
    but the tubes are _lines runs, not registry components, so pack_closes never sees them. `lines`
    is {id: tube-solid}, `ends` is {id: {the component names the run joins}} — the two components a
    run terminates on are skipped, since a tube seats INTO its end fittings' collets by design.

    Volume, not distance, is the test that matters here: BRepExtrema (the `_solid_gap` the routed
    clearance detail reads) returns 0 for a tube that just grazes another AND for one that drives
    clean through it — so only the overlap volume separates a kiss from an intersection. And the
    volume is `_common`, not one `intersect`: two tubes are the shape whose exact boolean comes
    back empty from an overlap, and a run pair is where that arrangement is authored on purpose.

    The printed pieces are in `solids` too. A wall is not a part a run may terminate on — every
    through-wall penetration is a panel BODY's (a bulkhead's), and the run stops at that body's
    inboard collet — so a tube inside a piece is always a defect. It is also the one the pack
    cannot show you: the runs share the ±X band with the seam's own posts and stations, and a
    tube driving through a post reads as clean geometry from every other check."""
    out = []
    ids = list(lines)
    lbb = {i: _boxes.boxed(lines[i]) for i in ids}
    sbb = {n: _boxes.boxed(solids[n]) for n in solids}
    for i, a in enumerate(ids):                                   # tube ∩ tube
        for b in ids[i + 1:]:
            if _bbox_gap(lbb[a], lbb[b]) > 0:
                continue
            v = _common_volume(lines[a], lines[b])
            if v > CLASH_TOL:
                out.append((a, b, v))
    for i in ids:                                                 # tube ∩ part it does not join
        for n, s in solids.items():
            if n in ends.get(i, ()):
                continue
            if _bbox_gap(lbb[i], sbb[n]) > 0:
                continue
            v = _common_volume(lines[i], s)
            if v > CLASH_TOL:
                out.append((i, n, v))
    return out


# ── Tube bend radius ────────────────────────────────────────────────────────
# A tube has a radius below which it stops being a tube: the wall on the inside of the turn
# buckles, the bore goes oval and then shut, and a push-to-connect collet a kink runs into no
# longer seals. That floor is a property of the STOCK — its material, its wall, its diameter —
# and not of the run, so it is stated here per stock and every run drawn in that stock is
# measured against it. Conventionally it is quoted as a multiple of OD, which is how these read.
#
# `min_bend` is the tightest CENTRELINE radius the stock takes. Two of the three are sourced;
# the LLDPE one is seeded, like CLEARANCE_FLOOR and `_routing.BEND_RATIO` — ~1 in. is the figure
# 1/4" polyethylene push-to-connect tube is commonly published at, and the tube actually bought
# ratifies it.
@dataclass
class Stock:
    name: str
    od: float            # the tube's outside Ø — the run's own `diam`
    min_bend: float      # tightest centreline radius, mm
    kinds: tuple         # the run kinds drawn in it
    source: str


STOCKS = (
    Stock("1/4\" LLDPE", 6.35, 25.4, ("fluid", "water", "co2"),
          "4×OD — seeded from the ~1 in. minimum 1/4\" polyethylene tube is published at"),
    Stock("1/4\" soft ACR copper", 6.35, 12.7, ("refrigerant",),
          "2×OD — a lever bender's smallest common former (_routing.BEND_RATIO)"),
    Stock("3/8\" braided PVC", 15.10, 15.9, ("water",),
          "neoPure PVCR-0610 datasheet minimum"),
)

# Grade bands on `radius ÷ the stock's minimum`. B is the requirement — a run AT its stock's
# floor is buildable and nothing more; A is the room that survives a part moving a millimetre.
GRADE_BANDS = ((1.5, "A"), (1.0, "B"), (0.75, "C"), (0.5, "D"), (0.0, "F"))
BEND_GRADE_PASS = "B"       # the worst grade a run may carry and still clear the gate


def stock_of(kind: str, od: float) -> Stock:
    """The stock a run is drawn in, from its kind and bore Ø. Raises on a pair no stock claims —
    a new tube on the machine states its own bend floor before its runs can be graded."""
    for s in STOCKS:
        if kind in s.kinds and abs(s.od - od) < 0.05:
            return s
    have = "; ".join(f"{s.name} Ø{s.od:g} for " + "/".join(s.kinds) for s in STOCKS)
    raise KeyError(
        f"no stock declared for a {kind} run at Ø{od:g} — add it to STOCKS with the minimum "
        f"bend radius its datasheet gives (have: {have})")


def grade_of(ratio: float) -> str:
    return next(g for lo, g in GRADE_BANDS if ratio >= lo)


def bend_radii(runs) -> list[dict]:
    """Every authored run graded on the radius it turns at, worst first.

    Two grades, because two different things are wrong when a bend is too tight:

      `drawn` — the radius the run is authored at over its stock's minimum. This is the
                buildable/not question, and the gate reads it.
      `reach` — the largest radius the run's own INTERIOR legs could seat, over the same
                minimum (`_routing.leg_caps`). This is the ceiling the PACK imposes: how gentle
                the run could be made if only its `bend=` were raised.

    The pair is the diagnostic. `drawn` F with `reach` A is an authoring number — one edit in
    `_lines.py` and the run is legal. `drawn` F with `reach` F is a placement: the lane the run
    passes through is too short to turn in at any legal radius, and something on either side of
    it has to move. The leads are held out of `reach` on purpose — a run's exit and approach
    stubs are reaches the author picks, so counting them would blame the pack for a number it
    does not own, and every run whose stub is one bend radius (`_routing.STUB`) would report a
    ceiling exactly at the radius it is already drawn at.

    HOLDING THE LEADS OUT CUTS BOTH WAYS, and a high `reach` on a run whose worst corner sits
    on an END leg is the one reading to distrust. `reach` says the interior is roomy; it says
    nothing about whether that end leg can grow, and there are three reasons it may not:

      - the leg is a `route` stub aimed at a constraint that stands nearer than the reach, so
        lengthening it OVERSHOOTS and folds the corner back on itself (`_routing.BLOCKED`
        names this: a corner turning 180° between a leg and the overshoot it came back on);
      - the leg is a `route` approach and the path stands off the port face by less than the
        stub asks, so the close backs out and comes straight back in;
      - the run is `bent` with no `lead`, in which case there IS no stub — the first and last
        legs are the hand-placed geometry itself, and their length is a station's to change.

    So a `reach` A row is a candidate, not a fix. What tells the two apart is whether the end
    leg is a reach the author picks or a distance the pack sets, and that is read at the call
    in `_lines.py`, not off this row.

    `reach` bounds the CENTRELINE and nothing else. A run redrawn at its reach sweeps a wider
    tube through different air, so it is a radius the waypoints seat, not one the pack has room
    for — `lines-clear` and the routed clearances are what answer that, after the edit.

    A run with no corner carries no bend to grade: `grade` is None and it is out of the gate's
    population. The radius on a straight run is the one it would turn at if it turned.
    """
    import _routing as R

    rows = []
    for r in runs:
        st = stock_of(r.kind, r.diam)
        caps = R.leg_caps(r)
        inner = [c for c in caps if c[4] == "interior"]
        seat = min((c[0] for c in caps), default=float("inf"))
        hold = min((c[0] for c in inner), default=float("inf"))
        binding = min(inner, key=lambda c: c[0]) if inner else None
        turns = [t for _i, t, _a, _b in r.bends]
        # Each CORNER is graded on the radius it turns at, and the run reports its worst. A run
        # holds as many radii as it has corners (`_routing.seat_radii`), so one number for the
        # whole run is the tightest of them and says nothing about the rest.
        corners = [{"at": i, "turn": round(t, 1), "radius": round(r.radii[i], 3),
                    "ratio": round(r.radii[i] / st.min_bend, 4),
                    "grade": grade_of(r.radii[i] / st.min_bend),
                    "legs": [round(a, 2), round(b, 2)]}
                   for i, t, a, b in r.bends]
        tightest = min((c["radius"] for c in corners), default=r.bend)
        ratio = tightest / st.min_bend
        rows.append({
            "id": r.id, "kind": r.kind, "frm": r.frm, "to": r.to,
            "stock": st.name, "od": r.diam,
            "radius": round(tightest, 3), "cap": round(r.bend, 3), "minBend": st.min_bend,
            "ratio": round(ratio, 4),
            "grade": grade_of(ratio) if turns else None,
            "need": need.figures(r),
            "corners": corners,
            "atSpec": sum(1 for c in corners if c["radius"] >= st.min_bend - 1e-9),
            "bends": len(turns), "worstTurn": round(max(turns), 1) if turns else None,
            "seat": None if seat == float("inf") else round(seat, 3),
            "reach": None if hold == float("inf") else round(hold, 3),
            "reachRatio": None if hold == float("inf") else round(hold / st.min_bend, 4),
            "reachGrade": None if not turns else ("A" if hold == float("inf")
                                                  else grade_of(hold / st.min_bend)),
            "binding": None if binding is None else {
                "leg": binding[1], "length": round(binding[2], 3),
                "demand": round(binding[3], 4),
                "from": [round(v, 2) for v in r.pts[binding[1]]],
                "to": [round(v, 2) for v in r.pts[binding[1] + 1]],
            },
        })
    order = {g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}
    # Worst first, and within a grade the run with the least room to improve — which is the
    # order the work wants: a run whose lanes cannot hold a legal bend is a part to move, and
    # one whose lanes can is a number to raise. The ungraded straights sort last.
    rows.sort(key=lambda d: (0 if d["grade"] else 1,
                             -order.get(d["grade"], 0), -order.get(d["reachGrade"], 0),
                             d["reachRatio"] if d["reachRatio"] is not None else 1e9))
    return rows


def part_clearances(solids: dict) -> list[tuple[str, str, float, bool]]:
    """Content pairs closer than REPORT_NEAR, as (a, b, gap, allowed) sorted tightest
    first. `allowed` marks a declared intentional contact (TOUCHING_OK). Part-to-wall is
    excluded on purpose — parts seat against walls by design; overlap there is the
    pack-closes gate's job, not clearance."""
    if not _computes("clearance-floor"):
        return []
    names = list(solids)
    bbs = {n: _boxes.boxed(solids[n]) for n in names}
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if _bbox_gap(bbs[a], bbs[b]) >= REPORT_NEAR:
                continue
            gap = _solid_gap(solids[a], solids[b])
            if gap < REPORT_NEAR:
                out.append((a, b, gap, frozenset((a, b)) in TOUCHING_OK))
    out.sort(key=lambda r: r[2])
    return out


# ── Mounted (a FOCUS axis) — the part whose printed feature fastens each component ──────────
# A component is MOUNTED when the feature that holds it is printed INTO another placed part.
# The board is the case the rest is read against: four boss columns stand in the cold core's top
# cap, so the cap holds the board, and the board is mounted whether or not the cap itself is.
# The test is local — what fastens THIS one — not a chain down to the floor.
#
# Resting on something is not being mounted, however closely. The front column's three trays
# carry mount ears and nothing under them answers: the bag-A plate rests over the refrigeration
# stratum, and the one body in reach — the compressor shroud, 12 mm under it — is sheet metal,
# which can carry no printed feature. Capture is not a fastener either: `foam-assembly` sits in
# a floor pocket, and `display` in a shell facet, and neither is mounted. Nor is adhesive.
#
# Distinct from the looser `held`, which is a declared holder STATE and counts both of those.
# The value here is the part whose printed geometry does the fastening, so each row names its
# own joint and an absent row is a component nothing yet fastens.
MOUNTED_BY = {
    # The cold core's top cap carries a boss column per hole; M3 SHCS into a ruthex short in each.
    # `deck-mounts-land` is the gate that measures whether each module still stands on all of its.
    "ground-stack": "foam-assembly",
    # The aft stand's two plates, bolted through their own mount ears to cap columns that stop
    # under the lid — the PSU's joint at the trays' stations. These rows read the other way from
    # the modules': the trays are placed by the enclosure's fences and the cap's table stands
    # where the placed ears land, held there by `deck-mounts-land`'s alignment rows.
    "bag-b-tray-assembly":  "foam-assembly",
    "vk-tray-assembly":     "foam-assembly",
    "nozzle-b-tray-assembly": "foam-assembly",
    "nozzle-tray-assembly": "foam-assembly",
    # Two M3 stations off `panel_screws()`, standing as bosses proud of the back panel's outer
    # face at insert depth plus a cap, drilled blind from the inner face.
    "c14-inlet":    "enclosure_back_top",
    # The basin rides a printed rail pair fused onto the back-top piece's −X wall, and stops
    # against a printed stop at the end of its travel (`contents.drip_pan_rails`,
    # `drip_pan_stop`). The rails take the tray's two 45° haunches on their inboard arrises,
    # so the pair pins it in plan and carries it in Z — a fastening with no fastener, which
    # is what a slide is. `enclosure._pan_rails` prints them; `mount_features` probes them.
    "drip-pan":     "enclosure_back_top",
}


# The cap deck mounts, and the solid each one carries. A module's own name IS its mount's
# except the ground bus, which is placed as the stack of lugs standing on its single column,
# and the aft stand's two trays, whose mounts follow THEM (`contents.TRAY_MOUNTS`).
# The cap's deck mounts, module by module. NO ELECTRICAL BODY is among them: the brick, the
# controller, the relay, the hub and the ground stud all hang on the +X wall
# (`_contents.EAST_WALL_SEAT`), so the joints that hold them are the wall's and not the cap's,
# and what the cap carries is the three fluid trays.
DECK_MOUNTED = {"bag-b-tray": "bag-b-tray-assembly",
                "vk-tray": "vk-tray-assembly",
                "nozzle-b-tray": "nozzle-b-tray-assembly",
                "nozzle-tray": "nozzle-tray-assembly"}


def deck_mount_landings(solids: dict) -> list[tuple[str, int, int, float]]:
    """Every cap deck mount, as (module, columns landed on, columns total, worst miss mm).

    A deck-mounted module is bolted down — one M3 through the module into a ruthex set in each
    column top — and the two ends of that joint are authored in DIFFERENT frames: the column is
    printed into the foam cap, the module rides the pack's own seat. So a module can be stood
    where no column reaches it and still rest on the cap, clear every other body, and read as
    seated everywhere else on this card. `clearance-floor` cannot see it either: cap-carries-module
    is a declared contact, and the contact stays true while the screws land in air.

    A column lands when the module has material directly over it — the plan test, cast as the
    column's own circle up the module's own height and intersected with it. `worst miss` is how
    far the furthest unlanded column stands from the module's outline, so the report says how far
    out it is and not just that it is out."""
    import cadquery as cq
    out = []
    for mount, name in sorted(DECK_MOUNTED.items()):
        if name not in solids:
            continue
        solid = solids[name]
        b = _boxes.boxed(solid)
        _ctr, cols, _top = contents.deck_mount(mount)
        landed, miss = 0, 0.0
        for cx, cy in cols:
            probe = (cq.Workplane("XY").workplane(offset=b.zmin - 1.0)
                     .circle(_cc.deck_mount_boss_radius)
                     .extrude(b.zlen + 2.0).val())
            probe = probe.translate((cx, cy, 0.0))
            # Per solid, and summed — NOT one boolean against the whole body. A tray
            # assembly is a COMPOUND (its plate and each of its valves are separate
            # solids), and a boolean against a compound under-reports: the same probe
            # that finds 264.65 mm³ of plate under an ear reads 0.00 against the
            # compound the plate is one of. A module with no material over a column is
            # a module whose screws land in air, so a false miss here is the check
            # calling a good joint bad — and a false LAND would be worse.
            if sum(probe.intersect(s).Volume() for s in solid.Solids()) > 1e-6:
                landed += 1
            else:
                miss = max(miss, min((_solid_gap(probe, s) for s in solid.Solids()),
                                     default=0.0))
        out.append((name, landed, len(cols), miss))
    return out


def tray_mount_alignment() -> list[tuple[str, float, list]]:
    """Each aft-stand plate's worst ear-hole-to-column miss in plan, mm, with the
    cap-frame stations its placed ears actually want.

    The two ends of a tray's joint are authored in different frames — the ear rides the
    tray's own seat, the column the cap's table — and the TRAY is the authority: it is
    placed by the enclosure's fences, and the table's stations are that derivation's
    result. The landing probe cannot read this (an ear is material over the column at
    any small drift), so this is the check that holds the table to the trays. A row past
    the mechanism's own slip is a moved tray, and its detail carries the stations the
    new pose wants, in the frame `_cold_core_interface.deck_mounts` is written in.

    The table's SEAT is the same kind of copy — the plate thickness the screw crosses
    before the lid — so a plate rethickened without the table hearing counts as the same
    drift, folded into the row's miss."""
    plate = contents.tray_mount_seat()
    out = []
    for mount, body in sorted(contents.TRAY_MOUNTS.items()):
        holes = contents.tray_mount_holes(mount)
        _ctr, cols, _top = contents.deck_mount(mount)
        worst = max(min(math.hypot(hx - cx, hy - cy) for cx, cy in cols)
                    for hx, hy in holes)
        worst = max(worst, abs(_cc.deck_mounts[mount].seat - plate))
        out.append((body, worst, [contents.foam_cap_frame(h) for h in holes]))
    return out


def mount_features(name: str) -> list[tuple[str, tuple]]:
    """The printed feature a joint stands on, as `(label, (x0, x1, y0, y1, z0, z1))` world
    boxes in the CARRIER's own solid.

    The deck family states its stations as columns and `deck_mount_landings` probes those;
    these are the joints whose feature is a run of material rather than a column."""
    if name == "drip-pan":
        return ([(f"rail {i}", b) for i, b in enumerate(contents.drip_pan_rails())]
                + [("stop", contents.drip_pan_stop())])
    if name == "c14-inlet":
        import enclosure as _enc
        d = _enc._dims()
        r = _enc.c14_boss_dia / 2.0
        y0, y1 = d.inner[3], d.inner[3] + _enc.heatset_depth
        return [(f"boss {i}", (sx - r, sx + r, y0, y1, sz - r, sz + r))
                for i, (sx, sz) in enumerate(contents.c14_screw_stations())]
    return []


def feature_probe(carrier, part, boxes) -> list[tuple[str, float, float, bool]]:
    """Per feature box: how much of it the CARRIER's solid fills, and whether the PART meets
    it. A joint is named against a feature, and both halves can be missing independently —
    the feature never printed, or the part standing away from one that was.

    `filled` is a presence figure and not a fit: a boss is an annulus in its own box and a
    rail fills its own, so what it separates is material from nothing."""
    import cadquery as cq
    out = []
    for label, (x0, x1, y0, y1, z0, z1) in boxes:
        vol = abs((x1 - x0) * (y1 - y0) * (z1 - z0))
        if vol < 1e-9:
            continue
        probe = cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
        filled = sum(probe.intersect(s).Volume() for s in carrier.Solids()) / vol
        out.append((f"{label} printed", filled, MOUNT_FEATURE_FILL,
                    filled >= MOUNT_FEATURE_FILL))
        gap = min((_solid_gap(probe, s) for s in part.Solids()), default=float("inf"))
        out.append((f"{label} met", gap, MOUNT_FEATURE_GAP, gap <= MOUNT_FEATURE_GAP))
    return out


# What a feature box must be to count as printed, and how far the part may stand off one.
# The fill is a presence floor — a boss is an annulus inside its own box, so a third of it
# is material — and the gap is the slip a sliding fit already carries.
MOUNT_FEATURE_FILL = 0.20
MOUNT_FEATURE_GAP = 1.0


def mount_audit(solids: dict, pieces: dict | None = None) -> list[tuple[str, str, bool, list]]:
    """For each component `MOUNTED_BY` names a carrier for, measure the joint and return
    (name, carrier, holds, [(label, value, bound_mm, ok)]).

    The rows are the joint's own figures, taken from the derivation that already computes
    them — the deck family's landing probe, its ear-to-bore alignment, and the seat its
    table was cut for. A carrier named with nothing measuring the joint returns a single
    unmeasured row that cannot hold: the distance between a fastening that is drawn and one
    that is only intended is exactly this measurement, and `MOUNTED_BY` alone does not
    cross it.

    Components with no carrier are not returned — they are simply not-yet-mounted."""
    if not _computes("mounted"):
        return []
    landings = {n: (landed, total, miss) for n, landed, total, miss in deck_mount_landings(solids)}
    aligned = {n: worst for n, worst, _want in tray_mount_alignment()}
    bodies = dict(solids, **(pieces or {}))
    out = []
    for name, carrier in sorted(MOUNTED_BY.items()):
        checks = []
        if name in landings:
            landed, total, miss = landings[name]
            checks.append((f"lands on {landed}/{total} columns", miss, 0.0, landed == total))
        if name in aligned:
            checks.append(("ear over its column's bore", aligned[name],
                           _cc.deck_mount_lid_slip, aligned[name] <= _cc.deck_mount_lid_slip))
        feats = mount_features(name)
        if feats and carrier in bodies and name in bodies:
            checks += feature_probe(bodies[carrier], bodies[name], feats)
        if not checks:
            checks.append(("no joint measured", float("inf"), 0.0, False))
        out.append((name, carrier, all(c[3] for c in checks), checks))
    return out


def fit_bed(pieces: dict, bed: tuple[float, float, float]) -> list[tuple[str, float, float, float, bool]]:
    """Each printed piece's extents vs the H2C bed (per-axis, the pieces are stored in
    print orientation). Mirrors _report_split's fit test."""
    bx, by, bz = bed
    out = []
    for n, s in pieces.items():
        b = _boxes.boxed(s)
        fits = b.xlen <= bx + BED_TOL and b.ylen <= by + BED_TOL and b.zlen <= bz + BED_TOL
        out.append((n, b.xlen, b.ylen, b.zlen, fits))
    return out


def seam_mates(pieces: dict) -> list[tuple[str, str, float, bool]]:
    """Every piece pair's overlap volume; under SLIP_TOL is a slide-fit seam, over is
    interference. Mirrors _report_split's piece∩piece test."""
    names = list(pieces)
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = pieces[a].intersect(pieces[b]).Volume()
            out.append((a, b, v, v < SLIP_TOL))
    return out


# ── The scorecard ───────────────────────────────────────────────────────────
@dataclass
class Check:
    id: str
    label: str
    kind: str            # "gate" | "goal"
    status: str          # "pass" | "fail" | "warn"
    value: str
    target: str
    detail: list = field(default_factory=list)
    active: bool = True   # goal axes only: False renders gray (deferred, not yet worked)


@dataclass
class Scorecard:
    checks: list
    gates_pass: bool
    placed: int
    located: int
    shaped: int
    routed: int
    held: int
    mounted: int
    ports: list = field(default_factory=list)   # the full connector inventory — every port's
                                                # component, position, face, bore Ø, mate, and
                                                # status. Uncapped (unlike check.detail, which
                                                # DETAIL_MAX trims), so the audit reads every
                                                # coordinate + diameter straight from the sidecar.
    shapes: list = field(default_factory=list)  # per component: the boxes it really occupies (one
                                                # per solid it is built from), how much of them is
                                                # material, and whether the geometry is still a
                                                # bare primitive. Also uncapped.
    bends: list = field(default_factory=list)   # per routed run: the radius it turns at, the stock
                                                # minimum it is graded against, and the interior
                                                # leg that caps how gentle it could be made.
                                                # Uncapped, unlike the gate's own detail.
    mounts: list = field(default_factory=list)  # per component: the part whose printed feature
                                                # fastens it (None = the joint is still to
                                                # design) and what merely holds it today. The
                                                # other focus axis's table, in the same form.
    poses: list = field(default_factory=list)   # per component: whether its POSE is settled or
                                                # provisional, and for a settled one the
                                                # statement of what is settled. Reported, never
                                                # graded — provisional is a true state of the
                                                # work and not a shortfall in it.


def _pct(done: int, total: int) -> int:
    return 100 if total == 0 else round(100 * done / total)


def routed_check(solids=None) -> tuple:
    """The routed goal axis on its own — a (Check, pct) pair. Kept separate from the component
    gates and audits because it reads _lines (which route work changes every build) while the
    component audits do not: a build reusing cached component audits still recomputes this fresh,
    so the routed % never goes stale. Given the placed solids, each authored run's detail carries
    its tightest gap to a part it does not terminate on — the tube↔part clearance."""
    if not _computes("routed"):
        return _stood_down("routed", "Connections modeled as real 3D paths", "goal"), 0
    import _lines
    conns = load_connections()
    fluid = sum(1 for c in conns if c.kind == "fluid")
    wire = sum(1 for c in conns if c.kind == "wire")
    refrig = sum(1 for c in conns if c.kind == "refrigerant")
    water = sum(1 for c in conns if c.kind == "water")
    co2 = sum(1 for c in conns if c.kind == "co2")
    routed_done = sum(1 for c in conns if c.routed)
    blocked = sum(1 for c in conns if c.blocked)
    routed = _pct(routed_done, len(conns))
    # Derived, not narrated: a hand-written account of which paths stand goes stale the
    # build after it is written, and this line is the one a reader takes the state from.
    routed_detail = [f"{fluid} fluid + {water} water + {co2} CO2 + {refrig} refrigerant + "
                     f"{wire} electrical; {routed_done} routed, {blocked} blocked by the pack, "
                     f"{len(conns) - routed_done - blocked} waiting on an author or on a body "
                     f"the pack has not placed"]
    # The per-run nearest-gap report is an exact solid-distance query against every body.
    # HSM_SKIP_CLEARANCES drops it; each run's ports, length and bends still print, and
    # `lines-clear` still gates on interpenetration.
    if solids is None or os.environ.get("HSM_SKIP_CLEARANCES"):
        runs = [(r, None) for r in _lines.build_runs()]
    else:
        runs = _lines.clearances(solids)
    for r, near in runs:
        gap = f" — nearest {near[0]:.2f} mm to {near[1]}" if near else ""
        routed_detail.append(f"✓ {r.id}: {r.frm} → {r.to} — Ø{r.diam:g} × {r.length:.1f} mm, "
                             f"{len(r.bends)} bends at R{r.bend:.1f}{gap}")
    # A blocked connection stays counted, with the measurement that blocks it.
    for c in conns:
        if c.blocked:
            routed_detail.append(f"✗ {c.id}: BLOCKED — {c.blocked}")
    ck = Check("routed", "Connections modeled as real 3D paths (fluid + water + CO2 + refrigerant + electrical)",
               "goal", "pass" if (routed == 100 and bool(conns)) else "warn",
               f"{routed}% ({routed_done}/{len(conns)})", "100%", routed_detail[:DETAIL_MAX], False)
    return ck, routed


def lines_clear_check(solids: dict, pieces: dict) -> Check:
    """The tube-interpenetration GATE, computed fresh every build. Like routed_check it reads
    _lines — which route work rewrites every build — so it is kept OUT of the cached component
    verdict and recomputed on a cache hit; a route-only change must never serve a stale clash
    verdict. It builds each authored run's swept tube and gates on line_clashes: no routed tube
    may drive through a part it does not terminate on, through a printed piece, or through another
    tube. Blocks the export alongside pack-closes (enclosure_assembly.main) — a tube that
    intersects another solid is as physically unbuildable as two overlapping parts."""
    if not _computes("lines-clear"):
        return _stood_down("lines-clear",
                           "No routed tube intersects a part, a piece or another tube")
    import _lines
    import _routing as R
    runs = _lines.build_runs()
    lines = {r.id: R.tube(r) for r in runs}
    ends = {r.id: {r.frm.split(".")[0], r.to.split(".")[0]} for r in runs}
    clashes = line_clashes(lines, {**solids, **pieces}, ends)
    by_id = {r.id: r for r in runs}
    rows = []
    for a, b, v in clashes[:DETAIL_MAX]:
        # A run against a run is read in mm of tube inside tube; everything else has only
        # the volume, since a printed piece carries no centreline to stand off.
        if a in by_id and b in by_id:
            rows.append(f"{a} ∩ {b}: {tube_depth(by_id[a], by_id[b]):.2f} mm deep, {v:.1f} mm³")
        else:
            rows.append(f"{a} ∩ {b}: {v:.1f} mm³")
    return Check("lines-clear", "No routed tube intersects a part, a piece or another tube", "gate",
                 "pass" if not clashes else "fail", f"{len(clashes)} clash", "0 clash", rows)


def bend_radius_check() -> tuple:
    """The bend-radius GATE and the table behind it — a (Check, rows) pair. Reads _lines, so it
    is recomputed on a cache hit like `routed` and `lines-clear`; a route redrawn at a new radius
    must never be graded on the last build's corners.

    A tube turned tighter than its stock takes kinks: the bore goes oval and then shut, and the
    machine cannot be assembled with that piece of tube in it. That is the same class of defect
    as two solids overlapping, so it gates rather than scores — the anticipated one this file's
    clearance note has been naming since it was written. It reports without blocking the export,
    as every gate but pack-closes and lines-clear does."""
    import _lines
    rows = bend_radii(_lines.build_runs())
    order = {g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}
    limit = order[BEND_GRADE_PASS]
    graded = [d for d in rows if d["grade"]]
    straight = len(rows) - len(graded)
    short = [d for d in graded if order[d["grade"]] > limit]
    hist = {g: sum(1 for d in graded if d["grade"] == g) for _lo, g in GRADE_BANDS}
    pinned = sum(1 for d in short if order[d["reachGrade"]] > limit)
    worst = graded[0]["grade"] if graded else "A"
    tally = " ".join(f"{g}:{hist[g]}" for _lo, g in GRADE_BANDS if hist[g])

    corners = [c for d in rows for c in d["corners"]]
    at_spec = sum(d["atSpec"] for d in rows)
    detail = ["grade = radius ÷ the stock's minimum — " + ", ".join(
        f"{s.name} R{s.min_bend:g} ({s.source})" for s in STOCKS)]
    # Every CORNER turns at its own radius, so the population is corners and a run's grade is the
    # worst of the ones it holds. A run reading F on one corner and A on three is the ordinary
    # case, and the run figure alone hides which.
    detail.append(
        f"{at_spec}/{len(corners)} CORNERS at or above their stock's minimum, across "
        f"{len(graded)} bent runs")
    detail.append(
        f"{len(graded) - len(short)}/{len(graded)} runs with every corner at or above it; "
        f"{tally}; {straight} straight runs carry no bend to grade. Rows read "
        f"drawn/reach — `reach` is the largest radius this run's INTERIOR legs could seat, so a "
        f"row failing on BOTH is a placement to move and not a number to raise ({pinned} of "
        f"{len(short)}). Reach bounds the centreline only: a run redrawn at it sweeps a wider "
        f"tube, and lines-clear is what says whether that fits. Each row ends with its NEED — "
        f"the span its two ends stand apart, split by axis, against the path drawn: a path far "
        f"over its span rides infrastructure its ends do not ask for, and there the move is "
        f"the route, not the corner (need.py prints the pack's table, worst first).")
    # Which BODIES the pinned runs hang off. A reach failure is a leg too short to turn in, and
    # a leg is short because of where its run's two ends stand — so the components on the ends
    # of those runs are the ones a fix moves, and the ones carrying several are where to start.
    pin = {}
    for d in rows:
        if d["reachGrade"] and order[d["reachGrade"]] > limit:
            for comp in (d["frm"].split(".")[0], d["to"].split(".")[0]):
                pin.setdefault(comp, []).append(d["id"])
    ranked = sorted(pin.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:8]
    if ranked:
        detail.append("pinned runs hang off: " + "; ".join(
            f"{c} ×{len(ids)} ({', '.join(sorted(ids))})" for c, ids in ranked))
    for d in rows:
        b = d["binding"]
        where = (f"leg {b['leg']}→{b['leg'] + 1} is {b['length']:.2f} mm and wants "
                 f"{b['demand']:.2f}×R, {tuple(b['from'])}→{tuple(b['to'])}"
                 if b else "no interior leg — its own stubs alone hold it")
        if not d["grade"]:
            detail.append(f"—/— {d['id']}: straight, no bend — {d['stock']}, R{d['radius']:.2f} "
                          f"if it turned")
            continue
        n = d["need"]
        detail.append(
            f"{d['grade']}/{d['reachGrade']} {d['id']} ({d['frm']} → {d['to']}): "
            f"{d['atSpec']}/{d['bends']} corners at spec, tightest R{d['radius']:.2f} = "
            f"{d['ratio']:.2f}× the {d['stock']} minimum (R{d['minBend']:g}) under a cap of "
            f"R{d['cap']:.2f}, corners "
            + "[" + ", ".join(f"{c['at']}:R{c['radius']:.1f}{c['grade']}" for c in d["corners"])
            + "] — reach "
            + (f"R{d['reach']:.2f} ({d['reachRatio']:.2f}×): {where}"
               if d["reach"] is not None else f"unbounded: {where}")
            + f" — need Δ({n['axis']['x']:g}, {n['axis']['y']:g}, {n['axis']['z']:g}) "
            + f"span {n['span']:g}, path {n['path']:g}"
            + (f" = {n['detour']:.2f}× span" if n["detour"] is not None else ""))
    # Worst-first, so the cap takes the best rows off the end. Say so rather than letting the
    # list end where a reader would read it as complete; `scorecard.bends` carries all of them.
    if len(detail) > FOCUS_DETAIL_MAX:
        detail = detail[:FOCUS_DETAIL_MAX - 1] + [
            f"… {len(detail) - FOCUS_DETAIL_MAX + 1} further rows not shown — the list is "
            f"worst-first, so these grade better or are ungraded straights; the sidecar's "
            f"`bends` table carries all {len(rows)}"]
    ck = Check("bend-radius", "Every routed tube turns at or above its stock's minimum radius",
               "gate", "pass" if not short else "fail",
               f"{worst} — {at_spec}/{len(corners)} corners at spec",
               f"every corner ≥ its stock's minimum ({BEND_GRADE_PASS})", detail)
    return ck, rows


def build_scorecard(solids: dict, pieces: dict, bed: tuple[float, float, float], inner: tuple) -> Scorecard:
    reg = {c.name: c for c in COMPONENTS}
    checks: list[Check] = []

    def _cap(cid):
        return FOCUS_DETAIL_MAX if cid in FOCUS_IDS else DETAIL_MAX

    def gate(cid, label, ok, value, target, detail=None):
        checks.append(Check(cid, label, "gate", "pass" if ok else "fail", value, target, (detail or [])[:_cap(cid)]))

    def goal(cid, label, done, value, target, detail=None, active=True):
        checks.append(Check(cid, label, "goal", "pass" if done else "warn", value, target, (detail or [])[:_cap(cid)], active))

    # ── GATES — must hold to print + assemble what is placed ──
    # Coverage: the registry must describe exactly the placed set, or the goal counts
    # below are measured against the wrong universe.
    placed_set = set(solids)
    declared = set(reg)
    undeclared = sorted(placed_set - declared)
    unplaced = sorted(declared - placed_set)
    # A settled pose whose name is not a component stands as authority over a body the pack
    # does not have.
    orphan_settled = sorted(set(SETTLED) - declared)
    gate("coverage", "Every placed part declared in the registry",
         not undeclared and not unplaced and not orphan_settled,
         f"{len(placed_set & declared)}/{len(placed_set)} placed declared", "all declared",
         [f"{n}: placed but not declared" for n in undeclared]
         + [f"{n}: declared but not placed" for n in unplaced]
         + [f"{n}: pose declared settled but no such component" for n in orphan_settled])

    clashes = pack_clashes(solids, pieces)
    gate("pack-closes", "No two solids overlap (pack closes)", not clashes,
         f"{len(clashes)} clash", "0 clash",
         [f"{a} ∩ {b}: {v:.1f} mm³" for a, b, v in clashes])

    # A pose derived from a band it does not have still lands, and pack-closes reads the overlap
    # it makes — but a band short of what stands in it is a measurement, and the body that has to
    # move to give it back is often not either of the two the clash names. `_contents.SHORT` is
    # filled as the pack is built, so this reads the same build the solids above came from.
    gate("room-holds", "Every derived pose has the room its own construction states",
         not contents.SHORT, f"{len(contents.SHORT)} short", "0 short",
         [f"{who}: {why}" for who, why in sorted(contents.SHORT.items())])

    # The routed tubes clash against the placed solids the same way — but they live outside the
    # component registry, so pack-closes never sees them. Fresh every build (reads _lines); the
    # cache layer recomputes it on a hit, like routed.
    checks.append(lines_clear_check(solids, pieces))

    # And they have to be BENDABLE. lines-clear says a tube's path is free of everything else;
    # this says the path can be made out of that tube at all.
    bend_ck, bend_rows = bend_radius_check()
    checks.append(bend_ck)

    # Body-to-body clearance says two parts do not touch; it never says a connector between
    # them can be used. This does: every tube port gets its own bore cast along its own axis
    # for the straight a run off it would take. Two trays a clean millimetre apart with their
    # collets facing each other pass every other check on this card and pass nothing a tube
    # can be built through.
    leads = port_leads(solids)
    short = [r for r in leads if not r[5] and r[6]]
    ungated = [r for r in leads if not r[6]]
    gate("port-leads", "Every tube port has the straight a run off it needs", not short,
         f"{sum(1 for r in leads if r[6]) - len(short)}/{sum(1 for r in leads if r[6])} clear",
         "all clear",
         [f"{c}.{p}: {free:.2f} mm to {who}, needs {need:.2f} — ✗ no room to leave"
          for c, p, who, free, need, ok, _g in short]
         + [f"{c}.{p}: {free:.2f} mm to {who}, needs {need:.2f} — picked on placeholder "
            f"geometry, not gated" for c, p, who, free, need, ok, _g in ungated if not ok])

    clr = part_clearances(solids)
    violations = [(a, b, g) for a, b, g, allowed in clr if not allowed and g < CLEARANCE_FLOOR]
    tightest = next(((a, b, g) for a, b, g, allowed in clr if not allowed), None)
    gate("clearance-floor", "Part↔part clearance ≥ floor (unless a declared contact)", not violations,
         f"{tightest[2]:.2f} mm" if tightest else "—", f"≥ {CLEARANCE_FLOOR} mm",
         # Show the tightest handful either way, marking declared contacts and violations.
         [f"{a} — {b}: {g:.2f} mm" + (" — CONTACT (declared ok)" if allowed else (" — ✗ below floor" if g < CLEARANCE_FLOOR else ""))
          for a, b, g, allowed in clr[:DETAIL_MAX]])

    # A module bolted to the cap and the columns it bolts to are authored in different frames,
    # so nothing else on this card compares them: the contact between them is declared, and a
    # module standing where no column reaches still makes it. This is what reads the joint —
    # landings for the modules the stations place, and hole-to-bore alignment for the trays
    # the stations follow.
    land = deck_mount_landings(solids)
    off = [r for r in land if r[1] < r[2]]
    align = tray_mount_alignment()
    adrift = [r for r in align if r[1] > _cc.deck_mount_lid_slip]
    gate("deck-mounts-land", "Every cap-mounted module stands on all of its own columns",
         not off and not adrift,
         f"{sum(r[1] for r in land)}/{sum(r[2] for r in land)} columns landed", "all landed",
         [f"{n}: {c}/{t} columns under it — furthest stands {m:.2f} mm off its outline"
          for n, c, t, m in off]
         + [f"{n}: an ear hole stands {m:.2f} mm off its column's bore — the tray moved and the "
            f"cap's table has not. `_cold_core_interface.deck_mounts` wants stations "
            + "; ".join(f"({x:.2f}, {y:.2f})" for x, y in want)
            for n, m, want in adrift])


    beds = fit_bed(pieces, bed)
    over = [r for r in beds if not r[4]]
    gate("pieces-fit-bed", f"Each printed piece fits the H2C bed ({bed[0]:g}×{bed[1]:g}×{bed[2]:g})", not over,
         f"{len(beds) - len(over)}/{len(beds)} fit", f"{len(beds)}/{len(beds)}",
         [f"{n}: {x:.0f}×{y:.0f}×{z:.0f} mm — OVER" for n, x, y, z, _f in over])

    seams = seam_mates(pieces)
    interf = [r for r in seams if not r[3]]
    gate("seams-mate", "Printed pieces mate to a slide fit", not interf,
         f"{len(interf)} interfering", "0 interfering",
         [f"{a} ∩ {b}: {v:.1f} mm³ — INTERFERENCE" for a, b, v, ok in interf])

    unsourced = [c for c in COMPONENTS if not c.sourced]
    gate("parts-sourced", "Every component is a selected real part / finished print", not unsourced,
         f"{len(COMPONENTS) - len(unsourced)}/{len(COMPONENTS)}", f"{len(COMPONENTS)}/{len(COMPONENTS)}",
         [f"{c.name}: {c.note}" for c in unsourced])

    # ── GOALS — five realization axes. placed + located + shaped are the focus (rendered live);
    # routed + held wait behind them (rendered gray). Scored by authorship, not collision. ──
    total = len(COMPONENTS)

    # placed — FOCUS: placement criteria defined AND currently held (measured face-to-datum).
    pa = placement_audit(solids, inner)
    placed_held = [r for r in pa if r[1]]
    placed_pct = _pct(len(placed_held), total)

    def _fmt(cks):
        return " ".join(
            f"{f} {g:.1f}" + ("" if ok else (f"(<{mx:g})" if f.startswith("clear") else f"(>{mx:g})"))
            for f, g, mx, ok in cks)
    placed_detail = [f"{'✓' if ok else '✗'} {name}: {_fmt(cks)} mm" for name, ok, cks in pa]
    placed_detail.append(f"{total - len(pa)} components: no placement rules defined yet")
    goal("placed", "Placement criteria defined and held (face-to-datum)", placed_pct == 100,
         f"{placed_pct}% ({len(placed_held)}/{total})", "100%", placed_detail, active=False)

    # located — FOCUS: every connector (tube + wire) has a position AND a bore on the component.
    # A connection has no path until both ends are located, so this is the precondition to routed.
    # A declared connector-free part (PASSIVE_NO_PORTS) counts once — it has nothing to locate.
    pta = ports_audit(solids)
    passive = [c for c in COMPONENTS if c.name in PASSIVE_NO_PORTS]
    located_comps = [r for r in pta if r[1]]
    located_pct = _pct(len(located_comps) + len(passive), total)
    _pstat = {"off-surface": "⚠ off-surface", "no-pos": "needs a position", "no-diam": "needs a bore Ø"}
    located_detail = []
    for comp, ok, prows in pta:
        n_ok = sum(1 for _pt, s in prows if s == "ok")
        located_detail.append(f"{'✓' if ok else '✗'} {comp}: {n_ok}/{len(prows)} connectors located")
        for pt, s in prows:
            xyz = f"({pt.pos[0]:g}, {pt.pos[1]:g}, {pt.pos[2]:g}) {pt.face}" if pt.pos else "no position"
            od = f"Ø{pt.diam:g}" if pt.diam is not None else "Ø?"
            tag = "" if s == "ok" else f"  — {_pstat.get(s, '⚠ ' + s)}"
            located_detail.append(f"    – {comp}:{pt.name} ({pt.kind}) {xyz} {od} → {pt.mates}{tag}")
    for c in passive:
        located_detail.append(f"✓ {c.name}: no connectors (passive body)")
    unlocated = total - len(pta) - len(passive)
    located_detail.append(f"{unlocated} components: no connector positions defined yet")
    goal("located", "Connectors located on the component — position + bore Ø (tubes + wires)", located_pct == 100,
         f"{located_pct}% ({len(located_comps) + len(passive)}/{total})", "100%", located_detail, active=False)

    # shaped — FOCUS: real geometry, not a placeholder box/cylinder. The registry declares it and
    # the geometry has to agree: a bare box or cylinder is a placeholder whatever the entry says,
    # so a component counts only when it is declared real AND measures as authored geometry.
    shapes = shape_audit(solids)
    def _prim(name):
        return shapes[name][2] if name in shapes else None
    real = [c for c in COMPONENTS if c.is_real and _prim(c.name) is False]
    mismatched = [c for c in COMPONENTS if _prim(c.name) is not None and _prim(c.name) == c.is_real]
    shaped = _pct(len(real), total)
    shaped_detail = [f"{c.name}: still a {c.kind} — {c.note}" for c in COMPONENTS if not c.is_real]
    shaped_detail += [
        f"{c.name}: declared {c.kind} but the geometry is "
        f"{'a bare primitive' if c.is_real else 'authored'} — ⚠ registry disagrees with the shape"
        for c in mismatched
    ]
    # How much of each component's boxes is material — the components a single box describes
    # worst are the ones whose box must not be read as their shape.
    loose = sorted(((shapes[c.name][1], c.name) for c in COMPONENTS if c.name in shapes))[:6]
    shaped_detail += [f"{n}: {len(shapes[n][0])} "
                      f"{'box holds' if len(shapes[n][0]) == 1 else 'boxes hold'} "
                      f"{f * 100:.0f}% material" for f, n in loose]
    goal("shaped", "Components modeled as real geometry (not a placeholder box)",
         shaped == 100 and not mismatched,
         f"{shaped}% ({len(real)}/{total})", "100%", shaped_detail, active=False)

    # routed — DEFERRED: every fluid + water + refrigerant + electrical connection a real 3D path. Lives in
    # routed_check() so a cache-hit build can recompute just this (it reads _lines) without redoing
    # the component audits above.
    routed_ck, routed = routed_check(solids)
    checks.append(routed_ck)

    # held — DEFERRED: a printed holder that fastens each component to the enclosure.
    held_done = [c for c in COMPONENTS if c.is_held]
    held = _pct(len(held_done), total)
    goal("held", "Components in a printed holder fastened to the enclosure", held == 100,
         f"{held}% ({len(held_done)}/{total})", "100%",
         [f"{len(held_done)} held ({', '.join(f'{c.name} by {c.held}' for c in held_done) or 'none'}); "
          f"{total - len(held_done)} loose internal parts unheld"],
         active=False)

    # mounted — FOCUS: the feature that fastens each component is printed into another placed
    # part. Every row absent from MOUNTED_BY is a joint still to design, which is what the
    # remainder counts; the rollup names which part carries what, so a reader sees where the
    # fastening already concentrates.
    ma = mount_audit(solids, pieces)
    mount_rows = {name: (carrier, holds, cks) for name, carrier, holds, cks in ma}
    mounted_done = [c for c in COMPONENTS if mount_rows.get(c.name, (None, False))[1]]
    adrift = [c for c in COMPONENTS
              if c.name in mount_rows and not mount_rows[c.name][1]]
    loose = [c for c in COMPONENTS if c.name not in mount_rows]
    mounted = _pct(len(mounted_done), total)
    carriers: dict[str, list[str]] = {}
    for c in mounted_done:
        carriers.setdefault(mount_rows[c.name][0], []).append(c.name)
    mounted_detail = [f"{by} carries {len(ns)}: {', '.join(sorted(ns))}"
                      for by, ns in sorted(carriers.items())]
    mounted_detail += [
        f"✗ {c.name}: named to {mount_rows[c.name][0]}, "
        + "; ".join(f"{lbl} {v:.2f}" + ("" if ok else f" (>{mx:g})") if v != float("inf")
                    else lbl for lbl, v, mx, ok in mount_rows[c.name][2])
        for c in sorted(adrift, key=lambda c: c.name)]
    mounted_detail.append(
        f"{len(loose)} with nothing fastening them — a body resting on another is not mounted, "
        f"and neither is one captured by a pocket or stuck down. One row each, below.")
    # One row per open joint, carrying what holds that body today. The distance from there to a
    # feature printed into another part is the joint to design.
    mounted_detail += [
        f"{c.name}: nothing fastens it — "
        + (f"held by {c.held}, which is not a printed-in feature" if c.is_held
           else "nothing holds it at all")
        for c in sorted(loose, key=lambda c: (c.is_held, c.name))]
    goal("mounted", "The feature that fastens each component is printed into another part",
         mounted == 100, f"{mounted}% ({len(mounted_done)}/{total})", "100%",
         mounted_detail, active=True)

    # The fastening record as structured rows, one per component — what `bends` is to the other
    # focus axis. Uncapped; the check.detail strings above are its capped human summary.
    mounts_table = [
        {"component": c.name, "by": MOUNTED_BY.get(c.name), "held": c.held, "kind": c.kind,
         "joint": ("holds" if mount_rows.get(c.name, (None, False))[1]
                   else "adrift" if c.name in mount_rows else None),
         "checks": [{"label": lbl, "value": None if v == float("inf") else round(v, 3),
                     "bound": mx, "ok": ok}
                    for lbl, v, mx, ok in mount_rows.get(c.name, (None, None, []))[2]]}
        for c in sorted(COMPONENTS, key=lambda c: (c.name in MOUNTED_BY, c.name))
    ]

    # The full connector inventory as structured rows — the audit-readable port table. Every
    # declared port, with its world coordinate and bore Ø, so the audit reads them directly
    # (the check.detail strings are a capped human summary; this is the complete record).
    ports_table = [
        {"component": comp, "name": pt.name, "kind": pt.kind,
         "pos": [round(v, 3) for v in pt.pos] if pt.pos else None, "face": pt.face,
         "diam": pt.diam, "mates": pt.mates, "status": s, "note": pt.note}
        for comp, _ok, prows in pta for pt, s in prows
    ]

    # The boxes each component really occupies, one row per component — the shape record behind
    # the shaped axis, in the same uncapped form as the port table.
    shapes_table = [
        {"component": n,
         "boxes": [[round(b.xmin, 3), round(b.ymin, 3), round(b.zmin, 3),
                    round(b.xmax, 3), round(b.ymax, 3), round(b.zmax, 3)] for b in boxes],
         "fill": round(fill, 4), "primitive": prim,
         "declared": reg[n].kind if n in reg else None}
        for n, (boxes, fill, prim) in sorted(shapes.items())
    ]

    # The pose table — every placed body with its provenance, settled ones carrying their
    # statement. Sorted settled first, so the short list a limit may be priced against reads
    # ahead of the long one that is still the work.
    poses_table = [
        {"name": n, "pose": pose(n), "settled": SETTLED.get(n)}
        for n in sorted(solids, key=lambda n: (pose(n) != "settled", n))
    ]

    # A row nobody asked for is reported stood down rather than left off the card, so a
    # partial card still names everything the full one does and none of it reads as held.
    if CARD_ONLY:
        checks = [c if c.id in CARD_ONLY else _stood_down(c.id, c.label, c.kind)
                  for c in checks]
    gates_pass = all(c.status == "pass" for c in checks if c.kind == "gate")
    return Scorecard(checks, gates_pass, placed_pct, located_pct, shaped, routed, held, mounted,
                     ports_table, shapes_table, bend_rows, mounts_table, poses_table)


def scorecard_dict(sc: Scorecard) -> dict:
    """The verdict as a JSON-serializable dict — the web sidecar written next to
    enclosure-assembly.step (enclosure-assembly.scorecard.json). This is the SAME `sc`
    the terminal prints, so the build and the viewer read one verdict, not two. Shape
    pinned by web/contracts/scorecard-sidecar.js and its conformance test."""
    return {
        "gatesPass": sc.gates_pass,
        "placed": sc.placed,
        "located": sc.located,
        "shaped": sc.shaped,
        "routed": sc.routed,
        "held": sc.held,
        "mounted": sc.mounted,
        "checks": [
            {"id": c.id, "label": c.label, "kind": c.kind, "status": c.status,
             "value": c.value, "target": c.target, "detail": list(c.detail), "active": c.active}
            for c in sc.checks
        ],
        "ports": list(sc.ports),
        "shapes": list(sc.shapes),
        "bends": list(sc.bends),
        "mounts": list(sc.mounts),
        "poses": list(sc.poses),
    }


def format_scorecard(sc: Scorecard) -> str:
    """Render the verdict as a terminal block. The two FOCUS axes come first, with their rows;
    then the gates (green pass / red fail) and the goals, the deferred ones gray and down to
    their figure. Color is emitted only to a TTY — piped/captured output stays plain."""
    tty = sys.stdout.isatty()
    GREEN, YELLOW, RED, GRAY = "32", "33", "31", "90"

    def col(s, code):
        return f"\033[{code}m{s}\033[0m" if tty else s

    mark = {"pass": "✓", "fail": "✗", "warn": "•", "skip": "·"}
    gates = [c for c in sc.checks if c.kind == "gate"]
    goals = {c.id: c for c in sc.checks if c.kind == "goal"}
    by_id = {c.id: c for c in sc.checks}
    passed = sum(1 for c in gates if c.status == "pass")
    w = max(len(c.label) for c in sc.checks)
    rows = []

    rows.append("── enclosure scorecard " + "─" * 30)

    # FOCUS, ahead of the blocks and carrying its own rows: the two axes the work is on.
    # `bend-radius` is a gate and `mounted` is a goal, so no existing block carries both, and a
    # figure read after ten others is not a focus. Their rows print here; the blocks below carry
    # each one's line alone.
    bend = by_id.get("bend-radius")
    bend_met = bend is not None and bend.status == "pass"
    focus_met = bend_met and sc.mounted == 100
    rows.append("FOCUS  "
                + col(f"bend-radius {bend.value if bend else '—'}", GREEN if bend_met else RED)
                + "   ·   "
                + col(f"mounted {sc.mounted}%", GREEN if sc.mounted == 100 else YELLOW)
                + (col("   ✓ FOCUS MET", GREEN) if focus_met else ""))
    for fid in FOCUS_IDS:
        c = by_id.get(fid)
        if c is None:
            continue
        code = GRAY if c.status == "skip" else (
            GREEN if c.status == "pass" else (RED if c.kind == "gate" else YELLOW))
        rows.append(f"  {col(mark[c.status], code)} {col(c.label.ljust(w), code)}  {c.value}  (want {c.target})")
        for d in c.detail:
            rows.append(f"      – {d}")

    # Gates. The focus gate keeps its line among the ten; its rows are above.
    hdr = f"GATES (printable + assembleable)   {passed}/{len(gates)} pass"
    rows.append(hdr if sc.gates_pass else hdr + "   " + col("✗ NOT BUILD-READY", RED))
    for c in gates:
        code = GRAY if c.status == "skip" else (GREEN if c.status == "pass" else RED)
        focus = c.id in FOCUS_IDS
        note = col("  ↑ rows under FOCUS", code) if focus else ""
        rows.append(f"  {col(mark[c.status], code)} {c.label.ljust(w)}  {c.value}  (want {c.target}){note}")
        if focus:
            continue
        for d in c.detail:
            rows.append(f"      – {d}")

    # Goals — mounted is the live axis, the rest gray behind it. A deferred axis prints its
    # figure and the count of rows `scorecard.json` holds for it.
    done = (sc.gates_pass and focus_met and sc.placed == 100 and sc.located == 100
            and sc.shaped == 100 and sc.routed == 100 and sc.held == 100)
    tail = col("  ✓ DONE", GREEN) if done else ""
    rows.append("GOAL   " + col(f"focus: mounted {sc.mounted}%", GREEN if sc.mounted == 100 else YELLOW)
                + "   " + col(f"deferred: placed {sc.placed}% · located {sc.located}% · "
                              f"shaped {sc.shaped}% · routed {sc.routed}% · held {sc.held}%", GRAY) + tail)

    ordered = sorted(goals, key=lambda g: (g not in FOCUS_IDS, list(goals).index(g)))
    for gid in ordered:
        c = goals[gid]
        if gid in FOCUS_IDS:
            code = GRAY if c.status == "skip" else (GREEN if c.status == "pass" else YELLOW)
            rows.append(f"  {col(mark[c.status], code)} {col(c.label.ljust(w), code)}  {c.value}  "
                        f"(want {c.target}){col('  ↑ rows under FOCUS', code)}")
        else:
            n = len(c.detail)
            rows.append(col(f"  · {c.label.ljust(w)}  {c.value}  — deferred; {n} "
                            f"row{'' if n == 1 else 's'} in the sidecar", GRAY))

    # POSE — which placements a limit may be priced against, and which are still the work.
    # Not a gate and not a goal: 100% settled is not a finish line, and a body's pose being
    # provisional is a true reading of this pack rather than a shortfall in it.
    if sc.poses:
        settled = [p["name"] for p in sc.poses if p["pose"] == "settled"]
        rows.append(f"POSE   settled {len(settled)}/{len(sc.poses)}   "
                    + col(", ".join(settled) + " (+ the enclosure walls)", GREEN))
        rows.append(col(f"       every other pose is provisional, and so is every route — "
                        f"`scorecard.SETTLED` states what each settled one covers", GRAY))

    rows.append("─" * 53)
    return "\n".join(rows)
