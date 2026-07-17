"""Zone C hopper funnel — the removable dishwasher-safe silicone insert.

One rectangular basin filling the whole top-wall opening right of the display
(cut by ../../enclosure/enclosure/enclosure.py via `_hopper_hole`), sized to
take a full 440 mL SodaStream flavor bottle poured in one go — capacity to
the rim is printed at export and runs well past the bottle. Top to bottom:

  * a stepped tub: the lower body drops through the opening (press-fitting
    the 3 mm top wall) and floors just above the power deck; at the top
    surface the walls step outward to a wider curb whose underside rests on
    the wall frame around the opening — the step carries the load and the
    curb stands proud as the pour rim;
  * the basin floor, sloping from every side into the throat mouth;
  * a rectangular throat dropping down the clear column between the two
    pumps;
  * a short ramp necking to a 1/4" round spout just above the tallest
    content under the throat (read live), where the V-B pickup tube meets
    it.

The funnel shares the opening rectangle with the enclosure, so the body
always matches the hole. It is built in enclosure world coordinates
(+X right, +Y back, +Z up), so it seats straight into the opening.
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
bowl_proud = 18.0       # curb rim height above the enclosure top surface
bowl_wall = 5.5         # basin wall — chunky, for grip when lifting the funnel
curb_out = {            # curb overhang past the opening, per side — the ledge
    "left": 3.0,        # the step rests on (left: only the strip between the
    "right": 8.0,       # display gusset and the opening; back: shy of the
    "front": 6.0,       # Y-seam line on the top surface)
    "back": 4.0,
}
floor_wall = 4.0        # basin floor slab thickness
floor_gap = 2.5         # floor underside clearance over the content below it
slope_drop = 8.0        # basin floor fall, walls to the throat mouth
throat_w = 27.0         # throat slot width (X) — the clear column between
                        # pump 1 and the power deck's edge
throat_y0, throat_y1 = 25.0, 100.0   # throat slot span (Y), inside the opening
throat_cx = 178.5       # throat slot center (X), mid-column
throat_wall = 3.0       # throat + ramp wall
ramp_top_z = 250.0      # throat bottom / ramp start
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
spout_tube = 6.0        # straight spout tube below the ramp — its length sets
                        # how far the Ø6.35 exit drops toward the V-B pickup
tip_clearance = 1.0     # gap left above the tallest content under the throat


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
    """The tallest placed content whose footprint underlies the given
    rectangle, plus clearance — read live, so the funnel tracks the packing."""
    top = 0.0
    for shape, _c in E._contents.build().values():
        b = shape.BoundingBox()
        if min(b.xmax, x1) > max(b.xmin, x0) and min(b.ymax, y1) > max(b.ymin, y0):
            top = max(top, b.zmax)
    return top + tip_clearance


def build_solids():
    """The funnel's outer envelope and inner bore as separate solids, plus a
    metrics dict. This is the source the silicone-mold generator consumes: the
    mold cavity is the negative of `solid` and the mold core is `cavity`. The
    exterior only ever widens going up (lower body → curb), so both mold
    halves still pull straight vertically. See ../hopper-funnel-mold/."""
    inner, outer, yj, _cf = E._dims()
    oz1 = outer[5]
    x0, x1, y0, y1 = E._hopper_hole(inner, outer, yj)
    w, d = x1 - x0, y1 - y0                            # lower body = the opening
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    # The curb: the opening grown per side, resting on the wall frame.
    ux0, ux1 = x0 - curb_out["left"], x1 + curb_out["right"]
    uy0, uy1 = y0 - curb_out["front"], y1 + curb_out["back"]
    uw, ud = ux1 - ux0, uy1 - uy0
    ucx, ucy = (ux0 + ux1) / 2.0, (uy0 + uy1) / 2.0
    top_z = oz1 + bowl_proud                           # curb rim = outermost point

    # The basin floors just above the tallest content under the opening (the
    # power deck); the spout necks to just above the content under the throat
    # slot (the water deck), read live.
    floor_out_z = _content_top(x0, x1, y0, y1) + floor_gap
    mouth_z = floor_out_z + floor_wall                 # throat mouth (floor low point)
    slope_z = mouth_z + slope_drop                     # floor slope start at the walls
    tcy = (throat_y0 + throat_y1) / 2.0
    td = throat_y1 - throat_y0
    end_z = _content_top(throat_cx - throat_w / 2.0, throat_cx + throat_w / 2.0,
                         throat_y0, throat_y1)
    neck_z = end_z + spout_tube
    spout_or = spout_id / 2.0 + spout_wall

    # Outer: lower body sunk through the opening to the floor slab, the wider
    # curb from the top surface up to the rim, the throat slot dropping the
    # pump column, the ramp necking to the spout, the spout tube.
    solid = (
        _box(w, d, floor_out_z, oz1 + 1.0, cx, cy)
        .fuse(_box(uw, ud, oz1, top_z, ucx, ucy))
        .fuse(_box(throat_w, td, ramp_top_z, floor_out_z + 1.0, throat_cx, tcy))
        .fuse(_loft_rc(throat_w, td, throat_cx, tcy, ramp_top_z, spout_or, throat_cx, tcy, neck_z))
        .fuse(_cyl(spout_or, neck_z, end_z, throat_cx, tcy))
    )
    # Bore: the curb basin, the step down to the lower basin (vertical walls,
    # then the floor sloping from every side into the throat mouth), the
    # throat bore, the ramp, the spout tube.
    bw, bd = w - 2.0 * bowl_wall, d - 2.0 * bowl_wall
    ubw, ubd = uw - 2.0 * bowl_wall, ud - 2.0 * bowl_wall
    tbw, tbd = throat_w - 2.0 * throat_wall, td - 2.0 * throat_wall
    cavity = (
        _box(ubw, ubd, oz1, top_z + 1.0, ucx, ucy)
        .fuse(_box(bw, bd, slope_z, oz1 + 1.0, cx, cy))
        .fuse(_loft_rr(bw, bd, cx, cy, slope_z, tbw, tbd, throat_cx, tcy, mouth_z))
        .fuse(_box(tbw, tbd, ramp_top_z, mouth_z + 1.0, throat_cx, tcy))
        .fuse(_loft_rc(tbw, tbd, throat_cx, tcy, ramp_top_z, spout_id / 2.0, throat_cx, tcy, neck_z))
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, throat_cx, tcy))
    )
    meta = {
        "w": w, "d": d, "cx": cx, "cy": tcy, "ncx": throat_cx,
        "bore_w": bw, "bore_d": bd,
        "out_w": uw, "out_d": ud, "out_cx": ucx, "out_cy": ucy,
        "rim_ring": bowl_wall, "collar_wall": throat_wall,
        "spout_id": spout_id, "spout_or": spout_or,
        "top_z": top_z, "oz1": oz1, "ramp_top_z": ramp_top_z,
        "neck_z": neck_z, "end_z": end_z, "floor_z": floor_out_z,
    }
    return solid, cavity, meta


def build():
    solid, cavity, m = build_solids()
    # Capacity filled to the curb rim: the cavity between the spout exit and rim top.
    fill = cavity.intersect(
        _box(600.0, 600.0, m["end_z"], m["top_z"], m["cx"], m["cy"])
    ).Volume()
    return cq.Workplane(obj=solid.cut(cavity)), (
        m["w"], m["d"], m["out_w"], m["out_d"], m["top_z"] - m["end_z"], m["end_z"], fill,
    )


def main():
    funnel, (w, d, uw, ud, drop, end_z, fill) = build()
    out = _here.parent / "hopper-funnel.step"
    export_step(funnel, str(out))
    print(f"-> {out.name}")
    b = funnel.val().BoundingBox()
    print(f"  basin:   {w:.1f} × {d:.1f} mm through the opening, curb {uw:.1f} × {ud:.1f}, "
          f"{bowl_proud:g} mm proud, top z={b.zmax:.1f}")
    print(f"  bore:    {w - 2*bowl_wall:.1f} × {d - 2*bowl_wall:.1f} mm at the floor")
    print(f"  throat:  {throat_w:g} × {throat_y1 - throat_y0:g} mm slot down the pump column")
    print(f"  spout:   Ø{spout_id:g} bore to z={end_z:.1f}, total drop {drop:.1f} mm")
    print(f"  capacity to rim: {fill:.0f} mm³ = {fill / 1000.0:.0f} mL "
          f"({fill / 440000.0:.2f}× a 440 mL SodaStream bottle)")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "HOPPER_BASIN": f"{w:.0f} × {d:.0f} mm",
            "HOPPER_CURB": f"{uw:.0f} × {ud:.0f} mm",
            "HOPPER_PROUD": f"{bowl_proud:g} mm",
            "HOPPER_CAPACITY": f"{fill / 1000.0:.0f} mL",
            "HOPPER_SPOUT_ID": f"{spout_id:g} mm",
            "HOPPER_DROP": f"{drop:.0f} mm",
        },
        expected_counts={"HOPPER_BASIN": 1, "HOPPER_CURB": 1, "HOPPER_PROUD": 1,
                         "HOPPER_CAPACITY": 1, "HOPPER_SPOUT_ID": 1, "HOPPER_DROP": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
