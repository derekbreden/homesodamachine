"""John Guest PP061208W: 3/8-inch stem to 1/4-inch push-connect reducer.

The exposed exterior follows the threaded ASSE assembly scan. The buried male
tip uses a nominal 18.29 mm stem-to-shoulder length; internal passages and the
stop are display geometry. Frame: stem tip X0, axis +X, socket mouth at +X.

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations
from pathlib import Path
import sys


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == 'hardware')
sys.path.insert(0, str(_hw/'scripts'))

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


def captured_transform():
    """Part-to-captured-chain rigid transform; nominal buried tip remains explicit."""
    r, t = PARAMETERS['captured_rotation'], PARAMETERS['captured_tip_origin_mm']
    return [[*r[i], t[i]] for i in range(3)]+[[0., 0., 0., 1.]]


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'jg-pp061208w.step'
PAYLOAD_PATH = _FROZEN_DIR / 'jg-pp061208w.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('jg-pp061208w frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == '__main__':
    main()
