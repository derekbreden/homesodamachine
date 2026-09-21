"""Read-only native placement and cap-station exploration for the selected pump."""
from pathlib import Path
import json
import sys
import time

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT/'hardware/manifold-layout'))
import enclosure_assembly as ea
import g_ganen_installation as pump


def reading(shape):
    b = shape.BoundingBox()
    return [[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]]


def region(shape, z0, z1, y0, y1, x0=None, x1=None):
    b = shape.BoundingBox()
    x0, x1 = (b.xmin-1 if x0 is None else x0), (b.xmax+1 if x1 is None else x1)
    slab = cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))
    return pump.occupied_bounds(pump.intersect_components(shape, slab))


def run():
    f0, _ = ea.build_foam(0.)
    foam, fc = ea.build_foam(ea._enc.rear_plane_y-ea._enc.rear_seam_clear-ea.box(f0).ylen)
    source = pump.build()
    rigid = pump.rigid_shape()
    target_y = ea.box(foam).ymax-rigid.BoundingBox().xmax
    bearing_z = ea.cap_face(foam)
    # This is the retained prior native gate reading, used only for this local
    # exploration. Production placement receives the current manifold's gate.
    facts = json.loads((ROOT/'hardware/manifold-layout/enclosure-assembly.facts.json').read_text())
    bb = facts['bodies']['bulkhead-flavor-a']
    gate = (bb[2]+bb[5])/2
    shape, carry = ea.seat_body(source, (((0, 0, 1), pump.YAW),),
                              station=(pump.bearing_datum(), (0., target_y, bearing_z)))
    foot_group = cq.Compound.makeCompound(list(pump.feet_shapes(carry).values()))
    radius = ea._jg.BODY_D/2
    foot_band = region(foot_group, bearing_z-3, bearing_z+40,
                       ea.bulkhead_mouth_y(), ea._enc.rear_plane_y,
                       ea.PANEL_X['bulkhead-flavor-a']-radius,
                       ea.PANEL_X['bulkhead-flavor-a']+radius)
    storey = max(gate, (foot_band[1][2]+ea.PORT_FOOT_CLEAR+radius) if foot_band else gate)
    pan_front = pump.discharge_shape(carry).BoundingBox().ymax+ea.PAN_PORT_CLEAR
    west_band = region(shape, bearing_z+pump.observed_pad_upper_z(), shape.BoundingBox().zmax,
                       pan_front, shape.BoundingBox().ymax)
    lane_band = region(shape, storey-radius, storey+radius,
                       ea.bulkhead_mouth_y(), ea._enc.rear_plane_y)
    shift_x = max(0., ea.water_pump_west_limit()-west_band[0][0] if west_band else 0.,
                  ea.water_pump_port_lane_limit()-lane_band[0][0] if lane_band else 0.)
    installed, carry = ea.seat_body(source, (((0, 0, 1), pump.YAW),),
                                  station=(pump.bearing_datum(), (shift_x, target_y, bearing_z)))
    columns = [ea.cap_xy(fc, carry(((x, y, 0.), (0., 0., 1.)))[0][:2]) for x, y in pump.mount_holes()]
    anchor_rows = {}
    for name, mod, label in [('suction-chain', ea._suct, 'MAACFLOW hex'),
                              ('discharge-chain', ea._dis, 'GASHER hex')]:
        section = next(row for row in mod.sections() if row[0] == label)
        mid = (section[2]+section[3])/2
        at = fc(ea.cap_anchor(name))[0]
        chain, chain_carry = ea.seat_body(mod.build(), ea.SUCT_CHAIN_TURN,
                station=(((0., 0., -mid), (0., 0., 1.)), at))
        anchor_rows[name] = {'bounds_mm': reading(chain), 'barb': chain_carry(mod.barb_tip())[0],
                             'tube': chain_carry(mod.tube_port())[0],
                             'distance_to_pump_mm': chain.distance(installed)}
    out = {'source': 'Native candidate; source artifacts untouched',
           'retained_gate_z_mm': gate, 'foot_band_mm': foot_band,
           'flavor_storey_z_mm': storey, 'pan_front_y_mm': pan_front,
           'west_band_mm': west_band, 'lane_band_mm': lane_band,
           'pump_local_to_world': {'z_rotation_degrees': pump.YAW,
                                  'translation_mm': [shift_x, target_y, bearing_z]},
           'installed_bounds_mm': reading(installed), 'cap_mount_xy_mm': columns,
           'suction': carry(pump.suction()), 'discharge': carry(pump.discharge()),
           'chain_placements': anchor_rows,
           'cap_lid_height_mm': ea._cci.foam_cap_lid_height,
           'deck_boss_top_mm': ea._cci.foam_cap_height,
           'observed_pad_upper_mm': pump.observed_pad_upper_z()}
    (HERE/'placement-candidate.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2), flush=True)


if __name__ == '__main__':
    run()
