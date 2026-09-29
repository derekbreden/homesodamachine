"""Ribbon-as-pallet on force-and-form, wave 3: numbers for the exchange file
../../../exchange/ribbon-as-pallet--on--force-and-form-w3.md

jst-crimp-study, explorer ribbon-as-pallet, wave 3, 2026-09-28.
Run:  python3 exchange_on_force_and_form_w3.py > exchange_on_force_and_form_w3.out.txt

Labels: [source]/[mfr] as cited in ../../../context/xh-facts.md; [f&f ...] are
force-and-form's calc outputs; [calc X] is borrowed-machines'
exchange_ribbon_as_pallet.out.txt; [pg] and [W2] are this explorer's
pallet_geometry.out.txt and stations_wave2.out.txt. [estimate] and
[assumption] are mine. Nothing here was measured.
"""
from math import pi, sqrt, sin, cos, acos, atan, radians, degrees

def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)

RIB = 1.7          # [source S29] conductor pitch = OD, +/-0.1
R_W = RIB / 2
XH = 2.5           # [mfr S1] housing pitch
FLOOR = 0.20       # [source S19-S21] stock thickness

def s_bend(delta, R=5.0, th_deg=30.0):
    """a1's fan rule (two arcs R joined by a straight at theta): (axial, path)."""
    delta = abs(delta)
    if delta == 0:
        return 0.0, 0.0
    th = radians(th_deg)
    d_arc = 2 * R * (1 - cos(th))
    if delta <= d_arc:
        t = acos(1 - delta / (2 * R))
        return 2 * R * sin(t), 2 * R * t
    s = (delta - d_arc) / sin(th)
    return 2 * R * sin(th) + s * cos(th), 2 * R * th + s

def diag_slack(m, L):
    """lower bound: a straight diagonal of axial span L with lateral move m."""
    return sqrt(L * L + m * m) - L

# ---------------------------------------------------------------------------
hdr("1. Half-rows and the feed-length rule (f5b, f2c, f4's 'where it leads')")
print("Insertion stroke s from a crimped contact fully behind the rear face to latched:")
print("  s = pocket gap + contact length + seated inset of the contact's rear")
print("  contact length 5.8-6.73 (clone drawings), 6.1 / 6.5 (JST catalogs) [xh-facts s1];")
print("  seated inset 0.2-1.25 [into-the-housing estimate]; pocket gap 0-1 mm [estimate]")
s_lo = 0.0 + 5.8 + 0.2
s_hi = 1.0 + 6.73 + 1.25
s_jst = (0.0 + 6.1 + 0.2, 0.5 + 6.5 + 1.25)
print(f"  -> s = {s_lo:.1f}-{s_hi:.1f} mm (JST lengths: {s_jst[0]:.1f}-{s_jst[1]:.1f}); c1 uses ~7 mm")
print()
print("Slack a straight-laid half-row can give by straightening its spread 3.4 -> 5.0 mm")
print("(outer conductor of a centred row moves m = (n-1)/2 x 1.6 mm):")
print("  row | m mm | straight diagonal L=12 / 16 / 20 | a1 fan rule R5/30deg")
for n in (2, 3, 4, 5):
    m = (n - 1) / 2 * 1.6
    d = [diag_slack(m, L) for L in (12, 16, 20)]
    a, p = s_bend(m)
    print(f"   {n}  | {m:4.1f} | {d[0]:.3f} / {d[1]:.3f} / {d[2]:.3f} mm           | {p - a:.3f} mm")
print(f"  -> at most ~0.4 mm, against s = {s_lo:.0f}-{s_hi:.0f} mm.")
print()
print("Geometry of two equal-length half-rows from one clamped web:")
print("  final state: every contact latched at the same distance D from the web.")
print("  row B must start behind the rear face, i.e. at D - s, on a conductor of length D:")
print("  it needs s of stored feed whatever row A did. Row A needs s of stored feed")
print("  too, unless the web follows its push, and if the web follows, row B's contacts")
print("  are carried to D with it, which is inside the housing.")
print("Hump that stores s (parabolic arch, h = sqrt(3 c s / 8)) [into-the-housing s9]:")
for c in (10.0, 15.0, 20.0):
    print(f"  chord {c:4.1f} mm: s 6 -> h {sqrt(3*c*6/8):.1f} mm; s 7 -> h {sqrt(3*c*7/8):.1f} mm; s 8 -> h {sqrt(3*c*8/8):.1f} mm")
print()
print("Both half-rows spread about the ribbon's centre by 5.0/3.4 interleave at 2.5 mm:")
for n in (4, 5, 9):
    xs = [(i - (n - 1) / 2) * RIB for i in range(n)]
    odd = [x * 5.0 / 3.4 for i, x in enumerate(xs) if i % 2 == 0]
    even = [x * 5.0 / 3.4 for i, x in enumerate(xs) if i % 2 == 1]
    allx = sorted(odd + even)
    gaps = {round(b - a, 3) for a, b in zip(allx, allx[1:])}
    print(f"  {n} conductors: odd {['%.2f' % v for v in odd]}, even {['%.2f' % v for v in even]}; spacing {sorted(gaps)}")
print("-> a 1.7 -> 2.5 mm fan of the whole ribbon IS the two half-rows at 5.0 mm, already")
print("   interleaved at housing pitch. Crimped contacts fit side by side at 2.5 mm")
print("   (insulation crimp 1.8-2.05 wide leaves 0.45-0.7 mm) [a6], so one merged row and one")
print("   housing move (i3) insert both half-rows with zero stored feed.")

# ---------------------------------------------------------------------------
hdr("2. f5b: stripped before the spread, and a V-tooth comb against a root-captured fan")
print("c1/f5b strip flat while webbed, then spread 3.4 -> 5.0. The spread pulls outer tips")
print("back relative to inner ones by the slack above, so insulation edges stagger:")
for n in (2, 3, 4, 5):
    m = (n - 1) / 2 * 1.6
    lo = diag_slack(m, 20); hi = diag_slack(m, 12)
    a, p = s_bend(m)
    print(f"  row of {n}: insulation-edge stagger {lo:.2f}-{hi:.2f} mm (diagonal, L 20-12); {p-a:.2f} mm (R5/30 fan)")
print("  axial window for the conductor ~+/-0.2-0.3 mm [f&f placement_budget]")
print("-> rows of 2-3 are inside the window; J1's 5-row and the 4-rows spend 0.14-0.8 mm of")
print("   it before any lay error. Strip after the spread, at the comb face (a8 rolls a")
print("   whole half-row at any pitch), and the stagger is zero by construction.")
print()
print("Comb capture. A straight-descending V-tooth comb captures a conductor that moves")
print("less than half a slot (2.5 mm) minus lay error; margins +1.5/+0.7/-0.1/-0.9 mm for")
print("rows of 2/3/4/5 [ctq calc off s4].")
print("A grooved fan block pressed down from the root captures each conductor where it")
print("already lies (groove pitch = in-plane pitch 3.4 mm at the root) and the capture")
print("propagates toward the tip, so the move itself never limits capture. What limits it")
print("is the ribbon's own pitch stack at the root, from a centred datum [pg s1]:")
for nplane, nrib in ((3, 5), (5, 9)):
    worst = {5: 0.23, 9: 0.43}[nrib]
    print(f"  {nplane}-row plane out of a {nrib}-conductor end: worst stack {worst:.2f} mm "
          f"against a 1.70 mm half-pitch in the plane -> margin {1.70 - worst:.2f} mm")
print("-> rows of four and five lay without a tilted or rolling comb.")

# ---------------------------------------------------------------------------
hdr("3. K1: dock on strip, tack, cut, then press one at a time")
PS = (6.8, 7.1, 8.0, 9.5)   # strip pitch: Wurth analog 7.10 [mfr]; clones 6.8-9.5 [est]
print("Parted length to fan each ribbon alone to strip pitch ~7 mm [pg s2]: 3P 21, 4P 25, 5P 30 mm")
print()
print("Tack stroke on the strip (insulation barrels closed loosely, conductor barrels open):")
print("  per contact 33-132 N [ctq c1b: 66-660 N for 2-5 contacts]")
for n in (3, 4, 5):
    print(f"  {n}P: {33*n:.0f}-{132*n:.0f} N   (tab shear after it, same comb as pad: {50*n}-{160*n} N [calc X s5])")
MOUTH = 3.25   # notch mouth as wide as the open wings: 2.46-3.00 +0.25 [xh-facts s1; c1b's rule]
for p in PS:
    print(f"  tack-comb steel between notch mouths at pitch {p}: {p - MOUTH:.2f} mm (mouth {MOUTH} mm)")
print("  (c1b at 3.4 mm needs two passes at 6.8 mm for the same reason; at strip pitch one")
print("   pass does.) A loose tack's profile tolerance is a tenth or two, so a laser-cut")
print("   plate (+/-0.127 mm, SendCutSend [f&f f7]) serves; no EDM.")
print()
print("Seating the box against the nest's front stop after a vertical entry: the stage")
print("pushes the contact +Y through the straight overhang between fan-block face and barrel.")
for L in (9.0, 12.0):
    EIv = 14.9
    Pcr = pi**2 * EIv / L**2
    print(f"  overhang {L:.0f} mm: pinned-pinned Euler {Pcr:.1f} N (elastic, EI from [pg s4])")
print("  A box resting in a slot ~0.3 mm longer than itself slides at tenths of a newton")
print("  [estimate]: under the overhang's buckling load and under the tack's 0.4-9 N.")
print("  A vertical entry loads the tack across the jacket, where the wrapped wings hold it;")
print("  c1b's box-first push into a slot (0.1-0.5 N [c1b estimate]) loads it along the jacket,")
print("  where a loose tack may hold as little as 0.1-0.4 N [c1b; f&f wave2 s5].")
print()
print("Heavy station: tacked neighbours stand one strip pitch away. Neighbour half-width")
print("~1.1 mm (loosely closed insulation barrel 2.0-2.2 wide; open conductor wings")
print("1.68-1.90 [xh-facts s1]); 0.3 mm air [estimate]:")
for p in PS:
    hw = p - 1.1 - 0.3
    print(f"  pitch {p}: jaws, nest block and crimper holder <= {2*hw:.1f} mm wide where neighbours pass")
print("  (f4 needed <= ~6 mm at 5 mm pitch; f3's crimper is 3.5-4.4 mm [f&f gang s1])")
print()
print("Handing a tacked contact to a keyed nest: what the tack must resist")
EI = (14.9, 16.5)    # N mm^2 [pg s4]
MP = 0.36            # N mm plastic moment of the bundle [pg s4]
for L in (20.0, 30.0):
    for d in (0.3, 0.5):
        f_el = [3 * ei * d / L**3 for ei in EI]
        f_pl = MP / L
        f = min(max(f_el), f_pl)
        print(f"  free length {L:.0f} mm, contact moved {d} mm sideways by a chamfer: {f*1000:.0f} mN "
              f"(elastic {min(f_el)*1000:.1f}-{max(f_el)*1000:.1f}, plastic cap {f_pl*1000:.0f})")
G_CU, G_SI = 45000.0, 1.0     # MPa; silicone G ~ E/3, E 2.5-5.5 [f&f wave2 s5] -> ~1
J_strands = 60 * pi * 0.08**4 / 32
J_jacket = pi / 32 * (RIB**4 - 0.72**4)
GJ = G_CU * J_strands + G_SI * J_jacket
print(f"  torsion of the free conductor: strands free to slip {G_CU*J_strands:.1f} + jacket "
      f"{G_SI*J_jacket:.2f} = {GJ:.1f} N mm^2 [estimate]")
for L in (10.0, 20.0, 30.0):
    for th in (5, 10):
        T = GJ * radians(th) / L
        print(f"  square a contact rolled {th:2d} deg on {L:.0f} mm of free conductor: {T:.3f} N mm")
print("  tack grip: strands slip in the jacket at 0.4-9 N; torque 0.4-2.5 N mm [f&f wave2 s5; f9]")
print("-> the conductor bends and twists long before a tack slips: the nest locates the")
print("   contact, and 10 mm or more of free conductor makes any stage error harmless.")
print()
print("Contacts and time per unit")
ends = [(5, 0), (4, 0), (3, 0), (3, 1), (4, 0), (4, 0), (3, 0), (4, 0), (5, 0), (5, 0),
        (3, 1), (4, 0), (4, 0), (4, 0)]  # 14 ribbon ends; (conductors, trimmed)
assert len(ends) == 14
crimps = sum(n - t for n, t in ends)
spares = 2 * len(ends)
print(f"  {len(ends)} ribbon ends, {crimps} crimps; N+2 per end with trimmed positions snipped out:"
      f" {crimps + spares} contacts per unit")
for price, label in ((0.0235, "SXH reel"), (0.0471, "SXH 100-piece strip"), (0.0079, "CJT clone reel")):
    print(f"    at ${price:.4f} ({label}): ${price*(crimps+spares):.2f} per unit")
for tmin in (1.0, 2.0):
    print(f"  heavy station at {tmin:.0f} min per crimp: {crimps*tmin:.0f} min per unit, unattended")
person = 20 + 10 + 15 + 10   # s: strip segment, dock, tack+shear levers, move to heavy station
print(f"  person per ribbon end ~{person} s (strip 20, dock 10, levers 15, move 10) [estimate]:"
      f" {person*len(ends)/60:.0f} min per unit, plus pallet loading and insertion")

# ---------------------------------------------------------------------------
hdr("4. a2/a2e: a proof pull against the carrier bends the tab")
arm = FLOOR + R_W - FLOOR / 2
print(f"  wire axis {FLOOR + R_W:.2f} mm above the floor's underside; tab mid-plane {FLOOR/2:.2f}; arm {arm:.2f} mm")
for My in (2.40, 3.00, 3.47, 4.33):      # N mm, first yield [calc X s5]
    print(f"  tab first-yield moment {My:.2f} N mm -> the tab yields at a pull of {My/arm:.1f} N")
for lever in (3.0, 5.0):
    print(f"  hold-down pad {lever:.0f} mm ahead of the tab reacting a 20 N pull: {20*arm/lever:.1f} N")
print("-> pulled against the carrier with nothing on the barrels, every contact pitches")
print("   about its tab at 2.5-4.6 N, far short of 20 N. The shear comb's pad down on the")
print("   crimped barrels during the pull (4-6 N), or a blade on the box's rear face")
print("   (f&f f3: arm ~0, 25-100 MPa), fixes it.")

# ---------------------------------------------------------------------------
hdr("5. a2/a2e/a2b: the lance under a strip laid on a flat shelf, and a head from the box end")
for L in (5.8, 6.73):
    for tip in (2.24, 2.64):
        for proud in (0.6, 0.9):
            ang = degrees(atan(proud / (L - tip)))
            print(f"  length {L:.2f}, lance tip {tip:.2f} from front, {proud} proud: "
                  f"propped {ang:4.1f} deg about the tab")
kappa = 2 * 450 / (110000 * FLOOR)
print(f"  tab elastic bend at first yield over ~1 mm: {degrees(kappa*1.0):.1f} deg (sy 450, E 110 GPa)")
print("-> a carrier clamped flat on a flat shelf props every contact 7-16 deg on its lance:")
print("   the tab or the lance takes a set. The shelf, the support comb and the strip")
print("   pallet need a groove along X under the lance line, 2.2-2.7 mm behind the")
print("   contact front, >= 1.1 mm deep (c1 uses ~1.1 mm).")
print()
print("a2's head approaches from the box end with its lower die at floor level. The lance")
print("hangs across that path. The die can pass under it (>= 1 mm low) and rise behind")
print("its tip only if the conductor barrel starts behind the tip + 0.1 mm, i.e.")
for tip in (2.24, 2.44, 2.64):
    print(f"  lance tip {tip:.2f}: transition t >= {tip + 0.1 - 2.0:.2f} mm (box 2.0 mm) [f&f on_ith s1d]")
print("-> the same t that decides f8 decides a2's walking head.")

# ---------------------------------------------------------------------------
hdr("6. f6: which way bend-and-look can bend at the press")
for pin_d in (1.0, 2.0, 3.0):
    Ra = pin_d / 2 + R_W
    eps = R_W / Ra
    print(f"  pin diameter {pin_d:.0f} mm (radius {pin_d/2:.1f}): jacket surface strain +/-{eps:.2f}")
print("  (f&f wave2 s7 gives 0.46 / 0.30 / 0.22 for '1 / 2 / 3 mm pins': those are radii;")
print("   f6's 2 mm hardened dowel is a diameter, so its surface strain is 0.46, not 0.30)")
print("  The wing tips of a B/F insulation crimp sit on TOP of the crimp [f&f wave2 s5], so a")
print("  DOWN bend puts them on the outside (a cut gapes) and an UP bend on the inside (it closes).")
print("Room each direction needs right behind the insulation barrel, 2 mm pin:")
Ra = 1.0 + R_W
for th in (60, 90):
    side = Ra * (1 - cos(radians(th))) + R_W
    print(f"  {th} deg: the bent wire sweeps >= {side:.1f} mm to that side of its own axis")
for p in (3.4, 5.0, 7.1):
    print(f"  neighbour at {p} mm leaves a {p - RIB:.1f} mm gap between jackets")
print("  below: f3's strip track and carrier lie at floor level right behind the dies")
print("-> at f3/f6's press, with a fan of neighbours and the track behind, only UP is")
print("   free, and up puts the tip zone on the inside of the bend.")
print()
print("A row bent down at once over an edge by swinging the ribbon pallet about it (K7):")
for D in (9.0, 15.0):
    for th in (60, 90):
        print(f"  fan-block face {D:.0f} mm behind the edge, {th} deg: face moves {D*sin(radians(th)):.1f} down, "
              f"{D*(1-cos(radians(th))):.1f} toward the edge (a hinge on the edge line)")

# ---------------------------------------------------------------------------
hdr("7. Crimp width, target height and channel tolerance (f3, f7; KONNRA vs context)")
cases = [("JST SXA-01T 22 AWG analog [mfr S14]", 1.50, 0.80),
         ("context estimate for SXH on this ribbon [C1]", 1.50, 0.88),
         ("KONNRA KR2501 clone spec 22 AWG [source]", 1.75, 0.73)]
for name, w, h in cases:
    print(f"  {name:46s} W {w:.2f} x H {h:.2f} -> W*H {w*h:.2f} mm^2")
print("-> 1.20-1.32 mm^2 across all three: the clone's 0.73 and the context's 0.88 are the")
print("   same compaction in different widths, not a disagreement.")
for w in (1.54, 1.58, 1.63, 1.67):
    print(f"  channel {w:.2f} (f7 anvils): target H {1.20/w:.2f}-{1.32/w:.2f} mm; a 1.5 mm-channel "
          f"height copied unchanged over-compacts by {100*(1-1.5/w):.0f} %")
print()
for tol in (0.01, 0.05):
    print(f"  channel width +/-{tol} on 1.5 mm at a fixed height stop: compaction changes +/-{100*tol/1.5:.1f} %")
print("  J.S.T. UK publishes conductor crimp width +/-0.05 for SXA and SXH-002 [mfr S13, S14]")

# ---------------------------------------------------------------------------
hdr("8. f8: the 3.1 mm crimper beside a seated neighbour")
for od in (1.6, 1.7, 1.8):
    free = 2 * (XH - od / 2)
    side = (free - 3.1) / 2
    plays = [max(0.0, (op - od) / 2) for op in (1.95, 2.10)]
    print(f"  wire OD {od}: free {free:.2f} mm at the neighbour's equator, 3.1 crimper leaves {side:+.2f} a side;"
          f" wire play at a 1.95-2.10 rear opening {plays[0]:.2f}-{plays[1]:.2f} -> net {side-plays[1]:+.2f} to {side-plays[0]:+.2f}")
print("  (on_into_the_housing s2 takes the X offset off '0.2-0.45 mm' of clearance; s3's own")
print("   crimper leaves 0.05-0.15)")

# ---------------------------------------------------------------------------
hdr("9. f1: how far the fork bends the neighbours")
for h in (4.0, 6.0):
    for L in (20.0, 30.0):
        a = degrees(acos(1 - h / L))
        print(f"  neighbour tips held {h:.0f} mm above conductor i's over a {L:.0f} mm split: {a:.0f} deg out of line")
print("-> 29-46 deg, a set in the copper (yield below ~67 mm radius [pg s4]), not a gentle bend.")

# ---------------------------------------------------------------------------
hdr("10. a2e downstream: f8's crown drops crimped contacts below the tooling")
for p in (6.8, 7.1):
    for drop in (3.6, 4.0):
        R = p * p / (2 * drop)
        print(f"  strip pitch {p}, drop {drop} mm one pitch downstream: crown radius {R:.1f} mm, carrier strain {100*0.1/R:.1f} %")
for L in (15.0, 30.0):
    print(f"  a crimped contact dropped 4 mm on {L:.0f} mm of free conductor: S radius ~{L*L/16:.0f} mm "
          f"(copper sets below ~67 mm [pg s4]), so a small set remains for a6's clamp to take out")
