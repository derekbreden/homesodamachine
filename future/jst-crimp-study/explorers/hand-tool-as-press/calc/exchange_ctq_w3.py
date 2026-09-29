"""hand-tool-as-press on change-the-question, wave 3: numbers for the exchange file.

Run:  python3 exchange_ctq_w3.py > exchange_ctq_w3.out.txt

Cited from exchange/hand-tool-as-press--on--change-the-question-w3.md as [htq §n].
Labels: [mfr], [source], [calc], [estimate], [assumption].
[w2 §n] = change-the-question's calc/wave2.out.txt; [ctq §n] = its calc/ctq.out.txt;
[ith ex §n] = into-the-housing's calc/exchange_hand_tool_as_press.out.txt;
[ht w2 §n] = this explorer's calc/wave2.out.txt.
"""

import math


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


T = 0.20                 # stock, mm [source S19-S21: 0.20 +/-0.02]
OD_NOM = 1.70            # jacket OD, mm [source S29: 1.7 +/-0.1 per conductor]
CORE = (0.75, 0.80)      # strand bundle, mm [xh-facts section 7; as change-the-question uses]

# ---------------------------------------------------------------------------
hr("1. c6's round keyhole against a closed insulation crimp")
print("Tips lie on the bore circle with gap g at the top. Height of the highest metal above")
print("the contact's underside = floor t + r + y_tip + t*sin(phi), phi = angle of the tip's radius")
print("above horizontal. Throat opening angle = 2*asin(g/D) seen from the bore centre.")
print("Closed insulation crimp height: 1.80 mm at 22 AWG on the KONNRA clone spec [digest];")
print("the SN-2549's own insulation height is unmeasured [assumption: 1.8-2.1 mm].")
print()
print("  bore D (mandrel+springback) | throat g | tip-top metal | open arc | jacket top (on bore floor) | tip-top below 1.80 by")
for D in (1.57, 1.60, 1.65):
    r = D / 2
    for g in (1.3, 1.4, 1.5):
        x = g / 2
        y = math.sqrt(r * r - x * x)
        phi = math.atan2(y, x)
        top = T + r + y + T * math.sin(phi)
        arc = 2 * math.degrees(math.asin(g / D))
        jacket_top = T + OD_NOM
        print(f"        {D:4.2f}                 |   {g:3.1f}    |   {top:4.2f} mm     |  {arc:4.0f} deg | "
              f"      {jacket_top:4.2f} mm            |   {1.80 - top:+5.2f} mm")
print("-> the keyhole's metal ends 0.14-0.52 mm below the clone spec's closed insulation height,")
print("   with 104-146 deg of the jacket's top uncovered. A die that closes to 1.80 mm meets the")
print("   jacket first and reaches the wing tips only where its profile dips below ~1.3-1.6 mm")
print("   at x = +/-0.65-0.75 mm. A B-profile dips at x = 0 (the cusp), where there is only jacket.")
print("   The final stroke then presses the jacket through the throat and squeezes the sides;")
print("   it does not turn the tips over the jacket [assumption: B-profile insulation section].")
print()
print("  How a B-profile die forms an insulation barrel (kinematics, all single-stroke tools):")
print("  the open wing tips meet the die's flared walls, are pushed inside the die width, run up")
print("  the arches toward the central cusp, meet there and are driven down into the jacket.")
print("  The wing roots stay near vertical until the tips reach the cusp. No point of that")
print("  stroke is a round bore with an open 1.3-1.5 mm throat. Stopping the stroke early gives a")
print("  narrowed U with tips curling inward high up; stopping it at the pin gives tips closed")
print("  over the pin (no throat).")

# ---------------------------------------------------------------------------
hr("2. The keyhole's axial grip with springback and the jacket's OD tolerance")
print("change-the-question's grip model [w2 section 4], unchanged, evaluated at the bore the")
print("mandrel actually leaves (mandrel + 0.02-0.05 springback, as c6's own go/no-go text says),")
print("and at the ribbon's 1.7 +/-0.1 mm per conductor [source S29].")


def gent_E(shore_a):
    return 0.0981 * (56 + 7.62336 * shore_a) / (0.137505 * (254 - 2.54 * shore_a))


E_lo, E_hi = gent_E(50), gent_E(70)
L = (0.8, 1.5)   # insulation barrel length [xh-facts section 1 estimate]


def grip(ID, OD):
    d = (OD - ID) / 2
    if d <= 0:
        return (0.0, 0.0)
    wall = ((OD - CORE[1]) / 2, (OD - CORE[0]) / 2)
    strain = (d / wall[1], d / wall[0])
    p = (E_lo * strain[0], E_hi * strain[1])
    area = (math.pi * ID * L[0] * 0.5, math.pi * ID * L[1] * 0.8)
    return (0.3 * p[0] * area[0], 0.8 * p[1] * area[1])


print()
print("  mandrel | bore after springback | jacket OD 1.60 | jacket OD 1.70 | jacket OD 1.80")
for m in (1.55, 1.60):
    for sb in (0.02, 0.05):
        ID = m + sb
        cells = []
        for OD in (1.60, 1.70, 1.80):
            lo, hi = grip(ID, OD)
            cells.append(f"{lo:4.2f}-{hi:4.1f} N")
        print(f"   {m:4.2f}  |        {ID:4.2f}           |  {cells[0]:>12}  |  {cells[1]:>12}  |  {cells[2]:>12}")
lo_a, hi_a = grip(1.55, 1.70)
lo_b, hi_b = grip(1.60, 1.70)
print(f"  as c6 quotes it (bore = mandrel, OD 1.70): {lo_b:.2f}-{hi_a:.1f} N ('0.2-4 N')")
lo_c, _ = grip(1.65, 1.70)
_, hi_c = grip(1.57, 1.70)
print(f"  with springback, OD 1.70: {lo_c:.2f}-{hi_c:.1f} N")
print("  a keyed slot asks 0.1-0.5 N, a post 0.2-1.6 N [ts otq section 7, via w2 section 4]")
print("-> springback halves the low end; a conductor at the low edge of 1.7 +/-0.1 mm is not")
print("   gripped at all by a 1.60 mandrel's bore. The bore has to be chosen against the ribbon's")
print("   measured OD, not its nominal pitch.")

# ---------------------------------------------------------------------------
hr("3. The crimp tool as its own pre-former: is there a stroke window?")
print("Jaw gap above bottom dead centre at which each die first touches its open wing tips.")
print("Edge model: the die's flared side walls come down to within e of the anvil at BDC")
print("(they form the barrel's sides), and the open tips lie outside the die width, so they")
print("meet the flare when its lower edge reaches the tip height: gap = H_open - e.")
print("Apex model (pessimistic): the tips are first touched near the arch, gap = H_open - H_closed.")
H_ins = (2.75, 3.20)       # open insulation wing height [source S19-S22], +/-0.25
H_cond = (1.50, 1.60)      # open conductor wing height [source S19-S22], +/-0.25
Hc_ins = (1.80, 2.00)      # closed insulation height [digest KONNRA 1.80; estimate to 2.0]
Hc_cond = (0.73, 0.88)     # closed conductor height [digest KONNRA 0.73; estimate 0.88]
for e in (0.0, 0.2):
    wi = (H_ins[0] - e, H_ins[1] - e)
    wc = (H_cond[0] - e, H_cond[1] - e)
    print(f"  edge model, e = {e:.1f}: insulation first touch at {wi[0]:.2f}-{wi[1]:.2f} mm gap, conductor at "
          f"{wc[0]:.2f}-{wc[1]:.2f}; window {wi[0]-wc[1]:.2f}-{wi[1]-wc[0]:.2f} mm (nominal drawings)")
wi_t = H_ins[0] - 0.25
wc_t = H_cond[1] + 0.25
print(f"  edge model, drawing tolerances against each other: window down to {wi_t - wc_t:.2f} mm")
ai = (H_ins[0] - Hc_ins[1], H_ins[1] - Hc_ins[0])
ac = (H_cond[0] - Hc_cond[1], H_cond[1] - Hc_cond[0])
print(f"  apex model: insulation {ai[0]:.2f}-{ai[1]:.2f}, conductor {ac[0]:.2f}-{ac[1]:.2f}; window "
      f"{ai[0]-ac[1]:+.2f} to {ai[1]-ac[0]:+.2f} mm")
print("  in grip travel at the tool's open end (gain 3-6 [ht w2 section 5, assumption]):")
for w in (0.65, 1.15, 1.70):
    print(f"    die window {w:.2f} mm -> {3*w:4.1f}-{6*w:4.1f} mm of grip travel")
print("-> on the edge model the insulation wings are pushed inside the die width over 0.65-1.7 mm")
print("   of stroke before the conductor die touches anything: several mm of grip, likely one or")
print("   more ratchet clicks [estimate; click pitch unmeasured]. On the apex model the window can")
print("   vanish. One slow close on an empty contact, looked at end-on, decides which.")
print("  what the tool-made pre-form looks like at the end of the window [estimate]:")
print("    outer width ~ die width 1.8-2.0 (+0.02-0.05 springback), tips curling inward high in the")
print("    arches, height ~2.3-3.0 mm, conductor barrel untouched.")

# ---------------------------------------------------------------------------
hr("4. A flag pushed box-first through the open SN-2549: lance, grip and opening")
box_h = (2.2, 2.4)          # [source S19-S22]
lance = (0.6, 0.9)          # [xh-facts section 1]
lance_fold = (1.0, 5.0)     # N [ith ex section 3, estimate]
print(f"  lance fold force {lance_fold[0]}-{lance_fold[1]} N [ith ex section 3] against the flag's axial grip "
      f"{lo_c:.2f}-{hi_c:.1f} N [section 2]")
print("  -> if the flag slides on the anvil, the lance is dragged across the jaw's thickness and")
print("     the contact is pushed back along the jacket whenever fold force exceeds grip: most")
print("     of the range. The tip-to-contact position the snap block set is then lost unseen.")
entry = (lance[0] + 0.2, lance[1] + 0.2)
exit_lift = (1.0, 1.7)      # [ith ex section 2]
print(f"  flag carried level at height h above the anvil: entry needs h >= {entry[0]:.1f}-{entry[1]:.1f} mm "
      f"(lance + 0.2); exit needs lift {exit_lift[0]}-{exit_lift[1]} mm [ith ex section 2]")
for h in (1.1, 1.4, 1.7):
    for name, top in (("round keyhole (box governs)", box_h), ("tool-made U 2.3-3.0", (2.3, 3.0))):
        need = (h + max(box_h[0], top[0]) + 0.2, h + max(box_h[1], top[1]) + 0.2)
        print(f"    h {h:.1f}: {name:<28} -> jaw opening at the nest {need[0]:.1f}-{need[1]:.1f} mm")
print("  for comparison: an open contact needs 3.35-4.10 mm [ith ex section 2]; a flag dragged on")
print("  the anvil needs only the box, 2.4-2.6 mm, but drags its lance.")

# ---------------------------------------------------------------------------
hr("5. One SN nest as c1c's punch: how narrow, how tall")
pitch = 3.4
clear = 0.1
neigh = {
    "c6 round keyhole 1.96-2.14 [w2 s2]": (1.96, 2.14),
    "tool-made U 1.82-2.05 [s3 est.]": (1.82, 2.05),
    "crimped insulation 1.90-2.00 [est.]": (1.90, 2.00),
    "open conductor barrel 1.43-2.15 [S19-S22]": (1.43, 2.15),
}
print(f"  tongue width allowed at {pitch} mm pitch, {clear} mm clearance each side, beside:")
for k, (a, b) in neigh.items():
    print(f"    {k:<42} {2*(pitch - b/2 - clear):4.2f}-{2*(pitch - a/2 - clear):4.2f} mm")
tops = {
    "c6 keyhole with jacket (jacket top)": (1.8, 2.0),
    "tool-made U tips": (2.3, 3.0),
    "open conductor wings": (1.25, 1.85),
}
print("  tongue must stay that narrow up to the tallest neighbour inside the punch's footprint + 0.3:")
for k, (a, b) in tops.items():
    print(f"    {k:<38} -> narrow to {a+0.3:.1f}-{b+0.3:.1f} mm above the anvil")
for arch in (1.5, 1.6):
    print(f"  walls either side of a {arch} mm conductor arch in a 4.46 mm tongue: {(4.46-arch)/2:.2f} mm")
print("  anvil blade through a 2.0 mm pocket with 0.05 mm clearance: <= 1.90 mm wide")
print("  a 3 x 3 mm HSS blank (c1's anvil) must lose >= 1.1 mm of width")
print("  hand-tool-as-press a4's 'one-nest die narrowed to 6-8 mm' is 1.5-3.5 mm too wide here.")

# ---------------------------------------------------------------------------
hr("6. c1c: carriers sprung forward, a fixed front stop, and a rearward proof pull")
for s in (0.2, 0.5):
    for ang in (30, 45):
        dx = s / math.tan(math.radians(ang))
        print(f"  overtravel {s:.1f} mm, side ramp {ang} deg: box pushed back over {dx:.2f} mm of the 3.4 mm step")
print("  carrier spring 0.1-0.5 N [c1c] against a 20 N per-contact proof pull [c1c]:")
for n in (2, 3, 4, 5):
    print(f"    row of {n}: {20*n:3d} N rearward on carriers whose only rearward restraint is 0.1-0.5 N each")
print("  box rear walls above the floor 1.27 mm^2 -> 16 MPa at 20 N [ht w2 section 2]: a printed")
print("  shoulder takes the pressure; the carrier needs a rear lock, and the row's 40-100 N goes")
print("  into the pallet and its swing-arm pivot at 20-40 mm [estimate] -> 0.8-4.0 N*m.")

# ---------------------------------------------------------------------------
hr("7. c1c's fixed C with the spine in front of the housing nest: lower arm")
F = 3000.0
E = 200e3
for Lm in (20.0, 26.0):
    for b in (15.0, 25.0):
        t_s = math.sqrt(6 * F * Lm / (b * 1000.0))
        for t in (t_s, 12.0):
            dfl = 4 * F * Lm ** 3 / (E * b * t ** 3) * 1000
            tag = "stress-sized (1000 MPa)" if t == t_s else "12 mm arm"
            print(f"  reach {Lm:.0f} mm, width {b:.0f} mm, {tag:<24}: t {t:5.2f} mm, tip deflection {dfl:5.0f} um")
print("-> the arm can be wide and thick below the pallet; with the height stop in the die block")
print("   beside the anvil, arm deflection adds travel, not crimp height.")

# ---------------------------------------------------------------------------
hr("8. Person time at the combined bench (K1), estimates")
steps = {
    "pre-form at the second SN-2549 (drop, click, release, push to stick)": (8, 12),
    "snap at the block (lay tip on the stop, thumb press, lift the flag)": (6, 10),
    "crimp (flag along the guide to the stop, foot)": (8, 12),
}
tot = [0, 0]
for k, (a, b) in steps.items():
    print(f"  {k:<72} {a:2d}-{b:2d} s")
    tot[0] += a
    tot[1] += b
at_bench = (tot[0] - 8, tot[1] - 12)
print(f"  per contact {tot[0]}-{tot[1]} s; at the wire (snap + crimp) {at_bench[0]}-{at_bench[1]} s")
print(f"  per unit (53): {53*tot[0]/60:.0f}-{53*tot[1]/60:.0f} min, of which {53*8/60:.0f}-{53*12/60:.0f} min pre-forming "
      f"away from any wire")
print("  against today ~25 s a crimp (22 min) and a6 ~35 s with pull and gauge (31 min) [ht w2 section 9]")
