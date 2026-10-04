"""Prepare independent native PET-GF sources with one RC62 insertion pause each.

Run with --slice to export native G-code archives into the local print cache.
This never sends a print. Existing accepted archives are read-only inputs.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)
TAG = lambda name: f"{{{CORE}}}{name}"
SETTING = "Metadata/project_settings.config"
FRONT_BASE = ROOT / ".cache/prints/2026-10-03-enclosure-front-top-current-h2c-v17/enclosure-front-top-current-black-z018-h2c-v17-input.3mf"
PUMP_BASE = ROOT / ".cache/prints/2026-09-24-pump-cartridge-cap-mark2-v8/pump-cartridge-cap-black-z004-mark2-v8-six-wall-grip-rounds-input.3mf"
STUDIO = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def members(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def grip_ceiling_paint(points, depth=0):
    """Keep the production interface inside the flat ceiling's inset rectangle."""
    xy = points[:, :2].copy()
    xy[:, 0] = np.abs(xy[:, 0])
    lo, hi = np.array([92.55, 34.9325]), np.array([100.7, 49.3325])
    if ((xy >= lo) & (xy <= hi)).all():
        return "0"
    if (xy.max(axis=0) < lo).any() or (xy.min(axis=0) > hi).any() or depth == 7:
        return "8"
    a, b, c = points
    ab, bc, ca = (a+b)/2, (b+c)/2, (c+a)/2
    children = [np.array([a, ab, ca]), np.array([ab, b, bc]),
                np.array([bc, c, ca]), np.array([ab, bc, ca])]
    return "".join(grip_ceiling_paint(p, depth+1) for p in children) + "3"


def prepare(name, pocket):
    front = members(FRONT_BASE)
    base = members(PUMP_BASE) if name == "pump-cartridge" else front
    mesh = trimesh.load_mesh(ENC / f"enclosure-{name}.stl", process=True)
    assert mesh.is_watertight
    assert sha(ENC / f"enclosure-{name}.stl") == pocket["artifact_sha256"][".stl"]
    assert sha(ENC / f"enclosure-{name}.step") == pocket["artifact_sha256"][".step"]
    center = mesh.bounds.mean(axis=0)
    height = float(np.ptp(mesh.bounds[:, 2]))
    selected = copy.deepcopy(json.loads(base[SETTING]))
    assert selected["machine_pause_gcode"].strip() == "M400 U1"
    assert selected["layer_height"] == "0.24" and selected["initial_layer_print_height"] == "0.2"
    # Use the single-object production project structure. The cartridge gets
    # its own Mark2 settings and grip layer ranges, never the cap's object.
    model = ET.fromstring(front["3D/3dmodel.model"])
    component = model.find(f".//{TAG('component')}")
    member = component.get(f"{{{PROD}}}path").lstrip("/")
    item = model.find(f".//{TAG('item')}")
    transform = f"1 0 0 0 1 0 0 0 1 162.5 160 {height / 2:.9f}"
    item.set("transform", transform)
    geometry = ET.fromstring(front[member])
    geometry.set("xmlns:BambuStudio", "http://schemas.bambulab.com/package/2021")
    xml_mesh = geometry.find(f".//{TAG('mesh')}")
    xml_mesh.clear()
    vertices = ET.SubElement(xml_mesh, TAG("vertices"))
    for point in mesh.vertices - center:
        ET.SubElement(vertices, TAG("vertex"), **dict(zip("xyz", (f"{c:.9f}" for c in point))))
    triangles = ET.SubElement(xml_mesh, TAG("triangles"))
    px, _pz = pocket["axis_xz_mm"]
    ymin, ymax = pocket["pocket_y_mm"]
    r = pocket["pocket_radius_mm"]
    blocked_roof = inherited = grip_blocked = 0
    for face, points, normal in zip(mesh.faces, mesh.triangles, mesh.face_normals):
        attrs = dict(zip(("v1", "v2", "v3"), (str(int(v)) for v in face)))
        if name == "front-top":
            # Reapply the production v17 roof-side mask to the current
            # tessellation. Analytic faces can remesh after an unrelated cut;
            # matching triangle indices would omit some of the same surface.
            roof_side = (points[:, 2] >= 345.69).all() and (
                (points[:, 0] <= -100).all() or (points[:, 0] >= 100).all())
            if roof_side:
                attrs["paint_supports"] = "8"
                inherited += 1
        else:
            # The current production grip geometry. Curved show borders have
            # no supports; only the inset flat ceiling may receive an interface.
            c = points.mean(axis=0)
            in_grip = abs(c[0]) >= 91.7 and 22.19 <= c[1] <= 61.42 and 266.18 <= c[2] <= 278.21
            flat = np.max(np.abs(points[:, 2] - 272.1940001)) < 0.001
            inset = (np.abs(points[:, 0]) >= 92.55).all() and (np.abs(points[:, 0]) <= 100.7).all() \
                    and (points[:, 1] >= 34.9325).all() and (points[:, 1] <= 49.3325).all()
            if in_grip and normal[2] < -0.001 and not (flat and inset):
                attrs["paint_supports"] = grip_ceiling_paint(points) if flat else "8"
                grip_blocked += 1
        roof = np.max(np.abs(points[:, 2] - pocket["roof_z_mm"])) < 0.001 and normal[2] < -0.99
        inside = (points[:, 0] >= px-r-0.001).all() and (points[:, 0] <= px+r+0.001).all() \
                 and (points[:, 1] >= ymin-0.001).all() and (points[:, 1] <= ymax+0.001).all()
        if roof and inside:
            attrs["paint_supports"] = "8"
            blocked_roof += 1
        ET.SubElement(triangles, TAG("triangle"), **attrs)
    assert blocked_roof == 2, blocked_roof
    if name == "front-top":
        assert inherited > 30000, inherited
    else:
        assert grip_blocked > 1000
    config = ET.fromstring(front["Metadata/model_settings.config"])
    obj = config.find("object")
    part = obj.find("part")
    for item in obj.findall("metadata"):
        if item.get("key") == "name": item.set("value", f"enclosure-{name}-RC62")
    obj.find("metadata[@face_count]").set("face_count", str(len(mesh.faces)))
    for item in part.findall("metadata"):
        key = item.get("key")
        if key == "name": item.set("value", f"enclosure-{name}")
        if key == "source_file": item.set("value", f"enclosure-{name}.stl")
        if key.startswith("source_offset_"):
            item.set("value", str(center["xyz".index(key[-1])]))
    part.set("uuid", str(uuid.uuid5(uuid.NAMESPACE_URL, sha(ENC / f"enclosure-{name}.stl"))))
    part.find("mesh_stat").set("face_count", str(len(mesh.faces)))
    for item in config.findall("assemble/assemble_item"):
        if item.get("instance_id") is not None: item.set("transform", transform)
    for item in config.findall("plate/metadata"):
        if item.get("key") == "plater_name": item.set("value", f"enclosure-{name}: insert one RC62")
    roof_height = pocket["roof_z_mm"] - mesh.bounds[0, 2]
    # The slicer reads the contour at a layer's midplane. Pause immediately
    # before the first layer whose midplane reaches the roof, retaining the
    # highest fully printed open rim for seating the upright ring.
    pause_height = 0.2 + math.ceil((roof_height + 0.24/2 - 0.2) / 0.24) * 0.24
    message = ("Insert one RC62 upright into the centered pocket; attracting pole faces its mate. "
               "Seat it fully below both rims. Keep the tube passages clear. Resume manually after insertion.")
    pauses = ET.Element("custom_gcodes_per_layer")
    plate = ET.SubElement(pauses, "plate")
    ET.SubElement(plate, "plate_info", id="1")
    ET.SubElement(plate, "layer", top_z=f"{pause_height:.6f}", type="1", extruder="1",
                  color="", extra=message, gcode="M400 U1")
    ET.SubElement(plate, "mode", value="SingleExtruder")
    revised = {n: data for n, data in front.items() if not n.startswith("Metadata/plate_")}
    revised[SETTING] = json.dumps(selected).encode()
    revised["Metadata/filament_settings_1.config"] = base["Metadata/filament_settings_1.config"]
    revised["Metadata/layer_config_ranges.xml"] = base["Metadata/layer_config_ranges.xml"]
    for n, data in [("3D/3dmodel.model", model), (member, geometry),
                    ("Metadata/model_settings.config", config), ("Metadata/custom_gcode_per_layer.xml", pauses)]:
        revised[n] = ET.tostring(data, encoding="UTF-8", xml_declaration=True)
    project = HERE / f"{name}-pause.3mf"
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in revised.items(): z.writestr(n, data)
    return {"part": name, "printer": "Mark2" if name == "pump-cartridge" else "H2C",
            "project": str(project.relative_to(ROOT)), "project_sha256": sha(project),
            "source_stl_sha256": sha(ENC / f"enclosure-{name}.stl"),
            "source_step_sha256": sha(ENC / f"enclosure-{name}.step"),
            "machine_to_bed_translation_mm": [162.5-center[0], 160-center[1], -mesh.bounds[0, 2]],
            "requested_pause_height_mm": pause_height, "pocket_roof_height_mm": roof_height,
            "roof_support_blocked_facets": blocked_roof, "inherited_show_support_blocks": inherited,
            "grip_support_blocked_facets": grip_blocked,
            "baseline_project": str((PUMP_BASE if name == "pump-cartridge" else FRONT_BASE).relative_to(ROOT)),
            "baseline_project_sha256": sha(PUMP_BASE if name == "pump-cartridge" else FRONT_BASE)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slice", action="store_true")
    parser.add_argument("parts", nargs="*", choices=("pump-cartridge", "front-top"))
    args = parser.parse_args()
    geometry = json.loads((HERE / "geometry-check.json").read_text())
    assert geometry["geometry_checks_pass"]
    names = args.parts or ["pump-cartridge", "front-top"]
    record_path = HERE / "preparation.json"
    jobs = []
    if record_path.is_file():
        for row in json.loads(record_path.read_text())["jobs"]:
            if row["part"] not in names:
                assert sha(ROOT / row["project"]) == row["project_sha256"]
                assert sha(ENC / f"enclosure-{row['part']}.stl") == row["source_stl_sha256"]
                jobs.append(row)
    for name in names:
        record = prepare(name, geometry["pieces"][name])
        if args.slice:
            output = ROOT / ".cache/prints/cartridge-rc62-retention-v1" / name
            output.mkdir(parents=True, exist_ok=True)
            filename = f"enclosure-{name}-rc62-{record['printer'].lower()}-v1.gcode.3mf"
            command = [str(STUDIO), "--slice", "0", "--arrange", "0", "--orient", "0",
                       "--outputdir", str(output), "--export-3mf", filename, str(ROOT / record["project"])]
            print(f"Slicing {name}", flush=True)
            with (output / "slice.log").open("w") as log:
                subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True)
            record["native_archive"] = str((output / filename).relative_to(ROOT))
            record["native_archive_sha256"] = sha(output / filename)
            record["gcode_sha256"] = hashlib.sha256(members(output / filename)["Metadata/plate_1.gcode"]).hexdigest()
        jobs.append(record)
        (HERE / "preparation.json").write_text(json.dumps({"submitted": False, "jobs": jobs}, indent=2) + "\n")
    print(json.dumps({"submitted": False, "jobs": jobs}, indent=2), flush=True)


if __name__ == "__main__":
    main()
