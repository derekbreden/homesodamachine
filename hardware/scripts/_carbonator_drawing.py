"""Source parameters and drafting primitives for the carbonator drawing family.

Drawing generation only; no CAD, cut files, or qualification criteria are changed.
Run the drawing entry points with tools/cad-venv/bin/python.
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for folder in ("hardware/cold-core-layout", "hardware/assembly",
               "hardware/cut-parts/carbonation/endcaps-circular",
               "hardware/cut-parts/carbonation/float-rod"):
    sys.path.insert(0, str(ROOT / folder))

import _carbonator as carb
import float_rod_dimensions as rod_spec
import endcap_circular_dxf as cap
import _float_interface as float_interface
from endcap_circular_drawing import (
    line, text, arrow, leader, circular_leader, center, hatch,
    path_from_points, horizontal_dimension, cutting_plane_ends,
    VISIBLE, THIN, CENTER_DASH,
)
from _cadq_export import export_pdf

IN = 72.0
MM = 25.4
OD = carb.TUBE_OD / MM
WALL = carb.TUBE_WALL / MM
ID = carb.TUBE_ID / MM
LENGTH = carb.carbonator_height / MM
CAP_D = carb.PLATE_D / MM
CAP_T = carb.PLATE_T / MM
RECESS = carb.PLATE_RECESS / MM
ROD_D = carb.ROD_D / MM
ROD_X = carb.ROD_X / MM
FLOAT_D = float_interface.diameter / MM
FLOAT_H = float_interface.height / MM
REG_D = cap.register_drill_diameter
REG_DEPTH = cap.register_depth
ROD_LENGTH = rod_spec.finished_length
ROD_LENGTH_TOL = rod_spec.length_tolerance
ROD_D_TOL = rod_spec.diameter_tolerance
INSIDE_SPAN = rod_spec.inside_face_span
INSIDE_SPAN_TOL = rod_spec.inside_face_span_tolerance
FLOOR = RECESS + CAP_T
CEILING = LENGTH - RECESS - CAP_T
DRILL_HALF_ANGLE = math.radians(135 / 2)

# A flat rod end contacts the cone above its tip. The finished cut length is
# controlled by FR-CARB-01; its upper end is located from the seated lower end.
FLAT_SEAT_DEPTH = REG_DEPTH - ROD_D / (2 * math.tan(DRILL_HALF_ANGLE))
ROD_BOTTOM = FLOOR - FLAT_SEAT_DEPTH
ROD_TOP = ROD_BOTTOM + ROD_LENGTH


def frame(c, sheet):
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.rect(27, 27, sheet[0] - 54, sheet[1] - 54, stroke=1, fill=0)


def title_block(c, sheet, title, drawing, material, quantity, part_id,
                revision="A", status=("PROTOTYPE", "FOR REVIEW")):
    """Common family title block, independently sized for A and B sheets."""
    right, bottom, top = sheet[0] - 27, 27, 143
    left = right - 562
    c.setLineWidth(0.7)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    line(c, left, 98, right, 98)
    line(c, left, 65, right, 65)
    line(c, right - 135, 98, right - 135, top)
    text(c, left + 10, 126, "HOME SODA MACHINE", 8)
    text(c, left + 10, 108, title, 11.5, bold=True)
    text(c, right - 67.5, 125, status[0], 9, bold=True, align="center")
    text(c, right - 67.5, 110, status[1], 9, align="center")
    for x in (left + 235, left + 370):
        line(c, x, 65, x, 98)
    for x, label, value in ((left + 10, "MATERIAL", material),
                            (left + 245, "UNITS", "INCHES"),
                            (left + 380, "QUANTITY", quantity)):
        text(c, x, 87, label, 7)
        text(c, x, 73, value, 8.5, bold=True)
    fields = ((left, left + 175, "DRAWING", drawing),
              (left + 175, left + 220, "REV", revision),
              (left + 220, left + 335, "DATE", "2026-10-26"),
              (left + 335, left + 452, "SCALE", "AS SHOWN"),
              (left + 452, right, "SHEET", "1 OF 1"))
    for i, (a, b, label, value) in enumerate(fields):
        if i:
            line(c, a, bottom, a, 65)
        text(c, a + 9, 53, label, 7)
        text(c, a + 9, 37, value, 9, bold=True)
    text(c, 47, 126, part_id, 9, bold=True)
    text(c, 47, 110, "DIMENSIONS GOVERN.", 8)
    text(c, 47, 96, "DO NOT SCALE.", 8)
    text(c, 47, 66, "PRINT AT 100%", 8)
    text(c, 47, 52, "FOR STATED SCALES.", 8)
    text(c, 47, 36, "REF = REFERENCE", 8)


def vdim(c, x, y1, y2, witness1, witness2, label, outside=False,
         align="right", size=10):
    """Independent witness origins keep face dimensions tied to real edges."""
    for y, origin in ((y1, witness1), (y2, witness2)):
        direction = 1 if x > origin else -1
        line(c, origin + 4 * direction, y, x + 5 * direction, y)
    if outside:
        line(c, x, y1 - 13, x, y2 + 13)
        arrow(c, (x, y1), (x, y1 - 13))
        arrow(c, (x, y2), (x, y2 + 13))
    else:
        line(c, x, y1, x, y2)
        arrow(c, (x, y1), (x, y2))
        arrow(c, (x, y2), (x, y1))
    text(c, x + (9 if align == "left" else -9), (y1 + y2) / 2 - 3,
         label, size, align=align)


def balloon(c, number, at, tip):
    radius = 10
    dx, dy = tip[0] - at[0], tip[1] - at[1]
    distance = math.hypot(dx, dy)
    start = (at[0] + radius * dx / distance, at[1] + radius * dy / distance)
    line(c, *start, *tip)
    arrow(c, tip, start)
    c.setLineWidth(0.6)
    c.circle(*at, radius, stroke=1, fill=0)
    text(c, at[0], at[1] - 3, str(number), 9, bold=True, align="center")


def section_material(c, points, spacing=6, reverse=False):
    path = path_from_points(c, points)
    xs, ys = zip(*points)
    if reverse:
        c.saveState()
        c.translate(0, min(ys) + max(ys))
        c.scale(1, -1)
        mirrored = path_from_points(c, [(x, min(ys) + max(ys) - y) for x, y in points])
        hatch(c, mirrored, (min(xs), min(ys), max(xs), max(ys)), spacing=spacing)
        c.restoreState()
    else:
        hatch(c, path, (min(xs), min(ys), max(xs), max(ys)), spacing=spacing)
    c.setLineWidth(VISIBLE)
    c.drawPath(path, stroke=1, fill=0)


def register_opening(c, x, inside, scale, direction):
    """Erase section fill inside a blind 135-degree drilled register."""
    radius = REG_D * scale / 2
    tip = inside + direction * REG_DEPTH * scale
    shoulder = tip - direction * radius / math.tan(DRILL_HALF_ANGLE)
    points = [(x - radius, inside), (x - radius, shoulder), (x, tip),
              (x + radius, shoulder), (x + radius, inside)]
    opening = path_from_points(c, points)
    c.setFillColorRGB(1, 1, 1)
    c.drawPath(opening, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    # The register mouth is open, so the inside-face line does not bridge it.
    c.setStrokeColorRGB(1, 1, 1)
    line(c, x - radius + 0.2, inside, x + radius - 0.2, inside, 1.1)
    c.setStrokeColorRGB(0, 0, 0)
    for a, b in zip(points, points[1:]):
        line(c, *a, *b, VISIBLE)


def wrap_lines(c, x, y, paragraphs, width, size=9, leading=12, gap=5):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    for paragraph in paragraphs:
        words = paragraph.split()
        row = ""
        while words:
            word = words.pop(0)
            candidate = (row + " " + word).strip()
            if row and stringWidth(candidate, "Helvetica", size) > width:
                text(c, x, y, row, size)
                y -= leading
                row = word
            else:
                row = candidate
        if row:
            text(c, x, y, row, size)
            y -= leading
        y -= gap
    return y
