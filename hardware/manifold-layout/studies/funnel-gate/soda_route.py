"""Transverse DIGITEN meter and a square-entry tube to the soda bulkhead.

Pure NumPy layout data for the isolated arrangement. The measured reference
keeps its native collet-face datums; no CAD or study module is imported here.
"""
import numpy as np

E = np.array([1., 0., 0.])
N = np.array([0., 1., 0.])
U = np.array([0., 0., 1.])
METER_R = np.array([[1., 0., 0.], [0., 0., -1.], [0., 1., 0.]])
METER_T = np.array([-3., 440.4648, 326.1])
METER_PORT_FACE = 30.5
BULKHEAD_MOUTH = np.array([77.5, 446.51, 306.3760478805363])
STEM_TO_CORNER = 6.0452
SOCKET_TO_CORNER = 19.05
METER_INSERTION = 15.7
NEOFIT_INSERTION = 16.891
BEND_RADIUS = 14.


def falling_s(a, b, radius=BEND_RADIUS):
    """Two tangent circular bends with a straight diagonal between them.

    Both socket axes remain +X. The bends lie in the X/Z plane and each has
    the specified centreline radius. The scalar solve uses no SciPy runtime.
    """
    dx = float(b[0]-a[0])
    drop = float(a[2]-b[2])
    lo, hi = 0., np.pi/2-.001
    if dx < 2*radius:
        hi = np.arcsin(dx/(2*radius))
    for _ in range(70):
        theta = (lo+hi)/2
        predicted = (2*radius*(1-np.cos(theta))
                     +(dx-2*radius*np.sin(theta))*np.tan(theta))
        if predicted < drop:
            lo = theta
        else:
            hi = theta
    theta = (lo+hi)/2
    diagonal = (dx-2*radius*np.sin(theta))/np.cos(theta)
    angle = np.linspace(0., theta, 33)
    first = a+np.column_stack([radius*np.sin(angle), np.zeros(len(angle)),
                              -radius*(1-np.cos(angle))])
    corner = first[-1]+diagonal*np.array([np.cos(theta), 0., -np.sin(theta)])
    second = corner+np.column_stack([
        radius*(np.sin(theta)-np.sin(theta-angle)), np.zeros(len(angle)),
        -radius*(np.cos(theta-angle)-np.cos(theta))])
    exposed = np.vstack([first, corner, second[1:]])
    return exposed, theta, diagonal


def route():
    inlet = METER_T-METER_PORT_FACE*E
    outlet = METER_T+METER_PORT_FACE*E
    elbow_corner = BULKHEAD_MOUTH-STEM_TO_CORNER*N
    elbow_socket = elbow_corner-SOCKET_TO_CORNER*E
    exposed, angle, diagonal = falling_s(outlet, elbow_socket)
    # Extend only the square axial legs inside the existing push-connects.
    points = np.vstack([outlet-METER_INSERTION*E, exposed,
                        elbow_socket+NEOFIT_INSERTION*E])
    elbow_r = np.column_stack([-N, -E, np.cross(-N, -E)])
    return {
        'meter_native_translation_mm': METER_T.tolist(),
        'meter_native_rotation': METER_R.tolist(),
        'meter_inlet_mm': inlet.tolist(),
        'meter_outlet_mm': outlet.tolist(),
        'meter_flow_axis': E.tolist(),
        'meter_label_axis': U.tolist(),
        'bulkhead_inboard_mouth_mm': BULKHEAD_MOUTH.tolist(),
        'bulkhead_elbow_socket_mm': elbow_socket.tolist(),
        'joints': {'soda-stem-elbow': {
            'geometry': 'elbow-bulkhead', 'corner': elbow_corner.tolist(),
            'rotation': elbow_r.tolist()}},
        'tubes': {'soda-meter-bulkhead': points.tolist()},
        'mates': [['digiten-flow', 'soda-meter-bulkhead'],
                  ['soda-meter-bulkhead', 'soda-stem-elbow'],
                  ['soda-stem-elbow', 'bulkhead-carb']],
        'metrics': {
            'tube_od_mm': 6.35, 'tube_id_mm': 4.24,
            'minimum_centerline_radius_mm': BEND_RADIUS,
            'each_bend_angle_degrees': float(np.degrees(angle)),
            'diagonal_length_mm': diagonal,
            'exposed_tube_centerline_length_mm': float(
                2*BEND_RADIUS*angle+diagonal),
            'tube_cut_length_estimate_mm': float(
                METER_INSERTION+2*BEND_RADIUS*angle+diagonal+NEOFIT_INSERTION),
            'drop_mm': float(outlet[2]-elbow_socket[2]),
            'additional_elbows': 0,
            'insertions_mm': {'meter_estimate': METER_INSERTION,
                              'NeoFit_socket': NEOFIT_INSERTION,
                              'bulkhead_stem_estimate': 12.7}},
        'flow': 'Cold-core carbonated water → DIGITEN inlet → meter → short falling S → existing west-facing bulkhead stem elbow → soda bulkhead',
        'upstream_handoff': {
            'core_carb_water_out_mm': [77.50000001564078, 271.5999999, 253.4],
            'core_outward_axis': U.tolist(),
            'source': 'hardware/manifold-layout/enclosure-assembly.facts.json card_ports.foam-assembly.carb-water-out',
            'scope': 'Actual core source datum retained for the next upstream run; inlet route is not drawn here'},
        'scope': 'Measured exterior meter, square component axes and existing trimmed bulkhead elbow. The continuous tube has two R14 formed bends with axial entries. Meter socket engagement is estimated; retention and upstream routing remain separate.'}
