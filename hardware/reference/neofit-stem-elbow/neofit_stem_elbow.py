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

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('neofit_stem_elbow')
globals().update({name: _reference_values[name] for name in ('PARAMETER_SNAPSHOT_SHA256', 'PARAMETERS', 'TUBE_OD', 'STEM_OD', 'STEM_TIP_REACH', 'HUB_BACK_REACH', 'STEM_LENGTH', 'SOCKET_MOUTH_REACH', 'SOCKET_INSERTION', 'COLLAR_OD', 'OVERALL_STEM_AXIS', 'OVERALL_SOCKET_AXIS', 'FLOW_BORE')})




def socket():
    'Captured release face and outward axis, millimetres.'
    return _reference_data('neofit_stem_elbow', 'socket', (), {})


def stem_tip():
    return _reference_data('neofit_stem_elbow', 'stem_tip', (), {})


def stem_shoulder():
    return _reference_data('neofit_stem_elbow', 'stem_shoulder', (), {})


def seated_host_mouth(insertion=12.7):
    "Host release face after insertion; default is an unmeasured host estimate.\n\n    Specify the receiving fitting's actual engagement depth when known. The\n    family drawing's 16.891 mm female depth does not qualify every host socket.\n    "
    return _reference_data('neofit_stem_elbow', 'seated_host_mouth', (insertion,), {})


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
