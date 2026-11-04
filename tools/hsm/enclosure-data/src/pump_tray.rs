//! Pump collar stock, outlet joins and dimension reports.
use super::{array, f, text};
use anyhow::{Result, anyhow, ensure};
use serde_json::{Value, json};

fn defaults(v: &Value) -> Result<Value> {
    let p = &v["pump"];
    let c = &v["case"];
    let fit = &v["fits"];
    let head_half: f64 = f(p, "head_w")? / 2.0;
    let head_depth: f64 = 48.88;
    let head_front_z: f64 = f(p, "head_front_z")?;
    let head_front_below_skirt: f64 = f(p, "head_front_below_skirt")?;
    let boss_half: f64 = f(c, "bore_half_span")?;
    let boss_depth: f64 = f(c, "bore_bottom_z")?;
    let can_half: f64 = f(c, "cylinder_id")? / 2.0;
    let bracket_half: f64 = f(p, "bracket_w")? / 2.0;
    let bracket_t: f64 = f(p, "bracket_t")?;
    let motor_crown: f64 = f(p, "motor_end_z")?;
    let rear_axis_y_shift: f64 = f(p, "rear_axis_y_shift")?;
    let outlet_relief: f64 = f(p, "outlet_relief")?;
    let outlet_relief_run: f64 = f(p, "outlet_relief_run")?;
    let outlet_half: f64 = f(p, "outlet_span_x")? / 2.0;
    let outlet_pitch: f64 = f(p, "barb_pitch")?;
    let fitting_w: f64 = f(p, "tube_casing_w")?;
    let shaft_w: f64 = fitting_w + (2.0 * f(fit, "running")?);
    let outlet_open_half: f64 = (outlet_pitch + shaft_w) / 2.0;
    let skirt_depth: f64 = f(p, "skirt_depth")?;
    let skirt_support_air: f64 = f(fit, "running")?;
    let skirt_support_band: f64 = f(c, "skirt_support_band")?;
    let skirt_body_y: f64 = f(p, "skirt_body_y")?;
    let skirt_support_xy_air: f64 = f(fit, "running")?;
    let skirt_body_open_y: f64 = skirt_body_y + (2.0 * skirt_support_xy_air);
    let skirt_body_open_y_bounds = [
        (f(p, "skirt_body_y_min")? - skirt_support_xy_air),
        (f(p, "skirt_body_y_max")? + skirt_support_xy_air),
    ];
    let skirt_y: f64 = f(p, "skirt_y")?;
    let skirt_y_plus_air: f64 = f(p, "skirt_y_plus_air")?;
    let skirt_open_y_max: f64 = f(p, "skirt_y_max")? + skirt_y_plus_air;
    let skirt_upper_band: f64 = f(p, "skirt_upper_band")?;
    let skirt_support_y_minus: f64 =
        (f(p, "skirt_support_y_minus")? - skirt_support_xy_air) + f(p, "skirt_support_xy_air")?;
    let skirt_support_y_plus: f64 = skirt_open_y_max - skirt_body_open_y_bounds[1];
    let outlet_axis_z: f64 = f(c, "skirt_bottom_z")?;
    let case_half: f64 = f(c, "footprint_half_extent")?;
    let plate: f64 = f(c, "base_thickness")?;
    let shoulder: f64 = 3.0;
    Ok(json!({
        "head_half":head_half,
        "head_depth":head_depth,
        "head_front_z":head_front_z,
        "head_front_below_skirt":head_front_below_skirt,
        "boss_half":boss_half,
        "boss_depth":boss_depth,
        "can_half":can_half,
        "bracket_half":bracket_half,
        "bracket_t":bracket_t,
        "motor_crown":motor_crown,
        "rear_axis_y_shift":rear_axis_y_shift,
        "outlet_relief":outlet_relief,
        "outlet_relief_run":outlet_relief_run,
        "outlet_half":outlet_half,
        "outlet_pitch":outlet_pitch,
        "fitting_w":fitting_w,
        "shaft_w":shaft_w,
        "outlet_open_half":outlet_open_half,
        "skirt_depth":skirt_depth,
        "skirt_support_air":skirt_support_air,
        "skirt_support_band":skirt_support_band,
        "skirt_body_y":skirt_body_y,
        "skirt_support_xy_air":skirt_support_xy_air,
        "skirt_body_open_y":skirt_body_open_y,
        "skirt_body_open_y_bounds":skirt_body_open_y_bounds,
        "skirt_y":skirt_y,
        "skirt_y_plus_air":skirt_y_plus_air,
        "skirt_open_y_max":skirt_open_y_max,
        "skirt_upper_band":skirt_upper_band,
        "skirt_support_y_minus":skirt_support_y_minus,
        "skirt_support_y_plus":skirt_support_y_plus,
        "outlet_axis_z":outlet_axis_z,
        "case_half":case_half,
        "PLATE":plate,
        "SHOULDER":shoulder
    }))
}

fn depth(v: &Value) -> Result<f64> {
    Ok(f(&v["stock"], "boss_depth")? + f(&v["stock"], "SHOULDER")?)
}

fn passage(v: &Value) -> Result<f64> {
    let c = &v["case"];
    let offset = f(c, "skirt_wall")? - f(v, "air")?;
    Ok(f(c, "skirt_transition_y_end_plus")? + offset * (2_f64.sqrt() - 1.))
}

fn miter(v: &Value) -> Result<[f64; 4]> {
    let body =
        f(&v["case"], "skirt_wide_half_extent")? - (f(&v["case"], "skirt_wall")? - f(v, "air")?);
    let open = f(&v["stock"], "outlet_open_half")?;
    ensure!(
        open >= body - 1e-9,
        "the {} mm tube opening is narrower than the {} mm case-derived outlet room",
        hsm_documents::format_number(2. * open, "g")?,
        hsm_documents::format_number(2. * body, "g")?
    );
    let y0 = passage(v)?;
    Ok([body, y0, open, y0 + (open - body)])
}

fn tangent(v: &Value) -> Result<[f64; 4]> {
    let body = miter(v)?[0];
    let stock = &v["stock"];
    let c = &v["case"];
    let r = f(stock, "shaft_w")? / 2.;
    let seam = f(c, "skirt_bottom_z")? - f(c, "lower_footprint_straight")?;
    let wall = body - f(stock, "outlet_pitch")? / 2.;
    let rise = f(stock, "outlet_axis_z")? - seam;
    let reach = wall * wall + rise * rise;
    ensure!(
        reach > r * r,
        "the room edge stands {} mm off a tube axis, inside its {} mm opening — no tangent plane joins the seam to the circle",
        hsm_documents::format_number(reach.sqrt(), ".3f")?,
        hsm_documents::format_number(r, "g")?
    );
    let run = (reach - r * r).sqrt();
    let u = r * (r * wall + run * rise) / reach;
    let z = f(stock, "outlet_axis_z")? + r * (run * wall - r * rise) / reach;
    Ok([seam, wall, u, z])
}

fn recipe(v: &Value) -> Result<Value> {
    let c = &v["case"];
    let s = &v["stock"];
    let p = &v["pump"];
    let arc = c["arc_segments"]
        .as_u64()
        .ok_or_else(|| anyhow!("case arc segments is an integer"))? as usize;
    let footprint = super::pump_case::rounded(
        f(c, "footprint_x")?,
        f(c, "footprint_y")?,
        f(c, "corner_r")?,
        arc,
    )?;
    let ramp_end = super::pump_case::rounded(
        f(c, "footprint_x")? - 2. * f(c, "ramp_from_skirt_to_octagon_height")?,
        f(c, "footprint_y")? - 2. * f(c, "ramp_from_skirt_to_octagon_height")?,
        f(c, "corner_r")?,
        arc,
    )?;
    let trays = v["trays"]
        .as_object()
        .ok_or_else(|| anyhow!("trays is a mapping"))?
        .iter()
        .map(|(name, root)| json!([name, root]))
        .collect::<Vec<_>>();
    Ok(
        json!({"ramp_sections":[[0.,footprint],[c["base_thickness"],footprint],[c["bore_bottom_z"],ramp_end]],
        "bore_wall":c["bore_wall_profile"],"bore":c["bore_profile"],
        "bore_depth":c["bore_depth"],"boss_depth":s["boss_depth"],
        "tower_start":c["cylinder_top_z"],"tower_end":c["cylinder_bottom_z"],
        "tower_outer_radius":c["cylinder_r_outer"],"tower_inner_radius":c["cylinder_r_inner"],
        "tower_bore_start":f(c,"bore_bottom_z")?-f(c,"overcut")?,
        "tower_bore_end":f(c,"bore_bottom_z")?+f(c,"tower_height")?-f(c,"tower_cap_thickness")?,
        "rear_axis_y_shift":s["rear_axis_y_shift"],"half_width":s["case_half"],
        "far_reach":s["case_half"],"depth":depth(v)?,"plate":c["base_thickness"],"case_half":s["case_half"],
        "head_box":[[-f(p,"head_w")?/2.,-f(p,"head_w")?/2.,p["head_front_z"]],
                     [f(p,"head_w")?/2.,f(p,"head_w")?/2.,p["base_plane_z"]]],
        "motor_radius":f(p,"motor_dia")?/2.,"motor_end":p["motor_end_z"],"trays":trays,
        "section_stations":[0.,s["boss_depth"]],"section_rise":0.05,"section_thickness":0.02,"section_span":1e3}),
    )
}

fn shown(x: f64, spec: &str) -> Result<String> {
    hsm_documents::format_number(x, spec)
}

fn report(v: &Value) -> Result<Value> {
    let trays = v["trays"]
        .as_object()
        .ok_or_else(|| anyhow!("trays is a mapping"))?;
    let rows = array(&v["measured"], "trays")?;
    let s = &v["stock"];
    let c = &v["case"];
    let p = &v["pump"];
    let mut lines = vec![format!(
        "Pump clamp collar — {} fused into the top clamp: {}",
        trays.len(),
        trays.keys().cloned().collect::<Vec<_>>().join(", ")
    )];
    let mut total = 0.;
    let mut storey = [0., 0.];
    for row in rows {
        let name = text(row, "name")?;
        let root = trays[name]
            .as_f64()
            .ok_or_else(|| anyhow!("collar root is numeric"))?;
        total += f(row, "volume")?;
        storey = [
            row["storeys"][0]
                .as_f64()
                .ok_or_else(|| anyhow!("head storey is numeric"))?,
            row["storeys"][1]
                .as_f64()
                .ok_or_else(|| anyhow!("crown storey is numeric"))?,
        ];
        lines.push(format!(
            "  {name}: {} x {}, {} of shoulder over {} of bore, rooted {} mm off the pump's axis",
            shown(2. * f(s, "case_half")?, "g")?,
            shown(root + f(s, "case_half")?, "g")?,
            shown(f(s, "SHOULDER")?, "g")?,
            shown(f(s, "boss_depth")?, "g")?,
            shown(root, "g")?
        ));
        let valid = if row["valid"] == true {
            "True"
        } else {
            "False"
        };
        lines.push(format!(
            "    material {} cm^3, valid {valid}, fouls the pump by {} mm^3",
            shown(f(row, "volume")? / 1000., ".2f")?,
            shown(f(row, "fouled_volume")?, ".6f")?
        ));
        lines.push(format!(
            "    covers {} mm^2 on the head's crown and {} on the boss's",
            shown(storey[0], ".0f")?,
            shown(storey[1], ".0f")?
        ));
    }
    let root = trays
        .values()
        .map(|x| x.as_f64().ok_or_else(|| anyhow!("root is numeric")))
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .min_by(f64::total_cmp)
        .ok_or_else(|| anyhow!("collar report has trays"))?;
    let mut variables = serde_json::Map::new();
    for (name, x, spec) in [
        ("TRAY_W", 2. * f(s, "case_half")?, "g"),
        ("TRAY_L", root + f(s, "case_half")?, "g"),
        ("TRAY_D", depth(v)?, "g"),
        ("PLATE", f(s, "PLATE")?, "g"),
        ("SHOULDER", f(s, "SHOULDER")?, "g"),
        ("CAN_BORE", 2. * f(s, "can_half")?, "g"),
        ("TRAY_VOL", total / 1000., ".2f"),
        ("SOCKET_SPAN", 2. * f(s, "boss_half")?, "g"),
        ("SOCKET_LEDGE", f(c, "ledge_depth")?, "g"),
        ("BOSS_DEPTH", f(s, "boss_depth")?, "g"),
        ("HEAD_W", f(p, "head_w")?, "g"),
        ("HEAD_D", f(p, "head_depth")?, "g"),
        ("CAN_DIA", f(p, "motor_dia")?, "g"),
        ("BRACKET_W", 2. * f(s, "bracket_half")?, "g"),
        ("REAR_AXIS_Y_SHIFT", f(s, "rear_axis_y_shift")?.abs(), "g"),
        ("ON_HEAD", storey[0], ".0f"),
        ("ON_CROWN", storey[1], ".0f"),
        ("RAMP_H", f(c, "ramp_from_skirt_to_octagon_height")?, "g"),
        ("CASE_W", 2. * f(s, "case_half")?, "g"),
    ] {
        variables.insert(name.into(), json!(shown(x, spec)?));
    }
    variables.insert("TRAY_COUNT".into(), json!(trays.len().to_string()));
    Ok(json!({"lines":lines,"variables":variables}))
}

pub fn dispatch(v: &Value) -> Result<Value> {
    Ok(match text(v, "op")? {
        "pump-tray-defaults" => defaults(v)?,
        "pump-tray-depth" => json!(depth(v)?),
        "pump-tray-passage" => json!(passage(v)?),
        "pump-tray-miter" => json!(miter(v)?),
        "pump-tray-tangent" => json!(tangent(v)?),
        "pump-tray-recipe" => recipe(v)?,
        "pump-tray-report" => report(v)?,
        _ => return Err(anyhow!("unknown pump tray operation")),
    })
}
