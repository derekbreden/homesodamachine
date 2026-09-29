"""Numbers for p3 (terminate at the spool, cut last).

Run: python3 spool_test.py > spool_test.out.txt

1. Testing a finished XH end through the rest of the spool: resistance, what it can see.
2. How many turns the spool makes per unit (slip ring or tether).
3. Force to guillotine a ribbon (or a pair) after feed-out.
4. Length error of an encoder wheel riding on silicone.

Sources: 60 x 0.08 mm tinned copper per conductor, 0.302 mm^2 [calc C1 via xh-facts §7];
spool 15.24 m [repo]; ribbon use per unit by type [calc unit_inventory.out.txt];
Adafruit 736 slip ring, 6 circuits, 2 A, 300 rpm, $14.95 in stock 2026-09-28 [source].
"""

import math

RHO_CU = 1.72e-8     # ohm m, annealed copper at 20 C
TIN_FACTOR = 1.03    # tinned strands, a few percent higher [assumption]
A = 0.302e-6         # m^2


def section(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def main():
    section("1. Continuity through the spool")
    for L in (15.24, 8.0, 2.0):
        R = RHO_CU * TIN_FACTOR * L / A
        print(f"  {L:5.2f} m of one conductor: {R:.2f} ohm")
    print("  slip ring contact: tens to hundreds of milliohm [assumption; Adafruit does not state]")
    print("  -> open (infinite) vs good (<~1.5 ohm) is trivially separated by a GPIO + resistor")
    print("     divider or an ADC; adjacent short (a stray strand bridging two contacts) shows as")
    print("     a low resistance between two conductors that should read open.")
    print("  -> a crimp's own resistance (1-10 milliohm, 10-20 max per JST rating [mfr S1]) is")
    print("     invisible in series with ~0.9 ohm of spool; this test sees opens, shorts and")
    print("     which conductor went to which contact, not crimp quality.")

    section("2. Spool turns per unit, and over a spool's life")
    use = {"3P": 1.85, "4P": 2.80, "5P": 1.35}  # m per unit [calc unit_inventory]
    for D_hub, D_full in ((60.0, 140.0), (100.0, 160.0)):
        D_mean = (D_hub + D_full) / 2 / 1000
        print(f"  hub {D_hub:.0f} mm, full {D_full:.0f} mm (mean {D_mean*1000:.0f} mm) [assumption]:")
        for k, m in use.items():
            turns = m / (math.pi * D_mean)
            life = 15.24 / (math.pi * D_mean)
            print(f"    {k}: {turns:4.1f} turns per unit, {life:4.0f} turns per spool")
    print("  -> a lead from the spool's inner end would wind up 30-80 turns over a spool: a slip")
    print("     ring on the spool axle carries the test circuits (5 conductors on a 6-circuit ring).")

    section("3. Guillotine force, cutting the loom free after feed-out")
    for tau in (120e6, 200e6):  # shear strength of annealed/work-hardened copper strands [assumption]
        for n in (3, 4, 5, 9):
            F_cu = tau * A * n
            F_si = 2.0 * n  # silicone tears; a few newtons per conductor [assumption]
            print(f"  tau {tau/1e6:.0f} MPa, {n} conductors: straight blade ~{(F_cu+F_si):5.0f} N")
    print("  A scissor (angled) blade cuts one conductor at a time: ~40-65 N peak [calc, per conductor].")
    for lead_mm, T in ((8.0, 0.3), (2.0, 0.3)):
        F = 2 * math.pi * T * 0.3 / (lead_mm / 1000)
        print(f"  NEMA 17 at {T} N*m on a Tr8 lead {lead_mm:.0f} mm (eta 0.3): {F:.0f} N")
    print("  -> a Tr8x2 lead screw or a lever does a straight cut; an angled blade needs almost nothing.")

    section("4. Length by encoder wheel on silicone")
    for slip in (0.0, 0.005, 0.01, 0.02):
        for L in (100.0, 600.0):
            print(f"  slip {slip*100:.1f}%: {L:.0f} mm loom reads within {L*slip:.1f} mm")
    print("  plus wheel diameter error: a 20 mm wheel off by 0.1 mm is 0.5% [calc]")
    print("  -> +/-3-6 mm on the longest loom; compare with the service loop (Derek question).")


if __name__ == "__main__":
    main()
