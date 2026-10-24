"""Protect-Air EcoReg239KS1245 water-regulator layout reference.

Manual CAD-queue build. Published body dimensions control the envelope;
axial shoulder locations and made-up adapter reaches remain estimates.
"""
from pathlib import Path
import hashlib
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "hardware/cad-artifacts.json").is_file())
BODY_LENGTH = 52.
BODY_MAX_DIAMETER = 34.
WRENCH_AF = 17.
LONG_NECK_D = 19.
SHORT_NECK_D = 20.
NPT_SHANK_D = 13.7
NPT_ENGAGEMENT = 11.
JG_COLLET_D = 14.
JG_COLLET_LENGTH = 13.5
JG_HEX_CORNERS = 16.5
JG_HEX_LENGTH = 5.
ADAPTER_EXPOSED = JG_COLLET_LENGTH + JG_HEX_LENGTH
ADAPTER_TOTAL = ADAPTER_EXPOSED + NPT_ENGAGEMENT
TUBE_D = 6.35

# The long inlet and short outlet ends follow the OEM outline and flow arrow.
# Main shoulder stations are estimated from that outline, not dimensioned.
BODY_PROFILE = [(0., 9.5), (18.8, 9.5), (22., 12.1), (27.2, 15.2),
                (29.4, 17.), (39.3, 17.), (40.5, 16.5), (43.8, 10.), (52., 10.)]
JG_SOURCE = "hardware/reference/jg-pp010822e/jg_pp010822e.py"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cylinder(radius, x0, x1):
    return cq.Solid.makeCylinder(radius, x1-x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def turned(profile):
    points = [(0, profile[0][0]), *((r, x) for x, r in profile), (0, profile[-1][0])]
    return (cq.Workplane("XZ").polyline(points).close().revolve(360, (0, 0), (0, 1)).val()
            .rotate((0, 0, 0), (0, 1, 0), 90))


def wrench_pair(solid, x0, x1):
    # Two opposed flats retain the stated round neck diameter on the other
    # radial axis. The exact number/clock of wrench flats is not established.
    box = cq.Solid.makeBox(x1-x0+2., WRENCH_AF, 50., cq.Vector(x0-1., -WRENCH_AF/2, -25.))
    return solid.intersect(box)


def body():
    long_neck = wrench_pair(turned(BODY_PROFILE[:2]), 0., 18.8)
    center = turned(BODY_PROFILE[1:-1])
    short_neck = wrench_pair(turned(BODY_PROFILE[-2:]), 43.8, BODY_LENGTH)
    outer = long_neck.fuse(center, short_neck).clean()
    # Simplified female thread occupancy sockets; internal regulation is not drawn.
    return outer.cut(cylinder(NPT_SHANK_D/2, -.01, NPT_ENGAGEMENT)).cut(
        cylinder(NPT_SHANK_D/2, BODY_LENGTH-NPT_ENGAGEMENT, BODY_LENGTH+.01))


def jg_adapter():
    # Frozen nominal PP010822E sections from the current existing reference.
    collet = cq.Workplane("XY").circle(JG_COLLET_D/2).extrude(JG_COLLET_LENGTH)
    hexagon = (cq.Workplane("XY").workplane(offset=JG_COLLET_LENGTH)
               .polygon(6, JG_HEX_CORNERS).extrude(JG_HEX_LENGTH))
    shank = (cq.Workplane("XY").workplane(offset=ADAPTER_EXPOSED)
             .circle(NPT_SHANK_D/2).extrude(NPT_ENGAGEMENT))
    solid = collet.union(hexagon).union(shank).val().rotate((0, 0, 0), (0, 1, 0), 90)
    return solid.cut(cylinder(TUBE_D/2, -.01, ADAPTER_TOTAL+.01))


def pieces():
    regulator = body()
    adapter = jg_adapter()
    inlet = adapter.translate((-ADAPTER_EXPOSED, 0, 0))
    outlet = adapter.rotate((0, 0, 0), (0, 1, 0), 180).translate((BODY_LENGTH+ADAPTER_EXPOSED, 0, 0))
    return [("ecoreg-body", regulator), ("ecoreg-inlet-adapter", inlet), ("ecoreg-outlet-adapter", outlet)]


def port(point, outward, kind, insertion=None):
    result = {"point_mm": list(point), "outward_axis": list(outward), "kind": kind}
    if insertion is not None:
        result["engagement_mm"] = insertion
    return result


def export():
    folder = HERE/"geometry"
    folder.mkdir(exist_ok=True)
    assembly = cq.Assembly(name="EcoReg239KS1245_with_nominal_JG_water_adapters")
    bare = cq.Assembly(name="EcoReg239KS1245_body")
    records, all_v, all_f, offset = {}, [], [], 0
    face_records = {}
    for name, solid in pieces():
        assembly.add(solid, name=name, color=cq.Color(.14, .15, .16) if name == "ecoreg-body" else cq.Color(.1, .11, .12))
        if name == "ecoreg-body":
            bare.add(solid, name=name, color=cq.Color(.14, .15, .16))
            for label, selector, p, axis in [
                ("inlet_1_4NPT_face", "<X", [0., 0., 0.], [-1., 0., 0.]),
                ("outlet_1_4NPT_face", ">X", [BODY_LENGTH, 0., 0.], [1., 0., 0.])]:
                face = cq.Workplane().add(solid).faces(selector).val()
                assembly.objects[name].addSubshape(face, name=label)
                bare.objects[name].addSubshape(face, name=label)
                face_records[label] = {"point_mm": p, "outward_normal": axis,
                                      "native_face_area_mm2": float(face.Area())}
        vv, ff = solid.tessellate(.035, .12)
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
    assembly_path = folder/"ecoreg-with-adapters.step"
    bare_path = folder/"ecoreg-regulator.step"
    assembly.export(str(assembly_path)); bare.export(str(bare_path))
    v, f = np.vstack(all_v), np.vstack(all_f)
    mesh = folder/"ecoreg-with-adapters.npz"
    np.savez_compressed(mesh, v=v, f=f)
    dims = {
        "units": "mm", "candidate": "Protect-Air EcoReg239KS1245 fixed45psi liquid regulator",
        "status": "Research/layout candidate; not selected, purchased or installed",
        "canonical_frame": "Native+Xflow from long inlet neckX0 to short outlet neckX52; radial axesY/Z",
        "published_body": {"overall_length_mm": BODY_LENGTH, "maximum_diameter_mm": BODY_MAX_DIAMETER,
            "long_inlet_neck_diameter_mm": LONG_NECK_D, "short_outlet_neck_diameter_mm": SHORT_NECK_D,
            "wrench_across_flats_mm": WRENCH_AF, "inlet_thread": "1/4NPT female", "outlet_thread": "1/4NPT female",
            "preset_psi": 45., "maximum_water_inlet_psi": 145., "water_temperature_C": [4., 60.],
            "housing_material": "GrivoryGV-5FWA"},
        "body_estimates": {"profile_x_radius_mm": BODY_PROFILE,
            "wrench_geometry": "Two opposed17mm flats on each neck; exact count/clock of flats not established",
            "socket_occupancy_diameter_mm": NPT_SHANK_D, "socket_occupancy_depth_mm": NPT_ENGAGEMENT,
            "scope": "Undimensioned axial transitions and plain socket bores are layout estimates. No regulator mechanism, NPT helix or sealing geometry is modeled."},
        "named_faces": face_records,
        "body_ports": {
            "inlet": port([0., 0., 0.], [-1., 0., 0.], "female1/4NPT"),
            "outlet": port([BODY_LENGTH, 0., 0.], [1., 0., 0.], "female1/4NPT")},
        "nominal_adapters": {"part": "JohnGuest PP010822E water-path male connector",
            "reference_source": JG_SOURCE, "reference_source_sha256": sha(ROOT/JG_SOURCE),
            "source_sections_mm": {"collet_diameter": JG_COLLET_D, "collet_length": JG_COLLET_LENGTH,
                "hex_corner_diameter": JG_HEX_CORNERS, "hex_length": JG_HEX_LENGTH,
                "thread_envelope_diameter": NPT_SHANK_D, "thread_length": NPT_ENGAGEMENT},
            "exposed_reach_each_mm": ADAPTER_EXPOSED, "nominal_thread_engagement_each_mm": NPT_ENGAGEMENT,
            "tube_bore_diameter_mm": TUBE_D, "tube_insertion_estimate_mm": 12.7,
            "scope": "Nominal existing reference reused with a6.35mm open display bore. Adapter exterior, actual NPTmake-up and exact tube insertion are not measured;89mm is a layout estimate, not a measured made-up stack."},
        "tube_ports": {
            "inlet": port([-ADAPTER_EXPOSED, 0., 0.], [-1., 0., 0.], "1/4tube_socket"),
            "outlet": port([BODY_LENGTH+ADAPTER_EXPOSED, 0., 0.], [1., 0., 0.], "1/4tube_socket")},
        "nominal_tube_mouth_span_mm": BODY_LENGTH+2*ADAPTER_EXPOSED,
        "assembly_bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
        "assembly_mesh": str(mesh.relative_to(HERE)), "assembly_mesh_sha256": sha(mesh),
        "assembly_step": str(assembly_path.relative_to(HERE)), "assembly_step_sha256": sha(assembly_path),
        "named_body_step": str(bare_path.relative_to(HERE)), "named_body_step_sha256": sha(bare_path),
        "geometry": records,
        "sources": [
            {"title": "EPSGroup239KS1245 product listing", "url": "https://store.epsgroupllc.com/ecoreg-45-psi-inline-liquid-pressure-regulator-239ks1245/",
             "verified_date": "2026-10-23", "snapshot": {"price_USD": 48., "quantity_in_stock": 6, "stated_shipping": "Usually ships within24hours"}},
            {"title": "Protect-Air EcoReg technical data", "url": "https://store.epsgroupllc.com/content/pdf/Technical-Data-EcoReg.pdf",
             "local": "sources/technical-data.pdf", "sha256": sha(HERE/"sources/technical-data.pdf"), "page": 1,
             "supports": "52mm full-body length,34mm maximum diameter,19/20mm necks,17AF,239KS1245 NPT45psi row and water-service data"},
            {"title": "Protect-Air series239 installation instructions", "url": "https://store.epsgroupllc.com/content/pdf/EcoReg-Instructions.pdf",
             "local": "sources/instructions.pdf", "sha256": sha(HERE/"sources/instructions.pdf"), "page": 1,
             "supports": "Any mounting orientation; follow body flow arrow; fixed preset; drinking/mains water application"},
        ],
    }
    (HERE/"dimensions.json").write_text(json.dumps(dims, indent=2)+"\n")
    print(json.dumps({"body": dims["published_body"], "tube_ports": dims["tube_ports"],
        "nominal_tube_mouth_span_mm": dims["nominal_tube_mouth_span_mm"],
        "assembly_bounds_mm": dims["assembly_bounds_mm"],
        "all_native_parts_valid": all(p["valid_native_solid"] for p in records.values())}, indent=2))


if __name__ == "__main__":
    export()
