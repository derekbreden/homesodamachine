"""TAP and two FLAVOR bulkhead rings, face up, black and white PET-GF on Mark2.

Derek, 2026-09-23: "Since Mark2 is loaded up with white pet-gf still on a 0.04 nozzle on the
right side, I'd like to do a quick run of the tap and flavor bulkhead collars there first."
The two-hotend settings are the nameplate's (`nameplate/prepare_print.py`), which printed on
Mark2: black on the left hotend (filament 1, external 254), white on the right (filament 2,
external 255). The saved profile's start G-code carries Mark2's +0.04 trim (0.02 emitted on
Textured PEI).
"""
import copy, hashlib, json, os, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
RING = ROOT / "hardware/printed-parts/enclosure/bulkhead-ring"
sys.path.insert(0, str(RING))
import cadquery as cq
import trimesh
import bulkhead_ring as ring

PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", CORE)
Q = lambda name: f"{{{CORE}}}{name}"
STEM = "bulkhead-rings-tap-flavor-black-white-z004-mark2-v1"
BLACK, WHITE = 1, 2
# (station, chip filament, word filament, bed centre)
PLATE = (("water", WHITE, BLACK, (115.0, 125.0)),
         ("flavor-a", BLACK, WHITE, (165.0, 125.0)),
         ("flavor-b", BLACK, WHITE, (215.0, 125.0)))


def meta(parent, key, value):
    ET.SubElement(parent, "metadata", key=key, value=str(value))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def face_up(shape):
    """The chip's outboard face (+Y in the seat frame) turned to +Z, seating face on the bed."""
    return shape.rotate((0, 0, 0), (1, 0, 0), 90.0)


def prepare():
    with zipfile.ZipFile(PROFILE) as source:
        settings = json.loads(source.read("Metadata/project_settings.config"))
        filament_values = json.loads(source.read("Metadata/filament_settings_1.config"))
    filament_values["filament_printable"] = ["3"]
    filament = json.dumps(filament_values, indent=2).encode()
    original = copy.deepcopy(settings)
    for key, value in list(settings.items()):
        if isinstance(value, list) and len(value) in (1, len(original["filament_extruder_variant"])):
            settings[key] = value * 2
    settings.update(filament_colour=["#000000", "#FFFFFF"], filament_map=["1", "2"],
                    filament_map_2=["1", "2"], filament_nozzle_map=["0", "1"],
                    filament_map_mode="Manual", filament_volume_map=["0", "0"],
                    filament_self_index=["1"] * len(original["filament_extruder_variant"])
                                        + ["2"] * len(original["filament_extruder_variant"]),
                    filament_printable=["3", "3"],
                    extruder_ams_count=["1#0|4#0", "1#0|4#0"],
                    filament_prime_volume=["45", "45"],
                    flush_volumes_vector=["140"] * 4,
                    flush_volumes_matrix=["0", "140", "140", "0"] * 2)
    # 0.20 layers: ten of them make the 2.0 mm chip exactly, and the word's 1.0 mm floor
    # falls on a layer boundary. 0.24 layers print it 2.12 mm with the floor mid-layer.
    settings["layer_height"] = "0.2"
    # Solid through: the chip is a washer the fitting's nut clamps between flange and wall.
    settings["bottom_shell_layers"] = "5"
    settings["top_shell_layers"] = "5"
    model = ET.Element(Q("model"), unit="millimeter")
    ET.SubElement(model, Q("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
    ET.SubElement(model, Q("metadata"), name="BambuStudio:3mfVersion").text = "1"
    resources = ET.SubElement(model, Q("resources")); build = ET.SubElement(model, Q("build"))
    config = ET.Element("config"); plater = ET.Element("plate")
    for key, value in {"plater_id": 1, "plater_name": "TAP and FLAVOR bulkhead rings",
                       "locked": "false", "bed_type": settings["curr_bed_type"],
                       "filament_map_mode": "Manual", "filament_maps": "1 2",
                       "filament_volume_maps": "0 0"}.items():
        meta(plater, key, value)
    meshes, next_id = [], 1
    for station, chip_f, word_f, (bx, by) in PLATE:
        chip, word = ring.split(cq.importers.importStep(str(ring.STEPS[station])).val())
        chip, word = face_up(chip), face_up(word)
        bb = chip.BoundingBox()
        shift = cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin)
        ids = []
        for shape, part in ((chip, "chip"), (word, "word")):
            shape = shape.translate(shift)
            vertices, faces = shape.tessellate(.015, .05)
            mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices], faces=faces, process=True)
            if not mesh.is_watertight or not mesh.is_winding_consistent:
                raise ValueError(f"{station} {part} mesh is not closed and consistently oriented")
            obj = ET.SubElement(resources, Q("object"), id=str(next_id), type="model")
            geometry = ET.SubElement(obj, Q("mesh"))
            vs = ET.SubElement(geometry, Q("vertices")); ts = ET.SubElement(geometry, Q("triangles"))
            for vertex in mesh.vertices:
                ET.SubElement(vs, Q("vertex"), **dict(zip("xyz", (f"{v:.8f}" for v in vertex))))
            for tri in mesh.faces:
                ET.SubElement(ts, Q("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, tri))))
            meshes.append({"station": station, "part": part, "faces": len(mesh.faces),
                           "bounds": mesh.bounds.tolist(), "volume_mm3": float(mesh.volume),
                           "bodies": len(mesh.split(only_watertight=False))})
            ids.append((next_id, f"{station} {part}", chip_f if part == "chip" else word_f))
            next_id += 1
        obj_id = next_id; next_id += 1
        obj = ET.SubElement(resources, Q("object"), id=str(obj_id), type="model")
        components = ET.SubElement(obj, Q("components"))
        cfg = ET.SubElement(config, "object", id=str(obj_id))
        meta(cfg, "name", f"bulkhead-ring-{station}"); meta(cfg, "extruder", 1)
        for child, name, extruder in ids:
            ET.SubElement(components, Q("component"), objectid=str(child))
            part = ET.SubElement(cfg, "part", id=str(child), subtype="normal_part")
            meta(part, "name", name); meta(part, "extruder", extruder)
            meta(part, "matrix", "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
        ET.SubElement(build, Q("item"), objectid=str(obj_id),
                      transform=f"1 0 0 0 1 0 0 0 1 {bx} {by} 0", printable="1")
        instance = ET.SubElement(plater, "model_instance")
        for key, value in {"object_id": obj_id, "instance_id": 0, "identify_id": 2300 + obj_id}.items():
            meta(instance, key, value)
    config.append(plater)
    members = {"3D/3dmodel.model": ET.tostring(model, encoding="UTF-8", xml_declaration=True),
               "Metadata/model_settings.config": ET.tostring(config, encoding="UTF-8", xml_declaration=True),
               "Metadata/project_settings.config": json.dumps(settings, indent=2).encode(),
               "Metadata/filament_settings_1.config": filament,
               "Metadata/filament_settings_2.config": filament,
               "_rels/.rels": b'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>''',
               "[Content_Types].xml": b'''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'''}
    out = HERE / f"{STEM}-input.3mf"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    report = {"layer_height_mm": 0.2, "project": str(out.relative_to(ROOT)), "project_sha256": sha(out),
              "source_steps": {s: {"path": str(ring.STEPS[s].relative_to(ROOT)), "sha256": sha(ring.STEPS[s])}
                               for s, *_ in PLATE},
              "profile_source": str(PROFILE.relative_to(ROOT)), "profile_sha256": sha(PROFILE),
              "meshes": meshes, "orientation": "face up: seating face on the bed, word in the top 1 mm",
              "printer": "Mark2", "requested_z_trim_mm": 0.04,
              "filaments": {"1": "Black PET-GF, left hotend, external 254",
                            "2": "White PET-GF, right hotend, external 255"},
              "assignment": {s: {"chip": {1: "black", 2: "white"}[c], "word": {1: "black", 2: "white"}[w]}
                             for s, c, w, _ in PLATE}}
    (HERE / "preparation.json").write_text(json.dumps(report, indent=2) + "\n")
    return out


def slice_(project):
    directory = HERE / "ready"; directory.mkdir()
    with (directory / "bambu-cli.log").open("w") as log:
        result = subprocess.run(["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
                                 "--slice", "0", "--arrange", "0", "--orient", "0",
                                 "--outputdir", str(directory), "--export-3mf", f"{STEM}.gcode.3mf",
                                 str(project)], cwd=directory, stdout=log, stderr=subprocess.STDOUT)
    return result.returncode


if __name__ == "__main__":
    project = prepare(); print(project, flush=True)
    code = slice_(project); print("slice exit", code); raise SystemExit(code)
