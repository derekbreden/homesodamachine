"""Time and mass budget for the tube swap, and the numbers that decide whether a puck coupling holds.

Sources: rotating mass 1.40 kg (first closure) / 2.01 kg (second closure), rev time 26-78 s, nest with three M3 radial
adjusters and an indicated runout acceptance [repo] weld-rotation-rig.md. Swap and prep TIMES are ILLUSTRATIVE guesses
(nobody has timed them: [unknown]); change them and see. Coupling preload/friction are ILLUSTRATIVE.
"""
import math
def cycle(trial_s, swap_s, trials_per_load):
    tot = trials_per_load*trial_s + swap_s
    return trials_per_load*trial_s/tot, tot/60.0
print("Utilisation of the rig = trial time / (trial time + swap time)  [ILLUSTRATIVE times]")
print(" trial_s  swap_s  trials/load  utilisation  cycle_min")
for trial in (60, 120, 180):
    for swap in (30, 600, 900):
        for n in (1, 5, 20, 100):
            u, m = cycle(trial, swap, n)
            print(f"  {trial:5d}  {swap:6d}  {n:10d}   {u:9.2f}   {m:8.1f}")
print("\nDay and night: trials per 8 h if one load supports N trials and a hand swap costs S seconds (trial 120 s)")
for S in (30, 600, 900):
    for N in (5, 20, 100):
        per = N*120+S; loads = 8*3600/per
        print(f"  swap {S:4d}s, {N:3d} trials/load: {loads:5.1f} loads, {loads*N:6.0f} trials, {loads:4.1f} human visits")

print("\nKinematic coupling holding torque (ILLUSTRATIVE): 3 balls at radius Rb, magnet preload Fm total, V-groove half-angle alpha")
def hold(Rb_mm, Fm_N, alpha_deg, mu=0.3):
    # tangential force at one ball before it climbs its groove flank: F_t = (Fm/3)*tan(alpha_eff) with radial groove
    # for a radial V-groove the tangential direction is across the groove: flank normal has tangential component sin(alpha)
    a = math.radians(alpha_deg)
    ft = (Fm_N/3) * math.tan(a)      # per ball, ignoring friction (friction only helps)
    return 3*ft*Rb_mm/1000.0
for Fm in (15, 30, 60):
    for Rb in (60, 80):
        print(f"  Fm {Fm:3d} N, ball circle r {Rb} mm, 45 deg flank: holds about {hold(Rb,Fm,45):.2f} N*m before a ball leaves its groove")
print("  Drive torque to turn 2 kg on a ball race: order of 0.05-0.3 N*m [ILLUSTRATIVE guess; ball-race friction coeff 0.005-0.02 at r = 82 mm gives",
      round(2.0*9.81*0.02*0.0825,3), "N*m at mu 0.02]")
print("  A wire catch at the weld radius (61.85 mm): each N of tangential pull is", round(1*0.06185,3), "N*m. Wire-pull force: [unknown]")

print("\nSeam displacement from puck tilt (small angle): lateral = h*theta, vertical at the weld radius = R*theta")
h = 146.05 + 20     # seam height above the tube bottom + nest under it, ILLUSTRATIVE 20 mm
for span in (60, 100, 150):
    for rep_um in (5, 10, 25, 50):
        th = rep_um/1000/span
        print(f"  coupling repeatability {rep_um:3d} um over a {span:3d} mm span: tilt {th*1e6:6.1f} urad -> lateral {h*th*1000:5.1f} um, vertical {61.85*th*1000:5.1f} um")
print("\nMasses [derived]: tube 316L OD 127 / ID 123.7 x 152.4 mm, plate 123.44 x 6.35 mm")
rho = 8.0e-3  # g/mm^3
tube = math.pi/4*(127**2-123.7**2)*152.4*rho
plate = math.pi/4*123.44**2*6.35*rho
print(f"  tube {tube/1000:.2f} kg, one plate {plate/1000:.2f} kg -> {(tube+plate)/1000:.2f} kg one plate, {(tube+2*plate)/1000:.2f} kg two plates  (rig doc: 1.40 / 2.01 kg incl. nest parts)")
