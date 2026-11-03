"""Native builders for manually requested plumbing views.

Loaded by _plumbing_native only when a manual tool requests a builder. Dimensions
and palettes are supplied by the active scene driver before this module loads.
"""
from __future__ import annotations

import math
import cadquery as cq
from _cadq_export import _atomic_write, _per_solid_color, _write_mesh_payload, import_step, note_write


def _vector(values) -> cq.Vector:
    return values if isinstance(values, cq.Vector) else cq.Vector(*values)

def _unit(values) -> cq.Vector:
    vector = _vector(values)
    if vector.Length <= 0.0:
        raise ValueError("a direction needs non-zero length")
    return vector.multiply(1.0 / vector.Length)

def _cylinder(diameter: float, length: float, base, axis) -> cq.Solid:
    return cq.Solid.makeCylinder(diameter / 2.0, length, _vector(base), _unit(axis))

def _ring(outer_d: float, inner_d: float, length: float, base, axis) -> cq.Shape:
    direction = _unit(axis)
    outer = _cylinder(outer_d, length, base, direction)
    inner = _cylinder(
        inner_d,
        length + 0.40,
        _vector(base) - direction.multiply(0.20),
        direction,
    )
    return outer.cut(inner)

def _tube(start, end) -> cq.Shape:
    """A hollow 1/4-inch LLDPE tube with true square-cut end faces."""
    first = _vector(start)
    last = _vector(end)
    vector = last - first
    direction = _unit(vector)
    outer = cq.Solid.makeCylinder(TUBE_OD / 2.0, vector.Length, first, direction)
    inner = cq.Solid.makeCylinder(
        TUBE_ID / 2.0,
        vector.Length + 0.40,
        first - direction.multiply(0.20),
        direction,
    )
    return outer.cut(inner)

def _swept_round(points: list[cq.Vector], radius: float) -> cq.Shape:
    path = cq.Wire.assembleEdges([cq.Edge.makeSpline(points)])
    first = points[0]
    plane = cq.Plane(
        origin=(first.x, first.y, first.z),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
    )
    return cq.Workplane(plane).circle(radius).sweep(path, isFrenet=True).val()

def _branch_points(
    start_z: float,
    *,
    tee_x: float = TEE_X,
    y: float = 0.0,
) -> list[cq.Vector]:
    return [
        cq.Vector(tee_x, y, start_z),
        cq.Vector(tee_x, y, start_z - 18.0),
        cq.Vector(tee_x + 7.0, y, start_z - 31.0),
        cq.Vector(tee_x + 28.0, y, start_z - 47.0),
        cq.Vector(tee_x + 75.0, y, start_z - 65.0),
        cq.Vector(tee_x + 170.0, y, start_z - 93.0),
        cq.Vector(tee_x + 360.0, y, start_z - 132.0),
    ]

def _branch(
    start_z: float,
    *,
    tee_x: float = TEE_X,
    open_end: bool = False,
) -> cq.Shape:
    outer = _swept_round(_branch_points(start_z, tee_x=tee_x), TUBE_OD / 2.0)
    if not open_end:
        return outer
    bore = _cylinder(
        TUBE_ID,
        8.2,
        (tee_x, 0.0, start_z + 0.2),
        (0.0, 0.0, -1.0),
    )
    return outer.cut(bore)

def _bore_witness(face, inward) -> cq.Solid:
    """A recessed dark disk that makes a free square tube end legible."""
    direction = _unit(inward)
    start = _vector(face) + direction.multiply(0.28)
    return cq.Solid.makeCylinder(TUBE_ID / 2.0, 0.22, start, direction)

def _add(scene: cq.Assembly, shape: cq.Shape, name: str, color) -> None:
    if not shape.isValid():
        raise RuntimeError(f"invalid shape: {name}")
    scene.add(shape, name=name, color=color if isinstance(color, cq.Color) else cq.Color(*color))

def _pp0208e_parts(center=(0.0, 0.0, 0.0)) -> tuple[cq.Shape, tuple[cq.Shape, ...]]:
    """A dimensionally held PP0208E instruction solid from the official drawing.

    The three-port topology and every published envelope/port/tube dimension
    are exact.  The official sheet does not dimension the minor cosmetic
    breakpoints along each arm, so those are a restrained symmetric profile:
    a 10.6-mm barrel, a full-16.3-mm collar body, and an annular release collet.
    """
    collar_near = 8.2
    collet_near = 16.3
    barrel_d = 10.6
    collet_d = 9.7
    collet_bore = 6.70

    arms = (
        ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)),
        ((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        ((0.0, 0.0, -1.0), (0.0, 0.0, 1.0)),
    )
    body = cq.Solid.makeSphere(barrel_d / 2.0)
    collets = []
    for axis, inward in arms:
        axis_v = _vector(axis)
        body = body.fuse(
            _cylinder(barrel_d, collar_near, (0.0, 0.0, 0.0), axis),
            _cylinder(
                PP0208_MAX_OD,
                collet_near - collar_near,
                axis_v.multiply(collar_near),
                axis,
            ),
        )
        collets.append(
            _ring(
                collet_d,
                collet_bore,
                PP0208_REACH - collet_near,
                axis_v.multiply(collet_near),
                axis,
            )
        )

        face = axis_v.multiply(PP0208_REACH)
        socket_stop = face + _vector(inward).multiply(PP0208_INSERTION)
        socket = _cylinder(
            PP0208_TUBE_OD,
            PP0208_INSERTION + 0.2,
            socket_stop - _vector(inward).multiply(0.1),
            axis,
        )
        body = body.cut(socket)

    run_bore = _cylinder(
        PP0208_BORE,
        PP0208_RUN_SPAN + 0.4,
        (-PP0208_REACH - 0.2, 0.0, 0.0),
        (1.0, 0.0, 0.0),
    )
    branch_bore = _cylinder(
        PP0208_BORE,
        PP0208_REACH + 0.2,
        (0.0, 0.0, -PP0208_REACH - 0.2),
        (0.0, 0.0, 1.0),
    )
    body = body.cut(run_bore.fuse(branch_bore))

    translation = cq.Vector(*center)
    return body.translate(translation), tuple(part.translate(translation) for part in collets)

def _add_tee(scene: cq.Assembly, *, center_x: float) -> None:
    body, collets = _pp0208e_parts((center_x, 0.0, AXIS_Z))
    _add(scene, body, "pp0208e-body", C_TEE_BODY)
    for index, collet in enumerate(collets, start=1):
        _add(scene, collet, f"pp0208e-release-collet-{index}", C_TEE_COLLET)

def _canonical_union_parts(
    *,
    pressed_right: bool,
    separate_right: bool = False,
) -> tuple[cq.Shape, ...]:
    union = import_step(str(union_ref.STEP)).val()
    if not pressed_right and not separate_right:
        return (union,)

    sleeve_start = union_ref.ring_face_z
    sleeve_end = union_ref.port_face_z
    erase = _cylinder(
        union_ref.COLLET_D + 0.4,
        sleeve_end - sleeve_start + 0.4,
        (0.0, 0.0, sleeve_start - 0.2),
        (0.0, 0.0, 1.0),
    )
    body = union.cut(erase)
    sleeve = _ring(
        union_ref.COLLET_D,
        union_ref.COLLET_BORE,
        sleeve_end - sleeve_start,
        (
            0.0,
            0.0,
            sleeve_start - (ILLUSTRATED_COLLET_TRAVEL if pressed_right else 0.0),
        ),
        (0.0, 0.0, 1.0),
    )
    return body, sleeve

def _add_union(
    scene: cq.Assembly,
    *,
    center=(UNION_X, 0.0, AXIS_Z),
    pressed_right: bool = False,
    highlight_right: bool = False,
) -> None:
    parts = _canonical_union_parts(
        pressed_right=pressed_right,
        separate_right=highlight_right,
    )
    for index, part in enumerate(parts, start=1):
        posed = part.rotate((0, 0, 0), (0, 1, 0), 90.0).translate(center)
        color = C_TOUCHED_COLLET if highlight_right and index == 2 else C_WATER_WHITE
        _add(scene, posed, f"existing-pp0408w-{index}", color)

def _add_source_line(scene: cq.Assembly) -> None:
    stop_x = UNION_LEFT_FACE + UNION_INSERTION
    _add(
        scene,
        _tube((-SCENE_END, 0.0, AXIS_Z), (stop_x, 0.0, AXIS_Z)),
        "existing-source-lldpe",
        C_WATER_WHITE,
    )

def _add_original_line(scene: cq.Assembly, *, destination: str) -> None:
    if destination == "union":
        start_x = UNION_RIGHT_FACE - UNION_INSERTION
    elif destination == "tee":
        start_x = TEE_RIGHT_FACE - PP0208_INSERTION
    elif destination == "release-started":
        start_x = RELEASE_STARTED_X
    elif destination == "tee-staged":
        start_x = TEE_RIGHT_FACE + ORIGINAL_STAGE_GAP
    else:
        raise ValueError(f"unknown original-line destination: {destination}")
    _add(
        scene,
        _tube((start_x, 0.0, AXIS_Z), (SCENE_END, 0.0, AXIS_Z)),
        "existing-downstream-lldpe",
        C_WATER_WHITE,
    )
    if destination == "tee-staged":
        _add(
            scene,
            _bore_witness((start_x, 0.0, AXIS_Z), (1.0, 0.0, 0.0)),
            "existing-downstream-free-bore",
            C_CUT_BORE,
        )

def _add_assembly_stub(scene: cq.Assembly, *, tee_x: float, staged: bool) -> None:
    tee_left_face = tee_x - PP0208_REACH
    start_x = tee_left_face - ASSEMBLY_FACE_GAP - UNION_INSERTION
    stop_x = tee_left_face + PP0208_INSERTION
    _add(
        scene,
        _tube((start_x, 0.0, AXIS_Z), (stop_x, 0.0, AXIS_Z)),
        "supplied-assembly-stub",
        C_WATER_WHITE,
    )
    if staged:
        _add(
            scene,
            _bore_witness((start_x, 0.0, AXIS_Z), (1.0, 0.0, 0.0)),
            "supplied-stub-free-bore",
            C_CUT_BORE,
        )

def _add_connected_branch(
    scene: cq.Assembly,
    *,
    tee_x: float = TEE_X,
    tugged: bool = False,
) -> None:
    insertion = PP0208_INSERTION - (3.2 if tugged else 0.0)
    start_z = TEE_BRANCH_FACE_Z + insertion
    _add(
        scene,
        _branch(start_z, tee_x=tee_x),
        "filter-to-appliance-branch",
        C_WATER_WHITE,
    )

def _add_shipped_assembly(
    scene: cq.Assembly,
    *,
    tee_x: float,
    staged: bool,
    branch_tugged: bool = False,
) -> None:
    _add_tee(scene, center_x=tee_x)
    _add_assembly_stub(scene, tee_x=tee_x, staged=staged)
    _add_connected_branch(scene, tee_x=tee_x, tugged=branch_tugged)

def build_release_ready() -> cq.Assembly:
    scene = cq.Assembly(name="modern-release-ready")
    _add_union(scene, pressed_right=False, highlight_right=True)
    _add_source_line(scene)
    _add_original_line(scene, destination="union")
    return scene

def build_release_pressed() -> cq.Assembly:
    scene = cq.Assembly(name="modern-release-pressed")
    _add_union(scene, pressed_right=True, highlight_right=True)
    _add_source_line(scene)
    _add_original_line(scene, destination="union")
    return scene

def build_release_withdrawn() -> cq.Assembly:
    scene = cq.Assembly(name="modern-release-withdrawn")
    # Hold the highlighted collar depressed while the tube begins to move clear.
    _add_union(scene, pressed_right=True, highlight_right=True)
    _add_source_line(scene)
    _add_original_line(scene, destination="release-started")
    return scene

def _tee_scene(name: str) -> cq.Assembly:
    scene = cq.Assembly(name=name)
    _add_union(scene, pressed_right=False)
    _add_source_line(scene)
    return scene

def build_tee_assembly_ready() -> cq.Assembly:
    scene = _tee_scene("modern-tee-assembly-ready")
    _add_shipped_assembly(scene, tee_x=TEE_STAGED_X, staged=True)
    return scene

def build_tee_line_ready() -> cq.Assembly:
    scene = _tee_scene("modern-tee-line-ready")
    _add_shipped_assembly(scene, tee_x=TEE_X, staged=False)
    _add_original_line(scene, destination="tee-staged")
    return scene

def build_tee_complete() -> cq.Assembly:
    scene = _tee_scene("modern-tee-complete")
    _add_shipped_assembly(scene, tee_x=TEE_X, staged=False)
    _add_original_line(scene, destination="tee")
    return scene

def _add_modern_shutoff(scene: cq.Assembly, *, on: bool) -> None:
    body_left = WIDE_VALVE_X - 28.0
    _add(
        scene,
        _cylinder(24.0, 56.0, (body_left, 0.0, WIDE_AXIS_Z), (1.0, 0.0, 0.0)),
        "quarter-turn-shutoff-body",
        C_VALVE_BODY,
    )
    for suffix, x, axis in (
        ("left", body_left, (-1.0, 0.0, 0.0)),
        ("right", body_left + 56.0, (1.0, 0.0, 0.0)),
    ):
        _add(scene, _cylinder(16.0, 7.0, (x, 0.0, WIDE_AXIS_Z), axis),
             f"shutoff-ptc-shoulder-{suffix}", C_VALVE_SHOULDER)
        _add(scene, _ring(9.7, 6.70, 3.2,
                         _vector((x, 0.0, WIDE_AXIS_Z)) + _vector(axis).multiply(7.0), axis),
             f"shutoff-release-collet-{suffix}", C_STEM)

    _add(scene, _cylinder(9.0, 13.0, (WIDE_VALVE_X, 0.0, WIDE_AXIS_Z + 8.0),
                          (0.0, 0.0, 1.0)), "shutoff-stem", C_STEM)
    hub_z = WIDE_AXIS_Z + 21.0
    handle = cq.Solid.makeBox(62.0, 9.0, 5.0,
                              cq.Vector(WIDE_VALVE_X - 31.0, -4.5, hub_z))
    handle = handle.fuse(
        _cylinder(12.0, 5.0, (WIDE_VALVE_X, 0.0, hub_z), (0.0, 0.0, 1.0))
    )
    if not on:
        handle = handle.rotate(
            (WIDE_VALVE_X, 0.0, hub_z),
            (WIDE_VALVE_X, 0.0, hub_z + 1.0),
            90.0,
        )
    _add(scene, handle, "quarter-turn-blue-handle", C_HANDLE)

    valve_left_face = body_left - 10.2
    valve_right_face = body_left + 66.2
    wide_union_left = WIDE_UNION_X - UNION_REACH
    wide_union_right = WIDE_UNION_X + UNION_REACH
    _add(scene, _tube((-SCENE_END, 0.0, WIDE_AXIS_Z),
                      (valve_left_face + 5.0, 0.0, WIDE_AXIS_Z)),
         "household-source-lldpe", C_WATER_WHITE)
    _add(scene, _tube((valve_right_face - 5.0, 0.0, WIDE_AXIS_Z),
                      (wide_union_left + UNION_INSERTION, 0.0, WIDE_AXIS_Z)),
         "household-line-before-union", C_WATER_WHITE)
    _add_union(scene, center=(WIDE_UNION_X, 0.0, WIDE_AXIS_Z), pressed_right=False)
    _add(scene, _tube((wide_union_right - UNION_INSERTION, 0.0, WIDE_AXIS_Z),
                      (SCENE_END, 0.0, WIDE_AXIS_Z)),
         "household-line-after-union", C_WATER_WHITE)

def build_water_on() -> cq.Assembly:
    scene = cq.Assembly(name="modern-water-on")
    _add_modern_shutoff(scene, on=True)
    return scene

def build_water_off() -> cq.Assembly:
    scene = cq.Assembly(name="modern-water-off")
    _add_modern_shutoff(scene, on=False)
    return scene

def _export_scene(scene: cq.Assembly, target: Path) -> None:
    compound = scene.toCompound()
    if not compound.isValid():
        raise RuntimeError(f"invalid scene compound: {scene.name}")
    colored = _per_solid_color(scene)
    _atomic_write(target, lambda path: colored.export(str(path)))
    _write_mesh_payload(target, colored)
