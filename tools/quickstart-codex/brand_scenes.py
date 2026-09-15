#!/usr/bin/env python3
"""Apply the approved white mark to the quick start's frozen power scene."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

import numpy as np
from PIL import Image

import insertion_actions as shared


ROOT = shared.ROOT
OUT = shared.SNAPSHOTS / 'brand-scenes'
OUTPUT = shared.ART / 'power-ready.png'
MARK = ROOT / 'brand/mark.svg'


def renderer():
    source = shared.private_renderer().read_text()

    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    replace('  opts.action = entry.action;',
            '  opts.action = entry.action;\n  opts.brandSvg = entry.brandSvg;\n  opts.oldMarkIndices = entry.oldMarkIndices;')
    replace('    const xray = await import("/js/viewer/xray.js");', '''
    const xray = await import("/js/viewer/xray.js");
    const { SVGLoader } = await import("three/addons/loaders/SVGLoader.js");
    const brandPaths = o.brandSvg ? new SVGLoader().parse(o.brandSvg).paths : [];
    const branding = { replaced: [], added: [] };''')
    replace('    currentGroup.updateMatrixWorld(true);', '''
    if (o.brandSvg) {
      const plate = currentGroup.children.find(part => part.name === "nameplate");
      const oldMark = currentGroup.children.filter(part =>
        part.name === "nameplate-ink" && o.oldMarkIndices.includes(part.userData.occtIndex));
      if (!plate || oldMark.length !== 4 || brandPaths.length !== 2)
        throw new Error(`The frozen nameplate or approved mark has changed: plate=${!!plate}, old=${oldMark.length}, paths=${brandPaths.length}`);
      const white = oldMark[0].material.clone();
      white.side = THREE.DoubleSide;
      // The old solids fill corresponding recesses in the plate. Matching its
      // material makes a flush black face without leaving an engraved old mark.
      const filled = plate.material.clone();
      for (const part of oldMark) {
        part.material = filled;
        branding.replaced.push({ name: part.name, index: part.userData.occtIndex });
      }
      const scale = (75.39459991455078 - 52.85329818725586) / 640;
      const centerX = (75.39459991455078 + 52.85329818725586) / 2;
      const centerZ = (291.43499755859375 + 262.2349853515625) / 2;
      for (const [index, path] of brandPaths.entries()) {
        for (const shape of SVGLoader.createShapes(path)) {
          const geometry = new THREE.ShapeGeometry(shape, 48);
          const positions = geometry.getAttribute("position");
          for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i), y = positions.getY(i);
            positions.setXYZ(i, centerX - (x - 504) * scale, 467.02,
                             centerZ - (y - 504) * scale);
          }
          positions.needsUpdate = true;
          const indices = geometry.getIndex();
          for (let i = 0; i < indices.count; i += 3) {
            const b = indices.getX(i + 1);
            indices.setX(i + 1, indices.getX(i + 2));
            indices.setX(i + 2, b);
          }
          geometry.computeVertexNormals();
          const mark = new THREE.Mesh(geometry, white);
          mark.name = `guide-brand-mark/${index}`;
          currentGroup.add(mark);
          branding.added.push(mark.name);
        }
      }
      if (branding.added.length !== 2)
        throw new Error("The approved mark must produce one faucet and one drop");
    }
    currentGroup.updateMatrixWorld(true);''')
    replace('const registration = { moved, points: {} };',
            'const registration = { moved, branding, points: {} };')
    # Both jobs mount the same STEP. A fresh page keeps the comparison's cord
    # displacement from being applied twice to a viewer-cached group.
    replace('if (page && pageSize === want) {', 'if (false) {')
    path = OUT / 'render-brand.mjs'
    path.write_text(source)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    backup = OUT / 'power-ready-before-brand.png'
    if not backup.exists():
        shutil.copy2(OUTPUT, backup)
    entry = shared.metadata('power-ready')
    mesh = (ROOT / entry['source_mesh']).read_bytes()
    header_length = struct.unpack_from('<I', mesh)[0]
    meshes = json.loads(mesh[4:4 + header_length])['meshes']
    old_names = {f'nameplate-ink/{n}' for n in range(1, 5)}
    old_indices = [index for index, item in enumerate(meshes) if item['name'] in old_names]
    assert len(old_indices) == 4
    jobs = []
    for name, branded in [('baseline', False), ('on-tap', True)]:
        jobs.append(dict(
            step=str(Path(entry['source_step']).relative_to('hardware')),
            out=str(OUT / f'{name}.png'), cam=entry['cam'], target=entry['target'],
            span=entry['span'], size='1800x1300', up=(0, 0, 1), bg='#f2eee8',
            transparent=True, solid=True, ortho=True, trim=False,
            ground=False, fog=False, action=entry['action'],
            anchors={key: value['world'] for key, value in entry['points'].items()},
            metadata=str(OUT / f'{name}.render.json'),
            brandSvg=MARK.read_text() if branded else None,
            oldMarkIndices=old_indices,
        ))
    manifest = OUT / 'scenes.json'
    manifest.write_text(json.dumps(jobs, indent=2) + '\n')
    subprocess.run(['node', str(renderer()), '--jobs', str(manifest)], cwd=ROOT, check=True)

    old = np.array(Image.open(backup).convert('RGBA'))
    baseline = np.array(Image.open(OUT / 'baseline.png').convert('RGBA'))
    branded = np.array(Image.open(OUT / 'on-tap.png').convert('RGBA'))
    assert old.shape == baseline.shape == branded.shape == (1300, 1800, 4)
    assert np.array_equal(old, baseline), 'The baseline no longer matches the frozen illustration'
    assert np.array_equal(baseline[:, :, 3], branded[:, :, 3]), 'The silhouette moved'
    changed = np.any(baseline != branded, axis=2)
    yy, xx = np.nonzero(changed)
    bounds = [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]
    assert 990 <= bounds[0] <= bounds[2] <= 1185 and 860 <= bounds[1] <= bounds[3] <= 1190, bounds
    for name in ('baseline', 'on-tap'):
        measured = json.loads((OUT / f'{name}.render.json').read_text())
        for key, point in entry['points'].items():
            assert max(abs(a - b) for a, b in zip(point['pixel'], measured['points'][key])) < 1e-5
    report = dict(source_mesh_sha256=entry['source_mesh_sha256'],
                  brand_sha256=hashlib.sha256(MARK.read_bytes()).hexdigest(),
                  dimensions=[1800, 1300], action=entry['action'],
                  changed_bounds=bounds, changed_pixels=int(changed.sum()),
                  baseline_changed_pixels=int(np.any(old != baseline, axis=2).sum()),
                  alpha_unchanged=True, anchor_tolerance_pixels=1e-5)
    (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    for name, image in [('before', baseline), ('after', branded)]:
        Image.fromarray(image).crop((875, 780, 1640, 1290)).save(OUT / f'{name}-detail.png')
    shutil.copy2(OUT / 'on-tap.png', OUTPUT)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
