#!/usr/bin/env python3
"""Native fixed-fitting pockets, complete anchor stock and straight tie access.

Read an already placed native pack. This builds only a bounded west-wall segment;
it neither exports production parts nor qualifies a complete enclosure or slice.
"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import marshal
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack-cache', type=Path, required=True,
                        help='frames.json and placed native .brep bodies from one build_pack')
    parser.add_argument('--box', type=Path,
                        default=ROOT/'hardware/manifold-layout/enclosure-box.json')
    parser.add_argument('--output', type=Path, default=HERE/'flank-clearance.json')
    args = parser.parse_args()
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path[:0] = [str(ROOT/'hardware/manifold-layout'), str(ROOT/'hardware/scripts'),
                    str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
    import cadquery as cq
    import _box_spec
    import enclosure as enc
    import enclosure_assembly as assembly
    import water_split

    box, _ = _box_spec.read(enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate), path=args.box)
    records_path = args.pack_cache/'frames.json'
    records = json.loads(records_path.read_text())
    body_paths = {n:args.pack_cache/records[n]['brep'] for n in ('water-split','flow-regulator')}
    inputs = {str(p.resolve()):sha(p) for p in (args.box, records_path, *body_paths.values())}
    bodies = {n:cq.Shape.importBrep(str(p)) for n,p in body_paths.items()}
    pockets = assembly.flank_reliefs({n:(s,None) for n,s in bodies.items()})
    stations = [s for s in box.pack.tube_anchors
                if s[2] == (-1.,0.,0.) and abs(s[0][0]-assembly.SPLIT_COLUMN) < .01]
    if len(stations) != 2:
        raise ValueError(f'Expected split and regulator anchors; found {len(stations)}')
    roots = enc.piece_root_faces(box.inner, 'back', 'top')
    base = enc._ybox(box.outer[0], enc.back_top_flank_face()[0], box.y_joint,
                    box.inner[3], box.splits[1], box.inner[5])

    def anchors(stock):
        return enc._tube_anchors(stock, roots, box.inner, stations, box.y_joint,
                                 box.inner[3], box.splits[1], box.inner[5], up=-1.)

    wall = anchors(enc._flank_body_pockets(base,pockets))
    rows = []

    def maximum(name,value,limit=1e-5):
        row = {'check':name,'value':value,'maximum':limit,'pass':value <= limit}
        rows.append(row)
        print(('PASS ' if row['pass'] else 'FAIL ')+name+f': {value:.8g}',flush=True)

    def minimum(name,value,limit):
        row = {'check':name,'value':value,'minimum':limit,'pass':value >= limit-1e-6}
        rows.append(row)
        print(('PASS ' if row['pass'] else 'FAIL ')+name+f': {value:.8g}',flush=True)

    maximum('bounded wall is one valid solid',int(not wall.isValid())+abs(len(wall.Solids())-1),0)
    # The full generated rib, including stock inside the grown flank. A remote seed allows
    # the same native feature to be built without a wall that would hide a missing end root.
    seed = cq.Solid.makeBox(1.,1.,1.,cq.Vector(1000.,1000.,1000.))
    expected = anchors(seed).cut(seed)
    maximum('all complete native anchor stock is retained mm3',expected.cut(wall).Volume())
    for name,shape in bodies.items():
        maximum(name+' native body overlap mm3',shape.intersect(wall).Volume())
        minimum(name+' native bearing air mm',shape.distance(wall),assembly.BODY_ANCHOR_SLIP)
    pocket_wall = enc._flank_body_pockets(base,pockets)
    minimum('water-split pocket outside its anchor has running air mm',
            bodies['water-split'].distance(pocket_wall),enc.fits.running)
    for name,floor,face,*_ in pockets:
        minimum(name+' pocket leaves wall mm',floor-box.outer[0],enc.wall)

    details = []
    for i,station in enumerate(stations):
        mid,u,n,seat_r = station[:4]
        reach = seat_r+enc.wall
        b_root = mid[0]-box.inner[0]
        free = b_root-reach
        available = min(free,enc.tube_anchor_cavity_depth+enc.fits.supported_surface)
        minimum(f'anchor {i+1} tie passage fits its thickness mm',available,enc.tie_t)
        # Preserve the entire nominal 3 mm wall beneath the tie band, not only its ends.
        skin = enc._ybox(box.outer[0]+.01,box.inner[0]-.01,
                        mid[1]-enc.tie_w/2,mid[1]+enc.tie_w/2,
                        mid[2]-reach,mid[2]+reach)
        maximum(f'anchor {i+1} nominal wall missing mm3',skin.cut(wall).Volume())
        center_b = reach+available/2
        corridor = enc._ybox(mid[0]-center_b-enc.tie_t/2,mid[0]-center_b+enc.tie_t/2,
                             mid[1]-enc.tie_w/2,mid[1]+enc.tie_w/2,
                             mid[2]-reach-2.,mid[2]+reach+2.)
        maximum(f'anchor {i+1} straight tie threading overlap mm3',corridor.intersect(wall).Volume())
        for name,shape in bodies.items():
            maximum(f'anchor {i+1} tie threading / {name} overlap mm3',corridor.intersect(shape).Volume())
        # A clearance-shrunk rectangular plug covers the complete support-filled tunnel.
        # It can translate vertically out either mouth before fitting installation.
        tunnel = enc._ybox(mid[0]-reach-available+.01,mid[0]-reach-.01,
                          mid[1]-enc.tie_cav_w/2+.01,mid[1]+enc.tie_cav_w/2-.01,
                          mid[2]-reach-2.,mid[2]+reach+2.)
        maximum(f'anchor {i+1} open straight support-extraction corridor mm3',tunnel.intersect(wall).Volume())
        details.append({'station':station,'nominal_wall_mm':enc.wall,'passage_depth_mm':available,
                        'tie_width_mm':enc.tie_w,'tie_thickness_mm':enc.tie_t,
                        'tie_thickness_air_each_side_mm':(available-enc.tie_t)/2,
                        'shortest_closed_tie_loop_mm':enc.tube_anchor_tie_loop(seat_r)})
    water_split.clearance_seat(enc.tube_anchor_len,enc.tie_w)
    maximum('fixed split collar carries the complete tie width',0.,0.)
    # Clock the split's lock on its exposed +X crown. This is the same declared
    # 5 x 3.6 x 2.8 mm head envelope used by the carrier's 2.5 mm ties.
    mid,_,_,seat_r = stations[0][:4]
    body_r = seat_r-assembly.BODY_ANCHOR_SLIP
    head = enc._ybox(mid[0]+body_r,mid[0]+body_r+2.8,
                     mid[1]-1.8,mid[1]+1.8,mid[2]-2.5,mid[2]+2.5)
    tail = enc._ybox(mid[0]+body_r+.4,mid[0]+body_r+1.4,
                     mid[1]-enc.tie_w/2,mid[1]+enc.tie_w/2,
                     mid[2]+2.5,mid[2]+27.5)
    maximum('split tie head / bounded native wall overlap mm3',head.intersect(wall).Volume())
    maximum('split 25 mm straight tail-tension lane / wall overlap mm3',tail.intersect(wall).Volume())
    neighbor_rows = []
    for name,row in records.items():
        if name == 'water-split':
            continue
        bb = row['bbox']
        hb = tail.fuse(head).BoundingBox()
        if any(bb[axis+'max'] < getattr(hb,axis+'min')-.01
               or bb[axis+'min'] > getattr(hb,axis+'max')+.01 for axis in ('x','y','z')):
            continue
        path = args.pack_cache/row['brep']
        inputs[str(path.resolve())] = sha(path)
        shape = bodies.get(name)
        if shape is None:
            shape = cq.Shape.importBrep(str(path))
        h = head.intersect(shape).Volume()
        t = tail.intersect(shape).Volume()
        maximum('split tie head / '+name+' overlap mm3',h)
        maximum('split tail-tension lane / '+name+' overlap mm3',t)
        neighbor_rows.append({'name':name,'head_overlap_mm3':h,'tail_lane_overlap_mm3':t})
    for path,digest in inputs.items():
        if sha(path) != digest:
            raise ValueError('Native input changed during check: '+path)
    functions = (assembly.flank_reliefs,enc._flank_body_pockets,enc._tube_anchors,
                 enc._anchor_rib,enc._anchor_corbel,enc._anchor_column,
                 enc._anchor_bore,enc._supported_cut,water_split.clearance_seat)
    def function_source_digest(function):
        source = Path(function.__code__.co_filename).read_text()
        node = next(n for n in ast.parse(source).body
                    if isinstance(n,ast.FunctionDef) and n.name == function.__name__)
        return hashlib.sha256(ast.get_source_segment(source,node).encode()).hexdigest()

    record = {'created_at_utc':datetime.now(timezone.utc).isoformat(),
        'status':'pass' if all(r['pass'] for r in rows) else 'fail',
        'scope':'Bounded back-top west wall, actual placed split/regulator and declared anchor stations. Complete shell and unrelated pack neighbors are not tested here.',
        'assembly_current':False,'production_print_released':False,
        'input_sha256':inputs,'checker_sha256':sha(__file__),
        'loaded_function_bytecode_sha256':{f.__module__+'.'+f.__name__:hashlib.sha256(marshal.dumps(f.__code__)).hexdigest() for f in functions},
        'function_source_sha256':{f.__module__+'.'+f.__name__:function_source_digest(f) for f in functions},
        'pockets':pockets,'anchors':details,'checks':rows,
        'support_access':{'print_up':'-Z','opening_axis':'Z','removal_state':'Before split, regulator or tubing installation, with back-top separate.',
            'actual_slice_bodies_reviewed':False,'physical_cleanup_tested':False,
            'limit':'Native tunnel has two open mouths; production slicing must verify connected support branches do not obstruct that straight extraction lane.'},
        'tie_installation':{'water_split_required_closed_loop_mm':enc.tube_anchor_tie_loop(stations[0][3]),
            'length_selection':'Use the documented 6 inch 18 lb tie; the 4 inch tie closing circumference is too short for the split anchor.',
            'head_clocking':'Head on the exposed inboard crown, away from the wall and moving collets.',
            'head_envelope_mm':[2.8,3.6,5.0],
            'straight_tail_tension_lane_length_mm':25.,
            'head_and_tail_neighbor_readings':neighbor_rows,
            'provided_pack_head_and_tail_lane_verified':True,
            'complete_tool_body_and_physical_threading_verified':False}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    if not all(r['pass'] for r in rows):
        raise ValueError('One or more native flank checks failed')


if __name__ == '__main__':
    main()
