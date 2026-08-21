"""The enclosure's flutes, in the triangles every picture is drawn from.

`printed-parts/enclosure/enclosure/flute_skin.py` cuts the show surfaces into the MESH and says
why they are not in the solid. The STEP beside that mesh is a smooth prism — 343 faces on the
front-top piece, every one a plane or a cylinder — so a reader who is handed the solid is handed
a box with no texture on it.

THE VIEWER PREFERS A PAYLOAD TO THE STEP BESIDE IT. `loadStepFile` fetches `<file>.step.mesh`
first and only parses the solid when there is none (`web/public/js/viewer/step.js`), and every
picture this repository draws goes through that one mount: `/3d` in a browser,
`tools/render/render-step-posed.js` driving the same page headless for the assembly cards,
`render-thumbnails.js` for the grid. So the flutes reach all of them by standing in the payload,
and nothing above it is touched — same card, same part, same camera, same x-ray, same pickable
edges.

WHAT IS DECIMATED TO IS THE VIEWER'S OWN TOLERANCE. `_mesh_payload.LINEAR_DEFLECTION_RATIO` is
the deflection occt-import-js meshes a STEP at, which is what every other part in the catalog is
already drawn at; a piece is reduced as far as it will go while every point of the printed mesh
stays inside that distance of the result, measured exactly rather than sampled. On the front-top
piece that is 676,188 facets down to 53,492 at 0.147 mm against a 0.206 mm budget, and the
groove comes through at its full depth. The printed mesh is what a slicer reads and is
untouched — it is this file's input.

SHADING BREAKS WHERE THE VIEWER DRAWS A LINE. `xray.js` draws a feature edge at a 30° crease, so
the normals are split on the same angle: a groove shades round, the arris between it and its land
stays hard, and a box corner does not smear. The smooth regions that split produces are the
payload's face ranges too — `fac` is what the edge picker reconstructs BREP edges out of
(`edge-picker.js`), and on a surface with no BREP left those regions are the faces it has.

A NAME AND A COLOUR ARE READ OFF THE SOLID, not chosen here. `export_assembly` writes the piece's
name as its `PRODUCT` and its colour as the one `COLOUR_RGB` in the file, and `cq.Color` converts
that sRGB to the linear a STEP round trip delivers — the same expression `_mesh_payload` shades
every other part through. A picture drawn from this payload is the picture the STEP would have
drawn, with the surface it actually has.

    tools/cad-venv/bin/python hardware/scripts/flute_payload.py
    tools/cad-venv/bin/python hardware/scripts/flute_payload.py selftest
"""

import json
import re
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mesh_payload                                                    # noqa: E402

_ROOT = Path(__file__).resolve().parent.parent.parent

#: Where a printed mesh stands beside the solid it was cut from. A piece is any `.step` here with
#: an `.stl` of the same stem — so a seventh piece is carried with no edit to this file.
PIECES_DIR = _ROOT / "hardware/printed-parts/enclosure/enclosure"

#: The crease `xray.js` draws a feature edge at, in degrees.
CREASE_DEG = 30.0

#: Reductions tried, hardest first. `fast_simplification` refuses collapses it cannot make and
#: returns what it reached, so the ladder is short: the run takes the first rung that holds.
LADDER = (0.97, 0.95, 0.90, 0.80, 0.60, 0.0)

#: How aggressively to collapse. Below the library's default of 7, which trades the run's speed
#: for the shape — at 7 the front-top piece leaves the deflection budget by a factor of thirty.
AGGRESSION = 4.0

#: Points of the printed mesh the deviation is measured at. Every vertex is the exact answer and
#: costs minutes on a million-facet piece; this is drawn without replacement and is the same
#: draw every run, so a reading is reproducible.
PROBE_POINTS = 40000


def deflection(mesh) -> float:
    """The distance the printed surface may stand from the payload's.

    occt-import-js meshes a STEP at a ratio of the mean of its three bounding-box extents
    (`_mesh_payload.LINEAR_DEFLECTION_RATIO`), so this is the tolerance the viewer is already
    drawing every un-fluted part in the catalog at."""
    return float(mesh.bounding_box.extents.mean()) * _mesh_payload.LINEAR_DEFLECTION_RATIO


def deviation(printed, reduced) -> float:
    """The furthest any probed point of `printed` stands from the surface of `reduced`.

    POINT TO SURFACE, NOT POINT TO POINT. A nearest-vertex reading falls to the sampling spacing
    of whichever mesh is denser and reports that instead of the error — it holds flat across a
    tenfold reduction and says nothing. This is the closest point on a triangle."""
    rng = np.random.default_rng(0)
    n = min(PROBE_POINTS, len(printed.vertices))
    probe = printed.vertices[rng.choice(len(printed.vertices), n, replace=False)]
    return float(trimesh.proximity.closest_point(reduced, probe)[1].max())


def simplify_within(printed, bound):
    """`printed` collapsed as far as the ladder reaches while staying inside `bound`.

    Returns the mesh and the reading it was accepted on. A piece already inside the budget at
    full size — the pump cap is 1,704 facets — comes back untouched, because the last rung of
    the ladder is no reduction at all."""
    import fast_simplification

    v32 = printed.vertices.astype(np.float32)
    f32 = printed.faces.astype(np.uint32)
    for rung in LADDER:
        if rung <= 0.0:
            return printed, 0.0
        v, f = fast_simplification.simplify(v32, f32, rung, agg=AGGRESSION)
        reduced = trimesh.Trimesh(v, f, process=False)
        dev = deviation(printed, reduced)
        if dev <= bound:
            return reduced, dev
    return printed, 0.0


def creased(mesh, angle_deg=CREASE_DEG):
    """`mesh` as (positions, normals, indices, face ranges), split at creases.

    A CORNER BELONGS TO ITS OWN SMOOTH REGION. Faces joined across an edge gentler than
    `angle_deg` are one region; a vertex on the boundary between two regions is emitted once per
    region and takes each one's normal, so the groove either side of an arris shades round and
    the arris itself stays hard. Averaging over the whole ring instead rounds every box corner
    into a smear.

    THE TRIANGLES ARE ORDERED BY REGION, which is what makes `fac` expressible: it is a flat
    [first, last, ...] of inclusive triangle indices, one pair per region, and the edge picker
    walks it to decide which segments bound a face."""
    faces = mesh.faces
    pairs = mesh.face_adjacency
    smooth = mesh.face_adjacency_angles <= np.radians(angle_deg)
    n = len(faces)
    if len(pairs):
        kept = pairs[smooth]
        graph = coo_matrix((np.ones(len(kept), dtype=np.int8), (kept[:, 0], kept[:, 1])),
                           shape=(n, n))
    else:
        graph = coo_matrix((n, n), dtype=np.int8)
    _count, region = connected_components(graph, directed=False)

    order = np.argsort(region, kind="stable")
    faces = faces[order]
    region = region[order]
    normals = mesh.face_normals[order]
    # Area-weighted, so a region's many slivers do not outvote its one large triangle.
    weight = mesh.area_faces[order][:, None]

    # A corner is (its vertex, its face's region); the unique set of those is the new vertices.
    corner = np.stack([faces.ravel(), np.repeat(region, 3)], axis=1)
    _uniq, inverse = np.unique(corner, axis=0, return_inverse=True)
    inverse = inverse.ravel()
    idx = inverse.reshape(-1, 3)

    pos = np.zeros((inverse.max() + 1, 3), dtype=np.float64)
    pos[inverse] = mesh.vertices[faces.ravel()]
    nrm = np.zeros_like(pos)
    np.add.at(nrm, inverse, np.repeat(normals * weight, 3, axis=0))
    length = np.linalg.norm(nrm, axis=1)
    # A region of zero total area leaves nothing to normalise; its own face normal stands.
    blank = length < 1e-12
    if blank.any():
        nrm[blank] = np.repeat(normals, 3, axis=0)[np.isin(inverse, np.flatnonzero(blank))][:1] \
            if blank.sum() == 1 else np.array([0.0, 0.0, 1.0])
        length = np.linalg.norm(nrm, axis=1)
    nrm = nrm / length[:, None]

    # One [first, last] per run of equal region in the ordered triangles.
    edges = np.flatnonzero(np.diff(region)) + 1
    firsts = np.concatenate([[0], edges])
    lasts = np.concatenate([edges - 1, [len(region) - 1]])
    fac = np.stack([firsts, lasts], axis=1).ravel()
    return pos, nrm, idx, fac


def solid_identity(step: Path):
    """The name and the linear colour the viewer reads off `step`.

    `export_assembly` writes the piece under its own `PRODUCT` and gives it the file's one
    `COLOUR_RGB`, in sRGB. `cq.Color` is what converts that to the linear a STEP round trip
    delivers — the same expression `_mesh_payload._mesh` shades every other part through, so a
    payload written here and one written there agree on the colour by construction."""
    import cadquery as cq
    from OCP.Quantity import Quantity_TypeOfColor

    text = step.read_text(errors="ignore")
    names = [n for n in re.findall(r"PRODUCT\('([^']*)'", text) if not n.startswith("Open CASCADE")]
    rgbs = set(re.findall(r"COLOUR_RGB\('',([\d.eE+-]+),([\d.eE+-]+),([\d.eE+-]+)\)", text))
    if len(names) != 1:
        raise ValueError(f"{step.name}: {len(names)} named products, expected the piece's own")
    if len(rgbs) != 1:
        raise ValueError(f"{step.name}: {len(rgbs)} colours, expected the piece's own")
    srgb = [float(c) for c in next(iter(rgbs))]
    linear = list(cq.Color(*srgb).wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB))
    return names[0], linear


def pieces(directory=PIECES_DIR):
    """Every solid in `directory` that has a printed mesh beside it, as (step, stl) pairs."""
    out = []
    for step in sorted(directory.glob("*.step")):
        stl = step.with_suffix(".stl")
        if stl.is_file():
            out.append((step, stl))
    return out


def surfaces(directory=PIECES_DIR):
    """The fluted surfaces standing on this disk, keyed by the name a payload holds them under.

    What `graft` is handed. A tree that has not cut them yet answers with nothing, and a graft
    of nothing leaves every payload as it stands — which is the smooth solid, and is what a
    machine with no printed mesh could draw anyway."""
    out = {}
    for step, _stl in pieces(directory):
        held = read_payload(step.with_name(step.name + ".mesh"))
        if held and len(held) == 1:
            out[held[0]["name"]] = held[0]
    return out


#: How far a grafted surface may stand from the bodies it replaces. A piece is cut where the
#: assembly stands it, so the two agree to a tessellation's deflection and nothing more; a
#: reading past this is a body landing somewhere its own solid does not.
PLACEMENT_TOL = 0.5


def graft_glb(path, fluted):
    """Put the fluted surfaces into the scene mesh at `path`, in place. Returns how many landed.

    A `.glb` IS WHAT /3d OPENS A BENCH SCENE AS — `parts.js` hands one to `openGlbDetail`, and
    there is no STEP behind it to fall back to, so a scene mesh cut from the B-rep is the last
    place a piece is still drawn smooth.

    cadquery WRITES ONE MESH PER BREP FACE, so a piece arrives as hundreds of patches named
    `<piece>`, `<piece>_1`, `<piece>_2` … under one node. All of them go and the payload's single
    body stands in their place, keeping that node's transform and the material the patches were
    painted with — the scene decides where a body stands and what colour it is, and swapping the
    surface is not swapping which part it is.

    THE TRIANGLES NEED NO TURNING. A glTF file holds its geometry in the model's own frame and
    puts the Y-up convention in the node graph above it, so the payload's positions drop in as
    they stand. `PLACEMENT_TOL` is what says so rather than this comment: the body that lands
    has to occupy the box the bodies it replaced occupied."""
    scene = trimesh.load(str(path))
    landed = 0
    for name, surface in fluted.items():
        members = [k for k in scene.geometry if k == name or k.startswith(name + "_")]
        if not members:
            continue
        node = scene.graph.geometry_nodes[members[0]][0]
        transform = scene.graph.get(frame_to=node)[0]
        material = getattr(scene.geometry[members[0]].visual, "material", None)
        low = np.min([scene.geometry[k].bounds[0] for k in members], axis=0)
        high = np.max([scene.geometry[k].bounds[1] for k in members], axis=0)
        for k in members:
            scene.delete_geometry(k)
        pos = np.asarray(surface["pos"], dtype=np.float64).reshape(-1, 3)
        idx = np.asarray(surface["idx"], dtype=np.int64).reshape(-1, 3)
        nrm = np.asarray(surface["nrm"], dtype=np.float64).reshape(-1, 3)
        mesh = trimesh.Trimesh(pos, idx, vertex_normals=nrm, process=False)
        if material is not None:
            mesh.visual = trimesh.visual.TextureVisuals(material=material)
        drift = max(float(np.abs(mesh.bounds[0] - low).max()),
                    float(np.abs(mesh.bounds[1] - high).max()))
        if drift > PLACEMENT_TOL:
            raise ValueError(
                f"{Path(path).name}: {name}'s surface stands {drift:.3f} mm from the "
                f"{len(members)} bodies it replaces, past {PLACEMENT_TOL} mm — a piece drawn "
                f"somewhere its own solid is not.")
        scene.add_geometry(mesh, node_name=name, geom_name=name, transform=transform)
        landed += 1
    if landed:
        scene.export(str(path))
    return landed


def cut(step: Path, stl: Path, verbose=True):
    """Write the payload beside `step` out of the printed mesh at `stl`. Returns the mesh."""
    printed = trimesh.load_mesh(str(stl))
    printed.merge_vertices()
    bound = deflection(printed)
    reduced, dev = simplify_within(printed, bound)
    pos, nrm, idx, fac = creased(reduced)
    name, color = solid_identity(step)
    mesh = {"name": name, "color": color,
            "pos": pos.ravel().tolist(), "nrm": nrm.ravel().tolist(),
            "idx": idx.ravel().tolist(), "fac": fac.tolist()}
    out = step.with_name(step.name + ".mesh")
    _mesh_payload.write([mesh], str(out))
    if verbose:
        print(f"-> {out.name}  {len(printed.faces)} -> {len(reduced.faces)} facets, "
              f"{len(pos)} vertices, {len(fac) // 2} regions, "
              f"{out.stat().st_size / 1e6:.2f} MB, "
              f"{dev:.3f} mm inside a {bound:.3f} mm budget")
    return mesh


def read_payload(path):
    """The meshes `_mesh_payload.write` put in `path`, or None for anything else.

    The reader the page runs is `decodeMeshPayload` in `web/public/js/viewer/step.js`; this is
    the same header and the same four arrays, off the same offsets."""
    try:
        raw = Path(path).read_bytes()
        head_len = struct.unpack("<I", raw[:4])[0]
        head = json.loads(raw[4:4 + head_len])
    except (OSError, ValueError, struct.error):
        return None
    if head.get("v") != _mesh_payload.VERSION:
        return None
    blob = raw[4 + head_len:]
    out = []
    for m in head["meshes"]:
        entry = {"name": m["name"], "color": m["color"]}
        for key, dtype in (("pos", "<f4"), ("nrm", "<f4"), ("idx", "<u4"), ("fac", "<u4")):
            offset, count = m[key]
            entry[key] = np.frombuffer(blob, dtype=dtype, count=count, offset=offset).tolist()
        out.append(entry)
    return out


def payload_names(path):
    """The names the payload at `path` holds, off its header alone.

    A payload is up to fourteen megabytes of triangles behind a few hundred bytes of JSON, and
    asking which bodies it holds is a question the header answers."""
    try:
        with open(path, "rb") as fh:
            head_len = struct.unpack("<I", fh.read(4))[0]
            head = json.loads(fh.read(head_len))
    except (OSError, ValueError, struct.error):
        return []
    if head.get("v") != _mesh_payload.VERSION:
        return []
    return [m["name"] for m in head["meshes"]]


def piece_names(directory=PIECES_DIR):
    """The names the fluted pieces standing on this disk are held under.

    What a caller asks when it needs to know whether a payload holds a surface its solid does
    not — cheaper than `surfaces`, which decodes the triangles as well."""
    out = set()
    for step, _stl in pieces(directory):
        out.update(payload_names(step.with_name(step.name + ".mesh")))
    return out


def graft(path: Path, fluted: dict):
    """Put the fluted surfaces into the payload at `path`, in place. Returns how many landed.

    A PIECE IS THE SAME BODY WHEREVER IT IS PLACED. `enclosure.py` cuts the printed mesh off the
    piece as the assembly stands it, so the triangles here are already in the coordinates every
    payload that holds that piece places it at — the assembled box, the whole appliance, and each
    bench scene agree with the piece's own solid to within a tessellation's deflection.

    THE HOST KEEPS ITS OWN NAME AND COLOUR. A body is coloured by the assembly that places it,
    and swapping the surface is not swapping which part it is."""
    held = read_payload(path)
    if held is None:
        return 0
    landed = 0
    for entry in held:
        surface = fluted.get(entry["name"].replace("_", "-"))
        if surface is None:
            continue
        entry.update({k: surface[k] for k in ("pos", "nrm", "idx", "fac")})
        landed += 1
    if not landed:
        return 0
    # BYTES THAT DID NOT MOVE DO NOT MOVE THE FILE. A payload rewritten identically takes a new
    # mtime, and every reader that keyed off it — the ETag the page revalidates against, the
    # `_current` comparison `_cadq_export` skips a re-tessellation on — reads a change that did
    # not happen. `render_scenes.write_payload` holds the same property for the payload it cuts.
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    _mesh_payload.write(held, str(tmp))
    if path.is_file() and path.read_bytes() == tmp.read_bytes():
        tmp.unlink()
    else:
        tmp.replace(path)
    return landed


def main():
    found = pieces()
    if not found:
        raise SystemExit(f"no printed meshes beside the solids in {PIECES_DIR}")
    fluted = {}
    for step, stl in found:
        mesh = cut(step, stl)
        fluted[mesh["name"]] = mesh

    # AND INTO THE BOX THE SIX OF THEM MAKE. `enclosure.py` writes `enclosure.step` and the
    # payload beside it off the same B-rep the pieces come out of, so that payload holds all six
    # as smooth prisms and this is where they get their surface back.
    #
    # A PAYLOAD IS GRAFTED BY WHOEVER WRITES IT. Everywhere else the run that cuts one does its
    # own graft as it goes — `manifold-layout/enclosure_assembly.py` for the appliance,
    # `assembly/scenes/render_scenes.py` for each bench scene — so nothing here walks the tree
    # looking for them, and this reads one directory.
    cut_here = {step.name + ".mesh" for step, _ in found}
    for path in sorted(PIECES_DIR.glob("*.step.mesh")):
        if path.name in cut_here:
            continue
        landed = graft(path, fluted)
        if landed:
            print(f"-> {path.relative_to(_ROOT)}  {landed} piece(s) grafted, "
                  f"{path.stat().st_size / 1e6:.2f} MB")
    return 0


# --- selftest ----------------------------------------------------------------
#
# What is being protected is that the payload draws the surface a slicer prints. Each check below
# is a way that can break while the file still decodes and the picture still looks like a box.


def _ridged_slab(pitch=5.0, depth=1.2, width=215.0, height=195.0, thick=10.0, nx=601, nz=121):
    """A closed slab with a half-round groove field on one face, at the enclosure's own figures.

    THE SHAPE OF THE THING THIS FILE HAS TO KEEP, with none of the enclosure in it: a show face
    carrying `depth` grooves on `pitch` centres, a flat back, and four walls closing it."""
    x = np.linspace(0, width, nx)
    z = np.linspace(0, height, nz)
    xs, zs = np.meshgrid(x, z)
    across = (xs + pitch / 2.0) % pitch - pitch / 2.0
    ys = -depth * np.sqrt(np.clip(1.0 - (across / (pitch * 0.4)) ** 2, 0.0, None))
    face = np.stack([xs, ys, zs], axis=-1).reshape(-1, 3)
    back = np.stack([xs, np.full_like(xs, -thick), zs], axis=-1).reshape(-1, 3)
    verts = np.vstack([face, back])
    n = nx * nz

    def sheet(base):
        a = (np.arange(nz - 1)[:, None] * nx + np.arange(nx - 1)[None, :]).ravel() + base
        return np.vstack([np.stack([a, a + 1, a + nx], -1),
                          np.stack([a + 1, a + nx + 1, a + nx], -1)])

    def wall(ring):
        """Quads joining a border run of the face to the same run of the back."""
        a, b = ring[:-1], ring[1:]
        return np.vstack([np.stack([a, b, b + n], -1), np.stack([a, b + n, a + n], -1)])

    rows, cols = np.arange(nz), np.arange(nx)
    borders = [cols, cols + (nz - 1) * nx, rows * nx, rows * nx + (nx - 1)]
    faces = np.vstack([sheet(0), sheet(n)] + [wall(r) for r in borders])

    # EVERY TRIANGLE WOUND OUTWARD. `creased` reads the angle between neighbouring normals, so a
    # face wound the other way from its neighbour reads as a 180° crease and splits a smooth
    # region in half. On a slab whose grooves are shallower than it is thick, a face's outward
    # side is the side its centre stands on.
    tri = verts[faces]
    normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    outward = tri.mean(axis=1) - verts.mean(axis=0)
    flip = (normal * outward).sum(axis=1) < 0
    faces[flip] = faces[flip][:, ::-1]
    return trimesh.Trimesh(verts, faces, process=False)


def selftest():
    import json
    import struct
    import tempfile

    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append((ok, name, got, want))
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got!r}" + ("" if ok else f" != {want!r}"))

    # A box's six sides are six smooth regions, and every corner vertex is emitted once per side
    # it touches. Averaged over the ring instead, a corner normal points along the diagonal and
    # the box shades like a sphere.
    box = trimesh.creation.box(extents=(10, 20, 60))
    pos, nrm, idx, fac = creased(box)
    check("a box splits into six regions", len(fac) // 2, 6)
    check("every corner is emitted once per side", len(pos), 24)
    check("region ranges tile the triangles end to end",
          fac.tolist(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    check("every normal is an axis", sorted({abs(round(v, 6)) for v in nrm.ravel()}), [0.0, 1.0])

    # A cylinder's side is one smooth region however many facets it has, and its normals vary
    # across it. A split that fired inside it would shade the barrel faceted.
    cyl = trimesh.creation.cylinder(radius=5, height=20, sections=64)
    _p, cn, _i, cf = creased(cyl)
    check("a cylinder is a barrel and two caps", len(cf) // 2, 3)
    check("barrel normals are not all one direction", len({tuple(np.round(v, 3)) for v in cn}) > 3, True)

    # And the triangles a region names are that region's. An off-by-one here hands the edge
    # picker a face bounded by somebody else's segments.
    faces_in_ranges = sum(cf[i + 1] - cf[i] + 1 for i in range(0, len(cf), 2))
    check("ranges account for every triangle", faces_in_ranges, len(cyl.faces))

    # The deviation reading has to fall when the mesh gets closer, or the budget it gates on
    # means nothing. A sphere against a coarser sphere is a known-answer version of that.
    fine = trimesh.creation.icosphere(subdivisions=4, radius=50)
    coarse = trimesh.creation.icosphere(subdivisions=2, radius=50)
    coarser = trimesh.creation.icosphere(subdivisions=1, radius=50)
    check("deviation falls as the surface gets closer",
          deviation(fine, coarse) < deviation(fine, coarser), True)
    # And it reads the geometry rather than a sampling spacing: a 100 mm ball tessellated at
    # subdivision 2 stands 0.8 mm inside the one at subdivision 4. A point-to-point reading of
    # the same pair answers with whichever mesh is denser and holds there.
    check("deviation of a coarse sphere is a fraction of a millimetre",
          round(deviation(fine, coarse), 1), 0.8)

    # The budget is the viewer's own, not a number chosen here.
    check("deflection is occt-import-js's ratio of the mean extent",
          round(deflection(trimesh.creation.box(extents=(10, 20, 60))), 6), 0.03)

    # And what is written decodes as the payload the page reads: the version it knows, every
    # typed array 4-byte aligned, and the arrays the header indexes actually in the blob.
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "t.step.mesh"
        _mesh_payload.write([{"name": "b", "color": [0.1, 0.2, 0.3],
                              "pos": pos.ravel().tolist(), "nrm": nrm.ravel().tolist(),
                              "idx": idx.ravel().tolist(), "fac": fac.tolist()}], str(path))
        raw = path.read_bytes()
        head_len = struct.unpack("<I", raw[:4])[0]
        head = json.loads(raw[4:4 + head_len])
        check("the page's payload version is stated", head["v"], _mesh_payload.VERSION)
        check("every array offset is 4-byte aligned",
              sorted({e[k][0] % 4 for e in head["meshes"] for k in ("pos", "nrm", "idx", "fac")}),
              [0])
        check("the blob holds exactly what the header indexes",
              len(raw) - 4 - head_len,
              max(e[k][0] + e[k][1] * 4 for e in head["meshes"]
                  for k in ("pos", "nrm", "idx", "fac")))
        check("read_version reads it back", _mesh_payload.read_version(str(path)),
              _mesh_payload.VERSION)

        # A GRAFT PUTS THE SURFACE IN AND LEAVES EVERYTHING ELSE STANDING. A host payload holds
        # bodies this file knows nothing about, and each of them is named and coloured by the
        # assembly that placed it — a graft that took the piece's own name or colour over would
        # rename a part in the scorecard and repaint it in every picture.
        host = Path(d) / "host.step.mesh"
        _mesh_payload.write([
            {"name": "some_piece", "color": [0.5, 0.5, 0.5],
             "pos": [0.0] * 9, "nrm": [0.0, 0.0, 1.0] * 3, "idx": [0, 1, 2], "fac": [0, 0]},
            {"name": "a-neighbour", "color": None,
             "pos": [1.0] * 9, "nrm": [0.0, 1.0, 0.0] * 3, "idx": [0, 1, 2], "fac": [0, 0]},
        ], str(host))
        surface = {"name": "some-piece", "color": [0.9, 0.0, 0.0],
                   "pos": [7.0] * 18, "nrm": [1.0, 0.0, 0.0] * 6,
                   "idx": [0, 1, 2, 3, 4, 5], "fac": [0, 1]}
        check("a graft lands on the piece the host names", graft(host, {"some-piece": surface}), 1)
        back = read_payload(host)
        check("the host keeps its own name and colour",
              [(m["name"], m["color"]) for m in back],
              [("some_piece", [0.5, 0.5, 0.5]), ("a-neighbour", None)])
        check("and takes the fluted surface", back[0]["pos"], [7.0] * 18)
        check("a body the graft does not name is left alone", back[1]["pos"], [1.0] * 9)
        check("a payload naming none of them is not rewritten",
              graft(host, {"nothing-here": surface}), 0)
        # A second graft of the same surface must leave the file alone, or every run re-dates a
        # payload nothing moved and every reader keyed to its mtime reads a change.
        was = host.stat().st_mtime_ns
        graft(host, {"some-piece": surface})
        check("a graft that changes nothing leaves the mtime alone", host.stat().st_mtime_ns, was)

        # AND THE SAME SUBSTITUTION IN A SCENE MESH. cadquery gives a piece one body per BREP
        # face; the graft has to take every one of them and leave the bodies around it standing,
        # at the place and in the frame the scene put them.
        glb = Path(d) / "scene.glb"
        patch = trimesh.creation.box(extents=(4, 4, 4))
        neighbour = trimesh.creation.box(extents=(2, 2, 2))
        neighbour.apply_translation([20, 0, 0])
        built = trimesh.Scene()
        built.add_geometry(patch, node_name="a-piece", geom_name="a-piece")
        built.add_geometry(patch.copy(), node_name="a-piece_1", geom_name="a-piece_1")
        built.add_geometry(neighbour, node_name="bystander", geom_name="bystander")
        built.export(str(glb))
        replacement = trimesh.creation.box(extents=(4, 4, 4))
        piece = {"pos": replacement.vertices.ravel().tolist(),
                 "nrm": replacement.vertex_normals.ravel().tolist(),
                 "idx": replacement.faces.ravel().tolist(), "fac": [0, 11]}
        check("a scene graft takes every patch of the piece", graft_glb(glb, {"a-piece": piece}), 1)
        got = trimesh.load(str(glb))
        check("the piece is one body and the bystander stands",
              sorted(got.geometry), ["a-piece", "bystander"])

        # AND IT REFUSES A SURFACE THAT WOULD LAND SOMEWHERE ELSE. A body drawn in the wrong
        # place is worse than one drawn smooth, and nothing downstream would catch it.
        built.export(str(glb))
        adrift = replacement.copy()
        adrift.apply_translation([50, 0, 0])
        moved = {"pos": adrift.vertices.ravel().tolist(),
                 "nrm": adrift.vertex_normals.ravel().tolist(),
                 "idx": adrift.faces.ravel().tolist(), "fac": [0, 11]}
        try:
            graft_glb(glb, {"a-piece": moved})
            check("a surface that lands elsewhere is refused", "accepted", "refused")
        except ValueError:
            check("a surface that lands elsewhere is refused", "refused", "refused")

    # THE CONTROL THAT SEES WHAT THIS FILE IS FOR: the groove has to survive the collapse. A
    # decimation that flattened the flutes passes every check above — the payload decodes, the
    # regions tile, the box is still a box — and draws the smooth prism the STEP already drew.
    # A ridged slab stands in for the show face: 1.2 mm deep on 5 mm centres, the enclosure's own
    # figures (`printed-parts/cadlib/reeding.py`, `enclosure.py:240`).
    #
    # AND IT IS CLOSED, because a piece is. A collapse pulls an open mesh's border inward and
    # the deviation that produces is the border's, not the field's — on the same field as a
    # sheet it floors at 0.36 mm and no rung of the ladder is ever taken.
    ridged = _ridged_slab()

    def depth(m):
        """Peak-to-valley of the ridged field, off the surface rather than off its vertices.

        Only the interior of the show face: the slab's back and its four walls run the whole
        thickness and would report that instead of the groove."""
        lo, hi = m.bounds
        pts, _ = trimesh.sample.sample_surface(m, 400000)
        inset = 0.05 * (hi - lo)
        show = pts[(pts[:, 0] > lo[0] + inset[0]) & (pts[:, 0] < hi[0] - inset[0])
                   & (pts[:, 2] > lo[2] + inset[2]) & (pts[:, 2] < hi[2] - inset[2])
                   & (pts[:, 1] > hi[1] - 0.5 * (hi[1] - lo[1]))]
        return float(np.percentile(show[:, 1], 99.5) - np.percentile(show[:, 1], 0.5))

    # AT THE BUDGET A SHOW FACE IS HELD TO. `deflection` is a ratio of the mean of three extents,
    # and the bar's third extent is the groove itself — a sheet's own mean is a fraction of the
    # piece it stands on, and would hold it to a fraction of the distance. The two the face spans
    # are what set it, through the same function.
    span = np.sort(ridged.bounding_box.extents)
    budget = deflection(trimesh.creation.box(extents=span[[1, 2, 2]]))
    before = depth(ridged)
    kept, dev = simplify_within(ridged, budget)
    after = depth(kept)
    check("the slab is closed, the way a piece is", ridged.is_watertight, True)
    check("the ridged bar is cut deep", round(before, 1), 1.2)
    check("the collapse takes most of the triangles away", len(kept.faces) < len(ridged.faces) / 2,
          True)
    check("and the groove is still there afterwards", round(after, 1), round(before, 1))
    check("inside the budget it was accepted on", dev <= budget, True)

    bad = [c for c in checks if not c[0]]
    print(f"\n{len(checks) - len(bad)}/{len(checks)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:2] == ["selftest"] else main())
