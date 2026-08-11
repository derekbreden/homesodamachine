"""Line-art reference solid of the 1/4" push-to-connect through-wall
(bulkhead) union — the McMaster-Carr 51055K3 (gray acetal, NSF/ANSI 61
for drinking water), reduced to coaxial cylinders: a wide body, a
release ring, and the tube port — three concentric circles, which is
all of it a line drawing of the rear face can show.

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
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)
from _cadq_export import export_step
from _measuring import bores
from world_workplane import xz_plane_y_up

STEP = _here.parent / "jg-bulkhead-union.step"

BODY_D = 22.86       # flange + collet barrel
RING_D = 11.43       # release ring
THREAD_D = 17.14     # threading / panel pass-through
PORT_D = 6.35        # 1/4" tube port bore

# Body + release ring at each end, threading spanning the middle; the
# segments sum to the 34.29 overall length.
BODY_LEN = 5.0
RING_LEN = 4.5
THREAD_LEN = 15.29
PORT_DEPTH = 4.0     # bore recess into each release-ring end face

# Length standing proud of the seating face (one body + release ring),
# clearing the mounting panel.
PROUD_LENGTH = BODY_LEN + RING_LEN

# Seating planes along Y where the coaxial segments meet. The near end
# stands at y ≥ 0; the threading and far end sit at y ≤ 0, mirrored
# about Y = -THREAD_LEN/2.
near_body_to_ring_y = BODY_LEN
near_ring_face_y = PROUD_LENGTH
far_thread_to_body_y = -THREAD_LEN
far_body_to_ring_y = -THREAD_LEN - BODY_LEN
far_ring_face_y = -THREAD_LEN - BODY_LEN - RING_LEN


# --- What a panel owes this fitting -----------------------------------------
# The union clamps THROUGH a wall, so a panel carrying one owes it two things and they are
# different sizes: a hole the THREADING passes through, and face room for the NUT that clamps
# on it. The nut is the wider by half again, so a row spaced to the holes fouls on the metal.

def panel_hole_d(clearance: float) -> float:
    """The through-hole diameter, given the slip a panel wants around the threading."""
    return THREAD_D + clearance


def panel_footprint() -> tuple:
    """`(width, height)` the clamping nut takes on the panel FACE. Round, so one figure
    twice — and it is what crowds a neighbour, a wall or a ceiling."""
    return (BODY_D, BODY_D)


def flange_footprint() -> float:
    """What the OUTBOARD flange covers, and so what a port ring has to reach past to show.
    The flange and the collet barrel are one diameter on this fitting."""
    return BODY_D


def port(side: float) -> tuple:
    """One of the two 1/4" tube ports: `(position, outward axis)`, `side` picking the near
    (+Y, outboard) or far (−Y, inboard) end. The bore is recessed into the release ring's own
    face, and a tube is pushed in to that face."""
    face = near_ring_face_y if side > 0 else far_ring_face_y
    return ((0.0, face, 0.0), (0.0, 1.0 if side > 0 else -1.0, 0.0))


def stations_hold():
    """Hold the panel figures and both ports to `jg-bulkhead-union.step` — the file the
    enclosure seats through its wall, while it bores and spaces off these live figures.

    The nut is the body's widest section, an extent of that solid's box, and each port stands
    on the ring face at the end of it. The threading is neither: it is a turned face inside
    the envelope, so it is read off the bore itself."""
    solid = cq.importers.importStep(str(STEP)).val()
    bb = solid.BoundingBox()
    for what, claimed, actual in (("nut width", BODY_D, bb.xlen),
                                  ("nut height", BODY_D, bb.zlen),
                                  ("near port", near_ring_face_y, bb.ymax),
                                  ("far port", far_ring_face_y, bb.ymin)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"jg-bulkhead-union {what} is {claimed:g} and {STEP.name} carries "
                f"{actual:.4f} — a panel spaced or bored to this figure is spaced to a "
                f"fitting that is not there.")
    radii = sorted({r for _axis, r in bores(solid)})
    if not any(abs(2.0 * r - THREAD_D) <= 1e-6 for r in radii):
        raise ValueError(
            f"the threading is declared Ø{THREAD_D:g} and {STEP.name} turns no face at that "
            f"diameter — it carries Ø{[round(2 * r, 3) for r in radii]}. A panel bored to "
            f"the declared figure does not pass the barrel that is there.")


def build_near_end():
    """Body (Y=0 to near_body_to_ring_y) and release ring out to
    near_ring_face_y, bored PORT_DEPTH in from the ring face."""
    body = (
        cq.Workplane(xz_plane_y_up)
        .circle(BODY_D / 2)
        .extrude(BODY_LEN)
    )
    ring = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=near_body_to_ring_y)
        .circle(RING_D / 2)
        .extrude(RING_LEN)
    )
    port = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=near_ring_face_y)
        .circle(PORT_D / 2)
        .extrude(-PORT_DEPTH)
    )
    return body.union(ring.cut(port))


def build_threading():
    """Panel pass-through barrel spanning far_thread_to_body_y to Y=0."""
    return (
        cq.Workplane(xz_plane_y_up)
        .circle(THREAD_D / 2)
        .extrude(-THREAD_LEN)
    )


def build_far_end():
    """Mirror of the near end behind the panel: body from
    far_thread_to_body_y to far_body_to_ring_y, release ring out to
    far_ring_face_y, bored PORT_DEPTH in from the ring face."""
    body = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=far_thread_to_body_y)
        .circle(BODY_D / 2)
        .extrude(-BODY_LEN)
    )
    ring = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=far_body_to_ring_y)
        .circle(RING_D / 2)
        .extrude(-RING_LEN)
    )
    port = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=far_ring_face_y)
        .circle(PORT_D / 2)
        .extrude(PORT_DEPTH)
    )
    return body.union(ring.cut(port))


def build_jg_bulkhead_union():
    """The union as a single solid wrapped in a cq.Workplane."""
    return build_near_end().union(build_threading()).union(build_far_end())


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
