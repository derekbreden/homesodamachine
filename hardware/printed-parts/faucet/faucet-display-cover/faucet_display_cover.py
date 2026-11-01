"""Shallow faucet display cover with broad lips around the rigid neck.

The display and cover slide onto the tip together, then seat normal to the glass.
The cosmetic skin follows the glass closely. Its preformed walls remain spread
against the seated groove roots.
The PET-GF snap's force and durability require the representative print trial.

The kernel cuts the cover (`faucet_display_cover.rs`, beside this module) from the numbers
`numbers()` writes for it (`hardware/scripts/_rust_part.py`). The builders here draw it in
CadQuery for the faucet assembly's CadQuery assembly, the display snap trial and the geometry
check, which read them.
"""

from __future__ import annotations
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for path in (
    _hw / "scripts",
    _hw / "printed-parts" / "faucet",
    _hw / "printed-parts" / "faucet" / "faucet-shell",
    next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools",
):
    sys.path.insert(0, str(path))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq
from _faucet_interface import (
    display_corner_r, display_cover_lap, display_cover_over_face,
    display_housing_length, display_housing_width,
)
from docgen import substitute_md
import _display_snap
import faucet_shell as shell

plate_n_top = shell.display_cover_top_n
bezel_n_bottom = shell.display_face_n + display_cover_over_face
bezel_thickness = plate_n_top - bezel_n_bottom
window_half_x = display_housing_width / 2.0 - display_cover_lap
window_s_south = shell.display_s_bottom + shell.display_cradle_clearance + display_cover_lap
window_s_north = shell.display_s_top - shell.display_cradle_clearance - display_cover_lap
window_corner_r = display_corner_r - display_cover_lap
window_x = 2.0 * window_half_x
window_s = window_s_north - window_s_south
front_rim_n = 14.0
front_rim_slope = 1.8
rear_skirt_extension = 1.2
rear_trim_s0 = 42.1
rear_trim_ds_dn = 0.6
# The prisms (half x, s0, s1, n0, n1) the skin and the display's clearance are cut to, and the
# band the lips are cut from.
outer_clamp = (30.0, shell.display_head_s_min,
               shell.display_head_s_max + rear_skirt_extension + 1.0, -30.0, 40.0)
cavity_clamp = (50.0, shell.dispense_face_thickness, shell.display_head_s_max + 1.0, -30.0, 40.0)
lip_band = (shell.display_cover_skirt_width / 2.0 + 1.0,
            shell.display_clip_s_bottom, shell.display_clip_s_top,
            shell.display_clip_bottom_n, shell.display_clip_top_n)


def outer_rows() -> tuple:
    """The skin's (width, length, corner radius, n, centre s) rows: the skirt, carried back over
    the display's feet, at the bottom and at the shoulder, and the face."""
    skirt = (shell.display_cover_skirt_width,
             shell.display_cover_skirt_length + rear_skirt_extension, shell.display_cover_skirt_r)
    skirt_s = shell._display_cover_center_s + rear_skirt_extension / 2.0
    return ((*skirt, shell.display_cover_bottom_n, skirt_s),
            (*skirt, shell.display_cover_shoulder_n, skirt_s),
            (shell.display_cover_face_width, shell.display_cover_face_length,
             shell.display_cover_face_r, shell.display_cover_top_n, shell._display_cover_center_s))


def build_plate_outer() -> cq.Workplane:
    """Rounded skin with its lower rear skirt enclosing the display feet."""
    wires = [shell._display_outline_wire(width, length, r, n, center_s=s)
             for width, length, r, n, s in outer_rows()]
    loft = shell._display_world(cq.Workplane(obj=cq.Solid.makeLoft(wires, ruled=False)))
    return loft.intersect(shell._cradle_prism(*outer_clamp))


def window_n() -> tuple:
    """The glass window's cutter, from just under the bezel to past the cover's top."""
    return bezel_n_bottom - 0.1, plate_n_top + 1.0


def build_plate_inner_cut() -> cq.Workplane:
    window = shell._cradle_prism(
        window_half_x, window_s_south, window_s_north, *window_n(), corner_r=window_corner_r,
    )
    cavity = shell.build_display_cover_inner_envelope().intersect(
        shell._cradle_prism(*cavity_clamp))
    return cavity.union(window)


def build_corner_rim_relief() -> cq.Workplane:
    """Sloping front and rear lower edges meet the open underside."""
    bottom = shell.display_cover_bottom_n
    front_s = (front_rim_n - bottom) / front_rim_slope
    front = (cq.Workplane("YZ")
             .polyline([(-10.0, -30.0), (front_s, -30.0), (front_s, bottom),
                        (-10.0, front_rim_n + 10.0 * front_rim_slope)])
             .close().extrude(30.0, both=True))
    rear_s = rear_trim_s0 + rear_trim_ds_dn * bottom
    rear_n = (70.0 - rear_trim_s0) / rear_trim_ds_dn
    rear = (cq.Workplane("YZ")
            .polyline([(rear_s, -30.0), (70.0, -30.0),
                       (70.0, rear_n), (rear_s, bottom)])
            .close().extrude(30.0, both=True))
    return shell._display_world(front).union(shell._display_world(rear))


def build_display_cover_lips(outer: cq.Workplane | None = None) -> cq.Workplane:
    """Broad retaining lips backed by the cover's complete outer skin."""
    outer = build_plate_outer() if outer is None else outer
    band = shell._cradle_prism(*lip_band)
    inner = shell.build_display_neck_reference(
        shell.display_neck_outer_r - shell.display_clip_lip_radius)
    return shell.relieve_display_lip_inner_edges(outer.intersect(band).cut(inner))


# The cover as it sits on the tip, which the faucet assembly stands in place.
SEATED_STEP = _here.parent / "faucet-display-cover-seated.step"


def build_seated_display_cover() -> cq.Workplane:
    """Nominal seated fit surface; not a predicted elastic deformation."""
    outer = build_plate_outer()
    skin = (outer.cut(build_plate_inner_cut())
            .cut(shell.build_display_neck_clearance())
            .cut(build_corner_rim_relief()))
    return skin.union(build_display_cover_lips(outer))


def preload_inward_at(n: float) -> float:
    """Free wing inset in X, referenced to its upper retaining edge."""
    return max(0.0, _display_snap.X_PRELOAD * (bezel_n_bottom-n)
               / (bezel_n_bottom-shell.display_clip_top_n))


def wing_slope() -> float:
    """How far each wing's relaxed print leans inward per millimetre below the bezel."""
    return _display_snap.X_PRELOAD / (bezel_n_bottom - shell.display_clip_top_n)


def relaxed_wing_transform(side: int) -> cq.Matrix:
    slope = side * wing_slope()
    return cq.Matrix([[1.0, 0.0, slope, -slope*bezel_n_bottom],
                      [0.0, 1.0, 0.0, 0.0],
                      [0.0, 0.0, 1.0, 0.0],
                      [0.0, 0.0, 0.0, 1.0]])


def build_display_cover(seated: cq.Workplane | None = None) -> cq.Workplane:
    """Relaxed printable cover with both wings preformed inward in X, from the seated cover
    (`build_seated_display_cover`, unless it is handed in).

    The planar bezel keeps its dimensions. The two lower halves shear
    inward below its inner face and join through the broad end bridges.
    The seated builder is a fit reference; spring shape and force are measured
    on the complete printed enclosure.
    """
    origin, _, normal = shell._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    seated = (build_seated_display_cover() if seated is None else seated).val().moved(frame.inverse)
    bezel = seated.intersect(cq.Solid.makeBox(100.0, 150.0, 50.0,
                                             cq.Vector(-50.0, -50.0, bezel_n_bottom)))
    pieces = [bezel]
    for side in (-1, 1):
        half = cq.Solid.makeBox(50.0, 150.0, bezel_n_bottom+50.0,
                                cq.Vector(0.0 if side > 0 else -50.0, -50.0, -50.0))
        wing = seated.intersect(half).transformGeometry(relaxed_wing_transform(side))
        pieces.append(wing)
    relaxed = pieces[0].fuse(*pieces[1:]).clean()
    if not relaxed.isValid() or len(relaxed.Solids()) != 1:
        raise ValueError("the preloaded cover must be one valid printable solid")
    return cq.Workplane(obj=relaxed.moved(frame))


def _plane_faces(cover: cq.Workplane, axis: cq.Vector, station: float, sign: float) -> tuple:
    tip_end, _, _ = shell._tip_frame()
    found = []
    for face in cover.val().Faces():
        if face.geomType() != "PLANE":
            continue
        center = face.Center()
        if abs((center - tip_end).dot(axis) - station) < 1e-6 and abs(face.normalAt(center).dot(axis) - sign) < 1e-6:
            found.append(face)
    return len(found), sum(face.Area() for face in found)


def show_face(cover: cq.Workplane) -> tuple:
    return _plane_faces(cover, shell._tip_frame()[2], plate_n_top, 1.0)


def bed_face(cover: cq.Workplane) -> tuple:
    # The broad, planar bezel is the candidate's face-down bed surface.
    return show_face(cover)


def selftest() -> int:
    cover = build_display_cover()
    failures = []
    if not cover.val().isValid() or len(cover.val().Solids()) != 1:
        failures.append("cover must be one valid solid")
    if bezel_thickness < 1.0 - 1e-8:
        failures.append("cosmetic bezel is thinner than 1 mm")
    if _display_snap.LIP_HEIGHT < 1.0 - 1e-8:
        failures.append("cover lip is thinner than 1 mm")
    if show_face(cover)[0] != 1:
        failures.append("bezel must have one planar show face")
    for failure in failures:
        print("FAIL", failure)
    if not failures:
        print("ok faucet-display-cover: one solid; planar 1.3 mm bezel and 3 mm preloaded lips; physical retention requires print trial")
    return int(bool(failures))


def numbers() -> dict:
    """What `faucet_display_cover.rs` cuts the cover from, in the tip frame: x across the neck, s
    back up it from the tube exit, n out through the glass. A row is (width, length, corner
    radius, n, centre s), a prism (half x, s0, s1, n0, n1)."""
    return {
        **shell.numbers(),
        "name": "faucet-display-cover",
        "names": {"cover": "faucet-display-cover", "seated": SEATED_STEP.stem},
        "cover_outer_rows": [list(row) for row in outer_rows()],
        "cover_outer_clamp": list(outer_clamp),
        "cover_cavity_rows": [[*row, shell._display_housing_center_s]
                              for row in shell.display_cover_inner_rows],
        "cover_cavity_clamps": [list(shell.display_cover_inner_clamp), list(cavity_clamp)],
        "cover_window_half_x": window_half_x,
        "cover_window_s": [window_s_south, window_s_north],
        "cover_window_n": list(window_n()),
        "cover_window_corner_r": window_corner_r,
        "cover_neck_clearance_r": shell.display_neck_outer_r + shell.display_cover_slip,
        # The lower front edge rises to n = front_rim_n - front_rim_slope * s, and the rear edge
        # runs back to s = rear_trim_s0 + rear_trim_ds_dn * n.
        "cover_front_rim": [front_rim_n, front_rim_slope],
        "cover_rear_trim": [rear_trim_s0, rear_trim_ds_dn],
        "cover_lip_band": list(lip_band),
        # The radius the lips' neck reference draws: the neck's, less the shrink it is handed.
        "cover_lip_r": shell.display_neck_outer_r - (
            shell.display_neck_outer_r - shell.display_clip_lip_radius),
        "cover_lip_relief": _display_snap.LIP_INNER_EDGE_RELIEF,
        "cover_bezel_n": bezel_n_bottom,
        "cover_wing_slope": wing_slope(),
    }


def main():
    # A run cuts the cover; an import of this module is a reader of its builders and numbers.
    import _rust_part

    said = _rust_part.cut("faucet", "faucet-display-cover", numbers(), _here.parent)
    print("-> " + ", ".join(said["files"]))
    out = _here.parent / "faucet-display-cover.step"
    substitute_md(_here.parent / "README.md", variables={
        "PLATE_X": f"{shell.display_cover_face_width:g} mm",
        "PLATE_S": f"{shell.display_cover_face_length:g} mm",
        "WINDOW_X": f"{window_x:g} mm",
        "WINDOW_S": f"{window_s:g} mm",
        "COVER_OVER_FACE": f"{display_cover_over_face:g} mm",
        "COSMETIC_WALL": f"{bezel_thickness:g} mm",
        "DISPENSE_FACE_T": f"{shell.dispense_face_thickness:g} mm",
        "SNAP_ENGAGEMENT": f"{_display_snap.ENGAGEMENT:g} mm",
        "LIP_HEIGHT": f"{_display_snap.LIP_HEIGHT:g} mm",
        "WING_PRELOAD": f"{_display_snap.X_PRELOAD:g} mm",
        "WING_BOTTOM_PRELOAD": f"{preload_inward_at(shell.display_clip_bottom_n):.3f} mm",
        "GROOVE_DEPTH": f"{_display_snap.ENGAGEMENT + _display_snap.RADIAL_SLIP:g} mm",
        "GROOVE_ROOF_CLEARANCE": f"{_display_snap.BEARING_SLIP:g} mm",
        "GROOVE_END_CLEARANCE": f"{_display_snap.END_SLIP:g} mm",
        "LIP_INNER_EDGE_RELIEF": f"{_display_snap.LIP_INNER_EDGE_RELIEF:g} mm",
        "DISPLAY_FEET_N": f"{shell.display_feet_n:g} mm",
        "DISPLAY_INSTALL_LIFT": f"{shell.display_cartridge_lift_n:g} mm",
        "FOOT_PAD_WIDTH": f"{shell.display_foot_pad_width:g} mm",
        "FOOT_PAD_DEPTH": f"{shell.display_foot_pad_depth:g} mm",
        "REAR_SKIRT_EXT": f"{rear_skirt_extension:g} mm",
        "REAR_TRIM_S0": f"{rear_trim_s0:g} mm",
        "REAR_TRIM_DS_DN": f"{rear_trim_ds_dn:g}",
    })
    cover = next(body for body in said["bodies"] if body["name"] == out.stem)
    print(f"-> {out.name}; {cover['volume']:.0f} mm³")


if __name__ == "__main__":
    sys.exit(selftest()) if len(sys.argv) > 1 and sys.argv[1] == "selftest" else main()
