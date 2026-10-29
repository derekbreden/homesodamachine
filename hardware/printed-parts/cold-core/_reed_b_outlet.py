"""Reservoir B cable's open, cap-covered outlet at the shell rim."""
import importlib

depth = 6.0


def datums():
    """Shell-native millimetres; the existing reed cavity remains behind the mouth."""
    core = importlib.import_module('_cold_core_interface')
    front = -core.outer_shell_x_length / 2.0
    axis = -core.reed_column_axis_x
    y = core.level_rod_y
    half = core.reed_y_half_w
    top = core.foam_shell_outer_height
    bottom = top - depth
    return {
        'axis_xy_mm': (axis, y),
        'front_x_mm': front,
        'width_mm': 2.0 * half, 'depth_mm': depth,
        'top_z_mm': top, 'bottom_z_mm': bottom,
        'notch_min_mm': (front - 1.0, y - half, bottom),
        'notch_max_mm': (axis, y + half, top + 0.6),
    }


def apply(shell):
    """The dry channel's top `depth`, opened through the fore face at the channel's own width:
    the notch's sides are the channel's sides and its walls are the channel's walls. Open
    upward; the unchanged cap floor closes its roof."""
    import cadquery as cq
    d = datums()
    lo, hi = d['notch_min_mm'], d['notch_max_mm']
    return shell.cut(cq.Solid.makeBox(*(b - a for a, b in zip(lo, hi)), cq.Vector(*lo)))
