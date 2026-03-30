"""
Lever v2 — CadQuery STEP Generation Script
Season 1, Phase 2, Item 7 of the pump cartridge build sequence.

Updates from v1: strut positions updated to match release plate v2 strut positions.
Plate height increased from 50mm to 65mm to match release plate height and
contain struts at Z=5.0 and Z=60.0.

Coordinate system:
  Origin: Bottom-left corner of lever plate front face (X=0, Y=0, Z=0)
  X: Width axis — positive rightward as seen by user from front face
     Range: 0 → 80.0 mm
  Y: Depth axis — positive rearward (into cartridge)
     Y=0:  Lever plate front face (user contact / pull surface)
     Y=4:  Lever plate rear face (strut attachment point)
     Y=94: Strut tips (4mm plate + 90mm struts)
  Z: Height axis — positive upward
     Range: 0 → 65.0 mm

Envelope: 80.0 (X) × 94.0 (Y) × 65.0 (Z) mm
"""

import sys
from pathlib import Path

# Add tools/ to sys.path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

import cadquery as cq

# ============================================================
# Rubric 1 — Feature Planning Table
# ============================================================

print()
print("=" * 90)
print("RUBRIC 1 — Feature Planning Table")
print("=" * 90)
print()

FEATURE_TABLE = [
    ("1", "Plate Body",
     "Rigid load-transfer body: user finger contact surface (Y=0) to strut attachment (Y=4)",
     "Add", "Box", "Y", "(40.0, 2.0, 32.5)",
     "80W × 4D × 65H mm; X:[0,80] Y:[0,4] Z:[0,65]", "Base body"),

    ("2", "Plate Perimeter Corner Radii",
     "Prevents sharp corners snagging front panel hole; design language consistency with release plate",
     "Remove (blend)", "Fillet", "Y",
     "Edges at (X=0/80, Z=0/65), each runs Y=0→4",
     "R=2.0 mm on all 4 vertical (|Y) plate edges", "concept.md §5"),

    ("3", "Plate Bottom Chamfer (Elephant's Foot)",
     "Prevents elephant's foot dimensional error at build-plate contact edge; requirements.md §6",
     "Remove", "Chamfer", "Y (edge at Z=0, Y=0 face)",
     "Bottom edge of front face (Z=0, Y=0→4 edge, full X width)",
     "0.3 mm × 45°", "Build plate contact = Z=0 face; bottom edge of front face only"),

    ("4", "Strut TL (Top-Left)",
     "Transmits pull force from lever plate to Phase 2 joint; anti-rotation via 4-strut pattern",
     "Add", "Box", "Y", "Center (9.0, 49.0, 60.0)",
     "6W × 90D × 6H mm; X:[6,12] Y:[4,94] Z:[57,63]", "Matches release plate strut TL (X=9, Z=60)"),

    ("5", "Strut TR (Top-Right)",
     "Transmits pull force; mirror of TL about X=40",
     "Add", "Box", "Y", "Center (71.0, 49.0, 60.0)",
     "6W × 90D × 6H mm; X:[68,74] Y:[4,94] Z:[57,63]", "Matches release plate strut TR (X=71, Z=60)"),

    ("6", "Strut BL (Bottom-Left)",
     "Transmits pull force; mirror of TL about Z=32.5",
     "Add", "Box", "Y", "Center (9.0, 49.0, 5.0)",
     "6W × 90D × 6H mm; X:[6,12] Y:[4,94] Z:[2,8]", "Matches release plate strut BL (X=9, Z=5)"),

    ("7", "Strut BR (Bottom-Right)",
     "Transmits pull force; mirror of both TL and BL",
     "Add", "Box", "Y", "Center (71.0, 49.0, 5.0)",
     "6W × 90D × 6H mm; X:[68,74] Y:[4,94] Z:[2,8]", "Matches release plate strut BR (X=71, Z=5); diagonal 82.9mm"),
]

col_w = [3, 26, 20, 15, 10, 6, 22, 30, 35]
header = (f"{'#':<{col_w[0]}} {'Feature Name':<{col_w[1]}} {'Operation':<{col_w[3]}} "
          f"{'Shape':<{col_w[4]}} {'Axis':<{col_w[5]}} {'Center (X,Y,Z)':<{col_w[6]}} "
          f"{'Dimensions':<{col_w[7]}} Notes")
print(header)
print("-" * 120)
for row in FEATURE_TABLE:
    num, name, func, op, shape, axis, center, dims, notes = row
    print(f"{num:<{col_w[0]}} {name:<{col_w[1]}} {op:<{col_w[3]}} "
          f"{shape:<{col_w[4]}} {axis:<{col_w[5]}} {center:<{col_w[6]}} "
          f"{dims:<{col_w[7]}} {notes}")

print()

# ============================================================
# Rubric 2 — Coordinate System Declaration
# ============================================================

print("=" * 90)
print("RUBRIC 2 — Coordinate System Declaration")
print("=" * 90)
print()
print("  Origin: Bottom-left corner of lever plate front face (X=0, Y=0, Z=0)")
print("  X: Plate width, left to right as seen from front face; range [0, 80.0] mm")
print("  Y: Plate depth, front (user contact Y=0) to rear (strut tips Y=94.0); range [0, 94.0] mm")
print("  Z: Plate height, bottom to top; range [0, 65.0] mm")
print("  Envelope: 80.0 × 94.0 × 65.0 mm  →  X:[0,80]  Y:[0,94]  Z:[0,65]")
print()
print("  Feature coordinate cross-check:")
print("    Plate occupies  X:[0,80]   Y:[0,4]    Z:[0,65]")
print("    Strut TL center X=9.0,  Z=60.0  → box X:[6,12]   Y:[4,94]  Z:[57,63]")
print("    Strut TR center X=71.0, Z=60.0  → box X:[68,74]  Y:[4,94]  Z:[57,63]")
print("    Strut BL center X=9.0,  Z=5.0   → box X:[6,12]   Y:[4,94]  Z:[2,8]")
print("    Strut BR center X=71.0, Z=5.0   → box X:[68,74]  Y:[4,94]  Z:[2,8]")
print()

# ============================================================
# Geometry constants
# ============================================================

# Plate
PLATE_W  = 80.0   # X
PLATE_D  =  4.0   # Y
PLATE_H  = 65.0   # Z — matches release plate height so strut Z positions align

# Struts
STRUT_W  =  6.0   # X cross-section
STRUT_H  =  6.0   # Z cross-section
STRUT_L  = 90.0   # Y length
STRUT_Y0 =  4.0   # struts start at plate rear face
STRUT_Y1 = 94.0   # strut tips

# Strut center positions in lever local X and Z
# Positions match release plate v2 strut positions exactly (same X, same Z).
STRUTS = {
    "TL": (9.0,  60.0),
    "TR": (71.0, 60.0),
    "BL": (9.0,   5.0),
    "BR": (71.0,  5.0),
}

# Plate corner fillet radius (Feature 2)
CORNER_R = 2.0    # mm — from parts.md Feature 2 (concept.md §5)

# Elephant's foot chamfer (Feature 3)
CHAMFER  = 0.3    # mm

# ============================================================
# Feature 1 — Plate Body
# ============================================================
print("Building Feature 1: Plate Body ...")
# centered=False places box at X:[0,80] Y:[0,4] Z:[0,50]
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# ============================================================
# Feature 2 — Plate Perimeter Corner Radii
# ============================================================
print("Building Feature 2: Corner radii on vertical plate edges ...")
# At this point the plate is a clean box — the 4 vertical (|Y) edges are
# the 4 corners of the XZ rectangle.  Use "|Y" to select all 4 at once.
plate = plate.edges("|Y").fillet(CORNER_R)

# ============================================================
# Feature 3 — Elephant's Foot Chamfer on bottom front edge
# ============================================================
print("Building Feature 3: Elephant's foot chamfer ...")
# The bottom front edge is the edge at Z=0 on the Y=0 face.
# On the clean plate (before struts), use a compound selector:
#   "<Z" selects edges at the minimum Z face (Z=0 face edges)
#   "<Y" selects edges at the minimum Y face (Y=0 face edges)
# The intersection of edges on the Z=0 face AND Y=0 face gives only the
# bottom-front edge of the plate (running in X direction, after fillets
# the arc end-tangents remain on these faces).
plate = plate.edges("<Z").edges("<Y").chamfer(CHAMFER)

# ============================================================
# Features 4–7 — Struts (union to plate)
# ============================================================
print("Building Features 4–7: Struts (TL, TR, BL, BR) ...")
lever = plate
for label, (cx, cz) in STRUTS.items():
    # strut box: centered on (cx, cz) in XZ, Y from STRUT_Y0 to STRUT_Y1
    sx0 = cx - STRUT_W / 2   # left X edge of strut
    sz0 = cz - STRUT_H / 2   # bottom Z edge of strut
    # Place strut at sx0, STRUT_Y0, sz0 using a fresh workplane + transform
    strut = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(sx0, STRUT_Y0, sz0))
        .box(STRUT_W, STRUT_L, STRUT_H, centered=False)
    )
    lever = lever.union(strut)

# ============================================================
# Export STEP file
# ============================================================
OUT_DIR = Path(__file__).parent
STEP_PATH = OUT_DIR / "lever-cadquery.step"
print(f"\nExporting STEP to: {STEP_PATH}")
cq.exporters.export(lever, str(STEP_PATH))
print("Export complete.")

# ============================================================
# Rubric 3 — Feature-Specification Reconciliation
# ============================================================

print()
print("=" * 90)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 90)
print()

v = Validator(lever)

# --- Feature 1: Plate Body ---
print("Feature 1: Plate Body")
v.check_solid("Plate interior center",     40.0,  2.0, 25.0, "solid at plate center")
v.check_solid("Plate left face interior",   1.0,  2.0, 25.0, "solid near left face")
v.check_solid("Plate right face interior", 79.0,  2.0, 25.0, "solid near right face")
v.check_solid("Plate front face interior", 40.0,  0.5, 25.0, "solid near front face")
v.check_solid("Plate rear face interior",  40.0,  3.5, 25.0, "solid near rear face")
v.check_solid("Plate top interior",        40.0,  2.0, 64.0, "solid near top face")
# Bottom interior — above chamfer zone
v.check_solid("Plate bottom interior",     40.0,  2.0,  1.0, "solid near bottom face (above chamfer)")
# Void outside plate (forward of front face)
v.check_void("Void in front of plate",     40.0, -1.0, 25.0, "void in front of plate front face")
# Void outside plate (above)
v.check_void("Void above plate (no strut)",45.0,  2.0, 66.0, "void above plate where no strut")

print()

# --- Feature 2: Corner Radii ---
print("Feature 2: Plate Corner Radii (R=2.0mm)")
# The fillet removes material at the corners. The corner edge at (X=0, Z=0) means
# a point at (X=-0.5, Y=2, Z=0.5) should be void after filleting.
# Before fillet such a point would be on the edge; a point at ~(X=0.3, Y=2, Z=0.3) in
# the right orientation tests the fillet removal.
# At (X=0, Z=0) corner: a point in the former corner region at ~45° should be void.
# The fillet radius is 2mm, so X=-1 at Z=1 (radially inside the original corner = void after fillet).
# Actually: fillet replaces the corner edge with a cylindrical surface of R=2.
# A point at (X=0.2, Y=2.0, Z=0.2) is near the corner — if corner has R=2 fillet,
# the material boundary is at sqrt(x^2+z^2)=2 from corner origin.
# Point at (0.2, 2.0, 0.2): dist from corner = sqrt(0.04+0.04) = 0.28mm — well inside fillet, solid.
# Point at (1.0, 2.0, 1.0): dist from corner = sqrt(1+1) = 1.41mm < 2mm — inside fillet, should be void.
# Wait: fillet removes the OUTER corner, so points that were OUTSIDE the original corner
# (in the cut-away zone) become void.
# Original corner is at X=0,Z=0 — the fillet removes material from the solid in a 2mm radius arc.
# Before fillet: point at (X=0, Y=2, Z=0) is ON the edge (boundary), i.e. solid.
# After fillet: the boundary is the arc center is at (X=2, Y=2, Z=2) ... no wait.
# For a vertical edge at X=0,Z=0 (running along Y), the fillet creates a cylindrical surface
# centered on the axis of the original edge. Material outside the cylinder of radius R=2
# centered at X=0,Z=0 that would normally be solid becomes void.
# Actually the fillet rounds the OUTER corner: solid material at the corner is replaced by the fillet.
# Corner at X=0, Z=0: The original solid has all four quadrants of XZ space filled at that corner.
# Wait — the plate only occupies X>=0 and Z>=0. The corner at X=0,Z=0 is convex.
# Convex fillet: removes material to produce a rounded exterior corner.
# After fillet: at Z=0.5, X should be ~sqrt(4-0.25)-...
# Let me think simpler: after a 2mm fillet on the corner at (0,0) in XZ:
# The fillet makes the physical edge a curved arc. The center of the fillet radius is at (2,z,2).
# A point at (X=0.5, Y=2, Z=0.5) is at distance sqrt(0.25+0.25)=0.71 from corner.
# But the fillet arc is at R=2 from (2,y,2). Point (0.5,y,0.5) is at dist sqrt(1.5^2+1.5^2)=2.12>2 from (2,y,2).
# Since it's outside R=2 from (2,y,2), and XZ<2 plate corner... this is the removed region: VOID.
v.check_void("Corner BL fillet (should be void at removed corner)",
             0.5, 2.0, 0.5, "void in BL corner fillet zone (R=2mm fillet removes this corner)")
v.check_void("Corner BR fillet",
             PLATE_W - 0.5, 2.0, 0.5, "void in BR corner fillet zone")
v.check_void("Corner TL fillet",
             0.5, 2.0, PLATE_H - 0.5, "void in TL corner fillet zone (Z=64.5)")
v.check_void("Corner TR fillet",
             PLATE_W - 0.5, 2.0, PLATE_H - 0.5, "void in TR corner fillet zone (Z=64.5)")
# Solid should exist just inside the fillet tangent points
v.check_solid("Plate BL near-corner solid",  3.0, 2.0,  0.5, "solid past fillet tangent on X=3")
v.check_solid("Plate BL near-corner solid2", 0.5, 2.0,  3.0, "solid past fillet tangent on Z=3")

print()

# --- Feature 3: Elephant's Foot Chamfer ---
print("Feature 3: Elephant's Foot Chamfer (0.3mm × 45°, bottom front edge)")
# Chamfer is on the bottom-front edge at Z=0, Y=0, running in X.
# The chamfer removes a 0.3mm triangular section at the Y=0, Z=0 edge.
# At exactly Y=0.1, Z=0.1, X=40 — a point that would be solid before chamfer.
# After 0.3mm×45° chamfer: boundary line at Y+Z=0.3.
# Point at Y=0.1, Z=0.1: Y+Z=0.2 < 0.3 → void (in chamfer zone).
v.check_void("Chamfer void at (40, 0.1, 0.1)",
             40.0, 0.1, 0.1, "void in chamfer zone (0.3mm chamfer removes this corner)")
# Point at Y=0.25, Z=0.25: Y+Z=0.5 > 0.3 → solid
v.check_solid("Solid above chamfer zone (40, 0.25, 0.25)",
              40.0, 0.25, 0.25, "solid above 0.3mm chamfer zone")
# Verify front face solid above chamfer (not touching Z=0 edge)
v.check_solid("Front face solid above chamfer",
              40.0, 0.2, 2.0, "solid on front face above chamfer zone")

print()

# --- Features 4–7: Struts ---
print("Features 4–7: Struts TL, TR, BL, BR")

for label, (cx, cz) in STRUTS.items():
    mid_y = (STRUT_Y0 + STRUT_Y1) / 2  # Y=49.0 (midpoint of strut)
    tip_y = STRUT_Y1 - 1.0             # Y=93.0 (near strut tip)
    base_y = STRUT_Y0 + 1.0            # Y=5.0 (near strut base)

    # Interior of strut at midpoint
    v.check_solid(f"Strut {label} mid-center",
                  cx, mid_y, cz, f"solid at strut {label} center (X={cx}, Y={mid_y}, Z={cz})")
    # Near strut tip
    v.check_solid(f"Strut {label} tip interior",
                  cx, tip_y, cz, f"solid near strut {label} tip (Y={tip_y})")
    # At strut base (just past plate rear face)
    v.check_solid(f"Strut {label} base",
                  cx, base_y, cz, f"solid at strut {label} base (Y={base_y})")

    # Dimensions: check that points just outside strut cross-section are void
    sx0 = cx - STRUT_W / 2
    sx1 = cx + STRUT_W / 2
    sz0 = cz - STRUT_H / 2
    sz1 = cz + STRUT_H / 2

    # Check void just beyond X extents at mid strut (only if not inside plate)
    if sx0 - 0.5 > 0 and sx0 - 0.5 < PLATE_W:
        # Only check void if we're not within the plate Y range
        v.check_void(f"Strut {label} void X- side",
                     sx0 - 0.5, mid_y, cz,
                     f"void just left of strut {label} (X={sx0-0.5:.1f}), outside strut cross-section")

    if sx1 + 0.5 < PLATE_W:
        v.check_void(f"Strut {label} void X+ side",
                     sx1 + 0.5, mid_y, cz,
                     f"void just right of strut {label} (X={sx1+0.5:.1f}), outside strut cross-section")

    if sz0 - 0.5 > 0:
        v.check_void(f"Strut {label} void Z- side",
                     cx, mid_y, sz0 - 0.5,
                     f"void below strut {label} (Z={sz0-0.5:.1f})")

    if sz1 + 0.5 < PLATE_H:
        v.check_void(f"Strut {label} void Z+ side",
                     cx, mid_y, sz1 + 0.5,
                     f"void above strut {label} (Z={sz1+0.5:.1f})")

    # Void beyond strut tips
    v.check_void(f"Strut {label} void beyond tip",
                 cx, STRUT_Y1 + 1.0, cz,
                 f"void beyond strut {label} tip (Y={STRUT_Y1+1.0})")

print()

# ============================================================
# Rubric 4 — Solid Validity
# ============================================================
print("=" * 90)
print("RUBRIC 4 — Solid Validity")
print("=" * 90)
print()

v.check_valid()
v.check_single_body()

# Volume estimate:
# Plate: 80 × 4 × 65 = 20800 mm³
# 4 struts: 4 × 6 × 90 × 6 = 12960 mm³
# Minus corner fillets and chamfer (small)
# Total ≈ 33760 mm³ (before subtractions, which are small)
# Use plate+strut envelope: 80 × 94 × 65 = 488800 mm³
# Fill ratio: ~33760/488800 ≈ 6.9%
# Use a tighter fill_range since geometry is well-known
envelope_vol = PLATE_W * STRUT_Y1 * PLATE_H  # 80 × 94 × 65 = 488800
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.05, 0.15))

print()

# ============================================================
# Rubric 5 — Bounding Box Reconciliation
# ============================================================
print("=" * 90)
print("RUBRIC 5 — Bounding Box Reconciliation")
print("=" * 90)
print()
print("Expected envelope from parts.md: 80.0mm (X) × 94.0mm (Y) × 65.0mm (Z)")
print()

bb = lever.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, STRUT_Y1)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H)

print()

# ============================================================
# Summary
# ============================================================
ok = v.summary()
if not ok:
    sys.exit(1)
else:
    print(f"\nSTEP file written to: {STEP_PATH}")
    sys.exit(0)
