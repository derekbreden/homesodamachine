#!/usr/bin/env python3
"""Read cap fit, open crown and floor clearance at the retained native station."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/docgen').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/enclosure'))
import enclosure as enc  # noqa: E402

PRINT_INPUT = ROOT / '.cache/prints/2026-09-13-enclosure/enclosure-pump-cartridge-mark2-input.3mf'
PRINT_SHA = '9f84eb4edb3faba30243680036600c45f6a700ee7e884a7f0237940f153df372'


def fitted_cap_comparison(cap):
    """Compare the exact earlier print surface in a common pump-local frame."""
    assert hashlib.sha256(PRINT_INPUT.read_bytes()).hexdigest() == PRINT_SHA
    with zipfile.ZipFile(PRINT_INPUT) as archive:
        root = ET.fromstring(archive.read('3D/Objects/object_2.model'))
    vertices = np.array([tuple(float(v.attrib[a]) for a in ('x', 'y', 'z'))
                         for v in root.iter() if v.tag.endswith('}vertex')])
    faces = np.array([tuple(int(v.attrib[a]) for a in ('v1', 'v2', 'v3'))
                     for v in root.iter() if v.tag.endswith('}triangle')])
    provenance = json.loads(PRINT_INPUT.with_name(
        'enclosure-pump-cartridge-mark2.provenance.json').read_text())
    printed = provenance['parts'][1]
    vertices += np.asarray(printed['model_bounds_mm']).mean(0)
    # The input's cylinder centers are Y45.009; the archived native station uses Y44.909.
    # Both values are readings of their own geometry; this is a rigid placement translation.
    vertices[:, 1] -= .1
    mesh = trimesh.Trimesh(vertices, faces, process=False)
    points = np.vstack((mesh.vertices, mesh.triangles_center))
    selected = ((points[:, 2] > 216.) & (points[:, 2] < 270.)
                & (abs(points[:, 0]) > 25.) & (abs(points[:, 0]) < 78.)
                & (points[:, 1] > 18.) & (points[:, 1] < 71.))
    points = points[selected]
    verts, tris = cap.tessellate(.005, .1)
    current = trimesh.Trimesh([v.toTuple() for v in verts], tris, process=False)
    _, distances, _ = trimesh.proximity.closest_point(current, points)
    assert len(points) > 200
    assert distances.max() < .025, 'Fitted cap surface differs from the earlier print'
    return {
        'input_project': str(PRINT_INPUT.relative_to(ROOT)), 'input_sha256': PRINT_SHA,
        'printed_cap_stl_sha256': printed['sha256'],
        'rigid_translation_mm': [0., -.1, 0.], 'sample_count': len(points),
        'maximum_surface_distance_mm': float(distances.max()),
        'p95_surface_distance_mm': float(np.quantile(distances, .95)),
        'scope': 'Earlier printed mesh vertices and triangle centers on the fitted boss/can band; excludes crown, screws, outer boundary and aft extension. Difference includes mesh chord approximation.',
        'physical_binding': 'Earlier print available in retained job provenance; Derek confirms the existing assembled cap fit but has not identified its job date.'}


def check(native_dir):
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    measured = json.loads((HERE / 'scan-measurements.json').read_text())
    fixture = evidence['native_contact_fixture']
    trays = fixture['pump_trays']
    box = SimpleNamespace(pack=SimpleNamespace(pump_trays=trays,
                          collet_plate=fixture['collet_plate']),
                          inner=fixture['inner'], pump_bay=fixture['pump_bay'])
    native_path = native_dir / 'enclosure-pump-cartridge.step'
    native_hash = hashlib.sha256(native_path.read_bytes()).hexdigest()
    assert native_hash == evidence['native_baseline']['sha256'][native_path.name]
    cradle = cq.importers.importStep(str(native_path)).val()
    cap = enc.build_pump_cap(box).val()
    assert cap.isValid() and len(cap.Solids()) == 1
    base, crown = enc.cap_base_z(trays), enc.cap_crown_z(box)
    assert abs(cap.BoundingBox().zmin-base) < 1e-6
    assert abs(crown-(box.pump_bay[2]-enc.pump_cartridge_top_clearance)) < 1e-6
    path = []
    for dz in (-enc.cap_lift_clearance, 0., .25, 5., 35., 70.):
        foul = cap.translate((0, 0, dz)).intersect(cradle).Volume()
        assert foul < 1e-5, f'Cap/cradle interference at lift {dz}: {foul} mm3'
        path.append({'lift_mm': dz, 'interference_mm3': foul})
    openings = []
    for cx, cy, _ in trays:
        bottom = enc.cap_terminal_opening_z(box)
        room = enc._zcyl(enc.cap_terminal_opening_r-.001,
                          cx, cy+enc.clamp_pump_y_shift, bottom+.001, crown+1.)
        assert cap.intersect(room).Volume() < 1e-5
        openings.append({'center_xy_mm':[cx,cy+enc.clamp_pump_y_shift],
                         'diameter_mm':2*enc.cap_terminal_opening_r,
                         'bottom_z_mm':bottom, 'top_z_mm':crown})
    land = enc.pump_skirt_support_z(trays)
    floor_bottom, floor_top = enc.bay_floor_z(trays)
    front_height = measured['baseline_front_rim']['head_front_height_above_skirt_land_mm']['min']
    front_air = land+front_height-floor_top
    envelope_air = land-enc._tray.head_front_below_skirt-floor_top
    assert min(front_air,envelope_air) >= enc.fits.running
    assert floor_top-floor_bottom >= 4.
    assert abs(land-measured['native_placement']['native_cradle_bearing_z_mm']) < .001
    floor = enc._bay_floor(fixture['inner'],fixture['y_joint'],fixture['collet_plate'],trays)
    assert floor.isValid()
    for cx,cy,_ in trays:
        above=enc._ybox(cx-32,cx+32,enc.front_plane_y,cy+33,floor_top+.001,floor_top+2.)
        below=enc._ybox(cx-32,cx+32,enc.front_plane_y,cy+33,floor_top-.1,floor_top-.001)
        assert floor.intersect(above).Volume() < 1e-5
        assert below.cut(floor).Volume() < 1e-5
    return {
        'status':'passed_bounded_native_fit_and_clearance_checks',
        'native_cradle_step_sha256':native_hash,
        'cap_valid':True,'cap_solids':1,'broad_base_z_mm':base,
        'cap_cradle_sampled_vertical_path':path,
        'fitted_cap_comparison':fitted_cap_comparison(cap),
        'open_terminal_wells':openings,
        'land_z_mm':land,'floor_z_mm':[floor_bottom,floor_top],
        'minimum_floor_stock_mm':floor_top-floor_bottom,
        'minimum_air_above_floor_observed_mm':front_air,
        'minimum_air_above_floor_declared_envelope_mm':envelope_air,
        'scan_placement_scope':'Clearance assumes the observed underside strips are seated on the native lands. Actual cap contact surfaces are not independently identified.',
        'physical_fit':'Derek confirms both pumps held firmly with no vertical play in the existing assembled cartridge/cap; physical-fit.json.',
        'support_access':'Crown-down print; upper motor-well annuli are flat supported faces open axially to the bed. Support leaves through the same open wells.',
        'remaining_assembly_test':'Raised crown connector clearance, full enclosure insertion, four tube connections and spring-loaded carrier operation.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-dir',type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('command',nargs='?',choices=['selftest'])
    args=parser.parse_args()
    evidence=json.loads((HERE/'scan-evidence.json').read_text())
    native_dir=args.native_dir or Path(evidence['capture_archive'])/evidence['native_baseline']['directory']
    result=check(native_dir)
    if args.out: args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS cap/floor: fitted surface max {result["fitted_cap_comparison"]["maximum_surface_distance_mm"]:.4f} mm; floor stock {result["minimum_floor_stock_mm"]:.3f} mm; open crown and native lift path.')


if __name__ == '__main__': main()
