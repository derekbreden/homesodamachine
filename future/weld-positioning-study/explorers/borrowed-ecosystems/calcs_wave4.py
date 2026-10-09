"""Wave-4 numbers: (1) the exchange on sequence-of-use's monitor-arm session,
(2) combination F, the hand-steered isocentre.

Corrected opening pose (grip 45, hole dial 30, vertical -15). Everything marked
[assumption] is an estimate; the umbilical's bending stiffness in particular is
unknown. Run: python3 calcs_wave4.py
"""
import numpy as np
import geometry as G

g0 = 9.81
POSE = (45, 30, -15)
B = G.BENCH_OFFSET
dot = G.JOINT
gb = G.pose_point(G.GRIP_BASE, *POSE)
gax = (gb - dot) / np.linalg.norm(gb - dot)
cg = G.pose_point(G.CG_LOCAL, *POSE)

print("== 1. Umbilical saddle height: natural apex vs a saddle at 680 mm ==")
start = gb + 70 * gax
el = np.degrees(np.arcsin(gax[2]))
R = 350.0
rise_to_vertical = R * np.cos(np.radians(el))       # turning up from el to 90 deg at R
run_to_vertical = R * (1 - np.sin(np.radians(el)))
print(f"cable on the grip axis 70 mm out: bench z {start[2]+B:.0f}, elevation {el:.0f} deg")
print(f"free (turning down at R 350): apex {start[2]+B + R*(1-np.cos(np.radians(el))):.0f} mm above the bench")
print(f"to reach 680 mm it must first turn UP: at the minimum radius it gains {rise_to_vertical:.0f} mm over {run_to_vertical:.0f} mm, "
      f"reaching {start[2]+B+rise_to_vertical:.0f} mm heading vertical, then turn over a saddle")
for EI in (0.1, 0.3, 0.5):   # N*m^2, umbilical bending stiffness [assumption]
    print(f"   EI {EI} N*m^2: bending moment held at the butt when forced to R 350 = {EI/0.35:.2f} N*m")
d_axis = np.linalg.norm(np.cross(cg - dot, gax))
print(f"CG proxy distance from the grip axis (cable exit line): {d_axis:.0f} mm; "
      f"distance CG to cable exit: {np.linalg.norm(cg-gb):.0f} mm")
for F in (2, 5, 8):
    print(f"   cable tension {F} N along the grip axis -> torque about the CG {F*d_axis/1000:.2f} N*m")

print("\n== 2. Trimming a constant cable torque by offsetting the bail pins ==")
for W in (15, 20, 25):
    for tau in (0.3, 0.65):
        d = tau / W * 1000
        print(f"gun+shell {W} N, cable torque {tau} N*m -> pin offset {d:.0f} mm (horizontal); residual after a 20 deg hand tilt "
              f"{tau*(1-np.cos(np.radians(20))):.3f} N*m")

print("\n== 3. Drag instead of a lock on the bail pins (fluid-head principle) ==")
I_gun = 0.03   # kg m^2 about the bail pins, gun + shell ~1.5 kg with ~0.14 m radius of gyration [assumption]
for c in (0.5, 1.0, 2.0):   # N*m*s/rad
    drift = 0.65 / c
    print(f"drag {c} N*m*s/rad: let go with 0.65 N*m unbalance -> drifts {np.degrees(drift):.0f} deg/s; "
          f"hand turning at 20 deg/s feels {c*np.radians(20):.2f} N*m; time constant {I_gun/c*1000:.0f} ms")

print("\n== 4. Solenoid vs servo for the dock trigger ==")
lap = 388.61 / 8.0
print(f"trigger hold for one lap at 8 mm/s + 20 deg overlap + start ~ {lap + lap*20/360 + 3:.0f} s (continuous)")
print("Heschen HS-1564B listing: 3 N at 20 mm stroke, 60 N only at closure with the shim removed, and it states the coil heats "
      "and is unsuitable for prolonged operation")
tq = 12 * 0.0981   # MG996R 12 kg*cm at 6 V -> N*m [listing]
for horn in (15, 20, 25):
    print(f"MG996R 12 kg*cm on a {horn} mm horn: {tq/(horn/1000):.0f} N stall at the presser; holds position under PWM")

print("\n== 5. M2: pole-arm swivel friction vs the balancer line ==")
for W in (15, 20):
    for Ff in (1, 3, 5):   # N, swivel friction referred to the arm tip [assumption]
        th = np.degrees(np.arctan(Ff / W))
        print(f"W {W} N, arm friction {Ff} N: line leans {th:.1f} deg before the anchor follows -> "
              f"{0.6*np.tan(np.radians(th))*1000:.0f} mm offset on a 0.6 m line, {Ff} N sideways on the gun, swing on release")

print("\n== 6. F: gravity about the hole axis follows a sine; a zero-length spring balances it ==")
def hole_geom(hole, roll=45, m=1.5):
    p = (roll, hole, -15)
    c = G.pose_point(G.CG_LOCAL, *p)
    v = np.radians(p[2]); ha = np.array([np.cos(v), np.sin(v), 0])
    rvec = c - dot
    rperp = rvec - np.dot(rvec, ha) * ha
    r = np.linalg.norm(rperp)
    alpha = np.degrees(np.arccos(np.clip(rperp[2] / r, -1, 1)))
    tau = float(np.dot(np.cross(rvec / 1000, [0, 0, -m * g0]), ha))
    return r, alpha, tau
for hole in (15, 20, 30, 40, 45):
    r, a, t = hole_geom(hole)
    print(f"dial {hole}: CG {r:.0f} mm from the hole axis, {a:.0f} deg from vertical; torque {t:.2f} N*m "
          f"(m g r sin(alpha) = {1.5*g0*r/1000*np.sin(np.radians(a)):.2f})")
r30, a30, t30 = hole_geom(30)
for a_, b_ in ((0.10, 0.10), (0.15, 0.15)):
    k = 1.5 * g0 * (r30 / 1000) / (a_ * b_)
    print(f"zero-length spring attached {a_*1000:.0f} mm out along the CG line, anchored {b_*1000:.0f} mm above the pivot: "
          f"k = {k:.0f} N/m ({k/1000:.2f} N/mm) balances 1.5 kg at every hole angle")
print("mass error 10% -> residual 10% of 1.0-2.2 N*m = 0.10-0.22 N*m, held by drag; the anchor height b is the trim knob")

print("\n== 7. F: roll about the grip axis also follows a sine ==")
for roll in (0, 10, 30, 45, 60, 75):
    p = (roll, 30, -15)
    gbp = G.pose_point(G.GRIP_BASE, *p); ga = (gbp - dot) / np.linalg.norm(gbp - dot)
    c = G.pose_point(G.CG_LOCAL, *p)
    t = float(np.dot(np.cross((c - dot) / 1000, [0, 0, -1.5 * g0]), ga))
    print(f"roll {roll:2d}: grip-axis torque {t:.2f} N*m   (0.90*sin(roll) = {0.90*np.sin(np.radians(roll)):.2f})")

print("\n== 8. F: hand on a tiller, drag as a tremor filter ==")
I = 1.5 * (r30 / 1000) ** 2 + 0.6 * 0.15 ** 2   # gun + spoke about the hole axis [assumption]
for c in (0.5, 1.0, 2.0):
    fc = c / (2 * np.pi * I)
    att = np.sqrt(1 + (10 / fc) ** 2)
    print(f"I {I:.3f} kg m^2, drag {c}: corner {fc:.1f} Hz; 10 Hz tremor attenuated ~{att:.0f}x; steering 10 deg/s needs "
          f"{c*np.radians(10):.2f} N*m = {c*np.radians(10)/0.25:.1f} N at a 250 mm tiller")
L, E, Iext, F = 300.0, 69000.0, 1.1e5, 10.0
print(f"tiller push {F:.0f} N on a 4040 spoke, gun carried at 300 mm with the nozzle near the root: "
      f"nozzle moves {F*L**3/(6*E*Iext):.4f} mm (tip deflection minus rotation x L)")
mu = 60.0   # Pa*s, heavy damping grease [assumption]
r_, Lc, h = 0.03, 0.02, 0.0002
print(f"grease-film damper r 30 mm, length 20 mm, gap 0.2 mm, mu {mu:.0f} Pa*s: c = {mu*2*np.pi*r_*Lc*r_**2/h:.2f} N*m*s/rad")

print("\n== 9. F: a bicycle disc brake as the hinge lock ==")
for Fp in (300, 600):
    print(f"cable caliper pad force {Fp} N, mu 0.4, two pads, 160 mm rotor (r_eff 0.07 m): holding {2*Fp*0.4*0.07:.0f} N*m vs 1-3.3 N*m needed")
