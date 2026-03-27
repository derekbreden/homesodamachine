"""
Generate STEP file for the Cartridge Release Plate using build123d.

Part spec: hardware/cartridge-release-plate/planning/parts.md
JG fitting geometry: hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

Axis convention (matching engineering drawing):
  X = width (59mm)
  Y = depth (6mm) -- fitting side is Y=0, back side is Y=6
  Z = height (47mm)

The plate origin is at the bottom-left corner of the fitting face:
  X: 0 to 59
  Y: 0 to 6  (fitting side to back side)
  Z: 0 to 47
"""

from build123d import *
from pathlib import Path

# ── Plate dimensions ──
PLATE_W = 59.0   # X
PLATE_D = 6.0    # Y
PLATE_H = 47.0   # Z

# ── Stepped bore dimensions (caliper-verified interface) ──
# Outer bore (body end cradle): just over 15.10mm body end OD
OUTER_BORE_DIA = 15.6    # mm (0.5mm clearance over 15.10mm OD)
OUTER_BORE_DEPTH = 2.0   # mm (from fitting face, Y=0 inward)

# Inner lip (collet hugger): just over 9.57mm collet OD
INNER_LIP_DIA = 10.0     # mm (0.43mm clearance over 9.57mm OD)
INNER_LIP_DEPTH = 2.0    # mm

# Tube clearance hole: between 6.30mm tube OD and 6.69mm collet ID
TUBE_HOLE_DIA = 6.5      # mm (0.20mm over tube, 0.19mm under collet ID)
# Through remaining thickness: 6.0 - 2.0 - 2.0 = 2.0mm
TUBE_HOLE_DEPTH = 2.0    # mm (through to back face)

# Chamfers
OUTER_BORE_CHAMFER = 0.3  # mm, 45-degree lead-in at outer bore entry
TUBE_HOLE_CHAMFER = 0.1   # mm, at tube hole entry edge

# ── Bore grid positions (from bottom-left of plate) ──
# 2x2 grid: 40mm horizontal, 28mm vertical center-to-center
BORE_CENTERS = [
    (9.5, 9.5),
    (49.5, 9.5),
    (9.5, 37.5),
    (49.5, 37.5),
]

# ── Push rod contact boss ──
BOSS_DIA = 8.0       # mm
BOSS_HEIGHT = 1.0    # mm proud of back face
BOSS_CENTER = (29.5, 23.5)  # (X, Z) from bottom-left

# ── Guide pin tabs ──
# Elongated slots for 3mm dowel pins
SLOT_W = 3.3    # mm (X direction, matches 3mm pin + clearance)
SLOT_H = 7.3    # mm (Z direction, elongated for travel)
# Tab dimensions: extend from plate edge
TAB_EXTENSION = 11.0  # mm total from plate center to slot center (X=-5.5 and X=64.5)
TAB_WIDTH = SLOT_W + 2 * 2.5  # mm wall around slot (2.5mm each side)
TAB_HEIGHT = SLOT_H + 2 * 2.5  # mm wall around slot
TAB_DEPTH = PLATE_D   # same depth as plate

# Slot center positions (X, Z) from plate bottom-left
SLOT_CENTERS = [
    (-5.5, 23.5),   # left tab
    (64.5, 23.5),   # right tab
]

# ── Output path ──
STEP_PATH = Path(__file__).parent / "release-plate-build123d.step"


def make_release_plate():
    """Build the release plate geometry."""

    # ── 1. Main plate body ──
    # Origin at bottom-left of fitting face (X=0, Y=0, Z=0)
    # Box centered, then relocated
    plate = Box(PLATE_W, PLATE_D, PLATE_H)
    plate = Pos(PLATE_W / 2, PLATE_D / 2, PLATE_H / 2) * plate

    # ── 2. Guide pin tabs ──
    # Tabs extend from plate edges. Overlap 1mm with plate body to ensure
    # boolean fusion (adjacent-but-not-overlapping produces compound solids).
    OVERLAP = 1.0

    # Left tab: extends from X=0 to the left, overlapping into plate by 1mm
    left_tab_left_edge = SLOT_CENTERS[0][0] - TAB_WIDTH / 2  # leftmost edge
    left_tab_right_edge = OVERLAP  # overlap 1mm into plate
    left_tab_actual_w = left_tab_right_edge - left_tab_left_edge
    left_tab_x_center = (left_tab_left_edge + left_tab_right_edge) / 2
    left_tab = Box(left_tab_actual_w, TAB_DEPTH, TAB_HEIGHT)
    left_tab = Pos(left_tab_x_center, PLATE_D / 2, SLOT_CENTERS[0][1]) * left_tab

    # Right tab: extends from X=59 to the right, overlapping into plate by 1mm
    right_tab_left_edge = PLATE_W - OVERLAP  # overlap 1mm into plate
    right_tab_right_edge = SLOT_CENTERS[1][0] + TAB_WIDTH / 2
    right_tab_actual_w = right_tab_right_edge - right_tab_left_edge
    right_tab_x_center = (right_tab_left_edge + right_tab_right_edge) / 2
    right_tab = Box(right_tab_actual_w, TAB_DEPTH, TAB_HEIGHT)
    right_tab = Pos(right_tab_x_center, PLATE_D / 2, SLOT_CENTERS[1][1]) * right_tab

    # Union plate + tabs (overlap ensures proper fusion)
    body = plate + left_tab + right_tab

    # ── 3. Push rod contact boss on back face ──
    boss = Cylinder(BOSS_DIA / 2, BOSS_HEIGHT)
    # Cylinder axis is Z by default in build123d; we need it along Y
    # Rotate 90 degrees around X to point cylinder along Y
    boss = Rot(90, 0, 0) * boss
    # Position: center at (BOSS_CENTER[0], PLATE_D + BOSS_HEIGHT/2, BOSS_CENTER[1])
    boss = Pos(BOSS_CENTER[0], PLATE_D + BOSS_HEIGHT / 2, BOSS_CENTER[1]) * boss
    body = body + boss

    # ── 4. Stepped bores (subtract from fitting face) ──
    # Bores go along Y axis (into the plate from fitting face at Y=0)
    # Each bore has 3 concentric zones stacked in Y:
    #   Y=0 to Y=2.0: outer bore (15.6mm dia)
    #   Y=2.0 to Y=4.0: inner lip (10.0mm dia)
    #   Y=4.0 to Y=6.0: tube clearance hole (6.5mm dia)

    for cx, cz in BORE_CENTERS:
        # Outer bore: from Y=0 to Y=OUTER_BORE_DEPTH
        outer = Cylinder(OUTER_BORE_DIA / 2, OUTER_BORE_DEPTH)
        outer = Rot(90, 0, 0) * outer
        outer = Pos(cx, OUTER_BORE_DEPTH / 2, cz) * outer

        # Inner lip: from Y=OUTER_BORE_DEPTH to Y=OUTER_BORE_DEPTH+INNER_LIP_DEPTH
        inner = Cylinder(INNER_LIP_DIA / 2, INNER_LIP_DEPTH)
        inner = Rot(90, 0, 0) * inner
        y_inner = OUTER_BORE_DEPTH + INNER_LIP_DEPTH / 2
        inner = Pos(cx, y_inner, cz) * inner

        # Tube clearance hole: from Y=OUTER_BORE_DEPTH+INNER_LIP_DEPTH to Y=PLATE_D
        tube = Cylinder(TUBE_HOLE_DIA / 2, TUBE_HOLE_DEPTH)
        tube = Rot(90, 0, 0) * tube
        y_tube = OUTER_BORE_DEPTH + INNER_LIP_DEPTH + TUBE_HOLE_DEPTH / 2
        tube = Pos(cx, y_tube, cz) * tube

        bore = outer + inner + tube
        body = body - bore

    # ── 5. Chamfers on bores ──
    # We need to chamfer specific edges on the bore features.
    # Outer bore entry chamfer (0.3mm at Y=0 face) and tube hole entry chamfer
    # (0.1mm at the Y=2.0 step where tube hole meets inner lip).
    #
    # Strategy: find edges by position. After boolean subtraction, the bore
    # edges exist on the body. We select edges near the bore entry circles.

    for cx, cz in BORE_CENTERS:
        # Outer bore entry chamfer: circular edge at Y=0, radius = OUTER_BORE_DIA/2
        outer_entry_edges = body.edges().filter_by(
            lambda e: (
                abs(e.center().Y) < 0.01
                and abs(
                    ((e.center().X - cx) ** 2 + (e.center().Z - cz) ** 2) ** 0.5
                    - OUTER_BORE_DIA / 2
                )
                < 0.1
            )
        )
        if len(outer_entry_edges) > 0:
            body = chamfer(outer_entry_edges, OUTER_BORE_CHAMFER)

        # Tube hole entry chamfer: circular edge at Y=OUTER_BORE_DEPTH+INNER_LIP_DEPTH
        # where the inner lip meets the tube hole (step from 10mm to 6.5mm)
        tube_entry_y = OUTER_BORE_DEPTH + INNER_LIP_DEPTH
        tube_entry_edges = body.edges().filter_by(
            lambda e, _y=tube_entry_y, _cx=cx, _cz=cz: (
                abs(e.center().Y - _y) < 0.01
                and abs(
                    ((e.center().X - _cx) ** 2 + (e.center().Z - _cz) ** 2) ** 0.5
                    - TUBE_HOLE_DIA / 2
                )
                < 0.1
            )
        )
        if len(tube_entry_edges) > 0:
            body = chamfer(tube_entry_edges, TUBE_HOLE_CHAMFER)

    # ── 6. Guide pin slots (through tabs) ──
    for sx, sz in SLOT_CENTERS:
        # Elongated slot = rectangle with semicircular ends (stadium shape)
        # Through full depth (Y direction)
        # Use SlotOverall for the 2D shape, then extrude
        slot_profile = SlotOverall(SLOT_H, SLOT_W)
        # SlotOverall makes a horizontal slot; we need it vertical (Z direction)
        # The slot is SLOT_W wide (X) and SLOT_H tall (Z)
        # SlotOverall(length, width) - length along local X, so rotate 90 degrees
        slot_profile = Rot(0, 0, 90) * slot_profile
        # Extrude along Y through full depth
        slot_solid = extrude(slot_profile, PLATE_D)
        slot_solid = Pos(sx, 0, sz) * slot_solid
        body = body - slot_solid

    return body


if __name__ == "__main__":
    print("Generating release plate...")
    part = make_release_plate()

    # ── Validation ──
    bb = part.bounding_box()
    print(f"Bounding box:")
    print(f"  X: {bb.min.X:.3f} to {bb.max.X:.3f}  (width: {bb.max.X - bb.min.X:.3f})")
    print(f"  Y: {bb.min.Y:.3f} to {bb.max.Y:.3f}  (depth: {bb.max.Y - bb.min.Y:.3f})")
    print(f"  Z: {bb.min.Z:.3f} to {bb.max.Z:.3f}  (height: {bb.max.Z - bb.min.Z:.3f})")
    print(f"Volume: {part.volume:.2f} mm^3")
    print(f"Face count: {len(part.faces())}")

    # ── Export STEP ──
    export_step(part, str(STEP_PATH))
    print(f"STEP file written to: {STEP_PATH}")
