"""Measure the funnel's complete ramp wall and sampled surface-normal thickness.

The global minimum covers every complete inner ramp face against the filled
exterior boundary. Surface-normal readings cover an interior UV grid and eight
compass directions from the neck to the collar, independently in source geometry
and exported STEP. Additional samples measure the collar, brim and clamp land.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import cadquery as cq
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.gp import gp_Dir, gp_Lin, gp_Pnt


ROOT = Path(__file__).resolve().parents[2]
FUNNEL = ROOT / "hardware/printed-parts/zone-c/funnel"
RAY_EPS = 0.0001
DIRECTIONS = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")


def intersections(shape, point, direction, start=-200.0, end=200.0):
    reader = IntCurvesFace_ShapeIntersector()
    reader.Load(shape.wrapped, 1e-7)
    reader.Perform(gp_Lin(gp_Pnt(*point), gp_Dir(*direction)), start, end)
    return sorted(
        [(reader.WParameter(i), cq.Vector(reader.Pnt(i)),
          cq.Face(reader.Face(i))) for i in range(1, reader.NbPnt() + 1)],
        key=lambda hit: hit[0],
    )


def boundary_distance(face, point):
    vertex = cq.Vertex.makeVertex(*point.toTuple())
    return min(vertex.distance(edge) for edge in face.Edges())


def ramp_face(face, metadata):
    bounds = face.BoundingBox()
    return (
        face.geomType() != "CYLINDER"
        and bounds.zlen > 0.1
        and bounds.zmin >= metadata["neck_z"] - 0.001
        and bounds.zmax <= metadata["ramp_top_z"] + 0.001
        and face.normalAt().z < -0.2
    )


def sample_points(bore, metadata, grid, edge_margin):
    faces = [(index, face) for index, face in enumerate(bore.Faces())
             if ramp_face(face, metadata)]
    if not faces:
        raise ValueError("The inner bore has no sloping ramp faces.")
    samples = []
    coverage = {}
    for index, face in faces:
        u0, u1, v0, v1 = face._uvBounds()
        count = 0
        for row in range(grid):
            for col in range(grid):
                u = u0 + (u1 - u0) * (row + 0.5) / grid
                v = v0 + (v1 - v0) * (col + 0.5) / grid
                point = face.positionAt(u, v)
                margin = boundary_distance(face, point)
                if margin < edge_margin:
                    continue
                normal = face.normalAt(point)
                if normal.z >= -0.2:
                    continue
                samples.append((f"face-{index}-uv-{row}-{col}", index,
                                point, normal, margin))
                count += 1
        if not count:
            raise ValueError(f"Ramp face {index} has no interior grid samples.")
        coverage[str(index)] = {"surface": face.geomType(), "grid_samples": count}
    for index, direction in enumerate(DIRECTIONS):
        angle = math.radians(index * 45.0)
        dx, dy = math.cos(angle), math.sin(angle)
        mouth_hits = intersections(bore,
            (metadata['ncx'], metadata['ncy'], metadata['ramp_top_z'] + 1.0),
            (dx, dy, 0), 0.001, 300.0)
        if not mouth_hits:
            raise ValueError(f'{direction}: no mouth boundary from the offset outlet')
        reach = mouth_hits[0][0]
        radii = (metadata["spout_id"] / 2 + 0.5,
                 metadata["spout_id"] / 2 + 2.0,
                 *(reach * fraction for fraction in (0.2, 0.45, 0.7, 0.9)))
        for radius in radii:
            x = metadata["ncx"] + radius * math.cos(angle)
            y = metadata["ncy"] + radius * math.sin(angle)
            hits = intersections(bore, (x, y, 0), (0, 0, -1))
            ramps = [(point, face) for _, point, face in hits
                     if ramp_face(face, metadata)]
            if not ramps or any((point - ramps[0][0]).Length > 1e-6
                                for point, _ in ramps[1:]):
                raise ValueError(f"{direction} radius {radius}: expected one ramp hit.")
            point, face = ramps[0]
            margin = boundary_distance(face, point)
            face_index = next(i for i, f in faces if f.isSame(face))
            samples.append((f"{direction}-r{radius:g}", face_index, point,
                            face.normalAt(point), margin))
    return samples, coverage


def wall_reading(shape, point, normal):
    inside = shape.isInside(point + normal * (RAY_EPS * 2), 1e-7)
    hits = intersections(shape, point.toTuple(), normal.toTuple(), RAY_EPS, 200)
    if not inside or not hits:
        return {"thickness_mm": None, "enters_silicone": inside,
                "exit_surface": None}
    # An OFFSET surface can report a continuation beyond its trimmed face.
    # Count the boundary the ray actually crosses out of the solid, not that
    # underlying surface: the same B-rep may otherwise read differently after STEP.
    probe = RAY_EPS * 10
    for distance, exit_point, face in hits:
        before = shape.isInside(exit_point - normal * probe, 1e-7)
        after = shape.isInside(exit_point + normal * probe, 1e-7)
        if before and not after:
            return {"thickness_mm": round(distance, 6), "enters_silicone": True,
                    "exit_surface": face.geomType(),
                    "exit_mm": [round(value, 6) for value in exit_point.toTuple()]}
    return {"thickness_mm": None, "enters_silicone": True,
            "exit_surface": None}


def nominal_plug(module, metadata):
    """The plug as the generator cuts it: its outline prism less the elbow cradle's hook pockets."""
    cradle = module.elbow_cradle
    plug = cradle.plug_outline(module.plug_width / 2, 0.0, 0.0, module.plug_height).translate(
        cq.Vector(metadata["ncx"], metadata["ncy"], metadata["end_z"]))
    lift = cq.Vector(metadata["ncx"], metadata["ncy"], metadata["end_z"] - cradle.WEB)
    for pocket in cradle.pockets():
        plug = plug.cut(pocket.translate(lift))
    return plug


def region_readings(cast, exported, metadata, brim_thickness, spout_wall, tolerance, plug):
    readings = []

    def measure(label, point, normal, expected):
        source = wall_reading(cast, cq.Vector(*point), cq.Vector(*normal))
        step = wall_reading(exported, cq.Vector(*point), cq.Vector(*normal))
        values = [reading["thickness_mm"] for reading in (source, step)]
        readings.append({
            "sample": label, "point_mm": point, "normal": normal,
            "required_thickness_mm": expected, "source": source, "step": step,
            "passes": all(value is not None and abs(value - expected) <= tolerance
                          for value in values),
        })

    for axis in (0, 1):
        other = 1 - axis
        bore = (metadata["bore_w"], metadata["bore_d"])
        collar = (metadata["w"], metadata["d"])
        outside = (metadata["out_w"], metadata["out_d"])
        for side in (-1, 1):
            normal = [0, 0, 0]
            normal[axis] = side
            for station, fraction in enumerate((-0.75, 0.0, 0.75)):
                point = [0, 0, metadata["ramp_top_z"] / 2]
                point[axis] = side * bore[axis] / 2
                # Axis-aligned rays measure the straight wall, before its
                # rounded corner starts; corner rays use surface normals.
                straight_half = bore[other] / 2 - metadata["mouth_corner_r"]
                point[other] = fraction * straight_half
                measure(f"collar-{axis}-{side}-{station}", point, normal,
                        metadata["collar_wall"])
                point = [0, 0, 0]
                point[axis] = side * (outside[axis] + collar[axis]) / 4
                point[other] = fraction * collar[other] / 2
                measure(f"brim-{axis}-{side}-{station}", point, [0, 0, 1],
                        brim_thickness)
    bottom, top = metadata["end_z"], metadata["spout_land_z"]
    seal_bottom = top - metadata["sealing_land"]
    lead_top = bottom + metadata["lead_height"]
    stations = (
        ("lead", (bottom + lead_top) / 2,
         (metadata["lead_radius"] + metadata["relief_radius"]) / 2),
        ("relief", (lead_top + seal_bottom) / 2, metadata["relief_radius"]),
        ("seal", (seal_bottom + top) / 2, metadata["sealing_radius"]),
    )
    for index, direction in enumerate(DIRECTIONS):
        angle = math.radians(index * 45)
        normal = [math.cos(angle), math.sin(angle), 0]
        for station, z, radius in stations:
            point = [metadata["ncx"] + normal[0] * radius,
                     metadata["ncy"] + normal[1] * radius, z]
            # The wall reaches the plug's outline, or a hook pocket where one stands in the way.
            reach = wall_reading(plug, cq.Vector(*point), cq.Vector(*normal))["thickness_mm"]
            measure(f"plug-{direction}-{station}", point, normal, reach)
    return {"sample_count": len(readings), "readings": readings,
            "passes": all(reading["passes"] for reading in readings)}


def review(source, step, minimum=6.0, tolerance=0.01, grid=5, edge_margin=0.25):
    os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
    # The source imports its sibling generators (the elbow cradle) by name.
    sys.path.insert(0, str(Path(source).resolve().parent))
    spec = importlib.util.spec_from_file_location("funnel_wall_source", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    exterior, bore, metadata = module.build_solids()
    cast = module.build()[0].val()
    exported = cq.importers.importStep(str(step)).val()
    ramp_faces = [face for face in bore.Faces() if ramp_face(face, metadata)]
    assert ramp_faces, "The inner bore has no sloping ramp faces."
    ramp_boundary = cq.Compound.makeCompound(ramp_faces)
    exterior_boundary = cq.Compound.makeCompound(exterior.Faces())
    global_ramp_minimum = ramp_boundary.distance(exterior_boundary)
    samples, coverage = sample_points(bore, metadata, grid, edge_margin)
    readings = []
    for label, face_index, point, normal, margin in samples:
        source_reading = wall_reading(cast, point, normal)
        step_reading = wall_reading(exported, point, normal)
        a, b = source_reading["thickness_mm"], step_reading["thickness_mm"]
        passes = (a is not None and b is not None
                  and min(a, b) >= minimum - tolerance
                  and abs(a - b) <= tolerance)
        readings.append({
            "sample": label, "bore_face": face_index,
            "point_mm": [round(value, 6) for value in point.toTuple()],
            "outward_bore_normal": [round(value, 6) for value in normal.toTuple()],
            "distance_to_face_boundary_mm": round(margin, 6),
            "height_above_neck_mm": round(point.z - metadata["neck_z"], 6),
            "source": source_reading, "step": step_reading, "passes": passes,
        })
    difference = cast.cut(exported).Volume() + exported.cut(cast).Volume()
    ranges = {}
    for label in ("source", "step"):
        values = [reading[label]["thickness_mm"] for reading in readings
                  if reading[label]["thickness_mm"] is not None]
        ranges[label] = {"minimum_mm": min(values) if values else None,
                         "maximum_mm": max(values) if values else None}
    regions = region_readings(cast, exported, metadata, module.brim_thickness,
                              module.spout_wall, tolerance, nominal_plug(module, metadata))
    return {
        "method": "Exact B-rep rays along outward inner-ramp surface normals.",
        "scope": "Interior of every sloping bore face; cylindrical outlet excluded.",
        "global_ramp_minimum_mm": global_ramp_minimum,
        "global_ramp_method": "Exact B-rep minimum distance between complete inner ramp faces and the filled exterior boundary.",
        "global_ramp_scope": "Every point of all inner ramp faces, including face boundaries and throat transitions; cylindrical outlet excluded.",
        "minimum_required_mm": minimum, "tolerance_mm": tolerance,
        "edge_margin_mm": edge_margin, "grid_per_face": [grid, grid],
        "source": str(source.resolve()), "step": str(step.resolve()),
        "sha256": {"source": hashlib.sha256(source.read_bytes()).hexdigest(),
                   "step": hashlib.sha256(step.read_bytes()).hexdigest()},
        "surface_coverage": coverage,
        "sample_count": len(readings), "thickness_range": ranges,
        "source_step_symmetric_difference_mm3": round(difference, 6),
        "failed_samples": [reading["sample"] for reading in readings
                           if not reading["passes"]],
        "collar_brim_and_plug": regions,
        "passes": global_ramp_minimum >= minimum - tolerance
                  and all(reading["passes"] for reading in readings)
                  and regions["passes"] and difference < 0.001,
        "readings": readings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=FUNNEL / "funnel.py")
    parser.add_argument("--step", type=Path, default=FUNNEL / "funnel.step")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--minimum", type=float, default=6.0)
    parser.add_argument("--tolerance", type=float, default=0.01)
    parser.add_argument("--grid", type=int, default=5)
    parser.add_argument("--edge-margin", type=float, default=0.25)
    args = parser.parse_args()
    if args.grid < 2 or args.minimum < 0 or args.tolerance < 0 or args.edge_margin < 0:
        parser.error("Use grid >= 2 and nonnegative dimensions.")
    result = review(args.source, args.step, args.minimum, args.tolerance,
                    args.grid, args.edge_margin)
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
        summary = {key: value for key, value in result.items()
                   if key not in ("readings", "collar_brim_and_plug")}
        summary["collar_brim_and_plug"] = {
            key: value for key, value in result["collar_brim_and_plug"].items()
            if key != "readings"}
        print(json.dumps(summary, indent=2), flush=True)
    else:
        print(encoded, end="", flush=True)
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
