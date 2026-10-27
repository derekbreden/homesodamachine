"""Water-inlet jet elbow assembly: purchased fitting plus welded drilled cap.

The exterior envelope and local tip section use the same parametric reference
fitting as the cold core. It is a layout stand-in, not measured vendor detail. The drawing
identifies the purchased item and controls assembly alignment and acceptance;
cap dimensions belong to JET-CAP-01. Grey bands show the required fusion path,
not a predicted or dimensioned weld profile. Measured fit and weld qualification
remain explicit release items under assembly/water-inlet-jet.md.

Run with tools/cad-venv/bin/python. No machine geometry or weld recipe changes.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

HERE = Path(__file__).resolve().parent
HW = HERE.parent
for folder in (HERE, HW / "scripts", HW / "printed-parts/cold-core",
               HW / "cut-parts/carbonation/endcaps-circular"):
    sys.path.insert(0, str(folder))
from _cadq_export import export_pdf
from endcap_circular_drawing import (
    line, text, arrow, leader, circular_leader, center, horizontal_dimension,
    path_from_points, hatch, cutting_plane_ends, VISIBLE, THIN, CENTER_DASH,
)
import _carbonator as carbonator
import _fittings as fitting
import water_inlet_jet_cap_drawing as cap
from _water_inlet_jet import JET_CAP_D, JET_CAP_T, JET_PASSAGE_D

PDF_PATH = HERE / "water-inlet-jet-elbow-drawing.pdf"
SHEET = (17 * 72, 11 * 72)
PT_PER_MM = 72 / 25.4
SCALE = 2 * PT_PER_MM
CX, SEAT = 300, 650
CAP_OFFSET_MAX = 0.10
JET_OFFSET_MAX = 0.20
REVISION = "A"
MATERIAL_ID = "HSM-000338"
CORNER_Z = -carbonator.ELBOW_AXIS_OFFSET - fitting.ELBOW_MALE_LEN

REVIEW_REGIONS = [
    ("assembly-upper", 35, 565, 665, 756),
    ("assembly-lower", 155, 407, 687, 575),
    ("exit-view", 175, 195, 673, 377),
    ("joint-detail", 681, 519, 1191, 756),
    ("assembly-parts", 700, 390, 1190, 520),
    ("requirements", 700, 166, 1190, 390),
    ("release-and-footer", 35, 27, 629, 178),
    ("title-block", 630, 27, 1197, 146),
]


def reference_parts():
    """Build a canonical reference: male tip Z=0, outlet +X.

    Hex clocking in the installed layout is not a purchased-part requirement.
    This view uses the reference builder's canonical orientation.
    """
    body, _ = fitting.street_elbow(
        corner=(0, 0, CORNER_Z), up=(0, 0, 1), out=(1, 0, 0),
        up_leg=carbonator.ELBOW_AXIS_OFFSET, male_len=fitting.ELBOW_MALE_LEN)
    blank = cq.Solid.makeCylinder(JET_CAP_D / 2, JET_CAP_T)
    passage = cq.Solid.makeCylinder(JET_PASSAGE_D / 2, JET_CAP_T)
    return body, blank.cut(passage)


def section_material(c, points, *, reverse=False):
    p = path_from_points(c, points)
    xs, ys = zip(*points)
    if reverse:
        low, high = min(ys), max(ys)
        c.saveState()
        c.translate(0, low + high)
        c.scale(1, -1)
        mirrored = path_from_points(c, [(x, low + high - y) for x, y in points])
        hatch(c, mirrored, (min(xs), low, max(xs), high), spacing=6)
        c.restoreState()
    else:
        hatch(c, p, (min(xs), min(ys), max(xs), max(ys)), spacing=6)
    c.setLineWidth(VISIBLE)
    c.drawPath(p, stroke=1, fill=0)


def fusion_bands(c, x, y, scale, *, half_height):
    """Diagrammatic continuous fusion to the inside root, on both cut lands."""
    inside, outside = fitting.ELBOW_BORE / 2, JET_CAP_D / 2
    c.setFillColorRGB(0.78, 0.78, 0.78)
    for sign in (-1, 1):
        a, b = sorted((x + sign * inside * scale, x + sign * outside * scale))
        c.rect(a, y - half_height, b - a, 2 * half_height, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)


def balloon(c, value, at, target):
    radius = 10
    dx, dy = target[0] - at[0], target[1] - at[1]
    distance = math.hypot(dx, dy)
    start = (at[0] + radius * dx / distance, at[1] + radius * dy / distance)
    line(c, *start, *target)
    arrow(c, target, start)
    c.setLineWidth(0.6)
    c.circle(*at, radius, stroke=1, fill=0)
    text(c, at[0], at[1] - 3, str(value), 9, bold=True, align="center")


def assembly_view(c, body):
    text(c, CX, 735, "WATER-INLET JET ELBOW", 12, bold=True, align="center")
    text(c, CX, 718, "SIDE VIEW - SCALE 2:1 - HIDDEN DETAIL OMITTED", 9, align="center")
    r = fitting.ELBOW_HEX_AF / math.sqrt(3)
    male_r, male_base, out = fitting.ELBOW_MALE_R, -fitting.ELBOW_MALE_LEN, fitting.ELBOW_LEG
    # The two barstock-leg envelopes and male stub, viewed from -Y. Internal
    # turning geometry is deliberately left to the actual purchased fitting.
    outline = [(-r, male_base), (-r, CORNER_Z), (0, CORNER_Z),
               (0, CORNER_Z-r), (out, CORNER_Z-r), (out, CORNER_Z+r),
               (r, CORNER_Z+r), (r, male_base), (male_r, male_base),
               (male_r, 0), (-male_r, 0), (-male_r, male_base)]
    p = path_from_points(c, [(CX+x*SCALE, SEAT+z*SCALE) for x,z in outline])
    c.setLineWidth(VISIBLE)
    c.drawPath(p, stroke=1, fill=0)
    # Visible flat-to-angle edges of the hexagonal body, not thread graphics.
    for x, end_z in ((-r/2, CORNER_Z), (r/2, CORNER_Z+r)):
        line(c, CX+x*SCALE, SEAT+male_base*SCALE,
             CX+x*SCALE, SEAT+end_z*SCALE, THIN)
    line(c, CX+r*SCALE, SEAT+(CORNER_Z+r/2)*SCALE,
         CX+out*SCALE, SEAT+(CORNER_Z+r/2)*SCALE, THIN)
    cap_r = JET_CAP_D*SCALE/2
    c.setLineWidth(VISIBLE)
    c.rect(CX-cap_r, SEAT, 2*cap_r, JET_CAP_T*SCALE, stroke=1, fill=0)
    left = r
    bottom = body.BoundingBox().zmin
    line(c, CX, SEAT + bottom * SCALE - 12, CX,
         SEAT + JET_CAP_T * SCALE + 14, dash=CENTER_DASH)
    axis_y = SEAT + CORNER_Z * SCALE
    line(c, CX - 12, axis_y, CX + fitting.ELBOW_LEG * SCALE + 15,
         axis_y, dash=CENTER_DASH)
    leader(c, (CX - JET_CAP_D * SCALE / 2, SEAT),
           (207, 692), (184, 692),
           ["W1 - CONTINUOUS 360° WELD", "FULL WETTED-ROOT FUSION"], 9.5)
    leader(c, (CX + fitting.ELBOW_MALE_R * SCALE, SEAT - 3 * SCALE),
           (452, 674), (473, 674),
           ["1/4-18 NPT MALE", "AS RECEIVED"], 9.5)
    leader(c, (CX + fitting.ELBOW_LEG * SCALE,
               axis_y + fitting.SOCKET_R * SCALE),
           (500, 555), (522, 555),
           ["1/4-18 NPT FEMALE", "AS RECEIVED"], 9.5)
    balloon(c, 1, (177, 513), (CX - left * SCALE, SEAT - 18 * SCALE))
    balloon(c, 2, (370, 697), (CX + 10, SEAT + JET_CAP_T * SCALE))


def exit_view(c):
    x, y = CX, 270
    r = fitting.ELBOW_HEX_AF / math.sqrt(3)
    pts = [(x + r * SCALE * math.cos(math.radians(60 * i)),
            y + r * SCALE * math.sin(math.radians(60 * i))) for i in range(6)]
    text(c, x, 360, "JET EXIT END VIEW", 12, bold=True, align="center")
    text(c, x, 344, "LOOKING ALONG MALE PORT AXIS - SCALE 2:1", 8.5, align="center")
    c.setLineWidth(VISIBLE)
    c.drawPath(path_from_points(c, pts), stroke=1, fill=0)
    # The other hex leg is lower than the male leg in this projection.
    half_w = fitting.ELBOW_HEX_AF * SCALE / 2
    upper_x = x + r * SCALE / 2
    end_x = x + fitting.ELBOW_LEG * SCALE
    line(c, upper_x, y + half_w, end_x, y + half_w, VISIBLE)
    line(c, end_x, y + half_w, end_x, y - half_w, VISIBLE)
    line(c, end_x, y - half_w, upper_x, y - half_w, VISIBLE)
    line(c, x + r * SCALE, y, end_x, y, VISIBLE)
    for radius in (fitting.ELBOW_MALE_R, JET_CAP_D / 2, JET_PASSAGE_D / 2):
        c.setLineWidth(VISIBLE)
        c.circle(x, y, radius * SCALE, stroke=1, fill=0)
    center(c, x, y, 14)
    left, right = x - r * SCALE - 20, end_x + 20
    line(c, left + 14, y, right - 14, y, dash=CENTER_DASH)
    cutting_plane_ends(c, left, right, y, "A", rise=20)
    circular_leader(c, (x, y), JET_PASSAGE_D * SCALE / 2,
                    (485, 355), (505, 355),
                    ["JET BORE: JET-CAP-01", "RETAIN LIMITS AFTER WELD"], 9.5)
    text(c, x + 45, 207, "FITTING BODY AND THREAD PROFILES ARE SCHEMATIC.", 8, align="center")


def joint_detail(c):
    x, seat, s = 945, 600, 5 * PT_PER_MM
    cr, hole = JET_CAP_D * s / 2, JET_PASSAGE_D * s / 2
    inner, outer = fitting.ELBOW_BORE * s / 2, fitting.ELBOW_MALE_R * s
    top, bottom = seat + JET_CAP_T * s, 550
    text(c, x, 735, "SECTION A-A - CAP-TO-ELBOW JOINT", 11, bold=True, align="center")
    text(c, x, 718, "LOCAL AT MALE TIP - SCALE 5:1", 9, align="center")
    for a, b in ((x - outer, x - inner), (x + inner, x + outer)):
        # Broken lower ends crop only the purchased fitting, not the cap.
        points = [(a, seat), (b, seat), (b, bottom + 5),
                  (b - (b - a) / 3, bottom + 8),
                  (a + (b - a) / 3, bottom + 2), (a, bottom + 5)]
        section_material(c, points)
    for a, b in ((x - cr, x - hole), (x + hole, x + cr)):
        section_material(c, [(a, seat), (b, seat), (b, top), (a, top)], reverse=True)
    fusion_bands(c, x, seat, s, half_height=3)
    line(c, x, bottom - 3, x, top + 13, dash=CENTER_DASH)
    horizontal_dimension(c, x - hole, x + hole, top, 670,
                         f"Ø{JET_PASSAGE_D:.4f} REF", 9.5)
    dim_x = 1065
    for y in (seat, top):
        line(c, x + cr + 4, y, dim_x + 5, y)
    line(c, dim_x, seat, dim_x, top)
    arrow(c, (dim_x, seat), (dim_x, top))
    arrow(c, (dim_x, top), (dim_x, seat))
    text(c, dim_x + 9, (seat + top) / 2 - 3,
         f"{JET_CAP_T:.2f} REF", 9.5)
    leader(c, (x - inner, seat), (807, 650), (780, 650),
           ["WETTED ROOT", "FULLY FUSED"], 9.5)
    leader(c, (x + (inner + cr) / 2, seat), (1070, 555), (1100, 555),
           ["W1 / 360°", "SEE NOTE 2"], 9.5)
    text(c, x, 529, "GREY BAND: REQUIRED FUSION PATH; WELD PROFILE DIAGRAMMATIC.", 7.7, align="center")


def parts_list(c):
    left, right, top = 710, 1178, 485
    cols = (left, 744, 779, 876, right)
    text(c, left, 503, "PARTS AT THIS WELD", 10, bold=True)
    c.setLineWidth(THIN)
    c.rect(left, 399, right - left, top - 399, stroke=1, fill=0)
    for col in cols[1:-1]:
        line(c, col, 399, col, top)
    line(c, left, 463, right, 463)
    line(c, left, 431, right, 431)
    for j, label in enumerate(("ITEM", "QTY", "MATERIAL", "DESCRIPTION / DEFINITION")):
        text(c, (cols[j] + cols[j + 1]) / 2, 471, label, 7.8, bold=True, align="center")
    for y, values, more in ((450, ("1", "1", "HSM-000010", "TAISHER 316L STREET ELBOW, 1/4 NPT M X F"), "ORDER ID B0CZ38MYL1; AS RECEIVED"),
                            (418, ("2", "1", "HSM-000011", "316 STAINLESS DRILLED CAP; JET-CAP-01"), "FINISHED COMPONENT BEFORE WELDING")):
        for j, value in enumerate(values):
            text(c, cols[j] + 5, y, value, 7.9, bold=j == 0)
        text(c, cols[3] + 5, y - 12, more, 7.7)


def requirements(c):
    x, y, width, size = 710, 355, 468, 8.7
    text(c, x, 375, "ASSEMBLY AND ACCEPTANCE", 10, bold=True)
    paragraphs = [
        "1. Assemble items 1 and 2. The purchased elbow controls fitting geometry. Body, bores and thread profiles are reference representations. Cap dimensions: JET-CAP-01.",
        "2. W1: continuous 360° weld. Fuse the complete cap-to-tip interface through to the wetted bore-side root. Preserve the open jet. The grey band shows the required fusion path, not a weld size. Use the accepted small-joint coupon procedure; filler, if used: ER316L.",
        f"3. Cap OD axis within {CAP_OFFSET_MAX:.2f} radial of male-port bore axis; pre-weld seating gap {cap.FACE_GAP_MAX:.2f} MAX. Completed jet axis within {JET_OFFSET_MAX:.2f} radial of that bore axis and normal to the elbow tip within {cap.AXIS_ANGLE_MAX:g}°. Retain JET-CAP-01 passage limits after welding.",
        "4. Verify both threads after welding. Trial-fit through the loose END-CAP-01 plate at Port 2; the welded envelope must clear the actual tapped port and the jet exit must project into headspace. Record make-up depth, clocking and projection.",
        "5. Inspect the cap and open passage; remove loose metal and cutting fluid. Flush, clean, passivate and flow-check the completed elbow per assembly/water-inlet-jet.md. Flow must emerge through the jet passage only.",
        "6. Record actual bore/tip/land, cap overlap, maximum welded OD and port clearance. Qualify the same-material joint by sectioned-root inspection; retain settings and coupon identity. Numerical weld settings and flow acceptance require that qualification.",
    ]
    for paragraph in paragraphs:
        row = ""
        for word in paragraph.split():
            trial = (row + " " + word).strip()
            if row and stringWidth(trial, "Helvetica", size) > width:
                text(c, x, y, row, size)
                y -= 11
                row = word
            else:
                row = trial
        text(c, x, y, row, size)
        y -= 16
    return y


def title_block(c):
    left, right = 635, 1197
    c.setLineWidth(0.7)
    c.rect(left, 27, right - left, 116, stroke=1, fill=0)
    for y in (98, 65):
        line(c, left, y, right, y)
    line(c, 1010, 98, 1010, 143)
    text(c, 645, 126, "HOME SODA MACHINE", 8)
    text(c, 645, 108, "CARBONATOR WATER-INLET JET ELBOW", 11.5, bold=True)
    text(c, 1104, 125, "ASSEMBLY DEFINITION", 8.5, bold=True, align="center")
    text(c, 1104, 110, "QUALIFICATION PENDING", 8.5, align="center")
    for col in (866, 1030):
        line(c, col, 65, col, 98)
    for x, label, value in ((645, "MATERIAL", "SEE PARTS LIST"),
                            (876, "UNITS", "MILLIMETERS"),
                            (1040, "QUANTITY", "1 PER CARBONATOR")):
        text(c, x, 87, label, 7)
        text(c, x, 73, value, 8.5, bold=True)
    fields = ((635, 815, "DRAWING", "JET-ELB-01"), (815, 867, "REV", REVISION),
              (867, 990, "DATE", "2026-10-26"), (990, 1113, "SCALE", "AS SHOWN"),
              (1113, 1197, "SHEET", "1 OF 1"))
    for i, (a, b, label, value) in enumerate(fields):
        if i:
            line(c, a, 27, a, 65)
        text(c, a + 9, 53, label, 7)
        text(c, a + 9, 37, value, 9, bold=True)
    text(c, 47, 127, MATERIAL_ID, 9, bold=True)
    text(c, 47, 110, "mm DIMENSIONS GOVERN. REF = REFERENCE.", 8.5)
    text(c, 47, 94, "PURCHASED FITTING CONTROLS ITS OWN GEOMETRY.", 8.5)
    text(c, 47, 74, "DO NOT SCALE. ANSI B / 17 x 11 IN. PRINT AT 100% FOR SCALE.", 8.5)
    text(c, 47, 48, "CAP COMPONENT: JET-CAP-01. ASSEMBLY: WATER-INLET-JET.MD.", 8)


def build_pdf(path):
    body, jet = reference_parts()
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Carbonator water-inlet jet elbow - assembly engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("JET-ELB-01 Rev A: welded cap and TAISHER street elbow, full-root fusion and finished assembly acceptance")
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.rect(27, 27, SHEET[0] - 54, SHEET[1] - 54, stroke=1, fill=0)
    assembly_view(c, body)
    exit_view(c)
    joint_detail(c)
    parts_list(c)
    requirements(c)
    text(c, 47, 164, "RELEASE ITEMS: MEASURED FIT / LAND AND PORT CLEARANCE; QUALIFIED SMALL-JOINT WELD; FLOW ACCEPTANCE.", 8.5, bold=True)
    title_block(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
