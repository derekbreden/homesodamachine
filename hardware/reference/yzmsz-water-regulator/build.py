"""Estimated YZMSZ B0CGS34P93 fixed 0.3 MPa water regulator reference.

Run manually through the shared CAD queue. Exterior dimensions are layout
estimates scaled from the product photograph and the dimensioned Frizzlife
PRV01 housing, not measurements or a claim of a common manufacturer.
"""
from pathlib import Path
import hashlib
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
LENGTH = 67.0
DIAMETER = 27.0
TUBE_OD = 6.35
INSERTION = 15.0

# Native +X flow follows the pictured arrow: broad/windowed cap end to the
# narrow outlet neck. Axial shoulder positions and diameters are estimates.
PROFILE = [
    (0.0, 5.8), (1.8, 5.8), (1.8, 8.0), (4.0, 8.0),
    (4.0, 10.5), (7.0, 10.5), (7.0, 12.6), (9.0, 12.6),
    (9.0, 13.5), (23.5, 13.5), (27.0, 12.0), (50.0, 12.0),
    (52.5, 11.0), (52.5, 7.0), (56.0, 7.0), (57.0, 9.6),
    (63.0, 9.6), (64.5, 7.5), (65.0, 5.8), (67.0, 5.8),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def body():
    points = [(0.0, 0.0), *((r, x) for x, r in PROFILE), (0.0, LENGTH)]
    shape = (cq.Workplane("XZ").polyline(points).close()
             .revolve(360, (0, 0), (0, 1)).val()
             .rotate((0, 0, 0), (0, 1, 0), 90))
    # A plain display bore marks the two native push-connect sockets. The
    # internal regulating mechanism and tube seals are not modeled.
    bore = cq.Solid.makeCylinder(TUBE_OD/2, LENGTH + 0.02,
                                cq.Vector(-0.01, 0, 0), cq.Vector(1, 0, 0))
    shape = shape.cut(bore)
    # Two shallow housing windows visible in the seller photograph. Their
    # depth is illustrative; they do not expose or define regulator internals.
    for y in (-7.2, 4.2):
        recess = cq.Solid.makeBox(3.0, 3.0, 3.5, cq.Vector(13.0, y, 11.5))
        shape = shape.cut(recess)
    return shape.clean()


def port(x, axis):
    return {"point_mm": [x, 0.0, 0.0], "outward_axis": [axis, 0.0, 0.0],
            "kind": "1/4tube_socket", "tube_od_mm": TUBE_OD,
            "insertion_estimate_mm": INSERTION}


def export():
    folder = HERE/"geometry"
    folder.mkdir(exist_ok=True)
    shape = body()
    assembly = cq.Assembly(name="YZMSZ_B0CGS34P93_fixed_0_3MPa_water_regulator")
    assembly.add(shape, name="yzmsz-water-regulator", color=cq.Color(.88, .89, .87))
    named_faces = {}
    for name, selector, x, outward in [
        ("inlet_push_connect_mouth", "<X", 0.0, -1.0),
        ("outlet_push_connect_mouth", ">X", LENGTH, 1.0),
    ]:
        face = cq.Workplane().add(shape).faces(selector).val()
        assembly.objects["yzmsz-water-regulator"].addSubshape(face, name=name)
        named_faces[name] = {"point_mm": [x, 0.0, 0.0],
                             "outward_normal": [outward, 0.0, 0.0],
                             "native_face_area_mm2": float(face.Area())}
    step = folder/"yzmsz-water-regulator.step"
    mesh = folder/"yzmsz-water-regulator.npz"
    assembly.export(str(step))
    vv, ff = shape.tessellate(.035, .12)
    v = np.array([p.toTuple() for p in vv], dtype=np.float32)
    f = np.array(ff, dtype=np.int32)
    np.savez_compressed(mesh, v=v, f=f)
    facts = json.loads((HERE/"sources/product-facts.json").read_text())
    dims = {
        "units": "mm",
        "part": "YZMSZ fixed 0.3 MPa water pressure regulator, ASIN B0CGS34P93",
        "selected_variant": "1/4 inch O.D. 0.3 MPa Pressure",
        "status": "Purchased reference; exterior layout estimate",
        "canonical_frame": "Native +X flow; broad/windowed inlet mouth X0 to narrow-neck outlet mouth X67",
        "published": {"tube_od_mm": TUBE_OD, "connection_type": "Native push-connect at both ends",
                      "fixed_outlet_pressure_MPa": 0.3, "fixed_outlet_pressure_psi": 43.5113,
                      "application": "Reverse osmosis and household water filtration",
                      "housing_material": "Engineering plastic, exact polymer unspecified"},
        "estimated_envelope": {"tube_mouth_span_mm": LENGTH, "maximum_diameter_mm": DIAMETER,
                               "length_range_mm": [60.0, 74.0], "diameter_range_mm": [24.0, 30.0],
                               "profile_x_radius_mm": PROFILE,
                               "basis": "Seller photo proportions and dimensioned Frizzlife PRV01 66.802 x 26.67 mm housing as a size proxy; common manufacture is not established",
                               "scope": "Exterior layout estimate, not a measured or manufacturer-dimensioned envelope. End shoulder positions, collet sizes, window recesses, open display bore and 15 mm tube insertion are estimates."},
        "tube_ports": {"inlet": port(0.0, -1.0), "outlet": port(LENGTH, 1.0)},
        "named_faces": named_faces,
        "geometry": {"yzmsz-water-regulator": {"mesh": str(mesh.relative_to(HERE)),
                     "mesh_sha256": sha(mesh), "step": str(step.relative_to(HERE)),
                     "step_sha256": sha(step), "bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
                     "valid_native_solid": bool(shape.isValid()), "native_solid_count": len(shape.Solids()),
                     "volume_mm3": float(shape.Volume()), "triangles": len(f)}},
        "sources": facts["sources"],
        "unpublished": ["Exact physical dimensions", "Outlet pressure tolerance and flow curve",
                        "Maximum inlet pressure and service temperature", "Exact housing polymer"],
    }
    (HERE/"dimensions.json").write_text(json.dumps(dims, indent=2)+"\n")
    print(json.dumps({"estimated_envelope": dims["estimated_envelope"],
                      "tube_ports": dims["tube_ports"],
                      "valid_native_solid": bool(shape.isValid()),
                      "native_solid_count": len(shape.Solids()), "triangles": len(f)}, indent=2))


if __name__ == "__main__":
    export()
