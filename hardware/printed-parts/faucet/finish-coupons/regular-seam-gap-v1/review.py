"""Manually inspect this ordinary-seam-only native plate; never send a print."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
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
FAUCET = ROOT / "hardware/printed-parts/faucet"
WORK = ROOT / ".cache/printer-control/faucet-regular-seam-gap-v1-20261011"
sys.path[:0] = [str(FAUCET), str(ROOT / "hardware/scripts")]
import prepare_vent_prints as prep
from prepare_display_print import extrusion_segments


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, d):
    p.write_text(json.dumps(d, indent=2) + "\n")


def transform(vertices, value):
    tf = np.array([float(x) for x in value.split()]).reshape(4, 3)
    return vertices @ tf[:3] + tf[3]


def main():
    for name in ("launch-plan.json", "launch.json"):
        if (HERE / name).exists():
            d = json.loads((HERE / name).read_text())
            assert not any(d.get(k) for k in ("import_attempted", "send_attempted", "accepted"))
    report = json.loads((HERE / "preparation.json").read_text())
    prep.verify_sources(report)
    project = ROOT / report["project"]
    assert sha(project) == report["project_sha256"]
    native = WORK / (project.stem + ".gcode.3mf")
    validation = prep.native_validation(native, project, report, WORK)
    assert 30*60 <= validation["estimated_seconds"] <= 120*60
    geometry = []
    core = {"m": prep.writer.CORE}
    prod = prep.writer.PROD
    with zipfile.ZipFile(native) as arc, zipfile.ZipFile(project) as prepared, zipfile.ZipFile(ROOT / report["settings_source"]) as defaults:
        original = json.loads(defaults.read(prep.writer.SETTINGS_MEMBER))
        expected = json.loads(prepared.read(prep.writer.SETTINGS_MEMBER))
        delta = {k for k in set(original) | set(expected) if original.get(k) != expected.get(k)}
        assert delta <= {"machine_start_gcode", "printer_settings_id", "filament_colour"}
        for member in defaults.namelist():
            if member.startswith("Metadata/filament_settings_"):
                assert defaults.read(member) == prepared.read(member) == arc.read(member)
        assert original["seam_position"] == expected["seam_position"] == "aligned"
        assert expected["seam_slope_type"] == "none" and expected["filament_scarf_seam_type"] == ["none"]
        assert expected["override_filament_scarf_seam_setting"] == "0"
        assert expected["enable_wrapping_detection"] == "0"
        assert not any(n.startswith("Metadata/layer_config_ranges") for n in prepared.namelist())
        if "Metadata/layer_config_ranges.xml" in arc.namelist():
            assert not ET.fromstring(arc.read("Metadata/layer_config_ranges.xml")).findall("object")
        model = ET.fromstring(arc.read("3D/3dmodel.model"))
        objects = {o.get("id"):o for o in model.findall("m:resources/m:object",core)}
        builds = {b.get("objectid"):b for b in model.findall("m:build/m:item",core)}
        cfg = ET.fromstring(arc.read("Metadata/model_settings.config"))
        assert len(cfg.findall("object")) == 7 and not cfg.findall(".//part[@subtype='modifier_part']")
        assert not cfg.findall(".//part[@subtype='negative_part']")
        for part, specimen in zip(report["parts"],report["specimens"],strict=True):
            obj = cfg.find(f"object[@id='{part['object_id']}']")
            metadata = {m.get("key"):m.get("value") for m in obj.findall("metadata") if m.get("key")}
            # The control has no process override; every other object changes only seam_gap.
            process_keys = set(metadata) - {"name","extruder"}
            assert process_keys == set(specimen["object_overrides"]), (specimen["id"],process_keys)
            for k,v in specimen["object_overrides"].items(): assert metadata[k] == v
            mesh = trimesh.load(ROOT / part["source"],force="mesh",process=True)
            component = objects[part["object_id"]].find("m:components/m:component",core)
            child = ET.fromstring(arc.read(component.get("{"+prod+"}path").lstrip("/")))
            geo = child.find("m:resources/m:object/m:mesh",core)
            vertices = np.array([[float(v.get(k)) for k in "xyz"] for v in geo.find("m:vertices",core)])
            faces = np.array([[int(v.get(k)) for k in ("v1","v2","v3")] for v in geo.find("m:triangles",core)])
            assert np.array_equal(faces,mesh.faces)
            placed = transform(transform(vertices,component.get("transform")),builds[part["object_id"]].get("transform"))
            target = transform(mesh.vertices-part["source_center_mm"]," ".join(map(str,part["build_transform"])))
            error = float(np.abs(placed-target).max()); assert error < 1e-4
            geometry.append(dict(id=specimen["id"],source_stl_sha256=part["stl_sha256"],native_vertex_error_mm=error,triangle_indices_identical=True))
        (HERE / "native-preview.png").write_bytes(arc.read("Metadata/plate_1.png"))
        if "Metadata/top_1.png" in arc.namelist(): (HERE / "native-top.png").write_bytes(arc.read("Metadata/top_1.png"))
    gcode = WORK / "plate_1.gcode"
    text = gcode.read_text()
    assert not re.search(r"^\s*G39(?:\s|;|$)",text,re.M)
    bounds = prep.writer.object_toolpaths(gcode,WORK/"all-beads.gcode",None)
    lo,hi = np.array(bounds["extrusion_bounds_xy_mm"])
    margin = float(min(np.min(lo),np.min(np.array([325,320])-hi)))
    assert margin >= 80,margin
    first,second = defaultdict(list),defaultdict(list)
    layers,ramps,supports = defaultdict(dict),defaultdict(int),defaultdict(int)
    gap_runs = defaultdict(list)
    run = []
    witness_z = (4.04,9.80,16.04)

    def finish_run():
        nonlocal run
        if run:
            pts = np.array([run[0]["a"]]+[x["b"] for x in run])
            area = abs(float(np.sum(pts[:,0]*np.roll(pts[:,1],-1)-np.roll(pts[:,0],-1)*pts[:,1])/2))
            gap_runs[(run[0]["object"],round(run[0]["layer"],2))].append(dict(
                projected_enclosed_area_mm2=area,gap_mm=float(np.linalg.norm(pts[0,:2]-pts[-1,:2])),
                start_mm=pts[0].tolist(),end_mm=pts[-1].tolist(),length_mm=sum(math.dist(x["a"],x["b"]) for x in run)))
        run = []

    for road in extrusion_segments(gcode):
        oid,z,feature = road["object"],road["layer"],road["feature"]
        if feature.startswith("Support"): supports[oid] += 1
        if oid is not None and "wall" in feature.lower():
            layers[oid][round(z,4)] = road["height"]
            if abs(road["a"][2]-z)>1e-5 or abs(road["b"][2]-z)>1e-5: ramps[oid] += 1
        if abs(z-.2)<1e-5 or abs(z-.44)<1e-5:
            bead = LineString([road["a"][:2],road["b"][:2]]).buffer(road["width"]/2,quad_segs=4)
            if abs(z-.2)<1e-5: first[oid].append(bead)
            elif "wall" in feature.lower(): second[oid].append(bead)
        chosen = any(abs(z-w)<1e-5 for w in witness_z)
        if feature in ("Outer wall","Overhang wall") and chosen:
            if run and (oid!=run[-1]["object"] or z!=run[-1]["layer"] or math.dist(run[-1]["b"],road["a"])>1e-4): finish_run()
            run.append(road)
        else: finish_run()
    finish_run()
    assert not supports and not ramps,(dict(supports),dict(ramps))
    readings = []
    fig,ax = plt.subplots(figsize=(8,8))
    for specimen in report["specimens"]:
        oid=specimen["identify_id"]
        assert layers[oid] and min(layers[oid])==.2
        assert all(abs(h-(.2 if z==.2 else .24))<1e-5 for z,h in layers[oid].items())
        bed,walls = unary_union(first[oid]),unary_union(second[oid])
        overlaps = [bead.intersection(bed).area/bead.area for bead in second[oid]]
        assert overlaps and min(overlaps)>1e-9
        witnesses=[]
        for z in witness_z:
            exterior=max(gap_runs[(oid,z)],key=lambda x:x["projected_enclosed_area_mm2"])
            assert exterior["projected_enclosed_area_mm2"]>300
            assert abs(exterior["gap_mm"]-specimen["nominal_path_gap_mm"])<.001,(specimen["id"],z,exterior)
            witnesses.append(dict(nominal_z_mm=z,**exterior))
        readings.append(dict(id=specimen["id"],control=specimen["control"],seam_gap_percent=specimen["seam_gap_percent_of_nozzle"],
                             expected_path_gap_mm=specimen["nominal_path_gap_mm"],wall_layers=len(layers[oid]),
                             first_height_mm=.2,remaining_wall_height_mm=.24,scarf_ramp_segments=0,
                             second_wall_segments=len(overlaps),second_segments_without_bed_overlap=0,
                             minimum_second_segment_overlap_fraction=min(overlaps),gap_witnesses=witnesses))
        for poly in (list(bed.geoms) if hasattr(bed,"geoms") else [bed]):
            x,y=poly.exterior.xy;ax.fill(x,y,color="#518ca8" if specimen["control"] else "#c3a86b",alpha=.8)
            for hole in poly.interiors:
                x,y=hole.xy;ax.fill(x,y,color="white")
        x,y=bed.centroid.xy
        ax.text(x[0],y[0],specimen["id"]+"\n"+str(specimen["seam_gap_percent_of_nozzle"])+"%"+("\nCONTROL" if specimen["control"] else ""),ha="center",va="center",fontsize=10,weight="bold")
    ax.plot([80,245,245,80,80],[80,80,240,240,80],"k--",lw=1)
    ax.set(xlim=(0,325),ylim=(0,320),xlabel="Printer X (mm)",ylabel="Printer Y (mm)",
           title=f"Ordinary seam gap only · scarf OFF · one control\nFront is bottom · {margin:.1f} mm full-bead edge clearance")
    ax.set_aspect("equal");fig.tight_layout();fig.savefig(HERE/"plate-layout.png",dpi=150);plt.close(fig)
    destination=HERE/native.name;shutil.copyfile(native,destination)
    validation["archive"]=str(destination.relative_to(ROOT))
    result=dict(schema=1,native=validation,geometry=geometry,prepared_project=report["project"],
                prepared_project_sha256=report["project_sha256"],source_profile_sha256=report["settings_source_sha256"],
                inherited_profile_process_identical=True,only_object_process_override="seam_gap",
                control_has_no_process_override=True,seam_position="aligned",scarf_enabled=False,
                fine_layer_bands=False,minimum_full_bead_bed_margin_mm=margin,full_bead_bounds=bounds,
                support_deposition_segments=0,probing_clump_detection=False,gcode_postprocessed=False,
                ordinary_seam_readings=readings,analysis_script_sha256=sha(Path(__file__)),
                scope="Native settings, source geometry, plate footprint, bed contact and commanded endpoint gaps. Physical flatness and full-faucet transfer remain unassessed.",pass_check=True)
    save(HERE/"native-check.json",result);shutil.copyfile(WORK/"result.json",HERE/"native-result.json")
    print(json.dumps(dict(minutes=validation["estimated_seconds"]/60,grams=validation["estimated_grams_saved_profile_density"],minimum_edge_clearance_mm=margin,gaps=[dict(id=r["id"],expected=r["expected_path_gap_mm"],emitted=[w["gap_mm"] for w in r["gap_witnesses"]]) for r in readings],pass_check=True),indent=2))


if __name__ == "__main__":
    main()
