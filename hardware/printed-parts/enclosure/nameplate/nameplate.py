"""Rear-wall nameplate — the plate the machine is named and rated on.

A flat plate lying in a pocket of the back wall's outer face, flush with it, in the field east
of the flavour chips. Two M3 cap screws hold it; their heads land in counterbores sunk into the
plate's own local thickening, so the face a customer meets is one plane of plate, head and wall.

    THICK     the plate's thickness, the depth its pocket is cut to, and the height of the boss
              the wall stands behind each screw
    LAND      the plate's own section under a screw head. The plate thickens by `PAD_DEPTH`
              there and the wall is pocketed to take that pad

WHERE IT STANDS. `WIDTH` and `HEIGHT` are the plate's, and the field it drops into is the
wall's: `enclosure_assembly.nameplate_station` strikes that field on the flavour chips' own edge
west, the flat rear face's tangent east, the top row's chips north and the back column's Z seam
south, and `nameplate-field` reads these two figures back against it. The plate's horizontal
centreline is the SCREW LINE — the band where the cold core's cap crowns at z 253.4 and the
SeaFlo's aft disc comes down to z 266.4, both standing 3 mm off the wall, leaving room open
across the face — so its two screws stand at mid-height.

THE TYPE IS A SECOND SOLID, as the chips' words are: it lies in a recess `INK_DEPTH` into the
plate's outboard face and fills it flush, printed in the second filament.

Coordinate frame — the wall's, as `port_ring` states it, so the assembly seats one with no turn
of its own:
  Y = out through the wall. +Y = outboard, toward the customer.
  Origin = the plate's INBOARD face at its own centre. The plate spans y = 0 to y = THICK and
      each pad hangs below y = 0.
  +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
      +X runs to the LEFT, a line of type reads along −X, and a row starts at large x.

It prints flat, two colours to a plate.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py 27
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "back-panel",
           _hw / "printed-parts" / "enclosure" / "enclosure",
           _hw / "printed-parts" / "enclosure" / "port-ring"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly              # noqa: E402
from _materials import step_safe                      # noqa: E402
from docgen import substitute_md                      # noqa: E402
import _back_panel_dimensions as _rear                # noqa: E402
import _nameplate_dimensions as _plan                 # noqa: E402
import enclosure as _enc                              # noqa: E402
import port_ring as _ring                             # noqa: E402


# --- the plate -------------------------------------------------------------

# The plate's thickness and the depth of the pocket it lies in — `port_ring.THICK`, the depth of
# inlay the rest of this face carries.
THICK = _ring.THICK
# The slip the plate takes all round in its pocket.
SLIP = 0.2
# The plate's corner round, and its pocket's.
CORNER_R = 3.0
# The quiet band inside the plate's edge that nothing is set in.
MARGIN = 6.0
# The plate across and up. The width is the FIELD'S, less a margin at each end, so the plate runs
# the whole of what the wall leaves it. The height is the stack standing on it plus HALF the
# padding the width came out with — the plate is landscape and its quiet band is landscape with
# it. `enclosure_assembly.check_nameplate` reads both back against the wall; `selftest` reads
# them against the type.
WIDTH = 104.53
HEIGHT = 66.07


# --- the two screws --------------------------------------------------------
#
# The head lands inside the plate and the wall's plane closes over it — a counterbore sunk to
# the head's own height, standing in the local thickening the plate carries at each screw. The
# wall is pocketed to take that pad, and bored past it for the insert.
LAND = 1.5
HEAD_H = _enc.display_cover_head_h
CBORE_DIA = _enc.head_cbore_dia
SHANK_DIA = _enc.screw_clear_dia
PAD_DEPTH = HEAD_H + LAND - THICK
CBORE_DEPTH = HEAD_H
# The pad, and the slip it drops into its own pocket on. One `enclosure.boss_ligament` of plate
# stands round the counterbore, the section this machine gives every M3 seat.
PAD_DIA = CBORE_DIA + 2.0 * _enc.boss_ligament
PAD_SLIP = _enc.display_screw_pad_slip
# How far a screw station stands in from the plate's edge: half a pad and one plate wall past it.
SCREW_INSET = PAD_DIA / 2.0 + 2.5
# DIN 912 states a length under the head.
SCREW_LEN = 8.0


def bore_relief() -> float:
    """Air past the screw tip at the bore's blind end: `enclosure.mount_bore_relief`, or what an
    M3x`SCREW_LEN` asks for past the insert, whichever is the more."""
    return max(_enc.mount_bore_relief, SCREW_LEN - LAND - _enc.heatset_depth)


def screw_reach() -> float:
    """What stands under a screw head: the plate's land, then the bore the wall cuts past it —
    the insert's depth and the relief under it."""
    return LAND + _enc.heatset_depth + bore_relief()


def thread_engaged() -> float:
    """How much of the insert the screw takes."""
    return min(SCREW_LEN - LAND, _enc.heatset_depth)


def pad_floor_depth() -> float:
    """How far under the plate's OUTBOARD face a pad's pocket floor lies. The wall is pocketed
    to this, and what the boss reaches inboard is measured from it."""
    return THICK + PAD_DEPTH


def boss_reach() -> float:
    """How far inboard of the wall's inner face a screw boss stands: everything under the pocket
    floor, less the wall's own stock the pocket left standing."""
    return pad_floor_depth() + _enc.heatset_depth + bore_relief() - _enc.wall


def boss_collar_d() -> float:
    """The boss at its widest, round the pad's own pocket — one `enclosure.wall` of material,
    less the ligament the pad's plate already carries."""
    return PAD_DIA + 2.0 * PAD_SLIP + 2.0 * 2.5


def boss_stem_d() -> float:
    """And the boss under that pocket, round the insert alone — `enclosure.c14_boss_dia`, one
    wall about a ruthex M3 short."""
    return _enc.c14_boss_dia


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
# One face, `port_ring.WORD_FONT` — what the chips beside this plate are lettered in and what the
# customer's sheet is set in — at three sizes. `FINE_EM` is the smallest, and the bridge and the
# stroke it leaves are what `selftest` holds against the tip.
FONT = _ring.WORD_FONT
FONT_KIND = _ring.WORD_KIND
TITLE_EM = _ring.WORD_SIZE
BODY_EM = _ring.WORD_SIZE
# The link is the one register under the chips' em — 26 characters at `BODY_EM` set wider than
# the plate — and `link_em` is what it comes out at.
# How deep the type's recess is cut into the plate's face — `port_ring.WORD_DEPTH`, half the
# plate, so the colour behind the lettering is as thick as the lettering.
INK_DEPTH = _ring.WORD_DEPTH
# The bead the 0.2 mm tip lays, and the tip itself.
BEAD = _ring.WORD_BEAD
NOZZLE = _ring.WORD_NOZZLE
# Leading inside a block of lines, and the air between two blocks, both as multiples of the em.
# Every line is caps and there are no descenders to clear.
LEADING = 1.14
BLOCK_GAP = 0.62
# The glass mark standing beside the name, the air between them, and its stroke.
LOGO_H = 15.0
LOGO_STROKE = 0.9
LOGO_GAP = 5.0


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
    return logo_width() + LOGO_GAP + text_width(lines(1)["name"][0], TITLE_EM)


def link_em() -> float:
    """The em the link is set at: the one that brings it out exactly as wide as the lockup over
    it, so the plate is bracketed by two marks of one width.

    ONE FIGURE FOR THE WHOLE RUN. Every serial is four digits and this face sets figures on one
    advance, so the link measures the same on unit 1 as on unit 9999."""
    return BODY_EM * lockup_width() / text_width(lines(9999)["url"][0], BODY_EM)


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
# The soda glass the board silkscreens (`/hardware/pcb/pcba/logo.ts`) and the app icon draws
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
        return cq.Workplane("XY").polyline(points).close()

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


# --- the layout ------------------------------------------------------------

def build_ink(unit: int):
    """Everything the plate says, as one solid in the second filament — three things, each
    centred on the plate's axis: the brand lockup, the block of what it is, and the link."""
    text = lines(unit)
    block = text["serial"] + text["input"] + text["warn"]
    step = BODY_EM * LEADING
    gap = BODY_EM * BLOCK_GAP

    logo = _upright(build_logo())
    lb = logo.BoundingBox()
    name = _upright(_flat(text["name"][0], TITLE_EM))
    nb = name.BoundingBox()
    lock_w = lb.xlen + LOGO_GAP + nb.xlen
    lock_h = max(lb.zlen, nb.zlen)
    link = text["url"][0]
    link_h = cap_height(link_em())

    tall = lock_h + gap + len(block) * step + gap + link_h
    z = tall / 2.0

    parts = []
    lock_left = lock_w / 2.0
    parts.append(logo.translate(cq.Vector(lock_left - lb.xmax,
                                          THICK - INK_DEPTH - lb.ymin,
                                          z - lock_h / 2.0 - (lb.zmin + lb.zmax) / 2.0)))
    parts.append(name.translate(cq.Vector(lock_left - lb.xlen - LOGO_GAP - nb.xmax,
                                          THICK - INK_DEPTH - nb.ymin,
                                          z - lock_h / 2.0 - (nb.zmin + nb.zmax) / 2.0)))
    z -= lock_h + gap

    for s in block:
        parts.append(line(s, BODY_EM, text_width(s, BODY_EM) / 2.0, z - step / 2.0))
        z -= step
    z -= gap

    parts.append(line(link, link_em(), text_width(link, link_em()) / 2.0, z - link_h / 2.0))

    ink = parts[0]
    for p in parts[1:]:
        ink = ink.fuse(p)
    # THE STACK IS CENTRED ON WHAT IT INKS, not on the slots its lines stand in. A line's slot is
    # one `LEADING` and its cap is shorter, so the plate is squared up on the built solid.
    bb = ink.BoundingBox()
    return ink.translate(cq.Vector(0.0, 0.0, -(bb.zmin + bb.zmax) / 2.0))


def lines(unit: int) -> dict:
    """Every string one unit's plate carries, by the block it stands in."""
    return {
        "name": ("HOME SODA MACHINE",),
        "serial": (f"SERIAL  {_plan.serial_of(unit)}",),
        "input": (_plan.input_rating,),
        "warn": (_plan.warning_line, _plan.warning_line_2),
        "url": (_plan.unit_url_plain(unit),),
    }


def _stack_height(unit: int) -> float:
    """How tall the centred stack stands, off the built solids."""
    return build_ink(unit).BoundingBox().zlen


def build_plate(unit: int):
    """The plate: the outline, a pad under each screw, the screw passages through both, and the
    type's recess taken out of its face."""
    body = (cq.Workplane("XY").workplane(offset=0.0)
            .rect(WIDTH, HEIGHT).extrude(THICK)
            .edges("|Z").fillet(CORNER_R).val())
    # A quarter about −X carries the outline onto the wall's plane with its thickness running
    # OUTBOARD: the inboard face lands on y = 0, which is the face `seat` hands the pocket.
    body = body.rotate((0, 0, 0), (1, 0, 0), -90.0)
    for sx, sz in screw_stations():
        body = body.fuse(cq.Solid.makeCylinder(
            PAD_DIA / 2.0, PAD_DEPTH, cq.Vector(sx, -PAD_DEPTH, sz), cq.Vector(0, 1, 0)))
    for sx, sz in screw_stations():
        body = body.cut(cq.Solid.makeCylinder(
            SHANK_DIA / 2.0, THICK + PAD_DEPTH + 2.0,
            cq.Vector(sx, -PAD_DEPTH - 1.0, sz), cq.Vector(0, 1, 0)))
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
    seating face; everything else lies in the recess."""
    solids = shape.Solids() if hasattr(shape, "Solids") else shape
    floor = [s for s in solids if s.BoundingBox().ymin < -1e-6]
    if len(floor) != 1 or len(solids) < 2:
        raise ValueError(
            f"a plate's STEP is the body and the type lying in it, and this one carries "
            f"{len(solids)} {'body' if len(solids) == 1 else 'bodies'}, {len(floor)} of them "
            f"reaching the pads' own depth")
    return (floor[0], cq.Compound.makeCompound([s for s in solids if s is not floor[0]]))


def selftest() -> int:
    """The plate against its own field, its screws against the stack they close, and the finest
    type on it against the tip that lays it."""
    fails = []
    if THICK >= _enc.wall:
        fails.append(f"a plate {THICK:g} thick lies in a wall {_enc.wall:g} thick and leaves no "
                     f"floor under it")
    if INK_DEPTH >= THICK:
        fails.append(f"type {INK_DEPTH:g} deep is cut through a plate {THICK:g} thick")
    if CBORE_DEPTH >= THICK + PAD_DEPTH:
        fails.append(f"a counterbore {CBORE_DEPTH:g} deep leaves no land in a seat "
                     f"{THICK + PAD_DEPTH:g} thick")
    if abs((THICK + PAD_DEPTH - CBORE_DEPTH) - LAND) > 1e-9:
        fails.append(f"the seat leaves {THICK + PAD_DEPTH - CBORE_DEPTH:g} under the head and "
                     f"`LAND` states {LAND:g}")
    if SCREW_LEN > screw_reach() + 1e-9:
        fails.append(f"an M3x{SCREW_LEN:g} runs {SCREW_LEN:g} under its head and the station "
                     f"gives it {screw_reach():.2f}")
    if thread_engaged() < _enc.heatset_depth - 1e-9:
        fails.append(f"the screw takes {thread_engaged():.2f} of a {_enc.heatset_depth:g} insert")
    for sx, sz in screw_stations():
        if abs(sx) + PAD_DIA / 2.0 > WIDTH / 2.0 - 1e-9:
            fails.append(f"a pad at x {sx:g} reaches past the plate's own edge")
    for em in (TITLE_EM, BODY_EM, link_em()):
        got = _min_stroke(_flat("MACHINE", em))
        if got < BEAD:
            fails.append(f"type at em {em:g} carries a {got:.3f} mm stroke and the profile lays "
                         f"a {BEAD:g} bead")
    room = WIDTH - 2.0 * MARGIN
    for key, row in lines(1).items():
        for s in row:
            em = {"name": TITLE_EM, "url": link_em()}.get(key, BODY_EM)
            got = text_width(s, em)
            if got > room + 1e-9:
                fails.append(f"'{s}' sets {got:.2f} mm wide and the plate's margins leave "
                             f"{room:.2f}")
    tall = _stack_height(1)
    if tall > HEIGHT - 2.0 * MARGIN + 1e-9:
        fails.append(f"the stack stands {tall:.2f} mm tall and the plate's margins leave "
                     f"{HEIGHT - 2.0 * MARGIN:.2f}")
    for f in fails:
        print(f"FAIL {f}")
    if not fails:
        print(f"ok  nameplate  {WIDTH:g} x {HEIGHT:g} x {THICK:g}, "
              f"{LAND:g} of land under each head, boss {boss_reach():.2f} inboard")
    return 1 if fails else 0


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
    print(f"  boss {boss_reach():.2f} inboard, Ø{boss_collar_d():g} collar / "
          f"Ø{boss_stem_d():g} stem")
    print(f"-> {out.name}")

    variables = {
        "PLATE_W": f"{WIDTH:g} mm",
        "PLATE_H": f"{HEIGHT:g} mm",
        "NAMEPLATE_T": f"{THICK:g} mm",
        "PLATE_CORNER": f"{CORNER_R:g} mm",
        "PLATE_MARGIN": f"{MARGIN:g} mm",
        "PLATE_SLIP": f"{SLIP:g} mm",
        "SCREW_INSET": f"{SCREW_INSET:g} mm",
        "CBORE_D": f"{CBORE_DIA:g} mm",
        "NAMEPLATE_CBORE_DEPTH": f"{CBORE_DEPTH:g} mm",
        "NAMEPLATE_PAD_D": f"{PAD_DIA:g} mm",
        "NAMEPLATE_PAD_DEPTH": f"{PAD_DEPTH:g} mm",
        "NAMEPLATE_LAND": f"{LAND:g} mm",
        "NAMEPLATE_SCREW_LEN": f"{SCREW_LEN:g} mm",
        "NAMEPLATE_SCREW_REACH": f"{screw_reach():.4g} mm",
        "BORE_RELIEF": f"{bore_relief():.4g} mm",
        "THREAD_ENGAGED": f"{thread_engaged():.4g} mm",
        "BOSS_REACH": f"{boss_reach():.4g} mm",
        "BOSS_COLLAR_D": f"{boss_collar_d():g} mm",
        "BOSS_STEM_D": f"{boss_stem_d():g} mm",
        "TITLE_EM": f"{TITLE_EM:g}",
        "BODY_EM": f"{BODY_EM:g}",
        "LINK_EM": f"{link_em():.3g}",
        "LOCKUP_W": f"{lockup_width():.4g} mm",
        "INK_DEPTH": f"{INK_DEPTH:g} mm",
        "STACK_H": f"{_stack_height(unit):.4g} mm",
        "LOGO_H": f"{LOGO_H:g} mm",
    }
    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
