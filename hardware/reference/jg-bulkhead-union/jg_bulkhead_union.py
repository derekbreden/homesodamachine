"""Line-art reference solid of the 1/4" push-to-connect through-wall
(bulkhead) union — the McMaster-Carr 51055K3 (gray acetal, NSF/ANSI 61
for drinking water), reduced to coaxial cylinders: a wide body, a
release ring, and the tube port — three concentric circles at the
altitude of the CO2 coupling body's cup + mouth.

Real-world dimensions (mm):
  Flange / collet body OD: 22.86 (0.90")
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
    tools/cad-venv/bin/python hardware/reference/jg-bulkhead-union/jg_bulkhead_union.py
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


BODY_D = 22.86       # flange + collet barrel
RING_D = 11.43       # release ring
THREAD_D = 17.14     # threading / panel pass-through
PORT_D = 6.35        # 1/4" tube port bore

# Symmetric ends (body + release ring) with threading spanning the
# middle; the segments sum to the 34.29 overall length.
BODY_LEN = 5.0
RING_LEN = 4.5
THREAD_LEN = 15.29
PORT_DEPTH = 4.0     # bore recess into each release-ring end face

# Length standing proud of the seating face (one body + release ring),
# clearing the mounting panel.
PROUD_LENGTH = BODY_LEN + RING_LEN


def build_jg_bulkhead_union():
    """The union as a single solid wrapped in a cq.Workplane."""
    near_body = (
        cq.Workplane(xz_plane_y_up)
        .circle(BODY_D / 2)
        .extrude(BODY_LEN)
    )
    near_ring = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=BODY_LEN)
        .circle(RING_D / 2)
        .extrude(RING_LEN)
    )
    near_port = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=PROUD_LENGTH)
        .circle(PORT_D / 2)
        .extrude(-PORT_DEPTH)
    )
    near_ring = near_ring.cut(near_port)

    threading = (
        cq.Workplane(xz_plane_y_up)
        .circle(THREAD_D / 2)
        .extrude(-THREAD_LEN)
    )

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
