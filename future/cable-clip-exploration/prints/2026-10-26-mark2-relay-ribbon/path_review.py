"""Read the upright coupon's native pocket, footprint and corbel paths. Offline only."""
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
    if not np.allclose(record["build_rotation"], np.eye(3), atol=1e-9):
        raise ValueError("The upright source STL must have no additional rotation")
    offset = np.array(record["translation_mm"]) - np.array(record["source_center_mm"])
    triangles = _mesh.read_stl(ROOT / record["stl"]).astype(float) + offset
    windows = []
    for label, key in (("cable seat", "print_pocket_bounds_mm"),
                       ("entry corridor", "print_entry_core_bounds_mm")):
        bounds = np.array(geometry[key]).reshape(2, 3) + offset
        windows.append({"name": label, "source_bounds_mm": geometry[key],
                        "plate_bounds_mm": bounds.tolist(), "support_crossings": [],
                        "brim_or_other_nonmodel_crossings": []})
    counts, first_two, arm_layers, lip_layers = Counter(), [], [], []
    previous = None
    arm_region = box(offset[0]+1e-3,offset[1]-4.001,offset[0]+5.201,offset[1]+4.001)
    corbel_start = geometry["corbel"]["build_start_z_mm"]+offset[2]
    lip_z = geometry["retaining_lip"]["build_underside_z_mm"]+offset[2]
    handle, stream = reader.gcode_lines(ROOT / overview["archive"])
    with stream:
        for z, height, roads in reader.layers(stream):
            counts.update(r[5] for r in roads)
            for window in windows:
                lo, hi = window["plate_bounds_mm"]
                if z-height >= hi[2]-1e-3 or z <= lo[2]+1e-3:
                    continue
                void = box(lo[0]+1e-3,lo[1]+1e-3,hi[0]-1e-3,hi[1]-1e-3)
                for a,b,c,d,w,f,o in roads:
                    if f in reader.MODEL:
                        continue
                    overlap = LineString([(a,b),(c,d)]).buffer(w/2,quad_segs=4).intersection(void)
                    if overlap.area > 1e-6:
                        target = "support_crossings" if f in reader.SUPPORT else "brim_or_other_nonmodel_crossings"
                        window[target].append({"layer_top_z_mm":z,"feature":f,
                            "road_mm":[a,b,c,d,w],"bead_area_in_void_mm2":overlap.area})
            own = [r for r in roads if r[5] in reader.MODEL and r[6] == oid]
            if not own:
                continue
            lines = np.array([LineString([(r[0],r[1]),(r[2],r[3])]) for r in own],dtype=object)
            beads_each = buffer(lines,np.array([r[4] for r in own])/2,quad_segs=4)
            beads = union_all(beads_each)
            mid = z-height/2
            if len(first_two)<2:
                row = {"layer_top_z_mm":z,"height_mm":height,
                       "model_components":len(polygons(beads)),
                       "component_areas_mm2":sorted(g.area for g in polygons(beads))}
                if previous is not None:
                    contact = [g.intersection(previous).area/g.area for g in beads_each]
                    row.update(bead_area_fraction_over_first=beads.intersection(previous).area/beads.area,
                               minimum_individual_road_contact_fraction=min(contact),
                               roads_without_any_bead_contact=sum(c<1e-8 for c in contact))
                first_two.append(row)
            if mid>corbel_start:
                stock = _mesh.section_polygons(triangles,mid).intersection(arm_region)
                if stock.area>1e-5:
                    printed = beads.intersection(arm_region)
                    components = [g for g in polygons(beads) if g.intersects(printed)]
                    arm_layers.append({"layer_top_z_mm":z,"stock_area_mm2":stock.area,
                        "bead_coverage":stock.intersection(printed).area/stock.area,
                        "model_components":len(polygons(printed)),
                        "previous_model_contact":bool(components) and all(
                            g.intersects(previous) for g in components)})
            if lip_z<=mid<lip_z+.6:
                lip_layers.append({"layer_top_z_mm":z,"features":dict(Counter(r[5] for r in own)),
                    "roads":[list(r[:6]) for r in own if min(r[0],r[2])<offset[0]+2.2
                             and max(r[0],r[2])>offset[0]+1.45]})
            previous = beads
    handle.close()
    no_support = not any(w["support_crossings"] for w in windows)
    no_other = not any(w["brim_or_other_nonmodel_crossings"] for w in windows)
    brim_roads = sum(n for f,n in counts.items() if "brim" in f.lower() or "skirt" in f.lower())
    summary = {"sampled_layers":len(arm_layers),
        "minimum_model_section_bead_coverage":min(r["bead_coverage"] for r in arm_layers),
        "layers_without_previous_model_contact":sum(not r["previous_model_contact"] for r in arm_layers),
        "layers":arm_layers}
    result = dict(
        scope="Manual native bead reading of the upright fit coupon. Physical adhesion, ribbon grip and surface finish remain untested.",
        archive=overview["archive"],archive_sha256=overview["archive_sha256"],
        source_sha256=overview["source_sha256"],features=dict(counts),voids=windows,
        no_support_in_seat_or_entry=no_support,no_nonmodel_in_seat_or_entry=no_other,
        no_brim=brim_roads==0,first_two_model_layers=first_two,hook_layers=summary,
        retaining_lip_layers=lip_layers,
        interpretation="A single 24 by 3 mm wall footprint starts on the bed. The hook grows from the wall on its 45 degree corbel beginning at Z6 mm. Hook contact follows each complete connected bead section through its wall attachment, including the first corbel layer. The 0.75 mm retaining lip keeps its flat underside. Tree(auto)/Default remains enabled; no brim is requested.")
    result["pass"] = (overview["native_review_pass"] and no_support and no_other and brim_roads==0
        and len(first_two)==2 and all(r["model_components"]==1 for r in first_two)
        and first_two[1]["roads_without_any_bead_contact"]==0
        and summary["layers_without_previous_model_contact"]==0)
    (HERE/"path-review.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"source_sha256","voids","hook_layers","retaining_lip_layers"}},indent=2))
    print(json.dumps({"hook":{k:v for k,v in summary.items() if k!="layers"},
                     "void_crossing_counts":[{w["name"]:{k:len(w[k]) for k in
                         ["support_crossings","brim_or_other_nonmodel_crossings"]}} for w in windows]},indent=2))
    if not result["pass"]:
        raise ValueError("The upright coupon needs review before submission")


if __name__ == "__main__":
    main()
