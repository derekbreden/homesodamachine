"""Finished drilled water-inlet jet cap, on one ANSI A landscape sheet.

The nominal disc and through passage come from _water_inlet_jet, the same
parameters used by the installed model. This drawing owns finished-component
tolerances, centering, face condition and burr limits. The cap-to-elbow joint,
installed port fit and post-weld acceptance belong to assembly/water-inlet-jet.md.

Run with tools/cad-venv/bin/python. No CAD geometry or welding settings change.
"""

import sys
from pathlib import Path

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
HW = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HW / "scripts"))
sys.path.insert(0, str(HW / "cut-parts/carbonation/endcaps-circular"))
from _cadq_export import export_pdf
from endcap_circular_drawing import (
    line, text, arrow, leader, circular_leader, center, horizontal_dimension,
    path_from_points, hatch, cutting_plane_ends, VISIBLE, CENTER_DASH,
)
from _water_inlet_jet import JET_CAP_D, JET_CAP_T, JET_PASSAGE_D

PDF_PATH = HERE / "water-inlet-jet-cap-drawing.pdf"
SHEET = (11 * 72, 8.5 * 72)
SCALE = 5 * 72 / 25.4
OD_TOL = 0.05
THICKNESS_TOL = 0.20
BORE_PLUS = 0.050
BORE_MINUS = 0.010
RADIAL_OFFSET_MAX = 0.10
AXIS_ANGLE_MAX = 1.0
FACE_GAP_MAX = 0.05
THICKNESS_VARIATION_MAX = 0.05
HOLE_EDGE_BREAK_MAX = 0.05
REVISION = "A"
CX, CY = 230, 420

REVIEW_REGIONS = [
    ("face-and-hole", 126, 337, 613, 569),
    ("od-and-section-markers", 126, 299, 338, 469),
    ("section-and-face-labels", 45, 183, 455, 337),
    ("manufacturing-notes", 427, 175, 746, 471),
    ("units-and-finished-state", 35, 27, 199, 146),
    ("title-block", 198, 27, 765, 146),
]


def face_view(c):
    r = JET_CAP_D * SCALE / 2
    bore = JET_PASSAGE_D * SCALE / 2
    text(c, CX, 555, "JET EXIT FACE VIEW", 12, bold=True, align="center")
    text(c, CX, 538, "SCALE 5:1", 9, align="center")
    c.setLineWidth(VISIBLE)
    c.circle(CX, CY, r, stroke=1, fill=0)
    c.circle(CX, CY, bore, stroke=1, fill=0)
    center(c, CX, CY, r + 14)
    cutting_plane_ends(c, CX - r - 24, CX + r + 24, CY, "A")
    circular_leader(c, (CX, CY), bore, (350, 515), (370, 515),
                    [f"Ø{JET_PASSAGE_D:.4f} +{BORE_PLUS:.3f}/-{BORE_MINUS:.3f} THRU",
                     "(1/16 IN DRILL)", "POSITION / ALIGNMENT: SEE NOTE 3"], 9.5)
    # The OD witnesses descend from the real circular silhouette. The bore
    # callout stays above their origins and clear of the section arrows.
    horizontal_dimension(c, CX - r, CX + r, CY, 315,
                         f"Ø{JET_CAP_D:.2f} ±{OD_TOL:.2f}", 11)


def section_view(c):
    r = JET_CAP_D * SCALE / 2
    bore = JET_PASSAGE_D * SCALE / 2
    bottom = 250
    top = bottom + JET_CAP_T * SCALE
    left, right = CX - r, CX + r
    for a, b in ((left, CX - bore), (CX + bore, right)):
        p = path_from_points(c, [(a, bottom), (b, bottom), (b, top), (a, top)])
        hatch(c, p, (a, bottom, b, top), spacing=6)
        c.setLineWidth(VISIBLE)
        c.drawPath(p, stroke=1, fill=0)
    line(c, CX, bottom - 12, CX, top + 12, dash=CENTER_DASH)
    dim_x = 348
    for y in (bottom, top):
        line(c, right + 4, y, dim_x + 5, y)
    line(c, dim_x, bottom, dim_x, top)
    arrow(c, (dim_x, bottom), (dim_x, top))
    arrow(c, (dim_x, top), (dim_x, bottom))
    text(c, dim_x + 9, (bottom + top) / 2 - 3,
         f"{JET_CAP_T:.2f} ±{THICKNESS_TOL:.2f}", 10)
    leader(c, (190, top), (150, 305), (130, 305), ["JET EXIT FACE"], 8.5)
    leader(c, (270, bottom), (316, 215), (339, 215),
           ["ELBOW SEATING FACE"], 8.5)
    text(c, CX, 220, "SECTION A-A", 11, bold=True, align="center")
    text(c, CX, 204, "THROUGH AXIS - SCALE 5:1", 8.5, align="center")


def manufacture_notes(c):
    x, y, width, size, leading = 435, 440, 300, 8.7, 11.5
    text(c, x, 460, "MANUFACTURE AND INSPECTION", 10, bold=True)
    paragraphs = [
        "1. MATERIAL: 316 STAINLESS ROUND ROD. SELECT STOCK MEETING THE OD LIMITS. DIMENSIONS APPLY AFTER FACE FINISHING AND DEBURRING.",
        "2. DRILL WHILE ATTACHED TO A 50-60 mm HANDLING BLANK. EXTEND THE FULL-DIAMETER BORE BEYOND THE FINAL CUT FACE; SAW THE SLICE AND FINISH TO THICKNESS.",
        f"3. CENTER THE HOLE AT BOTH FACES WITHIN {RADIAL_OFFSET_MAX:.2f} RADIAL OF THE OD AXIS. HOLE AXIS NORMAL TO ELBOW SEATING FACE WITHIN {AXIS_ANGLE_MAX:g}°.",
        f"4. THICKNESS VARIATION ACROSS CAP: {THICKNESS_VARIATION_MAX:.2f} MAX. ELBOW SEATING FACE: {FACE_GAP_MAX:.2f} MAX GAP ON A FLAT INSPECTION SURFACE, UNDER OWN WEIGHT.",
        f"5. REMOVE BURRS FROM BOTH HOLE ENDS; EDGE BREAK {HOLE_EDGE_BREAK_MAX:.2f} MAX. MAINTAIN THE CYLINDRICAL PASSAGE. OD CORNERS: BURR REMOVAL ONLY; PRESERVE THE SQUARE WELD RIM.",
        "6. REMOVE ALL CUTTING FLUID AND LOOSE METAL. CAP-TO-ELBOW WELD, INSTALLED FIT AND POST-WELD INSPECTION: ASSEMBLY/WATER-INLET-JET.MD.",
    ]
    for paragraph in paragraphs:
        row = ""
        for word in paragraph.split():
            trial = (row + " " + word).strip()
            if row and stringWidth(trial, "Helvetica", size) > width:
                text(c, x, y, row, size)
                y -= leading
                row = word
            else:
                row = trial
        text(c, x, y, row, size)
        y -= leading + 5
    return y


def title_block(c):
    left, right, bottom, top = 203, 765, 27, 143
    c.setLineWidth(0.7)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    line(c, left, 98, right, 98)
    line(c, left, 65, right, 65)
    line(c, right - 135, 98, right - 135, top)
    text(c, left + 10, 126, "HOME SODA MACHINE", 8)
    text(c, left + 10, 108, "WATER-INLET JET CAP", 11.5, bold=True)
    text(c, right - 67.5, 125, "FINISHED PART", 9, bold=True, align="center")
    text(c, right - 67.5, 110, "CAP BEFORE WELD", 9, align="center")
    for col in (left + 235, left + 370):
        line(c, col, 65, col, 98)
    for x, label, value in ((left + 10, "MATERIAL", "316 STAINLESS STEEL"),
                            (left + 245, "UNITS", "MILLIMETERS"),
                            (left + 380, "QUANTITY", "1 PER CARBONATOR")):
        text(c, x, 87, label, 7)
        text(c, x, 73, value, 8.5, bold=True)
    fields = ((left, left + 175, "DRAWING", "JET-CAP-01"),
              (left + 175, left + 220, "REV", REVISION),
              (left + 220, left + 335, "DATE", "2026-10-26"),
              (left + 335, left + 452, "SCALE", "AS SHOWN"),
              (left + 452, right, "SHEET", "1 OF 1"))
    for i, (a, b, label, value) in enumerate(fields):
        if i:
            line(c, a, bottom, a, 65)
        text(c, a + 9, 53, label, 7)
        text(c, a + 9, 37, value, 9, bold=True)
    text(c, 47, 127, "HSM-000011", 9, bold=True)
    text(c, 47, 110, "mm DIMENSIONS GOVERN.", 8)
    text(c, 47, 80, "FINISHED, DEBURRED CAP.", 8)
    text(c, 47, 63, "DO NOT SCALE.", 8, bold=True)
    text(c, 47, 49, "ANSI A / 11 x 8.5 IN", 7.5)
    text(c, 47, 36, "PRINT AT 100% FOR SCALE.", 7.5)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Carbonator water-inlet jet cap - engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("JET-CAP-01 Rev A: finished 316 cap, 1/16-inch through passage and pre-weld finish")
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.rect(27, 27, SHEET[0] - 54, SHEET[1] - 54, stroke=1, fill=0)
    face_view(c)
    section_view(c)
    manufacture_notes(c)
    title_block(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
