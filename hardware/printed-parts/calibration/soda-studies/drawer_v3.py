"""One native pump well with its complete docking and retention mechanism.

Cache construction only.  Production files are inputs and remain untouched.
The source centre spine is retained beside the right pump, so the original
two M3 x 60 fasteners, contact ear datums and sealed magnet pair keep their
actual cross-sections and relative positions.  One empty width run is closed
with broad stock.  The parent owns the cabinet and applies the returned rooms
after adding its walls, floors and fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import enclosure_features as native


@dataclass
class Drawer:
    parts: dict
    fixed: dict
    cut: dict
    reference: dict = field(default_factory=dict)
    external_service_rooms: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def apply_fixed(self, host):
        host = host.val() if isinstance(host, cq.Workplane) else host
        for shape in self.fixed.values():
            host = host.fuse(shape)
        for shape in self.cut.values():
            host = host.cut(shape)
        return host.clean()

    def report(self):
        result = dict(self.metadata)
        for kind in ('parts', 'fixed', 'cut', 'reference', 'external_service_rooms'):
            result[kind] = {name: {'bounds_mm': native.bounds(shape),
                'volume_mm3': shape.Volume(), 'valid': shape.isValid(),
                'solids': len(shape.Solids())}
                for name, shape in getattr(self, kind).items()}
        return result


def _union(shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.clean()


def build(*, pump_axis=(20.,126.), bay_floor_z=6., front_y=0.,
          fascia_top_z=70., fixed_wall_top_z=None, side_air=.25,
          withdrawal_mm=175.):
    e,b = native.source()
    sx,sy,sz = b.pack.pump_trays[0]
    source_floor = e.bay_floor_z(b.pack.pump_trays)[1]
    dx,dy,dz = pump_axis[0]-sx, pump_axis[1]-sy, bay_floor_z-source_floor
    move = (dx,dy,dz)
    aft = e.pump_cartridge_aft_y(b.pack.pump_trays,b.pack.collet_plate)
    face = e.bay_back_y(b.pack.collet_plate)
    crown = e.cap_crown_z(b)
    split = e.cap_split_z(b.pack.pump_trays)
    base = e.cap_base_z(b.pack.pump_trays)
    plate = b.pack.collet_plate

    # A fresh 3 mm wall closes the cut through the empty central width run.
    # The source centre-lane opening is the receiving room for the cap spine.
    # Its exact left side, not an approximate well boundary, sets this wall.
    centre_room = e._pump_drop_voids(b)[-1]
    left_inner = centre_room.BoundingBox().xmin
    left_outer = left_inner - 3.
    cap_left = left_inner + e.clamp_drop_air
    right_outer = e._cap_x_span(b.pump_bay)[1]
    crop = native.box((left_inner,right_outer+1.,b.outer[2]-1.,aft+1.,
                       source_floor-1.,crown+1.))
    cartridge = native.step('enclosure-pump-cartridge').intersect(crop)
    cut_wall = native.box((left_outer,left_inner,b.outer[2],aft,
                          source_floor,crown))
    cartridge = cartridge.fuse(cut_wall)

    # The original cap spine is complete.  Omit only the lead groove whose
    # physical pump was omitted; keep the native right-pump lead destination.
    cap_crop = native.box((cap_left,right_outer+1.,b.outer[2]-1.,aft+1.,
                           base-1.,crown+1.))
    cap = e._pump_clamp_gross(b).intersect(cap_crop)
    for cutter in e._cap_screws(b)[0]:
        cap = cap.cut(cutter)
    cap_cuts = e._pump_contact_cap_cuts(b)
    for cutter in cap_cuts[:4] + [cap_cuts[4]]:
        cap = cap.cut(cutter)

    # The active well remains in its source frame.  Low bed-rooted stock
    # joins it to the front face, under the compact cabinet's front flat.
    source_front = b.outer[2] + dy
    wx0,wx1 = left_outer+dx,right_outer+dx
    cartridge = cartridge.translate(move)
    cap = cap.translate(move)
    floor = native.box((wx0,wx1,front_y,source_front+.5,
                        bay_floor_z,bay_floor_z+3.))
    fascia = native.box((wx0,wx1,front_y,front_y+3.,
                         bay_floor_z,fascia_top_z))
    runners = [native.box((x0,x1,front_y+3.,source_front+.5,
                           bay_floor_z,bay_floor_z+6.)) for x0,x1 in
               ((wx0,wx0+3.),(wx1-3.,wx1))]
    cartridge = _union([cartridge,floor,fascia,*runners])
    cap = cap.clean()

    # The stationary partition has the source release shoulder and journal,
    # male contact half, inserts, lead bore and inward-facing RC62 pocket.
    # It roots directly on the cabinet bearing floor; no specimen holder.
    actual_fixed_top = b.pump_bay[2]+dz if fixed_wall_top_z is None else fixed_wall_top_z
    fixed = native.box((wx0,wx1,face+dy,plate['wall_aft_y']+dy,
                        bay_floor_z,actual_fixed_top))
    fixed_rooms = []
    for hx,hz in plate['holes']:
        if hx > 0:
            fixed_rooms.append(e._ycyl(plate['hole_d']/2.,hx,hz,
                                      face-1.,plate['aft_y']+1.).translate(move))
            fixed_rooms.append(e._tee_bore(plate,hx,hz).translate(move))
    fixed_rooms.extend(c.translate(move) for c in e._pump_contact_fixed_cuts(b))
    fixed_rooms.append(e.pump_retention_pocket(b,'front-top').translate(move))
    for room in fixed_rooms:
        fixed = fixed.cut(room)
    fixed = fixed.clean()

    # Rooms are cut from every stationary cabinet contribution after fusing.
    # Their whole withdrawal envelope is kept; the +Z clamp room is separate.
    fascia_room = native.box((wx0-side_air,wx1+side_air,front_y-1.,source_front+.5,
                              bay_floor_z-.25,fascia_top_z+.50))
    rear_room = native.box((wx0-side_air,wx1+side_air,source_front-.5,face+dy,
                            bay_floor_z, crown+dz+.50))
    cap_lift_room = native.box((cap_left+dx-e.clamp_drop_air,
                                sx+e.cap_slot_half+dx+e.clamp_drop_air,
                                e._pump_upper_well_fore_y(b.pack.pump_trays)+dy,
                                face+dy,split+dz-e.clamp_drop_air,140.))
    travel = native.box((wx0-side_air,wx1+side_air,
                         front_y-withdrawal_mm,face+dy,
                         bay_floor_z-.25,crown+dz+.50))

    # Nominal hardware is for mating review, not a request to fabricate a
    # substitute connector.  The male's travel equals the seated face gap.
    kiss = face-aft
    px,pz = e.pump_contact_station(b)
    male = e._pogo.build_male(pin_reach=kiss).val().rotate((0,0,0),(1,0,0),90)
    male = male.translate((px+dx,face+dy,pz+dz))
    female = e._pogo.build_female().val().rotate((0,0,0),(1,0,0),-90)
    female = female.translate((px+dx,aft+dy,pz+dz))
    magnets = {
        'RC62_fixed': e._retention.magnet(e.pump_retention_station(b),face,1.).translate(move),
        'RC62_drawer': e._retention.magnet(e.pump_retention_station(b),aft,-1.).translate(move),
        'pogo_male_pressed':male, 'pogo_female':female,
    }
    pull_ys = e.pull_y_span(b.pack.pump_trays,plate)
    pull_zs = e.pull_z_span(b)
    screw_y = [y+dy for y in e.cap_screw_ys(b.inner,plate)]
    meta = {
        'name':'one_pump_complete_drawer',
        'entries':['E23','E24','E28','E29','E38','E39','E40','E41','E42','E43'],
        'source_translation_mm':move,
        'source_crop_x_mm':[left_inner,right_outer],
        'closed_cut_wall_x_mm':[wx0,left_inner+dx],
        'cap_cut_x_mm':cap_left+dx,
        'part_print_up':{'pump_drawer':(0,0,1),'pump_cap':(0,0,-1),
                         'fixed_docking_wall':(0,0,1)},
        'native_sill_air_mm':.25, 'native_lintel_air_mm':.50,
        'side_running_air_mm':side_air,
        'bearing_floor_z_mm':bay_floor_z,
        'drawer_aft_y_mm':aft+dy,'fixed_mating_y_mm':face+dy,
        'docking_face_air_mm':kiss,
        'fixed_wall_thickness_mm':plate['wall_aft_y']-face,
        'source_collet_release_face_mm':plate['aft_y']-face,
        'whole_cap_source_z_mm':[base+dz,crown+dz],
        'native_bracket_station_z_mm':split+dz,
        'M3_pair':{'world_x_mm':dx,'world_y_mm':screw_y,'underhead_length_mm':60.,
                   'source_head_seat_z_mm':e.cap_head_seat_z(b)+dz,
                   'long_insert_mm':e.cap_heatset_len,
                   'cradle_pilot_mm':e.heatset_dia,
                   'cap_shank_clear_mm':e.screw_clear_dia,
                   'cap_head_counterbore_mm':e.head_cbore_dia},
        'pogo_pair':{'world_axis_xz_mm':[px+dx,pz+dz],
                     'M1_4_pilot_dia_mm':e.pogo_heatset_dia,
                     'insert_setback_mm':e.pogo_heatset_setback,
                     'ear_back_mm':e._pogo.ear_back(),
                     'lead_groove_mm':e.pogo_groove,
                     'nominal_pin_press_mm':e._pogo.PIN_PROUD-kiss},
        'retention_pair':{'world_axis_xz_mm':[v+t for v,t in zip(e.pump_retention_station(b),(dx,dz))],
                          'cover_mm':e._retention.FACE_COVER,
                          'rear_backing_mm':e._retention.BACKING,
                          'requires_real_RC62_pair_and_native_insertion_pause':True},
        'genuine_side_pull':{'opening_world_x_mm':right_outer+dx,
                             'y_mm':[v+dy for v in pull_ys],
                             'z_mm':[v+dz for v in pull_zs],
                             'depth_mm':e.pull_depth,'corners_r_mm':e.pull_corner_r,
                             'rim_r_mm':e.pull_edge_r,
                             'access':'right side service aperture or removed side member',
                             'cannot_fit_intact_below_front_flat_83_7_mm':True},
        'routes':{'drawer':'remove front-top counter/display section, then straight world -Y; reverse +Y to dock before reinstalling front-top',
                  'cap':'remove the two M3 screws, then +world Z through the upper well with drawer withdrawn',
                  'service_dependency':'the closed counter front flat at Z 83.7 is lower than the intact Z 124.979 cap; do not pull the full cartridge through it',
                  'full_withdrawal_mm':withdrawal_mm,
                  'cartridge_sweep_bounds_mm':native.bounds(travel),
                  'scope':'nominal corridor bounds; final loaded cabinet collision review is parent-owned'},
        'physical_scope':{'pump_fit_record':'hardware/reference/kamoer-kphm400/physical-fit.json',
                          'source_mag_cover_record':'hardware/printed-parts/enclosure/enclosure/magnet-retention/selected-fit-v1/h2c-v20/physical-acceptance.json',
                          'limits':'Native existing holder fit and identified first-over-magnet appearance only. This cropped single-pump assembly, new wall, forward stock, magnetic force, contact compression and handling life are unprinted.'},
        'provenance':[native.provenance(native.ENC/'enclosure-pump-cartridge.step'),
                      native.provenance(native.ENC/'enclosure.py', '_pump_clamp_gross'),
                      native.provenance(native.ENC/'enclosure.py', '_cap_screws'),
                      native.provenance(native.ENC/'enclosure.py', '_pump_contact_cap_cuts'),
                      native.provenance(native.ENC/'enclosure.py', '_pump_contact_fixed_cuts'),
                      native.provenance(native.ENC/'enclosure.py', '_tee_bore'),
                      native.provenance(native.ENC/'_cartridge_retention.py')],
    }
    # Fixed rooms are separately returned so later broad cabinet stock cannot
    # refill the native apertures, roofs or recessed heat-set seats.
    cuts = {'front_fascia_and_runners_room':fascia_room,
            'native_rear_drawer_room':rear_room,
            **{f'fixed_native_room_{i}':s for i,s in enumerate(fixed_rooms)}}
    return Drawer({'pump_drawer':cartridge,'pump_cap':cap},
                  {'fixed_docking_wall':fixed},cuts,magnets,
                  {'cap_vertical_installation_room_outside_cabinet':cap_lift_room},meta)


if __name__=='__main__':
    result = build()
    out = HERE/'drawer'
    out.mkdir(exist_ok=True)
    assembly = cq.Assembly(name='one-pump-drawer')
    for kind in ('parts','fixed'):
        for name,shape in getattr(result,kind).items():
            cq.exporters.export(shape,str(out/(name+'.step')))
            cq.exporters.export(shape,str(out/(name+'.stl')),tolerance=.015,angularTolerance=.08)
            assembly.add(shape,name=name,color=cq.Color(.14,.16,.17))
    from _cadq_export import export_assembly
    export_assembly(assembly,str(out/'drawer-assembly.step'))
    (out/'metadata.json').write_text(json.dumps(result.report(),indent=2)+'\n')
    print(json.dumps(result.report(),indent=2),flush=True)
