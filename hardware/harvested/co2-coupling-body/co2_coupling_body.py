"""Reference solid of the CPC LCD10004 / LCD15004 1/4" NPT Valved
Coupling Body (LC Series, chrome-plated brass, Buna-N o-rings,
acetal valves, 316 SS valve spring). Vacuum to 250 psi, -40°F to
180°F.

Not a fabricated part — sourced from Colder Products Company. Used
as the envelope reference for the appliance's right-side CO2 inlet
in the enclosure iso line-art, and as a placeholder for future
internal-plumbing geometry where the in-wall receptacle connects.

External geometry only — the internal valve mechanism (thumb-latch
spring, acetal valve poppet, sealing geometry) doesn't show in the
iso projection and isn't modeled.

Coordinate convention:
  Z = coupling axis. +Z = forward (toward the customer / coupling
      mouth). -Z = back (into the appliance wall at install).
  Origin = the back face of the hex section (the mounting plane;
      this is where the wall sits at install, give or take whether
      the hex is recessed or proud).
  +Y = up (thumb-latch direction in installed orientation; the
      coupling rotates freely around its axis so this is just a
      clocking choice for the model).
  X = tangential to the coupling axis, completing the right-handed
      frame.

Geometry zones from -Z to +Z:
  Z = -thread_length to Z = 0: 1/4" NPT thread shank (modeled as a
      plain cylinder at the nominal major Ø; not actually threaded).
  Z = 0 to Z = hex_length: 3/4" hex section for wrench.
  Z = hex_length to Z = hex_length + body_length: chrome-plated brass
      body cup with the coupling mouth on its +Z face.
  On +Y top of the body cup: thumb-latch bump (rectangular stand-in
      for the actual curved CPC latch).

External dimensions match the CPC LC Series datasheet (in mm):
  Body OD: 19.1 (Ø 0.75")
  Hex: 19.05 flat-to-flat (3/4")
  Total length: 29.2 (B = 1.15") = thread + hex + body.
  Thread length: 12.7 (0.50")

Run:
    tools/cad-venv/bin/python hardware/harvested/co2-coupling-body/co2_coupling_body.py
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
from _cadq_export import export_step


# External dimensions from the CPC LC Series datasheet.
body_d = 19.1                           # body cup OD
body_length = 11.5                      # cup length along axis
hex_flats = 19.05                       # 3/4" hex, flat-to-flat
hex_length = 5.0                        # hex section thickness along axis
hex_points = hex_flats * 2 / math.sqrt(3)   # point-to-point (CadQuery polygon takes circumscribed Ø)

thread_d = 13.7                         # 1/4" NPT major Ø (~0.540")
thread_length = 12.7                    # 0.50" thread engagement

# Coupling mouth — circular recess at the +Z front face of the body
# cup where the male stem plugs in. Inside the real part there are
# three collet jaws around this bore that grip the stem; collet
# geometry isn't drawn in iso line-art and isn't modeled.
mouth_d = 13.0                          # coupling bore inner diameter
mouth_depth = 9.0                       # recess depth into the body cup
                                        # (deep enough to read as a hole
                                        # in iso, not a shallow dimple)

# Latch — single piece of thin sheet metal bent into two visible
# pieces: a thumb pad on the +Y top of the body cup, and a "front
# plate" strap running down the +Z front face. The thumb pad and
# front plate share a 90° bend at the body cup's top-front edge.
# Pressing the pad slides the whole strap forward / down, releasing
# the latch mechanism inside the body. Sized from photos of the
# LC10004 / LCD10004.
latch_thickness = 0.8                   # sheet-metal thickness (Y above pad,
                                        # Z out from front plate)
# Pad — pill / slot shape sitting on top of the body cup, biased
# toward the +Z front. Cantilevers ~2 mm past the front face so it
# joins cleanly to the front plate at the bent corner.
latch_l = 8.0                           # along body axis (Z) — pad full length incl. rounded ends
latch_w = 5.0                           # tangential (X) — pill width = rounded-end diameter
latch_cantilever = 2.0                  # how far the pad sticks past the body cup's front face
# Front plate — rectangular strap on the front face, sharing the
# pad's tangential width.
front_plate_drop = 12.0                 # how far down the front face it extends (Y)


def build_co2_coupling_body():
    """Build the coupling body at canonical origin (mounting plane at
    z=0, axis along +Z). Returns a cq.Workplane wrapping the solid."""
    # Hex section, z=0 to z=hex_length. CadQuery's polygon places a
    # vertex at the +X axis; rotate by 30° around the axis so the
    # flats land top/bottom — matches how the part installs with a
    # wrench from above.
    hex_part = (
        cq.Workplane("XY")
        .polygon(6, hex_points)
        .extrude(hex_length)
        .rotate((0, 0, 0), (0, 0, 1), 30)
    )

    # Body cup cylinder, on top of the hex.
    body = (
        cq.Workplane("XY")
        .workplane(offset=hex_length)
        .circle(body_d / 2)
        .extrude(body_length)
    )

    # Coupling mouth — recess at the +Z front face of the body cup.
    front_face_z = hex_length + body_length
    mouth = (
        cq.Workplane("XY")
        .workplane(offset=front_face_z)
        .circle(mouth_d / 2)
        .extrude(-mouth_depth)
    )
    body = body.cut(mouth)

    # NPT thread shank, below the hex.
    thread = (
        cq.Workplane("XY")
        .circle(thread_d / 2)
        .extrude(-thread_length)
    )

    # Latch — pill-shaped thumb pad on top + rectangular front plate
    # on the front face, modeled as two thin solids that overlap at
    # the top-front corner so union merges them into a single bent-
    # sheet shape.

    # Thumb pad: pill (slot) on a workplane whose local +x is the body
    # axis (world +Z) and normal is body radial (world +Y). slot2D's
    # length runs along local +x; diameter is the rounded-end width.
    latch_front_z = front_face_z + latch_cantilever
    latch_back_z = latch_front_z - latch_l
    latch_z_mid = (latch_front_z + latch_back_z) / 2
    pad_plane = cq.Plane(
        origin=(0, body_d / 2, latch_z_mid),
        xDir=(0, 0, 1),
        normal=(0, 1, 0),
    )
    pad = (
        cq.Workplane(pad_plane)
        .slot2D(length=latch_l, diameter=latch_w, angle=0)
        .extrude(latch_thickness)
    )

    # Front plate: thin rectangle on the +Z front face of the body
    # cup, sharing the pad's tangential width. Top edge runs up to
    # (body_d/2 + latch_thickness) so it overlaps with the pad in the
    # corner region — the union then reads as one continuous L-shape.
    plate_top_y = body_d / 2 + latch_thickness
    plate_bottom_y = body_d / 2 - front_plate_drop
    plate_corner = cq.Vector(
        -latch_w / 2,
        plate_bottom_y,
        front_face_z,
    )
    front_plate = cq.Solid.makeBox(
        latch_w,
        plate_top_y - plate_bottom_y,
        latch_thickness,
        pnt=plate_corner,
    )

    # Union order matters here: with the pad unioned BEFORE the front
    # plate, OCCT's boolean ends up dropping everything but the corner
    # overlap region. Unioning the pad last avoids it. (Cause unclear;
    # likely an OCCT quirk with the slot solid plus the L-overlap.)
    result = hex_part.union(body)
    result = result.union(thread)
    result = result.union(front_plate)
    result = result.union(pad)
    return result


def main():
    body = build_co2_coupling_body()

    bb = body.val().BoundingBox()
    print("CPC LCD10004 / LCD15004 — 1/4\" NPT Valved Coupling Body")
    print(f"  Bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Body cup:     Ø {body_d} × {body_length} mm")
    print(f"  Hex:          {hex_flats} mm flat-to-flat × {hex_length} mm")
    print(f"  Thread:       Ø {thread_d} × {thread_length} mm (1/4\" NPT, simplified)")
    print(f"  Total length: {thread_length + hex_length + body_length} mm")

    here = Path(__file__).resolve().parent
    out = here / "co2-coupling-body.step"
    export_step(body, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
