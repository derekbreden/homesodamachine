"""John Guest PP061208W: 3/8-inch stem to 1/4-inch push-connect reducer.

The exposed exterior follows the threaded ASSE assembly scan. The buried male
tip uses a nominal 18.29 mm stem-to-shoulder length; internal passages and the
stop are display geometry. Frame: stem tip X0, axis +X, socket mouth at +X.
"""
from pathlib import Path
import argparse
import json
import math
import sys

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == 'hardware')
sys.path.insert(0, str(_hw/'scripts'))
from _cadq_export import export_assembly
from _materials import M_JG_WHITE_PP

STEP = _here.with_name('jg-pp061208w.step')
# Frozen component measurements keep layout imports independent of scan files.
PARAMETER_SNAPSHOT_SHA256 = '605b991c076da190a2655bdeda8b7d49691228aa4dbbbada204f4be7200971e4'
PARAMETERS = {'units': 'mm',
 'part': 'John Guest PP061208W',
 'nominal_stem_diameter_mm': 9.525,
 'nominal_free_stem_to_shoulder_mm': 18.29,
 'stem_tip_chamfer_display_mm': 0.6,
 'source_stem_tip_station_mm': 75.83561645217995,
 'source_shoulder_station_mm': 94.12561645217995,
 'source_release_station_mm': 107.76171740799833,
 'source_body_end_station_mm': 106.175,
 'source_collet_start_station_mm': 106.255,
 'stem_cylinder_end_mm': 17.239383547820054,
 'body_face_x_mm': 30.33938354782005,
 'collet_start_x_mm': 30.419383547820047,
 'length_mm': 31.926100955818384,
 'body_profile_x_radius_mm': [[17.239383547820054, 4.805],
                              [17.639383547820046, 4.962],
                              [18.03938354782005, 5.358],
                              [18.239383547820054, 6.281],
                              [18.439383547820057, 6.59],
                              [18.83938354782005, 6.858],
                              [19.639383547820046, 6.959],
                              [22.239383547820054, 6.951],
                              [22.639383547820046, 7.11],
                              [23.439383547820057, 7.921],
                              [23.83938354782005, 8.184],
                              [27.03938354782005, 8.293],
                              [27.439383547820057, 8.26],
                              [27.83938354782005, 8.045],
                              [28.03938354782005, 7.277],
                              [28.239383547820054, 7.076],
                              [29.639383547820046, 7.252],
                              [30.03938354782005, 7.055],
                              [30.239383547820054, 6.118],
                              [30.33938354782005, 5.802000000000023]],
 'collet_profile_x_radius_mm': [[30.419383547820047, 5.549200000000031],
                                [30.439383547820057, 5.486],
                                [30.83938354782005, 5.305],
                                [31.926100955818384, 5.255861473725293]],
 'nominal_tube_diameter_mm': 6.35,
 'tube_bore_display_diameter_mm': 6.48,
 'through_bore_display_diameter_mm': 5.84,
 'body_face_to_stop_display_mm': 14.1,
 'captured_rotation': [[0.9999006182304766, -0.01341462891749083, -0.004336057347023858],
                       [0.013414502787343326, 0.9999100198172864, -5.8171834587589795e-05],
                       [0.004336447541365958, 0.0, 0.9999905975671577]],
 'captured_tip_origin_mm': [75.82807977442403, -0.24210931411608816, 27.112817468003414],
 'scan_evidence_sha256': '9cecaf4a67a686bd0d3e359e17212f48c60dac4e0830dc77ca6e87b353f66ce7'}

STEM_D = PARAMETERS['nominal_stem_diameter_mm']
STEM_LENGTH = PARAMETERS['nominal_free_stem_to_shoulder_mm']
STEM_TIP_CHAMFER = PARAMETERS['stem_tip_chamfer_display_mm']
TUBE_D = PARAMETERS['nominal_tube_diameter_mm']
TUBE_BORE_D = PARAMETERS['tube_bore_display_diameter_mm']
THROUGH_BORE_D = PARAMETERS['through_bore_display_diameter_mm']
TUBE_STOP_DEPTH = PARAMETERS['body_face_to_stop_display_mm']
BODY_D = 2*max(r for x, r in PARAMETERS['body_profile_x_radius_mm'])
body_face_x = PARAMETERS['body_face_x_mm']
LENGTH = PARAMETERS['length_mm']
COLLET_PROUD = LENGTH-body_face_x
tube_stop_x = body_face_x-TUBE_STOP_DEPTH
TUBE_INSERTION_DEPTH = LENGTH-tube_stop_x
stem_to_shoulder_x = STEM_LENGTH


def stem_tip():
    """Nominal hidden male tip and insertion direction; not a scanned stop."""
    return (0., 0., 0.), (-1., 0., 0.)


def stem_shoulder():
    """Fitted shoulder plane in the nominal full-part frame."""
    return (STEM_LENGTH, 0., 0.), (-1., 0., 0.)


def tube_port():
    """Captured representative release face and outward tube axis."""
    return (LENGTH, 0., 0.), (1., 0., 0.)


def _turned(profile):
    points = [(profile[0][0], 0), *profile, (profile[-1][0], 0)]
    return cq.Workplane('XY').polyline(points).close().revolve(360, (0, 0), (1, 0)).val()


def _cylinder(radius, lo, hi):
    return cq.Solid.makeCylinder(radius, hi-lo, cq.Vector(lo, 0, 0), cq.Vector(1, 0, 0))


def build_stem():
    """Nominal straight 3/8-inch mating stem and illustrative tip lead-in."""
    lead = cq.Solid.makeCone(STEM_D/2-STEM_TIP_CHAMFER, STEM_D/2,
                            STEM_TIP_CHAMFER, cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))
    return lead.fuse(_cylinder(STEM_D/2, STEM_TIP_CHAMFER, STEM_LENGTH))


def build_body():
    return _turned(PARAMETERS['body_profile_x_radius_mm'])


def build_collet():
    return _turned(PARAMETERS['collet_profile_x_radius_mm'])


def build_bore_cut():
    """Unmeasured layout passage and tube stop, retaining existing nominal depths."""
    return (_cylinder(THROUGH_BORE_D/2, -.05, tube_stop_x+.02)
            .fuse(_cylinder(TUBE_BORE_D/2, tube_stop_x, LENGTH+.05)))


def parts():
    bore = build_bore_cut()
    fixed = build_stem().fuse(build_body()).cut(bore).clean().fix()
    collet = build_collet().cut(bore).clean().fix()
    return {'body_and_stem': fixed, 'release_collet': collet}


def build():
    """Assembly-compatible shape containing the fixed fitting and free collet."""
    return cq.Compound.makeCompound(list(parts().values()))


def build_assembly():
    assembly = cq.Assembly(name='John_Guest_PP061208W_scan_reference')
    for name, shape in parts().items():
        assembly.add(shape, name=name, color=M_JG_WHITE_PP)
    return assembly


def captured_transform():
    """Part-to-captured-chain rigid transform; nominal buried tip remains explicit."""
    r, t = PARAMETERS['captured_rotation'], PARAMETERS['captured_tip_origin_mm']
    return [[*r[i], t[i]] for i in range(3)]+[[0., 0., 0., 1.]]


def in_assembly(shape=None):
    """Place a standalone shape in the preserved ASSE assembly's frame."""
    r = PARAMETERS['captured_rotation']
    angle = math.acos(max(-1., min(1., (sum(r[i][i] for i in range(3))-1)/2)))
    shape = build() if shape is None else shape
    if angle > 1e-10:
        axis = (r[2][1]-r[1][2], r[0][2]-r[2][0], r[1][0]-r[0][1])
        shape = shape.rotate((0, 0, 0), axis, math.degrees(angle))
    return shape.translate(tuple(PARAMETERS['captured_tip_origin_mm']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, help='Also write a portable STL.')
    args = parser.parse_args(); assembly = build_assembly()
    export_assembly(assembly, str(STEP))
    if args.stl:
        cq.exporters.export(assembly.toCompound(), str(args.stl), tolerance=.025, angularTolerance=.08)
    shape = assembly.toCompound(); bb = shape.BoundingBox()
    print(json.dumps({'step': str(STEP), 'extent_mm': [bb.xlen, bb.ylen, bb.zlen],
                      'components': {k: {'valid': s.isValid(), 'solids': len(s.Solids())} for k, s in parts().items()},
                      'stem_tip': stem_tip(), 'stem_shoulder': stem_shoulder(), 'tube_port': tube_port(),
                      'hidden_stem_length_nominal_mm': STEM_LENGTH}, indent=2))


if __name__ == '__main__':
    main()
