"""Industrial faucet display cover in the shared assembled faucet frame.

The rectangular cover carries the display during axial placement. Its broad
preformed wings spread around the rigid neck and seat in the shared grooves.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys

import cadquery as cq

_here = Path(__file__).resolve()
_faucet = _here.parent.parent
for path in (_faucet, _faucet / "faucet-shell"):
    sys.path.insert(0, str(path))

import _display_snap
from _faucet_interface import (
    display_corner_r, display_cover_lap, display_cover_over_face,
    display_housing_width,
)
import faucet_shell as shell


from _rust_data import request

_SHELL_FIELDS = (
    'wall_thickness_min',
    'dispense_face_thickness',
    'display_cover_bottom_n',
    'display_cover_top_n',
    'display_face_n',
    'display_s_bottom',
    'display_cradle_clearance',
    'display_s_top',
    'display_clip_top_n',
    'display_feet_n',
    'display_neck_outer_r',
    'display_cover_slip',
    'display_clip_lip_radius',
)


def _data(dimensions=None, *, preload_n=None):
    return request("faucet-data", "faucet-data", {
        "op": "industrial-cover", "shell": {key: getattr(shell, key) for key in _SHELL_FIELDS},
        "dimensions": vars(dimensions) if dimensions is not None else None, "preload_n": preload_n,
    })


_defaults = _data()["defaults"]


@dataclass(frozen=True)
class CoverDimensions:
    width: float = _defaults["width"]
    length: float = _defaults["length"]
    upper_side_wall: float = _defaults["upper_side_wall"]
    lower_side_wall: float = _defaults["lower_side_wall"]
    rear_wall: float = _defaults["rear_wall"]
    front_wall: float = _defaults["front_wall"]
    n_bottom: float = _defaults["n_bottom"]
    wing_extension_mm: float = _defaults["wing_extension_mm"]

    @property
    def n_top(self) -> float:
        return _data(self)["n_top"]

    @property
    def bezel_n_bottom(self) -> float:
        return _data(self)["bezel_n_bottom"]


DIMENSIONS = CoverDimensions()
globals().update(_data(DIMENSIONS)["datums"])


def build_plate_outer(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    return shell._cradle_prism(dimensions.width / 2.0, 0.0, dimensions.length,
                               dimensions.n_bottom, dimensions.n_top)


def cavity_sections(dimensions: CoverDimensions = DIMENSIONS) -> tuple:
    """Rust-derived cavity (half width, n) rows."""
    return tuple(tuple(row) for row in _data(dimensions)["cavity_sections"])


def window_n(dimensions: CoverDimensions = DIMENSIONS) -> tuple:
    """The glass window cutter's normal interval, from the Rust recipe."""
    return tuple(_data(dimensions)["window_n"])


def build_plate_inner_cut(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    s0, s1 = dimensions.front_wall, dimensions.length - dimensions.rear_wall
    wires = [(cq.Workplane("XY").workplane(offset=n)
              .moveTo(-half_x, s0).lineTo(half_x, s0).lineTo(half_x, s1)
              .lineTo(-half_x, s1).lineTo(-half_x, s0).wire().val())
             for half_x, n in cavity_sections(dimensions)]
    cavity = shell._display_world(cq.Workplane(obj=cq.Solid.makeLoft(wires, ruled=True)))
    window = shell._cradle_prism(
        window_half_x, window_s_south, window_s_north, *window_n(dimensions),
        corner_r=window_corner_r,
    )
    return cavity.union(window)


def build_display_cover_lips(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    band = shell._cradle_prism(
        dimensions.width / 2.0, shell.display_clip_s_bottom, shell.display_clip_s_top,
        shell.display_clip_bottom_n, shell.display_clip_top_n,
    )
    core = shell.build_display_neck_reference(
        shell.display_neck_outer_r - shell.display_clip_lip_radius)
    return shell.relieve_display_lip_inner_edges(band.cut(core))


# The cover as it sits on the tip, which the Industrial assembly stands in place.
SEATED_STEP = _here.parent / "industrial-display-cover-seated.step"


def build_seated_display_cover(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    """Nominal seated reference with planar sides and a filled rear wall."""
    _, _, normal = shell._tip_frame()
    arch_clearance = shell.build_display_neck_clearance().translate(
        normal.multiply(dimensions.wing_extension_mm).toTuple())
    skin = (build_plate_outer(dimensions).cut(build_plate_inner_cut(dimensions))
            .cut(arch_clearance))
    return skin.union(build_display_cover_lips(dimensions))


def preload_inward_at(n: float, dimensions: CoverDimensions = DIMENSIONS) -> float:
    return _data(dimensions, preload_n=n)["preload"]


def wing_slope(dimensions: CoverDimensions = DIMENSIONS) -> float:
    """Inward print lean per millimetre below the bezel."""
    return _data(dimensions)["wing_slope"]


def relaxed_wing_transform(side: int, dimensions: CoverDimensions = DIMENSIONS) -> cq.Matrix:
    slope = side * wing_slope(dimensions)
    return cq.Matrix([[1.0, 0.0, slope, -slope * dimensions.bezel_n_bottom],
                      [0.0, 1.0, 0.0, 0.0],
                      [0.0, 0.0, 1.0, 0.0],
                      [0.0, 0.0, 0.0, 1.0]])


def build_display_cover(dimensions: CoverDimensions = DIMENSIONS,
                        seated: cq.Workplane | None = None) -> cq.Workplane:
    """Relaxed printable shape; the bezel retains its exact seated dimensions. It is cut from the
    seated cover (`build_seated_display_cover`, unless it is handed in)."""
    origin, _, normal = shell._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    seated = (build_seated_display_cover(dimensions) if seated is None else seated).val().moved(frame.inverse)
    margin = dimensions.width + dimensions.length
    bezel = seated.intersect(cq.Solid.makeBox(
        2.0 * margin, 2.0 * margin, margin,
        cq.Vector(-margin, -margin, dimensions.bezel_n_bottom)))
    pieces = [bezel]
    for side in (-1, 1):
        half = cq.Solid.makeBox(
            margin, 2.0 * margin, dimensions.bezel_n_bottom + margin,
            cq.Vector(0.0 if side > 0 else -margin, -margin, -margin))
        wing = seated.intersect(half).transformGeometry(relaxed_wing_transform(side, dimensions))
        pieces.append(wing)
    relaxed = pieces[0].fuse(*pieces[1:]).clean()
    if not relaxed.isValid() or len(relaxed.Solids()) != 1:
        raise ValueError("the Industrial display cover must be one valid printable solid")
    return cq.Workplane(obj=relaxed.moved(frame))


def show_face(cover: cq.Workplane, dimensions: CoverDimensions = DIMENSIONS) -> tuple[int, float]:
    origin, _, normal = shell._tip_frame()
    faces = [face for face in cover.val().Faces()
             if face.geomType() == "PLANE"
             and abs((face.Center() - origin).dot(normal) - dimensions.n_top) < 1e-6
             and abs(face.normalAt().dot(normal) - 1.0) < 1e-6]
    return len(faces), sum(face.Area() for face in faces)


def bed_face(cover: cq.Workplane, dimensions: CoverDimensions = DIMENSIONS) -> tuple[int, float]:
    return show_face(cover, dimensions)


def numbers(dimensions: CoverDimensions = DIMENSIONS) -> dict:
    """The Rust scalar program supplies the industrial cover's tip-frame recipe."""
    return _data(dimensions)["numbers"]
