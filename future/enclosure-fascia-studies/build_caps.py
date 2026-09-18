"""Display/chamfer appearance surfaces in the enclosure's X, Y-aft, Z-up frame."""
from pathlib import Path
import base64
import gzip
import functools
import json
import math
import struct
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "hardware/scripts"))
from flute_payload import creased

cap_bottom = 242.0
cap_back = 315.0
roof_z = 355.0
half_width = 107.5
rear_y = 467.0
plan_radius = 12.0
edge_radius = 8.0

forms = {
    "A": dict(name="Soft sweep", angle=40, front_depth=18, funnel_aft=32,
              lower_radius=24, upper_radius=30, display_flat=94),
    "B": dict(name="Low console", angle=28, front_depth=40, funnel_aft=44,
              lower_radius=30, upper_radius=44, display_flat=100),
    "C": dict(name="Upright crown", angle=62, front_depth=24, funnel_aft=26,
              lower_radius=18, upper_radius=34, display_flat=96),
}


@functools.cache
def cartridge_pull_air():
    parts = HERE.parents[1] / "hardware/printed-parts/enclosure/enclosure"
    front_top = cq.importers.importStep(str(parts / "enclosure-front-top.step")).val()
    cartridge = cq.importers.importStep(str(parts / "enclosure-pump-cartridge.step")).val()
    cuts = []
    for side in (-1, 1):
        box = (cq.Workplane("XY").box(21, 43, 40, centered=(True, False, False))
               .translate((side * 98.0, 21, cap_bottom - 1)).val())
        cuts.append(box.cut(front_top).cut(cartridge))
    return cuts


def cap_stations(spec):
    angle = math.radians(spec["angle"])
    lower_radius, upper_radius = spec["lower_radius"], spec["upper_radius"]
    lower_run = lower_radius * math.tan((math.pi / 2 - angle) / 2)
    upper_run = upper_radius * math.tan(angle / 2)
    slant = spec["display_flat"] + lower_run + upper_run
    front_y = 5.0 - spec["front_depth"]
    front_z = roof_z - slant * math.sin(angle)
    ridge_y = front_y + slant * math.cos(angle)
    lower_center = (front_y + lower_radius, front_z - lower_run)
    upper_center = (ridge_y + upper_run, roof_z - upper_radius)
    lower_start = (front_y, front_z - lower_run)
    lower_end = (front_y + lower_run * math.cos(angle), front_z + lower_run * math.sin(angle))
    upper_start = (ridge_y - upper_run * math.cos(angle), roof_z - upper_run * math.sin(angle))
    upper_end = (ridge_y + upper_run, roof_z)
    lower_mid = (lower_center[0] - lower_radius * math.cos((math.pi / 2 - angle) / 2),
                 lower_center[1] + lower_radius * math.sin((math.pi / 2 - angle) / 2))
    upper_mid = (upper_center[0] - upper_radius * math.sin(angle / 2),
                 upper_center[1] + upper_radius * math.cos(angle / 2))
    display_center = [0, lower_end[0] + spec["display_flat"] / 2 * math.cos(angle),
                      lower_end[1] + spec["display_flat"] / 2 * math.sin(angle)]
    return dict(front_y=front_y, front_z=front_z, ridge_y=ridge_y, lower_center=lower_center,
                upper_center=upper_center, lower_start=lower_start, lower_end=lower_end,
                upper_start=upper_start, upper_end=upper_end, lower_mid=lower_mid,
                upper_mid=upper_mid, display_center=display_center, edge_radius=edge_radius)


def build_cap(spec):
    stations = cap_stations(spec)
    spec.update(stations)
    front_y = stations["front_y"]
    profile = (cq.Workplane("YZ").moveTo(front_y, cap_bottom)
               .lineTo(*stations["lower_start"])
               .threePointArc(stations["lower_mid"], stations["lower_end"])
               .lineTo(*stations["upper_start"])
               .threePointArc(stations["upper_mid"], stations["upper_end"])
               .lineTo(rear_y, roof_z).lineTo(rear_y, cap_bottom)
               .lineTo(front_y, cap_bottom).wire().extrude(230, both=True))
    plan = (cq.Workplane("XY").workplane(offset=cap_bottom)
            .center(0, (front_y + rear_y) / 2).rect(half_width * 2, rear_y - front_y)
            .extrude(roof_z - cap_bottom).edges("|Z").fillet(plan_radius))
    solid = plan.intersect(profile).val()
    roof_edges = [edge for edge in solid.Edges()
                  if abs(abs(edge.Center().x) - half_width) < .001
                  and edge.BoundingBox().zmin > cap_bottom + .001
                  and edge.BoundingBox().ylen > 1]
    solid = solid.fillet(edge_radius, roof_edges)

    angle = math.radians(spec["angle"])
    normal = (0, -math.sin(angle), math.cos(angle))
    origin = tuple(spec["display_center"][i] + normal[i] for i in range(3))
    display_plane = cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal)
    display_hole = (cq.Workplane(display_plane).sketch().rect(153.5, 83)
                    .vertices().fillet(2.5).finalize().extrude(-30).val())
    funnel_hole = (cq.Workplane("XY").workplane(offset=cap_bottom - 1)
                   .center(0, 156.5 + spec["funnel_aft"]).rect(159.4, 159.4)
                   .extrude(roof_z - cap_bottom + 2).val())
    front_half = (cq.Workplane("XY").box(400, 800, 400, centered=(True, False, False))
                  .translate((0, cap_back - 800, 0)).val())
    solid = solid.cut(display_hole).cut(funnel_hole).intersect(front_half).clean()
    for air in cartridge_pull_air():
        solid = solid.cut(air).clean()
    if not solid.isValid():
        raise ValueError(f"Invalid cap: {spec['name']}")

    vertices, faces = [], []
    for face in solid.Faces():
        bound = face.BoundingBox()
        if bound.zmax < cap_bottom + .001 or bound.ymin > cap_back - .001:
            continue
        if (bound.xlen < .001 and abs(face.Center().x) < half_width - 5
                and bound.ymin >= 21 - .001 and bound.ymax <= 64 + .001
                and bound.zmin >= cap_bottom - .001 and bound.zmax <= cap_bottom + 39 + .001):
            continue
        positions, triangles = face.tessellate(.045, .12)
        start = len(vertices)
        vertices.extend(p.toTuple() for p in positions)
        faces.extend(tuple(i + start for i in tri) for tri in triangles)
    mesh = trimesh.Trimesh(vertices, faces, process=True)
    positions, normals, indices, _ = creased(mesh)
    return {"p": positions, "n": normals, "i": indices}


def separate_shared(meshes):
    triangles = {}
    for name, mesh in meshes.items():
        points = np.rint(mesh["p"].reshape(-1, 3) * 1000).astype(np.int32)
        normals = np.rint(mesh["n"].reshape(-1, 3) * 1000).astype(np.int32)
        vertices = [tuple(map(int, np.concatenate((p, n)))) for p, n in zip(points, normals)]
        triangles[name] = set()
        for face in mesh["i"].reshape(-1, 3):
            tri = tuple(vertices[i] for i in face)
            triangles[name].add(min(tri, tri[1:] + tri[:1], tri[2:] + tri[:2]))
    shared = set.intersection(*triangles.values())
    groups = {name: faces - shared for name, faces in triangles.items()}
    groups["shared"] = shared
    result = {}
    for name, faces in groups.items():
        vertex_map, positions, normals, indices = {}, [], [], []
        for tri in sorted(faces):
            for vertex in tri:
                if vertex not in vertex_map:
                    vertex_map[vertex] = len(positions)
                    positions.append(vertex[:3])
                    normals.append(vertex[3:])
                indices.append(vertex_map[vertex])
        result[name] = {"p": np.array(positions, dtype=float) / 1000,
                        "n": np.array(normals, dtype=float) / 1000,
                        "i": np.array(indices, dtype=np.int32)}
    print("shared", len(shared), "triangles", flush=True)
    return result


def main():
    meshes, readings = {}, {}
    for key, spec in forms.items():
        meshes[key] = build_cap(spec)
        readings[key] = {"cad_valid": True, "triangles": meshes[key]["i"].size // 3,
                         "roof_flat_start_y": spec["upper_end"][0],
                         "funnel_brim_front_y": 70 + spec["funnel_aft"],
                         "funnel_front_landing": 70 + spec["funnel_aft"] - spec["upper_end"][0]}
        print(key, spec["name"], readings[key], flush=True)
    meshes = separate_shared(meshes)
    blob = bytearray()
    for mesh in meshes.values():
        for field, scale in (("p", 1000), ("n", 1000), ("i", 1)):
            array = np.rint(mesh[field] * scale).astype(np.int32)
            if field == "i":
                array = np.diff(array.reshape(-1), prepend=0)
            else:
                array = np.diff(array.reshape(-1, 3), axis=0, prepend=np.zeros((1, 3), dtype=np.int32))
            array = array.astype("<i4").reshape(-1)
            mesh[field] = [len(blob), len(array)]
            blob.extend(array.tobytes())
    payload = dict(forms=forms, meshes=meshes, cap_bottom=cap_bottom, cap_back=cap_back,
                   scales=dict(p=1000, n=1000))
    header = json.dumps(payload, separators=(",", ":")).encode()
    raw = struct.pack("<I", len(header)) + header
    raw += b"\0" * (-len(raw) % 4) + blob
    encoded = base64.b64encode(gzip.compress(raw, 9)).decode()
    (HERE / "caps.b64").write_text(encoded)
    (HERE / "cap-readings.json").write_text(json.dumps(readings, indent=2) + "\n")
    print(len(encoded), "bytes", flush=True)


if __name__ == "__main__":
    main()
