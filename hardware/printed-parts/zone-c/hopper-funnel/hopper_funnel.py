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
spout_tube = 6.0        # straight spout tube continuing below the ramp tip
tip_clearance = 1.0     # gap left above the tallest content under the mouth


# --- primitives -------------------------------------------------------------

def _box(w, d, z0, z1, cx, cy):
    """Axis-aligned box of footprint w×d centered at (cx, cy), spanning z[z0,z1]."""
    return (
        cq.Workplane("XY").box(w, d, z1 - z0, centered=(True, True, False))
        .translate((cx, cy, z0)).val()
    )


def _ramp(w, d, r, z_top, z_bot, cx, cy):
    """Loft from a w×d rectangle at z_top down to a radius-r circle at z_bot,
    both centered at (cx, cy)."""
    return (
        cq.Workplane("XY", origin=(cx, cy, z_top))
        .rect(w, d)
        .workplane(offset=z_bot - z_top)
        .circle(r)
        .loft(combine=True)
        .val()
    )


def _cyl(r, z_top, z_bot, cx, cy):
    return cq.Solid.makeCylinder(r, z_top - z_bot, cq.Vector(cx, cy, z_bot), cq.Vector(0, 0, 1))


# --- the funnel -------------------------------------------------------------

def _tip_z(hole, iz1):
    """How far the spout can hang: one mm above the tallest content whose
    footprint underlies the opening — the bib-gate tray, with the funnel centered
    on the opening. Read live from the placed contents, so it tracks the packing."""
    x0, x1, y0, y1 = hole
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
    tip_z = _tip_z((x0, x1, y0, y1), iz1)               # ramp tip (mouth → spout)
    end_z = tip_z - spout_tube                          # straight tube reaches here
    spout_or = spout_id / 2.0 + spout_wall

    # Outer: brim flange on top, straight collar through the wall, ramp to the
    # spout, then a straight tube continuing the spout below the ramp tip.
    solid = (
        _box(w + 2.0 * brim_overhang, d + 2.0 * brim_overhang, oz1, top_z, cx, cy)
        .fuse(_box(w, d, iz1, oz1, cx, cy))
        .fuse(_ramp(w, d, spout_or, iz1, tip_z, cx, cy))
        .fuse(_cyl(spout_or, tip_z, end_z, cx, cy))
    )
    # Bore: open rectangular mouth straight down through the collar, then ramping
    # to the round spout and out through the tube.
    cavity = (
        _box(bore_w, bore_d, iz1, top_z + 1.0, cx, cy)
        .fuse(_ramp(bore_w, bore_d, spout_id / 2.0, iz1, tip_z, cx, cy))
        .fuse(_cyl(spout_id / 2.0, tip_z, end_z - 1.0, cx, cy))
    )
    return cq.Workplane(obj=solid.cut(cavity)), (w, d, top_z - end_z, end_z)


def main():
    funnel, (w, d, drop, end_z) = build()
    out = _here.parent / "hopper-funnel.step"
    export_step(funnel, str(out))
    print(f"-> {out.name}")
    b = funnel.val().BoundingBox()
    print(f"  brim:    {b.xlen:.1f} × {b.ylen:.1f} mm, top z={b.zmax:.1f}")
    print(f"  mouth:   {w:.1f} × {d:.1f} mm (collar), bore {w - 2*collar_wall:.1f} × {d - 2*collar_wall:.1f}")
    print(f"  spout:   Ø{spout_id:g} bore, {spout_tube:g} mm tube to z={end_z:.1f}, total drop {drop:.1f} mm")

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
