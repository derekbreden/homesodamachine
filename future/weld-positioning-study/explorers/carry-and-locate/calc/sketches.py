"""Generate the arrangement sketches (SVG) from the scene pose. Run from this directory."""
import numpy as np
from pathlib import Path
from sketch_lib import Sketch, bench
from pose import pose_point, LOCAL, JOINT, BENCH_Z, R_IN, TUBE_H

OUT = Path(__file__).resolve().parent.parent / "sketches"
POSE = (45, 30, -15)
DOT = bench(JOINT)
RIM_Z = BENCH_Z + TUBE_H


def gp(local):
    return bench(pose_point(np.asarray(local, float), *POSE))


gdir = (LOCAL["grip_end"] - LOCAL["grip_start"]) / np.linalg.norm(LOCAL["grip_end"] - LOCAL["grip_start"])
T = gp([0, 0, 40])                            # tip loop on the graduated tube
B = gp(LOCAL["grip_base"] + 40 * gdir)        # base loop round the cable / shell collar
C = gp(LOCAL["housing_top_back"])             # third ring
COM = gp([0, -25, 190])
TOP = 950


# ---------------------------------------------------------------- A: suspension, original
def suspension_original():
    s = Sketch("A  Suspension as Derek described it: two loops on wires + one bungee axis; an arm grips the shell")
    s.station(POSE)
    # overhead bar (pegboard boom / ceiling) along Y and a second along X for bungee posts
    s.line([-300, -330, TOP], [300, -330, TOP], "#8b5a2b", 3, views=("elevX",))
    s.line([60, -330, TOP], [60, 250, TOP], "#8b5a2b", 3, views=("elevY", "plan"))
    s.label([60, 200, TOP], "overhead bar: pegboard boom or ceiling (CARRIES only)", "#8b5a2b", -150, -8, 10, views=("elevY",))
    for P, name in ((T, "tip loop"), (B, "base loop (cable + wire)")):
        s.line(P, [P[0], P[1], TOP], "#555", 1.2)
        s.dot(P, "#8b5a2b", 5)
        s.label(P, name, "#8b5a2b", 7, 12, 10)
        # bungee pair along X to posts
        for xe in (P[0] + 230, P[0] - 330):
            s.line(P, [xe, P[1], P[2]], "#e67e22", 1.6, "7,3", views=("plan", "elevX"))
            s.dot([xe, P[1], P[2]], "#e67e22", 3, views=("plan", "elevX"))
    s.label([T[0] + 230, T[1], T[2]], "bungee post", "#e67e22", -20, -8, 9, views=("elevX", "plan"))
    # third ring, dashed
    s.line(C, [C[0], C[1], TOP], "#555", 1.0, "4,4")
    s.dot(C, "#8b5a2b", 4)
    s.label(C, "3rd ring (option)", "#8b5a2b", -40, -16, 10)
    # arm grip options
    for loc, name in (([0, 17, 60], "A1 tip grip"), ([0, 17, 190], "A2 at CoM"), (LOCAL["grip_base"], "A3 at base"),
                      ([0, 17, 253], "A4 roll lever")):
        p = gp(loc)
        s.dot(p, "#2b7bb9", 4)
        s.label(p, name, "#2b7bb9", 6, 4, 9.5, views=("elevY", "elevX"))
    s.label(DOT, "dot", "#d00", 6, 14, 10)
    notes = [
        "Wire in Z at each loop: stiff vertically (EA/L ~ 13-260 N/mm), a pendulum horizontally (T/L ~ 0.01 N/mm for 5 N on 500 mm).",
        "Bungee pair in X: ~0.1 N/mm. So the loops CARRY (weight, cable) and centre softly; 1 N moves an unrestrained gun ~10 mm.",
        "Put the bungee axis on X (radial) and leave Y (tangent) as the pendulum: a 2 mm tangent shift is only 0.03 mm off the circle.",
        "At this pose the tip loop carries ~56-68 % of the gun and the base loop the rest plus the cable; the CoM sits 40-55 mm off",
        "the tip-base line, so ~0.39-0.54 N·m per kg of gun must come from the arm or the 3rd ring (3rd ring belongs at the housing back).",
        "Arm grip A1 locates the dot directly; A3 uses the tip loop as a Z fulcrum (dot moves ~1/5 of A3's vertical motion); A4 rolls about the loop line.",
    ]
    (OUT / "A-suspension-original.svg").write_text(s.svg(notes))


# ---------------------------------------------------------------- A2: tension-located (wires + bungee preload)
def unit(az, el):
    az, el = np.radians(az), np.radians(el)
    return np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])


def wire_located():
    s = Sketch("B  Wire-located suspension: three wires whose lines meet at the dot + three far wires + a bungee preload")
    s.station(POSE)
    a, L = 70, 400
    anchors = []
    for i, (az, el) in enumerate(((90, 55), (-30, 55), (210, 55))):
        u = unit(az, el)
        A = DOT + a * u
        P = DOT + (a + L) * u
        s.line(DOT, A, "#c0392b", 0.9, "2,3")          # virtual segment through the dot
        s.line(A, P, "#c0392b", 1.8)
        s.dot(A, "#c0392b", 3.5)
        s.dot(P, "#555", 4)
        anchors.append(P)
        s.label(P, f"W{i+1}", "#c0392b", 5, -5, 10)
    s.label(DOT + 70 * unit(90, 55), "collar near the nozzle", "#c0392b", 6, 12, 9.5, views=("elevY",))
    gb = gp(LOCAL["grip_base"])
    ht = gp(LOCAL["housing_top_back"])
    far = [(gb, unit(32, 43), "W4"), (gb, unit(184, 72), "W5"), (ht, unit(-158, 12), "W6 (grip-axis roll)")]
    for p, u, name in far:
        P = p + 330 * u
        s.line(p, P, "#8e44ad", 1.8)
        s.dot(p, "#8e44ad", 3.5)
        s.dot(P, "#555", 4)
        anchors.append(P)
        s.label(P, name, "#8e44ad", 5, -5, 10)
    # anchor frame: connect anchors (triangulated top frame) and legs to the bench
    for i in range(len(anchors)):
        for j in range(i + 1, len(anchors)):
            if np.linalg.norm(anchors[i] - anchors[j]) < 420:
                s.line(anchors[i], anchors[j], "#aaa", 0.8, "3,3")
    for P in anchors[:3]:
        s.line(P, [P[0] * 1.6, P[1] * 1.6, 0], "#aaa", 0.8, "3,3")
    # two soft preloads: from the grip base (down, slightly out) and from a shell arm over the +X rim (straight down)
    bu = unit(-133, -88)
    s.line(gb, gb + 420 * bu, "#e67e22", 2.0, "7,3")
    s.label(gb + 300 * bu, "preload bungee 1 (~38 N)", "#e67e22", 6, 0, 10)
    arm = bench(np.array([115.0, 9.0, 200.0]))
    s.line(gp([0, 0, 70]), arm, "#2b7bb9", 3)
    s.line(arm, [arm[0], arm[1], 30], "#e67e22", 2.0, "7,3")
    s.label([arm[0], arm[1], 120], "preload bungee 2 (~36 N) from a shell arm", "#e67e22", 6, 0, 10, views=("elevX", "plan"))
    # grip axis
    s.line(DOT, gb, "#2b7bb9", 0.9, "6,3")
    s.label((DOT + gb) / 2, "grip axis", "#2b7bb9", 5, 0, 9.5, views=("elevY",))
    s.label(DOT, "dot = virtual ball joint", "#d00", 6, 14, 10)
    notes = [
        "W1-W3: lines meet at the dot, so turning the gun about the dot leaves their lengths unchanged to first order; their lengths set dot XYZ.",
        "Finite turns: dot drifts ~0.02-0.05 mm at 2 deg, 0.13-0.33 mm at 5 deg, 0.5-1.3 mm at 10 deg (a = 70 mm). A real pivot 56 mm up: 2 mm at 2 deg.",
        "W4-W5 hold the grip base on its sphere about the dot (hole-axis and vertical-axis turns); W6 alone sets roll about the grip axis.",
        "1 mm 7x7 stainless, L = 400: dot stiffness ~64 / 64 / 262 N/mm from the wires alone; the anchor frame is in series and must be triangulated.",
        "Two soft bungees (~38 N + ~36 N) + gravity keep all six wires taut with >= 6.8 N to spare under 5 N pushes at the dot and a 5 N trigger push.",
        "Anchors drawn schematically; the frame they sit on is the reference and belongs to the rotator's frame, not to the pegboard.",
    ]
    (OUT / "B-wire-located-suspension.svg").write_text(s.svg(notes))


# ---------------------------------------------------------------- C: float + kinematic dock
def float_dock():
    s = Sketch("C  Float and dock: a balancer and a cable saddle carry; a magnet-preloaded kinematic seat locates")
    s.station(POSE)
    # balancer above the CoM
    s.line(COM, [COM[0], COM[1], 860], "#555", 1.2)
    s.poly([[COM[0]-25, COM[1]-25, 860], [COM[0]+25, COM[1]-25, 860], [COM[0]+25, COM[1]+25, 860],
            [COM[0]-25, COM[1]+25, 860], [COM[0]-25, COM[1]-25, 860]], "#555", 1.5)
    s.poly([[COM[0]-25, COM[1], 860], [COM[0]+25, COM[1], 860], [COM[0]+25, COM[1], 920], [COM[0]-25, COM[1], 920],
            [COM[0]-25, COM[1], 860]], "#555", 1.5, views=("elevY", "elevX"))
    s.label([COM[0], COM[1], 920], "spring balancer (carries ~90 % of gun)", "#555", -60, -8, 10, views=("elevY", "elevX"))
    s.dot(COM, "#555", 3)
    # tongue from the barrel region out over the rim to the seat (+X side)
    t0 = gp([0, 0, 70])
    seat = np.array([118.0, -10.0, 300.0])
    s.line(t0, seat, "#2b7bb9", 4)
    s.label(t0, "shell tongue", "#2b7bb9", 6, -6, 9.5, views=("elevX",))
    for ang in (90, 210, 330):
        p = seat + 35 * np.array([0, np.cos(np.radians(ang)), np.sin(np.radians(ang))])
        s.dot(p, "#2b7bb9", 4)
    # seat plate + adjustment stack + post on the bench/rotator frame
    s.poly([seat + [8, -45, -40], seat + [8, 45, -40], seat + [8, 45, 40], seat + [8, -45, 40], seat + [8, -45, -40]], "#16a085", 2)
    s.label(seat, "3 V-seats + switchable magnet", "#16a085", 12, -44, 10, views=("elevX", "elevY"))
    stack = seat + np.array([60, 0, 0])
    s.poly([stack + [-25, -40, -40], stack + [25, -40, -40], stack + [25, 40, -40], stack + [-25, 40, -40], stack + [-25, -40, -40]], "#16a085", 1.2, views=("plan",))
    s.poly([stack + [-25, 0, -40], stack + [25, 0, -40], stack + [25, 0, 40], stack + [-25, 0, 40], stack + [-25, 0, -40]], "#16a085", 1.2, views=("elevX",))
    s.label(stack, "adjustment stack (sets the pose; carries only preload)", "#16a085", -40, 58, 9.5, views=("elevX",))
    s.line(stack + [0, 0, -40], [stack[0], stack[1], 36], "#16a085", 5)
    s.label([stack[0], stack[1], 120], "post to the frame shared with the rotator", "#16a085", 6, 0, 9.5, views=("elevX",))
    # trigger presser
    tp = gp([0, -40, 175])
    s.dot(tp, "#9b59b6", 4)
    s.label(tp, "shell-mounted trigger presser (internal force)", "#9b59b6", -230, 16, 9.5, views=("elevY",))
    s.label(DOT, "dot", "#d00", 6, 14, 10)
    notes = [
        "Loads: balancer takes ~90 % of the gun at its CoM (near-constant force); a saddle takes the umbilical before it reaches the gun.",
        "Position: three balls on the shell's tongue sit in three V-seats (hardened rods) on an adjustment stack; a switchable magnet preloads them.",
        "Tip-off: seat radius 50 mm, 40 N preload holds ~17 N at the wire tip but only ~5 N at the trigger 200 mm away -> no hand on the trigger.",
        "Lift-off: switch the magnet off; the balancer lifts the gun; the seat keeps the setting. Re-docking repeats the pose to seat repeatability.",
        "Stuck wire / bump: over-limit loads pop the seat (breakaway) instead of bending the wire guide or the stack; re-seat and check the dot.",
        "The stack only sees tens of newtons, so small optical-class stages fit; the post + stack + frame + rotator form the whole position loop.",
    ]
    (OUT / "C-float-and-dock.svg").write_text(s.svg(notes))


# ---------------------------------------------------------------- D: rim-riding carriage
def rim_carriage():
    s = Sketch("D  Rim carriage: the turning tube carries a C-ring on rollers; the gun hangs from the ring; a float trims the load")
    s.station(POSE)
    z = RIM_Z
    # C-ring riding on rim, open near the station (0 deg)
    arc = [np.array([62.5 * np.cos(t), 62.5 * np.sin(t), z + 8]) for t in np.radians(np.linspace(24, 336, 60))]
    s.poly(arc, "#16a085", 4)
    for ang, name in ((30, "pinch pair + rim roller"), (180, "rim roller (Z only)"), (330, "pinch pair + rim roller")):
        p = np.array([62.5 * np.cos(np.radians(ang)), 62.5 * np.sin(np.radians(ang)), z + 4])
        s.dot(p, "#16a085", 5)
        s.label(p, name, "#16a085", 6, -6 if ang != 180 else 14, 9.5, views=("plan",))
    # local radial reference near the station
    for ang in (-12,):
        p = np.array([R_IN * np.cos(np.radians(ang)), R_IN * np.sin(np.radians(ang)), z - 5])
        s.dot(p, "#c0392b", 4)
        s.label(p, "D2: local cap/bore shoe (option)", "#c0392b", 6, 24, 9.5, views=("plan",))
    # post from the ring at 180 deg up to the gun stack at the housing back
    post0 = np.array([-62.5, 0, z + 8])
    post1 = np.array([-62.5, 0, 470])
    s.line(post0, post1, "#16a085", 4)
    hb = gp(LOCAL["housing_back"])
    s.line(post1, hb, "#16a085", 4)
    s.label(post1, "post + adjustment stack", "#16a085", -120, -8, 10, views=("elevX", "elevY"))
    # float from overhead to the post top
    s.line(post1, [post1[0], post1[1], 900], "#555", 1.2, "5,3")
    s.label([post1[0], post1[1], 880], "float: balancer sets rim preload (~10-20 N)", "#555", 5, 0, 9.5, views=("elevX",))
    # tether against spinning
    s.line(post1 + [0, 0, -100], [-260, -200, 370], "#e67e22", 1.6, "7,3")
    s.label([-260, -200, 370], "soft tether (spin only; don't-care DOF)", "#e67e22", 5, 12, 9.5, views=("plan", "elevX"))
    s.label(DOT, "dot", "#d00", 6, 14, 10)
    notes = [
        "Rim rollers (3) set Z and both tilts from the rim plane; pinch pairs at +/-30 deg (a roller inside and outside the 1.65 mm lip) set the centre",
        "without pushing the tube sideways. Spin about the tube axis only slides the dot along the joint, so a soft tether is enough for it.",
        "Downward load inside the tube footprint cannot tip the tube; a net radial rim push of only ~6 N (first closure) would lift its far edge.",
        "The float carries the gun, ring and cables; the rim only sees a chosen preload. The dot follows radial runout, face runout and reseating.",
        "What the ring follows is the RIM; the joint is the cap face + bore 6.35 mm below. A local bore/cap follower near the station closes that gap.",
        "Contacts ride material 20+ mm from the puddle (bulk temperature); stainless or ceramic rollers avoid iron pickup on the 316L.",
    ]
    (OUT / "D-rim-carriage.svg").write_text(s.svg(notes))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    suspension_original()
    wire_located()
    float_dock()
    rim_carriage()
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
