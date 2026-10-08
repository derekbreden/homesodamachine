"""The umbilical plug and socket as printable parts: the SOCKET that snaps into back-top's rear wall,
the RETAINER screwed behind its unions, the PLUG on the umbilical's machine end, the KEY that clamps
the plug's four tubes, and a COUPON of 6 mm wall cut the way back-top would be.

Every outside surface shares one section, `profile`: a circle closed top and bottom by 36-degree
planes and a flat, the support-free roof `enclosure.teardrop_roof_angle` sets for these prints. Both
halves print with their mating face standing, so the K&J SB443-IN bars slide down printed rails at
one pause and are printed over.

The socket's four unions float NOSE_AIR + one collet stroke along their axes. Pulling the plug drags
them forward until each collet sleeve lands on the floor's back face, the RELEASE face, and the
collets let go: the pump cartridge's fixed release plate and floating tees
(`assembly/internal-plumbing.md` §4), turned to face the plug.

Frame: the socket floor, where the plug's face lands, is y = 0. The cup and the wall are -Y, the
machine is +Y, up is +Z. The plug is drawn mated.
"""
import math
import sys
from pathlib import Path

_HERE = (Path(__file__).resolve() if "__file__" in globals()
         else Path.cwd() / "future/umbilical-plug-and-socket-exploration/umbilical.py")
ROOT = next(p for p in _HERE.parents if (p / "hardware").is_dir())
REF = ROOT / "hardware" / "reference"
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ROOT / "hardware/printed-parts/cadlib"),
                str(REF / "jg-pp0408w"), str(REF / "yyfkgcp-pogo-4p")]

import cadquery as cq  # noqa: E402
import fits  # noqa: E402
import jg_pp0408w as U  # noqa: E402
import yyfkgcp_pogo_4p as P  # noqa: E402

ROOF = math.radians(36.0)                 # enclosure.teardrop_roof_angle
SIN, COS, TAN = math.sin(ROOF), math.cos(ROOF), math.tan(ROOF)
BACK_TOP_WALL = 6.0                       # enclosure.back_top_wall_t

# --- purchased parts ------------------------------------------------------------------------------
# K&J SB443-IN, 1/4 x 1/4 x 3/16 in, N42 through the 3/16: a 1.6 mm full-width band at the pole
# face, then a 1.6 mm groove 0.79 deep in each side, then full width again (drawing rev 0).
BAR, BAR_T = 6.35, 4.7625
GROOVE_TOP, GROOVE_H, GROOVE_D = 1.6, 1.6, (6.35 - 4.7625) / 2
BAR_CLR = 0.10                            # each side of the slot the bar slides down
RAIL_H = GROOVE_H - 0.10                  # rail in the groove, 0.05 above and below
RAIL_CLR = 0.09                           # rail tip to groove floor
BAR_AIR = 0.10                            # least air over the bar before the first closing bead

# neoFit AUC44M, 4 mm union (FWS; John Guest PM0404E is its equivalent). The neoFit drawing gives
# Ø13.2 x 31.8 with 14.7 mm socket ends; John Guest's DS-PM04 gives the 13.0 mm tube insertion.
# Neither gives the collet sleeve, so its release face is the cavity's own floor and its back
# stop assumes a sleeve standing at least D_PROUD_MIN proud.
D_RING, D_L, D_END, D_INSERTION = 13.2, 31.8, 14.7, 13.0
D_PROUD_MIN = 1.0
D_REAR_PASS = 10.0                         # retainer's hole over its rear collet, whatever its size

LAYER, FIRST_LAYER = 0.24, 0.20           # hardware/printed-parts/petgf.3mf

# --- layout on the face ---------------------------------------------------------------------------
WEB = 1.5                                 # PET-GF between a bar's slot and a tube hole
HOLE_Q = 6.6                              # over 1/4" tube (6.35), under the collet's 6.69 bore
HOLE_D = 4.3                              # over 4 mm tube, under its collet's bore
MAG_X = 9.0
PITCH = 2 * (HOLE_Q / 2 + WEB + BAR / 2 + BAR_CLR)
H = PITCH / 2
R_AXIS = H * math.sqrt(2)
PORTS = {                                 # name: (x, z, tube OD)
    "flavor-a": (-H, H, 6.35),
    "flavor-b": (H, H, 6.35),
    "soda": (-H, -H, 6.35),
    "drain": (H, -H, 4.0),
}

# --- the socket, along y --------------------------------------------------------------------------
RELEASE = 9.8                             # floor back face, where each collet sleeve lands
NOSE_AIR = 0.5                            # sleeve to release face, connected
COLLET_Q = RELEASE + NOSE_AIR             # 1/4" collet face, connected
RING_Q = COLLET_Q + U.COLLET_PROUD        # its body's front face
REAR = RING_Q + U.BODY_LEN                # its body's back face: the retainer's face
RING_FROM = RELEASE + U.COLLET_PROUD - U.COLLET_TRAVEL - 0.10   # cavity shoulder, past full release
DRAIN_STOP = RELEASE + NOSE_AIR + D_L - D_PROUD_MIN
STUB_MARGIN = 0.5                         # a stub stops this short of its tube stop
STUB_Q = COLLET_Q + U.INSERTION - STUB_MARGIN
STUB_D = COLLET_Q + D_INSERTION - STUB_MARGIN
CUP_DEPTH = math.ceil(STUB_Q + 8.0)       # the plug is 8 mm into the cup before a stub reaches a hole
FACE = -CUP_DEPTH                         # flange front, flush with back-top's outer face
FLANGE_T = 3.0
LEDGE = FACE + FLANGE_T
WALL_IN = FACE + BACK_TOP_WALL
HOOK_CLR = 0.15
RETAINER_T = 4.0

# --- sections -------------------------------------------------------------------------------------
PLUG_R = R_AXIS + HOLE_Q / 2 + WEB        # the 45-degree web on the tube holes
PLUG_F = 15.0
CUP_CLR = fits.running
BODY_R, BODY_F = 21.0, 22.3
FLANGE_R = BODY_R + 2.5
HOLE_CLR = fits.slip
PLUG_L = 52.0
COUNTER_HOLE = 34.93                      # faucet_assembly.countertop_hole_diameter, 1-3/8"

# --- pogo, both halves (yyfkgcp-pogo-4p/mounting-audit.md) ---------------------------------------
POGO_RECESS = 0.123                       # each nose behind its face: 0.246 between them, as on the cartridge
POGO_CLR = 0.20
INSERT_HOLE, INSERT_PILOT, INSERT_L = 2.6, 2.0, 4.0
SCREW_L, HEAD_D, HEAD_H = 8.0, 2.6, 1.4
DATUM = POGO_RECESS + P.EAR_FACE + P.EAR_T          # ear plate's back, the face it is screwed to
INSERT_TOP = DATUM + 2.0
PILOT_END = DATUM + 7.5

# --- the tube key ---------------------------------------------------------------------------------
KEY_Y0, KEY_Y1 = -29.0, -17.0
KEY_BITE = 0.5                            # into each tube once the tube bears on its bore
KEY_HALF = H + HOLE_Q / 2 - 6.35 + KEY_BITE
KEY_LUG = H + HOLE_D / 2 - 4.0 + KEY_BITE           # down to the drain tube
KEY_CLR = fits.slip
RIBBON_W, RIBBON_T = 4.1, 1.3                       # BNTECHGO 4-conductor, faucet_assembly.cable_*


def _v(x, y, z):
    return cq.Vector(x, y, z)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, _v(x0, y0, z0))


def cyl(d, y0, y1, x=0.0, z=0.0):
    return cq.Solid.makeCylinder(d / 2.0, y1 - y0, _v(x, y0, z), _v(0, 1, 0))


def prism(points, y0, y1):
    """A prism on Y over a closed (x, z) polygon."""
    wire = cq.Wire.makePolygon([_v(x, y0, z) for x, z in points], close=True)
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), _v(0, y1 - y0, 0))


def profile_corners(r, f):
    """The section's tangent points and flat ends: (tx, tz, xf)."""
    tx, tz = r * SIN, r * COS
    return tx, tz, tx - (f - tz) / TAN


def profile_wire(r, f, y):
    """The shared section's outline at y: a circle of radius r with 36-degree planes standing on its
    tangent points top and bottom and a flat at +-f across them."""
    tx, tz, xf = profile_corners(r, f)
    pts = [(tx, -tz), (r, 0.0), (tx, tz), (xf, f), (-xf, f), (-tx, tz), (-r, 0.0), (-tx, -tz),
           (-xf, -f), (xf, -f)]
    p = [_v(x, y, z) for x, z in pts]
    return cq.Wire.assembleEdges([
        cq.Edge.makeThreePointArc(p[0], p[1], p[2]), cq.Edge.makeLine(p[2], p[3]),
        cq.Edge.makeLine(p[3], p[4]), cq.Edge.makeLine(p[4], p[5]),
        cq.Edge.makeThreePointArc(p[5], p[6], p[7]), cq.Edge.makeLine(p[7], p[8]),
        cq.Edge.makeLine(p[8], p[9]), cq.Edge.makeLine(p[9], p[0])])


def profile(r, f, y0, y1):
    """The shared section on Y from y0 to y1. Offsetting it by c is profile(r + c, f + c)."""
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(profile_wire(r, f, y0)), _v(0, y1 - y0, 0))


def teardrop(d, y0, y1, x=0.0, z=0.0, up=1.0):
    """A bore on Y whose crown on the print-up side closes on the same 36-degree planes."""
    r = d / 2.0
    roof = [(x - r * SIN, z + up * r * COS), (x + r * SIN, z + up * r * COS), (x, z + up * r / COS)]
    return cyl(d, y0, y1, x, z).fuse(prism(roof, y0, y1))


def stadium_z(length, width, y0, y1, z=0.0):
    """A slot on end, long axis Z."""
    s = length - width
    return box(-width / 2, width / 2, y0, y1, z - s / 2, z + s / 2).fuse(
        cyl(width, y0, y1, 0, z - s / 2)).fuse(cyl(width, y0, y1, 0, z + s / 2))


def chamfer_ring(d, depth, y, sign, x=0.0, z=0.0):
    """A 45-degree countersink of `depth` on a hole of diameter d, opening at y toward -sign."""
    return cq.Solid.makeCone(d / 2 + depth, d / 2, depth, _v(x, y - sign * 0.001, z), _v(0, sign, 0))


def span(a, b, sign):
    """y from a to b measured into the part: +Y for the socket, -Y for the plug."""
    return min(sign * a, sign * b), max(sign * a, sign * b)


def cut_all(body, tools):
    for t in tools:
        body = body.cut(t)
    return body.clean()


def fuse_all(body, tools):
    for t in tools:
        body = body.fuse(t)
    return body.clean()


# --- shared face features -------------------------------------------------------------------------
def bar_slot_top(face_z_bed):
    """How far the slot's print-up end stands over the bar, so its top lands on a layer boundary
    at least BAR_AIR over the bar. `face_z_bed` is the print height of the bar's centre."""
    top = face_z_bed + BAR / 2
    k = math.ceil((top + BAR_AIR - FIRST_LAYER) / LAYER - 1e-9)
    return FIRST_LAYER + k * LAYER - top


def magnet_slots(sign, up, slot_top):
    """Each bar's slot, open at the face, with a printed rail left in each groove. The print-up end
    stands `slot_top` over the bar: the layer that closes it is the first one printed after the
    pause, and the bar slides down the rails into the closed end."""
    h = BAR / 2 + BAR_CLR
    reach = h - (BAR / 2 - GROOVE_D + RAIL_CLR)
    lo, hi = (-h, BAR / 2 + slot_top) if up > 0 else (-(BAR / 2 + slot_top), h)
    out = []
    for x in (-MAG_X, MAG_X):
        slot = box(x - h, x + h, *span(-0.1, BAR_T + BAR_CLR, sign), lo, hi)
        for side in (-1, 1):
            x0 = x + side * h
            slot = slot.cut(box(min(x0, x0 - side * reach), max(x0, x0 - side * reach),
                                *span(GROOVE_TOP + 0.05, GROOVE_TOP + 0.05 + RAIL_H, sign),
                                lo - 0.1, hi + 0.1))
        out.append(slot)
    return out


def bars(sign):
    """The two SB443-IN bars, pole faces flush with the face."""
    h = BAR / 2
    out = []
    for x in (-MAG_X, MAG_X):
        bar = box(x - h, x + h, *span(0.0, BAR_T, sign), -h, h)
        for side in (-1, 1):
            x0 = x + side * h
            bar = bar.cut(box(min(x0, x0 - side * GROOVE_D), max(x0, x0 - side * GROOVE_D),
                              *span(GROOVE_TOP, GROOVE_TOP + GROOVE_H, sign), -h - 0.1, h + 0.1))
        out.append((x, bar))
    return out


def pogo_cuts(sign, lead_to):
    """The pogo half's seat, recessed POGO_RECESS: nose, ear plate datum, body, the cavity its four
    tails are soldered in, the screw heads' counterbores, the inserts' entries and pilots."""
    w = P.BODY_W + 2 * POGO_CLR
    nose = P.BODY_L + 2 * POGO_CLR
    ear_front = POGO_RECESS + P.EAR_FACE
    body_back = POGO_RECESS + P.BODY_T
    out = [stadium_z(nose, w, *span(-0.1, ear_front, sign)),
           stadium_z(P.EAR_L + 2 * POGO_CLR, w, *span(ear_front, DATUM, sign)),
           stadium_z(nose, w, *span(DATUM, body_back + 0.3, sign)),
           box(-w / 2, w / 2, *span(body_back, lead_to, sign), -5.0, 5.0)]
    for zc in (P.EAR_PITCH / 2, -P.EAR_PITCH / 2):
        out += [cyl(HEAD_D + 0.6, *span(-0.1, ear_front, sign), 0, zc),
                cyl(INSERT_HOLE, *span(DATUM - 0.01, INSERT_TOP, sign), 0, zc),
                cyl(INSERT_PILOT, *span(INSERT_TOP - 0.01, PILOT_END, sign), 0, zc)]
    return out


def pogo_hardware(sign):
    """Inserts and screws, as fitted."""
    out = []
    for zc in (P.EAR_PITCH / 2, -P.EAR_PITCH / 2):
        tag = "top" if zc > 0 else "bottom"
        out.append((f"insert-{tag}", cyl(2.3, *span(INSERT_TOP, INSERT_TOP + INSERT_L, sign), 0, zc)
                    .cut(cyl(1.4, *span(INSERT_TOP - 1, INSERT_TOP + INSERT_L + 1, sign), 0, zc))))
        ear_front = POGO_RECESS + P.EAR_FACE
        screw = cyl(HEAD_D, *span(ear_front - HEAD_H, ear_front, sign), 0, zc).fuse(
            cyl(1.4, *span(ear_front, ear_front + SCREW_L, sign), 0, zc))
        out.append((f"screw-{tag}", screw))
    return out


def pogo_location(sign):
    """The pogo half's frame (face +Z, long axis X) turned on end and set POGO_RECESS into the face."""
    turn = cq.Location(_v(0, 0, 0), _v(0, 1, 0), -90) * \
        cq.Location(_v(0, 0, 0), _v(1, 0, 0), 90 if sign > 0 else -90)
    return cq.Location(_v(0, sign * POGO_RECESS, 0)) * turn


# --- the socket -----------------------------------------------------------------------------------
SOCKET_UP = 1.0                           # prints on its bottom flat, machine +Z up
RETAINER_SCREWS = (15.5, -15.5)           # M3 insert stations on the socket's back face, z
SOCKET_BED = -BODY_F
SOCKET_SLOT_TOP = bar_slot_top(-SOCKET_BED)


def snap_leaves():
    """One leaf each side, cut from the body's wall: free at its hook end, rooted 20 mm into the
    machine. Its hook ramps through back-top's inner bore and catches the wall's inner face."""
    hook_y = WALL_IN + HOOK_CLR
    root_y = hook_y + 20.0
    half, slot, leaf_t, gap, hook = 5.5, 0.8, 1.5, 1.9, 1.6
    cuts, adds = [], []
    for side in (-1, 1):
        x_in = BODY_R - leaf_t - gap
        lo, hi = sorted((side * x_in, side * (BODY_R + 2)))
        cuts.append(box(lo, hi, hook_y - slot, root_y, -half - slot, half + slot))
        lo, hi = sorted((side * (BODY_R - leaf_t), side * (BODY_R + 2)))
        leaf = profile(BODY_R, BODY_F, hook_y, root_y + 0.01).intersect(
            box(lo, hi, hook_y, root_y + 0.01, -half, half))
        tip = BODY_R + hook
        x_base = BODY_R - leaf_t + 0.4
        hook_pts = [(x_base, hook_y), (tip, hook_y), (tip, hook_y + 0.6), (x_base, hook_y + 0.6 + (tip - x_base) / TAN)]
        hk = cq.Workplane("XY").polyline([(side * x, y) for x, y in hook_pts]).close().extrude(2 * half) \
            .translate((0, 0, -half)).val()
        adds += [leaf, hk]
    return cuts, adds


def socket():
    body = profile(FLANGE_R, BODY_F, FACE, LEDGE).fuse(profile(BODY_R, BODY_F, LEDGE - 0.01, REAR)).clean()
    cuts, adds = snap_leaves()
    body = fuse_all(cut_all(body, cuts), adds)
    c = CUP_CLR
    tools = [profile(PLUG_R + c, PLUG_F + c, FACE - 0.1, 0.0),
             cq.Solid.makeLoft([profile_wire(PLUG_R + c + 1.0, PLUG_F + c + 1.0, FACE - 0.001),
                                profile_wire(PLUG_R + c, PLUG_F + c, FACE + 1.0)])]       # 1 mm lead-in
    tools += magnet_slots(+1, SOCKET_UP, SOCKET_SLOT_TOP)
    tools += pogo_cuts(+1, RELEASE - 2.0)
    for name, (x, z, od) in PORTS.items():
        if od > 5:
            tools += [teardrop(HOLE_Q, -0.1, RELEASE + 0.01, x, z, SOCKET_UP),
                      chamfer_ring(HOLE_Q, 0.6, 0.0, +1, x, z),
                      teardrop(U.COLLET_D + 2 * 0.15, RELEASE, RING_FROM + 0.01, x, z, SOCKET_UP),
                      teardrop(U.RING_D + 2 * HOLE_CLR, RING_FROM, REAR + 0.1, x, z, SOCKET_UP)]
        else:
            tools += [teardrop(HOLE_D, -0.1, RELEASE + 0.01, x, z, SOCKET_UP),
                      chamfer_ring(HOLE_D, 0.5, 0.0, +1, x, z),
                      teardrop(D_RING + 2 * HOLE_CLR, RELEASE, REAR + 0.1, x, z, SOCKET_UP)]
    tools.append(teardrop(5.0, RELEASE - 2.5, REAR + 0.1, 0, 0, SOCKET_UP))       # pogo leads
    for zc in RETAINER_SCREWS:
        tools.append(teardrop(4.0, REAR - 8.0, REAR + 0.1, 0, zc, SOCKET_UP))     # M3 insert pockets
    return cut_all(body, tools)


def retainer():
    """Bears on the three 1/4" unions' back ring faces and, through a boss, the drain union's;
    the rear collets and the pogo leads pass. Two M3 x 8 socket-head screws into RX-M3x5.7 inserts."""
    plate = profile(BODY_R - 0.5, BODY_F - 0.5, REAR, REAR + RETAINER_T)
    x, z, _ = PORTS["drain"]
    boss = cyl(D_RING - 0.8, DRAIN_STOP, REAR + 0.01, x, z)
    body = plate.fuse(boss).clean()
    tools = [cyl(5.0, REAR - 1, REAR + RETAINER_T + 1)]
    for name, (x, z, od) in PORTS.items():
        d = U.COLLET_D + 0.7 if od > 5 else D_REAR_PASS
        tools.append(cyl(d, DRAIN_STOP - 1 if od < 5 else REAR - 1, REAR + RETAINER_T + 1, x, z))
    for zc in RETAINER_SCREWS:
        tools += [cyl(3.4, REAR - 1, REAR + RETAINER_T + 1, 0, zc),
                  cyl(6.2, REAR + RETAINER_T - 3.2, REAR + RETAINER_T + 1, 0, zc)]
    return cut_all(body, tools)


# --- the plug -------------------------------------------------------------------------------------
PLUG_UP = -1.0                            # prints upside down on its top flat, machine -Z up
PLUG_BED = PLUG_F
PLUG_SLOT_TOP = bar_slot_top(PLUG_BED)
RIBBON_TOP = (11.7, 11.7 + RIBBON_T + 0.5)          # channel under the top flat, z
RIBBON_DROP = (-15.0, -11.4)                         # y where it drops to the pogo's tails


def plug():
    front = cq.Solid.makeLoft([profile_wire(PLUG_R, PLUG_F, -0.8), profile_wire(PLUG_R - 0.8, PLUG_F - 0.8, 0.0)])
    rear = cq.Solid.makeLoft([profile_wire(PLUG_R - 1.0, PLUG_F - 1.0, -PLUG_L), profile_wire(PLUG_R, PLUG_F, -PLUG_L + 1.0)])
    body = profile(PLUG_R, PLUG_F, -PLUG_L + 1.0 - 0.01, -0.8 + 0.01).fuse(front).fuse(rear).clean()
    tools = magnet_slots(-1, PLUG_UP, PLUG_SLOT_TOP)
    tools += pogo_cuts(-1, -RIBBON_DROP[1])
    for name, (x, z, od) in PORTS.items():
        tools.append(teardrop(HOLE_Q if od > 5 else HOLE_D, -PLUG_L - 0.1, 0.1, x, z, PLUG_UP))
    w = RIBBON_W + 0.9
    tools += [box(-w / 2, w / 2, -PLUG_L - 0.1, RIBBON_DROP[1], *RIBBON_TOP),
              box(-w / 2, w / 2, RIBBON_DROP[0], RIBBON_DROP[1] + 0.01, -5.0, RIBBON_TOP[1])]
    tools += key_slot()
    return cut_all(body, tools)


def key_slot():
    c = KEY_CLR
    x, z, _ = PORTS["drain"]
    return [box(-PLUG_R - 1, PLUG_R + 1, KEY_Y0 - c, KEY_Y1 + c, -KEY_HALF - c, KEY_HALF + c),
            box(x - 2.6 - c, PLUG_R + 1, KEY_Y0 - c, KEY_Y1 + c, -KEY_LUG - c, -KEY_HALF + 0.01)]


def key():
    """One bar across the plug between the tube rows, flush with its sides. It goes in from the
    drain side and bites KEY_BITE into each tube; its lug reaches down to the 4 mm drain tube."""
    x, z, _ = PORTS["drain"]
    bar = box(-PLUG_R - 1, PLUG_R + 1, KEY_Y0, KEY_Y1, -KEY_HALF, KEY_HALF)
    bar = bar.fuse(box(x - 2.6, x + 2.6, KEY_Y0, KEY_Y1, -KEY_LUG, -KEY_HALF + 0.01)).clean()
    bar = bar.intersect(profile(PLUG_R, PLUG_F, KEY_Y0 - 1, KEY_Y1 + 1))
    # lead-ins: 0.6 off each face over the 3 mm that enter first (-X), and the lug's leading edge
    x0 = -math.sqrt(PLUG_R ** 2 - KEY_HALF ** 2)
    lead = [prism([(x0 - 1, s * (KEY_HALF - 0.8)), (x0 + 3.0, s * KEY_HALF), (x0 + 3.0, s * (KEY_HALF + 1)),
                   (x0 - 1, s * (KEY_HALF + 1))], KEY_Y0 - 1, KEY_Y1 + 1) for s in (1, -1)]
    lug_x = x - 2.6
    lead.append(prism([(lug_x - 0.1, -KEY_LUG - 0.1), (lug_x + 1.0, -KEY_LUG - 0.1), (lug_x - 0.1, -KEY_LUG + 1.0)],
                      KEY_Y0 - 1, KEY_Y1 + 1))
    return cut_all(bar, lead)


# --- back-top, as a coupon ------------------------------------------------------------------------
def wall_hole(y0, y1):
    """The stepped hole back-top would take: the flange's section for FLANGE_T, the body's through
    the rest. Both close on the section's own 36-degree planes, so the wall prints without support."""
    return [profile(FLANGE_R + HOLE_CLR, BODY_F + HOLE_CLR, y0 - 0.1, LEDGE),
            profile(BODY_R + HOLE_CLR, BODY_F + HOLE_CLR, LEDGE - 0.01, y1 + 0.1)]


def coupon():
    """84 x 68 of 6 mm wall with the hole, on a foot along its machine-top edge: it prints standing
    roof-down, as back-top does."""
    wall = box(-42, 42, FACE, WALL_IN, -34, 34)
    foot = box(-42, 42, FACE - 12, WALL_IN + 12, 31, 34)
    return cut_all(wall.fuse(foot).clean(), wall_hole(FACE, WALL_IN))


def wall_patch():
    """A patch of back-top for the scenes."""
    return cut_all(box(-45, 45, FACE, WALL_IN, -38, 38), wall_hole(FACE, WALL_IN))


# --- unions as fitted -----------------------------------------------------------------------------
def auc44m(x, z, collet_face, proud=1.8):
    """neoFit AUC44M envelope at its station, collet face `collet_face`: Ø13.2 ring bodies, a short
    waist, collet sleeves `proud` proud (not dimensioned; drawn for the picture)."""
    y0 = collet_face
    parts = [cyl(8.0, y0, y0 + proud, x, z), cyl(D_RING, y0 + proud, y0 + D_END, x, z),
             cyl(9.0, y0 + D_END, y0 + D_L - D_END, x, z), cyl(D_RING, y0 + D_L - D_END, y0 + D_L - proud, x, z),
             cyl(8.0, y0 + D_L - proud, y0 + D_L, x, z)]
    s = fuse_all(parts[0], parts[1:])
    return s.cut(cyl(4.0, y0 - 1, y0 + D_L + 1, x, z))


def union_location(x, z, collet_face):
    """jg_pp0408w's frame (axis Z, origin at its mid-plane) turned onto Y, the collet facing the
    floor at `collet_face`."""
    mid = collet_face + U.OVERALL / 2
    return cq.Location(_v(x, mid, z), _v(1, 0, 0), 90)
