"""Carbonator closure assembly: source-defined sections and an exterior end view.

Fabrication state of HSM-000004, before permanent fittings. Registers show their
actual drill points; the rod has its fixed finished length and the cap spacing
is controlled to its specified interface tolerance. Weld profiles are
diagrammatic because a qualified weld size is not established by the procedure.
"""

import sys
from pathlib import Path

from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from _carbonator_drawing import *

PDF_PATH = HERE / "carbonator-vessel-weldment-drawing.pdf"
SHEET = (17 * IN, 11 * IN)
CX, BASE = 330, 242

REVIEW_REGIONS = [
    ("section-upper", 30, 594, 655, 765),
    ("section-body", 30, 330, 655, 600),
    ("section-lower", 30, 185, 655, 335),
    ("end-view", 640, 473, 1190, 765),
    ("closure-detail", 875, 478, 1190, 765),
    ("parts-list", 642, 353, 1180, 476),
    ("requirements", 642, 145, 1180, 355),
    ("title-release", 35, 27, 1197, 181),
]


def z(value):
    return BASE + value * IN


def longitudinal_section(c):
    text(c, CX, 750, "SECTION A-A", 12, bold=True, align="center")
    text(c, CX, 733, "THROUGH VESSEL AND ROD AXES - SCALE 1:1", 9, align="center")
    left, right = CX - OD * IN / 2, CX + OD * IN / 2
    bore_l, bore_r = CX - ID * IN / 2, CX + ID * IN / 2
    cap_l, cap_r = CX - CAP_D * IN / 2, CX + CAP_D * IN / 2
    for a, b in ((left, bore_l), (bore_r, right)):
        section_material(c, [(a, BASE), (b, BASE), (b, z(LENGTH)), (a, z(LENGTH))], spacing=6)
    for lo, hi in ((RECESS, FLOOR), (CEILING, LENGTH - RECESS)):
        section_material(c, [(cap_l, z(lo)), (cap_r, z(lo)),
                             (cap_r, z(hi)), (cap_l, z(hi))], reverse=True)
    for wall_x, side in ((bore_l, 1), (bore_r, -1)):
        for face_y, up in ((z(RECESS), -1), (z(LENGTH - RECESS), 1)):
            # Same diagrammatic fillet as detail B, at the view scale.
            p = c.beginPath()
            p.moveTo(wall_x + side * 5, face_y)
            p.curveTo(wall_x + side * 2, face_y + up * 0.5,
                      wall_x + side * 0.5, face_y + up * 2,
                      wall_x, face_y + up * 5)
            p.lineTo(wall_x, face_y)
            p.close()
            c.setFillColorRGB(0.85, 0.85, 0.85)
            c.setLineWidth(0.5)
            c.drawPath(p, fill=1, stroke=1)
            c.setFillColorRGB(0, 0, 0)
    rod_x = CX + ROD_X * IN
    register_opening(c, rod_x, z(FLOOR), IN, -1)
    register_opening(c, rod_x, z(CEILING), IN, 1)
    # Longitudinal solid rod is left unhatched, at its finished nominal length.
    c.setFillColorRGB(1, 1, 1)
    c.setLineWidth(VISIBLE)
    c.rect(rod_x - ROD_D * IN / 2, z(ROD_BOTTOM), ROD_D * IN,
           (ROD_TOP - ROD_BOTTOM) * IN, stroke=1, fill=1)
    c.setFillColorRGB(0, 0, 0)
    line(c, CX, BASE - 15, CX, z(LENGTH) + 15, dash=CENTER_DASH)
    line(c, rod_x, z(ROD_BOTTOM) - 9, rod_x, z(ROD_TOP) + 9, dash=CENTER_DASH)
    # Float is a reference envelope at an arbitrary position in its travel.
    float_w, float_h = FLOAT_D * IN, FLOAT_H * IN
    c.setDash((10, 3, 2, 3, 2, 3))
    c.setLineWidth(THIN)
    c.rect(rod_x - float_w / 2, z(2.6), float_w, float_h, stroke=1, fill=0)
    c.setDash()
    balloon(c, 1, (126, 488), (left, 454))
    balloon(c, 2, (185, 610), (210, z(CEILING)))
    balloon(c, 2, (185, 310), (210, z(FLOOR)))
    balloon(c, 3, (352, 554), (rod_x - ROD_D * IN / 2, 525))
    balloon(c, 4, (365, 399), (rod_x - float_w / 2, z(2.6) + 20))
    vdim(c, 95, BASE, z(LENGTH), left, left, f"{LENGTH:.3f} REF", size=10)
    # Direct inside-face dimension: arrow tips touch the two physical planes.
    gap_x = 250
    line(c, gap_x, z(FLOOR), gap_x, z(CEILING))
    arrow(c, (gap_x, z(FLOOR)), (gap_x, z(CEILING)))
    arrow(c, (gap_x, z(CEILING)), (gap_x, z(FLOOR)))
    text(c, gap_x - 9, z((FLOOR + CEILING) / 2),
         f"{INSIDE_SPAN:.3f} ±{INSIDE_SPAN_TOL:.3f}", 10, align="right")
    text(c, gap_x - 9, z((FLOOR + CEILING) / 2) - 14,
         "CAP SPAN AT R1", 8, align="right")
    # Detail boundary has its own identifier, separate from the section arrows.
    c.setLineWidth(0.5)
    c.circle(bore_r - 2, z(LENGTH - RECESS) + 2, 23, stroke=1, fill=0)
    line(c, bore_r + 13, z(LENGTH - RECESS) + 19, 546, 708)
    text(c, 551, 710, "B", 12, bold=True)
    leader(c, (rod_x + ROD_D * IN / 2, 580), (525, 550), (545, 550),
           ["FINISHED ROD", "PER FR-CARB-01"], 8.5)
    # A representative tack at the bottom register; the procedure governs it.
    tack_tip = (rod_x + ROD_D * IN / 2, z(FLOOR))
    tack = path_from_points(c, [tack_tip, (tack_tip[0] + 2.5, tack_tip[1]),
                               (tack_tip[0], tack_tip[1] + 2.5)])
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.drawPath(tack, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    leader(c, (tack_tip[0] + 1, tack_tip[1] + 1), (525, 320), (545, 320),
           ["T1 - ROD TACK", "BOTTOM CAP ONLY"], 8.5)
    text(c, CX, 211, "FIXED-LENGTH ROD SEATS IN BOTTOM REGISTER; TOP REGISTER RETAINS CLEARANCE.", 8, align="center")
    text(c, CX, 197, "PORTS LIE OUT OF THE SECTION PLANE. FLOAT ENVELOPE IS REFERENCE ONLY.", 8, align="center")


def outside_end_view(c):
    x, y, s = 780, 613, IN / 2
    text(c, x, 750, "TOP OUTSIDE END VIEW", 11, bold=True, align="center")
    text(c, x, 733, "LOOKING DOWN -Z - SCALE 1:2", 8.5, align="center")
    c.setLineWidth(VISIBLE)
    c.circle(x, y, OD * s / 2, stroke=1, fill=0)
    c.setLineWidth(THIN)
    c.circle(x, y, ID * s / 2, stroke=1, fill=0)
    line(c, x - 101, y, x + 101, y, dash=CENTER_DASH)
    line(c, x, y - 101, x, y + 101, dash=CENTER_DASH)
    port_r = cap.hole_radius * s
    for sign in (-1, 1):
        py = y + sign * carb.carbonator_port_offset / MM * s
        c.setLineWidth(VISIBLE)
        c.circle(x, py, port_r, stroke=1, fill=0)
        c.setLineWidth(THIN)
        c.arc(x - port_r - 1.5, py - port_r - 1.5,
              x + port_r + 1.5, py + port_r + 1.5, 35, 270)
        center(c, x, py, 13)
    rx = x + ROD_X * s
    c.setDash((3, 2))
    c.circle(rx, y, REG_D * s / 2, stroke=1, fill=0)
    c.setDash()
    center(c, rx, y, 8)
    cutting_plane_ends(c, x - 113, x + 113, y, "A", rise=18)
    text(c, x + 9, y + 104, "+Y", 8)
    text(c, rx, y - 20, "R1", 8, bold=True, align="center")
    horizontal_dimension(c, x - OD * s / 2, x + OD * s / 2, y,
                         496, f"Ø{OD:.3f} REF", 9)
    text(c, x, 481, "BOTH R1 REGISTERS SHARE +X; BOTH PORT PAIRS SHARE ±Y.", 7.7, align="center")


def closure_detail(c):
    x, rim, s = 1050, 701, 4 * IN
    outside, inside = rim - RECESS * s, rim - (RECESS + CAP_T) * s
    wall_right, cap_edge = x + WALL * s, x - (ID - CAP_D) / 2 * s
    text(c, 1050, 750, "DETAIL B - CLOSURE JOINT", 10.5, bold=True, align="center")
    text(c, 1050, 733, "SCALE 4:1 - LOWER END MIRRORED", 8.3, align="center")
    section_material(c, [(x, rim), (wall_right, rim), (wall_right, inside - 22),
                         (x + WALL * s * 0.66, inside - 19),
                         (x + WALL * s * 0.33, inside - 25),
                         (x, inside - 22)], spacing=8)
    cap_left = x - 76
    section_material(c, [(cap_left, outside), (cap_edge, outside), (cap_edge, inside),
                         (cap_left, inside), (cap_left + 3, inside + 20),
                         (cap_left - 3, inside + 29),
                         (cap_left + 3, inside + 38),
                         (cap_left, inside + 45)], spacing=7, reverse=True)
    # A schematic concave fillet shows the joint's side and extent. Its leg
    # length is deliberately undimensioned pending the production qualification.
    p = c.beginPath()
    p.moveTo(x - 20, outside)
    p.curveTo(x - 8, outside + 2, x - 2, outside + 8, x, outside + 20)
    p.lineTo(x, outside)
    p.close()
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.setLineWidth(0.7)
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)
    vdim(c, 947, outside, rim, cap_left, x, f"2X {RECESS:.3f}")
    leader(c, (x - 11, outside + 6), (1094, 583), (1114, 583),
           ["W1 - FILLET", "BOTH ENDS"], 8.5)
    text(c, 1050, 507, "WELD PROFILE DIAGRAMMATIC; SIZE NOT ESTABLISHED.", 7.8, align="center")
    text(c, 1050, 493, "CAP OD / BORE SLIP GAP SHOWN; DO NOT CHAMFER WELD ROOT.", 7.5, align="center")


def parts_list(c):
    left, right, top, height = 650, 1177, 452, 19
    columns = (left, 681, 715, 797, right)
    text(c, left, top + 13, "PARTS AT CLOSURE", 10, bold=True)
    rows = [
        ("ITEM", "QTY", "MATERIAL", "DESCRIPTION / DEFINITION"),
        ("1", "1", "HSM-000008", f"316 SS TUBE; Ø{OD:.3f} x {WALL:.3f} WALL x {LENGTH:.3f}"),
        ("2", "2", "HSM-000009", "316 SS FINISHED END CAP; END-CAP-01"),
        ("3", "1", "HSM-000336", "316 SS FLOAT GUIDE ROD; FR-CARB-01"),
        ("4", "1", "HSM-000032", "ASA AERO MAGNETIC FLOAT; INSTALL BEFORE CLOSURE"),
    ]
    c.setLineWidth(THIN)
    c.rect(left, top - len(rows) * height, right - left, len(rows) * height, stroke=1, fill=0)
    for col in columns[1:-1]:
        line(c, col, top - len(rows) * height, col, top)
    for i, row in enumerate(rows):
        baseline = top - i * height - 12
        if i:
            line(c, left, top - i * height, right, top - i * height)
        for j, value in enumerate(row):
            text(c, columns[j] + 5, baseline, value, 7.7, bold=i == 0)


def requirements(c):
    text(c, 650, 336, "ASSEMBLY REQUIREMENTS", 10, bold=True)
    paragraphs = [
        "1. Fabrication state of HSM-000004 before permanent fittings. Component ports, registers and edge preparation: END-CAP-01. Stock dimensions are nominal.",
        f"2. Finished cap inside-face spacing AT ROD AXIS: {INSIDE_SPAN:.3f} ±{INSIDE_SPAN_TOL:.3f}. Set both outside faces 0.250 below adjacent tube rims. Align both port pairs on one diameter; both R1 register axes coaxial with the rod. Rod +X faces reservoir B; ports lie on ±Y in the cold core.",
        "3. Use the fixed-length rod per FR-CARB-01. Seat and tack it in the bottom register before the bottom closure weld. Install the float before top closure; verify top engagement, free travel and full cap seating at the specified spacing.",
        "4. W1: continuous internal-corner fillet around BOTH cap perimeters. ER316L .030 filler. Clean bore band and cap outside face; preserve the square cap weld root. T1: tack rod to bottom cap. Welding, inspection, hydro and passivation: pressure-vessel procedure, steps 2-8.",
    ]
    end = wrap_lines(c, 650, 318, paragraphs, 525, size=8.6, leading=11.3, gap=5)
    return end


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Carbonator vessel - closure assembly engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("CV-WLD-01 Rev B: closure geometry, cap clocking and fixed-length rod interface")
    frame(c, SHEET)
    longitudinal_section(c)
    outside_end_view(c)
    closure_detail(c)
    parts_list(c)
    requirements(c)
    text(c, 47, 168, "RELEASE ITEMS: W1 SIZE AND WELD QUALIFICATION; REMAINING UNSPECIFIED ASSEMBLY TOLERANCES.", 8.5, bold=True)
    title_block(c, SHEET, "CARBONATOR VESSEL - CLOSURE ASSEMBLY", "CV-WLD-01",
                "SEE PARTS LIST", "1 PER MACHINE", "HSM-000004 / FABRICATION STATE",
                revision="B")
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
