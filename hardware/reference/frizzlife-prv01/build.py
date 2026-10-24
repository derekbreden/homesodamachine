"""Frizzlife PRV01 native outside-envelope reference; run through cadq."""
from pathlib import Path
import hashlib
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
LENGTH = 2.63 * 25.4
MAIN_LENGTH = 1.51 * 25.4
MAIN_START = 10.0
MAIN_END = MAIN_START + MAIN_LENGTH
MAIN_D = .98 * 25.4
CUFF_D = 1.05 * 25.4
CAP_WIDTH = .79 * 25.4
TUBE_D = 6.35
INSERTION = 15.7
PARTS = ("frizzlife-body", "frizzlife-inlet-collet", "frizzlife-outlet-collet",
         "frizzlife-inlet-clip", "frizzlife-outlet-clip")
OFFICIAL = "https://www.frizzlife.com/collections/pressure-regulators/products/frizzlife-water-filter-pressure-regulator-protection-valve-for-reverse-osmosis-water-filter-system-60psi-1-4-quick-connect-push-fit-prv01"
CDN = "https://cdn.shopify.com/s/files/1/0159/8429/5990/files/"
PROFILE = [(2.4, 4.7), (3.5, 4.7), (3.5, 7.6), (5.4, 7.9),
           (5.4, 9.9), (9.8, 9.9), (MAIN_START, CUFF_D/2-.3),
           (10.3, CUFF_D/2), (23.0, CUFF_D/2), (25.0, MAIN_D/2),
           (MAIN_END-.5, MAIN_D/2), (MAIN_END, MAIN_D/2-.3),
           (MAIN_END, 7.5), (50.6, 7.5), (50.6, 8.5), (55.5, 8.5),
           (55.5, 9.8), (62.2, 9.8), (62.2, 7.1), (63.2, 7.1),
           (63.2, 4.7), (LENGTH-2.4, 4.7)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cylinder(r, x0, x1):
    return cq.Solid.makeCylinder(r, x1-x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def turned(profile):
    points = [(0, profile[0][0]), *((r, x) for x, r in profile), (0, profile[-1][0])]
    return (cq.Workplane("XZ").polyline(points).close().revolve(360, (0, 0), (0, 1)).val()
            .rotate((0, 0, 0), (0, 1, 0), 90))


def body():
    outer = turned(PROFILE)
    # The photo shows a faceted outlet collar. Its published projected width
    # controls the across-corners envelope; exact flat clock is estimated.
    collar = (cq.Workplane("XY").polygon(6, CAP_WIDTH).extrude(6.7).val()
              .rotate((0, 0, 0), (0, 1, 0), 90).translate((55.5, 0, 0)))
    outer = outer.cut(cylinder(15., 55.5, 62.2)).fuse(collar).clean()
    outer = outer.cut(cylinder(TUBE_D/2, -.01, INSERTION))
    outer = outer.cut(cylinder(TUBE_D/2, LENGTH-INSERTION, LENGTH+.01))
    return outer


def collet():
    # Simplified release ring: the tube mouth is the outer annular face.
    return cylinder(5.5, 0., 1.5).fuse(cylinder(4.7, 1.5, 2.4)).cut(
        cylinder(TUBE_D/2, -.01, 2.41)).clean()


def clip():
    ring = cylinder(6.2, 1.5, 2.4).cut(cylinder(4.9, 1.49, 2.41))
    # C opening and small pull tab follow the photo qualitatively.
    opening = cq.Solid.makeBox(2., 4., 8., cq.Vector(1., -2., 0.))
    return ring.cut(opening)


def mirror_end(solid):
    return solid.rotate((0, 0, 0), (0, 1, 0), 180).translate((LENGTH, 0, 0))


def pieces():
    return [(PARTS[0], body()), (PARTS[1], collet()), (PARTS[2], mirror_end(collet())),
            (PARTS[3], clip()), (PARTS[4], mirror_end(clip()))]


def port(x, direction):
    return {"point_mm": [x, 0., 0.], "outward_axis": [direction, 0., 0.],
            "kind": "1/4tube_socket", "tube_od_mm": TUBE_D,
            "insertion_estimate_mm": INSERTION}


def export():
    folder = HERE/"geometry"
    folder.mkdir(exist_ok=True)
    assembly = cq.Assembly(name="Frizzlife_PRV01_1_4_push_connect")
    records, all_v, all_f, offset = {}, [], [], 0
    face_records = {}
    for name, solid in pieces():
        is_clip = name.endswith("clip")
        assembly.add(solid, name=name, color=cq.Color(.08, .18, .77) if is_clip else cq.Color(.91, .91, .89))
        if name.endswith("collet"):
            inlet = "inlet" in name
            label = "inlet_1_4OD_tube_mouth" if inlet else "outlet_1_4OD_tube_mouth"
            face = cq.Workplane().add(solid).faces("<X" if inlet else ">X").val()
            assembly.objects[name].addSubshape(face, name=label)
            face_records[label] = {**port(0. if inlet else LENGTH, -1. if inlet else 1.),
                                  "native_face_area_mm2": float(face.Area())}
        vv, ff = solid.tessellate(.04, .12)
        v = np.array([p.toTuple() for p in vv], dtype=np.float32)
        f = np.array(ff, dtype=np.int32)
        path = folder/(name+".npz")
        np.savez_compressed(path, v=v, f=f)
        cq.exporters.export(solid, str(path.with_suffix(".step")))
        records[name] = {"mesh": str(path.relative_to(HERE)), "mesh_sha256": sha(path),
            "step": str(path.with_suffix(".step").relative_to(HERE)),
            "step_sha256": sha(path.with_suffix(".step")),
            "bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
            "valid_native_solid": bool(solid.isValid()), "native_solid_count": len(solid.Solids()),
            "volume_mm3": float(solid.Volume()), "triangles": len(f)}
        all_v.append(v); all_f.append(f+offset); offset += len(v)
    step = folder/"frizzlife-prv01.step"
    assembly.export(str(step))
    v, f = np.vstack(all_v), np.vstack(all_f)
    mesh = folder/"frizzlife-prv01.npz"
    np.savez_compressed(mesh, v=v, f=f)
    dims = {
        "units": "mm", "part": "Frizzlife PRV01", "asin": "B08NDQCZN2",
        "status": "Purchased by Derek; manufacturer-dimensioned outside-envelope layout reference",
        "canonical_frame": "+X flow from broad-cuff inlet X0 to narrow-neck outlet X66.802; Y/Z radial",
        "published_body": {"overall_length_mm": LENGTH, "main_housing_length_mm": MAIN_LENGTH,
            "upper_housing_diameter_mm": MAIN_D, "maximum_cuff_diameter_mm": CUFF_D,
            "outlet_collar_projected_width_mm": CAP_WIDTH, "tube_od_mm": TUBE_D,
            "advertised_preset_psi": 60., "stated_regulated_range_psi": [50., 60.],
            "maximum_inlet_psi": 300., "maximum_temperature_C": 40.},
        "geometry_estimates": {"main_housing_start_x_mm": MAIN_START,
            "main_housing_end_x_mm": MAIN_END, "profile_x_radius_mm": PROFILE,
            "collet_outer_diameter_mm": 11., "clip_outer_diameter_mm": 12.4,
            "outlet_collar": "Six-sided,20.066mm across corners; published photo width controls maximum envelope",
            "tube_insertion_estimate_mm": INSERTION,
            "scope": "Axial split between two socket necks, shoulders, collet/clip detail, exact collar facet clock and socket engagement are estimated from the official photo and familiar1/4OD fittings. Published overall length is used as nominal tube-mouth span. No internal regulator mechanism is drawn; plain blind sockets display the tube insertion volumes."},
        "tube_ports": {"inlet": port(0., -1.), "outlet": port(LENGTH, 1.)},
        "named_faces": face_records, "nominal_tube_mouth_span_mm": LENGTH,
        "assembly_bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
        "assembly_mesh": str(mesh.relative_to(HERE)), "assembly_mesh_sha256": sha(mesh),
        "assembly_step": str(step.relative_to(HERE)), "assembly_step_sha256": sha(step),
        "geometry": records,
        "sources": [
            {"title": "Frizzlife official PRV01 product page", "url": OFFICIAL, "verified_date": "2026-10-23",
             "supports": "PRV01 identity,native1/4push-in,50–60psi,maximum300psi inlet and40Cwater"},
            {"title": "Frizzlife official dimensional photograph", "url": CDN+"PRV013_77f49cde-2932-4349-856b-636ef15aa6ae_1.jpg?v=1758007365",
             "local": "sources/dimensions.jpg", "sha256": sha(HERE/"sources/dimensions.jpg"),
             "supports": "2.63in overall,1.51in housing,0.98in upper-body,0.79in collar and1.05in lower-cuff widths"},
            {"title": "Frizzlife official product photograph", "url": CDN+"PRV01.png?v=1758007365",
             "local": "sources/product.png", "sha256": sha(HERE/"sources/product.png"),
             "supports": "Outside shoulders,release collets,blue clips and flow arrow"},
            {"title": "Purchased item listing", "url": "https://www.amazon.com/dp/B08NDQCZN2",
             "supports": "User-provided purchased item identity; signed-inPrimeoffer verified by integrating agent"}
        ]}
    (HERE/"dimensions.json").write_text(json.dumps(dims, indent=2)+"\n")
    print(json.dumps({"tube_ports": dims["tube_ports"], "bounds_mm": dims["assembly_bounds_mm"],
        "all_native_parts_valid": all(p["valid_native_solid"] for p in records.values())}, indent=2))


if __name__ == "__main__":
    export()
