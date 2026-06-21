"""Zone C hopper funnel — the removable dishwasher-safe silicone insert.

A shallow wide funnel that drops into the top-wall opening to the right of the
display (cut by ../../enclosure/enclosure/enclosure.py via `_hopper_hole`). Top
to bottom:

  * a flat brim that overhangs the opening all around and rests on the enclosure
    top surface;
  * a straight rectangular collar — vertical walls, no slope — that press-fits
    into the opening, filling the 3 mm top wall;
  * a ramp from that rectangular mouth down to a 1/4" round spout that hangs into
    the Zone C funnel reserve, stopping one mm clear of the tallest content below
    (the bib-gate tray) — so the drop is exactly the room the current packing
    leaves.

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
_ENCL = _repo / "hardware" / "printed-parts" / "enclosure" / "enclosure"
sys.path.insert(0, str(_ENCL))
from _cadq_export import export_step
from docgen import substitute_md
import enclosure as E

# --- funnel parameters ------------------------------------------------------
brim_overhang = 3.0     # brim flange reach past the opening, all around
brim_thickness = 3.0    # flange thickness, resting on the enclosure top
collar_wall = 3.0       # straight press-fit collar wall (opening − bore)
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
spout_tube = 21.0       # straight spout tube below the ramp tip — its length sets
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

    # The ramp necks to the round spout one mm above the bib-gate tray (read live);
    # a straight spout tube then carries the Ø6.35 exit straight down the clear
    # column, centered on the opening.
    neck_z = _content_top(x0, x1, y0, y1)
    end_z = neck_z - spout_tube

    # Outer: brim flange, straight collar, ramp to the spout, straight spout tube.
    solid = (
        _box(w + 2.0 * brim_overhang, d + 2.0 * brim_overhang, oz1, top_z, cx, cy)
        .fuse(_box(w, d, iz1, oz1, cx, cy))
        .fuse(_loft_rc(w, d, cx, cy, iz1, spout_or, cx, cy, neck_z))
        .fuse(_cyl(spout_or, neck_z, end_z, cx, cy))
    )
    # Bore: the same chain, one wall in, open at the top and out through the tube.
    cavity = (
        _box(bore_w, bore_d, iz1, top_z + 1.0, cx, cy)
        .fuse(_loft_rc(bore_w, bore_d, cx, cy, iz1, spout_id / 2.0, cx, cy, neck_z))
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, cx, cy))
    )
    # Capacity filled to the brim rim: the cavity between the spout exit and brim top.
    fill = cavity.intersect(_box(600.0, 600.0, end_z, top_z, cx, cy)).Volume()
    return cq.Workplane(obj=solid.cut(cavity)), (w, d, top_z - end_z, end_z, fill)


def main():
    funnel, (w, d, drop, end_z, fill) = build()
    out = _here.parent / "hopper-funnel.step"
    export_step(funnel, str(out))
    print(f"-> {out.name}")
    b = funnel.val().BoundingBox()
    print(f"  brim:    {b.xlen:.1f} × {b.ylen:.1f} mm, top z={b.zmax:.1f}")
    print(f"  mouth:   {w:.1f} × {d:.1f} mm (collar), bore {w - 2*collar_wall:.1f} × {d - 2*collar_wall:.1f}")
    print(f"  spout:   Ø{spout_id:g} bore, centered, to z={end_z:.1f}, total drop {drop:.1f} mm")
    print(f"  capacity to brim: {fill:.0f} mm³ = {fill / 1000.0:.2f} mL")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "HOPPER_SPOUT_ID": f"{spout_id:g} mm",
            "HOPPER_DROP": f"{drop:.0f} mm",
        },
        expected_counts={"HOPPER_SPOUT_ID": 1, "HOPPER_DROP": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
