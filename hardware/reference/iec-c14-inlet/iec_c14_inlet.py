"""Reference solid of an IEC 60320 C14 panel-mount AC power inlet — the two-screw
male appliance inlet, 40 mm screw pitch. BOM: MXR IEC 60320 C14 panel-mount AC
inlet, 10 A / 250 VAC (Amazon B07DCXKNXQ); rear-wall mains inlet that accepts a
standard NEMA 5-15P-to-C13 line cord. Moulded "AC-04" on its face.

One moulded body: a LOZENGE FLANGE with a screw ear at each end, and one keyed
COLUMN through it — barely proud on the mating face, where the recess the C13
cordset enters is sunk into it and the three flat male blades stand, and long on
the wiring face, where it carries the quick-connect spade terminals into the
machine. The column's section is the same read from either side, and so is the
45 deg key cut into it.

Calipered (the part on the bench)
---------------------------------
  FLANGE_W 49.77 x FLANGE_H 22.17 — tip to tip through the ears, and across the
      two flats. The ear is a round of half the difference from the pitch
      (`EAR_R`), struck on the screw itself, so 40 + 2 x 4.885 is the length.
  BODY_W 26.46 x BODY_H 18.18 — the moulded column that passes through the
      flange, the same section read from either face. It is the widest thing
      outboard of the seating plane, so a cutout is cut to it, and the flange
      is left 1.995 mm of bearing either side.
  EAR_SPAN 17.98 — across one ear, from the round where the full-width flat
      gives way to the taper, to the round where the far taper meets that ear.
      The taper's own 12.15 mm lies inside it, and the reading is what fixes the
      run of the flat — see `_flat_run_for`.
  7.04 IS NOT IN THIS FILE. It is calipered off the same part and its two loci
      are not yet known, so nothing here is struck on it — a figure wired into
      geometry on a guess at what it spans is worse than one left out.
  SCREW_PITCH 40.0 — both screws ON the mating axis, one either side of the hole.

Estimated off the same photographs (rounding, and what nothing bears on)
------------------------------------------------------------------------
  FLANGE_T, FLANGE_FLAT_W and the corner radii; SHROUD_PROUD, CAVITY_DEPTH,
  BODY_REACH and the blade layout; the Faston stubs. Each is marked at its own
  constant.

Coordinate convention
----------------------
Matches jg_bulkhead_union.py.
  Y = insertion / mating axis. +Y = OUTWARD (toward the outside of the
      enclosure, where the C13 line cord plugs in — the male blades face
      +Y). -Y = INWARD (the housing and spade terminals reach into the
      enclosure).
  Origin = the panel-seating plane = the outboard face of the flange, which
      bears on the INSIDE of the +Y wall of back-top. The boss and its blades
      reach out through the cutout at y >= 0; the flange, the housing and the
      terminals sit at y < 0, inside the enclosure.
  +Z = up. X completes the right-handed frame. The flange's long axis (49.77)
      is along X; its short axis (22.17) is along Z.

Note on the sketch plane: on the raw cq.Workplane(xz_plane_y_up), local +y
maps to world -Z (chirality inversion documented in world_workplane.py), so
the earth blade is placed at local -y to land at world +Z (top).

Run:
    tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/iec_c14_inlet.py
    tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/iec_c14_inlet.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import C_C14, one_body  # noqa: E402
from world_workplane import xz_plane_y_up  # noqa: E402

STEP = _here.parent / "iec-c14-inlet.step"


# --- CALIPERED: the flange, and where a panel drills for it ----------------
FLANGE_W = 49.77     # X, tip to tip through the two screw ears
FLANGE_H = 22.17     # Z, across the two flats
SCREW_PITCH = 40.0   # X, centre to centre; both screws on the cutout's own Z centreline
EAR_R = (FLANGE_W - SCREW_PITCH) / 2.0   # 4.885 — the ear is a round on its screw

# THE TAPER IS THE TANGENT the outline draws from the full-width flat onto the ear's round, so
# the run of that flat is the only figure the outline needs beyond the extents. It is not typed:
# `EAR_SPAN` is calipered across the ear — from the round where the flat gives way to the taper,
# to the round where the far taper meets the ear — and the taper's own 12.15 mm lies inside it.
# `_flat_run_for` is what turns that reading back into the run.
EAR_SPAN = 17.98
FLANGE_KNUCKLE = 1.0
FLANGE_T = 5.0       # ESTIMATED. Y, the flange's own thickness
SCREW_D = 3.5        # ESTIMATED. clearance hole for the M3 that holds it

# --- CALIPERED: the moulded body, and the 45 deg key cut into it -----------
# THE BODY IS ONE COLUMN THROUGH THE FLANGE, standing out on the mating face and in on the
# wiring face, and its section is the same read from either side. That section is a rectangle
# with every corner cut back at 45 deg, and the two flats those cuts leave are what the
# calipers take — which is why both figures read the same from either face.
BODY_W = 26.46       # X — the column, mating side and wiring side alike
BODY_H = 18.18       # Z — the widest section outboard of the seating plane, so what a cutout
                     #     is cut to, with 1.995 mm of flange bearing either side of it
KEY = 4.24           # ESTIMATED. the 45 deg cut on each corner of that section
CAVITY_H = 15.52     # ESTIMATED. the recess across the short axis
SHROUD_T = (BODY_H - CAVITY_H) / 2.0        # 1.33 — the wall the two leave between them
CAVITY_W = BODY_W - 2.0 * SHROUD_T          # 23.80
BODY_R = 1.0         # ESTIMATED. round on every corner of that outline

# --- ESTIMATED: how far the column stands either way of the seating plane --
# The mating face is very nearly the flange's own: this receptacle sinks its recess into the
# body rather than standing a shroud off the panel, and a C13 lands on the flange.
SHROUD_PROUD = 1.0   # ESTIMATED. Y, the column outboard of the seating plane
CAVITY_DEPTH = 9.0   # ESTIMATED. Y, recess floor below the mating face
BODY_REACH = 19.8    # ESTIMATED. Y, seating plane to the housing's back face, terminals aside

# --- Male blades (mate with the C13 cordset) — ESTIMATED, IEC 60320-1 sheet C14
BLADE_W = 4.0        # X
BLADE_T = 1.0        # Z thickness
BLADE_PROUD = 5.0    # Y projection from the cavity floor toward +Y
LN_SPACING = 14.0    # line<->neutral center spacing along X
EARTH_OFFSET_Z = 8.0  # earth blade above the L/N line (world +Z)

TAB_W = 4.8          # ESTIMATED. X, Faston quick-connect spade
TAB_T = 0.8          # ESTIMATED. Z
TAB_PROUD = 6.0      # ESTIMATED. Y, behind the housing back face

# Seating planes along Y.
shroud_rim_y = SHROUD_PROUD                       # outer face of the boss, out through the hole
cavity_floor_y = shroud_rim_y - CAVITY_DEPTH      # floor the blades stand on
flange_back_y = -FLANGE_T                          # the flange's inboard face
body_back_y = -BODY_REACH                          # housing back face, where the tabs start


# --- What a panel owes this receptacle --------------------------------------
# A screw-mount C14 asks a panel for three things: a CUTOUT its boss reaches out through,
# two SCREW STATIONS that hold it there, and the FACE ROOM its flange takes on the inside
# once it is in. A field spaced to the cutout fouls on the flange, which is the widest of
# the three.
#   All three are symmetric about the mating axis: the cutout is centred on it and both
# screws sit on it. So a panel places one station and the three follow.


def panel_cutout() -> tuple:
    """`(width, height, corner radius)` of the axis-centred rounded rectangle the boss
    reaches out through. The keyed corners are inside this rectangle, so a panel cuts the
    rectangle and the key rides free of it."""
    return (BODY_W, BODY_H, BODY_R)


def panel_screws() -> tuple:
    """The two screw stations in the panel plane, as `(x, z)` off the cutout's own centre.
    Both sit ON the mating axis, one either side of the hole."""
    return ((-SCREW_PITCH / 2.0, 0.0), (SCREW_PITCH / 2.0, 0.0))


def panel_footprint() -> tuple:
    """`(width, height)` the receptacle takes on the panel face, seen down the mating axis —
    what crowds a neighbour, a wall or a ceiling. The flange is the widest section, and it
    bears on the panel's INNER face."""
    return (FLANGE_W, FLANGE_H)


def panel_stack() -> tuple:
    """`(outboard, inboard)` of the seating plane. The first is all the panel and whatever
    it carries may take before the cordset stops landing on the boss; the second is the room
    the part asks for behind that plane, terminals aside."""
    return (SHROUD_PROUD, BODY_REACH)


def stations_hold():
    """Hold the calipered panel figures to `iec-c14-inlet.step` — the file the enclosure
    seats through its wall, while it cuts and drills off these live figures.

    The face footprint is the flange's own outline, an extent of that solid's box either
    way. Against the cutout: what stands outboard of the seating plane clears it, the
    flange covers it, and both screws land in flange and miss it."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    face_w, face_h = panel_footprint()
    for what, claimed, actual in (("face width", face_w, bb.xlen),
                                  ("face height", face_h, bb.zlen)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"iec-c14-inlet {what} is {claimed:g} and {STEP.name} carries {actual:.4f} — "
                f"a panel field spaced to this figure is spaced to a body that is not there.")
    cut_w, cut_h, _r = panel_cutout()
    # Everything standing OUTBOARD of the seating plane is what reaches through the hole.
    out = cq.Solid.makeBox(bb.xlen + 2, bb.ymax + 1, bb.zlen + 2,
                           cq.Vector(bb.xmin - 1, 1e-3, bb.zmin - 1))
    ob = solid.intersect(out).BoundingBox()
    for what, thru, hole in (("width", ob.xlen, cut_w), ("height", ob.zlen, cut_h)):
        if thru > hole + 1e-6:
            raise ValueError(
                f"iec-c14-inlet reaches {thru:.4f} through the panel in {what} and the "
                f"calipered cutout is {hole:g} — the part does not pass its own hole.")
    for what, cover, hole in (("width", face_w, cut_w), ("height", face_h, cut_h)):
        if cover <= hole + 1e-6:
            raise ValueError(
                f"the cutout is {hole:g} in {what} and the flange {cover:g} — the flange no "
                f"longer covers the hole it is meant to bear around.")
    # Each screw has to land in flange material and miss the hole it stands beside.
    for sx, sz in panel_screws():
        if abs(sx) + SCREW_D / 2.0 > face_w / 2.0 or abs(sz) + SCREW_D / 2.0 > face_h / 2.0:
            raise ValueError(
                f"the screw at ({sx:g}, {sz:g}) reaches past the {face_w:g} x {face_h:g} "
                f"flange — there is no moulding there to drive into.")
        if abs(sx) - SCREW_D / 2.0 < cut_w / 2.0 and abs(sz) - SCREW_D / 2.0 < cut_h / 2.0:
            raise ValueError(
                f"the screw at ({sx:g}, {sz:g}) breaks into the {cut_w:g} x {cut_h:g} "
                f"cutout — a boss there stands in the hole the boss comes through.")
    outboard, inboard = panel_stack()
    if abs(ob.ymax - outboard) > 1e-6 or abs(bb.ymin + inboard + TAB_PROUD) > 1e-6:
        raise ValueError(
            f"`panel_stack` states {outboard:g} out and {inboard:g} in, and {STEP.name} "
            f"carries {ob.ymax:.4f} out and {-bb.ymin - TAB_PROUD:.4f} in — a wall spaced to "
            f"the stated stack is spaced to a part that is not there.")


# --- outlines ---------------------------------------------------------------
# THE TWO PROFILES THIS PART IS DRAWN FROM, each struck one round INSIDE its stated size
# and offset back out, so every corner of the result carries that round and the stated
# figure is the outline's own extent.


def _tangent(half_run, half_height, ear_x, ear_r):
    """Where the hull's straight taper touches the ear's round, as `(x, z)`."""
    dx, dz = ear_x - half_run, -half_height
    span = math.hypot(dx, dz)
    if ear_r >= span:
        raise ValueError(
            f"an ear of {ear_r:g} swallows the corner {span:.3f} away it is meant to tangent "
            f"from — there is no taper left between flat and ear.")
    heading = math.atan2(dz, dx) + math.pi - math.acos(ear_r / span)
    return ear_x + ear_r * math.cos(heading), ear_r * math.sin(heading)


def _ear_span(flat_run):
    """What a caliper reads across one ear on a flange with this flat: the two rounds the jaws
    land on are where the flat gives way to the taper on one side, and where the far taper meets
    the ear on the other, so the whole taper lies between them."""
    a, hz = flat_run / 2.0, FLANGE_H / 2.0 - FLANGE_KNUCKLE
    tx, tz = _tangent(a, hz, SCREW_PITCH / 2.0, EAR_R - FLANGE_KNUCKLE)
    vx, vz = tx - a, tz - hz
    length = math.hypot(vx, vz)
    nx, nz = -vz / length, vx / length                      # the taper's outward normal
    sx, sz = a + FLANGE_KNUCKLE * nx, hz + FLANGE_KNUCKLE * nz
    ex, ez = tx + FLANGE_KNUCKLE * nx, tz + FLANGE_KNUCKLE * nz
    return math.hypot(ex - sx, ez + sz)


def _flat_run_for(span, lo=8.0, hi=40.0):
    """The flat run whose ear reads `span`. Monotone in between, so a bisection settles it."""
    for _ in range(80):
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if _ear_span(mid) > span else (lo, mid)
    return lo


FLANGE_FLAT_W = _flat_run_for(EAR_SPAN)     # 24.378


def _hull_outline(wp, half_run, half_height, ear_x, ear_r):
    """The flange's lozenge: two flats `2 * half_height` apart running `2 * half_run`, a
    round of `ear_r` on each screw at `+/-ear_x`, and the tangent the hull draws between
    them."""
    tx, tz = _tangent(half_run, half_height, ear_x, ear_r)
    return (wp.moveTo(-half_run, half_height).lineTo(half_run, half_height).lineTo(tx, tz)
              .threePointArc((ear_x + ear_r, 0.0), (tx, -tz))
              .lineTo(half_run, -half_height).lineTo(-half_run, -half_height).lineTo(-tx, -tz)
              .threePointArc((-(ear_x + ear_r), 0.0), (-tx, tz))
              .close())


def _keyed_outline(wp, width, height, key):
    """The C13/C14 section: a rectangle with every corner cut back at 45 deg. One `KEY` answers for
    the column and for the recess inside it."""
    hw, hh = width / 2.0, height / 2.0
    return (wp.moveTo(-(hw - key), hh).lineTo(hw - key, hh)
              .lineTo(hw, hh - key).lineTo(hw, -(hh - key))
              .lineTo(hw - key, -hh).lineTo(-(hw - key), -hh)
              .lineTo(-hw, -(hh - key)).lineTo(-hw, hh - key)
              .close())


def _plane(offset):
    return cq.Workplane(xz_plane_y_up).workplane(offset=offset)


def _flange_prism(radius, offset, length):
    """The lozenge struck `radius` under size and offset back out, extruded `length` from
    `offset` — every corner of the result carrying `radius`."""
    return (_hull_outline(_plane(offset),
                          FLANGE_FLAT_W / 2.0, FLANGE_H / 2.0 - radius,
                          SCREW_PITCH / 2.0, EAR_R - radius)
            .offset2D(radius, kind="arc").extrude(length))


def _keyed_prism(width, height, key, radius, offset, length):
    """The same for a keyed section."""
    return (_keyed_outline(_plane(offset),
                           width - 2 * radius, height - 2 * radius, key - radius)
            .offset2D(radius, kind="arc").extrude(length))


def build_flange():
    """The lozenge, `flange_back_y` to 0, bearing on the panel's inner face and bored for
    the two screws that hold it there."""
    flange = _flange_prism(FLANGE_KNUCKLE, flange_back_y, FLANGE_T)
    for sx, sz in panel_screws():
        bore = (cq.Workplane(xz_plane_y_up)
                .workplane(offset=flange_back_y)
                .center(sx, -sz)                  # local +y -> world -Z
                .circle(SCREW_D / 2.0)
                .extrude(FLANGE_T))
        flange = flange.cut(bore)
    return flange


def build_shroud():
    """The keyed column standing outboard of the seating plane (0 -> `shroud_rim_y`), which is
    the whole of what reaches through a panel."""
    return _keyed_prism(BODY_W, BODY_H, KEY, BODY_R, 0.0, SHROUD_PROUD)


def build_cavity():
    """The recess the C13 enters, sunk back from the mating face into the column — past the
    flange and on into the housing, which is where a C13's blade engagement is."""
    return _keyed_prism(CAVITY_W, CAVITY_H, KEY, BODY_R, shroud_rim_y, -CAVITY_DEPTH)


def build_blades():
    """The three flat male blades standing on the cavity floor, projecting +Y.
    Line/neutral on a horizontal line `LN_SPACING` apart; earth centred above (world +Z ->
    local -y on this plane)."""
    blades = None
    ln_z_local = EARTH_OFFSET_Z / 2.0   # local +y -> world -Z: L/N below centre
    for sx in (-1.0, 1.0):
        b = (cq.Workplane(xz_plane_y_up)
             .workplane(offset=cavity_floor_y)
             .center(sx * LN_SPACING / 2.0, ln_z_local)
             .rect(BLADE_W, BLADE_T)
             .extrude(BLADE_PROUD))
        blades = b if blades is None else blades.union(b)
    earth = (cq.Workplane(xz_plane_y_up)
             .workplane(offset=cavity_floor_y)
             .center(0.0, ln_z_local - EARTH_OFFSET_Z)
             .rect(BLADE_T, BLADE_W)   # earth blade oriented vertically (taller)
             .extrude(BLADE_PROUD))
    return blades.union(earth)


def build_body():
    """The moulded housing behind the flange (`flange_back_y` -> `body_back_y`), standing in
    the enclosure with the terminals on its back face."""
    return _keyed_prism(BODY_W, BODY_H, KEY, BODY_R,
                        flange_back_y, body_back_y - flange_back_y)


def build_terminals():
    """Three Faston quick-connect spade tabs projecting -Y from the housing back face, on
    the same X/Z layout as the blades."""
    tabs = None
    ln_z_local = EARTH_OFFSET_Z / 2.0
    for sx in (-1.0, 1.0):
        t = (cq.Workplane(xz_plane_y_up)
             .workplane(offset=body_back_y)
             .center(sx * LN_SPACING / 2.0, ln_z_local)
             .rect(TAB_W, TAB_T)
             .extrude(-TAB_PROUD))
        tabs = t if tabs is None else tabs.union(t)
    earth = (cq.Workplane(xz_plane_y_up)
             .workplane(offset=body_back_y)
             .center(0.0, ln_z_local - EARTH_OFFSET_Z)
             .rect(TAB_T, TAB_W)
             .extrude(-TAB_PROUD))
    return tabs.union(earth)


def build_iec_c14_inlet():
    """The inlet as a single solid wrapped in a cq.Workplane."""
    return (
        build_flange()
        .union(build_shroud())
        .union(build_body())
        .cut(build_cavity())
        .union(build_blades())
        .union(build_terminals())
    )


def selftest() -> int:
    """The receptacle against the figures calipered off it."""
    fails = []
    if abs(SCREW_PITCH + 2 * EAR_R - FLANGE_W) > 1e-9:
        fails.append(
            f"the ears are Ø{2 * EAR_R:.3f} on a {SCREW_PITCH:g} pitch and the flange is "
            f"{FLANGE_W:g} long — the tip is not the ear's own outer point.")
    if BODY_H >= FLANGE_H:
        fails.append(
            f"the body is {BODY_H:g} across and the flange {FLANGE_H:g} — the flange has "
            f"no bearing left either side of the hole it covers.")
    if KEY > min(CAVITY_W, CAVITY_H) / 2.0:
        fails.append(f"a {KEY:g} key cuts past the middle of the {CAVITY_W:g} x "
                     f"{CAVITY_H:g} recess it is also cut into")
    if CAVITY_DEPTH >= SHROUD_PROUD + BODY_REACH:
        fails.append(
            f"the recess is {CAVITY_DEPTH:g} deep and the column runs "
            f"{SHROUD_PROUD + BODY_REACH:g} — its floor is out the back of the housing.")
    if abs(_ear_span(FLANGE_FLAT_W) - EAR_SPAN) > 1e-6:
        fails.append(
            f"the flat runs {FLANGE_FLAT_W:.4f} and reads {_ear_span(FLANGE_FLAT_W):.4f} across "
            f"the ear, and the calipers read {EAR_SPAN:g}")
    if FLANGE_FLAT_W / 2.0 >= SCREW_PITCH / 2.0 - EAR_R:
        fails.append(
            f"the flat runs to x {FLANGE_FLAT_W / 2.0:g} and the ear starts at "
            f"{SCREW_PITCH / 2.0 - EAR_R:g} — there is no taper between them.")
    try:
        stations_hold()
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  iec-c14-inlet AC-04  flange {FLANGE_W:g} x {FLANGE_H:g}, "
              f"flat {FLANGE_FLAT_W:.3f} off a {EAR_SPAN:g} ear span, "
              f"body {BODY_W:g} x {BODY_H:g}, "
              f"{BODY_REACH:g} in, screws {SCREW_PITCH:g} apart")
    return 1 if fails else 0


def main():
    part = build_iec_c14_inlet()
    bb = part.val().BoundingBox()
    print("IEC 60320 C14 panel-mount AC inlet — two-screw, 40 mm pitch (MXR B07DCXKNXQ)")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Extents: X {bb.xlen:.2f}  Y {bb.ylen:.2f}  Z {bb.zlen:.2f}")
    print(f"  Proud of seating face (outward): {bb.ymax:.2f} mm")
    print(f"  Into enclosure (inward): {bb.ymin:.2f} mm")
    print(f"  Flange {FLANGE_W} x {FLANGE_H} / body {BODY_W} x {BODY_H}, key {KEY:.2f}")
    print(f"  Solid valid: {part.val().isValid()}")
    export_assembly(one_body(part, "iec-c14-inlet", C_C14), str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
