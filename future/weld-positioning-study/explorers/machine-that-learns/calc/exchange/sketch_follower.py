"""Sketch for the exchange: carry-and-locate's rim carriage turned into a light sensor
(branch D-s, 'sense, don't carry'). Section through the dot (looking along the tangent)
and plan. Gun = scene proxy at the opening pose; stylus geometry is a proposal."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import Svg, draw_gun, R_IN  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "../../sketches/")


def section():
    s = Svg(820, 520, -140, 160, -70, 110,
            "D-s  sense, don't carry: a light stylus on the lip's outside, at the dot's own angle (section)",
            notes=["Ceramic ball or wheel, 0.5-1 N spring, 9 mm below the joint level on the tube OD, radially in line with the dot.",
                   "It reads the wall's radial position where the bead is being laid - runout, ovality and bulk thermal growth - during the weld,",
                   "when the camera cannot see the red dot. The reading drives X (tube stage in A, gun stage in B). Its stand is on whatever carries the gun."])
    wall = 1.65
    s.rect(0, -60, wall, 6.35, fill="#bbb", stroke="#444")
    s.rect(-120, -6.35, -0.25, 0, fill="#ccc", stroke="#444")
    s.text((-115, -4), "endcap plate (6.35 mm, recessed)", size=10)
    s.text((3, 9), "lip", size=9)
    draw_gun(s, "front")
    s.dot((0, 0), 4)
    s.text((-30, 8), "dot", size=10, color="#b00")
    # stylus
    tip = (wall + 2.5, -9.0)
    s.circle(tip, 2.5, fill="#eee", stroke="#222", sw=1.5)
    s.line((tip[0] + 2.5, tip[1]), (70, tip[1]), stroke="#555", sw=3)
    s.rect(70, tip[1] - 10, 130, tip[1] + 10, fill="#c9d6c9", stroke="#353")
    s.text((72, tip[1] + 14), "slide + scale", size=10)
    s.text((72, tip[1] - 22), "(caliper beam or AS5048 lever)", size=9)
    s.line((100, tip[1] - 10), (100, -60), stroke="#555", sw=4)
    s.text((104, -55), "stand on the gun's frame", size=9)
    s.line((30, 20), (8, -7), stroke="#888")
    s.text((32, 22), "0.5-1 N, insulating tip", size=10)
    s.items.append(f'<rect x="0" y="0" width="{s.w}" height="{s.top}" fill="#fff"/>')
    s.items.append('<text x="10" y="22" font-size="15" font-weight="bold">D-s  sense, don\'t carry: a light stylus on the lip\'s outside, at the dot\'s own angle (section)</text>')
    s.save(OUT + "exchange-follower-section.svg")


if __name__ == "__main__":
    section()
