#!/usr/bin/env python
"""Build a 3D model of the whole board — the board body plus every component's real
3D model, placed — from a tscircuit circuit-json.

Each `cad_component` carries the part's `position`, `rotation`, a `model_step_url`,
and a `model_origin_position` (the center-of-component-on-board-surface point in the
raw model). Fetch each distinct STEP once (cached by LCSC under .cad-cache/), read it
as a prototype, instance it once per placement — recentered by its model_origin_position,
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
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.gp import gp_Trsf
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


def ensure_cached(url, cache_dir):
    """Fetch a component STEP keyed by LCSC; reused on later runs."""
    dest = cache_dir / f"{lcsc_from_url(url)}.step"
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": CDN_UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())
    return dest


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
    its colors), instanced at every placement; board slab added with a green color."""
    layer = {e["pcb_component_id"]: e.get("layer", "top")
             for e in cj if e.get("type") == "pcb_component"}
    cads = [e for e in cj if e.get("type") == "cad_component" and e.get("model_step_url")]

    app = XCAFApp_Application.GetApplication_s()
    doc = TDocStd_Document(TCollection_ExtendedString("BinXCAF"))
    app.NewDocument(TCollection_ExtendedString("BinXCAF"), doc)
    sht = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ctool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    def free_tags():
        s = TDF_LabelSequence()
        sht.GetFreeShapes(s)
        return {s.Value(i).Tag(): s.Value(i) for i in range(1, s.Length() + 1)}

    proto = {}  # model_step_url -> prototype label
    for cad in cads:
        url = cad["model_step_url"]
        if url in proto:
            continue
        try:
            before = set(free_tags())
            r = STEPCAFControl_Reader()
            r.SetColorMode(True)
            r.SetNameMode(True)
            if r.ReadFile(str(ensure_cached(url, cache_dir))) != IFSelect_RetDone:
                raise RuntimeError("OCCT could not read model")
            r.Transfer(doc)
            new = [lbl for tag, lbl in free_tags().items() if tag not in before]
            if not new:
                raise RuntimeError("no shape transferred")
            proto[url] = new[-1]
        except Exception as e:
            print(f"  ! {lcsc_from_url(url)}: {e}", file=sys.stderr)

    asm = sht.NewShape()
    placed = failed = 0
    for cad in cads:
        label = proto.get(cad["model_step_url"])
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


def canonicalize_glb(glb_path: Path) -> None:
    """Rewrite the GLB in a byte-stable canonical form so identical geometry
    yields identical bytes across runs — the same reason
    hardware/scripts/_cadq_export.py canonicalizes STEP/DXF/PDF output.

    OCCT's RWGltf_CafWriter computes each accessor's min/max bounds in a
    precision finer than the float32 vertex data it stores, and that
    computation is not run-to-run stable: two runs emit a byte-identical
    vertex buffer (the BIN chunk) yet a handful of accessor min/max values
    differ in their last double ULP — e.g. -0.0601943076 vs
    -0.060194307600000004, which round to the SAME float32. Left alone this
    flips ~32 bytes every run, churning git (`out/<board>.glb` is committed)
    and burning agent tokens chasing a non-change.

    Fix: round every accessor min/max to 9 decimal places — nanometre
    precision at the GLB's metre scale, far below the float32 the data is
    stored in, so the sub-ULP jitter collapses while the bound stays exact
    for any real purpose — then re-serialize the JSON chunk compactly and
    deterministically. The BIN chunk is copied through untouched. Written
    atomically, and skipped entirely when the canonical bytes already match
    the file on disk (a true no-op leaves mtime alone). Best-effort: any
    parse failure leaves the writer's own output in place."""
    try:
        data = glb_path.read_bytes()
        if len(data) < 12 or data[:4] != b"glTF":
            return
        _magic, version, _total = struct.unpack_from("<4sII", data, 0)
        if version != 2:
            return
        off = 12
        chunks = []  # [type_bytes, data_bytes] per GLB chunk, in file order
        while off + 8 <= len(data):
            clen, ctype = struct.unpack_from("<I4s", data, off)
            off += 8
            chunks.append([ctype, data[off:off + clen]])
            off += clen
        json_idx = next((i for i, (t, _) in enumerate(chunks) if t == b"JSON"), None)
        if json_idx is None:
            return
        gltf = json.loads(chunks[json_idx][1])

        for acc in gltf.get("accessors", []):
            for key in ("min", "max"):
                vals = acc.get(key)
                if isinstance(vals, list):
                    acc[key] = [round(v, 9) if isinstance(v, float) else v for v in vals]

        new_json = json.dumps(
            gltf, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
        new_json += b"\x20" * ((-len(new_json)) % 4)  # pad to 4 bytes with spaces
        chunks[json_idx][1] = new_json

        body = bytearray()
        for ctype, cdata in chunks:
            body += struct.pack("<I4s", len(cdata), ctype)
            body += cdata
        out = struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + bytes(body)

        if out == data:
            return  # already canonical — no write keeps mtime stable
        fd, tmp = tempfile.mkstemp(prefix=f".{glb_path.name}.", suffix=".tmp",
                                   dir=str(glb_path.parent))
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(out)
            os.replace(tmp, glb_path)
        except BaseException:
            try:
                os.unlink(tmp)
            except FileNotFoundError:
                pass
            raise
    except Exception as e:
        print(f"  ! GLB canonicalization skipped: {e}", file=sys.stderr)


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
    n = sum(1 for e in cj if e.get("type") == "cad_component" and e.get("model_step_url"))
    print(f"[{board_name}] {n} components, board + drills…")
    doc, top, placed, failed = build_assembly(cj, cache_dir, args.vias)

    BRepTools.Clean_s(top)
    BRepMesh_IncrementalMesh(top, args.deflection, False, 0.5, True)

    glb_path = out_dir / f"{board_name}.glb"
    writer = RWGltf_CafWriter(TCollection_AsciiString(str(glb_path)), True)
    if not writer.Perform(doc, TColStd_IndexedDataMapOfStringString(), Message_ProgressRange()):
        sys.exit("GLB write failed")
    # OCCT's glTF writer emits run-to-run-unstable accessor bounds; normalize so
    # an unchanged board re-exports byte-identical (out/<board>.glb is committed).
    canonicalize_glb(glb_path)

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
