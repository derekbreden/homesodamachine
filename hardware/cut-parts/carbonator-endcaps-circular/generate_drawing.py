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
    tools/cad-venv/bin/python hardware/cut-parts/carbonator-endcaps-circular/generate_drawing.py
"""

from datetime import date
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# ── Part geometry (inches) — mirrors generate_dxf.py ──
DISC_DIA = 4.860
DISC_R = DISC_DIA / 2
HOLE_DIA = 0.438           # 7/16" tap drill for 1/4"-18 NPT
HOLE_R = HOLE_DIA / 2
HOLE_POSITIONS = [(-0.750, 0.0), (+0.750, 0.0)]
THICKNESS = 0.250

# ── Sheet layout (inches) ──
SHEET_W = 11.0
SHEET_H = 8.5
MARGIN = 0.5

# Title-block box (bottom-right corner, inside margin)
TB_W = 4.0
TB_H = 2.0
TB_X = SHEET_W - MARGIN - TB_W
TB_Y = MARGIN

# View is placed on the left 2/3 of the sheet
VIEW_CX = 3.3          # disc center X on the sheet
VIEW_CY = SHEET_H / 2  # vertically centered

# Line weights (inches → points)
LW_BORDER = 0.020 * 72
LW_PART   = 0.015 * 72
LW_THIN   = 0.008 * 72

# Dash pattern for centerlines (ASME dash-dot, in points)
CENTERLINE_DASH = [6, 2, 1, 2]

OUT_DIR = Path(__file__).resolve().parent
PDF_PATH = OUT_DIR / "endcap-circular-2hole-drawing.pdf"


# ── Helpers ──────────────────────────────────────────────────────────

def draw_border(c: canvas.Canvas) -> None:
    c.setLineWidth(LW_BORDER)
    c.setDash()
    c.rect(
        MARGIN * inch,
        MARGIN * inch,
        (SHEET_W - 2 * MARGIN) * inch,
        (SHEET_H - 2 * MARGIN) * inch,
        stroke=1,
        fill=0,
    )


def draw_centermark(c: canvas.Canvas, cx: float, cy: float, size: float = 0.12) -> None:
    """Short crosshair at a circle's center."""
    c.setLineWidth(LW_THIN)
    c.setDash()
    c.line((cx - size) * inch, cy * inch, (cx + size) * inch, cy * inch)
    c.line(cx * inch, (cy - size) * inch, cx * inch, (cy + size) * inch)


def draw_circle_with_centermark(c: canvas.Canvas, cx: float, cy: float, dia: float) -> None:
    c.setLineWidth(LW_PART)
    c.setDash()
    c.circle(cx * inch, cy * inch, (dia / 2) * inch, stroke=1, fill=0)
    draw_centermark(c, cx, cy, size=min(0.15, dia * 0.6))


def draw_centerline(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    c.setLineWidth(LW_THIN)
    c.setDash(CENTERLINE_DASH, 0)
    c.line(x1 * inch, y1 * inch, x2 * inch, y2 * inch)
    c.setDash()


def _arrow(c: canvas.Canvas, x: float, y: float, dx: float, dy: float, size: float = 0.08) -> None:
    """Tiny filled arrowhead at (x,y) pointing in direction (dx,dy)."""
    import math
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
    c.setLineWidth(LW_THIN)
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
    c.setLineWidth(LW_THIN)
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
    x0 = TB_X
    y0 = TB_Y + TB_H + 0.10
    w = TB_W
    h = 1.35

    c.setLineWidth(LW_THIN)
    c.setDash()
    c.rect(x0 * inch, y0 * inch, w * inch, h * inch, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 9)
    c.drawString((x0 + 0.08) * inch, (y0 + h - 0.20) * inch, "NOTES:")

    notes = [
        "1. REMOVE ALL BURRS AND SHARP EDGES.",
        "2. TAP BOTH HOLES 1/4-18 NPT, THRU FULL PLATE (0.250 IN).",
        "3. NPT THREAD DEPTH: THRU (NO COUNTERBORE, NO SPOT-FACE).",
        "4. BREAK OUTER EDGE 0.010 IN x 45\u00b0.",
        "5. PART IS SYMMETRIC \u2014 NO HANDEDNESS.",
    ]
    c.setFont("Helvetica", 8)
    line_h = 0.17
    for i, note in enumerate(notes):
        c.drawString((x0 + 0.10) * inch, (y0 + h - 0.40 - i * line_h) * inch, note)


def draw_title_block(c: canvas.Canvas) -> None:
    x0 = TB_X
    y0 = TB_Y
    w = TB_W
    h = TB_H

    c.setLineWidth(LW_BORDER)
    c.setDash()
    c.rect(x0 * inch, y0 * inch, w * inch, h * inch, stroke=1, fill=0)

    rows = [
        ("PART",      "CARBONATOR END CAP, CIRCULAR, 2-HOLE NPT"),
        ("MATERIAL",  "304 STAINLESS STEEL"),
        ("THICKNESS", "0.250 IN (1/4)"),
        ("SCALE",     "1:1"),
        ("UNITS",     "INCHES"),
        ("TOLERANCE", "\u00b10.005 IN LINEAR, \u00b10.5\u00b0 ANGULAR (UNLESS NOTED)"),
        ("DATE",      date.today().isoformat()),
        ("PROJECT",   "SODA FLAVOR INJECTOR \u2014 CARBONATOR VESSEL"),
        ("DRAWN BY",  "derekbreden@gmail.com"),
    ]
    n = len(rows)
    row_h = h / n
    label_w = 1.05

    c.setLineWidth(LW_THIN)
    for i in range(1, n):
        y = y0 + i * row_h
        c.line(x0 * inch, y * inch, (x0 + w) * inch, y * inch)
    # Label/value divider column
    c.line((x0 + label_w) * inch, y0 * inch, (x0 + label_w) * inch, (y0 + h) * inch)

    # Title row gets a slightly larger font — first row (top) is "PART"
    for i, (label, value) in enumerate(rows):
        # rows list is top→bottom in reading order; reportlab y grows up,
        # so the topmost row sits at y0 + h - row_h
        row_index_from_top = i
        ry = y0 + h - (row_index_from_top + 1) * row_h

        c.setFont("Helvetica-Bold", 7)
        c.drawString((x0 + 0.06) * inch, (ry + row_h / 2 - 0.04) * inch, label)

        font_size = 10 if label == "PART" else 9
        c.setFont("Helvetica", font_size)
        # Shrink value if too long
        max_val_w = (w - label_w - 0.10) * inch
        text_w = c.stringWidth(value, "Helvetica", font_size)
        while text_w > max_val_w and font_size > 6:
            font_size -= 1
            c.setFont("Helvetica", font_size)
            text_w = c.stringWidth(value, "Helvetica", font_size)
        c.drawString((x0 + label_w + 0.08) * inch, (ry + row_h / 2 - 0.04) * inch, value)


# ── Main view ────────────────────────────────────────────────────────

def draw_main_view(c: canvas.Canvas) -> None:
    # Disc outline
    c.setLineWidth(LW_PART)
    c.setDash()
    c.circle(VIEW_CX * inch, VIEW_CY * inch, DISC_R * inch, stroke=1, fill=0)

    # Disc centerlines — 0.25" overshoot past the OD
    over = 0.30
    draw_centerline(
        c,
        VIEW_CX - DISC_R - over, VIEW_CY,
        VIEW_CX + DISC_R + over, VIEW_CY,
    )
    draw_centerline(
        c,
        VIEW_CX, VIEW_CY - DISC_R - over,
        VIEW_CX, VIEW_CY + DISC_R + over,
    )

    # Disc center mark
    draw_centermark(c, VIEW_CX, VIEW_CY, size=0.18)

    # Holes
    for hx, hy in HOLE_POSITIONS:
        cx = VIEW_CX + hx
        cy = VIEW_CY + hy
        c.setLineWidth(LW_PART)
        c.circle(cx * inch, cy * inch, HOLE_R * inch, stroke=1, fill=0)
        draw_centermark(c, cx, cy, size=HOLE_DIA * 0.85)

    # ── Dimensions ──────────────────────────────────────────────────

    # OD dimension (Ø4.860) — placed below the disc, horizontal
    draw_linear_dimension(
        c,
        VIEW_CX - DISC_R, VIEW_CY - DISC_R,
        VIEW_CX + DISC_R, VIEW_CY - DISC_R,
        offset=-0.70,
        text=f"\u00d8{DISC_DIA:.3f}",
        direction="horizontal",
    )

    # Hole center-to-center (1.500) — placed above the holes, horizontal
    left_cx = VIEW_CX + HOLE_POSITIONS[0][0]
    right_cx = VIEW_CX + HOLE_POSITIONS[1][0]
    dim_y_above = VIEW_CY + 0.45
    c.setLineWidth(LW_THIN)
    c.setDash()
    # Extension lines from hole centers up to dim line
    c.line(left_cx * inch, VIEW_CY * inch, left_cx * inch, (dim_y_above + 0.08) * inch)
    c.line(right_cx * inch, VIEW_CY * inch, right_cx * inch, (dim_y_above + 0.08) * inch)
    c.line(left_cx * inch, dim_y_above * inch, right_cx * inch, dim_y_above * inch)
    _arrow(c, left_cx, dim_y_above, 1, 0)
    _arrow(c, right_cx, dim_y_above, -1, 0)
    c.setFont("Helvetica", 8)
    c.drawCentredString(VIEW_CX * inch, (dim_y_above + 0.05) * inch, "1.500")

    # Hole position from center — two .750 dims above the 1.500 dim
    dim_y_750 = VIEW_CY + 0.90
    # left .750: from center to left hole
    c.line(VIEW_CX * inch, VIEW_CY * inch, VIEW_CX * inch, (dim_y_750 + 0.08) * inch)
    c.line(left_cx * inch, VIEW_CY * inch, left_cx * inch, (dim_y_750 + 0.08) * inch)
    c.line(left_cx * inch, dim_y_750 * inch, VIEW_CX * inch, dim_y_750 * inch)
    _arrow(c, left_cx, dim_y_750, 1, 0)
    _arrow(c, VIEW_CX, dim_y_750, -1, 0)
    c.drawCentredString(((left_cx + VIEW_CX) / 2) * inch, (dim_y_750 + 0.05) * inch, ".750")
    # right .750: from center to right hole
    c.line(right_cx * inch, VIEW_CY * inch, right_cx * inch, (dim_y_750 + 0.08) * inch)
    c.line(right_cx * inch, dim_y_750 * inch, VIEW_CX * inch, dim_y_750 * inch)
    _arrow(c, VIEW_CX, dim_y_750, 1, 0)
    _arrow(c, right_cx, dim_y_750, -1, 0)
    c.drawCentredString(((right_cx + VIEW_CX) / 2) * inch, (dim_y_750 + 0.05) * inch, ".750")

    # ── Tap callout leader ──────────────────────────────────────────
    # Two leaders share a common shoulder at the text. Each arrow tip
    # lands on the upper-right quadrant (~45°) of its hole. Targets are
    # well above the 1.500/.750 dim stack visually but the leaders
    # still approach from the upper-right, clear of the dim text.
    # Left hole: tip on 12 o'clock (top) so the leader drops almost
    # vertically past the .750/1.500 dim stack without running along
    # the dim labels. Right hole: tip on upper-right quadrant (~45°).
    hx_targets = [
        VIEW_CX + HOLE_POSITIONS[0][0],
        VIEW_CX + HOLE_POSITIONS[1][0] + HOLE_R * 0.707,
    ]
    hy_targets = [
        VIEW_CY + HOLE_POSITIONS[0][1] + HOLE_R,
        VIEW_CY + HOLE_POSITIONS[1][1] + HOLE_R * 0.707,
    ]
    # Text anchor: upper-right of view (above/right of right hole)
    text_x = VIEW_CX + 1.60
    text_y = VIEW_CY + 1.75
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
    c = canvas.Canvas(str(PDF_PATH), pagesize=(SHEET_W * inch, SHEET_H * inch))
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
        (MARGIN + 0.10) * inch,
        (SHEET_H - MARGIN - 0.25) * inch,
        "CARBONATOR END CAP — CIRCULAR, 2-HOLE NPT",
    )

    c.showPage()
    c.save()
    print(f"Exported: {PDF_PATH}")


if __name__ == "__main__":
    main()
