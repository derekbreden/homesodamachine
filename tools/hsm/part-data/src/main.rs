//! Scalar construction recipes for printed shop tools and compliant fittings.
#![recursion_limit = "512"]
use anyhow::{Context, Result, bail};
use hsm_documents::format_number;
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    io::{self, BufRead, Write},
};

mod electronics;
mod sleeve;
mod zone;

fn num(v: &Value, key: &str) -> Result<f64> {
    v[key]
        .as_f64()
        .with_context(|| format!("Missing number {key}"))
}
fn opt(v: &Value, key: &str, fallback: f64) -> f64 {
    v[key].as_f64().unwrap_or(fallback)
}
fn point(v: &Value) -> Result<[f64; 3]> {
    let a = v.as_array().context("Expected three coordinates")?;
    if a.len() != 3 {
        bail!("Expected three coordinates")
    }
    Ok([
        a[0].as_f64().context("coordinate")?,
        a[1].as_f64().context("coordinate")?,
        a[2].as_f64().context("coordinate")?,
    ])
}
fn variables(rows: &[(&str, f64, &str, &str)]) -> Result<Value> {
    let mut out = BTreeMap::new();
    for &(key, value, spec, suffix) in rows {
        out.insert(key, format!("{}{suffix}", format_number(value, spec)?));
    }
    Ok(serde_json::to_value(out)?)
}
fn color(v: &Value) -> Value {
    v.get("color").cloned().unwrap_or(Value::Null)
}

fn drain(v: &Value) -> Result<Value> {
    let (barb_bore, tube_bore, tube_depth, reducer_length, min_wall, groove_depth) =
        (6.10, 3.80, 14.0, 5.50, 3.45, 0.50);
    let barb_od = barb_bore + 2.0 * (min_wall + groove_depth);
    let tube_od = tube_bore + 2.0 * (min_wall + groove_depth);
    let (groove_flat, groove_ramp, barb_tie_z, installed_reach) = (2.80, 1.0, 5.5, 8.6);
    let (elbow_reach, elbow_r) = (25.4, 4.05);
    let turn_start_z = -reducer_length;
    let socket_drop = -turn_start_z + elbow_r;
    let barb = if v["installed"].as_bool().unwrap_or(false) {
        num(v, "vent_diameter")?
    } else {
        barb_bore
    };
    let tube = if v["installed"].as_bool().unwrap_or(false) {
        4.0
    } else {
        tube_bore
    };
    let rb = f64::sqrt(barb_od * barb_od + barb * barb - barb_bore * barb_bore) / 2.0;
    let rt = f64::sqrt(tube_od * tube_od + tube * tube - tube_bore * tube_bore) / 2.0;
    let flat_z = -(rb + socket_drop + rt) / 2_f64.sqrt() + 0.6;
    if v["method"] == "tube_mouth" {
        let p = point(&v["tip"])?;
        return Ok(json!([p[0] - elbow_reach, p[1], p[2] - socket_drop]));
    }
    Ok(json!({
        "values": {"BARB_BORE":barb_bore,"TUBE_BORE":tube_bore,"TUBE_DEPTH":tube_depth,
            "REDUCER_LENGTH":reducer_length,"MIN_WALL":min_wall,"GROOVE_DEPTH":groove_depth,
            "BARB_OD":barb_od,"TUBE_OD":tube_od,"GROOVE_FLAT":groove_flat,"GROOVE_RAMP":groove_ramp,
            "BARB_TIE_Z":barb_tie_z,"INSTALLED_REACH":installed_reach,"ELBOW_REACH":elbow_reach,
            "ELBOW_R":elbow_r,"TURN_START_Z":turn_start_z,"SOCKET_DROP":socket_drop},
        "numbers": {"barb_bore":barb,"tube_bore":tube,"barb_radius":rb,"tube_radius":rt,
            "installed_reach":installed_reach,"socket_drop":socket_drop,"elbow_reach":elbow_reach,
            "elbow_radius":elbow_r,"turn_start_z":turn_start_z,"reducer_length":reducer_length,
            "groove_depth":groove_depth,"groove_flat":groove_flat,"groove_ramp":groove_ramp,
            "groove_centres":[installed_reach-barb_tie_z,elbow_reach-6.0],"flat_z":flat_z,
            "print_shift":[(elbow_reach+socket_drop+rt-rb-installed_reach)/(2.0*2_f64.sqrt()),0.0,-flat_z],"color":color(v)},
        "variables":variables(&[
            ("BARB_BORE",barb_bore,".2f",""),("BARB_DEPTH",installed_reach,"g",""),
            ("TUBE_BORE",tube_bore,".2f",""),("TUBE_DEPTH",tube_depth,"g",""),
            ("BARB_OD",barb_od,"g",""),("TUBE_OD",tube_od,"g",""),("MIN_WALL",min_wall,".2f",""),
            ("SOCKET_DROP",socket_drop,".2f",""),("REDUCER_LENGTH",reducer_length,".2f",""),
            ("VOLUME",opt(v,"volume",0.0)/1000.0,".3f","")])?
    }))
}

fn cuffs(v: &Value) -> Result<Value> {
    let (metal_wall, reducer, tube_depth, tube_radius, outer_radius, throat) =
        (2.8, 5.0, 15.0, 3.175, 5.916, 2.2);
    let profile = |depth: f64, bore: f64| {
        let outer = bore + metal_wall;
        let tube_end = -reducer - tube_depth;
        json!([
            [outer, depth],
            [outer, 0.0],
            [outer_radius, -reducer],
            [outer_radius, tube_end],
            [tube_radius, tube_end],
            [tube_radius, -reducer],
            [throat, -reducer],
            [throat, 0.0],
            [bore, 0.0],
            [bore, depth]
        ])
    };
    let inlet = profile(13.0, 8.575);
    let outlet = profile(14.0, 7.94);
    Ok(
        json!({"values":{"SIDES":["inlet","outlet"],"METAL_SOCKET_DEPTH":{"inlet":13.0,"outlet":14.0},
        "METAL_SOCKET_RADIUS":{"inlet":8.575,"outlet":7.94},"METAL_WALL":metal_wall,
        "REDUCER_LENGTH":reducer,"TUBE_SOCKET_DEPTH":tube_depth,"TUBE_SOCKET_RADIUS":tube_radius,
        "TUBE_OUTER_RADIUS":outer_radius,"THROAT_RADIUS":throat,"ASSE_OUTLET_X":65.0},
        "profiles":{"inlet":inlet,"outlet":outlet},
        "numbers":{"cuffs":[{"side":"inlet","profile":inlet,"depth":13.0},
            {"side":"outlet","profile":outlet,"depth":14.0}],"color":color(v)}}),
    )
}

fn countertop(v: &Value) -> Result<Value> {
    let (inch, reach_x, reach_y, border) = (25.4, 325.0, 320.0, 5.0);
    let hole = 1.375 * inch;
    let (below, bend, hand_room) = (80.0 - 6.0, 30.0, 60.0);
    let (t, height, cavity) = (30.0, 220.0, 130.0);
    let slab_x = cavity + 2.0 * t;
    let slab_y = reach_y - 2.0 * border;
    let (corner, root, foot) = (6.0, 6.0, 3.0);
    let mut vars = variables(&[
        ("FCT_CAVITY", cavity, "g", " mm"),
        ("FCT_T", t, "g", " mm"),
        ("FCT_HEIGHT", height, "g", " mm"),
        ("FCT_CLEAR", height - t, "g", " mm"),
        ("FCT_HOLE", hole, ".2f", " mm"),
        ("FCT_CORNER_R", corner, "g", " mm"),
        ("FCT_ROOT_R", root, "g", " mm"),
        ("FCT_FOOT_R", foot, "g", " mm"),
        ("FCT_UMBILICAL", below + bend, "g", " mm"),
        ("FCT_VOLUME", opt(v, "volume", 0.0) / 1000.0, ".0f", " cm³"),
    ])?;
    vars["FCT_SLAB"] = json!(format!(
        "{} × {} mm",
        format_number(slab_x, "g")?,
        format_number(slab_y, "g")?
    ));
    Ok(
        json!({"values":{"INCH":inch,"LEFT_REACH_X":reach_x,"LEFT_REACH_Y":reach_y,
        "PLATE_BORDER":border,"COUNTER_HOLE_D":hole,"UMBILICAL_BELOW_COUNTER":below,
        "UMBILICAL_BEND_R":bend,"HAND_ROOM":hand_room,"T":t,"HEIGHT":height,"CAVITY":cavity,
        "SLAB_X":slab_x,"SLAB_Y":slab_y,"CORNER_R":corner,"ROOT_R":root,"FOOT_R":foot,
        "clear_height":height-t,"leg_inner_x":cavity/2.0},
        "numbers":{"slab_x":slab_x,"slab_y":slab_y,"cavity":cavity,"thickness":t,"height":height,
            "corner_radius":corner,"root_radius":root,"foot_radius":foot,"hole_diameter":hole,
            "reach_x":reach_x,"reach_y":reach_y,"umbilical_below":below,"bend_radius":bend,
            "hand_room":hand_room,"color":color(v)},"variables":vars}),
    )
}

fn miter(v: &Value) -> Result<Value> {
    let running = num(v, "running")?;
    let inch = 25.4;
    let tube_small = inch / 4.0;
    let tube_large = inch * 3.0 / 8.0;
    let (blade_l, blade_h, blade_t, spine_h) = (1.5 * inch, 0.75 * inch, 0.009 * inch, 5.0);
    let reach = blade_h - spine_h;
    let (slot_w, slot_l, slot_depth, end_wall, floor, offcut, keep, pitch, lift) =
        (0.8, 40.0, 15.0, 5.0, 3.0, 5.0, 19.0, 20.0, 2.5);
    let (block_x, block_y, block_z) = (
        slot_l + 2.0 * end_wall,
        offcut + slot_w + keep,
        floor + slot_depth,
    );
    let (slot_y0, slot_y1, trough_floor, edge_z) =
        (offcut, offcut + slot_w, floor + lift, block_z - reach);
    if v["method"] == "trough_r" {
        return Ok(json!(num(v, "tube_od")? / 2.0 + running));
    }
    let y = (slot_y0 + slot_y1) / 2.0;
    let mut vars = variables(&[
        ("TMB_TROUGH_1_4", tube_small + 2.0 * running, ".2f", " mm"),
        ("TMB_TROUGH_3_8", tube_large + 2.0 * running, ".2f", " mm"),
        ("TMB_RUNNING", running, "g", " mm"),
        ("TMB_TROUGH_PITCH", pitch, "g", " mm"),
        ("TMB_SLOT_W", slot_w, "g", " mm"),
        ("TMB_SLOT_L", slot_l, "g", " mm"),
        ("TMB_OFFCUT_SIDE", offcut, "g", " mm"),
        ("TMB_KEEP_SIDE", keep, "g", " mm"),
        ("TMB_RAZOR_PAST_FLOOR", trough_floor - edge_z, ".2f", " mm"),
        ("TMB_TROUGH_FLOOR_ABOVE_SLOT_FLOOR", lift, "g", " mm"),
        (
            "TMB_WALL_ABOVE_3_8",
            block_z - (trough_floor + tube_large),
            ".2f",
            " mm",
        ),
    ])?;
    vars["TMB_BLOCK"] = json!(format!(
        "{} × {} × {} mm",
        format_number(block_x, "g")?,
        format_number(block_y, "g")?,
        format_number(block_z, "g")?
    ));
    Ok(
        json!({"values":{"INCH":inch,"TUBE_OD_1_4":tube_small,"TUBE_OD_3_8":tube_large,
        "RAZOR_BLADE_L":blade_l,"RAZOR_BLADE_H":blade_h,"RAZOR_BLADE_T":blade_t,"RAZOR_SPINE_H":spine_h,
        "RAZOR_REACH":reach,"SLOT_W":slot_w,"SLOT_L":slot_l,"SLOT_DEPTH":slot_depth,"END_WALL":end_wall,
        "FLOOR_UNDER_SLOT":floor,"OFFCUT_SIDE":offcut,"KEEP_SIDE":keep,"TROUGH_FLOOR_ABOVE_SLOT_FLOOR":lift,
        "TROUGH_PITCH":pitch,"BLOCK_X":block_x,"BLOCK_Y":block_y,"BLOCK_Z":block_z,
        "slot_y0":slot_y0,"slot_y1":slot_y1,"slot_floor_z":floor,"trough_floor_z":trough_floor,
        "razor_edge_z":edge_z,"TROUGHS":{"1/4":[-pitch/2.0,tube_small],"3/8":[pitch/2.0,tube_large]},
        "MESH_TOLERANCE":0.02,"MESH_ANGLE":0.15},
        "numbers":{"block":[block_x,block_y,block_z],"trough_floor":trough_floor,
            "troughs":[-pitch/2.0,tube_small/2.0+running,tube_small,pitch/2.0,tube_large/2.0+running,tube_large],
            "slot_y":[slot_y0,slot_y1],"slot_length":slot_l,"slot_floor":floor,
            "razor_bounds":[-blade_l/2.0,blade_l/2.0,y-blade_t/2.0,y+blade_t/2.0,edge_z,block_z],
            "color":color(v)},"variables":vars}),
    )
}

fn jet_fixture(v: &Value) -> Result<Value> {
    let rod = num(v, "cap_diameter")?;
    let drill = num(v, "passage_diameter")?;
    let (slip, gap, base_x, base_y, base_t, jaw_x, jaw_depth, grip) =
        (0.15, 1.0, 120.0, 90.0, 8.0, 64.0, 25.0, 30.0);
    let groove = rod / 2.0 + slip;
    let mut vars = variables(&[
        ("JET_FIXTURE_GRIP", grip, "g", " mm"),
        ("JET_FIXTURE_GROOVE", 2.0 * groove, "g", " mm"),
        ("JET_FIXTURE_GAP", gap, "g", " mm"),
        ("JET_FIXTURE_BLANK", 50.0, "g", " mm"),
        ("JET_FIXTURE_MIN_BLANK", 40.0, "g", " mm"),
    ])?;
    vars["JET_FIXTURE_BASE"] = json!(format!(
        "{} × {} × {} mm",
        format_number(base_x, "g")?,
        format_number(base_y, "g")?,
        format_number(base_t, "g")?
    ));
    vars["JET_FIXTURE_JAW_CLAMP_X"] = json!("±20 mm");
    vars["JET_FIXTURE_BASE_CLAMP_X"] = json!("±46 mm");
    Ok(
        json!({"values":{"ROD_D":rod,"GROOVE_RADIAL_SLIP":slip,"GROOVE_R":groove,"OPEN_JAW_GAP":gap,
        "BASE_X":base_x,"BASE_Y":base_y,"BASE_T":base_t,"JAW_X":jaw_x,"JAW_DEPTH":jaw_depth,"GRIP_Z":grip,
        "HANDLING_BLANK_L":50.0,"MIN_HANDLING_BLANK_L":40.0,"JAW_CLAMP_X":20.0,"BASE_CLAMP_X":46.0,
        "MESH_TOLERANCE":0.02,"MESH_ANGLE":0.15},
        "numbers":{"base":[base_x,base_y,base_t],"jaw":[jaw_x,jaw_depth,grip],"gap":gap,
            "groove_radius":groove,"stock_diameter":rod,"radial_slip":slip,"minimum_blank":40.0,
            "drill_diameter":drill,"color":color(v)},"variables":vars}),
    )
}

fn collet(v: &Value) -> Result<Value> {
    let port = num(v, "port_diameter")?;
    let collet_d = num(v, "collet_diameter")?;
    let collet_bore = num(v, "collet_bore")?;
    let collet_wall = num(v, "collet_wall")?;
    let travel = num(v, "collet_travel")?;
    let (gap, root_u, angle, head_t, head_w, tip_r, handle_l) =
        (6.55, 0.0, 45_f64, 6.0, 20.0, 2.0, 88.0);
    let jaw_r = gap / 2.0;
    let tip_u = collet_d / 2.0;
    let depth = tip_u - (root_u - jaw_r);
    let overrun = tip_u - port / 2.0;
    let arm_w = (head_w - gap) / 2.0;
    let back_land = arm_w;
    let back = root_u - jaw_r - back_land;
    let front = tip_u + tip_r;
    let bury = head_t * angle.to_radians().cos();
    let lower = head_t - bury;
    let shift = lower - back * angle.to_radians().sin();
    let underside = |z: f64| (z - shift) / angle.to_radians().tan();
    if v["method"] == "head_underside_x" {
        return Ok(json!(underside(num(v, "z")?)));
    }
    let bed_x = underside(0.0);
    let top_x = underside(head_t);
    let rear_x = bed_x - handle_l;
    let (z0, z1) = (-1.0, head_t + 1.0);
    let mut vars = variables(&[
        ("TUBE_D", port, ".2f", " mm"),
        ("JAW_GAP", gap, ".2f", " mm"),
        ("JAW_DEPTH", depth, ".2f", " mm"),
        ("STRAIGHT_OVERRUN", overrun, ".2f", " mm"),
        ("ARM_W", arm_w, ".3f", " mm"),
        ("TIP_R", tip_r, ".1f", " mm"),
        ("HEAD_BACK_LAND", back_land, ".3f", " mm"),
        ("ROOT_BURY", bury, ".2f", " mm"),
        ("TUBE_CLEARANCE", gap - port, ".2f", " mm"),
        ("COLLET_D", collet_d, ".2f", " mm"),
        ("COLLET_BORE", collet_bore, ".2f", " mm"),
        ("COLLET_WALL", collet_wall, ".2f", " mm"),
        ("JAW_COVER", (collet_d - gap) / 2.0, ".2f", " mm per side"),
        ("COLLET_TRAVEL", travel, ".3f", " mm"),
        ("HEAD_ANGLE", angle, ".0f", "°"),
        ("HEAD_T", head_t, ".2f", " mm"),
        ("HEAD_W", head_w, ".0f", " mm"),
        ("HANDLE_L", handle_l, ".0f", " mm"),
        ("HANDLE_W", head_w, ".0f", " mm"),
        ("HANDLE_T", head_t, ".2f", " mm"),
        ("TOOL_VOLUME", opt(v, "volume", 0.0) / 1000.0, ".1f", " cm³"),
    ])?;
    for (key, index) in [("TOOL_X", 0), ("TOOL_Y", 1), ("TOOL_Z", 2)] {
        vars[key] = json!(format!(
            "{} mm",
            format_number(v["span"][index].as_f64().unwrap_or(0.0), ".1f")?
        ));
    }
    Ok(
        json!({"values":{"JAW_GAP":gap,"JAW_RADIUS":jaw_r,"JAW_ROOT_U":root_u,"STRAIGHT_TIP_U":tip_u,
        "JAW_DEPTH":depth,"STRAIGHT_OVERRUN":overrun,"HEAD_ANGLE":angle,"HEAD_THICKNESS":head_t,
        "HEAD_WIDTH":head_w,"ARM_WIDTH":arm_w,"TIP_RADIUS":tip_r,"HEAD_BACK_LAND":back_land,
        "HEAD_BACK_U":back,"HEAD_FRONT_U":front,"HEAD_LENGTH":front-back,"HEAD_CENTER_U":(back+front)/2.0,
        "HANDLE_LENGTH":handle_l,"HANDLE_WIDTH":head_w,"HANDLE_THICKNESS":head_t,"HANDLE_CORNER_RADIUS":tip_r,
        "ROOT_BURY":bury,"HEAD_REAR_LOWER_Z":lower,"HEAD_Z_SHIFT":shift,"HANDLE_FRONT_BED_X":bed_x,
        "HANDLE_FRONT_TOP_X":top_x,"HANDLE_REAR_X":rear_x},
        "numbers":{"head_back":back,"head_front":front,"head_width":head_w,"head_thickness":head_t,
            "head_angle":angle,"head_z_shift":shift,"jaw_gap":gap,"jaw_root":root_u,"tip_radius":tip_r,
            "handle_x":[rear_x,top_x+2.0],"handle_width":head_w,"handle_thickness":head_t,"handle_corner_radius":tip_r,
            "handle_clip":[rear_x-2.0,z0,underside(z0),z0,underside(z1),z1,rear_x-2.0,z1],
            "tube_diameter":port,"collet_bore":collet_bore,"color":color(v)},"variables":vars}),
    )
}

fn valve_seat(v: &Value) -> Result<Value> {
    let inset_x = num(v, "corner_inset_x")?;
    let inset_y = num(v, "corner_inset_y")?;
    let post_r = num(v, "corner_post_radius")?;
    let seat_top = num(v, "seat_top_z")?;
    let port_r = num(v, "port_radius")?;
    let port_z = num(v, "port_center_z")?;
    let slip = num(v, "slip")?;
    let (socket_d, alternate_d, wall, floor, corner, air) = (6.9, 7.0, 3.0, -1.0, 3.0, 0.5);
    let socket_r = socket_d / 2.0;
    let clearance = socket_r - post_r;
    let boss_r = post_r + slip + wall;
    let (hx, hy) = (inset_x + boss_r, inset_y + boss_r);
    let socket_depth = seat_top - floor;
    let area = 4.0 * hx * hy - (4.0 - std::f64::consts::PI) * corner * corner;
    let r = port_r + air;
    let d = port_z - seat_top;
    let section = r * r * (d / r).acos() - d * (r * r - d * d).sqrt();
    let seat = opt(v, "seat", -floor);
    let volume = area * (seat + seat_top)
        - 4.0 * std::f64::consts::PI * socket_r * socket_r * socket_depth
        - 2.0 * hy * section;
    let gap = (port_z - port_r) - (port_z - (port_r + air));
    let method = v["method"].as_str().unwrap_or("state");
    if method == "volume" {
        return Ok(json!(volume));
    }
    if method == "socket_depth" {
        return Ok(json!(socket_depth));
    }
    if method == "port_clearance" {
        return Ok(json!(gap));
    }
    if method == "main" && (gap - air).abs() > 1e-6_f64.max(1e-9 * air.abs()) {
        bail!("port channel clearance {gap}")
    }
    Ok(
        json!({"values":{"corner_inset_x":inset_x,"corner_inset_y":inset_y,"corner_post_radius":post_r,
        "seat_top_z":seat_top,"socket_diameter":socket_d,"alternate_socket_diameter":alternate_d,
        "socket_radius":socket_r,"socket_clearance":clearance,"wall":wall,"socket_floor_z":floor,
        "boss_radius":boss_r,"seat_half_x":hx,"seat_half_y":hy,"seat_corner_radius":corner,"port_air":air},
        "variables":variables(&[("POST_DIA",2.0*post_r,".4g",""),("SOCKET_DIA",2.0*socket_r,".4g",""),
            ("PLINTH_WIDTH",2.0*hx,".4g",""),("PLINTH_DEPTH",2.0*hy,".4g",""),("PLINTH_CORNER",corner,".4g",""),
            ("BOSS_DIA",2.0*boss_r,".4g",""),("SOCKET_CLEAR",clearance,".4g"," mm"),("WALL",wall,".4g"," mm"),
            ("CORNER_PITCH_X",2.0*inset_x,"g",""),("CORNER_PITCH_Y",2.0*inset_y,"g",""),
            ("SEAT_TOP_Z",seat_top,".4g",""),("SOCKET_FLOOR_Z",floor,".4g",""),("SOCKET_DEPTH",socket_depth,".4g",""),
            ("PORT_DIA",2.0*port_r,".4g",""),("PORT_CLEARANCE",gap,".3f"," mm")])?,
        "report":format!("seat at {} mm: {} mm^3, port clearance {} mm",format_number(-floor,"g")?,format_number(volume,".1f")?,format_number(gap,".4f")?)}),
    )
}

fn request(v: &Value) -> Result<Value> {
    match v["part"].as_str().context("Missing part name")? {
        "asse-drain-adapter" => drain(v),
        "asse-straight-cuffs" => cuffs(v),
        "fake-countertop" => countertop(v),
        "tube-miter-box" => miter(v),
        "water-inlet-jet-fixture" => jet_fixture(v),
        "collet-press" => collet(v),
        "valve-seat" => valve_seat(v),
        "diaphragm-pump-sleeve" => sleeve::request(v),
        "module-tray" | "pcba-tray" | "pcba-assembly" => electronics::request(v),
        "funnel" | "elbow-cradle" | "funnel-frame" | "funnel-cover" | "funnel-mold" => {
            zone::request(v)
        }
        other => bail!("Unknown part-data provider {other}"),
    }
}

fn answer(line: &str) -> Value {
    let result = serde_json::from_str(line)
        .context("Invalid request JSON")
        .and_then(|v| request(&v));
    result.unwrap_or_else(|e| json!({"error":format!("{e:#}")}))
}
fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.as_slice() == ["--serve"] {
        let stdin = io::stdin();
        let stdout = io::stdout();
        let mut out = stdout.lock();
        for line in stdin.lock().lines() {
            writeln!(out, "{}", answer(&line?))?;
            out.flush()?;
        }
    } else if let [payload] = args.as_slice() {
        println!("{}", request(&serde_json::from_str(payload)?)?);
    } else {
        bail!("usage: part-data --serve | '<request JSON>'");
    }
    Ok(())
}
