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
copper). The enclosure has FIVE axes, one per thing every component owes — and today
only the first three are the focus (the other two render, dimmed, but are not yet worked):

    placed  — FOCUS. Placement criteria are DEFINED in code (expected face-to-datum
              measurements) and currently HELD. "Foam is against the back-bottom",
              with "against" pinned to numbers the scorecard measures.
    located — FOCUS. Every connector (tube + wire) has a POSITION on the component — a
              point on the body the scorecard confirms is on-surface. A connection has no
              path until both its ends are located, so this precedes routed.
    shaped  — FOCUS. Real geometry, not a placeholder box/cylinder.
    routed  — deferred. Every connection (fluid + water + refrigerant + electrical) a real 3D
              path (bend radius, length, clearance), not endpoints + an external graph.
    held    — deferred. A printed holder that fastens the component to the enclosure (a
              few bosses + screws, or a tray-with-bosses that itself fastens) — not a
              free solid resting in a collision-checked void.

placed + located + shaped are driven to 100% first; routed + held wait behind them (gray).
The score is by AUTHORSHIP, not by "it doesn't collide": a bounding box that happens not
to overlap is the enclosure's version of the autorouter's accidentally-clean net —
crediting it would count the box-thinking this effort exists to remove as progress. So
`shaped`/`held` are read from the declared COMPONENTS registry, `placed` from measured
face-to-datum rules and `located` from measured port positions (both authored per component),
and `routed` from the fluid + refrigerant + wiring topologies (a connection counts only once a
real path exists). Prose for the why — and the lessons — is in requirements.md.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _boxes  # noqa: E402  — optimal bounding boxes, memoized once per placed solid
import _contents as contents  # noqa: E402  — the manifold ports derive from the pack's own placement

# Minimum solid-to-solid distance. cadquery 2 binds OpenCascade as OCP; the guarded import
# leaves `_HAVE_EXACT` false when it is absent, and `_solid_gap` raises.
try:
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound
    from OCP.gp import gp_Pnt
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
    # Cold core + floor block
    _c("foam-assembly",     "real",        True,  "none", "cold core; seats on floor/against walls, support-ring TBD (enclosure-mechanical Open #6)"),
    _c("compressor-shroud", "real",        True,  "none", "floor-boss capture TBD (enclosure-mechanical Open #1)"),
    _c("condenser+fan",     "placeholder", True,  "none", "harvested donor block; side-wall bosses TBD (enclosure-mechanical Open #1)"),
    _c("mq6-sensor",        "real",        True,  "none", "MQ-6 module STEP (PCB + sensor can + header); floor gas sensor, no mount"),
    # Water deck
    _c("seaflo-pump",       "real",        True,  "none", "SEAFLO 22-series 12 V 1.3 GPM diaphragm pump (reference/seaflo-22-pump); the deck's floor plan. Lies motor-axis along X, head at −X; its two 3/8\" barbs are molded into the head casting and leave its ±Y side faces — the suction faces north (+Y) to V-K, the discharge south (−Y) to the cold-core water-in. Its feet carry the widest 98 mm; the head end is 44 mm narrower, and that taper is what opens the band V-K lies in. Isolation mounts to the foam cap TBD"),
    _c("asse1022-assembly", "real",        True,  "none","Multiplex 19-0897 ASSE 1022 backflow preventer + PP010822E, GAGIRA coupling, flare38-14ptc (3/8\" flare → 1/4\" PTC) and the clear-PVC vent stub as one chain (reference/asse1022-assembly); lies along +X in the service bay's aft strip behind the pump, 1/4\" PTC inlet west on its pigtail off the rear-panel water bulkhead, 1/4\" PTC outlet east onto the line to the split, vent in its native pose weeping down its own column onto the pan's ground on the foam-cap top, holder TBD"),
    _c("water-split",       "real",        True,  "none","JG PP0208E 1/4\" union tee (reference/water-split); tube-hung in the east pocket, its three collets in the suction's own Z plane. The run carries the ASSE feed straight down the pocket — in at +Y, on at −Y to the flow regulator — and the branch turns V-K's share west. No tray, no holder"),
    _c("vk-fill-valve",     "real",        True,  "none","Beduan 12 V NC solenoid (reference/beduan-solenoid) — V-K, the water-supply fill/shutoff valve. Downstream of the ASSE 1022, between the split and the SeaFlo suction. Yawed a quarter turn so it lies along X in the band the pump's narrow head end opens: inlet east at the split's branch, outlet west at the suction, all three collets in one plane. Stands on a short cradle off the foam cap; cradle TBD"),
    _c("flow-regulator",    "real",        True,  "none","neoFit ABCVU44 1/4\" needle flow control (reference/neofit-flow-control) — the flavor tap's regulator, throttling the manifold's feed to its low working pressure. Tube-hung inline on the split's flavor run, further down the same pocket, flow running south; its needle stem stands up where a screwdriver reaches it over the deck. No tray, no holder"),
    # Valve manifold
    _c("source-select-assembly", "real",   True,  "none", "Tray 1 — printed tray + 4 Beduan NC solenoids + 2 PP2308E Y-dividers + 4 outlet elbows (valve-manifold/source-select-tray); floors the stack, plate down and valves up, holder TBD"),
    _c("bag-circuit-assembly",   "real",   True,  "none", "Tray 2 — printed dog-bone tray + 4 Beduan NC solenoids + 2 PP0208E Tees + 2 west outlet elbows (valve-manifold/bag-circuit-tray); rides INVERTED on the source tray's stacking walls, east ports bare, holder TBD"),
    _c("nozzle-gate-assembly",   "real",   True,  "none", "Tray 3 — printed tray + 2 Beduan NC solenoids, every port bare (valve-manifold/nozzle-gate-tray); rides INVERTED on the same source walls in the pocket east of the bag assembly, holder TBD"),
    # Pump row
    _c("pump-a",            "real",        True,  "none", "Kamoer KPHM400 peristaltic + 2 PP0308E outlet elbows (reference/kamoer-kphm400 pump-assembly); lies depth-along-X ahead of the tray stack, motor west, elbows on the +Z face, holder TBD"),
    _c("pump-b",            "real",        True,  "none", "Kamoer KPHM400 peristaltic + 2 PP0308E outlet elbows (reference/kamoer-kphm400 pump-assembly); same lying pose one slot east, head east under the funnel's high floor, holder TBD"),
    # In-line fittings — tube-hung PTC junctions, carried by their lines (no tray, no holder)
    _c("tee-y-c", "real", True, "none", "JG PP0208E union tee (fluid topology Y-C) hanging in the junction column: run vertical — V-C-O's drop into the run-up collet, the bag V-E-O return onto the run-down — branch rolled forward (−Y) off the pump row; its leg climbs behind pump A's barrel and drapes east over the pumps to pump B (segment 11)"),
    _c("tee-y-f", "real", True, "none", "JG PP0208E union tee (Y-F), the channel-B twin one port row aft: V-D-O above, V-H-O return below, branch rolled forward (−Y), canted east to thread past tee-y-c; its leg climbs the west end of the column then runs east above the source tray to pump A's inlet (segment 21)"),
    _c("y-d", "real", True, "none", "JG PP2308E two-way divider (reference/y-divider) — the Y connector for pump-discharge junction A (flavor A → pump B), seated in the open air over the pump row, tilted to face its elbows: its two outlets take the bag-V-F elbow (Y-D-2, segment 13) and the nozzle-V-G elbow (Y-D-3, segment 17), stem toward pump B (Y-D-1, segment 12)"),
    _c("y-g", "real", True, "none", "JG PP2308E two-way divider (reference/y-divider) — the Y connector for pump-discharge junction B (flavor B → pump A), over the pump row one slot east, tilted to face its elbows: its two outlets take the bag-V-I elbow (Y-G-2, segment 23) and the nozzle-V-J elbow (Y-G-3, segment 27), stem toward pump A (Y-G-1, segment 22)"),
    _c("elbow-bag-y-d", "real", True, "none", "JG PP0308E 90° elbow turning bag V-F-I (east) off the stack, rolled to aim its free leg at the Y-D divider's upper outlet (segment 13)"),
    _c("elbow-bag-y-g", "real", True, "none", "JG PP0308E 90° elbow turning bag V-I-I (east) off the stack, rolled to aim its free leg at the Y-G divider's upper outlet (segment 23)"),
    _c("elbow-y-d", "real", True, "none", "JG PP0308E 90° elbow turning nozzle-gate V-J-I (flipped, west) off the stack, rolled to aim its free leg at the Y-G divider's lower outlet (segment 27)"),
    _c("elbow-y-g", "real", True, "none", "JG PP0308E 90° elbow turning nozzle-gate V-G-I (flipped, west) off the stack, rolled to aim its free leg at the Y-D divider's lower outlet (segment 17)"),
    _c("elbow-noz-a", "real", True, "none", "JG PP0308E 90° elbow turning nozzle-gate V-G-O (east) up out of the +X wall pocket, free leg +Z onto its run aft to bulkhead-flavor-a (segment 18)"),
    _c("elbow-noz-b", "real", True, "none", "JG PP0308E 90° elbow turning nozzle-gate V-J-O (east) up out of the +X wall pocket, free leg +Z onto its run aft to bulkhead-flavor-b (segment 28)"),
    # Electronics shelf
    # Rear-panel through-wall bodies — captured by their own flange/nut on the printed wall
    _c("bulkhead-flavor-a", "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut"),
    _c("bulkhead-flavor-b", "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut"),
    _c("bulkhead-carb",     "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut"),
    _c("bulkhead-water",    "real",        True,  "wall-capture", "JG bulkhead: rear-wall hole + its own nut"),
    _c("c14-inlet",         "real",        True,  "wall-capture", "C14 mains inlet: rear-wall cutout + its own flange"),
    _c("co2-inlet",         "real",        True,  "wall-capture", "DERPIPE PTC STEP (collet + wrench hex + NPT shank): front-wall hole + its own 1/4\" NPT thread"),
    # Front-panel / opening
    _c("display",           "real",        True,  "shell-facet", "Waveshare 4.3B: 45° facet housing in the front-top (bezel counterbore + PCB through-hole)"),
    _c("hopper-funnel",     "real",        True,  "none", "removable silicone basin; rests on the top-wall rim ledge, attach mode TBD (enclosure-mechanical Open #3)"),
]

# Unordered part pairs allowed to touch by design — a part resting on another's top, or
# a body reaching into a pan. PROVISIONAL: seeded from the pack's deliberate stacks; the
# clearance gate excludes these, so a sub-floor gap between any OTHER pair is what fails.
# Ratifying this set (and the floor above) is the first directed step.
TOUCHING_OK = {
    frozenset(p) for p in [
        ("foam-assembly", "seaflo-pump"),       # the pump's base flat on the foam-cap top
        # The valve-manifold stack: the source-select tray's floor rests on the
        # bag-circuit tray's column wall tops, one tray pitch apart by design.
        ("source-select-assembly", "bag-circuit-assembly"),
    ]
}


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
    ("water-3", "water-split to-vk (PP0208E 1/4\" tee)", "vk-fill-valve inlet (Beduan 1/4\" QC)"),
    ("water-4", "vk-fill-valve outlet (Beduan 1/4\" QC)", "seaflo-pump suction (1/4\" → 3/8\" barb adapter)"),
    ("water-5", "seaflo-pump discharge (MAACFLOW → GASHER check)", "foam-assembly water-in"),
]


def load_connections() -> list[Connection]:
    """Every connection the box must route: the fluid tube segments (fluid-topology.md,
    `| N | From | To |`), the electrical runs (ac-wiring-schedule.md, `| AC/DC/SIG/LV-N |
    From | To |`), the sealed refrigerant loop (REFRIGERANT_SEGMENTS) and the tap-water
    path (WATER_SEGMENTS). A connection counts as routed only once a real 3D path is
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
    # Routed state comes from the paths _lines.py builds. Deferred import: _lines reads PORTS
    # back out of this module.
    import _lines
    done = _lines.routed_ids()
    for c in conns:
        c.routed = c.id in done
        c.blocked = _lines.BLOCKED.get(c.id, "")
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
PLACEMENT_RULES = {
    # "Foam is against the back-bottom, full width" — the canonical example. It
    # sits flat on the floor and flush against the SEAMS rather than the walls:
    # the ±X walls stand one boss chain (`_contents.SIDE_RIB_INSET`) off it so the
    # corner posts and boss chains have their full section, and the back wall one
    # wall (`enclosure.rear_seam_clear`) off it so the rear Z-seam lip's inner
    # face is what it seats against. Those standoffs are the placement, so the
    # tolerances carry them.
    "foam-assembly":     [("y+", 4.0), ("x-", 15.0), ("x+", 15.0), ("z-", 1.0)],
    # "Compressor is front-left on the floor" — one corner-rib chain inboard of the
    # cold core's side face, which the wall stands a further chain outboard of.
    # Like the foam it seats on a SEAM, not a wall: the front wall stands one wall
    # (`enclosure.front_seam_clear`) off it so the front column's Z-seam lip keeps
    # a full-width front segment, and that lip's inner face is what it seats on.
    "compressor-shroud": [("y-", 4.0), ("z-", 4.0), ("x-", 29.0)],
    # "Condenser is front-right on the floor" — the same, off the right.
    "condenser+fan":     [("y-", 4.0), ("z-", 4.0), ("x+", 29.0)],
    # "The assembly stands a bag-line corridor ahead of the cold core": the open
    # Y between its tall walls' back faces and the foam's front face is the lane
    # both bag lines fall down to the reservoir ports, and the only one that
    # reaches reservoir-A behind the condenser. Measured on the real solids, so
    # closing it from either side fails here rather than in the routing.
    "source-select-assembly": [("clear", "foam-assembly", contents.BAG_FALL_CORRIDOR)],
    # "The funnel rides the top wall" — brim top one brim thickness + one wall above the
    # interior ceiling. Its shallow-floored basin runs the top frame's full depth and
    # its centred drain hangs high over the pump row — the pumps' own `clear` keep-out
    # holds the segment-4 drop corridor open beneath it.
    "hopper-funnel":     [("z+", 6.1)],
    # "The source-select tray carries the bag tray": stacked one tray pitch
    # above, this tray's wall tops resting on the source tray's (a declared
    # contact — the `near` holds at zero), while the floor stratum below the
    # stack stays one stack gap open (the compressor and tipped condenser tops
    # are the deferred water deck's ground).
    "bag-circuit-assembly": [("near", "source-select-assembly", 1.0),
                             ("clear", "compressor-shroud", 2.5),
                             ("clear", "condenser+fan", 2.5)],
    # "The nozzle-gate tray rides the pocket east of the bag assembly, on the
    # stack's second-story plane": its hanging wall tops reach the source
    # tray's wall-top plane, but the source's east wall slabs (which follow
    # its aimed valves) stop just outboard of them, so the tray floats a few
    # millimetres off the source assembly — held open until its holder. Its
    # bare east (V-G/V-J) ports stand INSET off the cold core's +X face (by
    # GATE_WALL_INSET, in _contents.py), opening the pocket their outlet elbows
    # will turn aft into. The +X wall then stands a further corner-rib chain
    # outboard of that face, so the measured gap to the wall carries both.
    "nozzle-gate-assembly": [("near", "source-select-assembly", 4.0),
                             ("x+", 30.0)],
    # "P-A stands one stack gap ahead of the stack, under the funnel's
    # drop": its aft face a stack gap off the bag tray's front columns — the
    # stack's flat front at the row's height, which the bag branches rise
    # clear of, rolled up into their fall — and the segment-4 drop corridor
    # under the funnel's high centred drain held open over it, a keep-out
    # the gravity drain physically depends on.
    "pump-a": [("near", "bag-circuit-assembly", 10.0), ("clear", "hopper-funnel", 4.0)],
    # "P-B rides the row one nose gap east of P-A, its elbows ahead of the
    # east bank": the row tie to its neighbor, and a keep-out holding its
    # aft elbow clear of the source-select east walls it threads past.
    "pump-b": [("near", "pump-a", 6.5), ("clear", "source-select-assembly", 2.5)],
    # The tees hang in the junction column between the source and bag banks. The
    # column leans off vertical (each elbow rolled to aim at the other, _contents
    # `JUNCTION_ROLL`) and tee-y-c slides up its run toward the bag (`JUNCTION_LIFT`,
    # raising its branch so the suction stem leaves gently), so a tee stands well
    # off the source bank — the `near` gap allows for that.
    "tee-y-c": [("near", "source-select-assembly", 15.0)],
    "tee-y-f": [("near", "source-select-assembly", 15.0)],
    # "The ASSE 1022 chain lies in the service bay's aft strip, one pigtail off the
    # water bulkhead, vent aimed forward over the pan's ground." Five measurements pin
    # it. `near bulkhead-water` holds the inlet at the bulkhead it takes its feed from —
    # that stance is the placement. `fall` is the drip, and the rule the pose exists for:
    # the vent tip's own column, dropped straight down, lands on the cap, where the pan
    # and its moisture plate sit. It reads the column, not the body — the two part company
    # in this strip, where the body stands 28 mm off the shelf and the column 4. `clear
    # power-tray` holds
    # open the lane between the shelf's back edge and this body, which the C14's cordage
    # crosses going forward to the AC hub. `x-` reads the outlet end's stance off the −X
    # wall — the room the 1/4" line to the split leaves in, bounded east by the
    # nozzle-outlet runs crossing the strip.
    "asse1022-assembly": [("near", "bulkhead-water", 20.0),
                          ("fall", "vent-tip", "foam-assembly", 60.0),
                          ("clear", "power-tray", 8.0),
                          ("clear", "c14-inlet", 4.0),
                          ("x-", 80.0)],
    # V-K on its cradle, laid along X in the band the pump's head taper opens: its inlet takes the
    # split's branch (`near water-split` — the feed that anchors the pose), its outlet looks west
    # straight down the lane under the ASSE overhang to the suction. Lifted off the cap on its
    # cradle (`clear foam-assembly`), clear of the pump body (`clear seaflo-pump`), and standing
    # off the backflow preventer it sits downstream of (`clear asse1022-assembly`).
    "vk-fill-valve": [("near", "water-split", 12.0),
                      ("clear", "seaflo-pump", 4.0),
                      ("clear", "asse1022-assembly", 3.0),
                      ("clear", "foam-assembly", 5.0)],
    # The flow regulator hangs on the flavor run below the split (`near water-split` — the tube
    # that carries it), out in the pocket clear of everything else.
    "flow-regulator": [("near", "water-split", 24.0),
                       ("clear", "foam-assembly", 5.0)],
}


def placement_audit(solids: dict, inner: tuple) -> list[tuple[str, bool, list]]:
    """For each component that has placement rules, measure every rule and return
    (name, all_hold, [(label, gap, bound_mm, ok)]) — label is the face for a face-to-datum
    rule, "near <other>" / "clear <other>" for the part-to-part forms. Components without
    rules are not returned — they are simply not-yet-placed."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    datum = {"x-": ix0, "x+": ix1, "y-": iy0, "y+": iy1, "z-": iz0, "z+": iz1}
    out = []
    for name, rules in PLACEMENT_RULES.items():
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
                p = next(q for q in PORTS if q.component == name and q.name == port)
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


# The cold core's front face in world. Its placement puts the shell's local Y origin there,
# so every foam port is written as this face, or a reach aft off it, and they ride the core.
_FOAM_FACE = contents.FRONT_DEPTH
# The rear panel's OUTER face — the one `panel_bodies()` seats the bulkhead unions and the C14
# on, standing one wall behind the pack's own rear standoff. The through-wall ports below are
# written as reaches off it, so a change in the pack's depth carries them.
_PANEL_OUT = contents._port_frame()[2] + contents.WALL
_JG_OUT, _JG_IN = 6.5, 27.8   # JG bulkhead union: tube-face reach outboard / inboard of the panel
_C14_IN = 30.0                # C14 inlet: spade-terminal face inboard of the panel
# Each rear-panel station as (x, z), read off the hole the wall is cut for, so the hole,
# the body seated in it and the ports below are the one reading.
_BACK_A     = contents.back_port_station("bulkhead-flavor-a")
_BACK_B     = contents.back_port_station("bulkhead-flavor-b")
_BACK_CARB  = contents.back_port_station("bulkhead-carb")
_BACK_WATER = contents.back_port_station("bulkhead-water")
_BACK_C14   = contents.back_port_station("c14-inlet")

PORTS = [
    # foam-assembly — 8 tube penetrations (foam-shell README §Penetrations) + 2 reed-cable exits
    # on the −Y front wall. All on −Y except the CO2 inlet, which drops through the +Z foam-cap
    # top, at its own station aft of the face. Ø: the beverage/flavor lines run the foam shell's
    # Ø6.5 port-holes (_cold_core_interface.port_hole_radius 3.25) sized for 1/4" tube; the
    # water-in takes the SeaFlo's 3/8" discharge; the copper legs are 1/4" ACR = 6.35.
    _p("carb-water-out", "foam-assembly", "fluid",       (141.5, _FOAM_FACE, 46.5),  "y-", 6.35,  "dispense faucet (carb-water riser to the rear umbilical)", "1/4\" tank NPT elbow line"),
    _p("reservoir-A",    "foam-assembly", "fluid",       (238.5, _FOAM_FACE, 35.5),  "y-", 6.35,  "reservoir A ↔ peristaltic pump A (bag circuit)", "1/4\" LLDPE flavor line, Ø6.5 foam port"),
    _p("reservoir-B",    "foam-assembly", "fluid",       (44.5,  _FOAM_FACE, 35.5),  "y-", 6.35,  "reservoir B ↔ peristaltic pump B (bag circuit)", "1/4\" LLDPE flavor line, Ø6.5 foam port"),
    _p("co2-in",         "foam-assembly", "fluid",       (141.5, _FOAM_FACE + 17.8, 262.9), "z+", 6.35,  "CO2 chain (WR1110 → foam-cap top entry)", "1/4\" PTC CO2 line; seats in the Ø16 foam-cap bore"),
    _p("evap-inlet",     "foam-assembly", "refrigerant", (141.5, _FOAM_FACE, 72.0),  "y-", 6.35,  "condenser+fan outlet (liquid line via drier + cap tube)", "1/4\" ACR copper"),
    _p("evap-outlet",    "foam-assembly", "refrigerant", (141.5, _FOAM_FACE, 191.0), "y-", 6.35,  "compressor-shroud suction", "1/4\" ACR copper"),
    _p("water-in",       "foam-assembly", "fluid",       (141.5, _FOAM_FACE, 223.0), "y-", 9.525, "gasher-water out (SeaFlo outlet check → carbonator water inlet)", "3/8\" hose barb (SeaFlo 22-series port)"),
    _p("prv-vent",       "foam-assembly", "fluid",       (141.5, _FOAM_FACE, 231.0), "y-", 6.35,  "appliance interior (relief-event discharge only)", "1/4\" relief discharge"),
    _p("reed-cable-A",   "foam-assembly", "electrical",  (254.5, _FOAM_FACE, 35.5),  "y-", 6.5,   "J6 REEDS A — reservoir A level reeds (SIG-10)", "reed cable through the Ø6.5 pass-through, 16 mm outboard of reservoir-A (_port_cuts.py)"),
    _p("reed-cable-B",   "foam-assembly", "electrical",  (28.5,  _FOAM_FACE, 35.5),  "y-", 6.5,   "J7 REEDS B — reservoir B level reeds (SIG-11)", "reed cable through the Ø6.5 pass-through, 16 mm outboard of reservoir-B (_port_cuts.py)"),
    # compressor-shroud — compressor_shroud.py local hole centers carried through _contents'
    # _rot((0,0,1),−90) + _at(14,0,3). Both copper stubs share the one face → world +Y (toward
    # the foam/cold core they mate to); the AC gland + earth bond ride the +X face (into the
    # inter-part channel). suction/discharge assigned by world x per the physical loop. Copper is
    # 1/4" ACR; the AC gland Ø and earth-stud Ø are estimates pending the shroud teardown.
    _p("ac-mains",        "compressor-shroud", "electrical",  (192.0, 66.5, 78.0),  "x+", 10.0,  "Teyleten relay #1 / AC distribution (AC-4 switched-H + AC-5 N, 3-wire gland)", "gland bore ~Ø10 for 3-wire mains (estimate — confirm at shroud teardown)"),
    _p("earth-bond",      "compressor-shroud", "electrical",  (192.0, 31.5, 78.0),  "x+", 5.0,   "electronics-shelf ground bus (AC-6)", "M5 earth stud/ring (estimate — confirm at shroud teardown)"),
    _p("refrig-suction",  "compressor-shroud", "refrigerant", (59.25, 133.0, 78.0), "y+", 6.35,  "foam-assembly evaporator outlet", "1/4\" ACR copper"),
    _p("refrig-discharge","compressor-shroud", "refrigerant", (146.75, 133.0, 78.0),"y+", 6.35,  "condenser+fan inlet", "1/4\" ACR copper"),
    # condenser+fan — placeholder box harvested from the donor, tipped on its back (a −90°
    # turn about X: donor top → aft, donor front → up); ports are the 2026-07-17 step-viewer
    # picks carried through the tip. Both refrigerant ports on the −X face (toward the
    # compressor): inlet back-top, outlet front-bottom (drier + cap-tube hang off it). The
    # fan is on the opposite +X face; airflow runs −X → +X, unchanged by the tip. Copper is
    # 1/4" ACR; the fan pigtail Ø is an estimate.
    _p("refrig-inlet",  "condenser+fan", "refrigerant", (213.0, 172.5, 148.5), "x-", 6.35, "compressor-shroud discharge", "1/4\" ACR copper"),
    _p("refrig-outlet", "condenser+fan", "refrigerant", (213.0, 5.5, 8.5),     "x-", 6.35, "filter-drier → cap tube → foam-assembly evaporator inlet", "1/4\" ACR copper"),
    _p("fan-power",     "condenser+fan", "electrical",  (269.0, 89.0, 78.5),   "x+", 4.0,  "J2 MANIFOLD B FAN + COM (DC-8, 12 V)", "DC pigtail 2-wire (estimate); +X exhaust face (fan centered); airflow −X→+X"),
    # CO2 inlet (front panel) — the DERPIPE steps the customer's 5/16" PTC down to the 1/4"
    # NPT stub inboard. The chain it feeds (GASHER check → WR1110 → foam co2-in) is deferred
    # from the pack — its old front-left column is the source-select assembly's west bank.
    _p("tube-in",  "co2-inlet", "fluid", (46.0, -22.0, 234.0),  "y-", 7.94, "customer CO2 supply — 5/16\" push-to-connect (rear umbilical)", "5/16\" PTC collet, outboard"),
    _p("npt-out",  "co2-inlet", "fluid", (46.0, 5.0, 234.0),    "y+", 6.35, "CO2 chain (GASHER check → WR1110, deferred) → foam-assembly co2-in", "1/4\" NPT shank, inboard"),
    # Rear-panel through-wall bodies — each JG bulkhead union is a 1/4" tube port each side of the
    # rear wall (Y = tube-flow axis, +Y = outward to the rear umbilical, −Y = inward to the
    # subsystem it feeds). The C14 mains inlet carries one 3-wire harness inboard from the panel
    # cord entry. Each station is a reach off `_PANEL_OUT`, the face `panel_bodies()` seats them
    # on, so the ports ride the wall the box sizes itself to rather than a world Y of their own.
    _p("tube-out", "bulkhead-flavor-a", "fluid", (_BACK_A[0], _PANEL_OUT + _JG_OUT, _BACK_A[1]), "y+", 6.35, "customer flavor A line (rear umbilical)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-flavor-a", "fluid", (_BACK_A[0], _PANEL_OUT - _JG_IN, _BACK_A[1]), "y-", 6.35, "flavor A internal line (bag/pump circuit A)", "JG 1/4\" PTC, inward"),
    _p("tube-out", "bulkhead-flavor-b", "fluid", (_BACK_B[0], _PANEL_OUT + _JG_OUT, _BACK_B[1]), "y+", 6.35, "customer flavor B line (rear umbilical)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-flavor-b", "fluid", (_BACK_B[0], _PANEL_OUT - _JG_IN, _BACK_B[1]), "y-", 6.35, "flavor B internal line (bag/pump circuit B)", "JG 1/4\" PTC, inward"),
    _p("tube-out", "bulkhead-carb", "fluid", (_BACK_CARB[0], _PANEL_OUT + _JG_OUT, _BACK_CARB[1]), "y+", 6.35, "carbonated-water line (rear umbilical / faucet)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-carb", "fluid", (_BACK_CARB[0], _PANEL_OUT - _JG_IN, _BACK_CARB[1]), "y-", 6.35, "carb-water internal riser (DIGITEN → foam carb-water-out)", "JG 1/4\" PTC, inward"),
    _p("tube-out", "bulkhead-water", "fluid", (_BACK_WATER[0], _PANEL_OUT + _JG_OUT, _BACK_WATER[1]), "y+", 6.35, "house tap-water line (rear umbilical)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-water", "fluid", (_BACK_WATER[0], _PANEL_OUT - _JG_IN, _BACK_WATER[1]), "y-", 6.35, "asse1022-assembly tube-in (the backflow preventer's own chain) — segment water-1 (routed)", "JG 1/4\" PTC, inward"),
    _p("mains-in", "c14-inlet", "electrical", (_BACK_C14[0], _PANEL_OUT - _C14_IN, _BACK_C14[1] + 0.5), "y-", 8.0, "AC distribution — L/N/E to the electronics shelf", "C14 spade terminals; 3-wire mains harness inboard"),
    # Floor sensor — a single signal header (one cable penetration, not one per conductor).
    # MQ-6 header pins down (−Z) at the board floor — the 4-pin row runs along the
    # PCB's −X edge (x≈103), NOT the board centre, so the port sits on that edge.
    _p("header", "mq6-sensor", "electrical", (103.0, 144.0, 3.0), "z-", 8.0, "PCBA gas-sensor input — VCC/GND/DO/AO (SIG)", "4-pin 2.54 mm header at the PCB's −X edge, pins down"),
    # ASSE 1022 assembly — its three terminals, each read off the reference module's own
    # station and carried through the placement (contents.bfp_terminal). The chain's stack-up
    # sets where they land, so a length changed in any of its five parts moves them together.
    # The vent is not a connection: it terminates to atmosphere over the drip pan, and plumbing
    # it into anything would destroy the telltale it exists to be (internal-plumbing.md §2).
    _p("tube-in",  "asse1022-assembly", "fluid", *contents.bfp_terminal("tube-in"),  6.35,  "bulkhead-water tube-in — segment water-1 (routed)", "JG PP010822E 1/4\" PTC, facing west; water-1 is the pigtail off the rear-panel bulkhead"),
    _p("tube-out", "asse1022-assembly", "fluid", *contents.bfp_terminal("tube-out"), 6.35,  "water-split supply — segment water-2 (routed)", "flare38-14ptc 1/4\" PTC, facing east down the aft strip to the split"),
    _p("vent-tip", "asse1022-assembly", "fluid", *contents.bfp_terminal("vent-tip"), 6.35,  "atmosphere, dripping onto the drip pan + moisture plate (deferred) — never plumbed", "Sealproof 1/4\" ID clear-PVC stub, facing −Z over the foam-cap top; cut to length at the bench"),
    # V-K — the water-supply fill/shutoff solenoid, its two 1/4" QC collets on the flow axis,
    # each carried through the placement (contents.vk_terminal). Downstream of the ASSE, between
    # the split and the suction.
    _p("inlet",  "vk-fill-valve", "fluid", *contents.vk_terminal("inlet"),  6.35, "water-split to-vk — segment water-3 (routed)", "Beduan 1/4\" QC collet, facing east (+X) at the split's branch"),
    _p("outlet", "vk-fill-valve", "fluid", *contents.vk_terminal("outlet"), 6.35, "seaflo-pump suction — segment water-4 (routed)", "Beduan 1/4\" QC collet, facing west (+X reversed); looks straight down the lane under the ASSE overhang to the suction"),
    # The water split — a 1/4" tee: the run carries the ASSE feed through to the flavor tap,
    # the branch turns V-K's share west.
    _p("supply",    "water-split", "fluid", *contents.split_terminal("supply"),    6.35, "asse1022-assembly tube-out — segment water-2 (routed)", "PP0208E 1/4\" PTC run, facing north up the pocket at the line off the ASSE outlet"),
    _p("to-vk",     "water-split", "fluid", *contents.split_terminal("to-vk"),     6.35, "vk-fill-valve inlet — segment water-3 (routed)", "PP0208E 1/4\" PTC branch, facing west at V-K's inlet"),
    _p("to-flavor", "water-split", "fluid", *contents.split_terminal("to-flavor"), 6.35, "flow-regulator inlet — fluid segment 1 (routed)", "PP0208E 1/4\" PTC run, facing south down the pocket to the regulator"),
    # The flow regulator, inline on the flavor run below the split.
    _p("inlet",  "flow-regulator", "fluid", *contents.flowreg_terminal("inlet"),  6.35, "water-split to-flavor — fluid segment 1 (routed)", "neoFit 1/4\" PTC collet, facing north up the pocket at the split"),
    _p("outlet", "flow-regulator", "fluid", *contents.flowreg_terminal("outlet"), 6.35, "source-select-assembly V-A-I — fluid segment 2 (routed)", "neoFit 1/4\" PTC collet, facing south down the pocket to the manifold"),
    # The SeaFlo's two head barbs, on its ±Y side faces; the yaw turns the suction north, the
    # discharge south.
    _p("suction",  "seaflo-pump", "fluid", *contents.seaflo_terminal("suction"),   6.35,  "vk-fill-valve outlet — segment water-4 (routed)", "3/8\" hose barb on the head, facing north (+Y); a 1/4\"→3/8\" barb adapter takes the LLDPE, worm-gear clamp"),
    _p("discharge","seaflo-pump", "fluid", *contents.seaflo_terminal("discharge"), 9.525, "foam-assembly water-in via the MAACFLOW → GASHER check (deferred) — segment water-5", "3/8\" hose barb on the head, facing south (−Y); worm-gear clamp"),
    # Hopper funnel — the removable silicone basin's single drain: the spout-tube exit annulus,
    # feeding V-B by tube (segment 4). Defined in the funnel's own frame
    # (hopper_funnel.drain_local = (neck_dx, 0, −drop)) carried through the placement's
    # FUNNEL_ROT + FUNNEL_CX/CY (brim on the box top), so it rides the part. The spout sits
    # on the collar centre and the shallow full-frame floor keeps it high: the drain hangs
    # over the pump row's crest (the pumps' `clear` keep-out holds the drop corridor open).
    # Segment 4 is the gravity drain + air-purge path and must only fall; V-B-I's collet
    # plane lies ~23 below the drain, ~126 mm aft-east of it — the tray stack's height
    # spends most of the banked fall, and the leg's author has the elbow-roll DOF
    # (bag_circuit_tray place_elbow) to turn V-B-I sideways if the drop needs it.
    _p("drain", "hopper-funnel", "fluid", (193.75, 92.5, 284.78), "z-", 6.35, "V-B-I by tube — segment 4 (hopper gate → shared source; must fall)", "funnel drain; spout exit annulus (`spout_id` 6.35 bore), bottom face of the spout tube"),
    # Source-select assembly (Tray 1) — the manifold's four boundary connectors: the outlet
    # elbows' free collets. Each tray publishes its collets in its own coordinates
    # (`boundary_collets`, off the same rolls the STEP is built with) and _contents carries
    # them through the placement, so a tray edit or a stack move lands here on its own —
    # position and axis both. The tray floors the stack (180° about Z), so V-A/V-B face
    # straight UP east — the tap feed and the funnel drain both arrive from above — while
    # V-C/V-D face up WEST along the junction column, each rolled inward off its port axis to
    # aim at the bag tray's collet across the gap. On-tray plumbing (segments 3/5/6/7/8 —
    # valve↔divider tubes) is interior to the assembly and carries no port here.
    _p("V-A-I", "source-select-assembly", "fluid", *contents.src_collet("VA"), 6.35, "tap-water chain — segment 2, teed off the BFP's 3/8\" discharge hose ahead of the SeaFlo (pressurized; length-tolerant)", "JG elbow collet, 1/4\" tube, facing up at the aft-east station"),
    _p("V-B-I", "source-select-assembly", "fluid", *contents.src_collet("VB"), 6.35, "hopper-funnel drain by tube — segment 4 (gravity + air purge; the drain exit sits ~86 above this collet)", "JG elbow collet, 1/4\" tube, facing up at the fwd-east station"),
    _p("V-C-O", "source-select-assembly", "fluid", *contents.src_collet("VC"), 6.35, "tee-y-c Y-C-1 — segment 9 (routed)", "JG elbow collet, 1/4\" tube, rolled inward up the junction column"),
    _p("V-D-O", "source-select-assembly", "fluid", *contents.src_collet("VD"), 6.35, "tee-y-f Y-F-1 — segment 19 (routed)", "JG elbow collet, 1/4\" tube, rolled inward up the junction column"),
    # Bag-circuit assembly (Tray 2) — the manifold's six boundary connectors: the west
    # outlet elbows' free collets, the bare east port tips, and the two Tee bag branches,
    # derived the same way through the tray's INVERTED pose (180° about Y). V-E/V-H face
    # DOWN the junction column, each rolled outward off its port axis to meet the source
    # tray's; V-F/V-I run bare, facing EAST, each turned −Y by a discharge elbow onto the
    # LLDPE run down to its divider over the pumps; both bag branches are rolled to the one
    # `bag_fall_aim`, each aimed DOWN its own fall to its reservoir. On-tray plumbing (segments
    # 14/16/24/26 — valve↔Tee port butts) is
    # interior to the assembly and carries no port here.
    _p("V-F-I", "bag-circuit-assembly", "fluid", *contents.bag_collet("VF"), 6.35, "Y-D-2 via elbow-bag-y-d — segment 13 (routed)", "bare valve port collet, 1/4\" tube, facing east onto its discharge elbow"),
    _p("V-I-I", "bag-circuit-assembly", "fluid", *contents.bag_collet("VI"), 6.35, "Y-G-2 via elbow-bag-y-g — segment 23 (routed)", "bare valve port collet, 1/4\" tube, facing east onto its discharge elbow"),
    _p("V-E-O", "bag-circuit-assembly", "fluid", *contents.bag_collet("VE"), 6.35, "tee-y-c Y-C-2 — segment 10 (bag A to pump return, routed)", "JG elbow collet, 1/4\" tube, rolled outward down the junction column"),
    _p("V-H-O", "bag-circuit-assembly", "fluid", *contents.bag_collet("VH"), 6.35, "tee-y-f Y-F-2 — segment 20 (bag B to pump return, routed)", "JG elbow collet, 1/4\" tube, rolled outward down the junction column"),
    _p("Y-E-2", "bag-circuit-assembly", "fluid", *contents.bag_collet("YE"), 6.35, "Bag A port — foam-assembly reservoir-A line, segment 15", "Tee branch collet, 1/4\" tube, rolled to aim down the fall to reservoir A"),
    _p("Y-H-2", "bag-circuit-assembly", "fluid", *contents.bag_collet("YH"), 6.35, "Bag B port — foam-assembly reservoir-B line, segment 25", "Tee branch collet, 1/4\" tube, rolled to aim down the fall to reservoir B"),
    # Nozzle-gate assembly (Tray 3) — four boundary connectors, all bare valve port tips,
    # derived the same way through the tray's INVERTED pose (180° about Y, in the pocket
    # east of the bag assembly). V-G-I/V-J-I face WEST at the bag tray's east bank, each
    # turned −Y by a discharge elbow onto its run to the divider; V-G-O/V-J-O face EAST into the
    # +X wall pocket, each turned +Z by an outlet elbow onto its run aft to the rear umbilical.
    _p("V-G-I", "nozzle-gate-assembly", "fluid", *contents.noz_collet("VG-I"), 6.35, "Y-D-3 via elbow-y-g — segment 17 (routed)", "bare valve port collet, 1/4\" tube, facing west onto its discharge elbow"),
    _p("V-J-I", "nozzle-gate-assembly", "fluid", *contents.noz_collet("VJ-I"), 6.35, "Y-G-3 via elbow-y-d — segment 27 (routed)", "bare valve port collet, 1/4\" tube, facing west onto its discharge elbow"),
    _p("V-G-O", "nozzle-gate-assembly", "fluid", *contents.noz_collet("VG-O"), 6.35, "bulkhead-flavor-a via elbow-noz-a — segment 18 (routed)", "bare valve port collet, 1/4\" tube, facing east onto its outlet elbow"),
    _p("V-J-O", "nozzle-gate-assembly", "fluid", *contents.noz_collet("VJ-O"), 6.35, "bulkhead-flavor-b via elbow-noz-b — segment 28 (routed)", "bare valve port collet, 1/4\" tube, facing east onto its outlet elbow"),
    # Pump row — each Kamoer's two boundary connectors are its outlet ELBOWS' free collets
    # (pump_assembly.py seats a PP0308E on each arch_xs outlet), carried through the lying
    # pose (−90° about Y, +90° roll about X) + the POS tuples: the elbows stand on the +Z
    # face, legs turning west over the head, both free collets facing −X at z 271.17. The
    # two stations straddle the pump's width; inlet aft, outlet front (the peristaltic
    # direction is firmware's; the assignment is the loom's convention). Ø is the 1/4"
    # line nominal.
    _p("P-A-I", "pump-a", "fluid", *contents.pump_inlet_pose("pump-a"), 6.35, "tee-y-f Y-F-3 — segment 21 (channel B suction, routed)", "PP0308E elbow collet, aft station, facing west at the collet centre (fluid-21 climbs the west end then runs east into it)"),
    _p("P-A-O", "pump-a", "fluid", *contents.pump_outlet_pose("pump-a"), 6.35, "Y-G-1 divider stem — segment 22 (channel B discharge, routed)", "PP0308E elbow collet, front station, aimed east at y-g"),
    _p("P-B-I", "pump-b", "fluid", *contents.pump_inlet_pose("pump-b"), 6.35, "tee-y-c Y-C-3 — segment 11 (channel A suction, routed)", "PP0308E elbow collet, aft station, aimed northwest where fluid-11 drops in off the pump row"),
    _p("P-B-O", "pump-b", "fluid", *contents.pump_outlet_pose("pump-b"), 6.35, "Y-D-1 divider stem — segment 12 (channel A discharge, routed)", "PP0308E elbow collet, front station, facing west at y-d"),
    # Pump-inlet union tees — free-hanging PP0208E fittings in the junction column, ports
    # named by the fluid topology and derived off _contents' tee placement. The run lies on
    # the line between the two collets it butts, which leans off vertical because both elbows
    # are rolled to aim at each other: -1 down at the source drop, -2 up at the bag return,
    # each one straight stub away, and branch -3 rolled about the run (JUNCTION_ROLL) to swing
    # forward (−Y) off the pump row, where its suction leg picks it up.
    _p("Y-C-1", "tee-y-c", "fluid", *contents.tee_port("tee-y-c", 1), 6.35, "source-select V-C-O — segment 9 (routed)", "PP0208E run collet, down the column at the source"),
    _p("Y-C-2", "tee-y-c", "fluid", *contents.tee_port("tee-y-c", 2), 6.35, "bag-circuit V-E-O — segment 10 (routed)", "PP0208E run collet, up the column at the bag tray"),
    _p("Y-C-3", "tee-y-c", "fluid", *contents.tee_port("tee-y-c", 3), 6.35, "pump-b P-B-I — segment 11 (routed)", "PP0208E branch collet, rolled forward (−Y) off the pump row"),
    _p("Y-F-1", "tee-y-f", "fluid", *contents.tee_port("tee-y-f", 1), 6.35, "source-select V-D-O — segment 19 (routed)", "PP0208E run collet, down the column at the source"),
    _p("Y-F-2", "tee-y-f", "fluid", *contents.tee_port("tee-y-f", 2), 6.35, "bag-circuit V-H-O — segment 20 (routed)", "PP0208E run collet, up the column at the bag tray"),
    _p("Y-F-3", "tee-y-f", "fluid", *contents.tee_port("tee-y-f", 3), 6.35, "pump-a P-A-I — segment 21 (routed)", "PP0208E branch collet, rolled forward (−Y), canted east past tee-y-c"),
    # Pump-discharge dividers Y-D/Y-G — free-hanging PP2308E two-way dividers over the pump row,
    # ports off _contents' divider placement. Each divider is tilted (_solve_discharge) so its two
    # parallel outlets (-2 upper, -3 lower) face back at a flavor's bag and nozzle elbows; the stem
    # (-1) faces the pump discharge it will later feed. The netlist is diagonal — a flavor's two
    # valves sit on opposite tray rows.
    _p("Y-D-1", "y-d", "fluid", *contents.divider_port("y-d", 1), 6.35, "pump-b P-B-O — segment 12 (channel A discharge, routed)", "PP2308E stem collet, facing the pump"),
    _p("Y-D-2", "y-d", "fluid", *contents.divider_port("y-d", 2), 6.35, "elbow-bag-y-d free — segment 13 (routed)", "PP2308E upper outlet, aimed at the bag-A elbow"),
    _p("Y-D-3", "y-d", "fluid", *contents.divider_port("y-d", 3), 6.35, "elbow-y-g free — segment 17 (routed)", "PP2308E lower outlet, aimed at the nozzle-A elbow"),
    _p("Y-G-1", "y-g", "fluid", *contents.divider_port("y-g", 1), 6.35, "pump-a P-A-O — segment 22 (channel B discharge, routed)", "PP2308E stem collet, facing the pump"),
    _p("Y-G-2", "y-g", "fluid", *contents.divider_port("y-g", 2), 6.35, "elbow-bag-y-g free — segment 23 (routed)", "PP2308E upper outlet, aimed at the bag-B elbow"),
    _p("Y-G-3", "y-g", "fluid", *contents.divider_port("y-g", 3), 6.35, "elbow-y-d free — segment 27 (routed)", "PP2308E lower outlet, aimed at the nozzle-B elbow"),
    # The four discharge turn-elbows' free collets — where each LLDPE run to a divider leaves. Each
    # elbow is rolled about its valve-port axis so its free leg aims at the divider outlet it feeds.
    _p("free", "elbow-bag-y-d", "fluid", *contents.elbow_free_pose("elbow-bag-y-d"), 6.35, "y-d Y-D-2 — segment 13 (routed)", "PP0308E free collet, aimed at the Y-D upper outlet"),
    _p("free", "elbow-y-g", "fluid", *contents.elbow_free_pose("elbow-y-g"), 6.35, "y-d Y-D-3 — segment 17 (routed)", "PP0308E free collet, aimed at the Y-D lower outlet"),
    _p("free", "elbow-bag-y-g", "fluid", *contents.elbow_free_pose("elbow-bag-y-g"), 6.35, "y-g Y-G-2 — segment 23 (routed)", "PP0308E free collet, aimed at the Y-G upper outlet"),
    _p("free", "elbow-y-d", "fluid", *contents.elbow_free_pose("elbow-y-d"), 6.35, "y-g Y-G-3 — segment 27 (routed)", "PP0308E free collet, aimed at the Y-G lower outlet"),
    # The two nozzle-outlet elbows' free collets — where each LLDPE run to a rear flavor bulkhead
    # leaves, standing +Z out of the +X wall pocket.
    _p("free", "elbow-noz-a", "fluid", *contents.outlet_free_pose("elbow-noz-a"), 6.35, "bulkhead-flavor-a tube-in — segment 18 (routed)", "PP0308E free collet, up out of the pocket"),
    _p("free", "elbow-noz-b", "fluid", *contents.outlet_free_pose("elbow-noz-b"), 6.35, "bulkhead-flavor-b tube-in — segment 28 (routed)", "PP0308E free collet, up out of the pocket"),
    # Waveshare display — its data/power connector is NOT in the imported STEP (only the four
    # corner mounts are), so this one harness port is placed provisionally on the interior (+Y)
    # back face at the PCB centre. A viewer pick would pin it exactly.
    _p("harness", "display", "electrical", (56.75, 43.8, 300.2), "y+", 8.0, "5 V power + display data (PCBA / power bus)", "connector not modeled in STEP; PROVISIONAL on the interior back face — refine with a pick"),
    # Controller PCBA — every field loom lands on a labelled JST XH edge connector (J1–J14, no
    # J12; ac-wiring-schedule.md §Board connector map). Positions are EXACT: each connector's
    # pcba.tsx board coordinate mapped world = (x+258.8, y+228.8) — the transform solved from the
    # four mounting holes — with Z at the board's top plane (looms plug from +Z). Ø is the loom
    # bundle OD by conductor count (est).
    _p("J1-manifold-a", "pcba", "electrical", (269.8, 245.28, 292.5), "z+", 10.0, "8 manifold-A solenoids (DC-6)", "9-cond JST XH"),
    _p("J2-manifold-b", "pcba", "electrical", (269.8, 223.03, 292.5), "z+", 8.0,  "4 manifold-B solenoids + condenser fan (DC-7/DC-8)", "6-cond JST XH"),
    _p("J3-faucet",     "pcba", "electrical", (206.55, 198.5, 292.5), "z+", 6.0,  "faucet display UART up the umbilical (SIG-6)", "4-cond JST XH"),
    _p("J4-sensors",    "pcba", "electrical", (223.8, 198.5, 292.5),  "z+", 8.0,  "temp bus + DIGITEN flow + moisture (SIG-1/4/9)", "7-cond JST XH"),
    _p("J5-relays",     "pcba", "electrical", (216.85, 259.8, 292.5), "z+", 6.0,  "both Teyleten relay modules (LV-1/2/3)", "4-cond JST XH"),
    _p("J6-reeds-a",    "pcba", "electrical", (231.7, 259.8, 292.5),  "z+", 7.0,  "foam-assembly reed-cable-A — reservoir A reeds (SIG-10)", "5-cond JST XH"),
    _p("J7-reeds-b",    "pcba", "electrical", (258.3, 198.5, 292.5),  "z+", 8.0,  "foam-assembly reed-cable-B — reservoir B + carbonator reeds (SIG-2/3/11)", "7-cond JST XH"),
    _p("J8-i2c",        "pcba", "electrical", (260.1, 259.8, 292.5),  "z+", 6.0,  "off-board MPR121 cap-sense (SIG-8)", "4-cond JST XH"),
    _p("J9-display",    "pcba", "electrical", (241.05, 198.5, 292.5), "z+", 6.0,  "display harness — 4.3B RS485 + 12 V (SIG-7)", "4-cond JST XH"),
    _p("J10-12v",       "pcba", "electrical", (271.15, 207.3, 292.5), "z+", 5.0,  "dc-dist 12 V block — board power inlet (DC-4)", "2-pole 5.0 mm screw block"),
    _p("J11-gas",       "pcba", "electrical", (196.8, 204.95, 292.5), "z+", 6.0,  "mq6-sensor header — MQ-6 gas/leak sensor (SIG-12)", "4-cond JST XH"),
    _p("J13-pumps",     "pcba", "electrical", (246.55, 259.8, 292.5), "z+", 6.0,  "Kamoer pump A + B motors (DC-5)", "4-cond JST XH"),
    _p("J14-usb",       "pcba", "electrical", (196.8, 245.3, 292.5),  "z+", 9.0,  "USB-C programming port (bench only, no loom)", "USB-C receptacle"),
    # 12 V distribution block (DIN) — the three runs that land on it, on its top face. Terminal
    # positions along the block are provisional (the block's internal poles aren't modeled).
    _p("in",       "dc-dist", "electrical", (34.0, 305.0, 283.0), "z+", 6.0, "PSU 12 V output (DC-1)", "16 AWG; PROVISIONAL terminal position"),
    _p("to-board", "dc-dist", "electrical", (49.0, 305.0, 283.0), "z+", 5.0, "board J10 12 V inlet (DC-4)", "16 AWG; PROVISIONAL terminal position"),
    _p("to-relay2","dc-dist", "electrical", (64.0, 305.0, 283.0), "z+", 6.0, "Teyleten relay #2 contact — SeaFlo gate (DC-2)", "16 AWG; PROVISIONAL terminal position"),
    # Power assembly (tray + Mean Well PSU + 2 Teyleten relays + AC-dist block + ground bus) — the
    # connection groups entering/leaving the tray. Terminal positions are provisional (the device
    # terminals inside the tray aren't individually modeled).
    _p("ac-in",           "power-tray", "electrical", (30.0, 212.0, 290.0), "y-", 8.0, "C14 mains inlet — H+N+G (AC-1)", "16 AWG mains; PROVISIONAL"),
    _p("compressor-feed", "power-tray", "electrical", (175.0, 247.0, 290.0), "x+", 8.0, "compressor terminal block — switched-H + N + G through the shroud grommet (AC-4/5/6)", "16 AWG; PROVISIONAL"),
    _p("dc-out",          "power-tray", "electrical", (100.0, 285.9, 290.0), "y+", 6.0, "dc-dist 12 V block (DC-1)", "16 AWG; PROVISIONAL"),
    _p("relay-ctrl",      "power-tray", "electrical", (130.0, 212.0, 290.0), "y-", 6.0, "board J5 RELAYS control loom (LV-1/2/3)", "4-cond; PROVISIONAL"),
]


# Components that carry NO tube or wire connector at all — a passive body, located trivially
# once declared connector-free. Declaring the absence is the honest analogue of declaring a
# position — never a silent gap, and it lets the located axis reach 100% without inventing a
# port. Empty today: every packed component carries at least one connector. A name here must
# own no PORTS entry (asserted in ports_audit).
PASSIVE_NO_PORTS: frozenset = frozenset()


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


def _on_surface(pos, solid, shell, diam, tol) -> bool:
    """True when `pos` sits on the body's real surface. A port names the mouth of the bore it
    carries, so the allowance is one bore radius — the distance from a bore's centre out to its
    rim — plus tol. An opening is wherever the body has one: the free collet of an elbow, a
    connector on a populated board, a hole in a wall. Degrades to the bounding box when the exact
    kernel is unavailable."""
    if not _HAVE_EXACT or shell is None:
        return _on_bbox_surface(pos, _boxes.boxed(solid), tol)
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(*pos)).Vertex()
    dss = BRepExtrema_DistShapeShape(v, shell)
    dss.Perform()
    if not dss.IsDone():
        return _on_bbox_surface(pos, _boxes.boxed(solid), tol)
    return dss.Value() <= (diam or 0.0) / 2.0 + tol


def ports_audit(solids: dict, tol: float = 2.0) -> list[tuple[str, bool, list]]:
    """Group PORTS by component; return (component, all_located, [(port, status)]) where status
    is 'ok' (positioned + on the placed body's surface + sized), 'off-surface' (a position not on
    the solid — a drifted/typo'd port), 'no-pos' (not yet located), or 'no-diam' (located but its
    bore Ø is still unknown). A component is located only when every port is 'ok' — a full
    coordinate AND bore, the PCBA per-pad specificity. Components with no ports declared are not
    returned — like placement rules, they are simply not-yet-authored."""
    by_comp: dict[str, list[Port]] = {}
    for p in PORTS:
        by_comp.setdefault(p.component, []).append(p)
    contradiction = PASSIVE_NO_PORTS & by_comp.keys()
    assert not contradiction, f"declared connector-free but has ports: {sorted(contradiction)}"
    out = []
    for comp, ports in by_comp.items():
        solid = solids.get(comp)
        shell = _face_shell(solid) if (solid is not None and _HAVE_EXACT) else None
        rows = []
        for p in ports:
            if p.pos is None:
                rows.append((p, "no-pos"))
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
    names = list(solids)
    bbs = {n: _boxes.boxed(solids[n]) for n in names}
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if _bbox_gap(bbs[a], bbs[b]) > 0:
                continue
            v = solids[a].intersect(solids[b]).Volume()
            if v > CLASH_TOL:
                out.append((a, b, v))
    for hn, hs in pieces.items():
        hbb = _boxes.boxed(hs)
        for n in names:
            if _bbox_gap(hbb, bbs[n]) > 0:
                continue
            v = hs.intersect(solids[n]).Volume()
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
            inter = sa.intersect(sb)
            if inter.Volume() > CLASH_TOL:
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


def line_clashes(lines: dict, solids: dict, ends: dict) -> list[tuple[str, str, float]]:
    """Every routed tube that INTERPENETRATES another tube, or a placed solid it does not
    terminate on, by overlap volume over CLASH_TOL — the routed analogue of pack_clashes. A tube
    driving through a part, or through another tube, is as unbuildable as two overlapping solids;
    but the tubes are _lines runs, not registry components, so pack_closes never sees them. `lines`
    is {id: tube-solid}, `ends` is {id: {the component names the run joins}} — the two components a
    run terminates on are skipped, since a tube seats INTO its end fittings' collets by design.

    Volume, not distance, is the test that matters here: BRepExtrema (the `_solid_gap` the routed
    clearance detail reads) returns 0 for a tube that just grazes another AND for one that drives
    clean through it — so only the overlap volume separates a kiss from an intersection.

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
            v = lines[a].intersect(lines[b]).Volume()
            if v > CLASH_TOL:
                out.append((a, b, v))
    for i in ids:                                                 # tube ∩ part it does not join
        for n, s in solids.items():
            if n in ends.get(i, ()):
                continue
            if _bbox_gap(lbb[i], sbb[n]) > 0:
                continue
            v = lines[i].intersect(s).Volume()
            if v > CLASH_TOL:
                out.append((i, n, v))
    return out


def part_clearances(solids: dict) -> list[tuple[str, str, float, bool]]:
    """Content pairs closer than REPORT_NEAR, as (a, b, gap, allowed) sorted tightest
    first. `allowed` marks a declared intentional contact (TOUCHING_OK). Part-to-wall is
    excluded on purpose — parts seat against walls by design; overlap there is the
    pack-closes gate's job, not clearance."""
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
    ports: list = field(default_factory=list)   # the full connector inventory — every port's
                                                # component, position, face, bore Ø, mate, and
                                                # status. Uncapped (unlike check.detail, which
                                                # DETAIL_MAX trims), so the audit reads every
                                                # coordinate + diameter straight from the sidecar.
    shapes: list = field(default_factory=list)  # per component: the boxes it really occupies (one
                                                # per solid it is built from), how much of them is
                                                # material, and whether the geometry is still a
                                                # bare primitive. Also uncapped.


def _pct(done: int, total: int) -> int:
    return 100 if total == 0 else round(100 * done / total)


def routed_check(solids=None) -> tuple:
    """The routed goal axis on its own — a (Check, pct) pair. Kept separate from the component
    gates and audits because it reads _lines (which route work changes every build) while the
    component audits do not: a build reusing cached component audits still recomputes this fresh,
    so the routed % never goes stale. Given the placed solids, each authored run's detail carries
    its tightest gap to a part it does not terminate on — the tube↔part clearance."""
    import _lines
    conns = load_connections()
    fluid = sum(1 for c in conns if c.kind == "fluid")
    wire = sum(1 for c in conns if c.kind == "wire")
    refrig = sum(1 for c in conns if c.kind == "refrigerant")
    water = sum(1 for c in conns if c.kind == "water")
    routed_done = sum(1 for c in conns if c.routed)
    routed = _pct(routed_done, len(conns))
    routed_detail = [f"{fluid} fluid + {water} water + {refrig} refrigerant + {wire} electrical; "
                     f"{routed_done} routed — the water path waits on the SeaFlo the ASSE 1022's "
                     f"discharge hose lands on, the fluid path on the manifold's remaining legs; "
                     f"the electrical runs on the components being held"]
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
    ck = Check("routed", "Connections modeled as real 3D paths (fluid + water + refrigerant + electrical)",
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
    import _lines
    import _routing as R
    runs = _lines.build_runs()
    lines = {r.id: R.tube(r) for r in runs}
    ends = {r.id: {r.frm.split(".")[0], r.to.split(".")[0]} for r in runs}
    clashes = line_clashes(lines, {**solids, **pieces}, ends)
    return Check("lines-clear", "No routed tube intersects a part, a piece or another tube", "gate",
                 "pass" if not clashes else "fail", f"{len(clashes)} clash", "0 clash",
                 [f"{a} ∩ {b}: {v:.1f} mm³" for a, b, v in clashes][:DETAIL_MAX])


def build_scorecard(solids: dict, pieces: dict, bed: tuple[float, float, float], inner: tuple) -> Scorecard:
    reg = {c.name: c for c in COMPONENTS}
    checks: list[Check] = []

    def gate(cid, label, ok, value, target, detail=None):
        checks.append(Check(cid, label, "gate", "pass" if ok else "fail", value, target, (detail or [])[:DETAIL_MAX]))

    def goal(cid, label, done, value, target, detail=None, active=True):
        checks.append(Check(cid, label, "goal", "pass" if done else "warn", value, target, (detail or [])[:DETAIL_MAX], active))

    # ── GATES — must hold to print + assemble what is placed ──
    # Coverage: the registry must describe exactly the placed set, or the goal counts
    # below are measured against the wrong universe.
    placed_set = set(solids)
    declared = set(reg)
    undeclared = sorted(placed_set - declared)
    unplaced = sorted(declared - placed_set)
    gate("coverage", "Every placed part declared in the registry", not undeclared and not unplaced,
         f"{len(placed_set & declared)}/{len(placed_set)} placed declared", "all declared",
         [f"{n}: placed but not declared" for n in undeclared] + [f"{n}: declared but not placed" for n in unplaced])

    clashes = pack_clashes(solids, pieces)
    gate("pack-closes", "No two solids overlap (pack closes)", not clashes,
         f"{len(clashes)} clash", "0 clash",
         [f"{a} ∩ {b}: {v:.1f} mm³" for a, b, v in clashes])

    # The routed tubes clash against the placed solids the same way — but they live outside the
    # component registry, so pack-closes never sees them. Fresh every build (reads _lines); the
    # cache layer recomputes it on a hit, like routed.
    checks.append(lines_clear_check(solids, pieces))

    clr = part_clearances(solids)
    violations = [(a, b, g) for a, b, g, allowed in clr if not allowed and g < CLEARANCE_FLOOR]
    tightest = next(((a, b, g) for a, b, g, allowed in clr if not allowed), None)
    gate("clearance-floor", "Part↔part clearance ≥ floor (unless a declared contact)", not violations,
         f"{tightest[2]:.2f} mm" if tightest else "—", f"≥ {CLEARANCE_FLOOR} mm",
         # Show the tightest handful either way, marking declared contacts and violations.
         [f"{a} — {b}: {g:.2f} mm" + (" — CONTACT (declared ok)" if allowed else (" — ✗ below floor" if g < CLEARANCE_FLOOR else ""))
          for a, b, g, allowed in clr[:DETAIL_MAX]])

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
         f"{placed_pct}% ({len(placed_held)}/{total})", "100%", placed_detail, active=True)

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
            tag = "" if s == "ok" else f"  — {_pstat[s]}"
            located_detail.append(f"    – {comp}:{pt.name} ({pt.kind}) {xyz} {od} → {pt.mates}{tag}")
    for c in passive:
        located_detail.append(f"✓ {c.name}: no connectors (passive body)")
    unlocated = total - len(pta) - len(passive)
    located_detail.append(f"{unlocated} components: no connector positions defined yet")
    goal("located", "Connectors located on the component — position + bore Ø (tubes + wires)", located_pct == 100,
         f"{located_pct}% ({len(located_comps) + len(passive)}/{total})", "100%", located_detail, active=True)

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
         f"{shaped}% ({len(real)}/{total})", "100%", shaped_detail, active=True)

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
         [f"{len(held_done)} held (through-wall bodies + display); {total - len(held_done)} loose internal parts unheld"],
         active=False)

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

    gates_pass = all(c.status == "pass" for c in checks if c.kind == "gate")
    return Scorecard(checks, gates_pass, placed_pct, located_pct, shaped, routed, held,
                     ports_table, shapes_table)


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
        "checks": [
            {"id": c.id, "label": c.label, "kind": c.kind, "status": c.status,
             "value": c.value, "target": c.target, "detail": list(c.detail), "active": c.active}
            for c in sc.checks
        ],
        "ports": list(sc.ports),
        "shapes": list(sc.shapes),
    }


def format_scorecard(sc: Scorecard) -> str:
    """Render the verdict as a terminal block. Gates read green (pass) / red (fail); the
    two focus goals read green (100%) / yellow (in progress); the two deferred goals render
    gray. Color is emitted only to a TTY — piped/captured output stays plain."""
    tty = sys.stdout.isatty()
    GREEN, YELLOW, RED, GRAY = "32", "33", "31", "90"

    def col(s, code):
        return f"\033[{code}m{s}\033[0m" if tty else s

    mark = {"pass": "✓", "fail": "✗", "warn": "•"}
    gates = [c for c in sc.checks if c.kind == "gate"]
    goals = {c.id: c for c in sc.checks if c.kind == "goal"}
    passed = sum(1 for c in gates if c.status == "pass")
    w = max(len(c.label) for c in sc.checks)
    rows = []

    rows.append("── enclosure scorecard " + "─" * 30)

    # Gates.
    hdr = f"GATES (printable + assembleable)   {passed}/{len(gates)} pass"
    rows.append(hdr if sc.gates_pass else hdr + "   " + col("✗ NOT BUILD-READY", RED))
    for c in gates:
        code = GREEN if c.status == "pass" else RED
        rows.append(f"  {col(mark[c.status], code)} {c.label.ljust(w)}  {c.value}  (want {c.target})")
        for d in c.detail:
            rows.append(f"      – {d}")

    # Goals — the three focus axes live, the two deferred axes gray.
    focus_met = sc.placed == 100 and sc.located == 100 and sc.shaped == 100
    done = sc.gates_pass and focus_met and sc.routed == 100 and sc.held == 100
    tail = col("  ✓ DONE", GREEN) if done else (col("  ✓ FOCUS MET", GREEN) if focus_met else "")
    rows.append("GOAL   " + col(f"focus: placed {sc.placed}% · located {sc.located}% · shaped {sc.shaped}%", GREEN if focus_met else YELLOW)
                + "   " + col(f"deferred: routed {sc.routed}% · held {sc.held}%", GRAY) + tail)

    def render_goal(gid):
        c = goals[gid]
        if c.active:
            code = GREEN if c.status == "pass" else YELLOW
            rows.append(f"  {col(mark[c.status], code)} {col(c.label.ljust(w), code)}  {c.value}  (want {c.target})")
            for d in c.detail:
                rows.append(f"      – {d}")
        else:
            rows.append(col(f"  · {c.label.ljust(w)}  {c.value}  — deferred until focus is met", GRAY))
            for d in c.detail:
                rows.append(col(f"      – {d}", GRAY))

    for gid in ("placed", "located", "shaped", "routed", "held"):
        render_goal(gid)

    rows.append("─" * 53)
    return "\n".join(rows)
