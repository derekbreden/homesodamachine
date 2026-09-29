"""
Wave-2 numbers for the into-the-housing explorer.

Run:  python3 wave2.py > wave2.out.txt

Every input carries a label: [mfr], [source], [repo], [calc], [estimate],
[assumption]. Coordinates as in ../handover.md: Y along the contact (+Y toward
the mating face), X across the row, Z up (barrels open up, lance down).
"""
import math
from itertools import permutations, product


def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


PITCH_H = 2.50   # XH housing pitch [mfr S1]
PITCH_R = 1.70   # BNTECHGO ribbon pitch, 1.7 +/-0.1 per conductor [source S29]
WIRE = 1.70      # conductor OD [source S29]

# ---------------------------------------------------------------------------
# Pin maps [repo: hardware/pcb/pcba/pcba.tsx; hardware/assembly/cable-assemblies.md
# section Ribbon pairs; hardware/wiring/*.md SIG-1/4/9]
# J4 SENSORS pins 1..7 = 3V3, GND, V5, IO25, IO26, IO27, IO23.
#   4P carries the 1-wire pair (3V3, IO26) and the flow pair (V5, IO25);
#   3P carries the moisture trio (GND, IO27, IO23).
#   A pair peels off the web together at the far end, so its two conductors
#   must be adjacent in the ribbon [repo: "a ribbon is peeled at one place"].
# J7 REEDS B pins 1..7 = RB1, RB2, RB3, RB4, CLO, CHI, GND.
#   5P carries RB1..RB4 and GND; 3P carries CLO, CHI and one trimmed conductor.
# ---------------------------------------------------------------------------
J4_PIN = {"3V3": 1, "GND": 2, "V5": 3, "IO25": 4, "IO26": 5, "IO27": 6, "IO23": 7}
J7_PIN = {"RB1": 1, "RB2": 2, "RB3": 3, "RB4": 4, "CLO": 5, "CHI": 6, "GND": 7}


def inversions(seq):
    return sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])


def lds(seq):
    """Length of the longest strictly decreasing subsequence = minimum number of
    layers (monotone increasing groups) the sequence splits into (Dilworth)."""
    best = [1] * len(seq)
    for i in range(len(seq)):
        for j in range(i):
            if seq[j] > seq[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best) if seq else 0


def layering(seq):
    """Greedy patience layering: returns a layer index per element such that
    every layer is increasing in web order. Layer 0 is laid first (flat)."""
    # Put in layer 0 the longest increasing subsequence, then repeat.
    remaining = list(range(len(seq)))
    layer = [None] * len(seq)
    k = 0
    while remaining:
        # longest increasing subsequence among remaining indices
        n = len(remaining)
        L = [1] * n
        prev = [-1] * n
        for a in range(n):
            for b in range(a):
                if seq[remaining[b]] < seq[remaining[a]] and L[b] + 1 > L[a]:
                    L[a] = L[b] + 1
                    prev[a] = b
        end = max(range(n), key=lambda a: L[a])
        chain = []
        while end != -1:
            chain.append(remaining[end])
            end = prev[end]
        for idx in chain:
            layer[idx] = k
        remaining = [r for r in remaining if r not in chain]
        k += 1
    return layer


def ribbon_orders_with_pairs(members, pairs):
    """All orders of `members` in which every pair in `pairs` is adjacent."""
    out = []
    for p in permutations(members):
        ok = True
        for a, b in pairs:
            if abs(p.index(a) - p.index(b)) != 1:
                ok = False
        if ok:
            out.append(p)
    return out


hr("A. Pin maps as layers: which looms need a crossing, and how many levels")
print("A crossing between ribbon and housing is one conductor lying over another in the")
print("split. Any pin map splits into layers, each laid in order without crossing; the")
print("minimum number of layers is the longest run of conductors whose pins DEcrease in")
print("web order (Dilworth). Layer 0 lies flat; each higher layer lies over the ones below.")

# J4
four = ["3V3", "IO26", "V5", "IO25"]
three = ["GND", "IO27", "IO23"]
orders4_pairs = ribbon_orders_with_pairs(four, [("3V3", "IO26"), ("V5", "IO25")])
orders4_free = list(permutations(four))
orders3 = list(permutations(three))

def survey(name, groups_a, groups_b, pinmap, label):
    rows = []
    for a, b in product(groups_a, groups_b):
        for left_right in ((a, b), (b, a)):
            seq_names = list(left_right[0]) + list(left_right[1])
            seq = [pinmap[n] for n in seq_names]
            rows.append((lds(seq), inversions(seq), seq_names, seq))
    rows.sort(key=lambda r: (r[0], r[1]))
    best_layers = rows[0][0]
    best_inv = min(r[1] for r in rows)
    print(f"\n{name} ({label}): {len(rows)} web orders surveyed")
    print(f"   fewest layers = {best_layers}; fewest crossings = {best_inv}")
    shown = 0
    for L, inv, names, seq in rows:
        if L == best_layers and shown < 4:
            lay = layering(seq)
            over = [names[i] for i in range(len(names)) if lay[i] > 0]
            print(f"   web order {names} -> pins {seq}: {L} layers, {inv} crossings; rides over: {over}")
            shown += 1
    return rows

j4_free = survey("J4 SENSORS", orders4_free, orders3, J4_PIN, "any order within each ribbon")
j4_pair = survey("J4 SENSORS", orders4_pairs, orders3, J4_PIN, "4P pairs kept adjacent")

# The layout change-the-question named, and the one this file proposes
for tag, names in (("change-the-question's least-crossing layout", ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"]),
                   ("this file's two-layer layout", ["V5", "IO25", "3V3", "IO26", "GND", "IO27", "IO23"]),
                   ("repo order as wave 1 read it (4P sorted, pairs split)", ["3V3", "V5", "IO25", "IO26", "GND", "IO27", "IO23"])):
    seq = [J4_PIN[n] for n in names]
    lay = layering(seq)
    print(f"   {tag}: pins {seq}, {lds(seq)} layers, {inversions(seq)} crossings, "
          f"upper layers {[names[i] + '(L' + str(lay[i]) + ')' for i in range(len(names)) if lay[i] > 0]}")

# J7
five = ["RB1", "RB2", "RB3", "RB4", "GND"]
three7 = ["CLO", "CHI"]
orders5 = [tuple(["RB1", "RB2", "RB3", "RB4", "GND"]), tuple(["GND", "RB1", "RB2", "RB3", "RB4"])]
orders3_7 = [("CLO", "CHI")]
print("\nJ7 REEDS B: the 5P's order is taken as the reed column's order, GND at one edge [assumption]")
for o5 in orders5:
    for left_right in ((o5, orders3_7[0]), (orders3_7[0], o5)):
        names = list(left_right[0]) + list(left_right[1])
        seq = [J7_PIN[n] for n in names]
        lay = layering(seq)
        print(f"   web order {names} -> pins {seq}: {lds(seq)} layers, {inversions(seq)} crossings; "
              f"rides over: {[names[i] for i in range(len(names)) if lay[i] > 0]}")
print("   (the 3P's trimmed conductor is cut back behind the split and never reaches the row)")
print("   procedure-is-the-machine's rewire (GND on the 3P, the 5P's fifth trimmed): pins [1,2,3,4 | 5,6,7] = 1 layer")

print("\nJ1 (5P+4P -> XHP-9) and J2 (3P+3P -> XHP-6, cavity 3 empty): each ribbon's pins are")
print("   contiguous and in order [repo], so 1 layer. J2's gap is an empty target slot, not a crossing.")
print("-> Every loom in the unit is 1 layer except J4 and J7, which are 2 layers when the ribbons")
print("   are laid 4P-left and 5P-left. Two levels of staging cover the whole unit.")


# ---------------------------------------------------------------------------
hr("B. How far each conductor travels sideways from its web position to its cavity")
print("Web centred on the housing [assumption]; pair laid edge to edge at 1.7 mm per conductor.")

def lateral(names, pinmap, n_cav):
    n = len(names)
    web_x = [(i - (n - 1) / 2) * PITCH_R for i in range(n)]
    cav_x = [(pinmap[nm] - 1 - (n_cav - 1) / 2) * PITCH_H for nm in names]
    return web_x, cav_x

cases = [
    ("J4", ["V5", "IO25", "3V3", "IO26", "GND", "IO27", "IO23"], J4_PIN, 7),
    ("J7", ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI"], J7_PIN, 7),
    ("J1 (9 straight)", [f"c{i}" for i in range(1, 10)], {f"c{i}": i for i in range(1, 10)}, 9),
]
max_dx = {}
for name, names, pm, ncav in cases:
    wx, cx = lateral(names, pm, ncav)
    dx = [c - w for w, c in zip(wx, cx)]
    max_dx[name] = max(abs(d) for d in dx)
    print(f"\n{name}:")
    for nm, w, c, d in zip(names, wx, cx, dx):
        print(f"   {nm:>5}: web x {w:+6.2f} -> cavity x {c:+6.2f}   travel {d:+6.2f} mm")
print("\nSpan L from the split root to the target row: angle, and how much shorter the reach")
print("in Y becomes for the largest traveller (dx^2 / 2L); a conductor that travels less is that")
print("much too long and bows; sag of that bow h = sqrt(3 L s / 8).")
for name in max_dx:
    d = max_dx[name]
    for L in (20.0, 25.0, 30.0, 35.0):
        s = d * d / (2 * L)
        sag = math.sqrt(3 * L * s / 8)
        print(f"   {name:>16}: max travel {d:5.2f} over L {L:4.0f}: {math.degrees(math.atan(d / L)):5.1f} deg, "
              f"reach short by {s:4.2f} mm, a straight neighbour bows {sag:4.1f} mm")


# ---------------------------------------------------------------------------
hr("C. Stage high, place low: how high the staged row must sit")
print("The crimped row waits in web order in a staging comb directly above the target comb,")
print("at the same Y, raised h. A carrier moves each contact down into its target slot. A placed")
print("conductor lies flat (Z 0..1.7); a staged one rises linearly from its root to height h.")
print("Where their plan views cross at fraction f of the span from the root, the staged one's")
print("underside is at f*h. It must clear the placed one's top by 0.3 mm: h >= 2.0 / f.")

def crossing_fraction(rA, tA, rB, tB):
    # parametric: x = r + (t - r) s, s in [0, 1]; solve rA + (tA-rA)s = rB + (tB-rB)s
    den = (tA - rA) - (tB - rB)
    if abs(den) < 1e-9:
        return None
    s = (rB - rA) / den
    return s if 0.0 < s < 1.0 else None

def worst_f(placement, wx, cx, stage_x):
    worst = (1.0, None)
    placed = []
    for k in placement:
        for s_idx in [i for i in placement if i not in placed and i != k]:
            for p_idx in placed + [k]:
                f = crossing_fraction(wx[p_idx], cx[p_idx], wx[s_idx], stage_x[s_idx])
                if f is not None and f < worst[0]:
                    worst = (f, (p_idx, s_idx))
        placed.append(k)
    return worst

for (name, names, pm, ncav), stage_pitch in [(c, sp) for c in cases for sp in (2.5, 5.0)]:
    wx, cx = lateral(names, pm, ncav)
    seq = [pm[n] for n in names]
    lay = layering(seq)
    n = len(names)
    stage_x = [(i - (n - 1) / 2) * stage_pitch for i in range(n)]
    flat = [i for i in range(n) if lay[i] == 0]
    up = [i for i in range(n) if lay[i] > 0]
    orders = {
        "web order, lower layer first": flat + up,
        "inside out, lower layer first": sorted(flat, key=lambda i: abs(cx[i])) + sorted(up, key=lambda i: abs(cx[i])),
    }
    if n <= 7:
        best = None
        for pf in permutations(flat):
            for pu in permutations(up):
                f, pair = worst_f(list(pf) + list(pu), wx, cx, stage_x)
                if best is None or f > best[0]:
                    best = (f, list(pf) + list(pu))
        orders["most clearance (exhaustive), lower layer first"] = best[1]
    print(f"   {name}, staged at {stage_pitch} mm pitch:")
    for tag, order in orders.items():
        f, pair = worst_f(order, wx, cx, stage_x)
        if pair:
            print(f"      {tag:<48}: tightest f = {f:.2f} (placed {names[pair[0]]} under staged {names[pair[1]]}) -> h >= {2.0 / f:4.1f} mm")
        else:
            print(f"      {tag:<48}: no placed conductor crosses a staged one")
        if tag.startswith("most clearance"):
            print(f"         order: {[names[i] for i in order]}")
print("-> Placing from the housing centre outward keeps the drop small: ~5-8 mm covers every loom")
print("   at either staging pitch; web order at 5 mm pitch needs up to ~11 mm [calc above].")


# ---------------------------------------------------------------------------
hr("D. Holding sorted contacts, and the backing blade that takes the push")
print("Target slot under-width, so the silicone grips (AMP US 4,230,008 principle):")
for E in (1.0, 3.0, 10.0):          # MPa silicone [estimate]
    for slot in (1.50, 1.60):
        squeeze = (WIRE - slot) / 2          # per side
        strain = squeeze / 0.49              # wall ~0.49 mm [calc C1]
        p = E * strain                       # MPa, crude
        for Lg in (6.0, 10.0):
            N = 2 * p * Lg * 0.9             # two walls, ~0.9 mm contact band each [estimate]
            for mu in (0.5, 1.0):
                pass
            print(f"   E {E:4.1f} MPa, slot {slot:.2f} ({squeeze:.2f}/side, {strain*100:3.0f} %), grip length {Lg:4.1f}: "
                  f"normal {N:5.1f} N, axial hold {0.5*N:5.1f}-{1.0*N:5.1f} N (mu 0.5-1.0)")
print("-> a slot keeps a sorted contact where the carrier left it (a few N) but may not react a")
print("   9.8-25 N insertion. The push is reacted by a blade behind the barrels instead.")
print("\nBacking blade: slotted stainless (laminated stencil foil) dropped behind every insulation")
print("barrel, straddling the wires; each tine bears on the rear edge of the crimped insulation")
print("barrel / tab stub.")
for F in (9.8, 15.0, 25.0):      # per contact; 9.8 N = KONNRA clone max insertion [source]
    for bearing in (0.2 * 0.8, 0.2 * 1.9):
        print(f"   push {F:5.1f} N on {bearing:4.2f} mm^2 of barrel/tab edge: {F / bearing:6.0f} MPa "
              f"(phosphor bronze yields ~500 MPa [estimate])")
print("   A blade tine 0.4 mm wide x 1.0 mm deep, cantilever 1.5 mm, at 25 N: bending stress "
      f"{6 * 25 * 1.5 / (0.4 * 1.0**2) / 1:.0f} MPa (stack foils to 1.0 mm deep; 304 half-hard ~1000 MPa yield [estimate])")


# ---------------------------------------------------------------------------
hr("E. i6b: a bed of long posts through the housing as the target")
for mat, E in (("steel", 200e3), ("brass", 100e3)):
    I = 0.64 ** 4 / 12.0
    for L in (6.0, 8.0, 10.0):
        k = 3 * E * I / L ** 3
        print(f"   0.64 mm square {mat}, free {L:4.1f} mm: {k:6.1f} N/mm; 1 N side load moves the tip {1 / k:5.3f} mm")
print("Box grip on a 0.64 post: 0.2-1.6 N [terminal-supply calc, Molex KK analog, secondhand].")
print("Threading the box onto the post tip: the box mouth (0.60-0.70 mm [source S19-S21]) on a")
print("0.64 post with a 0.2 mm tip chamfer captures +/-0.2 mm; the post then centres the box.")
print("Travel of the housing along the posts to seat: contact length 6.1-6.73 + margin ~ 7.5-8.5 mm")
print("(posts stand ~8.5 mm proud of the rear face).")


# ---------------------------------------------------------------------------
hr("F. Rigid grip through the crimp: how much of the mismatch the silicone jacket takes")
EI = 14.5   # N mm^2 [calc wave 1 section 1]
for Lf in (2.0, 3.0):
    kb = 12 * EI / Lf ** 3            # fixed-guided beam, N/mm
    for Es in (1.0, 3.0, 10.0):
        ks = 2 * Es * (2.0 * 1.0) / 0.49     # two pads 2 x 1 mm on a 0.49 mm wall [estimate]
        share = kb / (kb + ks)
        for d in (0.05, 0.1, 0.2):
            bend = d * (1 - share)
            R = Lf ** 2 / (4 * bend) if bend > 0 else float("inf")
            print(f"   free {Lf:.0f} mm, silicone E {Es:4.1f}: jacket takes {share*100:3.0f} % ; mismatch {d:.2f} -> strands "
                  f"bend {bend:.3f} mm, R {R:6.1f} mm ({'sets' if R < 67 else 'elastic'})")
print("-> The jacket absorbs 20-70 % of a mismatch, which halves the kink but does not remove it")
print("   at 0.1-0.2 mm. Fingers that float in X and Z during the stroke remain the repair.")


# ---------------------------------------------------------------------------
hr("G. The lance condition belongs to the contact, not to i2")
print("A contact held by its box, with a flat anvil under its conductor barrel and the lance hanging")
print("free, needs the anvil's front edge behind the lance tip (+0.1 mm) and in front of the")
print("conductor barrel's front. Measured from the contact's front, that is:")
print("   lance_tip + 0.1 <= box + t   ->   t >= lance_tip + 0.1 - 2.0")
for tip in (2.24, 2.44, 2.64):
    print(f"   lance tip {tip:.2f} mm behind the front: transition t >= {tip + 0.1 - 2.0:.2f} mm")
print("The box depth in a cavity (i2), in a stub (i2d) or in front of a hand tool's jaw drops out:")
print("the same inequality governs every locator that holds the box and leaves the lance free.")
print("-> The iCrimp SN-2549 already crimps these contacts. If its XH anvil is a plain block with")
print("   no slot or step where the lance hangs, today's crimps show t is long enough. If it has a")
print("   relief, every machine anvil needs the same relief. One look at the jaw settles which.")


# ---------------------------------------------------------------------------
hr("H. i2d: a housing stub the lance never enters")
print("Lance length unknown; root = tip - length [assumption: 0.8-1.4 mm long lance].")
for tip in (2.24, 2.44, 2.64):
    for ln in (0.8, 1.1, 1.4):
        root = tip - ln
        dmax = root - 0.1
        print(f"   tip {tip:.2f}, lance {ln:.1f} mm: root {root:.2f} mm behind the front -> box may enter the stub "
              f"up to {dmax:.2f} mm with the lance untouched")
print("Roll held by the stub's walls over that depth (box 1.95 wide in a 2.00-2.10 cavity):")
for clr in (0.05, 0.10, 0.15):
    print(f"   total side clearance {clr:.2f} mm: roll play +/-{math.degrees(math.atan(clr / 1.95)):.1f} deg "
          f"(window 5-11 deg [digest])")
print("Gap between the stub's rear face and the anvil's front edge, for the lance to hang in:")
for tip in (2.24, 2.44, 2.64):
    for d in (1.0, 1.3):
        print(f"   tip {tip:.2f}, box {d:.1f} mm in: lance tip {tip - d:.2f} mm behind the stub face; anvil front "
              f">= {tip - d + 0.1:.2f} mm behind it")


# ---------------------------------------------------------------------------
hr("I. Time per unit for i6 (sort, then push), rough")
moves = 53
for t_move in (20.0, 40.0):
    for t_push in (60.0, 120.0):
        tot = moves * t_move + 10 * t_push + 10 * 60.0 + moves * 10.0
        print(f"   {t_move:4.0f} s per carrier move, {t_push:4.0f} s per housing push, 60 s per housing to load,"
              f" 10 s per pull-back: {tot / 60:5.0f} min per unit")
print("-> under two hours a unit of machine time; the person loads 14 ribbon ends and 10 housings.")
