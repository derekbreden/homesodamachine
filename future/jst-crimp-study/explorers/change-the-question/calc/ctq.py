"""change-the-question explorer: numbers behind the reframed arrangements.

Run:  python3 ctq.py > ctq.out.txt

Every input carries its label: [repo], [mfr], [source], [calc], [estimate], [assumption].
Sections are cited from the idea files as "calc ctq §n".
"""

import math

def hr(t):
    print("\n" + "=" * 76)
    print(t)
    print("=" * 76)

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
RIBBON_PITCH = 1.7          # mm per conductor [source S29, xh-facts §7]
HOUSING_PITCH = 2.5         # mm [mfr S1]
STRIP = 2.4                 # mm strip length for SXH-001T-P0.6 at 22 AWG [mfr S6]

# open insulation-barrel width (the widest part of an uncrimped contact), mm
WING_W = {
    "JST catalog end-view envelope (1.95)": 1.95,         # [mfr S1-S3] - whether wings fit inside is unresolved
    "HDGC / JXT clone (2.7-2.8 nominal)": 2.80,           # [source S19, S21]
    "clone worst case (3.0 + 0.25)": 3.25,                # [source S22 +tol]
}
WING_H = {"JST env 2.4": 2.4, "HDGC 3.0": 3.0, "CJT 3.2 + 0.25": 3.45}  # open insulation wing height [mfr S1 envelope / source S19-S22]
# The Wurth 646 001 137 22 drawing (open wings 2.3 x 2.15) is NOT an XH-sized contact: its box is
# 1.45 x 2.00 mm (section C-C) against XH's 1.85-1.95 x 2.2-2.4 [mfr Wurth rev H 2017, re-read
# 2026-09-28]. It is kept out of every XH table here; see wave2.py section 1.
CRIMPED_W = 1.95            # crimped contact width, taken as the catalog envelope [mfr S1]
COND_OD = 1.7               # insulated conductor OD [source S29]

# Per unit, the ten XH looms [repo cable-assemblies.md]; lengths [repo ac-wiring-schedule.md]
# (ribbons laid edge to edge, conductor position -> cavity; None = trimmed, not crimped)
LOOMS = {
    # name: (end type, housing ways, ribbons, cut length mm, position->cavity map)
    "J1 MANIFOLD A": ("T9", 9, "5P+4P", 350, {i: i for i in range(1, 10)}),
    "J2 MANIFOLD B": ("T6", 6, "3P+3P", 400, {1: 1, 2: 2, 3: None, 4: 4, 5: 5, 6: 6}),
    "J3 FAUCET":     ("T4", 4, "4P",    None, {1: 1, 2: 2, 3: 3, 4: 4}),
    # J4: 4P laid [3V3, IO26, V5, IO25] -> cavities 1,5,3,4; 3P laid [GND, IO27, IO23] -> 2,6,7.
    # Pairs kept adjacent for peeling; this is the least-crossing order of all such layouts
    # (searched in order_search.py: 2 conductors off their ribbon-parity plane, 2 crossings).
    "J4 SENSORS":    ("T7s", 7, "4P+3P", 350, {1: 1, 2: 5, 3: 3, 4: 4, 5: 2, 6: 6, 7: 7}),
    "J5 RELAYS":     ("T4", 4, "4P",    100, {1: 1, 2: 2, 3: 3, 4: 4}),
    "J6 REEDS A":    ("T5", 5, "5P",    450, {i: i for i in range(1, 6)}),
    # J7: 5P laid [RB1..RB4, GND] -> 1,2,3,4,7; 3P laid [trimmed, CLO, CHI] -> -,5,6.
    # Least-crossing order (order_search.py): every conductor on its parity plane, one crossing.
    "J7 REEDS B":    ("T7r", 7, "5P+3P", 400, {1: 1, 2: 2, 3: 3, 4: 4, 5: 7, 6: None, 7: 5, 8: 6}),
    "J9 DISPLAY":    ("T4", 4, "4P",    400, {1: 1, 2: 2, 3: 3, 4: 4}),
    "J11 GAS":       ("T4", 4, "4P",    600, {1: 1, 2: 2, 3: 3, 4: 4}),
    "J13 PUMPS":     ("T4", 4, "4P",    350, {1: 1, 2: 2, 3: 3, 4: 4}),
}
UNITS = 60   # program: 1 + 10 + 50 [repo future/README.md via shared-context]

# ---------------------------------------------------------------------------
hr("1. End types: what the machine would actually be asked to make")
types = {}
for name, (t, ways, rib, L, m) in LOOMS.items():
    crimps = sum(1 for v in m.values() if v is not None)
    d = types.setdefault(t, {"looms": [], "crimps": 0, "ways": ways, "rib": rib, "n": 0})
    d["looms"].append(name.split()[0]); d["crimps"] += crimps; d["n"] += 1
tot = sum(d["crimps"] for d in types.values())
print(f"{'type':<5}{'ribbons':<8}{'housing':<9}{'looms':<24}{'ends/unit':>10}{'crimps/unit':>12}{'share':>7}{'program ends':>13}")
for t, d in sorted(types.items(), key=lambda kv: -kv[1]["crimps"]):
    print(f"{t:<5}{d['rib']:<8}{'XHP-'+str(d['ways']):<9}{','.join(d['looms']):<24}{d['n']:>10}{d['crimps']:>12}{d['crimps']/tot:>7.0%}{d['n']*UNITS:>13}")
print(f"total crimps per unit {tot}  (shared context says 53)")
print("T4 = 4P into XHP-4, no pair, no skip, no crossing: 5 of 10 housings, 20 of 53 crimps.")

# ---------------------------------------------------------------------------
hr("2. Half-rows (c1): assign each crimped conductor to the odd- or even-cavity row")
def half_rows(m):
    A = sorted([(c, p) for p, c in m.items() if c is not None and c % 2 == 1])
    B = sorted([(c, p) for p, c in m.items() if c is not None and c % 2 == 0])
    return A, B

def crossings(row):
    # a crossing = two conductors whose ribbon order is opposite to their cavity order
    ps = [p for c, p in row]
    return sum(1 for i in range(len(ps)) for j in range(i + 1, len(ps)) if ps[i] > ps[j])

def parity_mismatch(row, want_odd):
    return [p for c, p in row if (p % 2 == 1) != want_odd]

print(f"{'loom':<15}{'row A (odd cav)':<22}{'row B (even cav)':<22}{'cross A/B':>10}  conductors not on their ribbon-parity row")
for name, (t, ways, rib, L, m) in LOOMS.items():
    A, B = half_rows(m)
    fa = " ".join(f"{p}>{c}" for c, p in A); fb = " ".join(f"{p}>{c}" for c, p in B)
    mis = parity_mismatch(A, True) + parity_mismatch(B, False)
    print(f"{name:<15}{fa:<22}{fb:<22}{crossings(A):>5}/{crossings(B):<4}  {mis if mis else '-'}")
print("Notation p>c: ribbon position p lands in cavity c. Row A pallets hold at most 5 contacts (J1),")
print("row B at most 4. Only J4 and J7 need a conductor sent to the 'wrong' plane or crossed in-plane.")

hr("2b. Row spread after the crimp: pallet pitch 3.4 mm (2 x ribbon) -> 5.0 mm (2 x housing)")
def s_bend_length(d, theta_deg):
    # two equal arcs, tangent at the ends: lateral offset d, max slope theta; returns axial length
    th = math.radians(theta_deg)
    R = d / (2 * (1 - math.cos(th)))
    return 2 * R * math.sin(th), R
for n in (2, 3, 4, 5):
    span_in = (n - 1) * 2 * RIBBON_PITCH
    span_out = (n - 1) * 2 * HOUSING_PITCH
    d = (span_out - span_in) / 2
    L20, R20 = s_bend_length(d, 20) if d > 0 else (0, 0)
    L30, R30 = s_bend_length(d, 30) if d > 0 else (0, 0)
    print(f"{n} contacts in a row: span {span_in:4.1f} -> {span_out:4.1f} mm; outermost moves {d:4.2f} mm; "
          f"S-bend length {L20:4.1f} mm at 20 deg, {L30:4.1f} mm at 30 deg")
print("Rows start at 3.4 mm only if each row keeps its ribbon order; a pair laid edge to edge is one row.")

# ---------------------------------------------------------------------------
hr("3. Can open contacts sit side by side? gap between open insulation wings at a pitch")
print(f"{'wing width':<42}" + "".join(f"{p:>9.1f}" for p in (2.5, 3.4, 5.0)) + "   (gap mm; negative = collide)")
for k, w in WING_W.items():
    print(f"{k:<42}" + "".join(f"{p - w:>9.2f}" for p in (2.5, 3.4, 5.0)))
print("\nMost a crimp punch can spread either side of its contact centreline without touching an")
print("OPEN neighbour's wings (0.1 mm clearance), vs a CRIMPED neighbour (1.95 envelope):")
for p in (2.5, 3.4, 5.0):
    for k, w in WING_W.items():
        open_n = p - w / 2 - 0.1
        crimp_n = p - CRIMPED_W / 2 - 0.1
        print(f"  pitch {p:3.1f}  {k:<40} beside open: {open_n:4.2f}  beside crimped: {crimp_n:4.2f}")
print("A conductor-crimp punch with ~1.0 mm legs around a ~1.5-1.8 mm profile is ~1.75-1.9 mm")
print("half-width [estimate]: it fits beside open neighbours at 5.0, is marginal at 3.4, fails at 2.5.")

hr("4. Lift-to-crimp (c1): lift one contact out of its row so any die width fits")
for k, h in WING_H.items():
    lift = h + 0.25 + 0.5
    for Lsplit in (12, 15, 20):
        ang = math.degrees(math.atan(lift / Lsplit))
        print(f"  wing height {k:<14} -> lift {lift:4.2f} mm; conductor slope over {Lsplit} mm split {ang:4.1f} deg")

# ---------------------------------------------------------------------------
hr("5. Tack first (c1b): gang-close the insulation barrels, crimp conductor barrels later")
INS_LO, INS_HI = 33, 132        # N per insulation barrel wing forming [calc C1 section 4, context]
COND_LO, COND_HI = 750, 2300    # N per conductor barrel at bottom of stroke [calc C1 section 4]
for n in (2, 3, 4, 5):
    print(f"  half-row of {n}: gang tack {n*INS_LO:4d}-{n*INS_HI:4d} N   vs   gang conductor crimp {n*COND_LO/1000:4.2f}-{n*COND_HI/1000:5.2f} kN")
print("  NEMA 23 1.5 N*m through a 2 mm trapezoid screw at eta 0.3: ~1.4 kN [calc C1 section 5] -> ample for a tack gang.")
# stress on a printed anvil under a tack, and on a steel anvil
area = 1.2 * 1.9   # mm^2 insulation barrel floor on anvil [estimate from drawings]
for F in (INS_LO, INS_HI):
    print(f"  tack {F} N on {area:.1f} mm^2 barrel floor -> {F/area:5.1f} MPa (PETG yields ~45-50 MPa [estimate]; steel anvil strip)")

# ---------------------------------------------------------------------------
hr("6. Solder-set joint (c3): fold wings without coining, then solder")
t = 0.20            # mm stock [source S19-S21]
sy = 550.0          # MPa yield of spring-temper C5191 phosphor bronze [estimate, 450-650]
wing_len = 1.4      # mm, conductor barrel length [estimate]
M = sy * t**2 / 4 * wing_len            # N*mm fully plastic hinge moment per wing
for arm in (0.8, 1.2):
    print(f"  plastic hinge moment per wing {M:4.2f} N*mm; force at {arm} mm arm {M/arm:5.1f} N per wing")
print("  curling both wings against a punch arch with friction: tens to ~300 N total [calc C1 section 4 range],")
print("  i.e. roughly 3-10x less than coining the conductor barrel (0.75-2.3 kN).")
# heat to solder temperature
m_contact = 0.043e-3        # kg [source S27b]
c_pb = 380.0                # J/kg K phosphor bronze
m_cu = 8960 * 0.302e-6 * 0.010   # kg of copper in 10 mm of conductor [calc C1 section 1 area]
c_cu = 385.0
dT = 230.0
E = (m_contact * c_pb + m_cu * c_cu) * dT
print(f"  heat to lift contact + 10 mm of conductor by {dT:.0f} K: {E:4.1f} J (a 60-70 W iron supplies this in well under a second;")
print("  real dwell 1-3 s is set by conduction into the wire and tip contact) [calc]")

# ---------------------------------------------------------------------------
hr("7. Carrier strip pitch against the housing (the strip cannot load several cavities)")
P = 7.10   # mm, Wurth 646 001 137 22 carrier pitch [mfr Wurth drawing]: the only public 2.5 mm-class
           # carrier pitch, but for a SMALLER contact (box 1.45 mm); JST SXH pitch is unmeasured
for k in (2, 3, 4):
    print(f"  {k} x 2.5 = {k*2.5:4.1f} mm  (strip {P} mm, mismatch {P-k*2.5:+5.2f} mm)")
for k in (4,):
    print(f"  {k} x 1.7 = {k*1.7:4.1f} mm  (ribbon every 4th conductor; mismatch {P-k*1.7:+5.2f} mm)")
print("  7.10 mm belongs to Wurth's smaller WR-WTB 2.50 contact (box 1.45 mm), not to an XH contact.")
print("  JST's own SXH pitch is licence-gated; clone drawings scale to 7-9.5 mm [xh-facts section 1].")

# ---------------------------------------------------------------------------
hr("8. Bought factory crimps (c2): JST ASXHSXH22K jumper leads against the loom lengths")
jumper_max = 304.8   # mm, ASXHSXH22K305 [source Digi-Key 2026-09-28]
price_100 = 0.65     # $ each at 100 [source Digi-Key]
usable = jumper_max - 15   # one end cut off and stripped [estimate]
fits = [n for n, (t, w, r, L, m) in LOOMS.items() if L is not None and L <= usable]
print(f"  usable single-ended length {usable:.0f} mm; looms that fit: {fits}")
print(f"  a lead cut in half gives two ~{jumper_max/2-10:.0f} mm pigtails at ${price_100/2:.3f} per crimped end")
print(f"  53 ends x ${price_100/2:.3f} = ${53*price_100/2:.2f} per unit (if lengths allowed; they mostly do not)")
print("  J4, J6, J7 run in the cold core, which asks for silicone, not PVC [repo bom.md section 11]")

# ---------------------------------------------------------------------------
hr("9. Ends as stock (c5): standard lengths cut down at build time")
price_m = {"3P": 20.36 / 15.24, "4P": 24.65 / 15.24, "5P": 31.08 / 15.24}   # $/m [repo bom.md section 11]
loop = 50   # mm service loop [assumption]
J3_LEN = 450  # mm, J3 is unmeasured in the repo [assumption]
stock_T4 = (350 + loop, 650 + loop)
waste = 0.0
print(f"  T4 stock lengths {stock_T4} mm; J3 taken as {J3_LEN} mm [assumption]; +{loop} mm service loop")
for name in ("J3 FAUCET", "J5 RELAYS", "J9 DISPLAY", "J11 GAS", "J13 PUMPS"):
    L = LOOMS[name][3] or J3_LEN
    need = L + loop
    s = min(x for x in stock_T4 if x >= need)
    waste += (s - need) / 1000 * price_m["4P"]
    print(f"    {name:<12} needs {need:4d} -> stock {s:4d}, offcut {s-need:4d} mm")
print(f"  T4 offcut per unit ${waste:.2f} of 4P ribbon")
per_spool = int(15240 // stock_T4[1])
print(f"  one 15.2 m 4P spool makes {per_spool} long T4 ends, or {int(15240 // stock_T4[0])} short ones, in one unattended run")
print(f"  program T4 ends: {5*UNITS}; at 3 long + 2 short per unit that is "
      f"~{math.ceil(UNITS*(3*stock_T4[1]+2*stock_T4[0])/15240)} spools of 4P for the T4 ends alone")
