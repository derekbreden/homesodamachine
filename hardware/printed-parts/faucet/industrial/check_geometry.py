"""Read Industrial faucet solids against the shared hardware and moving lever."""

import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
import trimesh
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "tools").is_dir())
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "hardware/faucet-layout"))
import industrial_faucet as design
import faucet_assembly as faucet
from _cadq_export import import_assembly, import_step


def volume(solid, integration_tolerance=None):
    return sum(part.Volume(tol=integration_tolerance) for part in solid.Solids())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def surface_properties(shape, integration_tolerance):
    properties = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape.wrapped, properties, integration_tolerance)
    return properties.Mass(), cq.Vector(properties.CentreOfMass())


def surface_reading(solid, clip_z, integration_tolerance):
    readings = []
    for face in solid.Faces():
        nodes, _triangles = face.tessellate(0.005, 0.05)
        nodes = sorted(nodes, key=lambda point: point.toTuple())
        indices = {round(index * (len(nodes)-1) / 63) for index in range(64)}
        samples = [nodes[index] for index in sorted(indices)]
        area, center = surface_properties(face, integration_tolerance)
        key = (face.geomType(), round(area, 5),
               *(round(value, 5) for value in center.toTuple()))
        if (face.geomType() == "PLANE" and abs(abs(face.normalAt().z)-1.0) < 1e-10
                and abs(BRepAdaptor_Surface(face.wrapped).Plane().Location().Z()-clip_z) < 1e-10):
            # Pair the artificial clipping cap by its actual plane. Its raw
            # area and centroid have separate bounds alongside all samples.
            key = ("Z_CLIP", clip_z)
        readings.append((key, face, samples))
    return sorted(readings, key=lambda entry: entry[0])


def main():
    rows = {}

    def record(name, passed, **measurements):
        rows[name] = {"passed": bool(passed), **measurements}
        print(f"{'PASS' if passed else 'FAIL'} {name}", flush=True)

    solids = {}
    paths = [Path(__file__), HERE / "industrial_faucet.py",
             HERE / "industrial_display_cover.py",
             design.FAUCET / "faucet-shell/faucet_shell.py",
             design.FAUCET / "faucet-shell/faucet-shell-base.step",
             ROOT / "hardware/faucet-layout/faucet-assembly.step"]
    for name in ("industrial-shell-base", "industrial-display-cover",
                 "industrial-above-counter-plate", "industrial-above-counter-gasket"):
        step, stl = HERE / f"{name}.step", HERE / f"{name}.stl"
        paths.extend((step, stl))
        shape = solids[name] = import_step(step).val()
        mesh = trimesh.load_mesh(stl)
        record(f"{name}-solid", shape.isValid() and len(shape.Solids()) == 1,
               solids=len(shape.Solids()), volume_mm3=volume(shape))
        record(f"{name}-print-mesh", mesh.is_watertight and mesh.is_winding_consistent
               and len(mesh.split()) == 1,
               watertight=mesh.is_watertight, facets=len(mesh.faces),
               print_deflection_mm=design.shell.piece_mesh_tol)

    base = solids["industrial-shell-base"]
    assembly = import_assembly(ROOT / "hardware/faucet-layout/faucet-assembly.step")
    for name in ("westbrass", "soda_faucet_tube", "flavor_tube_pos_x",
                 "flavor_tube_neg_x", "display_signal_ribbon", "shell_tip"):
        other = assembly[name][0]
        common = base.intersect(other)
        if not common.isValid():
            raise RuntimeError(f"base-{name}: native common volume is invalid")
        overlap = volume(common)
        # This row requires zero interference, with no positive gap threshold.
        # The complete curved cable has expensive global spline extrema; its
        # exact common-volume reading supplies the unchanged pass criterion.
        measure_gap = name != "display_signal_ribbon"
        record(f"base-{name}-clear", overlap < 1e-5,
               overlap_mm3=overlap,
               clearance_mm=base.distance(other) if measure_gap else None,
               clearance_measured=measure_gap,
               interference_method="valid native B-rep common volume")

    lever_overlaps, lever_gaps = [], []
    for angle in range(19):
        lever = faucet.build_lever_at(angle).val()
        lever_overlaps.append(volume(base.intersect(lever)))
        lever_gaps.append(base.distance(lever))
    record("lever-full-travel", max(lever_overlaps) < 1e-5,
           angles_deg=list(range(19)), overlaps_mm3=lever_overlaps,
           clearances_mm=lever_gaps)
    point = cq.Vertex.makeVertex(-0.434, -12.227, 52.355)
    record("open-lever-front", not base.isInside(point.Center()),
           selected_point_mm=list(point.Center().toTuple()),
           clearance_mm=base.distance(point))

    source_base = import_step(design.FAUCET / "faucet-shell/faucet-shell-base.step").val()
    lever_edge_sections = []
    for x in (-6.84, 0.0, 6.84):
        for y in (-16.5, -16.0):
            probe = cq.Edge.makeLine(cq.Vector(x, y, 30.0), cq.Vector(x, y, 50.0))
            heights = {name: max(vertex.Center().z for vertex in shape.intersect(probe).Vertices())
                       for name, shape in (("sculpted", source_base), ("industrial", base))}
            lever_edge_sections.append({"x_mm": x, "y_mm": y, "upper_z_mm": heights,
                                        "material_at_z37": base.isInside(cq.Vector(x, y, 37.0))})
    record("lever-lower-edge-matches-sculpted",
           all(abs(row["upper_z_mm"]["industrial"] - row["upper_z_mm"]["sculpted"]) < 1e-5
               and row["material_at_z37"] for row in lever_edge_sections),
           sections=lever_edge_sections)

    for name in ("industrial-above-counter-plate", "industrial-above-counter-gasket"):
        overlap = volume(base.intersect(solids[name]))
        record(f"base-{name}-clear", overlap < 1e-5, overlap_mm3=overlap)
    for index in range(1, 4):
        for kind in ("base_screw", "base_insert"):
            name = f"{kind}_{index}"
            overlap = volume(base.intersect(assembly[name][0]))
            # Heat-set inserts displace the smaller pilot; the screw itself is a clearance fit.
            if kind == "base_screw":
                record(f"{name}-clear", overlap < 1e-5, overlap_mm3=overlap)

    cavities = design.lower_cavities()
    for section, radius, center, low, high in (
        ("body", design.body_radius, design.body_center_y, design.foot_top, design.body_top),
        ("neck", design.neck_radius, design.neck_center_y, design.body_top, design.neck_join_z),
    ):
        face = next(face for face in design.cylinder(radius, center, low, high).Faces()
                    if face.geomType() == "CYLINDER")
        readings = {name: face.distance(cavity.val()) for name, cavity in cavities.items()
                    if name not in ("lever", "mount-sockets", "neck")}
        record(f"{section}-cavity-wall", min(readings.values()) >= design.wall - 1e-6,
               radial_stock_mm=readings, required_mm=design.wall)

    socket_stock = design.foot_radius - max(
        (x*x+y*y)**0.5 + design.shell.base_pod_hole_dia/2.0
        for x, y in design.shell.base_pod_centers)
    record("foot-socket-outside-wall", socket_stock >= design.wall,
           stock_mm=socket_stock, required_mm=design.wall)

    upper_mask = cq.Solid.makeBox(200, 400, 400, cq.Vector(-100, -200, design.neck_join_z + 0.5))
    original_upper, actual_upper = source_base.intersect(upper_mask), base.intersect(upper_mask)
    clip_z = design.neck_join_z + 0.5
    integration_tolerance = 1e-10
    original_faces = surface_reading(original_upper, clip_z, integration_tolerance)
    actual_faces = surface_reading(actual_upper, clip_z, integration_tolerance)
    original_caps = [row[1] for row in original_faces if row[0][0] == "Z_CLIP"]
    actual_caps = [row[1] for row in actual_faces if row[0][0] == "Z_CLIP"]
    cap_count_ok = len(original_caps) == len(actual_caps) == 1
    cap_area_drift = abs(surface_properties(original_caps[0], integration_tolerance)[0]
                         - surface_properties(actual_caps[0], integration_tolerance)[0]) if cap_count_ok else float("inf")
    cap_center_drift = (surface_properties(original_caps[0], integration_tolerance)[1]
                       - surface_properties(actual_caps[0], integration_tolerance)[1]).Length if cap_count_ok else float("inf")
    matching_faces = (cap_count_ok and cap_area_drift < 1e-4 and cap_center_drift < 1e-5
                      and [row[0] for row in original_faces] == [row[0] for row in actual_faces])
    drift = max(target[1].distance(cq.Vertex.makeVertex(*point.toTuple()))
                for old, new in zip(original_faces, actual_faces)
                for source, target in ((old, new), (new, old))
                for point in source[2]) if matching_faces else float("inf")
    volume_drift = abs(volume(original_upper, integration_tolerance)
                       - volume(actual_upper, integration_tolerance))
    default_volume_drift = abs(volume(original_upper)-volume(actual_upper))
    area_drift = abs(surface_properties(original_upper, integration_tolerance)[0]
                     - surface_properties(actual_upper, integration_tolerance)[0])
    default_area_drift = abs(original_upper.Area() - actual_upper.Area())
    record("shared-gooseneck-surface-agreement", matching_faces and drift < 1e-5
           and volume_drift < 1e-4 and area_drift < 1e-4,
           matched_faces=len(original_faces) if matching_faces else 0,
           samples_per_face_up_to=64, directions=2, max_surface_sample_drift_mm=drift,
           volume_difference_mm3=volume_drift, area_difference_mm2=area_drift,
           adaptive_integration_tolerance=integration_tolerance,
           default_integration_volume_difference_mm3=default_volume_drift,
           default_integration_area_difference_mm2=default_area_drift,
           artificial_clip_caps_per_body=[len(original_caps), len(actual_caps)],
           artificial_clip_cap_area_difference_mm2=cap_area_drift,
           artificial_clip_cap_centroid_distance_mm=cap_center_drift,
           lower_z_mm=clip_z,
           method="Exact face type and five-decimal adaptive native area/centroid signatures for every production face; the unique artificial Z clip cap is identified by its native plane with bounded adaptive area and centroid differences. Every paired face receives bidirectional native surface-node distances. Total area and volume use adaptive integration under the same limits, with default-integral differences retained separately. Coincident whole-solid subtraction is not used as evidence.")

    report = {
        "style": "Industrial",
        "scope": "Saved production solids, print meshes, shared hardware, lever travel and named cylindrical wall sections. Display cover fit and assembly motion are in display-cover-check.json. Physical retention and surface finish are print readings.",
        "sources_sha256": {str(path.relative_to(ROOT)): digest(path) for path in paths},
        "passed": all(row["passed"] for row in rows.values()),
        "checks": rows,
    }
    (HERE / "geometry-check.json").write_text(json.dumps(report, indent=2) + "\n")
    if not report["passed"]:
        sys.exit("Industrial geometry has failed readings")


if __name__ == "__main__":
    main()
