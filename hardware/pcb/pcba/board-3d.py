#!/usr/bin/env python
"""Build a 3D model of the whole board — the board body plus every component's real
3D model, placed — from a tscircuit circuit-json.

Each `cad_component` carries the part's `position`, `rotation`, a `model_step_url`
(or, for the few CDN parts that ship only an OBJ, a `model_obj_url`), and a
`model_origin_position` (the center-of-component-on-board-surface point in the raw
model). Fetch each distinct model once (cached by LCSC under .cad-cache/), read it as a
prototype, instance it once per placement — recentered by its model_origin_position,
rotated by the tscircuit convention, resting on the board surface — and add a slab built
from the pcb_board outline with the drilled holes cut. Colors come from the component
models; the board is green.

Writes out/<board>.glb (instanced, colored mesh — what the /3d viewer renders). With
--step, also writes out/<board>.step (full B-rep assembly).

    tools/cad-venv/bin/python board-3d.py [board.tsx|circuit.json] [--step] [--vias]

With no argument: board = the directory name. Reads out/<board>.circuit.json, exporting
it via tsci first if it's missing or older than <board>.tsx.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.gp import gp_Trsf, gp_Pnt
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing,
)
from OCP.TopLoc import TopLoc_Location
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString, TCollection_AsciiString
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.TDF import TDF_LabelSequence
from OCP.Quantity import Quantity_Color, Quantity_TOC_sRGB
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.RWGltf import RWGltf_CafWriter
from OCP.TColStd import TColStd_IndexedDataMapOfStringString
from OCP.Message import Message_ProgressRange
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

HERE = Path(__file__).resolve().parent
CDN_UA = "homesodamachine-board-3d/1.0"
BOARD_GREEN = Quantity_Color(0.10, 0.48, 0.20, Quantity_TOC_sRGB)


# tscircuit's rotation convention (@tscircuit/cli dist/cli/main.js `rotateVector`):
# intrinsic X, then Y, then Z.
def rotate_vector(v, rx, ry, rz):
    x, y, z = v
    if rx:
        c, s = math.cos(rx), math.sin(rx)
        y, z = y * c - z * s, y * s + z * c
    if ry:
        c, s = math.cos(ry), math.sin(ry)
        x, z = x * c + z * s, -x * s + z * c
    if rz:
        c, s = math.cos(rz), math.sin(rz)
        x, y = x * c - y * s, x * s + y * c
    return (x, y, z)


def rotation_columns(rot_deg, extra_x_flip=False):
    """Columns of the rotation matrix R (R·e_i). extra_x_flip pre-composes Rx(180),
    the flip a bottom-side part takes onto the board's underside."""
    rx = math.radians(rot_deg.get("x", 0) or 0)
    ry = math.radians(rot_deg.get("y", 0) or 0)
    rz = math.radians(rot_deg.get("z", 0) or 0)
    cols = [rotate_vector(e, rx, ry, rz) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]
    if extra_x_flip:  # Rx(180): (x,y,z) -> (x,-y,-z)
        cols = [(c[0], -c[1], -c[2]) for c in cols]
    return cols


def placement_trsf(position, rotation, model_origin, is_bottom):
    """world = Translate(position) · R · Translate(-model_origin) · model.
    Recentering by model_origin (footprint center in x/y, bottom face in z) drops the
    part onto the origin; `position` then lifts it to the board surface."""
    cx, cy, cz = rotation_columns(rotation, extra_x_flip=is_bottom)
    mo = (model_origin.get("x", 0) or 0, model_origin.get("y", 0) or 0, model_origin.get("z", 0) or 0)
    rmo = tuple(cx[k] * mo[0] + cy[k] * mo[1] + cz[k] * mo[2] for k in range(3))
    t = gp_Trsf()
    t.SetValues(cx[0], cy[0], cz[0], position.get("x", 0) - rmo[0],
                cx[1], cy[1], cz[1], position.get("y", 0) - rmo[1],
                cx[2], cy[2], cz[2], position.get("z", 0) - rmo[2])
    return t


def lcsc_from_url(url):
    return url.rsplit("/", 1)[-1].split("?", 1)[0].rsplit(".", 1)[0]


def ensure_cached(url, cache_dir, ext="step"):
    """Fetch a component model (STEP or OBJ) keyed by LCSC; reused on later runs."""
    dest = cache_dir / f"{lcsc_from_url(url)}.{ext}"
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": CDN_UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())
    return dest


# --- OBJ mesh models -------------------------------------------------------------------------
# A few EasyEDA parts ship an OBJ but no STEP on the model CDN (e.g. J7's B7B-EH-A, C160254:
# .obj 200, .step 404). The OBJ is the same geometry in the same board-referenced frame as the
# STEP would be, so the imported model_origin_position / pcbRotationOffset place it identically.
# We parse it into per-colour sewn shells (OBJ faces here are plain triangles with inline
# newmtl/Kd materials) and hand XCAF a small coloured sub-assembly — the STEP path's twin, so
# placement, meshing and GLB export downstream treat an OBJ-only part like any other.
def parse_obj(text):
    """(verts, groups): verts is a 1-indexed vertex list; groups maps an (r,g,b) colour to its
    triangles (i,j,k). Reads inline materials (newmtl/Kd) and usemtl switches; ignores
    normals/texcoords (faces are `a// b// c//`)."""
    verts, mats, groups = [], {}, {}
    cur_name, cur_col = None, (0.6, 0.6, 0.6)
    for line in text.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == "v":
            verts.append((float(p[1]), float(p[2]), float(p[3])))
        elif p[0] == "newmtl":
            cur_name = p[1] if len(p) > 1 else ""
        elif p[0] == "Kd" and cur_name is not None:
            mats[cur_name] = (float(p[1]), float(p[2]), float(p[3]))
        elif p[0] == "usemtl":
            cur_col = mats.get(p[1] if len(p) > 1 else "", (0.6, 0.6, 0.6))
        elif p[0] == "f":
            idx = [int(tok.split("/")[0]) for tok in p[1:]]
            g = groups.setdefault(cur_col, [])
            for i in range(1, len(idx) - 1):  # fan-triangulate (already triangles)
                g.append((idx[0], idx[i], idx[i + 1]))
    return verts, groups


def obj_shells(verts, groups):
    """One sewn shell per material colour: [(shape, (r,g,b)), …]."""
    out = []
    for color, tris in groups.items():
        sew = BRepBuilderAPI_Sewing(1e-3)
        n = 0
        for a, b, c in tris:
            pa, pb, pc = verts[a - 1], verts[b - 1], verts[c - 1]
            if pa == pb or pb == pc or pa == pc:
                continue
            poly = BRepBuilderAPI_MakePolygon(gp_Pnt(*pa), gp_Pnt(*pb), gp_Pnt(*pc), True)
            if not poly.IsDone():
                continue
            face = BRepBuilderAPI_MakeFace(poly.Wire())
            if not face.IsDone():
                continue
            sew.Add(face.Face())
            n += 1
        if n:
            sew.Perform()
            out.append((sew.SewedShape(), color))
    return out


def obj_prototype(url, cache_dir, sht, ctool):
    """Read an OBJ into a coloured XCAF sub-assembly prototype; returns its label (instanced by
    the caller at each placement, exactly like a STEP prototype)."""
    verts, groups = parse_obj(ensure_cached(url, cache_dir, "obj").read_text())
    shells = obj_shells(verts, groups)
    if not shells:
        raise RuntimeError("OBJ yielded no faces")
    proto = sht.NewShape()
    for shape, color in shells:
        lbl = sht.AddShape(shape, False, True)
        ctool.SetColor(lbl, Quantity_Color(*color, Quantity_TOC_sRGB),
                       XCAFDoc_ColorType.XCAFDoc_ColorSurf)
        sht.AddComponent(proto, lbl, TopLoc_Location(gp_Trsf()))
    return proto


def build_board(cj, cut_vias):
    board = next((e for e in cj if e.get("type") == "pcb_board"), None)
    if not board:
        raise RuntimeError("no pcb_board in circuit-json")
    thickness = board.get("thickness", 1.4)
    outline = board.get("outline") or []
    if len(outline) >= 3:
        pts = [(p["x"], p["y"]) for p in outline]
    else:
        w, h = board["width"], board["height"]
        cx, cy = board.get("center", {}).get("x", 0), board.get("center", {}).get("y", 0)
        pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
               (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    slab = (cq.Workplane("XY").polyline(pts).close()
            .extrude(thickness).translate((0, 0, -thickness / 2)))

    cut_h = thickness + 2.0
    cutters = None

    def add(solid):
        nonlocal cutters
        cutters = solid if cutters is None else cutters.union(solid, glue=True, tol=1e-4)

    for h in cj:
        t = h.get("type")
        if t in ("pcb_plated_hole", "pcb_hole"):
            try:
                x, y = h["x"], h["y"]
                shape = h.get("shape") or h.get("hole_shape") or "circle"
                if shape == "pill":
                    w, ln = h["hole_width"], h["hole_height"]
                    slot = (cq.Workplane("XY").slot2D(max(w, ln), min(w, ln), 0 if ln >= w else 90)
                            .extrude(cut_h).translate((0, 0, -cut_h / 2)))
                    add(slot.rotate((0, 0, 0), (0, 0, 1), h.get("ccw_rotation", 0)).translate((x, y, 0)))
                else:
                    d = h.get("hole_diameter") or h.get("hole_width") or 0
                    if d > 0:
                        add(cq.Workplane("XY").center(x, y).circle(d / 2)
                            .extrude(cut_h).translate((0, 0, -cut_h / 2)))
            except Exception as e:
                print(f"  ! skipped a {t}: {e}", file=sys.stderr)
        elif t == "pcb_via" and cut_vias:  # 0.3 mm barrels; --vias only
            d = h.get("hole_diameter", 0)
            if d > 0:
                add(cq.Workplane("XY").center(h["x"], h["y"]).circle(d / 2)
                    .extrude(cut_h).translate((0, 0, -cut_h / 2)))

    if cutters is not None:
        slab = slab.cut(cutters)
    return slab.val().wrapped, thickness


def build_assembly(cj, cache_dir, cut_vias):
    """One XCAF assembly: each distinct component model read once as a prototype (with
    its colors), instanced at every placement; board slab added with a green color.
    A part's model is its STEP when it has one, else its OBJ (some CDN parts ship only OBJ)."""
    layer = {e["pcb_component_id"]: e.get("layer", "top")
             for e in cj if e.get("type") == "pcb_component"}
    src = lambda cad: cad.get("model_step_url") or cad.get("model_obj_url")  # noqa: E731
    cads = [e for e in cj if e.get("type") == "cad_component" and src(e)]

    app = XCAFApp_Application.GetApplication_s()
    doc = TDocStd_Document(TCollection_ExtendedString("BinXCAF"))
    app.NewDocument(TCollection_ExtendedString("BinXCAF"), doc)
    sht = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ctool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    def free_tags():
        s = TDF_LabelSequence()
        sht.GetFreeShapes(s)
        return {s.Value(i).Tag(): s.Value(i) for i in range(1, s.Length() + 1)}

    proto = {}  # model source url (STEP preferred, else OBJ) -> prototype label
    for cad in cads:
        key = src(cad)
        if key in proto:
            continue
        step_url, obj_url, label = cad.get("model_step_url"), cad.get("model_obj_url"), None
        if step_url:  # STEP: read the colored B-rep prototype (as-transferred)
            try:
                before = set(free_tags())
                r = STEPCAFControl_Reader()
                r.SetColorMode(True)
                r.SetNameMode(True)
                if r.ReadFile(str(ensure_cached(step_url, cache_dir))) != IFSelect_RetDone:
                    raise RuntimeError("OCCT could not read model")
                r.Transfer(doc)
                new = [lbl for tag, lbl in free_tags().items() if tag not in before]
                if not new:
                    raise RuntimeError("no shape transferred")
                label = new[-1]
            except Exception as e:
                print(f"  ! {lcsc_from_url(step_url)}: {e}", file=sys.stderr)
        if label is None and obj_url:  # no/failed STEP → build from the OBJ mesh
            try:
                label = obj_prototype(obj_url, cache_dir, sht, ctool)
            except Exception as e:
                print(f"  ! {lcsc_from_url(obj_url)} (obj): {e}", file=sys.stderr)
        if label is not None:
            proto[key] = label

    asm = sht.NewShape()
    placed = failed = 0
    for cad in cads:
        label = proto.get(src(cad))
        if label is None:
            failed += 1
            continue
        is_bottom = (layer.get(cad.get("pcb_component_id"), "top") or "top").lower() == "bottom"
        trsf = placement_trsf(cad.get("position", {}), cad.get("rotation", {}),
                              cad.get("model_origin_position", {}), is_bottom)
        sht.AddComponent(asm, label, TopLoc_Location(trsf))
        placed += 1

    board_shape, _ = build_board(cj, cut_vias)
    board_label = sht.AddShape(board_shape, False, True)
    ctool.SetColor(board_label, BOARD_GREEN, XCAFDoc_ColorType.XCAFDoc_ColorSurf)
    sht.AddComponent(asm, board_label, TopLoc_Location(gp_Trsf()))
    sht.UpdateAssemblies()
    return doc, sht.GetShape_s(asm), placed, failed


def ensure_circuit_json(board_name):
    cj_path = HERE / "out" / f"{board_name}.circuit.json"
    tsx = HERE / f"{board_name}.tsx"
    fresh = cj_path.exists() and (not tsx.exists() or cj_path.stat().st_mtime >= tsx.stat().st_mtime)
    if not fresh:
        if not tsx.exists():
            sys.exit(f"no {tsx.name} and no {cj_path}")
        print(f"[{board_name}] exporting circuit-json (route pass)…")
        subprocess.run([str(HERE / "node_modules" / ".bin" / "tsci"), "export", "-f", "circuit-json",
                        "-o", f"out/{board_name}.circuit.json", f"{board_name}.tsx"], cwd=HERE, check=True)
    return cj_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="board.tsx or a .circuit.json (default: this dir's board)")
    ap.add_argument("--step", action="store_true", help="also write the full B-rep out/<board>.step")
    ap.add_argument("--vias", action="store_true", help="cut via barrels into the board slab")
    ap.add_argument("--cache-dir", default=str(HERE / ".cad-cache"))
    ap.add_argument("--deflection", type=float, default=0.3, help="mesh linear deflection, mm")
    args = ap.parse_args()

    if args.target and args.target.endswith(".circuit.json"):
        board_name = Path(args.target).name.replace(".circuit.json", "")
        cj_path = Path(args.target)
    else:
        board_name = Path(args.target).name.replace(".tsx", "") if args.target else HERE.name
        cj_path = ensure_circuit_json(board_name)

    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_dir = HERE / "out"
    out_dir.mkdir(exist_ok=True)

    t0 = time.time()
    cj = json.loads(cj_path.read_text())
    n = sum(1 for e in cj if e.get("type") == "cad_component"
            and (e.get("model_step_url") or e.get("model_obj_url")))
    print(f"[{board_name}] {n} components, board + drills…")
    doc, top, placed, failed = build_assembly(cj, cache_dir, args.vias)

    BRepTools.Clean_s(top)
    BRepMesh_IncrementalMesh(top, args.deflection, False, 0.5, True)

    glb_path = out_dir / f"{board_name}.glb"
    writer = RWGltf_CafWriter(TCollection_AsciiString(str(glb_path)), True)
    if not writer.Perform(doc, TColStd_IndexedDataMapOfStringString(), Message_ProgressRange()):
        sys.exit("GLB write failed")

    bb = Bnd_Box()
    BRepBndLib.Add_s(top, bb)
    xmn, ymn, zmn, xmx, ymx, zmx = bb.Get()
    mb = glb_path.stat().st_size / 1024 / 1024
    gz = len(gzip.compress(glb_path.read_bytes())) / 1024 / 1024
    tag = f", {failed} without a model" if failed else ""
    print(f"[{board_name}] wrote out/{glb_path.name} — {placed} placed{tag}, {mb:.1f} MB ({gz:.1f} MB gzipped)")

    # Green-soldermask face textures the viewer lays over the board (needs the fab
    # gerbers from a prior render-board.ts). Best-effort — the GLB stands without them.
    bun = shutil.which("bun") or str(Path.home() / ".bun" / "bin" / "bun")
    try:
        subprocess.run([bun, "board-texture.ts", board_name], cwd=HERE, check=True)
    except Exception as e:
        print(f"[{board_name}] board-texture skipped ({e}) — run: bun board-texture.ts {board_name}", file=sys.stderr)

    if args.step:
        Interface_Static.SetCVal_s("write.step.schema", "AP214")
        sw = STEPCAFControl_Writer()
        sw.Transfer(doc)
        step_path = out_dir / f"{board_name}.step"
        if sw.Write(str(step_path)) != IFSelect_RetDone:
            sys.exit("STEP write failed")
        print(f"[{board_name}] wrote out/{step_path.name} — {step_path.stat().st_size/1024/1024:.0f} MB (B-rep)")

    print(f"[{board_name}] {xmx-xmn:.1f} × {ymx-ymn:.1f} × {zmx-zmn:.1f} mm, {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
