"""Scan-fitted neoFit ATEU44W 1/4-inch tube x 1/4-inch stem elbow.

The axes cross at the origin; female socket opens +Y and the male stem points
-X. The reference retains the exposed free stem and socket datums from two
oppositely mounted specimens, with a nominal orthogonal crossing and 6.35 mm
straight male diameter. Hidden passages are display geometry.
"""
from pathlib import Path
import argparse
import json
import math
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]/'scripts'))
from _cadq_export import export_assembly
from _materials import M_NEOFIT_WHITE_ACETAL

STEP = HERE/'neofit-stem-elbow.step'
# Frozen measurements keep layout imports independent of local scan archives.
PARAMETER_SNAPSHOT_SHA256 = 'a6d4486619514f64cad829bd281c90216c04cb94813d2784adea6a8a23fd5d8f'
PARAMETERS = {'units': 'mm',
 'material_id': 'HSM-000330',
 'tube_od_mm': 6.35,
 'stem_od_mm': 6.35,
 'stem_tip_x_mm': -27.02535353479422,
 'stem_shoulder_x_mm': -6.113547528963171,
 'socket_mouth_y_mm': 21.082366093950743,
 'stem_length_mm': 20.91180600583105,
 'flow_bore_display_mm': 4.3,
 'published_socket_insertion_mm': 16.891,
 'fixed_nose_y_mm': 19.0,
 'collet_start_y_mm': 19.08,
 'bend_radius_mm': 5.066279836802499,
 'collet_ellipse': {'center_xz_mm': [-0.06848629126006257, -0.05282793793301456],
                    'angle_radians': 0.297310387790615,
                    'minor_major_ratio': 0.8413251285872266},
 'profiles': {'fixed_body_y': [[0.0, 5.11019],
                               [4.95, 5.09439],
                               [5.35, 5.13339],
                               [5.45, 5.21773],
                               [5.55, 5.42916],
                               [5.65, 6.26253],
                               [5.75, 6.53757],
                               [5.95, 6.83879],
                               [6.25, 7.10216],
                               [6.65, 7.24498],
                               [7.95, 7.30081],
                               [8.55, 7.71255],
                               [9.05, 7.83786],
                               [14.95, 7.89743],
                               [15.65, 7.86289],
                               [15.95, 7.72594],
                               [16.25, 7.45757],
                               [16.45, 7.35603],
                               [16.75, 7.30671],
                               [17.95, 7.28925],
                               [18.45, 7.07686],
                               [18.65, 6.87668],
                               [18.85, 6.34219],
                               [18.95, 5.74134],
                               [19.0, 5.74134]],
              'release_collet_y': [[19.08, 6.08151],
                                   [19.33, 6.11464],
                                   [19.83, 5.93075],
                                   [20.63, 5.85555],
                                   [21.08237, 5.72046]],
              'stem_x': [[-27.02535, 3.0],
                         [-26.80535, 3.175],
                         [-6.25355, 3.175],
                         [-6.13355, 4.75],
                         [-6.07535, 4.76682],
                         [-5.97535, 4.91636],
                         [-5.8, 4.99467],
                         [-5.5, 5.08],
                         [0.0, 5.08]]},
 'scan_evidence_sha256': '3e0b546b32ac3c669df6d45378f6d28642550becc5c6e87d00e01f29baa7b559'}

TUBE_OD = PARAMETERS['tube_od_mm']
STEM_OD = PARAMETERS['stem_od_mm']
STEM_TIP_REACH = -PARAMETERS['stem_tip_x_mm']
HUB_BACK_REACH = -PARAMETERS['stem_shoulder_x_mm']
STEM_LENGTH = PARAMETERS['stem_length_mm']
SOCKET_MOUTH_REACH = PARAMETERS['socket_mouth_y_mm']
SOCKET_INSERTION = PARAMETERS['published_socket_insertion_mm']
COLLAR_OD = 2*max(r for y, r in PARAMETERS['profiles']['fixed_body_y'])
OVERALL_STEM_AXIS = STEM_TIP_REACH+COLLAR_OD/2
OVERALL_SOCKET_AXIS = SOCKET_MOUTH_REACH+PARAMETERS['bend_radius_mm']
FLOW_BORE = PARAMETERS['flow_bore_display_mm']


def socket():
    """Captured release face and outward axis, millimetres."""
    return (0., SOCKET_MOUTH_REACH, 0.), (0., 1., 0.)


def stem_tip():
    return (-STEM_TIP_REACH, 0., 0.), (-1., 0., 0.)


def stem_shoulder():
    return (-HUB_BACK_REACH, 0., 0.), (-1., 0., 0.)


def seated_host_mouth(insertion=12.7):
    """Host release face after insertion; default is an unmeasured host estimate.

    Specify the receiving fitting's actual engagement depth when known. The
    family drawing's 16.891 mm female depth does not qualify every host socket.
    """
    if not 0 < insertion <= STEM_LENGTH:
        raise ValueError('Insertion must fit within the male stem')
    return (insertion-STEM_TIP_REACH, 0., 0.), (-1., 0., 0.)


def _turned_x(profile):
    outline = [(profile[0][0], 0), *profile, (profile[-1][0], 0)]
    return cq.Workplane('XY').polyline(outline).close().revolve(360, (0, 0), (1, 0)).val()


def _turned_y(profile):
    return cq.Workplane(obj=_turned_x(profile).rotate((0, 0, 0), (0, 0, 1), 90))


def _corridor(radius, length, origin, axis):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*origin), cq.Vector(*axis))


def build():
    """Named fixed body/stem and release collet as CadQuery workplanes."""
    p = PARAMETERS
    core = cq.Workplane('XY').sphere(p['bend_radius_mm']).val()
    fixed = _turned_y(p['profiles']['fixed_body_y']).val()
    stem = _turned_x(p['profiles']['stem_x'])
    body = core.fuse(fixed).fuse(stem)
    body = body.cut(_corridor(FLOW_BORE/2, STEM_TIP_REACH+.1,
                              (-STEM_TIP_REACH-.05, 0, 0), (1, 0, 0)))
    body = body.cut(_corridor(FLOW_BORE/2, SOCKET_MOUTH_REACH+.1,
                              (0, -.05, 0), (0, 1, 0)))
    socket_clearance = _corridor(TUBE_OD/2, SOCKET_INSERTION+.1,
                                 (0, SOCKET_MOUTH_REACH-SOCKET_INSERTION, 0), (0, 1, 0))
    body = body.cut(socket_clearance).clean().fix()
    oval = p['collet_ellipse']
    scale = cq.Matrix([[1, 0, 0, 0], [0, 1, 0, 0],
                       [0, 0, oval['minor_major_ratio'], 0], [0, 0, 0, 1]])
    collet = (_turned_y(p['profiles']['release_collet_y']).val().transformGeometry(scale)
              .rotate((0, 0, 0), (0, 1, 0), -math.degrees(oval['angle_radians']))
              .translate((oval['center_xz_mm'][0], 0, oval['center_xz_mm'][1])))
    collet = collet.cut(socket_clearance).clean().fix()
    return [('body_and_stem', cq.Workplane(obj=body)),
            ('release_collet', cq.Workplane(obj=collet))]


def build_assembly():
    assembly = cq.Assembly(name='neoFit_ATEU44W_scan_reference')
    for name, piece in build():
        assembly.add(piece, name=name, color=M_NEOFIT_WHITE_ACETAL)
    return assembly


def export_stl(shape, path):
    """Native tessellation with zero-area pole triangles removed, without filling."""
    path = Path(path)
    cq.exporters.export(shape, str(path), tolerance=.025, angularTolerance=.08)
    raw = path.read_bytes()
    record = np.dtype([('normal', '<f4', 3), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
    count = int.from_bytes(raw[80:84], 'little')
    triangles = np.frombuffer(raw, dtype=record, count=count, offset=84)
    v = triangles['vertices'].astype(float)
    keep = np.linalg.norm(np.cross(v[:, 1]-v[:, 0], v[:, 2]-v[:, 0]), axis=1) > 1e-10
    removed = int((~keep).sum())
    if removed:
        path.write_bytes(raw[:80]+int(keep.sum()).to_bytes(4, 'little')+triangles[keep].tobytes())
    return removed


def export(stl=None):
    pieces = build(); assembly = cq.Assembly(name='neoFit_ATEU44W_scan_reference')
    verts, faces, offset, checks = [], [], 0, []
    for name, piece in pieces:
        solid = piece.val()
        if not solid.isValid():
            raise ValueError(f'Invalid reference solid: {name}')
        checks.append({'name': name, 'valid': True, 'solids': len(solid.Solids()),
                       'volume_mm3': solid.Volume()})
        assembly.add(piece, name=name, color=M_NEOFIT_WHITE_ACETAL)
        vv, ff = solid.tessellate(.025, .08)
        v = np.asarray([p.toTuple() for p in vv], dtype=np.float32); f = np.asarray(ff, dtype=np.int32)
        triangles = v[f].astype(float)
        keep = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0]), axis=1) > 1e-10
        f = f[keep]
        np.savez_compressed(HERE/f'{name}.npz', v=v, f=f)
        verts.append(v); faces.append(f+offset); offset += len(v)
    export_assembly(assembly, str(STEP))
    v, f = np.vstack(verts), np.vstack(faces)
    np.savez_compressed(HERE/'neofit-stem-elbow.npz', v=v, f=f)
    if stl:
        export_stl(assembly.toCompound(), stl)
    record = {'units': 'mm', 'pieces': checks, 'bounds_mm': [v.min(0).tolist(), v.max(0).tolist()],
              'vertices': len(v), 'triangles': len(f), 'socket': socket(), 'stem_tip': stem_tip(),
              'stem_shoulder': stem_shoulder(), 'estimated_unknown_host_mouth': seated_host_mouth()}
    (HERE/'model-check.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, help='Also export a portable STL.')
    args = parser.parse_args(); export(args.stl)
