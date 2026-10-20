"""Scoped STEP solid replacement without reserializing unrelated geometry.

The named products, styles, component relations and placements remain in the
original document. Only their MANIFOLD_SOLID_BREP records point to new geometry;
all original records outside those roots are retained byte for byte.
"""
import re
import tempfile
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.TopLoc import TopLoc_Location

RECORD = re.compile(r'^#(\d+)\s*=(.*?);[ \t]*\n', re.M | re.S)
REF = re.compile(r'#(\d+)')


def records(text):
    return {int(m[1]): m for m in RECORD.finditer(text)}


def refs(body):
    return [int(i) for i in REF.findall(body)]


def patch(path, mapped, palette):
    text = Path(path).read_text()
    original = records(text)
    next_id = max(original) + 1
    replacements, added, roots = {}, [], {}

    def kind(number, typename):
        return original[number][2].strip().startswith(typename + '(')

    def parent(number, typename):
        hits = [n for n, record in original.items()
                if kind(n, typename) and number in refs(record[2])]
        assert len(hits) == 1, (number, typename, hits)
        return hits[0]

    for name, shape in mapped.items():
        products = [n for n, record in original.items()
                    if record[2].strip().startswith(f"PRODUCT('{name}','")]
        assert len(products) == 1, (name, products)
        product = products[0]
        for typename in ('PRODUCT_DEFINITION_FORMATION', 'PRODUCT_DEFINITION',
                         'PRODUCT_DEFINITION_SHAPE', 'SHAPE_DEFINITION_REPRESENTATION'):
            product = parent(product, typename)
        representation = refs(original[product][2])[1]
        solids = [n for n in refs(original[representation][2]) if kind(n, 'MANIFOLD_SOLID_BREP')]
        assert len(solids) == 1, (name, solids)
        target = solids[0]
        # Bake the local shape transform into its coordinates. Original component
        # placements are retained; these aggregates place the selected members at identity.
        native = shape.wrapped
        baked = cq.Shape.cast(BRepBuilderAPI_Transform(
            native.Located(TopLoc_Location()), native.Location().Transformation(), True).Shape())
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / 'replacement.step'
            cq.exporters.export(baked, str(source_path))
            source_text = source_path.read_text()
        source = records(source_text)
        source_roots = [n for n, record in source.items()
                        if record[2].strip().startswith('MANIFOLD_SOLID_BREP(')]
        assert len(source_roots) == 1, (name, source_roots)
        root = source_roots[0]
        closure, pending = set(), [root]
        while pending:
            number = pending.pop()
            if number not in closure:
                closure.add(number)
                pending.extend(refs(source[number][2]))
        renumber = {root: target}
        for number in sorted(closure - {root}):
            renumber[number] = next_id
            next_id += 1
        for number in sorted(closure):
            body = REF.sub(lambda match: '#' + str(renumber[int(match[1])]), source[number][2])
            record = f'#{renumber[number]} ={body};\n'
            if number == root:
                replacements[target] = record
            else:
                added.append(record)
        roots[name] = target
    changed = RECORD.sub(lambda match: replacements.get(int(match[1]), match[0]), text)
    end = changed.rfind('ENDSEC;')
    assert end > 0
    changed = changed[:end] + ''.join(added) + changed[end:]
    updated = records(changed)
    assert all(updated[n][0] == record[0] for n, record in original.items() if n not in replacements)
    Path(path).write_text(changed)
    return {name: [1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0.] for name in roots}
