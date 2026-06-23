"""Reference solid of an IEC 60320 C14 panel-mount AC power inlet — the
standard cheap snap-in (V-lock / clip-mount) male appliance inlet you see
on PC power supplies and most appliances. BOM: MXR IEC 60320 C14
panel-mount AC inlet, 10 A / 250 VAC (Amazon B07DCXKNXQ); rear-panel mains
inlet that accepts a standard NEMA 5-15P-to-C13 line cord.

A single molded body: a rounded-corner front flange (bezel) that overhangs
the panel cutout, a recessed shroud on the outside face holding the three
flat male blades (line, neutral, earth) that mate with the C13 cordset, and
a deeper housing behind the panel carrying the quick-connect spade
terminals into the enclosure.

Real-world dimensions (mm)
--------------------------
IEC 60320 C14 is a highly standardized form factor. No exact MXR drawing is
published, so this is a representative generic snap-in C14 inlet built from
the dimensions that repeat across mainstream datasheets:
  Panel cutout: 27.0 W x 20.0 H rectangle with two stepped notches at the
      top corners that receive the V-lock snap tabs (Jameco 27.00 x 20.50;
      Panel Components / eBay 27 x 19.5; Mouser drawing 26.7 x 20.4;
      Interpower 27.5 x 20). Panel thickness 1.0-1.5 mm.
  Front flange / bezel: 30.5 W x 22.5 H, 2.0 thick, rounded corners
      (Amazon C14 listing bezel height 22.5; standard ~31 x 23 face).
  Recessed shroud on the outside face: ~16 W x ~13 H opening, ~9 deep,
      with the three blades projecting toward +Y inside it.
  Male blades: IEC flat blades ~4.0 W x 1.0 thick. Line + neutral on a
      horizontal line 14 mm apart; earth blade centered above, offset ~8 mm
      up. Faston quick-connect tabs behind the panel are 4.8 x 0.8 mm.
  Body depth behind the panel face: ~27 mm overall housing + terminal
      stubs (Amazon C14 listing total ~49.7 mm minus the bezel/shroud).

Sources: Mouser IEC-connector spec drawing, Interpower C14 snap-in inlet
note, Jameco IEC 320-C14 snap-in receptacle, Panel Components Corp snap-in
C14, RS PRO C14 snap-in datasheet — all IEC 60320-1 sheet C14.

Coordinate convention
----------------------
Matches jg_bulkhead_union.py.
  Y = insertion / mating axis. +Y = OUTWARD (toward the outside of the
      enclosure, where the C13 line cord plugs in — the male blades face
      +Y). -Y = INWARD (the housing and spade terminals reach into the
      enclosure).
  Origin = the panel-seating plane = the back face of the front flange
      (the plane that sits against the OUTSIDE of the rear panel). The
      bezel + recessed blades stand proud at y >= 0; the housing + terminals
      sit at y < 0.
  +Z = up. X completes the right-handed frame. The cutout long axis
      (width 27 mm) is along X; the short axis (20 mm) is along Z.

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


# --- Front flange (bezel), outside the panel ------------------------------
FLANGE_W = 30.5      # X
FLANGE_H = 22.5      # Z
FLANGE_T = 2.0       # Y, proud of the seating face
FLANGE_FILLET = 2.5  # rounded bezel corners

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
BODY_W = 27.5        # X, snaps into the 27 mm cutout
BODY_H = 20.5        # Z
BODY_DEPTH = 22.0    # Y, molded housing into the enclosure
BODY_FILLET = 1.5
# Earth-blade notch at the top of the cutout-fitting body (the stepped
# corners of a snap-in C14): a shallow raised key spanning the top edge.
KEY_W = 14.0         # X
KEY_H = 2.0          # Z, rises above BODY_H top edge
KEY_DEPTH = 6.0      # Y

TAB_W = 4.8          # X, Faston quick-connect spade
TAB_T = 0.8          # Z
TAB_PROUD = 5.0      # Y, behind the housing back face
TAB_DEPTH_Y = -BODY_DEPTH  # tabs start at the housing back face

# Seating planes along Y.
shroud_rim_y = FLANGE_T + SHROUD_PROUD            # outer rim of the shroud
cavity_floor_y = shroud_rim_y - CAVITY_DEPTH      # floor the blades stand on
body_back_y = -BODY_DEPTH                          # housing back face


def build_flange():
    """Rounded-corner bezel, Y = 0 to FLANGE_T, overhanging the cutout."""
    return (
        cq.Workplane(xz_plane_y_up)
        .rect(FLANGE_W, FLANGE_H)
        .extrude(FLANGE_T)
        .edges("|Y")
        .fillet(FLANGE_FILLET)
    )


def build_shroud():
    """Raised ring on the bezel face (FLANGE_T -> shroud_rim_y) with a
    recessed cavity bored back down to the cavity floor — the pocket the
    C13 plug body enters."""
    ring = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=FLANGE_T)
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
    """Molded housing behind the panel (Y = 0 -> body_back_y) that snaps
    into the cutout, plus a shallow top key representing the stepped
    earth-corner of a snap-in C14 cutout."""
    body = (
        cq.Workplane(xz_plane_y_up)
        .rect(BODY_W, BODY_H)
        .extrude(-BODY_DEPTH)
        .edges("|Y")
        .fillet(BODY_FILLET)
    )
    # Top key: local -y to sit at world +Z (top edge of the body).
    key = (
        cq.Workplane(xz_plane_y_up)
        .center(0.0, -(BODY_H / 2.0 + KEY_H / 2.0))
        .rect(KEY_W, KEY_H)
        .extrude(-KEY_DEPTH)
    )
    return body.union(key)


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
