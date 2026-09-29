"""change-the-question, wave 2 exchange on force-and-form: the numbers behind the critique.

Run:  python3 on_force_and_form.py > on_force_and_form.out.txt

Cited from exchange/change-the-question--on--force-and-form.md as "calc off §n".
Every input carries its label: [repo], [mfr], [source], [calc], [estimate], [assumption].
Force-and-form's own numbers are cited as [f&f calc: <file>].
"""

import math


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


RIBBON_PITCH = 1.7   # mm [source S29, xh-facts §7]
HOUSING_PITCH = 2.5  # mm [mfr S1]
T = 0.20             # contact stock thickness, mm [source S19-S21]
OD = 1.7             # insulated conductor OD, +/-0.1 [source S29]
BUNDLE = 0.72        # strand bundle diameter, mm [calc C1 §1]
WALL = 0.49          # silicone wall, mm [calc C1 §1]

# per-station crimp peak force, kN: low / central / high [f&f calc: stroke_model.out.txt §1]
F_STATION = {"low": 0.783, "central": 1.680, "high": 2.432}
ARBOR_1T_KN = 8.9    # Harbor Freight 1 t arbor press, 2,000 lbf [source via f&f f2b]

# ---------------------------------------------------------------------------
hr("1. Threading a 1.7 mm silicone conductor through a captured insulation barrel (f1, f3, f4)")
print("At capture the insulation wings sit inside the insulation crimper's channel, whose width")
print("is ~1.8-2.0 mm [mfr analog SXA-01T, f&f f3]. Inner clear width = channel - 2 x stock.")
print("Silicone must squeeze through it. Friction estimate: per-side normal force =")
print("E_si x (radial strain) x (barrel length x ~1.0 mm contact height); push = mu x 2 x N.")
print("E_si 2-5 MPa [estimate, Shore ~40-60A silicone]; mu 0.5-1.0 [estimate, silicone on tin];")
print("insulation barrel length 0.8-1.5 mm [estimate, xh-facts §1].")
for Wi in (1.8, 1.9, 2.0):
    inner = Wi - 2 * T
    for od in (OD - 0.1, OD, OD + 0.1):
        interf = max(0.0, od - inner)
        strain = (interf / 2) / WALL
        lo = 0.5 * 2 * (2.0 * strain * 0.8 * 1.0)
        hi = 1.0 * 2 * (5.0 * strain * 1.5 * 1.0)
        print(f"  channel {Wi:.1f} -> clear {inner:.2f} mm; OD {od:.1f}: interference {interf:.2f} mm, "
              f"wall strain {strain:4.0%}, push ~{lo:4.1f}-{hi:4.1f} N")
print("Buckling of the conductor under that push (strand-sum EI 14.1 N*mm^2 + silicone), pinned-pinned:")
print("  2 mm 37-41 N, 5 mm 5.9-6.5 N, 10 mm 1.5-1.6 N [source: sibling calc ribbon-as-pallet")
print("  pallet_geometry §4 and into-the-housing insertion_geometry §1]")
print("-> worst case (1.8 mm conductor into a 1.4 mm clearance) is ~6 N, the buckling load of a")
print("   5 mm free length. A guide within ~3 mm of the barrel mouth carries it with ~2x margin.")
print("   The repo's hand procedure already threads into a one-click-captured SN-2549 contact")
print("   [repo cable-assemblies.md], so some capture height exists where this works by hand.")
print("   The number to take from the bench is that capture gap (feeler or pin gauge at click 1).")

# ---------------------------------------------------------------------------
hr("2. f3: where the lead contact's pilot hole sits relative to the threading path")
for tab in (0.7, 1.15):           # tab between carrier edge and contact rear [estimate, xh-facts §1]
    for carrier_w in (3.0,):      # Wurth carrier width [mfr Wurth drawing]
        hole_c = tab + carrier_w / 2
        print(f"  tab {tab:.2f} mm, carrier {carrier_w:.1f} mm: pilot-hole centre {hole_c:.2f} mm behind the "
              f"insulation barrel, on the contact centreline; hole spans +/-0.75 mm across it")
print(f"  the insulated conductor ({OD} mm OD) slides on the carrier's top face, spanning +/-{OD/2:.2f} mm")
print("-> any pin standing above the carrier top in the lead contact's own hole is in the conductor's")
print("   path. Riding over a 0.3-0.5 mm pin tilts the conductor up by:")
for p in (0.3, 0.5):
    for d in (2.2, 2.65):
        print(f"     pin {p:.1f} mm proud at {d:.2f} mm behind the barrel: {math.degrees(math.atan(p/d)):4.1f} deg")

# ---------------------------------------------------------------------------
hr("3. f4: can the head leave a crimped contact, and can it pick one off the strip?")
box_w, box_h = 1.95, 2.4        # crimped contact end-view envelope [mfr S1]
diag = math.hypot(box_w, box_h)
funnel_exit = 2.0               # f4's funnel, 4 mm mouth tapering to 2 mm [f&f f4]
print(f"  crimped contact end view {box_w} x {box_h} mm, diagonal {diag:.2f} mm; funnel exit {funnel_exit} mm")
print("  -> a closed funnel round the conductor cannot pass back over the crimped contact, and a")
print("     downward move would take the funnel through the wire.")
open_knee = 5.0                 # knee opening stroke [f&f calc: drives §B, 'open 5 mm']
for Hc in (0.73, 0.88):
    roof = Hc + open_knee
    d_max = roof - box_h
    need = box_h - Hc + 0.3
    print(f"  crimp height {Hc:.2f}: opened crimper roof {roof:.2f} mm above the floor; the crimper is above the")
    print(f"     contact, so a downward head move closes on it after {d_max:.2f} mm and never frees it.")
    print(f"     An axial retreat (dies slide off past the box) needs an opening of only {need:.2f} mm.")
print("  At the pick, the carrier (3.0 mm wide, 0.7-1.15 mm tab) lies directly behind the insulation")
print("  barrel, where the head's rear funnel has to be. A funnel fixed to the head collides with it.")

# ---------------------------------------------------------------------------
hr("4. f5 x c1: a half-row cassette at 5.0 mm (twice the housing pitch)")
print("Half-rows (c1): odd cavities in one pass, even in the other. Each row's conductors lie at")
print("3.4 mm in their own plane (2 x ribbon pitch) and are spread to 5.0 mm (2 x housing pitch).")
print("A straight-descending V-tooth comb puts a conductor in the right slot if it moves < 2.5 mm")
print("(half the slot pitch); +/-0.2 mm lay uncertainty [estimate] is taken off the margin.")
for m in range(2, 6):
    move = (m - 1) / 2 * (5.0 - 3.4)
    margin = 2.5 - move - 0.2
    forces = "  ".join(f"{k} {m*v:4.1f}" for k, v in F_STATION.items())
    cover = "covers" if m * F_STATION["high"] <= ARBOR_1T_KN else ("central only" if m * F_STATION["central"] <= ARBOR_1T_KN else "no")
    print(f"  row of {m} cavities: outer conductor moves {move:.1f} mm, comb margin {margin:+.1f} mm; "
          f"gang force kN: {forces}; 1 t arbor press: {cover}")
for cw in (3.5, 4.4):
    print(f"  crimper outer width {cw} mm [f&f calc: gang §1] at 5.0 mm pitch: {5.0-cw:.1f} mm of steel between stations")
# rows per loom by cavity count (row A odd, row B even); crimps per row
ROWS = {  # loom: [(cavities in row, contacts crimped in row), ...] [repo cable-assemblies.md; ctq §2]
    "J1": [(5, 5), (4, 4)], "J2": [(3, 2), (3, 3)], "J3": [(2, 2), (2, 2)], "J4": [(4, 4), (3, 3)],
    "J5": [(2, 2), (2, 2)], "J6": [(3, 3), (2, 2)], "J7": [(4, 4), (3, 3)], "J9": [(2, 2), (2, 2)],
    "J11": [(2, 2), (2, 2)], "J13": [(2, 2), (2, 2)],
}
tot = sum(c for r in ROWS.values() for _, c in r)
le3 = sum(c for r in ROWS.values() for m, c in r if m <= 3)
eq4 = sum(c for r in ROWS.values() for m, c in r if m == 4)
eq5 = sum(c for r in ROWS.values() for m, c in r if m == 5)
strokes = sum(len(r) for r in ROWS.values())
print(f"  per unit: {strokes} row strokes, {tot} crimps; in rows of <=3 cavities {le3} ({le3/tot:.0%}), "
      f"rows of 4 {eq4} (J1 B, J4 A, J7 A), row of 5 {eq5} (J1 A)")
print("  -> a straight comb lays every T4, J2 and J6 row and the 3-rows of J4 and J7; the 4-rows")
print("     have ~0 margin and J1's 5-row fails, so those want a tilted or rolling comb.")
print("  Compare f5 at strip pitch: a 5P fans 30-38 mm, outer conductors move 12-15 mm [f&f calc: gang §1].")

# ---------------------------------------------------------------------------
hr("5. f5 branch: take every k-th conductor, which already sits near the strip pitch")
print("k x 1.7 mm against the carrier pitch (unmeasured for SXH; Wurth 7.10 [mfr]; clones 7-9.5 est.)")
for ps in (7.1, 7.5, 8.0, 8.5, 9.0, 9.5):
    best = min(range(3, 7), key=lambda k: abs(k * RIBBON_PITCH - ps))
    mis = best * RIBBON_PITCH - ps
    print(f"  strip pitch {ps:.1f}: every {best}th conductor ({best*RIBBON_PITCH:.1f} mm), mismatch {mis:+.1f} mm per pitch; "
          f"row of 3 outer moves {abs(mis):.1f} mm")
print("  rows available per ribbon end at k = 4: 3P -> 1+1+1; 4P -> 1+1+1+1; 5P -> 2+1+1+1;")
print("  J1 laid as 9 -> 3+2+2+2. The gang is small; what it buys is the strip kept as the pallet")
print("  with a fan of <= 1 mm instead of 12-15 mm, at the price of k strokes per ribbon end.")

# ---------------------------------------------------------------------------
hr("6. Reference crimp (c2): correcting a genuine JST lead's crimp height to the ribbon's copper")
a_rib = 60 * math.pi * 0.08 ** 2 / 4
print(f"  ribbon conductor: 60 x 0.08 mm = {a_rib:.3f} mm^2 [source S29]")
W = 1.5   # conductor crimp width, JST analog SXA-01T [mfr S14]
wings = (1.3 + 2 * 1.4) * T   # developed conductor-barrel width x stock [estimate from clone drawings]
for k in (0.80, 0.90):
    H = (wings + a_rib) / (W * k)
    print(f"  consistency: wings {wings:.2f} + copper {a_rib:.2f} mm^2 in a {W} mm wide B at fill {k:.2f} -> "
          f"H = {H:.2f} mm (the C1 estimate is 0.88)")
refs = {"22 AWG nominal": 0.324, "17/0.16 (JIS-style 22)": 17 * math.pi * 0.16 ** 2 / 4,
        "7/30 AWG (7 x 0.254)": 7 * math.pi * 0.254 ** 2 / 4, "19/34 AWG (19 x 0.160)": 19 * math.pi * 0.160 ** 2 / 4}
for name, a in refs.items():
    lo = (a - a_rib) / (W * 0.90)
    hi = (a - a_rib) / (W * 0.80)
    print(f"  reference lead {name:<24} {a:.3f} mm^2: same profile and compaction crimps the ribbon "
          f"{lo:.3f}-{hi:.3f} mm lower")
print("-> H_ribbon ~= H_ref - (A_ref - 0.302) / (1.5 x 0.8-0.9). Count the reference lead's strands")
print("   under the ELP camera and caliper one strand to get A_ref. The correction is 0.02-0.07 mm,")
print("   the same size as JST's +/-0.05 mm tolerance, so it cannot be ignored.")

# ---------------------------------------------------------------------------
hr("7. How often each arrangement calls the person back, per unit")
ENDS, CRIMPS, HOUSINGS = 14, 53, 10   # [repo via shared-context]
rows = [
    ("f1 as written (contact dropped per crimp)", ENDS + CRIMPS, "every 1-2 min through the run [f&f f3 cycle estimate]"),
    ("f1 + keyed stick magazine loaded at leisure", ENDS + 1, "53 contacts still handled, in one sitting"),
    ("f1 + strip dispenser and shear over the flap", ENDS, "reel every ~150 units"),
    ("f1 fed tacked ribbon ends from a c1b tack station", ENDS + 2 * HOUSINGS, "pallets loaded per half-row at the tack station"),
    ("f2, f3, f4 as written (strip fed)", ENDS, "plus a reel"),
    ("f5 as written, shop press pumped by hand", 2 * ENDS, "load, then pump"),
    ("f5 x c1 half-row cassette, loose contacts", HOUSINGS + 2 * HOUSINGS, "housing and ribbon, then pockets per row"),
]
for name, n, note in rows:
    print(f"  {name:<52} {n:>3} calls   ({note})")
print("-> loose-contact arrangements call the person once per row or per crimp; strip-fed ones once")
print("   per ribbon end. The contact's form sets the call count more than any mechanism does.")

# ---------------------------------------------------------------------------
hr("8. What a fork or pusher behind the crimped contact can bear on (f3 proof pull; c1 pusher)")
print("End view from behind. The wire behind the contact is uncrimped silicone, 1.7 +/-0.1 mm OD,")
print("its underside level with the barrel floor's inner face (0.2 mm up).")
Wi_rng = (1.80, 2.00)        # insulation crimp width [mfr S13, S14 analogs: 1.80; f&f f3: 1.8-2.0]
Hi = 1.80                    # insulation crimp height, 22 AWG [source: KONNRA clone spec, digest]
for Wi in Wi_rng:
    for od in (1.6, 1.7, 1.8):
        slot = od + 0.05     # a slot that lets the wire through
        side = (Wi - slot) / 2
        top = Hi - (T + od)
        print(f"  insulation crimp {Wi:.2f} wide x {Hi:.2f} tall, wire {od:.1f}: side rim beyond a {slot:.2f} mm slot "
              f"{side:+.3f} mm per side; crimp top vs wire top {top:+.2f} mm")
print(f"  floor's rear edge below the wire: {T:.2f} mm (and the tab stub, if cut)")
for Hc in (0.73, 0.88):
    for bh in (2.2, 2.4):
        print(f"  box rear face ({bh} tall, 1.9 wide) exposed above a {Hc:.2f} mm conductor crimp: {bh-Hc:.2f} mm; "
              f"above the {Hi:.2f} mm insulation crimp: {bh-Hi:.2f} mm")
print("-> behind the insulation barrel there is at most 0.03-0.18 mm of metal per side, none for a")
print("   1.8 mm wire in a 1.8 mm crimp, plus 0.2 mm of floor edge. A fork there bears mostly on")
print("   silicone. The box's rear face, reached from above in the space over the conductor crimp,")
print("   offers 1.3-1.7 x 1.9 mm of steel-to-bronze")
print("   bearing for a proof pull; its top 0.4-0.6 mm clears the insulation crimp for a pusher that")
print("   must withdraw straight back.")

# ---------------------------------------------------------------------------
hr("9. Delivery in cavity order (output pallet after a single-conductor crimper): J4 and J7 moves")
MAPS = {  # ribbon position -> cavity, least-crossing layouts [ctq §2, order_search.out.txt]
    "J4": {1: 1, 2: 5, 3: 3, 4: 4, 5: 2, 6: 6, 7: 7},
    "J7": {1: 1, 2: 2, 3: 3, 4: 4, 5: 7, 6: None, 7: 5, 8: 6},
}
for loom, m in MAPS.items():
    best = None
    for i in range(-600, 601):
        off = i / 100
        mv = {p: abs((c - 1) * HOUSING_PITCH + off - (p - 1) * RIBBON_PITCH) for p, c in m.items() if c}
        worst = max(mv.values())
        if best is None or worst < best[0]:
            best = (worst, off, mv)
    worst, off, mv = best
    lst = ", ".join(f"pos {p}->cav {m[p]}: {v:.1f}" for p, v in sorted(mv.items()))
    print(f"  {loom} (housing offset {off:+.2f} mm): {lst}")
    for split in (15, 20):
        print(f"     largest move {worst:.1f} mm over a {split} mm split: {math.degrees(math.atan(worst/split)):.0f} deg")
