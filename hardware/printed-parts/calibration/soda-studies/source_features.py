"""Source features for the print reference, in their manufacturing frames.

The complete Industrial cover is its relaxed printable shape. The rigid host
is a crop of the actual shared faucet tip, including its grooves and passages.
An open cover pose keeps elastic preload distinct from rigid CAD placement.

Run this file manually with HSM_NO_BUILD_LOCK=1 to capture the existing source
assets and write a dimension/mesh proof beneath .cache. No production geometry,
reference assembly, print project, viewer payload or printer is changed here.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
PRINTED = ROOT / "hardware/printed-parts"
FAUCET = PRINTED / "faucet"
INPUTS = HERE / "inputs/source-features"
PROOF = ROOT / ".cache/prints/soda-studies/source-features"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def bounds(shape: cq.Shape) -> list[list[float]]:
    b = shape.BoundingBox()
    return [[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]]


def transform_shape(shape: cq.Shape, matrix) -> cq.Shape:
    """Rigid transforms retain the source's analytic faces."""
    from OCP.gp import gp_Trsf
    values = np.asarray(matrix, dtype=float)
    rigid = gp_Trsf()
    rigid.SetValues(*(float(values[i, j]) for i in range(3) for j in range(4)))
    return shape.moved(cq.Location(rigid))


def rotation_x(degrees: float) -> np.ndarray:
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1., 0., 0., 0.], [0., c, -s, 0.],
                     [0., s, c, 0.], [0., 0., 0., 1.]])


def translation(x=0., y=0., z=0.) -> np.ndarray:
    matrix = np.eye(4)
    matrix[:3, 3] = (x, y, z)
    return matrix


def source_anchor(path: Path, anchors: list[str]) -> dict:
    return {"path": relative(path), "sha256": digest(path.read_bytes()),
            "anchors": anchors}


def tee_print_provenance() -> dict:
    acceptance_path = PRINTED / "enclosure/tee-carrier/physical-acceptance.json"
    accepted = json.loads(acceptance_path.read_text())
    settings_path = ROOT / accepted["print_record"]
    settings_path = settings_path.with_name("effective-settings.json")
    settings = json.loads(settings_path.read_text())
    return {"native_archive_sha256": accepted["native_archive_sha256"],
            "source_stl_sha256": accepted["source_stl_sha256"],
            "effective_settings": source_anchor(settings_path,
                ["wall_generator", "wall_sequence", "infill_wall_overlap"]),
            "physical_record": source_anchor(acceptance_path,
                ["native_archive_sha256", "wall_loops", "scope"]),
            "wall_generator": settings["wall_generator"],
            "scope": accepted["scope"],
            "reference_scope": "The source tee surface recipe uses Classic. This cropped surface study uses the saved Mark2 profile and is unprinted."}


def capture_sources(folder: Path = INPUTS) -> dict:
    """Capture once; later calls consume only the frozen assets and dimensions."""
    folder = Path(folder)
    manifest = folder / "sources.json"
    if manifest.exists():
        return load_sources(folder)
    if os.environ.get("HSM_NO_BUILD_LOCK") != "1":
        raise RuntimeError("Capture these source assets with HSM_NO_BUILD_LOCK=1")
    sys.path[:0] = [str(ROOT / "hardware/scripts"), str(FAUCET),
                    str(FAUCET / "faucet-shell"), str(FAUCET / "industrial")]
    import industrial_display_cover as cover
    import faucet_shell as shell
    import _display_snap as snap

    assets = {
        "cover_step": FAUCET / "industrial/industrial-display-cover.step",
        "cover_stl": FAUCET / "industrial/industrial-display-cover.stl",
        "tip_step": FAUCET / "faucet-shell/faucet-shell-tip.step",
    }
    missing = [relative(path) for path in assets.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Existing production outputs are required: " + ", ".join(missing))
    folder.mkdir(parents=True, exist_ok=True)
    source_rows = {}
    for key, path in assets.items():
        data = path.read_bytes()
        target = folder / (path.name + ".gz")
        compressed = gzip.compress(data, mtime=0)
        target.write_bytes(compressed)
        source_rows[key] = dict(source=relative(path), source_sha256=digest(data),
                                snapshot=target.name, snapshot_sha256=digest(compressed))

    origin, along, normal = shell._tip_frame()
    native_to_source = np.eye(4)
    native_to_source[:3, 0] = (1., 0., 0.)
    native_to_source[:3, 1] = along.toTuple()
    native_to_source[:3, 2] = normal.toTuple()
    native_to_source[:3, 3] = origin.toTuple()
    tee_report_path = PRINTED / "enclosure/tee-carrier/low-force-trial/geometry-check.json"
    tee_report = json.loads(tee_report_path.read_text())
    tee_dimensions = tee_report["preserved_dimensions"]
    floor = tee_dimensions["floor_z"] + tee_report["floor_clearance_mm"]
    roof = tee_dimensions["roof_z"] - tee_report["roof_clearance_mm"]
    acceptance_path = FAUCET / "industrial/physical-acceptance.json"
    accepted = json.loads(acceptance_path.read_text())
    accepted_cover = next(row for row in accepted["parts"]
                          if row["name"] == "industrial-display-cover")
    record = {
        "schema": 1,
        "assets": source_rows,
        "native_frame": {"axes": ["X lateral", "S up the gooseneck", "N through the bezel"],
                         "origin_source_mm": origin.toTuple(),
                         "native_to_source_matrix": native_to_source.tolist()},
        "cover": {"width_mm": cover.DIMENSIONS.width, "length_mm": cover.DIMENSIONS.length,
                  "native_n_bounds_mm": [cover.DIMENSIONS.n_bottom, cover.DIMENSIONS.n_top],
                  "bezel_bottom_n_mm": cover.DIMENSIONS.bezel_n_bottom,
                  "bezel_thickness_mm": cover.bezel_thickness,
                  "window_width_mm": cover.window_x, "window_length_mm": cover.window_s,
                  "wing_extension_mm": cover.DIMENSIONS.wing_extension_mm,
                  "wing_preload_at_lip_top_mm": snap.X_PRELOAD,
                  "production_rotation_x_degrees": -50.,
                  "open_lift_n_mm": shell.display_cartridge_lift_n},
        "snap": {"neck_outer_radius_mm": shell.display_neck_outer_r,
                 "lip_radius_mm": shell.display_clip_lip_radius,
                 "groove_root_radius_mm": shell.display_clip_groove_radius,
                 "lip_s_span_mm": [shell.display_clip_s_bottom, shell.display_clip_s_top],
                 "groove_s_span_mm": [shell.display_clip_s_bottom - snap.END_SLIP,
                                      shell.display_clip_s_top + snap.END_SLIP],
                 "lip_n_span_mm": [shell.display_clip_bottom_n, shell.display_clip_top_n],
                 "groove_n_span_mm": [shell.display_clip_bottom_n,
                                      shell.display_clip_top_n + snap.BEARING_SLIP],
                 "lip_engagement_mm": snap.ENGAGEMENT,
                 "lip_inner_edge_relief_mm": snap.LIP_INNER_EDGE_RELIEF,
                 "radial_slip_mm": snap.RADIAL_SLIP,
                 "bearing_slip_mm": snap.BEARING_SLIP,
                 "end_slip_mm": snap.END_SLIP,
                 "tip_production_rotation_x_degrees": -math.degrees(shell.print_tip_build_rot)},
        "expanding_r6": {"column_x_mm": tee_dimensions["column_x"],
                         "column_y_mm": tee_dimensions["column_y"],
                         "column_z_mm": [floor, roof], "radius_mm": 6.,
                         "outward_per_build_height": .5,
                         "source_bed_face": "+Y aft face; build direction -Y",
                         "bottom_transition": tee_report["bottom_chamfer"]},
        "r6_print_provenance": tee_print_provenance(),
        "source_anchors": [
            source_anchor(FAUCET / "industrial/industrial_display_cover.py",
                          ["CoverDimensions", "build_display_cover", "relaxed_wing_transform"]),
            source_anchor(FAUCET / "faucet-shell/faucet_shell.py",
                          ["_tip_frame", "build_shell_tip", "build_display_retention_grooves",
                           "relieve_display_lip_inner_edges", "print_tip_build_rot"]),
            source_anchor(FAUCET / "_display_snap.py", ["ENGAGEMENT", "X_PRELOAD", "BEARING_SLIP"]),
            source_anchor(FAUCET / "refresh_print_project.py", ["PARTS"]),
            source_anchor(PRINTED / "enclosure/tee-carrier/tee_carrier.py", ["_column", "_plate_body"]),
            source_anchor(PRINTED / "cadlib/overhang_round.py", ["transition", "three_side_fill"]),
            source_anchor(tee_report_path, ["preserved_dimensions", "bottom_chamfer"]),
        ],
        "physical_evidence": {
            "cover_approach": relative(FAUCET / "faucet-display-cover/physical-acceptance.json"),
            "industrial_complete_print": relative(acceptance_path),
            "industrial_accepted_cover_stl_sha256": accepted_cover["stl_sha256"],
            "current_snapshot_matches_accepted_cover_stl_bytes":
                accepted_cover["stl_sha256"] == source_rows["cover_stl"]["source_sha256"],
            "r6_surface": relative(PRINTED / "enclosure/tee-carrier/physical-acceptance.json"),
            "scope": "Source precedent and identified prior prints; this cropped host and reference assembly are unprinted."
        },
    }
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    return record


def load_sources(folder: Path = INPUTS) -> dict:
    folder = Path(folder)
    path = folder / "sources.json"
    if not path.is_file():
        raise FileNotFoundError("Capture the existing source features once with "
                                "HSM_NO_BUILD_LOCK=1 and source_features.py --proof")
    record = json.loads(path.read_text())
    for row in record["assets"].values():
        compressed = (folder / row["snapshot"]).read_bytes()
        if digest(compressed) != row["snapshot_sha256"] or digest(gzip.decompress(compressed)) != row["source_sha256"]:
            raise ValueError(f"Frozen source asset changed: {row['snapshot']}")
    return record


def asset_bytes(key: str, record: dict, folder: Path = INPUTS) -> bytes:
    return gzip.decompress((Path(folder) / record["assets"][key]["snapshot"]).read_bytes())


def step_shape(key: str, record: dict, folder: Path = INPUTS) -> cq.Shape:
    with tempfile.TemporaryDirectory(prefix="the-pour-source-") as temporary:
        path = Path(temporary) / "source.step"
        path.write_bytes(asset_bytes(key, record, folder))
        return cq.importers.importStep(str(path)).val()


@dataclass
class Feature:
    """A printable shape/mesh and exact maps back to its production coordinates."""
    name: str
    shape: cq.Shape
    mesh: trimesh.Trimesh | None
    metadata: dict

    def native_shape(self, *, lift_n_mm=0., slide_s_mm=0.) -> cq.Shape:
        matrix = translation(y=slide_s_mm, z=lift_n_mm) @ np.array(self.metadata["print_to_native_matrix"])
        return transform_shape(self.shape, matrix)

    def native_mesh(self, *, lift_n_mm=0., slide_s_mm=0.) -> trimesh.Trimesh:
        if self.mesh is None:
            sys.path.insert(0, str(PRINTED / "cadlib"))
            from print_mesh import print_mesh
            mesh = print_mesh(self.shape)
        else:
            mesh = self.mesh.copy()
        matrix = translation(y=slide_s_mm, z=lift_n_mm) @ np.array(self.metadata["print_to_native_matrix"])
        mesh.apply_transform(matrix)
        return mesh


def manufacturing_feature(name: str, source_shape: cq.Shape, angle: float,
                          native_to_source, provenance: dict,
                          source_mesh: trimesh.Trimesh | None = None) -> Feature:
    rotation = rotation_x(angle)
    turned_shape = transform_shape(source_shape, rotation)
    if source_mesh is None:
        low, high = np.array(bounds(turned_shape))
    else:
        mesh = source_mesh.copy()
        mesh.apply_transform(rotation)
        low, high = mesh.bounds
    offset = translation(-float((low[0]+high[0])/2),
                         -float((low[1]+high[1])/2), -float(low[2]))
    source_to_print = offset @ rotation
    native_to_source = np.asarray(native_to_source, dtype=float)
    metadata = {**provenance,
                "rotation_x_degrees": 0.,
                "manufacturing_pose": "Source production rotation followed by XY centering and bed normalization",
                "production_rotation_x_degrees": angle,
                "source_to_print_matrix": source_to_print.tolist(),
                "print_to_source_matrix": np.linalg.inv(source_to_print).tolist(),
                "print_to_native_matrix": (np.linalg.inv(native_to_source) @ np.linalg.inv(source_to_print)).tolist(),
                "native_to_print_matrix": (source_to_print @ native_to_source).tolist(),
                "bed_normal_source_xyz": rotation[:3, :3].T[:, 2].tolist()}
    mesh = None
    if source_mesh is not None:
        mesh = source_mesh.copy()
        mesh.apply_transform(source_to_print)
    return Feature(name, transform_shape(source_shape, source_to_print), mesh, metadata)


def industrial_cover(folder: Path = INPUTS) -> Feature:
    """The complete relaxed cover, with every current source STL facet retained."""
    record = load_sources(folder)
    shape = step_shape("cover_step", record, folder)
    mesh = trimesh.load_mesh(io.BytesIO(asset_bytes("cover_stl", record, folder)),
                             file_type="stl", process=False)
    return manufacturing_feature(
        "complete-industrial-cover", shape, record["cover"]["production_rotation_x_degrees"],
        record["native_frame"]["native_to_source_matrix"],
        {"source_assets": {key: record["assets"][key] for key in ("cover_step", "cover_stl")},
         "source_anchors": record["source_anchors"][:4],
         "dimensions": record["cover"], "snap": record["snap"],
         "geometry_scope": "Complete unmodified relaxed source cover; rigid transform only",
         "source_stl_triangles": len(mesh.faces),
         "assembly_state": "Elastic wings must spread to seat; the relaxed rigid mesh intersects the host at the seated datum",
         "print_recipe": {"initial_layer_height_mm": .20, "layer_height_mm": .24,
                          "supports": "Tree (auto), saved Default style and automatic sections",
                          "orientation": "Bezel up; lower skirt/lip lands toward bed"}}, mesh)


def rigid_groove_host(*, crop_end_s_mm=55., folder: Path = INPUTS) -> Feature:
    """Actual faucet tip cropped at one rear S plane, beyond both whole grooves."""
    record = load_sources(folder)
    last_contact = max(record["snap"]["groove_s_span_mm"][1], record["cover"]["length_mm"])
    if not math.isfinite(crop_end_s_mm) or crop_end_s_mm < last_contact:
        raise ValueError(f"The host crop must retain the complete cover footprint through S{last_contact:g} mm")
    source = step_shape("tip_step", record, folder)
    frame = np.array(record["native_frame"]["native_to_source_matrix"])
    native = transform_shape(source, np.linalg.inv(frame))
    low, high = np.array(bounds(native))
    cutter = cq.Solid.makeBox(high[0]-low[0]+2, crop_end_s_mm-low[1]+1,
                             high[2]-low[2]+2, cq.Vector(low[0]-1, low[1]-1, low[2]-1))
    crop = native.intersect(cutter)
    source_crop = transform_shape(crop, frame)
    return manufacturing_feature(
        "rigid-production-groove-host", source_crop,
        record["snap"]["tip_production_rotation_x_degrees"], frame,
        {"source_assets": {"tip_step": record["assets"]["tip_step"]},
         "source_anchors": record["source_anchors"][1:4],
         "native_crop_end_s_mm": crop_end_s_mm,
         "mounting_face": "Rear crop plane S=crop_end_s_mm; keep attachments off the source grooves and cover footprint",
         "snap": record["snap"],
         "geometry_scope": "Actual rigid tip stock, grooves and passages; one rear cut, no resized engagement geometry",
         "print_recipe": {"initial_layer_height_mm": .20, "layer_height_mm": .24,
                          "supports": "Tree (auto), saved Default style and automatic sections",
                          "orientation": "Original tip production rotation about X"}})


def cover_open_reference(*, lift_n_mm=None, slide_s_mm=0., folder: Path = INPUTS) -> cq.Shape:
    """Display the relaxed full cover at its source loading lift, in X/S/N."""
    feature = industrial_cover(folder)
    if lift_n_mm is None:
        lift_n_mm = feature.metadata["dimensions"]["open_lift_n_mm"]
    return feature.native_shape(lift_n_mm=lift_n_mm, slide_s_mm=slide_s_mm)


def expanding_r6_surface(*, length_mm=None, folder: Path = INPUTS) -> Feature:
    """Plain positive-X tee-column stock with its exact additive bottom profile.

    The source external column dimensions and open inboard edge are retained.
    A caller may shorten the straight run, which is explicitly recorded as a
    derivative. Spring bores and tee fixtures are outside this surface study.
    """
    record = load_sources(folder)
    dim = record["expanding_r6"]
    (x0, x1), (y0, y1), (z0, z1) = (dim[key] for key in ("column_x_mm", "column_y_mm", "column_z_mm"))
    original_length = z1-z0
    if length_mm is not None:
        z1 = z0 + float(length_mm)
    radius = dim["radius_mm"]
    if not math.isfinite(z1-z0) or z1-z0 <= 2*radius:
        raise ValueError("The straight R6 run must exceed its two 6 mm end radii")
    sys.path.insert(0, str(PRINTED / "cadlib"))
    import overhang_round
    if overhang_round.OUTWARD_PER_HEIGHT != dim["outward_per_build_height"]:
        raise ValueError("The shared expanding-round slope differs from this frozen source feature")
    stock = cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))
    edges = [e for e in stock.Edges()
             if not (abs(e.startPoint().x-x0) < 1e-6 and abs(e.endPoint().x-x0) < 1e-6)]
    rounded = stock.fillet(radius, edges)
    plane = cq.Plane(origin=(0, y1, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    fill = overhang_round.three_side_fill(x0, x1, z0, z1, radius, plane)
    body = rounded.fuse(fill).clean()
    height, foot = overhang_round.transition(radius)
    return manufacturing_feature(
        "expanding-r6-column-surface", body, -90., np.eye(4),
        {"source_anchors": record["source_anchors"][4:],
         "print_recipe_source": record["r6_print_provenance"],
         "dimensions": {"width_mm": x1-x0, "build_height_mm": y1-y0,
                        "straight_run_mm": z1-z0, "source_straight_run_mm": original_length,
                        "radius_mm": radius, "outward_per_build_height": dim["outward_per_build_height"],
                        "tangent_height_mm": height, "bed_inset_mm": foot},
         "shortened_straight_run": length_mm is not None and abs(float(length_mm)-original_length) > 1e-9,
         "geometry_scope": "Source column exterior and additive tangent chamfer; plain stock excludes spring/tee hardware",
         "geometry_readings": {"added_volume_mm3": body.cut(rounded).Volume(),
                               "removed_volume_mm3": rounded.cut(body).Volume(),
                               "outside_original_stock_volume_mm3": body.cut(stock).Volume()},
         "print_recipe": {"initial_layer_height_mm": .20, "bottom_and_body_layer_height_mm": .24,
                          "wall_generator": record["r6_print_provenance"]["wall_generator"],
                          "top_round_layer_height_mm": .08,
                          "top_round_print_z_mm": [y1-y0-radius, y1-y0],
                          "local_wall_loops": 6, "local_wall_print_z_mm": [0., 6.1],
                          "elsewhere_wall_loops": 2, "supports_enabled": False,
                          "wall_infill_order": "inner wall/outer wall, then infill",
                          "infill_wall_overlap": "15%", "speeds_and_acceleration": "Saved PET-GF profile",
                          "wall_probes": [
                              {"name": "expanding +X midspan land", "line_xy_mm": [[10., 0.], [3., 0.]],
                               "print_z_mm": [0., 6.1], "expected_wall_roads": 6},
                              {"name": "plain +X midspan body", "line_xy_mm": [[10., 0.], [3., 0.]],
                               "print_z_mm": [6.11, 14.9], "expected_wall_roads": 2}]}})


def write_proof(directory: Path = PROOF, *, crop_end_s_mm=55., folder: Path = INPUTS) -> dict:
    """Manual geometric proof, without claiming a slice or physical result."""
    record = capture_sources(folder)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(PRINTED / "cadlib"))
    from print_mesh import write_print_stl
    features = [industrial_cover(folder), rigid_groove_host(crop_end_s_mm=crop_end_s_mm, folder=folder),
                expanding_r6_surface(folder=folder)]
    rows = []
    for feature in features:
        step, stl = directory / f"{feature.name}.step", directory / f"{feature.name}.stl"
        if not feature.shape.isValid() or len(feature.shape.Solids()) != 1:
            raise ValueError(f"{feature.name}: expected one valid solid")
        cq.exporters.export(feature.shape, str(step))
        if feature.mesh is None:
            mesh = write_print_stl(feature.shape, stl)
        else:
            data = feature.mesh.export(file_type="stl")
            mesh = trimesh.load_mesh(io.BytesIO(data), file_type="stl", process=True)
            if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.body_count != 1:
                raise ValueError(f"{feature.name}: transformed source STL is not one closed oriented body")
            stl.write_bytes(data)
        rows.append({"name": feature.name, "step": relative(step), "stl": relative(stl),
                     "step_sha256": digest(step.read_bytes()), "stl_sha256": digest(stl.read_bytes()),
                     "valid_one_solid": True, "watertight_oriented_mesh": True,
                     "triangles": len(mesh.faces), "volume_mm3": feature.shape.Volume(),
                     "print_bounds_mm": bounds(feature.shape), "native_bounds_mm": bounds(feature.native_shape()),
                     "metadata": feature.metadata})
    cover, host = features[:2]
    native_cover, native_host = cover.native_shape(), host.native_shape()
    lift = record["cover"]["open_lift_n_mm"]
    closed_overlap = native_cover.intersect(native_host).Volume()
    open_overlap = cover.native_shape(lift_n_mm=lift).intersect(native_host).Volume()
    assembly = cq.Compound.makeCompound([native_host, cover.native_shape(lift_n_mm=lift)])
    cq.exporters.export(assembly, str(directory / "open-source-snap-reference.step"))
    proof = {"schema": 1, "helper_source": relative(Path(__file__)),
             "helper_sha256": digest(Path(__file__).read_bytes()),
             "frozen_sources": relative(Path(folder) / "sources.json"),
             "frozen_sources_sha256": digest((Path(folder) / "sources.json").read_bytes()),
             "features": rows,
             "snap_pose_reading": {"measurement": "Rigid CAD intersection volume; no elastic deformation is predicted",
                                   "relaxed_cover_at_seated_datums_overlap_mm3": closed_overlap,
                                   "open_lift_n_mm": lift, "open_reference_overlap_mm3": open_overlap,
                                   "open_reference_step": relative(directory / "open-source-snap-reference.step"),
                                   "interpretation": "The source cover has intentional preload; a rigid closed mesh is not a seated elastic state"},
             "physical_evidence": record["physical_evidence"],
             "native_slice_performed": False, "physical_print_performed": False}
    (directory / "dimension-proof.json").write_text(json.dumps(proof, indent=2) + "\n")
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", action="store_true", help="Capture existing sources and write a cache-only proof")
    parser.add_argument("--proof-output", type=Path, default=PROOF)
    parser.add_argument("--crop-end-s", type=float, default=55.)
    args = parser.parse_args()
    if args.proof:
        proof = write_proof(args.proof_output, crop_end_s_mm=args.crop_end_s)
        print(json.dumps({"proof": relative(args.proof_output / "dimension-proof.json"),
                          "features": [{k: row[k] for k in ("name", "triangles", "print_bounds_mm")}
                                       for row in proof["features"]],
                          "snap_pose_reading": proof["snap_pose_reading"]}, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
