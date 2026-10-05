"""Five upright four-post Beduan socket panels for a tighter hand-fit screen.

The panel carries the production body bearing, port channel and horizontal
teardrop sockets. Only the socket diameter varies between labelled samples.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import sys

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())
sys.path[:0] = [str(ROOT / "hardware/scripts"),
               str(ROOT / "hardware/printed-parts/enclosure/enclosure")]

import cadquery as cq
import enclosure as enc
import trimesh
from _cadq_export import export_assembly
from _material_base import M_PETGF_BLACK, one_body
from flute_payload import cut as write_print_payload

CANDIDATES = (("V72", 7.20), ("V71", 7.10), ("V70", 7.00),
              ("V69", 6.90), ("V68", 6.80))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def panel(diameter, label):
    seat, tray = enc._seat, enc._valve_tray
    width = 2 * (seat.seat_half_x + tray.MARGIN)
    height = tray.height(((0.0, 0.0),))
    station = height / 2
    face_y = seat.seat_top_z
    rear_y = face_y - tray.THICK
    body = enc._ybox(-width / 2, width / 2, rear_y, face_y, 0.0, height)
    at = cq.Location(cq.Vector(0, 0, station))
    turn = cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90)
    body = body.cut(tray.build_body_clearance().val().moved(turn).moved(at))
    sockets = []
    centers = []
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            x, z = sx * seat.corner_inset_x, station + sz * seat.corner_inset_y
            centers.append([x, z])
            socket = enc._teardrop_y(diameter / 2, x, z,
                                     seat.socket_floor_z, face_y + 1)
            sockets.append(socket)
            body = body.cut(socket)
    body = body.cut(tray.build_port_channel(height + 2).val().moved(turn).moved(at))
    # The rear label foot clears the valve's +Y approach and leaves the bearing
    # face unchanged. Its 2 mm overlap joins it to the standing panel.
    tab = cq.Solid.makeBox(width, 9, 1.4, cq.Vector(-width / 2, rear_y - 7, 0))
    label_solid = (cq.Workplane("XY").workplane(offset=1.39)
                   .center(0, rear_y - 3.5)
                   .text(f"{diameter:.2f}", 4, 0.73, font="Arial", kind="bold",
                         combine=False).val())
    body = body.fuse(tab).fuse(label_solid).clean()
    assert body.isValid() and len(body.Solids()) == 1, label
    valve = seat.valve.build_beduan_solenoid().val().moved(turn).moved(at)
    # Remove the four nominal engagement portions from the reference valve to
    # distinguish intentional post/socket interference from an unrelated foul.
    posts = cq.Compound.makeCompound([
        cq.Solid.makeCylinder(seat.corner_post_radius, face_y + 0.0001,
                             cq.Vector(x, 0, z), cq.Vector(0, 1, 0))
        for x, z in centers])
    nonpost_overlap = body.intersect(valve.cut(posts)).Volume()
    assert nonpost_overlap < 1e-5, (label, nonpost_overlap)
    readings = [{"valve_outward_offset_mm": distance,
                 "nominal_valve_overlap_mm3": body.intersect(
                     valve.translate((0, distance, 0))).Volume()}
                for distance in (20, 10, 5.2, 2, 0)]
    if diameter >= 2 * seat.corner_post_radius:
        assert max(r["nominal_valve_overlap_mm3"] for r in readings) < 1e-5
    return body, dict(label=label, printed_label=f"{diameter:.2f}",
                     socket_diameter_mm=diameter,
                     nominal_post_diameter_mm=2 * seat.corner_post_radius,
                     nominal_diametral_clearance_mm=round(
                         diameter - 2 * seat.corner_post_radius, 3),
                     socket_centers_source_xz_mm=centers,
                     post_pitch_xz_mm=[2 * seat.corner_inset_x,
                                       2 * seat.corner_inset_y],
                     bearing_face_y_mm=face_y,
                     socket_floor_y_mm=seat.socket_floor_z,
                     socket_depth_mm=seat.socket_depth(),
                     nominal_post_engagement_mm=face_y,
                     standing_panel_height_mm=height,
                     panel_width_mm=width, panel_thickness_mm=tray.THICK,
                     rear_label_foot_extension_mm=7,
                     teardrop_roof_angle_degrees=enc.teardrop_roof_angle,
                     native_valve_insertion_samples=readings,
                     nonpost_seated_interference_mm3=nonpost_overlap)


def main():
    geometry_path = HERE / "geometry.json"
    if geometry_path.exists():
        frozen = json.loads(geometry_path.read_text())
        for row in frozen["samples"]:
            for extension in ("stl", "step", "payload"):
                assert sha(HERE / row[extension]) == row[f"{extension}_sha256"]
        print("Existing valve trial geometry and frozen hashes verified", flush=True)
        return
    rows = []
    for label, diameter in CANDIDATES:
        body, row = panel(diameter, label)
        name = f"beduan-socket-{label.lower()}"
        step, stl = HERE / f"{name}.step", HERE / f"{name}.stl"
        export_assembly(one_body(cq.Workplane(obj=body), name, M_PETGF_BLACK), str(step))
        cq.exporters.export(body, str(stl), tolerance=0.005, angularTolerance=0.05)
        mesh = trimesh.load_mesh(stl, process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
        write_print_payload(step, stl, verbose=False, preserve_print_triangles=True)
        payload = step.with_name(step.name + ".mesh")
        row.update(name=name, stl=stl.name, step=step.name, payload=payload.name,
                   stl_sha256=sha(stl), step_sha256=sha(step), payload_sha256=sha(payload),
                   source_bounds_mm=mesh.bounds.tolist(), volume_mm3=body.Volume(),
                   mesh_watertight=True, mesh_bodies=1, triangles=len(mesh.faces))
        rows.append(row)
    source_paths = [Path(__file__), Path(enc.__file__), Path(enc._seat.__file__),
                    Path(enc._valve_tray.__file__), Path(enc._seat.valve.__file__)]
    record = dict(schema_version=1, article="Tighter Beduan four-post socket hand-fit screen",
                  revision=2, control="V72 reproduces the accepted 7.20 mm socket profile",
                  physical_baseline="../physical-acceptance.json",
                  production_orientation="Enclosure-front-top +Z up; socket axes horizontal on Y",
                  insertion_axis=[0, -1, 0], extraction_axis=[0, 1, 0],
                  production_socket_profile_changed=False,
                  supports_required_by_geometry=False, insertion_pause=False,
                  physical_fit_qualified=False,
                  intentional_interference="V68 is 0.10 mm smaller in diameter than the nominal post. CAD post overlap is intentional in this empirical hand-fit candidate.",
                  source_sha256={str(p.relative_to(ROOT)): sha(p) for p in source_paths},
                  samples=rows,
                  scope="Comparative insertion, fully seated body bearing and hand removal of the actual four-post valve. No retention-force, endurance, loaded assembly or tube-operation qualification.")
    geometry_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"geometry": str(geometry_path.relative_to(ROOT)),
                      "samples": [{k: r[k] for k in ("label", "socket_diameter_mm", "stl")}
                                  for r in rows]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
