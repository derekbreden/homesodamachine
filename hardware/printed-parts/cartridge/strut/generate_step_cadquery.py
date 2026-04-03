from pathlib import Path

import cadquery as cq

STRUT_W = 6.0
STRUT_H = 6.0
STRUT_L = 150.0

TIP_SIZE = 5.0
TIP_INSET = (STRUT_W - TIP_SIZE) / 2  # 0.5mm per side

GROOVE_SIZE = 5.75
GROOVE_INSET = (STRUT_W - GROOVE_SIZE) / 2  # 0.125mm per side

RAMP_L = 2.0
LEVER_GROOVE_L = 4.0     # matches lever PLATE_D
RELEASE_GROOVE_L = 5.0   # matches release plate PLATE_D

# Y layout (lever end at Y=0, release end at Y=150):
#   Y=0..2:     lever taper (5x5 -> 6x6)
#   Y=2..6:     lever groove (5.75x5.75)
#   Y=6..143:   body (6x6)
#   Y=143..148: release groove (5.75x5.75)
#   Y=148..150: release taper (6x6 -> 5x5)

oc = 0.1

# Full 6x6 bar
strut = cq.Workplane("XY").box(STRUT_W, STRUT_L, STRUT_H, centered=False)


def cut_groove(solid, y0, length, inset):
    """Step down to (STRUT - 2*inset) on all 4 faces over a Y span."""
    for x0, w in [(-oc, inset + oc), (STRUT_W - inset, inset + oc)]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(x0, y0, -oc))
            .box(w, length, STRUT_H + 2 * oc, centered=False)
        )
    for z0, h in [(-oc, inset + oc), (STRUT_H - inset, inset + oc)]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(-oc, y0, z0))
            .box(STRUT_W + 2 * oc, length, h, centered=False)
        )
    return solid


def cut_taper(solid, y_tip, y_body):
    """Cut lead-in taper on all 4 faces from y_tip (narrow) to y_body (full size)."""
    inset = TIP_INSET
    y_tip_oc = y_tip - oc if y_tip < y_body else y_tip + oc

    # ±X face wedges (XY plane, extruded in Z)
    for pts in [
        [(-oc, y_tip_oc), (inset, y_tip_oc), (-oc, y_body)],
        [(STRUT_W + oc, y_tip_oc), (STRUT_W - inset, y_tip_oc), (STRUT_W + oc, y_body)],
    ]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, -oc))
            .moveTo(*pts[0]).lineTo(*pts[1]).lineTo(*pts[2]).close()
            .extrude(STRUT_H + 2 * oc)
        )

    # ±Z face wedges (YZ plane, extruded in X)
    # YZ workplane: local X = world Y, local Y = world Z
    for pts in [
        [(y_tip_oc, -oc), (y_tip_oc, inset), (y_body, -oc)],
        [(y_tip_oc, STRUT_H + oc), (y_tip_oc, STRUT_H - inset), (y_body, STRUT_H + oc)],
    ]:
        solid = solid.cut(
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, 0, -oc))
            .moveTo(*pts[0]).lineTo(*pts[1]).lineTo(*pts[2]).close()
            .extrude(STRUT_W + 2 * oc)
        )

    return solid


# Lever groove (Y=2..6)
strut = cut_groove(strut, RAMP_L, LEVER_GROOVE_L, GROOVE_INSET)

# Release groove (Y=143..148)
strut = cut_groove(strut, STRUT_L - RAMP_L - RELEASE_GROOVE_L, RELEASE_GROOVE_L, GROOVE_INSET)

# Lever taper (Y=0..2, narrow at Y=0)
strut = cut_taper(strut, y_tip=0, y_body=RAMP_L)

# Release taper (Y=148..150, narrow at Y=150)
strut = cut_taper(strut, y_tip=STRUT_L, y_body=STRUT_L - RAMP_L)

# Export
output_path = Path(__file__).parent / "strut-cadquery.step"
cq.exporters.export(strut, str(output_path))
print(f"Exported {output_path}")
