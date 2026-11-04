//! Display cover dimensions and their tip-frame construction recipes.

use crate::formatted;
use anyhow::{Context, Result};
use serde_json::{Value, json};

pub fn snap() -> Value {
    json!({"ENGAGEMENT":1.2,"RADIAL_SLIP":0.0,"X_PRELOAD":1.25,
           "BEARING_SLIP":0.48,"END_SLIP":0.30,"END_MARGIN":3.0,
           "LIP_HEIGHT":3.0,"LIP_INNER_EDGE_RELIEF":0.25})
}

fn f(values: &Value, key: &str) -> Result<f64> {
    values[key]
        .as_f64()
        .with_context(|| format!("no numeric {key} in display source"))
}
fn merge(base: &Value, overlay: Value) -> Value {
    let mut out = base.as_object().cloned().unwrap_or_default();
    out.extend(overlay.as_object().cloned().unwrap_or_default());
    Value::Object(out)
}

pub fn consumer(request: &Value) -> Result<Value> {
    let shell = &request["shell"];
    let s = |key| f(shell, key);
    let plate_n_top = s("display_cover_top_n")?;
    let bezel_n_bottom = s("display_face_n")? + 0.10;
    let bezel_thickness = plate_n_top - bezel_n_bottom;
    let window_half_x = 24.50 / 2.0 - 2.0;
    let window_s_south = s("display_s_bottom")? + s("display_cradle_clearance")? + 2.0;
    let window_s_north = s("display_s_top")? - s("display_cradle_clearance")? - 2.0;
    let window_corner_r = 5.75 - 2.0;
    let window_x = 2.0 * window_half_x;
    let window_s = window_s_north - window_s_south;
    let front_rim_n = 14.0;
    let front_rim_slope = 1.8;
    let rear_skirt_extension = 1.2;
    let rear_trim_s0 = 42.1;
    let rear_trim_ds_dn = 0.6;
    let outer_clamp = [
        30.0,
        s("display_head_s_min")?,
        s("display_head_s_max")? + rear_skirt_extension + 1.0,
        -30.0,
        40.0,
    ];
    let cavity_clamp = [
        50.0,
        s("dispense_face_thickness")?,
        s("display_head_s_max")? + 1.0,
        -30.0,
        40.0,
    ];
    let lip_band = [
        s("display_cover_skirt_width")? / 2.0 + 1.0,
        s("display_clip_s_bottom")?,
        s("display_clip_s_top")?,
        s("display_clip_bottom_n")?,
        s("display_clip_top_n")?,
    ];
    let skirt_width = s("display_cover_skirt_width")?;
    let skirt_length = s("display_cover_skirt_length")? + rear_skirt_extension;
    let skirt_r = s("display_cover_skirt_r")?;
    let skirt_s = s("_display_cover_center_s")? + rear_skirt_extension / 2.0;
    let outer_rows = [
        [
            skirt_width,
            skirt_length,
            skirt_r,
            s("display_cover_bottom_n")?,
            skirt_s,
        ],
        [
            skirt_width,
            skirt_length,
            skirt_r,
            s("display_cover_shoulder_n")?,
            skirt_s,
        ],
        [
            s("display_cover_face_width")?,
            s("display_cover_face_length")?,
            s("display_cover_face_r")?,
            plate_n_top,
            s("_display_cover_center_s")?,
        ],
    ];
    let window_n = [bezel_n_bottom - 0.1, plate_n_top + 1.0];
    let wing_slope = 1.25 / (bezel_n_bottom - s("display_clip_top_n")?);
    let preload = |n: f64| {
        (1.25 * (bezel_n_bottom - n)
            / (bezel_n_bottom - s("display_clip_top_n").expect("clip top")))
        .max(0.0)
    };
    let mut cavity_rows = shell["display_cover_inner_rows"]
        .as_array()
        .context("cover cavity rows")?
        .clone();
    for row in &mut cavity_rows {
        row.as_array_mut()
            .context("cover cavity row")?
            .push(json!(s("_display_housing_center_s")?));
    }
    let numbers = merge(
        &request["shell_numbers"],
        json!({
            "name":"faucet-display-cover",
            "names":{"cover":"faucet-display-cover","seated":"faucet-display-cover-seated"},
            "cover_outer_rows":outer_rows,"cover_outer_clamp":outer_clamp,
            "cover_cavity_rows":cavity_rows,
            "cover_cavity_clamps":[shell["display_cover_inner_clamp"],cavity_clamp],
            "cover_window_half_x":window_half_x,"cover_window_s":[window_s_south,window_s_north],
            "cover_window_n":window_n,"cover_window_corner_r":window_corner_r,
            "cover_neck_clearance_r":s("display_neck_outer_r")?+s("display_cover_slip")?,
            "cover_front_rim":[front_rim_n,front_rim_slope],"cover_rear_trim":[rear_trim_s0,rear_trim_ds_dn],
            "cover_lip_band":lip_band,
            "cover_lip_r":s("display_neck_outer_r")?-(s("display_neck_outer_r")?-s("display_clip_lip_radius")?),
            "cover_lip_relief":0.25,"cover_bezel_n":bezel_n_bottom,"cover_wing_slope":wing_slope,
        }),
    );
    let variables = formatted(&[
        ("PLATE_X", s("display_cover_face_width")?, "g", " mm"),
        ("PLATE_S", s("display_cover_face_length")?, "g", " mm"),
        ("WINDOW_X", window_x, "g", " mm"),
        ("WINDOW_S", window_s, "g", " mm"),
        ("COVER_OVER_FACE", 0.10, "g", " mm"),
        ("COSMETIC_WALL", bezel_thickness, "g", " mm"),
        ("DISPENSE_FACE_T", s("dispense_face_thickness")?, "g", " mm"),
        ("SNAP_ENGAGEMENT", 1.2, "g", " mm"),
        ("LIP_HEIGHT", 3.0, "g", " mm"),
        ("WING_PRELOAD", 1.25, "g", " mm"),
        (
            "WING_BOTTOM_PRELOAD",
            preload(s("display_clip_bottom_n")?),
            ".3f",
            " mm",
        ),
        ("GROOVE_DEPTH", 1.2 + 0.0, "g", " mm"),
        ("GROOVE_ROOF_CLEARANCE", 0.48, "g", " mm"),
        ("GROOVE_END_CLEARANCE", 0.30, "g", " mm"),
        ("LIP_INNER_EDGE_RELIEF", 0.25, "g", " mm"),
        ("DISPLAY_FEET_N", s("display_feet_n")?, "g", " mm"),
        (
            "DISPLAY_INSTALL_LIFT",
            s("display_cartridge_lift_n")?,
            "g",
            " mm",
        ),
        ("FOOT_PAD_WIDTH", s("display_foot_pad_width")?, "g", " mm"),
        ("FOOT_PAD_DEPTH", s("display_foot_pad_depth")?, "g", " mm"),
        ("REAR_SKIRT_EXT", rear_skirt_extension, "g", " mm"),
        ("REAR_TRIM_S0", rear_trim_s0, "g", " mm"),
        ("REAR_TRIM_DS_DN", rear_trim_ds_dn, "g", ""),
    ]);
    Ok(json!({"datums":{
        "plate_n_top":plate_n_top,"bezel_n_bottom":bezel_n_bottom,"bezel_thickness":bezel_thickness,
        "window_half_x":window_half_x,"window_s_south":window_s_south,"window_s_north":window_s_north,
        "window_corner_r":window_corner_r,"window_x":window_x,"window_s":window_s,
        "front_rim_n":front_rim_n,"front_rim_slope":front_rim_slope,
        "rear_skirt_extension":rear_skirt_extension,"rear_trim_s0":rear_trim_s0,"rear_trim_ds_dn":rear_trim_ds_dn,
        "outer_clamp":outer_clamp,"cavity_clamp":cavity_clamp,"lip_band":lip_band,
    },"numbers":numbers,"variables":variables,"outer_rows":outer_rows,"window_n":window_n,
    "wing_slope":wing_slope,"preload":request["preload_n"].as_f64().map(preload)}))
}

pub fn industrial_cover(request: &Value) -> Result<Value> {
    let shell = &request["shell"];
    let s = |key| f(shell, key);
    let defaults = json!({"width":29.8,"length":49.75,"upper_side_wall":s("wall_thickness_min")?,
        "lower_side_wall":1.25,"rear_wall":s("wall_thickness_min")?,"front_wall":s("dispense_face_thickness")?,
        "n_bottom":s("display_cover_bottom_n")?,"wing_extension_mm":0.50});
    let dimensions = if request["dimensions"].is_object() {
        &request["dimensions"]
    } else {
        &defaults
    };
    let d = |key| f(dimensions, key);
    let n_top = s("display_cover_top_n")? + d("wing_extension_mm")?;
    let bezel_n_bottom = s("display_face_n")? + 0.10 + d("wing_extension_mm")?;
    let bezel_thickness = n_top - bezel_n_bottom;
    let window_half_x = 24.50 / 2.0 - 2.0;
    let window_s_south = s("display_s_bottom")? + s("display_cradle_clearance")? + 2.0;
    let window_s_north = s("display_s_top")? - s("display_cradle_clearance")? - 2.0;
    let window_corner_r = 5.75 - 2.0;
    let wing_slope = 1.25 / (bezel_n_bottom - s("display_clip_top_n")?);
    let preload = |n: f64| {
        (1.25 * (bezel_n_bottom - n)
            / (bezel_n_bottom - s("display_clip_top_n").expect("clip top")))
        .max(0.0)
    };
    let upper_half_x = d("width")? / 2.0 - d("upper_side_wall")?;
    let lower_half_x = (upper_half_x + preload(s("display_feet_n")?))
        .min(d("width")? / 2.0 - d("lower_side_wall")?);
    let sections = [
        [lower_half_x, d("n_bottom")? - 1.0],
        [lower_half_x, s("display_feet_n")?],
        [upper_half_x, bezel_n_bottom],
    ];
    let window_n = [bezel_n_bottom - 0.1, n_top + 1.0];
    Ok(
        json!({"defaults":defaults,"n_top":n_top,"bezel_n_bottom":bezel_n_bottom,
        "datums":{"plate_n_top":n_top,"bezel_n_bottom":bezel_n_bottom,"bezel_thickness":bezel_thickness,
            "window_half_x":window_half_x,"window_s_south":window_s_south,"window_s_north":window_s_north,
            "window_corner_r":window_corner_r,"window_x":2.0*window_half_x,"window_s":window_s_north-window_s_south,
            "display_head_s_min":0.0,"display_head_s_max":d("length")?},
        "cavity_sections":sections,"window_n":window_n,"wing_slope":wing_slope,
        "preload":request["preload_n"].as_f64().map(preload),
        "numbers":{"cover_half_x":d("width")?/2.0,"cover_length":d("length")?,
            "cover_n":[d("n_bottom")?,n_top],
            "cover_cavity_s":[d("front_wall")?,d("length")?-d("rear_wall")?],
            "cover_cavity_sections":sections,"cover_window_half_x":window_half_x,
            "cover_window_s":[window_s_south,window_s_north],"cover_window_n":window_n,"cover_window_corner_r":window_corner_r,
            "cover_neck_clearance_r":s("display_neck_outer_r")?+s("display_cover_slip")?,
            "cover_arch_lift":d("wing_extension_mm")?,
            "cover_lip_r":s("display_neck_outer_r")?-(s("display_neck_outer_r")?-s("display_clip_lip_radius")?),
            "cover_lip_relief":0.25,"cover_bezel_n":bezel_n_bottom,"cover_wing_slope":wing_slope}}),
    )
}

pub fn industrial_body(request: &Value) -> Result<Value> {
    let shell = &request["shell"];
    let s = |key| f(shell, key);
    let wall = s("wall_thickness_min")?;
    let foot_radius = s("foot_width")?.max(s("foot_depth")?) / 2.0;
    let foot_top = 14.0;
    let body_center_y = 5.4;
    let signal_turn_stock_allowance = 1.0;
    let body_radius =
        s("westbrass_bore_diameter")? / 2.0 + body_center_y + wall + signal_turn_stock_allowance;
    let body_top = s("zone4_z_top")?;
    let neck_center_y = s("soda_faucet_tube_y")? + s("tube_shell_center_y")?;
    let neck_radius = s("tube_shell_outer_r")?;
    let neck_join_z = s("zone5_z_top")?;
    let neck_join_overlap = 0.2;
    let pieces = json!({"base":"industrial-shell-base","cover":"industrial-display-cover",
        "plate":"industrial-above-counter-plate","gasket":"industrial-above-counter-gasket"});
    let mut numbers = merge(&request["shell_numbers"], request["cover_numbers"].clone());
    let mut names = pieces.clone();
    names["seated"] = json!("industrial-display-cover-seated");
    let plate = &request["plate"];
    let gasket = &request["gasket"];
    let extra = json!({"name":"industrial-faucet","names":names,"gasket_color":request["gasket_color"],
        "foot_radius":foot_radius,"foot_top":foot_top,"body_radius":body_radius,
        "body_center_y":body_center_y,"body_top":body_top,"neck_radius":neck_radius,
        "neck_center_y":neck_center_y,"neck_join_overlap":neck_join_overlap,
        "plate_z":plate["plate_z_range"],"gasket_z":gasket["gasket_z_range"],
        "base_pedestal_dia":shell["base_pedestal_dia"],"base_pedestal_height":shell["base_pedestal_height"],
        "base_pedestal_chamfer":shell["base_pedestal_chamfer"],"base_pod_shank_dia":shell["base_pod_shank_dia"],
        "base_pod_counterbore_dia":shell["base_pod_counterbore_dia"],"base_screw_counterbore_depth":shell["base_screw_counterbore_depth"],
        "shank_hole_center":plate["shank_hole_center"],"shank_hole_radius":plate["shank_hole_radius"],"pill_slot_center":plate["pill_slot_center"]});
    numbers = merge(&numbers, extra);
    Ok(
        json!({"datums":{"wall":wall,"foot_radius":foot_radius,"foot_top":foot_top,
        "body_center_y":body_center_y,"signal_turn_stock_allowance":signal_turn_stock_allowance,
        "body_radius":body_radius,"body_top":body_top,"neck_center_y":neck_center_y,
        "neck_radius":neck_radius,"neck_join_z":neck_join_z,"neck_join_overlap":neck_join_overlap},
        "pieces":pieces,"numbers":numbers}),
    )
}
