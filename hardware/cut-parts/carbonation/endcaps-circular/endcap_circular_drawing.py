"""Finished carbonator end cap, on one ANSI B landscape engineering sheet.

The face view and location table describe the two tapped ports and the blind
rod register. Section A-A identifies the plate faces and NPT entry direction;
local section B-B shows the actual 135-degree drill point and tip-depth datum.
All part dimensions come from the laser-blank/register source module. Thread
lines are a conventional representation, not a model of the helical surfaces.

Run with tools/cad-venv/bin/python. No CAD or cut-file geometry is changed.
"""

import math
import sys
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(ROOT / "hardware" / "scripts"))
from _cadq_export import export_pdf
from endcap_circular_dxf import (
    disc_diameter,
    disc_thickness,
    hole_positions,
    hole_radius,
    register_position,
    register_drill_diameter,
    register_depth,
)

PDF_PATH = HERE / "endcap-circular-2hole-drawing.pdf"
REVISION = "C"
REVISION_DATE = "2026-10-26"
SHEET = (17 * inch, 11 * inch)
MARGIN = 27
VISIBLE = 0.85
THIN = 0.35
CENTER_DASH = (12, 3, 2, 3)
CX, CY = 294, 490
RADIUS = disc_diameter * inch / 2


def line(c, x1, y1, x2, y2, weight=THIN, dash=()):
    c.setLineWidth(weight)
    c.setDash(dash)
    c.line(x1, y1, x2, y2)
    c.setDash()


def text(c, x, y, value, size=9, bold=False, align="left"):
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    if align == "center":
        c.drawCentredString(x, y, value)
    elif align == "right":
        c.drawRightString(x, y, value)
    else:
        c.drawString(x, y, value)


def arrow(c, tip, tail, length=6, width=2):
    """A filled arrow whose point touches the feature or extension line."""
    dx, dy = tip[0] - tail[0], tip[1] - tail[1]
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    bx, by = tip[0] - length * ux, tip[1] - length * uy
    p = c.beginPath()
    p.moveTo(*tip)
    p.lineTo(bx - width * uy, by + width * ux)
    p.lineTo(bx + width * uy, by - width * ux)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def leader(c, tip, knee, end, lines, size=9):
    """End the shoulder beside the first line, at the text's mid-height."""
    line(c, *tip, *knee)
    line(c, *knee, *end)
    arrow(c, tip, knee)
    text_on_right = end[0] > knee[0]
    text_x = end[0] + (4 if text_on_right else -4)
    align = "left" if text_on_right else "right"
    cap_height = pdfmetrics.getAscent("Helvetica", size)
    for i, value in enumerate(lines):
        text(c, text_x, end[1] - cap_height / 2 - i * 12,
             value, size, align=align)


def circular_leader(c, center_xy, radius, knee, end, lines, size=9):
    """Touch the circle exactly, with the inclined line directed radially."""
    dx, dy = knee[0] - center_xy[0], knee[1] - center_xy[1]
    distance = math.hypot(dx, dy)
    tip = (center_xy[0] + radius * dx / distance,
           center_xy[1] + radius * dy / distance)
    leader(c, tip, knee, end, lines, size)


def horizontal_dimension(c, x1, x2, witness_y, dim_y, label, size=10):
    sign = 1 if dim_y > witness_y else -1
    for x in (x1, x2):
        line(c, x, witness_y + sign * 4, x, dim_y + sign * 5)
    line(c, x1, dim_y, x2, dim_y)
    arrow(c, (x1, dim_y), (x2, dim_y))
    arrow(c, (x2, dim_y), (x1, dim_y))
    text(c, (x1 + x2) / 2, dim_y + 5, label, size, align="center")


def vertical_dimension(c, x, y1, y2, witness_x, lines, outside=False):
    """Text at the right; outside arrows make the thin plate legible."""
    for y in (y1, y2):
        line(c, witness_x + 4, y, x + 5, y)
    if outside:
        line(c, x, y1 - 13, x, y2 + 13)
        arrow(c, (x, y1), (x, y1 - 13))
        arrow(c, (x, y2), (x, y2 + 13))
    else:
        line(c, x, y1, x, y2)
        arrow(c, (x, y1), (x, y2))
        arrow(c, (x, y2), (x, y1))
    y = (y1 + y2) / 2 + (len(lines) - 1) * 5 - 3
    for i, value in enumerate(lines):
        text(c, x + 9, y - i * 11, value, 9)


def center(c, x, y, half=13):
    line(c, x - half, y, x + half, y, dash=CENTER_DASH)
    line(c, x, y - half, x, y + half, dash=CENTER_DASH)


def hatch(c, path, bounds, spacing=7):
    """45-degree section lines, clipped to material, never to the hole."""
    c.saveState()
    c.clipPath(path, stroke=0, fill=0)
    x0, y0, x1, y1 = bounds
    for offset in range(math.floor(x0 - (y1 - y0)), math.ceil(x1) + 1, spacing):
        line(c, offset, y0, offset + (y1 - y0), y1, 0.25)
    c.restoreState()


def path_from_points(c, points):
    p = c.beginPath()
    p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    p.close()
    return p


def cutting_plane_ends(c, left, right, y, label, rise=21):
    """The viewing arrows point up the inside-face view (+Y)."""
    line(c, left, y, left + 16, y, 1.0)
    line(c, right - 16, y, right, y, 1.0)
    for x in (left, right):
        line(c, x, y, x, y + rise, 1.0)
        arrow(c, (x, y + rise), (x, y), length=8, width=2.5)
        text(c, x, y + rise + 7, label, 11, bold=True, align="center")


def face_view(c):
    text(c, CX, 734, "INSIDE FACE VIEW", 12, bold=True, align="center")
    text(c, CX, 718, "SCALE 1:1", 9, align="center")
    c.setLineWidth(VISIBLE)
    c.circle(CX, CY, RADIUS, stroke=1, fill=0)
    line(c, CX - RADIUS - 13, CY, CX + RADIUS + 13, CY,
         dash=CENTER_DASH)
    line(c, CX, CY - RADIUS - 13, CX, CY + RADIUS + 13,
         dash=CENTER_DASH)
    # The visible minor circle and thin partial root arc identify internal
    # threads. Neither graphic diameter is a finished-port inspection size.
    for i, (px, py) in enumerate(hole_positions, 1):
        x, y = CX + px * inch, CY + py * inch
        minor = hole_radius * inch
        c.setLineWidth(VISIBLE)
        c.circle(x, y, minor, stroke=1, fill=0)
        c.setLineWidth(THIN)
        root = minor + 0.04 * inch
        c.arc(x - root, y - root, x + root, y + root, 35, 270)
        center(c, x, y, 24)
        text(c, x, y + 31, f"P{i}", 10, bold=True, align="center")
    rx, ry = CX + register_position[0] * inch, CY + register_position[1] * inch
    c.setLineWidth(VISIBLE)
    c.circle(rx, ry, register_drill_diameter * inch / 2, stroke=1, fill=0)
    center(c, rx, ry, 10)
    # A-A passes through the two ports. B-B is a local section at R1.
    cutting_plane_ends(c, CX - RADIUS - 24, CX + RADIUS + 24, CY, "A")
    line(c, rx - 28, ry, rx + 28, ry, dash=CENTER_DASH)
    cutting_plane_ends(c, rx - 37, rx + 37, ry, "B", rise=16)
    circular_leader(c, (CX + hole_positions[1][0] * inch, CY), hole_radius * inch,
                    (484, 600), (510, 600),
                    ["2X 1/4-18 NPT THRU", "TAP FROM OUTSIDE FACE", "P1, P2 - SEE NOTE 2"], 10)
    circular_leader(c, (rx, ry), register_drill_diameter * inch / 2,
                    (429, 351), (510, 351),
                    ["R1 - BLIND ROD REGISTER", "SEE SECTION B-B"], 9)
    # The witnesses start at the actual OD silhouette, not an imaginary
    # rectangle tangent to the bottom of the disc.
    horizontal_dimension(c, CX - RADIUS, CX + RADIUS, CY,
                         286, f"Ø{disc_diameter:.3f}", 11)


def port_section(c):
    bottom = 226
    top = bottom + disc_thickness * inch
    left, right = CX - RADIUS, CX + RADIUS
    outer = path_from_points(c, [(left, bottom), (right, bottom),
                                (right, top), (left, top)])
    hatch(c, outer, (left, bottom, right, top), spacing=6)
    c.setLineWidth(VISIBLE)
    c.drawPath(outer, stroke=1, fill=0)
    for px, _ in hole_positions:
        x = CX + px * inch
        r_inside = hole_radius * inch
        # Conventional thread envelope: taper is larger at the outside
        # entry. The thread designation and functional trial govern fit.
        r_outside = r_inside + disc_thickness * inch / 32
        opening = path_from_points(c, [(x - r_outside, bottom),
                                      (x + r_outside, bottom),
                                      (x + r_inside, top), (x - r_inside, top)])
        c.setFillColorRGB(1, 1, 1)
        c.drawPath(opening, stroke=0, fill=1)
        c.setFillColorRGB(0, 0, 0)
        line(c, x - r_outside, bottom, x - r_inside, top, VISIBLE)
        line(c, x + r_outside, bottom, x + r_inside, top, VISIBLE)
        for sign in (-1, 1):
            line(c, x + sign * (r_outside + 0.04 * inch), bottom,
                 x + sign * (r_inside + 0.04 * inch), top)
        line(c, x, bottom - 9, x, top + 9, dash=CENTER_DASH)
    vertical_dimension(c, 493, bottom, top, right, [f"{disc_thickness:.3f}"],
                       outside=True)
    text(c, CX, 194, "SECTION A-A", 11, bold=True, align="center")
    text(c, CX, 180, "SCALE 1:1 - THREADS SHOWN CONVENTIONALLY", 8,
         align="center")
    # Direct face labels make tap entry and OD preparation unambiguous.
    leader(c, (175, top), (140, 273), (110, 273),
           ["INSIDE FACE"], 8.5)
    leader(c, (405, bottom), (425, 190), (445, 190),
           ["OUTSIDE FACE", "NPT ENTRY / WELD FACE"], 8.5)


def register_section(c):
    scale = 4 * inch
    x, top, half_width = 900, 630, 122
    bottom = top - disc_thickness * scale
    radius = register_drill_diameter * scale / 2
    tip = top - register_depth * scale
    point_angle = 135
    point_height = radius / math.tan(math.radians(point_angle / 2))
    shoulder = tip + point_height
    text(c, x, 734, "SECTION B-B", 12, bold=True, align="center")
    text(c, x, 718, "LOCAL VIEW AT R1 - SCALE 4:1", 9, align="center")
    # Broken ends crop the plate locally; the V is the drill point, not a
    # flat-bottom pocket. The source depth always ends at its deepest tip.
    left, right = x - half_width, x + half_width
    points = [(left, top), (x - radius, top), (x - radius, shoulder),
              (x, tip), (x + radius, shoulder), (x + radius, top),
              (right, top), (right, top - 23), (right + 4, top - 30),
              (right - 4, top - 40), (right, top - 47), (right, bottom),
              (left, bottom), (left, bottom + 23), (left - 4, bottom + 30),
              (left + 4, bottom + 40), (left, bottom + 47)]
    material = path_from_points(c, points)
    hatch(c, material, (left - 5, bottom, right + 5, top), spacing=8)
    c.setLineWidth(VISIBLE)
    c.drawPath(material, stroke=1, fill=0)
    line(c, x, bottom - 9, x, top + 18, dash=CENTER_DASH)
    horizontal_dimension(c, x - radius, x + radius, top, 674, "Ø9/64", 10)
    # Both depth witnesses originate on the inside face and actual drill tip.
    vertical_dimension(c, 1050, tip, top, right, [f"{register_depth:.3f}", "TO TIP"])
    # Extend the tip datum from the real point without painting through the
    # section hatching. The first depth extension is continued to that point.
    line(c, x + 4, tip, right + 4, tip)
    remaining = disc_thickness - register_depth
    vertical_dimension(c, 1125, bottom, tip, right,
                       [f"{remaining:.3f} REF", "WEB"])
    text(c, left, top + 13, "INSIDE FACE", 8.5)
    text(c, left, bottom - 16, "OUTSIDE FACE", 8.5)
    text(c, x, 526, "135° DRILL POINT", 9, align="center")
    text(c, x, 511, "DO NOT BREAK THROUGH", 10, bold=True, align="center")


def location_table(c):
    left, right, top = 705, 1168, 455
    columns = (left, left + 65, left + 154, left + 243, right)
    row_height = 24
    bottom = top - 4 * row_height
    text(c, left, top + 14, "FEATURE LOCATIONS", 10, bold=True)
    c.setLineWidth(THIN)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    for x in columns[1:-1]:
        line(c, x, bottom, x, top)
    for i in range(1, 4):
        line(c, left, top - i * row_height, right, top - i * row_height)
    headers = ("FEATURE", "X", "Y", "DESCRIPTION")
    for i, value in enumerate(headers):
        text(c, (columns[i] + columns[i + 1]) / 2, top - 16, value,
             8.5, bold=True, align="center")
    features = [("P1", *hole_positions[0], "THREADED PORT"),
                ("P2", *hole_positions[1], "THREADED PORT"),
                ("R1", *register_position, "BLIND ROD REGISTER")]
    for row, (feature, x, y, description) in enumerate(features, 1):
        baseline = top - row_height * row - 16
        values = (feature, f"{x:.3f}", f"{y:.3f}", description)
        for i, value in enumerate(values):
            text(c, (columns[i] + columns[i + 1]) / 2, baseline, value,
                 9, bold=i == 0, align="center")
    text(c, left, bottom - 16,
         "ORIGIN: DISC OD CENTER. +X RIGHT; +Y UP IN INSIDE FACE VIEW.", 8)
    text(c, left, bottom - 29,
         "COORDINATES LOCATE FEATURE AXES. HOLE AXES NORMAL TO FACES.", 8)


def notes(c):
    x, y = 661, 306
    text(c, x, y, "FABRICATION NOTES", 10, bold=True)
    rows = [
        "1. BLANK: ENDCAP-CIRCULAR-2HOLE.DXF; TWO Ø0.438 LASER-CUT PILOTS.",
        "2. CLEAR THE CUT LIP ON BOTH PORT FACES WITH AN 82° COUNTERSINK",
        "    BEFORE TAPPING. NPT FORM: ASME B1.20.1. TARGET 4.5 TURNS",
        "    ENGAGEMENT; VERIFY ELBOW FIT AND FINAL CLOCKING ON A TRIAL",
        "    PART PER PRESSURE-VESSEL PROCEDURE, STEP 1.",
        "3. R1 IS BLIND. TOP CAP ONLY: Ø5/32 AT THE SAME TIP DEPTH IS",
        "    PERMITTED IF NEEDED FOR ROD-TIP FIT. BOTH CAPS START AT Ø9/64.",
        "4. OD: CHAMFER THE INSIDE EDGE FOR INSERTION. OUTSIDE EDGE:",
        "    REMOVE BURR ONLY; PRESERVE THE SQUARE CLOSURE-WELD CORNER.",
        "5. REMOVE BURRS, CHIPS AND CUTTING FLUID. ROD TACK AND VESSEL",
        "    WELDS: PRESSURE-VESSEL ASSEMBLY PROCEDURE.",
    ]
    for i, value in enumerate(rows):
        text(c, x, y - 19 - i * 12, value, 8.6)


def title_block(c):
    left, bottom, right, top = 635, MARGIN, SHEET[0] - MARGIN, 143
    c.setLineWidth(0.7)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    line(c, left, 98, right, 98)
    line(c, left, 65, right, 65)
    line(c, 1010, 98, 1010, top)
    text(c, left + 10, 125, "HOME SODA MACHINE", 8)
    text(c, left + 10, 108, "CARBONATOR END CAP - FINISHED", 13, bold=True)
    text(c, 1104, 124, "PROTOTYPE", 10, bold=True, align="center")
    text(c, 1104, 109, "FOR REVIEW", 9, align="center")
    for x in (866, 1030):
        line(c, x, 65, x, 98)
    for x, label, value in [(left + 10, "MATERIAL", "316 STAINLESS STEEL"),
                            (876, "UNITS", "INCHES"),
                            (1040, "QUANTITY", "2 PER CARBONATOR")]:
        text(c, x, 87, label, 7)
        text(c, x, 73, value, 9, bold=True)
    fields = [(635, 815, "DRAWING", "END-CAP-01"),
              (815, 867, "REV", REVISION),
              (867, 990, "DATE", REVISION_DATE),
              (990, 1113, "SCALE", "AS SHOWN"),
              (1113, 1197, "SHEET", "1 OF 1")]
    for i, (a, b, label, value) in enumerate(fields):
        if i:
            line(c, a, bottom, a, 65)
        text(c, a + 9, 53, label, 7)
        text(c, a + 9, 37, value, 9, bold=True)
    text(c, 47, 125, "UNLESS OTHERWISE SPECIFIED", 9, bold=True)
    text(c, 47, 108, "LINEAR ±0.005 IN     ANGULAR ±0.5°", 10)
    text(c, 47, 91, "REFERENCE DIMENSIONS ARE IDENTIFIED BY REF.", 8.5)
    text(c, 47, 65, "DIMENSIONS GOVERN. DO NOT SCALE THE DRAWING.", 9, bold=True)
    text(c, 47, 49, "ANSI B / 17 x 11 IN. PRINT AT 100% FOR THE STATED VIEW SCALES.", 8)
    text(c, 47, 36, "MACHINED CAP COMMON TO TOP AND BOTTOM; ROD TACK IS AN ASSEMBLY OPERATION.", 8)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Carbonator end cap - finished machined part")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject(f"END-CAP-01 Rev {REVISION}: tapped ports, blind float-rod register and face-specific edge preparation")
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(MARGIN, MARGIN, SHEET[0] - 2 * MARGIN, SHEET[1] - 2 * MARGIN,
           stroke=1, fill=0)
    face_view(c)
    port_section(c)
    register_section(c)
    location_table(c)
    notes(c)
    title_block(c)
    c.showPage()
    c.save()


def main():
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")


if __name__ == "__main__":
    main()
