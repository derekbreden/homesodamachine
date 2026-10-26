"""Finished carbonator guide rod: fixed cut length, tolerances and end finish.

The controlled cap spacing and conical-register tolerance basis are stated on
the sheet. All rod dimensions and fit assumptions come from float_rod_dimensions.
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
    length = ROD_LENGTH * IN
    diameter = ROD_D * IN
    text(c, x + length / 2, 544, "SIDE VIEW", 12, bold=True, align="center")
    text(c, x + length / 2, 527, "SCALE 1:1", 8.5, align="center")
    c.setLineWidth(VISIBLE)
    c.rect(x, y, length, diameter, stroke=1, fill=0)
    line(c, x - 14, y + diameter / 2, x + length + 14, y + diameter / 2,
         dash=CENTER_DASH)
    horizontal_dimension(c, x, x + length, y + diameter, 485,
                         f"{ROD_LENGTH:.3f} ±{ROD_LENGTH_TOL:.3f}", 12)
    text(c, x + length / 2, 468, f"{ROD_LENGTH * MM:.2f} ±{ROD_LENGTH_TOL * MM:.2f} mm REF", 9, align="center")
    leader(c, (x, y + diameter / 2), (x + 36, 390), (x + 60, 390),
           ["SQUARE CUT; DEBURR BOTH ENDS", "KEEP GUIDE SURFACE FREE OF BURRS"], 9)
    center_x, center_y, end_scale = 620, y + diameter / 2, 4 * IN
    radius = ROD_D * end_scale / 2
    text(c, center_x, 544, "END VIEW", 12, bold=True, align="center")
    text(c, center_x, 527, "SCALE 4:1", 8.5, align="center")
    c.setLineWidth(VISIBLE)
    c.circle(center_x, center_y, radius, stroke=1, fill=0)
    center(c, center_x, center_y, radius + 10)
    circular_leader(c, (center_x, center_y), radius, (646, 490), (662, 490),
                    [f"Ø{ROD_D:.3f}", f"±{ROD_D_TOL:.3f}"], 10)


def requirements(c):
    text(c, 48, 343, "FINISHED PART REQUIREMENTS", 10, bold=True)
    paragraphs = [
        "1. Material: 316 stainless round rod. Stock: Tandefio B0CY4DWJFQ, nominal 1/8-inch x 12-inch sticks. Select stock meeting the stated diameter tolerance.",
        f"2. Length is the FINISHED overall length after cutting and deburring. Cut both ends flat and square to the rod axis within {rod_spec.end_squareness_degrees:g}°. Remove burrs; edge break {rod_spec.edge_break_maximum:.3f} MAX. Keep the sliding surface free of burrs, chips and cutting fluid.",
        f"3. Assembly interface: cap inside faces {INSIDE_SPAN:.3f} ±{INSIDE_SPAN_TOL:.3f} apart AT THE ROD AXIS; registers coaxial, per CV-WLD-01. Registers per END-CAP-01: Ø9/64, {REG_DEPTH:.3f} ±{rod_spec.register_depth_tolerance:.3f} TO DRILL TIP; point {rod_spec.register_point_degrees:g}° ±{rod_spec.register_point_tolerance_degrees:g}°. Flat rod ends seat above the drill tip.",
        "4. Seat the rod in the bottom register and tack to the bottom cap. Before top closure, verify top-register engagement and full cap seating; verify free float travel. Maintain the specified cap spacing; rod length is controlled by this drawing.",
        "5. Quantity: one per carbonator. Reservoir rods are separate parts. Rod tack and vessel assembly follow the pressure-vessel procedure, steps 2-5.",
    ]
    return wrap_lines(c, 48, 324, paragraphs, 691, size=9, leading=12, gap=6)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Carbonator float guide rod - engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("FR-CARB-01 Rev B: finished 316 rod, fixed cut length and toleranced assembly interface")
    frame(c, SHEET)
    views(c)
    requirements(c)
    text(c, 48, 160, "ALL DIMENSIONS APPLY TO THE FINISHED, DEBURRED PART. INCH DIMENSIONS GOVERN.", 8.5, bold=True)
    title_block(c, SHEET, "CARBONATOR FLOAT GUIDE ROD", "FR-CARB-01",
                "316 STAINLESS STEEL", "1 PER CARBONATOR", "HSM-000336",
                revision="B", status=("FINISHED PART", "DESIGN DEFINITION"))
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
