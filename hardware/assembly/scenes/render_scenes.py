"""Draw the assembly cards' pictures — every scene and every part shot in `_scenes`.

    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py             # all
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top    # one scene
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py en08-asse-drip-pan # one part
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py --force     # anyway

A PART SHOT COSTS NO APPLIANCE — its subject is a STEP — so a run asked for nothing but part
shots stands no machine at all.

THE MACHINE IS BUILT ONCE for however many scenes are asked for: a scene is a subset of that one
assembly, so the cost of four pictures is the cost of one build plus four cuts. What lands in the
tree is the PNG and a fingerprint beside it; the scene STEPs go to `out/`, which `.gitignore`
holds, because they are a rendering intermediate and a 20 MB artifact that churns on every move
of any body is exactly what this must not add to a commit.

AND THE BROWSER IS STOOD ONCE, for however many pictures the run has to draw. Every cut queues
its picture into one `Batch`, and the whole list goes to `render-step-posed.js --jobs` at the
end — one server, one Chromium, one page re-pointed at each subject in turn. See `Batch`.

`//:render-scene-cards` draws the pictures. The enclosure-assembly producer cuts the viewer
meshes from the named machine it already built, through `write_glbs`, so publication neither
rebuilds that machine nor starts Chromium.
"""

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
for _p in (_HERE.parent, _HW / "scripts", _HW / "manifold-layout",
           _HW / "cold-core-layout", _HW / "printed-parts" / "cold-core",
           _ROOT / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _mesh_payload                                    # noqa: E402
import _scenes                                          # noqa: E402
import _cold_core_style                                 # noqa: E402
import flute_payload                                    # noqa: E402
from docgen import note_rewritten                       # noqa: E402
from _cadq_export import note_read, note_write, _per_solid_color   # noqa: E402

OUT_DIR = _HERE.parent / "out"
IMG_DIR = _HW / "assembly" / "cards" / "img"
GLB_DIR = _HERE.parent / "glb"
ASSEMBLY_MESH = _HW / "manifold-layout" / "enclosure-assembly.step.mesh"
CORE_MESH = _HW / "cold-core-layout" / "cold-core-assembly.step.mesh"
CORE_SCORECARD = _HW / "cold-core-layout" / "cold-core-assembly.scorecard.json"
GLB_TOL = 0.5
RENDERER = _ROOT / "tools" / "render" / "render-step-posed.js"
SIZE = "1600x1200"
# A part shot is drawn on the scenes' own canvas and then TRIMMED to its subject, so this is
# what the render has to work with rather than what the card receives: the picture that comes
# out is the subject's own projection, and the card scales it into a panel.
PART_SIZE = SIZE


# The nine scenes a card knows as `scene-<id>.png` keep that name; the two named for the card
# whose picture they are take the card's own file name, the way a part shot does.
_SCENE_PNG = {"en04-stratum": "en04-stratum.png", "en06-column": "en06-column.png"}


def png_for(scene) -> Path:
    return IMG_DIR / _SCENE_PNG.get(scene.id, f"scene-{scene.id}.png")


def cut(assembly, scene):
    """The scene as its own assembly, and the point the camera looks at.

    Every named body, world-placed and keeping its own colour, so the picture is the model's own
    geometry and not a redraw. A name `inner` claims is one of the core's bodies and the rest are
    the machine's, and both come off the same assembly. The look-at point is what is drawn OF the
    unit — the roots, or the core's own bodies where a scene draws those instead.
    See `_scenes.SCENES`."""
    import enclosure_assembly as ea
    placed = ea._solids(assembly)
    inner = set(_scenes.inner_of(scene))
    # THE MACHINE STANDS THESE ITSELF. `ea._solids` reads the pack, where the core is one
    # envelope; `ea._core_solids` is the other half of the same children — the core's bodies
    # already placed, so nothing here stands the stack a second time or repeats its transform.
    core = ea._core_solids(assembly) if inner else {}
    names = _scenes.members(scene, assembly)
    # ONE LENGTH OF TUBE, ONE COLOUR. Each model paints its own half — the core tells its eight
    # lines apart, the machine paints fluid — and a picture carrying both would break colour at
    # the conduit, where there is no joint. Where both halves are drawn the machine's is what
    # both take; a line that crosses nothing keeps the colour its own model gives it.
    joined = {line: placed[half][1]
              for line, half in _scenes.crossings(assembly.runs).items()
              if line in names and half in names}
    out = cq.Assembly(name=scene.id)
    drawn_roots = []
    for name in names:
        solid, colour = core[name] if name in inner else placed[name]
        out.add(solid, name=name, color=joined.get(name, colour))
        if name in inner or (not inner and name in scene.roots):
            drawn_roots.append(solid)
    # THE POSE THE UNIT IS WORKED IN. A piece open at its ceiling is turned over on the bench,
    # so the scene is turned with it and the camera stays a camera.
    if scene.flip:
        axis, deg = scene.flip
        turn = cq.Location(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
        turned = cq.Assembly(name=scene.id)
        for child in out.children:
            turned.add(child.obj, name=child.name, color=child.color, loc=turn * child.loc)
        out = turned
        drawn_roots = [r.moved(turn) for r in drawn_roots]

    lo = [1e9] * 3
    hi = [-1e9] * 3
    for solid in drawn_roots:
        b = solid.BoundingBox()
        for i, (a, z) in enumerate(((b.xmin, b.xmax), (b.ymin, b.ymax), (b.zmin, b.zmax))):
            lo[i], hi[i] = min(lo[i], a), max(hi[i], z)
    mid = [(lo[i] + hi[i]) / 2.0 for i in range(3)]
    if scene.look == "crown":
        mid[2] = hi[2]
    return out, tuple(mid)


# --- what the picture is drawn FROM ----------------------------------------
#
# `loadStepFile` reads `/meshes/<file>.mesh`, and parses `/steps/<file>` where there is no
# payload of the version it decodes — `web/public/js/viewer/step.js`. A scene is drawn from the
# payload `draw` writes beside its STEP; a part shot is drawn from the B-rep, through a link
# that has no payload beside it. Each sidecar's `geometry` is the digest of that file.


def write_payload(step, source) -> Path:
    """Tessellate `source` into `<step>.mesh`.

    `_mesh_payload` is deterministic: one shape, one set of bytes. The digest of this file
    names the shape it was made from. Bytes that match what is already there are dropped, so a
    payload that did not move keeps its mtime and the page keeps its ETag."""
    mesh = Path(str(step) + ".mesh")
    meshes = (_mesh_payload.from_assembly(source) if hasattr(source, "toCompound")
              else _mesh_payload.from_shape(source))
    tmp = mesh.with_name(mesh.name + ".tmp")
    _mesh_payload.write(meshes, str(tmp))
    if mesh.is_file() and mesh.read_bytes() == tmp.read_bytes():
        tmp.unlink()
    else:
        os.replace(tmp, mesh)
    return mesh


def payload_stands(mesh) -> bool:
    """Whether `mesh` is a payload of the version `web/public/js/viewer/step.js` decodes."""
    try:
        return _mesh_payload.read_version(mesh) == _mesh_payload.VERSION
    except Exception:
        return False


_FLUTED = {}


def fluted_pieces(surfaces=False):
    """The enclosure pieces whose show surface is in the mesh — names, or the surfaces too.

    Read once per run: the names come off six payload headers, the surfaces decode six payloads,
    and every scene and part shot in a run asks the same question."""
    key = "surfaces" if surfaces else "names"
    if key not in _FLUTED:
        _FLUTED[key] = flute_payload.surfaces() if surfaces else flute_payload.piece_names()
    return _FLUTED[key]


def carried_payload(step) -> Path | None:
    """`<step>.mesh` where it holds a surface the solid does not, else None.

    THE ENCLOSURE'S PIECES CARRY THEIR SHOW SURFACES IN THE MESH, not in the B-rep
    (`printed-parts/enclosure/enclosure/flute_skin.py`), so a picture drawn off those bytes is a
    picture of a smooth prism. `hardware/scripts/flute_payload.py` cuts the payload that holds
    the fluted surface, `pack.py`'s `BUNDLED_PAYLOAD_DIRS` bundles it and the lock names it — so
    it is as answerable as the STEP is, and a fresh checkout has both.

    WHICH SOLIDS THOSE ARE IS READ OFF THE PAYLOAD, not listed: any that names one of the pieces
    is one whose picture the B-rep cannot draw, which reaches the piece itself, the box the six
    of them make, and the appliance that places the box."""
    payload = Path(str(step) + ".mesh")
    if not payload.is_file():
        return None
    held = {n.replace("_", "-") for n in flute_payload.payload_names(payload)}
    return payload if held & {n.replace("_", "-") for n in fluted_pieces()} else None


def bare_subject(step, name) -> Path:
    """`step` hard-linked at `OUT_DIR/<name>.step`, carrying a payload only where the solid does
    not hold the surface.

    `_atomic_write` replaces a STEP by rename, so a link stands for the inode it was made from.
    This one is remade on every render, and the digest the sidecar records is taken from `step`.

    WHERE THE B-REP IS THE WHOLE PART IT IS ALSO THE SUBJECT, and the link stands bare: the
    colour occt-import-js reads off a component is in those bytes, and a fresh checkout, a
    sandbox and this tree then hand the page the same triangles. `carried_payload` names the
    pieces that is not true of."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bare = OUT_DIR / f"{name}.step"
    bare_mesh = Path(str(bare) + ".mesh")
    for stray in (bare, bare_mesh):
        if stray.exists():
            stray.unlink()
    try:
        os.link(step, bare)
    except OSError:
        shutil.copyfile(step, bare)
    payload = carried_payload(step)
    if payload is not None:
        try:
            os.link(payload, bare_mesh)
        except OSError:
            shutil.copyfile(payload, bare_mesh)
    return bare


# --- what the run hands the browser ----------------------------------------


class Batch:
    """Every picture a run has decided to draw, and the record each one leaves behind.

    ONE BROWSER FOR THE RUN. `render-step-posed.js` stands a web server, launches Chromium,
    navigates and waits for the page's whole module graph — three.js, the viewer, occt-import-js
    in wasm — before it draws anything, and that is ~1.6 s on this machine against a render of
    ~0.3 s. Called once a picture it was 34 boots for 34 pictures. `--jobs` takes the whole run
    as a JSON array on stdin and re-points ONE page at each subject in turn, so the boot is paid
    once however many pictures come out.

    THE SIDECAR IS WRITTEN AFTER THE PICTURE, because `image` is the fingerprint of the file the
    renderer just wrote. So a record is held here with everything the run already knows and
    finished when the browser hands the picture back — and a run whose renderer fails writes no
    record at all, which is what makes the next run redraw rather than trust a picture that was
    never taken."""

    def __init__(self):
        self.jobs = []
        self.records = []

    def queue(self, step: Path, png: Path, **flags):
        """One picture: `step` (repo-relative to `hardware/`) posed by `flags`, into `png`."""
        job = {"step": step.relative_to(_HW).as_posix(), "out": str(png), **flags}
        self.jobs.append(job)
        print("   " + json.dumps(job, sort_keys=True))

    def record(self, png: Path, held: dict):
        self.records.append((png, held))

    def run(self):
        """Draw everything queued, then write every record.

        A JOB LIST GOES OVER STDIN rather than into a file. The renderer's own path is what the
        tracer sees on node's command line and what the build graph declares as an input; a
        manifest written to disk would be a second one, named nowhere and belonging to nobody."""
        if self.jobs:
            print(f"\ndrawing {len(self.jobs)} picture(s) on one browser…")
            subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=str(_ROOT),
                           input=json.dumps(self.jobs), text=True, check=True)
        for png, held in self.records:
            _scenes.sidecar_path(png).write_text(json.dumps(
                {**held, "image": _scenes.image_fingerprint(png)},
                indent=2, sort_keys=True) + "\n")


def draw(scene, assembly, batch, force=False, images=True, glbs=True) -> Path:
    # THE RENDERER IS READ WHETHER OR NOT THIS RUN STARTS IT. A scene whose geometry and camera
    # both stand skips the browser, and a trace of that run would not see node's command line
    # at all — so the file that draws every picture here would go undeclared, and the action
    # that redraws one would not find it.
    if images:
        note_read(RENDERER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GLB_DIR.mkdir(parents=True, exist_ok=True)
    step = OUT_DIR / f"{scene.id}.step"
    scene_assembly, target = cut(assembly, scene)

    # THE SCENE'S GEOMETRY, ONCE, IN THE FORM occt-import-js READS A COLOUR OFF. The payload the
    # picture is drawn from and the STEP it is fetched under are both this restatement.
    colored = _per_solid_color(scene_assembly)

    # THE STEP IS THE NAME THE PAYLOAD IS FETCHED UNDER. `render-step-posed.js` stats it and the
    # page asks for `<file>.mesh`. `.gitignore:91` holds this directory, and `pack.py:49`,
    # `parts-tree.js`'s `EXCLUDED_DIRS` and `BUILD.bazel` each name it as one they do not carry —
    # so it is written straight, the way the `.glb` below is.
    colored.export(str(step))
    mesh = write_payload(step, colored)
    if not payload_stands(mesh):
        raise RuntimeError(
            f"scene {scene.id!r} has no v{_mesh_payload.VERSION} payload at {mesh}, which is the "
            f"file its picture is drawn from.")

    # AND THE FLUTED PIECES PUT BACK INTO IT. The payload above is a tessellation of the scene's
    # B-rep, and for an enclosure piece that B-rep is a smooth prism — the show surfaces live in
    # the printed mesh (`printed-parts/enclosure/enclosure/flute_skin.py`). A piece is cut where
    # the assembly stands it, so its own surface drops into the scene's coordinates unchanged.
    grafted = flute_payload.graft(mesh, fluted_pieces(surfaces=True))
    if grafted:
        print(f"   ({grafted} fluted piece(s) into {mesh.name})")

    # AND THE VIEWER'S OWN ARTIFACT. A scene's B-rep is 2–10 MB and would churn on every move of
    # any body in it; a mesh at viewer tolerance is a third of that, and /3d reads a `.glb` the
    # same way it reads a board's. Same bargain the PCB carrier already takes: the big drawing
    # stays out of the tree, the thing a browser opens goes in.
    #
    # `GLB_TOL` is what makes it affordable: the whole set comes to 9 MB at this tolerance and
    # three times that at the 0.1 mm default, and the difference is invisible on a body a browser
    # draws 900 px wide.
    # Written straight rather than through `_cadq_export`: that helper's atomic write and
    # thumbnail queue are for a repo artifact a page lists, and it is imported by nearly every
    # generator in the tree — a keyword added there for one mesh moves the hash of every build
    # graph that reads it.
    if glbs:
        glb = GLB_DIR / f"{scene.id}.glb"
        scene_assembly.export(str(glb), tolerance=GLB_TOL, angularTolerance=GLB_TOL)
        # AND THE SAME SUBSTITUTION THE PAYLOAD ABOVE TOOK. This mesh is cut from the B-rep too,
        # and it is what /3d opens a scene AS — there is no STEP behind it to fall back to.
        in_glb = flute_payload.graft_glb(glb, fluted_pieces(surfaces=True))
        if in_glb:
            print(f"   ({in_glb} fluted piece(s) into {glb.name})")
        note_write(glb)

    # Publication needs the viewer GLB but not a photograph of it. Keeping that action on this
    # side of the return removes Chromium and all 68 card outputs from the CAD fast lane.
    if not images:
        return glb

    png = png_for(scene)
    # THE PICTURE IS DRAWN BY NODE, below Python, and the sidecar beside it is not. Both are
    # what this run makes, and this is the one place that holds either name.
    note_write(png)
    # AND BOTH ARE READ BACK, which is what lets the skip below mean anything. A picture and its
    # record are what this run COMPARES against before it decides to draw, so an action that is
    # not handed them cannot skip: `held_record` comes back empty, `png.is_file()` is false, and
    # every picture is redrawn whether or not a millimetre moved. THE PAIR TRAVELS TOGETHER —
    # a picture staged without its record, or a record without its picture, is a guard that
    # misses forever.
    note_rewritten(png)
    note_rewritten(_scenes.sidecar_path(png))

    # WHAT THE PICTURE IS OF IS THIS FILE. The payload holds the exact triangles the page builds
    # the scene out of, and the scene's own tuple is the camera they are drawn with — so two runs
    # agreeing on both hand the browser the same job. A source moving is what makes a scene worth
    # doubting; these two are what answer the doubt, and most edits in this tree move neither.
    geometry = _scenes.digest_of(mesh)
    held = _scenes.held_record(png)
    # WHAT THE SIDECAR WATCHES IS THIS TREE. The flags below are node's and move no file this
    # record hashes; `--force` redraws against a renderer that has moved under a standing scene.
    unchanged = (not force
                 and held.get("geometry") == geometry
                 and held.get("scene") == _scenes.scene_digest(scene)
                 and png.is_file()
                 and held.get("image") == _scenes.image_fingerprint(png))

    if unchanged:
        print(f"   (geometry unchanged — {png.name} stands)")
    else:
        batch.queue(
            step, png,
            cam=list(scene.cam),
            # Three decimals, the way this reached node as a command line — a look-at point is
            # a millimetre station on a body, and the digits past it are the float's, not the
            # machine's.
            target=[float(f"{v:.3f}") for v in target],
            up=list(scene.up),
            zoom=scene.zoom,
            size=SIZE,
            # Trimmed to the subject. A box seen at an angle projects to a parallelogram and
            # leaves a corner of any rectangle empty; the card wants the picture, not the corner.
            trim=True,
            # A unit as a hand meets it: opaque walls, and what is seen of the inside seen
            # through the mouth the unit leaves open. The viewer ghosts an assembly otherwise.
            solid=True,
        )

    # What the picture is OF: the scene's own tuple hashed, the digest of the payload it was
    # drawn from, the picture that came out, and the bodies that went into it — the machine's
    # answer at the moment of the render. Committed beside the PNG, which the payload is not.
    # `image` is filled in when the browser hands the picture back — see `Batch`.
    batch.record(png, {
        "scene": _scenes.scene_digest(scene),
        "geometry": geometry,
        "drawn": sorted(c.name for c in scene_assembly.children),
    })
    return png


def part_png(part) -> Path:
    return IMG_DIR / f"{part.id}.png"


def draw_part(part, batch, force=False) -> Path:
    """One part shot: the STEP the tree already keeps for that part, posed, with the same
    sidecar a scene gets.

    NO MACHINE IS STOOD FOR THIS. The subject is a file, so the picture costs the render and
    the digest of the bytes it drew — which is also what makes a part shot answerable on its
    own: `render_scenes.py en08-asse-drip-pan` needs no appliance."""
    # THE RENDERER IS READ WHETHER OR NOT THIS RUN STARTS IT, and so is the STEP. A part whose
    # geometry and pose both stand skips the browser, and a trace of that run would declare
    # neither the file that draws every picture here nor the file it draws.
    note_read(RENDERER)
    step = _ROOT / part.step
    note_read(step)
    # AND THE SURFACE IT IS DRAWN FROM, WHERE THAT IS NOT THE SOLID. A payload re-cut against a
    # piece whose STEP has not moved is a different picture, so it goes into the digest below;
    # taken off the solid alone, the standing picture answers as current forever.
    payload = carried_payload(step)
    if payload is not None:
        note_read(payload)
    png = part_png(part)
    note_write(png)
    # Read back for the same reason `draw` reads its own: see there.
    note_rewritten(png)
    note_rewritten(_scenes.sidecar_path(png))

    geometry = _scenes.digest_of(step)
    if geometry is not None and payload is not None:
        geometry = f"{geometry}+{_scenes.digest_of(payload)}"
    if geometry is None:
        raise FileNotFoundError(
            f"part shot {part.id!r} draws {part.step}, which is not in the tree. A part shot's "
            f"subject is a STEP some generator cuts; a name here with no file is that "
            f"generator's output moving or being renamed.")
    held = _scenes.held_record(png)
    unchanged = (not force
                 and held.get("geometry") == geometry
                 and held.get("part") == _scenes.part_digest(part)
                 and png.is_file()
                 and held.get("image") == _scenes.image_fingerprint(png))

    if unchanged:
        print(f"   (geometry unchanged — {png.name} stands)")
    else:
        # THE B-REP IS THE SUBJECT. The colour occt-import-js reads off a component is in these
        # bytes, and `.step.mesh` is `.gitignore`d and in no action's `srcs` — so the picture is
        # drawn through a link with no payload beside it, and a fresh checkout, a sandbox and
        # this tree all hand the page the same triangles.
        batch.queue(
            bare_subject(step, f"part-{part.id}"), png,
            cam=list(part.cam),
            up=list(part.up),
            zoom=part.zoom,
            size=PART_SIZE,
            trim=True,
            solid=bool(part.solid),
        )

    batch.record(png, {
        "part": _scenes.part_digest(part),
        "geometry": geometry,
        "drawn": ([part.step] if payload is None
                  else [part.step, str(payload.relative_to(_ROOT))]),
    })
    return png


def main(images=True, glbs=True):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scenes", nargs="*", help="scene or part-shot ids; default every one")
    ap.add_argument("--force", action="store_true",
                    help="redraw even where the geometry and the camera both stand")
    args = ap.parse_args()

    every = [s.id for s in _scenes.SCENES] + ([p.id for p in _scenes.PARTS] if images else [])
    wanted = args.scenes or every
    unknown = [s for s in wanted if s not in _scenes.SCENE_BY_ID and s not in _scenes.PART_BY_ID]
    if unknown:
        ap.error(f"no such picture: {', '.join(unknown)} — have {', '.join(every)}")
    scenes = [_scenes.SCENE_BY_ID[s] for s in wanted if s in _scenes.SCENE_BY_ID]
    parts = ([_scenes.PART_BY_ID[s] for s in wanted if s in _scenes.PART_BY_ID]
             if images else [])

    # EVERY PICTURE IN THIS RUN GOES INTO ONE BATCH, cut and posed here and drawn in one
    # browser at the end — see `Batch`. What is queued is only what the guards above did not
    # stand down, so a run that moved nothing still starts no browser at all.
    batch = Batch()

    # THE PART SHOTS ARE CUT FIRST because they cost no appliance. A run asked for nothing but
    # part shots never stands the machine at all.
    for part in parts:
        print(f"\n{part.id} — {part.title}: {part.step}")
        print(f"-> {draw_part(part, batch, force=args.force).relative_to(_ROOT)}")

    if scenes:
        print(f"\nbuilding the machine once for {len(scenes)} scene(s)…")
        import enclosure_assembly as ea
        draw_all(scenes, ea.build_enclosure_assembly(), batch, force=args.force,
                 images=images, glbs=glbs)

    batch.run()


def draw_all(scenes, assembly, batch, force=False, images=True, glbs=True) -> list:
    """Every scene in `scenes`, off a machine somebody already stood.

    The assembly's own run has one in hand when it writes the STEP, so the pictures cost the
    cuts and the renders rather than a second appliance."""
    out = []
    for scene in scenes:
        names = _scenes.members(scene, assembly)
        print(f"\n{scene.id} — {scene.title}: {len(names)} bodies")
        print("   " + ", ".join(names))
        out.append(draw(scene, assembly, batch, force=force, images=images, glbs=glbs))
        print(f"-> {out[-1].relative_to(_ROOT)}")
    return out


_SOLID_INDEX = re.compile(r"/\d+$")
_LEAF_NAME = re.compile(r"^(.+?)(?:/([1-9]\d*))?$")
_Z_UP_TO_Y_UP = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, -1.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
])


def _body_name(name):
    """The assembly body named by one per-solid payload entry."""
    return _SOLID_INDEX.sub("", name)


def _payload_geometry(path):
    """The positions, normals and triangles in a v2 `.step.mesh`, as zero-copy arrays.

    A GLB carries no BREP-face table, so `fac` stays in the payload rather than being decoded.
    The outer payload has just been written and fluted by `enclosure_assembly.main`; reading
    those triangles is what makes the scene use that exact current surface without standing a
    scene B-rep and tessellating it twice more."""
    path = Path(path)
    raw = path.read_bytes()
    if len(raw) < 4:
        raise ValueError(f"{path}: not a mesh payload")
    head_len = struct.unpack("<I", raw[:4])[0]
    if not head_len or head_len % 4 or 4 + head_len > len(raw):
        raise ValueError(f"{path}: invalid mesh-payload header span")
    try:
        head = json.loads(raw[4:4 + head_len])
    except (UnicodeDecodeError, ValueError, TypeError) as exc:
        raise ValueError(f"{path}: malformed mesh-payload header") from exc
    if not isinstance(head, dict) or not isinstance(head.get("meshes"), list):
        raise ValueError(f"{path}: mesh-payload header has no meshes list")
    if head.get("v") != _mesh_payload.VERSION:
        raise ValueError(
            f"{path}: mesh payload v{head.get('v')!r}, expected v{_mesh_payload.VERSION}")
    blob = memoryview(raw)[4 + head_len:]
    if not head["meshes"]:
        raise ValueError(f"{path}: mesh payload has no leaves")
    out, spans, leaf_names = [], [], set()
    for number, held in enumerate(head["meshes"], 1):
        if not isinstance(held, dict):
            raise ValueError(f"{path}: mesh leaf {number} is not an object")
        name = held.get("name")
        leaf = _LEAF_NAME.fullmatch(name) if isinstance(name, str) else None
        # `_LEAF_NAME` already takes a trailing `/<index>` off, so what is left is the body's
        # own name — `cold-core/evap-coil` included. A slash there names the sub-assembly the
        # body stands in, which is a body's name and not a malformed one.
        if not name or leaf is None:
            raise ValueError(f"{path}: mesh leaf {number} has an invalid name")
        if name in leaf_names:
            raise ValueError(f"{path}: duplicate mesh leaf {name!r}")
        leaf_names.add(name)
        color = held.get("color")
        if color is not None and (
                not isinstance(color, list) or len(color) != 3
                or not all(isinstance(v, (int, float)) and np.isfinite(v) for v in color)):
            raise ValueError(f"{path}: {name!r} has an invalid linear RGB")
        entry = {"name": name, "color": color}
        for key, dtype in (("pos", "<f4"), ("nrm", "<f4"),
                           ("idx", "<u4"), ("fac", "<u4")):
            span = held.get(key)
            if (not isinstance(span, list) or len(span) != 2
                    or any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in span)):
                raise ValueError(f"{path}: {name!r} has an invalid {key} span")
            offset, count = span
            end = offset + count * 4
            if offset % 4 or end > len(blob):
                raise ValueError(f"{path}: {name!r} has a truncated or unaligned {key} span")
            try:
                entry[key] = np.frombuffer(blob, dtype=dtype, count=count, offset=offset)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{path}: {name!r} has an invalid {key} span") from exc
            spans.append((offset, end, name, key))
        if (not len(entry["pos"]) or len(entry["pos"]) % 3
                or len(entry["nrm"]) != len(entry["pos"])
                or not len(entry["idx"]) or len(entry["idx"]) % 3
                or not len(entry["fac"]) or len(entry["fac"]) % 2):
            raise ValueError(f"{path}: {name!r} has malformed vector or index counts")
        if not np.isfinite(entry["pos"]).all() or not np.isfinite(entry["nrm"]).all():
            raise ValueError(f"{path}: {name!r} has non-finite geometry")
        vertices, triangles = len(entry["pos"]) // 3, len(entry["idx"]) // 3
        if int(entry["idx"].max()) >= vertices:
            raise ValueError(f"{path}: {name!r} indexes past its {vertices} vertices")
        face_ranges = entry["fac"].reshape((-1, 2))
        cursor = 0
        for first, last in face_ranges:
            if int(first) != cursor or int(last) < int(first) or int(last) >= triangles:
                raise ValueError(f"{path}: {name!r} has invalid BREP-face triangle ranges")
            cursor = int(last) + 1
        if cursor != triangles:
            raise ValueError(f"{path}: {name!r} does not assign every triangle to a face")
        out.append(entry)
    cursor = 0
    for start, end, name, key in sorted(spans):
        if start != cursor:
            kind = "overlapping" if start < cursor else "gapped"
            raise ValueError(f"{path}: {name!r} has a {kind} {key} span")
        cursor = end
    if cursor != len(blob):
        raise ValueError(f"{path}: mesh payload has {len(blob) - cursor} unclaimed trailing bytes")
    return out


def _core_contract(entries):
    """Validate the action-only core payload against its producing scorecard and style."""
    try:
        card = json.loads(CORE_SCORECARD.read_text())
        bodies = card["bodies"]
        bends = card["bends"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f"{CORE_SCORECARD}: malformed cold-core scorecard") from exc
    if (not isinstance(bodies, list) or not all(isinstance(n, str) and n for n in bodies)
            or not isinstance(bends, list)
            or not all(isinstance(row, dict) and isinstance(row.get("id"), str)
                       and row["id"] for row in bends)):
        raise ValueError(f"{CORE_SCORECARD}: malformed body or bend census")
    expected = tuple(sorted(bodies + [f"line-{row['id']}" for row in bends]))
    if len(expected) != len(set(expected)):
        raise ValueError(f"{CORE_SCORECARD}: duplicate cold-core body name")

    by_body = _entries_by_body(entries)
    missing, extra = sorted(set(expected) - set(by_body)), sorted(set(by_body) - set(expected))
    if missing or extra:
        raise ValueError(
            f"{CORE_MESH}: body census differs from its scorecard"
            f"; missing {', '.join(missing) or 'none'}; extra {', '.join(extra) or 'none'}")

    rgba = {name: _linear_rgba(_cold_core_style.colour_for(name)) for name in expected}
    for name, leaves in sorted(by_body.items()):
        leaf_names = [entry["name"] for entry in leaves]
        want = ([name] if len(leaves) == 1
                else [f"{name}/{i}" for i in range(1, len(leaves) + 1)])
        if sorted(leaf_names) != sorted(want):
            raise ValueError(
                f"{CORE_MESH}: {name!r} leaves are {leaf_names!r}, expected {want!r}")
        for entry in leaves:
            if entry["color"] is None or tuple(entry["color"]) != rgba[name][:3]:
                raise ValueError(
                    f"{CORE_MESH}: {entry['name']!r} linear RGB differs from its source style")
    return rgba


def _location_matrix(location):
    """A CadQuery `Location` as a homogeneous matrix, without an Euler round trip."""
    trsf = location.wrapped.Transformation()
    out = np.eye(4)
    for row in range(3):
        for col in range(4):
            out[row, col] = trsf.Value(row + 1, col + 1)
    return out


def _flip_matrix(flip):
    if not flip:
        return np.eye(4)
    axis, degrees = flip
    return trimesh.transformations.rotation_matrix(np.radians(degrees), axis)


def _linear_rgba(color):
    """The linear RGBA CadQuery's glTF exporter reads off `cq.Color`."""
    from OCP.Quantity import Quantity_TypeOfColor

    rgb = color.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB)
    return tuple(float(v) for v in (*rgb, color.wrapped.Alpha()))


def _assembly_rgba(assembly):
    """Every named body colour in a live assembly, however deep it nests.

    A SUB-ASSEMBLY HAS NO COLOUR AND OWES NONE. `cold-core` is a node the machine holds and not
    a body anybody draws, so what carries a colour is the leaves inside it. Reading `children`
    one level deep would ask the node for a colour it is right not to have, and would miss the
    62 that do."""
    import manifold_layout as ml

    out = {}
    for child_name, _shape, colour in ml.placed_leaves(assembly):
        if colour is None:
            raise ValueError(f"{child_name!r}: scene body has no colour")
        name = _body_name(child_name)
        rgba = _linear_rgba(colour)
        if name in out and out[name] != rgba:
            raise ValueError(f"{name!r}: its solids carry different scene colours")
        out[name] = rgba
    return out


def _entries_by_body(entries):
    out = {}
    for entry in entries:
        out.setdefault(_body_name(entry["name"]), []).append(entry)
    return out


def _scene_material(rgba, index, exact):
    """One shared material per exact RGBA, and the name used to restore its float precision."""
    rgba = tuple(float(v) for v in rgba)
    if rgba in exact:
        return exact[rgba][0]
    name = f"hsm-rgba-{index}"
    args = {"name": name, "baseColorFactor": rgba, "doubleSided": True}
    if rgba[3] < 1.0:
        args.update(alphaMode="BLEND", metallicFactor=0.0)
    material = trimesh.visual.material.PBRMaterial(**args)
    exact[rgba] = (material, name)
    return material


def _payload_mesh(entry, material):
    pos = np.asarray(entry["pos"], dtype=np.float32).reshape((-1, 3))
    nrm = np.asarray(entry["nrm"], dtype=np.float32).reshape((-1, 3))
    idx = np.asarray(entry["idx"], dtype=np.uint32).reshape((-1, 3))
    if len(pos) != len(nrm) or not len(idx):
        raise ValueError(f"{entry['name']!r}: malformed positions, normals, or indices")
    mesh = trimesh.Trimesh(pos, idx, vertex_normals=nrm, process=False, validate=False)
    mesh.visual = trimesh.visual.TextureVisuals(material=material)
    return mesh


def _add_payload_body(scene, name, entries, transform, rgba, material_index, exact):
    """One named body, with a child node per solid where `_per_solid_color` split it."""
    material = _scene_material(rgba, material_index, exact)
    if len(entries) == 1:
        scene.add_geometry(_payload_mesh(entries[0], material),
                           node_name=name, geom_name=entries[0]["name"], transform=transform)
        return
    scene.graph.update(frame_from=scene.graph.base_frame, frame_to=name, matrix=transform)
    for entry in entries:
        scene.add_geometry(_payload_mesh(entry, material), parent_node_name=name,
                           node_name=entry["name"], geom_name=entry["name"])


def _write_payload_glb(path, names, inner, outer_entries, core_entries,
                       outer_rgba, core_rgba, flip, core_to_world, overrides):
    """One scene composed from the two already-meshed named assemblies."""
    outer, core = _entries_by_body(outer_entries), _entries_by_body(core_entries)
    turn = _flip_matrix(flip)
    outer_transform = _Z_UP_TO_Y_UP @ turn
    core_transform = outer_transform @ core_to_world
    scene = trimesh.Scene(base_frame="world")
    exact_materials = {}
    missing = []
    for name in names:
        # THE MACHINE CARRIES THE CORE NOW, so a body of it is in the appliance's own payload,
        # under the name the appliance holds it by, already stood where the appliance stands it.
        # The core's own payload is the fallback and the contract read above still holds it to
        # its card — but a scene draws one model, and the transform it needs is the outer one.
        inside = name in inner and name not in outer
        entries = (core if inside else outer).get(name)
        if not entries:
            missing.append(name)
            continue
        colours = core_rgba if inside else outer_rgba
        if name not in colours and name not in overrides:
            raise ValueError(f"{name!r}: live assembly has no RGBA")
        rgba = overrides.get(name, colours.get(name))
        _add_payload_body(scene, name, entries,
                          core_transform if inside else outer_transform,
                          rgba, len(exact_materials), exact_materials)
    if missing:
        raise ValueError(f"scene payload is missing {', '.join(sorted(missing))}")

    exact_by_name = {name: rgba for rgba, (_material, name) in exact_materials.items()}

    def restore_material_precision(tree):
        # `PBRMaterial` quantises a base factor to u8. RWGltf carries the live linear floats,
        # including alpha, so put them back after trimesh has built the accessor/buffer tree.
        for material in tree.get("materials", ()):
            rgba = exact_by_name.get(material.get("name"))
            if rgba is None:
                continue
            pbr = material.setdefault("pbrMetallicRoughness", {})
            pbr["baseColorFactor"] = list(rgba)
            material["doubleSided"] = True
            if rgba[3] < 1.0:
                material["alphaMode"] = "BLEND"
                pbr["metallicFactor"] = 0.0
            else:
                material.pop("alphaMode", None)
                pbr.pop("metallicFactor", None)

    raw = trimesh.exchange.gltf.export_glb(
        scene, include_normals=True, tree_postprocessor=restore_material_precision)
    Path(path).write_bytes(raw)
    return path


def write_glbs(assembly, require_core_payload=False) -> list:
    """Write every viewer scene from the current appliance mesh and one current core mesh.

    `enclosure_assembly.main` calls this after exporting and fluting the appliance payload, while
    its named machine is still live. Scene membership and every material therefore come from
    that machine. The inner model is stood and tessellated once; each scene after that is only a
    named subset and two node transforms. No scene STEP, scene B-rep tessellation, or GLB graft
    stands on the publication path."""
    outer_entries = _payload_geometry(ASSEMBLY_MESH)
    outer_rgba = _assembly_rgba(assembly)

    # The Bazel action receives the exact mesh and scorecard from //:cold-core-assembly. A
    # missing, stale, or malformed handoff is an error, never permission to rebuild from some
    # ambient checkout. A direct design/render run takes the other branch unconditionally and
    # builds the live core, even when an ignored payload happens to be sitting beside its STEP.
    note_read(CORE_MESH)
    if require_core_payload:
        core_entries = _payload_geometry(CORE_MESH)
        core_rgba = _core_contract(core_entries)
    else:
        import cold_core_assembly as cca
        core = cca.build_assembly()
        core_rgba = _assembly_rgba(core)
        core_entries = _mesh_payload.from_assembly(_per_solid_color(core))
    core_to_world = _location_matrix(assembly.carries[_scenes.INNER_ROOT].where)
    crossings = _scenes.crossings(assembly.runs)

    GLB_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for scene in _scenes.SCENES:
        names = _scenes.members(scene, assembly)
        inner = set(_scenes.inner_of(scene))
        # One continuous tube keeps the outer model's full RGBA across the core boundary.
        overrides = {line: outer_rgba[half]
                     for line, half in crossings.items()
                     if line in names and half in names}
        glb = GLB_DIR / f"{scene.id}.glb"
        _write_payload_glb(glb, names, inner, outer_entries, core_entries,
                           outer_rgba, core_rgba, scene.flip, core_to_world, overrides)
        note_write(glb)
        print(f"-> {glb.relative_to(_ROOT)}")
        out.append(glb)
    return out


def payload_glb_selftest():
    """Focused holds for strict payload reads and exact scene composition."""
    import tempfile

    def tri(name, x):
        return {"name": name,
                "pos": np.array([x, 0, 0, x + 1, 0, 0, x, 1, 0], dtype=np.float32),
                "nrm": np.array([0, 0, 1] * 3, dtype=np.float32),
                "idx": np.array([0, 1, 2], dtype=np.uint32)}

    outer = [tri("wall/1", 0), tri("wall/2", 2), tri("tube", 4)]
    core = [tri("inside", 0), tri("line", 2)]
    wall = (0.123456789, 0.2, 0.3, 1.0)
    tube = (0.7, 0.8, 0.9, 0.6000000238418579)
    inside = (0.4, 0.5, 0.6, 0.3499999940395355)
    carry = np.eye(4)
    carry[:3, 3] = (10, 20, 30)
    flip = ((0, 1, 0), 180.0)
    checks = []

    def check(label, held):
        checks.append((label, bool(held)))
        print(f"  {'ok  ' if held else 'FAIL'} {label}")

    def payload_entry(name, x=0, color=(0.1, 0.2, 0.3), index=(0, 1, 2)):
        return {"name": name, "color": list(color),
                "pos": [x, 0, 0, x + 1, 0, 0, x, 1, 0],
                "nrm": [0, 0, 1] * 3, "idx": list(index), "fac": [0, 0]}

    def rejects(label, path):
        try:
            _payload_geometry(path)
        except ValueError:
            check(label, True)
        else:
            check(label, False)

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "scene.glb"
        _write_payload_glb(
            path, ("wall", "tube", "inside", "line"), {"inside", "line"},
            outer, core, {"wall": wall, "tube": tube},
            {"inside": inside, "line": (0.1, 0.2, 0.3, 1.0)},
            flip, carry, {"line": tube})
        raw = path.read_bytes()
        head_len, kind = struct.unpack_from("<I4s", raw, 12)
        tree = json.loads(raw[20:20 + head_len])
        materials = {tuple(m["pbrMetallicRoughness"]["baseColorFactor"]): m
                     for m in tree["materials"]}
        check("opaque linear floats are not quantised", wall in materials)
        check("inner alpha is exact", inside in materials)
        check("joined line takes the outer tube's full RGBA", tube in materials)
        check("transparent material blends and is nonmetallic",
              materials[tube].get("alphaMode") == "BLEND"
              and materials[tube]["pbrMetallicRoughness"].get("metallicFactor") == 0.0)
        check("every material is double-sided",
              all(m.get("doubleSided") is True for m in tree["materials"]))
        loaded = trimesh.load(path)
        check("multi-solid body keeps its parent and indexed solids",
              "wall" in loaded.graph.nodes
              and {"wall/1", "wall/2"} <= set(loaded.graph.nodes_geometry))
        outer_turn = _Z_UP_TO_Y_UP @ _flip_matrix(flip)
        check("flip has RWGltf's transform semantics",
              np.allclose(loaded.graph["wall"][0], outer_turn))
        check("core carry composes before the scene flip",
              np.allclose(loaded.graph["inside"][0], outer_turn @ carry))
        held_location = cq.Location(cq.Vector(10, 20, 30), cq.Vector(0, 0, 1), 90)
        check("CadQuery carry is read without Euler decomposition",
              np.allclose(_location_matrix(held_location),
                          np.array([[1, 0, 0, 10], [0, 1, 0, 20],
                                    [0, 0, 1, 30], [0, 0, 0, 1]])
                          @ trimesh.transformations.rotation_matrix(
                              np.radians(90), (0, 0, 1), point=(0, 0, 0))))
        check("the GLB JSON chunk is first", kind == b"JSON")

        # A valid payload first, then one mutation per class of silent corruption the strict
        # action handoff refuses. These are byte-format tests; no CadQuery shape is built.
        payload = Path(directory) / "valid.step.mesh"
        _mesh_payload.write([payload_entry("one")], payload)
        check("a complete v2 payload is admitted", len(_payload_geometry(payload)) == 1)

        duplicate = Path(directory) / "duplicate.step.mesh"
        _mesh_payload.write([payload_entry("one"), payload_entry("one", 2)], duplicate)
        rejects("duplicate leaf names are rejected", duplicate)

        truncated = Path(directory) / "truncated.step.mesh"
        truncated.write_bytes(payload.read_bytes()[:-4])
        rejects("truncated spans are rejected", truncated)

        wrong_version = Path(directory) / "wrong-version.step.mesh"
        raw = payload.read_bytes()
        header_len = struct.unpack("<I", raw[:4])[0]
        header = json.loads(raw[4:4 + header_len])
        blob = raw[4 + header_len:]
        header["v"] = _mesh_payload.VERSION + 1
        encoded = json.dumps(header, separators=(",", ":")).encode()
        encoded += b" " * (-(len(encoded) + 4) % 4)
        wrong_version.write_bytes(struct.pack("<I", len(encoded)) + encoded + blob)
        rejects("a payload of another version is rejected", wrong_version)

        malformed = Path(directory) / "malformed.step.mesh"
        malformed.write_bytes(struct.pack("<I", 4) + b"nope")
        rejects("a malformed header is rejected", malformed)

        bad_index = Path(directory) / "bad-index.step.mesh"
        _mesh_payload.write([payload_entry("one", index=(0, 1, 3))], bad_index)
        rejects("indices outside the vertex array are rejected", bad_index)

        bad_face = Path(directory) / "bad-face.step.mesh"
        _mesh_payload.write([payload_entry("one")], bad_face)
        raw = bad_face.read_bytes()
        header_len = struct.unpack("<I", raw[:4])[0]
        header = json.loads(raw[4:4 + header_len])
        blob = raw[4 + header_len:]
        header["meshes"][0]["fac"][0] -= 4
        encoded = json.dumps(header, separators=(",", ":")).encode()
        encoded += b" " * (-(len(encoded) + 4) % 4)
        bad_face.write_bytes(struct.pack("<I", len(encoded)) + encoded + blob)
        rejects("overlapping or gapped spans are rejected", bad_face)

        # The scorecard is the exact body census. Split one body into two properly indexed
        # leaves to exercise the only legal many-solid spelling, and take alpha from the same
        # source colour whose linear RGB every payload leaf must carry.
        card = json.loads(CORE_SCORECARD.read_text())
        expected = sorted(card["bodies"] + [f"line-{row['id']}" for row in card["bends"]])
        entries = []
        for i, name in enumerate(expected):
            rgba = _linear_rgba(_cold_core_style.colour_for(name))
            leaves = (f"{name}/1", f"{name}/2") if name == expected[0] else (name,)
            entries.extend(payload_entry(leaf, i * 3 + j, rgba[:3])
                           for j, leaf in enumerate(leaves))
        contract_path = Path(directory) / "core.step.mesh"
        _mesh_payload.write(entries, contract_path)
        contract = _core_contract(_payload_geometry(contract_path))
        check("scorecard membership and indexed leaves are exact",
              set(contract) == set(expected))
        check("source material alpha survives the mesh boundary",
              contract["reservoir-a"][3]
              == _linear_rgba(_cold_core_style.colour_for("reservoir-a"))[3])
        parsed = _payload_geometry(contract_path)
        parsed[0]["color"] = [0.0, 0.0, 0.0]
        try:
            _core_contract(parsed)
        except ValueError:
            check("a payload RGB that differs from source style is rejected", True)
        else:
            check("a payload RGB that differs from source style is rejected", False)
        try:
            _core_contract(_payload_geometry(contract_path)[1:])
        except ValueError:
            check("a missing scorecard body is rejected", True)
        else:
            check("a missing scorecard body is rejected", False)
        extra = _payload_geometry(contract_path)
        extra.append({**extra[-1], "name": "not-in-the-scorecard"})
        try:
            _core_contract(extra)
        except ValueError:
            check("a body outside the scorecard is rejected", True)
        else:
            check("a body outside the scorecard is rejected", False)

    bad = [label for label, ok in checks if not ok]
    print(f"\n{len(checks) - len(bad)}/{len(checks)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.path.insert(0, str(_HW / "scripts"))
    if sys.argv[1:] == ["selftest"]:
        raise SystemExit(payload_glb_selftest())
    main()
