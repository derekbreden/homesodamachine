"""Build and slice one connected, cutaway-web elbow pair offline; no send."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
BASE = HERE.parent / "2026-10-16-departure-lap040-normal-lift-tpu85a-mark1"
STEM = "2026-10-16-elbow-pair-cutaway-web-tpu85a-right06-z000-mark1"
SETTINGS = "Metadata/project_settings.config"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
Q = lambda name: f"{{{CORE}}}{name}"
ET.register_namespace("", CORE)
ET.register_namespace("p", "http://schemas.microsoft.com/3dmanufacturing/production/2015/06")
sys.path.insert(0, str(HERE.parent.parent))
from sacrificial_web import build, solid, sections
from wall_travel import route


def sha(data):
    return hashlib.sha256(data).hexdigest()


def xml(element):
    return ET.tostring(element, encoding="UTF-8", xml_declaration=True)


def mesh_xml(template, mesh):
    child = ET.fromstring(template)
    owner = child.find(f"{Q('resources')}/{Q('object')}")
    owner.remove(owner.find(Q("mesh")))
    me = ET.SubElement(owner, Q("mesh"))
    vertices, triangles = ET.SubElement(me, Q("vertices")), ET.SubElement(me, Q("triangles"))
    for v in mesh.vertices:
        ET.SubElement(vertices, Q("vertex"), **dict(zip("xyz", (f"{x:.9f}" for x in v))))
    for f in mesh.faces:
        ET.SubElement(triangles, Q("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, f))))
    return xml(child)


def main():
    source = next(p for p in BASE.glob("*.3mf") if not p.name.endswith(".gcode.3mf"))
    mesh, web, geometry = build(source, joining_web="follow_leg")
    mesh.export(HERE / "connected-pair.stl")
    web.export(HERE / "cutaway-web.stl")
    body = solid(mesh)
    layer_z = [.1] + [.26 + .12 * i for i in range(183)]
    island_counts = [len(sections(body, z)) for z in layer_z]
    geometry.update(source_project=str(source.relative_to(ROOT)),
                    source_project_sha256=sha(source.read_bytes()),
                    layer_section_heights_mm=layer_z,
                    connected_islands_per_layer=island_counts,
                    all_184_layer_sections_connected=all(n == 1 for n in island_counts))
    (HERE / "geometry-review.json").write_text(json.dumps(geometry, indent=2) + "\n")
    if not geometry["all_184_layer_sections_connected"]:
        raise ValueError("A printed layer has disconnected islands")
    with zipfile.ZipFile(source) as z:
        members = {n: z.read(n) for n in z.namelist()}
    recipe = json.loads(members[SETTINGS])
    recipe.update(print_settings_id="Connected Bambu85A elbow pair cutaway web 0.4 Normal Lift Mark1",
                  time_lapse_gcode="",
                  retraction_minimum_travel=["0.1"] * len(recipe["retraction_minimum_travel"]),
                  filament_retraction_minimum_travel=["0.1"] * len(recipe["filament_retraction_minimum_travel"]))
    members[SETTINGS] = (json.dumps(recipe, indent=2) + "\n").encode()
    model = ET.fromstring(members["3D/3dmodel.model"])
    model.find(f"{Q('metadata')}[@name='Title']").text = "Connected cutaway-web TPU elbows - Mark1"
    resources = model.find(Q("resources"))
    resources.remove(resources.findall(Q("object"))[1])
    build_items = model.find(Q("build"))
    build_items.remove(build_items.findall(Q("item"))[1])
    members["3D/3dmodel.model"] = xml(model)
    members["3D/Objects/full_base_single_elbow.model"] = mesh_xml(
        members["3D/Objects/full_base_single_elbow.model"], mesh)
    config = ET.fromstring(members["Metadata/model_settings.config"])
    config.remove(config.findall("object")[1])
    owner = config.find("object")
    owner.find("metadata[@key='name']").set("value", "Connected cutaway-web TPU elbow pair")
    owner.find("metadata[@face_count]").set("face_count", str(len(mesh.faces)))
    part = owner.find("part")
    part.find("metadata[@key='name']").set("value", "connected-pair")
    part.find("metadata[@key='source_file']").set("value", "connected-pair.stl")
    part.find("mesh_stat").set("face_count", str(len(mesh.faces)))
    plate = config.find("plate")
    plate.find("metadata[@key='plater_name']").set("value", "Connected cutaway-web TPU elbows - Mark1")
    plate.remove(plate.findall("model_instance")[1])
    assembly = config.find("assemble")
    assembly.remove(assembly.findall("assemble_item")[1])
    members["Metadata/model_settings.config"] = xml(config)
    project = HERE / (STEM + ".3mf")
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    single, _, single_geometry = build(source, copies=1, joining_web="follow_leg")
    single.export(HERE / "single-elbow-with-fin.stl")
    single_body = solid(single)
    single_counts = [len(sections(single_body, z)) for z in layer_z]
    if any(n != 1 for n in single_counts):
        raise ValueError("A standalone elbow layer separates")
    single_geometry.update(connected_islands_per_layer=single_counts,
                           all_184_layer_sections_connected=True)
    (HERE / "single-geometry-review.json").write_text(json.dumps(single_geometry, indent=2) + "\n")
    single_members = dict(members)
    single_members["3D/Objects/full_base_single_elbow.model"] = mesh_xml(
        members["3D/Objects/full_base_single_elbow.model"], single)
    single_model = ET.fromstring(members["3D/3dmodel.model"])
    single_model.find(f"{Q('metadata')}[@name='Title']").text = "One TPU elbow with cutaway leg fin"
    centre = "1 0 0 0 1 0 0 0 1 177.5 160 0"
    single_model.find(f"{Q('build')}/{Q('item')}").set("transform", centre)
    single_members["3D/3dmodel.model"] = xml(single_model)
    single_config = ET.fromstring(members["Metadata/model_settings.config"])
    single_config.find("object/metadata[@key='name']").set("value", "One TPU elbow with cutaway leg fin")
    single_config.find("plate/metadata[@key='plater_name']").set("value", "One TPU elbow with cutaway leg fin")
    single_config.find("object/metadata[@face_count]").set("face_count", str(len(single.faces)))
    single_config.find("object/part/mesh_stat").set("face_count", str(len(single.faces)))
    single_config.find("object/part/metadata[@key='source_file']").set("value", "single-elbow-with-fin.stl")
    single_config.find("assemble/assemble_item").set("transform", centre)
    single_members["Metadata/model_settings.config"] = xml(single_config)
    with zipfile.ZipFile(HERE / "single-elbow-with-fin.3mf", "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in single_members.items():
            z.writestr(name, data)
    cache = ROOT / ".cache/pump-elbow-exploration/cutaway-web"
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
        objects = ET.fromstring(z.read("Metadata/slice_info.config")).findall("plate/object")
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("G-code checksum differs")
    with zipfile.ZipFile(next(BASE.glob("*-native.gcode.3mf"))) as z:
        baseline = json.loads(z.read(SETTINGS))
    differences = {k: {"from": baseline.get(k), "to": emitted.get(k)}
                   for k in baseline.keys() | emitted.keys() if baseline.get(k) != emitted.get(k)}
    row, = result["sliced_plates"]
    record = dict(prepared_at=datetime.now(timezone.utc).isoformat(),
                  status="Offline candidate; not submitted", printer="Mark1 (H2C)",
                  project=project.name, project_sha256=sha(project.read_bytes()),
                  archive=native.name, archive_sha256=sha(native.read_bytes()),
                  gcode_sha256=sha(gcode), native_settings_differences=differences,
                  objects=[dict(o.attrib) for o in objects],
                  estimated_seconds=row["total_predication"],
                  estimated_filament_g=sum(f["total_used_g"] for f in row["filaments"]),
                  slicer_warning=row["warning_message"], cache_run=str(run.relative_to(ROOT)),
                  emitted_photo_trip_commands=gcode.count(b"M9711"))
    (HERE / "native-readback.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)
    route(native, HERE / (STEM + ".gcode.3mf"), HERE / "wall-travel-review.json")


if __name__ == "__main__":
    main()
