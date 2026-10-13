"""Prepare one saved sealing thimble for Mark1; run manually, without sending."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
SOURCE = HERE.parents[1] / "tpu-o-ring-85A-6mm.3mf"
STEM = "2026-10-13-tpu-o-ring-85a-right06-z018-mark1"
PROJECT = HERE / (STEM + ".3mf")
NATIVE = ROOT / ".cache/printer-control/tpu-o-ring-mark1-20261013"
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    NATIVE.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SOURCE) as z:
        members = {name: z.read(name) for name in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    original = dict(settings)
    start = settings["machine_start_gcode"]
    marker = re.search(r"(?m)^;===== for Textured PEI Plate", start)
    end = start.index("\nG150.1", marker.start())
    block = ";===== plate compensation plus user-calibrated +0.18 mm Z trim =====\n" + """{if curr_bed_type=="Textured PEI Plate"}
    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}
        G29.1 Z{0.18 - 0.01}
    {else}
        G29.1 Z{0.18 - 0.02}
    {endif}
{else}
    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}
        G29.1 Z{0.18 + 0.01}
    {else}
        G29.1 Z{0.18}
    {endif}
{endif}"""
    settings["machine_start_gcode"] = start[:marker.start()] + block + start[end:]
    settings["printer_settings_id"] = "Bambu Lab H2C 0.6 Standard +0.18 Z trim"
    settings["print_compatible_printers"] = [settings["printer_settings_id"]]
    settings["filament_map"] = ["2"] * len(settings["filament_map"])
    settings["filament_nozzle_map"] = ["1"] * len(settings["filament_nozzle_map"])
    settings["filament_colour"] = ["#161616"] * len(settings["filament_colour"])
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()

    model = ET.fromstring(members["3D/3dmodel.model"])
    item, = model.findall("./" + writer.qn("build") + "/" + writer.qn("item"))
    transform = item.get("transform").split()
    transform[9:11] = ["177.5", "160"]
    item.set("transform", " ".join(transform))
    members["3D/3dmodel.model"] = writer.xml(model)
    config = ET.fromstring(members["Metadata/model_settings.config"])
    config.find("./object/metadata[@key='name']").set("value", "tpu-o-ring")
    config.find("./plate/metadata[@key='plater_name']").set("value", "TPU O-ring - Mark1")
    config.find("./plate/metadata[@key='filament_maps']").set("value", "2 2")
    members["Metadata/model_settings.config"] = writer.xml(config)
    writer.archive_write(PROJECT, members)

    changed = {k: {"from": original.get(k), "to": settings.get(k)}
               for k in settings if original.get(k) != settings.get(k)}
    changed["machine_start_gcode"] = {
        "from_sha256": sha(start.encode()),
        "to_sha256": sha(settings["machine_start_gcode"].encode()),
        "requested_z_trim_mm": 0.18,
    }
    report = {
        "source_project": str(SOURCE.relative_to(ROOT)),
        "source_project_sha256": sha(SOURCE.read_bytes()),
        "project": PROJECT.name,
        "project_sha256": sha(PROJECT.read_bytes()),
        "mesh_members_sha256": {k: sha(v) for k, v in members.items()
                                if k.startswith("3D/Objects/")},
        "mesh_unchanged": True,
        "settings_changes": changed,
        "count": 1,
        "pose": "Saved cap-down orientation; centered at X177.5 Y160",
        "printer": "Mark1 (H2C)",
        "material": "TPU 85A",
        "nozzle_mapping": "Right fixed 0.6 mm; external spool 255",
    }
    PROJECT.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
               "--slice", "0", "--arrange", "0", "--orient", "0",
               "--export-3mf", STEM + ".gcode.3mf", "--outputdir", str(NATIVE), str(PROJECT)]
    with (NATIVE / "slice.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((NATIVE / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    native = NATIVE / (STEM + ".gcode.3mf")
    with zipfile.ZipFile(native) as z:
        if z.testzip() is not None:
            raise ValueError("Native archive checksum error")
        gcode = z.read("Metadata/plate_1.gcode")
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum error")
    path = NATIVE / "plate_1.gcode"
    path.write_bytes(gcode)
    envelope = writer.object_toolpaths(path, NATIVE / "review.gcode", None)
    low, high = envelope["extrusion_bounds_xy_mm"]
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0, 0.16]:
        raise ValueError(f"Unexpected Mark1 trim: {trims}")
    features = sorted({v.decode() for v in re.findall(rb"^; FEATURE: (.+)$", gcode, re.M)})
    plate, = result["sliced_plates"]
    target = HERE / native.name
    target.write_bytes(native.read_bytes())
    review = {
        "status": "Native slice reviewed; physical result pending",
        "project_sha256": report["project_sha256"],
        "archive": target.name,
        "archive_sha256": sha(target.read_bytes()),
        "gcode_sha256": sha(gcode),
        "plate_trim_commands_mm": trims,
        "bead_envelope": envelope,
        "bead_margin_mm": [low[0] - 25, low[1], 330 - high[0], 320 - high[1]],
        "features": features,
        "layers": int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
        "estimated_seconds": plate["total_predication"],
        "estimated_filament_g": sum(v["total_used_g"] for v in plate["filaments"]),
        "slicer_warning": plate["warning_message"],
    }
    PROJECT.with_suffix(".readiness.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps(review, indent=2))


if __name__ == "__main__":
    main()
