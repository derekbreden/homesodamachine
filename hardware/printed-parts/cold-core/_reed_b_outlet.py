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
    shoulder = top + 0.25
    peak = shoulder + 2.0 * half
    return {
        'axis_xy_mm': (axis, y),
        'front_x_mm': front,
        'width_mm': 2.0 * half, 'depth_mm': depth,
        'top_z_mm': top, 'bottom_z_mm': bottom,
        'roof_shoulder_z_mm': shoulder, 'roof_peak_z_mm': peak,
        'notch_min_mm': (front - 1.0, y - half, bottom),
        'notch_max_mm': (axis, y + half, peak),
    }


def apply(shell):
    """Open the dry channel through a self-supporting peaked side window."""
    import cadquery as cq
    d = datums()
    lo, hi = d['notch_min_mm'], d['notch_max_mm']
    plane = cq.Plane(origin=(lo[0], 0., 0.), xDir=(0., 1., 0.), normal=(1., 0., 0.))
    shoulder = d['roof_shoulder_z_mm']
    profile = [(lo[1], lo[2]), (hi[1], lo[2]), (hi[1], shoulder),
               (d['axis_xy_mm'][1], d['roof_peak_z_mm']), (lo[1], shoulder)]
    opening = cq.Workplane(plane).polyline(profile).close().extrude(hi[0]-lo[0]).val()
    return shell.cut(opening)
