"""Shallow faucet display cover with broad lips around the rigid neck.

The display and cover slide onto the tip together, then seat normal to the glass.
The cosmetic skin follows the glass closely. Its preformed walls remain spread
against the seated groove roots.
The PET-GF snap's force and durability require the representative print trial.

`faucet_display_cover.rs` cuts the cover from its numbers crate (`numbers.rs`). This module is
for the readers that still take it from Python: the builders here draw it in CadQuery for the
faucet assembly's CadQuery assembly, the display snap trial and the geometry check.
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
import cadquery as cq
from _faucet_interface import (
    display_corner_r, display_cover_lap, display_cover_over_face,
    display_housing_length, display_housing_width,
)
import _display_snap
import faucet_shell as shell

from _rust_data import request

_SHELL_FIELDS = (
    'display_cover_top_n',
    'display_face_n',
    'display_s_bottom',
    'display_cradle_clearance',
    'display_s_top',
    'display_head_s_min',
    'display_head_s_max',
    'dispense_face_thickness',
    'display_cover_skirt_width',
    'display_clip_s_bottom',
    'display_clip_s_top',
    'display_clip_bottom_n',
    'display_clip_top_n',
    'display_cover_skirt_length',
    'display_cover_skirt_r',
    '_display_cover_center_s',
    'display_cover_bottom_n',
    'display_cover_shoulder_n',
    'display_cover_face_width',
    'display_cover_face_length',
    'display_cover_face_r',
    'display_cover_inner_rows',
    '_display_housing_center_s',
    'display_cover_inner_clamp',
    'display_neck_outer_r',
    'display_cover_slip',
    'display_clip_lip_radius',
    'display_feet_n',
    'display_cartridge_lift_n',
    'display_foot_pad_width',
    'display_foot_pad_depth',
)


def _data(*, preload_n=None):
    payload = {"op": "consumer-cover", "shell": {key: getattr(shell, key) for key in _SHELL_FIELDS},
               "preload_n": preload_n}
    return request("faucet-data", "faucet-data", payload)


globals().update(_data()["datums"])
outer_clamp = tuple(outer_clamp)
cavity_clamp = tuple(cavity_clamp)
lip_band = tuple(lip_band)


def outer_rows() -> tuple:
    """Rust-derived (width, length, corner radius, n, centre s) skin rows."""
    return tuple(tuple(row) for row in _data()["outer_rows"])


def build_plate_outer() -> cq.Workplane:
    """Rounded skin with its lower rear skirt enclosing the display feet."""
    wires = [shell._display_outline_wire(width, length, r, n, center_s=s)
             for width, length, r, n, s in outer_rows()]
    loft = shell._display_world(cq.Workplane(obj=cq.Solid.makeLoft(wires, ruled=False)))
    return loft.intersect(shell._cradle_prism(*outer_clamp))


def window_n() -> tuple:
    """The glass window cutter's normal interval, from the Rust recipe."""
    return tuple(_data()["window_n"])


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
    return _data(preload_n=n)["preload"]


def wing_slope() -> float:
    """Inward print lean per millimetre below the bezel."""
    return _data()["wing_slope"]


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
