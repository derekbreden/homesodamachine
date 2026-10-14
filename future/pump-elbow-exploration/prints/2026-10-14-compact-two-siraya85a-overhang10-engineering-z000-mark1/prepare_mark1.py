"""Duplicate the accepted Siraya elbow and slice two together; no printer action."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
BASE = HERE.parent / "2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1"
BASE_STEM = "2026-10-14-compact-single-elbow-siraya85a-overhang10-engineering-right06-z000-mark1"
STEM = "2026-10-14-compact-two-elbows-siraya85a-overhang10-engineering-right06-z000-mark1"
SETTINGS = "Metadata/project_settings.config"
SLICER = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
LABEL = "Two Siraya TPU elbows - Mark1"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def uid(label):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "homesodamachine/siraya-two-elbows/" + label))


def xml(element):
    return ET.tostring(element, encoding="UTF-8", xml_declaration=True)


def set_meta(parent, key, value):
    found = next((e for e in parent.findall("metadata") if e.get("key") == key), None)
    if found is None:
        found = ET.SubElement(parent, "metadata", key=key)
    found.set("value", str(value))


def main():
    with zipfile.ZipFile(BASE / (BASE_STEM + ".3mf")) as z:
        members = {n: z.read(n) for n in z.namelist()}
    recipe = json.loads(members[SETTINGS])
    recipe["print_settings_id"] = "Two accepted Siraya85A elbows 215C overhang10 Engineering Plate zero Z trim Mark1"
    recipe["seam_position"] = "nearest"
    recipe["reduce_crossing_wall"] = "1"
    members[SETTINGS] = (json.dumps(recipe, indent=2) + "\n").encode()
    model = ET.fromstring(members["3D/3dmodel.model"])
    q = lambda name: f"{{{CORE}}}{name}"
    model.find(f"{q('metadata')}[@name='Title']").text = LABEL
    resources, build = model.find(q("resources")), model.find(q("build"))
    original = resources.find(q("object"))
    duplicate = deepcopy(original)
    duplicate.set("id", "3")
    duplicate.set(f"{{{PROD}}}UUID", uid("owner-2"))
    for component in duplicate.iter(q("component")):
        component.set(f"{{{PROD}}}UUID", uid("component-2"))
    resources.append(duplicate)
    first = build.find(q("item"))
    second = deepcopy(first)
    second.set("objectid", "3")
    second.set(f"{{{PROD}}}UUID", uid("build-2"))
    build.append(second)
    placements = []
    for i, (item, y) in enumerate(zip((first, second), (148.5, 171.5)), 1):
        transform = f"1 0 0 0 1 0 0 0 1 177.500000000 {y:.9f} 0"
        item.set("transform", transform)
        placements.append(dict(name=f"Accepted Siraya elbow {i}", object_id=i+1,
                               identify_id=1900+i, transform=transform,
                               plate_translation_mm=[177.5, y, 0.0]))
    config = ET.fromstring(members["Metadata/model_settings.config"])
    owner = config.find("object")
    copy = deepcopy(owner)
    copy.set("id", "3")
    for part in copy.findall("part"):
        part.set("uuid", uid("part-2"))
    config.insert(1, copy)
    for obj, row in zip((owner, copy), placements):
        set_meta(obj, "name", row["name"])
    plate = config.find("plate")
    set_meta(plate, "plater_name", LABEL)
    for instance in plate.findall("model_instance"):
        plate.remove(instance)
    assembly = config.find("assemble")
    for item in list(assembly):
        assembly.remove(item)
    for row in placements:
        instance = ET.SubElement(plate, "model_instance")
        for key, value in {"object_id": row["object_id"], "instance_id": 0,
                           "identify_id": row["identify_id"]}.items():
            set_meta(instance, key, value)
        ET.SubElement(assembly, "assemble_item", object_id=str(row["object_id"]),
                      instance_id="0", transform=row["transform"], offset="0 0 0")
    members["3D/3dmodel.model"] = xml(model)
    members["Metadata/model_settings.config"] = xml(config)
    project = HERE / (STEM + ".3mf")
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    cache = ROOT / ".cache/pump-elbow-exploration/siraya85a-two"
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
        native_model = ET.fromstring(z.read("3D/3dmodel.model"))
        objects = ET.fromstring(z.read("Metadata/slice_info.config")).findall("plate/object")
        # Bambu emits an unused empty model when two owners share one mesh.
        # Compare the files actually referenced by the installed components.
        referenced = {c.get(f"{{{PROD}}}path").lstrip("/")
                      for c in native_model.iter(q("component"))}
        child_meshes = {n: z.read(n) for n in referenced}
    with zipfile.ZipFile(BASE / (BASE_STEM + ".gcode.3mf")) as z:
        baseline = json.loads(z.read(SETTINGS))
        baseline_model = ET.fromstring(z.read("3D/3dmodel.model"))
        referenced = {c.get(f"{{{PROD}}}path").lstrip("/")
                      for c in baseline_model.iter(q("component"))}
        baseline_meshes = {n: z.read(n) for n in referenced}
    changes = {k: {"from": baseline.get(k), "to": emitted.get(k)}
               for k in baseline.keys() | emitted.keys() if baseline.get(k) != emitted.get(k)}
    if set(changes) != {"print_settings_id", "seam_position", "reduce_crossing_wall"}:
        raise ValueError(f"Unexpected recipe differences: {changes}")
    if child_meshes != baseline_meshes:
        raise ValueError("Mesh data changed")
    if len(native_model.findall(f"{q('build')}/{q('item')}")) != 2 or len(objects) != 2:
        raise ValueError("Native slice does not contain two objects and instances")
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0]:
        raise ValueError(f"Unexpected Z trim: {trims}")
    (run / "plate_1.gcode").write_bytes(gcode)
    row, = result["sliced_plates"]
    record = dict(status="Offline; not submitted", printer="Mark1 (H2C)",
        prepared_at=datetime.now(timezone.utc).isoformat(), baseline_archive=str((BASE / (BASE_STEM + ".gcode.3mf")).relative_to(ROOT)),
        baseline_archive_sha256=sha((BASE / (BASE_STEM + ".gcode.3mf")).read_bytes()),
        project=project.name, project_sha256=sha(project.read_bytes()), archive=archive.name,
        archive_sha256=sha(archive.read_bytes()), gcode_sha256=sha(gcode),
        native_settings_differences=changes, native_mesh_bytes_match_accepted_single=True,
        native_referenced_mesh_sha256={n: sha(data) for n, data in child_meshes.items()},
        native_objects=[dict(o.attrib) for o in objects], placements=placements,
        centre_separation_y_mm=23.0, plate_trim_commands_mm=trims,
        estimated_seconds=row["total_predication"],
        estimated_filament_g=sum(f["total_used_g"] for f in row["filaments"]),
        slicer_warning=row["warning_message"], cache_run=str(run.relative_to(ROOT)))
    (HERE / "native-readback.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
