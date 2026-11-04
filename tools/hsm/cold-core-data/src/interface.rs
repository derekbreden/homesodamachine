//! Casing stock, mating extents, clamp stack and source-frame port datums.

use anyhow::Result;
use serde_json::{Value, json};

pub fn base(fits: &Value) -> Result<Value> {
    let running = super::number(fits, "running")?;
    let slip = super::number(fits, "slip")?;
    let m5_thread_pass_dia = super::number(fits, "m5_thread_pass_dia")?;
    let supported_surface = super::number(fits, "supported_surface")?;
    let stock = super::stock();
    let carbonator_outer_radius = stock["carbonator_outer_radius"].as_f64().unwrap();
    let carbonator_height = stock["carbonator_height"].as_f64().unwrap();
    let wall_thickness = 2.38;
    let floor_thickness = 2.;
    let wall_and_floor_thickness = floor_thickness;
    let hole_shift_from_edge = 15.;
    let outer_shell_wall = wall_thickness;
    let coil_radial_clearance = 7.;
    let carbonator_coil_envelope_radius = carbonator_outer_radius + coil_radial_clearance;
    let pocket_centerward_arc_outer_radius = 80.5;
    let foam_thickness_around_cylinder =
        pocket_centerward_arc_outer_radius - wall_thickness - carbonator_outer_radius;
    let below_carbonator_elbows_height = 30.;
    let above_carbonator_elbows_height = 30.;
    let foam_shell_outer_height =
        carbonator_height + below_carbonator_elbows_height + above_carbonator_elbows_height + 1.;
    let carbonator_support_ring_height = 30.;
    let support_ring_radial_width = 9.;
    let passage_tube_od = 6.5;
    let port_hole_radius = passage_tube_od / 2. + 0.5;
    let reed_x_depth = 6.;
    let reed_y_half_w = 4.;
    let level_rod_y = 32.5;
    let bag_pocket_far_inner_x = 129.5;
    let bag_pocket_y_inner_max = 70.5;
    let bag_pocket_width = 2. * (bag_pocket_y_inner_max + wall_thickness);
    let bag_pocket_depth =
        bag_pocket_far_inner_x - pocket_centerward_arc_outer_radius + 2. * wall_thickness;
    let bag_pocket_floor_top_z = floor_thickness;
    let bag_pocket_walls_top_z = foam_shell_outer_height;
    let reed_channel_inner_x = 131.5;
    let reed_column_axis_x = reed_channel_inner_x + reed_x_depth / 2.;
    let reservoir_clearance = running;
    let bag_pocket_corner_inner_radius = 6. + reservoir_clearance;
    let reservoir_floor_thickness = 3.;
    let reservoir_fill_port = json!({"-1": [-90.5, 43.5], "1": [102.5, -61.]});
    let reservoir_fill_sides = [-1, 1];
    let reservoir_draw_port = json!({"-1": [-94.3, 6.], "1": [84.2, -45.]});
    let casing_foil_allowance = 0.30;
    let casing_foil_land = 13.;
    let outer_shell_x_length = 282.4;
    let outer_shell_y_length = 180.4;
    let seam_channel_land = 1.;
    let seam_channel_width = 2. * (port_hole_radius + seam_channel_land);
    let seam_channel_depth = 1.5;
    let bag_pocket_outermost_x = bag_pocket_far_inner_x + wall_thickness;
    let outer_shell_foam_gap = outer_shell_y_length / 2. - outer_shell_wall - bag_pocket_width / 2.;
    let forward_band_width = outer_shell_x_length / 2. - outer_shell_wall - bag_pocket_outermost_x;
    let forward_band_mid_x = bag_pocket_outermost_x + forward_band_width / 2.;
    let pour_band_pocket_side_y = -(bag_pocket_width / 2.);
    let pour_band_shell_side_y = -(outer_shell_y_length / 2. - outer_shell_wall);
    let foam_cap_interior_height = 16.;
    let foam_cap_height = foam_cap_interior_height + wall_and_floor_thickness;
    let foam_cap_lid_pour_radius = 10.;
    let foam_cap_lid_vent_radius = 3.;
    let foam_cap_lid_hole_inset = 30.;
    let top_lid_pour_xy = [outer_shell_x_length / 2. - foam_cap_lid_hole_inset, -73.];
    let top_lid_vent_setback = 2.5;
    let carbonator_port_offset = 0.750 * 25.4;
    let carbonator_sensor_azimuth = -90.;
    let carbonator_sensor_axis = [0., -1.];
    let carbonator_float_top_stop_height = 4.;
    let carbonator_float_top_stop_diameter = 9.5;
    let co2_inlet_y = -carbonator_port_offset;
    let co2_inlet_tube_radius = port_hole_radius;
    let water_inlet_port_y = -carbonator_port_offset;
    let prv_port_y = carbonator_port_offset;
    let cap_shell_clearance = slip;
    let cap_lid_clearance = slip;
    let screw_clearance_radius = m5_thread_pass_dia / 2.;
    let insert_pocket_radius = 3.2;
    let insert_pocket_depth = 10.5;
    let screw_boss_size = 11.6;
    let screw_guard_diameter = screw_boss_size;
    let screw_head_height = 5.;
    let head_seat_recess = slip;
    let head_cbore_radius = 4.5;
    let head_cbore_depth = screw_head_height + head_seat_recess;
    let head_pad_height = head_cbore_depth + supported_surface;
    let head_pad_slip = slip;
    let foam_cap_lid_height = wall_and_floor_thickness + head_pad_height;
    let top_lid_bottom_z = foam_shell_outer_height + foam_cap_height - head_pad_height;
    let foam_shell_rim_z = top_lid_bottom_z - cap_lid_clearance;
    let bottom_cap_height = foam_cap_height + wall_and_floor_thickness - cap_shell_clearance;
    let bottom_pour_radius = 15.;
    let bottom_pour_positions: Vec<_> = [-75., 75.]
        .iter()
        .flat_map(|x| [-40., 40.].map(|y| [*x, y]))
        .collect();
    let front_wall_x = -141.5;
    let port_lane_outer_y = -82.5;
    let port_lane_inner_y = -72.5;
    let port_lane_mid_y = (port_lane_outer_y + port_lane_inner_y) / 2.;
    let west_lane_mid_y = -port_lane_mid_y;
    let evap_tail_low_z =
        hole_shift_from_edge + wall_and_floor_thickness + below_carbonator_elbows_height;
    let evap_tail_high_z = foam_shell_outer_height
        - hole_shift_from_edge
        - wall_and_floor_thickness
        - above_carbonator_elbows_height;
    let corner_round_radius = 11.7;
    let boss_wall_y = 84.4;
    let boss_wall_x = 135.4;
    let mid_screw_x_offset = 45.;
    let mut attachment_stations: Vec<([f64; 2], &str)> = vec![];
    for x in [-boss_wall_x, boss_wall_x] {
        for y in [-60., 0., 60.] {
            attachment_stations.push(([x, y], "x"));
        }
    }
    for x in [45., 110.] {
        for y in [-boss_wall_y, boss_wall_y] {
            attachment_stations.push(([x, y], "y"));
        }
    }
    let attachment_xy_positions: Vec<_> = attachment_stations.iter().map(|row| row.0).collect();
    let lid_attachment_stations: Vec<_> = attachment_stations
        .iter()
        .map(|(xy, wall)| ([-xy[0], -xy[1]], *wall))
        .collect();
    let lid_attachment_xy_positions: Vec<_> =
        lid_attachment_stations.iter().map(|row| row.0).collect();
    let cap_screw_length = 100.;
    let insert_length = 9.5;
    let cap_screw_beyond_face =
        cap_screw_length - (wall_and_floor_thickness + (foam_cap_height - head_pad_height));
    let top_lid_screw_beyond_face =
        cap_screw_length - (foam_cap_lid_height - head_cbore_depth + cap_lid_clearance);
    let cap_screw_tip_air = 2.5;
    let bottom_screw_bore_depth = cap_screw_beyond_face + cap_screw_tip_air;
    let top_screw_bore_depth = top_lid_screw_beyond_face + cap_screw_tip_air;
    let deck_mount_boss_radius = 5.;
    let deck_mount_bore_radius = 2.;
    let deck_mount_lid_slip = slip;
    let deck_mount_insert_length = 5.7;
    let deck_mount_bore_relief = 1.;
    let deck_mount_cap_gap = 1.5;
    let f = super::formatted;
    let states = json!([
        [
            "forward-band-takes-a-bore",
            "The forward band still passes a line",
            format!(
                "{} >= {} mm",
                f(forward_band_width, "g"),
                f(passage_tube_od, "g")
            ),
            forward_band_width >= passage_tube_od,
            format!(
                "the open routing band is {} mm wide for the {} mm measured tube; enlarged bores cross printed walls and caps",
                f(forward_band_width, "g"),
                f(passage_tube_od, "g")
            )
        ],
        [
            "cap-screw-reach",
            "The clamp screw reaches the whole of its insert",
            format!("{} mm past the shell face", f(insert_length, "g")),
            cap_screw_beyond_face >= insert_length,
            format!(
                "an M5 × {} reaches {} mm past the shell face, short of its {} mm insert",
                f(cap_screw_length, "g"),
                f(cap_screw_beyond_face, "g"),
                f(insert_length, "g")
            )
        ],
        [
            "cap-screw-bottom",
            "The clamp screw pulls its head down before it bottoms",
            format!(
                "{} mm past the shell face at most",
                f(bottom_screw_bore_depth, "g")
            ),
            cap_screw_beyond_face <= bottom_screw_bore_depth,
            format!(
                "an M5 × {} reaches {} mm past the shell face and bottoms in a {} mm tail passage before its head is down",
                f(cap_screw_length, "g"),
                f(cap_screw_beyond_face, "g"),
                f(bottom_screw_bore_depth, "g")
            )
        ]
    ]);
    Ok(json!({
        "wall_thickness": wall_thickness, "floor_thickness": floor_thickness,
        "wall_and_floor_thickness": wall_and_floor_thickness, "hole_shift_from_edge": hole_shift_from_edge,
        "outer_shell_wall": outer_shell_wall, "coil_radial_clearance": coil_radial_clearance,
        "carbonator_coil_envelope_radius": carbonator_coil_envelope_radius,
        "pocket_centerward_arc_outer_radius": pocket_centerward_arc_outer_radius,
        "foam_thickness_around_cylinder": foam_thickness_around_cylinder,
        "below_carbonator_elbows_height": below_carbonator_elbows_height,
        "above_carbonator_elbows_height": above_carbonator_elbows_height,
        "foam_shell_outer_height": foam_shell_outer_height,
        "carbonator_support_ring_height": carbonator_support_ring_height,
        "support_ring_radial_width": support_ring_radial_width,
        "passage_tube_od": passage_tube_od, "port_hole_radius": port_hole_radius,
        "reed_x_depth": reed_x_depth, "reed_y_half_w": reed_y_half_w, "level_rod_y": level_rod_y,
        "bag_pocket_far_inner_x": bag_pocket_far_inner_x, "bag_pocket_y_inner_max": bag_pocket_y_inner_max,
        "bag_pocket_width": bag_pocket_width, "bag_pocket_depth": bag_pocket_depth,
        "bag_pocket_floor_top_z": bag_pocket_floor_top_z, "bag_pocket_walls_top_z": bag_pocket_walls_top_z,
        "reed_channel_inner_x": reed_channel_inner_x, "reed_column_axis_x": reed_column_axis_x,
        "reservoir_clearance": reservoir_clearance, "bag_pocket_corner_inner_radius": bag_pocket_corner_inner_radius,
        "reservoir_floor_thickness": reservoir_floor_thickness,
        "reservoir_fill_port": reservoir_fill_port, "reservoir_fill_sides": reservoir_fill_sides,
        "reservoir_draw_port": reservoir_draw_port,
        "casing_foil_allowance": casing_foil_allowance, "casing_foil_land": casing_foil_land,
        "outer_shell_x_length": outer_shell_x_length, "outer_shell_y_length": outer_shell_y_length,
        "seam_channel_land": seam_channel_land, "seam_channel_width": seam_channel_width,
        "seam_channel_depth": seam_channel_depth, "bag_pocket_outermost_x": bag_pocket_outermost_x,
        "outer_shell_foam_gap": outer_shell_foam_gap, "forward_band_width": forward_band_width,
        "forward_band_mid_x": forward_band_mid_x, "pour_band_pocket_side_y": pour_band_pocket_side_y,
        "pour_band_shell_side_y": pour_band_shell_side_y, "foam_cap_interior_height": foam_cap_interior_height,
        "foam_cap_height": foam_cap_height, "foam_cap_lid_pour_radius": foam_cap_lid_pour_radius,
        "foam_cap_lid_vent_radius": foam_cap_lid_vent_radius, "foam_cap_lid_hole_inset": foam_cap_lid_hole_inset,
        "top_lid_pour_xy": top_lid_pour_xy, "top_lid_vent_setback": top_lid_vent_setback,
        "carbonator_port_offset": carbonator_port_offset, "carbonator_sensor_azimuth": carbonator_sensor_azimuth,
        "carbonator_sensor_axis": carbonator_sensor_axis,
        "carbonator_float_top_stop_height": carbonator_float_top_stop_height,
        "carbonator_float_top_stop_diameter": carbonator_float_top_stop_diameter,
        "co2_inlet_y": co2_inlet_y, "co2_inlet_tube_radius": co2_inlet_tube_radius,
        "water_inlet_port_y": water_inlet_port_y, "prv_port_y": prv_port_y,
        "cap_shell_clearance": cap_shell_clearance, "cap_lid_clearance": cap_lid_clearance,
        "screw_clearance_radius": screw_clearance_radius,
        "insert_pocket_radius": insert_pocket_radius, "insert_pocket_depth": insert_pocket_depth,
        "screw_boss_size": screw_boss_size, "screw_guard_diameter": screw_guard_diameter,
        "screw_head_height": screw_head_height, "head_seat_recess": head_seat_recess,
        "head_cbore_radius": head_cbore_radius, "head_cbore_depth": head_cbore_depth,
        "head_pad_height": head_pad_height, "head_pad_slip": head_pad_slip,
        "foam_cap_lid_height": foam_cap_lid_height, "top_lid_bottom_z": top_lid_bottom_z,
        "foam_shell_rim_z": foam_shell_rim_z, "bottom_cap_height": bottom_cap_height,
        "bottom_pour_radius": bottom_pour_radius, "bottom_pour_positions": bottom_pour_positions,
        "front_wall_x": front_wall_x, "port_lane_outer_y": port_lane_outer_y,
        "port_lane_inner_y": port_lane_inner_y, "port_lane_mid_y": port_lane_mid_y,
        "west_lane_mid_y": west_lane_mid_y, "evap_tail_low_z": evap_tail_low_z,
        "evap_tail_high_z": evap_tail_high_z, "corner_round_radius": corner_round_radius,
        "_boss_wall_y": boss_wall_y, "_boss_wall_x": boss_wall_x,
        "mid_screw_x_offset": mid_screw_x_offset, "attachment_stations": attachment_stations,
        "attachment_xy_positions": attachment_xy_positions,
        "lid_attachment_stations": lid_attachment_stations,
        "lid_attachment_xy_positions": lid_attachment_xy_positions,
        "cap_screw_length": cap_screw_length, "insert_length": insert_length,
        "cap_screw_beyond_face": cap_screw_beyond_face,
        "top_lid_screw_beyond_face": top_lid_screw_beyond_face,
        "cap_screw_tip_air": cap_screw_tip_air, "bottom_screw_bore_depth": bottom_screw_bore_depth,
        "top_screw_bore_depth": top_screw_bore_depth,
        "deck_mount_boss_radius": deck_mount_boss_radius, "deck_mount_bore_radius": deck_mount_bore_radius,
        "deck_mount_lid_slip": deck_mount_lid_slip, "deck_mount_insert_length": deck_mount_insert_length,
        "deck_mount_bore_relief": deck_mount_bore_relief, "deck_mount_cap_gap": deck_mount_cap_gap,
        "_states": states
    }))
}
