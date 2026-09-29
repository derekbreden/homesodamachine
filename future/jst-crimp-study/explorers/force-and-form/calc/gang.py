"""Ganged crimping of a whole ribbon end in one stroke (idea f5).

force-and-form explorer, jst-crimp-study, 2026-09-28.
Run:  python3 gang.py > gang.out.txt

How close the stations can sit, what the stroke costs, what an unbalanced
stroke does to a two-post die cassette, and whether one bad station shows in
the summed force. Inputs labelled; model family from stroke_model.py.
"""
from stroke_model import total_force

print("=" * 76)
print("1. Station pitch")
print("=" * 76)
ins_open = (2.46, 3.00)     # insulation barrel open width, clone drawings  [source S19-S22]
chan = (1.9, 2.0)           # insulation crimper channel width             [estimate from 1.8-2.0 crimp W]
wall = (0.8, 1.2)           # tool-steel side wall each side of the channel [estimate]
lo = chan[0] + 2 * wall[0]
hi = chan[1] + 2 * wall[1]
print(f"insulation crimper outer width {lo:.1f}-{hi:.1f} mm; open insulation wings {ins_open[0]}-{ins_open[1]} mm")
print(f"-> minimum station pitch ~{max(lo, ins_open[1]) + 0.3:.1f}-{hi + 0.3:.1f} mm with 0.3 mm air [estimate]")
print("-> 2.5 mm (the housing pitch) is impossible; 5.0 mm (every other cavity) fits;")
print("   the carrier strip's own pitch (unmeasured; 7-9.5 mm read off clone drawings)")
print("   fits with room to spare.")
for n in (3, 4, 5):
    for P in (5.0, 7.5, 9.0):
        span = (n - 1) * P
        move = (span - (n - 1) * 1.7) / 2
        print(f"  {n}P at {P:3.1f} mm pitch: span {span:4.1f} mm, outer conductor moves {move:5.2f} mm "
              "from its place in the ribbon")

print()
print("=" * 76)
print("2. Stroke force for a whole ribbon end")
print("=" * 76)
for n in (3, 4, 5):
    for case in ("central", "high"):
        F = n * total_force(0.0, case)
        print(f"  {n} stations, {case:7s}: {F/1000:5.1f} kN at BDC")
print("  VEVOR 12 t shop press ~118 kN [calc C1]; 1 t arbor press ~9 kN [source HF 59766]")
print("  -> the shop press does any ribbon end with huge margin; a 1 t arbor press does")
print("     3 stations at the high estimate, 5 at the central one only.")

print()
print("=" * 76)
print("3. Unbalanced stroke in a two-post cassette")
print("=" * 76)
post_spacing = 60.0     # mm between guide posts            [assumption]
engage = 20.0           # mm post engagement in bushing       [assumption]
clear = 0.010           # mm diametral clearance, plain bushing [assumption]
for n in (3, 5):
    for P in (5.0, 9.0):
        x_out = (n - 1) / 2 * P
        dF = 0.5 * total_force(0.0, "high")       # one outer station at half force [assumption]
        M = dF * x_out                            # N*mm
        side = M / post_spacing
        tilt = clear / engage
        dh = tilt * x_out
        print(f"  {n} st. at {P:3.1f} mm: outer station short by {dF:5.0f} N -> moment {M/1000:5.2f} N*m, "
              f"post side load ~{side:4.0f} N; clearance tilt at the outer station {1000*dh:4.1f} um")
print("  -> a two-post cassette with 10 um clearance keeps station-to-station height")
print("     within a few um; the stations' own die heights have to match to ~0.01 mm,")
print("     which means grinding the anvils as one block or shimming each [estimate].")

print()
print("=" * 76)
print("4. Does one bad station show in the summed force?")
print("=" * 76)
for n in (3, 4, 5):
    for keep in (0.4, 0.6):
        drop = (1 - keep) / n
        print(f"  {n} stations, one with no conductor keeping {int(keep*100)} % of its force: "
              f"sum drops {100*drop:4.1f} %")
print("  force without conductor, as a share of force with it, is unknown for XH")
print("  (\"headroom\"); 40-60 % is an assumption. Industrial monitors work in a ~+/-4 %")
print("  band [source: Assembly Magazine]. A summed signal sees a missing conductor")
print("  in a 3-station gang and probably a 5-station gang; it cannot say which one,")
print("  and it sees nothing finer. The camera, before the stroke, is the station check.")
