"""Manual local fit review. Run from repo root with the CAD Python.

Uses the declared placement, exported back-top and separate wire/tool probes.
This script is not invoked by a build, hook or scorecard.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import cadquery as cq

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
for rel in ('hardware/scripts','hardware/manifold-layout','hardware/printed-parts/enclosure/enclosure'):
    sys.path.insert(0,str(ROOT/rel))
import enclosure as enc
import enclosure_assembly as assembly
import _box_spec


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry_wire(start, sign):
    # 2 mm stock OD, 1 mm exposed straight, R3 fixed bend, 10 mm inboard leg.
    x,y,z = start
    a = cq.Vector(x,y+sign,z)
    middle = cq.Vector(x-3+3/math.sqrt(2),y+sign*(1+3/math.sqrt(2)),z)
    b = cq.Vector(x-3,y+sign*4,z)
    end = cq.Vector(x-13,y+sign*4,z)
    path = cq.Wire.assembleEdges([
        cq.Edge.makeLine(cq.Vector(x,y+sign*.05,z),a),
        cq.Edge.makeThreePointArc(a,middle,b), cq.Edge.makeLine(b,end)])
    plane = cq.Plane(origin=(x,y+sign*.05,z), normal=(0,sign,0))
    return cq.Workplane(plane).circle(1.0).sweep(path).val()


def main():
    box,_ = _box_spec.read(enc.Box,enc.Bound,(enc.Pack,enc.PortField,enc.Nameplate))
    observed = json.loads((HERE/'assembly-feedback.json').read_text())
    shell_path = ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step'
    shell = cq.importers.importStep(str(shell_path)).val()
    # Only zmin is used by cap_face; no inferred top-face seating.
    foam = cq.Solid.makeBox(1,1,1)
    psu, carry = assembly.build_psu(foam,assembly.east_wall_seat())
    relay, _ = assembly.build_relay2(psu,foam,assembly.east_wall_seat())
    board, _ = assembly.build_pcba(foam,relay,assembly.east_wall_seat())
    obstacles = {'back-top':shell,'relay-2':relay,'pcba':board}
    probes = []
    for side,positions in ((1,(-3.75,3.75)),(-1,(-7.5,-2.5,2.5,7.5))):
        local,axis = assembly._psu.wire_entry(side)
        for pitch in positions:
            position,direction = carry(((pitch,local[1],local[2]),axis))
            wire = entry_wire(position,side)
            screws,_ = carry(((pitch,(assembly._psu.length/2-assembly._psu.block_inset)*side,
                                assembly._psu.ledge_h+assembly._psu.block_h),(0,0,1)))
            tool_start = (screws[0]-.2,screws[1],screws[2])
            tool_axis = (-1,0,0)
            tool = cq.Solid.makeCylinder(1.75,35,
                    cq.Vector(*tool_start),cq.Vector(*tool_axis))
            for kind,shape,start,probe_axis in (('wire',wire,position,direction),
                                              ('screwdriver',tool,tool_start,tool_axis)):
                probes.append({'side':'AC' if side>0 else 'DC','reference_pitch_mm':pitch,
                    'kind':kind,'start_mm':list(start),'axis':list(probe_axis),
                    'obstacles':{name:{'intersection_mm3':abs(shape.intersect(body).Volume()),
                                      'gap_mm':shape.distance(body)}
                                 for name,body in obstacles.items()}})
    c14 = assembly.build_c14()[0]
    native_air = abs(shell.intersect(c14).Volume())
    before_board = observed['baseline_main_board_mounting_stations_mm']
    after_board = [list(s[:3]) for s in box.pack.east_bosses[4:8]]
    result = {
        'scope':'Local nominal wire bends and tool access against exported shell and adjacent electronics. Block mouths are representative. This is not a physical fit or complete harness-route result.',
        'sources':{str(p.relative_to(ROOT)):sha(p) for p in (shell_path,
            ROOT/'hardware/manifold-layout/enclosure-box.json',
            ROOT/'hardware/manifold-layout/enclosure_assembly.py',
            ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure.py',
            Path(__file__).resolve(),
            ROOT/'hardware/reference/meanwell-irm90/meanwell_irm90.py')},
        'c14_reference_intersection_mm3':native_air,
        'back_top_valid':shell.isValid(), 'back_top_solid_count':len(shell.Solids()),
        'main_board_mounting_stations_mm':after_board,
        'main_board_mounting_stations_unchanged':before_board==after_board,
        'psu_mounting_stations_mm':[list(s[:3]) for s in box.pack.east_bosses[:4]],
        'wire_probe':{'od_mm':2.0,'straight_mm':1.0,'bend_centre_radius_mm':3.0,
                      'inboard_leg_mm':10.0,'physical_bend_qualified':False},
        'tool_probe':{'shaft_diameter_mm':3.5,'reach_mm':35.0}, 'probes':probes}
    (HERE/'native-clearance-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
    hits=[p for p in probes if any(v['intersection_mm3']>1e-5 for v in p['obstacles'].values())]
    print('Local wire/tool probes:',len(probes),'blocked:',len(hits))
    print('C14 reference overlap mm3:',native_air)
    print('Board stations unchanged:',before_board==after_board)
    print('Back-top valid solids:',shell.isValid(),len(shell.Solids()))
    for p in hits:print(p)

if __name__ == '__main__':main()
