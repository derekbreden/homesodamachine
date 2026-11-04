//! Finished evaporator winding and its tangent R15 manufacturing tail forms.

use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use std::f64::consts::PI;

type Point = [f64; 3];
fn add(a: Point, b: Point) -> Point {
    std::array::from_fn(|i| a[i] + b[i])
}
fn scale(a: Point, s: f64) -> Point {
    a.map(|v| v * s)
}
fn unit(a: Point) -> Point {
    scale(a, 1. / a.iter().map(|v| v * v).sum::<f64>().sqrt())
}
fn distance(a: Point, b: Point) -> f64 {
    a.iter()
        .zip(b)
        .map(|(a, b)| (a - b).powi(2))
        .sum::<f64>()
        .sqrt()
}
fn ease(t: f64) -> f64 {
    0.5 - 0.5 * (PI * t.clamp(0., 1.)).cos()
}

pub struct Coil {
    spec: Value,
    mandrel: Value,
    pub constants: Value,
}

impl Coil {
    pub fn new(spec: &Value) -> Result<Self> {
        let n = |key: &str| super::number(spec, key);
        let low = n("evap_tail_low_z")?;
        let high = n("evap_tail_high_z")?;
        let mandrel = super::mandrel::datums(low, high);
        let tube_r = mandrel["tube_radius"].as_f64().unwrap();
        let carbonator_r = n("carbonator_outer_radius")?;
        let wind_r = carbonator_r + tube_r;
        let total_wraps = 9.5;
        let wind_height = high - low;
        let pitch = wind_height / total_wraps;
        let lift = n("plateau_radius")? - carbonator_r;
        let bridge_ramp = (n("copper_bend")? * lift * PI.powi(2) / 2.).sqrt();
        let bridge_arc_runout = (bridge_ramp / n("plateau_radius")?).to_degrees();
        let edge = n("bridge_half_angle")?.to_degrees();
        let bottom_z = n("wall_and_floor_thickness")? + n("carbonator_support_ring_height")?;
        let constants = json!({
            "TUBE_R": tube_r, "WIND_R": wind_r, "TOTAL_WRAPS": total_wraps,
            "COPPER_BEND": n("copper_bend")?, "AZ_IN": -90., "AZ_OUT": 90.,
            "WIND_HEIGHT": wind_height, "PITCH": pitch, "BRIDGE_LIFT": lift,
            "BRIDGE_RAMP": bridge_ramp, "BRIDGE_ARC_RUNOUT": bridge_arc_runout,
            "RIDE_RADII": [[edge, n("plateau_radius")?], [edge + bridge_arc_runout, carbonator_r]],
            "BRIDGE_Z": [n("bridge_z_bottom")? + bottom_z, n("bridge_z_top")? + bottom_z],
            "BRIDGE_AXIAL_RAMP": n("axial_ramp_length")?.max(bridge_ramp),
            "WRAP_SAMPLES_PER_TURN": 96, "TAIL_BEND_R": 15., "STUB_TAIL_TOL": 1.
        });
        Ok(Self {
            spec: spec.clone(),
            mandrel,
            constants,
        })
    }

    fn n(&self, key: &str) -> f64 {
        self.constants[key].as_f64().unwrap()
    }
    fn s(&self, key: &str) -> f64 {
        self.spec[key].as_f64().unwrap()
    }
    fn m(&self, key: &str) -> f64 {
        self.mandrel[key].as_f64().unwrap()
    }

    pub fn at(&self, azimuth: f64, z: f64, radius: Option<f64>) -> Point {
        let radius = radius.unwrap_or_else(|| self.n("WIND_R"));
        let angle = azimuth.to_radians();
        [radius * angle.cos(), radius * angle.sin(), z]
    }

    pub fn ride_radius(&self, azimuth: f64, z: f64) -> f64 {
        let angle =
            ((azimuth - self.s("carbonator_sensor_azimuth") + 180.).rem_euclid(360.) - 180.).abs();
        let radii = self.constants["RIDE_RADII"].as_array().unwrap();
        let mut surface = self.s("carbonator_outer_radius");
        for (i, row) in radii.iter().enumerate() {
            let edge = row[0].as_f64().unwrap();
            let radius = row[1].as_f64().unwrap();
            if angle <= edge {
                surface = if i == 0 {
                    radius
                } else {
                    let low_edge = radii[i - 1][0].as_f64().unwrap();
                    let low_radius = radii[i - 1][1].as_f64().unwrap();
                    low_radius
                        + (radius - low_radius) * ease((angle - low_edge) / (edge - low_edge))
                };
                break;
            }
        }
        let z0 = self.constants["BRIDGE_Z"][0].as_f64().unwrap();
        let z1 = self.constants["BRIDGE_Z"][1].as_f64().unwrap();
        let ramp = self.n("BRIDGE_AXIAL_RAMP");
        let axial = ease(((z - (z0 - ramp)) / ramp).min(((z1 + ramp) - z) / ramp));
        self.n("WIND_R") + axial * (surface - self.s("carbonator_outer_radius")).max(0.)
    }

    pub fn wrap_points(&self) -> Vec<Point> {
        let count = ((self.n("TOTAL_WRAPS") * self.n("WRAP_SAMPLES_PER_TURN")).round_ties_even()
            as usize)
            .max(2);
        let swell = 1. / (PI * self.n("TOTAL_WRAPS") / count as f64).cos();
        (0..=count)
            .map(|i| {
                let turn = self.n("TOTAL_WRAPS") * i as f64 / count as f64;
                let angle = self.n("AZ_IN") + 360. * turn;
                let z = self.s("evap_tail_low_z") + self.n("PITCH") * turn;
                self.at(angle, z, Some(self.ride_radius(angle, z) * swell))
            })
            .collect()
    }

    pub fn wrap_length(&self) -> f64 {
        self.wrap_points()
            .windows(2)
            .map(|pair| distance(pair[1], pair[0]))
            .sum()
    }

    pub fn gap_z_near(&self, angle: f64, target_z: f64) -> f64 {
        let turns = (target_z - self.s("evap_tail_low_z")) / self.n("PITCH")
            - (angle - self.n("AZ_IN")) / 360.;
        let wrap_z = self.s("evap_tail_low_z")
            + (turns.floor() + (angle - self.n("AZ_IN")) / 360.) * self.n("PITCH");
        wrap_z + self.n("PITCH") / 2.
    }

    pub fn tail_layout(&self, which: &str, working_tail: bool, with_midpoints: bool) -> Value {
        let inlet = which == "inlet";
        let sign = if inlet { -1. } else { 1. };
        let angle = self.n(if inlet { "AZ_IN" } else { "AZ_OUT" });
        let z = self.s(if inlet {
            "evap_tail_low_z"
        } else {
            "evap_tail_high_z"
        });
        let beta = (self.n("PITCH") / (2. * PI * self.n("WIND_R"))).atan();
        let mut form = TailLayout::new(
            self.at(angle, z, None),
            [-beta.cos(), 0., sign * beta.sin()],
            self.n("TAIL_BEND_R"),
            with_midpoints,
        );
        form.bend(
            [-beta.sin(), 0., -sign * beta.cos()],
            beta.to_degrees(),
            "B0",
        );
        let lane_y = self.s(if inlet {
            "port_lane_mid_y"
        } else {
            "west_lane_mid_y"
        });
        let cross_z = self.s("evap_cross_z");
        let offset = lane_y.abs() - self.n("WIND_R");
        let angle = (1. - offset / (2. * self.n("TAIL_BEND_R"))).acos();
        form.bend([0., sign, 0.], angle.to_degrees(), "B1");
        form.bend(
            [-angle.sin(), -sign * angle.cos(), 0.],
            angle.to_degrees(),
            "B2",
        );
        if inlet {
            let drop = form.point[2] - cross_z;
            let angle = (1. - drop / (2. * self.n("TAIL_BEND_R"))).acos();
            form.bend([0., 0., -1.], angle.to_degrees(), "B3");
            form.bend([-angle.sin(), 0., angle.cos()], angle.to_degrees(), "B4");
        } else {
            form.bend([0., 0., -1.], 90., "B3");
            form.straight(form.point[2] - (cross_z + self.n("TAIL_BEND_R")), "S1");
            form.bend([-1., 0., 0.], 90., "B4");
        }
        let exit_x = self.s("front_wall_x") - self.s("wall_and_floor_thickness");
        form.straight(form.point[0] - exit_x, "S2");
        if working_tail {
            form.straight(
                self.mandrel["stub_protrusion"][which].as_f64().unwrap(),
                "WORKING TAIL",
            );
        }
        if with_midpoints {
            json!({"segments": form.segments, "point": form.point, "tangent": form.tangent})
        } else {
            json!(form.segments)
        }
    }

    pub fn tail_length(&self, which: &str) -> f64 {
        self.tail_layout(which, false, false)
            .as_array()
            .unwrap()
            .iter()
            .map(|item| {
                if item["kind"] == "bend" {
                    item["radius"].as_f64().unwrap() * item["angle"].as_f64().unwrap().to_radians()
                } else {
                    item["length"].as_f64().unwrap()
                }
            })
            .sum()
    }

    pub fn report(&self, input: &Value) -> String {
        use std::fmt::Write;
        let f = super::formatted;
        let cf = |key: &str, spec: &str| f(self.n(key), spec);
        let mf = |key: &str, spec: &str| f(self.m(key), spec);
        let wrap = input["laid_length"]
            .as_f64()
            .unwrap_or_else(|| self.wrap_length());
        let stock_name = input["stock_name"].as_str().unwrap_or("");
        let stock_source = input["stock_source"].as_str().unwrap_or("");
        let mut out = String::new();
        writeln!(out, "  evaporator coil").unwrap();
        writeln!(
            out,
            "    stock           {stock_name}, min bend {} — {stock_source}",
            cf("COPPER_BEND", ".2f")
        )
        .unwrap();
        writeln!(
            out,
            "    wound at        r {} (carbonator {} + tube {}); the mandrel winds at r {}",
            cf("WIND_R", ".3f"),
            f(self.s("carbonator_outer_radius"), ".1f"),
            cf("TUBE_R", ".3f"),
            mf("helix_path_radius", ".3f")
        )
        .unwrap();
        writeln!(
            out,
            "    wraps           {} at {} mm pitch, z {}..{}",
            cf("TOTAL_WRAPS", ".3f"),
            cf("PITCH", ".4g"),
            f(self.s("evap_tail_low_z"), ".1f"),
            f(self.s("evap_tail_high_z"), ".1f")
        )
        .unwrap();
        writeln!(
            out,
            "    azimuths        inlet {}°, outlet {}°, CCW delta {}°",
            cf("AZ_IN", "+.2f"),
            cf("AZ_OUT", "+.2f"),
            f((self.n("AZ_OUT") - self.n("AZ_IN")).rem_euclid(360.), ".2f")
        )
        .unwrap();
        writeln!(
            out,
            "    wrap laid       {} mm ({} ft) — mandrel {}, sprung {}, reed bridge {}",
            f(wrap, ".0f"),
            f(wrap / 304.8, ".2f"),
            mf("mandrel_wrap_length", ".0f"),
            mf("fitted_wrap_length", ".0f"),
            f(
                wrap - self.n("TOTAL_WRAPS") * (2. * PI * self.n("WIND_R")).hypot(self.n("PITCH")),
                "+.0f"
            )
        )
        .unwrap();
        for end in ["inlet", "outlet"] {
            let length = input["tail_lengths"][end]
                .as_f64()
                .unwrap_or_else(|| self.tail_length(end));
            writeln!(
                out,
                "    {:15} {} mm allowed = {} mm drawn in-shell ({} billed) + {} protruding",
                format!("{end} stub"),
                f(self.mandrel["stub_allowance"][end].as_f64().unwrap(), ".1f"),
                f(length, ".1f"),
                f(self.mandrel["tail_in_shell"][end].as_f64().unwrap(), ".1f"),
                f(
                    self.mandrel["stub_protrusion"][end].as_f64().unwrap(),
                    ".0f"
                )
            )
            .unwrap();
        }
        let cut = wrap + self.m("stub_total");
        let spare = self.m("roll_length_ft") - self.m("carbonators_per_roll") * cut / 304.8;
        writeln!(
            out,
            "    cut per carb    {} mm ({} ft); {} per {} ft roll leaves {} ft ({} mm)",
            f(cut, ".1f"),
            f(cut / 304.8, ".3f"),
            f(self.m("carbonators_per_roll"), "g"),
            mf("roll_length_ft", ".0f"),
            f(spare, "+.3f"),
            f(spare * 304.8, "+.0f")
        )
        .unwrap();
        out
    }
}

struct TailLayout {
    point: Point,
    tangent: Point,
    radius: f64,
    with_midpoints: bool,
    segments: Vec<Value>,
}

impl TailLayout {
    fn new(point: Point, tangent: Point, radius: f64, with_midpoints: bool) -> Self {
        Self {
            point,
            tangent: unit(tangent),
            radius,
            with_midpoints,
            segments: vec![],
        }
    }

    fn bend(&mut self, normal: Point, degrees: f64, label: &str) {
        let normal = unit(normal);
        let angle = degrees.to_radians();
        let (start, tangent, radius) = (self.point, self.tangent, self.radius);
        let end = add(
            add(start, scale(tangent, radius * angle.sin())),
            scale(normal, radius * (1. - angle.cos())),
        );
        let mut segment = json!({"id": label, "kind": "bend", "start": start, "end": end,
            "radius": radius, "angle": degrees, "tangent": tangent, "normal": normal});
        if self.with_midpoints {
            segment["mid"] = json!(add(
                add(start, scale(tangent, radius * (angle / 2.).sin())),
                scale(normal, radius * (1. - (angle / 2.).cos()))
            ));
        }
        self.segments.push(segment);
        self.point = end;
        self.tangent = add(scale(tangent, angle.cos()), scale(normal, angle.sin()));
    }

    fn straight(&mut self, length: f64, label: &str) {
        if length <= 1e-8 {
            return;
        }
        let end = add(self.point, scale(self.tangent, length));
        self.segments
            .push(json!({"id": label, "kind": "straight", "start": self.point,
            "end": end, "length": length}));
        self.point = end;
    }
}

pub fn request(input: &Value) -> Result<Value> {
    let coil = Coil::new(&input["spec"])?;
    let n = |key: &str| super::number(input, key);
    let side = || -> Result<&str> {
        match input["which"].as_str().context("coil tail needs which")? {
            side @ ("inlet" | "outlet") => Ok(side),
            side => bail!("unknown coil tail {side}"),
        }
    };
    match input["action"]
        .as_str()
        .context("coil request needs action")?
    {
        "constants" => Ok(coil.constants),
        "at" => Ok(json!(coil.at(
            n("azimuth_deg")?,
            n("z")?,
            input["radius"].as_f64()
        ))),
        "ease" => Ok(json!(ease(n("t")?))),
        "ride-radius" => Ok(json!(coil.ride_radius(n("azimuth_deg")?, n("z")?))),
        "wrap-points" => Ok(json!(coil.wrap_points())),
        "wrap-length" => Ok(json!(coil.wrap_length())),
        "bridge-lift-length" => Ok(json!(
            coil.wrap_length()
                - coil.n("TOTAL_WRAPS") * (2. * PI * coil.n("WIND_R")).hypot(coil.n("PITCH"))
        )),
        "gap-z-near" => Ok(json!(coil.gap_z_near(n("azimuth_deg")?, n("target_z")?))),
        "tail-layout" | "tail-edges" => Ok(coil.tail_layout(
            side()?,
            input["working_tail"].as_bool().unwrap_or(false),
            input["action"] == "tail-edges",
        )),
        "tail-length" => Ok(json!(coil.tail_length(side()?))),
        "tail-ledger" => {
            let tolerance = coil.n("STUB_TAIL_TOL");
            let rows: Vec<_> = ["inlet", "outlet"].iter().map(|end| {
                let drawn = coil.tail_length(end);
                let billed = coil.mandrel["tail_in_shell"][end].as_f64().unwrap();
                json!({"holds": (drawn - billed).abs() <= tolerance,
                    "detail": format!("{end} tail draws {} mm against the {} mm `coil_mandrel.tail_in_shell` bills — {} mm out of the {} mm that end has to protrude with",
                        super::formatted(drawn, ".1f"), super::formatted(billed, ".1f"),
                        super::formatted(drawn - billed, "+.1f"),
                        super::formatted(coil.mandrel["stub_protrusion"][end].as_f64().unwrap(), ".0f"))})
            }).collect();
            Ok(
                json!({"label": "Each coil tail's in-shell run is the one its stub allowance bills",
                "target": format!("within {} mm of `coil_mandrel.tail_in_shell`", super::formatted(tolerance, ".1f")),
                "rows": rows}),
            )
        }
        "tail-points" => {
            let layout = coil.tail_layout(side()?, false, false);
            let segments = layout.as_array().unwrap();
            let mut points = vec![segments[0]["start"].clone()];
            points.extend(segments.iter().map(|segment| segment["end"].clone()));
            Ok(json!(points))
        }
        "cut-length" => Ok(json!(coil.wrap_length() + coil.m("stub_total"))),
        "roll-spare-ft" => Ok(json!(
            coil.m("roll_length_ft")
                - coil.m("carbonators_per_roll") * (coil.wrap_length() + coil.m("stub_total"))
                    / 304.8
        )),
        "report" => Ok(json!(coil.report(input))),
        action => bail!("unknown coil action {action}"),
    }
}
