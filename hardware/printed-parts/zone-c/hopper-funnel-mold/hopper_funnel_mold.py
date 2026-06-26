"""Hopper-funnel silicone mold — the two-piece printed mold that casts the
Zone C hopper funnel ([../hopper-funnel/](../hopper-funnel/README.md)) in
food-grade platinum silicone.

The funnel is a hollow 3 mm shell, so the silicone forms in the gap between two
printed halves:

  * CAVITY — a block with the funnel *exterior* carved out, opening up. The brim
    sits in a recess at the top rim; the spout pokes down through a pin-register
    hole in the floor.
  * CORE — the funnel *interior* (the bore) as a plug, hanging from a top plate
    that forms the brim's top face and registers over the cavity via a skirt. A
    pin continues the Ø6.35 spout bore down through the cavity floor, fixing the
    thin spout wall concentric. Vents + a pour port pass through the plate.

Both halves pull straight up — a funnel is its own draft. The geometry is read
live from the funnel: `hopper_funnel.build_solids()` returns the exterior and
bore solids, and the mold is those Booleaned out of blocks, so the mold tracks
the part. Forming surfaces carry no clearance (the mold face *is* the part face;
platinum silicone shrinks ~0.1 %); release is by silicone flex + a mould-release
film, not by gap.

Pour (see README.md): degas the silicone, pour into the open cavity to the brim
line, lower the core, and let air + excess weep out the plate vents. Vacuum the
filled mold for the deep spout if you have the chamber.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
_FUNNEL = _repo / "hardware" / "printed-parts" / "zone-c" / "hopper-funnel"
sys.path.insert(0, str(_FUNNEL))
from _cadq_export import export_assembly, export_step
from docgen import substitute_md
import hopper_funnel as HF

# --- mold parameters --------------------------------------------------------
mold_wall = 8.0       # cavity-block wall around the funnel exterior
mold_base = 10.0      # solid floor below the spout tip
skirt_wall = 6.0      # core registration-skirt wall (wraps the cavity top)
plate_thk = 10.0      # core top plate — forms the brim top, carries the vents
lip_h = 10.0          # how far the skirt drops over the cavity (registration)
lip_gap = 0.20        # slip between the skirt and the cavity outside
pin_reg_clear = 0.0   # spout pin press-fits the cavity-floor register hole (PETG seals at zero)
fill_port_id = 4.0    # pour port through the plate (fallback to the open-cavity pour)
fill_port_csink = 5.0   # shallow pour basin countersunk on top of the fill port
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
    cx, cy, ncx = m["cx"], m["cy"], m["ncx"]
    top_z, end_z = m["top_z"], m["end_z"]
    pin_r = m["spout_id"] / 2.0
    brim_w = m["w"] + 2.0 * m["brim_overhang"]
    brim_d = m["d"] + 2.0 * m["brim_overhang"]
    block_w, block_d = brim_w + 2.0 * mold_wall, brim_d + 2.0 * mold_wall
    plate_w, plate_d = block_w + 2.0 * skirt_wall, block_d + 2.0 * skirt_wall
    floor_z = end_z - mold_base

    # CAVITY: block from floor to brim top, funnel exterior carved out (opens
    # up), with a through-hole in the floor that registers the spout pin.
    cavity = (
        _box(block_w, block_d, floor_z, top_z, cx, cy)
        .cut(solid)
        .cut(_cyl(pin_r + pin_reg_clear, end_z, floor_z - 1.0, ncx, cy))
    )

    # CORE: the bore is the plug; extend the spout pin down through the cavity
    # floor; cap with a top plate that forms the brim top, joined to a skirt that
    # drops over the cavity outside for registration.
    # pin with a tapered lead nose so it self-centers into the floor register
    # hole on assembly (the nose is below the silicone — pure registration).
    pin_nose = 3.0
    pin = (
        _cyl(pin_r, end_z - 1.0, floor_z + pin_nose, ncx, cy)
        .fuse(cq.Solid.makeCone(pin_r - 1.0, pin_r, pin_nose, cq.Vector(ncx, cy, floor_z), cq.Vector(0, 0, 1)))
    )
    plate = _box(plate_w, plate_d, top_z, top_z + plate_thk, cx, cy)
    skirt = (
        _box(plate_w, plate_d, top_z - lip_h, top_z, cx, cy)
        .cut(_box(block_w + 2.0 * lip_gap, block_d + 2.0 * lip_gap, top_z - lip_h - 1.0, top_z, cx, cy))
    )
    core = bore.fuse(pin).fuse(plate).fuse(skirt)

    # Pour port + vents through the plate, set over the brim flange ring (between
    # the mouth and the brim edge) so they open into the silicone, not the plug.
    rx = (m["bore_w"] / 2.0 + brim_w / 2.0) / 2.0
    ry = (m["bore_d"] / 2.0 + brim_d / 2.0) / 2.0
    # Pour port + vents live on the brim flange ring; keep them inside it so they
    # open into the silicone and never breach the bore mouth or the brim edge.
    ring_w = min(brim_w - m["bore_w"], brim_d - m["bore_d"]) / 2.0
    assert fill_port_csink <= ring_w, f"fill-port csink {fill_port_csink} > brim ring {ring_w:.1f} mm"
    fill_xy = (cx - rx, cy - ry)
    vents = [(cx + rx, cy - ry), (cx - rx, cy + ry), (cx + rx, cy + ry), (cx - rx, cy), (cx + rx, cy)]
    core = core.cut(_cyl(fill_port_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, *fill_xy))
    core = core.cut(_cyl(fill_port_csink / 2.0, top_z + plate_thk + 1.0, top_z + plate_thk - 3.0, *fill_xy))
    for vx, vy in vents:
        core = core.cut(_cyl(vent_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, vx, vy))

    # Tidy origin: centered in XY, mold floor at z=0. Same transform on both
    # halves keeps them mated.
    dx, dy, dz = -cx, -cy, -floor_z
    cavity = cavity.translate((dx, dy, dz))
    core = core.translate((dx, dy, dz))
    funnel = HF.build()[0].val().translate((dx, dy, dz))

    info = {
        "funnel": funnel,
        "sil_vol": funnel.Volume(),
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
    export_step(cq.Workplane(obj=cavity), str(here / "hopper-funnel-mold-cavity.step"))
    print("-> hopper-funnel-mold-cavity.step")
    export_step(cq.Workplane(obj=core), str(here / "hopper-funnel-mold-core.step"))
    print("-> hopper-funnel-mold-core.step")

    # Exploded assembly (cavity → silicone funnel → core, stacked up) so the
    # thumbnail shows how the three nest.
    assy = cq.Assembly()
    assy.add(cavity, name="cavity", color=cq.Color(0.72, 0.72, 0.74, 1.0))
    assy.add(info["funnel"].translate((0, 0, 45)), name="funnel", color=cq.Color(0.27, 0.73, 0.35, 1.0))
    assy.add(core.translate((0, 0, 100)), name="core", color=cq.Color(0.42, 0.70, 0.97, 1.0))
    export_assembly(assy, str(here / "hopper-funnel-mold-assembly.step"))
    print("-> hopper-funnel-mold-assembly.step")

    cbb, kbb = info["cavity_bb"], info["core_bb"]
    print(f"  cavity:  {cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm")
    print(f"  core:    {kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm")
    print(f"  silicone per pour: {info['sil_vol']:.0f} mm³ = {info['sil_vol'] / 1000.0:.1f} mL")

    substitute_md(
        here / "README.md",
        variables={
            "MOLD_WALL": f"{mold_wall:g} mm",
            "MOLD_BASE": f"{mold_base:g} mm",
            "PLATE_THK": f"{plate_thk:g} mm",
            "SIL_WALL": f"{info['sil_wall']:g} mm",
            "SPOUT_BORE": f"{info['spout_id']:g} mm",
            "SIL_VOLUME": f"{info['sil_vol'] / 1000.0:.0f} mL",
            "CAVITY_DIMS": f"{cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm",
            "CORE_DIMS": f"{kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm",
            "FILL_D": f"{fill_port_id:g} mm",
            "VENT_D": f"{vent_id:g} mm",
            "N_VENTS": f"{info['n_vents']}",
        },
        expected_counts={
            "MOLD_WALL": 1,
            "MOLD_BASE": 1,
            "PLATE_THK": 1,
            "SIL_WALL": 2,
            "SPOUT_BORE": 1,
            "SIL_VOLUME": 1,
            "CAVITY_DIMS": 1,
            "CORE_DIMS": 1,
            "FILL_D": 1,
            "VENT_D": 1,
            "N_VENTS": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
