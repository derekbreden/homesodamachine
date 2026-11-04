"""Raw provider and object-type adapters for enclosure Rust calculations."""
from _enclosure_data import read


def tupled(value):
    if isinstance(value, list):
        return tuple(tupled(item) for item in value)
    if isinstance(value, dict):
        return {name: tupled(item) for name, item in value.items()}
    return value


def namespace(interface, fits, swept, funnel, funnel_frame, wago, mq6, tray, layout):
    interface_names = (
        'boss_ligament', 'ceiling_skin', 'display_bezel_depth', 'display_bezel_slope',
        'display_bezel_x', 'display_corner_r', 'display_cover_slip', 'display_cover_thickness',
        'display_inset_depth', 'display_inset_lap', 'display_inset_reach', 'display_inset_slope',
        'display_inset_x', 'flute_depth', 'flute_full_depth_height', 'flute_rise',
        'funnel_collar_air', 'head_cbore_dia', 'heatset_depth', 'heatset_dia', 'heatset_len',
        'heatset_long_len', 'mount_bore_relief', 'mount_boss_dia', 'pump_station_drop',
        'pump_station_lead', 'rear_plane_y', 'rear_seam_clear', 'relief_chamfer',
        'screw_clear_dia', 'show_corner_r', 'show_edge_r', 'slide_slip', 'wall',
        'y_stack_high_depth', 'z_seam',
    )
    return tupled(read('core-namespace',
        interface={name: getattr(interface, name) for name in interface_names},
        fits={name: getattr(fits, name) for name in ('m5_thread_pass_dia', 'running', 'slip')},
        swept={name: getattr(swept, name) for name in ('ANGLE', 'FLAT', 'FUNNEL_SEAT')},
        funnel={name: getattr(funnel, name) for name in ('brim_thickness', 'collar_d')},
        funnel_frame={'center_y': funnel_frame.center_y},
        mq6={name: getattr(mq6, name) for name in ('CAN_D', 'PCB_T', 'PCB_X', 'PCB_Y')},
        tray={'shaft_w': tray.shaft_w},
        wago={'SIZES': wago.SIZES, 'lever_swing': wago.lever_swing},
        clearance_sliding_floor=fits.clearance(sliding=True, at_floor=True),
        c14_pose=layout.pose('c14-inlet'), layout_spec=layout.specification()))


def wago(op, provider, size, wall=None, press=None):
    return tupled(read('core-wago-' + op,
        wago={'SIZES': provider.SIZES, 'lever_swing': provider.lever_swing},
        size=size, wall=wall, press=press))
