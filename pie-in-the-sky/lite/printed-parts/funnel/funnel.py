"""Lite hopper funnel — the removable pour-through insert.

A wide funnel that drops into the top-wall opening to the right of the display
(cut by ../../enclosure/enclosure.py via `_hopper_hole`). You pour SodaStream
concentrate into it; it drains through its spout to V-B on the source-select
tray (fluid topology segment 4, "Hopper funnel bottom -> V-B-I"). A pour-through
guide with a small buffer, not a batch reservoir — what gets poured in is pumped
straight on to a bag.

The same idiom as the Kitchen edition's [hopper funnel](/hardware/printed-parts/zone-c/hopper-funnel/):
top to bottom,

  * a flat brim that overhangs the opening all around and rests on the enclosure
    top surface;
  * a tall straight rectangular chute — vertical walls, no slope — pressing the
    [3 mm](WALL) top wall at its top and hanging down into the reserve;
  * a shallow ramp from the bottom of that chute down to a round
    [6.35 mm](SPOUT_ID) spout (1/4", matching the pump tubing). The spout exits
    into the open air above the tallest content below the mouth (read live — the
    front bag-circuit tray), with room left below for a tube/barb fitting; a
    short flexible tube then carries the pour on to V-B. Like the Kitchen hopper,
    the spout does not land on V-B directly; the topology routes Hopper → V-B
    through the manifold.

The funnel shares the opening rectangle with the enclosure, so the collar always
matches the hole. It is built in enclosure world coordinates (+X right, +Y back,
+Z up), so it seats straight into the opening.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
_ENCL = _repo / "pie-in-the-sky" / "lite" / "enclosure"
sys.path.insert(0, str(_ENCL))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
import enclosure as E

# --- funnel parameters ------------------------------------------------------
brim_overhang = 3.0     # brim flange reach past the opening, all around
brim_thickness = 3.0    # flange thickness, resting on the enclosure top
collar_wall = 3.0       # straight press-fit collar wall (opening − bore)
chute_h = 30.0          # straight rectangular chute height — brim top down to the ramp
                        # start. Leaves the rest of the drop for a real funnel ramp.
neck_dx = 0.0           # spout centered under the opening — nothing below the mouth
                        # to dodge (only the front bag-circuit lid), so no offset
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
spout_tube = 6.0        # straight spout tube below the ramp tip — its length sets
                        # how far the Ø6.35 exit drops toward V-B
tip_clearance = 1.0     # gap left above the tallest content under the mouth
# The spout exits into the open air ABOVE the front trays (the whole mouth
# footprint has content under it — the front bag-circuit lid — so there is no
# clear column to drop into, unlike the Kitchen). Leave room below the exit for a
# tube/barb fitting and the flex-tube run back to V-B — but not so much that the
# ramp is squeezed out.
spout_fitting_gap = 8.0


# --- primitives -------------------------------------------------------------

def _box(w, d, z0, z1, cx, cy):
    """Axis-aligned box of footprint w×d centered at (cx, cy), spanning z[z0,z1]."""
    return (
        cq.Workplane("XY").box(w, d, z1 - z0, centered=(True, True, False))
        .translate((cx, cy, z0)).val()
    )


def _loft_rc(w0, d0, cx0, cy0, z0, r1, cx1, cy1, z1):
    """Loft from a rectangle down to a circle (centers may differ)."""
    return (
        cq.Workplane("XY", origin=(cx0, cy0, z0))
        .rect(w0, d0)
        .workplane(offset=z1 - z0).center(cx1 - cx0, cy1 - cy0)
        .circle(r1)
        .loft(combine=True)
        .val()
    )


def _cyl(r, z_top, z_bot, cx, cy):
    return cq.Solid.makeCylinder(r, z_top - z_bot, cq.Vector(cx, cy, z_bot), cq.Vector(0, 0, 1))


# --- the funnel -------------------------------------------------------------

def _content_top(x0, x1, y0, y1):
    """One mm above the tallest placed content whose footprint underlies the given
    rectangle — read live, so the funnel tracks the packing."""
    top = 0.0
    for shape, _c in E._contents.build().values():
        b = shape.BoundingBox()
        if min(b.xmax, x1) > max(b.xmin, x0) and min(b.ymax, y1) > max(b.ymin, y0):
            top = max(top, b.zmax)
    return top + tip_clearance


def build():
    inner, outer, _yj, _cf = E._dims()
    iz1, oz1 = inner[5], outer[5]
    x0, x1, y0, y1 = E._hopper_hole(inner, outer)
    w, d = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    bore_w, bore_d = w - 2.0 * collar_wall, d - 2.0 * collar_wall
    top_z = oz1 + brim_thickness                       # brim top = outermost point
    spout_or = spout_id / 2.0 + spout_wall
    ncx = cx + neck_dx                                 # spout/neck, shifted in X
    ramp_top_z = top_z - chute_h                        # straight chute bottom = ramp start

    # The ramp necks to the round spout, whose straight tube exits a fitting-gap
    # above the tallest content under the mouth (read live), leaving open air for a
    # tube/barb to attach; a flexible tube then carries the Ø6.35 exit on toward V-B.
    end_z = _content_top(x0, x1, y0, y1) + spout_fitting_gap
    neck_z = end_z + spout_tube            # the round neck, one tube-length up

    # Outer: brim flange, a tall straight rectangular chute, a shallow ramp down to
    # the +X-offset spout, straight spout tube.
    solid = (
        _box(w + 2.0 * brim_overhang, d + 2.0 * brim_overhang, oz1, top_z, cx, cy)
        .fuse(_box(w, d, ramp_top_z, oz1, cx, cy))
        .fuse(_loft_rc(w, d, cx, cy, ramp_top_z, spout_or, ncx, cy, neck_z))
        .fuse(_cyl(spout_or, neck_z, end_z, ncx, cy))
    )
    # Bore: the same chain, one wall in, open at the top and out through the tube.
    cavity = (
        _box(bore_w, bore_d, ramp_top_z, top_z + 1.0, cx, cy)
        .fuse(_loft_rc(bore_w, bore_d, cx, cy, ramp_top_z, spout_id / 2.0, ncx, cy, neck_z))
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, ncx, cy))
    )
    # Capacity filled to the brim rim: the cavity between the spout exit and brim top.
    fill = cavity.intersect(_box(600.0, 600.0, end_z, top_z, cx, cy)).Volume()
    return cq.Workplane(obj=solid.cut(cavity)), (w, d, top_z - end_z, end_z, fill)


def main():
    funnel, (w, d, drop, end_z, fill) = build()
    out = _here.parent / "funnel.step"
    export_step(funnel, str(out))
    print(f"-> {out.name}")
    b = funnel.val().BoundingBox()
    print(f"  brim:    {b.xlen:.1f} × {b.ylen:.1f} mm, top z={b.zmax:.1f}")
    print(f"  mouth:   {w:.1f} × {d:.1f} mm (collar), bore {w - 2*collar_wall:.1f} × {d - 2*collar_wall:.1f}")
    print(f"  spout:   Ø{spout_id:g} bore, to z={end_z:.1f}, total drop {drop:.1f} mm")
    print(f"  capacity to brim: {fill:.0f} mm³ = {fill / 1000.0:.2f} mL")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "SPOUT_ID": f"{spout_id:g} mm",
            "HOPPER_CHUTE": f"{chute_h:g} mm",
            "HOPPER_DROP": f"{drop:.0f} mm",
            "HOPPER_CAP": f"{fill / 1000.0:.0f} mL",
        },
        expected_counts={"SPOUT_ID": 1, "HOPPER_CHUTE": 1, "HOPPER_DROP": 1, "HOPPER_CAP": 1},
    )
    print("-> README.md")
    substitute_py_comments(
        _here,
        variables={"WALL": f"{collar_wall:g} mm", "SPOUT_ID": f"{spout_id:g} mm"},
        expected_counts={"WALL": 1, "SPOUT_ID": 1},
    )
    print(f"-> {_here.name} (self)")


if __name__ == "__main__":
    main()
