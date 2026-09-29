"""Wave 3 numbers for procedure-is-the-machine.

Run: python3 wave3.py > wave3.out.txt

 1. Lift and the set it leaves, per crimp-head pose that makes an upright crimp from a flat row:
    a fin anvil rising from below (p1d, p5c) against an SN-2549 closing normal to the row
    (p1c, p5b, p6 stage 1-SN), using the wave-2 elastic-plastic set model (wave2.py §1).
 2. The fin anvil: its travel, its clearance to the neighbours at each barrel step, where the
    tip comb can stand, its column strength, and the laminated-shim route to its two widths.
 3. A knee near straight: how little the bottom moves with the knee's lateral position.
 4. Stops under an eccentric (p5): the surplus force a margin costs, and what a doubled contact
    meets, with and without a compliant loop.
 5. p7's slug push: pads on the slug, and why they must grip the jacket harder than the jacket
    grips the strands.
 6. Cycle and person minutes for p1d and p5c, on the wave-2 task library.
 7. Consistency: p5b's squeeze-lobe work against the crimp's work.

Labels: every input is marked where it is set. [assumption] and [estimate] are not measured.
"""

import math

import wave2 as w2   # the wave-2 set model: cantilever(a, h, sy, e_sil)

BUNDLE_R = w2.BUNDLE_R     # 0.36 mm [digest]
OD = w2.OD                 # 1.7 mm [xh-facts §7]
PITCH = 2.5                # mm, housing pitch [mfr S1]
STOCK = 0.20               # mm, contact stock [source S19-S21 via xh-facts §1]


def section(t):
    print("\n" + "=" * 92)
    print(t)
    print("=" * 92)


# ----------------------------------------------------------------------------------------------
def s1_lift_and_set():
    section("1. Lift needed for an upright crimp from a flat row, and the set each lift leaves in k")
    print("Only k is lifted; the neighbours stay in the row. Heights from the row axis.")
    print("(a) Fin anvil from below (p1d, p5c): only the fin passes through the row plane, in k's own")
    print("    empty slot. The crimper is <= 3.1-4 mm wide [force-and-form f8], so it never overlaps a")
    print("    neighbour laterally; the lift has to clear the posted contacts' lances over their own")
    print("    unlifted conductors and the crimped neighbours' tops (+0.95..+1.25):")
    print("    h >= 2.8-3.1 mm [force-and-form calc exchange_procedure_w3 §1a]; h = 3.5 mm used here.")
    print("(b) SN-2549 closing normal to the row (tool on its side over a flat row, or tip-down over a")
    print("    row stood on edge): the jaw half facing the row must pass outside the row plane.")
    print("    h = a + 2.7 mm, a = nest floor to the back face of that jaw half, 6-12 mm [assumption,")
    print("    hand-tool-as-press a3, calc w3 §2] -> h = 8.7-14.7 mm.")
    print("(c) SN-2549 hung tip-down, closing along the row: h = nest-to-tip + 1.85 = 3.9-7.9 mm, but")
    print("    the jaw closing direction is the contact's floor normal, so every crimp is rolled 90 deg")
    print("    (hand-tool-as-press a3; into-the-housing calc ex §8). Not used.")
    print()
    print("Residual rise at the tip after one lift and release (sy 60..120 MPa, E_sil 2..6 MPa")
    print("[assumption, wave2 §1]; tip 5 mm past the lift point; free = comb root to lift point):")
    lifts = [3.0, 3.5, 8.7, 11.7, 14.7]
    print(f"{'free mm':>8}" + "".join(f"{('h ' + format(h, '.1f')):>16}" for h in lifts))
    for a in (15, 20, 25, 30, 35):
        row = f"{a:>8}"
        for h in lifts:
            vals = []
            for sy in (60, 120):
                for es in (2, 6):
                    P, pb, ra, rt, pbr = w2.cantilever(a, h, sy, es)
                    vals.append(rt)
            row += f"{min(vals):>9.2f}-{max(vals):<6.2f}"
        print(row)
    print()
    print("Loaded tip pull-back while lifted (what the trim in the pose absorbs):")
    print(f"{'free mm':>8}" + "".join(f"{('h ' + format(h, '.1f')):>16}" for h in lifts))
    for a in (20, 25, 30):
        row = f"{a:>8}"
        for h in lifts:
            pbs = []
            for sy in (60, 120):
                for es in (2, 6):
                    P, pb, ra, rt, pbr = w2.cantilever(a, h, sy, es)
                    pbs.append(pb)
            row += f"{min(pbs):>9.2f}-{max(pbs):<6.2f}"
        print(row)
    print("-> The fin from below leaves 0-0.8 mm of rise at 20 mm free and essentially none from 25 mm:")
    print("   squaring only tidies. The SN closing normal to the row needs 8.7-14.7 mm of lift, which")
    print("   leaves 0-8.2 mm of rise at 30 mm free and 0-5.7 mm at 35 mm: a 30-35 mm split and a")
    print("   squaring pass on every conductor. (Small-deflection model; rough at short lengths.)")


# ----------------------------------------------------------------------------------------------
def s2_fin():
    section("2. The fin anvil (p1d, p5c; p1 B-drop and p5 use it free-standing)")
    h = 3.5
    floor_under = h - BUNDLE_R - STOCK         # underside of k's barrel floor, strands on the floor
    rest = -(OD / 2) - 1.0                     # fin top 1 mm below the row's underside at rest
    print(f"k lifted {h} mm: barrel floor underside at +{floor_under:.2f} mm; fin at rest {rest:.2f} mm;")
    print(f"fin travel to the floor {floor_under - rest:.2f} mm [calc]. The lift finger and the fin meet the")
    print("contact at the same height, so the finger sets it and the fin only has to arrive under it.")
    print()
    print("Width: the anvil sits inside the crimper's channel. JST's analog SXA-01T-P0.6 at 22 AWG")
    print("crimps 1.50 wide x 0.80 high [mfr S14], xh-facts estimates ~1.5 for SXH-001T-P0.6. So the")
    print("fin is stepped: ~1.45 mm under the conductor barrel, 1.8-1.9 mm under the insulation")
    print("barrel [force-and-form calc exchange_procedure_w3 §2].")
    print()
    print("Clearance, fin side to the neighbour's surface, neighbours at 2.5 mm centres:")
    cases = [("conductor step 1.45 vs uncrimped bare strands", 1.45, BUNDLE_R),
             ("conductor step 1.45 vs uncrimped jacket (strip in pose)", 1.45, OD / 2),
             ("conductor step 1.45 vs crimped conductor barrel (1.5 wide)", 1.45, 0.75),
             ("insulation step 1.88 vs uncrimped jacket", 1.88, OD / 2),
             ("insulation step 1.88 vs crimped insulation barrel (1.8-2.0 wide)", 1.88, 1.0)]
    for name, w, r in cases:
        print(f"  {name:<66} {PITCH - w/2 - r:5.2f} mm a side")
    print()
    print("Where the tip comb can stand. The contact spans, from k's tip (Y=0, +Y toward the box):")
    brush, neck, box = 0.2, 0.5, 2.0            # [estimate from xh-facts §1 clone drawings]
    strip = 2.4                                 # [mfr S6]
    ins_len = (0.8, 1.5)                        # insulation barrel length [estimate, xh-facts §1]
    window = 0.3                                # gap between barrels [estimate]
    ins_rear = [-(strip + window + L) for L in ins_len]
    print(f"  box front ~+{brush + neck + box:.1f}, box rear ~+{brush + neck:.1f}; conductor barrel to ~-{strip - 0.9:.1f}..-{strip:.1f};")
    print(f"  insulation barrel rear at {ins_rear[0]:.1f} to {ins_rear[1]:.1f} mm.")
    pin_half = 0.64 / 2
    comb_gap_half = PITCH / 2 - pin_half
    print(f"  Tip-comb pins (0.64 mm) sit between conductors: the clear half-gap between k's two pins is")
    print(f"  {comb_gap_half:.2f} mm, against the insulation step's half-width 0.94 mm, so the fin's rear end")
    print(f"  must stop ahead of the pins: the tip comb stands >= ~{-ins_rear[1] + 0.5:.1f} mm behind the tip line")
    print("  (5-7 mm), not 4 mm.")
    print()
    print("Column (fixed base, free top, K = 2; E 205 GPa):")
    for name, w, d, L in (("p1d/p5c fin, narrow only through the row band", 1.45, 4.0, 5.0),
                          ("p1/p5 B-drop fin at the JST width, 9 mm tall", 1.45, 4.0, 9.0),
                          ("p1/p5 B-drop fin at the JST width, 10 mm tall", 1.45, 4.0, 10.0)):
        I = d * w ** 3 / 12
        Pcr = math.pi ** 2 * 205000 * I / (2 * L) ** 2
        print(f"  {name:<50} {w} x {d} x {L:>4} mm: Euler {Pcr/1000:5.1f} kN, stress at 3 kN "
              f"{3000/(w*d):4.0f} MPa")
    print("  (the crimper's legs guide the top at compaction, so the real load is higher)")
    print()
    print("Laminated 1095 blue-tempered shim [Prime: spring steel shim 0.005-0.032 in]:")
    inch = 25.4
    for name, leaves in (("conductor step", (0.032, 0.025)), ("insulation step", (0.032, 0.032, 0.010))):
        print(f"  {name}: {' + '.join(str(x) for x in leaves)} in = {sum(leaves)*inch:.3f} mm")
    print("  Spring temper (~Rc 45-50 [assumption]) against 400-900 MPa mean die pressure [xh-facts §4] is")
    print("  the open question; ground O1 or gauge plate stood on edge is the harder route.")


# ----------------------------------------------------------------------------------------------
def s3_knee():
    section("3. A knee near straight: the bottom is geometry")
    print("Two links of length L; the joint sits x off the straight line. Height short of straight")
    print("= 2(L - sqrt(L^2 - x^2)) ~ x^2 / L:")
    for L in (15, 20, 30):
        print(f"  L {L:>2} mm: " + ", ".join(f"x {x:.1f} mm -> {2*(L - math.sqrt(L*L - x*x))*1000:5.1f} um"
                                          for x in (0.1, 0.2, 0.5, 1.0)))
    print("-> A cam or screw that puts the joint within 0.2-0.5 mm of straight sets the bottom to a few")
    print("   microns. What moves the crimp height is the loop's stretch under force scatter:")
    for k in (40, 100, 200):
        print(f"   loop {k:>3} kN/mm, +/-300-600 N of scatter -> +/-{300/k:.1f}-{600/k:.1f} um")


# ----------------------------------------------------------------------------------------------
def s4_stops():
    section("4. Stops under an eccentric (p5): what a margin costs, and a compliant loop")
    print("The eccentric must be able to push past the stops by a margin m (frame creep, bearing play,")
    print("shim error: 0.02-0.10 mm [assumption]). Once the stops touch, the loop is squeezed by the")
    print("rest of the travel, so the frame carries F + k m at bottom dead centre (k = loop stiffness")
    print("outside the stops). A doubled contact (a rigid 0.2 mm) meets F + k (m + 0.2).")
    F = 2.43   # kN, 'high' crimp [force-and-form stroke_model via exchange_procedure_w3 §3]
    print(f"crimp force {F} kN ('high' case)")
    print(f"{'k kN/mm':>8}{'m 0.02':>10}{'m 0.05':>10}{'m 0.10':>10}{'doubled, m 0.10':>18}")
    for k in (40, 20, 10, 5, 2):
        print(f"{k:>8}" + "".join(f"{F + k*m:>9.2f} " for m in (0.02, 0.05, 0.10))
              + f"{F + k*(0.10 + 0.2):>15.2f} kN")
    print("-> A stiff loop pays 1.3-2.6x the crimp every stroke for the margin and puts 14 kN into a")
    print("   doubled contact; a loop of 5-10 kN/mm pays 1.05-1.4x and caps the doubled contact at")
    print("   3.9-5.4 kN with no preloaded stack. Height stays on the stops, in a short steel loop at the")
    print("   dies (~670 kN/mm [hand-tool-as-press calc H §4]). Peak shaft torque with the frame's")
    print("   wind-up counted is 1.0-2.3 N*m for loops of 2-40 kN/mm [force-and-form calc")
    print("   exchange_procedure_w3 §3].")
    print()
    print("A rod spring that sets k when the frame is stiffer than wanted [assumption: DIN 2093 series A")
    print("table values, not fetched]: one A25 disc (25 x 12.2 x 1.5 mm, h0 0.55) carries ~2.9 kN at 75 %")
    print("of its travel (~0.41 mm): ~7 kN/mm, nearly linear; two stacked in series ~3.5 kN/mm.")
    for k_frame in (20, 40):
        for k_spring in (3.5, 7.0):
            k = 1 / (1 / k_frame + 1 / k_spring)
            print(f"  frame {k_frame} kN/mm + rod spring {k_spring} kN/mm -> loop {k:4.1f} kN/mm, "
                  f"surplus at m 0.10 {k*0.10:4.2f} kN")
    print()
    print("Load cell placement: a 500 kg button cell deflects ~0.05-0.1 mm at full scale (~50-100 kN/mm")
    print("[estimate]). Inside the stop loop (between fin and fin holder) it moves height by:")
    for kc in (50, 100):
        print(f"  {kc} kN/mm: +/-{300/kc:.0f}-{600/kc:.0f} um for +/-300-600 N of scatter")
    print("  Under the whole lower die (fin holder and stops together) it is outside the stop loop and")
    print("  sees the stop contact as a sharp rise in stiffness. Foil gauges on a steel member add no")
    print("  compliance at all [Prime: foil strain gauges BF350].")


# ----------------------------------------------------------------------------------------------
def s5_p7_pads():
    section("5. p7: pushing the slug through pads, and what the pads' squeeze costs")
    print("The blades' front faces bear only on the cut caps' end faces: 0.28-0.65 mm2 per conductor,")
    print("which crush at 2-5x silicone's 8-11 MPa before the flanks tear [force-and-form calc")
    print("exchange_procedure_w3 §6]. A pad pair on the slug's top and bottom, travelling with the")
    print("blades, carries the push by friction. The same squeeze presses the jacket onto the strands,")
    print("so the slug's own friction on the strands rises too:")
    print("  net drive per conductor = 2 N (mu_pad - mu_js) + F_cap,  need >= T_tear + S0")
    print("  N = pad force per side per conductor; mu_pad pad on silicone; mu_js silicone on tinned")
    print("  strands; F_cap what the cap faces carry before they crush (8-11 MPa x 0.28-0.65 mm2);")
    print("  T_tear 3-15 N per conductor [digest; wave2 §7]; S0 the unsqueezed slug's friction on its")
    print("  strands, 0.5-3 N [assumption].")
    for mu_p, mu_s, label in ((0.8, 0.5, "smooth TPU pad"), (1.2, 0.3, "grippy TPU pad"),
                              (2.0, 0.4, "fine-toothed pad (teeth bite the jacket) [assumption]")):
        print(f"  {label}: mu_pad {mu_p}, mu_js {mu_s}")
        for T in (3, 15):
            need = T + 3 - 2.2          # S0 3 N worst, F_cap ~2.2 N (8 MPa x 0.28 mm2) low end
            if mu_p - mu_s <= 0:
                print("    no net drive")
                continue
            N = max(need, 0) / (2 * (mu_p - mu_s))
            print(f"    T {T:>2} N/cond: pad force {N:5.1f} N per side per conductor, "
                  f"{5*N:5.0f} N per side for a 5P; pad pressure on ~2.6-3.3 mm2 of crown "
                  f"{N/3.3:4.1f}-{N/2.6:4.1f} MPa")
    print("-> Smooth pads need 30-130 N per side on a 5P, and their squeeze presses the jacket onto the")
    print("   strands hard enough to cancel most of what they deliver. Grippy TPU needs 11-44 N per side;")
    print("   pads that bite (fine teeth, or a knurled steel face) 6-25 N. The teeth mark only the slug,")
    print("   which is thrown away.")
    print()
    print("Slice while pressing: each blade drawn 2-4 mm along its own edge as it closes (an inclined")
    print("slot in the carrier). A sharp edge pressed straight in indents silicone ~0.03-0.25 mm before it")
    print("cuts [force-and-form estimate], comparable to the 0.2-0.3 mm ligament, so a pressed kerf can")
    print("stop short of the steel stop; a sliced one reaches it.")
    print("Lower blade slot: the lower blade rides the carriage +Y 3-4 mm, so either the slot is 3.3-4.3 mm")
    print("long or the floor ahead of the strip line is part of the carriage (a split floor) and the")
    print("lower blade rises through the joint.")


# ----------------------------------------------------------------------------------------------
def s6_minutes():
    section("6. Cycle and person minutes: p1d (fin from below at bench B) and p5c (camshaft turns a knee)")
    steps = [("index", 3), ("lift", 2), ("trim in pose (grounded blade: identity)", 6),
             ("strip in pose", 15), ("look (backlit silhouette)", 3), ("place: post bar -Y", 5),
             ("fin up, gate in", 4), ("knee to end of curl, pause, identity", 8),
             ("knee to straight (compaction)", 8), ("re-touch, read height", 5),
             ("clear: knee open, gate out, fin down, post bar back", 6), ("proof pull 20 N", 5),
             ("lay back, square", 6)]
    tot = sum(s for _, s in steps)
    no_strip = tot - 15 - 6
    print("p1d per key [estimate]:")
    for n, s in steps:
        print(f"  {n:<58} {s:>3} s")
    print(f"  total {tot} s with trim and strip in pose; {no_strip} s when p7 has stripped the end")
    for name, per in (("with strip in pose", tot), ("after p7", no_strip)):
        print(f"  {name}: J1 (9) {9*per/60:4.1f} min; unit (53) {53*per/60:4.0f} min")
    print()
    N, ENDS, HOUS = 53, 14, 10
    t = {"cut": 20, "peel": 40, "load cassette (lay in, loft crossings, close)": 60,
         "load one contact on the post bar": 4, "dock cassette in magazine": 10,
         "insert by hand": 8, "gang insert at bench C, per housing": 20, "test and label per housing": 25,
         "p7 lever strip per end": 15}
    print("Person minutes per unit, wave-2 task library plus cassette tasks [estimate; compare rows]:")
    base = (ENDS * (t["cut"] + t["peel"] + t["p7 lever strip per end"]) + HOUS * t["load cassette (lay in, loft crossings, close)"]
            + N * t["load one contact on the post bar"] + HOUS * t["dock cassette in magazine"]
            + HOUS * t["test and label per housing"])
    hand = base + N * t["insert by hand"]
    gang = base + HOUS * t["gang insert at bench C, per housing"]
    print(f"  p1d, hand insertion: {hand/60:.0f} min; with bench C gang insertion: {gang/60:.0f} min")
    print("  (today by the same library ~46 min; p1 at stage 3 ~36 min [calc person_timeline])")
    print("  The machine calls once a unit if a magazine holds the unit's ten cassettes.")
    print()
    print("p5c: one shaft turn per key, 40-60 s [estimate]: J1 6-9 min, unit 35-53 min of shaft time.")
    print("  Shaft torque: the knee lobe needs 0.25-1.9 N*m peak plus 0.1-0.3 N*m of knee friction and")
    print("  return spring [force-and-form calc exchange_procedure_w3 §8]; the other cams ~50 N at their")
    print("  followers, ~0.1-0.4 N*m. A 12 V self-locking worm gearmotor, 40 kg*cm (3.9 N*m), 10 rpm")
    print("  [Prime: Greartisan], or a NEMA 17 with a 26.85:1 planetary, 3 N*m permissible, not")
    print("  self-locking [Prime: STEPPERONLINE 17HS19-1684S-PG27], each covers it.")


# ----------------------------------------------------------------------------------------------
def s7_consistency():
    section("7. Consistency: p5b's squeeze lobe against the crimp's work")
    for F in (220, 275):
        print(f"  lobe {F} N over the last 8 mm of grip: {F*8/1000:.2f} J at the handle")
    print("  crimp work 0.13-0.48 J [digest; force-and-form stroke_model]")
    print("-> Either the tool's linkage loses 75-90 % or the constant-force assumption overstates the")
    print("   lobe by 2-4x. Either way the motor sizing (2.1-3.2 N*m) errs on the safe side.")


def main():
    s1_lift_and_set()
    s2_fin()
    s3_knee()
    s4_stops()
    s5_p7_pads()
    s6_minutes()
    s7_consistency()


if __name__ == "__main__":
    main()
