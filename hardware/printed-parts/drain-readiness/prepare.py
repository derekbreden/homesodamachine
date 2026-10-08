"""Prepare and natively slice the dedicated DRAIN production print set.

Usage: tools/cad-venv/bin/python hardware/printed-parts/drain-readiness/prepare.py
The output stays in .cache/prints/2026-10-07-drain. No printer job is submitted.
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

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def slice_project(project, report=None):
    out = project.parent / "ready"
    out.mkdir(exist_ok=True)
    cmd = [SLICER, "--slice", "0", "--arrange", "0", "--orient", "0",
           "--outputdir", str(out), "--export-3mf", project.stem + ".gcode.3mf", str(project)]
    save(project.parent / "slice-command.json", cmd)
    with (out / "slice.log").open("w") as stream:
        got = subprocess.run(cmd, cwd=out, stdout=stream, stderr=subprocess.STDOUT)
    if got.returncode:
        raise RuntimeError(f"Native slice failed ({got.returncode}): {out / 'slice.log'}")
    if report:
        audit = writer.slice_review(project, report, out)
        save(project.parent / "native-review.json", audit)
    else:
        bounds = writer.object_toolpaths(out / "plate_1.gcode", out / "all-beads.gcode", None)
        low, high = np.array(bounds["extrusion_bounds_xy_mm"])
        margin = float(min(np.min(low - [25, 0]), np.min([325, 320] - high)))
        assert margin >= 80, (project.name, margin)
        save(project.parent / "native-review.json", {"full_bead_bounds": bounds,
             "minimum_shared_bed_margin_mm": margin,
             "native_archive_sha256": sha(out / (project.stem + ".gcode.3mf")),
             "support_policy": "No supports; face-up chips and flat-face-down collars."})
    print("Prepared", project, flush=True)


def back_top():
    source = HERE / "profiles/back-top-mark2.3mf"
    part = ROOT / "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.stl"
    p = JOB / "back-top-mark2/back-top-black-z004-mark2.3mf"
    report = writer.refresh(source, p, parts=(("enclosure-back-top", part, 180.),),
                            offsets=((0., 0.),), title="Three-row DRAIN rear wall; Mark2", plate_border=20)
    with zipfile.ZipFile(p) as z:
        members = {n: z.read(n) for n in z.namelist()}
    row = report["parts"][0]
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings["support_type"] = "normal(auto)"
    settings["support_style"] = "default"
    # Complete insert hosts/root stock need the locally proven wall envelope.
    # Ordinary stock retains two walls; the roof transition retains its local six.
    settings["wall_loops"] = "2"
    settings["detect_narrow_internal_solid_infill"] = "0"
    settings["minimum_sparse_infill_area"] = "15"
    settings["top_one_wall_type"] = "not apply"
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    # Roof-down print, with a 90-degree bed yaw to center the full footprint.
    transform = np.array(row["build_transform"][:9]).reshape(3, 3)
    yaw = np.array([[0., 1., 0.], [-1., 0., 0.], [0., 0., 1.]])
    transform = transform @ yaw
    row["build_transform"][:9] = transform.reshape(-1).tolist()
    model = ET.fromstring(members["3D/3dmodel.model"])
    model.find(writer.qn("build"))[0].set("transform", " ".join(map(str, row["build_transform"])))
    members["3D/3dmodel.model"] = writer.xml(model)
    cfg = ET.fromstring(members["Metadata/model_settings.config"])
    for item in cfg.findall("./assemble/assemble_item"):
        if item.get("instance_id") == "0":
            item.set("transform", " ".join(map(str, row["build_transform"])))
    members["Metadata/model_settings.config"] = writer.xml(cfg)
    # Preserve the supported exterior-transition rule from the production archive.
    geometry = ET.fromstring(members[row["member"]])
    vertices = np.array([[float(v.get(k)) for k in "xyz"] for v in geometry.findall(".//" + writer.qn("vertex"))])
    world = vertices + row["source_center_mm"]
    count = 0
    for triangle in geometry.findall(".//" + writer.qn("triangle")):
        face = world[[int(triangle.get(k)) for k in ("v1", "v2", "v3")]]
        if np.min(face[:, 2]) >= 345.69 and (np.min(face[:, 0]) >= 100 or np.max(face[:, 0]) <= -100):
            triangle.set("paint_supports", "8")
            count += 1
    members[row["member"]] = writer.xml(geometry)
    with zipfile.ZipFile(source) as z:
        members["Metadata/layer_config_ranges.xml"] = z.read("Metadata/layer_config_ranges.xml")
    # Complete insert hosts, caps, seam ligaments and roots receive solid infill.
    # Modifier bounds are in the same machine frame as the unmodified STL.
    region_path = ROOT / "hardware/printed-parts/enclosure/enclosure/heat-set-review/print-regions.json"
    regions = json.loads(region_path.read_text())["pieces"]["back-top"]
    components = model.find(".//" + writer.qn("components"))
    owner = cfg.find("object")
    relations = ET.fromstring(members["3D/_rels/3dmodel.model.rels"])
    low, high = world.min(axis=0), world.max(axis=0)
    modifiers = []
    for index, region in enumerate(regions, 3):
        bounds = np.array(region["machine_bounds_mm"]).reshape(3, 2)
        bounds[:, 0] = np.maximum(bounds[:, 0], low + .001)
        bounds[:, 1] = np.minimum(bounds[:, 1], high - .001)
        assert np.all(bounds[:, 1] > bounds[:, 0]), region
        box = trimesh.creation.box(extents=bounds[:, 1] - bounds[:, 0])
        box.apply_translation(bounds.mean(axis=1) - row["source_center_mm"])
        document = ET.Element(writer.qn("model"), unit="millimeter")
        resources = ET.SubElement(document, writer.qn("resources"))
        solid = ET.SubElement(resources, writer.qn("object"), id=str(index), type="model")
        geom = ET.SubElement(solid, writer.qn("mesh"))
        verts, tris = ET.SubElement(geom, writer.qn("vertices")), ET.SubElement(geom, writer.qn("triangles"))
        for v in box.vertices:
            ET.SubElement(verts, writer.qn("vertex"), **dict(zip("xyz", map(str, v))))
        for f in box.faces:
            ET.SubElement(tris, writer.qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, f))))
        member = f"3D/Objects/solid-host-{index}.model"
        members[member] = writer.xml(document)
        ET.SubElement(components, writer.qn("component"), objectid=str(index),
                      transform="1 0 0 0 1 0 0 0 1 0 0 0", **{f"{{{writer.PROD}}}path": "/" + member})
        part_cfg = ET.SubElement(owner, "part", id=str(index), subtype="modifier_part")
        for k, value in {"name": region["name"], "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                         "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag",
                         "wall_loops": "10"}.items():
            writer.metadata(part_cfg, k, value)
        ET.SubElement(relations, f"{{{writer.REL}}}Relationship", Target="/" + member,
                      Type=next(iter(relations)).get("Type"), Id=f"solid-host-{index}")
        modifiers.append({**region, "applied_machine_bounds_mm": bounds.flatten().tolist()})
    members["3D/3dmodel.model"] = writer.xml(model)
    members["Metadata/model_settings.config"] = writer.xml(cfg)
    members["3D/_rels/3dmodel.model.rels"] = writer.xml(relations).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    writer.archive_write(p, members)
    row["plate_translation_mm"] = row["build_transform"][9:]
    row["rotation_z_degrees"] = 90.
    placed = vertices @ transform + np.array(row["build_transform"][9:])
    row["plate_bounds_mm"] = [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()]
    report.update(project_sha256=sha(p),
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  printer="Mark2", show_support_blocked_faces=count,
                  solid_host_regions=modifiers, solid_host_region_source_sha256=sha(region_path),
                  support_type="normal(auto)",
                  wall_loops=2, solid_host_wall_loops=10,
                  detect_narrow_internal_solid_infill="0", top_one_wall_type="not apply",
                  support_reason="Vertical support columns keep the full model/support/brim footprint within the 20 mm bed margin.")
    save(p.with_suffix(".preparation.json"), report)
    slice_project(p, report)


def labels():
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
        details = []
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
                children = []
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
                # A multi-material prime tower requires one shared layer schedule.
                # DATA nose closure applies to all five black-plate objects.
                bands = ([("1.40", "1.68", "0.14"), ("1.92", "2.0", "0.08"),
                          ("3.20", "3.36", "0.08")] if colour == "black"
                         else [("1.88", "2.0", "0.12")])
                object_ranges = ET.SubElement(ranges, "object", id=str(index + 1))
                for low, high, height in bands:
                    band = ET.SubElement(object_ranges, "range", min_z=low, max_z=high)
                    ET.SubElement(band, "option", opt_key="layer_height").text = height
                details.append({"station": station, "kind": kind, "body_filament": body_tool,
                                "word_filament": letter_tool, "position_xy_mm": position})
        members.update({"3D/3dmodel.model": writer.xml(model),
                        "Metadata/model_settings.config": writer.xml(cfg),
                        "Metadata/layer_config_ranges.xml": writer.xml(ranges),
                        writer.SETTINGS_MEMBER: json.dumps(settings, indent=2).encode(),
                        "_rels/.rels": b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
                        "[Content_Types].xml": b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'})
        writer.archive_write(p, members)
        save(directory / "preparation.json", {"project_sha256": sha(p), "parts": details,
             "source_sha256": {str(f.relative_to(ROOT)): sha(f) for f in (base, registration_path, Path(ring.__file__), Path(ring.port_chip.__file__), Path(collar.__file__), Path(data.__file__), Path(data.interface.__file__), Path(__file__))},
             "extruder_offset": settings["extruder_offset"], "z_trim_mm": .04,
             "first_layer_mm": .20, "normal_layer_mm": .24})
        slice_project(p)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("jobs", nargs="*", choices=("back-top", "labels"))
    args = ap.parse_args()
    actions = {"back-top": back_top, "labels": labels}
    for name in args.jobs or actions:
        actions[name]()
