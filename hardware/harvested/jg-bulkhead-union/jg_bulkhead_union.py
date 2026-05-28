"""Reference solid of the John Guest 1/4" Bulkhead Union (PP1208E
black polypropylene / PI1208S gray acetal / CI1208W white acetal —
same body, different material and color). Push-to-connect at both
ends, NSF-51 / NSF-61, 150 psi @ 70 F.

Not a fabricated part — sourced from John Guest. Used as the envelope
reference for a panel-mounted 1/4" tube pass-through: the body seats
in a panel hole with one hex flange and an O-ring on the wet side,
and a separate locknut clamps the panel from the dry side.

External geometry only — the spring-steel collet grippers and the
internal O-ring seats don't show in the iso projection and aren't
modeled. Threading is modeled as a plain cylinder at the major
diameter.

Coordinate convention:
  Y = tube-flow axis. +Y = outward (toward the near flange's release
      ring and tube push-in port, the end that stands proud of a
      panel). -Y = inward (the far flange and far release ring).
  Origin = the outer face of the near hex flange (the panel-seating
      reference face).
  +Z = up. The body is rotationally symmetric about Y, so the hex
      clocking is a free choice; the flats are clocked so two land
      horizontal (top and bottom).
  X = tangential to the axis, completing the right-handed frame.

Geometry zones from +Y to -Y:
  Y = release_ring_length to Y = 0: near release ring (push-to-connect
      collet release sleeve). Its +Y end face carries the tube
      push-in port — a 1/4" tube-OD bore recessed into it.
  Y = 0 to Y = -flange_length: near hex flange (panel-seating).
  Y = -flange_length to Y = -(flange_length + threading_length):
      threading section (locknut threads on this).
  Y = -(flange_length + threading_length) to
      Y = -(2 * flange_length + threading_length): far hex flange.
  Y = -(2 * flange_length + threading_length) to
      Y = -(2 * flange_length + threading_length + release_ring_length):
      far release ring, with its tube push-in port on its -Y end face.
  Locknut: a separate hex prism with a through-bore, sitting on the
      threading section against the near flange's inner face.

External dimensions from the JG catalog and drawing-derived
measurement (hardware/off-the-shelf-parts/jg-bulkhead-union):
  Overall length: 34.5 (catalog 1.36")
  Flange across-flats: 22.9 (catalog 0.90" envelope)
  Mounting hole / threading major diameter: 17.0 (catalog 0.67")
  Tube OD: 6.35 (1/4")

Run:
    tools/cad-venv/bin/python hardware/harvested/jg-bulkhead-union/jg_bulkhead_union.py
"""

import math
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


# External dimensions from the JG catalog and drawing-derived
# measurement.
release_ring_d = 9.57                    # release-ring OD (push-to-connect sleeve)
release_ring_length = 3.5                # release-ring length along axis

flange_flats = 22.9                      # hex flange across-flats (envelope OD)
flange_length = 8.5                      # hex flange thickness along axis
flange_points = flange_flats * 2 / math.sqrt(3)   # point-to-point (CadQuery polygon takes circumscribed Ø)

threading_d = 17.0                       # threading major Ø (fits 0.67" panel hole)
threading_length = 10.0                  # threading span between the two flanges

tube_od = 6.35                           # 1/4" tube OD — push-in port bore
tube_port_depth = 4.0                    # port recess depth into the release-ring
                                         # end face (deep enough to read as a hole
                                         # in projection, not a shallow dimple)

# Locknut — separate hex piece, threads onto the central threading and
# clamps the panel against one flange. Modeled as a hex prism with a
# through-bore at the threading major Ø, sitting against the near
# flange's inner face.
locknut_flats = 18.0                     # locknut across-flats
locknut_thickness = 5.0                  # locknut thickness along axis
locknut_points = locknut_flats * 2 / math.sqrt(3)  # point-to-point (circumscribed Ø)
locknut_bore_d = threading_d             # through-bore at the threading major Ø


# Axial boundaries along +Y (origin = near flange outer face).
_near_ring_outer_y = release_ring_length                     # +Y tip of near release ring
_near_flange_inner_y = -flange_length                        # near flange / threading boundary
_threading_inner_y = _near_flange_inner_y - threading_length  # threading / far flange boundary
_far_flange_inner_y = _threading_inner_y - flange_length     # far flange / far ring boundary
_far_ring_outer_y = _far_flange_inner_y - release_ring_length  # -Y tip of far release ring


def build_jg_bulkhead_union():
    """Build the bulkhead union at canonical origin (near flange outer
    face at y=0, axis along +Y). Returns a cq.Workplane wrapping the
    union of both release rings, both hex flanges, the threading
    section, and the locknut. The locknut stays a distinct solid in the
    same Workplane."""
    # Near hex flange, y=0 to y=-flange_length. Sketched on
    # xz_plane_y_up (the plane perpendicular to the axis +Y), extruded
    # in -Y. CadQuery's polygon places a vertex at the +X axis; the
    # 30 rotation about Y lands the flats top and bottom, matching how
    # a wrench seats from above.
    near_flange = (
        cq.Workplane(xz_plane_y_up)
        .polygon(6, flange_points)
        .extrude(-flange_length)
        .rotate((0, 0, 0), (0, 1, 0), 30)
    )

    # Near release ring, on the +Y side of the near flange.
    near_ring = (
        cq.Workplane(xz_plane_y_up)
        .circle(release_ring_d / 2)
        .extrude(release_ring_length)
    )

    # Tube push-in port — recess into the +Y end face of the near
    # release ring.
    near_port = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=_near_ring_outer_y)
        .circle(tube_od / 2)
        .extrude(-tube_port_depth)
    )
    near_ring = near_ring.cut(near_port)

    # Threading section, on the -Y side of the near flange.
    threading = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=_near_flange_inner_y)
        .circle(threading_d / 2)
        .extrude(-threading_length)
    )

    # Far hex flange, mirror of the near flange, on the -Y side of the
    # threading. Same clocking.
    far_flange = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=_threading_inner_y)
        .polygon(6, flange_points)
        .extrude(-flange_length)
        .rotate((0, 0, 0), (0, 1, 0), 30)
    )

    # Far release ring, on the -Y side of the far flange.
    far_ring = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=_far_flange_inner_y)
        .circle(release_ring_d / 2)
        .extrude(-release_ring_length)
    )

    # Tube push-in port — recess into the -Y end face of the far
    # release ring.
    far_port = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=_far_ring_outer_y)
        .circle(tube_od / 2)
        .extrude(tube_port_depth)
    )
    far_ring = far_ring.cut(far_port)

    # Locknut — hex prism with a through-bore, sitting on the threading
    # against the near flange's inner face (y=-flange_length), extending
    # -Y by locknut_thickness.
    locknut = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=_near_flange_inner_y)
        .polygon(6, locknut_points)
        .extrude(-locknut_thickness)
        .rotate((0, 0, 0), (0, 1, 0), 30)
    )
    locknut_bore = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=_near_flange_inner_y)
        .circle(locknut_bore_d / 2)
        .extrude(-locknut_thickness)
    )
    locknut = locknut.cut(locknut_bore)

    result = near_flange.union(near_ring)
    result = result.union(threading)
    result = result.union(far_flange)
    result = result.union(far_ring)
    result = result.union(locknut)
    return result


def main():
    union = build_jg_bulkhead_union()

    bb = union.val().BoundingBox()
    overall_length = 2 * flange_length + threading_length + 2 * release_ring_length
    print("John Guest PP1208E / PI1208S / CI1208W — 1/4\" Bulkhead Union")
    print(f"  Bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Release ring: Ø {release_ring_d} × {release_ring_length} mm "
          f"(tube port Ø {tube_od})")
    print(f"  Hex flange:   {flange_flats} mm flat-to-flat × {flange_length} mm")
    print(f"  Threading:    Ø {threading_d} × {threading_length} mm (simplified, not threaded)")
    print(f"  Locknut:      {locknut_flats} mm flat-to-flat × {locknut_thickness} mm "
          f"(bore Ø {locknut_bore_d})")
    print(f"  Overall length: {overall_length} mm")

    here = Path(__file__).resolve().parent
    out = here / "jg-bulkhead-union.step"
    export_step(union, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
