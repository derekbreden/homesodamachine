"""Carbonator float guide rod: cut stock, square/deburred ends, match-fit length.

The procedure's calculated starting blank is not a released finished length.
This drawing keeps the finished-length dimension functional and assigns the cut
carbonator variant its own material identity, separate from reservoir rod stock.
"""

import sys
from pathlib import Path

from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HW / "scripts"))
from _carbonator_drawing import *

PDF_PATH = HERE / "carbonator-float-rod-drawing.pdf"
SHEET = (11 * IN, 8.5 * IN)
REVIEW_REGIONS = [
    ("side-view", 40, 365, 493, 555),
    ("end-view", 508, 365, 751, 555),
    ("notes-fit", 40, 169, 752, 360),
    ("title-status", 35, 27, 765, 179),
]


def views(c):
    x, y = 72, 430
    length = (ROD_TOP - ROD_BOTTOM) * IN
    diameter = ROD_D * IN
    text(c, x + length / 2, 544, "SIDE VIEW", 12, bold=True, align="center")
    text(c, x + length / 2, 527, "FINISHED ROD - NOT TO SCALE", 8.5, align="center")
    c.setLineWidth(VISIBLE)
    c.rect(x, y, length, diameter, stroke=1, fill=0)
    line(c, x - 14, y + diameter / 2, x + length + 14, y + diameter / 2,
         dash=CENTER_DASH)
    horizontal_dimension(c, x, x + length, y + diameter, 485,
                         "L - MATCH FIT (NOTE 2)", 11)
    leader(c, (x, y + diameter / 2), (x + 36, 390), (x + 60, 390),
           ["SQUARE CUT; DEBURR BOTH ENDS", "KEEP GUIDE SURFACE FREE OF BURRS"], 9)
    center_x, center_y, end_scale = 620, y + diameter / 2, 4 * IN
    radius = ROD_D * end_scale / 2
    text(c, center_x, 544, "END VIEW", 12, bold=True, align="center")
    text(c, center_x, 527, "SCALE 4:1", 8.5, align="center")
    c.setLineWidth(VISIBLE)
    c.circle(center_x, center_y, radius, stroke=1, fill=0)
    center(c, center_x, center_y, radius + 10)
    circular_leader(c, (center_x, center_y), radius, (659, 490), (679, 490),
                    ["Ø1/8", "STOCK"], 10)


def requirements(c):
    text(c, 48, 343, "PART AND FIT REQUIREMENTS", 10, bold=True)
    paragraphs = [
        "1. Material: 316 stainless round rod, nominal Ø1/8. Purchased stock: Tandefio B0CY4DWJFQ, 12-inch sticks. Cut square and remove burrs from both ends. Remove chips and cutting fluid.",
        f"2. L is the FINISHED, MATCH-FIT length for the actual bottom/top end-cap register pair in CV-WLD-01. Start with a {BLANK_LENGTH:.3f} in blank ({BLANK_LENGTH_MM:.2f} mm calculated); trim to fit before tacking. The starting blank is not a finished-length acceptance dimension.",
        "3. With the rod seated in the bottom register, its top must engage the top register while BOTH cap outside faces reach their 0.250-inch recesses. The rod must not bottom in the top register and hold that cap proud. Verify engagement and full seating with the actual caps and tube.",
        f"4. Registers are drilled {REG_DEPTH:.3f} deep TO THE DRILL TIP with a 135° point (END-CAP-01). A flat rod end seats above that tip. Verify finished L with the actual register pair.",
        "5. Rod tack and final free-sliding check with the actual float are assembly operations; see the pressure-vessel procedure, steps 2-5. This drawing applies to the CARBONATOR rod only.",
    ]
    return wrap_lines(c, 48, 324, paragraphs, 691, size=9, leading=12, gap=6)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Carbonator float guide rod - engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("FR-CARB-01 Rev A: 1/8-inch 316 rod, starting blank and functional match-fit length")
    frame(c, SHEET)
    views(c)
    requirements(c)
    text(c, 48, 160, "FINAL LENGTH IS CONTROLLED BY THE MATCH-FIT REQUIREMENTS ABOVE.", 8.5, bold=True)
    title_block(c, SHEET, "CARBONATOR FLOAT GUIDE ROD", "FR-CARB-01",
                "316 STAINLESS STEEL", "1 PER CARBONATOR", "HSM-000336")
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
