#!/usr/bin/env python3
"""Silkscreen legibility + DFM audit: no label ink on bare copper, no silk clobbered by silk.

Silk printed onto an exposed copper pad is a fab defect — it fouls solder wetting and many
fabs shave it off anyway, so the label just vanishes. Every pad on this board is bare copper
(`is_covered_with_solder_mask: false`), so ANY silkscreen text stroke that lands on a pad is a
problem; silk over a soldermasked trace is fine and is NOT flagged. This checks three things:

  SILK-ON-BARE-COPPER  a text stroke's ink touches an exposed pad / plated-hole ring. Checked on
                       BOTH sides: the front legend against front copper, and the mirrored back
                       legend (bottom-silk.ts copies every label to the bottom at the same anchor)
                       against the bottom copper (the through-hole rings).
  SILK-ON-SILK-PATH    a label's ink crosses a component outline / fence stroke (illegible).
  SILK-ON-SILK-TEXT    two labels' ink overlap (illegible).

The geometry is the REAL fab geometry, not an approximation: it reproduces circuit-json-to-gerber's
`renderVectorText` exactly — the same Hershey stroke font (read straight out of the installed
package, so it can't drift), the same CAP_HEIGHT_SCALE 0.7, 0.3·em letter-spacing, per-glyph
advances, anchor alignment, rotation, and mirror. A label's strokes here are byte-for-byte the
polylines in F_SilkScreen.gbr. Stroke ink half-width is font_size/8/2 (the gerber aperture).

Pads are modelled as filled shapes (capsule / circle / rotated rect), so a glyph sitting fully
INSIDE a big thermal pad is caught (an edge-distance test alone would miss it).

    tools/cad-venv/bin/python silk-audit.py [out/pcba.circuit.json]   # PIL not required

Exits non-zero if anything lands on copper (so it can gate a build); silk-on-silk is reported
but does not fail the run (legibility, not manufacturability).
"""
import json, math, sys, os, glob, re

CIRCUIT = next((a for a in sys.argv[1:] if a.endswith(".json")), "out/pcba.circuit.json")

# ---- the Hershey stroke font, read from the gerber generator itself ---------------------------
# circuit-json-to-gerber embeds `const HERSHEY = {...}` in a hashed chunk; parse it so this audit
# always measures the exact glyphs the fab will draw, even if the fork bumps the font.
def load_hershey():
    for f in glob.glob(os.path.join(os.path.dirname(__file__),
                                    "node_modules/circuit-json-to-gerber/dist/*.js")):
        s = open(f).read()
        i = s.find("const HERSHEY = {")
        if i == -1:
            continue
        lit = s[i + len("const HERSHEY = "): s.index("};", i) + 1]
        return json.loads(lit.replace('\'"\':', '"\\"":'))  # only the '"' key is non-JSON
    sys.exit("silk-audit: could not find the HERSHEY font in circuit-json-to-gerber")

HERSHEY = load_hershey()
CAP = 0.7  # circuit-json-to-gerber CAP_HEIGHT_SCALE

# ---- geometry primitives ----------------------------------------------------------------------
def seg_seg(p1, p2, p3, p4):
    """min distance between segments p1p2 and p3p4 (0 if they cross)."""
    d1x, d1y = p2[0]-p1[0], p2[1]-p1[1]
    d2x, d2y = p4[0]-p3[0], p4[1]-p3[1]
    rx, ry = p1[0]-p3[0], p1[1]-p3[1]
    a = d1x*d1x + d1y*d1y; e = d2x*d2x + d2y*d2y; f = d2x*rx + d2y*ry
    E = 1e-12; cl = lambda v: max(0.0, min(1.0, v))
    if a <= E and e <= E: return math.hypot(rx, ry)
    if a <= E: s = 0.0; t = cl(f/e)
    else:
        c = d1x*rx + d1y*ry
        if e <= E: t = 0.0; s = cl(-c/a)
        else:
            b = d1x*d2x + d1y*d2y; den = a*e - b*b
            s = cl((b*f - c*e)/den) if den > E else 0.0
            t = (b*s + f)/e
            if t < 0: t = 0.0; s = cl(-c/a)
            elif t > 1: t = 1.0; s = cl((b-c)/a)
    return math.hypot(p1[0]+d1x*s-(p3[0]+d2x*t), p1[1]+d1y*s-(p3[1]+d2y*t))

def dist_pt_seg(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; L = dx*dx + dy*dy
    if L <= 1e-12: return math.hypot(p[0]-a[0], p[1]-a[1])
    t = max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/L))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))

# ---- pad model: capsule(seg+r) | circle(pt+r) | rect(cx,cy,w,h,deg) ----------------------------
def pad_shape(e):
    if e["type"] == "pcb_smtpad":
        shp = e["shape"]
        if shp in ("rect", "rotated_rect"):
            return ("rect", (e["x"], e["y"], e["width"], e["height"], e.get("ccw_rotation", 0) or 0))
        if shp == "circle":
            return ("circle", (e["x"], e["y"]), e.get("radius") or e["width"]/2)
        w, h = e["width"], e["height"]; r = e.get("radius") or min(w, h)/2
    else:  # pcb_plated_hole
        if e["shape"] == "circle":
            return ("circle", (e["x"], e["y"]), e["outer_diameter"]/2)
        w, h = e["outer_width"], e["outer_height"]; r = min(w, h)/2
    half = max(0.0, (max(w, h) - 2*r)/2)
    ang = math.radians((90 if h >= w else 0) + (e.get("ccw_rotation", 0) or 0))
    c1 = (e["x"]-math.cos(ang)*half, e["y"]-math.sin(ang)*half)
    c2 = (e["x"]+math.cos(ang)*half, e["y"]+math.sin(ang)*half)
    return ("capsule", c1, c2, r)

def pad_bbox(sh):
    if sh[0] == "rect":
        cx, cy, w, h, _ = sh[1]; rr = math.hypot(w, h)/2
        return cx-rr, cx+rr, cy-rr, cy+rr
    if sh[0] == "circle":
        (cx, cy), r = sh[1], sh[2]; return cx-r, cx+r, cy-r, cy+r
    c1, c2, r = sh[1], sh[2], sh[3]
    return min(c1[0],c2[0])-r, max(c1[0],c2[0])+r, min(c1[1],c2[1])-r, max(c1[1],c2[1])+r

def signed_inside(p, sh):
    """+ve = p is this far INSIDE the pad copper; -ve = this far outside."""
    if sh[0] == "circle":
        (cx, cy), r = sh[1], sh[2]; return r - math.hypot(p[0]-cx, p[1]-cy)
    if sh[0] == "capsule":
        return sh[3] - dist_pt_seg(p, sh[1], sh[2])
    cx, cy, w, h, deg = sh[1]; a = math.radians(deg); c = math.cos(a); s = math.sin(a)
    lx = (p[0]-cx)*c + (p[1]-cy)*s; ly = -(p[0]-cx)*s + (p[1]-cy)*c
    dx = abs(lx)-w/2; dy = abs(ly)-h/2
    return -(math.hypot(max(dx, 0.0), max(dy, 0.0)) + min(max(dx, dy), 0.0))

def seg_pad_pen(a, b, rs, sh):
    """max penetration of a silk stroke (a-b, ink radius rs) into pad copper. >0 => ink on copper."""
    best = -1e9; n = max(1, int(math.ceil(math.hypot(b[0]-a[0], b[1]-a[1]) / 0.03)))
    for i in range(n+1):
        t = i/n; p = (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
        best = max(best, signed_inside(p, sh) + rs)
    return best

# ---- silk text -> stroke segments (reproduce renderVectorText) --------------------------------
def text_strokes(el, force_mirror=None):
    """(segments[(a,b)], ink_radius, bbox). force_mirror models the mirrored back-side copy."""
    fs = el["font_size"] * CAP; ls = fs * 0.3; space = HERSHEY[" "]["w"] * fs
    text = el["text"].upper()
    adv = lambda ch: space if ch == " " else (HERSHEY.get(ch) or HERSHEY["?"])["w"] * fs
    tw = sum(adv(ch) + ls for ch in text) - ls
    th = fs
    ax0, ay0 = el["anchor_position"]["x"], el["anchor_position"]["y"]
    align = el.get("anchor_alignment") or "center"
    ix, iy = ax0, ay0
    if   align == "top_left":     pass
    elif align == "top_center":   ix -= tw/2
    elif align == "top_right":    ix -= tw
    elif align == "center_right": iy -= th/2
    elif align == "center_left":  ix -= tw; iy -= th/2
    elif align == "bottom_left":  iy -= th
    elif align == "bottom_center":ix -= tw/2; iy -= th
    elif align == "bottom_right": ix -= tw; iy -= th
    else:                         ix -= tw/2; iy -= th/2   # center
    cx, cy = ix + tw/2, iy + th/2
    rot = el.get("ccw_rotation", 0) or 0
    mirror = force_mirror if force_mirror is not None else (
        el.get("is_mirrored") if el.get("is_mirrored") is not None else el.get("layer") == "bottom")
    if mirror: rot = -rot
    cosr, sinr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    def xf(px, py):
        if mirror: px = 2*cx - px
        dx, dy = px-cx, py-cy
        return (cx + dx*cosr - dy*sinr, cy + dx*sinr + dy*cosr)
    segs = []; x = ix
    for ch in text:
        if ch == " ": x += space + ls; continue
        g = HERSHEY.get(ch) or HERSHEY["?"]
        for stroke in g["s"]:
            pts = [xf(x + px*fs, iy + py*fs) for px, py in stroke]
            for i in range(len(pts)-1): segs.append((pts[i], pts[i+1]))
            if len(pts) == 1: segs.append((pts[0], pts[0]))
        x += g["w"]*fs + ls
    r = (el["font_size"]/8)/2
    xs = [p[0] for s in segs for p in s]; ys = [p[1] for s in segs for p in s]
    bbox = (min(xs)-r, max(xs)+r, min(ys)-r, max(ys)+r) if xs else (ax0, ax0, ay0, ay0)
    return segs, r, bbox

# ---- component / pin naming -------------------------------------------------------------------
def build(circuit):
    src_port = {}; pcb_port = {}; comp_name = {}; pcbcomp_src = {}
    for e in circuit:
        t = e["type"]
        if   t == "source_port":      src_port[e["source_port_id"]] = e
        elif t == "pcb_port":         pcb_port[e["pcb_port_id"]] = e
        elif t == "source_component": comp_name[e["source_component_id"]] = e.get("name", "?")
        elif t == "pcb_component":    pcbcomp_src[e["pcb_component_id"]] = e.get("source_component_id")
    def refpin(ppid):
        pp = pcb_port.get(ppid); sp = src_port.get(pp["source_port_id"]) if pp else None
        return f"{comp_name.get(sp.get('source_component_id'),'?')}.{sp.get('name','?')}" if sp else "?"
    def comp_of(pcid):
        return comp_name.get(pcbcomp_src.get(pcid), pcid)
    return refpin, comp_of

def bbox_far(b1, b2, m=0.0):
    return b1[0] > b2[1]+m or b2[0] > b1[1]+m or b1[2] > b2[3]+m or b2[2] > b1[3]+m

def main():
    circuit = json.load(open(CIRCUIT))
    refpin, comp_of = build(circuit)
    texts = [e for e in circuit if e["type"] == "pcb_silkscreen_text"]
    paths = [e for e in circuit if e["type"] == "pcb_silkscreen_path"]

    # Copper that silk must clear, split by the layer(s) it exposes (plated hole / through via =
    # a barrel on both sides). Vias are included and treated as exposed — most fabs tent small
    # vias, but silk over a via is poor practice either way, and this stays a 0-noise regression
    # guard as long as no label rides one.
    top_pads, bot_pads = [], []
    for e in circuit:
        if e["type"] in ("pcb_smtpad", "pcb_plated_hole"):
            sh = pad_shape(e); entry = (sh, pad_bbox(sh), refpin(e.get("pcb_port_id")))
            layers = e.get("layers") or [e.get("layer", "top")]
        elif e["type"] == "pcb_via":
            sh = ("circle", (e["x"], e["y"]), e["outer_diameter"]/2)
            entry = (sh, pad_bbox(sh), f"via@({e['x']:.1f},{e['y']:.1f})")
            layers = e.get("layers") or ["top", "bottom"]
        else:
            continue
        if "top" in layers: top_pads.append(entry)
        if "bottom" in layers: bot_pads.append(entry)

    front = [(e, *text_strokes(e)) for e in texts]                        # as authored
    back  = [(e, *text_strokes(e, force_mirror=True)) for e in texts]     # bottom-silk.ts mirror

    path_models = []
    for e in paths:
        rt = e.get("route", [])
        r = e.get("stroke_width", 0.1)/2
        segs = [((rt[i]["x"], rt[i]["y"]), (rt[i+1]["x"], rt[i+1]["y"])) for i in range(len(rt)-1)]
        xs = [p["x"] for p in rt]; ys = [p["y"] for p in rt]
        bbox = (min(xs)-r, max(xs)+r, min(ys)-r, max(ys)+r) if rt else (0, 0, 0, 0)
        path_models.append((segs, r, bbox, comp_of(e.get("pcb_component_id"))))

    # SILK-ON-BARE-COPPER (each side)
    copper = {}
    def check(models, pads, side):
        for te, tsegs, tr, tbb in models:
            for sh, pbb, plbl in pads:
                if bbox_far(tbb, pbb, 0.05): continue
                pen = max((seg_pad_pen(a, b, tr, sh) for a, b in tsegs), default=-1e9)
                if pen > 0:
                    d = copper.setdefault((side, te["pcb_silkscreen_text_id"]), (te, side, {}))[2]
                    d[plbl] = max(d.get(plbl, -1e9), pen)
    check(front, top_pads, "top")
    check(back, bot_pads, "bottom")

    # SILK-ON-SILK-PATH (front only; the back mirrors identically, same relative geometry)
    path_hits = {}
    for te, tsegs, tr, tbb in front:
        for psegs, pr, pbb, owner in path_models:
            if bbox_far(tbb, pbb, 0.05): continue
            g = min((seg_seg(a, b, c, d) - tr - pr for a, b in tsegs for c, d in psegs), default=1e9)
            if g < 0:
                dd = path_hits.setdefault(te["pcb_silkscreen_text_id"], (te, {}))[1]
                dd[owner] = min(dd.get(owner, 1e9), g)

    # SILK-ON-SILK-TEXT
    text_text = []
    for i in range(len(front)):
        for j in range(i+1, len(front)):
            te1, s1, r1, b1 = front[i]; te2, s2, r2, b2 = front[j]
            if bbox_far(b1, b2, 0.05): continue
            g = min((seg_seg(a, b, c, d) - r1 - r2 for a, b in s1 for c, d in s2), default=1e9)
            if g < 0: text_text.append((te1, te2, g))

    def info(te):
        p = te["anchor_position"]
        return f'"{te["text"]}" @({p["x"]:.2f},{p["y"]:.2f}) rot{te.get("ccw_rotation",0)}'

    print("="*74)
    print(f"SILK-ON-BARE-COPPER (text ink on an exposed pad) — {len(copper)} labels")
    print("="*74)
    for _, (te, side, d) in sorted(copper.items(), key=lambda kv: -max(kv[1][2].values())):
        pads_s = ", ".join(f"{k} (ink {v:.3f}mm onto copper)" for k, v in sorted(d.items(), key=lambda kv: -kv[1]))
        print(f"  [{side:6s}] {info(te):45s} -> {pads_s}")
    print(f"\n{'='*74}\nSILK-ON-SILK-PATH (label ink on a component outline/fence) — {len(path_hits)} labels\n{'='*74}")
    for _, (te, d) in sorted(path_hits.items(), key=lambda kv: min(kv[1][1].values())):
        print(f"  {info(te):45s} -> " + ", ".join(f"{k} fence (ovl {-v:.3f}mm)" for k, v in sorted(d.items(), key=lambda kv: kv[1])))
    print(f"\n{'='*74}\nSILK-ON-SILK-TEXT — {len(text_text)} pairs\n{'='*74}")
    for te1, te2, g in sorted(text_text, key=lambda x: x[2]):
        print(f"  {info(te1):45s} <-> {info(te2):45s} (ovl {-g:.3f}mm)")

    if copper:
        print(f"\nFAIL: {len(copper)} label(s) print on bare copper.")
        return 1
    print("\nOK: no silk on bare copper.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
