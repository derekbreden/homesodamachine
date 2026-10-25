"""Paired Reservoir A seats and tie passages in the appliance world frame.

Run native CAD work through the shared queue. ``supports`` adds the bearing
stock to the lid; ``cuts`` opens the belt slot and its two threading mouths.
The aft slot's east mouth lies beyond the lid edge and opens directly to air.
"""
from pathlib import Path
import json
import math


HERE = Path(__file__).resolve().parent


def specification():
    return json.loads((HERE / "reservoir-a-anchors.json").read_text())


def datums():
    spec = specification()
    result = {}
    for station in spec["stations"]:
        first, last = station["tube_centers_world_mm"]
        x0, x1 = first[0], last[0]
        y = first[1]
        half = spec["station_length_mm"] / 2
        slot_half = spec["tie_slot_width_y_mm"] / 2
        outer = spec["tie_access_outer_offset_mm"]
        inner = spec["tie_access_inner_offset_mm"]
        result[station["id"]] = {
            **station,
            "stock_bounds_mm": [
                [x0 - spec["stock_west_of_first_tube_mm"], y-half, spec["root_z_mm"]],
                [x1 + spec["stock_east_of_last_tube_mm"], y+half, spec["seat_top_z_mm"]],
            ],
            "tie_slot_bounds_mm": [
                [x0-outer-.1, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                [x1+outer+.1, y+slot_half, spec["tie_slot_top_z_mm"]],
            ],
            "access_bounds_mm": [
                [[x0-outer-.1, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [x0-inner, y+slot_half, spec["seat_top_z_mm"]+.1]],
                [[x1+inner, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [x1+outer+.1, y+slot_half, spec["seat_top_z_mm"]+.1]],
            ],
        }
    return result


def _box(bounds):
    import cadquery as cq
    lo, hi = bounds
    return cq.Solid.makeBox(*(b-a for a, b in zip(lo, hi)), cq.Vector(*lo))


def cuts():
    """Subtract these after fusing each corresponding seat into its lid."""
    return {name: _box(row["tie_slot_bounds_mm"]).fuse(
                *(_box(b) for b in row["access_bounds_mm"])).clean()
            for name, row in datums().items()}


def supports():
    """Shallow open seats; no snap lips, caps or additional fasteners."""
    import cadquery as cq
    spec = specification()
    passages = cuts()
    result = {}
    for name, row in datums().items():
        body = _box(row["stock_bounds_mm"])
        for x, y, z in row["tube_centers_world_mm"]:
            bore = cq.Solid.makeCylinder(
                spec["seat_radius_mm"], spec["station_length_mm"]+.2,
                cq.Vector(x, y-spec["station_length_mm"]/2-.1, z), cq.Vector(0, 1, 0))
            body = body.cut(bore)
        result[name] = body.cut(passages[name]).clean()
    return result


def tie_profile(row):
    """A closed X/Z centerline for a trimmed narrow tie, without a loose tail."""
    spec = specification()
    first, last = row["tube_centers_world_mm"]
    x0, x1, z = first[0], last[0], first[2]
    radius = spec["tie_witness_outer_bend_radius_mm"]
    bottom = spec["tie_witness_bottom_center_z_mm"]
    turn = 1.5
    points = []

    def arc(x, zz, r, a, b):
        for i in range(13):
            t = a+(b-a)*i/12
            points.append((x+r*math.cos(t), zz+r*math.sin(t)))

    arc(x0, z, radius, math.pi, math.pi/2)
    arc(x1, z, radius, math.pi/2, 0)
    arc(x1+radius-turn, bottom+turn, turn, 0, -math.pi/2)
    arc(x0-radius+turn, bottom+turn, turn, -math.pi/2, -math.pi)
    return points


def tie_witnesses():
    """Nominal bands and small west-side heads for the arrangement display."""
    import cadquery as cq
    from shapely.geometry import Polygon
    spec = specification()
    result = {}
    for name, row in datums().items():
        line = Polygon(tie_profile(row))
        outer = line.buffer(spec["tie_witness_thickness_mm"]/2, join_style=2)
        inner = line.buffer(-spec["tie_witness_thickness_mm"]/2, join_style=2)
        x, y, z = row["tube_centers_world_mm"][0]
        width = spec["tie_witness_width_mm"]

        def wire(points):
            return cq.Wire.makePolygon(
                [cq.Vector(a, y+width/2, b) for a, b in list(points)[:-1]], close=True)

        strip = cq.Solid.extrudeLinear(wire(outer.exterior.coords),
                                      [wire(inner.exterior.coords)], cq.Vector(0, -width, 0))
        head = _box([[x-7.25, y-1.9, z-.5], [x-3.55, y+1.9, z+2.9]])
        result[name+"-tie"] = strip.fuse(head).clean()
    return result


def main():
    import numpy as np
    spec = specification()
    bodies = {**supports(), **tie_witnesses()}
    output = HERE / "parts"
    report = {"assembly_owner": spec["assembly_owner"], "parts": {}}
    for name, shape in bodies.items():
        vertices, faces = shape.tessellate(.025, .12)
        np.savez_compressed(output/(name+".npz"),
                            vertices=np.array([v.toTuple() for v in vertices]),
                            faces=np.array(faces))
        bb = shape.BoundingBox()
        report["parts"][name] = {
            "valid": shape.isValid(), "solid_count": len(shape.Solids()),
            "bounds_mm": [[bb.xmin, bb.ymin, bb.zmin], [bb.xmax, bb.ymax, bb.zmax]],
        }
    core = _box([[-90.5, 182.3, 244.4], [90.5, 460.3, 253.4]])
    for shape in supports().values():
        core = core.fuse(shape)
    for cut in cuts().values():
        core = core.cut(cut)
    core = core.clean()
    report["nominal_lid_union"] = {"valid": core.isValid(), "solid_count": len(core.Solids())}
    report["tie_to_lid_and_seat_overlap_mm3"] = {
        name: core.intersect(tie).Volume() for name, tie in tie_witnesses().items()}
    report["seat_floor_above_tie_slot_mm"] = (
        spec["stations"][0]["tube_centers_world_mm"][0][2]
        -spec["seat_radius_mm"]-spec["tie_slot_top_z_mm"])
    report["slot_leaves_nominal_9mm_lid_floor_mm"] = spec["tie_slot_bottom_z_mm"]-244.4
    report["scope"] = "Native seats, tie cuts and nominal flat lid union; production lid features are separate."
    (HERE/"reservoir-a-anchor-review.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
