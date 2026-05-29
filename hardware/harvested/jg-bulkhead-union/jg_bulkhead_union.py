"""Reference solid of the 1/4" push-to-connect through-wall (bulkhead)
union, loaded from the McMaster-Carr 51055K3 vendor STEP (gray acetal,
NSF/ANSI 61 for drinking water, no-threads variant). Push-to-connect at
both ends; the body mounts through a panel hole and a locknut clamps it.

Not a fabricated part — the geometry is the vendor CAD, transformed into
the canonical frame below. The source export is `51055K3-no-threads.step`
in this directory. The no-threads variant is used so the central body
reads as a plain cylinder in the iso line-art instead of a hatch of
helical thread edges.

Source frame (as exported by McMaster): the tube-flow axis runs along Z,
the body centered on the origin (Z ∈ [-17.145, 17.145], length 34.29).
Radially: Ø22.86 flange at each end of the central Ø17.14 threading,
tapering to the Ø11.43 release ring + 1/4" tube port at each tip.

Canonical frame (returned by build_jg_bulkhead_union):
  Y = tube-flow axis. +Y = outward (toward the proud flange's release
      ring and tube port). -Y = inward (threading and the far end).
  Origin = the proud flange's panel-seating face (its inner face). The
      flange and everything beyond it sit at y ≥ 0; the threading and
      far end sit at y < 0.
  +Z = up. X completes the right-handed frame.

Run:
    tools/cad-venv/bin/python hardware/harvested/jg-bulkhead-union/jg_bulkhead_union.py
"""

import sys
import cadquery as cq
from pathlib import Path


_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)
from _cadq_export import export_step


# Vendor STEP, tube-flow axis along Z, body centered on the origin.
SOURCE_STEP = _here.parent / "51055K3-no-threads.step"

# Source-frame Z of the proud flange's inner (panel-seating) face — the
# step up from the Ø17.14 threading to the Ø22.86 flange on the +Z end.
SEAT_Z = 7.75

# Across-flange diameter (the widest feature), for callers sizing a
# marking disc around the fitting.
FLANGE_D = 22.86


def build_jg_bulkhead_union():
    """Load the vendor STEP and return it in the canonical frame (axis
    along +Y, the proud flange's seating face at y=0, proud features at
    y ≥ 0). Returns a cq.Workplane wrapping the single solid."""
    part = cq.importers.importStep(str(SOURCE_STEP)).val()
    # +Z (source axis) -> +Y (canonical axis): rotate -90° about X maps
    # (x, y, z) -> (x, z, -y), so the +Z tip becomes the +Y tip.
    part = part.rotate((0, 0, 0), (1, 0, 0), -90)
    # The seating face (source z = SEAT_Z) is now at world y = SEAT_Z;
    # slide it back to y = 0.
    part = part.translate((0, -SEAT_Z, 0))
    return cq.Workplane().add(part)


def main():
    part = build_jg_bulkhead_union()
    bb = part.val().BoundingBox()
    print("McMaster 51055K3 — 1/4\" push-to-connect through-wall union (no threads)")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Proud of seating face: {bb.ymax:.2f} mm")
    print(f"  Flange Ø {FLANGE_D} mm")
    print(f"  Solid valid: {part.val().isValid()}")


if __name__ == "__main__":
    main()
