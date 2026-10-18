"""Prepare and natively slice the four identification plates: chips, collars and DATA.

Usage: tools/cad-venv/bin/python hardware/printed-parts/drain-readiness/prepare.py labels
The output stays in .cache/prints/2026-10-07-drain. No printer job is submitted.
Each plate's fine closing layers land a layer top on every face-up chip and DATA face
and lettering top, read from the tessellated bodies; the localized PET-GF cooling of
cadlib/petgf_cooling.py applies to both filament slots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
JOB = ROOT / ".cache/prints/2026-10-07-drain"
SLICER = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _run_lock import acquire
acquire(str(Path(__file__)))
sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer
sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/trial-preparation"))
from _derive import closing_schedule

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def slice_project(project):
    out = project.parent / "ready"
    out.mkdir(exist_ok=True)
    cmd = [SLICER, "--slice", "0", "--arrange", "0", "--orient", "0",
           "--outputdir", str(out), "--export-3mf", project.stem + ".gcode.3mf", str(project)]
    save(project.parent / "slice-command.json", cmd)
    with (out / "slice.log").open("w") as stream:
        got = subprocess.run(cmd, cwd=out, stdout=stream, stderr=subprocess.STDOUT)
    if got.returncode:
        raise RuntimeError(f"Native slice failed ({got.returncode}): {out / 'slice.log'}")
    bounds = writer.object_toolpaths(out / "plate_1.gcode", out / "all-beads.gcode", None)
    low, high = np.array(bounds["extrusion_bounds_xy_mm"])
    margin = float(min(np.min(low - [25, 0]), np.min([325, 320] - high)))
    assert margin >= 80, (project.name, margin)
    save(project.parent / "native-review.json", {"full_bead_bounds": bounds,
         "minimum_shared_bed_margin_mm": margin,
         "native_archive_sha256": sha(out / (project.stem + ".gcode.3mf")),
         "support_policy": "No supports; face-up chips and flat-face-down collars."})
    print("Prepared", project, flush=True)


def labels(label_colours=None):
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/bulkhead-ring"))
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet/tube-collar"))
    import bulkhead_ring as ring
    import tube_collar as collar
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/data-ring"))
    import data_ring as data
    base = ROOT / "hardware/printed-parts/enclosure/nameplate/nameplate-001-petgf.3mf"
    registration_path = ROOT / "hardware/printed-parts/calibration/dual-nozzle-registration/mark2-registration.json"
    registration = json.loads(registration_path.read_text())
    assert registration["status"] == "nameplate_appearance_accepted"
    assert registration["native_extruder_offset"] == ["0x0", "0.5x-0.7"]
    groups = (("white", ["water", "drain"], ["#FFFFFF", "#000000"], 1, 2),
              ("blue", ["carb"], ["#FFFFFF", "#46A8F9"], 2, 1),
              ("red", ["co2"], ["#FFFFFF", "#F54749"], 2, 1),
              ("black", ["flavor-a", "flavor-b", "data"], ["#FFFFFF", "#000000"], 2, 1))
    for colour, stations, colours, body_tool, letter_tool in groups:
        if label_colours and colour not in label_colours:
            continue
        directory = JOB / ("labels-" + colour + "-mark2")
        p = directory / ("labels-" + colour + "-z004-mark2.3mf")
        with zipfile.ZipFile(base) as z:
            settings = json.loads(z.read(writer.SETTINGS_MEMBER))
            members = {n: z.read(n) for n in z.namelist() if n.startswith("Metadata/filament_settings_")}
        settings.update(extruder_offset=registration["native_extruder_offset"],
                        enable_support="0", brim_type="no_brim", brim_width="0",
                        initial_layer_print_height="0.2", layer_height="0.24", flush_into_support="0",
                        filament_colour=colours, filament_multi_colour=colours,
                        wipe_tower_x=["135", "135"], wipe_tower_y=["90", "90"])
        Q = writer.qn
        model = ET.Element(Q("model"), unit="millimeter")
        ET.SubElement(model, Q("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
        resources, build = ET.SubElement(model, Q("resources")), ET.SubElement(model, Q("build"))
        cfg, ranges = ET.Element("config"), ET.Element("objects")
        plate = ET.SubElement(cfg, "plate")
        for key, value in {"plater_id": 1, "plater_name": colour + " DRAIN identification; Mark2",
                           "locked": "false", "bed_type": settings["curr_bed_type"],
                           "filament_map_mode": "Manual", "filament_maps": "1 2", "filament_volume_maps": "0 0"}.items():
            writer.metadata(plate, key, value)
        details, tops, objects = [], [], []
        for station in stations:
            if station == "data":
                shapes = [("chip", [s.rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), 180)
                                    for s in (data.build_ring(), data.build_word())])]
            else:
                shapes = [("chip", [s.rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), 180)
                                 for s in (ring.build_ring(station), ring.build_word(station))]),
                      ("collar", [s.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, collar.RISE))
                                   for s in (collar.build_collar(station), collar.build_word(station))])]
            for kind, pair in shapes:
                index = len(details)
                bb = pair[0].BoundingBox()
                shift = (-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, 0)
                children, heights = [], []
                for label, shape, tool in zip(("body", "word"), pair, (body_tool, letter_tool)):
                    shape = shape.translate(shift)
                    vs, fs = shape.tessellate(.015, .05)
                    mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vs], faces=fs, process=True)
                    volume = mesh.volume
                    if not mesh.is_watertight:
                        mesh.update_faces(mesh.nondegenerate_faces())
                        mesh.remove_unreferenced_vertices()
                        mesh.merge_vertices(digits_vertex=5)
                        mesh.fix_normals(multibody=True)
                        assert abs(mesh.volume - volume) < .01
                    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0, (station, kind, label)
                    heights.append((float(mesh.bounds[0][2]), float(mesh.bounds[1][2])))
                    stl = directory / "geometry" / f"{station}-{kind}-{label}.stl"
                    stl.parent.mkdir(parents=True, exist_ok=True)
                    mesh.export(stl)
                    oid = len(resources) + 1
                    obj = ET.SubElement(resources, Q("object"), id=str(oid), type="model")
                    geom = ET.SubElement(obj, Q("mesh"))
                    vertices, triangles = ET.SubElement(geom, Q("vertices")), ET.SubElement(geom, Q("triangles"))
                    for v in mesh.vertices:
                        ET.SubElement(vertices, Q("vertex"), **dict(zip("xyz", map(str, v))))
                    for f in mesh.faces:
                        ET.SubElement(triangles, Q("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, f))))
                    children.append((oid, label, tool))
                oid = len(resources) + 1
                obj = ET.SubElement(resources, Q("object"), id=str(oid), type="model")
                comp = ET.SubElement(obj, Q("components"))
                config = ET.SubElement(cfg, "object", id=str(oid))
                writer.metadata(config, "name", f"{station}-{kind}")
                writer.metadata(config, "extruder", body_tool)
                for child, label, tool in children:
                    ET.SubElement(comp, Q("component"), objectid=str(child))
                    item = ET.SubElement(config, "part", id=str(child), subtype="normal_part")
                    for key, value in {"name": label, "extruder": tool,
                                       "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"}.items():
                        writer.metadata(item, key, value)
                position = (150 + (index % 2) * 50, 145 + (index // 2) * 35)
                ET.SubElement(build, Q("item"), objectid=str(oid), transform=f"1 0 0 0 1 0 0 0 1 {position[0]} {position[1]} 0", printable="1")
                instance = ET.SubElement(plate, "model_instance")
                for key, value in {"object_id": oid, "instance_id": 0, "identify_id": 2901 + index}.items():
                    writer.metadata(instance, key, value)
                floor = min(low for low, _ in heights)
                if kind == "chip":
                    tops.extend(round(high - floor, 4) for _, high in heights)
                objects.append(index + 1)
                details.append({"station": station, "kind": kind, "body_filament": body_tool,
                                "word_filament": letter_tool, "position_xy_mm": position,
                                "face_up_tops_mm": [round(high - floor, 4) for _, high in heights] if kind == "chip" else None})
        # A multi-material prime tower requires one shared layer schedule.
        bands = closing_schedule(tops)
        for number in objects:
            object_ranges = ET.SubElement(ranges, "object", id=str(number))
            for low, high, height in bands:
                band = ET.SubElement(object_ranges, "range", min_z=f"{low:g}", max_z=f"{high:g}")
                ET.SubElement(band, "option", opt_key="layer_height").text = f"{height:g}"
        members.update({"3D/3dmodel.model": writer.xml(model),
                        "Metadata/model_settings.config": writer.xml(cfg),
                        "Metadata/layer_config_ranges.xml": writer.xml(ranges),
                        writer.SETTINGS_MEMBER: json.dumps(settings, indent=2).encode(),
                        "_rels/.rels": b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
                        "[Content_Types].xml": b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'})
        cooling = writer.petgf_cooling.apply_members(members)
        writer.archive_write(p, members)
        save(directory / "preparation.json", {"project_sha256": sha(p), "parts": details,
             "closing_layer_ranges_mm": bands, "face_up_tops_mm": sorted(set(tops)),
             "cooling_changes": cooling,
             "source_sha256": {str(f.relative_to(ROOT)): sha(f) for f in (base, registration_path, Path(ring.__file__), Path(ring.port_chip.__file__), Path(collar.__file__), Path(data.__file__), Path(data.interface.__file__), Path(data.interface.nameplate.__file__), Path(data.interface.nameplate.dimensions.__file__), Path(__file__))},
             "extruder_offset": settings["extruder_offset"], "z_trim_mm": .04,
             "first_layer_mm": .20, "normal_layer_mm": .24})
        slice_project(p)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("jobs", nargs="*", choices=("labels",))
    ap.add_argument("--label-colour", action="append", choices=("white", "blue", "red", "black"),
                    help="Prepare only the selected identification plate(s).")
    args = ap.parse_args()
    labels(args.label_colour)
