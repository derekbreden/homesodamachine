"""Line-art reference solid of the 1/4" push-to-connect through-wall
(bulkhead) union — a simplified stand-in for the McMaster-Carr 51055K3
(gray acetal, NSF/ANSI 61 for drinking water).

The vendor CAD (`51055K3-no-threads.step` in this directory) carries the
full push-to-connect detail: a stepped collet barrel, a release-ring
groove, and a snap cap, which project as a stack of concentric circles
too busy for the iso line-art. This module rebuilds the part as a few
coaxial cylinders whose diameters and lengths are measured from that
STEP, so the geometry stays correct while the silhouette reduces to a
wide body, a release ring, and the tube port — three concentric
circles, matching the altitude of the CO2 coupling body's cup + mouth.

Measured from the vendor STEP (mm):
  Flange / collet body OD: 22.86 (0.90" envelope; the Ø22.86 flange and
      the Ø20.94 collet barrel behind it are merged into one body)
  Release ring OD: 11.43
  Threading / panel pass-through OD: 17.14 (0.67" mounting hole)
  Tube port bore: 6.35 (1/4" tube OD)
  Overall length: 34.29 (1.36")

Coordinate convention:
  Y = tube-flow axis. +Y = outward (toward the proud body's release ring
      and tube port). -Y = inward (threading and the far end).
  Origin = the body's panel-seating face (its inner face). The body and
      everything beyond it sit at y ≥ 0; the threading and far end sit
      at y < 0.
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
from world_workplane import xz_plane_y_up


# Diameters measured from the vendor STEP.
BODY_D = 22.86       # flange + collet barrel, merged into one body
RING_D = 11.43       # release ring
THREAD_D = 17.14     # threading / panel pass-through
PORT_D = 6.35        # 1/4" tube port bore

# Axial lengths. The two ends are identical (body + release ring); the
# threading spans the middle. Total = 2*(BODY_LEN + RING_LEN) + THREAD_LEN
# = 34.29, the vendor overall length.
BODY_LEN = 5.0
RING_LEN = 4.5
THREAD_LEN = 15.29
PORT_DEPTH = 4.0     # bore recess into each release-ring end face

# The seating face is the proud body's inner face. Everything outward of
# it (one body + release ring) stands proud; this is the length that
# clears a panel.
PROUD_LENGTH = BODY_LEN + RING_LEN


def build_jg_bulkhead_union():
    """Build the simplified union in the canonical frame (axis +Y,
    seating face at y=0, proud features at y ≥ 0). Returns a cq.Workplane
    wrapping the single solid."""
    # Proud body (flange + collet barrel), y = 0 .. BODY_LEN.
    near_body = (
        cq.Workplane(xz_plane_y_up)
        .circle(BODY_D / 2)
        .extrude(BODY_LEN)
    )
    # Release ring beyond the body, y = BODY_LEN .. PROUD_LENGTH.
    near_ring = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=BODY_LEN)
        .circle(RING_D / 2)
        .extrude(RING_LEN)
    )
    # Tube port — bore recessed into the +Y end face.
    near_port = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=PROUD_LENGTH)
        .circle(PORT_D / 2)
        .extrude(-PORT_DEPTH)
    )
    near_ring = near_ring.cut(near_port)

    # Threading / panel pass-through, y = -THREAD_LEN .. 0.
    threading = (
        cq.Workplane(xz_plane_y_up)
        .circle(THREAD_D / 2)
        .extrude(-THREAD_LEN)
    )

    # Far end mirrors the near end: body then release ring then port.
    far_body = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=-THREAD_LEN)
        .circle(BODY_D / 2)
        .extrude(-BODY_LEN)
    )
    far_ring = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=-THREAD_LEN - BODY_LEN)
        .circle(RING_D / 2)
        .extrude(-RING_LEN)
    )
    far_port = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=-THREAD_LEN - BODY_LEN - RING_LEN)
        .circle(PORT_D / 2)
        .extrude(PORT_DEPTH)
    )
    far_ring = far_ring.cut(far_port)

    result = near_body.union(near_ring)
    result = result.union(threading)
    result = result.union(far_body)
    result = result.union(far_ring)
    return result


def main():
    part = build_jg_bulkhead_union()
    bb = part.val().BoundingBox()
    print("1/4\" push-to-connect through-wall union — simplified (McMaster 51055K3)")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Proud of seating face: {bb.ymax:.2f} mm")
    print(f"  Body Ø {BODY_D} / release ring Ø {RING_D} / port Ø {PORT_D}")
    print(f"  Solid valid: {part.val().isValid()}")

    here = Path(__file__).resolve().parent
    out = here / "jg-bulkhead-union.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
