#!/usr/bin/env python3
"""trace-check — what actually intersects what, by geometry, not by eye.

The clearance DRC reports a violation by the two traces' END pads ("trace A..B overlaps trace C..D");
it does not say WHICH segment of a multi-bend hand trace is at fault, where, or whether the other
party is your own copper (fix your route), a foreign pad (nudge off it), or an autorouter trace
(evict its net). This does.

    trace-check.py out/pcba.circuit.json pcba.tsx --region -60 -42 17 32
    trace-check.py out/pcba.circuit.json pcba.tsx --net "U13 > .DTR"

For every hand-authored trace touching the filter, it prints each sub-floor approach: the exact
segment of your trace, what it hits (a segment of another net — flagged AUTO/hand — or a pad
comp.pin), the gap, and the point. The tail groups fouls by other-net with a verdict: an AUTO net is
`evict`; a hand net or pad is `fix`. Vias are full-stack; a trace segment near a foreign via is
reported like a pad. Copper on different layers never conflicts — with one exception: a pad's
footprint projects through the ENTIRE stack (plane stitches and pad-via-to-pad-via both land a
barrel in it), so a cross-layer approach inside a foreign pad's outline reports as `shadow`, same
floor. clearance.ts gates the same rule as `pad-shadow` errors.
"""
import json, sys, argparse, math

def seg_pt_dist(ax, ay, bx, by, px, py):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy), cx, cy

def seg_seg(a, b, c, d):
    """Min distance between segments ab and cd, and the closest point on ab."""
    def cross(ox, oy, ax, ay, bx, by): return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)
    d1 = cross(c[0], c[1], d[0], d[1], a[0], a[1]); d2 = cross(c[0], c[1], d[0], d[1], b[0], b[1])
    d3 = cross(a[0], a[1], b[0], b[1], c[0], c[1]); d4 = cross(a[0], a[1], b[0], b[1], d[0], d[1])
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        # proper crossing — find the intersection point on ab
        t = d3 / (d3 - d4) if (d3 - d4) else 0.0
        return 0.0, (c[0] + t * (d[0] - c[0]), c[1] + t * (d[1] - c[1]))
    best = (1e9, (0, 0))
    for (px, py) in (c, d):
        g, cx, cy = seg_pt_dist(a[0], a[1], b[0], b[1], px, py)
        if g < best[0]: best = (g, (cx, cy))
    for (px, py) in (a, b):
        g, cx, cy = seg_pt_dist(c[0], c[1], d[0], d[1], px, py)
        if g < best[0]: best = (g, (px, py))
    return best

def seg_rect_dist(a, b, rx, ry, hw, hh, rot_deg=0):
    """Min distance from segment ab to a rect centred (rx,ry), half (hw,hh), rotated ccw rot_deg.
    Sample the segment; rotate each sample into the pad's own frame so the rect is axis-aligned
    (exact for rectangles; a slight over-estimate for pills, i.e. conservative)."""
    t = -math.radians(rot_deg); cs, sn = math.cos(t), math.sin(t)
    best = 1e9
    n = max(24, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 0.35) + 1)  # step ≤ 0.35 mm so no pad slips between samples
    for k in (i / n for i in range(n + 1)):
        px, py = a[0] + k * (b[0] - a[0]) - rx, a[1] + k * (b[1] - a[1]) - ry
        lx, ly = cs * px - sn * py, sn * px + cs * py
        ddx, ddy = max(abs(lx) - hw, 0), max(abs(ly) - hh, 0)
        best = min(best, math.hypot(ddx, ddy))
    return best

def load(circuit_path, tsx_path):
    c = json.load(open(circuit_path))
    by = lambda t: [e for e in c if e["type"] == t]
    scomp = {s["source_component_id"]: s.get("name", "?") for s in by("source_component")}
    comp_name = {e["pcb_component_id"]: scomp.get(e.get("source_component_id"), "?") for e in by("pcb_component")}
    sport = {s["source_port_id"]: s for s in by("source_port")}
    strace = {s["source_trace_id"]: s for s in by("source_trace")}
    # net key per pcb_port: the connectivity-map key of any source_trace touching its source_port
    port_key = {}
    for st in by("source_trace"):
        k = st.get("subcircuit_connectivity_map_key")
        for spid in st.get("connected_source_port_ids", []):
            port_key.setdefault(spid, k)
    def pcbport_net(ppid):
        pp = next((p for p in by("pcb_port") if p["pcb_port_id"] == ppid), None)
        return port_key.get(pp["source_port_id"]) if pp else None
    # hand-authored connections from source (pcbPath/pcbComb/pcbStraightLine, comment-stripped)
    src = open(tsx_path).read()
    import re
    live = re.sub(r"/\*[\s\S]*?\*/", "", src)
    authored = set()
    for tag in re.findall(r"<trace\b[^<]*?/>", live):
        if not re.search(r"\b(pcbPath|pcbComb|pcbStraightLine)\b", tag): continue
        f = re.search(r'from="([^"]*)"', tag); t = re.search(r'to="([^"]*)"', tag)
        if f and t: authored.add(frozenset((f.group(1).replace(" ", "").replace(".", "").replace(">", ""),
                                             t.group(1).replace(" ", "").replace(".", "").replace(">", ""))))
    def is_authored(disp):
        m = re.match(r"(.+) to (.+)", disp or "")
        if not m: return False
        norm = lambda s: s.replace(" ", "").replace(".", "").replace(">", "")
        return frozenset((norm(m.group(1)), norm(m.group(2)))) in authored
    # trace segments (via-aware: copper leaving a via is on its to_layer)
    traces = []
    for tr in by("pcb_trace"):
        st = strace.get(tr.get("source_trace_id"), {})
        disp = st.get("display_name", tr.get("source_trace_id", "?"))
        key = st.get("subcircuit_connectivity_map_key", disp)
        segs = []
        rt = tr["route"]
        for i in range(len(rt) - 1):
            p, q = rt[i], rt[i + 1]
            if p.get("x") is None or q.get("x") is None: continue
            if p["x"] == q["x"] and p["y"] == q["y"]: continue
            layer = (p.get("to_layer") if p.get("route_type") == "via"
                     else q.get("from_layer") if q.get("route_type") == "via"
                     else p.get("layer") if p.get("layer") == q.get("layer") else None)
            if layer: segs.append(((p["x"], p["y"]), (q["x"], q["y"]), layer, p.get("width", 0.2)))
        traces.append({"disp": disp, "key": key, "auth": is_authored(disp), "segs": segs})
    # pads (smt + plated holes) and vias
    pads = []
    for sp in by("pcb_smtpad"):
        nm = comp_name.get(sp["pcb_component_id"], "?")
        hint = (sp.get("port_hints") or ["?"])[0]
        pads.append({"name": f"{nm}.{hint}", "x": sp["x"], "y": sp["y"],
                     "hw": sp.get("width", 0) / 2, "hh": sp.get("height", 0) / 2, "rot": sp.get("ccw_rotation", 0),
                     "layers": [sp.get("layer")], "net": pcbport_net(sp.get("pcb_port_id"))})
    for ph in by("pcb_plated_hole"):
        nm = comp_name.get(ph.get("pcb_component_id"), "?")
        hint = (ph.get("port_hints") or ["?"])[0]
        r = ph.get("outer_diameter", ph.get("radius", 0.5) * 2) / 2
        pads.append({"name": f"{nm}.{hint}", "x": ph["x"], "y": ph["y"], "hw": r, "hh": r,
                     "rot": 0, "layers": ["top", "bottom", "inner1", "inner2"],
                     "net": pcbport_net(ph.get("pcb_port_id"))})
    for v in by("pcb_via"):
        r = v.get("outer_diameter", 0.5) / 2
        pads.append({"name": "via", "x": v["x"], "y": v["y"], "hw": r, "hh": r, "rot": 0,
                     "layers": ["top", "bottom", "inner1", "inner2", "inner3", "inner4"],
                     "net": v.get("subcircuit_connectivity_map_key")})
    return traces, pads

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("circuit"); ap.add_argument("tsx")
    ap.add_argument("--region", nargs=4, type=float, metavar=("X0", "X1", "Y0", "Y1"))
    ap.add_argument("--net", help="substring of a trace display_name to focus on")
    ap.add_argument("--floor", type=float, default=0.14)
    a = ap.parse_args()
    traces, pads = load(a.circuit, a.tsx)

    def seg_in(s):
        (ax, ay), (bx, by), _, _ = s
        if a.region:
            x0, x1, y0, y1 = a.region
            if max(ax, bx) < min(x0, x1) or min(ax, bx) > max(x0, x1): return False
            if max(ay, by) < min(y0, y1) or min(ay, by) > max(y0, y1): return False
        return True
    def trace_in(t):
        if a.net:  # explicit net filter targets any trace, authored or not
            return a.net.replace(" ", "") in t["disp"].replace(" ", "")
        # a bare region sweep focuses on MY hand copper — what the autorouter foul is against
        return t["auth"] and any(seg_in(s) for s in t["segs"])

    focus = [t for t in traces if trace_in(t)]
    if not focus:
        print("no matching hand traces"); return
    findings = []
    for t in focus:
        for s in t["segs"]:
            if a.region and not seg_in(s): continue
            (ax, ay), (bx, by), layer, w = s
            half = w / 2
            for u in traces:
                if u is t or u["key"] == t["key"]: continue
                for s2 in u["segs"]:
                    if s2[2] != layer: continue
                    g, pt = seg_seg((ax, ay), (bx, by), s2[0], s2[1])
                    gap = g - half - s2[3] / 2
                    if gap < a.floor:
                        findings.append((gap, "trace", t, s, u["disp"], u["auth"], u["key"], s2, pt))
            for pd in pads:
                if pd["net"] is not None and pd["net"] == t["key"]: continue
                # cross-layer only ever reaches here for a single-layer pad (vias/holes span every
                # layer): that's the pad's through-stack SHADOW — via-in-pad territory
                shadow = layer not in pd["layers"]
                g = seg_rect_dist((ax, ay), (bx, by), pd["x"], pd["y"], pd["hw"], pd["hh"], pd.get("rot", 0))
                gap = g - half
                if gap < a.floor:
                    findings.append((gap, "shadow" if shadow else "pad", t, s, pd["name"], False, pd["net"], None, (pd["x"], pd["y"])))
    findings.sort(key=lambda f: f[0])
    print(f"# {len(focus)} hand trace(s) in filter; floor {a.floor} mm\n")
    for gap, kind, t, s, other, auth, okey, s2, pt in findings:
        seg = f"({s[0][0]:.2f},{s[0][1]:.2f})->({s[1][0]:.2f},{s[1][1]:.2f}) {s[2]}"
        where = f"@({pt[0]:.2f},{pt[1]:.2f})"
        if kind == "trace":
            tag = "AUTO" if not auth else "hand"
            print(f"{gap:+.3f}mm  MINE [{t['disp']}] seg {seg}")
            print(f"          x {tag} [{other}] {where}")
        elif kind == "shadow":
            print(f"{gap:+.3f}mm  MINE [{t['disp']}] seg {seg}")
            print(f"          x SHADOW of pad {other} {where} (cross-layer: its column is via territory)")
        else:
            print(f"{gap:+.3f}mm  MINE [{t['disp']}] seg {seg}")
            print(f"          x pad {other} {where}")
    # verdicts grouped by other party
    print("\n# by other party:")
    grp = {}
    for gap, kind, t, s, other, auth, okey, s2, pt in findings:
        if kind == "trace":
            k = (other, "AUTO" if not auth else "hand")
        elif kind == "shadow":
            k = (f"pad {other}", "shadow")
        else:
            k = (f"pad {other}", "pad")
        g = grp.setdefault(k, [1e9, 0]); g[0] = min(g[0], gap); g[1] += 1
    for (name, cls), (worst, n) in sorted(grp.items(), key=lambda kv: kv[1][0]):
        verdict = ("EVICT its net" if cls == "AUTO" else "fix your trace" if cls == "hand"
                   else "leave its column — pad projects through the stack" if cls == "shadow" else "nudge off pad")
        print(f"  {worst:+.3f}mm x{n}  [{name}] ({cls}) -> {verdict}")

if __name__ == "__main__":
    main()
