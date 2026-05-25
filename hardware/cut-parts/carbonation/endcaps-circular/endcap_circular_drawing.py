"""
Engineering drawing (PDF) for the circular 2-hole carbonator end cap.

Xometry requires a drawing alongside the DXF that calls out thread type and
depth:

    "Drawing required to avoid delays. Attach a drawing that calls out
     thread type and depth. If no depth is specified, we will drill to
     the depth of the CAD, and thread per best shop practice with
     standard tooling."

This script produces `endcap-circular-2hole-drawing.pdf` — an ANSI A
landscape sheet with a 1:1 plan view of the disc, dimensions, a tap
callout (1/4-18 NPT THRU), general notes, and a title block.

Geometry mirrors `endcap_circular_dxf.py` in this folder — single source of truth
for the cut geometry is still the DXF; this PDF only annotates.

Run:
    tools/cad-venv/bin/python hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_drawing.py
"""

import math
import sys
from datetime import date
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_py_comments

# Part geometry in inches — mirrors endcap_circular_dxf.py.

# [4.86 in](DISC_D) disc OD — tube ID 4.870 in minus 0.010 in slip-fit.
disc_diameter = 4.860
# [2.43 in](DISC_R) disc radius = disc_diameter / 2.
disc_radius = disc_diameter / 2
# [0.25 in](DISC_THK) 1/4" 316 SS plate thickness.
disc_thickness = 0.250
# [0.438 in](HOLE_D) 7/16" tap drill for 1/4"-18 NPT.
hole_diameter = 0.438
# [0.219 in](HOLE_R) hole radius = hole_diameter / 2.
hole_radius = hole_diameter / 2
# [1.5 in](HOLE_SPACING) center-to-center spacing along X (matches the
# CNC dome-cap variants preserved at git tag archive-plan-b).
hole_spacing = 1.500
# [0.75 in](HOLE_OFFSET) each hole's |X| offset from disc center = hole_spacing / 2.
hole_offset = hole_spacing / 2
hole_positions = [(-hole_offset, 0.0), (+hole_offset, 0.0)]

# Sheet layout in inches (ANSI A landscape).
sheet_width = 11.0
sheet_height = 8.5
sheet_margin = 0.5

# Title-block box in the bottom-right corner, inside the margin.
title_block_width = 4.0
title_block_height = 2.0
title_block_x = sheet_width - sheet_margin - title_block_width
title_block_y = sheet_margin

# Part view occupies the left ~2/3 of the sheet, vertically centered.
view_center_x = 3.3
view_center_y = sheet_height / 2

# Line weights, given in inches and converted to PDF points (1 in = 72 pt).
points_per_inch = 72
border_line_width = 0.020 * points_per_inch
part_line_width = 0.015 * points_per_inch
thin_line_width = 0.008 * points_per_inch

# ASME dash-dot pattern for centerlines, in points.
centerline_dash = [6, 2, 1, 2]

out_dir = Path(__file__).resolve().parent
pdf_path = out_dir / "endcap-circular-2hole-drawing.pdf"


# ── Helpers ──────────────────────────────────────────────────────────

def draw_border(c: canvas.Canvas) -> None:
    c.setLineWidth(border_line_width)
    c.setDash()
    c.rect(
        sheet_margin * inch,
        sheet_margin * inch,
        (sheet_width - 2 * sheet_margin) * inch,
        (sheet_height - 2 * sheet_margin) * inch,
        stroke=1,
        fill=0,
    )


def draw_centermark(c: canvas.Canvas, cx: float, cy: float, size: float = 0.12) -> None:
    """Short crosshair at a circle's center."""
    c.setLineWidth(thin_line_width)
    c.setDash()
    c.line((cx - size) * inch, cy * inch, (cx + size) * inch, cy * inch)
    c.line(cx * inch, (cy - size) * inch, cx * inch, (cy + size) * inch)


def draw_centerline(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    c.setLineWidth(thin_line_width)
    c.setDash(centerline_dash, 0)
    c.line(x1 * inch, y1 * inch, x2 * inch, y2 * inch)
    c.setDash()


def _arrow(c: canvas.Canvas, x: float, y: float, dx: float, dy: float, size: float = 0.08) -> None:
    """Tiny filled arrowhead with its tip at (x, y) pointing in direction (dx, dy)."""
    length = math.hypot(dx, dy)
    if length == 0:
        return
    unit_x, unit_y = dx / length, dy / length
    perp_x, perp_y = -unit_y, unit_x
    half_base = size * 0.35

    tip = (x, y)
    base_x = x - unit_x * size
    base_y = y - unit_y * size
    left = (base_x + perp_x * half_base, base_y + perp_y * half_base)
    right = (base_x - perp_x * half_base, base_y - perp_y * half_base)

    p = c.beginPath()
    p.moveTo(tip[0] * inch, tip[1] * inch)
    p.lineTo(left[0] * inch, left[1] * inch)
    p.lineTo(right[0] * inch, right[1] * inch)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def draw_horizontal_dimension(
    c: canvas.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    offset: float,
    text: str,
) -> None:
    """Horizontal linear dimension between (x1, y1) and (x2, y2) placed
    at y = max(y1, y2) + offset (or y1 + offset when y1 == y2).
    Draws extension lines from the points up to the dim line, the dim
    line itself, inward-pointing arrows, and the centered text label.
    """
    c.setLineWidth(thin_line_width)
    c.setDash()
    c.setFillColorRGB(0, 0, 0)
    c.setStrokeColorRGB(0, 0, 0)

    dim_y = y1 + offset if abs(y1 - y2) < 1e-9 else max(y1, y2) + offset
    extension_overshoot = 0.08 if offset > 0 else -0.08

    # Extension lines from each endpoint up past the dim line.
    c.line(x1 * inch, y1 * inch, x1 * inch, (dim_y + extension_overshoot) * inch)
    c.line(x2 * inch, y2 * inch, x2 * inch, (dim_y + extension_overshoot) * inch)
    # Dimension line.
    c.line(x1 * inch, dim_y * inch, x2 * inch, dim_y * inch)
    # Arrows point inward.
    _arrow(c, x1, dim_y,  1, 0)
    _arrow(c, x2, dim_y, -1, 0)
    # Centered text just above the dim line.
    c.setFont("Helvetica", 8)
    c.drawCentredString(((x1 + x2) / 2) * inch, (dim_y + 0.05) * inch, text)


def draw_leader(
    c: canvas.Canvas,
    targets,
    text_anchor,
    text_lines,
) -> None:
    """Multileader: arrow tips at each point in `targets` share a common
    shoulder at `text_anchor`, with `text_lines` stacked above it.

    `targets` is a list of (x, y) points.
    `text_anchor` is the (x, y) where the shoulder meets the text.
    """
    c.setLineWidth(thin_line_width)
    c.setDash()
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    text_x, text_y = text_anchor

    # Short horizontal shoulder shared by all leaders, on whichever side
    # of the text anchor the targets sit.
    shoulder_length = 0.35
    target_avg_x = sum(x for x, _ in targets) / len(targets)
    knee_x = text_x - shoulder_length if text_x > target_avg_x else text_x + shoulder_length
    knee_y = text_y

    # Shoulder from text anchor to shared knee.
    c.line(knee_x * inch, knee_y * inch, text_x * inch, text_y * inch)

    # One slanted leader per target, all originating at the shared knee.
    for tx, ty in targets:
        c.line(tx * inch, ty * inch, knee_x * inch, knee_y * inch)
        _arrow(c, tx, ty, tx - knee_x, ty - knee_y, size=0.10)

    # Text block: left-aligned, first line just above the shoulder,
    # subsequent lines stacked below.
    c.setFont("Helvetica", 9)
    anchor_x = (text_x + 0.05) * inch
    line_height = 0.14
    for i, line in enumerate(text_lines):
        c.drawString(anchor_x, (text_y + 0.04 - i * line_height) * inch, line)


def draw_notes(c: canvas.Canvas) -> None:
    """General notes block above the title block."""
    x0 = title_block_x
    y0 = title_block_y + title_block_height + 0.10
    w = title_block_width
    h = 1.35

    c.setLineWidth(thin_line_width)
    c.setDash()
    c.rect(x0 * inch, y0 * inch, w * inch, h * inch, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 9)
    c.drawString((x0 + 0.08) * inch, (y0 + h - 0.20) * inch, "NOTES:")

    notes = [
        "1. REMOVE ALL BURRS AND SHARP EDGES.",
        f"2. TAP BOTH HOLES 1/4-18 NPT, THRU FULL PLATE ({disc_thickness:.3f} IN).",
        "3. NPT THREAD DEPTH: THRU (NO COUNTERBORE, NO SPOT-FACE).",
        "4. BREAK OUTER EDGE 0.010 IN x 45\u00b0.",
        "5. PART IS SYMMETRIC \u2014 NO HANDEDNESS.",
    ]
    c.setFont("Helvetica", 8)
    line_height = 0.17
    for i, note in enumerate(notes):
        c.drawString((x0 + 0.10) * inch, (y0 + h - 0.40 - i * line_height) * inch, note)


def draw_title_block(c: canvas.Canvas) -> None:
    x0 = title_block_x
    y0 = title_block_y
    w = title_block_width
    h = title_block_height

    c.setLineWidth(border_line_width)
    c.setDash()
    c.rect(x0 * inch, y0 * inch, w * inch, h * inch, stroke=1, fill=0)

    rows = [
        ("PART",      "CARBONATOR END CAP, CIRCULAR, 2-HOLE NPT"),
        ("MATERIAL",  "316 STAINLESS STEEL"),
        ("THICKNESS", f"{disc_thickness:.3f} IN (1/4)"),
        ("SCALE",     "1:1"),
        ("UNITS",     "INCHES"),
        ("TOLERANCE", "\u00b10.005 IN LINEAR, \u00b10.5\u00b0 ANGULAR (UNLESS NOTED)"),
        ("DATE",      date.today().isoformat()),
        ("PROJECT",   "SODA FLAVOR INJECTOR \u2014 CARBONATOR VESSEL"),
        ("DRAWN BY",  "derekbreden@gmail.com"),
    ]
    n = len(rows)
    row_height = h / n
    label_width = 1.05

    c.setLineWidth(thin_line_width)
    for i in range(1, n):
        y = y0 + i * row_height
        c.line(x0 * inch, y * inch, (x0 + w) * inch, y * inch)
    # Label/value divider column
    c.line((x0 + label_width) * inch, y0 * inch, (x0 + label_width) * inch, (y0 + h) * inch)

    # Title row gets a slightly larger font — first row (top) is "PART".
    # rows list is top->bottom in reading order; reportlab y grows up, so
    # the topmost row sits at y0 + h - row_height.
    for i, (label, value) in enumerate(rows):
        ry = y0 + h - (i + 1) * row_height

        c.setFont("Helvetica-Bold", 7)
        c.drawString((x0 + 0.06) * inch, (ry + row_height / 2 - 0.04) * inch, label)

        font_size = 10 if label == "PART" else 9
        c.setFont("Helvetica", font_size)
        # Shrink value if too long
        max_value_width = (w - label_width - 0.10) * inch
        text_width = c.stringWidth(value, "Helvetica", font_size)
        while text_width > max_value_width and font_size > 6:
            font_size -= 1
            c.setFont("Helvetica", font_size)
            text_width = c.stringWidth(value, "Helvetica", font_size)
        c.drawString((x0 + label_width + 0.08) * inch, (ry + row_height / 2 - 0.04) * inch, value)


# ── Main view ────────────────────────────────────────────────────────

def draw_main_view(c: canvas.Canvas) -> None:
    # Disc outline
    c.setLineWidth(part_line_width)
    c.setDash()
    c.circle(view_center_x * inch, view_center_y * inch, disc_radius * inch, stroke=1, fill=0)

    # Disc centerlines extend past the OD by `centerline_overshoot`.
    centerline_overshoot = 0.30
    draw_centerline(
        c,
        view_center_x - disc_radius - centerline_overshoot, view_center_y,
        view_center_x + disc_radius + centerline_overshoot, view_center_y,
    )
    draw_centerline(
        c,
        view_center_x, view_center_y - disc_radius - centerline_overshoot,
        view_center_x, view_center_y + disc_radius + centerline_overshoot,
    )

    draw_centermark(c, view_center_x, view_center_y, size=0.18)

    # Holes (drawn at view-coordinate positions = disc center + offset).
    for hole_dx, hole_dy in hole_positions:
        hole_cx = view_center_x + hole_dx
        hole_cy = view_center_y + hole_dy
        c.setLineWidth(part_line_width)
        c.circle(hole_cx * inch, hole_cy * inch, hole_radius * inch, stroke=1, fill=0)
        draw_centermark(c, hole_cx, hole_cy, size=hole_diameter * 0.85)

    # ── Dimensions ──────────────────────────────────────────────────

    # OD dimension placed below the disc.
    draw_horizontal_dimension(
        c,
        view_center_x - disc_radius, view_center_y - disc_radius,
        view_center_x + disc_radius, view_center_y - disc_radius,
        offset=-0.70,
        text=f"\u00d8{disc_diameter:.3f}",
    )

    # Hole center-to-center (1.500), placed above the holes, horizontal.
    left_hole_cx = view_center_x + hole_positions[0][0]
    right_hole_cx = view_center_x + hole_positions[1][0]
    hole_spacing_dim_y = view_center_y + 0.45
    c.setLineWidth(thin_line_width)
    c.setDash()
    # Extension lines from hole centers up to dim line.
    c.line(left_hole_cx * inch, view_center_y * inch,
           left_hole_cx * inch, (hole_spacing_dim_y + 0.08) * inch)
    c.line(right_hole_cx * inch, view_center_y * inch,
           right_hole_cx * inch, (hole_spacing_dim_y + 0.08) * inch)
    c.line(left_hole_cx * inch, hole_spacing_dim_y * inch,
           right_hole_cx * inch, hole_spacing_dim_y * inch)
    _arrow(c, left_hole_cx, hole_spacing_dim_y, 1, 0)
    _arrow(c, right_hole_cx, hole_spacing_dim_y, -1, 0)
    c.setFont("Helvetica", 8)
    c.drawCentredString(view_center_x * inch,
                        (hole_spacing_dim_y + 0.05) * inch, "1.500")

    # Hole position from disc center (two .750 dims, one each side,
    # sharing the disc-center extension line).
    half_spacing_dim_y = view_center_y + 0.90
    c.line(view_center_x * inch, view_center_y * inch,
           view_center_x * inch, (half_spacing_dim_y + 0.08) * inch)
    c.line(left_hole_cx * inch, view_center_y * inch,
           left_hole_cx * inch, (half_spacing_dim_y + 0.08) * inch)
    c.line(left_hole_cx * inch, half_spacing_dim_y * inch,
           view_center_x * inch, half_spacing_dim_y * inch)
    _arrow(c, left_hole_cx, half_spacing_dim_y, 1, 0)
    _arrow(c, view_center_x, half_spacing_dim_y, -1, 0)
    c.drawCentredString(((left_hole_cx + view_center_x) / 2) * inch,
                        (half_spacing_dim_y + 0.05) * inch, ".750")
    c.line(right_hole_cx * inch, view_center_y * inch,
           right_hole_cx * inch, (half_spacing_dim_y + 0.08) * inch)
    c.line(right_hole_cx * inch, half_spacing_dim_y * inch,
           view_center_x * inch, half_spacing_dim_y * inch)
    _arrow(c, view_center_x, half_spacing_dim_y, 1, 0)
    _arrow(c, right_hole_cx, half_spacing_dim_y, -1, 0)
    c.drawCentredString(((right_hole_cx + view_center_x) / 2) * inch,
                        (half_spacing_dim_y + 0.05) * inch, ".750")

    # Tap callout. Two leaders share a common shoulder at the text and
    # approach the two holes from the upper-right, clear of the dim
    # stack. Left hole: arrow tip at 12 o'clock so the leader drops
    # almost vertically past the .750/1.500 dim labels. Right hole:
    # arrow tip on the upper-right quadrant (~45°).
    sin45 = 0.707
    left_dx, left_dy = hole_positions[0]
    right_dx, right_dy = hole_positions[1]
    tap_callout_targets = [
        (view_center_x + left_dx, view_center_y + left_dy + hole_radius),
        (view_center_x + right_dx + hole_radius * sin45,
         view_center_y + right_dy + hole_radius * sin45),
    ]
    # Text anchor: upper-right of the view, above and right of the right hole.
    tap_callout_text_anchor = (view_center_x + 1.60, view_center_y + 1.75)
    draw_leader(
        c,
        tap_callout_targets,
        tap_callout_text_anchor,
        [
            "2X \u00d8.438 THRU",
            "    1/4-18 NPT THRU",
        ],
    )


# ── Driver ───────────────────────────────────────────────────────────

def main() -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=(sheet_width * inch, sheet_height * inch))
    c.setTitle("Carbonator End Cap — Circular, 2-Hole NPT")
    c.setAuthor("derekbreden@gmail.com")
    c.setSubject("Engineering drawing — Xometry NPT tapping callout")

    # Black strokes/fills throughout
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    draw_border(c)
    draw_main_view(c)
    draw_notes(c)
    draw_title_block(c)

    # Sheet-top title
    c.setFont("Helvetica-Bold", 12)
    c.drawString(
        (sheet_margin + 0.10) * inch,
        (sheet_height - sheet_margin - 0.25) * inch,
        "CARBONATOR END CAP — CIRCULAR, 2-HOLE NPT",
    )

    c.showPage()
    c.save()
    print(f"Exported: {pdf_path}")

    # Short names scoped to this part. Units live inside the value so the
    # script controls them — change a value in source and every
    # dynamic-comment marker follows.
    variables = {
        "DISC_D": f"{disc_diameter:g} in",
        "DISC_R": f"{disc_radius:g} in",
        "DISC_THK": f"{disc_thickness:g} in",
        "HOLE_D": f"{hole_diameter:g} in",
        "HOLE_R": f"{hole_radius:g} in",
        "HOLE_SPACING": f"{hole_spacing:g} in",
        "HOLE_OFFSET": f"{hole_offset:g} in",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "DISC_D": 1,
            "DISC_R": 1,
            "DISC_THK": 1,
            "HOLE_D": 1,
            "HOLE_R": 1,
            "HOLE_SPACING": 1,
            "HOLE_OFFSET": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
