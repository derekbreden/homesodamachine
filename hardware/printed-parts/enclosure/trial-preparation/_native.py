"""Write one native Bambu Studio plate project without a CAD kernel or the slicer.

The printer recipe is a saved project's own settings members, taken as
`hardware/printed-parts/faucet/refresh_print_project.py` takes them: the
requested user Z trim replaces the start G-code's plate-compensation block with
that writer's block text, the usable plate is the reachable area of the nozzles
the job maps its filaments to, and `cadlib/petgf_cooling.py` applies the
localized PET-GF cooling values to the project and its embedded filament presets.

Object meshes stream into the archive member by member.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import quoteattr
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path.insert(0, str(ROOT / "hardware/printed-parts/cadlib"))
import petgf_cooling  # noqa: E402

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
MODEL_TYPE = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
SETTINGS_MEMBER = "Metadata/project_settings.config"
IDENTITY = "1 0 0 0 1 0 0 0 1 0 0 0"
MATRIX = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)


def qn(name: str) -> str:
    return f"{{{CORE}}}{name}"


def identifier(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "homesodamachine/enclosure-trial/" + name))


def _xml(element) -> bytes:
    return ET.tostring(element, xml_declaration=True, encoding="UTF-8")


def _metadata(parent, key, value):
    ET.SubElement(parent, "metadata", key=key, value=str(value))


PRESETS = Path("/Applications/BambuStudio.app/Contents/Resources/profiles/BBL")
PRESET_METADATA = {"type", "name", "inherits", "include", "from", "setting_id", "instantiation", "description",
                   "alias", "filament_id", "version", "rename", "compatible_printers",
                   "compatible_printers_condition", "compatible_prints", "compatible_prints_condition"}


def filament_keys(name: str) -> set:
    """Every setting Bambu's filament presets define, through the named preset's parents and templates."""
    data = json.loads((PRESETS / "filament" / f"{name}.json").read_text())
    keys = set(data) - PRESET_METADATA
    for parent in ([data["inherits"]] if data.get("inherits") else []) + list(data.get("include", [])):
        keys |= filament_keys(parent)
    return keys


def take_filament(settings: dict, filament_from: Path) -> tuple[dict, dict]:
    """Another saved project's filament block over this project's printer and process.

    The block is every setting the filament's system presets define, plus the variant index
    that ties its per-hotend arrays together. Returns the embedded filament presets that
    describe it (those named as the project's filament) and the record of what moved."""
    with zipfile.ZipFile(filament_from) as other:
        theirs = json.loads(other.read(SETTINGS_MEMBER))
        presets = {n: other.read(n) for n in other.namelist()
                   if n.startswith("Metadata/filament_settings_") and n.endswith(".config")}
    named = theirs["filament_settings_id"][0]
    current = {n: data for n, data in presets.items() if json.loads(data).get("name") == named}
    system = next((json.loads(data).get("inherits") for data in current.values()), None) or named
    keys = filament_keys(system) | {k for data in current.values() for k in json.loads(data)} - PRESET_METADATA
    keys |= {"filament_self_index"}
    moved = sorted(k for k in keys if k in theirs and settings.get(k) != theirs[k])
    for key in moved:
        settings[key] = theirs[key]
    for group in ("inherits_group", "different_settings_to_system"):
        if isinstance(theirs.get(group), list) and isinstance(settings.get(group), list) \
                and len(theirs[group]) == len(settings[group]):
            settings[group] = settings[group][:1] + theirs[group][1:-1] + settings[group][-1:]
    return current, {"project": str(filament_from.resolve().relative_to(ROOT)),
                     "sha256": hashlib.sha256(filament_from.read_bytes()).hexdigest(),
                     "filament": named, "system_preset": system, "keys": moved}


def profile_settings(settings_from: Path, z_trim: float | None, filament_from: Path | None = None) -> dict:
    """The saved project's settings and filament members with trim and cooling applied.

    `filament_from` replaces the project's filament block with another saved project's."""
    with zipfile.ZipFile(settings_from) as source:
        if source.testzip() is not None:
            raise ValueError("source project has a damaged member")
        payload = source.read(SETTINGS_MEMBER)
        original = payload
        settings = json.loads(payload)
        changes = {}
        filament_members = None
        if filament_from is not None:
            filament_members, changes["filament_from"] = take_filament(settings, filament_from)
            payload = (json.dumps(settings, indent=2) + "\n").encode()
        if z_trim is not None:
            if not math.isfinite(z_trim):
                raise ValueError("Z trim must be a finite millimetre value")
            start = settings["machine_start_gcode"]
            marker = re.search(r"(?m)^;===== (?:for Textured PEI Plate|plate compensation plus user-calibrated)", start)
            if marker is None:
                raise ValueError("The profile has no recognized plate-compensation block")
            end = start.index("\nG150.1", marker.start())
            block = f''';===== plate compensation plus user-calibrated +{z_trim:.2f} mm Z trim =====
{{if curr_bed_type=="Textured PEI Plate"}}
    {{if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}}
        G29.1 Z{{{z_trim:.2f} - 0.01}}
    {{else}}
        G29.1 Z{{{z_trim:.2f} - 0.02}}
    {{endif}}
{{else}}
    {{if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}}
        G29.1 Z{{{z_trim:.2f} + 0.01}}
    {{else}}
        G29.1 Z{{{z_trim:.2f}}}
    {{endif}}
{{endif}}'''
            settings["machine_start_gcode"] = start[:marker.start()] + block + start[end:]
            nozzle = float(settings["nozzle_diameter"][0])
            identity = f"Bambu Lab H2C {nozzle:g} Standard +{z_trim:.2f} Z trim"
            changes.update({
                "machine_start_gcode": {"from_sha256": hashlib.sha256(start.encode()).hexdigest(),
                                        "to_sha256": hashlib.sha256(settings["machine_start_gcode"].encode()).hexdigest(),
                                        "requested_z_trim_mm": z_trim},
                "printer_settings_id": {"from": settings["printer_settings_id"], "to": identity}})
            settings["printer_settings_id"] = identity
            # The slicer refuses a process whose compatible printers do not name the printer
            # (error 3002) when the project carries no system parent to match instead.
            compatible = settings.get("print_compatible_printers")
            if isinstance(compatible, list) and identity not in compatible:
                settings["print_compatible_printers"] = compatible + [identity]
                changes["print_compatible_printers"] = {"from": compatible, "to": settings["print_compatible_printers"]}
            payload = (json.dumps(settings, indent=2) + "\n").encode()
        areas = [np.array([[float(v) for v in point.split("x")] for point in area.split(",")])
                 for area in settings.get("extruder_printable_area", [])]
        used = sorted({int(n) for n in settings.get("filament_nozzle_map", [])} & set(range(len(areas))))
        chosen = [areas[i] for i in used] if used else areas
        bed = np.array([[float(v) for v in point.split("x")] for point in settings["printable_area"]])
        low = np.max([a.min(axis=0) for a in chosen], axis=0) if chosen else bed.min(axis=0)
        high = np.min([a.max(axis=0) for a in chosen], axis=0) if chosen else bed.max(axis=0)
        members = {SETTINGS_MEMBER: payload}
        if filament_members is not None:
            members.update(filament_members)
        else:
            for name in source.namelist():
                if name.startswith("Metadata/filament_settings_") and name.endswith(".config"):
                    members[name] = source.read(name)
    cooling = petgf_cooling.apply_members(members)
    changes.update(cooling.get(SETTINGS_MEMBER, {}))
    return {"members": members, "settings": json.loads(members[SETTINGS_MEMBER]),
            "changes": changes, "cooling_member_changes": cooling, "original_payload": original,
            "usable_low": low.tolist(), "usable_high": high.tolist(),
            "printable_area_extruders": used if used else list(range(len(areas)))}


class Plate:
    """One plate of objects; each object is a normal part plus its declared extra parts."""

    def __init__(self, title: str, profile: dict):
        self.title = title
        self.profile = profile
        self.settings = dict(profile["settings"])
        self.objects: list[dict] = []
        self._next_id = 1

    def _id(self) -> int:
        value = self._next_id
        self._next_id += 1
        return value

    def add_object(self, name: str, vertices: np.ndarray, faces: np.ndarray, *, source_file: str,
                   source_center, build_rotation: np.ndarray, translation, paint=None,
                   settings: dict | None = None) -> dict:
        """`vertices` are in the source frame less `source_center`; the build item rotates and
        places them: plate = build_rotation @ local + translation."""
        part_id, object_id = self._id(), self._id()
        obj = {"name": name, "object_id": object_id, "part_id": part_id,
               "identify_id": 1900 + len(self.objects) + 1, "source_file": source_file,
               "source_center_mm": [float(v) for v in source_center],
               "build_rotation": np.asarray(build_rotation, float).tolist(),
               "translation_mm": [float(v) for v in translation],
               "member": f"3D/Objects/object_{len(self.objects) + 1}.model",
               "mesh": (vertices, faces, paint), "settings": dict(settings or {}),
               "parts": [], "ranges": []}
        self.objects.append(obj)
        return obj

    def add_part(self, obj: dict, name: str, vertices: np.ndarray, faces: np.ndarray, *,
                 subtype: str, settings: dict | None = None, paint_all: str | None = None) -> dict:
        part = {"name": name, "id": self._id(), "subtype": subtype,
                "member": f"3D/Objects/{re.sub(r'[^A-Za-z0-9_.-]+', '-', name).strip('-')}-{len(obj['parts']) + 1}-{obj['object_id']}.model",
                "mesh": (np.asarray(vertices, float), np.asarray(faces, int),
                         None if paint_all is None else [paint_all] * len(faces)),
                "settings": dict(settings or {})}
        obj["parts"].append(part)
        return part

    def transform_values(self, obj: dict) -> list[float]:
        rotation = np.array(obj["build_rotation"])
        return [*rotation.T.reshape(-1).tolist(), *obj["translation_mm"]]

    @staticmethod
    def _stream_mesh(archive: zipfile.ZipFile, member: str, object_id: int, vertices, faces, paint):
        info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        with archive.open(info, "w") as out:
            out.write((f"<?xml version='1.0' encoding='UTF-8'?>\n<model xmlns=\"{CORE}\" unit=\"millimeter\">"
                       f"<resources><object id=\"{object_id}\" type=\"model\"><mesh><vertices>").encode())
            for start in range(0, len(vertices), 50000):
                out.write("".join(f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>'
                                  for x, y, z in vertices[start:start + 50000].tolist()).encode())
            out.write(b"</vertices><triangles>")
            for start in range(0, len(faces), 50000):
                rows = faces[start:start + 50000].tolist()
                codes = paint[start:start + 50000] if paint is not None else [None] * len(rows)
                serialized = []
                for (a, b, c), code in zip(rows, codes):
                    attributes = code if isinstance(code, dict) else ({"paint_supports": code} if code and code != "0" else {})
                    suffix = "".join(f' {key}="{value}"' for key, value in attributes.items())
                    serialized.append(f'<triangle v1="{a}" v2="{b}" v3="{c}"{suffix}/>')
                out.write("".join(serialized).encode())
            out.write(b"</triangles></mesh></object></resources></model>")

    def write(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        model = ET.Element(qn("model"), unit="millimeter", requiredextensions="p",
                           **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
        ET.SubElement(model, qn("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
        ET.SubElement(model, qn("metadata"), name="BambuStudio:3mfVersion").text = "1"
        ET.SubElement(model, qn("metadata"), name="Title").text = self.title
        resources = ET.SubElement(model, qn("resources"))
        build = ET.SubElement(model, qn("build"), **{f"{{{PROD}}}UUID": identifier(self.title + "/build")})
        config = ET.Element("config")
        plate = ET.Element("plate")
        for key, value in {"plater_id": 1, "plater_name": self.title, "locked": "false",
                           "filament_map_mode": "Auto For Flush",
                           "filament_maps": " ".join(self.settings.get("filament_map", ["1"])),
                           "filament_volume_maps": "0", "bed_type": self.settings["curr_bed_type"]}.items():
            _metadata(plate, key, value)
        assemble = ET.Element("assemble")
        rels = ET.Element(f"{{{REL}}}Relationships")
        ranges = ET.Element("objects")
        for index, obj in enumerate(self.objects, 1):
            name = obj["name"]
            owner = ET.SubElement(resources, qn("object"), id=str(obj["object_id"]), type="model",
                                  **{f"{{{PROD}}}UUID": identifier(name)})
            components = ET.SubElement(owner, qn("components"))
            ET.SubElement(components, qn("component"), objectid=str(obj["part_id"]), transform=IDENTITY,
                          **{f"{{{PROD}}}path": "/" + obj["member"], f"{{{PROD}}}UUID": identifier(name + "/component")})
            ET.SubElement(rels, f"{{{REL}}}Relationship", Target="/" + obj["member"], Id=f"rel-{index}", Type=MODEL_TYPE)
            transform = " ".join(f"{v:.9f}" for v in self.transform_values(obj))
            ET.SubElement(build, qn("item"), objectid=str(obj["object_id"]), transform=transform, printable="1",
                          **{f"{{{PROD}}}UUID": identifier(name + "/item")})
            cfg = ET.SubElement(config, "object", id=str(obj["object_id"]))
            _metadata(cfg, "name", name)
            _metadata(cfg, "extruder", 1)
            for key, value in obj["settings"].items():
                _metadata(cfg, key, value)
            faces = obj["mesh"][1]
            ET.SubElement(cfg, "metadata", face_count=str(len(faces)))
            part = ET.SubElement(cfg, "part", id=str(obj["part_id"]), subtype="normal_part",
                                 uuid=identifier(name + "/part"))
            center = obj["source_center_mm"]
            for key, value in {"name": name, "matrix": MATRIX, "source_file": obj["source_file"],
                               "source_object_id": 0, "source_volume_id": 0, "source_offset_x": center[0],
                               "source_offset_y": center[1], "source_offset_z": center[2]}.items():
                _metadata(part, key, value)
            ET.SubElement(part, "mesh_stat", face_count=str(len(faces)), edges_fixed="0", degenerate_facets="0",
                          facets_removed="0", facets_reversed="0", backwards_edges="0")
            for extra in obj["parts"]:
                attributes = {f"{{{PROD}}}path": "/" + extra["member"]}
                if extra["subtype"] == "normal_part":
                    attributes[f"{{{PROD}}}UUID"] = identifier(name + "/" + extra["member"])
                ET.SubElement(components, qn("component"), objectid=str(extra["id"]), transform=IDENTITY, **attributes)
                ET.SubElement(rels, f"{{{REL}}}Relationship", Target="/" + extra["member"],
                              Id=f"part-{extra['id']}", Type=MODEL_TYPE)
                element = ET.SubElement(cfg, "part", id=str(extra["id"]), subtype=extra["subtype"],
                                        uuid=identifier(name + "/" + extra["member"] + "/part"))
                _metadata(element, "name", extra["name"])
                _metadata(element, "matrix", MATRIX)
                for key, value in extra["settings"].items():
                    _metadata(element, key, value)
                ET.SubElement(element, "mesh_stat", face_count=str(len(extra["mesh"][1])), edges_fixed="0",
                              degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
            instance = ET.SubElement(plate, "model_instance")
            for key, value in {"object_id": obj["object_id"], "instance_id": 0, "identify_id": obj["identify_id"]}.items():
                _metadata(instance, key, value)
            ET.SubElement(assemble, "assemble_item", object_id=str(obj["object_id"]), instance_id="0",
                          transform=transform, offset="0 0 0")
            ET.SubElement(assemble, "assemble_item", object_id=str(obj["object_id"]), volume_id="0",
                          transform=IDENTITY)
            if obj["ranges"]:
                # Bambu keys layer ranges by the object's 1-based plate order.
                element = ET.SubElement(ranges, "object", id=str(index))
                for band in obj["ranges"]:
                    span = ET.SubElement(element, "range", min_z=f"{band['min_z']:.4f}", max_z=f"{band['max_z']:.4f}")
                    for key, value in band["options"].items():
                        ET.SubElement(span, "option", opt_key=key).text = str(value)
        config.append(plate)
        config.append(assemble)
        root_rels = ET.Element(f"{{{REL}}}Relationships")
        ET.SubElement(root_rels, f"{{{REL}}}Relationship", Target="/3D/3dmodel.model", Id="rel-1", Type=MODEL_TYPE)
        fixed = lambda element: _xml(element).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
        members = dict(self.profile["members"])
        members[SETTINGS_MEMBER] = (json.dumps(self.settings, indent=2) + "\n").encode()
        members["3D/3dmodel.model"] = _xml(model)
        members["3D/_rels/3dmodel.model.rels"] = fixed(rels)
        members["_rels/.rels"] = fixed(root_rels)
        members["Metadata/model_settings.config"] = _xml(config)
        if len(ranges):
            members["Metadata/layer_config_ranges.xml"] = _xml(ranges)
        members["[Content_Types].xml"] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="config" ContentType="application/octet-stream"/>
</Types>'''
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, data in sorted(members.items()):
                entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o644 << 16
                archive.writestr(entry, data)
            for obj in self.objects:
                self._stream_mesh(archive, obj["member"], obj["part_id"], *obj["mesh"])
                for extra in obj["parts"]:
                    self._stream_mesh(archive, extra["member"], extra["id"], *extra["mesh"])
        temporary.replace(path)


def coordinates_project(project: Path, object_id: int, output: Path) -> Path:
    """A copy of the project holding one object, for readers that map plate to CAD by its item."""
    with zipfile.ZipFile(project) as source:
        members = {name: source.read(name) for name in source.namelist()}
    model = ET.fromstring(members["3D/3dmodel.model"])
    resources, build = model.find(qn("resources")), model.find(qn("build"))
    for item in list(resources):
        if item.get("id") != str(object_id):
            resources.remove(item)
    for item in list(build):
        if item.get("objectid") != str(object_id):
            build.remove(item)
    config = ET.fromstring(members["Metadata/model_settings.config"])
    for item in list(config):
        if item.tag == "object" and item.get("id") != str(object_id):
            config.remove(item)
    members["3D/3dmodel.model"] = _xml(model)
    members["Metadata/model_settings.config"] = _xml(config)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(members.items()):
            archive.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), data)
    return output
