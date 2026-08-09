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
    return cq.Workplane("XY").polyline(pts).close().extrude(height).val()


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
# `bom.md` §2 — all four vessel-port elbows. Male on one leg, female on the other: the male
# threads into the plate's own tapped 1/4"-18 NPT and the female socket turns the line 90° onto
# its lateral axis, where a PP010822E collet, the SV-125 or the sparge barb makes up on it.
#
# The hex is sized by the ⌀[19](PRV_INNER_D) mm bore of `prv-shroud`, which the README there
# states the elbow seat enters: across corners has to clear it, so across flats stops at 5/8".
# `_vessel.ELBOW_AXIS_OFFSET` is the male leg's standoff read off the shell's own storeys, and
# `_vessel` passes it in rather than taking the catalog reach below.
ELBOW_HEX_AF = 0.625 * IN                 # 5/8" across flats — 18.33 across corners in a ⌀19 bore
ELBOW_LEG = 0.81 * IN                     # centre of the body to either face
ELBOW_BORE = 0.25 * IN                    # the 1/4" run through it
# The male stub is drawn as the HOLE IT OCCUPIES — the 7/16" tap drill — through the plate it
# threads into. A 1/4" NPT major Ø is 0.540", wider than the drill, because the thread is cut
# into the plate rather than displacing it.
ELBOW_MALE_R = 0.5 * 0.4375 * IN
ELBOW_MALE_LEN = 0.26 * IN                # L1 hand-tight engagement, one plate thick
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
    the face it lands on leaves, and `_vessel` passes the standoff the shell's storeys strike.
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


# --- LTWFITTING 1/4" hose barb × 1/4" MNPT, 316 SS ---------------------------
#
# `bom.md` §2, port 1. Threads into the bottom plate's lane-side elbow with the barb facing
# INWARD, into the vessel: the silicone stub hangs off it and the sparge stone hangs off that.
# The barb and the port's own elbow are two male fittings in ONE through-tapped hole, one from
# each face, so each reaches half the plate.
BARB_STUB_LEN = 0.125 * IN
BARB_HEX_AF = 0.5625 * IN
BARB_HEX_H = 0.31 * IN
BARB_LEN = 0.75 * IN
BARB_R = 0.5 * 0.25 * IN


def hose_barb(*, at, axis):
    """The barb adapter, male stub at `at`, barb reaching along `axis`."""
    axis = cq.Vector(*axis).normalized()
    base = cq.Vector(*at)
    stub = _orient(_cyl(ELBOW_MALE_R, BARB_STUB_LEN), -axis).translate(base)
    hexb = _orient(_hex(BARB_HEX_AF, BARB_HEX_H), axis).translate(base)
    barb = _orient(_cyl(BARB_R * 1.15, BARB_LEN), axis).translate(base + axis.multiply(BARB_HEX_H))
    tip = base + axis.multiply(BARB_HEX_H + BARB_LEN)
    return stub.fuse(hexb).fuse(barb), Mouth(tuple(tip), tuple(axis), 0.25 * IN)


# --- FERRODAY 0.5 µm sintered 316 SS sparge stone, 1/4" barb -----------------
#
# `bom.md` §2. Hangs in the water column on the silicone stub off port 1.
# ⌀[2"](STONE_D) × 1/2" is the 2-set's size.
STONE_R = 0.5 * 2.0 * IN
STONE_H = 0.5 * IN
STONE_STEM_LEN = 0.55 * IN


def sparge_stone(*, at, axis):
    """The stone, its barb stem at `at` and its body along `axis`."""
    axis = cq.Vector(*axis).normalized()
    base = cq.Vector(*at)
    stem = _orient(_cyl(BARB_R * 1.15, STONE_STEM_LEN), axis).translate(base)
    body = _orient(_cyl(STONE_R, STONE_H), axis).translate(base + axis.multiply(STONE_STEM_LEN))
    return stem.fuse(body)


def sparge_reach() -> float:
    return STONE_STEM_LEN + STONE_H


# --- YXQ float capsule (harvested) -------------------------------------------
#
# `bom.md` §12. Only the float is shipped product — a commodity ⌀[28](FLOAT_D) mm crimped
# stainless capsule with a ferrite donut inside. It rides the 1/8" rod, so its bore places it.
FLOAT_OD = 28.0
FLOAT_H = 19.0
FLOAT_BORE = 0.1875 * IN


def float_capsule(*, centre, axis=(0, 0, 1)):
    axis = cq.Vector(*axis).normalized()
    c = cq.Vector(*centre)
    body = _orient(_cyl(FLOAT_OD / 2, FLOAT_H), axis).translate(c - axis.multiply(FLOAT_H / 2))
    bore = _orient(_cyl(FLOAT_BORE / 2, FLOAT_H + 2), axis).translate(
        c - axis.multiply(FLOAT_H / 2 + 1))
    return body.cut(bore)


# --- Gebildet reed switch, 14 mm glass body ----------------------------------
#
# `bom.md` §12. The glass body is the whole of what has to fit: leads are wire and follow the
# channel. [10](REEDS_TOTAL) per build — 2 on the carbonator's bridge, 4 in each reservoir.
REED_GLASS_LEN = 14.0
REED_GLASS_R = 1.1


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


# --- PureSec 1/4" RO push-to-connect 90° elbow bulkhead ----------------------
#
# `bom.md` §8 — the reservoir floor/trough outlet. Threaded barrel up through the ⌀16 floor
# bore, hex nut under it, integral 90° elbow turning the syrup line laterally.
PURESEC_BARREL_R = 8.0
PURESEC_NUT_AF = 22.0
PURESEC_NUT_H = 6.0
PURESEC_COLLET_R = 6.0
PURESEC_ELBOW_LEG = 16.0


PURESEC_BARREL_LEN = 14.0
PURESEC_BODY_DROP = 3.0


def puresec_elbow(*, corner, up=(0, 0, 1), out, barrel_len=None, collet_r=None):
    """The bulkhead standing on `corner`, where its two leg axes cross.

    The barrel rises `up` from the corner through the trough floor, with its nut on the wet side
    at the top of it; the collet faces `out` on the corner's own storey."""
    up = cq.Vector(*up).normalized()
    out = cq.Vector(*out).normalized()
    c = cq.Vector(*corner)
    barrel_len = PURESEC_BARREL_LEN if barrel_len is None else barrel_len
    collet_r = PURESEC_COLLET_R if collet_r is None else collet_r
    barrel = _orient(_cyl(PURESEC_BARREL_R, barrel_len), up).translate(c)
    nut = _orient(_hex(PURESEC_NUT_AF, PURESEC_NUT_H), up).translate(
        c + up.multiply(barrel_len))
    leg = _orient(_cyl(collet_r, PURESEC_ELBOW_LEG), out).translate(c)
    body = _orient(_cyl(collet_r, PURESEC_BODY_DROP), -up).translate(c)
    solid = barrel.fuse(nut).fuse(leg).fuse(body)
    return solid, Mouth(tuple(c + out.multiply(PURESEC_ELBOW_LEG)), tuple(out), 6.35)


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


# --- uxcell silicone flat washer, ⌀16 ID × ⌀24 OD × 3 mm ---------------------
#
# `bom.md` §8 — the reservoir bulkhead's wet-side face seal, in the wet-side counterbore under
# the bulkhead's own nut.
WASHER_ID = 16.0
WASHER_OD = 24.0
WASHER_T = 3.0


def silicone_washer(*, centre, axis=(0, 0, 1)):
    axis = cq.Vector(*axis).normalized()
    c = cq.Vector(*centre)
    ring = _orient(_cyl(WASHER_OD / 2, WASHER_T), axis).translate(c)
    bore = _orient(_cyl(WASHER_ID / 2, WASHER_T + 2), axis).translate(c - axis.multiply(1))
    return ring.cut(bore)


# --- LVDALAB PTFE membrane filter, ⌀13 × 0.45 µm ----------------------------
#
# `bom.md` §13 — the hydrophobic membrane in each reservoir cap's vent pocket.
MEMBRANE_D = 13.0
MEMBRANE_T = 0.15


def membrane(*, centre, axis=(0, 0, 1)):
    axis = cq.Vector(*axis).normalized()
    return _orient(_cyl(MEMBRANE_D / 2, MEMBRANE_T), axis).translate(cq.Vector(*centre))
