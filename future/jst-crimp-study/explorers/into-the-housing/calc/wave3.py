"""
Wave-3 numbers for the into-the-housing explorer.

Run:  python3 wave3.py > wave3.out.txt

Every input carries a label: [mfr], [source], [repo], [calc], [estimate],
[assumption]. Coordinates as in ../handover.md: Y along the contact (+Y toward
the mating face), X across the row, Z up (barrels open up, lance down).

[ctq w3 §n] = change-the-question's calc on this explorer,
../../change-the-question/calc/on_into_the_housing_w3.out.txt
[ith w2 §X] = ./wave2.out.txt
"""
import math


def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


PITCH = 2.50          # XH housing pitch [mfr S1]
WIRE = 1.70           # conductor OD [source S29]
WALL_SIL = 0.49       # silicone wall, nominal [calc C1 section 1]
EI_WIRE = 14.5        # N mm^2, strands + jacket [calc wave 1 section 1]
E_STEEL = 200e3
E_BRONZE = 100e3      # header pins: brass or phosphor bronze [assumption]

# ---------------------------------------------------------------------------
hr("A. The insulation step's mouth at 2.5 mm pitch, in every host that crimps in the row")
print("The stepped crimper's insulation step must swallow the insulation wings at first touch.")
print("Outer half-width needed = s/2 + m (capture margin) + l (wall land at the mouth), and that")
print("outer face passes down beside the neighbour. Available half-width depends on what lies")
print("beside the working axis at the insulation barrel's Y [ctq w3 section 1, reproduced]:")
print("   i2/K1, i1b, k6 (uncrimped side): a seated or waiting neighbour's 1.7 mm jacket: 2.5 - 0.85 = 1.65 mm")
print("   i2b pass 2, k6 (crimped side): a crimped insulation barrel ~2.0 wide:        2.5 - 1.00 = 1.50 mm")
print("   i2b pass 1: empty cavities both sides:                                          >= 2.5 mm")
spreads = [("pre-formed keyhole (c6), low", 1.96), ("pre-formed keyhole (c6), high", 2.14),
           ("clone open, drawing min", 2.46), ("clone open, typical", 2.80),
           ("clone open, drawing max", 3.00), ("clone open, max + tol", 3.25)]
cases = [("tight", 0.05, 0.05, 0.05), ("generous", 0.15, 0.10, 0.10)]
for avail_name, avail in (("beside a jacket (1.65)", 1.65), ("beside a crimped barrel (1.50)", 1.50)):
    print(f"\n   {avail_name}:")
    for name, s in spreads:
        row = []
        for cname, m, l, c in cases:
            need = s / 2 + m + l + c
            row.append(f"{cname}: need {need:4.2f}, margin {avail - need:+5.2f}")
        print(f"     {name:<32} s {s:4.2f}  " + " | ".join(row))

print("\nPush-aside (i2, i1b, k6's uncrimped side only): the step's outer face, with a lead-in")
print("chamfer on its neighbour side, moves the neighbour's jacket sideways by the shortfall.")
print("The neighbour's wire is held at its crimped insulation barrel (inside the cavity, 0.2-1.8 mm")
print("inside the rear face, section H) and at its saddle 10-20 mm back; the push lands at contact")
print("n's insulation barrel, 2.3-5.3 mm behind the rear face [estimate from box 1.4-2 mm deep and")
print("contact length 5.8-6.73 mm, source S19-S22]. Fixed-fixed beam, point load:")
for a in (2.5, 4.5, 7.0):          # mm from the neighbour's insulation barrel to the load
    for Lspan in (12.0, 20.0):      # mm, neighbour's barrel to its saddle
        b = Lspan - a
        for d in (0.10, 0.33):
            F = d * 3 * EI_WIRE * Lspan ** 3 / (a ** 3 * b ** 3)
            M_end = F * a * b ** 2 / Lspan ** 2
            R = EI_WIRE / M_end
            print(f"   load {a:3.1f} mm from the barrel, span {Lspan:4.1f}: push {d:.2f} mm -> {F:5.2f} N; "
                  f"root bend radius {R:6.1f} mm ({'sets a little' if R < 67 else 'elastic'})")
print("   Local indentation instead of bending: ~1 N on a 1.5 x 0.5 mm patch is ~1.3 MPa, strain")
print("   0.25-0.5 at E 2.5-5.5 MPa: 0.12-0.25 mm of the push can be taken by the jacket itself.")
print("   Line load on the jacket <~1 N over ~1.5 mm = <~0.7 N/mm, against a tear strength of 15-25 N/mm")
print("   [source Primasil, via ribbon-as-pallet]: a polished face with a lead-in does not cut it.")
print("   Friction drag on the neighbour, <~1 N toward -Z, is below the 5 N latch test.")
print("-> Beside a jacket, pushing it aside 0.10-0.33 mm costs 0.05-1.9 N (less where the jacket")
print("   indents) and, when the push is large and close to the housing, a slight set in the")
print("   neighbour's wire 2-7 mm behind the rear face, bent away from the working cavity. With that allowance the")
print("   step swallows every clone spread (need <= 1.98 mm, available 1.65 + 0.33). Beside a crimped")
print("   barrel (i2b pass 2, k6's crimped side) nothing yields: only pre-formed contacts, or kit")
print("   wings narrower than ~2.5 mm (tight) to ~2.2 mm (generous), fit.")

# ---------------------------------------------------------------------------
hr("B. Holding the camera-set tip until the crimper arrives (i2)")
print("The hump presser sets the tip's Y by pressing the saddle hump. If it lifts before the crimp,")
print("the hump's elastic share recovers and pulls the tip back. The most that recovery can push or")
print("pull along the wire is of the order of the hump's elastic buckling load:")
for L in (10.0, 15.0, 20.0):
    pinned = math.pi ** 2 * EI_WIRE / L ** 2
    clamped = 4 * pinned
    print(f"   hump chord {L:4.1f} mm, EI {EI_WIRE}: pinned {pinned:4.2f} N, clamped {clamped:4.2f} N")
print("   A keyhole bore grips the jacket axially at 0.2-4 N [change-the-question c6, w2 section 4].")
print("-> If the hump presser stays down through the stroke (it works 5-15 mm behind the dies, outside")
print("   their footprint), nothing recovers and the tip's Y is geometry: web clamp, pressed hump, tip.")
print("   The presser foot at the barrels must leave; it held Z, not Y. The conductor's lift at the")
print("   barrels is 1-44 mN [ctq w3 section 2], so a sprung hold-down pad in the insulation step's")
print("   channel (a few newtons, leading the walls by ~1 mm) keeps it down through first touch.")

# ---------------------------------------------------------------------------
hr("C. A box-nose stop that does not fight conductor-barrel growth (i2d, i2d'')")
print("Growth of the conductor barrel's front toward the box: 0.03-0.11 mm; the flow can push with")
print("80-520 N; the transition yields at ~90-310 N [ctq w3 section 3, estimates].")
nose_area = 1.7      # mm^2 box nose end face [ctq w3 section 3]
print("Preloaded stub: a spring holds the stub carrier -Y against the adjusting screw with preload P.")
print("The person's push (1-2 N [estimate]) never lifts it off; growth does, at force P.")
for P in (10.0, 20.0, 30.0):
    print(f"   P {P:4.1f} N: nose bearing on the PA6 face {P / nose_area:5.1f} MPa (PA6 yield ~50-90 [estimate]); "
          f"transition load {P:4.1f} N against 90-310 N yield")
print("Unpreloaded but compliant stub (no hard stop), stiffness k in Y:")
for k in (100.0, 250.0):
    for push in (1.0, 2.0):
        pass
    print(f"   k {k:5.0f} N/mm: the 1-2 N push moves the reference {1 / k:.3f}-{2 / k:.3f} mm; "
          f"growth 0.03-0.11 mm raises the force to {0.03 * k:4.1f}-{0.11 * k:4.1f} N")
print("-> A 10-30 N preload against the adjusting screw keeps the reference exact under the person's")
print("   push and gives way to growth at 6-18 MPa on the PA6 face, a third or less of its yield.")
print("   A steel pocket (i2d'') on a preloaded slide behaves the same. A rigid steel nose stop does not.")

# ---------------------------------------------------------------------------
hr("D. Roll of a box in a stub: clone boxes, and a floor shim that takes up height")
print("Small-angle roll of a W x H box in a channel C wide and D tall is the smaller of")
print("(C - W) / H and (D - H) / W.")
boxes = [("JST envelope", 1.95, 2.40), ("clone large", 1.90, 2.35), ("clone small", 1.85, 2.20)]
for name, W, H in boxes:
    for C in (2.00, 2.10):
        by_width = math.degrees((C - W) / H)
        print(f"   {name:<13} {W:.2f} x {H:.2f} in C {C:.2f}: width-limited roll +/-{by_width:4.1f} deg", end="")
        for gap in (0.05, 0.10):
            by_height = math.degrees(gap / W)
            print(f" | with height clearance {gap:.2f} (shim): +/-{min(by_width, by_height):4.1f} deg", end="")
        print()
print("-> Clone boxes roll up to +/-6.5 deg in a loose cavity, above the 5 deg low end of the 5-11 deg")
print("   window [digest]. A stencil-foil shim on the stub's floor (0.05-0.10 mm of height clearance")
print("   left) limits roll to +/-1.5-3.1 deg whatever the width clearance, and it touches only the box.")

# ---------------------------------------------------------------------------
hr("E. Contact length spread in a gang push (i6, i6b, i3)")
print("Clone drawings: 5.8 / 6.2 / 6.73 / 5.9 mm, each +/-0.25 [source S19-S22]; within a lot unknown.")
print("A rigid backing blade sets every rear on one line; the longest contact bottoms first.")
print("Two repairs:")
print(" (1) Tines on constant-force springs at 1.25 x single insertion: each rides back after it bottoms.")
for n, name in ((4, "XHP-4"), (7, "XHP-7"), (9, "XHP-9")):
    for Fi in (9.8, 15.0):
        P = 1.25 * Fi
        print(f"     {name}: preload {P:4.1f} N each, all bottomed: {n * P:6.1f} N on the nest cell")
print("     Ride-back = spread + overtravel; the conductor stores it as a bow over its split:")
for s in (0.1, 0.25, 0.5):
    for c in (20.0, 30.0):
        h = math.sqrt(3 * c * s / 8)
        print(f"       ride-back {s:.2f} mm over a {c:4.1f} mm split: bow height ~{h:3.1f} mm")
print(" (2) Push to the first wall, then one finishing tine visits each cavity and pushes that contact")
print("     to its own wall with a force ceiling, logging fold, snap and wall per contact. The extra")
print("     travel is the spread (<= ~0.5 mm), drawn from the conductor's bow; the target comb drops")
print("     away first so its slot grip (1.4-20 N, section G) is not added to the push.")
print("-> (2) needs one tine and the stage that already exists; (1) needs a spring per tine at 2.5 mm")
print("   pitch. Flat constant-force coils are wider than 2.5 mm [assumption], so they stagger in")
print("   3-4 rows or act through push-wires.")

# ---------------------------------------------------------------------------
hr("F. i6b post bed: where the post is supported, and 2.54 against 2.50")
I_sq = 0.64 ** 4 / 12.0
print("A post pressed into a PCB at the mating face passes the housing's front-wall post opening,")
print("then the open cavity (2.0 mm wide), then stands 8.5 mm out of the rear face. With nothing at")
print("the rear face, its free length from the front wall to the tip is ~7.1 + 8.5 = 15.6 mm")
print("[housing 7.75 mm, mfr S2; front wall ~0.6 mm, assumption].")
for label, L in (("unsupported, front wall to tip", 15.6), ("support comb at the rear face", 8.5),
                 ("support comb 3 mm below the tip", 3.0)):
    for mat, E in (("steel", E_STEEL), ("bronze", E_BRONZE)):
        k = 3 * E * I_sq / L ** 3
        print(f"   {label:<34} {mat:<6} free {L:4.1f} mm: {1 / k:6.3f} mm per N")
d_round = 0.635
I_round = math.pi * d_round ** 4 / 64
for L in (15.6, 8.5, 3.0):
    k = 3 * E_STEEL * I_round / L ** 3
    print(f"   round music wire 0.635 (K&S 5005)  free {L:4.1f} mm: {1 / k:6.3f} mm per N")
print("Threading at 0.5-1 N of side load against a +/-0.2 mm capture:")
for L in (15.6, 8.5, 3.0):
    k = 3 * E_BRONZE * I_sq / L ** 3
    print(f"   bronze, free {L:4.1f}: {0.5 / k:5.3f}-{1.0 / k:5.3f} mm")
print("-> Unsupported, the posts are useless for threading (0.45-0.9 mm per N). A slotted stencil-steel")
print("   support comb that slides in along X near the post tips, and withdraws in Z after every box")
print("   is on, makes the material irrelevant and puts the tips at the comb's laser-cut pitch.")
print("2.54 against 2.50 mm, first to last post (intervals = n - 1):")
for n in (4, 5, 6, 7, 9):
    err = (n - 1) * 0.04
    print(f"   XHP-{n}: {err:.2f} mm end to end, +/-{err / 2:.2f} mm if centred")

# ---------------------------------------------------------------------------
hr("G. Silicone modulus from Shore 50-70A (E 2.5-5.5 MPa, Gent), in this explorer's own models")
print("[ith w2 D] slot grip, [ith w2 F] jacket share, re-run at the sourced range.")
for E in (2.5, 3.6, 5.5):
    for slot in (1.50, 1.60):
        squeeze = (WIRE - slot) / 2
        strain = squeeze / WALL_SIL
        p = E * strain
        for Lg in (6.0, 10.0):
            N = 2 * p * Lg * 0.9
            print(f"   slot grip: E {E:3.1f}, slot {slot:.2f}, length {Lg:4.1f}: axial hold {0.5 * N:5.1f}-{1.0 * N:5.1f} N")
for Lf in (2.0, 3.0):
    kb = 12 * EI_WIRE / Lf ** 3
    for E in (2.5, 3.6, 5.5):
        ks = 2 * E * (2.0 * 1.0) / WALL_SIL
        share = kb / (kb + ks)
        print(f"   jacket share: free {Lf:.0f} mm, E {E:3.1f}: {share * 100:3.0f} % of a grip-to-anvil mismatch")
print("-> slot hold 1.4-20 N; jacket share 33-52 % over 2 mm and 13-24 % over 3 mm. Neither changes a")
print("   conclusion: the blade still reacts the push; fingers still go loose for the stroke.")

# ---------------------------------------------------------------------------
hr("H. Seated rear depth and the finishing blade's reach")
print("Rear inside the rear face = housing 7.75 [mfr S2] - front wall 0.4-0.8 [assumption] - contact length.")
for Lc_name, Lc in (("HDGC 5.8 - 0.25", 5.55), ("HDGC 5.8", 5.8), ("JST 6.1", 6.1), ("JST 6.5", 6.5),
                    ("CJT 6.73", 6.73), ("CJT 6.73 + 0.25", 6.98)):
    lo = 7.75 - 0.8 - Lc
    hi = 7.75 - 0.4 - Lc
    print(f"   {Lc_name:<16}: rear {lo:5.2f} to {hi:5.2f} mm inside the rear face")
print("-> 0 to 1.8 mm. Finishing blades reach up to ~2 mm into the cavity; the kit's own contact and")
print("   housing, measured once, fix it for this bench.")

# ---------------------------------------------------------------------------
hr("I. k8 (c1c + i6): pallet A swinging into the working plane over sorted row-B conductors")
print("Sorted conductors run from the root (Z = 0) down to the target row (Z = -h) over the span; at a")
print("fraction f of the span they are f*h below the working plane. A carrier body reaches d_c below")
print("the plane; a wire's radius is 0.85 mm. Clear when f*h > d_c + 0.85 + 0.3.")
for h in (4.0, 6.0, 8.0):
    for dc in (1.0, 2.0):
        fmin = (dc + 0.85 + 0.3) / h
        print(f"   drop h {h:3.1f} mm, carrier depth {dc:3.1f}: pallet must sit at f > {fmin:4.2f} of the span")
print("-> A pallet parked up and back reaches the working plane from above and never sweeps the")
print("   sorted conductors; once there, shallow carriers near the tips clear them for h >= ~6 mm.")
print("   Parked down and back (c1c as drawn), its arc sweeps the space in front of and below the")
print("   root, where every sorted conductor lies.")

# ---------------------------------------------------------------------------
hr("J. k7: what the pre-formed contact does at 2.5 mm, and the snap's load path")
print("Pre-formed insulation barrel: keyhole outside 1.96-2.14 mm, bore 1.55-1.60, throat 1.3-1.5")
print("[change-the-question c6, w2 section 2]. Height of the keyhole's top above the barrel floor's")
print("underside ~ floor 0.2 + bore 1.6 + wing 0.2 = ~2.0 mm [estimate], against 2.75-3.20 open")
print("[source S19-S22] and 1.50-1.60 for the conductor wings.")
for s in (1.96, 2.14):
    for m, l, c in ((0.05, 0.05, 0.05), (0.15, 0.10, 0.10)):
        need = s / 2 + m + l + c
        print(f"   keyhole {s:.2f}: need {need:4.2f}; beside a jacket margin {1.65 - need:+.2f}, beside a crimped barrel {1.50 - need:+.2f}")
print("   Loading an even cavity between crimped odds (gap = 2.5 - s/2 - 1.0):")
for s in (1.96, 2.14, 2.46, 2.80, 3.00, 3.25):
    print(f"     spread {s:.2f}: gap {2.5 - s / 2 - 1.0:+.2f} mm")
print("Snap: 0.5-20 N down on the jacket over the insulation barrel [c6 w2 section 4]. The anvil")
print("must be under the insulation barrel too. Its front edge sits behind the lance tip (2.24-2.64 mm")
print("behind the contact's front [source S22]); the insulation barrel is ~4.3-5.7 mm behind the front")
print("[estimate], so the snap lands 1.7-3.5 mm behind the anvil's front edge, and the lance carries none.")
print("Bore grip 0.2-4 N against the hump's elastic push (section B): with the hump presser held down")
print("the bore need only resist the crimper's first touch, which the steel flare and walls take.")
