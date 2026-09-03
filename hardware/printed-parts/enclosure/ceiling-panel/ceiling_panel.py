"""Ceiling panel — enclosure-back-top's ceiling, printed flat and slid in.

In the BOX'S OWN FRAME, not a frame of its own: every plane this part stands on is a
plane the box states about itself, and a second copy of any of them is a second machine.
Its 3 mm show skin spans the established pack ceiling lane and its top face IS the appliance's
top surface. A broad 11 mm structural field descends into the room, relieved only where the
placed bodies and their zip-tie approaches need that volume. The fixed side strips present a
separate 6 mm physical face without moving the lane any body was placed from.

WHY IT IS A SEPARATE PART. enclosure-back-top prints mouth-down on its seam rim with the
build axis +Z (`enclosure.py`'s module docstring), so a ceiling printed in that piece is
a roof laid down `piece_h` over the open service bay. front-top's ceiling is two
corbelled side strips with the funnel's throat as the void between them. back-top has no
throat of its own, so its ceiling is this part instead: a flat plate on the bed, show face
down, all pockets opening upward, slid in through the Y-seam mouth before the front half
telescopes in.

WHAT THE PIECE KEEPS is the two side strips either side of this panel, `rail_run` wide,
and it is those strips that carry the dado this panel's tongues run in — a drawer bottom
in a dado. Each tongue is a 6 mm square rail centred on the fixed strips' physical face, wholly
rooted in the structural field and finishing at the established pack lane. The strips' own
section, the run of their corbels and the dados are back-top's; what this file states is the
MATING FIGURES they are cut to (`dado`, `fore_y`, `aft_y`, `panel_half_w`, `underside_z`).

Plan:

  * WIDTH is `funnel.collar_w`, whole. The throat's opening is that wide and this
    panel's edges are collinear with it, so the ceiling reads as ONE channel down the
    machine — funnel in the front of it, panel filling the rest — rather than as a lid
    with a hole beside it. The visible skin grows into an 11 mm structural field on the
    interior side; rounded pockets leave the exact headroom the purchased bodies need.
  * FORE EDGE is the collar's own aft edge, and it is load-bearing: the funnel's brim
    overhangs the collar by `funnel.brim_overhang` and lands on this panel's first
    `brim_overhang` of show face, inside the `brim_margin` of top wall that
    `enclosure_assembly`'s `funnel-brim-margin` asks at that free edge. The show face and
    the panel field stay whole.
  * AFT EDGE is back-top's own back-wall face, which is the panel's stop. Rounded pockets
    preserve the C14, both upper umbilical unions, the CO2 neoFit and the tap-water chain;
    the field between them carries continuously to the wall.

The two continuous dados hold the panel in X and Z and provide the fitted sliding contact;
the +Y wall is its home stop. The panel and fixed strips carry no separate keeper hardware.

AND EVERY RIB ROOTED ON THE CEILING OVER THIS FIELD IS THIS PART'S. The flow meter's two
anchors and the three anchors bored for `carb-1`, `co2-2` and the WR1110's barrel hang from
this field.
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
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "enclosure"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "zone-c" / "funnel"))
sys.path.insert(0, str(_tools))
import fits
import plan
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, one_body
# The bound this file states about its own show face, recorded at import for the machine's card.
import _stated_bounds as _bounds
from docgen import substitute_md
import enclosure as _enc
import funnel as _funnel

# --- the planes the box states, and the panel that fills them ----------------

# The pack's established ceiling lane, off the appliance's own stated height — the same arithmetic
# `enclosure_assembly.interior_ceiling` takes, and the plane the WHOLE rear storey hangs
# from: `deck_storey` is this less the tap-water chain's crown and its tie clearance, and
# every port, receptacle, axis and anchor on that deck is placed off it. Nothing below moves.
underside_z = _enc.appliance_height - _enc.floor_t - _enc.wall
# The show face — the appliance's top surface. The panel carries the top wall's own
# section, so this is one `wall` over the interior ceiling and the exterior top face both.
show_z = underside_z + _enc.wall
# The fixed strips' physical interior face. It is distinct from `underside_z`: the latter is
# the immutable pack/furniture lane, while this is the six-millimetre printed ceiling section.
fixed_under_z = show_z - _enc.back_top_ceiling_t
# The broad interior field absorbs the roots of the meter and tube furniture.
# It is sparse infill rather than a solid billet in the stated print profile; the CAD states the
# load path and the slicer states how that envelope is filled.
structural_t = 11.0
structural_under_z = show_z - structural_t
relief_corner_r = 3.0
# Two body clearances facing across less than one wall do not leave a structural web between
# them. Their openings meet over the depth they share; each pocket keeps its own roof above it.
relief_min_web = _enc.wall

# THE PANEL SHOWS ONE FACE AND IT LIES FLAT, so the box's field never crosses it. That field is
# struck along a plan and runs vertically (`enclosure.flute_rails`); the top surface is the top
# rail's own answer, unfluted like the 45° facet and the pockets round the drop cutouts
# (`cadlib/flute_skin.py`). The only band of this piece a run could pass over is the show skin's
# own edge — and every one of those edges is a mating face anyway: the ±X pair runs in back-top's
# dado, the fore edge takes the funnel's brim, and the aft edge butts the back wall.
_bounds.state(
    "ceiling-panel-reveal", "The ceiling panel's show face is the top, and its edge is a reveal",
    f"under {_enc.flute_full_depth_height:g} mm of standing edge",
    _enc.flute_reach(show_z - underside_z) < _enc.flute_depth,
    f"the show skin stands {show_z - underside_z:g} mm on edge, at or over the "
    f"{_enc.flute_full_depth_height:g} mm at which the field reaches its full "
    f"{_enc.flute_depth:g} mm — so a groove would land "
    f"{_enc.flute_reach(show_z - underside_z):.3f} mm on it, in a dado nobody sees")
# How tall enclosure-back-top stands on the bed: its Z-seam rim to this face. Everything
# the piece closes over its bay is printed at that height, over open air.
piece_h = show_z - _enc.z_seam

# The throat's own width. The panel is exactly as wide as the funnel's collar so the two
# edges of the ceiling channel run unbroken from the display facet to the +Y wall.
panel_w = _funnel.collar_w
panel_half_w = panel_w / 2.0
# The collar's aft edge — the box stands the collar's front on `funnel_front_y` and the
# funnel reaches aft for its capacity (`enclosure_assembly.funnel_centre`).
fore_y = _enc.funnel_front_y + _funnel.collar_d
# back-top's own back-wall face. The box's interior rear plane is `rear_plane_y`; this
# piece's wall stands `back_top_wall_t` in from the exterior and the panel butts it.
aft_y = _enc.back_top_wall_face()
depth = aft_y - fore_y

# The side strip left either side of the panel, and the ONE figure back-top's ceiling is
# cut to: back-top's own flank face less the panel's half-width. The rail is that strip,
# and its inboard face is where the dado is cut.
rail_run = _enc.back_top_flank_face()[1] - panel_half_w

# The funnel's brim lands on this much of the show face at the fore edge.
brim_seat = _funnel.brim_overhang

# --- the tongue and the dado it runs in --------------------------------------
#
# THE RAIL FILLS THE GROWN FIXED SECTION. Its six-millimetre square is centred on the fixed
# strip's physical face, wholly rooted in the broad structural field and finishing at the
# established furniture lane. Outboard, back-top's corbel grows one millimetre deeper for every
# millimetre of run. At the dado's blind end that gives the captured rail a full lower ligament
# as well as the show-skin lip above it.
#
# THE DADO'S ROOF RISES AT `relief_chamfer` FROM THE BLIND END TO THE MOUTH, the way every
# relief ceiling on this box does — a roof left flat would hang over the slot in a piece
# that prints mouth-down. A 45 degree roof climbs one millimetre of section per millimetre
# of reach and runs clear of the show face at the open mouth. The roof rises off the tongue's
# own top plane at the blind edge — the plane the fixed C14 surround's crown is clipped to as
# well — so the tongue's tip, one slip short of that edge, clears the roof by one slip and every
# point of the rail behind it by more. At the blind end the slide clearance is struck on the
# rail's floor, its tip and the mouth-side face.
dado_slip = fits.slip   # printed-fit clearance on each face of the tongue — a slide fit
                        # down the whole `depth` of groove, not a press
# One grown fixed section in both directions makes the tongue a 36 mm2 rail.
tongue_t = _enc.back_top_ceiling_t
tongue_reach = _enc.back_top_ceiling_t
# The tongues' outer faces — the widest the panel's plan reaches.
rail_outer_x = panel_half_w + tongue_reach
tongue_floor_z = fixed_under_z - tongue_t / 2.0
tongue_roof_z = fixed_under_z + tongue_t / 2.0
dado_depth = tongue_reach + dado_slip

dado_floor_z = tongue_floor_z - dado_slip
dado_roof_z = tongue_roof_z                   # at the blind edge; it climbs inboard
dado_mouth_x = panel_half_w                    # the rail's inboard face
dado_blind_x = panel_half_w + dado_depth
# The fixed corbel's lower face at this run is `fixed_under_z - dado_depth`; what remains below the
# groove and above it are the two ligaments that capture the rail at the blind end.
dado_lower_ligament = dado_floor_z - (fixed_under_z - dado_depth)
lip_t = show_z - dado_roof_z


def dado():
    """The groove back-top cuts in each rail's inboard face, as
    `(mouth_x, blind_x, floor_z, roof_z, chamfer_deg)` on the +X side; the −X side is its
    mirror. The roof is struck at the blind end and rises at `chamfer_deg` to the mouth,
    where it runs out on the show face."""
    return (dado_mouth_x, dado_blind_x, dado_floor_z, dado_roof_z, _enc.relief_chamfer)


# --- primitives -------------------------------------------------------------

def _slab(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def structural_stock():
    """The ceiling's unrelieved eleven-millimetre envelope below the show face."""
    return _slab(-panel_half_w, panel_half_w, fore_y, aft_y,
                 structural_under_z, underside_z)


def rail_stock(y0=fore_y, y1=aft_y):
    """Both exact six-millimetre-square rails over one Y band, before printed-fit clearance."""
    rails = None
    for sx in (-1.0, 1.0):
        edge = sx * panel_half_w
        rail = _slab(min(edge, sx * rail_outer_x), max(edge, sx * rail_outer_x),
                     y0, y1, tongue_floor_z, tongue_roof_z)
        rails = rail if rails is None else rails.fuse(rail)
    return rails


def _body_relief_cavity(reliefs):
    """The body pockets as one cavity: a prism per roof level, each the figure every pocket
    reaching that level makes together. Two pockets facing across less than `relief_min_web`
    are one opening over the depth both claim, a pocket crossing the field-and-rail plan is
    square where it leaves it, and every enclosed corner is rounded to `relief_corner_r`."""
    pockets = [(x0, x1, y0, y1, min(underside_z, top))
               for _name, x0, x1, y0, y1, top in reliefs]
    pockets = [p for p in pockets if p[4] > structural_under_z]
    roofs = sorted({p[4] for p in pockets})
    within = (-rail_outer_x, rail_outer_x, fore_y, aft_y)
    prisms = []
    for floor, roof in zip([structural_under_z - 0.1] + roofs[:-1], roofs):
        figure = plan.closed(plan.union(
            plan.rect(x0, x1, y0, y1) for x0, x1, y0, y1, top in pockets if top >= roof),
            relief_min_web)
        prisms += plan.prism(figure, floor, roof, relief_corner_r, within=within)
    return tuple(prisms)


def _tie_reliefs(box):
    """Full anchor footprints whose existing zip tie approach enters the deeper field."""
    meter_anchors, ribs = _enc.ceiling_stations(
        box.pack.flow_meter_anchors, box.pack.tube_anchors, panel=True)
    raw = structural_stock()
    pockets = []
    if meter_anchors:
        x_axis, _z_axis, seat_r, bands = meter_anchors
        reach = seat_r + _enc.flow_meter_anchor_wall + _enc.tie_cav_buffer
        for by0, by1 in bands:
            mid = (by0 + by1) / 2.0
            tie = _slab(
                x_axis - reach, x_axis + reach,
                mid - _enc.tie_cav_w / 2.0, mid + _enc.tie_cav_w / 2.0,
                structural_under_z - 0.1, underside_z + 0.1)
            if raw.intersect(tie).Volume() > 1e-6:
                pockets.append(tie)
    for mid, u, n, seat_r in ribs:
        origin = tuple(mid[k] - u[k] * _enc.tube_anchor_len / 2.0 for k in range(3))
        crown = seat_r + _enc.wall
        tie_origin = tuple(origin[k] + u[k] * _enc.tie_cav_wall for k in range(3))
        tie = _enc._anchor_rib(tie_origin, u, n, _enc.tie_cav_w,
                                  crown, crown, crown + _enc.tie_t)
        if raw.intersect(tie).Volume() <= 1e-6:
            continue
        if tuple(n) != (0, 0, 1):
            raise ValueError(
                f"a ceiling zip tie relief names root {n}; only a +Z root can be cut out of "
                f"the panel's downward-open structural field")
        b_face = underside_z - mid[2]
        pockets.append(_enc._anchor_rib(
            origin, u, n, _enc.tube_anchor_len,
            crown + _enc.tie_t + _enc.tie_cav_buffer, 0.0, b_face))
    return tuple(pockets)


def _relieved_stock(box):
    """The broad field and rails after body headroom and zip tie approaches are opened below."""
    stock = structural_stock().fuse(rail_stock())
    for prism in _body_relief_cavity(box.pack.ceiling_reliefs):
        stock = stock.cut(prism)
    for pocket in _tie_reliefs(box):
        stock = stock.cut(pocket)
    # A wall several prisms cut is one face.
    return cq.Workplane(obj=stock).clean().val()


# --- the panel --------------------------------------------------------------

def build(box=None):
    """The panel as one solid: show skin, relieved structural field, tongues and furniture.

    THE 11 MM FIELD IS THE STRUCTURE. Its downward-open pockets are struck from the purchased
    bodies' intersections with the unrelieved stock, so the broad remainder carries load in two
    dimensions while most furniture roots disappear into it. A box-less build keeps the stock
    whole; the machine build hands in the exact relief stations.

    EVERY RIB ROOTED ON THE INTERIOR CEILING OVER THIS FIELD ROOTS ON THIS PART. The flow meter's
    two anchors and the three run anchors under the top wall used to hang off back-top; it has no
    ceiling there any more, so they hang off this. `enclosure.ceiling_stations` is the one call
    that splits them, and back-top reads the same call for its own half, so neither can grow a rib
    the other grew too. The ribs are built by `enclosure`'s own two builders on the box's own
    `inner`, which is what keeps an anchor here the same anchor it was on the piece.

    AND IT IS A BETTER BENCH FOR THEM. A seat hanging off the top wall is an upward-opening cradle
    with the piece inverted, and this panel inverted is a flat plate on the bench: the meter drops
    into its two anchors and the runs into their three, zip ties go round, and the loaded panel then
    slides into back-top's dados."""
    field = _slab(-panel_half_w, panel_half_w, fore_y, aft_y, underside_z, show_z)
    stock = (_relieved_stock(box) if box is not None
             else structural_stock().fuse(rail_stock()))
    field = field.fuse(stock)
    solid = cq.Workplane(obj=field)
    if box is None:
        return solid
    # The C14 surround belongs wholly to back-top and reaches this panel's underside. Its
    # constant-section pocket is open at the aft edge, so the fixed crown enters as the panel
    # slides home; the show skin above the pocket remains whole and lands on that crown.
    c14_pocket = _enc.c14_ceiling_pocket(
        box.inner, box.outer, box.pack.c14, box.pack.back_ports,
        structural_stock().fuse(rail_stock()))
    if c14_pocket is not None and c14_pocket.Volume() > 1e-6:
        solid = solid.cut(c14_pocket)
    # If the RJ11 keystone's fixed snap-in receptacle reaches this underside, its rectangular
    # running-clearance pocket stays open through the aft edge. A lower receptacle returns no
    # pocket and leaves the panel untouched.
    keystone_pocket = _enc.keystone_ceiling_pocket(
        box.inner, box.outer, box.pack.keystone,
        structural_stock().fuse(rail_stock()))
    if keystone_pocket is not None and keystone_pocket.Volume() > 1e-6:
        solid = solid.cut(keystone_pocket)
    # The same bore used by back-top opens the purchased part's insertion room through any
    # surrounding field material which remains outside the fixed surround's pocket.
    c14_geometry = _enc._c14_tunnel_geometry(
        box.inner, box.outer, box.pack.c14, box.pack.back_ports,
        box.inner[4], box.outer[5])
    if c14_geometry is not None:
        _feature, c14_bore, c14_inserts = c14_geometry
        solid = solid.cut(c14_bore)
        for cutter in c14_inserts:
            solid = solid.cut(cutter)
    meter_anchors, ribs = _enc.ceiling_stations(
        box.pack.flow_meter_anchors, box.pack.tube_anchors, panel=True)
    # THE CEILING THESE ROOT ON IS THIS PANEL'S UNDERSIDE. A rib's two ends climb to the face it
    # stops on and the zip tie's channel is the room they leave between them, so what the builders
    # are handed is the plane this part puts there — `enclosure.piece_root_faces` is the same
    # substitution for a wall, on the pieces that carry one thicker than the box's own.
    roots = box.inner[:5] + (underside_z,)
    body = solid.val()
    body = _enc._flow_meter_anchors(body, roots, meter_anchors,
                                 fore_y, aft_y, box.inner[4], show_z)
    body = _enc._tube_anchors(body, roots, box.inner, ribs,
                              fore_y, aft_y, box.inner[4], show_z)
    return cq.Workplane(obj=body)


def machine_of():
    """The placement-derived box, shared with the enclosure producer.

    An action reads the declared output of `enclosure_box.py`; a direct design run derives the
    live placement. The deferred assembly import keeps the direct path free of the module cycle
    created when the final assembly imports this part back."""
    import _box_spec

    if _box_spec.in_action():
        box, bounds = _box_spec.read(
            _enc.Box, _enc.Bound, (_enc.Pack, _enc.PortField, _enc.Nameplate))
        _enc.BOUNDS[:] = bounds
        return box
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
            f"slide-in lid is one body, and a second one is a tongue or socket that missed "
            f"the field it was fused to")
    if min(dado_lower_ligament, lip_t) <= 0.0:
        raise ValueError(
            f"the ceiling rail's dado leaves {dado_lower_ligament:.2f} mm below and "
            f"{lip_t:.2f} mm above its blind end; both capture ligaments must be positive")
    bed_x, bed_y = _enc.H2C_X, _enc.H2C_Y
    lies = min(b.xlen, b.ylen) <= min(bed_x, bed_y) and max(b.xlen, b.ylen) <= max(bed_x, bed_y)
    if not lies:
        raise ValueError(
            f"the panel is {b.xlen:.1f} x {b.ylen:.1f} mm and the H2C's bed is "
            f"{bed_x:g} x {bed_y:g} — it prints flat or it does not print")

    out = _here.parent / "ceiling-panel.step"
    export_assembly(one_body(panel, "ceiling-panel", M_PETGF_BLACK), str(out))
    print(f"-> {out.name}")
    print(f"  field:   {panel_w:.1f} x {depth:.1f} x {structural_t:.1f} mm structural, "
          f"x +-{panel_half_w:g}, y {fore_y:g}..{aft_y:g}, "
          f"z {structural_under_z:g}..{show_z:g}")
    print(f"  bbox:    {b.xlen:.1f} x {b.ylen:.1f} x {b.zlen:.1f} mm "
          f"(tongues out to +-{rail_outer_x:g}, field to {structural_under_z:g}, "
          f"ribs to {b.zmin:g})")
    print(f"  tongue:  {tongue_t:.2f} thick x {tongue_reach:.2f} reach "
          f"({tongue_t * tongue_reach:.2f} mm2), z {tongue_floor_z:g}..{tongue_roof_z:g}, "
          f"{dado_slip:g} slip per face")
    print(f"  dado:    x {dado_mouth_x:g}..{dado_blind_x:g}, z {dado_floor_z:g}..{dado_roof_z:g}, "
          f"roof at {_enc.relief_chamfer:g} deg to the mouth; "
          f"ligaments {dado_lower_ligament:.2f} below / {lip_t:.2f} above at the blind end")
    print(f"  rails:   {rail_run:g} mm side strip each side, "
          f"back-top flank face at +-{_enc.back_top_flank_face()[1]:g}")
    print(f"  brim:    lands y {fore_y:g}..{fore_y + brim_seat:g} on the show face")
    meter_anchors, ribs = _enc.ceiling_stations(
        box.pack.flow_meter_anchors, box.pack.tube_anchors, panel=True)
    print(f"  carries: {0 if meter_anchors is None else len(meter_anchors[3])} meter anchor(s), "
          f"{len(ribs)} ceiling rib(s) — "
          + ", ".join(f"({m[0]:.2f}, {m[1]:.2f}) r{r:g}" for m, _u, _n, r in ribs))
    print(f"  reliefs: {len(box.pack.ceiling_reliefs)} body pocket(s), "
          f"{len(_tie_reliefs(box))} full zip tie approach pocket(s), rounded r{relief_corner_r:g}")
    print(f"  piece:   back-top stands {piece_h:g} mm on its seam rim at z {_enc.z_seam:g}")
    print(f"  bed:     {b.xlen:.1f} x {b.ylen:.1f} on the H2C's {bed_x:g} x {bed_y:g}")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "PANEL_W": f"{panel_w:g} mm",
            "PANEL_HALF_W": f"{panel_half_w:g}",
            "PANEL_D": f"{depth:g} mm",
            "PANEL_T": f"{_enc.wall:g} mm",
            "STRUCTURAL_T": f"{structural_t:g} mm",
            "STRUCTURAL_UNDER": f"{structural_under_z:g}",
            "RELIEF_R": f"{relief_corner_r:g} mm",
            "RELIEF_MIN_WEB": f"{relief_min_web:g} mm",
            "RELIEF_N": f"{len(box.pack.ceiling_reliefs)}",
            "TIE_RELIEF_N": f"{len(_tie_reliefs(box))}",
            "PIECE_H": f"{piece_h:g} mm",
            "PANEL_FORE": f"{fore_y:g}",
            "PANEL_AFT": f"{aft_y:g}",
            "PANEL_UNDER": f"{underside_z:g}",
            "PANEL_SHOW": f"{show_z:g}",
            "FIXED_UNDER": f"{fixed_under_z:g}",
            "FIXED_T": f"{_enc.back_top_ceiling_t:g} mm",
            "CEILING_GROWTH": f"{_enc.back_top_ceiling_growth:g} mm",
            "PANEL_BBOX_X": f"{b.xlen:g} mm",
            "RAIL_RUN": f"{rail_run:g} mm",
            "TONGUE_T": f"{tongue_t:g} mm",
            "TONGUE_REACH": f"{tongue_reach:g} mm",
            "TONGUE_FLOOR": f"{tongue_floor_z:g}",
            "TONGUE_ROOF": f"{tongue_roof_z:g}",
            "RAIL_AREA": f"{tongue_t * tongue_reach:g} mm²",
            "DADO_SLIP": f"{dado_slip:g} mm",
            "DADO_DEPTH": f"{dado_depth:g} mm",
            "DADO_FLOOR": f"{dado_floor_z:g}",
            "DADO_ROOF": f"{dado_roof_z:g}",
            "DADO_LOWER_LIGAMENT": f"{dado_lower_ligament:g} mm",
            "LIP_T": f"{lip_t:g} mm",
            "CHAMFER": f"{_enc.relief_chamfer:g}°",
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
