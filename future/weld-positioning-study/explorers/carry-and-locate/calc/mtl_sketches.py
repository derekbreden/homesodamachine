"""Wave-2 branch sketches on machine-that-learns' B and C, drawn with the same three-view sketcher.
B geometry follows their b-rcm-gun-carriage.md (arc R 285 in the plane 40 mm outboard of the dot,
yoke bearings on the grip axis at the grip base and 125 mm ahead); C follows their hexapod_check.py."""
import numpy as np
from pathlib import Path
from sketch_lib import Sketch, bench
from pose import pose_point, LOCAL, JOINT, rot_matrix

OUT = Path(__file__).resolve().parent.parent / "sketches"
POSE = (45, 30, -15)
D = JOINT.copy()
gp = lambda l: bench(pose_point(np.asarray(l, float), *POSE))
DOT = bench(D)
GB = gp(LOCAL["grip_base"])
R = rot_matrix(*POSE)


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)


def ring(s, centre, axis, radius, a0, a1, color, w, dash=None):
    ax = unit(axis); p = unit(np.cross(ax, [0, 0, 1])); q = np.cross(ax, p)
    pts = [centre + radius * (np.cos(t) * p + np.sin(t) * q) for t in np.radians(np.linspace(a0, a1, 60))]
    s.poly(pts, color, w, dash)
    return p, q


def sketch_b():
    s = Sketch("B + float (on machine-that-learns' RCM carriage): the chain locates, a float and a riding saddle carry")
    s.station(POSE, cable=False)
    # arc about the hole axis, in the plane 40 mm outboard of the dot
    for rr, w, dash in ((271, 1.5, None), (299, 1.5, None), (285, 0.8, "6,4")):
        s.poly([DOT + np.array([40, -rr * np.cos(e), rr * np.sin(e)]) for e in np.radians(np.linspace(4, 60, 40))], "#5a9a3a", w, dash)
    e = np.radians(31)
    car = DOT + np.array([40, -285 * np.cos(e), 285 * np.sin(e)])
    s.dot(car, "#5a9a3a", 5)
    s.label(car, "arc carriage", "#5a9a3a", 8, -6, 10, views=("elevY", "elevX"))
    stub = bench(D + np.array([-33.1, -123.7, 73.9]))
    s.line(car, GB, "#963", 3.5); s.line(GB, stub, "#963", 2.5)
    s.dot(stub, "#963", 4)
    s.label(stub, "stub bearing (grip axis)", "#963", 6, 14, 9.5, views=("elevY",))
    # open C-ring roll bearing around the cable exit, gap on top
    ga = GB - DOT
    ring(s, GB, ga, 45, 190, 350 + 180, "#963", 2.5)
    s.label(GB, "open C-ring roll bearing (cable drops in)", "#963", 8, 26, 9.5, views=("elevY", "elevX"))
    # Y carriage, stages and column (schematic)
    yc = DOT + np.array([40, -330, 420])
    s.poly([yc + [-30, -60, 0], yc + [-30, 60, 0], yc + [-30, 60, 30], yc + [-30, -60, 30], yc + [-30, -60, 0]], "#7a9a8a", 2, views=("elevY",))
    s.line(yc, car, "#555", 3)
    s.label(yc, "Y carriage (X, Z above; column behind)", "#555", -40, -12, 9.5, views=("elevY", "elevX"))
    # float: attached ~40 mm off the CoM, line up to the ceiling
    com = gp([0, -25, 190])
    att = com + R @ np.array([36, -13, -38])
    s.dot(com, "#555", 3)
    s.line(att, att + np.array([0, 0, 1100]), "#555", 1.4, "6,3")
    s.dot(att, "#e67e22", 4)
    s.label(att + np.array([0, 0, 420]), "balancer ~90 % of gun+shell+yoke, line >= 1.2 m", "#e67e22", 5, 0, 9.5, views=("elevY", "elevX"))
    s.label(att, "attach ~40 mm off CoM: every drive loaded one way", "#e67e22", 6, 14, 9.5, views=("elevX",))
    # cable: from the exit through the C-ring to a saddle riding on the arc carriage, then over a big saddle
    gdir = unit(gp(LOCAL["grip_base"] + 60 * unit(LOCAL["grip_end"] - LOCAL["grip_start"])) - GB)
    sad = car + np.array([30, -90, 90])
    pts = [GB, GB + 80 * gdir, sad, sad + np.array([0, -150, 160]), sad + np.array([0, -380, 200]),
           sad + np.array([0, -600, 60]), sad + np.array([0, -650, -300])]
    s.poly(pts, "#6a3d9a", 3)
    s.dot(sad, "#6a3d9a", 5)
    s.label(sad, "first cable support rides the arc carriage", "#6a3d9a", 6, -8, 9.5, views=("elevY", "elevX"))
    s.label(DOT, "dot", "#d00", 6, 14, 10)
    notes = [
        "Without a float (3 kg gun+shell+yoke): arc drive 1.9-5.7 N·m, roll drive -0.8..+3.2 N·m (reverses inside the workspace), Y-carriage moment 4.1-8.5 N·m.",
        "Float at the CoM on a 1.5 m line: arc <= 0.44, roll <= 0.09 N·m, Y-carriage <= 0.67 N·m - but a drive near zero load has no chosen backlash side.",
        "Float at 90 % attached ~40 mm off the CoM: arc +0.55..+1.70, roll +0.60..+1.46 N·m (one sign everywhere), Z carries a steady 3 N down.",
        "Cable's first support on the arc carriage: X/Y/Z/tilt move the cable with the gun; only roll changes the free span (twist ~0.87x roll at the exit in the proxy).",
        "Open C-ring: three rollers in a 120 deg sector, ring >= 190 deg for +/-25 deg of roll, so the umbilical and wire conduit drop in without unplugging the QBH.",
    ]
    (OUT / "X-mtl-B-float-and-open-ring.svg").write_text(s.svg(notes))


def sketch_c():
    s = Sketch("C + preload (on machine-that-learns' hexapod): a central gas spring keeps all six legs in tension")
    s.station(POSE)
    P0 = D + np.array([-77.9, -105.1, 153.5]); n = unit([0.775, 0.158, 0.612])
    u = unit(np.cross(n, [0, 0, 1])); v = np.cross(n, u)
    B0 = P0 + 190 * n
    plat = [bench(P0 + 60 * (np.cos(np.radians(a)) * u + np.sin(np.radians(a)) * v)) for a in (-10, 10, 110, 130, 230, 250)]
    base = [bench(B0 + 120 * (np.cos(np.radians(a)) * u + np.sin(np.radians(a)) * v)) for a in (-50, 50, 70, 170, 190, 290)]
    ring(s, bench(P0), n, 60, 0, 360, "#963", 2.5)
    ring(s, bench(B0), n, 120, 0, 360, "#555", 3)
    for p, b in zip(plat, base):
        s.line(p, b, "#1a9a5a", 2)
    s.line(bench(P0), bench(B0), "#e67e22", 5)
    s.label(bench((P0 + B0) / 2), "gas spring, ~110-185 N push", "#e67e22", 8, 0, 10)
    s.label(bench(B0), "base ring (on a lockable carrier)", "#555", 8, -8, 9.5, views=("elevY", "elevX"))
    s.label(bench(P0), "platform = seat on the shell", "#963", 8, 14, 9.5, views=("elevY", "elevX"))
    s.label(DOT, "dot (software pivot)", "#d00", 6, 14, 10)
    notes = [
        "Their geometry, 2 kg gun+shell: under gravity alone three legs are in compression and three in tension (+20, -12, -2, +6, -3, +4 N).",
        "Across +/-7 deg about the dot with 5 N trigger / 5 N cable / 3 N wire-drag disturbances, four legs change sign: nut and rod-end play goes both ways.",
        "A push between base and platform (internal preload, gas spring on the hexapod axis) keeps every leg in tension if it is ~185 N,",
        "or ~110 N with the gun floated, the trigger closed inside the shell and the cable carried. Play then becomes a fixed offset the camera removes once.",
        "Tr8x8 4-start leads back-drive; under preload the legs creep when the motors release. Tr8x2 self-locks, or keep holding current.",
    ]
    (OUT / "X-mtl-C-preloaded-hexapod.svg").write_text(s.svg(notes))





def sketch_e():
    s = Sketch("E  Switch-locked skate: the float carries, a magnetic shoe on a steel plate locates, magnetic stops remember")
    s.station(POSE)
    com = gp([0, -25, 190])
    s.line(com, com + np.array([0, 0, 1000]), "#555", 1.4, "6,3")
    s.dot(com, "#555", 3)
    s.label(com + np.array([0, 0, 480]), "spring balancer ~95-100 % (carries only)", "#555", 5, 0, 9.5, views=("elevY", "elevX"))
    t0 = gp([0, 0, 70])
    shoe = np.array([120.0, -20.0, 285.0])
    s.line(t0, shoe + np.array([0, 0, 12]), "#2b7bb9", 4)
    s.label(t0, "tongue (metal) from the shell", "#2b7bb9", -150, -8, 9.5, views=("elevX",))
    # shoe and three ball feet
    s.poly([shoe + [-28, -17, 0], shoe + [28, -17, 0], shoe + [28, 17, 0], shoe + [-28, 17, 0], shoe + [-28, -17, 0]], "#c0392b", 2, views=("plan",))
    s.poly([shoe + [-28, 0, 0], shoe + [28, 0, 0], shoe + [28, 0, 46], shoe + [-28, 0, 46], shoe + [-28, 0, 0]], "#c0392b", 2, views=("elevX",))
    s.poly([shoe + [0, -17, 0], shoe + [0, 17, 0], shoe + [0, 17, 46], shoe + [0, -17, 46], shoe + [0, -17, 0]], "#c0392b", 2, views=("elevY",))
    for a in (90, 210, 330):
        s.dot(shoe + 25 * np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0]), "#c0392b", 2.5, views=("plan",))
    s.label(shoe + [0, 0, 46], "switchable-magnet shoe on 3 balls", "#c0392b", -60, -8, 9.5)
    # steel plate
    pz = 285.0
    s.poly([[80, -110, pz], [210, -110, pz], [210, 70, pz], [80, 70, pz], [80, -110, pz]], "#16a085", 2, views=("plan",))
    s.line([80, 0, pz], [210, 0, pz], "#16a085", 4, views=("elevX",))
    s.line([0, -110, pz], [0, 70, pz], "#16a085", 4, views=("elevY",))
    s.label([210, 70, pz], "ground steel plate (X, plan angle, don't-care slide)", "#16a085", -250, -10, 9.5, views=("plan",))
    # post
    s.line([175, -20, pz], [175, -20, 0], "#16a085", 5, views=("elevX", "elevY"))
    s.label([175, -20, 150], "steel post to the rotator's frame; plate height = Z", "#16a085", 6, 0, 9.5, views=("elevX",))
    # magnetic stops
    for p in ([120, -45, pz], [155, -20, pz]):
        s.poly([np.array(p) + [-10, -6, 0], np.array(p) + [10, -6, 0], np.array(p) + [10, 6, 0], np.array(p) + [-10, 6, 0], np.array(p) + [-10, -6, 0]], "#8e44ad", 2, views=("plan",))
    s.label([160, -50, pz], "magnetic stops = the taught pose", "#8e44ad", 6, 14, 9.5, views=("plan",))
    s.label(DOT, "dot", "#d00", 6, 14, 10)
    notes = [
        "Unlocked: the balancer carries the gun; ~3 N of residual weight keeps the three balls on the plate; a finger slides it (friction ~0.6 N).",
        "Locked: MagJig 95 (43 kg normal breakaway on full contact; ~30-50 % across the ball stand-off, estimate) presses the balls already touching.",
        "Lock shift: ball approach rises from 0.2 to ~3 um; no load changes hands because the float keeps carrying. The knob's twist must react on the shoe.",
        "Holds: ~24-39 N sideways before slip, ~30-50 N at the dot before a ball unloads; wire push 2 N moves the dot ~6 um through ~360 N/mm (estimate).",
        "Debris is the enemy: a 0.05 mm speck under a ball moves the dot ~0.1 mm. Wipe, lock, look (eye, indicator or camera).",
        "Tube change: magnet off, lift 15-20 mm on the float, change, set down against the magnetic stops, magnet on.",
    ]
    (OUT / "E-switch-lock-skate.svg").write_text(s.svg(notes))


def sketch_f():
    s = Sketch("F  Nose on the work, tail on a table, weight on a float (work-as-datum's hung nose + switch lock + float + camera)")
    s.station(POSE)
    N = gp([0, 0, 30])
    ga_ = unit(GB - DOT)
    T = GB + 40 * ga_
    nt = unit(T - N); across = unit(np.cross([0, 0, 1.0], nt))
    # plate hanger on the endcap plate: hub, wheels, stalk, nose loop
    hub = bench(np.array([0.0, 0.0, 146.05 + 20]))
    s.dot(hub, "#1a4f8a", 5)
    s.label(hub, "plate hanger: port nipples, centre pin, 3 wheels (work-as-datum)", "#1a4f8a", -60, 28, 9.5, views=("elevY", "elevX"))
    s.line(hub, N + np.array([0, 0, -10]), "#1a4f8a", 3)
    bar = unit(gp([0, 0, 31]) - N)
    ring(s, N, bar, 16, 0, 360, "#c0392b", 2.5)
    s.label(N, "V-loop with sprung jaw on the grooved nose collar (46 mm from dot)", "#c0392b", 10, -10, 9.5, views=("elevX",))
    s.line(hub, np.array([60.0, 260.0, hub[2]]), "#e67e22", 1.4, "6,3", views=("plan", "elevY"))
    s.label(np.array([60.0, 200.0, hub[2]]), "azimuth tether (don't-care spin; also a plan-angle trim)", "#e67e22", -40, -8, 9.5, views=("plan",))
    # tail: two ball transfers on a table, 120 mm apart across the nose-tail line
    tz = T[2] - 25
    b1, b2 = T + 60 * across + np.array([0, 0, -25]), T - 60 * across + np.array([0, 0, -25])
    s.line(T, b1, "#16a085", 2.5); s.line(T, b2, "#16a085", 2.5)
    s.dot(b1, "#16a085", 4); s.dot(b2, "#16a085", 4)
    tab = [T + np.array([-90, -70, -25]), T + np.array([90, -70, -25]), T + np.array([90, 70, -25]), T + np.array([-90, 70, -25])]
    s.poly(tab + [tab[0]], "#16a085", 2, views=("plan",))
    s.line(T + np.array([-90, 0, -25]), T + np.array([90, 0, -25]), "#16a085", 4, views=("elevX",))
    s.line(T + np.array([0, -70, -25]), T + np.array([0, 70, -25]), "#16a085", 4, views=("elevY",))
    s.line(T + np.array([0, 0, -25]), [T[0], T[1], 0], "#16a085", 5, views=("elevX", "elevY"))
    s.label(T + np.array([0, 0, -25]), "tail table: height screw = hole, cross-tilt screw = roll", "#16a085", -40, 28, 9.5, views=("elevX", "elevY"))
    s.label(b1, "ball transfers (roll freely)", "#16a085", 6, -6, 9.5, views=("plan",))
    # across link to a MagJig-braked carriage on a rail
    car = T + 150 * across + np.array([0, 0, -20])
    s.line(T, car, "#8e44ad", 2.5)
    s.dot(car, "#8e44ad", 5)
    s.label(car, "1-DOF link to a magnet-braked carriage = plan angle, locked", "#8e44ad", 6, 14, 9.5, views=("plan", "elevX"))
    # float, hooked off the CoM
    com = gp([0, -30, 200]); hook = com + R @ np.array([6, 59, -60])
    s.line(hook, hook + np.array([0, 0, 1000]), "#555", 1.4, "6,3")
    s.dot(hook, "#555", 4)
    s.label(hook + np.array([0, 0, 470]), "balancer ~77 %, hooked ~85 mm off the CoM (keeps both balls seated)", "#555", 5, 0, 9.5, views=("elevY", "elevX"))
    s.label(DOT, "dot", "#d00", 6, 14, 10)
    notes = [
        "Nose (work): a ball joint 46 mm from the dot on the plate being welded - follows runout, face tilt and tube length (work-as-datum D1, sprung jaw added).",
        "Tail (room table): two ball transfers set hole (height screw, 0.23 deg/mm) and roll (cross-tilt screw, ~1.1 deg/mm at 120 mm spacing).",
        "Plan angle: one ball-ended link to a carriage braked by a switchable magnet (0.23 deg per mm of tail slide). 3 + 2 + 1 = 6: determinate, nothing fights.",
        "A 2-ball magnetic shoe locked to the table would add 4 friction constraints: the nose's once-per-rev runout would then fight the tail. Hence rolling balls + a 1-DOF lock.",
        "Float and saddle carry weight and cable, so the tube carries ~nothing; tube length is re-trimmed by the table height (1 mm up = the 1 mm longer tube's 0.23 deg).",
        "Dot knobs: the stalk's XZ micro-stage (work-as-datum). Camera on the hanger's +Y side reads the dot in plate coordinates (machine-that-learns).",
    ]
    (OUT / "F-nose-and-tail.svg").write_text(s.svg(notes))


def sketch_era():
    s = Sketch("E-RA  Cup on the work holds the dot; the switch-locked skate holds the tail (work-as-datum's R-A + a roll pad)")
    s.station(POSE)
    bar = unit(gp([0, 0, 1]) - gp([0, 0, 0]))
    g = np.array([0, 0, -1.0]); e1 = unit(g - np.dot(g, bar) * bar); e2 = np.cross(bar, e1)
    Rs, al = 50.0, np.radians(35)
    ax, rho = Rs * np.cos(al), Rs * np.sin(al)
    c0 = DOT + ax * bar
    balls = [c0 + rho * (np.cos(t) * e1 + np.sin(t) * e2) for t in np.radians([0, 120, 240])]
    for b in balls:
        s.dot(b, "#c0392b", 4)
    ring(s, c0, bar, rho + 6, 0, 360, "#c0392b", 2.5)
    s.label(c0, "cup: 3 balls in a spherical band centred on the dot (R 50)", "#c0392b", 10, -14, 9.5, views=("elevX", "elevY"))
    hub = bench(np.array([0.0, 0.0, 146.05 + 20]))
    s.dot(hub, "#1a4f8a", 5)
    s.line(hub, c0 + rho * e2 * 1.2, "#1a4f8a", 3)
    s.label(hub, "plate hanger (work-as-datum)", "#1a4f8a", -40, 30, 9.5, views=("elevY", "elevX"))
    # tail: grip-base ball in a round vertical bore of the magnet shoe, on a room plate
    shoe = GB + np.array([0, 0, -20])
    s.poly([shoe + [-28, -17, -25], shoe + [28, -17, -25], shoe + [28, 17, -25], shoe + [-28, 17, -25], shoe + [-28, -17, -25]], "#c0392b", 2, views=("plan",))
    s.poly([shoe + [-28, 0, -25], shoe + [28, 0, -25], shoe + [28, 0, 20], shoe + [-28, 0, 20], shoe + [-28, 0, -25]], "#c0392b", 2, views=("elevX",))
    s.poly([shoe + [0, -17, -25], shoe + [0, 17, -25], shoe + [0, 17, 20], shoe + [0, -17, 20], shoe + [0, -17, -25]], "#c0392b", 2, views=("elevY",))
    s.dot(GB, "#c0392b", 4)
    s.label(GB, "grip-base ball in a round vertical bore (magnet shoe)", "#c0392b", 8, -10, 9.5)
    pz = shoe[2] - 25
    pl = [shoe + [-90, -80, -25], shoe + [90, -80, -25], shoe + [90, 80, -25], shoe + [-90, 80, -25]]
    s.poly(pl + [pl[0]], "#16a085", 2, views=("plan",))
    s.line(shoe + [-90, 0, -25], shoe + [90, 0, -25], "#16a085", 4, views=("elevX",))
    s.line(shoe + [0, -80, -25], shoe + [0, 80, -25], "#16a085", 4, views=("elevY",))
    s.line(shoe + [0, 0, -25], [shoe[0], shoe[1], 0], "#16a085", 5, views=("elevX", "elevY"))
    s.label(shoe + [0, 0, -25], "steel plate on a post from the rotator frame: X/Y slide = hole + plan", "#16a085", -60, 30, 9.5, views=("elevX", "elevY"))
    # roll pad: a second ball 40 mm off the grip axis rests on a screw pad on the same shoe
    side = unit(np.cross(unit(GB - DOT), [0, 0, 1.0]))
    rb = GB + 40 * side + np.array([0, 0, -8])
    s.line(GB, rb, "#8e44ad", 2.5); s.dot(rb, "#8e44ad", 4)
    s.label(rb, "roll ball on a screw pad on the shoe (1.4 deg/mm)", "#8e44ad", 6, 14, 9.5, views=("plan", "elevX"))
    com = gp([0, -25, 190])
    s.line(com, com + np.array([0, 0, 1000]), "#555", 1.4, "6,3"); s.dot(com, "#555", 3)
    s.label(com + np.array([0, 0, 470]), "balancer (carries); cup preload by spring, not by weight (my addition)", "#555", 5, 0, 9.5, views=("elevY", "elevX"))
    s.label(DOT, "dot = cup centre", "#d00", 6, 14, 10)
    notes = [
        "Cup (work): contact normals at the three balls pass through the dot, so the dot's translations are held by the plate being welded and all rotations are free.",
        "Tail (room): the magnet shoe's round bore holds the grip-base ball in X and Y only; its height is free, so runout and tube length never fight the lock.",
        "Sliding the shoe turns the gun about the dot: 0.21 deg per mm (hole and plan). A 0.1 mm speck under the shoe moves the dot ~nothing to first order.",
        "Roll (about the grip axis, dot to grip base) sits on a screw pad on the same shoe: one switch locks everything. Count: 3 + 2 + 1 = 6.",
        "Weak points left: the cup's centre must be the dot (calibrate by rotating and shimming); cup pads ~40 mm from the puddle; nipples in the ports.",
    ]
    (OUT / "E-RA-cup-and-tail.svg").write_text(s.svg(notes))


if __name__ == "__main__":
    sketch_era()
    sketch_b()
    sketch_c()
    sketch_e()
    sketch_f()
    print("wrote X-mtl-B, X-mtl-C, E-switch-lock-skate, F-nose-and-tail, E-RA-cup-and-tail")
