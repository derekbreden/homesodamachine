"""hand-tool-as-press, wave 3: numbers the settled idea files cite as [calc w3 §n].

Run:  python3 wave3.py > wave3.out.txt

Labels: [calc] worked here, [estimate], [assumption].
Other calc cited:
  [sl w3 §n]  machine-that-sees-and-learns calc/w3_on_hand_tool_as_press.out.txt
  [htq §n]    this explorer's calc/exchange_ctq_w3.out.txt
  [calc w2 §n] this explorer's calc/wave2.out.txt
  [ith ex §n] into-the-housing calc/exchange_hand_tool_as_press.out.txt
"""

import math


def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------------------
hr("1. a4 / a4b / a4c / a4d: where to set die contact when the frame is not rigid")
print("Model [calc]: eccentric e, angle phi before BDC, ram travel still to go d = e(1 - cos phi).")
print("Nominal die contact (zero load) is set y_c above BDC; s = y_c - d is travel past it.")
print("Crimp: force rises linearly over the last 0.2 mm of die gap to Fc at die contact [xh-facts §4].")
print("Frame loop k_f (shaft, bushings, holders, button cell) 15-30 kN/mm [estimate, sl w3 §6];")
print("disc stack preload P = 3.5 kN, rate k_s = 3 kN/mm [estimate]. Past P the loop is k_f in series with k_s.")
print()

P, KS = 3.5, 3.0          # kN, kN/mm
COMPACT = 0.2             # mm of die gap over which the crimp force builds


def force_at(s, Fc, kf):
    """Force (kN) at travel s (mm) past nominal die contact."""
    if s <= -COMPACT:
        return 0.0
    # before die faces meet: F = Fc(1 - g/0.2), g = -s + F/kf
    F = Fc * (1 + s / COMPACT) / (1 + Fc / (COMPACT * kf))
    if F < Fc and (F / kf - s) > 0:
        return max(F, 0.0)
    # faces meet: loop only
    if kf * s <= P:
        return max(kf * s, Fc) if kf * s >= Fc else Fc
    kser = 1 / (1 / kf + 1 / KS)
    return P + (s - P / kf) * kser


def stroke(e, yc, Fc, kf, n=4000):
    """Return F at BDC, peak torque (N*m) and its angle (deg), and whether the dies meet."""
    peakT, peakA = 0.0, 0.0
    meet = False
    for i in range(n + 1):
        phi = math.radians(40.0) * (1 - i / n)
        d = e * (1 - math.cos(phi))
        s = yc - d
        F = force_at(s, Fc, kf)
        g = -s + F / kf
        if g <= 1e-6 and F >= Fc - 1e-9:
            meet = True
        T = F * 1e3 * e * 1e-3 * math.sin(phi)   # N * m
        if T > peakT:
            peakT, peakA = T, math.degrees(phi)
    FB = force_at(yc, Fc, kf)
    return FB, peakT, peakA, meet


print("  e   Fc   k_f | y_c 0.15 (rigid-frame setting)          | y_c = P/k_f + 0.05 (stack engages)")
for e in (2.0, 2.5):
    for Fc in (1.5, 2.6):
        for kf in (15, 20, 30):
            FB1, T1, A1, m1 = stroke(e, 0.15, Fc, kf)
            yc2 = P / kf + 0.05
            FB2, T2, A2, m2 = stroke(e, yc2, Fc, kf)
            tag1 = "dies meet" if m1 else "dies DO NOT meet"
            eng1 = "stack engages" if FB1 > P else "stack idle"
            print(f"  {e:3.1f} {Fc:3.1f} {kf:4d} | F_BDC {FB1:4.2f} kN, {tag1:16s}, {eng1:13s} "
                  f"| y_c {yc2:5.3f}: F_BDC {FB2:4.2f} kN, peak {T2:4.2f} N*m at {A2:4.1f} deg")
print("  add 30-50 % for eccentric and ram-guide friction [assumption, calc §5]")
print("-> agrees with [sl w3 §6] in every row that matters: at 0.15 mm a 15-20 kN/mm loop keeps a")
print("   2.6 kN crimp's dies apart or leaves the stack idle, so height follows frame stiffness.")
print("   Set die contact 0.17-0.28 mm above BDC (P/k_f + 0.05); the BDC force is ~3.6 kN, the")
print("   peak shaft torque ~1.6-2.0 N*m before friction, ~2.0-3.0 N*m with 30-50 % friction.")
print()
print("  Drives against 2.0-3.0 N*m (with friction):")
drives = [
    ("NEMA 23 on hand (~1.0 N*m running) + 3:1 belt", 3.0 * 1.0 * 0.95),
    ("NEMA 23 + 10:1 planetary (Prime, 10 N*m permissible, 96 %)", min(10.0, 10 * 1.0 * 0.96)),
    ("5840-31ZY worm gearmotor, working", 2.3),
    ("Greartisan 40 kg*cm worm gearmotor (Prime), if 40 kg*cm is working torque", 40 * 0.0981),
    ("hand lever 150 mm on the shaft, 20 N at the grip", 0.150 * 20),
    ("hand lever 200 mm on the shaft, 20 N at the grip", 0.200 * 20),
]
for name, T in drives:
    verdict = "carries it" if T >= 3.0 else ("at the edge" if T >= 2.0 else "short")
    print(f"    {name:70s} {T:4.1f} N*m  {verdict}")
print("-> a hand lever on the eccentric shaft is a motorless first build of the die set: ~15-20 N at")
print("   a 150-200 mm lever, over ~40 deg of the last part of the turn [calc].")

# ---------------------------------------------------------------------------
hr("2. Side-entry stand-out with crimped neighbours (a2, a2b, a3)")
print("h = a + 1.05 (floor to axis) + 1.35 (crimped box above its axis) + 0.3 clearance = a + 2.7")
print("root radius R = L^2 / (3h), tip pull-back 0.6 h^2 / L  [ith ex §6 method]")
for a in (6, 9, 12):
    h = a + 2.7
    row = []
    for L in (20, 25, 35):
        row.append(f"L{L}: R {L*L/(3*h):5.1f}, pull-back {0.6*h*h/L:4.2f}")
    print(f"  a {a:2d}: h {h:4.1f} mm | " + " | ".join(row))
print("-> 8.7-14.7 mm of stand-out; R 9-47 mm, below the 67-78 mm at which the strands yield;")
print("   pull-back 1.3-6.5 mm. Matches [sl w3 §3].")

# ---------------------------------------------------------------------------
hr("3. The pull plate: what has to fit in the neck and what does not")
print("Crimped contact, end view, box 1.85-1.95 wide, walls 0.2 [xh-facts §1]; crimped conductor")
print("barrel ~1.5 wide and ~0.9 tall (crimp width 1.5 [mfr S14 analog], height ~0.88 [xh-facts §1]).")
box_w = (1.85, 1.95)
cb_w = (1.40, 1.60)
for bw in box_w:
    for cw in cb_w:
        free = (bw - cw) / 2
        print(f"  box {bw:.2f}, crimped barrel {cw:.2f}: the box's rear side-wall edges stand "
              f"{free:+.2f} mm outside the barrel each side")
print("  above the crimped barrel (z > ~1.1 mm) the box's rear edges (top wall, upper side walls)")
print("  face free space: a plate there can be any thickness and can be backed from behind.")
print()
print("Three plates, 20 N pull, two tines [calc; stress = 6 M / (b t^2)]:")
# (a) unbacked tines, cantilever 2-4 mm (calc w2 §2): 0.3 mm needed.
# (b) backer over the barrel to 1 mm above the floor: unbacked 1 mm; the lower side walls carry
#     their share of the 20 N.
area_total = 1.27
area_low = 2 * 0.2 * 0.9          # side walls from floor to ~1.1 mm
share = 20 * area_low / area_total
for t in (0.15, 0.20, 0.30):
    for b in (0.6, 1.0):
        M = (share / 2) * 0.5      # load centroid ~0.5 mm from the backer edge
        sig = 6 * M / (b * t * t)
        print(f"  (b) backer to 1 mm above floor: tine t {t:.2f}, width {b:.1f}: {share/2:4.1f} N each, "
              f"{sig:6.0f} MPa")
print("  (c) stepped plate: thick (0.5-1.0) and backed wherever it bears on the box outside the")
print("      barrel's width or above its height; thin only where it faces the barrel's front edge,")
print("      where it bears nothing. The neck then limits only the thin tongue, not the load path.")
for free in (0.05, 0.10, 0.25):
    print(f"      barrel inside the box by {free:.2f} a side -> backer clearance to the barrel side "
          f"{free:.2f} mm {'(tight)' if free < 0.1 else ''}")
print("-> [sl w3 §2 a6] holds for a flat plate: it needs a transition of ~0.35-0.5 mm.")
print("   A stepped plate needs only that the crimped barrel be narrower than the box by ~0.1 mm a")
print("   side and the box's rear edges be a clean step, not a sloped transition. The same neck")
print("   photo settles both [estimate]. In a crimp jig the contact is alone, so the space outside")
print("   the box is free.")

# ---------------------------------------------------------------------------
hr("4. a4c: the one-nest die set at C behind a tack station (checks of [sl w3 §7])")
pitch, up = 5.0, 5.0
for label, halfw in (("bare neighbour (jacket r 0.85)", 0.85), ("crimped neighbour's box (half 0.975)", 0.975)):
    for c in (0.0, 0.3):
        print(f"  free width for the punch between the two neighbours of k ({label}), clearance {c}: {2*pitch - 2*halfw - 2*c:4.2f} mm")
print("  neighbours' crimped boxes reach 5.0 + 1.35 = 6.35 above the working floor; their lance tips")
print("  hang to 5.0 - 1.05 - 0.9 = 3.05 above it [sl w3 §7]")
for bdc in (0.73, 0.90):
    print(f"  punch crimping edge at BDC {bdc:.2f}: narrow section reaches {6.35 + 0.3 - bdc:4.2f} mm above the edge")
print()
print("Passage of a tacked contact carried level under the open punch (floor lifted 1.0-1.7 mm):")
for e in (1.5, 2.0, 2.5):
    for bdc in (0.73, 0.90):
        opening = bdc + 2 * e
        tallest = 1.7 + 2.5      # lift + tacked barrel
        print(f"  e {e:3.1f}: punch open at {opening:4.2f}; tallest carried point {tallest:4.2f}: "
              f"clearance {opening - tallest:+5.2f} mm")
print("-> e 2.0-2.5 passes a tacked contact (+0.5 to +1.7 mm); agrees with [sl w3 §7].")
print()
print("Other order, 'C tacks for itself': lay-in under the open punch, part stroke to tack, look,")
print("finish. The waiting conductor's top is axis 5.0 + 0.85 = 5.85, plus 0-0.55 of curl [sl w3 §7]:")
for e in (2.5, 3.0, 3.5):
    for bdc in (0.73, 0.90):
        opening = bdc + 2 * e
        print(f"  e {e:3.1f}, BDC {bdc:.2f}: open at {opening:4.2f} -> clearance {opening - 6.40:+5.2f} to "
              f"{opening - 5.85:+5.2f} mm; torque x{math.sqrt(e/2.5):4.2f} of e 2.5")
print("-> e 3.5 opens room for the lay-in under the punch (+1.3 to +2.1 mm) at ~1.18x the torque of")
print("   e 2.5 (peak torque ~ F sqrt(2 y e) near BDC). The look is then oblique, under the punch.")

# ---------------------------------------------------------------------------
hr("5. The flag seat on the SN-2549 (a6b, a6c): jaw opening at the nest")
print("Flag carried level with its floor at h above the anvil; h >= lance 0.6-0.9 + 0.2 on entry,")
print("and the crimp needs a 1.0-1.7 mm lift before drawing back [ith ex §2]. Opening = h + the")
print("flag's tallest part above its floor + 0.2 margin [calc, as htq §4].")
parts = [("tool-made pre-form (a6b)", 2.3, 3.0), ("v8 tack (a6c)", 2.3, 2.5), ("open contact, for comparison", 2.75, 3.2)]
for h in (1.1, 1.4, 1.7):
    row = []
    for name, lo, hi in parts:
        row.append(f"{name} {h+lo+0.2:3.1f}-{h+hi+0.2:3.1f}")
    print(f"  h {h:.1f}: " + " | ".join(row))
print("  springs under the ledge and rear guide 1-3 N; the wings start to curl at tens of N [xh-facts §4],")
print("  so the punch seats the flag on the anvil before it forms anything [estimate].")
print("-> a flag needs ~3.6-4.9 mm of opening at the nest; the SN-2549's full opening is unmeasured.")
print()
print("What holds the flag on its wire against the person's push to the stop:")
print("  tool-made pre-form: 0.08-3.8 N [htq §2 model]; v8 tack: 0.2-1.5 N wanted, 0.4-9 N estimated")
print("  lance fold force 1-5 N [ith ex §3]: a flag dragged on the anvil loses its place on the wire")
print("-> green (box on the wired stop) means stop pushing; the seat carries the flag clear of the anvil.")

# ---------------------------------------------------------------------------
hr("6. a4d: one SN nest as a tongue under change-the-question c1c's pallet (checks of [htq §5])")
for nb, w in (("c6 round keyhole", 2.14), ("tool-made pre-form", 2.05), ("crimped insulation", 2.00)):
    print(f"  tongue allowed at 3.4 mm pitch beside a {nb} {w:.2f} wide, 0.1 clearance each side: "
          f"{2*(3.4 - w/2 - 0.1):4.2f} mm")
print("  walls either side of a 1.5-1.6 mm conductor arch in a 4.45 mm tongue: "
      f"{(4.45-1.6)/2:4.2f}-{(4.45-1.5)/2:4.2f} mm")
print("-> <= ~4.45 mm; a4's 6-8 mm one-nest cut does not fit here; its anvil becomes a <= 1.90 mm")
print("   HSS blade and crimp height comes from the stop alone.")

# ---------------------------------------------------------------------------
hr("7. Strip length follows the contact (a6's end jig, a2b, a1)")
for name, E, A in (("clone drawings", (1.25, 1.5), (0.5, 0.8)),):
    lo = E[0] + A[0] / 2 + 0.1
    hi = E[1] + A[1] / 2 + 0.2
    print(f"  {name}: S = E + A/2 + b = {lo:.2f}-{hi:.2f} mm (KONNRA clone spec 1.6-2.1 [digest])")
print("  JST 2.4 mm [mfr S6] implies a genuine conductor barrel of ~1.8-2.05 mm [sl w3 §4]")
print("-> the Klein stop is set from one measured contact of the lot in use, not from a figure.")
