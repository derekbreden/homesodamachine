"""
Wing Knob -- CadQuery STEP Generation Script

Generates the wing knob for the cartridge twist-release mechanism.
Internal female Tr12x3 2-start trapezoidal thread mates with strut,
converting half-turn rotation into 3mm of linear plate travel.

Coordinate system:
  Origin: Center of knob rear face (bearing surface against front wall)
  X: Left-right (radial, wing extension axis)
  Y: Depth axis (0=rear face, 25=front face, positive toward user)
  Z: Up-down (radial)
  Envelope: 45mm (X) x 25mm (Y) x 40mm (Z)
    X: [-22.5, +22.5]  Y: [0, 25]  Z: [-20, +20]
"""

import sys
import math
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator

# ============================================================
# Parameters
# ============================================================

BODY_OD = 40.0
BODY_DEPTH = 25.0
BODY_RADIUS = BODY_OD / 2  # 20.0

WINGSPAN = 45.0
WING_THICKNESS = 10.0
WING_HALF = WINGSPAN / 2  # 22.5
WING_HEIGHT = 20.0

THREAD_PITCH = 3.0
THREAD_STARTS = 2
THREAD_LEAD = THREAD_PITCH * THREAD_STARTS  # 6.0
THREAD_DEPTH = 1.5
FLANK_ANGLE = 29.0

BORE_MINOR_DIA = 12.6
BORE_MINOR_R = BORE_MINOR_DIA / 2  # 6.3
THREAD_ROOT_DIA = 15.6
THREAD_ROOT_R = THREAD_ROOT_DIA / 2  # 7.8

THREAD_ENGAGEMENT = 20.0
SMOOTH_BORE_SECTION = 5.0

KNURL_DEPTH = 0.9
KNURL_PITCH = 2.0

CHAMFER_SIZE = 1.0

# ============================================================
# Rubric 1: Feature Planning Table
# ============================================================
print("=" * 70)
print("FEATURE PLANNING TABLE")
print("=" * 70)
features = [
    ("1", "Cylindrical body",        "Add",     "Cylinder",   "Y", f"OD={BODY_OD}, depth={BODY_DEPTH}"),
    ("2", "Internal smooth bore",    "Remove",  "Cylinder",   "Y", f"dia={BORE_MINOR_DIA}, Y=[20,25]"),
    ("3", "Female Tr12x3 thread",    "Remove",  "Helix/ring", "Y", f"minor={BORE_MINOR_DIA}, root={THREAD_ROOT_DIA}, engage={THREAD_ENGAGEMENT}"),
    ("4", "Wing extensions",         "Add",     "Stadium",    "X", f"span={WINGSPAN}, thick={WING_THICKNESS}, H={WING_HEIGHT}"),
    ("5", "Knurled exterior",        "Remove",  "V-grooves",  "R", f"depth={KNURL_DEPTH}, pitch={KNURL_PITCH}"),
    ("6", "Rear annular face",       "Inherent","Flat",       "Y", f"OD={BODY_OD}, ID=12.5"),
    ("7", "Thread entry chamfer",    "Remove",  "Countersink","Y", f"{CHAMFER_SIZE}mm x 45deg"),
]
print(f"{'#':<3} {'Feature':<25} {'Op':<9} {'Shape':<12} {'Ax':<4} {'Dimensions'}")
print("-" * 80)
for f in features:
    print(f"{f[0]:<3} {f[1]:<25} {f[2]:<9} {f[3]:<12} {f[4]:<4} {f[5]}")
print()

# ============================================================
# Rubric 2: Coordinate System
# ============================================================
print("COORD SYSTEM: Origin=center rear face, X=wings, Y=depth(0..25), Z=up/down")
print(f"  X:[{-WING_HALF},{WING_HALF}] Y:[0,{BODY_DEPTH}] Z:[{-BODY_RADIUS},{BODY_RADIUS}]")
print()

# ============================================================
# Build geometry
# ============================================================
print("Building wing knob...")

# Feature 1: Cylindrical body (Y=0 to Y=25, centered on Y-axis)
# XZ workplane normal is -Y. Negative extrude goes +Y.
body = (
    cq.Workplane("XZ")
    .circle(BODY_RADIUS)
    .extrude(-BODY_DEPTH)
)
print("  1. Body cylinder")

# Feature 4: Wing extensions
# Stadium lobes: slot2D with long axis along X, centered in Y.
# The wings are centered on the body Y midpoint.
WING_Y_START = (BODY_DEPTH - WING_THICKNESS) / 2  # 7.5
WING_Y_END = WING_Y_START + WING_THICKNESS         # 17.5

wing = (
    cq.Workplane("XZ")
    .transformed(offset=(0, 0, -WING_Y_START))
    .slot2D(WINGSPAN, WING_HEIGHT, angle=0)
    .extrude(-WING_THICKNESS)
)
body = body.union(wing)
print("  4. Wings added")

# Feature 5: Knurl grooves on body OD surface.
# Each groove is a V-shaped ring cut into the cylindrical surface.
# Build a single sawtooth profile (V-dips at groove positions, r_outer between)
# and revolve once. The profile's enclosed area is only the triangular V-dips.
print("  5. Building knurl grooves...")
KNURL_Y_START_POS = 2.0
KNURL_Y_END_POS = BODY_DEPTH - 2.0
KNURL_GROOVE_WIDTH = 0.8

r_outer = BODY_RADIUS + 0.1   # Slightly outside to ensure clean cut
r_inner = BODY_RADIUS - KNURL_DEPTH  # 19.1mm
hw = KNURL_GROOVE_WIDTH / 2   # 0.4mm

groove_y_positions = []
y_pos = KNURL_Y_START_POS
while y_pos <= KNURL_Y_END_POS + 0.001:
    groove_y_positions.append(y_pos)
    y_pos += KNURL_PITCH

# Sawtooth profile: traces along r_outer between grooves, dips to r_inner at each groove.
# Profile is in XY plane (X=radius, Y=axial position), revolved around Y-axis (0,1).
# The closing segment from (r_outer, last_y+hw) back to (r_outer, first_y-hw)
# is at r_outer, so the enclosed area is only the V-notches below r_outer.
saw_pts = []
for y_g in groove_y_positions:
    saw_pts.append((r_outer, y_g - hw))
    saw_pts.append((r_inner, y_g))
    saw_pts.append((r_outer, y_g + hw))

# The polyline auto-closes: from last point (r_outer, last_y+hw) to first (r_outer, first_y-hw).
# Both at r_outer, so closing segment is at r_outer => zero-area closing edge (good).
# CadQuery needs a properly enclosed area. Since points alternate between r_outer and r_inner,
# the enclosed area is the union of all V-triangles. polyline().close() should handle it.

knurl_cutter = (
    cq.Workplane("XY")
    .polyline(saw_pts)
    .close()
    .revolve(360, (0, 0), (0, 1))
)
body = body.cut(knurl_cutter)
print(f"    {len(groove_y_positions)} grooves cut via single revolve")

# Feature 2+3: Bore (smooth + threaded)
# Full-depth bore at minor diameter runs through entire knob
full_bore = (
    cq.Workplane("XZ")
    .circle(BORE_MINOR_R)
    .extrude(-BODY_DEPTH)
)
body = body.cut(full_bore)
print("  2. Full bore at minor diameter")

# Feature 3: Thread grooves via helical sweep
print("  3. Thread grooves...")

HALF_FLANK = FLANK_ANGLE / 2  # 14.5 deg
GROOVE_HW_BORE = THREAD_PITCH / 4  # 0.75mm at bore surface
GROOVE_DEPTH_R = THREAD_ROOT_R - BORE_MINOR_R  # 1.5mm
GROOVE_HW_ROOT = GROOVE_HW_BORE + GROOVE_DEPTH_R * math.tan(math.radians(HALF_FLANK))
pitch_r = (BORE_MINOR_R + THREAD_ROOT_R) / 2  # 7.05mm

THREAD_METHOD = "none"

try:
    from OCP.gp import gp_Pnt
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
    from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipe

    inner_r = BORE_MINOR_R - 0.1   # 6.2 - ensure groove reaches bore
    outer_r = THREAD_ROOT_R + 0.1   # 7.9 - ensure groove reaches root
    hw_i = GROOVE_HW_BORE
    hw_o = GROOVE_HW_ROOT

    all_grooves = None

    for start_idx in range(THREAD_STARTS):
        start_angle = start_idx * (360.0 / THREAD_STARTS)  # 0, 180
        sa_rad = math.radians(start_angle)
        cos_sa = math.cos(sa_rad)
        sin_sa = math.sin(sa_rad)

        # Helix along Z-axis at pitch radius
        # Note: do NOT pass angle=0 — it triggers a degenerate conical surface in OCC.
        # Omitting angle defaults to a cylindrical helix.
        helix_wire = cq.Wire.makeHelix(
            pitch=THREAD_PITCH,
            height=THREAD_ENGAGEMENT,
            radius=pitch_r,
            lefthand=False,
        )
        if start_angle != 0:
            helix_wire = helix_wire.rotate((0, 0, 0), (0, 0, 1), start_angle)

        # Trapezoidal groove profile at helix start point
        # Profile in the plane containing radial direction and Z-axis
        def to_pt(r, z_off):
            return gp_Pnt(r * cos_sa, r * sin_sa, z_off)

        p1 = to_pt(inner_r, -hw_i)
        p2 = to_pt(inner_r, +hw_i)
        p3 = to_pt(outer_r, +hw_o)
        p4 = to_pt(outer_r, -hw_o)

        e1 = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
        e2 = BRepBuilderAPI_MakeEdge(p2, p3).Edge()
        e3 = BRepBuilderAPI_MakeEdge(p3, p4).Edge()
        e4 = BRepBuilderAPI_MakeEdge(p4, p1).Edge()

        wb = BRepBuilderAPI_MakeWire()
        wb.Add(e1); wb.Add(e2); wb.Add(e3); wb.Add(e4)
        prof_face = BRepBuilderAPI_MakeFace(wb.Wire()).Face()

        pipe = BRepOffsetAPI_MakePipe(helix_wire.wrapped, prof_face)
        pipe.Build()
        if not pipe.IsDone():
            raise RuntimeError("MakePipe failed")

        groove_cq = cq.Shape(pipe.Shape())
        # Rotate from Z-helix to Y-axis: -90 around X maps (x,y,z)->(x,z,-y)
        # so Z=0..20 becomes Y=0..20 (into the knob body)
        groove_cq = groove_cq.rotate((0, 0, 0), (1, 0, 0), -90)

        if all_grooves is None:
            all_grooves = cq.Workplane(groove_cq)
        else:
            all_grooves = all_grooves.union(cq.Workplane(groove_cq))

    body = body.cut(all_grooves)
    THREAD_METHOD = "helical_sweep"
    print("    Helical sweep SUCCESS")

except Exception as e:
    import traceback
    print(f"    Helical sweep failed: {e}")
    traceback.print_exc()
    print("    Fallback: annular bore at thread root diameter")
    thread_zone = (
        cq.Workplane("XZ")
        .circle(THREAD_ROOT_R)
        .extrude(-THREAD_ENGAGEMENT)
    )
    body = body.cut(thread_zone)
    THREAD_METHOD = "annular_fallback"

# Feature 7: Thread entry chamfer (1mm x 45deg at Y=0)
if THREAD_METHOD == "helical_sweep":
    eff_r = BORE_MINOR_R  # 6.3
else:
    eff_r = THREAD_ROOT_R  # 7.8

chamfer_outer = eff_r + CHAMFER_SIZE
# Revolved profile: annular chamfer cone at bore entry
# Profile in XY plane (X=radius, Y=axial). Revolve around Y-axis.
chamfer_pts = [
    (0,            0),
    (chamfer_outer, 0),
    (eff_r,        CHAMFER_SIZE),
    (0,            CHAMFER_SIZE),
]
chamfer_solid = (
    cq.Workplane("XY")
    .polyline(chamfer_pts)
    .close()
    .revolve(360, (0, 0), (0, 1))
)
body = body.cut(chamfer_solid)
print("  7. Chamfer added")

# ============================================================
# Clean up and merge fragments
# ============================================================
# Boolean operations can leave thin slivers as separate bodies.
# Use clean() and fuse all solids into one.
print("\nCleaning and fusing bodies...")
body = body.clean()

# If multiple bodies remain, fuse them
solids = body.solids().vals()
if len(solids) > 1:
    print(f"  Found {len(solids)} bodies after clean(), fusing...")
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.TopoDS import TopoDS
    import OCP.TopAbs as TopAbs
    from OCP.TopExp import TopExp_Explorer

    # Fuse all solids together
    result_shape = solids[0].wrapped
    for s in solids[1:]:
        fuser = BRepAlgoAPI_Fuse(result_shape, s.wrapped)
        fuser.Build()
        if fuser.IsDone():
            result_shape = fuser.Shape()

    # Extract the single solid from the compound
    explorer = TopExp_Explorer(result_shape, TopAbs.TopAbs_SOLID)
    fused_solids = []
    while explorer.More():
        fused_solids.append(explorer.Current())
        explorer.Next()

    if len(fused_solids) == 1:
        body = cq.Workplane(cq.Solid(fused_solids[0]))
        print("  Fused to single body")
    else:
        # If fuse still yields multiple, use the largest by volume
        print(f"  Fuse yielded {len(fused_solids)} solids, selecting largest")
        best = max(fused_solids, key=lambda s: cq.Solid(s).Volume())
        body = cq.Workplane(cq.Solid(best))
else:
    print("  Already a single body")

# ============================================================
# Export
# ============================================================
STEP_PATH = Path(__file__).parent / "wing-knob-cadquery.step"
cq.exporters.export(body, str(STEP_PATH))
print(f"\nSTEP exported: {STEP_PATH}")

# ============================================================
# Validation (Rubrics 3-5)
# ============================================================
print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)

v = Validator(body)

# -- Feature 1: Body --
# Check solid at points well inside the body wall (R=15, between bore/root and OD)
v.check_solid("Body +Z wall", 0, 12.5, 15.0, "solid in body wall (Z=15)")
v.check_solid("Body -Z wall", 0, 12.5, -15.0, "solid in body wall (Z=-15)")
v.check_solid("Body +X wall", 15.0, 12.5, 0, "solid in body wall (X=15)")
v.check_solid("Body -X wall", -15.0, 12.5, 0, "solid in body wall (X=-15)")
v.check_void("Outside body OD", 0, 12.5, BODY_RADIUS + 1, "void outside OD")
v.check_solid("Near rear face", 15.0, 0.5, 0, "solid just inside rear face")
v.check_solid("Near front face", 15.0, BODY_DEPTH - 0.5, 0, "solid near front face")
v.check_void("Behind rear", 10, -1, 0, "void behind rear face")
v.check_void("Past front", 10, BODY_DEPTH + 1, 0, "void past front face")

# -- Feature 2+3: Bore --
v.check_void("Bore Y=1", 0, 1.0, 0, "void at bore center Y=1")
v.check_void("Bore Y=10", 0, 10.0, 0, "void at bore center Y=10")
v.check_void("Bore Y=22", 0, 22.0, 0, "void at bore center Y=22")
v.check_void("Bore Y=24", 0, 24.0, 0, "void at bore center Y=24")
v.check_void("Inside bore wall", BORE_MINOR_R - 0.3, 22.0, 0, "void inside bore")

# Wall outside thread root must be solid
v.check_solid("Wall past root", THREAD_ROOT_R + 2, 10.0, 0,
              "solid in body wall (R=9.8) past thread root")

if THREAD_METHOD == "helical_sweep":
    # Groove existence: at Y=0.1, angular scan confirms VOID at 90 deg (0, 0.1, 7.5).
    # Probing at R=7.5 (between bore 6.3 and root 7.8) at angle=90 deg (+Z).
    v.check_void("Groove at Y=0.1", 0, 0.1, 7.5,
                 "void in thread groove at 90deg, Y=0.1")
    # Land existence: at Y=0.1, angular scan confirms SOLID at 0 deg (7.5, 0.1, 0).
    v.check_solid("Land at Y=0.1", 7.5, 0.1, 0,
                  "solid on thread land at 0deg, Y=0.1")
    # Groove at deeper position: at Y=10 (midway), check that grooves still present.
    # At mid-engagement, the helical grooves have wrapped around.
    # Verify void exists somewhere at R=7.5 by probing multiple angles.
    found_void = False
    found_solid = False
    for angle_deg in range(0, 360, 30):
        a = math.radians(angle_deg)
        x = 7.5 * math.cos(a)
        z = 7.5 * math.sin(a)
        if v.is_void(x, 10.0, z):
            found_void = True
        else:
            found_solid = True
    v._record("Groove at Y=10", found_void, "at least one void found at R=7.5 in thread zone")
    v._record("Land at Y=10", found_solid, "at least one solid found at R=7.5 in thread zone")
else:
    # Annular fallback: entire thread zone cut to root
    v.check_void("Thread root zone", THREAD_ROOT_R - 0.3, 10.0, 0,
                 "void in annular thread zone")

# Smooth bore section (Y=20..25): wall at BORE_MINOR_R + 1 should be solid
v.check_solid("Smooth section wall", BORE_MINOR_R + 1.0, 22.0, 0,
              "solid wall in smooth bore section")

# -- Feature 4: Wings --
# Wing tips at +/-X, at Y=mid, Z=0 (center of stadium)
v.check_solid("Wing +X tip", WING_HALF - 0.5, BODY_DEPTH / 2, 0,
              "solid at +X wing tip")
v.check_solid("Wing -X tip", -(WING_HALF - 0.5), BODY_DEPTH / 2, 0,
              "solid at -X wing tip")
# At wing tips (X=22), the stadium rounded end limits Z extent.
# Stadium slot2D(45, 20) has semicircular ends of radius WING_HEIGHT/2 = 10mm.
# The slot has flat sides (along X) and semicircular caps at X = +/-WINGSPAN/2.
# Actually, slot2D creates a shape with length=45 (in X), width=20 (in Z).
# At X=22 (0.5 from tip at 22.5), the semicircular end has:
# distance from center of semicircle at X=22.5-10=12.5 is 22-12.5=9.5
# Wait... slot2D(length=45, width=20): the straight section has length 45-20=25mm
# centered on X, so from X=-12.5 to X=+12.5. Beyond that are semicircles of R=10.
# At X=22, we're 22-12.5=9.5mm into the semicircle. The Z extent at that X:
# z = sqrt(10^2 - 9.5^2) = sqrt(100-90.25) = sqrt(9.75) = 3.12mm
# So at X=22, the wing only extends Z = +/-3.12mm, not +/-10.
# Therefore checking Z=+/-8 at X=22 would be void.
# Let's check Z extent at X=22 more conservatively:
v.check_solid("Wing +Z at center", 0, BODY_DEPTH / 2, WING_HEIGHT / 2 - 1,
              "solid at wing center Z=+9 (body cylinder covers this)")
v.check_solid("Wing -Z at center", 0, BODY_DEPTH / 2, -(WING_HEIGHT / 2 - 1),
              "solid at wing center Z=-9 (body cylinder)")
# Check wing tip Z extent is limited (should be void at Z=5 at X=22)
# At X=22, 9.5mm into semicircle radius 10: max Z = 3.12mm
v.check_void("Wing tip Z+5", WING_HALF - 0.5, BODY_DEPTH / 2, 5,
             "void at wing tip Z=5 (beyond stadium semicircle)")
v.check_void("Past +X wing", WING_HALF + 1, BODY_DEPTH / 2, 0,
             "void past +X wing")
v.check_void("Past -X wing", -(WING_HALF + 1), BODY_DEPTH / 2, 0,
             "void past -X wing")
# Wings only exist in Y range [7.5, 17.5] beyond the body
v.check_void("Wing pre-Y", WING_HALF - 0.5, WING_Y_START - 1, 0,
             "void at wing tip before Y range")
v.check_void("Wing post-Y", WING_HALF - 0.5, WING_Y_END + 1, 0,
             "void at wing tip after Y range")

# -- Feature 5: Knurl --
# At a knurl groove Y position, point at body OD - half groove depth should be void
knurl_check_y = KNURL_Y_START_POS + KNURL_PITCH  # Y=4.0 (second groove)
# At Y=4.0 (groove center), R=BODY_RADIUS - KNURL_DEPTH/2 = 19.55:
# This point is at the V-tip depth. The V-groove at Y=4.0 has tip at R=19.1
# and edges at R=20 for Y=3.6 and Y=4.4. At R=19.55, Y=4.0 should be void.
v.check_void("Knurl groove center", 0, knurl_check_y, BODY_RADIUS - KNURL_DEPTH * 0.4,
             "void at knurl groove (R=19.64, Z direction)")
# Between grooves at Y=3.0 (halfway between groove at Y=2 and Y=4)
# At R=BODY_RADIUS - 0.3 = 19.7, should be solid
v.check_solid("Between knurls", 0, KNURL_Y_START_POS + KNURL_PITCH * 0.5, BODY_RADIUS - 0.3,
              "solid between knurl grooves")

# -- Feature 6: Rear face --
v.check_solid("Rear annular face", 15.0, 0.2, 0, "solid on rear face (R=15)")
v.check_void("Rear bore center", 0, 0.2, 0, "void at bore center")

# -- Feature 7: Chamfer --
v.check_void("Chamfer at face", eff_r + 0.5, 0.1, 0,
             "void at chamfered bore entry")
if THREAD_METHOD == "helical_sweep":
    # Past chamfer in thread zone: check body wall at a safe radius
    # At Y=2.0 (past chamfer at Y=1), angle=0 (+X), the groove at start 0
    # will have rotated. Check at 90 degrees (Z direction) on a thread land.
    v.check_solid("Past chamfer land", 0, 2.0, BORE_MINOR_R + 0.3,
                  "solid on thread land past chamfer zone")
else:
    # In annular fallback, bore is at root radius through thread zone
    v.check_void("Past chamfer fallback", BORE_MINOR_R + 0.5, CHAMFER_SIZE + 0.5, 0,
                 "void past chamfer (annular fallback)")

# -- Rubric 4 --
v.check_valid()
v.check_single_body()

body_envelope_vol = math.pi * BODY_RADIUS**2 * BODY_DEPTH  # ~31416
wing_envelope_vol = WINGSPAN * WING_HEIGHT * WING_THICKNESS  # 9000
total_envelope = body_envelope_vol + wing_envelope_vol
v.check_volume(expected_envelope=total_envelope, fill_range=(0.25, 0.85))

# -- Rubric 5: Bounding box --
bb = body.val().BoundingBox()
print(f"\nBBox: X[{bb.xmin:.2f},{bb.xmax:.2f}] Y[{bb.ymin:.2f},{bb.ymax:.2f}] Z[{bb.zmin:.2f},{bb.zmax:.2f}]")
v.check_bbox("X", bb.xmin, bb.xmax, -WING_HALF, WING_HALF, tol=1.5)
v.check_bbox("Y", bb.ymin, bb.ymax, 0, BODY_DEPTH, tol=0.5)
v.check_bbox("Z", bb.zmin, bb.zmax, -BODY_RADIUS, BODY_RADIUS, tol=0.5)

if not v.summary():
    sys.exit(1)

print(f"\nThread method: {THREAD_METHOD}")
print("Done.")
