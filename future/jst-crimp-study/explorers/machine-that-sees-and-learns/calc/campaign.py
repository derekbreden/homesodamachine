"""The press that runs its own experiments (v3): how big a crimp-height campaign is, what it
consumes, how many samples a level needs, what force monitoring can and cannot see, and a
camera-read spring as a force gauge.

Explorer: machine-that-sees-and-learns. Run: python3 campaign.py > campaign.out.txt
"""
import math

print("=" * 76)
print("1. A crimp-height sweep for SXH-001T-P0.6 (or the kit clone) on the 22 AWG ribbon")
print("=" * 76)
# Estimated crimp height 0.69-1.12 mm, central 0.88; JST analogs 0.80 [xh-facts s1, calc C1].
levels = [round(0.70 + 0.02 * i, 2) for i in range(16)]
per_level = 5
print(f"  conductor crimp-height set points: {levels[0]:.2f} .. {levels[-1]:.2f} mm, step 0.02 -> {len(levels)} levels")
print(f"  {per_level} crimps per level -> {len(levels)*per_level} crimps, each pulled to failure")
extra = [("insulation-crimp settings, 6 levels x 3", 18),
         ("insertion depth / insulation-edge position, 5 levels x 3", 15),
         ("proof-then-destroy pairs at the chosen setting", 20),
         ("genuine SXH vs kit contacts at the chosen setting, 10 + 10", 20)]
total = len(levels) * per_level + sum(n for _, n in extra)
for name, n in extra:
    print(f"  + {name}: {n}")
print(f"  total ~{total} test crimps")
t_crimp = 2.5 * 60         # v1 cycle without the proof pull  [estimate, cycle_and_cost]
t_pull = 10 / 25.4 * 60    # 10 mm of travel at UL's 25.4 mm/min [source: Molex handbook via prior-art]
t_photo = 15
t_each = t_crimp + t_pull + t_photo
print(f"  per test: crimp {t_crimp:.0f} s + pull {t_pull:.0f} s + photos {t_photo} s = {t_each/60:.1f} min")
print(f"  campaign: {total*t_each/3600:.1f} h unattended (one or two nights)")
coupon_mm = 40
print(f"  wire: {total} x {coupon_mm} mm = {total*coupon_mm/1000:.1f} m of conductor "
      f"= {total*coupon_mm/1000/5:.1f} m of 5P ribbon")
print(f"  contacts: {total}; at LCSC reel-cut prices (~$0.01 each [xh-facts s6]) about ${total*0.01:.2f}")
print("  Person: strip the coupons (or let v6 strip them), load pallets, ~1 min per 5 coupons.")

print()
print("=" * 76)
print("2. How many crimps a level needs  [assumption: pull-out scatter sigma 2-5 N]")
print("=" * 76)
for sigma in (2, 3, 5):
    for n in (3, 5, 10):
        hw = 1.96 * sigma / math.sqrt(n)
        print(f"  sigma {sigma} N, n = {n:2d}: mean known to +/-{hw:4.1f} N (95%)")
    need = 39.2 + 3 * sigma
    print(f"    to keep mean - 3 sigma above JST's 39.2 N the mean must be >= {need:.1f} N")
print("  22 AWG breaks at ~85-100 N [xh-facts s1]: a crimp that breaks the wire instead of")
print("  pulling out is itself a strong result, and the camera sees which one happened.")

print()
print("=" * 76)
print("3. What crimp-force monitoring can see on 60 x 0.08 mm strands")
print("=" * 76)
strands = 60
one = 1 / strands
print(f"  one strand = {one:.1%} of the copper; a typical monitor's band is ~+/-4% [prior-art s6]")
for k in (1, 2, 3, 4, 6):
    print(f"    {k} strands missing -> {k/strands:.1%} less copper "
          f"({'inside' if k/strands < 0.04 else 'outside'} a 4% band, before scatter)")
print("  So the force curve catches: no wire, no contact, a doubled or misfed contact, insulation")
print("  under the conductor barrel, the wrong gauge, and drift in the peak over hundreds of")
print("  crimps. It does not catch a few cut strands; the camera at the stripped tip does, or")
print("  nothing does. [calc on prior-art numbers]")

print()
print("=" * 76)
print("4. A spring the camera reads, as the force gauge for pulls  [calc]")
print("=" * 76)
E_steel = 200e3  # MPa
def leaf(b, t, L):
    I = b * t ** 3 / 12
    k = 3 * E_steel * I / L ** 3
    return I, k
for (b, t, L) in ((12, 1.0, 20), (12, 1.5, 20), (12, 1.0, 30), (10, 0.8, 20)):
    I, k = leaf(b, t, L)
    for F in (25, 100):
        defl = F / k
        stress = F * L * (t / 2) / I
        print(f"  spring-steel leaf {b}x{t} mm, {L} mm long: k = {k:5.1f} N/mm; {F:3d} N -> "
              f"{defl:5.2f} mm, root stress {stress:4.0f} MPa")
for pxmm, lab in ((45, "ELP at 100 mm"), (122, "12 mm M12 lens at 100 mm")):
    _, k = leaf(12, 1.0, 20)
    res_mm = 0.2 / pxmm
    print(f"  read by {lab} ({pxmm} px/mm) at 0.2 px: {res_mm*1000:.1f} um -> {res_mm*k:.2f} N resolution")
print("  Spring steel yields at ~1,000-1,500 MPa [assumption, hardened 1075/1095 shim]. The")
print("  12x1x20 leaf suits ~25 N proof pulls (250 MPa); pulls to failure near 100 N want the")
print("  12x1.5x20 leaf (~440 MPa, 0.4 mm at 100 N). A $10 load cell and HX711 does the same job")
print("  with a wire instead of a picture; the leaf's merit is that it lives in the same frame as")
print("  the crimp, so one image holds both the force and whether the conductor slipped.")

print()
print("=" * 76)
print("5. Proof load in production")
print("=" * 76)
for frac in (0.5, 0.6):
    print(f"  {frac:.0%} of 39.2 N = {frac*39.2:.1f} N")
print("  Whether a ~20-24 N proof pull leaves a good crimp undamaged is an [assumption] the")
print("  campaign tests directly: proof-then-destroy pairs against destroy-only at one setting.")
