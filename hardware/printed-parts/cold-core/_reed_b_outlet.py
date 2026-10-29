"""Reservoir B cable's open, cap-covered outlet at the shell rim."""
import importlib

width = 10.0
depth = 6.0


def datums():
    """Shell-native millimetres; the existing reed cavity remains behind the mouth."""
    core = importlib.import_module('_cold_core_interface')
    front = -core.outer_shell_x_length / 2.0
    axis = -core.reed_column_axis_x
    inner = -core.reed_channel_inner_x
    y = core.level_rod_y
    top = core.foam_shell_outer_height
    bottom = top - depth
    wall = core.wall_thickness
    cavity_front = inner - core.reed_x_depth
    return {
        'axis_xy_mm': (axis, y),
        'front_x_mm': front,
        'width_mm': width, 'depth_mm': depth,
        'top_z_mm': top, 'bottom_z_mm': bottom,
        'neck_min_mm': (front, y - width / 2.0 - wall, bottom - wall),
        'neck_max_mm': (inner, y + width / 2.0 + wall, top),
        'cavity_min_mm': (cavity_front, y - core.reed_y_half_w,
                          bottom - wall - 0.1),
        'cavity_max_mm': (inner, y + core.reed_y_half_w, top + 0.1),
        'notch_min_mm': (front - 1.0, y - width / 2.0, bottom),
        'notch_max_mm': (inner, y + width / 2.0, top + 0.6),
        'throat_xy_mm': ((front - 1.0, y - width / 2.0),
                         (cavity_front, y - width / 2.0),
                         (inner, y - core.reed_y_half_w),
                         (inner, y + core.reed_y_half_w),
                         (cavity_front, y + width / 2.0),
                         (front - 1.0, y + width / 2.0)),
        'lower_blend_z_mm': bottom - wall - 2.0,
        'existing_outer_y_mm': (y - core.reed_y_half_w - wall,
                                y + core.reed_y_half_w + wall),
    }


def apply(shell):
    """A broad dry neck, open upward; the unchanged cap floor closes its roof."""
    import cadquery as cq
    d = datums()

    def box(lo, hi):
        return cq.Solid.makeBox(*(b - a for a, b in zip(lo, hi)), cq.Vector(*lo))

    neck = box(d['neck_min_mm'], d['neck_max_mm'])
    # Grow the two 1 mm flank extensions at 0.5 mm per build millimetre,
    # so their undersides join the existing channel without horizontal lips.
    front, inner = d['neck_min_mm'][0], d['neck_max_mm'][0]
    base = d['neck_min_mm'][2]
    for existing, outer in zip(d['existing_outer_y_mm'],
                               (d['neck_min_mm'][1], d['neck_max_mm'][1])):
        blend = (cq.Workplane('YZ')
                 .polyline(((existing, d['lower_blend_z_mm']),
                            (existing, base), (outer, base))).close()
                 .extrude(inner - front).translate((front, 0, 0)).val())
        neck = neck.fuse(blend)
    cavity = box(d['cavity_min_mm'], d['cavity_max_mm'])
    # The full-width mouth crosses the skin, then meets the 8 mm dry
    # channel with two continuous walls instead of 1 mm end shoulders.
    notch = (cq.Workplane('XY').workplane(offset=d['bottom_z_mm'])
             .polyline(d['throat_xy_mm']).close()
             .extrude(d['depth_mm'] + 0.6).val())
    return shell.union(neck).cut(cavity).cut(notch)
