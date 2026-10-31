"""Files from mesh solids: STL, 3MF, the viewer's `.step.mesh`, GLB, and the model file.

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
    """(V float64, T int64, face index per triangle, face records) of one MeshSolid."""
    topo = solid._topology().t
    return topo.V, topo.T, topo.tri_face, [topo.face_record(f) for f in range(len(topo.face_surface))]


def _triangles(solid):
    """(V float64, T int64) of one MeshSolid, for a writer that needs no faces: the solid
    simplified to the rule's TOLERANCE, so no sliver the booleans left reaches a file."""
    mesh = solid.m.simplify(TOLERANCE).to_mesh64()
    return (np.asarray(mesh.vert_properties, float)[:, :3],
            np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3))


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


def write_model(solids, path, names=None, colors=None):
    """The mesh model a mesh-kernel run leaves beside each STEP it would have written:
    float64 vertices, triangles, a face per triangle and the face records, per solid, with
    each solid's name and linear colour."""
    data = model_bytes(solids, names, colors)
    with open(path, "wb") as f:
        f.write(data)


def model_bytes(solids, names=None, colors=None):
    """`write_model`'s bytes."""
    return npz_bytes(model_arrays(solids, names, colors))


def model_arrays(solids, names=None, colors=None):
    """`write_model`'s arrays, by name."""
    arrays, records = {}, []
    names = names or [""] * len(solids)
    colors = colors or [None] * len(solids)
    for i, s in enumerate(solids):
        V, T, face, recs = _arrays(s)
        arrays[f"V{i}"] = V
        arrays[f"T{i}"] = T.astype(np.uint32)
        arrays[f"F{i}"] = face.astype(np.uint32)
        records.append([_jsonable(r) for r in recs])
    arrays["names"] = np.frombuffer(json.dumps(names).encode(), np.uint8)
    arrays["colors"] = np.frombuffer(json.dumps(
        [None if c is None else [round(float(x), 9) for x in c] for c in colors]).encode(), np.uint8)
    arrays["records"] = np.frombuffer(json.dumps(records, separators=(",", ":")).encode(), np.uint8)
    return arrays


def npz_bytes(arrays):
    """`arrays` as an .npz whose bytes are the same whenever the arrays are."""
    buf = io.BytesIO()
    np.savez(buf, **arrays)
    return _stable_npz(buf.getvalue())


def _stable_npz(data):
    """An .npz with its zip entries' timestamps fixed, so equal arrays are equal bytes."""
    src = zipfile.ZipFile(io.BytesIO(data))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
        for info in src.infolist():
            fixed = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0))
            z.writestr(fixed, src.read(info.filename))
    return out.getvalue()


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
