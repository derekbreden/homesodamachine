#!/usr/bin/env python3
"""Doc-sync driver for the fluid-topology charts.

The enclosure assembly is the source of truth for the arrangement. `_lines.py` authors
every run port to port against the placed pack, `_routing.Run.length` measures the built
centreline, and `_contents.build()` says which body seats which valve. This driver reads
all three and holds the charts to them.

Two jobs:

  1. GATE. Every edge in fluid-topology-manifold.mmd names two chart nodes; each node
     declares the placed body and the ports it stands for (`NODES`). An edge labelled
     `fluid-17` passes only if the built run `fluid-17` starts at one of its head node's
     ports and ends at one of its tail node's — either way round, because a run is
     authored from whichever end `_lines.py` reached first and the chart draws FLOW.
     Every fluid segment must appear exactly once. In fluid-topology-trays.mmd every
     tray box must hold exactly the valves its placed body declares ports for.

  2. WRITE. The measured length onto every labelled edge, the `linkStyle` index lists
     off the parsed edge order, and the [value](NAME) markers in the charts' `%%`
     comments and in fluid-topology.md.

A mermaid file has two regions and a managed number takes a different form in each:

  * `%%` COMMENT LINES never reach the renderer, so a docgen `[value](NAME)` marker sits
    there invisible to the drawn chart. `substitute_mmd` writes them.
  * EDGE LABELS render. The label is `<route-id><br/><length> mm`, and this driver
    rewrites everything after the route id, keyed on the id. Same contract as a docgen
    marker: the value is in the file for a reader, the script is authoritative.

Run:  tools/cad-venv/bin/python hardware/topology/_fluid_topology_sync.py
      tools/cad-venv/bin/python hardware/topology/_fluid_topology_sync.py --check
"""

import re
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(
    0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "enclosure-assembly"))

from docgen import substitute_md, substitute_mmd  # noqa: E402
import _contents as contents  # noqa: E402
import _lines  # noqa: E402
import scorecard  # noqa: E402

MANIFOLD = _here / "fluid-topology-manifold.mmd"
TRAYS = _here / "fluid-topology-trays.mmd"
TOPOLOGY = _here / "fluid-topology.md"


# ─── The chart-to-assembly contract ───────────────────────────────────
# Chart node id → (placed body, the port names that node stands for). This table is what
# makes the gate mean anything: without the port names, two valves on one tray would be
# interchangeable and an edge could name the wrong one and pass.
NODES = {
    "Split":  ("water-split",             ("to-flavor", "to-vk")),
    "Reg":    ("flow-regulator",          ("inlet", "outlet")),
    "Hopper": ("hopper-funnel",           ("drain",)),
    "VA":     ("source-tray-assembly",    ("V-A-I", "V-A-O")),
    "VB":     ("source-tray-assembly",    ("V-B-I", "V-B-O")),
    "VC":     ("selects-tray-assembly",   ("V-C-I", "V-C-O")),
    "VD":     ("selects-tray-assembly",   ("V-D-I", "V-D-O")),
    "VE":     ("bag-a-tray-assembly",     ("V-E-I", "V-E-O")),
    "VF":     ("bag-a-tray-assembly",     ("V-F-I", "V-F-O")),
    "VG":     ("nozzle-tray-assembly",    ("V-G-I", "V-G-O")),
    "VH":     ("bag-b-tray-assembly",     ("V-H-I", "V-H-O")),
    "VI":     ("bag-b-tray-assembly",     ("V-I-I", "V-I-O")),
    "VJ":     ("nozzle-b-tray-assembly",  ("V-J-I", "V-J-O")),
    "VK":     ("vk-tray-assembly",        ("V-K-I", "V-K-O")),
    "YA":     ("tee-y-a",                 ("Y-A-1", "Y-A-2", "Y-A-3")),
    "YB":     ("tee-y-b",                 ("Y-B-1", "Y-B-2", "Y-B-3")),
    "YC":     ("tee-y-c",                 ("Y-C-1", "Y-C-2", "Y-C-3")),
    "YD":     ("tee-y-d",                 ("Y-D-1", "Y-D-2", "Y-D-3")),
    "YE":     ("tee-y-e",                 ("Y-E-1", "Y-E-2", "Y-E-3")),
    "YF":     ("tee-y-f",                 ("Y-F-1", "Y-F-2", "Y-F-3")),
    "YG":     ("tee-y-g",                 ("Y-G-1", "Y-G-2", "Y-G-3")),
    "PA":     ("pump-a",                  ("P-A-I", "P-A-O")),
    "PB":     ("pump-b",                  ("P-B-I", "P-B-O")),
    "ResA":   ("foam-assembly",           ("reservoir-A",)),
    "ResB":   ("foam-assembly",           ("reservoir-B",)),
    "ResBFill": ("foam-assembly",         ("reservoir-b-fill",)),
    "BhA":    ("bulkhead-flavor-a",       ("tube-in",)),
    "BhB":    ("bulkhead-flavor-b",       ("tube-in",)),
    "SuctChain": ("suction-chain",        ("tube-port",)),
}

# Chart nodes that stand for nothing the pack places — the far side of the rear panel.
# No edge to one of these may carry a route id, because no run in this pack carries it.
UNPLACED = {"Faucet"}

# Which tray box in fluid-topology-trays.mmd is which placed body.
TRAY_BOXES = {
    "TSrc":  "source-tray-assembly",
    "TSel":  "selects-tray-assembly",
    "TBagA": "bag-a-tray-assembly",
    "TBagB": "bag-b-tray-assembly",
    "TNozA": "nozzle-tray-assembly",
    "TVK":   "vk-tray-assembly",
    "TNozB": "nozzle-b-tray-assembly",
}

# The manifold chart's circuit colouring, and so its `linkStyle` groups. The split is
# fluid-topology.md's own — Shared / Channel A / Channel B — because that is the one
# division of the 28 segments the topology itself makes.
FLUID_GROUPS = (("shared", 1, 8), ("channel-a", 9, 18), ("channel-b", 19, 28))


# ─── Reading the charts ───────────────────────────────────────────────
# One edge per line, no chaining: `A -->|"label"| B`. Uniform lines are what let this
# driver both gate the graph and number the linkStyle lines; a chained or multi-edge line
# would make the link index a guess. Anything on a non-comment line that looks like an
# arrow and does not match RAISES rather than being skipped over.
_EDGE_RE = re.compile(
    r'^\s*(?P<a>\w+)\s*(?P<arrow><-->|-->|-\.->)\s*'
    r'(?:\|"(?P<label>[^"]*)"\|\s*)?'
    r'(?P<b>\w+)\s*$')
_ARROWISH = re.compile(r'-->|-\.->|<-->|==>')
# A label is `<route-id>` and then anything — the anything is this driver's to write.
_LABEL_RE = re.compile(r'^(?P<id>[a-z]+-\d+)(?P<rest>.*)$', re.DOTALL)
# `linkStyle <indices> <style>`; the indices are written, the style is authored.
_LINKSTYLE_RE = re.compile(r'^(?P<lead>\s*linkStyle\s+)(?P<idx>[\d,\s]+?)(?P<style>\s+\S.*)$')
# The group a linkStyle line belongs to, declared in the comment above it.
_GROUP_RE = re.compile(r'\(group:(?P<name>[\w-]+)\)')
_SUBGRAPH_RE = re.compile(r'^\s*subgraph\s+(?P<id>\w+)\s*\["(?P<label>[^"]*)"\]\s*$')
_NODE_RE = re.compile(r'^\s*(?P<id>\w+)\s*[\[\{\(]')


def check_comments(path: Path) -> list[str]:
    """A `%%` with nothing after it is NOT a comment. Mermaid's comment token wants text
    after the marker, so a bare `%%` falls through to the node grammar and DRAWS — a box
    labelled `%%` floating beside the chart. It is the shape a comment paragraph break
    wants to take, and it is silent: the file parses, the chart renders, and there is an
    extra node in it. Paragraph breaks in these charts are blank lines."""
    return [f"  {path.name} line {i + 1}: a bare `%%` — mermaid draws this as a node, not a "
            f"comment. Use a blank line for a paragraph break."
            for i, ln in enumerate(path.read_text().splitlines())
            if ln.strip() == "%%"]


class Edge:
    """One arrow in a chart: its two node ids, its route id (or None), and the line it
    sits on."""

    def __init__(self, lineno, a, b, arrow, label):
        self.lineno, self.a, self.b, self.arrow, self.label = lineno, a, b, arrow, label
        m = _LABEL_RE.match(label) if label else None
        self.rid = m.group("id") if m else None
        if label and not m:
            raise ValueError(f"line {lineno + 1}: edge label {label!r} has no route id")


def read_edges(path: Path) -> tuple[list[str], list[Edge]]:
    """The chart's lines, and its edges in declaration order — which is the order mermaid
    numbers links in, and so the order `linkStyle` counts."""
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
def check_manifold_graph(edges: list[Edge], runs: dict) -> list[str]:
    """Every edge against the run it names. An edge passes only if the built run's two
    ends are the two nodes' own ports — in either order, because `_lines.py` authors a run
    from whichever end it reached first and the chart draws the direction fluid moves."""
    bad = []
    seen = {}

    def anchors(node):
        if node in UNPLACED:
            return None
        body, ports = NODES[node]
        return {f"{body}.{p}" for p in ports}

    for e in edges:
        for node in (e.a, e.b):
            if node not in NODES and node not in UNPLACED:
                bad.append(f"  line {e.lineno + 1}: node {node!r} is in no table — add it "
                           f"to NODES with the body and ports it stands for")
        if any(n not in NODES and n not in UNPLACED for n in (e.a, e.b)):
            continue

        if e.rid is None:
            if e.a in UNPLACED or e.b in UNPLACED:
                continue
            bad.append(f"  line {e.lineno + 1}: {e.a} → {e.b} carries no route id, but both "
                       f"ends are placed bodies — every run between two placed bodies is "
                       f"authored and has one")
            continue
        if e.a in UNPLACED or e.b in UNPLACED:
            bad.append(f"  line {e.lineno + 1}: {e.rid} reaches {e.a} → {e.b}, and the pack "
                       f"places no body for one of them — no run can carry it")
            continue
        if e.rid in seen:
            bad.append(f"  line {e.lineno + 1}: {e.rid} drawn twice (also line {seen[e.rid] + 1})")
            continue
        seen[e.rid] = e.lineno

        run = runs.get(e.rid)
        if run is None:
            bad.append(f"  line {e.lineno + 1}: {e.rid} is drawn here and authored nowhere "
                       f"in _lines.py")
            continue
        ends = (run.frm, run.to)
        if not ({run.frm} <= anchors(e.a) and {run.to} <= anchors(e.b)) and \
           not ({run.frm} <= anchors(e.b) and {run.to} <= anchors(e.a)):
            bad.append(f"  line {e.lineno + 1}: {e.rid} is drawn {e.a} → {e.b}; the pack "
                       f"routes it {ends[0]} → {ends[1]}")
    return bad


def check_manifold_coverage(edges: list[Edge], runs: dict) -> list[str]:
    """Every fluid segment exactly once. The chart says it is the complete flavor topology,
    so a segment the assembly routes and the chart omits is a hole in that claim."""
    drawn = {e.rid for e in edges if e.rid}
    owed = {r for r in runs if r.startswith("fluid-")}
    missing = sorted(owed - drawn, key=_seg_no)
    return [f"  fluid segments authored in the pack and absent from the chart: "
            f"{', '.join(missing)}"] if missing else []


def seated_valves() -> dict[str, set]:
    """Valve → the placed body that seats it, off the port table: the assembly's own answer
    to which tray a valve rides."""
    seated: dict[str, set] = {}
    for p in scorecard.ports():
        m = re.fullmatch(r"(V-[A-Z])-[IO]", p.name)
        if m:
            seated.setdefault(p.component, set()).add(m.group(1))
    return seated


def check_boxes(path: Path, strict: bool) -> list[str]:
    """Every tray box holds exactly the valves its placed body seats, and its TITLE names
    that body. The subgraph id is this driver's handle; the title is what the chart draws,
    so both are held to the same body.

    `strict` says every subgraph in the file must be a tray. The trays chart is nothing but
    trays; the manifold chart also boxes the regions the stands stand in, and those are
    prose, not carriers."""
    pack = contents.build()
    seated = seated_valves()
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
            body = TRAY_BOXES.get(box)
            if body is None:
                if strict:
                    bad.append(f"  {path.name} line {at + 1}: subgraph {box!r} is in no "
                               f"table — add it to TRAY_BOXES, or take it out of a chart "
                               f"that is nothing but trays")
                continue
            if body not in pack:
                bad.append(f"  {path.name} line {at + 1}: {box} — the pack places no {body!r}")
            elif held != seated.get(body, set()):
                bad.append(f"  {path.name} line {at + 1}: {box} ({body}) draws "
                           f"{sorted(held) or '—'}; the placed body seats "
                           f"{sorted(seated.get(body, set()))}")
            if not label.startswith(body):
                bad.append(f"  {path.name} line {at + 1}: {box} is drawn {label!r} and holds "
                           f"{body!r} — the title a reader sees must name the placed body")
            continue
        n = _NODE_RE.match(ln)
        if stack and n and n.group("id") in NODES:
            stack[-1][3].add(n.group("id").replace("V", "V-", 1))

    if stack:
        bad.append(f"  {path.name}: {len(stack)} subgraph(s) never closed")

    drawn = set(re.findall(r'^\s*subgraph\s+(\w+)\s*\[', path.read_text(), re.M))
    for miss in sorted(set(TRAY_BOXES) - drawn):
        bad.append(f"  {path.name}: {TRAY_BOXES[miss]} is placed in the pack and has no box "
                   f"in the chart")
    for body in sorted(seated):
        if body not in TRAY_BOXES.values():
            bad.append(f"  {body} seats valves {sorted(seated[body])} and no chart box "
                       f"claims it — add it to TRAY_BOXES and draw it")
    return bad


# ─── Writing ──────────────────────────────────────────────────────────
def _seg_no(rid: str) -> int:
    return int(rid.rsplit("-", 1)[1])


def edge_group(e: Edge) -> str:
    """Which linkStyle group an edge belongs to — derived from its route id, so a segment
    moved between channels moves its colour with it."""
    if e.rid is None:
        return "outside"
    if not e.rid.startswith("fluid-"):
        return "carbonator"
    n = _seg_no(e.rid)
    for name, lo, hi in FLUID_GROUPS:
        if lo <= n <= hi:
            return name
    raise ValueError(f"{e.rid}: outside every group in FLUID_GROUPS")


def rewrite_labels(lines: list[str], edges: list[Edge], runs: dict) -> None:
    """The measured length onto every labelled edge, in place."""
    for e in edges:
        if e.rid is None:
            continue
        want = f'{e.rid}<br/>{runs[e.rid].length:.1f} mm'
        if e.label != want:
            lines[e.lineno] = lines[e.lineno].replace(f'|"{e.label}"|', f'|"{want}"|')
            e.label = want


def rewrite_linkstyles(lines: list[str], edges: list[Edge]) -> list[str]:
    """The `linkStyle` index lists, off the parsed edge order. Mermaid numbers links by
    declaration order, so these indices are a COUNT and not an authorship — insert one
    edge by hand and every later number is wrong. The style that follows each index list
    stays the chart's own; only the numbers are written."""
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
            problems.append(f"  line {i + 1}: a linkStyle with no (group:NAME) in the "
                            f"comment above it — this driver writes its indices and cannot "
                            f"tell which edges it is for")
            continue
        idx = groups.get(pending)
        if idx is None:
            problems.append(f"  line {i + 1}: group {pending!r} matches no edge in the chart")
        else:
            lines[i] = f"{m.group('lead')}{','.join(str(n) for n in idx)}{m.group('style')}"
            written.add(pending)
        pending = None
    for g in sorted(set(groups) - written):
        problems.append(f"  {len(groups[g])} edges are in group {g!r} and no linkStyle "
                        f"claims it — they render in the default colour")
    return problems


def manifold_variables(runs: dict) -> dict:
    """The chart's own prose numbers, off the same built runs its edges carry."""
    fluid = {k: v for k, v in runs.items() if k.startswith("fluid-")}
    longest = max(fluid.values(), key=lambda r: r.length)
    shortest = min(fluid.values(), key=lambda r: r.length)
    return {
        "FLUID_TOTAL":  f"{sum(r.length for r in fluid.values()):.1f} mm",
        "FLUID_BENDS":  f"{sum(len(r.bends) for r in fluid.values())}",
        "LONGEST_ID":   longest.id,
        "LONGEST_LEN":  f"{longest.length:.1f} mm",
        "SHORTEST_ID":  shortest.id,
        "SHORTEST_LEN": f"{shortest.length:.1f} mm",
    }


def tray_variables() -> dict:
    """The tray inventory, counted off the placed pack rather than off the plate a reader
    remembers. A plate takes a second seat only where a PAIR meets at one junction."""
    seated: dict[str, set] = {}
    for p in scorecard.ports():
        m = re.fullmatch(r"(V-[A-Z])-[IO]", p.name)
        if m:
            seated.setdefault(p.component, set()).add(m.group(1))
    trays = {b: v for b, v in seated.items() if b in TRAY_BOXES.values()}
    return {
        "TRAY_COUNT":       f"{len(trays)}",
        "TRAY_VALVE_COUNT":      f"{sum(len(v) for v in trays.values())}",
        "TWO_VALVE_COUNT":  f"{sum(1 for v in trays.values() if len(v) == 2)}",
        "ONE_VALVE_COUNT":  f"{sum(1 for v in trays.values() if len(v) == 1)}",
    }


# ─── Driver ───────────────────────────────────────────────────────────
def main() -> int:
    check = "--check" in sys.argv

    runs = {r.id: r for r in _lines.build_runs()}

    problems = []
    problems += check_comments(MANIFOLD)
    problems += check_comments(TRAYS)
    lines, edges = read_edges(MANIFOLD)
    problems += check_manifold_graph(edges, runs)
    problems += check_manifold_coverage(edges, runs)
    problems += check_boxes(MANIFOLD, strict=False)
    problems += check_boxes(TRAYS, strict=True)
    if problems:
        print("fluid-topology charts disagree with the enclosure assembly:")
        print("\n".join(problems))
        return 1

    before = list(lines)
    rewrite_labels(lines, edges, runs)
    problems += rewrite_linkstyles(lines, edges)
    if problems:
        print("fluid-topology-manifold.mmd linkStyle:")
        print("\n".join(problems))
        return 1

    mf_vars, tray_vars = manifold_variables(runs), tray_variables()

    if check:
        stale = [f"  {MANIFOLD.name} line {i + 1}: {b.strip()}"
                 for i, (b, a) in enumerate(zip(before, lines)) if b != a]
        stale += _stale_markers(MANIFOLD, mf_vars)
        stale += _stale_markers(TRAYS, tray_vars)
        stale += _stale_markers(TOPOLOGY, tray_vars)
        if stale:
            print("fluid-topology charts are stale — run _fluid_topology_sync.py:")
            print("\n".join(stale))
            return 1
        print("fluid-topology ✓")
        return 0

    if lines != before:
        MANIFOLD.write_text("\n".join(lines) + "\n")
    substitute_mmd(MANIFOLD, mf_vars, {k: 1 for k in mf_vars})
    substitute_mmd(TRAYS, tray_vars, {k: 1 for k in tray_vars})
    substitute_md(TOPOLOGY, tray_vars, {k: 1 for k in tray_vars})

    fluid = [r for k, r in sorted(runs.items(), key=lambda kv: _seg_no(kv[0]))
             if k.startswith("fluid-")]
    for r in fluid:
        print(f"  {r.id:<9} {r.length:7.1f} mm  {len(r.bends)} bends   {r.frm} → {r.to}")
    print(f"  {'TOTAL':<9} {sum(r.length for r in fluid):7.1f} mm over {len(fluid)} segments")
    print(f"  trays {tray_vars['TRAY_COUNT']} "
          f"({tray_vars['TWO_VALVE_COUNT']} two-seat, {tray_vars['ONE_VALVE_COUNT']} one-seat), "
          f"valves {tray_vars['TRAY_VALVE_COUNT']}")
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
