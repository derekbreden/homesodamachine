"""change-the-question on into-the-housing, wave 3: numbers for the exchange file
exchange/change-the-question--on--into-the-housing-w3.md (cited there as [w3 §n]).

Run:  python3 on_into_the_housing_w3.py > on_into_the_housing_w3.out.txt

Inputs carry labels: [mfr], [source], [calc], [estimate], [assumption].
[ith] = into-the-housing's calc (explorers/into-the-housing/calc/wave2.out.txt),
[ff] = force-and-form's reading of into-the-housing
(explorers/force-and-form/calc/on_into_the_housing.out.txt),
[w2] = this explorer's calc/wave2.out.txt.
Coordinates as into-the-housing's handover: Y along the contact (+Y toward the
mating face), X across the row, Z up (barrels open up, lance down).
"""

import math
from itertools import permutations


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


P = 2.5        # housing pitch [mfr S1]
WIRE = 1.7     # jacket OD [source S29]
T = 0.20       # stock [source S19-S21]

# ---------------------------------------------------------------------------
hr("1. The stepped crimper's insulation step has to swallow the open wings (i2/K1, i1b, i2b)")
print("The stepped crimper's mouth is its lower edge. Wing tips must land inside it at first touch;")
print("a tip that lands on the wall's end face is folded outward, not curled in. The insulation")
print("wings stand taller (2.75-3.20 open [source S19-S22]) than the conductor wings (1.50-1.60), so")
print("the insulation step touches first, before the conductor step's flare has centred anything.")
print("Needed outer width at the mouth = wing spread s + 2 x capture margin m + 2 x wall land l.")
print("That outer width passes down beside the neighbour to the barrel floor.")
print()
spreads = [("pre-formed keyhole (c6), low", 1.96), ("pre-formed keyhole (c6), high", 2.14),
           ("clone open, drawing min", 2.46), ("clone open, typical", 2.80),
           ("clone open, drawing max", 3.00), ("clone open, max + tol", 3.25)]
# Beside a seated neighbour's wire (i2 / K1): wire centre at 2.5 mm, radius 0.85 -> free half-width
# to the jacket at its equator 1.65 mm; clearance c to the jacket.
# Between two crimped insulation barrels (i2b pass 2): neighbour half-width 0.95-1.00 [ff] -> 1.50-1.55.
cases = [("i2/K1: beside a seated neighbour wire (one side)", 2.5 - 0.85),
         ("i2b pass 2: between crimped insulation barrels 2.0 wide", 2.5 - 1.00)]
for label, room in cases:
    print(f"  {label}: free half-width {room:.2f} mm")
    print(f"    {'wing spread':<34} {'need (m 0.05, l 0.05, c 0.05)':>30} {'need (m 0.15, l 0.10, c 0.10)':>30}")
    for name, s in spreads:
        lo = s / 2 + 0.05 + 0.05 + 0.05
        hi = s / 2 + 0.15 + 0.10 + 0.10
        print(f"    {name:<24} {s:5.2f}    {lo:5.2f} -> margin {room - lo:+5.2f}         {hi:5.2f} -> margin {room - hi:+5.2f}")
    print()
print("  The step's outer width 2.5-2.7 mm [ff; i2] leaves a mouth of at most 2.3-2.6 mm with a")
print("  0.05-0.10 mm land: it swallows a pre-formed keyhole (1.96-2.14) and the narrowest clone")
print("  wings (2.46) only. Widening the step to swallow 3.0-3.25 mm wings needs a half-width of")
print("  1.70-1.95 mm, over the 1.65 mm to the neighbour's jacket (i2) and 1.50 mm between crimped")
print("  neighbours (i2b pass 2).")
print("  The conductor step (3.1 mm, 0.8 mm walls) has no such problem: open conductor wings are")
print("  1.43-2.15 mm [source S19-S22], its mouth can flare to ~2.7-2.9 mm.")
print()
print("  Loading the evens of i2b between crimped odds (gap = 2.5 - s/2 - 1.0):")
for name, s in spreads:
    print(f"    {name:<34} gap {2.5 - s / 2 - 1.0:+5.2f} mm")

# ---------------------------------------------------------------------------
hr("2. Does a snapped conductor stay in the barrels when the presser foot lifts? (c6 in i2)")
EI = 14.5   # N mm^2, jacket + strands [ith wave 1 section 1]
print("A humped conductor over a saddle springs up at the barrels by its elastic share of the hump.")
for L in (10.0, 15.0, 20.0):
    for d in (0.2, 0.5, 1.0):
        F = 3 * EI * d / L ** 3
        print(f"   free length {L:4.0f} mm, elastic lift {d:3.1f} mm -> lift force {F*1000:6.1f} mN")
print("   throat retention of a 1.3-1.4 mm keyhole: ~0.3-10 N [w2 section 4, assumption 0.5-1x push-in]")
print("-> a keyhole holds the conductor down by 1-3 orders of magnitude; an open U holds it by nothing.")

# ---------------------------------------------------------------------------
hr("3. Conductor-barrel growth against a rigid stop at the box nose (i2d, i2d'', c1c, c6b)")
print("Coining after full fill lengthens the conductor barrel; the forward half pushes the")
print("transition and box toward +Y. A stop at the box nose blocks it; a stop behind (tab stub,")
print("box rear shoulder) does not.")
L_b = (1.25, 1.5)          # conductor barrel length [xh-facts estimate]
growth = (0.05, 0.15)      # fractional elongation after full fill [estimate]
fwd = (L_b[0] * growth[0] / 2, L_b[1] * growth[1] / 2)
print(f"   forward growth of the barrel front: {fwd[0]:.2f}-{fwd[1]:.2f} mm [estimate]")
F_die = (800.0, 2600.0)    # N peak [xh-facts section 4]
mu = (0.1, 0.2)            # die-to-tin friction [estimate]
print(f"   axial force the flow can push with, bounded by friction on the dies: "
      f"{mu[0]*F_die[0]:.0f}-{mu[1]*F_die[1]:.0f} N [estimate]")
for label, A in (("floor strip only, 0.2 x 1.0-1.4", (0.2 * 1.0, 0.2 * 1.4)),
                 ("U-section with 0.5 mm side walls", (0.2 * 2.0, 0.2 * 2.4))):
    print(f"   transition yield ({label}): {A[0]*450:.0f}-{A[1]*650:.0f} N (450-650 MPa [estimate])")
nose_area = 2 * (1.9 + 2.3) * 0.2
print(f"   box nose end face ~{nose_area:.1f} mm^2: at 90-290 N it bears {90/nose_area:.0f}-{290/nose_area:.0f} MPa")
print("   on the stop: a PA6 stub face (yield ~50-90 MPa [estimate]) dents; a steel stop does not,")
print("   so with steel the transition takes the growth.")
for dL in fwd:
    for Lt in (0.34, 0.8):
        amp = math.sqrt(4 * Lt * dL) / math.pi
        print(f"   growth {dL:.2f} mm taken as a buckle in a {Lt:.2f} mm transition: lateral amplitude ~{amp:.2f} mm")
print("-> Overlapping ranges: a rigid nose stop may bow the transition by ~0.05-0.2 mm (JST's")
print("   bend fault); a PA6 stop dents instead and walks forward. A stop that holds only until")
print("   capture, or a sprung stop (10-30 N), or a rear reference avoids it. Unmeasured.")

# ---------------------------------------------------------------------------
hr("4. Roll play of a box in a stub or cavity: clone boxes, lever = box height")
print("Small-angle roll of a W x H box in a channel of width C: theta ~ (C - W) / H.")
for bw, bh, tag in ((1.95, 2.40, "JST envelope 1.95 x 2.4 [mfr S1]"),
                    (1.90, 2.35, "clone 1.90 x 2.35 [source S19-S22]"),
                    (1.85, 2.20, "clone 1.85 x 2.2 [source S19-S22]")):
    vals = []
    for C in (2.00, 2.10):
        c = max(C - bw, 0)
        vals.append(math.degrees(math.atan(c / bh)))
    print(f"   {tag:<38} in a 2.00-2.10 cavity [ith estimate]: roll +/-{vals[0]:.1f}-{vals[1]:.1f} deg")
print("   into-the-housing's calc H (box 1.95, lever 1.95): +/-1.5-4.4 deg; the window is 5-11 deg [digest].")

# ---------------------------------------------------------------------------
hr("5. i6b post bed: 2.54 against 2.50 mm across a housing")
for n in (4, 5, 6, 7, 9):
    err = (n - 1) * 0.04
    print(f"   XHP-{n}: first to last post {err:.2f} mm off end to end, +/-{err/2:.2f} mm if centred")
print("   capture of a post tip in a box mouth: +/-0.2 mm [ith section E]")

# ---------------------------------------------------------------------------
hr("6. Silicone modulus: into-the-housing's slot grip and jacket share at the Shore-derived range")
print("E 2.5-5.5 MPa from Shore 50-70A by Gent [w2 section 4; Shore via ribbon-as-pallet, source Primasil].")
for E in (2.5, 3.6, 5.5):
    for slot in (1.50, 1.60):
        sq = (WIRE - slot) / 2
        p = E * sq / 0.49
        for Lg in (6.0, 10.0):
            N = 2 * p * Lg * 0.9
            print(f"   slot grip [ith D model]: E {E:3.1f}, slot {slot:.2f}, length {Lg:4.1f}: axial hold {0.5*N:5.1f}-{N:5.1f} N")
for Lf in (2.0, 3.0):
    kb = 12 * EI / Lf ** 3
    for E in (2.5, 3.6, 5.5):
        ks = 2 * E * 2.0 / 0.49
        print(f"   jacket share [ith F model]: free {Lf:.0f} mm, E {E:3.1f}: {100*kb/(kb+ks):3.0f} % of a grip mismatch")

# ---------------------------------------------------------------------------
hr("7. The feed-length rule applied to c1/c1c's two row pushes with housing and web still")
print("Each row is pushed ~7 mm from its pallet into the cavities [c1 step 8]. With the web clamp")
print("and housing still, every conductor of a pushed row must carry 7 mm of extra length, as a")
print("bow over its split. Circular-arc bow of arc length c + s over chord c:")


def arc_height(c, a):
    # solve sin(t)/t = c/a for t in (0, pi)
    target = c / a
    lo, hi = 1e-6, math.pi - 1e-6
    for _ in range(200):
        mid = (lo + hi) / 2
        if math.sin(mid) / mid > target:
            lo = mid
        else:
            hi = mid
    t = (lo + hi) / 2
    R = a / (2 * t)
    return R * (1 - math.cos(t)), R


for c in (6.0, 12.0, 20.0, 26.0):
    for s in (5.0, 7.0):
        h, R = arc_height(c, c + s)
        print(f"   split chord {c:4.0f} mm, stored {s:.0f} mm: bow height {h:4.1f} mm, radius {R:4.1f} mm")
print("-> A 4-9 mm bow per conductor between the web root and the pallet, where c1c's presser comb,")
print("   pallets and row B's carriers work. The alternative is a gang push with the housing moving")
print("   onto one merged row (i3, i6), which stores nothing.")

# ---------------------------------------------------------------------------
hr("8. Length spread in a rigid-blade gang push (i6)")
lengths = {"HDGC 5.8": 5.8, "JXT 5.9": 5.9, "DLL 6.2": 6.2, "CJT 6.73": 6.73, "JST 6.1/6.5": 6.1}
print("   clone drawings: overall length 5.8 / 6.2 / 6.73 / 5.9, each +/-0.25 [source S19-S22];")
print("   JST 6.1 or 6.5 [mfr S1-S3]. Within one lot the spread is unknown [assumption: tight].")
print("   With rears held on one line by a rigid blade, the longest contact bottoms first; the rest")
print("   stop short by the length difference until the drive crushes the longest or stops.")
for d in (0.05, 0.1, 0.25, 0.5):
    print(f"   spread {d:.2f} mm: shortest contact stops {d:.2f} mm short of the longest when the first bottoms")
print("   A tine on a constant-force spring (i3b's preload, 1.25 x single insertion) rides back instead.")
print("   Seated rear inside the rear face: 7.75 - front wall 0.4-0.8 - length (HDGC 5.8-0.25 to CJT 6.73) ->")
print(f"   {7.75-0.8-6.73:.2f}-{7.75-0.4-5.55:.2f} mm (into-the-housing's handover: 0.2-1.25 mm, using 6.1-6.73)")

# ---------------------------------------------------------------------------
hr("9. J4 and J7 orders under both metrics: layers (one plane, i6) and half-row planes (c1/c1c)")
J4 = {"3V3": 1, "GND": 2, "V5": 3, "IO25": 4, "IO26": 5, "IO27": 6, "IO23": 7}   # [repo pcba.tsx]
J7 = {"RB1": 1, "RB2": 2, "RB3": 3, "RB4": 4, "CLO": 5, "CHI": 6, "GND": 7}       # [repo pcba.tsx]


def lds(seq):
    # longest strictly decreasing subsequence = fewest layers (Dilworth)
    best = [1] * len(seq)
    for i in range(len(seq)):
        for j in range(i):
            if seq[j] > seq[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best) if seq else 0


def inv(seq):
    return sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])


def halfrows(seq_with_none):
    m = {i + 1: c for i, c in enumerate(seq_with_none)}
    A = sorted([(c, p) for p, c in m.items() if c is not None and c % 2 == 1])
    B = sorted([(c, p) for p, c in m.items() if c is not None and c % 2 == 0])
    cr = lambda row: sum(1 for i in range(len(row)) for j in range(i + 1, len(row)) if row[i][1] > row[j][1])
    mis = sum(1 for c, p in A if p % 2 == 0) + sum(1 for c, p in B if p % 2 == 1)
    return mis, cr(A) + cr(B)


rows = [
    ("J4", ["V5", "IO25", "3V3", "IO26", "GND", "IO27", "IO23"], J4, "into-the-housing's two-layer order"),
    ("J4", ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"], J4, "change-the-question's c1 order"),
    ("J4", ["3V3", "V5", "IO25", "IO26", "GND", "IO27", "IO23"], J4, "pairs split (1-wire around flow)"),
    ("J7", ["RB1", "RB2", "RB3", "RB4", "GND", "X", "CLO", "CHI"], J7, "3P laid X, CLO, CHI (first trimmed)"),
    ("J7", ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI", "X"], J7, "3P laid CLO, CHI, X (last trimmed)"),
]
print(f"   {'loom':<4} {'web order':<46} {'layers':>6} {'crossings':>9} {'half-rows (off-parity, crossings)':>34}")
for loom, order, pm, tag in rows:
    seq = [pm[n] for n in order if n != "X"]
    seqn = [pm.get(n) for n in order]
    print(f"   {loom:<4} {' '.join(order):<46} {lds(seq):>6} {inv(seq):>9} {str(halfrows(seqn)):>34}   {tag}")
print("   Board pin orders that make each ribbon one layer (a PCB change, Derek's choice):")
print("   J4 pins 1-7 = 3V3, IO26, V5, IO25, GND, IO27, IO23 (or V5, IO25, 3V3, IO26, ...): 0 crossings;")
print("   J7 pins 1-7 = RB1, RB2, RB3, RB4, GND, CLO, CHI: 0 crossings.")

# ---------------------------------------------------------------------------
hr("10. i6b posts as sourced: pulled header pins (brass or bronze) or round music wire")
print("into-the-housing sources its 0.64 mm posts from extra-long male headers [ith sourcing-requests];")
print("the Prime row is uxcell 25 mm-pin headers [sourcing/amazon-prime.md]. Header pins are usually")
print("brass or phosphor bronze [assumption; the listing's material was not recorded].")
posts = [("square 0.64 steel", 200e3, 0.64 ** 4 / 12),
         ("square 0.64 brass/bronze", 100e3, 0.64 ** 4 / 12),
         ("round 0.635 music wire (K&S 5005, Prime row)", 200e3, math.pi * 0.635 ** 4 / 64)]
for name, E, I in posts:
    for L in (8.0, 10.0):
        k = 3 * E * I / L ** 3
        print(f"   {name:<46} free {L:4.1f} mm: {k:5.1f} N/mm, {1/k:5.3f} mm per N")
