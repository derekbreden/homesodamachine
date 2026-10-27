"""Evaporator forming drawing: installed centerlines and working tails.

The coil source supplies the laid wrap, interfaces and cut allowance. Its
current tail arcs are below the stock's minimum bend radius. Those intermediate
routes are omitted and explicitly remain a release item; the sheet must not
depict them as a manufacturing pattern. Limits are design requirements, not
measured forming capability.
"""

import math
import sys
from pathlib import Path
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
HW = HERE.parent
sys.path.insert(0, str(HW / "scripts"))
sys.path.insert(0, str(HERE))
import _coil as source
import coil_mandrel as mandrel
from _fabrication_drawing import *

PDF_PATH = HERE / "evaporator-coil-drawing.pdf"
SHEET = (1224, 792)
SCALE = MM / 2
EXIT_TOL = 0.25
WIND_HEIGHT_TOL = 1.0
START_Z_TOL = 0.5
END_CLOCK_TOL = 0.5
CUT_LENGTH = math.ceil(source.cut_length())
CUT_PLUS = 10
MATERIAL_ID = "HSM-000015"
REVIEW_REGIONS = [
    ("elevation", 35, 438, 685, 756),
    ("plan-upper", 35, 265, 685, 452),
    ("plan-lower", 35, 120, 685, 280),
    ("tube-section", 35, 210, 345, 310),
    ("coordinate-table", 700, 531, 1190, 756),
    ("forming-notes", 700, 158, 1190, 532),
    ("title-block", 630, 27, 1197, 146),
    ("footer", 35, 27, 630, 148),
]


def interface(end):
    return source.tail_points(end)[-1]


def end_point(end):
    x, y, z = interface(end)
    return (x - mandrel.stub_protrusion[end], y, z)


def source_tail_minimum(end):
    wire = source._R.route_wire(source.tail_points(end), source.COPPER_BEND)
    return min(edge.radius() for edge in wire.Edges() if edge.geomType() == "CIRCLE")


def elevation(c):
    x0, z0, s = 300, 450, SCALE
    project = lambda p: (x0 + p.y * s, z0 + p.z * s)
    text(c, x0, 741, "INSTALLED ELEVATION - LOOKING ALONG -X", 11, bold=True, align="center")
    text(c, x0, 724, "TUBE CENTERLINES SHOWN - SCALE 1:2", 9, align="center")
    polyline(c, [project(p) for p in source.wrap_points()], 0.9)
    for end in ("inlet", "outlet"):
        _, y, z = interface(end)
        px, py = x0 + y * s, z0 + z * s
        c.setLineWidth(0.75)
        c.circle(px, py, source.TUBE_R * s, stroke=1, fill=0)
        text(c, px, py - 21, "E1 / INLET" if end == "inlet" else "E2 / OUTLET",
             9, bold=True, align="center")
    lo, hi = source.evap_tail_low_z, source.evap_tail_high_z
    x = 125
    # Heights refer to the actual helix-start and helix-end centerline points.
    for z, point in ((lo, source._at(source.AZ_IN, lo)),
                     (hi, source._at(source.AZ_OUT, hi))):
        origin, py = project(point)
        line(c, x - 5, py, origin - 4, py)
    line(c, x, z0 + lo * s, x, z0 + hi * s)
    arrow(c, (x, z0 + lo * s), (x, z0 + hi * s))
    arrow(c, (x, z0 + hi * s), (x, z0 + lo * s))
    c.saveState()
    c.translate(x - 10, z0 + (lo + hi) * s / 2)
    c.rotate(90)
    text(c, 0, 0, f"{source.WIND_HEIGHT:.2f} ±{WIND_HEIGHT_TOL:.1f} AXIAL SPAN", 9.5, align="center")
    c.restoreState()
    leader(c, project(source._at(source.AZ_OUT, hi)), (451, 698), (476, 698),
           ["H2 / OUTLET / UPPER HELIX END", f"Z {hi:.2f} REF"], 9)
    leader(c, project(source._at(source.AZ_IN, lo)), (455, 500), (479, 500),
           ["H1 / INLET / LOWER HELIX END", f"Z {lo:.2f} ±{START_Z_TOL:.1f}"], 9)
    text(c, 455, 624, "9 FULL TURNS + END CLOCKING", 9, bold=True)
    text(c, 455, 608, f"{source.TOTAL_WRAPS:.5f} TURNS REF", 9)
    text(c, 455, 592, f"{source.PITCH:.3f} PITCH REF", 9)
    text(c, 455, 552, "TAIL TRANSITIONS OMITTED", 9, bold=True)
    text(c, 455, 536, "ROUTING RELEASE: SEE NOTE 8", 8.5)
    axes(c, 56, 456, "+Y", "+Z")


def plan(c):
    x0, y0, s = 563, 275, SCALE
    project = lambda p: (x0 + p[0] * s, y0 + p[1] * s)
    text(c, 325, 439, "PLAN - LOOKING ALONG -Z", 11, bold=True, align="center")
    text(c, 325, 423, "TAIL CENTERLINES / WRAP ENVELOPE - SCALE 1:2", 9, align="center")
    c.setLineWidth(0.7)
    c.setDash(CENTER_DASH)
    c.circle(x0, y0, source.WIND_R * s, stroke=1, fill=0)
    c.setDash([])
    # The source's laid path includes the local lift over the reed bridge.
    polyline(c, [(x0+p.x*s, y0+p.y*s) for p in source.wrap_points()], 0.35)
    center(c, x0, y0, 14)
    text(c, x0 + 12, y0 - 15, "O", 9)
    exit_x = interface("inlet")[0]
    px = x0 + exit_x * s
    line(c, px, 142, px, 388, dash=CENTER_DASH)
    text(c, px, 132, f"E PLANE: X {exit_x:.2f}", 8, align="center")
    for end, label, dim_y in (("inlet", "E1 / INLET", 150),
                              ("outlet", "E2 / OUTLET", 400)):
        a, b = project(interface(end)), project(end_point(end))
        line(c, *a, *b, 1.0)
        center(c, *a, 7)
        line(c, b[0], b[1]-5, b[0], b[1]+5, VISIBLE)
        text(c, (a[0]+b[0])/2, b[1]+(12 if end == "inlet" else -18),
             label, 9, bold=True, align="center")
        # The disconnected interface is intentional: no sub-minimum source
        # curve is presented as an accepted tail bend.
        line(c, a[0]+10, a[1], a[0]+25, a[1], dash=CENTER_DASH)
        horizontal_dimension(c, b[0], a[0], b[1], dim_y,
                             f"{mandrel.stub_protrusion[end]:.0f} +5 / -0 WORKING TAIL", 9)
    # Pairwise clocking follows the increasing-azimuth helix, not the minor arc.
    a0, delta = source.AZ_IN, mandrel.tail_ccw_delta
    radius = 31
    pts = [(x0+radius*math.cos(math.radians(a0+delta*i/120)),
            y0+radius*math.sin(math.radians(a0+delta*i/120))) for i in range(121)]
    polyline(c, pts, THIN)
    arrow(c, pts[0], pts[2])
    arrow(c, pts[-1], pts[-3])
    for az, ident, end in ((a0, "H1", "inlet"), (a0+delta, "H2", "outlet")):
        a = math.radians(az)
        line(c, x0+(radius+4)*math.cos(a), y0+(radius+4)*math.sin(a),
             x0+(source.WIND_R*s+8)*math.cos(a), y0+(source.WIND_R*s+8)*math.sin(a))
        xx, yy = project(source.tail_points(end)[0])
        c.setLineWidth(0.7)
        c.circle(xx, yy, 2, stroke=1, fill=0)
        text(c, xx-12, yy-3, ident, 8.5, align="right")
    text(c, 590, 332, f"{delta:.2f}° ±{END_CLOCK_TOL:.1f}° CCW", 8.5, align="center")
    text(c, 590, 317, "INLET TO OUTLET", 7.5, align="center")
    text(c, 585, 222, "NOMINAL WRAP CL", 8.5, align="center")
    text(c, 585, 207, f"Ø{2*source.WIND_R:.2f} REF", 8.5, align="center")
    text(c, 210, 328, "TAIL TRANSITIONS OMITTED", 8.5, bold=True, align="center")
    axes(c, 55, 340, "+X", "+Y")


def tube_section(c):
    x, y, scale = 91, 265, 4 * MM
    outer = source.TUBE_R * scale
    wall = 0.031 * 25.4
    annulus = c.beginPath()
    annulus.circle(x, y, outer)
    annulus.circle(x, y, outer-wall*scale)
    hatch(c, annulus, (x-outer,y-outer,x+outer,y+outer), spacing=6)
    c.setLineWidth(VISIBLE)
    for r in (outer, outer - wall * scale):
        c.circle(x, y, r, stroke=1, fill=0)
    center(c, x, y, outer+6)
    text(c, x, 219, "TUBE SECTION - 4:1", 8, align="center")
    text(c, 144, 280, "1/4 IN OD x 0.031 IN WALL", 8.5)
    text(c, 144, 265, "Ø6.35 x 0.787 WALL REF", 8.5)
    text(c, 144, 250, "ACR COPPER; PURCHASED STOCK", 8)


def coordinate_table(c):
    x, right, top, bottom = 714, 1178, 698, 585
    text(c, x, 741, "INSTALLED CENTERLINE COORDINATES", 11, bold=True)
    text(c, x, 724, "COLD-CORE NATIVE FRAME; SEE NOTE 1", 9)
    cols = (x, 777, 870, 963, 1055, right)
    c.setLineWidth(THIN)
    c.rect(x, bottom, right-x, top-bottom, stroke=1, fill=0)
    for xx in cols[1:-1]:
        line(c, xx, bottom, xx, top)
    for yy in (675, 645, 615):
        line(c, x, yy, right, yy)
    for j, label in enumerate(("POINT", "X", "Y", "Z", "FUNCTION")):
        text(c, (cols[j]+cols[j+1])/2, 683, label, 8, bold=True, align="center")
    data = (("H1", source.tail_points("inlet")[0], "HELIX START"),
            ("H2", source.tail_points("outlet")[0], "HELIX END"),
            ("E1/E2", None, "EXITS"))
    for yy, (ident, point, description) in zip((655,625,595), data):
        values = ((ident, f"{point[0]:.2f}", f"{point[1]:.2f}", f"{point[2]:.3f}", description)
                  if point else (ident, f"{interface('inlet')[0]:.2f}", "-77.50 / +77.50", f"{interface('inlet')[2]:.3f}", description))
        for j, value in enumerate(values):
            text(c, (cols[j]+cols[j+1])/2, yy, value, 8.1 if j!=2 else 7.6, align="center")
    text(c, x, 567, "E1 = -Y / INLET; E2 = +Y / OUTLET. EXIT Y AND Z: ±0.25.", 8.5, bold=True)
    text(c, x, 552, "H1/H2 X,Y ARE REF; SPAN / CLOCKING CONTROL THE WRAP.", 8.3)
    text(c, x, 537, "NOMINAL SHELL PORT STATIONS: X -141.50 REF, 2 mm INBOARD OF E.", 8.1)


def requirements(c):
    text(c, 714, 512, "FORMING AND FINISHED-STATE REQUIREMENTS", 10, bold=True)
    items = [
        "1. One continuous length of GOORY 1/4-inch OD x 0.031-inch wall ACR copper. O is the carbonator axis in X,Y; Z=0 is the cold-core shell base. Dimensions describe the coil fitted to the vessel and bridge, before foam and final refrigeration tie-in.",
        f"2. Cut stock {CUT_LENGTH} +{CUT_PLUS}/-0. Nominal laid wrap {source.wrap_length():.1f} REF plus inlet/outlet allowances {mandrel.stub_allowance['inlet']:.1f}/{mandrel.stub_allowance['outlet']:.1f} REF. Preserve each working tail's stated length at E; trim only during refrigeration fit-up.",
        f"3. Use the Ø{mandrel.mandrel_od:.0f} winding mandrel as the forming aid; adjust winding and tails to the INSTALLED dimensions. The mandrel is not the acceptance gauge. Keep nine complete turns plus the stated CCW end clocking, rising from inlet to outlet. Pitch is derived from axial span and turns.",
        f"4. Fit the nominal Ø{2*source.carbonator_outer_radius:.0f} vessel with foil thermal interface; maintain contact around the available wrap. Ease locally over the reed bridge: {source.BRIDGE_LIFT:.2f} REF radial lift. Do not compress reeds or force the copper through the bridge. Free-state diameter / springback is not a controlled finished dimension.",
        f"5. Blend helix-to-tail transitions smoothly; all tail bends R{source.COPPER_BEND:.1f} MIN to tube centerline. Both exit axes parallel to -X within 1°. Exit centers at E1/E2 within the table limits; confirm passage through the actual shell feed-throughs before foam.",
        "6. Finished tube must have an open bore, no kink, crease or visible flattening. Square-cut and deburr both open ends; keep the bore clean and capped until tie-in. Retain clearance to reservoirs, reeds and other lines in the assembled core. Inspect before foam conceals the coil.",
        "7. The working tails belong to the refrigeration fit-up; braze joints, heat protection, leak checks and final charge follow assembly/refrigerant-loop.md. Confirm forming capability and installed fit on the first article.",
        f"8. TAIL ROUTE RELEASE ITEM: current layout arcs reach R{source_tail_minimum('inlet'):.2f} inlet / R{source_tail_minimum('outlet'):.2f} outlet REF, below the required minimum. Intermediate routes are omitted. Establish compliant transitions and assembled clearances, then verify a formed first article before release.",
    ]
    return paragraphs(c, 714, 492, items, 464, size=9, leading=12, gap=6)


def build_pdf(path):
    c = canvas.Canvas(str(path), pagesize=SHEET, invariant=1, pageCompression=1)
    c.setTitle("Evaporator coil - engineering drawing")
    c.setAuthor("Home Soda Machine / Codex")
    c.setSubject("EVAP-01 Rev A: installed coil centerlines, winding, working tails and forming acceptance")
    frame(c, SHEET)
    elevation(c)
    plan(c)
    tube_section(c)
    coordinate_table(c)
    requirements(c)
    title_block(c, SHEET, "EVAPORATOR COIL", "EVAP-01", "ACR COPPER TUBE",
                "1 PER COLD CORE", MATERIAL_ID, ("FORMING DEFINITION", "TAIL ROUTE PENDING"))
    c.showPage()
    c.save()


if __name__ == "__main__":
    export_pdf(build_pdf, str(PDF_PATH))
    print(f"Exported: {PDF_PATH}")
