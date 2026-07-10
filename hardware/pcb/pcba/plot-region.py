#!/usr/bin/env python3
"""Zoom a board region from a render, so hand routing is done by looking, not guessing.

Draws pads, traces (colored by layer), vias, and pin labels for a rectangular board region to a
PNG — precise enough to place `pcbPath` copper on purpose (see hand-routing.md). Reads a rendered
circuit-json; run `bun render-board.ts pcba.tsx` first.

    tools/cad-venv/bin/python plot-region.py [circuit.json] X0 X1 Y0 Y1 [out.png]

e.g. the USB-C corner:
    tools/cad-venv/bin/python plot-region.py out/pcba.circuit.json -63 -52 13 23 /tmp/corner.png

Coordinates are board mm (north is up). Legend: red=top blue=bottom teal=inner1 orange=inner2 green=via gold=pad.
"""
import json, sys, math
from PIL import Image, ImageDraw, ImageFont

args = sys.argv[1:]
path = next((a for a in args if a.endswith(".json")), "out/pcba.circuit.json")
out = next((a for a in args if a.endswith(".png")), "/tmp/region.png")
nums = [float(a) for a in args if a.replace("-", "").replace(".", "").isdigit()]
if len(nums) < 4:
    sys.exit("need X0 X1 Y0 Y1 (board mm), e.g. -63 -52 13 23")
x0, x1, y0, y1 = nums[:4]
SCALE = 60  # px/mm
W, H = int((x1 - x0) * SCALE), int((y1 - y0) * SCALE)
img = Image.new("RGB", (W, H), (18, 18, 22))
d = ImageDraw.Draw(img)
def P(bx, by): return ((bx - x0) * SCALE, (y1 - by) * SCALE)  # y-flip so north is up
try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
except Exception: font = ImageFont.load_default()

c = json.load(open(path))
LAYER = {"top": (235, 70, 60), "bottom": (70, 120, 235),
         "inner1": (60, 190, 165), "inner2": (225, 150, 60)}  # teal SDA/3V3 layer, orange SCL/5V layer

for gx in range(math.ceil(x0), math.floor(x1) + 1):
    d.line([P(gx, y0), P(gx, y1)], fill=(55, 55, 62) if gx % 5 == 0 else (32, 32, 38))
    if gx % 2 == 0: d.text((P(gx, y0)[0] + 1, H - 14), f"{gx}", fill=(120, 120, 130), font=font)
for gy in range(math.ceil(y0), math.floor(y1) + 1):
    d.line([P(x0, gy), P(x1, gy)], fill=(55, 55, 62) if gy % 5 == 0 else (32, 32, 38))
    if gy % 2 == 0: d.text((2, P(x0, gy)[1] - 7), f"{gy}", fill=(120, 120, 130), font=font)

scname = {e["source_component_id"]: e.get("name") for e in c if e.get("type") == "source_component"}
name_by_pcbcid = {e["pcb_component_id"]: scname.get(e["source_component_id"])
                  for e in c if e.get("type") == "pcb_component"}

for e in c:
    if e.get("type") not in ("pcb_smtpad", "pcb_plated_hole"): continue
    bx, by = e["x"], e["y"]
    if not (x0 - 1 <= bx <= x1 + 1 and y0 - 1 <= by <= y1 + 1): continue
    nm = name_by_pcbcid.get(e.get("pcb_component_id"))
    hint = (e.get("port_hints") or [""])[0]
    if e["type"] == "pcb_plated_hole":
        r = e.get("outer_diameter", 1) / 2 * SCALE
        cx, cy = P(bx, by)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(210, 200, 120), width=2)
    else:
        w, h, rot = e.get("width", 0.5), e.get("height", 0.5), e.get("ccw_rotation", 0)
        t = math.radians(rot)
        corners = [P(bx + sx * math.cos(t) - sy * math.sin(t), by + sx * math.sin(t) + sy * math.cos(t))
                   for sx, sy in [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]]
        d.polygon(corners, outline=(210, 200, 120), fill=(60, 58, 40))
    if hint: d.text((P(bx, by)[0] + 2, P(bx, by)[1] - 6), f"{nm}.{hint}", fill=(230, 220, 160), font=font)

for e in c:
    if e.get("type") != "pcb_trace": continue
    pts = e.get("route", [])
    for a, b in zip(pts, pts[1:]):
        if a.get("x") is None or b.get("x") is None: continue
        col = LAYER.get(a.get("layer") or b.get("layer") or "top", (150, 150, 150))
        d.line([P(a["x"], a["y"]), P(b["x"], b["y"])], fill=col, width=max(2, int(0.2 * SCALE)))

for e in c:
    if e.get("type") != "pcb_via": continue
    bx, by = e["x"], e["y"]
    if not (x0 <= bx <= x1 and y0 <= by <= y1): continue
    r = e.get("outer_diameter", 0.5) / 2 * SCALE
    cx, cy = P(bx, by)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 200, 120), outline=(255, 255, 255))

img.save(out)
print(f"wrote {out}  box x[{x0},{x1}] y[{y0},{y1}]  {W}x{H}px")
