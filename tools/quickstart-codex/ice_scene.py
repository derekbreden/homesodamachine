#!/usr/bin/env python3
"""Model and render ice in the owner guides' frozen first-pour scene."""
from pathlib import Path
import argparse
import json
import math
import os
import subprocess
import sys

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
OUT = HARDWARE / 'quickstart-codex/out/ice'
SOURCE = HARDWARE / 'quickstart-codex/out/pour-legibility/pour-running.step'
RENDERER = ROOT / 'tools/render/render-step-posed.js'
os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')
sys.path.insert(0, str(HARDWARE / 'scripts'))
from _cadq_export import _per_solid_color, _write_mesh_payload

GLASS_CENTER = (0, -133.99672200476698)
CAMERA = (1, -1.8, .67)


def scene():
    assembly = cq.Assembly.load(str(SOURCE))
    result = cq.Assembly(name='first-pour-with-ice')
    for child in assembly.children:
        result.add(child)
    length = math.hypot(*CAMERA[:2])
    front = (CAMERA[0] / length, CAMERA[1] / length)
    right = (-front[1], front[0])
    cubes = [
        (-14, -8, 78, (21, 21, 23), (11, -8, 18)),
        (15, -10, 79, (21, 21, 22), (-9, 12, -19)),
        (0, 15, 76, (22, 21, 24), (8, -9, 34)),
    ]
    layers = [
        (14.8, 10.3, -12, (18.8, 19.0, 16.8)),
        (33.4, 10.8, 14, (20.0, 19.7, 17.2)),
        (51.9, 11.1, -5, (20.4, 20.1, 17.0)),
    ]
    turns = [(-2, 2, -2), (2, -1, 2), (-1, -2, -3), (1, 2, 3)]
    alignment = math.degrees(math.atan2(right[1], right[0]))
    for z, spread, yaw, size in layers:
        angle = math.radians(yaw)
        for (u, v), (rx, ry, rz) in zip(
                [(-spread, -spread), (spread, -spread),
                 (spread, spread), (-spread, spread)], turns):
            u, v = (u*math.cos(angle)-v*math.sin(angle),
                    u*math.sin(angle)+v*math.cos(angle))
            cubes.append((u, v, z, size, (rx, ry, alignment-yaw+rz)))
    for i, (u, v, z, size, angles) in enumerate(cubes, 1):
        cube = cq.Workplane('XY').box(*size).edges().fillet(2.1)
        for axis, angle in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), angles):
            cube = cube.rotate((0, 0, 0), axis, angle)
        x = GLASS_CENTER[0] + right[0]*u + front[0]*v
        y = GLASS_CENTER[1] + right[1]*u + front[1]*v
        cube = cube.translate((x, y, z))
        result.add(cube, name=f'ice-{i}', color=cq.Color(.83, .92, .97))
    target = OUT / 'pour-with-ice.step'
    colored = _per_solid_color(result)
    colored.export(str(target))
    _write_mesh_payload(target, colored)
    return target


def renderer():
    source = RENDERER.read_text()

    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    replace('from "./browser.js"', f'from {(RENDERER.parent / "browser.js").as_uri()!r}')
    replace('from "../../web/server.js"', f'from {(ROOT / "web/server.js").as_uri()!r}')
    replace('import sharp from "sharp";',
            f'import {{ createRequire }} from "module"; const sharp = createRequire({str(RENDERER)!r})("sharp");')
    replace('const REPO_ROOT = path.resolve(__dirname, "..", "..");', f'const REPO_ROOT = {str(ROOT)!r};')
    replace('const opts = defaults();\n  if (entry.cam',
            'const opts = defaults();\n  opts.iceStyle = entry.iceStyle;\n'
            '  opts.colaOpacity = entry.colaOpacity;\n  if (entry.cam')
    replace('if (page && pageSize === want) {', 'if (false) {')
    replace('renderer.render(scene, cam);', '''
    const drink = currentGroup.children.find(part => part.name === "drink");
    if (!drink) throw new Error("The frozen first-pour scene has no cola.");
    // Keep the drink's depth dark beneath its translucent near surfaces.
    const back = new THREE.Mesh(drink.geometry.clone(), new THREE.MeshBasicMaterial({
      color: "#351a0f", side: THREE.BackSide,
    }));
    back.name = "cola-depth";
    back.position.copy(drink.position);
    back.quaternion.copy(drink.quaternion);
    back.scale.copy(drink.scale);
    currentGroup.add(back);
    currentGroup.traverse((part) => {
      if (!part.isMesh) return;
      if (part.name === "countertop" || part.name.startsWith("glass-edge-") ||
          part.name.startsWith("glass-highlight-") || part.name === "glass-rim-edge" ||
          part.name === "glass-base-edge") {
        part.visible = false;
      } else if (part.name === "glass") {
        part.material = new THREE.MeshPhysicalMaterial({
          color: "#d6e8ec", opacity: 0.045, transparent: true,
          roughness: 0.15, metalness: 0.05, depthWrite: false, side: THREE.DoubleSide,
        });
        part.renderOrder = 10;
      } else if (part.name === "glass-rim" || part.name === "glass-base") {
        part.material = new THREE.MeshBasicMaterial({color: "#edf2f3"});
      } else if (part.name === "drink") {
        const geometry = part.geometry.clone();
        const normals = geometry.getAttribute("normal");
        const index = geometry.getIndex();
        const kept = [];
        for (let i = 0; i < index.count; i += 3) {
          const triangle = [index.getX(i), index.getX(i+1), index.getX(i+2)];
          if (triangle.reduce((sum, j) => sum + normals.getZ(j), 0) < 1.5)
            kept.push(...triangle);
        }
        geometry.setIndex(kept);
        part.geometry = geometry;
        part.material = new THREE.MeshBasicMaterial({
          color: "#351a0f", transparent: o.colaOpacity < 1,
          opacity: o.colaOpacity, depthWrite: o.colaOpacity === 1,
        });
        part.renderOrder = 2;
      } else if (part.name === "drink-top") {
        part.material = new THREE.MeshBasicMaterial({
          color: "#6f422b", transparent: o.colaOpacity < 1,
          opacity: o.colaOpacity, depthWrite: o.colaOpacity === 1,
        });
        part.renderOrder = 3;
      } else if (part.name.startsWith("ice-")) {
        const geometry = part.geometry.clone();
        const normals = geometry.getAttribute("normal");
        const colors = [];
        const light = new THREE.Vector3(-.25, -.65, 1).normalize();
        const dark = new THREE.Color("#7594a8");
        const pale = new THREE.Color("#f0f9ff");
        for (let i = 0; i < normals.count; i++) {
          const n = new THREE.Vector3().fromBufferAttribute(normals, i);
          const t = Math.min(1, Math.max(0, .25 + .8*n.dot(light)));
          const color = dark.clone().lerp(pale, t);
          colors.push(color.r, color.g, color.b);
        }
        geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
        part.geometry = geometry;
        part.material = new THREE.MeshBasicMaterial({
          vertexColors: true, toneMapped: false, transparent: o.iceStyle === "clear",
          opacity: o.iceStyle === "clear" ? .78 : 1,
        });
        part.renderOrder = 1;
      }
    });
    renderer.render(scene, cam);''')
    target = OUT / 'render-ice.mjs'
    target.write_text(source)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style', choices=['frosted', 'clear'], default='clear')
    parser.add_argument('--cola-opacity', type=float, default=.82)
    parser.add_argument('--compare', action='store_true')
    args = parser.parse_args()
    if not 0 < args.cola_opacity <= 1:
        parser.error('--cola-opacity must be between 0 and 1')
    OUT.mkdir(parents=True, exist_ok=True)
    step = scene()
    entries = []
    for opacity in ([.70, .82] if args.compare else [args.cola_opacity]):
        directory = OUT / f'cola-{round(opacity*100)}'
        directory.mkdir(exist_ok=True)
        job = dict(step=str(step.relative_to(HARDWARE)), out=str(directory / 'pour-base.png'),
                   iceStyle=args.style, colaOpacity=opacity,
                   cam=CAMERA, target=(0, -78, 119), span=140,
                   size='1600x1500', up=(0, 0, 1), bg='#ffffff', transparent=True,
                   solid=True, ortho=True, trim=False, ground=False, fog=False)
        entries.append(job)
    jobs = OUT / 'jobs.json'
    jobs.write_text(json.dumps(entries, indent=2)+'\n')
    subprocess.run(['node', str(renderer()), '--jobs', str(jobs)], cwd=ROOT, check=True)
    for job in entries:
        print(job['out'])


if __name__ == '__main__':
    main()
