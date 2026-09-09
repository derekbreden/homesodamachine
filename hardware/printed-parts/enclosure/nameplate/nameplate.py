"""Nameplate — the plate the machine is named and rated on.

A flat plate lying in a pocket of the +Y wall of back-top's outer face, flush with it, in
the field east of the flavour chips. Two M3 cap screws hold it; their heads land in
counterbores sunk into the plate itself, so the face a customer meets is one plane of plate,
head and wall.

    THICK     a screw seat's own section — the head's height and the land under it. The plate
              carries it EVERYWHERE, so nothing stands off its back
    WALL      what the wall thickens to behind it, to floor a pocket one THICK deep

IT PRINTS LETTERING UP, and that is what sets the section. The type is 0.2 mm work and wants to
be laid last, on the face looking at the nozzle — which puts the plate's INBOARD face on the bed.
A screw seat deeper than the plate would stand off that face as a pad, and a plate resting on two
pads is a plate bridging its whole area. So the seat's depth goes INTO the plate: one thickness
throughout, every feature sunk into the face that looks up, and the bed takes a solid plane.
`enclosure._nameplate` thickens the wall to take the pocket that costs.

WHERE IT STANDS. `WIDTH` and `HEIGHT` are the plate's, and the field it drops into is the
wall's: `enclosure_assembly.nameplate_station` strikes that field on the flavour chips' own edge
west, the flat rear face's tangent east, the top row's chips north and the back column's Z seam
south, and `nameplate-field` reads these two figures back against it. The plate's horizontal
centreline is the SCREW LINE — the lowest band where the two complete corbelled supports clear
the cold core's cap, with the SeaFlo's rounded aft disc and the PSU still clear at their own
ends — so its two screws stand at mid-height.

THE TYPE IS A SECOND SOLID, as the chips' words are: it lies in a recess `INK_DEPTH` into the
plate's outboard face and fills it flush, printed in the second filament.

Coordinate frame — the wall's, as `bulkhead_ring` states it, so the assembly seats one with no
turn of its own:
  Y = out through the wall. +Y = outboard, toward the customer.
  Origin = the plate's INBOARD face at its own centre. The plate spans y = 0 to y = THICK and
      nothing reaches below y = 0 — that plane is the bed.
  +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
      +X runs to the LEFT, a line of type reads along −X, and a row starts at large x.

Its BACK EDGE IS CHAMFERED `BEVEL` at 45°, so the face on the bed is inset all round and
the outline grows out to full size over the first three millimetres.

It prints flat, two colours to a plate.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py 27
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "y-wall-of-back-top",
           _hw / "printed-parts" / "enclosure" / "enclosure",
           _hw / "printed-parts" / "enclosure" / "bulkhead-ring"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
import fits                                           # noqa: E402
from _cadq_export import export_assembly              # noqa: E402
from _materials import step_safe                      # noqa: E402
from docgen import substitute_md                      # noqa: E402
import _y_wall_dimensions as _rear                    # noqa: E402
import _nameplate_dimensions as _plan                 # noqa: E402
import _enclosure_interface as _enc                   # noqa: E402
import bulkhead_ring as _ring                         # noqa: E402


# --- the two screws --------------------------------------------------------
#
# The head lands inside the plate and the wall's plane closes over it — a counterbore sunk to
# the head's own height, with a land under it. THE PLATE CARRIES THAT SECTION EVERYWHERE rather
# than thickening at each screw, so no pad stands off its back. What pays for it is the wall,
# which thickens to floor a pocket that deep and is bored past it for the insert.
LAND = 1.5
HEAD_H = _enc.display_cover_head_h
CBORE_DIA = _enc.head_cbore_dia
SHANK_DIA = _enc.screw_clear_dia
CBORE_DEPTH = HEAD_H
# The plate's own section round a counterbore: one `enclosure.boss_ligament`, what this machine
# gives every M3 seat.
SEAT_DIA = CBORE_DIA + 2.0 * _enc.boss_ligament
# How far a screw station stands in from the plate's edge: half a seat and one plate wall past it.
SCREW_INSET = SEAT_DIA / 2.0 + 2.5
# DIN 912 states a length under the head.
SCREW_LEN = 8.0


# --- the plate -------------------------------------------------------------

# THE PLATE IS ONE SCREW SEAT THICK, everywhere — the head's own height and the land under it.
# `bulkhead_ring.THICK` is what the rest of this face inlays at, and this plate is deeper than that,
# because what it has to bury is a screw and not a colour.
THICK = CBORE_DEPTH + LAND
# What the wall stands to behind it: its own stock, and the band the pack already stands off it.
# `enclosure.rear_seam_clear` is that band — the plane the rear Z seam's lip presents the core —
# so the thickening reaches a plane the box was holding open anyway and takes nothing from the
# pack. `floor_under` is what the wall keeps below the pocket.
WALL = _enc.wall + _enc.rear_seam_clear
# The slip the plate takes all round in its pocket.
SLIP = fits.slip
# The plate's corner round, and its pocket's.
CORNER_R = 3.0
# THE BACK EDGE IS CHAMFERED, 45° and `BEVEL` in the thickness. That face is the one on the bed,
# so the chamfer is the first thing laid and the outline grows out to full size over three
# layers of 45° — no elephant's foot on the rim the customer can see, and no arris to catch the
# pocket's own inside corner on the way in. It is `CORNER_R`, which is what takes the corner
# rounds to nothing on the bed and the outline there to a plain rectangle.
#
# THE POCKET ANSWERS IT, so this figure is the wall's as much as the plate's: `enclosure.
# _nameplate` cuts the pocket to this whole silhouette, and what that buys the WALL is its
# ceiling. 45° is `enclosure.relief_chamfer`, the angle every relief ceiling on this box rises at
# — struck square here, which is that angle, and `selftest` holds the two together.
BEVEL = CORNER_R
# The plate's envelope in the field east of the flavour chips. `enclosure_assembly.check_nameplate`
# reads it against the wall; `selftest` reads the lettering and screw seats within it.
WIDTH = 104.53
HEIGHT = 66.07


def bore_relief() -> float:
    """Air past the screw tip at the bore's blind end: `enclosure.mount_bore_relief`, or what an
    M3x`SCREW_LEN` asks for past the insert, whichever is the more."""
    return max(_enc.mount_bore_relief, SCREW_LEN - LAND - _enc.heatset_depth)


def screw_reach() -> float:
    """What stands under a screw head: the plate's land, then the bore the wall cuts past it —
    the insert's depth and the relief under it."""
    return LAND + _enc.heatset_depth + bore_relief()


def thread_engaged() -> float:
    """How much of the insert the screw takes.

    Against the INSERT's own body and not the pocket's depth: the bore is one relief deeper
    than the brass in it, and a screw that crosses the relief has taken no more thread for it.
    The long ruthex goes in here — the bore this station already cuts is deeper than that body,
    so the plate's two screws take the whole of it."""
    return min(SCREW_LEN - LAND, _enc.heatset_long_len)


def floor_under() -> float:
    """The stock the wall keeps under the plate, once a pocket one THICK deep is cut into a wall
    `WALL` thick."""
    return WALL - THICK


def boss_reach() -> float:
    """How far a screw boss stands off the THICKENED wall's inner face: everything under the
    pocket floor, less the floor the pocket left standing.

    It is the one thing here that reaches into the pack, and the plateau is why it is short: the
    wall now carries `floor_under` of what the bore needs, so the boss stands for the rest."""
    return THICK + _enc.heatset_depth + bore_relief() - WALL


def pocket_flat() -> float:
    """The pocket's ceiling ACROSS, between its own corner rounds. The slip cancels — it widens
    the pocket and its corners equally — so this is the plate's width less two corner radii."""
    return WIDTH - 2.0 * CORNER_R


def pocket_soffit(hang: float) -> float:
    """How much FLAT ceiling the pocket hangs off its head, for a pocket hanging `hang` deep.

    The wall this pocket is cut into prints vertical, so its head is a down-facing face starting
    in air. Cut square a pocket hangs its whole `THICK`; cut to the plate's chamfer it hangs
    `THICK - BEVEL`, and the rest of the head is a 45° ramp the wall reaches under."""
    return pocket_flat() * hang


def boss_stem_d() -> float:
    """And the boss under that pocket, one enclosure-standard M3 heat-set section wide.

    Its upper half is round; the enclosure squares the lower half to the two tangents and carries
    that whole face on a wall-wide corbel. It keeps the standard `boss_ligament` around the insert
    and fits with its corbel in the cap-to-pump lane."""
    return _enc.mount_boss_dia


def screw_stations() -> tuple:
    """The two screw stations in the plate's own frame: on its horizontal centreline, one
    `SCREW_INSET` in from each end. That centreline is the wall's own screw line, which is what
    `enclosure_assembly.nameplate_station` stands the plate on."""
    return ((WIDTH / 2.0 - SCREW_INSET, 0.0), (-(WIDTH / 2.0 - SCREW_INSET), 0.0))


def seat() -> tuple:
    """The face the pocket takes the plate by: `(position, outward axis)` on its INBOARD face,
    pointing at the wall."""
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


# --- the type --------------------------------------------------------------
#
# One face, `bulkhead_ring.WORD_FONT` — what the rings beside this plate are lettered in and
# what the customer's sheet is set in. The footer's stroke and letter spacing are measured
# on its own letterforms against the 0.2 mm profile's bead.
FONT = _ring.WORD_FONT
FONT_KIND = _ring.WORD_KIND
TITLE_EM = 11.2
LINK_EM = 5.5
BODY_EM = 2.8
DETAIL_TRACKING = 0.1
# The type's recess depth; its outboard face is flush with the plate.
INK_DEPTH = _ring.WORD_DEPTH
# The bead the 0.2 mm tip lays, and the tip itself.
BEAD = _ring.WORD_BEAD
NOZZLE = _ring.WORD_NOZZLE
# The brand's top margin, air between its three lines, and the link and details below, in mm.
BRAND_MARGIN = 4.5
TITLE_GAP = 1.4
LINK_MID = -6.4
DETAIL_TOP = -13.4
DETAIL_GAP = 1.2
# The glass mark standing beside the name, the air between them, and its stroke.
LOGO_H = 28.0
LOGO_STROKE = 1.2
LOGO_GAP = 5.5
# The flame hangs beside the detail column at the shared cap height.
FLAME_GAP = 1.2


def _flat(s: str, em: float):
    """One line set flat in XY, extruded `INK_DEPTH`, its own metrics centred on the origin."""
    return cq.Workplane("XY").text(s, em, INK_DEPTH, font=FONT, kind=FONT_KIND,
                                   halign="center", valign="center").val()


def text_width(s: str, em: float) -> float:
    """How wide a line comes out, off the built letterforms."""
    return _flat(s, em).BoundingBox().xlen


def cap_height(em: float) -> float:
    """And how tall a cap stands at that em."""
    return _flat("HOME", em).BoundingBox().ylen


def lockup_width() -> float:
    """The brand lockup across: the glass mark, the air beside it, and the name."""
    return logo_width() + LOGO_GAP + max(text_width(s, TITLE_EM) for s in lines(1)["name"])


def link_em() -> float:
    """The unit link's em, fixed across the four-digit serial range."""
    return LINK_EM


def _upright(shape):
    """A flat XY solid carried onto the wall's plane: a quarter about X stands it up, a half
    about Z turns it to face the customer — extruding outboard, cap up, advance along −X."""
    return (shape.rotate((0, 0, 0), (1, 0, 0), 90.0)
                 .rotate((0, 0, 0), (0, 0, 1), 180.0))


def _place(shape, x_start: float, z_mid: float):
    """One upright solid put where a row starts: its READING-LEFT edge on `x_start`, its own
    extent centred on `z_mid`, its outboard face flush with the plate's."""
    bb = shape.BoundingBox()
    return shape.translate(cq.Vector(x_start - bb.xmax,
                                     THICK - INK_DEPTH - bb.ymin,
                                     z_mid - (bb.zmin + bb.zmax) / 2.0))


def line(s: str, em: float, x_start: float, z_mid: float):
    """One line of type standing in the plate's face."""
    return _place(_upright(_flat(s, em)), x_start, z_mid)


# --- the brand mark --------------------------------------------------------
#
# The soda glass the main board silkscreens (`/hardware/pcb/pcba/logo.ts`) and the app icon draws
# (`/ios/AppIcon.svg`), as stroked outline: the glass, the liquid's surface, and four bubbles.
# Coordinates are the icon's own 1024 viewBox, Y down.
_GLASS_SVG_H = 530.0
_SVG_C = 512.0
_GLASS = [(310, 247), (340, 747)]
_WAVE = [(300, 347), (400, 327), (512, 352), (624, 377), (724, 342)]
_BUBBLES = ((440, 740, 42), (572, 610, 36), (500, 489, 33), (628, 408, 29))


def _qbez(p0, c, p1, n=10):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1.0 - t
        out.append((u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0],
                    u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1]))
    return out


def _glass_outline():
    g = list(_GLASS)
    g += _qbez((340, 747), (345, 777), (380, 777))
    g += [(644, 777)]
    g += _qbez((644, 777), (679, 777), (684, 747))
    g += [(714, 247)]
    return g


def _wave_points():
    w = [_WAVE[0]]
    w += _qbez(_WAVE[0], _WAVE[1], _WAVE[2])
    w += _qbez(_WAVE[2], _WAVE[3], _WAVE[4])
    return w


def _icon_xy(p, scale):
    """One icon point in the plate's flat XY frame, centred on the mark's own centre."""
    return ((p[0] - _SVG_C) * scale, -(p[1] - _SVG_C) * scale)


def build_logo(height: float = LOGO_H, stroke: float = LOGO_STROKE):
    """The mark as a flat XY solid `INK_DEPTH` thick: the glass's outline, and inside it the
    liquid's surface and four bubbles, each clipped to the glass the way the icon clips them."""
    s = height / _GLASS_SVG_H
    half = stroke / 2.0
    outline = [_icon_xy(p, s) for p in _glass_outline()]

    def loop(points):
        return cq.Workplane("XY").polyline(points + points[:1]).wire()

    glass = (loop(outline).offset2D(half, "arc").extrude(INK_DEPTH).val()
             .cut(loop(outline).offset2D(-half, "arc").extrude(INK_DEPTH).val()))
    inside = loop(outline).offset2D(-half, "arc").extrude(INK_DEPTH).val()

    wave = (cq.Workplane("XY").polyline([_icon_xy(p, s) for p in _wave_points()])
            .offset2D(half, "arc").extrude(INK_DEPTH).val())
    mark = glass.fuse(wave.intersect(inside))
    for bx, by, br in _BUBBLES:
        cx, cy = _icon_xy((bx, by), s)
        r = br * s
        ring = (cq.Workplane("XY").center(cx, cy)
                .circle(r).circle(max(r - stroke, 0.25)).extrude(INK_DEPTH).val())
        mark = mark.fuse(ring.intersect(inside))
    return mark


def logo_width(height: float = LOGO_H, stroke: float = LOGO_STROKE) -> float:
    return build_logo(height, stroke).BoundingBox().xlen


# --- the flame -------------------------------------------------------------
#
# A flame silhouette, drawn in the icon frame `_icon_xy` reads — the same
# 1024 viewBox, Y down, that the glass is drawn in. The mark is filled where the glass is stroked,
# so it takes a closed polyline rather than an `offset2D` outline.
_FLAME_SVG_H = 800.0


def _flame_outline():
    p = [(500, 112)]
    p += _qbez((500, 112), (640, 300), (632, 430))
    p += _qbez((632, 430), (628, 520), (690, 556))
    p += _qbez((690, 556), (742, 470), (734, 392))
    p += _qbez((734, 392), (830, 520), (826, 660))
    p += _qbez((826, 660), (820, 830), (512, 912))
    p += _qbez((512, 912), (204, 830), (198, 660))
    p += _qbez((198, 660), (194, 520), (268, 420))
    p += _qbez((268, 420), (300, 540), (356, 556))
    p += _qbez((356, 556), (398, 470), (372, 352))
    p += _qbez((372, 352), (400, 200), (500, 112))
    return p


def build_flame(height: float | None = None):
    """The flame as a flat XY solid `INK_DEPTH` thick, filled."""
    if height is None:
        height = cap_height(BODY_EM)
    s = height / _FLAME_SVG_H
    pts = [_icon_xy(q, s) for q in _flame_outline()]
    return cq.Workplane("XY").polyline(pts).close().extrude(INK_DEPTH).val()


def flame_width(height: float | None = None) -> float:
    return build_flame(height).BoundingBox().xlen


def tracked_text(s: str, em: float, tracking: float):
    """A detail line with extra space between consecutive letterforms."""
    letters = sorted(_flat(s, em).Solids(),
                     key=lambda s: s.BoundingBox().xmin)
    return cq.Compound.makeCompound([
        letter.translate(cq.Vector(i * tracking, 0, 0))
        for i, letter in enumerate(letters)
    ])


def detail_rows(unit: int):
    """Serial, ratings and refrigerant notice in one small type size, in reading order."""
    text = lines(unit)
    return [
        (s, tracked_text(s, BODY_EM, DETAIL_TRACKING))
        for s in text["serial"] + text["input"] + text["warn"] + text["hazard"]
    ]


# --- the layout ------------------------------------------------------------

def build_ink(unit: int):
    """Large brand above the unit link; serial, ratings and refrigerant notice below it."""
    text = lines(unit)
    logo = _upright(build_logo())
    lb = logo.BoundingBox()
    names = [_upright(_flat(s, TITLE_EM)) for s in text["name"]]
    name_h = sum(s.BoundingBox().zlen for s in names) + TITLE_GAP * (len(names) - 1)
    lock_h = max(lb.zlen, name_h)
    lock_left = lockup_width() / 2.0
    brand_mid = HEIGHT / 2.0 - BRAND_MARGIN - lock_h / 2.0
    column_left = lock_left - lb.xlen - LOGO_GAP
    parts = [_place(logo, lock_left, brand_mid)]
    z = brand_mid + name_h / 2.0
    for name in names:
        h = name.BoundingBox().zlen
        parts.append(_place(name, column_left, z - h / 2.0))
        z -= h + TITLE_GAP

    link = text["url"][0]
    parts.append(line(link, link_em(), text_width(link, link_em()) / 2.0, LINK_MID))

    z = DETAIL_TOP
    for s, flat in detail_rows(unit):
        upright = _upright(flat)
        h = upright.BoundingBox().zlen
        parts.append(_place(upright, column_left, z - h / 2.0))
        if s == text["hazard"][0]:
            flame = _upright(build_flame())
            parts.append(_place(flame, column_left + flame.BoundingBox().xlen + FLAME_GAP,
                                z - h / 2.0))
        z -= h + DETAIL_GAP
    return cq.Compound.makeCompound(parts)


def lines(unit: int) -> dict:
    """Every string one unit's plate carries, by the block it stands in."""
    return {
        "name": ("HOME", "SODA", "MACHINE"),
        "serial": (f"SERIAL  {_plan.serial_of(unit)}",),
        "input": (_plan.input_rating,),
        "warn": (_plan.warning_line, _plan.warning_line_2),
        "hazard": (_plan.hazard_line,),
        "url": (_plan.unit_url_plain(unit),),
    }


def _stack_height(unit: int) -> float:
    """How tall the complete lettering stands, off the built solids."""
    return build_ink(unit).BoundingBox().zlen


def build_plate(unit: int):
    """The plate: one slab of the outline, chamfered on the back edge, the two screw passages,
    and the type's recess.

    EVERY CUT OPENS ON THE OUTBOARD FACE and nothing is fused to the inboard one, so the plate
    goes on the bed as a plane and every feature is a hole the nozzle looks down into. The shank
    is the one passage that reaches through, and at Ø`SHANK_DIA` it is a hole, not a bridge. The
    chamfer is struck before the passages, on the clean prism."""
    body = (cq.Workplane("XY").workplane(offset=0.0)
            .rect(WIDTH, HEIGHT).extrude(THICK)
            .edges("|Z").fillet(CORNER_R)
            .faces("<Z").chamfer(BEVEL).val())
    # A quarter about −X carries the outline onto the wall's plane with its thickness running
    # OUTBOARD: the inboard face lands on y = 0, which is the face `seat` hands the pocket.
    body = body.rotate((0, 0, 0), (1, 0, 0), -90.0)
    for sx, sz in screw_stations():
        body = body.cut(cq.Solid.makeCylinder(
            SHANK_DIA / 2.0, THICK + 2.0, cq.Vector(sx, -1.0, sz), cq.Vector(0, 1, 0)))
        body = body.cut(cq.Solid.makeCylinder(
            CBORE_DIA / 2.0, CBORE_DEPTH + 1.0,
            cq.Vector(sx, THICK - CBORE_DEPTH, sz), cq.Vector(0, 1, 0)))
    return body.cut(build_ink(unit))


def _filament(rgb):
    return step_safe(cq.Color(*(c / 255.0 for c in rgb)))


def build_part(unit: int) -> cq.Assembly:
    """One unit's plate as it prints: the body, and everything lettered lying in its recess,
    each in the filament it comes off."""
    a = cq.Assembly()
    a.add(build_plate(unit), name=f"nameplate-{unit:03d}",
          color=_filament(_rear.chip_color("flavor")))
    a.add(build_ink(unit), name=f"nameplate-{unit:03d}-ink",
          color=_filament(_rear.word_color("flavor")))
    return a


def split(shape) -> tuple:
    """A unit's STEP back apart, as `(plate, ink)`. The plate is the one body that reaches the
    seating face; everything else lies in the recess, one `INK_DEPTH` off it."""
    solids = shape.Solids() if hasattr(shape, "Solids") else shape
    floor = [s for s in solids if s.BoundingBox().ymin < 1e-6]
    if len(floor) != 1 or len(solids) < 2:
        raise ValueError(
            f"a plate's STEP is the body and the type lying in it, and this one carries "
            f"{len(solids)} {'body' if len(solids) == 1 else 'bodies'}, {len(floor)} of them "
            f"reaching the seating face")
    return (floor[0], cq.Compound.makeCompound([s for s in solids if s is not floor[0]]))


def selftest() -> int:
    """The plate against its own field, its screws against the stack they close, and the finest
    type on it against the tip that lays it."""
    fails = []
    if THICK >= WALL:
        fails.append(f"a plate {THICK:g} thick lies in a wall {WALL:g} thick and leaves no floor "
                     f"under it")
    if WALL - _enc.wall > _enc.rear_seam_clear + 1e-9:
        fails.append(f"the wall thickens {WALL - _enc.wall:g} behind the plate and the band the "
                     f"pack stands off it is {_enc.rear_seam_clear:g} — the rest is in the pack")
    if INK_DEPTH >= THICK:
        fails.append(f"type {INK_DEPTH:g} deep is cut through a plate {THICK:g} thick")
    if abs(_enc.relief_chamfer - 45.0) > 1e-9:
        fails.append(f"the plate's back edge and its pocket's ceiling are struck square, which is "
                     f"45°, and this box rises its relief ceilings at "
                     f"{_enc.relief_chamfer:g}° — the two no longer name one angle")
    if BEVEL > CORNER_R + 1e-9:
        fails.append(f"a {BEVEL:g} chamfer on a {CORNER_R:g} corner round turns the corner "
                     f"inside out")
    if BEVEL >= THICK:
        fails.append(f"a {BEVEL:g} chamfer takes the whole of a plate {THICK:g} thick and "
                     f"leaves it no straight rim in its pocket")
    # A SCREW SEAT IS DEEPER THAN AN INLAY, and the pocket's head hangs in air either way. The
    # chamfer is what keeps the deeper pocket from hanging more of it than the shallow one did —
    # if it ever stops doing that, the section is being paid for by the wall's own printability.
    if pocket_soffit(THICK - BEVEL) > pocket_soffit(_ring.THICK) + 1e-9:
        fails.append(f"the pocket hangs {pocket_soffit(THICK - BEVEL):.1f} mm2 of flat ceiling "
                     f"and an inlay-deep one at {_ring.THICK:g} hangs "
                     f"{pocket_soffit(_ring.THICK):.1f}")
    if CBORE_DEPTH >= THICK:
        fails.append(f"a counterbore {CBORE_DEPTH:g} deep leaves no land in a plate "
                     f"{THICK:g} thick")
    if abs((THICK - CBORE_DEPTH) - LAND) > 1e-9:
        fails.append(f"the seat leaves {THICK - CBORE_DEPTH:g} under the head and "
                     f"`LAND` states {LAND:g}")
    if SCREW_LEN > screw_reach() + 1e-9:
        fails.append(f"an M3x{SCREW_LEN:g} runs {SCREW_LEN:g} under its head and the station "
                     f"gives it {screw_reach():.2f}")
    if thread_engaged() < _enc.heatset_depth - 1e-9:
        fails.append(f"the screw takes {thread_engaged():.2f} of a {_enc.heatset_depth:g} insert")
    boss_ligament = (boss_stem_d() - _enc.heatset_dia) / 2.0
    if boss_ligament < _enc.boss_ligament - 1e-9:
        fails.append(f"the boss keeps {boss_ligament:g} round its insert and the enclosure's "
                     f"standard M3 boss keeps {_enc.boss_ligament:g}")
    for sx, sz in screw_stations():
        if abs(sx) + SEAT_DIA / 2.0 > WIDTH / 2.0 - 1e-9:
            fails.append(f"a seat at x {sx:g} reaches past the plate's own edge")
        if abs(sx) + SHANK_DIA / 2.0 > WIDTH / 2.0 - BEVEL - 1e-9:
            fails.append(f"the shank at x {sx:g} breaks out of the chamfer and the plate has no "
                         f"face on the bed round it")
    for em in (TITLE_EM, BODY_EM, link_em()):
        got = _min_stroke(_flat("MACHINE", em))
        if got < BEAD:
            fails.append(f"type at em {em:g} carries a {got:.3f} mm stroke and the profile lays "
                         f"a {BEAD:g} bead")
    for s, flat in detail_rows(1):
        letters = sorted(flat.Solids(), key=lambda s: s.BoundingBox().xmin)
        bridge = min(a.distance(b) for a, b in zip(letters, letters[1:]))
        if bridge < BEAD:
            fails.append(f"'{s}' leaves a {bridge:.3f} mm bridge between letters "
                         f"and the profile lays a {BEAD:g} bead")
        if _min_stroke(flat) < BEAD:
            fails.append(f"'{s}' has a stroke narrower than the {BEAD:g} bead")
    # The link spans the plate below the screw line; the actual ink clears both seats below.
    room = WIDTH - 4.0
    for unit in (1, 9999):
        s = lines(unit)["url"][0]
        got = text_width(s, link_em())
        if got > room:
            fails.append(f"'{s}' sets {got:.2f} mm wide in a {room:.2f} mm field")
    tall = _stack_height(1)
    if tall > HEIGHT + 1e-9:
        fails.append(f"the stack stands {tall:.2f} mm tall on a plate {HEIGHT:g} high")
    ink = build_ink(1)
    bb = ink.BoundingBox()
    if max(abs(bb.xmin), abs(bb.xmax)) > WIDTH / 2.0 - 2.0:
        fails.append("the lettering reaches into the plate's 2 mm side margin")
    if max(abs(bb.zmin), abs(bb.zmax)) > HEIGHT / 2.0 - 2.0:
        fails.append("the lettering reaches into the plate's 2 mm top or bottom margin")
    for sx, sz in screw_stations():
        counterbore = cq.Solid.makeCylinder(
            CBORE_DIA / 2.0, THICK, cq.Vector(sx, 0, sz), cq.Vector(0, 1, 0))
        if ink.distance(counterbore) < _enc.boss_ligament:
            fails.append(f"the lettering reaches into the seat around the screw at x {sx:g}")
    # THE FACE ON THE BED IS ONE PLANE — the whole point of the section, and the one claim here
    # that is measured off the built solid rather than argued from the figures.
    faces, got, low = bed_face(1)
    want = bed_face_want()
    if low < -1e-6:
        fails.append(f"the plate reaches {-low:.3f} mm below its seating face, and that face is "
                     f"what goes on the bed")
    if faces != 1 or abs(got - want) > 1e-3:
        fails.append(f"the face on the bed is {faces} face(s) of {got:.2f} mm2 and the outline "
                     f"less its two shanks measures {want:.2f}")
    for f in fails:
        print(f"FAIL {f}")
    if not fails:
        print(f"ok  nameplate  {WIDTH:g} x {HEIGHT:g} x {THICK:g}, {LAND:g} of land under each "
              f"head, one plane of {got:.0f} mm2 on the bed, boss {boss_reach():.2f} off a wall "
              f"{WALL:g} thick")
    return 1 if fails else 0


def bed_face(unit: int = 1) -> tuple:
    """What the plate lays on the bed, off the BUILT solid: `(faces, area, lowest)`.

    Everything the plate carries is sunk into the face that looks up, so its inboard face is one
    plane — the outline chamfered back by `BEVEL`, less the two screw shanks — and nothing
    reaches below it. That is the whole claim of the section, and this is where it is measured
    rather than argued."""
    body = build_plate(unit)
    bed = [f for f in body.Faces()
           if abs(f.Center().y) < 1e-6 and abs(abs(f.normalAt().y) - 1.0) < 1e-6]
    return (len(bed), sum(f.Area() for f in bed), body.BoundingBox().ymin)


def bed_face_want() -> float:
    """And what that face measures if it is the chamfered outline less the two shanks and
    nothing else. At `BEVEL` = `CORNER_R` the corner rounds come to nothing there and the figure
    is a plain rectangle, but the term is carried so the reading follows either one."""
    return ((WIDTH - 2.0 * BEVEL) * (HEIGHT - 2.0 * BEVEL)
            - (4.0 - math.pi) * (CORNER_R - BEVEL) ** 2
            - 2.0 * math.pi * (SHANK_DIA / 2.0) ** 2)


def _min_stroke(solid) -> float:
    out = []
    for f in solid.Faces():
        if abs(f.Center().z - INK_DEPTH) > 1e-6:
            continue
        perimeter = sum(e.Length() for e in f.Edges())
        if perimeter > 0:
            out.append(2.0 * f.Area() / perimeter)
    return min(out) if out else 0.0


def step_path(unit: int) -> Path:
    return _here.parent / f"nameplate-{unit:03d}.step"


def main(unit: int):
    part = build_part(unit)
    out = step_path(unit)
    export_assembly(part, str(out))
    print(f"Nameplate — unit {unit:03d}")
    print(f"  {WIDTH:g} x {HEIGHT:g} x {THICK:g}, corners r{CORNER_R:g}")
    print(f"  screws at x ±{screw_stations()[0][0]:.3f} on the plate's centreline, "
          f"Ø{CBORE_DIA:g} counterbore {CBORE_DEPTH:g} deep, {LAND:g} of land")
    print(f"  wall {WALL:g} behind it, {floor_under():g} of floor, "
          f"boss {boss_reach():.2f} off it, Ø{boss_stem_d():g} stem")
    print(f"  back edge chamfered {BEVEL:g} at 45°, "
          f"{bed_face(unit)[1]:.0f} mm2 of it on the bed")
    print(f"  pocket hangs {pocket_soffit(THICK - BEVEL):.1f} mm2 of flat ceiling, "
          f"where square it would hang {pocket_soffit(THICK):.1f}")
    print(f"-> {out.name}")

    variables = {
        "PLATE_W": f"{WIDTH:g} mm",
        "PLATE_H": f"{HEIGHT:g} mm",
        "NAMEPLATE_T": f"{THICK:g} mm",
        "WALL_T": f"{_enc.wall:g} mm",
        "PLATE_CORNER": f"{CORNER_R:g} mm",
        "PLATE_BEVEL": f"{BEVEL:g} mm",
        "RING_T": f"{_ring.THICK:g} mm",
        "POCKET_RIM": f"{THICK - BEVEL:g} mm",
        "POCKET_SOFFIT": f"{pocket_soffit(THICK - BEVEL):.1f} mm\u00b2",
        "POCKET_SOFFIT_SQUARE": f"{pocket_soffit(THICK):.1f} mm\u00b2",
        "PLATE_SLIP": f"{SLIP:g} mm",
        "SCREW_INSET": f"{SCREW_INSET:g} mm",
        "CBORE_D": f"{CBORE_DIA:g} mm",
        "NAMEPLATE_CBORE_DEPTH": f"{CBORE_DEPTH:g} mm",
        "NAMEPLATE_SEAT_D": f"{SEAT_DIA:g} mm",
        "NAMEPLATE_WALL": f"{WALL:g} mm",
        "NAMEPLATE_FLOOR": f"{floor_under():g} mm",
        "NAMEPLATE_LAND": f"{LAND:g} mm",
        "NAMEPLATE_SCREW_LEN": f"{SCREW_LEN:g} mm",
        "NAMEPLATE_SCREW_REACH": f"{screw_reach():.4g} mm",
        "BORE_RELIEF": f"{bore_relief():.4g} mm",
        "THREAD_ENGAGED": f"{thread_engaged():.4g} mm",
        "BOSS_REACH": f"{boss_reach():.4g} mm",
        "BOSS_STEM_D": f"{boss_stem_d():g} mm",
        "TITLE_EM": f"{TITLE_EM:g}",
        "TITLE_CAP": f"{cap_height(TITLE_EM):.3g} mm",
        "BODY_EM": f"{BODY_EM:g}",
        "BODY_CAP": f"{cap_height(BODY_EM):.3g} mm",
        "DETAIL_TRACKING": f"{DETAIL_TRACKING:g} mm",
        "FLAME_H": f"{cap_height(BODY_EM):.3g} mm",
        "LINK_EM": f"{link_em():.3g}",
        "LINK_CAP": f"{cap_height(link_em()):.3g} mm",
        "LINK_W": f"{text_width(lines(unit)['url'][0], link_em()):.4g} mm",
        "LOCKUP_W": f"{lockup_width():.4g} mm",
        "INK_DEPTH": f"{INK_DEPTH:g} mm",
        "INK_FLOOR": f"{THICK - INK_DEPTH:g} mm",
        "BED_AREA": f"{bed_face(unit)[1]:.0f} mm\u00b2",
        "STACK_H": f"{_stack_height(unit):.4g} mm",
        "LOGO_H": f"{LOGO_H:g} mm",
    }
    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
