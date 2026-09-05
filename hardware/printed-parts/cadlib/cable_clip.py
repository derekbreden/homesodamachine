"""Wall-integrated cable clip.

The clip is the same 3 mm-grid profile at every wall thickness.  ``embed``
moves that profile into the host wall:

* 0 mm embedded leaves the full 9 mm projection;
* 6 mm embedded leaves 3 mm proud;
* 9 mm embedded leaves the outside face flush.

Local +X points out of the host wall, local +Y points up the profile, and
local +Z follows the retained cable.  ``apply`` maps that frame onto any
orthogonal wall.  The two ends of an embedded channel ramp from the wall
face to the recessed section so a cable never has to turn through a step.
"""

import math
import sys

import cadquery as cq


GRID = 3.0
DEPTH = 3.0 * GRID
BACKING = GRID
HEIGHT = 11.0 * GRID
RUN = 6.0 * GRID
RAMP = 2.0 * GRID
OVERLAP = 0.05


# The two dark regions in the user's profile, in (outward, up).  Every
# vertex lands on the 3 mm grid; the lower arm reaches the full 9 mm and the
# upper arm reaches 6 mm.  The space between them is the continuous S-shaped
# cable channel below.
_UPPER = (
    (0.0, 8.0), (2.0, 10.0), (2.0, 11.0), (0.0, 11.0),
)
_LOWER = (
    (0.0, 0.0), (3.0, 3.0), (3.0, 8.0), (2.0, 8.0),
    (1.0, 7.0), (1.0, 6.0), (2.0, 5.0), (2.0, 4.0),
    (0.0, 4.0),
)
_CHANNEL = (
    (3.0, 8.0), (2.0, 10.0), (0.0, 8.0), (0.0, 4.0),
    (2.0, 4.0), (2.0, 5.0), (1.0, 6.0), (1.0, 7.0),
    (2.0, 8.0),
)


def projection(embed):
    """How far the completed clip stands proud of the wall."""
    return DEPTH - float(embed)


def required_wall(embed):
    """Minimum host-wall thickness, including the backing behind the channel."""
    return float(embed) + BACKING


def _scaled(points, x_shift=0.0):
    return tuple((x * GRID + x_shift, y * GRID) for x, y in points)


def _prism(points, run):
    return cq.Workplane("XY").polyline(_scaled(points)).close().extrude(run).val()


def _channel_loft(embed, run, ramp):
    """The channel cutter, recessed in its middle and at the wall face at both ends."""
    sections = (
        (0.0, 0.0),
        (ramp, -embed),
        (run - ramp, -embed),
        (run, 0.0),
    )
    wires = [
        cq.Wire.makePolygon(
            [cq.Vector(x, y, z) for x, y in _scaled(_CHANNEL, shift)],
            close=True,
        )
        for z, shift in sections
    ]
    return cq.Solid.makeLoft(wires, True)


def local_geometry(*, embed, wall_thickness, run=RUN, ramp=RAMP):
    """Return ``(addition, cutter)`` in the clip's local frame.

    The wall face is X=0 and host material lies at X<=0.  ``addition`` is
    clipped to the air side; ``cutter`` is the longitudinally ramped channel.
    """
    embed = float(embed)
    wall_thickness = float(wall_thickness)
    run = float(run)
    ramp = float(ramp)
    if not 0.0 <= embed <= DEPTH:
        raise ValueError(f"cable-clip embed must be between 0 and {DEPTH:g} mm")
    if wall_thickness + 1e-9 < required_wall(embed):
        raise ValueError(
            f"a cable clip embedded {embed:g} mm needs a {required_wall(embed):g} mm "
            f"wall ({BACKING:g} mm backing); got {wall_thickness:g} mm")
    if ramp <= 0.0 or run < 2.0 * ramp:
        raise ValueError("cable-clip run must hold two positive end ramps")

    addition = None
    if projection(embed) > 1e-9:
        shifted = []
        for profile in (_UPPER, _LOWER):
            body = _prism(profile, run).translate((-embed, 0.0, 0.0))
            # A face-only union is not a mechanical root and is not reliably one
            # OCCT solid.  The duplicate extends the wallward edge by 0.05 mm;
            # the stated projection is still set by the unshifted copy.
            shifted.append(body.fuse(body.translate((-OVERLAP, 0.0, 0.0))))
        outside = cq.Solid.makeBox(
            DEPTH + OVERLAP, HEIGHT + 2.0 * OVERLAP, run + 2.0 * OVERLAP,
            cq.Vector(-OVERLAP, -OVERLAP, -OVERLAP),
        )
        addition = shifted[0].fuse(shifted[1]).intersect(outside)
    cutter = _channel_loft(embed, run, ramp)
    return addition, cutter


def _unit(vector, label):
    v = cq.Vector(*vector)
    length = v.Length
    if length <= 1e-9:
        raise ValueError(f"cable-clip {label} axis has zero length")
    return cq.Vector(v.x / length, v.y / length, v.z / length)


def apply(solid, *, origin, outward, along, embed, wall_thickness,
          run=RUN, ramp=RAMP):
    """Fuse and cut one clip into ``solid`` at a wall face.

    ``origin`` is the profile's lower corner at the start of its run.
    ``outward`` is the wall normal toward air, and ``along`` is the direction
    the cable travels.  Their cross product is the profile's +Y direction.
    """
    x_dir = _unit(outward, "outward")
    z_dir = _unit(along, "along")
    if abs(x_dir.dot(z_dir)) > 1e-8:
        raise ValueError("cable-clip outward and along axes must be perpendicular")
    addition, cutter = local_geometry(
        embed=embed, wall_thickness=wall_thickness, run=run, ramp=ramp)
    location = cq.Location(cq.Plane(origin=origin, xDir=x_dir, normal=z_dir))
    host = solid.val() if hasattr(solid, "val") else solid
    if addition is not None:
        host = host.fuse(addition.moved(location))
    return cq.Workplane(obj=host.cut(cutter.moved(location)))


def check():
    """Exercise the three stated embedments and their wall-thickness bound."""
    for embed, wall_thickness, proud in ((0.0, 3.0, 9.0),
                                         (6.0, 9.0, 3.0),
                                         (9.0, 12.0, 0.0)):
        addition, cutter = local_geometry(embed=embed, wall_thickness=wall_thickness)
        if (addition is not None and addition.Volume() <= 0.0) or cutter.Volume() <= 0.0:
            raise AssertionError("cable-clip geometry did not make valid solids")
        if not math.isclose(projection(embed), proud, abs_tol=1e-9):
            raise AssertionError("cable-clip projection no longer follows embedment")
        wall = cq.Solid.makeBox(
            wall_thickness, 50.0, 45.0,
            cq.Vector(-wall_thickness, 0.0, 0.0),
        )
        clipped = apply(
            cq.Workplane(obj=wall),
            origin=(0.0, 34.0, 6.0),
            outward=(1.0, 0.0, 0.0),
            along=(0.0, -1.0, 0.0),
            embed=embed,
            wall_thickness=wall_thickness,
        )
        result = clipped.val()
        if not result.isValid() or len(clipped.solids().vals()) != 1:
            raise AssertionError("cable clip did not remain one valid solid with its wall")
        if not math.isclose(result.BoundingBox().xmax, proud, abs_tol=1e-6):
            raise AssertionError("built cable-clip projection differs from its stated value")
        try:
            local_geometry(embed=embed, wall_thickness=wall_thickness - 0.01)
        except ValueError:
            pass
        else:
            raise AssertionError("a cable clip accepted a wall without its backing")


def selftest():
    check()
    return ["  embed 0/6/9 mm: one valid solid, projection 9/3/0 mm, backing 3 mm"]


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        for line in selftest():
            print(line)
        print("cable_clip selftest OK")
    else:
        check()
        print("cable clip: 0/6/9 mm embedments valid; projections 9/3/0 mm")
