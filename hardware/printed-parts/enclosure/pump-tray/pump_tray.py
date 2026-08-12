"""A PUMP TRAY IS A PLATE WITH A HOLE FOR THE MOTOR CAN AND A SOCKET UNDER IT FOR THE BOSS, and
it is a wall of the enclosure.

One per Kamoer. The can passes up through the hole and everything round it bears: the plate lands
on the boss's own top face all the way round that hole, and the socket hanging under the plate
takes the boss down to the head. The can's end face is the pump's highest and the tray never
touches it. It is `enclosure-front-top`'s own material, fused the way the tap-water trough, the
meter's saddles and the valve panels are: `enclosure._pump_trays` stands one per pump, off the
stations `enclosure_assembly.pump_tray_stations` reads off the placed pumps. NO TRAY SHIPS AS A
PART.

THE TRAY IS THE PUMP CASE'S OWN BORE. The socket is `pump_case.bore_profile`, the octagon that
case bores for this pump, ledges and all, and the section `kamoer_kphm400.build_rotor_housing`
extrudes the boss on; the hole is `pump_case.cylinder_id`, the tower bore that case turns the can
in. The socket takes the boss in X, in Y and in YAW over the boss's whole depth, so nothing about
where a pump stands is stated here.

    ACROSS  the strap's two channels, and one `MARGIN` past each
    ALONG   the head's own square, one `MARGIN` past its far edge, and as far toward the wall
            it roots on as the piece says
    DEEP    `THICK` of plate on the boss's crown, and the boss's own run of socket under it

THE STRAP IS THE LOAD PATH, the bargain the flow meter's saddles and the regulator's rib strike:
a pump hangs UNDER its tray. One strap closes round the pump and the tray together — down one
channel, past the socket and down that flank of the head, across the head's front face, up the
far flank and back up the other channel — and what it pulls is the boss's crown onto the plate.
The socket takes every moment; the strap stops the pump dropping.

THE STRAP'S BAND IS WHAT THE CAN LEAVES OF THE HEAD. Its two channels stand outside the head, so
the run between them crosses the plate's own face: inboard of the can's own radius that run lies
against the can, and outboard of the head's half-square its legs come down off the end of the
head.

This module states the tray's own figures and draws one in its own frame; `enclosure` turns it
onto a pump and fuses it. The frame is the pump's, as `kamoer_kphm400` draws it:
  Z = the pump's depth axis, out of the head toward the can. `z = 0` IS THE HEAD'S +Z FACE, so
      the socket spans z = 0 to the boss's own depth and the plate stands on top of that.
  X = across the tray. Y = along it, and `root` is the way it runs to the wall.
  Origin is the pump's own axis on that face.

In the piece's own print orientation — ceiling on the bed — the tray is a horizontal soffit over
the lane its pump hangs in, and it takes print support the way the tap-water trough's block and
the drip tray's rails do. The pump is laid INTO it that way up, its strap threaded first.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "reference" / "kamoer-kphm400",
           _hw / "printed-parts" / "flavor" / "pump-case"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
import kamoer_kphm400 as _kp                              # noqa: E402
import pump_case as _pc                                   # noqa: E402
from docgen import substitute_md                          # noqa: E402


# --- what the pump brings ----------------------------------------------------
# The head's square, half of it: how far its face reaches off the pump's axis, and the flank the
# strap turns down.
head_half = _kp.head_w / 2.0
# How far the head hangs under that face — the strap's two long legs.
head_depth = _kp.head_depth
# The boss's octagon, half of it at the flats: the socket's own span.
boss_half = _pc.bore_half_span
# That octagon, ledges and all, in the pump's own frame.
bore = _pc.bore_profile
# The socket's outer wall, one `pump_case.wall_thickness` round that octagon.
bore_wall = _pc.bore_wall_profile
# The boss's whole run off the head's face — the socket's depth.
boss_depth = _pc.bore_bottom_z
# The bore the case turns the motor can in, half of it: the hole the can passes through, and
# what the strap's run has to clear where it crosses the plate.
can_half = _pc.cylinder_id / 2.0

# --- what a strap is, here ---------------------------------------------------
# The WIDE strap, which is the one the tap-water trough's cavity is cut for.
# `enclosure_assembly`'s `strap-vocabulary` holds this table, the box's and the cold core's equal.
strap_w = 4.826          # the 50 lb strap, across its width — 0.19"
strap_t = 1.0            # and through its thickness
cav_buffer = 1.0         # the room a cavity carries over the strap
cav_w = strap_w + cav_buffer

# --- what the tray adds over the pump it takes -------------------------------
# The plate on the boss's crown, and twice itself on the strap's loop.
THICK = 3.0
# Material carried past a channel's far edge and past the head's own, the same figure
# `valve_panel` carries past its last boss.
MARGIN = 3.0
# The strap band's own standoff off the can.
CAN_LEAD = 0.5


def depth() -> float:
    """The tray's whole run along the pump's axis — the socket on the boss and the plate on its
    crown. What the piece has to own in height to build one."""
    return boss_depth + THICK


def chan_y() -> tuple:
    """The strap band, as `(near, far)` off the pump's axis — what the can leaves of the head's
    own square, which is where a run that crosses the plate clears the can and still lands on the
    head."""
    near = can_half + CAN_LEAD
    return near, near + cav_w


def chan_x() -> tuple:
    """A channel's own span across the tray, as `(near, far)` off the pump's axis. It opens one
    strap thickness outside the head, on the flank the strap runs down."""
    near = head_half + strap_t
    return near, near + cav_w


def half_width() -> float:
    """Half the tray across: the strap's channels, and one `MARGIN` past them."""
    return chan_x()[1] + MARGIN


def far_reach() -> float:
    """How far the tray runs off the pump's axis away from the wall it roots on: the head's own
    square and one `MARGIN` past it, so the plate bears on the whole of that face."""
    return head_half + MARGIN


def strap_loop() -> float:
    """The shortest strap that closes round a pump and its tray together.

    A strap turns INSIDE the channels, so what it reaches round is the pump with the plate's own
    material over it: across the plate's face between the two channels, down each channel, past
    the socket and down each flank of the head, and across the head's front face."""
    return (2.0 * chan_x()[0] + 2.0 * THICK
            + 2.0 * (boss_depth + head_depth) + 2.0 * head_half)


def build_pump_tray(root: float):
    """One tray, in the pump's own frame.

    `root` is how far the plate runs from the pump's axis toward the wall it stands on — the
    piece's figure, since where that wall is is not the pump's business. The channels stand on
    that side."""
    near, far = chan_y()
    if far > head_half + 1e-9:
        raise ValueError(
            f"the strap's band runs to {far:.3f} mm off the axis and the head reaches "
            f"{head_half:.3f} — its legs come down off the end of the head and wrap nothing. "
            f"The can's {can_half:g} and the head are what leave this band")
    if root < far + MARGIN - 1e-9:
        raise ValueError(
            f"a tray rooted {root:.3f} mm off the axis carries no material past its own strap "
            f"channel, which ends at {far:.3f} and wants one `MARGIN` past it. The wall stands "
            f"nearer this pump than its strap does")
    if can_half >= boss_half:
        raise ValueError(
            f"the can's bore is {can_half:g} mm off the axis and the boss's octagon reaches "
            f"{boss_half:g} — the hole takes the whole crown and the plate lands on nothing")
    hw, fr, d = half_width(), far_reach(), depth()
    # THE SOCKET: the case's own bore wall standing off the head's face, bored to the octagon
    # that is the boss — so the boss is taken on each of its eight faces and both its ledges.
    tray = (cq.Workplane("XY")
            .polyline(bore_wall).close()
            .extrude(boss_depth))
    # AND THE PLATE ON ITS CROWN, with the case's own tower bore through it for the can.
    tray = tray.union(cq.Workplane("XY")
                      .workplane(offset=boss_depth)
                      .polyline([(-hw, -root), (hw, -root), (hw, fr), (-hw, fr)])
                      .close()
                      .extrude(THICK))
    tray = tray.cut(cq.Workplane("XY")
                    .workplane(offset=-1.0)
                    .polyline(bore).close()
                    .extrude(boss_depth + 1.0))
    tray = tray.cut(cq.Workplane("XY")
                    .workplane(offset=boss_depth)
                    .circle(can_half)
                    .extrude(THICK + 1.0))
    # AND THE STRAP'S TWO CHANNELS through the plate, one either side of the can.
    x0, x1 = chan_x()
    for sx in (-1.0, 1.0):
        tray = tray.cut(cq.Workplane("XY")
                        .workplane(offset=boss_depth - 1.0)
                        .polyline([(sx * x0, -near), (sx * x1, -near),
                                   (sx * x1, -far), (sx * x0, -far)])
                        .close()
                        .extrude(THICK + 2.0))
    return tray


def pump_bodies():
    """The reference pump's three solids, moved onto the tray's own origin — `kamoer_kphm400`
    draws them on the case's footprint centre, and this frame stands on the pump's axis."""
    return tuple(part().val().translate((-_kp.cx, -_kp.cy, 0.0))
                 for _name, part, _colour in _kp.BODY_PARTS)


def _polygon_area(pts) -> float:
    """A closed polygon's area, by the shoelace — the socket's own section."""
    n = len(pts)
    return abs(sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
                   for i in range(n))) / 2.0


def tray_volume(root: float) -> float:
    """One tray's material, in closed form — the socket's ring, and the plate less the can's hole
    and its two channels.

    Every one of the four is a prism through its own layer's whole depth, and no two of them meet
    (`selftest`). The socket's outer wall stands inside the plate's plan, so the two layers meet
    on a plane and the union adds no volume."""
    x0, x1 = chan_x()
    near, far = chan_y()
    ring = _polygon_area(bore_wall) - _polygon_area(bore)
    plan = 2.0 * half_width() * (root + far_reach())
    channels = 2.0 * (x1 - x0) * (far - near)
    return ring * boss_depth + (plan - math.pi * can_half ** 2 - channels) * THICK


def fouled_volume(root: float) -> float:
    """How much of the pump a tray stands inside — 0 mm³, or the tray is in the pump's way.

    The socket is the section the boss is extruded on, so the two share their eight walls; the
    plate's face lands on the boss's crown and the socket's rim on the head's, which are planes;
    and the can turns in a bore the case cuts wider than it."""
    tray = build_pump_tray(root).val()
    return sum(tray.intersect(body).Volume() for body in pump_bodies())


def trays_of_machine():
    """The trays the enclosure stands, as `{name: root}` — one off each placed pump. Imported
    inside the call, because that module builds its box out of this one's figures."""
    sys.path.insert(0, str(_hw / "manifold-layout"))
    import enclosure_assembly as _ea                            # noqa: PLC0415
    return _ea.pump_tray_plans()


def selftest() -> int:
    """The tray against the pump it takes and the case it is bored like."""
    fails = []
    near, far = chan_y()
    x0, _x1 = chan_x()
    if far > head_half:
        fails.append(f"the strap band ends {far:.3f} mm off the axis, past the head's "
                     f"{head_half:.3f} — its legs wrap nothing")
    if near <= can_half:
        fails.append(f"the strap band starts {near:.3f} mm off the axis, inside the can's "
                     f"{can_half:g} — the run between its channels lies against the can")
    if x0 <= head_half:
        fails.append(f"a channel opens {x0:.3f} mm off the axis, inside the head's "
                     f"{head_half:.3f} — the strap turns down onto the head's own face")
    if can_half >= boss_half:
        fails.append(f"the can's bore reaches {can_half:g} mm and the boss's octagon "
                     f"{boss_half:g} — the plate lands on nothing")
    root = far_reach()
    try:
        built = build_pump_tray(root).val()
        closed = tray_volume(root)
        if abs(built.Volume() - closed) > 1e-6 * closed:
            fails.append(f"a tray measures {built.Volume():.3f} mm^3 against the {closed:.3f} "
                         f"its closed form says — a channel has met the socket or run off the "
                         f"plate")
        foul = fouled_volume(root)
        if foul > 1e-6:
            fails.append(f"the tray stands {foul:.6f} mm^3 inside the pump it holds")
        bb = built.BoundingBox()
        if abs(bb.zlen - depth()) > 1e-6:
            fails.append(f"a tray runs {bb.zlen:.4f} mm along the pump's axis against the "
                         f"{depth():g} it declares")
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for what, bad in (("a tray rooted inside its own channel", far),
                      ("a tray rooted on the pump's axis", 0.0)):
        try:
            build_pump_tray(bad)
            fails.append(f"{what} was accepted")
        except ValueError:
            pass
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  pump-tray  {2 * half_width():g} across, {THICK:g} of plate on "
              f"{boss_depth:g} of socket, octagon {2 * boss_half:g} at the flats, can bore "
              f"{2 * can_half:g}, strap band {near:g}..{far:g}, loop {strap_loop():.1f} mm")
    return 1 if fails else 0


def main():
    trays = trays_of_machine()
    print(f"Pump tray — {len(trays)} stood in enclosure-front-top: {', '.join(sorted(trays))}")
    total = 0.0
    for name, root in sorted(trays.items()):
        solid = build_pump_tray(root).val()
        total += solid.Volume()
        print(f"  {name}: {2 * half_width():g} x {root + far_reach():g} plate {THICK:g} on "
              f"{boss_depth:g} of socket, rooted {root:g} mm off the pump's axis")
        print(f"    material {solid.Volume() / 1000.0:.2f} cm^3, closed form "
              f"{tray_volume(root) / 1000.0:.2f} cm^3, valid {solid.isValid()}, fouls the pump "
              f"by {fouled_volume(root):.6f} mm^3")
    root = next(iter(sorted(trays.values())))

    substitute_md(
        _here.parent / "README.md",
        variables={
            "TRAY_W": f"{2 * half_width():g}",
            "TRAY_L": f"{root + far_reach():g}",
            "TRAY_T": f"{THICK:g}",
            "TRAY_D": f"{depth():g}",
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
            "STRAP_LOOP": f"{strap_loop():.1f}",
            "STRAP_W": f"{strap_w:g}",
            "BAND_NEAR": f"{chan_y()[0]:.4g}",
            "BAND_FAR": f"{chan_y()[1]:.4g}",
        },
        expected_counts={
            "TRAY_W": 1, "TRAY_L": 1, "TRAY_T": 1, "TRAY_D": 1, "CAN_BORE": 1,
            "TRAY_MARGIN": 1, "TRAY_COUNT": 1,
            "TRAY_VOL": 1, "SOCKET_SPAN": 1, "SOCKET_LEDGE": 1, "BOSS_DEPTH": 2,
            "HEAD_W": 1, "HEAD_D": 1, "CAN_DIA": 1, "STRAP_LOOP": 2, "STRAP_W": 1,
            "BAND_NEAR": 1, "BAND_FAR": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
