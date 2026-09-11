"""PETG funnel tooling with two open V channels in each print back, in the funnel's brim-centred assembly frame.

The cavity stands on a rounded foot with a continuous outer taper, at least
60 degrees above the print bed including the rounded corners.
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

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p/'hardware/scripts/_cadq_export.py').is_file())
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
foot_width = 146.0
foot_radius = 12.0
foot_height = 3.2
outer_taper_angle = 60.0
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


def build_stock():
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
    taper_run = ((body_width-foot_width)/math.sqrt(2)
                 +(foot_radius-rim_radius)*(math.sqrt(2)-1))
    taper_rise = taper_run*math.tan(math.radians(outer_taper_angle))
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
            'cavity_outer_taper': {
                'foot_width_mm': foot_width, 'foot_height_mm': foot_height,
                'taper_top_z_mm': taper_top-floor,
                'minimum_angle_from_bed_degrees': outer_taper_angle,
                'maximum_outward_growth_per_0_40_mm_layer':
                    0.4/math.tan(math.radians(outer_taper_angle))},
            'ramp_print_z_mm': {'cavity': [neck-floor, m['ramp_top_z']-floor],
                'core': [top+plate_thickness-m['ramp_top_z'], top+plate_thickness-neck]},
            'nominal_chamber_diameter_mm': chamber_diameter,
            'status': 'CAD design; physical printing and release untested'}
    return parts, info


def write_parts(parts, info, output):
    """Export one tooling design and views of those same bodies."""
    output.mkdir(parents=True, exist_ok=True)
    colors = {'cavity': cq.Color('#3D9998'), 'core': cq.Color('#D8A751'),
              'funnel': cq.Color('#555C68'), 'rod': cq.Color('#AAB9C8')}
    assembly = cq.Assembly()
    radii = []
    for name, shape in parts.items():
        assembly.add(shape, name=name, color=colors[name])
        single = one_body(cq.Workplane(obj=shape), name, colors[name])
        export_assembly(single, str(output/f'{name}.step'))
        if name in ('cavity', 'core'):
            path = output/f'{name}.stl'
            cq.exporters.export(shape, str(path), tolerance=0.02, angularTolerance=0.08)
            mesh = trimesh.load(path, force='mesh', process=True)
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
            mesh.export(path)
            write_print_payload(output/f'{name}.step', path)
            radii.append(float(np.linalg.norm(mesh.vertices[:, :2], axis=1).max()))
    export_assembly(assembly, str(output/'assembly.step'))
    overview = cq.Assembly()
    spacing = (parts['cavity'].BoundingBox().xlen+parts['core'].BoundingBox().xlen)/4+22
    overview.add(parts['cavity'].translate((-spacing, 0, 0)), name='cavity', color=colors['cavity'])
    core = parts['core'].rotate((0, 0, 0), (1, 0, 0), 180)
    core = core.translate((spacing, 0, -core.BoundingBox().zmin))
    overview.add(core, name='core', color=colors['core'])
    export_assembly(overview, str(output/'overview.step'))
    section = cq.Assembly()
    section_slab = box(240, 2, -1, 120)
    for name, shape in parts.items():
        section.add(shape.intersect(section_slab), name=name, color=colors[name])
    export_assembly(section, str(output/'section.step'))
    info['enclosing_diameter_mm'] = 2*max(radii)
    info['chamber_radial_clearance_mm'] = chamber_diameter/2-max(radii)
    assert info['chamber_radial_clearance_mm'] > 10
    (output/'design.json').write_text(json.dumps(info, indent=2)+'\n')
    print(json.dumps(info, indent=2), flush=True)



centres = (-28.0, 28.0)
roof_rise_per_run = 5.0/3.0
cavity_depth = 28.0
core_depth = 32.0
core_mouth_depth = 3.0
core_deep_half_length = 35.0
core_taper_end = 65.0
minimum_backing = 6.0


def channel(stations, y):
    """A ruled V roof, with height varying along X and a constant side slope."""
    profiles = []
    for x, height in stations:
        half_width = (height+1)/roof_rise_per_run
        profiles.append(cq.Wire.makePolygon([
            cq.Vector(x, y-half_width, -1), cq.Vector(x, y+half_width, -1),
            cq.Vector(x, y, height)], close=True))
    return cq.Solid.makeLoft(profiles, ruled=True)


def build():
    parts, info = build_stock()
    reference = dict(parts)
    back_z = parts['core'].BoundingBox().zmax
    profiles = {
        'cavity': [(-120, cavity_depth), (120, cavity_depth)],
        'core': [(-110, core_mouth_depth), (-core_taper_end, core_mouth_depth),
                 (-core_deep_half_length, core_depth), (core_deep_half_length, core_depth),
                 (core_taper_end, core_mouth_depth), (110, core_mouth_depth)]}
    reports = {}
    for name in ('cavity', 'core'):
        tools = []
        for y in centres:
            tool = channel(profiles[name], y)
            if name == 'core':
                tool = tool.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, back_z))
            tools.append(tool)
        removed = [one(reference[name].intersect(tool), f'{name} channel')
                   for tool in tools]
        clearance = min(p.distance(parts['funnel']) for p in removed)-finish_allowance
        assert clearance >= minimum_backing, (name, 'forming backing', clearance)
        assert all(p.distance(parts['rod']) >= minimum_backing for p in removed)
        parts[name] = one(reference[name].cut(*tools), name)
        assert reference[name].intersect(parts[name]).Volume() > parts[name].Volume()-0.001
        assert parts[name].intersect(parts['funnel']).Volume() < 0.001
        # The cutter must open through both sides above a flat shelf. At these
        # stations its section is entirely outside the original body's bounds.
        assert all(t.BoundingBox().xmin < reference[name].BoundingBox().xmin and
                   t.BoundingBox().xmax > reference[name].BoundingBox().xmax for t in tools)
        for y in centres:
            passage = cq.Solid.makeCylinder(0.5, 240, cq.Vector(-120, y, 1.1), cq.Vector(1, 0, 0))
            if name == 'core':
                passage = passage.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, back_z))
            assert parts[name].intersect(passage).Volume() < 0.001, 'side passage obstructed'
        bed_z = reference[name].BoundingBox().zmin if name == 'cavity' else back_z
        bed_area = lambda s: sum(f.Area() for f in s.Faces()
            if f.geomType() == 'PLANE' and abs(f.Center().z-bed_z) < 1e-6
            and abs(f.normalAt().z) > .999)
        reports[name] = {
            'stock_volume_ml': reference[name].Volume()/1000,
            'volume_ml': parts[name].Volume()/1000,
            'removed_ml': sum(p.Volume() for p in removed)/1000,
            'minimum_added_channel_to_forming_face_mm': clearance,
            'bed_contact_mm2': bed_area(parts[name]),
            'stock_bed_contact_mm2': bed_area(reference[name])}
        info['volume_ml'][name] = parts[name].Volume()/1000
    assert parts['cavity'].intersect(parts['core']).Volume() < 0.001
    info['channels'] = {
        'count_per_body': 2, 'centres_y_mm': centres,
        'roof_angle_from_bed_degrees': math.degrees(math.atan(roof_rise_per_run)),
        'max_horizontal_growth_per_0_40_mm_layer': 0.4/roof_rise_per_run,
        'cavity_depth_mm': cavity_depth, 'core_depth_mm': core_depth,
        'core_side_mouth_height_mm': core_mouth_depth,
        'core_side_mouth_width_mm': 2*core_mouth_depth/roof_rise_per_run,
        'clear_through_passage_diameter_mm': 1.0,
        'parts': reports}
    return parts, info



def write_channel_views(parts, output):
    # A transverse section cuts across both V channels and shows their roof angle.
    section = cq.Assembly()
    slab = box(2, 240, -1, 120)
    colors = {'cavity': cq.Color('#3D9998'), 'core': cq.Color('#D8A751'),
              'funnel': cq.Color('#555C68'), 'rod': cq.Color('#AAB9C8')}
    for name, part in parts.items():
        section.add(part.intersect(slab), name=name, color=colors[name])
    export_assembly(section, str(output/'channel-section.step'))
    backs = cq.Assembly()
    for name, dx in (('cavity', -120), ('core', 120)):
        part = parts[name]
        if name == 'cavity':
            part = part.rotate((0, 0, 0), (1, 0, 0), 180)
        part = part.translate((dx, 0, -part.BoundingBox().zmin))
        backs.add(part, name=name, color=colors[name])
    export_assembly(backs, str(output/'backs.step'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
        default=ROOT/'hardware/printed-parts/zone-c/funnel-mold')
    args = parser.parse_args()
    parts, info = build()
    write_parts(parts, info, args.output)
    write_channel_views(parts, args.output)


if __name__ == '__main__':
    main()
