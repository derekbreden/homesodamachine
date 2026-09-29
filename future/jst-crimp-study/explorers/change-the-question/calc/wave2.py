"""change-the-question, wave 2: numbers for the revised and new arrangements.

Run:  python3 wave2.py > wave2.out.txt

Cited from the idea files as "calc w2 §n". Inputs carry labels:
[mfr], [source], [calc], [estimate], [assumption], [ts] = terminal-supply's
exchange calc (explorers/terminal-supply/calc/on_change_the_question.out.txt),
[ff] = force-and-form wave-2 calc.
"""

import math


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


RIBBON_PITCH = 1.7   # mm [source S29]
HOUSING_PITCH = 2.5  # mm [mfr S1]
JACKET_OD = 1.7      # mm [source S29]
CORE_D = (0.75, 0.80)  # mm strand bundle, 60 x 0.08 mm [xh-facts section 7, estimate]
T = 0.20             # mm stock, +/-0.02 [source S19-S21]

# ---------------------------------------------------------------------------
hr("1. The Wurth 646 001 137 22 contact is not XH-sized")
wurth_box = (1.45, 2.00)      # W x H, section C-C [mfr Wurth drawing rev H 2017, re-read 2026-09-28]
xh_box_w = (1.85, 1.95)       # [source S19-S22; mfr S1 envelope]
xh_box_h = (2.2, 2.4)
print(f"  Wurth box {wurth_box[0]} x {wurth_box[1]} mm; XH box {xh_box_w[0]}-{xh_box_w[1]} x {xh_box_h[0]}-{xh_box_h[1]} mm")
print(f"  Wurth is {xh_box_w[0]-wurth_box[0]:.2f}-{xh_box_w[1]-wurth_box[0]:.2f} mm narrower and "
      f"{xh_box_h[0]-wurth_box[1]:.2f}-{xh_box_h[1]-wurth_box[1]:.2f} mm lower: it would sit loose in an XHP cavity.")
print("  Its open wings (2.3 x 2.15), its 7.10 mm carrier pitch and its 1.50 mm pilot hole describe a")
print("  smaller 2.5 mm-pitch contact, not an XH one; it is kept out of every XH gap table.")

# ---------------------------------------------------------------------------
hr("2. Pre-formed contact (c6): envelope, gaps at a pitch, and room for a punch beside it")
# Pre-form: insulation wings closed around a mandrel of diameter d, leaving a throat g at the top.
mandrels = (1.50, 1.55, 1.60, 1.65)   # mm [design choice]
springback_id = (0.02, 0.05)          # mm growth of the ID after release [estimate, see section 3]
cond_open = {"clone nominal 1.80": 1.80, "clone max 1.90+0.25": 2.15, "clone min 1.68-0.25": 1.43}
# [source S19-S22: conductor barrel open width 1.68-1.90 +/-0.25]
print("  insulation envelope after pre-form = mandrel + springback + 2 x stock")
for d in mandrels:
    lo = d + springback_id[0] + 2 * (T - 0.02)
    hi = d + springback_id[1] + 2 * (T + 0.02)
    print(f"    mandrel {d:.2f} mm -> insulation envelope {lo:.2f}-{hi:.2f} mm")
W_INS = (1.96, 2.14)   # adopted range for a 1.55-1.60 mandrel [calc, above]
print(f"  adopted pre-formed insulation envelope {W_INS[0]}-{W_INS[1]} mm (1.55-1.60 mandrel);")
print("  compare JST's catalog end-view envelope 1.95 mm [mfr S1] and clone open wings 2.46-3.25 mm.")
print()
print("  gap between neighbouring contacts, widest section governing (mm; negative = collide):")
print(f"  {'pitch':>6} {'pre-formed ins.':>16} {'open cond. nominal':>19} {'open cond. max':>15} {'clone open ins. 2.8/3.25':>25}")
for p in (2.5, 3.4, 5.0):
    print(f"  {p:>6.1f} {p - W_INS[1]:>16.2f} {p - 1.80:>19.2f} {p - 2.15:>15.2f} {p-2.8:>12.2f} / {p-3.25:<8.2f}")
print()
# Room for a punch section beside a neighbour: p - neighbour half-width - 0.1 clearance
PUNCH_COND = (1.75, 1.90)   # half-width, single-nest conductor punch [estimate, wave 1 ctq section 3]
PUNCH_INS = (1.90, 2.00)    # half-width, insulation section [ts otq section 4]
PUNCH_NARROW_COND = (1.20, 1.55)  # half-width: into-the-housing 2.4-3.05 mm; force-and-form f8 3.1 mm step
print("  room (half-width) for the target's punch beside ONE neighbour, 0.1 mm clearance:")
for p in (2.5, 3.4, 5.0):
    r_ins_pre = p - W_INS[1] / 2 - 0.1
    r_ins_clone = p - 3.25 / 2 - 0.1
    r_cond_nom = p - 1.80 / 2 - 0.1
    r_cond_max = p - 2.15 / 2 - 0.1
    print(f"  pitch {p:3.1f}: insulation section beside pre-formed {r_ins_pre:4.2f} (beside clone-open {r_ins_clone:4.2f}); "
          f"conductor section beside open barrel {r_cond_max:4.2f}-{r_cond_nom:4.2f}")
print(f"  needed: conductor punch {PUNCH_COND[0]}-{PUNCH_COND[1]}, insulation punch {PUNCH_INS[0]}-{PUNCH_INS[1]};"
      f" a narrow conductor punch {PUNCH_NARROW_COND[0]}-{PUNCH_NARROW_COND[1]}")
p = 3.4
spare_ins = (p - W_INS[1] / 2 - 0.1 - PUNCH_INS[1], p - W_INS[0] / 2 - 0.1 - PUNCH_INS[0])
spare_cond = (p - 2.15 / 2 - 0.1 - PUNCH_COND[1], p - 1.80 / 2 - 0.1 - PUNCH_COND[0])
print(f"  at 3.4 mm beside pre-formed neighbours: insulation spare {spare_ins[0]:.2f}-{spare_ins[1]:.2f} mm, "
      f"conductor spare {spare_cond[0]:.2f}-{spare_cond[1]:.2f} mm -> an ordinary single-nest punch fits, no lift")
p = 2.5
print(f"  at 2.5 mm beside open conductor barrels: room {p-2.15/2-0.1:.2f}-{p-1.80/2-0.1:.2f} mm against a narrow punch "
      f"{PUNCH_NARROW_COND[0]}-{PUNCH_NARROW_COND[1]} -> passes only for punches <= ~2.6-3.0 mm wide")
print("  (the 3.1 mm conductor step of force-and-form f8 misses by up to 0.2 mm beside a 2.15 mm open barrel)")

# ---------------------------------------------------------------------------
hr("3. Forming the pre-form: force per wing, die force, springback (c6)")
sy = {"phosphor bronze C5191 spring temper [estimate 450-650]": (450, 650),
      "brass C2680 half-hard, if a clone uses it [assumption 300-420]": (300, 420)}
b_ins = (0.8, 1.5)     # mm insulation barrel length [xh-facts section 1 estimate]
arm = (1.0, 2.0)       # mm, from bend line to where the die bears [estimate]
for k, (s_lo, s_hi) in sy.items():
    Mlo = s_lo * (T - 0.02) ** 2 / 4 * b_ins[0]
    Mhi = s_hi * (T + 0.02) ** 2 / 4 * b_ins[1]
    print(f"  {k}: plastic hinge moment {Mlo:.2f}-{Mhi:.2f} N*mm per wing;"
          f" force {Mlo/arm[1]:.1f}-{Mhi/arm[0]:.1f} N per wing")
print("  two wings, friction on the die and an overbend allowance x2-3 -> die force ~10-80 N per contact [estimate]")
print("  (context calc: insulation forming with a wire in it is 33-132 N per barrel; no wire here, so lower)")
E_pb, E_br = 110e3, 100e3   # MPa [estimate]
for name, s, E in (("PB 550 MPa", 550, E_pb), ("PB 650 MPa", 650, E_pb), ("brass 400 MPa", 400, E_br)):
    for R in (0.78, 1.0):
        x = s * R / (E * T)
        K = 4 * x ** 3 - 3 * x + 1
        print(f"  springback {name}, bend radius {R} mm: K = {K:.3f} -> the wing opens back {100*(1-K):.1f}% of its bend angle")
print("  a 30 deg inward bend springs back ~2 deg: the die overbends by that much; the ID grows ~0.02-0.05 mm")

# ---------------------------------------------------------------------------
hr("4. Snap-in: pushing the jacket through the throat, retention, axial grip (c6)")
def gent_E(shore_a):
    # Gent's relation, Shore A to Young's modulus in MPa [source: A.N. Gent 1958, as commonly quoted]
    return 0.0981 * (56 + 7.62336 * shore_a) / (0.137505 * (254 - 2.54 * shore_a))
for s in (50, 60, 70):
    print(f"  silicone Shore {s}A -> E ~ {gent_E(s):.1f} MPa   [Shore 50-70A: source Primasil via ribbon-as-pallet]")
E_lo, E_hi = gent_E(50), gent_E(70)
wall = ((JACKET_OD - CORE_D[1]) / 2, (JACKET_OD - CORE_D[0]) / 2)
L = b_ins
print(f"  jacket wall {wall[0]:.2f}-{wall[1]:.2f} mm over a {CORE_D[0]}-{CORE_D[1]} mm strand core")
print("  push-in through a throat g: per-side interference d = (1.7 - g)/2, wall strain d/wall,")
print("  contact chord a = 2 sqrt(0.85 d), normal force N = k E strain a L (k = 0.5-1 for bulge relief),")
print("  push F = 2 N (tan(alpha) + mu)/(1 - mu tan(alpha)), alpha 30-40 deg, mu 0.3-0.8 [all estimate]")
for g in (1.2, 1.3, 1.4, 1.5):
    d = (JACKET_OD - g) / 2
    a = 2 * math.sqrt(0.85 * d)
    Nlo = 0.5 * E_lo * (d / wall[1]) * a * L[0]
    Nhi = 1.0 * E_hi * min(d / wall[0], 0.6) * a * L[1]
    def push(N, alpha, mu):
        ta = math.tan(math.radians(alpha))
        return 2 * N * (ta + mu) / (1 - mu * ta)
    Flo, Fhi = push(Nlo, 30, 0.3), push(Nhi, 40, 0.8)
    print(f"  throat {g:.1f} mm: interference {d:.2f}/side, N {Nlo:.2f}-{Nhi:.1f} N/side, push-in ~{Flo:.1f}-{Fhi:.0f} N")
print("  retention against lifting out is taken as 0.5-1x the push-in force [assumption]: ~0.3-10 N for g = 1.3")
print()
print("  axial grip of the C on the jacket (the flag's axial hold):")
for ID in (1.50, 1.55, 1.60, 1.65):
    d = (JACKET_OD - ID) / 2
    for (E, lab) in ((E_lo, "E lo"), (E_hi, "E hi")):
        pass
    strain = (d / wall[1], d / wall[0])
    p = (E_lo * strain[0], E_hi * strain[1])            # MPa
    area = (math.pi * ID * L[0] * 0.5, math.pi * ID * L[1] * 0.8)   # mm^2 in contact
    mu = (0.3, 0.8)
    F = (mu[0] * p[0] * area[0], mu[1] * p[1] * area[1])
    print(f"  C inner diameter {ID:.2f}: squeeze {100*(JACKET_OD-ID)/JACKET_OD:4.1f}% of OD, pressure {p[0]:.2f}-{p[1]:.2f} MPa,"
          f" axial grip ~{F[0]:.2f}-{F[1]:.1f} N")
print("  force-and-form's thin-layer model gives 0.4-9 N at 10-30 % squeeze [ff wave2 section 5]; same order.")
print()
w_contact = 0.043e-3 * 9.81
print(f"  what a snapped flag has to resist: its weight {w_contact*1000:.2f} mN; a keyed slot 0.1-0.5 N [ts otq section 7];")
print("  a 0.64 mm post push-on 0.2-1.6 N [ts section 7]. A 1.55-1.60 mm C clears the slot case at central values.")

# ---------------------------------------------------------------------------
hr("5. Pre-formed contacts stack nose to tail: no nesting (c6)")
throat = (1.2, 1.4)
print(f"  box {xh_box_w[0]}-{xh_box_w[1]} wide vs pre-formed throat {throat[0]}-{throat[1]} and C bore 1.55-1.65:"
      " the next contact's box can enter neither from above nor from behind.")
print("  open clone wings (2.46-3.25 wide) admit a box (1.85-1.95): that is why loose contacts nest [hand-tool-as-press].")
Lc = (5.8, 6.73)   # contact length [source S19-S22]
for n, what in ((4, "one T4 end"), (9, "J1"), (53, "one unit"), (84, "a long T4 spool run (21 ends)"),
                (100, "a 100-piece strip")):
    print(f"  stick for {what:<32} {n:>4} contacts: {n*Lc[0]/1000:.2f}-{n*Lc[1]/1000:.2f} m")
print("  short loom-order sticks (4-9 contacts, 23-61 mm) are the handy unit; a unit is 14 of them, or 10 per housing.")

# ---------------------------------------------------------------------------
hr("6. c1, Repair A (crimp both rows, then insert A, then B): split length it needs")
def s_bend_length(d, theta_deg):
    th = math.radians(theta_deg)
    R = d / (2 * (1 - math.cos(th)))
    return 2 * R * math.sin(th)
carrier_len = (3.0, 8.0)   # mm: box-only carrier 3 mm, whole-contact pocket ~8 mm [estimate]
for n in (2, 3, 4, 5):
    d = (n - 1) * (2 * HOUSING_PITCH - 2 * RIBBON_PITCH) / 2
    L20, L30 = s_bend_length(d, 20), s_bend_length(d, 30)
    need = (L30 + carrier_len[0], L20 + carrier_len[1])
    print(f"  row of {n}: outer move {d:.1f} mm, S-bend {L30:4.1f}-{L20:4.1f} mm (30-20 deg);"
          f" split needed so pallet B meets only straight row-A wire: {need[0]:4.1f}-{need[1]:4.1f} mm")
print("  T4 rows of two fit a 12 mm split; J1's row of five needs ~15-26 mm (a box-only carrier and a 30 deg bend")
print("  keep it near 15). Split length stays Derek's question.")

# ---------------------------------------------------------------------------
hr("7. c5 with supply sized to the run (terminal-supply C2), and c6 sticks")
spool = 15240
for L, lab in ((700, "long"), (400, "short")):
    ends = spool // L
    contacts = ends * 4
    print(f"  {lab} T4 run: {ends} ends, {contacts} contacts, {ends} XHP-4;"
          f" housing stick {ends*5.7:.0f} mm (stacked by 5.7 mm depth) to {ends*7.75:.0f} mm (by 7.75 mm height)")
print("  a long run's 84 contacts fit one 100-piece strip with 16 spare [ts otq section 9]: spool and strip change together.")
print(f"  as pre-formed loose contacts: 84 in a {84*Lc[0]/1000:.2f}-{84*Lc[1]/1000:.2f} m coiled track, or 21 four-contact sticks.")

# ---------------------------------------------------------------------------
hr("8. The skew end (notebook direction): pitch from one uniform bend at a diagonal split root")
for p in (2.5, 3.4, 5.0):
    beta = math.degrees(math.asin(RIBBON_PITCH / p))
    bend = 90 - beta
    stagger = RIBBON_PITCH / math.tan(math.radians(beta))
    for R in (3.0, 5.0):
        arc = R * math.radians(bend)
        print(f"  pitch {p:3.1f}: root line at {beta:4.1f} deg to the conductors, each bends {bend:4.1f} deg;"
              f" root points {stagger:4.2f} mm apart along the wire; bend radius {R:.0f} -> arc {arc:4.1f} mm")
print("  Every conductor makes the same bend, so one groove shape translated N times replaces a fan block;")
print("  free length is arc + ~2 mm (~5-7 mm) against 14-18 mm for a housing-pitch fan [ribbon-as-pallet calc 2].")
print("  The ribbon then leaves the housing ~47 deg off the contact axis, in the row's plane.")
