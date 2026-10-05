#!/usr/bin/env python3
"""Render the frozen rear-port scene with axial cameras and cavity lighting."""
from __future__ import annotations

import json
import math
import subprocess

from PIL import Image

import insertion_actions as shared


ROOT, HARDWARE = shared.ROOT, shared.HARDWARE
OUT = shared.OUT / 'rear-ports'
ART = OUT / 'art'
SOURCE = shared.SNAPSHOTS / 'connect-rear-open.step'
SIZE = (1600, 1120)
SPAN = 70.5
CROP = (565, 40, 1565, 855)
REAR = {
    'c14-inlet', 'keystone-jack', 'co2-inlet', 'bulkhead-water', 'bulkhead-carb',
    'bulkhead-flavor-a', 'bulkhead-flavor-b', 'funnel', 'nameplate', 'nameplate-ink',
    'enclosure-back-bottom', 'enclosure-back-top',
}
JACK = (-37.81, 467.0, 303.9502868652344)


def pose(tilt):
    jack_height = (JACK[2] - 292) / math.sqrt(1 + .16 ** 2)
    target_z = JACK[2] - jack_height * math.sqrt(1 + tilt ** 2)
    return dict(cam=(0, 1, tilt), target=(-3, 467, target_z), span=SPAN, size=SIZE)


def points():
    bounds = shared.mesh_bounds(SOURCE.with_suffix('.step.mesh'))
    result = {'jack-face': JACK, 'jack-port': (JACK[0], JACK[1], JACK[2] - 1)}
    for name in ('co2-inlet', 'bulkhead-water', 'bulkhead-carb',
                 'bulkhead-flavor-a', 'bulkhead-flavor-b', 'c14-inlet'):
        lo, hi = bounds[name]
        result[name] = ((lo[0] + hi[0]) / 2, hi[1], (lo[2] + hi[2]) / 2)
    return result


def private_renderer():
    source = shared.RENDERER.read_text()

    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    replace('from "./browser.js"', f'from {(shared.RENDERER.parent / "browser.js").as_uri()!r}')
    replace('from "../../web/server.js"', f'from {(ROOT / "web/server.js").as_uri()!r}')
    replace('import sharp from "sharp";',
            f'import {{ createRequire }} from "module"; const sharp = createRequire({str(shared.RENDERER)!r})("sharp");')
    replace('const REPO_ROOT = path.resolve(__dirname, "..", "..");',
            f'const REPO_ROOT = {str(ROOT)!r};')
    replace('const opts = defaults();\n  if (entry.cam',
            'const opts = defaults();\n  opts.rear = entry.rear;\n'
            '  opts.cavityShadows = entry.cavityShadows;\n'
            '  opts.anchors = entry.anchors;\n  opts.metadata = entry.metadata;\n  if (entry.cam')
    replace('    const box = new THREE.Box3().setFromObject(currentGroup);', '''
    const rear = new Set(o.rear);
    for (const part of [...currentGroup.children]) {
      if (!rear.has(part.name) && !part.name.startsWith("bulkhead-ring-"))
        currentGroup.remove(part);
    }
    currentGroup.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(currentGroup);''')
    replace('    renderer.render(scene, cam);', '''
    if (o.cavityShadows) {
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      scene.environmentIntensity = 0.05;
      currentGroup.traverse((part) => {
        if (part.isMesh) { part.castShadow = true; part.receiveShadow = true; }
      });
      for (const light of scene.children.filter(part => part.isDirectionalLight)) {
        const toward = light.position.clone().normalize();
        light.position.copy(center).addScaledVector(toward, radius * 4);
        light.target.position.copy(center);
        scene.add(light.target);
        light.castShadow = true;
        light.shadow.mapSize.set(4096, 4096);
        Object.assign(light.shadow.camera, {
          left: -radius * 1.8, right: radius * 1.8,
          top: radius * 1.8, bottom: -radius * 1.8,
          near: radius, far: radius * 7,
        });
        light.shadow.camera.updateProjectionMatrix();
        light.shadow.bias = -0.00002;
      }
    }
    renderer.render(scene, cam);''')
    replace('    if (!o.__debug) return { png, state: null };', '''
    const registration = { parts: currentGroup.children.map(p => p.name), points: {} };
    for (const [name, point] of Object.entries(o.anchors)) {
      const p = new THREE.Vector3(...point).project(cam);
      registration.points[name] = [(p.x + 1) * window.innerWidth / 2,
                                   (1 - p.y) * window.innerHeight / 2];
    }
    if (!o.__debug) return { png, state: null, registration };''')
    replace('    return { png, state: {', '    return { png, registration, state: {')
    replace('  fs.writeFileSync(outAbs, buf);',
            '  fs.writeFileSync(outAbs, buf);\n'
            '  fs.writeFileSync(opts.metadata, JSON.stringify(shot.registration, null, 2) + "\\n");')
    path = OUT / 'render-scenes.mjs'
    path.write_text(source)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    anchors = points()
    metadata, jobs = {}, []
    for name, tilt in [('rear-near-axial', .04), ('rear-level', 0),
                       ('rear-cavity-shadow', .12)]:
        camera = pose(tilt)
        metadata[name] = dict(
            **camera, projection='orthographic', up=(0, 0, 1), trim=False,
            crop=CROP, pixel_origin='top-left', source_step=str(SOURCE.relative_to(ROOT)),
            lighting=(dict(environment_intensity=.05, directional_shadows=True,
                           shadow_map_size=4096, shadow_bias=-.00002)
                      if name == 'rear-cavity-shadow' else dict(studio_default=True)),
            points={key: shared.anchor(point, camera) for key, point in anchors.items()})
        jobs.append(dict(
            step=str(SOURCE.relative_to(HARDWARE)), out=str(ART / f'{name}.png'),
            cam=camera['cam'], target=camera['target'], span=SPAN, size='1600x1120',
            up=(0, 0, 1), bg='#f2eee8', transparent=True, solid=True, ortho=True,
            trim=False, ground=False, fog=False, rear=sorted(REAR), anchors=anchors,
            metadata=str(OUT / f'{name}.render.json'),
            cavityShadows=name == 'rear-cavity-shadow'))
    manifest = OUT / 'scenes.json'
    manifest.write_text(json.dumps(jobs, indent=2) + '\n')
    subprocess.run(['node', str(private_renderer()), '--jobs', str(manifest)],
                   cwd=ROOT, check=True)
    for name, entry in metadata.items():
        with Image.open(ART / f'{name}.png') as rendered:
            assert rendered.mode == 'RGBA' and rendered.size == SIZE
            entry['alpha_bounds'] = rendered.getchannel('A').getbbox()
        registration = json.loads((OUT / f'{name}.render.json').read_text())
        entry['retained_meshes'] = len(registration['parts'])
        for key, anchor in entry['points'].items():
            assert max(abs(a - b) for a, b in zip(anchor['pixel'], registration['points'][key])) < 1e-5
    (OUT / 'anchors.json').write_text(json.dumps(dict(scenes=metadata), indent=2) + '\n')
    print(OUT / 'anchors.json')


if __name__ == '__main__':
    main()
