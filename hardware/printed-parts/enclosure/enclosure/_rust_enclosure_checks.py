"""Enclosure fit/readings on fine model references, without Python CAD objects.

The enclosure's scalar station functions supply numeric tool recipes. Rust owns
their geometry and all model, volume, face and connected-component readings. The
existing report functions consume those readings, keeping their labels, units,
limits and document variables in one place with the mechanical dimensions.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager, redirect_stdout
import hashlib
import io
import json
import math
from pathlib import Path
from types import SimpleNamespace

from _enclosure_panel import _Graph, _Shape, _record


class _Vector:
    """The numeric vector operations used by the enclosure's report formatting."""

    def __init__(self, *coordinates):
        self.xyz = tuple(coordinates[0]) if len(coordinates) == 1 else tuple(coordinates)
        self.x, self.y, self.z = self.xyz

    def __iter__(self):
        return iter(self.xyz)

    def __getitem__(self, index):
        return self.xyz[index]

    def __add__(self, other):
        return _Vector(*(a+b for a, b in zip(self, other)))

    def __sub__(self, other):
        return _Vector(*(a-b for a, b in zip(self, other)))

    def dot(self, other):
        return sum(a*b for a, b in zip(self, other))

    @property
    def Length(self):
        return math.sqrt(self.dot(self))


def _bounds(lower, upper):
    lower, upper = lower or (0., 0., 0.), upper or (0., 0., 0.)
    row = {axis+suffix: values[k] for k, axis in enumerate('xyz')
           for suffix, values in (('min', lower), ('max', upper))}
    row.update({axis+'len': upper[k]-lower[k] for k, axis in enumerate('xyz')})
    row['center'] = _Vector(*((a+b)/2 for a, b in zip(lower, upper)))
    return SimpleNamespace(**row)


class _ScalarFace:
    def __init__(self, row):
        self.row = row

    def Area(self):
        return self.row['area']

    def Center(self):
        return _Vector(*self.row['centre'])

    def normalAt(self):
        return _Vector(*self.row['normal'])

    def BoundingBox(self):
        return _bounds(self.row['min'], self.row['max'])

    def geomType(self):
        return self.row['kind']


class _ScalarComponent:
    def __init__(self, row):
        self.row = row

    def BoundingBox(self):
        return _bounds(self.row['min'], self.row['max'])

    def Volume(self):
        return self.row['volume_mm3']


class _ReadingShape(_Shape):
    """A recipe index and scalar replies; it holds no triangles or CAD backend."""

    def translate(self, delta):
        return super().translate(tuple(delta))

    def Volume(self):
        return self.graph.reading(self)['volume_mm3']

    def BoundingBox(self):
        if self is self.graph.extras.get('receiver_field') and self.bounds is not None:
            # This box only sizes the exterior clip around the receiver tool. Its
            # conservative construction extents enclose that tool in either phase.
            return _bounds(self.bounds[::2], self.bounds[1::2])
        row = self.graph.reading(self)
        if self.graph.answers is None and self.bounds is not None:
            return _bounds(self.bounds[::2], self.bounds[1::2])
        return _bounds(row['min'], row['max'])

    def Solids(self):
        row = self.graph.reading(self, components=True, valid=True)
        return [_ScalarComponent(part) for part in row.get('components', ())]

    def isValid(self):
        return self.graph.reading(self, valid=True).get('valid', True)

    def Faces(self):
        rows = self.graph.reading(self, kind='faces')
        return [_ScalarFace(row) for row in rows]


class _Questions(_Graph):
    def __init__(self, answers=None):
        super().__init__()
        self.answers = answers
        self.queries = {}
        self.extras = {}

    def add(self, op, inputs=(), *, bounds=None, **numbers):
        if op == 'empty':
            bounds = (0.,)*6
        shape = super().add(op, inputs, bounds=bounds, **numbers)
        return _ReadingShape(self, shape.index, shape.bounds)

    def model(self, value):
        if isinstance(value, (list, tuple)):
            parts = [self.model(reference) for reference in value]
            return parts[0].fuse(*parts[1:]) if parts else self.add('empty')
        reference = ({'model': str(Path(value).resolve())}
                     if isinstance(value, (str, Path)) else dict(value))
        reference['model'] = str(Path(reference['model']).resolve())
        return self.add('model', reference=reference)

    def identity(self, index):
        keys = []
        for node in self.nodes[:index+1]:
            row = {key: value for key, value in node.items() if key not in ('inputs', 'source')}
            row['inputs'] = [keys[k] for k in node['inputs']]
            keys.append(hashlib.sha256(json.dumps(row, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest())
        return keys[index]

    def reading(self, shape, *, kind='stats', components=False, valid=False):
        key = self.identity(shape.index) + ':' + kind
        if self.answers is not None:
            if key not in self.answers:
                raise ValueError('an enclosure report asked an unmeasured question: '+key)
            row = self.answers[key]
            if components and 'components' not in row:
                raise ValueError('an enclosure report asked unmeasured components: '+key)
            return row
        query = self.queries.setdefault(key, dict(key=key, node=shape.index, kind=kind))
        if components:
            query['components'] = True
        if valid:
            query['valid'] = True
        return [] if kind == 'faces' else {'volume_mm3': 0., 'min': None, 'max': None,
                                           'components': [], 'valid': True}

    def document(self):
        # Every question is a root. Unasked helper fields are not part of the program.
        needed = set()
        def visit(k):
            if k in needed:
                return
            needed.add(k)
            for child in self.nodes[k]['inputs']:
                visit(child)
        for question in self.queries.values():
            visit(question['node'])
        order = sorted(needed)
        remap = {old: new for new, old in enumerate(order)}
        return dict(nodes=[dict(self.nodes[k], inputs=[remap[i] for i in self.nodes[k]['inputs']])
                           for k in order],
                    queries=[dict(row, node=remap[row['node']]) for row in self.queries.values()])


@contextmanager
def _numeric(shell, graph, box=None):
    """Use the same mechanical station recipes, replacing their geometry leaves."""
    original_cq = shell.cq
    shell.cq = SimpleNamespace(Vector=_Vector)
    try:
        with ExitStack() as stack:
            stack.enter_context(_record(shell, graph, None))
            if box is not None:
                import _enclosure_back_top
                stack.enter_context(_enclosure_back_top._leaves(shell, graph, box))
            yield
    finally:
        shell.cq = original_cq


def _measure(graph):
    import _rust_part
    return _rust_part.check('enclosure-shell', 'enclosure-checks', graph.document())['answers']


def check_rows(bounds):
    """The existing enclosure rows in the whole-machine scorecard's scalar form."""
    return [dict(id=row.id, label=row.label, kind='gate',
                 status='pass' if row.ok else 'fail', value=row.value,
                 target=row.target, detail=row.detail, active=True) for row in bounds]


def _piece_reports(shell, box, models, installed_retainer, core, graph):
    pieces = {name: graph.model(model) for name, model in models.items()}
    seated = graph.model(installed_retainer) if installed_retainer is not None else None
    cold_core = graph.model(core) if core is not None else None
    collected = []
    original_record = shell.record_bound
    def record(row):
        collected.append(row)
        if graph.answers is not None:
            return original_record(row)
        return row
    shell.record_bound = record
    try:
        with _numeric(shell, graph, box):
            disconnected = []
            for name, piece in pieces.items():
                count = len(piece.Solids())
                valid = piece.isValid()
                if count != 1 or not valid:
                    disconnected.append(f'{name}: {count} solids')
            record(shell.Bound('connected-pieces',
                'Each printed enclosure piece is one valid connected solid',
                not disconnected, '; '.join(disconnected) if disconnected else
                f'{len(pieces)} connected pieces', 'one valid solid per printed piece', disconnected))
            if 'back-top' in pieces:
                shell._ceiling_show_cap_bound(pieces['back-top'], box)
            if 'front-bottom' in pieces and 'back-bottom' in pieces:
                shell._handhold_bound(pieces, box)
            shell._silhouette_bound(pieces, box)
            try:
                slides = shell._report_slide(pieces, box)
            except ValueError as error:
                if graph.answers is not None or not str(error).startswith(
                        'the back Z-slide catch is not two broad horizontal bearing planes:'):
                    raise
                # Both existing face questions are registered before the scalar
                # bearing limit can be evaluated from the measured faces.
                slides = {}
            if 'front-top' in pieces:
                shell._report_facet(pieces['front-top'], box)
            shell._report_split(pieces, cold_core, box, installed_retainer=seated)
            vents = shell.vent_readings(pieces, box)
    finally:
        shell.record_bound = original_record
    piece_bounds = {}
    if graph.answers is not None:
        for name, piece in pieces.items():
            row = graph.reading(piece)
            piece_bounds[name] = [*row['min'], *row['max']]
    return dict(bounds=collected, checks=check_rows(collected), slides=slides, vents=vents,
                piece_bounds=piece_bounds)


def check_pieces(shell, box, models, installed_retainer=None, core=None):
    """All current inline enclosure questions in one Rust invocation.

    ``models`` is ordered piece name -> fine NPZ path/instance specification. A
    logical body can also name an ordered list of instance specifications. The
    installed retainer is explicit; the relaxed print is not substituted for it.
    Existing scalar decisions and report text run after the answers arrive.
    """
    if 'pump-retainer' in models and installed_retainer is None:
        raise ValueError('enclosure checks need the explicit installed retainer model')
    graph = _Questions()
    with redirect_stdout(io.StringIO()):
        _piece_reports(shell, box, models, installed_retainer, core, graph)
    answers = _measure(graph)
    return _piece_reports(shell, box, models, installed_retainer, core, _Questions(answers))


def box_readings(shell, pack, bounds, references):
    """The complete Box lip/floor/under-wall/pillar questions from fine selections."""
    def ask(graph):
        with _numeric(shell, graph):
            tools, questions = shell.box_question_tools(pack, bounds)
            bodies = {name: graph.model(references[name]) for name in pack.placed}
            tables = {family: {} for family in ('floor', 'under', 'pillars')}
            tables['lip'] = {'front': {}, 'back': {}}
            for question in questions:
                tool = tools[question['tool']]
                raw = {'volume_mm3': 0., 'min': None, 'max': None}
                if question['positive_components']:
                    raw['components'] = []
                overlaps = tool is not None
                if overlaps and tool.bounds is not None:
                    lower, upper = bounds[question['body']]
                    overlaps = all(upper[k] > tool.bounds[2*k]
                                   and tool.bounds[2*k+1] > lower[k] for k in range(3))
                if overlaps:
                    reference = references[question['body']]
                    instances = reference if isinstance(reference, (list, tuple)) else [reference]
                    sections = [dict(ref, indices=[i]) for ref in instances
                                for i in ref.get('indices', ())]
                    if question['body_first'] and len(sections) > 1:
                        # A native compound section is the ordered body sections, not a
                        # union that can remove a body's own internal overlap reading.
                        hits = [graph.model(ref).intersect(tool) for ref in sections]
                        hit = graph.add('compose', [shape.index for shape in hits])
                    else:
                        body = bodies[question['body']]
                        hit = body.intersect(tool) if question['body_first'] else tool.intersect(body)
                    raw = graph.reading(hit, components=question['positive_components'])
                    raw = {key: value for key, value in raw.items() if key != 'valid'}
                family, key = question['family'], question['key']
                if family == 'lip':
                    tables[family][key[0]][key[1]] = raw
                else:
                    tables[family][tuple(key)] = raw
            return shell.BoxReadings(dict(bounds), tables['lip'], tables['floor'],
                                     tables['under'], tables['pillars'])
    graph = _Questions()
    ask(graph)
    return ask(_Questions(_measure(graph)))
