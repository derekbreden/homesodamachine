"""Borrowed-machines explorer: geometry of presenting ribbon conductors to
borrowed crimp tooling, fanning for a travelling head, and laser scoring.

jst-crimp-study, wave 1, 2026-09-28. Run:  python3 geometry.py > geometry.out.txt
Labels as in presses.py. Dimensions the applicator vendor or the kit parts
would settle are marked [estimate] and listed in the idea files.
"""
from math import pi, sin, cos, sqrt, atan, atan2, degrees, radians, asin

def hr(t):
    print()
    print("=" * 76)
    print(t)
    print("=" * 76)

OD = 1.7            # conductor OD, mm [facts]
RIB = 1.7           # ribbon pitch, mm [facts]
XH = 2.5            # housing pitch, mm [facts]
STRIP = 2.4         # strip length, mm [facts, JST WC-110 calibration]
BUNDLE = 0.72       # strand bundle diameter, mm [facts calc]
WALL = (OD - BUNDLE) / 2

# ------------------------------------------------------------------ 1
hr("1. Neighbour conductors versus the tooling footprint (ideas b1, b1b, b2)")
# Tooling footprint around the contact axis, in plan: the punch plates straddle the anvil.
for half_w in (3.0, 4.0, 6.0):       # mm half-width of punch/holder/guard at anvil level [estimate]
    first_clear = None
    for n_away in range(1, 6):
        y_ribbon = n_away * RIB
        y_splayed = n_away * XH
        if first_clear is None and y_ribbon - OD / 2 > half_w:
            first_clear = n_away
    n_rib = first_clear - 1 if first_clear else 5
    n_xh = int((half_w + OD / 2) // XH)
    print(f"tooling half-width {half_w} mm: conductors lying flat inside it on each side of the target:"
          f" {n_rib} at ribbon pitch, {n_xh} at 2.5 mm pitch")
print("-> any neighbour left in the anvil plane, in front of the tooling, is crushed. They have to leave the")
print("   plane (fold up or fold back) or the tooling has to be narrower than the conductor spacing.")

print()
print("Fold-back parking: split length needed so the clamp edge (fold line) stays in front of the tooling")
for Dt in (6.0, 8.0, 10.0, 12.0):     # conductor tip to tooling front face, mm [estimate: box 2 + barrels ~4 + tab/carrier/guide ~3-6]
    for c in (2.0, 3.0):              # clearance fold line to tooling face for the fork and bends [estimate]
        Ls = Dt + c
        print(f"  tip-to-tooling-face {Dt:>4.1f} mm, clearance {c:.0f} mm -> split length >= {Ls:.0f} mm")
print("  Bend over the clamp edge at radius 1.5-2.5 mm uses pi*R = "
      f"{pi*1.5:.1f}-{pi*2.5:.1f} mm of that length; the rest lies back on the cassette top.")

print()
print("Fan angle from ribbon pitch to housing pitch over the split length (for the final housing):")
for n in (3, 4, 5):
    worst = (n - 1) / 2 * (XH - RIB)
    for Ls in (12.0, 15.0, 20.0):
        print(f"  {n}P, split {Ls:.0f} mm: outer conductor moves {worst:.2f} mm -> {degrees(atan(worst/Ls)):.1f} deg")
for name, a, b, hsg in (("J1 5P+4P", 5, 4, 9), ("J4 4P+3P", 4, 3, 7), ("J7 5P+3P", 5, 3, 7), ("J2 3P+3P", 3, 3, 6)):
    span = (hsg - 1) * XH
    move = (span - (a + b - 1) * RIB) / 2
    print(f"  {name} into XHP-{hsg}: outermost moves {move:.2f} mm -> {degrees(atan(move/15.0)):.1f} deg over 15 mm")

# ------------------------------------------------------------------ 2
hr("2. Travelling crimp head between fanned conductors (idea b3)")
print("Plan view: the head's dies straddle the target; neighbours must clear the die plates.")
for W in (4.5, 6.0, 8.0, 10.0):      # die-set width across the wire at anvil level, mm [estimate]
    p_min = W / 2 + OD / 2 + 0.5     # half die + half conductor + 0.5 mm clearance
    for n in (4, 5):
        fan_w = (n - 1) * p_min
        move = (fan_w - (n - 1) * RIB) / 2
        print(f"  dies {W:>4.1f} mm wide -> fan pitch >= {p_min:.2f} mm; {n}P fan {fan_w:.1f} mm wide;"
              f" outer conductor moves {move:.1f} mm ({degrees(atan(move/20.0)):.0f} deg over 20 mm)")
print("SN-2549-style jaw plates run ~20-40 mm across the wire [estimate]: no fan clears them -> b3 needs")
print("narrow applicator-style blades (a few mm wide) or its own made dies.")

print()
print("Insertion by the same gantry: the housing visits each fanned contact in turn")
for p in (4.0, 5.0, 6.0):
    for n in (4, 5):
        drag = (n - 1) * (p - XH)
        print(f"  fan pitch {p:.0f} mm, {n}P: first-inserted conductor is dragged {drag:.1f} mm sideways by the last insertion"
              f" ({degrees(atan(drag/20.0)):.0f} deg over a 20 mm free length)")

# ------------------------------------------------------------------ 3
hr("3. Laser scoring from above and below (idea b4)")
R_o = OD / 2
R_i = BUNDLE / 2
print(f"conductor OD {OD} mm, bundle {BUNDLE} mm, wall {WALL:.2f} mm [facts]")
print("Model: vertical beam; removal along the beam scales with cos(incidence) [estimate];")
print("radial depth ~ d0*cos^2(phi), phi = angle of the surface normal from vertical.")
for frac in (0.6, 0.8, 0.95):
    d0 = frac * WALL
    # remaining ligament thickness around a half circumference, top scoring covers phi 0..90
    n = 900
    A_lig = 0.0
    thin = 0.0
    for i in range(n):
        phi = (i + 0.5) / n * (pi / 2)
        t = WALL - d0 * cos(phi) ** 2
        r_mid = R_i + t / 2
        A_lig += t * r_mid * (pi / 2) / n
    A_lig *= 4   # four quadrants (top two, bottom two)
    full = pi * (R_o**2 - R_i**2)
    for sig in (4.0, 8.0, 11.0):     # MPa silicone tensile [source: 4-11 general, 8-11 wire grade]
        pass
    print(f"  score depth at top/bottom {frac*100:.0f}% of wall: ligament area {A_lig:.2f} mm^2 of {full:.2f} mm^2 unscored;"
          f" tear-off by tension {A_lig*4:.1f}-{A_lig*11:.1f} N (4-11 MPa), unscored {full*4:.1f}-{full*11:.1f} N")
print("The thin ligament sits at the flanks (phi near 90 deg), where the beam grazes. Tilting the fixture")
print("+/-45 deg for two more passes scores the flanks too:")
for frac in (0.8,):
    d0 = frac * WALL
    n = 900
    A_lig = 0.0
    for i in range(n):
        phi = (i + 0.5) / n * (pi / 2)
        best = max(cos(phi) ** 2, cos(phi - pi / 4) ** 2)   # a vertical pass and a 45 deg pass cover each quadrant
        t = WALL - d0 * best
        A_lig += t * (R_i + t / 2) * (pi / 2) / n
    A_lig *= 4
    print(f"  with the extra 45 deg passes: ligament {A_lig:.2f} mm^2 -> {A_lig*4:.1f}-{A_lig*11:.1f} N")
print("Compare: a 22 AWG conductor breaks at ~85-100 N [facts]; the cassette clamps the insulation, so a")
print("slug pull of 5-15 N per conductor is carried by the clamp, not the strands.")

print()
print("Web slitting, per ribbon end:")
for n in (3, 4, 5):
    for Ls in (15.0, 20.0):
        length = (n - 1) * Ls
        for v, passes in ((10.0, 3),):
            t = length * passes / v
            print(f"  {n}P, split {Ls:.0f} mm: {n-1} webs x {Ls:.0f} mm = {length:.0f} mm of kerf;"
                  f" at {v:.0f} mm/s x {passes} passes ~{t:.0f} s [estimate speed/passes]")
