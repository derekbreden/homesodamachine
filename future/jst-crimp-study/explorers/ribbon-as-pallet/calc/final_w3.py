"""ribbon-as-pallet: numbers for the idea files as they finally stand.
Run: python3 final_w3.py > final_w3.out.txt
Cited in the idea files as [calc F §n].

Inputs are labelled where they are used:
  [xh]   context/xh-facts.md
  [pg]   calc/pallet_geometry.out.txt
  [W2]   calc/stations_wave2.out.txt
  [w3]   calc/exchange_on_force_and_form_w3.out.txt
  [P3]   ../procedure-is-the-machine/calc/exchange_ribbon_w3.out.txt
  [X]    ../borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt
  [est]  estimate; [asm] assumption
"""
import math

def hdr(n, t):
    print()
    print("=" * 78)
    print(f"{n}. {t}")
    print("=" * 78)

# ---------------------------------------------------------------------------
hdr(1, "Kinematic seats: contact stress at the balls, and which seat parts must be hardened")
# Hertz point contact. Re = sqrt(Rx*Ry); a = (3 F Re / (4 E*))^(1/3); p0 = 3F / (2 pi a^2)
def estar(E1, n1, E2, n2):
    return 1.0 / ((1 - n1**2) / E1 + (1 - n2**2) / E2)

def hertz(F, Rx, Ry, Es):
    Re = math.sqrt(Rx * Ry)
    a = (3 * F * Re / (4 * Es)) ** (1 / 3)
    p0 = 3 * F / (2 * math.pi * a * a)
    return a, p0

E_st, n_st = 210000.0, 0.30      # 52100 ball, case-hardened rod
E_ss, n_ss = 193000.0, 0.29      # 304 stainless dowel
Rb = 3.0                          # 6 mm ball
print("Preload P = the magnets' total pull on the pallet, 10-40 N [est: 3-4 N52 10x3 discs")
print("across a small gap]. Three balls share it; each ball bears on two faces.")
for P in (10.0, 40.0):
    # ball in a V of two 6 mm stainless pins, faces at 45 deg
    Fc = (P / 3) / (2 * math.cos(math.radians(45)))
    a, p0 = hertz(Fc, Rb, 1 / (1 / Rb + 1 / 3.0), estar(E_st, n_st, E_ss, n_ss))
    print(f"  P {P:4.0f} N, ball on two 6 mm 304 pins (Prime row: precision ground, NOT hardened):"
          f" {Fc:4.1f} N per contact, p0 {p0:5.0f} MPa")
    # ball on two touching 6 mm balls: contact normals 30 deg from vertical
    Fc2 = (P / 3) / (2 * math.cos(math.radians(30)))
    a2, p02 = hertz(Fc2, 1.5, 1.5, estar(E_st, n_st, E_st, n_st))
    print(f"  P {P:4.0f} N, ball on two touching 6 mm balls (all 52100):"
          f" {Fc2:4.1f} N per contact, p0 {p02:5.0f} MPa")
    # ball on two 8 mm case-hardened rods
    a3, p03 = hertz(Fc, Rb, 1 / (1 / Rb + 1 / 4.0), estar(E_st, n_st, E_st, n_st))
    print(f"  P {P:4.0f} N, ball on two 8 mm case-hardened chrome rods:"
          f" {Fc:4.1f} N per contact, p0 {p03:5.0f} MPa")
print("  first yield under a point contact at p0 ~ 1.6 x yield strength:")
print("    304 stainless 215-310 MPa annealed, ~500-700 cold-drawn [asm] -> yields at p0 ~350-1100 MPa")
print("    hardened 52100 / case-hardened rod ~60 HRC: static contact to ~4000 MPa (bearing static rating)")
print("-> the Prime stainless dowels dent under the balls at any useful preload (~1100-1700 MPa);")
print("   a seat of balls on ball pairs, or on cut lengths of case-hardened rod, stays elastic.")

# ---------------------------------------------------------------------------
hdr(2, "Backshell (a3): top above the board for each arrangement's parted length")
print("top = parted length + XHP mated height 9.8 + backshell 12 = parted + ~21.8 mm [X s7]")
rows = [
    ("fold-back parking (a3 with borrowed-machines b1/b4)", 8, 15),
    ("housing-pitch fan only", 14, 18),
    ("a1c or a2c at 5 mm crimp pitch, per ribbon", 17, 23),
    ("a2, a2e, a10 at ~7 mm strip pitch, per ribbon", 21, 30),
    ("a9: ~7.1 mm with the equal-path recession allowance", 22, 33),
    ("a1 with the tongue (5 mm pitch + 10-12 mm)", 30, 47),
]
for name, lo, hi in rows:
    print(f"  {name:55s} parted {lo:2d}-{hi:2d} mm -> top {lo+21.8:4.0f}-{hi+21.8:4.0f} mm")

# ---------------------------------------------------------------------------
hdr(3, "Proof pull: two load paths that keep the carrier and the tab out of it")
F = 20.0
# (a) blade in the neck, bearing on the box's rear face above the brush
box_w, box_h, t_wall = 1.87, 2.28, 0.20    # [xh s1 clone box 1.85-1.90 x 2.2-2.35; 0.20 stock]
z_blade = 1.2                               # blade stops 1.2 mm above the floor [P3 T3]
bear = box_w * t_wall + 2 * (box_h - z_blade) * t_wall
print(f"(a) blade in the neck bearing on the box's rear face from {z_blade} mm up:")
print(f"    wall edges in contact ~{bear:.2f} mm^2 -> {F/bear:.0f} MPa at {F:.0f} N (phosphor bronze yields ~450-650)")
print("    it needs the neck between box and conductor barrel, t, to take a ~0.3 mm blade [w3 s5]")
# (b) pad on the crimped barrels, pull taken by the tab in compression into slot pins
tab_w, tab_t = 0.8, 0.20
A = tab_w * tab_t
I = tab_w * tab_t**3 / 12
for L in (0.7, 1.15):
    Pcr = 4 * math.pi**2 * 110000 * I / L**2
    print(f"(b) pad down, tab {tab_w}x{tab_t} mm, {L} mm long, in compression: {F/A:.0f} MPa;"
          f" fixed-fixed buckling {Pcr:.0f} N")
print("    the pad (3.8-6.3 N [w3 s4]) stops the contact pitching about its tab; slot pins at")
print("    +/-3.55 mm hold the carrier to ~1 um [P3 s3]. End grips alone let a 2.5-3 mm carrier")
print("    bow 0.2-2.7 mm [P3 s3].")

# ---------------------------------------------------------------------------
hdr(4, "Docking when the open insulation barrel is narrower than the jacket")
print("Capture read from the clone drawings [P3 s2]: +0.51 mm a side if the drawn widths are inside")
print("widths; +0.01 mm worst if they are outside widths; -0.08 mm if JST's 1.95 mm envelope is the")
print("open wing. Placement error ~0.16 RSS, 0.32 worst [P3 s2].")
E_sil = (2.5, 5.5)            # MPa, Shore 50-70A via Gent [change-the-question]
L_ib = 1.2                    # insulation barrel length, mm [xh s1: 0.8-1.5]
for d in (0.05, 0.08, 0.15):
    k_sil = [E * L_ib for E in E_sil]              # N/mm per side, line indentation [est]
    wing_I = L_ib * 0.2**3 / 12
    k_wing = 3 * 110000 * wing_I / 2.8**3          # cantilever wing 2.8 mm tall
    ks = [1 / (1 / k + 1 / k_wing) for k in k_sil]
    f_side = [k * d for k in ks]
    push = [2 * f * (1 + 1.0) for f in f_side]     # two sides, mu ~1 on silicone
    print(f"  interference {d:.2f} mm a side: wing {k_wing:4.1f} N/mm, silicone {k_sil[0]:.0f}-{k_sil[1]:.0f} N/mm;"
          f" push to seat ~{push[0]:.1f}-{push[1]:.1f} N per conductor")
print("-> if docking has to press, a comb of fingers on the ribbon pallet pushes each jacket past")
print("   the wing tips with ~0.5-2 N (5-10 N for a 5P), taken by the shelf or rail under the")
print("   barrels, never by the tabs (which yield at 0.5-0.9 N at the box [X s5]).")

# ---------------------------------------------------------------------------
hdr(5, "Two consistent orders, and the length each leaves in the finished loom")
# recession of the outer conductor, compact R5/30 S, from [W2 s3]
rec = {  # (n, pitch): outer conductor's recession, compact R5/30 S [W2 s3]
    (3, 2.5): 0.11, (4, 2.5): 0.20, (5, 2.5): 0.31,
    (3, 5.0): 0.76, (4, 5.0): 1.20, (5, 5.0): 1.65,
    (3, 7.1): 1.32, (4, 7.1): 2.05, (5, 7.1): 2.77,
}
print("Order A: flush-cut and strip at the fan block face after the fan (a1, a2, a2e, a10).")
print("  Tips and insulation edges lie on one line in the crimp pose. The outer conductors are")
print("  longer than the centre one by their fan recession. Closed to 2.5 mm, and latched at one")
print("  depth, that excess stays in the loom: e = r(p) - r(2.5) for the outer conductor.")
for n in (3, 4, 5):
    for p in (5.0, 7.1):
        e = rec[(n, p)] - rec[(n, 2.5)]
        for S in (20.0, 30.0):
            h = math.sqrt(3 * S * e / 8)
            print(f"   {n}P fanned to {p} mm: outer excess {e:.2f} mm; over a {S:.0f} mm split"
                  f" a shallow arc stands {h:.1f} mm")
print("Order B: flush-cut and strip before the split (procedure-is-the-machine p7), then an")
print("  equal-path fan (humps in the inner grooves [P3 s1]) (a9). Every conductor is one length")
print("  from the root, so the finished loom carries no excess; the humps' set is pulled straight")
print("  by the insertion clamp's forward push.")
Mp = (0.31, 0.61)             # N mm, strand plastic moment [P3 C11]
for h in (2.6, 3.3, 5.1):
    print(f"   hump {h} mm: straightening tension ~M_p/h = {Mp[0]/h:.2f}-{Mp[1]/h:.2f} N")
print("Order C: one conductor at a time, each tip found by touch (a4 with a8, or a8b with a snout).")
print("  Any fan; each conductor's own Y is read and used. Excess as in order A if the fan is")
print("  closed afterwards.")
print("Housing pitch only (2.5 mm): recession 0.11-0.31 mm, and either order is the same.")

# ---------------------------------------------------------------------------
hdr(6, "Insertion from a fan closed to 2.5 mm: the natural staircase and what the load cell sees")
print("Fronts left free after closing (order A, or order B with the humps not pressed flat)")
print("[P3 s10]: 4P from 7.1: outer pair +1.85, inner pair 0; 5P from 7.1: outer +2.47, next +1.22,")
print("centre 0; from 5.0: 4P +1.00/0; 5P +1.34/+0.65/0.")
for n, steps in ((3, ["outer pair", "centre"]), (4, ["outer pair", "inner pair"]),
                 (5, ["outer pair", "next pair", "centre"])):
    print(f"  {n}P: latch events in order: " + ", then ".join(steps) +
          f"  ({len(steps)} events for {n} contacts)")
print("-> the load cell counts events, not contacts; a pair is two lances in one event.")
print("   The spring-limited pull-back and the camera confirm each contact.")

# ---------------------------------------------------------------------------
hdr(7, "Contacts per unit by arrangement (14 ribbon ends, 53 crimps, 55 conductors reaching housings)")
ends, crimps, reach = 14, 53, 55
cases = [
    ("grips in spare contacts' pilot holes: N+4", reach + 4 * ends),
    ("a2 / a10: N+2, trimmed positions snipped out", crimps + 2 * ends),
    ("a2e: grips in the carrier's end slots, segments cut in sequence (N+1)", crimps + ends),
    ("a9: from the reel, N per end (trimmed positions docked empty, not stroked)", reach),
]
for name, c in cases:
    print(f"  {name:75s} {c:3d} contacts; 8,000 reel ~{8000/c:4.0f} units; ${0.0235*c:.2f} at $0.0235")

# ---------------------------------------------------------------------------
hdr(8, "a9's parted length: strip pitch plus the equal-path recession allowance")
for n, base, r in ((3, 21, 1.32), (4, 25, 2.05), (5, 30, 2.77)):
    print(f"  {n}P: fan to ~7 mm {base} mm [pg s2] + {r} mm recession [W2 s3] -> {base + r:.0f} mm")
