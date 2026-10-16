"""Slice the Bambu TPU pair with Normal Lift and add 0.4 mm laps; no send."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
BASE = HERE.parent / "2026-10-15-departure-lap-tpu85a-mark1"
STEM = "2026-10-16-elbow-pair-tpu85a-lap040-normal-right06-z000-mark1"
SETTINGS = "Metadata/project_settings.config"
sys.path.insert(0, str(HERE.parent.parent))
from departure_lap import insert


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = next(p for p in BASE.glob("*.3mf") if not p.name.endswith(".gcode.3mf"))
    with zipfile.ZipFile(source) as z:
        members = {n: z.read(n) for n in z.namelist()}
    recipe = json.loads(members[SETTINGS])
    recipe.update(print_settings_id="Two Bambu85A elbows 225C Normal Lift 0.4mm departure lap Mark1",
                  z_hop=["0.4"] * len(recipe["z_hop"]),
                  z_hop_types=["Normal Lift"] * len(recipe["z_hop_types"]),
                  filament_z_hop=["0.4"] * len(recipe["filament_z_hop"]),
                  filament_z_hop_types=["Normal Lift"] * len(recipe["filament_z_hop_types"]))
    members[SETTINGS] = (json.dumps(recipe, indent=2) + "\n").encode()
    project = HERE / (STEM + ".3mf")
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    cache = ROOT / ".cache/pump-elbow-exploration/departure-lap040-normal"
    cache.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="native-", dir=cache))
    native = HERE / (STEM + "-native.gcode.3mf")
    with (run / "slice.log").open("w") as log:
        subprocess.run(["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
                        "--slice", "0", "--arrange", "0", "--orient", "0",
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
    with zipfile.ZipFile(next(BASE.glob("*-native.gcode.3mf"))) as z:
        baseline = json.loads(z.read(SETTINGS))
    changes = {k: {"from": baseline.get(k), "to": emitted.get(k)}
               for k in baseline.keys() | emitted.keys() if baseline.get(k) != emitted.get(k)}
    if set(changes) != {"print_settings_id", "z_hop_types", "filament_z_hop", "filament_z_hop_types"}:
        raise ValueError(f"Unexpected recipe differences: {changes}")
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.]:
        raise ValueError(f"Unexpected local Z trim: {trims}")
    row, = result["sliced_plates"]
    record = dict(prepared_at=datetime.now(timezone.utc).isoformat(),
                  status="Offline; not submitted", printer="Mark1 (H2C)",
                  source_project=str(source.relative_to(ROOT)),
                  project=project.name, project_sha256=sha(project.read_bytes()),
                  native_archive=native.name, native_archive_sha256=sha(native.read_bytes()),
                  native_gcode_sha256=sha(gcode), native_settings_differences=changes,
                  plate_trim_commands_mm=trims,
                  native_estimated_seconds=row["total_predication"],
                  estimated_filament_g=sum(f["total_used_g"] for f in row["filaments"]),
                  slicer_warning=row["warning_message"], cache_run=str(run.relative_to(ROOT)))
    (HERE / "native-readback.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)
    insert(native, HERE / (STEM + ".gcode.3mf"), HERE / "lap-review.json", height=.4)


if __name__ == "__main__":
    main()
