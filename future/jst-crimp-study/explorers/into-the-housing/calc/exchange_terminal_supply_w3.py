"""
Numbers for into-the-housing's wave-3 exchange on terminal-supply
(exchange/into-the-housing--on--terminal-supply-w3.md).

Run:  python3 exchange_terminal_supply_w3.py > exchange_terminal_supply_w3.out.txt

Coordinates as in ../handover.md: Y along the contact (+Y toward the mating
face), X across the row, Z up (barrels open up, lance down). Every input
carries a label: [mfr], [source], [repo], [calc], [estimate], [assumption].
"TS" = terminal-supply's files; "xh" = context/xh-facts.md.
"""
import math
from itertools import permutations


def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


PITCH_H = 2.50      # XH housing pitch [mfr S1]
PITCH_R = 1.70      # ribbon pitch per conductor [source S29]
WIRE = 1.70         # conductor OD [source S29]
H_HOUSING = 7.75    # XHP height along the mating axis [mfr S2]

# ---------------------------------------------------------------------------
hr("A. How far a contact travels from where it is crimped to where it seats")
print("Seated box front = housing height 7.75 [mfr S2] minus front wall 0.8-1.0 [assumption, as TS")
print("calc 4] inside the rear face. Staged/loaded box front positions are TS's own numbers.")
seat_front = [H_HOUSING - w for w in (1.0, 0.8)]           # 6.75, 6.95 inside rear face
print(f"   seated box front: {seat_front[0]:.2f}-{seat_front[1]:.2f} mm inside the rear face")
print("\n a5 (bare contact staged d mm into the rear mouth, crimped there, then pushed home):")
for d in (1.0, 1.5, 2.0):
    T = [s - d for s in seat_front]
    print(f"   staged {d:.1f} mm -> push after the crimp {T[0]:.2f}-{T[1]:.2f} mm   (TS a5 text says '~4.5 mm')")
print("   (4.5 mm corresponds to a seated contact whose rear is flush with the rear face; TS calc 4")
print("    puts the seated rear 0.25-0.85 mm inside it, which gives the numbers above)")
print("\n a4b (post stands P mm out of the rear face, box engaged e mm on its tip, crimped there):")
for P in (9.0,):
    for e in (1.5, 1.8):
        out = P - e
        T = [out + s for s in seat_front]
        print(f"   post {P:.1f} proud, box on {e:.1f}: box front {out:.1f} mm outside -> travel {T[0]:.2f}-{T[1]:.2f} mm")
print("\n i6b (this explorer; posts 8.5 proud, crimped box threaded 1-2 mm on, housing slides onto all):")
for e in (1.0, 2.0):
    out = 8.5 - e
    T = [out + s for s in seat_front]
    print(f"   box on {e:.1f}: box front {out:.1f} outside -> housing travel {T[0]:.2f}-{T[1]:.2f} mm "
          f"(i6b's housing travel)")

# ---------------------------------------------------------------------------
hr("B. Where that travel is stored when one contact is crimped and seated at a time")
print("With one web clamp for all conductors, square-cut ends, and every contact seated taut, a")
print("contact crimped T short of its seat needs its conductor T longer than the straight line")
print("at the moment of the crimp. The length lives in a bow between root and crimp")
print("(sag h = sqrt(3 L T / 8), shallow-arch approximation) - or, if the housing moves onto")
print("the contact instead, in the already-seated neighbours. A gang push stores none: every")
print("conductor gets its T at once from one move of the web or the housing.")
for name, T in (("a5 as written (4.5)", 4.5), ("a5 from TS calc 4 geometry", 5.35), ("a4b, post 9 proud", 14.2)):
    row = []
    for L in (20.0, 25.0, 30.0, 40.0):
        row.append(f"L {L:.0f}: {math.sqrt(3 * L * T / 8):4.1f}")
    print(f"   {name:<28} T {T:5.2f} mm -> bow sag  " + ",  ".join(row) + " mm")
print("Tightest bend in that hump if both ends are held straight (clamped-clamped cosine shape,")
print("excess length pi^2 h^2 / 4L, peak curvature 2 pi^2 h / L^2), against the strands' yield")
print("radius ~67 mm [digest]:")
for name, T in (("a5", 5.35), ("a4b", 14.2)):
    for L in (25.0, 30.0):
        h = math.sqrt(4 * L * T) / math.pi
        Rmin = L ** 2 / (2 * math.pi ** 2 * h)
        print(f"   {name:<4} T {T:5.2f}, L {L:.0f}: hump {h:4.1f} mm, tightest radius {Rmin:4.1f} mm -> "
              f"{'sets (kinks)' if Rmin < 67 else 'elastic'}")
Mp = 60 * 70.0 * 0.08 ** 3 / 6    # N mm: 60 strands, yield 70 MPa [TS calc estimate], d 0.08
print(f"   plastic moment of the 60-strand bundle ~{Mp:.2f} N mm; drawing a 7-13 mm hump straight needs "
      f"~{Mp / 13:.2f}-{Mp / 7:.2f} N of tension")
print("-> each conductor stands in a 6-8 mm hump (a5) or an 11-15 mm hump (a4b) while it is")
print("   crimped, between the web and the die, beside conductors lying flat. The hump bends the")
print("   strands past yield, so it holds its shape rather than springing against neighbours, and")
print("   the push draws it straight with a few hundredths of a newton.")

# ---------------------------------------------------------------------------
hr("C. Neighbours beside a die at the housing: seated side and waiting side")
print("Clearance per side = neighbour centre distance - punch half-width - neighbour half-width.")
print("Negative = the punch lands on it. TS a5 counted only the seated (swept) side.")
punches = (("2.7 conductor punch [TS a5]", 2.7), ("3.1 stepped crimper, 0.8 walls [f&f, IH i2]", 3.1),
           ("3.5 conductor/ins punch [TS a5]", 3.5), ("4.0 insulation punch [TS a5]", 4.0))
neigh = (("waiting conductor, insulation 1.7 OD, fanned to 2.5", 2.5, 1.70),
         ("waiting conductor, insulation 1.7 OD, at web pitch 1.7", 1.7, 1.70),
         ("crimped neighbour, conductor barrel ~1.5 wide, at 2.5", 2.5, 1.50),
         ("crimped neighbour, insulation barrel ~1.8-2.0, at 2.5", 2.5, 1.95))
for nname, c, w in neigh:
    print(f"   {nname}:")
    for pname, pw in punches:
        clr = c - pw / 2 - w / 2
        print(f"      {pname:<45} {clr:+5.2f} mm")
print("   Branch T2 (narrow stepped dies; neighbours waiting flat at 2.5, or crimped and staged):")
for lab, c, w in (("waiting conductor 1.7 OD", 2.5, 1.70), ("crimped insulation barrel 1.95", 2.5, 1.95)):
    for step in (2.5, 2.7):
        print(f"      {lab:<32} vs {step:.1f} insulation step: {c - step / 2 - w / 2:+5.2f} mm")
for wo in (2.46, 3.00):
    print(f"      open clone wings {wo:.2f} of a newly staged contact vs a crimped neighbour's 1.95 "
          f"insulation barrel: {2.5 - wo / 2 - 1.95 / 2:+5.2f} mm")
print("-> the waiting side needs the same sweep or a lift as the seated side for 3.5-4.0 mm")
print("   punches; crimped neighbours left staged at the mouth (branch T2) admit only the 3.1 mm")
print("   stepped crimper at the conductor barrel, and 2.5-2.7 mm steps at the insulation barrel.")

# ---------------------------------------------------------------------------
hr("D. Lance and anvil: the window for a flat anvil's front edge (IH calc wave2 G)")
print("Anvil front edge must sit >= lance tip + 0.1 behind the contact front and <= the conductor")
print("barrel's front (box 2.0 + transition t). Margin = (2.0 + t) - (tip + 0.1).")
print("Lance tip 2.24-2.64 mm [xh S19-S22]; transition t 0.4-0.6 [TS calc wave2 section 5 reading].")
for t in (0.4, 0.5, 0.6):
    row = []
    for tip in (2.24, 2.44, 2.64):
        row.append(f"tip {tip:.2f}: {2.0 + t - (tip + 0.1):+5.2f}")
    print(f"   t {t:.1f}:  " + ",  ".join(row) + " mm")
print("   TS a5's own staging numbers (tip 0.94 outside the face at 1.5 staged -> tip 2.44;")
print(f"   conductor barrel 1.1 behind the face -> front at 2.6): margin {2.6 - (2.44 + 0.1):+.2f} mm")
print("   TS a5's sentence 'tip ~0.1 mm ahead of the conductor barrel's start' is margin 0 by construction.")
print("-> across the clone-drawing ranges a flat anvil fits in about half the cases; the rest need")
print("   a lance slot in the anvil (conductor barrel carried on the slot's shoulders).")

# ---------------------------------------------------------------------------
hr("E. A barrels-up contact on a channel floor with no lance groove (TS a6 pocket plate)")
print("The lance stands p proud of the floor side [xh: 0.6-0.9], tip at x_t from the front")
print("[xh: 2.24-2.64]; overall length L [xh: 5.8-6.73, tab excluded].")
print("Rough centre of mass from sheet areas (0.2 mm stock): box 2.0 long x ~8.4 perimeter, transition,")
print("conductor barrel ~1.4 x 4.7, insulation barrel ~1.2 x 8.5 [estimate]:")
parts = ((1.0, 2.0 * 8.4), (2.25, 0.5 * 2.0), (3.2, 1.4 * 4.7), (5.4, 1.2 * 8.5))
xcom = sum(x * a for x, a in parts) / sum(a for _, a in parts)
print(f"   x_com ~ {xcom:.2f} mm behind the front (the lance tip is 2.24-2.64): close to the tip, so either")
print("   rest occurs; both are shown.")
for p in (0.6, 0.75, 0.9):
    for xt in (2.24, 2.64):
        for L in (5.8, 6.73):
            up = math.degrees(math.atan(p / (L - xt)))
            front = p * L / (L - xt)
            dn = math.degrees(math.atan(p / xt))
            rear = p * L / xt
            print(f"   p {p:.2f} tip {xt:.2f} L {L:.2f}: nose-up rest {up:4.1f} deg, box front floor "
                  f"{front:4.2f} mm high | nose-down rest {dn:4.1f} deg, rear {rear:4.2f} mm high")
print("-> the contact sits 8-22 deg off the channel axis; resting nose-up its box front floor is")
print("   0.9-1.7 mm high - several times the post's capture (section F). A lance groove along the")
print("   whole channel floor (channels are open at both ends) lets it lie flat.")

# ---------------------------------------------------------------------------
hr("F. Post capture at the box front: the entry, not the inside")
print("xh-facts: box entry 0.60-0.70 mm [source S19, S21]; post 0.64 mm square [mfr S1].")
print("TS wave2 5 used the box inside (~1.45 x 1.80) and got +/-0.41 lateral, +/-0.58 vertical.")
for entry in (0.60, 0.70):
    for c in (0.10, 0.20, 0.28):
        tip = 0.64 - 2 * c
        print(f"   entry {entry:.2f}, pin tip chamfer {c:.2f}/side (tip flat {tip:.2f}): capture +/-{(entry - tip) / 2:.2f} mm")
print("-> +/-0.1-0.2 mm with ordinary chamfers, +/-0.2-0.25 mm with a near-pointed tip; the")
print("   box's own formed lead-in (unmeasured) adds to this.")

# ---------------------------------------------------------------------------
hr("G. Floating the housing instead of setting the anvil by wedge (TS a5)")
EI = 14.1 + 1.6   # N mm^2, strands + silicone [TS calc wave2 section 4]
print(f"Seated conductor EI ~{EI:.1f} N mm^2 [TS calc]; as a fixed-guided beam between web and housing k = 12EI/L^3.")
for L in (15.0, 20.0, 30.0):
    k = 12 * EI / L ** 3
    for n in (4, 8):
        print(f"   L {L:.0f} mm, {n} seated conductors: {n * k:6.3f} N/mm -> 0.2 mm of float costs {n * k * 0.2:6.3f} N")
print("-> the seated wires do not resist a floating nest; a flexure nest of 1-2 N/mm costs 0.2-0.4 N")
print("   at 0.2 mm, against tens of newtons of punch lead-in at first touch. The anvil can be the")
print("   master and the housing can follow, with no per-cavity measurement.")

# ---------------------------------------------------------------------------
hr("H. T1: the crown station's fan is the staging plane (a2d + i6)")
print("Split needed to fan a ribbon end to pitch p (outer conductor moves (n-1)/2 (p - 1.7)) at a")
print("20 deg fan, plus ~6 mm straight [TS calc 5 convention]:")
for name, n in (("3P", 3), ("4P", 4), ("5P", 5), ("J4/J7 pair, 7-8", 8), ("J1 5P+4P, 9", 9)):
    row = []
    for p in (3.0, 3.5):
        mv = (n - 1) / 2 * (p - PITCH_R)
        row.append(f"p {p:.1f}: outer moves {mv:4.1f}, split {mv / math.tan(math.radians(20)) + 6:4.1f}")
    print(f"   {name:<17} " + ";  ".join(row) + " mm")

J4_PIN = {"3V3": 1, "GND": 2, "V5": 3, "IO25": 4, "IO26": 5, "IO27": 6, "IO23": 7}
J7_PIN = {"RB1": 1, "RB2": 2, "RB3": 3, "RB4": 4, "CLO": 5, "CHI": 6, "GND": 7}


def layering(seq):
    remaining = list(range(len(seq)))
    layer = [None] * len(seq)
    k = 0
    while remaining:
        n = len(remaining)
        Lb = [1] * n
        prev = [-1] * n
        for a in range(n):
            for b in range(a):
                if seq[remaining[b]] < seq[remaining[a]] and Lb[b] + 1 > Lb[a]:
                    Lb[a] = Lb[b] + 1
                    prev[a] = b
        end = max(range(n), key=lambda a: Lb[a])
        chain = []
        while end != -1:
            chain.append(remaining[end])
            end = prev[end]
        for idx in chain:
            layer[idx] = k
        remaining = [r for r in remaining if r not in chain]
        k += 1
    return layer


def crossing_fraction(rA, tA, rB, tB):
    den = (tA - rA) - (tB - rB)
    if abs(den) < 1e-9:
        return None
    s = (rB - rA) / den
    return s if 0.0 < s < 1.0 else None


def worst_f(order, wx, cx, sx):
    worst = (1.0, None)
    placed = []
    for k in order:
        for s_idx in [i for i in order if i not in placed and i != k]:
            for p_idx in placed + [k]:
                f = crossing_fraction(wx[p_idx], cx[p_idx], wx[s_idx], sx[s_idx])
                if f is not None and f < worst[0]:
                    worst = (f, (p_idx, s_idx))
        placed.append(k)
    return worst


cases = [
    ("J4", ["V5", "IO25", "3V3", "IO26", "GND", "IO27", "IO23"], J4_PIN, 7),
    ("J7", ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI"], J7_PIN, 7),
    ("J1 (9 straight)", [f"c{i}" for i in range(1, 10)], {f"c{i}": i for i in range(1, 10)}, 9),
    ("5P straight (J6)", [f"c{i}" for i in range(1, 6)], {f"c{i}": i for i in range(1, 6)}, 5),
]
print("\nStaging at the crown's fan pitch: how high above the target row the fan must sit")
print("(IH wave2 C rule, h >= 2.0/f; root = web position at 1.7 mm, staged at pitch p, target at 2.5 mm)")
for name, names, pm, ncav in cases:
    n = len(names)
    wx = [(i - (n - 1) / 2) * PITCH_R for i in range(n)]
    cx = [(pm[nm] - 1 - (ncav - 1) / 2) * PITCH_H for nm in names]
    seq = [pm[nm] for nm in names]
    lay = layering(seq)
    flat = [i for i in range(n) if lay[i] == 0]
    up = [i for i in range(n) if lay[i] > 0]
    for p in (3.0, 3.5):
        sx = [(i - (n - 1) / 2) * p for i in range(n)]
        order = sorted(flat, key=lambda i: abs(cx[i])) + sorted(up, key=lambda i: abs(cx[i]))
        f, pair = worst_f(order, wx, cx, sx)
        best = None
        if n <= 7:
            for pf in permutations(flat):
                for pu in permutations(up):
                    ff, _ = worst_f(list(pf) + list(pu), wx, cx, sx)
                    if best is None or ff > best[0]:
                        best = (ff, list(pf) + list(pu))
        txt = f"centre outward: " + (f"h >= {2.0 / f:4.1f} mm" if pair else "no crossing")
        if best:
            txt += f"; best order h >= {2.0 / best[0]:4.1f} mm" if best[0] < 1.0 else "; best order: no crossing"
        maxmove = max(abs(c - s) for c, s in zip(cx, sx))
        print(f"   {name:<17} p {p:.1f}: {txt}; largest sideways move staging->cavity {maxmove:4.1f} mm")
print("-> an 8-10 mm drop from the crown's fan to the target row covers every loom, as at 2.5 or 5 mm.")

print("\nSpear push on a staged crimped contact (post head, 0.2-2 N) against buckling of its free")
print("conductor: digest ~6 N over 5 mm, ~40 N over 2 mm -> P ~ 150-160 / L^2 N [digest, scaled]")
for L in (20.0, 25.0, 30.0):
    print(f"   free {L:.0f} mm: buckles at ~{155 / L ** 2:4.2f} N")
print("-> the spear needs a fork behind the insulation barrel (a6's backstop blade, slotted for the")
print("   wire); the conductor alone cannot react it.")

# ---------------------------------------------------------------------------
hr("I. The skip-pitch crown as i2's strip feed (i2 needs neighbours under the housing)")
print("Neighbour at arc s on a crown of radius R: rotated s/R; floor drop R(1-cos); box top (2.3 mm")
print("above its floor [xh end view 2.2-2.4]) at (R+2.3)cos(s/R) - R; X = (R+2.3) sin(s/R).")
print("Housing underside ~0.4 mm below the station contact's floor [assumption: cavity floor wall].")
for R in (6.3, 8.0, 12.5, 25.0, 30.0):
    strain = 0.2 / (2 * R) * 100
    for s in ((7.1, 9.5, 14.2, 21.3) if R == 12.5 else (7.1, 14.2, 21.3)):
        ph = s / R
        drop = R * (1 - math.cos(ph))
        boxtop = (R + 2.3) * math.cos(ph) - R
        X = (R + 2.3) * math.sin(ph)
        ok = "clears housing" if boxtop < -0.4 else "HITS housing if within its span"
        print(f"   R {R:4.1f} (strain {strain:4.2f} %), s {s:4.1f}: floor drop {drop:4.2f}, box top {boxtop:+5.2f}, X {X:5.1f} -> {ok}")
print("XHP spans beside a station cavity (worst case, station at an end): XHP-4 9.1, XHP-5 11.6,")
print("XHP-7 16.6, XHP-9 21.6 mm (A + 1.6) [mfr S2 widths].")
print("-> with every contact kept, the 7.1 mm neighbour's box top clears the housing only on a")
print("   plastic crown (R <= ~8-10); with every other contact removed, TS a2d's elastic R 25-30")
print("   puts it 1.2-2.0 mm below the housing's underside, and the floor drop is 3.3-3.9 mm.")

# ---------------------------------------------------------------------------
hr("J. i2b with every cavity preloaded: open neighbours beside the stepped crimper (TS a7 change 4)")
print("Clearance per side at 2.5 mm pitch = 2.5 - open width/2 - die step/2.")
for label, w in (("open conductor barrel, clone 1.68", 1.68), ("open conductor barrel, clone 1.90", 1.90)):
    print(f"   {label}: vs 3.1 conductor step {2.5 - w / 2 - 1.55:+5.2f} mm")
for label, w in (("open insulation wings, JST envelope 1.95", 1.95), ("Wurth analog 2.30", 2.30),
                 ("clone 2.46", 2.46), ("clone 3.00", 3.00)):
    print(f"   {label}: vs 2.5 insulation step {2.5 - w / 2 - 1.25:+5.2f}, vs 2.7 step {2.5 - w / 2 - 1.35:+5.2f} mm")
print("-> narrower genuine wings let every cavity be preloaded (TS a7), but the conductor step")
print("   clears an open neighbour's conductor barrel by 0.00-0.11 mm only; the odd/even order")
print("   stays unless genuine conductor barrels are narrower than the clone drawings.")

# ---------------------------------------------------------------------------
hr("K. Force ladder (IH/f&f) against TS a4b's seat pull")
for pull in (5.0, 10.0):
    print(f"   seat pull {pull:4.1f} N: {pull / 14.7 * 100:3.0f} % of 14.7 N (Molex analog retention), "
          f"{pull / 19.6 * 100:3.0f} % of 19.6 N (KONNRA clone spec)")

# ---------------------------------------------------------------------------
hr("L. T1 machine time per unit [estimate]")
a2d = 53 * 106 / 60.0   # TS calc wave2 11
for t_move, t_push in ((20.0, 60.0), (40.0, 120.0)):
    i6 = (53 * t_move + 10 * t_push + 10 * 60.0 + 53 * 10.0 + 53 * 15.0) / 60.0   # +15 s proof pull each
    dock = 14 * 30 / 60.0
    print(f"   crown station {a2d:4.0f} min + sort/pull/push {i6:4.0f} min + 14 carriage moves {dock:3.0f} min "
          f"= {(a2d + i6 + dock) / 60:.1f} h")
