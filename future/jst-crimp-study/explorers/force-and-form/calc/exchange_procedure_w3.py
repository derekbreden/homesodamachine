"""force-and-form on procedure-is-the-machine, wave 3: numbers for the exchange file.

Run: python3 exchange_procedure_w3.py > exchange_procedure_w3.out.txt

 1. Lift needed, and set left, for each crimp head working one conductor out of a flat
    2.5 mm row: SN tip-down (rolled crimp), SN upright (side-pull / on-edge), and a steel
    die with a fin anvil rising from below between the unlifted neighbours (combination
    FP1). The set model is procedure-is-the-machine's own (calc/wave2.py §1), imported
    read-only.
 2. The fin anvil: width against crimp width, clearance to neighbours at 2.5 mm pitch,
    column checks (FP1 fin against p1 / p5 B-drop fin).
 3. p5: steel stop blocks with a preloaded disc-spring stack under an eccentric. What the
    frame carries on every stroke, and the shaft torque, against a knee at straight.
 4. The proof pull's reaction path: how much jacket squeeze the ribbon clamp needs so a
    20 N pull reaches the copper, and why the jacket cannot carry it.
 5. The neck: blade, brush and strip scatter against the transition length, and what a
    touch-off identity check does to a camera-set depth.
 6. p7: where the push reaches the slug (the cut caps), and the stress there.
 7. Fan pull-back of the fronts after a whole-end strip, at housing pitch and at 5.0 mm
    half-rows (p7 x f5b).
 8. A cam lobe driving a knee (combination FP2): shaft torque from the crimp's energy.

Labels: [assumption] and [estimate] are unmeasured; sources are named where used.
"""

import importlib.util
import math
import os
import sys

sys.dont_write_bytecode = True   # never write into another explorer's directory

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PIM = load("pim_wave2", os.path.join(HERE, "..", "..", "procedure-is-the-machine", "calc", "wave2.py"))
SM = load("fnf_stroke", os.path.join(HERE, "stroke_model.py"))


def section(t):
    print("\n" + "=" * 90)
    print(t)
    print("=" * 90)


# ------------------------------------------------------------------------------------------
PITCH = 2.5          # XHP pitch [mfr S1]
R_J = 0.85           # jacket radius, 1.7 mm OD [source S29]
STOCK = 0.20         # contact stock [source S19-S21]
FLOOR = R_J + STOCK  # contact floor's underside below the conductor axis, jacket resting on the
#                      insulation-barrel floor, floors one plane [assumption, f&f on_into_the_housing §1]
LANCE = (0.6, 0.9)   # lance below the floor [source S22 via f&f calc]
LEGS = (0.3, 0.5)    # crimper legs reach below the floor at bottom, straddling the anvil
#                      [assumption, applicator B-crimp practice]
INS_CRIMP_H = (2.0, 2.3)   # insulation crimp height on this wire [f&f wave2 §5]
MARGIN = 0.3


def s1_lift_and_set():
    section("1. Lift needed and set left, per crimp head, one conductor out of a flat 2.5 mm row")
    print("All heights relative to the row axis; k is lifted by h. Neighbour tops: uncrimped "
          f"+{R_J:.2f}; crimped insulation barrel +{INS_CRIMP_H[0]-FLOOR:.2f}..+{INS_CRIMP_H[1]-FLOOR:.2f}.")
    print()
    print("(a) Steel die, crimper from above, fin anvil rising from below through k's slot (FP1):")
    for label, ntop in (("uncrimped neighbours", R_J), ("crimped, squared neighbours", INS_CRIMP_H[1] - FLOOR)):
        lo = FLOOR + LEGS[0] + ntop + MARGIN
        hi = FLOOR + LEGS[1] + ntop + MARGIN
        print(f"    crimper of any width clears {label:<28}: h >= {lo:.2f}-{hi:.2f} mm")
    # posted contacts for later keys sit over conductors k+-2 when the post bar slides onto k
    lo = FLOOR + LANCE[0] + R_J + MARGIN
    hi = FLOOR + LANCE[1] + R_J + MARGIN
    print(f"    posted contacts for keys k+-2 (lance down) clear their own uncrimped conductors: h >= {lo:.2f}-{hi:.2f} mm")
    print("    -> h = 3.5 mm serves every case; only the fin (<= 3.3 mm wide) passes through the row plane.")
    print()
    print("(b) SN-2549 hung tip-down, jaws closing along the row (p1c, p2 head T, p3 C1, p5b, p6):")
    print("    h = t + 1.85, t = 2-6 mm -> 3.85-7.85 mm; the crimp is ROLLED 90 deg [into-the-housing calc ex §8].")
    BOX_H = 2.4
    top_side = BOX_H - FLOOR
    for ln in LANCE:
        floor_side = FLOOR + ln
        gap = PITCH - top_side - floor_side
        print(f"    rolled row, every floor facing the same way: box top side +{top_side:.2f}, floor side with lance "
              f"-{floor_side:.2f} -> gap to the next rolled box {gap:+.2f} mm")
    print(f"    without the lance: {PITCH - BOX_H:+.2f} mm (into-the-housing §8's 0.1-0.3 mm). With it, each lance")
    print("    overlaps the neighbouring box where the fronts are aligned, which squaring and gang insertion want.")
    print("(c) SN-2549 closing normal to the row, crimp upright (a3-e on-edge side-pull, or the tool on its")
    print("    side): h = a + ~2, a = jaw-half depth behind the nest 6-12 mm [assumption, hand-tool-as-press a3]")
    print("    -> 8-14 mm.")
    print()
    print("Residual rise at the tip after one lift and release, procedure-is-the-machine's model")
    print("(calc/wave2.py §1: elastic-plastic strands 60-120 MPa, silicone 2-6 MPa, tip 5 mm past the")
    print("lift point, 'free' = comb root to lift point; small-deflection, rough at short lengths):")
    print(f"{'free mm':>8}" + "".join(f"{'h ' + str(h):>16}" for h in (3.0, 3.5, 5.0, 8.0, 11.0, 14.0)))
    for a in (15, 20, 25, 30, 35):
        row = f"{a:>8}"
        for h in (3.0, 3.5, 5.0, 8.0, 11.0, 14.0):
            vals = []
            for sy in (60, 120):
                for es in (2, 6):
                    P, pb, ra, rt, pbr = PIM.cantilever(a, h, sy, es)
                    vals.append(rt)
            row += f"{min(vals):>8.2f}-{max(vals):<6.2f} "
        print(row)
    print("-> The fin-from-below die needs 3-3.5 mm of lift and keeps the crimp upright. At 20 mm free")
    print("   that leaves 0-1 mm of rise; at 25 mm and more, essentially none. The tip-down SN needs")
    print("   3.9-7.9 mm and rolls the crimp; making the SN crimp upright needs 8-14 mm, which leaves")
    print("   several mm of set below ~30 mm free and needs a squaring pass on every conductor.")


# ------------------------------------------------------------------------------------------
def s2_fin():
    section("2. The fin anvil: width, clearance at 2.5 mm pitch, column")
    print("Conductor crimp width: JST's analog SXA-01T-P0.6 at 22 AWG 1.50 x 0.80 mm [mfr S14];")
    print("estimate for SXH-001T-P0.6 ~1.5 [xh-facts table]. The anvil sits inside the crimper's channel,")
    print("so anvil = channel - clearance (0.04-0.08) [f&f wave2 §8].")
    print("Crimp height at equal enclosed area, (W - 2t)(H - 2t) = (1.50 - 0.40)(0.80 - 0.40) [estimate]:")
    for w in (1.45, 1.50, 1.60, 1.70, 1.90):
        ch = w + 0.06
        H = 2 * STOCK + (1.50 - 2 * STOCK) * (0.80 - 2 * STOCK) / (ch - 2 * STOCK)
        print(f"  anvil {w:.2f} -> channel ~{ch:.2f}, crimp {ch:.2f} wide x {H:.2f} high")
    print("-> A fin 1.6-1.9 mm wide under the conductor barrel makes a crimp 1.66-1.96 wide and")
    print("   ~0.05-0.12 mm lower than JST's analog profile. For that profile the fin is stepped:")
    print("   ~1.45 under the conductor barrel, ~1.8-1.9 under the insulation barrel.")
    print()
    print("Clearance, fin side to neighbour surface, at the barrels' Y position (k's centre to neighbour")
    print("centre 2.5 mm):")
    neigh = (("uncrimped: bare strands (conductor-step Y)", 0.36),
             ("uncrimped: jacket (insulation-step Y)", R_J),
             ("crimped: conductor crimp", 0.75),
             ("crimped: insulation crimp 1.8-2.0", 1.0))
    for w in (1.45, 1.90):
        for lab, r in neigh:
            print(f"  fin {w:.2f}: {lab:<44} {PITCH - r - w/2:5.2f} mm a side")
    print("  (an open contact's wings, 2.46-3.0 wide, next to a crimped insulation barrel 1.8-2.0 wide,")
    print(f"   leave {(2*PITCH - 3.0 - 2.0)/2:.2f}-{(2*PITCH - 2.46 - 1.8)/2:.2f} mm a side: why k is lifted, not crimped in the row)")
    print()
    E = 200e3
    def euler(b, h, L, K=2.0):
        I = b * h ** 3 / 12
        return math.pi ** 2 * E * I / ((K * L) ** 2)
    print("Column (fixed base, free top, K = 2; the crimper's legs guide the top at compaction):")
    for lab, b, h, L in (("FP1 fin, narrow only through the row band", 3.5, 1.45, 4.0),
                         ("p1/p5 B-drop fin as drawn (hand-tool-as-press R2)", 4.0, 1.6, 10.0),
                         ("B-drop fin narrowed to 1.45 for JST width", 4.0, 1.45, 9.0),
                         ("B-drop fin narrowed to 1.45, 10 mm tall", 4.0, 1.45, 10.0)):
        print(f"  {lab:<52} {b:.1f} x {h:.2f} x {L:4.1f} mm: Euler {euler(b, h, L)/1000:5.1f} kN, "
              f"stress at 3 kN {3000/(b*h):4.0f} MPa")
    print("-> Rising through the row, the fin only has to be narrow over ~4 mm; below the row it widens.")
    print("   Standing 7-10 mm tall between dropped neighbours at the JST width it keeps 5-6 kN")
    print("   against 3 kN free-topped. Ground flat stock stood on edge (1.5 mm gauge plate, +/-0.013)")
    print("   is the fin; its top lapped is the anvil face [f&f wave2 §8].")


# ------------------------------------------------------------------------------------------
E_ECC = 2.5     # p5 eccentric [p5]
L_ROD = 40.0


def z_of(theta):
    """Eccentric height above BDC (mm) at crank angle theta before BDC (rad)."""
    return E_ECC * (1 - math.cos(theta)) + L_ROD - math.sqrt(L_ROD ** 2 - (E_ECC * math.sin(theta)) ** 2)


def stack_x(F, P0, ks):
    return max(0.0, (F - P0) / ks)


def force_at(z, delta0, kf, P0, ks, case):
    """Force in the loop at eccentric height z (mm above BDC). Stops meet when the die reaches
    its final height (y = 0); delta0 = eccentric height at which a rigid machine's stops would
    meet. Frame compliance 1/kf, preloaded stack (rigid below P0, rate ks above)."""
    y_rigid = z - delta0
    Fc0 = SM.total_force(0.0, case)
    # would the dies be held off the stops at the crimp's own peak force?
    if y_rigid + Fc0 / kf + stack_x(Fc0, P0, ks) > 0:
        # dies above the stops: F = Fc(y), y = y_rigid + F/kf + x(F); solve by bisection on F
        lo, hi = 0.0, Fc0
        for _ in range(60):
            F = 0.5 * (lo + hi)
            y = y_rigid + F / kf + stack_x(F, P0, ks)
            if y <= 0:
                hi = F
                continue
            if F < SM.total_force(min(y, 5.0), case):
                lo = F
            else:
                hi = F
        return 0.5 * (lo + hi), False
    # on the stops: y = 0, F from y_rigid + F/kf + x(F) = 0
    lo, hi = Fc0, 200000.0
    for _ in range(80):
        F = 0.5 * (lo + hi)
        if y_rigid + F / kf + stack_x(F, P0, ks) < 0:
            lo = F
        else:
            hi = F
    return 0.5 * (lo + hi), True


def stroke(delta0, kf, P0, ks, case):
    Tmax, th_at, F_bdc = 0.0, 0.0, 0.0
    n = 4000
    for i in range(n, -1, -1):
        th = math.radians(90.0) * i / n
        z = z_of(th)
        F, on = force_at(z, delta0, kf, P0, ks, case)
        dz = (z_of(th + 1e-5) - z_of(th - 1e-5)) / 2e-5 if th > 1e-5 else 0.0
        T = F * dz / 1000.0   # N*m
        if T > Tmax:
            Tmax, th_at = T, math.degrees(th)
        if i == 0:
            F_bdc = F
    return F_bdc, Tmax, th_at


def s3_stops_and_stack():
    section("3. p5: stop blocks + preloaded disc-spring stack under an eccentric; frame load every stroke")
    print(f"Eccentric e {E_ECC} mm, rod {L_ROD} mm [p5]; crimp force curve 'high' (2.43 kN peak) and 'central'")
    print("(1.68 kN) from f&f stroke_model; stack preload P0 3.5-4 kN, rate above preload 3-10 kN/mm")
    print("[assumption: DIN 2093 discs near flat]; stop loop ~670 kN/mm, treated rigid [hand-tool-as-press")
    print("calc H §4]. delta0 = where a rigid machine's stops would meet, above BDC. To be sure of reaching")
    print("the stops, delta0 must exceed the frame's deflection at the crimp peak by a margin m that covers")
    print("frame creep, bearing play and shim error [assumption: m 0.02-0.10 mm].")
    print()
    print(f"{'frame':>7}{'case':>9}{'m':>6}{'P0':>6}{'ks':>5}{'frame load at BDC':>20}{'stack':>7}{'max shaft torque':>18}{'at':>7}")
    for kf in (40.0, 20.0, 10.0, 5.0, 2.0):
        for case in ("high", "central"):
            Fp = SM.total_force(0.0, case)
            for m in (0.02, 0.05, 0.10):
                for P0 in (3500.0,):
                    for ks in (3000.0,):
                        delta0 = Fp / (kf * 1000) + m
                        Fb, Tm, ang = stroke(delta0, kf * 1000, P0, ks, case)
                        eng = "yes" if Fb > P0 + 1 else "no"
                        print(f"{kf:>5.0f}k {case:>9}{m:>6.2f}{P0/1000:>6.1f}{ks/1000:>5.0f}"
                              f"{Fb/1000:>15.2f} kN{eng:>8}{Tm:>14.2f} N*m{ang:>6.0f}d")
    print()
    print("Same, preload 4 kN and a stiffer stack (10 kN/mm), 'high' case:")
    for kf in (40.0, 20.0, 10.0, 5.0):
        Fp = SM.total_force(0.0, "high")
        for m in (0.02, 0.05, 0.10):
            delta0 = Fp / (kf * 1000) + m
            Fb, Tm, ang = stroke(delta0, kf * 1000, 4000.0, 10000.0, "high")
            print(f"  frame {kf:>4.0f} kN/mm, m {m:.2f}: frame load at BDC {Fb/1000:5.2f} kN, max torque {Tm:4.2f} N*m at {ang:3.0f} deg")
    print()
    print("Torque against hand-tool-as-press calc H §4 (adopted in p5), 'high' case, m 0.10, P0 3.5, ks 3:")
    h4 = {2.0: (64, 5.84), 5.0: (41, 4.28), 10.0: (31, 3.36), 20.0: (25, 2.72), 40.0: (21, 2.32)}
    for kf in (2.0, 5.0, 10.0, 20.0, 40.0):
        Fp = SM.total_force(0.0, "high")
        delta0 = Fp / (kf * 1000) + 0.10
        Fb, Tm, ang = stroke(delta0, kf * 1000, 3500.0, 3000.0, "high")
        W_frame = Fb ** 2 / (2 * kf * 1000) / 1000.0
        print(f"  frame {kf:>4.0f} kN/mm: H §4 {h4[kf][1]:.2f} N*m at {h4[kf][0]} deg | this model {Tm:.2f} N*m at {ang:.0f} deg, "
              f"frame load at BDC {Fb/1000:.2f} kN, frame strain energy {W_frame:.2f} J")
    print("  Why they differ: in a compliant loop the stops touch when the eccentric is the margin m above")
    print("  BDC, whatever the frame stiffness (die height y = z - delta0 + F/k = 0 with delta0 = F/k + m")
    print("  gives z = m). Compaction happens earlier in the crank but at lower force, while the frame")
    print("  winds up. H §4 put the whole 2.6 kN at the angle where overtravel = deflection + margin.")
    print("  Energy check: shaft work = crimp work 0.13-0.44 J + frame strain energy (returned after BDC).")
    print()
    print("A doubled contact (a rigid 0.2 mm obstruction), force at BDC, 'high' case, m 0.10:")
    for kf in (40.0, 20.0, 10.0, 5.0):
        Fp = SM.total_force(0.0, "high")
        delta0 = Fp / (kf * 1000) + 0.10
        for P0, ks, lab in ((1e9, 1.0, "no stack"), (3500.0, 3000.0, "stack 3.5 kN, 3 kN/mm")):
            lo, hi = 0.0, 300000.0
            for _ in range(80):
                F = 0.5 * (lo + hi)
                if -delta0 - 0.2 + F / (kf * 1000) + stack_x(F, P0, ks) < 0:
                    lo = F
                else:
                    hi = F
            print(f"  frame {kf:>4.0f} kN/mm, {lab:<22}: {0.5*(lo+hi)/1000:5.2f} kN")
    print()
    print("Knee or crank at a geometric bottom, no stop (for comparison): the frame carries the crimp")
    print("force only; the price is that height moves by force scatter / loop stiffness:")
    for k in (15.0, 40.0, 100.0, 200.0):
        print(f"  local loop {k:>5.0f} kN/mm: +/-300-600 N of scatter -> +/-{300/k:.1f}-{600/k:.1f} um of crimp height")
    print("-> With stops, height does not depend on the loop, and neither does the torque much: the peak")
    print("   is 1.0-2.3 N*m for frames of 2-40 kN/mm, inside a NEMA 17 through 30:1 (3.1 N*m). What the")
    print("   loop stiffness does set is the surplus: the margin m that guarantees reaching the stops")
    print("   costs k x m on every stroke. A stiff frame (>= 20 kN/mm) with m 0.05-0.10 mm reaches the")
    print("   stack's preload every stroke (3.5-4.5 kN, 1.5-2.1x the crimp); a soft loop (5-10 kN/mm)")
    print("   stays at 1.05-1.4x and caps a doubled contact at 3.9-5.4 kN with no stack at all, where a")
    print("   40 kN/mm frame without the stack would put 14 kN into it.")
    print("   With stops, the compliant rod is the design, not the defect. A knee or crank bottom in a")
    print("   small steel C (100-200 kN/mm) is the other route: +/-1.5-6 um, no surplus, no stops.")


# ------------------------------------------------------------------------------------------
def s4_proof_pull_reaction():
    section("4. Proof pull through the box: where the 20 N is reacted")
    print("Strand-in-jacket slip, from f&f wave2 §5 (insulation barrel model), per mm of squeezed length:")
    rows = (("10 % squeeze, E 2.5 MPa", 0.4 / 0.8, 0.8 / 0.8), ("10 % squeeze, E 5.5 MPa", 1.6 / 1.5, 3.1 / 1.5),
            ("30 % squeeze, E 2.5 MPa", 1.1 / 0.8, 2.3 / 0.8), ("30 % squeeze, E 5.5 MPa", 4.7 / 1.5, 9.4 / 1.5))
    for lab, lo, hi in rows:
        print(f"  {lab}: {lo:.1f}-{hi:.1f} N/mm -> clamp length for 20 N {20/hi:5.1f}-{20/lo:5.1f} mm, "
              f"for 30 N (1.5x) {30/hi:5.1f}-{30/lo:5.1f} mm")
    A_cu = 0.302
    A_sil = 1.863
    L = 25.0
    k_cu = 117e3 * A_cu / L
    print()
    print(f"Axial stiffness over {L:.0f} mm of split conductor: copper {k_cu:,.0f} N/mm; "
          f"jacket {2.5*A_sil/L:.2f}-{5.5*A_sil/L:.2f} N/mm")
    print(f"  at a 0.5 mm pull threshold the jacket path carries {0.5*2.5*A_sil/L:.2f}-{0.5*5.5*A_sil/L:.2f} N; "
          "the copper path carries the 20 N in ~"
          f"{20/k_cu*1000:.0f} um")
    print("-> A pull through the box tests the conductor crimp (the jacket cannot carry it at small")
    print("   motion), provided the clamp behind hands 20 N from jacket to copper. A light TPU clamp")
    print("   (a few % squeeze) lets the strands slide back inside the jacket and fails a good crimp.")
    print("   The clamp wants 15-30 % squeeze over 5-20 mm, or the copper anchored some other way")
    print("   (the reel's whole length at a spool; a web clamp at the cassette).")


# ------------------------------------------------------------------------------------------
def s5_neck():
    section("5. The neck: blade, brush and strip scatter; touch-off identity against a camera-set depth")
    blade, clear = 0.30, 0.05
    scatter = 0.20     # strip-length tear, the largest term in procedure-is-the-machine calc wave2 §3
    for brush in (0.10, 0.30):
        need = clear + blade + scatter + 0.05 + brush
        print(f"  blade {blade} + box clearance {clear} + tip gap for +/-{scatter} strip scatter (+0.05) + "
              f"visible brush {brush}: transition t >= {need:.2f} mm")
    print("  t from the clone drawings' length budget: 0.30-2.28 mm; lance relief alone needs t >= 0.34-0.74")
    print("  [f&f on_into_the_housing §1d]. One kit contact side-on under the ELP camera settles t.")
    print()
    EI = 117e3 * math.pi * 0.04 ** 4 / 4
    for Lb in (1.6, 2.1, 2.4):
        P1 = math.pi ** 2 * EI / (4 * Lb ** 2)
        print(f"  bare length {Lb} mm: one 0.08 mm strand buckles at {P1:.3f} N (fixed-free); 60 strands "
              f"{60*P1:.1f} N free, ~{4*60*P1:.0f} N if confined sideways")
    print("-> If the depth comes from the camera (insulation edge mid-window) and identity from strands")
    print("   touching the neck blade, the two disagree by the strip scatter, +/-0.2 mm: half the")
    print("   conductors would be fed 0-0.4 mm past first touch, against a bundle that buckles at")
    print("   ~6-54 N while a lead screw pushes. Take identity where copper is touched anyway (the")
    print("   grounded trim blade in the lifted pose, or strands on the contact floor through a")
    print("   wired post) and keep the tips off the blade by design.")


# ------------------------------------------------------------------------------------------
def seg_area(R, d):
    """Area of a circle's segment above a chord at distance d from the centre."""
    if d >= R:
        return 0.0
    return R * R * math.acos(d / R) - d * math.sqrt(R * R - d * d)


def s6_p7_push():
    section("6. p7: where the blades' faces push the slug")
    print("The kerf cuts each crown to a chord at +/-zs; the blade's front face bears only on that cut")
    print("cap's end face. The flanks and web (|z| < zs) are what must tear [procedure-is-the-machine")
    print("calc wave2 §7]. Silicone 8-11 MPa tensile [digest].")
    for lig in (0.15, 0.20, 0.30):
        zs = 0.36 + lig
        cap = seg_area(R_J, zs)
        chord = 2 * math.sqrt(R_J ** 2 - zs ** 2)
        both = 2 * cap
        print(f"  ligament {lig:.2f} (zs {zs:.2f}): cap end face {cap:.3f} mm2 per blade, {both:.2f} mm2 per "
              f"conductor; chord {chord:.2f} mm; cap-to-slug shear area {chord*2.4:.2f} mm2 per cap")
        for F in (3.0, 10.0, 15.0):
            print(f"      push {F:4.0f} N per conductor -> {F/both:5.1f} MPa on the cap faces, "
                  f"{F/2/(chord*2.4):4.2f} MPa shear under each cap")
    print("  neo-Hookean compression, E 4 MPa: nominal stress 10 / 20 / 30 MPa needs stretch "
          + " / ".join(f"{lam:.2f}" for lam in (0.34, 0.25, 0.21)) + " (strain 66-79 %)")
    print("-> Against 10-15 N per conductor (the tension bound) the caps carry 15-29 MPa at ligaments")
    print("   0.15-0.20 and 36-54 MPa at 0.30, on 0.3-0.65 mm2: 2-5x silicone's tensile strength on a")
    print("   face that is free on top. The 0.14-0.34 mm caps crush and can roll over the blade edges")
    print("   before the flanks tear. At the low tear figure (3 N) it is 5-11 MPa, marginal. The thicker")
    print("   the ligament (safer strands), the smaller the cap and the worse this gets.")
    print("   A pad pair gripping the slug's top and bottom ahead of")
    print("   the blades spreads the push over the caps' tops (~2.6-3 mm2 each): ~3-4 MPa of pad")
    print("   pressure at friction ~0.8 carries 15 N per conductor.")


# ------------------------------------------------------------------------------------------
def s7_fan():
    section("7. Fronts after a whole-end strip, then a fan (S-bend excess length 0.6 d^2 / L)")
    print("Check against procedure-is-the-machine calc exchange_borrowed §7 (4P 0.05, 5P 0.09, J1 0.35 at 15 mm):")
    for lab, d in (("4P 1.7->2.5 outer", 1.2), ("5P 1.7->2.5 outer", 1.6), ("J1 nine 1.7->2.5 outer", 3.2)):
        print(f"  {lab:<30} d {d:.1f}:  L 8 mm {0.6*d*d/8:.2f}   L 15 mm {0.6*d*d/15:.2f}")
    print("Half-rows at 5.0 mm from a plane at 3.4 mm (f5b / change-the-question c1):")
    for n, d in ((2, 0.8), (3, 1.6), (4, 2.4), (5, 3.2)):
        print(f"  row of {n}: outer d {d:.1f} mm:  L 12 mm {0.6*d*d/12:.2f}   L 20 mm {0.6*d*d/20:.2f} mm")
    print("-> Strip-before-split puts every insulation edge on one line, and a fan then moves the outer")
    print("   edges back by 0.6 d^2/L. Rows of 2-3 at 5.0 mm stay inside +/-0.1 mm; rows of 4-5 lose")
    print("   0.2-0.5 mm, most of a +/-0.3 mm window, unless the fixed pockets are staggered by the")
    print("   computed amount or the strip is made after the spread.")


# ------------------------------------------------------------------------------------------
def s8_cam_knee():
    section("8. A cam lobe driving a knee in a small steel C (FP2): shaft torque from crimp work")
    for case in ("low", "central", "high"):
        pts = SM.profile(case)
        W = sum(0.5 * (f1 + f2) * (s1 - s2) for (s1, f1), (s2, f2) in zip(pts, pts[1:])) / 1000.0
        for deg in (40, 60):
            avg = W / math.radians(deg)
            print(f"  {case:<8} work {W:.2f} J over a {deg} deg lobe: average {avg:.2f} N*m, "
                  f"peak ~{2*avg:.2f}-{3*avg:.2f} N*m at a 2-3x profile factor [estimate]")
    print("  plus the knee's own friction and return spring [estimate +0.1-0.3 N*m]")
    print("-> A lobe that drives the knee through straight needs well under the 2.1-3.2 N*m p5b's lobe")
    print("   needs for the SN handle, and the printed cam frame carries only the knee's input")
    print("   (60-160 N) while the crimp closes inside the steel C.")


def main():
    s1_lift_and_set()
    s2_fin()
    s3_stops_and_stack()
    s4_proof_pull_reaction()
    s5_neck()
    s6_p7_push()
    s7_fan()
    s8_cam_knee()


if __name__ == "__main__":
    main()
