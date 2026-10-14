"""Slice one compact elbow in Siraya Tech 85A Clear with the corrected 10 mm/s exterior; no send."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
BASE = HERE.parent / "2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1"
BASE_STEM = "2026-10-13-compact-single-elbow-tpu85a-overhang10-engineering-right06-z000-mark1"
STEM = "2026-10-14-compact-single-elbow-siraya85a-overhang10-engineering-right06-z000-mark1"
SETTINGS = "Metadata/project_settings.config"
SLICER = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = BASE / (BASE_STEM + ".3mf")
    baseline_archive = BASE / (BASE_STEM + ".gcode.3mf")
    with zipfile.ZipFile(source) as z:
        members = {n: z.read(n) for n in z.namelist()}
    recipe = json.loads(members[SETTINGS])
    material = json.loads((HERE / "material-profile.json").read_text())
    for key, value in material["selected_material_values"].items():
        count = len(recipe[key]) if isinstance(recipe.get(key), list) else 1
        recipe[key] = [value] * count
    colour = os.environ.get("ELBOW_SPOOL_COLOUR", "161616").upper()
    if not re.fullmatch(r"[0-9A-F]{6}", colour):
        raise ValueError("ELBOW_SPOOL_COLOUR must be the reported six-digit RGB value")
    recipe["filament_colour"] = ["#" + colour]
    recipe["print_settings_id"] = "One compact Siraya85A Clear elbow overhang10 Engineering Plate zero Z trim Mark1"
    members[SETTINGS] = (json.dumps(recipe, indent=2) + "\n").encode()
    project = HERE / (STEM + ".3mf")
    with zipfile.ZipFile(project, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    cache = ROOT / ".cache/pump-elbow-exploration/siraya85a"
    cache.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="native-", dir=cache))
    with (run / "slice.log").open("w") as log:
        subprocess.run([SLICER, "--slice", "0", "--arrange", "0", "--orient", "0",
                        "--export-3mf", STEM + ".gcode.3mf", "--outputdir", str(run), str(project)],
                       cwd=run, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((run / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    archive = HERE / (STEM + ".gcode.3mf")
    archive.write_bytes((run / archive.name).read_bytes())
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Native archive checksum error")
        gcode = z.read("Metadata/plate_1.gcode")
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum error")
        emitted = json.loads(z.read(SETTINGS))
        model_members = {n: z.read(n) for n in z.namelist() if n.endswith(".model")}
    with zipfile.ZipFile(baseline_archive) as z:
        baseline = json.loads(z.read(SETTINGS))
        baseline_models = {n: z.read(n) for n in z.namelist() if n.endswith(".model")}
    changes = {k: {"from": baseline.get(k), "to": emitted.get(k)}
               for k in baseline.keys() | emitted.keys() if baseline.get(k) != emitted.get(k)}
    if set(changes) - (set(material["selected_material_values"]) | {"filament_colour", "print_settings_id"}):
        raise ValueError(f"Unexpected native recipe differences: {changes}")
    if model_members != baseline_models:
        raise ValueError("Native mesh or pose differs from the baseline")
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0]:
        raise ValueError(f"Unexpected Z trim: {trims}")
    (run / "plate_1.gcode").write_bytes(gcode)
    row, = result["sliced_plates"]
    record = {"status": "Offline candidate; not submitted", "printer": "Mark1 (H2C)",
              "prepared_at": datetime.now(timezone.utc).isoformat(),
              "baseline_archive": str(baseline_archive.relative_to(ROOT)),
              "baseline_archive_sha256": sha(baseline_archive.read_bytes()),
              "project": project.name, "project_sha256": sha(project.read_bytes()),
              "archive": archive.name, "archive_sha256": sha(archive.read_bytes()),
              "gcode_sha256": sha(gcode), "native_settings_differences": changes,
              "native_mesh_and_pose_match_baseline": True, "plate_trim_commands_mm": trims,
              "cache_run": str(run.relative_to(ROOT)),
              "estimated_seconds": row["total_predication"],
              "estimated_filament_g": sum(f["total_used_g"] for f in row["filaments"]),
              "slicer_warning": row["warning_message"]}
    (HERE / "native-readback.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
