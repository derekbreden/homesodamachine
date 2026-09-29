"""Wave 2 numbers for procedure-is-the-machine.

Run: python3 wave2.py > wave2.out.txt

 1. Set left in a conductor: one lift (lift once, do everything in that pose) against a presser
    that pushes every waiting conductor down. Elastic-plastic strands, elastic silicone.
 2. Spool curl: what the spool's own winding leaves in the ribbon, and the hub radius a
    rewind reel needs so it adds none.
 3. Axial chain for the lift-once station (p1c, p6 stage 2): where the insulation edge lands.
 4. Two heads, one person (p4b): the person's minutes against machine cycle time.
 5. The camshaft squeezes the hand tool (p5b): shaft torque per lobe and follower stress.
 6. The spool-end bench that grows (p6): attended minutes, unattended stretch and rough
    cost at each stage, from one task library.
 7. Strip before split (p7): what two straight blades leave to tear across a whole webbed
    ribbon end, and why pitch error does not matter to them.

Labels: every input is marked where it is set. [assumption] and [estimate] are not measured.
"""

import math

# ----------------------------------------------------------------------------------------
# conductor (xh-facts §7, digest): 60 x 0.08 mm tinned strands, jacket OD 1.7 mm
N_STRAND = 60
R_STRAND = 0.04          # mm
E_CU = 117000.0          # MPa, annealed copper [source class value]
BUNDLE_R = 0.36          # mm, strand bundle radius (0.72 mm across) [digest]
OD = 1.7
I_SIL = math.pi / 64 * (OD ** 4 - (2 * BUNDLE_R) ** 4)   # mm^4
I_STRAND = math.pi / 4 * R_STRAND ** 4
EI_S = N_STRAND * E_CU * I_STRAND                        # N*mm^2


def section(t):
    print("\n" + "=" * 90)
    print(t)
    print("=" * 90)


def m_strand(kappa, sy):
    """Bending moment of one elastic-perfectly-plastic round strand at curvature kappa.
    Closed form: elastic core of half-depth c = sy/(E kappa), plastic outside it."""
    if kappa <= 0:
        return 0.0
    r = R_STRAND
    c = min(sy / (E_CU * kappa), r)
    el = 4 * E_CU * kappa * ((c / 8) * (2 * c * c - r * r) * math.sqrt(max(r * r - c * c, 0.0))
                             + (r ** 4 / 8) * math.asin(c / r))
    pl = (4.0 / 3.0) * sy * max(r * r - c * c, 0.0) ** 1.5
    return el + pl


def m_total(kappa, sy, e_sil):
    return N_STRAND * m_strand(kappa, sy) + e_sil * I_SIL * kappa


def kappa_for(M, sy, e_sil):
    lo, hi = 0.0, 5.0
    for _ in range(45):
        mid = (lo + hi) / 2
        if m_total(mid, sy, e_sil) < M:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def residual_kappa(kappa, sy, e_sil):
    """Curvature left after the load is removed (elastic unloading, no reverse yield)."""
    ei_sil = e_sil * I_SIL
    return max((EI_S * kappa - N_STRAND * m_strand(kappa, sy)) / (EI_S + ei_sil), 0.0)


def cantilever(a, h, sy, e_sil, stick=5.0, nseg=50):
    """Conductor fixed at x=0, lifted by h at x=a by a point load, free tip at a+stick.
    Returns (P, loaded tip pull-back, residual rise at the lift point, residual rise at the tip,
    residual tip pull-back). Small-deflection integration."""
    def solve(P):
        xs, ks = [], []
        for i in range(nseg):
            x = (i + 0.5) * a / nseg
            ks.append(kappa_for(P * (a - x), sy, e_sil))
            xs.append(x)
        return xs, ks

    def defl(xs, ks, at):
        return sum(k * (at - x) * (a / nseg) for x, k in zip(xs, ks) if x < at)

    lo, hi = 0.0, 50.0
    for _ in range(30):
        mid = (lo + hi) / 2
        xs, ks = solve(mid)
        if defl(xs, ks, a) < h:
            lo = mid
        else:
            hi = mid
    P = (lo + hi) / 2
    xs, ks = solve(P)
    # slope along the loaded beam, then pull-back = 1/2 int theta^2
    th, pb, t = [], 0.0, 0.0
    for k in ks:
        t += k * a / nseg
        th.append(t)
        pb += 0.5 * t * t * a / nseg
    pb += 0.5 * t * t * stick
    kr = [residual_kappa(k, sy, e_sil) for k in ks]
    rise_a = sum(k * (a - x) * (a / nseg) for x, k in zip(xs, kr))
    slope_a = sum(k * a / nseg for k in kr)
    rise_tip = rise_a + slope_a * stick
    t, pbr = 0.0, 0.0
    for k in kr:
        t += k * a / nseg
        pbr += 0.5 * t * t * a / nseg
    pbr += 0.5 * t * t * stick
    return P, pb, rise_a, rise_tip, pbr


def s1_set():
    section("1. Set left in a conductor by one lift, against a presser that pushes the waiting ones down")
    print(f"EI strands {EI_S:.1f} N*mm^2; silicone jacket I = {I_SIL:.3f} mm^4, EI {2*I_SIL:.1f}-{6*I_SIL:.1f} "
          "N*mm^2 at E 2-6 MPa [assumption]")
    print("strand yield 60-120 MPa [assumption, annealed tinned copper]; small-deflection theory, so")
    print("figures at short free lengths are rough. 'free' = comb root (fixed) to the lift point; the tip")
    print("sticks out 5 mm past it.")
    print()
    print("(a) Presser: every waiting conductor pushed 7 mm down near its tip, released (sanity check")
    print("    against hand-tool-as-press calc H §1: 10 mm 4.3-5.7, 15 mm 2.7-4.7, 20 mm 1.0-3.4, 30 mm 0-0.7)")
    print(f"{'free mm':>8}{'sy MPa':>8}{'Esil':>6}{'residual drop at press pt':>28}{'at tip':>9}{'tip pull-back':>15}")
    for a in (10, 15, 20, 30):
        for sy in (60, 120):
            for es in (2, 6):
                P, pb, ra, rt, pbr = cantilever(a, 7.0, sy, es)
                print(f"{a:>8}{sy:>8}{es:>6}{ra:>22.2f} mm{rt:>9.2f}{pbr:>12.2f} mm")
    print()
    print("(b) Lift once: conductor k lifted h at the station, worked in that pose, laid back once.")
    print("    h = t + 1.85 mm for a tip-down SN jaw whose usable nest is t from the jaw tip [calc P")
    print("    selector_and_bow §1 inverted; hand-tool-as-press exchange]; t = 2-6 mm -> h = 3.9-7.9 mm")
    print(f"{'free mm':>8}{'h mm':>6}{'residual rise at tip (sy 60..120, Esil 2..6)':>48}{'loaded pull-back':>18}")
    for a in (15, 20, 25, 30):
        for h in (4.0, 6.0, 8.0):
            vals, pbs = [], []
            for sy in (60, 120):
                for es in (2, 6):
                    P, pb, ra, rt, pbr = cantilever(a, h, sy, es)
                    vals.append(rt)
                    pbs.append(pb)
            print(f"{a:>8}{h:>6.0f}{min(vals):>36.2f} - {max(vals):.2f} mm"
                  f"{min(pbs):>12.2f}-{max(pbs):.2f} mm")
    print("-> With a presser, every conductor still waiting carries the first press's set into its own")
    print("   turn: keys 2..N arrive low by the residual drop, and their tips short by the pull-back.")
    print("   With a lifter, only k is bent, and all of k's work (trim, strip, measure, crimp, pull) is")
    print("   done in the same bent pose, so k's own set never enters its own crimp. What remains is")
    print("   k's set after it is laid back: the crimped contact sits high by the residual rise until a")
    print("   squaring comb presses it into the row (copper that yielded re-yields; over-press by the")
    print("   springback). The waiting conductors are never touched.")


# ----------------------------------------------------------------------------------------
def s2_curl():
    section("2. Spool curl: what winding leaves in the ribbon, and a rewind reel that adds none")
    print("Each conductor bends about its own centre when the flat ribbon is wound (all centres lie in")
    print("the midplane), so the single-conductor model above applies. Ribbon thickness 1.7 mm per layer")
    print("[repo]; 15.24 m per spool [repo]; the BNTECHGO hub radius is unrecorded [assumption: 25-60 mm].")
    for sy in (60, 120):
        ry = R_STRAND * E_CU / sy
        print(f"  strand yield {sy} MPa -> first yield at bend radius {ry:.0f} mm; "
              f"springback carries up to ~1.7x that curvature")
    print()
    print(f"{'wound R mm':>11}{'residual R (sy 60/120, Esil 2..6) mm':>40}{'free end 20 mm rises':>24}{'40 mm':>10}")
    for Rw in (25, 35, 50, 70, 90):
        rr, t20, t40 = [], [], []
        for sy in (60, 120):
            for es in (2, 6):
                kr = residual_kappa(1.0 / Rw, sy, es)
                rr.append(1 / kr if kr > 1e-9 else float("inf"))
                t20.append(kr * 20 ** 2 / 2)
                t40.append(kr * 40 ** 2 / 2)
        rtxt = f"{min(rr):.0f} - " + ("straight" if max(rr) == float("inf") else f"{max(rr):.0f}")
        print(f"{Rw:>11}{rtxt:>40}{min(t20):>15.2f}-{max(t20):.2f} mm{min(t40):>6.1f}-{max(t40):.1f}")
    print()
    print("Where on the spool the ribbon was wound tight enough to take a set (15.24 m, 1.7 mm/layer):")
    for r0 in (25, 40, 60, 80):
        # n turns: sum 2*pi*(r0 + 1.7 i) = L
        L = 15240.0
        a_, b_, c_ = math.pi * 1.7, 2 * math.pi * r0, -L
        n = (-b_ + math.sqrt(b_ * b_ - 4 * a_ * c_)) / (2 * a_)
        rout = r0 + 1.7 * n
        frac = []
        for ry in (39.0, 78.0):
            if ry <= r0:
                frac.append(0.0)
                continue
            m = min((ry - r0) / 1.7, n)
            wound = math.pi * 1.7 * m * m + 2 * math.pi * r0 * m
            frac.append(wound / L)
        print(f"  hub r {r0:>3} mm: {n:5.1f} turns, outer r {rout:5.0f} mm (OD {2*rout:4.0f}); "
              f"length wound below first-yield radius: {frac[0]*100:4.0f}% (yield 120 MPa) to "
              f"{frac[1]*100:4.0f}% (60 MPa)")
    print("-> A rewind reel with an 80 mm hub radius (OD ~240 mm full, 15.24 m of any width) adds no set")
    print("   and brings the inner end out through the hub. It does not remove curl already in the")
    print("   ribbon; a roller straightener (reverse bends through 3-5 rollers) between spool and reel,")
    print("   or at the machine's feed, does. A clamp holds the ribbon flat up to its face, so curl")
    print("   matters only in the free length past the clamp: 20-40 mm of split conductors.")


# ----------------------------------------------------------------------------------------
def rss(v):
    return math.sqrt(sum(x * x for x in v))


def s3_axial():
    section("3. Axial chain at a lift-once station: where the insulation edge lands in the window")
    print("Window: insulation edge between the barrels, brush visible, ~+/-0.3 mm usable [estimate, wave 1];")
    print("contact in the die ~+/-0.1 mm for the bellmouth [hand-tool-as-press calc H1 §7].")
    rows = [
        ("wave 1 p1, strip elsewhere, no wire stop",
         [("trim blade to cassette", 0.05), ("cassette to station", 0.05), ("strip length, V-jaw tear", 0.20),
          ("lift retraction, ragged split", 0.27), ("contact: pilot hole", 0.075)]),
        ("lift once, strip in pose, contact by box front",
         [("tool Y stage repeat", 0.02), ("strip length, tear", 0.20), ("contact: box front on a stop", 0.25)]),
        ("lift once, strip in pose, contact by neck blade",
         [("tool Y stage repeat", 0.02), ("strip length, tear", 0.20), ("contact: blade on box shoulder", 0.075)]),
        ("lift once, camera measures bare length, Y corrects; neck blade",
         [("tool Y stage repeat", 0.02), ("camera edge on backlit strands", 0.05),
          ("contact: blade on box shoulder", 0.075)]),
        ("lift once, camera; contact on a post, offset measured on the post (x1)",
         [("tool Y stage repeat", 0.02), ("camera edge on backlit strands", 0.05),
          ("contact: post + camera offset", 0.05)]),
        ("touch-off on the strand tips (no camera), neck blade",
         [("tool Y stage repeat", 0.02), ("touch-off at first strand", 0.05), ("strip length, tear", 0.20),
          ("contact: blade on box shoulder", 0.075)]),
    ]
    for name, terms in rows:
        w = sum(t for _, t in terms)
        print(f"  {name:<70} worst +/-{w:.2f}  RSS +/-{rss([t for _, t in terms]):.2f}")
    print("-> Doing trim, strip and crimp to conductor k in one pose removes the split-point term. The")
    print("   strip-length tear is then the largest term left, and only a measurement of where the edge")
    print("   actually is (camera on a backlit tip, or a scored edge) takes it out. Touch-off finds the")
    print("   strand tips, which is the wrong end for the insulation edge.")


# ----------------------------------------------------------------------------------------
def s4_rhythm():
    section("4. Two heads, one person (p4b): the person's minutes against machine cycle time")
    N, ENDS, HOUS = 53, 14, 10
    fixed_today = ENDS * (20 + 40) + HOUS * 30          # cut + peel per end, test + label per housing
    hand = fixed_today + N * (8 + 15 + 8)
    print(f"today by hand, same task library as wave 1: {hand/60:.0f} min (cut 20 s, peel 40 s per end;")
    print("strip 8 s, crimp 15 s, insert 8 s per conductor; test and label 30 s per housing) [estimate]")
    print()
    print(f"{'machine cycle':>14}{'present':>9}{'insert':>8}{'1 head min':>12}{'2 heads min':>13}{'person waits/cond (2 heads)':>30}")
    for c in (20, 26, 35, 45):
        for p, i in ((4, 6), (6, 10)):
            per1 = max(p + i, c)
            per2 = max(p + i, c / 2)
            tot1 = fixed_today + N * per1
            tot2 = fixed_today + N * per2
            print(f"{c:>12} s{p:>8} s{i:>6} s{tot1/60:>12.0f}{tot2/60:>13.0f}{max(0, c/2 - p - i):>25.1f} s")
    print("-> One head saves minutes only if its cycle beats the ~31 s of a hand strip-crimp-insert;")
    print("   two heads make the person's own present-and-insert pace the rhythm at any cycle up to")
    print("   ~2x that pace (20-32 s). Machine cycle includes strip, contact drop, hold, feed to")
    print("   touch-off, crimp with a slow last 8 mm of grip, blade proof pull, release [estimate].")


# ----------------------------------------------------------------------------------------
def s5_cam():
    section("5. The camshaft squeezes the hand tool (p5b): torque per lobe, follower stress")
    print("Handle need 90-220 N at the grip [hand-tool-as-press calc H1 §1, source class]; approach")
    print("~45 mm of grip travel at ~20 N (return spring) [estimate]; the last ~8 mm of grip carries the")
    print("compaction [calc H1 §4].")
    lobes = [("approach, 45 mm over 120 deg at 20 N", 45, 120, 20),
             ("hold click, 3 mm over 20 deg at 40 N", 3, 20, 40),
             ("squeeze, 8 mm over 40 deg at 220 N", 8, 40, 220),
             ("squeeze through a spring link preloaded 275 N", 8, 40, 275),
             ("squeeze, 8 mm over 60 deg at 275 N", 8, 60, 275)]
    for name, rise, deg, F in lobes:
        T = F * rise / math.radians(deg) / 1000
        print(f"  {name:<52} shaft torque {T:4.2f} N*m")
    print("  drives at the shaft [calc P cam_drive §1; force-and-form source]: NEMA17 + 30:1 worm ~3.1 N*m,")
    print("  + 50:1 ~4.5 N*m, the bench NEMA23 + 30:1 ~12.6 N*m; StepperOnline NEMA23 + NMRV30 30:1 rated 20 N*m.")
    print()
    print("Follower on a printed lobe (steel roller on PET-CF, E ~5-8 GPa printed [assumption]; line contact):")
    for F in (220, 275):
        for Lw in (8, 16):
            for R1, R2 in ((8, 60),):
                Re = 1 / (1 / R1 + 1 / R2)
                for Ep in (5000, 8000):
                    Es = Ep / (1 - 0.35 ** 2)
                    p = math.sqrt(F * Es / (math.pi * Lw * Re))
                    print(f"  F {F} N, roller 16 mm dia x {Lw} mm on a R{R2} lobe, E {Ep/1000:.0f} GPa: "
                          f"peak contact {p:4.0f} MPa")
    print("-> The squeeze lobe sets the motor (2.5-3.3 N*m through a 40 deg lobe; stretch it to 60 deg")
    print("   and it falls to ~2.1 N*m). A printed lobe under a narrow roller is near a printed")
    print("   part's compressive limit; a steel wear strip on the squeeze lobe, or a 16 mm wide")
    print("   roller, carries it.")


# ----------------------------------------------------------------------------------------
def s6_stages():
    section("6. The spool-end bench that grows (p6): minutes, unattended stretch and cost by stage")
    N, ENDS, HOUS = 53, 14, 10
    SPOOL_CHANGES = 1 / 5.4 + 1 / 8 + 1 / 11      # per unit, one of each spool type mounted [calc unit_inventory]
    t = {  # seconds [estimate], same task library as wave 1 where the task is the same
        "cut": 20, "peel": 40, "strip": 8, "hand crimp": 15, "insert": 8, "test label": 30,
        "draw to peg and cut": 15, "plug hub lead, test, unplug": 15, "partner nest a pair": 30,
        "spool change and rewind": 180 + 300,
        "place contact (post pen) + index + lift + push to light": 12, "machine crimp wait": 15,
        "load one contact on the post revolver": 4, "start an end": 10, "clamp and thread an end": 20,
        "load housing tube": 60, "label": 10,
    }
    stages = []
    # stage 0: today's hand work, at the spool
    person = (ENDS * (t["draw to peg and cut"] + t["peel"] + t["plug hub lead, test, unplug"])
              + N * (t["strip"] + t["hand crimp"] + t["insert"])
              + 4 * t["partner nest a pair"] + HOUS * t["label"]
              + SPOOL_CHANGES * t["spool change and rewind"])
    stages.append(("0 hand work at the spool", person, 0, "$25-45"))
    # stage 1: powered crimp at the clamp; person places contact, indexes, pushes; waits on crimp
    person = (ENDS * (t["draw to peg and cut"] + t["peel"] + t["plug hub lead, test, unplug"])
              + N * (t["strip"] + t["place contact (post pen) + index + lift + push to light"]
                     + t["machine crimp wait"] + t["insert"])
              + 4 * t["partner nest a pair"] + HOUS * t["label"]
              + SPOOL_CHANGES * t["spool change and rewind"])
    stages.append(("1 + powered crimp at the clamp", person, 0, "+$100-170"))
    # stage 2: motors on the stage-1 screws walk the row, post revolver in loom order; person splits, strips all, loads revolver
    per_cond_machine = 75
    person = (ENDS * (t["draw to peg and cut"] + t["peel"] + t["start an end"])
              + N * (t["strip"] + t["load one contact on the post revolver"] + t["insert"])
              + 4 * t["partner nest a pair"] + HOUS * t["label"]
              + SPOOL_CHANGES * t["spool change and rewind"])
    stages.append(("2 + motors on the same screws, post revolver", person, 9 * per_cond_machine, "+$90-140"))
    # stage 3: strip at the clamp (in pose, or p7's whole-end stroke)
    person = (ENDS * (t["draw to peg and cut"] + t["peel"] + t["start an end"])
              + N * (t["load one contact on the post revolver"] + t["insert"])
              + 4 * t["partner nest a pair"] + HOUS * t["label"]
              + SPOOL_CHANGES * t["spool change and rewind"])
    stages.append(("3 + strip at the clamp", person, 9 * (per_cond_machine + 30), "+$20-60"))
    # stage 4: powered draw-off, guillotine, gang insertion of singles from a tube, slip ring; batch by spool
    # person: split each end (peel) still, load post revolvers in bulk, pairs (28 contacts) by hand
    person = (ENDS * t["peel"] + N * t["load one contact on the post revolver"]
              + 28 * t["insert"] + 4 * t["partner nest a pair"] + HOUS * t["label"]
              + 3 * t["load housing tube"] / 5 + SPOOL_CHANGES * t["spool change and rewind"])
    # the machine stops per end for the split unless stage 5; longest alone = one end
    stages.append(("4 + draw-off, guillotine, gang insert", person, 9 * (per_cond_machine + 30) + 120,
                   "+$120-200"))
    # stage 5: split at the clamp; the machine runs a spool's singles alone
    person = (N * t["load one contact on the post revolver"] + 28 * t["insert"]
              + 4 * t["partner nest a pair"] + HOUS * t["label"]
              + 3 * t["load housing tube"] / 5 + SPOOL_CHANGES * t["spool change and rewind"])
    run_4p = 5 * (20 * (per_cond_machine + 30) + 5 * 150) + 5 * 8 * (per_cond_machine + 30)
    stages.append(("5 + split at the clamp", person, run_4p, "+$20-60"))
    today = ENDS * (t["cut"] + t["peel"]) + N * (t["strip"] + t["hand crimp"] + t["insert"]) + HOUS * t["test label"]
    print(f"today by hand, same library: {today/60:.0f} min per unit [estimate; compare rows, not the ledger]")
    print(f"{'stage':<44}{'person min/unit':>16}{'longest alone':>15}{'added cost':>12}")
    for name, p, alone, cost in stages:
        a = "-" if alone == 0 else (f"{alone/60:.0f} min" if alone < 5400 else f"{alone/3600:.1f} h")
        print(f"{name:<44}{p/60:>16.0f}{a:>15}{cost:>12}")
    print("Notes:")
    print(" - Stage 0 and 1 add the per-end test through the spool (15 s) and change nothing else; they buy")
    print("   recovery at the spool, identity and pin order before the cut, pair lengths equal by the peg,")
    print("   and (stage 1) a force curve and identity for every crimp. They do not save minutes.")
    print(" - Stage 2's 'longest alone' is one 9-conductor end (J1); the person strips and loads a column")
    print("   per end, so the machine calls ~14 times a unit, as p2 did.")
    print(" - Stage 4 counts the 25 crimps of the six single-ribbon housings as gang-inserted; the four")
    print("   pairs (28 contacts) are inserted by hand at the partner nest.")
    print(" - Stage 5's 'longest alone' is the 4P spool: five units of 4P ends (J3, J5, J9, J11, J13 plus")
    print("   the 4P halves of J1 and J4), made while the printers run.")
    print(" - The per-end test through the spool replaces today's pin test; stage rows count 10 s of labelling")
    print("   per housing where today's row counts 30 s of test and label.")
    print(" - Costs are rough [estimate]: parts beyond what the bench already has (SN-2549, NEMA 23 set,")
    print("   ELP camera, printers). Stage 1 builds its slides as lead-screw slides turned by knobs, so")
    print("   stage 2 adds only motors, a board, a servo and a post revolver to the same screws. A $199")
    print("   Ender-3 V3 SE [source: machine-that-sees-and-learns, Creality store 2026-09-28] is the")
    print("   alternative if the gantry is bought instead of grown.")
    print()
    print("Stage 0 details:")
    print(" - The hub lead is plugged only while the spool stands still (termination and test), so it never")
    print("   twists: 0 turns, no slip ring until stage 4 powers the draw-off.")
    print(" - Draw to a peg: the housing is clipped to a peg at the loom's length from the clamp face; hand")
    print("   pull of a few newtons on silicone ribbon stretches it well under 1 mm on 600 mm")
    E_sil_bulk = 4.0   # MPa, the jacket and web carry little; copper carries the pull
    area_cu = N_STRAND * math.pi * R_STRAND ** 2
    for F in (2, 5, 10):
        strain = F / (area_cu * E_CU)
        print(f"   pull {F:>2} N on one conductor's copper ({area_cu:.2f} mm^2): {strain*600*1000:.1f} um on 600 mm"
              " (copper carries it; silicone stretches with it)")
    print("   Peg placement +/-1 mm and ribbon lying straight on the rail set the length: ~+/-1-2 mm [estimate].")


# ----------------------------------------------------------------------------------------
def band_area(zs, R=OD / 2, r=BUNDLE_R, n=400):
    """Area of the jacket (between r and R) inside |z| < zs, per conductor."""
    tot = 0.0
    dz = 2 * zs / n
    for i in range(n):
        z = -zs + (i + 0.5) * dz
        outer = 2 * math.sqrt(max(R * R - z * z, 0.0))
        inner = 2 * math.sqrt(max(r * r - z * z, 0.0))
        tot += (outer - inner) * dz
    return tot


def s7_strip_before_split():
    section("7. Strip before split (p7): two straight blades across the whole webbed end")
    print("Blades close from above and below across the full ribbon width and stop at +/-zs from the")
    print("conductor centre plane. Each crown is cut to a chord; what is left to tear is the band |z|<zs")
    print("of every jacket, plus the web in the valley (web neck thickness unmeasured). Strand bundle")
    print(f"radius {BUNDLE_R} mm, jacket OD {OD} mm (wall 0.49 mm) [digest].")
    print(f"{'ligament over strands':>22}{'zs':>7}{'band area/cond':>16}{'tension bound 8-11 MPa':>25}"
          f"{'3P':>10}{'4P':>10}{'5P':>10}{'5P+4P':>11}")
    for lig in (0.15, 0.20, 0.30):
        zs = BUNDLE_R + lig
        A = band_area(zs)
        lo, hi = 8 * A, 11 * A
        print(f"{lig:>20.2f} mm{zs:>7.2f}{A:>13.2f} mm2{lo:>15.1f}-{hi:.1f} N/cond"
              + "".join(f"{n*lo:>6.0f}-{n*hi:<4.0f}" for n in (3, 4, 5)) + f"{9*lo:>6.0f}-{9*hi:.0f} N")
    print("  Tearing from the two score lines takes less than the tension bound: the digest gives 3-15 N per")
    print("  conductor for a 0.15-0.3 mm ligament cut all round, and borrowed-machines 4-11 N scored top and")
    print("  bottom to 80 % [calc geometry §3]. A 5P end is ~20-75 N of pull: a lead screw or a hand lever.")
    print()
    print("Margins that set the ligament (straight blades):")
    terms = [("strand bundle off-centre in its jacket [assumption]", 0.05, 0.10),
             ("blade stop to channel floor (steel stop, printed floor)", 0.02, 0.03),
             ("jacket OD tolerance / 2 (1.7 +/- 0.1 -> centre height)", 0.05, 0.05),
             ("channel floor flatness under the clamp", 0.02, 0.03)]
    for n_, lo, hi in terms:
        print(f"   {n_:<60} +/-{lo:.2f}-{hi:.2f} mm")
    lo = rss([x[1] for x in terms])
    hi = rss([x[2] for x in terms])
    print(f"   RSS +/-{lo:.2f}-{hi:.2f} mm  -> a 0.15 mm ligament is inside the scatter at the high end;"
          f" 0.20-0.30 mm keeps the blade off the strands")
    print()
    print("Pitch error: straight blades cut every crown at the same height whatever the conductor's x,")
    print("so the ribbon's +/-0.1 mm per conductor (0.43 mm worst from a centred datum on 9 [ribbon-as-")
    print("pallet calc §1]) does not matter. Scalloped cutters (US 4,046,045) cut closer at the flanks but")
    print("their notches must sit on each conductor: an offset d moves the flank cut d toward the strands.")
    for lig in (0.15, 0.25, 0.35):
        for off in (0.1, 0.2, 0.43):
            print(f"   scallop ligament {lig:.2f} mm, notch offset {off:.2f} mm -> flank ligament {lig-off:+.2f} mm"
                  + ("  (cuts strands)" if lig - off <= 0 else ""))
    print()
    print("Strip line after the fan: the strip line is straight across the webbed ribbon; fanning 1.7 ->")
    print("2.5 mm afterwards pulls the outer conductors' fronts back [calc P exchange_borrowed §7]:")
    print("  split 8 mm: 4P 0.09, 5P 0.16, J1 9 0.67 mm; split 15 mm: 4P 0.05, 5P 0.09, J1 9 0.35 mm.")
    print("  The insulation edge stays where it is on each conductor, so the crimp's own axial chain is")
    print("  unaffected; only the fronts for gang insertion move, and single ribbons stay inside +/-0.3 mm.")


def main():
    s1_set()
    s2_curl()
    s3_axial()
    s4_rhythm()
    s5_cam()
    s6_stages()
    s7_strip_before_split()


if __name__ == "__main__":
    main()
