"""Zone C hopper funnel — the removable dishwasher-safe silicone insert.

A wide catch bowl standing on the enclosure top, draining through the top-wall
throat to the right of the display (cut by ../../enclosure/enclosure/enclosure.py
via `_hopper_hole`). The through-hole is boxed in on every side — the display
housing left, the electronics stack right, the Y-seam lip band behind — so the
pour target lives ABOVE the surface: the bowl spans the whole top zone right of
the display, riding the solid wall over the electronics and back across the Y
seam (it lifts off before the pieces do). Top to bottom:

  * the catch bowl — a shallow rectangular basin, vertical rim walls, its floor
    sloping from every side into the throat, its flat underside resting on the
    enclosure top surface;
  * a straight rectangular throat — vertical walls, no slope — press-fitting
    the 3 mm top wall and dropping on down into the reserve;
  * a shallow ramp from the bottom of that throat down to a 1/4" round spout.
    The spout is offset in +X toward the clear column beside the pumps and
    necks down to just above the tallest content under the mouth (read live),
    then a short straight tube carries the exit down to skim it.

The funnel shares the throat rectangle with the enclosure, so the collar always
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
_ENCL = _repo / "hardware" / "printed-parts" / "enclosure" / "enclosure"
sys.path.insert(0, str(_ENCL))
from _cadq_export import export_step
from docgen import substitute_md
import enclosure as E

# --- funnel parameters ------------------------------------------------------
bowl_h = 22.0           # catch-bowl rim height above the enclosure top surface
bowl_wall = 5.5         # bowl rim wall — chunky, for grip when lifting the funnel
bowl_band = 8.0         # vertical inner wall below the rim, before the floor slope
bowl_drop = 2.0         # the floor slope lands this far below the enclosure top,
                        # inside the throat, so the bowl drains dry
bowl_x_inset = 15.0     # bowl's +X rim, in from the interior +X wall — shy of the
                        # box's rounded top edge
bowl_y1 = 158.0         # bowl's back rim — on the solid top wall over the foam,
                        # just short of the tray band below
collar_wall = 3.0       # straight press-fit collar wall (throat opening − bore)
throat_h = 27.0         # straight rectangular throat — enclosure top surface down
                        # to the ramp start
neck_dx = 24.0          # neck (ramp foot + spout) shift in X off the throat center,
                        # aiming the drop into the clear column between the two pumps
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
spout_tube = 6.0       # straight spout tube below the ramp tip — its length sets
                        # how far the Ø6.35 exit drops into the clear column
tip_clearance = 1.0     # gap left above the tallest content under the mouth


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


def _loft_rr(w0, d0, cx0, cy0, z0, w1, d1, cx1, cy1, z1):
    """Loft from a rectangle down to a rectangle (centers may differ)."""
    return (
        cq.Workplane("XY", origin=(cx0, cy0, z0))
        .rect(w0, d0)
        .workplane(offset=z1 - z0).center(cx1 - cx0, cy1 - cy0)
        .rect(w1, d1)
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


def build_solids():
    """The funnel's outer envelope and inner bore as separate solids, plus a
    metrics dict. This is the source the silicone-mold generator consumes: the
    mold cavity is the negative of `solid` and the mold core is `cavity`. Keeping
    it here, beside the funnel, keeps the mold in lockstep with the part.
    See ../hopper-funnel-mold/."""
    inner, outer, yj, _cf = E._dims()
    iz1, oz1 = inner[5], outer[5]
    x0, x1, y0, y1 = E._hopper_hole(inner, outer, yj)
    w, d = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    bore_w, bore_d = w - 2.0 * collar_wall, d - 2.0 * collar_wall
    # The catch bowl's footprint: from just left of the throat (the display
    # housing bounds it) across the whole top zone — over the solid wall above
    # the electronics stack — to shy of the box's rounded +X top edge, and
    # from the front edge back over the Y seam to the tray band.
    bx0, bx1 = x0 - 1.0, inner[1] - bowl_x_inset
    by0, by1 = y0 - 1.0, bowl_y1
    bw, bd = bx1 - bx0, by1 - by0
    bcx, bcy = (bx0 + bx1) / 2.0, (by0 + by1) / 2.0
    top_z = oz1 + bowl_h                               # bowl rim = outermost point
    spout_or = spout_id / 2.0 + spout_wall
    ncx = cx + neck_dx                                  # spout/neck, shifted in X
    ramp_top_z = oz1 - throat_h                         # straight throat bottom = ramp start

    # The ramp necks to the round spout just above the tallest content under
    # the mouth (read live); a straight spout tube then carries the Ø6.35 exit
    # down to skim that content, where the delivery tube picks it up over the
    # clear column beside it.
    neck_z = _content_top(x0, x1, y0, y1) + spout_tube
    end_z = neck_z - spout_tube

    # Outer: the bowl block seated flat on the enclosure top, the straight
    # rectangular throat through the wall, a shallow ramp down to the
    # +X-offset spout, straight spout tube.
    solid = (
        _box(bw, bd, oz1, top_z, bcx, bcy)
        .fuse(_box(w, d, ramp_top_z, oz1, cx, cy))
        .fuse(_loft_rc(w, d, cx, cy, ramp_top_z, spout_or, ncx, cy, neck_z))
        .fuse(_cyl(spout_or, neck_z, end_z, ncx, cy))
    )
    # Bore: the basin (vertical rim band, then the floor sloping from every
    # side into the throat), the throat bore, the ramp, the spout tube.
    slope_top = oz1 + bowl_band
    cavity = (
        _box(bw - 2.0 * bowl_wall, bd - 2.0 * bowl_wall, slope_top, top_z + 1.0, bcx, bcy)
        .fuse(_loft_rr(bw - 2.0 * bowl_wall, bd - 2.0 * bowl_wall, bcx, bcy, slope_top,
                       bore_w, bore_d, cx, cy, oz1 - bowl_drop))
        .fuse(_box(bore_w, bore_d, ramp_top_z, oz1 - bowl_drop + 1.0, cx, cy))
        .fuse(_loft_rc(bore_w, bore_d, cx, cy, ramp_top_z, spout_id / 2.0, ncx, cy, neck_z))
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, ncx, cy))
    )
    meta = {
        "w": w, "d": d, "cx": cx, "cy": cy, "ncx": ncx,
        "bore_w": bore_w, "bore_d": bore_d,
        "out_w": bw, "out_d": bd, "out_cx": bcx, "out_cy": bcy,
        "rim_ring": bowl_wall, "collar_wall": collar_wall,
        "spout_id": spout_id, "spout_or": spout_or,
        "top_z": top_z, "oz1": oz1, "ramp_top_z": ramp_top_z,
        "neck_z": neck_z, "end_z": end_z,
    }
    return solid, cavity, meta


def build():
    solid, cavity, m = build_solids()
    # Capacity filled to the bowl rim: the cavity between the spout exit and rim top.
    fill = cavity.intersect(
        _box(600.0, 600.0, m["end_z"], m["top_z"], m["cx"], m["cy"])
    ).Volume()
    return cq.Workplane(obj=solid.cut(cavity)), (
        m["w"], m["d"], m["out_w"], m["out_d"], m["top_z"] - m["end_z"], m["end_z"], fill,
    )


def main():
    funnel, (w, d, bw, bd, drop, end_z, fill) = build()
    out = _here.parent / "hopper-funnel.step"
    export_step(funnel, str(out))
    print(f"-> {out.name}")
    b = funnel.val().BoundingBox()
    print(f"  bowl:    {bw:.1f} × {bd:.1f} mm rim, {bowl_h:g} mm proud, top z={b.zmax:.1f}")
    print(f"  throat:  {w:.1f} × {d:.1f} mm (collar), bore {w - 2*collar_wall:.1f} × {d - 2*collar_wall:.1f}")
    print(f"  spout:   Ø{spout_id:g} bore, +X-offset, to z={end_z:.1f}, total drop {drop:.1f} mm")
    print(f"  capacity to rim: {fill:.0f} mm³ = {fill / 1000.0:.2f} mL")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "HOPPER_BOWL": f"{bw:.0f} × {bd:.0f} mm",
            "HOPPER_BOWL_H": f"{bowl_h:g} mm",
            "HOPPER_SPOUT_ID": f"{spout_id:g} mm",
            "HOPPER_CHUTE": f"{throat_h:g} mm",
            "HOPPER_DROP": f"{drop:.0f} mm",
        },
        expected_counts={"HOPPER_BOWL": 1, "HOPPER_BOWL_H": 1,
                         "HOPPER_SPOUT_ID": 1, "HOPPER_CHUTE": 1, "HOPPER_DROP": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
