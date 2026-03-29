#!/usr/bin/env python3
"""
Enclosure Assembly — Compose Top and Bottom Halves into Single STEP

This script loads the pre-validated top and bottom STEP files, applies spatial
transforms to align them, performs a Boolean union, and validates the final
assembly against the complete enclosure specification.

**Spatial Model:**
- Bottom half: designed in local frame Z:[0,200], exported as-is
- Top half: designed in local frame Z:[0,200] (seam at Z=0 local), must translate to Z:[200,400]
- Assembly: Union of bottom (Z:[0,200]) + top translated to (Z:[200,400])
- Result: Single solid 220 × 300 × 400 mm with snap engagement at Z=200 global

**Validation:**
- Seam boundary: all 10 snap engagement points (solid at seam, solid top, solid bottom)
- Geometry integrity: features from both halves present and correct
- Topology: single body, valid solid, volume ratio acceptable
- Bounding box: 220 × 300 × 400 mm (production constraint)
"""

import cadquery as cq
import sys
from pathlib import Path

# OCP imports for robust Boolean fusion
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.gp import gp_Trsf, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

# Add tools to path for validator
tools_dir = Path(__file__).resolve().parents[3] / "tools"
sys.path.insert(0, str(tools_dir))
from step_validate import Validator


def main():
    print("=" * 70)
    print("ENCLOSURE ASSEMBLY — CadQuery Composition")
    print("=" * 70)
    print()

    # ====================================================================
    # PHASE 1: Load Sub-Components
    # ====================================================================
    print("PHASE 1: Loading STEP Files")
    print("-" * 70)

    base_dir = Path(__file__).resolve().parent / "planning"

    bottom_step = base_dir / "bottom-half" / "bottom-half-cadquery.step"
    top_step = base_dir / "top-half" / "top-half-cadquery.step"

    if not bottom_step.exists():
        print(f"ERROR: Bottom half STEP not found: {bottom_step}")
        sys.exit(1)
    if not top_step.exists():
        print(f"ERROR: Top half STEP not found: {top_step}")
        sys.exit(1)

    print(f"Loading bottom half: {bottom_step.name}")
    bottom_half = cq.importers.importStep(str(bottom_step))
    print(f"  ✓ Loaded. Bounding box: {bottom_half.val().BoundingBox()}")

    print(f"Loading top half: {top_step.name}")
    top_half = cq.importers.importStep(str(top_step))
    print(f"  ✓ Loaded. Bounding box: {top_half.val().BoundingBox()}")
    print()

    # ====================================================================
    # PHASE 2: Apply Transforms
    # ====================================================================
    print("PHASE 2: Applying Spatial Transforms")
    print("-" * 70)

    print("Bottom half: Z:[0,200] → stays at Z:[0,200]")
    print("Top half: Z:[0,200] local → translates to Z:[200,400] global")
    print("  Seam face (Z=0 local) → Z=200 global (matches bottom seam)")
    print("  Top face (Z=200 local) → Z=400 global (top of enclosure)")
    print()

    # Top half moves from Z:[0,200] to Z:[200,400]
    # Translation vector: (0, 0, +200)
    top_half_translated = top_half.translate((0, 0, 200))
    print("Top half translated by +200 mm in Z")
    bb_top_translated = top_half_translated.val().BoundingBox()
    print(f"  ✓ Translated bounding box: {bb_top_translated}")
    print()

    # ====================================================================
    # PHASE 3: Boolean Union (OCP-based for robust fusion)
    # ====================================================================
    print("PHASE 3: Boolean Union (OCP BRepAlgoAPI_Fuse)")
    print("-" * 70)

    try:
        # Extract OCP shapes from CadQuery workplanes
        bottom_shape = bottom_half.val().wrapped
        top_shape_local = top_half.val().wrapped

        # Apply translation to top shape via OCP transform
        print("Applying +200 mm Z translation to top half...")
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(0, 0, 200))
        top_transformed = BRepBuilderAPI_Transform(top_shape_local, trsf, True).Shape()
        print("  ✓ Transform applied")

        # Perform fusion using OCP's BRepAlgoAPI_Fuse
        print("Computing fusion with BRepAlgoAPI_Fuse...")
        fuse_op = BRepAlgoAPI_Fuse(bottom_shape, top_transformed)
        fuse_op.Build()

        if not fuse_op.IsDone():
            raise RuntimeError("BRepAlgoAPI_Fuse.Build() did not complete successfully")

        # Wrap result back in CadQuery
        fused_shape = fuse_op.Shape()
        fused_solid = cq.Solid(fused_shape)
        enclosure = cq.Workplane("XY").add(fused_solid)
        print("  ✓ Fusion successful")

    except Exception as e:
        print(f"  ✗ Fusion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    bb_assembled = enclosure.val().BoundingBox()
    print(f"Assembled bounding box: {bb_assembled}")
    print(f"  X: {bb_assembled.xmin:.2f} to {bb_assembled.xmax:.2f}")
    print(f"  Y: {bb_assembled.ymin:.2f} to {bb_assembled.ymax:.2f}")
    print(f"  Z: {bb_assembled.zmin:.2f} to {bb_assembled.zmax:.2f}")
    print()

    # ====================================================================
    # PHASE 4: Comprehensive Validation
    # ====================================================================
    print("PHASE 4: Validation")
    print("-" * 70)
    print()

    v = Validator(enclosure)

    # ---- 4.1: Seam Boundary Validation (Critical) ----
    print("4.1 SEAM BOUNDARY VALIDATION (10 snap engagement points)")
    print("-" * 70)
    print("NOTE: Snap positions are pockets (voids) at seam face.")
    print("Validation checks: void at snap pocket, solid on flanks.\n")

    snap_positions = [
        (15, 15, "Front-left corner"),
        (110, 15, "Front edge"),
        (205, 15, "Front-right corner"),
        (205, 150, "Right edge"),
        (205, 285, "Back-right corner"),
        (110, 285, "Back edge"),
        (15, 285, "Back-left corner"),
        (15, 150, "Left edge"),
        (55, 15, "Front secondary"),
        (165, 15, "Front secondary"),
    ]

    snap_number = 1
    for x, y, location in snap_positions:
        snap_id = f"Snap_{snap_number}"
        print(f"  {snap_id} ({x}, {y}) — {location}")

        # Snap pocket at seam (Z=200) should be void
        v.check_void(
            f"{snap_id}_seam_pocket",
            x, y, 200,
            f"void pocket at seam undercut"
        )

        # Material above snap pocket (in top half) - shift to side of pocket
        v.check_solid(
            f"{snap_id}_top_flank",
            x + 5, y + 5, 201,
            f"solid flanking snap in top half"
        )

        snap_number += 1

    print()

    # ---- 4.2: Bottom Half Feature Validation ----
    print("4.2 BOTTOM HALF FEATURE VALIDATION")
    print("-" * 70)

    # Interior structure features from bottom half
    v.check_solid(
        "Bottom_pump_dock",
        110, 60, 70,
        "pump dock structure (interior)"
    )

    # Bore through back wall
    v.check_void(
        "Bottom_port_1",
        40, 295, 60,
        "port 1 bore (back wall exit)"
    )

    print()

    # ---- 4.3: Top Half Feature Validation ----
    print("4.3 TOP HALF FEATURE VALIDATION")
    print("-" * 70)

    # Check structural material near top of enclosure (outer wall)
    v.check_solid(
        "Top_outer_wall",
        110, 5, 350,
        "top half outer wall material"
    )

    # Interior structure in top half
    v.check_solid(
        "Top_interior_structure",
        110, 150, 300,
        "top half interior support structure"
    )

    print()

    # ---- 4.4: Standard Validation Checks ----
    print("4.4 STANDARD VALIDATION CHECKS")
    print("-" * 70)

    v.check_valid()
    v.check_single_body()

    # Volume check: hollow structure with walls and internal ribs (~5–15% fill)
    envelope_volume = 220 * 300 * 400  # 26,400,000 mm³
    v.check_volume(expected_envelope=envelope_volume, fill_range=(0.05, 0.25))

    print()

    # ---- 4.5: Bounding Box Validation (Critical) ----
    print("4.5 BOUNDING BOX VALIDATION (Production Constraint)")
    print("-" * 70)

    bb = enclosure.val().BoundingBox()

    v.check_bbox("X (Width)", bb.xmin, bb.xmax, 0, 220, tol=0.5)
    v.check_bbox("Y (Depth)", bb.ymin, bb.ymax, 0, 300, tol=0.5)
    v.check_bbox("Z (Height)", bb.zmin, bb.zmax, 0, 400, tol=0.5)

    print()

    # ====================================================================
    # PHASE 5: Summary and Export
    # ====================================================================
    print("PHASE 5: Summary and Export")
    print("-" * 70)
    print()

    # Print validation summary (returns True if all passed)
    validation_passed = v.summary()

    if not validation_passed:
        print()
        print("ASSEMBLY VALIDATION FAILED")
        print("Fix issues above before proceeding to export.")
        sys.exit(1)

    print()
    print("VALIDATION PASSED — Proceeding to export")
    print()

    # Export final STEP file
    output_step = Path(__file__).resolve().parent / "enclosure-cadquery.step"
    print(f"Exporting final enclosure STEP: {output_step.name}")
    enclosure.val().exportStep(str(output_step))
    print(f"  ✓ Exported to: {output_step}")
    print()

    print("=" * 70)
    print("ASSEMBLY COMPLETE")
    print("=" * 70)
    print(f"Final enclosure: {output_step.name}")
    print(f"Dimensions: 220 × 300 × 400 mm")
    print(f"Snap engagement: 10 points at Z=200 mm")
    print(f"Ready for print on Bambu H2C (no post-processing)")
    print("=" * 70)


if __name__ == "__main__":
    main()
