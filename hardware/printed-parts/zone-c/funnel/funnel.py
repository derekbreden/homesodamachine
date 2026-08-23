"""Zone C funnel — the removable dishwasher-safe silicone insert.

A static part in its own frame: origin at the collar-rectangle center, z = 0
the brim underside — the plane that rests on the enclosure's top surface.
The machine places it (`enclosure_assembly.build_funnel`, on `enclosure_assembly.funnel_centre`
and the box's outer top), and the enclosure cuts its top-wall opening from this collar
(`enclosure.py _funnel_hole`), asserting the placement clears the display
gusset, the ±X boss chains, and the Y-seam lip. The drain is defined here, in
the funnel's frame, and rides the part wherever it is placed.

Top to bottom:

  * a flat brim that overhangs the collar all around and rests on the
    enclosure top surface;
  * a tall straight rectangular chute — vertical walls, no slope — pressing
    the 3 mm top wall at its top and hanging on down into the box;
  * a shallow ramp from the bottom of that chute down to a 1/4" round spout
    offset off the collar centre in X — the whole floor is the ramp, every
    surface of it falling toward the spout, so the funnel drains dry. One rise
    serves every run, so `ramp_angle` is struck on the LONGEST half-run to
    the neck — the X one, which the offset lengthens — and every other line
    on the floor lands steeper. The neck stands on the collar's Y CENTRE, so
    the front and back runs are equal and the fall segment 4 needs (the
    gravity drain and the air-purge path; it may not rise) is banked in the
    placement below the drain rather than spent inside the part.

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
sys.path.insert(0, str(_repo / "hardware" / "reference" / "worm-clamp"))
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly
from _materials import M_SILICONE_BLACK, one_body
from docgen import substitute_md
# The bound this file states about its own collar, recorded at import for the machine's card.
import _stated_bounds as _bounds
# The band that closes the spout on the drain stub, and so the length of round the spout owes it.
import worm_clamp as _clamp

# --- funnel parameters ------------------------------------------------------
# The collar sits at least one `brim_margin` inside the zone-C top-wall frame on
# every side. The margin is twice the overhang, so the brim edge lands on the
# MIDDLE of that ring where the collar fills the frame, and a full overhang's
# width of top wall remains beyond it in every case. enclosure.py `_funnel_hole`
# owns the frame and asserts it; the funnel takes the front of the Y span, and a
# deeper box adds its top wall behind rather than growing the part.
collar_w = 159.0        # collar footprint (X) — the frame's width less 2 × brim_margin. The
                        # funnel takes the top wall's FULL width: it stands behind the display
                        # facet, which spans the machine, so there is nothing beside it to leave
                        # room for
collar_d = collar_w     # collar footprint (Y) — as deep as it is wide. One rise serves every
                        # run (see ramp_angle), struck on the LONGEST of them, and square is
                        # the most plan area a given rise serves: plan area is what buys
                        # capacity cheaply
brim_margin = 10.0      # top-wall left between the collar edge and the frame, all around —
                        # one overhang catches the flange, the rest is what stands beyond it
brim_overhang = 7.0     # brim flange reach past the collar — what actually catches the
                        # top wall and holds the funnel out of the box, all around
brim_thickness = 3.0    # flange thickness, resting on the enclosure top
collar_wall = 3.0       # straight press-fit collar wall (opening − bore)
# The funnel is sized in bottles: a full one goes in dumped, not metered, and the
# margin is what keeps a miss off the counter. The ramp's depth is set by its grade
# and the spout by its tube, so the straight section is the only height the funnel's
# volume is in — and it stands between two bounds. The FLOOR is that requirement,
# asserted in `build`. The CEILING is the pack: the chute hangs the ramp, the spout
# and the drain lower with every millimetre of itself, so what the chute may spend is
# the fall `fluid-4` is left off the spout before its first corner
# (`enclosure_assembly.build_funnel`, recorded against this body and held by the machine
# scorecard's `room-holds` gate). It takes that band whole rather than stopping at the
# floor: the collar already fills its frame in both axes, so depth is the only thing
# left that buys capacity.
#   The band the chute stands in is the fall, and the SPOUT takes its cut of that band first:
# the clamp land below is straight tube, and every millimetre of it lowers the drain exactly as a
# millimetre of chute does. So the two are one budget, and the chute is the half of it that buys
# capacity while the spout is the half that buys a joint.
bottle_ml = 440.0       # one SodaStream concentrate bottle
capacity_bottles = 1.3  # funnel capacity to the brim, in bottles — the floor it must clear
chute_h = 21.31        # straight rectangular chute height — brim top down to the ramp start,
                        # and what holds `drop` where the drain's elbow still stands over the
                        # folded deck: the ramp's rise rides its longest half-run, and every
                        # millimetre it grows comes back out of this figure so the drain's
                        # height stands still
neck_dx = 1.85          # neck (ramp foot + spout) off the collar centre. THE SPOUT STANDS OVER
                        # THE SLOT IT DRAINS INTO, and that slot is not on the collar's own
                        # centre: the two source valves leave it between their coils, the
                        # east one stepped outboard (`manifold_layout.SOURCE_SPREAD`), and
                        # V-D's aft corner reaches the fall's own band from the west now that
                        # the folded deck rides `manifold_layout.BARB_STANDOFF` — so the
                        # column stands east of the slot's middle, its tube one air off that
                        # corner and still inside the east coil's fence. A collar centred in
                        # the top wall's frame and a neck centred in the collar would hang the
                        # spout against the west coil — `fluid-4` falls one straight column
                        # off this tip and has no corner to spend stepping across. The offset
                        # costs depth, since it lengthens the floor's long half-run and one
                        # rise serves every run, and what pays for it is the fall under the
                        # spout (`enclosure_assembly.build_funnel`, held by `room-holds`).
neck_dy = 0.0           # neck off the collar centre IN Y, and it is 0: THE FUNNEL KEEPS ITS
                        # OWN MIRROR PLANE ACROSS Y. Every feature of the part — brim, chute,
                        # ramp and spout — stands on one plane through the collar's X axis, so
                        # the depth axis of the mould, of the floor's grade and of the finished
                        # funnel is unhanded, and the Y offset costs no depth the X one does not
                        # already ask for. WHAT THE FITTING NEEDS IS A COLUMN, NOT A BERTH:
                        # the elbow under the spout turns the fall aft inside its own envelope
                        # (`reference/elbow-connector`) and stands one leg under the exit face,
                        # so nothing below the funnel asks the funnel to lean.
ramp_angle = 15.0       # deg — the floor's shallowest line (the long X half-run); the
                        # front/back runs land steeper on their own. Concentrate is
                        # sticky and the funnel has to come out of the machine clean, so
                        # this is graded to SHED, not merely to slope — a shallow floor
                        # holds a residue film that a rinse has to chase. Depth is what
                        # buys it: one rise serves every run, so the grade costs
                        # `_ramp_run × tan(angle)` of it, and the chute gives that back
                        # by shortening (the funnel's volume is the target, not its
                        # depth). What caps it is the pack: the drain hangs lower with
                        # every degree, and the manifold's east elbow row and the lane
                        # its pump-discharge crossings use are directly under the spout.
spout_id = 6.35         # 1/4" outlet bore
spout_wall = 2.0        # spout wall at the tip
clamp_shoulder = 2.0    # silicone left standing either side of the clamp's band
# The straight spout tube below the ramp tip — the CLAMP LAND. The drain stub runs up the
# whole of it (`reference/funnel-drain-stub`) and the worm clamp's band closes on the middle,
# between two shoulders. Above the tip the outer face is the ramp cone, and it is the ramp's
# own grade over the collar's own half-run: a band that reaches it closes on nothing.
spout_tube = _clamp.BAND_W + 2.0 * clamp_shoulder
# The drop stacks the chute below the brim, the ramp rise the shallowest line
# needs at its grade, and the spout tube.
#
# ONE RISE SERVES EVERY RUN, so a longer run is a shallower one — and the rise is struck on
# the LONGEST half-run to the neck, whichever axis that is, so `ramp_angle` describes the
# shallowest line by construction. Both offsets lengthen their own half; the drop grows with
# the longest of them, and `chute_h` is where that growth is paid back so the drain stands
# still.
_ramp_run = (collar_w - 2.0 * collar_wall) / 2.0 - spout_id / 2.0 + abs(neck_dx)
_y_run = (collar_d - 2.0 * collar_wall) / 2.0 - spout_id / 2.0 + abs(neck_dy)
_ramp_rise = max(_ramp_run, _y_run) * math.tan(math.radians(ramp_angle))
drop = (chute_h - brim_thickness) + _ramp_rise + spout_tube

# ONE RISE SERVES EVERY RUN AND IT IS STRUCK ON THE LONGEST, which is what lets `ramp_angle`
# describe the floor's shallowest line by construction. WHICH AXIS THAT LONGEST RUN IS ON is the
# neck's to say: an offset lengthens its own half and shortens the other, so the run the grade
# rides is the run on the axis the neck is offset along — and the neck is offset in X alone. The
# reading is what holds the part to that description, so a neck moved in Y is a floor whose
# depth is being bought on an axis the part is not offset on.
_bounds.state(
    "funnel-floor-grade", "The funnel's floor takes its rise off the half-run the neck lengthens",
    f"the Y half-run at or under the X ({_ramp_run:.2f} mm)",
    _y_run <= _ramp_run + 1e-9,
    f"the neck stands {neck_dy:g} mm off the collar's Y centre, which makes the Y half-run "
    f"{_y_run:.2f} mm against the X's {_ramp_run:.2f} — so the rise the whole floor is struck "
    f"on rides the depth axis, and `neck_dx` buys the funnel nothing.")

# The drain, in the funnel's own frame: the spout exit annulus center. World
# position = this + the funnel's placement; it rides the part.
drain_local = (neck_dx, neck_dy, -drop)


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
    See ../funnel-mold/."""
    w, d = collar_w, collar_d
    cx = cy = 0.0
    bore_w, bore_d = w - 2.0 * collar_wall, d - 2.0 * collar_wall
    top_z = brim_thickness                              # brim top = outermost point
    spout_or = spout_id / 2.0 + spout_wall
    ncx = cx + neck_dx                                  # spout/neck, shifted in X
    ncy = cy + neck_dy                                  # and aft over `fluid-4`'s slot
    ramp_top_z = top_z - chute_h                        # straight chute bottom = ramp start
    end_z = -drop                                       # spout exit (the drain)
    neck_z = end_z + spout_tube                         # ramp tip = tube top

    # Outer: brim flange, a tall straight rectangular chute, a shallow ramp down to
    # the offset spout, straight spout tube.
    solid = (
        _box(w + 2.0 * brim_overhang, d + 2.0 * brim_overhang, 0.0, top_z, cx, cy)
        .fuse(_box(w, d, ramp_top_z, 0.0, cx, cy))
        .fuse(_loft_rc(w, d, cx, cy, ramp_top_z, spout_or, ncx, ncy, neck_z))
        .fuse(_cyl(spout_or, neck_z, end_z, ncx, ncy))
    )
    # Bore: the same chain, one wall in, open at the top and out through the tube.
    cavity = (
        _box(bore_w, bore_d, ramp_top_z, top_z + 1.0, cx, cy)
        .fuse(_loft_rc(bore_w, bore_d, cx, cy, ramp_top_z, spout_id / 2.0, ncx, ncy, neck_z))
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, ncx, ncy))
    )
    meta = {
        "w": w, "d": d, "cx": cx, "cy": cy, "ncx": ncx, "ncy": ncy,
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
    # The chute is what carries the funnel past its floor. Capacity is LINEAR in
    # chute_h (the cone spans the ramp rise, which the X half-run fixes, and the
    # spout tube is fixed), so a miss names the height that closes it.
    want = capacity_bottles * bottle_ml * 1000.0
    if fill < want - 1.0:
        bore_area = m["bore_w"] * m["bore_d"]
        raise ValueError(
            f"the funnel holds {fill / 1000.0:.1f} mL, short of the "
            f"{capacity_bottles:g} × {bottle_ml:g} mL = {want / 1000.0:.1f} mL target — "
            f"set chute_h to {chute_h + (want - fill) / bore_area:.2f} mm")
    return cq.Workplane(obj=solid.cut(cavity)), (
        m["w"], m["d"], m["top_z"] - m["end_z"], m["end_z"], fill,
    )


def main():
    funnel, (w, d, total, end_z, fill) = build()
    out = _here.parent / "funnel.step"
    # The funnel is cast in platinum-cure silicone, and the STEP says so — the card's own picture
    # of it is drawn off this file, the machine's picture off the same colour.
    export_assembly(one_body(funnel, "funnel", M_SILICONE_BLACK), str(out))
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
            "FUNNEL_SPOUT_ID": f"{spout_id:g} mm",
            "FUNNEL_CHUTE": f"{chute_h:g} mm",
            "FUNNEL_LAND": f"{spout_tube:g} mm",
            "FUNNEL_DROP": f"{total:.0f} mm",
            "FUNNEL_CAP": f"{fill / 1000.0:.0f} mL",
            "FUNNEL_HOLD": f"{brim_overhang:g} mm",
            "FUNNEL_MARGIN": f"{brim_margin:g} mm",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
