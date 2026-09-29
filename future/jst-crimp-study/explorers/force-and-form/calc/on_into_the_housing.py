"""
force-and-form's numbers for its wave-2 exchange on into-the-housing.

Each section tests one specific conflict in one of into-the-housing's ideas
(i1, i1b, i2, i2b, i2c, i3, i3b, i4, i5) or in its handover.md. Inputs carry
labels: [mfr], [source], [repo], [calc], [estimate], [assumption].
Coordinates follow into-the-housing/handover.md: Y along the contact, +Y toward
the mating face; X across the row; Z up, barrels open up, lance down.

Run:  python3 on_into_the_housing.py > on_into_the_housing.out.txt
"""
import math


def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


# ---------------------------------------------------------------------------
# Shared inputs
# ---------------------------------------------------------------------------
PITCH = 2.50                    # XH pitch [mfr S1]
WIRE_OD = 1.70                  # BNTECHGO 22 AWG conductor OD [source S29]
BOX_L = 2.0                     # box length [mfr S1]
LANCE_TIP = (2.24, 2.44, 2.64)  # tip behind contact front, CJT 2.44 +/-0.20 [source S22]
LANCE_PROUD = (0.6, 0.67, 0.9)  # below the floor [source S19-S22]
STOCK = 0.20                    # C5191 phosphor bronze [source S19-S21]
E_CU = 117e3                    # N/mm^2 [estimate]
E_PB = 110e3                    # phosphor bronze, N/mm^2 [estimate]
SY_PB = (500.0, 650.0)          # C5191 spring-temper yield, N/mm^2 [estimate]
F_PEAK = (780.0, 1680.0, 2430.0)  # crimp peak force low/central/high [calc stroke_model]
PULLOUT_MIN = 39.2              # JST 22 AWG [mfr S6]
RETENTION_ANALOG = 14.7         # Molex Mini-SPOX analog, via search summary [source]
EI_WIRE = (14.5, 18.1)          # N*mm^2, strands + silicone [calc into-the-housing §1]
R_SET_CU = 67.0                 # strands yield below ~67 mm bend radius [digest wave 1]

# ---------------------------------------------------------------------------
hr("1. The lance and the anvil (i2, and every die in the study)")
# ---------------------------------------------------------------------------
print("""The lance hangs 0.6-0.9 mm below the box floor, its tip 2.44 +/-0.20 mm behind the
contact front [source S22], i.e. 0.24-0.64 mm behind the box's rear end, in the
transition between box and conductor barrel. The barrel floor and box floor are one
plane (the contact is formed from one flat strip) [assumption].""")
print("\n1a. i2's own sketch (25 px/mm): rear face x=560, cavity floor y=300,")
print("    anvil rect x=466..554, top y=300; lance drawn from (575,300) to (549,317).")
px = 25.0
anvil_front_behind_rf = (560 - 554) / px
lance_tip_behind_rf = (560 - 549) / px
lance_tip_below_floor = (317 - 300) / px
lance_root_inside_rf = (575 - 560) / px
print(f"    anvil front edge   {anvil_front_behind_rf:.2f} mm behind the rear face, top at the floor")
print(f"    lance tip          {lance_tip_behind_rf:.2f} mm behind the rear face, {lance_tip_below_floor:.2f} mm below the floor")
print(f"    lance root         {lance_root_inside_rf:.2f} mm inside the rear face")
overlap = lance_tip_behind_rf - anvil_front_behind_rf
print(f"    -> the drawn lance tip lies {overlap:.2f} mm inside the anvil in Y and "
      f"{lance_tip_below_floor:.2f} mm below its top: the two occupy the same steel.")

print("\n1b. Where the lance tip sits relative to the rear face, box engaged d mm")
print("    (lance free, i.e. not yet folded by the entry):")
print("     d   | tip behind rear face for tip = 2.24 / 2.44 / 2.64 | lance over an anvil whose front is 0.2-0.3 mm back?")
for d in (1.4, 1.8, 2.0, 2.2, 2.4):
    tips = [lt - d for lt in LANCE_TIP]
    over = ["yes" if t > 0.2 else ("edge" if t > 0.0 else "inside housing") for t in tips]
    print(f"    {d:4.1f} | {tips[0]:6.2f} {tips[1]:6.2f} {tips[2]:6.2f}                             | {', '.join(over)}")

print("\n1c. What a flat anvil under a free lance does: the contact rests on its lance tip.")
for p in LANCE_PROUD:
    # contact pivots about the box held in the cavity; the barrels ride p high
    print(f"    lance {p:.2f} proud -> barrels start {p:.2f} mm above the anvil; the punch meets them "
          f"{p:.2f} mm early and the stroke flattens the lance (the retention feature) and "
          f"bends the transition")
print("    A force monitor sees this as 'contact seated high': the curve rises ~0.6-0.9 mm early,")
print("    far outside any band [calc: metrology §3 logic]. It is detected, not prevented.")

print("\n1d. Repair: a lance relief. The anvil's front end stops behind the lance tip, or is")
print("    slotted under the lance, as applicator strip tracks are [assumption: applicator practice].")
print("    The conductor barrel floor must still be supported, so the barrel's front must lie")
print("    behind the lance tip + margin. Transition t = conductor-barrel front minus box rear.")
print("    t needed (lance tip + 0.1 mm margin - box length):")
for lt in LANCE_TIP:
    print(f"      lance tip {lt:.2f}: t >= {lt + 0.1 - BOX_L:.2f} mm")
print("    t from the length budget (overall - box - conductor barrel - window - insulation barrel):")
rows = []
for L in (6.1, 6.5, 6.73):          # JST 2025 / JST 2016,2021 / CJT [mfr S1-S3, source S22]
    for cb in (1.25, 1.5):          # conductor barrel length [estimate, xh-facts]
        for win in (0.4, 0.8):      # window between barrels [estimate]
            for ib in (0.8, 1.5):   # insulation barrel length [estimate, xh-facts]
                rows.append(L - BOX_L - cb - win - ib)
print(f"      t ranges {min(rows):.2f} .. {max(rows):.2f} mm over the drawn lengths and estimated barrels;")
print("      i2 assumed 0.2-0.5. The lance-relief condition and i2's barrel-clear condition both")
print("      turn on t, and one kit contact photographed side-on under the ELP camera gives it.")

print("\n1e. The i2 window with the lance included (all behind-rear-face distances, mm):")
print("    conditions: box engaged d >= 1.4 (walls hold it) [i2 calc §4];")
print("    conductor-barrel front (2.0 + t - d) >= 0.2 die-wall clearance [i2];")
print("    anvil front >= lance tip (L - d) + 0.1 and <= barrel front (lance free), OR")
print("    lance root inside the entry so the entry folds the lance (then no anvil conflict).")
for t in (0.2, 0.4, 0.6, 0.8, 1.0):
    ok = []
    for d10 in range(14, 25):
        d = d10 / 10.0
        barrel_front = 2.0 + t - d
        if barrel_front < 0.2:
            continue
        # lance free: anvil front must sit between lance tip + 0.1 and the barrel front
        lt = LANCE_TIP[2]  # worst case: tip farthest back
        anvil_min = max(lt - d + 0.1, 0.1)
        if anvil_min <= barrel_front:
            ok.append(d)
    rng = f"{min(ok):.1f}-{max(ok):.1f}" if ok else "none"
    print(f"    t = {t:.1f}: box depth d with barrel clear AND a supported barrel behind a lance relief: {rng}")
print("    -> with t below ~0.7 no depth works while the lance hangs free under the barrel front;")
print("       the idea then needs the lance folded by the entry (lance root inside) or a")
print("       notched anvil that leaves the barrel's front edge unsupported.")

# ---------------------------------------------------------------------------
hr("2. Two locators for one contact: cavity (PA6) and die (steel) in X (i2, i2b)")
# ---------------------------------------------------------------------------
box_w = (1.85, 1.95)       # [mfr S1, source S19-S22]
cav_w = (2.00, 2.10)       # cavity width [estimate]
print("Box play in the cavity, per side:")
for bw in box_w:
    for cw in cav_w:
        print(f"  box {bw:.2f} in cavity {cw:.2f}: +/-{(cw - bw) / 2:.3f} mm")
print("Sources of cavity-to-die X offset [estimate]:")
src = {
    "printed nest locating the housing": 0.10,
    "XHP pitch accumulated to the far cavity of XHP-9 (8 pitches)": 0.10,
    "carriage lead screw step error": 0.02,
}
for k, v in src.items():
    print(f"  {k:62s} +/-{v:.2f}")
tot = sum(src.values())
rss = math.sqrt(sum(v * v for v in src.values()))
print(f"  worst-case sum +/-{tot:.2f}, root-sum-square +/-{rss:.2f}")
print("Offset left after the box's play, carried by the transition over its length t:")
for off in (0.05, 0.10, 0.15):
    for t in (0.3, 0.6, 1.0):
        ang = math.degrees(math.atan(2 * off / t))  # S-bend, both ends held square
        print(f"  offset {off:.2f} over t = {t:.1f}: S-bend slope ~{ang:4.1f} deg")
print("The punch flare centres the barrels on the die with tens to hundreds of N at first")
print("touch, so this offset goes into the transition or into the PA6 wall. It also comes off")
print("the 0.2-0.45 mm clearance between the punch and the seated neighbour's wire.")

# ---------------------------------------------------------------------------
hr("3. Narrow crimper: what governs is wall bending, not the column (i1b, i2, i2b)")
# ---------------------------------------------------------------------------
print("Free half-width beside the working axis, set by the neighbour wire (1.7 mm round,")
print("centre 2.5 mm away). Neighbour wire centre height above the floor h_c ~1.05 mm")
print("(0.2 stock + 0.85 radius) [estimate]. Z measured up from the barrel floor.")
r = WIRE_OD / 2
h_c = STOCK + r
for z in (0.0, 0.2, 0.4, 0.6, 0.85, 1.05, 1.3, 1.6, 1.9):
    dz = abs(z - h_c)
    if dz >= r:
        free = PITCH  # neighbour wire absent at this height -> up to the neighbour's centre plane
        note = "(below/above the neighbour wire)"
    else:
        free = PITCH - math.sqrt(r * r - dz * dz)
        note = ""
    print(f"  Z = {z:4.2f}: tool may be up to {2 * free:4.2f} mm wide {note}")
print("-> the narrowest place is at the neighbour's equator (Z ~1.05), just ABOVE a conductor")
print("   crimp whose top is at ~0.8-0.9. Below Z ~0.6 there is 3.9 mm or more.")

print("\nWall bending at the root of the conductor crimper's channel (root at the roof, Z ~0.85).")
print("Lateral pressure on each wall = k x mean die pressure; k 0.3-1.0 [assumption: confined")
print("compaction pushes sideways at a fraction of the vertical pressure].")
W_ch = 1.5    # conductor crimp width, SXA analog [mfr S14]
L_b = 1.4     # barrel length along Y [estimate]
h_load = 0.7  # wall height the crimp presses on [estimate]
for F in F_PEAK[1:]:
    p = F / (W_ch * L_b)
    for k in (0.3, 0.5, 1.0):
        Flat = k * p * h_load * L_b
        M = Flat * h_load / 2
        cells = []
        for tw in (0.3, 0.4, 0.55, 0.7, 0.85):
            Zs = L_b * tw * tw / 6
            cells.append(f"{tw:.2f}:{M / Zs:6.0f}")
        print(f"  F {F:5.0f} N (p {p:4.0f} MPa), k {k:.1f}: wall t: stress MPa  " + "  ".join(cells))
print("  hardened D2/SKD11 transverse-rupture strength ~2500-3500 MPa; keep working stress")
print("  well under ~1200-1500 MPa for thousands of cycles [estimate].")
print("-> 0.3-0.4 mm walls on the CONDUCTOR crimper crack; 0.7-0.85 mm walls hold at k <= 0.5.")
print("   A 1.5 mm channel + 2 x 0.8 walls = 3.1 mm: fits the 3.35 mm free at Z 0.85 with")
print("   ~0.1 mm a side, and narrows to <= 3.2 above, where the neighbour's equator is.")
print("Insulation crimper: 30-130 N [xh-facts §4]; at 130 N over 1.9 x 1.2 mm, k = 1:")
p_ins = 130 / (1.9 * 1.2)
for tw in (0.3, 0.4):
    M = p_ins * 1.0 * 1.2 * 1.2 * 0.6  # force x arm, h 1.2
    print(f"  wall {tw:.1f}: {M / (1.2 * tw * tw / 6):6.0f} MPa")
print("-> the insulation crimper can be thin-walled; the conductor crimper cannot.")
print("Column check of the narrow neck, 2.9 x 1.4 mm, 4 mm tall, K = 2, at 2.43 kN:")
I_min = 2.9 * 1.4 ** 3 / 12
Pcr = math.pi ** 2 * 210e3 * I_min / (2 * 4.0) ** 2
print(f"  compressive {2430 / (2.9 * 1.4):.0f} MPa, Euler load {Pcr / 1000:.0f} kN: not the limit.")

print("\nDies that bottom on each other inside the narrow envelope: the crimper walls land on")
print("shoulders of the anvil block below the floor (Z < 0, where the neighbour wires are not).")
A_end = 2 * 0.8 * 1.4
for surplus in (300, 1000, 3000):
    print(f"  surplus force {surplus:5d} N on 2 wall ends of 0.8 x 1.4 mm: {surplus / A_end:6.0f} MPa")
print("-> workable only with the surplus capped near 1 kN: a spring-limited or current-limited")
print("   drive, or a knee whose straight position arrives with the dies just touching.")

# ---------------------------------------------------------------------------
hr("4. A gripper that holds the wire rigidly through the crimp (i1, i4)")
# ---------------------------------------------------------------------------
print("The anvil sets the barrel floor; a rigid grip 2-3 mm behind sets the wire. A Z (or X)")
print("mismatch delta between them is forced into an S-bend over the gap L.")
print("S-bend radius R ~ L^2 / (4 delta) [geometry]; copper strands set below ~67 mm.")
for L in (2.0, 3.0):
    for dlt in (0.05, 0.1, 0.2, 0.4):
        R = L * L / (4 * dlt)
        print(f"  L {L:.0f} mm, mismatch {dlt:.2f} mm: R {R:6.1f} mm -> {'sets (permanent kink)' if R < R_SET_CU else 'springs back'}")
print("-> any mismatch above ~0.02 mm leaves a permanent bend at the barrel, JST's")
print("   'bend up/down' fault and the handover's 'straight' requirement.")

# ---------------------------------------------------------------------------
hr("5. Touching a wire stop with the stripped tip (i1, i4)")
# ---------------------------------------------------------------------------
d = 0.08
I = math.pi * d ** 4 / 64
for Ls in (1.6, 2.1, 2.4):     # strip length: clone 1.6-2.1, JST 2.4 [mfr S6, digest]
    Pcr = math.pi ** 2 * E_CU * I / (2 * Ls) ** 2
    print(f"  one 0.08 mm strand, {Ls:.1f} mm free past the insulation, K = 2: buckles at {Pcr:.3f} N")
print("-> a ragged cut touches with a few strands first; the stop must be felt at ~0.1-0.3 N")
print("   or the first strands fold back. A 5 kg bar cell + HX711 resolves ~0.01-0.02 N at")
print("   10 SPS [estimate], so it is possible, but drag along the barrel floor is the same size.")
print("   The camera (insulation edge between the barrels) is the stronger axial reference.")

# ---------------------------------------------------------------------------
hr("6. i3b's staggered push loads the first crimps in compression")
# ---------------------------------------------------------------------------
print("Force path: housing front wall -> box -> contact -> crimps -> wire -> clamp 2-4 mm back.")
for F in (20, 30, 36, 46, 60, 70):
    Lc = [math.pi * math.sqrt(EI / F) / 0.5 for EI in EI_WIRE]
    frac = F / PULLOUT_MIN
    print(f"  {F:3d} N: {frac * 100:4.0f} % of JST's 39.2 N pull-out minimum; clamp-to-crimp wire "
          f"buckles (K=0.5) beyond {Lc[0]:.1f}-{Lc[1]:.1f} mm")
print("-> above ~20 N the crimp is asked to hold more than half its minimum pull-out, pushed")
print("   the way that drives the brush toward the box; at 60-70 N a 4 mm clamp distance")
print("   also buckles. Constant-force springs (or weights) on the clamps hold the load at the")
print("   preload however far the clamp rides back.")
for fi in (5, 8, 12, 15, 20, 25):
    pre = 1.25 * fi
    print(f"  measured single insertion {fi:2d} N -> preload {pre:5.1f} N ({pre / PULLOUT_MIN * 100:3.0f} % of pull-out min)")
print("-> staggering is comfortable if one contact inserts at <= ~12-15 N; Derek's scale")
print("   measurement under a housing decides it.")

# ---------------------------------------------------------------------------
hr("7. The force ladder: why a crimp proof-pull must come before insertion (all ideas)")
# ---------------------------------------------------------------------------
ladder = [
    ("latch test pull-back (i2, i3, i4)", 5.0),
    ("lance retention minimum, analog", RETENTION_ANALOG),
    ("crimp proof pull, half of JST pull-out", PULLOUT_MIN / 2),
    ("JST crimp pull-out minimum, 22 AWG", PULLOUT_MIN),
    ("22 AWG conductor break", 85.0),
]
for name, f in ladder:
    print(f"  {f:6.1f} N  {name}")
print("-> a proof load big enough to mean something about the crimp (~20 N) exceeds what a")
print("   latched contact holds (~15 N analog). After insertion only the latch can be tested;")
print("   the crimp can be proof-loaded only between the crimp and the push.")

# ---------------------------------------------------------------------------
hr("8. How far a lance can bend and spring back (i2c)")
# ---------------------------------------------------------------------------
print("Cantilever tip deflection at first yield: delta = 2 sy L^2 / (3 E t) [beam theory].")
for L in (1.0, 1.5, 2.0, 3.0):
    ds = [2 * sy * L * L / (3 * E_PB * STOCK) for sy in SY_PB]
    print(f"  lance {L:.1f} mm long, 0.2 mm thick: elastic to {ds[0]:.3f}-{ds[1]:.3f} mm of tip travel")
print("  against 0.6-0.9 mm of stand-proud [source S19-S22].")
print("-> folding the lance into a cavity is partly plastic by design [assumption: the lance")
print("   is not much longer than the drawings suggest]. Every extra fold (stub latch, lift,")
print("   re-latch in the product housing) is another plastic event of unknown cost to")
print("   retention. A stub that never engages the lance removes those events.")

# ---------------------------------------------------------------------------
hr("9. Insertability is an insulation-die dimension (handover item 3)")
# ---------------------------------------------------------------------------
print("Closed insulation barrel on 1.7 mm silicone, modelled as an ellipse of inner width")
print("w_i = channel - 2 x 0.2 holding the wire's section; e = share of silicone pushed out")
print("along the wire. Cavity envelope 1.95 wide x 2.4 tall [mfr S1, contact end view].")
A_wire = math.pi / 4 * WIRE_OD ** 2
for ch in (1.8, 1.85, 1.9, 1.95, 2.0):
    wi = ch - 2 * STOCK
    cells = []
    for e in (0.0, 0.1, 0.2):
        hi = A_wire * (1 - e) / (math.pi / 4 * wi)
        ho = hi + 2 * STOCK
        cells.append(f"e {e:.1f}: {ho:4.2f} tall{' (over)' if ho > 2.4 else ''}")
    print(f"  channel {ch:.2f} wide{' (over)' if ch > 1.95 else '       '}: " + "; ".join(cells))
print("-> [estimate, crude model] 1.7 mm silicone nearly fills the cavity section; a narrower")
print("   insulation crimp grows taller. Today's SN-2549 crimps evidently enter the housing,")
print("   so their insulation width and height (caliper) are the target any machine die copies.")

# ---------------------------------------------------------------------------
hr("10. Bending the strip over a crown so neighbour contacts miss the housing (i2 strip route)")
# ---------------------------------------------------------------------------
print("Drop needed at the neighbour's X: floor-to-housing-bottom ~0.8 [estimate] + contact")
print("height with open wings 2.75-3.2 [source S19-S22] -> ~3.6-4.0 mm.")
for pitch in (7.1, 8.0, 9.5):   # strip pitch: Wurth analog 7.1; clone drawings 7-9.5 [digest]
    for drop in (3.6, 4.0):
        R = pitch ** 2 / (2 * drop)
        strain = STOCK / 2 / R
        print(f"  strip pitch {pitch:.1f}, drop {drop:.1f}: crown radius {R:4.1f} mm, carrier strain "
              f"{strain * 100:4.2f} % ({'plastic' if strain > 0.005 else 'elastic'})")
print("-> the carrier takes a permanent curl over the crown (one-way, it is scrap after the")
print("   cut), and the feed pawl works on an arc. Feasible [estimate].")

# ---------------------------------------------------------------------------
hr("11. i2b: the anvil must drop below the neighbours' lances to step")
# ---------------------------------------------------------------------------
for drop in (1.0, 1.5):
    for p in LANCE_PROUD:
        print(f"  anvil drop {drop:.1f} mm, neighbour lance {p:.2f} proud: clearance {drop - p:+.2f} mm")
print("-> 1 mm leaves 0.1 mm on the tallest clone lance; 1.5 mm is comfortable.")

# ---------------------------------------------------------------------------
hr("12. The saddle hump turns Z error into Y error (i2, i1b)")
# ---------------------------------------------------------------------------
print("Stored feed f = 8 h^2 / (3 c) for a shallow arch of chord c, sag h [into-the-housing §9].")
print("df/dh = 16 h / (3 c): how far the tip moves in Y per mm the hump sits low or high.")
for c in (10.0, 15.0, 20.0):
    for f in (5.2, 8.2):
        h = math.sqrt(3 * c * f / 8)
        g = 16 * h / (3 * c)
        print(f"  chord {c:4.1f}, feed {f:3.1f}: sag {h:4.2f} mm, gain {g:4.2f} -> 0.1 mm of sag error = "
              f"{0.1 * g:4.2f} mm at the tip")
print("-> the tip's Y is ~1.5-3x as sensitive to how the conductor sits on its saddle; the")
print("   +/-0.2-0.3 mm axial window is gone at 0.1 mm of seating error. The same gain is a")
print("   lever: a Z presser on the hump moves the tip in Y by twice its own travel, which")
print("   gives a camera-measured axial correction without a Y axis on the conductor.")
