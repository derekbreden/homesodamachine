"""One editable compact-reference plate and its requested native readings.

Call this manually after the two geometry exports are frozen. It uses the
generic 3MF writer and path readers as libraries, with one native parent and
two same-material normal volumes. It does not connect to a printer.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import LineString, box as rectangle
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/"tools/bambu_print.py").is_file())
GENERIC = ROOT/"hardware/printed-parts/calibration/soda-studies"
PROFILE = ROOT/"hardware/printed-parts/petgf.3mf"
IDENTITY = np.eye(4).tolist()
PROJECT = HERE/"prints/the-pour-v5-petgf.3mf"
PLAN = HERE/"print-plan.json"
SUMMARY = HERE/"native-summary.json"

GLOBAL_OPTIONS = {
    "layer_height": "0.24", "initial_layer_print_height": "0.20",
    "wall_loops": "6", "wall_generator": "arachne",
    "wall_sequence": "inner wall/outer wall", "is_infill_first": "0",
    "infill_wall_overlap": "15%", "seam_position": "aligned",
    "seam_gap": "15%", "seam_slope_type": "none",
    "override_filament_scarf_seam_setting": "1",
    "enable_support": "1", "support_type": "tree(auto)",
    "support_style": "default", "support_filament": "1",
    "support_interface_filament": "1", "brim_type": "no_brim",
    "brim_width": "0", "brim_object_gap": "0", "skirt_loops": "0",
    "enable_prime_tower": "0", "elefant_foot_compensation": "0",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def libraries():
    generic = load_module(GENERIC/"prepare_prints.py", "compact_generic_prepare")
    generic.WORK = ROOT/".cache/pour-wedge/native-work"
    portal = load_module(HERE/"pip.py", "compact_portal_recipe")
    return generic, portal


def stations(bay):
    b=bay["proof"]["actual_stock_bounds_mm"]
    g=bay["proof"]["nominal_gaps_mm"]["xy_per_face"]
    return {"leg0":b["front_wall"][3]+g,
            "leg1":b["floor_plinth"][2]-g,
            "leg2":b["floor_plinth"][3]+g,
            "leg3":b["back_wall"][2]-g,
            "front_wall_min":b["front_wall"][2],
            "front_wall_max":b["front_wall"][3],
            "back_wall_min":b["back_wall"][2],
            "back_wall_max":b["back_wall"][3]}


def probes(bay):
    p = bay["proof"]["contact_planes_z_mm"]
    b = bay["proof"]["actual_stock_bounds_mm"]
    floor_y0, floor_y1 = b["floor_plinth"][2:4]
    station=stations(bay)
    requested=bay["proof"]["nominal_gaps_mm"]
    g=requested["xy_per_face"]
    cy = (floor_y0+floor_y1)/2
    # Source-frame bounds deliberately isolate each contact from neighboring
    # body/handle faces. Both leaves share one native object identity.
    lower_xy = [[-6., cy-1.2], [6., cy+1.2]]
    upper_xy = [[-6.,station["leg1"]+.85],[6.,station["leg1"]+1.85]]
    def window(xy, z0, z1):
        return [[xy[0][0], xy[0][1], z0], [xy[1][0], xy[1][1], z1]]
    release = [
        {"name": "One lower solid-skin release gap", "fixed_body_id": "body",
         "moving_body_id": "moving", "fixed_surface": "top",
         "moving_surface": "bottom", "requested_gap_mm": requested["lower_z"],
         "fixed_contact_bounds_mm": window(lower_xy, p["floor"]-.50, p["floor"]+.015),
         "moving_contact_bounds_mm": window(lower_xy, p["bar_bottom"]+.015, p["bar_bottom"]+.48),
         "support_gap_bounds_mm": window(lower_xy, p["floor"], p["bar_bottom"])},
        {"name": "One upper solid-skin release gap", "fixed_body_id": "body",
         "moving_body_id": "moving", "fixed_surface": "bottom",
         "moving_surface": "top", "requested_gap_mm": requested["upper_z"],
         "fixed_contact_bounds_mm": window(upper_xy, p["lip_underside"]+.015, p["lip_underside"]+.48),
         "moving_contact_bounds_mm": window(upper_xy, p["bar_top"]-.50, p["bar_top"]+.015),
         "support_gap_bounds_mm": window(upper_xy, p["bar_top"], p["lip_underside"])},
    ]
    lateral = [
        {"name": "Front outside running face",
         "line_xy_mm": [[0.,station["front_wall_max"]-1.],[0.,station["leg0"]+1.25]],
         "fixed_interval_mm": [0.,1.], "moving_interval_mm": [1.+g,2.25+g]},
        {"name": "Front inside running face",
         "line_xy_mm": [[0.,station["leg1"]-1.25],[0.,floor_y0+1.]],
         "fixed_interval_mm": [1.25+g,2.25+g], "moving_interval_mm": [0.,1.25]},
        {"name": "Rear inside running face",
         "line_xy_mm": [[0.,floor_y1-1.],[0.,station["leg2"]+1.25]],
         "fixed_interval_mm": [0.,1.], "moving_interval_mm": [1.+g,2.25+g]},
        {"name": "Rear outside running face",
         "line_xy_mm": [[0.,station["leg3"]-1.25],[0.,station["back_wall_min"]+1.]],
         "fixed_interval_mm": [1.25+g,2.25+g], "moving_interval_mm": [0.,1.25]},
    ]
    for value in lateral:
        value.update(fixed_body_id="body", moving_body_id="moving", requested_gap_mm=g,
                     print_z_mm=[1.16,p["floor"] if "inside" in value["name"] else p["bar_top"]-.24])
    return release, lateral


def create_plan(geometry, portal):
    requested=geometry["pip"]["nominal_gaps_mm"]
    bay = portal.build(xy_air=requested["xy_per_face"],z_air=requested["lower_z"])
    planes = bay["proof"]["contact_planes_z_mm"]
    station=stations(bay)
    width,depth,height=geometry["dimensions_mm"]
    bed_probe_x=geometry["ceiling"]["rear_access_mm"][1]-4.
    bed_probe_start=station["back_wall_max"]+.12
    release, lateral = probes(bay)
    parts = []
    for name, title in (("body", "The Pour frame"), ("moving", "Captive portal slide")):
        source = ROOT/geometry["parts"][name]["stl"]
        part = {"id": name, "name": title, "stl": relative(source),
                "stl_sha256": sha(source)}
        if name == "body":
            part["native_body_window"] = [[-5.,station["front_wall_min"]+.05,0.],
                                          [5.,station["front_wall_max"]-.05,planes["lip_top"]]]
            part["native_review"] = {"wall_probes": [
                {"name": "Left rear bed round", "line_xy_mm": [[-bed_probe_x,bed_probe_start],[-bed_probe_x,depth]],
                 "print_z_mm": [0.,1.], "expected_wall_roads": 6},
                {"name": "Right rear bed round", "line_xy_mm": [[bed_probe_x,bed_probe_start],[bed_probe_x,depth]],
                 "print_z_mm": [0.,1.], "expected_wall_roads": 6}]}
        else:
            part.update(native_body_window=[[-5.,station["leg0"],0.],[5.,station["leg1"],planes["bar_top"]]],
                native_release_probes=release, native_gap_probes=lateral,
                travel_x_mm=bay["proof"]["mechanical_stroke_mm"],
                y_running_air_per_side_mm=requested["xy_per_face"], first_layer_chamfer_mm=.35,
                native_review={"wall_probes": [
                    {"name": "Front moving bed foot",
                     "line_xy_mm": [[0.,station["leg0"]-requested["xy_per_face"]/2],
                                    [0.,station["leg1"]+requested["xy_per_face"]/2]],
                     "print_z_mm": [0.,1.]},
                    {"name": "Rear moving bed foot",
                     "line_xy_mm": [[0.,station["leg2"]-requested["xy_per_face"]/2],
                                    [0.,station["leg3"]+requested["xy_per_face"]/2]],
                     "print_z_mm": [0.,1.]}]})
        parts.append(part)
    modifiers = []
    for name, shape in bay["support_blockers"].items():
        bound = shape.BoundingBox()
        modifiers.append({"id": "PIP "+name, "name": "Intentional motion: "+name,
                          "subtype": "support_blocker",
                          "bounds_mm": [[bound.xmin,bound.ymin,bound.zmin],
                                        [bound.xmax,bound.ymax,bound.zmax]]})
    source_paint = geometry.get("native_support_paint", {})
    paint = source_paint.get("body")
    if "body_stl_sha256" in source_paint:
        if source_paint["body_stl_sha256"] != parts[0]["stl_sha256"]:
            raise ValueError("Frozen exterior support paint does not match the current body STL")
        indices = sorted(set(source_paint["bed_R6_exterior_transition_faces"]))
        paint = {"block_triangle_indices": indices,
                 "index_scope": "trimesh.load(force=mesh,process=True) frozen STL face order",
                 "scope": "Outward/downward source R6 rear bed transition faces only. Horizontal functional ceilings remain supportable.",
                 "source_selection": {k:v for k,v in source_paint.items() if not isinstance(v,list)}}
    if paint is None:
        paint = geometry["parts"]["body"].get("support_paint")
    if paint is None:
        raise ValueError("Frozen geometry must identify its exterior R6 support paint")
    paint = {**paint, "source_stl_sha256": parts[0]["stl_sha256"]}
    if "block_triangle_indices" not in paint:
        raise ValueError("Exterior support paint requires exact processed STL triangle indices")
    cohort = {"id": "compact-corner-petgf", "settings_source": relative(PROFILE),
              "requested_z_trim_mm": .04, "global_overrides": GLOBAL_OPTIONS,
              "material_source": {"scope": "Saved PET-GF single-slot profile; no printer state inferred",
                                  "printer": "Mark2", "physical_nozzle": "left 0.4 mm",
                                  "source_sha256": sha(PROFILE)}}
    native_review = geometry.get("native_review", {}).copy()
    if geometry.get("ceiling"):
        c = geometry["ceiling"]["reading_rectangle_mm"]
        native_review["ceiling_probes"] = [{"name": "Accessible rear supported crown flat",
            "nominal_ceiling_z_mm": c[4], "window_xy_mm": [[c[0],c[2]],[c[1],c[3]]],
            "requested_support_top_gap_mm": .45}]
    obj = {"id": "compact-corner", "name": "The Pour",
           "manufacturing_frame": {"id": "compact-corner-print-up-plus-z",
                                   "from_source_matrix_mm": IDENTITY},
           "object_overrides": {}, "layer_ranges": [], "modifiers": modifiers,
           "volumes": [{"part_id": "body", "filament_slot": 1, "support_paint": paint},
                       {"part_id": "moving", "filament_slot": 1}],
           "native_review": native_review}
    plan = {"schema": 1, "name": "The Pour compact print reference",
            "geometry_dimensions_mm":[width,depth,height],
            "parts": parts, "cohort": cohort, "print_object": obj,
            "plate": {"id": "compact-corner", "offsets_mm": [[0.,0.]],
                      "model_border_mm": 80.},
            "geometry_source_sha256": {relative(HERE/"geometry.json"): sha(HERE/"geometry.json"),
                                       relative(HERE/"reference.py"): sha(HERE/"reference.py"),
                                       relative(HERE/"pip.py"): sha(HERE/"pip.py")},
            "recipe_source_sha256": sha(__file__),
            "recipe_functions_sha256": recipe_functions_sha(), "submitted": False,
            "seam_paint": {**geometry.get("native_seam_paint", {}),
                           "radius_mm":geometry["display"]["side_radius_mm"]},
            "variation_scope": "One whole object uses one recipe. Change a setting and reprint the complete object for comparison.",
            "layer_scope": "0.20 mm bed layer followed by uniform 0.24 mm model layers; no height bands.",
            "support_scope": "Default Tree(auto), retaining automatic normal sections. Only intentional PIP motion volumes and the named rear bed R6 faces are blocked."}
    return plan, bay


def retitle(project, report, generic, plan):
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    document = ET.fromstring(members["3D/3dmodel.model"])
    for item in document.findall(generic.writer.qn("metadata")):
        if item.get("name") == "Title":
            item.text = "The Pour V5 — Corner PET-GF reference, Mark2"
    seam = plan.get("seam_paint", {})
    if seam:
        ET.SubElement(document,generic.writer.qn("metadata"),
                      name="BambuStudio:SeamPaintingVersion").text="0"
        volume = next(v for v in report["volumes"] if v["part_id"] == "body")
        child = ET.fromstring(members[volume["member"]])
        triangles = child.findall(f".//{generic.writer.qn('triangles')}/{generic.writer.qn('triangle')}")
        indices = seam["standing_left_rear_R6_faces"]
        for index in indices:
            triangles[index].set("paint_seam","4")
        members[volume["member"]]=generic.writer.xml(child)
        report["contour_seam_paint"] = {**seam,"source_stl_sha256":volume["source_stl_sha256"],
                                      "serialization":"Unsplit triangle seam ENFORCER=1 -> paint_seam=4",
                                      "enforced_triangle_count":len(indices)}
    members["3D/3dmodel.model"] = generic.writer.xml(document)
    config = ET.fromstring(members["Metadata/model_settings.config"])
    for item in config.findall("plate/metadata"):
        if item.get("key") == "plater_name":
            item.set("value", "The Pour V5 — Corner PET-GF reference, Mark2")
    members["Metadata/model_settings.config"] = generic.writer.xml(config)
    generic.writer.archive_write(project, members)
    report.update(project_sha256=sha(project), printer="Mark2",
                  requested_z_trim_mm=.04, expected_textured_plate_trim_mm=.02,
                  physical_result="Unprinted compact reference; release, motion, finish, strength and lifetime remain unmeasured.",
                  generated_with_compact_preparer_source_sha256=sha(__file__),
                  current_compact_preparer_source_sha256=sha(__file__),
                  recipe_functions_sha256=recipe_functions_sha(),
                  recipe_binding_scope="The generated-with digest binds the source bytes used for this editable project. Current preparer and native reader digests bind their recorded sources. The recipe-function digest binds construction and requested settings; project and native archive digests bind their saved bytes.",
                  generic_preparer_source_sha256=sha(generic.__file__))


def footprint(deposit, shift):
    points = np.asarray(deposit["points"])-shift[:2]
    width = deposit["strand_width_mm"] or .6
    return LineString(points).buffer(width/2, cap_style=2, join_style=2)


def moving_support_contact_reading(deposits,report,bay,generic):
    """Separate removable end-pocket roots from contact with printed stock."""
    import math
    import trimesh
    from shapely.geometry import Point
    from shapely.ops import polygonize
    from shapely.prepared import prep
    from matplotlib import pyplot as plt
    from matplotlib.patches import Patch, Polygon as PlotPolygon

    obj=report["print_objects"][0]
    shift=np.asarray(obj["manufacturing_to_plate_mm"])[:3,3]
    volume=next(v for v in obj["volumes"] if v["part_id"] == "moving")
    source=ROOT/volume["source"]
    mesh=trimesh.load(source,force="mesh",process=True)
    mesh.apply_transform(np.asarray(volume["source_to_shared_frame_mm"]))
    model_height=float(report["layer_height_mm"])
    first_height=float(report["first_layer_height_mm"])
    top=float(mesh.bounds[1,2])
    slices={}
    prepared={}
    moving_lines={}
    fixed_lines={}
    support_lines={}
    support_heights={}
    for d in deposits:
        if d["feature"].startswith("Custom"):continue
        nozzle=d["commanded_nozzle_end_z_mm"]
        z=round((d["model_z_mm"] if nozzle is None else nozzle)-shift[2],5)
        if d["feature"].startswith("Support"):
            if z>top+model_height:continue
            support_lines.setdefault(z,[]).append(footprint(d,shift))
            support_heights[z]=max(support_heights.get(z,0.),d["strand_height_mm"] or model_height)
            continue
        if not generic.reading.is_model_deposit(d) or d["identify_id"] !=obj["identify_id"]:
            continue
        if z>top+.01:continue
        height=first_height if abs(z-first_height)<1e-5 else model_height
        if z not in slices:
            section=mesh.section(plane_origin=[0.,0.,z-height/2],plane_normal=[0.,0.,1.])
            if section is None:
                slices[z]=None
            else:
                # Planar intersection segments are already in the shared
                # XY frame; polygonize them without an optional graph backend.
                polygons=list(polygonize([LineString(section.vertices[e.points,:2])
                                          for e in section.entities]))
                slices[z]=unary_union(polygons)
                prepared[z]=prep(slices[z].buffer(.002))
        for a,b in zip(d["points"],d["points"][1:]):
            a,b=a-shift[:2],b-shift[:2]
            is_moving=slices[z] is not None and prepared[z].covers(Point((a+b)/2))
            if not is_moving and abs(z-first_height)>1e-5 and abs(z-5.96)>1e-5:
                continue
            width=d["strand_width_mm"] or .6
            poly=LineString([a,b]).buffer(width/2,cap_style=2,join_style=2)
            (moving_lines if is_moving else fixed_lines).setdefault(z,[]).append(poly)
    moving={z:unary_union(p) for z,p in moving_lines.items()}
    fixed={z:unary_union(p) for z,p in fixed_lines.items()}
    supports={z:unary_union(p) for z,p in support_lines.items()}
    pairs=[]
    best_3d=None
    for mz,mp in sorted(moving.items()):
        mh=first_height if abs(mz-first_height)<1e-5 else model_height
        for sz,sp in sorted(supports.items()):
            sh=support_heights[sz]
            zgap=max(0.,sz-sh-mz,mz-mh-sz)
            if best_3d is not None and zgap>best_3d["nominal_slab_distance_3d_mm"]+.00001:
                continue
            gap=float(mp.distance(sp))
            distance=math.hypot(gap,zgap)
            item={"moving_model_nozzle_z_mm":mz,"support_nozzle_z_mm":sz,
                  "minimum_xy_width_footprint_gap_mm":gap,
                  "nominal_slab_z_air_mm":zgap,"nominal_slab_distance_3d_mm":distance}
            if best_3d is None or distance<best_3d["nominal_slab_distance_3d_mm"]:
                best_3d=item
            if zgap<1e-5:
                item["xy_width_footprint_overlap_area_mm2"]=float(mp.intersection(sp).area)
                pairs.append(item)
    limits=bay["proof"]["actual_bounds_mm"]["moving"][:2]
    stop0=limits[0]-bay["proof"]["mechanical_stroke_mm"]/2
    stop1=limits[1]+bay["proof"]["mechanical_stroke_mm"]/2
    s=stations(bay)
    pockets=unary_union([rectangle(stop0,s["front_wall_max"],limits[0],s["back_wall_min"]),
                        rectangle(limits[1],s["front_wall_max"],stop1,s["back_wall_min"])])
    route_rows=[]
    for z,sp in sorted(supports.items()):
        if z>bay["proof"]["contact_planes_z_mm"]["lip_underside"]+1e-5:continue
        material=sp.intersection(pockets)
        if material.area>1e-6:
            route_rows.append({"support_nozzle_z_mm":z,
                               "end_pocket_width_footprint_area_mm2":float(material.area),
                               "end_pocket_width_footprint_bounds_mm":list(material.bounds)})
    image=PROJECT.with_name(PROJECT.stem+"-motion-paths.png")
    selected=[first_height,min(moving,key=lambda z:abs(z-5.96))]
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),constrained_layout=True)
    colours={"fixed":"#b9b4aa","moving":"#2389b0","supports":"#d8892d"}
    def draw(ax,geometry,colour):
        if geometry is None:return
        polygons=list(geometry.geoms) if hasattr(geometry,"geoms") else [geometry]
        for p in polygons:
            if p.geom_type!="Polygon":continue
            ax.add_patch(PlotPolygon(np.asarray(p.exterior.coords),closed=True,
                facecolor=colour,edgecolor=colour,linewidth=.15))
            for hole in p.interiors:
                ax.add_patch(PlotPolygon(np.asarray(hole.coords),closed=True,
                    facecolor="white",edgecolor=colour,linewidth=.15))
    for ax,z in zip(axes,selected):
        draw(ax,fixed.get(z),colours["fixed"])
        draw(ax,supports.get(z),colours["supports"])
        draw(ax,moving.get(z),colours["moving"])
        ax.axvline(limits[0],color="#2389b0",linestyle="--",linewidth=.6)
        ax.axvline(limits[1],color="#2389b0",linestyle="--",linewidth=.6)
        ax.set(xlim=[stop0-4,stop1+4],ylim=[s["front_wall_min"]-1,s["back_wall_min"]+4],
               xlabel="X · slide axis (mm)",ylabel="Y (mm)",title=f"Native nozzle Z {z:.2f} mm")
        ax.set_aspect("equal")
        ax.grid(alpha=.15)
    fig.legend(handles=[Patch(facecolor=colours[k],label=l) for k,l in
        (("fixed","Fixed model"),("moving","Moving model"),("supports","Automatic support"))],
        loc="outside lower center",ncol=3,frameon=False)
    fig.suptitle("Native support roots and printed moving paths",fontsize=12)
    fig.savefig(image,dpi=180)
    plt.close(fig)
    overlaps=[p for p in pairs if p["xy_width_footprint_overlap_area_mm2"]>1e-7]
    return {"moving_source_stl":relative(source),"moving_source_stl_sha256":sha(source),
        "moving_model_layers_classified":len(moving),
        "minimum_nominal_extrusion_slab_distance":best_3d,
        "minimum_xy_footprint_gap_with_touching_z_slabs_mm":min(p["minimum_xy_width_footprint_gap_mm"] for p in pairs),
        "maximum_xy_width_footprint_overlap_area_mm2":max(p["xy_width_footprint_overlap_area_mm2"] for p in pairs),
        "overlapping_slab_and_footprint_pair_count":len(overlaps),
        "no_commanded_support_contact_with_moving_stock":not overlaps,
        "slab_contact_pair_readings":pairs,"end_pocket_support_routes":route_rows,
        "path_image":relative(image),"path_image_sha256":sha(image),
        "cleanup_scope":"Remove the automatic ceiling supports and any terminal-pocket roots before assessing the slide. Empty pockets remain beyond the initial lip ends, and the rear opening reaches the crown underside and tab. Actual removal and release remain unprinted physical results.",
        "measurement_scope":"Model commands are classified by the frozen moving STL's nominal layer-midplane sections. Distances use commanded line-width footprints and model slabs, including neighboring slabs that share a Z plane. Strand sag, physical bead shape, removal force and reliable release are not measured."}


def compact_native_readings(text, report, bay, generic):
    """Read the explicit moving first layer, bridge direction and gap blockers."""
    reading = generic.reading
    obj = report["print_objects"][0]
    shift = np.asarray(obj["manufacturing_to_plate_mm"])[:3,3]
    label = obj["identify_id"]
    deposits = list(reading.native_deposits(text))
    planes = bay["proof"]["contact_planes_z_mm"]
    station=stations(bay)
    bar_bottom = planes["bar_bottom"]
    first_bar = min((d["model_z_mm"] for d in deposits
                     if d["identify_id"] == label and reading.is_model_deposit(d)
                     and d["model_z_mm"] > bar_bottom
                     and reading.intersects_native_window(d,
                         np.array([[-8.,station["leg1"]+.05,bar_bottom],
                                   [8.,station["leg2"]-.05,bar_bottom+.5]])+shift)), default=None)
    bridge_rows = []
    if first_bar is not None:
        for d in deposits:
            if (d["identify_id"] != label or not reading.is_model_deposit(d)
                    or abs(d["model_z_mm"]-first_bar) > 1e-6
                    or d["feature"] != "Bridge"):
                continue
            for a, b in zip(d["points"],d["points"][1:]):
                a, b = a-shift[:2], b-shift[:2]
                clipped = reading.clipped_segment(a,b,[-8.,station["leg1"]],[8.,station["leg2"]])
                if clipped is None or np.linalg.norm(clipped[1]-clipped[0]) < .01:
                    continue
                direction = b-a
                length = float(np.linalg.norm(direction))
                angle = float(np.degrees(np.arctan2(direction[1],direction[0]))%180)
                bridge_rows.append({"line_1based":d["gcode_line_1based"],
                    "endpoints_in_manufacturing_frame_mm":[a.tolist(),b.tolist()],
                    "length_mm":length,"angle_from_x_degrees":angle,
                    "commanded_width_mm":d["strand_width_mm"],
                    "strand_flow_height_mm":d["strand_height_mm"],
                    "connects_both_leg_regions": bool(min(a[1],b[1]) < station["leg1"]
                        and max(a[1],b[1]) > station["leg2"]),
                    "runs_along_y": bool(abs(direction[0]) < .02)})
    foot_rows = []
    for name, bounds in (("front_moving_leg",[[-5.,station["leg0"],0.],[5.,station["leg1"],.45]]),
                         ("back_moving_leg",[[-5.,station["leg2"],0.],[5.,station["leg3"],.45]])):
        layers = {}
        for d in deposits:
            if d["identify_id"] == label and reading.is_model_deposit(d) \
                    and reading.intersects_native_window(d,np.asarray(bounds)+shift):
                value = layers.setdefault(d["model_z_mm"],{"positive_segments":0,"features":set(),"widths":set()})
                value["positive_segments"] += len(d["points"])-1
                value["features"].add(d["feature"])
                if d["strand_width_mm"] is not None:value["widths"].add(d["strand_width_mm"])
        foot_rows.append({"name":name,"unique_window_mm":bounds,
            "first_two_attributed_layers":[{"nozzle_z_mm":z,
                "positive_segments":v["positive_segments"],"features":sorted(v["features"]),
                "commanded_widths_mm":sorted(v["widths"])} for z,v in sorted(layers.items())[:2]]})
    first_layer_models = [d for d in deposits if d["identify_id"] == label
                          and reading.is_model_deposit(d) and abs(d["model_z_mm"]-.20) < 1e-6]
    first_skin = unary_union([footprint(d,shift) for d in first_layer_models])
    components = list(first_skin.geoms) if hasattr(first_skin,"geoms") else [first_skin]
    witness_regions = {
        "fixed": rectangle(-2.,station["front_wall_min"]+.5,
                            2.,station["front_wall_max"]-.5),
        "front_moving_leg": rectangle(-2.,station["leg0"]+.75,2.,station["leg1"]-.75),
        "back_moving_leg": rectangle(-2.,station["leg2"]+.75,2.,station["leg3"]-.75),
    }
    component_ids = {name:[i for i,p in enumerate(components) if p.intersection(region).area > 1e-5]
                     for name,region in witness_regions.items()}
    first_isolation = {
        "component_ids_in_unique_windows":component_ids,
        "moving_feet_have_separate_model_footprints":bool(component_ids["fixed"])
            and bool(component_ids["front_moving_leg"]) and bool(component_ids["back_moving_leg"])
            and not (set(component_ids["fixed"]) & (set(component_ids["front_moving_leg"])
                |set(component_ids["back_moving_leg"])))
            and not (set(component_ids["front_moving_leg"]) & set(component_ids["back_moving_leg"])),
        "scope":"Connected unions of commanded first-layer model width footprints; physical bead shape and bonding remain unmeasured."}
    contours=[]
    previous=None
    current=None
    outer_features={"Outer wall","Overhang wall"}
    for d in deposits:
        if d["identify_id"] == label and d["feature"] in outer_features:
            start=d["points"][0]-shift[:2]
            end=d["points"][-1]-shift[:2]
            continuation = (previous is not None and previous["feature"] in outer_features
                and previous["identify_id"] == label and abs(previous["model_z_mm"]-d["model_z_mm"]) < 1e-6
                and np.linalg.norm(previous["points"][-1]-d["points"][0]) < .0001)
            if not continuation:
                current={"model_nozzle_z_mm":d["model_z_mm"],"start_xy_mm":start.tolist(),
                         "end_xy_mm":end.tolist(),"first_line_1based":d["gcode_line_1based"]}
                contours.append(current)
            else:
                current["end_xy_mm"]=end.tolist()
        previous=d
    seam_record=report["contour_seam_paint"]
    corner=np.asarray(seam_record["world_corner_center_xy_mm"])
    seam_z0,seam_z1=seam_record["z_band_mm"]
    seam_radius=seam_record["radius_mm"]
    seam_starts=[]
    for c in contours:
        start=np.asarray(c["start_xy_mm"]); delta=start-corner
        radius=float(np.linalg.norm(delta))
        if not (seam_z0 <= c["model_nozzle_z_mm"] <=seam_z1
                and seam_radius-.4 <= radius <=seam_radius+.4
                and delta[0] <0 and delta[1] >0):continue
        c.update(radius_from_corner_mm=radius,
            degrees_from_minus_x_toward_plus_y=float(np.degrees(np.arctan2(delta[1],-delta[0]))),
            endpoint_centerline_gap_mm=float(np.linalg.norm(start-np.asarray(c["end_xy_mm"]))))
        c["closed_contour_endpoint_witness"] = c["endpoint_centerline_gap_mm"] < 1.
        seam_starts.append(c)
    blocker_rows = []
    for name, shape in bay["support_blockers"].items():
        b = shape.BoundingBox()
        xy = rectangle(b.xmin+1e-5,b.ymin+1e-5,b.xmax-1e-5,b.ymax-1e-5)
        hits=[]
        for d in deposits:
            if not d["feature"].startswith(("Support","Brim","Skirt","Prime")):
                continue
            z = d["model_z_mm"]-shift[2]
            step = d["strand_height_mm"] or .24
            if z <= b.zmin+1e-5 or z-step >= b.zmax-1e-5:
                continue
            area = footprint(d,shift).intersection(xy).area
            if area > 1e-7:
                hits.append({"line_1based":d["gcode_line_1based"],"feature":d["feature"],
                             "nozzle_z_mm":z,"xy_footprint_overlap_area_mm2":area})
        blocker_rows.append({"name":name,"commanded_support_brim_or_prime_intrusions":hits})
    return {"scope":"Commanded native paths and width footprints in the supplied manufacturing frame. Physical sag, bead shape, release and motion remain unmeasured.",
        "moving_leg_bed_witnesses":foot_rows,"first_crossbar_model_nozzle_z_mm":first_bar,
        "first_layer_model_footprint_isolation":first_isolation,
        "standing_R6_outer_contour_start_witnesses":seam_starts,
        "contour_start_scope":"First/last positive Outer wall or Overhang wall points in contiguous native contour runs. Open runs are marked separately and their endpoint distance is not a seam gap. This witnesses commanded placement and path endpoints, not a physical ridge, groove or scarf outcome.",
        "first_crossbar_bridge_roads":bridge_rows,
        "first_crossbar_bridge_roads_follow_y_anchors":bool(bridge_rows)
            and all(r["runs_along_y"] and r["connects_both_leg_regions"] for r in bridge_rows),
        "motion_blocker_footprint_readings":blocker_rows,
        "moving_support_contact_reading":moving_support_contact_reading(deposits,report,bay,generic),
        "no_support_brim_or_prime_in_motion_volume":all(not r["commanded_support_brim_or_prime_intrusions"] for r in blocker_rows),
        "saved_and_native_layers_scope":"Both leaves share the single parent schedule. No individual leaf schedule or physical first-layer bonding is inferred."}


def prepare(slice_native=False):
    generic, portal = libraries()
    geometry = json.loads((HERE/"geometry.json").read_text())
    plan, bay = create_plan(geometry,portal)
    PLAN.write_text(json.dumps(plan,indent=2)+"\n")
    project, report = generic.prepare_plate(plan,plan["cohort"],[plan["print_object"]],
        PROJECT,offsets=[[0.,0.]],border_mm=80.)
    report["plate_id"] = "compact-corner"
    report["source_compact_plan_sha256"] = sha(PLAN)
    retitle(project,report,generic,plan)
    if slice_native:
        generic.native_slice(project,report)
        archive_path = ROOT/report["native"]["archive"]
        with zipfile.ZipFile(archive_path) as archive:
            text = archive.read("Metadata/plate_1.gcode").decode()
        report["native"]["compact_readings"] = compact_native_readings(text,report,bay,generic)
        report["native"]["compact_reader_source_sha256"] = sha(__file__)
    project.with_suffix(".print.json").write_text(json.dumps(report,indent=2)+"\n")
    write_totals(report,generic)


def write_totals(report,generic):
    project=ROOT/report["project"]
    totals = {"project":relative(project),"project_sha256":sha(project),
              "normal_volume_count":2,"native_parent_count":1,"plate_count":1,
              "first_layer_mm":.20,"uniform_model_layer_mm":.24,
              "saved_profile_source":relative(PROFILE),"saved_profile_sha256":sha(PROFILE),
              "source_compact_plan_sha256":report["source_compact_plan_sha256"],
              "generated_with_compact_preparer_source_sha256":report.get("generated_with_compact_preparer_source_sha256"),
              "current_compact_preparer_source_sha256":report.get("current_compact_preparer_source_sha256"),
              "recipe_functions_sha256":report.get("recipe_functions_sha256"),
              "submitted":False}
    if "native" in report:
        native=report["native"]
        totals.update(estimated_time=native["estimated_time"],
            estimated_seconds=generic.estimates_seconds(native["estimated_time"]),
            saved_profile_filament_estimate_g=native["saved_profile_filament_estimate_g"],
            minimum_full_bead_bed_margin_mm=native["minimum_full_bead_bed_margin_mm"],
            archive=native["archive"],archive_sha256=native["archive_sha256"],
            compact_reader_source_sha256=native.get("compact_reader_source_sha256"))
    SUMMARY.write_text(json.dumps(totals,indent=2)+"\n")
    write_preparation_index(report,totals)
    print(json.dumps(totals,indent=2))


def write_preparation_index(report,totals):
    """One current project and its saved source/output bindings."""
    manifest=HERE/"manifest.json"
    normal_volumes=[v for o in report["print_objects"] for v in o["volumes"]
                    if v["subtype"]=="normal_part"]
    blocker_count=sum(v["subtype"]=="support_blocker"
                      for o in report["print_objects"] for v in o["volumes"])
    counts={part:sum(v["part_id"]==part for v in normal_volumes)
            for part in ("body","moving")}
    project=ROOT/report["project"]
    metadata=project.with_suffix(".print.json")
    value={"schema":4,"title":"The Pour V5 — Corner",
        "source_manifest":relative(manifest),"source_manifest_sha256":sha(manifest),
        "variation_scope":"One geometry configuration and one recipe per complete object; compare settings across complete prints.",
        "projects":[{"plate_id":report["plate_id"],"project":relative(project),
            "project_sha256":sha(project),"preparation_metadata":relative(metadata),
            "preparation_metadata_sha256":sha(metadata),
            "native_parent_count":len(report["print_objects"]),
            "normal_volume_count":len(normal_volumes),
            "support_blocker_volume_count":blocker_count,
            "first_layer_mm":totals["first_layer_mm"],
            "uniform_model_layer_mm":totals["uniform_model_layer_mm"]}],
        "physical_part_coverage":{"expected_part_ids":["body","moving"],
            "material_volume_counts":counts,
            "missing_part_ids":[p for p,n in counts.items() if not n],
            "parts_in_multiple_native_parents":[p for p,n in counts.items() if n>1]},
        "physical_result":"Unprinted. Release, sliding feel, support removal and finish remain unmeasured.",
        "preparation_only":"native" not in report,
        "sliced_locally":"native" in report,"submitted":False}
    if "native" in report:
        for key in ("estimated_time","estimated_seconds","saved_profile_filament_estimate_g",
                    "minimum_full_bead_bed_margin_mm"):
            value["projects"][0][key]=totals[key]
        contact=report["native"]["compact_readings"]["moving_support_contact_reading"]
        value["projects"][0].update(motion_path_image=contact["path_image"],
            motion_path_image_sha256=contact["path_image_sha256"])
        value.update(total_estimated_seconds=totals["estimated_seconds"],
            total_saved_profile_filament_estimate_g=sum(totals["saved_profile_filament_estimate_g"]),
            minimum_full_bead_bed_margin_mm=totals["minimum_full_bead_bed_margin_mm"])
    (HERE/"print-preparation.json").write_text(json.dumps(value,indent=2)+"\n")


def recipe_functions_sha():
    source="\n".join(inspect.getsource(f) for f in (stations,probes,create_plan,retitle))
    source+="\n"+json.dumps(GLOBAL_OPTIONS,sort_keys=True)
    return hashlib.sha256(source.encode()).hexdigest()


def read_existing():
    """Read the saved immutable native archive without preparing or slicing."""
    generic,portal=libraries()
    geometry=json.loads((HERE/"geometry.json").read_text())
    report=json.loads(PROJECT.with_suffix(".print.json").read_text())
    for volume in report["print_objects"][0]["volumes"]:
        if volume["subtype"]!="normal_part":continue
        if sha(ROOT/volume["source"]) != volume["source_stl_sha256"]:
            raise ValueError("Saved native readings require their frozen source meshes; current geometry differs")
    requested=geometry["pip"]["nominal_gaps_mm"]
    bay=portal.build(xy_air=requested["xy_per_face"],z_air=requested["lower_z"])
    native=report["native"]
    archive_path=ROOT/native["archive"]
    with zipfile.ZipFile(archive_path) as archive:
        text=archive.read("Metadata/plate_1.gcode").decode()
    native["compact_readings"]=compact_native_readings(text,report,bay,generic)
    native["compact_reader_source_sha256"]=sha(__file__)
    report.pop("compact_recipe_source_sha256",None)
    report.update(current_compact_preparer_source_sha256=sha(__file__),
                  current_recipe_functions_sha256=recipe_functions_sha(),
                  source_compact_plan_sha256=sha(PLAN),
                  recipe_binding_scope="Generated-with source and recipe-function digests retain the editable project's construction inputs. Current preparer, current recipe-function and native reader digests identify the current reading code. The existing plan, editable project and native archive keep their saved byte digests.")
    PROJECT.with_suffix(".print.json").write_text(json.dumps(report,indent=2)+"\n")
    write_totals(report,generic)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--slice",action="store_true",help="Request one local native slice; never submit a print")
    mode.add_argument("--read-existing",action="store_true",help="Read saved paths without preparing or slicing")
    args=parser.parse_args()
    read_existing() if args.read_existing else prepare(args.slice)
