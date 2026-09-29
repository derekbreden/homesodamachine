"""Stiffness of the force loop, and what it does to crimp height.

force-and-form explorer, jst-crimp-study, 2026-09-28.
Run:  python3 force_loop.py > force_loop.out.txt

Every candidate frame is a spring in series with the crimp. With a drive that
sets the ram position (crank, toggle, screw to a count), the crimp ends
F/k_loop higher than the drive's BDC, and F varies from crimp to crimp. With a
hard stop inside a stiff local loop (dies bottoming, or a stop block beside the
dies), the outer frame only has to push; its stretch becomes extra drive travel.
Numbers are beam estimates [calc] on assumed sections [assumption]; the point
is the order of magnitude and which loop decides crimp height.
"""
from math import pi

E_STEEL = 200e3     # MPa
E_CI = 110e3        # MPa, grey cast iron                  [source: handbook value]
E_PRINT = 3.0e3     # MPa, PETG/PET-CF as printed, in-plane [estimate; 2-6 GPa]


def c_frame(F, a, h, b, d, E):
    """Gap opening of a C-frame: throat depth a, back column height h,
    rectangular section b x d everywhere (mm). Bending of both arms and the
    column; shear and joints ignored (they add compliance)."""
    I = b * d ** 3 / 12.0
    return F * a * a / (E * I) * (h + 2.0 * a / 3.0)


def column(F, L, A, E):
    return F * L / (A * E)


print("=" * 76)
print("1. Loop stiffness, gap opening per kN (mm/kN), and at 2.4 kN")
print("=" * 76)
rows = []
# Printed C-frame, 30 x 40 mm solid section, 40 mm throat, 80 mm column
d = c_frame(1000.0, 40, 80, 30, 40, E_PRINT)
rows.append(("printed C-frame, 30x40 section, 40 mm throat", d))
d = c_frame(1000.0, 40, 80, 60, 50, E_PRINT)
rows.append(("printed C-frame, 60x50 section, 40 mm throat", d))
# Two 12.7 mm A36 plates (SendCutSend cuts A36 to 0.500 in) side by side, 60 mm deep
d = c_frame(1000.0, 40, 100, 2 * 12.7, 60, E_STEEL)
rows.append(("steel C-frame, 2 x 12.7 mm plate, 60 mm deep", d))
# Cast-iron arbor press: throat ~60 mm, column ~150 mm, section ~40 x 60  [assumption]
d = c_frame(1000.0, 60, 150, 40, 60, E_CI)
rows.append(("cast-iron arbor press body (assumed section)", d))
# Die blades: conductor punch/anvil as 1.5 x 1.6 mm blades, 8 mm free each [estimate]
d = 2 * column(1000.0, 8.0, 1.5 * 1.6, E_STEEL)
rows.append(("the two die blades themselves, 8 mm free each", d))
# Hand-tool jaws: SN-type jaws are EDM-cut plates on a pivoted head [estimate]
rows.append(("ratchet hand tool, jaws + pivots (guess, not measured)", 0.05))
rows.append(("  same, pessimistic guess", 0.15))
for name, dd in rows:
    k = 1.0 / dd
    print(f"{name:52s}: {dd:7.4f} mm/kN  (k ~{k:7.1f} kN/mm)  -> {2.4*dd:6.3f} mm at 2.4 kN")

print()
print("=" * 76)
print("2. Crimp-to-crimp height scatter under position control")
print("=" * 76)
print("Peak force varies crimp to crimp (strand count, contact hardness, stripping):")
print("take +/-10 % and +/-25 % of a 1.6 kN central peak [assumption]. Height scatter")
print("= dF / (k_loop + k_crimp), k_crimp = crimp's own slope near BDC (stroke_model")
print("gives 12-70 kN/mm). Crimp height tolerance to hold: +/-0.05 mm [mfr analog].")
for name, dd in rows:
    k_loop = 1.0 / dd
    # crimp-to-crimp shift of the crimp's own force curve by dF moves the final
    # height by dF / (k_loop + k_crimp); the loop alone bounds it by dF / k_loop
    vals = []
    for dF_frac in (0.10, 0.25):
        dF = 1.6 * dF_frac
        vals.append((dF / (k_loop + 30.0), dF / (k_loop + 12.0), dF / k_loop))
    (a1, b1, c1), (a2, b2, c2) = vals
    print(f"{name:52s}: +/-{a1:6.3f}-{b1:6.3f} mm at 10 %, +/-{a2:6.3f}-{b2:6.3f} mm at 25 %"
          f"  (loop-only bound {c2:6.3f})")
print("   (steel plate figure is bending only; bolted joints and pins add compliance, so")
print("   read it as tens to hundreds of kN/mm [estimate])")
print("-> scatter: the crimp's own steep curve near BDC carries most of the force change,")
print("   so even a printed loop scatters inside +/-0.05 mm IF its offset stays put.")
print("-> offset: a printed loop sits 0.2-0.85 mm open at peak force, and that offset")
print("   drifts with creep, temperature and humidity (PETG ~60-80 um/m/K, and a few %")
print("   creep of 0.85 mm is 0.02-0.04 mm) [estimate]. Steel loops stretch microns.")
print("   A printed loop is usable only with a hard stop in a steel local loop, or with")
print("   a per-crimp crimp-height measurement that re-sets the next stroke.")

print()
print("=" * 76)
print("3. Hard stop inside the local loop: what the outer frame then has to do")
print("=" * 76)
F_stop_margin = 0.5   # kN more than the crimp needs, so the stop is always reached
for name, dd in rows[:4]:
    extra_travel = (2.6 + F_stop_margin) * dd
    print(f"{name:52s}: extra drive travel to reach the stop at 3.1 kN = {extra_travel:5.2f} mm")
print("-> with a stop block beside the dies, a sloppy or springy outer frame only costs")
print("   drive travel. The crimp height is then set by the stop-to-anvil stack, which")
print("   is a few mm of steel (k in the hundreds of kN/mm).")
stack = column(1000.0, 10.0, 10.0 * 10.0, E_STEEL)
print(f"   e.g. a 10 x 10 mm steel stop, 10 mm tall: {stack*1000:.2f} um/kN")

print()
print("=" * 76)
print("4. Printed parts under the crimp force: stress, for the record")
print("=" * 76)
F = 2400.0
for name, area in (("printed anvil seat 10 x 10 mm", 100.0), ("printed seat 20 x 20 mm", 400.0),
                   ("wing tip on printed punch: 0.2 x 1.3 mm edge", 0.26),
                   ("insulation crimp 130 N over 1.9 x 1.2 mm", None)):
    if area is None:
        print(f"{name:52s}: {130.0/(1.9*1.2):6.1f} MPa mean (printed PET-CF compressive ~60-100 MPa"
              " [estimate]); tip line loads far higher")
        continue
    print(f"{name:52s}: {F/area:8.1f} MPa (printed polymer compressive ~50-100 MPa [estimate])")
print("-> printed faces can carry a spread-out seat under a steel die block, never a die")
print("   face; the insulation crimp is the only forming load within reach of polymer on")
print("   average, and its wing-tip contact still is not.")
