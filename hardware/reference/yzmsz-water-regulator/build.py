"""Scan-fitted YZMSZ B0CGS34P93 fixed 0.3 MPa regulator exterior."""
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from _cadq_export import _atomic_write, _write_payload_beside

PARAMETERS = json.loads((HERE / 'reference-parameters.json').read_text())
LENGTH = PARAMETERS['length_mm']
PROFILE = PARAMETERS['profile_x_radius_mm']
DIAMETER = 2 * max(r for x, r in PROFILE)
TUBE_OD = 6.35
INSERTION = 15.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def body():
    points = [(0.0, 0.0), *((r, x) for x, r in PROFILE), (0.0, LENGTH)]
    shape = (cq.Workplane("XZ").polyline(points).close()
             .revolve(360, (0, 0), (0, 1)).val()
             .rotate((0, 0, 0), (0, 1, 0), 90))
    # Blind display sockets and their entrance bevels carry no claim about
    # insertion stops, seals, internals or the pressure-bearing wall thickness.
    for x, sign in [(0, 1), (LENGTH, -1)]:
        bore = cq.Solid.makeCylinder(TUBE_OD/2, INSERTION+.02,
            cq.Vector(x-sign*.01, 0, 0), cq.Vector(sign, 0, 0))
        entrance = cq.Solid.makeCone(4.15, TUBE_OD/2, .75,
            cq.Vector(x-sign*.01, 0, 0), cq.Vector(sign, 0, 0))
        shape = shape.cut(bore.fuse(entrance))
    for name, x, sign in [('inlet', 0, 1), ('outlet', LENGTH, -1)]:
        record = PARAMETERS['release_recesses'][name]
        inner = record['inner_profile_inward_radius_mm']
        outline = [(-.02, record['outer_radius_mm']), (-.02, inner[0][1]), *[tuple(p) for p in inner]]
        pocket = cq.Workplane('XY').polyline(outline).close().revolve(360, (0, 0), (1, 0)).val()
        if sign < 0:
            pocket = pocket.rotate((0, 0, 0), (0, 1, 0), 180).translate((x, 0, 0))
        shape = shape.cut(pocket)
    windows = PARAMETERS['windows']
    lo, hi = windows['x_range_mm']
    for angle in windows['angles_degrees']:
        recess = cq.Solid.makeBox(hi-lo, 8., windows['tangent_width_mm'],
            cq.Vector(lo, windows['bottom_radius_mm'], -windows['tangent_width_mm']/2))
        shape = shape.cut(recess.rotate((0, 0, 0), (1, 0, 0), angle))
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
    # This assembly contains one solid. Export it directly so its two named
    # mouth faces survive the STEP writer, alongside the matching viewer mesh.
    _atomic_write(str(step), lambda path: assembly.export(path))
    _write_payload_beside(str(step), assembly)
    vv, ff = shape.tessellate(.035, .12)
    v = np.array([p.toTuple() for p in vv], dtype=np.float32)
    f = np.array(ff, dtype=np.int32)
    np.savez_compressed(mesh, v=v, f=f)
    facts = json.loads((HERE/"sources/product-facts.json").read_text())
    dims = {
        "units": "mm",
        "part": "YZMSZ fixed 0.3 MPa water pressure regulator, ASIN B0CGS34P93",
        "selected_variant": "1/4 inch O.D. 0.3 MPa Pressure",
        "status": "Purchased reference; scan-fitted exterior",
        "canonical_frame": "Native +X flow; broad/windowed inlet release face X0 to narrow-neck outlet release face at measured length",
        "published": {"tube_od_mm": TUBE_OD, "connection_type": "Native push-connect at both ends",
                      "fixed_outlet_pressure_MPa": 0.3, "fixed_outlet_pressure_psi": 43.5113,
                      "application": "Reverse osmosis and household water filtration",
                      "housing_material": "Engineering plastic, exact polymer unspecified"},
        "measured_envelope": {"tube_mouth_span_mm": LENGTH, "maximum_diameter_mm": DIAMETER,
                               "profile_x_radius_mm": PROFILE,
                               "basis": "872-frame native MINI 2 capture, 0.10 mm fusion, rigid registration at unit scale; scan-evidence.json",
                               "scope": "Fitted exterior with rotational continuation below the putty boundary. Window cuts approximate their observed opening. Blind bore closures and 15 mm insertion remain display estimates."},
        "tube_ports": {"inlet": port(0.0, -1.0), "outlet": port(LENGTH, 1.0)},
        "named_faces": named_faces,
        "geometry": {"yzmsz-water-regulator": {"mesh": str(mesh.relative_to(HERE)),
                     "mesh_sha256": sha(mesh), "step": str(step.relative_to(HERE)),
                     "step_sha256": sha(step), "bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
                     "valid_native_solid": bool(shape.isValid()), "native_solid_count": len(shape.Solids()),
                     "volume_mm3": float(shape.Volume()), "triangles": len(f)}},
        "sources": facts["sources"],
        "scan_evidence_sha256": sha(HERE/'scan-evidence.json'),
        "reference_parameters_sha256": sha(HERE/'reference-parameters.json'),
        "unpublished": ["Calibrated absolute dimensions and paint thickness", "Outlet pressure tolerance and flow curve",
                        "Maximum inlet pressure and service temperature", "Exact housing polymer"],
    }
    (HERE/"dimensions.json").write_text(json.dumps(dims, indent=2)+"\n")
    print(json.dumps({"measured_envelope": dims["measured_envelope"],
                      "tube_ports": dims["tube_ports"],
                      "valid_native_solid": bool(shape.isValid()),
                      "native_solid_count": len(shape.Solids()), "triangles": len(f)}, indent=2))


if __name__ == "__main__":
    export()
