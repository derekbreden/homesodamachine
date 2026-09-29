"""Borrowed-machines explorer: numbers behind the settled idea files.

jst-crimp-study, 2026-09-28. Run:  python3 wave3.py > wave3.out.txt

Labels on inputs:
  [facts]  ../../../context/xh-facts.md
  [TS]     terminal-supply's calc/w3_on_borrowed.out.txt (numbers reused, cited there)
  [Prime]  ../../../sourcing/amazon-prime.md, observed 2026-09-28
  [estimate], [assumption]

Sections
  1. Slider-crank angles for ram heights, 30 mm and 40 mm strokes (b1b, b1c)
  2. b1c's order with the gate before the feed-finger band; cam pressure angle for
     a fork swing squeezed into 40 deg of shaft
  3. HX711 samples through compaction at 10/20/40 s per turn (b1b, b1c)
  4. Drive limits: the 10:1 NEMA 23 planetary at its 10 N*m permissible rating;
     what a stall at 4 kN needs from the rod stack (b1b, b1c)
  5. The reject turn: time between 'crimpers clear' and 'feed moves' (b1b, b1c)
  6. b2 / b2b closing drives from Prime rows: cycle time and handle force
  7. b8b (the flat spool line over a crown): split length the carrier zone needs,
     fronts in the housing, the spreading comb entered from the tip side, and the
     parting-pair alternative
  8. b8 / b8b / b6 whole-tip strip: pull per conductor at 50-60 % score depth, with
     silicone tensile 4-11 MPa (this explorer) and 8-11 MPa (digest)
"""
from math import pi, sin, cos, tan, atan, sqrt, radians, degrees, asin, hypot


def hr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def ram_height(theta_deg, r, L):
    """ram height above BDC (mm); theta measured from TDC (0) through BDC (180)"""
    ph = radians(180.0 - theta_deg)   # angle from BDC
    return r * (1 - cos(ph)) + L - sqrt(L * L - (r * sin(ph)) ** 2)


def angle_at_height(h, r, L, downstroke=True):
    """shaft angle from TDC where the ram is h mm above BDC; downstroke half (0-180) or upstroke (180-360)"""
    lo, hi = 0.0, 180.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if ram_height(mid, r, L) > h:
            lo = mid
        else:
            hi = mid
    a = (lo + hi) / 2
    return a if downstroke else 360.0 - a


def dsdtheta_from_bdc(phi, r, L):
    """ds/dphi (mm/rad) at angle phi (rad) from BDC"""
    return r * sin(phi) + (r * r * sin(phi) * cos(phi)) / sqrt(L * L - (r * sin(phi)) ** 2)


def phi_at_height(s, r, L):
    lo, hi = 0.0, pi
    for _ in range(80):
        mid = (lo + hi) / 2
        if (r * (1 - cos(mid)) + L - sqrt(L * L - (r * sin(mid)) ** 2)) < s:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ------------------------------------------------------------------------------------------ 0
hr("0. Which way the rod's obliquity term goes, for a crank ABOVE the ram (b1b, b1c)")
r0, L0 = 15.0, 100.0


def y_ram(phi):
    """crank centre at the origin, pin at angle phi from straight down, ram on the vertical axis below"""
    px, py = r0 * sin(phi), -r0 * cos(phi)
    return -py + sqrt(L0 * L0 - px * px)


for d in (40.0, 46.0, 90.0):
    s_vec = y_ram(0.0) - y_ram(radians(d))
    s_plus = r0 * (1 - cos(radians(d))) + (L0 - sqrt(L0 ** 2 - (r0 * sin(radians(d))) ** 2))
    s_minus = r0 * (1 - cos(radians(d))) - (L0 - sqrt(L0 ** 2 - (r0 * sin(radians(d))) ** 2))
    print(f"  {d:4.0f} deg from BDC: vector geometry {s_vec:6.3f} mm; '+' formula {s_plus:6.3f}; '-' formula {s_minus:6.3f}")
print("  -> with the crank above the ram (b1b's crank unit under the press's top beam), the ram's lowest")
print("     point is the rod's straight-in-line position and the obliquity term ADDS: 4 mm up at 40 deg from")
print("     BDC (220 deg from TDC). The '-' form (226 deg, 274-293 deg in terminal-supply's s6) is the")
print("     geometry of a crank below a ram it pulls down. This file uses the '+' form throughout.")

# ------------------------------------------------------------------------------------------ 1
hr("1. Slider-crank angles for ram heights (0 deg = TDC, 180 = BDC)")
print("  OTP mini-applicators for the Chinese 1.5-2 t presses: 30 mm stroke [source: Sanao, in b1];")
print("  JST CDS SXH001-06/CMKS-L: 40 mm stroke [facts s2]. Rod 100 mm [estimate].")
for stroke in (30.0, 40.0):
    r, L = stroke / 2, 100.0
    print(f"\n  stroke {stroke:.0f} mm (crank {r:.0f} mm, rod {L:.0f} mm)")
    for h, what in ((4.0, "crimpers clear the box (box 2.2-2.4 tall + margin) [TS s6]"),
                    (6.0, ""),
                    (15.0, "feed finger band, low end [b1b assumption, jack test measures it]"),
                    (20.0, "feed finger band, high end"),
                    (12.0, "ram 12 mm up: fork swing must be done above this [estimate]")):
        d = angle_at_height(h, r, L, True)
        u = angle_at_height(h, r, L, False)
        print(f"    ram {h:4.1f} mm above BDC: downstroke {d:6.1f} deg, upstroke {u:6.1f} deg   {what}")
    if stroke == 40.0:
        print("    (a 40 mm-stroke applicator's feed band is unmeasured; if it scales with stroke,"
              " 20-27 mm up)")

# ------------------------------------------------------------------------------------------ 2
hr("2. b1c: gate before the feed-finger band, and the squeezed fork swing")
r, L = 15.0, 100.0
band_lo = angle_at_height(20.0, r, L, True)
band_hi = angle_at_height(15.0, r, L, True)
print(f"  A cam-driven feed lever follows ram height [assumption, WERI-pattern]: on the downstroke the finger")
print(f"  retracts to the next hole between {band_lo:.1f} and {band_hi:.1f} deg (ram 20 -> 15 mm up).")
print(f"  Reversing the shaft through that band re-advances the strip [TS s6].")
for gate in (55.0, 60.0, 62.0):
    print(f"    gate at {gate:.0f} deg: ram {ram_height(gate, r, L):.1f} mm above BDC; margin to the band {band_lo - gate:.1f} deg")
print()
print("  Squeezed schedule: tines down 0-10, fork lays in 10-50, foot seats 50-58, gate 60.")
for a in (10.0, 50.0, 58.0, 60.0):
    print(f"    at {a:4.0f} deg the ram is {ram_height(a, r, L):5.1f} mm above BDC "
          f"(crimper faces {ram_height(a, r, L):.1f} mm over the barrel floor, wing tips at 3.2-3.45 mm)")
print()
print("  Face-cam pressure angle for the fork lever: lever throw 60 deg (3:1 sector -> 180 deg at the fork)")
print("  over 40 deg of shaft [estimate geometry]; follower arm length a; cam track radius R.")
for a_mm in (15.0, 20.0):
    for R in (30.0, 45.0, 60.0):
        for sector, throw in ((3.0, 60.0), (4.0, 45.0)):
            rise = a_mm * radians(throw)                   # follower arc travel
            run = R * radians(40.0)                         # cam track length over 40 deg
            # modified-sine motion: peak slope ~1.76 x mean [standard cam law]
            pa = degrees(atan(1.76 * rise / run))
            flag = "ok (<= 30 deg)" if pa <= 30 else ("tight (30-40)" if pa <= 40 else "too steep")
            print(f"    arm {a_mm:4.0f} mm, track R {R:4.0f} mm, sector {sector:.0f}:1 (lever {throw:.0f} deg): "
                  f"rise {rise:5.1f} mm over {run:5.1f} mm, peak pressure angle {pa:4.1f} deg  {flag}")
print("  -> squeezing the 180 deg fork swing into 40 deg of shaft needs a cam track of ~60 mm radius")
print("     with a 4:1 sector, or the swing driven by its own servo gated by a shaft switch (the fork")
print("     is light; only the ram and the feed must be tied to the shaft).")

# ------------------------------------------------------------------------------------------ 3
hr("3. HX711 samples through compaction (last 0.2 mm), 80 Hz")
for stroke in (30.0, 40.0):
    r = stroke / 2
    ph = phi_at_height(0.2, r, 100.0)
    for T in (10.0, 20.0, 40.0):
        t = (degrees(ph) / 360.0) * T
        print(f"  stroke {stroke:.0f} mm, {T:4.0f} s per turn: last 0.2 mm spans {degrees(ph):5.2f} deg = {t:5.2f} s -> {t*80:5.0f} samples")
print("  (p5's eccentric spans 22 deg of compaction [procedure cam_drive s4]; a 15 mm crank spans 8.7 deg)")

# ------------------------------------------------------------------------------------------ 4
hr("4. Drive limits at the crank")
eta = 0.85
print("  StepperOnline 10:1 NEMA 23 planetary [Prime]: 10 N*m permissible, 20 N*m momentary.")
for T_out, label in ((10.0, "10:1 held to its 10 N*m permissible rating (DM542T current set so)"),
                     (10.8, "10:1 at the 1.2 N*m motor torque this explorer assumed"),
                     (20.0, "10:1 at its 20 N*m momentary rating")):
    print(f"  {label}: {T_out:.1f} N*m at the crank")
    for s in (0.2, 0.1, 0.05):
        ph = phi_at_height(s, 15.0, 100.0)
        F = T_out * 1000.0 * eta / dsdtheta_from_bdc(ph, 15.0, 100.0)
        print(f"     ram force at {s:.2f} mm above BDC: {F/1000:5.2f} kN")
    # height above which a 4 kN obstruction stalls the drive
    lo, hi = 0.0, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        ph = phi_at_height(mid, 15.0, 100.0)
        if T_out * 1000 * eta / dsdtheta_from_bdc(ph, 15.0, 100.0) > 4000:
            lo = mid
        else:
            hi = mid
    print(f"     a 4 kN obstruction met above {lo:.3f} mm over BDC stalls the drive; below it the crank "
          f"pushes through, so the rod stack needs ~{lo:.2f} mm of travel past its preload")
print("  Crimp need: 3.8 N*m through a 3 kN design crimp; 5.4 N*m at mid-stroke for 300 N of")
print("  applicator springs [calc presses s1]. The permissible 10 N*m covers both.")
print("  Rod stack: two DIN 2093 A35.5 discs in series, ~4 kN preload, ~0.30 mm to ~5.2 kN [TS s7].")

# ------------------------------------------------------------------------------------------ 5
hr("5. The reject turn: blow-off window between 'crimpers clear' and 'feed moves'")
r, L = 15.0, 100.0
a_clear = angle_at_height(4.0, r, L, False)
a_feed = angle_at_height(15.0, r, L, False)
for T in (10.0, 40.0):
    print(f"  {T:.0f} s per turn: crimpers clear at {a_clear:.0f} deg, feed starts at ~{a_feed:.0f} deg: "
          f"{(a_feed - a_clear) / 360 * T:.2f} s, or any length if the shaft stops there")
m = 0.043e-3 * 9.81
print(f"  A crimped-empty contact weighs {m*1000:.2f} mN [facts: 0.043 g]. An air jet from a 1 mm nozzle at")
for p_bar in (1.0, 3.0):
    F = p_bar * 1e5 * pi * (0.5e-3) ** 2 * 0.5   # rough momentum flux ~ half of p*A [estimate]
    print(f"    {p_bar:.0f} bar gives ~{F*1000:.0f} mN at the nozzle [estimate: ~p*A/2]: {F/m:,.0f} x its weight")
print("  -> the jet has force to spare; what can stop it is a contact still gripped by the stripper plate or")
print("     wedged in the anvil nest [assumption]; the after-picture shows the anvil empty or not.")

# ------------------------------------------------------------------------------------------ 6
hr("6. b2 / b2b closing drives from Prime rows")
travel = 40.0       # mm of handle travel at the actuator's pin [estimate, b2]
for name, v, F, fb in (("Justech 1,500 N, 7 mm/s loaded, limit switches, no feedback [Prime]", 7.0, 1500.0, "AS5600 on the handle pivot [Prime] for 'captive'"),
                       ("Progressive Automations PA-01-POT 750 N, pot feedback [Prime]; speed not on the page", None, 750.0, "built-in pot"),
                       ("NEMA 17 + integrated Tr8x2 (Iverntech 42HD6039-05) [Prime], ~150-300 rpm under load [estimate]", 7.5, 330.0, "step count")):
    if v:
        t = travel / v
        print(f"  {name}:")
        print(f"     close or open {t:.1f} s over {travel:.0f} mm; thrust ~{F:.0f} N; position: {fb}")
    else:
        print(f"  {name}:")
        print(f"     thrust {F:.0f} N; position: {fb}")
print("  Handle need 40-325 N for a 0.8-2.6 kN crimp at a handle-to-die ratio of 8-20 [calc presses s4].")
print("  Spring link preload ~1.25 x the handle need: ~160 N at ratio 20, ~410 N at ratio 8 [b2].")
for F in (330.0, 750.0, 1500.0):
    for ratio in (8.0, 20.0):
        need = 2600.0 / ratio
        print(f"    drive {F:5.0f} N, ratio {ratio:4.0f}: need {need:5.0f} N, link preload {1.25*need:5.0f} N -> "
              f"{'carries the link' if F >= 1.25 * need else 'short of the link preload'}")
cyc_parts = {"close": 5.7, "open": 5.7, "feed + shear + place + captive": 8.0, "clamp, pull, flap": 3.0}
print(f"  b2b cycle with the Justech: ~{sum(cyc_parts.values()):.0f} s "
      f"({', '.join(f'{k} {v:.1f}' for k, v in cyc_parts.items())}) [estimates]; Derek's share ~17 s [b2b]")

# ------------------------------------------------------------------------------------------ 7
hr("7. b8b, the flat spool line over a crown (b8 x terminal-supply a2d)")
print("  Along the wire, from the strip line back toward the root [facts s1 clone drawings; estimates]:")
zone = [("rest of the window behind the insulation edge", 0.3, 0.5),
        ("insulation barrel", 0.8, 1.5),
        ("tab", 0.7, 1.15),
        ("carrier width [estimate: unmeasured; pilot holes 1.5 mm plus land]", 2.5, 4.0),
        ("clearance to the crown block's rear edge [estimate]", 1.0, 2.0)]
lo = sum(z[1] for z in zone)
hi = sum(z[2] for z in zone)
for z in zone:
    print(f"    {z[0]}: {z[1]:.2f}-{z[2]:.2f} mm")
print(f"  -> the carrier and crown occupy {lo:.1f}-{hi:.1f} mm behind the strip line.")
for comb in (4.0, 6.0):
    print(f"     With a {comb:.0f} mm spreading comb behind that, the split is at least {lo+comb:.1f}-{hi+comb:.1f} mm.")
print()
print("  Fronts in the housing when every contact sits the same along-conductor distance from the root")
print("  (strip line cut while the ribbon is flat) [straight-conductor model, as TS s2]:")
ends = {"4P": (4, None), "5P": (5, None), "J4 (4P+3P)": (7, None), "J1 (5P+4P)": (9, None)}
for Lf in (12.0, 15.0, 20.0):
    row = []
    for name, (n, _) in ends.items():
        dy = (n - 1) / 2 * (2.5 - 1.7)
        short = sqrt(Lf * Lf + dy * dy) - Lf
        row.append(f"{name} {short:.2f}")
    print(f"    free length {Lf:4.1f} mm: outermost front short by " + ", ".join(row) + " mm")
print("  (against a gang window of ~+/-0.3 mm [digest]; J1 needs ~20 mm of free length)")
print()
print("  Spreading comb entered from the tip side after the strip (tines pass between the stripped")
print("  bundles, 1.7 - 0.72 = ~1.0 mm apart, then wedge between the split, touching jackets):")
for n in (4, 5, 9):
    for p in (2.5, 2.8):
        out = (n - 1) / 2 * (p - 1.7)
        for fan in (2.5, 4.0):
            ang = degrees(atan(out / fan))
            print(f"    {n}P-wide end, p {p:.1f} mm: outermost moves {out:.2f} mm over a {fan:.1f} mm fan section: "
                  f"slot angle {ang:4.1f} deg")
print("  -> a fan section of 4 mm keeps a 4P or 5P under ~20 deg; J1 at 9 wide needs ~6 mm of fan or")
print("     two passes. The comb's parallel section at pitch p holds the conductors straight past it.")
print()
print("  Parting pair (alternative for the crimp only): two 0.25 mm blades drop into the valleys either")
print("  side of conductor k and move apart, each pushing its whole side out by D = p - 1.7:")
for p in (2.35, 2.5, 2.8):
    D = p - 1.7
    Mp = 0.51   # N*mm, plastic moment of 60 strands [calc wave2 s1, upper]
    for x in (6.0, 10.0):
        print(f"    p {p:.2f}: D {D:.2f} mm; pushed at {x:.0f} mm from the root, each conductor needs ~{Mp/x*1000:.0f} mN "
              f"to set at the root (plus silicone) [calc wave2 s1]")
print("  -> trivial forces; but the crimped contacts then lie at ~1.7-2.0 mm pitch, boxes 1.85-1.95 mm wide")
print("     [facts], so they crowd; the row needs spreading before a housing goes on. The comb avoids that.")
print()
print("  Supply at skip-2 for T4 (1,200 crimps over ~60 units): 2,400 strip contacts, 0.30 of an 8,000 reel;")
print("  1,200 loose contacts drop into the thinning cup, 61 % of the other looms' 1,980 crimps [TS s5].")

# ------------------------------------------------------------------------------------------ 8
hr("8. Whole-tip strip pull per conductor at the depth a fixed-stop blade can hold")
print("  Ligament area after crown scores at 60 % of the wall: 1.18 mm^2 of 1.86 unscored [calc geometry s3].")
for lab, lo_, hi_ in (("this explorer's 4-11 MPa (general silicone rubber)", 4.0, 11.0),
                      ("the digest's 8-11 MPa (wire grade)", 8.0, 11.0)):
    print(f"    {lab}: {1.18*lo_:.1f}-{1.18*hi_:.1f} N per conductor; 4P {4*1.18*lo_:.0f}-{4*1.18*hi_:.0f} N; "
          f"5P {5*1.18*lo_:.0f}-{5*1.18*hi_:.0f} N")
print("  Break of one 22 AWG conductor 85-100 N [facts]; the clamp carries the pull on the insulation.")
print("  Flat blades to a fixed stop at 70-80 % reach the strands in the worst case; 50-60 % keeps")
print("  +0.08 mm or more of ligament [TS s8].")
