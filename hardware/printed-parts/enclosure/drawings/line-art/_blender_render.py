"""Blender-driven SVG renderer for the enclosure iso line-art drawings.

The appliance solid (CadQuery) is exported as STL and rendered by
Blender's Freestyle line engine into an SVG. After the render, the
script adds a red disc fill at the CO2 port location and clips it by
the projected silhouette of the coupler so the visible portion of the
disc reads as a ring around the coupler.

Steps:

1. Export appliance as STL into a temp dir.
2. Invoke Blender headless with `_blender_scene.py`. Inside Blender,
   the scene script renders the appliance with Freestyle strokes, then
   computes the red disc + coupler silhouette and injects them into
   the SVG with `clip-path`.
3. Post-process the SVG (stroke caps, namespace cleanup, group stroke).
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_BLENDER_SCENE = _HERE / "_blender_scene.py"

# STL tessellation tolerance — small enough that the ~10 mm hex outline,
# ring annulus, and cup ellipses look smooth at the rendered scale.
STL_TOLERANCE = 0.05


def _find_blender() -> str:
    """Resolve the `blender` binary; fall back to the macOS .app bundle."""
    for cmd in ("blender", "/opt/homebrew/bin/blender"):
        if shutil.which(cmd) or Path(cmd).exists():
            return cmd
    macos_app = Path("/Applications/Blender.app/Contents/MacOS/Blender")
    if macos_app.exists():
        return str(macos_app)
    raise RuntimeError("blender executable not found")


def _export_stl(workplane: cq.Workplane, dest: Path) -> None:
    cq.exporters.export(
        workplane, str(dest), exportType="STL", tolerance=STL_TOLERANCE
    )


def _postprocess_svg(svg_path: Path) -> None:
    """Patch the SVG file the Freestyle SVG Exporter emits.

    Fixes:
    - `fill_rule` (the exporter writes an underscored form that some
      renderers ignore) -> `fill-rule`.
    - `stroke-linecap="butt"` -> `stroke-linecap="round"` so adjacent
      stroke endpoints meet cleanly instead of leaving sub-pixel scratches.
    - Strips the exporter's white fills. Even with the BORDER-only fill
      predicate, the exporter emits white-filled regions for any
      not-quite-manifold edges in the imported appliance STL (CSG joins
      produce a handful). On a light background they're invisible; on a
      dark one they paint every white blob over the line art. A line
      drawing wants strokes + markings, NOT a white silhouette.

      A port marking is spared, white or not: it is a ring the machine
      actually wears, and the tap-water station's is white. Markings are
      the only CLIPPED paths in the file — the scene script gives each one
      the clip that bites its fitting's silhouette out of it — so carrying
      a clip-path is what tells a marking from an exporter artifact.
    """
    import re

    text = svg_path.read_text()

    # fill_rule (exporter bug) -> fill-rule
    text = text.replace('fill_rule="', 'fill-rule="')

    # Smooth stroke endpoints
    text = text.replace('stroke-linecap="butt"', 'stroke-linecap="round"')

    # Strip the exporter's white fills; keep a clipped one, which is a marking.
    def _keep_only_markings(m):
        return m.group(0) if "clip-path=" in m.group(0) else ""

    text = re.sub(
        r'\s*<path\b[^/]*?fill="rgb\(255,\s*255,\s*255\)"[^/]*/>',
        _keep_only_markings,
        text,
    )

    # Strip inkscape: namespace attributes and declarations. The exporter
    # decorates groups with inkscape:groupmode / inkscape:label for the
    # benefit of Inkscape's layer panel — purely informational. When the
    # SVG gets embedded inside another <svg> (e.g. the quickstart sheet),
    # the inner inkscape: attributes are stranded without a namespace
    # declaration and rsvg-convert's PDF backend rejects the whole file.
    text = re.sub(r'\s+xmlns:inkscape="[^"]+"', "", text)
    text = re.sub(r'\s+inkscape:[\w-]+="[^"]+"', "", text)

    # Set stroke on the strokes group so that `stroke: inherit !important`
    # (applied by the quickstart sheet's CSS to undo the site's dark-mode
    # recolor) resolves to a real color. Per-path `stroke="rgb(0,0,0)"`
    # attributes get overridden by the !important rule, and with no
    # stroke set anywhere up the inheritance chain the computed value
    # falls back to `none` — strokes disappear in the PDF. Putting the
    # color on the group means `inherit` lands on a defined value.
    # Idempotent: only add the color when the group has no stroke yet.
    # The match group spans the whole opening tag, so re-running on
    # already-processed SVG (or exporter output that already carries a
    # stroke) is a no-op rather than appending a second stroke=/fill= pair —
    # which would produce duplicate attributes (invalid XML) that churn the
    # file on every regen.
    def _set_strokes_color(m):
        attrs = m.group(1)
        if "stroke=" in attrs:
            return m.group(0)
        return f'{attrs} stroke="rgb(0,0,0)" fill="none">'

    text = re.sub(r'(<g\b[^>]*\bid="strokes"[^>]*)>', _set_strokes_color, text)

    svg_path.write_text(text)


def render_iso(
    appliance: cq.Workplane,
    markings: list,
    view: str,
    out_svg: Path,
    *,
    anchors: list = (),
    image_height: int = 800,
    stroke_width: float = 3,
    margin: float = 20.0,
) -> None:
    """Render the iso view of `appliance` plus a set of marking discs.

    Each entry in `markings` is a dict:
        {"id": str,                       # unique clip id stem
         "disc": {center, axis, radius},  # the printed marking circle
         "color": [r, g, b],              # 0-255 fill color
         "clip": cq.Workplane}            # the part that occludes it

    Each disc is projected, filled in its color, and clipped by the
    projected silhouette of its `clip` solid, so the part occludes the
    disc's center and the visible remainder reads as a ring around it.

    Each entry in `anchors` is a dict {"id": str, "point": [x, y, z]};
    the point is projected through the same camera and emitted as an
    invisible zero-radius <circle id=...> so a consumer can aim at it."""
    if view not in ("front", "back"):
        raise ValueError(f"unknown view: {view}")
    out_svg = Path(out_svg)
    out_svg.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="enclosure-iso-") as tmpdir:
        tmp = Path(tmpdir)
        appliance_stl = tmp / "appliance.stl"
        _export_stl(appliance, appliance_stl)

        marking_args = []
        for i, mk in enumerate(markings):
            clip_stl = tmp / f"clip_{i}.stl"
            _export_stl(mk["clip"], clip_stl)
            marking_args.append({
                "id": mk["id"],
                "disc": mk["disc"],
                "color": mk["color"],
                "clip_stl": str(clip_stl),
            })

        args = {
            "appliance_stl": str(appliance_stl),
            "markings": marking_args,
            "anchors": list(anchors),
            "out_svg": str(out_svg),
            "view": view,
            "image_height": image_height,
            "stroke_width": stroke_width,
            "margin": margin,
        }
        args_path = tmp / "args.json"
        args_path.write_text(json.dumps(args))

        cmd = [
            _find_blender(),
            "--background",
            "--python", str(_BLENDER_SCENE),
            "--",
            str(args_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not out_svg.exists():
            raise RuntimeError(
                f"blender render failed (rc={result.returncode}):\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    _postprocess_svg(out_svg)
