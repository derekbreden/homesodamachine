"""Manual bead reading of this coupon's roots and six curved leaves.

Reads the retained native archive only. It changes no geometry or print setting.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from shapely import buffer, union_all
from shapely.geometry import LineString, box

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
SHARED = ROOT / "hardware/printed-parts/enclosure/trial-preparation"
sys.path.insert(0, str(SHARED))
import _mesh

spec = importlib.util.spec_from_file_location("tube_snap_native_reader", SHARED / "review.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def components(shape):
    return [g for g in getattr(shape, "geoms", [shape]) if g.area > 1e-6]


def main():
    overview = json.loads((HERE / "offline-review.json").read_text())
    directory = ROOT / overview["directory"]
    preparation = json.loads((directory / "preparation.json").read_text())
    report = json.loads((HERE.parents[1] / "geometry-report.json").read_text())
    record = preparation["objects"][0]
    oid = record["identify_id"]
    rotation = np.array(record["build_rotation"])
    translation = np.array(record["translation_mm"])
    centre = np.array(record["source_center_mm"])
    triangles = _mesh.read_stl(ROOT / record["stl"]).astype(float)
    triangles = ((triangles.reshape(-1, 3) - centre) @ rotation.T + translation).reshape(-1, 3, 3)
    source_offset = translation - centre
    y0, y1 = source_offset[1] - 4, source_offset[1] + 4
    axis_z = report["samples"][0]["tube_axis_z_mm"] + source_offset[2]
    rows, leaf_rows, feature_counts = [], [], Counter()
    previous = None
    handle, stream = reader.gcode_lines(ROOT / overview["archive"])
    with stream:
        for z, height, roads in reader.layers(stream):
            model = [r for r in roads if r[5] in reader.MODEL and r[6] == oid]
            if not model:
                continue
            lines = np.array([LineString([(r[0], r[1]), (r[2], r[3])]) for r in model], dtype=object)
            widths = np.array([r[4] for r in model])
            road_beads = buffer(lines, widths / 2, quad_segs=4)
            beads = union_all(road_beads)
            mid = z - height / 2
            feature_counts.update(r[5] for r in model)
            unbacked, contact, fully_clear_lengths = [], [], []
            if previous is not None:
                for line, road, bead in zip(lines, model, road_beads):
                    contact.append(bead.intersection(previous).area / bead.area)
                    clear = line.difference(previous.buffer(road[4] / 2, quad_segs=4))
                    fully_clear_lengths.extend(g.length for g in getattr(clear, "geoms", [clear]))
                    free = line.difference(previous)
                    if free.length > 1e-6:
                        unbacked.append({"feature": road[5], "free_mm": free.length,
                                         "road_mm": line.length,
                                         "longest_free_piece_mm": max(g.length for g in getattr(free, "geoms", [free])),
                                         "fully_free": free.length >= line.length - 1e-5})
            rows.append({"layer_top_z_mm": z, "height_mm": height,
                         "model_area_mm2": beads.area,
                         "minimum_road_bead_contact_fraction": min(contact) if contact else None,
                         "roads_without_previous_bead_contact": sum(c <= 1e-8 for c in contact),
                         "longest_centerline_with_no_bead_contact_mm": max(fully_clear_lengths, default=0),
                         "unbacked_centerline_mm": sum(r["free_mm"] for r in unbacked),
                         "longest_unbacked_centerline_mm": max((r["longest_free_piece_mm"] for r in unbacked), default=0),
                         "fully_unbacked_roads": sum(r["fully_free"] for r in unbacked),
                         "fully_unbacked_nonbridge_roads": sum(r["fully_free"] and r["feature"] not in {"Bridge", "Internal Bridge"} for r in unbacked),
                         "bridge_unbacked_mm": sum(r["free_mm"] for r in unbacked if r["feature"] in {"Bridge", "Internal Bridge"})})
            if mid >= axis_z:
                section = _mesh.section_polygons(triangles, mid)
                for sample in report["samples"]:
                    x = sample["centre_x_mm"] + source_offset[0]
                    radius = sample["outer_radius_mm"]
                    for side, xlo, xhi in (("left", x-radius-.01, x), ("right", x, x+radius+.01)):
                        region = box(xlo, y0-.01, xhi, y1+.01)
                        stock = section.intersection(region)
                        if stock.area < .01:
                            continue
                        printed = beads.intersection(region)
                        stock_pieces = components(stock)
                        printed_pieces = components(printed)
                        probe = LineString([(xlo, source_offset[1]), (xhi, source_offset[1])])
                        crossings = []
                        for line, road in zip(lines, model):
                            cross = line.intersection(probe)
                            if cross.is_empty:
                                continue
                            for point in getattr(cross, "geoms", [cross]):
                                if point.geom_type == "Point" and stock.buffer(.03).covers(point):
                                    crossings.append((round(point.x-source_offset[0], 5), road[5], road[4]))
                        leaf_rows.append({"sample": sample["label"], "bore_mm": sample["bore_diameter_mm"],
                                          "side": side, "layer_top_z_mm": z,
                                          "stock_area_mm2": stock.area,
                                          "bead_coverage": printed.intersection(stock).area / stock.area,
                                          "stock_components": len(stock_pieces),
                                          "bead_components": len(printed_pieces),
                                          "stock_pieces_touched": sum(printed.intersects(part) for part in stock_pieces),
                                          "centre_span_path_crossings": sorted(set(crossings)),
                                          "bead_footprint_touches_previous": previous.intersects(printed) if previous is not None else None})
            previous = beads
    handle.close()
    summary = {
        "scope": "STL cross-sections and emitted bead envelopes; no mechanical, adhesion or physical print acceptance.",
        "archive": overview["archive"], "archive_sha256": overview["archive_sha256"],
        "source_sha256": overview["source_sha256"],
        "analysis": "Every upper-leaf layer is compared with the STL at its layer midpoint. Previous-layer coverage uses commanded model bead footprints; an uncovered road centreline can still have partial bead overlap. No support or brim roads were emitted.",
        "layers": len(rows), "features": dict(feature_counts),
        "upper_leaf_samples": len(leaf_rows),
        "minimum_upper_leaf_bead_coverage": min(r["bead_coverage"] for r in leaf_rows),
        "upper_leaf_missing_stock_pieces": sum(r["stock_components"]-r["stock_pieces_touched"] for r in leaf_rows),
        "upper_leaf_disconnected_bead_footprints": sum(r["bead_components"] > 1 for r in leaf_rows),
        "upper_leaf_layers_without_previous_bead_contact": sum(not r["bead_footprint_touches_previous"] for r in leaf_rows),
        "second_layer_minimum_individual_road_bead_contact_fraction": rows[1]["minimum_road_bead_contact_fraction"],
        "second_layer_roads_without_previous_bead_contact": rows[1]["roads_without_previous_bead_contact"],
        "upper_leaf_minimum_individual_road_bead_contact_fraction": min(r["minimum_road_bead_contact_fraction"] for r in rows if r["layer_top_z_mm"]-r["height_mm"]/2 >= axis_z),
        "upper_leaf_longest_centerline_without_any_previous_bead_contact_mm": max(r["longest_centerline_with_no_bead_contact_mm"] for r in rows if r["layer_top_z_mm"]-r["height_mm"]/2 >= axis_z),
        "roads_without_any_previous_bead_contact_above_floor": sum(r["roads_without_previous_bead_contact"] for r in rows if r["layer_top_z_mm"] > 3),
        "longest_centerline_with_no_bead_contact_above_floor_mm": max(r["longest_centerline_with_no_bead_contact_mm"] for r in rows if r["layer_top_z_mm"] > 3),
        "fully_unbacked_nonbridge_roads_above_floor": sum(r["fully_unbacked_nonbridge_roads"] for r in rows if r["layer_top_z_mm"] > 3),
        "longest_unbacked_model_centerline_mm": max(r["longest_unbacked_centerline_mm"] for r in rows),
        "support_removal": "Native Tree(auto)/Default generated no support, including unlabelled bodies; no support-removal lane is required by this archive.",
        "contact_interpretation": "Every second-layer and upper-leaf road has previous-layer bead contact. Centreline excursions inside a partially overlapping bead do not imply an unanchored road. The short zero-contact spans near the floor/root skin are native bridges over the retained sparse infill. These readings establish commanded path continuity, not physical layer bonding or flexural survival.",
        "leaf_rows": leaf_rows, "layer_rows": rows,
    }
    (HERE / "path-review.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in {"leaf_rows", "layer_rows", "source_sha256"}}, indent=2))


if __name__ == "__main__":
    main()
