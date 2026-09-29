"""What a slow press can measure about each crimp, and how finely.

force-and-form explorer, jst-crimp-study, 2026-09-28.
Run:  python3 metrology.py > metrology.out.txt

1. Re-touch crimp height: after the stroke, back off, close again at a light
   force and read the punch-to-anvil gap with a gauge fixed across the dies.
2. Springback and die deflection: why the gap at peak force is not the crimp
   height, and why the re-touch is.
3. Which faults shift the force-position curve enough to see.
4. Stop-at-force versus stop-at-position.
Labels on every input; model family from stroke_model.py.
"""
from stroke_model import total_force, CASES

E_ST, E_CU = 200e3, 115e3          # MPa
A_CU = 0.3016                      # mm^2 copper, 60 x 0.08         [calc C1]
W = 1.5                            # mm crimp width                 [mfr analog SXA 22 AWG]
FILL = 0.83                        # outline area actually filled   [calc C1 est.]

print("=" * 76)
print("1. Re-touch crimp height")
print("=" * 76)
blade_k = 1.0 / (2 * 8.0 / (1.5 * 1.6 * E_ST))       # N/mm, two die blades, 8 mm free each
for F_touch in (5.0, 10.0, 20.0):
    print(f"re-touch at {F_touch:4.0f} N: die blades compress {1000*F_touch/blade_k:6.3f} um")
print("gauge options (gap measured across the dies, not through the frame):")
for name, res in (("0.001 mm digital indicator with data port", 0.001),
                  ("iGaging/Shahe capacitive scale (TouchDRO reads them on an ESP32)", 0.01),
                  ("stepper position through a 2 mm screw, 1/16 microstep", 0.000625)):
    print(f"  {name:66s}: {res*1000:6.2f} um resolution")
print("  a capacitive 0.01 mm scale resolves a fifth of the +/-0.05 mm band: coarse.")
print("  a 0.001 mm indicator resolves it 50 times over. Motor position counts the")
print("  drive, not the dies, and includes every stretch in between.")

print()
print("=" * 76)
print("2. Gap under load versus crimp height")
print("=" * 76)
for case in ("central", "high"):
    F = total_force(0.0, case)
    d_blade = F / blade_k
    # elastic recovery of the crimped section (bronze + compacted copper), as a block
    k_block = 0.5 * (E_ST * 0.55 + E_CU * 0.45) * W * 1.4 / 0.85  # N/mm, rough [estimate]
    d_block = F / k_block
    print(f"{case:8s} {F:5.0f} N: die blades {1000*d_blade:5.1f} um, crimp block recovery "
          f"~{1000*d_block:4.1f} um, lobe-shape springback 10-30 um [estimate]")
print("-> the gap at peak force reads 20-60 um low; the re-touch at 5-20 N reads the")
print("   crimp as the dies see it, within ~1 um of blade compression.")
print("   The punch arches touch the tops of the crimp lobes and the anvil touches the")
print("   floor: the same two surfaces a point-and-blade crimp micrometer measures")
print("   between, provided the crimp has not moved in the nest [assumption].")

print()
print("=" * 76)
print("3. Which faults move the curve, and by how much")
print("=" * 76)
dh_per_area = 1.0 / (W * FILL)   # mm of height per mm^2 of material in the barrel
faults = (
    ("one strand of 60 missing", A_CU / 60),
    ("six strands missing (10 %)", A_CU / 10),
    ("no conductor at all", A_CU / 0.92),
    ("0.5 mm of 0.49 mm wall silicone under the conductor barrel (strip short)",
     None),
)
for name, dA in faults:
    if dA is None:
        # insulation ring area over the barrel footprint: OD 1.7, bore ~0.72
        ring = 3.14159 / 4 * (1.7 ** 2 - 0.72 ** 2)
        frac_len = 0.5 / 1.45                           # 0.5 mm of a ~1.45 mm barrel
        dA = ring * frac_len
        sign = "+"
    else:
        sign = "-"
    dh = dA * dh_per_area
    print(f"{name:66s}: {sign}{dA:6.4f} mm^2 -> compaction onset {sign}{1000*dh:6.1f} um")
print()
print("Force at BDC, position-controlled, when compaction onset moves by dh:")
for case in ("central", "high", "steep"):
    F0 = total_force(0.0, case)
    for dh_um in (4.0, 30.0, 270.0):
        F = total_force(dh_um / 1000.0, case)
        print(f"  {case:8s}: onset {dh_um:5.0f} um later -> peak {F:5.0f} N vs {F0:5.0f} N "
              f"({100*(F-F0)/F0:+5.1f} %)  [upper bound: model is steep]")
print("Industrial crimp force monitoring: one strand of 7 is ~6.7 % of force, one of 19")
print("~2.5 % and not reliably seen [source: Assembly Magazine, in prior-art]. That is")
print("~0.47 x the copper fraction; for 1 of 60 strands it gives ~0.8 %.")
print("-> one missing strand is below any force signal here. Missing conductor, missing")
print("   contact, insulation in the barrel, a contact seated high or rolled: all move")
print("   the curve by tens of percent or tenths of a mm, and a slow press sees them.")

print()
print("=" * 76)
print("4. Stop at force versus stop at position")
print("=" * 76)
for case in CASES:
    F0 = total_force(0.0, case)
    k_c = (F0 - total_force(0.01, case)) / 0.01       # N/mm near BDC
    for frac in (0.10, 0.25):
        dh = frac * F0 / k_c
        print(f"{case:9s}: curve shifts by {int(frac*100):2d} % of force -> stop-at-force height moves "
              f"{1000*dh:5.1f} um (slope {k_c/1000:4.1f} kN/mm)")
print("-> if the real curve is as steep as the family, a force-limited drive (air")
print("   cylinder, current-limited motor) also lands inside +/-50 um. If the real")
print("   slope near BDC is 5 kN/mm, a 25 % shift moves it 80 um. The slope is the")
print("   first thing the logged curve tells you; the re-touch height is the check.")
