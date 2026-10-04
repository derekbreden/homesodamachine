"""Draw the three Letter bench sheets. Run by hand; no appliance/CAD build.

The endcap drawing reads its small numeric dependency closure with an AST
arithmetic reader. The welding sequence is authored craft, with the practice
recipe read from the production procedure. ReportLab writes vector artwork
and embedded IBM Plex type. No scene render or full-deck sync is invoked.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import operator
import re
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/pdf"
PDF = OUT / "assembly-drill-and-weld-letter.pdf"
SOURCES = {
    "endcap": "hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py",
    "float": "hardware/printed-parts/cold-core/_float_interface.py",
    "rotator": "hardware/printed-parts/fixtures/weld-rotator/_rotator_interface.py",
    "procedure": "hardware/assembly/pressure-vessel.md",
    "rig": "hardware/assembly/weld-rotation-rig.md",
    "sequence": "hardware/weld-rotator-guide/46-the-per-weld-sequence.html",
    "controls": "firmware/src_weld_rotator/README.md",
}
MANUAL = "https://www.xlaserlab.com/pages/xlaserlab-x1-pro-instruction-manual"
W, H = 612, 792
INK, BLUE, ORANGE = "#202337", "#1749D1", "#E95A2C"
PAPER, ICE, STEEL = "#FCFCFA", "#EAF0FC", "#E4E8EE"
MUTED, RULE, COPPER, GLOVE = "#606A78", "#DCE2EB", "#B8722C", "#ECD5AA"


def constants(path, wanted, external=None):
    """Read only arithmetic expressions needed by the requested constants."""
    tree = ast.parse(path.read_text())
    expressions = {
        target.id: statement.value
        for statement in tree.body if isinstance(statement, ast.Assign)
        for target in statement.targets if isinstance(target, ast.Name)
    }
    values = dict(external or {})
    ops = {ast.Add: operator.add, ast.Sub: operator.sub,
           ast.Mult: operator.mul, ast.Div: operator.truediv}

    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            return get(node.id)
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)
        raise ValueError(f"Review the changed numeric source: {path}: {ast.dump(node)}")

    def get(name):
        if name not in values:
            values[name] = evaluate(expressions[name])
        return values[name]

    return {name: get(name) for name in wanted}


FLOAT = constants(ROOT / SOURCES["float"], ["rod_axis_from_inner_wall"])
D = constants(ROOT / SOURCES["endcap"],
              ["disc_diameter", "disc_thickness", "hole_diameter", "hole_spacing",
               "register_radius", "register_drill_diameter", "register_depth"], FLOAT)
R = constants(ROOT / SOURCES["rotator"],
              ["TUBE_OD", "TUBE_ID", "TUBE_WALL", "ENDCAP_RECESS",
               "TRAVEL_NOMINAL", "OVERLAP_DEGREES"])
procedure = (ROOT / SOURCES["procedure"]).read_text()
recipe = re.search(
    r"Recorded practice settings: power (\d+) %, wobble (\d+) Hz × (\d+) mm, "
    r"wire feed (\d+) mm/s, argon (\d+) s pre/post, ER316L \.(\d+) filler, "
    r"(\d+)-tack opposite-side-bisecting pattern", procedure)
if not recipe:
    raise ValueError("Review the changed closure practice recipe in pressure-vessel.md")
POWER, HZ, SWEEP, FEED, GAS, WIRE, TACKS = recipe.groups()
if TACKS != "8":
    raise ValueError("Review the authored eight-tack illustration")
if not math.isclose(D["register_drill_diameter"], 9 / 64):
    raise ValueError("Review the named 9/64-inch drill")
if not math.isclose(R["ENDCAP_RECESS"] / 25.4, 1 / 4):
    raise ValueError("Review the named 1/4-inch spacer")
rig = (ROOT / SOURCES["rig"]).read_text()
radial = re.search(r"radial runout at the weld end \*\*≤ ([\d.]+) mm TIR", rig).group(1)
face = re.search(r"end-cap face runout at the weld circle \*\*≤ ([\d.]+) mm TIR", rig).group(1)
for requirement in ["through two dry revolutions", "Start at **[8 mm/s](SPEED_NOM)"]:
    if requirement not in rig:
        raise ValueError(f"Review changed rotator procedure: {requirement}")
if not 0 < D["register_depth"] < D["disc_thickness"]:
    raise ValueError("Register must leave an intact plate")

FONT_DIR = ROOT / "hardware/quickstart-codex/fonts"
for face_name, filename in [("Plex", "Plex-Regular.ttf"),
                            ("PlexSemi", "Plex-Semibold.ttf"),
                            ("PlexBold", "Plex-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(face_name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily("Plex", normal="Plex", bold="PlexBold",
                              italic="Plex", boldItalic="PlexBold")


def color(value):
    return HexColor(value)


def box(c, x, y, width, height, fill=PAPER, stroke=None, radius=0):
    c.setFillColor(color(fill))
    c.setStrokeColor(color(stroke or fill))
    c.setLineWidth(0.7)
    if radius:
        c.roundRect(x, H - y - height, width, height, radius,
                    fill=1, stroke=bool(stroke))
    else:
        c.rect(x, H - y - height, width, height, fill=1, stroke=bool(stroke))


def text(c, value, x, y, size=12, font="Plex", fill=INK, align="left"):
    c.setFont(font, size)
    c.setFillColor(color(fill))
    getattr(c, {"left": "drawString", "center": "drawCentredString",
                "right": "drawRightString"}[align])(x, H - y, value)


def paragraph(c, value, x, y, width, size=11.4, leading=None, fill=INK,
              max_height=None):
    style = ParagraphStyle("copy", fontName="Plex", fontSize=size,
                           leading=leading or size * 1.22, textColor=color(fill))
    p = Paragraph(value, style)
    _, height = p.wrap(width, H)
    if max_height and height > max_height:
        raise ValueError(f"Text exceeds its box: {value}")
    p.drawOn(c, x, H - y - height)
    return height


class Art:
    """Top-left coordinates for vector pictures; text remains upright."""

    def __init__(self, c, x, y, scale=1):
        self.c, self.x, self.y, self.scale = c, x, y, scale

    def __enter__(self):
        self.c.saveState()
        self.c.translate(self.x, H - self.y)
        self.c.scale(self.scale, -self.scale)
        self.c.setLineCap(1)
        self.c.setLineJoin(1)
        return self

    def __exit__(self, *exc):
        self.c.restoreState()

    def shape(self, points, fill=None, stroke=INK, width=1.5, close=True):
        c = self.c
        p = c.beginPath()
        p.moveTo(*points[0])
        for point in points[1:]:
            if len(point) == 2:
                p.lineTo(*point)
            else:
                p.curveTo(*point)
        if close:
            p.close()
        c.setStrokeColor(color(stroke or fill))
        c.setFillColor(color(fill or PAPER))
        c.setLineWidth(width)
        c.drawPath(p, fill=bool(fill), stroke=bool(stroke))

    def line(self, x1, y1, x2, y2, fill=INK, width=1.4, dash=None):
        c = self.c
        c.setStrokeColor(color(fill))
        c.setLineWidth(width)
        c.setDash(dash or [])
        c.line(x1, y1, x2, y2)
        c.setDash([])

    def rect(self, x, y, width, height, fill=STEEL, stroke=INK):
        self.shape([(x, y), (x + width, y), (x + width, y + height),
                    (x, y + height)], fill, stroke)

    def ellipse(self, x, y, width, height, fill=STEEL, stroke=INK, lw=1.5):
        c = self.c
        c.setFillColor(color(fill or PAPER))
        c.setStrokeColor(color(stroke or fill))
        c.setLineWidth(lw)
        c.ellipse(x, y, x + width, y + height, fill=bool(fill), stroke=bool(stroke))

    def label(self, value, x, y, size=10, fill=INK, font="PlexSemi", align="left"):
        c = self.c
        c.saveState()
        c.scale(1, -1)
        c.setFont(font, size)
        c.setFillColor(color(fill))
        getattr(c, {"left": "drawString", "center": "drawCentredString",
                    "right": "drawRightString"}[align])(x, -y, value)
        c.restoreState()

    def arrow(self, x1, y1, x2, y2, fill=BLUE, width=2, head=6):
        self.line(x1, y1, x2, y2, fill, width)
        angle = math.atan2(y2 - y1, x2 - x1)
        self.shape([(x2, y2),
                    (x2 - head * math.cos(angle - .5), y2 - head * math.sin(angle - .5)),
                    (x2 - head * math.cos(angle + .5), y2 - head * math.sin(angle + .5))],
                   fill, None)

    def dim(self, x1, y1, x2, y2, fill=BLUE):
        self.line(x1, y1, x2, y2, fill, .8)
        if x1 == x2:
            for y in [y1, y2]:
                self.line(x1 - 4, y, x1 + 4, y, fill, 1)
        else:
            for x in [x1, x2]:
                self.line(x, y1 - 4, x, y1 + 4, fill, 1)


def badge(c, n, x, y, label, fill=BLUE, size=14):
    box(c, x, y, 22, 22, fill, radius=5)
    text(c, str(n), x + 11, y + 15.5, 12, "PlexBold", PAPER, "center")
    text(c, label, x + 31, y + 16, size, "PlexSemi")


def header(c, n, title, subtitle):
    box(c, 0, 0, W, H, PAPER)
    box(c, 0, 0, W, 8, BLUE)
    box(c, W - 7, 8, 7, H - 8, ORANGE)
    text(c, "HOME SODA MACHINE / BENCH INSTRUCTIONS", 32, 35, 10,
         "PlexSemi", BLUE)
    text(c, f"{n:02d} / 03", 577, 35, 10, "PlexSemi", MUTED, "right")
    for i, line in enumerate(title.split("\n")):
        text(c, line, 32, 75 + i * 31, 30, "PlexBold")
    last = 75 + (len(title.split("\n")) - 1) * 31
    paragraph(c, subtitle, 33, last + 14, 544, 13, 16, MUTED, 36)


def footer(c, n, source, link):
    box(c, 32, 752, 548, .8, RULE)
    paragraph(c, source, 32, 759, 420, 8.1, 9.5, MUTED, 20)
    text(c, f"LETTER / 04 OCT 2026 / {n}", 580, 768, 7.8,
         "PlexSemi", MUTED, "right")
    c.linkURL(link, (32, 15, 580, 38), relative=0)


def panel(c, x, y, width, height):
    box(c, x, y, width, height, "#FFFFFF", RULE, 8)


def plate(a, cx, cy, radius, register=True, tacks=False):
    a.ellipse(cx - radius, cy - radius, 2 * radius, 2 * radius)
    unit = 2 * radius / D["disc_diameter"]
    hole_radius = D["hole_diameter"] * unit / 2
    for sign in [-1, 1]:
        hx = cx + sign * D["hole_spacing"] * unit / 2
        a.ellipse(hx - hole_radius, cy - hole_radius, 2 * hole_radius,
                  2 * hole_radius, PAPER)
    if register:
        ry = cy + D["register_radius"] * unit
        r = D["register_drill_diameter"] * unit / 2
        a.ellipse(cx - r, ry - r, 2 * r, 2 * r, ORANGE, ORANGE)
    if tacks:
        order = [-90, 90, 180, 0, 225, 45, 315, 135]
        for i, degrees in enumerate(order, 1):
            angle = math.radians(degrees)
            x, y = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
            a.ellipse(x - 2.5, y - 2.5, 5, 5, ORANGE, None)
            a.label(str(i), cx + (radius + 15) * math.cos(angle),
                    cy + (radius + 15) * math.sin(angle) + 3,
                    11, BLUE, "PlexBold", "center")


def bit(a, x, y, length=47):
    a.rect(x - 4, y, 8, length, STEEL)
    for offset in range(5, int(length - 3), 10):
        a.line(x - 4, y + offset, x + 4, y + offset + 6, MUTED, .9)
    a.shape([(x - 4, y + length), (x, y + length + 3),
             (x + 4, y + length)], STEEL)


def clamp(a, x, y, reverse=False):
    dx = -1 if reverse else 1
    a.shape([(x, y), (x + dx * 35, y), (x + dx * 35, y + 27),
             (x + dx * 12, y + 27), (x + dx * 12, y + 19),
             (x + dx * 25, y + 19), (x + dx * 25, y + 8), (x, y + 8)], ICE)
    a.line(x + dx * 6, y - 9, x + dx * 6, y + 15, BLUE, 2)
    a.line(x - dx * 2, y - 9, x + dx * 14, y - 9, BLUE, 2)


def tube(a, x, y, width=108, height=100, cap=True, purge=False, shoe=False):
    a.shape([(x, y + 11), (x, y + height),
             (x, y + height + 15, x + width, y + height + 15, x + width, y + height),
             (x + width, y + 11)], STEEL)
    a.ellipse(x, y, width, 26, "#F6F7F9")
    a.ellipse(x + 5, y + 5, width - 10, 18, "#BAC2D0")
    if cap:
        a.ellipse(x + 6, y + 9, width - 12, 15, STEEL)
        for hx in [x + width * .37, x + width * .63]:
            a.ellipse(hx - 4, y + 14, 8, 5, PAPER)
    a.ellipse(x - 15, y + height + 4, width + 30, 22, "#BAC2D0")
    a.rect(x - 28, y + height + 20, width + 56, 10, INK)
    if shoe:
        a.rect(x + width - 1, y + height - 27, 10, 34, COPPER)
        a.shape([(x + width + 7, y + height - 15),
                 (x + width + 27, y + height - 25),
                 (x + width + 30, y + height - 20),
                 (x + width + 9, y + height - 10)], ORANGE)
        a.line(x + width + 27, y + height - 23, x + width + 47, y + height - 23)
    if purge:
        a.arrow(x - 24, y + height - 20, x + 20, y + height - 20)
        a.arrow(x + 20, y + height - 20, x + 20, y + 45)
        a.arrow(x + 35, y + 42, x + width * .65, y + 42)
        a.arrow(x + width * .65, y + 42, x + width * .65, y + height - 20)
        a.arrow(x + width * .65, y + height - 20, x + width + 27, y + height - 20)


def turn_arrow(a, x, y, size=40):
    a.shape([(x, y + 10), (x + size * .15, y - 8, x + size * .85, y - 8,
                            x + size, y + 10)], None, BLUE, 2, False)
    a.arrow(x + size, y + 10, x + size - 2, y + 17, BLUE, 2, 5)


def gun(a, x, y, scale=1, hand=False, firing=False, cable=True):
    """Schematic X1-style head, tip at (x,y), drawn toward upper right."""
    c = a.c
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    g = a
    g.shape([(0, 0), (15, -5), (20, -18), (8, -12)], COPPER)
    g.shape([(15, -5), (71, -35), (64, -47), (20, -18)], STEEL)
    g.shape([(62, -46), (104, -67), (126, -59), (142, -45),
             (125, -25), (89, -21), (76, -31)], "#C0CBD5")
    g.shape([(105, -30), (125, -25), (143, 28), (123, 35),
             (108, -8), (94, -20)], "#BAC2D0")
    # Trigger on the front of the grip; orange only when pulled.
    g.shape([(106, -11), (111, -8), (117, 10), (113, 12)],
            ORANGE if firing else INK)
    g.line(35, 10, 14, 5, COPPER, 3)
    g.line(14, 5, 1, 0, MUTED, 1.2)
    g.shape([(34, 10), (59, 30), (94, 45)], None, INK, 3, False)
    if cable:
        g.shape([(136, 33), (147, 69, 179, 74, 195, 90)], None, INK, 6, False)
    if hand:
        g.shape([(161, 23), (147, 8), (144, -9),
                 (138, -14, 130, -11, 130, -4), (134, 13),
                 (124, 17), (119, 7), (109, 1),
                 (99, 0, 99, -6, 107, -6), (115, -3),
                 (114, -13), (105, -17),
                 (91, -18, 90, -5, 96, 4),
                 (106, 21), (124, 44), (150, 48), (171, 40)], GLOVE)
        g.shape([(157, 19), (194, 34), (181, 65), (146, 45)], ICE)
        g.line(125, 21, 136, 34, MUTED, .8)
        if firing:
            g.arrow(87, 8, 104, 7, ORANGE, 2, 5)
    if firing:
        g.ellipse(-3.5, -3.5, 7, 7, ORANGE, None)
        # The visible mark denotes the puddle; no free beam is pictured.
        for dx, dy in [(-7, -9), (-11, 1), (-4, 10)]:
            g.line(-3, -1, dx, dy, ORANGE, 1.2)
    c.restoreState()


def pedal(a, x, y, pressed=True, boot=True):
    a.shape([(x, y + 33), (x + 87, y + 33), (x + 94, y + 45),
             (x + 9, y + 45)], "#BAC2D0")
    rise = 26 if pressed else 10
    a.shape([(x + 5, y + rise), (x + 80, y + 22),
             (x + 87, y + 33), (x + 9, y + 38)], STEEL)
    for j in range(15, 74, 8):
        a.line(x + j, y + rise + 3, x + j + 4, y + 33, MUTED, .6)
    a.shape([(x + 4, y + 43), (x - 12, y + 62, x + 15, y + 75,
                              x + 39, y + 74)], None, INK, 2, False)
    if boot:
        a.shape([(x + 5, y - 39), (x + 30, y - 39), (x + 34, y - 4),
                 (x + 52, y + 6), (x + 76, y + 9),
                 (x + 84, y + 13, x + 86, y + 23, x + 79, y + 24),
                 (x + 9, y + 28), (x - 2, y + 17), (x + 3, y - 5)], GLOVE)
        a.shape([(x - 1, y + 18), (x + 9, y + 28), (x + 81, y + 24),
                 (x + 79, y + 30), (x + 6, y + 34), (x - 3, y + 24)], INK)
        a.rect(x + 2, y - 53, 32, 20, ICE)
        a.arrow(x + 54, y - 31, x + 54, y - 3, BLUE, 2.5)


def drill_page(c):
    header(c, 1, "DRILL THE\nBLIND REGISTER",
           "One small pocket, inside each endcap.<br/>It locates the float rod without piercing the plate.")
    panel(c, 32, 164, 548, 254)
    text(c, "INSIDE FACE / TOP VIEW", 46, 184, 10, "PlexSemi", BLUE)
    text(c, "ENLARGED SECTION", 360, 184, 10, "PlexSemi", BLUE)
    with Art(c, 44, 192) as a:
        cx, cy, radius = 127, 105, 89
        plate(a, cx, cy, radius)
        a.line(cx - 98, cy, cx + 98, cy, MUTED, .7, [4, 3])
        a.line(cx, cy - 97, cx, cy + 97, MUTED, .7, [4, 3])
        ry = cy + D["register_radius"] * (2 * radius / D["disc_diameter"])
        a.ellipse(cx - 10, ry - 10, 20, 20, None, ORANGE, 1.3)
        a.dim(234, cy, 234, ry)
        a.line(cx + 3, cy, 243, cy, BLUE, .6)
        a.line(cx + 12, ry, 243, ry, BLUE, .6)
        a.label(f'{D["register_radius"]:.4f} in', 250, cy + 23, 11, BLUE)
        a.label(f'{D["register_radius"] * 25.4:.3f} mm', 250, cy + 39, 9.2, BLUE)
        a.label("from center", 250, cy + 54, 9, MUTED)
        a.label("Two existing ports", cx, 11, 10.5, INK, align="center")
    # A section drawn from the actual plate/depth/135-degree point proportions.
    with Art(c, 362, 236) as a:
        thickness, pocket = 55, 55 * D["register_depth"] / D["disc_thickness"]
        drill_width = D["register_drill_diameter"] / D["disc_thickness"] * thickness
        cone = drill_width / (2 * math.tan(math.radians(67.5)))
        a.label("Inside face", 0, -5, 11)
        a.rect(0, 7, 187, thickness)
        mx = 92
        a.shape([(mx - drill_width / 2, 7),
                 (mx - drill_width / 2, 7 + pocket - cone), (mx, 7 + pocket),
                 (mx + drill_width / 2, 7 + pocket - cone),
                 (mx + drill_width / 2, 7)], PAPER)
        a.dim(158, 7, 158, 7 + pocket)
        a.dim(158, 7 + pocket, 158, 7 + thickness)
        a.line(mx, 7 + pocket, 151, 7 + pocket, BLUE, .7)
        a.label("9/64 in drill", 0, 87, 13, BLUE)
        a.label(f'{D["register_depth"]:.3f} in to TIP', 0, 107, 13, ORANGE)
        remaining = D["disc_thickness"] - D["register_depth"]
        a.label(f'{remaining:.3f} in stays solid', 0, 127, 12, BLUE)
        a.label("Do not drill through.", 0, 149, 11, ORANGE)
    text(c, "Ports' midpoint = plate center. Pocket is on the perpendicular, toward -Y.",
         46, 404, 10.2, "Plex", MUTED)

    cards = [(32, 431, 1, "Locate the pocket",
              "Inside face up. Mark the location shown above on both plates."),
             (312, 431, 2, "Clamp the disc",
              "Secure it to the press table. Check the bit and chuck clear every clamp."),
             (32, 564, 3, "Set + prove the stop",
              f'Touch the stopped tip to the face. Set {D["register_depth"]:.3f} in travel; prove on scrap.'),
             (312, 564, 4, "Drill both plates",
              "9/64 in M35 cobalt, 135° split point. ~740 RPM; Tap Magic on the point.")]
    for x, y, n, title, copy in cards:
        panel(c, x, y, 268, 121)
        badge(c, n, x + 12, y + 10, title, size=13.5)
        paragraph(c, copy, x + 12, y + 81, 244, 10.8, 12.7, max_height=29)
        with Art(c, x + 18, y + 40) as a:
            if n == 1:
                plate(a, 62, 19, 24)
                a.line(62, 0, 62, 44, BLUE, .7, [2, 2])
                a.arrow(142, 6, 69, 34, ORANGE, 1.4, 5)
                a.label("inside face", 158, 24, 11, BLUE)
            elif n == 2:
                a.rect(19, 23, 150, 8)
                a.ellipse(47, 7, 96, 19)
                clamp(a, 46, 11)
                clamp(a, 145, 11, True)
                a.label("secured", 186, 25, 11, BLUE)
            elif n == 3:
                a.rect(16, 32, 100, 11)
                bit(a, 60, 0, 26)
                a.dim(141, 19, 141, 32)
                a.label("TIP depth", 158, 21, 11, ORANGE)
                a.label("scrap first", 158, 38, 10, MUTED)
            else:
                a.ellipse(35, 20, 62, 16)
                bit(a, 66, 0, 22)
                a.ellipse(132, 20, 62, 16)
                a.label("× 2", 211, 33, 16, BLUE, "PlexBold")

    box(c, 32, 698, 548, 43, ICE, radius=7)
    text(c, "CHECK BOTH POCKETS", 45, 715, 10, "PlexBold", BLUE)
    text(c, f'Blind, {D["register_depth"]:.3f} in to tip; {remaining:.3f} in of solid plate remains.',
         45, 732, 12, "PlexSemi")
    footer(c, 1, "Sources: pressure-vessel §1 / endcap drawing. Dimensions govern; picture is not a template.",
           "https://github.com/derekbreden/homesodamachine/blob/main/hardware/assembly/pressure-vessel.md")


def setup_page(c):
    header(c, 2, "SET UP THE\nCLOSURE WELD",
           "Working end up. Endcap's outer face toward you.<br/>The register face and float rod face into the tube.")
    box(c, 32, 164, 548, 34, "#FFF0E7", radius=6)
    paragraph(c, "<b>Class 4 laser.</b> Laser-rated eye/face protection, gloves, protective clothing.<br/>Use a protected welding area with fume extraction.",
              44, 169, 524, 10.5, 12.5, max_height=28)

    for x, title, n in [(32, "Clean + seat", 1), (312, "Tack opposite pairs", 2)]:
        panel(c, x, 208, 268, 218)
        badge(c, n, x + 12, 220, title, size=13.5)
    with Art(c, 46, 252) as a:
        # Enlarged cutaway: a recessed outside face, with mass beneath the fillet.
        a.rect(28, 6, 12, 127)
        a.rect(40, 50, 114, 44)
        a.shape([(40, 50), (40, 29), (62, 50)], "#F0B429")
        a.dim(166, 6, 166, 50)
        a.label("1/4 in", 178, 27, 12, BLUE)
        a.label("recess", 178, 42, 10, MUTED)
        a.label("outer face", 88, 46, 10, BLUE, align="center")
        a.label("interior", 82, 112, 10, MUTED)
        a.label("plate", 88, 76, 11, INK, align="center")
        a.label("rim", 11, 0, 9, MUTED)
    paragraph(c, "Clean the bore band and plate's outer face. Deburr tube ID + OD.<br/><b>Seat on the 1/4 in spacer; check all around.</b>",
              44, 384, 244, 11, 13, max_height=39)
    with Art(c, 323, 252) as a:
        plate(a, 122, 56, 47, False, True)
    paragraph(c, "Eight tacks, bisecting the gaps in opposite pairs. Recheck seated depth.<br/><b>The rod must not hold the plate up.</b>",
              324, 384, 244, 11, 13, max_height=39)

    for x, title, n in [(32, "Indicate the work", 3), (312, "Purge + prove contact", 4)]:
        panel(c, x, 438, 268, 207)
        badge(c, n, x + 12, 450, title, size=13.3)
    with Art(c, 51, 482) as a:
        tube(a, 35, 0, 80, 71)
        a.line(170, 4, 170, 75, BLUE, 3)
        a.rect(152, 71, 37, 12, ICE)
        a.ellipse(146, 6, 42, 42, ICE, BLUE)
        a.line(167, 27, 175, 18, BLUE)
        a.line(146, 32, 116, 32, BLUE, 2)
        a.label("TIR", 167, 39, 8, BLUE, align="center")
    paragraph(c, f'<b>Clamp the base; touch adjusters lightly.</b><br/>Weld-end radial TIR &lt;= {radial} mm.<br/>Endcap-face TIR &lt;= {face} mm.<br/>Use the commissioned rotator.',
              44, 588, 244, 10.7, 12.7, max_height=51)
    with Art(c, 330, 482) as a:
        tube(a, 39, 0, 79, 55, shoe=True)
        # Second-closure purge uses the two ports below, through the open base.
        a.line(48, 47, 109, 47, MUTED, 1)
        a.line(61, 47, 61, 76, BLUE, 1.5)
        a.line(94, 47, 94, 76, BLUE, 1.5)
        a.arrow(3, 82, 61, 82, BLUE, 1.6)
        a.arrow(61, 82, 61, 52, BLUE, 1.6)
        a.arrow(94, 53, 94, 82, BLUE, 1.6)
        a.arrow(94, 82, 145, 82, BLUE, 1.6)
        a.label("Ar in", 3, 98, 9, BLUE)
        a.label("vent", 131, 98, 9, BLUE)
        a.label("copper shoe", 155, 51, 9, COPPER)
    paragraph(c, "First: purge through open held end.<br/>Second: lower port in; other port vent.<br/><b>Scuff tube + shoe; clip work lead to shoe.</b><br/>Laser OFF: continuity for 2 dry turns.",
              324, 589, 244, 10.6, 12.5, max_height=51)

    box(c, 32, 657, 548, 49, ICE, radius=7)
    settings = [("POWER", f"{POWER}%"), ("WOBBLE", f"{HZ} Hz / {SWEEP} mm"),
                ("WIRE", f"{FEED} mm/s"), ("ARGON", f"{GAS} s pre/post"),
                ("FILLER", f"ER316L .{WIRE}")]
    widths = [90, 122, 100, 115, 121]
    xx = 32
    for (label, value), width in zip(settings, widths):
        text(c, label, xx + 11, 674, 8.7, "PlexBold", BLUE)
        text(c, value, xx + 11, 694, 12, "PlexSemi")
        xx += width
    paragraph(c, "<b>Recorded practice recipe.</b> Closure root fusion and internal oxidation still need qualification. These settings are for the endcap closure.",
              34, 717, 544, 10.8, 13, max_height=27)
    footer(c, 2, "Sources: pressure-vessel §§2-5 / weld-rotation-rig / X1 Pro manual, pp.11-14.", MANUAL)


def start_page(c):
    header(c, 3, "START THE BEAD",
           "Your foot turns the tube. Your trigger starts the weld.<br/>Hold the head steady as the joint travels under it.")
    # A deliberately short header gives the comic more drawing space.
    top = 139
    frames = [(32, top, 1, "Set speed while stopped"),
              (312, top, 2, "Aim into the corner"),
              (32, top + 151, 3, "Ready the welder"),
              (312, top + 151, 4, "Press + hold the pedal")]
    for x, y, n, title in frames:
        panel(c, x, y, 268, 146)
        badge(c, n, x + 12, y + 10, title, size=13.1)
        with Art(c, x + 16, y + 43) as a:
            if n == 1:
                a.rect(0, 0, 125, 49, INK)
                a.label("status", 9, 16, 11, PAPER, "Plex")
                a.label(f'speed {R["TRAVEL_NOMINAL"]:.1f}', 9, 36, 15, PAPER, "PlexSemi")
                plate(a, 189, 27, 22, False)
                turn_arrow(a, 164, 0, 48)
                copy = f'Start at {R["TRAVEL_NOMINAL"]:g} mm/s travel. Verify direction from above and return the index to the first tack.'
            elif n == 2:
                a.rect(25, 28, 10, 27)
                a.rect(35, 41, 61, 14)
                a.shape([(35, 41), (35, 32), (46, 41)], "#F0B429")
                gun(a, 42, 36, .48, cable=False)
                a.label("plate mass", 171, 42, 9.5, BLUE)
                copy = 'Beam into plate mass, washing onto wall. Wire on arriving side. Use the coupon-proven angle + standoff.'
            elif n == 3:
                a.rect(0, 0, 238, 52, INK)
                a.label("WELDING", 10, 15, 10, PAPER, "PlexSemi")
                for j, word in enumerate(["Wire feed", "Gas", "Laser enable"]):
                    a.rect(8 + j * 78, 24, 69, 21, BLUE)
                    a.label(word, 42 + j * 78, 38, 8.5, PAPER, align="center")
                copy = 'PPE + protected area ready; shielding and back-purge established. Enable wire feed and laser on the X1 Pro.'
            else:
                a.c.saveState()
                a.c.scale(.42, .42)
                pedal(a, 24, 53)
                a.c.restoreState()
                tube(a, 170, 3, 32, 22)
                turn_arrow(a, 168, 0, 39)
                copy = 'Keep the trigger released. Hold the pedal down until rotation is steady; keep the head at the joint.'
        paragraph(c, copy, x + 12, y + 100, 244, 10.6, 12, max_height=37)

    box(c, 32, 442, 548, 64, ICE, radius=7)
    text(c, "KNOW THE FINISH BEFORE YOU START", 44, 458, 9.8, "PlexBold", BLUE)
    paragraph(c, f'Carry the bead a full lap, then about {R["OVERLAP_DEGREES"]:g}° past the first tack. Trail off; <b>release trigger, then pedal.</b> Keep the head in position for post-flow. The table has no automatic stop. Snip stuck wire with the gun held still.',
              44, 465, 524, 11.4, 13.8, max_height=42)

    panel(c, 32, 519, 548, 219)
    badge(c, 5, 45, 533, "Pedal held. Pull + hold the trigger.", ORANGE, 19)
    text(c, "STEADY ROTATION FIRST", 566, 572, 9.8, "PlexBold", BLUE, "right")
    # Final frame includes both active controls, with a visible gloved trigger finger.
    with Art(c, 49, 576) as a:
        tube(a, 44, 28, 99, 83, shoe=True)
        gun(a, 126, 40, .75, hand=True, firing=True)
        turn_arrow(a, 55, 0, 62)
        a.arrow(197, 118, 212, 52, ORANGE, 1.4, 5)
        a.label("TRIGGER HELD", 182, 132, 12, ORANGE, "PlexBold")
        pedal(a, 367, 64)
        a.label("PEDAL DOWN", 410, 123, 12, BLUE, "PlexBold", "center")
        a.label("Tube rotates", 90, 150, 10, BLUE, align="center")
        a.label("Weld begins at the moving corner", 208, 150, 11, ORANGE)
    footer(c, 3, "Sources: per-weld sequence 46 / rotator controls / X1 Pro manual, pp.12-14. Pose is schematic.", MANUAL)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(PDF), pagesize=(W, H), invariant=1, pageCompression=1)
    c.setTitle("Assembly bench sheets - Drill the endcap and start the weld")
    c.setAuthor("Home Soda Machine")
    c.setSubject("Three borderless Letter sheets: blind register, weld setup, pedal and trigger")
    for draw in [drill_page, setup_page, start_page]:
        draw(c)
        c.showPage()
    c.save()
    manifest = {
        "pdf": PDF.name,
        "pages": 3,
        "page_inches": [8.5, 11],
        "artwork": "vector schematic; dimensions govern; no drilling template or qualified gun pose",
        "source_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in SOURCES.values()
        },
        "manufacturer_source": MANUAL,
        "endcap_inches": D,
        "rotator_mm": R,
        "practice_recipe": dict(zip(["power_percent", "wobble_hz", "sweep_mm",
                                      "wire_mm_s", "argon_pre_post_s", "wire_inches_suffix",
                                      "tacks"], recipe.groups())),
        "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
    }
    (OUT / "assembly-drill-and-weld-letter.sources.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {PDF.relative_to(ROOT)} (3 pages, 8.5 x 11 in)")


if __name__ == "__main__":
    main()
