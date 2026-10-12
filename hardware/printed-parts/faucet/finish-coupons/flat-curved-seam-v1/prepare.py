"""Prepare the matched flat/curved seam plate locally; never connect or Send."""
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
FAUCET = ROOT / "hardware/printed-parts/faucet"
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
REFERENCE = HERE.parent / "scarf-swatches-v1/faucet-neck-swatch.step"
WORK = ROOT / ".cache/printer-control/flat-curved-seam-mark2-20261012"
STEM = "2026-10-12-flat-curved-seams-petgf-left04-z004-mark2"
HEIGHT = .20 + 29 * .24
FLAT_WIDTH = 12.0
PAINT_HALF_WIDTH = 1.1
VARIANTS = (("A", "flat", (-17.5, -17.5)),
            ("B", "curved", (17.5, -17.5)),
            ("C", "curved", (-17.5, 17.5)),
            ("D", "flat", (17.5, 17.5)))
QUOTE = "Please prepare that plate (for mark2 which is likely to be available next)"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2) + "\n")


def geometry():
    original = cq.importers.importStep(str(REFERENCE)).val()
    outer = max((f for f in original.Faces() if f.geomType() == "CYLINDER"),
                key=lambda f: f.Area())._geomAdaptor().Cylinder()
    p, direction = outer.Location(), outer.Axis().Direction()
    location = (p.X(), p.Y(), p.Z())
    angle = math.degrees(math.atan2(direction.Y(), direction.Z()))
    radius = outer.Radius()
    face_y = math.sqrt(radius**2 - (FLAT_WIDTH / 2)**2)
    local = original.translate(tuple(-v for v in location)).rotate((0, 0, 0), (1, 0, 0), angle)
    retained = cq.Solid.makeBox(120, 120, 120, cq.Vector(-60, face_y - 120, -60))
    flat = local.intersect(retained).rotate((0, 0, 0), (1, 0, 0), -angle).translate(location)
    clip = cq.Solid.makeBox(200, 200, HEIGHT, cq.Vector(-100, -60, 0))
    curved, flat = original.intersect(clip), flat.intersect(clip)
    # The inspection face has at least 3 mm of uninterrupted backing over its
    # entire width. Interior bores are unchanged: no added stock is necessary.
    backing = cq.Solid.makeBox(FLAT_WIDTH, 3, 120,
                              cq.Vector(-FLAT_WIDTH / 2, face_y - 3, -60))
    backing = backing.rotate((0, 0, 0), (1, 0, 0), -angle).translate(location).intersect(clip)
    missing_backing = backing.cut(flat).Volume()
    assert missing_backing < 1e-6
    assert flat.cut(curved).Volume() < 1e-6
    records = {}
    for name, shape in (("curved", curved), ("flat", flat)):
        assert shape.isValid() and len(shape.Solids()) == 1
        step, stl = HERE / (name + ".step"), HERE / (name + ".stl")
        cq.exporters.export(shape, str(step))
        raw = WORK / (name + "-raw.stl")
        cq.exporters.export(shape, str(raw), tolerance=.012, angularTolerance=.07)
        mesh = trimesh.load(raw, force="mesh", process=True)
        volume = mesh.volume
        # Uniform subdivision provides small paintable triangles on the flat
        # face without changing any existing facet plane or opening T-junctions.
        mesh = mesh.subdivide().subdivide()
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
        assert abs(mesh.volume - volume) < 1e-5
        mesh.export(stl)
        records[name] = dict(step=str(step.relative_to(ROOT)), step_sha256=sha(step),
                             stl=str(stl.relative_to(ROOT)), stl_sha256=sha(stl),
                             cad_volume_mm3=shape.Volume(), triangles=len(mesh.faces),
                             bounds_mm=mesh.bounds.tolist())
    return dict(reference_step=str(REFERENCE.relative_to(ROOT)), reference_sha256=sha(REFERENCE),
                height_mm=HEIGHT, outer_radius_mm=radius, axis_location_mm=location,
                axis_rotation_x_degrees=-angle, flat_face_axis_frame_y_mm=face_y,
                flat_face_width_mm=FLAT_WIDTH, minimum_continuous_backing_mm=3,
                backing_missing_volume_mm3=missing_backing, added_stock_mm3=0,
                interior_bores_unchanged=True, uniform_subdivision_iterations=2, meshes=records)


def paint(members, parts, geo):
    theta = math.radians(-geo["axis_rotation_x_degrees"])
    rotation = np.array([[1, 0, 0], [0, math.cos(theta), -math.sin(theta)],
                         [0, math.sin(theta), math.cos(theta)]])
    origin = np.array(geo["axis_location_mm"])
    result = []
    for part in parts:
        child = ET.fromstring(members[part["member"]])
        mesh = child.find(f"{writer.qn('resources')}/{writer.qn('object')}/{writer.qn('mesh')}")
        vertices = np.array([[float(v.get(a)) for a in "xyz"] for v in mesh.find(writer.qn("vertices"))])
        triangles = list(mesh.find(writer.qn("triangles")))
        ids = np.array([[int(t.get(k)) for k in ("v1", "v2", "v3")] for t in triangles])
        points = vertices[ids]
        normals = np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0])
        normals /= np.linalg.norm(normals, axis=1)[:, None]
        source_points = points + part["source_center_mm"]
        local_points = (source_points - origin) @ rotation.T
        local = local_points.mean(axis=1)
        side = abs(normals[:, 2]) < .35
        # Paint all triangles intersecting the vertical strip. Selecting only
        # triangle centroids would leave unpainted bands along a triangulated
        # flat face and let the seam fall back to its corners on those layers.
        crosses_strip = ((local_points[:, :, 0].min(axis=1) <= PAINT_HALF_WIDTH) &
                         (local_points[:, :, 0].max(axis=1) >= -PAINT_HALF_WIDTH))
        enforced = side & crosses_strip & (local[:, 1] > 11.9) & (normals[:, 1] > .9)
        for i, triangle in enumerate(triangles):
            if side[i]:
                triangle.set("paint_seam", "4" if enforced[i] else "8")
        assert enforced.any()
        members[part["member"]] = writer.xml(child)
        result.append(dict(identify_id=part["identify_id"], enforcer_triangles=int(enforced.sum()),
                           blocker_triangles=int((side & ~enforced).sum()),
                           target="Center region of the outward Y+ inspection face",
                           target_strip_half_width_mm=PAINT_HALF_WIDTH,
                           selection="Side triangles intersecting the target strip"))
    model = ET.fromstring(members["3D/3dmodel.model"])
    ET.SubElement(model, writer.qn("metadata"), name="BambuStudio:SeamPaintingVersion").text = "0"
    members["3D/3dmodel.model"] = writer.xml(model)
    return result


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    geo = geometry()
    project = HERE / (STEM + ".3mf")
    report = writer.refresh(PROFILE, project,
                            parts=tuple((f"{letter} {kind} face", HERE / (kind + ".stl"), 0.)
                                        for letter, kind, _ in VARIANTS),
                            offsets=tuple(v[2] for v in VARIANTS), z_trim=.04, plate_border=80,
                            title="Flat and curved seam diagnostic - PET-GF defaults - Mark2")
    with zipfile.ZipFile(project) as z:
        members = {n: z.read(n) for n in z.namelist()}
    painting = paint(members, report["parts"], geo)
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  printer="Mark2", requested_z_trim_mm=.04, active_nozzle=0,
                  geometry=geo, seam_painting=painting,
                  specimens=[dict(id=v[0], face=v[1], row_from_front=1 if v[2][1] < 0 else 2,
                                  column_from_left=1 if v[2][0] < 0 else 2,
                                  identify_id=p["identify_id"]) for v, p in zip(VARIANTS, report["parts"])],
                  source_sha256={str(p.relative_to(ROOT)):sha(p) for p in
                                 (PROFILE, REFERENCE, Path(writer.__file__), Path(__file__),
                                  HERE / "curved.stl", HERE / "flat.stl")},
                  factor="Outer inspection-face curvature; all process settings common",
                  common_process="petgf.3mf defaults, regular aligned seam, scarf off, 15% seam gap",
                  preparation_only=True, launch_authorized=False,
                  import_attempted=False, send_attempted=False, accepted=False)
    save(HERE / "preparation.json", report)
    save(project.with_suffix(".print.json"), report)
    save(HERE / "study-plan.json", dict(authorization_quote=QUOTE,
        customer_outcome="Identify whether the visible seam requires a curved surface, with a flat reference for a sideways step",
        specimens=report["specimens"], factor=report["factor"],
        fixed_settings="Saved temperature, cooling, flow, wall count/order, speed, wipe, retraction and motion settings. 0.20 mm first layer and 0.24 mm above; no scarf or fine layer bands.",
        geometry=geo, comparison="Two copies of each face with positions swapped. Both use a central painted seam zone. The curved reference retains the full-scale faucet neck and both retain its 15-degree axis and interior bores.",
        assessment="Keep letters with specimens. Inspect the Y+ painted face after removal, under several light directions and across the surface. Record whether the seam has a lateral step, raised/recessed material, or a texture-only line, and whether the result repeats in the other copy.",
        limitation="Shape changes perimeter length and per-object extrusion duration. The common plate shares layer return time; this does not duplicate a complete faucet's thermal history. Visual inspection alone is not a measured surface profile.",
        preparation_only=True, launch_authorized=False, send_attempted=False, physical_result_pending=True))
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir", str(WORK), "--export-3mf", STEM + ".gcode.3mf", str(project)]
    save(WORK / "slice-command.json", dict(argv=command, printer_connection=False))
    print(json.dumps(dict(project=report["project"], height_mm=HEIGHT, specimens=len(VARIANTS), geometry=geo), indent=2))


if __name__ == "__main__":
    main()
