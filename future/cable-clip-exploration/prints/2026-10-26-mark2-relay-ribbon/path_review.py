"""Read native pocket clearance, bed islands and bridge paths. Offline only."""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from shapely import buffer, union_all
from shapely.geometry import LineString, Point, box

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
SHARED = ROOT / "hardware/printed-parts/enclosure/trial-preparation"
sys.path.insert(0, str(SHARED))
import _mesh

spec = importlib.util.spec_from_file_location("ribbon_native_paths", SHARED / "review.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def polygons(geometry):
    return [g for g in getattr(geometry, "geoms", [geometry]) if g.area > 1e-6]


def main():
    overview = json.loads((HERE / "offline-review.json").read_text())
    directory = ROOT / overview["directory"]
    preparation = json.loads((directory / "preparation.json").read_text())
    geometry = json.loads((HERE.parents[1] / "geometry-report.json").read_text())
    record = preparation["objects"][0]
    oid = record["identify_id"]
    rotation = np.array(record["build_rotation"])
    centre = np.array(record["source_center_mm"])
    translation = np.array(record["translation_mm"])
    if not np.allclose(rotation, np.eye(3), atol=1e-9):
        raise ValueError("This manual reading expects the source's already-posed STL, without additional turns")
    offset = translation - centre
    triangles = _mesh.read_stl(ROOT / record["stl"]).astype(float) + offset
    windows = []
    for label, key in (("cable seat", "print_pocket_bounds_mm"),
                       ("entry corridor", "print_entry_core_bounds_mm")):
        bounds = np.array(geometry[key]).reshape(2, 3) + offset
        windows.append({"name": label, "source_bounds_mm": geometry[key],
                        "plate_bounds_mm": bounds.tolist(), "support_crossings": [],
                        "brim_or_other_nonmodel_crossings": []})
    counts, first_two, bridge_layers, upper_arm = Counter(), [], [], []
    previous = None
    bridge_z = geometry["pocket_closure"]["build_z_mm"] + offset[2]
    gap = geometry["dimensions"]["seat_depth_mm"]
    bridge_footprint = box(offset[0], offset[1]-4, offset[0]+gap, offset[1]+4)
    arm_region = box(offset[0]+gap-1e-3, offset[1]-4.01, offset[0]+5.21, offset[1]+4.01)
    handle, stream = reader.gcode_lines(ROOT / overview["archive"])
    with stream:
        for z, height, roads in reader.layers(stream):
            counts.update(r[5] for r in roads)
            for window in windows:
                lo, hi = window["plate_bounds_mm"]
                if z-height >= hi[2]-1e-3 or z <= lo[2]+1e-3:
                    continue
                void = box(lo[0]+1e-3, lo[1]+1e-3, hi[0]-1e-3, hi[1]-1e-3)
                for a,b,c,d,w,f,o in roads:
                    if f in reader.MODEL:
                        continue
                    bead = LineString([(a,b),(c,d)]).buffer(w/2,quad_segs=4)
                    overlap = bead.intersection(void)
                    if overlap.area > 1e-6:
                        entry = {"layer_top_z_mm": z, "feature": f, "road_mm": [a,b,c,d,w],
                                 "bead_area_in_void_mm2": overlap.area}
                        target = "support_crossings" if f in reader.SUPPORT else "brim_or_other_nonmodel_crossings"
                        window[target].append(entry)
            own = [r for r in roads if r[5] in reader.MODEL and r[6] == oid]
            if not own:
                continue
            lines = np.array([LineString([(r[0],r[1]),(r[2],r[3])]) for r in own],dtype=object)
            beads_each = buffer(lines,np.array([r[4] for r in own])/2,quad_segs=4)
            beads = union_all(beads_each)
            mid = z-height/2
            if len(first_two) < 2:
                row = {"layer_top_z_mm": z, "height_mm": height,
                       "model_components": len(polygons(beads)),
                       "component_areas_mm2": sorted(g.area for g in polygons(beads))}
                if previous is not None:
                    contact = [g.intersection(previous).area/g.area for g in beads_each]
                    row.update(bead_area_fraction_over_first=beads.intersection(previous).area/beads.area,
                               minimum_individual_road_contact_fraction=min(contact),
                               roads_without_any_bead_contact=sum(c<1e-8 for c in contact),
                               longest_centerline_without_bead_contact_mm=max(
                                   (g.length for line,road in zip(lines,own)
                                    for g in getattr(line.difference(previous.buffer(road[4]/2,quad_segs=4)),"geoms",
                                                     [line.difference(previous.buffer(road[4]/2,quad_segs=4))])),default=0))
                first_two.append(row)
            if mid < bridge_z:
                stock = _mesh.section_polygons(triangles,mid).intersection(arm_region)
                printed = beads.intersection(arm_region)
                upper_arm.append({"layer_top_z_mm":z,"stock_area_mm2":stock.area,
                                  "bead_coverage":stock.intersection(printed).area/stock.area,
                                  "model_components":len(polygons(printed)),
                                  "previous_layer_contact":previous.intersects(printed) if previous is not None else None})
            if bridge_z <= mid < bridge_z+.6:
                crossing = []
                for road,line in zip(own,lines):
                    length = line.intersection(bridge_footprint).length
                    if length > .01:
                        crossing.append({"feature":road[5],"road_mm":list(road[:5]),
                                         "length_over_gap_mm":length,
                                         "endpoint_bead_contacts_previous":[
                                             previous.intersects(Point(road[0],road[1]).buffer(road[4]/2)),
                                             previous.intersects(Point(road[2],road[3]).buffer(road[4]/2))]})
                bridge_layers.append({"layer_top_z_mm":z,"height_mm":height,
                                      "gap_footprint_bead_coverage":beads.intersection(bridge_footprint).area/bridge_footprint.area,
                                      "crossing_roads":crossing})
            previous = beads
    handle.close()
    result = {
        "scope":"Manual reading of commanded paths and bead envelopes. Adhesion, bridge finish, release, layer bonding and cable grip remain physical observations.",
        "archive":overview["archive"],"archive_sha256":overview["archive_sha256"],
        "source_sha256":overview["source_sha256"],"features":dict(counts),
        "voids":windows,
        "no_support_in_seat_or_entry":not any(w["support_crossings"] for w in windows),
        "no_brim_or_other_nonmodel_in_seat_or_entry":not any(w["brim_or_other_nonmodel_crossings"] for w in windows),
        "first_two_model_layers":first_two,
        "outer_arm_below_bridge":{
            "sampled_layers":len(upper_arm),
            "minimum_model_section_bead_coverage":min(r["bead_coverage"] for r in upper_arm),
            "layers_with_multiple_bead_islands":sum(r["model_components"]>1 for r in upper_arm),
            "layers_without_previous_model_contact_above_first":sum(r["previous_layer_contact"] is False for r in upper_arm),
            "layers":upper_arm},
        "pocket_closure_bridge_layers":bridge_layers,
        "interpretation":"The two bed islands belong to one native solid joined above the open pocket. Retain automatic supports; inspect emitted support and brim within the two source-bound voids. A road-centreline excursion alone does not imply loss of bead contact.",
    }
    (HERE/"path-review.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"source_sha256","voids","pocket_closure_bridge_layers","outer_arm_below_bridge"}},indent=2))
    print(json.dumps({"void_crossing_counts":[{w["name"]:{k:len(w[k]) for k in ["support_crossings","brim_or_other_nonmodel_crossings"]}} for w in windows],
                      "arm":{k:v for k,v in result["outer_arm_below_bridge"].items() if k!="layers"},
                      "bridge_layers":[{k:v for k,v in r.items() if k!="crossing_roads"} for r in bridge_layers]},indent=2))


if __name__ == "__main__":
    main()
