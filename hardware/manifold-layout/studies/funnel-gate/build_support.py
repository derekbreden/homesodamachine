"""Build the frame-carried V-B seat wall through the shared native CAD queue."""
from pathlib import Path
import importlib.util
import json

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def block(bounds):
    lo, hi = bounds
    return cq.Solid.makeBox(*(b-a for a, b in zip(lo, hi)), cq.Vector(*lo))


def main():
    plan = json.loads((HERE / 'mount-plan.json').read_text())
    seat = module('funnel_gate_valve_seat', ROOT / 'hardware/printed-parts/valve-seat/valve_seat.py')
    exporter = module('funnel_gate_native_export', HERE.parent / 'co2-fold/build.py')
    exporter.HERE = HERE
    rotation, origin = plan['vb_native_rotation'], plan['vb_native_origin_mm']
    placement = cq.Location(cq.Plane(origin=tuple(origin),
        xDir=tuple(rotation[i][0] for i in range(3)),
        normal=tuple(rotation[i][2] for i in range(3))))
    support = block(plan['seat_wall_bounds_mm']).fuse(block(plan['frame_bridge_bounds_mm']))
    support = support.cut(seat.build_sockets().val().moved(placement))
    support = support.cut(seat.build_port_channel(2*seat.seat_half_y+2).val().moved(placement)).clean()
    report = exporter.export('vb-frame-support', [('integral-frame-extension', support)])
    report.update(assembly_owner=plan['assembly_owner'], attachment=plan['attachment'],
                  socket_diameter_mm=seat.socket_diameter,
                  socket_floor_stock_mm=plan['socket_floor_stock_mm'],
                  bridge_thickness_mm=plan['bridge_thickness_mm'], scope=plan['scope'])
    (HERE / 'parts/vb-frame-support.report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
