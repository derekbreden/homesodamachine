"""Lite hopper-funnel silicone mold — the two-piece printed mold that casts the
lite pour-through funnel ([../funnel/](../funnel/funnel.py)) in food-grade
platinum silicone.

Same architecture as the Kitchen edition's mold
([/hardware/printed-parts/zone-c/hopper-funnel-mold/](/hardware/printed-parts/zone-c/hopper-funnel-mold/README.md)),
applied to the lite funnel's geometry (narrow-X, deeper drop, centered spout).
The funnel is a hollow 3 mm shell, so the silicone forms in the gap between an
outer CAVITY (funnel exterior, opening up; brim recess at the rim; spout-pin
register hole in the floor) and an inner CORE (the bore as a plug on a top plate
that registers over the cavity, with a centered lead-nosed pin continuing the
Ø6.35 spout bore into the floor; pour port + vents through the plate).

Both halves pull straight up — a funnel is its own draft. Geometry is read live
from the lite funnel: funnel.build_solids() returns the exterior + bore solids,
and the mold wraps those, so it tracks the funnel as the lite packing keeps
settling. Both are relieved shells, not solid blocks: a registration skin and a
forming wall around the funnel, braced by a rib lattice, with the dead volume
hollowed out — the cavity relief vents to the bed, the core plug to a shell
vented through the plate. Forming surfaces carry no release clearance (the mold
face is the part face). Pour / degas / post-cure bake: see README.md and the
Kitchen mold's notes.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
_FUNNEL = _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "funnel"
sys.path.insert(0, str(_FUNNEL))
from _cadq_export import export_assembly, export_step
from docgen import substitute_md
import funnel as F

# --- mold parameters (shared with the Kitchen mold) -------------------------
mold_wall = 8.0       # cavity-block wall around the funnel exterior
mold_base = 10.0      # solid floor below the spout tip
skirt_wall = 6.0      # core registration-skirt wall (wraps the cavity top)
plate_thk = 10.0      # core top plate — forms the brim top, carries the vents
lip_h = 10.0          # how far the skirt drops over the cavity (registration)
lip_gap = 0.20        # slip between the skirt and the cavity outside
pin_reg_clear = 0.15  # slip for the spout pin in the cavity-floor register hole
fill_port_id = 4.0    # pour port through the plate (fallback to the open-cavity pour)
fill_port_csink = 5.0   # shallow pour basin countersunk on top of the fill port
vent_id = 2.5         # vent holes through the plate, over the brim ring

# --- lightening: a ribbed shell, not a solid block --------------------------
skin_wall = 5.0       # outer registration skin kept around the cavity block
bowl_wall = 6.0       # forming wall kept around the funnel — silicone containment
                      # and a gas-tight PETG backing for the vacuum-degas pour
rib_wall = 4.0        # ribs bracing the skin to the forming wall
rib_pitch = 30.0      # target spacing of the relief rib lattice — short enough that
                      # the steep deep-Y forming wall bridges between ribs, no support
plate_relief = 4.0    # solid kept under the plate's brim face when its top is relieved
boss_wall = 4.0       # solid kept around each plate through-hole when relieved


# --- primitives (match the funnel's own idiom) ------------------------------

def _box(w, d, z0, z1, cx, cy):
    """Axis-aligned box of footprint w×d centered at (cx, cy), spanning z[z0,z1]."""
    return (
        cq.Workplane("XY").box(w, d, z1 - z0, centered=(True, True, False))
        .translate((cx, cy, z0)).val()
    )


def _cyl(r, z_top, z_bot, cx, cy):
    return cq.Solid.makeCylinder(r, z_top - z_bot, cq.Vector(cx, cy, z_bot), cq.Vector(0, 0, 1))


def _loft_rc(w, d, cx0, cy0, z0, r1, cx1, cy1, z1):
    """Loft from a rectangle (w×d at (cx0,cy0)) down to a circle (r1 at (cx1,cy1))."""
    return (
        cq.Workplane("XY", origin=(cx0, cy0, z0)).rect(w, d)
        .workplane(offset=z1 - z0).center(cx1 - cx0, cy1 - cy0).circle(r1)
        .loft(combine=True).val()
    )


def _rib_lattice(block_w, block_d, z0, z1, cx, cy, t, pitch):
    """A grid of thin vertical ribs spanning z[z0,z1] over the block footprint.
    Kept out of the relief so the steep forming wall lands on a rib every `pitch`
    and bridges between them; off the forming face, the funnel cut removes them."""
    nx, ny = max(1, round(block_w / pitch)), max(1, round(block_d / pitch))
    ribs = _box(t, block_d, z0, z1, cx, cy)
    for i in range(nx + 1):
        ribs = ribs.fuse(_box(t, block_d, z0, z1, cx - block_w / 2.0 + i * block_w / nx, cy))
    for j in range(ny + 1):
        ribs = ribs.fuse(_box(block_w, t, z0, z1, cx, cy - block_d / 2.0 + j * block_d / ny))
    return ribs


def _grown_funnel(m, g):
    """The funnel exterior offset outward by g. Kept solid when the cavity block
    is relieved, so a bowl_wall of PETG always backs the forming face — the
    relief never reaches the silicone."""
    w, d, cx, cy, ncx = m["w"], m["d"], m["cx"], m["cy"], m["ncx"]
    bo, sor = m["brim_overhang"], m["spout_or"]
    oz1, top_z, rtz, nz, ez = m["oz1"], m["top_z"], m["ramp_top_z"], m["neck_z"], m["end_z"]
    return (
        _box(w + 2.0 * bo + 2.0 * g, d + 2.0 * bo + 2.0 * g, oz1, top_z, cx, cy)
        .fuse(_box(w + 2.0 * g, d + 2.0 * g, rtz, oz1, cx, cy))
        .fuse(_loft_rc(w + 2.0 * g, d + 2.0 * g, cx, cy, rtz, sor + g, ncx, cy, nz))
        .fuse(_cyl(sor + g, nz, ez, ncx, cy))
    )


# --- the mold ---------------------------------------------------------------

def build():
    solid, bore, m = F.build_solids()
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

    # Relieve the dead solid: keep a skin_wall registration shell, a bowl_wall of
    # PETG around the funnel, a mold_base spout boss carrying the pin register, and
    # a rib lattice — hollow the rest. The relief opens down to the bed (no sealed
    # void) and stops bowl_wall short of the funnel, so it never reaches the
    # forming face; the lattice carries the steep deep-Y wall on short bridges.
    relief = _box(block_w - 2.0 * skin_wall, block_d - 2.0 * skin_wall,
                  floor_z, top_z + 1.0, cx, cy).cut(_grown_funnel(m, bowl_wall))
    relief = relief.cut(_cyl(m["spout_or"] + bowl_wall, end_z, floor_z, ncx, cy))
    relief = relief.cut(_rib_lattice(block_w, block_d, floor_z, top_z, cx, cy, rib_wall, rib_pitch))
    cavity = cavity.cut(relief)

    # CORE: the bore is the plug; extend the spout pin (lead-nosed so it
    # self-centers) down through the cavity floor; cap with a top plate joined to
    # a skirt that drops over the cavity outside for registration.
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

    # Hollow the bulk of the plug: a bowl_wall shell around the chute portion of
    # the bore, tapering to a point down the ramp (no flat ceiling when printed
    # plate-down) and vented up through the plate. The vent holds the hollow at
    # chamber pressure through the degas, so no gas sits trapped behind the
    # forming face; the ramp + spout stay solid.
    plug_hollow = _box(m["bore_w"] - 2.0 * bowl_wall, m["bore_d"] - 2.0 * bowl_wall,
                       m["ramp_top_z"], top_z + plate_thk + 1.0, cx, cy).fuse(
        _loft_rc(m["bore_w"] - 2.0 * bowl_wall, m["bore_d"] - 2.0 * bowl_wall, cx, cy,
                 m["ramp_top_z"], 1.5, ncx, cy, m["neck_z"]))
    core = core.cut(plug_hollow)

    # Pour port + vents through the plate, over the brim flange ring.
    rx = (m["bore_w"] / 2.0 + brim_w / 2.0) / 2.0
    ry = (m["bore_d"] / 2.0 + brim_d / 2.0) / 2.0
    ring_w = min(brim_w - m["bore_w"], brim_d - m["bore_d"]) / 2.0
    assert fill_port_csink <= ring_w, f"fill-port csink {fill_port_csink} > brim ring {ring_w:.1f} mm"
    fill_xy = (cx - rx, cy - ry)
    vents = [(cx + rx, cy - ry), (cx - rx, cy + ry), (cx + rx, cy + ry), (cx - rx, cy), (cx + rx, cy)]
    core = core.cut(_cyl(fill_port_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, *fill_xy))
    core = core.cut(_cyl(fill_port_csink / 2.0, top_z + plate_thk + 1.0, top_z + plate_thk - 3.0, *fill_xy))
    for vx, vy in vents:
        core = core.cut(_cyl(vent_id / 2.0, top_z + plate_thk + 1.0, top_z - 1.0, vx, vy))

    # Relieve the plate top: keep plate_relief of solid over the brim face, a
    # boss around each through-hole, the skin and a rib cross. The plate prints
    # face-down, so the relief opens up — no support — and leaves the brim-forming
    # face and the pour/vent seals solid.
    bosses = _cyl(fill_port_id / 2.0 + boss_wall, top_z + plate_thk, top_z, *fill_xy)
    for vx, vy in vents:
        bosses = bosses.fuse(_cyl(vent_id / 2.0 + boss_wall, top_z + plate_thk, top_z, vx, vy))
    plate_relief_cut = _box(plate_w - 2.0 * skin_wall, plate_d - 2.0 * skin_wall,
                            top_z + plate_relief, top_z + plate_thk + 1.0, cx, cy).cut(bosses)
    plate_relief_cut = plate_relief_cut.cut(_box(rib_wall, plate_d, top_z + plate_relief, top_z + plate_thk, cx, cy))
    plate_relief_cut = plate_relief_cut.cut(_box(plate_w, rib_wall, top_z + plate_relief, top_z + plate_thk, cx, cy))
    core = core.cut(plate_relief_cut)

    # Tidy origin: centered in XY, mold floor at z=0; same transform on both
    # halves keeps them mated. funnel = solid.cut(bore) directly (no content
    # clearance check — that is the funnel's concern, not the mold's).
    dx, dy, dz = -cx, -cy, -floor_z
    cavity = cavity.translate((dx, dy, dz))
    core = core.translate((dx, dy, dz))
    funnel = solid.cut(bore).translate((dx, dy, dz))

    info = {
        "funnel": funnel,
        "sil_vol": funnel.Volume(),
        "sil_wall": m["collar_wall"],
        "spout_id": m["spout_id"],
        "cavity_bb": cavity.BoundingBox(),
        "core_bb": core.BoundingBox(),
        "cavity_vol": cavity.Volume(),
        "core_vol": core.Volume(),
        "n_vents": len(vents),
    }
    return cavity, core, info


def main():
    cavity, core, info = build()
    here = _here.parent
    export_step(cq.Workplane(obj=cavity), str(here / "funnel-mold-cavity.step"))
    print("-> funnel-mold-cavity.step")
    export_step(cq.Workplane(obj=core), str(here / "funnel-mold-core.step"))
    print("-> funnel-mold-core.step")

    # Exploded assembly (cavity → silicone funnel → core, stacked up).
    assy = cq.Assembly()
    assy.add(cavity, name="cavity", color=cq.Color(0.72, 0.72, 0.74, 1.0))
    assy.add(info["funnel"].translate((0, 0, 45)), name="funnel", color=cq.Color(0.27, 0.73, 0.35, 1.0))
    assy.add(core.translate((0, 0, 100)), name="core", color=cq.Color(0.42, 0.70, 0.97, 1.0))
    export_assembly(assy, str(here / "funnel-mold-assembly.step"))
    print("-> funnel-mold-assembly.step")

    cbb, kbb = info["cavity_bb"], info["core_bb"]
    petg_density = 1.27e-3  # g/mm³, solid PETG (100 % infill)
    cav_g = info["cavity_vol"] * petg_density
    core_g = info["core_vol"] * petg_density
    print(f"  cavity:  {cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm, {cav_g:.0f} g")
    print(f"  core:    {kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm, {core_g:.0f} g")
    print(f"  pair @100% infill: {cav_g + core_g:.0f} g")
    print(f"  silicone per pour: {info['sil_vol']:.0f} mm³ = {info['sil_vol'] / 1000.0:.1f} mL")

    substitute_md(
        here / "README.md",
        variables={
            "MOLD_WALL": f"{mold_wall:g} mm",
            "MOLD_BASE": f"{mold_base:g} mm",
            "PLATE_THK": f"{plate_thk:g} mm",
            "SKIN_WALL": f"{skin_wall:g} mm",
            "BOWL_WALL": f"{bowl_wall:g} mm",
            "RIB_WALL": f"{rib_wall:g} mm",
            "SIL_WALL": f"{info['sil_wall']:g} mm",
            "SPOUT_BORE": f"{info['spout_id']:g} mm",
            "SIL_VOLUME": f"{info['sil_vol'] / 1000.0:.0f} mL",
            "CAVITY_DIMS": f"{cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm",
            "CORE_DIMS": f"{kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm",
            "CAVITY_MASS": f"{cav_g:.0f} g",
            "CORE_MASS": f"{core_g:.0f} g",
            "PAIR_MASS": f"{cav_g + core_g:.0f} g",
            "FILL_D": f"{fill_port_id:g} mm",
            "VENT_D": f"{vent_id:g} mm",
            "N_VENTS": f"{info['n_vents']}",
        },
        expected_counts={
            "MOLD_WALL": 1, "MOLD_BASE": 1, "PLATE_THK": 1, "SIL_WALL": 2,
            "SKIN_WALL": 1, "BOWL_WALL": 1, "RIB_WALL": 1,
            "SPOUT_BORE": 1, "SIL_VOLUME": 1, "CAVITY_DIMS": 1, "CORE_DIMS": 1,
            "CAVITY_MASS": 1, "CORE_MASS": 1, "PAIR_MASS": 1,
            "FILL_D": 1, "VENT_D": 1, "N_VENTS": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
