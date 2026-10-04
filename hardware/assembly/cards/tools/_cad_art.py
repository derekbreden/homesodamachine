"""Render the drill/crimp station CAD panels in their SVG annotation frames.

The native STEP files retain their source materials and dimensions. Both panels
look down +Z with +Y up. Existing SVG feature anchors establish orthographic
scale and target, so changing the background does not move the callouts.
The PCBA keeps its explanatory x-ray presentation and simplified component
envelopes from pcba-board.step; this is not a production-board photograph.

    tools/cad-venv/bin/python hardware/assembly/cards/tools/_cad_art.py

Writes two PNGs and img/cad-art.json. Does not build CAD or PDFs.
"""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/render/render-step-posed.js").is_file())
HARDWARE = ROOT / "hardware"
ENDCAP = HARDWARE / "cut-parts/carbonation/endcaps-circular"
PCBA = HARDWARE / "printed-parts/electronics/pcba-tray"
sys.path.insert(0, str(ENDCAP))
sys.path.insert(0, str(PCBA))
import endcap_circular_step as cap
import pcba_tray as board

BACKGROUND = "#DCE6FF"
WIDTH, HEIGHT = 1980, 1040


class Anchors(HTMLParser):
    def __init__(self, tag, marker):
        super().__init__()
        self.tag, self.marker, self.items = tag, marker, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == self.tag and attrs.get("class") == self.marker:
            self.items.append(attrs)


def anchors(path, tag, marker):
    parser = Anchors(tag, marker)
    parser.feed(path.read_text())
    assert len(parser.items) == 2, (path, tag, marker)
    if tag == "circle":
        return [(float(a["cx"]), float(a["cy"])) for a in parser.items]
    return [(float(a["x"]) + float(a["width"]) / 2,
             float(a["y"]) + float(a["height"]) / 2) for a in parser.items]


def pose(points, pixels):
    """+Z orthographic projection fitted to two horizontal feature anchors."""
    scale = (pixels[1][0] - pixels[0][0]) / (points[1][0] - points[0][0])
    assert scale > 0 and abs(points[0][1] - points[1][1]) < 1e-7
    assert abs(pixels[0][1] - pixels[1][1]) < 1e-7
    target = [points[0][0] - (pixels[0][0] - WIDTH / 2) / scale,
              points[0][1] + (pixels[0][1] - HEIGHT / 2) / scale, 0]
    return {"cam": [0, 0, 1], "up": [0, 1, 0], "target": target,
            "span": HEIGHT / (2 * scale), "size": f"{WIDTH}x{HEIGHT}",
            "bg": BACKGROUND, "trim": False, "ortho": True,
            "ground": False, "fog": False, "transparent": False}


def project(point, options):
    scale = HEIGHT / (2 * options["span"])
    return [WIDTH / 2 + (point[0] - options["target"][0]) * scale,
            HEIGHT / 2 - (point[1] - options["target"][1]) * scale]


def connector_centers():
    """Read current J4/J7 placement and their native model-envelope centers."""
    circuit = json.loads((HARDWARE / "pcb/pcba/out/pcba.circuit.json").read_text())
    source_names = {e["source_component_id"]: e.get("name") for e in circuit
                    if e.get("type") == "source_component"}
    placements = {source_names.get(e.get("source_component_id")): e["center"]
                  for e in circuit if e.get("type") == "pcb_component"}
    boxes = board._glb_component_boxes()
    points = []
    for name in ("J4", "J7"):
        x, y = placements[name]["x"], placements[name]["y"]
        candidates = [b for b in boxes
                      if abs((b[0] + b[1]) / 2 - x) < 1e-6
                      and abs((b[2] + b[3]) / 2 - y) < 4
                      and 15 < b[1] - b[0] < 25]
        assert len(candidates) == 1, (name, candidates)
        b = candidates[0]
        points.append(((b[0] + b[1]) / 2 - board._centre[0],
                       (b[2] + b[3]) / 2 - board._centre[1]))
    return points


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cap_card, board_card = HERE / "dp-drill-press.html", HERE / "cr-crimp-bench.html"
    cap_pixels = anchors(cap_card, "circle", "rng")
    board_pixels = anchors(board_card, "rect", "box")
    cap_points, board_points = cap.hole_positions, connector_centers()
    cap_pose, board_pose = pose(cap_points, cap_pixels), pose(board_points, board_pixels)
    jobs = [
        {"step": str((ENDCAP / "endcap-circular-2hole.step").relative_to(HARDWARE)),
         "out": str(HERE / "img/dp-endcap-face.png"), "solid": True, **cap_pose},
        {"step": str((PCBA / "pcba-board.step").relative_to(HARDWARE)),
         "out": str(HERE / "img/cr-pcba.png"), "solid": False, **board_pose},
    ]
    for job in jobs:
        native = cq.importers.importStep(str(HARDWARE / job["step"])).val()
        assert native.isValid() and native.Volume() > 0, job["step"]
    subprocess.run(["node", str(ROOT / "tools/render/render-step-posed.js"), "--jobs", "-"],
                   input=json.dumps(jobs), text=True, cwd=ROOT, check=True)

    sources = [Path(__file__), cap_card, board_card,
               ENDCAP / "endcap_circular_step.py", ENDCAP / "endcap_circular_dxf.py",
               PCBA / "pcba_tray.py", PCBA / "pcba_assembly.py",
               HARDWARE / "printed-parts/electronics/module_tray.py",
               HARDWARE / "pcb/pcba/pcba.tsx", HARDWARE / "pcb/pcba/out/pcba.circuit.json",
               HARDWARE / "pcb/pcba/out/pcba.glb", ROOT / "tools/render/render-step-posed.js"]
    scenes = {}
    for job, points, pixels, card in zip(jobs, (cap_points, board_points),
                                       (cap_pixels, board_pixels), (cap_card, board_card)):
        output = Path(job["out"])
        source = HARDWARE / job["step"]
        with Image.open(output) as image:
            assert image.size == (WIDTH, HEIGHT), image.size
            assert image.convert("RGB").getpixel((0, 0)) == (220, 230, 255)
        scenes[output.stem] = {"file": output.name, "sha256": digest(output),
                              "source_step": str(source.relative_to(ROOT)),
                              "source_step_sha256": digest(source),
                              "card": str(card.relative_to(ROOT)),
                              "render": {k: v for k, v in job.items() if k not in ("step", "out")},
                              "feature_points_mm": points, "svg_anchor_pixels": pixels,
                              "projected_feature_pixels": [project(p, job) for p in points]}
    scenes["dp-endcap-face"]["blind_register_projected_pixel"] = project(cap.register_position, cap_pose)
    record = {"generator": str(Path(__file__).relative_to(ROOT)), "background": BACKGROUND,
              "image_size_px": [WIDTH, HEIGHT],
              "scope": "Native top-view renders registered to existing SVG feature anchors. Materials and dimensions come from STEP; PCBA preserves its simplified-envelope x-ray presentation.",
              "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
              "scenes": scenes}
    (HERE / "img/cad-art.json").write_text(json.dumps(record, indent=2) + "\n")
    print("wrote img/cad-art.json", flush=True)


if __name__ == "__main__":
    main()
