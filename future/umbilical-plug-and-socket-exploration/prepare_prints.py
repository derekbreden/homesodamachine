"""Write and slice the two print jobs: the machine side (socket, retainer, wall coupon) and the plug
side (plug, tube key). Each takes the shared PET-GF profile with supports off and one pause, before
the layer that closes over its two SB443-IN bars. Projects and sliced archives go to `print/`, the
STLs and slicer logs to `.cache/prints/umbilical/`. Nothing is sent to a printer.

    tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/prepare_prints.py [--printer H2C]
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

_HERE = (Path(__file__).resolve() if "__file__" in globals()
         else Path.cwd() / "future/umbilical-plug-and-socket-exploration/prepare_prints.py")
sys.path.insert(0, str(_HERE.parent))
import umbilical as u  # noqa: E402
from umbilical import ROOT  # noqa: E402

sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer  # noqa: E402

PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
SLICER = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
WORK = ROOT / ".cache/prints/umbilical"
PRINT = _HERE.parent / "print"
TRIMS = {"Mark2": 0.04, "H2C": 0.18}       # enclosure/print-readiness.md

BAR_RULE = ("Looking at the mating face, the left bar shows N and the right bar S. Mark each bar's N face "
            "with a compass first.")
JOBS = {
    "machine-side": {
        "title": "Umbilical socket, retainer and wall coupon",
        # name, solid, rotation about X into its print pose, bed offset from the plate centre
        "parts": [("socket", u.socket, 0.0, (-55.0, 0.0)),
                  ("retainer", u.retainer, -90.0, (40.0, -32.0)),
                  ("wall-coupon", u.coupon, 180.0, (40.0, 36.0))],
        "bar_centre_z": -u.SOCKET_BED, "slot_top": u.SOCKET_SLOT_TOP,
        "pause": "Socket: slide one K&J SB443-IN down each slot in the cup floor, grooves on the rails, "
                 "pole face flush with the floor. " + BAR_RULE + " Resume; the next layer closes over them.",
    },
    "plug-side": {
        "title": "Umbilical plug and tube key",
        "parts": [("plug", u.plug, 180.0, (-30.0, 0.0)),
                  ("tube-key", u.key, 90.0, (32.0, 0.0))],
        "bar_centre_z": u.PLUG_BED, "slot_top": u.PLUG_SLOT_TOP,
        "pause": "Plug: slide one K&J SB443-IN down each slot in the plug's face, grooves on the rails, "
                 "pole face flush with the face. " + BAR_RULE + " Resume; the next layer closes over them.",
    },
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export_stl(solid, path):
    solid.exportStl(str(path), tolerance=0.01, angularTolerance=0.1)


def closing_layer(job):
    """The layer that first closes over the bars: its bottom is the slot's top, a layer boundary."""
    bottom = job["bar_centre_z"] + u.BAR / 2 + job["slot_top"]
    return round(bottom, 3), round(bottom + u.LAYER, 3)


def pause_xml(top_z, message):
    root = ET.Element("custom_gcodes_per_layer")
    plate = ET.SubElement(root, "plate")
    ET.SubElement(plate, "plate_info", id="1")
    ET.SubElement(plate, "layer", top_z=f"{top_z:.3f}", type="1", extruder="1", color="", extra=message,
                  gcode="M400 U1")
    ET.SubElement(plate, "mode", value="SingleExtruder")
    return ET.tostring(root, xml_declaration=True, encoding="UTF-8")


def project(name, job, printer):
    WORK.mkdir(parents=True, exist_ok=True)
    PRINT.mkdir(parents=True, exist_ok=True)
    parts = []
    for part, build, angle, offset in job["parts"]:
        stl = WORK / f"{part}.stl"
        export_stl(build(), stl)
        parts.append((part, stl, angle))
    out = PRINT / f"{name}-{printer.lower()}.3mf"
    report = writer.refresh(PROFILE, out, parts=tuple(parts), offsets=tuple(p[3] for p in job["parts"]),
                            title=job["title"], z_trim=TRIMS[printer], plate_border=20.0)
    with zipfile.ZipFile(out) as z:
        members = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {"enable_support": "0", "wall_loops": "4", "sparse_infill_density": "25%"}
    for key, value in changes.items():
        settings[key] = value
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    bottom, top = closing_layer(job)
    members["Metadata/custom_gcode_per_layer.xml"] = pause_xml(top, job["pause"])
    writer.archive_write(out, members)
    report.update({"printer": printer, "z_trim_mm": TRIMS[printer], "settings_changes_after_refresh": changes,
                   "pause_before_layer_top_z_mm": top, "slot_top_mm": bottom,
                   "bar_top_print_z_mm": round(job["bar_centre_z"] + u.BAR / 2, 3),
                   "project_sha256": sha(out), "pause_message": job["pause"]})
    return out, report


def slice_project(path):
    log = WORK / f"{path.stem}.slice.log"
    stage = WORK / path.stem
    stage.mkdir(parents=True, exist_ok=True)
    archive = f"{path.stem}.gcode.3mf"
    cmd = [SLICER, "--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir", str(stage),
           "--export-3mf", archive, str(path)]
    with log.open("w") as stream:
        got = subprocess.run(cmd, cwd=stage, stdout=stream, stderr=subprocess.STDOUT)
    if got.returncode:
        raise RuntimeError(f"slice failed ({got.returncode}): {log}")
    sliced = stage / archive
    target = PRINT / archive
    target.write_bytes(sliced.read_bytes())
    return target


def review(archive, report):
    """Read the emitted G-code: the pause must open the closing layer, before any of its moves, and
    the slice must carry no supports."""
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        gcode = z.read("Metadata/plate_1.gcode").decode()
    layers, pause_layer, extruded_before_pause = [], None, False
    for line in gcode.splitlines():
        m = re.match(r"; Z_HEIGHT: ([\d.]+)", line)
        if m:
            layers.append(float(m.group(1)))
            extruded = False
        elif line.startswith("M400 U1") and layers:
            pause_layer, extruded_before_pause = layers[-1], extruded
        elif layers and re.match(r"G[123] .*E\.?\d", line) and not re.search(r"E-", line):
            extruded = True
    supports = len(re.findall(r"; FEATURE: Support", gcode))
    i = layers.index(pause_layer) if pause_layer in layers else None
    last_before = layers[i - 1] if i else None
    expected = report["pause_before_layer_top_z_mm"]
    out = {
        "archive": archive.name, "archive_sha256": sha(archive),
        "layers": len(layers), "first_layer_z": layers[0] if layers else None,
        "last_layer_before_pause_z": last_before, "pause_opens_layer_z": pause_layer,
        "expected_pause_layer_z": expected,
        "pause_placed_as_designed": pause_layer is not None and abs(pause_layer - expected) < 1e-3
        and not extruded_before_pause,
        "air_over_bar_mm": round(last_before - report["bar_top_print_z_mm"], 3) if last_before else None,
        "support_features": supports,
        "estimated_time": re.search(r"; total estimated time: (.+)", gcode).group(1).strip()
        if "; total estimated time:" in gcode else None,
        "filament_g": [float(v) for v in re.search(r"; total filament weight \[g\] : ([\d.,]+)", gcode)
                       .group(1).split(",")] if "; total filament weight [g]" in gcode else None,
    }
    if not out["pause_placed_as_designed"] or supports:
        raise RuntimeError(json.dumps(out, indent=2))
    return out


def bar_coverage(archive, report, part, sign):
    """Extrusion over each bar's footprint (inside its rails) on the last layer before the pause and
    the first after it: none, then a bridge."""
    import numpy as np
    with zipfile.ZipFile(archive) as z:
        gcode = z.read("Metadata/plate_1.gcode").decode().splitlines()
    want = {report["native"]["last_layer_before_pause_z"], report["native"]["pause_opens_layer_z"]}
    layers, z_now, x, y, feature = {zz: [] for zz in want}, None, 0.0, 0.0, ""
    for line in gcode:
        m = re.match(r"; Z_HEIGHT: ([\d.]+)", line)
        if m:
            z_now = float(m.group(1))
            continue
        if line.startswith("; FEATURE:"):
            feature = line[10:].strip()
            continue
        if not line.startswith(("G1", "G2", "G3")):
            continue
        w = dict(re.findall(r"([XYE])(-?[\d.]+)", line))
        nx, ny = float(w.get("X", x)), float(w.get("Y", y))
        if z_now in layers and float(w.get("E", 0)) > 0 and (nx, ny) != (x, y):
            layers[z_now].append((x, y, nx, ny, feature))
        x, y = nx, ny
    row = next(r for r in report["parts"] if r["name"] == part)
    centre, shift = np.array(row["source_center_mm"]), np.array(row["plate_translation_mm"])
    turn = np.array(row["build_transform"][:9]).reshape(3, 3).T
    out = {}
    for mx in (-u.MAG_X, u.MAG_X):
        corners = [(np.array((mx + dx, sign * dy, 0.0)) - centre) @ turn.T + shift
                   for dx in (-2.2, 2.2) for dy in (0.4, 4.4)]
        lo, hi = np.min(corners, axis=0), np.max(corners, axis=0)
        for zz, segs in layers.items():
            feats = [f for (x0, y0, x1, y1, f) in segs
                     if any(lo[0] < x0 + (x1 - x0) * t < hi[0] and lo[1] < y0 + (y1 - y0) * t < hi[1]
                            for t in np.linspace(0, 1, 11))]
            out[f"bar_x{mx:+.0f}_z{zz:g}"] = {"moves": len(feats), "features": sorted(set(feats))}
    before = [v["moves"] for k, v in out.items() if k.endswith(f"z{report['native']['last_layer_before_pause_z']:g}")]
    after = [v["moves"] for k, v in out.items() if k.endswith(f"z{report['native']['pause_opens_layer_z']:g}")]
    if any(before) or not all(after):
        raise RuntimeError(json.dumps(out, indent=2))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--printer", choices=sorted(TRIMS), default="Mark2")
    args = parser.parse_args()
    summary = {}
    for name, job in JOBS.items():
        path, report = project(name, job, args.printer)
        archive = slice_project(path)
        report["native"] = review(archive, report)
        part, sign = ("socket", +1) if name == "machine-side" else ("plug", -1)
        report["native"]["bar_coverage"] = bar_coverage(archive, report, part, sign)
        plate_picture(archive, _HERE.parent / "renders" / f"print-{name}.png")
        path.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
        summary[name] = report["native"]
        print(json.dumps({name: report["native"]}, indent=2), flush=True)
    m, q = summary["machine-side"], summary["plug-side"]
    fig = {"UMB_PRINTER": args.printer, "UMB_TRIM": f"{TRIMS[args.printer]:+.2f}",
           "UMB_PAUSE_SOCKET": f"{m['pause_opens_layer_z']:.2f}", "UMB_PAUSE_PLUG": f"{q['pause_opens_layer_z']:.2f}",
           "UMB_AIR_SOCKET": f"{m['air_over_bar_mm']:.3f}", "UMB_AIR_PLUG": f"{q['air_over_bar_mm']:.3f}",
           "UMB_TIME_SOCKET": short_time(m["estimated_time"]), "UMB_TIME_PLUG": short_time(q["estimated_time"]),
           "UMB_G_SOCKET": f"{m['filament_g'][0]:.0f}", "UMB_G_PLUG": f"{q['filament_g'][0]:.0f}"}
    sys.path.insert(0, str(ROOT / "tools"))
    from docgen import substitute_md
    substitute_md(_HERE.parent / "README.md", fig)
    return summary


def plate_picture(archive, out):
    """The slicer's own picture of the plate, laid on a light ground so it reads in either theme."""
    import io
    from PIL import Image
    with zipfile.ZipFile(archive) as z:
        shot = Image.open(io.BytesIO(z.read("Metadata/plate_1.png"))).convert("RGBA")
    ground = Image.new("RGBA", shot.size, (232, 231, 227, 255))
    ground.alpha_composite(shot)
    ground.convert("RGB").save(out, optimize=True)


def short_time(text):
    """'2h 38m 48s' -> '2 h 39 min'."""
    h = int(re.search(r"(\d+)h", text).group(1)) if "h" in text else 0
    m = int(re.search(r"(\d+)m", text).group(1)) if "m" in text else 0
    s = int(re.search(r"(\d+)s", text).group(1)) if "s" in text else 0
    total = round((h * 3600 + m * 60 + s) / 60)
    return f"{total // 60} h {total % 60} min" if total >= 60 else f"{total} min"


main()      # run as a file, like scene.py; no __main__ guard keeps it out of the build graph
