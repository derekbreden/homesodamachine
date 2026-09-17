"""Shallow faucet display cover with broad lips around the rigid neck.

The cover moves normal to the display. Its stable cosmetic skin follows the
glass closely. Its side walls spread over the cylinder and relax into grooves.
The PET-GF snap's force and durability require the representative print trial.
"""
from pathlib import Path
import sys

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for path in (
    _hw / "scripts",
    _hw / "printed-parts" / "faucet",
    _hw / "printed-parts" / "faucet" / "faucet-shell",
    next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools",
):
    sys.path.insert(0, str(path))
from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK, one_body
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
rear_rim_s = 42.0
rear_rim_slope = 1.5


def build_plate_outer() -> cq.Workplane:
    return shell.build_display_outer_envelope()


def build_plate_inner_cut() -> cq.Workplane:
    window = shell._cradle_prism(
        window_half_x, window_s_south, window_s_north,
        bezel_n_bottom - 0.1, plate_n_top + 1.0, corner_r=window_corner_r,
    )
    cavity = shell.build_display_cover_inner_envelope().intersect(
        shell._cradle_prism(50.0, shell.display_s_bottom,
                            shell.display_head_s_max + 1.0, -30.0, 40.0))
    return cavity.union(window)


def build_corner_rim_relief() -> cq.Workplane:
    """Blunt transverse rims keep the end skirts clear of the neck's tangent."""
    bottom = shell.display_cover_bottom_n
    front_s = (front_rim_n - bottom) / front_rim_slope
    front = (cq.Workplane("YZ")
             .polyline([(-10.0, -30.0), (front_s, -30.0), (front_s, bottom),
                        (-10.0, front_rim_n + 10.0 * front_rim_slope)])
             .close().extrude(30.0, both=True))
    rear = (cq.Workplane("YZ")
            .polyline([(rear_rim_s, -30.0), (60.0, -30.0),
                       (60.0, bottom + (60.0 - rear_rim_s) * rear_rim_slope),
                       (rear_rim_s, bottom)])
            .close().extrude(30.0, both=True))
    return shell._display_world(front.union(rear))


def build_display_cover() -> cq.Workplane:
    skin = (build_plate_outer().cut(build_plate_inner_cut())
            .cut(shell.build_display_neck_clearance())
            .cut(build_corner_rim_relief()))
    return skin.union(shell.build_display_cover_lips())


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
        print("ok faucet-display-cover: one solid; 1.3 mm bezel and retaining lips; PET-GF cover flex requires print trial")
    return int(bool(failures))


def main():
    cover = build_display_cover()
    out = _here.parent / "faucet-display-cover.step"
    export_assembly(one_body(cover, out.stem, C_FAUCET_BLACK), str(out))
    shell.write_bed_file(cover, out.with_suffix(".stl"))
    substitute_md(_here.parent / "README.md", variables={
        "PLATE_X": f"{shell.display_cover_face_width:g} mm",
        "PLATE_S": f"{shell.display_cover_face_length:g} mm",
        "WINDOW_X": f"{window_x:g} mm",
        "WINDOW_S": f"{window_s:g} mm",
        "COVER_OVER_FACE": f"{display_cover_over_face:g} mm",
        "COSMETIC_WALL": f"{bezel_thickness:g} mm",
        "SNAP_ENGAGEMENT": f"{_display_snap.ENGAGEMENT:g} mm",
        "DISPLAY_FEET_N": f"{shell.display_feet_n:g} mm",
    })
    print(f"-> {out.name}; {cover.val().Volume():.0f} mm³")


if __name__ == "__main__":
    sys.exit(selftest()) if len(sys.argv) > 1 and sys.argv[1] == "selftest" else main()
