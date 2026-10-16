"""Route native nonextruding shortcuts over the connected printed walls.

Manual experiment only. Model-outline routing retains every hole in the native
3MF's layer sections. The earlier bead-envelope mode is available to reproduce
its archived trial. Every E-command state and feed is retained. Startup,
shutdown and firmware interventions are outside scope.
"""
import heapq
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely import contains_xy
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from departure_lap import movements, MEMBER
from travel_survey import read, material, arc_xy


def safe_path(stock, start, end, pitch=.15, grid_clearance=.025):
    """Grid search followed by line-of-sight simplification inside material."""
    allowed = stock.buffer(.000001)
    if allowed.covers(LineString([start, end])):
        return [start, end]
    low = np.array(stock.bounds[:2]) - pitch
    high = np.array(stock.bounds[2:]) + pitch
    nx, ny = np.ceil((high-low)/pitch).astype(int) + 1
    xx, yy = np.meshgrid(low[0]+np.arange(nx)*pitch,
                         low[1]+np.arange(ny)*pitch)
    valid = contains_xy(stock.buffer(-grid_clearance), xx, yy)
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


def model_layer_outlines(source, moves):
    """Section the single connected native 3MF mesh in bed coordinates.

    Each section is at the midpoint of its printed layer. No hole-area cutoff
    or morphological filling is applied. This experiment uses one mesh owner.
    """
    import trimesh
    from sacrificial_web import solid, sections, Q

    production = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
    def transform(text):
        values = np.array([float(v) for v in text.split()])
        matrix = np.eye(4)
        matrix[:3,:3] = values[:9].reshape(3,3).T
        matrix[:3,3] = values[9:]
        return matrix

    with zipfile.ZipFile(source) as z:
        settings = json.loads(z.read("Metadata/project_settings.config"))
        root = ET.fromstring(z.read("3D/3dmodel.model"))
        items = root.findall(f"{Q('build')}/{Q('item')}")
        if len(items) != 1:
            raise ValueError("Model-outline routing requires one connected owner")
        item, = items
        owner = root.find(f"{Q('resources')}/{Q('object')}[@id='{item.get('objectid')}']")
        component, = owner.findall(f"{Q('components')}/{Q('component')}")
        child_path = component.get(f"{{{production}}}path").lstrip("/")
        child = ET.fromstring(z.read(child_path))
        mesh = child.find(f"{Q('resources')}/{Q('object')}[@id='{component.get('objectid')}']/{Q('mesh')}")
        vertices = [[float(v.get(k)) for k in "xyz"] for v in mesh.find(Q("vertices"))]
        faces = [[int(t.get(k)) for k in ("v1","v2","v3")] for t in mesh.find(Q("triangles"))]
        model = trimesh.Trimesh(vertices, faces, process=True)
        model.apply_transform(transform(item.get("transform")) @ transform(component.get("transform")))
    body = solid(model)
    heights = {m["layer"]:m["layer_z"] for m in moves if m["layer"] > 0}
    outlines, previous_z, planes = {},0.,{}
    for layer,z in sorted(heights.items()):
        plane = (previous_z+z)/2
        outlines[(layer,0)] = unary_union(sections(body,plane))
        planes[layer] = plane
        previous_z = z
    brim_width = float(settings.get("brim_width",0))
    if any(m["layer"] == 1 and m["feature"] == "Brim" for m in moves):
        if settings.get("brim_type") != "outer_only" or float(settings["brim_object_gap"]) != 0:
            raise ValueError("Connected first-layer routing requires an outer brim with zero object gap")
        first = outlines[(1,0)]
        islands = list(getattr(first,"geoms",[first]))
        holes = unary_union([Polygon(r) for p in islands for r in p.interiors]).difference(first)
        outlines[(1,0)] = unary_union([Polygon(p.exterior).buffer(brim_width)
                                      for p in islands]).difference(holes)
    return outlines, dict(native_mesh_member=child_path,
                          archive_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                          section_heights_mm=planes,
                          first_layer_outer_brim_width_mm=brim_width,
                          first_layer_brim_object_gap_mm=0,
                          hole_area_cutoff_mm2=None)


def route(source, output, report_path, model_outlines=False):
    with zipfile.ZipFile(source) as z:
        members = {n:z.read(n) for n in z.namelist()}
    native = members[MEMBER]
    lines = native.decode().splitlines(keepends=True)
    moves = list(movements(lines))
    photos = native.count(b"M9711")
    if photos:
        raise ValueError("Disable photo trips before routing walls")
    outline_record = None
    if model_outlines:
        stock, outline_record = model_layer_outlines(source,moves)
    else:
        runs, *_ = read(source)
        stock = {k:material(v) for k,v in runs.items()}
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
        keys = current_keys if model_outlines else current_keys | {
                (departure["layer"]-1,0),(arrival["layer"]-1,0)}
        cache_key = tuple(sorted(keys))
        if cache_key not in available_cache:
            current = unary_union([stock[k] for k in current_keys if k in stock])
            holes = unary_union([Polygon(r) for p in getattr(current,"geoms",[current])
                                 for r in p.interiors]).difference(current)
            available = unary_union([stock[k] for k in keys if k in stock])
            available_cache[cache_key] = (available, available if model_outlines
                                         else available.difference(holes))
        available, preferred = available_cache[cache_key]
        pts = [travel[0]["start"][:2]]
        for m in travel:
            w = m["words"]
            pts += (arc_xy(m["start"],m["end"],w.get("I",0),w.get("J",0),m["command"]=="G2")
                    if m["command"] in ("G2","G3") else [m["end"][:2]])
        line = LineString(pts)
        off = line.difference(preferred).length
        tested += 1
        if off <= (1e-5 if model_outlines else .03):
            maximum_off = max(maximum_off,line.difference(available).length)
            continue
        first,last = travel[0],travel[-1]
        if any("E" in m["words"] for m in moves[ia+1:ib]
               if first["index"] <= m["index"] <= last["index"]):
            raise ValueError("A travel contains an E command between XY moves")
        previous_floor = False
        try:
            # A clearance greater than half a grid diagonal prevents a grid
            # edge cutting across a concave boundary between valid nodes.
            path = safe_path(preferred,pts[0],pts[-1],
                             grid_clearance=.12 if model_outlines else .025)
        except ValueError as error:
            if model_outlines:
                raise ValueError(f"Layer {arrival['layer']}, line {first['index']+1}, "
                                 f"{departure['feature']} to {arrival['feature']}: {error}") from error
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
                  stock_scope=("Native 3MF material sections at each layer midpoint, retaining every hole. Same-layer travel uses only that layer; layer changes use the union of departing and arriving sections. The first layer includes its attached outer brim. No preceding-layer floor fallback. 0.00001 mm per-travel numerical length tolerance. Startup, shutdown and firmware interventions excluded. This tests the model's wall footprint, not the time order of deposited beads."
                               if model_outlines else "Union of departing, arriving and their preceding layers' emitted bead envelopes. Prefer avoiding current bore holes; newly exposed cavities may require travel over their printed preceding-layer floor. 0.03 mm per-travel numerical tolerance. Startup and shutdown excluded."),
                  layer_outline_source=outline_record,
                  routes=rows)
    report_path.write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({k:v for k,v in record.items() if k!="routes"},indent=2),flush=True)
    return record
