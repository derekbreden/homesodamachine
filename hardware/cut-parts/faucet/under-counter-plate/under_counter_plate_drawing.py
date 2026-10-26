"""Finished under-counter faucet mounting plate, on one ANSI A landscape sheet.

The plan strokes the actual production DXF's native arcs and lines. Feature
locations and widths read its generator's shared mounting interface; the sheet
metadata owns stock thickness. The rear opening has one semicircular end and
an open channel: its cap center and width define that actual cut geometry.

The drawing assigns finished profile/stock tolerances and edge/flatness limits.
Run with tools/cad-venv/bin/python. No geometry or laser ordering file changes.
"""

import json
import math
import sys
from pathlib import Path

import ezdxf
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HW / "scripts"))
sys.path.insert(0, str(HW / "cut-parts" / "carbonation" / "endcaps-circular"))
from _cadq_export import export_pdf
from endcap_circular_drawing import (
    line, text, arrow, leader, circular_leader, center, horizontal_dimension,
    VISIBLE, THIN, CENTER_DASH,
)
import under_counter_plate as plate

PDF_PATH = HERE / "under-counter-plate-drawing.pdf"
DXF_PATH = HERE / "under-counter-plate.dxf"
STOCK = json.loads((HERE / "under-counter-plate.dxf.json").read_text())
THICKNESS = STOCK["thickness_mm"]
PROFILE_TOL = 0.13
THICKNESS_TOL = 0.13
EDGE_BREAK_MAX = 0.10
FREE_STATE_GAP_MAX = 0.25
PT_PER_MM = 72 / 25.4
SHEET = (11 * 72, 8.5 * 72)
SCALE = 2 * PT_PER_MM
ORIGIN = (240, 385)
REVISION = "A"

REVIEW_REGIONS = [
    ("plan-upper", 65, 320, 468, 585),
    ("channel-widths", 175, 322, 430, 472),
    ("mouths-and-outline", 65, 194, 440, 332),
    ("edge-view", 483, 488, 762, 585),
    ("center-table", 480, 333, 751, 490),
    ("finish-notes", 480, 155, 751, 333),
    ("title-tolerances", 35, 27, 765, 146),
]


def xy(point):
    return ORIGIN[0] + point[0] * SCALE, ORIGIN[1] + point[1] * SCALE


def direct_width(c, left, right, at_y, label):
    """Width arrows touch the actual parallel channel walls."""
    x1, x2 = xy((left, 0))[0], xy((right, 0))[0]
    line(c, x1, at_y, x2, at_y)
    arrow(c, (x1, at_y), (x2, at_y))
    arrow(c, (x2, at_y), (x1, at_y))
    text(c, (x1 + x2) / 2, at_y + 5, label, 10, align="center")


def production_outline(c):
    """Join native entities into one closed stroke, including reversed arcs."""
    def endpoints(entity):
        if entity.dxftype() == "LINE":
            return tuple(entity.dxf.start)[:2], tuple(entity.dxf.end)[:2]
        if entity.dxftype() != "ARC":
            raise ValueError(f"Unrepresented production entity: {entity.dxftype()}")
        cx, cy = tuple(entity.dxf.center)[:2]
        r = entity.dxf.radius
        return tuple((cx + r * math.cos(math.radians(angle)),
                      cy + r * math.sin(math.radians(angle)))
                     for angle in (entity.dxf.start_angle, entity.dxf.end_angle))

    pending = list(ezdxf.readfile(DXF_PATH).modelspace())
    start = endpoints(pending[0])[0]
    current = start
    outline = c.beginPath()
    outline.moveTo(*xy(start))
    while pending:
        for index, entity in enumerate(pending):
            a, b = endpoints(entity)
            if math.dist(current, a) < 1e-7:
                reverse, current = False, b
                break
            if math.dist(current, b) < 1e-7:
                reverse, current = True, a
                break
        else:
            raise ValueError("Production profile is not one continuous boundary")
        pending.pop(index)
        if entity.dxftype() == "LINE":
            outline.lineTo(*xy(current))
        else:
            x, y = xy(entity.dxf.center)
            r = entity.dxf.radius * SCALE
            sweep = (entity.dxf.end_angle - entity.dxf.start_angle) % 360
            angle = entity.dxf.end_angle if reverse else entity.dxf.start_angle
            outline.arcTo(x - r, y - r, x + r, y + r,
                          angle, -sweep if reverse else sweep)
    if math.dist(current, start) >= 1e-7:
        raise ValueError("Production boundary is open")
    outline.close()
    c.setLineWidth(VISIBLE)
    c.drawPath(outline, stroke=1, fill=0)


def plan_view(c):
    disc_x, disc_y = xy((plate.disc_cx, plate.disc_cy))
    text(c, disc_x, 568, "PLAN VIEW", 12, bold=True, align="center")
    text(c, disc_x, 553, "SCALE 2:1 - DXF ORIENTATION", 8.5, align="center")
    production_outline(c)
    # Only feature-center marks are needed; long axes through the width labels
    # would crowd the two open channels.
    sx, sy = xy((plate.shank_cx, plate.shank_cy))
    bx, by = xy((plate.pill_cx, plate.pill_top_cap_cy))
    center(c, sx, sy, 14)
    center(c, bx, by, 13)
    text(c, sx - 21, sy + 12, "P1", 9, bold=True)
    text(c, bx, by + plate.pill_cap_radius * SCALE + 12, "P2", 9, bold=True, align="center")
    direct_width(c, plate.shank_cx - plate.shank_radius,
                 plate.shank_cx + plate.shank_radius, 350,
                 f"{plate.shank_diameter:.2f}")
    direct_width(c, plate.pill_left_x, plate.pill_right_x, 365,
                 f"{plate.pill_short_x:.2f}")
    horizontal_dimension(c, disc_x - plate.disc_radius * SCALE,
                         disc_x + plate.disc_radius * SCALE, disc_y, 200,
                         f"Ø{plate.disc_diameter:.2f}", 11)
    fillet_center, _, _ = plate.channel_corner_fillet(
        plate.shank_cx - plate.shank_radius, -1)
    # This radial ray lands on the fillet's actual short arc. Its label,
    # shoulder and target progress rightward without crossing the OD dimension.
    circular_leader(c, xy(fillet_center), plate.fillet_radius * SCALE,
                    (190, 220), (170, 220),
                    [f"4X R{plate.fillet_radius:.2f}"], 9)
    text(c, disc_x, 183, "ALL CHANNELS AND POCKETS CUT THROUGH.", 8.5, align="center")
    text(c, disc_x, 169, "CAPS SEMICIRCULAR; MOUTH ROUNDS TANGENT TO WALLS AND RIM.", 7.7, align="center")


def edge_view(c):
    x, bottom, scale = 514, 508, PT_PER_MM
    width, thickness = plate.disc_diameter * scale, THICKNESS * scale
    text(c, x + width / 2, 568, "EDGE VIEW", 12, bold=True, align="center")
    text(c, x + width / 2, 553, "LOOKING FROM +Y - SCALE 1:1", 8.5, align="center")
    text(c, x + width / 2, 538, "HIDDEN DETAIL OMITTED", 7.5, align="center")
    c.setLineWidth(VISIBLE)
    c.rect(x, bottom, width, thickness, stroke=1, fill=0)
    dim_x = 689
    for y in (bottom, bottom + thickness):
        line(c, x + width + 4, y, dim_x + 5, y)
    line(c, dim_x, bottom - 15, dim_x, bottom + thickness + 15)
    arrow(c, (dim_x, bottom), (dim_x, bottom - 15))
    arrow(c, (dim_x, bottom + thickness), (dim_x, bottom + thickness + 15))
    text(c, dim_x + 9, bottom + thickness / 2 - 3,
         f"{THICKNESS:.2f} ±{THICKNESS_TOL:.2f}", 8.5)


def center_table(c):
    left, right, top, row = 490, 743, 460, 22
    columns = (left, 539, 606, 673, right)
    text(c, left, 477, "ARC CENTER LOCATIONS", 10, bold=True)
    entries = [
        ("CENTER", "X", "Y", "R REF"),
        ("P1", f"{plate.shank_cx:.3f}", f"{plate.shank_cy:.3f}", f"{plate.shank_radius:.3f}"),
        ("P2", f"{plate.pill_cx:.3f}", f"{plate.pill_top_cap_cy:.3f}", f"{plate.pill_cap_radius:.3f}"),
        ("OD", f"{plate.disc_cx:.3f}", f"{plate.disc_cy:.3f}", f"{plate.disc_radius:.3f}"),
    ]
    bottom = top - row * len(entries)
    c.setLineWidth(THIN)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    for col in columns[1:-1]:
        line(c, col, bottom, col, top)
    for i, values in enumerate(entries):
        if i:
            line(c, left, top - i * row, right, top - i * row)
        for j, value in enumerate(values):
            text(c, (columns[j] + columns[j + 1]) / 2,
                 top - i * row - 14, value, 8.5, bold=i == 0 or j == 0, align="center")
    text(c, left, 358, "P1: SHANK CAP. P2: BUNDLE CAP. OD: OUTER ARC.", 7.8)
    text(c, left, 345, "ORIGIN P1; +X RIGHT, +Y UP. CHANNELS OPEN -Y.", 7.8)


def wrapped(c, x, y, paragraphs, width=253, size=8.7, leading=11.5):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    for paragraph in paragraphs:
        current = ""
        for word in paragraph.split():
            trial = (current + " " + word).strip()
            if current and stringWidth(trial, "Helvetica", size) > width:
                text(c, x, y, current, size)
                y -= leading
                current = word
            else:
                current = trial
        text(c, x, y, current, size)
        y -= leading + 5
    return y


def finish_notes(c):
    text(c, 490, 319, "FABRICATION AND FINISH", 10, bold=True)
    return wrapped(c, 490, 301, [
        '1. Laser-cut 316 stainless sheet, nominal 0.060 inch. Profile: UNDER-COUNTER-PLATE.DXF, at 1:1 in millimeters.',
        f"2. Remove all laser tabs and burrs. Finish BOTH FACES of the entire perimeter, channel walls, round caps and mouth rounds. Edge break {EDGE_BREAK_MAX:.2f} MAX.",
        "3. Profile dimensions apply to the remaining cut land after finishing. Keep both channels fully open and within the stated tolerances.",
        f"4. Deliver flat: {FREE_STATE_GAP_MAX:.2f} MAX gap under its own weight on a flat inspection surface. Remove loose metal, chips and cutting fluid.",
    ])


def title_block(c):
    left, right, bottom, top = 203, 765, 27, 143
    c.setLineWidth(0.7)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    line(c, left, 98, right, 98)
    line(c, left, 65, right, 65)
    line(c, right - 135, 98, right - 135, top)
    text(c, left + 10, 126, "HOME SODA MACHINE", 8)
    text(c, left + 10, 108, "UNDER-COUNTER MOUNTING PLATE", 11.5, bold=True)
    text(c, right - 67.5, 125, "FINISHED PART", 9, bold=True, align="center")
    text(c, right - 67.5, 110, "DESIGN DEFINITION", 9, align="center")
    for col in (left + 235, left + 370):
        line(c, col, 65, col, 98)
    for x, label, value in ((left + 10, "MATERIAL", "316 STAINLESS STEEL"),
                            (left + 245, "UNITS", "MILLIMETERS"),
                            (left + 380, "QUANTITY", "1 PER FAUCET")):
        text(c, x, 87, label, 7)
        text(c, x, 73, value, 8.5, bold=True)
    fields = ((left, left + 175, "DRAWING", "FCT-PLT-01"),
              (left + 175, left + 220, "REV", REVISION),
              (left + 220, left + 335, "DATE", "2026-10-26"),
              (left + 335, left + 452, "SCALE", "AS SHOWN"),
              (left + 452, right, "SHEET", "1 OF 1"))
    for i, (a, b, label, value) in enumerate(fields):
        if i:
            line(c, a, bottom, a, 65)
        text(c, a + 9, 53, label, 7)
        text(c, a + 9, 37, value, 9, bold=True)
    text(c, 47, 127, "HSM-000269", 9, bold=True)
    text(c, 47, 110, "UNLESS SPECIFIED", 8, bold=True)
    text(c, 47, 97, f"LINEAR ±{PROFILE_TOL:.2f} mm", 9)
    text(c, 47, 80, "REF = REFERENCE", 8)
    text(c, 47, 63, "DO NOT SCALE.", 8, bold=True)
    text(c, 47, 49, "ANSI A / 11 x 8.5 IN", 7.5)
    text(c, 47, 36, "PRINT AT 100% FOR SCALE.", 7.5)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Under-counter faucet mounting plate - engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("FCT-PLT-01 Rev A: production profile, channel dimensions and finished edge requirements")
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.rect(27, 27, SHEET[0] - 54, SHEET[1] - 54, stroke=1, fill=0)
    plan_view(c)
    edge_view(c)
    center_table(c)
    finish_notes(c)
    title_block(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
