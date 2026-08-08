#!/usr/bin/env python3
"""Doc-sync driver for the fluid-topology charts.

The front half is the source of truth for the arrangement.
[`manifold-layout/front_half.py`](/hardware/manifold-layout/front_half.py) places the pack,
[`_lines.py`](/hardware/manifold-layout/_lines.py) authors every run BETWEEN placed bodies and
`_routing.Run.length` measures the built centreline, and
[`manifold_layout.py`](/hardware/manifold-layout/manifold_layout.py) makes the flavour
manifold's own interior — where a segment is a butt, a fold or a quarter turn rather than a
drawn line. This driver reads all three and holds the charts to them.

Two jobs:

  1. GATE. Every edge in fluid-topology-manifold.mmd and fluid-topology-carbonator.mmd names two
     chart nodes; each node declares the anchors it stands for (`NODES`). An edge labelled
     `fluid-17` passes only if the built segment `fluid-17` starts on one of its head node's
     anchors and ends on one of its tail node's — either way round, because a segment is authored
     from whichever end its author reached first and the chart draws FLOW. Every fluid segment
     must appear exactly once, and the segments the machine BUILDS must be the segments
     fluid-topology.md's own tables name. In fluid-topology-limbs.mmd every limb box must hold
     exactly the bodies its limb chains.

  2. WRITE. The measured length onto every labelled edge, the manifold chart's `linkStyle` index
     lists off the parsed edge order, and the [value](NAME) markers in the charts' `%%` comments
     and in fluid-topology.md. Every chart's `linkStyle` lines are held to a partition of its
     edges, hand-written or not.

TWO NAMESPACES REACH ONE NODE. A run `_lines.py` draws anchors on `"<body>.<port>"` — the pack's
own placed bodies. A segment `manifold_layout.py` makes anchors on the topology's own port names,
`V-C-O` and `Y-C-1` and `P-B-I`; inside the manifold two collets meet with no body between them
to hang a port on. `NODES` carries both namespaces per node.

A mermaid file has two regions and a managed number takes a different form in each:

  * `%%` COMMENT LINES never reach the renderer, so a docgen `[value](NAME)` marker sits there
    invisible to the drawn chart. `substitute_mmd` writes them.
  * EDGE LABELS render. The label is `<route-id><br/><what the segment is>`, and this driver
    rewrites everything after the route id, keyed on the id. Same contract as a docgen marker:
    the value is in the file for a reader, the script is authoritative.

Run:  tools/cad-venv/bin/python hardware/topology/_fluid_topology_sync.py
      tools/cad-venv/bin/python hardware/topology/_fluid_topology_sync.py --check
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _p in (_repo / "tools", _repo / "hardware" / "scripts",
           _repo / "hardware" / "manifold-layout"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from docgen import substitute_md, substitute_mmd  # noqa: E402
import _lines                                     # noqa: E402
import _scorecard                                 # noqa: E402
import front_half                                 # noqa: E402
import manifold_layout as ml                      # noqa: E402

MANIFOLD = _here / "fluid-topology-manifold.mmd"
LIMBS = _here / "fluid-topology-limbs.mmd"
CARBONATOR = _here / "fluid-topology-carbonator.mmd"
TOPOLOGY = _here / "fluid-topology.md"


# ─── What the machine builds ──────────────────────────────────────────
@dataclass
class Seg:
    """One fluid segment as the machine actually makes it.

    `made` is what the chart's edge label says, and it is ONE OF `_scorecard.MADE_AS`'S NAMES.
    That table is the vocabulary: the card scores `routed` on it and this driver labels an edge
    with it, so a word spelt out again here is a word the chart and the card come to disagree
    over. `__post_init__` holds every segment to it.

    What these charts draw of it:

      `drawn`    — a run `_lines.py` authors between two placed bodies, swept and measured.
      `straight` — a lane's own straight inside the manifold, drawn and measured the same way.
      `butt`     — two collets face to face, no tube between them, 0.0 mm.
      `fold`     — one of the hinge's 180° hairpins, carrying a deck change.
      `turn`     — a quarter out of the deck plane and the step that follows it.
      `not drawn`— a mouth of the manifold study with nothing on the far end of it yet.

    The table's remaining name is `mate`, a joint made up across a plane its two bodies already
    share. That is how the refrigerant loop is built, and these charts draw fluid.
    """

    id: str
    ends: tuple           # one or two anchor names; one means the far end is not placed
    made: str
    length: float = None  # mm of stock the segment cuts; None where nothing is drawn
    corners: int = 0

    def __post_init__(self):
        if self.made not in _scorecard.MADE_AS:
            raise ValueError(
                f"{self.id} is made {self.made!r}, which is no name in _scorecard.MADE_AS "
                f"({', '.join(sorted(_scorecard.MADE_AS))}). That table is the one vocabulary "
                f"the card and these charts share — a label written outside it is an edge the "
                f"chart draws and the card's `routed` axis cannot count.")

    @property
    def label(self) -> str:
        return f"{self.id}<br/>{self.length:.1f} mm" if self.length else \
            f"{self.id}<br/>{self.made}"


def _interior(how: str) -> tuple:
    """How `manifold_layout` makes one of its own interior segments, as `(kind, mm, corners)`.

    THE KIND IS `_scorecard.made_of`'S. `manifold_layout.SEGMENTS` already says how the pack
    makes each interior connection, the card reads that column to score `routed`, and this
    reads it to label an edge — so classifying it twice is how the chart and the card come to
    disagree about the same segment. What is this driver's own is the mm and the corners, off
    `manifold_layout`'s figures: `SPINE_LEN` the hairpin, `QUARTER_LEN` the quarter out of the
    deck plane, `SOURCE_LEN` the step that carries on from it, `RUNS` the lanes' straights."""
    kind = _scorecard.made_of(how)
    if kind == "fold":
        return (kind, ml.SPINE_LEN, 2)                       # quarter · straight · quarter
    if kind == "turn":
        return (kind, ml.QUARTER_LEN + ml.SOURCE_LEN, 3)     # the quarter, then the step's pair
    if kind == "butt":
        return (kind, 0.0, 0)
    return (kind, ml.dist(*ml.RUNS[how]), 0)                 # a lane's own straight


def segments() -> dict:
    """Every fluid segment the machine owes, keyed by route id, plus the non-flavour runs the
    front half draws through this stand.

    Three sources. `_lines.py` draws the runs between PLACED BODIES and they arrive measured.
    `manifold_layout.SEGMENTS` is the manifold's interior, where a connection is a butt or a
    bend. `manifold_layout.MOUTHS` is what leaves that study, and a mouth `_lines.py` has not
    picked up is a stub drawn one bend radius long and stopped.

    THE WHOLE FRONT HALF, NOT THE PACK. A run between two bodies the pack places is drawn by
    `_lines.build_runs`, but a run to a body SEATED IN THE BOX cannot be — the box is sized on
    the pack, so it does not exist until the pack does. `build_front_half` seats the funnel and
    then draws `_lines.build_seated_runs` off the same frames, and the hopper drain `fluid-4` is
    the one segment in this table that arrives that way. Read the pack alone and that run falls
    through to the `MOUTHS` loop and is labelled `not drawn` — a chart claiming an open mouth on
    a line the machine has already routed, and no gate here catches it, because this driver
    would be self-consistent against its own partial reading."""
    a = front_half.build_front_half()
    segs = {}
    for r in a.runs:
        segs[r.id] = Seg(r.id, (r.frm, r.to), "drawn", r.length, len(r.bends))
    for cid, frm, to, how in ml.SEGMENTS:
        made, length, corners = _interior(how)
        segs[f"fluid-{cid}"] = Seg(f"fluid-{cid}", (frm, to), made, length, corners)
    for cid, port, _what, _body, _end in ml.MOUTHS:
        if cid not in segs:
            segs[cid] = Seg(cid, (port,), "not drawn")
    return segs


def owed() -> dict:
    """The fluid segments fluid-topology.md's own tables name, id → `(from, to)` — the same read
    `_scorecard.load_connections` takes to score the front half's `routed` axis."""
    return {c.id: (c.frm, c.to) for c in _scorecard.load_connections([]) if c.kind == "fluid"}


# ─── The chart-to-machine contract ────────────────────────────────────
# Chart node id → the anchors that node stands for.

def _body(name, *ports) -> frozenset:
    return frozenset(f"{name}.{p}" for p in ports)


def _valve(v) -> frozenset:
    """A valve reached from either side of the seam: `_lines.py` anchors on the placed body's
    two collets, `manifold_layout` on the topology's own two port names."""
    return frozenset({f"valve-{v.lower()}.inlet", f"valve-{v.lower()}.outlet",
                      f"{v}-I", f"{v}-O"})


NODES = {
    # The funnel is SEATED IN THE BOX rather than placed in the pack, but it is placed: its
    # drain is an anchor like any other, and `fluid-4` is drawn off it.
    "Hopper":     _body("hopper-funnel", "drain"),
    "Split":      _body("water-split", "supply", "to-flavor", "to-vk"),
    "FlowReg":    _body("flow-regulator", "inlet", "outlet"),
    "VK":         _body("vk-solenoid", "inlet", "outlet"),
    "SuctChain":  _body("suction-chain", "tube-port", "barb-tip"),
    "ResA":       _body("foam-assembly", "reservoir-a"),
    "ResAFill":   _body("foam-assembly", "reservoir-a-fill"),
    "ResB":       _body("foam-assembly", "reservoir-b"),
    "ResBFill":   _body("foam-assembly", "reservoir-b-fill"),
    "BhA":        _body("bulkhead-flavor-a", "tube-in", "tube-out"),
    "BhB":        _body("bulkhead-flavor-b", "tube-in", "tube-out"),
    # The carbonator spine's own bodies.
    "BhW":        _body("bulkhead-water", "inboard", "outboard"),
    "BFP":        _body("asse1022-assembly", "tube-in", "tube-out", "vent-tip"),
    "DischChain": _body("discharge-chain", "tube-port", "barb-tip"),
    "PW":         _body("seaflo-pump", "suction", "discharge"),
    "GasherCO2":  _body("gasher-co2", "inlet", "outlet"),
    "WR":         _body("wr1110", "inlet", "outlet"),
    "FlowMeter":  _body("digiten-flow", "inlet", "outlet"),
    "BhCarb":     _body("bulkhead-carb", "tube-in", "tube-out"),
    "CapWater":   _body("foam-assembly", "water-in"),
    "CapCO2":     _body("foam-assembly", "co2-in"),
    "CapCarb":    _body("foam-assembly", "carb-water-out"),
}
# The manifold's own members, off the placed pack: a valve, a tee or a pump that leaves the pack
# leaves this table with it, and every edge naming it then fails.
NODES.update({f"V{v[-1]}": _valve(v) for v in _lines.VALVES})
NODES.update({f"Y{t[-1]}": frozenset(f"{t}-{i}" for i in (1, 2, 3))
              for t in ml.P if t.startswith("Y-")})
NODES.update({f"P{p[-1].upper()}": frozenset({f"P-{p[-1].upper()}-I", f"P-{p[-1].upper()}-O"})
              for p in ml.PUMPS})

# Chart nodes that stand for nothing the pack places — the hopper's spout, the far side of the
# rear panel, the customer's supply, the DERPIPE clamped through the back wall, and everything
# inside the carbonator vessel. An edge to one of these carries a route id only if the segment
# it names has just one end the machine knows, which is what a mouth with nothing on it yet is.
UNPLACED = {"Faucet", "Nozzle", "Tap", "CO2", "CO2In", "Vent", "PRVOut", "LevelSense",
            "P1", "P2", "P3", "P4", "SpargeStone", "Headspace", "Water", "Float"}

# Which limb box in fluid-topology-limbs.mmd is which of the manifold's four lanes.
LIMB_BOXES = {"LA1": "A1", "LA2": "A2", "LB1": "B1", "LB2": "B2"}

# The manifold chart's circuit colouring, and so its `linkStyle` groups: fluid-topology.md's own
# division of the segments into Shared, Channel A and Channel B.
FLUID_GROUPS = (("shared", 1, 8), ("channel-a", 9, 18), ("channel-b", 19, 28))


# ─── Reading the charts ───────────────────────────────────────────────
# One edge per line, no chaining: `A -->|"label"| B`. The link index every linkStyle names is the
# count of edges declared before it. Anything on a non-comment line that looks like an arrow and
# does not match RAISES rather than being skipped over.
_EDGE_RE = re.compile(
    r'^\s*(?P<a>\w+)\s*(?P<arrow><-->|-->|-\.->|==>)\s*'
    r'(?:\|"(?P<label>[^"]*)"\|\s*)?'
    r'(?P<b>\w+)\s*$')
_ARROWISH = re.compile(r'-->|-\.->|<-->|==>')
# A label that opens with `<route-id>` names a segment, and everything after the id is this
# driver's to write. Any other label is the chart's own prose.
_LABEL_RE = re.compile(r'^(?P<id>[a-z][a-z0-9]*-\d+)(?P<rest>.*)$', re.DOTALL)
# `linkStyle <indices> <style>`; the indices are written, the style is authored.
_LINKSTYLE_RE = re.compile(r'^(?P<lead>\s*linkStyle\s+)(?P<idx>[\d,\s]+?)(?P<style>\s+\S.*)$')
# The group a linkStyle line belongs to, declared in the comment above it.
_GROUP_RE = re.compile(r'\(group:(?P<name>[\w-]+)\)')
_SUBGRAPH_RE = re.compile(r'^\s*subgraph\s+(?P<id>\w+)\s*\["(?P<label>[^"]*)"\]\s*$')
_NODE_RE = re.compile(r'^\s*(?P<id>\w+)\s*[\[\{\(]')
_CLASS_RE = re.compile(r'^\s*class\s+(?P<ids>[\w,\s]+?)\s+(?P<name>\w+)\s*;?\s*$')


def check_comments(path: Path) -> list[str]:
    """A `%%` with nothing after it is NOT a comment. Mermaid's comment token wants text after
    the marker, so a bare `%%` falls through to the node grammar and DRAWS — a box labelled `%%`
    floating beside the chart. It is the shape a comment paragraph break wants to take, and it is
    silent: the file parses, the chart renders, and there is an extra node in it. Paragraph
    breaks in these charts are blank lines."""
    return [f"  {path.name} line {i + 1}: a bare `%%` — mermaid draws this as a node, not a "
            f"comment. Use a blank line for a paragraph break."
            for i, ln in enumerate(path.read_text().splitlines())
            if ln.strip() == "%%"]


class Edge:
    """One arrow in a chart: its two node ids, its route id (or None), and the line it sits on."""

    def __init__(self, lineno, a, b, arrow, label):
        self.lineno, self.a, self.b, self.arrow, self.label = lineno, a, b, arrow, label
        m = _LABEL_RE.match(label) if label else None
        self.rid = m.group("id") if m else None


def read_edges(path: Path) -> tuple[list[str], list[Edge]]:
    """The chart's lines, and its edges in declaration order — which is the order mermaid numbers
    links in, and so the order `linkStyle` counts."""
    lines = path.read_text().splitlines()
    edges = []
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("%%"):
            continue
        m = _EDGE_RE.match(ln)
        if m:
            edges.append(Edge(i, m.group("a"), m.group("b"), m.group("arrow"),
                              m.group("label")))
        elif _ARROWISH.search(ln):
            raise ValueError(
                f"{path.name} line {i + 1}: an edge this driver cannot read —\n"
                f"    {ln.strip()}\n"
                f"  Charts it gates carry ONE edge per line, `A -->|\"label\"| B`, with no "
                f"chaining: the link index every linkStyle names is the count of edges "
                f"before it, and a line holding two would put every later index out.")
    return lines, edges


# ─── The gate ─────────────────────────────────────────────────────────
def check_graph(edges: list[Edge], segs: dict, owes_ids: bool) -> list[str]:
    """Every edge against the segment it names. An edge passes only if the built segment's ends
    are the two nodes' own anchors — in either order, because a segment is authored from
    whichever end its author reached first and the chart draws the direction fluid moves.

    `owes_ids` says every edge between two placed bodies names a segment. The flavor manifold is
    all tube; the carbonator spine also draws made-up threads, face-to-face collets and the
    vessel's own interior as edges, and none of those is a run."""
    bad = []
    seen = {}

    for e in edges:
        for node in (e.a, e.b):
            if node not in NODES and node not in UNPLACED:
                bad.append(f"  line {e.lineno + 1}: node {node!r} is in no table — add it to "
                           f"NODES with the anchors it stands for")
        if any(n not in NODES and n not in UNPLACED for n in (e.a, e.b)):
            continue

        if e.rid is None:
            if not owes_ids or e.a in UNPLACED or e.b in UNPLACED:
                continue
            bad.append(f"  line {e.lineno + 1}: {e.a} → {e.b} carries no route id, but the "
                       f"machine knows both ends — every segment between two of them has one")
            continue
        if e.rid in seen:
            bad.append(f"  line {e.lineno + 1}: {e.rid} drawn twice (also line {seen[e.rid] + 1})")
            continue
        seen[e.rid] = e.lineno

        seg = segs.get(e.rid)
        if seg is None:
            bad.append(f"  line {e.lineno + 1}: {e.rid} is drawn here and the machine builds "
                       f"nothing by that name")
            continue
        held = [NODES.get(e.a, frozenset()), NODES.get(e.b, frozenset())]
        if len(seg.ends) == 1:
            # A mouth: one end the machine knows, and on the other a node it does not place.
            if not any(seg.ends[0] in h for h in held):
                bad.append(f"  line {e.lineno + 1}: {e.rid} is drawn {e.a} → {e.b}; the machine "
                           f"builds it off {seg.ends[0]} and neither node holds that")
            elif not (e.a in UNPLACED or e.b in UNPLACED):
                bad.append(f"  line {e.lineno + 1}: {e.rid} is drawn between two placed nodes "
                           f"and the machine draws only its {seg.ends[0]} end")
            continue
        if e.a in UNPLACED or e.b in UNPLACED:
            bad.append(f"  line {e.lineno + 1}: {e.rid} reaches {e.a} → {e.b}, and the machine "
                       f"places no body for one of them, yet builds the segment end to end")
            continue
        frm, to = seg.ends
        if not (frm in held[0] and to in held[1]) and not (frm in held[1] and to in held[0]):
            bad.append(f"  line {e.lineno + 1}: {e.rid} is drawn {e.a} → {e.b}; the machine "
                       f"builds it {frm} → {to}")
    return bad


def check_linkstyle_cover(path: Path, lines: list[str], edges: list[Edge]) -> list[str]:
    """Every edge named by exactly one `linkStyle` index, and no index past the last edge. An
    index list is a COUNT of the edges declared before it, so an edge inserted by hand puts every
    later number out and the chart draws a line in the wrong circuit's colour."""
    seen, bad = {}, []
    for i, ln in enumerate(lines):
        m = _LINKSTYLE_RE.match(ln) if not ln.lstrip().startswith("%%") else None
        if not m:
            continue
        for n in (int(t) for t in m.group("idx").split(",") if t.strip()):
            if n >= len(edges):
                bad.append(f"  {path.name} line {i + 1}: linkStyle names edge {n} and the chart "
                           f"draws {len(edges)}")
            elif n in seen:
                bad.append(f"  {path.name} line {i + 1}: edge {n} is styled twice (also line "
                           f"{seen[n] + 1})")
            else:
                seen[n] = i
    for n in range(len(edges)):
        if n not in seen:
            e = edges[n]
            bad.append(f"  {path.name} line {e.lineno + 1}: edge {n} ({e.a} → {e.b}) is in no "
                       f"linkStyle — it renders in the default colour")
    return bad


def check_inventory(edges: list[Edge], segs: dict) -> list[str]:
    """The three lists held to one: what fluid-topology.md's tables NAME, what the machine
    BUILDS, and what the chart DRAWS."""
    named, built = set(owed()), {k for k in segs if k.startswith("fluid-")}
    drawn = {e.rid for e in edges if e.rid}
    bad = []
    for miss in sorted(named - built, key=_seg_no):
        bad.append(f"  {miss} has a row in fluid-topology.md and the machine builds nothing "
                   f"by that name")
    for miss in sorted(built - named, key=_seg_no):
        bad.append(f"  {miss} is built by the machine and fluid-topology.md's tables have no "
                   f"row for it")
    for miss in sorted(built - drawn, key=_seg_no):
        bad.append(f"  {miss} is built by the machine and the chart does not draw it")
    return bad


def limb_members() -> dict:
    """Limb → the bodies chained on it, off `manifold_layout.LIMBS`. A limb is one LANE: a line
    of valves and tees butted collet to collet, hinged in the middle, half of it folded up onto
    the deck above."""
    return {name: {body for body, _arg in limb["chain"]}
            for name, limb in ml.LIMBS.items()}


def check_boxes(path: Path, strict: bool) -> list[str]:
    """Every limb box holds exactly the bodies its limb chains, and its TITLE names that limb.
    The subgraph id is this driver's handle; the title is what the chart draws, so both are held
    to the same limb.

    `strict` says every subgraph in the file must be a limb. The limbs chart is nothing but
    limbs; the manifold chart also boxes the regions the machine's own bodies stand in, and those
    are prose, not carriers."""
    limbs = limb_members()
    bad, stack = [], []

    for i, ln in enumerate(path.read_text().splitlines()):
        if ln.lstrip().startswith("%%"):
            continue
        m = _SUBGRAPH_RE.match(ln)
        if m:
            stack.append((m.group("id"), m.group("label"), i, set()))
            continue
        if ln.strip() == "end":
            if not stack:
                bad.append(f"  {path.name} line {i + 1}: an `end` closing no subgraph")
                continue
            box, label, at, held = stack.pop()
            limb = LIMB_BOXES.get(box)
            if limb is None:
                if strict:
                    bad.append(f"  {path.name} line {at + 1}: subgraph {box!r} is in no table — "
                               f"add it to LIMB_BOXES, or take it out of a chart that is nothing "
                               f"but limbs")
                continue
            if limb not in limbs:
                bad.append(f"  {path.name} line {at + 1}: {box} — the manifold chains no "
                           f"{limb!r}")
            elif held != limbs[limb]:
                bad.append(f"  {path.name} line {at + 1}: {box} ({limb}) draws "
                           f"{sorted(held) or '—'}; the limb chains {sorted(limbs[limb])}")
            if not label.startswith(limb):
                bad.append(f"  {path.name} line {at + 1}: {box} is drawn {label!r} and holds "
                           f"limb {limb!r} — the title a reader sees must name the limb")
            continue
        n = _NODE_RE.match(ln)
        if stack and n and n.group("id") in NODES:
            stack[-1][3].add(_body_of(n.group("id")))

    if stack:
        bad.append(f"  {path.name}: {len(stack)} subgraph(s) never closed")

    drawn = set(re.findall(r'^\s*subgraph\s+(\w+)\s*\[', path.read_text(), re.M))
    for miss in sorted(set(LIMB_BOXES) - drawn):
        bad.append(f"  {path.name}: limb {LIMB_BOXES[miss]} is chained in the manifold and has "
                   f"no box in the chart")
    for limb in sorted(set(limbs) - set(LIMB_BOXES.values())):
        bad.append(f"  the manifold chains limb {limb!r} and no chart box claims it — add it to "
                   f"LIMB_BOXES and draw it")
    return bad


def _body_of(node: str) -> str:
    """A chart node id back to the manifold's own body name: `VA` → `V-A`, `YC` → `Y-C`."""
    return f"{node[0]}-{node[1:]}" if len(node) == 2 else node


def check_classes(path: Path, want: dict) -> list[str]:
    """Each `class` line's membership against the pack. The two the charts carry are the placed
    manifold's own: which nodes are TEES, and which stand on the folded deck."""
    bad = []
    for i, ln in enumerate(path.read_text().splitlines()):
        m = _CLASS_RE.match(ln) if not ln.lstrip().startswith("%%") else None
        if not m or m.group("name") not in want:
            continue
        drawn = {n.strip() for n in m.group("ids").split(",") if n.strip()}
        if drawn != want[m.group("name")]:
            bad.append(f"  {path.name} line {i + 1}: class {m.group('name')} draws "
                       f"{sorted(drawn)}; the pack has {sorted(want[m.group('name')])}")
    for name in want:
        if not re.search(r'^\s*class\s+[\w,\s]+\s+%s\s*;?\s*$' % name,
                         path.read_text(), re.M):
            bad.append(f"  {path.name}: nothing is classed {name!r}, and the pack has "
                       f"{sorted(want[name])}")
    return bad


def class_members() -> dict:
    """The two classed sets, off the placed manifold: its junction fittings, and the bodies the
    fold carries onto the upper deck."""
    return {
        "tee": {f"Y{t[-1]}" for t in ml.P if t.startswith("Y-")},
        "upper": {f"{n[0]}{n[2:]}" for n, p in ml.P.items() if p["fold"]},
    }


# ─── Writing ──────────────────────────────────────────────────────────
def _seg_no(rid: str) -> int:
    return int(rid.rsplit("-", 1)[1])


def edge_group(e: Edge) -> str:
    """Which linkStyle group an edge belongs to — derived from its route id, so a segment moved
    between channels moves its colour with it."""
    if e.rid is None:
        return "outside"
    if not e.rid.startswith("fluid-"):
        return "carbonator"
    n = _seg_no(e.rid)
    for name, lo, hi in FLUID_GROUPS:
        if lo <= n <= hi:
            return name
    raise ValueError(f"{e.rid}: outside every group in FLUID_GROUPS")


def rewrite_labels(lines: list[str], edges: list[Edge], segs: dict) -> None:
    """What each labelled edge's segment is, onto the label, in place."""
    for e in edges:
        if e.rid is None:
            continue
        want = segs[e.rid].label
        if e.label != want:
            lines[e.lineno] = lines[e.lineno].replace(f'|"{e.label}"|', f'|"{want}"|')
            e.label = want


def rewrite_linkstyles(lines: list[str], edges: list[Edge]) -> list[str]:
    """The `linkStyle` index lists, off the parsed edge order. Mermaid numbers links by
    declaration order, so these indices are a COUNT and not an authorship — insert one edge by
    hand and every later number is wrong. The style that follows each index list stays the
    chart's own; only the numbers are written."""
    groups: dict[str, list[int]] = {}
    for i, e in enumerate(edges):
        groups.setdefault(edge_group(e), []).append(i)

    problems, pending, written = [], None, set()
    for i, ln in enumerate(lines):
        g = _GROUP_RE.search(ln) if ln.lstrip().startswith("%%") else None
        if g:
            pending = g.group("name")
            continue
        m = _LINKSTYLE_RE.match(ln)
        if not m:
            continue
        if pending is None:
            problems.append(f"  line {i + 1}: a linkStyle with no (group:NAME) in the comment "
                            f"above it — this driver writes its indices and cannot tell which "
                            f"edges it is for")
            continue
        idx = groups.get(pending)
        if idx is None:
            problems.append(f"  line {i + 1}: group {pending!r} matches no edge in the chart")
        else:
            lines[i] = f"{m.group('lead')}{','.join(str(n) for n in idx)}{m.group('style')}"
            written.add(pending)
        pending = None
    for g in sorted(set(groups) - written):
        problems.append(f"  {len(groups[g])} edges are in group {g!r} and no linkStyle claims "
                        f"it — they render in the default colour")
    return problems


def manifold_variables(segs: dict) -> dict:
    """The chart's own prose numbers, off the same built segments its edges carry. The total is
    TUBE and the count is SEGMENTS — most of this manifold is butted collet to collet."""
    fluid = [s for k, s in segs.items() if k.startswith("fluid-")]
    cut = [s for s in fluid if s.length]
    longest = max(cut, key=lambda s: s.length)
    return {
        "SEGMENT_COUNT": f"{len(fluid)}",
        "DRAWN_COUNT":   f"{sum(1 for s in fluid if s.made == 'drawn')}",
        "BUTT_COUNT":    f"{sum(1 for s in fluid if s.made == 'butt')}",
        "OPEN_COUNT":    f"{sum(1 for s in fluid if s.made == 'not drawn')}",
        "FLUID_TOTAL":   f"{sum(s.length for s in cut):.1f} mm",
        "FLUID_BENDS":   f"{sum(s.corners for s in fluid)}",
        "LONGEST_ID":    longest.id,
        "LONGEST_LEN":   f"{longest.length:.1f} mm",
    }


def limb_variables() -> dict:
    """The manifold's carrier inventory, counted off the placed pack."""
    limbs = limb_members()
    valves = {v for m in limbs.values() for v in m if v.startswith("V-")}
    tees = {t for m in limbs.values() for t in m if t.startswith("Y-")}
    return {
        "LIMB_COUNT":   f"{len(limbs)}",
        "LIMB_VALVES":  f"{len(valves)}",
        "TEE_COUNT":    f"{len(tees)}",
        "UPPER_COUNT":  f"{sum(1 for p in ml.P.values() if p['fold'])}",
        "LOWER_COUNT":  f"{sum(1 for p in ml.P.values() if not p['fold'])}",
        "PUMP_COUNT":   f"{len(ml.PUMPS)}",
    }


# ─── Driver ───────────────────────────────────────────────────────────
def main() -> int:
    check = "--check" in sys.argv

    segs = segments()

    problems = []
    for chart in (MANIFOLD, LIMBS, CARBONATOR):
        problems += check_comments(chart)
    lines, edges = read_edges(MANIFOLD)
    carb_lines, carb_edges = read_edges(CARBONATOR)
    problems += check_graph(edges, segs, owes_ids=True)
    problems += check_graph(carb_edges, segs, owes_ids=False)
    problems += check_inventory(edges, segs)
    problems += check_boxes(MANIFOLD, strict=False)
    problems += check_boxes(LIMBS, strict=True)
    problems += check_classes(MANIFOLD, class_members())
    problems += check_classes(LIMBS, class_members())
    problems += check_linkstyle_cover(CARBONATOR, carb_lines, carb_edges)
    problems += check_linkstyle_cover(LIMBS, *read_edges(LIMBS))
    if problems:
        print("fluid-topology charts disagree with the front half:")
        print("\n".join(problems))
        return 1

    before, carb_before = list(lines), list(carb_lines)
    rewrite_labels(lines, edges, segs)
    rewrite_labels(carb_lines, carb_edges, segs)
    problems += rewrite_linkstyles(lines, edges)
    problems += check_linkstyle_cover(MANIFOLD, lines, edges)
    if problems:
        print("fluid-topology-manifold.mmd linkStyle:")
        print("\n".join(problems))
        return 1

    mf_vars, limb_vars = manifold_variables(segs), limb_variables()

    if check:
        stale = [f"  {p.name} line {i + 1}: {b.strip()}"
                 for p, was, now in ((MANIFOLD, before, lines), (CARBONATOR, carb_before,
                                                                 carb_lines))
                 for i, (b, a) in enumerate(zip(was, now)) if b != a]
        stale += _stale_markers(MANIFOLD, mf_vars)
        stale += _stale_markers(LIMBS, limb_vars)
        stale += _stale_markers(TOPOLOGY, limb_vars)
        if stale:
            print("fluid-topology charts are stale — run _fluid_topology_sync.py:")
            print("\n".join(stale))
            return 1
        print("fluid-topology ✓")
        return 0

    if lines != before:
        MANIFOLD.write_text("\n".join(lines) + "\n")
    if carb_lines != carb_before:
        CARBONATOR.write_text("\n".join(carb_lines) + "\n")
    substitute_mmd(MANIFOLD, mf_vars, {k: 1 for k in mf_vars})
    substitute_mmd(LIMBS, limb_vars, {k: 1 for k in limb_vars})
    substitute_md(TOPOLOGY, limb_vars, {k: 1 for k in limb_vars})

    fluid = [s for k, s in sorted(segs.items(), key=lambda kv: _seg_no(kv[0]))
             if k.startswith("fluid-")]
    for s in fluid:
        length = "        —" if s.length is None else f"{s.length:7.1f} mm"
        print(f"  {s.id:<9} {length}  {s.corners} corners  {s.made:<9} "
              f"{' → '.join(s.ends)}")
    print(f"  {'TOTAL':<9} {sum(s.length or 0.0 for s in fluid):7.1f} mm of tube over "
          f"{len(fluid)} segments")
    print(f"  limbs {limb_vars['LIMB_COUNT']}, valves {limb_vars['LIMB_VALVES']}, "
          f"tees {limb_vars['TEE_COUNT']}, pumps {limb_vars['PUMP_COUNT']} "
          f"({limb_vars['UPPER_COUNT']} bodies folded up, {limb_vars['LOWER_COUNT']} down)")
    return 0


def _stale_markers(path: Path, variables: dict) -> list[str]:
    text = path.read_text()
    out = []
    for name, want in variables.items():
        m = re.search(r"\[([^\]]*)\]\(%s\)" % name, text)
        if m and m.group(1) != str(want):
            out.append(f"  {path.name}: [{m.group(1)}]({name}) should be [{want}]({name})")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
