"""
Numbers for the into-the-housing explorer.

Every input carries a label: [mfr], [source], [repo], [calc], [estimate],
[assumption]. Ranges are carried through instead of single values where the
input is unknown. Run:  python3 insertion_geometry.py > insertion_geometry.out.txt
"""
import math
from itertools import permutations

def hr(t):
    print("\n" + "=" * 76 + "\n" + t + "\n" + "=" * 76)

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
PITCH = 2.50              # XH housing pitch, mm [mfr S1]
WIRE_OD = (1.6, 1.7, 1.8) # BNTECHGO 22 AWG conductor OD 1.7 +/-0.1 [source S29]
STRANDS = 60              # 60 x 0.08 mm [source S29]
STRAND_D = 0.08           # mm
E_CU = 117e3              # N/mm^2 copper, tinned annealed [estimate]
E_SIL = (1.0, 5.0, 10.0)  # N/mm^2 silicone rubber, Shore 50-80A range [estimate]
BUNDLE_D = 0.72           # mm strand bundle [calc C1 in context/calc]
BOX_W, BOX_H = 1.95, 2.40 # contact end-view envelope, JST Shape B [mfr S1]
CONTACT_L = (6.1, 6.5, 6.73)  # JST 2025 / JST 2016,2021 / CJT A2501-T drawing [mfr S1-S3, source S22]
BOX_L = 2.0               # box length [mfr S1]
LANCE_TIP = (2.2, 2.44, 2.6)  # lance tip behind contact front; CJT 2.44 +/-0.20 [source S22]
HOUSING_H = 7.75          # XHP height along mating axis, 7.5 + 0.25 [mfr S1, S2]
INS_CRIMP_W = (1.8, 1.9, 2.05)  # crimped insulation barrel width [estimate, xh-facts 1.8-2.0]
CON_CRIMP_W = (1.4, 1.5, 1.6)   # crimped conductor barrel width [estimate; SXA analog 1.50]
F_INSERT = (3.0, 8.0, 14.7, 25.0)  # N; contact insertion into housing. 14.7 N max is the
# Molex Mini-SPOX (2.50 mm, friction-lock family) product-spec figure seen via search
# summary, document not opened [source]; XH figure is licence-gated [mfr S16];
# 3-8 N is the feel of a hand push [estimate]; 25 N is a margin bound [assumption].
F_RETAIN_MIN = 14.7       # N, same Mini-SPOX analog, minimum retention [source]
F_PULLOUT_CRIMP = 39.2    # N, JST crimp pull-out min at 22 AWG [mfr S6]

# ---------------------------------------------------------------------------
hr("1. How far behind the crimp the wire may be pushed without buckling")
# Strands bend individually (they slide on each other), so the bundle's EI is
# the sum of the strands' EI [assumption: no bonding; a tinned, twisted bundle
# is somewhat stiffer, which only lengthens the allowed free length].
I_strand = math.pi * STRAND_D**4 / 64
EI_cu = STRANDS * E_CU * I_strand  # N*mm^2
print(f"strand-sum EI (60 x 0.08 mm copper)       = {EI_cu:8.3f} N*mm^2")
for od in WIRE_OD[1:2]:
    I_sil = math.pi * (od**4 - BUNDLE_D**4) / 64
    for e in E_SIL:
        EI = EI_cu + e * I_sil
        print(f"  + silicone E={e:4.1f} MPa, OD {od}: EI total = {EI:7.3f} N*mm^2")
EI_lo = EI_cu + E_SIL[0] * math.pi * (1.7**4 - BUNDLE_D**4) / 64
EI_hi = EI_cu + E_SIL[2] * math.pi * (1.7**4 - BUNDLE_D**4) / 64
print("\nLongest unsupported wire (mm) that carries the push without buckling, P = pi^2 EI/(K L)^2")
print("K = 2.0 (gripped behind, contact free to swing), 1.0 (both ends guided), 0.5 (both ends clamped square)")
print(f"{'F (N)':>7} | {'K=2 soft':>9} {'K=2 stiff':>9} | {'K=1 soft':>9} {'K=1 stiff':>9} | {'K=0.5 soft':>10} {'K=0.5 stiff':>11}")
for F in F_INSERT:
    row = []
    for K in (2.0, 1.0, 0.5):
        for EI in (EI_lo, EI_hi):
            row.append(math.pi * math.sqrt(EI / F) / K)
    print(f"{F:7.1f} | {row[0]:9.2f} {row[1]:9.2f} | {row[2]:9.2f} {row[3]:9.2f} | {row[4]:10.2f} {row[5]:11.2f}")
print("-> a gripper pushing through the insulation must hold the wire within ~1-3 mm of the")
print("   insulation barrel (K=2, the contact nose free before it finds the cavity); a guide that")
print("   keeps the contact square (K=0.5-1) stretches that to ~3-8 mm. Pushing from farther back")
print("   needs a tube or channel around the wire.")

# ---------------------------------------------------------------------------
hr("2. Room for a tool at 2.5 mm pitch, between neighbours")
for od in WIRE_OD:
    gap_wires = 2 * PITCH - od           # free width between neighbour wires, centred on axis
    print(f"wire OD {od}: free width between the two neighbour wires = {gap_wires:.2f} mm "
          f"(tool half-width must be < {gap_wires/2:.2f})")
for w in INS_CRIMP_W:
    gap = 2 * PITCH - w
    print(f"neighbour contacts crimped at {w:.2f} mm wide: free width between their barrels = {gap:.2f} mm")
# A crimp punch has walls outside the crimped profile.
for wall in (0.3, 0.4, 0.5):
    for w in INS_CRIMP_W:
        punch_w = w + 2 * wall
        margin = (2 * PITCH - WIRE_OD[1]) / 2 - punch_w / 2
        print(f"  punch walls {wall:.1f} mm on a {w:.2f} barrel -> punch {punch_w:.2f} wide; "
              f"clearance to a 1.7 mm neighbour wire each side {margin:+.2f} mm")
print("-> a narrow blade punch (<= ~3.0 mm wide where it passes the wire plane) fits between")
print("   neighbours with 0.1-0.3 mm to spare; anything wider (a hand-tool jaw) needs the")
print("   neighbours moved out of the plane, or the conductor moved out of the row.")
# Slotted pusher blade that follows the contact into the cavity
cav_w = (BOX_W + 0.05, BOX_W + 0.15)  # cavity width [estimate: box + 0.05-0.15 clearance]
for cw in cav_w:
    for slot in (1.35, 1.45, 1.55):
        tine = (cw - 0.05 - slot) / 2
        bear = (INS_CRIMP_W[1] - slot) / 2
        print(f"  pusher blade for cavity {cw:.2f} wide: slot {slot:.2f} (squeezes the 1.7 wire), "
              f"tines {tine:.2f} mm, bearing on a 1.90 barrel {bear:.2f} mm per side")

diag = math.hypot(BOX_W, BOX_H)
print(f"\nRound guide tube around the wire: the box's diagonal is {diag:.2f} mm, so a round tube must have")
print(f"ID >= {diag:.2f} mm; with a 0.225 mm wall (K&S metric brass) OD >= {diag + 0.45:.2f} mm, wider than the")
print(f"{2*PITCH - WIRE_OD[1]:.2f} mm free between neighbour wires. K&S 3.0 x 0.225 (ID 2.55) does not pass the box.")
print("-> a guide around the contact at 2.5 mm pitch is a U-channel or a rectangular slot, not a round tube.")

# ---------------------------------------------------------------------------
hr("3. Pin order: which looms can be laid straight across from ribbon to housing")
# Pin order from hardware/pcb/pcba/pcba.tsx; ribbon split from
# hardware/assembly/cable-assemblies.md (Ribbon pairs, assembly schedule) [repo].
looms = {
    "J4 SENSORS (4P+3P -> XHP-7)": (
        ["3V3", "GND", "V5", "IO25", "IO26", "IO27", "IO23"],
        {"4P": {"3V3", "IO26", "V5", "IO25"}, "3P": {"IO27", "IO23", "GND"}}),
    "J7 REEDS B (5P+3P -> XHP-7, one 3P conductor trimmed)": (
        ["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"],
        {"5P": {"RB1", "RB2", "RB3", "RB4", "GND"}, "3P": {"CLO", "CHI"}}),
    "J2 MANIFOLD B (3P+3P -> XHP-6, cavity 3 empty)": (
        ["COM", "FAN", "-", "OUT3", "OUT2", "OUT1"],
        {"3P a": {"COM", "FAN", "-"}, "3P b": {"OUT3", "OUT2", "OUT1"}}),
}
def min_cross(pins, groups):
    """Ribbons lie edge to edge; inside a ribbon, which conductor carries which net is
    assumed free (set at the far end). Crossings = pairs (a in left ribbon, b in right
    ribbon) with pin(a) > pin(b). Minimise over the side-by-side order of ribbons."""
    idx = {p: i for i, p in enumerate(pins)}
    best = None
    for order in permutations(groups):
        c = 0
        for i in range(len(order)):
            for j in range(i + 1, len(order)):
                for a in groups[order[i]]:
                    for b in groups[order[j]]:
                        if idx[a] > idx[b]:
                            c += 1
        if best is None or c < best[0]:
            best = (c, order)
    return best
for name, (pins, groups) in looms.items():
    c, order = min_cross(pins, groups)
    print(f"{name}: minimum crossings = {c}, ribbons left->right {order}")
    for g in order:
        print(f"     {g}: pins {sorted(pins.index(p) + 1 for p in groups[g])}")
print("J1 (5P+4P), J3, J5, J6, J9, J11, J13: single ribbon or split not stated -> assumed straight")
print("-> J4 needs one conductor (the 3P's GND, to pin 2) to cross three 4P conductors;")
print("   J7 needs the 5P's GND (to pin 7) to cross CLO and CHI. A gang arrangement that")
print("   keeps ribbon order into the housing cannot make J4 or J7 as the repo assigns them.")

# ---------------------------------------------------------------------------
hr("4. Where the contact sits in the housing, and the crimp-in-the-cavity window")
# Housing rear face at y = 0, mating face at y = +7.75. Seated contact front sits
# behind a front wall of t_front [estimate 0.4-0.8 mm].
for L in CONTACT_L:
    for tf in (0.4, 0.8):
        rear = HOUSING_H - tf - L
        print(f"contact {L:.2f} long, front wall {tf:.1f}: seated rear of insulation barrel is "
              f"{rear:+.2f} mm {'inside' if rear > 0 else 'proud of'} the rear face")
print("-> the last 0.4-1.2 mm of the push happens with the insulation barrel inside the")
print("   cavity (unless the seated contact stands proud): the pusher must fit the cavity,")
print("   or the push ends on something already inside (the box shoulder is gone by then).")
print()
print("Crimp in the cavity: box held in the cavity entry by depth d; conductor-barrel front")
print("must be >= c clear of the rear face for the die's front wall.")
for trans in (0.2, 0.5):      # box-to-conductor-barrel transition length [estimate]
    for c in (0.2, 0.4):
        d = BOX_L + trans - c
        for chamfer in (0.2, 0.4):
            print(f"  transition {trans:.1f}, die wall clearance {c:.1f}, entry chamfer {chamfer:.1f}: "
                  f"box engaged {d:.2f} mm, of which straight wall {d - chamfer:.2f} mm")
for lt in LANCE_TIP:
    print(f"  lance tip {lt:.2f} behind front -> lance first touches the entry at depth ~{lt:.2f} mm")
print("-> the box can sit 1.4-2.3 mm deep with the conductor barrel still outside; the lance")
print("   meets the entry at ~2.2-2.6 mm. The window exists only if the transition is long enough,")
print("   which one kit housing and contact under a caliper settles.")

# ---------------------------------------------------------------------------
hr("5. One contact at a time, or all of a ribbon at once")
for n in (4, 5, 7, 9):
    lo, hi = n * F_INSERT[0], n * F_INSERT[3]
    print(f"{n} contacts pushed together: {lo:5.0f} to {hi:5.0f} N total ({n}x 3-25 N)")
print("Staggered gang (spring-backed wire clamps): each clamp's preload must exceed the")
print("largest single insertion force so it stays put until its contact bottoms.")
for F_pre in (20.0, 30.0):
    for k in (2.0, 5.0):
        travel = 1.0 * 8  # 8 later contacts x 1 mm stagger
        print(f"  preload {F_pre:.0f} N, rate {k:.0f} N/mm, 1 mm stagger: first contact's clamp rides back "
              f"up to {travel:.0f} mm, ending at {F_pre + k*travel:.0f} N (J1, 9 contacts)")
print("-> the stagger turns one push into N separate force events in a known order;")
print("   each clamp's own switch reports that its contact bottomed.")

# ---------------------------------------------------------------------------
hr("6. Sensing the latch")
for v in (0.05, 0.2, 1.0):   # push speed mm/s
    for sps in (10, 80):     # HX711 rates [source: Adafruit 5974]
        print(f"  push {v:.2f} mm/s, HX711 at {sps:2d} SPS: {sps / v:6.0f} samples per mm of travel")
print("A lance snap is a force drop over roughly 0.1-0.3 mm of travel [estimate]; at <= 0.2 mm/s")
print("and 80 SPS that is 40-120 samples: a slow push resolves it with a $4 bar cell.")
print()
print("Force-limited pusher without a load cell: a spring and a displacement switch.")
for Flim in (15.0, 25.0):
    for dx in (1.0, 2.0):
        print(f"  trip at {Flim:.0f} N after {dx:.1f} mm spring travel -> spring rate {Flim/dx:.1f} N/mm")
print()
print("Pull-back test window:")
print(f"  lance retention min (analog) {F_RETAIN_MIN} N; crimp pull-out min {F_PULLOUT_CRIMP} N")
for Fp in (3.0, 5.0, 8.0):
    print(f"  pull back at {Fp:.0f} N = {Fp/F_RETAIN_MIN*100:3.0f}% of retention min, "
          f"{Fp/F_PULLOUT_CRIMP*100:3.0f}% of crimp pull-out min")
print("-> 3-8 N pulls an unlatched contact out and leaves a latched one and its crimp unharmed;")
print("   pass = < ~0.2 mm of travel at the test force (Boeing US 11,374,374 logic).")

# ---------------------------------------------------------------------------
hr("7. Splay needed to crimp at a wider pitch than the housing")
# Two-ribbon J1: 9 conductors, ribbon centres span 13.6 mm (15.3 wide - 1.7).
for name, n, ribbon_span in (("J1 5P+4P", 9, 15.3 - 1.7), ("J6 5P", 5, 8.5 - 1.7), ("J3 4P", 4, 6.8 - 1.7)):
    for pw in (2.5, 5.0, 7.5):
        move = (n - 1) * pw / 2 - ribbon_span / 2
        for ang in (20, 30):
            L = max(move, 0) / math.tan(math.radians(ang))
            print(f"  {name}: crimp pitch {pw:.1f} -> outermost conductor moves {move:5.1f} mm; "
                  f"split length >= {L:5.1f} mm at {ang} deg")
print("-> crimping at 5 mm pitch asks for ~20-35 mm of split web on J1 (vs ~6-9 mm for the")
print("   housing's own 2.5 mm fan).")

# ---------------------------------------------------------------------------
hr("8. Time per unit (53 crimps), rough, for scale")
cycles = {
    "i1 walk the housing past the head (feed 20 s, lay 10, crimp 30, insert 20, test 10)": 90,
    "i2 crimp in the cavity (load 20 s, lay 10, crimp 30, push 15, test 10)": 85,
    "i3 shuttles + gang push (per contact 60 s, plus 60 s per ribbon for converge/push)": 60,
    "i4 gantry hand (pick 30 s, look 10, insert 30, pull test 10) on top of any crimper": 80,
    "i5 person inserts on the sensing nest (attended, ~8 s per contact)": 8,
}
for k, s in cycles.items():
    extra = 14 * 60 if k.startswith("i3") else 0
    tot = (53 * s + extra) / 60
    print(f"  {k}: ~{tot:4.0f} min per unit")
print("-> every arrangement fits inside an afternoon; none of these times matters against a")
print("   week of printing. What matters is how often the person is called back.")

# ---------------------------------------------------------------------------
hr("9. Feed-length rule: one-at-a-time insertion stores the insertion travel as slack")
# Relative to the ribbon clamp (the web), a seated contact is where the final loom
# puts it. A contact crimped anywhere short of that point has to travel forward by
# the rest, so while it is crimped its conductor carries that much extra length.
# Only a gang push (housing moved onto a row of contacts that stay put) needs none.
SEAT_TRAVEL_FROM_REAR = HOUSING_H - 0.6   # box front from rear face to seated, front wall 0.6 [estimate]
cases = {
    "crimp in the cavity (box 2.0 mm in the entry)": SEAT_TRAVEL_FROM_REAR - 2.0,
    "crimp with box nose 1 mm behind the rear face": SEAT_TRAVEL_FROM_REAR + 1.0,
    "crimp at a head 5 mm behind the rear face": SEAT_TRAVEL_FROM_REAR + 5.0,
    "gang push of a row (housing moves)": 0.0,
}
for k, f in cases.items():
    print(f"  {k}: conductor must feed {f:4.1f} mm after its crimp")
print()
print("Stored as a hump between ribbon clamp and tip (parabolic arch, chord c, sag h):")
print("  h = sqrt(3 c f / 8)")
for c in (10.0, 15.0, 20.0, 30.0):
    row = "  ".join(f"f={f:.0f}: h={math.sqrt(3*c*f/8):4.1f}" for f in (5, 8, 10))
    print(f"  chord {c:4.1f} mm -> {row}")
print()
print("Stored as a straight lift of the tip up to a head above the row (conductor straight")
print("from the ribbon clamp to the tip, free length L, tip pulled back f):")
for L in (20.0, 25.0, 30.0, 40.0):
    row = "  ".join(f"f={f:.0f}: lift {math.sqrt(L**2 - (L - f)**2):4.1f}" for f in (8, 10, 13))
    print(f"  L {L:4.1f} mm -> {row}")
print("-> a head above the row sits ~15-25 mm up; a hump of 5-9 mm stores the feed in place.")
print("   Either way the split conductors need ~10-30 mm of free length behind the housing")
print("   during the build, even though the finished fan needs only ~6-9 mm.")
