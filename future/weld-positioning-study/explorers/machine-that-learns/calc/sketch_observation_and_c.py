"""Sketches: the observation layer (plan view + what the joint camera sees) and
arrangement C (hexapod with a software pivot at the dot).

Gun = scene proxy at 45/30/-15. Camera, hexapod and nest positions are
this explorer's proposals.
"""
import math
from svgkit import Svg, draw_gun, draw_tube_side, R_IN

OUT = "../sketches/"
CAM = (-45.0, 70.0, 85.0)


def plan():
    s = Svg(820, 700, -260, 200, -330, 200,
            "Observation layer: plan view from above (dot on the +X side of the tube)",
            notes=["Joint camera on the +Y side, mirror of the gun across the radial plane: ~69 deg between its view and the beam,",
                   "so the red dot's image moves 3+ px per 0.1 mm of standoff at 100-120 mm (ELP 16MP, 68 deg lens, cropped).",
                   "Station camera sees the whole gun, cable, tube and index ring; it reads the gun's LEDs and the table angle."])
    c = (-R_IN, 0)
    s.circle(c, 63.5, stroke="#555", sw=2)
    s.circle(c, R_IN, stroke="#555", sw=1)
    for sgn in (-1, 1):
        s.circle((c[0] + sgn * 19.05, 0), 5.56, stroke="#777")
    s.text((c[0] - 30, -12), "cap ports", size=9)
    s.line((c[0] - 70, 0), (40, 0), stroke="#6a4", dash="6,3")
    s.text((42, -3), "radial line / hole axis", size=9, color="#361")
    s.line((0, -150), (0, 120), stroke="#999", dash="3,3")
    s.text((4, 110), "tangent", size=9)
    draw_gun(s, "plan")
    s.dot((0, 0), 4)
    cam = (CAM[0], CAM[1])
    s.rect(cam[0] - 10, cam[1] - 7, cam[0] + 10, cam[1] + 7, fill="#333", stroke="#000")
    s.line(cam, (0, 0), stroke="#b00", dash="3,3")
    s.text((cam[0] - 14, cam[1] + 16), "joint camera, 85 mm above the dot, ~120 mm away", size=10, anchor="end")
    st = (-200, 160)
    s.rect(st[0] - 12, st[1] - 8, st[0] + 12, st[1] + 8, fill="#555", stroke="#000")
    s.line(st, (-100, -100), stroke="#555", dash="2,4")
    s.line(st, (40, -40), stroke="#555", dash="2,4")
    s.text((st[0] + 16, st[1] + 4), "station camera (wide)", size=10)
    s.line((-8, -60), (-2, -8), stroke="#c60", sw=2)
    s.text((6, -60), "wire arrives along -Y side", size=10, color="#a40")
    s.circle(c, 90, stroke="#48a", dash="2,2")
    s.text((c[0] - 60, -95), "printed index ring on the turntable (read by the station camera)", size=9, color="#236")
    s.save(OUT + "observation-plan.svg")


def camera_view():
    """Schematic of the joint camera image near the corner (not to scale)."""
    w, h = 760, 430
    items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">',
             f'<rect width="{w}" height="{h}" fill="#fff"/>',
             '<text x="10" y="22" font-size="15" font-weight="bold">What the joint camera measures at the corner (schematic, not to scale)</text>',
             '<polygon points="40,60 520,60 520,200 40,230" fill="#d8dde3" stroke="#555"/>',
             '<text x="50" y="80" font-size="12">tube bore wall (the 6.35 mm lip, seen obliquely)</text>',
             '<polygon points="40,230 520,200 520,380 40,380" fill="#eceff2" stroke="#555"/>',
             '<text x="50" y="370" font-size="12">endcap face</text>',
             '<line x1="40" y1="230" x2="520" y2="200" stroke="#222" stroke-width="2"/>',
             '<text x="330" y="232" font-size="12">corner line (edge fit: ~1 px)</text>',
             '<line x1="250" y1="170" x2="300" y2="262" stroke="#e00" stroke-width="5" stroke-linecap="round" opacity="0.8"/>',
             '<circle cx="275" cy="216" r="5" fill="#e00"/>',
             '<text x="120" y="160" font-size="12" fill="#b00">red reference beam, swept by the wobble into a line</text>',
             '<line x1="330" y1="330" x2="283" y2="226" stroke="#c60" stroke-width="3"/>',
             '<text x="335" y="340" font-size="12" fill="#a40">wire tip (position + scatter as wire is jogged)</text>',
             '<text x="540" y="80" font-size="12">Per image, per table angle:</text>',
             '<text x="540" y="100" font-size="12">a  dot/line centre to corner line (mm)</text>',
             '<text x="540" y="118" font-size="12">b  share of the swept line on wall vs cap</text>',
             '<text x="540" y="136" font-size="12">c  line length + orientation (wobble axis)</text>',
             '<text x="540" y="154" font-size="12">d  standoff, by triangulating the dot</text>',
             '<text x="540" y="172" font-size="12">e  wire tip to the line\'s leading end</text>',
             '<text x="540" y="190" font-size="12">f  tack positions -> table angle</text>',
             '<text x="540" y="226" font-size="12">Over a revolution: a(theta), d(theta)</text>',
             '<text x="540" y="244" font-size="12">= this tube\'s runout, as seen at</text>',
             '<text x="540" y="262" font-size="12">the dot, which X/Z can then follow.</text>',
             '<text x="540" y="298" font-size="12">Over hours with nothing moving:</text>',
             '<text x="540" y="316" font-size="12">drift of the station itself (creep,</text>',
             '<text x="540" y="334" font-size="12">temperature, cable settling).</text>',
             '</svg>']
    with open(OUT + "observation-camera-view.svg", "w") as f:
        f.write("".join(items))


def hexapod():
    s = Svg(900, 640, -260, 520, -250, 480,
            "C  hexapod with its pivot set at the dot: side view (looking from outside the tube)",
            notes=["Six identical NEMA17 lead-screw legs between a base ring (on a manually set arm) and a platform on the shell's outboard face.",
                   "The pivot is a number: rotations are commanded about the dot, the grip axis, the hole axis, or anything else.",
                   "Workspace is small (tens of mm, ~+/-10 deg): coarse placement stays manual; the hexapod is the fine, fully actuated last stage."])
    s.rect(-260, -242, 520, -232, fill="#caa472", stroke="#7a5a2a")
    s.rect(-180, -232, 120, -196, fill="#e8d9b5", stroke="#865")
    draw_tube_side(s)
    draw_gun(s, "side")
    s.dot((0, 0), 4)
    # platform on outboard face (body +x side), normal ~(0.775, 0.158, 0.612) -> side view (-y, z) dir (-0.158, 0.612)
    pc = (105.1, 153.5)
    n = (-0.158, 0.612)
    nn = math.hypot(*n)
    n = (n[0] / nn, n[1] / nn)
    t = (n[1], -n[0])
    plat = [(pc[0] + t[0] * k, pc[1] + t[1] * k) for k in (-60, 60)]
    base_c = (pc[0] + n[0] * 190, pc[1] + n[1] * 190)
    base = [(base_c[0] + t[0] * k, base_c[1] + t[1] * k) for k in (-120, 120)]
    s.line(plat[0], plat[1], stroke="#963", sw=6)
    s.line(base[0], base[1], stroke="#555", sw=8)
    for i in range(6):
        a = plat[0][0] + (plat[1][0] - plat[0][0]) * (i % 3) / 2, plat[0][1] + (plat[1][1] - plat[0][1]) * (i % 3) / 2
        b = base[0][0] + (base[1][0] - base[0][0]) * ((i + (1 if i < 3 else 2)) % 4) / 3, base[0][1] + (base[1][1] - base[0][1]) * ((i + (1 if i < 3 else 2)) % 4) / 3
        s.line(a, b, stroke="#2a6", sw=3)
    s.text((base[1][0] + 10, base[1][1]), "base ring on a manually set, lockable arm/column", size=10)
    s.text((plat[1][0] + 12, plat[1][1] - 10), "platform = kinematic seat on the shell", size=10, color="#963")
    s.line((0, 0), (0, 300), stroke="#b00", dash="2,4")
    s.text((6, 290), "software pivot (dot)", size=10, color="#b00")
    s.save(OUT + "c-hexapod-side.svg")


if __name__ == "__main__":
    plan()
    camera_view()
    hexapod()
