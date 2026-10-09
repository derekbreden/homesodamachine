"""Re-run of sequence-of-use's calc/drawer_path.py logic (their proxy, read-only) at the
TRUE opening pose, hole dial 30 (posePoint hole -5), next to their dial-65 default.
phi = 0: tube arrives moving -X, i.e. from the weld-station side. Tube held DROP mm low
until the last RAMP mm, then raised linearly."""
import math
from wave2_lid_checks import P, PTS, TAGS, posed_points

def check(P0, phi_deg, drop, ramp, travel=250, step=0.5):
    phi = math.radians(phi_deg)
    s = travel
    while s >= 0:
        cx, cy = s * math.cos(phi), s * math.sin(phi)
        dz = drop if s > ramp else drop * s / ramp
        for q, t in zip(P0, TAGS):
            qq = (q[0] - cx, q[1] - cy, q[2] + dz)
            if P.collides_tube(qq, margin=0.0 if s < 1 else 0.8):
                return f"COLLIDE at s={s:.1f} ({t})"
        s -= step
    return "OK"

for dial in (30, 65):
    P0 = posed_points(45, dial, -15, "rotate")
    print(f"== hole dial {dial}")
    for phi in (0, 20, 40, -20, -40, 90, -90, 180):
        row = [f"drop {d}: {check(P0, phi, d, 60)}" for d in (0, 10, 20)]
        print(f"   phi {phi:4d}: " + " | ".join(row))

# NOTE: in check(), a ramp shorter than the 0.5 mm step skips the rise itself, so the
# r0.5 column below is NOT a vertical-rise check; the last section does that properly
# (a vertical rise grazes the wire tip, which sits exactly at the bore radius).
print("\n== repair search at hole dial 30: shorter (steeper) ramps (r0.5 column skips the rise; see below)")
P0 = posed_points(45, 30, -15, "rotate")
for phi in (0, 20, -20, 45, -45, 90, 180):
    row = []
    for drop in (10, 15, 20, 30):
        for ramp in (0.5, 5, 10, 20):
            r = check(P0, phi, drop, ramp)
            row.append(f"d{drop}/r{ramp}:{'OK' if r == 'OK' else 'x'}")
    print(f"   phi {phi:4d}: " + " ".join(row))

print("\n== the vertical final rise itself (tube at final x/y, raised from -drop to 0 in 0.1 mm steps)")
for dial in (30, 65):
    P0 = posed_points(45, dial, -15, "rotate")
    for drop in (10, 20):
        hit = None
        dz = float(drop)
        while dz >= 0:
            for q, t in zip(P0, TAGS):
                if P.collides_tube((q[0], q[1], q[2] + dz), margin=0.0 if dz < 1 else 0.5):
                    hit = (round(dz, 1), t)
                    break
            if hit:
                break
            dz -= 0.1
        print(f"   dial {dial}, drop {drop}: {'OK' if not hit else 'COLLIDE at ' + str(hit)}")
