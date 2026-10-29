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
        'walls_min_mm': (front, y - width / 2.0 - wall, 0.0),
        'walls_max_mm': (inner, y + width / 2.0 + wall, top),
        'cavity_min_mm': (cavity_front, y - core.reed_y_half_w,
                          core.wall_and_floor_thickness),
        'cavity_max_mm': (inner, y + core.reed_y_half_w, top + 0.1),
        'notch_min_mm': (front - 1.0, y - width / 2.0, bottom),
        'notch_max_mm': (cavity_front, y + width / 2.0, top + 0.6),
    }


def apply(shell):
    """B's channel walls stand one wall outside the notch for the shell's full height, so the
    notch is a plain slot from the dry channel out through the fore face, open upward; the
    unchanged cap floor closes its roof."""
    import cadquery as cq
    d = datums()

    def box(lo, hi):
        return cq.Solid.makeBox(*(b - a for a, b in zip(lo, hi)), cq.Vector(*lo))

    walls = box(d['walls_min_mm'], d['walls_max_mm'])
    cavity = box(d['cavity_min_mm'], d['cavity_max_mm'])
    notch = box(d['notch_min_mm'], d['notch_max_mm'])
    return shell.union(walls).cut(cavity).cut(notch)
