"""Prepare three PET-GF sliding-fit pucks on one Mark2 plate; never submit.

Run manually with tools/cad-venv/bin/python. Source geometry, embedded meshes,
native commanded layers and full-bead bed margins are bound to this trial.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import trimesh

import organizer as o

ROOT = o.ROOT
HERE = o.HERE
OUT = HERE / "fit-trial-mark2"
WORK = ROOT / ".cache/prints/organizer-mark2"
PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
JOB = "2026-10-09-organizer-three-fits-petgf-left04-z004-mark2"
SAMPLES = (("tight", -0.10, (-43.0, 0.0)),
           ("best", 0.00, (0.0, 0.0)),
           ("loose", +0.10, (+43.0, 0.0)))
sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_meshes(archive, report):
    records = []
    for part in report["parts"]:
        model = ET.fromstring(archive.read(part["member"]))
        vertices = model.findall(".//"+writer.qn("vertex"))
        triangles = model.findall(".//"+writer.qn("triangle"))
        points = np.array([[float(v.get(k)) for k in "xyz"] for v in vertices])
        faces = np.array([[int(t.get(k)) for k in ("v1", "v2", "v3")] for t in triangles])
        original = trimesh.load(ROOT/part["source"], force="mesh", process=True)
        centered = original.vertices-original.bounds.mean(axis=0)
        # Bambu's float32 serialization moves these vertices by <=0.00000053 mm.
        matches = (np.allclose(points, centered, atol=1e-6, rtol=0)
                   and np.array_equal(faces, original.faces))
        if not matches:
            raise ValueError(f"Native mesh differs from the trial source: {part['name']}")
        records.append({"name": part["name"], "source_sha256": sha(ROOT/part["source"]),
                        "member": part["member"], "source_mesh_matches": True,
                        "vertex_count": len(points), "triangle_count": len(faces),
                        "max_coordinate_serialization_delta_mm": float(np.max(np.abs(points-centered)))})
    return records


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"parts").mkdir(exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    parts, offsets, samples = [], [], []
    for label, delta, offset in SAMPLES:
        tube_bore, drain_bore = o.TUBE_BORE+delta, o.DRAIN_BORE+delta
        shape = o.build_puck(tube_bore=tube_bore, drain_bore=drain_bore)
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError(f"Invalid puck: {label}")
        name = f"organizer-{label}-q{tube_bore:.2f}-d{drain_bore:.2f}"
        path = OUT/"parts"/(name+".stl")
        shape.exportStl(str(path), tolerance=0.05, angularTolerance=0.12)
        parts.append((name, path, 0.0))
        offsets.append(offset)
        samples.append({"label": label, "quarter_inch_bore_diameter_mm": round(tube_bore, 2),
                        "drain_bore_diameter_mm": round(drain_bore, 2),
                        "length_mm": o.LENGTH, "diameter_step_mm": delta,
                        "bed_offset_xy_mm": offset, "native_faces": len(shape.Faces()),
                        "native_edges": len(shape.Edges()), "valid_single_solid": True,
                        "source": str(path.relative_to(ROOT)), "sha256": sha(path)})
    project = OUT/(JOB+".3mf")
    report = writer.refresh(PROFILE, project, parts=tuple(parts), offsets=tuple(offsets),
                            title="PET-GF organizer: tight / best / loose", z_trim=.04, plate_border=80)
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {"enable_support": "0", "brim_type": "no_brim", "brim_width": "0",
               "filament_colour": ["#161616"]}
    settings.update(changes)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+"\n").encode()
    writer.archive_write(project, members)
    report.update(samples=samples, printer_connection="Mark2", material="physical PET-GF",
                  slot=254, fixed_nozzle="left 0.4 mm", requested_z_trim_mm=.04,
                  settings_changes_after_refresh=changes,
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  project_sha256=sha(project), organizer_source_sha256=sha(HERE/"organizer.py"),
                  preparation_source_sha256=sha(Path(__file__)), submitted=False)
    sliced_name = JOB+".gcode.3mf"
    command = [str(SLICER), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(WORK), "--export-3mf", sliced_name, str(project)]
    (OUT/"slice-command.json").write_text(json.dumps(command, indent=2)+"\n")
    print("Slicing three 10 mm PET-GF fit pucks for Mark2", flush=True)
    with (WORK/"slice.log").open("w") as log:
        result = subprocess.run(command, cwd=WORK, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Bambu slice returned {result.returncode}: {WORK/'slice.log'}")
    sliced = OUT/sliced_name
    shutil.copyfile(WORK/sliced_name, sliced)
    with zipfile.ZipFile(sliced) as archive:
        if archive.testzip():
            raise ValueError("The native archive has a damaged member")
        raw = archive.read("Metadata/plate_1.gcode")
        if hashlib.md5(raw).hexdigest() != archive.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum mismatch")
        matches = native_meshes(archive, report)
        info = ET.fromstring(archive.read("Metadata/slice_info.config"))
        objects = [n.attrib for n in info.findall(".//object") if n.get("skipped") != "true"]
        filaments = [n.attrib for n in info.findall(".//filament")]
        for member in archive.namelist():
            if member.startswith("Metadata/") and member.endswith(".png") and "plate_1" in member:
                (OUT/Path(member).name).write_bytes(archive.read(member))
    gcode_path = WORK/"plate_1.gcode"
    gcode_path.write_bytes(raw)
    gcode = raw.decode()
    beads = writer.object_toolpaths(gcode_path, WORK/"all-layer-beads.gcode", None)
    low, high = beads["extrusion_bounds_xy_mm"]
    bed_low, bed_high = report["shared_printable_area_mm"]
    margin = min(*(a-b for a,b in zip(low, bed_low)), *(b-a for a,b in zip(high, bed_high)))
    layers = [float(n) for n in re.findall(r"^; Z_HEIGHT: ([\d.]+)", gcode, re.M)]
    trims = [float(n) for n in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    supports = len(re.findall(r"^; FEATURE: Support", gcode, re.M))
    pauses = len(re.findall(r"^M400 U1", gcode, re.M))
    estimate = re.search(r"; total estimated time: (.+)", gcode).group(1).strip()
    masses = [float(n) for n in re.search(r"; total filament weight \[g\] : ([\d.,]+)", gcode).group(1).split(",")]
    heights_ok = all(abs(b-a-.24)<1e-4 for a,b in zip(layers,layers[1:]))
    if supports or pauses or margin<80 or layers[0] != .2 or not heights_ok or trims != [0.0,.02]:
        raise ValueError("Native paths do not match the requested trial settings")
    if len(objects) != 3 or {x['name'] for x in objects} != {p[0] for p in parts}:
        raise ValueError("Native slice does not contain the three requested pucks")
    if len(filaments) != 1 or filaments[0]["type"] != "PET-CF" or filaments[0]["color"].upper() != "#161616":
        raise ValueError("Native filament does not match Mark2's loaded left PET-GF")
    report["native"] = {"archive": sliced.name, "archive_sha256": sha(sliced),
                        "gcode_sha256": hashlib.sha256(raw).hexdigest(), "mesh_binding": matches,
                        "estimated_time": estimate, "filament_g": masses,
                        "first_layer_z_mm": layers[0], "normal_layer_mm": .24,
                        "last_layer_z_mm": layers[-1], "layer_count": len(layers),
                        "supports": supports, "pauses": pauses, "emitted_z_trim_mm": trims,
                        "complete_layer_bead_bounds": beads,
                        "minimum_full_bead_bed_margin_mm": margin, "objects": objects,
                        "filaments": filaments}
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report["native"], indent=2), flush=True)


if __name__ == "__main__":
    prepare()
