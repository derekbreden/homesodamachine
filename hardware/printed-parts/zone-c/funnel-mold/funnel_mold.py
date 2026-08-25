"""Funnel silicone mold — the two-piece printed mold that casts the
Zone C funnel ([../funnel/](../funnel/README.md)) in
food-grade platinum silicone.

The funnel is a hollow shell of one wall (`funnel.collar_wall`), so the silicone
forms in the gap between two printed halves:

  * CAVITY — a block with the funnel *exterior* carved out, opening up. The brim
    sits in a recess at the top rim; below the spout's own exit face the pocket
    carries on `tip_buffer` further as a blind, drafted bore that the floor closes.
  * CORE — the funnel *interior* (the bore) as a plug, hanging from a top plate
    that forms the brim's top face and registers over the cavity via a skirt. A
    pin continues the Ø6.35 spout bore down the whole of that buffer, stopping
    `tip_cap` short of its blind bottom. Vents + a pour port pass through the plate.

THE SPOUT IS CAST LONG AND CLOSED, AND CUT TO LENGTH AFTERWARDS. Moulding the
exit face itself is what asked the core for a slender Ø6.35 pin driven through a
zero-clearance hole in the cavity floor — a printed column loaded sideways on
assembly, which is a column that snaps. Nothing here forms that face: the buffer
hangs the pin free in silicone, so there is no hole to find and nothing to press.
The pin runs the full buffer, so the cast tube is OPEN bore wherever it is cut,
and the buffer steps `tip_step` in at the exit plane — a shoulder a blade seats
flat against, which is the cut. Everything below that shoulder is scrap.

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
from _materials import M_PETG_BLACK, M_SILICONE_BLACK, one_body
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
# it, and the cut that opens it is a post-process. What that buys is a core with no slender
# press fit on it: the pin hangs free in silicone the whole way down instead of being driven
# into the cavity floor.
tip_buffer = 12.0     # spout cast below the funnel's exit face — scrap, and the room the cut has
tip_step = 1.0        # how far the buffer's outer wall steps IN at that face. The step is the
                      # cut line: an annular shoulder facing down, which a razor laid flat on it
                      # follows to exactly the spout length the drain joint is dimensioned to
                      # (`reference/funnel-drain-stub` takes `funnel.spout_tube` whole). It steps
                      # in rather than out so the scrap still draws straight up out of its bore
tip_cap = 2.0         # silicone left under the pin's tip — what closes the cast tube's end
tip_draft = 0.5       # draft on the buffer's bore, off its radius over its length, so the scrap
                      # tube breaks its own seal at once instead of being pulled out of a
                      # straight sleeve it fits exactly
pin_lead = 2.0        # taper on the pin's last stretch, so it finds the pocket on the way down
fill_port_id = 4.0    # pour port through the plate (fallback to the open-cavity pour)
fill_port_csink = 5.0   # shallow pour dish countersunk on top of the fill port
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
    # The neck's own centre, both axes — the spout, the buffer and the pin all stand on it.
    ncx, ncy = m["ncx"], m["ncy"]
    ocx, ocy = m["out_cx"], m["out_cy"]
    top_z, end_z = m["top_z"], m["end_z"]
    pin_r = m["spout_id"] / 2.0
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

    # CORE: the bore is the plug; the spout pin runs on down the whole buffer and
    # stops `tip_cap` short of its blind bottom, so silicone closes the cast tube
    # under it and the pin is held by that silicone rather than by the mould. Its
    # last `pin_lead` tapers — a lead-in for the way down, not a press fit.
    # Nothing registers the pin at the bottom and nothing needs to: the skirt
    # squares the core on the cavity, and the pour is symmetric about the pin.
    pin_bot = buf_z + tip_cap
    pin = (
        _cyl(pin_r, end_z, pin_bot + pin_lead, ncx, ncy)
        .fuse(cq.Solid.makeCone(pin_r - 1.0, pin_r, pin_lead,
                                cq.Vector(ncx, ncy, pin_bot), cq.Vector(0, 0, 1)))
    )
    plate = _box(plate_w, plate_d, top_z, top_z + plate_thk, ocx, ocy)
    skirt = (
        _box(plate_w, plate_d, top_z - lip_h, top_z, ocx, ocy)
        .cut(_box(block_w + 2.0 * lip_gap, block_d + 2.0 * lip_gap, top_z - lip_h - 1.0, top_z, ocx, ocy))
    )
    core = bore.fuse(pin).fuse(plate).fuse(skirt)

    # Pour port + vents through the plate, set over the brim's rim ring (the
    # flange + collar band between the bore mouth and the brim's outer edge)
    # so they open into the silicone, not the plug.
    ring_w = m["rim_ring"]
    assert fill_port_csink <= ring_w, f"fill-port csink {fill_port_csink} > rim ring {ring_w:.1f} mm"
    rx = out_w / 2.0 - ring_w / 2.0
    ry = out_d / 2.0 - ring_w / 2.0
    fill_xy = (ocx - rx, ocy - ry)
    vents = [(ocx + rx, ocy - ry), (ocx - rx, ocy + ry), (ocx + rx, ocy + ry),
             (ocx - rx, ocy), (ocx + rx, ocy)]
    core = core.cut(_cyl(fill_port_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, *fill_xy))
    core = core.cut(_cyl(fill_port_csink / 2.0, top_z + plate_thk + 1.0, top_z + plate_thk - 3.0, *fill_xy))
    for vx, vy in vents:
        core = core.cut(_cyl(vent_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, vx, vy))

    # Tidy origin: centered in XY, mold floor at z=0. Same transform on both
    # halves keeps them mated.
    dx, dy, dz = -ocx, -ocy, -floor_z
    cavity = cavity.translate((dx, dy, dz))
    core = core.translate((dx, dy, dz))
    # What comes OUT of the mould is the funnel with its tip still on: the part, plus the
    # silicone standing in the buffer around the pin. That is the body the pour is mixed for
    # and the body the cut is made on, so it is the one drawn here.
    tip = tip_pocket.cut(pin)
    funnel = HF.build()[0].val()
    cast = funnel.fuse(tip).translate((dx, dy, dz))

    info = {
        "cast": cast,
        "sil_vol": cast.Volume(),
        "part_vol": funnel.Volume(),
        "tip_vol": tip.Volume(),
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
    export_assembly(assy, str(here / "funnel-mold-assembly.step"))
    print("-> funnel-mold-assembly.step")

    cbb, kbb = info["cavity_bb"], info["core_bb"]
    print(f"  cavity:  {cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm")
    print(f"  core:    {kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm")
    print(f"  silicone per pour: {info['sil_vol'] / 1000.0:.1f} mL "
          f"({info['part_vol'] / 1000.0:.1f} the funnel, {info['tip_vol'] / 1000.0:.1f} the tip cut off it)")
    print(f"  tip cast {tip_buffer:g} mm past the exit face, closed, and stepped {tip_step:g} mm "
          f"in at the cut")

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
            "TIP_STEP": f"{tip_step:g} mm",
            "CAVITY_DIMS": f"{cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm",
            "CORE_DIMS": f"{kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm",
            "FILL_D": f"{fill_port_id:g} mm",
            "MOLD_VENT_D": f"{vent_id:g} mm",
            "N_VENTS": f"{info['n_vents']}",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
