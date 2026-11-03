"""Live front-bottom construction and its independent exterior print field."""
from pathlib import Path


def _vents(shell, graph, solid, inner, outer, airway, y0, y1, z0, z1):
    if not airway:
        return solid
    ay0, ay1, az0, az1 = airway
    if not (y0 <= (ay0+ay1)/2 <= y1 and z0 <= (az0+az1)/2 <= z1):
        return solid
    courses = shell.vent_segments(airway)
    band = shell.vent_band(airway)
    half = shell.reeding.pierce_width/2
    columns, cutters = [], []
    for side, y in shell.vent_grooves(outer, airway):
        face = shell.vent_flank_face(side)
        xa, xb = sorted((face-side*shell.cond_vent_probe, face-side*shell.stated_bound_tol))
        indices = []
        for lo, hi in courses:
            indices.append(len(cutters))
            cutters.append(shell._vent_cutter(outer,side,y,lo,hi))
        columns.append({'side':side, 'probe':(xa,xb,
            y-half-shell.cond_vent_clear,y+half+shell.cond_vent_clear,
            band[0]-shell.cond_vent_clear,band[1]+shell.cond_vent_clear),
            'cutters':indices})
    return graph.add('flank-vents',[solid.index,*[shape.index for shape in cutters]],
        columns=columns,courses=courses,clearance=shell.cond_vent_clear,
        tolerance=shell.stated_bound_tol,island_min=shell.cond_vent_island_min,
        bounds=solid.bounds)


def numbers(shell, box):
    from _enclosure_panel import _Graph, _record
    from _enclosure_front_top import _front_half, _leaves
    from _enclosure_back_top import _replace
    import _enclosure_structure
    from _materials import linear
    graph = _Graph()
    graph.extras = {}
    structure = graph.add('silhouette',bounds=box.outer)
    with _record(shell,graph,structure), _leaves(shell,graph,box), _replace(shell,{
            '_flank_vents':lambda solid,*args:_vents(shell,graph,solid,*args)}):
        half = _front_half(shell,graph,box,structure)
        result = shell.build_piece(box,'front','bottom',halves_cache={'front':half})
    return dict(_enclosure_structure.numbers(box.outer),
                color=linear(shell.PIECE_COLORS['front-bottom']),
                panel=graph.document(result,graph.extras),panel_bounds=result.bounds)


def print_numbers(shell, box):
    """Read the existing rail's live field and plain lands without native geometry."""
    import _enclosure_skin
    identification = shell._above_core_shell.rear_identification()
    station = identification.nameplate_station()
    plan = identification.nameplate_plan()
    wing = identification.nameplate.wing_interface
    plain = (shell.disposal_field(box.outer),
             *wing.plain_lips(station,plan['face_y_mm']),
             *identification.rail_bounds(),shell._above_core_shell.keystone_land())
    if box.pack.nameplate:
        plain += shell._nameplate_fit.plain_lips(box.pack.nameplate,box.outer[3])
    if box.pack.keystone:
        plain += shell._data_fit.plain_lips(box.pack.keystone,box.outer[3])
    out = numbers(shell,box)
    import above_core as layout
    rear = layout.specification()['rear_wall']['rear_wall']['ymax']
    reach = max(shell.flute_rise,_enclosure_skin.reeding.flute_width)+shell._flute_skin.face_tol
    bounds = out['panel_bounds']
    if bounds is None or bounds[3]+reach >= rear-3.0:
        raise ValueError('the rear receiver land reaches the front-bottom print boundary')
    rail = shell._flute_skin.Rail(at=lambda s:shell.plan_at(s,box.outer),
                                  length=shell.plan_perimeter(box.outer),plain=plain)
    out.update(_enclosure_skin.field_numbers([rail],shell.flute_pitch(box.outer),
                                             shell.flute_depth,shell.flute_rise))
    out['disjoint_receiver_land'] = {'front_panel_ymax_mm':bounds[3],
                                    'field_reach_mm':reach,'rear_land_ymin_mm':rear-3.0}
    return out


def cut(shell, box, directory):
    """Write the fine structure and separately fluted print without another panel."""
    import _rust_part
    import trimesh
    from _enclosure_presentation import print_payload
    said = _rust_part.cut('enclosure-shell','enclosure-front-bottom',
                          print_numbers(shell,box),directory)
    step = Path(directory)/'enclosure-front-bottom.step'
    printed = trimesh.load_mesh(step.with_suffix('.stl'))
    loose = shell._flute_skin.non_manifold_edges(printed)
    if loose or not printed.is_watertight:
        raise ValueError(f'{step.with_suffix(".stl").name}: {loose} non-manifold edges, '
                         f'watertight={printed.is_watertight}')
    print_payload(step,printed)
    return said
