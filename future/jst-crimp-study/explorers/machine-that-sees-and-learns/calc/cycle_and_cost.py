"""Time per crimp for a look-act-look cell, per-unit totals, data volume and the cost of
asking Claude to judge images.

Explorer: machine-that-sees-and-learns. Run: python3 cycle_and_cost.py > cycle_and_cost.out.txt

Every step time is an [estimate] for a slow printer-part stage and a slow press; the point is
the order of magnitude, not the number.
"""
import math

CRIMPS_PER_UNIT = 53          # [repo: shared-context, cable-assemblies.md]
RIBBON_ENDS_PER_UNIT = 14     # [repo]
UNITS_PROGRAM = 60            # 1 + 10 + ~50 [repo: future/README.md via shared-context]

print("=" * 76)
print("1. One crimp at the watched nest (v1), seconds, low / high  [estimate]")
print("=" * 76)
steps = [
    ("present the next contact (strip index, or pick from the tray v4)", 5, 30),
    ("look: contact seated in the nest (1-2 frames + fit)", 1, 3),
    ("move the next conductor over the nest", 5, 10),
    ("look: stripped tip against the backlight (bundle, strip length)", 2, 4),
    ("visual servo: 3-8 x (move, settle, capture, fit)", 6, 16),
    ("lay in: lower Z, hold-down finger on the insulation", 3, 5),
    ("look: gate, top + side, 1-6 lighting states", 3, 10),
    ("Claude on a borderline gate (10-20% of crimps, ~20 s each)", 2, 4),
    ("press: approach @2 mm/s to the taught height, crawl 0.95-1.7 mm @0.05-0.1 mm/s, return", 19, 44),
    ("lift, move the crimp over the silhouette window", 4, 6),
    ("look: after-crimp side + top, optional 3-slice focus stack", 4, 15),
    ("proof pull to ~20 N while the camera watches for slip", 10, 20),
    ("cut the tab / clear the nest, park the conductor", 5, 10),
]
lo = sum(s[1] for s in steps)
hi = sum(s[2] for s in steps)
for name, a, b in steps:
    print(f"  {name:66s} {a:4d} {b:4d}")
print(f"  {'total per crimp, no retries':66s} {lo:4d} {hi:4d}  s  = {lo/60:.1f} - {hi/60:.1f} min")
for retry_rate in (0.1, 0.2):
    lo_r = lo + retry_rate * 60
    hi_r = hi + retry_rate * 90
    print(f"  with {retry_rate:.0%} of conductors backed out and retried once (+60-90 s): "
          f"{lo_r/60:.1f} - {hi_r/60:.1f} min")
unit_lo = CRIMPS_PER_UNIT * (lo + 0.1 * 60) / 3600
unit_hi = CRIMPS_PER_UNIT * (hi + 0.2 * 90) / 3600
print(f"Per unit ({CRIMPS_PER_UNIT} crimps): {unit_lo:.1f} - {unit_hi:.1f} h of unattended machine time.")
print(f"Program (~{UNITS_PROGRAM} units, ~{CRIMPS_PER_UNIT*UNITS_PROGRAM} crimps): "
      f"{unit_lo*UNITS_PROGRAM:.0f} - {unit_hi*UNITS_PROGRAM:.0f} h.")
print("A unit's print time is about a week [Derek]; ~100 printer-hours [repo: labor.md].")

print()
print("=" * 76)
print("2. The whole procedure per conductor in the patient cell (v6)  [estimate]")
print("=" * 76)
stages = [
    ("profile the ribbon end, slit one web 25-35 mm, look for copper", 40, 90),
    ("twist the tip, strip to the contact's length by sight, look at the cut", 40, 90),
    ("crimp at the watched nest (v1, above)", lo, hi),
    ("carry to the housing, align to the cavity, push, pull back, look", 40, 90),
]
tl = sum(s[1] for s in stages)
th = sum(s[2] for s in stages)
for name, a, b in stages:
    print(f"  {name:66s} {a:4d} {b:4d}")
print(f"  {'per conductor':66s} {tl:4d} {th:4d}  s  = {tl/60:.1f} - {th/60:.1f} min")
print(f"Per unit: {CRIMPS_PER_UNIT*tl/3600:.1f} - {CRIMPS_PER_UNIT*th/3600:.1f} h unattended.")
print(f"Person: cut {RIBBON_ENDS_PER_UNIT} ribbon ends and load them in pallets, load contacts and")
print("housings, clear the exception queue: ~1-2 min per ribbon end  [estimate]")
print(f"  -> {RIBBON_ENDS_PER_UNIT*1} - {RIBBON_ENDS_PER_UNIT*2} min attended per unit, plus exceptions.")

print()
print("=" * 76)
print("3. Claude judging images: tokens and dollars")
print("=" * 76)
# Visual tokens = ceil(w/28) * ceil(h/28) [source: platform.claude.com vision docs, fetched
# 2026-09-28]. Prices from the claude-api skill's model table cached 2026-09-25:
# Opus 5.5 $4 / $20 per MTok in/out, Sonnet 5.5 $2 / $10, Haiku 4.5 $1 / $5.
# The press line uses v7's crawl rule: crawl from >= 0.3 mm above the first wing touch,
# which [calc wave2 s5] puts at 0.65-1.40 mm, so 0.95-1.7 mm at 0.05-0.1 mm/s = 9-34 s,
# plus ~5 s approach and ~5 s return (borrowed-machines' exchange calc s10 found the
# earlier '1 mm' line up to 14 s short).
def vtok(w, h):
    return math.ceil(w / 28) * math.ceil(h / 28)

for w, h in ((800, 800), (1000, 1000), (1400, 1000), (2576, 1932)):
    print(f"  crop {w}x{h}: {vtok(w, h)} visual tokens")
models = {"Opus 5.5": (4, 20), "Sonnet 5.5": (2, 10), "Haiku 4.5": (1, 5)}
crops_per_call = 4
tok_images = crops_per_call * vtok(1000, 1000)
tok_text = 1500
for label, out_tokens, share in (("every crimp judged, short answer", 400, 1.0),
                                 ("every crimp judged, answer + thinking", 3000, 1.0),
                                 ("only borderline crimps (20%), with thinking", 3000, 0.2)):
    print(f"  {label}: {tok_images + tok_text} input + {out_tokens} output tokens per call")
    for m, (pin, pout) in models.items():
        per = ((tok_images + tok_text) * pin + out_tokens * pout) / 1e6
        unit = per * CRIMPS_PER_UNIT * share
        print(f"    {m:11s} ${per:.3f} per call  ${unit:6.2f} per unit  ${unit*UNITS_PROGRAM:7.2f} per program")
print("Reference images for few-shot judging can sit in a cached prefix (cache reads $0.20/MTok")
print("on Opus 5.5 and on Sonnet 5.5 [claude-api skill table, cached 2026-09-25]), which makes them")
print("nearly free after the first call.")
print("The vision docs say Claude's coordinates and counts are approximate, so the numbers")
print("(strip length, crimp height, offsets) come from OpenCV; Claude judges what a threshold")
print("cannot name: 'is that a strand outside the wing, or a reflection?'  [source]")

print()
print("=" * 76)
print("4. What the log weighs")
print("=" * 76)
crops = 8
crop_kb = 250      # 1000x1000 JPEG q95  [estimate]
full_mb = 3.0      # one 4656x3496 MJPG frame kept per crimp  [estimate]
per_crimp_mb = crops * crop_kb / 1000 + full_mb
print(f"  per crimp: {crops} crops x {crop_kb} KB + one full frame {full_mb} MB = {per_crimp_mb:.1f} MB")
print(f"  per unit: {per_crimp_mb*CRIMPS_PER_UNIT/1000:.2f} GB; program: {per_crimp_mb*CRIMPS_PER_UNIT*UNITS_PROGRAM/1000:.0f} GB")
print("  force-stroke curve: HX711 at 80 Hz x 30 s = 2,400 samples; negligible")
