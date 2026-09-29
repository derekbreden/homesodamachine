"""Ribbon-as-pallet, wave 2: numbers for the parting and stripping stations,
the fan's axial shortening, the lay-in tongue, the docked strip in a feedless
applicator, and the insulation crimp on silicone.

jst-crimp-study, explorer ribbon-as-pallet, wave 2, 2026-09-28.
Run:  python3 stations_wave2.py > stations_wave2.out.txt

Labels: [source]/[mfr] as cited in ../../../context/xh-facts.md and the idea
files; [estimate] and [assumption] are mine. Nothing here was measured.
"""
from math import pi, sqrt, sin, cos, acos, asin, atan, radians, degrees

def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)

RIB = 1.7            # [source] conductor pitch = conductor OD, +/-0.1
RC = RIB / 2         # outer radius of one conductor's jacket
R_BUNDLE = (0.345, 0.37)   # [calc C1] strand bundle radius (0.69-0.74 dia)
LOOSE = 0.04         # [assumption] an outer strand standing proud of the bundle
WALL = RC - 0.36     # ~0.49 nominal wall [calc C1]
XH = 2.5

SINGLE_RIBBONS = (3, 4, 5)

# ---------------------------------------------------------------------------
hdr("1. The web line: how much silicone lies between two bundles, and what a blade leaves")
gap = RIB - 2 * 0.36
print(f"pitch = OD = {RIB} mm, so neighbouring jackets meet at the valley plane (tangent circles,")
print(f"fused over some neck thickness t_n that BNTECHGO does not state).")
print(f"silicone along the mid-plane between two bundle surfaces: {gap:.2f} mm "
      f"({gap/2:.2f} mm each side of the valley plane)")
print()
print("A slitting blade of thickness t_b centred delta off the valley plane leaves, on the")
print("near conductor's flank at the equator, wall = 0.49 - (|delta| + t_b/2); it reaches the")
print(f"outermost strand when that wall falls below the loose-strand allowance ({LOOSE} mm).")
for tb, name in ((0.10, "double-edge razor, 0.10 mm"), (0.23, "single-edge razor, 0.23 mm")):
    print(f"  {name}:")
    for d in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
        wall = WALL - (d + tb / 2)
        tag = "strands touched" if wall <= LOOSE else ("jacket thin" if wall < 0.25 else "")
        print(f"    offset {d:.2f} mm -> near flank wall {max(wall,0):.2f} mm  {tag}")
    lim = WALL - LOOSE - tb / 2
    print(f"    offset at which the blade reaches strands: {lim:.2f} mm; "
          f"keeps >=0.25 mm wall up to {WALL - 0.25 - tb/2:.2f} mm")
print()
# where a blade's lateral error comes from
worst_ctr_5 = (4 * 0.1 + 0.05) / 2     # wave-1 calc section 1
rss_ctr_5 = sqrt(4.25) * 0.1 / sqrt(3) / sqrt(2)
stack = 0.02 * 2                          # [estimate] spacer error, two blades out from centre
chan = 0.05                               # [estimate] channel registration
print("Lateral error budget for a FIXED gang slitter on a 5P (centred datum):")
print(f"  ribbon pitch stack worst {worst_ctr_5:.2f} / RSS {rss_ctr_5:.2f}; blade-stack spacers "
      f"+/-{stack:.2f}; channel +/-{chan:.2f}")
print(f"  -> worst {worst_ctr_5 + stack + chan:.2f} mm, RSS {sqrt(rss_ctr_5**2 + (stack/sqrt(3))**2 + (chan/sqrt(3))**2):.2f} mm")
print("Lateral error for a FLOATING plough (each blade on a flexure, V-nose riding its own")
print("valley) [estimate]: valley-finding +/-0.05, nose-to-blade +/-0.02 -> +/-0.07 mm,")
print("independent of the ribbon's pitch stack.")
print("-> a 0.10 mm blade floating on its valley keeps >=0.25 mm of flank wall; a fixed 0.23 mm")
print("   gang on a 5P can reach within 0.1 mm of the strands at worst case.")

# ---------------------------------------------------------------------------
hdr("2. Tearing the web: force, which path the tear takes, the wedge tines")
print("Peel of one web (trouser-type tear): F ~ T x t_n, T = tear strength")
print("[source: Primasil, wire grades 15-25 N/mm; general grades ~10 N/mm]")
for tn in (0.15, 0.25, 0.35, 0.5, 0.7):
    lo, hi = 10 * tn, 25 * tn
    print(f"  neck t_n {tn:.2f} mm: {lo:4.1f}-{hi:4.1f} N per web; 4 webs of a 5P at once "
          f"{4*lo:5.1f}-{4*hi:5.1f} N")
print()
print("Which path the tear takes [estimate, energy argument]: a tear running along the neck")
print(f"cuts t_n of silicone per mm of advance. A tear that leaves the neck and runs along a")
print(f"jacket must cut the jacket wall (~{WALL:.2f} mm) instead, and a tear that reaches the")
print("strands then runs along the silicone-copper interface, which has almost no bond.")
print("The neck is the cheaper path while t_n is well under the wall:")
for tn in (0.15, 0.25, 0.35, 0.49, 0.7):
    r = tn / WALL
    verdict = ("zips (neck much cheaper)" if r < 0.6 else
               "marginal: the tear may wander" if r < 1.0 else
               "wanders into a jacket: cut, don't tear")
    print(f"  t_n {tn:.2f} mm: t_n / wall = {r:.2f}  -> {verdict}")
print("-> one cross-section photograph of the ribbon (fresh blade cut, ELP camera) that shows")
print("   t_n decides between tearing (a7) and cutting (a7b).")
print()
# tine buckling
E = 200000.0   # N/mm^2 steel
for t, h, L in ((0.2, 1.5, 10.0), (0.3, 1.5, 10.0), (0.2, 1.5, 5.0)):
    I = h * t ** 3 / 12
    p_free = pi ** 2 * E * I / (2 * L) ** 2      # fixed-free
    k_lo, k_hi = 2.0, 6.0                           # N/mm per mm, silicone either side [estimate]
    p_sup_lo, p_sup_hi = 2 * sqrt(k_lo * E * I), 2 * sqrt(k_hi * E * I)
    print(f"tine {t} x {h} mm, {L:.0f} mm long: buckles at {p_free:.1f} N unsupported; "
          f"{p_sup_lo:.0f}-{p_sup_hi:.0f} N when the silicone on both sides supports it")
print("-> a 0.2 mm tine pushed into a web tear (2-15 N) needs the conductors' support,")
print("   which it has while it is inside the split; the free length ahead of the ribbon")
print("   must stay short (<5 mm) or the tine is thicker there.")
print()
print("Tines that part and fan to housing pitch: tine noses at 1.7 mm pitch, roots at 2.5 mm,")
print("so tine j (counted from the centre valley) diverges j x 0.8 mm over its length:")
for Lt in (15.0, 20.0):
    for j in (0.5, 1.5, 2.5):
        a = degrees(atan(j * (XH - RIB) / Lt))
        print(f"  tine length {Lt:.0f} mm, tine {j:.1f} pitches out: {j*(XH-RIB):.1f} mm over {Lt:.0f} mm = {a:.1f} deg")
print("-> for single ribbons (<=5 conductors) the tines splay <=8 deg; the comb that parts is")
print("   also a housing-pitch fan.")

# ---------------------------------------------------------------------------
hdr("3. The fan shortens the outer conductors: flush cut and strip AFTER fanning")

def s_bend(delta, R=5.0, th_deg=30.0):
    """Two arcs R plus a straight at theta (a1's wave-1 fan rule).
    Returns (axial length, path length)."""
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

def offsets(n, pitch):
    return [(i - (n - 1) / 2) * (pitch - RIB) for i in range(n)]

print("A conductor anchored at the split root follows its groove; the groove's path is")
print("longer than its axial span, so the tip recedes by (path - axial). Centred datum,")
print("R 5 mm, 30 deg, each ribbon fanned alone:")
print(f"{'pitch':>6} | " + " | ".join(f"{n}P outer recedes" for n in SINGLE_RIBBONS))
for pitch in (2.5, 4.0, 5.0, 7.1):
    cells = []
    for n in SINGLE_RIBBONS:
        offs = offsets(n, pitch)
        ax_max = max(s_bend(o)[0] for o in offs)
        rec = []
        for o in offs:
            a, p = s_bend(o)
            # every groove spans the same axial length ax_max: straight run for the rest
            rec.append(p - a)
        cells.append(f"{max(rec):14.2f} mm")
    print(f"{pitch:6.1f} | " + " | ".join(cells))
print("-> at 5 mm crimp pitch a 5P's outer tips sit ~1.6 mm behind the centre tip; at 7.1 mm")
print("   strip pitch ~2.7 mm. A flush cut before the fan with the strip after it gives unequal")
print("   stripped lengths; cutting and stripping both before the fan gives equal stubs whose")
print("   insulation edges are staggered by the same amount. Order: part, fan, then flush-cut")
print("   at the fan block face and strip, all referenced to the fan block.")
print()
print("Closing from crimp pitch back to 2.5 mm reverses it: the outer contacts advance")
print("relative to the inner ones by the difference in recession:")
for pitch in (5.0, 7.1):
    for n in SINGLE_RIBBONS:
        offs_c = offsets(n, pitch)
        offs_h = offsets(n, XH)
        adv = max((s_bend(oc)[1] - s_bend(oc)[0]) - (s_bend(oh)[1] - s_bend(oh)[0])
                  for oc, oh in zip(offs_c, offs_h))
        print(f"  {n}P from {pitch} mm to 2.5 mm: outer contact leads by ~{adv:.2f} mm "
              f"(taken up as bow if the insertion clamp sets the fronts)")

# ---------------------------------------------------------------------------
hdr("4. Ring score: blade radius budget, score depth, ligament, tear-off force")
print("Blade tip radius r_s must clear the outermost strand with margin:")
print("  r_s >= r_bundle + loose strand + eccentricity + centring error + setting error + margin")
print("  (centring error: 0.02 for two blades closing together, 0.05 for the axis height of a")
print("   conductor rolled on a flat bed with OD 1.7 +/-0.1, 0.125 for one blade in a 1.85 bore)")
cases = [
    ("twin blades, self-centring, e 0.05", 0.37, LOOSE, 0.05, 0.02, 0.02, 0.05),
    ("twin blades, self-centring, e 0.10", 0.37, LOOSE, 0.10, 0.02, 0.02, 0.05),
    ("rolled under fixed blades, e 0.05", 0.37, LOOSE, 0.05, 0.05, 0.02, 0.05),
    ("rolled under fixed blades, e 0.10", 0.37, LOOSE, 0.10, 0.05, 0.02, 0.05),
    ("one blade in a 1.85 bore, e 0.05", 0.37, LOOSE, 0.05, 0.125, 0.02, 0.05),
    ("one blade in a 1.85 bore, e 0.10", 0.37, LOOSE, 0.10, 0.125, 0.02, 0.05),
]
for name, rb, ls, e, c, s, m in cases:
    rs = rb + ls + e + c + s + m
    depth = RC - rs
    lig = rs - 0.36
    area = pi * (rs ** 2 - 0.36 ** 2)
    f_lo, f_hi = area * 8 * 0.5, area * 11
    print(f"  {name:36s}: r_s {rs:.2f} mm, score depth {depth:.2f} of {WALL:.2f} wall "
          f"({depth/WALL*100:.0f} %), ligament {lig:.2f} mm, tear-off {f_lo:.1f}-{f_hi:.1f} N")
print("  (tear-off = ligament ring area x 8-11 MPa, lower bound halved for the notch)")
print("-> two opposed blades that close together centre the conductor and roughly double the")
print("   usable score depth over a single blade in a bore. Tear-off stays at 3-15 N per")
print("   conductor, a few tens of N for a whole 5P pulled one after another.")
print()
# cutting torque
for Gc in (0.1, 1.0):   # N/mm, blade-assisted cutting energy [estimate]
    for d in (0.2, 0.3):
        F = Gc * d * 2   # two blades
        T = F * 0.6
        print(f"  cutting energy {Gc} N/mm, depth {d} mm: {F:.2f} N at the blades, "
              f"{T:.2f} N*mm at the spindle")
print("-> an N20 gearmotor (tens of N*mm) turns it with room; the conductor, held 10-20 mm")
print("   back, twists a few degrees at most.")
print()
print("Twist after a partial pull (RotaryStrip's 'controlled twisting'):")
for L_free, turns in ((2.4, 0.25), (2.4, 0.5)):
    ang = turns * 360
    lay = L_free / turns
    print(f"  {turns} turn over the {L_free} mm stub: lay length {lay:.1f} mm; outer strand "
          f"angle {degrees(atan(2*pi*0.36/lay)):.0f} deg")

# ---------------------------------------------------------------------------
hdr("5. Whole-end crown score while webbed (flat blades top and bottom)")
for d in (0.20, 0.25, 0.30, 0.35):
    th = degrees(acos((RC - d) / RC))
    uncut = 360 - 4 * th
    margin_lo = WALL - d - 0.10 - LOOSE
    margin_hi = WALL - d - 0.0 - LOOSE
    print(f"  each blade {d:.2f} mm deep: cuts +/-{th:.0f} deg of each crown; {uncut:.0f} deg of "
          f"360 left for the flanks to tear; strand margin {margin_lo:.2f}-{margin_hi:.2f} mm (e 0.10-0)")
print("-> flat blades need no pitch match, but leave ~45 % of each circumference (the flanks")
print("   and the web) to tear. The flank tear quality is the unknown this branch rests on.")

# ---------------------------------------------------------------------------
hdr("6. Touch-off: the flush-cut copper face as a switch")
for L in (5.0, 9.0, 15.0):
    EI = 14.9
    Pcr = pi ** 2 * EI / (2 * L) ** 2     # fixed-free, conservative
    print(f"  free conductor {L:.0f} mm: buckles (fixed-free) at {Pcr:.2f} N")
print("  (a floor: inside the scorer's bore the tip is guided laterally, so it cannot take")
print("   the free buckling shape; the bore raises the limit several-fold)")
print("  touch force needed to read continuity through tinned strand ends on steel:")
print("  ~0.05-0.2 N [assumption]; the stage stops at the first reading.")
print("  stage resolution: Tr8x2 lead screw, 200 steps x 16 microsteps: "
      f"{2/3200*1000:.2f} um per microstep; repeatability ~0.01 mm [estimate]")
print("-> each conductor's tip is located to ~0.01-0.05 mm (cut-face squareness dominates),")
print("   so the score lands 2.4 mm (or the clone's 1.6-2.1) behind every tip individually.")

# ---------------------------------------------------------------------------
hdr("7. a1: the lay-in drop, done by a pallet-borne tongue")
for h in (5.0, 6.3):
    for Lt in (10.0, 12.0, 15.0):
        ang = degrees(asin(h / Lt))
        print(f"  drop {h} mm with a tongue {Lt:.0f} mm long: tongue angle {ang:.0f} deg; "
              f"overhang ahead of the fixed block {Lt + 9:.0f} mm (tongue + 9 mm tip)")
print("-> any 5-6 mm drop costs ~10-15 mm of extra parted length whether a tongue, a moved-back")
print("   block (borrowed-machines' Repair A) or a ram sole makes it. The tongue applies the")
print("   levelling moment at its front lip and lifts the crimped conductor back as it springs")
print("   up, so no separate ramp is needed.")

# ---------------------------------------------------------------------------
hdr("8. a2e: docked strip through a feedless applicator, time and travel")
for n, name in ((3, "3P"), (4, "4P"), (5, "5P")):
    for ps in (6.8, 7.1):
        travel = (n - 1) * ps
        t_dock, t_idx, t_cam, t_crank, t_pull, t_shear = 15, 3, 2, 10, 15, 20
        total = t_dock + n * (t_idx + t_cam + t_crank) + t_pull + t_shear
        print(f"  {name} at strip pitch {ps}: {travel:4.1f} mm of X travel downstream; "
              f"~{total/60:.1f} min per ribbon end [estimate]")
per_unit_ends = 14
print(f"  a unit's 14 ribbon ends: ~{14*1.4:.0f}-{14*2.0:.0f} min of machine time; person time is "
      "strip snipping (~20 s) plus pallet loading per end")

# ---------------------------------------------------------------------------
hdr("9. The insulation barrel on 1.7 mm silicone (clone crimp figures)")
t_stock = 0.20
for H, W in ((1.70, 1.90), (1.80, 2.05), (1.90, 2.05)):
    inner = pi / 4 * (H - 2 * t_stock) * (W - 2 * t_stock)
    for od in (1.6, 1.7, 1.8):
        cond = pi * (od / 2) ** 2
        sil = cond - pi * 0.36 ** 2
        sil_in = inner - pi * 0.36 ** 2
        print(f"  crimp {H:.2f} x {W:.2f} (inside ~{inner:.2f} mm2), OD {od}: silicone "
              f"{sil:.2f} -> {max(sil_in,0):.2f} mm2 ({max(sil_in,0)/sil*100:.0f} %)")
print("-> KONNRA's 1.80 x 2.05 insulation crimp [source, clone spec] squeezes this ribbon's")
print("   jacket to ~70-80 % of its area. Silicone is nearly incompressible, so the rest flows")
print("   out of both ends of the barrel as a bulge, and the wing tips bite into it. A bulge at")
print("   the barrel's front edge is the thing to look for in the camera frame: it can push")
print("   silicone into the window between the barrels.")
