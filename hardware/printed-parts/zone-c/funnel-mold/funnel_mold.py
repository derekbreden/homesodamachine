"""Two PETG mold bodies with flat print bases and steep corbels.

Frame: funnel brim centred in XY, cavity base at Z=0, +Z is closure lift.
The cavity prints upright; the core prints inverted on its flat dry back.
Six walls and 15% gyroid fill the solid stock. Bolt pockets have open side access.
"""

import argparse
import functools
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq
from cadquery.occ_impl.shapes import fuse as fuse_shapes
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCP.BRepOffset import BRepOffset_Mode
from OCP.GeomAbs import GeomAbs_Arc
import numpy as np
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p/'hardware/scripts/_cadq_export.py').is_file())
sys.path[:0] = [str(ROOT/'hardware/printed-parts/zone-c/funnel'),
                str(ROOT/'hardware/scripts')]
import funnel
from _cadq_export import export_assembly, import_assembly, import_step
from _materials import one_body
from flute_payload import cut as write_print_payload

finish_allowance = 0.30
# Dry-backing margin for the forming ramp's rounded offset joins.
forming_join_allowance = 0.01
shell_thickness = 5.0
corbel_run_per_rise = 0.5
base_thickness = 5.0
bolt_pocket_height = 8.0
bolt_pocket_width = 12.0
flange_thickness = 5.0
flange_margin = 16.0
flange_radius = 24.0
bolt_diameter = 5.0
bolt_edge_margin = 6.0
bolt_station = 50.0
locator_diameter = 8.0
locator_height = 3.0
locator_leadin = 1.0
locator_clearance = 0.60
locator_slot_travel = 1.5
locator_y = (22.0, -12.0)
rod_diameter = funnel.spout_id
rod_length = 25.0
rod_clearance = 0.40
rod_guide_length = 8.0
rod_seat_wall = shell_thickness
# The rod's lower end stands in a blind socket in the cavity floor, so the bore opens through
# the plug's bottom face. Both depths are measured below that face.
rod_socket_diameter = rod_diameter+rod_clearance
rod_socket_depth = 1.5
rod_end_depth = rod_socket_depth
vent_diameter = 4.0
pour_diameter = 11.0
floor_reserve = 0.7
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


def rounded(width, depth, radius, bottom, top):
    return cq.Workplane(obj=box(width, depth, bottom, top)).edges('|Z').fillet(radius).val()


def cleaned_shape(shape):
    """Unify faces when OCCT can preserve the boolean result's validity."""
    # Unifying coincident NURBS faces can lose a trim around the rod passage.
    # Keep the valid boolean result when OCCT's optional cleanup cannot preserve it.
    try:
        cleaned = shape.clean()
        if cleaned.isValid():
            shape = cleaned
    except Exception:
        if not shape.isValid():
            raise
    return shape


def single(shape, name):
    """The one valid solid in `shape`, or None with the reading on stderr."""
    shape = cleaned_shape(shape)
    solids = shape.Solids()
    if shape.isValid() and len(solids) == 1:
        return solids[0]
    print(f'{name}: valid={shape.isValid()} solids={len(solids)} '
          f'volumes={[round(s.Volume(), 3) for s in solids]}', file=sys.stderr, flush=True)
    return None


def one(shape, name):
    solid = single(shape, name)
    assert solid is not None, name
    return solid


def slab(face, distance):
    """The material within `distance` inside `face`. A plane's slab reaches past the
    face's own edges so its sides are nowhere coplanar with a neighbour's."""
    if face.geomType() == 'PLANE':
        plane = cq.Plane(origin=face.Center(), normal=-face.normalAt())
        return cq.Workplane(plane).rect(1000, 1000).extrude(distance).val()
    return face.thicken(-distance)


def contraction_attempts(shape, faces, distance):
    """An inward normal offset with joined edges, then face-skin fallbacks."""
    def joined():
        offset = BRepOffsetAPI_MakeOffsetShape()
        offset.PerformByJoin(shape.wrapped, -distance, 1e-5,
                             BRepOffset_Mode.BRepOffset_Skin,
                             True, False, GeomAbs_Arc, False)
        assert offset.IsDone() and not offset.Shape().IsNull(), 'joined core offset'
        inset = cq.Shape.cast(offset.Shape())
        if not inset.Solids() and len(inset.Shells()) == 1:
            inset = cq.Solid.makeSolid(inset.Shells()[0])
        assert inset.cut(shape, tol=tolerance).Volume() < tolerance
        return inset

    def sequential(tool):
        return functools.reduce(lambda s, f: s.cut(tool(f, distance), tol=tolerance),
                                faces, shape)
    yield 'joined normal offset', joined
    yield 'planes as slabs', lambda: shape.cut(
        *[slab(f, distance) for f in faces], tol=tolerance)
    yield 'faces at once', lambda: shape.cut(
        *[f.thicken(-distance) for f in faces], tol=tolerance)
    yield 'faces one at a time', lambda: sequential(lambda f, d: f.thicken(-d))
    yield 'slabs one at a time', lambda: sequential(slab)


def expanded(shape, distance):
    return funnel.normal_envelope(shape, distance)


def contracted(shape, distance, top):
    faces = [face for face in shape.Faces() if face.Center().z < top]
    boundary = cq.Compound.makeCompound(faces)
    for label, attempt in contraction_attempts(shape, faces, distance):
        try:
            solid = single(attempt(), f'core offset, {label}')
        except Exception as error:
            print(f'core offset, {label}: {error!r}', file=sys.stderr, flush=True)
            continue
        if solid is not None:
            clearance = boundary.distance(solid)
            if clearance >= distance - 0.001:
                return solid
            print(f'core offset, {label}: {clearance:g} mm minimum, '
                  f'wants {distance:g} mm', file=sys.stderr, flush=True)
    raise AssertionError('core offset')


def liquid_containment(cavity, core, rod, cast, floor, top, back, width,
                       neck, pour, vents, x, y, guide_top):
    """Check closure with the intended fill, vent and rod-guide mouths capped."""
    overlap = 0.02
    surrounding = box(width+26, width+26, floor-2, back+8)
    outside = cq.Vector(-(width+26)/2+1, 0, floor)
    # In the plug's silicone, beside the rod and above its socket.
    witness = cq.Vector(x+rod_diameter, y, rod.BoundingBox().zmin+rod_socket_depth)
    mouth_cap = box(width+2, width+2, top-overlap, back+2)
    ports = [(pour, pour_diameter), *[(xy, vent_diameter) for xy in vents]]
    caps = [cylinder(diameter/2+overlap, back-overlap, back+1, *xy)
            for xy, diameter in ports]
    caps.append(cylinder((rod_diameter+rod_clearance)/2+overlap,
                         guide_top-overlap, guide_top+1, x, y))
    readings = {}
    for label, tools in [('cavity', [cavity, mouth_cap]),
                         ('assembled', [cavity, core, rod, *caps])]:
        remainder = cleaned_shape(surrounding.cut(*tools))
        assert remainder.isValid(), f'{label}: invalid liquid complement'
        retained = [s for s in remainder.Solids()
                    if s.isInside(witness, 1e-6) and not s.isInside(outside, 1e-6)]
        assert len(retained) == 1, f'{label}: liquid space leaks to outside'
        target = cast.cut(*tools)
        missing = target.cut(retained[0]).Volume()
        assert missing < tolerance, f'{label}: {missing:g} mm3 of casting outside retained liquid'
        readings[label] = {'retained_volume_ml': retained[0].Volume()/1000,
                           'casting_outside_retained_mm3': missing}
    return readings


def build():
    exterior, bore, m = funnel.build_solids()
    top, neck, end = m['top_z'], m['neck_z'], m['end_z']
    x, y = m['ncx'], m['ncy']
    floor = end-rod_socket_depth-shell_thickness-floor_reserve
    flange_width = m['out_w']+2*flange_margin
    flange_depth = m['out_d']+2*flange_margin
    bolt_x = flange_width/2-bolt_edge_margin
    bolt_y = flange_depth/2-bolt_edge_margin
    bolt_xy = [(side*bolt_x, station*bolt_station)
               for side in (-1, 1) for station in (-1, 1)]
    bolt_xy += [(station*bolt_station, side*bolt_y)
                for side in (-1, 1) for station in (-1, 1)]
    locator_xy = [(bolt_x, locator_y[0]), (-bolt_x, locator_y[1])]

    nominal_exterior = one(exterior, 'casting envelope')
    print('Constructing forming faces and solid print bases', flush=True)
    forming_void = one(funnel.build_solids(outer_air=finish_allowance)[0], 'forming void')
    # Carry the forming ramp's rounded-join margin into its dry backing.
    backing_allowance = finish_allowance+shell_thickness+forming_join_allowance
    ramp = funnel._loft_rc(m['bore_w'], m['bore_d'], 0, 0, m['ramp_top_z'],
        m['spout_id']/2, x, y, neck, funnel.mouth_corner_r)
    cavity_outer = expanded(ramp, funnel.collar_wall + backing_allowance)
    backing_bodies = (
        funnel._rounded_box(m['w'], m['d'], funnel.collar_corner_r, m['ramp_top_z'], 0),
        funnel._rounded_box(m['out_w'], m['out_d'], funnel.brim_corner_r, 0, top),
        funnel.elbow_cradle.plug_outline(funnel.plug_width/2, 0.0, 0.0,
                                         funnel.plug_height).translate((x, y, end)),
    )
    # Fuse the analytic offset faces in one operation around the collar.
    backing = [cavity_outer, *[expanded(body, backing_allowance)
                               for body in backing_bodies],
               cylinder(rod_socket_diameter/2+shell_thickness,
                        end-rod_socket_depth-shell_thickness, end, x, y)]
    # Explicit spline surfaces preserve the trims where the offset ramp and
    # collar overlap, including the straight outlet's smaller neck radius.
    cavity_outer = one(fuse_shapes(*(s.toNURBS() for s in backing),
                                  tol=tolerance), 'cavity backing')
    forming_boundary = cq.Compound.makeCompound(forming_void.Faces())
    backing_boundary = cq.Compound.makeCompound(cavity_outer.Faces())
    minimum_backing = forming_boundary.distance(backing_boundary)
    cavity_flange = rounded(flange_width, flange_depth, flange_radius, top-flange_thickness, top)
    corbel_bottom = floor+base_thickness
    corbel_top = top-flange_thickness
    corbel_run = (corbel_top-corbel_bottom)*corbel_run_per_rise
    base_width, base_depth = flange_width-2*corbel_run, flange_depth-2*corbel_run
    base_radius = flange_radius-corbel_run
    assert base_radius > 0
    # Parallel rounded rectangles retain fixed corner centres. Their entire
    # outward boundary, including the curved corners, advances 0.5 mm/mm.
    base = rounded(base_width, base_depth, base_radius, floor, corbel_bottom)
    corbel = cq.Solid.makeLoft([
        funnel._rounded_wire(base_width, base_depth, base_radius, corbel_bottom),
        funnel._rounded_wire(flange_width, flange_depth, flange_radius, corbel_top),
    ], ruled=True)
    blank = one(base.fuse(corbel, cavity_flange), 'cavity stock')
    cavity = one(blank.cut(forming_void), 'cavity body')
    socket = cylinder(rod_socket_diameter/2, end-rod_socket_depth, end, x, y)
    cavity = one(cavity.cut(socket), 'cavity rod socket')

    back = top+flange_thickness
    nominal_plug = one(bore.intersect(box(flange_width, flange_depth, neck, top))
        .fuse(funnel._rounded_box(m['bore_w'], m['bore_d'], funnel.mouth_corner_r,
                                 top, back+1)), 'core envelope')
    # Explicit spline surfaces let the rod-guide booleans trim these
    # contracted lofts without relying on an OFFSET surface's continuation.
    plug = contracted(nominal_plug, finish_allowance, back+1).toNURBS()
    guide_radius = (rod_diameter+rod_clearance)/2
    guide_top = neck+rod_guide_length
    dry_radius = guide_radius+(back-guide_top)*corbel_run_per_rise
    # In the inverted print, this circular opening contracts at 0.5 mm/mm
    # until it meets the open straight rod guide; it has no flat ceiling.
    dry_void = cq.Solid.makeCone(guide_radius,
        dry_radius+corbel_run_per_rise, back+1-guide_top,
        cq.Vector(x, y, guide_top))
    plate = rounded(flange_width, flange_depth, flange_radius, top, back)
    # The brim's top face grows downward by the measured finishing thickness.
    plate = plate.cut(funnel._rounded_box(m['out_w']+2*finish_allowance,
        m['out_d']+2*finish_allowance, funnel.brim_corner_r+finish_allowance,
        top-1, top+finish_allowance))

    rod_bottom = end-rod_end_depth
    rod_top = rod_bottom+rod_length
    rod_engagement = rod_top-neck
    rod = cylinder(rod_diameter/2, rod_bottom, rod_top, x, y)
    seat = cylinder(guide_radius, neck-1, back+1, x, y)
    # An open straight guide admits the stock rod from the dry back. Its small
    # annular overflow and the lower-seat collar are accessible trim stock.
    core = one(plug.fuse(plate).cut(dry_void, seat)
               .intersect(box(flange_width+2, flange_depth+2, neck, back)),
               'core with open straight rod guide')

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
    bolt_pockets = []
    for px, py in bolt_xy:
        if abs(px) == bolt_x:
            sign = 1 if px > 0 else -1
            inner, outer = bolt_x-4.6, flange_width/2+1
            pocket = box(outer-inner, bolt_pocket_width,
                corbel_top-bolt_pocket_height, corbel_top,
                sign*(inner+outer)/2, py)
        else:
            sign = 1 if py > 0 else -1
            inner, outer = bolt_y-4.6, flange_depth/2+1
            pocket = box(bolt_pocket_width, outer-inner,
                corbel_top-bolt_pocket_height, corbel_top,
                px, sign*(inner+outer)/2)
        bolt_pockets.append(pocket)
    cavity = one(cavity.cut(*bolt_pockets), 'cavity bolt head access')
    cavity = one(cavity.cut(*bolts), 'cavity clamp holes')
    core = one(core.cut(*bolts), 'core clamp holes')
    port_radius = m['out_w']/2-m['rim_ring']/2
    arc_radius = funnel.brim_corner_r - m['rim_ring']/2
    corner_x = m['out_w']/2-funnel.brim_corner_r+arc_radius/math.sqrt(2)
    corner_y = m['out_d']/2-funnel.brim_corner_r+arc_radius/math.sqrt(2)
    pour = (-corner_x, -corner_y)
    vents = [(corner_x, -corner_y), (corner_x, corner_y),
             (-corner_x, corner_y), (-port_radius, 0), (port_radius, 0)]
    ports = [cylinder(pour_diameter/2, top-1, back+1, *pour)]
    ports += [cylinder(vent_diameter/2, top-1, back+1, *xy) for xy in vents]
    core = one(core.cut(*ports), 'core fill and vents')
    for angle, reach in ((0, flange_width/2), (90, flange_depth/2),
                         (180, flange_width/2), (270, flange_depth/2)):
        notch = box(pry_depth+1, pry_width, top-pry_height, top+1,
                    reach-pry_depth/2+0.5)
        cavity = cavity.cut(notch.rotate((0, 0, 0), (0, 0, 1), angle))
    cavity = one(cavity, 'cavity opening notches')
    # The core forms the bowl; one stock steel rod forms the straight outlet.
    cast = one(nominal_exterior.cut(nominal_plug.toNURBS(), rod.toNURBS()),
               'silicone casting')
    finished_funnel = nominal_exterior.cut(bore)
    assert cast.cut(finished_funnel).Volume() < tolerance
    assert finished_funnel.cut(cast).Volume() < tolerance

    print('Checking closure, release and passages', flush=True)
    containment = liquid_containment(cavity, core, rod, cast, floor, top, back,
                                     flange_width, neck, pour, vents, x, y, guide_top)
    assert cavity.intersect(core).Volume() < tolerance
    assert all(s.intersect(cast).Volume() < tolerance for s in (cavity, core))
    assert all(s.intersect(rod).Volume() < tolerance for s in (cavity, core))
    for lift in (0.5, 1.5, 3, 6, 12, rod_engagement, 52):
        assert cavity.intersect(core.translate((0, 0, lift))).Volume() < tolerance
    for withdrawal in (0, 0.5, 1, 2, 4, 8, rod_length):
        assert core.intersect(rod.translate((0, 0, -withdrawal))).Volume() < tolerance
    minimum_core_backing = dry_void.distance(cast) - finish_allowance
    for xy in bolt_xy:
        # M4 washers, 9 mm OD, sit directly on both flat flange backs.
        washer = cylinder(4.5, top-flange_thickness-1, top-flange_thickness, *xy)
        assert washer.intersect(cavity).Volume() < tolerance
    shift = (0, 0, -floor)
    parts = {name: shape.translate(shift) for name, shape in
             [('cavity', cavity), ('core', core), ('funnel', cast), ('rod', rod)]}
    info = {
        'dimensions_mm': {n: [s.BoundingBox().xlen, s.BoundingBox().ylen,
                              s.BoundingBox().zlen] for n, s in parts.items()},
        'volume_ml': {n: s.Volume()/1000 for n, s in parts.items()},
        'shell_thickness_mm': shell_thickness, 'flange_thickness_mm': flange_thickness,
        'minimum_cavity_backing_mm': minimum_backing,
        'backing_join_allowance_mm': forming_join_allowance,
        'minimum_core_backing_mm': minimum_core_backing,
        'liquid_containment': containment,
        'parting_z_mm': top-floor, 'finish_allowance_mm': finish_allowance,
        'casting_scope': 'whole finished funnel with rectangular block, flat bearing face and straight 6 mm outlet',
        'flange_plan_mm': [flange_width, flange_depth],
        'flange_margin_mm': flange_margin,
        'plug_blank_mm': [funnel.plug_width,
                          2*funnel.elbow_cradle.plug_half_length(funnel.plug_width/2)],
        'rod_support': {'engagement_mm': rod_guide_length-finish_allowance,
            'guide_diameter_mm': 2*guide_radius, 'dry_shank_diameter_mm': rod_diameter,
            'guide_diametral_clearance_mm': rod_clearance,
            'guide_length_mm': rod_guide_length-finish_allowance,
            'guide_top_mm': guide_top-floor,
            'guide_open': True,
            'rod_projection_above_guide_mm': rod_top-guide_top,
            'straight_dry_wall_mm': rod_seat_wall,
            'registration': 'open upper guide and lower blind floor seat',
            'retention': 'gravity; rod rests on lower floor and lifts out from the dry back',
            'air_path': 'open annular passage to dry back',
            'flash': 'trim guide overflow at bowl throat and lower-seat collar flush with block bottom'},
        'rod_socket': {'diameter_mm': rod_socket_diameter, 'depth_mm': rod_socket_depth,
            'rod_end_depth_mm': rod_end_depth, 'floor_backing_mm': shell_thickness,
            'reference': 'blind pilot seat below block bottom; bare floor establishes axial datum'},
        'rod': {'material': '304 stainless steel', 'diameter_mm': rod_diameter,
                'length_mm': rod_length, 'profile': 'straight stock cylinder',
                'supplier': 'uxcell 25-piece pack',
                'url': 'https://www.amazon.com/dp/B07Z18CKCY',
                'finishing': 'clean and apply release'},
        'funnel_to_mould_z_translation_mm': -floor,
        'finished_funnel_step_sha256': hashlib.sha256(
            (ROOT/'hardware/printed-parts/zone-c/funnel/funnel.step').read_bytes()).hexdigest(),
        'locators': {'diameter_mm': locator_diameter, 'height_mm': locator_height,
                     'radial_clearance_mm': locator_clearance, 'slot_travel_each_way_mm': locator_slot_travel,
                     'centres_xy_mm': locator_xy},
        'clamping': {'hole_diameter_mm': bolt_diameter, 'centres_xy_mm': bolt_xy,
                     'fastener': 'M4 x 20 with 9 mm OD washers and nuts; or small clamps on flange'},
        'ports': {'fill_diameter_mm': pour_diameter, 'vent_diameter_mm': vent_diameter,
                  'fill_xy_mm': pour, 'vent_xy_mm': vents},
        'print_bases': {'cavity_plan_mm': [base_width, base_depth],
            'cavity_corner_radius_mm': base_radius, 'base_thickness_mm': base_thickness,
            'corbel_run_per_rise': corbel_run_per_rise,
            'corbel_angle_from_bed_deg': math.degrees(math.atan(1/corbel_run_per_rise)),
            'corbel_print_z_mm': [base_thickness, corbel_top-floor],
            'bolt_access_pocket_width_mm': bolt_pocket_width,
            'bolt_access_pocket_height_mm': bolt_pocket_height,
            'core': 'flat dry back with one circular tapered access hole'},
        'dry_opening_mm': 2*dry_radius,
        'dry_opening_depth_mm': 2*dry_radius,
        'dry_opening_shape': 'circular conical access to straight rod guide',
        'postprint_breathers': breathers(base_width, back-floor),
        'ramp_print_z_mm': {'cavity': [neck-floor, m['ramp_top_z']-floor],
                            'core': [back-m['ramp_top_z'], back-neck]},
        'nominal_chamber_diameter_mm': chamber_diameter,
        'load_screen': load_screen(m, end),
        'status': 'Complete two-body tooling with flat print bases and straight stock steel rod; native geometry verified'}
    return parts, info


def breathers(base_width, core_back):
    return {'diameter_mm': 1.5,
        'cavity': {'entry_xyz_mm': [[-base_width/2, -30, 2.5], [base_width/2, 30, 2.5]],
            'drill_axes': [[1, 0, 0], [-1, 0, 0]], 'depth_mm': 3.2,
            'face': 'vertical sides of the flat base, clear of the catch tray'},
        'core': {'entry_xyz_mm': [[-40, -30, core_back], [40, 30, core_back]],
            'drill_axes': [[0, 0, -1], [0, 0, -1]], 'depth_mm': 1.8,
            'face': 'flat outer dry back'},
        'method': 'Drill through the printed skins into sparse infill after printing with a depth stop; keep dry faces and holes uncoated. CAD blind holes would receive sealed slicer walls.'}


def load_screen(m, bottom):
    span = m['w']
    pressure = 0.001  # N/mm² = 1 kPa, including head and a modest process allowance.
    head = m['top_z']+flange_thickness-bottom
    return {'model': 'silicone hydrostatic head and conservative uniform process-load screen',
            'span_mm': span, 'pressure_kpa': pressure*1000,
            'silicone_density_assumption_kg_m3': 1130,
            'maximum_silicone_head_mm': head, 'head_pressure_kpa': 1130*9.81*(head/1000)/1000,
            'pressure_force_n': pressure*span**2,
            'condition': 'complete mold inside chamber; fill, vents, rod guide and drilled dry-side infill breathers open to chamber air',
            'process': 'six walls, six top/bottom layers and 15% gyroid; slow evacuation and venting while silicone is fluid',
            'scope': 'Applied liquid load only. No stiffness, lifetime or pressure rating is inferred from infill percentage.'}


def write_parts(parts, info, output):
    """Export one tooling design and views of those same bodies."""
    output.mkdir(parents=True, exist_ok=True)
    colors = {'cavity': cq.Color('#3D9998'), 'core': cq.Color('#D8A751'),
              'funnel': cq.Color('#555C68'), 'rod': cq.Color('#AAB9C8')}
    assembly = cq.Assembly()
    radii = []
    for name, shape in parts.items():
        assembly.add(shape, name=name, color=colors[name])
        if name != 'seal':
            single = one_body(cq.Workplane(obj=shape), name, colors[name])
            # Fixed STEP uncertainty keeps the joined spline-face trims stable
            # for the print meshes and casting view.
            export_assembly(single, str(output/f'{name}.step'), precision_mode=1)
            saved = import_step(str(output/f'{name}.step')).val()
            info['volume_ml'][name] = saved.Volume()/1000
            if name == 'funnel':
                vertices, faces = saved.tessellate(0.005, 0.05)
                cast_mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices],
                                            faces=faces, process=True)
                cast_mesh.update_faces(cast_mesh.nondegenerate_faces())
                assert cast_mesh.is_watertight and cast_mesh.is_winding_consistent
        if name in ('cavity', 'core'):
            path = output/f'{name}.stl'
            # Tessellate the exported STEP's normalized face trims, so the print
            # mesh and the exact tooling file share the same closed boundaries.
            print_shape = import_step(str(output/f'{name}.step')).val()
            print_shape.exportStl(str(path), tolerance=0.02,
                angularTolerance=0.08, relative=False)
            mesh = trimesh.load(path, force='mesh', process=True)
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
            mesh.export(path)
            write_print_payload(output/f'{name}.step', path)
            radii.append(float(np.linalg.norm(mesh.vertices[:, :2], axis=1).max()))
    export_assembly(assembly, str(output/'assembly.step'), precision_mode=1)
    overview = cq.Assembly()
    spacing = (parts['cavity'].BoundingBox().xlen+parts['core'].BoundingBox().xlen)/4+22
    overview.add(parts['cavity'].translate((-spacing, 0, 0)), name='cavity', color=colors['cavity'])
    core = parts['core'].rotate((0, 0, 0), (1, 0, 0), 180)
    core = core.translate((spacing, 0, -core.BoundingBox().zmin))
    overview.add(core, name='core', color=colors['core'])
    export_assembly(overview, str(output/'overview.step'))
    section = cq.Assembly()
    section_slab = box(240, 2, -1, 120, y=funnel.neck_dy)
    for name, shape in parts.items():
        section.add(shape.intersect(section_slab), name=name, color=colors[name])
    export_assembly(section, str(output/'section.step'))
    info['enclosing_diameter_mm'] = 2*max(radii)
    info['chamber_radial_clearance_mm'] = chamber_diameter/2-max(radii)
    info['volume_measurement_scope'] = 'Numerical integration of the final native STEP solids; whole-shape equality is established by complete CSG, separately from spline volume integration.'
    assert info['chamber_radial_clearance_mm'] > 0
    info['native_shell_sha256'] = {f'{name}.{suffix}': hashlib.sha256(
        (output/f'{name}.{suffix}').read_bytes()).hexdigest()
        for name in ('cavity', 'core') for suffix in ('step', 'stl', 'step.mesh')}
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
