"""Wave 4 calcs. Pose: hole dial 30 (true opening pose), my proxy.
1. Film-grip carrier (borrowed-ecosystems E): gimbal pendulosity vs umbilical torque about the CG.
2. Teach-and-replay: what each measuring route resolves at the dot.
All masses, cable loads and sensor accuracies are labelled estimates."""
import math
from proxy import *
g = 9.81
cg, gb = pose((0, 0, 185.5)), pose(GB)
lever = math.dist(cg, gb)
print(f'== 1. CG (proxy) to cable exit: {lever:.0f} mm')
m = 2.5   # gun + shell + rider + gimbal [their estimate]
for F in (1, 2, 5):
    T = F * lever   # N*mm, worst case (pull perpendicular to the lever)
    print(f'   umbilical pull {F} N at the exit -> up to {T:.0f} N*mm about the CG')
for d in (2, 5, 20, 60, 100):
    k = m * g * d * math.pi / 180   # N*mm per degree (small angle)
    for F in (1, 5):
        T = F * lever
        s = T / (m * g * d)
        ang = math.degrees(math.asin(s)) if s < 1 else float('nan')
        print(f'   CG {d:3d} mm below the pivots: {k:5.2f} N*mm/deg; {F} N cable pull tips it {"over (flips)" if s >= 1 else f"{ang:.0f} deg"}')

print('\n== 2. Teach/record: resolution at the dot (estimates)')
L = 250.0
for name, joint_deg, n in (('AS5600 12-bit, uncalibrated (~0.3 deg)', 0.3, 5), ('AS5600 calibrated (~0.1 deg)', 0.1, 5), ('14-bit AS5048-class (~0.03 deg)', 0.03, 5)):
    per = L * math.radians(joint_deg)
    print(f'   {name}: {per:.2f} mm per joint at {L:.0f} mm; RSS over {n} joints ~{per*math.sqrt(n):.2f} mm')
for fov, px in ((300, 4656), (200, 4656)):
    mmpx = fov / px
    print(f'   16 MP camera, {fov} mm field: {mmpx:.3f} mm/px; tag corner at 0.2 px -> {0.2*mmpx:.3f} mm; 40 mm tag angle ~{math.degrees(0.2*mmpx*1.4/40):.3f} deg (calibration-limited in practice: ~0.1-0.3 deg)')
print('   IMU tilt vs gravity (BNO08x/ICM class): ~0.2-0.5 deg static after calibration (estimate); no heading')
print('   dot vs corner by camera ~69 deg off the beam: ~3 px per 0.1 mm standoff (machine-that-learns)')
