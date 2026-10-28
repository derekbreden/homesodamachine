#!/usr/bin/env python3
"""The app's HoldAtFaucet picture: a phone held to the faucet display the way people hold one
at a card reader, its top half over the display and its bottom half toward the person.

The faucet is the current source model above the counter, as the install guide builds it. The
phone is a prop: a plain outline, lying parallel to the display a little off its face. One
colored scene STEP is rendered the guide's way and written, trimmed, to the app's asset.
"""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
sys.path.insert(0, str(HARDWARE / 'install-guide'))
os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')

import cadquery as cq  # noqa: E402
from PIL import Image  # noqa: E402
import _cad_art as art  # noqa: E402

SCENE = HARDWARE / 'assembly/scenes/out/faucet-phone.step'
RENDER = HARDWARE / 'assembly/scenes/out/faucet-phone.png'
ASSET = ROOT / 'ios/SodaMachine/SodaMachine/Assets.xcassets/HoldAtFaucet.imageset/HoldAtFaucet.png'

GAP = 30.0      # the phone's back off the display screen, mm
OVER = 22.0     # the phone's top edge past the screen's centre, along the screen, mm
TWIST = -7.0    # the phone turned in its own plane, as a hand holds it, degrees
PHONE = (71.6, 147.6, 7.8)   # a common phone's outline and thickness, mm
CAMERA = dict(cam=(1.0, -0.85, 0.5), target=(0, -95, 125), span=150, size='2000x2000')
WIDTH = 1200    # the asset's width, px

ABOVE_COUNTER = (
    'westbrass', 'drain_tube', 'soda_faucet_tube', 'tpu_o_ring',
    'flavor_tube_pos_x', 'flavor_tube_neg_x', 'lever',
    'above_counter_plate', 'above_counter_gasket', 'shell_base', 'shell_tip',
    'faucet-display-cover-seated', 'faucet_display', 'faucet_display_screen',
)


def scene() -> Path:
    fa = art._load_faucet_module()
    parts = art._children_by_name(fa.build_assembly())
    lever_rest, _ = art._physical_levers(fa)
    out = cq.Assembly(name='faucet-phone')
    for name in ABOVE_COUNTER:
        child = parts[name]
        obj = lever_rest if name == 'lever' else child.obj
        if name in {'westbrass', 'drain_tube', 'flavor_tube_pos_x', 'flavor_tube_neg_x'}:
            obj = art._clip_z(obj, fa.countertop_top_z, 260.0)
        art._add_child(out, child, obj=obj)

    # The screen's tilt, from its own extents: it faces forward and up.
    screen = parts['faucet_display_screen'].obj
    box = (screen.val() if hasattr(screen, 'val') else screen).BoundingBox()
    centre = cq.Vector((box.xmin + box.xmax) / 2, (box.ymin + box.ymax) / 2, (box.zmin + box.zmax) / 2)
    dy, dz = box.ymax - box.ymin, box.zmax - box.zmin
    up = cq.Vector(0, dy, dz).normalized()
    normal = cq.Vector(0, -dz, dy).normalized()
    tilt = cq.Vector(0, 1, 0).getAngle(up) * 180 / 3.141592653589793

    w, h, t = PHONE
    body = (cq.Workplane('XY').box(w, h, t, centered=(True, True, False))
            .edges('|Z').fillet(10.5).edges('>Z or <Z').fillet(1.6))
    glass = (cq.Workplane('XY').workplane(offset=t - 0.2)
             .box(w - 4.2, h - 4.2, 0.45, centered=(True, True, False)).edges('|Z').fillet(8.6))
    island = (cq.Workplane('XY').workplane(offset=t + 0.2)
              .center(0, h / 2 - 11.6).rect(19.5, 5.8).extrude(0.25).edges('|Z').fillet(2.85))
    at = centre + normal * GAP + up * (OVER - h / 2)

    def place(shape):
        shape = shape.rotate((0, 0, 0), (0, 0, 1), TWIST).rotate((0, 0, 0), (1, 0, 0), tilt)
        return shape.translate((at.x, at.y, at.z))

    out.add(place(body), name='phone_body', color=cq.Color(0.80, 0.82, 0.85))
    out.add(place(glass), name='phone_screen', color=cq.Color(0x17 / 255, 0x49 / 255, 0xD1 / 255))
    out.add(place(island), name='phone_island', color=cq.Color(0.04, 0.04, 0.05))
    SCENE.parent.mkdir(parents=True, exist_ok=True)
    return art._export_colored(out, SCENE, mesh=True)


def render(step: Path) -> None:
    job = dict(step=str(step.relative_to(HARDWARE)), out=str(RENDER), up=(0, 0, 1), bg='#ffffff',
               transparent=True, solid=True, ortho=True, trim=False, ground=False, fog=False,
               **CAMERA)
    jobs = RENDER.with_suffix('.json')
    jobs.write_text(json.dumps([job], indent=2) + '\n')
    subprocess.run(['node', str(ROOT / 'tools/render/render-step-posed.js'), '--jobs', str(jobs)],
                   cwd=ROOT, check=True)


def asset() -> None:
    image = Image.open(RENDER).convert('RGBA')
    left, top, right, bottom = image.getbbox()
    pad = 40
    image = image.crop((left - pad, top - pad, right + pad, bottom + pad))
    image = image.resize((WIDTH, round(image.height * WIDTH / image.width)), Image.LANCZOS)
    image.save(ASSET, optimize=True)
    print(ASSET, image.size)


if __name__ == '__main__':
    render(scene())
    asset()
