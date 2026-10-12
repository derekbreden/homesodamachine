"""Prepare the compact 0.00 mm trim TPU liner retry for Mark1; no print submission."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SOURCE = HERE.parent / "2026-10-12-tpu-liners-mark1/2026-10-12-tube-insertion-liners-tpu85a-right06-z018-mark1.3mf"
STL = HERE.parents[1] / "tube-insertion-liner-print.stl"
PROJECT = HERE / "2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.3mf"
NATIVE = ROOT / ".cache/tube-insertion-tpu-mark1-close-z000-native"
sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if NATIVE.exists() and any(NATIVE.iterdir()):
        raise ValueError(f"Use an empty native output directory: {NATIVE}")
    NATIVE.mkdir(parents=True, exist_ok=True)
    reviewed = json.loads(SOURCE.with_suffix(".readiness.json").read_text())
    if sha(SOURCE) != reviewed["project_sha256"]:
        raise ValueError("The source project differs from its reviewed slice")
    if sha(STL) != reviewed["source_stls"][str(STL.relative_to(ROOT))]:
        raise ValueError("The grip-liner mesh differs from its reviewed slice")
    with zipfile.ZipFile(SOURCE) as z:
        members = {name: z.read(name) for name in z.namelist()}
    old_settings = json.loads(members[writer.SETTINGS_MEMBER])
    profile_settings = dict(old_settings)
    profile_settings["print_compatible_printers"] = ["Bambu Lab H2C 0.6 Standard +0.00 Z trim"]
    members[writer.SETTINGS_MEMBER] = (json.dumps(profile_settings, indent=2) + "\n").encode()
    profile = NATIVE / "mark1-settings.3mf"
    writer.archive_write(profile, members)
    report = writer.refresh(
        profile, PROJECT,
        parts=(("F lower TPU liner", STL, 0.0), ("F upper TPU liner", STL, 0.0)),
        offsets=((-5, 0), (5, 0)),
        title="Tube insertion grip liners — Mark1 TPU 85A compact retry",
        z_trim=0.00, plate_border=20.0,
    )
    with zipfile.ZipFile(PROJECT) as z:
        settings = json.loads(z.read(writer.SETTINGS_MEMBER))
    changed = [k for k in sorted(set(settings) | set(old_settings))
               if settings.get(k) != old_settings.get(k)]
    if set(changed) != {"machine_start_gcode", "printer_settings_id", "print_compatible_printers"}:
        raise ValueError(f"Unexpected recipe changes: {changed}")
    report.update(
        intended_printer="Mark1 (H2C)", material="Black TPU 85A",
        nozzle_mapping="Right fixed 0.6 mm; external spool 255",
        print_pose="Tube axis vertical; two preformed half-channel liners",
        changed_settings=changed,
        original_settings_source=str(SOURCE.relative_to(ROOT)),
        original_settings_source_sha256=sha(SOURCE),
    )
    PROJECT.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    archive_name = PROJECT.stem + ".gcode.3mf"
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
               "--slice", "0", "--arrange", "0", "--orient", "0",
               "--export-3mf", archive_name, "--outputdir", str(NATIVE), str(PROJECT)]
    with (NATIVE / "slice.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((NATIVE / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    sliced = NATIVE / archive_name
    with zipfile.ZipFile(sliced) as z:
        if z.testzip() is not None:
            raise ValueError("The native archive has a damaged member")
        gcode = z.read("Metadata/plate_1.gcode")
        expected = z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        if hashlib.md5(gcode).hexdigest() != expected:
            raise ValueError("The native G-code checksum differs")
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0, -0.02]:
        raise ValueError(f"Unexpected Mark1 trim commands: {trims}")
    path = NATIVE / "plate_1.gcode"
    path.write_bytes(gcode)
    envelope = writer.object_toolpaths(path, NATIVE / "review.gcode", None)
    low, high = envelope["extrusion_bounds_xy_mm"]
    usable_low, usable_high = report["shared_printable_area_mm"]
    margins = [low[0] - usable_low[0], low[1] - usable_low[1],
               usable_high[0] - high[0], usable_high[1] - high[1]]
    if min(margins) < 20:
        raise ValueError(f"Native full-bead margin is below 20 mm: {margins}")
    features = sorted({v.decode() for v in re.findall(rb"^; FEATURE: (.+)$", gcode, re.M)})
    if any("Support" in feature for feature in features):
        raise ValueError("Unexpected support on the constant upright liner profile")
    destination = HERE / archive_name
    shutil.copy2(sliced, destination)
    plate, = result["sliced_plates"]
    record = {
        "status": "Native Mark1 slice reviewed; physical print result pending",
        "project": PROJECT.name, "project_sha256": sha(PROJECT),
        "archive": destination.name, "archive_sha256": sha(destination),
        "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
        "source_project": str(SOURCE.relative_to(ROOT)),
        "source_project_sha256": sha(SOURCE),
        "source_stls": {str(STL.relative_to(ROOT)): sha(STL)},
        "printer": "Mark1 (H2C)", "requested_z_trim_mm": 0.00,
        "plate_trim_commands_mm": trims, "recipe_changes": changed,
        "nozzle_mapping": "Right fixed 0.6 mm; black TPU 85A external spool 255",
        "extruder_offset": settings.get("extruder_offset"),
        "features": features, "support_generated": False,
        "bead_envelope": envelope, "bead_margin_mm": margins,
        "model_edge_gap_mm": 2.0, "object_center_spacing_mm": 10.0,
        "object_centres_xy_mm": [[172.5, 160.0], [182.5, 160.0]],
        "layers": int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
        "estimated_seconds": plate["total_predication"],
        "estimated_filament_g": sum(v["total_used_g"] for v in plate["filaments"]),
        "slicer_warning": plate["warning_message"],
    }
    PROJECT.with_suffix(".readiness.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
