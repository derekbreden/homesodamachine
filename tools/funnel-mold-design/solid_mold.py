"""Solid PETG funnel tooling, in the funnel's brim-centred assembly frame.

The cavity stands on a rounded foot with a continuous 45-degree outer taper.
The core prints inverted on its flat back. All modeled stock prints at 100%
fill. Both forming faces reserve 0.20 mm of net finishing growth.

Run by hand with tools/cad-venv/bin/python. Outputs are in --output.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/zone-c/funnel'),
                str(ROOT / 'hardware/scripts')]
import funnel
from _cadq_export import export_assembly
from _materials import one_body
from flute_payload import cut as write_print_payload

finish_allowance = 0.20
forming_backing = 6.0
rim_margin = 8.0
base_thickness = 8.0
foot_width = 112.0
foot_radius = 12.0
foot_height = 3.2
rim_radius = 10.0
plate_thickness = 10.0
register_wall = 6.0
register_depth = 6.0
register_clearance = 0.30
key_depth = 2.0
key_width = 14.0
key_y = 38.0
tip_length = 12.0
tip_step = 1.0
tip_cap = 2.0
tip_draft = 0.5
rod_diameter = 6.35
rod_length = 50.8
rod_clearance = 0.10
socket_vent_diameter = 2.5
socket_vent_overlap = 1.0
vent_diameter = 3.0
pour_diameter = 11.0
pry_width = 24.0
pry_depth = 5.0
pry_height = 1.5
tolerance = 0.0001
chamber_diameter = 299.72


def box(width, depth, bottom, top, x=0, y=0):
    return (cq.Workplane('XY').box(width, depth, top-bottom,
            centered=(True, True, False)).translate((x, y, bottom)).val())


def cylinder(radius, bottom, top, x=0, y=0):
    return cq.Solid.makeCylinder(radius, top-bottom, cq.Vector(x, y, bottom))


def rounded(width, radius, bottom, top):
    return cq.Workplane(obj=box(width, width, bottom, top)).edges('|Z').fillet(radius).val()


def one(shape, name):
    shape = shape.clean()
    assert shape.isValid() and len(shape.Solids()) == 1, name
    return shape.Solids()[0]


def expanded(shape, distance):
    offsets = [face.thicken(distance) for face in shape.Faces()]
    for edge in shape.Edges():
        if edge.Length() > tolerance:
            profile = cq.Wire.makeCircle(distance, edge.positionAt(0), edge.tangentAt(0))
            offsets.append(cq.Solid.sweep(profile, [], edge))
    offsets.extend(cq.Solid.makeSphere(distance, vertex.Center(),
        angleDegrees1=-90, angleDegrees2=90) for vertex in shape.Vertices())
    return one(shape.fuse(*offsets, tol=tolerance), 'exterior offset')


def contracted(shape, distance, top):
    sides = [face.thicken(-distance) for face in shape.Faces() if face.Center().z < top]
    return one(shape.cut(*sides, tol=tolerance), 'core offset')


def build():
    exterior, bore, m = funnel.build_solids()
    top, neck, end = m['top_z'], m['neck_z'], m['end_z']
    x, y = m['ncx'], m['ncy']
    tip_bottom = end-tip_length
    floor = tip_bottom-base_thickness
    body_width = m['out_w']+2*rim_margin
    plate_width = body_width+2*register_wall
    tip_radius = m['spout_or']-tip_step
    tip = cq.Solid.makeCone(tip_radius-tip_draft, tip_radius, tip_length,
        cq.Vector(x, y, tip_bottom))
    nominal_exterior = one(exterior.fuse(tip), 'nominal casting envelope')
    forming_void = expanded(nominal_exterior, finish_allowance)

    taper_bottom = floor+foot_height
    taper_rise = ((body_width-foot_width)/math.sqrt(2)
                  +(foot_radius-rim_radius)*(math.sqrt(2)-1))
    taper_top = taper_bottom+taper_rise
    foot = rounded(foot_width, foot_radius, floor, taper_bottom)
    lower_wire = cq.Workplane(obj=foot).faces('>Z').val().outerWire()
    collar = rounded(body_width, rim_radius, taper_top, top)
    upper_wire = cq.Workplane(obj=collar).faces('<Z').val().outerWire()
    taper = cq.Solid.makeLoft([lower_wire, upper_wire], ruled=True)
    stock = one(foot.fuse(taper, collar), 'cavity stock')
    outer_faces = [face for face in stock.Faces()
                   if not (face.geomType() == 'PLANE' and face.normalAt().z > 0.9)]
    minimum_backing = min(forming_void.distance(face) for face in outer_faces)
    assert minimum_backing >= forming_backing-tolerance, 'forming face backing'
    cavity = one(stock.cut(forming_void), 'cavity')
    for angle in (0, 90, 180, 270):
        notch = box(pry_depth+1, pry_width, top-pry_height, top+1,
                    body_width/2-pry_depth/2+0.5)
        cavity = cavity.cut(notch.rotate((0, 0, 0), (0, 0, 1), angle))
    key_slot = box(key_depth+1, key_width, top-register_depth, top+1,
                   body_width/2-key_depth/2+0.5, key_y)
    cavity = cavity.cut(key_slot)
    cavity = one(cavity, 'cavity with pry lands')

    nominal_plug = one(bore.intersect(box(plate_width, plate_width,
                                         neck, top+1)), 'nominal core')
    plug = contracted(nominal_plug, finish_allowance, top)
    plate = rounded(plate_width, rim_radius+register_wall, top, top+plate_thickness)
    plate = plate.cut(box(m['out_w']+2*finish_allowance,
                         m['out_d']+2*finish_allowance, top-1, top+finish_allowance))
    register = rounded(plate_width, rim_radius+register_wall, top-register_depth, top)
    register = register.cut(rounded(body_width+2*register_clearance,
        rim_radius+register_clearance, top-register_depth-1, top+1))
    for angle in (0, 90, 180, 270):
        opening = box(register_wall+2, pry_width, top-register_depth-1, top+1,
                      body_width/2+register_wall/2)
        register = register.cut(opening.rotate((0, 0, 0), (0, 0, 1), angle))
    key_inner = body_width/2-key_depth+register_clearance
    key_outer = body_width/2+register_clearance+1
    key = box(key_outer-key_inner, key_width-2*register_clearance,
              top-register_depth+register_clearance, top,
              (key_inner+key_outer)/2, key_y)
    register = register.fuse(key)

    rod_below = funnel.spout_tube+tip_length-tip_cap
    rod_socket = rod_length-rod_below
    rod_bottom, rod_top = tip_bottom+tip_cap, neck+rod_socket
    rod = cylinder(rod_diameter/2, rod_bottom, rod_top, x, y)
    socket = cylinder((rod_diameter+rod_clearance)/2, neck-1, rod_top, x, y)
    socket_vent = cylinder(socket_vent_diameter/2, rod_top-socket_vent_overlap,
        top+plate_thickness+1, x+rod_diameter/2, y)
    core = plug.fuse(plate, register).cut(socket, socket_vent)
    port_radius = m['out_w']/2-m['rim_ring']/2
    pour = (-port_radius, -port_radius)
    vents = [(port_radius, -port_radius), (port_radius, port_radius),
             (-port_radius, port_radius), (-port_radius, 0), (port_radius, 0)]
    ports = [cylinder(pour_diameter/2, top-1, top+plate_thickness+1, *pour)]
    ports.extend(cylinder(vent_diameter/2, top-1, top+plate_thickness+1, *xy)
                 for xy in vents)
    core = one(core.cut(*ports), 'core')
    cast = one(exterior.cut(bore).fuse(tip.cut(rod)), 'silicone casting')
    assert cavity.intersect(core).Volume() < tolerance
    assert cavity.intersect(cast).Volume() < tolerance
    assert core.intersect(cast).Volume() < tolerance
    assert top+plate_thickness-rod_top > forming_backing
    assert socket.cut(rod).intersect(socket_vent).Volume() > 0.01, 'socket air cannot reach vent'
    for lift in (0.5, 1.5, 3, 6, 12, rod_socket, 52):
        assert cavity.intersect(core.translate((0, 0, lift))).Volume() < tolerance
    for angle in (90, 180, 270):
        turned = core.rotate((0, 0, 0), (0, 0, 1), angle)
        assert cavity.intersect(turned).Volume() > 1, 'key permits incorrect closure'
    for angle in (0, 90, 180, 270):
        blade = box(14, pry_width-2, top-pry_height+0.2, top-0.2,
                    body_width/2+3)
        blade = blade.rotate((0, 0, 0), (0, 0, 1), angle)
        assert sum(blade.intersect(s).Volume() for s in (core, cavity)) < tolerance
    shift = (0, 0, -floor)
    parts = {name: shape.translate(shift) for name, shape in
             [('cavity', cavity), ('core', core), ('funnel', cast), ('rod', rod)]}
    dimensions = {name: [s.BoundingBox().xlen, s.BoundingBox().ylen,
                         s.BoundingBox().zlen] for name, s in parts.items()}
    info = {'dimensions_mm': dimensions,
            'volume_ml': {name: s.Volume()/1000 for name, s in parts.items()},
            'parting_z_mm': top-floor, 'rod_socket_depth_mm': rod_socket,
            'rod_socket_vent_diameter_mm': socket_vent_diameter,
            'register_depth_mm': register_depth, 'finish_allowance_mm': finish_allowance,
            'cavity_stock_minimum_backing_before_rim_notches_mm': minimum_backing,
            'ramp_print_z_mm': {'cavity': [neck-floor, m['ramp_top_z']-floor],
                'core': [top+plate_thickness-m['ramp_top_z'], top+plate_thickness-neck]},
            'nominal_chamber_diameter_mm': chamber_diameter,
            'status': 'CAD design; physical printing and release untested'}
    return parts, info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    parts, info = build()
    colors = {'cavity': cq.Color('#3D9998'), 'core': cq.Color('#D8A751'),
              'funnel': cq.Color('#555C68'), 'rod': cq.Color('#AAB9C8')}
    assembly = cq.Assembly()
    radii = []
    for name, shape in parts.items():
        assembly.add(shape, name=name, color=colors[name])
        single = one_body(cq.Workplane(obj=shape), name, colors[name])
        export_assembly(single, str(args.output/f'{name}.step'))
        if name in ('cavity', 'core'):
            path = args.output/f'{name}.stl'
            cq.exporters.export(shape, str(path), tolerance=0.02, angularTolerance=0.08)
            mesh = trimesh.load(path, force='mesh', process=True)
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
            mesh.export(path)
            write_print_payload(args.output/f'{name}.step', path)
            radii.append(float(np.linalg.norm(mesh.vertices[:, :2], axis=1).max()))
    export_assembly(assembly, str(args.output/'assembly.step'))
    overview = cq.Assembly()
    spacing = (parts['cavity'].BoundingBox().xlen+parts['core'].BoundingBox().xlen)/4+22
    overview.add(parts['cavity'].translate((-spacing, 0, 0)), name='cavity', color=colors['cavity'])
    core = parts['core'].rotate((0, 0, 0), (1, 0, 0), 180)
    core = core.translate((spacing, 0, -core.BoundingBox().zmin))
    overview.add(core, name='core', color=colors['core'])
    export_assembly(overview, str(args.output/'overview.step'))
    section = cq.Assembly()
    section_slab = box(240, 2, -1, 120)
    for name, shape in parts.items():
        section.add(shape.intersect(section_slab), name=name, color=colors[name])
    export_assembly(section, str(args.output/'section.step'))
    info['enclosing_diameter_mm'] = 2*max(radii)
    info['chamber_radial_clearance_mm'] = chamber_diameter/2-max(radii)
    assert info['chamber_radial_clearance_mm'] > 10
    (args.output/'design.json').write_text(json.dumps(info, indent=2)+'\n')
    print(json.dumps(info, indent=2), flush=True)


if __name__ == '__main__':
    main()
