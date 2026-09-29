"""Final-pass numbers for machine-that-sees-and-learns: the tack defined against the final
insulation crimp, the tack drive and its load cell, per-unit times, the hand-pumped tack
station on an applicator (v9b), and why the applicator's own ram is not the tacker.

Explorer: machine-that-sees-and-learns. Run: python3 w3_final.py > w3_final.out.txt

Labels: [calc] worked here; [estimate]; [assumption]. Inputs carry their sources.
  [xh-facts]  ../../../context/xh-facts.md (clone drawings, S19-S22)
  [ff w2 s5]  force-and-form calc/wave2.out.txt s5 (insulation crimp on silicone, tack grip)
  [sl w3 s9]  this explorer's w3_on_hand_tool_as_press.out.txt s9 (insulation height on silicone)
  [sl w2 s5]  this explorer's wave2.out.txt s5 (first touches, tack forces)
  [bm W sn]   borrowed-machines calc/exchange_sees_learns_w3.out.txt
"""

def rng(a, b, fmt="{:.2f}"):
    return f"{fmt.format(a)}-{fmt.format(b)}"

print("=" * 78)
print("1. The tack, defined against the final insulation crimp at the same contact")
print("=" * 78)
OD = (1.6, 1.7, 1.8)          # jacket OD, 1.7 +/-0.1 mm [xh-facts s7]
t = 0.20                      # stock thickness [xh-facts s1]
Wf = (1.80, 1.95)             # final insulation crimp width on this silicone [ff w2 s5; sl w3 s9]
Hf_sets = {"force-and-form 2.0-2.3 [ff w2 s5]": (2.0, 2.3),
           "ellipse upper bound 2.03-2.46 [sl w3 s9]": (2.03, 2.46),
           "KONNRA PVC-wire figure 1.8-2.1 [sl w2 s5 input]": (1.8, 2.1)}
wing_open_H = (2.75, 3.20)    # insulation barrel open height [xh-facts s1]
cond_first_touch = (0.62, 0.87)  # conductor wings meet their crimper [sl w2 s5]
compaction = (0.10, 0.20)     # last part of the stroke [digest]
# Grip of a barrel squeezing the jacket: 0.4-3.1 N at 10 %, 1.1-9.4 N at 30 % [ff w2 s5];
# taken as roughly proportional to squeeze: 0.037-0.31 N per % [calc, fit to both rows].
g_lo, g_hi = 0.037, 0.31

print("Lateral squeeze of the jacket by a closed barrel of outside width W (inside W - 2t):")
for dW in (0.0, 0.1, 0.2):
    sq = []
    for W in Wf:
        for od in (OD[0], OD[2]):
            s = max(0.0, 1 - (W + dW - 2 * t) / od) * 100
            sq.append(s)
    smin, smax = min(sq), max(sq)
    print(f"  former width = final width + {dW:.1f} mm: squeeze {smin:4.1f}-{smax:4.1f} % "
          f"-> grip ~{g_lo*smin:.2f}-{g_hi*smax:.1f} N  [estimate]")
print("  wanted: 0.2-1.5 N (carries a 0.043 g contact through handling, slides off for a back-out)")
print("  -> at the final crimper's own width the lateral squeeze alone is ~3-22 %, which the")
print("     thin-layer model puts at up to ~7 N: a tack there can exceed the release target.")
print("     A former 0.1-0.2 mm wider than the final crimper brings the squeeze to 0-17 % or 0-11 %;")
print("     the grip then comes more from the wing tips on the jacket's top, set by height. The")
print("     spread is the grip model's (x8) and the jacket's +/-0.1 mm; the bench finds the setting.")
print("     The final crimper's mouth must then take a barrel 0.1-0.2 mm wider than its own width")
print("     [assumption: a flared B-crimper entry does; the jack test or f3b's sections show it].")
print()
print("Tack height H_t = H_f + dH, dH = 0.2-0.5 mm above the final insulation height at that width:")
for name, (h1, h2) in Hf_sets.items():
    print(f"  final {name}: tack {h1+0.2:.2f}-{h2+0.5:.2f} mm")
print("  (an absolute 2.3-2.5 mm tack lies -0.16 to +0.47 mm from the 2.03-2.46 final heights, so")
print("   at the low end it is the crimp, not a tack [bm W s1]; the relative definition cannot be)")
print()
print("First touches, remaining ram travel (both crimpers on one ram):")
for name, (h1, h2) in Hf_sets.items():
    a, b = wing_open_H[0] - h2, wing_open_H[1] - h1
    print(f"  untacked, final {name}: insulation wings met at {a:+.2f} to {b:+.2f} mm; "
          f"conductor wings at {cond_first_touch[0]:.2f}-{cond_first_touch[1]:.2f} mm")
print(f"  after a tack at H_f + 0.2-0.5: the insulation crimper meets the tacked barrel with 0.20-0.50 mm")
print(f"  left, always after the conductor wings ({cond_first_touch[0]:.2f}-{cond_first_touch[1]:.2f} mm).")
lo = cond_first_touch[0] - 0.5; hi = cond_first_touch[1] - 0.2
print(f"  the conductor wings curl for {lo:.2f}-{hi:.2f} mm of stroke before the insulation crimper retouches;")
print(f"  compaction ({compaction[0]:.1f}-{compaction[1]:.1f} mm) starts with the retouch or after it.")
print("  -> in both strokes the jacket is held before compaction. The untacked order (insulation")
print("     first) holds only where the final insulation height is low; on this silicone it can be")
print("     either. After a tack, the conductor wings are always met first.  [calc, clone dims,")
print("     crimper mouth flare not modelled]")

print()
print("=" * 78)
print("2. The tack drive and where its load cell sits")
print("=" * 78)
servo_Nm = 35 * 9.81 / 100    # DS3235 35 kg.cm [Prime row]
for horn in (0.020, 0.025):
    for lever in (1.0, 2.0, 3.0):
        print(f"  35 kg.cm servo, {horn*1000:.0f} mm horn, lever {lever:.0f}:1 -> {servo_Nm/horn*lever:5.0f} N at the former")
print("  forming force wanted 33-132 N [sl w2 s5, from xh-facts C1 s4]")
cells = {"5 kg bar (Prime pair, $9.99)": 5, "10 kg bar": 10, "20 kg bar": 20}
for n, kg in cells.items():
    F = kg * 9.81
    print(f"  {n}: rated {F:4.0f} N, ~{1.5*F:4.0f} N safe overload [assumption: 150 % typical]")
print("  -> bench T (v8): the cell under the nest insert reads only the forming force, because the")
print("     loose stop carries the servo's excess; 20 kg covers 132 N.")
print("  -> T at the applicator (v9): the anvil is the applicator's own block, so the cell sits in")
print("     the T-arm's link and reads servo force. The forming curve is the trace up to the knee")
print("     where the former lands on its stop; after the knee it reads the servo's excess. With a")
print("     1:1 lever the excess tops out at 137-172 N, inside a 20 kg cell's overload.")

print()
print("=" * 78)
print("3. Per-conductor and per-unit machine time  [estimate]")
print("=" * 78)
rows = [("v8  bench T, then C (v1-type press)", 29 + 40, 81 + 80, "T 29-81 s [sl w2 s5] + C 40-80 s"),
        ("v8b T, then a4's one-nest die set", 66, 144, "[sl w3 s7, W1]"),
        ("v9  tack at the anvil of a crank applicator", 72, 142, "[bm W s11]")]
for name, a, b, src in rows:
    print(f"  {name:48s} {a:4d}-{b:4d} s a conductor; {53*a/3600:.1f}-{53*b/3600:.1f} h a unit   {src}")

print()
print("=" * 78)
print("4. v9b: the tack by hand on the jack-test applicator, person time  [estimate]")
print("=" * 78)
# A 12 t bottle jack: pump plunger 10-14 mm, ram 40-55 mm, plunger stroke 15-25 mm [assumption].
best = (25 * (14 / 40) ** 2)
worst = (15 * (10 / 55) ** 2)
print(f"  ram travel per pump stroke: {worst:.2f}-{best:.2f} mm")
for stroke in (30, 40):
    print(f"  applicator stroke {stroke} mm: {stroke/best:.0f}-{stroke/worst:.0f} pump strokes, "
          f"~{stroke/best*0.8:.0f}-{stroke/worst*1.0:.0f} s")
steps = [("lay the conductor into the waiting contact by hand, foot on", 10, 20),
         ("throw the toggle: former closes the insulation wings to its stop", 2, 4),
         ("look: ELP preview through the swing mirror, two LEDs in turn", 5, 15),
         ("pump the jack to the stop collar (air-over-hydraulic: a valve)", 8, 40),
         ("release, applicator returns and pre-feeds the next contact", 3, 8),
         ("lift the crimp out, glance at it, next conductor", 3, 6)]
lo = sum(s[1] for s in steps); hi = sum(s[2] for s in steps)
for n, a, b in steps:
    print(f"  {n:66s} {a:3d}-{b:3d} s")
print(f"  per crimp {lo}-{hi} s; per 53-crimp unit {53*lo/60:.0f}-{53*hi/60:.0f} min attended")
print("  today's hand procedure: ~22 min of crimping a unit [hand-tool-as-press wave2 s9]")
print("  -> v9b is slower than today by hand. It is a first-week crimper that removes the")
print("     contact juggling, and a measuring bench for the tack, the order and the room.")

print()
print("=" * 78)
print("5. The applicator's own ram as the tacker (a direction set aside)")
print("=" * 78)
print("  To close the insulation wings to H_f + dH, the ram stops dH = 0.2-0.5 mm above bottom.")
for dH in (0.2, 0.35, 0.5):
    for ft in cond_first_touch:
        curl = max(0.0, ft - dH)
        total = ft - compaction[1]        # curl travel before compaction begins
        frac = min(1.0, curl / total) if total > 0 else 1.0
        print(f"  stop {dH:.2f} mm above bottom, conductor wings first met at {ft:.2f}: curled "
              f"{curl:.2f} mm of ~{total:.2f} -> opening left ~{(1-frac)*100:3.0f} %")
print("  -> the conductor barrel is partly to wholly closed at the moment of the look [estimate:")
print("     opening taken as shrinking in proportion to curl travel]. The separate former is what")
print("     keeps the barrel open for the straight-down look.")
