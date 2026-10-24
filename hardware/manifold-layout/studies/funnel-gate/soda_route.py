"""Edge-on DIGITEN meter between the pump and CO2 path, with both water runs.

Pure NumPy arrangement data. Main bodies stay square; compact stem elbows
make the lateral steps. All drawn tubes have straight, axial socket entries.
"""
import numpy as np

E = np.array([1., 0., 0.])
N = np.array([0., 1., 0.])
U = np.array([0., 0., 1.])
METER_R = np.column_stack([N, E, -U])
BULKHEAD_MOUTH = np.array([77.5, 446.51, 306.3760478805363])
CORE_MOUTH = np.array([77.50000001564078, 271.5999999, 253.4])
H = 6.0452
S = 19.05
L = 20.56239
METER_T = np.array([BULKHEAD_MOUTH[0]-S-H, 372., BULKHEAD_MOUTH[2]])
METER_PORT_FACE = 30.5
METER_INSERTION = 15.7
JG_INSERTION = 15.7
NEOFIT_INSERTION = 16.891
CORE_STEM_EXPOSED = 3.


def stem_rotation(host, outlet):
    return np.column_stack([host, outlet, np.cross(host, outlet)])


def union_rotation(inlet, outlet):
    return np.column_stack([np.cross(inlet, outlet), inlet, outlet])


def tube(a, direction, b, start_depth, end_depth):
    return np.array([a-start_depth*direction, a, b, b+end_depth*direction])


def route():
    inlet = METER_T-METER_PORT_FACE*N
    outlet = METER_T+METER_PORT_FACE*N
    core_turn = np.array([*CORE_MOUTH[:2], METER_T[2]])
    core_vertical_socket = core_turn-L*U
    core_return = core_turn-(L+H+CORE_STEM_EXPOSED)*E
    core_aft_socket = core_return+S*N
    t = np.linspace(0., 1., 65)[:, None]
    feed = core_aft_socket+t*(inlet-core_aft_socket)
    feed[:,0] = core_aft_socket[0]+(t[:,0]**2*(3-2*t[:,0]))*(inlet[0]-core_aft_socket[0])
    feed_points = np.vstack([core_aft_socket-NEOFIT_INSERTION*N,feed,inlet+METER_INSERTION*N])

    # The rear bulkhead's west-facing stem receives another stem directly;
    # its fore-facing socket lines up with the meter outlet on the Y axis.
    rear_turn = BULKHEAD_MOUTH-H*N
    rear_return = rear_turn-(S+H)*E
    rear_socket = rear_return-S*N
    joints = {
        'soda-core-elbow': ('jg-turn-elbow', core_turn, union_rotation(-U, -E)),
        'soda-core-stem': ('soda-core-stem-elbow', core_return, stem_rotation(-E, N)),
        'soda-stem-elbow': ('elbow-bulkhead', rear_turn, stem_rotation(-N, -E)),
        'soda-outlet-return-stem': ('elbow-elbow', rear_return, stem_rotation(-E, -N)),
    }
    tubes = {
        'soda-core-rise': tube(CORE_MOUTH, U, core_vertical_socket, 12., JG_INSERTION),
        'soda-core-meter': feed_points,
        'soda-meter-bulkhead': tube(outlet, N, rear_socket, METER_INSERTION, NEOFIT_INSERTION),
    }
    mates = [
        ['soda-core-rise', 'soda-core-elbow'],
        ['soda-core-elbow', 'soda-core-stem'],
        ['soda-core-stem', 'soda-core-meter'],
        ['soda-core-meter', 'digiten-flow'],
        ['digiten-flow', 'soda-meter-bulkhead'],
        ['soda-meter-bulkhead', 'soda-outlet-return-stem'],
        ['soda-outlet-return-stem', 'soda-stem-elbow'],
        ['soda-stem-elbow', 'bulkhead-carb'],
    ]
    exposed = [float(np.linalg.norm(b-a)) for a,b in
               [(CORE_MOUTH,core_vertical_socket), (core_aft_socket,inlet), (outlet,rear_socket)]]
    exposed[1] = float(np.linalg.norm(np.diff(feed,axis=0),axis=1).sum())
    return {
        'meter_native_translation_mm': METER_T.tolist(),
        'meter_native_rotation': METER_R.tolist(),
        'meter_inlet_mm': inlet.tolist(), 'meter_outlet_mm': outlet.tolist(),
        'meter_flow_axis': N.tolist(), 'meter_label_axis': E.tolist(),
        'bulkhead_inboard_mouth_mm': BULKHEAD_MOUTH.tolist(),
        'bulkhead_elbow_socket_mm': rear_socket.tolist(),
        'joints': {name:{'geometry':geometry,'corner':corner.tolist(),'rotation':rotation.tolist()}
                   for name,(geometry,corner,rotation) in joints.items()},
        'tubes': {name:points.tolist() for name,points in tubes.items()},
        'mates': mates,
        'metrics': {
            'tube_od_mm': 6.35, 'tube_id_mm': 4.24,
            'tube_centerlines': 'Straight riser and outlet; a gentle lateral offset in the long fore-aft feed has axial socket entries',
            'feed_lateral_offset_mm': float(inlet[0]-core_aft_socket[0]),
            'feed_minimum_centerline_radius_mm': float((inlet[1]-core_aft_socket[1])**2/(6*abs(inlet[0]-core_aft_socket[0]))),
            'core_stem_exposure_mm': CORE_STEM_EXPOSED,
            'exposed_core_rise_mm': exposed[0], 'exposed_core_meter_mm': exposed[1],
            'exposed_meter_bulkhead_mm': exposed[2],
            'total_exposed_tube_length_mm': sum(exposed),
            'elbows_total': len(joints), 'stem_elbows': 3,
            'insertions_mm': {'meter_estimate':METER_INSERTION,'JG':JG_INSERTION,
                              'NeoFit':NEOFIT_INSERTION,'core_handoff_overlap':12.},
        },
        'flow': 'Cold-core soda outlet → straight rise → nested west/aft elbows → feed beside V-K → meter → straight aft run → nested bulkhead stems → soda bulkhead',
        'upstream_handoff': {
            'core_carb_water_out_mm': CORE_MOUTH.tolist(), 'core_outward_axis': U.tolist(),
            'source': 'hardware/manifold-layout/enclosure-assembly.facts.json card_ports.foam-assembly.carb-water-out',
            'scope': 'The soda riser follows the retained core port and extends 12 mm below the handoff plane'},
        'scope': 'Measured exterior meter on edge, with square component axes and directly nested stem elbows. Socket engagements remain family-based estimates. Both water routes are drawn; the flexible pigtail and retention detail are separate.'}
