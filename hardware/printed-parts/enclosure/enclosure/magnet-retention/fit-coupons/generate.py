"""Open upright RC62 pocket coupons for independent X/Y hand-fit comparison.

Build direction +Z and ring axis Y match the cartridge. No roof, pause or
support is needed. Each ring projects above the rim for finger removal.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _cadq_export import export_assembly
from _materials import one_body, M_PETG_BLACK
from flute_payload import cut as write_print_payload

OD, THICKNESS = 19.05, 3.175
FACE, BACK, SIDE, FLOOR = 1.2, 3.0, 3.0, 3.0
RIM = 20.12
WIDTHS = {"A": 19.35, "B": 19.15, "C": 19.05, "D": 18.95}
DEPTHS = {1: 3.45, 2: 3.30, 3: 3.175, 4: 3.05}
BASELINE = HERE.parent / "v4/pump-cartridge-cap-pause.3mf"
STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidates():
    return [(f"{a}{b}", x, y) for a, x in WIDTHS.items() for b, y in DEPTHS.items()] + [
        ("C0", 19.45, 3.575)]


def build(label, width, depth):
    body = cq.Solid.makeBox(width + 2 * SIDE, FACE + depth + BACK, RIM,
                            cq.Vector(-width / 2 - SIDE, -FACE, 0))
    arc_z = FLOOR + width / 2
    seat = cq.Solid.makeCylinder(width / 2, depth, cq.Vector(0, 0, arc_z), cq.Vector(0, 1, 0))
    mouth = cq.Solid.makeBox(width, depth, RIM + 1 - arc_z,
                            cq.Vector(-width / 2, 0, arc_z))
    body = body.cut(seat.fuse(mouth))
    tab = cq.Solid.makeBox(width + 2 * SIDE, 9, 1.4,
                          cq.Vector(-width / 2 - SIDE, -FACE - 7, 0))
    letters = (cq.Workplane("XY").workplane(offset=1.39).center(0, -FACE - 3.5)
               .text(label, 4, 0.73, font="Arial", kind="bold", combine=False).val())
    solid = body.fuse(tab).fuse(letters).clean()
    assert solid.isValid() and len(solid.Solids()) == 1, label
    return solid


def generate():
    if (HERE / "geometry.json").exists():
        record = json.loads((HERE / "geometry.json").read_text())
        for row in record["samples"]:
            for ext in ("step", "stl"):
                assert sha(HERE / row[ext]) == row[f"{ext}_sha256"]
        print("Using the frozen coupon exports", flush=True)
        return record
    rows = []
    for label, width, depth in candidates():
        solid = build(label, width, depth)
        name = f"rc62-pocket-{label.lower()}"
        step, stl = HERE / f"{name}.step", HERE / f"{name}.stl"
        export_assembly(one_body(cq.Workplane(obj=solid), name, M_PETG_BLACK), str(step))
        cq.exporters.export(solid, str(stl), tolerance=0.005, angularTolerance=0.05)
        mesh = trimesh.load_mesh(stl, process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1, label
        write_print_payload(step, stl, verbose=False, preserve_print_triangles=True)
        rows.append(dict(label=label, name=name, pocket_width_x_mm=width, pocket_depth_y_mm=depth,
                         nominal_diametral_clearance_mm=round(width - OD, 3),
                         nominal_axial_clearance_mm=round(depth - THICKNESS, 3),
                         lower_arc_radius_mm=width / 2, lower_arc_center_z_mm=FLOOR + width / 2,
                         bounds_mm=mesh.bounds.tolist(), volume_mm3=solid.Volume(),
                         stl=stl.name, step=step.name, stl_sha256=sha(stl), step_sha256=sha(step),
                         payload_sha256=sha(step.with_name(step.name + ".mesh"))))
    record = dict(article="Open upright RC62 X/Y pocket grip comparison", revision=1,
                  magnet=dict(model="K&J RC62", od_mm=OD, thickness_mm=THICKNESS,
                              tolerance_mm=0.1, source="https://www.kjmagnetics.com/rc62-neodymium-ring-magnet"),
                  print_build_axis=[0, 0, 1], magnet_axis=[0, 1, 0], insertion_axis=[0, 0, -1],
                  dimensions_mm=dict(face_cover=FACE, backing=BACK, side_wall=SIDE,
                                     pocket_floor=FLOOR, open_rim=RIM,
                                     nominal_ring_exposed_above_rim=round(FLOOR + OD - RIM, 3)),
                  control="C0: current production clearances", roof=False, pause=False,
                  samples=rows, physical_grip_qualified=False,
                  scope="Comparative hand insertion and rattle screen. The open rim differs from encapsulated stiffness; no over-magnet layer or retention-force qualification.")
    (HERE / "geometry.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"Exported {len(rows)} open, labeled RC62 coupons", flush=True)
    return record


def prepare(record, revision, do_slice):
    project = HERE / f"mark2-v{revision}.3mf"
    report_path = HERE / f"mark2-v{revision}-preparation.json"
    if project.exists() or report_path.exists():
        raise FileExistsError("Use a fresh reviewed-print revision")
    source = ROOT / "hardware/printed-parts/faucet/refresh_print_project.py"
    spec = importlib.util.spec_from_file_location("coupon_project_writer", source)
    writer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(writer)
    samples = record["samples"]
    parts = tuple((s["name"], HERE / s["stl"], 0.0) for s in samples)
    offsets = tuple(((i % 5 - 2) * 32, (i // 5 - 1.5) * 23) for i in range(len(samples)))
    report = writer.refresh(BASELINE, project, parts=parts, offsets=offsets, z_trim=0.04,
                            title="RC62 upright pocket fit A1-D4 and C0; Mark2", plate_border=15)
    with zipfile.ZipFile(project) as z:
        members = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {"enable_support": "0", "brim_type": "no_brim", "filament_colour": ["#161616"]}
    settings.update(changes)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    for name in list(members):
        if name.startswith("Metadata/filament_settings_"):
            filament = json.loads(members[name])
            filament["filament_colour"] = ["#161616"]
            members[name] = (json.dumps(filament, indent=2) + "\n").encode()
    writer.archive_write(project, members)
    report.update(printer="Mark2", revision=revision, submitted=False, pause_count=0,
                  preparation_script_sha256=sha(HERE / "generate.py"),
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  included_labels=[s["label"] for s in samples],
                  fit_geometry_record_sha256=sha(HERE / "geometry.json"),
                  settings_changes_for_open_coupons=changes,
                  project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  expected_left_external_spool=dict(slot=254, type="PET-CF", profile="GFT01", colour="161616"),
                  requested_z_trim_mm=0.04, nozzle="fixed left hardened standard-flow 0.4 mm")
    if do_slice:
        output = ROOT / f".cache/prints/rc62-pocket-fit-mark2-v{revision}"
        output.mkdir(parents=True, exist_ok=True)
        archive = output / f"rc62-pocket-fit-mark2-v{revision}.gcode.3mf"
        if archive.exists():
            raise FileExistsError(archive)
        with (output / "slice.log").open("w") as log:
            subprocess.run([STUDIO, "--slice", "0", "--arrange", "0", "--orient", "0",
                            "--outputdir", str(output), "--export-3mf", archive.name, str(project)],
                           cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True)
        with zipfile.ZipFile(archive) as z:
            gcode = z.read("Metadata/plate_1.gcode")
        report.update(native_archive=str(archive.relative_to(ROOT)), native_archive_sha256=sha(archive),
                      gcode_sha256=hashlib.sha256(gcode).hexdigest())
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k:report.get(k) for k in ("project", "native_archive", "included_labels", "submitted")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--slice", action="store_true")
    parser.add_argument("--revision", type=int, default=1)
    args = parser.parse_args()
    record = generate()
    if args.prepare or args.slice:
        prepare(record, args.revision, args.slice)
