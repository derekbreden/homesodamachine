"""Wave-4 sketches (schematic): (1) borrowed-ecosystems E with carry pins and a two-stop rider Z,
phase by phase; (2) teach-record-replay: what is measured, the record, three meanings of replay,
and camera placement in plan (tube and proxy gun to scale at hole dial 30)."""
import math
from proxy import *

def T(x, y, s, **k):
    a = ' '.join(f'{kk.replace("_", "-")}="{v}"' for kk, v in k.items())
    return f'<text x="{x}" y="{y}" {a}>{s}</text>'

# ---------- 1. E session strip ----------
phases = ['park', 'lift out', 'set down\n(LAND)', 'Z to WELD', 'pins out', 'tacks /\ndry run', 'weld', 'stuck wire', 'Z to LAND', 'pins in,\nlift', 'park']
rows = [
    ('gimbal pins', ['IN', 'IN', 'IN', 'IN', 'OUT', 'OUT', 'OUT', 'OUT', 'OUT', 'IN', 'IN']),
    ('rider Z stop', ['LAND', 'LAND', 'LAND', 'WELD', 'WELD', 'WELD', 'WELD', 'WELD', 'LAND', 'LAND', 'LAND']),
    ('who locates', ['cup', 'hand', 'rider wheels', 'rider', 'rider', 'rider', 'rider', 'rider+tether', 'rider', 'hand', 'cup']),
    ('wire tip', ['in cup gauge', 'clear', '~10 mm back', 'short 1 mm', 'jog to touch', 'in corner', 'feeding', 'stuck: snip', 'leaves up+in', 'clear', 're-trim']),
    ('arm spring', ['carries', 'carries', 'lands (damper)', 'preload', 'preload', 'preload', 'preload', 'follows ~0 N', 'preload', 'carries', 'carries']),
]
C = {'IN': '#f6d6a8', 'OUT': '#c9e7cf', 'LAND': '#f6d6a8', 'WELD': '#c9e7cf'}
cw, ch, lw, top = 96, 40, 120, 80
W = lw + cw * len(phases) + 20; H = top + 40 + ch * len(rows) + 110
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="10">',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     T(10, 20, 'Film-grip carrier (borrowed-ecosystems E) with two phase states added: carry pins in the gimbal, two hard stops on the rider Z', font_size=14, font_weight='bold'),
     T(10, 38, 'Pins IN lock the gimbal\'s two non-vertical axes at the recipe attitude (the umbilical, not pendulosity, sets a free gimbal\'s attitude: 130–640 N·mm vs 1–2 N·mm per degree).', font_size=11),
     T(10, 54, 'LAND keeps the wire tip ~10 mm back along the barrel while the undamped arm settles the rider; WELD is the recipe stop. Lift-off reverses the order.', font_size=11)]
for i, p in enumerate(phases):
    for j, line in enumerate(p.split('\n')):
        o.append(T(lw + i * cw + 4, top + j * 12, line, font_weight='bold'))
for r, (name, cells) in enumerate(rows):
    y = top + 28 + r * ch
    o.append(T(10, y + 24, name, font_weight='bold', font_size=11))
    for i, c in enumerate(cells):
        x = lw + i * cw
        o.append(f'<rect x="{x}" y="{y}" width="{cw-2}" height="{ch-2}" fill="{C.get(c, "#fff")}" stroke="#bbb"/>')
        o.append(T(x + 4, y + 22, c))
y = top + 28 + len(rows) * ch + 22
o.append(T(10, y, 'Tacks: with the rider seated a rim-bridge hanger hits its ±60° rim wheels when the table indexes; use the stand-hung plate head (pads inside, arm over the −X rim) and tack as fixture pulses.', font_size=11))
o.append(T(10, y + 16, 'Stuck wire: the tube drags gun + rider round the rim until the tether breakaway opens the pedal loop (a proposed series contact); snip, slide back, re-trim stickout at the cup.', font_size=11))
o.append(T(10, y + 32, 'Second person: pins (coloured rings) and the Z lever (LAND / WELD) show the state; the recipe is the arm tension count, the indexing ring ID and the WELD stop ID.', font_size=11))
o.append('</svg>')
open('../sketches/w4-film-grip-session.svg', 'w').write('\n'.join(o))

# ---------- 2. teach-record-replay ----------
W, H = 1240, 820
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker></defs>',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     T(12, 22, 'Teach by hand, record, replay — the hand finds the pose, the record keeps it, a mechanism repeats it, anyone follows it', font_size=14, font_weight='bold')]
def box(x, y, w, h, title, lines, fill):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#666"/>', T(x + 10, y + 20, title, font_weight='bold', font_size=12)]
    for i, l in enumerate(lines): out.append(T(x + 10, y + 40 + i * 15, l))
    return '\n'.join(out)
o.append(box(20, 50, 280, 200, '1 TEACH (hand)', ['gun weightless on the carrier (CG bail,', 'carry pins OUT), dot on the corner by eye;', 'dry lap: hand holds while the table turns;', 'or real hand welds (tacks, coupons)', '', 'the hand feels: no weight, the', 'umbilical torque (0.1–0.6 N·m), nothing else'], '#eef3fb'))
o.append(box(320, 50, 300, 200, '2 RECORD (every frame)', ['shell pose in the station frame: AprilTag', '  plates, 2 cameras (~0.1–0.3°, ~0.1 mm)', 'dot vs corner + standoff: joint camera', '  (~3 px per 0.1 mm, machine-that-learns)', 'tilt vs gravity at 100 Hz: IMU on shell', 'table degrees + pedal: rotator console', 'trigger on/off: switch on the presser'], '#f3f8ee'))
o.append(box(640, 50, 290, 200, '3 RECIPE (a file + an object)', ['mean pose over the lap and its spread', '  (how steady the hand was)', 'dock numbers: X, Y dials; Z per tube', 'printed recipe block from the angles', '  (teach → print overnight)', 'timing: start after N°, stop at 380°', 'stickout, welder set, dot image'], '#fbf3e6'))
o.append(box(950, 50, 270, 200, '4 REPLAY (three meanings)', ['R1 stops: dial numbers + printed block;', '   dock the gun; camera overlay checks', 'R2 guide: live error bars; the hand', '   is the actuator, weightless', 'R3 motors: dock X/Z on steppers replay', '   pose + runout map; the AI refines', ''], '#f6e9ef'))
for x1, x2 in ((300, 320), (620, 640), (930, 950)):
    o.append(f'<line x1="{x1}" y1="150" x2="{x2}" y2="150" stroke="#333" stroke-width="2" marker-end="url(#a)"/>')
o.append(box(640, 270, 580, 110, '5 FOLLOW (tube change, second person)', ['the record is in the joint frame: rim set to the flag first, so tube length drops out;', 'a second person loads the recipe, fits the printed block, sets two dials, docks, and', 'matches the live dot to the recorded dot image — or follows the R2 bars by hand;', 'every dock is a camera calibration event (the docked pose is known)'], '#eef6f6'))
o.append(f'<path d="M1085,250 L1085,270" stroke="#333" stroke-width="2" marker-end="url(#a)"/>')
# plan with cameras (to scale 1.2 px/mm)
S = 0.9; cx, cy = 330, 590
def P(x, y): return (cx + S * x, cy - S * y)
o.append(T(20, 405, 'Plan at the true opening pose (tube, gun and dot to scale; camera and tag placements proposed)', font_weight='bold'))
o.append(f'<circle cx="{cx}" cy="{cy}" r="{S*R_OUT}" fill="#dfeaea" stroke="#577"/>')
d = P(R_IN, 0); o.append(f'<circle cx="{d[0]}" cy="{d[1]}" r="4" fill="#d00"/>')
pts = [pose(p) for p in ((0, 0, 0), (0, 0, 118), (0, 0, 253))]
o.append('<polyline points="%s" fill="none" stroke="#335" stroke-width="14" stroke-opacity="0.35" stroke-linecap="round"/>' % ' '.join(f'{P(q[0], q[1])[0]:.1f},{P(q[0], q[1])[1]:.1f}' for q in pts))
gs, gb = pose((0, -25, 172)), pose(GB)
o.append(f'<line x1="{P(gs[0],gs[1])[0]:.1f}" y1="{P(gs[0],gs[1])[1]:.1f}" x2="{P(gb[0],gb[1])[0]:.1f}" y2="{P(gb[0],gb[1])[1]:.1f}" stroke="#335" stroke-width="18" stroke-opacity="0.25" stroke-linecap="round"/>')
hm = pose((0, 0, 185.5)); q = P(hm[0], hm[1])
o.append(f'<rect x="{q[0]-14}" y="{q[1]-14}" width="28" height="28" fill="#fff" stroke="#000"/><text x="{q[0]-9}" y="{q[1]+4}" font-size="9">tag</text>')
o.append(T(q[0] - 150, q[1] + 30, 'tag plate + IMU on the shell (~50 g)'))
jc = P(R_IN - 45, 70); o.append(f'<circle cx="{jc[0]}" cy="{jc[1]}" r="8" fill="#6a6" stroke="#333"/>')
o.append(f'<line x1="{jc[0]}" y1="{jc[1]}" x2="{d[0]}" y2="{d[1]}" stroke="#6a6" stroke-dasharray="4 3"/>')
o.append(T(jc[0] + 12, jc[1] - 6, 'joint camera on the free +Y side (machine-that-learns):'))
o.append(T(jc[0] + 12, jc[1] + 8, 'dot vs corner, standoff, wire tip; red long-pass filter'))
oc = P(-250, 150); o.append(f'<circle cx="{oc[0]}" cy="{oc[1]}" r="8" fill="#6a6" stroke="#333"/>')
o.append(f'<line x1="{oc[0]}" y1="{oc[1]}" x2="{q[0]}" y2="{q[1]}" stroke="#6a6" stroke-dasharray="4 3"/>')
o.append(T(oc[0] + 12, oc[1] - 4, 'pose camera, high on −X/+Y: sees the shell tag and the station tags'))
for (x, y) in ((-160, -130), (160, -130), (160, 110)):
    t = P(x, y); o.append(f'<rect x="{t[0]-9}" y="{t[1]-9}" width="18" height="18" fill="#fff" stroke="#000"/>')
o.append(T(P(160, -130)[0] + 14, P(160, -130)[1] + 4, 'station tags (subplate / dock post)'))
o.append(T(20, 805, 'The pose is recorded relative to the station tags after the rim is set to its flag, so the record is a pose relative to the joint, not to wherever the carrier was.'))
o.append(box(640, 400, 580, 300, 'What replay physically is, and what limits it', [
    'R1  the dock\'s geometry reproduces the taught pose: error = dial reading + block print',
    '    (~0.1 mm / ~0.1°, estimates) + dock repeatability (tens of µm) + model error',
    '    (the scan-based kinematics that turn a pose into dial numbers)',
    'R2  a person reproduces it with live bars: error = how still a weightless, guided',
    '    hand stays (unknown; the teach record of Derek\'s own spread is the benchmark)',
    'R2b lock where the hand stops: holding electromagnets on each carrier joint;',
    '    lock-shift and a soft chain make this the weakest meaning',
    'R3  motors replay what R1 sets by hand, plus a per-tube runout map',
    '',
    'Recipe checks before printing: the taught pose must dock and escape',
    '(wire-escape sweep, lid/dock clearance) — the sweep scripts become the',
    'recipe validator.',
    '',
    'Biggest open problem: the pose→dial model. It needs the scanned gun and a',
    'measured dot-to-shell relation; until then R1 replays by iteration (dock,',
    'look, trim) with the record as the target image.'], '#fff'))
o.append('</svg>')
open('../sketches/w4-teach-record-replay.svg', 'w').write('\n'.join(o))
print('ok')
