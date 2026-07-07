#!/usr/bin/env python
"""Audit every placed part's 3D STEP model orientation against its footprint.

The failure this catches: a part whose imported cadModel `pcbRotationOffset` is wrong, so the 3D
STEP is rotated/mirrored relative to the 2D footprint (pads/courtyard/silk) it's supposed to sit
on — the "rotated wrong in the 3D view" class (e.g. BT1's CR2032 holder). A plain re-import diff
would NOT catch it, because the offset can be wrong straight out of `tsci import`; you have to
compare the actual 3D geometry to the footprint.

Method: for each cad_component, load its STEP, apply the SAME placement transform board-3d.py uses
(rotation incl. pcbRotationOffset + model_origin recenter + board position, verbatim), project the
model to the board XY plane, and compare that silhouette to the part's footprint courtyard (or pad
box). Two tells:
  - LONG-AXIS SWAP  — model's long axis ⟂ footprint's long axis ⇒ likely 90°/270° off.
  - CENTER OFFSET   — model silhouette centre far from the footprint centre ⇒ likely 180°/mirror.

Limits (be honest): a rotationally-symmetric silhouette (round/square, no asymmetric body feature)
carries no orientation signal, so a 180° error on such a part is invisible here — but so is it to
the eye, and polarity for those rides on the footprint's pin numbering, not the 3D. Flags are
"review", not proof: confirm against the part before acting. Thresholds are tuned so this board's
77 correctly-oriented parts all pass (max clean offset ~0.6 mm) while a deliberate 180° flip of
BT1 reads 2.49 mm.

    tools/cad-venv/bin/python part-orientation-audit.py [board]   # default: this dir's board
Reads out/<board>.circuit.json (run a render first). Exit code 1 if anything is flagged.
"""
import json, math, sys, urllib.request
from pathlib import Path
from OCP.STEPControl import STEPControl_Reader
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cad-cache"
CDN_UA = "homesodamachine-board-3d/1.0"
CENTER_FLAG_MM = 1.0   # model-vs-footprint centre offset that flags a likely 180°/mirror
ASPECT_MIN = 1.25      # how non-square a part must be before a long-axis swap is meaningful

# --- board-3d.py placement math (kept identical on purpose) ---------------------------------
def rotate_vector(v, rx, ry, rz):
    x, y, z = v
    if rx: c, s = math.cos(rx), math.sin(rx); y, z = y*c - z*s, y*s + z*c
    if ry: c, s = math.cos(ry), math.sin(ry); x, z = x*c + z*s, -x*s + z*c
    if rz: c, s = math.cos(rz), math.sin(rz); x, y = x*c - y*s, x*s + y*c
    return (x, y, z)

def rotation_columns(rot_deg, extra_x_flip=False):
    rx, ry, rz = (math.radians(rot_deg.get(k, 0) or 0) for k in "xyz")
    cols = [rotate_vector(e, rx, ry, rz) for e in ((1,0,0),(0,1,0),(0,0,1))]
    return [(c[0], -c[1], -c[2]) for c in cols] if extra_x_flip else cols

def place(p, position, rotation, model_origin, is_bottom):
    cols = rotation_columns(rotation, is_bottom)
    mo = tuple(model_origin.get(k, 0) or 0 for k in "xyz")
    q = [p[i] - mo[i] for i in range(3)]
    return tuple(position.get(k2, 0) + sum(cols[i][k]*q[i] for i in range(3)) for k, k2 in enumerate("xyz"))

def lcsc_from_url(url): return url.rsplit("/", 1)[-1].split("?", 1)[0].rsplit(".", 1)[0]

def ensure_cached(url):
    dest = CACHE / f"{lcsc_from_url(url)}.step"
    if dest.exists() and dest.stat().st_size > 0: return dest
    CACHE.mkdir(exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": CDN_UA})
    with urllib.request.urlopen(req, timeout=60) as r: dest.write_bytes(r.read())
    return dest

_bb = {}
def raw_bbox(path):
    if path not in _bb:
        r = STEPControl_Reader(); r.ReadFile(str(path)); r.TransferRoots()
        b = Bnd_Box(); BRepBndLib.Add_s(r.OneShape(), b); _bb[path] = b.Get()
    return _bb[path]

# --- load ------------------------------------------------------------------------------------
board = sys.argv[1] if len(sys.argv) > 1 else HERE.name
board = board.replace(".tsx", "").replace(".circuit.json", "")
cj_path = HERE / "out" / f"{board}.circuit.json"
if not cj_path.exists():
    sys.exit(f"no {cj_path} — run a render first (bun render-board.ts {board}.tsx)")
cj = json.load(open(cj_path))
sc = {e["source_component_id"]: e["name"] for e in cj if e.get("type") == "source_component"}
pcbc = {e["pcb_component_id"]: {"name": sc.get(e.get("source_component_id"), "?"),
                                "center": e.get("center", {}), "layer": e.get("layer", "top"),
                                "scid": e.get("source_component_id")}
        for e in cj if e.get("type") == "pcb_component"}
cy, pads = {}, {}
for e in cj:
    if e.get("type") == "pcb_courtyard_outline" and e.get("outline"):
        xs = [p["x"] for p in e["outline"]]; ys = [p["y"] for p in e["outline"]]
        cy[e["pcb_component_id"]] = (min(xs), min(ys), max(xs), max(ys))
    if e.get("type") in ("pcb_smtpad", "pcb_plated_hole") and e.get("pcb_component_id"):
        b = pads.setdefault(e["pcb_component_id"], [1e9, 1e9, -1e9, -1e9])
        b[0] = min(b[0], e["x"]); b[1] = min(b[1], e["y"]); b[2] = max(b[2], e["x"]); b[3] = max(b[3], e["y"])
scid2pid = {v["scid"]: k for k, v in pcbc.items()}

rows = []
for e in cj:
    if e.get("type") != "cad_component" or not e.get("model_step_url"): continue
    pid = e.get("pcb_component_id") or scid2pid.get(e.get("source_component_id"))
    if pid not in pcbc: continue
    name = pcbc[pid]["name"]
    fb = cy.get(pid) or (tuple(pads[pid]) if pid in pads else None)
    if not fb: continue
    try: rb = raw_bbox(ensure_cached(e["model_step_url"]))
    except Exception as ex: rows.append((name, 9e9, {"err": str(ex)})); continue
    corners = [(rb[i], rb[j], rb[k]) for i in (0, 3) for j in (1, 4) for k in (2, 5)]
    is_bottom = (pcbc[pid]["layer"] or "top").lower() == "bottom"
    P = [place(c, e.get("position", {}), e.get("rotation", {}), e.get("model_origin_position", {}), is_bottom) for c in corners]
    mb = (min(p[0] for p in P), min(p[1] for p in P), max(p[0] for p in P), max(p[1] for p in P))
    dctr = math.hypot((mb[0]+mb[2])/2 - (fb[0]+fb[2])/2, (mb[1]+mb[3])/2 - (fb[1]+fb[3])/2)
    mw, mh, fw, fh = mb[2]-mb[0], mb[3]-mb[1], fb[2]-fb[0], fb[3]-fb[1]
    m_asp, f_asp = max(mw, mh)/max(1e-6, min(mw, mh)), max(fw, fh)/max(1e-6, min(fw, fh))
    flags = []
    if m_asp > ASPECT_MIN and f_asp > ASPECT_MIN and (mw >= mh) != (fw >= fh):
        flags.append("LONG-AXIS SWAP → likely 90°/270°")
    if dctr > CENTER_FLAG_MM:
        flags.append(f"CENTRE OFF {dctr:.2f} mm → likely 180°/mirror")
    rows.append((name, dctr, {"z": round(e.get("rotation", {}).get("z", 0)),
                 "fkind": "courtyard" if pid in cy else "pads",
                 "mdim": (round(mw, 1), round(mh, 1)), "fdim": (round(fw, 1), round(fh, 1)), "flags": flags}))

flagged = [r for r in rows if r[2].get("flags")]
errs = [r for r in rows if r[2].get("err")]
print(f"PART ORIENTATION AUDIT — {board}: {len(rows)} placed parts, {len(flagged)} flagged, {len(errs)} STEP-load errors\n")
for name, d, i in sorted(flagged, key=lambda r: -r[1]):
    print(f"  ⚠ {name:6} z={i['z']:>4}°  model_dim={i['mdim']} footprint_dim={i['fdim']}")
    for f in i["flags"]: print(f"        {f}")
for name, d, i in errs: print(f"  ✗ {name}: STEP load failed — {i['err']}")
if not flagged and not errs:
    print("  ✓ every part's 3D model aligns with its footprint (no rotation/mirror outliers)")
    top = sorted((r for r in rows), key=lambda r: -r[1])[:5]
    print("    tightest (for reference): " + ", ".join(f"{n} {d:.2f}mm" for n, d, _ in top))
sys.exit(1 if (flagged or errs) else 0)
