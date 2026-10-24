"""Aft edge-on DIGITEN meter with a direct-down core inlet.

Pure NumPy arrangement data. Main component axes stay square. The meter's
outlet collet meets the rear fitting; only their seated tube is concealed.
"""
import numpy as np

E = np.array([1., 0., 0.])
N = np.array([0., 1., 0.])
U = np.array([0., 0., 1.])
METER_R = np.column_stack([N, E, -U])
BULKHEAD_MOUTH = np.array([77.5, 446.51, 306.3760478805363])
H = 6.0452
S = 19.05
METER_PORT_FACE = 30.5
METER_INSERTION = 15.7
NEOFIT_INSERTION = 16.891
METER_X = 50.
REAR_TURN = BULKHEAD_MOUTH-H*N
REAR_STEM_EXPOSED = BULKHEAD_MOUTH[0]-S-H-METER_X
REAR_RETURN = REAR_TURN-(S+H+REAR_STEM_EXPOSED)*E
REAR_SOCKET = REAR_RETURN-S*N
METER_T = REAR_SOCKET-METER_PORT_FACE*N
CORE_MOUTH = np.array([METER_X, METER_T[1]-METER_PORT_FACE-H, 253.4])


def stem_rotation(host, outlet):
    return np.column_stack([host, outlet, np.cross(host, outlet)])


def route():
    inlet = METER_T-METER_PORT_FACE*N
    outlet = METER_T+METER_PORT_FACE*N
    inlet_turn = inlet-H*N
    inlet_socket = inlet_turn-S*U
    joints = {
        'soda-inlet-stem': ('gas-stem-elbow', inlet_turn, stem_rotation(-N, -U)),
        'soda-stem-elbow': ('elbow-bulkhead', REAR_TURN, stem_rotation(-N, -E)),
        'soda-outlet-return-stem': ('soda-rear-stem-elbow', REAR_RETURN, stem_rotation(-E, -N)),
    }
    tubes = {
        'soda-core-rise': np.array([CORE_MOUTH-12.*U, CORE_MOUTH,
                                   inlet_socket, inlet_socket+NEOFIT_INSERTION*U]),
        'soda-meter-bulkhead': np.array([outlet-METER_INSERTION*N,
                                        REAR_SOCKET+NEOFIT_INSERTION*N]),
    }
    mates = [
        ['soda-core-rise', 'soda-inlet-stem'],
        ['soda-inlet-stem', 'digiten-flow'],
        ['digiten-flow', 'soda-meter-bulkhead'],
        ['soda-meter-bulkhead', 'soda-outlet-return-stem'],
        ['digiten-flow', 'soda-outlet-return-stem'],
        ['soda-outlet-return-stem', 'soda-stem-elbow'],
        ['soda-stem-elbow', 'bulkhead-carb'],
    ]
    exposed_rise = float(inlet_socket[2]-CORE_MOUTH[2])
    return {
        'meter_native_translation_mm': METER_T.tolist(),
        'meter_native_rotation': METER_R.tolist(),
        'meter_inlet_mm': inlet.tolist(), 'meter_outlet_mm': outlet.tolist(),
        'meter_flow_axis': N.tolist(), 'meter_label_axis': E.tolist(),
        'bulkhead_inboard_mouth_mm': BULKHEAD_MOUTH.tolist(),
        'bulkhead_elbow_socket_mm': REAR_SOCKET.tolist(),
        'joints': {name:{'geometry':geometry,'corner':corner.tolist(),'rotation':rotation.tolist()}
                   for name,(geometry,corner,rotation) in joints.items()},
        'tubes': {name:points.tolist() for name,points in tubes.items()},
        'mates': mates,
        'metrics': {
            'tube_od_mm': 6.35, 'tube_id_mm': 4.24,
            'tube_centerlines': 'Straight vertical core inlet and concealed axial outlet join',
            'exposed_core_rise_mm': exposed_rise,
            'exposed_meter_bulkhead_mm': float(np.linalg.norm(REAR_SOCKET-outlet)),
            'outlet_concealed_tube_length_mm': METER_INSERTION+NEOFIT_INSERTION,
            'total_exposed_tube_length_mm': exposed_rise,
            'rear_stem_exposure_mm': float(REAR_STEM_EXPOSED),
            'elbows_total': len(joints), 'stem_elbows': len(joints),
            'insertions_mm': {'meter_estimate':METER_INSERTION,'NeoFit':NEOFIT_INSERTION,
                              'core_handoff_overlap':12.},
        },
        'flow': 'Proposed aft core soda guide → vertical tube → directly seated inlet stem → meter → concealed tube join → nested rear stems → soda bulkhead',
        'upstream_handoff': {
            'core_carb_water_out_mm': CORE_MOUTH.tolist(), 'core_outward_axis': U.tolist(),
            'source': 'Proposed soda guide in the current cold-core roof, aft of the pump inlet elbow',
            'scope': 'The drawn tube extends 12 mm below the proposed handoff plane; the guide and internal core route require production integration'},
        'scope': 'Measured exterior meter on edge with square component axes. Outlet collet faces meet with no exposed tube. The rear nested stem retains 2.4048 mm exposure for CO2 clearance. Socket engagement remains estimated; core-guide integration, pigtail and retention are separate.'}
