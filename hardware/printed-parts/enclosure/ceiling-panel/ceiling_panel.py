"""Ceiling panel — enclosure-back-top's ceiling, printed flat and slid in.

In the BOX'S OWN FRAME, not a frame of its own: every plane this part stands on is a
plane the box states about itself, and a second copy of any of them is a second machine.
Its underside lies on the interior ceiling and its top face IS the appliance's top
surface, so the part occupies the top wall's own section over its whole footprint.

WHY IT IS A SEPARATE PART. enclosure-back-top prints mouth-down on its seam rim with the
build axis +Z (`enclosure.py`'s module docstring), so a ceiling printed in that piece is
a roof laid down `piece_h` over the open service bay. front-top's ceiling is two
corbelled side strips with the hopper throat as the void between them. back-top has no
throat of its own, so its ceiling is this part instead: a flat slab on the bed, show face
down, slid in through the Y-seam mouth before the front half telescopes in.

WHAT THE PIECE KEEPS is the two side strips either side of this panel, `rail_run` wide,
and it is those strips that carry the dado this panel's tongues run in — a drawer bottom
in a dado. The strips' own section, the run of their corbels and the bosses under the two
screw stations are back-top's; what this file states is the MATING FIGURES they are cut
to (`dado`, `screw_stations`, `fore_y`, `aft_y`, `panel_half_w`, `underside_z`).

Plan:

  * WIDTH is `hopper_funnel.collar_w`, whole. The throat's opening is that wide and this
    panel's edges are collinear with it, so the ceiling reads as ONE channel down the
    machine — funnel in the front of it, panel filling the rest — rather than as a lid
    with a hole beside it.
  * FORE EDGE is the collar's own aft edge, and it is load-bearing: the funnel's brim
    overhangs the collar by `hopper_funnel.brim_overhang` and lands on this panel's first
    `brim_overhang` of show face, inside the `brim_margin` of top wall that
    `enclosure_assembly`'s `funnel-brim-margin` asks at that free edge. The two screw
    heads stand in that same landing — reached through the throat with the funnel out,
    covered by the brim with it in.
  * AFT EDGE is back-top's own back-wall face, which is the panel's stop. The pack stands
    hard against the ceiling under that wall — the C14's flange, both umbilical unions,
    the CO2 neoFit and the tap-water chain's crown — so the storey there holds nothing a
    corbelled closure off the wall could descend into, and the panel takes the span whole.

The two screw stations pin the fore end against the slide. Aft of them the tongues hold
the panel down and the back wall holds it in, so nothing else is fastened.

AND EVERY RIB ROOTED ON THE CEILING OVER THIS FIELD IS THIS PART'S. The flow meter's two
saddles and the three anchors bored for `carb-1`, `co2-2` and the WR1110's barrel used to
hang off back-top; back-top has no ceiling there any more, so they hang off this.
`enclosure.ceiling_stations` splits the stations and both parts read that one call, so
neither can grow a rib the other grew too. It is also the better bench for them: a seat
hanging off the top wall is an upward-opening cradle with the piece inverted, and this
panel inverted is a flat plate on the bench.
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
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "enclosure"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "zone-c" / "hopper-funnel"))
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly
from _materials import M_PETG_BLACK, one_body
from docgen import substitute_md
import enclosure as _enc
import hopper_funnel as _funnel

# --- the planes the box states, and the panel that fills them ----------------

# The top wall's inner face, off the appliance's own stated height — the same arithmetic
# `enclosure_assembly.interior_ceiling` takes, and the plane the WHOLE rear storey hangs
# from: `deck_storey` is this less the tap-water chain's crown and its tie clearance, and
# every port, receptacle, axis and anchor on that deck is placed off it. The panel's
# underside lies ON it and nothing below moves.
underside_z = _enc.appliance_height - 2.0 * _enc.wall
# The show face — the appliance's top surface. The panel carries the top wall's own
# section, so this is one `wall` over the interior ceiling and the exterior top face both.
show_z = underside_z + _enc.wall
# How tall enclosure-back-top stands on the bed: its Z-seam rim to this face. Everything
# the piece closes over its bay is printed at that height, over open air.
piece_h = show_z - _enc.z_seam

# The throat's own width. The panel is exactly as wide as the funnel's collar so the two
# edges of the ceiling channel run unbroken from the display facet to the back wall.
panel_w = _funnel.collar_w
panel_half_w = panel_w / 2.0
# The collar's aft edge — the box stands the collar's front on `funnel_front_y` and the
# basin reaches aft for its capacity (`enclosure_assembly.funnel_centre`).
fore_y = _enc.funnel_front_y + _funnel.collar_d
# back-top's own back-wall face. The box's interior rear plane is `rear_plane_y`; this
# piece's wall stands `back_top_wall_t` in from the exterior and the panel butts it.
aft_y = _enc.back_top_wall_face()
depth = aft_y - fore_y

# The side strip left either side of the panel, and the ONE figure back-top's ceiling is
# cut to: back-top's own flank face less the panel's half-width. The rail is that strip,
# and its inboard face is where the dado is cut.
rail_run = _enc.back_top_flank_face()[1] - panel_half_w

# The funnel's brim lands on this much of the show face at the fore edge, and the screw
# heads stand under it.
brim_seat = _funnel.brim_overhang

# --- the tongue and the dado it runs in --------------------------------------
#
# THE WHOLE JOINT LIVES IN ONE `wall`, because the rail has one `wall` of section at the
# dado's mouth: the strip's corbel grows below the ceiling going OUTBOARD and reaches
# nothing at the panel's edge. So the tongue, its slip and the lip over it share the top
# wall's own thickness, and what closes the section is the lip's roof:
#
# THE DADO'S ROOF RISES AT `relief_chamfer` FROM THE BLIND END TO THE MOUTH, the way every
# relief ceiling on this box does — a roof left flat would hang over the slot in a piece
# that prints mouth-down. A 45 degree roof climbs one millimetre of section per millimetre
# of reach, so the dado is exactly as DEEP as the lip over it is THICK, and the ramp lands
# on the show face at the mouth with no flat anywhere.
dado_slip = 0.30        # printed-fit clearance on each face of the tongue — a slide fit
                        # down the whole `depth` of groove, not a press
# With the roof at 45 degrees the section reads tongue + slip + lip = `wall` and
# lip = reach + slip, which leaves the tongue SQUARE: as thick as it reaches.
tongue_t = (_enc.wall - 2.0 * dado_slip) / 2.0
tongue_reach = tongue_t
lip_t = tongue_reach + dado_slip     # the rail's section over the dado, at the blind end
dado_depth = lip_t                   # 45 degrees: the roof spends its whole reach climbing

dado_floor_z = underside_z                            # the ceiling plane, both parts alike
dado_roof_z = dado_floor_z + tongue_t + dado_slip     # at the blind end; it climbs inboard
dado_mouth_x = panel_half_w                           # the rail's inboard face
dado_blind_x = panel_half_w + dado_depth


def dado():
    """The groove back-top cuts in each rail's inboard face, as
    `(mouth_x, blind_x, floor_z, roof_z, chamfer_deg)` on the +X side; the −X side is its
    mirror. The roof is struck at the blind end and rises at `chamfer_deg` to the mouth,
    where it runs out on the show face."""
    return (dado_mouth_x, dado_blind_x, dado_floor_z, dado_roof_z, _enc.relief_chamfer)


# --- the two screws that pin the fore end ------------------------------------
#
# A 3 mm lid cannot bury a socket cap, so the panel takes the box's own web at each
# station: `cap_web_t` of section, the head down in the standard `head_cbore_dia` by
# `head_cbore_depth` seat with `cap_web_land` under it, and the pad hanging into the bay
# for the difference. `screw_len` then lands exactly: the land and a ruthex M3 short spend
# `screw_reach` of the under-head length and `mount_bore_relief` takes the rest, which
# main() reads back against the box's own screw.
screw_pad_t = _enc.cap_web_t
screw_seat_z = show_z - screw_pad_t             # the pad's underside — the boss's crown
screw_land = _enc.cap_web_land                  # what the screw pulls through
screw_reach = screw_land + _enc.heatset_depth   # of the screw's own under-head length
screw_pad_r = _enc.head_cbore_dia / 2.0 + _enc.boss_ligament
# THE PAD HANGS BELOW THE CEILING, AND ONLY THE PANEL'S OWN FIELD HAS ROOM FOR IT: outboard
# of the mouth the rail's corbel is standing in that storey, and a pad reaching into it
# could not travel the dado. So the station stands as far outboard as a full
# `boss_ligament` round its counterbore allows, which lands the pad tangent to the mouth.
screw_x = panel_half_w - screw_pad_r
# And centred in the brim's landing, the only `brim_overhang` of show face the flange
# covers — so the head is hidden by the brim and open to the throat without it.
screw_y = fore_y + brim_seat / 2.0
# How far the rail's boss reaches under the pad's crown: the insert and the air past the
# screw's tip, the section every M3 heat-set in this box stands in.
screw_bore_z = screw_seat_z - (_enc.heatset_depth + _enc.mount_bore_relief)


def screw_stations():
    """The two retention screws as `((x, y), ...)` in the box's frame — the axes the pad's
    bores and the rail's bosses are both struck on."""
    return ((-screw_x, screw_y), (screw_x, screw_y))


# --- primitives -------------------------------------------------------------

def _slab(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _post(r, cx, cy, z0, z1):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(cx, cy, z0), cq.Vector(0, 0, 1))


# --- the panel --------------------------------------------------------------

def build(box=None):
    """The panel as one solid: the field, a tongue down each long edge, the two screw pads sunk
    for their heads — and, when a `box` is handed in, THE CEILING'S OWN FURNITURE.

    EVERY RIB ROOTED ON THE INTERIOR CEILING OVER THIS FIELD ROOTS ON THIS PART. The flow meter's
    two saddles and the three anchors under the top wall used to hang off back-top; back-top has no
    ceiling there any more, so they hang off this. `enclosure.ceiling_stations` is the one call
    that splits them, and back-top reads the same call for its own half, so neither can grow a rib
    the other grew too. The ribs are built by `enclosure`'s own two builders on the box's own
    `inner`, which is what keeps a saddle here the same saddle it was on the piece.

    AND IT IS A BETTER BENCH FOR THEM. A seat hanging off the top wall is an upward-opening cradle
    with the piece inverted, and this panel inverted is a flat plate on the bench: the meter drops
    into its two saddles and the runs into their three, straps go round, and the loaded panel then
    slides into back-top's dados."""
    field = _slab(-panel_half_w, panel_half_w, fore_y, aft_y, underside_z, show_z)
    # The tongues, one down each long edge, at the panel's own underside.
    for sx in (-1.0, 1.0):
        edge = sx * panel_half_w
        field = field.fuse(_slab(min(edge, edge + sx * tongue_reach),
                                 max(edge, edge + sx * tongue_reach),
                                 fore_y, aft_y,
                                 underside_z, underside_z + tongue_t))
    # The screw pads, clipped to the panel's plan — each one's fore face is the panel's
    # fore edge, which is the plane the brim bears on.
    plan = _slab(-panel_half_w - tongue_reach, panel_half_w + tongue_reach,
                 fore_y, aft_y, screw_seat_z - 1.0, show_z)
    for cx, cy in screw_stations():
        field = field.fuse(_post(screw_pad_r, cx, cy, screw_seat_z, show_z).intersect(plan))
    solid = cq.Workplane(obj=field)
    # The head's seat, sunk from the show face, and the shank's clearance under it.
    for cx, cy in screw_stations():
        solid = solid.cut(cq.Workplane(obj=_post(
            _enc.head_cbore_dia / 2.0, cx, cy, show_z - _enc.head_cbore_depth, show_z + 1.0)))
        solid = solid.cut(cq.Workplane(obj=_post(
            _enc.screw_clear_dia / 2.0, cx, cy, screw_seat_z - 1.0, show_z + 1.0)))
    if box is None:
        return solid
    saddles, ribs = _enc.ceiling_stations(box.digiten_saddles, box.tube_anchors, panel=True)
    body = solid.val()
    body = _enc._digiten_saddles(body, box.inner, saddles,
                                 fore_y, aft_y, box.inner[4], show_z)
    body = _enc._tube_anchors(body, box.inner, ribs,
                              fore_y, aft_y, box.inner[4], show_z)
    return cq.Workplane(obj=body)


def machine_of():
    """The machine's pack and the box around it — `enclosure.machine_of`, and the same deferred
    import for the same reason: `enclosure_assembly` builds its assembly around these walls, so
    reading it at module scope would have this file importing a module that imports it back."""
    sys.path.insert(0, str(_repo / "hardware" / "manifold-layout"))
    import enclosure_assembly
    _assy, _pack, box = enclosure_assembly.machine()
    return box


def main():
    box = machine_of()
    panel = build(box)
    body = panel.val()
    b = body.BoundingBox()
    solids, shells = len(body.Solids()), len(body.Shells())
    if solids != 1 or shells != 1:
        raise ValueError(
            f"the ceiling panel came through as {solids} solid(s) in {shells} shell(s) — a "
            f"slide-in lid is one body, and a second one is a tongue or a pad that missed "
            f"the field it was fused to")
    if screw_reach > _enc.screw_len + 1e-9:
        raise ValueError(
            f"the retention screw has to cross {screw_land:g} mm of land and land "
            f"{_enc.heatset_depth:g} mm in its insert — {screw_reach:.2f} mm under the head, "
            f"and the box's own screw is {_enc.screw_len:g}. Thin the pad or lengthen it")
    bed_x, bed_y = _enc.H2C_X, _enc.H2C_Y
    lies = min(b.xlen, b.ylen) <= min(bed_x, bed_y) and max(b.xlen, b.ylen) <= max(bed_x, bed_y)
    if not lies:
        raise ValueError(
            f"the panel is {b.xlen:.1f} x {b.ylen:.1f} mm and the H2C's bed is "
            f"{bed_x:g} x {bed_y:g} — it prints flat or it does not print")

    out = _here.parent / "ceiling-panel.step"
    export_assembly(one_body(panel, "ceiling-panel", M_PETG_BLACK), str(out))
    print(f"-> {out.name}")
    print(f"  field:   {panel_w:.1f} x {depth:.1f} x {_enc.wall:.1f} mm, "
          f"x +-{panel_half_w:g}, y {fore_y:g}..{aft_y:g}, z {underside_z:g}..{show_z:g}")
    print(f"  bbox:    {b.xlen:.1f} x {b.ylen:.1f} x {b.zlen:.1f} mm "
          f"(tongues out to +-{panel_half_w + tongue_reach:g}, pads down to {screw_seat_z:g}, "
          f"ribs to {b.zmin:g})")
    print(f"  tongue:  {tongue_t:.2f} thick x {tongue_reach:.2f} reach, "
          f"{dado_slip:g} slip per face")
    print(f"  dado:    x {dado_mouth_x:g}..{dado_blind_x:g}, z {dado_floor_z:g}..{dado_roof_z:g}, "
          f"roof at {_enc.relief_chamfer:g} deg to the mouth; lip {lip_t:.2f} at the blind end")
    print(f"  rails:   {rail_run:g} mm side strip each side, "
          f"back-top flank face at +-{_enc.back_top_flank_face()[1]:g}")
    print(f"  screws:  M3x{_enc.screw_len:g} at x +-{screw_x:.3f}, y {screw_y:g} — "
          f"pad {screw_pad_t:g} thick, seat z {screw_seat_z:g}, boss bore to z {screw_bore_z:g}, "
          f"{screw_reach:.2f} of the {_enc.screw_len:g} under the head spent")
    print(f"  brim:    lands y {fore_y:g}..{fore_y + brim_seat:g} on the show face")
    saddles, ribs = _enc.ceiling_stations(box.digiten_saddles, box.tube_anchors, panel=True)
    print(f"  carries: {0 if saddles is None else len(saddles[3])} meter saddle(s), "
          f"{len(ribs)} ceiling rib(s) — "
          + ", ".join(f"({m[0]:.2f}, {m[1]:.2f}) r{r:g}" for m, _u, _n, r in ribs))
    print(f"  piece:   back-top stands {piece_h:g} mm on its seam rim at z {_enc.z_seam:g}")
    print(f"  bed:     {b.xlen:.1f} x {b.ylen:.1f} on the H2C's {bed_x:g} x {bed_y:g}")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "PANEL_W": f"{panel_w:g} mm",
            "PANEL_HALF_W": f"{panel_half_w:g}",
            "PANEL_D": f"{depth:g} mm",
            "PANEL_T": f"{_enc.wall:g} mm",
            "PIECE_H": f"{piece_h:g} mm",
            "PANEL_FORE": f"{fore_y:g}",
            "PANEL_AFT": f"{aft_y:g}",
            "PANEL_UNDER": f"{underside_z:g}",
            "PANEL_SHOW": f"{show_z:g}",
            "PANEL_BBOX_X": f"{b.xlen:g} mm",
            "RAIL_RUN": f"{rail_run:g} mm",
            "TONGUE_T": f"{tongue_t:g} mm",
            "TONGUE_REACH": f"{tongue_reach:g} mm",
            "DADO_SLIP": f"{dado_slip:g} mm",
            "DADO_DEPTH": f"{dado_depth:g} mm",
            "DADO_ROOF": f"{dado_roof_z:g}",
            "LIP_T": f"{lip_t:g} mm",
            "CHAMFER": f"{_enc.relief_chamfer:g}°",
            "SCREW_X": f"{screw_x:g}",
            "SCREW_Y": f"{screw_y:g}",
            "SCREW_PAD_T": f"{screw_pad_t:g} mm",
            "SCREW_SEAT": f"{screw_seat_z:g}",
            "SCREW_LAND": f"{screw_land:g} mm",
            "SCREW_REACH": f"{screw_reach:g} mm",
            "SCREW_BORE": f"{screw_bore_z:g}",
            "SCREW_LEN": f"M3x{_enc.screw_len:g}",
            "HEATSET": f"{_enc.heatset_depth:g} mm",
            "BRIM_SEAT": f"{brim_seat:g} mm",
            "BRIM_MARGIN": f"{_funnel.brim_margin:g} mm",
            "BED_X": f"{_enc.H2C_X:g} mm",
            "BED_Y": f"{_enc.H2C_Y:g} mm",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    # THIS FILE, UNDER THE NAME EVERYTHING ELSE IMPORTS IT BY — `enclosure.py` carries the same
    # line for the same reason. Run as a script this is `__main__`, and `enclosure._ceiling`
    # would `import ceiling_panel` and get a SECOND copy of every figure in it.
    sys.modules.setdefault(__name__ if __name__ != "__main__" else "ceiling_panel",
                           sys.modules[__name__])
    main()
