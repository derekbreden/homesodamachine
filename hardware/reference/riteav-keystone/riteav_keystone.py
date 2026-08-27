"""The RiteAV RJ11 6P4C black punchdown keystone jack, and the receptacle the +Y wall of
back-top holds it in.

A keystone is not held by a hole. It is held by a RECEPTACLE — an aperture at the show face, a
lip of stated depth behind it, a pocket taller than the aperture behind that, and two catches at
the pocket's back that the jack's own tang and latch snap over. The jack goes in from inside the
box: its top tang hooks the pocket's upper catch, the body swings down, and the lower latch
clicks. The ease under the aperture's top edge is what the body swings through; an aperture cut
straight through a wall blocks that swing and the jack will not seat.

    Interface        RJ11 6P4C — SIG-6's four conductors (TX / RX / 5 V / GND)
    Termination      110 IDC, 90 degrees, on the inboard face
    Mounting         keystone snap-in, face flush with the wall's outer plane
    Colour           black, with a snap-in dust cover in the bag
    Vendor           riteav.com mpn46181, bag of 10 (`ledger/purchases.md` §9)

WHERE THE FIGURES COME FROM. The keystone format's face is 14.5 × 16.0 mm, held by flexible
tabs — the module standard, per Wikipedia's *Keystone module*. The receptacle figures below are
the ones spuder's parametric keystone generator carries and prints against
(github.com/spuder/10-Inch-Rack-OpenSCAD, `KeystoneJack.scad`, CC-BY), which states the aperture
one clearance over the standard face and gives the ease angle, the pocket and the two catches.
That model exists because a receptacle without the ease does not accept a jack: the remix it
came from (thingiverse 4695995) was cut precisely to add it.

The jack's own depth behind the receptacle is estimated, not measured — a 110-punchdown Cat3
keystone runs about 30 mm from face to the back of its IDC block. `BODY_DEPTH` is what the band
above the cold core keeps clear behind the aperture, and it is the one figure here a caliper on
the delivered part is likely to move. RiteAV #58999 is on order.

Coordinate convention — jg_bulkhead_union's, so this station seats like the tube crossings:
  Y = mating axis. +Y = outward, toward the customer's plug.
  Origin = the wall's outer plane, which the jack's face lands on. The jack sits at y <= 0.
  +Z = up. X completes the right-handed frame.

Run:
    tools/cad-venv/bin/python hardware/reference/riteav-keystone/riteav_keystone.py
    tools/cad-venv/bin/python hardware/reference/riteav-keystone/riteav_keystone.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly  # noqa: E402
from _materials import M_DONOR_BLACK, one_body  # noqa: E402

STEP = _here.parent / "riteav-keystone.step"

# --- the module standard -------------------------------------------------------------
# The keystone face. Every module in the format shows this rectangle and no other.
FACE_W = 14.5
FACE_H = 16.0

# --- the receptacle the wall cuts ----------------------------------------------------
# The aperture, one printing clearance over the face.
APERTURE_W = 14.9
APERTURE_H = 16.3
# How deep the aperture runs before the pocket opens out behind it. The lip the jack's face
# bottoms against.
LIP_D = 3.0
# The pocket behind the lip: the room the body swings into, and taller than the aperture at
# both ends because the jack is wider behind its face than in it.
POCKET_W = 14.9
POCKET_H = 24.4
# How far the pocket's centre stands above the aperture's.
POCKET_RISE = 1.67
# The receptacle's whole depth, face plane to the catches' own faces.
DEPTH = 9.7
# The ease under the aperture's top edge, off the horizontal. The body swings through it.
EASE_DEG = 50.0
# The two catches standing at the pocket's back, as `(height, proud)` — the upper one the tang
# hooks and the lower one the latch snaps over.
CATCH_UPPER = (2.0, 1.4)
CATCH_LOWER = (2.6, 1.3)
# What the receptacle keeps around its pocket, so the boss carrying it is a wall and not a rim.
RECEPTACLE_WALL = 2.5

# --- the jack itself -----------------------------------------------------------------
# How far the body reaches inboard of the wall's outer plane — the volume the band above the
# cold core leaves clear behind the aperture. ESTIMATED.
BODY_DEPTH = 30.0
# The 6P4C port in the jack's face, and the latch slot over it.
PORT_W = 9.5
PORT_H = 7.6
PORT_DEPTH = 8.0
LATCH_SLOT_W = 3.4
LATCH_SLOT_H = 3.6
# The slip the jack takes in the pocket it snaps into.
FIT_SLIP = 0.25


def receptacle_envelope() -> tuple:
    """The boss's outline round the pocket, as `(wx, wz)`."""
    return (POCKET_W + 2.0 * RECEPTACLE_WALL, POCKET_H + 2.0 * RECEPTACLE_WALL)


def panel_cutout() -> tuple:
    """The aperture the wall shows, as `(wx, wz, radius)` — `iec_c14_inlet.panel_cutout`'s
    shape, which `enclosure_assembly.keystone_cutout` turns into a `back_ports` entry."""
    return (APERTURE_W, APERTURE_H, 0.4)


def panel_footprint() -> tuple:
    """What the station occupies on the wall's face, as `(wx, wz)`."""
    return receptacle_envelope()


def ease_rise() -> float:
    """How far the ease carries the aperture's top edge up over `LIP_D`."""
    return LIP_D * math.tan(math.radians(EASE_DEG))


def receptacle_cut(x: float, z: float, y_face: float):
    """The whole receptacle as one cutter, standing at `(x, z)` on a wall whose outer plane is
    `y_face`. Fused material is `receptacle_boss`; this is everything taken away.

    Three solids on one axis: the aperture through the lip, the ease over its top edge, and the
    pocket behind both."""
    y_lip = y_face - LIP_D
    y_back = y_face - DEPTH
    aperture = (cq.Workplane("XZ").rect(APERTURE_W, APERTURE_H).extrude(LIP_D + 0.02)
                .translate((x, y_face + 0.01, z)))
    pocket = (cq.Workplane("XZ").rect(POCKET_W, POCKET_H).extrude(DEPTH - LIP_D + 0.02)
              .translate((x, y_lip + 0.01, z + POCKET_RISE)))
    # THE EASE RAMPS THROUGH THE WALL'S DEPTH AND IS LEVEL ACROSS ITS WIDTH. It is a wedge on
    # the (Y, Z) plane swept along X: flush with the aperture's top edge where the customer's
    # eye meets it, standing `ease_rise` higher by the time it reaches the pocket. Swept on any
    # other pair it climbs across the face, which is an angle no jack has.
    top = z + APERTURE_H / 2.0
    ease = (cq.Workplane("YZ")
            .polyline([(y_face, top), (y_lip, top), (y_lip, top + ease_rise())]).close()
            .extrude(APERTURE_W)
            .translate((x - APERTURE_W / 2.0, 0.0, 0.0)))
    return aperture.union(pocket).union(ease).val(), (y_lip, y_back)


def receptacle_boss(x: float, z: float, y_face: float, y_inner: float):
    """The block the wall stands inboard to carry the pocket's remaining depth and its two
    catches. Returns `(material, catches)` — the catches are fused after the pocket is cut."""
    wx, wz = receptacle_envelope()
    y_back = y_face - DEPTH
    reach = y_inner - y_back
    if reach <= 0.0:
        return None, None
    block = (cq.Workplane("XZ").rect(wx, wz).extrude(reach)
             .translate((x, y_inner, z + POCKET_RISE)))
    top = z + POCKET_RISE + POCKET_H / 2.0
    bot = z + POCKET_RISE - POCKET_H / 2.0
    up_h, up_d = CATCH_UPPER
    lo_h, lo_d = CATCH_LOWER
    upper = (cq.Workplane("XZ").rect(POCKET_W, up_h).extrude(up_d)
             .translate((x, y_back + up_d, top - up_h / 2.0)))
    lower = (cq.Workplane("XZ").rect(POCKET_W, lo_h).extrude(lo_d)
             .translate((x, y_back + lo_d, bot + lo_h / 2.0)))
    return block.val(), upper.union(lower).val()


def build():
    """The jack as it stands in the wall: the face in the aperture, the body in the pocket, and
    the punchdown block reaching inboard behind them."""
    face = (cq.Workplane("XZ").rect(FACE_W, FACE_H).extrude(LIP_D)
            .translate((0.0, 0.0, 0.0)))
    body = (cq.Workplane("XZ").rect(POCKET_W - FIT_SLIP, POCKET_H - FIT_SLIP)
            .extrude(DEPTH - LIP_D)
            .translate((0.0, -LIP_D, POCKET_RISE)))
    block = (cq.Workplane("XZ").rect(FACE_W, POCKET_H - FIT_SLIP - 3.0)
             .extrude(BODY_DEPTH - DEPTH)
             .translate((0.0, -DEPTH, POCKET_RISE)))
    jack = face.union(body).union(block)
    port = (cq.Workplane("XZ").rect(PORT_W, PORT_H).extrude(PORT_DEPTH)
            .translate((0.0, 0.01, -1.0)))
    slot = (cq.Workplane("XZ").rect(LATCH_SLOT_W, LATCH_SLOT_H).extrude(PORT_DEPTH)
            .translate((0.0, 0.01, -1.0 - PORT_H / 2.0 - LATCH_SLOT_H / 2.0 + 1.2)))
    return jack.cut(port).cut(slot).val()


def selftest():
    """Checks the aperture clears the module face, the pocket clears the aperture, the ease
    carries the body's swing, and the built jack stands wholly inboard of the face plane."""
    ok = True
    if not (APERTURE_W > FACE_W and APERTURE_H > FACE_H):
        print("FAIL: the aperture does not clear the keystone face")
        ok = False
    if not (POCKET_H > APERTURE_H and DEPTH > LIP_D):
        print("FAIL: the pocket does not stand behind the lip")
        ok = False
    if ease_rise() < 2.0:
        print(f"FAIL: the ease carries only {ease_rise():.2f} mm over the lip")
        ok = False
    for name, (h, d) in (("upper", CATCH_UPPER), ("lower", CATCH_LOWER)):
        if not (0.0 < d < POCKET_W / 2.0 and 0.0 < h < POCKET_H / 2.0):
            print(f"FAIL: the {name} catch does not stand in the pocket")
            ok = False
    # THE EASE IS LEVEL ACROSS THE WIDTH, and this is the reading that says so. Swept on the
    # wrong pair it ramps across the face instead of through the depth, which leaves the
    # aperture's top edge standing at a different Z at each end of its own width.
    cut, (y_lip, _y_back) = receptacle_cut(0.0, 0.0, 0.0)

    def lip_top_at(xx):
        """The cutter's highest Z inside the lip's depth band, on a thin slab at `xx`."""
        probe = cq.Solid.makeBox(0.2, LIP_D - 0.4, POCKET_H * 3.0,
                                 cq.Vector(xx - 0.1, y_lip + 0.2, -POCKET_H * 1.5))
        return cut.intersect(probe).BoundingBox().zmax

    left = lip_top_at(-APERTURE_W / 2.0 + 1.0)
    right = lip_top_at(APERTURE_W / 2.0 - 1.0)
    if abs(left - right) > 0.02:
        print(f"FAIL: the ease stands at {left:.3f} on one side of the aperture and "
              f"{right:.3f} on the other — it ramps across the face, not through the depth")
        ok = False
    if not (APERTURE_H / 2.0 <= left <= APERTURE_H / 2.0 + ease_rise() + 0.02):
        print(f"FAIL: the ease tops out at {left:.3f}, outside the aperture's own "
              f"{APERTURE_H / 2.0:.3f} and its {ease_rise():.3f} of rise")
        ok = False
    bb = build().BoundingBox()
    if bb.ymax > LIP_D + 1e-9:
        print(f"FAIL: the jack stands {bb.ymax:.3f} proud of its own face plane")
        ok = False
    print("PASS: riteav-keystone receptacle and jack agree" if ok else "FAIL")
    return ok


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        raise SystemExit(0 if selftest() else 1)
    export_assembly(one_body(build(), "riteav-keystone", M_DONOR_BLACK), STEP)
    print(f"-> {STEP}")


if __name__ == "__main__":
    main()
