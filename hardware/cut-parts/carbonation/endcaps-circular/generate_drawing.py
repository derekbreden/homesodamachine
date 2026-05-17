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

Geometry mirrors `generate_dxf.py` in this folder — single source of truth
for the cut geometry is still the DXF; this PDF only annotates.

Run:
    tools/cad-venv/bin/python hardware/cut-parts/carbonation/endcaps-circular/generate_drawing.py
"""

import math
from datetime import date
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Part geometry in inches — mirrors generate_dxf.py.
disc_diameter = 4.860
disc_radius = disc_diameter / 2
disc_thickness = 0.250
hole_diameter = 0.438  # 7/16" tap drill for 1/4"-18 NPT
hole_radius = hole_diameter / 2
hole_positions = [(-0.750, 0.0), (+0.750, 0.0)]

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
    """Tiny filled arrowhead at (x,y) pointing in direction (dx,dy)."""
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    # Perpendicular
    px, py = -uy, ux
    half_w = size * 0.35
    tipx, tipy = x, y
    basex = x - ux * size
    basey = y - uy * size
    lx, ly = basex + px * half_w, basey + py * half_w
    rx, ry = basex - px * half_w, basey - py * half_w
    p = c.beginPath()
    p.moveTo(tipx * inch, tipy * inch)
    p.lineTo(lx * inch, ly * inch)
    p.lineTo(rx * inch, ry * inch)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def draw_linear_dimension(
    c: canvas.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    offset: float,
    text: str,
    direction: str = "horizontal",
    ext_to_point: bool = True,
) -> None:
    """Draw a linear dimension between (x1,y1) and (x2,y2) offset perpendicular.

    direction: 'horizontal' places the dim line at y = max(y1,y2)+offset (if +)
               'vertical' places the dim line at x = max(x1,x2)+offset (if +)
    """
    c.setLineWidth(thin_line_width)
    c.setDash()
    c.setFillColorRGB(0, 0, 0)
    c.setStrokeColorRGB(0, 0, 0)

    if direction == "horizontal":
        dy = offset
        dim_y = y1 + dy if abs(y1 - y2) < 1e-9 else max(y1, y2) + dy
        # Extension lines
        if ext_to_point:
            c.line(x1 * inch, y1 * inch, x1 * inch, (dim_y + (0.08 if dy > 0 else -0.08)) * inch)
            c.line(x2 * inch, y2 * inch, x2 * inch, (dim_y + (0.08 if dy > 0 else -0.08)) * inch)
        # Dimension line
        c.line(x1 * inch, dim_y * inch, x2 * inch, dim_y * inch)
        # Arrows point inward
        _arrow(c, x1, dim_y,  1, 0)
        _arrow(c, x2, dim_y, -1, 0)
        # Text
        c.setFont("Helvetica", 8)
        c.drawCentredString(((x1 + x2) / 2) * inch, (dim_y + 0.05) * inch, text)
    else:  # vertical
        dx = offset
        dim_x = x1 + dx if abs(x1 - x2) < 1e-9 else max(x1, x2) + dx
        if ext_to_point:
            c.line(x1 * inch, y1 * inch, (dim_x + (0.08 if dx > 0 else -0.08)) * inch, y1 * inch)
            c.line(x2 * inch, y2 * inch, (dim_x + (0.08 if dx > 0 else -0.08)) * inch, y2 * inch)
        c.line(dim_x * inch, y1 * inch, dim_x * inch, y2 * inch)
        _arrow(c, dim_x, y1, 0,  1)
        _arrow(c, dim_x, y2, 0, -1)
        c.saveState()
        c.translate((dim_x + 0.05) * inch, ((y1 + y2) / 2) * inch)
        c.rotate(90)
        c.setFont("Helvetica", 8)
        c.drawCentredString(0, 0, text)
        c.restoreState()


def draw_leader(
    c: canvas.Canvas,
    xtarget,
    ytarget,
    xtext: float,
    ytext: float,
    text_lines,
) -> None:
    """Leader line(s) from one or more (xtarget,ytarget) points to a text block.

    If xtarget/ytarget are sequences (same length), draws a multileader:
    both lines share a common shoulder near the text and branch to each
    target, arrowheads at each target.
    """
    c.setLineWidth(thin_line_width)
    c.setDash()
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    # Normalize targets to list form
    if hasattr(xtarget, "__iter__"):
        xs = list(xtarget)
        ys = list(ytarget)
    else:
        xs = [xtarget]
        ys = [ytarget]

    # Short horizontal shoulder at the text end (shared by all leaders)
    shoulder = 0.35
    # Determine shoulder direction based on where targets sit vs. text
    avg_xt = sum(xs) / len(xs)
    if xtext > avg_xt:
        knee_x = xtext - shoulder
    else:
        knee_x = xtext + shoulder
    knee_y = ytext

    # Horizontal shoulder from text to knee (single shared shoulder)
    c.line(knee_x * inch, knee_y * inch, xtext * inch, ytext * inch)

    # One slanted leader per target, each with its own arrowhead.
    # All leaders originate at the shared knee.
    for xt, yt in zip(xs, ys):
        c.line(xt * inch, yt * inch, knee_x * inch, knee_y * inch)
        dx = xt - knee_x
        dy = yt - knee_y
        _arrow(c, xt, yt, dx, dy, size=0.10)

    # Text block — left-aligned, stacked lines above the shoulder
    c.setFont("Helvetica", 9)
    if isinstance(text_lines, str):
        text_lines = [text_lines]
    # Start text just past the shoulder end-point so it doesn't collide
    anchor_x = (xtext + 0.05) * inch
    # Place first line just above the shoulder, subsequent lines below
    line_h = 0.14
    for i, line in enumerate(text_lines):
        c.drawString(anchor_x, (ytext + 0.04 - i * line_h) * inch, line)


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
        ("MATERIAL",  "304 STAINLESS STEEL"),
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

    # Disc centerlines — 0.25" overshoot past the OD
    over = 0.30
    draw_centerline(
        c,
        view_center_x - disc_radius - over, view_center_y,
        view_center_x + disc_radius + over, view_center_y,
    )
    draw_centerline(
        c,
        view_center_x, view_center_y - disc_radius - over,
        view_center_x, view_center_y + disc_radius + over,
    )

    # Disc center mark
    draw_centermark(c, view_center_x, view_center_y, size=0.18)

    # Holes
    for hx, hy in hole_positions:
        cx = view_center_x + hx
        cy = view_center_y + hy
        c.setLineWidth(part_line_width)
        c.circle(cx * inch, cy * inch, hole_radius * inch, stroke=1, fill=0)
        draw_centermark(c, cx, cy, size=hole_diameter * 0.85)

    # ── Dimensions ──────────────────────────────────────────────────

    # OD dimension (Ø4.860) — placed below the disc, horizontal
    draw_linear_dimension(
        c,
        view_center_x - disc_radius, view_center_y - disc_radius,
        view_center_x + disc_radius, view_center_y - disc_radius,
        offset=-0.70,
        text=f"\u00d8{disc_diameter:.3f}",
        direction="horizontal",
    )

    # Hole center-to-center (1.500) — placed above the holes, horizontal
    left_cx = view_center_x + hole_positions[0][0]
    right_cx = view_center_x + hole_positions[1][0]
    dim_y_above = view_center_y + 0.45
    c.setLineWidth(thin_line_width)
    c.setDash()
    # Extension lines from hole centers up to dim line
    c.line(left_cx * inch, view_center_y * inch, left_cx * inch, (dim_y_above + 0.08) * inch)
    c.line(right_cx * inch, view_center_y * inch, right_cx * inch, (dim_y_above + 0.08) * inch)
    c.line(left_cx * inch, dim_y_above * inch, right_cx * inch, dim_y_above * inch)
    _arrow(c, left_cx, dim_y_above, 1, 0)
    _arrow(c, right_cx, dim_y_above, -1, 0)
    c.setFont("Helvetica", 8)
    c.drawCentredString(view_center_x * inch, (dim_y_above + 0.05) * inch, "1.500")

    # Hole position from center — two .750 dims above the 1.500 dim
    dim_y_750 = view_center_y + 0.90
    # left .750: from center to left hole
    c.line(view_center_x * inch, view_center_y * inch, view_center_x * inch, (dim_y_750 + 0.08) * inch)
    c.line(left_cx * inch, view_center_y * inch, left_cx * inch, (dim_y_750 + 0.08) * inch)
    c.line(left_cx * inch, dim_y_750 * inch, view_center_x * inch, dim_y_750 * inch)
    _arrow(c, left_cx, dim_y_750, 1, 0)
    _arrow(c, view_center_x, dim_y_750, -1, 0)
    c.drawCentredString(((left_cx + view_center_x) / 2) * inch, (dim_y_750 + 0.05) * inch, ".750")
    # right .750: from center to right hole
    c.line(right_cx * inch, view_center_y * inch, right_cx * inch, (dim_y_750 + 0.08) * inch)
    c.line(right_cx * inch, dim_y_750 * inch, view_center_x * inch, dim_y_750 * inch)
    _arrow(c, view_center_x, dim_y_750, 1, 0)
    _arrow(c, right_cx, dim_y_750, -1, 0)
    c.drawCentredString(((right_cx + view_center_x) / 2) * inch, (dim_y_750 + 0.05) * inch, ".750")

    # ── Tap callout leader ──────────────────────────────────────────
    # Two leaders share a common shoulder at the text. Each arrow tip
    # lands on the upper-right quadrant (~45°) of its hole. Targets are
    # well above the 1.500/.750 dim stack visually but the leaders
    # still approach from the upper-right, clear of the dim text.
    # Left hole: tip on 12 o'clock (top) so the leader drops almost
    # vertically past the .750/1.500 dim stack without running along
    # the dim labels. Right hole: tip on upper-right quadrant (~45°).
    hx_targets = [
        view_center_x + hole_positions[0][0],
        view_center_x + hole_positions[1][0] + hole_radius * 0.707,
    ]
    hy_targets = [
        view_center_y + hole_positions[0][1] + hole_radius,
        view_center_y + hole_positions[1][1] + hole_radius * 0.707,
    ]
    # Text anchor: upper-right of view (above/right of right hole)
    text_x = view_center_x + 1.60
    text_y = view_center_y + 1.75
    draw_leader(
        c,
        hx_targets, hy_targets,
        text_x, text_y,
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


if __name__ == "__main__":
    main()
