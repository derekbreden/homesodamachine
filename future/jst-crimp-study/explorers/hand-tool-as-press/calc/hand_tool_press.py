"""Numbers for the hand-tool-as-press explorer.

Run: python3 hand_tool_press.py > hand_tool_press.out.txt

Every input carries its label. Die force, crimp height and barrel sizes come
from ../../../context/xh-facts.md (calc C1 there). Nothing here is measured.
"""
import math

def hr(title):
    print()
    print("=" * 76)
    print(title)
    print("=" * 76)

# ---------------------------------------------------------------------------
hr("1. Handle force needed to close a ratchet hand tool on an XH crimp")
# ---------------------------------------------------------------------------
die_force_kN = (0.8, 1.5, 2.6)          # [xh-facts §4, calc C1] low / mid / high
# Mechanical gain at full closure. Pressmaster C-frame tools: 23:1 (1976),
# 40:1 (1990s), 50:1 (today) [source: assemblymag 95079]. A $21 stamped tool
# is assumed to sit lower: 15-40 [assumption].
ma_end = (15, 23, 30, 40, 50)
print("die force (kN) -> handle force at the grip end (N), by end-of-stroke gain")
print("  gain:    " + "".join(f"{m:>8d}" for m in ma_end))
for F in die_force_kN:
    row = "".join(f"{F*1000/m:8.0f}" for m in ma_end)
    print(f"  {F:4.1f} kN  {row}")
# The hand as existence proof: Derek closes the SN-2549 on XH by hand [repo].
# Users apply 20 lbf (women) to 50 lbf (men) at the handle [source: assemblymag 95079].
hand_lo, hand_hi = 20*4.448, 50*4.448
print(f"hand force people apply: {hand_lo:.0f}-{hand_hi:.0f} N  [source]")
print("-> the grip-end force the SN-2549 needs on XH is at most what a hand gives,")
print("   ~90-220 N, whatever the tool's real gain; the table above spans 16-173 N.")
hand_max = hand_hi

# ---------------------------------------------------------------------------
hr("2. Slow actuators at the grip end (stall or rated figures, [calc] with assumed parts)")
# ---------------------------------------------------------------------------
def screw_force(T_Nm, lead_mm, eta):
    return 2*math.pi*T_Nm*eta/(lead_mm/1000.0)

opts = []
# NEMA 17, 48 mm stack, ~0.4-0.45 N*m holding; run slow at ~70 % of holding.
for T, lead, eta, name in [
    (0.30, 2, 0.30, "NEMA17 48mm, Tr8x2 external nut (0.3 N*m running)"),
    (0.30, 8, 0.45, "NEMA17 48mm, Tr8x8 external nut (0.3 N*m running)"),
    (1.0, 2, 0.30, "NEMA23 on hand (1.0 N*m running), Tr8x2"),
]:
    opts.append((name, screw_force(T, lead, eta)))
# Worm gearmotor winch: 5840-31ZY, max 70 kg*cm = 6.9 N*m [source NFP];
# take one third as a working figure [assumption]; drum radius 8 mm.
T_worm = 6.9/3
for r_mm in (6, 8, 12):
    opts.append((f"5840-31ZY worm winch, {T_worm:.1f} N*m working, drum r={r_mm} mm",
                 T_worm/(r_mm/1000)))
# Hobby servo 35 kg*cm = 3.4 N*m stall, working half, 25 mm horn
opts.append(("35 kg*cm hobby servo, half stall, 25 mm horn", 3.4/2/0.025))
# Pneumatic at 6 bar (87 psi)
for bore in (20, 25, 32):
    A = math.pi*(bore/2000)**2
    opts.append((f"air cylinder {bore} mm bore at 6 bar", 6e5*A))
for name, F in opts:
    flag = ">= hand max" if F >= hand_max else ("0.6-1x hand max" if F >= 0.6*hand_max else "< 0.6x hand max")
    print(f"  {name:62s} {F:7.0f} N  {flag}")

# ---------------------------------------------------------------------------
hr("3. Stroke and closing time at the grip end")
# ---------------------------------------------------------------------------
# SN-2549 listed as 8 x 3 x 1 in, 10 oz [source: TH3D listing]. Take the 3 in
# as the open span across the grips; closed span ~20-25 mm [estimate].
open_span = 3*25.4
for closed in (20, 25):
    travel = open_span - closed
    print(f"  open {open_span:.0f} mm -> closed {closed} mm: grip travel {travel:.0f} mm")
travel = open_span - 22
for v in (1, 2, 5, 10):
    print(f"  at {v:2d} mm/s the full squeeze takes {travel/v:5.0f} s")

# ---------------------------------------------------------------------------
hr("4. The handle as a magnifier of die position")
# ---------------------------------------------------------------------------
# Compaction happens in the last 0.10-0.20 mm of conductor-punch travel [xh-facts §4].
for m in (15, 30, 40):
    for dz in (0.10, 0.20):
        print(f"  gain {m:2d}: last {dz:.2f} mm at the die = {dz*m:4.1f} mm at the grip")
# Tr8x2 at 200 full steps x 16 microsteps
res = 2.0/(200*16)
print(f"  Tr8x2 pusher resolution: {res*1000:.2f} um per microstep at the grip")
print(f"  -> {res*1000/30:.3f} um at the die through a gain of 30, before compliance")
print("  Compliance (handles bending, pin play, pusher mount) adds grip travel that")
print("  is not die travel. It is measured by closing the empty tool and by closing")
print("  on a contact without wire; the difference curve is what the crimp did.")

# ---------------------------------------------------------------------------
hr("5. Eccentric drive for dies lifted into a die set (idea a4)")
# ---------------------------------------------------------------------------
# Ram driven by an eccentric of radius e. Stroke 2e. Force needed at angle
# theta from BDC: torque = F * e * sin(theta) (ignoring link angle, friction).
for e in (1.5, 2.5, 4.0):
    for F_kN, dz in ((1.5, 0.15), (3.0, 0.15), (3.0, 0.25)):
        th = math.acos(1 - dz/e)
        T = F_kN*1000*(e/1000)*math.sin(th)
        print(f"  e={e:3.1f} mm (stroke {2*e:3.1f}): {F_kN:.1f} kN starting {dz:.2f} mm above BDC"
              f" -> {math.degrees(th):4.1f} deg, peak shaft torque {T:4.2f} N*m")
print("  Add ~30-50 % for friction in the eccentric and ram guides [assumption].")
print("  5840-31ZY working ~2.3 N*m (stall 6.9): enough for e<=2.5 mm at 1.5 kN, and")
print("  near its limit at 3 kN; NEMA 23 (~1.0 N*m running) with a 3:1 belt gives ~3 N*m.")
# Wing forming before compaction: few hundred N over ~0.7 mm, trivial torque.

# ---------------------------------------------------------------------------
hr("6. Overtravel spring: force-limited full closure (the ratchet's job, done by a spring)")
# ---------------------------------------------------------------------------
# Dies bottom face-to-face at BDC [assumption for SN jaws; IWISS IWS-3220M jaws
# 'touch each other everywhere' when closed, source hackaday.io 176110].
# A preloaded disc-spring stack under the lower die holder: stays solid until
# the preload, then yields to absorb overtravel.
for preload_kN in (3.0, 3.5, 4.0):
    print(f"  preload {preload_kN:.1f} kN: crimp up to {preload_kN:.1f} kN happens rigid;"
          f" any extra eccentric travel compresses the stack instead of the frame")
# Disc spring stiffness order: a 20 mm OD x 1 mm disc ~ 2-4 kN per mm when stacked in series
print("  Series stack of 3-4 discs (20-25 mm OD, 1-1.25 mm) gives ~0.3-0.6 mm of travel")
print("  over ~1-2 kN rise [estimate, disc-spring catalogues]. With ~0.15 mm of eccentric")
print("  overtravel past die contact, the dies meet every stroke and the peak is ~4-5 kN.")

# ---------------------------------------------------------------------------
hr("7. Where the contact must sit along its axis, and what can reference it")
# ---------------------------------------------------------------------------
# Bellmouth: rear edge of conductor barrel 0.1-0.2 mm proud of the die edge
# [source: PA-09 advice in prior-art]; bellmouth 1-2x stock = 0.2-0.4 mm [xh-facts §5].
window = 0.10  # +/- mm, allowable axial error at the conductor die [estimate]
refs = [
    ("box front against a stop (contact length +/-0.25 on clone drawings)", 0.25),
    ("box rear shoulder against a flap (box length 2.0; tolerance assumed +/-0.05)", 0.05 + 0.03),
    ("pilot hole on a pin (pin 1.45 in hole 1.50; hole-to-barrel assumed +/-0.05)", 0.025 + 0.05),
    ("0.64 mm post in the box, box front on the post shoulder", 0.25),
    ("camera measures, carriage corrects (0.02 mm/px at ~20 mm field) ", 0.03),
]
print(f"  allowable axial error at the conductor die: about +/-{window:.2f} mm [estimate]")
for name, err in refs:
    print(f"  {name:78s} +/-{err:.3f}  {'fits' if err <= window else 'outside'}")
print("  Where the +/-0.25 on overall length sits (tab, box front, or between box and")
print("  barrels) is not on the drawings; a caliper on kit contacts measures it.")

# ---------------------------------------------------------------------------
hr("8. Getting neighbours out of the jaw: lift one conductor out of the ribbon plane")
# ---------------------------------------------------------------------------
for clear in (8, 12, 16):          # mm the working conductor must stand clear [estimate of jaw extent]
    for ang in (20, 30, 45):
        L = clear/math.tan(math.radians(ang))
        print(f"  stand {clear:2d} mm clear at a {ang} deg bend -> split length >= {L:4.0f} mm"
              f" (plus ~8 mm straight lead held in the fork)")
print("  Splay to XH pitch alone moves a 5P's outer conductor 1.6 mm [xh-facts §7];")
print("  the jaw needs far more room than the housing does.")

# ---------------------------------------------------------------------------
hr("9. Tab shear and pull proof")
# ---------------------------------------------------------------------------
for w in (0.8, 1.0, 1.2):
    for tau in (250, 400):
        print(f"  tab {w:.1f} x 0.20 mm, shear {tau} MPa -> {w*0.2*tau:5.0f} N")
spec = 39.2
for frac in (0.5, 0.6):
    print(f"  proof pull at {frac:.0%} of JST's 39.2 N minimum = {spec*frac:4.1f} N")
print("  A carriage pulling through a spring to ~20-25 N screens gross failures without")
print("  destroying a good crimp [assumption; proof loads are not a JST procedure].")

# ---------------------------------------------------------------------------
hr("10. Time per unit")
# ---------------------------------------------------------------------------
steps = {
    "index to next conductor / lift it": 8,
    "load contact (stub, post or chute) and hold one click": 15,
    "feed conductor to depth, continuity check": 12,
    "squeeze full stroke at ~2 mm/s": 25,
    "open, camera frame": 8,
    "proof pull": 10,
    "unload (and tab cut if stub-fed)": 15,
}
per = sum(steps.values())
for k, v in steps.items():
    print(f"  {k:55s} {v:4d} s")
print(f"  per crimp ~{per} s -> 53 crimps ~{53*per/60:.0f} min machine time per unit")
print(f"  at 3x slower (retries, dwell) ~{3*53*per/60:.0f} min")
print("  Person: 14 ribbon ends to clamp, contacts to stage.")

# ---------------------------------------------------------------------------
hr("11. Two-squeeze plier (idea a5): force per squeeze and moves between squeezes")
# ---------------------------------------------------------------------------
# PA-09: 175 mm plier; hand 150-300 N x gain 5-8 = 0.75-2.4 kN [xh-facts calc C1 §5]
for g in (5, 8):
    for F in (0.75, 1.5, 2.3):
        print(f"  gain {g}: conductor barrel alone at {F:.2f} kN needs {F*1000/g:4.0f} N at the grip")
# Barrel centre spacing: conductor barrel ~1.25-1.5, gap ~0.5-1.0, insulation barrel ~0.8-1.5
lo = 1.25/2 + 0.5 + 0.8/2
hi = 1.5/2 + 1.0 + 1.5/2
print(f"  axial move from conductor-die to insulation-die position: {lo:.1f}-{hi:.1f} mm"
      " plus the lateral nest spacing (measure on the tool)")
