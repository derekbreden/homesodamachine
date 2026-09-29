"""How sloppy a transfer may be when the station re-locates the carrier, and the tolerance chain
from the carrier's datum to the contact in the die.

Run: python3 transfer_capture.py > transfer_capture.out.txt

The idea tested: a person, a carousel, a conveyor or a cheap arm only has to deliver a cassette
within the capture range of the station's lead-ins; the station's own pins (or kinematic
grooves) then set position at the moment of work. Numbers are [estimate] unless labelled.
"""

import math


def section(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def main():
    section("1. What each transfer delivers, and what a lead-in captures")
    # A tapered dowel (30 deg half-angle cone) of tip diameter d_tip entering a hole D:
    for D, d_tip in ((4.0, 1.0), (6.0, 2.0), (8.0, 2.0)):
        cap = (D - d_tip) / 2
        print(f"  dowel into {D:.0f} mm hole, pointed to {d_tip:.0f} mm tip: captures +/-{cap:.1f} mm")
    print("  three balls into three printed V-grooves (Maxwell coupling): captures about +/- half")
    print("  the groove width, e.g. 8 mm grooves -> +/-3 mm; repeats to ~0.01-0.05 mm when the")
    print("  grooves are steel or hard inserts [estimate; principle from Wikipedia 'Kinematic coupling']")
    print()
    print("Transfer                               delivers (+/- mm)   note")
    rows = [
        ("person drops cassette in a nest", "2-5", "hands are fine at this"),
        ("carousel, NEMA17 + GT2 belt on rim, R=200", None, ""),
        ("carousel + spring ball detent", "0.1-0.3", "detent notch in rim"),
        ("linear belt conveyor, stepper", "0.5-1", ""),
        ("SO-101 class printed arm", "1-3", "[estimate]; hobby servos"),
        ("Dobot MG400", "0.05", "[source: Pololu listing, repeatability]"),
    ]
    R = 200.0
    ratio = 2 * math.pi * R / (20 * 2.0)  # rim belt length / 20T GT2 pulley circumference
    step_mm = (1.8 / ratio) * math.pi / 180 * R
    backlash_mm = 0.5  # belt stretch + tooth play at the rim [estimate]
    for name, d, note in rows:
        if d is None:
            d = f"{step_mm:.2f} step, ~{backlash_mm:.1f} play"
            note = f"rim ratio {ratio:.0f}:1"
        print(f"  {name:<38} {d:<19} {note}")
    print("-> every transfer above lands inside a +/-1.5-3 mm lead-in; none of them needs to be")
    print("   precise if the station lifts the cassette onto its own pins before it works.")

    section("2. Lateral chain: cassette datum -> conductor over the open contact")
    # allowed: strand bundle 0.69-0.74 into conductor barrel open 1.68-1.90 wide;
    # insulation 1.7 OD into insulation barrel open 2.46-3.00 wide [source, xh-facts §1, §7]
    allow_cond = (1.68 - 0.74) / 2
    allow_ins = (2.46 - 1.8) / 2
    print(f"allowed: strands into conductor barrel +/-{allow_cond:.2f} mm; insulation (1.7+0.1)")
    print(f"into the narrowest clone insulation barrel +/-{allow_ins:.2f} mm")
    chain = [
        ("station slide, lead screw, per step", 0.02),
        ("cassette on station dowels (steel pins in printed bores)", 0.05),
        ("comb slot 1.85 wide on a 1.7+/-0.1 conductor", 0.10),
        ("conductor tip wander, 8 mm stick-out, light touch", 0.20),
        ("contact on the anvil (strip track, pilot hole)", 0.05),
    ]
    worst = sum(v for _, v in chain)
    rss = math.sqrt(sum(v * v for _, v in chain))
    for n, v in chain:
        print(f"  {n:<58} +/-{v:.2f}")
    print(f"  worst case +/-{worst:.2f}, RSS +/-{rss:.2f} against +/-{allow_ins:.2f}")
    print("-> the free tip is the largest term; a fork or funnel closing 2-4 mm behind the strip")
    print("   line at the crimp station replaces it with that tool's own +/-0.05.")
    chain2 = chain[:3] + [("fork/funnel at the crimp station", 0.05)] + chain[4:]
    print(f"  with a fork: worst +/-{sum(v for _, v in chain2):.2f}, "
          f"RSS +/-{math.sqrt(sum(v*v for _, v in chain2)):.2f}")

    section("3. Axial chain: where the insulation edge lands between the barrels")
    print("window: insulation edge between conductor barrel and insulation barrel, strands")
    print("visible past the front of the conductor barrel; ~+/-0.3 mm usable [estimate from")
    print("clone barrel lengths ~1.25-1.5 mm and a ~0.5-0.8 mm window]")
    ax = [
        ("trim blade to cassette datum", 0.05),
        ("cassette to station", 0.05),
        ("strip length (V-jaw at 2.4 mm, slug tears)", 0.20),
        ("lift retraction scatter (s=20, h=8, split +/-3 mm)", 0.27),
        ("wire stop in the die (if used, replaces lift scatter)", 0.05),
    ]
    for n, v in ax:
        print(f"  {n:<58} +/-{v:.2f}")
    no_stop = ax[:4]
    with_stop = ax[:3] + [ax[4]]
    for label, c in (("no wire stop", no_stop), ("with a wire stop", with_stop)):
        print(f"  {label}: worst +/-{sum(v for _, v in c):.2f}, RSS +/-{math.sqrt(sum(v*v for _, v in c)):.2f}")
    print("-> the strip length and the split-point scatter matter most. Trimming and stripping")
    print("   in the pose the crimp uses (same station, same lift) removes the scatter term.")


if __name__ == "__main__":
    main()
