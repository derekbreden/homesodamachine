"""Hand the viewer the tessellation the generator already had.

A grid thumbnail is the /3d viewer's own render of a part
(tools/render/render-thumbnails.js drives it headlessly), and the viewer gets
its geometry by reading the STEP through occt-import-js in wasm. That read is
the whole cost of a thumbnail: on the enclosure assembly it is ~13 s against
~1 s for the tessellation that produced the STEP in the first place. The
generator is still holding the shape when it queues the thumbnail, so the
parse buys nothing but a round trip through text.

This module tessellates that shape into the same `meshes[]` occt-import-js
returns — one entry per solid, carrying its name, its color, positions,
normals and indices — and packs it for the browser to unpack (the reader is
`decodeMeshPayload` in web/public/js/viewer/step.js). Everything downstream of
`meshes[]` is untouched: the same buildMesh, the same x-ray shading, the same
camera. Where the triangles came from cannot change how the part looks.

Deflections and colors match what occt-import-js hands the viewer when it
passes no parameters, so the two routes agree on what a part looks like. They
do not agree triangle for triangle, and cannot: occt meshes the BREP a STEP
reconstructs, this meshes the BREP that was written to it, and a surface that
went out analytic can come back a spline that tessellates differently. Handed
the same BREP the two are within 0.5%; handed the original the enclosure
assembly comes out 3.6% lighter, which moves ~1.5% of the thumbnail's pixels
by an edge's width and nothing else. `selftest` holds the same-BREP agreement,
which is the half that can regress.
"""

import json
import os
import struct
from pathlib import Path

from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Bnd import Bnd_Box
from OCP.Precision import Precision
from OCP.Quantity import Quantity_TypeOfColor
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS, TopoDS_Compound

# What the viewer gets by calling ReadStepFile(buffer, null): a linear
# deflection stated as a ratio of the model's size, and an angular deflection
# in radians. Transcribed from TriangulateShape in occt-import-js's
# src/importer-utils.cpp — a ratio of the mean of the three bounding-box
# extents, not of its diagonal, and the box taken without triangulation.
LINEAR_DEFLECTION_RATIO = 0.001
ANGULAR_DEFLECTION = 0.5


def deflection(shape) -> float:
    """The absolute linear deflection occt-import-js would mesh this shape at.

    Taken once for the whole model, so a part's triangles depend on the model
    it sits in exactly as they do there."""
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, False)
    if box.IsVoid():
        return 1.0
    xm, ym, zm, xM, yM, zM = box.Get()
    linear = ((xM - xm) + (yM - ym) + (zM - zm)) / 3.0 * LINEAR_DEFLECTION_RATIO
    # A model too small to have a meaningful ratio falls back to 1 mm, as there.
    return linear if linear >= Precision.Confusion_s() else 1.0


def _mesh_all(solids, linear: float):
    """Triangulate every solid in one pass, as occt-import-js does — it meshes
    the whole shape it read, not one solid at a time, and BRepMesh derives its
    minimum element size from the shape it is handed, so solid-by-solid and
    all-at-once do not produce the same triangles.

    What is meshed is a COPY of each solid, and the copies are returned as what
    carries the triangulation. BRepMesh stores triangles on the faces of the
    shape it is given, and those faces belong to the caller's live model — this
    runs at export time, off `export_step`, so meshing in place would hand a
    generator back a part it has not finished measuring. An OCCT bounding box
    prefers a triangulation when one is present, so the next `BoundingBox()` on
    that model reads the mesh's box, wider than the analytic one by the linear
    deflection. A part exported and then checked against its own nominal extents
    would fail on a tolerance it never left."""
    copies = [BRepBuilderAPI_Copy(solid.wrapped).Shape() for solid in solids]
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    for copy in copies:
        builder.Add(compound, copy)
    BRepMesh_IncrementalMesh(compound, linear, False, ANGULAR_DEFLECTION, True)
    return copies


def _solid_arrays(shape):
    """Flat (positions, normals, indices) for one already-triangulated TopoDS
    shape, in world coordinates, with reversed faces flipped so every normal
    points out."""
    pos, nrm, idx = [], [], []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        exp.Next()
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:  # a face BRepMesh could not mesh contributes nothing
            continue
        tri.ComputeNormals()
        trsf = loc.Transformation()
        flip = face.Orientation() == TopAbs_REVERSED
        base = len(pos) // 3
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf)
            pos += [p.X(), p.Y(), p.Z()]
            n = tri.Normal(i).Transformed(trsf)
            s = -1.0 if flip else 1.0
            nrm += [n.X() * s, n.Y() * s, n.Z() * s]
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            if flip:
                a, c = c, a
            idx += [base + a - 1, base + b - 1, base + c - 1]
    return pos, nrm, idx


def _mesh(shape, name, color):
    pos, nrm, idx = _solid_arrays(shape)
    if not idx:
        return None
    # Linear RGB, not cq.Color.toTuple()'s sRGB: a color written to STEP and read
    # back through occt-import-js arrives linear, and that round trip is what the
    # viewer has always shaded. Handing over sRGB would wash every part out.
    rgb = list(color.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB)) if color else None
    return {"name": name, "color": rgb, "pos": pos, "nrm": nrm, "idx": idx}


def _placed(node, parent_loc=None):
    """Every shape-bearing node of an assembly, with its world location, its own
    color, and the solids it contributes."""
    loc = node.loc if parent_loc is None else parent_loc * node.loc
    if node.obj is not None:
        # A node holds either a Shape or the Workplane it was added as.
        vals = node.obj.vals() if hasattr(node.obj, "vals") else [node.obj]
        solids = [s for v in vals for s in v.moved(loc).Solids()]
        if solids:
            yield node.name, node.color, solids
    for child in node.children:
        yield from _placed(child, loc)


def from_assembly(assembly):
    """One mesh per solid of a cq.Assembly, in world position, colored the way
    the STEP the viewer reads carries the color.

    A STEP carries an assembly's color only where a component is a single solid.
    Give a component several — the reference sub-assemblies, the valve-manifold
    trays — and the color lands on a node whose leaves occt-import-js reports
    uncolored, so the viewer draws them default gray. Colouring them here
    instead would repaint ~50 solids of the enclosure that its detail view
    leaves gray, which is the one thing a handed-over tessellation must not do.
    An ancestor's color never reaches a leaf through a STEP either, and never
    reaches one here, because only a node's own color is read.

    occt-import-js names a mesh after its component (backfillMeshNames in
    step.js walks the STEP's node tree to do it); the assembly knows the name
    directly, so the leaf of its path is used.
    """
    placed = [(name.split("/")[-1], color if len(solids) == 1 else None, solid)
              for name, color, solids in _placed(assembly) for solid in solids]
    meshed = _mesh_all([s for _, _, s in placed], deflection(assembly.toCompound().wrapped))
    return [m for (name, color, _), solid in zip(placed, meshed)
            if (m := _mesh(solid, name, color))]


def from_shape(model):
    """One mesh per solid of a plain workplane/shape. These carry no color —
    matching a STEP from export_step, which the viewer shades default gray."""
    shape = model.val() if hasattr(model, "val") else model
    meshed = _mesh_all(shape.Solids(), deflection(shape.wrapped))
    return [m for solid in meshed if (m := _mesh(solid, "", None))]


def write(meshes, path):
    """u32 header length, that many bytes of JSON, then one blob every array
    indexes into by [byteOffset, length]. Typed-array offsets must be aligned
    to their element size, and every array here is 4 bytes wide, so the header
    is padded to a multiple of 4 and the blob stays aligned throughout."""
    entries, blob = [], bytearray()
    for m in meshes:
        e = {"name": m["name"], "color": m["color"]}
        for key, fmt, arr in (("pos", "f", m["pos"]), ("nrm", "f", m["nrm"]),
                              ("idx", "I", m["idx"])):
            e[key] = [len(blob), len(arr)]
            blob += struct.pack(f"<{len(arr)}{fmt}", *arr)
        entries.append(e)
    head = json.dumps({"meshes": entries}, separators=(",", ":")).encode()
    head += b" " * (-(len(head) + 4) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<I", len(head)))
        f.write(head)
        f.write(blob)


# --- selftest ----------------------------------------------------------------
#
# What is being protected is an agreement with a second implementation: every
# thumbnail this module feeds has to look like the one the viewer would have
# drawn from the STEP. Each check below is a way that agreement has broken or
# could break silently — the pixels stay plausible and only the part changes.


def _selftest():
    import subprocess
    import tempfile
    import cadquery as cq

    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append((ok, name, got, want))
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got!r}" + ("" if ok else f" != {want!r}"))

    # The deflection occt-import-js would use: the mean of the three extents
    # times the ratio. A 10x20x60 box averages 30, so 0.03mm.
    box = cq.Workplane("XY").box(10, 20, 60)
    check("deflection of a 10x20x60 box", round(deflection(box.val().wrapped), 6), 0.03)

    # Colors reach the viewer linear, the way a STEP round trip delivers them.
    # sRGB 0.85 is linear 0.6921; handing over 0.85 washes the part out.
    solid = box.val().Solids()[0]
    meshed = _mesh_all([solid], 0.03)

    # Meshing must leave the CALLER's shape alone. This runs at export time on a
    # generator's live model, and an OCCT bounding box prefers a triangulation
    # when it finds one — so a mesh stored on these faces widens every extent the
    # generator goes on to measure itself against, by the linear deflection.
    bb = solid.BoundingBox()
    check("the caller's solid is left untriangulated",
          [round(v, 9) for v in (bb.xlen, bb.ylen, bb.zlen)], [10.0, 20.0, 60.0])

    mesh = _mesh(meshed[0], "b", cq.Color(0.85, 0.78, 0.62))
    check("color is linear, not sRGB", [round(c, 4) for c in mesh["color"]],
          [0.6921, 0.5705, 0.3424])

    # A box is 6 quads, and every normal points away from its centre. A face
    # whose REVERSED orientation went unhonoured lights from the inside instead,
    # which reads as a hole in the part rather than as an error.
    check("box tessellates to 12 triangles", len(mesh["idx"]) // 3, 12)
    p, n = mesh["pos"], mesh["nrm"]
    outward = sum(p[i] * n[i] + p[i + 1] * n[i + 1] + p[i + 2] * n[i + 2] > 0
                  for i in range(0, len(p), 3))
    check("every box normal points outward", outward, len(p) // 3)

    # An assembly yields one mesh per solid, carrying the name it was added
    # under, placed where the assembly places it — and colored the way a STEP
    # carries the color, which is narrower than the assembly knows. The three
    # negatives below are each a way the viewer ends up drawing a solid gray;
    # painting it here instead makes the thumbnail a picture of a part the
    # detail view will not show. Nested `leaf` sits at 30+20 to catch a
    # location applied once.
    sub = cq.Assembly(name="sub", color=cq.Color(1, 0, 0), loc=cq.Location((30, 0, 0)))
    sub.add(cq.Workplane("XY").box(2, 2, 2).translate((20, 0, 0)), name="leaf")
    pair = cq.Compound.makeCompound([cq.Workplane("XY").box(2, 2, 2).translate((x, 0, 0)).val()
                                     for x in (60, 66)])
    assy = cq.Assembly()
    # Not a primary: 0 and 1 are fixed points of the sRGB transfer, so a pure
    # blue here would round-trip identically whether or not the color space is
    # right, and the round-trip check below would have nothing to catch.
    assy.add(cq.Workplane("XY").box(4, 4, 4), name="a", color=cq.Color(0.85, 0.78, 0.62))
    assy.add(cq.Workplane("XY").box(2, 2, 2).translate((10, 0, 0)), name="b")
    assy.add(sub)
    assy.add(pair, name="pair", color=cq.Color(0, 1, 0))
    meshes = from_assembly(assy)
    check("one mesh per assembly solid",
          [m["name"] for m in meshes], ["a", "b", "leaf", "pair", "pair"])
    check("a single-solid child keeps its own color",
          [round(c, 4) for c in meshes[0]["color"]], [0.6921, 0.5705, 0.3424])
    check("an uncolored child carries no color", meshes[1]["color"], None)
    check("a sub-assembly's color does not reach its leaf", meshes[2]["color"], None)
    check("a multi-solid child's color reaches neither solid",
          [meshes[3]["color"], meshes[4]["color"]], [None, None])
    xs = meshes[2]["pos"][0::3]
    check("nested location applied once", [round(min(xs)), round(max(xs))], [49, 51])

    # The header is padded so every typed array in the blob stays 4-byte aligned;
    # a misaligned offset is a DOMException in the browser, not a wrong picture.
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.mesh")
        write(meshes, path)
        raw = open(path, "rb").read()
        head_len = struct.unpack("<I", raw[:4])[0]
        head = json.loads(raw[4:4 + head_len])
        check("header ends 4-byte aligned", (4 + head_len) % 4, 0)
        check("every array offset is 4-byte aligned",
              sorted({e[k][0] % 4 for e in head["meshes"] for k in ("pos", "nrm", "idx")}), [0])
        check("blob holds exactly what the header indexes",
              len(raw) - 4 - head_len,
              max(e[k][0] + e[k][1] * 4 for e in head["meshes"] for k in ("pos", "nrm", "idx")))

    # The controls that matter, and the only ones that can see the thing this
    # module is actually claiming: ask the other implementation. Everything
    # above is a belief about what a STEP carries; these two check it against
    # the occt-import-js the viewer runs.
    if not _OCCT_PKG.exists():
        print("  skip occt-import-js cross-checks (the vendored package is absent)")
    else:
        def occt(step):
            return json.loads(subprocess.run(
                ["node", "-e", _OCCT_PROBE, str(step)], cwd=str(_OCCT_PKG.parent),
                capture_output=True, text=True, check=True).stdout)

        # Same BREP, both tessellators: the deflection constants are right only
        # if these land together. An upstream change to occt-import-js's
        # defaults shows up here and nowhere else.
        if _REF_STEP.exists():
            mine = from_shape(cq.importers.importStep(str(_REF_STEP)))
            js = occt(_REF_STEP)
            check(f"{_REF_STEP.name}: solid count matches occt-import-js", len(mine), js["meshes"])
            off = abs(sum(len(m["idx"]) // 3 for m in mine) - js["tris"]) / max(js["tris"], 1)
            check(f"{_REF_STEP.name}: triangles within 1% of occt-import-js", off < 0.01, True)

        # And the colors: export the assembly built above, read it back the way
        # the viewer does, and require that what is handed over is what would
        # have been read. This is what the single-solid rule and the linear
        # color space are for, and it holds them against the round trip rather
        # than against what this file believes about it.
        with tempfile.TemporaryDirectory() as d:
            step = os.path.join(d, "roundtrip.step")
            assy.export(step)
            seen = [tuple(round(c, 3) for c in m["color"]) if m["color"] else None
                    for m in occt(step)["colors"]]
            check("colors survive the STEP round trip exactly as handed over",
                  sorted(seen, key=str),
                  sorted((tuple(round(c, 3) for c in m["color"]) if m["color"] else None
                          for m in meshes), key=str))

    bad = [c for c in checks if not c[0]]
    print(f"\n{len(checks) - len(bad)}/{len(checks)} checks passed")
    return 1 if bad else 0


_REF_STEP = (Path(__file__).resolve().parent.parent
             / "printed-parts/faucet/touch-flo-shell/touch-flo-shell.step")
_OCCT_PKG = (Path(__file__).resolve().parent.parent
             / "pcb/pcba/node_modules/occt-import-js")
_OCCT_PROBE = """
const fs = require('fs');
require('occt-import-js')().then((occt) => {
  const r = occt.ReadStepFile(new Uint8Array(fs.readFileSync(process.argv[1])), null);
  console.log(JSON.stringify({ meshes: r.meshes.length,
    tris: r.meshes.reduce((s, m) => s + m.index.array.length / 3, 0),
    colors: r.meshes.map((m) => ({ color: m.color || null })) }));
});
"""


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["selftest"]:
        raise SystemExit(_selftest())
    print(__doc__)
    print("usage: _mesh_payload.py selftest")
