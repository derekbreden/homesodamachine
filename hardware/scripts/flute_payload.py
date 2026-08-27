"""The machine's flutes, in the triangles every picture is drawn from.

`printed-parts/cadlib/flute_skin.py` cuts the show surfaces into the MESH and says why they are
not in the solid. The STEP beside that mesh is a smooth prism — 343 faces on the front-top piece,
every one a plane or a cylinder — so a reader who is handed the solid is handed a box with no
texture on it. The box's six pieces, the cold core's shell and two caps, and the faucet's base
are all cut that way and all read the same here: a piece is any `.step` under `PIECES_DIRS` with
an `.stl` of the same stem, so another one is carried with no edit to this file.

THE VIEWER PREFERS A PAYLOAD TO THE STEP BESIDE IT. `loadStepFile` fetches `<file>.step.mesh`
first and only parses the solid when there is none (`web/public/js/viewer/step.js`), and every
picture this repository draws goes through that one mount: `/3d` in a browser,
`tools/render/render-step-posed.js` driving the same page headless for the assembly cards,
So the flutes reach all of them by standing in the payload,
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

    tools/cad-venv/bin/python hardware/scripts/flute_payload_enclosure.py
    tools/cad-venv/bin/python hardware/scripts/flute_payload_cold_core.py
    tools/cad-venv/bin/python hardware/scripts/flute_payload_faucet.py
    tools/cad-venv/bin/python hardware/scripts/flute_payload.py            # every tree
    tools/cad-venv/bin/python hardware/scripts/flute_payload.py selftest
"""

import itertools
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

#: Every directory whose solids stand beside a printed mesh the solid does not describe, in the
#: three trees they fall into. The box's six pieces are one tree; the cold core's shell and its
#: two caps are another; the faucet's base — the one piece that stands in the open on a kitchen
#: counter — is the third. All three are fluted on the same field off the same
#: `cadlib/flute_skin.py` (`cold-core/_show_skin.py`, `faucet_shell.write_bed_file`).
#:
#: NOTHING PASSES BETWEEN THEM. A run over one tree opens that tree's directories and writes
#: the payloads standing in them, and reads nothing of the others — which is what lets the build
#: flute them as three rules, `flute_payload_enclosure.py`, `flute_payload_cold_core.py` and
#: `flute_payload_faucet.py`.
#:
#: AN ASSEMBLY ASKS FOR THE TREE ITS BODIES CAME OUT OF. `foam_assembly` and `cold_core_assembly`
#: hold the core and nothing else, so they ask for `COLD_CORE_DIRS`; `enclosure_assembly` holds
#: the machine and takes the default, because "which surfaces on this disk are fluted" is one
#: question and a scene spanning several trees knows no better answer.
ENCLOSURE_DIRS = (
    _ROOT / "hardware/printed-parts/enclosure/enclosure",
)
COLD_CORE_DIRS = (
    _ROOT / "hardware/printed-parts/cold-core/foam-shell",
    _ROOT / "hardware/printed-parts/cold-core/foam-cap",
)
FAUCET_DIRS = (
    _ROOT / "hardware/printed-parts/faucet/faucet-shell",
)
PIECES_DIRS = ENCLOSURE_DIRS + COLD_CORE_DIRS + FAUCET_DIRS

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


def pieces(directories=PIECES_DIRS):
    """Every solid in `directories` that has a printed mesh beside it, as (step, stl) pairs.

    THE MESH BESIDE THE SOLID IS WHAT DECLARES A PIECE FLUTED. Nothing here holds a list of
    which parts carry a show skin: a generator that cuts one writes an `.stl` next to its
    `.step`, and that pair is the whole of the claim."""
    out = []
    for directory in directories:
        for step in sorted(directory.glob("*.step")):
            stl = step.with_suffix(".stl")
            if stl.is_file():
                out.append((step, stl))
    return out


def surfaces(directories=PIECES_DIRS):
    """The fluted surfaces standing on this disk, keyed by the name a payload holds them under.

    What `graft` is handed. A tree that has not cut them yet answers with nothing, and a graft
    of nothing leaves every payload as it stands — which is the smooth solid, and is what a
    machine with no printed mesh could draw anyway."""
    out = {}
    for step, _stl in pieces(directories):
        held = read_payload(step.with_name(step.name + ".mesh"))
        if held and len(held) == 1:
            out[held[0]["name"]] = held[0]
    return out


#: How far a grafted surface may stand from the bodies it replaces. A piece is cut where the
#: assembly stands it, so the two agree to a tessellation's deflection and nothing more; a
#: reading past this is a body landing somewhere its own solid does not.
PLACEMENT_TOL = 0.5


def glb_members(scene, fluted):
    """Every geometry key in `scene`, grouped by the fluted piece it is a patch of.

    TWO ORDINALS, TWO MEANINGS, and telling them apart is the whole of this. cadquery writes one
    mesh per BREP face, so a piece arrives as `<index>`, `<index>_1`, `<index>_2` … — an ordinal
    after an UNDERSCORE is one face of a single body and all of them are the same piece. An
    ordinal after a SLASH is a body of its own (`fluted_key`), and those never join."""
    out = {}
    for k in scene.geometry:
        key = fluted_key(re.sub(r"_\d+$", "", k), fluted)
        if key:
            out.setdefault(key, []).append(k)
    return {k: sorted(v) for k, v in out.items()}


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
    grouped = glb_members(scene, fluted)
    landed = 0
    for name, surface in fluted.items():
        members = grouped.get(name)
        if not members:
            continue
        # THE SCENE KEEPS ITS OWN NAME FOR THE BODY. A piece is `enclosure-front-top` in the
        # machine's own frame and `cold-core/foam-shell` under the subassembly that places it;
        # which surface it gets is this file's question, what it is called is the scene's.
        body = re.sub(r"_\d+$", "", members[0])
        node = scene.graph.geometry_nodes[members[0]][0]
        transform = scene.graph.get(frame_to=node)[0]
        material = getattr(scene.geometry[members[0]].visual, "material", None)
        low = np.min([scene.geometry[k].bounds[0] for k in members], axis=0)
        high = np.max([scene.geometry[k].bounds[1] for k in members], axis=0)
        # THE SAME CARRY THE PAYLOAD SIDE MAKES, and it has to be taken while the bodies it is
        # measured against are still here. A piece cut in its own frame — the cold core's three —
        # stands a subassembly's placement away from the patches it replaces, and the scene is
        # where that has to be put right, because a `.glb` has no STEP behind it to fall back to
        # (`placement_onto`).
        own = np.asarray(surface["pos"], dtype=np.float64).reshape(-1, 3)
        if max(float(np.abs(own.min(0) - low).max()),
               float(np.abs(own.max(0) - high).max())) > PLACEMENT_TOL:
            placement = placement_onto(
                trimesh.util.concatenate([scene.geometry[k] for k in members]), surface)
            if placement is not None:
                surface = carried(surface, placement)
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
        scene.add_geometry(mesh, node_name=body, geom_name=body, transform=transform)
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
    # THIS PAYLOAD CARRIES MORE SURFACE THAN THE SOLID AND IT STILL STANDS FOR IT. The flutes
    # are in the mesh and not in the STEP, so the two are not the same surface — but the mesh
    # is cut FROM this solid's print and is answerable to these bytes, and `_payload_current`
    # asks exactly that. Written without `src` it would read as a payload of unknown descent,
    # and the plain tessellation in `_cadq_export` would replace it — serving a smooth box.
    _mesh_payload.write([mesh], str(out), src=_mesh_payload.source_digest(step))
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
    if head.get("v") not in _mesh_payload.DECODABLE:
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
    if head.get("v") not in _mesh_payload.DECODABLE:
        return []
    return [m["name"] for m in head["meshes"]]


def piece_names(directories=PIECES_DIRS):
    """The names the fluted pieces standing on this disk are held under.

    What a caller asks when it needs to know whether a payload holds a surface its solid does
    not — cheaper than `surfaces`, which decodes the triangles as well."""
    out = set()
    for step, _stl in pieces(directories):
        out.update(payload_names(step.with_name(step.name + ".mesh")))
    return out


def fluted_key(name, fluted):
    """Which fluted surface `name` names, or None — the one place a body's name is matched.

    A SOLID INDEX IS A PATH AND A PIECE'S OWN NAME IS THE END OF IT. The box places its six in
    the machine's own frame and under their own names (`enclosure-front-top`); the machine
    places the cold core's three under the core's (`cold-core/foam-shell`), because the core is
    a subassembly that carries a name. They are the same pieces either way, so both spellings
    have to reach the same surface — and matching the whole string only ever found the first.

    A TRAILING ORDINAL IS NOT A NAME AND STOPS THE MATCH DEAD. `cold-core/evap-coil/2` is the
    second solid OF one body, and a fluted surface is the whole of a piece; landing a whole
    piece on one of its solids would be a worse answer than landing nothing. So only a name
    that ends ON the piece matches.

    AND AN ASSEMBLY MAY LEAVE THE FAMILY OFF. Inside `faucet-shell.step` the two pieces are
    `shell_base` and `shell_tip`, because the assembly is already called the faucet shell and
    saying it twice reads as a stutter; the printed piece is `faucet-shell-base`, because a
    file has no assembly around it to be named inside. Same body, and the surface has to
    reach it under either spelling. THE TAIL HAS TO LAND ON A HYPHEN AND CARRY ONE: `cap-top`
    is `foam-cap-top` and never `foam-cap-lid-top`, `top` alone is a role rather than a piece
    and names nothing, and a tail that fits two pieces fits neither — a whole piece landed on
    the wrong body is worse than nothing landing at all."""
    name = name.replace("_", "-")
    if name in fluted:
        return name
    owner, _sep, own = name.rpartition("/")
    if owner and own in fluted:
        return own
    if "-" not in own:
        return None
    tails = [k for k in fluted if k.endswith("-" + own)]
    return tails[0] if len(tails) == 1 else None


def _axis_rotations():
    """The 24 rotations that carry the axes onto the axes — every signed permutation of them
    whose determinant is +1.

    THAT IS THE WHOLE SET A PLACEMENT IN THIS TREE EVER USES. A subassembly is stood on the
    machine's floor at a quarter turn (`enclosure_assembly.build_foam`) and a scene poses a
    piece to look at the face it wants, which can turn it over. Both land on an axis; neither
    lands between two. A determinant of −1 is a mirror and no placement is one, so those are
    left out rather than tried and rejected — a mirrored piece that fitted would be a piece
    drawn inside out."""
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1.0, -1.0), repeat=3):
            m = np.zeros((3, 3))
            for row, col in enumerate(perm):
                m[row, col] = signs[row]
            if round(float(np.linalg.det(m))) == 1:
                out.append(m)
    return out


_AXIS_ROTATIONS = _axis_rotations()


def placement_onto(entry, surface, tol=PLACEMENT_TOL):
    """The rigid transform carrying `surface` onto the body `entry` holds — `(R, t)` — or None.

    A SUBASSEMBLY'S PLACEMENT IS A QUARTER TURN AND A SHIFT. The box's six pieces are cut in the
    machine's own frame and need none; the cold core's three are cut in the core's, and the
    machine stands that frame yawed and lifted (`enclosure_assembly.build_foam`), so their
    surfaces have to be carried before they can stand in for a body.

    THE TURN IS RECOVERED, NOT PLUMBED, because the payload already holds both ends of it: the
    body as the machine places it, and the piece as it was cut. Boxes say which axes swapped, and
    that is as far as boxes go — a part symmetric about its own mid-planes has the same box under
    several turns. WHAT SEPARATES THEM IS THE PIECE ITSELF: the shell's ports are on one face and
    its cavity is not centred, so only one turn lays its surface ON the body. That is measured,
    point to surface, on the same reading `deviation` takes.

    A piece that matches none of them is not this body, and gets nothing rather than a guess."""
    body = entry if isinstance(entry, trimesh.Trimesh) else trimesh.Trimesh(
        np.asarray(entry["pos"], dtype=np.float64).reshape(-1, 3),
        np.asarray(entry["idx"], dtype=np.int64).reshape(-1, 3), process=False)
    a = np.asarray(body.vertices, dtype=np.float64)
    b = np.asarray(surface["pos"], dtype=np.float64).reshape(-1, 3)
    rng = np.random.default_rng(0)
    probe = b[rng.choice(len(b), min(1500, len(b)), replace=False)]
    best = None
    for R in _AXIS_ROTATIONS:
        turned = b @ R.T
        # The shift is what puts the two boxes on each other; if it cannot, this turn is wrong
        # before any surface is measured.
        t = ((a.min(0) + a.max(0)) - (turned.min(0) + turned.max(0))) / 2.0
        if np.abs((turned.min(0) + t) - a.min(0)).max() > tol:
            continue
        # A HIGH PERCENTILE AND NOT THE MAX. The body being matched against is whatever
        # tessellation that payload holds — a scene cuts its own, coarser than the piece's — so a
        # handful of probe points land in a gap between its triangles and read far from a surface
        # they are actually on. The max is that straggler; the 99th is the fit. It still
        # separates the answer from every other turn by tens of millimetres.
        dev = float(np.percentile(
            trimesh.proximity.closest_point(body, probe @ R.T + t)[1], 99))
        if best is None or dev < best[0]:
            best = (dev, R, t)
    if best is None:
        return None
    # A GROOVE IS THE ONLY THING THAT MAY STAND OFF THE SMOOTH BODY, so the reading a correct
    # turn gives is a flute deep and no more. A wrong turn on this footprint is tens of mm out.
    dev, R, t = best
    return (R, t) if dev <= _FLUTE_STANDOFF else None


#: How far the fluted surface may stand from the smooth body it replaces and still BE it: the
#: groove's own depth with room for the tessellation either side. The box's flutes and the core's
#: are cut to the same 1.2 mm (`cadlib/reeding.py`, `_cold_core_interface.flute_depth`).
_FLUTE_STANDOFF = 2.0


def carried(surface, placement):
    """`surface` with its positions and normals carried by `placement` — a new dict, since the
    same cut surface stands in several payloads at several placements."""
    R, t = placement
    pos = np.asarray(surface["pos"], dtype=np.float64).reshape(-1, 3) @ R.T + t
    nrm = np.asarray(surface["nrm"], dtype=np.float64).reshape(-1, 3) @ R.T
    return {**surface, "pos": pos.ravel().tolist(), "nrm": nrm.ravel().tolist()}


def _placement_drift(entry, surface):
    """How far a fluted surface stands from the body it would replace, in mm.

    Bounding box to bounding box, which is the same reading `graft_glb` takes: the two are the
    same solid to within a groove's depth, so a box that has moved is a placement and not a
    shape."""
    a = np.asarray(entry["pos"], dtype=np.float64).reshape(-1, 3)
    b = np.asarray(surface["pos"], dtype=np.float64).reshape(-1, 3)
    return float(max(np.abs(a.min(0) - b.min(0)).max(), np.abs(a.max(0) - b.max(0)).max()))


def graft(path: Path, fluted: dict):
    """Put the fluted surfaces into the payload at `path`, in place. Returns how many landed.

    A PIECE IS THE SAME BODY WHEREVER IT IS PLACED. `enclosure.py` cuts the printed mesh off the
    piece as the assembly stands it, so the triangles here are already in the coordinates every
    payload that holds that piece places it at — the assembled box, the whole appliance, and each
    bench scene agree with the piece's own solid to within a tessellation's deflection.

    THE HOST KEEPS ITS OWN NAME AND COLOUR. A body is coloured by the assembly that places it,
    and swapping the surface is not swapping which part it is.

    AND IT KEEPS ITS OWN DESCENT. `src` says which STEP's bytes this payload answers to
    (`_mesh_payload.write`), and grafting a surface into it does not change that — the host
    was cut from the solid it still sits beside. Recomputing it here would also ask for a
    STEP that need not be on this disk: what is grafted into is a payload, and the graft is
    the same operation whether or not its solid was carried along with it."""
    src = _mesh_payload.read_source(path) if path.is_file() else None
    if src is None:
        # A host written before `src` existed states none. Its solid is what it was cut from,
        # so read it off the bytes beside it — and where there is no solid beside it, the
        # payload simply keeps stating none rather than claiming a descent nobody can check.
        solid = path.with_name(path.name[: -len(".mesh")])
        if solid.is_file():
            src = _mesh_payload.source_digest(solid)
    held = read_payload(path)
    if held is None:
        return 0
    skipped = []
    landed = 0
    for entry in held:
        surface = fluted.get(fluted_key(entry["name"], fluted) or "")
        if surface is None:
            continue
        # AND IT HAS TO LAND WHERE THE BODY IT REPLACES STANDS. `graft_glb` has always asked
        # this and this side never did, because every piece it had was authored in the frame it
        # is placed in — the box's six are cut in the machine's own coordinates. A piece that is
        # NOT, like the cold core's three, arrives in its own frame and drops in a subassembly's
        # placement away from itself: still a correct surface, drawn somewhere its solid is not.
        # Silence is the wrong answer to that, so it is measured here on the same figure.
        drift = _placement_drift(entry, surface)
        if drift > PLACEMENT_TOL:
            placement = placement_onto(entry, surface)
            if placement is None:
                skipped.append((entry["name"], drift))
                continue
            surface = carried(surface, placement)
        entry.update({k: surface[k] for k in ("pos", "nrm", "idx", "fac")})
        landed += 1
    for name, drift in skipped:
        print(f"   {Path(path).name}: {name} keeps its own surface — the fluted one stands "
              f"{drift:.1f} mm off the body it would replace, past {PLACEMENT_TOL} mm")
    if not landed:
        return 0
    # BYTES THAT DID NOT MOVE DO NOT MOVE THE FILE. A payload rewritten identically takes a new
    # mtime, and every reader that keyed off it — the ETag the page revalidates against, the
    # `_current` comparison `_cadq_export` skips a re-tessellation on — reads a change that did
    # not happen. `render_scenes.write_payload` holds the same property for the payload it cuts.
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    _mesh_payload.write(held, str(tmp), src=src)
    if path.is_file() and path.read_bytes() == tmp.read_bytes():
        tmp.unlink()
    else:
        tmp.replace(path)
    return landed


def main(directories=PIECES_DIRS):
    found = pieces(directories)
    if not found:
        raise SystemExit("no printed meshes beside the solids in "
                         + ", ".join(str(d) for d in directories))
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
    # looking for them, and this reads only the directories it was handed.
    cut_here = {step.name + ".mesh" for step, _ in found}
    for directory in directories:
        for path in sorted(directory.glob("*.step.mesh")):
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
        #
        # THE BODY AND THE SURFACE THAT REPLACES IT STAND IN ONE PLACE. A graft changes how
        # finely a piece is drawn, never where it is, so the two agree to within a groove and
        # `_placement_drift` reads nothing. A fixture whose surface stood somewhere else would
        # be exercising the carry below instead of the substitution this asks about.
        host = Path(d) / "host.step.mesh"
        smooth = [0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 10.0, 0.0]
        flutes = smooth + [10.0, 0.0, 0.0, 10.0, 10.0, 0.0, 0.0, 10.0, 0.0]
        _mesh_payload.write([
            {"name": "some_piece", "color": [0.5, 0.5, 0.5],
             "pos": smooth, "nrm": [0.0, 0.0, 1.0] * 3, "idx": [0, 1, 2], "fac": [0, 0]},
            {"name": "a-neighbour", "color": None,
             "pos": [1.0] * 9, "nrm": [0.0, 1.0, 0.0] * 3, "idx": [0, 1, 2], "fac": [0, 0]},
        ], str(host))
        surface = {"name": "some-piece", "color": [0.9, 0.0, 0.0],
                   "pos": flutes, "nrm": [0.0, 0.0, 1.0] * 6,
                   "idx": [0, 1, 2, 3, 4, 5], "fac": [0, 1]}
        check("a graft lands on the piece the host names", graft(host, {"some-piece": surface}), 1)
        back = read_payload(host)
        check("the host keeps its own name and colour",
              [(m["name"], m["color"]) for m in back],
              [("some_piece", [0.5, 0.5, 0.5]), ("a-neighbour", None)])
        check("and takes the fluted surface", back[0]["pos"], flutes)
        check("a body the graft does not name is left alone", back[1]["pos"], [1.0] * 9)
        check("a payload naming none of them is not rewritten",
              graft(host, {"nothing-here": surface}), 0)
        # A second graft of the same surface must leave the file alone, or every run re-dates a
        # payload nothing moved and every reader keyed to its mtime reads a change.
        was = host.stat().st_mtime_ns
        graft(host, {"some-piece": surface})
        check("a graft that changes nothing leaves the mtime alone", host.stat().st_mtime_ns, was)

        # AND A PIECE CUT IN ITS OWN FRAME IS CARRIED ONTO THE BODY IT REPLACES. The box's six
        # are cut in the machine's own coordinates and drop straight in; the cold core's three
        # are cut in the core's, and the machine stands that frame yawed and lifted, so their
        # surfaces arrive a subassembly's placement away from the body they answer to. Dropping
        # them where they arrive is a piece drawn correctly and in the wrong place.
        #
        # A WEDGE AND NOT A BOX. Boxes narrow the turn to four and no further — a box is its own
        # mirror about each of its mid-planes — so what picks the answer is the piece's own
        # asymmetry, here the corner three unequal edges meet at.
        wedge = trimesh.Trimesh([[0, 0, 0], [30, 0, 0], [0, 20, 0], [0, 0, 10]],
                                [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]],
                                process=False).subdivide().subdivide().subdivide()
        yaw = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        placed = wedge.vertices @ yaw.T + np.array([319.5, 0.0, 20.0])
        own_frame = {"name": "a-wedge", "color": None,
                     "pos": wedge.vertices.ravel().tolist(),
                     "nrm": wedge.vertex_normals.ravel().tolist(),
                     "idx": wedge.faces.ravel().tolist(), "fac": [0, len(wedge.faces) - 1]}
        stood = Path(d) / "stood.step.mesh"
        _mesh_payload.write([{**own_frame, "name": "core/a-wedge",
                              "pos": placed.ravel().tolist()}], str(stood))
        check("a piece cut in its own frame is carried onto the body",
              graft(stood, {"a-wedge": own_frame}), 1)
        carried_pos = np.asarray(read_payload(stood)[0]["pos"]).reshape(-1, 3)
        check("and lands where the body it replaces stood",
              round(float(np.abs(carried_pos - placed).max()), 3), 0.0)

        # AND A SURFACE THAT IS NOT THAT BODY GETS NOTHING RATHER THAN A GUESS. The wedge's own
        # bounding box passes the gate boxes give and no turn lays it on the wedge, so every one
        # is refused and the piece keeps the smooth surface it had.
        crate = wedge.bounding_box.subdivide().subdivide()
        check("a surface that is not the body is not placed at all",
              placement_onto(own_frame, {"pos": crate.vertices.ravel().tolist()}), None)

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

        # AND A SURFACE THAT ARRIVES IN THE PIECE'S OWN FRAME IS CARRIED HERE TOO. The reading
        # is taken against the bodies it replaces, so it has to be taken while those bodies are
        # still in the scene — a `.glb` has no STEP behind it to fall back to.
        built.export(str(glb))
        adrift = replacement.copy()
        adrift.apply_translation([50, 0, 0])
        moved = {"pos": adrift.vertices.ravel().tolist(),
                 "nrm": adrift.vertex_normals.ravel().tolist(),
                 "idx": adrift.faces.ravel().tolist(), "fac": [0, 11]}
        check("a scene carries a surface onto the bodies it replaces",
              graft_glb(glb, {"a-piece": moved}), 1)
        check("and the piece stands where it stood",
              bool(np.abs(trimesh.load(str(glb)).geometry["a-piece"].bounds
                          - replacement.bounds).max() < PLACEMENT_TOL), True)

        # AND IT REFUSES ONE IT CANNOT LAY ON THEM AT ALL. A surface no turn carries onto the
        # bodies it would replace is a different solid, and dropping it in where it arrived
        # draws the piece somewhere its own solid is not — worse than drawing it smooth, and
        # nothing downstream would catch it.
        built.export(str(glb))
        stranger = trimesh.creation.box(extents=(4, 4, 12))
        stranger.apply_translation([50, 0, 0])
        elsewhere = {"pos": stranger.vertices.ravel().tolist(),
                     "nrm": stranger.vertex_normals.ravel().tolist(),
                     "idx": stranger.faces.ravel().tolist(), "fac": [0, 11]}
        try:
            graft_glb(glb, {"a-piece": elsewhere})
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

    # THE SPELLINGS A BODY'S NAME COMES IN, all of them reaching the one surface — and the three
    # that must reach nothing. `shell_base` inside `faucet-shell.step` and `faucet-shell-base.step`
    # on its own are the same piece; `top` is a role; a tail two pieces answer to is a piece
    # about to land on the wrong body.
    family = {"faucet-shell-base": 0, "foam-cap-top": 0, "foam-cap-lid-top": 0,
              "enclosure-back-top": 0, "cold-core-back-top": 0}
    check("a piece under its own name", fluted_key("faucet-shell-base", family),
          "faucet-shell-base")
    check("a piece under a subassembly's path", fluted_key("core/foam-cap-top", family),
          "foam-cap-top")
    check("a piece an assembly left the family off", fluted_key("shell_base", family),
          "faucet-shell-base")
    check("a tail lands on a hyphen and takes the piece it ends",
          fluted_key("cap-top", family), "foam-cap-top")
    check("and the longer piece keeps its own tail",
          fluted_key("lid-top", family), "foam-cap-lid-top")
    check("a tail two pieces answer to reaches neither",
          fluted_key("back-top", family), None)
    check("a one-word tail is a role and not a piece", fluted_key("top", family), None)
    check("a trailing ordinal is one solid OF a body and stops the match",
          fluted_key("faucet-shell-base/2", family), None)

    bad = [c for c in checks if not c[0]]
    print(f"\n{len(checks) - len(bad)}/{len(checks)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:2] == ["selftest"] else main())
