"""Zone C hopper funnel — the removable dishwasher-safe silicone insert.

The same idiom as the Lite edition's funnel
(/pie-in-the-sky/lite/printed-parts/funnel/): a wide flush funnel that drops
into the top-wall opening right of the display (cut by
../../enclosure/enclosure/enclosure.py via `_hopper_hole`) — nothing stands
on the enclosure top but a flat brim. Pour a full 440 mL SodaStream flavor
bottle into it in one go; capacity to the brim is printed at export and runs
past the bottle. Top to bottom:

  * a flat brim that overhangs the opening all around and rests on the
    enclosure top surface;
  * a straight rectangular chute — vertical walls, no slope — press-fitting
    the 3 mm top wall and dropping to a floor just above the tallest
    content under the opening (read live);
  * the floor, dishing gently from every side into the drain mouth so the
    basin drains dry;
  * a short taper necking the mouth to a 1/4" round spout in the clear
    column between the two pumps — a stub under the floor, not a chute —
    where the V-B pickup tube meets it.

The funnel shares the opening rectangle with the enclosure, so the chute
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
brim_overhang = 3.0     # brim flange reach past the opening, all around
brim_thickness = 3.0    # flange thickness, resting on the enclosure top
collar_wall = 3.0       # straight press-fit chute wall (opening − bore)
floor_wall = 3.0        # basin floor thickness
floor_gap = 2.5         # floor underside clearance over the content below it
slope_drop = 5.0        # basin floor fall, walls to the drain mouth
mouth_w = 24.0          # drain mouth (X) — inside the clear column between
                        # the two pumps
mouth_d = 28.0          # drain mouth (Y)
mouth_cx = 179.5        # drain mouth center (X), mid-column
mouth_cy = 60.0         # drain mouth center (Y)
taper_h = 21.0          # mouth → spout necking taper below the floor
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
spout_tube = 12.0       # straight spout tube below the taper — the barb stub
                        # the V-B pickup tube lands on


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
    rectangle — read live, so the funnel tracks the packing."""
    top = 0.0
    for shape, _c in E._contents.build().values():
        b = shape.BoundingBox()
        if min(b.xmax, x1) > max(b.xmin, x0) and min(b.ymax, y1) > max(b.ymin, y0):
            top = max(top, b.zmax)
    return top


def build_solids():
    """The funnel's outer envelope and inner bore as separate solids, plus a
    metrics dict. This is the source the silicone-mold generator consumes: the
    mold cavity is the negative of `solid` and the mold core is `cavity`. The
    exterior only ever widens going up (spout → taper → chute → brim), so
    both mold halves pull straight vertically. See ../hopper-funnel-mold/."""
    inner, outer, yj, _cf = E._dims()
    oz1 = outer[5]
    x0, x1, y0, y1 = E._hopper_hole(inner, outer, yj)
    w, d = x1 - x0, y1 - y0                            # chute = the opening
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    bw, bd = w + 2.0 * brim_overhang, d + 2.0 * brim_overhang
    top_z = oz1 + brim_thickness                       # brim top = outermost point

    # The basin floors just above the tallest content under the opening
    # (pump 1), read live; the mouth taper and spout stub hang below it in
    # the clear column between the two pumps.
    floor_out_z = _content_top(x0, x1, y0, y1) + floor_gap
    mouth_z = floor_out_z + floor_wall                 # drain mouth (floor low point)
    slope_z = mouth_z + slope_drop                     # floor dish start at the walls
    neck_z = mouth_z - taper_h
    end_z = neck_z - spout_tube
    spout_or = spout_id / 2.0 + spout_wall

    # Outer: the flat brim on the top surface, the straight chute sunk
    # through the opening to the floor, the mouth taper necking to the
    # spout under the floor, the spout tube.
    solid = (
        _box(bw, bd, oz1, top_z, cx, cy)
        .fuse(_box(w, d, floor_out_z, oz1 + 1.0, cx, cy))
        .fuse(_loft_rc(mouth_w + 2.0 * collar_wall, mouth_d + 2.0 * collar_wall,
                       mouth_cx, mouth_cy, floor_out_z + 1.0, spout_or, mouth_cx, mouth_cy, neck_z))
        .fuse(_cyl(spout_or, neck_z, end_z, mouth_cx, mouth_cy))
    )
    # Bore: the basin (vertical chute walls, then the floor dishing from
    # every side into the drain mouth), the taper, the spout tube.
    cw, cd = w - 2.0 * collar_wall, d - 2.0 * collar_wall
    cavity = (
        _box(cw, cd, slope_z, top_z + 1.0, cx, cy)
        .fuse(_loft_rr(cw, cd, cx, cy, slope_z, mouth_w, mouth_d, mouth_cx, mouth_cy, mouth_z))
        .fuse(_loft_rc(mouth_w, mouth_d, mouth_cx, mouth_cy, mouth_z + 1.0,
                       spout_id / 2.0, mouth_cx, mouth_cy, neck_z))
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, mouth_cx, mouth_cy))
    )
    meta = {
        "w": w, "d": d, "cx": cx, "cy": mouth_cy, "ncx": mouth_cx,
        "bore_w": cw, "bore_d": cd,
        "out_w": bw, "out_d": bd, "out_cx": cx, "out_cy": cy,
        "rim_ring": collar_wall + brim_overhang, "collar_wall": collar_wall,
        "spout_id": spout_id, "spout_or": spout_or,
        "top_z": top_z, "oz1": oz1,
        "neck_z": neck_z, "end_z": end_z, "floor_z": floor_out_z,
    }
    return solid, cavity, meta


def build():
    solid, cavity, m = build_solids()
    # Capacity filled to the brim: the cavity between the spout exit and brim top.
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
    print(f"  basin:   {w:.1f} × {d:.1f} mm through the opening, brim {bw:.1f} × {bd:.1f}, "
          f"{brim_thickness:g} mm proud, top z={b.zmax:.1f}")
    print(f"  bore:    {w - 2*collar_wall:.1f} × {d - 2*collar_wall:.1f} mm at the chute")
    print(f"  mouth:   {mouth_w:g} × {mouth_d:g} mm drain over the pump column")
    print(f"  spout:   Ø{spout_id:g} bore to z={end_z:.1f}, total drop {drop:.1f} mm")
    print(f"  capacity to brim: {fill:.0f} mm³ = {fill / 1000.0:.0f} mL "
          f"({fill / 440000.0:.2f}× a 440 mL SodaStream bottle)")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "HOPPER_BASIN": f"{w:.0f} × {d:.0f} mm",
            "HOPPER_BRIM": f"{brim_thickness:g} mm",
            "HOPPER_CAPACITY": f"{fill / 1000.0:.0f} mL",
            "HOPPER_SPOUT_ID": f"{spout_id:g} mm",
            "HOPPER_DROP": f"{drop:.0f} mm",
        },
        expected_counts={"HOPPER_BASIN": 1, "HOPPER_BRIM": 1,
                         "HOPPER_CAPACITY": 1, "HOPPER_SPOUT_ID": 1, "HOPPER_DROP": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
