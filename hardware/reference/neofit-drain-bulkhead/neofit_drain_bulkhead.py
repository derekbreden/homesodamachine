"""Scan-fitted neoFit ABU44M-E 4 mm bulkhead union, HSM-000061.

Native +Y points outboard. The origin is the fixed flange's panel-seating
face; the nut retains its captured free position. build() supplies the bare
fitting, and build_assembly() includes the separate captured nut. Hidden
threads use a crest envelope; bore and mouth closures are display geometry.

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations
from pathlib import Path
import sys


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == 'hardware')
sys.path.insert(0, str(_hw/'scripts'))

STEP = _here.with_name('neofit-drain-bulkhead.step')
# Frozen measurements keep consumers of this fitting independent of scan files.
PARAMETER_SNAPSHOT_SHA256 = '94ca62eae9afc8396e83d6398120e3af16a67db7372d4db9617fe52a5e39eed5'
PARAMETERS = {'units': 'mm',
 'material_id': 'HSM-000061',
 'panel_seat_local_x_mm': -4.366836575879036,
 'outboard_mouth_local_x_mm': -16.194239450616685,
 'inboard_mouth_local_x_mm': 17.09425949942281,
 'overall_mm': 33.2884989500395,
 'near_ring_face_y_mm': 11.827402874737649,
 'far_ring_face_y_mm': -21.461096075301846,
 'body_hex': {'across_flats_mm': 17.104185173888958,
              'center_yz_mm': [-0.04768709067598976, -0.05612018401489432],
              'vertex_clock_degrees': -2.4051501489046956},
 'body_hex_stop_local_x_mm': -6.35,
 'nut_hex': {'across_flats_mm': 18.003496010716436,
             'center_yz_mm': [-0.01158748418158394, -0.08839434533385554],
             'vertex_clock_degrees': -5.014448978196818},
 'nut_hex_start_local_x_mm': 2.9,
 'nut_axial_range_local_mm': [1.1612581975635323, 7.968500093292667],
 'captured_nut_gap_mm': 5.528094773442568,
 'barrel_end_local_x_mm': 10.75,
 'profiles': {'outboard': [[-16.19424, 4.96158],
                           [-16.13174, 4.96158],
                           [-15.88174, 5.24215],
                           [-15.75674, 5.31402],
                           [-14.88174, 5.40967],
                           [-14.75674, 5.51821],
                           [-14.50674, 5.99143],
                           [-14.38174, 6.14039],
                           [-14.13174, 6.302],
                           [-13.75674, 6.36745],
                           [-12.38174, 6.31295],
                           [-11.75674, 6.69304],
                           [-11.13174, 6.77188],
                           [-11.00674, 6.90072],
                           [-10.75674, 6.90072],
                           [-10.63174, 7.18068],
                           [-10.50674, 7.28462],
                           [-10.38174, 7.98927],
                           [-10.25674, 8.35845],
                           [-10.00674, 8.89807],
                           [-9.75674, 9.34704],
                           [-9.50674, 9.60895],
                           [-9.38174, 9.66911],
                           [-9.00674, 9.71024],
                           [-7.25674, 9.6443],
                           [-6.13174, 9.68507],
                           [-6.00674, 9.74362],
                           [-5.75674, 10.0493],
                           [-5.63174, 10.14832],
                           [-5.38174, 10.22951],
                           [-4.75674, 10.17168],
                           [-4.50674, 10.05211],
                           [-4.36684, 9.90899]],
              'inboard': [[10.75, 7.1135],
                          [10.8125, 7.1135],
                          [11.4375, 6.59594],
                          [11.8125, 6.45312],
                          [13.1875, 6.2739],
                          [14.4375, 6.28671],
                          [14.9375, 6.22282],
                          [15.1875, 6.11181],
                          [15.3125, 5.9947],
                          [15.4375, 5.78421],
                          [15.5625, 5.40208],
                          [15.6875, 5.16172],
                          [16.5625, 5.00578],
                          [16.8125, 4.83622],
                          [17.09426, 4.76881]],
              'nut': [[1.16126, 10.03375],
                      [1.72376, 10.12894],
                      [3.22376, 9.99822],
                      [4.47376, 9.98225],
                      [6.72376, 10.07864],
                      [7.22376, 9.88391],
                      [7.59876, 9.5566],
                      [7.84876, 9.21939],
                      [7.9685, 9.21939]]},
 'profile_method': '97.5th percentile outward-facing radius in 0.125 mm axial bins; three-bin '
                   'median; 0.035 mm radial simplification.',
 'published': {'tube_od_mm': 4.0,
               'thread_diameter_mm': 15.0,
               'thread_pitch_mm': 1.5,
               'overall_mm': 32.4,
               'bare_panel_span_mm': 8.1,
               'nut_length_mm': 6.5,
               'body_hex_af_mm': 17.0,
               'nut_hex_af_mm': 18.0,
               'tube_stop_depth_mm': 14.7},
 'scan_evidence_sha256': 'b65271a1f5ef5970958ea068cecf00059cd2b8bdccf777155755ec0d2defe332'}

TUBE_OD = PARAMETERS['published']['tube_od_mm']
THREAD_D = PARAMETERS['published']['thread_diameter_mm']
THREAD_PITCH = PARAMETERS['published']['thread_pitch_mm']
PANEL_THREAD = PARAMETERS['published']['bare_panel_span_mm']
NUT_LEN = PARAMETERS['published']['nut_length_mm']
TUBE_STOP_DEPTH = PARAMETERS['published']['tube_stop_depth_mm']
OVERALL = PARAMETERS['overall_mm']
FLANGE_AF = PARAMETERS['body_hex']['across_flats_mm']
NUT_AF = PARAMETERS['nut_hex']['across_flats_mm']
FLANGE_D = 2*max(r for x, r in PARAMETERS['profiles']['outboard'])
NUT_D = 2*max(r for x, r in PARAMETERS['profiles']['nut'])
near_ring_face_y = PARAMETERS['near_ring_face_y_mm']
far_ring_face_y = PARAMETERS['far_ring_face_y_mm']
far_body_face_y = PARAMETERS['panel_seat_local_x_mm']-PARAMETERS['barrel_end_local_x_mm']
PROUD_LENGTH = near_ring_face_y


def panel_hole_d(clearance):
    return THREAD_D+clearance


def panel_footprint():
    diameter = max(FLANGE_D, NUT_D)
    return diameter, diameter


def flange_footprint():
    return FLANGE_D


def port(side):
    return ((0., near_ring_face_y if side > 0 else far_ring_face_y, 0.),
            (0., 1. if side > 0 else -1., 0.))


def radius_at(profile, x):
    if x <= profile[0][0]: return profile[0][1]
    if x >= profile[-1][0]: return profile[-1][1]
    for (a, ra), (b, rb) in zip(profile, profile[1:]):
        if a <= x <= b:
            return ra+(rb-ra)*(x-a)/(b-a)
    raise ValueError('Station outside the recorded profile')


def profile_between(profile, lo, hi):
    return [(lo, radius_at(profile, lo)), *[(x, r) for x, r in profile if lo+1e-4 < x < hi-1e-4],
            (hi, radius_at(profile, hi))]


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'neofit-drain-bulkhead.step'
PAYLOAD_PATH = _FROZEN_DIR / 'neofit-drain-bulkhead.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('neofit-drain-bulkhead frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == '__main__':
    main()
