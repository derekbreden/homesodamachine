"""Slice and process the connected Siraya pair; no printer action."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
GEOMETRY = HERE.parent / "2026-10-16-vertical-center-web-tpu85a-mark1"
MATERIAL = HERE.parent / "2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1"
STEM = "2026-10-16-elbows-deposited-links-siraya85a-right06-z000-mark1"
SETTINGS = "Metadata/project_settings.config"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    geometry = next(p for p in GEOMETRY.glob("2026*.3mf") if not p.name.endswith(".gcode.3mf"))
    material = next(p for p in MATERIAL.glob("*.3mf") if not p.name.endswith(".gcode.3mf"))
    with zipfile.ZipFile(geometry) as z:
        members = {n: z.read(n) for n in z.namelist()}
    geometry_recipe = json.loads(members[SETTINGS])
    with zipfile.ZipFile(material) as z:
        recipe = json.loads(z.read(SETTINGS))
    recipe.update(print_settings_id="Siraya85A connected elbows deposited links Mark1",
                  seam_position="nearest", reduce_crossing_wall="1",
                  time_lapse_gcode="", brim_object_gap="0")
    for key in ("wall_loops", "sparse_infill_density", "sparse_infill_pattern",
                "retraction_minimum_travel", "filament_retraction_minimum_travel"):
        recipe[key] = geometry_recipe[key]
    members[SETTINGS] = (json.dumps(recipe, indent=2) + "\n").encode()
    project = HERE / (STEM + ".3mf")
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    cache = ROOT / ".cache/pump-elbow-exploration/deposited-links"
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
        gcode = z.read("Metadata/plate_1.gcode")
        emitted = json.loads(z.read(SETTINGS))
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("G-code checksum differs")
    row, = result["sliced_plates"]
    record = dict(prepared_at=datetime.now(timezone.utc).isoformat(),
                  geometry_source=str(geometry.relative_to(ROOT)), geometry_sha256=sha(geometry.read_bytes()),
                  material_source=str(material.relative_to(ROOT)), material_sha256=sha(material.read_bytes()),
                  project=project.name, project_sha256=sha(project.read_bytes()),
                  archive=native.name, archive_sha256=sha(native.read_bytes()),
                  gcode_sha256=sha(gcode), estimated_seconds=row["total_predication"],
                  estimated_filament_g=sum(f["total_used_g"] for f in row["filaments"]),
                  slicer_warning=row["warning_message"], cache_run=str(run.relative_to(ROOT)),
                  emitted_photo_trip_commands=gcode.count(b"M9711"),
                  settings={k:emitted[k] for k in ("filament_settings_id", "filament_colour", "filament_map",
                            "filament_nozzle_map", "nozzle_diameter", "nozzle_temperature",
                            "nozzle_temperature_initial_layer", "eng_plate_temp", "filament_flow_ratio",
                            "filament_max_volumetric_speed", "filament_retraction_length", "curr_bed_type",
                            "wall_loops", "sparse_infill_density", "brim_object_gap")})
    (HERE / "native-readback.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)
    sys.path.insert(0,str(HERE.parent.parent))
    from deposited_links import prepare
    prepare(native,HERE/(STEM+'.gcode.3mf'),HERE/'deposition-review.json')


if __name__ == "__main__":
    main()
