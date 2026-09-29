#!/usr/bin/env python3
"""
terminal-supply on borrowed-machines, wave 3.

Numbers for exchange/terminal-supply--on--borrowed-machines-w3.md.
Inputs are taken from xh-facts.md, the digest, borrowed-machines' calcs,
procedure-is-the-machine's exchange_borrowed calc and this explorer's
wave2 calc; anything else is labelled [estimate] or [assumption] beside it.
"""
import math

def hdr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)

# ---------------------------------------------------------------------------
hdr("1. b2: drop-shear of the tab while a printed tweezer grips the box")
F_shear = (48.0, 158.0)            # N, tab shear [xh-facts C1]
L_over = (5.8, 6.73)               # mm, box front to insulation-barrel rear, clone drawings [xh-facts §1]
grip = 1.0                         # mm, tweezer centre behind the box front [estimate]
lev = (L_over[0] - grip, L_over[1] - grip)
M_lo, M_hi = F_shear[0] * lev[0], F_shear[1] * lev[1]
print(f"  lever gripper -> tab root {lev[0]:.1f}-{lev[1]:.1f} mm; moment at the grip "
      f"{M_lo:.0f}-{M_hi:.0f} N*mm")

def mp_channel(b, t, h, sy):
    """Plastic moment of a floor b x t with two side walls t thick, h tall above the floor,
    bent so the floor goes down (axis horizontal, across the contact). Sliced numerically."""
    n = 4000
    ztop = t + h
    dz = ztop / n
    def width(z):
        return b if z < t else (2 * t if h > 0 else 0.0)
    area = sum(width((i + 0.5) * dz) * dz for i in range(n))
    half, acc, zp = area / 2, 0.0, 0.0
    for i in range(n):
        z = (i + 0.5) * dz
        acc += width(z) * dz
        if acc >= half:
            zp = z
            break
    S = sum(width((i + 0.5) * dz) * dz * abs((i + 0.5) * dz - zp) for i in range(n))
    return sy * S

for b in (1.0, 1.5):
    for h in (0.0, 0.3, 0.6):
        lo = mp_channel(b, 0.2, h, 450)
        hi = mp_channel(b, 0.2, h, 650)
        print(f"  neck floor {b:.1f} mm wide, walls {h:.1f} mm: plastic moment {lo:5.1f}-{hi:5.1f} N*mm"
              f"  -> shear moment is {M_lo/hi:5.0f}-{M_hi/lo:5.0f} x that")
print("  [neck width and wall height estimates; C5191 yield 450-650 MPa, as wave2 §2]")
for N in (1.0, 5.0):
    for mu in (0.3, 0.5):
        cap = mu * N * (2.0 / 3.0) * 0.8 * 2   # two jaw faces, ~0.8 mm patch half-length [estimate]
        print(f"  tweezer squeeze {N:.0f} N, mu {mu}: moment it resists by friction ~{cap:.1f} N*mm")
print("  -> the neck yields, or the contact turns in the tweezers, long before the tab shears.")
print("     The shear must be reacted at the tab root: a steel edge under the insulation barrel's")
print("     rear (lever ~0), with a guided steel drop blade beside it.")

# ---------------------------------------------------------------------------
hdr("2. b3: the stepped trim is taken off conductors that are already stripped")
trims = {  # outermost conductor's excess length, procedure calc exchange_borrowed §6 (20 mm split)
    3.60: {"4P": 0.26, "5P": 0.53, "J4 (7)": 1.15, "J1 (9)": 1.97},
    4.35: {"4P": 0.54, "5P": 1.06, "J4 (7)": 2.27, "J1 (9)": 3.80},
}
strip = 2.4          # mm [xh-facts §1, JST WC-110]
win_half = (0.3, 0.5)  # mm, half of the 0.6-1.0 mm window between barrels [estimate]
for fan, d in trims.items():
    print(f"  fan pitch {fan:.2f} mm:")
    for k, tr in d.items():
        bare = strip - tr
        state = ("insulation edge still in the window" if tr <= win_half[0] else
                 "insulation edge at or past the conductor barrel's rear edge" if tr <= win_half[1] + 0.2
                 else "insulation under the conductor barrel" if bare > 0 else
                 "trim reaches the insulation: no bare strands")
        print(f"    {k:7s}: trimmed {tr:.2f} -> bare {bare:5.2f} mm; with the tip on b3's neck blade the "
              f"insulation edge moves {tr:.2f} mm forward: {state}")
print("  Trimmed and stripped flat (before splitting), each contact placed on its own conductor:")
print("  the front's along-conductor distance from the root is the same for every conductor, and the")
print("  fan pitch at the crimp drops out. In the housing the outermost front lands short by")
for ell in (12.0, 20.0):
    row = []
    for k, y in (("4P", 1.2), ("5P", 1.6), ("J4", 2.4), ("J1", 3.2)):   # outermost lateral move [geometry §1]
        row.append(f"{k} {ell - math.sqrt(ell**2 - y**2):.2f}")
    print(f"    free length {ell:4.1f} mm: " + ", ".join(row) + " mm (the same at any fan pitch)")
print("  [straight-conductor model; agrees with procedure calc §7 for 12 mm]")

# ---------------------------------------------------------------------------
hdr("3. Strip length follows the contact: 2.4 mm on a clone barrel")
E = (1.25, 1.5)       # conductor barrel length, clone drawings [xh-facts §1 estimate]
A = (0.6, 1.0)        # window between barrels [estimate]
neck = (0.4, 0.6)     # box-to-conductor-barrel transition [wave2 §5 inputs, clone drawings]
for L in (2.4, 2.1, 1.85, 1.6):
    a_lo = L - E[1] - A[1] / 2
    a_hi = L - E[0] - A[0] / 2
    # insulation edge steered to window centre -> brush past barrel front
    flag = []
    if a_hi > neck[0]:
        flag.append(f"brush reaches the box when it exceeds the {neck[0]}-{neck[1]} mm neck")
    if a_lo < 0:
        flag.append("strands can stop short of the barrel front (no brush)")
    # strands on a blade at brush 0.25 -> insulation edge distance behind the conductor barrel
    ie_lo = L - E[1] - 0.25
    ie_hi = L - E[0] - 0.25
    print(f"  strip {L:.2f}: edge-steered brush {a_lo:+.2f} to {a_hi:+.2f} mm; tip on a blade at 0.25 brush puts "
          f"the insulation edge {ie_lo:.2f}-{ie_hi:.2f} mm behind the conductor barrel (window 0.6-1.0)"
          + ("; " + "; ".join(flag) if flag else ""))
print("  -> with clone barrels, 2.4 mm gives a long brush (edge-steered) or buries the insulation edge in")
print("     the insulation barrel (tip-stopped); the clone spec's 1.6-2.1 mm fits. JST's 2.4 mm belongs to")
print("     JST's own barrel lengths, which are unpublished.")

# ---------------------------------------------------------------------------
hdr("4. b1: lateral capture of the insulation between open insulation wings, by supply")
OD = (1.6, 1.8)   # 1.7 +/-0.1 [xh-facts §7]
for name, W in (("JST catalog envelope, if it is the open width", (1.95, 1.95)),
                ("Wurth analog", (2.30, 2.30)),
                ("clone drawings +/-0.25", (2.46 - 0.25, 3.00 + 0.25))):
    lo = (W[0] - OD[1]) / 2
    hi = (W[1] - OD[0]) / 2
    print(f"  {name:45s}: clearance per side {lo:+.3f} to {hi:+.3f} mm")
print("  b1's table uses +/-0.4 mm; that holds for clone wings only.")

# ---------------------------------------------------------------------------
hdr("5. K1, the flat spool line (b8 x a2d): pitch, crown, fronts, supply, time")
R_crown = (25.0, 30.0)                  # mm [wave2 §2]
for wb in (2.4, 2.7, 3.0):               # knife-set punch outer width [estimate]
    for rn in (0.85, 1.0):               # neighbour half-width: conductor 0.85, crimped barrel up to ~1.0
        p = wb / 2 + rn + 0.3
        drops = ", ".join(f"R{R:.0f}: {p*p/(2*R):.2f}" for R in R_crown)
        print(f"  punch {wb:.1f} wide, neighbour half-width {rn:.2f}: fan pitch p >= {p:.2f} mm; crown surface "
              f"at p lies below the crest by {drops} mm")
print("  outermost conductor's lateral move at the tips, ribbon pitch 1.7 -> p, and in the housing (2.5):")
for n, lbl in ((3, "4P"), (4, "5P"), (8, "J1 (9)")):
    half = n / 2
    for p in (2.5, 2.8):
        y_f = half * (p - 1.7)
        y_h = half * (2.5 - 1.7)
        curv = 3 * y_f / 12.0**2          # cantilever end-load, 12 mm free length
        print(f"    {lbl:7s} p {p:.1f}: at the crimp {y_f:.2f} mm, in the housing {y_h:.2f} mm; comb then moves it "
              f"{y_f - y_h:+.2f} mm; root curvature {curv:.3f}/mm = {curv/0.0150:.1f}x strand yield (sets toward the housing fan)")
print("  fronts in the housing: as section 2 (4P 0.06, 5P 0.11, J1 0.43 mm short at 12 mm), independent of p")
units, per_unit, t4 = 60, 53, 20
t4_prog = units * t4
other = units * (per_unit - t4)
print(f"  supply: T4 {t4_prog} crimps over ~{units} units; skip-2 uses {2*t4_prog} strip contacts "
      f"({2*t4_prog/8000:.2f} of an 8,000 reel) and drops {t4_prog} loose ones into the thinning cup;")
print(f"          the other looms need {other} crimps, so the cup covers {t4_prog/other*100:.0f} % of them "
      f"with the same contact")
prep, crimp, finish = 120, 106, 90        # s: b8 feed/rip/strip; a2d per crimp [wave2 §11]; b8 insert/test/cut
end_s = prep + 4 * crimp + finish
print(f"  time: ~{end_s/60:.1f} min per T4 end, ~{5*end_s/60:.0f} min per unit's five T4 ends [estimates]")

# ---------------------------------------------------------------------------
hdr("6. b1c: where the pre-feed finger moves on the downstroke, and backing out")
r, Lr = 15.0, 100.0
def drop_from_tdc(th):
    th = math.radians(th)
    return r * (1 - math.cos(th)) + Lr - math.sqrt(Lr**2 - (r * math.sin(th))**2)
def angle_for_height_above_bdc(h):
    # upstroke angle (from TDC, 180..360) at which the ram is h above BDC
    target = 2 * r - h
    lo, hi = 180.0, 360.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if drop_from_tdc(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
for h in (4, 6, 15, 20):
    up = angle_for_height_above_bdc(h)
    print(f"  ram {h:2d} mm above BDC: upstroke {up:5.1f} deg, the same height on the downstroke at {360-up:5.1f} deg")
a15, a20 = angle_for_height_above_bdc(15), angle_for_height_above_bdc(20)
print(f"  pre-feed advance at 15-20 mm up on the upstroke [b1b assumption] -> {a15:.0f}-{a20:.0f} deg (b1c's table: ~266-285);")
print("  a cam-driven feed lever is a function of ram height [assumption], so the finger retracts to the next")
print(f"  hole on the downstroke at ~{360-a20:.0f}-{360-a15:.0f} deg: inside b1c's fork lay-in (20-80) and at the start of the")
print("  foot (80-110), before the gate at 115. Reversing the shaft from 115 to 0 passes that band again and")
print("  re-advances the strip one pitch under a laid-in, footed conductor: b1's Break 1, re-created by the back-out.")
last = 8.74   # deg for the last 0.2 mm, b1b presses calc §1
for T in (10, 20, 40):
    print(f"  {T:2d} s per turn: last 0.2 mm lasts {last/360*T:.2f} s -> {last/360*T*80:.0f} HX711 samples at 80 Hz")
print("  (b1c quotes ~190 from p5's eccentric, whose compaction spans 22 deg; b1b's 15 mm crank gives ~78.)")

# ---------------------------------------------------------------------------
hdr("7. The rod stack of b1b/b1c (and a1's stack) from DIN 2093 series A discs")
E_s, nu = 206e3, 0.3
def disc_F(De, Di, t, h0, s):
    d = De / Di
    K1 = (1 / math.pi) * ((d - 1) / d) ** 2 / ((d + 1) / (d - 1) - 2 / math.log(d))
    C = 4 * E_s / (1 - nu**2) * t**4 / (K1 * De**2)
    return C * (s / t) * ((h0 / t - s / t) * (h0 / t - s / (2 * t)) + 1)
def s_at(De, Di, t, h0, F):
    lo, hi = 0.0, 0.75 * h0
    if disc_F(De, Di, t, h0, hi) < F:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if disc_F(De, Di, t, h0, mid) < F:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
discs = {"A25": (25, 12.2, 1.5, 0.55), "A28": (28, 14.2, 1.5, 0.65), "A31.5": (31.5, 16.3, 1.75, 0.70),
         "A35.5": (35.5, 18.3, 2.0, 0.80), "A40": (40, 20.4, 2.25, 0.90)}
Fpre, Fcap = 4000.0, 5400.0
for k, g in discs.items():
    F75 = disc_F(*g, 0.75 * g[3])
    s_pre = s_at(*g, Fpre)
    s_cap = s_at(*g, Fcap)
    s_end = s_cap if s_cap is not None else 0.75 * g[3]
    F_end = min(Fcap, F75)
    txt = (f"  DIN 2093 {k:5s}: F at 0.75 h0 = {F75/1000:4.2f} kN; ")
    if s_pre is None:
        txt += "cannot reach a 4 kN preload"
    else:
        trav = s_end - s_pre
        txt += (f"4 kN at s={s_pre:.3f} mm; to {F_end/1000:.2f} kN by s={s_end:.3f}: {trav:.3f} mm per disc, "
                f"~{(F_end-Fpre)/1000/trav:.1f} kN/mm; two in series {2*trav:.3f} mm")
    print(txt)
T_av, eta = 10.8, 0.85
thr = T_av * eta / Fpre * 1000
print(f"  NEMA 23 + 10:1 = {T_av} N*m at the crank stalls at 4 kN wherever ds/dtheta > {thr:.2f} mm/rad,")
print("  i.e. for obstructions met above ~0.15-0.16 mm over BDC (b1b calc §1 table). Below that the crank")
print("  passes BDC, so the stack needs ~0.16 mm of travel beyond its preload, less the loop's own")
print("  0.04-0.1 mm at 4 kN in a 40-100 kN/mm loop: two A35.5 in series do it (b1b's '4 kN, ~4 kN/mm').")
print("  Prime shows only a light stainless M3-M12 Belleville assortment [sourcing/amazon-prime.md];")
print("  DIN 2093 discs of this size come from industrial suppliers.")

# ---------------------------------------------------------------------------
hdr("8. b8 (and b6): flat crown-scoring blades closed to a fixed stop")
wall, rj = 0.49, 0.85
strand_top = (0.345, 0.37 + 0.06)       # bundle radius + offset [facts; b7 calc §3]
centre_err = 0.05                       # conductor centre height in the clamp [estimate]
for f in (0.5, 0.6, 0.7, 0.8):
    zb = rj - f * wall
    lo = zb - strand_top[1] - centre_err
    hi = zb - strand_top[0] + centre_err
    print(f"  score {int(f*100)} % of nominal wall at the crown: blade {zb:.3f} mm from the conductor centre; "
          f"ligament over the strands {lo:+.3f} to {hi:+.3f} mm")
print("  -> at 70-80 % the worst case reaches the strands; a fixed stop holds ~50-60 %, or the blade rides")
print("     a shoe on the jacket's own top so centre-height error drops out.")

# ---------------------------------------------------------------------------
hdr("9. A sprocket for the contact carrier ('SMT-style' feeders in b2, b3)")
print("  EIA-481 8 mm tape: sprocket hole 1.5 mm at 4.0 mm pitch [assumption, standard]; XH carrier: 1.5 mm")
print("  holes [xh-facts §1] at ~7.1 mm (Wurth analog; 7.0-8.5 scaled from clone drawings) -> the hole")
print("  matches, the pitch does not.")
t_c = 0.2
for pitch in (7.1, 8.5):
    for N in (8, 12, 16, 22):
        R = N * pitch / (2 * math.pi)
        eps = t_c / (2 * R) * 100
        print(f"  pitch {pitch} mm, {N:2d} teeth: pitch radius {R:5.1f} mm, carrier strain {eps:.2f} % "
              f"({'elastic' if eps < 0.41 else 'at yield' if eps < 0.59 else 'plastic'}; yield 0.41-0.59 %)")
print("  -> a sprocket the carrier wraps must be ~25 mm radius or larger (22 teeth at 7.1 mm), or the drive")
print("     is a pawl on a flat run (the applicator's own feed finger principle).")

# ---------------------------------------------------------------------------
hdr("10. b8: a residual fold kink at the root, and the fronts at the gang push")
print("  Each conductor in b8 goes forward, back over the clamp face (R 1.5-2.5 mm), forward, back, forward")
print("  [b1: ~4 reversals]. Copper sets below a ~67 mm radius [digest], so a kink angle remains at the root.")
print("  If the comb holds the tips in the plane, the kink becomes a bow that uses length:")
for ell in (12.0, 15.0):
    row = ", ".join(f"{a:2d} deg -> {ell*(1-math.cos(math.radians(a))):.2f} mm short" for a in (5, 10, 15))
    print(f"    free length {ell:.0f} mm: {row}")
print("  against a gang window of ~+/-0.3 mm [digest] that the housing fan already uses 0.06 mm of (4P).")
print("  The angle differs conductor to conductor (each is picked, parked and laid out separately).")

# ---------------------------------------------------------------------------
hdr("11. b1's catch plate: is the box wider than the crimped barrels?")
box_W = (1.85, 1.95)     # clone 1.85-1.90, JST envelope 1.95 [xh-facts §1]
box_H = (2.2, 2.4)       # clone 2.2-2.35, JST 2.4 [xh-facts §1]
ins_W = (1.8, 2.0)       # insulation crimp width, estimate [xh-facts §1 table, calc C1 §3]
ins_H = (1.8, 1.8)       # insulation crimp height, KONNRA clone spec at 22 AWG [digest]
con_W, con_H = 1.5, (0.69, 1.12)   # conductor crimp [xh-facts §1 estimate]
lance = (0.6, 0.9)       # lance proud of the floor, tip 2.4-2.6 mm behind the front (over the neck)
print(f"  width : box {box_W[0]}-{box_W[1]} vs crimped insulation barrel {ins_W[0]}-{ins_W[1]} mm "
      f"-> margin {box_W[0]-ins_W[1]:+.2f} to {box_W[1]-ins_W[0]:+.2f} mm")
print(f"  height: box {box_H[0]}-{box_H[1]} vs crimped insulation barrel ~{ins_H[0]} mm "
      f"-> margin {box_H[0]-ins_H[0]:+.2f} to {box_H[1]-ins_H[0]:+.2f} mm")
print(f"  neck  : crimped conductor barrel {con_W} wide x {con_H[0]}-{con_H[1]} tall behind the box: "
      f"margin {box_W[0]-con_W:+.2f} mm a side-pair in width, {box_H[0]-con_H[1]:+.2f} mm or more in height")
print(f"  lance : stands {lance[0]}-{lance[1]} mm below the floor with its tip over the neck, pointing rearward")
print("  -> a slot 'narrower than the box and wider than the crimped barrels' has no width window;")
print("     a catch works on height (plate edge ~2.0 mm above the floor, bearing on the box roof's rear")
print("     edge, 0.4-0.6 mm band) or as a fork in the neck, and in both cases clear of the lance. A plate")
print("     reaching below the floor meets the lance tip end-on, as a housing shoulder does in a retention")
print("     pull; 20 N there is an unrated retention test on the part that must later latch [xh-facts §3].")
