"""Route native nonextruding shortcuts over the connected printed walls.

Manual experiment only. The available stock is the union of the departing,
arriving and preceding layers' emitted beads. Every E-command state and feed
is retained. Startup, shutdown and firmware interventions are outside scope.
"""
import heapq
import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile

import numpy as np
from shapely import contains_xy
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from departure_lap import movements, MEMBER
from travel_survey import read, material, arc_xy


def safe_path(stock, start, end, pitch=.15):
    """Grid search followed by line-of-sight simplification inside bead stock."""
    allowed = stock.buffer(.000001)
    if allowed.covers(LineString([start, end])):
        return [start, end]
    low = np.array(stock.bounds[:2]) - pitch
    high = np.array(stock.bounds[2:]) + pitch
    nx, ny = np.ceil((high-low)/pitch).astype(int) + 1
    xx, yy = np.meshgrid(low[0]+np.arange(nx)*pitch,
                         low[1]+np.arange(ny)*pitch)
    valid = contains_xy(stock.buffer(-.025), xx, yy)
    def anchor(p):
        ix, iy = np.rint((np.array(p)-low)/pitch).astype(int)
        choices = []
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                x,y = ix+dx,iy+dy
                if 0 <= x < nx and 0 <= y < ny and valid[y,x]:
                    q = (xx[y,x],yy[y,x])
                    if allowed.covers(LineString([p,q])):
                        choices.append((math.dist(p,q),(int(x),int(y))))
        if not choices:
            raise ValueError(f"No wall-grid anchor for {p}; distance {stock.distance(Point(p))}")
        return min(choices)[1]
    a,b = anchor(start),anchor(end)
    queue, costs, previous = [(math.dist(a,b),0.,a)], {a:0.}, {}
    found = False
    while queue:
        _,cost,p = heapq.heappop(queue)
        if cost != costs[p]:
            continue
        if p == b:
            found = True
            break
        x,y = p
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            u,v = x+dx,y+dy
            if not (0 <= u < nx and 0 <= v < ny and valid[v,u]):
                continue
            if dx and dy and not (valid[y,u] and valid[v,x]):
                continue
            q, nc = (u,v),cost+math.hypot(dx,dy)
            if nc < costs.get(q,float("inf")):
                costs[q],previous[q] = nc,p
                heapq.heappush(queue,(nc+math.dist(q,b),nc,q))
    if not found:
        raise ValueError("No connected wall route on emitted beads")
    nodes, p = [b],b
    while p != a:
        p = previous[p]
        nodes.append(p)
    path = [start]+[(xx[y,x],yy[y,x]) for x,y in reversed(nodes)]+[end]
    out, i = [path[0]],0
    while i < len(path)-1:
        j = len(path)-1
        while j > i+1 and not allowed.covers(LineString([path[i],path[j]])):
            j -= 1
        out.append(path[j]);i=j
    if not allowed.covers(LineString(out)):
        raise ValueError("Simplified route leaves wall stock")
    return out


def route(source, output, report_path):
    runs, _, photos, *_ = read(source)
    if photos:
        raise ValueError("Disable photo trips before routing walls")
    stock = {k:material(v) for k,v in runs.items()}
    with zipfile.ZipFile(source) as z:
        members = {n:z.read(n) for n in z.namelist()}
    native = members[MEMBER]
    lines = native.decode().splitlines(keepends=True)
    moves = list(movements(lines))
    extrusions = [i for i,m in enumerate(moves) if m["layer"] > 0
                  and m["words"].get("E",-1) >= 0
                  and ("X" in m["words"] or "Y" in m["words"])]
    replacements, deleted, rows, available_cache = {},set(),[],{}
    tested, maximum_off = 0,0.
    for ia,ib in zip(extrusions,extrusions[1:]):
        departure,arrival = moves[ia],moves[ib]
        travel = [m for m in moves[ia+1:ib]
                  if "X" in m["words"] or "Y" in m["words"]
                  or m["command"] in ("G2","G3")]
        if not travel:
            continue
        current_keys = {(departure["layer"],0),(arrival["layer"],0)}
        keys = current_keys | {
                (departure["layer"]-1,0),(arrival["layer"]-1,0)}
        cache_key = tuple(sorted(keys))
        if cache_key not in available_cache:
            current = unary_union([stock[k] for k in current_keys if k in stock])
            holes = unary_union([Polygon(r) for p in getattr(current,"geoms",[current])
                                 for r in p.interiors]).difference(current)
            available = unary_union([stock[k] for k in keys if k in stock])
            available_cache[cache_key] = available, available.difference(holes)
        available, preferred = available_cache[cache_key]
        pts = [travel[0]["start"][:2]]
        for m in travel:
            w = m["words"]
            pts += (arc_xy(m["start"],m["end"],w.get("I",0),w.get("J",0),m["command"]=="G2")
                    if m["command"] in ("G2","G3") else [m["end"][:2]])
        line = LineString(pts)
        off = line.difference(preferred).length
        tested += 1
        if off <= .03:
            maximum_off = max(maximum_off,line.difference(available).length)
            continue
        first,last = travel[0],travel[-1]
        if any("E" in m["words"] for m in moves[ia+1:ib]
               if first["index"] <= m["index"] <= last["index"]):
            raise ValueError("A travel contains an E command between XY moves")
        previous_floor = False
        try:
            path = safe_path(preferred,pts[0],pts[-1])
        except ValueError:
            # A new cavity can expose disconnected skin paths over a fully
            # printed preceding-layer floor. That floor remains printed stock.
            path = safe_path(available,pts[0],pts[-1])
            previous_floor = True
        full_z = max(first["start"][2],last["end"][2],
                     departure["layer_z"]+.4,arrival["layer_z"]+.4)
        feed = min(6000.,min(m["feed"] for m in travel))
        block = [f"; WALL_ROUTE layer={arrival['layer']}\n",
                 f"G1 Z{full_z:.6f} F600\n"]
        block += [f"G1 X{x:.6f} Y{y:.6f} F{feed:.3f}\n" for x,y in path[1:]]
        block += [f"G1 Z{last['end'][2]:.6f} F600\n",
                  f"G1 F{last['feed']:.3f}\n"]
        replacements[first["index"]] = block
        deleted.update(m["index"] for m in travel)
        rows.append(dict(layer=arrival["layer"],source_first_line=first["index"]+1,
                         source_last_line=last["index"]+1,
                         native_xy_mm=line.length,native_off_stock_mm=off,
                         routed_xy_mm=LineString(path).length,route_xy_mm=path,
                         routed_off_stock_mm=LineString(path).difference(available).length,
                         uses_preceding_layer_floor_at_new_cavity=previous_floor,
                         travel_z_mm=full_z,travel_speed_mm_s=feed/60))
    rewritten = "".join("".join(replacements.get(i,[])) + (raw if i not in deleted else "")
                        for i,raw in enumerate(lines)).encode()
    original_e = [(m["raw"],m["start"],m["end"],m["feed"])
                  for m in moves if "E" in m["words"]]
    changed_e = [(m["raw"],m["start"],m["end"],m["feed"])
                 for m in movements(rewritten.decode().splitlines(keepends=True)) if "E" in m["words"]]
    if original_e != changed_e:
        mismatch = next((a,b) for a,b in zip(original_e,changed_e) if a != b)
        raise ValueError(f"An E-command position or feed changed: {mismatch}")
    members[MEMBER] = rewritten
    members[MEMBER+".md5"] = hashlib.md5(rewritten).hexdigest().encode()
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as z:
        for n,data in members.items():z.writestr(n,data)
    record = dict(source=source.name,archive=output.name,
                  archive_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  gcode_sha256=hashlib.sha256(rewritten).hexdigest(),
                  travels_assessed=tested,travels_rerouted=len(rows),
                  all_e_command_states_and_feeds_unchanged=True,e_commands=len(original_e),
                  unchanged_travel_max_off_stock_mm=maximum_off,
                  routed_travel_max_off_stock_mm=max((r["routed_off_stock_mm"] for r in rows),default=0.),
                  photo_trip_commands=0,wall_grid_pitch_mm=.15,
                  routes_using_preceding_layer_floor=sum(r["uses_preceding_layer_floor_at_new_cavity"] for r in rows),
                  stock_scope="Union of departing, arriving and their preceding layers' emitted bead envelopes. Prefer avoiding current bore holes; newly exposed cavities may require travel over their printed preceding-layer floor. 0.03 mm per-travel numerical tolerance. Startup and shutdown excluded.",
                  routes=rows)
    report_path.write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({k:v for k,v in record.items() if k!="routes"},indent=2),flush=True)
    return record
