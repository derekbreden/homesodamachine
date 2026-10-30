"""The captured planned threaded ASSE chain, with six named exterior bodies.

Profiles and poses come from reference-parameters.json. The frame is the bare
ASSE reference: +X flow, inlet rim X=0, vent tip Z=0. Buried joint geometry and
blind bore closures are display geometry, not hydraulic or material models.
"""
from pathlib import Path
import argparse
import json
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path[:0] = [str(HW / 'scripts'), str(HERE.parent / 'multiplex-asse1022')]
from _cadq_export import export_assembly
from _materials import M_BRASS, M_STAINLESS, M_JG_BLACK_PP, M_JG_GREY_ACETAL, M_JG_WHITE_PP
import multiplex_asse1022 as bfp


def parameters():
    return json.loads((HERE / 'reference-parameters.json').read_text())['components']


def turned(profile):
    outline = [(profile[0][0], 0), *[tuple(p) for p in profile], (profile[-1][0], 0)]
    return cq.Workplane('XY').polyline(outline).close().revolve(360, (0, 0), (1, 0)).val()


def inline(record):
    profile = record['visible_profile']
    wrench = record.get('wrench')
    if wrench:
        lo, hi = profile[0][0], profile[-1][0]
        h0, slope = wrench['apothem_at_x_zero_mm'], wrench['apothem_slope']
        start = (cq.Workplane('YZ', origin=(lo, 0, 0))
                 .polygon(6, 2 * (h0+slope*lo) / math.cos(math.pi/6)))
        prism = (start.extrude(hi-lo).val() if slope == 0 else
                 start.workplane(offset=hi-lo)
                 .polygon(6, 2 * (h0+slope*hi) / math.cos(math.pi/6)).loft().val())
        prism = prism.rotate((0, 0, 0), (1, 0, 0), wrench['clock_degrees'])
        return turned(profile).intersect(prism).clean().fix()
    return turned(profile)


def x_bore(radius, lo, hi):
    return cq.Solid.makeCylinder(radius, hi-lo, cq.Vector(lo, 0, 0), cq.Vector(1, 0, 0))


def placed(shape, record):
    r, t = record['rotation'], record['origin_mm']
    angle = math.acos(max(-1., min(1., (sum(r[i][i] for i in range(3))-1)/2)))
    if angle > 1e-10:
        axis = (r[2][1]-r[1][2], r[0][2]-r[2][0], r[1][0]-r[0][1])
        shape = shape.rotate((0, 0, 0), axis, math.degrees(angle))
    return shape.translate(tuple(t))


def local_tee(record):
    plus = turned(record['run_profiles']['plus']).rotate((0, 0, 0), (0, 0, 1), 90)
    minus = turned(record['run_profiles']['minus']).rotate((0, 0, 0), (0, 0, 1), -90)
    part = plus.fuse(minus).fuse(turned(record['branch_profile']))
    for sign, name in [(1, 'plus'), (-1, 'minus')]:
        reach = record['run_profiles'][name][-1][0]
        mouth = cq.Solid.makeCylinder(3.25, 8.1,
                    cq.Vector(0, sign*(reach+.1), 0), cq.Vector(0, -sign, 0))
        part = part.cut(mouth)
    return part.clean()


def parts():
    data = parameters()
    result = {}
    for key in ('pp010822e', 'gagira', 'pi4512f6s', 'pp061208w'):
        record = data[key]
        shape = inline(record)
        lo, hi = record['visible_axial_range_mm']
        if key == 'pp010822e':
            shape = shape.cut(x_bore(3.25, lo-.1, lo+6.))
        elif key == 'gagira':
            shape = shape.cut(x_bore(6.9, lo-.1, -10.)).cut(x_bore(8.9, -.1, hi+.1))
        elif key == 'pi4512f6s':
            shape = shape.cut(x_bore(8.9, lo-.1, 66.0)).cut(x_bore(4.90, 65.9, hi+.1))
        elif key == 'pp061208w':
            shape = shape.cut(x_bore(3.25, lo-.1, hi+.1))
        result[key] = placed(shape.fix(), record)
    result['multiplex-asse1022'] = bfp.build()
    result['atbu444-e'] = placed(local_tee(data['atbu444-e']), data['atbu444-e'])
    return result


COLORS = {'pp010822e': M_JG_BLACK_PP, 'gagira': M_STAINLESS,
          'multiplex-asse1022': M_BRASS, 'pi4512f6s': M_JG_GREY_ACETAL,
          'pp061208w': M_JG_WHITE_PP, 'atbu444-e': cq.Color(.13, .14, .15)}


def build():
    assembly = cq.Assembly(name='asse1022-threaded-chain')
    for name, shape in parts().items():
        assembly.add(shape, name=name, color=COLORS[name])
    return assembly


def ports():
    data = parameters()
    result = {'vent': bfp.vent()}
    inlet = data['pp010822e']
    station = inlet['visible_profile'][0][0]
    r, t = inlet['rotation'], inlet['origin_mm']
    result['inlet'] = (tuple(t[i]+r[i][0]*station for i in range(3)), tuple(-r[i][0] for i in range(3)))
    tee = data['atbu444-e']; r, t = tee['rotation'], tee['origin_mm']
    for sign, name in [(1, 'plus'), (-1, 'minus')]:
        reach = tee['run_profiles'][name][-1][0]
        result['outlet_'+name] = (tuple(t[i]+sign*r[i][1]*reach for i in range(3)), tuple(sign*r[i][1] for i in range(3)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, help='Also export the assembled exterior as STL.')
    args = parser.parse_args()
    assembly = build()
    path = HERE / 'asse1022-threaded-chain.step'
    export_assembly(assembly, str(path))
    if args.stl:
        cq.exporters.export(assembly.toCompound(), str(args.stl), tolerance=.025, angularTolerance=.08)
    bb = assembly.toCompound().BoundingBox()
    print(f'-> {path}\nBounds: {bb.xlen:.2f} × {bb.ylen:.2f} × {bb.zlen:.2f} mm')
    print(json.dumps(ports(), indent=2))


if __name__ == '__main__':
    main()
