"""The purchased hardware inside the cold core, as solids.

Every body here is a PARAMETRIC STAND-IN built to its catalog envelope. What each one owes the
arrangement is where its mouths are and how much room it takes; what it does not owe is a
thread form or a casting radius. Each is built from the two or three figures the layout reads
off it — the mating dimension, the reach, the envelope — and each of those figures carries its
source in its own comment.

WHAT A FITTING IS FOR, in this file: the mouth. Each builder hands back the point and axis a
line lands on, and the assembly routes to that. A fitting that moves carries its line with it.
"""

from __future__ import annotations

import math
from collections import namedtuple

import cadquery as cq

IN = 25.4

# Where a line meets a body: the point it lands on and the outward axis it arrives along.
Mouth = namedtuple("Mouth", ["pos", "axis", "diam"])


def _hex(across_flats: float, height: float) -> cq.Solid:
    """A hex bar section — the barstock body every SS fitting here is turned from."""
    r = across_flats / math.sqrt(3.0)      # across-flats to circumradius
    pts = [(r * math.cos(math.radians(60 * i)), r * math.sin(math.radians(60 * i)))
           for i in range(6)]
    return cq.Workplane("XY").polyline(pts + pts[:1]).wire().extrude(height).val()


def _cyl(radius: float, height: float, base=(0, 0, 0), axis=(0, 0, 1)) -> cq.Solid:
    return cq.Solid.makeCylinder(radius, height, cq.Vector(*base), cq.Vector(*axis))


def _orient(solid, axis):
    """A solid built on +Z, stood on `axis`."""
    axis = cq.Vector(*axis)
    axis = axis.normalized()
    z = cq.Vector(0, 0, 1)
    dot = max(-1.0, min(1.0, z.dot(axis)))
    if dot > 1 - 1e-12:
        return solid
    if dot < -1 + 1e-12:
        return solid.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)
    return solid.rotate(cq.Vector(0, 0, 0), z.cross(axis), math.degrees(math.acos(dot)))


# --- TAISHER 316L 90° barstock street elbow, 1/4" NPT M × F -------------------
#
# `bom.md` §2 — the top plate's two carbonator-port elbows. Male on one leg, female on the other:
# the male threads into the plate's own tapped 1/4"-18 NPT and the female socket turns the line
# 90° onto its lateral axis, where a push-connect adapter or the SV-125 makes up on it.
#
# The hex is sized by the ⌀19 mm bore of `prv-shroud`, which the README there
# states the elbow seat enters: across corners has to clear it, so across flats stops at 5/8".
# `_carbonator.ELBOW_AXIS_OFFSET` is the male leg's standoff read off the shell's own storeys, and
# `_carbonator` passes it in rather than taking the catalog reach below.
ELBOW_HEX_AF = 0.625 * IN                 # 5/8" across flats — 18.33 across corners in a ⌀19 bore
ELBOW_LEG = 0.81 * IN                     # centre of the body to either face
ELBOW_BORE = 0.25 * IN                    # layout placeholder, NOT a measured purchased bore
# The male stub is drawn as the HOLE IT OCCUPIES — the 7/16" tap drill — through the plate it
# threads into. A 1/4" NPT major Ø is 0.540", wider than the drill, because the thread is cut
# into the plate rather than displacing it.
ELBOW_MALE_R = 0.5 * 0.4375 * IN
ELBOW_MALE_LEN = 0.26 * IN                # nominal L1 engagement; installed projection unmeasured
# The female socket is tapped, so what it receives is a male at its MAJOR Ø — the 0.540" the
# `jg-pp010822e` reference draws its shank at — for as deep as a stub goes, and the 1/4" run
# past that.
SOCKET_R = 0.5 * 0.540 * IN
SOCKET_DEPTH = 0.5 * IN


def street_elbow(*, corner, up=(0, 0, 1), out, up_leg=None, out_leg=None,
                 male_len=None):
    """A 90° street elbow standing on `corner`, where its two leg axes cross.

    The male leg runs `up` and threads into the plate its hex boss reaches; the female socket
    faces `out`. Each leg reaches `ELBOW_LEG` unless given its own: a male leg is as long as
    the face it lands on leaves, and `_carbonator` passes the standoff the shell's storeys strike.
    Hands back the solid and the mouth the next fitting makes up on."""
    up = cq.Vector(*up).normalized()
    out = cq.Vector(*out).normalized()
    c = cq.Vector(*corner)
    up_leg = ELBOW_LEG if up_leg is None else up_leg
    out_leg = ELBOW_LEG if out_leg is None else out_leg
    male_len = ELBOW_MALE_LEN if male_len is None else male_len

    leg_up = _orient(_hex(ELBOW_HEX_AF, up_leg), up).translate(c)
    leg_out = _orient(_hex(ELBOW_HEX_AF, out_leg), out).translate(c)
    stub = _orient(_cyl(ELBOW_MALE_R, male_len), up).translate(c + up.multiply(up_leg))
    solid = leg_up.fuse(leg_out).fuse(stub)

    bore_up = _orient(_cyl(ELBOW_BORE / 2, up_leg + male_len + 1), up).translate(c)
    bore_out = _orient(_cyl(ELBOW_BORE / 2, out_leg + 1), out).translate(c)
    socket = _orient(_cyl(SOCKET_R, min(SOCKET_DEPTH, out_leg)), out).translate(
        c + out.multiply(out_leg - min(SOCKET_DEPTH, out_leg)))
    solid = solid.cut(bore_up).cut(bore_out).cut(socket)
    return solid, Mouth(tuple(c + out.multiply(out_leg)), tuple(out), ELBOW_BORE)


# --- neoFit AME4-N2-E push-fit male elbow, 1/4" tube × 1/4" NPTF, black acetal ---------
#
# `bom.md` §2 — the bottom plate's two carbonator-port elbows. One piece: the male thread enters
# the plate's tapped 1/4"-18 NPT and the push-fit socket turns the line 90°, so the tube pushes
# straight into the elbow with no adapter. Figures off neoFit's Male Elbow NPTF drawing, AME4-N2
# row, linked from the FWS listing. The plan view draws the body's back as the post's own round,
# centred on the thread, which puts the mouth L − H/2 off the thread axis (about ±1 mm); the flow
# bore is the estimate the NeoFit stem-elbow reference takes.
MALE_ELBOW_THREAD = 0.520 * IN            # A — thread tip to shoulder
MALE_ELBOW_HEIGHT = 1.256 * IN            # E — thread tip to the far side of the body
MALE_ELBOW_BODY_D = 0.610 * IN            # ⌀P — the socket body
MALE_ELBOW_LENGTH = 1.063 * IN            # L — socket face to the back of the body
MALE_ELBOW_POST_W = 0.4375 * IN           # H — the body's width over the thread
MALE_ELBOW_INSERTION = 0.665 * IN         # B — socket face to tube stop
MALE_ELBOW_FLOW_BORE = 4.3
MALE_ELBOW_TUBE_OD = 0.25 * IN
# The socket axis over the thread's shoulder, and the mouth's reach off the thread axis.
MALE_ELBOW_AXIS_REACH = MALE_ELBOW_HEIGHT - MALE_ELBOW_THREAD - MALE_ELBOW_BODY_D / 2
MALE_ELBOW_MOUTH_REACH = MALE_ELBOW_LENGTH - MALE_ELBOW_POST_W / 2


def male_elbow(*, corner, up, out):
    """The one-piece push-fit male elbow standing on `corner`, where its two axes cross.

    The thread runs `up` into the plate from a shoulder `MALE_ELBOW_AXIS_REACH` off the corner;
    the socket faces `out`. Hands back the solid and the mouth the tube pushes into."""
    up = cq.Vector(*up).normalized()
    out = cq.Vector(*out).normalized()
    c = cq.Vector(*corner)
    body_r = MALE_ELBOW_BODY_D / 2
    socket_body = _orient(_cyl(body_r, MALE_ELBOW_MOUTH_REACH), out).translate(c)
    post = _orient(_cyl(MALE_ELBOW_POST_W / 2, body_r + MALE_ELBOW_AXIS_REACH), up).translate(
        c - up.multiply(body_r))
    thread = _orient(_cyl(ELBOW_MALE_R, MALE_ELBOW_THREAD), up).translate(
        c + up.multiply(MALE_ELBOW_AXIS_REACH))
    solid = socket_body.fuse(post).fuse(thread)

    mouth = c + out.multiply(MALE_ELBOW_MOUTH_REACH)
    socket = _orient(_cyl(MALE_ELBOW_TUBE_OD / 2, MALE_ELBOW_INSERTION), out).translate(
        mouth - out.multiply(MALE_ELBOW_INSERTION))
    bore_out = _orient(_cyl(MALE_ELBOW_FLOW_BORE / 2, MALE_ELBOW_MOUTH_REACH), out).translate(c)
    bore_up = _orient(_cyl(MALE_ELBOW_FLOW_BORE / 2,
                           MALE_ELBOW_AXIS_REACH + MALE_ELBOW_THREAD + 1), up).translate(c)
    solid = solid.cut(socket).cut(bore_out).cut(bore_up)
    return solid, Mouth(tuple(mouth), tuple(out), MALE_ELBOW_TUBE_OD)


# --- Control Devices SV-125 safety valve, 1/4" NPT, 125 psi -------------------
#
# `bom.md` §2, port 4. An open-port pop-off: the discharge leaves through the cap's own slots.
# Brass, hex base on a round cap. `printed-parts/cold-core/prv-shroud/` is what stands over it.
PRV_HEX_AF = 0.5625 * IN
PRV_HEX_H = 0.44 * IN
PRV_CAP_R = 0.5 * 0.62 * IN
PRV_CAP_H = 1.06 * IN
PRV_MALE_LEN = 0.50 * IN


def sv125(*, at, axis):
    """The PRV made up on a socket whose mouth is `at`, its body reaching along `axis`.

    The stub runs back from the mouth into the socket; the hex and cap stand off it."""
    axis = cq.Vector(*axis).normalized()
    base = cq.Vector(*at)
    stub = _orient(_cyl(ELBOW_MALE_R, PRV_MALE_LEN), axis).translate(
        base - axis.multiply(PRV_MALE_LEN))
    hexb = _orient(_hex(PRV_HEX_AF, PRV_HEX_H), axis).translate(base)
    cap = _orient(_cyl(PRV_CAP_R, PRV_CAP_H), axis).translate(base + axis.multiply(PRV_HEX_H))
    return stub.fuse(hexb).fuse(cap)


def sv125_reach() -> float:
    """How far the valve stands off the mouth it makes up on."""
    return PRV_HEX_H + PRV_CAP_H


# --- Guided ASA Aero float with an inserted RC62 ----------------------------
import _float_interface as _float
FLOAT_OD = _float.diameter
FLOAT_H = _float.height
FLOAT_BORE = _float.bore_diameter


def float_capsule(*, centre, axis=(0, 0, 1)):
    axis = cq.Vector(*axis).normalized()
    c = cq.Vector(*centre)
    body = _orient(_cyl(FLOAT_OD / 2, FLOAT_H), axis).translate(c - axis.multiply(FLOAT_H / 2))
    bore = _orient(_cyl(FLOAT_BORE / 2, FLOAT_H + 2), axis).translate(
        c - axis.multiply(FLOAT_H / 2 + 1))
    pocket = _cyl(_float.pocket_od / 2, _float.pocket_depth).cut(
        _cyl(_float.pocket_id / 2, _float.pocket_depth))
    pocket = _orient(pocket, axis).translate(c + axis.multiply(_float.magnet_seat - FLOAT_H / 2))
    magnet = _cyl(_float.magnet_od / 2, _float.magnet_thickness).cut(
        _cyl(_float.magnet_id / 2, _float.magnet_thickness))
    magnet = _orient(magnet, axis).translate(c + axis.multiply(_float.magnet_seat - FLOAT_H / 2))
    return cq.Compound.makeCompound([body.cut(bore).cut(pocket), magnet])


# --- MDSR-7-10-15 reed, 14 x 2.5 mm capture envelope -------------------------
#
# `bom.md` §12. The glass body is the whole of what has to fit: leads are wire and follow the
# channel. [10](REEDS_TOTAL) per build — 2 on the carbonator's bridge, 4 in each reservoir.
REED_GLASS_LEN = 14.0
REED_GLASS_R = 1.25              # ⌀2.5, the same figure `reed_bridge` cuts its pockets to


def reed(*, centre, axis=(0, 0, 1)):
    axis = cq.Vector(*axis).normalized()
    c = cq.Vector(*centre)
    return _orient(_cyl(REED_GLASS_R, REED_GLASS_LEN), axis).translate(
        c - axis.multiply(REED_GLASS_LEN / 2))


# --- DS18B20 / DS18S20 TO-92 1-wire probe ------------------------------------
#
# `bom.md` §5. Bare TO-92, leads heat-shrunk, taped to the surface it reads and potted in the
# pour. The package is the whole body: 4.3 × 4.3 mm with one face rounded, 5.2 tall.
TO92_W = 4.3
TO92_H = 5.2


def to92(*, centre, axis=(0, 0, 1)):
    axis = cq.Vector(*axis).normalized()
    c = cq.Vector(*centre)
    body = (cq.Workplane("XY").rect(TO92_W, TO92_W).extrude(TO92_H)
            .edges("|Z").fillet(1.2).val())
    return _orient(body, axis).translate(c - axis.multiply(TO92_H / 2))


def stand_x_along(solid, *, at, axis):
    """A solid built on +X, stood so its own +X runs along `axis` with its origin at `at`."""
    a = cq.Vector(*axis).normalized()
    x = cq.Vector(1, 0, 0)
    dot = max(-1.0, min(1.0, x.dot(a)))
    if dot > 1 - 1e-12:
        turned = solid
    elif dot < -1 + 1e-12:
        turned = solid.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)
    else:
        turned = solid.rotate(cq.Vector(0, 0, 0), x.cross(a), math.degrees(math.acos(dot)))
    return turned.translate(cq.Vector(*at))
