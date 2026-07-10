#!/usr/bin/env python3
"""topreach — is a TOP-layer trace between two pads even POSSIBLE? (global, not by-eye)

The mistake this kills: judging routability by the DIRECT path. "They cross the pocket" / "full cross"
is only ever a claim about the straight shot through the middle. Two nets do not cross if one takes the
long way — the perimeter moat, the connected ring of empty board outside every part. A top pour on a net
is one connected sheet that floods AROUND every obstacle; a 0.2 mm trace is just that sheet narrowed to a
thread. So the real question is topological: after eroding the top free-space by (half-trace + clearance)
— a morphological opening — do the two pads sit in the SAME connected component?

  - same component  -> a top trace EXISTS (go find the thread; don't drop to the bottom)
  - split, pads on opposite islands -> top is genuinely blocked (bottom is honest)

    topreach.py out/pcba.circuit.json U1.IO19 J5.IO19 [--png out.png]

Models foreign TOP copper (smtpads on top, top trace segments + width, the V12 top island), full-stack
copper (plated holes, vias), the board outline, and excludes the two query pads' own net. Approximate at
RES mm/px — a screening oracle, not a router. It does NOT yet model the WROOM antenna keepout (far west).
"""
import json, sys, argparse
import numpy as np
from scipy import ndimage

RES = 0.08          # mm per pixel
CLEAR = 0.16        # clearance floor (mm)
HALFW = 0.10        # half of a 0.2 mm trace (mm)
R = CLEAR + HALFW   # opening radius: a trace centre needs this much clear of foreign copper

def load(path):
    c = json.load(open(path))
    els = c if isinstance(c, list) else c.get("circuitJson", c)
    by = lambda t: [e for e in els if e.get("type") == t]
    scname = {s["source_component_id"]: s.get("name", "?") for s in by("source_component")}
    comp_name = {e["pcb_component_id"]: scname.get(e.get("source_component_id"), "?") for e in by("pcb_component")}
    sport = {s["source_port_id"]: s for s in by("source_port")}
    # net key per source_port (any source_trace touching it)
    port_key = {}
    for st in by("source_trace"):
        k = st.get("subcircuit_connectivity_map_key")
        for spid in st.get("connected_source_port_ids", []):
            port_key.setdefault(spid, k)
    pcbport = {p["pcb_port_id"]: p for p in by("pcb_port")}
    def net_of_pcbport(ppid):
        p = pcbport.get(ppid)
        return port_key.get(p["source_port_id"]) if p else None
    # locate a named "Comp.pad" pad -> its pcb feature + net
    def find_pad(anchor):
        comp, pad = anchor.split(".")
        for e in els:
            if e.get("type") in ("pcb_smtpad", "pcb_plated_hole") and comp_name.get(e.get("pcb_component_id")) == comp:
                hints = e.get("port_hints") or []
                labs = [sport.get(pcbport.get(e.get("pcb_port_id"), {}).get("source_port_id"), {}).get("port_hints", [])]
                allnames = set(hints) | set(labs[0] if labs else [])
                if pad in allnames:
                    return e
        raise SystemExit(f"pad {anchor} not found")
    return els, by, comp_name, pcbport, net_of_pcbport, find_pad

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("circuit"); ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--png")
    args = ap.parse_args()
    els, by, comp_name, pcbport, net_of, find_pad = load(args.circuit)

    board = by("pcb_board")[0]
    cx, cy = board["center"]["x"], board["center"]["y"]
    W, H = board["width"], board["height"]
    x0, y0 = cx - W / 2, cy - H / 2
    nx, ny = int(np.ceil(W / RES)) + 1, int(np.ceil(H / RES)) + 1
    def px(x, y): return (x - x0) / RES, (y - y0) / RES   # -> (col, row)

    pa, pb = find_pad(args.a), find_pad(args.b)
    exclude_nets = {net_of(pa.get("pcb_port_id")), net_of(pb.get("pcb_port_id"))} - {None}
    exclude_ids = {id(pa), id(pb)}

    XX, YY = np.meshgrid(np.arange(nx), np.arange(ny))     # col, row indices
    blocked = np.zeros((ny, nx), bool)

    def fill_rect(rx, ry, hw, hh, rot_deg):
        c, r = px(rx, ry)
        t = np.radians(rot_deg); cs, sn = np.cos(t), np.sin(t)
        dx, dy = (XX - c) * RES, (YY - r) * RES
        lx, ly = cs * dx + sn * dy, -sn * dx + cs * dy
        blocked[(np.abs(lx) <= hw) & (np.abs(ly) <= hh)] = True

    def fill_circle(rx, ry, rad):
        c, r = px(rx, ry)
        blocked[((XX - c) * RES) ** 2 + ((YY - r) * RES) ** 2 <= rad * rad] = True

    def fill_capsule(ax, ay, bx, by_, w):
        # thick segment: pixels within w/2 of segment ab
        ca, ra = px(ax, ay); cb, rb = px(bx, by_)
        pxs, pys = (XX - ca) * RES, (YY - ra) * RES
        vx, vy = (cb - ca) * RES, (rb - ra) * RES
        L2 = vx * vx + vy * vy
        tt = np.clip((pxs * vx + pys * vy) / L2, 0, 1) if L2 > 0 else np.zeros_like(pxs)
        dx, dy = pxs - tt * vx, pys - tt * vy
        blocked[dx * dx + dy * dy <= (w / 2) ** 2] = True

    def fill_poly(pts):
        # even-odd point-in-polygon over the whole grid
        gx, gy = x0 + XX * RES, y0 + YY * RES
        inside = np.zeros((ny, nx), bool)
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
            cond = ((y1 > gy) != (y2 > gy))
            xint = (x2 - x1) * (gy - y1) / (y2 - y1 + 1e-30) + x1
            inside ^= cond & (gx < xint)
        blocked[inside] = True

    for e in els:
        t = e.get("type")
        if t == "pcb_smtpad":
            if id(e) in exclude_ids or net_of(e.get("pcb_port_id")) in exclude_nets: continue
            if e.get("layer") != "top": continue
            w = e.get("width") or (e.get("radius", 0) * 2); h = e.get("height") or (e.get("radius", 0) * 2)
            fill_rect(e["x"], e["y"], w / 2, h / 2, e.get("ccw_rotation", 0))
        elif t == "pcb_plated_hole":
            if id(e) in exclude_ids or net_of(e.get("pcb_port_id")) in exclude_nets: continue
            w = e.get("outer_width") or e.get("outer_diameter") or e.get("hole_diameter") or 0.5
            h = e.get("outer_height") or e.get("outer_diameter") or e.get("hole_diameter") or w
            fill_rect(e["x"], e["y"], w / 2, h / 2, 0)
        elif t == "pcb_via":
            fill_circle(e["x"], e["y"], e.get("outer_diameter", 0.5) / 2)
        elif t == "pcb_trace":
            segs = e.get("route", [])
            for i in range(len(segs) - 1):
                p, q = segs[i], segs[i + 1]
                if p.get("route_type") == "via" or q.get("route_type") == "via": continue
                if p.get("layer") != "top" or q.get("layer") != "top": continue
                fill_capsule(p["x"], p["y"], q["x"], q["y"], p.get("width", 0.2))
        elif t == "pcb_copper_pour" and e.get("layer") == "top":
            # the V12 top island — a foreign top sheet unless it IS our net
            polys = e.get("polygons") or ([{"points": e.get("outline")}] if e.get("outline") else [])
            for poly in polys:
                pts = [(pt["x"], pt["y"]) for pt in (poly.get("points") or poly.get("vertices") or [])]
                if len(pts) >= 3: fill_poly(pts)

    # opening: dilate foreign copper by R, free centreline = board interior minus that
    rad_px = int(np.ceil(R / RES))
    yy, xx = np.ogrid[-rad_px:rad_px + 1, -rad_px:rad_px + 1]
    disk = (xx * xx + yy * yy) * RES * RES <= R * R
    blocked_d = ndimage.binary_dilation(blocked, structure=disk)
    interior = np.zeros((ny, nx), bool)
    m = int(np.ceil(HALFW / RES))
    interior[m:ny - m, m:nx - m] = True
    free = interior & ~blocked_d

    labels, _ = ndimage.label(free)

    def pad_labels(e):
        c, r = px(e["x"], e["y"])
        w = (e.get("width") or e.get("outer_width") or e.get("outer_diameter") or e.get("radius", 0.25) * 2)
        h = (e.get("height") or e.get("outer_height") or e.get("outer_diameter") or w)
        hw, hh = max(w, 0.4) / 2 / RES, max(h, 0.4) / 2 / RES
        sub = labels[max(0, int(r - hh)):int(r + hh) + 1, max(0, int(c - hw)):int(c + hw) + 1]
        return set(int(v) for v in np.unique(sub) if v > 0)

    la, lb = pad_labels(pa), pad_labels(pb)
    shared = la & lb
    ok = bool(shared)
    print(f"{args.a}  free-components at pad: {sorted(la) or 'NONE (boxed in)'}")
    print(f"{args.b}  free-components at pad: {sorted(lb) or 'NONE (boxed in)'}")
    print(f"\nTOP {'ROUTABLE' if ok else 'BLOCKED'} — pads {'share component ' + str(sorted(shared)) if ok else 'are on different islands (or a pad is boxed in)'}")

    # Show the THREAD: BFS through the free-space from pad A to pad B, then print a simplified
    # (mm) polyline so it can be turned into route() waypoints. The pour cannot make my local
    # mistake — it finds the way around, including the perimeter moat.
    path_px = None
    if ok:
        from collections import deque
        # Seed BFS from ALL free pixels inside pad A's own footprint, so the thread starts at the pad
        # and reveals the REAL escape (a snake up-and-around vs a clean corridor), then reaches pad B.
        def pad_free_pixels(e):
            c, r = px(e["x"], e["y"])
            w = (e.get("width") or e.get("outer_width") or e.get("outer_diameter") or e.get("radius", 0.25) * 2)
            h = (e.get("height") or e.get("outer_height") or e.get("outer_diameter") or w)
            hw, hh = max(w, 0.5) / 2 / RES, max(h, 0.5) / 2 / RES
            out = []
            for rr in range(max(0, int(r - hh)), min(ny, int(r + hh) + 1)):
                for cc in range(max(0, int(c - hw)), min(nx, int(c + hw) + 1)):
                    if free[rr, cc] and labels[rr, cc] in shared: out.append((rr, cc))
            return out
        seeds, goals = pad_free_pixels(pa), set(pad_free_pixels(pb))
        if seeds and goals:
            prev = {s: None for s in seeds}; q = deque(seeds); goal = None
            while q:
                cur = q.popleft()
                if cur in goals: goal = cur; break
                r, c = cur
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ny and 0 <= nc < nx and free[nr, nc] and (nr, nc) not in prev:
                        prev[(nr, nc)] = cur; q.append((nr, nc))
            if goal:
                chain = []; cur = goal
                while cur is not None: chain.append(cur); cur = prev[cur]
                chain.reverse(); path_px = chain
                # simplify: keep points where direction changes, sample ~every 2mm
                step = max(1, int(2.0 / RES)); pts = chain[::step] + [chain[-1]]
                mm = [(round(x0 + c * RES, 2), round(y0 + r * RES, 2)) for r, c in pts]
                print("thread (mm, approx, ~2mm samples):")
                print("  " + " -> ".join(f"({x},{y})" for x, y in mm))

    if args.png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        img = np.zeros((ny, nx, 3), np.uint8)
        img[blocked_d] = (60, 60, 60)         # foreign copper + clearance
        img[free] = (20, 60, 20)              # free centreline space
        # highlight the two pads' components
        for lab, col in ((la, (0, 200, 255)), (lb, (255, 200, 0))):
            for L in lab: img[labels == L] = col
        if path_px:
            for r, c in path_px:
                img[max(0, r - 1):r + 2, max(0, c - 1):c + 2] = (255, 0, 255)  # the thread, magenta
        for e, col in ((pa, (0, 255, 255)), (pb, (255, 255, 0))):
            c, r = px(e["x"], e["y"]);
            img[max(0,int(r-2)):int(r+3), max(0,int(c-2)):int(c+3)] = col
        plt.figure(figsize=(nx / 100, ny / 100), dpi=100)
        plt.imshow(img, origin="lower"); plt.axis("off"); plt.tight_layout(pad=0)
        plt.savefig(args.png, dpi=100); print(f"wrote {args.png}")

if __name__ == "__main__":
    main()
