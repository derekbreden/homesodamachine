"""Join this finned elbow slice into layer tours; manual experiment, no sending.

Native deposition segments form a graph. Straight, visible links join nearby
paths; doubled links join components without adding plastic. Odd endpoints
are paired by visible straight links, with a shortest deposited return where
necessary. An Euler tour splices the existing printed paths together. Every
remaining bent transfer prints its links at layer height, including the bend.
"""
from collections import defaultdict
import hashlib
import heapq
import json
import math
from pathlib import Path
import zipfile

import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point

from departure_lap import MEMBER, movements
from travel_survey import arc_xy
from wall_travel import model_layer_outlines


class Graph:
    def __init__(self):
        self.points, self.lookup, self.edges, self.adj = [], {}, [], defaultdict(list)

    def node(self, p):
        p = tuple(round(float(x), 6) for x in p)
        if p not in self.lookup:
            self.lookup[p] = len(self.points)
            self.points.append(p)
        return self.lookup[p]

    def edge(self, a, b, **data):
        if a == b:
            return
        data.update(a=a, b=b, length=math.dist(self.points[a], self.points[b]))
        key = len(self.edges)
        self.edges.append(data)
        self.adj[a].append(key)
        self.adj[b].append(key)

    def components(self):
        labels, number = {}, 0
        for start in range(len(self.points)):
            if start in labels:
                continue
            stack, labels[start] = [start], number
            while stack:
                p = stack.pop()
                for key in self.adj[p]:
                    e = self.edges[key]
                    q = e['b'] if e['a'] == p else e['a']
                    if q not in labels:
                        labels[q] = number
                        stack.append(q)
            number += 1
        return labels, number


def visible(stock, a, b):
    return stock.covers(LineString([a, b]))


def connect(graph, stock):
    """Short straight links between deposited paths, retaining every hole."""
    labels, count = graph.components()
    native_components = count
    tree = cKDTree(graph.points)
    for neighbours in (12, 48, 192, len(graph.points)):
        if count == 1:
            break
        _, ids = tree.query(graph.points, k=min(neighbours, len(graph.points)))
        candidates = set()
        for a, row in enumerate(ids):
            for b in np.atleast_1d(row):
                b = int(b)
                if a != b and labels[a] != labels[b]:
                    candidates.add((min(a,b),max(a,b)))
        parent = list(range(count))
        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for a,b in sorted(candidates, key=lambda ab:math.dist(graph.points[ab[0]],graph.points[ab[1]])):
            aa,bb = root(labels[a]),root(labels[b])
            if aa == bb or not visible(stock,graph.points[a],graph.points[b]):
                continue
            # An out-and-back link preserves the native graph's parity.
            graph.edge(a,b,kind='travel',reason='component_link')
            graph.edge(a,b,kind='travel',reason='component_link')
            parent[aa] = bb
        labels,count = graph.components()
    if count != 1:
        raise ValueError(f'{count} deposition components cannot be joined by contained straight links')
    return native_components


def pair_ends(graph, stock):
    odd = {p for p,keys in graph.adj.items() if len(keys)%2}
    original_odd = len(odd)
    pairs = sorted((math.dist(graph.points[a],graph.points[b]),a,b)
                   for a in odd for b in odd if a < b)
    for _,a,b in pairs:
        if a in odd and b in odd and visible(stock,graph.points[a],graph.points[b]):
            graph.edge(a,b,kind='travel',reason='open_path_pair')
            odd.remove(a)
            odd.remove(b)
    duplicated = []
    while odd:
        start = min(odd)
        queue, costs, previous = [(0.,start)],{start:0.},{}
        while queue:
            cost,p = heapq.heappop(queue)
            if cost != costs[p]:
                continue
            if p != start and p in odd:
                end = p
                break
            for key in graph.adj[p]:
                e = graph.edges[key]
                q = e['b'] if e['a'] == p else e['a']
                # Minimise added deposition, then distance on existing links.
                nc = cost + (e['length'] if e['kind']=='native' else e['length']*.001)
                if nc < costs.get(q,math.inf):
                    costs[q],previous[q] = nc,(p,key)
                    heapq.heappush(queue,(nc,q))
        else:
            raise ValueError('An odd deposition endpoint is unreachable')
        p = end
        while p != start:
            before,key = previous[p]
            e = dict(graph.edges[key])
            a,b = e.pop('a'),e.pop('b')
            e.pop('length')
            if e['kind']=='native':
                e['kind'] = 'deposited_return'
            e['reason'] = 'odd_endpoint_return'
            graph.edge(a,b,**e)
            duplicated.append(len(graph.edges)-1)
            p = before
        odd.remove(start)
        odd.remove(end)
    return original_odd, duplicated


def tour(graph, start):
    # Hierholzer's algorithm. A native edge gets priority over a free link.
    choices = {p: sorted(keys,key=lambda k:(graph.edges[k]['kind']=='travel',graph.edges[k]['length']),
                         reverse=True) for p,keys in graph.adj.items()}
    used, stack, result = set(), [(start,None,None)], []
    while stack:
        p,_,_ = stack[-1]
        while choices[p] and choices[p][-1] in used:
            choices[p].pop()
        if choices[p]:
            key = choices[p].pop()
            used.add(key)
            e = graph.edges[key]
            q = e['b'] if e['a']==p else e['a']
            stack.append((q,key,p))
        else:
            q,key,p = stack.pop()
            if key is not None:
                result.append((key,p,q))
    result.reverse()
    if len(result) != len(graph.edges) or result[-1][2] != start:
        raise ValueError('Layer graph is not one Euler circuit')
    return result


def layer_graph(native_moves):
    g = Graph()
    for m in native_moves:
        w = m['words']
        pts = [m['start'][:2]]
        if m['command'] in ('G2','G3'):
            chord = min(.10,math.sqrt(8*math.hypot(w.get('I',0),w.get('J',0))*.0005))
            pts += arc_xy(m['start'],m['end'],w.get('I',0),w.get('J',0),m['command']=='G2',chord=chord)
        else:
            a,b = np.asarray(pts[0]),np.asarray(m['end'][:2])
            pts += [tuple(a+(b-a)*i/max(1,math.ceil(np.linalg.norm(b-a)/.25)))
                    for i in range(1,max(1,math.ceil(np.linalg.norm(b-a)/.25))+1)]
        lengths = [math.dist(a,b) for a,b in zip(pts,pts[1:])]
        total = sum(lengths)
        if total == 0:
            raise ValueError('Unexpected zero-length native deposition')
        for a,b,length in zip(pts,pts[1:],lengths):
            if length < 1e-9:
                continue
            e = w['E']*length/total
            feed = min(m['feed'],2.2*length/(e*math.pi*(1.75/2)**2)*60)
            g.edge(g.node(a),g.node(b),kind='native',e=e,
                   feed=feed,acceleration=m['acceleration'],feature=m['feature'],
                   width=m['width'],source_line=m['index']+1)
    return g


def prepare(source, output, report_path):
    source,output,report_path = map(Path,(source,output,report_path))
    with zipfile.ZipFile(source) as z:
        members = {n:z.read(n) for n in z.namelist()}
    raw = members[MEMBER]
    if hashlib.md5(raw).hexdigest() != members[MEMBER+'.md5'].decode().strip().lower():
        raise ValueError('Native checksum mismatch')
    if b'M9711' in raw:
        raise ValueError('Photo trips must be disabled')
    lines = raw.decode().splitlines(keepends=True)
    ms = list(movements(lines))
    acceleration, accelerations = None, {}
    for i,line in enumerate(lines):
        if line.startswith('M204 S'):
            acceleration = float(line.split('S',1)[1].split()[0])
        accelerations[i] = acceleration
    for m in ms:
        m['acceleration'] = accelerations[m['index']]
    native = [m for m in ms if m['layer']>0 and m['words'].get('E',-1)>0
              and math.dist(m['start'][:2],m['end'][:2])>1e-8]
    if not all(m['relative_e'] and m['absolute'] and abs(m['start'][2]-m['layer_z'])<1e-6
               and abs(m['end'][2]-m['layer_z'])<1e-6 for m in native):
        raise ValueError('Requires G90/M83 and planar native deposition')
    stock,outline_review = model_layer_outlines(source,ms)
    by_layer = defaultdict(list)
    for m in native:
        by_layer[m['layer']].append(m)
    body,rows = [],[]
    last_xy,last_z = native[0]['start'][:2],native[0]['start'][2]
    first_index,last_index = native[0]['index'],native[-1]['index']
    layer_markers = {}
    for i,line in enumerate(lines[:last_index+1]):
        if line.startswith('; CHANGE_LAYER'):
            layer_markers[len(layer_markers)+1] = i
    for layer,moves in sorted(by_layer.items()):
        shape = stock[(layer,0)]
        allowed = shape.buffer(1e-6)
        graph = layer_graph(moves)
        components = connect(graph,allowed)
        odd,duplicates = pair_ends(graph,allowed)
        # This point stays on the vertical joining sheet through all layers.
        candidates = sorted(range(len(graph.points)),key=lambda p:math.dist(graph.points[p],(177.5,160.)))
        start = next((p for p in candidates if layer==1 or visible(allowed,last_xy,graph.points[p])),None)
        if start is None:
            raise ValueError(f'No straight contained layer-change link at layer {layer}')
        path = tour(graph,start)
        # Collapse free links to their endpoint chord only when the chord stays
        # over material. Otherwise deposit the complete bent connection.
        emitted, pending, anchors = [],[],[]
        def flush():
            if not pending:
                return
            pts = [graph.points[pending[0][1]]] + [graph.points[q] for _,_,q in pending]
            if visible(allowed,pts[0],pts[-1]):
                if math.dist(pts[0],pts[-1])>1e-8:
                    emitted.append(dict(kind='travel',a=pts[0],b=pts[-1]))
            else:
                for key,p,q in pending:
                    a,b = graph.points[p],graph.points[q]
                    if math.dist(a,b)<1e-8:
                        continue
                    # Match normal rounded-rectangle bead area, 0.4 mm width.
                    h = .2 if layer==1 else .12
                    width = min(.4,2*shape.boundary.distance(LineString([a,b]))-.002)
                    if width < .25:
                        raise ValueError(f'Anchor too narrow at layer {layer}: {width}')
                    area = h*(width-h*(1-math.pi/4))
                    e = math.dist(a,b)*area*.96/(math.pi*(1.75/2)**2)
                    item = dict(kind='deposited_anchor',a=a,b=b,e=e,feed=600.,acceleration=5000.,
                                width=width,feature='Custom',source_line=0)
                    emitted.append(item)
                    anchors.append(item)
            pending.clear()
        for key,p,q in path:
            e = graph.edges[key]
            if e['kind']=='travel':
                pending.append((key,p,q))
            else:
                flush()
                emitted.append(dict(e,a=graph.points[p],b=graph.points[q]))
        flush()
        z = moves[0]['layer_z']
        if layer>1:
            body += [f'; CHANGE_LAYER\n; Z_HEIGHT: {z}\n; LAYER_HEIGHT: {z-last_z:.6f}\n',
                     f'; layer num/total_layer_count: {layer}/{len(by_layer)}\n',
                     f'M73 L{layer}\nM991 S0 P{layer-1}\n']
            # Retain the source's layer-specific temperature, fan and recovery commands.
            before = layer_markers[layer]
            for line in lines[before:moves[0]['index']]:
                if line.split(' ',1)[0] in ('M104','M106','M1003'):
                    body.append(line)
        body += [f'; DEPOSITED_LINKS_LAYER {layer}\n',f'; OBJECT_ID: 1901\n',
                 f'G1 Z{z:.6f} F600\n',f'G1 X{graph.points[start][0]:.6f} Y{graph.points[start][1]:.6f} F6000\n']
        current_feature,current_width,current_acceleration,current_source = None,None,None,None
        for item in emitted:
            a,b = item['a'],item['b']
            if item['kind']=='travel':
                # Straight travel at print height; its complete chord is contained.
                body.append(f'G1 X{b[0]:.6f} Y{b[1]:.6f} F6000\n')
                continue
            feature,width = item['feature'],item['width']
            if feature != current_feature:
                body.append(f'; FEATURE: {feature}\n')
                current_feature = feature
            if item['acceleration'] != current_acceleration:
                body.append(f'M204 S{item["acceleration"]:.0f}\n')
                current_acceleration = item['acceleration']
            if width != current_width:
                body.append(f'; LINE_WIDTH: {width:.6f}\n')
                current_width = width
            source_tag = (item['kind'],item['source_line'])
            if source_tag != current_source:
                body.append(f'; DEPOSITION_SOURCE: {source_tag[0]} {source_tag[1]}\n')
                current_source = source_tag
            body.append(f'G1 X{b[0]:.6f} Y{b[1]:.6f} E{item["e"]:.9f} F{item["feed"]:.3f}\n')
        native_e = sum(m['words']['E'] for m in moves)
        extra_e = sum(item.get('e',0) for item in emitted if item['kind']!='native')
        rows.append(dict(layer=layer,native_components=components,native_odd_endpoints=odd,
                         native_segments=len([e for e in graph.edges if e['kind']=='native']),
                         native_e_mm=native_e,added_e_mm=extra_e,
                         deposited_returns=len(duplicates),deposited_anchors=len(anchors),
                         added_volume_mm3=extra_e*math.pi*(1.75/2)**2,
                         added_nominal_bead_volume_mm3=extra_e*math.pi*(1.75/2)**2/.96,
                         deposited_return_length_mm=sum(e['length'] for e in graph.edges if e['kind']=='deposited_return'),
                         deposited_anchor_length_mm=sum(math.dist(a['a'],a['b']) for a in anchors),
                         straight_travels=sum(e['kind']=='travel' for e in emitted),
                         nominal_motion_seconds=sum((math.dist(e['a'],e['b'])/(100. if e['kind']=='travel' else e['feed']/60))
                                                    for e in emitted),
                         start_xy_mm=graph.points[start], end_xy_mm=graph.points[start]))
        last_xy,last_z = graph.points[start],z
        print(json.dumps({k:v for k,v in rows[-1].items() if k in ('layer','native_components','added_e_mm','deposited_anchors')}),flush=True)
    # Startup and shutdown remain native. The final native retraction and lift
    # act at the tour's final XY; no added final crossing goes through the bores.
    rewritten = (''.join(lines[:first_index])+''.join(body)+''.join(lines[last_index+1:])).encode()
    # Replace body progress at each layer using its nominal motion time. Native
    # startup/end progress and the archive's native timing metadata are retained.
    total_seconds = sum(r['nominal_motion_seconds'] for r in rows)
    completed = 0.
    for row in rows:
        marker = f'; DEPOSITED_LINKS_LAYER {row["layer"]}\n'.encode()
        progress = f'M73 P{min(99,int(100*completed/total_seconds))} R{math.ceil((total_seconds-completed)/60)}\n'.encode()
        rewritten = rewritten.replace(marker,marker+progress,1)
        completed += row['nominal_motion_seconds']
    members[MEMBER] = rewritten
    members[MEMBER+'.md5'] = hashlib.md5(rewritten).hexdigest().encode()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in members.items():
            z.writestr(name,data)
    record = dict(source=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  archive=output.name,archive_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  gcode_sha256=hashlib.sha256(rewritten).hexdigest(),layers=len(rows),
                  native_deposition_e_mm=sum(r['native_e_mm'] for r in rows),
                  added_deposition_e_mm=sum(r['added_e_mm'] for r in rows),
                  added_volume_mm3=sum(r['added_volume_mm3'] for r in rows),
                  added_nominal_bead_volume_mm3=sum(r['added_nominal_bead_volume_mm3'] for r in rows),
                  deposited_anchors=sum(r['deposited_anchors'] for r in rows),
                  deposited_return_length_mm=sum(r['deposited_return_length_mm'] for r in rows),
                  deposited_anchor_length_mm=sum(r['deposited_anchor_length_mm'] for r in rows),
                  nominal_part_motion_seconds=total_seconds,
                  outline_source=outline_review,layer_review=rows)
    report_path.write_text(json.dumps(record,indent=2)+'\n')
    return record


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--report',required=True,type=Path)
    args = parser.parse_args()
    prepare(args.source,args.output,args.report)
