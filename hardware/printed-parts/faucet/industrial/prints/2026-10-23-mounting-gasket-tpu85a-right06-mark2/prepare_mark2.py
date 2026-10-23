"""Prepare one current Industrial mounting gasket; manual, without sending."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
SOURCE = ROOT / "hardware/printed-parts/gaskets.3mf"
MESH = HERE.parents[1] / "industrial-above-counter-gasket.stl"
STEM = "2026-10-23-industrial-mounting-gasket-tpu85a-right06-z000-mark2"
PROJECT = HERE / (STEM + ".3mf")
CACHE = ROOT / ".cache/printer-control/industrial-gasket-mark2-20261023"
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SOURCE) as z:
        members = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    original = dict(settings)
    settings.update(
        curr_bed_type="Engineering Plate",
        printer_settings_id="Bambu Lab H2C 0.6 Standard zero user Z trim",
        print_settings_id="Industrial solid mounting gasket Bambu85A Mark2",
        filament_map=["2"] * len(settings["filament_map"]),
        filament_nozzle_map=["1"] * len(settings["filament_nozzle_map"]),
        filament_colour=["#161616"] * len(settings["filament_colour"]),
        time_lapse_gcode="", seam_gap="0%", reduce_crossing_wall="1",
        enable_support="0", brim_type="no_brim", brim_width="0",
    )
    settings["print_compatible_printers"] = [settings["printer_settings_id"]]
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    seed = CACHE / "engineering-right06-seed.3mf"
    writer.archive_write(seed, members)
    report = writer.refresh(
        seed, PROJECT,
        parts=(("industrial-above-counter-gasket", MESH, 0.0),),
        offsets=((0.0, 0.0),), title="Industrial above-counter gasket - Mark2",
        plate_border=80.0,
    )
    report.update(
        settings_source=str(SOURCE.relative_to(ROOT)),
        settings_source_sha256=sha(SOURCE.read_bytes()),
        settings_changes={k: {"from": original.get(k), "to": settings[k]}
                          for k in settings if original.get(k) != settings[k]},
        printer="Mark2", material="Black Bambu TPU 85A",
        nozzle_mapping="Right fixed 0.6 mm; external spool 255",
        requested_z_trim_mm=0, mesh_sha256=sha(MESH.read_bytes()), count=1,
        preparation_script_sha256=sha(Path(__file__).read_bytes()),
    )
    PROJECT.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
               "--slice", "0", "--arrange", "0", "--orient", "0",
               "--export-3mf", STEM + ".gcode.3mf", "--outputdir", str(CACHE), str(PROJECT)]
    with (CACHE / "slice.log").open("w") as log:
        subprocess.run(command, cwd=CACHE, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((CACHE / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    target = HERE / (STEM + ".gcode.3mf")
    target.write_bytes((CACHE / target.name).read_bytes())
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:
            raise ValueError("Native archive checksum error")
        gcode = z.read("Metadata/plate_1.gcode")
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum error")
        effective = json.loads(z.read(writer.SETTINGS_MEMBER))
    path = CACHE / "plate_1.gcode"
    path.write_bytes(gcode)
    envelope = writer.object_toolpaths(path, CACHE / "review.gcode", None)
    low, high = envelope["extrusion_bounds_xy_mm"]
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0]:
        raise ValueError(f"Unexpected Mark2 trim: {trims}")
    plate, = result["sliced_plates"]
    review = dict(
        status="Native slice prepared; physical result pending",
        project_sha256=sha(PROJECT.read_bytes()), archive=target.name,
        archive_sha256=sha(target.read_bytes()), gcode_sha256=sha(gcode),
        plate_trim_commands_mm=trims, bead_envelope=envelope,
        bead_margin_mm=[low[0] - 25, low[1], 330 - high[0], 320 - high[1]],
        layers=int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
        estimated_seconds=plate["total_predication"],
        estimated_filament_g=sum(v["total_used_g"] for v in plate["filaments"]),
        slicer_warning=plate["warning_message"],
        effective_settings={k: effective[k] for k in (
            "curr_bed_type", "filament_nozzle_map", "filament_map", "filament_settings_id",
            "nozzle_diameter", "nozzle_temperature", "nozzle_temperature_initial_layer",
            "eng_plate_temp", "eng_plate_temp_initial_layer", "filament_max_volumetric_speed",
            "filament_flow_ratio", "layer_height", "initial_layer_print_height", "wall_loops",
            "wall_generator", "sparse_infill_density", "sparse_infill_pattern", "top_shell_layers",
            "bottom_shell_layers", "enable_support", "brim_type", "seam_gap", "time_lapse_gcode")},
    )
    PROJECT.with_suffix(".readiness.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps(review, indent=2))


if __name__ == "__main__":
    main()
