"""The placed world as a scene: one mesh per distinct body, one node per placement.

    import _scene
    _scene.write(assembly, "enclosure-assembly.glb")

Where [`_mesh_payload`](_mesh_payload.py) hands the viewer triangles already standing where the
body stands, this keeps the two apart — the triangles a part module drew, in the part's own
frame, and the 4×4 that seats them. Eleven valves drawn once are eleven nodes over one mesh, and
a body that moves changes its node's matrix and nothing else.

`enclosure_assembly.seat_body` hangs a placement over the drawn body rather than folding it into
the coordinates, so `_meshes._unplaced` has a frame and a matrix to take apart. A body whose
pose reached its coordinates arrives here at identity, drawn where it stands, and is written as
its own mesh.

glTF is +Y up and the machine is +Z up, so the root turns -90° about X and every body hangs
under it in the coordinates the layout uses.
"""

import collections
import json
import struct
import sys

from OCP.gp import gp_TrsfForm
from OCP.Quantity import Quantity_TypeOfColor

import _mesh_payload
import _meshes

Node = collections.namedtuple("Node", "name mesh matrix color")

# A body's triangles are cut for the machine it sits in, the way the viewer's are: one
# deflection for the whole model, taken off the assembly's own box.
DEFLECTION_RATIO = _mesh_payload.LINEAR_DEFLECTION_RATIO


def _matrix(trsf):
    """A gp_Trsf as glTF's column-major 16, in the layout's own millimetres."""
    if trsf.Form() == gp_TrsfForm.gp_Identity:
        return [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]
    rows = [[trsf.Value(r, c) for c in range(1, 5)] for r in range(1, 4)]
    return [rows[0][0], rows[1][0], rows[2][0], 0.0,
            rows[0][1], rows[1][1], rows[2][1], 0.0,
            rows[0][2], rows[1][2], rows[2][2], 0.0,
            rows[0][3], rows[1][3], rows[2][3], 1.0]


def scene(assembly):
    """`(nodes, meshes)` — every placement, and the local-frame triangles they stand over.

    A mesh is named the way `_meshes` names the triangles it keeps, so two placements of one
    drawn body meet at one entry and an edit to the body that draws it names a new one."""
    deflection = _mesh_payload.deflection(assembly.toCompound().wrapped)
    nodes, meshes, drawn = [], {}, {}
    for name, color, solids in _mesh_payload._placed(assembly):
        rgb = None
        if color is not None and len(solids) == 1:
            rgb = list(color.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB))
        for solid in solids:
            local, trsf = _meshes._unplaced(solid)
            key = _meshes._named(local, deflection)
            if key not in drawn:
                drawn[key] = local
                meshes[key] = None
            nodes.append(Node(name.split("/")[-1], key, _matrix(trsf), rgb))
    for key, shape in sorted(drawn.items()):
        copied = _mesh_payload._mesh_all([_Wrapped(shape)], deflection)[0]
        pos, nrm, idx = _mesh_payload._solid_arrays(copied)
        meshes[key] = (pos, nrm, idx)
    return nodes, meshes


class _Wrapped:
    """`_mesh_payload._mesh_all` copies `.wrapped` off what it is handed; a bare TopoDS_Shape
    comes through `_meshes._unplaced` without a CadQuery wrapper around it."""

    def __init__(self, shape):
        self.wrapped = shape


def _accessor(gltf, blob, values, fmt, count_of, kind, target, minmax=False):
    stride = {"SCALAR": 1, "VEC3": 3}[kind]
    offset = len(blob)
    blob += struct.pack(f"<{len(values)}{fmt}", *values)
    blob += b"\x00" * (-len(blob) % 4)
    gltf["bufferViews"].append({"buffer": 0, "byteOffset": offset,
                                "byteLength": len(values) * 4, "target": target})
    acc = {"bufferView": len(gltf["bufferViews"]) - 1, "componentType": count_of,
           "count": len(values) // stride, "type": kind}
    if minmax:
        xs, ys, zs = values[0::3], values[1::3], values[2::3]
        acc["min"] = [min(xs), min(ys), min(zs)]
        acc["max"] = [max(xs), max(ys), max(zs)]
    gltf["accessors"].append(acc)
    return len(gltf["accessors"]) - 1


def gltf(nodes, meshes):
    """The glTF document and its buffer. Meshes go out in name order and nodes in the order the
    assembly walks, so one pack writes one file."""
    doc = {"asset": {"version": "2.0", "generator": "homesodamachine/_scene"},
           "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [], "meshes": [],
           "materials": [], "accessors": [], "bufferViews": [], "buffers": []}
    blob = bytearray()
    arrays, materials, index = {}, {}, {}

    # The triangles land once each. A mesh entry is a name over them and a colour to draw them
    # in, so a body worn in two colours is two entries reading one set of accessors.
    for key in sorted(meshes):
        pos, nrm, idx = meshes[key]
        arrays[key] = {"POSITION": _accessor(doc, blob, pos, "f", 5126, "VEC3", 34962, True),
                       "NORMAL": _accessor(doc, blob, nrm, "f", 5126, "VEC3", 34962)}, \
                      _accessor(doc, blob, idx, "I", 5125, "SCALAR", 34963)

    def material(rgb):
        tag = tuple(round(c, 6) for c in rgb) if rgb else None
        if tag not in materials:
            base = list(tag) + [1.0] if tag else [0.6, 0.6, 0.6, 1.0]
            doc["materials"].append(
                {"name": "gray" if tag is None else "-".join(f"{c:.3f}" for c in tag),
                 "pbrMetallicRoughness": {"baseColorFactor": base, "metallicFactor": 0.1,
                                          "roughnessFactor": 0.55},
                 "doubleSided": True})
            materials[tag] = len(doc["materials"]) - 1
        return materials[tag]

    for node in nodes:
        worn = (node.mesh, material(node.color))
        if worn not in index:
            attributes, indices = arrays[node.mesh]
            doc["meshes"].append({"name": f"{node.mesh}:{worn[1]}",
                                  "primitives": [{"attributes": attributes, "indices": indices,
                                                  "material": worn[1]}]})
            index[worn] = len(doc["meshes"]) - 1
        doc["nodes"].append({"name": node.name, "mesh": index[worn], "matrix": node.matrix})

    # +Z up into glTF's +Y up: -90° about X, as the column-major 16.
    doc["nodes"].insert(0, {"name": "root", "matrix": [1, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0,
                                                       0, 0, 0, 1],
                            "children": list(range(1, len(doc["nodes"]) + 1))})
    doc["buffers"].append({"byteLength": len(blob)})
    return doc, bytes(blob)


def write(assembly, path):
    """One GLB: a JSON chunk of nodes and meshes, then the triangles they index into."""
    doc, blob = gltf(*scene(assembly))
    return write_document(doc, blob, path)


def write_document(doc, blob, path):
    head = json.dumps(doc, separators=(",", ":"), sort_keys=False).encode()
    head += b" " * (-len(head) % 4)
    body = blob + b"\x00" * (-len(blob) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(head) + 8 + len(body)))
        f.write(struct.pack("<II", len(head), 0x4E4F534A)); f.write(head)
        f.write(struct.pack("<II", len(body), 0x004E4942)); f.write(body)
    return path


def selftest():
    """A scene keeps what a payload folds together: the drawn body, and where it stands."""
    import cadquery as cq

    length, width, thick, apart = 18.0, 11.0, 7.0, 60.0
    part = cq.Workplane("XY").box(length, width, thick).faces(">Z").workplane().hole(4.0).val()
    a = cq.Assembly(name="pair")
    a.add(cq.Workplane(obj=part), name="one", color=cq.Color(0.85, 0.78, 0.62))
    a.add(cq.Workplane(obj=part.moved(cq.Location(cq.Vector(apart, 0, 0),
                                                  cq.Vector(0, 0, 1), 37.0))), name="two")

    nodes, meshes = scene(a)
    if len(nodes) != 2:
        raise AssertionError(f"a two-body pack wrote {len(nodes)} nodes")
    if len(meshes) != 1:
        raise AssertionError(f"one drawn body wrote {len(meshes)} meshes — two placements of a "
                             f"body are not meeting at its triangles")
    yield "two placements of one drawn body share one mesh"

    if nodes[1].matrix[12:15] == [0.0, 0.0, 0.0]:
        raise AssertionError("a seated body's node carries no translation — the placement did "
                             "not reach the matrix")
    yield f"a seated node carries its own matrix, at {tuple(round(v, 1) for v in nodes[1].matrix[12:15])}"

    # The triangles are the body's own, so the node's matrix is what stands them up. A payload's
    # are already standing and cannot be re-seated.
    pos = meshes[nodes[0].mesh][0]
    if max(pos[0::3]) > length / 2 + 1e-6:
        raise AssertionError(f"a mesh reaches x={max(pos[0::3]):.3f} on a {length:g} mm body — "
                             f"the triangles carry a placement the matrix also carries")
    yield "a mesh stands in the body's own frame, centred where it was drawn"

    doc, blob = gltf(nodes, meshes)
    if doc["buffers"][0]["byteLength"] != len(blob):
        raise AssertionError("the buffer's stated length is not what was written")
    for acc in doc["accessors"]:
        view = doc["bufferViews"][acc["bufferView"]]
        if view["byteOffset"] % 4:
            raise AssertionError(f"a buffer view starts at {view['byteOffset']}, off the 4-byte "
                                 f"alignment a typed array reads at")
    if len(doc["accessors"]) != 3 * len(meshes):
        raise AssertionError(f"{len(meshes)} drawn bodies wrote {len(doc['accessors'])} "
                             f"accessors — the triangles landed once per placement")
    if any(n["mesh"] >= len(doc["meshes"]) for n in doc["nodes"][1:]):
        raise AssertionError("a node points past the meshes written")
    if len(set(n["mesh"] for n in doc["nodes"][1:])) != len(doc["meshes"]):
        raise AssertionError(f"{len(doc['meshes'])} mesh entries for "
                             f"{len(set(n['mesh'] for n in doc['nodes'][1:]))} in use — the file "
                             f"carries an entry nothing stands over")
    yield (f"{len(doc['meshes'])} mesh entries over {len(doc['accessors'])} accessors, "
           f"{len(doc['nodes'])} nodes, {len(blob)} bytes, aligned")

    import tempfile
    import pathlib
    with tempfile.TemporaryDirectory() as d:
        out = write(a, str(pathlib.Path(d) / "pair.glb"))
        raw = open(out, "rb").read()
        magic, version, total = struct.unpack("<III", raw[:12])
        if magic != 0x46546C67 or version != 2 or total != len(raw):
            raise AssertionError(f"the header reads magic {magic:#x} version {version} length "
                                 f"{total} over {len(raw)} bytes on disk")
    yield "a GLB's header describes the file that carries it"


def _from_module(path):
    """The scene of the assembly a layout script builds, written beside its STEP."""
    import importlib.util
    import pathlib

    path = pathlib.Path(path).resolve()
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    builder = next(getattr(module, n) for n in dir(module)
                   if n.startswith("build_") and n.endswith("_assembly"))
    out = path.parent / (path.stem.replace("_", "-") + ".glb")
    nodes, meshes = scene(builder())
    doc, blob = gltf(nodes, meshes)
    write_document(doc, blob, out)
    print(f"-> {out.name}  {len(nodes)} nodes over {len(meshes)} drawn bodies, "
          f"{out.stat().st_size / 1e6:.1f} MB")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        for line in selftest():
            print(" ", line)
        print("_scene selftest OK")
    elif len(sys.argv) == 2:
        _from_module(sys.argv[1])
    else:
        print(__doc__)
        print("usage: _scene.py selftest | _scene.py <layout script>")
