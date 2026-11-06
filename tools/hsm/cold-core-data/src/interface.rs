//! The cold core's interface numbers, handed to its generated recipes: the casing stock, mating
//! extents, clamp stack and source-frame port datums from `hsm-cold-core-interface`, and the
//! stated bounds they settle.

use anyhow::{Context, Result};
use hsm_cold_core_interface as c;
use serde_json::{Value, json};

/// The fits a request names.
pub fn fits(value: &Value) -> Result<c::Fits> {
    Ok(c::Fits {
        slip: super::number(value, "slip")?,
        running: super::number(value, "running")?,
        supported_surface: super::number(value, "supported_surface")?,
        m5_thread_pass_dia: super::number(value, "m5_thread_pass_dia")?,
    })
}

/// The fits the generated interface module holds, as the numbers take them.
pub fn module_fits(value: &crate::compiled::Val) -> Result<c::Fits> {
    use crate::compiled::Val;
    let number = |name: &str| value.get(Val::Str(name.into()))?.num();
    Ok(c::Fits {
        slip: number("slip")?,
        running: number("running")?,
        supported_surface: number("supported_surface")?,
        m5_thread_pass_dia: number("m5_thread_pass_dia")?,
    })
}

/// A point as the generated recipes hold one.
pub fn tuple(xy: &[f64]) -> crate::compiled::Val {
    use crate::compiled::Val;
    Val::tuple(xy.iter().map(|v| Val::Float(*v)).collect())
}

fn ports(ports: &[(i64, [f64; 2])]) -> Value {
    Value::Object(ports.iter().map(|(side, xy)| (side.to_string(), json!(xy))).collect())
}

/// One side's reservoir conduit in the cap's frame: the cap installs spun a half turn.
pub fn reservoir_conduit(kind: &str, side: i64) -> Result<Value> {
    let table = match kind {
        "fill" => &c::RESERVOIR_FILL_PORT,
        "draw" => &c::RESERVOIR_DRAW_PORT,
        _ => anyhow::bail!("unknown reservoir conduit {kind}"),
    };
    let xy = c::reservoir_port(table, side).context("unknown reservoir side")?;
    Ok(json!([-xy[0], -xy[1]]))
}

pub fn base(fits_value: &Value) -> Result<Value> {
    let f = &fits(fits_value)?;
    let attachment_stations = c::attachment_stations();
    let lid_attachment_stations = c::lid_attachment_stations();
    let fmt = super::formatted;
    let states = json!([
        [
            "forward-band-takes-a-bore",
            "The forward band still passes a line",
            format!(
                "{} >= {} mm",
                fmt(c::FORWARD_BAND_WIDTH, "g"),
                fmt(c::PASSAGE_TUBE_OD, "g")
            ),
            c::FORWARD_BAND_WIDTH >= c::PASSAGE_TUBE_OD,
            format!(
                "the open routing band is {} mm wide for the {} mm measured tube; enlarged bores cross printed walls and caps",
                fmt(c::FORWARD_BAND_WIDTH, "g"),
                fmt(c::PASSAGE_TUBE_OD, "g")
            )
        ],
        [
            "cap-screw-reach",
            "The clamp screw reaches the whole of its insert",
            format!("{} mm past the shell face", fmt(c::INSERT_LENGTH, "g")),
            c::cap_screw_beyond_face(f) >= c::INSERT_LENGTH,
            format!(
                "an M5 × {} reaches {} mm past the shell face, short of its {} mm insert",
                fmt(c::CAP_SCREW_LENGTH, "g"),
                fmt(c::cap_screw_beyond_face(f), "g"),
                fmt(c::INSERT_LENGTH, "g")
            )
        ],
        [
            "cap-screw-bottom",
            "The clamp screw pulls its head down before it bottoms",
            format!(
                "{} mm past the shell face at most",
                fmt(c::bottom_screw_bore_depth(f), "g")
            ),
            c::cap_screw_beyond_face(f) <= c::bottom_screw_bore_depth(f),
            format!(
                "an M5 × {} reaches {} mm past the shell face and bottoms in a {} mm tail passage before its head is down",
                fmt(c::CAP_SCREW_LENGTH, "g"),
                fmt(c::cap_screw_beyond_face(f), "g"),
                fmt(c::bottom_screw_bore_depth(f), "g")
            )
        ]
    ]);
    Ok(json!({
        "wall_thickness": c::WALL_THICKNESS, "floor_thickness": c::FLOOR_THICKNESS,
        "wall_and_floor_thickness": c::WALL_AND_FLOOR_THICKNESS,
        "hole_shift_from_edge": c::HOLE_SHIFT_FROM_EDGE,
        "outer_shell_wall": c::OUTER_SHELL_WALL, "coil_radial_clearance": c::COIL_RADIAL_CLEARANCE,
        "carbonator_coil_envelope_radius": c::CARBONATOR_COIL_ENVELOPE_RADIUS,
        "pocket_centerward_arc_outer_radius": c::POCKET_CENTERWARD_ARC_OUTER_RADIUS,
        "foam_thickness_around_cylinder": c::FOAM_THICKNESS_AROUND_CYLINDER,
        "below_carbonator_elbows_height": c::BELOW_CARBONATOR_ELBOWS_HEIGHT,
        "above_carbonator_elbows_height": c::ABOVE_CARBONATOR_ELBOWS_HEIGHT,
        "foam_shell_outer_height": c::FOAM_SHELL_OUTER_HEIGHT,
        "carbonator_support_ring_height": c::CARBONATOR_SUPPORT_RING_HEIGHT,
        "support_ring_radial_width": c::SUPPORT_RING_RADIAL_WIDTH,
        "passage_tube_od": c::PASSAGE_TUBE_OD, "port_hole_radius": c::PORT_HOLE_RADIUS,
        "reed_x_depth": c::REED_X_DEPTH, "reed_y_half_w": c::REED_Y_HALF_W,
        "level_rod_y": c::LEVEL_ROD_Y,
        "bag_pocket_far_inner_x": c::BAG_POCKET_FAR_INNER_X,
        "bag_pocket_y_inner_max": c::BAG_POCKET_Y_INNER_MAX,
        "bag_pocket_width": c::BAG_POCKET_WIDTH, "bag_pocket_depth": c::BAG_POCKET_DEPTH,
        "bag_pocket_floor_top_z": c::BAG_POCKET_FLOOR_TOP_Z,
        "bag_pocket_walls_top_z": c::BAG_POCKET_WALLS_TOP_Z,
        "reed_channel_inner_x": c::REED_CHANNEL_INNER_X,
        "reed_column_axis_x": c::REED_COLUMN_AXIS_X,
        "reservoir_clearance": c::reservoir_clearance(f),
        "bag_pocket_corner_inner_radius": c::bag_pocket_corner_inner_radius(f),
        "reservoir_floor_thickness": c::RESERVOIR_FLOOR_THICKNESS,
        "reservoir_fill_port": ports(&c::RESERVOIR_FILL_PORT),
        "reservoir_fill_sides": c::RESERVOIR_FILL_SIDES,
        "reservoir_draw_port": ports(&c::RESERVOIR_DRAW_PORT),
        "casing_foil_allowance": c::CASING_FOIL_ALLOWANCE, "casing_foil_land": c::CASING_FOIL_LAND,
        "outer_shell_x_length": c::OUTER_SHELL_X_LENGTH,
        "outer_shell_y_length": c::OUTER_SHELL_Y_LENGTH,
        "seam_channel_land": c::SEAM_CHANNEL_LAND, "seam_channel_width": c::SEAM_CHANNEL_WIDTH,
        "seam_channel_depth": c::SEAM_CHANNEL_DEPTH,
        "bag_pocket_outermost_x": c::BAG_POCKET_OUTERMOST_X,
        "outer_shell_foam_gap": c::OUTER_SHELL_FOAM_GAP,
        "forward_band_width": c::FORWARD_BAND_WIDTH, "forward_band_mid_x": c::FORWARD_BAND_MID_X,
        "pour_band_pocket_side_y": c::POUR_BAND_POCKET_SIDE_Y,
        "pour_band_shell_side_y": c::POUR_BAND_SHELL_SIDE_Y,
        "foam_cap_interior_height": c::FOAM_CAP_INTERIOR_HEIGHT,
        "foam_cap_height": c::FOAM_CAP_HEIGHT,
        "foam_cap_lid_pour_radius": c::FOAM_CAP_LID_POUR_RADIUS,
        "foam_cap_lid_vent_radius": c::FOAM_CAP_LID_VENT_RADIUS,
        "foam_cap_lid_hole_inset": c::FOAM_CAP_LID_HOLE_INSET,
        "top_lid_pour_xy": c::TOP_LID_POUR_XY, "top_lid_vent_setback": c::TOP_LID_VENT_SETBACK,
        "carbonator_port_offset": c::CARBONATOR_PORT_OFFSET,
        "carbonator_sensor_azimuth": c::CARBONATOR_SENSOR_AZIMUTH,
        "carbonator_sensor_axis": c::CARBONATOR_SENSOR_AXIS,
        "carbonator_float_top_stop_height": c::CARBONATOR_FLOAT_TOP_STOP_HEIGHT,
        "carbonator_float_top_stop_diameter": c::CARBONATOR_FLOAT_TOP_STOP_DIAMETER,
        "co2_inlet_y": c::CO2_INLET_Y, "co2_inlet_tube_radius": c::CO2_INLET_TUBE_RADIUS,
        "water_inlet_port_y": c::WATER_INLET_PORT_Y, "prv_port_y": c::PRV_PORT_Y,
        "cap_shell_clearance": c::cap_shell_clearance(f),
        "cap_lid_clearance": c::cap_lid_clearance(f),
        "screw_clearance_radius": c::screw_clearance_radius(f),
        "insert_pocket_radius": c::INSERT_POCKET_RADIUS,
        "insert_pocket_depth": c::INSERT_POCKET_DEPTH,
        "screw_boss_size": c::SCREW_BOSS_SIZE, "screw_guard_diameter": c::SCREW_GUARD_DIAMETER,
        "screw_head_height": c::SCREW_HEAD_HEIGHT, "head_seat_recess": c::head_seat_recess(f),
        "head_cbore_radius": c::HEAD_CBORE_RADIUS, "head_cbore_depth": c::head_cbore_depth(f),
        "head_pad_height": c::head_pad_height(f), "head_pad_slip": c::head_pad_slip(f),
        "foam_cap_lid_height": c::foam_cap_lid_height(f),
        "top_lid_bottom_z": c::top_lid_bottom_z(f),
        "foam_shell_rim_z": c::foam_shell_rim_z(f), "bottom_cap_height": c::bottom_cap_height(f),
        "bottom_pour_radius": c::BOTTOM_POUR_RADIUS,
        "bottom_pour_positions": c::bottom_pour_positions(),
        "front_wall_x": c::FRONT_WALL_X, "port_lane_outer_y": c::PORT_LANE_OUTER_Y,
        "port_lane_inner_y": c::PORT_LANE_INNER_Y, "port_lane_mid_y": c::PORT_LANE_MID_Y,
        "west_lane_mid_y": c::WEST_LANE_MID_Y, "evap_tail_low_z": c::EVAP_TAIL_LOW_Z,
        "evap_tail_high_z": c::EVAP_TAIL_HIGH_Z, "corner_round_radius": c::CORNER_ROUND_RADIUS,
        "_boss_wall_y": c::BOSS_WALL_Y, "_boss_wall_x": c::BOSS_WALL_X,
        "mid_screw_x_offset": c::MID_SCREW_X_OFFSET,
        "attachment_stations": attachment_stations,
        "attachment_xy_positions": attachment_stations.iter().map(|row| row.0).collect::<Vec<_>>(),
        "lid_attachment_stations": lid_attachment_stations,
        "lid_attachment_xy_positions":
            lid_attachment_stations.iter().map(|row| row.0).collect::<Vec<_>>(),
        "cap_screw_length": c::CAP_SCREW_LENGTH, "insert_length": c::INSERT_LENGTH,
        "cap_screw_beyond_face": c::cap_screw_beyond_face(f),
        "top_lid_screw_beyond_face": c::top_lid_screw_beyond_face(f),
        "cap_screw_tip_air": c::CAP_SCREW_TIP_AIR,
        "bottom_screw_bore_depth": c::bottom_screw_bore_depth(f),
        "top_screw_bore_depth": c::top_screw_bore_depth(f),
        "deck_mount_boss_radius": c::DECK_MOUNT_BOSS_RADIUS,
        "deck_mount_bore_radius": c::DECK_MOUNT_BORE_RADIUS,
        "deck_mount_lid_slip": c::deck_mount_lid_slip(f),
        "deck_mount_insert_length": c::DECK_MOUNT_INSERT_LENGTH,
        "deck_mount_bore_relief": c::DECK_MOUNT_BORE_RELIEF,
        "deck_mount_cap_gap": c::DECK_MOUNT_CAP_GAP,
        "_states": states
    }))
}
