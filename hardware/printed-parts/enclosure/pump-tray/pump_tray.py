"""A PUMP TRAY IS THE PUMP CASE WITH ITS CYLINDER CUT OFF, and it is a wall of the enclosure.

One per Kamoer. `pump_case` draws a two-piece case for this pump; its BASE is a plate on the
head's crown, a 45° ramp off that plate, an octagonal bore wall standing in the ramp, and a
cylindrical tower over the bore that the motor can turns in. Cut the tower off above the bore and
cut down to one `SHOULDER` over it, and what is left is the tray: the same four surfaces, still
conforming to the same pump.

WHAT IT COVERS IS TWO STOREYS OF THE PUMP, NOT ONE. The base plate lands on the head's own +Z
face and wraps its top edge all the way round; the ramp climbs off that plate; the bore wall
takes the boss on each of its eight faces and both its ledges; and the shoulder the cut tower
leaves lands on the boss's crown and wraps ITS top edge. The can rises out of the tower's own
bore and the tray never touches it.

It is the pump cartridge's own material (`enclosure.build_cartridge`), fused onto its deck the
way the tap-water trough and the meter's saddles are fused onto their walls, one per pump off
the stations `enclosure_assembly.pump_tray_stations` reads off the placed pumps, rooted on the
face's own pump relief. NO TRAY SHIPS AS A PART.

    ACROSS  the case's own footprint, carried out to the straps' channels and one `MARGIN`
            past each
    ALONG   the case's own footprint, cut back to the face it roots on
    DEEP    the bore's whole run on the boss, and one `SHOULDER` of tower over its crown

THE CAP IS THE LOAD PATH AND THIS TRAY IS THE SEAT. A pump stands in the tray in plan and in
clock, and what holds it up is the BRACKET the part carries at that same crown
(`kamoer_kphm400.bracket_w`, stated there and drawn by nobody), lapping the top face of
`enclosure.build_pump_cap` all round the head's opening. The cap parts from the cartridge on
that very plane and two M3 draw it up, so this tray takes plan, clock and every moment, and the
screws take the weight.

This module states what the tray adds over the case and draws one in its own frame; `enclosure`
turns it onto a pump and fuses it. The frame is the pump's, as `kamoer_kphm400` draws it:
  Z = the pump's depth axis, out of the head toward the can. `z = 0` IS THE HEAD'S +Z FACE, which
      is `pump_case`'s own base plane, so the case drops in with no turn and only a shift.
  X = across the tray. Y = along it, and `root` is the way it runs to the wall.
  Origin is the pump's own axis on that face.

Printed face-down in the cartridge the deck stands as a wall off the face, and the ramp, bore
wall and shoulder grow off the plate's own section — nothing of the tray hangs.

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
# The head's square, half of it: how far its crown reaches off the pump's axis, and the flank the
# strap turns down.
head_half = _kp.head_w / 2.0
# How far the head hangs under that crown — the strap's two long legs.
head_depth = _kp.head_depth
# The boss's octagon, half of it at the flats.
boss_half = _pc.bore_half_span
# The boss's whole run off the head's crown — the bore wall's depth.
boss_depth = _pc.bore_bottom_z
# The bore the case turns the can in, half of it: what rises out of the shoulder, and what the
# strap's run has to clear where it crosses.
can_half = _pc.cylinder_id / 2.0
# The mounting bracket the part carries at that same crown, stated by `kamoer_kphm400` and drawn
# by nobody. It stands proud of the head all the way round, in the plane the plate lands on and
# the plane the cap parts on, and THAT LIP IS WHAT THE CAP'S TOP FACE LAPS — so what carries a
# pump is its own bracket and the two screws under it.
bracket_half = _kp.bracket_w / 2.0
bracket_t = _kp.bracket_t
# The case's own footprint, half of it — what its base plate and the foot of its ramp reach.
case_half = _pc.footprint_half_extent
# And that base plate's own thickness. It is the band a tray meets its neighbours in: every web
# `enclosure._tray_webs` runs to a wall, to the other tray or aft onto the valve panel is this
# thick and stands in this band, so the whole storey reads as one plate.
PLATE = _pc.base_thickness

# --- what the tray adds over the case it is cut out of -----------------------
# Tower kept over the boss's crown after the cylinder comes off. One wall, and it is the face
# that lands on that crown.
SHOULDER = 3.0
# Material carried past the head's own edge on the side the tray roots on, the same figure
# `valve_panel` carries past its last boss.
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


def trays_of_machine():
    """The trays the enclosure stands, as `{name: root}` — one off each placed pump, as the
    artifact carries them from the run that stood the machine.

    BOTH IMPORTS ARE IN THE CALL. `enclosure_assembly` builds its box out of this module's
    figures, so importing it at module scope closes a cycle through `enclosure`. And the import
    is what the sidecar's walk needs: that walk resolves a module name against the `sys.path`
    its driver stands on, and does not follow the one `_facts` makes inside `gather` — without
    this the tray's doc watches 26 files instead of 73 and stops noticing the machine that
    decides how far it runs to the wall."""
    sys.path.insert(0, str(_hw / "manifold-layout"))
    import enclosure_assembly as _ea                            # noqa: PLC0415,F401
    import _facts                                               # noqa: PLC0415
    return _facts.read().pump_trays


def selftest() -> int:
    """The tray against the pump it takes and the case it is cut out of."""
    fails = []
    # THE CAP IS WHAT CARRIES A PUMP, and the lip it lands on is the bracket's, in the plane
    # this tray's plate lands on. The tray reaches past that lip, so the bracket is captured
    # between the two pieces.
    if half_width() < bracket_half:
        fails.append(f"the tray runs {half_width():.3f} mm off the axis and the bracket reaches "
                     f"{bracket_half:.3f} — the lip stands outside the case that closes on it")
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
    trays = trays_of_machine()
    print(f"Pump tray — {len(trays)} stood on the pump cartridge: {', '.join(sorted(trays))}")
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
