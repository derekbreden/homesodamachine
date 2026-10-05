"""Prepare immutable enclosure layer-policy revisions; no printer control.

Run one part at a time. Preparation retains the current frozen exports and the
production grip support lanes. Native slicing is a separate explicit step.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
PUMP_BASE = ENC / "magnet-retention/v4/pump-cartridge-cap-pause.3mf"
PUMP_RECORD = ENC / "magnet-retention/v4/preparation.json"
HOST_RECORD = ENC / "heat-set-review/print-regions.json"
JOBS = {
    "pump-cartridge-cap": {
        "stem": "2026-10-04-pump-cartridge-cap-normal-transition-mark2-v5",
        "printer": "Mark2", "trim": .04, "revision": 5,
    },
    "front-bottom": {
        "stem": "2026-10-04-enclosure-front-bottom-normal-grip-h2c-v6",
        "printer": "H2C", "trim": .18, "revision": 6,
    },
    "back-bottom": {
        "stem": "2026-10-04-enclosure-back-bottom-normal-grip-mark2-v6",
        "printer": "Mark2", "trim": .04, "revision": 6,
    },
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def archive_members(path):
    with zipfile.ZipFile(path) as source:
        assert source.testzip() is None
        return {name: source.read(name) for name in source.namelist()}


def write_archive(path, members):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for name, payload in sorted(members.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            target.writestr(entry, payload, compresslevel=6)
    temporary.replace(path)


def prepare_pump(project):
    baseline = json.loads(PUMP_RECORD.read_text())["jobs"][0]
    assert sha(PUMP_BASE) == baseline["project_sha256"]
    for component in baseline["components"]:
        for suffix in ("stl", "step"):
            path = ENC / f'enclosure-{component["part"]}.{suffix}'
            assert sha(path) == component[f"source_{suffix}_sha256"], path
    members = archive_members(PUMP_BASE)
    before = {name: hashlib.sha256(payload).hexdigest() for name, payload in members.items()}
    band_member = "Metadata/layer_config_ranges.xml"
    bands = ET.fromstring(members[band_member])
    objects = bands.findall("object")
    assert len(objects) == 1 and objects[0].get("id") == "1"
    ranges = objects[0].findall("range")
    actual = [(float(r.get("min_z")), float(r.get("max_z")),
               {o.get("opt_key"): o.text for o in r}) for r in ranges]
    assert actual == [(6., 18.4, {"layer_height": "0.08"}),
                      (100.3, 113.2, {"layer_height": "0.08", "wall_loops": "6"})], actual
    ranges[1].find('option[@opt_key="layer_height"]').text = "0.24"
    members[band_member] = ET.tostring(bands, encoding="utf-8", xml_declaration=True)
    settings = json.loads(members["Metadata/project_settings.config"])
    assert settings["layer_height"] == "0.24"
    assert settings["initial_layer_print_height"] == "0.2"
    write_archive(project, members)
    changed = [name for name, payload in members.items()
               if hashlib.sha256(payload).hexdigest() != before[name]]
    assert changed == [band_member], changed
    return {
        "baseline_project": relative(PUMP_BASE), "baseline_project_sha256": sha(PUMP_BASE),
        "baseline_preparation": relative(PUMP_RECORD), "baseline_preparation_sha256": sha(PUMP_RECORD),
        "components": copy.deepcopy(baseline["components"]),
        "settings_sha256": hashlib.sha256(members["Metadata/project_settings.config"]).hexdigest(),
        "changed_project_members": changed,
        "unchanged_project_member_sha256": {name: digest for name, digest in before.items() if name not in changed},
        "layer_ranges_mm": [
            {"object_index": 1, "min_z": 6., "max_z": 18.4, "layer_height": .08,
             "reason": "Real inward/top lower hand-pocket rim."},
            {"object_index": 1, "min_z": 100.3, "max_z": 113.2,
             "layer_height": .24, "wall_loops": 6,
             "reason": "Additive expanding upper hand-pocket chamfer/taper."},
        ],
        "requested_pause_height_mm": baseline["requested_pause_height_mm"],
        "magnet_count_to_insert": 1, "magnet_model": "K&J RC62",
        "source_sha256": {relative(p): sha(p) for p in (PUMP_BASE, PUMP_RECORD, HOST_RECORD,
            ENC / "enclosure.py", ENC / "_cartridge_retention.py",
            ENC / "enclosure-pump-cartridge.stl", ENC / "enclosure-pump-cartridge.step",
            ENC / "enclosure-pump-cap.stl", ENC / "enclosure-pump-cap.step")},
    }


def prepare_bottom(part, project, directory, trim):
    # These imports construct no geometry exports. They provide the same current
    # grip datums, native mesh writer and declared solid-host boxes as production.
    sys.path[:0] = [str(ENC), str(ROOT / "hardware/printed-parts/faucet")]
    import enclosure as shell
    import refresh_print_project as writer
    import numpy as np
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union

    shared_path = ENC / "support-bottom-gap/prepare_prints.py"
    spec = importlib.util.spec_from_file_location("frozen_host_preparation", shared_path)
    shared = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shared)
    name = f"enclosure-{part}"
    source = ENC / f"{name}.stl"
    report = writer.refresh(PROFILE, project, parts=((name, source, 0.),),
                            offsets=((0., 0.),), z_trim=trim,
                            title=f"{part}: ordinary additive grip transition")
    members = archive_members(project)
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(layer_height="0.24", initial_layer_print_height="0.2",
                    support_filament="1", support_interface_filament="1", flush_into_support="0")
    assert settings["support_type"] == "tree(auto)"
    assert settings["wall_sequence"] == "inner wall/outer wall"
    assert settings["infill_wall_overlap"] == "15%" and settings["is_infill_first"] == "0"
    members[writer.SETTINGS_MEMBER] = json.dumps(settings, indent=2).encode()
    ranges = ET.Element("objects")
    obj = ET.SubElement(ranges, "object", id="1")
    band = ET.SubElement(obj, "range", min_z="35.0", max_z="41.5")
    ET.SubElement(band, "option", opt_key="layer_height").text = "0.24"
    ET.SubElement(band, "option", opt_key="wall_loops").text = "6"
    members["Metadata/layer_config_ranges.xml"] = writer.xml(ranges)

    item, = report["parts"]
    document = ET.fromstring(members[item["member"]])
    vertices = np.array([[float(v.get(a)) for a in "xyz"]
                         for v in document.iter(writer.qn("vertex"))]) + item["source_center_mm"]
    triangles = list(document.iter(writer.qn("triangle")))
    points = vertices[np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")]
                               for t in triangles])]
    normals = np.cross(points[:, 1]-points[:, 0], points[:, 2]-points[:, 0])
    nz = normals[:, 2]/np.maximum(np.linalg.norm(normals, axis=1), 1e-30)
    grip = shell.grip_interface()
    roof = grip.ROOF
    piece = part.split("-", 1)[0]
    mouth = shell._handhold_y()[0 if piece == "front" else 1]
    ymin, ymax = ((mouth-shell.handhold_wall-.01, mouth+.01) if piece == "front"
                  else (mouth-.01, mouth+shell.handhold_wall+.01))
    half = grip.WING_SPAN/2+grip.WING_END_AIR
    slots = [box(side*grip.X_CENTER-half-.001, ymin,
                 side*grip.X_CENTER+half+.001, ymax) for side in (-1, 1)]
    blocked = unary_union(slots)
    flat = ((np.max(np.abs(points[:, :, 2]-roof), axis=1) < .0001) & (nz < -.99)
        & (np.min(np.abs(points[:, :, 0]), axis=1) >= grip.INNER_FACE-shell.handhold_wall-.001)
        & (np.min(points[:, :, 1], axis=1) >= shell._handhold_y()[0]-shell.handhold_wall-.12)
        & (np.max(points[:, :, 1], axis=1) <= shell._handhold_y()[1]+shell.handhold_wall+.12))
    exterior = ((np.min(np.abs(points[:, :, 0]), axis=1) >= grip.INNER_FACE-.001)
        & (np.min(points[:, :, 1], axis=1) >= shell._handhold_y()[0]-shell.handhold_corner_r-.01)
        & (np.max(points[:, :, 1], axis=1) <= shell._handhold_y()[1]+shell.handhold_corner_r+.01)
        & (np.min(points[:, :, 2], axis=1) >= roof-shell.handhold_edge_r-.01)
        & (np.max(points[:, :, 2], axis=1) <= roof+shell.handhold_edge_r+3.05)
        & (nz < -.00001) & ~flat)
    assert flat.sum() > 0 and exterior.sum() > 0
    flat_area = unary_union([Polygon(p[:, :2]) for p in points[flat]])
    halo = 1.0
    permitted = flat_area.buffer(-.8).difference(blocked.buffer(halo, join_style=2))
    blocked_area = slot_area = 0.

    def encode(p, depth=0):
        nonlocal blocked_area, slot_area
        polygon = Polygon(p[:, :2])
        if permitted.covers(polygon):
            return "0"
        if not permitted.intersects(polygon) or depth == 10:
            blocked_area += polygon.area
            slot_area += polygon.intersection(blocked).area
            return "8"
        a, b, c = p
        ab, bc, ca = (a+b)/2, (b+c)/2, (c+a)/2
        return "".join(encode(np.array(q), depth+1)
                       for q in ((a, ab, ca), (ab, b, bc), (bc, c, ca), (ab, bc, ca)))+"3"

    for triangle, pts, isflat, isexterior in zip(triangles, points, flat, exterior):
        if isexterior:
            triangle.set("paint_supports", "8")
        elif isflat:
            triangle.set("paint_supports", encode(pts))
    assert 30 < slot_area < 35, (slot_area, blocked_area)
    members[item["member"]] = writer.xml(document)
    np.savez_compressed(directory / "support-review-geometry.npz", exterior_triangles=points[exterior])
    model = ET.fromstring(members["3D/3dmodel.model"])
    config = ET.fromstring(members["Metadata/model_settings.config"])
    source_bounds = np.array([vertices.min(axis=0), vertices.max(axis=0)])
    hosts, host_digest = shared.add_solid_hosts(members, model, config, part,
                                                np.array(item["source_center_mm"]), source_bounds)
    members["3D/3dmodel.model"] = writer.xml(model)
    members["Metadata/model_settings.config"] = writer.xml(config)
    write_archive(project, members)
    report.update(
        piece=piece, settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
        slot_bounds_cad_xy_mm=[list(s.bounds) for s in slots], slot_roof_cad_z_mm=roof,
        slot_floor_cad_z_mm=grip.BACK-grip.WING_THICK-grip.BEARING_AIR,
        support_review_geometry_sha256=sha(directory / "support-review-geometry.npz"),
        blocked_slot_area_mm2=slot_area, blocked_ceiling_edge_area_mm2=blocked_area-slot_area,
        painted_exterior_triangles=int(exterior.sum()), painted_flat_triangles=int(flat.sum()),
        six_wall_print_z_mm=[35., 41.5], fine_flute_runout_print_z_mm=None,
        layer_ranges_mm=[dict(object_index=1, min_z=35., max_z=41.5, layer_height=.24,
                              wall_loops=6, reason="Additive expanding upper handhold transition.")],
        flat_ceiling_support_inset_mm=.8, slot_support_halo_mm=halo,
        solid_host_regions=hosts, solid_host_region_record_sha256=host_digest,
        source_sha256={relative(p): sha(p) for p in (PROFILE, source,
            ENC / f"{name}.step", ENC / "_grip_interface.py", ENC / "enclosure.py",
            ENC / "_enclosure_interface.py", ROOT / "hardware/printed-parts/cadlib/overhang_round.py",
            ROOT / "hardware/printed-parts/cadlib/flute_skin.py", HOST_RECORD, shared_path,
            ROOT / "hardware/printed-parts/enclosure/bottom-grip-print/prepare.py")},
    )
    return report


def prepare(part):
    target = JOBS[part]
    directory = ROOT / ".cache/prints" / target["stem"]
    if directory.exists():
        raise FileExistsError("Revision directory already exists; frozen preparations are not overwritten.")
    directory.mkdir(parents=True)
    project = directory / (target["stem"] + "-input.3mf")
    if part == "pump-cartridge-cap":
        report = prepare_pump(project)
    else:
        report = prepare_bottom(part, project, directory, target["trim"])
    report.update(schema_version=1, part=part, revision=target["revision"],
                  printer=target["printer"], stem=target["stem"], project=project.name,
                  project_path=relative(project), project_sha256=sha(project),
                  requested_trim_mm=target["trim"], preparation_script_sha256=sha(__file__),
                  geometry_exports_changed=False, submitted=False,
                  physical_surface_qualification=False,
                  launch_state="queued_awaiting_printer_availability_and_fresh_preflight")
    write_json(directory / "preparation.json", report)
    public = HERE / part
    public.mkdir(exist_ok=True)
    write_json(public / "preparation.json", report)
    print(json.dumps({"part": part, "project": relative(project), "project_sha256": sha(project)}), flush=True)
    return project


def slice_part(part):
    target = JOBS[part]
    directory = ROOT / ".cache/prints" / target["stem"]
    prep = json.loads((directory / "preparation.json").read_text())
    project = directory / prep["project"]
    assert sha(project) == prep["project_sha256"]
    assert sha(__file__) == prep["preparation_script_sha256"]
    for name, digest in prep["source_sha256"].items():
        assert sha(ROOT / name) == digest, name
    ready = directory / "ready"
    if ready.exists():
        raise FileExistsError("Native output already exists; use a fresh revision after a failure.")
    ready.mkdir()
    command = [STUDIO, "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(ready), "--export-3mf", target["stem"] + ".gcode.3mf", str(project)]
    write_json(directory / "slice-command.json", command)
    with (ready / "slice.log").open("w") as log:
        result = subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT)
    print(json.dumps({"part": part, "slice_exit": result.returncode, "ready": relative(ready)}), flush=True)
    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=tuple(JOBS))
    parser.add_argument("--slice", action="store_true", help="Slice an already prepared revision.")
    args = parser.parse_args()
    if args.slice:
        raise SystemExit(slice_part(args.part))
    prepare(args.part)
