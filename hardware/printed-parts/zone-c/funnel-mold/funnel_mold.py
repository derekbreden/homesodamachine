"""Funnel silicone mold — the two-piece printed mold that casts the
Zone C funnel ([../funnel/](../funnel/README.md)) in
food-grade platinum silicone.

The funnel is a hollow shell of one wall (`funnel.collar_wall`), so the silicone
forms in the gap between two printed halves:

  * CAVITY — a block with the funnel *exterior* carved out, opening up. The brim
    sits in a recess at the top rim; below the spout's own exit face the pocket
    carries on `tip_buffer` further as a blind, drafted bore that the floor closes.
  * CORE — the funnel *interior* (the bore) as a plug, hanging from a top plate
    that forms the brim's top face and registers over the cavity via a skirt. The
    plug STOPS AT THE RAMP TIP, and a socket bores up the cone from that tip.
    Vents + a pour port pass through the plate.
  * ROD — a 1/4" ground dowel dropped into that socket, and the whole of the Ø6.35
    spout bore. It bottoms in the socket, so `rod_len` sets its own reach; it stops
    `tip_cap` short of the pocket's blind floor; and it is a slip fit, so the core
    lifts OFF it. Stock, not a print: it writes no STEP.

THE SPOUT IS CAST LONG AND CLOSED, AND CUT TO LENGTH AFTERWARDS. Nothing here
moulds the exit face. The spout runs on `tip_buffer` past it into a blind pocket
and closes there, so the rod hangs free in silicone with no hole to find and
nothing to press. The rod runs the full buffer, so the cast tube is OPEN bore
wherever it is cut, and the buffer steps `tip_step` in at the exit plane — a
shoulder a blade seats flat against, which is the cut. Everything below that
shoulder is scrap.

Both halves pull straight up — a funnel is its own draft. The geometry is read
live from the funnel: `funnel.build_solids()` returns the exterior and
bore solids, and the mold is those Booleaned out of blocks, so the mold tracks
the part. Forming surfaces carry no clearance (the mold face *is* the part face;
platinum silicone shrinks ~0.1 %); release is by silicone flex + a mould-release
film, not by gap.

Pour (see README.md): degas the silicone, pour into the open cavity to the brim
line, lower the core, and let air + excess weep out the plate vents. Vacuum the
filled mold for the deep spout if you have the chamber. Then trim the tip at its
shoulder — the funnel is not a funnel until that cut is made.
"""

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
_FUNNEL = _repo / "hardware" / "printed-parts" / "zone-c" / "funnel"
sys.path.insert(0, str(_FUNNEL))
from _cadq_export import export_assembly
from _materials import M_PETG_BLACK, M_SILICONE_BLACK, M_STAINLESS, one_body
from docgen import substitute_md
import funnel as HF

# --- mold parameters --------------------------------------------------------
mold_wall = 8.0       # cavity-block wall around the funnel exterior
mold_base = 10.0      # solid floor below the spout tip
skirt_wall = 6.0      # core registration-skirt wall (wraps the cavity top)
plate_thk = 10.0      # core top plate — forms the brim top, carries the vents
lip_h = 10.0          # how far the skirt drops over the cavity (registration)
lip_gap = 0.0         # slip between the skirt and the cavity outside
# The sacrificial tip. The mould casts the spout PAST the funnel's own exit face and closes
# it, and the cut that opens it is a post-process. What that buys is a core with no press fit
# on it: the rod hangs free in silicone the whole way down and reaches nothing.
tip_buffer = 12.0     # spout cast below the funnel's exit face — scrap, and the room the cut has
tip_step = 1.0        # how far the buffer's outer wall steps IN at that face. The step is the
                      # cut line: an annular shoulder facing down, which a razor laid flat on it
                      # follows to exactly the spout length the drain joint is dimensioned to
                      # (`reference/funnel-drain-stub` takes `funnel.spout_tube` whole). It steps
                      # in rather than out so the scrap still draws straight up out of its bore
tip_cap = 2.0         # silicone left under the rod's tip — what closes the cast tube's end
tip_draft = 0.5       # draft on the buffer's bore, off its radius over its length, so the scrap
                      # tube breaks its own seal at once instead of being pulled out of a
                      # straight sleeve it fits exactly
# THE SPOUT'S BORE IS NOT PRINTED. Below the ramp tip the core is a dropped-in dowel, and the
# print stops where the cone does. What that costs is one piece of stock; what it buys is three
# things a printed column cannot have.
#   IT CANNOT BE LEVERED. The rod is not fixed to the plate, so nothing that frees the plug
# reaches it: the core lifts OFF it and leaves it standing in the cast, and it then comes out on
# its own, straight, gripped where it stands. A Ø6.35 column buried this deep parts at about
# 34 N sideways and takes about 950 N to pull, so every hand on it wants to be an axial one —
# and each of the three pulls this mould asks for is.
#   IT IS ROUND. That bore is a SEALING bore — `reference/funnel-drain-stub` closes the worm
# clamp's band onto silicone that was moulded on this surface — and ground stock is rounder and
# smoother than any printed column of the same nominal.
#   IT IS STOCK. A bent rod is replaced from the drawer, and the core it drops into is
# untouched — the plug's own finish (sand, seal, gas off, coupon-test) outlives it.
rod_d = 6.35          # 1/4" ground dowel, the same nominal round as `funnel.spout_id`
rod_len = 50.8        # 1/4" × 2" — the stock length, and what the socket's depth is cut to so
                      # the rod sets its own reach by bottoming in it
rod_fit = 0.10        # slip on the socket's diameter. Small: the socket is the one place
                      # silicone could wick past the rod, and it will not cross this in a pot
                      # life
# THE POUR PORT TAKES THE WHOLE RING. Silicone is poured degassed and it is honey: what a
# port costs to pour through is its narrowest section, and there is nothing to trade against
# it here. What comes out of a wide one is a wide sprue standing on the brim's top face, and
# that is cut flush with the tip in the same pass. So the port is not a size — it is whatever
# the rim ring leaves once its land is kept, and it grows with the ring.
fill_port_land = 1.0  # PETG left between the port's edge and the brim's outer edge. The port
                      # stands in the ring's CORNER, where the ring is a square of its own
                      # width, so the land is struck on the outer edge — the near one — and the
                      # bore mouth inboard is further off than that by the corner's diagonal.
                      # Past this edge the plate stops sitting on silicone and starts sitting on
                      # the cavity's own top face, and a port over that is a port that weeps
                      # onto the parting line
fill_dish_d = 20.0    # the pour dish's mouth, on top of the plate — a cone necking into the
                      # port. It is the target the cup is aimed at, and it lives in the plate's
                      # own top with no silicone under it, so it is not held to the ring
fill_dish_h = 4.0     # how deep that cone necks down, out of `plate_thk`
vent_id = 2.5         # vent holes through the plate, over the brim ring


# --- primitives (match the funnel's own idiom) ------------------------------

def _box(w, d, z0, z1, cx, cy):
    """Axis-aligned box of footprint w×d centered at (cx, cy), spanning z[z0,z1]."""
    return (
        cq.Workplane("XY").box(w, d, z1 - z0, centered=(True, True, False))
        .translate((cx, cy, z0)).val()
    )


def _cyl(r, z_top, z_bot, cx, cy):
    return cq.Solid.makeCylinder(r, z_top - z_bot, cq.Vector(cx, cy, z_bot), cq.Vector(0, 0, 1))


# --- the mold ---------------------------------------------------------------

def build():
    solid, bore, m = HF.build_solids()
    # The neck's own centre, both axes — the spout, the buffer and the rod all stand on it.
    ncx, ncy = m["ncx"], m["ncy"]
    ocx, ocy = m["out_cx"], m["out_cy"]
    top_z, end_z = m["top_z"], m["end_z"]
    spout_r = m["spout_id"] / 2.0
    out_w, out_d = m["out_w"], m["out_d"]         # the brim = the part's outer footprint
    block_w, block_d = out_w + 2.0 * mold_wall, out_d + 2.0 * mold_wall
    plate_w, plate_d = block_w + 2.0 * skirt_wall, block_d + 2.0 * skirt_wall
    # THE SACRIFICIAL TIP. `end_z` is the funnel's own exit face and so the CUT plane; the
    # mould carries the spout `tip_buffer` past it into a blind, drafted bore, and the block's
    # floor stands under THAT. The bore steps `tip_step` inside the spout's own radius, which
    # leaves an annulus of that width facing down at the cut plane — the shoulder the blade
    # rides. Stepping IN keeps every face below the funnel narrowing downward, so the scrap
    # draws up out of its own bore with the part.
    buf_or = m["spout_or"] - tip_step
    buf_z = end_z - tip_buffer
    floor_z = buf_z - mold_base
    tip_pocket = cq.Solid.makeCone(buf_or - tip_draft, buf_or, tip_buffer,
                                   cq.Vector(ncx, ncy, buf_z), cq.Vector(0, 0, 1))

    # CAVITY: block from floor to brim top, funnel exterior carved out (opens
    # up), the sacrificial tip's pocket carrying on below it and CLOSED — nothing
    # passes the floor, so there is no register to press and no path to weep down.
    cavity = (
        _box(block_w, block_d, floor_z, top_z, ocx, ocy)
        .cut(solid)
        .cut(tip_pocket)
    )

    # THE ROD, and the socket that holds it. What stands in silicone is the spout's own land
    # plus the buffer less the cap it leaves; what the core holds is the rest of the stock
    # length. The two add to `rod_len`, so the rod BOTTOMS in the socket and sets its own reach
    # — nothing measures it on assembly. It stops `tip_cap` short of the pocket's blind floor,
    # so silicone closes the cast tube under it and the rod touches no part of the mould but
    # this socket.
    neck_z = m["neck_z"]                          # the ramp tip: where the bore stops being round
    rod_below = HF.spout_tube + tip_buffer - tip_cap
    rod_socket = rod_len - rod_below
    rod_bot = buf_z + tip_cap
    rod_top = neck_z + rod_socket
    assert rod_socket > 0.0, (
        f"a {rod_len:g} mm rod is shorter than the {rod_below:.1f} mm of it that stands in "
        f"silicone — bill a longer one")
    assert rod_top <= top_z, (
        f"the socket reaches z {rod_top:.2f} and the plate's underside is {top_z:.2f} — the "
        f"socket is boring out of the plug and into the plate. Bill a shorter rod")
    rod = _cyl(rod_d / 2.0, rod_top, rod_bot, ncx, ncy)
    plate = _box(plate_w, plate_d, top_z, top_z + plate_thk, ocx, ocy)
    skirt = (
        _box(plate_w, plate_d, top_z - lip_h, top_z, ocx, ocy)
        .cut(_box(block_w + 2.0 * lip_gap, block_d + 2.0 * lip_gap, top_z - lip_h - 1.0, top_z, ocx, ocy))
    )
    # The printed plug STOPS AT THE RAMP TIP — below it the round is the rod's, not the
    # print's — and the socket bores up the cone from that same tip.
    plug = (
        bore.cut(_cyl(spout_r + 1.0, neck_z, buf_z - 1.0, ncx, ncy))
        .cut(_cyl((rod_d + rod_fit) / 2.0, rod_top, neck_z - 1.0, ncx, ncy))
    )
    core = plug.fuse(plate).fuse(skirt)

    # Pour port + vents through the plate, set over the brim's rim ring (the
    # flange + collar band between the bore mouth and the brim's outer edge)
    # so they open into the silicone, not the plug.
    ring_w = m["rim_ring"]
    # The ring is what the port is allowed, less a land either side of it.
    fill_port_id = ring_w - 2.0 * fill_port_land
    assert fill_dish_h < plate_thk, (
        f"the pour dish necks {fill_dish_h} mm into a {plate_thk} mm plate — it breaks through")
    rx = out_w / 2.0 - ring_w / 2.0
    ry = out_d / 2.0 - ring_w / 2.0
    fill_xy = (ocx - rx, ocy - ry)
    vents = [(ocx + rx, ocy - ry), (ocx - rx, ocy + ry), (ocx + rx, ocy + ry),
             (ocx - rx, ocy), (ocx + rx, ocy)]
    core = core.cut(_cyl(fill_port_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, *fill_xy))
    # and the dish over it — a cone from the port's own bore out to `fill_dish_d` at the plate's
    # top face, so what the pour is aimed at is the mouth and what it necks into is the port.
    core = core.cut(cq.Solid.makeCone(
        fill_port_id / 2.0, fill_dish_d / 2.0, fill_dish_h,
        cq.Vector(fill_xy[0], fill_xy[1], top_z + plate_thk - fill_dish_h), cq.Vector(0, 0, 1)))
    for vx, vy in vents:
        core = core.cut(_cyl(vent_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, vx, vy))

    # Tidy origin: centered in XY, mold floor at z=0. Same transform on both
    # halves keeps them mated.
    dx, dy, dz = -ocx, -ocy, -floor_z
    cavity = cavity.translate((dx, dy, dz))
    core = core.translate((dx, dy, dz))
    # What comes OUT of the mould is the funnel with its tip still on: the part, plus the
    # silicone standing in the buffer around the rod. That is the body the pour is mixed for
    # and the body the cut is made on, so it is the one drawn here.
    tip = tip_pocket.cut(rod)
    funnel = HF.build()[0].val()
    cast = funnel.fuse(tip).translate((dx, dy, dz))

    info = {
        "cast": cast,
        # The rod is stock, so it writes no STEP of its own — it is drawn in the exploded
        # picture and billed as a length, the way `reference/funnel-drain-stub` is.
        "rod": rod.translate((dx, dy, dz)),
        "rod_len": rod_len, "rod_below": rod_below, "rod_socket": rod_socket,
        "sil_vol": cast.Volume(),
        "part_vol": funnel.Volume(),
        "tip_vol": tip.Volume(),
        "fill_d": fill_port_id,
        "fill_xy": fill_xy,
        "sil_wall": m["collar_wall"],
        "spout_id": m["spout_id"],
        "cavity_bb": cavity.BoundingBox(),
        "core_bb": core.BoundingBox(),
        "n_vents": len(vents),
    }
    return cavity, core, info


def main():
    cavity, core, info = build()
    here = _here.parent
    export_assembly(one_body(cq.Workplane(obj=cavity), "funnel-mold-cavity",
                             M_PETG_BLACK), str(here / "funnel-mold-cavity.step"))
    print("-> funnel-mold-cavity.step")
    export_assembly(one_body(cq.Workplane(obj=core), "funnel-mold-core",
                             M_PETG_BLACK), str(here / "funnel-mold-core.step"))
    print("-> funnel-mold-core.step")

    # Exploded assembly (cavity → silicone funnel → core, stacked up) so the
    # thumbnail shows how the three nest.
    assy = cq.Assembly()
    # Two printed halves off the black spool and the black silicone they cast between them —
    # what tells the three apart in this picture is the 45 mm of air each is lifted by.
    assy.add(cavity, name="cavity", color=M_PETG_BLACK)
    assy.add(info["cast"].translate((0, 0, 45)), name="funnel", color=M_SILICONE_BLACK)
    assy.add(core.translate((0, 0, 100)), name="core", color=M_PETG_BLACK)
    # The rod, standing where it stands in the cast — the one piece of this mould that is
    # neither printed nor poured.
    assy.add(info["rod"].translate((0, 0, 72)), name="rod", color=M_STAINLESS)
    export_assembly(assy, str(here / "funnel-mold-assembly.step"))
    print("-> funnel-mold-assembly.step")

    cbb, kbb = info["cavity_bb"], info["core_bb"]
    print(f"  cavity:  {cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm")
    print(f"  core:    {kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm")
    print(f"  silicone per pour: {info['sil_vol'] / 1000.0:.1f} mL "
          f"({info['part_vol'] / 1000.0:.1f} the funnel, {info['tip_vol'] / 1000.0:.1f} the tip cut off it)")
    print(f"  tip cast {tip_buffer:g} mm past the exit face, closed, and stepped {tip_step:g} mm "
          f"in at the cut")
    print(f"  rod: Ø{rod_d:g} × {info['rod_len']:g} dowel — {info['rod_socket']:.1f} mm in the "
          f"core's socket, {info['rod_below']:.1f} mm standing in silicone")
    print(f"  pour port: Ø{info['fill_d']:g} through the plate at "
          f"({info['fill_xy'][0]:.1f}, {info['fill_xy'][1]:.1f}), Ø{fill_dish_d:g} dish over it")

    substitute_md(
        here / "README.md",
        variables={
            "MOLD_WALL": f"{mold_wall:g} mm",
            "MOLD_BASE": f"{mold_base:g} mm",
            "PLATE_THK": f"{plate_thk:g} mm",
            "SIL_WALL": f"{info['sil_wall']:g} mm",
            "SPOUT_BORE": f"{info['spout_id']:g} mm",
            "SIL_VOLUME": f"{info['sil_vol'] / 1000.0:.0f} mL",
            "TIP_BUFFER": f"{tip_buffer:g} mm",
            "ROD_D": f"{rod_d:g} mm",
            "ROD_LEN": f"{rod_len:g} mm",
            "ROD_SOCKET": f"{info['rod_socket']:.1f} mm",
            "ROD_BELOW": f"{info['rod_below']:.1f} mm",
            "ROD_FIT": f"{rod_fit:g} mm",
            "LIP_H": f"{lip_h:g} mm",
            "BRIM_SQ": f"{info['cast'].BoundingBox().xlen:.0f} mm",
            "TIP_STEP": f"{tip_step:g} mm",
            "CAVITY_DIMS": f"{cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm",
            "CORE_DIMS": f"{kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm",
            "FILL_D": f"{info['fill_d']:g} mm",
            "FILL_DISH": f"{fill_dish_d:g} mm",
            "FILL_LAND": f"{fill_port_land:g} mm",
            "MOLD_VENT_D": f"{vent_id:g} mm",
            "N_VENTS": f"{info['n_vents']}",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
