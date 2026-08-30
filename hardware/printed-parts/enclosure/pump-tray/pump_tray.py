"""A PUMP CLAMP COLLAR IS THE PUMP CASE WITH ITS CYLINDER CUT OFF.

One per Kamoer. `pump_case` draws a two-piece case for this pump; its base is a plate on the
head-to-boss plane, a 45° ramp off that plate, an octagonal bore wall standing in the ramp,
and a cylindrical tower over the bore that the motor can turns in. Cut the tower to one
`SHOULDER` over the boss and the remaining fitted surfaces are the collar source.

Both collar sources are fused into the small top clamp (`enclosure.build_pump_cap`). The
enclosure builder clears the omitted stamped bracket through its measured thickness, restores
one complete pressing plate above it, and joins the two collars with screw bridges. NO COLLAR
SHIPS AS A PART.

    ACROSS  the case's own footprint
    ALONG   the case's own footprint, cut back to the face it roots on
    DEEP    the bore's whole run on the boss, and one `SHOULDER` of tower over its crown

THE LOWER CRADLE IS THE LOAD PATH. Its lands bear under three sides of the stamped bracket.
The top clamp presses the bracket down and this collar locates the boss in plan and clock;
its octagonal bore takes the boss above the bracket and its shoulder surrounds the can.

This module states what the tray adds over the case and draws one in its own frame; `enclosure`
turns it onto a pump and fuses it. The frame is the pump's, as `kamoer_kphm400` draws it:
  Z = the pump's depth axis, out of the head toward the can. `z = 0` IS THE HEAD'S +Z FACE, which
      is `pump_case`'s own base plane, so the case drops in with no turn and only a shift.
  X = across the tray. Y = along it, and `root` is the way it runs to the wall.
  Origin is the pump's own axis on that face.

Printed as part of the shallow clamp, the ramp, bore wall and shoulder grow off the pressing
plate's own section.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "reference" / "kamoer-kphm400",
           _here.parent):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
import kamoer_kphm400 as _kp                              # noqa: E402
import pump_case as _pc                                   # noqa: E402
from docgen import substitute_md                          # noqa: E402


# --- what the pump brings ----------------------------------------------------
# The head's square, half of it: how far its crown reaches off the pump's axis.
head_half = _kp.head_w / 2.0
# How far the head hangs below the bracket plane, into the lower cradle.
head_depth = _kp.head_depth
# The boss's octagon, half of it at the flats.
boss_half = _pc.bore_half_span
# The boss's whole run off the bracket plane — the bore wall's depth.
boss_depth = _pc.bore_bottom_z
# The bore the case turns the can in, half of it — what rises out of the shoulder.
can_half = _pc.cylinder_id / 2.0
# The mounting bracket the part carries at that plane, stated by `kamoer_kphm400` and drawn by
# nobody. It stands proud of the head all the way round. The cradle bears below it and the
# clamp's restored pressing plate lands above it.
bracket_half = _kp.bracket_w / 2.0
bracket_t = _kp.bracket_t
# The fall the head's outlet side takes under its barbs, and how far up off its front face it
# holds it — figures the lower cradle uses for its vertical fitting opening.
outlet_relief = _kp.outlet_relief
outlet_relief_run = _kp.outlet_relief_run
# The complete pump's widest X span, across the two tube fittings on its outlet face. This is
# not the head body's width; it is what the cradle opening passes at that one face.
outlet_half = _kp.outlet_span_x / 2.0
# The case's own footprint, half of it — what its base plate and the foot of its ramp reach.
case_half = _pc.footprint_half_extent
# And that base plate's own thickness. The enclosure restores this whole section above the
# stamped bracket before joining both collars into the clamp.
PLATE = _pc.base_thickness

# --- what the tray adds over the case it is cut out of -----------------------
# Tower kept over the boss's crown after the cylinder comes off. One wall, and it is the face
# that lands on that crown.
SHOULDER = 3.0
# Material carried past the head's own edge on the side the tray roots on, the same figure
# `valve_tray` carries past its last boss.
MARGIN = 3.0


def depth() -> float:
    """The tray's whole run along the pump's axis — the bore on the boss, and one `SHOULDER` of
    tower over its crown. What the piece has to own in height to build one."""
    return boss_depth + SHOULDER


def half_width() -> float:
    """Half the tray across — the case's own footprint."""
    return case_half


def far_reach() -> float:
    """How far the tray runs off the pump's axis away from the wall it roots on — the case's own
    footprint, which already carries past the head."""
    return case_half


def boss_room(air: float):
    """The room the clamp's pressing plate leaves one boss, in this module's frame — the
    case's own bore struck `air` off it over the boss's whole depth.

    IT IS THE BORE'S FIGURE AND NOT A BOX ROUND IT. The boss is an octagon with a ledge on
    four of its faces, and a block that took a square out for it left the square's four
    corners standing outside everything that goes back in: the tray's ramp closes them
    underneath, the tray's bore wall and tower wall them inboard, and the block's own fill
    closes them where the can begins. The octagonal collar walls, rather than this cutter,
    carry the fitted location."""
    return (cq.Workplane("XY")
            .polyline(_pc.offset_polygon(_pc.bore_profile, air)).close()
            .extrude(boss_depth).val())


def _case_base():
    """`pump_case`'s BASE, in that module's own frame: the calls `build_pump_case` makes for
    everything standing on the head's crown, and none of the skirt below it.

    The bore is left for `build_pump_tray` to cut. The case bores its own one `overcut` past the
    boss, which is what pierces a cut cleanly through to the skirt below; here there is no skirt
    under it and that overcut is the shoulder standing off the crown it is meant to land on."""
    solid = _pc.build_base_plate_with_ramp()
    solid = _pc.add_bore_wall(solid)
    return solid.union(_pc.build_tower())


def _slab(x0, x1, y0, y1, z0, z1):
    """One box, in `pump_case`'s frame."""
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def build_pump_tray(root: float):
    """One tray, in the pump's own frame.

    `root` is how far the plate runs from the pump's axis toward the wall it stands on — the
    piece's figure, since where that wall is is not the pump's business."""
    if root < head_half + MARGIN - 1e-9:
        raise ValueError(
            f"a tray rooted {root:.3f} mm off the axis stops short of the head's own "
            f"{head_half:.3f} and the `MARGIN` past it. The plate has to wrap the head's top "
            f"edge on the side it roots on, and the wall stands nearer this pump than that")
    if SHOULDER <= 0.0:
        raise ValueError(
            f"a {SHOULDER:g} mm shoulder leaves no tower over the boss's crown — the cut lands "
            f"on the crown itself and the tray covers only the head")
    cx, cy, hw, fr, d = _pc.center_x, _pc.center_y, half_width(), far_reach(), depth()
    big = max(hw, fr, root) + case_half + 10.0
    tray = _case_base()
    # CUT OFF THE CYLINDER, and then more: the tower down to one `SHOULDER` over the boss's crown.
    tray = tray.cut(_slab(cx - big, cx + big, cy - big, cy + big, d, d + big))
    # AND CARRY THE PLATE OUT to the case's own footprint, then re-cut the bore the plate just
    # filled back in.
    tray = tray.union(_slab(cx - hw, cx + hw, cy - root, cy + fr, 0.0, _pc.base_thickness))
    # THE BORE, on the boss's own depth exactly, so the shoulder over it lands ON the crown. Its
    # top face stands inside the tower's material, which is what a cut needs instead of the
    # overcut that would pierce free air here.
    tray = tray.cut(cq.Workplane("XY")
                    .workplane(offset=-1.0)
                    .center(cx, cy)
                    .polyline(_pc.bore_profile).close()
                    .extrude(boss_depth + 1.0))
    # AND THE TRAY STOPS ON THE FACE IT ROOTS ON, so it meets the wall plane to plane.
    tray = tray.cut(_slab(cx - big, cx + big, cy - root - big, cy - root, -1.0, d + 1.0))
    return tray.translate((-cx, -cy, 0.0))


def pump_bodies():
    """The reference pump's three solids, moved onto the tray's own origin — `kamoer_kphm400`
    draws them on the case's footprint centre, and this frame stands on the pump's axis."""
    return tuple(part().val().translate((-_kp.cx, -_kp.cy, 0.0))
                 for _name, part, _colour in _kp.BODY_PARTS)


def fouled_volume(root: float) -> float:
    """How much of the pump a tray stands inside — 0 mm³, or the tray is in the pump's way.

    The bore is the section the boss is extruded on, so the two share their eight walls; the
    plate's face lands on the head's crown and the shoulder's on the boss's, which are planes;
    and the can turns in a bore the case cuts wider than it."""
    tray = build_pump_tray(root).val()
    return sum(tray.intersect(body).Volume() for body in pump_bodies())


def storeys(root: float) -> tuple:
    """The tray's material on each of the two faces it covers, as `(on the head, on the crown)`
    in mm² of section — the reading that says a tray wraps BOTH storeys of the pump and not one.

    Read a hair above each face, so what is measured is the tray standing on it."""
    tray = build_pump_tray(root).val()
    out = []
    for z in (0.0, boss_depth):
        cut = tray.intersect(cq.Workplane("XY")
                             .box(1e3, 1e3, 0.02, centered=True)
                             .translate((0.0, 0.0, z + 0.05)).val())
        out.append(cut.Volume() / 0.02)
    return tuple(out)


def trays_of_machine(facts):
    """The collar sources the enclosure places, as `{name: root}` — one off each pump, as the
    artifact carries them from the run that stood the machine.

    The doc-only `main` hands in the artifact and imports the assembly that decides it. Keeping
    those run dependencies in `main` leaves the shape functions' source closure at this part."""
    return facts.pump_trays


def selftest() -> int:
    """The tray against the pump it takes and the case it is cut out of."""
    fails = []
    # The collar footprint must cover the stamped bracket so the enclosure can restore a
    # complete pressing annulus above its pocket.
    if half_width() < bracket_half:
        fails.append(f"the collar runs {half_width():.3f} mm off the axis and the bracket reaches "
                     f"{bracket_half:.3f} — the pressing annulus cannot cover it")
    if can_half >= boss_half:
        fails.append(f"the can's bore reaches {can_half:g} mm and the boss's octagon "
                     f"{boss_half:g} — the shoulder lands on nothing")
    root = head_half + MARGIN
    try:
        built = build_pump_tray(root).val()
        if not built.isValid():
            fails.append("the tray is not a valid solid")
        if len(built.Solids()) != 1:
            fails.append(f"the tray comes out {len(built.Solids())} solids, not one — the plate "
                         f"carried out has parted from the case's own")
        bb = built.BoundingBox()
        if abs(bb.zlen - depth()) > 1e-6:
            fails.append(f"a tray runs {bb.zlen:.4f} mm along the pump's axis against the "
                         f"{depth():g} it declares")
        foul = fouled_volume(root)
        if foul > 1e-6:
            fails.append(f"the tray stands {foul:.6f} mm^3 inside the pump it holds")
        on_head, on_crown = storeys(root)
        if on_head <= 0.0:
            fails.append("the tray carries no material on the head's own crown")
        if on_crown <= 0.0:
            fails.append("the tray carries no material on the boss's crown — the cut took the "
                         "shoulder with the cylinder")
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for what, bad in (("a tray rooted short of the head's own edge", head_half),
                      ("a tray rooted on the pump's axis", 0.0)):
        try:
            build_pump_tray(bad)
            fails.append(f"{what} was accepted")
        except ValueError:
            pass
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  pump-tray  {2 * half_width():g} across, {SHOULDER:g} of shoulder over "
              f"{boss_depth:g} of bore, octagon {2 * boss_half:g} at the flats, can bore "
              f"{2 * can_half:g}, clear of a {2 * bracket_half:g} bracket, "
              f"{on_head:.0f} mm² on the head and {on_crown:.0f} on the crown")
    return 1 if fails else 0


def main():
    sys.path.insert(0, str(_hw / "manifold-layout"))
    import enclosure_assembly as _ea                            # noqa: PLC0415,F401
    import _facts                                               # noqa: PLC0415

    trays = trays_of_machine(_facts.read())
    print(f"Pump clamp collar — {len(trays)} fused into the top clamp: {', '.join(sorted(trays))}")
    total, storey = 0.0, (0.0, 0.0)
    for name, root in sorted(trays.items()):
        solid = build_pump_tray(root).val()
        total += solid.Volume()
        storey = storeys(root)
        print(f"  {name}: {2 * half_width():g} x {root + far_reach():g}, {SHOULDER:g} of "
              f"shoulder over {boss_depth:g} of bore, rooted {root:g} mm off the pump's axis")
        print(f"    material {solid.Volume() / 1000.0:.2f} cm^3, valid {solid.isValid()}, "
              f"fouls the pump by {fouled_volume(root):.6f} mm^3")
        print(f"    covers {storey[0]:.0f} mm^2 on the head's crown and {storey[1]:.0f} on the "
              f"boss's")
    root = next(iter(sorted(trays.values())))

    substitute_md(
        _here.parent / "README.md",
        variables={
            "TRAY_W": f"{2 * half_width():g}",
            "TRAY_L": f"{root + far_reach():g}",
            "TRAY_D": f"{depth():g}",
            "PLATE": f"{PLATE:g}",
            "SHOULDER": f"{SHOULDER:g}",
            "CAN_BORE": f"{2 * can_half:g}",
            "TRAY_MARGIN": f"{MARGIN:g}",
            "TRAY_COUNT": f"{len(trays)}",
            "TRAY_VOL": f"{total / 1000.0:.2f}",
            "SOCKET_SPAN": f"{2 * boss_half:g}",
            "SOCKET_LEDGE": f"{_pc.ledge_depth:g}",
            "BOSS_DEPTH": f"{boss_depth:g}",
            "HEAD_W": f"{_kp.head_w:g}",
            "HEAD_D": f"{_kp.head_depth:g}",
            "CAN_DIA": f"{_kp.motor_dia:g}",
            "BRACKET_W": f"{2 * bracket_half:g}",
            "ON_HEAD": f"{storey[0]:.0f}",
            "ON_CROWN": f"{storey[1]:.0f}",
            "RAMP_H": f"{_pc.ramp_from_skirt_to_octagon_height:g}",
            "CASE_W": f"{2 * case_half:g}",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
