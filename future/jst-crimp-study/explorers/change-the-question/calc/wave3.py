"""change-the-question, wave 3: numbers for the settled idea files.

Run:  python3 wave3.py > wave3.out.txt

Cited from the idea files as "calc w3b §n" (w3b, to keep it apart from the exchange
calc on_into_the_housing_w3, cited as "w3 §n"). Labels on inputs:
[mfr], [source], [calc], [estimate], [assumption];
[w2 §n] = calc/wave2.out.txt; [htq §n] = hand-tool-as-press's
calc/exchange_ctq_w3.out.txt; [digest] = context/digest-wave1.md.
"""

import math


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


T = 0.20                    # stock, mm [source S19-S21: 0.20 +/-0.02]
CORE = (0.75, 0.80)         # strand bundle, mm [xh-facts section 7, estimate]
SPRINGBACK = (0.02, 0.05)   # growth of a formed width after release, mm [w2 section 3, estimate]
DIE_INS_W = (1.80, 1.90, 2.00)  # insulation die width, mm [assumption: JST UK gives 1.80 for SXH-002 and
                                # SXA, mfr S13, S14; the SN-2549's own XH insulation width is unmeasured]
L_INS = (0.8, 1.5)          # insulation barrel length, mm [xh-facts section 1, estimate]


def gent_E(shore_a):
    # Gent's relation, Shore A -> Young's modulus, MPa [as in w2 section 4]
    return 0.0981 * (56 + 7.62336 * shore_a) / (0.137505 * (254 - 2.54 * shore_a))


E_LO, E_HI = gent_E(50), gent_E(70)   # 2.5-5.5 MPa [w2 section 4; Shore 50-70A via ribbon-as-pallet]


def bore_grip(ID, OD):
    """w2 section 4's axial-grip model of a round bore on the jacket, unchanged."""
    d = (OD - ID) / 2
    if d <= 0:
        return (0.0, 0.0)
    wall = ((OD - CORE[1]) / 2, (OD - CORE[0]) / 2)
    strain = (d / wall[1], d / wall[0])
    p = (E_LO * strain[0], E_HI * strain[1])
    area = (math.pi * ID * L_INS[0] * 0.5, math.pi * ID * L_INS[1] * 0.8)
    mu = (0.3, 0.8)
    return (mu[0] * p[0] * area[0], mu[1] * p[1] * area[1])


# ---------------------------------------------------------------------------
hr("1. What the final stroke does to a round keyhole (c6): side squeeze pinches the throat")
print("The keyhole's outside (bore + 2 x stock) is wider than the die's insulation section, so the")
print("die's side walls, which reach down to near the anvil at the bottom of the stroke [htq section 3,")
print("edge model], push the ring's widest point inward by delta per side. Each wing then turns")
print("about its root near the floor corner, and the tip, higher up than the widest point, moves")
print("inward by k x delta, k = (tip height - pivot height) / (widest-point height - pivot height).")
print("The tip also moves slightly DOWN (it lies inboard of the pivot), so the die's arches, which")
print("close at ~1.8 mm, never reach it; the die's cusp meets the jacket top instead [htq section 1].")
print()
print("  bore D | throat g | outside | k (pivot 0.2-0.6 above floor) | throat after the stroke for die width 1.80 / 1.90 / 2.00")
for D in (1.57, 1.60, 1.65):
    for g in (1.3, 1.4, 1.5):
        yc = T + D / 2
        ytip = yc + math.sqrt((D / 2) ** 2 - (g / 2) ** 2)
        k = [(ytip - (T + yp)) / (yc - (T + yp)) for yp in (0.0, 0.4)]
        out = D + 2 * T
        res = []
        for W in DIE_INS_W:
            delta = max(0.0, (out - W) / 2)
            lo = g - 2 * max(k) * delta
            hi = g - 2 * min(k) * delta
            res.append(f"{max(lo, 0):.2f}-{max(hi, 0):.2f}")
        print(f"  {D:5.2f}  |   {g:3.1f}    |  {out:4.2f}   |          {min(k):.2f}-{max(k):.2f}            |  " + " / ".join(res))
print("-> With an insulation die 1.80-1.90 mm wide the stroke pinches the throat from 1.3-1.5 mm down")
print("   to roughly 0.75-1.4 mm, pressing the tips into the jacket's shoulders: an O-shaped crimp")
print("   with a narrowed gap on top, not a B. With a 2.00 mm die the ring is barely touched and the")
print("   insulation grip stays the snap's. The tips are not turned over the jacket in either case")
print("   (agreeing with htq section 1); how far the throat closes depends on the SN-2549's")
print("   insulation width, which nobody has measured. Rigid-wing kinematics [estimate]; the jacket")
print("   resists the closure, and elastic recovery of the wings reopens it a few percent [w2 section 3].")

# ---------------------------------------------------------------------------
hr("2. The tool-made pre-form (c6c): a narrowed U, and the snap and grip it gives")
print("At the end of the insulation-first window the wings are inside the die width, roots near")
print("vertical, tips 2.3-3.0 mm above the underside and starting to curl inward [htq section 3].")
print("Inside width of the U = die width + springback - 2 x stock.")
k_wall = (12.0, 33.0)   # N/mm per wall, 3EI/L^3 at 2.0-2.8 mm [htq H1 estimate]; checked:
E_pb = 110e3
I = 1.2 * T ** 3 / 12
for Lw in (2.0, 2.8):
    print(f"  wall stiffness check: 3EI/L^3, E 110 GPa, 1.2 x 0.2 mm, L {Lw} mm -> {3*E_pb*I/Lw**3:4.1f} N/mm")
print()
print("  die W | U inside | jacket OD 1.60 / 1.70 / 1.80: interference per side")
for W in DIE_INS_W:
    wi = (W + SPRINGBACK[0] - 2 * (T + 0.02), W + SPRINGBACK[1] - 2 * (T - 0.02))
    ds = []
    for OD in (1.60, 1.70, 1.80):
        ds.append(f"{(OD - wi[1]) / 2:+.2f} to {(OD - wi[0]) / 2:+.2f}")
    print(f"  {W:4.2f}  | {wi[0]:.2f}-{wi[1]:.2f}  | " + " / ".join(ds))
print()
print("  lateral grip of the U walls on the jacket, walls and silicone in series:")
print("  silicone side stiffness k_s = E x contact width (0.6-0.9 mm) x barrel length / wall (0.45-0.47 mm)")
ks = (E_LO * 0.6 * L_INS[0] / 0.47, E_HI * 0.9 * L_INS[1] / 0.45)
kser = (k_wall[0] * ks[0] / (k_wall[0] + ks[0]), k_wall[1] * ks[1] / (k_wall[1] + ks[1]))
print(f"  k_s {ks[0]:.1f}-{ks[1]:.1f} N/mm; in series with a wall of {k_wall[0]:.0f}-{k_wall[1]:.0f} N/mm -> {kser[0]:.1f}-{kser[1]:.1f} N/mm")
for d in (0.02, 0.05, 0.10, 0.15, 0.20):
    N = (d * kser[0], d * kser[1])
    G = (2 * 0.3 * N[0], 2 * 0.8 * N[1])
    print(f"  interference {d:.2f} per side: normal {N[0]:.2f}-{N[1]:.1f} N per side, axial grip {G[0]:.2f}-{G[1]:.1f} N")
print("  -> about the round keyhole's band (0.08-3.8 N at OD 1.70 [htq section 2]); the silicone, not")
print("     the softer wall, still sets most of it at the low end.")
print()
print("  snap through the tips' gap g_t (tips vertical: g_t = U inside; curl started: 0.1-0.3 mm less):")
for gt in (1.65, 1.50, 1.40, 1.30, 1.20):
    d = (1.70 - gt) / 2
    N = (d * kser[0], d * kser[1])
    push = []
    for (Nn, a, mu) in ((N[0], 30, 0.3), (N[1], 40, 0.8)):
        ta = math.tan(math.radians(a))
        push.append(2 * Nn * (ta + mu) / (1 - mu * ta))
    print(f"  g_t {gt:.2f} on a 1.70 jacket: interference {d:.2f}/side, push-in {push[0]:.2f}-{push[1]:.1f} N,"
          f" retention against lift ~{0.5*push[0]:.2f}-{push[1]:.1f} N [assumption 0.5-1x push-in]")
print("  -> with the tips still vertical (g_t = U inside, 1.4-1.65) there is no undercut: the U holds")
print("     the jacket against lift only by wall friction, the same ~0.02-3.5 N as its axial grip.")
print("     Once the click has started the curl (g_t 1.2-1.4) the tips form an undercut; push-in is")
print("     ~0.7-27 N and retention ~0.3-27 N, the keyhole's band [assumption 0.5-1x push-in].")
print()
box_w = (1.85, 1.95)
print(f"  nesting: a box {box_w[0]}-{box_w[1]} mm wide cannot enter a U 1.42-1.85 mm inside whose tips curl in;")
print("  a pre-formed contact stands 2.3-3.0 mm tall at the insulation barrel against a 2.2-2.4 mm box,")
print("  so a stick channel is ~2.1-2.2 mm wide x ~3.1-3.2 mm tall (c6's 2.1 x 2.6 is for the round keyhole).")

# ---------------------------------------------------------------------------
hr("3. Choosing the mandrel against the measured jacket OD (c6, c6b): bore, grip and pins")
print("Rule [htq H2 repair]: bore after springback 0.08-0.12 mm under the measured jacket OD;")
print("mandrel = bore - springback (0.02-0.05); go pin just under the smallest bore; no-go pin")
print("0.05-0.08 mm under the jacket OD.")
print("  jacket OD | bore target | mandrel    | axial grip at that bore (w2 model) | go pin | no-go pin")
for OD in (1.60, 1.65, 1.70, 1.75, 1.80):
    b = (OD - 0.12, OD - 0.08)
    m = (b[0] - SPRINGBACK[0], b[1] - SPRINGBACK[1])
    g_lo = bore_grip(b[1], OD)[0]
    g_hi = bore_grip(b[0], OD)[1]
    print(f"   {OD:.2f}    | {b[0]:.2f}-{b[1]:.2f}   | {min(m):.2f}-{max(m):.2f}  |"
          f"             {g_lo:.2f}-{g_hi:.1f} N              | {b[0]-0.01:.2f}   | {OD-0.08:.2f}-{OD-0.05:.2f}")
print("  the Prime-confirmed Accusize set stops at 1.52 mm [sourcing/amazon-prime.md]: it holds the")
print("  mandrel and both pins only if the jacket measures ~1.60 mm; at 1.70 the pins are a Wave 3 request.")
print("  Grip at a bore the rule leaves: ~0.1-4 N, the same band, but no longer zero at the low edge")
print("  of the ribbon's 1.7 +/-0.1 mm [source S29], because the bore follows the measured jacket.")
print("  If the OD varies by +/-0.1 mm along one spool, one mandrel cannot follow it; the grip then")
print("  spans ~0-6 N across the spool [htq section 2].")

# ---------------------------------------------------------------------------
hr("4. Throat retention, restated from w2 section 4 (consistency)")
for g, (plo, phi) in ((1.3, (0.7, 30)), (1.4, (0.5, 20)), (1.5, (0.3, 11))):
    print(f"  throat {g}: push-in {plo}-{phi} N -> retention against lift, 0.5-1x push-in: {0.5*plo:.2f}-{phi} N")
print("  (the earlier '0.3-10 N' had no derivation for its 10 N ceiling; nothing downstream used it)")

# ---------------------------------------------------------------------------
hr("5. Row B's stored length in c1/c1c's two-push ending: forming the bow at the park")
print("Two sequential pushes into one housing need one row to carry ~7 mm of stored length")
print("(w3 section 7). If the housing moves onto row A, only row B stores it: pallet B draws back")
print("7 mm as it parks, and its conductors bow below the working plane over the split.")
print("Buckling load of one free conductor, Euler scaling from 6 N over 5 mm [digest]:")
for Lc in (6, 12, 20, 26):
    print(f"  split chord {Lc:2d} mm: buckling load ~{6*(5/Lc)**2:.2f} N per conductor")
print("  bow height for 7 mm stored over 6-26 mm: 4.6-8.6 mm [w3 section 7]")
print("-> drawing pallet B back costs well under the pallet's own friction; what matters is that")
print("   the bow goes down (the park fold sets it) and stays clear of row A's wires above.")

# ---------------------------------------------------------------------------
hr("6. c7: the pin map, the housing count and the ribbon width")
J4_now = ["3V3", "GND", "V5", "IO25", "IO26", "IO27", "IO23"]     # [repo hardware/pcb/pcba/pcba.tsx]
J7_now = ["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"]        # [repo pcba.tsx]
J4_new = ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"]     # swap pins 2 and 5
J7_new = ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI"]        # GND to pin 5


def lds(seq):
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


def score(board, lay):
    pm = {n: i + 1 for i, n in enumerate(board)}
    seq = [pm[n] for n in lay if n != "X"]
    seqn = [pm.get(n) for n in lay]
    return lds(seq), inv(seq), halfrows(seqn)


cases = [
    ("J4 board now", J4_now, ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"], "4P 1-wire+flow pairs | 3P GND+moisture (repo)"),
    ("J4 board now", J4_now, ["3V3", "GND", "V5", "IO25", "IO26", "IO27", "IO23"], "(a') 4P = pins 1-4 | 3P = pins 5-7"),
    ("J4 swap 2<->5", J4_new, ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"], "(a) 4P 1-wire+flow | 3P GND+moisture"),
    ("J7 board now", J7_now, ["RB1", "RB2", "RB3", "RB4", "GND", "X", "CLO", "CHI"], "5P column+GND | 3P X, CLO, CHI (repo)"),
    ("J7 board now", J7_now, ["RB1", "RB2", "RB3", "RB4", "X", "CLO", "CHI", "GND"], "(a') GND on the 3P [procedure-is-the-machine]"),
    ("J7 GND to 5", J7_new, ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI", "X"], "(a) 5P column+GND | 3P CLO, CHI, X"),
]
print(f"  {'board':<14} {'ribbon order at the housing':<46} layers crossings half-rows(off-parity, crossings)")
for tag, board, lay, what in cases:
    l, c, h = score(board, lay)
    print(f"  {tag:<14} {' '.join(lay):<46} {l:>4} {c:>7}      {str(h):<10} {what}")
print("  'off-parity' after a trimmed conductor is a per-loom split-jaw pattern, not a crossing.")
print()
print("  (b) one ribbon, one housing: split each pair housing. Housing overall width C = A + 4.8,")
print("  A = (n-1) x 2.5 [mfr S2]; a row of housings needs the sum of their C plus a gap [assumption 0.5-1 mm]:")
C = lambda n: (n - 1) * 2.5 + 4.8
splits = [("J1", 9, (5, 4)), ("J2", 6, (3, 2)), ("J4", 7, (4, 3)), ("J7", 7, (5, 2))]
tot = 0.0
for name, n, parts in splits:
    now = C(n)
    new = sum(C(k) for k in parts)
    tot += new - now
    print(f"  {name}: XHP-{n} C {now:4.1f} mm -> " + " + ".join(f"XHP-{k}" for k in parts) +
          f" = {new:4.1f} mm: {new-now:+.1f} mm plus one gap")
print(f"  total {tot:+.1f} mm of housing row plus 4 gaps -> ~{tot+2:.0f}-{tot+4:.0f} mm more board edge [estimate]")
ends = {"4P into XHP-4": ["J3", "J5", "J9", "J11", "J13", "J1b", "J4a"],
        "5P into XHP-5": ["J6", "J1a", "J7a"],
        "3P into XHP-3": ["J2b", "J4b"],
        "3P into XHP-2, one trimmed": ["J2a", "J7b"]}
for k, v in ends.items():
    print(f"  {k:<28} {len(v):>2} ends: {', '.join(v)}")
print("  14 ends, 14 housings, 53 crimps unchanged; 4P into XHP-4 becomes 7 ends and 28 crimps (53 %).")
print("  J2 as XHP-3 + XHP-2 drops the empty-cavity guard: each 3P fills its own housing, so landing")
print("  one position off can only happen by using the wrong housing.")

# ---------------------------------------------------------------------------
hr("7. Pre-forming in a host's own press (c6c): pitch at which the tongue clears open neighbours")
tongue_half = 4.45 / 2   # [htq section 5]
for w in (2.46, 2.80, 3.25):
    pmin = tongue_half + 0.1 + w / 2
    print(f"  open neighbour wings {w:.2f} mm: tongue half-width {tongue_half:.2f} + 0.1 clearance -> pitch >= {pmin:.2f} mm")
print("  -> at 3.4 mm the tongue meets open neighbours' wing tips; at 5.0 mm, or on strip at its")
print("     carrier pitch (7-9.5 mm [xh-facts section 1]), it clears them.")
