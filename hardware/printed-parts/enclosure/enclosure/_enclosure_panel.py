"""Enclosure-private numeric construction for the structural back-bottom panel.

The native seam helpers keep ownership of their stations. This module records their
simple solid operations; Rust builds the solids and releases each intermediate after
its last use. Native builders and their cached geometry remain available to callers.
"""

from contextlib import contextmanager
from functools import cache
from pathlib import Path
import sys
import _enclosure_structure


class _Shape:
    def __init__(self, graph, index, bounds=None):
        self.graph, self.index, self.bounds = graph, index, bounds

    def _boolean(self, op, others):
        nodes = [self, *others]
        if op == 'cut' and self.bounds is not None:
            nodes = [self, *(other for other in others if other.bounds is None or
                       all(self.bounds[2*k] < other.bounds[2*k+1] and
                           other.bounds[2*k] < self.bounds[2*k+1] for k in range(3)))]
        if len(nodes) == 1:
            return self
        bounds = self.bounds
        if op == 'union':
            bounds = (tuple(v for k in range(3) for v in
                      (min(n.bounds[2*k] for n in nodes),
                       max(n.bounds[2*k+1] for n in nodes)))
                      if all(n.bounds is not None for n in nodes) else None)
        elif op == 'intersect' and all(n.bounds is not None for n in nodes):
            bounds = tuple(v for k in range(3) for v in
                           (max(n.bounds[2*k] for n in nodes),
                            min(n.bounds[2*k+1] for n in nodes)))
        return self.graph.add(op, [n.index for n in nodes], bounds=bounds)

    def fuse(self, *others, **_kwargs):
        return self._boolean('union', others)

    def cut(self, *others, **_kwargs):
        return self._boolean('cut', others)

    def intersect(self, *others, **_kwargs):
        return self._boolean('intersect', others)

    def translate(self, delta):
        bounds = (tuple(v + delta[k] for k in range(3)
                        for v in self.bounds[2*k:2*k+2]) if self.bounds is not None else None)
        return self.graph.add('translate', [self.index], delta=delta, bounds=bounds)

    def rotate(self, origin, end, angle):
        import math
        from itertools import product
        axis = [b-a for a, b in zip(origin, end)]
        length = math.sqrt(sum(a*a for a in axis))
        axis = [a/length for a in axis]
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        def point(p):
            q = [a-b for a, b in zip(p, origin)]
            cross = (axis[1]*q[2]-axis[2]*q[1], axis[2]*q[0]-axis[0]*q[2],
                     axis[0]*q[1]-axis[1]*q[0])
            dot = sum(a*b for a, b in zip(axis, q))
            return [origin[k]+c*q[k]+s*cross[k]+(1-c)*dot*axis[k] for k in range(3)]
        corners = ([point(p) for p in product(*(self.bounds[2*k:2*k+2] for k in range(3)))]
                   if self.bounds is not None else None)
        bounds = (tuple(v for k in range(3) for v in
                        (min(p[k] for p in corners), max(p[k] for p in corners)))
                  if corners is not None else None)
        return self.graph.add('rotate', [self.index], origin=origin, end=end,
                              angle=angle, bounds=bounds)

    def mirror(self, plane):
        axis = {'YZ': 0, 'XZ': 1, 'XY': 2}[plane]
        bounds = list(self.bounds) if self.bounds is not None else None
        if bounds is not None:
            bounds[2*axis:2*axis+2] = [-bounds[2*axis+1], -bounds[2*axis]]
        return self.graph.add('mirror', [self.index], axis=axis, bounds=bounds)

    def clean(self):
        return self

    def val(self):
        return self

    def BoundingBox(self):
        from types import SimpleNamespace
        if self.bounds is None:
            raise ValueError('this private feature has no conservative numeric bounds')
        return SimpleNamespace(**{key: self.bounds[2*k+i]
            for k, axis in enumerate('xyz') for i, key in enumerate((axis+'min',axis+'max'))})

    def Solids(self):
        return [self]


class _Graph:
    def __init__(self):
        self.nodes = []

    def add(self, op, inputs=(), *, bounds=None, **numbers):
        index = len(self.nodes)
        frame = sys._getframe(1)
        source = frame
        while frame is not None:
            if Path(frame.f_code.co_filename).name == 'enclosure.py':
                source = frame
                break
            frame = frame.f_back
        path = Path(source.f_code.co_filename).resolve()
        root = next(p for p in path.parents if (p/'hardware/scripts').is_dir())
        self.nodes.append(dict(op=op, inputs=list(inputs),
                               source=dict(path=path.relative_to(root).as_posix(), line=source.f_lineno),
                               **numbers))
        return _Shape(self, index, bounds)

    def box(self, *bounds):
        return self.add('box', bounds=bounds, box=bounds)

    def cylinder(self, axis, radius, a, b, lo, hi):
        other = [k for k in range(3) if k != axis]
        bounds = [0.0]*6
        bounds[2*axis:2*axis+2] = sorted((lo, hi))
        for k, centre in zip(other, (a, b)):
            bounds[2*k:2*k+2] = [centre-radius, centre+radius]
        return self.add('cylinder', axis=axis, radius=radius, centre=(a, b),
                        span=sorted((lo, hi)), bounds=bounds)

    def prism(self, axis, lo, hi, section):
        section = tuple(section)
        other = [k for k in range(3) if k != axis]
        bounds = [0.0]*6
        bounds[2*axis:2*axis+2] = sorted((lo, hi))
        for i, k in enumerate(other):
            bounds[2*k:2*k+2] = [min(p[i] for p in section), max(p[i] for p in section)]
        return self.add('prism', axis=axis, span=sorted((lo, hi)),
                        section=section, bounds=bounds)

    def rounded(self, shape, radius):
        if radius <= 0:
            return shape
        if self.nodes[shape.index]['op'] != 'box':
            raise ValueError('the enclosure standing round belongs to rectangular stock')
        return self.add('rounded-box', box=shape.bounds, radius=radius, bounds=shape.bounds)

    def document(self, result, extras=None):
        reachable = set()
        def visit(index):
            if index in reachable:
                return
            reachable.add(index)
            for child in self.nodes[index]['inputs']:
                visit(child)
        visit(result.index)
        for shape in (extras or {}).values():
            visit(shape.index)
        order = sorted(reachable)
        remap = {old: new for new, old in enumerate(order)}
        out = dict(nodes=[dict(self.nodes[i], inputs=[remap[k] for k in self.nodes[i]['inputs']])
                          for i in order], result=remap[result.index])
        if extras:
            out['extras'] = {key:remap[shape.index] for key,shape in extras.items()}
        return out


@contextmanager
def _record(shell, graph, structure):
    """Substitute only the enclosure's private geometry leaves, then restore them."""
    def teardrop_y(radius, x, z, y0, y1, up=1.0):
        import math
        angle = math.radians(shell.teardrop_roof_angle)
        half = radius * math.sin(angle)
        tangent = z + up * radius * math.cos(angle)
        apex = z + up * radius / math.cos(angle)
        circle = graph.add('cylinder', axis=1, radius=radius, centre=(x, z),
            span=(y0, y1), stations=(up*math.pi/2-angle, up*math.pi/2+angle),
            bounds=(x-radius, x+radius, y0, y1, z-radius, z+radius))
        return circle.fuse(graph.prism(1, y0, y1,
            ((x-half, tangent), (x+half, tangent), (x, apex))))

    def handhold_cutter(inner, x_ext, sx):
        bed, roof, _crown = shell._handhold_levels(inner)
        y0, y1 = shell._handhold_y()
        _flank, cap = shell._band_x(x_ext, sx)
        xa, xb = sorted((cap-sx*shell.handhold_wall, x_ext-sx))
        bounds = (xa, xb, y0, y1, bed-1.0, roof)
        return graph.add('handhold-cutter', box=bounds, radius=shell.handhold_corner_r,
                         bounds=bounds)

    @cache
    def handhold_finish(inner):
        bed, roof, crown = shell._handhold_levels(inner)
        y0, y1 = shell._handhold_y()
        depth = shell.wall+shell.y_stack_low_depth
        end = shell.handhold_corner_r+shell.handhold_edge_r+shell.handhold_wall
        return graph.add('handhold-finish-air', bed=bed, roof=roof, crown=crown,
                         y=[y0, y1], depth=depth, corner=shell.handhold_corner_r,
                         radius=shell.handhold_edge_r, end_stock=end,
                         cutter_depth=depth-shell.handhold_wall,
                         slope=_enclosure_structure.OUTWARD_PER_HEIGHT,
                         bounds=(0.0, depth, y0-end, y1+end, bed, crown))

    from _disposal_artwork import numbers as warning_artwork
    replacements = {
        '_ybox': graph.box,
        '_xcyl': lambda r, y, z, x0, x1: graph.cylinder(0, r, y, z, x0, x1),
        '_ycyl': lambda r, x, z, y0, y1: graph.cylinder(1, r, x, z, y0, y1),
        '_teardrop_y': teardrop_y,
        '_zcyl': lambda r, x, y, z0, z1: graph.cylinder(2, r, x, y, z0, z1),
        '_yz_prism': lambda x0, x1, section: graph.prism(0, x0, x1, section),
        '_xz_prism': lambda y0, y1, section: graph.prism(1, y0, y1, section),
        '_xy_prism': lambda z0, z1, section: graph.prism(2, z0, z1, section),
        '_round_z': graph.rounded,
        '_rounded_outer': lambda outer: structure,
        '_handhold_cutter': handhold_cutter,
        '_handhold_finish_air': handhold_finish,
        'disposal_letters': lambda outer: graph.add('disposal-letters',
            outer=outer, lines=shell.disposal_lines, family=shell.disposal_font,
            artwork=warning_artwork(shell.disposal_font, shell.disposal_kind),
            cap_height=shell.disposal_cap_height, depth=shell.disposal_raise+shell.disposal_embed,
            embed=shell.disposal_embed, line_gap=shell.disposal_line_gap,
            bottom=shell.disposal_bottom),
        '_unified': lambda shape: shape,
    }
    originals = {name: getattr(shell, name) for name in replacements}
    for name, replacement in replacements.items():
        setattr(shell, name, replacement)
    try:
        yield
    finally:
        for name, original in originals.items():
            setattr(shell, name, original)


def numbers(shell, box):
    """Record the complete current back-bottom construction, with its live seam numbers."""
    graph = _Graph()
    structure_numbers = _enclosure_structure.numbers(box.outer)
    structure = graph.add('silhouette', bounds=box.outer)
    with _record(shell, graph, structure):
        # The lower half starts below the display/funnel storeys. Refuse a new
        # overlap until that additional feature has an explicit Rust construction.
        top = box.splits[1]
        if structure_numbers['profile']['foot'][1] <= top:
            raise ValueError('the display keepout reaches the structural back-bottom boundary')
        if shell.housing_back_y(box.outer) >= box.y_joint:
            raise ValueError('the display keepout reaches the back column')
        if box.pack.funnel:
            seat = shell.funnel_seat_z(box.outer)
            lower = seat-shell._funnel.drop-shell._funnel_frame_part.web-shell.funnel_collar_air-1.0
            if lower <= top:
                raise ValueError('the funnel clearance reaches the structural back-bottom boundary')
        o = box.outer
        half = structure.cut(shell._cavity(box.inner)).intersect(
            graph.box(o[0], o[1], box.y_joint, o[3], o[4], top))
        half = half.cut(shell._floor_tongue(box.inner, box.y_joint)[1])
        for ports, cutter in ((box.pack.back_ports, shell._port_cuts),
                              (box.pack.west_ports, shell._x_port_cuts)):
            selected = [p for p in ports if p[2] <= top]
            if cutter is shell._port_cuts:
                cuts = cutter(selected, box.inner[3]-5.0, o[3]+5.0)
            else:
                cuts = cutter(selected, o[0]-5.0, box.inner[0]+5.0)
            for air in cuts:
                half = half.cut(air)
        result = shell.build_piece(box, 'back', 'bottom', halves_cache={'back': half})
    from _materials import linear
    return dict(structure_numbers, color=linear(shell.PIECE_COLORS['back-bottom']),
                panel=graph.document(result))


def print_numbers(shell, box):
    """The complete back-bottom print recipe, including the exterior field's live phase.

    Other rear plain lands are above this panel. Read their exact pure bounds and
    a conservative bound on the receiver pad before excluding them from its rail.
    The warning land is calculated in Rust from the raked glyphs it actually built.
    """
    import _enclosure_skin
    identification = shell._above_core_shell.rear_identification()
    station = identification.nameplate_station()
    wing = identification.nameplate.wing_interface
    plan = identification.nameplate_plan()
    # apply()'s pad extends ph/2 to each side, plus one end margin. This wider
    # whole-height bound contains it while the accepted run-out/end margins each
    # remain within half the body height. Cutting the pad cannot enlarge that bound.
    runout = max(2.0, wing.FLOOR_STOCK+wing.RUNOUT_LEAD)
    end_margin = shell.wall+shell.fits.supported_surface
    if max(runout, end_margin) > wing.HEIGHT/2:
        raise ValueError('the receiver pad exceeds the back-bottom disjoint bound')
    pad_floor = station.z-wing.HEIGHT-2*wing.FACE_SLIP
    other = [*identification.rail_bounds(),
             *wing.plain_lips(station, plan['face_y_mm']),
             shell._above_core_shell.keystone_land()]
    if box.pack.nameplate:
        other.extend(shell._nameplate_fit.plain_lips(box.pack.nameplate, box.outer[3]))
    if box.pack.keystone:
        other.extend(shell._data_fit.plain_lips(box.pack.keystone, box.outer[3]))
    panel_top = max(box.splits[1]+shell.z_rise, shell._handhold_levels(box.inner)[2])
    if min(pad_floor, *(land[4] for land in other)) <= panel_top:
        raise ValueError('a rear plain land reaches the back-bottom print boundary')
    rail = shell._flute_skin.Rail(at=lambda s: shell.plan_at(s, box.outer),
                                  length=shell.plan_perimeter(box.outer))
    out = numbers(shell, box)
    out.update(_enclosure_skin.field_numbers([rail], shell.flute_pitch(box.outer),
                                             shell.flute_depth, shell.flute_rise))
    out['print'] = {'warning_margin': shell.disposal_margin,
                    'warning_raise': shell.disposal_raise, 'wall': shell.wall}
    out['disjoint_lands'] = {'panel_top': panel_top, 'receiver_pad_floor': pad_floor,
                              'other_bounds': other}
    return out


def cut(shell, box, directory):
    """Write one native-free back-bottom part through the installed engine and print payload."""
    import _rust_part
    from _enclosure_presentation import print_payload
    said = _rust_part.cut('enclosure-shell', 'enclosure-panel', print_numbers(shell, box),
                          directory)
    step = Path(directory)/'enclosure-back-bottom.step'
    print_payload(step, check_print=True)
    return said
