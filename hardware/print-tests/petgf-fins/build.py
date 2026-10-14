"""Make the PET-GF fin/bridge screening plate. Run by hand; does not send."""
from pathlib import Path
import hashlib
import json
import math
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools/funnel-mold-print"))
from profiles import PROD, REL, mesh_object, metadata, qn

PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
STEM = "2026-10-14-fin-bridges-petgf-left04-z004-mark2"
FIRST = 0.20
LAYER = 0.24
ROOF_BOTTOM = FIRST + 42 * LAYER  # 10.28; first shelf extrusion at 10.52
ROOF_THICKNESS = 8 * LAYER
DEPTH = 12.0
FIN_THICKNESS = 1.0
FIN_HEIGHT = FIRST + 53 * LAYER
FOOT_HEIGHT = FIRST + 2 * LAYER
FOOT_WIDTH = 3.2
UNDERLAP = 0.50
SPANS = (4, 8, 12, 16, 24, 32)
ANGLES = (30, 35, 40, 45, 50, 55, 60)


def block(x, y, z, origin=(0, 0, 0)):
    return cq.Workplane("XY").box(x, y, z, centered=False).translate(origin)


def label(text, size, origin, rotation=90):
    return (cq.Workplane("XY").text(text, size, 2 * LAYER,
            font="Arial", kind="bold", combine=False)
            .rotate((0, 0, 0), (0, 0, 1), rotation).translate(origin))


def bridge(span, gap, name):
    """Two removable side fins with horizontal teeth; no permanent model anchor.

    The first tooth row lies directly below the shelf and reaches UNDERLAP
    into its footprint. Its inner ends define the labelled clear bridge span.
    Two higher rows kiss the shelf's side faces with 0.01 mm Boolean overlap.
    Body clearance is horizontal, distinct from a prop's vertical support gap.
    """
    width = span + 2 * UNDERLAP
    right = width + 2 * gap
    shelf = block(width, DEPTH, ROOF_THICKNESS, (gap, 0, ROOF_BOTTOM))
    shelf = shelf.union(label(name, 3.6,
                         (gap + width / 2, DEPTH / 2, ROOF_BOTTOM + ROOF_THICKNESS)))
    fins = []
    for side in (0, 1):
        blade = block(FIN_THICKNESS, DEPTH, FIN_HEIGHT, (-FIN_THICKNESS, 0, 0))
        blade = blade.edges("|Y and >Z").fillet(0.45)
        foot = block(FOOT_WIDTH, DEPTH + 2, FOOT_HEIGHT, (-FOOT_WIDTH, -1, 0))
        fin = blade.union(foot)
        for y in np.linspace(1.0, DEPTH - 1.0, 7):
            fin = fin.union(block(gap + UNDERLAP + 0.02, 0.50, LAYER,
                                  (-0.02, y - 0.25, ROOF_BOTTOM - LAYER)))
        for z in (ROOF_BOTTOM + 2 * LAYER, ROOF_BOTTOM + 5 * LAYER):
            for y in (2.0, 6.0, 10.0):
                fin = fin.union(block(gap + 0.03, 0.50, LAYER,
                                      (-0.02, y - 0.25, z)))
        if side:
            fin = fin.mirror("YZ").translate((right, 0, 0))
        fins.append(fin)
    return shelf.union(fins[0]).union(fins[1]).clean(), {
        "kind": "fin_bridge", "clear_span_mm": span,
        "horizontal_body_gap_mm": gap, "shelf_width_mm": width,
        "shelf_depth_mm": DEPTH, "shelf_thickness_mm": ROOF_THICKNESS,
        "shelf_bottom_z_mm": ROOF_BOTTOM,
        "first_shelf_nozzle_z_mm": ROOF_BOTTOM + LAYER,
        "first_tooth_nozzle_z_mm": ROOF_BOTTOM,
        "fin_inner_face_spacing_mm": right,
        "lower_tooth_underlap_mm": UNDERLAP,
        "tine_width_mm": 0.50, "tine_height_mm": LAYER,
        "tines_per_fin": 13, "fin_count": 2,
        "bridge_axis": "X", "bridge_angle_override": "180",
        "shelf_bounds_local_mm": [[gap, 0, ROOF_BOTTOM],
                                  [gap + width, DEPTH, ROOF_BOTTOM + ROOF_THICKNESS]],
        "clear_span_bounds_local_mm": [gap + UNDERLAP, gap + UNDERLAP + span],
    }


def slope(angle):
    # Angle is measured UP FROM THE BED. Each has the same 14 mm horizontal reach.
    start, reach, bottom, thickness = 4.0, 14.0, FIRST + 12 * LAYER, 2.4
    tangent = math.tan(math.radians(angle))
    rise = reach * tangent
    bar = (cq.Workplane("XZ").polyline([
        (start - 0.1, bottom - 0.1 * tangent), (start + reach, bottom + rise),
        (start + reach, bottom + rise + thickness), (start - 0.1, bottom + thickness - 0.1 * tangent)
    ]).close().extrude(-DEPTH))
    post = block(start, DEPTH, bottom + thickness)
    foot = block(5, DEPTH + 7, FOOT_HEIGHT, (0, -6, 0))
    part = post.union(bar).union(foot)
    part = part.union(label(str(angle), 3.2, (2.5, -3, FOOT_HEIGHT)))
    return part.clean(), {
        "kind": "slope", "angle_from_bed_degrees": angle,
        "horizontal_reach_mm": reach, "depth_mm": DEPTH,
        "vertical_thickness_mm": thickness, "underside_start_z_mm": bottom,
        "rise_mm": rise,
    }


def tine(width):
    # An upright stock surface and an edge-on fin, separated at the feet as well.
    gap, height = 0.24, FIRST + 51 * LAYER
    stock = block(3, DEPTH, height)
    stock = stock.union(block(5, DEPTH, FOOT_HEIGHT, (-2, 0, 0)))
    stock = stock.union(label(f"{width:g}", 2.7, (1.5, DEPTH / 2, height)))
    fin = block(6, 1, height, (3 + gap, 5.5, 0))
    fin = fin.union(block(6, 5, FOOT_HEIGHT, (3 + gap, 3.5, 0)))
    zs = [FIRST + n * LAYER for n in (12, 25, 38)]
    for z in zs:
        fin = fin.union(block(gap + 0.04, width, LAYER, (2.98, 6 - width / 2, z)))
    return stock.union(fin).clean(), {
        "kind": "tine_release", "tine_width_mm": width,
        "horizontal_body_gap_mm": gap, "tine_height_mm": LAYER,
        "tine_count": 3, "tine_z_intervals_mm": [[z, z + LAYER] for z in zs],
        "fin_count": 1,
    }


def vertical_reference():
    height = FIRST + 51 * LAYER
    part = block(3, DEPTH, height).union(block(7, DEPTH, FOOT_HEIGHT, (-2, 0, 0)))
    return part.union(label("V", 2.8, (1.5, DEPTH / 2, height))).clean(), {
        "kind": "vertical_surface_reference", "angle_from_bed_degrees": 90,
    }


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    (HERE / "parts").mkdir(parents=True, exist_ok=True)
    groups = []
    for prefix, gap, cy in (("A", 0.24, 108), ("B", 0.48, 132)):
        groups.append((cy, [(f"{prefix}{s}", *bridge(s, gap, f"{prefix}{s}")) for s in SPANS]))
    groups.append((161, [(f"S{a}", *slope(a)) for a in ANGLES]))
    cross, cross_info = bridge(12, 0.24, "Y12")
    cross = cross.rotate((0, 0, 0), (0, 0, 1), 90)
    cross_info.update(bridge_axis="Y", bridge_angle_override="90")
    cross_info["shelf_bounds_local_mm"] = [[-DEPTH, 0.24, ROOF_BOTTOM],
        [0, 13.24, ROOF_BOTTOM + ROOF_THICKNESS]]
    cross_info["clear_span_bounds_local_mm"] = [0.74, 12.74]
    groups.append((194, [(f"T{round(w * 100)}", *tine(w)) for w in (.45, .5, .6, .8)]
                        + [("Y12", cross, cross_info), ("V", *vertical_reference())]))

    with zipfile.ZipFile(PROFILE) as source:
        settings = json.loads(source.read("Metadata/project_settings.config"))
        data = {name: source.read(name) for name in
                ("Metadata/filament_settings_1.config", "[Content_Types].xml")}
    changes = {
        "enable_support": "0", "brim_type": "no_brim", "skirt_loops": "0",
        "filament_colour": ["#161616"], "filament_multi_colour": ["#161616"],
        "filament_density": ["1.43"],
        "filament_map_mode": "Manual", "filament_map": ["1"], "filament_map_2": ["1"],
        "filament_nozzle_map": ["0"], "filament_volume_map": ["0"],
        "extruder_ams_count": ["1#0|4#0", "1#0|4#0"],
        "printer_settings_id": "Bambu Lab H2C 0.4 Standard +0.04 Z trim",
        "print_settings_id": "PET-GF fin screening 0.24 mm",
    }
    edits = {k: {"profile": settings.get(k), "plate": v} for k, v in changes.items()
             if settings.get(k) != v}
    settings.update(changes)
    data["Metadata/project_settings.config"] = json.dumps(settings, indent=2).encode()
    filament = json.loads(data["Metadata/filament_settings_1.config"])
    for k in ("filament_colour", "filament_multi_colour", "filament_density"):
        if k in filament:
            filament[k] = settings[k]
    data["Metadata/filament_settings_1.config"] = json.dumps(filament, indent=2).encode()

    model = ET.Element(qn("model"), unit="millimeter", requiredextensions="p",
                       **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    for key, value in (("Application", "BambuStudio-02.08.02.61"),
                       ("BambuStudio:3mfVersion", "1"), ("Title", STEM)):
        ET.SubElement(model, qn("metadata"), name=key).text = value
    resources = ET.SubElement(model, qn("resources"))
    build = ET.SubElement(model, qn("build"), **{f"{{{PROD}}}UUID": str(uuid.uuid4())})
    config = ET.Element("config")
    plate = ET.SubElement(config, "plate")
    for k, v in {"plater_id": 1, "plater_name": STEM, "locked": "false",
                 "filament_map_mode": "Manual", "filament_maps": "1",
                 "filament_volume_maps": "0", "bed_type": "Textured PEI Plate"}.items():
        metadata(plate, k, v)
    rels = ET.Element(f"{{{REL}}}Relationships")
    records, placed_meshes = [], []
    for group, (cy, items) in enumerate(groups, 1):
        meshes = []
        for name, shape, info in items:
            path = HERE / "parts" / f"{name}.stl"
            cq.exporters.export(shape, str(path), tolerance=0.015, angularTolerance=0.12)
            mesh = trimesh.load(path, force="mesh", process=True)
            meshes.append((name, shape, info, path, mesh))
        total = sum(m.bounds[1, 0] - m.bounds[0, 0] for _, _, _, _, m in meshes) + 3 * (len(meshes) - 1)
        cursor = 162.5 - total / 2
        for name, shape, info, path, mesh in meshes:
            center = mesh.bounds.mean(axis=0)
            width = mesh.bounds[1, 0] - mesh.bounds[0, 0]
            cx = cursor + width / 2
            translation = np.array([cx, cy, center[2]]) - center
            bounds = mesh.bounds + translation
            number = len(records) + 1
            pid, oid = str(2 * number - 1), str(2 * number)
            subpath = f"/3D/Objects/object_{number}.model"
            sub = ET.Element(qn("model"), unit="millimeter")
            mesh_object(ET.SubElement(sub, qn("resources")), pid, mesh, center)
            data[subpath.lstrip("/")] = ET.tostring(sub, encoding="UTF-8", xml_declaration=True)
            obj = ET.SubElement(resources, qn("object"), id=oid, type="model",
                                **{f"{{{PROD}}}UUID": str(uuid.uuid4())})
            ET.SubElement(ET.SubElement(obj, qn("components")), qn("component"),
                          objectid=pid, transform="1 0 0 0 1 0 0 0 1 0 0 0",
                          **{f"{{{PROD}}}path": subpath, f"{{{PROD}}}UUID": str(uuid.uuid4())})
            transform = f"1 0 0 0 1 0 0 0 1 {cx:.9f} {cy:.9f} {center[2]:.9f}"
            ET.SubElement(build, qn("item"), objectid=oid, printable="1", transform=transform)
            ET.SubElement(rels, f"{{{REL}}}Relationship", Target=subpath, Id=f"rel-{number}",
                          Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
            cfg = ET.SubElement(config, "object", id=oid)
            metadata(cfg, "name", name)
            metadata(cfg, "extruder", "1")
            if "bridge_angle_override" in info:
                metadata(cfg, "bridge_angle", info["bridge_angle_override"])
            ET.SubElement(cfg, "metadata", face_count=str(len(mesh.faces)))
            part = ET.SubElement(cfg, "part", id=pid, subtype="normal_part")
            for k, v in {"name": path.name, "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                         "source_file": path.name, "source_object_id": 0, "source_volume_id": 0,
                         "source_offset_x": center[0], "source_offset_y": center[1],
                         "source_offset_z": center[2]}.items():
                metadata(part, k, v)
            inst = ET.SubElement(plate, "model_instance")
            for k, v in {"object_id": oid, "instance_id": 0, "identify_id": 4100 + number}.items():
                metadata(inst, k, v)
            record = {"id": name, "row": group, "object_id": int(oid),
                      "identify_id": 4100 + number, "mesh": str(path.relative_to(HERE)),
                      "mesh_sha256": sha(path), "plate_translation_mm": translation.tolist(),
                      "plate_bounds_mm": bounds.tolist(), "triangles": len(mesh.faces),
                      "cad_valid": shape.val().isValid(), "cad_solids": len(shape.solids().vals()),
                      "mesh_watertight": bool(mesh.is_watertight),
                      "mesh_winding_consistent": bool(mesh.is_winding_consistent),
                      "mesh_bodies": mesh.body_count, **info}
            records.append(record)
            placed = mesh.copy()
            placed.apply_translation(translation)
            placed_meshes.append(placed)
            cursor += width + 3
    package = ET.Element(f"{{{REL}}}Relationships")
    ET.SubElement(package, f"{{{REL}}}Relationship", Target="/3D/3dmodel.model", Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
    for path, element in (("3D/3dmodel.model", model), ("Metadata/model_settings.config", config),
                          ("3D/_rels/3dmodel.model.rels", rels), ("_rels/.rels", package)):
        # Studio's package loader expects unprefixed OPC relationship tags.
        data[path] = ET.tostring(element, encoding="UTF-8", xml_declaration=True).replace(
            b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    project = HERE / f"{STEM}.3mf"
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, payload in data.items():
            archive.writestr(path, payload)
    bounds = trimesh.util.concatenate(placed_meshes).bounds
    report = {"project": project.name, "project_sha256": sha(project),
              "source_profile": str(PROFILE.relative_to(ROOT)), "source_profile_sha256": sha(PROFILE),
              "printer": "Mark2", "material": "Polymaker Fiberon PET-GF15",
              "nozzle": "Left fixed hardened Standard 0.4 mm; external spool 254",
              "plate": "Textured PEI Plate", "requested_z_trim_mm": 0.04,
              "expected_emitted_z_trim_mm": 0.02, "first_layer_mm": FIRST,
              "normal_layer_mm": LAYER, "settings_edits": edits,
              "cad_plate_bounds_mm": bounds.tolist(), "parts": records,
              "physical_result": "pending", "submitted": False}
    (HERE / f"{STEM}.print.json").write_text(json.dumps(report, indent=2) + "\n")
    render_layout(records)
    render_geometry()
    print(json.dumps({"project": str(project), "specimens": len(records),
                      "bounds_mm": bounds.tolist(),
                      "invalid": [r["id"] for r in records if not r["cad_valid"]
                                  or not r["mesh_watertight"] or r["mesh_bodies"] != 1]}))


def render_layout(records):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=160)
    colours = {"fin_bridge": "#59a6ca", "slope": "#edaa61",
               "tine_release": "#8bb18b", "vertical_surface_reference": "#9d9ba9"}
    for r in records:
        lo, hi = np.asarray(r["plate_bounds_mm"])
        ax.add_patch(Rectangle(lo[:2], hi[0] - lo[0], hi[1] - lo[1],
                              facecolor=colours[r["kind"]], edgecolor="#273740", lw=1))
        ax.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, r["id"],
                ha="center", va="center", fontsize=10, fontweight="bold")
    for y, title in ((108, "A · 0.24 mm side clearance"), (132, "B · 0.48 mm side clearance"),
                     (161, "S · angle up from bed"), (194, "T · tine width / Y · rotated repeat / V · wall reference")):
        ax.text(162.5, y - (16 if y == 194 else 14), title, ha="center", fontsize=10, color="#273740")
    ax.set(xlim=(72, 253), ylim=(87, 215), xlabel="Bed X (mm)", ylabel="Bed Y (mm)")
    ax.set_aspect("equal")
    ax.set_title("PET-GF fin screening · Mark2\nBridges 4–32 mm · Slopes 30–60° · 0.24 mm layers", pad=18)
    ax.grid(alpha=.12)
    ax.text(.5, -.16, "Facing the printer: front is at the bottom. Each coupon is separate; fins are built into its geometry.",
            transform=ax.transAxes, ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(HERE / "plate-layout.png", bbox_inches="tight")
    plt.close(fig)


def render_geometry():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(12, 4.5), dpi=160)
    samples = (("A16", "16 mm bridge between two fins"),
               ("S45", "45° slope without support"),
               ("T50", "0.5 mm horizontal tines"))
    for i, (name, title) in enumerate(samples, 1):
        mesh = trimesh.load(HERE / "parts" / f"{name}.stl", force="mesh")
        ax = fig.add_subplot(1, 3, i, projection="3d")
        colours = ["#579bbc" if n[2] < .7 else "#8bc2d2" for n in mesh.face_normals]
        ax.add_collection3d(Poly3DCollection(mesh.triangles, facecolors=colours,
                                             linewidths=.04, edgecolors="#3d6574"))
        lo, hi = mesh.bounds
        ax.set(xlim=(lo[0] - 1, hi[0] + 1), ylim=(lo[1] - 1, hi[1] + 1), zlim=(0, hi[2] + 1))
        ax.set_box_aspect(hi - lo + [2, 2, 1])
        ax.view_init(elev=20, azim=-65)
        ax.set_axis_off()
        ax.set_title(title, fontsize=11, pad=16)
    fig.tight_layout()
    fig.savefig(HERE / "specimen-geometry.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
