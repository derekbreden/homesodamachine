"""Millimetre drawing-sheet helpers for formed and cut parts."""

import sys
from pathlib import Path

HW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HW / "cut-parts/carbonation/endcaps-circular"))
from endcap_circular_drawing import (
    line, text, arrow, leader, circular_leader, center, path_from_points,
    horizontal_dimension, hatch, VISIBLE, THIN, CENTER_DASH,
)
from _cadq_export import export_pdf
from reportlab.pdfbase.pdfmetrics import stringWidth

MM = 72 / 25.4


def frame(c, sheet):
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.rect(27, 27, sheet[0] - 54, sheet[1] - 54, stroke=1, fill=0)


def title_block(c, sheet, title, drawing, material, quantity, part_id, status,
                revision="A", sheet_label="1 OF 1"):
    right = sheet[0] - 27
    left = right - 562
    c.setLineWidth(0.7)
    c.rect(left, 27, 562, 116, stroke=1, fill=0)
    for y in (65, 98):
        line(c, left, y, right, y)
    line(c, right - 135, 98, right - 135, 143)
    text(c, left + 10, 126, "HOME SODA MACHINE", 8)
    text(c, left + 10, 108, title, 11, bold=True)
    text(c, right - 67.5, 125, status[0], 8.5, bold=True, align="center")
    text(c, right - 67.5, 110, status[1], 8.5, align="center")
    for x in (left + 235, left + 370):
        line(c, x, 65, x, 98)
    for x, label, value in ((left + 10, "MATERIAL", material),
                            (left + 245, "UNITS", "MILLIMETERS"),
                            (left + 380, "QUANTITY", quantity)):
        text(c, x, 87, label, 7)
        text(c, x, 73, value, 8.5, bold=True)
    fields = ((left, left + 175, "DRAWING", drawing),
              (left + 175, left + 220, "REV", revision),
              (left + 220, left + 335, "DATE", "2026-10-27"),
              (left + 335, left + 452, "SCALE", "AS SHOWN"),
              (left + 452, right, "SHEET", sheet_label))
    for i, (a, b, label, value) in enumerate(fields):
        if i:
            line(c, a, 27, a, 65)
        text(c, a + 9, 53, label, 7)
        text(c, a + 9, 37, value, 9, bold=True)
    text(c, 47, 126, part_id, 9, bold=True)
    text(c, 47, 109, "mm DIMENSIONS GOVERN.", 8)
    text(c, 47, 94, "DO NOT SCALE.", 8)
    text(c, 47, 73, "REF = REFERENCE.", 8)
    text(c, 47, 48, "PRINT AT 100%", 8)
    text(c, 47, 36, "FOR STATED SCALES.", 8)


def paragraphs(c, x, y, items, width, size=9, leading=12, gap=6):
    for item in items:
        row = ""
        for word in item.split():
            trial = (row + " " + word).strip()
            if row and stringWidth(trial, "Helvetica", size) > width:
                text(c, x, y, row, size)
                y -= leading
                row = word
            else:
                row = trial
        text(c, x, y, row, size)
        y -= leading + gap
    return y


def polyline(c, points, width=VISIBLE, dash=None):
    c.saveState()
    c.setLineWidth(width)
    c.setDash(dash or [])
    p = c.beginPath()
    p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def axes(c, x, y, horizontal, vertical):
    for target, label, tx, ty in (((x + 30, y), horizontal, x + 35, y - 3),
                                  ((x, y + 30), vertical, x - 5, y + 38)):
        line(c, x, y, *target)
        arrow(c, target, (x, y))
        text(c, tx, ty, label, 8)
