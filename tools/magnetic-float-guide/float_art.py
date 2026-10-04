"""Hand-run CAD illustrations for the all-ASA Aero magnetic-float guide.

Every float solid comes from all_aero_float.build(), including its enclosed
RC62 pocket. A cutaway keeps the rear half to expose the pocket and guide
bore. Warm white is ASA Aero White GFB02; silver is the purchased magnet.
Accent highlights identify the inserted ring or plastic after the pause.
Insertion arrows, plate tiles and the guide rod are explanatory proxies.
The artwork does not depict emitted extrusion roads.

The paused view clips the current CAD at the expected last open 0.20 mm layer
plane. That layer grid requires a separate native slice review; these images
do not establish a prepared project, printed fit or physical qualification.

    tools/cad-venv/bin/python tools/magnetic-float-guide/float_art.py
    tools/cad-venv/bin/python tools/magnetic-float-guide/float_art.py --list

This is a manual guide asset pass, not part of the CAD publish/build graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARDWARE = ROOT / "hardware"
FLOAT = HARDWARE / "printed-parts" / "cold-core" / "magnetic-float" / "all-aero"
INTERFACE = FLOAT.parents[1] / "_float_interface.py"
ART = HARDWARE / "magnetic-float-guide" / "art"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(FLOAT))
from _cadq_export import _per_solid_color
from _material_base import step_safe
import all_aero_float as mf

AERO = cq.Color(0.92, 0.90, 0.85)
NICKEL = cq.Color(0.68, 0.71, 0.76)
ACCENT_HEX = "#d64050"
ARROW_HEX = "#1749d1"
ACCENT = cq.Color(ACCENT_HEX)
ARROW = cq.Color(ARROW_HEX)
PLATE = cq.Color(0.73, 0.73, 0.73)
GUIDE = cq.Color(0.50, 0.55, 0.62)

# At the current layer grid the first expected covering plane is Z16.2.
# The illustration stops at Z16.0, where the annular pocket is still open.
LAST_OPEN_Z = mf.pause_before_z - mf.layer_height
PAUSE_SCOPE = ("Current CAD and nominal layer-grid illustration; expected last "
               "open plane and first covering plane require native slice review.")


@lru_cache(maxsize=1)
def parts():
    body, magnet = mf.build()
    return {"body-aero": body, "magnet": magnet}


def box(width, depth, bottom, top, *, x=0, y=0):
    return cq.Solid.makeBox(width, depth, top - bottom,
                            cq.Vector(x - width / 2, y - depth / 2, bottom))


def scene(name):
    return cq.Assembly(name=f"float-guide-{name}")


def add(a, shape, name, color):
    a.add(shape, name=name, color=step_safe(color))


def cutaway(shape):
    """Keep the rear semicircle. Camera faces the open Y=0 section."""
    return shape.intersect(box(200, 100, -10, 250, y=50)).clean()


def below(shape, top):
    return shape.intersect(box(200, 200, -10, top)).clean()


def paused_body():
    return below(parts()["body-aero"], LAST_OPEN_Z)


def upper_body():
    return parts()["body-aero"].cut(paused_body()).clean()


def arrow_down(x, y, z_top, z_tip, *, radius=0.65):
    """An explanatory arrow beside the physical insertion axis."""
    head_h = min(4.5, (z_top - z_tip) / 3)
    head = cq.Solid.makeCone(0.0, radius * 3.0, head_h,
                             cq.Vector(x, y, z_tip), cq.Vector(0, 0, 1))
    stem = cq.Solid.makeCylinder(radius, z_top - z_tip - head_h,
                                cq.Vector(x, y, z_tip + head_h))
    return head.fuse(stem).clean()


def plate_tile(*, size=52):
    """A cropped build-plate tile; its size is not a printer specification."""
    return box(size, size, -1.0, 0)


def whole(a, *, offset=(0, 0, 0), section=False, prefix=""):
    for name, shape in parts().items():
        if section:
            shape = cutaway(shape)
        color = NICKEL if name == "magnet" else AERO
        add(a, shape.translate(offset), prefix + name, color)
    return a


def s_hero():
    a = scene("hero")
    whole(a, offset=(-24, 0, 0), prefix="finished-")
    whole(a, offset=(24, 0, 0), section=True, prefix="section-")
    return a


def s_finished():
    return whole(scene("finished"))


def s_section():
    return whole(scene("section"), section=True)


def s_exploded():
    """One CAD body in section, with its ring lifted for identification."""
    a = scene("exploded")
    add(a, cutaway(parts()["body-aero"]), "one-body-cutaway", AERO)
    add(a, parts()["magnet"].translate((0, 0, mf.height)), "lifted-RC62", NICKEL)
    return a


def s_plate_aero():
    a = scene("plate-aero")
    add(a, plate_tile(), "plate", PLATE)
    add(a, parts()["body-aero"], "one-upright-body", AERO)
    return a


def s_paused_body():
    a = scene("paused-body")
    add(a, plate_tile(), "plate", PLATE)
    add(a, paused_body(), "open-pocket-body", AERO)
    return a


def s_magnet_seat():
    """Insert only the ring, leaving the paused body attached to its plate."""
    a = scene("magnet-seat")
    add(a, plate_tile(), "plate", PLATE)
    add(a, paused_body(), "open-pocket-body", AERO)
    add(a, parts()["magnet"].translate((0, 0, 10)), "insert-RC62", ACCENT)
    add(a, arrow_down(mf.diameter / 2 + 5, 0, LAST_OPEN_Z + 19, LAST_OPEN_Z + 1),
        "insertion-arrow", ARROW)
    return a


def s_magnet_seated():
    a = scene("magnet-seated")
    add(a, plate_tile(), "plate", PLATE)
    add(a, cutaway(paused_body()), "open-pocket-body-cutaway", AERO)
    add(a, cutaway(parts()["magnet"]), "seated-RC62", NICKEL)
    return a


def s_roof():
    """Accent is the same continuous body above the expected pause plane."""
    a = scene("roof")
    add(a, cutaway(paused_body()), "body-before-pause", AERO)
    add(a, cutaway(parts()["magnet"]), "seated-RC62", NICKEL)
    add(a, cutaway(upper_body()), "body-after-resume", ACCENT)
    return a


def s_guide_fit():
    a = scene("guide-fit")
    whole(a, section=True)
    rod = cq.Solid.makeCylinder(mf.guide_diameter / 2, mf.height + 14,
                                cq.Vector(0, 0, -7))
    add(a, rod, "3p175mm-guide-proxy", GUIDE)
    return a


@dataclass(frozen=True)
class Scene:
    build: object
    caption: str
    cam: tuple = (0.70, -1.0, 0.50)
    size: str = "2100x2100"


SCENES = {
    "hero": Scene(s_hero,
                  "Current one-piece ASA Aero float beside an axial cutaway, with one RC62 at Z14.0 mm.",
                  cam=(0.45, -1, 0.43), size="2600x1700"),
    "exploded": Scene(s_exploded,
                      "One ASA Aero CAD body in cutaway and one RC62 ring lifted for identification. The ring is inserted while the body is still printing.",
                      cam=(0.40, -1, 0.35), size="1700x2400"),
    "section": Scene(s_section,
                     "The 36 × 28 mm ASA Aero body surrounds a 3.60 mm deep enclosed annular pocket and a continuous 4.8 mm guide bore.",
                     cam=(0.30, -1, 0.36), size="2100x1900"),
    "plate-aero": Scene(s_plate_aero,
                        "One ASA Aero body prints upright, flat bottom attached to the glued Engineering plate. Gray is a cropped plate proxy.",
                        cam=(0.45, -1, 0.75), size="2100x1900"),
    "paused-body": Scene(s_paused_body,
                         "Current CAD clipped at the expected last open plane Z16.0, before covering plane Z16.2. Native pause and covering paths require separate review.",
                         cam=(0.40, -1, 0.90), size="2100x1800"),
    "magnet-seat": Scene(s_magnet_seat,
                         "Lower one RC62 into the open annular pocket, keeping the ASA Aero body attached to the plate. Accent identifies the inserted ring; the arrow shows insertion.",
                         cam=(0.50, -1, 0.85), size="2100x2100"),
    "magnet-seated": Scene(s_magnet_seated,
                           "Cutaway of the expected pause state: RC62 flat on the Z12.4125 pocket floor, below both rims, with the guide bore clear.",
                           cam=(0.35, -1, 0.58), size="2100x1700"),
    "roof": Scene(s_roof,
                  "Accent highlights the ASA Aero body above the expected pause plane. The inner collar and outer band meet the pocket cover, and the guide bore remains open.",
                  cam=(0.30, -1, 0.36), size="2100x1900"),
    "finished": Scene(s_finished,
                      "The current one-piece 36 × 28 mm ASA Aero CAD envelope with an open 4.8 mm guide bore. Finished print dimensions and service behavior require physical evidence.",
                      cam=(0.55, -1, 0.70), size="2100x1900"),
    "guide-fit": Scene(s_guide_fit,
                       "A 3.175 mm guide rod proxy passes through the 4.8 mm bore: 0.8125 mm nominal radial clearance. The cutaway shows the enclosed ring clear of the rod.",
                       cam=(0.35, -1, 0.34), size="1900x2300"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(names):
    ART.mkdir(parents=True, exist_ok=True)
    # STEP paths must be served beneath hardware/. Staged files disappear at exit.
    with tempfile.TemporaryDirectory(prefix=".staging-", dir=ART) as directory:
        staging = Path(directory)
        jobs = []
        for name in names:
            spec = SCENES[name]
            path = staging / f"{name}.step"
            _per_solid_color(spec.build()).export(str(path))
            jobs.append({"step": str(path.relative_to(HARDWARE)),
                         "out": str(ART / f"{name}.png"),
                         "cam": list(spec.cam), "up": [0, 0, 1], "size": spec.size,
                         "bg": "#ffffff", "trim": True, "solid": True,
                         "ortho": True, "ground": False, "fog": False,
                         "transparent": True})
            print(f"staged {name}", flush=True)
        subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=ROOT,
                       input=json.dumps(jobs), text=True, check=True)
    for name in names:
        path = ART / f"{name}.png"
        with Image.open(path) as image:
            image.convert("RGBA").save(path, format="PNG", compress_level=9)
        print(f"art/{name}.png — {path.stat().st_size // 1024} KB", flush=True)

    # Partial runs retain only images already bound to these exact sources.
    # A full run refreshes every declared scene and its PNG digest.
    sources = {str(path.relative_to(ROOT)): digest(path) for path in
               (Path(__file__), FLOAT / "all_aero_float.py", INTERFACE)}
    existing = {}
    manifest_path = ART / "manifest.json"
    if manifest_path.is_file():
        old = json.loads(manifest_path.read_text())
        if old.get("source_sha256") == sources:
            existing = old.get("scenes", {})
    scenes = {}
    for name, spec in SCENES.items():
        path = ART / f"{name}.png"
        if name in names or (name in existing and path.is_file()
                             and existing[name].get("sha256") == digest(path)):
            with Image.open(path) as image:
                size = list(image.size)
            scenes[name] = {"file": f"{name}.png", "caption": spec.caption,
                            "sha256": digest(path), "image_size_px": size}
    manifest = {
        "generator": "tools/magnetic-float-guide/float_art.py",
        "geometry": "hardware/printed-parts/cold-core/magnetic-float/all-aero/all_aero_float.py",
        "geometry_sha256": sources[str((FLOAT / "all_aero_float.py").relative_to(ROOT))],
        "interface": str(INTERFACE.relative_to(ROOT)),
        "source_sha256": sources,
        "cad_revision": "v2-upper-clearance",
        "dimensions_mm": {"diameter": mf.diameter, "height": mf.height,
                          "guide_bore": mf.bore_diameter, "guide_rod": mf.guide_diameter,
                          "pocket_depth": mf.pocket_depth, "magnet_center_z": mf.magnet_midplane,
                          "magnet_seat_z": mf.magnet_seat, "pocket_roof_z": mf.pocket_roof,
                          "expected_last_open_plane_z": LAST_OPEN_Z,
                          "expected_first_covering_plane_z": mf.pause_before_z,
                          "layer_height": mf.layer_height},
        "scope": PAUSE_SCOPE,
        "conventions": {"warm_white": "ASA Aero White GFB02; solid shading does not depict foam cells or emitted roads",
                        "silver": "RC62 ring magnet",
                        "accent": "inserted ring or ASA Aero deposited after the expected pause",
                        "accent_hex": ACCENT_HEX,
                        "arrow": "explanatory insertion arrow, not a component",
                        "arrow_hex": ARROW_HEX,
                        "gray_tile": "cropped build-plate proxy, not full printer bed",
                        "steel_gray_rod": "3.175 mm cylindrical guide proxy; no mounting end hardware depicted",
                        "cutaway": "front half removed for visibility; the printed body is one connected solid"},
        "scenes": scenes,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


def main(argv):
    if "--list" in argv:
        print("\n".join(SCENES))
        return 0
    names = [arg for arg in argv if not arg.startswith("-")] or list(SCENES)
    unknown = set(names) - SCENES.keys()
    if unknown:
        raise SystemExit(f"Unknown scenes: {', '.join(sorted(unknown))}")
    render(names)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
