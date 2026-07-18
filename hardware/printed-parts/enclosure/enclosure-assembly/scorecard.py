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
copper). The enclosure has FOUR axes, one per thing every component owes — and today
only the first two are the focus (the other two render, dimmed, but are not yet worked):

    placed — FOCUS. Placement criteria are DEFINED in code (expected face-to-datum
             measurements) and currently HELD. "Foam is against the back-bottom",
             with "against" pinned to numbers the scorecard measures.
    shaped — FOCUS. Real geometry, not a placeholder box/cylinder.
    routed — deferred. Every connection (fluid segment + electrical run) a real 3D
             path (bend radius, length, clearance), not endpoints + an external graph.
    held   — deferred. A printed holder that fastens the component to the enclosure (a
             few bosses + screws, or a tray-with-bosses that itself fastens) — not a
             free solid resting in a collision-checked void.

placed + shaped are driven to 100% first; routed + held wait behind them (rendered gray).
The score is by AUTHORSHIP, not by "it doesn't collide": a bounding box that happens not
to overlap is the enclosure's version of the autorouter's accidentally-clean net —
crediting it would count the box-thinking this effort exists to remove as progress. So
`shaped`/`held` are read from the declared COMPONENTS registry, `placed` from measured
face-to-datum rules that must be authored per component, and `routed` from the fluid +
wiring topologies (a connection counts only once a real path exists). Prose for the why —
and the lessons — is in requirements.md.
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
    _c("mq6-sensor",        "placeholder", True,  "none", "floor gas sensor; no mount"),
    # Water deck
    _c("drip-pan",          "placeholder", False, "none", "printed pan, no CAD yet — dims estimated, part+design TBD (enclosure-mechanical Open #4)"),
    _c("moisture-sensor",   "placeholder", True,  "none", "Shutao probe plate; lies in the pan, unfastened"),
    _c("multiplex",         "placeholder", True,  "none", "ASSE 1022 backflow preventer; floats over the pan, no mount"),
    _c("seaflo-pump",       "placeholder", True,  "none", "diaphragm pump; feet splay to ~98, no mount modeled"),
    _c("gasher-water",      "placeholder", True,  "none", "outlet check valve; rests on the seaflo top, unfastened"),
    _c("digiten-flow",      "real",        True,  "none", "flow sensor; rests on the seaflo top, unfastened"),
    # CO2 chain
    _c("gasher-co2",        "placeholder", True,  "none", "CO2 check valve; on the inlet chain, unfastened"),
    _c("wr1110",            "placeholder", True,  "none", "secondary regulator; bracket geometry TBD (front-panel README)"),
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
    _c("co2-inlet",         "placeholder", True,  "wall-capture", "DERPIPE PTC: front-wall hole + its own 1/4\" NPT thread"),
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
    routed: bool = False   # a real 3D path exists (today: none do)


def load_connections() -> list[Connection]:
    """Every connection the box must route: the fluid tube segments (fluid-topology.md,
    `| N | From | To |`) and the electrical runs (ac-wiring-schedule.md, `| AC/DC/SIG/LV-N
    | From | To |`). A connection counts as routed only once a real 3D path is modeled —
    none are today; the fluid segments live in the still-unplaced valve-manifold trays."""
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
    shaped: int
    routed: int
    held: int


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

    # ── GOALS — four realization axes. placed + shaped are the focus (rendered live);
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

    # shaped — FOCUS: real geometry, not a placeholder box/cylinder.
    real = [c for c in COMPONENTS if c.is_real]
    shaped = _pct(len(real), total)
    goal("shaped", "Components modeled as real geometry (not a placeholder box)", shaped == 100,
         f"{shaped}% ({len(real)}/{total})", "100%",
         [f"{c.name}: still a {c.kind} — {c.note}" for c in COMPONENTS if not c.is_real], active=True)

    # routed — DEFERRED: every fluid segment + electrical run a real 3D path.
    conns = load_connections()
    fluid = sum(1 for c in conns if c.kind == "fluid")
    wire = sum(1 for c in conns if c.kind == "wire")
    routed_done = sum(1 for c in conns if c.routed)
    routed = _pct(routed_done, len(conns))
    goal("routed", "Connections modeled as real 3D paths (fluid + electrical)", routed == 100 and bool(conns),
         f"{routed}% ({routed_done}/{len(conns)})", "100%",
         [f"{fluid} fluid segments + {wire} electrical runs, none routed — the fluid path waits on the unplaced valve-manifold trays"],
         active=False)

    # held — DEFERRED: a printed holder that fastens each component to the enclosure.
    held_done = [c for c in COMPONENTS if c.is_held]
    held = _pct(len(held_done), total)
    goal("held", "Components in a printed holder fastened to the enclosure", held == 100,
         f"{held}% ({len(held_done)}/{total})", "100%",
         [f"{len(held_done)} held (through-wall bodies + display); {total - len(held_done)} loose internal parts unheld"],
         active=False)

    gates_pass = all(c.status == "pass" for c in checks if c.kind == "gate")
    return Scorecard(checks, gates_pass, placed_pct, shaped, routed, held)


def scorecard_dict(sc: Scorecard) -> dict:
    """The verdict as a JSON-serializable dict — the web sidecar written next to
    enclosure-assembly.step (enclosure-assembly.scorecard.json). This is the SAME `sc`
    the terminal prints, so the build and the viewer read one verdict, not two. Shape
    pinned by web/contracts/scorecard-sidecar.js and its conformance test."""
    return {
        "gatesPass": sc.gates_pass,
        "placed": sc.placed,
        "shaped": sc.shaped,
        "routed": sc.routed,
        "held": sc.held,
        "checks": [
            {"id": c.id, "label": c.label, "kind": c.kind, "status": c.status,
             "value": c.value, "target": c.target, "detail": list(c.detail), "active": c.active}
            for c in sc.checks
        ],
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

    # Goals — the two focus axes live, the two deferred axes gray.
    focus_met = sc.placed == 100 and sc.shaped == 100
    done = sc.gates_pass and focus_met and sc.routed == 100 and sc.held == 100
    tail = col("  ✓ DONE", GREEN) if done else (col("  ✓ FOCUS MET", GREEN) if focus_met else "")
    rows.append("GOAL   " + col(f"focus: placed {sc.placed}% · shaped {sc.shaped}%", GREEN if focus_met else YELLOW)
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

    for gid in ("placed", "shaped", "routed", "held"):
        render_goal(gid)

    rows.append("─" * 53)
    return "\n".join(rows)
