"""Scan-fitted PISCO regulator and OEM-dimensioned Fluidfit reference."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from _cadq_export import export_assembly
LENGTH = 45.5
MAX_DIAMETER = 15.5
TUBE_DIAMETER = 6.35
INSERTION = 16.1
COLLET_LENGTH = 1.5

# Axisymmetric exterior estimated from the OEM outline. Native+Z follows
# its arrow from the short stepped socket to the long cylindrical end.
CHECK_PROFILE = [
    (1.5, 7.0), (2.2, 7.4), (4.0, 7.4), (4.4, 7.75),
    (8.2, 7.75), (8.7, 7.4), (9.2, 7.4), (9.6, 7.75),
    (10.2, 7.4), (13.8, 6.5), (14.3, 7.4), (15.5, 7.4),
    (16.0, 5.1), (17.5, 5.1), (17.5, 6.7), (22.0, 6.7),
    (24.0, 7.75), (41.6, 7.75), (42.5, 7.3), (44.0, 7.3),
]
REG_LENGTH = 62.4
REG_INSERTION = 17.


def regulator_parameters():
    return json.loads((HERE/'regulator-scan-parameters.json').read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cylinder(radius, z0, z1):
    return cq.Solid.makeCylinder(radius, z1-z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


def turned(profile):
    points = [(0, profile[0][0]), *((r, z) for z, r in profile), (0, profile[-1][0])]
    return cq.Workplane("XZ").polyline(points).close().revolve(360, (0, 0), (0, 1)).val()


def check_parts():
    # Both depths are OEM B values. The central display closure carries no
    # implied poppet, spring, seal, cracking or pressure mechanism.
    sockets = cylinder(TUBE_DIAMETER/2, -.01, INSERTION).fuse(
        cylinder(TUBE_DIAMETER/2, LENGTH-INSERTION, LENGTH+.01))
    body = turned(CHECK_PROFILE).cut(sockets)
    inlet_collet = cylinder(6.7, 0., COLLET_LENGTH).cut(sockets)
    outlet_collet = cylinder(6.7, LENGTH-COLLET_LENGTH, LENGTH).cut(sockets)
    return [("body", body), ("inlet_collet", inlet_collet), ("outlet_collet", outlet_collet)]


def regulator_parts():
    data = regulator_parameters()
    length = data['length_mm']
    sockets = cylinder(TUBE_DIAMETER/2, -.01, REG_INSERTION).fuse(
        cylinder(TUBE_DIAMETER/2, length-REG_INSERTION, length+.01))
    # The visibly enlarged inlet guide is a scan-fitted display counterbore.
    # The regulating mechanism and the hidden transition to seals are omitted.
    sockets = sockets.fuse(cylinder(4.0, -.01, 6.8))
    sockets = sockets.fuse(cq.Solid.makeCone(4., TUBE_DIAMETER/2, .7,
                          cq.Vector(0, 0, length+.01), cq.Vector(0, 0, -1)))
    profile = np.array(data['profile_z_radius_mm'])
    result = []
    for name in ('body', 'outlet_fitting', 'inlet_collet', 'outlet_collet'):
        lo, hi = data['component_ranges_mm'][name]
        middle = profile[(profile[:, 0] > lo) & (profile[:, 0] < hi)]
        trimmed = [[lo, float(np.interp(lo, profile[:, 0], profile[:, 1]))],
                   *middle.tolist(), [hi, float(np.interp(hi, profile[:, 0], profile[:, 1]))]]
        result.append((name, turned(trimmed).cut(sockets).clean()))
    return result


def export_candidate(candidate, title, pieces):
    folder = HERE/"geometry"
    folder.mkdir(exist_ok=True)
    assembly = cq.Assembly(name=title)
    merged_v, merged_f, offset = [], [], 0
    records = []
    for name, solid in pieces:
        color = cq.Color(.2, .22, .24) if candidate == "candidate-regulator" and name == "body" else (
            cq.Color(.66, .68, .7) if name == "outlet_fitting" else
            cq.Color(.62, .64, .65) if name == "body" else cq.Color(.78, .8, .81))
        assembly.add(solid, name=name, color=color)
        vv, ff = solid.tessellate(.035, .12)
        v = np.array([p.toTuple() for p in vv], dtype=np.float32)
        f = np.array(ff, dtype=np.int32)
        path = folder/(candidate+"-"+name+".npz")
        np.savez_compressed(path, v=v, f=f)
        merged_v.append(v); merged_f.append(f+offset); offset += len(v)
        records.append({"name": name, "mesh": path.name, "sha256": sha(path),
            "valid_native_solid": bool(solid.isValid()), "native_solid_count": len(solid.Solids()),
            "volume_mm3": float(solid.Volume()), "triangles": len(f)})
    step = folder/(candidate+".step")
    export_assembly(assembly, str(step))
    v, f = np.vstack(merged_v), np.vstack(merged_f)
    mesh = folder/(candidate+".npz")
    np.savez_compressed(mesh, v=v, f=f)
    return {"geometry": "geometry/"+candidate+".npz", "mesh_sha256": sha(mesh),
            "step": "geometry/"+candidate+".step", "step_sha256": sha(step),
            "bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
            "size_xyz_mm": np.ptp(v, axis=0).tolist(), "parts": records,
            "vertices": len(v), "triangles": len(f)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regulator-only', action='store_true', help='Export only the scanned PISCO reference.')
    args = parser.parse_args()
    check = (json.loads((HERE/'dimensions.json').read_text())['fluidfit_hcvu_quarter']
             if args.regulator_only else export_candidate("candidate-check", "Fluidfit_HCVU_quarter_inch_layout", check_parts()))
    regulator = export_candidate("candidate-regulator", "PISCO_RVFUP_quarter_inch_layout", regulator_parts())
    fitted = regulator_parameters()
    actual_length = fitted['length_mm']
    dimensions = {
        "units": "mm", "model_scope": "PISCO scanned exterior and Fluidfit OEM-dimensioned layout; no pressure-performance qualification implied",
        "canonical_frame": "Flow+Z, inlet release faceZ0, outlet release faceZlength; radial axesX/Y",
        "pisco_rvfup_quarter": {
            "requested_code": "RVFUP1/4-1/4-0.3", "dimensioned_oem_family": "RVFUP1/4-1/4 with preset code",
            "published": {"length_mm": REG_LENGTH, "max_diameter_mm": 21.5,
                "secondary_body_diameter_mm": 20., "L1_mm": 37.7, "L2_mm": 20.2,
                "tube_od_mm": TUBE_DIAMETER, "inlet_insertion_C1_mm": REG_INSERTION,
                "outlet_insertion_C2_mm": REG_INSERTION, "preset_MPa": .3, "preset_psi_catalog": 44,
                "maximum_service_pressure_MPa": 1., "maximum_service_pressure_psi_catalog": 145},
            "ports": {
                "inlet": {"point_mm": [0., 0., 0.], "outward_axis": [0., 0., -1.],
                          "tube_od_mm": TUBE_DIAMETER, "insertion_mm": REG_INSERTION,
                          "tube_stop_mm": [0., 0., REG_INSERTION]},
                "outlet": {"point_mm": [0., 0., actual_length], "outward_axis": [0., 0., 1.],
                           "tube_od_mm": TUBE_DIAMETER, "insertion_mm": REG_INSERTION,
                           "tube_stop_mm": [0., 0., actual_length-REG_INSERTION]},
            },
            "flow_mapping": "Long-neck IN is native Z0; short-neck OUT is at the measured mouth span; normal regulated flow +Z",
            "published_axial_landmarks_from_inlet_mm": {"B_minus_L1": 24.7, "B_minus_L2": 42.2},
            "fitted_exterior": {"mouth_span_mm": actual_length,
                "maximum_profile_diameter_mm": 2*max(r for z, r in fitted['profile_z_radius_mm']),
                "profile_z_radius_mm": fitted['profile_z_radius_mm'],
                "component_ranges_mm": fitted['component_ranges_mm'],
                "basis": "1,819-frame native MINI 2 capture at 0.10 mm fusion; regulator-scan-evidence.json",
                "scope": "Round housing, necks, retaining rings and release caps fitted from the exposed scan; hidden lower sectors continued rotationally; material boundaries are display interpretations"},
            "scan_evidence_sha256": sha(HERE/'regulator-scan-evidence.json'),
            "scan_parameters_sha256": sha(HERE/'regulator-scan-parameters.json'),
            "socket_scope": "Both blind bores reach17mm from release face, without modeling regulator internals",
            "operating_scope": "OEM specifies air and permits reverse free flow; retain a separate downstream check. Exact CO2 service is not established by this layout reference.",
            "source_materials": "OEM construction includes PBT resin body, aluminum fitting body, NBR/HNBR seals and POM release rings; the native solids estimate the visible material split",
            "source_pdf": "sources/pisco-preset-regulator.pdf", "source_pdf_sha256": sha(HERE/"sources/pisco-preset-regulator.pdf"),
            "source_pdf_drawing_page": 4, "source_pdf_specification_page": 3,
            "source_url": "https://shop.pisco.com/wp-content/themes/agency-ecommerce/assets/images/preset-regulator.pdf",
            "product_url": "https://shop.pisco.com/product/rvfup1-4-1-4-0-3/",
            **regulator,
        },
        "fluidfit_hcvu_quarter": {
            "requested_code": "HCVU1/4-1/4G", "dimensioned_oem_row": "HCVU1/4-1/4",
            "published": {"length_mm": LENGTH, "max_diameter_mm": MAX_DIAMETER,
                          "tube_od_mm": TUBE_DIAMETER, "tube_insertion_mm": INSERTION,
                          "weight_g": 7.4},
            "ports": {
                "inlet": {"point_mm": [0., 0., 0.], "outward_axis": [0., 0., -1.],
                          "tube_od_mm": TUBE_DIAMETER, "insertion_mm": INSERTION,
                          "tube_stop_mm": [0., 0., INSERTION]},
                "outlet": {"point_mm": [0., 0., LENGTH], "outward_axis": [0., 0., 1.],
                           "tube_od_mm": TUBE_DIAMETER, "insertion_mm": INSERTION,
                           "tube_stop_mm": [0., 0., LENGTH-INSERTION]},
            },
            "flow_mapping": "OEM arrow runs from the short stepped socket end to the long cylindrical-body end; that direction is native+Z",
            "estimated_form": {"collet_length_mm": COLLET_LENGTH, "collet_outer_diameter_mm": 13.4,
                               "body_profile_z_radius_mm": CHECK_PROFILE,
                               "scope": "Axial transitions, necks, collet detail and neutral gray display finish are outline-derived estimates; nominal overall and maximum diameter remain controlled by the OEM row"},
            "socket_scope": "Both blind bores reach16.1mm from their release faces, receiving the nominal full inserted stem without an artificial shallow display closure. The central valve mechanism is not modeled.",
            "source_pdf": "sources/fluidfit-hcvu-inch.pdf", "source_pdf_sha256": sha(HERE/"sources/fluidfit-hcvu-inch.pdf"),
            "source_url": "https://www.fluidfit.net/eng/open_content/product/view.php?pm_no=262",
            "source_drawing_url": "https://www.fluidfit.net/lib/pm_download.php?c_name=pdf_Metric_PT&pm_no=262",
            "catalog_url": "https://www.fluidfit.net/catalog/Catalog_Fluidfit_2026_eng.pdf",
            "application_scope": "Manufacturer POM-family catalog lists water, liquid foods, air and gas. Generic air/gas applicability is distinct from exact CO2 duty qualification.",
            "color_suffix_scope": "RequestedG variant uses the HCVU1/4-1/4 family's dimensions; no distinctG-suffix geometry is established here",
            **check,
        },
    }
    (HERE/"dimensions.json").write_text(json.dumps(dimensions, indent=2)+"\n")
    print(json.dumps({"candidate-check": check, "candidate-regulator": regulator}, indent=2))


if __name__ == "__main__":
    main()
