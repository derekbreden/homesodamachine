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
  * a shallow ramp from the bottom of that chute down to a 1/4" round spout
    at the collar centre — the whole floor is the ramp, every surface of it
    falling toward the spout, so the basin drains dry. The floor's
    shallowest line (the long X half-run to the neck) holds `ramp_angle`;
    the shorter front/back runs land steeper. Centring the neck keeps every
    run short, so the floor reaches its grade with the least depth and the
    drain rides high: the fall segment 4 needs (the gravity drain and the
    air-purge path; it may not rise) is banked in the placement below the
    drain, not spent inside the part.

Capacity to the brim is printed at export and runs past a full 440 mL
SodaStream bottle.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
# _repo is this EDITION's root; tools/ is shared machinery with one copy at the
# repo root, so it gets its own anchor rather than a tools/ per edition.
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_tools))
from _cadq_export import export_step
from docgen import substitute_md

# --- funnel parameters ------------------------------------------------------
# The collar sits at least one `brim_margin` inside the zone-C top-wall frame on
# every side. The margin is twice the overhang, so the brim edge lands on the
# MIDDLE of that ring where the collar fills the frame, and a full overhang's
# width of top wall remains beyond it in every case. enclosure.py `_hopper_hole`
# owns the frame and asserts it; the funnel takes the front of the Y span, and a
# deeper box adds its top wall behind rather than growing the part.
collar_w = 159.0        # collar footprint (X) — the frame's width less 2 × brim_margin. The
                        # basin takes the top wall's FULL width: it stands behind the display
                        # facet, which spans the machine, so there is nothing beside it to leave
                        # room for
collar_d = collar_w     # collar footprint (Y) — as deep as it is wide, which is the deepest a
                        # basin of this width may be. One rise serves every run (see ramp_angle),
                        # so the LONGEST run is what the grade is measured on, and a Y run past
                        # the X one would quietly put the front/back floor under `ramp_angle`.
                        # Square is where the two runs meet, so it is the most plan area the grade
                        # allows — and plan area is what buys capacity cheaply, so this is also
                        # the shallowest the basin can be. The check below holds the line
brim_margin = 10.0      # top-wall left between the collar edge and the frame, all around —
                        # one overhang catches the flange, the rest is what stands beyond it
brim_overhang = 7.0     # brim flange reach past the collar — what actually catches the
                        # top wall and holds the funnel out of the box, all around
brim_thickness = 3.0    # flange thickness, resting on the enclosure top
collar_wall = 3.0       # straight press-fit collar wall (opening − bore)
# The basin is sized in bottles: a full one goes in dumped, not metered, and the
# margin is what keeps a miss off the counter. The ramp's depth is set by its grade
# and the spout by its tube, so the straight section is the only height the basin's
# volume is in — and it stands between two bounds. The FLOOR is that requirement,
# asserted in `build`. The CEILING is the pack: the chute hangs the ramp, the spout
# and the drain lower with every millimetre of itself, and the source pair's coils
# stand directly under the basin, so what the column leaves over them
# (`_contents.SOURCE_TRAY_HEADROOM`, held by the enclosure scorecard's
# `source-tray-assembly clear hopper-funnel`) is what the chute may spend. It takes
# that band whole rather than stopping at the floor: the collar already fills its
# frame in both axes, so depth is the only thing left that buys capacity.
bottle_ml = 440.0       # one SodaStream concentrate bottle
capacity_bottles = 1.3  # basin capacity to the brim, in bottles — the floor it must clear
chute_h = 27.65        # straight rectangular chute height — brim top down to the ramp start
neck_dx = 0.0           # neck (ramp foot + spout) on the collar centre — every floor
                        # run stays short, so the grade costs the least depth
ramp_angle = 15.0       # deg — the floor's shallowest line (the long X half-run); the
                        # front/back runs land steeper on their own. Concentrate is
                        # sticky and the basin has to come out of the machine clean, so
                        # this is graded to SHED, not merely to slope — a shallow floor
                        # holds a residue film that a rinse has to chase. Depth is what
                        # buys it: one rise serves every run, so the grade costs
                        # `_ramp_run × tan(angle)` of it, and the chute gives that back
                        # by shortening (the basin's volume is the target, not its
                        # depth). What caps it is the pack: the drain hangs lower with
                        # every degree, and the manifold's east elbow row and the lane
                        # its pump-discharge crossings use are directly under the spout.
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
spout_tube = 6.0        # straight spout tube below the ramp tip
# The drop stacks the chute below the brim, the ramp rise the shallowest line
# needs at its grade, and the spout tube.
_ramp_run = (collar_w - 2.0 * collar_wall) / 2.0 - spout_id / 2.0 + neck_dx
_ramp_rise = _ramp_run * math.tan(math.radians(ramp_angle))
drop = (chute_h - brim_thickness) + _ramp_rise + spout_tube
# `ramp_angle` is applied to the X half-run, so it is the floor's true minimum grade
# only while that run is the LONGEST one to the neck. One rise serves every run, so a
# longer run is a shallower one: let the Y half-run overtake X and the front/back floor
# quietly falls below `ramp_angle` while this file still claims it. Widening the collar
# in Y walks straight at that line — hence the check.
_y_run = (collar_d - 2.0 * collar_wall) / 2.0 - spout_id / 2.0
if _y_run > _ramp_run:
    raise ValueError(
        f"collar_d {collar_d:g} makes the Y half-run ({_y_run:.2f} mm) longer than the X "
        f"({_ramp_run:.2f} mm), so the front/back floor grades "
        f"{math.degrees(math.atan(_ramp_rise / _y_run)):.2f}° — below ramp_angle "
        f"{ramp_angle:g}°, which no longer describes the shallowest line. Keep collar_d ≤ "
        f"{2.0 * (_ramp_run + spout_id / 2.0) + 2.0 * collar_wall:.1f} mm, or drive the rise "
        f"off the longer run instead.")

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
        "brim_overhang": brim_overhang, "brim_margin": brim_margin,
        "collar_wall": collar_wall,
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
    # The chute is what carries the basin past its floor. Capacity is LINEAR in
    # chute_h (the cone spans the ramp rise, which the X half-run fixes, and the
    # spout tube is fixed), so a miss names the height that closes it.
    want = capacity_bottles * bottle_ml * 1000.0
    if fill < want - 1.0:
        bore_area = m["bore_w"] * m["bore_d"]
        raise ValueError(
            f"hopper basin holds {fill / 1000.0:.1f} mL, short of the "
            f"{capacity_bottles:g} × {bottle_ml:g} mL = {want / 1000.0:.1f} mL target — "
            f"set chute_h to {chute_h + (want - fill) / bore_area:.2f} mm")
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
            "HOPPER_HOLD": f"{brim_overhang:g} mm",
            "HOPPER_MARGIN": f"{brim_margin:g} mm",
        },
        expected_counts={"HOPPER_SPOUT_ID": 1, "HOPPER_CHUTE": 1, "HOPPER_DROP": 1,
                         "HOPPER_CAP": 1, "HOPPER_HOLD": 1, "HOPPER_MARGIN": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
