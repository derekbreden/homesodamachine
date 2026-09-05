"""Lee Spring LCM060C12M metric compression spring reference.

The catalog dimensions come from Lee Spring's product page:
https://www.leespring.com/product/compression-spring-lcm060c12m-music-wire

This source builds one spring with its bearing planes at local Z=0 and
Z=`installed_length`.  The changing pitch is a kinematic CAD representation of an
installed spring, not a structural simulation.  `catalog_load_estimate()` is kept
separate from `build()` so the solid itself never purports to calculate force.

Run::

    tools/cad-venv/bin/python \
      hardware/reference/lee-lcm060c12m/lee_lcm060c12m.py
    tools/cad-venv/bin/python \
      hardware/reference/lee-lcm060c12m/lee_lcm060c12m.py selftest
    tools/cad-venv/bin/python \
      hardware/reference/lee-lcm060c12m/lee_lcm060c12m.py \
      --installed-length 18.322 --output-stem /tmp/lcm060c12m-18p322
"""

import argparse
import math
import sys
from pathlib import Path

import cadquery as cq


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step  # noqa: E402


PART_NUMBER = "LCM060C12M"
DISPLAY_PART_NUMBER = "LCM060C 12 M"

# Lee Spring's published metric values.  Dimensions are millimetres, rate is N/mm,
# and load is N.  The OD and rate tolerances are the published tolerances.
OUTSIDE_DIAMETER = 5.99
OUTSIDE_DIAMETER_TOLERANCE = (+0.08, -0.13)
INSIDE_DIAMETER = 4.78
WIRE_DIAMETER = 0.61
HOLE_DIAMETER = 6.40
ROD_DIAMETER = 4.39
FREE_LENGTH = 30.0
FREE_LENGTH_TOLERANCE = 0.99
SOLID_HEIGHT = 8.61
RATE = 0.688
RATE_TOLERANCE = 0.07
LOAD_AT_SOLID = 14.68
ACTIVE_COILS = 12.36
TOTAL_COILS = 14.36
ENDS = "squared and ground"
MATERIAL = "ASTM A228 music wire"
FINISH = "zinc plate and bake per ASTM B633"

# Model-only construction values.  One inactive turn at each end follows from the
# catalog's 14.36 total / 12.36 active coils.  The end centerline starts below one wire
# radius; clipping at the bearing planes leaves visible ground flats.  Neither value is
# a manufacturer drawing dimension.
END_COILS = (TOTAL_COILS - ACTIVE_COILS) / 2.0
MODEL_END_CENTER_Z = 0.20
MODEL_CENTERLINE_RADIUS = (OUTSIDE_DIAMETER - WIRE_DIAMETER) / 2.0
MODEL_INSIDE_DIAMETER = 2.0 * (MODEL_CENTERLINE_RADIUS - WIRE_DIAMETER / 2.0)
PATH_SAMPLES_PER_TURN = 28
# Reference-view mesh, not a printable appliance part.  The STEP remains the exact solid;
# this chord/angle pair keeps a 0.61 mm round wire legible without a multi-megabyte display
# mesh for fourteen turns.
MESH_TOLERANCE = 0.08
MESH_ANGLE = 0.35

STEP = _here.parent / "lee-lcm060c12m.step"
STL = _here.parent / "lee-lcm060c12m.stl"


def _checked_length(installed_length: float) -> float:
    """Return a finite catalog-range installed length, or raise ``ValueError``."""
    length = float(installed_length)
    if not math.isfinite(length):
        raise ValueError(f"installed length must be finite; got {installed_length!r}")
    if length < SOLID_HEIGHT - 1.0e-9 or length > FREE_LENGTH + 1.0e-9:
        raise ValueError(
            f"{PART_NUMBER} installed length must be between its {SOLID_HEIGHT:g} mm "
            f"solid height and {FREE_LENGTH:g} mm nominal free length; got {length:g} mm"
        )
    return min(FREE_LENGTH, max(SOLID_HEIGHT, length))


def bearing_planes(installed_length: float = FREE_LENGTH) -> tuple[float, float]:
    """The two local-Z bearing planes for the requested installed spring."""
    return (0.0, _checked_length(installed_length))


def catalog_load_estimate(installed_length: float) -> float:
    """Nominal one-spring load from the published linear rate, in newtons.

    This is a catalog arithmetic estimate, not a result extracted from the CAD and not
    a substitute for measuring preload, seat friction, buckling, or tolerance stack-up.
    """
    length = _checked_length(installed_length)
    return RATE * (FREE_LENGTH - length)


def centerline(installed_length: float = FREE_LENGTH) -> cq.Wire:
    """Return the model-only variable-pitch centerline for one installed spring.

    The first and last nominal inactive turns each rise one wire diameter.  The active
    turns divide the remaining bearing-plane distance uniformly.  A spline through 28
    points per turn rounds the two pitch transitions without claiming a winding-tool
    path or a stress solution.
    """
    length = _checked_length(installed_length)
    centerline_rise = length - 2.0 * MODEL_END_CENTER_Z
    end_rise = WIRE_DIAMETER
    active_rise = centerline_rise - 2.0 * end_rise
    if active_rise <= 0.0:
        raise ValueError(
            f"{length:g} mm leaves no positive rise for {ACTIVE_COILS:g} active coils"
        )

    samples = math.ceil(TOTAL_COILS * PATH_SAMPLES_PER_TURN)
    points = []
    for i in range(samples + 1):
        turns = TOTAL_COILS * i / samples
        if turns <= END_COILS:
            z = MODEL_END_CENTER_Z + end_rise * turns / END_COILS
        elif turns <= END_COILS + ACTIVE_COILS:
            z = (
                MODEL_END_CENTER_Z
                + end_rise
                + active_rise * (turns - END_COILS) / ACTIVE_COILS
            )
        else:
            z = (
                MODEL_END_CENTER_Z
                + end_rise
                + active_rise
                + end_rise
                * (turns - END_COILS - ACTIVE_COILS)
                / END_COILS
            )
        angle = 2.0 * math.pi * turns
        points.append(
            cq.Vector(
                MODEL_CENTERLINE_RADIUS * math.cos(angle),
                MODEL_CENTERLINE_RADIUS * math.sin(angle),
                z,
            )
        )
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(points)])


def build(installed_length: float = FREE_LENGTH) -> cq.Shape:
    """Build one spring at ``installed_length``, along local +Z.

    Z=0 and Z=``installed_length`` are the ground bearing planes.  The returned object
    is one valid solid throughout the catalog's solid-height-to-free-length range.  Pitch
    changes only to depict the requested envelope; use ``catalog_load_estimate`` for the
    separate nominal-rate arithmetic.
    """
    length = _checked_length(installed_length)
    path = centerline(length)
    swept = (
        cq.Workplane("XZ")
        .center(MODEL_CENTERLINE_RADIUS, MODEL_END_CENTER_Z)
        .circle(WIRE_DIAMETER / 2.0)
        .sweep(path, isFrenet=True)
        .val()
    )

    # The sweep extends below/above the bearing planes.  Intersecting it with this broad
    # prism makes the two catalogued ground ends literal planar faces.  Read vertex extrema
    # rather than OCCT's trimmed-surface bounding cache when checking those planes.
    clip_half = OUTSIDE_DIAMETER
    clip = cq.Solid.makeBox(
        2.0 * clip_half,
        2.0 * clip_half,
        length,
        cq.Vector(-clip_half, -clip_half, 0.0),
    )
    return swept.intersect(clip)


def export_model(
    installed_length: float = FREE_LENGTH,
    *,
    step_path: Path | str = STEP,
    stl_path: Path | str = STL,
) -> cq.Shape:
    """Build one spring and write its STEP and STL; return the exported solid."""
    length = _checked_length(installed_length)
    step_path = Path(step_path)
    stl_path = Path(stl_path)
    step_path.parent.mkdir(parents=True, exist_ok=True)
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    spring = build(length)
    # Writing the slicer mesh first also tells the STEP helper that this reference does not
    # need a second viewer-only mesh payload beside it.
    cq.exporters.export(
        spring,
        str(stl_path),
        tolerance=MESH_TOLERANCE,
        angularTolerance=MESH_ANGLE,
    )
    export_step(spring, str(step_path))
    print(
        f"-> {step_path} and {stl_path}  "
        f"{OUTSIDE_DIAMETER:g} mm OD x {length:g} mm installed length"
    )
    return spring


def _vertex_z_extrema(shape: cq.Shape) -> tuple[float, float]:
    zs = [vertex.Center().z for vertex in shape.Vertices()]
    return min(zs), max(zs)


def _ground_face_areas(shape: cq.Shape, length: float) -> tuple[float, float]:
    bottom = 0.0
    top = 0.0
    for face in shape.Faces():
        if face.geomType() != "PLANE":
            continue
        z = face.Center().z
        if math.isclose(z, 0.0, abs_tol=1.0e-5):
            bottom += face.Area()
        elif math.isclose(z, length, abs_tol=1.0e-5):
            top += face.Area()
    return bottom, top


def selftest() -> int:
    """Validate official constants and one-solid geometry across the usable range."""
    failures = []

    if not math.isclose(END_COILS, 1.0, abs_tol=1.0e-9):
        failures.append(f"catalog coil counts imply {END_COILS:g}, not one, end coil")
    if abs(MODEL_INSIDE_DIAMETER - INSIDE_DIAMETER) > 0.02:
        failures.append(
            f"OD/wire model implies {MODEL_INSIDE_DIAMETER:.3f} mm ID, too far from "
            f"catalog {INSIDE_DIAMETER:g} mm"
        )

    # Solid, representative compressed, and free states exercise both touching and open
    # pitches.  The carrier can ask build() for every intermediate length without new CAD.
    lengths = (SOLID_HEIGHT, 15.172, 18.322, 21.322, FREE_LENGTH)
    for length in lengths:
        spring = build(length)
        if not spring.isValid():
            failures.append(f"{length:g} mm spring is not a valid OCCT shape")
            continue
        if len(spring.Solids()) != 1:
            failures.append(f"{length:g} mm spring has {len(spring.Solids())} solids, not one")
        bb = spring.BoundingBox()
        radial_diameter = 2.0 * max(-bb.xmin, bb.xmax, -bb.ymin, bb.ymax)
        if not math.isclose(radial_diameter, OUTSIDE_DIAMETER, abs_tol=0.02):
            failures.append(
                f"{length:g} mm spring OD is {radial_diameter:.4f}, wants "
                f"{OUTSIDE_DIAMETER:g} mm"
            )
        z0, z1 = _vertex_z_extrema(spring)
        if not math.isclose(z0, 0.0, abs_tol=1.0e-5):
            failures.append(f"{length:g} mm lower bearing plane is Z={z0:.6f}")
        if not math.isclose(z1, length, abs_tol=1.0e-5):
            failures.append(
                f"{length:g} mm upper bearing plane is Z={z1:.6f}, wants {length:g}"
            )
        lower_area, upper_area = _ground_face_areas(spring, length)
        if lower_area <= 0.0 or upper_area <= 0.0:
            failures.append(
                f"{length:g} mm spring lacks ground faces "
                f"({lower_area:.4f}, {upper_area:.4f} mm^2)"
            )

    solid_estimate = catalog_load_estimate(SOLID_HEIGHT)
    if abs(solid_estimate - LOAD_AT_SOLID) > 0.10:
        failures.append(
            f"rate arithmetic gives {solid_estimate:.3f} N at solid, too far from "
            f"published {LOAD_AT_SOLID:g} N"
        )
    if catalog_load_estimate(FREE_LENGTH) != 0.0:
        failures.append("nominal free-length load estimate is not zero")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(
        f"PASS: {PART_NUMBER} is one valid Ø{OUTSIDE_DIAMETER:g} mm solid at "
        f"{', '.join(f'{length:g}' for length in lengths)} mm"
    )
    print("PASS: both local-Z bearing planes are flat at every validated length")
    print(
        f"PASS: nominal-rate estimate reaches {solid_estimate:.3f} N at "
        f"{SOLID_HEIGHT:g} mm (catalog {LOAD_AT_SOLID:g} N)"
    )
    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--installed-length",
        type=float,
        default=FREE_LENGTH,
        help=f"bearing-plane separation in mm ({SOLID_HEIGHT:g}..{FREE_LENGTH:g})",
    )
    parser.add_argument(
        "--output-stem",
        type=Path,
        help="path without suffix for a requested-state STEP and STL",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["selftest"]:
        return selftest()
    args = _parse_args(argv)
    length = _checked_length(args.installed_length)
    if args.output_stem is None:
        if not math.isclose(length, FREE_LENGTH, abs_tol=1.0e-9):
            sys.exit(
                "--output-stem is required for a non-free installed length so the canonical "
                "free-length reference files are not overwritten"
            )
        step_path, stl_path = STEP, STL
    else:
        step_path = args.output_stem.with_suffix(".step")
        stl_path = args.output_stem.with_suffix(".stl")
    export_model(length, step_path=step_path, stl_path=stl_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
