"""Registered under-sink cold-water hookup scenes for the Quick Start.

The four scenes use one literal coordinate frame and one camera.  They show the
common older-home installation: a copper wall stub, quarter-turn angle stop,
existing braided 3/8-inch faucet supply, an interposed 3/8 x 3/8 x 1/4 tee, and
the appliance's white 1/4-inch branch tube.  Every instructional object is CAD
geometry; there are no labels, arrows, or raster additions.

Frame:
    +X = installer right
    +Y = out from the wall and into the cabinet
    +Z = up
    Y=0 = finished wall face

Run from the repository root:
    tools/cad-venv/bin/python hardware/quickstart/plumbing/plumbing_scenes.py
    tools/cad-venv/bin/python hardware/quickstart/plumbing/plumbing_scenes.py --render
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import cadquery as cq
from PIL import Image


HERE = Path(__file__).resolve().parent
HARDWARE = next(parent for parent in HERE.parents if parent.name == "hardware")
ROOT = HARDWARE.parent
OUT = HERE / "out"
ART = HERE / "art"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_assembly  # noqa: E402


# One explicit viewport for all four states.  The wall slab is also identical in every STEP,
# making their source bounds common even in a viewer that falls back to bounding-box framing.
RENDER_CAM = (1.05, 1.70, 0.62)
RENDER_TARGET = (10.0, 53.0, 160.0)
RENDER_UP = (0.0, 0.0, 1.0)
RENDER_ORTHO_SPAN = 105.0
RENDER_SIZE = "2000x1100"

SCENE_NAMES = (
    "plumbing-valve-on",
    "plumbing-valve-off",
    "plumbing-pre-tee",
    "plumbing-tee-installed",
)


# Scene dimensions, millimetres.
WALL_WIDTH = 500.0
WALL_BOTTOM = -80.0
WALL_HEIGHT = 450.0
WALL_THICKNESS = 18.0
STUB_CENTER = (0.0, 0.0, 112.0)
VALVE_AXIS_Y = 50.0
VALVE_CENTER_Z = STUB_CENTER[2]
VALVE_OUTLET_Z = 145.0

TEE_BOTTOM_Z = 132.0
TEE_TOP_FACE_Z = 193.0
TEE_BRANCH_FACE_X = 47.0
TEE_BRANCH_Z = 163.0


# Instruction-lighting materials.  The two hose systems remain literal: stainless braid for the
# pre-existing 3/8-inch faucet line and white polyethylene for the appliance's 1/4-inch branch.
C_WALL = cq.Color(0.94, 0.935, 0.915, 1.0)
C_COPPER = cq.Color(0.72, 0.31, 0.13, 1.0)
C_BRASS = cq.Color(0.71, 0.46, 0.13, 1.0)
C_BRASS_LIGHT = cq.Color(0.86, 0.62, 0.22, 1.0)
C_CHROME = cq.Color(0.73, 0.76, 0.80, 1.0)
C_CHROME_DARK = cq.Color(0.38, 0.41, 0.45, 1.0)
C_BRAID = cq.Color(0.50, 0.53, 0.57, 1.0)
C_BRAID_HIGHLIGHT = cq.Color(0.76, 0.79, 0.82, 1.0)
C_BRANCH = cq.Color(0.94, 0.945, 0.94, 1.0)
C_BRANCH_EDGE = cq.Color(0.64, 0.66, 0.68, 1.0)
C_HANDLE_BLUE = cq.Color(0.035, 0.27, 0.73, 1.0)
C_GASKET = cq.Color(0.035, 0.038, 0.043, 1.0)


def _vector(values) -> cq.Vector:
    return values if isinstance(values, cq.Vector) else cq.Vector(*values)


def _unit(values) -> cq.Vector:
    vector = _vector(values)
    return vector.multiply(1.0 / vector.Length)


def _point_along(base, axis, distance: float) -> cq.Vector:
    return _vector(base).add(_unit(axis).multiply(distance))


def _cylinder(diameter: float, length: float, base, axis) -> cq.Solid:
    return cq.Solid.makeCylinder(diameter / 2.0, length, _vector(base), _unit(axis))


def _cone(diameter_a: float, diameter_b: float, length: float, base, axis) -> cq.Solid:
    return cq.Solid.makeCone(
        diameter_a / 2.0,
        diameter_b / 2.0,
        length,
        _vector(base),
        _unit(axis),
    )


def _hex_prism(across_flats: float, length: float, base, axis) -> cq.Solid:
    """A wrench hex extruded along a cardinal axis."""
    normal = _unit(axis)
    if abs(normal.z) > 0.9:
        x_dir = cq.Vector(1.0, 0.0, 0.0)
    elif abs(normal.y) > 0.9:
        x_dir = cq.Vector(1.0, 0.0, 0.0)
    else:
        x_dir = cq.Vector(0.0, 1.0, 0.0)
    across_corners = across_flats * 2.0 / math.sqrt(3.0)
    plane = cq.Plane(origin=_vector(base), xDir=x_dir, normal=normal)
    return cq.Workplane(plane).polygon(6, across_corners).extrude(length).val()


def _hex_nut(across_flats: float, bore_d: float, length: float, base, axis) -> cq.Shape:
    """A real open swivel/compression nut rather than a hex intersecting its male stem."""
    normal = _unit(axis)
    outer = _hex_prism(across_flats, length, base, normal)
    bore_base = _vector(base).add(normal.multiply(-0.5))
    bore = _cylinder(bore_d, length + 1.0, bore_base, normal)
    return outer.cut(bore)


def _ring(outer_d: float, inner_d: float, length: float, base, axis) -> cq.Shape:
    normal = _unit(axis)
    outer = _cylinder(outer_d, length, base, normal)
    inner_base = _vector(base).add(normal.multiply(-0.5))
    inner = _cylinder(inner_d, length + 1.0, inner_base, normal)
    return outer.cut(inner)


def _round_sweep(points, radius: float, start_tangent, end_tangent) -> cq.Shape:
    vectors = [_vector(point) for point in points]
    start = _unit(start_tangent)
    end = _unit(end_tangent)
    path = cq.Edge.makeSpline(vectors, tangents=(start, end), scale=False)
    profile = cq.Wire.makeCircle(radius, vectors[0], start)
    return cq.Solid.sweep(profile, [], path, makeSolid=True, isFrenet=True)


def _add(scene: cq.Assembly, shape: cq.Shape, name: str, color: cq.Color) -> None:
    scene.add(shape, name=name, color=color)


def _add_threaded_nipple(
    scene: cq.Assembly,
    *,
    name: str,
    base,
    axis,
    root_d: float,
    crest_d: float,
    length: float,
    pitch: float,
    color: cq.Color,
) -> None:
    """Compression-thread envelope with modeled crest rings, not a drawn texture."""
    _add(scene, _cylinder(root_d, length, base, axis), f"{name}-root", color)
    count = max(1, int((length - 1.0) // pitch))
    for index in range(count):
        offset = 0.8 + index * pitch
        _add(
            scene,
            _cylinder(crest_d, 0.75, _point_along(base, axis, offset), axis),
            f"{name}-crest-{index + 1}",
            color,
        )


def _add_static_wall(scene: cq.Assembly) -> None:
    wall = cq.Solid.makeBox(
        WALL_WIDTH,
        WALL_THICKNESS,
        WALL_HEIGHT,
        cq.Vector(-WALL_WIDTH / 2.0, -WALL_THICKNESS, WALL_BOTTOM),
    )
    _add(scene, wall, "finished-wall", C_WALL)

    escutcheon = _ring(
        54.0,
        17.4,
        4.0,
        (STUB_CENTER[0], -1.5, STUB_CENTER[2]),
        (0.0, 1.0, 0.0),
    )
    _add(scene, escutcheon, "wall-escutcheon", C_CHROME)

    stub = _cylinder(
        15.88,
        38.0,
        (STUB_CENTER[0], -4.0, STUB_CENTER[2]),
        (0.0, 1.0, 0.0),
    )
    _add(scene, stub, "half-inch-copper-wall-stub", C_COPPER)


def _add_handle(scene: cq.Assembly, *, on: bool) -> None:
    """Quarter-turn lever: aligned with the outlet for ON, perpendicular for OFF."""
    y0 = 78.0
    hub = _cylinder(17.0, 8.0, (0.0, y0 - 2.0, VALVE_CENTER_Z), (0.0, 1.0, 0.0))
    _add(scene, hub, "valve-handle-hub", C_CHROME_DARK)
    face = _cylinder(12.0, 1.2, (0.0, y0 + 6.0, VALVE_CENTER_Z), (0.0, 1.0, 0.0))
    _add(scene, face, "valve-handle-face", C_HANDLE_BLUE)

    if on:
        metal = cq.Solid.makeBox(8.0, 5.0, 33.0, cq.Vector(-4.0, y0 + 2.0, 79.0))
        grip = cq.Solid.makeBox(10.0, 6.0, 15.0, cq.Vector(-5.0, y0 + 1.5, 75.0))
        grip_cap = _cylinder(10.0, 6.0, (0.0, y0 + 1.5, 75.0), (0.0, 1.0, 0.0))
    else:
        metal = cq.Solid.makeBox(33.0, 5.0, 8.0, cq.Vector(0.0, y0 + 2.0, 108.0))
        grip = cq.Solid.makeBox(15.0, 6.0, 10.0, cq.Vector(25.0, y0 + 1.5, 107.0))
        grip_cap = _cylinder(10.0, 6.0, (40.0, y0 + 1.5, 112.0), (0.0, 1.0, 0.0))
    _add(scene, metal, "valve-handle-lever", C_CHROME)
    _add(scene, grip, "valve-handle-blue-grip", C_HANDLE_BLUE)
    _add(scene, grip_cap, "valve-handle-blue-end", C_HANDLE_BLUE)


def _add_angle_stop(scene: cq.Assembly, *, on: bool, outlet_exposed: bool) -> None:
    # 1/2-inch compression inlet: the rear nut, tapered forged body, and front stem are distinct
    # solids so their wrench flats and shoulders survive at instruction-page scale.
    _add(
        scene,
        _hex_nut(24.0, 16.3, 17.0, (0.0, 21.0, VALVE_CENTER_Z), (0.0, 1.0, 0.0)),
        "valve-inlet-compression-nut",
        C_BRASS_LIGHT,
    )
    _add(
        scene,
        _cone(17.0, 25.0, 9.0, (0.0, 35.0, VALVE_CENTER_Z), (0.0, 1.0, 0.0)),
        "valve-forged-body-rear",
        C_BRASS,
    )
    _add(
        scene,
        _cylinder(25.0, 17.0, (0.0, 44.0, VALVE_CENTER_Z), (0.0, 1.0, 0.0)),
        "valve-forged-body-center",
        C_BRASS,
    )
    _add(
        scene,
        _cone(25.0, 18.0, 10.0, (0.0, 61.0, VALVE_CENTER_Z), (0.0, 1.0, 0.0)),
        "valve-forged-body-front",
        C_BRASS,
    )
    _add(
        scene,
        _cylinder(8.5, 9.0, (0.0, 69.0, VALVE_CENTER_Z), (0.0, 1.0, 0.0)),
        "valve-quarter-turn-stem",
        C_BRASS_LIGHT,
    )

    # The angle-stop turn: an integral vertical boss, wrench shoulder, and exposed 3/8-inch male
    # compression thread.  Its mouth is the common seating datum for the original hose or tee.
    _add(
        scene,
        _cylinder(19.0, 18.0, (0.0, VALVE_AXIS_Y, 107.0), (0.0, 0.0, 1.0)),
        "valve-outlet-forged-boss",
        C_BRASS,
    )
    _add(
        scene,
        _hex_prism(18.0, 8.0, (0.0, VALVE_AXIS_Y, 121.0), (0.0, 0.0, 1.0)),
        "valve-outlet-wrench-shoulder",
        C_BRASS_LIGHT,
    )
    _add_threaded_nipple(
        scene,
        name="valve-three-eighths-compression-thread",
        base=(0.0, VALVE_AXIS_Y, 127.0),
        axis=(0.0, 0.0, 1.0),
        root_d=9.4,
        crest_d=10.5,
        length=18.0,
        pitch=2.0,
        color=C_BRASS_LIGHT,
    )
    if outlet_exposed:
        _add(
            scene,
            _cylinder(5.3, 0.6, (0.0, VALVE_AXIS_Y, VALVE_OUTLET_Z), (0.0, 0.0, 1.0)),
            "valve-open-waterway",
            C_GASKET,
        )
    _add_handle(scene, on=on)


def _add_faucet_supply(
    scene: cq.Assembly,
    *,
    connector_base,
    hose_points,
    free: bool,
) -> None:
    """Existing 3/8-inch braided faucet supply with swivel nut and crimp ferrule."""
    x, y, z = connector_base
    _add(
        scene,
        _hex_nut(18.5, 11.2, 19.0, connector_base, (0.0, 0.0, 1.0)),
        "faucet-supply-swivel-nut",
        C_CHROME,
    )
    _add(
        scene,
        _cylinder(13.0, 12.0, (x, y, z + 19.0), (0.0, 0.0, 1.0)),
        "faucet-supply-crimp-ferrule",
        C_CHROME_DARK,
    )
    for index, groove_z in enumerate((z + 21.0, z + 25.0, z + 29.0), start=1):
        _add(
            scene,
            _ring(13.8, 12.7, 0.7, (x, y, groove_z), (0.0, 0.0, 1.0)),
            f"faucet-supply-ferrule-groove-{index}",
            C_CHROME,
        )
    if free:
        _add(
            scene,
            _ring(10.8, 5.5, 0.7, connector_base, (0.0, 0.0, 1.0)),
            "faucet-supply-free-gasket",
            C_GASKET,
        )
    _add(
        scene,
        _round_sweep(hose_points, 5.1, (0.0, 0.0, 1.0), (0.0, 0.0, 1.0)),
        "existing-braided-three-eighths-faucet-hose",
        C_BRAID,
    )
    # A narrow raised strand is real geometry and gives the smooth STEP surface the highlight
    # break by which a stainless braided line is recognized at small scale.
    highlight_points = tuple((px + 3.7, py + 1.2, pz) for px, py, pz in hose_points)
    _add(
        scene,
        _round_sweep(highlight_points, 0.55, (0.0, 0.0, 1.0), (0.0, 0.0, 1.0)),
        "faucet-hose-braid-highlight",
        C_BRAID_HIGHLIGHT,
    )


def _add_tee(
    scene: cq.Assembly,
    *,
    origin=(0.0, VALVE_AXIS_Y, TEE_BOTTOM_Z),
    open_ports: bool,
) -> None:
    """Product-neutral 3/8 compression run x 1/4 compression side tee."""
    ox, oy, oz = origin
    _add(
        scene,
        _hex_nut(19.0, 11.2, 18.0, origin, (0.0, 0.0, 1.0)),
        "tee-bottom-three-eighths-swivel",
        C_CHROME,
    )
    _add(scene, _cylinder(12.0, 9.0, (ox, oy, oz + 18.0), (0.0, 0.0, 1.0)),
         "tee-bottom-neck", C_BRASS)
    _add(scene, _hex_prism(18.0, 18.0, (ox, oy, oz + 22.0), (0.0, 0.0, 1.0)),
         "tee-center-wrench-body", C_BRASS)
    _add_threaded_nipple(
        scene,
        name="tee-top-three-eighths-compression-thread",
        base=(ox, oy, oz + 40.0),
        axis=(0.0, 0.0, 1.0),
        root_d=9.4,
        crest_d=10.5,
        length=21.0,
        pitch=2.0,
        color=C_BRASS_LIGHT,
    )
    _add(scene, _cylinder(11.0, 32.0, (ox, oy, oz + 31.0), (1.0, 0.0, 0.0)),
         "tee-quarter-inch-branch-neck", C_BRASS)
    _add(scene, _hex_prism(14.0, 8.0, (ox + 24.0, oy, oz + 31.0), (1.0, 0.0, 0.0)),
         "tee-quarter-inch-branch-shoulder", C_BRASS)
    _add_threaded_nipple(
        scene,
        name="tee-quarter-inch-compression-thread",
        base=(ox + 31.0, oy, oz + 31.0),
        axis=(1.0, 0.0, 0.0),
        root_d=7.7,
        crest_d=8.7,
        length=16.0,
        pitch=1.75,
        color=C_BRASS_LIGHT,
    )
    if open_ports:
        _add(scene, _ring(10.8, 5.4, 0.7, origin, (0.0, 0.0, 1.0)),
             "tee-free-bottom-gasket", C_GASKET)
        _add(scene, _cylinder(5.4, 0.6, (ox, oy, oz + 61.0), (0.0, 0.0, 1.0)),
             "tee-open-top-waterway", C_GASKET)
        _add(scene, _cylinder(4.0, 0.6, (ox + 47.0, oy, oz + 31.0), (1.0, 0.0, 0.0)),
             "tee-open-branch-waterway", C_GASKET)


def _add_appliance_branch(
    scene: cq.Assembly,
    *,
    connector_base,
    tube_points,
    free: bool,
) -> None:
    """White 1/4-inch appliance tube with a conventional compression nut and ferrule."""
    x, y, z = connector_base
    _add(scene, _hex_nut(14.0, 9.1, 18.0, connector_base, (1.0, 0.0, 0.0)),
         "appliance-branch-quarter-inch-nut", C_CHROME)
    _add(scene, _cylinder(9.3, 11.0, (x + 18.0, y, z), (1.0, 0.0, 0.0)),
         "appliance-branch-strain-relief", C_BRANCH_EDGE)
    if free:
        _add(scene, _ring(9.0, 3.8, 0.7, connector_base, (1.0, 0.0, 0.0)),
             "appliance-branch-free-gasket", C_GASKET)
    _add(
        scene,
        _round_sweep(tube_points, 3.175, (1.0, 0.0, 0.0), (0.0, 0.0, -1.0)),
        "white-quarter-inch-appliance-branch",
        C_BRANCH,
    )


def _base_scene(name: str, *, valve_on: bool, outlet_exposed: bool) -> cq.Assembly:
    scene = cq.Assembly(name=name)
    _add_static_wall(scene)
    _add_angle_stop(scene, on=valve_on, outlet_exposed=outlet_exposed)
    return scene


def _direct_faucet_scene(name: str, *, valve_on: bool) -> cq.Assembly:
    scene = _base_scene(name, valve_on=valve_on, outlet_exposed=False)
    _add_faucet_supply(
        scene,
        connector_base=(0.0, VALVE_AXIS_Y, 132.0),
        hose_points=(
            (0.0, VALVE_AXIS_Y, 163.0),
            (-2.0, 56.0, 187.0),
            (-19.0, 65.0, 239.0),
            (-37.0, 66.0, 286.0),
            (-42.0, 65.0, 340.0),
        ),
        free=False,
    )
    return scene


def _pre_tee_scene() -> cq.Assembly:
    scene = _base_scene("plumbing-pre-tee", valve_on=False, outlet_exposed=True)
    _add_faucet_supply(
        scene,
        connector_base=(-24.0, VALVE_AXIS_Y, 182.0),
        hose_points=(
            (-24.0, VALVE_AXIS_Y, 213.0),
            (-25.0, 56.0, 237.0),
            (-34.0, 64.0, 281.0),
            (-42.0, 65.0, 340.0),
        ),
        free=True,
    )

    # Both new pieces are physically staged to the installer's right, preserving clear air at
    # every mating face.  The tee remains upright, so the next frame can be read as one seating
    # action rather than an unexplained reorientation.
    staged_tee = (45.0, 77.0, TEE_BOTTOM_Z + 20.0)
    _add_tee(scene, origin=staged_tee, open_ports=True)
    staged_branch_z = staged_tee[2] + 31.0
    _add_appliance_branch(
        scene,
        connector_base=(130.0, staged_tee[1], staged_branch_z),
        tube_points=(
            (159.0, staged_tee[1], staged_branch_z),
            (181.0, staged_tee[1], staged_branch_z),
            (176.0, 78.0, 155.0),
            (166.0, 78.0, 124.0),
            (158.0, 76.0, 69.0),
            (153.0, 75.0, -15.0),
        ),
        free=True,
    )
    return scene


def _tee_installed_scene() -> cq.Assembly:
    scene = _base_scene("plumbing-tee-installed", valve_on=False, outlet_exposed=False)
    _add_tee(scene, open_ports=False)
    _add_faucet_supply(
        scene,
        connector_base=(0.0, VALVE_AXIS_Y, 180.0),
        hose_points=(
            (0.0, VALVE_AXIS_Y, 211.0),
            (-4.0, 57.0, 231.0),
            (-22.0, 64.0, 267.0),
            (-38.0, 66.0, 300.0),
            (-42.0, 65.0, 340.0),
        ),
        free=False,
    )
    _add_appliance_branch(
        scene,
        connector_base=(35.0, VALVE_AXIS_Y, TEE_BRANCH_Z),
        tube_points=(
            (64.0, VALVE_AXIS_Y, TEE_BRANCH_Z),
            (82.0, 58.0, 158.0),
            (111.0, 69.0, 137.0),
            (132.0, 75.0, 98.0),
            (148.0, 76.0, 45.0),
            (153.0, 75.0, -15.0),
        ),
        free=False,
    )
    return scene


def build_scenes() -> dict[str, cq.Assembly]:
    return {
        "plumbing-valve-on": _direct_faucet_scene("plumbing-valve-on", valve_on=True),
        "plumbing-valve-off": _direct_faucet_scene("plumbing-valve-off", valve_on=False),
        "plumbing-pre-tee": _pre_tee_scene(),
        "plumbing-tee-installed": _tee_installed_scene(),
    }


def _render(step_paths: dict[str, Path], art_dir: Path) -> None:
    jobs = []
    for name in SCENE_NAMES:
        jobs.append(
            {
                "step": step_paths[name].relative_to(HARDWARE).as_posix(),
                "out": str(art_dir / f"{name}.png"),
                "cam": RENDER_CAM,
                "target": RENDER_TARGET,
                "up": RENDER_UP,
                "span": RENDER_ORTHO_SPAN,
                "size": RENDER_SIZE,
                "bg": "#ffffff",
                "trim": False,
                "solid": True,
                "ortho": True,
                "ground": False,
                "fog": False,
            }
        )
    subprocess.run(
        ["node", str(RENDERER), "--jobs", "-"],
        cwd=ROOT,
        input=json.dumps(jobs),
        text=True,
        check=True,
    )
    expected_size = tuple(int(value) for value in RENDER_SIZE.split("x"))
    for name in SCENE_NAMES:
        path = art_dir / f"{name}.png"
        with Image.open(path) as image:
            if image.size != expected_size:
                raise RuntimeError(f"unexpected render size {image.size}: {path}")
            canonical = image.convert("RGBA")
            canonical.save(path, format="PNG", compress_level=9, optimize=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT,
        help=f"STEP/PNG output directory (default: {OUT.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--render",
        dest="render",
        action="store_true",
        help="render the four registered 2000x1100 instruction PNGs (the default)",
    )
    parser.add_argument(
        "--steps-only",
        dest="render",
        action="store_false",
        help="export only the STEP and mesh intermediates",
    )
    parser.add_argument(
        "--art-dir",
        type=Path,
        default=ART,
        help=f"PNG output directory (default: {ART.relative_to(ROOT)})",
    )
    parser.set_defaults(render=True)
    args = parser.parse_args()
    output_dir = args.out_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes = build_scenes()
    if tuple(scenes) != SCENE_NAMES:
        raise RuntimeError(f"scene order/name drift: {tuple(scenes)}")

    step_paths = {}
    for name, scene in scenes.items():
        compound = scene.toCompound()
        if not compound.isValid():
            raise RuntimeError(f"invalid scene compound: {name}")
        bounds = compound.BoundingBox()
        path = output_dir / f"{name}.step"
        export_assembly(scene, str(path))
        step_paths[name] = path
        print(
            f"{name}: "
            f"X[{bounds.xmin:.1f},{bounds.xmax:.1f}] "
            f"Y[{bounds.ymin:.1f},{bounds.ymax:.1f}] "
            f"Z[{bounds.zmin:.1f},{bounds.zmax:.1f}] -> {path}"
        )

    if args.render:
        art_dir = args.art_dir.resolve()
        art_dir.mkdir(parents=True, exist_ok=True)
        _render(step_paths, art_dir)
        for name in SCENE_NAMES:
            print(f"rendered -> {art_dir / f'{name}.png'}")


if __name__ == "__main__":
    main()
