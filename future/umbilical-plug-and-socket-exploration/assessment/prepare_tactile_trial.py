"""Prepare one optional, unpowered tactile trial; never submit a printer job.

Socket and plug retain the exploration's interface, but have solid material
where the unowned magnets would sit. They cannot become functional magnet
parts later. The other three parts are unchanged. A sixth part represents
the countertop's 34.93 mm hole through 30 mm of material.
"""
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "hardware").is_dir())
sys.path[:0] = [str(BASE), str(ROOT / "hardware/printed-parts/faucet"),
               str(ROOT / "hardware/scripts")]
import umbilical as u
import refresh_print_project as writer

OUT = BASE / "tactile-trial"
WORK = ROOT / ".cache/prints/umbilical-tactile"
PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
SLICER = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shapes():
    original = u.magnet_slots
    try:
        u.magnet_slots = lambda *_args: []
        socket, plug = u.socket(), u.plug()
    finally:
        u.magnet_slots = original
    counter = u.cq.Solid.makeCylinder(25.0, 30.0).cut(
        u.cq.Solid.makeCylinder(u.COUNTER_HOLE / 2, 32.0,
                               u.cq.Vector(0, 0, -1)))
    # Positions measured from the center of the shared profile's usable area.
    return (("socket-tactile", socket, 0.0, (-52.5, -22.0)),
            ("plug-tactile", plug, 180.0, (-8.5, -25.0)),
            ("counter-hole", counter, 0.0, (43.5, -30.0)),
            ("wall-coupon", u.coupon(), 180.0, (-32.5, 40.0)),
            ("retainer", u.retainer(), -90.0, (37.5, 30.0)),
            ("tube-key", u.key(), 90.0, (39.5, 69.0)))


def prepare():
    WORK.mkdir(parents=True, exist_ok=True)
    (OUT / "parts").mkdir(parents=True, exist_ok=True)
    parts, offsets, geometry = [], [], []
    for name, shape, angle, offset in shapes():
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError(f"Invalid solid: {name}")
        source = OUT / "parts" / f"{name}.stl"
        shape.exportStl(str(source), tolerance=.01, angularTolerance=.1)
        parts.append((name, source, angle))
        offsets.append(offset)
        geometry.append({"name": name, "solid_count": 1, "valid": True,
                         "faces": len(shape.Faces()), "edges": len(shape.Edges())})
    project = OUT / "tactile-mark1-z018.3mf"
    report = writer.refresh(PROFILE, project, parts=tuple(parts), offsets=tuple(offsets),
                            title="Umbilical tactile trial — no magnets, no pauses",
                            z_trim=.18, plate_border=20.0)
    with zipfile.ZipFile(project) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {"enable_support": "0", "wall_loops": "4", "sparse_infill_density": "25%"}
    settings.update(changes)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    writer.archive_write(project, members)
    report.update(printer_connection="H2C", printer_name="Mark1", z_trim_mm=.18,
                  enable_support=False, wall_loops=4, sparse_infill_percent=25.0,
                  settings_changes_after_refresh=changes,
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  project_sha256=sha(project), source_geometry_sha256=sha(BASE / "umbilical.py"),
                  preparation_sha256=sha(Path(__file__)), geometry=geometry,
                  scope="Unpowered tactile geometry only. Magnet pockets filled. No pressure, electrical, magnetic retention or fourth-union release qualification.",
                  submitted=False)
    print("Slicing six tactile parts for Mark1", flush=True)
    archive_name = project.stem + ".gcode.3mf"
    with (WORK / "slice.log").open("w") as log:
        result = subprocess.run([SLICER, "--slice", "0", "--arrange", "0", "--orient", "0",
                                 "--outputdir", str(WORK), "--export-3mf", archive_name,
                                 str(project)], cwd=WORK, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Slicer returned {result.returncode}: {WORK / 'slice.log'}")
    sliced = OUT / archive_name
    sliced.write_bytes((WORK / archive_name).read_bytes())
    with zipfile.ZipFile(sliced) as archive:
        if archive.testzip() is not None:
            raise ValueError("Damaged native archive")
        raw = archive.read("Metadata/plate_1.gcode")
    gcode_path = WORK / "plate_1.gcode"
    gcode_path.write_bytes(raw)
    gcode = raw.decode()
    beads = writer.object_toolpaths(gcode_path, WORK / "all-layer-beads.gcode", None)
    low, high = beads["extrusion_bounds_xy_mm"]
    bed_low, bed_high = report["shared_printable_area_mm"]
    margin = min(*(a - b for a, b in zip(low, bed_low)),
                 *(b - a for a, b in zip(high, bed_high)))
    layers = [float(n) for n in re.findall(r"^; Z_HEIGHT: ([\d.]+)", gcode, re.M)]
    pauses = len(re.findall(r"^M400 U1", gcode, re.M))
    supports = len(re.findall(r"^; FEATURE: Support", gcode, re.M))
    trims = [float(n) for n in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    native = {"archive": sliced.name, "archive_sha256": sha(sliced),
              "gcode_sha256": hashlib.sha256(raw).hexdigest(),
              "estimated_time": re.search(r"; total estimated time: (.+)", gcode).group(1).strip(),
              "filament_g": [float(n) for n in re.search(
                  r"; total filament weight \[g\] : ([\d.,]+)", gcode).group(1).split(",")],
              "first_layer_z_mm": layers[0], "normal_layer_height_mm": .24,
              "layer_count": len(layers), "support_features": supports, "pause_commands": pauses,
              "emitted_z_trim_mm": trims, "complete_layer_bead_bounds": beads,
              "minimum_full_bead_bed_margin_mm": margin}
    heights_ok = all(abs(b - a - .24) < 1e-4 for a, b in zip(layers, layers[1:]))
    if pauses or supports or margin < 80 or layers[0] != .2 or not heights_ok or trims != [0.0, .16]:
        raise ValueError(json.dumps(native, indent=2))
    report["native"] = native
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(native, indent=2), flush=True)


if __name__ == "__main__":
    prepare()
