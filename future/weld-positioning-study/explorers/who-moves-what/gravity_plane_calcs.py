"""Wave 4 combination: gravity in the gun's plane (tilted station, nose in a dot-centred
cup on the work, one gravity-tensioned hole wire, weightless roll and yaw).

Room frame at the tilt tau (about the station tangent through the dot), origin at the dot.
Supports: a cup centred on the dot (force through the dot, no moment), a vertical wire
attached on the grip axis at distance s from the dot (one-knob-one-parameter's hole knob),
a horizontal X fork at the grip base (a yaw constraint), a roll lock (torque about the grip axis).
Solves the three moment equations about the dot for (wire T, fork F, roll torque), then the
cup force. Gun: CoM proxy local (0, 0, 185.5); masses are estimates.
Run: tools/cad-venv/bin/python gravity_plane_calcs.py
"""
import math
import numpy as np
from geometry import world, FEATURES, FIBER_DIR_LOCAL
from tilt_calcs import Ry, RECIPE, DOT

G = 9.81


def frame(tau):
    R = Ry(tau)
    rm = lambda p: R @ (np.asarray(p, float) - DOT)
    dot = np.zeros(3)
    gb = rm(world(FEATURES['grip_base_QBH'], RECIPE))
    com = rm(world((0.0, 185.5), RECIPE))
    g = gb / np.linalg.norm(gb)
    fib = R @ (world((FEATURES['grip_base_QBH'][0] + 100 * FIBER_DIR_LOCAL[1], FEATURES['grip_base_QBH'][1] + 100 * FIBER_DIR_LOCAL[2]), RECIPE)
               - world(FEATURES['grip_base_QBH'], RECIPE)) / 100
    nose = rm(world((0.0, 30.0), RECIPE))       # ~46 mm from the dot along the barrel
    return R, gb, com, g, fib, nose


def gravity_torques(tau, m=1.5):
    R, gb, com, g, fib, nose = frame(tau)
    W = np.array([0, 0, -m * G])
    M = np.cross(com / 1000, W)                 # N*m about the dot
    hole = R @ np.array([math.cos(math.radians(RECIPE[2])), math.sin(math.radians(RECIPE[2])), 0.0])
    return dict(grip=np.dot(M, g), hole=np.dot(M, hole), vertical=M[2])


def statics(tau, m=1.5, s=279.2, extra=(), ballast=(0.0, None)):
    """extra: list of (point, force N). ballast: (mass kg, point) added as a weight."""
    R, gb, com, g, fib, nose = frame(tau)
    a = g * s                                    # wire attachment on the grip axis
    loads = [(com, np.array([0, 0, -m * G]))] + list(extra)
    if ballast[0] > 0:
        loads.append((ballast[1] if ballast[1] is not None else gb, np.array([0, 0, -ballast[0] * G])))
    Mload = sum(np.cross(p, f) for p, f in loads)
    # unknowns: T (wire +z at a), F (fork +x at gb), L (roll torque about g)
    A = np.column_stack([np.cross(a, [0, 0, 1.0]), np.cross(gb, [1.0, 0, 0]), g])
    T, F, L = np.linalg.solve(A, -Mload)
    Fload = sum(f for _, f in loads)
    cup = -(Fload + T * np.array([0, 0, 1.0]) + F * np.array([1.0, 0, 0]))
    return T, F, L / 1000, cup


if __name__ == "__main__":
    print("== gravity torque about Derek's three axes (1.5 kg gun, CoM proxy), N*m")
    for tau in (0, 20, 30, 32.5, 35, 45):
        t = gravity_torques(tau)
        print(f"   tau {tau:5.1f}: grip {t['grip']:+.3f}  hole {t['hole']:+.3f}  vertical {t['vertical']:+.3f}")
    R, gb, com, g, fib, nose = frame(32.5)
    print(f"\n== at tau* 32.5: grip base {np.round(gb,1)}, CoM {np.round(com,1)}, nose (46 mm up the barrel) {np.round(nose,1)}, fiber dir {np.round(fib,2)}")
    print("\n== statics at tau*: cup at the dot, vertical hole wire on the grip axis at s, X fork at the grip base, roll lock")
    for s in (279.2, 200.0, 140.0):
        for bal in (0.0, 1.0, 2.0):
            for lab, ex in (("gravity only", ()), ("+ 5 N cable along its exit", ((gb, 5.0 * fib),)), ("+ 5 N cable straight up", ((gb, np.array([0, 0, 5.0])),))):
                T, F, L, cup = statics(32.5, s=s, extra=ex, ballast=(bal, gb))
                print(f"   s {s:5.1f}, ballast {bal:.0f} kg at grip base, {lab:28s}: wire {T:6.1f} N, fork {F:+5.1f} N, roll lock {L:+.3f} N*m, cup {np.round(cup,1)} N (|cup| {np.linalg.norm(cup):.1f})")
    print("\n== same supports upright (tau 0) for comparison, gravity only")
    for s in (279.2,):
        T, F, L, cup = statics(0.0, s=s)
        print(f"   s {s}: wire {T:.1f} N, fork {F:+.1f} N, roll lock {L:+.3f} N*m, cup {np.round(cup,1)}")
    # cup load line vs the beam: the cup must hold the nose; angle of the cup force from vertical
    T, F, L, cup = statics(32.5, s=279.2, ballast=(1.0, gb))
    print(f"\n== cup reaction direction at tau* (1 kg ballast): {np.degrees(np.arccos(-cup[2]/np.linalg.norm(cup))):.1f} deg from straight down")
