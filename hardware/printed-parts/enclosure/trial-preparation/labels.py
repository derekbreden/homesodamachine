#!/usr/bin/env python3
"""Prepare and natively slice the identification plates: rear chips, tube collars, DATA, nameplate.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/labels.py [--colour white] [--slice]

Four two-colour PET-GF plates on Mark2, one per chip colour. They carry the six compact rear
chips (`enclosure/rear-identification/`), the six tube collars (`faucet/tube-collar/`), the
DATA plate (`enclosure/data-ring/`) and the serial nameplate (`enclosure/nameplate/`). Each
part is read from its published STEP, split into its body and its lettering, and posed face
up. The chips, the DATA plate and the nameplate lie on their flat backs (`nameplate.print_pose`).
The collars lie on their flat faces.

The recipe is `petgf.3mf` on both 0.4 mm nozzles with Mark2's +0.04 mm Z trim. White PET-GF is
on the left nozzle, and the plate's colour is on the right. The right nozzle's registration
offset comes from `calibration/dual-nozzle-registration/mark2-registration.json`. There are no
supports and no brim. One shared layer schedule (`_derive.closing_schedule`) puts a layer top
on every face-up chip face and lettering top, because the prime tower needs one schedule.

A run writes `.cache/prints/trial/<date>-labels-<colour>-mark2-<digest>/`: the project, the
body and lettering meshes, `preparation.json`, and with `--slice` the archive and
`review.json`. No printer is contacted.
"""
from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path[:0] = [str(HERE), str(ROOT / "hardware/scripts"), str(ROOT / "hardware/printed-parts/cadlib"),
                str(ROOT / "hardware/printed-parts/enclosure/nameplate")]
from _run_lock import acquire  # noqa: E402

acquire(str(Path(__file__)))
import _derive  # noqa: E402
import _native  # noqa: E402
import review as reader  # noqa: E402

HP = ROOT / "hardware/printed-parts"
PROFILE = HP / "petgf.3mf"
REGISTRATION = HP / "calibration/dual-nozzle-registration/mark2-registration.json"
OUTPUT = ROOT / ".cache/prints/trial"
STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
Z_TRIM = 0.04
BORDER = 20.0
GAP = 8.0
#: One plate per chip colour. Filament 1 is the left nozzle's white; filament 2 the right's colour.
GROUPS = {
    "white": {"colours": ["#FFFFFF", "#000000"], "body": 1, "word": 2,
              "parts": ["chip:water", "chip:drain", "collar:water", "collar:drain"]},
    "blue": {"colours": ["#FFFFFF", "#46A8F9"], "body": 2, "word": 1, "parts": ["chip:carb", "collar:carb"]},
    "red": {"colours": ["#FFFFFF", "#F54749"], "body": 2, "word": 1, "parts": ["chip:co2", "collar:co2"]},
    "black": {"colours": ["#FFFFFF", "#000000"], "body": 2, "word": 1,
              "parts": ["chip:flavor-a", "chip:flavor-b", "collar:flavor-a", "collar:flavor-b", "data", "nameplate"]},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return Path(path).resolve().relative_to(ROOT).as_posix()


def source(part: str) -> tuple[Path, str]:
    kind, _, which = part.partition(":")
    return {"chip": (HP / f"enclosure/rear-identification/rear-label-{which}.step", "back"),
            "collar": (HP / f"faucet/tube-collar/tube-collar-{which}.step", "face"),
            "data": (HP / "enclosure/data-ring/data-ring.step", "back"),
            "nameplate": (HP / "enclosure/nameplate/nameplate-001.step", "back")}[kind]


def bodies(step: Path, bed: str):
    """The part's body and its lettering, posed face up and centred on the plate origin."""
    import cadquery as cq
    from _cadq_export import import_assembly
    solids = [s for shape, _ in import_assembly(step).values() for s in shape.Solids()]
    solids.sort(key=lambda s: -s.Volume())
    body, letters = solids[0], solids[1:]
    if not letters:
        raise ValueError(f"{relative(step)} has no lettering body")
    word = letters[0] if len(letters) == 1 else cq.Compound.makeCompound(letters)

    def pose(shape):
        if bed == "back":       # the flat Y0 back on the bed, +Y up (`nameplate.print_pose`)
            return shape.rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), 180)
        return shape.rotate((0, 0, 0), (1, 0, 0), 180)  # the collar's flat face on the bed
    body, word = pose(body), pose(word)
    bb = body.BoundingBox()
    shift = cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin)
    return body.translate(shift), word.translate(shift)


def two_hotend_settings(colours: list[str]) -> tuple[dict, dict, dict]:
    """`petgf.3mf` with its filament arrays doubled onto both nozzles, as the nameplate's preparer does."""
    profile = _native.profile_settings(PROFILE, Z_TRIM)
    settings = copy.deepcopy(profile["settings"])
    original = copy.deepcopy(settings)
    variants = len(original["filament_extruder_variant"])
    for key, value in list(settings.items()):
        if isinstance(value, list) and len(value) in (1, variants):
            settings[key] = value * 2
    registration = json.loads(REGISTRATION.read_text())
    if registration["status"] != "nameplate_appearance_accepted":
        raise ValueError(f"{relative(REGISTRATION)} status is {registration['status']}")
    settings.update(
        filament_colour=colours, filament_multi_colour=colours, filament_map=["1", "2"],
        filament_map_2=["1", "2"], filament_nozzle_map=["0", "1"], filament_map_mode="Manual",
        filament_volume_map=["0", "0"], filament_self_index=["1"] * variants + ["2"] * variants,
        filament_printable=["3", "3"], extruder_ams_count=["1#0|4#0", "1#0|4#0"],
        filament_prime_volume=["45", "45"], flush_volumes_vector=["140"] * 4,
        flush_volumes_matrix=["0", "140", "140", "0"] * 2,
        extruder_offset=registration["native_extruder_offset"], enable_support="0",
        brim_type="no_brim", brim_width="0", initial_layer_print_height="0.2", layer_height="0.24",
        flush_into_support="0", wipe_tower_x=["135", "135"], wipe_tower_y=["90", "90"])
    members = {k: v for k, v in profile["members"].items() if k.startswith("Metadata/filament_settings_")}
    filament = json.loads(members.pop("Metadata/filament_settings_1.config"))
    filament["filament_printable"] = ["3"]
    members["Metadata/filament_settings_1.config"] = members["Metadata/filament_settings_2.config"] = \
        json.dumps(filament, indent=2).encode()
    changes = {k: {"from": original.get(k), "to": v} for k, v in settings.items() if original.get(k) != v}
    return settings, members, {"profile_changes": profile["changes"], "two_hotend_changes": changes,
                               "registration": relative(REGISTRATION), "registration_sha256": sha256(REGISTRATION)}


def layout(footprints: list[tuple[float, float]], centre) -> list[tuple[float, float]]:
    """Rows of parts, widest first, centred on the shared printable area."""
    order = sorted(range(len(footprints)), key=lambda i: -footprints[i][0])
    rows, row, width = [], [], 0.0
    for i in order:
        dx = footprints[i][0]
        if row and width + GAP + dx > 130.0:
            rows.append(row)
            row, width = [], 0.0
        width += (GAP if row else 0.0) + dx
        row.append(i)
    rows.append(row)
    depth = sum(max(footprints[i][1] for i in r) for r in rows) + GAP * (len(rows) - 1)
    placed, y = {}, centre[1] + depth / 2
    for r in rows:
        row_depth = max(footprints[i][1] for i in r)
        row_width = sum(footprints[i][0] for i in r) + GAP * (len(r) - 1)
        x = centre[0] - row_width / 2
        for i in r:
            placed[i] = (x + footprints[i][0] / 2, y - row_depth / 2)
            x += footprints[i][0] + GAP
        y -= row_depth + GAP
    return [placed[i] for i in range(len(footprints))]


def prepare(colour: str) -> Path:
    from print_mesh import print_mesh
    group = GROUPS[colour]
    settings, filament_members, recipe = two_hotend_settings(group["colours"])
    low_area = np.max([[25.0, 0.0], [0.0, 0.0]], axis=0)
    high_area = np.array([325.0, 320.0])
    centre = (low_area + high_area) / 2
    parts, sources = [], {}
    for part in group["parts"]:
        step, bed = source(part)
        body, word = bodies(step, bed)
        meshes = {label: print_mesh(shape) for label, shape in (("body", body), ("word", word))}
        lo = np.min([m.bounds[0] for m in meshes.values()], axis=0)
        hi = np.max([m.bounds[1] for m in meshes.values()], axis=0)
        parts.append({"part": part, "step": step, "bed": bed, "meshes": meshes,
                      "footprint": (float(hi[0] - lo[0]), float(hi[1] - lo[1]))})
        sources[relative(step)] = sha256(step)
    positions = layout([p["footprint"] for p in parts], centre)
    # The prime tower stands centred behind the parts, clear of every footprint.
    back = max(y + p["footprint"][1] / 2 for p, (x, y) in zip(parts, positions))
    width = float(settings["prime_tower_width"])
    settings["wipe_tower_x"] = [f"{centre[0] - width / 2:.1f}"] * 2
    settings["wipe_tower_y"] = [f"{back + GAP * 2:.1f}"] * 2
    tops = []
    for p in parts:
        if p["bed"] == "back":
            tops.extend(round(float(m.bounds[1][2]), 4) for m in p["meshes"].values())
    bands = _derive.closing_schedule(tops)

    digest = hashlib.sha256("".join(sorted(sources.values())).encode()).hexdigest()[:8]
    stem = f"{datetime.date.today():%Y-%m-%d}-labels-{colour}-mark2-{digest}"
    directory = OUTPUT / stem
    if directory.exists():
        raise FileExistsError(f"{relative(directory)} exists; a preparation directory is written once")
    (directory / "geometry").mkdir(parents=True)
    Q = _native.qn
    model = ET.Element(Q("model"), unit="millimeter")
    ET.SubElement(model, Q("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
    resources, build = ET.SubElement(model, Q("resources")), ET.SubElement(model, Q("build"))
    config, ranges = ET.Element("config"), ET.Element("objects")
    plate = ET.SubElement(config, "plate")
    for key, value in {"plater_id": 1, "plater_name": f"{colour} identification; Mark2", "locked": "false",
                       "bed_type": settings["curr_bed_type"], "filament_map_mode": "Manual",
                       "filament_maps": "1 2", "filament_volume_maps": "0 0"}.items():
        _native._metadata(plate, key, value)
    records = []
    for number, (p, (x, y)) in enumerate(zip(parts, positions), 1):
        name = p["part"].replace(":", "-")
        children = []
        for label, tool in (("body", group["body"]), ("word", group["word"])):
            mesh = p["meshes"][label]
            stl = directory / "geometry" / f"{name}-{label}.stl"
            mesh.export(stl)
            oid = len(resources) + 1
            obj = ET.SubElement(resources, Q("object"), id=str(oid), type="model")
            geometry = ET.SubElement(obj, Q("mesh"))
            vertices, triangles = ET.SubElement(geometry, Q("vertices")), ET.SubElement(geometry, Q("triangles"))
            for v in mesh.vertices:
                ET.SubElement(vertices, Q("vertex"), x=f"{v[0]:.6f}", y=f"{v[1]:.6f}", z=f"{v[2]:.6f}")
            for f in mesh.faces:
                ET.SubElement(triangles, Q("triangle"), v1=str(f[0]), v2=str(f[1]), v3=str(f[2]))
            children.append((oid, label, tool, stl, mesh))
        oid = len(resources) + 1
        owner = ET.SubElement(resources, Q("object"), id=str(oid), type="model")
        components = ET.SubElement(owner, Q("components"))
        cfg = ET.SubElement(config, "object", id=str(oid))
        _native._metadata(cfg, "name", name)
        _native._metadata(cfg, "extruder", group["body"])
        for child, label, tool, _, _ in children:
            ET.SubElement(components, Q("component"), objectid=str(child))
            element = ET.SubElement(cfg, "part", id=str(child), subtype="normal_part")
            for key, value in {"name": label, "extruder": tool, "matrix": _native.MATRIX}.items():
                _native._metadata(element, key, value)
        ET.SubElement(build, Q("item"), objectid=str(oid), transform=f"1 0 0 0 1 0 0 0 1 {x:.4f} {y:.4f} 0",
                      printable="1")
        instance = ET.SubElement(plate, "model_instance")
        identify = 2900 + number
        for key, value in {"object_id": oid, "instance_id": 0, "identify_id": identify}.items():
            _native._metadata(instance, key, value)
        element = ET.SubElement(ranges, "object", id=str(number))
        for low, high, height in bands:
            band = ET.SubElement(element, "range", min_z=f"{low:g}", max_z=f"{high:g}")
            ET.SubElement(band, "option", opt_key="layer_height").text = f"{height:g}"
        records.append({"part": p["part"], "step": relative(p["step"]), "step_sha256": sha256(p["step"]),
                        "bed": "flat back" if p["bed"] == "back" else "flat face", "identify_id": identify,
                        "plate_center_xy_mm": [round(x, 3), round(y, 3)],
                        "footprint_xy_mm": [round(v, 3) for v in p["footprint"]],
                        "meshes": {label: {"stl": relative(stl), "stl_sha256": sha256(stl), "filament": tool,
                                           "facets": int(len(mesh.faces)), "volume_mm3": round(float(mesh.volume), 3),
                                           "top_mm": round(float(mesh.bounds[1][2]), 4)}
                                   for _, label, tool, stl, mesh in children}})
    members = dict(filament_members)
    members.update({"3D/3dmodel.model": _native._xml(model),
                    "Metadata/model_settings.config": _native._xml(config),
                    "Metadata/layer_config_ranges.xml": _native._xml(ranges),
                    _native.SETTINGS_MEMBER: (json.dumps(settings, indent=2) + "\n").encode(),
                    "_rels/.rels": b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
                    "[Content_Types].xml": b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'})
    cooling = _native.petgf_cooling.apply_members(members)
    project = directory / f"{stem}.3mf"
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for member, data in sorted(members.items()):
            entry = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, data)
    preparation = {
        "piece": f"labels-{colour}", "printer": "Mark2",
        "nozzle": {"left": "0.4 mm hardened, white PET-GF (filament 1)",
                   "right": f"0.4 mm hardened, {colour} PET-GF (filament 2)" if colour != "white"
                   else "0.4 mm hardened, black PET-GF (filament 2)"},
        "material": "Polymaker Fiberon PET-GF15, two colours", "filament_colours": group["colours"],
        "body_filament": group["body"], "word_filament": group["word"],
        "project": relative(project), "project_sha256": sha256(project),
        "profile": relative(PROFILE), "profile_sha256": sha256(PROFILE), "requested_z_trim_mm": Z_TRIM,
        "emitted_textured_trim_mm": round(Z_TRIM - 0.02, 3), "recipe": recipe, "cooling_changes": cooling,
        "closing_layer_ranges_mm": bands, "face_up_tops_mm": sorted(set(tops)),
        "usable_plate_mm": [low_area.tolist(), high_area.tolist()], "plate_border_mm": BORDER,
        "parts": records, "sources_sha256": sources,
        "tool_sha256": {relative(f): sha256(f) for f in (Path(__file__), HERE / "_native.py", HERE / "_derive.py")},
        "prepared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "sliced": False, "submitted": False}
    (directory / "preparation.json").write_text(json.dumps(preparation, indent=2) + "\n")
    print(relative(project), flush=True)
    return directory


def slice_and_review(directory: Path) -> dict:
    preparation = json.loads((directory / "preparation.json").read_text())
    project = ROOT / preparation["project"]
    if sha256(project) != preparation["project_sha256"]:
        raise ValueError("the project changed after preparation")
    native = directory / "native"
    native.mkdir()
    archive_name = project.name.replace(".3mf", ".gcode.3mf")
    with (native / "slice.log").open("w") as log:
        result = subprocess.run([STUDIO, "--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir", str(native),
                                 "--export-3mf", archive_name, str(project)], cwd=native, stdout=log,
                                stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Bambu Studio exited {result.returncode}; see {relative(native / 'slice.log')}")
    sliced = json.loads((native / "result.json").read_text())
    if sliced.get("return_code") != 0:
        raise RuntimeError(f"Bambu Studio reported {sliced.get('error_string')}")
    archive = directory / archive_name
    archive.write_bytes((native / archive_name).read_bytes())
    with zipfile.ZipFile(archive) as z:
        gcode = z.read("Metadata/plate_1.gcode")
        integrity = hashlib.md5(gcode).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
    text = gcode.decode("utf-8", "replace")
    trims = [float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", text[:400000], re.M)]
    low, high = np.full(2, np.inf), np.full(2, -np.inf)
    objects, supports, layer_count, tops = set(), 0, 0, []
    handle, stream = reader.gcode_lines(archive)
    with stream:
        for z, height, roads in reader.layers(stream):
            layer_count += 1
            tops.append(round(z, 4))
            for x0, y0, x1, y1, width, feature, obj in roads:
                low = np.minimum(low, [min(x0, x1) - width / 2, min(y0, y1) - width / 2])
                high = np.maximum(high, [max(x0, x1) + width / 2, max(y0, y1) + width / 2])
                supports += feature in reader.SUPPORT
                if obj is not None:
                    objects.add(obj)
    handle.close()
    area_low, area_high = (np.array(v) for v in preparation["usable_plate_mm"])
    margins = {"left": float(low[0] - area_low[0]), "front": float(low[1] - area_low[1]),
               "right": float(area_high[0] - high[0]), "back": float(area_high[1] - high[1])}
    wanted = preparation["face_up_tops_mm"]
    closed = {t: any(abs(t - z) < 1e-3 for z in tops) for t in wanted}
    expected = {p["identify_id"] for p in preparation["parts"]}
    result = {"archive": relative(archive), "archive_sha256": sha256(archive),
              "gcode_sha256": hashlib.sha256(gcode).hexdigest(), "gcode_md5_matches": integrity,
              "emitted_z_trim_mm": trims, "layers": layer_count,
              "bead_envelope_plate_mm": [low.tolist(), high.tolist()], "bed_margins_mm": margins,
              "minimum_bed_margin_mm": min(margins.values()), "support_roads": supports,
              "objects_printed": sorted(objects), "face_up_tops_closed": closed,
              "estimated_seconds": sum(p.get("total_predication", 0) for p in sliced.get("sliced_plates", [])),
              "slicer_warnings": [p.get("warning_message") for p in sliced.get("sliced_plates", []) if p.get("warning_message")]}
    checks = {"archive": integrity, "z_trim": bool(trims) and abs(trims[-1] - preparation["emitted_textured_trim_mm"]) < 0.005,
              "bed_border": result["minimum_bed_margin_mm"] >= preparation["plate_border_mm"],
              "no_support": supports == 0, "every_part_printed": expected <= objects,
              "face_up_tops_closed": all(closed.values())}
    result.update(checks=checks, passed=all(checks.values()),
                  scope="Commanded paths and bead envelopes from this archive. Colour registration, lettering "
                        "legibility, fit and finish are physical observations.")
    (directory / "review.json").write_text(json.dumps(result, indent=2) + "\n")
    preparation.update(sliced=True, archive=result["archive"], archive_sha256=result["archive_sha256"],
                       gcode_sha256=result["gcode_sha256"], estimated_seconds=result["estimated_seconds"])
    (directory / "preparation.json").write_text(json.dumps(preparation, indent=2) + "\n")
    print(json.dumps({"archive": result["archive"], "checks": checks, "minimum_bed_margin_mm": result["minimum_bed_margin_mm"],
                      "estimated_seconds": result["estimated_seconds"]}, indent=2), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--colour", action="append", choices=sorted(GROUPS), help="one plate (default: all four)")
    parser.add_argument("--slice", action="store_true", help="slice each plate natively and read it back")
    args = parser.parse_args()
    failed = []
    for colour in args.colour or list(GROUPS):
        directory = prepare(colour)
        if args.slice and not slice_and_review(directory)["passed"]:
            failed.append(colour)
    if failed:
        raise SystemExit(f"review did not pass: {', '.join(failed)}")


if __name__ == "__main__":
    main()
