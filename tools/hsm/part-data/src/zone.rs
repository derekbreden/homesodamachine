//! The funnel's, compliant cradle's and frame's scalar designs, for the hand-run tools that read
//! them through the funnel's Python.
use crate::{num, opt, variables};
use anyhow::{Context, Result, bail};
use hsm_documents::format_number;
use hsm_enclosure_interface as interface;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const COLLAR_W: f64 = 165.0;
const FORWARD: f64 = 41.6085;
const AFT: f64 = 35.0;
const COLLAR_D: f64 = 81.78301584656256 + FORWARD + AFT;
const MOUTH_R: f64 = 14.0;
const COLLAR_R: f64 = MOUTH_R + 6.0;
const BRIM_R: f64 = COLLAR_R + 7.0;
const BRIM_MARGIN: f64 = 7.0;
const OVERHANG: f64 = 7.0;
const BRIM_T: f64 = 6.0;
const APRON_RISE: f64 = 3.0;
const APRON_W: f64 = 215.0;
const APRON_D: f64 = COLLAR_D + 32.0;
const APRON_Y: f64 = 3.0;
const APRON_R: f64 = 6.0;
const COLLAR_WALL: f64 = 6.0;
const CHUTE: f64 = 23.485946291005064;
const RAMP_RISE: f64 = 14.199233063709995;
const SPOUT_ID: f64 = 6.0;
const SPOUT_WALL: f64 = 4.5;
const PLUG_W: f64 = 36.0;
const PLUG_LIFT: f64 = 3.15;
const PLUG_H: f64 = 16.0 - PLUG_LIFT;
const DROP: f64 = 46.1;
const SPOUT_LAND: f64 = BRIM_T - CHUTE - RAMP_RISE;
const STEM_ENGAGEMENT: f64 = SPOUT_LAND + DROP - PLUG_LIFT;

const WEB: f64 = 3.0;
const CRADLE_WALL: f64 = 3.0;
const LOWER_SIDE_RELIEF: f64 = 0.65;
const ROOT_STOCK: f64 = 3.0;
const STEM_BODY_AIR: f64 = 1.0;
const HOLE_D: f64 = 11.25;
const WING_ROOT: f64 = -8.84;
const SLOT_FORE: f64 = -11.24;
const SLOT_AFT: f64 = 20.56239;
const SOCKET_HALF: f64 = 18.3;
const LEAF_T: f64 = 1.3;
const SIDE: f64 = 0.5;
const OVERLAP: f64 = 2.6;
const HOOK_T: f64 = 2.75;
const HOOK_RISE: f64 = 0.25;
const END_SLIP: f64 = 0.25;
const SOCKET_CORNER: f64 = 0.25;

fn pair(v: &Value) -> Result<[f64; 2]> {
    Ok([
        v[0].as_f64().context("Missing x coordinate")?,
        v[1].as_f64().context("Missing y coordinate")?,
    ])
}
fn root(v: &Value) -> Result<&Path> {
    Ok(Path::new(
        v["root"].as_str().context("Missing checkout root")?,
    ))
}
fn read_json(path: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(
        &fs::read(path).with_context(|| format!("Reading {}", path.display()))?,
    )?)
}
fn digest(path: &Path) -> Result<String> {
    Ok(format!("{:x}", Sha256::digest(fs::read(path)?)))
}
fn socket_half_length() -> f64 {
    (SLOT_AFT + END_SLIP).max(-(SLOT_FORE - END_SLIP))
}
fn plug_half_length(half: f64) -> f64 {
    socket_half_length() - (SOCKET_HALF - half)
}

fn funnel_values() -> Value {
    json!({"collar_w":COLLAR_W,"forward_extension":FORWARD,"aft_extension":AFT,"collar_d":COLLAR_D,
        "mouth_corner_r":MOUTH_R,"collar_corner_r":COLLAR_R,"brim_corner_r":BRIM_R,"brim_margin":BRIM_MARGIN,
        "brim_overhang":OVERHANG,"brim_thickness":BRIM_T,"apron_rise":APRON_RISE,"apron_width":APRON_W,
        "apron_depth":APRON_D,"apron_y":APRON_Y,"apron_corner_r":APRON_R,"collar_wall":COLLAR_WALL,
        "capacity_ml":698.21,"chute_h":CHUTE,"neck_dx":0.0,"neck_dy":0.0,"spout_id":SPOUT_ID,
        "spout_wall":SPOUT_WALL,"_ramp_rise":RAMP_RISE,"plug_width":PLUG_W,"plug_lift":PLUG_LIFT,
        "plug_height":PLUG_H,"drop":DROP,"sealing_id":SPOUT_ID,"spout_land_z":SPOUT_LAND,
        "stem_engagement":STEM_ENGAGEMENT,"sealing_land":STEM_ENGAGEMENT,"drain_local":[0.0,0.0,-DROP+PLUG_LIFT]})
}
fn funnel_numbers(v: &Value) -> Value {
    json!({"bore_size":[COLLAR_W-2.0*COLLAR_WALL,COLLAR_D-2.0*COLLAR_WALL],"mouth_radius":MOUTH_R,
        "ramp_z":[BRIM_T-CHUTE,SPOUT_LAND],"bore_radius":SPOUT_ID/2.0,"drain_xy":[0.0,0.0],
        "collar_wall":COLLAR_WALL,"end_z":-DROP+PLUG_LIFT,"top_z":BRIM_T+APRON_RISE,
        "spout_radius":SPOUT_ID/2.0+SPOUT_WALL,"brim_size":[COLLAR_W+2.0*OVERHANG,COLLAR_D+2.0*OVERHANG],
        "brim_radius":BRIM_R,"brim_height":BRIM_T,"apron_size":[APRON_W,APRON_D],"apron_y":APRON_Y,
        "apron_radius":APRON_R,"apron_z":[BRIM_T,BRIM_T+APRON_RISE],"plug_size":[PLUG_W,2.0*plug_half_length(PLUG_W/2.0)],
        "plug_height":PLUG_H,"color":v["silicone_color"],"viewer_deflection_ratio":v["viewer_deflection_ratio"]})
}
fn funnel(v: &Value) -> Result<Value> {
    let mut vars = variables(&[
        ("FUNNEL_CHUTE", CHUTE, "g", " mm"),
        ("FUNNEL_DROP_UNDER", DROP, "g", " mm"),
        (
            "FUNNEL_DROP",
            BRIM_T + APRON_RISE - (-DROP + PLUG_LIFT),
            ".0f",
            " mm",
        ),
        ("FUNNEL_CAP", opt(v, "fill", 0.0) / 1000.0, ".0f", " mL"),
        ("FUNNEL_HOLD", OVERHANG, "g", " mm"),
        ("FUNNEL_MARGIN", BRIM_MARGIN, "g", " mm"),
    ])?;
    vars["FUNNEL_PLUG"] = json!(format!(
        "{} × {} mm",
        format_number(PLUG_W, "g")?,
        format_number(2.0 * plug_half_length(PLUG_W / 2.0), ".1f")?
    ));
    Ok(json!({"values":funnel_values(),"numbers":funnel_numbers(v),"variables":vars}))
}

fn bent(points: &[[f64; 3]], length: f64, tip: f64) -> Vec<[f64; 2]> {
    let th = 1.5 * tip / length;
    points
        .iter()
        .map(|&[x, h, xn]| {
            if h <= length {
                let s = h / length;
                let d = tip * s * s * (3.0 - s) / 2.0;
                let t = tip * 3.0 / (2.0 * length) * (2.0 * s - s * s);
                [xn - d + (x - xn) * t.cos(), h + (x - xn) * t.sin()]
            } else {
                let (dx, dh) = (x - xn, h - length);
                [
                    xn - tip + dx * th.cos() - dh * th.sin(),
                    length + dx * th.sin() + dh * th.cos(),
                ]
            }
        })
        .collect()
}
fn passage(
    w_in: f64,
    w_out: f64,
    tip: f64,
    slot_out: f64,
    base: f64,
    face: f64,
    top: f64,
    insertion_slip: f64,
) -> Value {
    let (length, height) = (face - base, top - base);
    let xn = (w_in + w_out) / 2.0;
    let n = 60;
    let mut points = vec![];
    for k in 0..=n {
        for x in [w_in, w_out] {
            points.push([x, height * k as f64 / n as f64, xn]);
        }
    }
    for k in 0..=n {
        for h in [length, height] {
            points.push([w_out + (tip - w_out) * k as f64 / n as f64, h, xn]);
        }
    }
    for k in 0..=n {
        points.push([tip, length + (height - length) * k as f64 / n as f64, xn]);
    }
    let (mut need, mut travel) = (0_f64, 0_f64);
    let mut t = -top;
    while t <= WEB - face + 1e-9 {
        let (a, b) = (-base - t, WEB - base - t);
        let (mut lo, mut hi) = (0.0, 6.0);
        for _ in 0..40 {
            let mid = (lo + hi) / 2.0;
            let ok = bent(&points, length, mid)
                .iter()
                .all(|&[x, h]| !(a < h && h < b) || x <= slot_out - insertion_slip);
            if ok { hi = mid } else { lo = mid }
        }
        need = need.max(hi);
        for ([x, h], p) in bent(&points, length, hi).into_iter().zip(&points) {
            if p[0] == w_in && a < h && h < b {
                travel = travel.max(w_in - x);
            }
        }
        t += 0.05;
    }
    json!({"free_length":length,"hook_deflection":need,"inner_face_travel":travel,
        "root_strain":1.5*(w_out-w_in)*need/length.powi(2)})
}

struct Cradle {
    parameters: Value,
    slip: f64,
    running: f64,
    catch_gap: f64,
    web_air: f64,
}
impl Cradle {
    fn read(v: &Value) -> Result<Self> {
        let parameters = read_json(
            &root(v)?.join("hardware/reference/neofit-stem-elbow/reference-parameters.json"),
        )?;
        let slip = num(v, "slip")?;
        let supported = num(v, "supported_surface")?;
        Ok(Self {
            parameters,
            slip,
            running: num(v, "running")?,
            catch_gap: slip + supported + HOOK_RISE,
            web_air: slip + supported,
        })
    }
    fn values(&self) -> Result<Value> {
        Ok(
            json!({"WEB":WEB,"SLIP":self.slip,"WALL":CRADLE_WALL,"LOWER_SIDE_RELIEF":LOWER_SIDE_RELIEF,
            "ROOT_STOCK":ROOT_STOCK,"STEM_BODY_AIR":STEM_BODY_AIR,"HOLE_D":HOLE_D,"WING_ROOT_Z":WING_ROOT,
            "SLOT_FORE_Y":SLOT_FORE,"SLOT_AFT_Y":SLOT_AFT,"SOCKET_HALF":SOCKET_HALF,"TIP_GAP":self.slip,
            "LEAF_T":LEAF_T,"SIDE":SIDE,"OVERLAP":OVERLAP,"HOOK_T":HOOK_T,"HOOK_RISE":HOOK_RISE,
            "CATCH_GAP":self.catch_gap,"HOOK_WEB_AIR":self.web_air,"INSERTION_SLIP":self.running,
            "END_SLIP":END_SLIP,"PLUG_CORNER":0.0,"SOCKET_CORNER":SOCKET_CORNER,
            "CORE_R":num(&self.parameters,"bend_radius_mm")?}),
        )
    }
    fn profile(&self, key: &str) -> Result<Vec<[f64; 2]>> {
        self.parameters["profiles"][key]
            .as_array()
            .context("Missing stem-elbow profile")?
            .iter()
            .map(pair)
            .collect()
    }
    fn profiles(&self, leg: &str) -> Result<(Vec<[f64; 2]>, Vec<[f64; 2]>)> {
        if leg == "y" {
            Ok((
                self.profile("fixed_body_y")?,
                self.profile("release_collet_y")?,
            ))
        } else {
            let mut p = self
                .profile("stem_x")?
                .into_iter()
                .map(|[x, r]| [-x, r])
                .collect::<Vec<_>>();
            p.sort_by(|a, b| a[0].total_cmp(&b[0]).then(a[1].total_cmp(&b[1])));
            Ok((p, vec![]))
        }
    }
    fn elbow_z(&self) -> Result<f64> {
        Ok(WEB
            + self.catch_gap
            + PLUG_LIFT
            + STEM_ENGAGEMENT
            + num(&self.parameters, "stem_tip_x_mm")?)
    }
    fn block(&self, v: &Value) -> Result<[f64; 5]> {
        let profile = self.profiles("y")?.0;
        let collar = profile
            .iter()
            .map(|p| p[1])
            .reduce(f64::max)
            .context("Empty elbow profile")?;
        let ry = collar + self.slip + CRADLE_WALL;
        let half = SOCKET_HALF - self.slip - OVERLAP - SIDE;
        let layout = read_json(&root(v)?.join("hardware/manifold-layout/above-core.json"))?;
        let stem_y = layout["snapshots"]["drain-outlet-stem"]["translation_mm"][1]
            .as_f64()
            .context("Missing drain stem pose")?;
        let drain_y = layout["fore_routes"]["drain_union_corner_mm"][1]
            .as_f64()
            .context("Missing drain corner")?;
        let aft = SLOT_AFT.min(stem_y - drain_y - collar - STEM_BODY_AIR);
        Ok([half, SLOT_FORE, aft, self.elbow_z()? - ry, WING_ROOT])
    }
    fn stations(&self, v: &Value) -> Result<Value> {
        let [half, y0, y1, z0, z1] = self.block(v)?;
        let (w_in, w_out) = (half - LEAF_T, half);
        let slot_out = w_out + SIDE;
        let face = WEB + self.catch_gap + self.web_air;
        let hook_tip = slot_out + OVERLAP;
        let hook_top = face + HOOK_T;
        let bend = passage(
            w_in,
            w_out,
            hook_tip,
            slot_out,
            z1,
            face,
            hook_top,
            self.running,
        );
        let lane = ((num(&bend, "inner_face_travel")? + self.running) * 100.0).ceil() / 100.0;
        Ok(
            json!({"half":half,"y0":y0,"y1":y1,"z0":z0,"top":z1,"w_in":w_in,"w_out":w_out,
            "slot_out":slot_out,"hook_tip":hook_tip,"face":face,"hook_top":hook_top,"bend":bend,
            "lane":lane,"slot_in":w_in-lane}),
        )
    }
    fn numbers(&self, v: &Value) -> Result<Value> {
        let b = self.block(v)?;
        let s = self.stations(v)?;
        let h = b[4] + 2.0 - self.elbow_z()?;
        let (zb, zc) = self.profiles("z")?;
        let (yb, yc) = self.profiles("y")?;
        let (mut run, mut reach) = (vec![], 0_f64);
        for [station, radius] in zb.into_iter().chain(zc.into_iter().skip(1)) {
            reach = reach.max(radius);
            run.push([station, reach + self.slip]);
        }
        let last = *run.last().context("Empty vertical elbow profile")?;
        run.push([(h + 1.0).max(last[0]), last[1]]);
        let mouth_radius = yc.iter().map(|p| p[1]).fold(
            yb.last().context("Empty horizontal elbow profile")?[1],
            f64::max,
        );
        let mut horizontal = yb;
        horizontal.push([
            yc.last().context("Empty collet profile")?[0] + self.slip,
            mouth_radius,
        ]);
        let (mut lower, mut reach) = (vec![], 0_f64);
        for &[station, radius] in &horizontal {
            reach = reach.max(radius);
            lower.push([station - self.slip, reach + self.slip]);
        }
        let (mut plan, mut reach) = (vec![], 0_f64);
        for &[station, radius] in &horizontal {
            reach = reach.max(radius + self.slip);
            plan.push([reach, station]);
        }
        let core = num(&self.parameters, "bend_radius_mm")?;
        let radius = core + self.slip;
        let mut tangents = vec![];
        for (index, &[x, y]) in plan.iter().enumerate() {
            let d2 = x * x + y * y;
            if d2 > radius * radius {
                let (a, c) = (
                    radius * radius / d2,
                    radius * (d2 - radius * radius).sqrt() / d2,
                );
                let tangent = [a * x + c * y, a * y - c * x];
                tangents.push((tangent[1].atan2(tangent[0]), index, tangent));
            }
        }
        let (_, start, tangent) = tangents
            .into_iter()
            .min_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)))
            .context("No elbow mouth tangent")?;
        let mut edge = vec![tangent];
        for &p in &plan[start..] {
            while edge.len() > 1 {
                let (a, c) = (edge[edge.len() - 2], edge[edge.len() - 1]);
                if (c[0] - a[0]) * (p[1] - c[1]) - (c[1] - a[1]) * (p[0] - c[0]) > 1e-12 {
                    break;
                }
                edge.pop();
            }
            edge.push(p);
        }
        let mut vertical = vec![[0.0, run[0][1]]];
        vertical.extend_from_slice(&run);
        let payload = "hardware/reference/neofit-stem-elbow/neofit-stem-elbow.fine.step.mesh";
        Ok(
            json!({"block":b,"elbow_z":self.elbow_z()?,"vertical_profile":turn_profile(&vertical),
            "horizontal_profile":turn_profile(&lower),"mouth_tangent":tangent,"mouth_chain":edge,
            "mouth_lift":(WING_ROOT-self.elbow_z()?).max(0.0),"shadow_height":h+1.0,
            "shadow_core_radius":core.max(run[0][1]-self.slip).max(horizontal[0][1])+self.slip,
            "lower_side_relief":LOWER_SIDE_RELIEF,"root_stock":ROOT_STOCK,"wing_x":[s["w_in"],s["w_out"]],
            "hook_tip":s["hook_tip"],"hook_face":s["face"],"hook_top":s["hook_top"],"catch_gap":self.catch_gap,
            "color":v["color"],"elbow_payload":payload,"elbow_payload_sha256":digest(&root(v)?.join(payload))?}),
        )
    }
    fn document(&self, s: &Value) -> Result<Value> {
        let bend = &s["bend"];
        variables(&[
            ("CRADLE_SLIP", self.slip, "g", " mm"),
            ("CRADLE_LENGTH", num(s, "y1")? - num(s, "y0")?, ".1f", " mm"),
            ("CRADLE_WING_T", LEAF_T, "g", " mm"),
            (
                "CRADLE_WING_H",
                num(s, "hook_top")? - num(s, "top")?,
                ".2f",
                " mm",
            ),
            (
                "CRADLE_HOOK",
                num(s, "hook_tip")? - num(s, "w_out")?,
                ".1f",
                " mm",
            ),
            ("CRADLE_OVERLAP", OVERLAP, "g", " mm"),
            ("CRADLE_CATCH", self.catch_gap, "g", " mm"),
            ("CRADLE_BEND", num(bend, "hook_deflection")?, ".2f", " mm"),
            ("CRADLE_LANE", num(s, "lane")?, ".2f", " mm"),
            (
                "CRADLE_STRAIN",
                100.0 * num(bend, "root_strain")?,
                ".1f",
                "%",
            ),
            ("CRADLE_TIP_GAP", self.slip, "g", " mm"),
            ("CRADLE_WIDTH", 2.0 * num(s, "half")?, ".1f", " mm"),
            ("CRADLE_HOOK_T", HOOK_T, "g", " mm"),
            ("CRADLE_WEB_AIR", self.web_air, ".2f", " mm"),
            ("CRADLE_SOCKET_CORNER", SOCKET_CORNER, "g", " mm"),
            (
                "CRADLE_WEB",
                num(s, "slot_in")? - HOLE_D / 2.0,
                ".2f",
                " mm",
            ),
        ])
    }
}
fn turn_profile(points: &[[f64; 2]]) -> Vec<[f64; 2]> {
    let mut raw = vec![[0.0, points[0][0]]];
    raw.extend(points.iter().map(|&[t, r]| [r, t]));
    raw.push([0.0, points[points.len() - 1][0]]);
    let mut pts: Vec<[f64; 2]> = vec![];
    for p in raw {
        if pts
            .last()
            .is_none_or(|q| (p[0] - q[0]).abs() > 1e-6 || (p[1] - q[1]).abs() > 1e-6)
        {
            pts.push(p)
        }
    }
    let mut k = 1;
    while k + 1 < pts.len() {
        let ([x0, y0], [x1, y1], [x2, y2]) = (pts[k - 1], pts[k], pts[k + 1]);
        if ((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)).abs() < 1e-9 {
            pts.remove(k);
        } else {
            k += 1;
        }
    }
    pts
}

fn cradle(v: &Value) -> Result<Value> {
    let method = v["method"].as_str().unwrap_or("state");
    if method == "socket_half_length" {
        return Ok(json!(socket_half_length()));
    }
    if method == "plug_half_length" {
        return Ok(json!(plug_half_length(num(v, "half_width")?)));
    }
    if method == "turn_profile" {
        return Ok(json!(turn_profile(
            &v["points"]
                .as_array()
                .context("Missing profile points")?
                .iter()
                .map(pair)
                .collect::<Result<Vec<_>>>()?
        )));
    }
    if method == "bent" {
        let points = v["points"]
            .as_array()
            .context("Missing spring points")?
            .iter()
            .map(crate::point)
            .collect::<Result<Vec<_>>>()?;
        return Ok(json!(bent(&points, num(v, "length")?, num(v, "tip")?)));
    }
    if method == "passage" {
        return Ok(passage(
            num(v, "w_in")?,
            num(v, "w_out")?,
            num(v, "tip")?,
            num(v, "slot_out")?,
            num(v, "base")?,
            num(v, "face")?,
            num(v, "top")?,
            num(v, "running")?,
        ));
    }
    let c = Cradle::read(v)?;
    match method {
        "profiles" => Ok(json!(
            c.profiles(v["leg"].as_str().context("Missing profile leg")?)?
        )),
        "elbow_z" => Ok(json!(c.elbow_z()?)),
        "block" => Ok(json!(c.block(v)?)),
        "stations" => c.stations(v),
        "numbers" => c.numbers(v),
        "hook_corner_clearance" => {
            let s = c.stations(v)?;
            let (cx, cy) = (
                SOCKET_HALF - SOCKET_CORNER,
                socket_half_length() - SOCKET_CORNER,
            );
            Ok(json!(
                SOCKET_CORNER
                    - (num(&s, "hook_tip")? - cx)
                        .max(0.0)
                        .hypot((num(&s, "y1")? - cy).max(0.0))
            ))
        }
        "document" => c.document(&v["stations"]),
        _ => Ok(json!({"values":c.values()?,"parameters":c.parameters})),
    }
}

const CENTER_Y: f64 = 182.5 + (AFT - FORWARD) / 2.0;
const FRAME_WEB: f64 = 3.0;
const FRAME_WIDTH: f64 = 196.5;
const BODY_WIDTH: f64 = 176.5;
const FRAME_DEPTH: f64 = COLLAR_D + 24.6;
const REAR_ACCESS: f64 = 5.0;
const FRAME_CORNER: f64 = 6.0;
const RAIL_BELOW: f64 = 42.1;
const SOCKET_DEPTH: f64 = 19.0;
const SCREW_LENGTH: f64 = 12.0;
const SCREW_ALLOW: f64 = 0.4;
const SCREW_GRIP: f64 = 5.8;
const HEAD_H: f64 = 3.0;
const HEAD_D: f64 = 5.5;
const PAD_HALF_Y: f64 = 6.0;
const PILOT_RELIEF: f64 = 1.5;
const DEFAULT_INNER: [f64; 6] = [-104.5, 104.5, 0.0, 290.0, 0.0, 352.0];
fn frame_values() -> Value {
    json!({"center_y":CENTER_Y,"web":FRAME_WEB,"width":FRAME_WIDTH,"body_width":BODY_WIDTH,"depth":FRAME_DEPTH,
        "rear_roof_access_extension":REAR_ACCESS,"corner_radius":FRAME_CORNER,"forming_air":0.3,
        "rail_below_seat":RAIL_BELOW,"receiver_height":23.3,
        "corbel_foot_half_depth":27.5+(FORWARD+AFT)/2.0,"corbel_slope":30_f64.to_radians().tan(),
        "tube_hole_diameter":HOLE_D,"socket_width":2.0*SOCKET_HALF,"socket_depth":SOCKET_DEPTH,
        "socket_flare":[2.0,1.0],"DEFAULT_INNER":DEFAULT_INNER,"SCREW_LENGTH":SCREW_LENGTH,
        "SCREW_LENGTH_ALLOWANCE":SCREW_ALLOW,"SCREW_GRIP":SCREW_GRIP,"SCREW_HEAD_H":HEAD_H,
        "SCREW_HEAD_D":HEAD_D,"SCREW_PAD_HALF_Y":PAD_HALF_Y,"SCREW_PILOT_RELIEF":PILOT_RELIEF})
}
fn frame_center(v: &Value) -> Result<[f64; 2]> {
    if v.get("centre").is_some() {
        pair(&v["centre"])
    } else {
        Ok([0.0, CENTER_Y])
    }
}
fn frame_datums(seat: f64) -> [f64; 3] {
    [seat - DROP - FRAME_WEB, seat - DROP, seat - RAIL_BELOW]
}
fn roof(v: &Value) -> Result<Value> {
    let [_cx, cy] = frame_center(v)?;
    let seat = opt(v, "seat", 349.0);
    Ok(
        json!({"width":FRAME_WIDTH,"front":cy-COLLAR_D/2.0-OVERHANG,"back":cy+FRAME_DEPTH/2.0+REAR_ACCESS,
        "floor":seat-FRAME_WEB,"top":seat+BRIM_T,"taper_floor":seat-FRAME_WEB,"side_reach":(FRAME_WIDTH-BODY_WIDTH)/2.0}),
    )
}
fn fasteners(v: &Value) -> Result<Vec<Value>> {
    let [cx, _cy] = frame_center(v)?;
    let r = roof(v)?;
    let ledge = num(&r, "floor")?;
    let head_seat = ledge + SCREW_GRIP;
    let heatset = interface::HEATSET_LONG_LEN;
    let bore_bottom = ledge - heatset - PILOT_RELIEF;
    let mut rows = vec![];
    for (col, x, y) in [
        ("front", 93.0, num(&r, "front")? + 32.0),
        ("back", 87.7, num(&r, "back")? - REAR_ACCESS - 11.2),
    ] {
        for side in [-1, 1] {
            let name = if side < 0 { "west" } else { "east" };
            rows.push(json!({"name":format!("{col}-{name}"),"col":col,"side":side,"x":cx+side as f64*x,"y":y,
                "ledge_z":ledge,"head_seat_z":head_seat,"head_top_z":head_seat+HEAD_H,
                "insert_top_z":ledge,"insert_bottom_z":ledge-heatset,"bore_bottom_z":bore_bottom,
                "host_bottom_z":bore_bottom-interface::WALL,"screw_length":SCREW_LENGTH,
                "screw_length_allowance":SCREW_ALLOW,"tip_z":head_seat-SCREW_LENGTH,
                "host_radius_mm":interface::HEATSET_DIA/2.0+interface::WALL}));
        }
    }
    Ok(rows)
}
fn body_half(v: &Value) -> Result<f64> {
    let [cx, _cy] = frame_center(v)?;
    fasteners(v)?
        .into_iter()
        .filter(|r| r["col"] == "front")
        .map(|r| {
            Ok((num(&r, "x")? - cx).abs()
                - num(&r, "host_radius_mm")?
                - interface::slide_slip())
        })
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .reduce(f64::min)
        .context("No front frame fasteners")
}
fn frame_numbers(v: &Value) -> Result<Value> {
    let [cx, cy] = frame_center(v)?;
    let seat = opt(v, "seat", 349.0);
    let [floor, plug, _rail] = frame_datums(seat);
    let r = roof(v)?;
    let rows = fasteners(v)?;
    let snap = Cradle::read(v)?.stations(v)?;
    let half = PLUG_W / 2.0;
    let gap = (2.0 * SOCKET_HALF - PLUG_W) / 2.0;
    let inner = v.get("inner").cloned().unwrap_or(json!(DEFAULT_INNER));
    let rear_limit = inner[1].as_f64().context("Inner east face")?
        - interface::Y_STACK_HIGH_DEPTH
        - interface::slide_slip();
    let screws: Vec<_> = rows
        .iter()
        .map(|r| {
            Ok(json!([
                num(r, "x")? - cx,
                num(r, "y")? - cy,
                num(r, "head_seat_z")? - floor,
                r["host_radius_mm"],
                r["side"],
                r["col"] == "front"
            ]))
        })
        .collect::<Result<_>>()?;
    Ok(
        json!({"color":v["color"],"viewer_deflection_ratio":v["viewer_deflection_ratio"],
        "roof_width":r["width"],"body_width":BODY_WIDTH,"front":num(&r,"front")?-cy,"back":num(&r,"back")?-cy,
        "roof_floor":num(&r,"floor")?-floor,"roof_top":num(&r,"top")?-floor,"seat":seat-floor,
        "corner_radius":FRAME_CORNER,"rear_limits":[-rear_limit-cx,rear_limit-cx],
        "rear_start":opt(v,"y_joint",200.0)-interface::slide_slip()-cy,
        "corbel_half_depth":27.5+(FORWARD+AFT)/2.0,"corbel_slope":30_f64.to_radians().tan(),
        "ledge_pad_half_y":PAD_HALF_Y,"slide_slip":interface::slide_slip(),"screw_clear_radius":interface::screw_clear_dia()/2.0,
        "head_radius":interface::head_cbore_dia()/2.0,"rear_pad_radius":HEAD_D/2.0,
        "front_head_inside":COLLAR_W/2.0+OVERHANG+interface::funnel_collar_air(),"screws":screws,
        "body_half_width":body_half(v)?,
        "brim_half_size":[COLLAR_W/2.0+OVERHANG+interface::funnel_collar_air(),COLLAR_D/2.0+OVERHANG+interface::funnel_collar_air()],
        "brim_radius":BRIM_R+interface::funnel_collar_air(),"drain_xy":[0.0,0.0],
        "socket_size":[2.0*(half+gap),2.0*(plug_half_length(half)+gap)],"socket_radius":SOCKET_CORNER,
        "socket_z":WEB,"socket_height":SOCKET_DEPTH,"socket_flare":[2.0,1.0],"hole_radius":HOLE_D/2.0,
        "web_cut_z":[-1.0,WEB+1.0],"slot_x":[snap["slot_in"],snap["slot_out"]],
        "slot_y":[SLOT_FORE-END_SLIP,SLOT_AFT+END_SLIP],"funnel":funnel_numbers(v),"forming_air":0.3,
        "forming_clip_z":[plug-floor,seat-floor]}),
    )
}
fn frame(v: &Value) -> Result<Value> {
    let method = v["method"].as_str().unwrap_or("state");
    match method {
        "state" => Ok(frame_values()),
        "datums" => Ok(json!(frame_datums(opt(v, "seat", 349.0)))),
        "roof" => roof(v),
        "fasteners" => Ok(json!(fasteners(v)?)),
        "body_half" => Ok(json!(body_half(v)?)),
        "numbers" => frame_numbers(v),
        "drain_seat" => {
            let [cx, cy] = frame_center(v)?;
            let [floor, plug, _rail] = frame_datums(opt(v, "seat", 349.0));
            let half = PLUG_W / 2.0;
            let gap = (2.0 * SOCKET_HALF - PLUG_W) / 2.0;
            Ok(
                json!({"x":cx,"y":cy,"floor_z":floor,"socket_floor_z":plug,"width":2.0*SOCKET_HALF,
                "depth":2.0*(plug_half_length(half)+gap)}),
            )
        }
        "document" => {
            let snap = Cradle::read(v)?.stations(v)?;
            let rear = DEFAULT_INNER[1]
                - interface::Y_STACK_HIGH_DEPTH
                - interface::slide_slip();
            let mut vars = variables(&[
                ("FRAME_WIDTH", FRAME_WIDTH, "g", " mm"),
                ("FRAME_BODY_WIDTH", 2.0 * body_half(v)?, "g", " mm"),
                ("FRAME_REAR_WIDTH", 2.0 * rear, "g", " mm"),
                ("FRAME_HOLE", HOLE_D, "g", " mm"),
            ])?;
            vars["FRAME_SCREWS"] = json!(format!("M3 × {} mm", format_number(SCREW_LENGTH, "g")?));
            vars["FRAME_SOCKET"] = json!(format!(
                "{} × {} mm",
                format_number(2.0 * SOCKET_HALF, "g")?,
                format_number(
                    2.0 * (plug_half_length(PLUG_W / 2.0) + (2.0 * SOCKET_HALF - PLUG_W) / 2.0),
                    ".1f"
                )?
            ));
            vars["FRAME_SLOTS"] = json!(format!(
                "{} × {} mm",
                format_number(num(&snap, "slot_out")? - num(&snap, "slot_in")?, ".2f")?,
                format_number(SLOT_AFT - SLOT_FORE + 2.0 * END_SLIP, ".1f")?
            ));
            Ok(vars)
        }
        _ => bail!("Unknown frame method {method}"),
    }
}

pub(super) fn request(v: &Value) -> Result<Value> {
    match v["part"].as_str().unwrap_or("") {
        "funnel" => funnel(v),
        "elbow-cradle" => cradle(v),
        "funnel-frame" => frame(v),
        other => bail!("Unknown zone-c scalar provider {other}"),
    }
}
