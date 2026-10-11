"""Read-only native enclosure feature bundles for the sectional reference blockout.

No producer main/export function is called.  Layout belongs to the caller.  A
bundle is additive stock and subtractive rooms in one source-aligned local frame;
it is intended to become part of a broad wall, floor or ceiling, not a loose tile.
`parts` are genuinely separate production moving/mating pieces.  Mating planes,
working spans, bores and source print directions are retained.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import cadquery as cq

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'hardware/scripts').is_dir())
ENC = ROOT / 'hardware/printed-parts/enclosure/enclosure'
PP = ROOT / 'hardware/printed-parts'


def box(bounds):
    x0, x1, y0, y1, z0, z1 = bounds
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]


def compound(shapes):
    shapes = [s for s in shapes if s is not None and s.Volume() > 1e-8]
    return cq.Compound.makeCompound(shapes) if shapes else None


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(None)
def source():
    sys.path.insert(0, str(ENC))
    # The exact geometry API; importing has no producer/export side effects.
    enclosure = _load(ENC / 'enclosure.py', 'pour_enclosure_native_source')
    import _box_spec
    b, _ = _box_spec.read(enclosure.Box, enclosure.Bound,
                          (enclosure.Pack, enclosure.PortField, enclosure.Nameplate))
    return enclosure, b


@lru_cache(None)
def step(name):
    return cq.importers.importStep(str(ENC / (name + '.step'))).val()


@lru_cache(None)
def provenance(path, function=None):
    path = Path(path)
    text = path.read_text() if path.suffix == '.py' else ''
    result = {'path': str(path.relative_to(ROOT)),
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if function:
        nodes = [n for n in ast.walk(ast.parse(text))
                 if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == function]
        if len(nodes) != 1:
            raise ValueError((str(path), function, len(nodes)))
        result.update(function=function, line=nodes[0].lineno)
    return result


@dataclass
class Feature:
    name: str
    entries: tuple[str, ...]
    add: dict = field(default_factory=dict)
    cut: dict = field(default_factory=dict)
    post_add: dict = field(default_factory=dict)
    parts: dict = field(default_factory=dict)
    source_origin_mm: tuple = (0., 0., 0.)
    source_print_up: tuple = (0., 0., 1.)
    part_print_up: dict = field(default_factory=dict)
    backing: dict = field(default_factory=dict)
    mates: tuple = ()
    group: str = ''
    notes: tuple = ()
    sources: tuple = ()
    bearing: dict = field(default_factory=dict)

    def apply(self, host):
        """Add stock, cut the whole host, then restore retained catches."""
        host = host.val() if isinstance(host, cq.Workplane) else host
        for shape in self.add.values():
            host = host.fuse(shape)
        for shape in self.cut.values():
            host = host.cut(shape)
        for shape in self.post_add.values():
            host = host.fuse(shape)
        return host.clean()

    def placed(self, at=(0., 0., 0.)):
        """Translate source-aligned local geometry; retain the native build axis."""
        from dataclasses import replace
        return replace(self, **{k: {n: s.translate(at) for n, s in getattr(self, k).items()}
                                for k in ('add', 'cut', 'post_add', 'parts')})

    def report(self):
        result = {k: v for k, v in self.__dict__.items()
                  if k not in ('add', 'cut', 'post_add', 'parts')}
        for k in ('add', 'cut', 'post_add', 'parts'):
            result[k] = {n: {'bounds_mm': bounds(s), 'volume_mm3': s.Volume(),
                            'solids': len(s.Solids()), 'valid': s.isValid()}
                         for n, s in getattr(self, k).items()}
        return result


def _feature(name, entries, *, origin=(0., 0., 0.), add=None, cut=None,
             post_add=None, parts=None, functions=(), files=(), **metadata):
    move = tuple(-float(v) for v in origin)
    shaped = {k: {n: s.translate(move) for n, s in (v or {}).items()
                  if s is not None and s.Volume() > 1e-8}
              for k, v in (('add', add), ('cut', cut), ('post_add', post_add), ('parts', parts))}
    return Feature(name, tuple(entries), **shaped, source_origin_mm=tuple(origin),
                   sources=tuple([provenance(ENC / 'enclosure.py', fn) for fn in functions]
                                 + [provenance(path) for path in files]), **metadata)


def _derive(builder, clip_bounds):
    """Recover source additions and rooms from the source's mutating solid API.

    A distant seed leaves only the source-added stock.  A solid clip containing
    that stock reveals rooms cut by the same API.  Both are kept, so fusing the
    feature into a larger wall cannot refill its aperture or tie channel.
    """
    remote = box((10000., 10001., 10000., 10001., 10000., 10001.))
    added = builder(remote).cut(remote).clean()
    clip = box(clip_bounds)
    removed = clip.cut(builder(clip)).clean()
    return ({'native_stock': added} if added.Volume() > 1e-8 else {},
            {'native_rooms': removed} if removed.Volume() > 1e-8 else {})


def m5_floor_post():
    e, b = source(); st = b.pack.floor_bosses[0]
    sx, sy, tip, dia = st
    clip = (sx-9, sx+9, sy-9, sy+9, b.inner[4]-6, tip+1)
    add, cut = _derive(lambda s: e._floor_bosses(s, b.inner, (st,), -1000, 1000,
                                               b.inner[4], b.inner[5]), clip)
    return _feature('compressor_M5_post', ('E23', 'E58'), origin=(sx, sy, b.inner[4]),
                    add=add, cut=cut, functions=('_floor_bosses',),
                    backing={'floor_mm': 6., 'post_od_mm': dia,
                             'pilot_diameter_mm': e.floor_heatset_dia,
                             'insert_body_mm': e.floor_heatset_depth,
                             'root_plane_local_z_mm': 0.},
                    mates=('ruthex RX-M5x9.5', 'compressor rubber grommet, washer and M5 screw'),
                    group='floor / refrigeration feet',
                    notes=('One of four repeated compressor mounts; retain the grommet seating height.',
                           '100% infill is a native print region, not represented by this solid.'))


def m3_wall_mount(index=14):
    e, b = source(); st = b.pack.east_bosses[index]
    roots = e.piece_root_faces(b.inner, 'back', 'top')
    sy, sz, tip = st[:3]
    selected = [f for f in b.pack.east_mount_fills
                if any(abs(sy-y) < 1e-6 and abs(sz-z) < 1e-6 for y,z in f[2])]
    # Preserve complete native fill groups.  A two-hole mounting bar is one mate.
    sites = {(y,z) for f in selected for y,z in f[2]}
    stations = tuple(s for s in b.pack.east_bosses if (s[0], s[1]) in sites) or (st,)
    clip = (tip-2, b.outer[1]+2, sy-35, sy+35, sz-45, sz+45)
    add, cut = _derive(lambda s: e._east_bosses(s, roots, b.outer, stations, selected,
                                               -1000,1000,-1000,1000,up=-1.), clip)
    return _feature('electronics_M3_mount', ('E23', 'E26') if selected else ('E23','E25'),
                    origin=(roots[1], sy, sz), add=add, cut=cut,
                    functions=('_east_bosses', '_east_boss_stem', '_east_boss_corbel'),
                    source_print_up=(0.,0.,-1.),
                    backing={'root_face_local_x_mm': 0., 'wall_mm': e.back_top_flank_t,
                             'pilot_diameter_mm': e.heatset_dia,
                             'native_insert_setback_mm': e.east_boss_insert_setback(st),
                             'station': st, 'fills': selected},
                    mates=('identified PCB / relay mounting datum', 'M3 insert and screw'),
                    group='east electronics wall',
                    notes=('Do not collapse a ceiling-column variant into a corbel or transfer its physical load claim.',
                           'Print-down is +world Z because back-top prints ceiling-down.'))


def pogo_seat(into=1., up=1.):
    e, _ = source()
    seat, bores = e._pogo_seat(0., into, 0., 0., up)
    return _feature('pogo_male' if into > 0 else 'pogo_female', ('E23','E28','E43'),
                    cut={'stadium': seat, **{f'M1_4_pilot_{i}': s for i,s in enumerate(bores)}},
                    functions=('_pogo_seat',), source_print_up=(0.,0.,up),
                    backing={'pilot_diameter_mm': e.pogo_heatset_dia,
                             'insert_body_mm': e.pogo_heatset_len,
                             'insert_setback_mm': e.pogo_heatset_setback,
                             'roof_skin_mm': e.pogo_crown_skin,
                             'bearing_face_local_y_mm': 0., 'into_y': into},
                    mates=('YYFKGCP four-pin male/female stadium contact pair', 'two M1.4 inserts per half'),
                    group='fixed bay rear wall / removable pump cap rear wall',
                    notes=('Keep both contact halves on the same X/Z datum and their native lead exits.',
                           'A bare stadium without the recessed insert rooms is incomplete.'))


def pogo_leads(which='fixed'):
    e, b = source(); x,z = e.pump_contact_station(b)
    face = e.bay_back_y(b.pack.collet_plate) if which == 'fixed' else e.pump_cartridge_aft_y(
        b.pack.pump_trays,b.pack.collet_plate)
    f = e._pump_contact_fixed_cuts if which == 'fixed' else e._pump_contact_cap_cuts
    cutters = f(b)
    return _feature('pogo_'+which+'_rooms_and_leads', ('E23','E24','E28','E43'),
                    origin=(x,face,z), cut={f'room_{i}':s for i,s in enumerate(cutters)},
                    functions=(f.__name__,), source_print_up=(0,0,1 if which=='fixed' else -1),
                    group='pump drawer docking faces',
                    backing={'native_station_xz_mm': (x,z), 'bearing_face_local_y_mm':0.},
                    mates=('matching other contact half',),
                    notes=('Cap lead grooves retain both source pump terminal destinations; use only the chosen destination in a one-pump drawer.',))


def magnet_pocket(into=1.):
    e, _ = source(); r = e._retention
    shape = r.pocket((0.,0.),0.,into)
    d = r.dimensions((0.,0.),0.,into)
    return _feature('RC62_'+('fixed' if into>0 else 'drawer'), ('E42',),
                    cut={'D_magnet_room':shape}, files=(ENC/'_cartridge_retention.py',),
                    backing={'cover_mm':r.FACE_COVER, 'rear_mm':r.BACKING,
                             'radial_mm':r.BACKING,'source_dimensions':d},
                    mates=('one RC62 ring magnet', 'matching opposite magnet pocket'),
                    group='two pump drawer docking faces',
                    notes=('Two physical magnets are a true production mate, not a repeated comparison.',
                           'The sealed cover needs its source insertion/pause workflow; force and life remain unmeasured.'))


def c14_tunnel():
    e,b=source(); cx,cz,wx,wz,r=e._c14_aperture(b.pack.c14,b.pack.back_ports)
    stock, room, inserts = e._c14_tunnel_geometry(b.inner,b.outer,b.pack.c14,
                                                 b.pack.back_ports,-1000,1000,up=-1.)
    return _feature('C14_tunnel', ('E23','E28','E49'), origin=(cx,b.outer[3],cz),
                    add={'native_tunnel':stock}, cut={'cord_and_flange_room':room,
                    **{f'M3_pilot_{i}':s for i,s in enumerate(inserts)}},
                    functions=('_c14_tunnel_geometry',), source_print_up=(0,0,-1),
                    backing={'rear_wall_mm':e.socket_cap,'root_face_local_y_mm':-e.socket_cap,
                             'pocket_depth_mm':e.c14_pocket_depth,
                             'aperture_mm':(wx,wz,r)},
                    mates=('C14 purchased inlet with dog-bone flange', 'two M3 inserts and screws', 'IEC cord'),
                    group='rear service wall with ceiling root',
                    notes=('Keep its complete two-ear pocket and straight inboard insertion path.',
                           'The source aperture bridge is part of the actual cord tunnel.'))


def keystone_receptacle():
    e,b=source(); x,z=b.pack.keystone
    stock,room,catches=e._keystone_receptacle_geometry(b.inner,b.outer,(x,z),-1000,1000,up=-1.)
    return _feature('RJ11_receptacle', ('E25','E48'), origin=(x,b.outer[3],z),
                    add={'receiver_stock':stock}, cut={'module_and_swing_room':room},
                    post_add={'two_retaining_catches':catches},
                    functions=('_keystone_receptacle_geometry','_keystone_pocket_cut'),
                    source_print_up=(0,0,-1),
                    backing={'nominal_surround_mm':e._keystone.RECEPTACLE_WALL,
                             'DATA_pocket_depth_mm':e._data_fit.POCKET_DEPTH},
                    mates=('RiteAV RJ11 keystone body, tang and latch', 'complete DATA flat-wing label'),
                    group='rear DATA service wall',
                    notes=('Cut module room before restoring catches; otherwise the cut deletes the catches.',
                           'Retain 50-degree swing ease and both catches.'))


def wago_well(index=0):
    e,b=source(); st=b.pack.side_wells[index]; side,sy,sz,size=st[:4]
    up=-1. if sy>b.y_joint and sz>b.splits[1] else 1.
    clip=(b.outer[0]-2,b.outer[1]+2,sy-25,sy+25,sz-60,sz+60)
    add,cut=_derive(lambda s:e._side_wells(s,b.inner,(st,),-1000,1000,-1000,1000,up=up),clip)
    root=b.inner[1] if side>0 else b.inner[0]
    return _feature('Wago_'+size+'_well', ('E25','E26','E55'), origin=(root,sy,sz),
                    add=add,cut=cut,functions=('_side_wells',),source_print_up=(0,0,up),
                    backing={'wall_mm':3.,'well_wall_mm':e.wago_well_wall,
                             'end_tab_mm':e.wago_roof_tab,'station':st},
                    mates=('Wago 221-'+size+' with working wire levers',),
                    group='electronics side wall',
                    notes=('Use one connector-size family; preserve its insertion direction, end tabs and lever access.',
                           'Index 0 is an authentic ceiling-column-backed well; index 5 is a wall corbel variant.'))


def condenser_crown_rail():
    e,b=source(); st=b.pack.cond_cradle[-1]; face,x0,x1,z0,z1,root=st
    add,cut=_derive(lambda s:e._cond_cradle(s,b.inner,(st,),-1000,1000,-1000,1000),
                     (x0-3,x1+3,face-4,face+8,root-10,z1+10))
    return _feature('condenser_sheet_rail', ('E25','E56'), origin=((x0+x1)/2,face,(z0+z1)/2),
                    add=add,cut=cut,functions=('_cond_cradle','_cond_cradle_corbel'),
                    backing={'wall_mm':3.,'rail_width_mm':x1-x0,
                             'slipped_opening_mm':(z1-z0)+2*e.cond_slot_half(z1-z0),
                             'sheet_thickness_mm':z1-z0,'grip_mm':e.cond_slot_grip},
                    mates=('condenser thin flange sheet',),group='front refrigeration wall',
                    notes=('Complete crown groove retains its seated floor and rising 45-degree roof; support-free opening.',))


def condenser_upper_mount():
    e,b=source(); st=b.pack.cond_mount; flank,y0,y1,bosses=st
    bx,by,tip=max(bosses,key=lambda s:s[2]); root=tip-e.cond_boss_t
    west=bx-e.mount_boss_dia
    stock=e._ybox(west,b.inner[1],y0,y1,root,tip).fuse(e._cond_mount_corbel(b.inner,st))
    bore=e._zcyl(e.heatset_dia/2,bx,by,tip-e.cond_bore_depth,tip)
    return _feature('condenser_M3_corbel', ('E23','E25'), origin=(flank,(y0+y1)/2,tip),
                    add={'upper_finger_and_corbel':stock},cut={'vertical_M3_pilot':bore},
                    functions=('_cond_mount','_cond_mount_corbel'),
                    backing={'wall_root_local_x_mm':0.,'finger_mm':e.cond_boss_t,
                             'pilot_diameter_mm':e.heatset_dia},
                    mates=('condenser upper flange hole and M3 screw',),group='east refrigeration wall',
                    notes=('Upper finger is an exact source section; grow its standing fin down into broad wall/floor stock.',))


def core_corner_stop():
    e,b=source(); st=b.pack.core_stops[0]; cx,cy,r=st
    add,cut=_derive(lambda s:e._core_stops(s,b.inner,(st,),-1000,1000,-1000,1000),
                    (b.inner[0]-3,cx+r+3,cy-r-10,cy+5,b.inner[4]-6,b.inner[4]+45))
    return _feature('cold_core_corner_stop', ('E57',),origin=(cx,cy,b.inner[4]),
                    add=add,cut=cut,functions=('_core_stops',),
                    backing={'floor_mm':6.,'height_mm':e.core_stop_rise,
                             'flat_web_mm':e.core_stop_web,'bore_diameter_mm':2*(r+e.core_stop_slip/2)},
                    mates=('native rounded cold-core cap corner and flat front datum',),
                    group='rear floor / corner column',
                    notes=('One of two mirrored locating corners; round and flat contacts are distinct constraints on the same seat.',))


def core_hold_down():
    e,b=source(); st=b.pack.core_holds[0]; x0,x1,aft,crown=st
    add,cut=_derive(lambda s:e._core_holds(s,b.inner,(st,),-1000,1000,-1000,1000),
                    (x0-3,x1+3,aft-e.core_hold_reach-3,b.inner[3]+4,crown-2,crown+45))
    return _feature('cold_core_hold_down', ('E57',),origin=((x0+x1)/2,b.inner[3],crown),
                    add=add,cut=cut,functions=('_core_holds',),source_print_up=(0,0,-1),
                    backing={'wall_mm':3.,'leg_height_mm':e.core_hold_rise,
                             'bearing_land_mm':e.core_hold_land,'reach_mm':e.core_hold_reach},
                    mates=('cold-core cap crown and incoming crown edge',),group='rear top wall',
                    notes=('Retain the trapezoid gusset, flat bearing face and 1 mm incoming-edge lead.',))


def mq6_slot():
    e,b=source(); st=b.pack.west_cradle[0]; sx,sy,sz=st[:3]
    add,cut=_derive(lambda s:e._west_cradle(s,b.inner,(st,),-1000,1000,-1000,1000),
                    (b.outer[0]-2,sx+10,sy-25,sy+25,b.inner[4]-6,sz+25))
    return _feature('MQ6_card_chute', ('E59',),origin=(e.lip_face_x()[0],sy,b.inner[4]),
                    add=add,cut=cut,functions=('_west_cradle',),
                    backing={'floor_mm':6.,'side_wall_mm':6.,'post_wall_mm':e.mq6_rail_wall,
                             'card_length_mm':e.mq6_card_y,'card_height_mm':e.mq6_card_z},
                    mates=('MQ-6 board ends and can, with header lead access',),group='west lower wall',
                    notes=('Preserve both complete opposed grooves and their blind bottom shoulders; top and header access remain open.',))


def prv_chase():
    e,b=source(); st=b.pack.vent_chase[0]; sx,sy,sz=st
    # Both source piece shares together keep the actual continuous escape path.
    parts={}
    masks=(('lower',b.outer[4],b.splits[1],1.),('upper',b.splits[1],b.outer[5],-1.))
    for name,z0,z1,up in masks:
        add,cut=_derive(lambda s:e._vent_chase(s,b.inner,b.outer,(st,),-1000,1000,z0,z1,up),
                       (b.outer[0]-3,sx+5,sy-15,sy+15,sz-85,sz+40))
        parts[name]=(add,cut)
    add={name+'_'+k:v for name,(a,c) in parts.items() for k,v in a.items()}
    cut={name+'_'+k:v for name,(a,c) in parts.items() for k,v in c.items()}
    return _feature('PRV_escape_chase', ('E24','E59'),origin=(b.outer[0],sy,sz),
                    add=add,cut=cut,functions=('_vent_chase',),
                    source_print_up=(0,0,-1),
                    backing={'liner_mm':e.vent_rib_wall,'channel_width_mm':e.vent_channel_w,
                             'native_Z_seam_local_mm':b.splits[1]-sz,
                             'shares':{'lower_print_up':(0,0,1),'upper_print_up':(0,0,-1)}},
                    mates=('PRV discharge tube and open atmosphere', 'paired Z-seam wall shares'),
                    group='west wall below the cold core',
                    notes=('Cut the chase after both source shares join their walls; do not close the show-skin exit.',
                           'Upper and lower shares retain opposite native print directions.'))


def tube_anchor(index=2):
    e,b=source(); st=b.pack.tube_anchors[index]; mid,u,n,r=st[:4]
    quadrant=('back','top') if mid[1]>b.y_joint and mid[2]>b.splits[1] else ('front','top')
    roots=e.piece_root_faces(b.inner,*quadrant); up=e.print_up(*quadrant)
    clip=tuple(v for pair in [(mid[0]-45,mid[0]+45),(mid[1]-45,mid[1]+45),(mid[2]-45,mid[2]+45)] for v in pair)
    add,cut=_derive(lambda s:e._tube_anchors(s,roots,b.inner,(st,),-1000,1000,-1000,1000,up),clip)
    return _feature('tube_anchor_'+str(index),('E25','E26','E52'),origin=mid,
                    add=add,cut=cut,functions=('_tube_anchors',),source_print_up=(0,0,up),
                    backing={'radial_wall_mm':3.,'length_mm':e.tube_anchor_len,
                             'seat_radius_mm':r,'tube_axis':u,'root_direction':n,
                             'tie_cavity_depth_mm':e.tube_anchor_cavity_depth},
                    mates=('tube or fitting of the stated source radius', 'nylon zip tie'),
                    group='plumbing run on side wall / ceiling',
                    notes=('Keep axis-plane truncation, full 3 mm flat lips and both tie-channel mouths.',
                           'The matching tube diameter is a geometry datum; the print is not the fluid passage.'))


def flow_meter_anchors():
    e,b=source(); st=b.pack.flow_meter_anchors; x,z,r,bands=st
    roots=e.piece_root_faces(b.inner,'back','top')
    clip=(x-r-8,x+r+8,min(y[0] for y in bands)-3,max(y[1] for y in bands)+3,z-r-10,b.inner[5]+4)
    add,cut=_derive(lambda s:e._flow_meter_anchors(s,roots,st,-1000,1000,-1000,1000,up=-1.),clip)
    cut.update({f'ceiling_tie_exit_{i}':s for i,s in enumerate(e._ceiling_tie_reliefs(b,b.inner[5])[:2])})
    return _feature('flow_meter_collar_pair',('E53','E60'),origin=(x,min(y[0] for y in bands),roots[5]),
                    add=add,cut=cut,functions=('_flow_meter_anchors',),source_print_up=(0,0,-1),
                    backing={'ceiling_mm':3.,'native_grown_ceiling_mm':e.back_top_ceiling_t,
                             'radial_wall_mm':3.,'seat_radius_mm':r,
                             'end_web_mm':e.flow_meter_anchor_end_wall,
                             'anchor_length_mm':e.flow_meter_anchor_len},
                    mates=('both fixed collars of the actual flow meter', 'two nylon zip ties'),
                    group='ceiling plumbing lane',
                    notes=('The two collars are a necessary physical mate on one meter; retain both source seats.',
                           'The two ties carry the meter; an open-down bore alone retains nothing.'))


def asse_anchor():
    e,b=source(); st=b.pack.asse_cradle; z,sections,ties,dn=st
    y0=min(s[0] for s in sections); y1=max(s[1] for s in sections)
    add,cut=_derive(lambda s:e._asse_cradle(s,b.inner,st,-1000,1000,-1000,1000,up=-1.),
                    (b.outer[0]-2,-55,y0-3,y1+3,z-45,b.inner[5]+5))
    cut['shared_ceiling_tie_exit']=e._ceiling_tie_channel_relief(b,b.inner[5])
    return _feature('ASSE_stepped_hex_anchor',('E24','E25','E54','E60'),
                    origin=(b.inner[0],y0,z),add=add,cut=cut,
                    functions=('_asse_cradle','_asse_v','_asse_tie_cavity'),source_print_up=(0,0,-1),
                    backing={'wall_mm':3.,'included_angle_degrees':120.,
                             'native_sections':sections,'tie_centres_mm':ties},
                    mates=('the stepped ASSE threaded chain', 'two wide nylon zip ties'),
                    group='west upper plumbing wall',
                    notes=('The three stepped contact sections retain actual round/hex profiles and longitudinal capture.',
                           'Keep the complete common channel and its ceiling exit; no support-access claim follows from geometry alone.'))


def valve_seat_section(sign=-1.):
    e,b=source(); source_row=next(st for st in b.pack.valve_trays if st[1]==sign)
    plane,sign,seats=source_row; sx,sz=seats[0]
    span=e._seat.seat_half_x+e._valve_tray.MARGIN
    half_height=e._valve_tray.height(((sx,sz),))/2.
    local_inner=(sx-span,sx+span,*b.inner[2:])
    add,cut=_derive(lambda s:e._valve_trays(s,local_inner,((plane,sign,((sx,sz),)),),
                                           -1000,1000,sz-half_height,1000),
                    (sx-span-3,sx+span+3,plane-20,plane+20,sz-half_height-5,sz+half_height+5))
    return _feature('Beduan_V69_four_post_seat',('E24','E25','E47'),origin=(sx,plane,sz),
                    add=add,cut=cut,functions=('_valve_trays','_valve_socket_cutters'),
                    backing={'socket_diameter_mm':2*e._seat.socket_radius,
                             'deck_thickness_mm':e._valve_tray.THICK,
                             'seat_mm':e._valve_tray.SEAT,'sign':sign},
                    mates=('one Beduan valve, all four mounting posts and both port channels',),
                    group='stationary manifold partition',
                    notes=('One complete four-post footprint represents the press fit; retain body clearance without reaming the sockets.',))


def cable_clip():
    e,_=source(); c=e._cable_clip
    # The exact local clip in a source-aligned broad ridge wall.  Clip +X maps
    # to machine +Y; its cable axis maps to +X and profile rise remains +Z.
    seed=box((-3,c.RUN+3,-3,0,-3,c.HEIGHT+3))
    formed=c.apply(seed,origin=(0,0,0),outward=(0,1,0),along=(1,0,0),
                   embed=0,wall_thickness=3).val()
    return _feature('wall_cable_clip',('E25','E51'),add={'native_clip':formed.cut(seed)},
                    cut={'S_entry':seed.cut(formed)},files=(PP/'cadlib/cable_clip.py',),
                    backing={'wall_mm':3.,'projection_mm':c.DEPTH,'height_mm':c.HEIGHT,
                             'cable_axis_length_mm':c.RUN,'root_plane_local_y_mm':0.},
                    mates=('braided loom across the display backing wall',),group='display ridge interior',
                    notes=('Keep the complete two mouths, S-entry ramps and 3 mm backing.',))


def pump_native_section():
    e,b=source(); cx,cy,cz=b.pack.pump_trays[0]
    # The cut is entirely within unused width between pump wells, not through
    # the octagon, full head/skirt datum, motor circle, fittings or right pull.
    x0=cx-e.cap_slot_half-3.
    window=(x0,b.outer[1]+1,b.outer[2]-1,e.pump_cartridge_aft_y(b.pack.pump_trays,b.pack.collet_plate)+1,
            e.bay_floor_z(b.pack.pump_trays)[1]-1,b.pump_bay[2]+1)
    cropped={name:step(file).intersect(box(window)).clean() for name,file in
             (('one_pump_drawer','enclosure-pump-cartridge'),('one_pump_cap','enclosure-pump-cap'))}
    origin=(cx,cy,e.bay_floor_z(b.pack.pump_trays)[1])
    rooms=e._pump_drop_voids(b)[:1]
    cap=e._pump_clamp_gross(b).intersect(box(window)).clean()
    cropped['uncut_cap_before_M3_and_pogo']=cap
    return _feature('one_pump_full_height_native_section',('E38','E39','E40'),origin=origin,
                    parts=cropped,cut={'complete_head_drop_and_fitting_rooms':rooms[0]},
                    functions=('_pump_drop_voids','_pump_clamp_gross'),
                    files=(ENC/'enclosure-pump-cartridge.step',ENC/'enclosure-pump-cap.step'),
                    part_print_up={'one_pump_drawer':(0,0,1),'one_pump_cap':(0,0,-1),
                                   'uncut_cap_before_M3_and_pogo':(0,0,-1)},
                    backing={'source_crop_mm':window,'native_drawer_height_mm':118.9790001,
                             'native_sill_air_mm':.25,'native_lintel_air_mm':.50,
                             'new_cut_face_requires_mm':3.},
                    mates=('one physical Kamoer pump with both fitting passages', 'fixed bay bearing floor and rear plane'),
                    group='working front pump drawer',
                    notes=('This is an open section through an empty source width run; it does not by itself include centre-spine M3/pogo fasteners.',
                           'Recompose that spine and its docking contacts as the same drawer’s inner wall; retain source M3 screw span and roof access.',
                           'STL flutes and the right rounded pull are not represented by a simple fresh smooth STEP mesh.'))


def tee_carrier_section():
    e,b=source(); c=e.tee_carrier(b.pack); tc=e._tee_carrier
    low=_load(PP/'enclosure/tee-carrier/low-force-trial/low_force_trial.py','pour_low_force_source')
    from dataclasses import asdict
    c=low.LowForceCarrier(**asdict(c))
    x0=max(c.tee_xs)-c.trough_r-3.
    plate=b.pack.collet_plate
    clip=box((x0,c.exterior_x+1,plate['fore_y']-1,c.cover_y[1]+1,
              min(plate['z0']-1,c.floor_z-2),c.roof_z+2))
    moving=tc.build_plate(c).val().intersect(clip).clean()
    post=tc._post(c).intersect(clip).clean()
    cover=tc._cover(c).intersect(clip).clean()
    pockets=[e._teardrop_y(r,x,z,y0,y1) for x,z,y0,y1,r in tc.spring_pockets(c) if x>0]
    origin=(c.flank_x,c.wall_aft_y,c.floor_z)
    release=e._tee_wall(b.inner,b.y_joint,plate,b.pump_bay).intersect(clip).clean()
    hx,hz=max(plate['holes'],key=lambda s:s[0])
    release_room=e._ycyl(plate['hole_d']/2,hx,hz,plate['fore_y']-1,plate['aft_y']+1).fuse(
        e._tee_bore(plate,hx,hz))
    return _feature('tee_carrier_working_section',('E11','E12','E24','E25','E29','E30','E41','E44','E45','E46'),
                    origin=origin,add={'window_cover_post':post,'collet_release_and_journal_wall':release},
                    cut={'window_and_staging_room':tc.opening(c).intersect(clip),
                         'collet_and_tee_journal':release_room,
                         **{f'return_spring_pocket_{i}':s for i,s in enumerate(pockets)}},
                    parts={'moving_tee_carrier':moving,'vertical_window_cover':cover},
                    functions=('tee_carrier','_collet_plate_body'),
                    files=(PP/'enclosure/tee-carrier/tee_carrier.py',
                           PP/'enclosure/tee-carrier/low-force-trial/low_force_trial.py'),
                    part_print_up={'moving_tee_carrier':(0,-1,0),'vertical_window_cover':(-1,0,0)},
                    backing={'native_flank_mm':9.,'radial_tee_backing_mm':3.,
                             'selected_roof_air_mm':c.roof_z-c.column_z[1],
                             'floor_air_mm':c.column_z[0]-c.floor_z,
                             'release_face_thickness_mm':plate['aft_y']-plate['fore_y'],
                             'carrier_fields':asdict(c),'source_empty_width_cut_mm':x0},
                    mates=('one complete outer tee and two ties', 'two real return springs in the one retained column',
                           'matching fixed release journal and window roof/floor', 'one sliding window cover'),
                    group='fixed plumbing rear partition with actual moving tee carrier',
                    notes=('Only repeated tee stations are omitted; the complete one-column working length, spring bores, R6 rounds and capture gap remain.',
                           'The cropped carrier section needs its open inner edge joined to the drawer’s native structure; it is not a free loose coupon.',
                           'Support-free additive R6 and 0.08 top-round recipe retain the accepted source scope; force, spring return and four-collet simultaneity are not accepted by it.'))


def ceiling_plumbing_rooms():
    e,b=source(); lane=b.inner[5]
    cuts=e._ceiling_tie_reliefs(b,lane)
    common=e._ceiling_tie_channel_relief(b,lane)
    if common is not None:cuts.append(common)
    # Actual reliefs that have a material ceiling to cut; the caller selects
    # the matching hardware/anchor group rather than depositing every repeat.
    for who,x0,x1,y0,y1,top in b.pack.ceiling_reliefs:
        roof=min(top,lane)
        if roof>e.back_top_ceiling_face()+e.stated_bound_tol and who!='c14-inlet':
            cuts.append(e._ybox(x0,x1,y0,y1,e.back_top_ceiling_face()-1,roof))
    return _feature('ceiling_plumbing_reliefs',('E60',),origin=(0,0,lane),
                    cut={f'source_relief_{i}':s for i,s in enumerate(cuts)},
                    functions=('_ceiling_tie_reliefs','_ceiling_tie_channel_relief','_back_top_ceiling'),
                    source_print_up=(0,0,-1),backing={'ceiling_mm':3.,'grown_ceiling_face_mm':e.back_top_ceiling_face()},
                    mates=('the same source meter, tube and ASSE anchor groups',),
                    group='underside of service roof',
                    notes=('These source rooms retain global plumbing stations; translate each complete matched anchor and its room together.',
                           'Do not use the whole source coordinate list as a standalone perforated coupon.'))


def source_funnel_frame():
    e,_=source(); ff=e._funnel_frame_part
    native=cq.importers.importStep(str(PP/'zone-c/funnel/funnel-frame.step')).val()
    return _feature('funnel_frame_source',('E20','E25','E50'),parts={'frame':native},
                    files=(PP/'zone-c/funnel/funnel_frame.py',PP/'zone-c/funnel/funnel-frame.step'),
                    backing={'native_frame_width_mm':ff.width,'native_body_width_mm':ff.body_width,
                             'web_mm':ff.web,'source_print_origin':(0,ff.center_y,ff.datums()[0])},
                    mates=('matching paired rail receivers', 'concentric funnel brim and bowl', 'elbow cradle hooks'),
                    group='actual drain surround / rear service roof',
                    notes=('The full source is wider than a 180 mm cabinet; use a true sectional crop with complete active rail and concentric brim arc.',
                           'Cropping a rail’s entry/catch/stop or leaving an incidental thin rim does not represent the joint.'))


def bundle_builders():
    """Research construction pass, not a production build hook or acceptance gate."""
    functions=(m5_floor_post,m3_wall_mount,pogo_seat,lambda:pogo_seat(-1.,-1.),
               lambda:pogo_leads('fixed'),lambda:pogo_leads('cap'),magnet_pocket,
               lambda:magnet_pocket(-1.),c14_tunnel,keystone_receptacle,
               wago_well,lambda:wago_well(5),condenser_crown_rail,condenser_upper_mount,
               core_corner_stop,core_hold_down,mq6_slot,prv_chase,tube_anchor,
               flow_meter_anchors,asse_anchor,valve_seat_section,cable_clip,
               pump_native_section,tee_carrier_section,ceiling_plumbing_rooms,source_funnel_frame)
    return functions


def all_bundles():
    return [f() for f in bundle_builders()]


if __name__=='__main__':
    # The only writes are the caller-requested private research metadata.
    result=[]
    for build_function in bundle_builders():
        build=build_function()
        result.append(build.report())
        print(build.name, flush=True)
    path=Path(__file__).with_name('enclosure-feature-bundles.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
