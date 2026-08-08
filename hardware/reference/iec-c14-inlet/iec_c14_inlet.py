"""Reference solid of an IEC 60320 C14 panel-mount AC power inlet — the
two-screw male appliance inlet, 40 mm screw pitch. BOM: MXR IEC 60320 C14
panel-mount AC inlet, 10 A / 250 VAC (Amazon B07DCXKNXQ); rear-wall mains
inlet that accepts a standard NEMA 5-15P-to-C13 line cord.

A single molded body: a rounded-corner flange that bears on the panel's
INSIDE face and carries the two screw holes, a recessed shroud that reaches
out through the cutout holding the three flat male blades (line, neutral,
earth) that mate with the C13 cordset, and a deeper housing carrying the
quick-connect spade terminals into the enclosure.

Two kinds of figure live here. The ones a PANEL is cut and drilled to are
CALIPERED off the part on the bench. The ones that only describe the part's
own moulding are datasheet generics, marked as such.

Calipered (the part on the bench)
---------------------------------
  Panel cutout: 30.95 W x 22.15 H, corner radius 3.0 — a rounded rectangle,
      not the notched snap-in rectangle. The whole shroud passes through it.
  Mounting: two screws, 40.0 mm apart, centred on the cutout's own 22.15 mm
      axis — so both sit ON the mating axis, one either side of the hole.
      The inlet lands from INSIDE the panel: its flange bears on the inner
      face, the screws drive from inside, and each heat-set therefore takes
      its insert flush with the INNER wall face with the boss standing proud
      OUTWARD. A boss standing inward would foul the flange it is holding.

Generic (datasheet consensus — awaiting calipers)
-------------------------------------------------
  Front flange: its two dimensions come off the calipered screw pitch and
      cutout plus what an M3 takes. See FLANGE_W / FLANGE_H.
  Recessed shroud on the outside face: ~16 W x ~13 H opening, ~9 deep,
      with the three blades projecting toward +Y inside it.
  Male blades: IEC flat blades ~4.0 W x 1.0 thick. Line + neutral on a
      horizontal line 14 mm apart; earth blade centered above, offset ~8 mm
      up. Faston quick-connect tabs behind the panel are 4.8 x 0.8 mm.
  Body depth behind the panel face: ~27 mm overall housing + terminal
      stubs (Amazon C14 listing total ~49.7 mm minus the bezel/shroud).

Sources for the generics: Mouser IEC-connector spec drawing, Interpower C14
inlet note, Jameco IEC 320-C14 receptacle, Panel Components Corp, RS PRO C14
datasheet — all IEC 60320-1 sheet C14.

Coordinate convention
----------------------
Matches jg_bulkhead_union.py.
  Y = insertion / mating axis. +Y = OUTWARD (toward the outside of the
      enclosure, where the C13 line cord plugs in — the male blades face
      +Y). -Y = INWARD (the housing and spade terminals reach into the
      enclosure).
  Origin = the panel-seating plane = the front face of the flange, which
      bears on the INSIDE of the rear wall. The shroud and its blades reach
      out through the cutout at y >= 0; the flange, the housing and the
      terminals sit at y < 0, inside the enclosure.
  +Z = up. X completes the right-handed frame. The cutout long axis
      (width 30.95) is along X; the short axis (22.15) is along Z.

Note on the sketch plane: on the raw cq.Workplane(xz_plane_y_up), local +y
maps to world -Z (chirality inversion documented in world_workplane.py), so
the earth blade is placed at local -y to land at world +Z (top).

Run:
    tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/iec_c14_inlet.py
"""

import sys
import cadquery as cq
from pathlib import Path


_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)
from _cadq_export import export_step
from world_workplane import xz_plane_y_up

STEP = _here.parent / "iec-c14-inlet.step"


# --- CALIPERED: what a panel is cut and drilled to ------------------------
# The rounded rectangle the shroud passes through, and the two screws that hold the
# inlet against the panel's INNER face. Everything a printed wall does for this part
# comes off these four numbers.
CUTOUT_W = 30.95     # X
CUTOUT_H = 22.15     # Z
CUTOUT_R = 3.0       # corner radius of that rectangle
SCREW_PITCH = 40.0   # X, centre to centre; both screws on the cutout's own Z centreline
SCREW_D = 3.0        # M3

# --- Front flange, bearing on the panel's INNER face ----------------------
# It reaches past both screws with moulding around each, and overhangs the cutout it
# covers. Both dimensions are the calipered figures plus what an M3 takes.
FLANGE_EAR = SCREW_D / 2.0 + 2.0     # moulding around a screw hole, edge to centre
FLANGE_W = SCREW_PITCH + 2.0 * FLANGE_EAR       # X — reaches past both screws
FLANGE_H = CUTOUT_H + 2.0 * FLANGE_EAR          # Z — overhangs the cutout it covers
FLANGE_T = 2.0       # Y, proud of the seating face
FLANGE_FILLET = 2.5  # rounded flange corners

# --- Shroud: the recessed cavity on the outside face that the C13 plug
#     enters, with the three male blades standing inside it ---------------
SHROUD_W = 24.0      # X, outer wall of the raised shroud ring
SHROUD_H = 18.0      # Z
SHROUD_T = 1.6       # ring wall thickness
SHROUD_PROUD = 9.0   # Y, how far the shroud ring rises past the bezel face
CAVITY_W = SHROUD_W - 2 * SHROUD_T   # recessed opening the plug enters
CAVITY_H = SHROUD_H - 2 * SHROUD_T
CAVITY_DEPTH = 8.0   # Y, how far the cavity floor sits below the shroud rim
SHROUD_FILLET = 1.5

# --- Male blades (mate with the C13 cordset) ------------------------------
BLADE_W = 4.0        # X
BLADE_T = 1.0        # Z thickness
BLADE_PROUD = 7.0    # Y projection from the cavity floor toward +Y
LN_SPACING = 14.0    # line<->neutral center spacing along X
EARTH_OFFSET_Z = 8.0  # earth blade above the L/N line (world +Z)

# --- Housing behind the panel + quick-connect terminal stubs -------------
# GENERIC. The inlet lands from inside, so this housing stands in the enclosure and
# passes through nothing — the cutout owes it no clearance.
BODY_W = 27.5        # X
BODY_H = 20.5        # Z
BODY_DEPTH = 22.0    # Y, molded housing into the enclosure
BODY_FILLET = 1.5

TAB_W = 4.8          # X, Faston quick-connect spade
TAB_T = 0.8          # Z
TAB_PROUD = 5.0      # Y, behind the housing back face

# Seating planes along Y.
shroud_rim_y = SHROUD_PROUD                       # outer rim of the shroud, out through the hole
cavity_floor_y = shroud_rim_y - CAVITY_DEPTH      # floor the blades stand on
flange_back_y = -FLANGE_T                          # the flange's inboard face
body_back_y = flange_back_y - BODY_DEPTH           # housing back face


# --- What a panel owes this receptacle --------------------------------------
# A screw-mount C14 asks a panel for three things: a rounded CUTOUT its shroud reaches
# out through, two SCREW STATIONS that hold it there, and the FACE ROOM its flange takes
# on the inside once it is in. A field spaced to the cutout fouls on the flange, which is
# the widest of the three.
#   All three are symmetric about the mating axis: the cutout is centred on it and both
# screws sit on it. So a panel places one station and the three follow.


def panel_cutout() -> tuple:
    """`(width, height, corner radius)` of the axis-centred rounded rectangle the shroud
    reaches out through."""
    return (CUTOUT_W, CUTOUT_H, CUTOUT_R)


def panel_screws() -> tuple:
    """The two screw stations in the panel plane, as `(x, z)` off the cutout's own centre.
    Both sit ON the mating axis, one either side of the hole."""
    return ((-SCREW_PITCH / 2.0, 0.0), (SCREW_PITCH / 2.0, 0.0))


def panel_footprint() -> tuple:
    """`(width, height)` the receptacle takes on the panel face, seen down the mating axis —
    what crowds a neighbour, a wall or a ceiling. The flange is the widest section, and it
    bears on the panel's INNER face."""
    return (FLANGE_W, FLANGE_H)


def stations_hold():
    """Hold the calipered panel figures to `iec-c14-inlet.step` — the file the enclosure
    seats through its wall, while it cuts and drills off these live figures.

    The face footprint is the flange's own outline, an extent of that solid's box either
    way. Against the cutout: what stands outboard of the seating plane clears it, the
    flange covers it, and both screws land in flange and miss it."""
    solid = cq.importers.importStep(str(STEP)).val()
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
        if thru > hole - 1e-6:
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
                f"cutout — a boss there stands in the hole the shroud comes through.")


def build_flange():
    """Rounded-corner flange, Y = 0 to FLANGE_T, bearing on the panel's inner face and
    bored for the two screws that hold it there."""
    flange = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=flange_back_y)
        .rect(FLANGE_W, FLANGE_H)
        .extrude(FLANGE_T)
        .edges("|Y")
        .fillet(FLANGE_FILLET)
    )
    for sx, sz in panel_screws():
        bore = (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=flange_back_y)
            .center(sx, -sz)                  # local +y -> world -Z
            .circle(SCREW_D / 2.0)
            .extrude(FLANGE_T)
        )
        flange = flange.cut(bore)
    return flange


def build_shroud():
    """Raised ring reaching out through the panel cutout (0 -> shroud_rim_y) with
    a recessed cavity bored back down to the cavity floor — the pocket the C13 plug
    body enters."""
    ring = (
        cq.Workplane(xz_plane_y_up)
        .rect(SHROUD_W, SHROUD_H)
        .extrude(SHROUD_PROUD)
        .edges("|Y")
        .fillet(SHROUD_FILLET)
    )
    cavity = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=shroud_rim_y)
        .rect(CAVITY_W, CAVITY_H)
        .extrude(-CAVITY_DEPTH)
    )
    return ring.cut(cavity)


def build_blades():
    """The three flat male blades standing on the cavity floor, projecting
    +Y. Line/neutral on a horizontal line LN_SPACING apart; earth centered
    above (world +Z -> local -y on this plane)."""
    blades = None
    # Line + neutral (along X, symmetric about origin), slightly below center
    # so the earth blade can sit above within the cavity.
    ln_z_local = EARTH_OFFSET_Z / 2.0   # local +y -> world -Z: L/N below center
    for sx in (-1.0, 1.0):
        b = (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=cavity_floor_y)
            .center(sx * LN_SPACING / 2.0, ln_z_local)
            .rect(BLADE_W, BLADE_T)
            .extrude(BLADE_PROUD)
        )
        blades = b if blades is None else blades.union(b)
    # Earth blade: above the L/N line. local -y => world +Z.
    earth_z_local = ln_z_local - EARTH_OFFSET_Z
    earth = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=cavity_floor_y)
        .center(0.0, earth_z_local)
        .rect(BLADE_T, BLADE_W)   # earth blade oriented vertically (taller)
        .extrude(BLADE_PROUD)
    )
    return blades.union(earth)


def build_body():
    """Molded housing behind the flange (Y = 0 -> body_back_y), standing in the
    enclosure with the terminals on its back face."""
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=flange_back_y)
        .rect(BODY_W, BODY_H)
        .extrude(-BODY_DEPTH)
        .edges("|Y")
        .fillet(BODY_FILLET)
    )


def build_terminals():
    """Three Faston quick-connect spade tabs projecting -Y from the housing
    back face, on the same X/Z layout as the blades."""
    tabs = None
    ln_z_local = EARTH_OFFSET_Z / 2.0
    for sx in (-1.0, 1.0):
        t = (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=body_back_y)
            .center(sx * LN_SPACING / 2.0, ln_z_local)
            .rect(TAB_W, TAB_T)
            .extrude(-TAB_PROUD)
        )
        tabs = t if tabs is None else tabs.union(t)
    earth_z_local = ln_z_local - EARTH_OFFSET_Z
    earth = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=body_back_y)
        .center(0.0, earth_z_local)
        .rect(TAB_T, TAB_W)
        .extrude(-TAB_PROUD)
    )
    return tabs.union(earth)


def build_iec_c14_inlet():
    """The inlet as a single solid wrapped in a cq.Workplane."""
    return (
        build_flange()
        .union(build_shroud())
        .union(build_blades())
        .union(build_body())
        .union(build_terminals())
    )


def main():
    part = build_iec_c14_inlet()
    bb = part.val().BoundingBox()
    print("IEC 60320 C14 panel-mount AC inlet — snap-in (MXR B07DCXKNXQ, generic)")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Extents: X {bb.xlen:.2f}  Y {bb.ylen:.2f}  Z {bb.zlen:.2f}")
    print(f"  Proud of seating face (outward): {bb.ymax:.2f} mm")
    print(f"  Into enclosure (inward): {bb.ymin:.2f} mm")
    print(f"  Flange {FLANGE_W} x {FLANGE_H} / cutout body {BODY_W} x {BODY_H}")
    print(f"  Solid valid: {part.val().isValid()}")

    here = Path(__file__).resolve().parent
    out = here / "iec-c14-inlet.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
