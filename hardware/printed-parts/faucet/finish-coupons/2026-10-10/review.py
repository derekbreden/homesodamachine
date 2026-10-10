"""Manual reading of the exact native coupon plate, after finish.py."""
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import json
import math
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
WORK = ROOT / ".cache/printer-control/faucet-finish-coupons-20261010"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from enclosure_support_audit import _WORD
from verify_round_layer_band import wall_layers, check_span


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pure_reader(file, name):
    # Read the existing G-code methods without importing faucet CAD builders.
    tree = ast.parse(file.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    env = dict(Path=Path, np=np, sys=sys, re=re, math=math, writer=SimpleNamespace(ROOT=ROOT))
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(file), "exec"), env)
    return env[name]


def transform(points, text):
    tf = np.array([float(x) for x in text.split()]).reshape(4, 3)
    return points @ tf[:3] + tf[3]


def main():
    prep = json.loads((HERE / "preparation.json").read_text())
    native, project = ROOT / prep["native_archive"], ROOT / prep["project"]
    assert sha(native) == prep["native_archive_sha256"]
    assert sha(project) == prep["project_sha256"]
    assert sha(ROOT / prep["source_step"]) == prep["source_step_sha256"]
    assert sha(ROOT / prep["source_stl"]) == prep["source_stl_sha256"]
    assert sha(ROOT / prep["shipping_reference"]) == prep["shipping_reference_sha256"]
    geometry = []
    with zipfile.ZipFile(native) as arc, zipfile.ZipFile(project) as source:
        assert arc.testzip() is None
        payload = arc.read("Metadata/plate_1.gcode")
        assert hashlib.sha256(payload).hexdigest() == prep["gcode_sha256"]
        assert arc.read("Metadata/plate_1.gcode.md5").decode().strip().lower() == hashlib.md5(payload).hexdigest()
        gcode = payload.decode()
        (WORK / "final.gcode").write_bytes(payload)
        for member, target in (("Metadata/plate_1.png", "native-preview.png"), ("Metadata/top_1.png", "native-top.png")):
            (HERE / target).write_bytes(arc.read(member))
        settings = json.loads(arc.read("Metadata/project_settings.config"))
        expected = json.loads(source.read("Metadata/project_settings.config"))
        normalizations = {k: [expected.get(k), settings.get(k)] for k in set(expected) | set(settings)
                          if expected.get(k) != settings.get(k)}
        allowed = {"filament_prime_volume": [["30"], ["45"]], "filament_map_2": [None, ["1"]]}
        assert all(k in allowed and v == allowed[k] for k,v in normalizations.items()), normalizations
        assert settings["curr_bed_type"] == "Textured PEI Plate"
        assert settings["support_type"] == "tree(auto)" and settings["support_style"] == "default"
        assert settings["support_top_z_distance"] == "0.45"
        assert settings["enable_wrapping_detection"] == "0" and settings["wrapping_detection_gcode"] == ""
        assert not re.search(r"^\s*G39(?:\s|;|$)", gcode, re.M)
        trims = [float(x) for x in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
        # Native startup clears the previous trim, then applies the plate trim.
        assert trims == [0., .02], trims
        cfg = ET.fromstring(arc.read("Metadata/model_settings.config"))
        assert not cfg.findall(".//part[@subtype='negative_part']")
        objects = {next(m.get("value") for m in o.findall("metadata") if m.get("key") == "name"):o
                   for o in cfg.findall("object")}
        assert set(objects) == {s["name"] for s in prep["specimens"]}
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        prod = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
        model = ET.fromstring(arc.read("3D/3dmodel.model"))
        resources = {o.get("id"):o for o in model.findall("m:resources/m:object",ns)}
        builds = {b.get("objectid"):b for b in model.findall("m:build/m:item",ns)}
        for part, specimen in zip(prep["parts"],prep["specimens"], strict=True):
            stl = ROOT / part["source"]
            assert sha(stl) == part["stl_sha256"]
            mesh = trimesh.load(stl, force="mesh", process=True)
            obj = objects[part["name"]]
            meta = {m.get("key"):m.get("value") for m in obj.findall("metadata")}
            for k,v in specimen["object_overrides"].items(): assert meta[k] == v
            modifiers = obj.findall("part[@subtype='modifier_part']")
            assert len(modifiers) == (1 if specimen["kind"] == "foot" else 0)
            if modifiers:
                fields = {m.get("key"):m.get("value") for m in modifiers[0].findall("metadata")}
                assert fields["wall_loops"] == "6" and fields["sparse_infill_density"] == "100%"
            normal = obj.find("part[@subtype='normal_part']")
            component = next(c for c in resources[obj.get("id")].findall("m:components/m:component",ns)
                             if c.get("objectid") == normal.get("id"))
            child = ET.fromstring(arc.read(component.get("{"+prod+"}path").lstrip("/")))
            geo = child.find("m:resources/m:object[@id='"+normal.get("id")+"']/m:mesh",ns)
            vertices = np.array([[float(v.get(a)) for a in "xyz"] for v in geo.find("m:vertices",ns)])
            faces = np.array([[int(v.get(a)) for a in ("v1","v2","v3")] for v in geo.find("m:triangles",ns)])
            assert np.array_equal(faces,mesh.faces)
            placed = transform(transform(vertices,component.get("transform","1 0 0 0 1 0 0 0 1 0 0 0")),builds[obj.get("id")].get("transform"))
            target = transform(mesh.vertices-np.array(part["source_center_mm"])," ".join(map(str,part["build_transform"])))
            error = float(np.abs(placed-target).max())
            assert error < 1e-4, (part["name"], error)
            geometry.append(dict(name=part["name"], native_vertex_rounding_maximum_mm=error,
                                 triangle_indices_identical=True, source_stl_sha256=sha(stl)))

    native_result = json.loads((WORK / "result.json").read_text())
    assert native_result["return_code"] == 0 and len(native_result["sliced_plates"]) == 1
    plate = native_result["sliced_plates"][0]
    assert not plate["warning_message"]
    layer_checks = []
    for specimen in prep["specimens"]:
        layers = wall_layers(native,specimen["identify_id"])
        lo,hi = specimen["layer_band_print_z_mm"]
        reading = check_span(layers,specimen["name"],lo,hi,specimen["fine_layer_height_mm"],.001)
        assert reading["pass"],reading
        layer_checks.append(reading)
    bounds_reader = pure_reader(ROOT/"hardware/printed-parts/faucet/refresh_print_project.py","object_toolpaths")
    bounds = bounds_reader(WORK/"final.gcode",WORK/"all-layer-beads.gcode",None)
    lo, hi = np.array(bounds["extrusion_bounds_xy_mm"])
    margin = float(min(np.min(lo),np.min(np.array([325,320])-hi)))
    assert margin >= 40, bounds

    segment_reader = pure_reader(ROOT/"hardware/printed-parts/faucet/prepare_display_print.py","extrusion_segments")
    first, second = defaultdict(list),defaultdict(list)
    support_count=defaultdict(int)
    ramps=defaultdict(list)
    for segment in segment_reader(WORK/"final.gcode"):
        oid,z,kind=segment["object"],segment["layer"],segment["feature"]
        if kind.startswith("Support"):support_count[oid]+=1
        if abs(z-.2)<1e-5 or abs(z-.44)<1e-5:
            bead=LineString([segment["a"][:2],segment["b"][:2]]).buffer(segment["width"]/2,quad_segs=4)
            if abs(z-.2)<1e-5:first[oid].append(bead)
            elif kind in ("Outer wall","Inner wall","Overhang wall"):second[oid].append(bead)
        if oid>=1904 and 16.04<z<=35.24 and kind=="Outer wall":
            if abs(segment["a"][2]-z)>1e-5 or abs(segment["b"][2]-z)>1e-5:
                ramps[oid].append([z,segment["a"][2],segment["b"][2]])
    first_second=[]
    fig,ax=plt.subplots(figsize=(10,7))
    colors=dict(zip(range(1901,1907),("#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f","#b07aa1")))
    for specimen in prep["specimens"]:
        oid=specimen["identify_id"]
        bed=unary_union(first[oid]); walls=unary_union(second[oid])
        assert not bed.is_empty and not walls.is_empty
        overlap=[bead.intersection(bed).area/bead.area for bead in second[oid]]
        first_second.append(dict(id=specimen["id"],second_wall_segments=len(overlap),
                                 no_first_layer_overlap_segments=sum(a<=1e-9 for a in overlap),
                                 minimum_segment_overlap_fraction=min(overlap),
                                 total_second_wall_footprint_overlap_fraction=walls.intersection(bed).area/walls.area))
        polygons=list(bed.geoms) if hasattr(bed,"geoms") else [bed]
        for polygon in polygons:
            x,y=polygon.exterior.xy;ax.fill(x,y,color=colors[oid],alpha=.65)
            for hole in polygon.interiors:
                x,y=hole.xy;ax.fill(x,y,color="white")
        x=(specimen["plate_bounds_mm"][0][0]+specimen["plate_bounds_mm"][1][0])/2
        y=specimen["plate_bounds_mm"][1][1]+5
        ax.text(x,y,specimen["id"],ha="center",weight="bold",fontsize=14)
    assert not ramps[1904], "Regular seam unexpectedly ramps outer wall Z"
    assert ramps[1905] and ramps[1906], "Scarf specimens lack emitted outer-wall Z ramps"
    ax.plot([40,285,285,40,40],[40,40,280,280,40],"k--",lw=1,label="40 mm inset")
    ax.set(xlim=(0,325),ylim=(0,320),xlabel="Printer X (mm)",ylabel="Printer Y (mm)",
           title="Native first-layer beads, including support and brim; front is bottom")
    ax.set_aspect("equal");ax.legend(loc="lower right");fig.tight_layout()
    fig.savefig(HERE/"plate-layout.png",dpi=150);plt.close(fig)
    report=dict(schema=1,archive=prep["native_archive"],archive_sha256=sha(native),gcode_sha256=prep["gcode_sha256"],
                prepared_project=prep["project"],prepared_project_sha256=sha(project),geometry=geometry,
                native_settings_normalizations=normalizations,layer_band_checks=layer_checks,
                complete_model_support_brim_bead_bounds=bounds,minimum_full_bead_bed_margin_mm=margin,
                first_second_layer_overlap=first_second,support_deposition_segment_counts=dict(support_count),
                fine_outer_wall_scarf_Z_ramp_segments={str(k):len(v) for k,v in ramps.items()},
                scarf_witnesses={str(k):v[:10] for k,v in ramps.items()},
                requested_Z_trim_mm=.04,emitted_Z_trim_commands_mm=trims,probing_clump_detection=False,
                native_estimated_seconds=plate["total_predication"],
                native_estimated_grams_saved_profile_density=sum(f["total_used_g"] for f in plate["filaments"]),
                scope="Commanded geometry, layer heights, bead footprints and scarf ramps; physical lifting, seam quality, adhesion and support release remain unevaluated.",
                **{"pass":True})
    (HERE/"native-check.json").write_text(json.dumps(report,indent=2)+"\n")
    shutil.copyfile(WORK/"result.json",HERE/"native-result.json")
    shutil.copyfile(WORK/"live-geometry-review.json",HERE/"live-geometry-review.json")
    print(json.dumps(dict(margin_mm=margin,estimated_seconds=report["native_estimated_seconds"],
                          layers=[r["pass"] for r in layer_checks],scarf_ramps=report["fine_outer_wall_scarf_Z_ramp_segments"],
                          first_second=first_second),indent=2),flush=True)


if __name__ == "__main__":
    main()
