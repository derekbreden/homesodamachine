//! The faucet shell's authored scalar dimensions, in millimetres.
#![allow(unused_parens)]
use serde::Serialize;
#[derive(Clone, Serialize)]
#[allow(non_snake_case)]
pub struct Dimensions {
    pub above_counter_gasket_thickness: f64,
    pub above_counter_plate_thickness: f64,
    pub flavor_tube_od: f64,
    pub flavor_tube_x_offset: f64,
    pub flavor_tube_hole_dia: f64,
    pub pill_length_x: f64,
    pub pill_width_y: f64,
    pub flavor_tube_depth: f64,
    pub display_housing_width: f64,
    pub display_housing_length: f64,
    pub display_pcb_width: f64,
    pub display_pcb_length: f64,
    pub display_corner_r: f64,
    pub display_pcb_corner_r: f64,
    pub display_total_depth: f64,
    pub display_pcb_top_z: f64,
    pub display_cover_slip: f64,
    pub display_cover_lap: f64,
    pub display_cover_over_face: f64,
    pub shell_center_x: f64,
    pub shell_center_y: f64,
    pub zone1_z_bottom: f64,
    pub zone1_z_top: f64,
    pub zone1_height: f64,
    pub bore_clearance: f64,
    pub westbrass_bore_diameter: f64,
    pub westbrass_bore_x: f64,
    pub westbrass_bore_y: f64,
    pub flavor_pill_center: Vec<f64>,
    pub flavor_pill_y_minus_edge: f64,
    pub wall_thickness_min: f64,
    pub show_wall: f64,
    pub print_layer_height: f64,
    pub print_bead_width: f64,
    pub _westbrass_bore_farthest_from_shell_center: f64,
    pub _pill_farthest_from_shell_center: f64,
    pub shell_outer_r: f64,
    pub zone2_z_bottom: f64,
    pub zone2_z_top: f64,
    pub zone2_height: f64,
    pub westbrass_rect_long_y: f64,
    pub westbrass_rect_short_x: f64,
    pub westbrass_bore_rect_long_y: f64,
    pub westbrass_bore_rect_short_x: f64,
    pub cove_r: f64,
    pub zone2_bore_z_bottom: f64,
    pub shell_outer_lip: f64,
    pub zone1_outer_z_top: f64,
    pub zone2_outer_z_bottom: f64,
    pub foot_width: f64,
    pub foot_depth: f64,
    pub foot_center_y: f64,
    pub base_pod_counterbore_dia: f64,
    pub base_pod_shank_dia: f64,
    pub base_pod_wall: f64,
    pub base_pod_center_x: f64,
    pub base_pod_center_y: f64,
    pub base_pod_front_center_x: f64,
    pub base_pod_front_center_y: f64,
    pub base_pod_centers: Vec<Vec<f64>>,
    pub base_pod_z_bottom: f64,
    pub base_pod_insert_dia: f64,
    pub base_insert_outer_dia: f64,
    pub base_insert_length: f64,
    pub base_pedestal_dia: f64,
    pub base_pedestal_height: f64,
    pub base_pedestal_chamfer: f64,
    pub base_pod_hole_dia: f64,
    pub base_pod_hole_depth: f64,
    pub base_insert_bottom_z: f64,
    pub base_pod_insert_depth: f64,
    pub base_pod_z_top: f64,
    pub base_pod_radius: f64,
    pub base_screw_length: f64,
    pub base_screw_head_height: f64,
    pub base_screw_head_recess: f64,
    pub base_screw_counterbore_depth: f64,
    pub base_screw_seat_z: f64,
    pub base_plate_seat_thickness: f64,
    pub lever_x_half: f64,
    pub lever_fit_clearance: f64,
    pub lever_sweep_allowance: f64,
    pub lever_insertion_front_y: f64,
    pub lever_rest_back_y: f64,
    pub lever_clearance_x_half: f64,
    pub lever_clearance_y_back: f64,
    pub lever_rest_top_z: f64,
    pub shell_rect_y_half: f64,
    pub shell_rect_x_half: f64,
    pub shell_rect_y_width: f64,
    pub shell_rect_x_width: f64,
    pub shell_rect_y_max: f64,
    pub shell_rect_y_min: f64,
    pub zone3_z_bottom: f64,
    pub arch_z_base: f64,
    pub arch_z_peak: f64,
    pub westbrass_arch_inner_x: f64,
    pub westbrass_arch_outer_x: f64,
    pub shell_arch_bore_inner_x: f64,
    pub shell_arch_bore_outer_x: f64,
    pub shell_arch_bore_z_foot_top: f64,
    pub shell_arch_bore_z_peak: f64,
    pub shell_arch_z_foot_top: f64,
    pub shell_arch_z_peak: f64,
    pub wing_inner_x: f64,
    pub wing_outer_x: f64,
    pub soda_faucet_tube_y: f64,
    pub soda_faucet_tube_od: f64,
    pub soda_faucet_hole_diameter: f64,
    pub flavor_tube_post_bend_y: f64,
    pub flavor_bend_min_radius: f64,
    pub flavor_bend_radius: f64,
    pub flavor_bend_start_z: f64,
    pub flavor_bend_angle_rad: f64,
    pub fill_y_min: f64,
    pub zone4_z_bottom: f64,
    pub zone4_z_top: f64,
    pub zone4_height: f64,
    pub zone5_z_bottom: f64,
    pub zone5_z_top: f64,
    pub zone5_height: f64,
    pub flavor_offset_y_from_water: f64,
    pub split_socket_wall: f64,
    pub split_plug_wall: f64,
    pub split_slip: f64,
    pub zone5_wall: f64,
    pub signal_lane_width: f64,
    pub signal_lane_depth: f64,
    pub signal_lane_center_n: f64,
    pub signal_ribbon_max_width: f64,
    pub signal_ribbon_max_depth: f64,
    pub _tube_soda_bore_r: f64,
    pub _tube_pill_bore_r: f64,
    pub _tube_pill_cap_x: f64,
    pub _tube_bore_caps: Vec<Vec<f64>>,
    pub tube_shell_center_y: f64,
    pub tube_shell_bore_radius: f64,
    pub tube_shell_outer_r: f64,
    pub tube_shell_soda_r_outer: f64,
    pub tube_shell_pill_x_half_outer: f64,
    pub tube_shell_x_half_outer: f64,
    pub tube_shell_x_outer: f64,
    pub display_neck_outer_r: f64,
    pub _neck_plug_min_wall: f64,
    pub gn_bend1_sweep_rad: f64,
    pub gn_bend2_sweep_rad: f64,
    pub gn_mid_straight_len: f64,
    pub gn_tip_straight_len: f64,
    pub gn_outlet_y: f64,
    pub gn_outlet_z: f64,
    pub _path_total_rot: f64,
    pub gn_bend1_r: f64,
    pub gn_bend2_r: f64,
    pub gn_bend1_z_start: f64,
    pub gn_bend1_z_mid: f64,
    pub split_junction_rot: f64,
    pub split_socket_overlap_len: f64,
    pub split_plug_overlap_len: f64,
    pub split_socket_shrink: f64,
    pub split_plug_shrink: f64,
    pub split_socket_angle_rad: f64,
    pub split_plug_angle_rad: f64,
    pub _path_socket_start_rot: f64,
    pub _path_socket_mid_rot: f64,
    pub _path_plug_start_rot: f64,
    pub _path_plug_mid_rot: f64,
    pub _tan_after_bend1: Vec<f64>,
    pub _tan_after_bend2: Vec<f64>,
    pub _tan_at_junction: Vec<f64>,
    pub _tan_at_socket_start: Vec<f64>,
    pub _tan_at_plug_start: Vec<f64>,
    pub _path_z_lift: f64,
    pub _path_p2: Vec<f64>,
    pub _path_p3: Vec<f64>,
    pub _path_center_bend2: Vec<f64>,
    pub _path_junction: Vec<f64>,
    pub _path_socket_start: Vec<f64>,
    pub _path_socket_mid: Vec<f64>,
    pub _path_plug_start: Vec<f64>,
    pub _path_plug_mid: Vec<f64>,
    pub _path_p4: Vec<f64>,
    pub _path_p5: Vec<f64>,
    pub split_normal: Vec<f64>,
    pub split_junction_y: f64,
    pub split_junction_z: f64,
    pub print_base_build_rot: f64,
    pub print_tip_build_rot: f64,
    pub print_base_tilt_rad: f64,
    pub print_tip_tilt_rad: f64,
    pub max_print_overhang_rad: f64,
    pub _back_arch_dy: f64,
    pub back_arch_center_z: f64,
    pub back_arch_r: f64,
    pub _back_arch_a_low: f64,
    pub _back_arch_a_mid: f64,
    pub back_arch_mid_y: f64,
    pub back_arch_mid_z: f64,
    pub _z5_y_min: f64,
    pub _z5_y_max: f64,
    pub zone45_front_y: f64,
    pub zone45_z_top: f64,
    pub zone45_z_bottom_at_front: f64,
    pub _a_front: f64,
    pub _a_high: f64,
    pub _a_mid45: f64,
    pub zone45_bot_mid_y: f64,
    pub zone45_bot_mid_z: f64,
    pub lower_outer_sections: Vec<Vec<f64>>,
    pub lower_neck_z: f64,
    pub neck_land_overrun: f64,
    pub signal_lower_exit_x: f64,
    pub signal_lower_exit_y: f64,
    pub signal_lower_exit_angle: f64,
    pub lower_signal_ribbon: (f64, f64, bool, f64),
    pub signal_lane_bottom_z: f64,
    pub bundle_land_below: f64,
    pub bundle_land_above: f64,
    pub bore_overrun: f64,
    pub beverage_lead: f64,
    pub drain_relief_lead: f64,
    pub vent_outlet_reach: f64,
    pub display_usb_reference_file: String,
    pub display_usb_reference_url: String,
    pub display_usb_reference_sha256: String,
    pub display_usb_reference_bounds: Vec<Vec<f64>>,
    pub display_usb_half_width: f64,
    pub display_usb_y_range: Vec<f64>,
    pub display_usb_top_z: f64,
    pub dispense_face_thickness: f64,
    pub display_seat_reference_n: f64,
    pub display_additional_tube_clearance: f64,
    pub display_nominal_tube_clearance: f64,
    pub display_feet_n: f64,
    pub display_floor_n: f64,
    pub display_pocket_inset: f64,
    pub display_cradle_clearance: f64,
    pub display_wire_bend_radius: f64,
    pub display_ribbon_join_s: f64,
    pub display_ribbon_reference_start_s: f64,
    pub display_ribbon_side_x: f64,
    pub display_ribbon_side_radius: f64,
    pub display_ribbon_side_drop: f64,
    pub display_ribbon_side_lift: f64,
    pub display_ribbon_side_run_n: f64,
    pub display_ribbon_pcb_gap: f64,
    pub display_s_bottom: f64,
    pub display_s_top: f64,
    pub _display_housing_center_s: f64,
    pub display_face_n: f64,
    pub display_cosmetic_wall: f64,
    pub display_cover_top_n: f64,
    pub display_cover_bottom_n: f64,
    pub display_cover_shoulder_n: f64,
    pub display_cover_face_width: f64,
    pub display_cover_end_margin: f64,
    pub display_cover_face_length: f64,
    pub _display_cover_center_s: f64,
    pub display_cover_skirt_width: f64,
    pub display_cover_skirt_length: f64,
    pub display_cover_face_r: f64,
    pub display_cover_skirt_r: f64,
    pub display_cover_skirt_rear_s: f64,
    pub display_cover_rear_rim_s0: f64,
    pub display_cover_rear_rim_ds_dn: f64,
    pub display_head_s_min: f64,
    pub display_head_s_max: f64,
    pub display_clip_s_bottom: f64,
    pub display_clip_s_top: f64,
    pub display_clip_bottom_n: f64,
    pub display_clip_top_n: f64,
    pub display_clip_lip_radius: f64,
    pub display_clip_groove_radius: f64,
    pub display_foot_pad_width: f64,
    pub display_foot_pad_depth: f64,
    pub display_channel_half_width: f64,
    pub display_cartridge_lift_n: f64,
    pub display_cartridge_slide_s: f64,
    pub display_loading_travel_n: f64,
    pub display_foot_envelope_r: f64,
    pub display_foot_centers: Vec<Vec<f64>>,
    pub display_ribbon_terminal_y: f64,
    pub display_ribbon_terminal_s: f64,
    pub display_cover_inner_rows: Vec<Vec<f64>>,
    pub display_cover_inner_clamp: Vec<f64>,
    pub display_groove_reach: f64,
    pub display_pocket_overrun: f64,
    pub display_channel_overlap: f64,
    pub display_ribbon_top_n: f64,
    pub piece_mesh_tol: f64,
    pub piece_mesh_angle: f64,
}
impl Dimensions {
    pub fn new(slip: f64) -> Self {
        let interface = crate::interface(slip);
        let paths = crate::constants();
        let snap = crate::covers::snap();
        let above_counter_gasket_thickness: f64 = interface["above_counter_gasket_thickness"]
            .as_f64()
            .unwrap();
        let above_counter_plate_thickness: f64 =
            interface["above_counter_plate_thickness"].as_f64().unwrap();
        let flavor_tube_od: f64 = interface["flavor_tube_od"].as_f64().unwrap();
        let flavor_tube_x_offset: f64 = interface["flavor_tube_x_offset"].as_f64().unwrap();
        let flavor_tube_hole_dia: f64 = interface["flavor_tube_hole_dia"].as_f64().unwrap();
        let pill_length_x: f64 = interface["pill_length_x"].as_f64().unwrap();
        let pill_width_y: f64 = interface["pill_width_y"].as_f64().unwrap();
        let flavor_tube_depth: f64 = interface["flavor_tube_depth"].as_f64().unwrap();
        let display_housing_width: f64 = interface["display_housing_width"].as_f64().unwrap();
        let display_housing_length: f64 = interface["display_housing_length"].as_f64().unwrap();
        let display_pcb_width: f64 = interface["display_pcb_width"].as_f64().unwrap();
        let display_pcb_length: f64 = interface["display_pcb_length"].as_f64().unwrap();
        let display_corner_r: f64 = interface["display_corner_r"].as_f64().unwrap();
        let display_pcb_corner_r: f64 = interface["display_pcb_corner_r"].as_f64().unwrap();
        let display_total_depth: f64 = interface["display_total_depth"].as_f64().unwrap();
        let display_pcb_top_z: f64 = interface["display_pcb_top_z"].as_f64().unwrap();
        let display_cover_slip: f64 = interface["display_cover_slip"].as_f64().unwrap();
        let display_cover_lap: f64 = interface["display_cover_lap"].as_f64().unwrap();
        let display_cover_over_face: f64 = interface["display_cover_over_face"].as_f64().unwrap();
        let shell_center_x: f64 = 0.0;
        let shell_center_y: f64 = (3.175);
        let zone1_z_bottom: f64 = 0.0;
        let zone1_z_top: f64 = 13.0;
        let zone1_height: f64 = (zone1_z_top - zone1_z_bottom);
        let bore_clearance: f64 = 0.25;
        let westbrass_bore_diameter: f64 = (31.5 + (2.0 * bore_clearance));
        let westbrass_bore_x: f64 = 0.0;
        let westbrass_bore_y: f64 = 0.0;
        let flavor_pill_center: Vec<f64> = vec![
            interface["bundle_slot_center_x"].as_f64().unwrap(),
            (flavor_tube_depth),
        ];
        let flavor_pill_y_minus_edge: f64 = {
            let mut values = vec![
                ((flavor_tube_depth) - (pill_width_y / 2.0)),
                (((westbrass_bore_diameter / 2.0).powi(2)
                    - ({
                        let mut values = vec![
                            (interface["bundle_slot_left_x"].as_f64().unwrap()).abs(),
                            (interface["bundle_slot_right_x"].as_f64().unwrap()).abs(),
                        ];
                        values.into_iter().fold(f64::NEG_INFINITY, f64::max)
                    })
                    .powi(2))
                .sqrt()),
            ];
            values.into_iter().fold(f64::INFINITY, f64::min)
        };
        let wall_thickness_min: f64 = 2.0;
        let show_wall: f64 = 4.2;
        let print_layer_height: f64 = 0.24;
        let print_bead_width: f64 = 0.42;
        let _westbrass_bore_farthest_from_shell_center: f64 =
            ((shell_center_y - westbrass_bore_y) + (westbrass_bore_diameter / 2.0));
        let _pill_farthest_from_shell_center: f64 =
            (((interface["bundle_mount_x"].as_f64().unwrap()).abs() + flavor_tube_x_offset)
                .hypot((flavor_tube_depth - shell_center_y))
                + (pill_width_y / 2.0));
        let shell_outer_r: f64 = ({
            let mut values = vec![
                _westbrass_bore_farthest_from_shell_center,
                _pill_farthest_from_shell_center,
            ];
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        } + show_wall);
        let zone2_z_bottom: f64 = zone1_z_top;
        let zone2_z_top: f64 = 39.0;
        let zone2_height: f64 = (zone2_z_top - zone2_z_bottom);
        let westbrass_rect_long_y: f64 = 31.5;
        let westbrass_rect_short_x: f64 = 17.0;
        let westbrass_bore_rect_long_y: f64 = (westbrass_rect_long_y + (2.0 * bore_clearance));
        let westbrass_bore_rect_short_x: f64 = (westbrass_rect_short_x + (2.0 * bore_clearance));
        let cove_r: f64 = 6.0;
        let zone2_bore_z_bottom: f64 = (zone1_z_top + bore_clearance);
        let shell_outer_lip: f64 = (wall_thickness_min + bore_clearance);
        let zone1_outer_z_top: f64 = (zone1_z_top + shell_outer_lip);
        let zone2_outer_z_bottom: f64 = zone1_outer_z_top;
        let foot_width: f64 = 58.0;
        let foot_depth: f64 = 59.0;
        let foot_center_y: f64 = 0.0;
        let base_pod_counterbore_dia: f64 = 6.15;
        let base_pod_shank_dia: f64 = 3.9;
        let base_pod_wall: f64 = wall_thickness_min;
        let base_pod_center_x: f64 = 22.5;
        let base_pod_center_y: f64 = -(2.0);
        let base_pod_front_center_x: f64 = 0.0;
        let base_pod_front_center_y: f64 = -(22.3);
        let base_pod_centers: Vec<Vec<f64>> = vec![
            vec![(base_pod_center_x), base_pod_center_y],
            vec![-(base_pod_center_x), base_pod_center_y],
            vec![base_pod_front_center_x, base_pod_front_center_y],
        ];
        let base_pod_z_bottom: f64 = zone1_z_bottom;
        let base_pod_insert_dia: f64 = 4.0;
        let base_insert_outer_dia: f64 = 4.6;
        let base_insert_length: f64 = 4.0;
        let base_pedestal_dia: f64 = (base_pod_shank_dia + (2.0 * base_pod_wall));
        let base_pedestal_height: f64 = 2.2;
        let base_pedestal_chamfer: f64 = 0.4;
        let base_pod_hole_dia: f64 = (base_pedestal_dia + (2.0 * slip));
        let base_pod_hole_depth: f64 = (base_pedestal_height + 1.0);
        let base_insert_bottom_z: f64 = (base_pod_z_bottom + base_pod_hole_depth);
        let base_pod_insert_depth: f64 = (base_insert_length + 1.25);
        let base_pod_z_top: f64 = ((base_insert_bottom_z + base_pod_insert_depth) + base_pod_wall);
        let base_pod_radius: f64 = ((base_insert_outer_dia / 2.0) + base_pod_wall);
        let base_screw_length: f64 = 8.0;
        let base_screw_head_height: f64 = 3.0;
        let base_screw_head_recess: f64 = 0.2;
        let base_screw_counterbore_depth: f64 = (base_screw_head_height + base_screw_head_recess);
        let base_screw_seat_z: f64 =
            (-(above_counter_plate_thickness) + base_screw_counterbore_depth);
        let base_plate_seat_thickness: f64 = (base_pedestal_height - base_screw_seat_z);
        let lever_x_half: f64 = 6.5;
        let lever_fit_clearance: f64 = 0.35;
        let lever_sweep_allowance: f64 = 0.005;
        let lever_insertion_front_y: f64 = -(65.0);
        let lever_rest_back_y: f64 = 9.0;
        let lever_clearance_x_half: f64 = (lever_x_half + lever_fit_clearance);
        let lever_clearance_y_back: f64 =
            ((lever_rest_back_y + lever_fit_clearance) + lever_sweep_allowance);
        let lever_rest_top_z: f64 = (zone2_z_top + 13.0);
        let shell_rect_y_half: f64 = shell_outer_r;
        let shell_rect_x_half: f64 = ((westbrass_bore_rect_short_x / 2.0) + show_wall);
        let shell_rect_y_width: f64 = (2.0 * shell_rect_y_half);
        let shell_rect_x_width: f64 = (2.0 * shell_rect_x_half);
        let shell_rect_y_max: f64 = (shell_center_y + shell_rect_y_half);
        let shell_rect_y_min: f64 = (shell_center_y - shell_rect_y_half);
        let zone3_z_bottom: f64 = zone2_z_top;
        let arch_z_base: f64 = 41.0;
        let arch_z_peak: f64 = 46.0;
        let westbrass_arch_inner_x: f64 = 7.0;
        let westbrass_arch_outer_x: f64 = 8.5;
        let shell_arch_bore_inner_x: f64 = (westbrass_arch_inner_x - bore_clearance);
        let shell_arch_bore_outer_x: f64 = (westbrass_arch_outer_x + bore_clearance);
        let shell_arch_bore_z_foot_top: f64 = (arch_z_base + bore_clearance);
        let shell_arch_bore_z_peak: f64 = (arch_z_peak + bore_clearance);
        let shell_arch_z_foot_top: f64 = (arch_z_base + shell_outer_lip);
        let shell_arch_z_peak: f64 = (arch_z_peak + shell_outer_lip);
        let wing_inner_x: f64 = shell_arch_bore_inner_x;
        let wing_outer_x: f64 = shell_rect_x_half;
        let soda_faucet_tube_y: f64 = (8.875);
        let soda_faucet_tube_od: f64 = (0.375 * 25.4);
        let soda_faucet_hole_diameter: f64 = ((soda_faucet_tube_od + (2.0 * bore_clearance)) + 0.2);
        let flavor_tube_post_bend_y: f64 =
            (soda_faucet_tube_y + paths["TIGHT_FLAVOR_N"].as_f64().unwrap());
        let flavor_bend_min_radius: f64 = paths["FLAVOR_MIN_BEND"].as_f64().unwrap();
        let flavor_bend_radius: f64 = 40.0;
        let flavor_bend_start_z: f64 = paths["LOWER_START_Z"].as_f64().unwrap();
        let flavor_bend_angle_rad: f64 = (1.0
            - ((flavor_tube_depth - flavor_tube_post_bend_y) / (2.0 * flavor_bend_radius)))
            .acos();
        let fill_y_min: f64 = (10.46);
        let zone4_z_bottom: f64 = shell_arch_z_foot_top;
        let zone4_z_top: f64 = 57.5;
        let zone4_height: f64 = (zone4_z_top - zone4_z_bottom);
        let zone5_z_bottom: f64 = zone4_z_top;
        let zone5_z_top: f64 = (zone4_z_top + 10.0);
        let zone5_height: f64 = (zone5_z_top - zone5_z_bottom);
        let flavor_offset_y_from_water: f64 = (flavor_tube_post_bend_y - soda_faucet_tube_y);
        let split_socket_wall: f64 = wall_thickness_min;
        let split_plug_wall: f64 = wall_thickness_min;
        let split_slip: f64 = (2.0 * slip);
        let zone5_wall: f64 = ((split_socket_wall + (split_slip / 2.0)) + split_plug_wall);
        let signal_lane_width: f64 = 5.0;
        let signal_lane_depth: f64 = 1.8;
        let signal_lane_center_n: f64 = 11.55;
        let signal_ribbon_max_width: f64 = paths["RIBBON_WIDTH"].as_f64().unwrap();
        let signal_ribbon_max_depth: f64 = paths["RIBBON_DEPTH"].as_f64().unwrap();
        let _tube_soda_bore_r: f64 = (soda_faucet_hole_diameter / 2.0);
        let _tube_pill_bore_r: f64 = (flavor_tube_hole_dia / 2.0);
        let _tube_pill_cap_x: f64 = ((pill_length_x - pill_width_y) / 2.0);
        let _tube_bore_caps: Vec<Vec<f64>> = vec![
            vec![
                paths["TIGHT_FLAVOR_X"].as_f64().unwrap(),
                paths["TIGHT_FLAVOR_N"].as_f64().unwrap(),
                _tube_pill_bore_r,
            ],
            vec![
                0.0,
                paths["TIGHT_DRAIN_N"].as_f64().unwrap(),
                (interface["drain_tube_hole_dia"].as_f64().unwrap() / 2.0),
            ],
            vec![
                ((signal_lane_width - signal_lane_depth) / 2.0),
                paths["TIGHT_RIBBON_N"].as_f64().unwrap(),
                (signal_lane_depth / 2.0),
            ],
        ];
        let tube_shell_center_y: f64 = paths["SHELL_CENTER_N"].as_f64().unwrap();
        let tube_shell_bore_radius: f64 = {
            let mut values = vec![(tube_shell_center_y + _tube_soda_bore_r)];
            values.extend({
                let mut out1 = Vec::new();
                for row1_0 in (_tube_bore_caps.clone()).iter() {
                    let x = row1_0[0];
                    let n = row1_0[1];
                    let r = row1_0[2];
                    out1.push(((x).hypot((n - tube_shell_center_y)) + r));
                }
                out1
            });
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        };
        let tube_shell_outer_r: f64 = paths["SHELL_RADIUS"].as_f64().unwrap();
        let tube_shell_soda_r_outer: f64 = (tube_shell_outer_r - tube_shell_center_y);
        let tube_shell_pill_x_half_outer: f64 = ((pill_length_x / 2.0) + zone5_wall);
        let tube_shell_x_half_outer: f64 = tube_shell_outer_r;
        let tube_shell_x_outer: f64 = (2.0 * tube_shell_x_half_outer);
        let display_neck_outer_r: f64 = tube_shell_outer_r;
        let _neck_plug_min_wall: f64 =
            (((tube_shell_outer_r - split_socket_wall) - (split_slip / 2.0)) - {
                let mut values = vec![(tube_shell_center_y + _tube_soda_bore_r)];
                values.extend({
                    let mut out2 = Vec::new();
                    for row2_0 in (_tube_bore_caps.clone()).iter() {
                        let x = row2_0[0];
                        let y = row2_0[1];
                        let radius = row2_0[2];
                        out2.push(((x).hypot((y - tube_shell_center_y)) + radius));
                    }
                    out2
                });
                values.into_iter().fold(f64::NEG_INFINITY, f64::max)
            });
        let gn_bend1_sweep_rad: f64 = (30.0 * (std::f64::consts::PI / 180.0));
        let gn_bend2_sweep_rad: f64 = (110.0 * (std::f64::consts::PI / 180.0));
        let gn_mid_straight_len: f64 = 0.0;
        let gn_tip_straight_len: f64 = 25.0;
        let gn_outlet_y: f64 = -(133.99672200476698);
        let gn_outlet_z: f64 = 180.38874339162197;
        let _path_total_rot: f64 = (gn_bend1_sweep_rad + gn_bend2_sweep_rad);
        let gn_bend1_r: f64 = (((soda_faucet_tube_y - gn_outlet_y)
            - (gn_tip_straight_len * (_path_total_rot).sin()))
            / (1.0 - (_path_total_rot).cos()));
        let gn_bend2_r: f64 = gn_bend1_r;
        let gn_bend1_z_start: f64 = ((gn_outlet_z - (gn_bend1_r * (_path_total_rot).sin()))
            - (gn_tip_straight_len * (_path_total_rot).cos()));
        let gn_bend1_z_mid: f64 =
            (gn_bend1_z_start + (gn_bend1_r * (gn_bend1_sweep_rad / 2.0).sin()));
        let split_junction_rot: f64 = paths["JOINT_ANGLE"].as_f64().unwrap();
        let split_socket_overlap_len: f64 = 20.0;
        let split_plug_overlap_len: f64 = 18.0;
        let split_socket_shrink: f64 = split_socket_wall;
        let split_plug_shrink: f64 = (split_socket_shrink + (split_slip / 2.0));
        let split_socket_angle_rad: f64 = (split_socket_overlap_len / gn_bend2_r);
        let split_plug_angle_rad: f64 = (split_plug_overlap_len / gn_bend2_r);
        let _path_socket_start_rot: f64 = (split_junction_rot - split_socket_angle_rad);
        let _path_socket_mid_rot: f64 = (split_junction_rot - (split_socket_angle_rad / 2.0));
        let _path_plug_start_rot: f64 = (split_junction_rot - split_plug_angle_rad);
        let _path_plug_mid_rot: f64 = (split_junction_rot - (split_plug_angle_rad / 2.0));
        let _tan_after_bend1: Vec<f64> =
            vec![(gn_bend1_sweep_rad).sin(), (gn_bend1_sweep_rad).cos()];
        let _tan_after_bend2: Vec<f64> = vec![(_path_total_rot).sin(), (_path_total_rot).cos()];
        let _tan_at_junction: Vec<f64> =
            vec![(split_junction_rot).sin(), (split_junction_rot).cos()];
        let _tan_at_socket_start: Vec<f64> = vec![
            (_path_socket_start_rot).sin(),
            (_path_socket_start_rot).cos(),
        ];
        let _tan_at_plug_start: Vec<f64> =
            vec![(_path_plug_start_rot).sin(), (_path_plug_start_rot).cos()];
        let _path_z_lift: f64 = (gn_bend1_z_start - zone5_z_top);
        let _path_p2: Vec<f64> = vec![
            (gn_bend1_r * (1.0 - (gn_bend1_sweep_rad).cos())),
            (_path_z_lift + (gn_bend1_r * (gn_bend1_sweep_rad).sin())),
        ];
        let _path_p3: Vec<f64> = vec![
            ((_path_p2.clone())[0] + (gn_mid_straight_len * (_tan_after_bend1.clone())[0])),
            ((_path_p2.clone())[1] + (gn_mid_straight_len * (_tan_after_bend1.clone())[1])),
        ];
        let _path_center_bend2: Vec<f64> = vec![
            ((_path_p3.clone())[0] + (gn_bend2_r * (gn_bend1_sweep_rad).cos())),
            ((_path_p3.clone())[1] - (gn_bend2_r * (gn_bend1_sweep_rad).sin())),
        ];
        let _path_junction: Vec<f64> = vec![
            _path_center_bend2[0] - gn_bend2_r * (split_junction_rot).cos(),
            _path_center_bend2[1] + gn_bend2_r * (split_junction_rot).sin(),
        ];
        let _path_socket_start: Vec<f64> = vec![
            _path_center_bend2[0] - gn_bend2_r * (_path_socket_start_rot).cos(),
            _path_center_bend2[1] + gn_bend2_r * (_path_socket_start_rot).sin(),
        ];
        let _path_socket_mid: Vec<f64> = vec![
            _path_center_bend2[0] - gn_bend2_r * (_path_socket_mid_rot).cos(),
            _path_center_bend2[1] + gn_bend2_r * (_path_socket_mid_rot).sin(),
        ];
        let _path_plug_start: Vec<f64> = vec![
            _path_center_bend2[0] - gn_bend2_r * (_path_plug_start_rot).cos(),
            _path_center_bend2[1] + gn_bend2_r * (_path_plug_start_rot).sin(),
        ];
        let _path_plug_mid: Vec<f64> = vec![
            _path_center_bend2[0] - gn_bend2_r * (_path_plug_mid_rot).cos(),
            _path_center_bend2[1] + gn_bend2_r * (_path_plug_mid_rot).sin(),
        ];
        let _path_p4: Vec<f64> = vec![
            _path_center_bend2[0] - gn_bend2_r * (_path_total_rot).cos(),
            _path_center_bend2[1] + gn_bend2_r * (_path_total_rot).sin(),
        ];
        let _path_p5: Vec<f64> = vec![
            ((_path_p4.clone())[0] + (gn_tip_straight_len * (_tan_after_bend2.clone())[0])),
            ((_path_p4.clone())[1] + (gn_tip_straight_len * (_tan_after_bend2.clone())[1])),
        ];
        let split_normal: Vec<f64> = vec![
            0.0,
            -((_tan_at_junction.clone())[0]),
            (_tan_at_junction.clone())[1],
        ];
        let split_junction_y: f64 = (soda_faucet_tube_y - (_path_junction.clone())[0]);
        let split_junction_z: f64 = (zone5_z_top + (_path_junction.clone())[1]);
        let print_base_build_rot: f64 = (15.0 * (std::f64::consts::PI / 180.0));
        let print_tip_build_rot: f64 = ((split_junction_rot + _path_total_rot) / 2.0);
        let print_base_tilt_rad: f64 = print_base_build_rot;
        let print_tip_tilt_rad: f64 = (print_tip_build_rot - split_junction_rot);
        let max_print_overhang_rad: f64 = {
            let mut values = vec![
                print_base_build_rot,
                (split_junction_rot - print_base_build_rot),
                (print_tip_build_rot - split_junction_rot),
                (_path_total_rot - print_tip_build_rot),
            ];
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        };
        let _back_arch_dy: f64 = (fill_y_min - shell_rect_y_min);
        let back_arch_center_z: f64 = (((zone4_z_top + zone3_z_bottom) / 2.0)
            - ((_back_arch_dy).powi(2) / (2.0 * (zone4_z_top - zone3_z_bottom))));
        let back_arch_r: f64 = (zone4_z_top - back_arch_center_z);
        let _back_arch_a_low: f64 =
            (zone3_z_bottom - back_arch_center_z).atan2((shell_rect_y_min - fill_y_min));
        let _back_arch_a_mid: f64 = (((std::f64::consts::PI / 2.0) + _back_arch_a_low) / 2.0);
        let back_arch_mid_y: f64 = (fill_y_min + (back_arch_r * (_back_arch_a_mid).cos()));
        let back_arch_mid_z: f64 = (back_arch_center_z + (back_arch_r * (_back_arch_a_mid).sin()));
        let _z5_y_min: f64 = ((soda_faucet_tube_y + tube_shell_center_y) - tube_shell_outer_r);
        let _z5_y_max: f64 = ((soda_faucet_tube_y + tube_shell_center_y) + tube_shell_outer_r);
        let zone45_front_y: f64 = {
            let mut values = vec![
                (_z5_y_min - (shell_rect_y_max - _z5_y_max)),
                ((soda_faucet_tube_y - (soda_faucet_hole_diameter / 2.0))
                    - (4.0 * wall_thickness_min)),
            ];
            values.into_iter().fold(f64::INFINITY, f64::min)
        };
        let zone45_z_top: f64 = (zone4_z_top + 3.0);
        let zone45_z_bottom_at_front: f64 = (back_arch_center_z
            + ((back_arch_r).powi(2) - (zone45_front_y - fill_y_min).powi(2)).sqrt());
        let _a_front: f64 =
            (zone45_z_bottom_at_front - back_arch_center_z).atan2((zone45_front_y - fill_y_min));
        let _a_high: f64 = (std::f64::consts::PI / 2.0);
        let _a_mid45: f64 = ((_a_front + _a_high) / 2.0);
        let zone45_bot_mid_y: f64 = (fill_y_min + (back_arch_r * (_a_mid45).cos()));
        let zone45_bot_mid_z: f64 = (back_arch_center_z + (back_arch_r * (_a_mid45).sin()));
        let lower_outer_sections: Vec<Vec<f64>> = vec![
            vec![0.0, foot_width, foot_depth, foot_center_y],
            vec![8.5, foot_width, foot_depth, foot_center_y],
            vec![20.0, 48.0, 53.5, 4.25],
            vec![34.0, 44.0, 52.5, 5.25],
            vec![43.0, 38.0, 50.0, 5.0],
            vec![59.0, 30.0, 31.0, 11.5],
        ];
        let lower_neck_z: f64 = 65.0;
        let neck_land_overrun: f64 = 0.2;
        let signal_lower_exit_x: f64 = paths["LOWER_BUNDLE_X"].as_f64().unwrap();
        let signal_lower_exit_y: f64 = paths["LOWER_RIBBON_Y"].as_f64().unwrap();
        let signal_lower_exit_angle: f64 = 0.0;
        let lower_signal_ribbon: (f64, f64, bool, f64) = (
            signal_ribbon_max_width,
            signal_ribbon_max_depth,
            false,
            -(50.0),
        );
        let signal_lane_bottom_z: f64 = -(6.2);
        let bundle_land_below: f64 = 0.5;
        let bundle_land_above: f64 = 0.2;
        let bore_overrun: f64 = 2.0;
        let beverage_lead: f64 = 0.5;
        let drain_relief_lead: f64 = 0.25;
        let vent_outlet_reach: f64 = 0.6;
        let display_usb_reference_file: String = "ESP32-S3-Touch-LCD-1_47_20250411.stp".to_string();
        let display_usb_reference_url: String="https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-2D3D.zip".to_string();
        let display_usb_reference_sha256: String =
            "15fddd5d2b699d0b7c5160f2e11f176a672e7b305604f43a6dbaa30b8cc0059e".to_string();
        let display_usb_reference_bounds: Vec<Vec<f64>> = vec![
            vec![-(4.799962), -(22.484226), 0.750479],
            vec![4.780038, -(14.954223), 4.910479],
        ];
        let display_usb_half_width: f64 = (({
            let mut values = vec![];
            values.extend({
                let mut out3 = Vec::new();
                for row3_0 in (display_usb_reference_bounds.clone()).iter() {
                    let row = row3_0.clone();
                    out3.push(((row)[0]).abs());
                }
                out3
            });
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        } * 100.0)
            .ceil()
            / 100.0);
        let display_usb_y_range: Vec<f64> = vec![
            ((((display_usb_reference_bounds.clone())[0])[1] * 100.0).floor() / 100.0),
            ((((display_usb_reference_bounds.clone())[1])[1] * 100.0).ceil() / 100.0),
        ];
        let display_usb_top_z: f64 =
            ((((display_usb_reference_bounds.clone())[1])[2] * 100.0).ceil() / 100.0);
        let dispense_face_thickness: f64 = 2.0;
        let display_seat_reference_n: f64 = 10.1;
        let display_additional_tube_clearance: f64 = 1.5;
        let display_nominal_tube_clearance: f64 = (0.3 + display_additional_tube_clearance);
        let display_feet_n: f64 = (display_seat_reference_n + display_additional_tube_clearance);
        let display_floor_n: f64 = display_feet_n;
        let display_pocket_inset: f64 =
            ((tube_shell_center_y + display_neck_outer_r) - display_feet_n);
        let display_cradle_clearance: f64 = 0.25;
        let display_wire_bend_radius: f64 = 2.5;
        let display_ribbon_join_s: f64 = 46.0;
        let display_ribbon_reference_start_s: f64 = (display_ribbon_join_s + 0.5);
        let display_ribbon_side_x: f64 = -(8.2);
        let display_ribbon_side_radius: f64 = 8.0;
        let display_ribbon_side_drop: f64 = 0.0;
        let display_ribbon_side_lift: f64 = 0.4;
        let display_ribbon_side_run_n: f64 = (display_seat_reference_n + 1.0);
        let display_ribbon_pcb_gap: f64 = 0.3;
        let display_s_bottom: f64 = ((dispense_face_thickness - (display_usb_y_range.clone())[0])
            - (display_housing_length / 2.0));
        let display_s_top: f64 =
            ((display_s_bottom + display_housing_length) + (2.0 * display_cradle_clearance));
        let _display_housing_center_s: f64 =
            ((display_s_bottom + display_cradle_clearance) + (display_housing_length / 2.0));
        let display_face_n: f64 = (display_feet_n + display_total_depth);
        let display_cosmetic_wall: f64 = 1.3;
        let display_cover_top_n: f64 =
            ((display_face_n + display_cover_over_face) + display_cosmetic_wall);
        let display_cover_bottom_n: f64 = (display_seat_reference_n - 6.8);
        let display_cover_shoulder_n: f64 = (display_seat_reference_n + 0.5);
        let display_cover_face_width: f64 = 27.5;
        let display_cover_end_margin: f64 = 1.25;
        let display_cover_face_length: f64 = (display_s_top + display_cover_end_margin);
        let _display_cover_center_s: f64 = (display_cover_face_length / 2.0);
        let display_cover_skirt_width: f64 =
            (2.0 * ((display_neck_outer_r + display_cover_slip) + display_cosmetic_wall));
        let display_cover_skirt_length: f64 = (display_cover_face_length + 5.1);
        let display_cover_face_r: f64 = 7.25;
        let display_cover_skirt_r: f64 = 10.0;
        let display_cover_skirt_rear_s: f64 =
            (_display_cover_center_s + (display_cover_skirt_length / 2.0));
        let display_cover_rear_rim_s0: f64 = 41.7;
        let display_cover_rear_rim_ds_dn: f64 = 0.6;
        let display_head_s_min: f64 = 0.0;
        let display_head_s_max: f64 = (display_cover_skirt_rear_s + 0.2);
        let display_clip_s_bottom: f64 = (((_display_cover_center_s
            - (display_cover_skirt_length / 2.0))
            + display_cover_skirt_r)
            + snap["END_MARGIN"].as_f64().unwrap());
        let display_clip_s_top: f64 = (((_display_cover_center_s
            + (display_cover_skirt_length / 2.0))
            - display_cover_skirt_r)
            - snap["END_MARGIN"].as_f64().unwrap());
        let display_clip_bottom_n: f64 = display_cover_bottom_n;
        let display_clip_top_n: f64 =
            (display_clip_bottom_n + snap["LIP_HEIGHT"].as_f64().unwrap());
        let display_clip_lip_radius: f64 =
            (display_neck_outer_r - snap["ENGAGEMENT"].as_f64().unwrap());
        let display_clip_groove_radius: f64 =
            (display_clip_lip_radius - snap["RADIAL_SLIP"].as_f64().unwrap());
        let display_foot_pad_width: f64 = 3.0;
        let display_foot_pad_depth: f64 = (wall_thickness_min + display_additional_tube_clearance);
        let display_channel_half_width: f64 = 6.75;
        let display_cartridge_lift_n: f64 = 9.5;
        let display_cartridge_slide_s: f64 = 60.0;
        let display_loading_travel_n: f64 = 25.0;
        let display_foot_envelope_r: f64 = (3.0_f64).sqrt();
        let display_foot_centers: Vec<Vec<f64>> = {
            let mut out4 = Vec::new();
            for row4_0 in (vec![-(8.5), 8.5]).iter() {
                let x = row4_0.clone();
                for row4_1 in (vec![-(19.5), 19.5]).iter() {
                    let y = row4_1.clone();
                    out4.push(vec![
                        x,
                        (((display_s_bottom + display_cradle_clearance)
                            + (display_housing_length / 2.0))
                            + y),
                    ]);
                }
            }
            out4
        };
        let display_ribbon_terminal_y: f64 = -(11.0);
        let display_ribbon_terminal_s: f64 =
            (_display_housing_center_s + display_ribbon_terminal_y);
        let display_cover_inner_rows: Vec<Vec<f64>> = vec![
            vec![
                (display_cover_skirt_width - (2.0 * display_cosmetic_wall)),
                50.0,
                8.7,
                (display_cover_bottom_n - 1.0),
            ],
            vec![
                (display_cover_skirt_width - (2.0 * display_cosmetic_wall)),
                50.0,
                8.7,
                display_cover_shoulder_n,
            ],
            vec![
                (display_housing_width + (2.0 * display_cradle_clearance)),
                (display_housing_length + (2.0 * display_cradle_clearance)),
                (display_corner_r + display_cradle_clearance),
                (display_face_n + display_cover_over_face),
            ],
        ];
        let display_cover_inner_clamp: Vec<f64> = vec![50.0, -(20.0), display_s_top, -(30.0), 40.0];
        let display_groove_reach: f64 = 1.0;
        let display_pocket_overrun: f64 = 1.0;
        let display_channel_overlap: f64 = 0.1;
        let display_ribbon_top_n: f64 = ((display_feet_n
            + interface["display_pcb_bottom_z"].as_f64().unwrap())
            - display_ribbon_pcb_gap);
        let piece_mesh_tol: f64 = 0.005;
        let piece_mesh_angle: f64 = 0.05;
        Self {
            above_counter_gasket_thickness,
            above_counter_plate_thickness,
            flavor_tube_od,
            flavor_tube_x_offset,
            flavor_tube_hole_dia,
            pill_length_x,
            pill_width_y,
            flavor_tube_depth,
            display_housing_width,
            display_housing_length,
            display_pcb_width,
            display_pcb_length,
            display_corner_r,
            display_pcb_corner_r,
            display_total_depth,
            display_pcb_top_z,
            display_cover_slip,
            display_cover_lap,
            display_cover_over_face,
            shell_center_x,
            shell_center_y,
            zone1_z_bottom,
            zone1_z_top,
            zone1_height,
            bore_clearance,
            westbrass_bore_diameter,
            westbrass_bore_x,
            westbrass_bore_y,
            flavor_pill_center,
            flavor_pill_y_minus_edge,
            wall_thickness_min,
            show_wall,
            print_layer_height,
            print_bead_width,
            _westbrass_bore_farthest_from_shell_center,
            _pill_farthest_from_shell_center,
            shell_outer_r,
            zone2_z_bottom,
            zone2_z_top,
            zone2_height,
            westbrass_rect_long_y,
            westbrass_rect_short_x,
            westbrass_bore_rect_long_y,
            westbrass_bore_rect_short_x,
            cove_r,
            zone2_bore_z_bottom,
            shell_outer_lip,
            zone1_outer_z_top,
            zone2_outer_z_bottom,
            foot_width,
            foot_depth,
            foot_center_y,
            base_pod_counterbore_dia,
            base_pod_shank_dia,
            base_pod_wall,
            base_pod_center_x,
            base_pod_center_y,
            base_pod_front_center_x,
            base_pod_front_center_y,
            base_pod_centers,
            base_pod_z_bottom,
            base_pod_insert_dia,
            base_insert_outer_dia,
            base_insert_length,
            base_pedestal_dia,
            base_pedestal_height,
            base_pedestal_chamfer,
            base_pod_hole_dia,
            base_pod_hole_depth,
            base_insert_bottom_z,
            base_pod_insert_depth,
            base_pod_z_top,
            base_pod_radius,
            base_screw_length,
            base_screw_head_height,
            base_screw_head_recess,
            base_screw_counterbore_depth,
            base_screw_seat_z,
            base_plate_seat_thickness,
            lever_x_half,
            lever_fit_clearance,
            lever_sweep_allowance,
            lever_insertion_front_y,
            lever_rest_back_y,
            lever_clearance_x_half,
            lever_clearance_y_back,
            lever_rest_top_z,
            shell_rect_y_half,
            shell_rect_x_half,
            shell_rect_y_width,
            shell_rect_x_width,
            shell_rect_y_max,
            shell_rect_y_min,
            zone3_z_bottom,
            arch_z_base,
            arch_z_peak,
            westbrass_arch_inner_x,
            westbrass_arch_outer_x,
            shell_arch_bore_inner_x,
            shell_arch_bore_outer_x,
            shell_arch_bore_z_foot_top,
            shell_arch_bore_z_peak,
            shell_arch_z_foot_top,
            shell_arch_z_peak,
            wing_inner_x,
            wing_outer_x,
            soda_faucet_tube_y,
            soda_faucet_tube_od,
            soda_faucet_hole_diameter,
            flavor_tube_post_bend_y,
            flavor_bend_min_radius,
            flavor_bend_radius,
            flavor_bend_start_z,
            flavor_bend_angle_rad,
            fill_y_min,
            zone4_z_bottom,
            zone4_z_top,
            zone4_height,
            zone5_z_bottom,
            zone5_z_top,
            zone5_height,
            flavor_offset_y_from_water,
            split_socket_wall,
            split_plug_wall,
            split_slip,
            zone5_wall,
            signal_lane_width,
            signal_lane_depth,
            signal_lane_center_n,
            signal_ribbon_max_width,
            signal_ribbon_max_depth,
            _tube_soda_bore_r,
            _tube_pill_bore_r,
            _tube_pill_cap_x,
            _tube_bore_caps,
            tube_shell_center_y,
            tube_shell_bore_radius,
            tube_shell_outer_r,
            tube_shell_soda_r_outer,
            tube_shell_pill_x_half_outer,
            tube_shell_x_half_outer,
            tube_shell_x_outer,
            display_neck_outer_r,
            _neck_plug_min_wall,
            gn_bend1_sweep_rad,
            gn_bend2_sweep_rad,
            gn_mid_straight_len,
            gn_tip_straight_len,
            gn_outlet_y,
            gn_outlet_z,
            _path_total_rot,
            gn_bend1_r,
            gn_bend2_r,
            gn_bend1_z_start,
            gn_bend1_z_mid,
            split_junction_rot,
            split_socket_overlap_len,
            split_plug_overlap_len,
            split_socket_shrink,
            split_plug_shrink,
            split_socket_angle_rad,
            split_plug_angle_rad,
            _path_socket_start_rot,
            _path_socket_mid_rot,
            _path_plug_start_rot,
            _path_plug_mid_rot,
            _tan_after_bend1,
            _tan_after_bend2,
            _tan_at_junction,
            _tan_at_socket_start,
            _tan_at_plug_start,
            _path_z_lift,
            _path_p2,
            _path_p3,
            _path_center_bend2,
            _path_junction,
            _path_socket_start,
            _path_socket_mid,
            _path_plug_start,
            _path_plug_mid,
            _path_p4,
            _path_p5,
            split_normal,
            split_junction_y,
            split_junction_z,
            print_base_build_rot,
            print_tip_build_rot,
            print_base_tilt_rad,
            print_tip_tilt_rad,
            max_print_overhang_rad,
            _back_arch_dy,
            back_arch_center_z,
            back_arch_r,
            _back_arch_a_low,
            _back_arch_a_mid,
            back_arch_mid_y,
            back_arch_mid_z,
            _z5_y_min,
            _z5_y_max,
            zone45_front_y,
            zone45_z_top,
            zone45_z_bottom_at_front,
            _a_front,
            _a_high,
            _a_mid45,
            zone45_bot_mid_y,
            zone45_bot_mid_z,
            lower_outer_sections,
            lower_neck_z,
            neck_land_overrun,
            signal_lower_exit_x,
            signal_lower_exit_y,
            signal_lower_exit_angle,
            lower_signal_ribbon,
            signal_lane_bottom_z,
            bundle_land_below,
            bundle_land_above,
            bore_overrun,
            beverage_lead,
            drain_relief_lead,
            vent_outlet_reach,
            display_usb_reference_file,
            display_usb_reference_url,
            display_usb_reference_sha256,
            display_usb_reference_bounds,
            display_usb_half_width,
            display_usb_y_range,
            display_usb_top_z,
            dispense_face_thickness,
            display_seat_reference_n,
            display_additional_tube_clearance,
            display_nominal_tube_clearance,
            display_feet_n,
            display_floor_n,
            display_pocket_inset,
            display_cradle_clearance,
            display_wire_bend_radius,
            display_ribbon_join_s,
            display_ribbon_reference_start_s,
            display_ribbon_side_x,
            display_ribbon_side_radius,
            display_ribbon_side_drop,
            display_ribbon_side_lift,
            display_ribbon_side_run_n,
            display_ribbon_pcb_gap,
            display_s_bottom,
            display_s_top,
            _display_housing_center_s,
            display_face_n,
            display_cosmetic_wall,
            display_cover_top_n,
            display_cover_bottom_n,
            display_cover_shoulder_n,
            display_cover_face_width,
            display_cover_end_margin,
            display_cover_face_length,
            _display_cover_center_s,
            display_cover_skirt_width,
            display_cover_skirt_length,
            display_cover_face_r,
            display_cover_skirt_r,
            display_cover_skirt_rear_s,
            display_cover_rear_rim_s0,
            display_cover_rear_rim_ds_dn,
            display_head_s_min,
            display_head_s_max,
            display_clip_s_bottom,
            display_clip_s_top,
            display_clip_bottom_n,
            display_clip_top_n,
            display_clip_lip_radius,
            display_clip_groove_radius,
            display_foot_pad_width,
            display_foot_pad_depth,
            display_channel_half_width,
            display_cartridge_lift_n,
            display_cartridge_slide_s,
            display_loading_travel_n,
            display_foot_envelope_r,
            display_foot_centers,
            display_ribbon_terminal_y,
            display_ribbon_terminal_s,
            display_cover_inner_rows,
            display_cover_inner_clamp,
            display_groove_reach,
            display_pocket_overrun,
            display_channel_overlap,
            display_ribbon_top_n,
            piece_mesh_tol,
            piece_mesh_angle,
        }
    }
}
