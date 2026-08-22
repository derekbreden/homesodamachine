"""Ceiling panel — enclosure-back-top's ceiling, printed flat and slid in.

In the BOX'S OWN FRAME, not a frame of its own: every plane this part stands on is a
plane the box states about itself, and a second copy of any of them is a second machine.
Its 3 mm show skin spans the interior ceiling datum and its top face IS the appliance's top
surface. A broad 8 mm structural field descends into the room, relieved only where the placed
bodies and a strap approach need that volume.

WHY IT IS A SEPARATE PART. enclosure-back-top prints mouth-down on its seam rim with the
build axis +Z (`enclosure.py`'s module docstring), so a ceiling printed in that piece is
a roof laid down `piece_h` over the open service bay. front-top's ceiling is two
corbelled side strips with the hopper throat as the void between them. back-top has no
throat of its own, so its ceiling is this part instead: a flat plate on the bed, show face
down, all pockets opening upward, slid in through the Y-seam mouth before the front half
telescopes in.

WHAT THE PIECE KEEPS is the two side strips either side of this panel, `rail_run` wide,
and it is those strips that carry the dado this panel's tongues run in — a drawer bottom
in a dado. Each tongue is a wall-square rail centred on the interior ceiling datum, with
half its section rooted in the structural field and half in the show skin. The strips' own
section, the run of their corbels and the bosses under the two screw stations are back-top's;
what this file states is the MATING FIGURES they are cut to (`dado`, `screw_stations`,
`fore_y`, `aft_y`, `panel_half_w`, `underside_z`).

Plan:

  * WIDTH is `hopper_funnel.collar_w`, whole. The throat's opening is that wide and this
    panel's edges are collinear with it, so the ceiling reads as ONE channel down the
    machine — funnel in the front of it, panel filling the rest — rather than as a lid
    with a hole beside it. The visible skin grows into an 8 mm structural field on the
    interior side; rounded pockets leave the exact headroom the purchased bodies need.
  * FORE EDGE is the collar's own aft edge, and it is load-bearing: the funnel's brim
    overhangs the collar by `hopper_funnel.brim_overhang` and lands on this panel's first
    `brim_overhang` of show face, inside the `brim_margin` of top wall that
    `enclosure_assembly`'s `funnel-brim-margin` asks at that free edge. The two screw
    axes stand in that same landing, but their heads are on back-top's Z− face and their
    inserts enter this panel from below; the show face stays whole.
  * AFT EDGE is back-top's own back-wall face, which is the panel's stop. Rounded pockets
    preserve the C14, both upper umbilical unions, the CO2 neoFit and the tap-water chain;
    the field between them carries continuously to the wall.

The two screw stations pin the fore end against the slide. Aft of them the tongues hold
the panel down and the back wall holds it in, so nothing else is fastened.

AND EVERY RIB ROOTED ON THE CEILING OVER THIS FIELD IS THIS PART'S. The flow meter's two
saddles and the three anchors bored for `carb-1`, `co2-2` and the WR1110's barrel hang from
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
# The broad interior field absorbs all but 1.25 mm of the screw-insert sockets and the roots of
# the meter and tube furniture.
# It is sparse infill rather than a solid billet in the stated print profile; the CAD states the
# load path and the slicer states how that envelope is filled.
structural_t = 8.0
structural_under_z = show_z - structural_t
relief_corner_r = 3.0
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

# The funnel's brim lands on this much of the show face at the fore edge, and the two screw
# axes stand in that full-section landing while their heads remain on the interior side.
brim_seat = _funnel.brim_overhang

# --- the tongue and the dado it runs in --------------------------------------
#
# THE RAIL STRADDLES THE INTERIOR CEILING DATUM. Half its wall-square section roots in the broad
# structural field and half in the show skin, so the whole 3 x 3 section is joined to both parts
# of the panel rather than hanging from the skin alone. Outboard, back-top's corbel grows one
# millimetre deeper for every millimetre of run. At the dado's blind end that gives the captured
# rail a lower ligament as well as the show-skin lip above it.
#
# THE DADO'S ROOF RISES AT `relief_chamfer` FROM THE BLIND END TO THE MOUTH, the way every
# relief ceiling on this box does — a roof left flat would hang over the slot in a piece
# that prints mouth-down. A 45 degree roof climbs one millimetre of section per millimetre
# of reach and runs clear of the show face at the open mouth. At the blind end, the slide
# clearance is struck on all four faces of the square rail.
dado_slip = 0.30        # printed-fit clearance on each face of the tongue — a slide fit
                        # down the whole `depth` of groove, not a press
# One top-wall section in both directions makes the tongue a 9 mm2 rail. Its Z centre is the
# ceiling datum, which puts half the root in the 8 mm field and half in the 3 mm show skin.
tongue_t = _enc.wall
tongue_reach = _enc.wall
tongue_floor_z = underside_z - tongue_t / 2.0
tongue_roof_z = underside_z + tongue_t / 2.0
dado_depth = tongue_reach + dado_slip

dado_floor_z = tongue_floor_z - dado_slip
dado_roof_z = tongue_roof_z + dado_slip       # at the blind end; it climbs inboard
dado_mouth_x = panel_half_w                    # the rail's inboard face
dado_blind_x = panel_half_w + dado_depth
# The fixed corbel's lower face at this run is `underside_z - dado_depth`; what remains below the
# groove and above it are the two ligaments that capture the rail at the blind end.
dado_lower_ligament = dado_floor_z - (underside_z - dado_depth)
lip_t = show_z - dado_roof_z


def dado():
    """The groove back-top cuts in each rail's inboard face, as
    `(mouth_x, blind_x, floor_z, roof_z, chamfer_deg)` on the +X side; the −X side is its
    mirror. The roof is struck at the blind end and rises at `chamfer_deg` to the mouth,
    where it runs out on the show face."""
    return (dado_mouth_x, dado_blind_x, dado_floor_z, dado_roof_z, _enc.relief_chamfer)


# --- the two screws that pin the fore end ------------------------------------
#
# THE SCREW ENTERS FROM Z− AND RUNS +Z. Its head belongs to the fixed back-top boss below the
# moving panel, and its heat-set belongs to a short socket grown down from the panel's broad
# field. This keeps the show face whole and makes the fastener answer to the part it retains:
# the screw pulls the panel's insert down onto back-top's boss.
screw_land = _enc.cap_web_land                  # fixed boss between head seat and panel socket
screw_reach = screw_land + _enc.heatset_depth   # land plus full insert engagement
screw_pad_r = _enc.head_cbore_dia / 2.0 + _enc.boss_ligament
# One wall caps the blind end under the show face. Below it are the insert and the standard
# relief past the screw tip; their sum sets the panel socket's downward-facing mouth.
screw_insert_bore_end_z = show_z - _enc.socket_cap
screw_insert_open_z = (screw_insert_bore_end_z
                       - _enc.heatset_depth - _enc.mount_bore_relief)
screw_insert_end_z = screw_insert_open_z + _enc.heatset_depth
# The fixed boss presents one `screw_land` between that mouth and the head's bearing face, then
# the standard counterbore opens downward to a flush head face.
screw_head_seat_z = screw_insert_open_z - screw_land
screw_head_face_z = screw_head_seat_z - _enc.head_cbore_depth
screw_tip_z = screw_head_seat_z + _enc.screw_len
screw_tip_air = screw_insert_bore_end_z - screw_tip_z
screw_socket_t = show_z - screw_insert_open_z
# THE SOCKET HANGS ONLY 1.25 MM BELOW THE BROAD FIELD and travels in the boss lane back-top cuts.
# The station stands as far outboard as a full ligament around it allows, tangent to the mouth.
screw_x = panel_half_w - screw_pad_r
# Centred in the brim's landing, where the fore edge has the full structural section it needs.
screw_y = fore_y + brim_seat / 2.0


def screw_stations():
    """The two retention screws as `((x, y), ...)` in the box's frame — the axes the panel's
    insert sockets and back-top's upward screw bosses are both struck on."""
    return ((-screw_x, screw_y), (screw_x, screw_y))


# --- primitives -------------------------------------------------------------

def _slab(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _post(r, cx, cy, z0, z1):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(cx, cy, z0), cq.Vector(0, 0, 1))


def structural_stock():
    """The ceiling's unrelieved 8 mm load field, inside the 3 mm show skin."""
    return _slab(-panel_half_w, panel_half_w, fore_y, aft_y,
                 structural_under_z, underside_z)


def rail_stock(y0=fore_y, y1=aft_y):
    """Both exact wall-square rails over one Y band, without their printed-fit clearance."""
    rails = None
    for sx in (-1.0, 1.0):
        edge = sx * panel_half_w
        rail = _slab(min(edge, edge + sx * tongue_reach),
                     max(edge, edge + sx * tongue_reach),
                     y0, y1, tongue_floor_z, tongue_roof_z)
        rails = rail if rails is None else rails.fuse(rail)
    return rails


def rail_clearance(y0=fore_y, y1=aft_y):
    """The rectangular clearance both moving rails require through late fixed features.

    The dado's self-supporting roof already opens farther than this toward its mouth. This is
    the blind-end section alone, carried through a screw pier or tunnel fused after the dado was
    cut so that no late feature fills the slide back in."""
    lanes = None
    for sx in (-1.0, 1.0):
        inboard = sx * (panel_half_w - dado_slip)
        outboard = sx * (panel_half_w + dado_depth)
        lane = _slab(min(inboard, outboard), max(inboard, outboard),
                     y0, y1, dado_floor_z, dado_roof_z)
        lanes = lane if lanes is None else lanes.fuse(lane)
    return lanes


def insertion_sweep():
    """The structural field and both rails swept continuously through back-top's Y seam."""
    first_y = fore_y - (aft_y - _enc.y_seam)
    sweep = _slab(-panel_half_w, panel_half_w, first_y, aft_y,
                  structural_under_z, underside_z)
    return sweep.fuse(rail_stock(first_y, aft_y))


def _rounded_slab(x0, x1, y0, y1, z0, z1, radius=relief_corner_r):
    solid = _slab(x0, x1, y0, y1, z0, z1)
    radius = min(radius, (x1 - x0) / 3.0, (y1 - y0) / 3.0)
    if radius <= 0.1:
        return solid
    return cq.Workplane(obj=solid).edges("|Z").fillet(radius).val()


def _strap_reliefs(box):
    """Full anchor footprints whose existing strap approach enters the deeper field."""
    _saddles, ribs = _enc.ceiling_stations(
        box.digiten_saddles, box.tube_anchors, panel=True)
    raw = structural_stock()
    pockets = []
    for mid, u, n, seat_r in ribs:
        origin = tuple(mid[k] - u[k] * _enc.tube_anchor_len / 2.0 for k in range(3))
        crown = seat_r + _enc.wall
        strap_origin = tuple(origin[k] + u[k] * _enc.tie_cav_wall for k in range(3))
        strap = _enc._anchor_rib(strap_origin, u, n, _enc.tie_cav_w,
                                  crown, crown, crown + _enc.tie_strap_t)
        if raw.intersect(strap).Volume() <= 1e-6:
            continue
        if tuple(n) != (0, 0, 1):
            raise ValueError(
                f"a ceiling strap relief names root {n}; only a +Z root can be cut out of "
                f"the panel's downward-open structural field")
        b_face = underside_z - mid[2]
        pockets.append(_enc._anchor_rib(
            origin, u, n, _enc.tube_anchor_len,
            crown + _enc.tie_strap_t + _enc.tie_cav_buffer, 0.0, b_face))
    return tuple(pockets)


def _relieved_stock(box):
    """The broad field and rails after body headroom and strap approaches are opened below."""
    stock = structural_stock().fuse(rail_stock())
    for _name, x0, x1, y0, y1, pocket_top_z in box.ceiling_reliefs:
        top = min(underside_z, pocket_top_z)
        if top <= structural_under_z:
            continue
        stock = stock.cut(_rounded_slab(
            x0, x1, y0, y1, structural_under_z - 0.1, top))
    for pocket in _strap_reliefs(box):
        stock = stock.cut(pocket)
    return stock


# --- the panel --------------------------------------------------------------

def build(box=None):
    """The panel as one solid: show skin, relieved structural field, tongues and furniture.

    THE 8 MM FIELD IS THE STRUCTURE. Its downward-open pockets are struck from the purchased
    bodies' intersections with the unrelieved stock, so the broad remainder carries load in two
    dimensions while the screw stations and most furniture roots disappear into it. A box-less
    build keeps the stock whole; the machine build hands in the exact relief stations.

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
    stock = (_relieved_stock(box) if box is not None
             else structural_stock().fuse(rail_stock()))
    field = field.fuse(stock)
    # The insert sockets, clipped to the panel's plan — each one's fore face is the panel's
    # fore edge, which is the plane the brim bears on. Their mouths face Z−.
    plan = _slab(-panel_half_w - tongue_reach, panel_half_w + tongue_reach,
                 fore_y, aft_y, screw_insert_open_z - 1.0, show_z)
    for cx, cy in screw_stations():
        field = field.fuse(_post(
            screw_pad_r, cx, cy, screw_insert_open_z, show_z).intersect(plan))
    solid = cq.Workplane(obj=field)
    # The ruthex bore opens from the underside, through its full insertion depth and one
    # `mount_bore_relief` past it. A whole `socket_cap` of show-face material remains blind.
    for cx, cy in screw_stations():
        solid = solid.cut(cq.Workplane(obj=_post(
            _enc.heatset_dia / 2.0, cx, cy,
            screw_insert_open_z - 1.0, screw_insert_bore_end_z)))
    if box is None:
        return solid
    # The C14 tunnel's crown occupies this field at the installed pose and therefore travels
    # with it. Back-top keeps the rest of the same feature; the union is unchanged when closed.
    c14_cap = _enc.c14_ceiling_cap(
        box.inner, box.outer, box.c14, box.back_ports, structural_stock())
    if c14_cap is not None and c14_cap.Volume() > 1e-6:
        solid = solid.union(c14_cap)
    saddles, ribs = _enc.ceiling_stations(box.digiten_saddles, box.tube_anchors, panel=True)
    # THE CEILING THESE ROOT ON IS THIS PANEL'S UNDERSIDE. A rib's two ends climb to the face it
    # stops on and the strap's channel is the room they leave between them, so what the builders
    # are handed is the plane this part puts there — `enclosure.piece_root_faces` is the same
    # substitution for a wall, on the pieces that carry one thicker than the box's own.
    roots = box.inner[:5] + (underside_z,)
    body = solid.val()
    body = _enc._digiten_saddles(body, roots, saddles,
                                 fore_y, aft_y, box.inner[4], show_z)
    body = _enc._tube_anchors(body, roots, box.inner, ribs,
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
            f"slide-in lid is one body, and a second one is a tongue or socket that missed "
            f"the field it was fused to")
    if screw_reach > _enc.screw_len + 1e-9:
        raise ValueError(
            f"the retention screw has to cross {screw_land:g} mm of land and land "
            f"{_enc.heatset_depth:g} mm in its insert — {screw_reach:.2f} mm under the head, "
            f"and the box's own screw is {_enc.screw_len:g}. Thin the land or lengthen it")
    if screw_tip_air < -1e-9:
        raise ValueError(
            f"the Z−-inserted M3x{_enc.screw_len:g} tip reaches z {screw_tip_z:.2f}, past "
            f"the socket bore's blind end at z {screw_insert_bore_end_z:.2f} by "
            f"{-screw_tip_air:.2f} mm. Deepen the relief or shorten the screw")
    if abs(show_z - screw_insert_bore_end_z - _enc.socket_cap) > 1e-9:
        raise ValueError(
            f"the panel's upward insert bore leaves {show_z - screw_insert_bore_end_z:.2f} "
            f"mm under the show face, not the box's {_enc.socket_cap:g} mm socket cap")
    if not (screw_head_face_z < screw_head_seat_z < screw_insert_open_z
            < screw_insert_end_z < screw_insert_bore_end_z < show_z):
        raise ValueError(
            "the ceiling screw stack is not ordered from its Z− head through the fixed land "
            "and upward panel insert to the blind show-face cap")
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
    export_assembly(one_body(panel, "ceiling-panel", M_PETG_BLACK), str(out))
    print(f"-> {out.name}")
    print(f"  field:   {panel_w:.1f} x {depth:.1f} x {structural_t:.1f} mm structural, "
          f"x +-{panel_half_w:g}, y {fore_y:g}..{aft_y:g}, "
          f"z {structural_under_z:g}..{show_z:g}")
    print(f"  bbox:    {b.xlen:.1f} x {b.ylen:.1f} x {b.zlen:.1f} mm "
          f"(tongues out to +-{panel_half_w + tongue_reach:g}, field to {structural_under_z:g}, "
          f"insert sockets to {screw_insert_open_z:g}, ribs to {b.zmin:g})")
    print(f"  tongue:  {tongue_t:.2f} thick x {tongue_reach:.2f} reach "
          f"({tongue_t * tongue_reach:.2f} mm2), z {tongue_floor_z:g}..{tongue_roof_z:g}, "
          f"{dado_slip:g} slip per face")
    print(f"  dado:    x {dado_mouth_x:g}..{dado_blind_x:g}, z {dado_floor_z:g}..{dado_roof_z:g}, "
          f"roof at {_enc.relief_chamfer:g} deg to the mouth; "
          f"ligaments {dado_lower_ligament:.2f} below / {lip_t:.2f} above at the blind end")
    print(f"  rails:   {rail_run:g} mm side strip each side, "
          f"back-top flank face at +-{_enc.back_top_flank_face()[1]:g}")
    print(f"  screws:  M3x{_enc.screw_len:g} at x +-{screw_x:.3f}, y {screw_y:g} — "
          f"inserted from Z-, head face {screw_head_face_z:g}, seat {screw_head_seat_z:g}, "
          f"panel insert {screw_insert_open_z:g}..{screw_insert_end_z:g}; "
          f"{screw_reach:.2f} of {_enc.screw_len:g} spent, {screw_tip_air:.2f} tip air")
    print(f"  brim:    lands y {fore_y:g}..{fore_y + brim_seat:g} on the show face")
    saddles, ribs = _enc.ceiling_stations(box.digiten_saddles, box.tube_anchors, panel=True)
    print(f"  carries: {0 if saddles is None else len(saddles[3])} meter saddle(s), "
          f"{len(ribs)} ceiling rib(s) — "
          + ", ".join(f"({m[0]:.2f}, {m[1]:.2f}) r{r:g}" for m, _u, _n, r in ribs))
    print(f"  reliefs: {len(box.ceiling_reliefs)} body pocket(s), "
          f"{len(_strap_reliefs(box))} full strap approach pocket(s), rounded r{relief_corner_r:g}")
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
            "RELIEF_N": f"{len(box.ceiling_reliefs)}",
            "STRAP_RELIEF_N": f"{len(_strap_reliefs(box))}",
            "PIECE_H": f"{piece_h:g} mm",
            "PANEL_FORE": f"{fore_y:g}",
            "PANEL_AFT": f"{aft_y:g}",
            "PANEL_UNDER": f"{underside_z:g}",
            "PANEL_SHOW": f"{show_z:g}",
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
            "SCREW_X": f"{screw_x:g}",
            "SCREW_Y": f"{screw_y:g}",
            "SCREW_LAND": f"{screw_land:g} mm",
            "SCREW_REACH": f"{screw_reach:g} mm",
            "SCREW_SOCKET_T": f"{screw_socket_t:g} mm",
            "SCREW_INSERT_OPEN": f"{screw_insert_open_z:g}",
            "SCREW_INSERT_END": f"{screw_insert_end_z:g}",
            "SCREW_INSERT_BORE_END": f"{screw_insert_bore_end_z:g}",
            "SCREW_HEAD_SEAT": f"{screw_head_seat_z:g}",
            "SCREW_HEAD_FACE": f"{screw_head_face_z:g}",
            "SCREW_TIP_AIR": f"{screw_tip_air:g} mm",
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
