"""Reservoir B cable's fore side outlet below the shell rim."""
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
        'notch_max_mm': (axis, y + half, top + 0.25),
    }


def apply(shell):
    """Open the fore wall into the dry channel; the raised channel mouth stays open above."""
    import cadquery as cq
    d = datums()
    lo, hi = d['notch_min_mm'], d['notch_max_mm']
    return shell.cut(cq.Solid.makeBox(*(b - a for a, b in zip(lo, hi)), cq.Vector(*lo)))
