//! The pump-port scan reader, elbow recipe and independent smooth-solid measurements.
use crate::{color, num, opt, point, variables};
use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use std::{collections::BTreeMap, f64::consts::PI, fs};

const BARB_BORE: f64 = 9.0;
const BARB_DEPTH: f64 = 11.0;
const TUBE_D: f64 = 6.35;
const TUBE_BORE: f64 = 6.10;
const TUBE_DEPTH: f64 = 15.0;
const PASSAGE: f64 = 4.40;
const MIN_WALL: f64 = 2.80;
const BARB_OD: f64 = BARB_BORE + 2.0 * MIN_WALL;
const TUBE_OD: f64 = TUBE_BORE + 2.0 * MIN_WALL;
const TUBE_STOP: f64 = 3.50;
const TUBE_MOUTH: f64 = TUBE_STOP + TUBE_DEPTH;
const NECK: f64 = TUBE_STOP + 3.0;
const CLAMP_BAND: f64 = 9.0;
const BAND_AIR: f64 = 1.0;
const ENTRY: f64 = 0.40;

fn installed_od(relaxed: f64, bore: f64, opened: f64) -> f64 {
    (relaxed.powi(2) + opened.powi(2) - bore.powi(2)).sqrt()
}
fn entry_height() -> f64 {
    ENTRY * 60_f64.to_radians().tan()
}
fn neck_radius(y: f64) -> f64 {
    let t = (y / NECK).clamp(0.0, 1.0);
    let blend = t.powi(3) * (10.0 + t * (-15.0 + 6.0 * t));
    BARB_OD / 2.0 + (TUBE_OD - BARB_OD) / 2.0 * blend
}
fn integral<F: Fn(f64) -> f64>(f: F, a: f64, b: f64) -> f64 {
    fn panel(a: f64, b: f64, fa: f64, fm: f64, fb: f64) -> f64 {
        (b - a) * (fa + 4.0 * fm + fb) / 6.0
    }
    fn refine<F: Fn(f64) -> f64>(
        f: &F,
        a: f64,
        b: f64,
        fa: f64,
        fm: f64,
        fb: f64,
        whole: f64,
        epsilon: f64,
        depth: u8,
    ) -> f64 {
        let mid = (a + b) / 2.0;
        let left = f((a + mid) / 2.0);
        let right = f((mid + b) / 2.0);
        let first = panel(a, mid, fa, left, fm);
        let second = panel(mid, b, fm, right, fb);
        let change = first + second - whole;
        if depth == 0 || change.abs() <= 15.0 * epsilon {
            first + second + change / 15.0
        } else {
            refine(f, a, mid, fa, left, fm, first, epsilon / 2.0, depth - 1)
                + refine(f, mid, b, fm, right, fb, second, epsilon / 2.0, depth - 1)
        }
    }
    let (fa, fm, fb) = (f(a), f((a + b) / 2.0), f(b));
    refine(&f, a, b, fa, fm, fb, panel(a, b, fa, fm, fb), 1e-7, 20)
}

struct Sleeve {
    rows: BTreeMap<&'static str, Vec<[f64; 2]>>,
    crest: f64,
    root: f64,
    tube_axis: f64,
    foot: f64,
    barb_installed: f64,
    tube_installed: f64,
}
impl Sleeve {
    fn read(v: &Value) -> Result<Self> {
        let path = v["parameters"]
            .as_str()
            .context("Missing pump parameter path")?;
        let data: Value =
            serde_json::from_slice(&fs::read(path).with_context(|| format!("Reading {path}"))?)?;
        let mut rows = BTreeMap::new();
        let (mut crest, mut root) = (f64::NEG_INFINITY, f64::NEG_INFINITY);
        for (port, key) in [("suction", "port_yminus"), ("discharge", "port_yplus")] {
            let raw = data["ports"][key]["profile"]
                .as_array()
                .context("Missing scanned barb profile")?;
            let mut profile: Vec<[f64; 2]> = raw
                .iter()
                .map(|r| Ok([-num(r, "distance_from_tip_mm")?, 2.0 * num(r, "radius_mm")?]))
                .collect::<Result<_>>()?;
            profile.sort_by(|a, b| a[0].total_cmp(&b[0]).then(a[1].total_cmp(&b[1])));
            let nearest = profile
                .iter()
                .min_by(|a, b| {
                    (a[0] - BARB_DEPTH)
                        .abs()
                        .total_cmp(&(b[0] - BARB_DEPTH).abs())
                })
                .context("Empty scanned barb")?;
            root = root.max(nearest[1]);
            let engaged = profile
                .iter()
                .filter(|r| r[0] <= BARB_DEPTH)
                .map(|r| r[1])
                .reduce(f64::max)
                .context("No engaged barb rows")?;
            crest = crest.max(engaged);
            rows.insert(port, profile);
        }
        let barb_installed = installed_od(BARB_OD, BARB_BORE, crest);
        let tube_installed = installed_od(TUBE_OD, TUBE_BORE, TUBE_D);
        let tube_axis = -(BARB_DEPTH - CLAMP_BAND) + BAND_AIR + tube_installed / 2.0;
        let foot = tube_axis / 2_f64.sqrt() + PASSAGE / 2.0 + MIN_WALL;
        Ok(Self {
            rows,
            crest,
            root,
            tube_axis,
            foot,
            barb_installed,
            tube_installed,
        })
    }
    fn foot_neck_end(&self) -> f64 {
        let c = 2_f64.sqrt() * self.foot - self.tube_axis;
        let (mut lo, mut hi) = (0.0, NECK);
        for _ in 0..48 {
            let mid = (lo + hi) / 2.0;
            let radius =
                neck_radius(mid).max(((BARB_OD / 2.0).powi(2) - mid * mid).max(0.0).sqrt());
            if radius > mid + c { lo = mid } else { hi = mid }
        }
        (lo + hi) / 2.0
    }
    fn foot_area(&self) -> f64 {
        let r = BARB_OD / 2.0;
        let c = 2_f64.sqrt() * self.foot - self.tube_axis;
        let negative = |theta: f64| {
            let (y, q) = (r * theta.sin(), r * theta.cos());
            let u = y + c;
            let width = if u < 0.0 {
                q
            } else {
                (q * q - u * u).max(0.0).sqrt()
            };
            2.0 * 2_f64.sqrt() * width * q
        };
        let positive = |y: f64| {
            let radius2 = neck_radius(y).powi(2).max(r * r - y * y);
            2.0 * 2_f64.sqrt() * (radius2 - (y + c).powi(2)).max(0.0).sqrt()
        };
        integral(negative, -PI / 2.0, 0.0) + integral(positive, 0.0, self.foot_neck_end())
    }
    fn volume(&self) -> f64 {
        let (rb, rt) = (BARB_OD / 2.0, TUBE_OD / 2.0);
        let positive = |theta: f64| {
            let (y, q) = (rb * theta.sin(), rb * theta.cos());
            let r = neck_radius(y);
            if q >= r {
                return (2.0 * q * (self.tube_axis + BARB_DEPTH) + PI * q * q / 2.0) * q;
            }
            let section = 2.0 * q * (self.tube_axis + BARB_DEPTH) + PI * r * r
                - q * (r * r - q * q).max(0.0).sqrt()
                - r * r * (q / r).clamp(-1.0, 1.0).asin();
            section * q
        };
        let mut outer = PI * rb * rb * (self.tube_axis + BARB_DEPTH) / 2.0
            + PI * rb.powi(3) / 3.0
            + integral(positive, 0.0, PI / 2.0)
            + PI * rt * rt * (TUBE_MOUTH - rb);
        let c = 2_f64.sqrt() * self.foot - self.tube_axis;
        let cap = |r: f64, u: f64| {
            if u >= r {
                return 0.0;
            }
            r * r * (u / r).clamp(-1.0, 1.0).acos() - u * (r * r - u * u).max(0.0).sqrt()
        };
        let foot_negative = |theta: f64| {
            let (y, q) = (rb * theta.sin(), rb * theta.cos());
            let u = y + c;
            let area = if u < 0.0 {
                PI * q * q / 2.0 - 2.0 * q * u
            } else {
                cap(q, u)
            };
            area * q
        };
        outer -= integral(foot_negative, -PI / 2.0, 0.0);
        outer -= integral(
            |y| cap(neck_radius(y).max((rb * rb - y * y).max(0.0).sqrt()), y + c),
            0.0,
            self.foot_neck_end(),
        );
        let (bore_b, bore_t, passage) = (BARB_BORE / 2.0, TUBE_BORE / 2.0, PASSAGE / 2.0);
        let cavity = PI
            * (bore_b.powi(2) * BARB_DEPTH
                + bore_t.powi(2) * TUBE_DEPTH
                + passage.powi(2) * (self.tube_axis + TUBE_STOP))
            - 4.0 * passage.powi(3) / 3.0
            + PI * entry_height() * (ENTRY * (bore_b + bore_t) + 2.0 * ENTRY.powi(2) / 3.0);
        outer - cavity
    }
    fn mouth(&self, v: &Value) -> Result<Value> {
        let tip = point(&v["tip"])?;
        let axis = point(&v["axis"])?;
        let toward = point(&v["toward"])?;
        let length = axis.iter().map(|n| n * n).sum::<f64>().sqrt();
        if length == 0.0 {
            bail!("Elbow axis has zero length")
        }
        let x = axis.map(|n| n / length);
        let dot = (0..3).map(|i| toward[i] * x[i]).sum::<f64>();
        let across = std::array::from_fn::<_, 3, _>(|i| toward[i] - x[i] * dot);
        let length = across.iter().map(|n| n * n).sum::<f64>().sqrt();
        if length == 0.0 {
            bail!("Elbow toward direction is parallel to its axis")
        }
        let y = across.map(|n| n / length);
        let p =
            std::array::from_fn::<_, 3, _>(|i| tip[i] + x[i] * self.tube_axis + y[i] * TUBE_MOUTH);
        Ok(json!([p, y]))
    }
}

pub(super) fn request(v: &Value) -> Result<Value> {
    let method = v["method"].as_str().unwrap_or("state");
    if method == "installed_od" {
        return Ok(json!(installed_od(
            num(v, "relaxed_od")?,
            num(v, "bore")?,
            num(v, "opened")?
        )));
    }
    if method == "neck_radius" {
        return Ok(json!(neck_radius(num(v, "y")?)));
    }
    let s = Sleeve::read(v)?;
    match method {
        "tube_mouth" => return s.mouth(v),
        "tube_port" => return Ok(json!([[s.tube_axis, TUBE_MOUTH, 0.0], [0.0, 1.0, 0.0]])),
        "barb_rows" => {
            return Ok(json!(
                s.rows
                    .get(v["port"].as_str().context("Missing port")?)
                    .context("Unknown pump port")?
            ));
        }
        "engaged" => {
            return Ok(json!(
                s.rows
                    .get(v["port"].as_str().context("Missing port")?)
                    .context("Unknown pump port")?
                    .iter()
                    .filter(|r| r[0] <= BARB_DEPTH)
                    .map(|r| r[1])
                    .collect::<Vec<_>>()
            ));
        }
        "crest" => return Ok(json!(s.crest)),
        "root" => return Ok(json!(s.root)),
        "foot_neck_end" => return Ok(json!(s.foot_neck_end())),
        "foot_area" => return Ok(json!(s.foot_area())),
        "volume" => return Ok(json!(s.volume())),
        _ => {}
    }
    let q = 1.0 / 2_f64.sqrt();
    let xmin = (-BARB_DEPTH - BARB_OD / 2.0) * q;
    let xmax = (s.tube_axis + TUBE_OD / 2.0 + TUBE_MOUTH) * q;
    let height =
        s.foot + (BARB_DEPTH + BARB_OD / 2.0).max(TUBE_MOUTH - s.tube_axis + TUBE_OD / 2.0) * q;
    let vars = if method == "document" {
        let valley = s
            .rows
            .values()
            .map(|rows| {
                rows.iter()
                    .filter(|r| 2.0 <= r[0] && r[0] <= BARB_DEPTH - 2.0)
                    .map(|r| r[1])
                    .reduce(f64::min)
                    .context("No barb valleys")
            })
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .reduce(f64::min)
            .unwrap();
        variables(&[
            ("BARB_BORE", BARB_BORE, ".2f", ""),
            ("BARB_DEPTH", BARB_DEPTH, "g", ""),
            ("TUBE_BORE", TUBE_BORE, ".2f", ""),
            ("TUBE_DEPTH", TUBE_DEPTH, "g", ""),
            ("PASSAGE", PASSAGE, ".2f", ""),
            ("TUBE_STOP", TUBE_STOP, ".1f", ""),
            ("BARB_OD", BARB_OD, "g", ""),
            ("TUBE_OD", TUBE_OD, "g", ""),
            ("MIN_WALL", MIN_WALL, ".2f", ""),
            ("NECK", NECK, "g", ""),
            ("INTERFERENCE", TUBE_D - TUBE_BORE, ".2f", ""),
            ("CLAMP_BAND", CLAMP_BAND, "g", ""),
            ("TUBE_AXIS", s.tube_axis, ".2f", ""),
            ("TUBE_MOUTH", TUBE_MOUTH, ".1f", ""),
            ("BAND_AIR", BAND_AIR, "g", ""),
            ("FOOT_AREA", opt(v, "foot_area", s.foot_area()), ".1f", ""),
            ("PRINT_HEIGHT", opt(v, "height", height), ".1f", ""),
            ("CREST", s.crest, ".2f", ""),
            ("VALLEY", valley, ".2f", ""),
            ("ROOT", s.root, ".2f", ""),
            (
                "CREST_STRETCH",
                (s.crest / BARB_BORE - 1.0) * 100.0,
                ".0f",
                "",
            ),
            ("BARB_OD_INSTALLED", s.barb_installed, ".2f", ""),
            ("TUBE_OD_INSTALLED", s.tube_installed, ".2f", ""),
            ("VOLUME", opt(v, "volume", s.volume()) / 1000.0, ".3f", ""),
        ])?
    } else {
        Value::Null
    };
    Ok(
        json!({"values":{"PORTS":{"suction":"port_yminus","discharge":"port_yplus"},"_COLOR_SRGB":[0.92,0.92,0.90,0.60],
        "BARB_BORE":BARB_BORE,"BARB_DEPTH":BARB_DEPTH,"TUBE_D":TUBE_D,"TUBE_BORE":TUBE_BORE,
        "TUBE_DEPTH":TUBE_DEPTH,"PASSAGE":PASSAGE,"MIN_WALL":MIN_WALL,"BARB_OD":BARB_OD,"TUBE_OD":TUBE_OD,
        "TUBE_STOP":TUBE_STOP,"TUBE_MOUTH":TUBE_MOUTH,"NECK":NECK,"CLAMP_BAND":CLAMP_BAND,
        "CLAMP_RANGE":[10.0,16.0],"BAND_AIR":BAND_AIR,"BAND_T":0.6,"ENTRY":ENTRY,
        "ENTRY_HEIGHT":entry_height(),"BARB_OD_INSTALLED":s.barb_installed,"TUBE_OD_INSTALLED":s.tube_installed,
        "TUBE_AXIS":s.tube_axis,"FOOT":s.foot},
        "numbers":{"barb_radius":BARB_OD/2.0,"barb_bore":BARB_BORE/2.0,"barb_depth":BARB_DEPTH,
            "tube_radius":TUBE_OD/2.0,"tube_bore":TUBE_BORE/2.0,"tube_stop":TUBE_STOP,"tube_mouth":TUBE_MOUTH,
            "tube_axis":s.tube_axis,"neck_length":NECK,"passage_radius":PASSAGE/2.0,"entry":ENTRY,
            "entry_height":entry_height(),"foot":s.foot,"foot_span":4.0*(BARB_DEPTH+TUBE_MOUTH),
            "print_s":q,"print_shift":[-(xmin+xmax)/2.0,0.0,s.foot],"color":color(v)},
        "height":height,"variables":vars}),
    )
}
