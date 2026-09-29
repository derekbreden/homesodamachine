"""Where the contact and the conductor have to be, at which moment, and what
can put them there.

force-and-form explorer, jst-crimp-study, 2026-09-28.
Run:  python3 placement_budget.py > placement_budget.out.txt

The fixed reference throughout is the anvil (lower die). Windows are
[estimate] from clone drawings and crimp-quality rules in ../../../context/;
locator capabilities are [estimate] unless labelled.
"""
from math import degrees, atan

t = 0.20                      # stock thickness                        [source S19-S21]
wing_h = 1.55                 # conductor wing tip height above floor, open [source S19-S22, 1.50-1.60]
flare = (0.15, 0.30)          # punch entry flare/radius half-width     [estimate]
bundle = 0.72                 # strand bundle dia                       [calc C1]
u_inner = (1.30, 1.50)        # open conductor U inner width            [estimate: 1.68-1.90 outer - 2t]
ins_od = 1.7                  # insulation OD                           [source S29]
ins_inner = (2.06, 2.60)      # open insulation barrel inner width      [estimate: 2.46-3.00 outer - 2t]

print("=" * 76)
print("Contact relative to the dies (reference: anvil)")
print("=" * 76)
print(f"axial (along the wire): bellmouth target ~1x stock = {t:.2f} mm, acceptable ~1-2x")
print(f"  = {t:.2f}-{2*t:.2f} mm [mfr S5, MKS-L manual; source S23] -> contact axial window ~+/-0.1 mm")
for f in flare:
    print(f"lateral: the punch flare captures the wings if the contact is within +/-{f:.2f} mm")
    print(f"  roll about the contact axis: tip moves {wing_h:.2f} x angle -> limit "
          f"{degrees(atan(f / wing_h)):4.1f} deg")
print("vertical: floor seated on the anvil; a contact standing 0.1 mm proud meets the")
print("  punch 0.1 mm early and is flattened into a bend-up or roll [MKS-L manual 7-6..7-9]")
print("-> the contact needs +/-0.1 mm axially and +/-0.15-0.3 mm laterally at the moment")
print("   the wings enter the punch, and not before; after that the punch holds it.")

print()
print("=" * 76)
print("Conductor relative to the contact (reference: the contact, once captured)")
print("=" * 76)
for u in u_inner:
    print(f"lateral in the conductor U: bundle {bundle} mm in {u:.2f} mm -> +/-{(u-bundle)/2:.2f} mm free, "
          "walls centre it")
for w in ins_inner:
    print(f"lateral in the insulation barrel: {ins_od} mm in {w:.2f} mm -> +/-{(w-ins_od)/2:.2f} mm free")
print("axial: strip 2.4 mm [mfr S6]; brush visible past the conductor barrel, insulation")
print("  edge in the window between barrels ('about 50/50') [mfr S5] -> about +/-0.2-0.3 mm")
print("  on the tip position, plus strip-length error [estimate]")
print("vertical: all strands below the wing tips before the punch arrives; a strand")
print("  over a wing tip is crimped outside the barrel ('strands outside' fault) [mfr S5]")

print()
print("=" * 76)
print("What can place them (capability, [estimate] unless labelled)")
print("=" * 76)
rows = (
    ("carrier strip on a pilot pin (hole dia 1.5 [source S19])", "+/-0.03-0.06 axial and lateral"),
    ("applicator feed finger + guide plates + pressure plate", "set by screws; 'no movement front to back' [mfr MKS-L 6-6]"),
    ("steel nest walls + box against a stop (WC-110 flap style)", "+/-0.02-0.05"),
    ("printed locator clipped to a steel die (not loaded)", "+/-0.05-0.15, drifts with fit wear"),
    ("printer-class gantry (belts, steppers)", "+/-0.05-0.1 repeat"),
    ("vibration settling into a shaped pocket", "whatever the pocket is; needs a check"),
    ("person with tweezers", "+/-0.3; a stop or keyed slot then sets it, the partial close holds it"),
    ("taut conductor in a comb slot", "+/-0.1 lateral at the slot, worse 10 mm away"),
)
for a, b in rows:
    print(f"  {a:62s}: {b}")
print("-> steel or strip locates the contact; printed parts may guide, not set.")
print("   The conductor's windows are ~0.3 mm, a floppy wire's worst enemy is the")
print("   vertical one (strands over a wing tip), which a presser or the partial")
print("   close with axial threading removes.")
