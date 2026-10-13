"""Prepare Derek's one-time base-only seam evaluation, without sending."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").is_file())
INDUSTRIAL = HERE.parents[1]
SOURCE = INDUSTRIAL / "seam-placement/rear-center-v1/2026-10-13-industrial-faucet-rear-seam-petgf-left04-z004-mark2.3mf"
STEM = "2026-10-13-industrial-base-rear-seam-petgf-left04-z004-mark2"
PROJECT = HERE / (STEM + ".3mf")
NATIVE = ROOT / ".cache/printer-control/faucet-rear-seam-base-only-20261013"
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(INDUSTRIAL.parent))
import refresh_print_project as writer


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_report = json.loads(SOURCE.with_suffix(".print.json").read_text())
    part = next(p for p in source_report["parts"] if p["name"] == "industrial-shell-base")
    with zipfile.ZipFile(SOURCE) as z:
        members = {name: z.read(name) for name in z.namelist()}
    model = ET.fromstring(members["3D/3dmodel.model"])
    resources = model.find(writer.qn("resources"))
    for obj in list(resources):
        if obj.get("id") != part["object_id"]:
            resources.remove(obj)
    build = model.find(writer.qn("build"))
    for item in list(build):
        if item.get("objectid") != part["object_id"]:
            build.remove(item)
    item, = list(build)
    transform = item.get("transform").split()
    # Center the sole base on the left nozzle's usable 325 mm bed width.
    dx = 80.0
    transform[9] = f"{float(transform[9]) + dx:.9f}"
    item.set("transform", " ".join(transform))
    title = model.find(f"{writer.qn('metadata')}[@name='Title']")
    title.text = "Industrial faucet base - one-time rear seam evaluation"
    keep = {c.get("{" + writer.PROD + "}path").lstrip("/")
            for c in resources.findall(f"{writer.qn('object')}/{writer.qn('components')}/{writer.qn('component')}")}
    members["3D/3dmodel.model"] = writer.xml(model)
    for name in list(members):
        if name.startswith("3D/Objects/") and name not in keep:
            del members[name]
    rels = ET.fromstring(members["3D/_rels/3dmodel.model.rels"])
    for relation in list(rels):
        if relation.get("Target").lstrip("/") not in keep:
            rels.remove(relation)
    ET.register_namespace("", writer.REL)
    members["3D/_rels/3dmodel.model.rels"] = writer.xml(rels)
    ET.register_namespace("", writer.CORE)

    config = ET.fromstring(members["Metadata/model_settings.config"])
    for obj in config.findall("object"):
        if obj.get("id") != part["object_id"]:
            config.remove(obj)
    plate = config.find("plate")
    plate.find("metadata[@key='plater_name']").set("value", "Industrial base rear seam evaluation")
    for instance in plate.findall("model_instance"):
        if instance.find("metadata[@key='object_id']").get("value") != part["object_id"]:
            plate.remove(instance)
    assemble = config.find("assemble")
    for entry in list(assemble):
        if entry.get("object_id") != part["object_id"]:
            assemble.remove(entry)
        elif entry.get("instance_id") is not None:
            entry.set("transform", item.get("transform"))
    members["Metadata/model_settings.config"] = writer.xml(config)
    writer.archive_write(PROJECT, members)
    row = dict(part)
    row["build_transform"] = list(part["build_transform"])
    row["build_transform"][9] += dx
    row["plate_translation_mm"] = list(part["plate_translation_mm"])
    row["plate_translation_mm"][0] += dx
    row["plate_bounds_mm"] = [list(p) for p in part["plate_bounds_mm"]]
    for point in row["plate_bounds_mm"]:
        point[0] += dx
    report = {
        "evaluation_only": True,
        "one_time_exception": True,
        "authorization_quote": "Alright, mark2 is open, let's try your fix for the seam. I think for this evaluation, and this evaluation only, this is a one time exception I am making, print just the faucet base, thanks.",
        "normal_complete_recipe_changed": False,
        "source_complete_project": str(SOURCE.relative_to(ROOT)),
        "source_complete_project_sha256": sha(SOURCE),
        "project": str(PROJECT.relative_to(ROOT)),
        "project_sha256": sha(PROJECT),
        "settings_payload_unchanged": True,
        "settings_sha256": hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
        "retained_mesh_members_sha256": {name: hashlib.sha256(members[name]).hexdigest()
                                        for name in sorted(keep)},
        "rear_seam_enforcement": source_report["rear_seam_enforcement"],
        "parts": [row],
        "placement_change_mm": [dx, 0, 0],
        "printer": "Mark2",
        "material": "PET-GF",
        "nozzle_mapping": "Left fixed 0.4 mm; external spool 254",
        "requested_z_trim_mm": 0.04,
        "submitted": False,
    }
    PROJECT.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    NATIVE.mkdir(parents=True, exist_ok=True)
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
               "--slice", "0", "--arrange", "0", "--orient", "0",
               "--export-3mf", STEM + ".gcode.3mf", "--outputdir", str(NATIVE), str(PROJECT)]
    with (NATIVE / "slice.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((NATIVE / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    archive = NATIVE / (STEM + ".gcode.3mf")
    (HERE / archive.name).write_bytes(archive.read_bytes())
    plate, = result["sliced_plates"]
    print(json.dumps({"project": PROJECT.name, "native_archive": archive.name,
                      "estimated_seconds": plate["total_predication"],
                      "estimated_grams": sum(f["total_used_g"] for f in plate["filaments"]),
                      "warning": plate["warning_message"]}))


if __name__ == "__main__":
    main()
