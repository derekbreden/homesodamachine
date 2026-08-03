"""CPC LCD10004 / LCD15004 1/4" NPT Valved Coupling Body (LC Series,
chrome-plated brass, Buna-N o-rings, acetal valves, 316 SS valve
spring). Vacuum to 250 psi, -40°F to 180°F. Sourced from Colder
Products Company.

The appliance's right-side CO2 inlet in the enclosure iso line-art;
the in-wall receptacle connects here. External geometry only — the
internal valve mechanism is not modeled.

Coordinate convention:
  Y = coupling axis. +Y = forward (toward the coupling mouth). -Y =
      back (into the appliance wall at install).
  Origin = the back face of the hex section (the mounting plane; the
      wall sits here at install).
  +Z = up (thumb-latch direction in installed orientation).
  X = tangential to the coupling axis, completing the right-handed
      frame.

Geometry zones from -Y to +Y:
  Y = -thread_length to Y = 0: 1/4" NPT thread shank, a plain
      cylinder at the nominal major Ø.
  Y = 0 to Y = hex_length: 3/4" hex section for wrench.
  Y = hex_length to Y = hex_length + body_length: body cup with the
      coupling mouth on its +Y face.
  Latch: one piece of thin sheet metal, bent 90° at the body cup's
      top-front edge into (a) a pill-shaped thumb pad on the +Z top
      of the body cup, and (b) a flat disk on the +Y front face,
      with a hole through it sized to the coupling mouth.

External dimensions from the CPC LC Series datasheet (in mm):
  Body OD: [19.1](BODY_D) (Ø 0.75")
  Hex: [19.05](HEX_FLATS) flat-to-flat (3/4")
  Total length: [29.2](TOTAL_LENGTH) (B = 1.15") = thread + hex + body.
  Thread length: [12.7](THREAD_LENGTH) (0.50")

Run:
    tools/cad-venv/bin/python hardware/reference/co2-coupling-body/co2_coupling_body.py
"""

import math
import sys
import cadquery as cq
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_step
from world_workplane import xy_plane_z_up, xz_plane_y_up
from docgen import substitute_py_comments


# External dimensions from the CPC LC Series datasheet.
body_d = 19.1                           # body cup OD
body_length = 11.5                      # cup length along axis
hex_flats = 19.05                       # 3/4" hex, flat-to-flat
hex_length = 5.0                        # hex section thickness along axis
hex_points = hex_flats * 2 / math.sqrt(3)   # point-to-point

thread_d = 13.7                         # 1/4" NPT major Ø (~0.540")
thread_length = 12.7                    # 0.50" thread engagement

# Coupling mouth — circular recess at the +Y front face of the body
# cup where the male stem plugs in. Inside the real part three collet
# jaws around this bore grip the stem; the collet is not modeled.
mouth_d = 13.0                          # coupling bore inner diameter
mouth_depth = 9.0                       # recess depth into the body cup

# Latch — single piece of thin sheet metal bent into two pieces: a
# thumb pad on the +Z top of the body cup, and a flat disk covering
# the body cup's +Y front face. The two pieces share a 90° bend at
# the body cup's top-front edge.
latch_thickness = 0.8                   # sheet-metal thickness (radial out
                                        # under the pad; axial out from the
                                        # front plate)

# Pad — pill / slot shape on the +Z top of the body cup. The pill's
# long axis runs tangentially (across the body), not along the
# coupling axis. The pad is biased toward the +Y front so it joins
# the front plate at the bent corner.
pad_length = 14.0                       # tangential (X) — full pill length incl. rounded ends
pad_diameter = 9.62                     # axial (Y) — pill width = rounded-end diameter
latch_cantilever = latch_thickness      # pad's +Y lands flush with the front plate's +Y so
                                        # they meet at a clean 90° outer corner (the bend)

# Front plate — flat disk (very thin cylinder) covering the body cup's
# +Y front face, with a hole through it sized to the coupling mouth.
# The pad + disk together are offset in +Z from the body axis, so the
# disk's hole sits above the coupling mouth, half-covering it.
latch_z_offset = 1.0                    # +Z rise of pad + disk vs body axis

# Connector tab — rectangular protrusion from the disk's top edge that
# carries up and meets the pad at the bent corner, giving the front
# plate a flat top edge flush with the pad. Same sheet-metal thickness
# as disk and pad.
connector_width = 8.0                   # tangential (X)
bend_radius = latch_thickness            # fillet on the outer + inner edges
                                        # of the 90° bend between tab and pad


# Derived geometry.
front_face_y = hex_length + body_length          # +Y front face of the body cup
pad_top_z = body_d / 2 + latch_z_offset + latch_thickness
pad_front_y = front_face_y + latch_cantilever
pad_center_y = pad_front_y - pad_diameter / 2


def build_hex_section():
    """3/4" hex wrench section, y=0 to y=hex_length, on xz_plane_y_up
    (perpendicular to the coupling axis +Y)."""
    return (
        cq.Workplane(xz_plane_y_up)
        .polygon(6, hex_points)
        .extrude(hex_length)
        .rotate((0, 0, 0), (0, 1, 0), 0)
    )


def build_body_cup():
    """Body cup cylinder atop the hex, with the coupling-mouth recess —
    a circular bore at the +Y front face where the male stem plugs in —
    cut into it."""
    body = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=hex_length)
        .circle(body_d / 2)
        .extrude(body_length)
    )
    mouth = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=front_face_y)
        .circle(mouth_d / 2)
        .extrude(-mouth_depth)
    )
    return body.cut(mouth)


def build_thread_shank():
    """NPT thread shank below the hex (in -Y), a plain cylinder at the
    nominal major Ø."""
    return (
        cq.Workplane(xz_plane_y_up)
        .circle(thread_d / 2)
        .extrude(-thread_length)
    )


def build_latch_front_plate():
    """Flat disk over the body cup's +Y face — disk ∪ connector tab −
    coupling-mouth hole — sitting latch_z_offset above the body axis.

    xz_plane_y_up has local Y = -world Z (chirality flip), so the tab at
    world +Z (the latch's up direction) sits at local -Y in the sketch."""
    tab_top_local_z = pad_top_z - latch_z_offset
    tab_bottom_local_z = 0.0
    tab_height_local = tab_top_local_z - tab_bottom_local_z
    tab_center_local_z = (tab_bottom_local_z + tab_top_local_z) / 2
    front_sketch = (
        cq.Sketch()
        .circle(body_d / 2)
        .push([(0, -tab_center_local_z)])  # local -Y = world +Z (chirality flip)
        .rect(connector_width, tab_height_local, mode="a")
        .reset()
        .circle(mouth_d / 2, mode="s")
    )
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=front_face_y)
        .center(0, -latch_z_offset)
        .placeSketch(front_sketch)
        .extrude(latch_thickness)
    )


def build_latch_pad():
    """Thumb pad — a pill (slot) on the body cup's +Z top, biased toward
    +Y so it meets the front plate's tab at the bend. On xy_plane_z_up:
    local +X is world +X (the pill's tangential long axis); local +Y is
    world +Y (the coupling-axis short dim)."""
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=body_d / 2 + latch_z_offset)
        .center(0, pad_center_y)
        .slot2D(length=pad_length, diameter=pad_diameter)
        .extrude(latch_thickness)
    )


def build_co2_coupling_body(fillet_bend=True):
    """Coupling body at canonical origin, mounting plane at y=0, axis
    along +Y. The latch is one bent sheet-metal piece — front plate plus
    thumb pad sharing a 90° bend; fillet_bend rounds that bend."""
    hex_part = build_hex_section()
    body = build_body_cup()
    thread = build_thread_shank()
    front_plate = build_latch_front_plate()
    pad = build_latch_pad()

    result = hex_part.union(body)
    result = result.union(thread)
    result = result.union(front_plate)
    result = result.union(pad)

    if fillet_bend:
        # The bend has two edges (in X): the OUTER corner where the
        # pad's top meets the tab's front, and the INNER corner where
        # the pad's bottom meets the tab's back. Filleted, the sharp
        # 90° corner is a sheet-metal bend of constant thickness.
        outer_corner_z = pad_top_z
        outer_corner_y = pad_front_y
        inner_corner_z = pad_top_z - latch_thickness
        inner_corner_y = front_face_y
        result = (
            result
            .edges(cq.NearestToPointSelector((0, outer_corner_y, outer_corner_z)))
            .fillet(bend_radius)
        )
        result = (
            result
            .edges(cq.NearestToPointSelector((0, inner_corner_y, inner_corner_z)))
            .fillet(bend_radius * 0.5)
        )
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

    substitute_py_comments(
        _here,
        variables={
            "BODY_D": f"{body_d:.4g}",
            "HEX_FLATS": f"{hex_flats:.4g}",
            "TOTAL_LENGTH": f"{thread_length + hex_length + body_length:.4g}",
            "THREAD_LENGTH": f"{thread_length:.4g}",
        },
        expected_counts={
            "BODY_D": 1,
            "HEX_FLATS": 1,
            "TOTAL_LENGTH": 1,
            "THREAD_LENGTH": 1,
        },
    )
    print(f"-> {_here.name} (self)")


if __name__ == "__main__":
    main()
