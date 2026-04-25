"""
Engineering drawings for the 316L SS pressure-swirl atomizer
(two-piece CNC, for Xometry quote upload alongside the STEP files).

Produces two ANSI A landscape PDFs:

  - atomizer-nozzle-body-drawing.pdf
        Longitudinal cross-section + outlet face view.  Calls out
        orifice Ø, orifice concentricity, swirl chamber Ø/depth,
        convergent cone angle, puck seat Ø (press fit), and both
        thread specifications (1/8-27 NPT male outlet, 1/4-28 UNF
        female inlet).

  - atomizer-nozzle-puck-drawing.pdf
        Front face view (showing 4 tangential slots + 4 axial feed
        holes) + side cross-section.  Calls out slot geometry,
        tangent radius, feed-hole PCD, and press-fit OD.

Drawings annotate the STEP geometry only — STEP remains the single
source of truth for shape.  Everything is metric (mm); title block
tolerance block is the default unless overridden by a specific
dimension's tolerance suffix.

Geometry mirrors generate_step_cadquery.py in this folder.

Run:
    tools/cad-venv/bin/python hardware/cut-parts/atomizer-nozzle/generate_drawing.py
"""

from datetime import date
from pathlib import Path
import math

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


# ════════════════════════════════════════════════════════════════
# PART DIMENSIONS (mm — mirror generate_step_cadquery.py)
# ════════════════════════════════════════════════════════════════

# ── Atomizer internal geometry ──
ORIFICE_D = 1.10
ORIFICE_L = 0.70
SWIRL_D   = 4.00
SWIRL_L   = 3.00
CONE_INCL_DEG = 90.0
CONE_L    = (SWIRL_D - ORIFICE_D) / 2.0   # 1.45 for 90° incl

PUCK_OD = 6.00
PUCK_L  = 2.50
PUCK_ID = 4.00

SLOT_N = 4
SLOT_W = 0.50
SLOT_D = 0.40
SLOT_TANGENT_R = SWIRL_D / 2.0
SLOT_LEN = math.sqrt((PUCK_OD / 2.0) ** 2 - SLOT_TANGENT_R ** 2)   # 2.236

FEED_HOLE_D = 0.50
FEED_T = 1.50
FEED_HOLE_R = math.sqrt(SLOT_TANGENT_R ** 2 + FEED_T ** 2)         # 2.500
FEED_HOLE_PCD = 2.0 * FEED_HOLE_R                                   # 5.000

BACK_CHAMFER = 0.30

# ── Body envelope ──
HEX_AF = 12.70
INLET_BORE_D = 6.40
INLET_BORE_L = 8.00
NPT_NOMINAL_OD = 10.287
NPT_L = 10.00

# Body Z-stack (top to bottom in cross-section)
Z_INLET_TOP    = 0.0
Z_PUCK_TOP     = INLET_BORE_L                         # 8.00
Z_SWIRL_TOP    = Z_PUCK_TOP + PUCK_L                  # 10.50
Z_CONE_TOP     = Z_SWIRL_TOP + SWIRL_L                # 13.50
Z_ORIFICE_TOP  = Z_CONE_TOP + CONE_L                  # 14.95
Z_OUTLET_FACE  = Z_ORIFICE_TOP + ORIFICE_L            # 15.65
BODY_TOTAL_L   = Z_OUTLET_FACE
HEX_L          = BODY_TOTAL_L - NPT_L                 # 5.65
Z_NPT_TOP      = HEX_L


# ════════════════════════════════════════════════════════════════
# SHEET / LINE-WEIGHT CONSTANTS
# ════════════════════════════════════════════════════════════════

SHEET_W = 11.0    # ANSI A landscape, inches
SHEET_H = 8.5
MARGIN = 0.5

LW_BORDER = 0.020 * 72
LW_PART   = 0.015 * 72
LW_THIN   = 0.008 * 72
LW_HIDDEN = 0.010 * 72

CENTERLINE_DASH = [6, 2, 1, 2]
HIDDEN_DASH     = [4, 2]

OUT_DIR = Path(__file__).resolve().parent


# ════════════════════════════════════════════════════════════════
# UNIT CONVERSION (mm → paper inches via drawing scale)
# ════════════════════════════════════════════════════════════════

def mm_to_in(x_mm, scale):
    """Convert a part dimension in mm to paper position in inches."""
    return x_mm / 25.4 * scale


# ════════════════════════════════════════════════════════════════
# SHARED DRAWING HELPERS
# ════════════════════════════════════════════════════════════════

def draw_border(c):
    c.setLineWidth(LW_BORDER)
    c.setDash()
    c.rect(
        MARGIN * inch, MARGIN * inch,
        (SHEET_W - 2 * MARGIN) * inch,
        (SHEET_H - 2 * MARGIN) * inch,
        stroke=1, fill=0,
    )


def draw_centermark(c, cx, cy, size=0.12):
    c.setLineWidth(LW_THIN)
    c.setDash()
    c.line((cx - size) * inch, cy * inch, (cx + size) * inch, cy * inch)
    c.line(cx * inch, (cy - size) * inch, cx * inch, (cy + size) * inch)


def draw_centerline(c, x1, y1, x2, y2):
    c.setLineWidth(LW_THIN)
    c.setDash(CENTERLINE_DASH, 0)
    c.line(x1 * inch, y1 * inch, x2 * inch, y2 * inch)
    c.setDash()


def _arrow(c, x, y, dx, dy, size=0.08):
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    half_w = size * 0.35
    basex = x - ux * size
    basey = y - uy * size
    lx, ly = basex + px * half_w, basey + py * half_w
    rx, ry = basex - px * half_w, basey - py * half_w
    p = c.beginPath()
    p.moveTo(x * inch, y * inch)
    p.lineTo(lx * inch, ly * inch)
    p.lineTo(rx * inch, ry * inch)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def draw_linear_dim(
    c, x1, y1, x2, y2, offset, text,
    direction="horizontal", label_font_size=8,
):
    """Draw a linear dimension between (x1,y1) and (x2,y2), offset perpendicular."""
    c.setLineWidth(LW_THIN)
    c.setDash()
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    if direction == "horizontal":
        dim_y = y1 + offset if abs(y1 - y2) < 1e-9 else max(y1, y2) + offset
        tick = 0.08 if offset > 0 else -0.08
        c.line(x1 * inch, y1 * inch, x1 * inch, (dim_y + tick) * inch)
        c.line(x2 * inch, y2 * inch, x2 * inch, (dim_y + tick) * inch)
        c.line(x1 * inch, dim_y * inch, x2 * inch, dim_y * inch)
        _arrow(c, x1, dim_y,  1, 0)
        _arrow(c, x2, dim_y, -1, 0)
        c.setFont("Helvetica", label_font_size)
        c.drawCentredString(((x1 + x2) / 2) * inch, (dim_y + 0.05) * inch, text)
    else:  # vertical
        dim_x = x1 + offset if abs(x1 - x2) < 1e-9 else max(x1, x2) + offset
        tick = 0.08 if offset > 0 else -0.08
        c.line(x1 * inch, y1 * inch, (dim_x + tick) * inch, y1 * inch)
        c.line(x2 * inch, y2 * inch, (dim_x + tick) * inch, y2 * inch)
        c.line(dim_x * inch, y1 * inch, dim_x * inch, y2 * inch)
        _arrow(c, dim_x, y1, 0,  1)
        _arrow(c, dim_x, y2, 0, -1)
        c.saveState()
        c.translate((dim_x + 0.05) * inch, ((y1 + y2) / 2) * inch)
        c.rotate(90)
        c.setFont("Helvetica", label_font_size)
        c.drawCentredString(0, 0, text)
        c.restoreState()


def draw_leader(c, xtargets, ytargets, xtext, ytext, text_lines,
                font_size=9, line_h=0.14):
    """Leader line(s) from one or more targets to a text block."""
    c.setLineWidth(LW_THIN)
    c.setDash()
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    if not hasattr(xtargets, "__iter__"):
        xtargets = [xtargets]
        ytargets = [ytargets]
    xtargets = list(xtargets)
    ytargets = list(ytargets)

    shoulder = 0.35
    avg_xt = sum(xtargets) / len(xtargets)
    knee_x = xtext - shoulder if xtext > avg_xt else xtext + shoulder
    knee_y = ytext

    c.line(knee_x * inch, knee_y * inch, xtext * inch, ytext * inch)

    for xt, yt in zip(xtargets, ytargets):
        c.line(xt * inch, yt * inch, knee_x * inch, knee_y * inch)
        _arrow(c, xt, yt, xt - knee_x, yt - knee_y, size=0.10)

    if isinstance(text_lines, str):
        text_lines = [text_lines]
    c.setFont("Helvetica", font_size)
    anchor_x = (xtext + 0.05) * inch
    for i, line in enumerate(text_lines):
        c.drawString(anchor_x, (ytext + 0.04 - i * line_h) * inch, line)


def draw_hatching(c, outer_pts, inner_pts, spacing=0.06, angle_deg=45.0):
    """Draw ANSI 31 hatching (45° parallel lines) in the region between an
    outer closed polygon and an inner closed polygon.  Uses reportlab's
    clipPath with even-odd fill rule to achieve the "ring" region.

    Coordinates in INCHES (paper space).
    """
    c.saveState()

    # Build compound path: outer polygon + inner polygon (even-odd = ring)
    p = c.beginPath()
    for i, (x, y) in enumerate(outer_pts):
        if i == 0:
            p.moveTo(x * inch, y * inch)
        else:
            p.lineTo(x * inch, y * inch)
    p.close()
    for i, (x, y) in enumerate(inner_pts):
        if i == 0:
            p.moveTo(x * inch, y * inch)
        else:
            p.lineTo(x * inch, y * inch)
    p.close()
    c.clipPath(p, stroke=0, fill=0)

    # Compute bounding box to know how many hatch lines to draw
    all_x = [x for x, _ in outer_pts] + [x for x, _ in inner_pts]
    all_y = [y for _, y in outer_pts] + [y for _, y in inner_pts]
    x_min, x_max = min(all_x) - 0.2, max(all_x) + 0.2
    y_min, y_max = min(all_y) - 0.2, max(all_y) + 0.2

    theta = math.radians(angle_deg)
    # Hatch lines are lines perpendicular to direction (cosθ, sinθ), spaced
    # by `spacing` along (cosθ, sinθ).
    # Parameterize line by offset s along (cosθ, sinθ):
    #   passes through (s·cosθ, s·sinθ), direction (−sinθ, cosθ)
    # Endpoints on the bbox: solve x, y ranges.

    c.setLineWidth(LW_THIN * 0.7)
    c.setStrokeColorRGB(0.25, 0.25, 0.25)
    c.setDash()

    diag = math.hypot(x_max - x_min, y_max - y_min)
    # Span of offset s: project bbox corners onto (cosθ, sinθ)
    s_proj = [
        x * math.cos(theta) + y * math.sin(theta)
        for x in (x_min, x_max) for y in (y_min, y_max)
    ]
    s_min, s_max = min(s_proj), max(s_proj)

    s = math.floor(s_min / spacing) * spacing
    while s <= s_max:
        # Line direction (perpendicular to projection axis): (−sinθ, cosθ)
        # Point on line: (s·cosθ, s·sinθ)
        # Draw long segment covering bbox diagonal
        cx0 = s * math.cos(theta)
        cy0 = s * math.sin(theta)
        dx = -math.sin(theta) * diag
        dy =  math.cos(theta) * diag
        x1, y1 = cx0 - dx, cy0 - dy
        x2, y2 = cx0 + dx, cy0 + dy
        c.line(x1 * inch, y1 * inch, x2 * inch, y2 * inch)
        s += spacing

    c.setStrokeColorRGB(0, 0, 0)
    c.restoreState()


def draw_polyline(c, pts, closed=True, line_width=LW_PART):
    c.setLineWidth(line_width)
    c.setDash()
    p = c.beginPath()
    p.moveTo(pts[0][0] * inch, pts[0][1] * inch)
    for x, y in pts[1:]:
        p.lineTo(x * inch, y * inch)
    if closed:
        p.close()
    c.drawPath(p, stroke=1, fill=0)


# ════════════════════════════════════════════════════════════════
# TITLE BLOCK / NOTES (shared structure, part-specific content)
# ════════════════════════════════════════════════════════════════

# Title block bottom-right, notes block bottom-left (side by side at bottom).
# Leaves the entire upper 5.5" of the sheet free for the cross-section and
# auxiliary views.
TB_W = 4.0
TB_H = 2.0
TB_X = SHEET_W - MARGIN - TB_W   # 6.5
TB_Y = MARGIN                     # 0.5

NOTES_X = MARGIN                  # 0.5
NOTES_Y = MARGIN                  # 0.5
NOTES_W = TB_X - MARGIN - 0.10    # 5.9
NOTES_H = TB_H                    # 2.0 — matches title block for visual balance


def draw_title_block(c, rows):
    x0, y0, w, h = TB_X, TB_Y, TB_W, TB_H
    c.setLineWidth(LW_BORDER)
    c.setDash()
    c.rect(x0 * inch, y0 * inch, w * inch, h * inch, stroke=1, fill=0)

    n = len(rows)
    row_h = h / n
    label_w = 1.05

    c.setLineWidth(LW_THIN)
    for i in range(1, n):
        y = y0 + i * row_h
        c.line(x0 * inch, y * inch, (x0 + w) * inch, y * inch)
    c.line((x0 + label_w) * inch, y0 * inch, (x0 + label_w) * inch, (y0 + h) * inch)

    for i, (label, value) in enumerate(rows):
        ry = y0 + h - (i + 1) * row_h
        c.setFont("Helvetica-Bold", 7)
        c.drawString((x0 + 0.06) * inch, (ry + row_h / 2 - 0.04) * inch, label)

        font_size = 10 if label == "PART" else 9
        c.setFont("Helvetica", font_size)
        max_val_w = (w - label_w - 0.10) * inch
        while c.stringWidth(value, "Helvetica", font_size) > max_val_w and font_size > 6:
            font_size -= 1
            c.setFont("Helvetica", font_size)
        c.drawString((x0 + label_w + 0.08) * inch, (ry + row_h / 2 - 0.04) * inch, value)


def draw_notes(c, notes, title="NOTES:"):
    """Notes block.  Auto-shrinks font + line height so the whole list fits
    in the fixed-height box (previous version silently overflowed into the
    title block when the note count grew)."""
    x0, y0, w, h = NOTES_X, NOTES_Y, NOTES_W, NOTES_H
    c.setLineWidth(LW_THIN)
    c.setDash()
    c.rect(x0 * inch, y0 * inch, w * inch, h * inch, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 9)
    c.drawString((x0 + 0.08) * inch, (y0 + h - 0.22) * inch, title)

    # Fit check — shrink line_h and/or font if the list is long.
    n = len(notes)
    header_pad = 0.38         # vertical space taken by "NOTES:" header
    content_h = h - header_pad - 0.05
    line_h = min(0.14, content_h / max(n, 1))
    font_size = 8 if line_h >= 0.135 else 7

    c.setFont("Helvetica", font_size)
    for i, note in enumerate(notes):
        c.drawString(
            (x0 + 0.10) * inch,
            (y0 + h - header_pad - (i + 0.5) * line_h) * inch,
            note,
        )


# ════════════════════════════════════════════════════════════════
# BODY DRAWING
# ════════════════════════════════════════════════════════════════

def build_body_profiles(scale, cx, cz_top):
    """Return (outer_pts, inner_pts) in paper inches for the BODY cross-section.

    Coordinate convention on paper:
        x grows right, y grows up.
        Body is drawn vertical with INLET face at top (y = cz_top)
        and OUTLET face at bottom.  Axis of symmetry at x = cx.
    """
    def s(mm):  # part mm → paper inches at drawing scale
        return mm / 25.4 * scale

    # ── Outer envelope (closed polygon, clockwise from top-left) ──
    outer = [
        (cx - s(HEX_AF / 2.0),         cz_top),                                  # top-left hex
        (cx + s(HEX_AF / 2.0),         cz_top),                                  # top-right hex
        (cx + s(HEX_AF / 2.0),         cz_top - s(HEX_L)),                       # bottom-right hex
        (cx + s(NPT_NOMINAL_OD / 2.0), cz_top - s(HEX_L)),                       # step in at NPT (right)
        (cx + s(NPT_NOMINAL_OD / 2.0), cz_top - s(BODY_TOTAL_L)),                # bottom-right NPT (= outlet face)
        (cx - s(NPT_NOMINAL_OD / 2.0), cz_top - s(BODY_TOTAL_L)),                # bottom-left NPT
        (cx - s(NPT_NOMINAL_OD / 2.0), cz_top - s(HEX_L)),                       # top-left NPT (=hex step)
        (cx - s(HEX_AF / 2.0),         cz_top - s(HEX_L)),                       # bottom-left hex (back to step)
    ]

    # ── Inner bore stack (closed polygon, counterclockwise to create hole) ──
    # From inlet face downward:
    #   Ø6.40 × 8.00  →  Ø6.00 × 2.50  →  Ø4.00 × 3.00  →
    #   90° cone (Ø4 → Ø1.1 over 1.45)  →  Ø1.10 × 0.70
    inner = [
        # Right side, top to bottom
        (cx + s(INLET_BORE_D / 2.0),   cz_top),                                  # top-right (inlet face opens)
        (cx + s(INLET_BORE_D / 2.0),   cz_top - s(INLET_BORE_L)),                # bottom of inlet bore
        (cx + s(PUCK_OD / 2.0),        cz_top - s(INLET_BORE_L)),                # step in to puck seat
        (cx + s(PUCK_OD / 2.0),        cz_top - s(Z_SWIRL_TOP)),                 # bottom of puck seat
        (cx + s(SWIRL_D / 2.0),        cz_top - s(Z_SWIRL_TOP)),                 # step in to swirl chamber
        (cx + s(SWIRL_D / 2.0),        cz_top - s(Z_CONE_TOP)),                  # bottom of swirl chamber
        (cx + s(ORIFICE_D / 2.0),      cz_top - s(Z_ORIFICE_TOP)),               # end of cone / top of orifice
        (cx + s(ORIFICE_D / 2.0),      cz_top - s(BODY_TOTAL_L)),                # bottom-right at outlet face
        # Left side, bottom to top (reverse)
        (cx - s(ORIFICE_D / 2.0),      cz_top - s(BODY_TOTAL_L)),
        (cx - s(ORIFICE_D / 2.0),      cz_top - s(Z_ORIFICE_TOP)),
        (cx - s(SWIRL_D / 2.0),        cz_top - s(Z_CONE_TOP)),
        (cx - s(SWIRL_D / 2.0),        cz_top - s(Z_SWIRL_TOP)),
        (cx - s(PUCK_OD / 2.0),        cz_top - s(Z_SWIRL_TOP)),
        (cx - s(PUCK_OD / 2.0),        cz_top - s(INLET_BORE_L)),
        (cx - s(INLET_BORE_D / 2.0),   cz_top - s(INLET_BORE_L)),
        (cx - s(INLET_BORE_D / 2.0),   cz_top),                                  # top-left (inlet face)
    ]
    return outer, inner


def draw_body_section(c):
    """Main BODY cross-section view — vertical, inlet at top, outlet at bottom.

    Layout:
      - Section occupies upper-left quadrant (section_cx = 2.9, top at y = 7.0).
      - Only two dim lines are drawn on the section itself: overall length
        (far left) and hex AF (top).  ALL internal bore-stack features are
        leader callouts on the right of the section, stacked vertically in
        inlet-to-orifice order.  NPT callout goes to the LEFT of the NPT
        shank so it doesn't pile on top of the right-side stack.
    """
    SCALE = 5.0

    def s(mm):
        return mm_to_in(mm, SCALE)

    section_cx = 2.9
    section_cz_top = 7.0

    outer, inner = build_body_profiles(SCALE, section_cx, section_cz_top)

    # Material hatching (ANSI 31)
    draw_hatching(c, outer, inner, spacing=0.07, angle_deg=45.0)
    draw_polyline(c, outer, closed=True, line_width=LW_PART)
    draw_polyline(c, inner, closed=True, line_width=LW_PART)

    # Axis centerline, extending past both ends
    draw_centerline(
        c,
        section_cx, section_cz_top + 0.30,
        section_cx, section_cz_top - s(BODY_TOTAL_L) - 0.30,
    )

    # ── Dim lines: only overall length + hex AF ──
    draw_linear_dim(
        c,
        section_cx - s(HEX_AF / 2.0) - 0.02, section_cz_top,
        section_cx - s(HEX_AF / 2.0) - 0.02, section_cz_top - s(BODY_TOTAL_L),
        offset=-0.70,
        text=f"{BODY_TOTAL_L:.2f}",
        direction="vertical",
    )
    draw_linear_dim(
        c,
        section_cx - s(HEX_AF / 2.0), section_cz_top,
        section_cx + s(HEX_AF / 2.0), section_cz_top,
        offset=0.55,
        text=f"{HEX_AF:.2f} AF",
        direction="horizontal",
    )

    # ── Leader callouts on RIGHT of section ──
    # Text anchor points are evenly spaced vertically so that no two
    # callouts' text bodies can overlap, even though their LEADER TARGETS
    # cluster near the bottom of the section (inside the orifice/cone/swirl
    # region).  Leader lines vary in length; text positions are fixed.
    RX = 5.4
    LINE_H = 0.13
    text_y = {
        "inlet":   6.85,   # 3 lines → bottom 6.59
        "puck":    6.15,   # 2 lines → bottom 6.02
        "swirl":   5.50,   # 2 lines → bottom 5.37
        "cone":    4.95,   # 1 line
        "orifice": 4.55,   # 5 lines → bottom 4.03  (notes top = 2.5)
    }

    # 1. Inlet bore + UNF tap
    draw_leader(
        c,
        [section_cx + s(INLET_BORE_D / 2.0)],
        [section_cz_top - s(INLET_BORE_L / 2.0)],
        RX, text_y["inlet"],
        [
            f"\u00d8{INLET_BORE_D:.2f} \u00d7 {INLET_BORE_L:.2f} DEEP",
            "TAP 1/4-28 UNF FEMALE",
            "(MIN 6.00 THREAD DEPTH)",
        ],
        font_size=7.5, line_h=LINE_H,
    )

    # 2. Puck seat
    draw_leader(
        c,
        [section_cx + s(PUCK_OD / 2.0)],
        [section_cz_top - s(Z_PUCK_TOP + PUCK_L / 2.0)],
        RX, text_y["puck"],
        [
            f"\u00d8{PUCK_OD:.2f} H7 \u00d7 {PUCK_L:.2f} DEEP",
            "PUCK PRESS-FIT SEAT",
        ],
        font_size=7.5, line_h=LINE_H,
    )

    # 3. Swirl chamber
    draw_leader(
        c,
        [section_cx + s(SWIRL_D / 2.0)],
        [section_cz_top - s(Z_SWIRL_TOP + SWIRL_L / 2.0)],
        RX, text_y["swirl"],
        [
            f"\u00d8{SWIRL_D:.2f} H7 \u00d7 {SWIRL_L:.2f} DEEP",
            "SWIRL CHAMBER",
        ],
        font_size=7.5, line_h=LINE_H,
    )

    # 4. 90° convergent cone (single line)
    cone_y_mid = section_cz_top - s(Z_CONE_TOP + CONE_L / 2.0)
    cone_x_mid = section_cx + s((SWIRL_D + ORIFICE_D) / 4.0)
    draw_leader(
        c,
        [cone_x_mid], [cone_y_mid],
        RX, text_y["cone"],
        ["90\u00b0 INCL. CONE \u00b12\u00b0"],
        font_size=7.5,
    )

    # 5. Orifice (critical) — five lines, bottom-most in the right column
    draw_leader(
        c,
        [section_cx + s(ORIFICE_D / 2.0)],
        [section_cz_top - s(Z_ORIFICE_TOP + ORIFICE_L / 2.0)],
        RX, text_y["orifice"],
        [
            f"\u00d8{ORIFICE_D:.2f} \u00b10.025 \u00d7 {ORIFICE_L:.2f}",
            "ORIFICE — DRILLED + REAMED",
            "  SHARP-EDGED INLET",
            "  NO DEBURR ON OUTLET FACE",
            "  CONCENTRIC TO \u00d84.00 WITHIN 0.05 TIR",
        ],
        font_size=7.5, line_h=LINE_H,
    )

    # 6. NPT male thread — LEFT side of section.  Kept to a single short
    #    label so the text does not extend into the NPT-shank silhouette.
    draw_leader(
        c,
        [section_cx - s(NPT_NOMINAL_OD / 2.0)],
        [section_cz_top - s(HEX_L + NPT_L / 2.0)],
        0.75, section_cz_top - s(BODY_TOTAL_L) + 0.35,
        ["1/8-27 NPT MALE"],
        font_size=7.5,
    )

    # View title (below the section, to the left)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        (section_cx - s(HEX_AF / 2.0) - 0.5) * inch,
        (section_cz_top - s(BODY_TOTAL_L) - 0.45) * inch,
        f"SECTION A\u2014A   (SCALE {int(SCALE)}:1)",
    )


def draw_body_outlet_face_view(c):
    """Auxiliary view: looking UP INTO the outlet face (orifice end)."""
    SCALE = 5.0

    def s(mm):
        return mm_to_in(mm, SCALE)

    # Top-right of sheet, pushed right so the hex point-to-point envelope
    # (±1.44") clears the inner border (10.5) by ~0.05", and high enough
    # that the hex bottom stays well above the notes/title-block row.
    ax_cx = 9.00
    ax_cy = SHEET_H - 2.30

    # Outer NPT shank boundary
    c.setLineWidth(LW_PART)
    c.setDash()
    c.circle(ax_cx * inch, ax_cy * inch, s(NPT_NOMINAL_OD / 2.0) * inch, stroke=1, fill=0)

    # Hex behind (hidden, since NPT is in front)
    c.setLineWidth(LW_HIDDEN)
    c.setDash(HIDDEN_DASH, 0)
    hex_pts = []
    for i in range(6):
        ang = math.radians(30.0 + 60.0 * i)   # flats on top/bottom
        r_ac = s(HEX_AF / 2.0) / math.cos(math.radians(30.0))
        hex_pts.append((ax_cx + r_ac * math.cos(ang), ax_cy + r_ac * math.sin(ang)))
    draw_polyline(c, hex_pts, closed=True, line_width=LW_HIDDEN)
    c.setDash()

    # Orifice in center
    c.setLineWidth(LW_PART)
    c.circle(ax_cx * inch, ax_cy * inch, s(ORIFICE_D / 2.0) * inch, stroke=1, fill=0)

    # Swirl chamber (hidden circle, as seen from outlet face)
    c.setLineWidth(LW_HIDDEN)
    c.setDash(HIDDEN_DASH, 0)
    c.circle(ax_cx * inch, ax_cy * inch, s(SWIRL_D / 2.0) * inch, stroke=1, fill=0)
    c.setDash()

    # Centerlines (vertical + horizontal through axis)
    ext = s(NPT_NOMINAL_OD / 2.0) + 0.20
    draw_centerline(c, ax_cx - ext, ax_cy, ax_cx + ext, ax_cy)
    draw_centerline(c, ax_cx, ax_cy - ext, ax_cx, ax_cy + ext)
    draw_centermark(c, ax_cx, ax_cy, size=0.10)

    # View title
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        (ax_cx - 1.10) * inch,
        (ax_cy + ext + 0.25) * inch,
        f"VIEW B (OUTLET FACE)   (SCALE {int(SCALE)}:1)",
    )


def draw_body_page(c):
    draw_border(c)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(
        (MARGIN + 0.10) * inch,
        (SHEET_H - MARGIN - 0.25) * inch,
        "ATOMIZER NOZZLE \u2014 BODY (316L SS, 2-PIECE ASSEMBLY)",
    )

    draw_body_section(c)
    draw_body_outlet_face_view(c)

    notes = [
        "1. MATERIAL: 316L STAINLESS STEEL.",
        "2. REMOVE ALL BURRS EXCEPT AT ORIFICE OUTLET FACE.",
        "3. CRITICAL — ORIFICE EDGE MUST REMAIN SHARP AS DRILLED + REAMED.",
        "   NO DEBURR, NO CHAMFER, NO RADIUS ON OUTLET FACE.",
        "4. SWIRL CHAMBER \u00d84.00 H7 CONCENTRIC TO \u00d81.10 ORIFICE",
        "   WITHIN 0.05 MM TIR.",
        "5. PRESS-FIT MATE: \u00d86.00 H7 BORE RECEIVES PUCK \u00d86.00 h7 OD",
        "   (DIAMETRAL INTERFERENCE 0.005\u20130.010 MM).",
        "6. SURFACE FINISH: AS MACHINED (Ra 3.2 \u03bcm) UNLESS NOTED.",
        "7. MATING PART: ATOMIZER-NOZZLE-PUCK (SEE SEPARATE DRAWING).",
    ]
    draw_notes(c, notes)

    rows = [
        ("PART",      "ATOMIZER NOZZLE \u2014 BODY"),
        ("MATERIAL",  "316L STAINLESS STEEL"),
        ("UNITS",     "MILLIMETERS"),
        ("SCALE",     "5:1 (SECTION A\u2014A, VIEW B)"),
        ("TOLERANCE", "\u00b10.1 LINEAR, \u00b10.5\u00b0 ANGULAR (UNLESS NOTED)"),
        ("FINISH",    "AS MACHINED, Ra 3.2 \u03bcm UNLESS NOTED"),
        ("DATE",      date.today().isoformat()),
        ("PROJECT",   "SODA FLAVOR INJECTOR \u2014 CARBONATOR ATOMIZER"),
        ("DRAWN BY",  "derekbreden@gmail.com"),
    ]
    draw_title_block(c, rows)


# ════════════════════════════════════════════════════════════════
# PUCK DRAWING
# ════════════════════════════════════════════════════════════════

def draw_puck_front_view(c):
    """Front-face (downstream side) view of the puck.  Scale 10:1.

    The view sits in the upper-left quadrant above the notes block.  Slot and
    feed-hole callouts use single-target leaders (with "4X" notation) so the
    leader lines do not criss-cross the part.
    """
    SCALE = 10.0

    def s(mm):
        return mm_to_in(mm, SCALE)

    cx = 2.9
    cy = 5.20

    # OD Ø6.00 + central bore Ø4.00
    c.setLineWidth(LW_PART)
    c.setDash()
    c.circle(cx * inch, cy * inch, s(PUCK_OD / 2.0) * inch, stroke=1, fill=0)
    c.circle(cx * inch, cy * inch, s(PUCK_ID / 2.0) * inch, stroke=1, fill=0)

    # Centerlines (vertical + horizontal) through the main axis
    ext = s(PUCK_OD / 2.0) + 0.40
    draw_centerline(c, cx - ext, cy, cx + ext, cy)
    draw_centerline(c, cx, cy - ext, cx, cy + ext)
    draw_centermark(c, cx, cy, size=0.15)

    # Feed-hole PCD centerline circle (dash-dot)
    c.setLineWidth(LW_THIN)
    c.setDash(CENTERLINE_DASH, 0)
    c.circle(cx * inch, cy * inch, s(FEED_HOLE_R) * inch, stroke=1, fill=0)
    c.setDash()

    # ── 4 tangential slots + feed holes, at angles 0, 90, 180, 270 ──
    # Save the θ = 90° (top) slot and feed-hole geometry for single-target
    # leader callouts after the loop — top-of-view is empty sheet space.
    top_slot_outer = None
    top_feed_hole = None
    for i in range(SLOT_N):
        theta = 2.0 * math.pi * i / SLOT_N

        # Tangent point on Ø4.00 (inner end of slot), world XY
        ix = SLOT_TANGENT_R * math.cos(theta)
        iy = SLOT_TANGENT_R * math.sin(theta)
        tx = -math.sin(theta)
        ty =  math.cos(theta)
        nx, ny = -ty, tx

        hw = SLOT_W / 2.0
        sl = SLOT_LEN
        start_x, start_y = ix, iy
        end_x,   end_y   = ix + tx * sl, iy + ty * sl
        corners_mm = [
            (start_x + nx * hw, start_y + ny * hw),
            (end_x   + nx * hw, end_y   + ny * hw),
            (end_x   - nx * hw, end_y   - ny * hw),
            (start_x - nx * hw, start_y - ny * hw),
        ]
        corners_in = [(cx + s(x), cy + s(y)) for x, y in corners_mm]
        draw_polyline(c, corners_in, closed=True, line_width=LW_PART)

        # Axial feed hole
        fx = ix + tx * FEED_T
        fy = iy + ty * FEED_T
        c.setLineWidth(LW_PART)
        c.circle((cx + s(fx)) * inch, (cy + s(fy)) * inch,
                 s(FEED_HOLE_D / 2.0) * inch, stroke=1, fill=0)
        draw_centermark(c, cx + s(fx), cy + s(fy), size=0.06)

        if i == 1:  # θ = 90°, top
            # Midpoint of the slot's OUTER edge — clean leader target
            mid_out_x = (corners_mm[1][0] + corners_mm[2][0]) / 2.0
            mid_out_y = (corners_mm[1][1] + corners_mm[2][1]) / 2.0
            top_slot_outer = (cx + s(mid_out_x), cy + s(mid_out_y))
            top_feed_hole  = (cx + s(fx),        cy + s(fy))

    # ── Dimensions ──
    # OD (below part)
    draw_linear_dim(
        c,
        cx - s(PUCK_OD / 2.0), cy - s(PUCK_OD / 2.0),
        cx + s(PUCK_OD / 2.0), cy - s(PUCK_OD / 2.0),
        offset=-0.80,
        text=f"\u00d8{PUCK_OD:.2f} h7",
        direction="horizontal",
    )
    # Central bore Ø — single-target leader, arrow onto Ø4.00 circle at
    # 8 o'clock position.  Text placed to the left of the view, away from
    # any slot or feed hole.
    bore_target_ang = math.radians(210)
    draw_leader(
        c,
        [cx + s(PUCK_ID / 2.0) * math.cos(bore_target_ang)],
        [cy + s(PUCK_ID / 2.0) * math.sin(bore_target_ang)],
        cx - 2.10, cy - 0.70,
        [f"\u00d8{PUCK_ID:.2f} CENTRAL BORE"],
        font_size=7.5,
    )
    # Feed hole PCD (above part)
    draw_linear_dim(
        c,
        cx - s(FEED_HOLE_R), cy + s(PUCK_OD / 2.0),
        cx + s(FEED_HOLE_R), cy + s(PUCK_OD / 2.0),
        offset=0.70,
        text=f"\u00d8{FEED_HOLE_PCD:.2f} PCD",
        direction="horizontal",
    )

    # Slot callout — single target on the θ=90° (top) slot, leader goes
    # up-right into free space above the view.  First line shortened so the
    # text block does not extend into the SIDE SECTION title area further
    # right on the sheet.
    if top_slot_outer is not None:
        draw_leader(
            c,
            [top_slot_outer[0]], [top_slot_outer[1]],
            cx + 1.40, cy + 1.75,
            [
                "4X TANGENTIAL SLOTS (EQ. 90\u00b0)",
                f"  {SLOT_W:.2f} WIDE \u00d7 {SLOT_D:.2f} DEEP",
                f"  TANGENT TO \u00d8{SWIRL_D:.2f}",
                f"  SLOT LENGTH {SLOT_LEN:.2f} REF",
                "  USE \u00d80.40 END MILL",
            ],
            font_size=7.5, line_h=0.13,
        )

    # Feed-hole callout — single target on the θ=90° (top) feed hole, leader
    # goes up-left into free space above the view.
    if top_feed_hole is not None:
        draw_leader(
            c,
            [top_feed_hole[0]], [top_feed_hole[1]],
            cx - 2.10, cy + 1.55,
            [
                f"4X \u00d8{FEED_HOLE_D:.2f} THRU",
                f"  ON \u00d8{FEED_HOLE_PCD:.2f} PCD",
                "  ALIGNED WITH SLOT CENTERLINES",
            ],
            font_size=7.5, line_h=0.13,
        )

    # View title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        (cx - s(PUCK_OD / 2.0) - 0.5) * inch,
        (cy + s(PUCK_OD / 2.0) + 1.05) * inch,
        f"FRONT FACE VIEW   (SCALE {int(SCALE)}:1)",
    )


def draw_puck_side_section(c):
    """Side cross-section of puck: looking at the cylindrical side.  Scale 10:1."""
    SCALE = 10.0

    def s(mm):
        return mm_to_in(mm, SCALE)

    # Right side of sheet, above notes/title-block row.  Shifted right so
    # its title ("SIDE SECTION ...") clears the slot-callout text on the
    # front view, which ends around x = 6.45.
    sec_cx = 8.40
    sec_cy_top = 6.20

    # Coordinate convention for this view:
    #   x: paper horizontal = radial in part
    #   y: paper vertical, up = BACK face of puck (upstream), down = FRONT face
    # Back face at y = sec_cy_top;  front face at y = sec_cy_top - s(PUCK_L)

    # Outer boundary — rectangle Ø6.00 wide × 2.50 tall
    outer = [
        (sec_cx - s(PUCK_OD / 2.0), sec_cy_top),
        (sec_cx + s(PUCK_OD / 2.0), sec_cy_top),
        (sec_cx + s(PUCK_OD / 2.0), sec_cy_top - s(PUCK_L)),
        (sec_cx - s(PUCK_OD / 2.0), sec_cy_top - s(PUCK_L)),
    ]

    # Inner bore with back chamfer at top.  Bore profile (clockwise from top-right):
    #   (+Ø_chamfered_at_back/2, Z=0) down the chamfer to (+Ø4/2, Z=0.30)
    #   straight down to (+Ø4/2, Z=PUCK_L)
    #   across to (-Ø4/2, Z=PUCK_L)
    #   straight up to (-Ø4/2, Z=0.30)
    #   chamfer up to (-Ø_chamfered_at_back/2, Z=0)
    chamfered_D = PUCK_ID + 2.0 * BACK_CHAMFER
    inner = [
        (sec_cx + s(chamfered_D / 2.0), sec_cy_top),
        (sec_cx + s(PUCK_ID / 2.0),     sec_cy_top - s(BACK_CHAMFER)),
        (sec_cx + s(PUCK_ID / 2.0),     sec_cy_top - s(PUCK_L)),
        (sec_cx - s(PUCK_ID / 2.0),     sec_cy_top - s(PUCK_L)),
        (sec_cx - s(PUCK_ID / 2.0),     sec_cy_top - s(BACK_CHAMFER)),
        (sec_cx - s(chamfered_D / 2.0), sec_cy_top),
    ]

    # We can't easily hatch this because the inner profile is OPEN (both ends
    # of the inner boundary land on the top edge of the outer rectangle).
    # Treat the section as the solid outer minus the through-bore + side
    # slots.  Build the compound path as a closed figure that runs around
    # the outer, then around the inner, so the even-odd clip produces the
    # correct ring.  We close the inner profile along the top edge.
    inner_closed = inner + [
        (sec_cx - s(chamfered_D / 2.0), sec_cy_top),
        (sec_cx + s(chamfered_D / 2.0), sec_cy_top),
    ]

    # Slots appear in the side view as small rectangles cut into the
    # FRONT face (bottom of section view).  Drawn as visible hollows.
    # Slot cross-section in side view:
    #   at the angular positions where a slot intersects our section
    #   plane (XZ plane), it cuts a rectangle SLOT_W wide × SLOT_D deep
    #   from the front face.  Our section plane is the horizontal
    #   diameter, so slots at θ=0 and θ=180 are IN this plane (cut
    #   through the slot length along its long axis; slot appears as a
    #   rectangle SLOT_LEN long × SLOT_D deep, positioned tangent to
    #   Ø4.00).  The slot is offset from axis by SLOT_TANGENT_R.
    # For a clean side view, show ONE slot (θ=0) crossing the section
    # at SLOT_TANGENT_R radial, running from +SLOT_TANGENT_R inward...
    # actually both θ=0 and θ=180 slots are perpendicular to the
    # section plane in their long dimension.  They project as a small
    # rectangle SLOT_W × SLOT_D at the tangent radial.
    #
    # Simpler: draw the slot PROJECTION at θ=90 (where the slot long
    # axis is perpendicular to the section plane).  The projection is
    # a rectangle SLOT_W × SLOT_D positioned at r = SLOT_TANGENT_R, on
    # the front face.  Draw two (one on each side of axis).

    slot_boxes = []
    for sign in (+1, -1):
        slot_boxes.append([
            (sec_cx + sign * s(SLOT_TANGENT_R - SLOT_W / 2.0), sec_cy_top - s(PUCK_L)),
            (sec_cx + sign * s(SLOT_TANGENT_R + SLOT_W / 2.0), sec_cy_top - s(PUCK_L)),
            (sec_cx + sign * s(SLOT_TANGENT_R + SLOT_W / 2.0), sec_cy_top - s(PUCK_L - SLOT_D)),
            (sec_cx + sign * s(SLOT_TANGENT_R - SLOT_W / 2.0), sec_cy_top - s(PUCK_L - SLOT_D)),
        ])

    # Feed holes appear in side view as dashed hidden lines running axially
    # through the puck.  Two visible at this section (at r = ±FEED_HOLE_R).
    feed_hole_lines = [
        (sec_cx + sign * s(FEED_HOLE_R), sec_cy_top,
         sec_cx + sign * s(FEED_HOLE_R), sec_cy_top - s(PUCK_L))
        for sign in (+1, -1)
    ]

    # ── Hatching inside material ──
    # Build a path that is "outer - inner - slots":  run outer CW,
    # inner CCW, slots CCW.  The even-odd rule fills the "ring minus holes".
    # Simpler: just hatch the outer ring (ignoring slot cutouts); slots are
    # small and we draw their outlines separately.
    draw_hatching(c, outer, inner_closed, spacing=0.07, angle_deg=45.0)

    # White-fill the slot boxes so hatching doesn't show through them
    for box in slot_boxes:
        p = c.beginPath()
        p.moveTo(box[0][0] * inch, box[0][1] * inch)
        for x, y in box[1:]:
            p.lineTo(x * inch, y * inch)
        p.close()
        c.setFillColorRGB(1, 1, 1)
        c.drawPath(p, stroke=0, fill=1)
        c.setFillColorRGB(0, 0, 0)

    # Outlines
    draw_polyline(c, outer, closed=True, line_width=LW_PART)
    draw_polyline(c, inner, closed=False, line_width=LW_PART)
    for box in slot_boxes:
        draw_polyline(c, box, closed=True, line_width=LW_PART)

    # Feed holes as hidden lines
    c.setLineWidth(LW_HIDDEN)
    c.setDash(HIDDEN_DASH, 0)
    for x1, y1, x2, y2 in feed_hole_lines:
        c.line(x1 * inch, y1 * inch, x2 * inch, y2 * inch)
    c.setDash()

    # Centerline
    ext = s(PUCK_OD / 2.0) + 0.30
    draw_centerline(c, sec_cx, sec_cy_top + 0.30,
                    sec_cx, sec_cy_top - s(PUCK_L) - 0.30)

    # ── Dimensions ──
    # Thickness (vertical, on right)
    draw_linear_dim(
        c,
        sec_cx + s(PUCK_OD / 2.0) + 0.02, sec_cy_top,
        sec_cx + s(PUCK_OD / 2.0) + 0.02, sec_cy_top - s(PUCK_L),
        offset=0.45,
        text=f"{PUCK_L:.2f}",
        direction="vertical",
    )
    # Slot depth (vertical, on far right of slot box)
    draw_linear_dim(
        c,
        sec_cx + s(SLOT_TANGENT_R + SLOT_W / 2.0), sec_cy_top - s(PUCK_L),
        sec_cx + s(SLOT_TANGENT_R + SLOT_W / 2.0), sec_cy_top - s(PUCK_L - SLOT_D),
        offset=-0.60,
        text=f"{SLOT_D:.2f}",
        direction="vertical",
    )
    # Back chamfer callout — anchor kept under the inner border (10.5)
    # regardless of SCALE, with a short shoulder.
    draw_leader(
        c,
        [sec_cx + s(PUCK_ID / 2.0 + BACK_CHAMFER / 2.0)],
        [sec_cy_top - s(BACK_CHAMFER / 2.0)],
        sec_cx + 0.70, sec_cy_top + 0.40,
        [f"{BACK_CHAMFER:.2f} \u00d7 45\u00b0 CHAMFER"],
        font_size=7.5, line_h=0.13,
    )

    # ── Face labels ──
    c.setFont("Helvetica", 7)
    c.drawString(
        (sec_cx - s(PUCK_OD / 2.0) - 0.65) * inch,
        (sec_cy_top - 0.04) * inch,
        "BACK FACE",
    )
    c.drawString(
        (sec_cx - s(PUCK_OD / 2.0) - 0.65) * inch,
        (sec_cy_top - s(PUCK_L) - 0.08) * inch,
        "FRONT FACE",
    )
    c.drawString(
        (sec_cx - s(PUCK_OD / 2.0) - 0.65) * inch,
        (sec_cy_top - s(PUCK_L) - 0.22) * inch,
        "(SLOTS)",
    )

    # View title
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        (sec_cx - s(PUCK_OD / 2.0) - 0.5) * inch,
        (sec_cy_top + 0.55) * inch,
        f"SIDE SECTION   (SCALE {int(SCALE)}:1)",
    )


def draw_puck_page(c):
    draw_border(c)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(
        (MARGIN + 0.10) * inch,
        (SHEET_H - MARGIN - 0.25) * inch,
        "ATOMIZER NOZZLE \u2014 PUCK (316L SS, SWIRL DISTRIBUTOR)",
    )

    draw_puck_front_view(c)
    draw_puck_side_section(c)

    notes = [
        "1. MATERIAL: 316L STAINLESS STEEL.",
        "2. REMOVE ALL BURRS AND SHARP EDGES.",
        "3. PRESS FIT: OD \u00d86.00 h7 \u2014 MATES WITH BODY BORE \u00d86.00 H7",
        "   (TARGET DIAMETRAL INTERFERENCE 0.005\u20130.010 MM).",
        "4. ANY ANGULAR ORIENTATION ABOUT CENTRAL AXIS IS ACCEPTABLE.",
        "5. SURFACE FINISH: AS MACHINED (Ra 3.2 \u03bcm) UNLESS NOTED.",
        "6. MATING PART: ATOMIZER-NOZZLE-BODY (SEE SEPARATE DRAWING).",
    ]
    draw_notes(c, notes)

    rows = [
        ("PART",      "ATOMIZER NOZZLE \u2014 PUCK"),
        ("MATERIAL",  "316L STAINLESS STEEL"),
        ("UNITS",     "MILLIMETERS"),
        ("SCALE",     "10:1 (ALL VIEWS)"),
        ("TOLERANCE", "\u00b10.05 LINEAR, \u00b10.5\u00b0 ANGULAR (UNLESS NOTED)"),
        ("FINISH",    "AS MACHINED, Ra 3.2 \u03bcm UNLESS NOTED"),
        ("DATE",      date.today().isoformat()),
        ("PROJECT",   "SODA FLAVOR INJECTOR \u2014 CARBONATOR ATOMIZER"),
        ("DRAWN BY",  "derekbreden@gmail.com"),
    ]
    draw_title_block(c, rows)


# ════════════════════════════════════════════════════════════════
# DRIVER
# ════════════════════════════════════════════════════════════════

def main():
    for fname, page_fn, subject in [
        ("atomizer-nozzle-body-drawing.pdf", draw_body_page,
         "Engineering drawing — atomizer body (316L SS)"),
        ("atomizer-nozzle-puck-drawing.pdf", draw_puck_page,
         "Engineering drawing — atomizer puck (316L SS)"),
    ]:
        path = OUT_DIR / fname
        c = canvas.Canvas(str(path), pagesize=(SHEET_W * inch, SHEET_H * inch))
        c.setTitle(fname.replace(".pdf", "").replace("-", " ").title())
        c.setAuthor("derekbreden@gmail.com")
        c.setSubject(subject)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFillColorRGB(0, 0, 0)

        page_fn(c)

        c.showPage()
        c.save()
        print(f"Exported: {path}")


if __name__ == "__main__":
    main()
