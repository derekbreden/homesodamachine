"""Numbers for the wave-2 exchange: ribbon-as-pallet on machine-that-sees-and-learns.

jst-crimp-study, explorer ribbon-as-pallet, wave 2, 2026-09-28.
Run:  python3 exchange_on_machine_that_sees.py > exchange_on_machine_that_sees.out.txt

Dimensions come from ../../../context/xh-facts.md (clone drawings S19-S22, KONNRA
clone spec) and from the two explorers' wave-1 calcs:
  [calc R]  ../calc/pallet_geometry.out.txt            (ribbon-as-pallet)
  [calc V]  ../../machine-that-sees-and-learns/calc/*  (machine-that-sees-and-learns)
Material values are labelled [assumption]. Nothing here was measured.
"""
from math import pi, sqrt, sin, cos, tan, radians, degrees, atan, asin, exp


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------- shared inputs
OD = 1.7                    # insulation OD, mm [source BNTECHGO via xh-facts s7]
BUNDLE = 0.72               # gathered 60 x 0.08 mm strands [xh-facts s7]
CB_WING_H = (1.50, 1.60)    # conductor barrel open height [xh-facts s1 clones]
IB_WING_H = (2.75, 3.20)    # insulation barrel open height [xh-facts s1 clones]
IB_WING_W = (2.46, 3.00)    # insulation barrel open width
AXIS_LAID = 0.85            # strand axis above barrel floor after lay-in [calc V vision_budget s5]
BOX_L = 2.0                 # box length [mfr S1]
LANCE_TIP = (2.4, 2.6)      # lance tip behind the front [xh-facts s1]
LANCE_PROUD = (0.6, 0.9)    # lance stands proud of the floor side
BOX_W = (1.85, 1.95)
BOX_H = (2.20, 2.35)
OVERALL = (5.8, 6.73)       # front of box to rear of insulation barrel, clones
CB_L = (1.25, 1.5)          # conductor barrel length [estimate, xh-facts]
WIN_L = (0.5, 1.0)          # window between barrels [calc V vision_budget s4]
IB_L = (0.8, 1.5)           # insulation barrel length [estimate, xh-facts]
BRUSH = (0.2, 0.5)          # brush past the conductor barrel [calc V s2]
CCH = (0.73, 0.90)          # conductor crimp height (KONNRA 0.73; estimate 0.88)
CCW = (1.60, 1.90)          # conductor crimp width 1.75 +/- 0.15 (KONNRA)
ICH = (1.70, 1.90)          # insulation crimp height 1.80 +/- 0.10 (KONNRA)
ICW = (1.8, 2.05)           # insulation crimp width <= 2.05 (KONNRA)
RETENTION_MIN = 19.6        # N, clone terminal retention in housing (KONNRA)
PULL_MIN = 39.2             # N, JST 22 AWG pull-out minimum [mfr S6]
WIRE_BREAK = (85, 100)      # N [source S23]

# copper strands
E_CU = 117e3                # MPa [assumption, annealed copper]
G_CU = 44e3                 # MPa [assumption]
SY_CU = (50.0, 70.0, 100.0) # MPa, annealed tinned strand yield range [assumption]
D_STR = 0.08
N_STR = 60
EI_STR = N_STR * E_CU * pi * D_STR**4 / 64   # strands free to slip [calc R s4]

# ============================================================================
hdr("1. v1: where the neighbours sit relative to the side silhouette")
# Camera 2 looks along X (across the wire) at wing-tip height. Neighbours in the
# fan comb are at pitch p in the same plane as the active conductor.
for p in (5.0, 6.0):
    print(f"fan pitch {p:.1f} mm, neighbours in plane: neighbour axis on the sight line at "
          f"X = +/-{p:.1f} mm, Y = the active conductor's Y, Z = the active conductor's Z")
    print("   -> both the camera-side and the backlight-side neighbour cross the line of sight"
          " for every inner conductor;")
    print("      the end conductors have one neighbour, which blocks the camera or the backlight.")
# How high must the neighbours be to clear the silhouette band (up to the insulation wing tips)?
margin = 0.5
for wh in IB_WING_H:
    h_axis = wh + margin + OD / 2
    print(f"insulation wing tips {wh:.2f} mm above the barrel floor: neighbour axis must sit "
          f">= {h_axis:.2f} mm above the floor (0.5 mm margin), i.e. {h_axis - AXIS_LAID:.2f} mm "
          f"above the laid-in conductor's axis")
print("   -> a1's fan block holds neighbours at h ~5 mm above the anvil plane: it clears.")
# Tilted sight line alternative
print("A tilted sight line (camera raised by angle t in the X-Z plane) passes above one neighbour")
print("and below the other. Clearing a neighbour's jacket by 0.2 mm needs:")
for p in (5.0, 6.0):
    t = degrees(atan((OD / 2 + 0.2) / p))
    print(f"  p = {p:.1f} mm: t >= {t:.1f} deg")
t = radians(11.0)
for H, W in ((CCH[0], CCW[0]), (CCH[1], CCW[1])):
    app = H * cos(t) + W * sin(t)
    print(f"  at 11 deg a crimp H {H:.2f} x W {W:.2f} shows a silhouette {app:.3f} mm tall: "
          f"{app - H:+.3f} mm of it is width, and width varies +/-0.15 mm -> "
          f"+/-{0.15 * sin(t):.3f} mm")
print("   -> the tilt mixes crimp width into crimp height at 0.2 mm/mm; not a crimp-height view.")
print("Camera 1 (oblique, a deg from vertical, from the side) with neighbours lifted to axis height h:")
print("  lowest point z0 in the U it can still see past the camera-side neighbour (jacket r 0.85):")
for p in (5.0, 5.5, 6.0):
    for h in (4.55, 5.0):
        row = []
        for a in (30, 35, 40, 45):
            k = 1 / tan(radians(a))          # line: Z = z0 + k X
            z0 = h - k * p + (OD / 2) * sqrt(1 + k * k)
            row.append(f"{a} deg: z0 >= {max(z0, 0):.2f}")
        print(f"  pitch {p:.1f}, h {h:.2f}: " + "; ".join(row) + " mm above the floor")

# ============================================================================
hdr("2. v1: the oblique camera sees X and Z on one image axis")
hover_axis = IB_WING_H[1] + 0.2 + OD / 2   # insulation clears the tallest insulation wing
dz = hover_axis - AXIS_LAID
print(f"hover: insulation bottom 0.2 mm above a {IB_WING_H[1]:.2f} mm wing -> axis {hover_axis:.2f} mm;"
      f" laid in: {AXIS_LAID} mm; drop dz = {dz:.2f} mm")
for a in (30, 45):
    print(f"  camera {a} deg from vertical: dz shows as {dz * tan(radians(a)):.2f} mm of apparent X;"
          f" X is recoverable only if dz is known to {0.49 / tan(radians(a)):.2f} mm"
          f" (half the +/-0.49 mm lateral room)")
print("   -> with camera 2 blocked, X comes from the commanded Z, not from the picture.")
print("   Lateral capture that needs no picture:")
print(f"   strands {BUNDLE} mm into a 1.68-1.90 mm open conductor barrel:"
      f" +/-{(1.68 - BUNDLE) / 2:.2f}..{(1.90 - BUNDLE) / 2:.2f} mm")
print(f"   jacket {OD} mm into a {IB_WING_W[0]:.2f}-{IB_WING_W[1]:.2f} mm open insulation barrel:"
      f" +/-{(IB_WING_W[0] - OD) / 2:.2f}..{(IB_WING_W[1] - OD) / 2:.2f} mm")
print("   pallet delivery [calc R s1]: +/-0.1 mm at the comb face, +/-0.2-0.3 mm tip wander")

# ============================================================================
hdr("3. The proof pull: what is behind the box, and where a pull can react")
neck_min = OVERALL[0] - BOX_L - CB_L[1] - WIN_L[1] - IB_L[1]
neck_max = OVERALL[1] - BOX_L - CB_L[0] - WIN_L[0] - IB_L[0]
print(f"neck (box rear to conductor-barrel front) from clone lengths: {neck_min:+.2f} .. {neck_max:+.2f} mm")
print(f"brush reaches into it by {BRUSH[0]}-{BRUSH[1]} mm -> free gap {neck_min - BRUSH[1]:+.2f} .. "
      f"{neck_max - BRUSH[0]:+.2f} mm  (undetermined; one kit contact under a caliper settles it)")
print(f"lance tip {LANCE_TIP[0] - BOX_L:.1f}-{LANCE_TIP[1] - BOX_L:.1f} mm behind the box rear, "
      f"{LANCE_PROUD[0]}-{LANCE_PROUD[1]} mm below the floor: it crosses the plane of any plate "
      "set against the box rear")
print(f"   a plate with a slot open upward (v5: crimp dropped in from above) has material under the"
      f" floor strip -> it meets the lance unless the slot runs >= {LANCE_PROUD[1]:.1f} mm below the floor")
print(f"   loaded at its tip, the lance carries the retention load; clone retention min {RETENTION_MIN} N"
      f" = the 20 N proof; v3's pull to failure goes to {WIRE_BREAK[1]} N")
# Plate requirements
print("   plate that works: thickness <= free gap - 0.2 mm placement; slot wider than the floor strip"
      " and the lance, narrower than the box less its 0.2 mm walls (~1.4 mm); slot depth past the lance;"
      " bearing on the side walls (and top wall if the slot opens downward)")
wall_area = 2 * 0.2 * 2.2
for F in (20, 100):
    print(f"     side-wall bearing {wall_area:.2f} mm^2 at {F} N: {F / wall_area:.0f} MPa (bronze yields ~450+)")
# Push sleeve on the insulation crimp rear
print("Push sleeve on the rear of the insulation crimp (to avoid the box altogether):")
print(f"   insulation crimp {ICH[0]}-{ICH[1]} x <= {ICW[1]} mm against a {OD} mm jacket: radial step"
      f" {(ICH[0] - OD) / 2:.2f}-{(ICW[1] - OD) / 2:.2f} mm -> nothing to bear on")
# Carrier tab reaction
b, t = 0.8, 0.2
for sy in (450.0, 600.0):
    Fy = sy * b * t
    Mp = sy * b * t**2 / 4
    print(f"carrier tab 0.8 x 0.2 mm, bronze yield {sy:.0f} MPa [assumption]: axial yield {Fy:.0f} N;"
          f" plastic moment {Mp:.1f} N mm")
    for e in (0.40, 0.85):
        print(f"   pull line {e:.2f} mm above the tab plane, no hold-down: tab bends at {Mp / e:.1f} N of pull")
for e in (0.40, 0.85):
    for L in (3.0, 5.0):
        print(f"   pull line {e:.2f} mm up, hold-down {L:.0f} mm ahead of the tab, support under it: hold-down"
              f" = {e / L:.2f} x pull -> {20 * e / L:.1f} N at 20 N, {100 * e / L:.1f} N at 100 N; tab in"
              " compression only")
print("   -> the tab, held against pitch, reacts a proof pull and pull-outs up to ~70-100 N; a crimp"
      f" that survives to tab yield is already {72 / PULL_MIN:.1f}x the 39.2 N minimum")

# ============================================================================
hdr("4. v3: coupon length for a capstan grip, and the jacket at the capstan entry")
for D in (10.0, 15.0, 25.0):
    turn = pi * (D + OD)
    Lc = 3 * turn + 20 + 10 + 6 + 2.4     # 3 turns, lead from crimp, tail to pin, contact, strip
    total = 153 * Lc / 1000
    print(f"drum {D:.0f} mm: {turn:.0f} mm per turn; coupon ~{Lc:.0f} mm; 153 coupons = {total:.1f} m of"
          f" conductor = {total / 5:.1f} m of 5P  (v3 counts 40 mm and 1.2 m of 5P)")
print("Friction transferred per mm of wire at the first contact with the drum, q = mu T / R:")
for D in (10.0, 15.0, 25.0):
    R = (D + OD) / 2
    for mu in (0.5, 1.0):
        q = mu * 100 / R
        print(f"  drum {D:.0f} mm, mu {mu}: T = 100 N -> {q:.1f} N/mm; over a 0.5-1.0 mm wide contact"
              f" strip of jacket {q / 1.0:.0f}-{q / 0.5:.0f} MPa of shear  (silicone tensile 8-11 MPa)")
print("Jacket-only alternative, a long pad clamp: pressure needed to pass 100 N from jacket to strands")
for mu in (0.3, 0.6):
    for L in (25.0, 40.0):
        p = 100 / (mu * pi * 0.9 * L)
        print(f"  jacket-to-strand mu {mu}, clamp {L:.0f} mm: {p:.1f} MPa on a Shore 60A jacket")
print("Soldered far-end lug: 10 mm of tinned bundle, perimeter ~2.5 mm, solder shear 20-30 MPa ->"
      f" {2.5 * 10 * 20:.0f}-{2.5 * 10 * 30:.0f} N, above wire break; coupon ~60 mm")

# ============================================================================
hdr("5. v5 / v1: roll of the crimp on a knife-edge support and silhouette crimp height")
print("Silhouette along X of a crimp rolled by r about the wire axis. Rectangle bound:")
print("  apparent = H cos r + W sin r.  Rounded-bottom bound: about half the width term.")
for H, W in ((CCH[0], CCW[0]), (CCH[1], CCW[1])):
    row = []
    for r in (0.5, 1.0, 2.0, 3.0):
        err = H * cos(radians(r)) + W * sin(radians(r)) - H
        row.append(f"{r:.1f} deg {err:+.3f}/{err / 2:+.3f}")
    print(f"  H {H:.2f} W {W:.2f}: " + "   ".join(row) + "  mm (rect/rounded)")
print("  -> against +/-0.05 mm, roll must be held to ~1-2 deg (rect) or ~2-4 deg (rounded).")
# torsional stiffness of a parted conductor
G_SIL = (1.0, 1.3)          # MPa, Shore 50-70A [assumption]
J_jk = pi / 32 * (OD**4 - 0.8**4)
GJ_str = N_STR * G_CU * pi * D_STR**4 / 32
for g in G_SIL:
    GJ = g * J_jk + GJ_str
    for L in (20.0, 35.0):
        k = GJ / L
        rolls = ", ".join(f"{int(fN * 1000)} mN -> {degrees(fN * 0.3 / k):.2f} deg" for fN in (0.01, 0.02, 0.05))
        print(f"  parted conductor GJ ~{GJ:.1f} N mm^2 (jacket {g * J_jk:.1f} + strands {GJ_str:.1f}),"
              f" {L:.0f} mm long: {k:.2f} N mm/rad; touch-down 0.3 mm off the knife line: {rolls}")
print("  -> a crimp still held by its ribbon keeps the roll the nest gave it if it is set down")
print("     on the blade at ~10-20 mN (stop at first silhouette contact, not at a force);")
print("     a crimp dropped loose onto a knife edge with round soft jaws has no roll reference.")

# ============================================================================
hdr("6. Curl from the spool, springback, and what pressing flat can and cannot do")
I_str = pi * D_STR**4 / 64
c = D_STR / 2


def moment_circle(kappa, sy, n=400):
    """Elastic-perfectly-plastic bending moment of one round strand at curvature kappa."""
    M = 0.0
    for i in range(n):
        y = -c + (i + 0.5) * 2 * c / n
        w = 2 * sqrt(max(c * c - y * y, 0.0))
        s = max(-sy, min(sy, E_CU * kappa * y))
        M += s * y * w * (2 * c / n)
    return M


for sy in SY_CU:
    ky = sy / (E_CU * c)
    print(f"strand yield {sy:.0f} MPa: yield radius {1 / ky:.0f} mm; a reverse bend stays elastic"
          f" over 2 x kappa_y, i.e. flattening removes no curl gentler than R {1 / (2 * ky):.0f} mm")
    for Rw in (25.0, 35.0, 50.0):
        k = 1 / Rw
        kr = k - moment_circle(k, sy) / (E_CU * I_str)
        Rr = 1 / kr if kr > 1e-6 else float("inf")
        for L in (7.0,):
            dev = L**2 * kr / 2
            print(f"   wound at R {Rw:.0f} mm -> residual curl R {Rr:.0f} mm -> tip {L:.0f} mm proud"
                  f" is off by {dev:.2f} mm; flattening it: "
                  f"{'elastic, springs back' if kr < 2 * ky else 'yields, partly removed'}")
print("  (silicone jacket's own springback toward straight ignored: it lowers these figures)")
print("  -> spool set leaves up to a few tenths of a mm of Z curl at 7 mm; inside the barrels'")
print("     lateral capture, and comparable to v1's ~0.3 mm spare in Z. A flat press does not")
print("     remove it; an over-bend or a roller straightener would.")
# a1's ramp bend-back of the finger kink
for sy in SY_CU[:2]:
    Rk = 2.0
    ksb = moment_circle(1 / Rk, sy) / (E_CU * I_str)   # springback curvature after a full reversal
    for s_k in (1.0, 3.0):
        ang = degrees(s_k * ksb)
        print(f"  a1's kink (R {Rk:.0f} mm, plastic over {s_k:.0f} mm) pressed straight on a ramp, yield {sy:.0f}"
              f" MPa: springs back {1 / ksb:.0f} mm radius over the kink = {ang:.1f} deg toward the kink;"
              f" {5 * tan(radians(ang)):.2f} mm at a box tip 5 mm ahead, unless over-bent")

# ============================================================================
hdr("7. Kinematic docks: a steel ball on a printed seat versus steel on steel")


def hertz_pmax(F, R, E1, n1, E2, n2):
    Es = 1 / ((1 - n1**2) / E1 + (1 - n2**2) / E2)
    return (6 * F * Es**2 / (pi**3 * R**2)) ** (1 / 3), Es


for Ftot in (10.0, 30.0):
    Fc = Ftot / 3 / (2 * cos(radians(45)))   # 3 balls, 2 flanks each at 45 deg
    for R, lab in ((3.0, "6 mm ball"), (2.0, "4 mm ball")):
        p_petg, _ = hertz_pmax(Fc, R, 210e3, 0.3, 2.1e3, 0.38)
        p_cyl, _ = hertz_pmax(Fc, R, 210e3, 0.3, 210e3, 0.3)
        print(f"  magnet preload {Ftot:.0f} N, {lab}, {Fc:.1f} N per flank: on PETG {p_petg:.0f} MPa"
              f" (PETG yields ~50); on a steel dowel {p_cyl:.0f} MPa (sphere-on-flat bound;"
              " hardened pin fine)")
print("  -> printed flanks bed in and creep under the preload; steel balls on dowel-pin pairs,")
print("     pressed into printed bodies, keep printed parts out of the contact.")

# ============================================================================
hdr("8. v6: insertion into a rear-face-up housing from a horizontal pallet")
for s in (25.0, 35.0):
    R = 2 * s / pi
    print(f"  90 deg turn made in a {s:.0f} mm parted length: R <= {R:.0f} mm, below the ~67 mm yield"
          " radius -> each conductor keeps a quarter-bend")
print(f"  gap beside an inserted neighbour at 2.5 mm pitch: {2.5 - OD:.1f} mm for a jaw")
EI5 = 5 * EI_STR
for L in (40.0,):
    k = 3 * EI5 / L**3
    print(f"  v6 split: 5P ribbon free {L:.0f} mm ahead of the clamp, EI ~{EI5:.0f} N mm^2 about its"
          f" thin axis -> tip stiffness {k:.4f} N/mm; a 0.1 N blade preload asks for"
          f" {0.1 / k:.0f} mm of deflection (it bends away instead)")

# ============================================================================
hdr("9. Piano-key fan block: where the lay-in bend goes")
for Lk in (20.0, 30.0):
    th = asin(5.0 / Lk)
    for s in (6.0, 10.0):
        print(f"  key {Lk:.0f} mm long from hinge to tip, 5 mm drop: {degrees(th):.1f} deg; bent over"
              f" {s:.0f} mm of free conductor at the key root -> R ~{s / th:.0f} mm, "
              f"{Lk:.0f}+ mm behind the contact")
print("  compare a1's finger: 5 mm drop in 1.2-3.5 mm of free conductor [borrowed-machines exchange,"
      " Break a1-1]")
print("  key width at the hinge: a 1.7 mm conductor plus two 0.4 mm walls needs >= 2.5 mm pitch,"
      " so the hinge line sits where the fan has opened to ~2.5 mm")

# ============================================================================
hdr("10. v6 twist pads: twist the stub or spin the bundle in its jacket?")
fr = 0.22 / 2.4       # N per mm of jacket, from the fully cut slug [calc R s6]
for r in (0.36, 0.45):
    for L in (7.0, 35.0):
        print(f"  jacket-to-strand friction {fr:.2f} N/mm at r {r} mm over {L:.0f} mm: spin resistance"
              f" {fr * r * L:.2f} N mm")
for sy in SY_CU[:2]:
    Mp1 = sy * D_STR**3 / 6
    print(f"  bending 60 strands into a half-turn helix over 2.4 mm (yield {sy:.0f} MPa): of order"
          f" {N_STR * Mp1 * 0.5:.2f} N mm [estimate]")
print("  -> spinning the bundle through the whole parted length resists ~7x the twist; through")
print("     only the 7 mm to the comb, ~1.5x. The stub should twist [estimate]; a pinch on the")
print("     jacket at the strip line makes it certain.")
