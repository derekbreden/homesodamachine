//! Funnel, compliant cradle and casting-tool scalar designs.
use crate::{num, opt, variables};
use anyhow::{Context, Result, bail};
use hsm_documents::format_number;
use hsm_enclosure_interface as interface;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, fs, path::Path};

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

fn cover(v: &Value) -> Result<Value> {
    let (plate_t, overhang, skirt_depth, skirt_wall, running, lead_h, lead_inset) =
        (3.0, 1.5, 6.0, 3.0, 0.25, 1.4, 0.7);
    let (extension, relief, overrun, overlap, inside_overlap) = (4.0, 1.2, 1.0, 0.01, 0.02);
    let (mouth_w, mouth_d) = (COLLAR_W - 2.0 * COLLAR_WALL, COLLAR_D - 2.0 * COLLAR_WALL);
    let width = COLLAR_W + 2.0 * (OVERHANG + overhang);
    let seated = COLLAR_D + 2.0 * (OVERHANG + overhang);
    let depth = seated + extension;
    let (sw, sd, sr) = (
        mouth_w - 2.0 * running,
        mouth_d - 2.0 * running,
        MOUTH_R - running,
    );
    Ok(
        json!({"values":{"PLATE_T":plate_t,"OVERHANG":overhang,"SKIRT_DEPTH":skirt_depth,"SKIRT_WALL":skirt_wall,
        "RUNNING_AIR":running,"LEAD_H":lead_h,"LEAD_INSET":lead_inset,"FRONT_EXTENSION":extension,
        "FRONT_RELIEF":relief,"CUT_OVERRUN":overrun,"SKIRT_PLATE_OVERLAP":overlap,"INNER_CUT_OVERLAP":inside_overlap,
        "MOUTH_W":mouth_w,"MOUTH_D":mouth_d,"WIDTH":width,"SEATED_DEPTH":seated,"DEPTH":depth},
        "skirt":[sw,sd,sr],"numbers":{"name":"funnel-cover","print_name":"funnel-cover-print","color":v["color"],
            "plate_half_size":[width/2.0,seated/2.0],"plate_corner_radius":BRIM_R+overhang,"plate_thickness":plate_t,
            "front_extension":extension,"relief_size":[width+2.0*overrun,extension+overrun],"relief_z":[-overrun,relief],
            "relief_center_y":-seated/2.0-(extension+overrun)/2.0+0.5,
            "skirt_sections":[[sw-2.0*lead_inset,sd-2.0*lead_inset,sr-lead_inset,-skirt_depth],
                [sw,sd,sr,-skirt_depth+lead_h],[sw,sd,sr,overlap]],
            "skirt_inside":[sw-2.0*skirt_wall,sd-2.0*skirt_wall,sr-skirt_wall,-skirt_depth-overrun,inside_overlap]},
        "variables":variables(&[("PLATE",plate_t,"g"," mm"),("SKIRT",skirt_depth,"g"," mm"),
            ("WALL",skirt_wall,"g"," mm"),("WIDTH",width,"g"," mm"),("DEPTH",depth,".3f"," mm"),
            ("OVERHANG",overhang,"g"," mm"),("AIR",running,"g"," mm"),("FRONT_EXTENSION",extension,"g"," mm"),
            ("FRONT_RELIEF",relief,"g"," mm"),("PRINT_HEIGHT",plate_t+skirt_depth,"g"," mm")])?}),
    )
}
const FINISH: f64 = 0.30;
const JOIN_ALLOWANCE: f64 = 0.01;
const SHELL: f64 = 5.0;
const CORBEL: f64 = 0.5;
const BASE: f64 = 5.0;
const FLANGE_T: f64 = 5.0;
const FLANGE_MARGIN: f64 = 16.0;
const FLANGE_R: f64 = 47.0;
const BOLT_EDGE: f64 = 6.0;
const BOLT_STATION: f64 = 50.0;
const LOCATOR_D: f64 = 8.0;
const LOCATOR_H: f64 = 3.0;
const LOCATOR_CLEAR: f64 = 0.60;
const LOCATOR_TRAVEL: f64 = 1.5;
const LOCATOR_X: f64 = 25.0;
const LOCATOR_FRONT: f64 = 11.0;
const ROD_LENGTH: f64 = 25.0;
const ROD_CLEAR: f64 = 0.40;
const ROD_GUIDE: f64 = 8.0;
const ROD_SOCKET: f64 = 1.5;
const FLOOR_RESERVE: f64 = 0.7;
const CHAMBER_D: f64 = 299.72;
fn mold_values() -> Value {
    json!({"finish_allowance":FINISH,"forming_join_allowance":JOIN_ALLOWANCE,"shell_thickness":SHELL,
        "corbel_run_per_rise":CORBEL,"base_thickness":BASE,"bolt_pocket_width":12.0,
        "flange_thickness":FLANGE_T,"flange_margin":FLANGE_MARGIN,"flange_radius":FLANGE_R,
        "bolt_diameter":5.0,"bolt_edge_margin":BOLT_EDGE,"bolt_station":BOLT_STATION,
        "locator_diameter":LOCATOR_D,"locator_height":LOCATOR_H,"locator_leadin":1.0,
        "locator_clearance":LOCATOR_CLEAR,"locator_slot_travel":LOCATOR_TRAVEL,"locator_x":LOCATOR_X,
        "locator_front_land":LOCATOR_FRONT,"rod_diameter":SPOUT_ID,"rod_length":ROD_LENGTH,
        "rod_clearance":ROD_CLEAR,"rod_guide_length":ROD_GUIDE,"rod_seat_wall":SHELL,
        "rod_socket_diameter":SPOUT_ID+ROD_CLEAR,"rod_socket_depth":ROD_SOCKET,"rod_end_depth":ROD_SOCKET,
        "vent_diameter":4.0,"pour_diameter":11.0,"floor_reserve":FLOOR_RESERVE,"pry_width":16.0,
        "pry_depth":5.0,"pry_height":1.0,"tolerance":0.0001,"chamber_diameter":CHAMBER_D})
}
fn mold_numbers(v: &Value) -> Result<Value> {
    let mut n = funnel_numbers(v);
    n.as_object_mut()
        .unwrap()
        .extend(mold_values().as_object().unwrap().clone());
    let (top, end) = (num(&n, "top_z")?, num(&n, "end_z")?);
    let floor = end - ROD_SOCKET - SHELL - FLOOR_RESERVE;
    let back = top + FLANGE_T;
    let width = APRON_W + 2.0 * FLANGE_MARGIN;
    let depth = APRON_D + 2.0 * APRON_Y.abs() + 2.0 * FLANGE_MARGIN;
    let (bx, by) = (width / 2.0 - BOLT_EDGE, depth / 2.0 - BOLT_EDGE);
    let (z0, z1) = (floor + BASE, top - FLANGE_T);
    let run = (z1 - z0) * CORBEL;
    let port_x = APRON_W / 2.0 - 14.5;
    let front_y = APRON_Y - APRON_D / 2.0 + 10.0;
    let rear_y = APRON_Y + APRON_D / 2.0 - 12.0;
    let locator_front = APRON_Y - APRON_D / 2.0 - LOCATOR_FRONT;
    let mut bolts = vec![];
    for side in [-1.0, 1.0] {
        for station in [-1.0, 1.0] {
            bolts.push([side * bx, station * BOLT_STATION]);
        }
    }
    for side in [-1.0, 1.0] {
        for station in [-1.0, 1.0] {
            bolts.push([station * BOLT_STATION, side * by]);
        }
    }
    let more = json!({"floor_z":floor,"back_z":back,"flange_size":[width,depth],"base_size":[width-2.0*run,depth-2.0*run],
        "base_radius":FLANGE_R-run,"corbel_z":[z0,z1],"bolt_limits":[bx,by],"bolt_xy":bolts,
        "locator_xy":[[LOCATOR_X,locator_front],[-LOCATOR_X,locator_front]],"pour_xy":[-port_x,front_y],
        "vent_xy":[[port_x,front_y],[port_x,rear_y],[-port_x,rear_y],[-APRON_W/2.0+7.0,0.0],[APRON_W/2.0-7.0,0.0]]});
    n.as_object_mut()
        .unwrap()
        .extend(more.as_object().unwrap().clone());
    for name in ["cavity", "core", "funnel", "rod"] {
        n[format!("{name}_color")] = v[format!("{name}_color")].clone();
    }
    Ok(n)
}
fn breathers(base_width: f64, core_back: f64) -> Value {
    json!({"diameter_mm":1.5,
        "cavity":{"entry_xyz_mm":[[-base_width/2.0,-30.0,2.5],[base_width/2.0,30.0,2.5]],
            "drill_axes":[[1,0,0],[-1,0,0]],"depth_mm":3.2,"face":"vertical sides of the flat base, clear of the catch tray"},
        "core":{"entry_xyz_mm":[[-40.0,-30.0,core_back],[40.0,30.0,core_back]],"drill_axes":[[0,0,-1],[0,0,-1]],
            "depth_mm":1.8,"face":"flat outer dry back"},
        "method":"Drill through the printed skins into sparse infill after printing with a depth stop; keep dry faces and holes uncoated. CAD blind holes would receive sealed slicer walls."})
}
fn load_screen(m: &Value, bottom: f64) -> Result<Value> {
    let span = num(m, "w")?;
    let pressure = 0.001;
    let head = num(m, "top_z")? + FLANGE_T - bottom;
    Ok(
        json!({"model":"silicone hydrostatic head and conservative uniform process-load screen",
        "span_mm":span,"pressure_kpa":pressure*1000.0,"silicone_density_assumption_kg_m3":1130,
        "maximum_silicone_head_mm":head,"head_pressure_kpa":1130.0*9.81*(head/1000.0)/1000.0,
        "pressure_force_n":pressure*span.powi(2),
        "condition":"complete mold inside chamber; fill, vents, rod guide and drilled dry-side infill breathers open to chamber air",
        "process":"six walls, six top/bottom layers and 15% gyroid; slow evacuation and venting while silicone is fluid",
        "scope":"Applied liquid load only. No stiffness, lifetime or pressure rating is inferred from infill percentage."}),
    )
}
fn design(v: &Value) -> Result<Value> {
    let n = mold_numbers(v)?;
    let m = &v["dimensions"];
    let (top, neck, end) = (num(m, "top_z")?, num(m, "neck_z")?, num(m, "end_z")?);
    let (floor, back) = (num(&n, "floor_z")?, num(&n, "back_z")?);
    let [flange_w, flange_d] = pair(&n["flange_size"])?;
    let [base_w, base_d] = pair(&n["base_size"])?;
    let guide_r = (SPOUT_ID + ROD_CLEAR) / 2.0;
    let guide_top = neck + ROD_GUIDE;
    let dry_radius = guide_r + (back - guide_top) * CORBEL;
    let rod_top = end - ROD_SOCKET + ROD_LENGTH;
    let mut sizes = BTreeMap::new();
    let mut volumes = BTreeMap::new();
    for (name, facts) in v["parts"].as_object().context("Missing mold part facts")? {
        sizes.insert(name, facts["size"].clone());
        volumes.insert(name, num(facts, "volume")? / 1000.0);
    }
    Ok(
        json!({"dimensions_mm":sizes,"volume_ml":volumes,"shell_thickness_mm":SHELL,
        "flange_thickness_mm":FLANGE_T,"minimum_cavity_backing_mm":v["minimum_backing"],
        "backing_join_allowance_mm":JOIN_ALLOWANCE,"minimum_core_backing_mm":v["minimum_core_backing"],
        "liquid_containment":v["containment"],"parting_z_mm":top-floor,"finish_allowance_mm":FINISH,
        "casting_scope":"whole finished funnel with flat-bottomed integral roof apron, rectangular block, flat bearing face and straight 6 mm outlet",
        "flange_plan_mm":[flange_w,flange_d],"flange_corner_radius_mm":FLANGE_R,"flange_margin_mm":FLANGE_MARGIN,
        "plug_blank_mm":[PLUG_W,2.0*plug_half_length(PLUG_W/2.0)],
        "rod_support":{"engagement_mm":ROD_GUIDE-FINISH,"guide_diameter_mm":2.0*guide_r,
            "dry_shank_diameter_mm":SPOUT_ID,"guide_diametral_clearance_mm":ROD_CLEAR,
            "guide_length_mm":ROD_GUIDE-FINISH,"guide_top_mm":guide_top-floor,"guide_open":true,
            "rod_projection_above_guide_mm":rod_top-guide_top,"straight_dry_wall_mm":SHELL,
            "registration":"open upper guide and lower blind floor seat",
            "retention":"gravity; rod rests on lower floor and lifts out from the dry back",
            "air_path":"open annular passage to dry back","flash":"trim guide overflow at bowl throat and lower-seat collar flush with block bottom"},
        "rod_socket":{"diameter_mm":SPOUT_ID+ROD_CLEAR,"depth_mm":ROD_SOCKET,"rod_end_depth_mm":ROD_SOCKET,
            "floor_backing_mm":SHELL,"reference":"blind pilot seat below block bottom; bare floor establishes axial datum"},
        "rod":{"material":"304 stainless steel","diameter_mm":SPOUT_ID,"length_mm":ROD_LENGTH,
            "profile":"straight stock cylinder","supplier":"uxcell 25-piece pack","url":"https://www.amazon.com/dp/B07Z18CKCY",
            "finishing":"clean and apply release"},
        "funnel_to_mould_z_translation_mm":-floor,
        "finished_funnel_step_sha256":digest(&root(v)?.join("hardware/printed-parts/zone-c/funnel/funnel.step"))?,
        "locators":{"diameter_mm":LOCATOR_D,"height_mm":LOCATOR_H,"radial_clearance_mm":LOCATOR_CLEAR,
            "slot_travel_each_way_mm":LOCATOR_TRAVEL,"centres_xy_mm":n["locator_xy"]},
        "clamping":{"hole_diameter_mm":5.0,"centres_xy_mm":n["bolt_xy"],"fastener":"M4 x 20 with 9 mm OD washers and nuts; or small clamps on flange"},
        "ports":{"fill_diameter_mm":11.0,"vent_diameter_mm":4.0,"fill_xy_mm":n["pour_xy"],"vent_xy_mm":n["vent_xy"]},
        "print_bases":{"cavity_plan_mm":[base_w,base_d],"cavity_corner_radius_mm":n["base_radius"],
            "base_thickness_mm":BASE,"corbel_run_per_rise":CORBEL,"corbel_angle_from_bed_deg":(1.0/CORBEL).atan().to_degrees(),
            "corbel_print_z_mm":[BASE,n["corbel_z"][1].as_f64().context("Corbel top")?-floor],
            "bolt_access_pocket_width_mm":12.0,"bolt_access_open_downward":true,
            "bolt_access_inner_wall_height_mm":(BOLT_EDGE+4.6)/CORBEL,"core":"flat dry back with one circular tapered access hole"},
        "dry_opening_mm":2.0*dry_radius,"dry_opening_depth_mm":2.0*dry_radius,
        "dry_opening_shape":"circular conical access to straight rod guide","postprint_breathers":breathers(base_w,back-floor),
        "ramp_print_z_mm":{"cavity":[neck-floor,num(m,"ramp_top_z")?-floor],"core":[back-num(m,"ramp_top_z")?,back-neck]},
        "nominal_chamber_diameter_mm":CHAMBER_D,"load_screen":load_screen(m,end)?,
        "status":"Complete two-body tooling with flat print bases and straight stock steel rod; native geometry verified"}),
    )
}
fn artifact_report(v: &Value) -> Result<Value> {
    let facts = &v["facts"];
    let numbers = &v["numbers"];
    let mut parts = serde_json::Map::new();
    for name in ["cavity", "core", "funnel", "rod"] {
        let f = &facts[name];
        let lo = crate::point(&f["bounds"][0])?;
        let hi = crate::point(&f["bounds"][1])?;
        parts.insert(
            name.into(),
            json!({"size":[hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]],"volume":f["volume_mm3"]}),
        );
    }
    let mut input = v.clone();
    input["parts"] = Value::Object(parts);
    input["dimensions"] = json!({"w":COLLAR_W,"d":COLLAR_D,"top_z":numbers["top_z"],
        "ramp_top_z":numbers["ramp_z"][0],"neck_z":numbers["ramp_z"][1],"end_z":numbers["end_z"],
        "ncx":0.0,"ncy":0.0,"out_w":APRON_W,"out_d":APRON_D+2.0*APRON_Y.abs()});
    let check = &facts["checks"];
    input["minimum_backing"] = check["minimum_cavity_backing_mm"].clone();
    input["minimum_core_backing"] = check["minimum_core_backing_mm"].clone();
    input["containment"] = check["liquid_containment"].clone();
    let mut info = design(&input)?;
    info["cavity_backing_scope"] = check["cavity_backing_scope"].clone();
    let output = Path::new(v["output"].as_str().context("Missing mold output path")?);
    let mut radius = 0_f64;
    let mut hashes = BTreeMap::new();
    for name in ["cavity", "core"] {
        let raw = fs::read(output.join(format!("{name}.stl")))?;
        if raw.len() < 84 || (raw.len() - 84) % 50 != 0 {
            bail!("Malformed binary STL for {name}")
        }
        for row in raw[84..].chunks_exact(50) {
            for vertex in 0..3 {
                let at = 12 + vertex * 12;
                let x = f32::from_le_bytes(row[at..at + 4].try_into()?) as f64;
                let y = f32::from_le_bytes(row[at + 4..at + 8].try_into()?) as f64;
                radius = radius.max((x * x + y * y).sqrt());
            }
        }
        for suffix in ["step", "stl", "step.mesh", "step.npz"] {
            let path = format!("{name}.{suffix}");
            hashes.insert(path.clone(), digest(&output.join(path))?);
        }
    }
    info["enclosing_diameter_mm"] = json!(2.0 * radius);
    info["chamber_radial_clearance_mm"] = json!(CHAMBER_D / 2.0 - radius);
    if CHAMBER_D / 2.0 - radius <= 0.0 {
        bail!("Mold exceeds nominal chamber diameter")
    }
    info["volume_measurement_scope"] = json!(
        "Numerical integration of the fine f64 models; printed facets have their own bound records."
    );
    info["shell_sha256"] = json!(hashes);
    info["status"] = json!(
        "Complete two-body tooling with flat print bases and straight stock steel rod; authored fine geometry verified"
    );
    Ok(info)
}
fn mold(v: &Value) -> Result<Value> {
    match v["method"].as_str().unwrap_or("state") {
        "numbers" => mold_numbers(v),
        "design" => design(v),
        "report" => artifact_report(v),
        "breathers" => Ok(breathers(num(v, "base_width")?, num(v, "core_back")?)),
        "load_screen" => load_screen(&v["dimensions"], num(v, "bottom")?),
        "part_facts" => {
            let lo = crate::point(&v["facts"]["bounds"][0])?;
            let hi = crate::point(&v["facts"]["bounds"][1])?;
            Ok(json!({"xlen":hi[0]-lo[0],"ylen":hi[1]-lo[1],"zlen":hi[2]-lo[2]}))
        }
        _ => Ok(mold_values()),
    }
}

pub(super) fn request(v: &Value) -> Result<Value> {
    match v["part"].as_str().unwrap_or("") {
        "funnel" => funnel(v),
        "elbow-cradle" => cradle(v),
        "funnel-frame" => frame(v),
        "funnel-cover" => cover(v),
        "funnel-mold" => mold(v),
        other => bail!("Unknown zone-c scalar provider {other}"),
    }
}
