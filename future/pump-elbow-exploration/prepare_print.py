"""Slice a compact elbow plate offline with the saved right 0.6 mm H2C mapping.

No printer connection is made. Physical material/nozzle mapping is a launch
decision, and this slice is no evidence of sealing performance.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import tempfile
import uuid
import zipfile
import xml.etree.ElementTree as ET

import cadquery as cq

from tpu_elbow import Elbow

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / ".cache/pump-elbow-exploration/native"
PROFILES = Path("/Applications/BambuStudio.app/Contents/Resources/profiles/BBL/filament")
TEMPLATE = ROOT / "hardware/printed-parts/asse-drain-adapter/asse-drain-adapter-tpu85a-right06-mark2.3mf"
SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from enclosure_support_audit import _current_profile_slice


def filament(name):
    d = json.loads((PROFILES / f"{name}.json").read_text())
    combined = filament(d["inherits"]) if d.get("inherits") else {}
    for entry in d.get("include", []):
        combined.update(filament(entry))
    combined.update(d)
    for key in ("inherits", "include", "name", "type", "from", "setting_id", "instantiation"):
        combined.pop(key, None)
    return combined


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    plate = cq.Compound.makeCompound([
        Elbow(tube_depth=12).print_shape().translate((-18.5, 0, 0)),
        Elbow(tube_depth=15).print_shape().translate((18.5, 0, 0)),
    ])
    mesh = CACHE / "elbow-plate.stl"
    cq.exporters.export(plate, str(mesh), tolerance=.01, angularTolerance=.05)
    profile = CACHE / "elbow-profile.3mf"
    with zipfile.ZipFile(TEMPLATE) as z, zipfile.ZipFile(profile, "w", zipfile.ZIP_DEFLATED) as target:
        d = json.loads(z.read("Metadata/project_settings.config"))
        selected = filament("Bambu TPU 95A HF @BBL H2C")
        d.update(selected)
        d.update({
            "filament_settings_id": ["Bambu TPU 95A HF @BBL H2C"],
            "filament_colour": ["#101820"], "filament_type": ["TPU"],
            "filament_extruder_compatibility": ["0"],
            "layer_height": "0.12", "initial_layer_print_height": "0.20",
            "wall_loops": "6", "enable_support": "0",
            "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag",
            "seam_gap": "0%", "line_width": "0.62", "outer_wall_line_width": "0.62",
            "inner_wall_line_width": "0.62", "brim_width": "5", "brim_type": "outer_only",
            "outer_wall_speed": ["25"]*4, "inner_wall_speed": ["25"]*4,
            "internal_solid_infill_speed": ["25"]*4, "top_surface_speed": ["25"]*4,
            "initial_layer_speed": ["20"]*4,
            "print_settings_id": "TPU elbow sealing exploration 0.12 mm right 0.6",
        })
        for info in z.infolist():
            payload = json.dumps(d).encode() if info.filename == "Metadata/project_settings.config" else z.read(info.filename)
            if info.filename.startswith("3D/Objects/") and info.filename.endswith(".model"):
                # The template's compact XML carries no production UUID.
                # Add the UUID used by native mesh replacement for binding.
                payload = payload.replace(b'<model ', b'<model xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" ', 1)
                payload = payload.replace(b'<object id="1"',
                    f'<object id="1" p:UUID="{uuid.uuid4()}"'.encode(), 1)
            if info.filename == "Metadata/model_settings.config":
                root = ET.fromstring(payload)
                for m in root.iter("metadata"):
                    if m.attrib.get("key") == "plater_name":
                        m.set("value", "elbow-plate-tpu95a-right06")
                ET.indent(root, space="  ")
                payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            target.writestr(info, payload)
    directory = Path(tempfile.mkdtemp(prefix="slice-", dir=CACHE))
    gcode, project, bed_shift = _current_profile_slice(mesh, profile, SLICER, directory)
    (CACHE/"plate_1.gcode").write_bytes(gcode.read_bytes())
    destination = HERE / "elbow-plate-tpu95a-right06.3mf"
    destination.write_bytes(project.read_bytes())
    report = {
        "scope": "Offline native Bambu slice; no printer launch; no seal qualification",
        "slicer": str(SLICER), "bed_shift_mm": bed_shift,
        "template_sha256": hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(),
        "project_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "gcode_sha256": hashlib.sha256(gcode.read_bytes()).hexdigest(),
        "nozzle_mm": .6, "layer_mm": .12, "first_layer_mm": .2,
        "support_enabled": False, "wall_loops": 6,
    }
    report.update(read_beads(gcode))
    (HERE / "native-slice.json").write_text(json.dumps(report, indent=2)+"\n")
    print(destination, flush=True)


def read_beads(path):
    """Native deposition envelope including bead widths and XY arc extrema."""
    xyz = dict(X=0., Y=0., Z=0.)
    e, relative, feature, width = 0., True, "Custom", .62
    bounds = [math.inf, math.inf, -math.inf, -math.inf]
    counts = {}
    for line in path.read_text().splitlines():
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
            counts[feature] = counts.get(feature, 0) + 1
        if line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":", 1)[1])
        code = line.split(";", 1)[0]
        tokens = code.split()
        if not tokens:
            continue
        cmd = tokens[0]
        words = {k: float(v) for k, v in re.findall(
            r"([XYZEIJ])(-?(?:\d+(?:\.\d*)?|\.\d+))", code)}
        if cmd == "M83":
            relative = True
        if cmd == "M82":
            relative = False
        if cmd == "G92":
            e = words.get("E", e)
            continue
        if cmd not in ("G0", "G1", "G2", "G3"):
            continue
        start = (xyz["X"], xyz["Y"])
        end = (words.get("X", xyz["X"]), words.get("Y", xyz["Y"]))
        positive = words.get("E", 0) > 0 if relative else words.get("E", e) > e
        points = [start, end]
        if cmd in ("G2", "G3") and "I" in words and "J" in words:
            cx, cy = start[0] + words["I"], start[1] + words["J"]
            radius = math.hypot(words["I"], words["J"])
            a0 = math.atan2(start[1]-cy, start[0]-cx)
            a1 = math.atan2(end[1]-cy, end[0]-cx)
            if cmd == "G2":
                while a1 >= a0:
                    a1 -= 2*math.pi
            else:
                while a1 <= a0:
                    a1 += 2*math.pi
            for k in range(-8, 9):
                a = k*math.pi/2
                if min(a0, a1) <= a <= max(a0, a1):
                    points.append((cx+radius*math.cos(a), cy+radius*math.sin(a)))
        if positive and feature != "Custom" and math.dist(start, end) > 1e-8:
            for x, y in points:
                bounds = [min(bounds[0], x-width/2), min(bounds[1], y-width/2),
                          max(bounds[2], x+width/2), max(bounds[3], y+width/2)]
        for axis in xyz:
            xyz[axis] = words.get(axis, xyz[axis])
        if "E" in words:
            e = e + words["E"] if relative else words["E"]
    if not all(math.isfinite(n) for n in bounds):
        raise ValueError("Native model deposition envelope is unavailable")
    return {"native_full_bead_bounds_xy_mm": bounds,
            "bed_edge_margin_lower_bound_mm": min(bounds[0]-25, bounds[1],
                                                   325-bounds[2], 320-bounds[3]),
            "native_feature_counts": counts}


if __name__ == "__main__":
    main()
