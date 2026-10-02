"""Prepare and verify one accepted grip insert for H2C, without receiver coupons."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

from shapely.geometry import LineString, Point
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
GRIP = HERE.parent
sys.path[:0] = [str(GRIP), str(ROOT / "hardware/printed-parts/faucet"),
               str(GRIP.parent / "nameplate"), str(ROOT / "hardware/scripts"),
               str(ROOT / "tools")]
import grip_cover as g
import refresh_print_project as writer
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from bambu_print_archive import package


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(revision):
    stem = f"grip-cover-only-h2c-v{revision}"
    job = ROOT / ".cache/prints" / stem
    project = job / f"{stem}-input.3mf"
    if project.exists():
        raise FileExistsError("Reviewed inputs are immutable; increment revision.")
    reference = json.loads((GRIP / "print-check.json").read_text())
    acceptance = json.loads((GRIP / "physical-acceptance.json").read_text())
    accepted_archive = ROOT / reference["archive"]
    accepted_project = accepted_archive.parent.parent / "grip-cover-and-receiver-v4-input.3mf"
    source = GRIP / "grip-cover.stl"
    assert sha(accepted_project) == reference["project_sha256"]
    assert sha(accepted_archive) == reference["archive_sha256"]
    assert sha(source) == acceptance["cover_stl_sha256"]
    job.mkdir(parents=True, exist_ok=True)
    report = writer.refresh(accepted_project, project,
                            parts=(("grip-cover", source, 0.0),),
                            offsets=((0.0, 0.0),), z_trim=0.18,
                            title="Second grip insert; H2C")
    with zipfile.ZipFile(project) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    with zipfile.ZipFile(accepted_project) as archive:
        baseline = json.loads(archive.read(writer.SETTINGS_MEMBER))
    with zipfile.ZipFile(accepted_archive) as archive:
        accepted_effective = json.loads(archive.read(writer.SETTINGS_MEMBER))
    differences = [k for k in sorted(set(settings) | set(baseline))
                   if settings.get(k) != baseline.get(k)]
    assert set(differences) == {"machine_start_gcode", "printer_settings_id"}
    ranges = ET.Element("objects")
    obj = ET.SubElement(ranges, "object", id="1")
    band = ET.SubElement(obj, "range", min_z="2.64", max_z=str(g.THICK))
    ET.SubElement(band, "option", opt_key="layer_height").text = "0.08"
    members["Metadata/layer_config_ranges.xml"] = ET.tostring(
        ranges, encoding="utf-8", xml_declaration=True)
    writer.archive_write(project, members)
    report.update(project_sha256=sha(project), requested_z_trim_mm=0.18,
                  accepted_project=str(accepted_project.relative_to(ROOT)),
                  settings_differences_from_accepted_project=differences,
                  source_sha256={str(p.relative_to(ROOT)): sha(p) for p in
                                 (source, Path(__file__), accepted_project,
                                  GRIP / "physical-acceptance.json")})
    (job / "preparation.json").write_text(json.dumps(report, indent=2) + "\n")
    ready = job / "ready"
    ready.mkdir()
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
               "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(ready), "--export-3mf", f"{stem}.gcode.3mf",
               str(project)]
    (job / "slice-command.json").write_text(json.dumps(command, indent=2) + "\n")
    with (ready / "slice.log").open("w") as log:
        subprocess.run(command, cwd=ready, stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    archive = ready / f"{stem}.gcode.3mf"
    with zipfile.ZipFile(archive) as native:
        assert native.testzip() is None
        gc = native.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gc).hexdigest() == native.read(
            "Metadata/plate_1.gcode.md5").decode().strip().lower()
        effective = json.loads(native.read(writer.SETTINGS_MEMBER))
        normalized = {k: {"input": settings.get(k), "emitted": effective.get(k)}
                      for k in sorted(set(settings) | set(effective))
                      if settings.get(k) != effective.get(k)}
        # Native slicing resolves these filament fields the same way as the
        # accepted three-piece slice, including its 45 mm3 prime volume.
        assert set(normalized) <= {"filament_prime_volume", "filament_map_2"}, normalized
        assert all(effective[k] == accepted_effective[k] for k in normalized)
        (HERE / "preview.png").write_bytes(native.read("Metadata/plate_1.png"))
    path = ready / "plate_1.gcode"
    path.write_bytes(gc)
    part, = report["parts"]
    roads = list(segments(path))
    assert {r["object"] for r in roads} == {part["identify_id"]}
    assert {r["tool"] for r in roads} == {0}
    assert not re.search(rb"^; FEATURE: Support", gc, re.M)
    assert not any(r["feature"].startswith("Support") for r in roads)
    layers = wall_layers(archive, part["identify_id"])
    assert [list(row) for row in layers] == reference["cover_layers_mm"]
    first_z, second_z = sorted({r["layer"] for r in roads})[:2]
    first = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                         for r in roads if r["layer"] == first_z])
    second = [r for r in roads if r["layer"] == second_z]
    overlap = min(LineString((r["a"], r["b"])).buffer(r["width"] / 2).intersection(first).area /
                  LineString((r["a"], r["b"])).buffer(r["width"] / 2).area for r in second)
    assert overlap > 0.50
    cx, cy = part["plate_translation_mm"][:2]
    assert all(first.covers(Point(cx + sign * (g.LENGTH / 2 + g.WING_REACH / 2), cy))
               for sign in (-1, 1))
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gc, re.M)]
    assert trims == [0.0, 0.16], trims
    result = json.loads((ready / "result.json").read_text())
    assert result["return_code"] == 0
    plate, = result["sliced_plates"]
    assert len(plate["objects"]) == 1 and not plate["warning_message"]
    checks = {"status": "native_slice_reviewed", "printer": "H2C", "quantity": 1,
              "part": "grip-cover", "source_stl_sha256": sha(source),
              "source_matches_accepted_insert": True, "native_archive_valid": True,
              "settings_differences_from_accepted_project": differences,
              "native_settings_normalization": normalized,
              "model_layers_identical_to_accepted_insert": True, "layers_mm": layers,
              "support_paths": 0, "both_wings_print_on_first_layer": True,
              "minimum_second_layer_bead_area_overlap_fraction": overlap,
              "requested_z_trim_mm": 0.18, "emitted_z_trim_commands_mm": trims,
              "estimated_seconds": plate["total_predication"],
              "estimated_grams_saved_profile_density": sum(f["total_used_g"] for f in plate["filaments"]),
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
              "project": str(project.relative_to(ROOT)), "project_sha256": sha(project),
              "gcode_sha256": hashlib.sha256(gc).hexdigest(),
              "plate_bounds_mm": part["plate_bounds_mm"],
              "physical_reference": str((GRIP / "physical-acceptance.json").relative_to(ROOT))}
    (HERE / "preflight.json").write_text(json.dumps(checks, indent=2) + "\n")
    submission = ready / f"{stem}-printonly.gcode.3mf"
    packaged = package(archive, submission)
    for key in ("source_archive", "print_only_archive"):
        packaged[key] = str(Path(packaged[key]).relative_to(ROOT))
    (HERE / "print-only-package.json").write_text(json.dumps(packaged, indent=2) + "\n")
    print(json.dumps({"archive": str(submission), "estimated_seconds": checks["estimated_seconds"],
                      "layers": len(layers), "status": checks["status"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", type=int, default=1)
    raise SystemExit(main(parser.parse_args().revision))
