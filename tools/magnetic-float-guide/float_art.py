"""Hand-run CAD illustrations for the magnetic-float assembly guide.

Every float solid comes from magnetic_float.build(). A cutaway removes the
front half only to expose the assembly. A coral part is the one the step adds;
the stock materials are Bambu PETG Translucent Clear 32101, warm white ASA Aero
and a nickel magnet. Pale blue diagrammatic shading identifies the clear PETG;
it does not depict pigment or predict the printed shell's optical clarity.
Blue arrows and plate tiles are explanatory proxies, not printed parts.

    tools/cad-venv/bin/python tools/magnetic-float-guide/float_art.py
    tools/cad-venv/bin/python tools/magnetic-float-guide/float_art.py --list

This is a manual guide asset pass, not part of the CAD publish/build graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARDWARE = ROOT / "hardware"
FLOAT = HARDWARE / "printed-parts" / "cold-core" / "magnetic-float"
ART = HARDWARE / "magnetic-float-guide" / "art"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(FLOAT))
from _cadq_export import _per_solid_color
from _material_base import step_safe
import magnetic_float as mf

# The printed shell is Clear 32101. This cool shading keeps its section faces
# distinct from the warm-white Aero without relying on optical transparency.
PETG = cq.Color("#aac4d1")
AERO = cq.Color(0.92, 0.90, 0.85)
NICKEL = cq.Color(0.68, 0.71, 0.76)
CORAL = cq.Color(0.84, 0.25, 0.31)
BLUE = cq.Color(0.23, 0.41, 0.67)
PLATE = cq.Color(0.73, 0.73, 0.73)


@lru_cache(maxsize=1)
def parts():
    return mf.build()


def scene(name):
    return cq.Assembly(name=f"float-guide-{name}")


def add(a, shape, name, color):
    a.add(shape, name=name, color=step_safe(color))


def cutaway(shape):
    """Keep the rear semicircle. Camera faces the open Y=0 section."""
    return shape.intersect(mf.box(200, 100, -10, 250, y=50)).clean()


def below(shape, top):
    return shape.intersect(mf.box(200, 200, -10, top)).clean()


def on_bed(shape):
    return shape.translate((0, 0, -shape.BoundingBox().zmin))


def arrow_down(x, y, z_top, z_tip, *, radius=0.65):
    """An explanatory arrow standing beside the physical insertion axis."""
    head_h = min(4.5, (z_top - z_tip) / 3)
    head = cq.Solid.makeCone(0.0, radius * 3.0, head_h,
                             cq.Vector(x, y, z_tip), cq.Vector(0, 0, 1))
    stem = cq.Solid.makeCylinder(radius, z_top - z_tip - head_h,
                                cq.Vector(x, y, z_tip + head_h))
    return head.fuse(stem).clean()


def plate_tile(x=0, y=0, *, size=55):
    """A cropped build-plate tile; its size is not a printer specification."""
    return mf.box(size, size, -1.0, 0, x=x, y=y)


def paused_shell():
    return below(parts()["body-petg"], mf.roof_bottom)


def roof():
    return parts()["body-petg"].cut(paused_shell()).clean()


def core_with_magnet(a, *, offset=(0, 0, 0), section=False, color=AERO,
                     magnet_color=NICKEL, prefix=""):
    for name, appearance in (("body-aero", color), ("magnet", magnet_color)):
        shape = parts()[name]
        if section:
            shape = cutaway(shape)
        add(a, shape.translate(offset), prefix + name, appearance)


def whole(a, *, offset=(0, 0, 0), section=False):
    for name, shape in parts().items():
        color = PETG if name == "body-petg" else NICKEL if name == "magnet" else AERO
        if section:
            shape = cutaway(shape)
        add(a, shape.translate(offset), f"{name}-{offset[0]:g}", color)
    return a


def s_hero():
    a = scene("hero")
    whole(a, offset=(-26, 0, 0))
    whole(a, offset=(26, 0, 0), section=True)
    return a


def s_finished():
    return whole(scene("finished"))


def s_section():
    return whole(scene("section"), section=True)


def s_exploded():
    """The open shell, core, ring and upper insert lifted along assembly Z."""
    a = scene("exploded")
    add(a, cutaway(paused_shell()), "open-shell", PETG)
    core_lift = mf.roof_bottom - mf.floor + 10
    add(a, parts()["body-aero"].translate((0, 0, core_lift)), "core", AERO)
    add(a, parts()["magnet"].translate((0, 0, core_lift + 14)), "magnet", NICKEL)
    add(a, parts()["insert-aero"].translate((0, 0, core_lift + 27)), "insert", AERO)
    return a


def s_parts():
    """Two printed Aero pieces and the purchased ring, all on the bench."""
    a = scene("parts")
    add(a, on_bed(parts()["body-aero"]).translate((-28, 0, 0)), "core", AERO)
    add(a, on_bed(parts()["insert-aero"]).translate((13, 0, 0)), "insert", AERO)
    add(a, on_bed(parts()["magnet"]).translate((44, 0, 0)), "ring", NICKEL)
    return a


def s_plate_aero():
    """Separate plate crops, matching plates 1 and 2 of the project."""
    a = scene("plate-aero")
    for x, name in ((-33, "body-aero"), (33, "insert-aero")):
        add(a, plate_tile(x), f"plate-{name}", PLATE)
        add(a, on_bed(parts()[name]).translate((x, 0, 0)), name, AERO)
    return a


def s_plate_core():
    a = scene("plate-core")
    add(a, plate_tile(size=55), "plate", PLATE)
    add(a, on_bed(parts()["body-aero"]), "core", AERO)
    return a


def s_plate_insert():
    a = scene("plate-insert")
    add(a, plate_tile(size=55), "plate", PLATE)
    add(a, on_bed(parts()["insert-aero"]), "insert", AERO)
    return a


def s_plate_petg():
    a = scene("plate-petg")
    add(a, plate_tile(size=60), "plate", PLATE)
    add(a, parts()["body-petg"], "finished-shell-shape", PETG)
    return a


def s_magnet_seat():
    """Put the magnet into the cooled core on the bench before the shell job."""
    a = scene("magnet-seat")
    add(a, on_bed(parts()["body-aero"]), "core", AERO)
    lift = 11.0 - mf.floor
    add(a, parts()["magnet"].translate((0, 0, lift)), "magnet", CORAL)
    add(a, arrow_down(20, 0, mf.insert_bottom + 8, mf.insert_bottom - mf.floor),
        "insertion-arrow", BLUE)
    return a


def s_magnet_seated():
    a = scene("magnet-seated")
    core_with_magnet(a, offset=(0, 0, -mf.floor))
    return a


def s_paused_shell():
    a = scene("paused-shell")
    add(a, plate_tile(size=60), "plate", PLATE)
    add(a, cutaway(paused_shell()), "open-shell-cutaway", PETG)
    return a


def s_core_in():
    a = scene("core-in")
    add(a, cutaway(paused_shell()), "open-shell-cutaway", PETG)
    lift = mf.roof_bottom - mf.floor + 7
    core_with_magnet(a, offset=(0, 0, lift), color=CORAL)
    add(a, arrow_down(23, 0, mf.roof_bottom + 30, mf.roof_bottom + 3),
        "insertion-arrow", BLUE)
    return a


def s_core_seated():
    a = scene("core-seated")
    add(a, cutaway(paused_shell()), "open-shell-cutaway", PETG)
    core_with_magnet(a, section=True, color=CORAL)
    return a


def s_insert_in():
    a = scene("insert-in")
    add(a, cutaway(paused_shell()), "open-shell-cutaway", PETG)
    core_with_magnet(a, section=True)
    add(a, parts()["insert-aero"].translate((0, 0, 22)), "upper-insert", CORAL)
    add(a, arrow_down(23, 0, mf.roof_bottom + 20, mf.roof_bottom + 3),
        "insertion-arrow", BLUE)
    return a


def s_insert_push():
    """The insert bears on a partly lowered core for the last even hand push."""
    a = scene("insert-push")
    lift = 8.0
    add(a, cutaway(paused_shell()), "open-shell-cutaway", PETG)
    core_with_magnet(a, section=True, offset=(0, 0, lift))
    add(a, cutaway(parts()["insert-aero"]).translate((0, 0, lift)),
        "upper-insert-pusher", CORAL)
    add(a, arrow_down(23, 0, mf.roof_bottom + 18, mf.roof_bottom + 3),
        "insertion-arrow", BLUE)
    return a


def s_roof_ready():
    a = scene("roof-ready")
    add(a, cutaway(paused_shell()), "open-shell-cutaway", PETG)
    core_with_magnet(a, section=True)
    add(a, cutaway(parts()["insert-aero"]), "upper-insert", CORAL)
    return a


def s_roof():
    a = s_roof_ready()
    a.name = "float-guide-roof"
    # Completed upper insert keeps its stock white; the new roof is coral.
    a.objects["upper-insert"].color = step_safe(AERO)
    add(a, cutaway(roof()), "printed-roof", CORAL)
    return a


def s_lead_in_detail():
    """The lower end of the core, turned up to reveal both entry chamfers."""
    a = scene("lead-in-detail")
    cropped = below(parts()["body-aero"], mf.floor + 10)
    underside_up = on_bed(cropped.rotate((0, 0, 0), (1, 0, 0), 180))
    add(a, underside_up, "core-underside", AERO)
    return a


def s_flush_detail():
    """A cropped cross-section of the complete paused rim and its supports."""
    a = scene("flush-detail")
    clip = mf.box(100, 100, mf.insert_bottom - 5, mf.roof_bottom + 1)
    add(a, cutaway(paused_shell()).intersect(clip), "shell-rim", PETG)
    add(a, cutaway(parts()["body-aero"]).intersect(clip), "core-top", AERO)
    add(a, cutaway(parts()["magnet"]), "magnet", NICKEL)
    add(a, cutaway(parts()["insert-aero"]), "insert", CORAL)
    return a


@dataclass(frozen=True)
class Scene:
    build: object
    caption: str
    cam: tuple = (0.70, -1.0, 0.50)
    size: str = "2100x2100"
    target: tuple | None = None
    span: float | None = None


SCENES = {
    "hero": Scene(s_hero, "Finished float beside a section through its axis. Pale blue shading identifies the clear PETG shell.",
                  cam=(0.45, -1, 0.43), size="2600x2100"),
    "finished": Scene(s_finished, "Finished PETG Translucent Clear 32101 float with its open guide bore. The clear shell is shaded pale blue for visibility."),
    "section": Scene(s_section, "The continuous clear PETG envelope surrounds both Aero pieces and the ring magnet. Pale blue distinguishes PETG from the white Aero.",
                     cam=(0.35, -1, 0.27), size="1700x2400"),
    "exploded": Scene(s_exploded, "Open PETG shell, lower Aero core, ring magnet and upper Aero insert. The roof prints in place after insertion.",
                      cam=(0.45, -1, 0.23), size="1500x2900"),
    "parts": Scene(s_parts, "Cooled Aero core, upper insert and one RC62 ring magnet.",
                   cam=(0.38, -1, 0.70), size="2400x1500"),
    "plate-aero": Scene(s_plate_aero, "Two separate plate crops: core on plate 1, upper insert on plate 2. Both print upright.",
                        cam=(0.35, -1, 0.85), size="2400x1600"),
    "plate-core": Scene(s_plate_core, "Aero core upright, flat bottom down and magnet pocket up.",
                        cam=(0.55, -1, 0.75), size="2000x2000"),
    "plate-insert": Scene(s_plate_insert, "Aero upper insert flat on its annular face.",
                          cam=(0.55, -1, 1.0), size="2100x1500"),
    "plate-petg": Scene(s_plate_petg, "PETG shell upright on the textured plate; its roof is completed after the pause.",
                        cam=(0.55, -1, 0.65), size="2000x2200"),
    "magnet-seat": Scene(s_magnet_seat, "Seat the RC62 ring in the upward-facing recess of the cooled Aero core.",
                         cam=(0.50, -1, 0.72), size="2000x2300"),
    "magnet-seated": Scene(s_magnet_seated, "The ring sits inside the core's top recess, leaving the central bore clear.",
                           cam=(0.55, -1, 1.0), size="2000x2200"),
    "paused-shell": Scene(s_paused_shell, "The shell pauses with its outer and bore walls at 57 mm and its roof still open. Cutaway view.",
                          cam=(0.40, -1, 0.45), size="2000x2300"),
    "core-in": Scene(s_core_in, "Lower the core and its seated magnet over the PETG bore tube. Cutaway shell.",
                     cam=(0.40, -1, 0.30), size="1500x2800"),
    "core-seated": Scene(s_core_seated, "The core stands on the PETG floor, with its magnet at the top. Cutaway view.",
                         cam=(0.35, -1, 0.30), size="1700x2300"),
    "insert-in": Scene(s_insert_in, "Lower the upper Aero insert over the bore tube and onto the core. Cutaway shell and core.",
                       cam=(0.40, -1, 0.40), size="1800x2600"),
    "insert-push": Scene(s_insert_push, "Use the upper insert to press the prepared core down evenly until the insert is level with the PETG rim. Cutaway view.",
                         cam=(0.35, -1, 0.34), size="1900x2500"),
    "roof-ready": Scene(s_roof_ready, "The top of the upper insert is flush with the PETG rim. Cutaway view.",
                        cam=(0.35, -1, 0.30), size="1700x2300"),
    "roof": Scene(s_roof, "Seventeen PETG layers close the roof over the supported insert. Cutaway view.",
                  cam=(0.35, -1, 0.30), size="1700x2300"),
    "lead-in-detail": Scene(s_lead_in_detail, "Underside detail: the 0.5 mm outer and inner lead-ins start the core into the PETG shell. Both Aero pieces have these lower-edge chamfers.",
                            cam=(0.40, -1, 0.80), size="2100x1300"),
    "flush-detail": Scene(s_flush_detail, "At the pause, the upper insert is level with the shell rim and bore lining. The guide bore stays clear. Cropped cutaway.",
                          cam=(0.28, -1, 0.40), size="2300x1500"),
}


def label_lead_ins(path):
    """Project source-geometry chamfer midpoints into the trimmed CAD image.

    The underside detail is a 10 mm cropped end, turned over: its chamfered
    face is at Z=10. The renderer uses the orthographic camera specified above.
    Projection bounds include the true circular silhouette and the 0.5 mm
    bevel. Leaders therefore land on the actual faces rather than guessed
    pixel positions. The labels live outside the part on transparent padding.
    """
    source = Image.open(path).convert("RGBA")
    direction = cq.Vector(*SCENES["lead-in-detail"].cam).normalized()
    right = cq.Vector(0, 0, 1).cross(direction).normalized()
    upward = direction.cross(right).normalized()
    near = cq.Vector(direction.x, direction.y, 0).normalized()
    r, lead, top = mf.core_outer_radius, mf.insertion_lead, 10.0
    pixels_per_mm = (source.width - 1) / (2 * r)
    radial_up = math.hypot(upward.x, upward.y)
    upper_bound = max((top - lead) * upward.z + r * radial_up,
                      top * upward.z + (r - lead) * radial_up)
    side, pad_top = 320, 55
    canvas = Image.new("RGBA", (source.width + side * 2, source.height + pad_top * 2))
    canvas.alpha_composite(source, (side, pad_top))
    draw = ImageDraw.Draw(canvas)
    font_path = HARDWARE / "assembly/cards/fonts/IBMPlexSans-400-700-normal-latin.woff2"
    label_font = ImageFont.truetype(str(font_path), 42)
    label_font.set_variation_by_axes([600])
    size_font = ImageFont.truetype(str(font_path), 34)
    ink = "#1a1a2e"
    blue = "#3a68ac"

    def project(radius, x_fraction, near_fraction):
        point = (right.multiply(radius * x_fraction)
                 .add(near.multiply(radius * near_fraction))
                 .add(cq.Vector(0, 0, top - lead / 2)))
        return (side + (source.width - 1) / 2 + point.dot(right) * pixels_per_mm,
                pad_top + (upper_bound - point.dot(upward)) * pixels_per_mm)

    outer = project(r - lead / 2, -0.8, 0.6)
    inner = project(mf.core_inner_radius + lead / 2, 0.6, -0.8)
    outer_xy = (25, round(outer[1] - 72))
    inner_xy = (side + source.width + 34, round(inner[1] - 100))
    for words, position in (("Outer chamfer", outer_xy), ("Bore chamfer", inner_xy)):
        draw.text(position, words, font=label_font, fill=ink)
        draw.text((position[0], position[1] + 54), f"{lead:g} mm", font=size_font, fill=blue)
    # End with a fine dot on the middle of each sloping face, not in the bore.
    for points in (
        [(outer_xy[0] + 140, outer_xy[1] + 106), (side - 20, outer_xy[1] + 106), outer],
        [(inner_xy[0], inner_xy[1] + 106), (side + source.width - 50, inner_xy[1] + 106), inner],
    ):
        draw.line(points, fill=blue, width=3, joint="curve")
        x, y = points[-1]
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=blue)
    canvas.save(path, format="PNG", compress_level=9)


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
            job = {"step": str(path.relative_to(HARDWARE)),
                   "out": str(ART / f"{name}.png"),
                   "cam": list(spec.cam), "up": [0, 0, 1], "size": spec.size,
                   "bg": "#ffffff", "trim": True, "solid": True,
                   "ortho": True, "ground": False, "fog": False,
                   "transparent": True}
            if spec.target is not None:
                job["target"] = list(spec.target)
            if spec.span is not None:
                job["span"] = spec.span
            jobs.append(job)
            print(f"staged {name}", flush=True)
        subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=ROOT,
                       input=json.dumps(jobs), text=True, check=True)
    for name in names:
        path = ART / f"{name}.png"
        with Image.open(path) as image:
            image.convert("RGBA").save(path, format="PNG", compress_level=9)
        if name == "lead-in-detail":
            label_lead_ins(path)
        print(f"art/{name}.png — {path.stat().st_size // 1024} KB", flush=True)
    manifest = {
        "generator": "tools/magnetic-float-guide/float_art.py",
        "geometry": "hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py",
        "geometry_sha256": hashlib.sha256((FLOAT / "magnetic_float.py").read_bytes()).hexdigest(),
        "conventions": {"pale_blue": "Bambu PETG Translucent Clear 32101 shell; diagrammatic shading, not pigment or a prediction of optical clarity",
                        "petg_shading_hex": "#aac4d1", "warm_white": "ASA Aero",
                        "silver": "RC62 ring magnet", "coral": "part added in this step",
                        "blue": "insertion arrow, not a component",
                        "gray_tile": "cropped build plate, not full printer bed"},
        "scenes": {name: {"file": f"{name}.png", "caption": spec.caption}
                   for name, spec in SCENES.items()},
    }
    (ART / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


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
