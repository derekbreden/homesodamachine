"""Industrial faucet display cover in the shared assembled faucet frame.

The rectangular cover carries the display during axial placement. Its broad
preformed wings spread around the rigid neck and seat in the shared grooves.
"""
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


@dataclass(frozen=True)
class CoverDimensions:
    width: float = 29.0
    length: float = 49.75
    upper_side_wall: float = shell.wall_thickness_min
    rear_wall: float = shell.wall_thickness_min
    front_wall: float = shell.dispense_face_thickness
    n_bottom: float = shell.display_cover_bottom_n
    n_top: float = shell.display_cover_top_n
    bezel_n_bottom: float = shell.display_face_n + display_cover_over_face


DIMENSIONS = CoverDimensions()
plate_n_top = DIMENSIONS.n_top
bezel_n_bottom = DIMENSIONS.bezel_n_bottom
bezel_thickness = plate_n_top - bezel_n_bottom
window_half_x = display_housing_width / 2.0 - display_cover_lap
window_s_south = shell.display_s_bottom + shell.display_cradle_clearance + display_cover_lap
window_s_north = shell.display_s_top - shell.display_cradle_clearance - display_cover_lap
window_corner_r = display_corner_r - display_cover_lap
window_x = 2.0 * window_half_x
window_s = window_s_north - window_s_south
display_head_s_min = 0.0
display_head_s_max = DIMENSIONS.length


def build_plate_outer(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    return shell._cradle_prism(dimensions.width / 2.0, 0.0, dimensions.length,
                               dimensions.n_bottom, dimensions.n_top)


def build_plate_inner_cut(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    upper_half_x = dimensions.width / 2.0 - dimensions.upper_side_wall
    lower_half_x = upper_half_x + preload_inward_at(shell.display_feet_n, dimensions)
    s0, s1 = dimensions.front_wall, dimensions.length - dimensions.rear_wall
    sections = ((lower_half_x, dimensions.n_bottom - 1.0),
                (lower_half_x, shell.display_feet_n),
                (upper_half_x, dimensions.bezel_n_bottom))
    wires = [(cq.Workplane("XY").workplane(offset=n)
              .moveTo(-half_x, s0).lineTo(half_x, s0).lineTo(half_x, s1)
              .lineTo(-half_x, s1).lineTo(-half_x, s0).wire().val())
             for half_x, n in sections]
    cavity = shell._display_world(cq.Workplane(obj=cq.Solid.makeLoft(wires, ruled=True)))
    window = shell._cradle_prism(
        window_half_x, window_s_south, window_s_north,
        dimensions.bezel_n_bottom - 0.1, dimensions.n_top + 1.0,
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
    return band.cut(core)


def build_seated_display_cover(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    """Nominal seated reference with planar sides and a filled rear wall."""
    skin = (build_plate_outer(dimensions).cut(build_plate_inner_cut(dimensions))
            .cut(shell.build_display_neck_clearance()))
    return skin.union(build_display_cover_lips(dimensions))


def preload_inward_at(n: float, dimensions: CoverDimensions = DIMENSIONS) -> float:
    return max(0.0, _display_snap.X_PRELOAD * (dimensions.bezel_n_bottom - n)
               / (dimensions.bezel_n_bottom - shell.display_clip_top_n))


def relaxed_wing_transform(side: int, dimensions: CoverDimensions = DIMENSIONS) -> cq.Matrix:
    slope = side * _display_snap.X_PRELOAD / (dimensions.bezel_n_bottom - shell.display_clip_top_n)
    return cq.Matrix([[1.0, 0.0, slope, -slope * dimensions.bezel_n_bottom],
                      [0.0, 1.0, 0.0, 0.0],
                      [0.0, 0.0, 1.0, 0.0],
                      [0.0, 0.0, 0.0, 1.0]])


def build_display_cover(dimensions: CoverDimensions = DIMENSIONS) -> cq.Workplane:
    """Relaxed printable shape; the bezel retains its exact seated dimensions."""
    origin, _, normal = shell._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    seated = build_seated_display_cover(dimensions).val().moved(frame.inverse)
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
