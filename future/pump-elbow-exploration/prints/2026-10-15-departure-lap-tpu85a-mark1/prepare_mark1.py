"""Prepare the Bambu TPU 85A pair and insert departure laps offline; no send."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
STUDY = HERE.parent.parent
PAIR = HERE.parent / "2026-10-14-compact-two-siraya85a-overhang10-engineering-z000-mark1"
MATERIAL = HERE.parent / "2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1"
STEM = "2026-10-15-elbow-pair-tpu85a-lap020-right06-z000-mark1"
SETTINGS = "Metadata/project_settings.config"
SLICER = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
sys.path.insert(0, str(STUDY))
from departure_lap import insert


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    pair = next(p for p in PAIR.glob("*.3mf") if not p.name.endswith(".gcode.3mf"))
    material = next(p for p in MATERIAL.glob("*.3mf") if not p.name.endswith(".gcode.3mf"))
    with zipfile.ZipFile(pair) as z:
        members = {n: z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(material) as z:
        recipe = json.loads(z.read(SETTINGS))
    with zipfile.ZipFile(next(MATERIAL.glob("*.gcode.3mf"))) as z:
        baseline = json.loads(z.read(SETTINGS))
    recipe.update(print_settings_id="Two Bambu85A elbows 225C overhang10 departure lap 0.2mm Mark1",
                  seam_position="nearest", reduce_crossing_wall="1",
                  filament_wipe=["0"] * len(recipe["filament_wipe"]))
    members[SETTINGS] = (json.dumps(recipe, indent=2) + "\n").encode()
    # Keep the exact pair meshes, poses, instance IDs and spacing. Label the
    # material correctly in the editable project and native object list.
    for name in ("3D/3dmodel.model", "Metadata/model_settings.config"):
        members[name] = members[name].replace(b"Siraya", b"Bambu")
    project = HERE / (STEM + ".3mf")
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    cache = ROOT / ".cache/pump-elbow-exploration/departure-lap"
    cache.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="native-", dir=cache))
    native = HERE / (STEM + "-native.gcode.3mf")
    with (run / "slice.log").open("w") as log:
        subprocess.run([SLICER, "--slice", "0", "--arrange", "0", "--orient", "0",
                        "--export-3mf", native.name, "--outputdir", str(run), str(project)],
                       cwd=run, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((run / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    native.write_bytes((run / native.name).read_bytes())
    with zipfile.ZipFile(native) as z:
        emitted = json.loads(z.read(SETTINGS))
        gcode = z.read("Metadata/plate_1.gcode")
        objects = ET.fromstring(z.read("Metadata/slice_info.config")).findall("plate/object")
    changes = {k: {"from": baseline.get(k), "to": emitted.get(k)}
               for k in baseline.keys() | emitted.keys() if baseline.get(k) != emitted.get(k)}
    if set(changes) != {"print_settings_id", "seam_position", "reduce_crossing_wall", "filament_wipe"}:
        raise ValueError(f"Unexpected recipe differences: {changes}")
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.]:
        raise ValueError(f"Unexpected local Z trim: {trims}")
    row, = result["sliced_plates"]
    native_record = dict(prepared_at=datetime.now(timezone.utc).isoformat(),
                         status="Offline; not submitted", printer="Mark1 (H2C)",
                         geometry_project=str(pair.relative_to(ROOT)),
                         material_project=str(material.relative_to(ROOT)),
                         project=project.name, project_sha256=sha(project.read_bytes()),
                         native_archive=native.name, native_archive_sha256=sha(native.read_bytes()),
                         native_gcode_sha256=sha(gcode), native_settings_differences=changes,
                         objects=[dict(o.attrib) for o in objects], plate_trim_commands_mm=trims,
                         native_estimated_seconds=row["total_predication"],
                         estimated_filament_g=sum(f["total_used_g"] for f in row["filaments"]),
                         slicer_warning=row["warning_message"], cache_run=str(run.relative_to(ROOT)))
    (HERE / "native-readback.json").write_text(json.dumps(native_record, indent=2) + "\n")
    print(json.dumps(native_record, indent=2), flush=True)
    insert(native, HERE / (STEM + ".gcode.3mf"), HERE / "lap-review.json")


if __name__ == "__main__":
    main()
