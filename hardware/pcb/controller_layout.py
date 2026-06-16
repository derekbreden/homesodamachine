"""Controller PCB — headless board layout from the netlist (KiCad pcbnew API).

EXPLORATION / proof-of-concept — not a reviewed or endorsed design path. See README.md
"Exploration"; the placement is a first pass and nothing here is signed off.

Reads controller-board.net, loads each footprint, places it by region, assigns every
net to its pads, draws the 100x100mm board outline, sets a 4-layer stack, and writes
controller-board.kicad_pcb.

Run with KiCad's bundled Python (the one with the pcbnew module):

    "/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9" \
        hardware/pcb/controller_layout.py

This is a FIRST-PASS, algorithmic placement — not hand-tuned. It yields a valid,
openable board with every part placed and every net connected (ratsnest), as the
starting point for routing + manual refinement in Pcbnew. It deliberately clusters the
mains parts (K1/J3/J4/OK1/Q1/D_K1) in one corner, but does NOT enforce the creepage /
RF-keepout / thermal-via intent in README.md "Layout" — review those by hand, the AC
corner especially, before this is manufacturable.
"""

import os
import re
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(HERE, "controller-board.net")
OUT = os.path.join(HERE, "controller-board.kicad_pcb")
FP_BASE = "/Applications/KiCad.app/Contents/SharedSupport/footprints"

W = H = 100.0          # board, mm
MARGIN = 6.0


# ── minimal S-expression parser ───────────────────────────────────────────────
def parse_sexp(text):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack, cur = [], []
    for t in toks:
        if t == "(":
            new = []
            cur.append(new)
            stack.append(cur)
            cur = new
        elif t == ")":
            cur = stack.pop()
        elif t.startswith('"'):
            cur.append(t[1:-1])
        else:
            cur.append(t)
    return cur[0]


def find_all(node, head):
    return [n for n in node if isinstance(n, list) and n and n[0] == head]


def field(node, head):
    for n in find_all(node, head):
        return n[1] if len(n) > 1 else None
    return None


# ── read the netlist ──────────────────────────────────────────────────────────
tree = parse_sexp(open(NET).read())
comps = []   # (ref, footprint, value)
for c in find_all(find_all(tree, "components")[0], "comp"):
    comps.append((field(c, "ref"), field(c, "footprint"), field(c, "value")))
nets = []    # (name, [(ref, [padnums])])
for n in find_all(find_all(tree, "nets")[0], "net"):
    name = field(n, "name")
    nodes = []
    for nd in find_all(n, "node"):
        ref, pin = field(nd, "ref"), field(nd, "pin")
        pads = re.findall(r"\d+", pin) if pin and pin.startswith("[") else [pin]
        nodes.append((ref, pads))
    nets.append((name, nodes))

print(f"netlist: {len(comps)} components, {len(nets)} nets")


# ── load footprints (need real sizes before placing) ─────────────────────────
board = pcbnew.CreateEmptyBoard()
board.SetCopperLayerCount(4)

loaded = []   # (ref, fp, w_mm, h_mm)
missing = []
for ref, fpname, value in comps:
    lib, _, name = fpname.partition(":")
    fp = pcbnew.FootprintLoad(os.path.join(FP_BASE, lib + ".pretty"), name)
    if not fp:
        missing.append(ref)
        continue
    fp.SetReference(ref)
    fp.SetValue(value or "")
    bb = fp.GetBoundingBox()
    loaded.append((ref, fp, pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())))

fp_by_ref = {ref: fp for ref, fp, _, _ in loaded}
size = {ref: (w, h) for ref, _, w, h in loaded}

# ── size-aware shelf placement (no courtyard overlaps) ────────────────────────
AC = ["K1", "J3", "J4", "OK1", "Q1", "D_K1"]          # mains — own corner cluster
BIG = ["U1", "U3", "U4", "U5", "U6", "U7", "U8", "U10", "U11", "U12", "U2", "U9"]
order = {r: i for i, r in enumerate(BIG)}
GAP = 1.6
pos = {}


def shelf(refs, x0, y0, x1, gap, keepout=None):
    """Left-to-right, wrap to a new row; place by top-left, return next free y.
    keepout=(kx, ky): for rows above ky, limit x to kx (reserves a top-right corner)."""
    x, y, rowh = x0, y0, 0.0
    for r in refs:
        w, h = size.get(r, (3, 3))
        xlim = keepout[0] if (keepout and y < keepout[1]) else x1
        if x + w > xlim and x > x0:
            x, y, rowh = x0, y + rowh + gap, 0.0
            xlim = keepout[0] if (keepout and y < keepout[1]) else x1
        pos[r] = (x + w / 2, y + h / 2)
        x += w + gap
        rowh = max(rowh, h)
    return y + rowh + gap


# mains cluster: top-right corner, kept apart from the logic
shelf([r for r in AC if r in size], W - 30, MARGIN, W - MARGIN, GAP)
# the rest: big ICs first (prime top rows), flowing around the reserved AC corner
rest = [r for r, _, _, _ in loaded if r not in AC]
rest.sort(key=lambda r: (order.get(r, 99), r))
shelf(rest, MARGIN, MARGIN, W - MARGIN, GAP, keepout=(W - 34, 34))

for ref, fp, _, _ in loaded:
    x, y = pos.get(ref, (W / 2, H / 2))
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    board.Add(fp)

# nets -> pads (expand bracketed pin lists; set every matching pad incl. thermal)
for name, nodes in nets:
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    for ref, pads in nodes:
        fp = board.FindFootprintByReference(ref)
        if not fp:
            continue
        want = set(pads)
        for pad in fp.Pads():
            if pad.GetNumber() in want:
                pad.SetNet(ni)

# board outline — 100x100 rectangle on Edge.Cuts
corners = [(0, 0), (W, 0), (W, H), (0, H), (0, 0)]
for (ax, ay), (bx, by) in zip(corners, corners[1:]):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(ax), pcbnew.FromMM(ay)))
    seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(bx), pcbnew.FromMM(by)))
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetWidth(pcbnew.FromMM(0.15))
    board.Add(seg)

pcbnew.SaveBoard(OUT, board)
print(f"placed {len(comps) - len(missing)}/{len(comps)} footprints"
      + (f" (MISSING: {missing})" if missing else ""))
print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")
