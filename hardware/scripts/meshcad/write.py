"""Files from mesh solids: STL, 3MF, STEP, the viewer's `.step.mesh`, GLB, and the model file.

Every writer here is a function of the triangles alone, so the same solid writes the same
bytes every run: no timestamps, no ordering that depends on a hash seed. `pack.py` keys on
those bytes.
"""

import io
import json
import struct
import zipfile

import numpy as np

from .rule import TOLERANCE

STL_HEADER = b"meshcad binary STL".ljust(80, b" ")


def _arrays(solid):
    """(V float64, T int64, face index per triangle, face records) of one MeshSolid: its own
    mesh, with its fillets applied. A solid whose fillets are pending selects on the solid
    before them (`MeshSolid.m`), so its selectors' topology is not its own. One the solid does
    not already hold is taken for the write and let go, without the edges and vertices a
    selector wants, and its faces stay on the solid for the next file written of it. An immutable
    fine-model input hands back the arrays and records it carries."""
    if (model_arrays := getattr(solid, "model_arrays", None)) is not None:
        return model_arrays()
    from .topo import Topology
    held = solid._topo if solid._rounds is None else None
    if held is not None:
        t = held.t
        return t.V, t.T, t.tri_face, [t.face_record(f) for f in range(len(t.face_surface))]
    faces = solid.__dict__.get("_faces")
    if faces is None:
        t = Topology(solid.m)
        solid._faces = faces = (t.tri_face, [t.face_record(f) for f in range(len(t.face_surface))])
        return (t.V, t.T, *faces)
    mesh = solid.m.to_mesh64()
    return (np.asarray(mesh.vert_properties, float)[:, :3],
            np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3), *faces)


def _partition_arrays(solid):
    """Fine arrays whose face slots retain the native Manifold partitions.

    Surface records may be equal across distinct native faces. Their slot
    identities still constrain drawing simplification, independently of what
    the selector topology considers one analytic surface.
    """
    if (model_arrays := getattr(solid, "model_arrays", None)) is not None:
        return model_arrays()
    from .build import REGISTRY
    from .topo import placed

    mesh = solid.m.to_mesh64()
    vertices = np.asarray(mesh.vert_properties, float)[:, :3]
    triangles = np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3)
    native_faces = np.asarray(mesh.face_id, np.int64)
    runs = np.asarray(mesh.run_index, np.int64) // 3
    originals = np.asarray(mesh.run_original_id, np.int64)
    transforms = np.asarray(mesh.run_transform, float).reshape(-1, 4, 3)
    run_of = np.repeat(np.arange(len(originals)), np.diff(runs))
    groups, face_of = np.unique(run_of * (1 << 32) + native_faces,
                               return_inverse=True)
    records = []
    for group in groups:
        run, face = int(group >> 32), int(group & 0xFFFFFFFF)
        table = REGISTRY.get(int(originals[run]))
        records.append(placed(table[face], transforms[run])
                       if table is not None and face < len(table) else None)
    return vertices, triangles, face_of.reshape(-1), records


def _triangles(solid, tolerance=TOLERANCE):
    """(V float64, T int64) of one MeshSolid, for a writer that needs no faces: the solid
    simplified to `tolerance`, at least the rule's TOLERANCE, so no sliver the booleans left
    reaches a file."""
    mesh = solid.m.simplify(max(tolerance, TOLERANCE)).to_mesh64()
    return (np.asarray(mesh.vert_properties, float)[:, :3],
            np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3))


#: The share of a drawn solid's triangles `drawn` collapses, and how hard. One fixed rung, not
#: `flute_payload`'s verified ladder: across the assembly scene it lands every solid but the
#: thin clamps and tubes inside the viewer's deflection, and those within a millimetre.
DRAWN_REDUCTION = 0.9
DRAWN_AGGRESSION = 4.0


def drawn(solid, tolerance):
    """(V float64, T int64) of one MeshSolid as a reader draws it, not as it prints: simplified
    to `tolerance`, then nine in ten triangles collapsed."""
    if (surface := getattr(solid, "_presentation", None)) is not None:
        return (np.asarray(surface["pos"], float).reshape(-1, 3),
                np.asarray(surface["idx"], np.int64).reshape(-1, 3))
    V, T = _triangles(solid, tolerance)
    if len(T) <= 500:
        return V, T
    import fast_simplification
    v, f = fast_simplification.simplify(V.astype(np.float32), T.astype(np.uint32),
                                        DRAWN_REDUCTION, agg=DRAWN_AGGRESSION)
    return v.astype(np.float64), f.astype(np.int64)


def drawn_payload(name, color, V, T):
    """One `_mesh_payload` mesh entry from drawn arrays, split at the viewer's creases."""
    import trimesh
    import flute_payload
    pos, nrm, idx, fac = flute_payload.creased(trimesh.Trimesh(V, T, process=False))
    return {"name": name, "color": color, "pos": pos.astype(np.float32),
            "nrm": nrm.astype(np.float32), "idx": np.asarray(idx, np.uint32),
            "fac": np.asarray(fac, np.uint32)}


def shown_payload(solid, name, color, tolerance, arrays=None):
    """A carried producer presentation, or this reader's ordinary drawing."""
    surface = getattr(solid, "_presentation", None)
    return ({**surface, "name": name, "color": color} if surface is not None
            else drawn_payload(name, color, *(arrays if arrays is not None else drawn(solid, tolerance))))


def _solids(shape):
    from .solids import MeshShape, lift
    if hasattr(shape, "vals"):
        return [s for v in shape.vals() for s in _solids(v)]
    if isinstance(shape, MeshShape):
        return shape._solids()
    return lift(shape)._solids()


def stl_bytes(shape):
    parts = []
    for s in _solids(shape):
        V, T = _triangles(s)
        parts.append(V[T])
    tri = np.concatenate(parts) if parts else np.zeros((0, 3, 3))
    tri32 = tri.astype(np.float32)
    a, b, c = (tri32[:, i].astype(np.float64) for i in range(3))
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n, axis=1)
    n = np.where(ln[:, None] > 0, n / np.where(ln > 0, ln, 1)[:, None], 0).astype(np.float32)
    rec = np.zeros(len(tri32), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, tri32
    return STL_HEADER + struct.pack("<I", len(tri32)) + rec.tobytes()


def write_stl(shape, path):
    data = stl_bytes(shape)
    with open(path, "wb") as f:
        f.write(data)


def threemf_bytes(shape, name="part"):
    """A 3MF package with one object per solid, written byte for byte the same each run."""
    objs, items = [], []
    for i, s in enumerate(_solids(shape), 1):
        V, T = _triangles(s)
        verts = "".join(f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in V)
        tris = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in T)
        objs.append(f'<object id="{i}" type="model" name="{name}-{i}"><mesh><vertices>{verts}</vertices>'
                    f'<triangles>{tris}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources>{"".join(objs)}</resources><build>{"".join(items)}</build></model>')
    types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
             '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, text in (("[Content_Types].xml", types), ("_rels/.rels", rels), ("3D/3dmodel.model", model)):
            info = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text)
    return buf.getvalue()


def write_3mf(shape, path, name="part"):
    with open(path, "wb") as f:
        f.write(threemf_bytes(shape, name))


def payload_meshes(shape, name="", color=None):
    """`_mesh_payload` mesh entries: per face its own vertices, so normals are smooth within a
    face and sharp across its edges, and one `fac` range per face, as the edge picker reads."""
    out = []
    for s in _solids(shape):
        V, T, face, _ = _arrays(s)
        order = np.argsort(face, kind="stable")
        Tf, ff = T[order], face[order]
        bounds = np.flatnonzero(np.diff(ff)) + 1
        starts = np.concatenate([[0], bounds])
        ends = np.concatenate([bounds, [len(ff)]])
        pos, nrm, idx, fac = [], [], [], []
        base = 0
        for a, b in zip(starts, ends):
            tri = Tf[a:b]
            used, local = np.unique(tri, return_inverse=True)
            local = local.reshape(-1, 3)
            p = V[used]
            tn = np.cross(V[tri[:, 1]] - V[tri[:, 0]], V[tri[:, 2]] - V[tri[:, 0]])
            vn = np.zeros_like(p)
            for k in range(3):
                np.add.at(vn, local[:, k], tn)
            ln = np.linalg.norm(vn, axis=1)
            vn = vn / np.where(ln > 0, ln, 1)[:, None]
            pos.append(p)
            nrm.append(vn)
            first = sum(len(x) for x in idx)
            idx.append(local + base)
            fac += [first, first + len(tri) - 1]
            base += len(p)
        out.append({"name": name, "color": color,
                    "pos": np.concatenate(pos).astype(np.float32),
                    "nrm": np.concatenate(nrm).astype(np.float32),
                    "idx": np.concatenate(idx).astype(np.uint32), "fac": np.asarray(fac, np.uint32)})
    return out


def write_payload(meshes, path, src=None, cut=None, version=3):
    """The bytes `_mesh_payload.write` writes, from numpy arrays."""
    entries, blob = [], bytearray()
    for m in meshes:
        e = {"name": m["name"], "color": m["color"]}
        for key, dt in (("pos", "<f4"), ("nrm", "<f4"), ("idx", "<u4"), ("fac", "<u4")):
            arr = np.ascontiguousarray(np.asarray(m[key]).reshape(-1), dtype=dt)
            e[key] = [len(blob), arr.size]
            blob += arr.tobytes()
        if "face_sources" in m:
            from _mesh_payload import aligned_face_sources
            sources = aligned_face_sources(m["face_sources"], len(np.asarray(m["fac"]).reshape(-1)) // 2)
            if sources is not None:
                e["face_sources"] = sources
        entries.append(e)
    header = {"v": version, "meshes": entries}
    if src is not None:
        header["src"] = src
    if cut is not None:
        header["cut"] = cut
    head = json.dumps(header, separators=(",", ":")).encode()
    head += b" " * (-(len(head) + 4) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<I", len(head)))
        f.write(head)
        f.write(blob)


def _jsonable(rec):
    if rec is None:
        return None
    return {k: (np.asarray(v, float).round(9).tolist() if isinstance(v, np.ndarray)
                else round(float(v), 9) if isinstance(v, (float, np.floating)) else v)
            for k, v in rec.items()}


def write_model(solids, path, names=None, colors=None, *, preserve_partitions=False):
    """The mesh model a mesh-kernel run leaves beside each STEP it would have written:
    float64 vertices, triangles, a face per triangle and the face records, per solid, with
    each solid's name and linear colour. `preserve_partitions` keeps a separate record
    slot for every native face, including faces whose records are equal."""
    with open(path, "wb") as f:
        write_npz(f, model_items(solids, names, colors,
                                preserve_partitions=preserve_partitions))


def model_bytes(solids, names=None, colors=None, *, preserve_partitions=False):
    """`write_model`'s bytes."""
    buf = io.BytesIO()
    write_npz(buf, model_items(solids, names, colors,
                              preserve_partitions=preserve_partitions))
    return buf.getvalue()


def model_items(solids, names=None, colors=None, *, preserve_partitions=False):
    """`write_model`'s arrays, by name, each made as the file takes it, so a model of many
    solids holds one solid's mesh at a time."""
    records = []
    names = names or [""] * len(solids)
    colors = colors or [None] * len(solids)
    for i, s in enumerate(solids):
        V, T, face, recs = _partition_arrays(s) if preserve_partitions else _arrays(s)
        records.append(json.dumps([_jsonable(r) for r in recs], separators=(",", ":")))
        yield f"V{i}", V
        yield f"T{i}", T.astype(np.uint32)
        yield f"F{i}", face.astype(np.uint32)
    yield "names", text_array(json.dumps(names))
    yield "colors", text_array(json.dumps(
        [None if c is None else [round(float(x), 9) for x in c] for c in colors]))
    yield "records", text_array("[" + ",".join(records) + "]")


#: The FILE_DESCRIPTION a mesh-kernel STEP carries, which `imports.step_solids` reads to take
#: the model file beside it instead.
STEP_MARK = "meshcad tessellated"


def write_step(bodies, path, root_name="model", tolerance=TOLERANCE):
    """`bodies` — (name, MeshSolid or its drawn (V, T), linear rgb or None) — as an AP242 STEP
    of triangulated surface sets: one product per body under its name and colour, under an
    assembly named `root_name` when there is more than one, each solid simplified to
    `tolerance`.

    OCCT writes the product structure, each body standing as one placeholder triangle whose
    first point is (k, 0, 0); each placeholder's coordinates and triangles are then written over
    with the body's own, from its arrays. A STEP reader takes the triangles; a mesh-kernel import
    takes the model file beside it."""
    import re
    import tempfile
    from pathlib import Path
    from OCP.BRep import BRep_Builder
    from OCP.gp import gp_Pnt
    from OCP.Interface import Interface_Static
    from OCP.Poly import Poly_Triangle, Poly_Triangulation
    from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
    from OCP.STEPCAFControl import STEPCAFControl_Writer
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Controller
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS_Face
    from OCP.XCAFDoc import XCAFDoc_ColorType, XCAFDoc_DocumentTool
    STEPControl_Controller.Init_s()
    Interface_Static.SetIVal_s("write.step.tessellated", 1)
    Interface_Static.SetIVal_s("write.step.schema", 5)
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    shapes = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    colors = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    root = None
    if len(bodies) > 1:
        root = shapes.NewShape()
        TDataStd_Name.Set_s(root, TCollection_ExtendedString(root_name))
    arrays = []
    for k, (name, solid, rgb) in enumerate(bodies, 1):
        arrays.append(solid if isinstance(solid, tuple) else _triangles(solid, tolerance))
        tri = Poly_Triangulation(3, 1, False)
        for j, p in enumerate(((k, 0, 0), (k, 1, 0), (k, 0, 1)), 1):
            tri.SetNode(j, gp_Pnt(*map(float, p)))
        tri.SetTriangle(1, Poly_Triangle(1, 2, 3))
        face = TopoDS_Face()
        BRep_Builder().MakeFace(face, tri)
        label = shapes.AddShape(face, False)
        TDataStd_Name.Set_s(label, TCollection_ExtendedString(name))
        if rgb is not None:
            colors.SetColor(label, Quantity_Color(*map(float, rgb), Quantity_TOC_RGB),
                            XCAFDoc_ColorType.XCAFDoc_ColorSurf)
        if root is not None:
            shapes.AddComponent(root, label, TopLoc_Location())
    if root is not None:
        shapes.UpdateAssemblies()
    writer = STEPCAFControl_Writer()
    writer.SetColorMode(True)
    writer.SetNameMode(True)
    writer.Transfer(doc, STEPControl_AsIs)
    with tempfile.TemporaryDirectory() as d:
        skeleton = Path(d) / "skeleton.step"
        writer.Write(str(skeleton))
        text = skeleton.read_text()
    text = text.replace("FILE_DESCRIPTION(('Open CASCADE Model')", f"FILE_DESCRIPTION(('{STEP_MARK}')", 1)
    coord_of = {int(float(m.group(2))): m.group(1) for m in re.finditer(
        r"#(\d+) = COORDINATES_LIST\('',3,\(\(([-\d.E+]+),0\.,0\.\)", text)}
    def entity(eid):
        start = text.index(f"#{eid} = ")
        return start, text.index(";\n", start) + 1
    out, cursor, spans = [], 0, []
    for k, (V, T) in enumerate(arrays, 1):
        cid = coord_of[k]
        spans.append((entity(cid), f"#{cid} = COORDINATES_LIST('',{len(V)},({_step_rows(V, '%.4f')}));"))
        m = re.search(rf"#(\d+) = TRIANGULATED_SURFACE_SET\('',#{cid},", text)
        spans.append((entity(m.group(1)), f"#{m.group(1)} = TRIANGULATED_SURFACE_SET('',#{cid},"
                      f"{len(V)},(),(),({_step_rows(T + 1, '%d')}));"))
    for (a, b), new in sorted(spans):
        out += [text[cursor:a], new]
        cursor = b
    out.append(text[cursor:])
    Path(path).write_text("".join(out))


def _step_rows(a, fmt):
    """Rows of `a` as STEP list members, `(x,y,z),(x,y,z)`, a line each."""
    buf = io.StringIO()
    np.savetxt(buf, a, fmt=fmt, delimiter=",", newline="),\n(")
    return "(" + buf.getvalue()[:-3]


def text_array(text):
    """`text` as the uint8 array an .npz carries it in."""
    return np.frombuffer(text.encode(), np.uint8)


def write_npz(f, items):
    """(name, array) pairs into the binary file `f` as an .npz, each array written as it comes.
    The entries carry one fixed date, so equal arrays are equal bytes."""
    with zipfile.ZipFile(f, "w", zipfile.ZIP_STORED) as z:
        for name, a in items:
            info = zipfile.ZipInfo(name + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            with z.open(info, "w") as out:
                np.lib.format.write_array(out, np.asanyarray(a), allow_pickle=False)


def model_identity(path):
    """[(name, linear colour)] of the solids in the model file at `path`."""
    with np.load(path, allow_pickle=False) as z:
        names = json.loads(bytes(z["names"]).decode())
        colors = json.loads(bytes(z["colors"]).decode()) if "colors" in z else [None] * len(names)
    return list(zip(names, colors))


def print_payload(step, printed):
    """The viewer's payload for a printed piece, cut from its print mesh (a trimesh) in the pass
    that made it — `flute_payload.cut` without the files in between. Name and colour are the
    model's beside `step`, and the payload states that model as its source."""
    from pathlib import Path
    import _mesh_payload
    import flute_payload
    step = Path(step)
    model = step.with_name(step.name + ".npz")
    (name, color), = model_identity(model)
    printed = printed.copy()
    printed.merge_vertices()
    bound = flute_payload.deflection(printed)
    reduced, dev = flute_payload.simplify_within(printed, bound)
    pos, nrm, idx, fac = flute_payload.creased(reduced)
    out = step.with_name(step.name + ".mesh")
    write_payload([{"name": name, "color": color, "pos": pos, "nrm": nrm, "idx": idx, "fac": fac}],
                  out, src=_mesh_payload.source_digest(model),
                  cut={"dev": round(float(dev), 4), "bound": round(float(bound), 4)})
    print(f"-> {out.name}  {len(printed.faces)} -> {len(reduced.faces)} facets, {len(pos)} vertices, "
          f"{len(fac) // 2} regions, {out.stat().st_size / 1e6:.2f} MB, "
          f"{dev:.3f} mm inside a {bound:.3f} mm budget")


def glb_bytes(bodies):
    """A binary glTF with one node per body: `bodies` is [(name, MeshShape, rgb or None)].

    Each primitive's triangles are grouped by face; `extras.faces` lists, per face, its first
    triangle, its count, its surface and the generator line that made it."""
    blob = bytearray()
    views, accessors, meshes, nodes, materials = [], [], [], [], []

    def add(arr, target, comp, typ):
        arr = np.ascontiguousarray(arr)
        while len(blob) % 4:
            blob.append(0)
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": arr.nbytes, "target": target})
        blob.extend(arr.tobytes())
        acc = {"bufferView": len(views) - 1, "componentType": comp, "count": int(arr.shape[0]), "type": typ}
        if typ == "VEC3":
            acc["min"] = arr.min(0).tolist()
            acc["max"] = arr.max(0).tolist()
        accessors.append(acc)
        return len(accessors) - 1

    for name, shape, rgb in bodies:
        prims = []
        for s in _solids(shape):
            V, T, face, recs = _arrays(s)
            order = np.argsort(face, kind="stable")
            Tf, ff = T[order], face[order]
            starts = np.concatenate([[0], np.flatnonzero(np.diff(ff)) + 1])
            counts = np.diff(np.concatenate([starts, [len(ff)]]))
            faces = [{"first": int(a), "count": int(n), **(_jsonable(recs[int(ff[a])]) or {})}
                     for a, n in zip(starts, counts)]
            pos = add(V.astype(np.float32), 34962, 5126, "VEC3")
            ind = add(Tf.reshape(-1).astype(np.uint32), 34963, 5125, "SCALAR")
            prim = {"attributes": {"POSITION": pos}, "indices": ind, "extras": {"faces": faces}}
            if rgb is not None:
                materials.append({"pbrMetallicRoughness": {"baseColorFactor": [*map(float, rgb), 1.0],
                                                           "metallicFactor": 0.0}})
                prim["material"] = len(materials) - 1
            prims.append(prim)
        meshes.append({"name": name, "primitives": prims})
        nodes.append({"name": name, "mesh": len(meshes) - 1})
    gltf = {"asset": {"version": "2.0", "generator": "meshcad"}, "scene": 0,
            "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes, "meshes": meshes,
            "accessors": accessors, "bufferViews": views, "buffers": [{"byteLength": len(blob)}]}
    if materials:
        gltf["materials"] = materials
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    while len(blob) % 4:
        blob.append(0)
    total = 12 + 8 + len(js) + 8 + len(blob)
    return (struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<I4s", len(js), b"JSON") + js
            + struct.pack("<I4s", len(blob), b"BIN\x00") + bytes(blob))


def write_glb(bodies, path):
    with open(path, "wb") as f:
        f.write(glb_bytes(bodies))
