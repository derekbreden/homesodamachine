"""Ribbon-as-pallet numbers: fan geometry, crimp-pitch clearance, pitch tolerance,
conductor mechanics, parting and stripping forces, gang forces, time budget.

jst-crimp-study, explorer ribbon-as-pallet, wave 1, 2026-09-28.
Run:  python3 pallet_geometry.py > pallet_geometry.out.txt

Labels: [source]/[mfr] are cited in ../../../context/xh-facts.md or in the idea
files; [estimate] and [assumption] are mine. Nothing here was measured.
"""
from math import pi, sqrt, sin, cos, radians, degrees, exp, asin

def hdr(t):
    print()
    print("=" * 76)
    print(t)
    print("=" * 76)

RIB = 1.7          # [source] BNTECHGO: 1.7 mm per conductor, +/-0.1
RIB_TOL = 0.1      # [source] per conductor
XH = 2.5           # [mfr] XH pitch

# Looms: (name, ribbons in order across the housing, housing ways, trimmed conductor index 1-based or None)
LOOMS = [
    ("J1 MANIFOLD A", (5, 4), 9, None),
    ("J2 MANIFOLD B", (3, 3), 6, 3),     # contact 3 empty, conductor 3 trimmed [repo]
    ("J3 FAUCET",     (4,),   4, None),
    ("J4 SENSORS",    (4, 3), 7, None),
    ("J5 RELAYS",     (4,),   4, None),
    ("J6 REEDS A",    (5,),   5, None),
    ("J7 REEDS B",    (5, 3), 7, 8),     # one 3P conductor trimmed; which one is [assumption]: the outer
    ("J9 DISPLAY",    (4,),   4, None),
    ("J11 GAS",       (4,),   4, None),
    ("J13 PUMPS",     (4,),   4, None),
]

# ---------------------------------------------------------------------------
hdr("1. Ribbon pitch tolerance vs comb capture")
# If each conductor's width is 1.7 +/- 0.1 independently (the listing's tolerance
# read as per-conductor), a conductor k places from a datum edge accumulate.
# Worst case: linear sum. Likely: RSS of uniform errors (sigma = tol/sqrt(3)).
print("capture limit for a comb slot with a lead-in: half a ribbon pitch = "
      f"{RIB/2:.2f} mm before a conductor can fall into the wrong slot")
for n in (3, 4, 5, 7, 8, 9):
    # datum at one edge: conductor k centre error ~ sum of (k-1) full widths + half its own
    worst_edge = (n - 1) * RIB_TOL + RIB_TOL / 2
    rss_edge = sqrt((n - 1) + 0.25) * RIB_TOL / sqrt(3)
    # datum at the centre line (channel squeezes symmetric): half the stack
    worst_ctr = worst_edge / 2
    rss_ctr = rss_edge / sqrt(2)
    print(f"{n} conductors: far conductor error from EDGE datum worst {worst_edge:.2f} / "
          f"RSS {rss_edge:.2f} mm;  from CENTRE datum worst {worst_ctr:.2f} / RSS {rss_ctr:.2f} mm")
print("-> even the worst-case 9-conductor stack from one edge (0.85 mm) sits at the capture")
print("   limit; from a centred datum, or with a channel slightly narrower than nominal")
print("   (the AMP US 4,230,008 trick), every conductor is inside a comb slot's lead-in.")
print("   The ribbon's own pitch is good enough to be the reference at the clamp; the comb")
print("   takes over at the tip.")

# ---------------------------------------------------------------------------
hdr("2. Fan geometry: lateral move per conductor and the parted length it needs")

def offsets(ribbons, pitch, trimmed=None):
    n = sum(ribbons)
    rib_pos = [(i - (n - 1) / 2) * RIB for i in range(n)]
    tgt = [(i - (n - 1) / 2) * pitch for i in range(n)]
    return [t - r for t, r in zip(tgt, rib_pos)]

def s_bend_length(delta, R, theta_max_deg):
    """Axial length of an S-bend (arc R, straight at theta, arc R) giving lateral
    offset delta. Returns (length, theta_used_deg)."""
    delta = abs(delta)
    if delta == 0:
        return 0.0, 0.0
    th_max = radians(theta_max_deg)
    # pure two-arc S at angle theta: delta = 2R(1-cos th)
    d_arc_max = 2 * R * (1 - cos(th_max))
    if delta <= d_arc_max:
        th = asin(sqrt(delta / (2 * R) * (2 - delta / (2 * R)))) if delta < 2 * R else pi / 2
        # simpler: 1 - cos th = delta/(2R)
        from math import acos
        th = acos(1 - delta / (2 * R))
        return 2 * R * sin(th), degrees(th)
    s = (delta - d_arc_max) / sin(th_max)
    return 2 * R * sin(th_max) + s * cos(th_max), theta_max_deg

R_BEND = 5.0      # [assumption] bend radius a 1.7 mm silicone conductor takes without fuss (~3x OD)
TH_MAX = 30.0     # [assumption] steepest fan angle before comb friction and kinking matter
OVERHANG = 9.0    # [estimate] comb front face to conductor tip: contact 5.8-6.7 + ~0.8 tab/bellmouth + 1-2 free
print(f"S-bend with R = {R_BEND} mm, steepest angle {TH_MAX} deg; tip overhang ahead of the comb "
      f"{OVERHANG} mm")
print("pitch cases: 2.5 = XH housing; 4.0 and 5.0 = crimp pitch wide enough for a slim tool;")
print("7.0 = carrier-strip pitch [estimate: HDGC2501-T drawing scaled by its own 1.5 mm pilot hole")
print("and 1.85 mm box, 6.8-7.5 mm; JST's number is licence-gated]")
for pitch in (2.5, 4.0, 5.0, 7.0):
    print(f"\n  target pitch {pitch} mm")
    for name, ribs, ways, trim in LOOMS:
        # pairs: consider both 'together' (one fan) and 'each ribbon alone' for carrier pitch
        off = offsets(ribs, pitch)
        dmax = max(abs(o) for o in off)
        L, th = s_bend_length(dmax, R_BEND, TH_MAX)
        split = L + OVERHANG
        extra = ""
        if len(ribs) == 2:
            dsep = max(max(abs(o) for o in offsets((r,), pitch)) for r in ribs)
            Ls, _ = s_bend_length(dsep, R_BEND, TH_MAX)
            extra = f" | each ribbon fanned alone: max move {dsep:.1f}, split {Ls + OVERHANG:.0f} mm"
        print(f"    {name:14s} {'+'.join(str(r)+'P' for r in ribs):6s} max move {dmax:5.1f} mm, "
              f"fan {L:4.1f} mm at {th:4.1f} deg -> part the web back ~{split:3.0f} mm{extra}")
print("\n-> Housing pitch alone needs only ~12-18 mm parted. A 5 mm crimp pitch needs ~20-40 mm.")
print("   Carrier pitch (~7 mm) needs ~30-60 mm unless each ribbon of a pair is fanned alone.")

# ---------------------------------------------------------------------------
hdr("3. How wide the crimp pitch must be: tool nose vs neighbours")
# half-widths, mm
open_ins = (2.46 / 2, 3.00 / 2)    # [source] clone drawings: insulation barrel open 2.46-3.00 wide
open_cond = (1.68 / 2, 1.90 / 2)   # [source] conductor barrel open
crimped_ins = 2.05 / 2             # [source] KONNRA KR2501 PS §6.5: insulation crimp width 2.05 max
bare = RIB / 2
print("Neighbour half-widths: bare conductor 0.85; crimped contact (ins. barrel) 1.03;")
print(f"open contact (ins. barrel) {open_ins[0]:.2f}-{open_ins[1]:.2f}")
print(f"(a) Open contacts side by side at 2.5 mm pitch: gap between open insulation wings "
      f"{2.5 - 2*open_ins[1]:+.2f} to {2.5 - 2*open_ins[0]:+.2f} mm -> they collide or nearly so:")
print("    contacts cannot be pre-loaded in a row at housing pitch; one at a time only.")
for nose in (3.0, 4.0, 6.0, 10.0):
    # neighbours in the same plane as the active contact: the nose must pass beside them
    pc_plane = nose / 2 + crimped_ins + 0.3
    print(f"(b) tool nose {nose:4.1f} mm wide, neighbours in plane: crimp pitch >= {pc_plane:.1f} mm")
print("(c) neighbours lifted 4-5 mm above the active contact: they only have to clear the")
print("    part of the tooling that reaches below their level at the bottom of the stroke -")
print("    the forming noses of punch and hold-down, typically 3-4 mm wide [estimate] ->")
print(f"    crimp pitch >= {3.5/2 + bare + 0.3:.1f}-{4.0/2 + crimped_ins + 0.3:.1f} mm. 5.0 mm is a round choice with margin.")

# ---------------------------------------------------------------------------
hdr("4. The conductor as a beam: sag, lay-in force, and why nobody pushes on a bare wire")
E_si_lo, E_si_hi = 2.0, 6.0        # MPa [estimate] Shore 50-70A silicone (wire grades per Primasil)
E_cu = 117e3                       # MPa
d_str, n_str = 0.08, 60            # [source]
OD, bundle = 1.7, 0.72             # [source]/[calc C1]
I_ins = pi / 64 * (OD**4 - bundle**4)
EI_ins = (E_si_lo * I_ins, E_si_hi * I_ins)
EI_cu_free = n_str * E_cu * pi / 64 * d_str**4       # strands slipping freely
EI = (EI_ins[0] + EI_cu_free, EI_ins[1] + EI_cu_free)
print(f"insulation I = {I_ins:.3f} mm^4 -> EI {EI_ins[0]:.2f}-{EI_ins[1]:.2f} N mm^2;"
      f" strands (free to slip) {EI_cu_free:.3f} N mm^2")
print(f"total EI ~{EI[0]:.2f}-{EI[1]:.2f} N mm^2: the copper strands carry most of the elastic stiffness")
# annealed copper yields at ~0.06 % strain [estimate: ~70 MPa / 117 GPa]; a strand of radius r
# bent to radius R strains r/R, so strands take a set below R ~ 0.04/0.0006 ~ 70 mm
sy_cu = 70.0
Mp = n_str * sy_cu * d_str**3 / 6
print(f"annealed strands take a permanent set below a bend radius of ~{0.04/(sy_cu/E_cu):.0f} mm; "
      f"plastic moment of the bundle ~{Mp:.2f} N mm")
print("-> the conductor keeps whatever shape the comb gives it (a fan stays fanned), and")
print("   handling leaves set in it; the silicone jacket springs back only part of the way")
A_cu = n_str * pi / 4 * d_str**2
A_si = pi / 4 * (OD**2 - bundle**2)
w = (A_cu * 8.96e-3 + A_si * 1.15e-3) * 9.81e-3     # N/mm  (g/mm^3 * mm^2 * g->N)
print(f"weight {w*1e3:.3f} N/m ({w/9.81e-3*1e3:.1f} g/m)")
for L in (5, 10, 15, 20):
    sag_hi = w * L**4 / (8 * EI[0])
    sag_lo = w * L**4 / (8 * EI[1])
    print(f"  cantilever {L:2d} mm from a comb: gravity sag {sag_lo:.3f}-{sag_hi:.3f} mm")
print("  -> within ~10 mm of a comb the conductor points where the comb points; residual set")
print("     from the spool, not gravity, is the error source [assumption: <0.3 mm at 10 mm].")
for L, d in ((10, 4), (15, 5)):
    F = 3 * EI[1] * d / L**3
    print(f"  pushing a {L} mm free length down {d} mm into a waiting contact: {F*1e3:.1f} mN")
print(f"  (elastic figures; the strands yield once the root moment passes {Mp:.2f} N mm, i.e. a")
print(f"   tip force of ~{Mp/10*1e3:.0f} mN on a 10 mm length, so the real force is lower still)")
print("  -> a lay-in finger needs a fraction of a newton.")
print("Euler buckling of the free conductor under an axial push (pinned-pinned):")
for L in (1, 2, 5, 10):
    Pcr = pi**2 * EI[1] / L**2
    Pcr_lo = pi**2 * EI[0] / L**2
    print(f"  L = {L:2d} mm: {Pcr_lo:.2f}-{Pcr:.2f} N")
F_ins = 9.8    # [source] KONNRA PS-KR2501-01 §6.2 insertion 1.0 kgf max (clone of XH)
print(f"-> insertion wants up to {F_ins} N per contact [source, clone spec]. Elastic Euler already")
print("   limits a free length to ~3-4 mm, and yielding strands lower that further. The push")
print("   must come from a clamp gripping the insulation within ~2 mm of the insulation barrel,")
print("   or through a closed channel. Clamp grip needed:")
for mu in (0.5, 1.0):
    print(f"   mu {mu}: normal force >= {F_ins/mu:.0f} N per conductor (two jaws: {F_ins/mu/2:.0f} N each face)")

# ---------------------------------------------------------------------------
hdr("5. Parting the web: tear and cut forces")
T_lo, T_hi = 10.0, 25.0     # N/mm [source] silicone tear strength: general ~9.8, wire grades 15-25 (Primasil, Shin-Etsu)
for t in (0.2, 0.4, 0.6):   # web thickness at the notch [assumption: unmeasured, Open item 5]
    print(f"web {t:.1f} mm thick: tear force to run a split {T_lo*t:.0f}-{T_hi*t:.0f} N per web")
print("-> a few newtons to ~15 N per web. A wedge comb opening all webs of a 5P at once")
print("   (4 webs) pulls ~10-60 N on the clamp. A hand or a hobby servo does this.")
print("   A sharp blade drawn along a valley cuts at well under the tear force [assumption].")

# ---------------------------------------------------------------------------
hdr("6. Pulling the strip slug")
L_strip = 2.4          # [mfr] JST WC-110 calibration strip length
# friction of the slug on strands after the ring is cut: silicone grips, but the slug is short
# and the insulation was not bonded to tinned strands [assumption]
p_contact = 0.05       # MPa [estimate] residual radial pressure of an extruded jacket
mu = 0.8
F_fric = p_contact * pi * bundle * L_strip * mu
print(f"friction of a {L_strip} mm slug if the ring is fully cut: ~{F_fric:.2f} N")
for lig in (0.05, 0.15, 0.3):
    # uncut ligament around the circumference torn: tear strength x ligament thickness,
    # two tear fronts per conductor [estimate]
    F_tear = (T_lo * lig * 2, T_hi * lig * 2)
    print(f"uncut ligament {lig:.2f} mm left by a depth-limited blade: tear {F_tear[0]:.1f}-{F_tear[1]:.1f} N per conductor")
print("-> leaving 0.1-0.2 mm of silicone uncut costs only a few newtons per conductor to tear,")
print("   so the blade can stop well short of the 0.08 mm strands.")
print("   Whole-end strip of a 9-conductor pair: ~9 x (3-15) = 30-135 N through the clamp.")

# ---------------------------------------------------------------------------
hdr("7. Gang strokes: all crimps of a ribbon at once")
F_one = (0.79, 2.59)   # kN [calc C1] peak per contact, both barrels
for n in (3, 4, 5, 9):
    print(f"{n} contacts in one stroke: {n*F_one[0]:.1f}-{n*F_one[1]:.1f} kN "
          f"(VEVOR 12 t shop press ~118 kN; margin {118/(n*F_one[1]):.0f}x at the high end)")
print("-> force is not the obstacle; die making and height control are. A die set that")
print("   bottoms on hardened stop blocks makes crimp height a property of the die set,")
print("   not of the press.")
# stop block stress when the press overdrives: suppose the operator reaches 20 kN
for A in (100, 200, 400):     # mm^2 total stop block area
    print(f"  stop blocks {A} mm^2 total at 20 kN overdrive: {20000/A:.0f} MPa (hardened steel ok < ~1000)")

# ---------------------------------------------------------------------------
hdr("8. Insertion: all at once vs one after another")
for n in (4, 5, 7, 9):
    print(f"{n} contacts straight in together: up to {n*F_ins:.0f} N through the clamp "
          f"[source max per contact]; tilted 'lean and slide' (Sogang) keeps ~1-2 in the "
          "lead-in at any moment: ~10-20 N")
print("Sogang #26 ribbon into 2.5 mm housings [source arXiv 2608.06996]: straight parallel approach")
print("3/20 success (pitch and yaw errors); lean-and-slide 18/20; with weaving and a guide clamp,")
print("insertion 49/50.")

# ---------------------------------------------------------------------------
hdr("9. Electrical access through the far end (pogo on the cut face)")
rho = 0.0172   # ohm mm^2 / m
R_per_m = rho / A_cu
print(f"conductor resistance {R_per_m*1e3:.0f} mOhm/m; a 100-600 mm loom {R_per_m*0.1*1e3:.0f}-{R_per_m*0.6*1e3:.0f} mOhm")
print("crimp resistance ~1-2 mOhm [mfr: 10 mOhm initial max for the XH contact interface]")
print("-> two-wire through the loom sees continuity, opens and shorts, and blade-to-copper")
print("   touches; it cannot grade a crimp. Four-wire at the crimp needs two probes on the")
print("   contact and two on the conductor's far end.")

# ---------------------------------------------------------------------------
hdr("10. Time budget for one unit, one conductor at a time [estimate]")
steps = {
    "load pallet (person)": 60,
    "flush cut": 10,
    "part webs (per web 20 s)": None,
    "fan comb on": 20,
    "strip (per conductor 30 s)": None,
    "crimp incl. lay-in, stroke, look (per conductor 90 s)": None,
    "pitch close + insert + pull-back (per housing 90 s)": 90,
    "unload (person)": 30,
}
ends = [(sum(r), ways, trim) for _, r, ways, trim in LOOMS]
n_cond = sum(n for n, _, _ in ends)
n_crimp = sum(n - (1 if t else 0) for n, _, t in ends)
n_webs = sum(sum(r) - 1 for _, r, _, _ in LOOMS)
n_ends = len(LOOMS)
t = n_ends * (60 + 10 + 20 + 90 + 30) + n_webs * 20 + n_crimp * 30 + n_crimp * 90
print(f"{n_ends} housings, {n_cond} conductors, {n_crimp} crimps, {n_webs} webs to part")
print(f"machine time ~{t/60:.0f} min per unit ({t/3600:.1f} h); person's hands ~{n_ends*90/60:.0f} min (load/unload)")
print("-> an afternoon per unit even at 2 minutes per crimp, against ~100 printer-hours per unit.")
