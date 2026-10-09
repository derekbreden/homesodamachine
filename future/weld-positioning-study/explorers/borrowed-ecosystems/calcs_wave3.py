"""Wave-3 numbers: the film-grip carrier (E) and the A1 wedge/goniometer repair.

Corrected opening pose (hole dial 30). Masses, spring rates and friction are
assumptions, labelled. Run: python3 calcs_wave3.py
"""
import numpy as np
import geometry as G

g0 = 9.81
POSE = (45, 30, -15)

print("== 1. What a wedge swap does to the dot (partner's objection to A1) ==")
for d in (100, 150, 200):
    for dth in (2, 5):
        print(f"seat {d} mm from the dot, {dth} deg swap -> dot moves {d*np.radians(dth):.1f} mm")
print("-> agree: a pivot not on the dot turns every angle change into a three-screw re-trim")

print("\n== 2. Goniometer about the dot (fine angle on top of a coarse wedge) ==")
# Huanyu 65 mm goniometer: +/-10 deg, 0.05 deg min adjustment [listing]; centre height unpublished
for h_err in (0.5, 1.0, 2.0):
    for dth in (2, 5, 10):
        print(f"goniometer centre {h_err} mm off the dot, {dth:2d} deg -> dot walk {h_err*np.radians(dth):.3f} mm")
print("-> the centre must be found (walk test) and shimmed to <0.5 mm for 0.09 mm over 10 deg")

print("\n== 3. Soft carriers compared: what the gun feels when parked 300 mm aside ==")
m = 2.5   # gun + shell + rider + gimbal [assumption]
W = m * g0
for L in (0.8, 1.2):
    print(f"balancer line {L} m: pendulum return force at 300 mm aside {W*0.3/L:.1f} N (must be hooked)")
print("iso-elastic arm (bearing hinges on vertical axes): ~0 N return horizontally; stays where left")
print("gas-spring monitor arm: swivel friction holds it; head joints pass moments into the gun")

print("\n== 4. Iso-elastic arm on the rider: vertical behaviour ==")
for k in (0.1, 0.3, 0.5):   # N/mm, effective vertical rate of an iso-elastic arm [assumption]
    f = np.sqrt(k * 1000 / m) / (2 * np.pi)
    print(f"vertical rate {k} N/mm: free bounce {f:.1f} Hz; force change over +/-0.15 mm rider follow {k*0.15:.3f} N")
print("underbalance for rider preload: 5-10 N = 0.5-1.0 kg of the 2-5 kg spring range [Galaxy blue spring]")

print("\n== 5. Gimbal at the CG: pendulosity chosen so the lifted gun hangs near the working attitude ==")
for d in (2, 5, 10):
    tau = m * g0 * d / 1000
    print(f"CG {d} mm below the gimbal: restoring torque {tau*1000*np.pi/180:.2f} N*mm per degree off; "
          f"on the rider at 10 deg off {tau*np.sin(np.radians(10)):.3f} N*m")

print("\n== 6. C-stand overturning with the arm cantilevered ==")
stand_m, base_r = 9.0, 0.45   # kg, m (turtle-base leg reach) [assumption for a stainless C-stand]
for reach in (0.5, 0.7):
    M_load = m * g0 * reach + 1.5 * g0 * reach / 2   # arm mass 1.5 kg at half reach [assumption]
    M_res = stand_m * g0 * base_r
    print(f"arm reach {reach} m: overturning {M_load:.1f} N*m vs stand restoring {M_res:.1f} N*m "
          f"-> {'OK' if M_res > 1.5*M_load else 'sandbag'} (a 7 kg sandbag adds {7*g0*base_r:.0f} N*m)")

print("\n== 7. Where the stand puts things at the corrected pose ==")
cg = G.pose_point(G.CG_LOCAL, *POSE) + np.array([0, 0, G.BENCH_OFFSET])
gb = G.pose_point(G.GRIP_BASE, *POSE) + np.array([0, 0, G.BENCH_OFFSET])
print(f"gimbal (at the CG proxy) at bench xyz {cg.round(0)}; cable exit {gb.round(0)}; "
      "umbilical apex ~420-450 mm above the bench about 0.3-0.5 m further along -Y")
