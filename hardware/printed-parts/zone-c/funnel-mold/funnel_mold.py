"""Vented PETG tooling for the Zone C silicone funnel.

Frame: XY at the funnel brim centre, +Z up when assembled. Both exported halves
share a transform that places the cavity's feet at Z=0. Print the cavity opening
up and the core inverted, its open back against the bed.

The nominal funnel defines the finished forming faces. The printed cavity is
expanded and the plug contracted by finish_allowance; finishing adds that net
thickness back. The registration lands and the steel rod socket stay nominal.
Skins carry the forming faces, ribs carry the skins, and transverse air channels
connect the open backs to the chamber even against a flat shelf or clamp board.
"""

import math
import os
import sys
from pathlib import Path

import cadquery as cq
import trimesh

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware/scripts/_cadq_export.py").is_file())
_tools = next(p for p in _here.parents if (p / "tools/docgen").is_dir()) / "tools"
sys.path[:0] = [str(_repo / "hardware/scripts"),
                str(_repo / "hardware/printed-parts/cadlib"), str(_tools),
                str(_repo / "hardware/printed-parts/zone-c/funnel")]
import fits
from _cadq_export import export_assembly
from _materials import M_PETG_BLACK, M_SILICONE_BLACK, M_STAINLESS, one_body
from flute_payload import cut as write_print_payload
from docgen import substitute_md
import funnel as HF

mold_wall = 8.0
mold_base = 10.0
skirt_wall = 6.0
plate_thk = 14.0
lip_h = 10.0
lip_gap = fits.slip
forming_skin = 3.2
rib_thk = 2.4
rib_pitch = 20.0
cross_rib_pitch = 64.0
foot_frame = 3.2
frame_height = 2.4
back_vent_d = 3.0
back_vent_depth = 3.0
register_corbel_run = 14.0
cavity_air_rows = (-80.0, -32.0, 32.0, 80.0)
core_air_rows = (-68.0, -32.0, 32.0, 68.0)
# Net surface growth: dry coating remaining minus substrate removed by sanding.
finish_allowance = 0.20
boolean_tol = 0.0001

tip_buffer = 12.0
# The annular shoulder at the nominal exit plane locates the trim blade.
tip_step = 1.0
tip_cap = 2.0
tip_draft = 0.5
rod_d = 6.35
rod_len = 50.8
rod_fit = 0.10
fill_port_land = 1.0
fill_dish_d = 20.0
fill_dish_h = 4.0
vent_id = 2.5

witness_w = 60.0
witness_d = 24.0
witness_floor = 10.0
witness_ramp_run = 20.0
witness_rail_w = 4.0
witness_rail_gap = 3.0

# One station repeats at 90 degrees around the four sides, inside the square
# mold's existing circumscribed circle (the chamber is round).
jack_x, jack_y = 119.0, 6.0
washer_y = 14.0
washer_od, washer_pocket_d = 25.0, 25.4
washer_thickness_range = (0.8, 2.0)
jack_length, jack_pitch, jack_hole = 50.0, 0.8, 5.8
nut_width, nut_thickness = 8.0, 4.0
nut_slot_width, nut_slot_height = 8.4, 4.4
guide_x = 119.0
guide_width, guide_depth = 12.0, 40.0
guide_bore, guide_bore_depth = guide_width+0.6, guide_depth+0.6
guide_drop, guide_top, guide_bottom = 54.0, 10.0, 24.0
guide_root_run = 6.0
extraction_stroke = 32.0
chamber_nominal_id = 11.8 * 25.4
column_radius = 16.0
station_root = 79.0
station_wall = 6.4
station_top_gap = 0.6
station_arm_root, station_arm_end = 87.0, 135.0
station_arm_width = 66.0
guide_relief = guide_bore + 4.0
guide_relief_depth = guide_bore_depth + 4.0
guide_outside = guide_bore + 2*station_wall
guide_outside_depth = guide_bore_depth + 2*station_wall
guide_y = -(guide_outside_depth+rib_thk)/2


def _box(w, d, z0, z1, cx=0.0, cy=0.0):
    return (cq.Workplane("XY").box(w, d, z1-z0, centered=(True, True, False))
            .translate((cx, cy, z0)).val())


def _cyl(r, z_top, z_bot, cx=0.0, cy=0.0):
    return cq.Solid.makeCylinder(r, z_top-z_bot, cq.Vector(cx, cy, z_bot), cq.Vector(0, 0, 1))


def _one(shape, name):
    shape = shape.clean()
    assert shape.isValid() and len(shape.Solids()) == 1, f"{name}: invalid or disconnected solid"
    return shape.Solids()[0]


def _quarter(shape, angle):
    return shape.rotate((0, 0, 0), (0, 0, 1), angle)


def _guide_post(z0, z1, x, y):
    post = cq.Workplane(obj=_box(guide_width, guide_depth, z0, z1, x, y))
    return post.edges('|Z').chamfer(0.6).faces('<Z').edges().chamfer(0.8).val()


def _guide_socket(z0, z1, x, y):
    bore = _box(guide_bore, guide_bore_depth, z0-1, z1+1, x, y)
    entry = (cq.Workplane('XY').workplane(offset=z1-0.6).center(x, y)
        .rect(guide_bore, guide_bore_depth).workplane(offset=0.61)
        .rect(guide_bore+1.22, guide_bore_depth+1.22).loft().val())
    return bore.fuse(entry)


def _nut_cut(top_z, x, y, exit_x):
    start = x-nut_slot_width/2
    return _box(exit_x-start, nut_slot_width, top_z+1.2,
        top_z+1.2+nut_slot_height, (start+exit_x)/2, y)


def build_extraction(top_z):
    """Bed-rooted bearing columns, braced guide towers and broad lifting arms."""
    pad_floor = top_z-3.0
    tie_top = top_z-lip_h-station_top_gap
    pad = _cyl(column_radius, pad_floor+1.2, 0, jack_x, washer_y)
    pad = pad.cut(_cyl(washer_pocket_d/2, top_z+1, pad_floor, jack_x, washer_y))
    sleeve = _box(guide_outside, guide_outside_depth, 0, top_z-guide_top, guide_x, guide_y)
    socket = _guide_socket(top_z-guide_bottom, top_z-guide_top, guide_x, guide_y)
    relief_top = top_z-guide_bottom-(guide_relief-guide_bore)/2
    relief = _box(guide_relief, guide_relief_depth, -1, relief_top, guide_x, guide_y)
    relief = relief.fuse(cq.Workplane('XY').workplane(offset=relief_top)
        .center(guide_x, guide_y).rect(guide_relief, guide_relief_depth)
        .workplane(offset=(guide_relief-guide_bore)/2)
        .rect(guide_bore, guide_bore_depth).loft().val())
    sleeve = sleeve.cut(socket, relief)
    walls = []
    pad_wall_spread = 2*(washer_y-rib_thk/2-station_wall/2)
    for x, y, spread in [(jack_x, washer_y, pad_wall_spread),
                          (guide_x, guide_y, guide_outside_depth-station_wall)]:
        walls.extend(_box(x-station_root, station_wall, 0, tie_top,
                     (station_root+x)/2, y+s*spread/2) for s in (-1, 1))
    lower = pad.fuse(sleeve, *walls)
    guide_air = cq.Solid.makeCylinder(back_vent_d/2, guide_outside,
        cq.Vector(guide_x, guide_y, back_vent_depth), cq.Vector(1, 0, 0))
    lower = lower.cut(guide_air, socket, relief)
    guide_arm_end = guide_x+guide_width/2+guide_root_run
    guide_arm_low = guide_y-guide_depth/2-guide_root_run
    arm_low, arm_high = -station_arm_width/2, station_arm_width/2
    corner_run = station_arm_end-guide_arm_end
    arm_plan = [(station_arm_root, guide_arm_low), (guide_arm_end, guide_arm_low),
                (guide_arm_end, arm_low-corner_run), (station_arm_end, arm_low),
                (station_arm_end, arm_high), (station_arm_root, arm_high),
                (station_arm_root, guide_arm_low)]
    arm = (cq.Workplane('XY').workplane(offset=top_z)
           .polyline(arm_plan).wire().extrude(plate_thk).val())
    post = _guide_post(top_z-guide_drop, top_z+plate_thk, guide_x, guide_y)
    shoulder = (cq.Workplane('XY').workplane(offset=top_z-guide_root_run)
        .center(guide_x, guide_y).rect(guide_width, guide_depth)
        .workplane(offset=guide_root_run)
        .rect(guide_width+2*guide_root_run, guide_depth+2*guide_root_run).loft().val())
    # The mark meets the sleeve mouth after 32 mm of lift; it is a witness mark,
    # not a catch that would prevent removing the core after the rod is clear.
    mark_z = top_z-guide_top-extraction_stroke
    post = post.cut(_box(0.4, 5.0, mark_z-0.4, mark_z+0.4,
                        guide_x+guide_width/2-0.15, guide_y))
    upper = arm.fuse(post, shoulder)
    upper = upper.cut(_cyl(jack_hole/2, top_z+plate_thk+1, top_z-1, jack_x, jack_y),
                      _nut_cut(top_z, jack_x, jack_y, station_arm_end+1))
    upper = _one(upper, 'extraction upper station')
    # Pads/sleeves, threads and sliding faces use the precision surface speed.
    slow_lower = _cyl(column_radius+0.5, top_z, pad_floor-forming_skin, jack_x, washer_y).fuse(
        _box(guide_outside+1, guide_outside_depth+1, top_z-guide_bottom,
             top_z-guide_top, guide_x, guide_y))
    slow_upper = arm.fuse(post, shoulder)
    lower_stations = [_quarter(lower, a) for a in range(0, 360, 90)]
    lower_all = cq.Compound.makeCompound(lower_stations)
    upper_all = cq.Compound.makeCompound([_quarter(upper, a) for a in range(0, 360, 90)])
    lower_slow = cq.Compound.makeCompound([_quarter(slow_lower, a) for a in range(0, 360, 90)])
    upper_slow = cq.Compound.makeCompound([_quarter(slow_upper, a) for a in range(0, 360, 90)])
    hardware = []
    for a in range(0, 360, 90):
        washer = _cyl(washer_od/2, pad_floor+1.0, pad_floor, jack_x, washer_y).cut(
            _cyl(2.7, pad_floor+2.0, pad_floor-1, jack_x, washer_y))
        # Smooth shaft/head representations; the purchased steel supplies threads.
        tip_z = pad_floor+1.0
        screw = _cyl(2.5, tip_z+jack_length, tip_z, jack_x, jack_y).fuse(
            _cyl(4.25, tip_z+jack_length+5, tip_z+jack_length, jack_x, jack_y))
        nut = _box(nut_width, nut_width, top_z+1.6, top_z+5.6, jack_x, jack_y).cut(
            _cyl(2.5, top_z+6, top_z+1, jack_x, jack_y))
        hardware.extend([(f'washer-{a//90+1}', _quarter(washer, a)),
                         (f'jack-screw-{a//90+1}', _quarter(screw, a)),
                         (f'square-nut-{a//90+1}', _quarter(nut, a))])
    return lower_all, upper_all, lower_slow, upper_slow, hardware


def build_hardware_witness():
    """Nut seat in the inverted core's print orientation, sleeve and washer seat."""
    nut_block = _box(34, 20, 0, plate_thk, -1, 0)
    nut_cut = _nut_cut(0, 0, 0, 17).rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, plate_thk))
    nut_block = nut_block.cut(nut_cut, _cyl(jack_hole/2, plate_thk+1, -1))
    sleeve = _box(guide_outside, guide_outside_depth, 0, 14, -26, 0).cut(
        _guide_socket(0, 14, -26, 0))
    pad = _cyl(column_radius, 4.4, 0, 0, 25).cut(_cyl(washer_pocket_d/2, 5, 3.2, 0, 25))
    coupon = _one(nut_block.fuse(sleeve, pad), 'hardware witness')
    pin = _guide_post(-24, 0, 0, 0).fuse(_box(guide_width+6, guide_depth+6, 0, 3))
    pin = pin.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, 3))
    return coupon, _one(pin, 'guide witness')


def _expanded(shape, distance):
    """Normal face offsets, with round joins at edges and vertices.

    Each face keeps its analytic/offset surface. Edge tubes and vertex spheres
    close the corner wedges between outward-offset faces.
    """
    parts = [f.thicken(distance) for f in shape.Faces()]
    for edge in shape.Edges():
        if edge.Length() > boolean_tol:
            circle = cq.Wire.makeCircle(distance, edge.positionAt(0), edge.tangentAt(0))
            parts.append(cq.Solid.sweep(circle, [], edge))
    parts.extend(cq.Solid.makeSphere(distance, v.Center(), angleDegrees1=-90,
                                     angleDegrees2=90) for v in shape.Vertices())
    return _one(shape.fuse(*parts, tol=boolean_tol), "expanded forming envelope")


def _contracted_plug(plug, distance, top_z):
    # The top face remains open into the back of the core plate.
    strips = [f.thicken(-distance) for f in plug.Faces() if f.Center().z < top_z]
    return _one(plug.cut(*strips, tol=boolean_tol), "contracted plug")


def _ribs(w, d, z0, z1, cx, cy):
    count = math.floor((w / 2 - foot_frame) / rib_pitch)
    ribs = [_box(rib_thk, d, z0, z1, cx+i*rib_pitch, cy) for i in range(-count, count+1)]
    ribs.extend(_box(w, rib_thk, z0, z1, cx, cy+y)
                for y in (-cross_rib_pitch, 0, cross_rib_pitch))
    return ribs[0].fuse(*ribs[1:], tol=boolean_tol)


def _air_channels(width, rows, z, cx, cy):
    return [cq.Solid.makeCylinder(back_vent_d/2, width+2,
            cq.Vector(cx-width/2-1, cy+y, z), cq.Vector(1, 0, 0)) for y in rows]


def build_witness():
    """One flat, one 15-degree ramp, and a vertical face for finishing trials.

    The two separate end rails remain uncoated. The central flat starts one
    allowance below their top; a straightedge across the rails reads the net
    growth. The ramp tests terrace removal and silicone release at the floor grade.
    """
    floor = _box(witness_w, witness_d, 0, witness_floor)
    rail_top = witness_floor + finish_allowance
    for x in (-witness_w/2+witness_rail_w/2, witness_w/2-witness_rail_w/2):
        floor = floor.fuse(_box(witness_rail_w, witness_d, witness_floor, rail_top, x))
    x0 = witness_w/2-witness_rail_w-witness_rail_gap-witness_ramp_run
    x1 = x0+witness_ramp_run
    rise = witness_ramp_run*math.tan(math.radians(HF.ramp_angle))
    ramp_wire = cq.Wire.makePolygon([cq.Vector(x0, -witness_d/2, witness_floor),
        cq.Vector(x1, -witness_d/2, witness_floor),
        cq.Vector(x1, -witness_d/2, witness_floor+rise),
        cq.Vector(x0, -witness_d/2, witness_floor)])
    ramp = cq.Solid.extrudeLinear(ramp_wire, [], cq.Vector(0, witness_d, 0))
    # Ramp occupies the rear half so the front half remains a flat measuring strip.
    ramp = ramp.intersect(_box(witness_w, witness_d/2, 0, witness_floor+rise+1, 0, witness_d/4))
    window = _box(rib_pitch-rib_thk, witness_d+2, -1, witness_floor-forming_skin, -14.0)
    return _one(floor.fuse(ramp).cut(window), "finish witness")


def build():
    exterior, bore, m = HF.build_solids()
    ncx, ncy, ocx, ocy = m['ncx'], m['ncy'], m['out_cx'], m['out_cy']
    top_z, end_z, neck_z = m['top_z'], m['end_z'], m['neck_z']
    out_w, out_d = m['out_w'], m['out_d']
    block_w, block_d = out_w+2*mold_wall, out_d+2*mold_wall
    plate_w, plate_d = block_w+2*skirt_wall, block_d+2*skirt_wall
    buf_z = end_z-tip_buffer
    floor_z = buf_z-mold_base
    buf_r = m['spout_or']-tip_step
    tip = cq.Solid.makeCone(buf_r-tip_draft, buf_r, tip_buffer,
                           cq.Vector(ncx, ncy, buf_z), cq.Vector(0, 0, 1))
    nominal_envelope = _one(exterior.fuse(tip), 'nominal exterior')
    forming_void = _expanded(nominal_envelope, finish_allowance)
    backing = _expanded(nominal_envelope, finish_allowance+forming_skin)
    cavity_blank = _box(block_w, block_d, floor_z, top_z, ocx, ocy)
    top_register = _box(block_w, block_d, top_z-lip_h, top_z, ocx, ocy)
    # The broad registration band grows out from the collar on a 45-degree
    # corbel; its underside must not start with an unsupported outward step.
    register_corbel = (cq.Workplane('XY').workplane(offset=top_z-lip_h-register_corbel_run)
        .center(ocx, ocy).rect(block_w-2*register_corbel_run, block_d-2*register_corbel_run)
        .workplane(offset=register_corbel_run).rect(block_w, block_d).loft().val())
    foot = _box(block_w, block_d, floor_z, floor_z+frame_height, ocx, ocy).cut(
        _box(block_w-2*foot_frame, block_d-2*foot_frame,
             floor_z-1, floor_z+frame_height+1, ocx, ocy))
    ribs = _ribs(block_w, block_d, floor_z, top_z, ocx, ocy)
    # Carry the blind spout floor directly to the bed; its rounded backing must
    # not begin as a cantilever between the ribs.
    tip_pedestal = _cyl(m['spout_or']+finish_allowance+forming_skin,
                        neck_z, floor_z, ncx, ncy)
    cavity = backing.fuse(top_register, register_corbel, foot, ribs, tip_pedestal,
                          tol=boolean_tol).intersect(cavity_blank)
    cavity = cavity.cut(forming_void)
    cavity_air = _air_channels(block_w, cavity_air_rows, floor_z+back_vent_depth, ocx, ocy)
    cavity = _one(cavity.cut(*cavity_air), 'cavity')

    rod_below = HF.spout_tube+tip_buffer-tip_cap
    rod_socket = rod_len-rod_below
    rod_bot, rod_top = buf_z+tip_cap, neck_z+rod_socket
    assert 0 < rod_socket and rod_top < top_z-forming_skin
    rod = _cyl(rod_d/2, rod_top, rod_bot, ncx, ncy)
    nominal_plug = _one(bore.intersect(_box(plate_w, plate_d, neck_z,
                                          top_z+1, ocx, ocy)), 'nominal plug')
    plug = _contracted_plug(nominal_plug, finish_allowance, top_z)
    interior = _contracted_plug(nominal_plug, finish_allowance+forming_skin, top_z)
    core_skin = plug.cut(interior)
    chimney = _box(m['bore_w']-2*(finish_allowance+forming_skin),
                   m['bore_d']-2*(finish_allowance+forming_skin),
                   top_z, top_z+plate_thk+1, ocx, ocy)
    interior = interior.fuse(chimney)
    socket_r = (rod_d+rod_fit)/2
    socket_back = _cyl(socket_r+forming_skin, rod_top+forming_skin, neck_z, ncx, ncy)
    interior = interior.cut(socket_back)
    core_ribs = _ribs(plate_w, plate_d, neck_z, top_z+plate_thk, ocx, ocy)
    interior = interior.cut(core_ribs)
    plate = _box(plate_w, plate_d, top_z, top_z+plate_thk, ocx, ocy)
    # A pocket in the brim-forming underside reserves the same finishing growth.
    plate = plate.cut(_box(out_w+2*finish_allowance, out_d+2*finish_allowance,
                           top_z-1, top_z+finish_allowance, ocx, ocy))
    skirt = _box(plate_w, plate_d, top_z-lip_h, top_z, ocx, ocy).cut(
        _box(block_w+2*lip_gap, block_d+2*lip_gap, top_z-lip_h-1, top_z, ocx, ocy))
    core = plug.fuse(plate, skirt).cut(interior)
    core = core.cut(_cyl(socket_r, rod_top, neck_z-1, ncx, ncy))
    fill_d = m['rim_ring']-2*fill_port_land
    rx, ry = out_w/2-m['rim_ring']/2, out_d/2-m['rim_ring']/2
    fill_xy = (ocx-rx, ocy-ry)
    vents = [(ocx+rx, ocy-ry), (ocx-rx, ocy+ry), (ocx+rx, ocy+ry),
             (ocx-rx, ocy), (ocx+rx, ocy)]
    ports = [_cyl(fill_d/2, top_z+plate_thk+1, top_z-1, *fill_xy),
             cq.Solid.makeCone(fill_d/2, fill_dish_d/2, fill_dish_h,
                cq.Vector(*fill_xy, top_z+plate_thk-fill_dish_h), cq.Vector(0, 0, 1))]
    ports.extend(_cyl(vent_id/2, top_z+plate_thk+1, top_z-1, *xy) for xy in vents)
    core_air = _air_channels(plate_w, core_air_rows,
                            top_z+plate_thk-back_vent_depth, ocx, ocy)
    core = _one(core.cut(*ports, *core_air), 'core')

    assert cavity.intersect(core).Volume() < 0.001, 'registration interference'
    for channel in cavity_air:
        assert channel.intersect(forming_void).Volume() < 0.001, 'air channel reaches cavity'
    for channel in core_air:
        assert sum(channel.intersect(port).Volume() for port in ports) < 0.001, 'air channel reaches pour/vent port'
    assert interior.intersect(rod).Volume() < 0.001, 'open back reaches rod socket'
    funnel = HF.build()[0].val()
    cast = funnel.fuse(tip.cut(rod))
    shift = (-ocx, -ocy, -floor_z)
    # Modifier volumes overlap only modeled material. They retain the careful
    # surface speed while the exposed reinforcing ribs use the bulk-wall speed.
    cavity_slow = backing.fuse(top_register).intersect(cavity_blank)
    core_slow = core_skin.fuse(skirt, socket_back,
        _box(plate_w, plate_d, top_z, top_z+finish_allowance+forming_skin, ocx, ocy))
    cavity, core = cavity.translate(shift), core.translate(shift)
    assembly_top = top_z-floor_z
    lower, upper, lower_slow, upper_slow, hardware = build_extraction(assembly_top)
    lower = lower.cut(forming_void.translate(shift), *(c.translate(shift) for c in cavity_air))
    cavity = _one(cavity.fuse(*lower.Solids()), 'cavity with jacks')
    core = _one(core.fuse(*upper.Solids()), 'core with jacks')
    cavity_slow = cavity_slow.translate(shift).fuse(*lower_slow.Solids())
    core_slow = core_slow.translate(shift).fuse(*upper_slow.Solids())
    assert cavity.intersect(core).Volume() < 0.001, 'extraction fixtures interfere at closure'
    # A rectangular swept envelope contains each chamfered post at every point
    # from seated through complete withdrawal. Its clearance is continuous.
    for a in range(0, 360, 90):
        swept_post = _quarter(_box(guide_width, guide_depth, assembly_top-guide_drop,
            assembly_top+guide_drop+plate_thk, guide_x, guide_y), a)
        assert cavity.intersect(swept_post).Volume() < 0.001, 'guide sweep blocked'
    assert guide_drop-extraction_stroke-guide_top >= 12.0, 'insufficient guide engagement'
    assert extraction_stroke > rod_socket, 'rod still engaged at working stroke'
    for washer_t in washer_thickness_range:
        tip_z = assembly_top-3.0+washer_t
        assert tip_z < assembly_top+1.2, 'screw misses full nut thickness'
        assert tip_z+jack_length-(assembly_top+plate_thk+extraction_stroke) >= 1.5, 'head bottoms before release'
    info = {
        'cast': cast.translate(shift), 'rod': rod.translate(shift),
        'rod_len': rod_len, 'rod_below': rod_below, 'rod_socket': rod_socket,
        'sil_vol': cast.Volume(), 'part_vol': funnel.Volume(), 'tip_vol': tip.cut(rod).Volume(),
        'fill_d': fill_d, 'fill_xy': fill_xy, 'sil_wall': m['collar_wall'],
        'spout_id': m['spout_id'], 'cavity_bb': cavity.BoundingBox(),
        'core_bb': core.BoundingBox(), 'n_vents': len(vents),
        'cavity_volume': cavity.Volume(), 'core_volume': core.Volume(),
        'cavity_air_z': back_vent_depth, 'core_air_z': top_z+plate_thk-back_vent_depth-floor_z,
        'forming_void': forming_void.translate(shift),
        'cavity_slow': cavity_slow, 'core_slow': core_slow,
        'assembly_top': assembly_top, 'hardware': hardware,
    }
    return cavity, core, info


def main():
    cavity, core, info = build()
    here = _here.parent
    hardware_witness, guide_witness = build_hardware_witness()
    for name, shape in [('cavity', cavity), ('core', core), ('finish-witness', build_witness()),
                        ('hardware-witness', hardware_witness), ('guide-witness', guide_witness)]:
        stem = f'funnel-mold-{name}'
        export_assembly(one_body(cq.Workplane(obj=shape), stem, M_PETG_BLACK),
                        str(here / f'{stem}.step'))
        cq.exporters.export(shape, str(here / f'{stem}.stl'), tolerance=0.02, angularTolerance=0.08)
        mesh = trimesh.load(here / f'{stem}.stl', force='mesh', process=True)
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.remove_unreferenced_vertices()
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
        mesh.export(here / f'{stem}.stl')
        if not os.environ.get('HSM_SKIP_MESH_PAYLOAD'):
            write_print_payload(here / f'{stem}.step', here / f'{stem}.stl')
        print(f'-> {stem}.step / .stl ({shape.Volume()/1000:.2f} mL PETG)', flush=True)
    for name in ('cavity', 'core'):
        cq.exporters.export(info[f'{name}_slow'],
            str(here / f'funnel-mold-{name}-surface-zone.stl'),
            tolerance=0.02, angularTolerance=0.08)
    assy = cq.Assembly()
    assy.add(cavity, name='cavity', color=M_PETG_BLACK)
    assy.add(info['cast'], name='funnel', color=M_SILICONE_BLACK)
    assy.add(core, name='core', color=M_PETG_BLACK)
    assy.add(info['rod'], name='rod', color=M_STAINLESS)
    for name, shape in info['hardware']:
        assy.add(shape, name=name, color=M_STAINLESS)
    export_assembly(assy, str(here / 'funnel-mold-assembly.step'))
    cbb, kbb = info['cavity_bb'], info['core_bb']
    print(f"cavity {info['cavity_volume']/1000:.2f} mL; core {info['core_volume']/1000:.2f} mL PETG", flush=True)
    print(f"nominal cast {info['sil_vol']/1000:.2f} mL; net finishing growth {finish_allowance:.2f} mm", flush=True)
    substitute_md(here / 'README.md', variables={
        'MOLD_WALL': f'{mold_wall:g} mm', 'MOLD_BASE': f'{mold_base:g} mm',
        'PLATE_THK': f'{plate_thk:g} mm', 'SIL_WALL': f"{info['sil_wall']:g} mm",
        'SPOUT_BORE': f"{info['spout_id']:g} mm", 'SIL_VOLUME': f"{info['sil_vol']/1000:.0f} mL",
        'TIP_BUFFER': f'{tip_buffer:g} mm', 'ROD_D': f'{rod_d:g} mm', 'ROD_LEN': f'{rod_len:g} mm',
        'ROD_SOCKET': f"{info['rod_socket']:.1f} mm", 'ROD_BELOW': f"{info['rod_below']:.1f} mm",
        'ROD_FIT': f'{rod_fit:g} mm', 'ROD_SOCKET_D': f'{rod_d+rod_fit:g} mm',
        'TIP_CAP': f'{tip_cap:g} mm', 'LIP_H': f'{lip_h:g} mm',
        'BRIM_SQ': f"{info['cast'].BoundingBox().xlen:.0f} mm", 'TIP_STEP': f'{tip_step:g} mm',
        'CAVITY_DIMS': f'{cbb.xlen:.1f} × {cbb.ylen:.1f} × {cbb.zlen:.1f} mm',
        'CORE_DIMS': f'{kbb.xlen:.1f} × {kbb.ylen:.1f} × {kbb.zlen:.1f} mm',
        'FILL_D': f"{info['fill_d']:g} mm", 'FILL_DISH': f'{fill_dish_d:g} mm',
        'FILL_LAND': f'{fill_port_land:g} mm', 'MOLD_VENT_D': f'{vent_id:g} mm',
        'N_VENTS': str(info['n_vents']), 'FORMING_SKIN': f'{forming_skin:g} mm',
        'RIB_THK': f'{rib_thk:g} mm', 'RIB_PITCH': f'{rib_pitch:g} mm',
        'BACK_VENT_D': f'{back_vent_d:g} mm', 'FINISH_ALLOWANCE': f'{finish_allowance:.2f} mm',
    })


if __name__ == '__main__':
    main()
