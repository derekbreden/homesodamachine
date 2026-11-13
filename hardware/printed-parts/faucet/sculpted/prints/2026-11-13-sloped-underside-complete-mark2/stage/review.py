"""Read a ready Sculpted tip-and-cover archive and write its slice review beside it.

usage: review.py <trial dir> <name> <slice dir> <purpose>
"""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

trial, name, run, purpose = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), sys.argv[4]
ready = trial / f"{name}-ready.gcode.3mf"
prep = json.loads((trial / f"{name}.print.json").read_text())
cooling = json.loads((run / "tip-end-cooling.json").read_text())
rim = json.loads((run / "tip-rim-contour.json").read_text())
result = json.loads((run / "result.json").read_text())["sliced_plates"][0]

with zipfile.ZipFile(ready) as z:
    raw = z.read("Metadata/plate_1.gcode")
    settings = json.loads(z.read("Metadata/project_settings.config"))
    assert hashlib.md5(raw).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
staged = json.loads((trial / "sloped-underside.json").read_text())
assert hashlib.sha256(raw).hexdigest() == staged["gcode_sha256"], "the archive does not hold the sloped stage's G-code"
with zipfile.ZipFile(staged["input_archive"]["path"]) as z:
    assert hashlib.sha256(z.read("Metadata/plate_1.gcode")).hexdigest() == cooling["gcode_sha256"], "the sloped stage did not start from the cooled slice"
gcode = raw.decode(errors="replace").splitlines()

MODEL = {
    "Outer wall", "Inner wall", "Overhang wall", "Floating vertical shell", "Sparse infill",
    "Internal solid infill", "Top surface", "Bottom surface", "Bridge", "Gap infill",
}
origin, axis, span = cooling["origin_plate_mm"], cooling["axis_plate"], cooling["span_mm"]
target = cooling["fan_percent"] * 255.0 / 100.0

pos = [0.0, 0.0, 0.0]
feed = 0.0
absolute = True
obj, feature, fan = -1, "", 0.0
lo, hi = [1e9, 1e9], [-1e9, -1e9]
stretch = {}
trims = []
for line in gcode:
    if line.startswith(";"):
        c = line[1:].strip()
        if c.startswith("FEATURE:"):
            feature = c[8:].strip()
        elif c.startswith("start printing object, unique label id:"):
            obj = int(c.split(":")[1])
        elif c.startswith("stop printing object"):
            obj = -1
        continue
    code = line.split(";")[0].split()
    if not code:
        continue
    cmd = code[0]
    w = {}
    for t in code[1:]:
        if len(t) > 1 and re.fullmatch(r"[-+0-9.]+", t[1:]):
            w[t[0]] = float(t[1:])
    if cmd == "G29.1" and "Z" in w:
        trims.append(w["Z"])
    elif cmd in ("M106", "M107") and w.get("P", 1.0) == 1.0:
        fan = 0.0 if cmd == "M107" else w.get("S", 255.0)
    elif cmd in ("G90", "G91"):
        absolute = cmd == "G90"
    if cmd not in ("G0", "G1", "G2", "G3"):
        continue
    feed = w.get("F", feed)
    nxt = [w.get(k, pos[i]) if absolute else pos[i] + w.get(k, 0.0) for i, k in enumerate("XYZ")]
    length = ((nxt[0] - pos[0]) ** 2 + (nxt[1] - pos[1]) ** 2) ** 0.5
    if w.get("E", 0.0) > 0.0 and length > 1e-9 and obj != -1:
        for p in (pos, nxt):
            lo = [min(lo[0], p[0]), min(lo[1], p[1])]
            hi = [max(hi[0], p[0]), max(hi[1], p[1])]
        if obj == cooling["identify_id"] and feature in MODEL:
            mid = [0.5 * (pos[i] + nxt[i]) for i in range(3)]
            along = sum((mid[i] - origin[i]) * axis[i] for i in range(3))
            if span[0] <= along <= span[1]:
                row = stretch.setdefault(feature, [0.0, 0.0])
                seconds = length * 60.0 / feed if feed > 0 else 0.0
                row[0] += seconds
                row[1] += seconds if fan >= target - 1e-6 else 0.0
    pos = nxt

bed = prep["shared_printable_area_mm"]
margin = min(lo[0] - bed[0][0], lo[1] - bed[0][1], bed[1][0] - hi[0], bed[1][1] - hi[1])
review = {
    "purpose": purpose,
    "printer": prep["printer"],
    "archive": {
        "gcode_sha256": hashlib.sha256(raw).hexdigest(),
        "name": ready.name,
        "objects": [p["name"] for p in prep["parts"]],
        "sha256": hashlib.sha256(ready.read_bytes()).hexdigest(),
        "slots": {"1": {"colour": settings["filament_colour"][0].lstrip("#"), "type": settings["filament_type"][0]}},
    },
    "project": Path(prep["project"]).name,
    "project_sha256": prep["project_sha256"],
    "native_settings_sha256": prep["native_settings_sha256"],
    "finish_selection_sha256": prep["finish_selection_sha256"],
    "bed": settings["curr_bed_type"],
    "nozzle": {"side": "left" if settings["filament_nozzle_map"] == ["0"] else "right", "diameter_mm": float(settings["nozzle_diameter"][0])},
    "spool": {"colour": prep["filament_colour"], "external_spool": prep["external_spool"], "material": "Polymaker PET-GF"},
    "requested_z_trim_mm": prep["requested_z_trim_mm"],
    "emitted_z_trim_mm": trims[-1],
    "layer_count": int(re.search(r"^; total layer number: (\d+)", "\n".join(gcode[:400]), re.M)[1]),
    "predicted_seconds": result["total_predication"],
    "predicted_filament_g": round(result["filaments"][0]["total_used_g"], 2),
    "minimum_bead_edge_margin_mm": round(margin, 2),
    "extrusion_bounds_xy_mm": [[round(v, 3) for v in lo], [round(v, 3) for v in hi]],
    "tip_rim_contour_segments": rim["emitted_contact_segments"],
    "sloped_underside": {"record": "sloped-underside.json", "head_replay": "head-replay.json",
                         "preamble_seconds": staged["preamble"]["seconds"], "preamble_filament_mm": staged["preamble"]["filament_mm"],
                         "scope": "The slicer's predictions above are for the plate as sliced; the scaffold, roof and skin print before it."},
    "tip_end_cooling": {
        "fan_percent": cooling["fan_percent"],
        "back_from_dispense_face_mm": cooling["span_mm"],
        "cooled_moves": cooling["cooled_moves"],
        "cooled_path_mm": round(cooling["cooled_path_mm"], 1),
        "cooled_print_z_mm": [round(v, 2) for v in cooling["cooled_z_mm"]],
        "fan_commands_added": cooling["fan_commands_added"],
        "commanded_motion_seconds": round(cooling["cooled_commanded_motion_seconds"], 1),
        "of_which_cooled_as_sliced_seconds": round(cooling["already_cooled_commanded_motion_seconds"], 1),
        "emitted_seconds_by_feature": {
            k: {"motion": round(v[0], 1), "at_or_above_selected_fan": round(v[1], 1)} for k, v in sorted(stretch.items())
        },
        "scope": "Commanded motion read from the submitted G-code. The fan's own response time is not in it.",
    },
    "parts": [
        {k: p[k] for k in ("name", "source", "stl_sha256", "watertight", "rotation_x_degrees", "build_transform", "plate_bounds_mm") if k in p}
        for p in prep["parts"]
    ],
}
(trial / "slice-review.json").write_text(json.dumps(review, indent=1) + "\n")
print(json.dumps({k: v for k, v in review.items() if k != "parts"}, indent=1))
