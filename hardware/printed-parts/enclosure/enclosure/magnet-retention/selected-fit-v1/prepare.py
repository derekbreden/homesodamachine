"""Prepare fresh C3 front-top and standalone cradle timing slices; never send.

Current geometry and host audits must match the exported pieces before this
entry point runs. Each per-part revision is immutable after preparation.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
RETENTION = HERE.parent
ENC = RETENTION.parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())
HOSTS = ENC / "heat-set-review/print-regions.json"
GEOMETRY = RETENTION / "geometry-check.json"
PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
JOBS = {
    "pump-cartridge": dict(scope="mark2-v6", printer="Mark2", trim=.04,
        colour="#161616", revision=6, stem="2026-10-05-pump-cradle-c3-mark2-v6"),
    "front-top": dict(scope="h2c-v20", printer="H2C", trim=.18,
        colour="#000000", revision=20, stem="2026-10-05-enclosure-front-top-c3-v69-h2c-v20"),
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT))


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def members(path):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        return {name: archive.read(name) for name in archive.namelist()}


def write_archive(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(payload.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, data)
    temporary.replace(path)


def ready_records(part):
    audit = json.loads(GEOMETRY.read_text())
    assert audit["geometry_checks_pass"], "Current retention geometry audit must pass."
    pocket = audit["pieces"][part]
    for suffix in (".stl", ".step"):
        assert pocket["artifact_sha256"][suffix] == sha(ENC / f"enclosure-{part}{suffix}")
    assert abs(pocket["width_mm"] - 19.05) < 1e-7
    assert abs(pocket["depth_mm"] - 3.175) < 1e-7
    assert abs(pocket["roof_z_mm"] - pocket["seat_floor_z_mm"] - 19.53) < 1e-7
    hosts = json.loads(HOSTS.read_text())
    assert hosts["native_artifact_sha256"][part][".stl"] == sha(ENC / f"enclosure-{part}.stl")
    assert len(hosts["pieces"][part]) == (2 if part == "pump-cartridge" else 5)
    assert all("valve" not in r["name"].lower() for r in hosts["pieces"][part])
    selection = json.loads((RETENTION / "fit-coupons/physical-fit-selection.json").read_text())
    assert selection["magnet"]["preferred_label"] == "C3"
    assert selection["valve"]["preferred_label"] == "V69"
    constants = {}
    for statement in ast.parse((ENC / "_cartridge_retention.py").read_text()).body:
        if isinstance(statement, ast.Assign) and isinstance(statement.targets[0], ast.Name):
            try:
                constants[statement.targets[0].id] = ast.literal_eval(statement.value)
            except (ValueError, TypeError):
                pass
    assert constants["RADIAL_AIR"] == 0. and constants["AXIAL_AIR"] == 0.
    assert constants["ROOF_AIR"] == .48
    return pocket


def profile_settings(payload, job):
    settings = json.loads(payload["Metadata/project_settings.config"])
    settings.update(layer_height="0.24", initial_layer_print_height="0.2",
        support_bottom_z_distance="0.3", support_object_xy_distance="0.5",
        extruder_ams_count=["1#0|4#0", "1#0|4#0"], support_filament="1",
        support_interface_filament="1", flush_into_support="0",
        filament_colour=[job["colour"]])
    assert settings["machine_pause_gcode"].strip() == "M400 U1"
    assert settings["curr_bed_type"] == "Textured PEI Plate"
    assert settings["filament_nozzle_map"] == ["0"]
    assert settings["support_type"] == "tree(auto)"
    assert settings["wall_loops"] == "2"
    assert settings["sparse_infill_density"] == "15%"
    assert abs(float(settings["filament_flow_ratio"][0])-.9555) < 1e-9
    assert float(settings["xy_hole_compensation"]) == 0.
    assert float(settings["xy_contour_compensation"]) == 0.
    assert settings["wall_sequence"] == "inner wall/outer wall"
    assert settings["infill_wall_overlap"] == "15%"
    assert settings["is_infill_first"] == "0"
    payload["Metadata/project_settings.config"] = (json.dumps(settings, indent=2)+"\n").encode()
    return settings


def prepare_cradle(scope, pocket, job):
    # The production single-object writer already carries the cradle's support
    # lanes, fine lower rim, ordinary upper six-wall band and current hosts.
    production = load_module("selected_fit_single_cradle", RETENTION / "prepare_prints.py")
    production.PUMP_BASE = RETENTION / "v4/pump-cartridge-cap-pause.3mf"
    baseline_record = RETENTION / "v4/preparation.json"
    baseline = json.loads(baseline_record.read_text())["jobs"][0]
    assert sha(production.PUMP_BASE) == baseline["project_sha256"]
    original = inspect.getsource(production.prepare)
    expression = "destination = HERE / f'v{revision}'"
    assert original.count(expression) == 1
    adapted = original.replace(expression, "destination = DESTINATION")
    namespace = dict(production.prepare.__globals__, DESTINATION=scope)
    exec(compile(adapted, str(Path(__file__)), "exec"), namespace)
    report = namespace["prepare"]("pump-cartridge", pocket, job["revision"])
    project = ROOT / report["project"]
    payload = members(project)
    settings = profile_settings(payload, job)
    # Reword the physical instruction without changing its programmed Z.
    pauses = ET.fromstring(payload["Metadata/custom_gcode_per_layer.xml"])
    layer, = pauses.findall("plate/layer")
    layer.set("extra", "Insert one labeled attracting K&J RC62 upright in the lower cradle; fully below both rims. Keep tube passages and toolhead clear. Resume only after separate authorization.")
    payload["Metadata/custom_gcode_per_layer.xml"] = ET.tostring(pauses, encoding="utf-8", xml_declaration=True)
    write_archive(project, payload)
    config = ET.fromstring(payload["Metadata/model_settings.config"])
    owner, = config.findall("object")
    normal, = owner.findall("part[@subtype='normal_part']")
    assert normal.find("metadata[@key='name']").get("value") == "enclosure-pump-cartridge"
    instance, = config.findall("plate/model_instance")
    report.update(part="pump-cartridge", source=relative(ENC / "enclosure-pump-cartridge.stl"),
        native_object_name=owner.find("metadata[@key='name']").get("value"),
        identify_id=int(instance.find("metadata[@key='identify_id']").get("value")),
        project_sha256=sha(project), quantity=1, cap_included=False,
        settings_sha256=hashlib.sha256(payload["Metadata/project_settings.config"]).hexdigest(),
        layer_ranges_mm=[dict(object_index=1, min_z=6., max_z=18.4, layer_height=.08,
            reason="Real inward/top lower hand-pocket rim."),
            dict(object_index=1, min_z=100.3, max_z=113.2, layer_height=.24, wall_loops=6,
            reason="Additive expanding upper hand-pocket transition.")],
        writer_scope=dict(original_prepare_source_sha256=hashlib.sha256(original.encode()).hexdigest(),
            scoped_prepare_source_sha256=hashlib.sha256(adapted.encode()).hexdigest(),
            replacement="Only the fresh immutable destination is selected in-process."),
        process=dict(layer_height=.24, initial_layer_height=.2, wall_loops=2,
            sparse_infill_percent=15, support_type=settings["support_type"]),
        baseline_preparation=relative(baseline_record), baseline_preparation_sha256=sha(baseline_record),
        baseline_scope="Only frozen Mark2 process/filament settings and grip layer ranges are read. Its cap geometry is excluded.")
    return project, report


def prepare_front(scope, directory, pocket, job):
    import manifold3d as md
    import numpy as np

    sys.path[:0] = [str(ROOT / "hardware/printed-parts/faucet"), str(ENC)]
    common = load_module("selected_fit_current_front", ENC / "support-bottom-gap/prepare_prints.py")
    source = ENC / "enclosure-front-top.stl"
    expected_sha = sha(source)
    validation = None

    def exact_current_sealed_cavity(mesh, source_path):
        nonlocal validation
        assert Path(source_path) == source and sha(source) == expected_sha
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume
        components = mesh.split(only_watertight=False)
        assert len(components) == 2
        assert all(c.is_watertight and c.is_winding_consistent for c in components)
        outer, = [c for c in components if c.volume > 0]
        cavity, = [c for c in components if c.volume < 0]
        x, _z = pocket["axis_xz_mm"]
        y0, y1 = pocket["pocket_y_mm"]
        radius = pocket["pocket_radius_mm"]
        expected_bounds = np.array([[x-radius, y0, pocket["seat_floor_z_mm"]],
            [x+radius, y1, pocket["roof_z_mm"]]])
        assert np.allclose(cavity.bounds, expected_bounds, atol=1e-5, rtol=0)

        def manifold(component):
            result = md.Manifold(md.Mesh(vert_properties=np.asarray(component.vertices, dtype=np.float32),
                tri_verts=np.asarray(component.faces, dtype=np.uint32)))
            assert result.status() == md.Error.NoError
            return result

        void = cavity.copy()
        void.invert()
        outside = (manifold(void)-manifold(outer)).volume()
        assert abs(outside) < 1e-5
        entire = manifold(mesh)
        assert abs(entire.volume() - (outer.volume + cavity.volume)) < .001
        validation = dict(source_stl_sha256=expected_sha, positive_material_bodies=1,
            inward_closed_cavities=1, cavity_bounds_mm=cavity.bounds.tolist(),
            cavity_outside_material_mm3=outside, total_material_volume_mm3=mesh.volume,
            scope="This exact current source: one exterior enclosing the selected C3 void. No mesh repair or extra material body accepted.")
        return True

    original = inspect.getsource(common.writer.refresh)
    expression = "mesh.body_count != 1"
    assert original.count(expression) == 1
    adapted = original.replace(expression, "not exact_current_sealed_cavity(mesh, source_path)")
    namespace = dict(common.writer.refresh.__globals__, exact_current_sealed_cavity=exact_current_sealed_cavity)
    exec(compile(adapted, str(Path(__file__)), "exec"), namespace)
    common.writer.refresh = namespace["refresh"]
    common.JOBS["front-top"] = (job["printer"], job["trim"], source, job["stem"])
    produced_directory, original_project, report = common.prepare("front-top", .3, .5)
    assert produced_directory == directory and validation is not None
    project = scope / original_project.name
    shutil.copyfile(original_project, project)
    payload = members(project)
    settings = profile_settings(payload, job)
    write_archive(project, payload)
    item, = report["parts"]
    offset = (np.array(item["build_transform"][9:])-np.array(item["source_center_mm"])).tolist()
    report.update(part="front-top", source=item["source"], native_object_name="enclosure-front-top",
        identify_id=item["identify_id"], quantity=1, cap_included=False,
        project=relative(project), project_sha256=sha(project),
        machine_to_bed_translation_mm=offset,
        requested_pause_height_mm=report["pause"]["requested_top_z_mm"],
        pocket_roof_height_mm=report["pause"]["pocket_roof_height_mm"],
        settings_sha256=hashlib.sha256(payload["Metadata/project_settings.config"]).hexdigest(),
        sealed_cavity_validation=validation,
        writer_scope=dict(original_refresh_source_sha256=hashlib.sha256(original.encode()).hexdigest(),
            scoped_refresh_source_sha256=hashlib.sha256(adapted.encode()).hexdigest(),
            replacement="Only the exact current source's one exterior and contained C3 cavity."),
        process=dict(layer_height=.24, initial_layer_height=.2, wall_loops=2,
            sparse_infill_percent=15, support_type=settings["support_type"]))
    return project, report


def prepare(part):
    job = JOBS[part]
    scope = HERE / job["scope"]
    directory = ROOT / ".cache/prints" / job["stem"]
    assert not scope.exists() and not directory.exists(), "Use a fresh revision; preparations are immutable."
    pocket = ready_records(part)
    scope.mkdir()
    if part == "pump-cartridge":
        directory.mkdir(parents=True)
        project, report = prepare_cradle(scope, pocket, job)
    else:
        project, report = prepare_front(scope, directory, pocket, job)
    sources = [Path(__file__), RETENTION / "prepare_prints.py",
        ENC / "support-bottom-gap/prepare_prints.py", GEOMETRY, HOSTS, PROFILE,
        ENC / "enclosure.py", ENC / "_cartridge_retention.py",
        ROOT / "hardware/printed-parts/valve-seat/valve_seat.py",
        ROOT / "hardware/printed-parts/faucet/refresh_print_project.py",
        RETENTION / "fit-coupons/physical-fit-selection.json",
        ENC / f"enclosure-{part}.stl", ENC / f"enclosure-{part}.step"]
    report.setdefault("source_sha256", {}).update({relative(path): sha(path) for path in sources})
    # Retain frozen preparation inputs locally without creating public duplicate
    # meshes; current STEP/STL and their hashes remain beside the owning part.
    inputs = directory / "selected-inputs"
    inputs.mkdir()
    for index, path in enumerate(sources):
        if path.suffix in (".py", ".json"):
            shutil.copyfile(path, inputs / f"{index:02d}-{path.name}")
    report.update(schema_version=1, stem=job["stem"], revision=job["revision"],
        printer=job["printer"], requested_z_trim_mm=job["trim"],
        expected_textured_trim_mm=round(job["trim"]-.02, 6), filament_colour=job["colour"],
        support_bottom_z_distance_mm=.3, support_object_xy_distance_mm=.5,
        preferred_magnet_label="C3", preferred_valve_label="V69",
        roof_air_nominal_mm=.48, roof_air_at_maximum_od_mm=.38,
        source_stl_sha256=sha(ENC / f"enclosure-{part}.stl"),
        source_step_sha256=sha(ENC / f"enclosure-{part}.step"),
        current_pocket=pocket, geometry_exports_changed=False, submitted=False,
        launch_authorized=False, purpose="Current geometry native insertion-pause timing only.",
        physical_fit_roof_and_strength_qualified=False)
    save(scope / "preparation.json", report)
    save(directory / "preparation.json", report)
    return directory, project, report


def slice_prepared(part):
    job = JOBS[part]
    scope = HERE / job["scope"]
    directory = ROOT / ".cache/prints" / job["stem"]
    report = json.loads((scope / "preparation.json").read_text())
    project = ROOT / report["project"]
    assert sha(project) == report["project_sha256"]
    for source, digest in report["source_sha256"].items():
        assert sha(ROOT / source) == digest, source
    ready = directory / "ready"
    assert not ready.exists(), "Native outputs are immutable; use a fresh revision."
    ready.mkdir()
    archive = ready / (job["stem"] + ".gcode.3mf")
    command = [STUDIO, "--slice", "0", "--arrange", "0", "--orient", "0",
        "--outputdir", str(ready), "--export-3mf", archive.name, str(project)]
    save(directory / "slice-command.json", command)
    with (ready / "slice.log").open("w") as log:
        subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = json.loads((ready / "result.json").read_text())
    assert result["return_code"] == 0
    plate, = result["sliced_plates"]
    assert len(plate["objects"]) == 1 and not plate["warning_message"]
    with zipfile.ZipFile(archive) as source:
        assert source.testzip() is None
        digest = hashlib.sha256()
        md5 = hashlib.md5()
        with source.open("Metadata/plate_1.gcode") as data, (ready / "plate_1.gcode").open("wb") as output:
            for block in iter(lambda: data.read(1024 * 1024), b""):
                output.write(block)
                digest.update(block)
                md5.update(block)
        assert md5.hexdigest() == source.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        (scope / "preview.png").write_bytes(source.read("Metadata/plate_1.png"))
    for source, expected in report["source_sha256"].items():
        assert sha(ROOT / source) == expected, source
    assert sha(project) == report["project_sha256"]
    native = dict(status="native_slice_awaiting_timing_review", part=part,
        printer=job["printer"], quantity=1, cap_included=False,
        archive=relative(archive), archive_sha256=sha(archive), gcode_sha256=digest.hexdigest(),
        project=relative(project), project_sha256=sha(project),
        estimated_seconds=plate["total_predication"], submitted=False, launch_authorized=False)
    save(scope / "native-slice.json", native)
    save(directory / "native-slice.json", native)
    print(native["archive"], flush=True)
    return native


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=JOBS)
    parser.add_argument("--slice", action="store_true", help="Slice the immutable prepared project; no printer command.")
    parser.add_argument("--prepared", action="store_true", help="Use an existing unsliced preparation of this revision.")
    args = parser.parse_args()
    if not args.prepared:
        directory, project, report = prepare(args.part)
        print(relative(project), flush=True)
    if args.slice:
        slice_prepared(args.part)
