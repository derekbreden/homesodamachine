"""The anchor cap and the tube anchor it closes, in the anchor's own frame.

`u` runs along the tube, `n` from the tube toward the face the rib roots on, and `t = n x u`; a
section point (a, b) stands at mid + a*t + b*n, with b = 0 on the tube's axis plane. That is the
frame `enclosure._tube_anchors` strikes every rib in, so one station places the rib, its catch
windows, the ceiling's wing room and the cap.

THE RIB IS THE TIE RIB'S HALF PIPE WITHOUT THE TIE. A solid post, the seat bored into it and its
lips flat one `WALL` past the axis plane, with a catch window in each flank. Each window is a
closed pocket between the rib's two end webs, so on a piece printed root-down its bearing face
prints as a bridge web to web, the way the tie channel's crown did. On a rib rooted on a wall the
flank that looks print-down and its window's roof bridge web to web instead, and the two end
webs stand on the tied rib's own 45-degree corbels (`enclosure._capped_anchor`).

THE CAP IS THE OTHER HALF OF THE PIPE, one section extruded `CAP_LEN` along the tube. Below the
axis plane it is solid from the bore out to its round back; two `WING`-thick wings rise up the
rib's flanks and each carries a lip that drops into its window. A `CAVITY` gap separates the
half pipe from each wing for `CAVITY_DEG` round the pipe, so a wing bends from the gap's round
end rather than from the axis plane. That length is what sets its strain going on
(`wing_strain`), and the cap's README holds it beside the accepted faucet display cover's.

THE CAP IS CUT FOR THE 1/4" TUBE'S SEAT AND PRINTS STANDING ON ITS END. Every layer is the
whole section, so the wings bend along their extrusion lines, and no face overhangs.
"""
import math
import sys
from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "cadlib"))
import _enclosure_interface as dims  # noqa: E402
import fits  # noqa: E402

WALL = dims.wall
# The tube every capped anchor holds, and the seat the rib bores for it.
TUBE_OD = 6.35
SEAT_R = TUBE_OD / 2.0 + fits.slip
RIB_R = SEAT_R + WALL                   # the rib's half-width, the tie rib's own
# Along the tube: the cap, its end air to each window end, and the rib's end webs past those.
# One cap closes every capped crossing, so its rib has to stand whole on the shortest straight
# among them: `co2-2`'s 16.85 mm between its two R14 bends.
CAP_LEN = 10.0
END_AIR = fits.slip
WINDOW_LEN = CAP_LEN + 2.0 * END_AIR
END_WEB = WALL
RIB_LEN = WINDOW_LEN + 2.0 * END_WEB
# The section.
SADDLE = 2.5                            # the cap's half pipe, bore to the wing gap
WING = 1.5                              # each spring wing
WING_AIR = fits.slip                    # wing to rib flank
ENGAGE = 1.2                            # the lip's reach off its wing, the faucet cover's engagement
LIP_TIP = 0.9                           # the straight face at the lip's tip
LEAD_IN = 30.0                          # the lip's ramp, degrees off the push
WING_TOP = 10.3                         # the wings' tops above the axis plane
CAVITY_DEG = 36.0                       # how far round the half pipe the wing gap runs
MOUTH = 0.45                            # the cap bore's eased edges...
MOUTH_DEG = 10.0                        # ...run out this far round the bore
RIB_CHAMFER = 0.8                       # the rib's outer bottom edges, where the lips ride on
HEADROOM = 0.6                          # wing top to the face the rib roots on

RAMP_H = ENGAGE / math.tan(math.radians(LEAD_IN))
LIP_H = LIP_TIP + RAMP_H
LIP_B = WING_TOP - LIP_H                # the lip's flat retention face
WING_IN = RIB_R + WING_AIR
WING_OUT = WING_IN + WING
SADDLE_R = SEAT_R + SADDLE
CAVITY = WING_IN - SADDLE_R             # `WALL + WING_AIR - SADDLE`, whatever the seat
# The window: deep enough for the lip's whole engagement with a slip and the bridged roof's
# finish allowance beyond it, from the bearing face a slip and that allowance under the seated
# lip up to where the flank ends (`window_top`), which is past a slip over where the lip's ramp
# crosses the flank (`WINDOW_B1`).
BEARING_PLAY = fits.slip + fits.supported_surface
WINDOW_DEPTH = ENGAGE + fits.slip + fits.supported_surface
WINDOW_B0 = LIP_B - BEARING_PLAY
WINDOW_B1 = LIP_B + LIP_TIP + (ENGAGE - WING_AIR) / ENGAGE * RAMP_H + fits.slip
# The wing room a root face standing inside the wings' reach gives up: the wing, the spread its
# lip makes passing the flank, and a slip either side, to `HEADROOM` over the wing tops.
SLOT_W = WING_AIR + WING + ENGAGE + 2.0 * fits.slip
SLOT_TOP = WING_TOP + HEADROOM


class Frame:
    """An anchor's frame: `mid` on the tube's axis at the rib's centre, `u` along the tube, `n`
    toward the root face."""

    def __init__(self, mid, u, n):
        self.mid = tuple(float(c) for c in mid)
        self.u = tuple(float(c) for c in u)
        self.n = tuple(float(c) for c in n)
        u_, n_ = self.u, self.n
        self.t = (n_[1] * u_[2] - n_[2] * u_[1], n_[2] * u_[0] - n_[0] * u_[2],
                  n_[0] * u_[1] - n_[1] * u_[0])

    def point(self, a, b, s=0.0):
        return tuple(self.mid[k] + a * self.t[k] + b * self.n[k] + s * self.u[k] for k in range(3))

    def plane(self, s):
        """The section plane `s` along the tube; its x is `t` and its y comes out as `n`."""
        return cq.Plane(origin=cq.Vector(*self.point(0.0, 0.0, s)), xDir=cq.Vector(*self.t),
                        normal=cq.Vector(*self.u))

    def prism(self, pts, s0, s1):
        return cq.Workplane(self.plane(s0)).polyline(pts).close().extrude(s1 - s0).val()

    def section(self, start, segments, s0, s1):
        """Lines ("L", p) and three-point arcs ("A", via, end) in (a, b), extruded s0..s1."""
        wp = cq.Workplane(self.plane(s0)).moveTo(*start)
        for seg in segments:
            wp = wp.lineTo(*seg[1]) if seg[0] == "L" else wp.threePointArc(seg[1], seg[2])
        return wp.close().extrude(s1 - s0).val()

    def bore(self, r, s0, s1):
        return cq.Solid.makeCylinder(r, s1 - s0, cq.Vector(*self.point(0.0, 0.0, s0)),
                                     cq.Vector(*self.u))


def _lip(side):
    """A wing's lip: the flat retention face under it, the straight tip, and the ramp back out to
    the wing's top inner corner, so no strip of the wing's inner face stands over the ramp."""
    pts = [(WING_IN + 0.05, LIP_B), (WING_IN - ENGAGE, LIP_B), (WING_IN - ENGAGE, LIP_B + LIP_TIP),
           (WING_IN, LIP_B + LIP_H), (WING_IN + 0.05, LIP_B + LIP_H)]
    return [(side * a, b) for a, b in pts]


def _cavity(frame, side, s0, s1):
    """The gap between half pipe and wing, from above the axis plane `CAVITY_DEG` round the pipe
    and round-ended there, so the wing's root is a full radius."""
    t = math.radians(CAVITY_DEG)
    r0, r1 = SADDLE_R, WING_IN
    rm, rh = (r0 + r1) / 2.0, (r1 - r0) / 2.0
    end = (rm * math.cos(t) - rh * math.sin(t), -rm * math.sin(t) - rh * math.cos(t))
    pts = [("L", (r1, 0.5)), ("L", (r1, 0.0)),
           ("A", (r1 * math.cos(t / 2), -r1 * math.sin(t / 2)), (r1 * math.cos(t), -r1 * math.sin(t))),
           ("A", end, (r0 * math.cos(t), -r0 * math.sin(t))),
           ("A", (r0 * math.cos(t / 2), -r0 * math.sin(t / 2)), (r0, 0.0))]
    mirror = [(k, *[(side * p[0], p[1]) for p in rest]) for k, *rest in pts]
    return frame.section((side * r0, 0.5), mirror, s0, s1)


def cap(frame, seat_r=SEAT_R):
    """The cap pushed home: its shoulders on the rib's lips at b = 0, centred on the station."""
    s0, s1 = -CAP_LEN / 2.0, CAP_LEN / 2.0
    ca, sa = math.cos(math.radians(MOUTH_DEG)), math.sin(math.radians(MOUTH_DEG))
    body = frame.section((WING_IN, WING_TOP), [
        ("L", (WING_OUT, WING_TOP)), ("L", (WING_OUT, 0.0)),
        ("A", (0.0, -WING_OUT), (-WING_OUT, 0.0)),
        ("L", (-WING_OUT, WING_TOP)), ("L", (-WING_IN, WING_TOP)), ("L", (-WING_IN, 0.0)),
        ("L", (-seat_r - MOUTH, 0.0)), ("L", (-seat_r * ca, -seat_r * sa)),
        ("A", (0.0, -seat_r), (seat_r * ca, -seat_r * sa)),
        ("L", (seat_r + MOUTH, 0.0)), ("L", (WING_IN, 0.0)),
    ], s0, s1)
    for side in (1, -1):
        body = body.fuse(frame.prism(_lip(side), s0, s1))
    for side in (1, -1):
        body = body.cut(_cavity(frame, side, s0 - 1.0, s1 + 1.0))
    return body.clean()


def rib(frame, b_root, seat_r=SEAT_R):
    """The rib, root face to the axis plane, its seat bored and its outer bottom edges chamfered.
    The windows are cut from the piece once the rib is fused (`windows`)."""
    c = RIB_CHAMFER
    body = frame.prism([(-RIB_R + c, 0.0), (RIB_R - c, 0.0), (RIB_R, c), (RIB_R, b_root),
                        (-RIB_R, b_root), (-RIB_R, c)], -RIB_LEN / 2.0, RIB_LEN / 2.0)
    return body.cut(frame.bore(seat_r, -RIB_LEN / 2.0 - 1.0, RIB_LEN / 2.0 + 1.0))


def window_top(b_face):
    """Where a window ends toward the root: where the flank it is cut in ends, so no band of
    flank stands between the window and that face. That is the root face, or the top of the
    wing room cut into it (`wing_room`), whose inner wall the flank runs on up."""
    return SLOT_TOP if b_face < SLOT_TOP - HEADROOM / 2.0 else b_face


def windows(frame, b_face):
    """The two catch windows, each run out past its flank so the cut is clean, from its bearing
    face to where the flank ends (`window_top`)."""
    top = window_top(b_face)
    out = []
    for side in (1, -1):
        a_in, a_out = side * (RIB_R - WINDOW_DEPTH), side * (RIB_R + 2.0)
        out.append(frame.prism([(a_in, WINDOW_B0), (a_out, WINDOW_B0), (a_out, top),
                                (a_in, top)], -WINDOW_LEN / 2.0, WINDOW_LEN / 2.0))
    return out


def wing_room(frame, b_face):
    """Where the face the rib roots on stands inside the wings' reach, the slot each wing and
    its spread take through that face, from a millimetre under it to `SLOT_TOP`. None where the
    face leaves the wing tops at least half their `HEADROOM`, which no slot that shallow would
    improve on."""
    if b_face >= SLOT_TOP - HEADROOM / 2.0:
        return []
    out = []
    for side in (1, -1):
        a0, a1 = side * RIB_R, side * (RIB_R + SLOT_W)
        out.append(frame.prism([(a0, b_face - 1.0), (a1, b_face - 1.0), (a1, SLOT_TOP),
                                (a0, SLOT_TOP)], -WINDOW_LEN / 2.0, WINDOW_LEN / 2.0))
    return out


def wing_strain():
    """Peak strain in a wing as its lip passes the flank, on the beam estimate: the wing fixed
    at the gap's round end, loaded across at the middle of the lip's flat tip, deflected by
    `ENGAGE`. delta = F/EI * integral(lever^2 ds); strain = F * max lever * (WING / 2) / EI."""
    rm = (WING_IN + WING_OUT) / 2.0
    load_b = LIP_B + LIP_TIP / 2.0
    pts = [(rm * math.cos(-math.radians(CAVITY_DEG) * (1 - i / 40)),
            rm * math.sin(-math.radians(CAVITY_DEG) * (1 - i / 40))) for i in range(41)]
    pts += [(rm, load_b * i / 20) for i in range(1, 21)]
    integral = sum((load_b - (p[1] + q[1]) / 2.0) ** 2 * math.dist(p, q) for p, q in zip(pts, pts[1:]))
    lever = max(abs(load_b - p[1]) for p in pts)
    return ENGAGE * lever * (WING / 2.0) / integral


def wing_flex_len():
    """The wing's length from the gap's round end to the middle of the lip's tip."""
    rm = (WING_IN + WING_OUT) / 2.0
    return rm * math.radians(CAVITY_DEG) + LIP_B + LIP_TIP / 2.0
