"""
Pump-case retainer clip.

A small flat plate with two flexing arms that snap into the diamond-profile
cavities in the pump case's pogo ridge.  Sits flat against the inner wall of
the pump case, covering the back of the pogo connector body.  The center
through-slot clears the wire / solder tails.

Built flat with the bottom face at Y=0 and height axis +Y (project
convention).  Arm profiles are lofted to match the 2-3-2 diamond cavity.
"""

from pathlib import Path
import cadquery as cq


# ═══════════════════════════════════════════════════════
# PHYSICAL DIMENSIONS
# ═══════════════════════════════════════════════════════

# ── Plate (pill / stadium) ──
PLATE_LENGTH_X = 28.0
PLATE_WIDTH_Z  = 10.0
PLATE_THICK_Y  = 2.0

# ── Center clearance slot ──
SLOT_LENGTH_X = 8.0
SLOT_WIDTH_Z  = 3.0

# ── Retention arm positions ──
ARM_OFFSET_X = 10.5

# ── Retention arm profile (diamond, matches cavity) ──
ARM_ENTRY = 2.0      # at plate surface (Y = PLATE_THICK_Y)
ARM_MID   = 3.0      # at mid depth
ARM_TIP   = 2.0      # at tip
ARM_MID_Y = 1.5
ARM_TIP_Y = 3.0

# ── Slit through each arm for flex ──
SLIT_WIDTH_X       = 0.4   # thin dimension: cuts X (separates the two halves)
# Arm cross-section is a diamond inscribed in the ARM_MID bounding square, so
# its Z extent is ±ARM_MID/2; 0.5 overhang per side fully severs the halves.
SLIT_Z_OVERHANG    = 0.5   # extend past arm in Z on each side
SLIT_TOP_OVERCUT   = 0.5   # above arm tip
SLIT_PLATE_CUT     = 0.8   # how far into the plate the slit extends (< PLATE_THICK_Y)

# ── Shared constants ──
OVERCUT = 0.1


# ═══════════════════════════════════════════════════════
# FEATURE FUNCTIONS
# ═══════════════════════════════════════════════════════

def build_plate():
    """Pill/stadium plate, bottom face at Y=0, extruded to Y=PLATE_THICK_Y."""
    # XZ plane: extrude(-h) builds the solid from Y=0 to Y=+h.
    return (
        cq.Workplane("XZ")
        .slot2D(PLATE_LENGTH_X, PLATE_WIDTH_Z)
        .extrude(-PLATE_THICK_Y)
    )


def cut_center_slot(solid):
    """Rectangular through-slot for wire / solder-tail clearance."""
    cutter = (
        cq.Workplane("XZ")
        .workplane(offset=-OVERCUT)
        .rect(SLOT_LENGTH_X, SLOT_WIDTH_Z)
        .extrude(-(PLATE_THICK_Y + 2 * OVERCUT))
    )
    return solid.cut(cutter)


def build_arm(center_x):
    """Lofted diamond arm rising from the plate top face at X=center_x."""
    def profile(size, y):
        return (
            cq.Workplane("XZ")
            .workplane(offset=y)
            .center(center_x, 0)
            .rect(size, size)
        )

    # CadQuery's XZ workplane has Y as its normal.  workplane(offset=y) shifts
    # in +Y when the plane's normal points +Y.  XZ normal points -Y by default,
    # so we build profiles on an explicit plane with +Y normal.
    plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
    wp = cq.Workplane(plane)
    arm = (
        wp.workplane(offset=PLATE_THICK_Y)
          .center(center_x, 0).rect(ARM_ENTRY, ARM_ENTRY)
          .workplane(offset=ARM_MID_Y)
          .center(0, 0).rect(ARM_MID, ARM_MID)
          .workplane(offset=ARM_TIP_Y - ARM_MID_Y)
          .center(0, 0).rect(ARM_TIP, ARM_TIP)
          .loft(ruled=True)
    )
    return arm


def cut_arm_slit(solid, center_x):
    """Thin slit through an arm so the two halves flex inward on insertion."""
    slit_length_z = ARM_MID + 2 * SLIT_Z_OVERHANG
    slit_height_y = PLATE_THICK_Y + ARM_TIP_Y + SLIT_TOP_OVERCUT - (PLATE_THICK_Y - SLIT_PLATE_CUT)
    slit_bottom_y = PLATE_THICK_Y - SLIT_PLATE_CUT

    plane = cq.Plane(
        origin=(center_x, slit_bottom_y, 0),
        xDir=(1, 0, 0),
        normal=(0, 1, 0),
    )
    cutter = (
        cq.Workplane(plane)
        .rect(SLIT_WIDTH_X, slit_length_z)
        .extrude(slit_height_y)
    )
    return solid.cut(cutter)


# ═══════════════════════════════════════════════════════
# ASSEMBLY
# ═══════════════════════════════════════════════════════

def build_retainer():
    solid = build_plate()
    solid = cut_center_slot(solid)
    for sign in (-1, +1):
        cx = sign * ARM_OFFSET_X
        solid = solid.union(build_arm(cx))
        solid = cut_arm_slit(solid, cx)
    return solid


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

retainer = build_retainer()

solids = retainer.solids().vals()
print(f"Retainer: {len(solids)} solid(s)")
for i, s in enumerate(solids):
    bb = s.BoundingBox()
    print(f"  Solid {i}: X[{bb.xmin:.2f},{bb.xmax:.2f}] "
          f"Y[{bb.ymin:.2f},{bb.ymax:.2f}] Z[{bb.zmin:.2f},{bb.zmax:.2f}]")

OUTPUT_DIR = Path(__file__).resolve().parent
out_path = OUTPUT_DIR / "pump-case-retainer-cadquery.step"
cq.exporters.export(retainer, str(out_path))
print(f"Exported → {out_path.name}")
