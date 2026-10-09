"""Prepare the centered ASSE vent faucet's production plates and native records.

The source STLs must be generated and geometrically reviewed first. Bambu
Studio slices locally; this tool never connects to or starts a printer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import refresh_print_project as writer

SEALS = HERE / "asse-vent-seals"
REVIEW = HERE / "vent-print-readiness"
SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")


def relative(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(parts: tuple) -> dict:
    candidates = [Path(__file__), Path(writer.__file__)]
    dependencies = {
        "asse-vent-seals": ("vent_seals.py", "faucet_paths.py"),
        "faucet-shell": ("_faucet_interface.py", "faucet_paths.py", "_display_snap.py",
                         "vent_seals.py", "faucet-shell/faucet_shell.py"),
        "faucet-display-cover": ("_faucet_interface.py", "_display_snap.py",
                                 "faucet-display-cover/faucet_display_cover.py"),
        "above-counter-plate": ("_faucet_interface.py", "faucet_paths.py", "faucet-shell/faucet_shell.py",
                                "above-counter-plate/above_counter_plate.py"),
        "above-counter-gasket": ("_faucet_interface.py", "faucet_paths.py", "faucet-shell/faucet_shell.py",
                                 "above-counter-gasket/above_counter_gasket.py"),
        "industrial": ("_faucet_interface.py", "faucet_paths.py", "_display_snap.py", "vent_seals.py",
                       "faucet-shell/faucet_shell.py", "above-counter-plate/above_counter_plate.py",
                       "above-counter-gasket/above_counter_gasket.py", "industrial/industrial_faucet.py",
                       "industrial/industrial_display_cover.py"),
    }
    for _, path, _ in parts:
        candidates.extend(HERE / name for name in dependencies.get(path.parent.name, ()))
    candidates.extend(path for _, path, _ in parts)
    return {relative(path): sha(path) for path in candidates if path.is_file()}


def verify_sources(report: dict) -> None:
    for name, expected in report["source_sha256"].items():
        if sha(ROOT / name) != expected:
            raise ValueError(f"{name} changed after preparing this plate")


def native_validation(native: Path, project: Path, report: dict, directory: Path) -> dict:
    """Bind the exported native payload, objects, emitted process and Z trim."""
    result = json.loads((directory / "result.json").read_text())
    if result.get("return_code") != 0 or len(result.get("sliced_plates", [])) != 1:
        raise ValueError("Native slice must complete with exactly one plate")
    plate = result["sliced_plates"][0]
    if plate["warning_message"]:
        raise ValueError(f"Native slice warning: {plate['warning_message']}")
    if plate["triangle_count"] != sum(row["triangles"] for row in report["parts"]):
        raise ValueError("Native slice triangle count differs from the source meshes")
    with zipfile.ZipFile(native) as archive, zipfile.ZipFile(project) as source:
        if archive.testzip() is not None:
            raise ValueError("The native archive has a damaged member")
        gcode = archive.read("Metadata/plate_1.gcode")
        if gcode != (directory / "plate_1.gcode").read_bytes():
            raise ValueError("Audited loose G-code differs from the native archive")
        if hashlib.md5(gcode).hexdigest() != archive.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("The native archive G-code checksum does not match")
        expected = json.loads(source.read(writer.SETTINGS_MEMBER))
        effective = json.loads(archive.read(writer.SETTINGS_MEMBER))
        normalization = {key: [expected.get(key), effective.get(key)]
                         for key in set(expected) | set(effective)
                         if expected.get(key) != effective.get(key)}
        allowed = {"filament_prime_volume": [["30"], ["45"]],
                   "filament_map_2": [None, ["1"]],
                   "version": ["02.07.01.57", "02.08.02.61"],
                   "farthest_point_timelapse": [None, "0"],
                   "counterbore_hole_bridging": [None, "none"],
                   "bed_heat_soak_area": [None, []],
                   "extruder_nozzle_stats_new": [None, ["Standard#1", "Standard#1"]],
                   "default_ams_type": [None, "-1"],
                   "inherits_group": [None, ["", "", ""]]}
        for key in ("ams_filament_load_time_n3f_s", "ams_filament_unload_time_n3f_s",
                    "ams_filament_load_time_ams_lite", "ams_filament_unload_time_ams_lite",
                    "ams_filament_load_time_ams", "ams_filament_unload_time_ams"):
            allowed[key] = [None, "0"]
        if any(key not in allowed or value != allowed[key]
               for key, value in normalization.items()):
            raise ValueError(f"Unexpected native settings normalization: {normalization}")
        plates = ET.fromstring(archive.read("Metadata/slice_info.config")).findall("plate")
        if len(plates) != 1:
            raise ValueError("The native archive must contain one plate")
        metadata = {node.get("key"): node.get("value") for node in plates[0].findall("metadata")}
        objects = plates[0].findall("object")
        if metadata.get("outside") != "false" or any(row.get("skipped") != "false" for row in objects):
            raise ValueError("The native archive has outside or skipped objects")
        if {row.get("name") for row in objects} != {row["name"] for row in report["parts"]}:
            raise ValueError("The native archive does not contain the exact requested parts")
        if "Metadata/plate_1.png" in archive.namelist():
            (directory / "native-preview.png").write_bytes(archive.read("Metadata/plate_1.png"))
    config, trims, layers = {}, [], None
    inside = False
    for line in gcode.decode().splitlines():
        if line == "; CONFIG_BLOCK_START":
            inside = True
        elif line == "; CONFIG_BLOCK_END":
            inside = False
        elif inside and (match := re.match(r"; ([a-z0-9_]+) = (.*)$", line)):
            config[match.group(1)] = match.group(2)
        elif match := re.match(r"\s*G29\.1 Z([-+.\d]+)", line):
            trims.append(float(match.group(1)))
        elif match := re.match(r"; total layer number: (\d+)", line):
            layers = int(match.group(1))
    if not config or layers is None:
        raise ValueError("Native G-code lacks its emitted configuration/layer count")
    required = {"layer_height": expected["layer_height"],
                "initial_layer_print_height": expected["initial_layer_print_height"],
                "wall_loops": expected["wall_loops"],
                "sparse_infill_density": expected["sparse_infill_density"],
                "enable_support": expected["enable_support"]}
    for key, value in required.items():
        if config.get(key) != value:
            raise ValueError(f"Emitted {key} differs from the reviewed project: {config.get(key)} vs {value}")
    if report.get("requested_z_trim_mm") is not None:
        expected_trim = round(report["requested_z_trim_mm"] - .02, 6)
        if trims != [0.0, expected_trim]:
            raise ValueError(f"Emitted trim differs from the H2C textured-plate request: {trims}")
    actual_nozzle = int(config["filament_nozzle_map"])
    if actual_nozzle != report["active_nozzle"]:
        raise ValueError(f"Emitted nozzle map is {actual_nozzle}; expected {report['active_nozzle']}")
    emitted_diameters = [float(value.strip()) for value in config["nozzle_diameter"].split(",")]
    if emitted_diameters != [float(value) for value in expected["nozzle_diameter"]]:
        raise ValueError("Emitted hotend diameters differ from the prepared profile")
    return {"archive": relative(native), "archive_sha256": sha(native),
            "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
            "native_settings_normalizations": normalization,
            "emitted_process": {key: config[key] for key in required},
            "actual_z_trim_commands_mm": trims, "active_nozzle": actual_nozzle,
            "nozzle_diameter_mm": emitted_diameters[actual_nozzle],
            "layers": layers, "estimated_seconds": plate["total_predication"],
            "estimated_grams_saved_profile_density": sum(row["total_used_g"] for row in plate["filaments"]),
            "slicer_return_code": 0, "slicer_warning": "", "objects": len(objects)}


def prepare(name: str, project: Path, settings_source: Path, parts: tuple,
            offsets: tuple, title: str, *, z_trim: float | None = None,
            active_nozzle: int = 0, border: float = 20.0,
            solid_regions: tuple[dict, ...] = ()) -> dict:
    directory = REVIEW / name
    directory.mkdir(parents=True, exist_ok=True)
    native = directory / (name + ".gcode.3mf")
    report = writer.refresh(settings_source, project, parts=parts, offsets=offsets,
                            title=title, z_trim=z_trim, plate_border=border)
    if solid_regions:
        report = writer.add_local_solid_regions(project, report, solid_regions)
        if any(region["part"] == "industrial-shell-base" for region in solid_regions):
            report["insert_review_regions"] = [
                {**region, "applied_source_bounds_mm": region["source_bounds_mm"]}
                for region in insert_host_regions("industrial-shell-base")]
    report.update(source_sha256=source_hashes(parts), active_nozzle=active_nozzle,
                  requested_z_trim_mm=z_trim, printer="H2C", submitted=False)
    save(project.with_suffix(".print.json"), report)
    verify_sources(report)
    command = [str(SLICER), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(directory), "--export-3mf", native.name, str(project)]
    save(directory / "slice-command.json", {"argv": command, "printer_connection": False})
    # Old outputs cannot serve as evidence for the next run.
    for old in (directory / "result.json", directory / "plate_1.gcode", native):
        old.unlink(missing_ok=True)
    with (directory / "slice.log").open("w") as stream:
        sliced = subprocess.run(command, cwd=directory, stdout=stream, stderr=subprocess.STDOUT)
    if sliced.returncode:
        raise RuntimeError(f"Native slice failed ({sliced.returncode}): {directory / 'slice.log'}")
    verify_sources(report)
    validation = native_validation(native, project, report, directory)
    save(project.with_suffix(".native-validation.json"), validation)
    audit = writer.slice_review(project, report, directory)
    record = {"status": "native slice prepared; support cleanup review pending",
              "project": relative(project), "project_sha256": sha(project),
              "settings_sha256": report["settings_sha256"],
              "print_report_sha256": sha(project.with_suffix(".print.json")),
              "source_sha256": report["source_sha256"], "native": validation,
              "support_audit_sha256": sha(project.with_suffix(".support-audit.json")),
              "fit": audit["fit"], "support_summary": {row["piece"]: row["summary"] for row in audit["parts"]},
              "submitted": False, "physical_print_evaluated": False}
    save(project.with_suffix(".readiness.json"), record)
    print(f"Prepared {relative(project)}; native {relative(native)}", flush=True)
    return record


def insert_host_regions(part: str) -> tuple[dict, ...]:
    """Keep the three insert backing regions independent of modifier topology."""
    shell = writer.shell
    reach = shell.base_pod_radius + shell.wall_thickness_min
    return tuple({"part": part, "name": f"Solid base insert host {index}",
                  "source_bounds_mm": [[x - reach, y - reach, shell.base_pod_z_bottom - .01],
                                       [x + reach, y + reach, shell.base_pod_z_top + 2.0]]}
                 for index, (x, y) in enumerate(shell.base_pod_centers, 1))


def insert_regions(part: str) -> tuple[dict, ...]:
    if part == "industrial-shell-base":
        from industrial.industrial_faucet import foot_radius, foot_top

        reach = foot_radius + 1.0
        return ({"part": part, "name": "Solid continuous industrial foot",
                 "source_bounds_mm": [[-reach, -reach, -.01],
                                      [reach, reach, foot_top + .01]],
                 "clip_to_part_bounds": False},)
    return insert_host_regions(part)


def rigid() -> dict:
    return prepare("faucet-black-z018-h2c", HERE / "faucet-petgf.3mf",
                   ROOT / "hardware/printed-parts/petgf.3mf", writer.PARTS, writer.PART_OFFSETS,
                   "Centered ASSE vent faucet; PET-GF; H2C", z_trim=.18,
                   solid_regions=insert_regions("faucet-shell-base"))


def seal_profile() -> Path:
    source = ROOT / "hardware/printed-parts/gaskets.3mf"
    with zipfile.ZipFile(source) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(layer_height="0.24", initial_layer_print_height="0.2",
                    print_settings_id="0.24mm centered vent bungs TPU85A",
                    filament_nozzle_map=["1"], enable_support="0", brim_type="no_brim", brim_width="0")
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    seed = REVIEW / "seal-profile.3mf"
    writer.archive_write(seed, members)
    return seed


def seals(industrial: bool = False) -> dict:
    parts = tuple((name, SEALS / (name + ".stl"), 0.0)
                  for name in ("asse-vent-upstream-bung", "asse-vent-downstream-bung"))
    if industrial:
        parts += (("industrial-above-counter-gasket", HERE / "industrial/industrial-above-counter-gasket.stl", 0.0),)
    else:
        parts += (("above-counter-gasket", HERE / "above-counter-gasket/above-counter-gasket.stl", 0.0),)
    stem = "vent-bungs-industrial-tpu85a" if industrial else "vent-bungs-tpu85a"
    return prepare(stem + "-h2c", SEALS / (stem + ".3mf"), seal_profile(),
                   parts, ((-25.0, -30.0), (25.0, -30.0), (0.0, 45.0)),
                   "ASSE vent bungs and counter gasket; TPU85A; right0.6; H2C", active_nozzle=1, border=80.0)


def tool() -> dict:
    parts = (("asse-vent-perimeter-tool", SEALS / "asse-vent-perimeter-tool.stl", 0.0),)
    return prepare("vent-seal-tool-petgf-z018-h2c", SEALS / "vent-seal-tool-petgf.3mf",
                   ROOT / "hardware/printed-parts/petgf.3mf", parts, ((0.0, 0.0),),
                   "ASSE vent perimeter insertion tool; PET-GF; H2C", z_trim=.18, border=80.0)


def industrial() -> dict:
    directory = HERE / "industrial"
    rotations = {name: angle for name, _, angle in writer.PARTS}
    parts = (("industrial-shell-base", directory / "industrial-shell-base.stl", rotations["faucet-shell-base"]),
             writer.PARTS[1],
             ("industrial-display-cover", directory / "industrial-display-cover.stl", rotations["faucet-display-cover"]),
             ("industrial-above-counter-plate", directory / "industrial-above-counter-plate.stl", 0.0))
    return prepare("faucet-industrial-black-z018-h2c", directory / "faucet-industrial-petgf.3mf",
                   ROOT / "hardware/printed-parts/petgf.3mf", parts, writer.PART_OFFSETS,
                   "Centered ASSE vent Industrial faucet; PET-GF; H2C", z_trim=.18,
                   solid_regions=insert_regions("industrial-shell-base"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs", nargs="*", choices=("rigid", "seals", "tool", "industrial", "seals-industrial"))
    args = parser.parse_args()
    actions = {"rigid": rigid, "seals": seals, "tool": tool, "industrial": industrial,
               "seals-industrial": lambda: seals(industrial=True)}
    for name in args.jobs or actions:
        actions[name]()
