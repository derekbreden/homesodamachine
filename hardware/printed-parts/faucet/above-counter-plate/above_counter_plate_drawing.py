"""Finished Sculpted faucet mounting plate, on one ANSI B landscape sheet.

Analytical views use the production generator's ellipse, passages and screw
seat parameters. The small ribbon clearance is contained within the rear slot;
it does not add an edge to this part. A local section through the front pedestal
shows the counterbore, solid bearing stock and locating chamfer.

The drawing assigns finished manufacturing tolerances. It does not alter CAD,
the print recipe or the assembled faucet. Run with tools/cad-venv/bin/python.
"""

import sys
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HW / "scripts"))
sys.path.insert(0, str(HW / "cut-parts/carbonation/endcaps-circular"))
from _cadq_export import export_pdf
from endcap_circular_drawing import (
    line, text, arrow, leader, circular_leader, center, horizontal_dimension,
    path_from_points, hatch, cutting_plane_ends, VISIBLE, THIN, CENTER_DASH,
)
import above_counter_plate as plate

PDF_PATH = HERE / "above-counter-plate-drawing.pdf"
SHEET = (17 * 72, 11 * 72)
PT_PER_MM = 72 / 25.4
SCALE = 2 * PT_PER_MM
ORIGIN = (300, 470)
GENERAL_TOL = 0.20
LOCATION_TOL = 0.10
FACE_GAP_MAX = 0.20
BEARING_MIN = 2.70
REVISION = "A"

# The production source orders the right, left, then front screws. Give the
# drawing's left/right/front identifiers an explicit geometric mapping.
PEDESTALS = [
    ("B1", *min(plate.base_pod_centers, key=lambda p: p[0])),
    ("B2", *max(plate.base_pod_centers, key=lambda p: p[0])),
    ("B3", *min(plate.base_pod_centers, key=lambda p: p[1])),
]
REVIEW_REGIONS = [
    ("plan-envelope", 35, 280, 500, 755),
    ("rear-slot", 125, 546, 470, 709),
    ("shank-and-pedestals", 136, 298, 692, 547),
    ("section-markers", 230, 298, 370, 400),
    ("front-view", 35, 166, 606, 286),
    ("pedestal-section", 660, 502, 1190, 763),
    ("location-table", 700, 307, 1189, 497),
    ("finish-notes", 640, 153, 1190, 300),
    ("general-tolerances", 35, 27, 625, 146),
    ("title-block", 630, 27, 1197, 146),
]


def xy(x, y):
    return ORIGIN[0] + x * SCALE, ORIGIN[1] + y * SCALE


def slot_path(c, center_xy, length, width):
    x, y = center_xy
    r = width / 2
    half = (length - width) / 2
    p = c.beginPath()
    p.moveTo(x - half, y - r)
    p.lineTo(x + half, y - r)
    p.arcTo(x + half - r, y - r, x + half + r, y + r, -90, 180)
    p.lineTo(x - half, y + r)
    p.arcTo(x - half - r, y - r, x - half + r, y + r, 90, 180)
    p.close()
    return p


def vertical_dim(c, x, y1, y2, lower_x, upper_x, label,
                 left_text=False, outside=False, size=10):
    direction = -1 if x < min(lower_x, upper_x) else 1
    for y, start in ((y1, lower_x), (y2, upper_x)):
        line(c, start + direction * 4, y, x + direction * 5, y)
    if outside:
        line(c, x, y1 - 13, x, y2 + 13)
        arrow(c, (x, y1), (x, y1 - 13))
        arrow(c, (x, y2), (x, y2 + 13))
    else:
        line(c, x, y1, x, y2)
        arrow(c, (x, y1), (x, y2))
        arrow(c, (x, y2), (x, y1))
    text(c, x - 8 if left_text else x + 9, (y1 + y2) / 2 - 3,
         label, size, align="right" if left_text else "left")


def plan_view(c):
    cx, cy = xy(0, plate.foot_center_y)
    rx, ry = plate.foot_width * SCALE / 2, plate.foot_depth * SCALE / 2
    text(c, cx, 735, "TOP VIEW - PEDESTAL SIDE", 12, bold=True, align="center")
    text(c, cx, 718, "LOOKING -Z - SCALE 2:1", 9, align="center")
    c.setLineWidth(VISIBLE)
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, stroke=1, fill=0)
    sx, sy = xy(*plate.shank_hole_center)
    c.circle(sx, sy, plate.shank_hole_radius * SCALE, stroke=1, fill=0)
    slot = slot_path(c, xy(*plate.pill_slot_center),
                     plate.bundle_slot_length_x * SCALE, plate.pill_width_y * SCALE)
    c.drawPath(slot, stroke=1, fill=0)
    center(c, sx, sy, 17)
    text(c, sx, sy + plate.shank_hole_radius * SCALE + 11,
         "O", 10, bold=True, align="center")
    slx, sly = xy(*plate.pill_slot_center)
    center(c, slx, sly, 12)
    text(c, slx, sly + plate.pill_width_y * SCALE / 2 + 11,
         "S1", 10, bold=True, align="center")
    for label, x, y in PEDESTALS:
        px, py = xy(x, y)
        for diameter in (plate.base_pedestal_dia,
                         plate.base_pedestal_dia - 2 * plate.base_pedestal_chamfer,
                         plate.base_pod_shank_dia):
            c.setLineWidth(VISIBLE)
            c.circle(px, py, diameter * SCALE / 2, stroke=1, fill=0)
        center(c, px, py, 14)
        text(c, px, py + (45 if label == "B3" else 33), label,
             10, bold=True, align="center")
    horizontal_dimension(c, cx - rx, cx + rx, cy, 689,
                         f"{plate.foot_width:.2f}", 11)
    vertical_dim(c, 85, cy - ry, cy + ry, cx, cx,
                 f"{plate.foot_depth:.2f}", left_text=True, size=11)
    text(c, cx, 287, "TRUE ELLIPSE; CENTER O. HIDDEN DETAIL OMITTED.",
         8.5, align="center")
    # Touch the upper straight slot edge. This route stays between the overall
    # width witnesses and to the right of the overall-height top extension.
    slot_top = sly + plate.pill_width_y * SCALE / 2
    leader(c, (slx + 30, slot_top), (315, 672), (295, 672),
           [f"S1: {plate.bundle_slot_length_x:.2f} X {plate.pill_width_y:.2f} THRU",
            "BOTH SIZES +0.20/0", f"ENDS R{plate.pill_width_y / 2:.3f} REF"], 9.5)
    circular_leader(c, (sx, sy), plate.shank_hole_radius * SCALE,
                    (505, 400), (525, 400),
                    [f"Ø{plate.shank_hole_diameter:.2f} +0.20/0 THRU", "ORIGIN O"], 10)
    _, bx, by = PEDESTALS[1]
    circular_leader(c, xy(bx, by), plate.base_pedestal_dia * SCALE / 2,
                    (505, 430), (525, 430),
                    [f"3X Ø{plate.base_pedestal_dia:.2f} +0/-0.10", "PEDESTAL OD"], 10)
    # This is a local section at B3, in +Y. The widened view below crops the
    # plate to either side of that pedestal with conventional broken ends.
    ax, ay = xy(*PEDESTALS[2][1:])
    line(c, ax - 30, ay, ax + 30, ay, 0.65, dash=CENTER_DASH)
    cutting_plane_ends(c, ax - 38, ax + 38, ay, "A", rise=18)


def front_view(c):
    z0, scale = 220, SCALE
    left, right = ORIGIN[0] - plate.foot_width * scale / 2, ORIGIN[0] + plate.foot_width * scale / 2
    bottom = z0 - plate.plate_thickness * scale
    text(c, ORIGIN[0], 267, "FRONT VIEW", 12, bold=True, align="center")
    text(c, ORIGIN[0], 251, "LOOKING +Y - SCALE 2:1 - HIDDEN DETAIL OMITTED", 8.5, align="center")
    c.setLineWidth(VISIBLE)
    c.rect(left, bottom, right - left, z0 - bottom, stroke=1, fill=0)
    for _, px, _ in PEDESTALS:
        x = ORIGIN[0] + px * scale
        r = plate.base_pedestal_dia * scale / 2
        ch = plate.base_pedestal_chamfer * scale
        top = z0 + plate.base_pedestal_height * scale
        p = c.beginPath()
        p.moveTo(x - r, z0)
        p.lineTo(x - r, top - ch)
        p.lineTo(x - r + ch, top)
        p.lineTo(x + r - ch, top)
        p.lineTo(x + r, top - ch)
        p.lineTo(x + r, z0)
        c.drawPath(p, stroke=1, fill=0)
    vertical_dim(c, 93, bottom, z0, left, left,
                 f"{plate.plate_thickness:.2f} ±0.10", left_text=True, size=9)
    right_center = max(p[1] for p in PEDESTALS)
    upper_x = ORIGIN[0] + (right_center + plate.base_pedestal_dia / 2
                         - plate.base_pedestal_chamfer) * scale
    vertical_dim(c, 501, z0, z0 + plate.base_pedestal_height * scale,
                 right, upper_x, f"3X {plate.base_pedestal_height:.2f} ±0.10", outside=True, size=9)


def pedestal_section(c):
    x, z0, scale, half = 890, 600, 5 * PT_PER_MM, 90
    bottom = z0 - plate.plate_thickness * scale
    top = z0 + plate.base_pedestal_height * scale
    shoulder = bottom + plate.base_screw_counterbore_depth * scale
    r = plate.base_pedestal_dia * scale / 2
    hole = plate.base_pod_shank_dia * scale / 2
    bore = plate.base_pod_counterbore_dia * scale / 2
    chamfer = plate.base_pedestal_chamfer * scale
    text(c, x, 746, "SECTION A-A", 12, bold=True, align="center")
    text(c, x, 729, "LOCAL AT B3 - TYPICAL 3 PLACES - SCALE 5:1", 9, align="center")
    left_points = [
        (x - half, z0), (x - r, z0), (x - r, top - chamfer),
        (x - r + chamfer, top), (x - hole, top),
        (x - hole, shoulder), (x - bore, shoulder), (x - bore, bottom),
        (x - half, bottom), (x - half, bottom + 12),
        (x - half - 3, bottom + 18), (x - half + 3, bottom + 26),
        (x - half, bottom + 32),
    ]
    for points in (left_points, [(2 * x - a, b) for a, b in left_points]):
        p = path_from_points(c, points)
        hatch(c, p, (x - half - 4, bottom, x + half + 4, top), spacing=6)
        c.setLineWidth(VISIBLE)
        c.drawPath(p, stroke=1, fill=0)
    line(c, x, bottom - 8, x, top + 12, dash=CENTER_DASH)
    horizontal_dimension(c, x - hole, x + hole, top, 681,
                         f"3X Ø{plate.base_pod_shank_dia:.2f} +0.20/0 THRU", 10)
    # Callouts touch the chamfer face, counterbore wall and bearing material,
    # leaving the hole diameter witnesses and each other's routes clear.
    leader(c, (x + r - chamfer / 2, top - chamfer / 2),
           (990, 661), (1014, 661),
           [f"3X {plate.base_pedestal_chamfer:.2f} X 45°", "CHAMFER ±0.10"], 10)
    leader(c, (x + bore, (bottom + shoulder) / 2),
           (995, 575), (1014, 575),
           [f"3X COUNTERBORE Ø{plate.base_pod_counterbore_dia:.2f} +0.15/0",
            f"{plate.base_screw_counterbore_depth:.2f} +0.10/0 DEEP",
            "FROM GASKET FACE"], 9.5)
    leader(c, (x - (r + hole) / 2, z0 + 10),
           (796, 660), (772, 660),
           ["BEARING STOCK", f"{plate.base_plate_seat_thickness:.2f} REF; {BEARING_MIN:.2f} MIN"], 9.5)
    leader(c, (x - half + 15, z0), (796, 590), (772, 590),
           ["SHELL FACE", "Z = 0"], 9.5)
    text(c, x, 520, f"GASKET FACE: Z = {-plate.plate_thickness:.2f}", 9, align="center")


def location_table(c):
    left, right, top, row = 710, 1178, 472, 24
    cols = (left, 770, 864, 958, right)
    text(c, left, 488, "FEATURE CENTER LOCATIONS", 10, bold=True)
    entries = [("FEATURE", "X", "Y", "DESCRIPTION")]
    entries += [(label, f"{x:.3f}", f"{y:.3f}", "PEDESTAL / SCREW AXIS")
                for label, x, y in PEDESTALS]
    entries += [("S1", f"{plate.pill_slot_center[0]:.3f}",
                 f"{plate.pill_slot_center[1]:.3f}", "REAR SLOT CENTER")]
    bottom = top - row * len(entries)
    c.setLineWidth(THIN)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    for col in cols[1:-1]:
        line(c, col, bottom, col, top)
    for i, values in enumerate(entries):
        if i:
            line(c, left, top - row * i, right, top - row * i)
        for j, value in enumerate(values):
            text(c, (cols[j] + cols[j + 1]) / 2, top - row * i - 16,
                 value, 9, bold=i == 0 or j == 0, align="center")
    text(c, left, 338, f"X AND Y COORDINATES: ±{LOCATION_TOL:.2f}. FEATURE AXES PARALLEL TO Z.", 8.5)
    text(c, left, 324, "ORIGIN O: SHANK AXIS / ELLIPSE CENTER. +X RIGHT; +Y UP.", 8.5)
    text(c, left, 310, "Z = 0 AT SHELL FACE; +Z TOWARD PEDESTALS.", 8.5)


def finish_notes(c):
    x, y, width, size, leading = 650, 269, 528, 9, 12
    text(c, x, 289, "FABRICATION AND FINISH", 10, bold=True)
    notes = [
        "1. FDM PRINT IN PET-GF15, GASKET FACE DOWN. USE THE SHARED PET-GF PROCESS: 0.20 FIRST LAYER, 0.24 NOMINAL LAYERS; SOLID MATERIAL THROUGH ALL THREE SCREW SEATS.",
        "2. REMOVE ALL THREE COUNTERBORE SUPPORTS, STRINGING AND LOOSE FIBERS. CLEAR THE HOLES AND REAR SLOT; PRESERVE FLAT SCREW SEATS AND LOCATING PEDESTALS.",
        f"3. FINISH FEATURES TO THE STATED SIZES. REMOVE SHARP FLASH. GASKET FACE FREE-STATE GAP: {FACE_GAP_MAX:.2f} MAX UNDER OWN WEIGHT ON A FLAT INSPECTION SURFACE.",
        "4. REAR SLOT S1 CARRIES THE FLAVOR/DRAIN BUNDLE AND FLAT RIBBON. SCREWS, SHELL INSERTS AND GASKET BELONG TO THE FAUCET ASSEMBLY.",
    ]
    for paragraph in notes:
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


def title_block(c):
    left, right, bottom, top = 635, 1197, 27, 143
    c.setLineWidth(0.7)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    line(c, left, 98, right, 98)
    line(c, left, 65, right, 65)
    line(c, 1010, 98, 1010, top)
    text(c, left + 10, 125, "HOME SODA MACHINE", 8)
    text(c, left + 10, 108, "SCULPTED FAUCET PLATE - ABOVE COUNTER", 11.5, bold=True)
    text(c, 1104, 124, "FINISHED PART", 10, bold=True, align="center")
    text(c, 1104, 109, "DESIGN DEFINITION", 9, align="center")
    for col in (866, 1030):
        line(c, col, 65, col, 98)
    for x, label, value in ((645, "MATERIAL", "PET-GF15"),
                            (876, "UNITS", "MILLIMETERS"),
                            (1040, "QUANTITY", "1 PER SCULPTED FAUCET")):
        text(c, x, 87, label, 7)
        text(c, x, 73, value, 9, bold=True)
    fields = ((635, 815, "DRAWING", "FCT-PLT-02"),
              (815, 867, "REV", REVISION),
              (867, 990, "DATE", "2026-10-26"),
              (990, 1113, "SCALE", "AS SHOWN"),
              (1113, 1197, "SHEET", "1 OF 1"))
    for i, (a, b, label, value) in enumerate(fields):
        if i:
            line(c, a, bottom, a, 65)
        text(c, a + 9, 53, label, 7)
        text(c, a + 9, 37, value, 9, bold=True)
    text(c, 47, 127, "HSM-000092", 9, bold=True)
    text(c, 47, 110, "UNLESS OTHERWISE SPECIFIED", 8, bold=True)
    text(c, 47, 96, f"LINEAR ±{GENERAL_TOL:.2f} mm     ANGULAR ±1°", 10)
    text(c, 47, 79, "REF = REFERENCE. DIMENSIONS APPLY AFTER SUPPORT REMOVAL.", 8.5)
    text(c, 47, 60, "DO NOT SCALE. ANSI B / 17 x 11 IN. PRINT AT 100% FOR SCALE.", 8.5)
    text(c, 47, 40, "PART ONLY. ASSEMBLY: FAUCET-SHELL/ASSEMBLY.MD, BASE JOINT.", 8)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Sculpted faucet above-counter mounting plate - engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("FCT-PLT-02 Rev A: finished plate, passages, locating pedestals and recessed screw seats")
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.rect(27, 27, SHEET[0] - 54, SHEET[1] - 54, stroke=1, fill=0)
    plan_view(c)
    front_view(c)
    pedestal_section(c)
    location_table(c)
    finish_notes(c)
    title_block(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
