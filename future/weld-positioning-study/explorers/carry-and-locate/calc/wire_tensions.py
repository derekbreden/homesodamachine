"""Wire-located suspension (idea B): are all six wires in tension under gravity + a bungee preload?
Solves the 6x6 statics for the FIRST layout drawn (W4 nearly vertical, W5 toward -Y, W6 at the housing back), which fails: W4 and W6 go slack. wire_layout_search.py finds layouts that work. Gun 1.0 kg with CoM 'toward grip' (assumed);
bungee pulls straight down at the grip base. Also: the wrench each wire resists if a disturbance acts."""
import numpy as np
from pose import pose_point, LOCAL, JOINT

POSE = (45, 30, -15)
D = JOINT.copy()
def unit(az, el):
    az, el = np.radians(az), np.radians(el)
    return np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
gp = lambda l: pose_point(np.asarray(l, float), *POSE)
gb, ht = gp(LOCAL["grip_base"]), gp(LOCAL["housing_top_back"])
wires = [(D + 70*unit(90, 55), unit(90, 55)), (D + 70*unit(-30, 55), unit(-30, 55)), (D + 70*unit(210, 55), unit(210, 55)),
         (gb, unit(20, 65)), (gb, unit(70, 15)), (ht, unit(160, 50))]
A = np.zeros((6, 6))
for i, (p, u) in enumerate(wires):
    A[:3, i] = u
    A[3:, i] = np.cross(p - D, u)
def solve(F_list):
    F = np.zeros(3); M = np.zeros(3)
    for p, f in F_list:
        F += f; M += np.cross(p - D, f)
    return np.linalg.solve(A, -np.concatenate([F, M]))
com = gp([0, -25, 190])
print("condition number of the wire matrix:", round(np.linalg.cond(A), 1))
for Fb in (0, 10, 25, 50):
    t = solve([(com, np.array([0, 0, -9.81])), (gb, np.array([0, 0, -Fb]))])
    print(f"bungee {Fb:2d} N: tensions W1..W6 = {np.round(t, 1)} N  {'ALL TAUT' if (t > 0).all() else 'SLACK: ' + str([i+1 for i in np.where(t <= 0)[0]])}")
# a 5 N push at the dot in each direction on top of gravity + 25 N bungee
base = [(com, np.array([0, 0, -9.81])), (gb, np.array([0, 0, -25.0]))]
for name, f in (("+X", [5,0,0]), ("-X", [-5,0,0]), ("+Y", [0,5,0]), ("-Y", [0,-5,0]), ("+Z (lift)", [0,0,5]), ("-Z", [0,0,-5])):
    t = solve(base + [(D, np.array(f, float))])
    print(f"5 N at the dot {name:9s}: {np.round(t,1)} {'ok' if (t>0).all() else 'SLACK'}")
tp = gp([0, -40, 175])
for name, f in (("trigger 5 N into grip (+local y)", None),):
    R = np.column_stack([gp(e) - gp([0,0,0]) for e in np.eye(3)])
    fw = R @ np.array([0, 5.0, 0])
    t = solve(base + [(tp, fw)])
    print(f"{name}: {np.round(t,1)} {'ok' if (t>0).all() else 'SLACK'}")
