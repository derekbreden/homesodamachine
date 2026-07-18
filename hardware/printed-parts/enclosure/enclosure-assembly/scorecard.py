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
    routed  — deferred. Every connection (fluid + refrigerant + electrical) a real 3D
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

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Minimum solid-to-solid distance. cadquery 2 binds OpenCascade as OCP; fall back to
# a bbox-gap estimate if the exact kernel call is unavailable, so the scorecard degrades
# to an approximation rather than crashing.
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
    _c("drip-pan",          "real",        True,  "none", "printed catch basin STEP (rounded basin + floor cove); rests on the compressor top, mount TBD (held)"),
    _c("moisture-sensor",   "real",        True,  "none", "Shutao probe plate STEP (flat board + lead holes); lies in the pan, unfastened"),
    _c("multiplex",         "real",        True,  "none", "ASSE 1022 backflow preventer (hex-barrel STEP + vent barb); floats over the pan, no mount"),
    _c("seaflo-pump",       "placeholder", True,  "none", "diaphragm pump; feet splay to ~98, no mount modeled"),
    _c("gasher-water",      "real",        True,  "none", "GASHER check valve (hex barrel STEP); rides the seaflo top, unfastened"),
    _c("digiten-flow",      "real",        True,  "none", "flow sensor; rests on the seaflo top, unfastened"),
    # CO2 chain
    _c("gasher-co2",        "real",        True,  "none", "GASHER check valve (hex barrel STEP); on the CO2 inlet chain, unfastened"),
    _c("wr1110",            "real",        True,  "none", "WR1110 regulator STEP (body between two wrench hexes); bracket geometry TBD (front-panel README)"),
    # Flavor pumps
    _c("pump-assembly-1",   "real",        True,  "none", "Kamoer pump; rests on the seaflo top, unfastened"),
    _c("pump-assembly-2",   "real",        True,  "none", "Kamoer pump; rests on the condenser top, unfastened"),
    # Electronics shelf
    _c("power-tray",        "real",        True,  "none", "printed tray holds its boards; tray-to-shell joinery deferred (power-tray README)"),
    _c("pcba",              "real",        True,  "none", "printed tray holds the board; tray-to-shell joinery deferred (pcba-tray README)"),
    _c("dc-dist",           "real",        True,  "none", "DIN distribution block; no mount modeled"),
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
        ("compressor-shroud", "drip-pan"),      # pan sits on the compressor top
        ("drip-pan", "moisture-sensor"),        # probe plate lies in the pan
        ("drip-pan", "multiplex"),              # vent barb reaches down into the pan
        ("moisture-sensor", "multiplex"),       # vent tip hovers just over the plate (drip-catch)
        ("seaflo-pump", "gasher-water"),        # check valve rides the seaflo top
        ("seaflo-pump", "digiten-flow"),        # flow sensor rides the seaflo top
        ("seaflo-pump", "pump-assembly-1"),     # flavor pump 1 rides the seaflo top
        ("condenser+fan", "pump-assembly-2"),   # flavor pump 2 rides the condenser top
        ("foam-assembly", "power-tray"),        # electronics shelf on the foam-cap top
        ("foam-assembly", "pcba"),
        ("foam-assembly", "dc-dist"),
        ("gasher-co2", "wr1110"),               # CO2 chain adjacency
        ("gasher-co2", "co2-inlet"),            # check valve on the DERPIPE inboard stub
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


def load_connections() -> list[Connection]:
    """Every connection the box must route: the fluid tube segments (fluid-topology.md,
    `| N | From | To |`), the electrical runs (ac-wiring-schedule.md, `| AC/DC/SIG/LV-N |
    From | To |`), and the sealed refrigerant loop (REFRIGERANT_SEGMENTS). A connection
    counts as routed only once a real 3D path is modeled — none are today; the fluid segments
    live in the still-unplaced valve-manifold trays."""
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
    # Routed state comes from the paths _lines.py builds. Deferred import: _lines reads PORTS
    # back out of this module.
    import _lines
    done = _lines.routed_ids()
    for c in conns:
        c.routed = c.id in done
        c.blocked = _lines.BLOCKED.get(c.id, "")
    return conns


# ── Placement rules (the placed axis) — measured face-to-datum expectations ──
# Each component's INTENDED placement, written as measurements the scorecard checks
# against the enclosure interior datum (enclosure._dims() `inner`): (face, max_mm) means
# the component's `face` must sit within max_mm of the interior's same face. iz0 is the
# fixed Z=0 floor (not content-derived), so "z-" is a true "how far off the floor" check;
# the other interior faces hug the content, so "within a millimeter of x-/x+/y+" reads as
# "this part is the one against that wall". A component is `placed` when it has rules AND
# every rule holds; rules defined but violated are a visible drift; no rules yet = not
# started. Seeded for the three floor/back parts; every component earns rules eventually.
# Faces: x-/x+ = left/right walls, y-/y+ = front/back walls, z-/z+ = floor/ceiling.
PLACEMENT_RULES = {
    # "Foam is against the back-bottom, full width" — the canonical example.
    "foam-assembly":     [("y+", 1.0), ("x-", 1.0), ("x+", 1.0), ("z-", 10.0)],
    # "Compressor is front-left on the floor" (inset one corner-rib chain off the left wall).
    "compressor-shroud": [("y-", 1.0), ("z-", 4.0), ("x-", 15.0)],
    # "Condenser is front-right on the floor" (inset one corner-rib chain off the right wall).
    "condenser+fan":     [("y-", 1.0), ("z-", 4.0), ("x+", 15.0)],
}


def placement_audit(solids: dict, inner: tuple) -> list[tuple[str, bool, list]]:
    """For each component that has placement rules, measure every rule against the interior
    datum and return (name, all_hold, [(face, gap, max_mm, ok)]). Components without rules
    are not returned — they are simply not-yet-placed."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    datum = {"x-": ix0, "x+": ix1, "y-": iy0, "y+": iy1, "z-": iz0, "z+": iz1}
    out = []
    for name, rules in PLACEMENT_RULES.items():
        if name not in solids:
            continue
        bb = solids[name].BoundingBox()
        val = {"x-": bb.xmin, "x+": bb.xmax, "y-": bb.ymin, "y+": bb.ymax, "z-": bb.zmin, "z+": bb.zmax}
        checks = [(f, abs(val[f] - datum[f]), mx, abs(val[f] - datum[f]) <= mx) for f, mx in rules]
        out.append((name, all(c[3] for c in checks), checks))
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


PORTS = [
    # foam-assembly — 8 tube penetrations (foam-shell README §Penetrations, world coords via
    # _contents' placement) + 2 reed-cable exits on the −Y front wall. All on −Y except the CO2
    # inlet, which drops through the +Z foam-cap top. Ø: the beverage/flavor lines run the foam
    # shell's Ø6.5 port-holes (_cold_core_interface.port_hole_radius 3.25) sized for 1/4" tube;
    # the water-in takes the SeaFlo's 3/8" discharge; the copper legs are 1/4" ACR = 6.35.
    _p("carb-water-out", "foam-assembly", "fluid",       (141.5, 155.0, 46.5),  "y-", 6.35,  "dispense faucet (carb-water riser to the rear umbilical)", "1/4\" tank NPT elbow line"),
    _p("reservoir-A",    "foam-assembly", "fluid",       (238.5, 155.0, 35.5),  "y-", 6.35,  "reservoir A ↔ peristaltic pump A (bag circuit)", "1/4\" LLDPE flavor line, Ø6.5 foam port"),
    _p("reservoir-B",    "foam-assembly", "fluid",       (44.5,  155.0, 35.5),  "y-", 6.35,  "reservoir B ↔ peristaltic pump B (bag circuit)", "1/4\" LLDPE flavor line, Ø6.5 foam port"),
    _p("co2-in",         "foam-assembly", "fluid",       (141.5, 172.8, 262.9), "z+", 6.35,  "CO2 chain (WR1110 → foam-cap top entry)", "1/4\" PTC CO2 line; seats in the Ø16 foam-cap bore"),
    _p("evap-inlet",     "foam-assembly", "refrigerant", (141.5, 155.0, 72.0),  "y-", 6.35,  "condenser+fan outlet (liquid line via drier + cap tube)", "1/4\" ACR copper"),
    _p("evap-outlet",    "foam-assembly", "refrigerant", (141.5, 155.0, 191.0), "y-", 6.35,  "compressor-shroud suction", "1/4\" ACR copper"),
    _p("water-in",       "foam-assembly", "fluid",       (141.5, 155.0, 223.0), "y-", 9.525, "gasher-water out (SeaFlo outlet check → carbonator water inlet)", "3/8\" hose barb (SeaFlo 22-series port)"),
    _p("prv-vent",       "foam-assembly", "fluid",       (141.5, 155.0, 231.0), "y-", 6.35,  "appliance interior (relief-event discharge only)", "1/4\" relief discharge"),
    _p("reed-cable-A",   "foam-assembly", "electrical",  (254.5, 155.0, 35.5),  "y-", 6.5,   "J6 REEDS A — reservoir A level reeds (SIG-10)", "reed cable through the Ø6.5 pass-through, 16 mm outboard of reservoir-A (_port_cuts.py)"),
    _p("reed-cable-B",   "foam-assembly", "electrical",  (28.5,  155.0, 35.5),  "y-", 6.5,   "J7 REEDS B — reservoir B level reeds (SIG-11)", "reed cable through the Ø6.5 pass-through, 16 mm outboard of reservoir-B (_port_cuts.py)"),
    # compressor-shroud — compressor_shroud.py local hole centers carried through _contents'
    # _rot((0,0,1),−90) + _at(14,0,3). Both copper stubs share the one face → world +Y (toward
    # the foam/cold core they mate to); the AC gland + earth bond ride the +X face (into the
    # inter-part channel). suction/discharge assigned by world x per the physical loop. Copper is
    # 1/4" ACR; the AC gland Ø and earth-stud Ø are estimates pending the shroud teardown.
    _p("ac-mains",        "compressor-shroud", "electrical",  (192.0, 66.5, 78.0),  "x+", 10.0,  "Teyleten relay #1 / AC distribution (AC-4 switched-H + AC-5 N, 3-wire gland)", "gland bore ~Ø10 for 3-wire mains (estimate — confirm at shroud teardown)"),
    _p("earth-bond",      "compressor-shroud", "electrical",  (192.0, 31.5, 78.0),  "x+", 5.0,   "electronics-shelf ground bus (AC-6)", "M5 earth stud/ring (estimate — confirm at shroud teardown)"),
    _p("refrig-suction",  "compressor-shroud", "refrigerant", (59.25, 133.0, 78.0), "y+", 6.35,  "foam-assembly evaporator outlet", "1/4\" ACR copper"),
    _p("refrig-discharge","compressor-shroud", "refrigerant", (146.75, 133.0, 78.0),"y+", 6.35,  "condenser+fan inlet", "1/4\" ACR copper"),
    # condenser+fan — placeholder box harvested from the donor; ports located from step-viewer
    # picks (2026-07-17). Both refrigerant ports on the −X face (toward the compressor): inlet
    # top-front, outlet bottom-back (drier + cap-tube hang off it). The fan is on the opposite
    # +X face; airflow runs −X → +X. Copper is 1/4" ACR; the fan pigtail Ø is an estimate.
    _p("refrig-inlet",  "condenser+fan", "refrigerant", (213.0, 5.5, 175.5),   "x-", 6.35, "compressor-shroud discharge", "1/4\" ACR copper"),
    _p("refrig-outlet", "condenser+fan", "refrigerant", (213.0, 145.5, 8.5),   "x-", 6.35, "filter-drier → cap tube → foam-assembly evaporator inlet", "1/4\" ACR copper"),
    _p("fan-power",     "condenser+fan", "electrical",  (269.0, 75.5, 92.0),   "x+", 4.0,  "J2 MANIFOLD B FAN + COM (DC-8, 12 V)", "DC pigtail 2-wire (estimate); +X exhaust face (fan centered); airflow −X→+X"),
    # CO2 chain (front-left column) — the DERPIPE front-panel inlet carries the line inboard,
    # through the GASHER check and the WR1110 regulator, up to the foam-cap co2-in. All run the
    # +Y flow axis (fitting flow-face centers from the placed bboxes); the DERPIPE steps the
    # customer's 5/16" PTC down to the 1/4" NPT chain, everything downstream 1/4". This is the
    # second connection with both ends of every segment located — the CO2 spine, like the
    # refrigerant loop before it.
    _p("tube-in",  "co2-inlet", "fluid", (46.0, -22.0, 234.0),  "y-", 7.94, "customer CO2 supply — 5/16\" push-to-connect (rear umbilical)", "5/16\" PTC collet, outboard"),
    _p("npt-out",  "co2-inlet", "fluid", (46.0, 5.0, 234.0),    "y+", 6.35, "gasher-co2 in", "1/4\" NPT shank, inboard"),
    _p("in",  "gasher-co2", "fluid", (46.0, 14.0, 232.85), "y-", 6.35, "co2-inlet npt-out", "1/4\" NPT stub"),
    _p("out", "gasher-co2", "fluid", (46.0, 54.0, 232.85), "y+", 6.35, "wr1110 in", "1/4\" NPT stub"),
    _p("in",  "wr1110", "fluid", (46.0, 55.0, 233.0),  "y-", 6.35, "gasher-co2 out", "1/4\" CO2 inlet hex"),
    _p("out", "wr1110", "fluid", (46.0, 112.0, 233.0), "y+", 6.35, "foam-assembly co2-in (CO2 line up to the foam-cap top)", "1/4\" CO2 outlet hex"),
    # Rear-panel through-wall bodies — each JG bulkhead union is a 1/4" tube port each side of the
    # rear wall (Y = tube-flow axis, +Y = outward to the rear umbilical, −Y = inward to the
    # subsystem it feeds). The C14 mains inlet carries one 3-wire harness inboard from the panel
    # cord entry. Positions are the union/inlet flow-face centers from the placed bboxes.
    _p("tube-out", "bulkhead-flavor-a", "fluid", (195.05, 348.5, 292.45), "y+", 6.35, "customer flavor A line (rear umbilical)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-flavor-a", "fluid", (195.05, 314.2, 292.45), "y-", 6.35, "flavor A internal line (bag/pump circuit A)", "JG 1/4\" PTC, inward"),
    _p("tube-out", "bulkhead-flavor-b", "fluid", (224.95, 348.5, 292.45), "y+", 6.35, "customer flavor B line (rear umbilical)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-flavor-b", "fluid", (224.95, 314.2, 292.45), "y-", 6.35, "flavor B internal line (bag/pump circuit B)", "JG 1/4\" PTC, inward"),
    _p("tube-out", "bulkhead-carb", "fluid", (210.0, 348.5, 318.3), "y+", 6.35, "carbonated-water line (rear umbilical / faucet)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-carb", "fluid", (210.0, 314.2, 318.3), "y-", 6.35, "carb-water internal riser (DIGITEN → foam carb-water-out)", "JG 1/4\" PTC, inward"),
    _p("tube-out", "bulkhead-water", "fluid", (145.0, 348.5, 293.0), "y+", 6.35, "house tap-water line (rear umbilical)", "JG 1/4\" PTC, outward"),
    _p("tube-in",  "bulkhead-water", "fluid", (145.0, 314.2, 293.0), "y-", 6.35, "tap-water internal line (to multiplex BFP in)", "JG 1/4\" PTC, inward"),
    _p("mains-in", "c14-inlet", "electrical", (90.0, 312.0, 295.5), "y-", 8.0, "AC distribution — L/N/E to the electronics shelf", "C14 spade terminals; 3-wire mains harness inboard"),
    # Water deck — the supply chain's backflow preventer + the SeaFlo outlet check. The Multiplex
    # ASSE 1022 runs the +X flow axis (tap → BFP → SeaFlo) with its atmospheric-vent barb down
    # (−Z) into the drip pan; the water GASHER is the SeaFlo's outlet check on the +Y axis to the
    # carbonator water inlet. Fitting flow-face centers from the placed bboxes.
    _p("in",   "multiplex", "fluid", (25.0, 37.5, 180.15), "x-", 6.35, "bulkhead-water tube-in (tap water)", "ASSE 1022 inlet; line Ø est"),
    _p("out",  "multiplex", "fluid", (90.0, 37.5, 180.15), "x+", 6.35, "seaflo-pump water-in", "ASSE 1022 outlet; line Ø est"),
    _p("vent", "multiplex", "fluid", (57.5, 37.5, 159.5), "z-", 6.0,  "atmospheric vent — discharges into the drip-pan", "vent barb; Ø est"),
    _p("in",  "gasher-water", "fluid", (76.5, 84.0, 222.85),  "y-", 6.35, "seaflo-pump water-out", "1/4\" NPT (SeaFlo outlet check)"),
    _p("out", "gasher-water", "fluid", (76.5, 124.0, 222.85), "y+", 6.35, "foam-assembly water-in", "1/4\" NPT"),
    # Floor + water-deck sensors — a single signal header each (one cable penetration per part,
    # not one per conductor). MQ-6 header pins down (−Z) at the board floor; the Shutao moisture
    # plate carries a 2-pin lead on its top face.
    _p("header", "mq6-sensor", "electrical", (116.0, 144.0, 3.0), "z-", 8.0, "PCBA gas-sensor input — VCC/GND/DO/AO (SIG)", "4-pin 2.54 mm header, pins down"),
    _p("header", "moisture-sensor", "electrical", (80.0, 35.0, 159.1), "z+", 5.0, "PCBA moisture input — 2-pin (SIG + GND)", "2-pin lead header on the plate; Ø est"),
    # Hopper funnel — the removable silicone basin's single drain: the spout-tube exit annulus,
    # feeding the shared source (V-B hopper gate). One fluid port. The spout carries
    # hopper_funnel.py's `neck_dx` −14 off the opening centre, into the clear column between the
    # two pump towers, so the drain sits at the spout, not at the basin's bbox centre.
    _p("drain", "hopper-funnel", "fluid", (179.75, 63.3, 306.533), "z-", 6.35, "V-B hopper gate → shared source (channel split)", "funnel drain; spout exit annulus (`spout_id` 6.35 bore), bottom face of the spout tube"),
    # Flavor pumps (Kamoer KPHM400, P-A + P-B) — each pump's two JG PP0308E elbows seat their −Z
    # leg on a barb at the pump body's top and turn the line to −Y, so the tube pushes into the
    # free collet facing −Y; those two collet-face centres are the elbow solid's only openings
    # (pump_assembly.py's `_elbow`, measured on the placed geometry). The 2-wire DC motor lead
    # exits the motor can's far end at −Y — kamoer_kphm400's `motor_body`, the +Z end of the
    # pump-local depth axis, which _contents' rotate-90-about-X turns to −Y. in/out follow the
    # flavor manifold (P-A: Y-C→Y-D, P-B: Y-F→Y-G).
    _p("inlet",  "pump-assembly-1", "fluid",      (98.37, 90.94, 298.17),  "y-", 6.35, "Y-C → P-A-I (channel A source select)", "JG PP0308E elbow collet; 1/4\" flavor line"),
    _p("outlet", "pump-assembly-1", "fluid",      (155.37, 90.94, 298.17), "y-", 6.35, "P-A-O → Y-D (channel A to bag/nozzle)", "JG PP0308E elbow collet; 1/4\" flavor line"),
    _p("motor",  "pump-assembly-1", "electrical", (126.87, 4.0, 247.30),   "y-", 4.0,  "L298N channel A / 12 V DC drive", "2-wire DC motor lead off the motor-can end face; Ø est"),
    _p("inlet",  "pump-assembly-2", "fluid",      (204.37, 90.94, 266.17), "y-", 6.35, "Y-F → P-B-I (channel B source select)", "JG PP0308E elbow collet; 1/4\" flavor line"),
    _p("outlet", "pump-assembly-2", "fluid",      (261.37, 90.94, 266.17), "y-", 6.35, "P-B-O → Y-G (channel B to bag/nozzle)", "JG PP0308E elbow collet; 1/4\" flavor line"),
    _p("motor",  "pump-assembly-2", "electrical", (232.87, 4.0, 215.31),   "y-", 4.0, "L298N channel B / 12 V DC drive", "2-wire DC motor lead off the motor-can end face; Ø est"),
    # DIGITEN flow sensor — the dispense-side meter on the carb-water riser. Its two G1/4 PTC
    # collet bodies face ±Y (the +Y one toward the foam front, the −Y toward the umbilical run);
    # the 3-wire pigtail exits +Z. Collet centres extracted from the placed geometry; 1/4" tube
    # bore each.
    _p("in",     "digiten-flow", "fluid",      (121.0, 154.0, 229.0), "y+", 6.35, "foam-assembly carb-water-out (riser)", "G1/4 PTC, 1/4\" tube bore"),
    _p("out",    "digiten-flow", "fluid",      (121.0, 132.0, 229.0), "y-", 6.35, "carb-water to rear umbilical (bulkhead-carb)", "G1/4 PTC, 1/4\" tube bore"),
    _p("signal", "digiten-flow", "electrical", (121.0, 143.0, 245.0), "z+", 4.0,  "PCBA flow input — VCC/GND/SIG (Hall pigtail)", "3-wire pigtail; Ø est"),
    # Waveshare display — its data/power connector is NOT in the imported STEP (only the four
    # corner mounts are), so this one harness port is placed provisionally on the interior (+Y)
    # back face at the PCB centre. A viewer pick would pin it exactly.
    _p("harness", "display", "electrical", (56.75, 62.8, 315.0), "y+", 8.0, "5 V power + display data (PCBA / power bus)", "connector not modeled in STEP; PROVISIONAL on the interior back face — refine with a pick"),
    # SeaFlo diaphragm pump — still a placeholder box (its real 3/8\"-port geometry is banked at
    # reference/seaflo-22-pump but not yet wired). Its two 3/8" hose barbs + 12 V lead are placed
    # provisionally on the −X head end; they move when the real pump is wired in the water-deck
    # repack (or pinned by a viewer pick).
    _p("water-in",  "seaflo-pump", "fluid",      (14.0, 100.0, 185.0), "x-", 9.525, "multiplex out (BFP → pump)", "3/8\" hose barb; PROVISIONAL — placeholder box, awaiting the real SeaFlo-22 geometry"),
    _p("water-out", "seaflo-pump", "fluid",      (14.0, 120.0, 185.0), "x-", 9.525, "gasher-water in (pump → outlet check)", "3/8\" hose barb; PROVISIONAL — placeholder box, awaiting the real SeaFlo-22 geometry"),
    _p("power",     "seaflo-pump", "electrical", (100.0, 147.0, 185.0), "y+", 5.0, "12 V DC pump power (level/faucet interlock)", "2-wire lead; PROVISIONAL — placeholder box"),
    # Controller PCBA — every field loom lands on a labelled JST XH edge connector (J1–J14, no
    # J12; ac-wiring-schedule.md §Board connector map). Positions are EXACT: each connector's
    # pcba.tsx board coordinate mapped world = (x+258.8, y+201.8) — the transform solved from the
    # four mounting holes — with Z at the board's top plane (looms plug from +Z). Ø is the loom
    # bundle OD by conductor count (est).
    _p("J1-manifold-a", "pcba", "electrical", (269.8, 218.28, 292.5), "z+", 10.0, "8 manifold-A solenoids (DC-6)", "9-cond JST XH"),
    _p("J2-manifold-b", "pcba", "electrical", (269.8, 196.03, 292.5), "z+", 8.0,  "4 manifold-B solenoids + condenser fan (DC-7/DC-8)", "6-cond JST XH"),
    _p("J3-faucet",     "pcba", "electrical", (206.55, 171.5, 292.5), "z+", 6.0,  "faucet display UART up the umbilical (SIG-6)", "4-cond JST XH"),
    _p("J4-sensors",    "pcba", "electrical", (223.8, 171.5, 292.5),  "z+", 8.0,  "temp bus + DIGITEN flow + moisture (SIG-1/4/9)", "7-cond JST XH"),
    _p("J5-relays",     "pcba", "electrical", (216.85, 232.8, 292.5), "z+", 6.0,  "both Teyleten relay modules (LV-1/2/3)", "4-cond JST XH"),
    _p("J6-reeds-a",    "pcba", "electrical", (231.7, 232.8, 292.5),  "z+", 7.0,  "foam-assembly reed-cable-A — reservoir A reeds (SIG-10)", "5-cond JST XH"),
    _p("J7-reeds-b",    "pcba", "electrical", (258.3, 171.5, 292.5),  "z+", 8.0,  "foam-assembly reed-cable-B — reservoir B + carbonator reeds (SIG-2/3/11)", "7-cond JST XH"),
    _p("J8-i2c",        "pcba", "electrical", (260.1, 232.8, 292.5),  "z+", 6.0,  "off-board MPR121 cap-sense (SIG-8)", "4-cond JST XH"),
    _p("J9-display",    "pcba", "electrical", (241.05, 171.5, 292.5), "z+", 6.0,  "display harness — 4.3B RS485 + 12 V (SIG-7)", "4-cond JST XH"),
    _p("J10-12v",       "pcba", "electrical", (271.15, 180.3, 292.5), "z+", 5.0,  "dc-dist 12 V block — board power inlet (DC-4)", "2-pole 5.0 mm screw block"),
    _p("J11-gas",       "pcba", "electrical", (196.8, 177.95, 292.5), "z+", 6.0,  "mq6-sensor header — MQ-6 gas/leak sensor (SIG-12)", "4-cond JST XH"),
    _p("J13-pumps",     "pcba", "electrical", (246.55, 232.8, 292.5), "z+", 6.0,  "Kamoer pump A + B motors (DC-5)", "4-cond JST XH"),
    _p("J14-usb",       "pcba", "electrical", (196.8, 218.3, 292.5),  "z+", 9.0,  "USB-C programming port (bench only, no loom)", "USB-C receptacle"),
    # 12 V distribution block (DIN) — the three runs that land on it, on its top face. Terminal
    # positions along the block are provisional (the block's internal poles aren't modeled).
    _p("in",       "dc-dist", "electrical", (34.0, 278.0, 283.0), "z+", 6.0, "PSU 12 V output (DC-1)", "16 AWG; PROVISIONAL terminal position"),
    _p("to-board", "dc-dist", "electrical", (49.0, 278.0, 283.0), "z+", 5.0, "board J10 12 V inlet (DC-4)", "16 AWG; PROVISIONAL terminal position"),
    _p("to-relay2","dc-dist", "electrical", (64.0, 278.0, 283.0), "z+", 6.0, "Teyleten relay #2 contact — SeaFlo gate (DC-2)", "16 AWG; PROVISIONAL terminal position"),
    # Power assembly (tray + Mean Well PSU + 2 Teyleten relays + AC-dist block + ground bus) — the
    # connection groups entering/leaving the tray. Terminal positions are provisional (the device
    # terminals inside the tray aren't individually modeled).
    _p("ac-in",           "power-tray", "electrical", (30.0, 185.0, 290.0), "y-", 8.0, "C14 mains inlet — H+N+G (AC-1)", "16 AWG mains; PROVISIONAL"),
    _p("compressor-feed", "power-tray", "electrical", (175.0, 220.0, 290.0), "x+", 8.0, "compressor terminal block — switched-H + N + G through the shroud grommet (AC-4/5/6)", "16 AWG; PROVISIONAL"),
    _p("dc-out",          "power-tray", "electrical", (100.0, 258.9, 290.0), "y+", 6.0, "dc-dist 12 V block (DC-1)", "16 AWG; PROVISIONAL"),
    _p("relay-ctrl",      "power-tray", "electrical", (130.0, 185.0, 290.0), "y-", 6.0, "board J5 RELAYS control loom (LV-1/2/3)", "4-cond; PROVISIONAL"),
]


# Components that carry NO tube or wire connector at all — a passive body, located trivially
# once declared connector-free. The drip pan is a catch basin: the Multiplex vent drips INTO it
# (that penetration is the Multiplex's port, not the pan's), and it drains nowhere. Declaring the
# absence is the honest analogue of declaring a position — never a silent gap, and it lets the
# located axis reach 100% without inventing a port. A name here must own no PORTS entry (asserted
# in ports_audit); if the pan ever gains a drain, move it out and give it that port.
PASSIVE_NO_PORTS = frozenset({"drip-pan"})


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
        return _on_bbox_surface(pos, solid.BoundingBox(), tol)
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(*pos)).Vertex()
    dss = BRepExtrema_DistShapeShape(v, shell)
    dss.Perform()
    if not dss.IsDone():
        return _on_bbox_surface(pos, solid.BoundingBox(), tol)
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
    """Exact min distance between two solids (0 if touching/overlapping)."""
    if not _HAVE_EXACT:
        return _bbox_gap(a.BoundingBox(), b.BoundingBox())
    dss = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    return dss.Value() if dss.IsDone() else _bbox_gap(a.BoundingBox(), b.BoundingBox())


# ── Shape (the shaped axis) — the boxes a component really occupies ─────────────────────────
# A component is a set of bodies, and its boxes are their boxes: one per solid it is built from,
# following the part's own construction. The single box drawn around all of them is a different
# object — the compressor shroud's holds twenty times the shroud's material, a flavor pump's holds
# three times its own, and an elbow's is mostly the air in the corner of the L. `box_fill` is how
# much of the boxes is material: at 1.0 they are the part, and the lower it runs the less a box
# stands in for the shape and the more only the solid will answer (`_solid_gap`, `_on_surface`).
def component_boxes(shape) -> list:
    """One axis-aligned box per solid the component is built from."""
    return [s.BoundingBox() for s in shape.Solids()]


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
    bbs = {n: solids[n].BoundingBox() for n in names}
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if _bbox_gap(bbs[a], bbs[b]) > 0:
                continue
            v = solids[a].intersect(solids[b]).Volume()
            if v > CLASH_TOL:
                out.append((a, b, v))
    for hn, hs in pieces.items():
        hbb = hs.BoundingBox()
        for n in names:
            if _bbox_gap(hbb, bbs[n]) > 0:
                continue
            v = hs.intersect(solids[n]).Volume()
            if v > CLASH_TOL:
                out.append((hn, n, v))
    return out


def part_clearances(solids: dict) -> list[tuple[str, str, float, bool]]:
    """Content pairs closer than REPORT_NEAR, as (a, b, gap, allowed) sorted tightest
    first. `allowed` marks a declared intentional contact (TOUCHING_OK). Part-to-wall is
    excluded on purpose — parts seat against walls by design; overlap there is the
    pack-closes gate's job, not clearance."""
    names = list(solids)
    bbs = {n: solids[n].BoundingBox() for n in names}
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
        b = s.BoundingBox()
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
        return " ".join(f"{f} {g:.1f}" + ("" if ok else f"(>{mx:g})") for f, g, mx, ok in cks)
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

    # routed — DEFERRED: every fluid + refrigerant + electrical connection a real 3D path.
    import _lines                                  # deferred: _lines reads PORTS back out of here
    conns = load_connections()
    fluid = sum(1 for c in conns if c.kind == "fluid")
    wire = sum(1 for c in conns if c.kind == "wire")
    refrig = sum(1 for c in conns if c.kind == "refrigerant")
    routed_done = sum(1 for c in conns if c.routed)
    routed = _pct(routed_done, len(conns))
    routed_detail = [f"{fluid} fluid + {refrig} refrigerant + {wire} electrical; "
                     f"{routed_done} routed — the fluid path waits on the unplaced valve-manifold "
                     f"trays, the electrical runs on the components being held"]
    for r in _lines.build_runs():
        routed_detail.append(f"✓ {r.id}: {r.frm} → {r.to} — Ø{r.diam:g} × {r.length:.1f} mm, "
                             f"{len(r.bends)} bends at R{r.bend:.1f}")
    # A blocked connection stays counted, with the measurement that blocks it.
    for c in conns:
        if c.blocked:
            routed_detail.append(f"✗ {c.id}: BLOCKED — {c.blocked}")
    goal("routed", "Connections modeled as real 3D paths (fluid + refrigerant + electrical)", routed == 100 and bool(conns),
         f"{routed}% ({routed_done}/{len(conns)})", "100%", routed_detail, active=False)

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
