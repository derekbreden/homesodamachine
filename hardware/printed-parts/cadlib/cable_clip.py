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


from _scalar_provider import call as _rust_scalar
globals().update(_rust_scalar('scalar.constants',group='cable_clip'))


# The two dark regions in the user's profile, in (outward, up).  Every
# vertex lands on the 3 mm grid; the lower arm reaches the full 9 mm and the
# upper arm reaches 6 mm.  The space between them is the continuous S-shaped
# cable channel below.
#
# THE SEAT IS THE TALL PART OF THAT CHANNEL, not the neck above it.  The cable
# lies in the pocket the lower arm's own face makes against the host wall — the
# `(2, 4)` to `(2, 7)` run, three grid of full 6 mm depth — and the S above it is
# what it is pressed past to get there.  A seat one grid tall took a flat ribbon
# and nothing else; at three it takes a round bundle, and the neck still closes
# over whatever went in.  Everything above that face stands one seat higher for
# it and the profile keeps every vertex on the grid.


def projection(embed):
    return _rust_scalar('scalar.clip_projection',embed=embed)


def seat_top():
    return _rust_scalar('scalar.clip_seat_top')


def seat_height():
    return _rust_scalar('scalar.clip_seat_height')


def channel_mouth():
    return _rust_scalar('scalar.clip_channel_mouth')


def required_wall(embed):
    return _rust_scalar('scalar.clip_required_wall',embed=embed)


def _scaled(points,x_shift=0.):
    return tuple(tuple(p) for p in _rust_scalar('scalar.clip_scaled',points=points,x_shift=x_shift))


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


def _unit(vector,label):
    return cq.Vector(*_rust_scalar('scalar.clip_unit',vector=vector,label=label))


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
    """Exercise the three stated embedments."""
    for embed, wall_thickness, proud in ((0.0, 3.0, 9.0),
                                         (6.0, 9.0, 3.0),
                                         (9.0, 12.0, 0.0)):
        addition, cutter = local_geometry(embed=embed, wall_thickness=wall_thickness)
        if (addition is not None and addition.Volume() <= 0.0) or cutter.Volume() <= 0.0:
            raise AssertionError("cable-clip geometry did not make valid solids")
        # The wall is sized off the profile, so it still holds the whole clip when the
        # section changes: the run lies along its −Y and the profile stands up its +Z.
        wall = cq.Solid.makeBox(
            wall_thickness, RUN + 2.0 * GRID, HEIGHT + 2.0 * GRID,
            cq.Vector(-wall_thickness, 0.0, 0.0),
        )
        clipped = apply(
            cq.Workplane(obj=wall),
            origin=(0.0, RUN + GRID, GRID),
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


def selftest():
    check()
    return ["  embed 0/6/9 mm: one valid solid, projection 9/3/0 mm"]


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        for line in selftest():
            print(line)
        print("cable_clip selftest OK")
    else:
        check()
        print("cable clip: 0/6/9 mm embedments valid; projections 9/3/0 mm")
