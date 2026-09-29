"""Borrowed-machines explorer, wave 2 (revise and new direction), 2026-09-28.

Run:  python3 wave2.py > wave2.out.txt

Sections
  1. b1: the feed conflict on a fast bought press. Why a compliant fork has no force window,
     and what the post-feed ram-borne finger and a pneumatic snatch need.
  2. b6: splitting by pins pierced at the root and pulled to the tip; the wire-harp branch;
     why a wire noose is not a self-limiting stripper.
  3. b7: stripping geometry on 1.7 mm silicone over 60 x 0.08 mm strands: V-blades, die-hole
     blades, a single rotary blade; ligament, tear-off force, twist.
  4. b8: a spool feed that rips the seams by retracting.
  5. Person minutes per unit, with procedure-is-the-machine's task library, for the wave-2 rows.

Labels: [facts] = context/xh-facts.md or the digest; [calc] = computed here; [estimate];
[assumption]; [procedure] = explorers/procedure-is-the-machine/calc (task library, feed window).
Every estimate is printed beside its result.
"""
from math import pi, sqrt, atan, degrees, radians, cos, sin

def hr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)

OD = 1.7                 # conductor OD, mm [facts]
RO = OD / 2
PITCH = 1.7              # ribbon pitch, mm [facts]
RB_LO, RB_HI = 0.345, 0.37   # strand bundle radius, mm (0.69-0.74 dia) [facts calc]
WALL_LO, WALL_HI = 0.43, 0.55   # insulation wall, mm [facts calc]
ECC = (WALL_HI - WALL_LO) / 2    # strand-bundle eccentricity in the jacket, mm [estimate from the wall range]
D_STRAND = 0.08          # mm [facts]
N_STRAND = 60            # [facts]
E_CU = 117e3             # MPa, copper [estimate, handbook]
EI_COND = 14.0           # N*mm^2, one conductor, strands dominate [ribbon-as-pallet calc, via digest]
SIG_SIL = (4.0, 11.0)    # MPa silicone tensile, general to wire grade [Primasil, RY via b4]
TEAR = (15.0, 25.0)      # N/mm silicone tear strength, wire grade [Primasil via b4]
BREAK_COND = (85.0, 100.0)   # N, 22 AWG conductor break [facts]

# ------------------------------------------------------------------------------------------ 1
hr("1. b1 on a fast bought press: the pre-feed arrives while the conductor is still held")

print("Plastic bending moment of 60 strands that slide on each other (each strand bends alone):")
for sy in (70.0, 100.0):       # MPa, annealed tinned strand; 70 MPa matches the digest's ~67 mm set radius
    Mp = N_STRAND * sy * D_STRAND ** 3 / 6.0     # N*mm
    row = ", ".join(f"L={L:>4.0f} mm -> {1000 * Mp / L:4.0f} mN" for L in (6, 8, 10, 15))
    print(f"  yield {sy:.0f} MPa: Mp = {Mp:.2f} N*mm; side force at the contact that sets the conductor: {row}")
print("  (L = lever from the fork/foot hold to the contact; silicone adds EI ~1-2 N*mm^2 elastically only)")

print()
print("Side loads the fork must resist during lay-in (elastic, conductor offset e at the barrel):")
for e in (0.1, 0.3, 0.5):
    for L in (4.0, 8.0):
        F = 3 * EI_COND * e / L ** 3
        print(f"  offset {e:.1f} mm over {L:.0f} mm: {1000 * F:5.0f} mN", end=";")
    print()
print("  plus friction under a presser foot at 0.5-2 N down, mu 0.5-1 on silicone: 250-2000 mN [estimate]")
print("-> a sprung or detented 'compliant fork' would need a breakaway above the lay-in loads (tens of mN,")
print("   hundreds with the foot down) and below the load that sets the conductor (24-85 mN). The window is")
print("   empty. The parts that hold the conductor must be OFF it before the feed moves, which on a fast")
print("   press means mounted on the ram (they lift with it) or a dwell (b1b).")

print()
print("Post-feed with a ram-borne finger (b1 repair):")
wing_top = 3.2 + 0.25          # open insulation wing height + drawing tolerance, mm [facts clone drawings]
margin = 0.3                   # clearance under the held conductor [estimate]
hc = wing_top + margin + RO    # conductor centre height above the barrel floor while waiting
seat_c = RO                    # conductor centre when seated in the insulation barrel
rise = hc - seat_c
print(f"  conductor waits with its centre {hc:.2f} mm above the barrel floor (wings {wing_top:.2f} + {margin} + OD/2)")
for L in (8.0, 10.0, 12.0, 15.0):
    print(f"  split {L:4.1f} mm: tip raised {rise:.2f} mm -> {degrees(atan(rise / L)):4.1f} deg at the root "
          f"(sets the copper; the finger bends it back)")
p_min = wing_top - OD          # finger protrusion below the insulation-forming face so the conductor is seated
print(f"  finger must protrude >= {p_min:.2f} mm below the insulation crimper's forming face, so the conductor")
print(f"  is seated (top at {OD:.1f} mm) before the crimper meets the wing tips ({wing_top:.2f} mm);")
print(f"  it first touches the waiting conductor when the forming face is ~{hc + RO + p_min:.1f} mm above the floor,")
print("  so the post-feed must have finished by then [assumption: post-feed completes early in the downstroke].")

print()
print("Pneumatic snatch inside the pre-feed window (alternative on the fast press):")
window = (50, 90)              # ms at a 0.5 s press cycle [procedure exchange_borrowed §2]
valve = (10, 20)               # ms, 24 V 5/2 solenoid valve response [estimate]
for v in (0.3, 0.6, 1.0):      # m/s piston speed, flow-limited [estimate]
    t_move = 7.0 / (v * 1000) * 1000 + 5    # ms, 7 mm plus ~5 ms to accelerate [estimate]
    print(f"  piston {v:.1f} m/s: 7 mm in ~{t_move:4.0f} ms + valve {valve[0]}-{valve[1]} ms = "
          f"{t_move + valve[0]:.0f}-{t_move + valve[1]:.0f} ms against a {window[0]}-{window[1]} ms window")
print("  trigger: a proximity switch on the ram at 4-6 mm up the upstroke. Tight; and the fork/foot must")
print("  already be off the conductor, so the snatch only helps if they ride the ram anyway.")

# ------------------------------------------------------------------------------------------ 2
hr("2. b6: pierce at the root, pull to the tip; the harp branch; the noose")

print("Seam position error from a centred datum (conductor pitch 1.7 +/-0.1 each, worst case) [facts]:")
for n in (3, 4, 5):
    seams = [(-(n - 2) / 2 + k) for k in range(n - 1)]     # seam index in pitches from centre
    worst = max(abs(s) for s in seams) * 0.1
    print(f"  {n}P: outer seam {max(abs(s) for s in seams) * PITCH:4.2f} mm from centre, error up to +/-{worst:.2f} mm"
          f"; a V-valley captures a point within +/-{PITCH / 2:.2f} mm")

print()
print("Rip force per seam (neck height h unmeasured; repo Open item 5):")
C_CUT = (1.0, 5.0)     # N/mm, cutting resistance of a sharp edge in filled silicone [estimate]
for h in (0.2, 0.4, 0.6):
    tear = (TEAR[0] * h, TEAR[1] * h)
    cut = (C_CUT[0] * h, C_CUT[1] * h)
    print(f"  neck {h:.1f} mm: round pin tears it {tear[0]:4.1f}-{tear[1]:4.1f} N; "
          f"pin with a trailing edge (seam-ripper crotch) cuts it {cut[0]:.1f}-{cut[1]:.1f} N")
print("  pierce, conical 0.4-0.6 mm pin through the neck: 0.5-3 N [estimate]")
print()
print("Pull on the ribbon to rip every seam of one end at once, round pins, neck 0.2-0.6 mm:")
for name, seams in (("3P", 2), ("4P", 3), ("5P", 4), ("5P+4P laid together (J1)", 7)):
    lo, hi = seams * TEAR[0] * 0.2, seams * TEAR[1] * 0.6
    print(f"  {name:26s} {seams} seams: {lo:5.1f}-{hi:5.1f} N  (conductors break at {BREAK_COND[0]:.0f}-"
          f"{BREAK_COND[1]:.0f} N each)")
print("  the tear runs only toward the tip, ahead of a pin that moves toward the tip, so the root is where")
print("  the pin went in: pin placement +/-0.05 mm plus ribbon slip in the clamp [estimate].")

print()
print("Harp branch: taut music wire at each seam, the square-cut end pushed through it:")
UTS_MW = 2300.0        # MPa, 0.2-0.3 mm music wire [estimate, typical ASTM A228]
for d in (0.20, 0.25, 0.30):
    A = pi * d ** 2 / 4
    for T in (20.0, 40.0):
        s = T / A
        L = 12.0       # mm span between upper and lower combs [estimate]
        F = 5.0        # N lateral cutting load per wire, mid of the range above [estimate]
        dx = F * L / (4 * T)
        ky = 4 * T / L
        print(f"  d {d:.2f} mm, T {T:3.0f} N: stress {s:5.0f} MPa ({100 * s / UTS_MW:3.0f} % of ~{UTS_MW:.0f}); "
              f"bows {dx:.2f} mm under 5 N; side stiffness {ky:.1f} N/mm")
print("  the harp pushes the end INTO the wires, so the ribbon is in compression between clamp and harp:")
for L in (5.0, 10.0, 15.0):
    EIr = 5 * EI_COND          # 5P, bending out of plane
    P = pi ** 2 * EIr / (0.7 * L) ** 2
    print(f"    5P free {L:4.1f} mm (fixed-pinned): buckles at ~{P:5.0f} N against 12-60 N of cutting")
print("  -> the harp needs guide combs over the free length; the pin-and-pull keeps the ribbon in tension.")
print()
print("How far a wedge opens the neck ahead of itself (double cantilever, both conductors EI 14 N*mm^2):")
for delta in (0.2, 0.5):               # opening = wire or tine diameter, mm
    for Gb in (0.4, 1.0, 4.0):         # N, tearing energy x neck height [estimate range]
        a = (9 * EI_COND * delta ** 2 / (4 * Gb)) ** 0.25
        print(f"  opening {delta:.1f} mm, G*h {Gb:3.1f} N: tear runs ~{a:.1f} mm ahead of the wedge", end="; ")
    print()
print("  -> a harp fed from the tip leaves the root ~0.6-2 mm beyond where the wires stop; stop short and let")
print("     the clamp be the tear stop. Pins pulled toward the tip never tear backward past where they went in.")

print()
print("Why a tightened wire noose is not a self-limiting stripper:")
Estar = 1 / ((1 - 0.09) / 210e3 + (1 - 0.11) / 117e3)   # MPa, steel on copper
for T in (2.0, 5.0):
    q = T / RB_HI                      # N/mm line load once the loop reaches the strands
    Fs = q * D_STRAND                  # N on each outer strand the loop crosses
    Rs = sqrt(0.10 * 0.04)             # mm, crossed cylinders 0.2 mm wire on 0.08 mm strand
    a = (3 * Fs * Rs / (4 * Estar)) ** (1 / 3)
    p = 3 * Fs / (2 * pi * a * a)
    q_out = T / RO
    print(f"  loop tension {T:.0f} N: {q_out:4.1f} N/mm at the jacket surface; at the strands {q:4.1f} N/mm, "
          f"{Fs:.2f} N per strand, Hertz peak ~{p:5.0f} MPa against copper yield ~70-100")
print("  -> the loop dents strands long before it stops by itself; it needs a stop like any blade.")

# ------------------------------------------------------------------------------------------ 3
hr("3. b7: stripping 1.7 mm silicone on 60 x 0.08 mm strands with borrowed blade geometries")

def ring_area(rcut, rb):
    return max(0.0, pi * (rcut ** 2 - rb ** 2))

print(f"Bundle radius {RB_LO}-{RB_HI} mm, jacket radius {RO} +/-0.05, bundle off-centre up to {ECC:.2f} mm [facts, estimate]")
print()
print("(a) Two opposed 90 deg V-blades closed to an inscribed radius ri: they cut deepest at four points")
print("    (ri) and shallowest at the V bottoms and crossings (ri*sqrt2):")
for ri in (0.42, 0.45, 0.50):
    deep = ri - RB_HI - ECC
    shallow = min(ri * sqrt(2), RO) - RB_LO + ECC
    # uncut area: integrate over the diamond, rigid jacket
    n = 3600
    A = 0.0
    for i in range(n):
        th = 2 * pi * i / n
        k = round((th - pi / 4) / (pi / 2))
        thk = pi / 4 + k * pi / 2
        r = min(ri / cos(th - thk), RO)
        A += 0.5 * (r * r - RB_HI ** 2) * (2 * pi / n)
    F = (A * SIG_SIL[0], A * SIG_SIL[1])
    print(f"  ri {ri:.2f}: ligament {deep:+.2f} mm (worst, deepest point) to {shallow:.2f} mm (corners); "
          f"ring left {A:.2f} mm^2 -> tear-off {F[0]:.1f}-{F[1]:.1f} N")
print("  a negative ligament is a nick. The corners leave up to ~0.3 mm of wall: the tear wanders there.")

print()
print("(b) Die-hole (two semicircle) blades of radius rd, centred by the jacket itself:")
for rd in (0.44, 0.47, 0.50):
    lo = rd - RB_HI - ECC
    hi = rd - RB_LO + ECC
    A = ring_area(rd, RB_HI)
    print(f"  rd {rd:.2f} (hole {2 * rd:.2f} mm): ligament {lo:+.2f} to {hi:.2f} mm all round; ring {A:.2f} mm^2 -> "
          f"tear-off {A * SIG_SIL[0]:.1f}-{A * SIG_SIL[1]:.1f} N")

print()
print("(c) One blade orbiting at radius rb about a guide bushing axis (RotaryStrip principle):")
for clr in (0.05, 0.10):              # conductor centring error in a 1.8-1.9 mm guide [estimate]
    for rbl in (0.47, 0.50):
        lo = rbl - RB_HI - ECC - clr
        print(f"  centring +/-{clr:.2f}, blade radius {rbl:.2f}: worst ligament {lo:+.2f} mm", end="; ")
    print()
print("  the RotaryStrip sets 'incision diameter' in 0.01 mm steps [mfr datasheet]; its radius centralizers")
print("  are the fix for centring. On a 0.49 mm wall the whole budget is ~0.12 mm of ligament.")

print()
print("(d) Twist while pulling: torque to shear a uniform ring ligament vs torque a blade grip can give:")
for t in (0.05, 0.10, 0.15):
    rm = RB_HI + t / 2
    for sig in SIG_SIL:
        tau = sig / sqrt(3)
        Tq = tau * 2 * pi * rm ** 2 * t      # N*mm
        print(f"  ligament {t:.2f}, silicone {sig:4.1f} MPa: shear torque {Tq:5.2f} N*mm", end="; ")
    print()
for N in (10.0, 30.0):
    print(f"  blades gripping the slug with {N:.0f} N at mu 0.5-1.0, radius ~0.5 mm: {N * 0.5 * 0.5:.1f}-"
          f"{N * 1.0 * 0.5:.1f} N*mm available")
print("  -> twisting tears the ligament around the ring at the cut instead of stretching the slug; the")
print("     conductor behind the cut must be held against turning (a V-clamp on the insulation).")

print()
print("(e) Far-end electrode as a blade-touch detector (Schleuniger SmartDetect idea, on DC):")
for Lm in (0.1, 0.6):
    R = 0.057 * Lm * 1000     # mOhm, 57 mOhm/m [ribbon-as-pallet calc via digest]
    print(f"  loom {Lm:.1f} m: conductor {R:.0f} mOhm; a strand touching an isolated blade reads ohms to tens of")
print("  ohms [estimate]; a 3.3 V input with a 10 k pull-up sees it in microseconds. Every nick attempt is logged.")

# ------------------------------------------------------------------------------------------ 4
hr("4. b8: the spool feed rips the seams by backing up")
for nip in (20.0, 40.0, 60.0):         # N, belt feed nip on the ribbon [estimate]
    for mu in (0.8, 1.5):              # silicone on a rubber belt [estimate]
        print(f"  nip {nip:3.0f} N, mu {mu:.1f}: traction {nip * mu * 2:5.0f} N (two belts)", end="; ")
    print()
print("  against 6-36 N to rip a 4P (3 seams, neck 0.2-0.6 mm) and 12-60 N for a 5P: the feed can pull it;")
print("  the encoder sees slip as a length error, and the pins' load cell sees the rip force.")
T4_ends, T4_crimps = 300, 1200
print(f"  T4 (4P into XHP-4) over the program: {T4_ends} ends, {T4_crimps} crimps [change-the-question c5]")

# ------------------------------------------------------------------------------------------ 5
hr("5. Person minutes per unit, procedure-is-the-machine's task library (compare rows, not absolutes)")
T = dict(cut=20, peel=40, strip=8, hand_crimp=15, insert=8, label=30)   # s [procedure person_timeline]
NC, NE, NH = 53, 14, 10
rows = []
today = NE * (T["cut"] + T["peel"]) + NC * (T["strip"] + T["hand_crimp"] + T["insert"]) + NH * T["label"]
rows.append(("today, by hand", today, "procedure's row, reproduced"))
# b1 as it now stands: cassette loading 20 s/end, prep station (pin rip + whole-end strip) 20 s/end of the
# person's time (dock, start, undock), fold-back lid 5 s/end, hand insertion
b1 = NE * (T["cut"] + 20 + 20 + 5) + NC * T["insert"] + NH * T["label"]
rows.append(("b1/b1b + b6 rip + whole-end strip + lid, hand insert", b1, "20+20+5 s per end [estimate]"))
b1i = NE * (T["cut"] + 20 + 20 + 5) + NH * (10 + T["label"])
rows.append(("  ... + b1's insertion extension (housing drop 10 s)", b1i, ""))
# b2b pedal-less station: person splits by hand (peel), pokes each conductor into the b7 strip nozzle (4 s),
# then into the crimp funnel (5 s), inserts contact k-1 while the machine crimps k (8 s)
cyc = 20.0
pres = 4 + 5
b2b = NE * (T["cut"] + T["peel"]) + NC * max(cyc, pres + T["insert"]) + NH * T["label"]
rows.append(("b2b pedal-less hand station, strip nozzle inline", b2b, "20 s machine cycle, person 9+8 s"))
b2b6 = NE * (T["cut"] + 25) + NC * max(cyc, pres + T["insert"]) + NH * T["label"]
rows.append(("  ... with a b6 pin-rip board by hand (25 s/end)", b2b6, ""))
# b8 spool line, T4 ends only; the rest of the unit by today's hand method
t4_c, t4_e, t4_h = 20, 5, 5
rest = (NE - t4_e) * (T["cut"] + T["peel"]) + (NC - t4_c) * (T["strip"] + T["hand_crimp"] + T["insert"]) \
    + (NH - t4_h) * T["label"]
line = 60.0     # s per unit: a 4P spool change (~5 min) every ~5.4 units, bins, housing tube [estimate]
b8 = rest + t4_h * (10 + T["label"]) + line
rows.append(("b8 spool line making T4 ends; other ends by hand", b8, "T4 = 20 crimps, 5 ends, 5 housings"))
for name, sec, note in rows:
    print(f"  {name:55s} {sec / 60:5.1f} min  {note}")
print("  The b8 row is the unit's hand work for the other 33 crimps plus ~1 min for the line: it removes the")
print("  T4 share only. A b8 that also takes J6 (5P) and the pairs is where the rest of the minutes go.")
