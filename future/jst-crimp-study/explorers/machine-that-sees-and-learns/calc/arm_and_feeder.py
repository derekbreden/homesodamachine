"""Two numbers for the ideas that lean on imprecise motion: what an SO-101 can place, and how
many taps a lit tray needs to offer a loose XH contact in the right pose.

Explorer: machine-that-sees-and-learns. Run: python3 arm_and_feeder.py > arm_and_feeder.out.txt
"""
import math

print("=" * 76)
print("1. SO-101 tip resolution and what the XH steps need")
print("=" * 76)
count_deg = 360 / 4096  # STS3215 / ST3215 position sensor 360/4096 [source: Waveshare wiki]
print(f"  one encoder count = {count_deg:.4f} deg")
for r in (0.05, 0.10, 0.25, 0.35):
    print(f"    at {r*1000:3.0f} mm from the joint: {r*math.radians(count_deg)*1000:.2f} mm per count")
print("  Gear backlash and servo compliance are not published [source: Waveshare wiki]; with")
print("  shoulder and elbow each worth ~0.4-0.5 mm per count at the tip, a tip repeatability of")
print("  ~1-2 mm is the working [estimate]. Dobot's MG400 states +/-0.05 mm [source: dobot].")
needs = [("conductor over the open barrel, lateral", 0.15),
         ("insulation edge in the window, axial", 0.25),
         ("contact into an XHP cavity, lateral", 0.2),
         ("clip into a chamfered dock (capture range)", 2.5)]
for name, tol in needs:
    print(f"    {name:48s} +/-{tol:.2f} mm -> arm error/tolerance ~{1.5/tol:4.1f}x")
print("  Everything but the dock is out of the arm's reach by 5-10x: the arm carries, a dock")
print("  locates, and a station's own small stage or guide does the last fraction of a mm.")

print()
print("=" * 76)
print("2. Transfers and teaching time for the arm (v2)  [estimate]")
print("=" * 76)
ends = 14
visits = 5
t_transfer = (15, 30)
print(f"  {ends} ribbon ends x {visits} station visits = {ends*visits} transfers per unit")
print(f"  at {t_transfer[0]}-{t_transfer[1]} s each: {ends*visits*t_transfer[0]/60:.0f}-{ends*visits*t_transfer[1]/60:.0f} min of arm time per unit")
subtasks = 5
episodes = 50   # LeRobot's own advice: "at least 50 episodes" [source: LeRobot docs]
t_ep = (1.0, 1.5)
print(f"  teaching: {subtasks} subtasks x {episodes} demonstrations x {t_ep[0]}-{t_ep[1]} min = "
      f"{subtasks*episodes*t_ep[0]/60:.1f}-{subtasks*episodes*t_ep[1]/60:.1f} h of Derek at the leader arm")
print("  Training: 'several hours' per policy [source: LeRobot docs], unattended, on the Mac (mps)")
print("  or a rented GPU. Harness labour today is 45 attended min per unit [repo: labor.md], so")
print("  the teaching costs roughly the harness labour of 5-8 units, spent once.")

print()
print("=" * 76)
print("3. The lit tray (v4): taps per usable contact  [assumption: pose odds unmeasured]")
print("=" * 76)
print("  p_up  = chance a settled contact lies barrels-up")
print("  yaw   = with a rotating nozzle any heading works; without one, only +/-15 deg of the")
print("          right heading with the box forward (30/360)")
print(f"  {'p_up':>5s} {'N on tray':>9s} {'yaw':>12s} {'P(>=1 usable)':>14s} {'taps/pick':>10s} {'s/pick @3 s/tap':>16s}")
for p_up in (0.15, 0.3, 0.5):
    for N in (10, 20, 40):
        for yaw_label, p_yaw in (("rotating", 1.0), ("fixed", 30 / 360)):
            p = p_up * p_yaw
            P = 1 - (1 - p) ** N
            taps = 1 / P
            print(f"  {p_up:5.2f} {N:9d} {yaw_label:>12s} {P:14.2f} {taps:10.1f} {taps*3:16.0f}")
print("  Even the worst row (few contacts, rare pose, fixed heading) is under half a minute a pick,")
print("  which a machine that takes 2-3 minutes a crimp can hide by picking during the press stroke.")
print("  The tray measures its own pose odds: 20 contacts x 50 taps, each pose counted by the camera.")
