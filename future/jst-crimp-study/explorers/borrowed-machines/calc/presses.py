"""Borrowed-machines explorer: force sources for the XH crimp.

jst-crimp-study, wave 1, 2026-09-28. Run:  python3 presses.py > presses.out.txt

Every input carries a label:
  [facts]    ../../../context/xh-facts.md (itself [mfr]/[source]/[calc] labelled)
  [source]   a published page, named in the idea file that uses the number
  [estimate] my judgement
  [assumption]

What this answers:
  1. A slow crank (slider-crank) press driving a 30 mm-stroke mini-applicator:
     how much torque it needs, and what a wiper motor, a geared NEMA 23 or a
     worm gearmotor gives near bottom dead centre (BDC).
  2. How long the ram spends in the crimp zone at each speed, and so how many
     samples a cheap HX711 load-cell ADC gets (slowness buys force monitoring).
  3. Frame stretch of a small O-frame at crimp force, and what that does to
     crimp height repeatability.
  4. Ball screw with an over-travel spring, and air cylinders, as alternatives.
  5. A ratchet hand crimper closed by a linear actuator.
"""
from math import pi, sin, cos, sqrt, radians, degrees, asin

def hr(t):
    print()
    print("=" * 76)
    print(t)
    print("=" * 76)

# ---------------------------------------------------------------- inputs
F_PEAK_LO, F_PEAK_HI = 800.0, 2600.0   # N  [facts] peak total 0.8-2.6 kN
F_DESIGN = 3000.0                      # N  [facts] "design to 3 kN"
F_FORMING = 300.0                      # N  [facts] wing curling "tens to a few hundred N"
S_COMPACT = 0.20                       # mm [facts] compaction happens in last ~0.10-0.20 mm
S_FORM = 0.92                          # mm [facts] conductor punch travel from wing touch to BDC

def crimp_force(s):
    """Ram force needed at distance s (mm) above BDC, design case [estimate
    shape: flat forming force, then linear rise to the design peak at BDC]."""
    if s > S_FORM:
        return 0.0
    if s > S_COMPACT:
        return F_FORMING
    return F_FORMING + (F_DESIGN - F_FORMING) * (1 - s / S_COMPACT)

# ---------------------------------------------------------------- 1. crank
hr("1. Slider-crank press for a 30 mm-stroke mini-applicator")
r = 15.0     # mm crank radius -> 30 mm stroke [facts: mini-applicator 30 or 40 mm stroke]
L = 100.0    # mm connecting rod, centre to centre [estimate, a printable/steel flat bar]
eta = 0.85   # crank + rod + ram bushing efficiency [estimate]

def s_of(theta):
    """ram height above BDC (mm) at crank angle theta (rad) from BDC"""
    return r * (1 - cos(theta)) + L - sqrt(L**2 - (r * sin(theta))**2)

def dsdtheta(theta):
    return r * sin(theta) + (r**2 * sin(theta) * cos(theta)) / sqrt(L**2 - (r * sin(theta))**2)

def theta_of(s):
    lo, hi = 0.0, pi
    for _ in range(80):
        mid = (lo + hi) / 2
        if s_of(mid) < s:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

print(f"crank radius {r} mm, rod {L} mm, efficiency {eta}")
print(f"{'s above BDC (mm)':>18} {'crank angle (deg)':>18} {'ds/dtheta (mm/rad)':>20} {'F needed (N)':>13} {'torque needed (N*m)':>20}")
T_need_max = 0.0
for s in (0.92, 0.5, 0.3, 0.2, 0.15, 0.10, 0.05, 0.02, 0.005):
    th = theta_of(s)
    v = dsdtheta(th)
    F = crimp_force(s)
    T = F * v / 1000.0 / eta
    T_need_max = max(T_need_max, T)
    print(f"{s:>18.3f} {degrees(th):>18.2f} {v:>20.3f} {F:>13.0f} {T:>20.2f}")
# fine scan for the true maximum
T_scan = 0.0
s_at = None
N = 4000
for i in range(1, N):
    s = S_FORM * i / N
    th = theta_of(s)
    T = crimp_force(s) * dsdtheta(th) / 1000.0 / eta
    if T > T_scan:
        T_scan, s_at = T, s
print(f"-> max torque needed through the crimp (design 3 kN peak): {T_scan:.2f} N*m at s = {s_at:.3f} mm above BDC")
print("   (the crank's mechanical advantage rises toward BDC as fast as the crimp force does)")
# the applicator's own springs (ram return, feed finger, hold-down) load the whole stroke
print()
print("Applicator springs over the whole stroke (ram return + feed + hold-down), unmeasured [estimate 100-300 N]:")
T_spring = 0.0
for i in range(1, 181):
    th = radians(i)
    T_spring = max(T_spring, dsdtheta(th) / 1000.0 / eta)
for Fs in (100.0, 300.0):
    print(f"  {Fs:.0f} N spring load -> peak {Fs*T_spring:.2f} N*m near mid-stroke (ds/dtheta max {T_spring*eta*1000:.1f} mm/rad)")
T_scan = max(T_scan, 300.0 * T_spring)
print(f"-> size the drive for ~{T_scan:.1f} N*m: mid-stroke spring work, not the crimp, sets the torque")

hr("1b. What borrowed drives give at the crank")
drives = [
    # name, usable output torque N*m, output rpm, label
    ("12 V wiper motor, small car class (stall 12 N*m, use 1/2)", 6.0, 50, "[source] stall 12.3 N*m; half used [estimate]"),
    ("12/24 V industrial wiper gearmotor (AM Equipment 240, stall 40 N*m, use 1/2)", 20.0, 40, "[source] stall 40 N*m, 20-100 rpm"),
    ("12 V worm gearmotor, '70 kg*cm' class", 6.9, 10, "[estimate] common hobby worm motor rating"),
    ("NEMA 23 (1.2 N*m usable) + 10:1 planetary (eta 0.9)", 1.2 * 10 * 0.9, 6, "[estimate] Derek's NEMA23 + DM542T [repo]"),
    ("NEMA 23 (1.2 N*m usable) + 20:1 planetary (eta 0.9)", 1.2 * 20 * 0.9, 3, "[estimate]"),
]
for name, T, rpm, lab in drives:
    ok = "enough" if T >= T_scan else "SHORT"
    # force available at a few heights above BDC
    fs = []
    for s in (0.2, 0.1, 0.05):
        th = theta_of(s)
        fs.append(T * eta / (dsdtheta(th) / 1000.0))
    print(f"- {name}: {T:.1f} N*m ({ok} vs {T_scan:.1f} needed) {lab}")
    print(f"    ram force available at 0.20 / 0.10 / 0.05 mm above BDC: "
          + " / ".join(f"{f/1000:.1f} kN" for f in fs))
    t_rev = 60.0 / rpm
    th02 = theta_of(S_COMPACT)
    t_zone = th02 / (2 * pi) * t_rev
    print(f"    {rpm} rpm -> {t_rev:.1f} s per stroke; time in last 0.20 mm before BDC {t_zone*1000:.0f} ms;"
          f" HX711 samples there at 80 Hz: {t_zone*80:.1f}, at 10 Hz: {t_zone*10:.1f}")

print()
print("Slow-down needed for a real force curve from a $3 HX711 at 80 Hz (>= 20 samples in the last 0.2 mm):")
th02 = theta_of(S_COMPACT)
t_zone_needed = 20 / 80.0
t_rev_needed = t_zone_needed * 2 * pi / th02
print(f"  crank angle for last 0.2 mm = {degrees(th02):.2f} deg -> stroke period >= {t_rev_needed:.0f} s"
      f" ({60/t_rev_needed:.2f} rpm), or dwell the stepper through that arc")

# ---------------------------------------------------------------- 2. frame
hr("2. Frame stretch at crimp force (O-frame: two steel plates, four tie rods)")
E = 200e3  # N/mm^2 steel
for plate_t, span, width, rod_d, rod_L in ((12.7, 170, 100, 16, 250), (2 * 12.7, 170, 100, 16, 250), (12.7, 110, 100, 16, 220), (15, 150, 100, 16, 250), (20, 150, 120, 20, 250)):
    I = width * plate_t**3 / 12.0
    k_plate = 48 * E * I / span**3            # centre-loaded simply supported plate [estimate model]
    A_rod = pi * (rod_d / 2)**2
    k_rods = 4 * E * A_rod / rod_L
    k_other = 60e3                            # N/mm bearings, pins, bushing, applicator frame [estimate]
    k = 1 / (2 / k_plate + 1 / k_rods + 1 / k_other)
    d3 = F_DESIGN / k
    d_var = 0.15 * 2000.0 / k                  # +/-15 % scatter on a 2 kN crimp [estimate]
    print(f"plates {plate_t:g} mm x {width} wide over {span} span, 4 rods d{rod_d}: k_total ~{k/1000:.0f} kN/mm;"
          f" stretch at 3 kN {d3*1000:.0f} um; crimp-to-crimp scatter from +/-15% force: +/-{d_var*1000:.1f} um")
print("-> mean stretch is dialled out once on the applicator's crimp-height dial; the scatter sits inside")
print("   the +/-0.05 mm J.S.T. UK tolerance [facts], comfortably so from 15 mm plates up.")
print("   12.7 mm (0.500 in) is the thickest mild steel a quick laser-cut service offers [source SendCutSend];")
print("   shortening the span between rods is the cheap way to stiffen it (stiffness ~ 1/span^3), but the")
print("   rods must clear the applicator (a WERI mini-applicator is 155 x 150 x 110 mm [prior-art s3]), so")
print("   ~170 mm is the realistic span one way; the 25.4 mm row is two 12.7 mm plates bolted/bonded as one [estimate].")
print("   A printed frame would not hold it: PETG-CF E ~ 4-8 GPa [estimate], and it creeps under load")
for Ep in (4e3, 8e3):
    I = 100 * 30**3 / 12.0
    k_p = 48 * Ep * I / 150**3
    print(f"  printed 30 mm-thick plate, E={Ep/1000:.0f} GPa: k ~{k_p/1000:.1f} kN/mm -> {F_DESIGN/k_p*1000:.0f} um at 3 kN, creeps")

# ---------------------------------------------------------------- 3. ball screw + spring
hr("3. Alternatives: ball screw with an over-travel spring; air cylinders")
T23 = 1.2   # N*m usable NEMA23 at low speed [estimate]
for lead, belt, eta_s, name in ((5.0, 1.0, 0.9, "SFU1605 direct"), (5.0, 3.0, 0.85, "SFU1605 via 3:1 belt"),
                                (4.0, 5.0, 0.85, "SFU1204 via 5:1 belt")):
    F = 2 * pi * T23 * belt * eta_s / (lead / 1000.0)
    print(f"NEMA23 {T23} N*m, {name}: {F/1000:.1f} kN thrust at stall")
print("Over-travel spring: the nut drives the ram through a disc-spring stack preloaded above the crimp peak")
print("(>3 kN). The ram lands on a hard stop at shut height; the nut runs on ~0.3-0.5 mm into the stack and")
print("stops by step count. BDC is set by the stop, not by the screw [estimate, standard press practice].")
print()
for bore, bar in ((50, 6), (63, 7), (80, 7)):
    A = pi * (bore / 2)**2
    F = bar * 0.1 * A
    print(f"air cylinder {bore} mm bore at {bar} bar: {F/1000:.2f} kN direct; {3*F/1000:.1f} kN through a 3:1 lever"
          f"  (DeWalt 200 PSI compressor on hand [repo]; regulated to {bar} bar)")
print("-> a hard stop sets BDC; the cylinder only has to exceed the crimp peak plus the stop's share")

# ---------------------------------------------------------------- 4. hand tool
hr("4. Ratchet hand crimper closed by a linear actuator (idea b2)")
for MA in (8, 12, 20):   # handle-to-die ratio of a compound ratchet crimper [estimate; SN-2549 unmeasured]
    Fh_lo, Fh_hi = F_PEAK_LO / MA, F_PEAK_HI / MA
    print(f"MA {MA:>2}: handle force {Fh_lo:.0f}-{Fh_hi:.0f} N for a {F_PEAK_LO/1000:.1f}-{F_PEAK_HI/1000:.1f} kN crimp")
print("12 V linear actuator rated 1500 N, 50 mm stroke, 5.7 mm/s [source listing]: 6-19x margin over the")
print("handle force above; closing ~40 mm of handle travel takes ~7 s, opening ~7 s [estimate]")
print("NEMA17 (0.4 N*m) on a T8x2 lead screw, eta 0.3: "
      f"{2*pi*0.4*0.3/0.002:.0f} N -> enough only if MA >= {F_PEAK_HI/(2*pi*0.4*0.3/0.002):.0f}")

# ---------------------------------------------------------------- 5. travelling head (b3)
hr("5. Small crank inside a travelling crimp head (idea b3)")
r_h = 3.0     # mm crank radius -> 6 mm stroke: clears a 2.35 mm box when withdrawn [estimate]
L_h = 30.0    # mm link [estimate]
def s_h(th):
    return r_h * (1 - cos(th)) + L_h - sqrt(L_h**2 - (r_h * sin(th))**2)
def v_h(th):
    return r_h * sin(th) + (r_h**2 * sin(th) * cos(th)) / sqrt(L_h**2 - (r_h * sin(th))**2)
def th_h(s):
    lo, hi = 0.0, pi
    for _ in range(80):
        mid = (lo + hi) / 2
        if s_h(mid) < s:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
for name, T in (("NEMA17 0.4 N*m + 10:1 planetary (eta 0.9)", 0.4 * 10 * 0.9),
                ("NEMA17 0.4 N*m + 50:1 planetary (eta 0.8)", 0.4 * 50 * 0.8)):
    fs = []
    for s in (0.2, 0.1, 0.05):
        fs.append(T * 0.85 / (v_h(th_h(s)) / 1000.0))
    print(f"{name}: {T:.1f} N*m -> force at 0.20 / 0.10 / 0.05 mm above BDC: "
          + " / ".join(f"{f/1000:.1f} kN" for f in fs))
print("Head mass ~1 kg (NEMA17 0.3 + gearbox 0.2 + steel C-frame 0.3-0.6) [estimate]; the crimp force")
print("closes inside the C-frame, so the printer gantry carries only the head's weight.")
for k_c in (10e3, 20e3, 40e3):   # N/mm C-frame opening stiffness at the die [estimate]
    print(f"C-frame stiffness {k_c/1000:.0f} kN/mm: opens {F_DESIGN/k_c*1000:.0f} um at 3 kN; +/-15% force scatter -> "
          f"+/-{0.15*2000/k_c*1000:.0f} um")
