"""Prepare the saved organizer and two diameter increments on Mark2; never submit.

Run manually. A is the production STL unchanged. B and C increase every bore
diameter by 0.10 and 0.20 mm from that saved part, including the signal passage.
The production model and its accepted physical-fit record are not modified.
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

import prepare_drain_fit as baseline

u, writer = baseline.u, baseline.writer
ROOT, HERE, PRODUCT = baseline.ROOT, baseline.HERE, baseline.PRODUCT
OUT = HERE / "diameter-increments-mark2"
WORK = ROOT / ".cache/prints/organizer-diameter-increments-mark2"
PROFILE = HERE / "drain-fit-mark2" / (baseline.JOB + ".3mf")
JOB = "2026-10-09-organizer-saved-plus010-plus020-petgf-left04-z004-mark2"
SAMPLES = (("A", 0.00, (-43.0, 0.0)),
           ("B", 0.10, (0.0, 0.0)),
           ("C", 0.20, (43.0, 0.0)))
sha = baseline.sha


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "parts").mkdir(exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    saved_bores = u.BORES
    parts, offsets, samples = [], [], []
    for label, delta, offset in SAMPLES:
        u.BORES = tuple((name, xy, diameter + delta) for name, xy, diameter in saved_bores)
        shape = u.build_organizer()
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError(f"Invalid organizer {label}")
        name = f"organizer-{label}-q{u.TUBE_BORE+delta:.2f}-d{u.DRAIN_BORE+delta:.2f}-s{u.CABLE_BORE+delta:.2f}"
        path = OUT / "parts" / (name + ".stl")
        if delta == 0:
            shutil.copyfile(PRODUCT / "umbilical-organizer.stl", path)
            generated = WORK / "saved-source-comparison.stl"
            shape.exportStl(str(generated), tolerance=0.05, angularTolerance=0.12)
            if sha(generated) != sha(path):
                raise ValueError("Saved production STL does not match the current source")
        else:
            shape.exportStl(str(path), tolerance=0.05, angularTolerance=0.12)
        parts.append((name, path, 0.0))
        offsets.append(offset)
        samples.append({"label": label, "diameter_increment_from_saved_mm": delta,
                        "quarter_inch_bore_diameter_mm": round(u.TUBE_BORE+delta, 2),
                        "drain_bore_diameter_mm": round(u.DRAIN_BORE+delta, 2),
                        "signal_bore_diameter_mm": round(u.CABLE_BORE+delta, 2),
                        "bores": [{"name": n, "axis_xy_mm": list(xy),
                                   "diameter_mm": round(d, 2)} for n, xy, d in u.BORES],
                        "length_mm": u.LENGTH, "od_mm": u.OD,
                        "bed_offset_xy_mm": list(offset),
                        "native_faces": len(shape.Faces()), "native_edges": len(shape.Edges()),
                        "valid_single_solid": True,
                        "source": str(path.relative_to(ROOT)), "sha256": sha(path),
                        "identical_to_saved_production_stl": delta == 0})
    u.BORES = saved_bores
    project = OUT / (JOB + ".3mf")
    report = writer.refresh(PROFILE, project, parts=tuple(parts), offsets=tuple(offsets),
                            title="Organizers A saved / B +0.10 / C +0.20 diameter",
                            plate_border=80)
    with zipfile.ZipFile(project) as z:
        settings = json.loads(z.read(writer.SETTINGS_MEMBER))
        if settings["enable_wrapping_detection"] != "0":
            raise ValueError("Clumping detection by probing must remain off")
        if settings["filament_nozzle_map"] != ["0"]:
            raise ValueError("Organizer plate must use the fixed left nozzle")
    report.update(samples=samples, printer_connection="Mark2", material="physical PET-GF",
                  slot=254, fixed_nozzle="left hardened standard-flow 0.4 mm",
                  requested_z_trim_mm=.04, probing_clump_detection=False,
                  production_source_sha256=sha(PRODUCT / "umbilical_organizer.py"),
                  production_stl_sha256=sha(PRODUCT / "umbilical-organizer.stl"),
                  preparation_source_sha256=sha(Path(__file__)), submitted=False)
    sliced_name = JOB + ".gcode.3mf"
    command = [str(baseline.SLICER), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(WORK), "--export-3mf", sliced_name, str(project)]
    (OUT / "slice-command.json").write_text(json.dumps(command, indent=2) + "\n")
    print("Slicing the saved organizer and two bore-diameter increments", flush=True)
    with (WORK / "slice.log").open("w") as log:
        result = subprocess.run(command, cwd=WORK, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Bambu slice returned {result.returncode}: {WORK / 'slice.log'}")
    sliced = OUT / sliced_name
    shutil.copyfile(WORK / sliced_name, sliced)
    with zipfile.ZipFile(sliced) as z:
        if z.testzip():
            raise ValueError("Damaged native archive member")
        raw = z.read("Metadata/plate_1.gcode")
        if hashlib.md5(raw).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum mismatch")
        matches = baseline.native_meshes(z, report)
        info = ET.fromstring(z.read("Metadata/slice_info.config"))
        objects = [n.attrib for n in info.findall(".//object") if n.get("skipped") != "true"]
        filaments = [n.attrib for n in info.findall(".//filament")]
        for member in z.namelist():
            if member.startswith("Metadata/") and member.endswith(".png") and "plate_1" in member:
                (OUT / Path(member).name).write_bytes(z.read(member))
    gcode_path = WORK / "plate_1.gcode"
    gcode_path.write_bytes(raw)
    gcode = raw.decode()
    beads = writer.object_toolpaths(gcode_path, WORK / "all-layer-beads.gcode", None)
    low, high = beads["extrusion_bounds_xy_mm"]
    bed_low, bed_high = report["shared_printable_area_mm"]
    margin = min(*(a-b for a,b in zip(low, bed_low)), *(b-a for a,b in zip(high, bed_high)))
    layers = [float(n) for n in re.findall(r"^; Z_HEIGHT: ([\d.]+)", gcode, re.M)]
    trims = [float(n) for n in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    supports = len(re.findall(r"^; FEATURE: Support", gcode, re.M))
    pauses = len(re.findall(r"^M400 U1", gcode, re.M))
    bare_g39 = len(re.findall(r"^\s*G39(?:\s|$)", gcode, re.M))
    estimate = re.search(r"; total estimated time: (.+)", gcode).group(1).strip()
    masses = [float(n) for n in re.search(r"; total filament weight \[g\] : ([\d.,]+)", gcode).group(1).split(",")]
    heights_ok = all(abs(b-a-.24)<1e-4 for a,b in zip(layers,layers[1:]))
    if supports or pauses or bare_g39 or margin < 80 or layers[0] != .2 or not heights_ok or trims != [0.0, .02]:
        raise ValueError("Native paths differ from the saved organizer process")
    if len(objects) != 3 or {x["name"] for x in objects} != {p[0] for p in parts}:
        raise ValueError("Native slice does not contain the three requested organizers")
    if len(filaments) != 1 or filaments[0]["type"] != "PET-CF" or filaments[0]["color"].upper() != "#161616":
        raise ValueError("Native filament differs from loaded left PET-GF")
    report["native"] = {"archive": sliced.name, "archive_sha256": sha(sliced),
                        "gcode_sha256": hashlib.sha256(raw).hexdigest(), "mesh_binding": matches,
                        "estimated_time": estimate, "filament_g": masses,
                        "first_layer_z_mm": layers[0], "normal_layer_mm": .24,
                        "last_layer_z_mm": layers[-1], "layer_count": len(layers),
                        "supports": supports, "pauses": pauses, "bare_G39_commands": bare_g39,
                        "emitted_z_trim_mm": trims, "complete_layer_bead_bounds": beads,
                        "minimum_full_bead_bed_margin_mm": margin, "objects": objects,
                        "filaments": filaments}
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["native"], indent=2), flush=True)


if __name__ == "__main__":
    prepare()
