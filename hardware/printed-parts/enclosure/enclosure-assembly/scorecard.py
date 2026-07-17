"""The enclosure's requirements as a single pass/fail scorecard — the one place the
appliance's printable + assembleable rules are enumerated as executable checks,
computed from the placed geometry (the same solids the pack check already builds).
Printed at the tail of every `enclosure_assembly.py` run, so the agent and a human
read the same verdict from the same shapes — a result no one can narrate around.

Modeled on the board's `hardware/pcb/pcba/scorecard.ts`. Two kinds of check:

  - GATE — a manufacturability requirement that must hold to PRINT + ASSEMBLE the box
           as it stands. A failing gate is a box you cannot build; it fails the run.
  - GOAL — the realization work this whole effort exists to drive, reported as a
           `score` (0..100), not a gate — the box still builds while it converts.

The board had ONE goal (take every connection off the autorouter onto deliberate hand
copper). The enclosure has THREE axes, one per thing every component owes:

    shaped — real geometry, not a placeholder box/cylinder.
    routed — every connection a real 3D path (bend radius, length, clearance),
             not just two endpoints and an external graph.
    held   — a printed holder that fastens the component to the enclosure (a few
             bosses + screws, or a tray-with-bosses that itself fastens) — not a
             free solid resting in a collision-checked void.

The score is by AUTHORSHIP, not by "it doesn't collide": a bounding box that happens
not to overlap is the enclosure's version of the autorouter's accidentally-clean net —
crediting it would count the box-thinking this effort exists to remove as progress.
So `shaped`/`held` are read from the declared COMPONENTS registry (what has actually
been modeled/engineered), and `routed` from the fluid topology (a segment counts only
once a real path exists). Prose for the why — and the lessons — is in requirements.md.
"""

from __future__ import annotations

import re
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
# become real STEP/engineered parts, flip `kind` — and the score moves.
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


# ── Connections (the routed axis) — read from the fluid topology ─────────────
@dataclass
class Connection:
    num: int
    frm: str
    to: str
    routed: bool = False   # a real 3D path exists (v1: none do)


def load_connections() -> list[Connection]:
    """The tube segments the box must route, parsed from fluid-topology.md's segment
    tables (`| N | From | To | ... |`). A segment counts as routed only once a real 3D
    path is modeled — none are today, and they live in the still-deferred valve-manifold
    trays, so this axis is both 0% and visibly blocked on that deferral."""
    conns: list[Connection] = []
    if not _TOPOLOGY.is_file():
        return conns
    row = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
    for line in _TOPOLOGY.read_text().splitlines():
        m = row.match(line)
        if m:
            conns.append(Connection(int(m.group(1)), m.group(2).strip(), m.group(3).strip()))
    return conns


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


@dataclass
class Scorecard:
    checks: list
    gates_pass: bool
    shaped: int
    routed: int
    held: int


def _pct(done: int, total: int) -> int:
    return 100 if total == 0 else round(100 * done / total)


def build_scorecard(solids: dict, pieces: dict, bed: tuple[float, float, float]) -> Scorecard:
    reg = {c.name: c for c in COMPONENTS}
    checks: list[Check] = []

    def gate(cid, label, ok, value, target, detail=None):
        checks.append(Check(cid, label, "gate", "pass" if ok else "fail", value, target, (detail or [])[:DETAIL_MAX]))

    def goal(cid, label, done, value, target, detail=None):
        checks.append(Check(cid, label, "goal", "pass" if done else "warn", value, target, (detail or [])[:DETAIL_MAX]))

    # ── GATES — must hold to print + assemble what is placed ──
    # Coverage: the registry must describe exactly the placed set, or the goal counts
    # below are measured against the wrong universe.
    placed = set(solids)
    declared = set(reg)
    undeclared = sorted(placed - declared)
    unplaced = sorted(declared - placed)
    gate("coverage", "Every placed part declared in the registry", not undeclared and not unplaced,
         f"{len(placed & declared)}/{len(placed)} placed declared", "all declared",
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

    # ── GOALS — the three realization axes, scored by authorship ──
    total = len(COMPONENTS)
    real = [c for c in COMPONENTS if c.is_real]
    shaped = _pct(len(real), total)
    goal("shaped", "Components modeled as real geometry (not a placeholder box)", shaped == 100,
         f"{shaped}%", "100%",
         [f"{c.name}: still a {c.kind} — {c.note}" for c in COMPONENTS if not c.is_real])

    conns = load_connections()
    routed_done = sum(1 for c in conns if c.routed)
    routed = _pct(routed_done, len(conns))
    goal("routed", "Connections modeled as real 3D paths (not endpoints + a graph)", routed == 100 and bool(conns),
         f"{routed}% ({routed_done}/{len(conns)})", "100%",
         ([f"seg {c.num}: {c.frm} → {c.to}" for c in conns if not c.routed][:DETAIL_MAX - 1]
          + ["(all 28 live in the deferred valve-manifold trays — blocked until those are placed)"]) if conns
         else ["fluid-topology.md not found — routed denominator unknown"])

    held_done = [c for c in COMPONENTS if c.is_held]
    held = _pct(len(held_done), total)
    goal("held", "Components in a printed holder fastened to the enclosure", held == 100,
         f"{held}% ({len(held_done)}/{total})", "100%",
         [f"{c.name}: {c.held} — {c.note}" for c in COMPONENTS if c.is_held][:6]
         + [f"{c.name}: UNHELD — {c.note}" for c in COMPONENTS if not c.is_held])

    gates_pass = all(c.status == "pass" for c in checks if c.kind == "gate")
    return Scorecard(checks, gates_pass, shaped, routed, held)


def format_scorecard(sc: Scorecard) -> str:
    mark = {"pass": "✓", "fail": "✗", "warn": "•"}
    gates = [c for c in sc.checks if c.kind == "gate"]
    goals = [c for c in sc.checks if c.kind == "goal"]
    passed = sum(1 for c in gates if c.status == "pass")
    w = max(len(c.label) for c in sc.checks)
    rows = []

    def line(c: Check):
        rows.append(f"  {mark[c.status]} {c.label.ljust(w)}  {c.value}  (want {c.target})")
        for d in c.detail:
            rows.append(f"      – {d}")

    rows.append("── enclosure scorecard " + "─" * 30)
    rows.append(f"GATES (printable + assembleable)   {passed}/{len(gates)} pass"
                + ("" if sc.gates_pass else "   ✗ NOT BUILD-READY"))
    for c in gates:
        line(c)
    done = sc.gates_pass and sc.shaped == 100 and sc.routed == 100 and sc.held == 100
    rows.append(f"GOAL (100% realized)   shaped {sc.shaped}% · routed {sc.routed}% · held {sc.held}%"
                + ("   ✓ DONE" if done else ""))
    for c in goals:
        line(c)
    rows.append("─" * 53)
    return "\n".join(rows)
