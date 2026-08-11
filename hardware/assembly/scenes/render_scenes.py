"""Draw the unit cards' pictures — one scene STEP and one PNG per finished sub-assembly.

    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py            # all
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top   # one
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py --stale     # only moved

THE MACHINE IS BUILT ONCE for however many scenes are asked for: a scene is a subset of that one
assembly, so the cost of four pictures is the cost of one build plus four cuts. What lands in the
tree is the PNG and a fingerprint beside it; the scene STEPs go to `out/`, which `.gitignore`
holds, because they are a rendering intermediate and a 20 MB artifact that churns on every move
of any body is exactly what this must not add to a commit.

Run when a picture has gone stale — `hardware/scripts/check_scenes.py` says which, off text
alone — not on every build.
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
from _cadq_export import export_assembly                # noqa: E402

OUT_DIR = _HERE.parent / "out"
IMG_DIR = _HW / "assembly" / "cards" / "img"
RENDERER = _ROOT / "tools" / "render" / "render-step-posed.js"
SIZE = "1500x1150"


def png_for(scene) -> Path:
    return IMG_DIR / f"scene-{scene.id}.png"


def cut(assembly, scene):
    """The scene as its own assembly: the named children of the built machine, each world-placed
    and keeping its own colour, so the picture is the machine's own geometry and not a redraw."""
    import enclosure_assembly as ea
    placed = ea._solids(assembly)
    out = cq.Assembly(name=scene.id)
    for name in _scenes.members(scene, assembly):
        solid, colour = placed[name]
        out.add(solid, name=name, color=colour)
    return out


def draw(scene, assembly) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    step = OUT_DIR / f"{scene.id}.step"
    export_assembly(cut(assembly, scene), str(step))

    png = png_for(scene)
    rel = step.relative_to(_HW).as_posix()          # the renderer takes a content-root path
    cmd = [
        "node", str(RENDERER), rel, str(png),
        "--cam", ",".join(str(v) for v in scene.cam),
        "--up", ",".join(str(v) for v in scene.up),
        "--zoom", str(scene.zoom),
        "--size", SIZE,
    ]
    print("   " + " ".join(cmd[1:]))
    subprocess.run(cmd, cwd=str(_ROOT), check=True)

    # What drew it, so `check_scenes` can doubt the picture without importing anything: the
    # scene's own tuple hashed, and every repo file the build reads, walked from in here where
    # the graph is complete and free.
    _scenes.sidecar_path(png).write_text(json.dumps({
        "scene": _scenes.scene_digest(scene),
        "sources": _scenes.source_map(),
    }, indent=2, sort_keys=True) + "\n")
    return png


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scenes", nargs="*", help="scene ids; default every one")
    ap.add_argument("--stale", action="store_true",
                    help="only the scenes whose fingerprint has moved")
    args = ap.parse_args()

    import check_scenes

    wanted = args.scenes or [s.id for s in _scenes.SCENES]
    unknown = [s for s in wanted if s not in _scenes.SCENE_BY_ID]
    if unknown:
        ap.error(f"no such scene: {', '.join(unknown)} — have "
                 f"{', '.join(s.id for s in _scenes.SCENES)}")
    scenes = [_scenes.SCENE_BY_ID[s] for s in wanted]
    if args.stale:
        scenes = [s for s in scenes if check_scenes.state(s)[0] != "current"]
        if not scenes:
            print("every scene carries the picture its sources make")
            return

    print(f"building the machine once for {len(scenes)} scene(s)…")
    import enclosure_assembly as ea
    assembly = ea.build_enclosure_assembly()

    for scene in scenes:
        names = _scenes.members(scene, assembly)
        print(f"\n{scene.id} — {scene.title}: {len(names)} bodies")
        print("   " + ", ".join(names))
        print(f"-> {draw(scene, assembly).relative_to(_ROOT)}")


if __name__ == "__main__":
    sys.path.insert(0, str(_HW / "scripts"))
    main()
