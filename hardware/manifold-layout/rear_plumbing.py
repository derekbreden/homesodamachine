"""Rear inlet header, pump joints and integral snap seats in appliance coordinates.

Purchased profiles retain their own reference frames. The shared production
specification places every fitting and defines the short flexible pump joints;
no exploratory assembly or exported study is a build input.
"""
import json
from pathlib import Path

import numpy as np

import above_core as layout
from _layout_data import data as _data


def plan():
    return layout.specification()['rear_plumbing']


def reference(name, path):
    import above_core_parts as parts
    return parts._module('rear_' + name, path)


def chain():
    return reference('threaded_chain', 'reference/asse1022-threaded-chain/asse1022_threaded_chain.py')


def union_tee():
    return reference('union_tee', 'reference/jg-pp0208e-tee/jg_pp0208e_tee.py')


def check():
    return reference('acvus', 'reference/neofit-acvus44-check/neofit_acvus44_check.py')


def joint():
    return reference('pump_joint', 'reference/pump-barb-joint/pump_barb_joint.py')


def _arc_three(points):
    return _data('arc-three', points=points)


def ports(name):
    data = plan()
    if name == 'bulkhead-water':
        p, u = chain().ports()['inlet']
        return {'outboard': (p,u,6.35), 'inboard':(p,tuple(-c for c in u),6.35)}
    if name in ('gas-regulator','co2-inlet'):
        return {'inlet':((0.,0.,0.),(0.,0.,-1.),6.35),
                'outlet':((0.,0.,62.814),(0.,0.,1.),6.35),
                'outboard':((0.,0.,0.),(0.,0.,-1.),6.35),
                'inboard':((0.,0.,62.814),(0.,0.,1.),6.35)}
    if name in ('gas-check','discharge-chain'):
        return {'inlet':(*check().stem_tip(),6.35), 'outlet':(*check().tube_port(),6.35),
                'tube-port':(*check().tube_port(),6.35)}
    if name == 'water-split':
        return {'supply':(*union_tee().branch(),6.35),
                'to-vk':(*union_tee().run(1),6.35),'to-flavor':(*union_tee().run(-1),6.35)}
    if name in ('suction-reducer','discharge-reducer'):
        mouth = joint().reducer.LENGTH-joint().CUT_X
        return {'tube':((mouth,0.,0.),(1.,0.,0.),6.35)}
    if name == 'jg-pp061208w':
        red = chain().parameters()['pp061208w']
        x = red['visible_axial_range_mm'][1]
        r = red['rotation']
        p = tuple(red['origin_mm'][i] + r[i][0]*x for i in range(3))
        return {'tube':(p,tuple(row[0] for row in r),6.35)}
    return None


def snap_datums():
    """The integral rear seats' axes and supporting wall planes."""
    data=plan()
    c=layout.point(data['chain_frame'],(0.,0.,chain().bfp.BODY_CENTER_Z))
    p=layout.point(data['gas_frame'],(0.,0.,0.))
    return {'asse_axis':(c[0],c[2]), 'asse_turn':90., 'pisco_axis':(p[0],p[2]),
            'mouth_y':p[1], 'ceiling':data['snap_ceiling_z_mm'], 'rear':465.3, 'side':98.5}


def regulator_datums():
    """The measured water-regulator profile in the snap's local +Y frame."""
    import rear_snaps as snaps
    mount=plan()['regulator_mount']
    profile=json.loads((Path(__file__).resolve().parent.parent/
        'reference/yzmsz-water-regulator/reference-parameters.json').read_text())['profile_x_radius_mm']
    fit=mount['cavity_fit']
    pose=layout.snapshot_pose('reg')
    turn=np.array(((0.,1.,0.),(-1.,0.,0.),(0.,0.,1.)))
    frame={'rotation':(turn@np.array(pose['rotation'])).tolist(),
           'translation_mm':(turn@np.array(pose['translation_mm'])).tolist()}
    st=dict(mount['station'],tool_angle_degrees=75.,tool_sides=(-1.,),tool_inner_slope=2.)
    half=st['inner']-snaps.ROOT_RADIUS-.5
    return dict(mount,station=st,profile_frame=frame,
        seat_profile=snaps.clearance_profile(profile,fit['receiver_radial_mm'],fit['axial_mm']),
        cap_profile=snaps.clearance_profile(profile,fit['cap_radial_mm'],fit['axial_mm']),
        cap_bearing_outlet_setback_mm=1.,
        cap_stock=[(st['axis_x']-half,st['axis_x']+half,st['y0'],st['y1']-1.,
                    mount['cap_bottom'],mount['axis'][1])])


def meter_spans():
    """Receiver and removable-cap extents on the meter's own axial frame."""
    y = layout.pose('digiten-flow')['translation_mm'][1]
    return (y-30.01, y+29.99), (y-19.01, y+18.99)


def _route_stations(operation, resolver):
    return {f'{name}.{port}': resolver(name, port)
            for name, port in _data('route-stations', operation=operation, spec=layout.specification())}


def route_specs():
    """Rust short-tube recipes, with provider ports carried to world stations."""
    import above_core_parts as parts

    def station(name, port):
        point, axis, diameter = parts.port_stations(name)[port]
        frame = parts.route_port_frame(name)
        return layout.point(frame, point), layout.vector(frame['rotation'], axis), diameter

    params = {'reducer_insertion': joint().reducer.TUBE_INSERTION_DEPTH,
              'tee_insertion': union_tee().INSERTION,
              'stem_insertion': parts.stem_elbow_reference().SOCKET_INSERTION}
    return dict(_data('rear-route-specs', spec=layout.specification(),
                      stations=_route_stations('rear-route-specs', station), params=params))


def continuations(station):
    """Rust water, gas and vent continuations between named interfaces."""
    bulkhead = reference('pp1208e', 'reference/jg-bulkhead-union/jg_bulkhead_union.py')
    params = {'check_insertion': check().INSERTION, 'bulkhead_tube_stop': bulkhead.TUBE_STOP_DEPTH}
    return dict(_data('rear-continuations', spec=layout.specification(),
                      stations=_route_stations('rear-continuations', station), params=params))


def _flavor_s_bend(start, heading, offset, axis):
    segments, end = _data('flavor-s-bend', start=start, heading=heading, offset=offset, axis=axis)
    return segments, tuple(end)


def _flavor_rear(flavor, destination):
    return _data('flavor-rear', flavor=flavor, destination=destination)


def flavor_routes(station):
    """Rust dispense-line recipes from the raw world-port stations."""
    return dict(_data('flavor-routes', stations=_route_stations('flavor-routes', station)))
