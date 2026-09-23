"""Read Industrial faucet solids against the shared hardware and moving lever."""

import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent / "tools").is_dir())
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "hardware/faucet-layout"))
import industrial_faucet as design
import faucet_assembly as faucet
from _cadq_export import import_assembly, import_step


def volume(solid):
    return sum(part.Volume() for part in solid.Solids())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def surface_reading(solid):
    readings = []
    for face in solid.Faces():
        nodes, _triangles = face.tessellate(0.005, 0.05)
        nodes = sorted(nodes, key=lambda point: point.toTuple())
        indices = {round(index * (len(nodes)-1) / 63) for index in range(64)}
        samples = [nodes[index] for index in sorted(indices)]
        key = (face.geomType(), round(face.Area(), 5),
               *(round(value, 5) for value in face.Center().toTuple()))
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
        overlap = volume(base.intersect(other))
        record(f"base-{name}-clear", overlap < 1e-5,
               overlap_mm3=overlap, clearance_mm=base.distance(other))

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
    original_faces, actual_faces = surface_reading(original_upper), surface_reading(actual_upper)
    matching_faces = [row[0] for row in original_faces] == [row[0] for row in actual_faces]
    drift = max(target[1].distance(cq.Vertex.makeVertex(*point.toTuple()))
                for old, new in zip(original_faces, actual_faces)
                for source, target in ((old, new), (new, old))
                for point in source[2]) if matching_faces else float("inf")
    volume_drift = abs(volume(original_upper) - volume(actual_upper))
    area_drift = abs(original_upper.Area() - actual_upper.Area())
    record("shared-gooseneck-surface-agreement", matching_faces and drift < 1e-5
           and volume_drift < 1e-4 and area_drift < 1e-4,
           matched_faces=len(original_faces) if matching_faces else 0,
           samples_per_face_up_to=64, directions=2, max_surface_sample_drift_mm=drift,
           volume_difference_mm3=volume_drift, area_difference_mm2=area_drift,
           lower_z_mm=design.neck_join_z + 0.5,
           method="Matching face types, areas and centroids, bidirectional surface-node distances to paired exact faces, total area and volume. Coincident whole-solid subtraction returns invalid OCCT solids and is not used as evidence.")

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
