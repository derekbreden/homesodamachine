"""Two open-backed PETG shells following the silicone funnel's forming faces.

Frame: funnel brim centred in XY, cavity feet at Z=0, +Z is closure lift.
The cavity prints upright; the core prints inverted, open dry back on the bed.
Slicer tree supports carry the dry faces. Both modeled skins print solid.
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
sys.path[:0] = [str(ROOT/'hardware/printed-parts/zone-c/funnel'),
                str(ROOT/'hardware/scripts')]
import funnel
from _cadq_export import export_assembly
from _materials import one_body
from flute_payload import cut as write_print_payload

finish_allowance = 0.30
shell_thickness = 5.0
flange_thickness = 5.0
flange_margin = 16.0
flange_radius = 16.0
bolt_diameter = 5.0
bolt_edge_margin = 6.0
bolt_station = 50.0
locator_diameter = 8.0
locator_height = 3.0
locator_leadin = 1.0
locator_clearance = 0.60
locator_slot_travel = 1.5
locator_y = (22.0, -12.0)
tip_length = 12.0
tip_step = 1.0
tip_cap = 2.0
tip_draft = 0.5
rod_diameter = 6.35
rod_length = 50.8
rod_clearance = 0.30
socket_wall = 4.0
socket_cap = 3.0
socket_vent_diameter = 2.5
socket_vent_overlap = 1.0
vent_diameter = 4.0
pour_diameter = 11.0
foot_diameter = 10.0
foot_clearance = 0.7
feet_xy = ((-55.0, -50.0), (55.0, -50.0), (0.0, 65.0))
pry_width = 16.0
pry_depth = 5.0
pry_height = 1.0
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
    floor = tip_bottom-finish_allowance-shell_thickness-foot_clearance
    flange_width = m['out_w']+2*flange_margin
    bolt_radius = flange_width/2-bolt_edge_margin
    bolt_xy = [(side*bolt_radius, station*bolt_station)
               for side in (-1, 1) for station in (-1, 1)]
    bolt_xy += [(station*bolt_station, side*bolt_radius)
                for side in (-1, 1) for station in (-1, 1)]
    locator_xy = [(bolt_radius, locator_y[0]), (-bolt_radius, locator_y[1])]

    tip_radius = m['spout_or']-tip_step
    tip = cq.Solid.makeCone(tip_radius-tip_draft, tip_radius, tip_length,
                            cq.Vector(x, y, tip_bottom))
    nominal_exterior = one(exterior.fuse(tip), 'casting envelope')
    print('Offsetting cavity forming face and dry back', flush=True)
    forming_void = expanded(nominal_exterior, finish_allowance)
    cavity_outer = expanded(nominal_exterior, finish_allowance+shell_thickness)
    cavity_flange = rounded(flange_width, flange_radius, top-flange_thickness, top)
    feet = [cylinder(foot_diameter/2, floor, m['ramp_top_z'], *xy) for xy in feet_xy]
    cavity = one(cavity_outer.fuse(cavity_flange, *feet).cut(forming_void)
                 .intersect(box(flange_width+2, flange_width+2, floor, top)), 'cavity shell')

    back = top+flange_thickness
    nominal_plug = one(bore.intersect(box(flange_width, flange_width, neck, top))
        .fuse(box(m['bore_w'], m['bore_d'], top, back+1)), 'core envelope')
    plug = contracted(nominal_plug, finish_allowance, back+1)
    dry_void = contracted(nominal_plug, finish_allowance+shell_thickness, back+1)
    plate = rounded(flange_width, flange_radius, top, back)
    # The brim's top face grows downward by the measured finishing thickness.
    plate = plate.cut(box(m['out_w']+2*finish_allowance,
                         m['out_d']+2*finish_allowance, top-1, top+finish_allowance))
    core = one(plug.fuse(plate).cut(dry_void)
               .intersect(box(flange_width+2, flange_width+2, neck, back)), 'core shell')

    rod_below = funnel.spout_tube+tip_length-tip_cap
    rod_socket = rod_length-rod_below
    rod_bottom, rod_top = tip_bottom+tip_cap, neck+rod_socket
    rod = cylinder(rod_diameter/2, rod_bottom, rod_top, x, y)
    socket_radius = (rod_diameter+rod_clearance)/2
    socket = cylinder(socket_radius, neck-1, rod_top, x, y)
    boss = cylinder(socket_radius+socket_wall, neck+finish_allowance,
                    rod_top+socket_cap, x, y)
    socket_vent = cylinder(socket_vent_diameter/2, rod_top-socket_vent_overlap,
                          rod_top+socket_cap+1, x+rod_diameter/2, y)
    core = one(core.fuse(boss.intersect(plug)).cut(socket, socket_vent), 'core and vented rod socket')

    locators, locator_holes = [], []
    for index, (px, py) in enumerate(locator_xy):
        peg = cylinder(locator_diameter/2, top-1, top+locator_height-locator_leadin, px, py)
        lead = cq.Solid.makeCone(locator_diameter/2, locator_diameter/2-locator_leadin,
                                locator_leadin, cq.Vector(px, py, top+locator_height-locator_leadin))
        locators.append(peg.fuse(lead))
        r = locator_diameter/2+locator_clearance
        hole = cylinder(r, top-1, back+1, px, py)
        entry = cq.Solid.makeCone(r+locator_leadin, r, locator_leadin,
                                 cq.Vector(px, py, top))
        if index:
            # The second locator's X slot admits centre-distance error.
            hole = hole.fuse(hole.translate((locator_slot_travel, 0, 0)),
                             hole.translate((-locator_slot_travel, 0, 0)),
                             box(2*locator_slot_travel, 2*r, top-1, back+1, px, py))
            entry = entry.fuse(entry.translate((locator_slot_travel, 0, 0)),
                               entry.translate((-locator_slot_travel, 0, 0)))
        locator_holes.append(hole.fuse(entry))
    cavity = one(cavity.fuse(*locators), 'cavity and locators')
    core = one(core.cut(*locator_holes), 'core locator holes')

    bolts = [cylinder(bolt_diameter/2, floor-1, back+1, *xy) for xy in bolt_xy]
    cavity = one(cavity.cut(*bolts), 'cavity clamp holes')
    core = one(core.cut(*bolts), 'core clamp holes')
    port_radius = m['out_w']/2-m['rim_ring']/2
    pour = (-port_radius, -port_radius)
    vents = [(port_radius, -port_radius), (port_radius, port_radius),
             (-port_radius, port_radius), (-port_radius, 0), (port_radius, 0)]
    ports = [cylinder(pour_diameter/2, top-1, back+1, *pour)]
    ports += [cylinder(vent_diameter/2, top-1, back+1, *xy) for xy in vents]
    core = one(core.cut(*ports), 'core fill and vents')
    for angle in (0, 90, 180, 270):
        notch = box(pry_depth+1, pry_width, top-pry_height, top+1,
                    flange_width/2-pry_depth/2+0.5)
        cavity = cavity.cut(notch.rotate((0, 0, 0), (0, 0, 1), angle))
    cavity = one(cavity, 'cavity opening notches')
    cast = one(exterior.cut(bore).fuse(tip.cut(rod)), 'silicone casting')

    print('Checking closure, release, passages and wall backing', flush=True)
    assert cavity.intersect(core).Volume() < tolerance
    assert all(s.intersect(cast).Volume() < tolerance for s in (cavity, core))
    assert all(s.intersect(rod).Volume() < tolerance for s in (cavity, core))
    for lift in (0.5, 1.5, 3, 6, 12, rod_socket, 52):
        assert cavity.intersect(core.translate((0, 0, lift))).Volume() < tolerance
    for angle in (90, 180, 270):
        assert cavity.intersect(core.rotate((0, 0, 0), (0, 0, 1), angle)).Volume() > 1
    assert socket.cut(rod).intersect(socket_vent).Volume() > 0.01
    assert dry_void.distance(cast) >= shell_thickness+finish_allowance-tolerance
    assert (forming_void.cut(nominal_exterior).Volume() > 0)
    for xy in bolt_xy:
        # M4 washers, 9 mm OD, sit directly on both flat flange backs.
        washer = cylinder(4.5, top-flange_thickness-1, top-flange_thickness, *xy)
        assert washer.intersect(cavity).Volume() < tolerance
    for xy in [pour, *vents]:
        assert core.intersect(cylinder(0.5, top-0.5, back+1, *xy)).Volume() < tolerance
    # A straight lift through the large dry opening keeps support removal accessible.
    dry_mouth = box(m['bore_w']-2*(shell_thickness+finish_allowance),
                    m['bore_d']-2*(shell_thickness+finish_allowance), back-1, back+1)
    assert core.intersect(dry_mouth).Volume() < tolerance
    shift = (0, 0, -floor)
    parts = {name: shape.translate(shift) for name, shape in
             [('cavity', cavity), ('core', core), ('funnel', cast), ('rod', rod)]}
    info = {
        'dimensions_mm': {n: [s.BoundingBox().xlen, s.BoundingBox().ylen,
                              s.BoundingBox().zlen] for n, s in parts.items()},
        'volume_ml': {n: s.Volume()/1000 for n, s in parts.items()},
        'shell_thickness_mm': shell_thickness, 'flange_thickness_mm': flange_thickness,
        'parting_z_mm': top-floor, 'finish_allowance_mm': finish_allowance,
        'rod_socket_depth_mm': rod_socket, 'rod_socket_diametral_clearance_mm': rod_clearance,
        'rod_socket_vent_diameter_mm': socket_vent_diameter,
        'locators': {'diameter_mm': locator_diameter, 'height_mm': locator_height,
                     'radial_clearance_mm': locator_clearance, 'slot_travel_each_way_mm': locator_slot_travel,
                     'centres_xy_mm': locator_xy},
        'clamping': {'hole_diameter_mm': bolt_diameter, 'centres_xy_mm': bolt_xy,
                     'fastener': 'M4 x 20 with 9 mm OD washers and nuts; or small clamps on flange'},
        'ports': {'fill_diameter_mm': pour_diameter, 'vent_diameter_mm': vent_diameter,
                  'fill_xy_mm': pour, 'vent_xy_mm': vents},
        'feet': {'diameter_mm': foot_diameter, 'centres_xy_mm': feet_xy,
                 'spout_back_clearance_mm': foot_clearance},
        'dry_opening_mm': m['bore_w']-2*(shell_thickness+finish_allowance),
        'ramp_print_z_mm': {'cavity': [neck-floor, m['ramp_top_z']-floor],
                            'core': [back-m['ramp_top_z'], back-neck]},
        'nominal_chamber_diameter_mm': chamber_diameter,
        'load_screen': load_screen(m, tip_bottom),
        'status': 'CAD and slice verification; coated closure, vacuum cycle and casting untested'}
    return parts, info


def load_screen(m, tip_bottom):
    # Simply supported flat-square screening surrogate; q is uniform at the maximum head.
    span = m['w']
    pressure = 0.001  # N/mm² = 1 kPa, including head and a modest process allowance.
    modulus = 1000.0  # MPa assumption for an untested solid PETG print at room temperature.
    poisson = 0.4
    rigidity = modulus*shell_thickness**3/(12*(1-poisson**2))
    deflection = 0.00406*pressure*span**4/rigidity
    head = m['top_z']+flange_thickness-tip_bottom
    return {'model': 'simply supported flat square under uniform load; screening, not FEA or a pressure rating',
            'span_mm': span, 'pressure_kpa': pressure*1000,
            'assumed_modulus_mpa': modulus, 'assumed_poisson_ratio': poisson,
            'silicone_density_assumption_kg_m3': 1130,
            'maximum_silicone_head_mm': head, 'head_pressure_kpa': 1130*9.81*(head/1000)/1000,
            'screen_deflection_mm': deflection,
            'pressure_force_n': pressure*span**2,
            'condition': 'fill, vents and both dry backs open to the same chamber; no sealed pressure differential',
            'material_reference': 'https://store.bblcdn.eu/s8/default/71ca815e70e74afc96ff5883f003235f/Bambu_PETG_Translucent_Technical_Data_Sheet.pdf'}


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
def write_back_view(parts, output):
    backs = cq.Assembly()
    for name, dx, color in [('cavity', -120, '#3D9998'), ('core', 120, '#D8A751')]:
        part = parts[name]
        if name == 'cavity':
            part = part.rotate((0, 0, 0), (1, 0, 0), 180)
        part = part.translate((dx, 0, -part.BoundingBox().zmin))
        backs.add(part, name=name, color=cq.Color(color))
    export_assembly(backs, str(output/'backs.step'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
        default=ROOT/'hardware/printed-parts/zone-c/funnel-mold')
    args = parser.parse_args()
    parts, info = build()
    write_parts(parts, info, args.output)
    write_back_view(parts, args.output)


if __name__ == '__main__':
    main()
