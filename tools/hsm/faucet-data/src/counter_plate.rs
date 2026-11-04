//! The 316 stainless countertop clamping plate's analytic laser-cut outline.
//!
//! The R2010 document template carries format headers, tables and blocks only.
//! Every line and circular arc in model space is constructed here.

use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use std::fmt::Write;
use std::path::Path;

use crate::{LOWER_Y, formatted};

#[derive(Clone, Copy)]
struct Dimensions {
    shank_cx: f64,
    shank_cy: f64,
    shank_diameter: f64,
    shank_radius: f64,
    pill_cx: f64,
    pill_cy: f64,
    pill_long_y: f64,
    pill_short_x: f64,
    pill_half_long: f64,
    pill_half_short: f64,
    pill_cap_radius: f64,
    pill_top_cap_cy: f64,
    pill_bot_cap_cy: f64,
    pill_left_x: f64,
    pill_right_x: f64,
    bore_front_x: f64,
    disc_reach_margin: f64,
    disc_cx: f64,
    disc_cy: f64,
    disc_radius: f64,
    disc_diameter: f64,
    fillet_radius: f64,
}

impl Dimensions {
    fn new() -> Self {
        let shank_cx = 0.0;
        let shank_cy = 0.0;
        let shank_diameter = 12.6;
        let shank_radius = shank_diameter / 2.0;
        let pill_cx = LOWER_Y;
        let pill_cy = 0.0;
        let pill_long_y = 18.15;
        let pill_short_x = 7.25;
        let pill_half_long = pill_long_y / 2.0;
        let pill_half_short = pill_short_x / 2.0;
        let pill_cap_radius = pill_half_short;
        let pill_top_cap_cy = pill_cy + (pill_half_long - pill_cap_radius);
        let pill_bot_cap_cy = pill_cy - (pill_half_long - pill_cap_radius);
        let pill_left_x = pill_cx - pill_half_short;
        let pill_right_x = pill_cx + pill_half_short;
        let bore_front_x = -16.0;
        let disc_reach_margin = 8.0;
        let disc_cx = (pill_right_x + bore_front_x) / 2.0;
        let disc_cy = 0.0;
        let disc_radius = (pill_right_x - bore_front_x) / 2.0 + disc_reach_margin;
        let disc_diameter = 2.0 * disc_radius;
        let fillet_radius = 1.5;
        Self {
            shank_cx,
            shank_cy,
            shank_diameter,
            shank_radius,
            pill_cx,
            pill_cy,
            pill_long_y,
            pill_short_x,
            pill_half_long,
            pill_half_short,
            pill_cap_radius,
            pill_top_cap_cy,
            pill_bot_cap_cy,
            pill_left_x,
            pill_right_x,
            bore_front_x,
            disc_reach_margin,
            disc_cx,
            disc_cy,
            disc_radius,
            disc_diameter,
            fillet_radius,
        }
    }
    fn datums(self) -> Value {
        json!({"shank_cx":self.shank_cx,"shank_cy":self.shank_cy,
            "shank_diameter":self.shank_diameter,"shank_radius":self.shank_radius,
            "pill_cx":self.pill_cx,"pill_cy":self.pill_cy,"pill_long_y":self.pill_long_y,
            "pill_short_x":self.pill_short_x,"pill_half_long":self.pill_half_long,
            "pill_half_short":self.pill_half_short,"pill_cap_radius":self.pill_cap_radius,
            "pill_top_cap_cy":self.pill_top_cap_cy,"pill_bot_cap_cy":self.pill_bot_cap_cy,
            "pill_left_x":self.pill_left_x,"pill_right_x":self.pill_right_x,
            "bore_front_x":self.bore_front_x,"disc_reach_margin":self.disc_reach_margin,
            "disc_cx":self.disc_cx,"disc_cy":self.disc_cy,"disc_radius":self.disc_radius,
            "disc_diameter":self.disc_diameter,"fillet_radius":self.fillet_radius})
    }
    fn rim_y_lower(self, x: f64) -> Result<f64> {
        let squared = self.disc_radius.powi(2) - (x - self.disc_cx).powi(2);
        if squared < 0.0 {
            bail!("math domain error");
        }
        Ok(self.disc_cy - squared.sqrt())
    }
    fn corner(self, wall_x: f64, material_side: f64, r: f64) -> Result<[[f64; 2]; 3]> {
        let x_c = wall_x + material_side * r;
        let dx = x_c - self.disc_cx;
        let inner_r = self.disc_radius - r;
        let squared = inner_r * inner_r - dx * dx;
        if squared < 0.0 {
            bail!("math domain error");
        }
        if inner_r == 0.0 {
            bail!("division by zero");
        }
        let y_c = self.disc_cy - squared.sqrt();
        let ux = (x_c - self.disc_cx) / inner_r;
        let uy = (y_c - self.disc_cy) / inner_r;
        Ok([
            [x_c, y_c],
            [wall_x, y_c],
            [
                self.disc_cx + self.disc_radius * ux,
                self.disc_cy + self.disc_radius * uy,
            ],
        ])
    }
    fn variables(self) -> Value {
        formatted(&[
            ("PLATE_D", self.disc_diameter, ".4g", " mm"),
            ("DISC_CX", self.disc_cx, ".4g", " mm"),
            ("BORE_FRONT_X", self.bore_front_x, ".4g", " mm"),
            (
                "TOP_OF_DISC_Y",
                self.disc_cy + self.disc_radius,
                ".4g",
                " mm",
            ),
            ("SHANK_HOLE_D", self.shank_diameter, ".4g", " mm"),
            (
                "SHANK_LEFT_WALL_X",
                self.shank_cx - self.shank_radius,
                ".4g",
                " mm",
            ),
            (
                "SHANK_RIGHT_WALL_X",
                self.shank_cx + self.shank_radius,
                ".4g",
                " mm",
            ),
            ("FLAVOR_TUBE_X", self.pill_cx, ".4g", " mm"),
            ("PILL_L", self.pill_long_y, ".4g", " mm"),
            ("PILL_W", self.pill_short_x, ".4g", " mm"),
            ("PILL_HALF_LONG", self.pill_half_long, ".4g", " mm"),
            ("PILL_HALF_SHORT", self.pill_half_short, ".4g", " mm"),
            ("PILL_CAP_R", self.pill_cap_radius, ".4g", " mm"),
            ("PILL_TOP_CAP_CY", self.pill_top_cap_cy, ".4g", " mm"),
            ("PILL_BOT_CAP_CY", self.pill_bot_cap_cy, ".4g", " mm"),
            ("PILL_LEFT_X", self.pill_left_x, ".4g", " mm"),
            ("PILL_RIGHT_X", self.pill_right_x, ".4g", " mm"),
            ("FILLET_R", self.fillet_radius, ".4g", " mm"),
            ("STEEL_PLATE_D", self.disc_diameter, ".4g", " mm"),
            ("STEEL_SHANK_HOLE_D", self.shank_diameter, ".4g", " mm"),
            ("STEEL_PILL_L", self.pill_long_y, ".4g", " mm"),
            ("STEEL_PILL_W", self.pill_short_x, ".4g", " mm"),
        ])
    }
    fn outline(self) -> Result<Vec<Entity>> {
        let top = [self.disc_cx, self.disc_cy + self.disc_radius];
        let shank_left = self.shank_cx - self.shank_radius;
        let shank_right = self.shank_cx + self.shank_radius;
        let disc_center = [self.disc_cx, self.disc_cy];
        let [sl_c, sl_wt, sl_rt] = self.corner(shank_left, -1.0, self.fillet_radius)?;
        let [sr_c, sr_wt, sr_rt] = self.corner(shank_right, 1.0, self.fillet_radius)?;
        let [pl_c, pl_wt, pl_rt] = self.corner(self.pill_left_x, -1.0, self.fillet_radius)?;
        let [pr_c, pr_wt, pr_rt] = self.corner(self.pill_right_x, 1.0, self.fillet_radius)?;
        Ok(vec![
            Entity::ccw_arc(disc_center, self.disc_radius, top, sl_rt),
            Entity::ccw_arc(sl_c, self.fillet_radius, sl_rt, sl_wt),
            Entity::Line(sl_wt, [shank_left, self.shank_cy]),
            Entity::Arc(
                [self.shank_cx, self.shank_cy],
                self.shank_radius,
                0.0,
                180.0,
            ),
            Entity::Line([shank_right, self.shank_cy], sr_wt),
            Entity::ccw_arc(sr_c, self.fillet_radius, sr_wt, sr_rt),
            Entity::ccw_arc(disc_center, self.disc_radius, sr_rt, pl_rt),
            Entity::ccw_arc(pl_c, self.fillet_radius, pl_rt, pl_wt),
            Entity::Line(pl_wt, [self.pill_left_x, self.pill_top_cap_cy]),
            Entity::Arc(
                [self.pill_cx, self.pill_top_cap_cy],
                self.pill_cap_radius,
                0.0,
                180.0,
            ),
            Entity::Line([self.pill_right_x, self.pill_top_cap_cy], pr_wt),
            Entity::ccw_arc(pr_c, self.fillet_radius, pr_wt, pr_rt),
            Entity::ccw_arc(disc_center, self.disc_radius, pr_rt, top),
        ])
    }
}

enum Entity {
    Line([f64; 2], [f64; 2]),
    Arc([f64; 2], f64, f64, f64),
}
impl Entity {
    fn ccw_arc(center: [f64; 2], radius: f64, start: [f64; 2], end: [f64; 2]) -> Self {
        let deg = 180.0 / std::f64::consts::PI;
        let start_angle = (start[1] - center[1]).atan2(start[0] - center[0]) * deg;
        let mut end_angle = (end[1] - center[1]).atan2(end[0] - center[0]) * deg;
        if end_angle <= start_angle {
            end_angle += 360.0;
        }
        Self::Arc(center, radius, start_angle, end_angle)
    }
    fn value(&self) -> Value {
        match self {
            Self::Line(a, b) => {
                json!({"type":"LINE","start":[a[0],a[1],0.0],"end":[b[0],b[1],0.0],"layer":"0"})
            }
            Self::Arc(c, r, start, end) => json!({"type":"ARC","center":[c[0],c[1],0.0],"radius":r,
                "start_angle":start,"end_angle":end,"layer":"0"}),
        }
    }
    fn append_dxf(&self, text: &mut String, handle: usize) {
        // Handles 0x100 and above are reserved for the calculated entities;
        // template object handles end below this range. Every entity belongs
        // to the template's *Model_Space block record (handle 0x17), layer 0.
        match self {
            Self::Line(a, b) => {
                write!(
                    text,
                    "  0\nLINE\n  5\n{handle:X}\n330\n17\n100\nAcDbEntity\n  8\n0\n100\nAcDbLine\n"
                )
                .expect("string write");
                for (base, p) in [(10, a), (11, b)] {
                    writeln!(
                        text,
                        "{base:>3}\n{}\n{:>3}\n{}\n{:>3}\n0.0",
                        p[0],
                        base + 10,
                        p[1],
                        base + 20
                    )
                    .expect("string write");
                }
            }
            Self::Arc(c, r, start, end) => {
                write!(text,"  0\nARC\n  5\n{handle:X}\n330\n17\n100\nAcDbEntity\n  8\n0\n100\nAcDbCircle\n 10\n{}\n 20\n{}\n 30\n0.0\n 40\n{}\n100\nAcDbArc\n 50\n{}\n 51\n{}\n",c[0],c[1],r,start,end).expect("string write");
            }
        }
    }
}

fn write_dxf(path: &Path, entities: &[Entity]) -> Result<()> {
    let mut body = String::new();
    for (index, entity) in entities.iter().enumerate() {
        entity.append_dxf(&mut body, 0x100 + index);
    }
    let text = include_str!("r2010-template.dxf.in")
        .replace("{{ENTITIES}}\n", &body)
        .replace("{{HANDSEED}}", &format!("{:X}", 0x100 + entities.len()));
    let bytes = hsm_documents::canonicalize_dxf(text.as_bytes());
    hsm_documents::write_if_changed(path, &bytes)?;
    Ok(())
}

pub fn dispatch(request: &Value) -> Result<Value> {
    let d = Dimensions::new();
    if let Some(x) = request["rim_x"].as_f64() {
        return Ok(json!(d.rim_y_lower(x)?));
    }
    if let Some(wall) = request["wall_x"].as_f64() {
        let side = request["material_side"]
            .as_f64()
            .context("corner material side")?;
        let radius = request["radius"].as_f64().unwrap_or(d.fillet_radius);
        return Ok(json!(d.corner(wall, side, radius)?));
    }
    if let Some(arc) = request.get("arc") {
        let point = |key: &str| -> Result<[f64; 2]> {
            Ok([
                arc[key][0].as_f64().context("arc X")?,
                arc[key][1].as_f64().context("arc Y")?,
            ])
        };
        return Ok(Entity::ccw_arc(
            point("center")?,
            arc["radius"].as_f64().context("arc radius")?,
            point("start")?,
            point("end")?,
        )
        .value());
    }
    let entities = d.outline()?;
    if let Some(path) = request["output"].as_str() {
        write_dxf(Path::new(path), &entities)?;
    }
    Ok(json!({"datums":d.datums(),"variables":d.variables(),
        "entities":entities.iter().map(Entity::value).collect::<Vec<_>>(),
        "version":"AC1024","units":4}))
}
