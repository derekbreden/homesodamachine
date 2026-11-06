//! Enclosure scalar interfaces and construction datums.
use super::{array, f, text};
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_numbers::{rear_wall, shell};
use serde_json::{Value, json};

fn wago_stand(v: &Value, size: &str) -> Result<[f64; 3]> {
    let row = &v["wago"]["SIZES"][size];
    Ok([f(row, "height")?, f(row, "width")?, f(row, "depth")?])
}

fn wago_half(v: &Value, size: &str, wall: f64, press: f64) -> Result<[f64; 2]> {
    let [y, z, _] = wago_stand(v, size)?;
    Ok([y / 2. + wall + press, z / 2. + wall + press])
}

fn wago_swing(v: &Value, size: &str) -> Result<f64> {
    let [y, _, _] = wago_stand(v, size)?;
    Ok(y + f(&v["wago"]["SIZES"][size], "rows")? * f(&v["wago"], "lever_swing")?)
}

fn interface(v: &Value) -> Result<Value> {
    let fit = &v["fits"];
    let z_seam: f64 = shell::Z_SEAM;
    let slide_slip: f64 = f(fit, "running")?;
    let wall: f64 = shell::WALL;
    let ceiling_skin: f64 = shell::CEILING_SKIN;
    let extrusion_w: f64 = 0.42;
    let rear_seam_clear: f64 = 3.0;
    let funnel_collar_air: f64 = f(fit, "running")?;
    let y_stack_high_depth: f64 = shell::Y_STACK_HIGH_DEPTH;
    let rear_plane_y: f64 = shell::REAR_PLANE_Y;
    let co2_axis_drop: f64 = f(fit, "supported_surface")?;
    let show_edge_r: f64 = shell::SHOW_EDGE_R;
    let show_corner_r: f64 = shell::CORNER_ROUND;
    let pump_station_lead: f64 = -0.074;
    let pump_station_drop: f64 = shell::shell().pump_station_drop;
    let pump_seated_drop: f64 = shell::shell().pump_seated_drop;
    let manifold_rise: f64 = 2.0;
    let inner_limb_drop: f64 = 9.5;
    let flute_depth: f64 = shell::FLUTE_DEPTH;
    let flute_rise: f64 = shell::FLUTE_RISE;
    let flute_full_depth_height: f64 = 2.0 * flute_rise;
    let screw_clear_dia: f64 = 3.0 + (2.0 * f(fit, "slip")?);
    let head_cbore_dia: f64 = 5.5 + (2.0 * f(fit, "slip")?);
    let heatset_dia: f64 = shell::HEATSET_DIA;
    let heatset_len: f64 = 4.0;
    let heatset_long_len: f64 = shell::HEATSET_LONG_LEN;
    let heatset_depth: f64 = shell::HEATSET_DEPTH;
    let heatset_min_wall: f64 = 1.6;
    let mount_boss_dia: f64 = shell::MOUNT_BOSS_DIA;
    let boss_ligament: f64 = (mount_boss_dia - heatset_dia) / 2.0;
    let mount_bore_relief: f64 = shell::MOUNT_BORE_RELIEF;
    let relief_chamfer: f64 = shell::RELIEF_CHAMFER;
    let display_bezel_x: f64 = 113.5;
    let display_bezel_slope: f64 = 77.0;
    let display_corner_r: f64 = 2.5;
    let display_inset_lap: f64 = 3.0;
    let display_inset_reach: f64 = 6.3;
    let display_inset_depth: f64 = 3.84;
    let display_inset_x: f64 = display_bezel_x + (2.0 * display_inset_reach);
    let display_inset_slope: f64 = 83.3;
    let display_cover_corner_r: f64 = show_edge_r;
    let display_cover_slip: f64 = 0.3;
    let display_inset_corner_r: f64 = display_cover_corner_r + f(fit, "slip")?;
    let display_bezel_depth: f64 = 5.84;
    let display_cover_thickness: f64 = 3.84;
    ensure!(
        boss_ligament >= heatset_min_wall,
        "an M3 mounting boss needs ruthex's minimum surrounding wall"
    );
    Ok(json!({
        "z_seam":z_seam,
        "slide_slip":slide_slip,
        "wall":wall,
        "ceiling_skin":ceiling_skin,
        "extrusion_w":extrusion_w,
        "rear_seam_clear":rear_seam_clear,
        "funnel_collar_air":funnel_collar_air,
        "y_stack_high_depth":y_stack_high_depth,
        "rear_plane_y":rear_plane_y,
        "co2_axis_drop":co2_axis_drop,
        "show_edge_r":show_edge_r,
        "show_corner_r":show_corner_r,
        "pump_station_lead":pump_station_lead,
        "pump_station_drop":pump_station_drop,
        "pump_seated_drop":pump_seated_drop,
        "manifold_rise":manifold_rise,
        "inner_limb_drop":inner_limb_drop,
        "flute_depth":flute_depth,
        "flute_rise":flute_rise,
        "flute_full_depth_height":flute_full_depth_height,
        "screw_clear_dia":screw_clear_dia,
        "head_cbore_dia":head_cbore_dia,
        "heatset_dia":heatset_dia,
        "heatset_len":heatset_len,
        "heatset_long_len":heatset_long_len,
        "heatset_depth":heatset_depth,
        "heatset_min_wall":heatset_min_wall,
        "mount_boss_dia":mount_boss_dia,
        "boss_ligament":boss_ligament,
        "mount_bore_relief":mount_bore_relief,
        "relief_chamfer":relief_chamfer,
        "display_bezel_x":display_bezel_x,
        "display_bezel_slope":display_bezel_slope,
        "display_corner_r":display_corner_r,
        "display_inset_lap":display_inset_lap,
        "display_inset_reach":display_inset_reach,
        "display_inset_depth":display_inset_depth,
        "display_inset_x":display_inset_x,
        "display_inset_slope":display_inset_slope,
        "display_cover_corner_r":display_cover_corner_r,
        "display_cover_slip":display_cover_slip,
        "display_inset_corner_r":display_inset_corner_r,
        "display_bezel_depth":display_bezel_depth,
        "display_cover_thickness":display_cover_thickness
    }))
}

fn namespace(v: &Value) -> Result<Value> {
    let wall: f64 = f(&v["interface"], "wall")?;
    let pump_station_lead: f64 = f(&v["interface"], "pump_station_lead")?;
    let pump_station_drop: f64 = f(&v["interface"], "pump_station_drop")?;
    let floor_t: f64 = shell::FLOOR_T;
    let floor_drop: f64 = f(v, "clearance_sliding_floor")?;
    let slab_t: f64 = floor_t - floor_drop;
    let rear_seam_clear: f64 = f(&v["interface"], "rear_seam_clear")?;
    let front_seam_clear: f64 = 3.0;
    let corner_round: f64 = f(&v["interface"], "show_corner_r")?;
    let piece_print_up =
        json!({"front-top": 1.0, "front-bottom": 1.0, "back-bottom": 1.0, "back-top": -1.0});
    let back_top_up: f64 = f(&piece_print_up, "back-top")?;
    let column_round: f64 = corner_round;
    let column_corners = json!(shell::COLUMN_CORNERS.map(|(sx, sy)| [sx as i64, sy as i64]));
    let flute_count: f64 = shell::FLUTE_COUNT;
    let flute_depth: f64 = f(&v["interface"], "flute_depth")?;
    let flute_backing: f64 = wall;
    let flute_samples: f64 = 13.0;
    let flute_rise: f64 = f(&v["interface"], "flute_rise")?;
    let flute_full_depth_height: f64 = f(&v["interface"], "flute_full_depth_height")?;
    let flute_fade_steps: f64 = 12.0;
    let flute_pitch_drift: f64 = 0.15;
    let disposal_lines = json!(shell::DISPOSAL_LINES);
    let disposal_font = shell::DISPOSAL_FONT;
    let disposal_kind = "bold";
    let disposal_cap_height: f64 = shell::DISPOSAL_CAP_HEIGHT;
    let disposal_raise: f64 = shell::DISPOSAL_RAISE;
    let disposal_embed: f64 = shell::DISPOSAL_EMBED;
    let disposal_line_gap: f64 = shell::DISPOSAL_LINE_GAP;
    let disposal_bottom: f64 = shell::DISPOSAL_BOTTOM;
    let disposal_margin: f64 = shell::DISPOSAL_MARGIN;
    let h2c_x: f64 = 325.0;
    let h2c_y: f64 = 320.0;
    let h2c_z: f64 = 320.0;
    let display_bezel_x: f64 = f(&v["interface"], "display_bezel_x")?;
    let display_bezel_slope: f64 = f(&v["interface"], "display_bezel_slope")?;
    let display_bezel_cut_x: f64 = display_bezel_x + (2.0 * f(&v["fits"], "slip")?);
    let display_bezel_cut_slope: f64 = display_bezel_slope + (2.0 * f(&v["fits"], "slip")?);
    let display_body_offset_x: f64 = 0.5;
    let display_body_offset_slope: f64 = -1.0;
    let display_corner_r: f64 = f(&v["interface"], "display_corner_r")?;
    let display_inset_lap: f64 = f(&v["interface"], "display_inset_lap")?;
    let display_inset_reach: f64 = f(&v["interface"], "display_inset_reach")?;
    let display_inset_depth: f64 = f(&v["interface"], "display_inset_depth")?;
    let display_inset_x: f64 = f(&v["interface"], "display_inset_x")?;
    let display_inset_slope: f64 = f(&v["interface"], "display_inset_slope")?;
    let display_facet_buffer: f64 = 2.25;
    let display_facet_x: f64 = display_inset_x + (2.0 * display_facet_buffer);
    let display_facet_slope: f64 = f(&v["swept"], "FLAT")?;
    let display_facet_angle_deg: f64 = f(&v["swept"], "ANGLE")?;
    let display_facet_thickness: f64 = 19.0;
    let display_bezel_depth: f64 = f(&v["interface"], "display_bezel_depth")?;
    let display_pcb_x: f64 = 106.0 + (2.0 * f(&v["fits"], "slip")?);
    let display_pcb_slope: f64 = 69.0 + (2.0 * f(&v["fits"], "slip")?);
    let display_pcb_cut_through: f64 =
        ((display_bezel_depth + 17.0) + 1.0) - display_facet_thickness;
    let ridge_wall_t: f64 = 3.0;
    let cable_sleeve_nom: f64 = 12.7;
    let cable_bore_air: f64 = 1.0;
    let cable_bore_dia: f64 = cable_sleeve_nom + (2.0 * cable_bore_air);
    let display_loom_x_offset: f64 = 32.0;
    let display_cover_thickness: f64 = f(&v["interface"], "display_cover_thickness")?;
    let display_cover_slip: f64 = f(&v["interface"], "display_cover_slip")?;
    let funnel_band_gap: f64 = 1.0;
    let funnel_collar_air: f64 = f(&v["interface"], "funnel_collar_air")?;
    let funnel_front_y: f64 =
        f(&v["funnel_frame"], "center_y")? - (f(&v["funnel"], "collar_d")? / 2.0);
    let funnel_seat_thickness: f64 = f(&v["swept"], "FUNNEL_SEAT")?;
    let ceiling_skin: f64 = f(&v["interface"], "ceiling_skin")?;
    let ceiling_lip_drop: f64 =
        (funnel_seat_thickness + f(&v["funnel"], "brim_thickness")?) - ceiling_skin;
    let y_stack_axis_in: f64 = shell::Y_STACK_AXIS_IN;
    let y_stack_lower_axis_in: f64 = shell::Y_STACK_LOWER_AXIS_IN;
    let y_stack_high_depth: f64 = f(&v["interface"], "y_stack_high_depth")?;
    let y_stack_front_root: f64 = shell::Y_STACK_FRONT_ROOT;
    let y_stack_clearance_dia: f64 = f(&v["fits"], "m5_thread_pass_dia")?;
    let y_stack_cbore_dia: f64 = shell::Y_STACK_CBORE_DIA;
    let y_stack_head_recess: f64 = shell::Y_STACK_HEAD_RECESS;
    let y_stack_head_h: f64 = shell::Y_STACK_HEAD_H;
    let y_stack_cbore_depth: f64 = shell::Y_STACK_CBORE_DEPTH;
    let y_stack_tip_clearance: f64 = shell::Y_STACK_TIP_CLEARANCE;
    let y_stack_screw_length_tolerance: f64 = shell::Y_STACK_SCREW_LENGTH_TOLERANCE;
    let y_stack_upper_chamfer: f64 = shell::Y_STACK_UPPER_CHAMFER;
    let lower_rod_len: f64 = shell::LOWER_ROD_LEN;
    let upper_rod_len: f64 = shell::UPPER_ROD_LEN;
    let y_stack_lower_anchor_face_drop: f64 = shell::Y_STACK_LOWER_ANCHOR_FACE_DROP;
    let y_stack_lower_plane_over_seat: f64 = shell::Y_STACK_LOWER_PLANE_OVER_SEAT;
    let y_stack_upper_datum: f64 = shell::Y_STACK_UPPER_DATUM;
    let y_stack_upper_head_datum: f64 = shell::Y_STACK_UPPER_HEAD_DATUM;
    let screw_clear_dia: f64 = f(&v["interface"], "screw_clear_dia")?;
    let head_cbore_dia: f64 = f(&v["interface"], "head_cbore_dia")?;
    let heatset_dia: f64 = f(&v["interface"], "heatset_dia")?;
    let heatset_len: f64 = f(&v["interface"], "heatset_len")?;
    let heatset_long_len: f64 = f(&v["interface"], "heatset_long_len")?;
    let heatset_depth: f64 = f(&v["interface"], "heatset_depth")?;
    let socket_cap: f64 = wall;
    let handhold_y: f64 = shell::HANDHOLD_Y;
    let handhold_length: f64 = shell::HANDHOLD_LENGTH;
    let handhold_height: f64 = shell::HANDHOLD_HEIGHT;
    let handhold_wall: f64 = shell::HANDHOLD_WALL;
    let handhold_roof: f64 = shell::HANDHOLD_ROOF;
    let handhold_corner_r: f64 = shell::HANDHOLD_CORNER_R;
    let handhold_edge_r: f64 = shell::HANDHOLD_EDGE_R;
    let mount_boss_dia: f64 = f(&v["interface"], "mount_boss_dia")?;
    let boss_ligament: f64 = f(&v["interface"], "boss_ligament")?;
    let east_boss_corbel_clear: f64 = 1.0;
    let east_knurl_entry_r: f64 = 2.5;
    let east_boss_joint_air: f64 = 0.5;
    let east_boss_min_stand: f64 = boss_ligament;
    let mount_bar_reach: f64 = 20.0;
    let mount_bore_relief: f64 = f(&v["interface"], "mount_bore_relief")?;
    let floor_heatset_dia: f64 = shell::FLOOR_HEATSET_DIA;
    let floor_heatset_depth: f64 = shell::FLOOR_HEATSET_DEPTH;
    let floor_heatset_min_wall: f64 = shell::FLOOR_HEATSET_MIN_WALL;
    let wago_well_wall: f64 = shell::WAGO_WELL_WALL;
    let wago_well_press: f64 = f(&v["fits"], "slip")?;
    let wago_roof_tab: f64 = 2.0;
    let wago_lever_clear: f64 = 1.0;
    let wago_pitch: f64 = (2.0 * wago_half(v, "413", wago_well_wall, wago_well_press)?[0])
        .max(wago_swing(v, "413")? + wago_lever_clear);
    let mq6_rail_wall: f64 = shell::MQ6_RAIL_WALL;
    let mq6_slot_press: f64 = f(&v["fits"], "running")?;
    let mq6_grip: f64 = shell::MQ6_GRIP;
    let mq6_header_relief: f64 = shell::MQ6_HEADER_RELIEF;
    let mq6_card_x: f64 = f(&v["mq6"], "PCB_T")?;
    let mq6_card_y: f64 = f(&v["mq6"], "PCB_X")?;
    let mq6_card_z: f64 = f(&v["mq6"], "PCB_Y")?;
    let mq6_can_yz: f64 = f(&v["mq6"], "CAN_D")?;
    let cond_rail_wall: f64 = shell::COND_RAIL_WALL;
    let cond_slot_grip: f64 = shell::COND_SLOT_GRIP;
    let cond_mount_clear: f64 = 1.0;
    let cond_slot_press: f64 = f(&v["fits"], "running")?;
    let cond_vent_clear: f64 = shell::COND_VENT_CLEAR;
    let cond_vent_probe: f64 = shell::COND_VENT_PROBE;
    let cond_vent_island_min: f64 = shell::COND_VENT_ISLAND_MIN as f64;
    let cond_fan_rise: f64 = shell::COND_FAN_RISE;
    let cond_fan_drop: f64 = shell::COND_FAN_DROP;
    let cond_vent_transoms: f64 = shell::COND_VENT_TRANSOMS as f64;
    let cond_vent_transom_h: f64 = shell::COND_VENT_TRANSOM_H;
    let core_stop_slip: f64 = 2.0 * f(&v["fits"], "running")?;
    let core_stop_web: f64 = shell::CORE_STOP_WEB;
    let core_stop_rise: f64 = shell::CORE_STOP_RISE;
    let core_hold_reach: f64 = shell::CORE_HOLD_REACH;
    let core_hold_land: f64 = shell::CORE_HOLD_LAND;
    let core_hold_rise: f64 = shell::CORE_HOLD_RISE;
    let cond_screw_len: f64 = shell::COND_SCREW_LEN;
    let cond_bore_depth: f64 = shell::COND_BORE_DEPTH;
    let cond_boss_t: f64 = shell::COND_BOSS_T;
    let mount_boss_out: f64 = heatset_depth + mount_bore_relief;
    let side_band_inset: f64 = shell::SIDE_BAND_INSET;
    let y_stack_low_depth: f64 = shell::y_stack_low_depth();
    let lip_len: f64 = shell::LIP_LEN;
    let appliance_height: f64 = shell::APPLIANCE_HEIGHT;
    let appliance_width: f64 = shell::APPLIANCE_WIDTH;
    let stated_bound_tol: f64 = shell::STATED_BOUND_TOL;
    let rear_plane_y: f64 = f(&v["interface"], "rear_plane_y")?;
    let back_top_wall_t: f64 = shell::BACK_TOP_WALL_T;
    let c14_station_x: f64 = array(&v["c14_pose"], "translation_mm")?[0]
        .as_f64()
        .ok_or_else(|| anyhow!("pose coordinate"))?;
    let back_top_port_row_z: f64 = array(&v["layout_spec"]["fluid_grid"], "rows_z_mm")?
        .iter()
        .map(|x| x.as_f64().ok_or_else(|| anyhow!("rear row Z")))
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .max_by(f64::total_cmp)
        .ok_or_else(|| anyhow!("rear rows"))?;
    let co2_axis_drop: f64 = 0.0;
    let c14_fit_extra: f64 = 0.5;
    let c14_cord_extra_x: f64 = 3.0;
    let c14_bore_w: f64 = (24.3 + (2.0 * c14_fit_extra)) + c14_cord_extra_x;
    let c14_bore_h: f64 = 18.3 + (2.0 * c14_fit_extra);
    let c14_bore_r: f64 = 1.5;
    let c14_pocket_w: f64 = rear_wall::c14::FLANGE_W;
    let c14_pocket_h: f64 = 22.17;
    let c14_pocket_end_chord: f64 = rear_wall::c14::FLANGE_END_CHORD;
    let c14_pocket_knuckle_r: f64 = rear_wall::c14::KNUCKLE_R;
    let c14_screw_pitch: f64 = 40.0;
    let c14_pocket_depth: f64 = 5.0;
    let c14_wall_relief_w: f64 =
        2.0 * (((c14_screw_pitch / 2.0) + (heatset_dia / 2.0)) + boss_ligament);
    let c14_wall_relief_h: f64 = c14_bore_h + (2.0 * back_top_wall_t);
    let back_top_wall_reliefs = json!([]);
    let station_land_draft: f64 = 2.0;
    let c14_tunnel_len: f64 = heatset_depth;
    let c14_tunnel_wall: f64 = back_top_wall_t;
    let c14_pocket_slip: f64 = f(&v["fits"], "slip")? + c14_fit_extra;
    let c14_pocket_wall: f64 = 3.0;
    let c14_insertion_relief: f64 = 9.0;
    let c14_pocket_overcut: f64 = 1.0;
    let back_top_flank_t: f64 = shell::BACK_TOP_FLANK_T;
    let back_bottom_flank_t: f64 = shell::BACK_BOTTOM_FLANK_T;
    let front_bottom_flank_t: f64 = shell::FRONT_BOTTOM_FLANK_T;
    let back_top_ceiling_t: f64 = shell::BACK_TOP_CEILING_T;
    let back_top_ceiling_growth: f64 = back_top_ceiling_t - ceiling_skin;
    let front_wall: f64 = shell::FRONT_WALL;
    let front_plane_y: f64 = shell::FRONT_PLANE_Y;
    let pump_show_growth: f64 = flute_depth;
    let fridge_reliefs = json!(shell::FRIDGE_RELIEFS);
    let pump_relief_skin: f64 = 3.9;
    let pump_cartridge_front_y: f64 = front_plane_y - front_wall;
    let pump_station_front_y: f64 = pump_cartridge_front_y + pump_show_growth;
    let pump_relief_floor: f64 = pump_station_front_y + pump_relief_skin;
    let relief_chamfer: f64 = f(&v["interface"], "relief_chamfer")?;
    let front_top_flank_t: f64 = shell::FRONT_TOP_FLANK_T;
    let y_seam: f64 = shell::Y_SEAM;
    let z_seam: f64 = f(&v["interface"], "z_seam")?;
    let z_joint_clear: f64 = 3.0;
    let z_lip_y_margin: f64 = shell::Z_LIP_Y_MARGIN;
    let slide_slip: f64 = f(&v["interface"], "slide_slip")?;
    let hook_foot: f64 = shell::HOOK_FOOT;
    let hook_lap: f64 = shell::HOOK_LAP;
    let front_hook_lap: f64 = shell::FRONT_HOOK_LAP;
    let back_hook_lap: f64 = shell::BACK_HOOK_LAP;
    let z_rise: f64 = shell::Z_RISE;
    let hook_arm: f64 = shell::HOOK_ARM;
    let rail_stop_len: f64 = shell::RAIL_STOP_LEN;
    let rail_entry: f64 = shell::RAIL_ENTRY;
    let rail_lead: f64 = shell::RAIL_LEAD;
    let rail_flare_drop: f64 = shell::rail_flare_drop();
    let rail_reach_in: f64 =
        (((front_top_flank_t).max(back_top_flank_t) - wall) + slide_slip) + hook_arm;
    let bay_crown_air: f64 = 1.7;
    let pump_bay_floor_relief: f64 = shell::shell().pump_bay_floor_relief;
    let pump_bay_roof_relief: f64 = 2.5;
    let pump_relief_z_air: f64 = shell::shell().pump_relief_z_air;
    let pump_cartridge_z_clearance: f64 = shell::shell().pump_cartridge_z_clearance;
    let pump_cartridge_top_clearance: f64 = f(&v["fits"], "running")?;
    let pump_bay_floor_air: f64 = f(v, "clearance_sliding_floor")?;
    let pump_bay_side_air: f64 = f(&v["fits"], "running")?;
    let cap_kiss: f64 = shell::shell().cap_kiss;
    let cap_kiss_station_allowance: f64 = shell::shell().cap_kiss_station_allowance;
    let plate_foot_reach: f64 = shell::PLATE_FOOT_REACH;
    let plate_foot_y: f64 = shell::PLATE_FOOT_Y;
    let plate_foot_t: f64 = shell::PLATE_FOOT_T;
    let plate_foot_corbel_angle: f64 = shell::PLATE_FOOT_CORBEL_ANGLE;
    let cap_pump_air: f64 = shell::shell().cap_pump_air;
    let cap_boss_air: f64 = shell::shell().cap_boss_air;
    let cap_fitting_half: f64 = f(&v["tray"], "shaft_w")? / 2.0;
    let mut out = serde_json::Map::new();
    out.insert("wall".into(), json!(wall));
    out.insert("pump_station_lead".into(), json!(pump_station_lead));
    out.insert("pump_station_drop".into(), json!(pump_station_drop));
    out.insert("floor_t".into(), json!(floor_t));
    out.insert("floor_drop".into(), json!(floor_drop));
    out.insert("slab_t".into(), json!(slab_t));
    out.insert("rear_seam_clear".into(), json!(rear_seam_clear));
    out.insert("front_seam_clear".into(), json!(front_seam_clear));
    out.insert("corner_round".into(), json!(corner_round));
    out.insert("PIECE_PRINT_UP".into(), json!(piece_print_up));
    out.insert("BACK_TOP_UP".into(), json!(back_top_up));
    out.insert("column_round".into(), json!(column_round));
    out.insert("column_corners".into(), json!(column_corners));
    out.insert("flute_count".into(), json!(flute_count as i64));
    out.insert("flute_depth".into(), json!(flute_depth));
    out.insert("flute_backing".into(), json!(flute_backing));
    out.insert("flute_samples".into(), json!(flute_samples as i64));
    out.insert("flute_rise".into(), json!(flute_rise));
    out.insert(
        "flute_full_depth_height".into(),
        json!(flute_full_depth_height),
    );
    out.insert("flute_fade_steps".into(), json!(flute_fade_steps as i64));
    out.insert("flute_pitch_drift".into(), json!(flute_pitch_drift));
    out.insert("disposal_lines".into(), json!(disposal_lines));
    out.insert("disposal_font".into(), json!(disposal_font));
    out.insert("disposal_kind".into(), json!(disposal_kind));
    out.insert("disposal_cap_height".into(), json!(disposal_cap_height));
    out.insert("disposal_raise".into(), json!(disposal_raise));
    out.insert("disposal_embed".into(), json!(disposal_embed));
    out.insert("disposal_line_gap".into(), json!(disposal_line_gap));
    out.insert("disposal_bottom".into(), json!(disposal_bottom));
    out.insert("disposal_margin".into(), json!(disposal_margin));
    out.insert("H2C_X".into(), json!(h2c_x));
    out.insert("H2C_Y".into(), json!(h2c_y));
    out.insert("H2C_Z".into(), json!(h2c_z));
    out.insert("display_bezel_x".into(), json!(display_bezel_x));
    out.insert("display_bezel_slope".into(), json!(display_bezel_slope));
    out.insert("display_bezel_cut_x".into(), json!(display_bezel_cut_x));
    out.insert(
        "display_bezel_cut_slope".into(),
        json!(display_bezel_cut_slope),
    );
    out.insert("display_body_offset_x".into(), json!(display_body_offset_x));
    out.insert(
        "display_body_offset_slope".into(),
        json!(display_body_offset_slope),
    );
    out.insert("display_corner_r".into(), json!(display_corner_r));
    out.insert("display_inset_lap".into(), json!(display_inset_lap));
    out.insert("display_inset_reach".into(), json!(display_inset_reach));
    out.insert("display_inset_depth".into(), json!(display_inset_depth));
    out.insert("display_inset_x".into(), json!(display_inset_x));
    out.insert("display_inset_slope".into(), json!(display_inset_slope));
    out.insert("display_facet_buffer".into(), json!(display_facet_buffer));
    out.insert("display_facet_x".into(), json!(display_facet_x));
    out.insert("display_facet_slope".into(), json!(display_facet_slope));
    out.insert(
        "display_facet_angle_deg".into(),
        json!(display_facet_angle_deg),
    );
    out.insert(
        "display_facet_thickness".into(),
        json!(display_facet_thickness),
    );
    out.insert("display_bezel_depth".into(), json!(display_bezel_depth));
    out.insert("display_pcb_x".into(), json!(display_pcb_x));
    out.insert("display_pcb_slope".into(), json!(display_pcb_slope));
    out.insert(
        "display_pcb_cut_through".into(),
        json!(display_pcb_cut_through),
    );
    out.insert("ridge_wall_t".into(), json!(ridge_wall_t));
    out.insert("cable_sleeve_nom".into(), json!(cable_sleeve_nom));
    out.insert("cable_bore_air".into(), json!(cable_bore_air));
    out.insert("cable_bore_dia".into(), json!(cable_bore_dia));
    out.insert("display_loom_x_offset".into(), json!(display_loom_x_offset));
    out.insert(
        "display_cover_thickness".into(),
        json!(display_cover_thickness),
    );
    out.insert("display_cover_slip".into(), json!(display_cover_slip));
    out.insert("funnel_band_gap".into(), json!(funnel_band_gap));
    out.insert("funnel_collar_air".into(), json!(funnel_collar_air));
    out.insert("funnel_front_y".into(), json!(funnel_front_y));
    out.insert("funnel_seat_thickness".into(), json!(funnel_seat_thickness));
    out.insert("ceiling_skin".into(), json!(ceiling_skin));
    out.insert("ceiling_lip_drop".into(), json!(ceiling_lip_drop));
    out.insert("y_stack_axis_in".into(), json!(y_stack_axis_in));
    out.insert("y_stack_lower_axis_in".into(), json!(y_stack_lower_axis_in));
    out.insert("y_stack_high_depth".into(), json!(y_stack_high_depth));
    out.insert("y_stack_front_root".into(), json!(y_stack_front_root));
    out.insert("y_stack_clearance_dia".into(), json!(y_stack_clearance_dia));
    out.insert("y_stack_cbore_dia".into(), json!(y_stack_cbore_dia));
    out.insert("y_stack_head_recess".into(), json!(y_stack_head_recess));
    out.insert("y_stack_head_h".into(), json!(y_stack_head_h));
    out.insert("y_stack_cbore_depth".into(), json!(y_stack_cbore_depth));
    out.insert("y_stack_tip_clearance".into(), json!(y_stack_tip_clearance));
    out.insert(
        "y_stack_screw_length_tolerance".into(),
        json!(y_stack_screw_length_tolerance),
    );
    out.insert("y_stack_upper_chamfer".into(), json!(y_stack_upper_chamfer));
    out.insert("lower_rod_len".into(), json!(lower_rod_len));
    out.insert("upper_rod_len".into(), json!(upper_rod_len));
    out.insert(
        "y_stack_lower_anchor_face_drop".into(),
        json!(y_stack_lower_anchor_face_drop),
    );
    out.insert(
        "y_stack_lower_plane_over_seat".into(),
        json!(y_stack_lower_plane_over_seat),
    );
    out.insert("y_stack_upper_datum".into(), json!(y_stack_upper_datum));
    out.insert(
        "y_stack_upper_head_datum".into(),
        json!(y_stack_upper_head_datum),
    );
    out.insert("screw_clear_dia".into(), json!(screw_clear_dia));
    out.insert("head_cbore_dia".into(), json!(head_cbore_dia));
    out.insert("heatset_dia".into(), json!(heatset_dia));
    out.insert("heatset_len".into(), json!(heatset_len));
    out.insert("heatset_long_len".into(), json!(heatset_long_len));
    out.insert("heatset_depth".into(), json!(heatset_depth));
    out.insert("socket_cap".into(), json!(socket_cap));
    out.insert("handhold_y".into(), json!(handhold_y));
    out.insert("handhold_length".into(), json!(handhold_length));
    out.insert("handhold_height".into(), json!(handhold_height));
    out.insert("handhold_wall".into(), json!(handhold_wall));
    out.insert("handhold_roof".into(), json!(handhold_roof));
    out.insert("handhold_corner_r".into(), json!(handhold_corner_r));
    out.insert("handhold_edge_r".into(), json!(handhold_edge_r));
    out.insert("mount_boss_dia".into(), json!(mount_boss_dia));
    out.insert("boss_ligament".into(), json!(boss_ligament));
    out.insert(
        "east_boss_corbel_clear".into(),
        json!(east_boss_corbel_clear),
    );
    out.insert("east_knurl_entry_r".into(), json!(east_knurl_entry_r));
    out.insert("east_boss_joint_air".into(), json!(east_boss_joint_air));
    out.insert("east_boss_min_stand".into(), json!(east_boss_min_stand));
    out.insert("mount_bar_reach".into(), json!(mount_bar_reach));
    out.insert("mount_bore_relief".into(), json!(mount_bore_relief));
    out.insert("floor_heatset_dia".into(), json!(floor_heatset_dia));
    out.insert("floor_heatset_depth".into(), json!(floor_heatset_depth));
    out.insert(
        "floor_heatset_min_wall".into(),
        json!(floor_heatset_min_wall),
    );
    out.insert("wago_well_wall".into(), json!(wago_well_wall));
    out.insert("wago_well_press".into(), json!(wago_well_press));
    out.insert("wago_roof_tab".into(), json!(wago_roof_tab));
    out.insert("wago_lever_clear".into(), json!(wago_lever_clear));
    out.insert("wago_pitch".into(), json!(wago_pitch));
    out.insert("mq6_rail_wall".into(), json!(mq6_rail_wall));
    out.insert("mq6_slot_press".into(), json!(mq6_slot_press));
    out.insert("mq6_grip".into(), json!(mq6_grip));
    out.insert("mq6_header_relief".into(), json!(mq6_header_relief));
    out.insert("mq6_card_x".into(), json!(mq6_card_x));
    out.insert("mq6_card_y".into(), json!(mq6_card_y));
    out.insert("mq6_card_z".into(), json!(mq6_card_z));
    out.insert("mq6_can_yz".into(), json!(mq6_can_yz));
    out.insert("cond_rail_wall".into(), json!(cond_rail_wall));
    out.insert("cond_slot_grip".into(), json!(cond_slot_grip));
    out.insert("cond_mount_clear".into(), json!(cond_mount_clear));
    out.insert("cond_slot_press".into(), json!(cond_slot_press));
    out.insert("cond_vent_clear".into(), json!(cond_vent_clear));
    out.insert("cond_vent_probe".into(), json!(cond_vent_probe));
    out.insert(
        "cond_vent_island_min".into(),
        json!(cond_vent_island_min as i64),
    );
    out.insert("cond_fan_rise".into(), json!(cond_fan_rise));
    out.insert("cond_fan_drop".into(), json!(cond_fan_drop));
    out.insert(
        "cond_vent_transoms".into(),
        json!(cond_vent_transoms as i64),
    );
    out.insert("cond_vent_transom_h".into(), json!(cond_vent_transom_h));
    out.insert("core_stop_slip".into(), json!(core_stop_slip));
    out.insert("core_stop_web".into(), json!(core_stop_web));
    out.insert("core_stop_rise".into(), json!(core_stop_rise));
    out.insert("core_hold_reach".into(), json!(core_hold_reach));
    out.insert("core_hold_land".into(), json!(core_hold_land));
    out.insert("core_hold_rise".into(), json!(core_hold_rise));
    out.insert("cond_screw_len".into(), json!(cond_screw_len));
    out.insert("cond_bore_depth".into(), json!(cond_bore_depth));
    out.insert("cond_boss_t".into(), json!(cond_boss_t));
    out.insert("mount_boss_out".into(), json!(mount_boss_out));
    out.insert("side_band_inset".into(), json!(side_band_inset));
    out.insert("y_stack_low_depth".into(), json!(y_stack_low_depth));
    out.insert("lip_len".into(), json!(lip_len));
    out.insert("appliance_height".into(), json!(appliance_height));
    out.insert("appliance_width".into(), json!(appliance_width));
    out.insert("stated_bound_tol".into(), json!(stated_bound_tol));
    out.insert("rear_plane_y".into(), json!(rear_plane_y));
    out.insert("back_top_wall_t".into(), json!(back_top_wall_t));
    out.insert("c14_station_x".into(), json!(c14_station_x));
    out.insert("back_top_port_row_z".into(), json!(back_top_port_row_z));
    out.insert("co2_axis_drop".into(), json!(co2_axis_drop));
    out.insert("c14_fit_extra".into(), json!(c14_fit_extra));
    out.insert("c14_cord_extra_x".into(), json!(c14_cord_extra_x));
    out.insert("c14_bore_w".into(), json!(c14_bore_w));
    out.insert("c14_bore_h".into(), json!(c14_bore_h));
    out.insert("c14_bore_r".into(), json!(c14_bore_r));
    out.insert("c14_pocket_w".into(), json!(c14_pocket_w));
    out.insert("c14_pocket_h".into(), json!(c14_pocket_h));
    out.insert("c14_pocket_end_chord".into(), json!(c14_pocket_end_chord));
    out.insert("c14_pocket_knuckle_r".into(), json!(c14_pocket_knuckle_r));
    out.insert("c14_screw_pitch".into(), json!(c14_screw_pitch));
    out.insert("c14_pocket_depth".into(), json!(c14_pocket_depth));
    out.insert("c14_wall_relief_w".into(), json!(c14_wall_relief_w));
    out.insert("c14_wall_relief_h".into(), json!(c14_wall_relief_h));
    out.insert("back_top_wall_reliefs".into(), json!(back_top_wall_reliefs));
    out.insert("station_land_draft".into(), json!(station_land_draft));
    out.insert("c14_tunnel_len".into(), json!(c14_tunnel_len));
    out.insert("c14_tunnel_wall".into(), json!(c14_tunnel_wall));
    out.insert("c14_pocket_slip".into(), json!(c14_pocket_slip));
    out.insert("c14_pocket_wall".into(), json!(c14_pocket_wall));
    out.insert("c14_insertion_relief".into(), json!(c14_insertion_relief));
    out.insert("c14_pocket_overcut".into(), json!(c14_pocket_overcut));
    out.insert("back_top_flank_t".into(), json!(back_top_flank_t));
    out.insert("back_bottom_flank_t".into(), json!(back_bottom_flank_t));
    out.insert("front_bottom_flank_t".into(), json!(front_bottom_flank_t));
    out.insert("back_top_ceiling_t".into(), json!(back_top_ceiling_t));
    out.insert(
        "back_top_ceiling_growth".into(),
        json!(back_top_ceiling_growth),
    );
    out.insert("front_wall".into(), json!(front_wall));
    out.insert("front_plane_y".into(), json!(front_plane_y));
    out.insert("pump_show_growth".into(), json!(pump_show_growth));
    out.insert("fridge_reliefs".into(), json!(fridge_reliefs));
    out.insert("pump_relief_skin".into(), json!(pump_relief_skin));
    out.insert(
        "pump_cartridge_front_y".into(),
        json!(pump_cartridge_front_y),
    );
    out.insert("pump_station_front_y".into(), json!(pump_station_front_y));
    out.insert("pump_relief_floor".into(), json!(pump_relief_floor));
    out.insert("relief_chamfer".into(), json!(relief_chamfer));
    out.insert("front_top_flank_t".into(), json!(front_top_flank_t));
    out.insert("y_seam".into(), json!(y_seam));
    out.insert("z_seam".into(), json!(z_seam));
    out.insert("z_joint_clear".into(), json!(z_joint_clear));
    out.insert("z_lip_y_margin".into(), json!(z_lip_y_margin));
    out.insert("slide_slip".into(), json!(slide_slip));
    out.insert("hook_foot".into(), json!(hook_foot));
    out.insert("hook_lap".into(), json!(hook_lap));
    out.insert("front_hook_lap".into(), json!(front_hook_lap));
    out.insert("back_hook_lap".into(), json!(back_hook_lap));
    out.insert("z_rise".into(), json!(z_rise));
    out.insert("hook_arm".into(), json!(hook_arm));
    out.insert("rail_stop_len".into(), json!(rail_stop_len));
    out.insert("rail_entry".into(), json!(rail_entry));
    out.insert("rail_lead".into(), json!(rail_lead));
    out.insert("rail_flare_drop".into(), json!(rail_flare_drop));
    out.insert("rail_reach_in".into(), json!(rail_reach_in));
    out.insert("bay_crown_air".into(), json!(bay_crown_air));
    out.insert("pump_bay_floor_relief".into(), json!(pump_bay_floor_relief));
    out.insert("pump_bay_roof_relief".into(), json!(pump_bay_roof_relief));
    out.insert("pump_relief_z_air".into(), json!(pump_relief_z_air));
    out.insert(
        "pump_cartridge_z_clearance".into(),
        json!(pump_cartridge_z_clearance),
    );
    out.insert(
        "pump_cartridge_top_clearance".into(),
        json!(pump_cartridge_top_clearance),
    );
    out.insert("pump_bay_floor_air".into(), json!(pump_bay_floor_air));
    out.insert("pump_bay_side_air".into(), json!(pump_bay_side_air));
    out.insert("cap_kiss".into(), json!(cap_kiss));
    out.insert(
        "cap_kiss_station_allowance".into(),
        json!(cap_kiss_station_allowance),
    );
    out.insert("plate_foot_reach".into(), json!(plate_foot_reach));
    out.insert("plate_foot_y".into(), json!(plate_foot_y));
    out.insert("plate_foot_t".into(), json!(plate_foot_t));
    out.insert(
        "plate_foot_corbel_angle".into(),
        json!(plate_foot_corbel_angle),
    );
    out.insert("cap_pump_air".into(), json!(cap_pump_air));
    out.insert("cap_boss_air".into(), json!(cap_boss_air));
    out.insert("cap_fitting_half".into(), json!(cap_fitting_half));
    Ok(Value::Object(out))
}

pub fn dispatch(v: &Value) -> Result<Value> {
    match text(v, "op")? {
        "core-interface" => interface(v),
        "core-namespace" => namespace(v),
        "core-flute-reach" => {
            let d = &v["values"];
            let t = (f(v, "band_height")? / 2.).min(f(d, "flute_rise")?) / f(d, "flute_rise")?;
            Ok(json!(f(d, "flute_depth")? * t * t * (3. - 2. * t)))
        }
        "core-wago-stand" => Ok(json!(wago_stand(v, text(v, "size")?)?)),
        "core-wago-engage" => Ok(json!(wago_stand(v, text(v, "size")?)?[2] / 2.)),
        "core-wago-half" => Ok(json!(wago_half(
            v,
            text(v, "size")?,
            f(v, "wall")?,
            f(v, "press")?
        )?)),
        "core-wago-swing" => Ok(json!(wago_swing(v, text(v, "size")?)?)),
        _ => Err(anyhow!("unknown enclosure core dimension operation")),
    }
}
