"""Read this experiment's native paths by hand. No build or commit integration."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import zipfile

import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools/gcode"))
from toolpaths import WORD, arc
from build import STEM


def segments(text):
    pos = np.zeros(3)
    obj, feature, z, height, width = None, "", None, 0.24, 0.42
    relative_e, absolute_xyz, e_pos, feed = True, True, 0.0, 0.0
    part_fan = 0
    out = []
    for number, raw in enumerate(text.splitlines(), 1):
        if raw.startswith(";"):
            s = raw[1:].strip()
            if s.startswith("Z_HEIGHT:"):
                z = float(s.split(":", 1)[1])
            elif s.startswith("LAYER_HEIGHT:"):
                height = float(s.split(":", 1)[1])
            elif s.startswith("LINE_WIDTH:"):
                width = float(s.split(":", 1)[1])
            elif s.startswith("FEATURE:"):
                feature = s.split(":", 1)[1].strip()
            elif s.startswith("OBJECT_ID:"):
                obj = int(s.split(":", 1)[1])
            elif s.startswith("start printing object, unique label id:"):
                obj = int(s.rsplit(":", 1)[1])
            elif s.startswith("stop printing object"):
                obj = None
            continue
        code = raw.split(";", 1)[0].strip()
        if not code:
            continue
        cmd = code.split(None, 1)[0]
        words = {k: float(v) for k, v in WORD.findall(code[len(cmd):])}
        if cmd in ("G90", "G91"):
            absolute_xyz = cmd == "G90"
        elif cmd in ("M82", "M83"):
            relative_e = cmd == "M83"
        elif cmd == "M106" and words.get("P", 1) == 1:
            part_fan = words.get("S", 255)
        elif cmd == "G92":
            for i, k in enumerate("XYZ"):
                if k in words:
                    pos[i] = words[k]
            e_pos = words.get("E", e_pos)
        elif cmd in ("G0", "G1", "G2", "G3"):
            feed = words.get("F", feed * 60) / 60
            nxt = pos.copy()
            for i, k in enumerate("XYZ"):
                if k in words:
                    nxt[i] = words[k] if absolute_xyz else pos[i] + words[k]
            de = 0
            if "E" in words:
                de = words["E"] if relative_e else words["E"] - e_pos
                e_pos = e_pos + words["E"] if relative_e else words["E"]
            if obj is not None and z is not None and de > 0 and np.linalg.norm(nxt[:2] - pos[:2]) > 1e-8:
                points = [tuple(pos)] + (arc(pos, nxt, words, cmd == "G2", chord=.02)
                                          if cmd in ("G2", "G3") else [tuple(nxt)])
                for a, b in zip(points, points[1:]):
                    out.append({"a": np.array(a), "b": np.array(b), "object": obj,
                                "feature": feature, "z": z, "height": height,
                                "width": width, "speed": feed, "fan": part_fan,
                                "line": number})
            pos = nxt
    return out


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    archive = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / f"{STEM}.gcode.3mf"
    spec = json.loads((HERE / f"{STEM}.print.json").read_text())
    with zipfile.ZipFile(archive) as z:
        raw = z.read("Metadata/plate_1.gcode")
        checksum = z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        settings = json.loads(z.read("Metadata/project_settings.config"))
    text = raw.decode()
    paths = segments(text)
    lo, hi = np.full(2, np.inf), np.full(2, -np.inf)
    for p in paths:
        xy = np.array([p["a"][:2], p["b"][:2]])
        lo = np.minimum(lo, xy.min(axis=0) - p["width"] / 2)
        hi = np.maximum(hi, xy.max(axis=0) + p["width"] / 2)
    rows = []
    for part in spec["parts"]:
        own = [p for p in paths if p["object"] == part["identify_id"]]
        first = [p for p in own if math.isclose(p["z"], .2, abs_tol=1e-4)]
        footprint = unary_union([LineString([p["a"][:2], p["b"][:2]]).buffer(
            p["width"] / 2, quad_segs=12) for p in first])
        components = list(footprint.geoms) if footprint.geom_type == "MultiPolygon" else [footprint]
        # Tiny numerical seams between adjacent native beads are joined for component count.
        joined = footprint.buffer(.005).buffer(-.005)
        joined_components = list(joined.geoms) if joined.geom_type == "MultiPolygon" else [joined]
        row = {"id": part["id"], "deposited_segments": len(own),
               "bed_foot_components": len(joined_components),
               "bed_foot_separation_mm": (min(a.distance(b) for i, a in enumerate(joined_components)
                    for b in joined_components[i + 1:]) if len(joined_components) > 1 else None)}
        if part["kind"] == "fin_bridge":
            layer = [p for p in own if abs(p["z"] - part["first_shelf_nozzle_z_mm"]) < 1e-4]
            axis = 0 if part["bridge_axis"] == "X" else 1
            cross_axis = 1 - axis
            trans = np.array(part["plate_translation_mm"])
            shelf_lo, shelf_hi = np.asarray(part["shelf_bounds_local_mm"]) + trans
            clear_lo, clear_hi = np.asarray(part["clear_span_bounds_local_mm"]) + trans[axis]
            bridge = [p for p in layer if p["feature"] == "Bridge"
                      and abs(p["a"][cross_axis] - p["b"][cross_axis]) < .005
                      and shelf_lo[cross_axis] <= (p["a"][cross_axis] + p["b"][cross_axis]) / 2 <= shelf_hi[cross_axis]
                      # Native infill anchors into the shelf's perimeter beads;
                      # their centerlines shorten the raster relative to clear air.
                      and min(p["a"][axis], p["b"][axis]) < clear_lo + .55
                      and max(p["a"][axis], p["b"][axis]) > clear_hi - .55]
            contact_layers = []
            gap = part["horizontal_body_gap_mm"]
            intervals = ((shelf_lo[axis] - gap, shelf_lo[axis]),
                         (shelf_hi[axis], shelf_hi[axis] + gap))
            tooth_zs = (part["first_tooth_nozzle_z_mm"],
                        part["shelf_bottom_z_mm"] + .72,
                        part["shelf_bottom_z_mm"] + 1.44)
            for tooth_z in tooth_zs:
                tooth_layer = [p for p in own if abs(p["z"] - tooth_z) < 1e-4]
                footprint_at_z = unary_union([LineString([p["a"][:2], p["b"][:2]]).buffer(
                    p["width"] / 2, quad_segs=12) for p in tooth_layer])
                # A feed/feature change can split a continuous bead at the gap.
                # Test the deposited footprint across each intended contact,
                # rather than demanding one G1 command cross the entire gap.
                positions = np.linspace(1, 11, 7) if tooth_z == tooth_zs[0] else (2, 6, 10)
                side_counts = []
                for side, (a0, a1) in enumerate(intervals):
                    count = 0
                    for y in positions:
                        cross_coordinate = (y if axis == 0 else -y) + trans[cross_axis]
                        v0, v1 = np.zeros(2), np.zeros(2)
                        underlap = part["lower_tooth_underlap_mm"] if tooth_z == tooth_zs[0] else .005
                        v0[axis] = a0 - (underlap if side else 0)
                        v1[axis] = a1 + (underlap if not side else 0)
                        v0[cross_axis] = v1[cross_axis] = cross_coordinate
                        probe = LineString([v0, v1])
                        if probe.difference(footprint_at_z.buffer(.001)).length < .005:
                            count += 1
                    side_counts.append(count)
                contact_layers.append({"nozzle_z_mm": tooth_z,
                                       "continuous_contact_footprints_per_side": side_counts,
                                       "extrusion_height_mm": sorted({round(p["height"], 4) for p in tooth_layer})})
            row.update(first_shelf_layer_z_mm=part["first_shelf_nozzle_z_mm"],
                       axial_bridge_moves=len(bridge), bridge_axis=part["bridge_axis"],
                       native_bridge_move_length_mm=sorted({round(abs(p["a"][axis] - p["b"][axis]), 4) for p in bridge}),
                       native_bridge_speed_mm_s=sorted({round(p["speed"], 4) for p in bridge}),
                       native_bridge_width_mm=sorted({round(p["width"], 4) for p in bridge}),
                       native_bridge_height_mm=sorted({round(p["height"], 4) for p in bridge}),
                       native_bridge_fan_command=sorted({p["fan"] for p in bridge}),
                       fin_contact_layers=contact_layers)
        if part["kind"] == "tine_release":
            trans = np.array(part["plate_translation_mm"])
            gaps = []
            for z0, z1 in part["tine_z_intervals_mm"]:
                crossing = [p for p in own if abs(p["z"] - z1) < 1e-4
                            and min(p["a"][0], p["b"][0]) <= trans[0] + 3.02
                            and max(p["a"][0], p["b"][0]) >= trans[0] + 3.22
                            and abs((p["a"][1] + p["b"][1]) / 2 - trans[1] - 6) < .5]
                gaps.append({"nozzle_z_mm": z1, "crossing_moves": len(crossing),
                             "height_mm": sorted({round(p["height"], 4) for p in crossing}),
                             "width_mm": sorted({round(p["width"], 4) for p in crossing})})
            row["tine_gap_crossings"] = gaps
        rows.append(row)
    requested_keys = ("enable_support", "brim_type", "layer_height", "initial_layer_print_height",
                      "filament_type", "filament_colour", "filament_density", "filament_map",
                      "filament_nozzle_map", "nozzle_diameter", "nozzle_volume_type", "curr_bed_type",
                      "nozzle_temperature", "nozzle_temperature_initial_layer", "fan_min_speed",
                      "fan_max_speed", "overhang_fan_speed", "bridge_speed", "filament_bridge_speed")
    review = {"native_archive": archive.name, "native_archive_sha256": sha(archive),
              "gcode_sha256": hashlib.sha256(raw).hexdigest(),
              "embedded_md5_matches": hashlib.md5(raw).hexdigest() == checksum,
              "trim_commands": re.findall(r"^\s*G29\.1[^\n]*", text, re.M),
              "effective_settings": {k: settings.get(k) for k in requested_keys},
              "support_extrusion_segments": sum(p["feature"].startswith("Support") for p in paths),
              "model_full_bead_xy_bounds_mm": [lo.tolist(), hi.tolist()],
              "model_bead_min_edge_inset_mm": float(min(lo[0], lo[1], 325 - hi[0], 320 - hi[1])),
              "extrusion_heights_mm": sorted({round(p["height"], 3) for p in paths}),
              "layer_z_steps_mm": sorted({round(b-a, 3) for a, b in zip(
                  sorted({p["z"] for p in paths}), sorted({p["z"] for p in paths})[1:])}),
              "specimens": rows,
              "limits": "Commanded bead envelopes include width and arcs, not physical squish or sag. Physical results pending."}
    (HERE / "native-review.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps({"checksum_ok": review["embedded_md5_matches"],
                      "edge_inset_mm": review["model_bead_min_edge_inset_mm"],
                      "support_segments": review["support_extrusion_segments"],
                      "bridges": [{"id": r["id"], "moves": r.get("axial_bridge_moves"),
                                   "speed": r.get("native_bridge_speed_mm_s")}
                                  for r in rows if "axial_bridge_moves" in r],
                      "tines": [r for r in rows if "tine_gap_crossings" in r],
                      "bed_components": {r["id"]: r["bed_foot_components"] for r in rows}}))
    render_bridge_layer(paths, spec)


def render_bridge_layer(paths, spec):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=160)
    for ax, name in zip(axes, ("A12", "Y12")):
        part = next(r for r in spec["parts"] if r["id"] == name)
        chosen = [p for p in paths if p["object"] == part["identify_id"]
                  and abs(p["z"] - part["first_shelf_nozzle_z_mm"]) < 1e-4]
        for feature, colour in (("Bridge", "#168db3"), ("Outer wall", "#b77a39"),
                                ("Inner wall", "#777777"), ("Gap infill", "#b98ba5")):
            lines = [[p["a"][:2], p["b"][:2]] for p in chosen if p["feature"] == feature]
            ax.add_collection(LineCollection(lines, colors=colour, linewidths=1.5, label=feature))
        lo, hi = np.asarray(part["plate_bounds_mm"])
        ax.set(xlim=(lo[0] - 1, hi[0] + 1), ylim=(lo[1] - 1, hi[1] + 1),
               xlabel="Bed X (mm)", ylabel="Bed Y (mm)")
        ax.set_aspect("equal")
        ax.set_title(f"{name} · first shelf layer at Z10.52")
        ax.grid(alpha=.12)
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.05, 1), fontsize=9)
    fig.tight_layout()
    fig.savefig(HERE / "native-bridge-paths.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
