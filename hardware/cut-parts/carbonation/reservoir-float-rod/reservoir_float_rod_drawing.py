"""Finished reservoir guide rod; common part for channels A and B.

Nominal dimensions are imported from the reservoir's seats. The limits below
are chosen finished-part requirements, not measured stock/print capability.
"""

import sys
from pathlib import Path
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == "hardware")
for p in (HW / "scripts", HW / "printed-parts/cold-core/reservoir"):
    sys.path.insert(0, str(p))
import reservoir as source
from _fabrication_drawing import *

PDF_PATH = HERE / "reservoir-float-rod-drawing.pdf"
SHEET = (792, 612)
LENGTH = source.reservoir_rod_len
DIAMETER = source.rod_diameter
LENGTH_MINUS = 0.10
DIAMETER_TOL = 0.05
STRAIGHTNESS = 0.10
EDGE_BREAK = 0.08
END_ANGLE = 0.5
ENDPLAY_MIN, ENDPLAY_MAX = 0.05, 0.50
MATERIAL_ID = "HSM-000339"
REVIEW_REGIONS = [
    ("side-view", 40, 375, 750, 565),
    ("end-view", 545, 230, 752, 370),
    ("requirements", 40, 155, 548, 370),
    ("title-block", 35, 27, 765, 146),
]


def views(c):
    x, y, s = 72, 447, MM
    length, diameter = LENGTH * s, DIAMETER * s
    text(c, x + length / 2, 552, "FINISHED ROD - SIDE VIEW", 12, bold=True, align="center")
    text(c, x + length / 2, 535, "SCALE 1:1", 9, align="center")
    c.setLineWidth(VISIBLE)
    c.rect(x, y, length, diameter, stroke=1, fill=0)
    line(c, x - 14, y + diameter / 2, x + length + 14, y + diameter / 2,
         dash=CENTER_DASH)
    horizontal_dimension(c, x, x + length, y + diameter, 500,
                         f"{LENGTH:.2f} +0.00 / -{LENGTH_MINUS:.2f}", 12)
    leader(c, (x + length, y + diameter / 2), (605, 403), (581, 403),
           ["BOTH ENDS FLAT AND SQUARE", "DEBURR; 0.08 MAX EDGE BREAK"], 9)
    x, y, s = 635, 290, 4 * MM
    radius = DIAMETER * s / 2
    text(c, x, 353, "END VIEW", 11, bold=True, align="center")
    text(c, x, 337, "SCALE 4:1", 9, align="center")
    c.setLineWidth(VISIBLE)
    c.circle(x, y, radius, stroke=1, fill=0)
    center(c, x, y, radius + 9)
    circular_leader(c, (x, y), radius, (674, 319), (690, 319),
                    [f"Ø{DIAMETER:.3f}", f"±{DIAMETER_TOL:.2f}"], 10)
    text(c, x, 244, "SAME PART FOR A AND B", 8.5, bold=True, align="center")


def requirements(c):
    text(c, 48, 353, "FINISHED PART AND ASSEMBLY REQUIREMENTS", 10, bold=True)
    seat_span = LENGTH + source.reservoir_rod_clearance
    items = [
        "1. Material: 316 stainless round rod. Use stock meeting the diameter limits; stock must be longer than the finished cut. Quantity: two identical rods per cold core, one per flavor reservoir.",
        f"2. Length applies after cutting and deburring. Ends flat; each square to the axis within {END_ANGLE:g}°. Edge break {EDGE_BREAK:.2f} MAX. Sliding surface free of raised burrs, sharp ridges and embedded debris; remove cutting fluid.",
        f"3. Centerline departure from a straight line joining the end centers: {STRAIGHTNESS:.2f} MAX over the full length. Verify free travel through the actual float's complete stroke.",
        f"4. Reservoir interface: Ø{source.rod_bore:.3f} nominal seat bores; lower seat to upper seat {seat_span:.2f} REF. At nominal seats, this rod's length limits leave 0.15-0.25 REF axial clearance.",
        f"5. Seat lower end in the body boss and capture upper end in the cap boss; no weld. With the gasket and cap fully seated, verify {ENDPLAY_MIN:.2f}-{ENDPLAY_MAX:.2f} total axial endplay. Correct out-of-limit seats; retain the specified rod length. The rod must not hold the cap off its gasket.",
    ]
    return paragraphs(c, 48, 333, items, 475, size=8.7, leading=11.5, gap=6)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Reservoir float guide rod - engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("FR-RES-01 Rev A: fixed finished length, end finish and reservoir-seat acceptance")
    frame(c, SHEET)
    views(c)
    requirements(c)
    title_block(c, SHEET, "RESERVOIR FLOAT GUIDE ROD", "FR-RES-01", "316 STAINLESS STEEL",
                "2 PER COLD CORE", MATERIAL_ID, ("FINISHED PART", "DESIGN DEFINITION"))
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
