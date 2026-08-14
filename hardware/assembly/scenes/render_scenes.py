"""Draw the unit cards' pictures — one scene STEP and one PNG per finished sub-assembly.

    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py            # all
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top   # one
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py --force    # anyway

THE MACHINE IS BUILT ONCE for however many scenes are asked for: a scene is a subset of that one
assembly, so the cost of four pictures is the cost of one build plus four cuts. What lands in the
tree is the PNG and a fingerprint beside it; the scene STEPs go to `out/`, which `.gitignore`
holds, because they are a rendering intermediate and a 20 MB artifact that churns on every move
of any body is exactly what this must not add to a commit.

`//:render-scenes` is what runs it: the build hands this the assembly's STEP and takes the
pictures back, and it runs when that STEP moves.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
for _p in (_HERE.parent, _HW / "scripts", _HW / "manifold-layout",
           _HW / "printed-parts" / "cold-core"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _scenes                                          # noqa: E402
from _cadq_export import export_assembly, note_write    # noqa: E402

OUT_DIR = _HERE.parent / "out"
IMG_DIR = _HW / "assembly" / "cards" / "img"
GLB_DIR = _HERE.parent / "glb"
GLB_TOL = 0.5
RENDERER = _ROOT / "tools" / "render" / "render-step-posed.js"
SIZE = "1600x1200"


def png_for(scene) -> Path:
    return IMG_DIR / f"scene-{scene.id}.png"


# The core's own bodies, placed, for however many scenes in one run ask for them. Standing the
# cold core costs a fraction of standing the machine and nothing at all for a run that never
# reaches inside it — `render_scenes.py back-top` builds what it always did.
_CORE = {}


def core_bodies(carry):
    """Every body the cold core's own assembly places, stood where the machine stands the core.

    `enclosure_assembly` imports `foam-assembly.step` as ONE solid, so the machine has no handle
    on the top cap, on the vessel, or on a line inside the shell — and those ARE what a bench
    unit of the core is made of. `cold-core-layout/cold_core_assembly` has them, and it builds in
    `foam-assembly`'s own frame: the same five printed pieces, and everything else around them.

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


def draw(scene, assembly, force=False) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GLB_DIR.mkdir(parents=True, exist_ok=True)
    step = OUT_DIR / f"{scene.id}.step"
    scene_assembly, target = cut(assembly, scene)
    export_assembly(scene_assembly, str(step))

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
    note_write(glb)

    png = png_for(scene)
    # THE PICTURE IS DRAWN BY NODE, below Python, and the sidecar beside it is not. Both are
    # what this run makes, and this is the one place that holds either name.
    note_write(png)

    # WHAT THE PICTURE IS OF IS THIS FILE. The scene's STEP is the exact geometry the renderer is
    # handed, and the scene's own tuple is the camera it is handed with — so two runs agreeing on
    # both would hand the browser the same job. A source moving is what makes a scene worth
    # doubting; these two are what answer the doubt, and most edits in this tree move neither.
    geometry = _scenes.digest_of(step)
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
        rel = step.relative_to(_HW).as_posix()      # the renderer takes a content-root path
        cmd = [
            "node", str(RENDERER), rel, str(png),
            "--cam", ",".join(str(v) for v in scene.cam),
            "--target", ",".join(f"{v:.3f}" for v in target),
            "--up", ",".join(str(v) for v in scene.up),
            "--zoom", str(scene.zoom),
            "--size", SIZE,
            # Trimmed to the subject. A box seen at an angle projects to a parallelogram and
            # leaves a corner of any rectangle empty; the card wants the picture, not the corner.
            "--trim",
            # A unit as a hand meets it: opaque walls, and what is seen of the inside seen
            # through the mouth the unit leaves open. The viewer ghosts an assembly otherwise.
            "--solid",
        ]
        print("   " + " ".join(cmd[1:]))
        subprocess.run(cmd, cwd=str(_ROOT), check=True)

    # What the picture is OF: the scene's own tuple hashed, the geometry it was drawn of, the
    # picture that came out, and the bodies that went into it — the machine's answer at the
    # moment of the render. Committed beside the PNG, which the scene STEP is not.
    _scenes.sidecar_path(png).write_text(json.dumps({
        "scene": _scenes.scene_digest(scene),
        "geometry": geometry,
        "drawn": sorted(c.name for c in scene_assembly.children),
        "image": _scenes.image_fingerprint(png),
    }, indent=2, sort_keys=True) + "\n")
    return png


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scenes", nargs="*", help="scene ids; default every one")
    ap.add_argument("--force", action="store_true",
                    help="redraw even where the geometry and the camera both stand")
    args = ap.parse_args()

    wanted = args.scenes or [s.id for s in _scenes.SCENES]
    unknown = [s for s in wanted if s not in _scenes.SCENE_BY_ID]
    if unknown:
        ap.error(f"no such scene: {', '.join(unknown)} — have "
                 f"{', '.join(s.id for s in _scenes.SCENES)}")
    scenes = [_scenes.SCENE_BY_ID[s] for s in wanted]

    print(f"building the machine once for {len(scenes)} scene(s)…")
    import enclosure_assembly as ea
    draw_all(scenes, ea.build_enclosure_assembly(), force=args.force)


def draw_all(scenes, assembly, force=False) -> list:
    """Every scene in `scenes`, off a machine somebody already stood.

    The assembly's own run has one in hand when it writes the STEP, so the pictures cost the
    cuts and the renders rather than a second appliance."""
    out = []
    for scene in scenes:
        names = _scenes.members(scene, assembly)
        print(f"\n{scene.id} — {scene.title}: {len(names)} bodies")
        print("   " + ", ".join(names))
        out.append(draw(scene, assembly, force=force))
        print(f"-> {out[-1].relative_to(_ROOT)}")
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(_HW / "scripts"))
    main()
