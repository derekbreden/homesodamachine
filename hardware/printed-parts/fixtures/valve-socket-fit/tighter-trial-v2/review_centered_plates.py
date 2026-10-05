"""Independently verify the two centered, fit-coupon-only native plates.

Reads frozen exports and the exact new native archive. No geometry, project,
printer state or previously saved review is changed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh
from shapely.geometry import LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())
RC62 = ROOT / "hardware/printed-parts/enclosure/enclosure/magnet-retention/fit-coupons"
sys.path.insert(0, str(HERE))
import review_native as dimensions

TAG = lambda name: f"{{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}}{name}"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
PLATES = {
    "Mark2": dict(rc62=[f"{a}{b}" for a in "AB" for b in range(1, 5)] + ["C0"],
                  valve=["V72", "V71", "V70"], trim=.02, colour="#161616"),
    "H2C": dict(rc62=[f"{a}{b}" for a in "CD" for b in range(1, 5)] + ["C0"],
                valve=["V70", "V69", "V68"], trim=.16, colour="#000000"),
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as data:
        for block in iter(lambda: data.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def metadata(node):
    return {item.get("key"): item.get("value") for item in node.findall("metadata")
            if item.get("key") is not None}


def native_mesh_binding(archive, preparation, samples):
    model = ET.fromstring(archive.read("3D/3dmodel.model"))
    resources = {obj.get("id"): obj for obj in model.findall(f"{TAG('resources')}/{TAG('object')}")}
    builds = {item.get("objectid"): item for item in model.findall(f"{TAG('build')}/{TAG('item')}")}
    config = ET.fromstring(archive.read("Metadata/model_settings.config"))
    objects = {obj.get("id"): obj for obj in config.findall("object")}
    assert len(resources) == len(builds) == len(objects) == 12
    assert len(config.findall("plate")) == 1
    instances = config.find("plate").findall("model_instance")
    instance_ids = {metadata(item)["object_id"]: int(metadata(item)["identify_id"]) for item in instances}
    assert len(instance_ids) == 12
    output = {}
    for part in preparation["parts"]:
        sample, folder, _ = samples[part["name"]]
        object_id, part_id = part["object_id"], part["part_id"]
        assert instance_ids[object_id] == part["identify_id"]
        values = metadata(objects[object_id])
        assert values["name"] == part["name"] and values["extruder"] == "1"
        assert values["enable_support"] == "0"
        component, = resources[object_id].findall(f"{TAG('components')}/{TAG('component')}")
        assert component.get("objectid") == part_id
        assert component.get(f"{{{PROD}}}path").lstrip("/") == part["member"]
        assert [float(v) for v in component.get("transform").split()] == [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        transform = np.array([float(v) for v in builds[object_id].get("transform").split()])
        assert np.allclose(transform[:9], np.eye(3).flatten(), atol=1e-10)
        assert np.allclose(transform, part["build_transform"], atol=1e-7)
        assert builds[object_id].get("printable") == "1"
        volume, = objects[object_id].findall("part")
        assert volume.get("id") == part_id and volume.get("subtype") == "normal_part"
        assert metadata(volume)["name"] == part["name"]
        child = ET.fromstring(archive.read(part["member"]))
        mesh_object, = child.findall(f"{TAG('resources')}/{TAG('object')}")
        assert mesh_object.get("id") == part_id
        geometry = mesh_object.find(TAG("mesh"))
        vertices = np.array([[float(v.get(a)) for a in "xyz"] for v in geometry.find(TAG("vertices"))])
        triangles = list(geometry.find(TAG("triangles")))
        assert all(t.get("paint_supports") is None for t in triangles)
        faces = np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in triangles])
        source = trimesh.load(folder / sample["stl"], force="mesh", process=True)
        assert source.is_watertight and source.is_winding_consistent and source.body_count == 1
        assert np.array_equal(faces, source.faces)
        error = float(np.max(np.abs(vertices + part["source_center_mm"] - source.vertices)))
        assert error < 1e-6
        placed = vertices + transform[9:]
        actual = np.array([placed.min(axis=0), placed.max(axis=0)])
        assert np.allclose(actual, part["plate_bounds_mm"], atol=1e-6)
        assert abs(actual[0, 2]) < 1e-6
        output[part["name"]] = dict(native_vertex_max_error_mm=error, native_triangle_count=len(faces),
            exact_source_faces_preserved=True, source_to_plate_translation_mm=(transform[9:]-part["source_center_mm"]).tolist(),
            native_bounds_mm=actual.tolist(), upright_identity_rotation=True, normal_part_only=True)
    assert set(resources) == {p["object_id"] for p in preparation["parts"]}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--printer", choices=PLATES, required=True)
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), "Use a new review filename instead of replacing a reviewed record."
    assert sha(args.archive) == args.expected_sha256
    expected = PLATES[args.printer]
    preparation = json.loads(args.preparation.read_text())
    magnet = json.loads((RC62 / "geometry.json").read_text())
    valve = json.loads((HERE / "geometry.json").read_text())
    assert magnet["print_build_axis"] == [0, 0, 1] and magnet["magnet_axis"] == [0, 1, 0]
    assert magnet["insertion_axis"] == [0, 0, -1] and magnet["roof"] is False and magnet["pause"] is False
    assert valve["insertion_axis"] == [0, -1, 0] and valve["insertion_pause"] is False
    samples = {s["name"]: (s, RC62, "rc62") for s in magnet["samples"]}
    samples.update({s["name"]: (s, HERE, "valve") for s in valve["samples"]})
    names = {name for name, (sample, _, kind) in samples.items() if sample["label"] in expected[kind]}
    assert len(preparation["parts"]) == 12 and {p["name"] for p in preparation["parts"]} == names
    assert len({p["identify_id"] for p in preparation["parts"]}) == 12
    assert preparation["pause"] is None
    assert sha(ROOT / preparation["project"]) == preparation["project_sha256"]
    for source, digest in preparation["source_sha256"].items():
        assert sha(ROOT / source) == digest, source
    bed = np.array(preparation["shared_printable_area_mm"])
    with zipfile.ZipFile(args.archive) as archive:
        assert archive.testzip() is None
        payload = archive.read("Metadata/plate_1.gcode")
        assert hashlib.md5(payload).hexdigest() == archive.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        settings = json.loads(archive.read("Metadata/project_settings.config"))
        with zipfile.ZipFile(ROOT / preparation["project"]) as project:
            prepared_settings = json.loads(project.read("Metadata/project_settings.config"))
        settings_differences = {key: dict(prepared=prepared_settings.get(key), native=settings.get(key))
            for key in set(settings) | set(prepared_settings) if settings.get(key) != prepared_settings.get(key)}
        assert settings_differences == {
            "filament_map_2": dict(prepared=None, native=["1"]),
            "filament_prime_volume": dict(prepared=["30"], native=["45"]),
        }, settings_differences
        plate, = ET.fromstring(archive.read("Metadata/slice_info.config")).findall("plate")
        values = metadata(plate)
        assert values["pause_count"] == "0" and values["support_used"] == "false" and values["outside"] == "false"
        assert {int(o.get("identify_id")): o.get("name") for o in plate.findall("object")} == {
            p["identify_id"]: p["name"] for p in preparation["parts"]}
        assert all(o.get("skipped") == "false" for o in plate.findall("object"))
        assert {n.get("id") for n in plate.findall("nozzle")} == {"0"}
        assert {n.get("extruder_id") for n in plate.findall("nozzle")} == {"1"}
        if "Metadata/layer_config_ranges.xml" in archive.namelist():
            assert not ET.fromstring(archive.read("Metadata/layer_config_ranges.xml")).findall("object/range")
        if "Metadata/custom_gcode_per_layer.xml" in archive.namelist():
            assert not ET.fromstring(archive.read("Metadata/custom_gcode_per_layer.xml")).findall(".//code")
        meshes = native_mesh_binding(archive, preparation, samples)
    for key, value in dict(initial_layer_print_height="0.2", layer_height="0.24", wall_loops="2",
            sparse_infill_density="15%", filament_map=["1"], filament_nozzle_map=["0"],
            filament_colour=[expected["colour"]],
            xy_contour_compensation="0", xy_hole_compensation="0", elefant_foot_compensation="0",
            enable_support="0", enable_arc_fitting="0", brim_type="no_brim",
            wall_sequence="inner wall/outer wall", infill_wall_overlap="15%", is_infill_first="0").items():
        assert settings[key] == value, (key, settings[key], value)
    assert settings["filament_flow_ratio"][0] == "0.9555"
    areas = [np.array([[float(v) for v in point.split("x")] for point in area.split(",")])
        for area in settings["extruder_printable_area"]]
    left_area = np.array([areas[0].min(axis=0), areas[0].max(axis=0)])
    assert np.array_equal(bed, left_area)
    text = payload.decode()
    assert not re.findall(r"^\s*(?:M400\s+U|M0(?:\s|$)|M1(?:\s|$))", text, re.M)
    assert not re.findall(r"^; FEATURE: (?:Support|Brim|Prime tower)", text, re.M)
    trims = [float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", text, re.M)]
    assert trims == [0., expected["trim"]]
    class TextSource:
        def read_text(self):
            return text
    roads = list(dimensions.segments(TextSource()))
    assert {r["object"] for r in roads} == {p["identify_id"] for p in preparation["parts"]}
    assert {r["tool"] for r in roads} == {0} and all(r["width"] > 0 for r in roads)
    results, footprints = [], {}
    for part in preparation["parts"]:
        sample, folder, kind = samples[part["name"]]
        assert sha(folder / sample["stl"]) == sample["stl_sha256"] == part["stl_sha256"]
        assert sha(folder / sample["step"]) == sample["step_sha256"]
        paths = [r for r in roads if r["object"] == part["identify_id"]]
        layers = sorted({r["layer"] for r in paths})
        assert layers[:2] == [.2, .44]
        assert all(abs(b-a-.24) < 1e-6 for a, b in zip(layers, layers[1:]))
        first = unary_union([LineString((r["a"], r["b"])).buffer(r["width"]/2) for r in paths if r["layer"] == .2])
        overlap = []
        for road in paths:
            if road["layer"] == .44:
                bead = LineString((road["a"], road["b"])).buffer(road["width"]/2)
                overlap.append((bead.intersection(first).area/bead.area, road["feature"]))
        minimum = min(v for v, _ in overlap)
        outer = min(v for v, feature in overlap if feature == "Outer wall")
        assert minimum > .5 and outer > .5, (part["name"], minimum, outer)
        shift = meshes[part["name"]]["source_to_plate_translation_mm"]
        measured = (dimensions.rc62_reading(sample, paths, shift) if kind == "rc62"
                    else dimensions.valve_reading(sample, paths, shift))
        edges = np.array([point for r in paths for point in (
            (min(r["a"][0], r["b"][0])-r["width"]/2, min(r["a"][1], r["b"][1])-r["width"]/2),
            (max(r["a"][0], r["b"][0])+r["width"]/2, max(r["a"][1], r["b"][1])+r["width"]/2))])
        bounds = np.array([edges.min(axis=0), edges.max(axis=0)])
        margin = float(min(*(bounds[0]-bed[0]), *(bed[1]-bounds[1])))
        assert margin >= 60., (part["name"], margin)
        footprints[part["name"]] = bounds
        label_rear = -1.2 if kind == "rc62" else -4.
        label_paths = [r for r in paths if 1.4 < r["layer"] <= 2.12 and
            max(r["a"][1], r["b"][1])-shift[1] < label_rear-0.01]
        label_layers = sorted({r["layer"] for r in label_paths})
        assert label_layers == [1.64, 1.88, 2.12] and len(label_paths) > 25
        results.append(dict(label=sample["label"], printed_label=sample.get("printed_label", sample["label"]),
            name=part["name"], kind=kind, identify_id=part["identify_id"], stl_sha256=sample["stl_sha256"],
            step_sha256=sample["step_sha256"], native_mesh_binding=meshes[part["name"]],
            model_layer_count=len(layers), first_two_layers_z_mm=layers[:2], last_model_layer_z_mm=layers[-1],
            minimum_second_layer_bead_area_overlap_fraction=minimum,
            minimum_second_layer_outer_wall_bead_area_overlap_fraction=outer,
            full_deposited_bead_bounds_xy_mm=bounds.tolist(), minimum_bed_edge_margin_mm=margin,
            raised_label_layers_z_mm=label_layers, raised_label_road_count=len(label_paths),
            fixed_left_model_tools=[0], support_road_count=0, measured_sections=measured))
    separations = []
    for index, a in enumerate(results):
        for b in results[index+1:]:
            aa, bb = footprints[a["name"]], footprints[b["name"]]
            gap = float(np.linalg.norm(np.maximum(0, np.maximum(aa[0]-bb[1], bb[0]-aa[1]))))
            assert gap >= 5., (a["name"], b["name"], gap)
            separations.append(dict(a=a["name"], b=b["name"], minimum_box_gap_mm=gap))
    output = dict(schema_version=1, checked_utc=datetime.now(timezone.utc).isoformat(),
        status="centered_native_coupon_only_plate_pass", checks_pass=True, printer=args.printer,
        preparation=str(args.preparation.resolve().relative_to(ROOT)), preparation_sha256=sha(args.preparation),
        project=preparation["project"], project_sha256=preparation["project_sha256"],
        archive=str(args.archive.resolve().relative_to(ROOT)), archive_sha256=sha(args.archive),
        gcode_sha256=hashlib.sha256(payload).hexdigest(), checksum_verified=True,
        reviewer_source_sha256=sha(Path(__file__)), dimension_reviewer_source_sha256=sha(Path(dimensions.__file__)),
        source_geometry_sha256={str((f/"geometry.json").relative_to(ROOT)): sha(f/"geometry.json") for f in (RC62, HERE)},
        shared_printable_area_mm=bed.tolist(), fit_object_count=12, rc62_count=9, valve_count=3,
        repeated_reference_labels=["C0", "V70"], no_full_parts=True, no_supports=True, no_layer_overrides=True,
        no_pauses=True, emitted_z_trim_commands_mm=trims, filament_colour=expected["colour"],
        minimum_all_model_bead_margin_mm=min(r["minimum_bed_edge_margin_mm"] for r in results),
        minimum_object_box_gap_mm=min(r["minimum_box_gap_mm"] for r in separations), samples=results,
        object_separations=separations,
        settings={k: settings[k] for k in ("wall_loops", "sparse_infill_density", "filament_flow_ratio",
            "xy_contour_compensation", "xy_hole_compensation", "wall_sequence", "infill_wall_overlap")},
        slicer_computed_settings_differences=settings_differences,
        physical_fit_qualified=False, adhesion_visually_confirmed=False,
        scope="Frozen sample geometry, exact native identities/orientation, deposited fit dimensions and centered bead footprints. Actual cooled insertion forces, first-layer adhesion and retention remain physical observations.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({k: output[k] for k in ("checks_pass", "printer", "fit_object_count", "archive_sha256",
        "minimum_all_model_bead_margin_mm", "minimum_object_box_gap_mm")}, indent=2))


if __name__ == "__main__":
    main()
