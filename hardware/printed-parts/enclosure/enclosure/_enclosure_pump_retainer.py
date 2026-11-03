"""Live numeric construction of the relaxed and installed lower pump retainer."""
from contextlib import contextmanager
from pathlib import Path


def _stack(graph, case, start, steps, profiles):
    collapsed = 4*(case.arc_segments+1)+2
    split = collapsed+2
    at = 2*(case.arc_segments+1)
    def aligned(profile):
        profile = list(profile)
        if len(profile) == split:
            return profile
        if len(profile) != collapsed:
            raise ValueError('the native pump skirt has an unknown correspondence')
        return profile[:at+1]+[profile[at]]+profile[at+1:]+[profile[-1]]
    z = start
    sections = [[(case.center_x+x, case.center_y+y, z) for x,y in aligned(profiles[0])]]
    for dz, profile in zip(steps, profiles[1:]):
        z += dz
        sections.append([(case.center_x+x, case.center_y+y, z) for x,y in aligned(profile)])
    points = [p for section in sections for p in section]
    bounds = tuple(v for axis in range(3) for v in
                   (min(p[axis] for p in points), max(p[axis] for p in points)))
    return graph.add('ruled-stack', sections=sections, bounds=bounds)


def _profile_prism(graph, case, profile, z0, z1):
    return graph.prism(2, z0, z1,
                       [(case.center_x+x, case.center_y+y) for x,y in profile])


def _case_drop_well(graph, case, air):
    offset = case.skirt_wall-air
    skirt = _stack(graph, case, 0.0, case.skirt_z_steps, case._skirt_profile_set(offset))
    lower = _stack(graph, case, case.skirt_bottom_z, case.lower_z_steps(),
                   case._lower_profile_set(offset))
    solid = skirt.fuse(lower)
    for z, profile in zip(case._stack_levels(), case._stack_profiles(offset)):
        if z < -1e-9:
            solid = solid.fuse(_profile_prism(graph, case, profile, z, 0.0))
    return solid


def _lower_well(shell, graph, pump_trays):
    tray, case = shell._tray, shell._tray._pc
    air = shell.cap_pump_air
    support = shell.pump_skirt_support_z(pump_trays)-min(z for _x,_y,z in pump_trays)
    offset = case.skirt_wall-air
    upper, lower = case._skirt_profile_set(offset)[1], case._skirt_profile_set(offset)[3]
    bottom = case.lower_cap_top_z-case.overcut

    def mask(z0,z1,y0,y1):
        return graph.box(case.center_x-case.cutter_half_extent,
                         case.center_x+case.cutter_half_extent,
                         case.center_y+y0,case.center_y+y1,z0,z1)

    lower_room = _case_drop_well(graph,case,air).intersect(
        _profile_prism(graph,case,lower,bottom,support)).intersect(
            mask(bottom,support,*tray.skirt_body_open_y_bounds))
    upper_room = _profile_prism(graph,case,upper,support,0.0).fuse(
        _profile_prism(graph,case,lower,support,0.0)).intersect(
            mask(support,0.0,-case.cutter_half_extent,tray.skirt_open_y_max))
    room = upper_room.fuse(lower_room).translate((-case.center_x,-case.center_y,0.0))
    body_half,y0,open_half,_ = tray.outlet_fore_miter(air)
    if open_half > body_half+1e-9:
        y1,z0 = body_half,tray.outlet_axis_z
        room = room.fuse(graph.box(-open_half,-body_half,y0,y1,z0,0.0),
                         graph.box(body_half,open_half,y0,y1,z0,0.0))
    return room


def _wing(shell, graph, box, side, spread):
    profile = shell._fixed_pump_mount.wing_profile(shell,box,side,spread)
    points = [p for segment in profile['segments'] for controls in segment.values()
              for p in controls]
    bounds = (min(p[0] for p in points),max(p[0] for p in points),
              *profile['span'],min(p[1] for p in points),max(p[1] for p in points))
    return graph.add('bezier-prism',axis=1,**profile,bounds=bounds)


@contextmanager
def _leaves(shell, graph):
    fixed = shell._fixed_pump_mount
    original_well, original_wing = shell._pump_lower_well, fixed._wing
    shell._pump_lower_well = lambda trays: _lower_well(shell,graph,trays)
    fixed._wing = lambda e,box,side,spread: _wing(e,graph,box,side,spread)
    try:
        yield
    finally:
        shell._pump_lower_well, fixed._wing = original_well, original_wing


def numbers(shell, box, *, seated=False):
    """The same retained wells and wing profiles as the native retainer builder."""
    from _enclosure_panel import _Graph, _record
    from _materials import linear
    graph = _Graph()
    with _record(shell,graph,None), _leaves(shell,graph):
        result = shell.build_pump_retainer(box,seated=seated)
    return {'panel':graph.document(result), 'color':linear(shell.PIECE_COLORS['pump-retainer']),
            'name':'enclosure-pump-retainer-seated' if seated else 'enclosure-pump-retainer',
            'seated':seated}


def cut(shell, box, directory, *, seated=False):
    """Write one retainer pose through the installed part engine."""
    import _rust_part
    directory = Path(directory)
    said = _rust_part.cut('enclosure-shell','enclosure-pump-retainer',
                          numbers(shell,box,seated=seated),directory,
                          numbers_name='enclosure-pump-retainer-seated' if seated else None)
    if not seated:
        from _enclosure_presentation import print_payload
        step = directory/'enclosure-pump-retainer.step'
        print_payload(step, check_print=False)
    return said
