//! Authored appliance/faucet stack and umbilical dimensions, in millimetres.
#![allow(unused_parens, unused_variables)]
use super::assembly::{axis, d2};
use anyhow::{Result, bail};
use serde::Serialize;
use serde_json::{Value, json};
#[derive(Clone, Serialize)]
pub struct Dimensions {
    #[serde(skip)]
    pub shell: crate::shell_dimensions::Dimensions,
    #[serde(skip)]
    pub root: std::path::PathBuf,
    pub display_housing_width: f64,
    pub display_housing_length: f64,
    pub display_pcb_width: f64,
    pub display_pcb_length: f64,
    pub display_corner_r: f64,
    pub display_pcb_corner_r: f64,
    pub display_total_depth: f64,
    pub display_pcb_bottom_z: f64,
    pub display_pcb_top_z: f64,
    pub port_center_depth: f64,
    pub plateau_z: f64,
    pub westbrass_od: f64,
    pub westbrass_r: f64,
    pub shank_od: f64,
    pub shank_length: f64,
    pub countertop_hole_diameter: f64,
    pub soda_faucet_tube_od: f64,
    pub soda_faucet_tube_r: f64,
    pub soda_faucet_tube_above_plateau: f64,
    pub soda_faucet_tube_into_port: f64,
    pub soda_faucet_tube_z_bottom: f64,
    pub soda_faucet_tube_z_top: f64,
    pub flavor_tube_od: f64,
    pub flavor_tube_r: f64,
    pub flavor_tube_depth_lower: f64,
    pub flavor_tube_x_offset: f64,
    pub countertop_thickness: f64,
    pub countertop_min_thickness: f64,
    pub countertop_max_thickness: f64,
    pub countertop_top_z: f64,
    pub countertop_bottom_z: f64,
    pub under_counter_plate_thickness: f64,
    pub under_counter_plate_bottom_z: f64,
    pub mount_return_start_z: f64,
    pub mount_return_lead: f64,
    pub foam_od: f64,
    pub foam_r: f64,
    pub pack_flavor_depth: f64,
    pub drain_tube_r: f64,
    pub drain_tail_x: f64,
    pub drain_pack_y: f64,
    pub drain_bypass_y: f64,
    pub drain_tail_y: f64,
    pub drain_bend_radius: f64,
    pub step_bend_radius: f64,
    pub flavor_a_step_lead: f64,
    pub flavor_b_step_lead: f64,
    pub flavor_sides: Vec<f64>,
    pub organizer_top_z: f64,
    pub organizer_bottom_z: f64,
    pub organizer_stations: Vec<f64>,
    pub organizer_gather_gap: f64,
    pub organizer_return_start_z: f64,
    pub step_theta_rad: f64,
    pub step_rise: f64,
    pub _drain_organizer_offset: f64,
    pub _drain_organizer_rise: f64,
    pub gather_start_z: f64,
    pub umbilical_bend_radius: f64,
    pub drain_gather_rise: f64,
    pub umbilical_z_bottom: f64,
    pub blue_cut_length: f64,
    pub umbilical_drawn: f64,
    pub soda_umbilical_tube_od: f64,
    pub soda_umbilical_tube_r: f64,
    pub soda_umbilical_tube_z_top: f64,
    pub umbilical_tail_z: f64,
    pub soda_umbilical_tube_z_bottom: f64,
    pub foam_z_top: f64,
    pub foam_bare_at_westbrass: f64,
    pub foam_bare_at_wall: f64,
    pub foam_length: f64,
    pub foam_z_bottom: f64,
    pub flavor_tube_depth_upper: f64,
    pub flavor_bend_radius: f64,
    pub _flavor_depth_offset: f64,
    pub flavor_bend_theta_rad: f64,
    pub pre_bend_rise: f64,
    pub pre_bend_z: f64,
    pub lever_top_z: f64,
    pub gn_bend1_r: f64,
    pub gn_bend2_r: f64,
    pub gn_bend1_sweep_rad: f64,
    pub gn_bend2_sweep_rad: f64,
    pub gn_bend1_mid_z: f64,
    pub gn_bend1_start_z: f64,
    pub gn_mid_straight_len: f64,
    pub gn_tip_straight_len: f64,
    pub _gn_flavor_depth_offset: f64,
    pub gn_flavor_bend1_r: f64,
    pub gn_flavor_bend2_r: f64,
    pub flavor_tube_z_bottom: f64,
    pub flavor_tube_z_top: f64,
    pub cable_lane: f64,
    pub cable_width: f64,
    pub sleeve_wall: f64,
    pub sleeve_z_top: f64,
    pub sleeve_z_bottom: f64,
    pub collar_air: f64,
    pub _tails_clear: f64,
    pub tail_half_x: f64,
    pub splay_bend_radius: f64,
    pub splay_theta_rad: f64,
    pub splay_rise: f64,
    pub splay_top_z: f64,
    pub drain_splay_rise: f64,
    pub drain_splay_top_z: f64,
    pub collar_top_z: f64,
    pub lever_pivot_y: f64,
    pub lever_pivot_z: f64,
    pub lever_press_angle_deg: f64,
    pub lever_aft_y: f64,
    pub base_screw_shaft_r: f64,
    pub base_screw_head_r: f64,
    pub base_screw_socket_af: f64,
    pub base_screw_socket_depth: f64,
    pub base_screw_socket_below: f64,
    pub base_insert_inner_r: f64,
    pub display_pocket_inset: f64,
    pub display_screen_width: f64,
    pub display_screen_length: f64,
    pub display_screen_depth: f64,
    pub display_screen_corner_r: f64,
    pub countertop_slab_xy: f64,
    pub hole_radius: f64,
    pub _display_buttons: Value,
    pub tails_apart: f64,
    pub soda_faucet_cut_length: f64,
    pub _factory_metrics: Value,
    pub _display_components: Value,
    pub _dimension_paths: Value,
    pub countertop_hole_center_y: f64,
    pub splay_extra_length: f64,
    pub _tail_planes: Vec<f64>,
    pub countertop_hole_margin: f64,
    pub collar_tails: Vec<(String, f64, f64)>,
    pub flavor_cut_length: f64,
    pub sleeve_center_y: f64,
}
impl Dimensions {
    pub fn new(slip: f64, collar: &Value, root: &std::path::Path) -> Result<Self> {
        let shell = crate::shell_dimensions::Dimensions::new(slip);
        let interface = crate::interface(slip);
        let paths = crate::constants();
        let organizer = crate::organizer()["datums"].clone();
        let display_housing_width: f64 = interface["display_housing_width"].as_f64().unwrap();
        let display_housing_length: f64 = interface["display_housing_length"].as_f64().unwrap();
        let display_pcb_width: f64 = interface["display_pcb_width"].as_f64().unwrap();
        let display_pcb_length: f64 = interface["display_pcb_length"].as_f64().unwrap();
        let display_corner_r: f64 = interface["display_corner_r"].as_f64().unwrap();
        let display_pcb_corner_r: f64 = interface["display_pcb_corner_r"].as_f64().unwrap();
        let display_total_depth: f64 = interface["display_total_depth"].as_f64().unwrap();
        let display_pcb_bottom_z: f64 = interface["display_pcb_bottom_z"].as_f64().unwrap();
        let display_pcb_top_z: f64 = interface["display_pcb_top_z"].as_f64().unwrap();
        let port_center_depth: f64 = 8.875;
        let plateau_z: f64 = 39.0;
        let westbrass_od: f64 = 31.5;
        let westbrass_r: f64 = (westbrass_od / 2.0);
        let shank_od: f64 = 11.0;
        let shank_length: f64 = 50.0;
        let countertop_hole_diameter: f64 = 34.93;
        let soda_faucet_tube_od: f64 = (0.375 * 25.4);
        let soda_faucet_tube_r: f64 = (soda_faucet_tube_od / 2.0);
        let soda_faucet_tube_above_plateau: f64 = 40.0;
        let soda_faucet_tube_into_port: f64 = 15.0;
        let soda_faucet_tube_z_bottom: f64 = (plateau_z - soda_faucet_tube_into_port);
        let soda_faucet_tube_z_top: f64 = (plateau_z + soda_faucet_tube_above_plateau);
        let flavor_tube_od: f64 = interface["flavor_tube_od"].as_f64().unwrap();
        let flavor_tube_r: f64 = (flavor_tube_od / 2.0);
        let flavor_tube_depth_lower: f64 = interface["flavor_tube_depth"].as_f64().unwrap();
        let flavor_tube_x_offset: f64 = interface["flavor_tube_x_offset"].as_f64().unwrap();
        let countertop_thickness: f64 = 30.0;
        let countertop_min_thickness: f64 = 19.0;
        let countertop_max_thickness: f64 = 38.0;
        let countertop_top_z: f64 = (vec![-6.0_f64, -4.0_f64])[0];
        let countertop_bottom_z: f64 = (countertop_top_z - countertop_thickness);
        let under_counter_plate_thickness: f64 = 1.524;
        let under_counter_plate_bottom_z: f64 =
            (countertop_bottom_z - under_counter_plate_thickness);
        let mount_return_start_z: f64 =
            ((countertop_top_z - countertop_max_thickness) - under_counter_plate_thickness);
        let mount_return_lead: f64 = (under_counter_plate_bottom_z - mount_return_start_z);
        let foam_od: f64 = 25.4;
        let foam_r: f64 = (foam_od / 2.0);
        let pack_flavor_depth: f64 =
            ((foam_r + flavor_tube_r).powi(2) - (flavor_tube_x_offset).powi(2)).sqrt();
        let drain_tube_r: f64 = (interface["drain_tube_od"].as_f64().unwrap() / 2.0);
        let drain_tail_x: f64 = 0.0;
        let drain_pack_y: f64 =
            -(((foam_r + drain_tube_r).powi(2) - (drain_tail_x).powi(2)).sqrt());
        let drain_bypass_y: f64 = 8.9;
        let drain_tail_y: f64 = (drain_pack_y - 20.0);
        let drain_bend_radius: f64 = interface["drain_bend_min_radius"].as_f64().unwrap();
        let step_bend_radius: f64 = 30.0;
        let flavor_a_step_lead: f64 = mount_return_lead;
        let flavor_b_step_lead: f64 = mount_return_lead;
        let flavor_sides: Vec<f64> = vec![(1.0), -(1.0)];
        let organizer_top_z: f64 = -(88.0);
        let organizer_bottom_z: f64 = (organizer_top_z - organizer["LENGTH"].as_f64().unwrap());
        let organizer_stations: Vec<f64> = vec![organizer_top_z];
        let organizer_gather_gap: f64 = 7.0;
        let organizer_return_start_z: f64 = (organizer_bottom_z - 3.0);
        let flavor_mount_x =
            |sign: f64| interface["bundle_mount_x"].as_f64().unwrap() + sign * flavor_tube_x_offset;
        let step_theta = |sign: f64| {
            let target = axis(&organizer, if sign > 0.0 { "F1" } else { "F2" });
            let offset = d2(
                &target,
                &vec![sign * flavor_tube_x_offset, flavor_tube_depth_lower],
            );
            (1.0 - offset / (2.0 * step_bend_radius)).acos()
        };
        let step_theta_rad: f64 = {
            let mut values = vec![];
            values.extend({
                let mut out1 = Vec::new();
                for row1_0 in (flavor_sides.clone()).iter() {
                    let sign = row1_0.clone();
                    out1.push(step_theta(sign));
                }
                out1
            });
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        };
        let step_rise: f64 = ((2.0 * step_bend_radius) * (step_theta_rad).sin());
        let _drain_organizer_offset: f64 =
            d2(&vec![drain_tail_x, drain_bypass_y], &axis(&organizer, "D"));
        let _drain_organizer_rise: f64 = ((2.0 * drain_bend_radius)
            * ((1.0 - (_drain_organizer_offset / (2.0 * drain_bend_radius))).acos()).sin());
        let gather_start_z: f64 = ((organizer_return_start_z - {
            let mut values = vec![step_rise, _drain_organizer_rise];
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        }) - organizer_gather_gap);
        let umbilical_bend_radius: f64 = 30.0;
        let drain_gather_rise: f64 = ((2.0 * drain_bend_radius)
            * ((1.0 - ((drain_pack_y - drain_bypass_y).abs() / (2.0 * drain_bend_radius))).acos())
                .sin());
        let gather_rise = |sign: f64| {
            let offset = (sign * flavor_tube_x_offset - sign * flavor_tube_x_offset)
                .hypot(pack_flavor_depth - flavor_tube_depth_lower);
            2.0 * umbilical_bend_radius
                * (1.0 - offset / (2.0 * umbilical_bend_radius)).acos().sin()
        };
        let umbilical_z_bottom: f64 = (gather_start_z - {
            let mut values = vec![gather_rise((1.0)), gather_rise(-(1.0)), drain_gather_rise];
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        });
        let blue_cut_length: f64 = 1540.0;
        let umbilical_drawn: f64 = 300.0;
        let soda_umbilical_tube_od: f64 = 6.35;
        let soda_umbilical_tube_r: f64 = (soda_umbilical_tube_od / 2.0);
        let soda_umbilical_tube_z_top: f64 = -(shank_length);
        let umbilical_tail_z: f64 = (soda_umbilical_tube_z_top - umbilical_drawn);
        let soda_umbilical_tube_z_bottom: f64 = umbilical_tail_z;
        let foam_z_top: f64 = umbilical_z_bottom;
        let foam_bare_at_westbrass: f64 = (soda_umbilical_tube_z_top - foam_z_top);
        let foam_bare_at_wall: f64 = 75.0;
        let foam_length: f64 = ((blue_cut_length - foam_bare_at_westbrass) - foam_bare_at_wall);
        let foam_z_bottom: f64 = (umbilical_tail_z + foam_bare_at_wall);
        let flavor_tube_depth_upper: f64 =
            (port_center_depth + paths["TIGHT_FLAVOR_N"].as_f64().unwrap());
        let flavor_bend_radius: f64 = shell.flavor_bend_radius;
        let _flavor_depth_offset: f64 = (flavor_tube_depth_lower - flavor_tube_depth_upper);
        let flavor_bend_theta_rad: f64 = shell.flavor_bend_angle_rad;
        let pre_bend_rise: f64 = 3.0;
        let pre_bend_z: f64 = shell.flavor_bend_start_z;
        let lever_top_z: f64 = (plateau_z + 13.0);
        let gn_bend1_r: f64 = shell.gn_bend1_r;
        let gn_bend2_r: f64 = shell.gn_bend2_r;
        let gn_bend1_sweep_rad: f64 = shell.gn_bend1_sweep_rad;
        let gn_bend2_sweep_rad: f64 = shell.gn_bend2_sweep_rad;
        let gn_bend1_mid_z: f64 = shell.gn_bend1_z_mid;
        let gn_bend1_start_z: f64 = shell.gn_bend1_z_start;
        let gn_mid_straight_len: f64 = shell.gn_mid_straight_len;
        let gn_tip_straight_len: f64 = shell.gn_tip_straight_len;
        let _gn_flavor_depth_offset: f64 = (flavor_tube_depth_upper - port_center_depth);
        let gn_flavor_bend1_r: f64 = (gn_bend1_r + _gn_flavor_depth_offset);
        let gn_flavor_bend2_r: f64 = (gn_bend2_r + _gn_flavor_depth_offset);
        let flavor_tube_z_bottom: f64 = umbilical_tail_z;
        let flavor_tube_z_top: f64 = soda_faucet_tube_z_top;
        let cable_lane: f64 = shell.signal_ribbon_max_depth;
        let cable_width: f64 = shell.signal_ribbon_max_width;
        let sleeve_wall: f64 = 1.0;
        let sleeve_z_top: f64 = organizer_top_z;
        let sleeve_z_bottom: f64 = foam_z_bottom;
        let collar_air: f64 = 2.0;
        let _tails_clear: f64 = ((2.0
            * (collar["OD"].as_f64().unwrap() / 2.0).hypot(collar["RISE"].as_f64().unwrap()))
            + collar_air);
        let tail_half_x: f64 = {
            let mut values = vec![
                (_tails_clear / 2.0),
                ({
                    let mut values =
                        vec![0.0, ((_tails_clear).powi(2) - (pack_flavor_depth).powi(2))];
                    values.into_iter().fold(f64::NEG_INFINITY, f64::max)
                })
                .sqrt(),
            ];
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        };
        let splay_bend_radius: f64 = 30.0;
        let splay_theta_rad: f64 =
            (1.0 - ((tail_half_x - flavor_tube_x_offset) / (2.0 * splay_bend_radius))).acos();
        let splay_rise: f64 = ((2.0 * splay_bend_radius) * (splay_theta_rad).sin());
        let splay_top_z: f64 = sleeve_z_bottom;
        let drain_splay_rise: f64 = ((2.0 * drain_bend_radius)
            * ((1.0 - ((drain_tail_y - drain_pack_y).abs() / (2.0 * drain_bend_radius))).acos())
                .sin());
        let drain_splay_top_z: f64 = splay_top_z;
        let collar_top_z: f64 = (splay_top_z - {
            let mut values = vec![splay_rise, drain_splay_rise];
            values.into_iter().fold(f64::NEG_INFINITY, f64::max)
        });
        let lever_pivot_y: f64 = (1.5);
        let lever_pivot_z: f64 = (plateau_z + 7.0);
        let lever_press_angle_deg: f64 = 18.0;
        let lever_aft_y: f64 = 9.0;
        let base_screw_shaft_r: f64 = 1.5;
        let base_screw_head_r: f64 = 2.75;
        let base_screw_socket_af: f64 = 2.5;
        let base_screw_socket_depth: f64 = 1.6;
        let base_screw_socket_below: f64 = 0.1;
        let base_insert_inner_r: f64 = 1.5;
        let display_pocket_inset: f64 = shell.display_pocket_inset;
        let display_screen_width: f64 = 17.75;
        let display_screen_length: f64 = 32.93;
        let display_screen_depth: f64 = 0.4;
        let display_screen_corner_r: f64 = 2.0;
        let countertop_slab_xy: f64 = 120.0;
        let hole_radius: f64 = (countertop_hole_diameter / 2.0);
        let mut data = Self {
            shell,
            root: root.to_owned(),
            display_housing_width,
            display_housing_length,
            display_pcb_width,
            display_pcb_length,
            display_corner_r,
            display_pcb_corner_r,
            display_total_depth,
            display_pcb_bottom_z,
            display_pcb_top_z,
            port_center_depth,
            plateau_z,
            westbrass_od,
            westbrass_r,
            shank_od,
            shank_length,
            countertop_hole_diameter,
            soda_faucet_tube_od,
            soda_faucet_tube_r,
            soda_faucet_tube_above_plateau,
            soda_faucet_tube_into_port,
            soda_faucet_tube_z_bottom,
            soda_faucet_tube_z_top,
            flavor_tube_od,
            flavor_tube_r,
            flavor_tube_depth_lower,
            flavor_tube_x_offset,
            countertop_thickness,
            countertop_min_thickness,
            countertop_max_thickness,
            countertop_top_z,
            countertop_bottom_z,
            under_counter_plate_thickness,
            under_counter_plate_bottom_z,
            mount_return_start_z,
            mount_return_lead,
            foam_od,
            foam_r,
            pack_flavor_depth,
            drain_tube_r,
            drain_tail_x,
            drain_pack_y,
            drain_bypass_y,
            drain_tail_y,
            drain_bend_radius,
            step_bend_radius,
            flavor_a_step_lead,
            flavor_b_step_lead,
            flavor_sides,
            organizer_top_z,
            organizer_bottom_z,
            organizer_stations,
            organizer_gather_gap,
            organizer_return_start_z,
            step_theta_rad,
            step_rise,
            _drain_organizer_offset,
            _drain_organizer_rise,
            gather_start_z,
            umbilical_bend_radius,
            drain_gather_rise,
            umbilical_z_bottom,
            blue_cut_length,
            umbilical_drawn,
            soda_umbilical_tube_od,
            soda_umbilical_tube_r,
            soda_umbilical_tube_z_top,
            umbilical_tail_z,
            soda_umbilical_tube_z_bottom,
            foam_z_top,
            foam_bare_at_westbrass,
            foam_bare_at_wall,
            foam_length,
            foam_z_bottom,
            flavor_tube_depth_upper,
            flavor_bend_radius,
            _flavor_depth_offset,
            flavor_bend_theta_rad,
            pre_bend_rise,
            pre_bend_z,
            lever_top_z,
            gn_bend1_r,
            gn_bend2_r,
            gn_bend1_sweep_rad,
            gn_bend2_sweep_rad,
            gn_bend1_mid_z,
            gn_bend1_start_z,
            gn_mid_straight_len,
            gn_tip_straight_len,
            _gn_flavor_depth_offset,
            gn_flavor_bend1_r,
            gn_flavor_bend2_r,
            flavor_tube_z_bottom,
            flavor_tube_z_top,
            cable_lane,
            cable_width,
            sleeve_wall,
            sleeve_z_top,
            sleeve_z_bottom,
            collar_air,
            _tails_clear,
            tail_half_x,
            splay_bend_radius,
            splay_theta_rad,
            splay_rise,
            splay_top_z,
            drain_splay_rise,
            drain_splay_top_z,
            collar_top_z,
            lever_pivot_y,
            lever_pivot_z,
            lever_press_angle_deg,
            lever_aft_y,
            base_screw_shaft_r,
            base_screw_head_r,
            base_screw_socket_af,
            base_screw_socket_depth,
            base_screw_socket_below,
            base_insert_inner_r,
            display_pocket_inset,
            display_screen_width,
            display_screen_length,
            display_screen_depth,
            display_screen_corner_r,
            countertop_slab_xy,
            hole_radius,
            _display_buttons: Value::Null,
            tails_apart: 0.0,
            soda_faucet_cut_length: 0.0,
            _factory_metrics: Value::Null,
            _display_components: Value::Null,
            _dimension_paths: Value::Null,
            countertop_hole_center_y: 0.0,
            splay_extra_length: 0.0,
            _tail_planes: Vec::new(),
            countertop_hole_margin: 0.0,
            collar_tails: Vec::new(),
            flavor_cut_length: 0.0,
            sleeve_center_y: 0.0,
        };
        data._display_components = serde_json::from_slice(&std::fs::read(root.join(
            "hardware/reference/touch-flo-faucet/display-reference/component-envelopes.json",
        ))?)?;
        data._display_buttons = serde_json::from_slice(&std::fs::read(
            root.join("hardware/reference/touch-flo-faucet/display-reference/buttons.json"),
        )?)?;
        data.finish_dimensions()?;
        Ok(data)
    }
}
