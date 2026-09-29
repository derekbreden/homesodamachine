"""terminal-supply explorer, jst-crimp-study, wave 2 (2026-09-28).

Numbers behind the wave-2 repairs and new directions:

  1. Skip-pitch strip: which fan pitches let a ribbon's other conductors lie in
     the strip's plane without landing on a fresh contact (repairs a2 Break 1).
  2. Crowned anvil: how far the fresh contacts fall below the station plane when
     the strip runs over a crown, and whether the carrier stays elastic.
  3. The gap a skip-pitch strip opens for a backlight (a2 Break 4).
  4. The set a lifted conductor keeps (the lifter repair's open question).
  5. The post as a gripper (a6): pick forces, capture, stiffness, float, and
     the axial tolerance chain from the box front to the bellmouth.
  6. Cutting the tab before the wire exists (a6 with strip supply).
  7. Supply consumption and cost when every other contact is removed.
  8. A self-locking wedge that sets anvil height per cavity (a5 repair).
  9. Where the drop-shear's kink ends up after the next index (a2 Break 3).
 10. Open-wing width by supply form, and what it does to other explorers'
     geometry (a7).
 11. Time per crimp for the post gripper (a6) and for the crown station (a2d).

Run:  python3 wave2.py > wave2.out.txt

Labels:
  [repo] [mfr] [mfr-an] [source] [calc] [estimate] [assumption]
  [critique] numbers from machine-that-sees-and-learns' calc on_terminal_supply
"""
from math import pi, tan, atan, cos, sin, acos, radians, degrees, sqrt

def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)

# ---------------------------------------------------------------- inputs
P = 7.10                  # [mfr-an] Wurth carrier pitch; SXH pitch unmeasured
T = 0.20                  # [source] stock thickness
E_BRONZE = 110e3          # MPa, C5191 [estimate]
SY_BRONZE = (450., 650.)  # MPa, C5191 spring temper range [estimate]
E_CU = 117e3              # MPa
SY_CU_ANNEALED = 70.      # MPa, annealed tinned strand [estimate]
D_STRAND = 0.08           # mm [source S29]
N_STRAND = 60
WIRE_OD = 1.70            # mm [source]
WING_HALF = 1.50          # mm, clone open insulation wing half-width (3.0 max) [source]
WING_H = 3.20             # mm, clone open insulation barrel height, max [source]
CRIMPED_HALF = 1.0        # mm, crimped insulation barrel half-width ~2.0 [source KONNRA]
XH = 2.50

# ---------------------------------------------------------------- 1
hdr("1. Skip-pitch strip: where a ribbon's other conductors may lie in the strip's plane")
print("Fresh contacts stand upstream of the station every s mm (s = 7.1 normal; 14.2 with every")
print("other contact removed; 21.3 with two of three removed). A waiting conductor (OD 1.7) lying")
print(f"in the plane collides if it lands within {0.85+WING_HALF:.2f} mm of a fresh contact's centre")
print(f"[critique calc 2]; a done conductor carrying its crimped contact within {CRIMPED_HALF+WING_HALF:.2f} mm.")
print("Worst case: all N-1 other conductors on the upstream side, at fan pitch p, at -p ... -(N-1)p.")

def clear_upstream(N, p, s, thr):
    for i in range(1, N):
        x = i * p
        m = 1
        while m * s - thr < x + thr + 1e-9 and m < 20:
            if abs(x - m * s) < thr:
                return False
            m += 1
    return True

for s in (P, 2 * P, 3 * P):
    print(f"\n  fresh contacts every {s:.1f} mm")
    for N in (3, 4, 5):
        ok = []
        p = 1.70
        while p <= 8.0 + 1e-9:
            if clear_upstream(N, p, s, 2.50):
                ok.append(round(p, 2))
            p += 0.05
        # compress into ranges
        rng = []
        for v in ok:
            if rng and abs(v - rng[-1][1] - 0.05) < 1e-6:
                rng[-1][1] = v
            else:
                rng.append([v, v])
        txt = ", ".join(f"{a:.2f}-{b:.2f}" for a, b in rng) if rng else "none"
        print(f"    {N}P (N-1={N-1} upstream): clear for fan pitch {txt} mm (1.70-8.00 scanned)")
print("\n  -> with every contact on the strip (7.1 mm) no 4P or 5P fan is clear [agrees with critique];")
print("     with every other contact removed (14.2 mm) any fan up to ~2.9 mm is clear for 5P, ~3.9 for 4P.")
print("     The punch holder still needs the nearest neighbour outside its footprint (section 2 note).")

# ---------------------------------------------------------------- 2
hdr("2. Crowned anvil: fresh contacts fall below the plane the conductors lie in")
print("The strip runs over a crown (a cylinder whose axis is along the contacts). The station")
print("contact sits on a flat land at the crest; a contact at arc distance s lies rotated by s/R")
print("and its open wing tips (height h above its floor) sit at (R+h)cos(s/R) - R relative to the crest.")
print(f"Carrier bending strain = t/(2R); yield strain = Sy/E = {SY_BRONZE[0]/E_BRONZE*100:.2f}-{SY_BRONZE[1]/E_BRONZE*100:.2f} %.")
R_el = [E_BRONZE * T / (2 * sy) for sy in SY_BRONZE]
print(f"  smallest elastic crown radius: {R_el[1]:.1f}-{R_el[0]:.1f} mm")
print(f"\n  {'R mm':>6} {'strain %':>9} {'elastic?':>9} | wing tip vs crest (mm), h={WING_H}:  s=7.1   s=14.2   s=21.3")
for R in (8, 10, 12, 15, 20, 25, 30, 40):
    eps = T / (2 * R) * 100
    el = "yes" if eps <= SY_BRONZE[0] / E_BRONZE * 100 else ("edge" if eps <= SY_BRONZE[1] / E_BRONZE * 100 else "no")
    vals = []
    for s in (P, 2 * P, 3 * P):
        th = s / R
        if th > pi / 2:
            vals.append("  below")
        else:
            vals.append(f"{(R + WING_H) * cos(th) - R:+7.2f}")
    print(f"  {R:6.0f} {eps:9.2f} {el:>9} |                                  {vals[0]} {vals[1]} {vals[2]}")
print("\n  -> an elastic crown (R >= ~25 mm) drops the 14.2 mm neighbour's wing tips 1.2 mm below the")
print("     crest plane: every other conductor can lie flat in the station plane at any fan pitch.")
print("     With every contact on the strip, the 7.1 mm neighbour clears only at R <= ~8 mm, which")
print("     bends the carrier plastically at every contact that passes.")
for R in (25.,):
    for x in (2.5, 3.0, 4.0, 5.0, 7.1):
        print(f"  R {R:.0f}: the crown surface at x = {x:3.1f} mm lies {R*(1-cos(x/R)):.2f} mm below the crest plane")
print("  -> pins in the removed contacts' holes at +/-7.1 mm sit ~1.0 mm below the plane: a flush or")
print("     recessed pin tip never touches a conductor lying over it.")

# ---------------------------------------------------------------- 3
hdr("3. The gap a skip-pitch strip opens beside the station")
for s in (P, 2 * P):
    gap = s - 2 * WING_HALF
    print(f"  neighbour at {s:4.1f} mm: clear gap between open wings {gap:4.1f} mm")
    for dh in (0.0, 0.10, 0.15, 0.25):
        th = atan((dh + 0.02) / s)
        hide = 1.9 * tan(th) * 1000
        print(f"     neighbour taller by {dh:.2f} mm -> grazing view needs >= {degrees(th):.2f} deg; near wing tip "
              f"hidden by {hide:3.0f} um")
print("  -> at 14.2 mm the grazing view needs half the tilt, and an 11 mm gap takes a backlight tile")
print("     (a 3-5 mm wide diffuser with one white LED) dropped in from above between look and stroke.")
print("  -> on a crown (section 2) the neighbour lies below the station plane, so the view along the")
print("     strip at wing height is unobstructed and needs no tilt at all.")

# ---------------------------------------------------------------- 4
hdr("4. The set a lifted conductor keeps (the lifter repair)")
print("A conductor clamped at the web and lifted delta at distance a (a bar or comb) bends most at the")
print("clamp. Strands slide on one another, so each 0.08 mm strand bends about its own axis.")
ky = 2 * SY_CU_ANNEALED / (E_CU * D_STRAND)
print(f"  strand yield curvature {ky:.4f} /mm (radius {1/ky:.0f} mm) [calc, agrees with digest ~67 mm]")
I_s = pi * D_STRAND ** 4 / 64
EI_strands = N_STRAND * E_CU * I_s
EI_sil = 1.6   # N mm^2, mid of 0.8-2.4 [source ribbon-as-pallet calc 4]
print(f"  EI strands {EI_strands:.1f} N mm^2, silicone ~{EI_sil} N mm^2")

def m_round(kappa):
    """moment of one round strand, elastic-perfectly-plastic, curvature kappa (per mm)."""
    r = D_STRAND / 2
    n = 400
    M = 0.0
    for i in range(n):
        y = -r + (i + 0.5) * 2 * r / n
        w = 2 * sqrt(max(r * r - y * y, 0))
        sig = max(-SY_CU_ANNEALED, min(SY_CU_ANNEALED, E_CU * kappa * y))
        M += sig * y * w * (2 * r / n)
    return M

def m_cond(kappa):
    return N_STRAND * m_round(kappa) + EI_sil * kappa

# tabulate M(kappa) once, then invert by interpolation
_K = [0.0] + [1e-4 * (1.06 ** i) for i in range(160)]
_M = [m_cond(k) for k in _K]

def kappa_of_m(M):
    if M <= 0:
        return 0.0
    for i in range(1, len(_K)):
        if _M[i] >= M:
            f = (M - _M[i - 1]) / (_M[i] - _M[i - 1])
            return _K[i - 1] + f * (_K[i] - _K[i - 1])
    return _K[-1]

def lift(a, delta):
    # find tip load P so that deflection at a equals delta; return residual deflection at a
    lo, hi = 0.0, 50.0
    for _ in range(40):
        Pm = (lo + hi) / 2
        n = 100
        d = 0.0
        for i in range(n):
            x = (i + 0.5) * a / n
            d += kappa_of_m(Pm * (a - x)) * (a - x) * a / n
        if d < delta:
            lo = Pm
        else:
            hi = Pm
    Pm = (lo + hi) / 2
    n = 100
    dres = 0.0
    kmax = kappa_of_m(Pm * a)
    for i in range(n):
        x = (i + 0.5) * a / n
        k = kappa_of_m(Pm * (a - x))
        kr = k - Pm * (a - x) / (EI_strands + EI_sil)   # elastic unloading
        dres += max(kr, 0) * (a - x) * a / n
    return Pm, kmax, dres

print(f"\n  {'a mm':>5} {'lift mm':>8} {'push N':>7} {'max curv /mm':>13} {'x yield':>8} {'set kept mm':>12}")
for a in (10, 15, 20, 25, 30):
    for delta in (3.5,):
        Pm, kmax, dres = lift(a, delta)
        print(f"  {a:5.0f} {delta:8.1f} {Pm:7.2f} {kmax:13.4f} {kmax/ky:8.1f} {dres:12.2f}")
print("  -> lifted 3.5 mm at 10-15 mm from the web, a conductor keeps ~1.3-2.2 mm of lift when")
print("     released; at 25-30 mm it keeps only a few tenths. The set is harmless during crimping")
print("     and is undone by whatever combs the conductors to 2.5 mm for insertion.")

# ---------------------------------------------------------------- 5
hdr("5. The post as a gripper (a6)")
GRIP = (0.2, 2.0)          # N, estimate from Molex KK secondhand figure [terminal_supply calc 7]
W = 0.043e-3 * 9.81        # N
print(f"  weight {W*1000:.2f} mN; post grip {GRIP[0]}-{GRIP[1]} N [estimate]: {GRIP[0]/W:.0f}-{GRIP[1]/W:.0f} x weight")
print(f"  vacuum nozzle 1.0 mm at 80 kPa: {pi*0.5**2*80e-3*1000:.0f} mN normal [critique calc 7]: a nozzle")
print("  places into an open pocket; it cannot push a box onto a post. A post pushed into a box")
print("  whose rear rests on a pocket wall needs only that wall to react 0.2-2 N.")
print("\n  Capture of a chamfered post tip by the box mouth [source S19-S21, clone box]:")
box_in_w = 1.85 - 2 * T
box_in_h = 2.20 - 2 * T
post = 0.64
print(f"    box inside ~{box_in_w:.2f} x {box_in_h:.2f} mm; post {post} mm square")
print(f"    lateral capture +/-{(box_in_w-post)/2:.2f} mm, vertical +/-{(box_in_h-post)/2:.2f} mm before the")
print("    spring leaves' own lead-in centre the post; the pocket holds the box to ~+/-0.1 mm.")
print("\n  Post stiffness, square 0.64 mm, k = 3EI/L^3:")
I = post ** 4 / 12
for mat, Em in (("brass", 100e3), ("steel", 200e3)):
    for L in (2.0, 3.0, 4.0):
        print(f"    {mat} free length {L:.0f} mm: {3*Em*I/L**3:6.0f} N/mm")
print("  -> a 2-4 mm post is rigid against every placement load; it must float in its holder so")
print("     the punch's lead-in can centre the barrels (as a4). Float +/-0.2 mm on springs of")
print("     1-2 N/mm resists with 0.2-0.4 N, against punch lead-in forces of tens of N.")
print("\n  Axial chain, box front (the post holder face) to the conductor barrel's rear edge:")
print("    clone drawings: box 2.0 + transition 0.4-0.6 + conductor barrel 1.25-1.5 -> 3.65-4.1 mm")
print("    within one lot +/-0.05 mm [estimate, progressive die]; between brands up to +/-0.25 [source]")
print("    bellmouth window +/-0.1 mm [xh-facts]: dead reckoning holds within a lot, not across lots.")
PXMM = (45, 86)
for pxmm in PXMM:
    print(f"    backlit silhouette on the post at {pxmm} px/mm: 0.1 mm = {0.1*pxmm:.1f} px; an edge fit to 0.2 px"
          f" = {0.2/pxmm*1000:.1f} um")
print("  -> the camera measures each contact on the post; the post carriage moves by the error.")
print("     Carriage resolution (NEMA 17 on Tr8x2, 1/16 step) 0.6 um; repeatability of a printer-class")
print("     axis +/-0.02-0.05 mm, inside the window, and the look is repeated after the move.")

# ---------------------------------------------------------------- 6
hdr("6. Cutting the tab before the wire exists (strip on the post)")
print("  With the post in the leading contact's box and pins in the carrier, nothing lies over the tab:")
print("  a flush punch from above, or a drop-shear, cuts it. Shear force 48-158 N [xh-facts C1].")
for lev in (3, 4):
    print(f"    metal-gear servo 45 N at a 20-25 mm arm x {lev}:1 lever = {45*lev} N")
print("  Stub target ~1 stock thickness (0.2-0.3 mm) [xh-facts S5, S23]. The shear line is set from")
print("  the contact's own rear edge as seen (per contact), not from the carrier, so tab variation")
print("  between brands (0.8 +/- 0.2 vs 1.00 +/- 0.15) drops out.")

# ---------------------------------------------------------------- 7
hdr("7. Supply when every other contact is removed from the strip")
prog = 53 * 61
prog_sp = prog * 1.10
for skip, name in ((1, "every contact used"), (2, "every other removed"), (3, "two of three removed")):
    used = prog_sp * skip
    print(f"  {name:22s}: {used:6.0f} contacts from strip for {prog_sp:.0f} crimps; "
          f"{used/8000:4.2f} reels of 8,000; strip {used*P/1000:5.1f} m; a unit {53*skip*P/1000:.2f} m")
print("  prices [xh-facts 6]: Digi-Key reel $0.0235, LCSC @1k $0.0100, clone CJT reel $0.0079")
for price, nm in ((0.0235, "Digi-Key SXH reel"), (0.0100, "LCSC SXH @1k"), (0.0079, "LCSC CJT clone")):
    print(f"    {nm:18s}: program at skip 2 ${prog_sp*2*price:6.0f}; at skip 1 ${prog_sp*price:6.0f}")
print("  -> one 8,000-piece reel covers the whole program even with every other contact removed.")
print(f"  -> the removed contacts ({prog_sp:.0f}) are loose stock for hand repair or any loose route.")

# ---------------------------------------------------------------- 8
hdr("8. A self-locking wedge that sets the anvil's height per cavity (a5)")
F = 3000.0
for mu in (0.10, 0.15):
    phi = degrees(atan(mu))
    for a in (2.0, 3.0, 5.0):
        back = F * tan(radians(a - phi))   # negative -> self-locking
        state = "self-locking" if back < 0 else f"back-drives with {back:.0f} N"
        print(f"  mu {mu:.2f} (friction angle {phi:4.1f} deg), wedge {a:.0f} deg: {state}; "
              f"height per mm of wedge travel {tan(radians(a))*1000:5.0f} um")
print("  a Tr8x2 lead screw at 1/16 step moves the wedge 0.6 um -> anvil height steps of 0.02-0.05 um.")
print("  -> a 2-3 deg steel wedge under the anvil holds 3 kN on its own, needs only a push against its")
print("     return spring to set, and gives the camera a per-cavity height to set it to.")

# ---------------------------------------------------------------- 9
hdr("9. Where the drop-shear's kink goes after the next index (a2 Break 3 repair)")
print("  Upstream carrier clamped flat to an edge at x_c (between the upstream contact's tab and the")
print("  station tab); everything downstream of x_c drops 0.3-0.5 mm; the carrier yields at x_c")
print("  [critique calc 6: yields at 0.16 mm of drop, 0.14-0.34 mm set, 1.7-4.2 deg].")
for s in (P, 2 * P):
    for xc in (-2.0, -3.0):
        after = xc + s
        print(f"    index {s:4.1f} mm, clamp edge at {xc:+.1f} mm: the kink moves to {after:+.1f} mm, "
              f"downstream of the new station tab (0): scrap side")
print("  -> the next contact's own tab and the carrier upstream of it are never bent.")

# ---------------------------------------------------------------- 10
hdr("10. Open-wing width by supply form, and the geometry it sets for other explorers")
forms = [
    ("JST SXH/BXH, catalog envelope", 1.95, 1.95),
    ("Wurth 646 x01 137 22 (analog)", 2.30, 2.30),
    ("clone drawings (HDGC/DLL/CJT/JXT)", 2.46, 3.00),
]
print(f"  {'supply':36s} {'wings mm':>10} | gap to an open neighbour at 2.5 / 3.4 / 5.0 mm pitch")
for nm, lo, hi in forms:
    g = [f"{p-hi:+.2f}..{p-lo:+.2f}" for p in (2.5, 3.4, 5.0)]
    print(f"  {nm:36s} {lo:4.2f}-{hi:4.2f} | {g[0]:>12} {g[1]:>12} {g[2]:>12}")
print("  (clone tolerance +/-0.25 on open wings widens the clone row further)")
print("\n  v4b pocket plate, floor channel 2.05 mm (critique's corrected width):")
for nm, lo, hi in forms:
    fall = "may fall in (tips < 2.05)" if lo < 2.05 else "rest on top (tips >= 2.05)"
    print(f"    barrels-down {nm:36s}: wing tips {lo:.2f}-{hi:.2f} apart -> {fall}")
print("  a3 hanging rail, 2.4 mm upper slot: hangs only if the open wings exceed 2.4 mm:")
for nm, lo, hi in forms:
    hang = "hangs" if lo > 2.4 else ("some hang" if hi > 2.4 else "falls through")
    print(f"    {nm:36s}: {hang}")
print("  -> the two orienters that use the wings as a head (a3 rail, v4b plate) depend on clone-width")
print("     wings; genuine JST, if inside its envelope, needs the lance or the box to orient it.")

# ---------------------------------------------------------------- 11
hdr("11. Time per crimp [estimate]")
a6 = [("pick from the pocket plate (approach, spear, lift)", 10), ("travel to the die", 5),
      ("silhouette on the post, correct, look again", 10), ("conductor presented and steered", 30),
      ("slow stroke", 30), ("release by pulling the wire off the post", 5), ("after-crimp look", 10),
      ("return; plate re-tapped while the stroke runs", 0), ("retries, average", 15)]
tot = sum(t for _, t in a6)
for n, t in a6:
    print(f"  a6 {n:52s} {t:3d} s")
print(f"  a6 per crimp ~{tot} s -> 53 crimps in {tot*53/60:.0f} min")
a2d = [("index two pitches, pins home", 6), ("look at the waiting contact (backlight in the gap)", 10),
       ("conductor presented and steered", 30), ("slow stroke", 30), ("drop-shear", 5),
       ("after-crimp look", 10), ("retries, average", 15)]
tot2 = sum(t for _, t in a2d)
print(f"  a2d per crimp ~{tot2} s -> 53 crimps in {tot2*53/60:.0f} min")
