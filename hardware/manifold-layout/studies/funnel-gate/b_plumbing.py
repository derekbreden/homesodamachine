"""Compact B inlet and an aft-side return above the PCB.

Route data only. Geometry keys refer to the enclosure study's existing fitting
meshes; main component and support placement belongs to the enclosing study.
"""
import numpy as np


E = np.array([1., 0., 0.])
N = np.array([0., 1., 0.])
U = np.array([0., 0., 1.])
L = 20.56239
S = 19.05
H = 6.0452
JG_DEPTH = 15.7
NEOFIT_DEPTH = 16.891
VB_ORIGIN = np.array([38., 227.40434, 280.41])
VB_ROTATION = np.array([[0., 0., 1.], [0., 1., 0.], [-1., 0., 0.]])
DRAIN_CORNER = np.array([0., 161.69575, 280.41])
YB_MOUTH = np.array([-22.35, 166.24, 270.675])


def stem_rotation(host, outlet):
    return np.column_stack([host, outlet, np.cross(host, outlet)])


def union_rotation(inlet, outlet):
    return np.column_stack([np.cross(inlet, outlet), inlet, outlet])


def bezier(control):
    p = np.array(control, float)
    t = np.linspace(0., 1., 65)[:, None]
    points = ((1-t)**3*p[0] + 3*(1-t)**2*t*p[1]
              + 3*(1-t)*t*t*p[2] + t**3*p[3])
    d = 3*((1-t)**2*(p[1]-p[0]) + 2*(1-t)*t*(p[2]-p[1])
           + t*t*(p[3]-p[2]))
    dd = 6*((1-t)*(p[2]-2*p[1]+p[0])
            + t*(p[3]-2*p[2]+p[1]))
    curvature = np.linalg.norm(np.cross(d, dd), axis=1)/np.linalg.norm(d, axis=1)**3
    maximum = float(curvature.max())
    return points, (1/maximum if maximum else float('inf'))


def route(vb_origin=None, drain_exposure=3.3058):
    origin = VB_ORIGIN if vb_origin is None else np.array(vb_origin, float)
    inlet = origin + VB_ROTATION @ np.array([0., -29.75, 11.05])
    outlet = origin + VB_ROTATION @ np.array([0., 29.75, 11.05])
    drain = DRAIN_CORNER + (L+H+drain_exposure)*N
    valve_inlet = inlet-H*N

    lift = np.radians(10.)
    drain_out = np.cos(lift)*E + np.sin(lift)*U
    inlet_out = -np.cos(lift)*E + np.sin(lift)*U
    drain_face = drain + S*drain_out
    inlet_face = valve_inlet + S*inlet_out
    handle = np.linalg.norm(inlet_face-drain_face)/3
    inlet_control = np.array([drain_face, drain_face+handle*drain_out,
                              inlet_face+handle*inlet_out, inlet_face])
    inlet_curve, inlet_radius = bezier(inlet_control)
    inlet_points = np.vstack([drain_face-NEOFIT_DEPTH*drain_out,
                              inlet_curve, inlet_face-NEOFIT_DEPTH*inlet_out])

    yb_angle = np.radians(7.5)
    yb_out = -np.sin(yb_angle)*E + np.cos(yb_angle)*N
    yb = YB_MOUTH + H*U
    yb_face = yb + S*yb_out

    rise = np.radians(8.)
    cross_axis = -np.cos(rise)*E + np.sin(rise)*U
    valve_outlet = outlet + H*N
    turn = np.array([yb_face[0], valve_outlet[1],
                     valve_outlet[2] + (valve_outlet[0]-yb_face[0])*np.tan(rise)])
    cross_start = valve_outlet + S*cross_axis
    cross_end = turn-L*cross_axis
    cross_points = np.array([cross_start-NEOFIT_DEPTH*cross_axis,
                             cross_start, cross_end, cross_end+JG_DEPTH*cross_axis])
    return_face = turn-L*N
    return_control = np.array([return_face, return_face-20*N,
                               yb_face+20*yb_out, yb_face])
    return_curve, return_radius = bezier(return_control)
    return_points = np.vstack([return_face+JG_DEPTH*N, return_curve,
                               yb_face-NEOFIT_DEPTH*yb_out])

    joints = {
        'drain-outlet-stem': ('drain-stem-elbow', drain, stem_rotation(N, drain_out)),
        'vb-inlet-turn': ('stem-elbow-trimmed', valve_inlet, stem_rotation(-N, inlet_out)),
        'vb-outlet-stem': ('stem-elbow-trimmed', valve_outlet, stem_rotation(N, cross_axis)),
        'vb-outlet-return': ('jg-turn-elbow', turn, union_rotation(-cross_axis, -N)),
        'yb-stem-elbow': ('gas-stem-elbow', yb, stem_rotation(U, yb_out)),
    }
    tubes = {'drain-vb-east-link': inlet_points,
             'vb-yb-cross': cross_points,
             'vb-yb-link': return_points}
    mates = [
        ('funnel-drain-union', 'drain-outlet-stem'),
        ('drain-outlet-stem', 'drain-vb-east-link'),
        ('drain-vb-east-link', 'vb-inlet-turn'), ('vb-inlet-turn', 'vb'),
        ('vb', 'vb-outlet-stem'), ('vb-outlet-stem', 'vb-yb-cross'),
        ('vb-yb-cross', 'vb-outlet-return'), ('vb-outlet-return', 'vb-yb-link'),
        ('vb-yb-link', 'yb-stem-elbow'), ('yb-stem-elbow', 'tee-yb-target'),
    ]
    return {
        'joints': {name: {'geometry': geometry, 'corner': corner.tolist(),
                          'rotation': rotation.tolist()}
                   for name, (geometry, corner, rotation) in joints.items()},
        'tubes': {name: points.tolist() for name, points in tubes.items()},
        'mates': [list(pair) for pair in mates],
        'vb_native_origin_mm': origin.tolist(),
        'vb_native_rotation': VB_ROTATION.tolist(),
        'vb_inlet_mm': inlet.tolist(), 'vb_outlet_mm': outlet.tolist(),
        'metrics': {
            'inlet_control_mm': inlet_control.tolist(),
            'inlet_minimum_radius_mm': inlet_radius,
            'inlet_exposed_length_mm': float(np.linalg.norm(np.diff(inlet_curve, axis=0), axis=1).sum()),
            'inlet_arm_lift_degrees': 10.,
            'cross_rise_degrees': 8.,
            'cross_exposed_length_mm': float(np.linalg.norm(cross_end-cross_start)),
            'return_control_mm': return_control.tolist(),
            'return_minimum_radius_mm': return_radius,
            'return_exposed_length_mm': float(np.linalg.norm(np.diff(return_curve, axis=0), axis=1).sum()),
            'yb_clock_west_of_aft_degrees': 7.5,
            'return_minimum_y_mm': float(return_curve[:, 1].min()),
            'insertions_mm': {'JG': JG_DEPTH, 'NeoFit': NEOFIT_DEPTH,
                              'Beduan': 12.7, 'YB_tee': JG_DEPTH},
            'drain_stem_exposure_mm': float(drain_exposure),
        },
    }
