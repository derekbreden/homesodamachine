#!/usr/bin/env python3
"""Apply the shared PET-GF appearances to native STEP styles and viewer payloads.

    tools/cad-venv/bin/python hardware/scripts/materialize_material_colors.py --write
    tools/cad-venv/bin/python hardware/scripts/materialize_material_colors.py --check
    tools/cad-venv/bin/python hardware/scripts/materialize_material_colors.py --selftest

Only presentation records and payload color/source metadata may change. Geometry,
component placements, names, and every viewer geometry byte remain identical.
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import cadquery as cq

from _material_base import M_PETGF_BLACK
from _materials import linear, petgf_color

ROOT = Path(__file__).resolve().parents[2]
RECORD = re.compile(r"#(\d+)\s*=\s*(.*?);", re.S)
REF = re.compile(r"#(\d+)")
STYLES = {"COLOUR_RGB", "FILL_AREA_STYLE_COLOUR", "FILL_AREA_STYLE",
          "SURFACE_STYLE_FILL_AREA", "SURFACE_SIDE_STYLE", "SURFACE_STYLE_USAGE",
          "PRESENTATION_STYLE_ASSIGNMENT", "STYLED_ITEM",
          "MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION"}
STRUCTURE = {"PRODUCT", "PRODUCT_DEFINITION_FORMATION", "PRODUCT_DEFINITION",
             "PRODUCT_DEFINITION_SHAPE", "SHAPE_DEFINITION_REPRESENTATION",
             "SHAPE_REPRESENTATION", "ADVANCED_BREP_SHAPE_REPRESENTATION",
             "SHAPE_REPRESENTATION_RELATIONSHIP", "MANIFOLD_SOLID_BREP", "BREP_WITH_VOIDS"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def close(a, b):
    return a is not None and all(abs(x-y) < 1e-7 for x, y in zip(a, b))


def legacy_black(rgb, native=False):
    """Exact signatures of the shared black and its earlier double conversion.

    The separate black-chip appearance is the same Fiberon black stock. Neither
    neutral black PETG nor any bought-in black material has these triples.
    """
    source = [M_PETGF_BLACK, cq.Color(31 / 255, 34 / 255, 35 / 255), cq.Color(.12, .14, .17)]
    candidates = []
    for color in source:
        candidates += [color.toTuple()[:3], linear(color)] if native else [linear(color), linear(cq.Color(*linear(color)))]
    return rgb is not None and any(close(rgb, c) for c in candidates)


def refs(rhs):
    return [int(x) for x in REF.findall(rhs)]


def rgb_of(rhs):
    return tuple(float(x) for x in rhs[rhs.index(",")+1:].rstrip(")").split(","))


def step_colors(text):
    """Change AP214 presentation only; retain all geometry records verbatim."""
    rows, spans, kinds, max_id = {}, {}, {}, 0
    geometry = hashlib.sha256()
    for m in RECORD.finditer(text):
        eid, rhs = int(m[1]), m[2]
        max_id = max(max_id, eid)
        kind = rhs.partition("(")[0].strip()
        if kind not in STYLES:
            geometry.update(m[0].encode())
        if kind in STYLES | STRUCTURE:
            rows[eid], spans[eid], kinds[eid] = rhs, m.span(), kind
    edits, appended = {}, []
    black = M_PETGF_BLACK.toTuple()[:3]
    for eid, kind in kinds.items():
        if kind == "COLOUR_RGB" and legacy_black(rgb_of(rows[eid]), native=True) and not close(rgb_of(rows[eid]), black):
            edits[eid] = f"COLOUR_RGB('',{','.join(format(c, '.12g') for c in black)})"
            rows[eid] = edits[eid]

    def add(rhs):
        nonlocal max_id
        max_id += 1
        appended.append(f"#{max_id} = {rhs};\n")
        return max_id

    styled = {}
    for eid, kind in kinds.items():
        if kind == "STYLED_ITEM":
            styled.setdefault(refs(rows[eid])[-1], []).append(eid)

    def colors(eid, seen=None):
        seen = set() if seen is None else seen
        if eid in seen or kinds.get(eid) not in STYLES:
            return []
        seen.add(eid)
        if kinds[eid] == "COLOUR_RGB":
            return [rgb_of(rows[eid])]
        return [rgb for ref in refs(rows[eid]) for rgb in colors(ref, seen)]

    products = {}
    for eid, kind in kinds.items():
        if kind == "PRODUCT":
            match = re.match(r"PRODUCT\('((?:[^']|'')*)'", rows[eid])
            if match:
                color = petgf_color(match[1].replace("''", "'"))
                if color:
                    products[eid] = (match[1], color)
    formations = {eid: products.get(refs(rows[eid])[-1]) for eid, kind in kinds.items() if kind == "PRODUCT_DEFINITION_FORMATION"}
    definitions = {eid: formations.get(refs(rows[eid])[0]) for eid, kind in kinds.items() if kind == "PRODUCT_DEFINITION"}
    shapes = {eid: definitions.get(refs(rows[eid])[-1]) for eid, kind in kinds.items() if kind == "PRODUCT_DEFINITION_SHAPE"}
    representations = {}
    linked = {}
    for eid, kind in kinds.items():
        if kind == "SHAPE_REPRESENTATION_RELATIONSHIP":
            a, b = refs(rows[eid])[-2:]
            linked.setdefault(a, []).append(b)
            linked.setdefault(b, []).append(a)
        if kind == "SHAPE_DEFINITION_REPRESENTATION":
            a, b = refs(rows[eid])
            if shapes.get(a):
                representations[b] = shapes[a]

    style_for, checked = {}, {}
    def style(rgb):
        if rgb not in style_for:
            col = add(f"COLOUR_RGB('',{','.join(format(c, '.12g') for c in rgb)})")
            fill = add(f"FILL_AREA_STYLE_COLOUR('',#{col})")
            area = add(f"FILL_AREA_STYLE('',(#{fill}))")
            surface = add(f"SURFACE_STYLE_FILL_AREA(#{area})")
            side = add(f"SURFACE_SIDE_STYLE('',(#{surface}))")
            use = add(f"SURFACE_STYLE_USAGE(.BOTH.,#{side})")
            style_for[rgb] = add(f"PRESENTATION_STYLE_ASSIGNMENT((#{use}))")
        return style_for[rgb]

    for rep, (name, color) in representations.items():
        wanted = color.toTuple()[:3]
        queue, seen = [rep], set()
        while queue:
            rep = queue.pop()
            if rep in seen:
                continue
            seen.add(rep)
            queue += linked.get(rep, [])
            if kinds.get(rep) not in ("SHAPE_REPRESENTATION", "ADVANCED_BREP_SHAPE_REPRESENTATION"):
                continue
            targets = [r for r in refs(rows[rep])[:-1] if kinds.get(r) in ("MANIFOLD_SOLID_BREP", "BREP_WITH_VOIDS")]
            for target in targets:
                checked[name] = list(linear(color))
                existing = styled.get(target, [])
                if existing and all(colors(eid) and all(close(rgb, wanted) for rgb in colors(eid)) for eid in existing):
                    continue
                assignment = style(wanted)
                if existing:
                    for eid in existing:
                        edits[eid] = f"STYLED_ITEM('color',(#{assignment}),#{target})"
                else:
                    item = add(f"STYLED_ITEM('color',(#{assignment}),#{target})")
                    context = refs(rows[rep])[-1]
                    add(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(#{item}),#{context})")

    if not edits and not appended:
        return text, checked, geometry.hexdigest()
    chunks, cursor = [], 0
    for eid in sorted(edits, key=lambda i: spans[i][0]):
        start, end = spans[eid]
        chunks.extend((text[cursor:start], f"#{eid} = {edits[eid]};"))
        cursor = end
    chunks.append(text[cursor:])
    text = ''.join(chunks)
    at = text.rindex("ENDSEC;")
    text = text[:at] + ''.join(appended) + text[at:]
    after = hashlib.sha256()
    for m in RECORD.finditer(text):
        if m[2].partition("(")[0].strip() not in STYLES:
            after.update(m[0].encode())
    assert after.digest() == geometry.digest(), 'Native geometry or structure changed'
    return text, checked, geometry.hexdigest()


def payload_colors(data, src, previous_src):
    length = struct.unpack('<I', data[:4])[0]
    head, body = json.loads(data[4:4+length]), data[4+length:]
    changed = []
    for m in head['meshes']:
        color = petgf_color(m['name'])
        if color is None and legacy_black(m['color']):
            color = M_PETGF_BLACK
        if color is not None:
            wanted = list(linear(color))
            if m['color'] != wanted:
                m['color'] = wanted
                changed.append(m['name'])
    source_changed = head.get('src') == previous_src and src != previous_src
    if source_changed:
        head['src'] = src
    if not changed and not source_changed and length % 4 == 0:
        return data, changed, sha(body)
    packed = json.dumps(head, separators=(',', ':')).encode()
    packed += b' ' * (-(len(packed) + 4) % 4)
    result = struct.pack('<I', len(packed)) + packed + body
    assert result[4+len(packed):] == body, 'Viewer geometry bytes changed'
    return result, changed, sha(body)


def apply(path, write=False):
    path = Path(path)
    before = path.read_bytes()
    after, checked, geometry = step_colors(before.decode())
    after = after.encode()
    outputs = {path: after}
    payload = path.with_name(path.name+'.mesh')
    changed, arrays = [], None
    if payload.is_file():
        data, changed, arrays = payload_colors(payload.read_bytes(), sha(after), sha(before))
        outputs[payload] = data
    moved = [str(p) for p, data in outputs.items() if p.read_bytes() != data]
    if write:
        for p, data in outputs.items():
            if str(p) in moved:
                temp = p.with_name(p.name+'.material-colors.tmp')
                temp.write_bytes(data)
                temp.replace(p)
    return dict(paths=moved, petgf_members=checked, changed_viewer_members=changed,
                native_geometry_and_structure_sha256=geometry,
                viewer_geometry_sha256=arrays)


def selftest():
    import subprocess
    import tempfile
    from _cadq_export import export_assembly, import_assembly
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/'materials.step'
        assembly = cq.Assembly(name='materials')
        assembly.add(cq.Workplane('XY').box(3,4,5), name='enclosure-front-top', color=cq.Color(*linear(M_PETGF_BLACK)), loc=cq.Location((20,30,40)))
        assembly.add(cq.Workplane('XY').box(4,5,6), name='funnel-frame', loc=cq.Location((50,60,70)))
        assembly.add(cq.Workplane('XY').box(5,6,7), name='metal', color=cq.Color(.7,.72,.75))
        export_assembly(assembly, str(path))
        original = import_assembly(path)
        report = apply(path, True)
        repaired = import_assembly(path)
        for name in ('enclosure-front-top', 'funnel-frame'):
            assert close(repaired[name][1].toTuple()[:3], M_PETGF_BLACK.toTuple()[:3]), name
            assert repaired[name][0].BoundingBox().xmin == original[name][0].BoundingBox().xmin
        assert repaired['metal'][1].toTuple() == original['metal'][1].toTuple()
        assert len(report['changed_viewer_members']) == 2
        probe = """
const fs = require('fs');
const packed = fs.readFileSync(process.argv[1] + '.mesh');
const bytes = packed.buffer.slice(packed.byteOffset, packed.byteOffset + packed.byteLength);
const length = new DataView(bytes).getUint32(0, true);
const head = JSON.parse(new TextDecoder().decode(new Uint8Array(bytes, 4, length)));
for (const mesh of head.meshes) for (const key of ['pos','nrm','idx','fac']) {
  const [offset, count] = mesh[key];
  const View = key === 'pos' || key === 'nrm' ? Float32Array : Uint32Array;
  new View(bytes, 4 + length + offset, count);
}
require(process.argv[2])().then(occt => {
  const result = occt.ReadStepFile(new Uint8Array(fs.readFileSync(process.argv[1])), null);
  console.log(JSON.stringify(result.meshes.map(m => ({name:m.name, color:m.color}))));
});
"""
        parsed = subprocess.run(['node', '-e', probe, str(path),
                                 str(ROOT/'hardware/pcb/pcba/node_modules/occt-import-js')],
                                text=True, capture_output=True, check=True)
        browser_colors = {m['name']:m['color'] for m in json.loads(parsed.stdout)}
        for name in ('enclosure-front-top', 'funnel-frame'):
            assert close(browser_colors[name], linear(M_PETGF_BLACK)), (name, browser_colors)
        assert apply(path, True)['paths'] == [], 'Material application is not idempotent'
    assert petgf_color('cold-core/foam-cap-lid-top') is M_PETGF_BLACK
    assert petgf_color('tee-y-a') is None
    assert close(linear(petgf_color('nameplate-001')), linear(M_PETGF_BLACK))
    assert close(linear(petgf_color('tube-collar-water-word/1')), linear(M_PETGF_BLACK))
    print('Material color selftest passed: native styles, missing styles, shared colors, geometry, and idempotence.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--selftest', action='store_true')
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        from _solids import solids
        paths = [ROOT / p for p in solids() if p.endswith('.step') and (ROOT / p).is_file()]
    report = {}
    for path in paths:
        result = apply(path, args.write)
        if result['paths']:
            report[str(path.relative_to(ROOT))] = result
            print(f"{path.relative_to(ROOT)}: {len(result['changed_viewer_members'])} viewer material(s), presentation-only STEP repair", flush=True)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(f"PET-GF materials: {len(paths)} STEP(s) checked, {len(report)} file pair(s) {'updated' if args.write else 'need updates'}.", flush=True)
    return int(bool(report) and args.check)


if __name__ == '__main__':
    sys.exit(main())
