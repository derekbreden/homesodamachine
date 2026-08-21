"""Draw the assembly cards' pictures — every scene and every part shot in `_scenes`.

    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py             # all
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top    # one scene
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py en08-drippan # one part
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

`//:render-scenes` is what runs it: the build hands this the assembly's STEP and takes the
pictures back, and it runs when that STEP moves.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
for _p in (_HERE.parent, _HW / "scripts", _HW / "manifold-layout",
           _HW / "printed-parts" / "cold-core", _ROOT / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _mesh_payload                                    # noqa: E402
import _scenes                                          # noqa: E402
import flute_payload                                    # noqa: E402
from docgen import note_rewritten                       # noqa: E402
from _cadq_export import note_read, note_write, _per_solid_color   # noqa: E402

OUT_DIR = _HERE.parent / "out"
IMG_DIR = _HW / "assembly" / "cards" / "img"
GLB_DIR = _HERE.parent / "glb"
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


# The core's own bodies, placed, for however many scenes in one run ask for them. Standing the
# cold core costs a fraction of standing the machine and nothing at all for a run that never
# reaches inside it — `render_scenes.py back-top` builds what it always did.
_CORE = {}


def core_bodies(carry):
    """Every body the cold core's own assembly places, stood where the machine stands the core.

    `enclosure_assembly` imports `foam-assembly.step` as ONE solid, so the machine has no handle
    on the top cap, on the vessel, or on a line inside the shell — and those ARE what a bench
    unit of the core is made of. `cold-core-layout/cold_core_assembly` has them, and it builds in
    `foam-assembly`'s own frame: the same six printed pieces, and everything else around them.

    `carry.where` is the placement the machine seats that stack under, so it is what stands
    these."""
    import cold_core_assembly as cca

    where = carry.where
    key = repr(where.toTuple())
    if key not in _CORE:
        core = cca.build_assembly()
        _CORE[key] = {c.name: (c.obj.moved(where), c.color) for c in core.children}
    return _CORE[key]


def cut(assembly, scene):
    """The scene as its own assembly, and the point the camera looks at.

    Every named body, world-placed and keeping its own colour, so the picture is the model's own
    geometry and not a redraw. A name `inner` claims comes from the cold core's frame and the
    rest from the machine's. The look-at point is what is drawn OF the unit — the roots, or the
    core's own bodies where a scene draws those instead. See `_scenes.SCENES`."""
    import enclosure_assembly as ea
    placed = ea._solids(assembly)
    inner = set(_scenes.inner_of(scene))
    core = core_bodies(assembly.carries[_scenes.INNER_ROOT]) if inner else {}
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


def draw(scene, assembly, batch, force=False) -> Path:
    # THE RENDERER IS READ WHETHER OR NOT THIS RUN STARTS IT. A scene whose geometry and camera
    # both stand skips the browser, and a trace of that run would not see node's command line
    # at all — so the file that draws every picture here would go undeclared, and the action
    # that redraws one would not find it.
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
    # `parts-tree.js:45` and `BUILD.bazel` each name it as one they do not carry — so it is
    # written straight, the way the `.glb` below is.
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
    glb = GLB_DIR / f"{scene.id}.glb"
    scene_assembly.export(str(glb), tolerance=GLB_TOL, angularTolerance=GLB_TOL)
    # AND THE SAME SUBSTITUTION THE PAYLOAD ABOVE TOOK. This mesh is cut from the B-rep too, and
    # it is what /3d opens a scene AS — there is no STEP behind it to fall back to — so a piece
    # left as exported is drawn smooth wherever a reader browses the bench.
    in_glb = flute_payload.graft_glb(glb, fluted_pieces(surfaces=True))
    if in_glb:
        print(f"   ({in_glb} fluted piece(s) into {glb.name})")
    note_write(glb)

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
    own: `render_scenes.py en08-drippan` needs no appliance."""
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scenes", nargs="*", help="scene or part-shot ids; default every one")
    ap.add_argument("--force", action="store_true",
                    help="redraw even where the geometry and the camera both stand")
    args = ap.parse_args()

    every = [s.id for s in _scenes.SCENES] + [p.id for p in _scenes.PARTS]
    wanted = args.scenes or every
    unknown = [s for s in wanted if s not in _scenes.SCENE_BY_ID and s not in _scenes.PART_BY_ID]
    if unknown:
        ap.error(f"no such picture: {', '.join(unknown)} — have {', '.join(every)}")
    scenes = [_scenes.SCENE_BY_ID[s] for s in wanted if s in _scenes.SCENE_BY_ID]
    parts = [_scenes.PART_BY_ID[s] for s in wanted if s in _scenes.PART_BY_ID]

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
        draw_all(scenes, ea.build_enclosure_assembly(), batch, force=args.force)

    batch.run()


def draw_all(scenes, assembly, batch, force=False) -> list:
    """Every scene in `scenes`, off a machine somebody already stood.

    The assembly's own run has one in hand when it writes the STEP, so the pictures cost the
    cuts and the renders rather than a second appliance."""
    out = []
    for scene in scenes:
        names = _scenes.members(scene, assembly)
        print(f"\n{scene.id} — {scene.title}: {len(names)} bodies")
        print("   " + ", ".join(names))
        out.append(draw(scene, assembly, batch, force=force))
        print(f"-> {out[-1].relative_to(_ROOT)}")
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(_HW / "scripts"))
    main()
