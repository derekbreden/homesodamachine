"""Small checks for the dock and the rim-riding carriage. All inputs are labelled estimates.

Dock: a three-ball / three-groove (Maxwell) seat preloaded by a magnet plus residual weight.
  Tip-off: a disturbing force F at lever h about the nearest ball-to-ball line unloads the
  seat when F*h > Fp * r/2 (equilateral triangle, balls on radius r, preload through centroid).
Rim carriage: a stationary load on a rotating 0.065 in wall tube seated in a light nest.
"""
import numpy as np

G = 9.81
print("== Dock tip-off: largest disturbing force the seat holds, F = Fp*r/(2h) ==")
for Fp in (20, 40, 80):
    for r in (30, 50, 80):
        row = []
        for h, what in ((60, "at the dot / wire tip, seat near barrel"),
                        (200, "at the trigger, 200 mm from seat")):
            row.append(f"{what}: {Fp*r/(2*h):5.1f} N")
        print(f"  preload {Fp:3d} N, seat radius {r} mm -> " + " | ".join(row))

print("\n  Hand trigger (assumed 3-8 N) at ~200 mm from a seat near the barrel needs Fp*r >= 2*8*200 = 3200 N·mm,")
print("  e.g. 80 N on r=40 mm. A shell-mounted presser (servo/Bowden) puts no net force on the seat.")

print("\n== Rim carriage: what a stationary load does to the tube in its nest ==")
tube_h = 152.4
r_rim = 62.5
for mass, label in ((1.40, "first closure"), (2.01, "second closure")):
    W = mass * G
    # a net outward radial force at the rim tips the tube about its lower rim edge (weight restores)
    Fr_max = W * 63.5 / tube_h
    print(f"  {label}: tube weight {W:.1f} N; net radial rim force that lifts the far lower edge ~{Fr_max:.1f} N")
print("  Downward rim load inside the tube's own footprint cannot tip it; it only adds seat load.")
print("  A pinch (rollers inside and outside the lip) puts zero net radial force on the tube.")

# table friction torque added by a downward carriage preload on the 36-ball race (rolling, tiny)
for Fz in (10, 20, 40):
    # PP balls on printed races: assume rolling-resistance coefficient 0.005 at 82.5 mm race radius
    T = Fz * 0.005 * 0.0825
    print(f"  carriage preload {Fz} N adds ~{T*1000:.1f} N·mm of race drag (motor delivers ~8500 N·mm at the table)")

print("\n== Heat ahead of the puddle (Rosenthal characteristic length 2*alpha/v) ==")
alpha = 4.0  # mm^2/s, 316L near room temperature
for v in (5, 8, 15):
    print(f"  travel {v} mm/s: 2α/v = {2*alpha/v:.2f} mm -> a contact 20-40 mm ahead sees essentially "
          f"bulk (not puddle) temperature")
# bulk temperature rise from one revolution, crude
for eff in (0.3, 0.6):
    Q = 700 * 0.60 * 48.6 * eff  # J absorbed at 60 % power over one revolution at 8 mm/s
    dT = Q / (1.40 * 500)
    print(f"  absorbed fraction {eff}: ~{Q/1000:.0f} kJ -> {dT:.0f} K bulk rise if spread over the 1.4 kg vessel")

print("\n== Umbilical twist from grip-axis roll ==")
# angle between grip direction (cable exit) and grip axis in the gun's local frame
grip_dir = np.array([0, -86.0, 60.0]); grip_dir /= np.linalg.norm(grip_dir)
axis = np.array([0, -118.0, 253.0]); axis /= np.linalg.norm(axis)
c = np.dot(grip_dir, axis)
print(f"  cable exit is {np.degrees(np.arccos(c)):.0f} deg off the grip axis: a grip-axis roll of θ twists the"
      f" cable at the exit by ~{c:.2f}·θ (45 deg roll -> ~{45*c:.0f} deg of twist)")
for L in (50, 300, 1000):
    print(f"  that twist spread over {L} mm of free cable: {45*c/L*1000:.0f} deg per metre")
