#!/usr/bin/env python3
"""Extract native header models and textured board crops from the published PCBA.

On demand: tools/cad-venv/bin/python tools/harness/extract-j2-board.py [J2 J13]
No board render, invented silkscreen or regenerated component geometry.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import struct

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'hardware/pcb/pcba/out'
DEST = ROOT / 'web/public/harness'
# Board Xmin, Xmax, Ymin, Ymax, in mm. Each crop retains the complete header
# courtyard, function legend, reference designator and both rows of pin labels.
HEADERS = {
    'J2': {'bounds': (5.0, 17.0, -16.0, 5.0),
           'rotation': (-math.pi / 2, 0, 0), 'position': (-110.55, .4, -5.77), 'pinMaterial': 6},
    'J13': {'bounds': (-19.75, -4.75, 27.8, 36.5),
            'rotation': (-math.pi / 2, 0, math.pi / 2), 'position': (-68.55, .4, -12.25), 'pinMaterial': 2},
}


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def extract(name):
    config = HEADERS[name]
    bounds = config['bounds']
    raw = (SOURCE / 'pcba.glb').read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    src = json.loads(raw[20:20 + length])
    binary = raw[28 + length:]
    cj = json.loads((SOURCE / 'pcba.circuit.json').read_text())
    source = next(x for x in cj if x.get('type') == 'source_component' and x.get('name') == name)
    pcb = next(x for x in cj if x.get('type') == 'pcb_component' and x.get('source_component_id') == source['source_component_id'])
    board = next(x for x in cj if x.get('type') == 'pcb_board')
    board_xmin = min(p['x'] for p in board['outline'])
    board_ymax = max(p['y'] for p in board['outline'])
    cad = [x for x in cj if x.get('type') == 'cad_component' and x.get('model_step_url')]
    index = next(i + 1 for i, x in enumerate(cad) if x.get('source_component_id') == source['source_component_id'])
    header_node = src['nodes'][index]
    pin_tip_z = max(src['accessors'][p['attributes']['POSITION']]['max'][2]
                    for p in src['meshes'][header_node['mesh']]['primitives']
                    if p['material'] == config['pinMaterial']) + header_node['translation'][2]
    board_node = src['nodes'][-1]
    # Bind extraction to the board model and texture release the site names.
    release = json.loads((ROOT / 'hardware/cad-artifacts.json').read_text())['solids']
    for filename in ['pcba.glb', 'pcba.top3d.png', 'pcba.bottom3d.png']:
        assert sha(SOURCE / filename) == release[f'hardware/pcb/pcba/out/{filename}'], filename
    assert header_node['mesh'] == index - 1

    dst = {'asset': {'version': '2.0', 'generator': f'{name} crop of the published PCBA'},
           'scene': 0, 'scenes': [{'nodes': [0, 1, 2]}], 'nodes': [], 'meshes': [],
           'materials': src['materials'].copy(), 'accessors': [], 'bufferViews': [],
           'buffers': [], 'images': [], 'textures': [], 'samplers': [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 33071}]}
    buf = bytearray()

    def blob(payload, target=None):
        while len(buf) % 4:
            buf.append(0)
        view = {'buffer': 0, 'byteOffset': len(buf), 'byteLength': len(payload)}
        if target:
            view['target'] = target
        dst['bufferViews'].append(view)
        buf.extend(payload)
        return len(dst['bufferViews']) - 1

    def accessor(values, kind, component=5126):
        width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[kind]
        rows = values if width > 1 else [[x] for x in values]
        flat = [x for row in rows for x in row]
        payload = struct.pack('<' + ('f' if component == 5126 else 'I') * len(flat), *flat)
        acc = {'bufferView': blob(payload, 34962 if component == 5126 else 34963),
               'componentType': component, 'count': len(rows), 'type': kind}
        if kind == 'VEC3':
            acc['min'] = [min(row[k] for row in rows) for k in range(width)]
            acc['max'] = [max(row[k] for row in rows) for k in range(width)]
        dst['accessors'].append(acc)
        return len(dst['accessors']) - 1

    def read(acc_id):
        acc = src['accessors'][acc_id]
        view = src['bufferViews'][acc['bufferView']]
        width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[acc['type']]
        fmt = {5126: 'f', 5125: 'I', 5123: 'H', 5121: 'B'}[acc['componentType']]
        size = struct.calcsize(fmt) * width
        start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
        rows = [list(struct.unpack_from('<' + fmt * width, binary, start + i * view.get('byteStride', size))) for i in range(acc['count'])]
        return rows if width > 1 else [x[0] for x in rows]

    def clip(poly, axis, bound, greater):
        out = []
        for a, b in zip(poly, poly[1:] + poly[:1]):
            ai = a[axis] >= bound if greater else a[axis] <= bound
            bi = b[axis] >= bound if greater else b[axis] <= bound
            if ai:
                out.append(a)
            if ai != bi:
                t = (bound - a[axis]) / (b[axis] - a[axis])
                out.append([a[k] + t * (b[k] - a[k]) for k in range(len(a))])
        return out

    for node, cropped in [(header_node, False), (board_node, True)]:
        batches = {}
        for primitive in src['meshes'][node['mesh']]['primitives']:
            positions = read(primitive['attributes']['POSITION'])
            normals = read(primitive['attributes']['NORMAL'])
            indices = read(primitive['indices'])
            if cropped:
                pts, ns, ids = [], [], []
                for i in range(0, len(indices), 3):
                    poly = [positions[k] + normals[k] for k in indices[i:i + 3]]
                    for axis, bound, greater in [(0, bounds[0] / 1000, True), (0, bounds[1] / 1000, False), (1, bounds[2] / 1000, True), (1, bounds[3] / 1000, False)]:
                        if poly:
                            poly = clip(poly, axis, bound, greater)
                    if len(poly) < 3:
                        continue
                    start = len(pts)
                    pts.extend(p[:3] for p in poly)
                    ns.extend(p[3:] for p in poly)
                    for k in range(1, len(poly) - 1):
                        ids.extend([start, start + k, start + k + 1])
                positions, normals, indices = pts, ns, ids
            if not indices:
                continue
            # CAD tessellation emits a primitive for each tiny face. Retain all
            # source vertices, normals and winding, batching only by material so
            # orbiting the native header does not require hundreds of draw calls.
            batch = batches.setdefault(primitive['material'], {'positions': [], 'normals': [], 'indices': []})
            start = len(batch['positions'])
            batch['positions'].extend(positions)
            batch['normals'].extend(normals)
            batch['indices'].extend(start + i for i in indices)
        primitives = []
        for material, batch in batches.items():
            primitives.append({'attributes': {'POSITION': accessor(batch['positions'], 'VEC3'), 'NORMAL': accessor(batch['normals'], 'VEC3')},
                               'indices': accessor(batch['indices'], 'SCALAR', 5125), 'material': material})
        mesh_index = len(dst['meshes'])
        dst['meshes'].append({'name': f'{name} native header' if not cropped else 'Native board crop', 'primitives': primitives})
        dst['nodes'].append({**{k: v for k, v in node.items() if k not in ('mesh', 'name')}, 'mesh': mesh_index,
                             'name': name if not cropped else 'PCB'})

    faces = []
    texture_crops = {}
    for side, z in [('top', .000705), ('bottom', -.000705)]:
        image = Image.open(SOURCE / f'pcba.{side}3d.png')
        w, h = image.size
        left = math.floor((bounds[0] - board_xmin) / board['width'] * w)
        right = math.ceil((bounds[1] - board_xmin) / board['width'] * w)
        top = math.floor((board_ymax - bounds[3]) / board['height'] * h)
        bottom = math.ceil((board_ymax - bounds[2]) / board['height'] * h)
        texture_crops[side] = {'sourceSize': [w, h], 'pixelBounds': [left, top, right, bottom]}
        png = io.BytesIO()
        image.crop((left, top, right, bottom)).save(png, format='PNG')
        dst['images'].append({'bufferView': blob(png.getvalue()), 'mimeType': 'image/png'})
        dst['textures'].append({'sampler': 0, 'source': len(dst['images']) - 1})
        material = len(dst['materials'])
        dst['materials'].append({'name': f'Actual fabrication {side} face', 'pbrMetallicRoughness': {
            'baseColorTexture': {'index': len(dst['textures']) - 1}, 'metallicFactor': 0, 'roughnessFactor': .85}})
        xmin, xmax, ymin, ymax = [x / 1000 for x in bounds]
        pts = [[xmin, ymin, z], [xmax, ymin, z], [xmax, ymax, z], [xmin, ymax, z]]
        uv = [[((x * 1000 - board_xmin) / board['width'] * w - left) / (right - left), ((board_ymax - y * 1000) / board['height'] * h - top) / (bottom - top)] for x, y, _ in pts]
        faces.append({'attributes': {'POSITION': accessor(pts, 'VEC3'), 'NORMAL': accessor([[0, 0, 1 if side == 'top' else -1]] * 4, 'VEC3'),
                                       'TEXCOORD_0': accessor(uv, 'VEC2')}, 'indices': accessor([0, 1, 2, 0, 2, 3] if side == 'top' else [2, 1, 0, 3, 2, 0], 'SCALAR', 5125), 'material': material})
    dst['nodes'].append({'name': 'Fabrication faces', 'mesh': len(dst['meshes'])})
    dst['meshes'].append({'name': 'Unmodified fabrication textures', 'primitives': faces})
    while len(buf) % 4:
        buf.append(0)
    dst['buffers'] = [{'byteLength': len(buf)}]
    js = json.dumps(dst, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    glb = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(buf)) + struct.pack('<I4s', len(js), b'JSON') + js + struct.pack('<I4s', len(buf), b'BIN\0') + buf
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / f'{name.lower()}-board.glb').write_bytes(glb)
    ports = sorted([x for x in cj if x.get('type') == 'source_port' and x.get('source_component_id') == source['source_component_id']], key=lambda x: x['pin_number'])
    pins = []
    for port in ports:
        pad = next(x for x in cj if x.get('type') == 'pcb_port' and x.get('source_port_id') == port['source_port_id'])
        pins.append({'pin': port['pin_number'], 'label': port['name'], 'boardMm': [pad['x'], pad['y']]})
    evidence = {'source': 'hardware/pcb/pcba/out/pcba.glb', 'sha256': sha(SOURCE / 'pcba.glb'),
                'textures': {side: sha(SOURCE / f'pcba.{side}3d.png') for side in ['top', 'bottom']},
                'header': name, 'headerNode': index, 'headerCad': cad[index - 1]['cad_component_id'],
                'headerPcb': pcb['pcb_component_id'], 'cropMm': bounds, 'textureCrops': texture_crops,
                'pins': pins, 'pinTipZMm': pin_tip_z * 1000, 'padSurfaceZMm': board['thickness'] / 2,
                'pinMaterialName': src['materials'][config['pinMaterial']]['name'],
                'benchPose': {'scale': 1000, 'rotationXYZ': config['rotation'], 'positionMm': config['position']},
                'matingAxis': {'native': [0, 0, 1], 'bench': [0, 1, 0], 'type': 'vertical top-entry'},
                'method': f'Native {name} mesh and board triangles clipped in board XY; triangles batched by native material with unchanged vertex positions, normals and winding. Original fabrication PNG pixels embedded with matching UV coordinates. No retyped silkscreen.'}
    (DEST / f'{name.lower()}-board.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(f'{name} native PCB crop: {len(glb):,} bytes')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('headers', nargs='*', choices=HEADERS, help='Headers to crop; defaults to J2 and J13.')
    for name in parser.parse_args().headers or HEADERS:
        extract(name)


if __name__ == '__main__':
    main()
