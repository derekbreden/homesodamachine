//! Pump case polygonal stock and signed axial dimensions.
use super::{array, f, shown};
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_numbers::pump;
use serde_json::{Value, json};

pub fn defaults() -> Result<Value> {
    let footprint_x: f64 = pump::stock::FOOTPRINT_X;
    let footprint_y: f64 = pump::stock::FOOTPRINT_Y;
    let corner_r: f64 = pump::stock::CORNER_R;
    let wall_thickness: f64 = pump::stock::WALL_THICKNESS;
    let center_x: f64 = footprint_x / 2.0;
    let center_y: f64 = footprint_y / 2.0;
    let footprint_half_extent: f64 = footprint_x / 2.0;
    let base_thickness: f64 = pump::stock::BASE_THICKNESS;
    let ramp_from_skirt_to_octagon_height: f64 = pump::stock::RAMP_FROM_SKIRT_TO_OCTAGON_HEIGHT;
    let skirt_upper_height: f64 = pump::stock::SKIRT_UPPER_HEIGHT;
    let skirt_wall: f64 = wall_thickness;
    let skirt_wide_flare_per_side: f64 = pump::stock::SKIRT_WIDE_FLARE_PER_SIDE;
    let skirt_narrow_taper_per_side: f64 = pump::stock::SKIRT_NARROW_TAPER_PER_SIDE;
    let skirt_wide_straight_height: f64 = pump::stock::SKIRT_WIDE_STRAIGHT_HEIGHT;
    let skirt_support_band: f64 = skirt_narrow_taper_per_side;
    let bore_square_side: f64 = pump::stock::BORE_SQUARE_SIDE;
    let ledge_depth: f64 = pump::stock::LEDGE_DEPTH;
    let ledge_shelf_span: f64 = pump::stock::LEDGE_SHELF_SPAN;
    let bore_half_diag: f64 = (bore_square_side * 2.0_f64.sqrt()) / 2.0;
    let bore_half_span: f64 = pump::stock::BORE_SPAN / 2.0;
    let vertex_far: f64 = bore_half_span;
    let vertex_near: f64 = bore_half_diag - bore_half_span;
    let tower_height: f64 = pump::stock::TOWER_HEIGHT;
    let tower_cap_thickness: f64 = pump::stock::TOWER_CAP_THICKNESS;
    let cylinder_id: f64 = pump::stock::CYLINDER_ID;
    let cylinder_r_inner: f64 = cylinder_id / 2.0;
    let lower_height: f64 = pump::stock::LOWER_HEIGHT;
    let lower_cap_thickness: f64 = pump::stock::LOWER_CAP_THICKNESS;
    let lower_footprint_straight: f64 = skirt_wide_straight_height;
    let step_height: f64 = 19.0;
    let step_y_clearance: f64 = 6.0;
    let snap_zone_width: f64 = 20.0;
    let snap_wall_height: f64 = 9.0;
    let snap_deflection: f64 = 1.0;
    let arch_radius: f64 = 6.5;
    let arch_pitch: f64 = 59.75;
    let arch_hole_xs = [
        (center_x - (arch_pitch / 2.0)),
        (center_x + (arch_pitch / 2.0)),
    ];
    let snap_protrusion_per_side: f64 = pump::stock::SNAP_PROTRUSION_PER_SIDE;
    let tube_protrusion_length: f64 = pump::stock::TUBE_PROTRUSION_LENGTH;
    let case_outer_x: f64 = footprint_x + (2.0 * snap_protrusion_per_side);
    let case_outer_y: f64 =
        (footprint_y + (2.0 * skirt_wide_flare_per_side)) + tube_protrusion_length;
    let case_outer_z: f64 = ((((((base_thickness + ramp_from_skirt_to_octagon_height)
        + tower_height)
        + skirt_upper_height)
        + skirt_wide_flare_per_side)
        + skirt_wide_straight_height)
        + lower_height)
        + lower_cap_thickness;
    let cutter_half_extent: f64 = (case_outer_x.max(case_outer_y) / 2.0) + 5.0;
    let overcut: f64 = pump::stock::OVERCUT;
    let arc_segments: f64 = 8.0;
    let octagon_wall_outer_extent: f64 = vertex_far + wall_thickness;
    let bore_depth: f64 = base_thickness + ramp_from_skirt_to_octagon_height;
    let bore_bottom_z: f64 = bore_depth;
    let cylinder_cardinal_step: f64 = pump::stock::CYLINDER_CARDINAL_STEP;
    let cylinder_r_outer: f64 = octagon_wall_outer_extent + cylinder_cardinal_step;
    let cylinder_top_z: f64 = (footprint_half_extent + base_thickness) - cylinder_r_outer;
    let cylinder_bottom_z: f64 = bore_bottom_z + tower_height;
    let skirt_base_half_extent: f64 = footprint_half_extent;
    let skirt_wide_half_extent: f64 = skirt_base_half_extent + skirt_wide_flare_per_side;
    let skirt_narrow_half_extent: f64 = skirt_base_half_extent - skirt_narrow_taper_per_side;
    let skirt_wide_full_width: f64 = 2.0 * skirt_wide_half_extent;
    let skirt_narrow_full_width: f64 = 2.0 * skirt_narrow_half_extent;
    let skirt_mid_narrow_half_extent: f64 = skirt_base_half_extent - skirt_wide_flare_per_side;
    let skirt_narrow_straight_height: f64 =
        skirt_wide_straight_height - (skirt_narrow_taper_per_side - skirt_wide_flare_per_side);
    let skirt_transition_y_mid = [skirt_wide_flare_per_side, -skirt_wide_flare_per_side];
    let skirt_transition_y_end = [skirt_wide_flare_per_side, -skirt_narrow_taper_per_side];
    let skirt_transition_y_end_plus: f64 = skirt_transition_y_end[0];
    let skirt_z_steps = [
        -skirt_upper_height,
        -skirt_wide_flare_per_side,
        -(skirt_narrow_taper_per_side - skirt_wide_flare_per_side),
        -skirt_narrow_straight_height,
    ];
    let skirt_bottom_z: f64 = skirt_z_steps.iter().sum::<f64>();
    let narrow_split_z: f64 = skirt_bottom_z + step_height;
    let lower_ramp_height: f64 =
        (skirt_base_half_extent + skirt_wide_flare_per_side) - skirt_narrow_half_extent;
    let lower_cap_top_z: f64 = skirt_bottom_z - lower_height;
    let lower_cap_bottom_z: f64 = lower_cap_top_z - lower_cap_thickness;
    let pos_y_face_y: f64 = center_y + footprint_half_extent;
    let mut data = json!({
        "footprint_x":footprint_x,
        "footprint_y":footprint_y,
        "corner_r":corner_r,
        "wall_thickness":wall_thickness,
        "center_x":center_x,
        "center_y":center_y,
        "footprint_half_extent":footprint_half_extent,
        "base_thickness":base_thickness,
        "ramp_from_skirt_to_octagon_height":ramp_from_skirt_to_octagon_height,
        "skirt_upper_height":skirt_upper_height,
        "skirt_wall":skirt_wall,
        "skirt_wide_flare_per_side":skirt_wide_flare_per_side,
        "skirt_narrow_taper_per_side":skirt_narrow_taper_per_side,
        "skirt_wide_straight_height":skirt_wide_straight_height,
        "skirt_support_band":skirt_support_band,
        "bore_square_side":bore_square_side,
        "ledge_depth":ledge_depth,
        "ledge_shelf_span":ledge_shelf_span,
        "bore_half_diag":bore_half_diag,
        "bore_half_span":bore_half_span,
        "vertex_far":vertex_far,
        "vertex_near":vertex_near,
        "tower_height":tower_height,
        "tower_cap_thickness":tower_cap_thickness,
        "cylinder_id":cylinder_id,
        "cylinder_r_inner":cylinder_r_inner,
        "lower_height":lower_height,
        "lower_cap_thickness":lower_cap_thickness,
        "lower_footprint_straight":lower_footprint_straight,
        "step_height":step_height,
        "step_y_clearance":step_y_clearance,
        "snap_zone_width":snap_zone_width,
        "snap_wall_height":snap_wall_height,
        "snap_deflection":snap_deflection,
        "arch_radius":arch_radius,
        "arch_pitch":arch_pitch,
        "arch_hole_xs":arch_hole_xs,
        "snap_protrusion_per_side":snap_protrusion_per_side,
        "tube_protrusion_length":tube_protrusion_length,
        "case_outer_x":case_outer_x,
        "case_outer_y":case_outer_y,
        "case_outer_z":case_outer_z,
        "cutter_half_extent":cutter_half_extent,
        "overcut":overcut,
        "arc_segments":arc_segments,
        "octagon_wall_outer_extent":octagon_wall_outer_extent,
        "bore_depth":bore_depth,
        "bore_bottom_z":bore_bottom_z,
        "cylinder_cardinal_step":cylinder_cardinal_step,
        "cylinder_r_outer":cylinder_r_outer,
        "cylinder_top_z":cylinder_top_z,
        "cylinder_bottom_z":cylinder_bottom_z,
        "skirt_base_half_extent":skirt_base_half_extent,
        "skirt_wide_half_extent":skirt_wide_half_extent,
        "skirt_narrow_half_extent":skirt_narrow_half_extent,
        "skirt_wide_full_width":skirt_wide_full_width,
        "skirt_narrow_full_width":skirt_narrow_full_width,
        "skirt_mid_narrow_half_extent":skirt_mid_narrow_half_extent,
        "skirt_narrow_straight_height":skirt_narrow_straight_height,
        "skirt_transition_y_mid":skirt_transition_y_mid,
        "skirt_transition_y_end":skirt_transition_y_end,
        "skirt_transition_y_end_plus":skirt_transition_y_end_plus,
        "skirt_z_steps":skirt_z_steps,
        "skirt_bottom_z":skirt_bottom_z,
        "narrow_split_z":narrow_split_z,
        "lower_ramp_height":lower_ramp_height,
        "lower_cap_top_z":lower_cap_top_z,
        "lower_cap_bottom_z":lower_cap_bottom_z,
        "pos_y_face_y":pos_y_face_y
    });
    data["arc_segments"] = json!(arc_segments as u64);
    data["bore_profile"] = json!(bore(&data)?);
    data["bore_wall_profile"] = json!(offset(&points(&data["bore_profile"])?, wall_thickness)?);
    data["skirt_outer_profiles"] = json!(skirt_set(&data, 0.)?);
    data["skirt_inner_profiles"] = json!(skirt_set(&data, skirt_wall)?);
    Ok(data)
}

fn points(v: &Value) -> Result<Vec<[f64; 2]>> {
    v.as_array()
        .ok_or_else(|| anyhow!("profile is a list"))?
        .iter()
        .map(|p| {
            Ok([
                p[0].as_f64()
                    .ok_or_else(|| anyhow!("profile X is numeric"))?,
                p[1].as_f64()
                    .ok_or_else(|| anyhow!("profile Y is numeric"))?,
            ])
        })
        .collect()
}

fn bore(d: &Value) -> Result<Vec<[f64; 2]>> {
    let vf = f(d, "vertex_far")?;
    let vn = f(d, "vertex_near")?;
    let vertices = [
        [vn, vf],
        [vf, vn],
        [vf, -vn],
        [vn, -vf],
        [-vn, -vf],
        [-vf, -vn],
        [-vf, vn],
        [-vn, vf],
    ];
    let mut points = Vec::new();
    for i in 0..8 {
        let [x, y] = vertices[i];
        let [end_x, end_y] = vertices[(i + 1) % 8];
        points.push([x, y]);
        if i % 2 != 0 {
            continue;
        }
        let (dx, dy) = (end_x - x, end_y - y);
        let length = dx.hypot(dy);
        let heading = dy.atan2(dx).to_degrees();
        let (mx, my) = ((x + end_x) / 2., (y + end_y) / 2.);
        let (ux, uy) = (dx / length, dy / length);
        let (mut nx, mut ny) = (uy, -ux);
        if nx * (-mx) + ny * (-my) < 0. {
            (nx, ny) = (-nx, -ny);
        }
        let inward_left = nx * (-uy) + ny * ux > 0.;
        let ramp = f(d, "ledge_depth")? * 2_f64.sqrt();
        let entry = (length - f(d, "ledge_shelf_span")?) / 2.;
        let shelf = f(d, "ledge_shelf_span")? - 2. * f(d, "ledge_depth")?;
        let mut cursor = [x, y];
        let mut direction = heading.to_radians();
        let turn = if inward_left {
            45_f64.to_radians()
        } else {
            -45_f64.to_radians()
        };
        for (distance, angle) in [(entry, 0.), (ramp, turn), (shelf, -turn), (ramp, -turn)] {
            direction += angle;
            cursor[0] += distance * direction.cos();
            cursor[1] += distance * direction.sin();
            points.push(cursor);
        }
    }
    Ok(points)
}

fn offset(points: &[[f64; 2]], distance: f64) -> Result<Vec<[f64; 2]>> {
    let n = points.len();
    let mut edges = Vec::new();
    for i in 0..n {
        let [x1, y1] = points[i];
        let [x2, y2] = points[(i + 1) % n];
        let (dx, dy) = (x2 - x1, y2 - y1);
        let length = dx.hypot(dy);
        ensure!(length != 0., "cannot offset a zero length polygon edge");
        edges.push([dx, dy, -dy / length, dx / length]);
    }
    let mut result = Vec::new();
    for i in 0..n {
        let prev = (i + n - 1) % n;
        let [adx, ady, anx, any] = edges[prev];
        let [bdx, bdy, bnx, bny] = edges[i];
        let (ax, ay) = (
            points[prev][0] + distance * anx,
            points[prev][1] + distance * any,
        );
        let (bx, by) = (points[i][0] + distance * bnx, points[i][1] + distance * bny);
        let det = adx * bdy - ady * bdx;
        result.push(if det.abs() < 1e-10 {
            [bx, by]
        } else {
            let t = ((bx - ax) * bdy - (by - ay) * bdx) / det;
            [ax + t * adx, ay + t * ady]
        });
    }
    Ok(result)
}

pub fn rounded(width: f64, height: f64, radius: f64, n: usize) -> Result<Vec<[f64; 2]>> {
    ensure!(n > 0, "rounded profile has arc segments");
    let (hw, hh) = (width / 2., height / 2.);
    let mut result = Vec::new();
    for (cx, cy, start, end) in [
        (hw - radius, hh - radius, 0., 90.),
        (-hw + radius, hh - radius, 90., 180.),
        (-hw + radius, -hh + radius, 180., 270.),
        (hw - radius, -hh + radius, 270., 360.),
    ] {
        for i in 0..=n {
            let angle = (start + (end - start) * i as f64 / n as f64).to_radians();
            result.push([cx + radius * angle.cos(), cy + radius * angle.sin()]);
        }
    }
    Ok(result)
}

fn split(v: &Value) -> Result<Vec<[f64; 2]>> {
    let (wide, narrow) = (f(v, "wide_half_extent")?, f(v, "narrow_half_extent")?);
    let wr = f(v, "wide_radius")?.max(0.01);
    let nr = f(v, "narrow_radius")?.max(0.01);
    let wy = v["wide_half_extent_y"].as_f64().unwrap_or(wide);
    let ny = v["narrow_half_extent_y"].as_f64().unwrap_or(narrow);
    let ty_plus = v["transition_y_plus"]
        .as_f64()
        .unwrap_or((wide - narrow) / 2.);
    let ty_minus = v["transition_y_minus"].as_f64().unwrap_or(-ty_plus);
    let n = v["n"].as_u64().unwrap_or(8) as usize;
    ensure!(n > 0, "split profile has arc segments");
    let mut result = Vec::new();
    for (cx, cy, r, start) in [
        (wide - wr, wy - wr, wr, 0.),
        (-wide + wr, wy - wr, wr, 90.),
        (-narrow + nr, -ny + nr, nr, 180.),
        (narrow - nr, -ny + nr, nr, 270.),
    ] {
        if start == 180. {
            let a = [-wide, ty_plus];
            let b = [-narrow, ty_minus];
            result.push(a);
            if b != a {
                result.push(b);
            }
        }
        for i in 0..=n {
            let a = (start + 90. * i as f64 / n as f64).to_radians();
            result.push([cx + r * a.cos(), cy + r * a.sin()]);
        }
    }
    let a = [narrow, ty_minus];
    let b = [wide, ty_plus];
    result.push(a);
    if b != a {
        result.push(b);
    }
    Ok(result)
}

fn skirt_set(d: &Value, wall: f64) -> Result<Vec<Vec<[f64; 2]>>> {
    let shift = wall * (2_f64.sqrt() - 1.);
    let base = f(d, "skirt_base_half_extent")? - wall;
    let wide = f(d, "skirt_wide_half_extent")? - wall;
    let narrow = f(d, "skirt_narrow_half_extent")? - wall;
    let mid_narrow = f(d, "skirt_mid_narrow_half_extent")? - wall;
    let radius = f(d, "corner_r")? - wall;
    let mut args = json!({"wide_radius":radius,"narrow_radius":radius,"wide_half_extent_y":base,
        "narrow_half_extent_y":base,"n":d["arc_segments"]});
    args["wide_half_extent"] = json!(base);
    args["narrow_half_extent"] = json!(base);
    args["transition_y_plus"] = json!(shift);
    args["transition_y_minus"] = json!(shift);
    let symmetric = split(&args)?;
    args["wide_half_extent"] = json!(wide);
    args["narrow_half_extent"] = json!(mid_narrow);
    args["transition_y_plus"] = json!(d["skirt_transition_y_mid"][0].as_f64().unwrap() + shift);
    args["transition_y_minus"] = json!(d["skirt_transition_y_mid"][1].as_f64().unwrap() + shift);
    let mid = split(&args)?;
    args["narrow_half_extent"] = json!(narrow);
    args["transition_y_plus"] = json!(d["skirt_transition_y_end"][0].as_f64().unwrap() + shift);
    args["transition_y_minus"] = json!(d["skirt_transition_y_end"][1].as_f64().unwrap() + shift);
    let end = split(&args)?;
    Ok(vec![symmetric.clone(), symmetric, mid, end.clone(), end])
}

fn variables(d: &Value) -> Result<Value> {
    let mut result = serde_json::Map::new();
    for (name, key, spec, unit) in [
        ("CASE_OUTER_X", "case_outer_x", ".1f", " mm"),
        ("CASE_OUTER_Y", "case_outer_y", ".1f", " mm"),
        ("CASE_OUTER_Z", "case_outer_z", ".1f", " mm"),
        ("CYLINDER_BOTTOM_Z", "cylinder_bottom_z", "+g", " mm"),
        ("BORE_BOTTOM_Z", "bore_bottom_z", "+g", " mm"),
        ("CYLINDER_TOP_Z", "cylinder_top_z", "+g", " mm"),
        ("NARROW_SPLIT_Z", "narrow_split_z", "+g", " mm"),
        ("SKIRT_BOTTOM_Z", "skirt_bottom_z", "+g", " mm"),
        ("LOWER_CAP_TOP_Z", "lower_cap_top_z", "+g", " mm"),
        ("LOWER_CAP_BOTTOM_Z", "lower_cap_bottom_z", "+g", " mm"),
        ("FOOTPRINT_X", "footprint_x", ".4g", ""),
        ("SKIRT_WIDE_WIDTH", "skirt_wide_full_width", ".4g", ""),
        ("SKIRT_NARROW_WIDTH", "skirt_narrow_full_width", ".4g", ""),
        ("SKIRT_WIDE_FLARE", "skirt_wide_flare_per_side", ".4g", "mm"),
        (
            "SKIRT_NARROW_TAPER",
            "skirt_narrow_taper_per_side",
            ".4g",
            "mm",
        ),
    ] {
        result.insert(name.into(), shown(f(d, key)?, spec, unit)?);
    }
    result.insert(
        "BASE_PLATE_FAR_Z".into(),
        json!(format!(
            "+{}",
            shown(f(d, "base_thickness")?, ".4g", " mm")?
                .as_str()
                .unwrap()
        )),
    );
    result.insert(
        "RAMP_BOTTOM_WIDTH".into(),
        shown(
            f(d, "footprint_x")? - 2. * f(d, "ramp_from_skirt_to_octagon_height")?,
            ".4g",
            "",
        )?,
    );
    Ok(Value::Object(result))
}

pub fn dispatch(v: &Value) -> Result<Value> {
    Ok(match super::text(v, "op")? {
        "pump-case-defaults" => defaults()?,
        "pump-case-bore" => json!(bore(&v["case"])?),
        "pump-case-offset" => json!(offset(&points(&v["points"])?, f(v, "distance")?)?),
        "pump-case-rounded" => json!(rounded(
            f(v, "width")?,
            f(v, "height")?,
            f(v, "radius")?,
            v["n"]
                .as_u64()
                .ok_or_else(|| anyhow!("arc segments is an integer"))? as usize
        )?),
        "pump-case-split" => json!(split(v)?),
        "pump-case-skirt-set" => json!(skirt_set(&v["case"], f(v, "wall_offset")?)?),
        "pump-case-ring" => {
            let mut pts = array(v, "points")?.clone();
            ensure!(!pts.is_empty(), "ring has points");
            if pts.first() != pts.last() {
                pts.push(pts[0].clone());
            }
            json!(pts)
        }
        "pump-case-variables" => variables(&v["case"])?,
        _ => return Err(anyhow!("unknown pump case operation")),
    })
}
