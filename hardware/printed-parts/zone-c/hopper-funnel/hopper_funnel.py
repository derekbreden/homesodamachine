"""Zone C hopper funnel — the removable dishwasher-safe silicone insert.

A static part in its own frame: origin at the collar-rectangle center, z = 0
the brim underside — the plane that rests on the enclosure's top surface.
The enclosure assembly places it (`_contents.FUNNEL_CX/CY` + the box's outer
top), and the enclosure cuts its top-wall opening from this collar
(`enclosure.py _hopper_hole`), asserting the placement clears the display
gusset, the corner pod, and the Y-seam lip. The drain is defined here, in
the funnel's frame, and rides the part wherever it is placed.

Top to bottom:

  * a flat brim that overhangs the collar all around and rests on the
    enclosure top surface;
  * a tall straight rectangular chute — vertical walls, no slope — pressing
    the 3 mm top wall at its top and hanging on down into the box;
  * a shallow ramp from the bottom of that chute down to a 1/4" round spout —
    the whole floor is the ramp, every surface of it falling toward the
    spout, so the basin drains dry. The spout is offset off the collar
    centre (neck_dx); the placement's FUNNEL_ROT picks which side of the
    box it descends. The drain must feed V-B by a falling tube (segment 4
    is the gravity drain and the air-purge path; it may not rise), and the
    offset makes the drain-side ramp steep, shedding syrup instead of
    pooling.

Capacity to the brim is printed at export and runs past a full 440 mL
SodaStream bottle.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_step
from docgen import substitute_md

# --- funnel parameters ------------------------------------------------------
collar_w = 148.5        # collar footprint (X) — spans the zone-C top opening
collar_d = 110.6        # collar footprint (Y)
brim_overhang = 3.0     # brim flange reach past the collar, all around
brim_thickness = 3.0    # flange thickness, resting on the enclosure top
collar_wall = 3.0       # straight press-fit collar wall (opening − bore)
chute_h = 30.0          # straight rectangular chute height — brim top down to the ramp start
neck_dx = 54.0          # neck (ramp foot + spout) shift in X off the collar center;
                        # the placement's FUNNEL_ROT picks which side of the box
                        # the drop lands
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
spout_tube = 6.0        # straight spout tube below the ramp tip
drop = 79.0             # brim underside (z 0) down to the spout exit — deep enough
                        # that the ramp runs steep and the drain keeps fall to spare
                        # over V-B's collet (the enclosure scorecard measures the
                        # real-solid gaps below the spout)

# The drain, in the funnel's own frame: the spout exit annulus center. World
# position = this + the funnel's placement; it rides the part.
drain_local = (neck_dx, 0.0, -drop)


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

def build_solids(drop=drop):
    """The funnel's outer envelope and inner bore as separate solids, plus a
    metrics dict. This is the source the silicone-mold generator consumes: the
    mold cavity is the negative of `solid` and the mold core is `cavity`. Keeping
    it here, beside the funnel, keeps the mold in lockstep with the part.
    See ../hopper-funnel-mold/."""
    w, d = collar_w, collar_d
    cx = cy = 0.0
    bore_w, bore_d = w - 2.0 * collar_wall, d - 2.0 * collar_wall
    top_z = brim_thickness                              # brim top = outermost point
    spout_or = spout_id / 2.0 + spout_wall
    ncx = cx + neck_dx                                  # spout/neck, shifted in X
    ramp_top_z = top_z - chute_h                        # straight chute bottom = ramp start
    end_z = -drop                                       # spout exit (the drain)
    neck_z = end_z + spout_tube                         # ramp tip = tube top

    # Outer: brim flange, a tall straight rectangular chute, a shallow ramp down to
    # the neck_dx-offset spout, straight spout tube.
    solid = (
        _box(w + 2.0 * brim_overhang, d + 2.0 * brim_overhang, 0.0, top_z, cx, cy)
        .fuse(_box(w, d, ramp_top_z, 0.0, cx, cy))
        .fuse(_loft_rc(w, d, cx, cy, ramp_top_z, spout_or, ncx, cy, neck_z))
        .fuse(_cyl(spout_or, neck_z, end_z, ncx, cy))
    )
    # Bore: the same chain, one wall in, open at the top and out through the tube.
    cavity = (
        _box(bore_w, bore_d, ramp_top_z, top_z + 1.0, cx, cy)
        .fuse(_loft_rc(bore_w, bore_d, cx, cy, ramp_top_z, spout_id / 2.0, ncx, cy, neck_z))
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, ncx, cy))
    )
    meta = {
        "w": w, "d": d, "cx": cx, "cy": cy, "ncx": ncx,
        "bore_w": bore_w, "bore_d": bore_d,
        "brim_overhang": brim_overhang, "collar_wall": collar_wall,
        # The part's outer footprint (the brim) and the flange + collar ring
        # between the bore mouth and that outer edge — the mold's pour/vent land.
        "out_w": w + 2.0 * brim_overhang, "out_d": d + 2.0 * brim_overhang,
        "out_cx": cx, "out_cy": cy,
        "rim_ring": collar_wall + brim_overhang,
        "spout_id": spout_id, "spout_or": spout_or,
        "top_z": top_z, "ramp_top_z": ramp_top_z,
        "neck_z": neck_z, "end_z": end_z,
    }
    return solid, cavity, meta


def build(drop=drop):
    solid, cavity, m = build_solids(drop)
    # Capacity filled to the brim rim: the cavity between the spout exit and brim top.
    fill = cavity.intersect(
        _box(600.0, 600.0, m["end_z"], m["top_z"], m["cx"], m["cy"])
    ).Volume()
    return cq.Workplane(obj=solid.cut(cavity)), (
        m["w"], m["d"], m["top_z"] - m["end_z"], m["end_z"], fill,
    )


def main():
    funnel, (w, d, total, end_z, fill) = build()
    out = _here.parent / "hopper-funnel.step"
    export_step(funnel, str(out))
    print(f"-> {out.name}")
    b = funnel.val().BoundingBox()
    print(f"  brim:    {b.xlen:.1f} × {b.ylen:.1f} mm, top z={b.zmax:.1f} (local; z 0 = brim underside)")
    print(f"  mouth:   {w:.1f} × {d:.1f} mm (collar), bore {w - 2*collar_wall:.1f} × {d - 2*collar_wall:.1f}")
    print(f"  spout:   Ø{spout_id:g} bore, drain at ({drain_local[0]:g}, {drain_local[1]:g}, {drain_local[2]:g}) local, total drop {total:.1f} mm")
    print(f"  capacity to brim: {fill:.0f} mm³ = {fill / 1000.0:.0f} mL "
          f"({fill / 440000.0:.2f}× a 440 mL SodaStream bottle)")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "HOPPER_SPOUT_ID": f"{spout_id:g} mm",
            "HOPPER_CHUTE": f"{chute_h:g} mm",
            "HOPPER_DROP": f"{total:.0f} mm",
            "HOPPER_CAP": f"{fill / 1000.0:.0f} mL",
        },
        expected_counts={"HOPPER_SPOUT_ID": 1, "HOPPER_CHUTE": 1, "HOPPER_DROP": 1,
                         "HOPPER_CAP": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
